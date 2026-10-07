"""
Put a painted pose into the game.

    python3 tools/install_pose.py "~/ComfyUI-Shared/output/pose_dorm_common__nobara__evening_a_00001_.png"
    python3 tools/install_pose.py <render.png> --box 400,300,500,700
    python3 tools/install_pose.py <render.png> --name pose_cafeteria__yuji
    python3 tools/install_pose.py <render.png> --dry                  # every check and the preview; writes nothing else
    options: --root <a copy of the project>  --layout-dump <file>  --bg <picture>  --plan <rows.json>
             --match-cloth   --no-game (with --root and --bg: a test room that is not the game's)

A pose is a whole picture of a room with one person painted in
(tools/make_pose_workflow.py; PHASE2_DESIGN.md D36, D37; docs/UI2_DESIGN.md
5.12). The game lays only a box around the person over the room, so this tool
has to know where the person is, has to be sure the rest of the room was left
alone, and has to be sure the box leaves the room usable.

What it does:
  1. Reads the name: pose_<place>__<who>[__<variant>][__asleep], from the
     file's own name (the workflow's `_a_00001_` tail is ignored) or from
     --name. A pose at the Bathhouse, the Sauna or the Pool is refused (K16).
  2. Brings the render to 1920x1080 (scaled to the full width; the height
     is then padded with the room's own rows, or cropped, about the centre:
     a 2752x1536 render is the room at 1920x1072, 4 px down) and compares it
     with the room's own picture, game/images/bg/<room>[_<variant>].png (or --bg). "Changed"
     means: after a 4 px blur of both (each 4x4 block is averaged), a block
     differs by more than 24 in any channel. An editor's faint noise over the
     whole frame is not a change; a person is.
  3. Refuses the picture when more than 35% of the room changed: the editor
     redrew the room, so the box would show a seam. Run the other candidate.
  4. Measures the box: the largest connected changed region, with any
     changed region within 12 px of it (feet or a shadow cut off from the
     body), grown by 24 px (the feathered edge needs room). --box x,y,w,h
     sets it by hand.
  5. KEEPS THE ROOM USABLE. The box is refused, and the point or the other
     pose is named, when it
       - covers an exit point of its room;
       - covers a hotspot point, unless that hotspot is the one the pose's
         row names in `at` (the reading table a person is painted at);
       - overlaps the box of another installed pose of the same room and
         hour picture THAT CAN SHOW AT THE SAME TIME. A pose reaches the
         game as an opaque box cut from a whole-room render, so an overlap
         would paint empty room over the other person. Who can show with
         whom is read from the schedule, the weekend table and the asleep
         and away tables in the layout dump: the same person awake and
         asleep never show together and may share a bed; two people the
         game sends to one Tokyo district the same hour may not overlap.
     The points are the ones the game draws today, from the layout dump
     (tools/game_layout.py), which refuses a dump that is out of date; in a
     worktree pass --layout-dump <file>.
  6. THE UNIFORM'S CLOTH (D59). For someone in the school uniform the cloth
     inside the box is measured against the ramp of tools/cloth_match.py and
     reported. --match-cloth runs the same match on the figure's box before
     the picture is installed. (It needs ComfyUI's Python; without it the
     line reads SKIPPED.)
  7. Writes the box to game/layout/pose_<place>.json under "poses" (the only
     file it writes a box to: the room's view_ and hot_ files are never
     touched, K15), the pose's row to game/layout/pictures.json (which room
     picture, at which revision, it was painted on: without that row a pose
     on a revised picture counts as stale and would not show), the picture
     to game/images/place/<name>.png, and a side-by-side preview to
     shots/art/<name>.png.

--dry does everything but write the sidecar, the row and the picture. --root
<dir> reads the room from, and writes under, another folder than the project.
--plan <file> reads the pose rows from a JSON list instead of POSES (tests).
--no-game is for a harness's own test room: nothing of the game is read, so
none of step 5 or 6 runs and no row is written; it needs --root and --bg.

AFTER AN INSTALL the layout dump is out of date (it covers game/layout/):
run tools/smoke.sh u2_dump again before the next tool.

Pure Python: raster.py and pngread.py.
"""
import sys, os, re, json, subprocess, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, resample
import game_layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
CELL = 4                    # the blur: each CELL x CELL block is averaged
THRESH = 24                 # a block differs when any channel is off by more than this
REFUSE = 0.35               # more of the room than this changed: refuse
GROW = 24                   # the box is the region grown by this many pixels
NEAR = 3                    # a region this many blocks (12 px) or less from the person is part of them
NEAR_MIN = 4                # ... when it has at least this many blocks (a lone speck is not)
UNIFORM = ("megumi", "toge", "nobara", "maki", "mc", "yuji")        # tools/cloth_match.py: who wears the school uniform

NAME_RE = re.compile(r"^(pose_(.+?)__([a-z0-9]+?)(?:__(?!asleep)([a-z0-9]+?))?(__asleep)?)(?:_[ab])?(?:_\d+_?)?$")
KEY_RE = re.compile(r"^([a-z0-9]+?)(?:__(?!asleep)([a-z0-9]+?))?(__asleep)?$")


def parse_name(text):
    """(stem, place, who, variant, state) from a file name or a --name value."""
    base = os.path.splitext(os.path.basename(text))[0]
    m = NAME_RE.match(base)
    if not m:
        raise SystemExit("can't tell the place and the person from %r: the name must be "
                         "pose_<place>__<who>, pose_<place>__<who>__<variant> or ...__asleep (pass --name)" % base)
    return m.group(1), m.group(2), m.group(3), m.group(4) or "", "asleep" if m.group(5) else "awake"


def pose_key(who, variant="", state="awake"):
    """The key a pose's box is written under: yuji, nobara__evening, megumi__night__asleep."""
    return who + ("__" + variant if variant else "") + ("__asleep" if state == "asleep" else "")


def parse_key(key):
    m = KEY_RE.match(key)
    return (m.group(1), m.group(2) or "", "asleep" if m.group(3) else "awake") if m else None


def rgb(im):
    if im.ch == 3:
        return im
    out = Img(im.w, im.h)
    b, o = im.buf, out.buf
    o[0::3], o[1::3], o[2::3] = b[0::4], b[1::4], b[2::4]
    return out


def fit(im, under=None):
    """The picture at exactly 1920x1080. An off-ratio picture is scaled to the
    full width, and then its height is padded or cropped about the centre:
    the editor lays the room across the render's whole width, so a 2752x1536
    render is the room at 1920x1072, 4 px down (cropping its sides to 16:9
    instead would put everything 6 to 7 px off). The padding rows are taken
    from `under` (the room, already 1920x1080) when it is given, else the
    picture's own edge rows are repeated."""
    im = rgb(im)
    if (im.w, im.h) == (W, H):
        return im
    nh = max(1, int(im.h * W / float(im.w) + 0.5))
    if (im.w, im.h) != (W, nh):
        im = resample(im, W, nh)
    if nh == H:
        return im
    if nh > H:
        from raster import crop
        y0 = (nh - H) // 2
        return crop(im, 0, y0, W, y0 + H)
    y0 = (H - nh) // 2
    out = Img(W, H)
    stride = W * 3
    if under is not None and (under.w, under.h) == (W, H):
        out.buf[:] = rgb(under).buf
    else:
        top, bottom = im.buf[:stride], im.buf[(nh - 1) * stride:nh * stride]
        for y in range(y0):
            out.buf[y * stride:(y + 1) * stride] = top
        for y in range(y0 + nh, H):
            out.buf[y * stride:(y + 1) * stride] = bottom
    out.buf[y0 * stride:(y0 + nh) * stride] = im.buf
    return out


def blocks(im):
    """The picture blurred and shrunk: [channel][row] -> list of block sums
    (CELL x CELL pixels each)."""
    gw, gh = im.w // CELL, im.h // CELL
    out = [[None] * gh for _c in range(3)]
    stride = im.w * 3
    for gy in range(gh):
        acc = [[0] * gw for _c in range(3)]
        for dy in range(CELL):
            row = im.buf[(gy * CELL + dy) * stride:(gy * CELL + dy + 1) * stride]
            for c in range(3):
                chan = row[c::3]
                a = acc[c]
                for d in range(CELL):
                    part = chan[d::CELL]
                    for gx in range(gw):
                        a[gx] += part[gx]
        for c in range(3):
            out[c][gy] = acc[c]
    return out, gw, gh


def changed_cells(a, b):
    """A grid of 0/1: the blocks where the two pictures differ."""
    ba, gw, gh = blocks(a)
    bb, _w, _h = blocks(b)
    lim = THRESH * CELL * CELL
    grid = []
    for gy in range(gh):
        row = bytearray(gw)
        for c in range(3):
            ra, rb = ba[c][gy], bb[c][gy]
            for gx in range(gw):
                if not row[gx] and abs(ra[gx] - rb[gx]) > lim:
                    row[gx] = 1
        grid.append(row)
    return grid, gw, gh


def regions(grid, gw, gh):
    """[(cells, x0, y0, x1, y1)] for every connected region of changed blocks
    (8-connected), in block units, the largest first."""
    seen = [bytearray(gw) for _y in range(gh)]
    out = []
    for sy in range(gh):
        row = grid[sy]
        for sx in range(gw):
            if not row[sx] or seen[sy][sx]:
                continue
            stack = [(sx, sy)]
            seen[sy][sx] = 1
            n, x0, y0, x1, y1 = 0, sx, sy, sx, sy
            while stack:
                x, y = stack.pop()
                n += 1
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if 0 <= nx < gw and 0 <= ny < gh and grid[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = 1
                            stack.append((nx, ny))
            out.append((n, x0, y0, x1, y1))
    out.sort(key=lambda r: -r[0])
    return out


def person_region(grid, gw, gh):
    """(cells, x0, y0, x1, y1) of the person, in block units; None when
    nothing changed. It is the largest region, together with every region of
    at least NEAR_MIN blocks that lies within NEAR blocks of it (feet, a hand
    or a shadow that a few unchanged blocks cut off from the body); what is
    taken in can bring its own neighbours."""
    found = regions(grid, gw, gh)
    if not found:
        return None
    n, x0, y0, x1, y1 = found[0]
    rest = [r for r in found[1:] if r[0] >= NEAR_MIN]
    grew = True
    while grew:
        grew = False
        for r in list(rest):
            _n, a0, b0, a1, b1 = r
            dx = max(0, a0 - x1 - 1, x0 - a1 - 1)
            dy = max(0, b0 - y1 - 1, y0 - b1 - 1)
            if dx <= NEAR and dy <= NEAR:
                rest.remove(r)
                n += _n
                x0, y0, x1, y1 = min(x0, a0), min(y0, b0), max(x1, a1), max(y1, b1)
                grew = True
    return (n, x0, y0, x1, y1)


def half(im):
    """A quick half-size copy for the preview."""
    out = Img(im.w // 2, im.h // 2)
    stride = im.w * 3
    for y in range(out.h):
        row = im.buf[(y * 2) * stride:(y * 2 + 1) * stride]
        o = y * out.w * 3
        out.buf[o + 0:o + out.w * 3:3] = row[0::6]
        out.buf[o + 1:o + out.w * 3:3] = row[1::6]
        out.buf[o + 2:o + out.w * 3:3] = row[2::6]
    return out


def outline(im, x, y, w, h, c, t=3):
    for k in range(t):
        im.row_fill(y + k, x, x + w, c)
        im.row_fill(y + h - 1 - k, x, x + w, c)
    for yy in range(y, y + h):
        im.row_fill(yy, x, x + t, c)
        im.row_fill(yy, x + w - t, x + w, c)


def preview(bg, pose, box, grid, path):
    """The room and the render side by side at half size: the changed blocks
    tinted on the left, the box drawn on both."""
    a, b = half(bg), half(pose)
    sheet = Img(a.w * 2 + 8, a.h, fill=(20, 18, 28))
    for y in range(a.h):
        o = y * sheet.w * 3
        sheet.buf[o:o + a.w * 3] = a.buf[y * a.w * 3:(y + 1) * a.w * 3]
        o += (a.w + 8) * 3
        sheet.buf[o:o + b.w * 3] = b.buf[y * b.w * 3:(y + 1) * b.w * 3]
    for gy, row in enumerate(grid):
        for gx in range(len(row)):
            if row[gx]:
                for yy in range(gy * CELL // 2, (gy + 1) * CELL // 2):
                    for xx in range(gx * CELL // 2, (gx + 1) * CELL // 2):
                        sheet.blend(xx, yy, (232, 51, 79), 0.45)
    x, y, w, h = [v // 2 for v in box]
    outline(sheet, x, y, w, h, (255, 209, 102))
    outline(sheet, a.w + 8 + x, y, w, h, (255, 209, 102))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)


def read_json(path, what):
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s is not JSON (%s): fix it or remove it first" % (path, e))
    if not isinstance(data, dict):
        raise SystemExit("%s must be a JSON object" % path)
    return data


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def write_sidecar(path, key, box):
    """Set poses[key] in the pose sidecar, keeping every other box in it."""
    data = read_json(path, "the pose sidecar")
    poses = data.get("poses")
    if not isinstance(poses, dict):
        poses = {}
    poses[key] = [int(v) for v in box]
    data["poses"] = poses
    write_json(path, data)


# ---- who can show with whom -------------------------------------------------------------------------------
def plan_rows(plan_path=None):
    if plan_path:
        rows = json.load(open(plan_path, encoding="utf-8"))
        if not isinstance(rows, list):
            raise SystemExit("%s must be a JSON list of pose rows" % plan_path)
        return rows
    import make_pose_workflow
    return make_pose_workflow.POSES


def plan_row(rows, place, who, variant, state):
    for row in rows:
        if (row.get("who"), row.get("place"), row.get("variant", ""), row.get("state") or "awake") == (who, place, variant, state):
            return row
    return {"who": who, "place": place, "variant": variant, "state": state}


def show_cells(lay, row):
    """The (weekday, period) cells at which a row's pose can be on screen; None when nothing says (a `via`
    row: something other than the routine puts the person there)."""
    if row.get("via"):
        return None
    who, place, variant = row["who"], row["place"], row.get("variant", "")
    state = row.get("state") or "awake"
    periods = lay.periods_showing(place, variant) if lay.has_place(place) else set(lay.d.get("periods", []))
    out = set()
    for day, per in lay.cells():
        weekend = day in game_layout.WEEKEND_DAYS
        if (row.get("days") == "weekdays" and weekend) or (row.get("days") == "weekends" and not weekend):
            continue
        if per not in periods or lay.where(who, day, per) != place:
            continue
        asleep = lay.asleep(who, day, per)
        if asleep is not None and asleep != (state == "asleep"):
            continue
        out.add((day, per))
    return out


def together(lay, a, b):
    """A cell at which both rows' poses can show, or None. One person is never in two of their own poses."""
    if a["who"] == b["who"]:
        return None
    ca, cb = show_cells(lay, a), show_cells(lay, b)
    if ca is None and cb is None:
        return ("any day", "Night")
    if ca is None or cb is None:
        both = sorted(ca if cb is None else cb)
        return both[0] if both else None
    both = [c for c in lay.cells() if c in ca and c in cb]
    return both[0] if both else None


def fresh(manifest, stem, parent):
    """5.5: is a dependant picture still the one made for its parent's revision?"""
    import check_campus
    row = (manifest.get("pictures") or {}).get(stem)
    now = check_campus.rev_of(manifest, parent)
    if row is None:
        return now == 1
    return row.get("of_rev", now) == now


def inside(pt, box):
    x, y, w, h = box
    return x <= pt[0] < x + w and y <= pt[1] < y + h


def overlap(a, b):
    return min(a[0] + a[2], b[0] + b[2]) > max(a[0], b[0]) and min(a[1] + a[3], b[1] + b[3]) > max(a[1], b[1])


def room_refusals(lay, rows, root, manifest, stem, place, who, variant, state, box):
    """Why this box cannot go into this room: [text]. Empty when it can."""
    out = []
    row = plan_row(rows, place, who, variant, state)
    if lay.has_place(place):
        for pt in lay.points(place, root):
            if not inside(pt["at"], box):
                continue
            if pt["kind"] == "exit":
                out.append("the box covers an exit of the room: %s at (%d, %d). Move the spot and run the pose again."
                           % (pt["name"], pt["at"][0], pt["at"][1]))
            elif pt["id"] != row.get("at"):
                out.append("the box covers %s at (%d, %d), which the pose's row does not name in `at`%s. Move the "
                           "spot, or name the hotspot in `at` if the person is painted at that thing."
                           % (pt["name"], pt["at"][0], pt["at"][1],
                              " (its `at` is %s)" % row["at"] if row.get("at") else ""))
    base = lay.bg_stem(place) if lay.has_place(place) else place
    parent = base + ("_" + variant if variant else "")
    boxes = dict(read_json(os.path.join(root, "game", "layout", "view_%s.json" % place), "").get("poses") or {})
    boxes.update(read_json(os.path.join(root, "game", "layout", "pose_%s.json" % place), "").get("poses") or {})
    mine = pose_key(who, variant, state)
    for key, other in sorted(boxes.items()):
        got = parse_key(key)
        if key == mine or got is None or got[1] != variant or not overlap(box, other):
            continue
        o_who, o_variant, o_state = got
        o_stem = "pose_%s__%s" % (place, key)
        if not os.path.exists(os.path.join(root, "game", "images", "place", o_stem + ".png")):
            continue
        if not fresh(manifest, o_stem, parent):
            print("   note: %s overlaps this box but is stale (made for an older %s.png), so it is not shown" % (o_stem, parent))
            continue
        cell = together(lay, row, plan_row(rows, place, o_who, o_variant, o_state))
        if cell is None:
            print("   note: the box overlaps %s's, and the two never show together (%s)"
                  % (o_stem, "the same person" if o_who == who else "the schedule never has both there"))
            continue
        out.append("the box (%d,%d %dx%d) overlaps the box of %s (%d,%d %dx%d), and the two can show together (%s, "
                   "%s): one would paint empty room over the other. Give this pose a place of its own and run it again."
                   % (box[0], box[1], box[2], box[3], o_stem, other[0], other[1], other[2], other[3], cell[0], cell[1]))
    return out


def cloth(pose_png, room_png, box, match_to=None):
    """D59: the uniform's cloth in the box against the ramp. Prints the tool's lines; True when a matched
    picture was written to `match_to`."""
    tools = os.path.dirname(os.path.abspath(__file__))
    cmd = ["/bin/bash", os.path.join(tools, "py_art.sh"), os.path.join(tools, "pose_cloth.py"), pose_png, room_png,
           "%d,%d,%d,%d" % tuple(box)]
    if match_to:
        cmd += ["--match", match_to]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode("utf-8", "replace").strip()
    if p.returncode == 69:
        print("   cloth     SKIPPED (no ComfyUI python): the uniform's cloth was not measured against the ramp")
        return False
    for line in text.splitlines():
        print("   cloth     " + line)
    if p.returncode != 0:
        raise SystemExit("the cloth measure failed (see the lines above); nothing was written")
    return bool(match_to) and os.path.exists(match_to)


def install(src, name=None, box=None, bg_path=None, root=None, dry=False, dump_path=None, plan_path=None,
            no_game=False, match_cloth=False):
    root = root or ROOT
    src = os.path.expanduser(src)
    if not os.path.exists(src):
        raise SystemExit("no picture at %s" % src)
    stem, place, who, variant, state = parse_name(name or src)
    if place in game_layout.NO_POSE_PLACES:
        raise SystemExit("REFUSED: no pose is ever installed at the Bathhouse, the Sauna or the Pool (K16)")
    lay = manifest = rows = None
    if no_game:
        if os.path.realpath(root) == os.path.realpath(ROOT) or bg_path is None:
            raise SystemExit("--no-game is for a test room: it needs --root <another folder> and --bg <its picture>")
    else:
        import check_campus
        lay = game_layout.load(dump_path, root)
        manifest = check_campus.load_manifest(root)
        rows = plan_rows(plan_path)
        if not lay.has_place(place):
            districts = lay.districts()
            if districts is None or place not in districts:
                raise SystemExit("no place %r in the game, and it is not a Tokyo district the game sends anyone to%s"
                                 % (place, "" if districts is not None else " (the layout dump has no away table)"))
            sent = set(d for day, per in lay.cells() for d in [lay.away(who, day, per)] if d)
            if place not in sent:
                raise SystemExit("REFUSED: the game never sends %s to %s (WORLD_AWAY)" % (who, place))
        if bg_path is None:
            base = lay.bg_stem(place) if lay.has_place(place) else place
            bg_path = os.path.join(root, "game", "images", "bg", base + ("_" + variant if variant else "") + ".png")
    if not os.path.exists(bg_path):
        raise SystemExit("no room picture at %s to compare with" % bg_path)
    bg = fit(load(bg_path))
    pose = fit(load(src), under=bg)

    grid, gw, gh = changed_cells(bg, pose)
    total = sum(sum(row) for row in grid)
    frac = total / float(gw * gh)
    region = person_region(grid, gw, gh)
    print("%s: %.1f%% of the room changed" % (stem, 100.0 * frac))

    prev = os.path.join(root, "shots", "art", stem + ".png")
    if frac > REFUSE:
        preview(bg, pose, (0, 0, W, H), grid, prev)
        print("   preview -> %s" % prev)
        raise SystemExit("REFUSED: more than %d%% of the room changed, so the editor redrew the room and the "
                         "box would show a seam. Use the other candidate, or run the workflow again."
                         % int(REFUSE * 100))
    if box is None:
        if region is None:
            raise SystemExit("REFUSED: nothing changed: the picture is the empty room")
        _n, x0, y0, x1, y1 = region
        bx0 = max(0, x0 * CELL - GROW)
        by0 = max(0, y0 * CELL - GROW)
        bx1 = min(W, (x1 + 1) * CELL + GROW)
        by1 = min(H, (y1 + 1) * CELL + GROW)
        box = (bx0, by0, bx1 - bx0, by1 - by0)
        stray = total - region[0]
        if stray > 0.25 * region[0]:
            print("   !! %d changed blocks lie outside the person's region (%d blocks): look at the preview; "
                  "if part of the person is outside the box, pass --box x,y,w,h" % (stray, region[0]))
    else:
        x, y, w, h = box
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
            raise SystemExit("--box %d,%d,%d,%d does not fit inside %dx%d" % (x, y, w, h, W, H))
    print("   box %d,%d  %dx%d" % box)
    preview(bg, pose, box, grid, prev)
    print("   preview -> %s" % prev)

    if not no_game:
        why = room_refusals(lay, rows, root, manifest, stem, place, who, variant, state, box)
        if why:
            raise SystemExit("REFUSED: " + "\nREFUSED: ".join(why))
        if who in UNIFORM and state != "asleep":
            tmp = tempfile.mkdtemp(prefix="pose_cloth_")
            try:
                a, b = os.path.join(tmp, "pose.png"), os.path.join(tmp, "room.png")
                pose.save(a); bg.save(b)
                out = os.path.join(tmp, "matched.png") if match_cloth else None
                if cloth(a, b, box, out):
                    pose = fit(load(out))
            finally:
                import shutil
                shutil.rmtree(tmp, ignore_errors=True)
    if dry:
        return box
    key = pose_key(who, variant, state)
    side = os.path.join(root, "game", "layout", "pose_%s.json" % place)
    write_sidecar(side, key, box)
    print("   box written -> %s (poses[%r])" % (side, key))
    if not no_game:
        import check_campus
        base = lay.bg_stem(place) if lay.has_place(place) else place
        parent = base + ("_" + variant if variant else "")
        mpath = os.path.join(root, "game", "layout", "pictures.json")
        data = read_json(mpath, "the manifest")
        pics = data.get("pictures")
        if not isinstance(pics, dict):
            pics = {}
        pics[stem] = {"of": parent, "of_rev": check_campus.rev_of({"pictures": pics}, parent)}
        data["pictures"] = pics
        write_json(mpath, data)
        print("   row written -> %s (%s: painted on %s.png at revision %d)" % (mpath, stem, parent, pics[stem]["of_rev"]))
    dest = os.path.join(root, "game", "images", "place", stem + ".png")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    pose.save(dest)
    print("   installed -> %s" % dest)
    if not no_game:
        print("   the layout dump is now out of date: run tools/smoke.sh u2_dump before the next tool")
    return box


def main(argv):
    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv):
                raise SystemExit("%s needs a value" % flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    box, name, bg, root, plan = opt("--box"), opt("--name"), opt("--bg"), opt("--root"), opt("--plan")
    dump_path = game_layout.pop_dump_arg(argv)
    known = ("--dry", "--no-game", "--match-cloth")
    dry, no_game, match_cloth = [f in argv for f in known]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or [a for a in argv if a.startswith("--") and a not in known]:
        print(__doc__); raise SystemExit(1)
    if box is not None:
        try:
            box = tuple(int(v) for v in box.split(","))
            assert len(box) == 4
        except (ValueError, AssertionError):
            raise SystemExit("--box takes four whole numbers: x,y,w,h")
    install(args[0], name=name, box=box, bg_path=bg, root=root, dry=dry, dump_path=dump_path, plan_path=plan,
            no_game=no_game, match_cloth=match_cloth)


if __name__ == "__main__":
    main(sys.argv[1:])
