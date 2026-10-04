"""
Put a painted pose into the game.

    python3 tools/install_pose.py "~/ComfyUI-Shared/output/pose_dorm_common__nobara__evening_a_00001_.png"
    python3 tools/install_pose.py <render.png> --box 400,300,500,700
    python3 tools/install_pose.py <render.png> --name pose_cafeteria__yuji

A pose is a whole picture of a room with one person painted in
(tools/make_pose_workflow.py; PHASE2_DESIGN.md D36, D37). The game lays only
a box around the person over the room, so this tool has to know where the
person is, and has to be sure the rest of the room was left alone.

What it does:
  1. Reads the name: pose_<place>__<who>[__<variant>], from the file's own
     name (the workflow's `_a_00001_` tail is ignored) or from --name.
  2. Brings the render to 1920x1080 and compares it with the room's own
     picture, game/images/bg/<room>[_<variant>].png (or --bg). "Changed"
     means: after a 4 px blur of both (each 4x4 block is averaged), a block
     differs by more than 24 in any channel. An editor's faint noise over the
     whole frame is not a change; a person is.
  3. Refuses the picture when more than 35% of the room changed: the editor
     redrew the room, so the box would show a seam. Run the other candidate.
  4. Measures the box: the largest connected changed region, grown by 24 px
     (the feathered edge needs room). --box x,y,w,h sets it by hand.
  5. Writes the box to game/layout/view_<place>.json under "poses" (the only
     file it writes there; slots and other poses in it are kept, and
     hot_<place>.json is never touched), a side-by-side preview to
     shots/art/<name>.png, and the picture to game/images/place/<name>.png.

--dry does everything but write the sidecar and the picture. --root <dir>
writes under another folder than the project (the harness uses it).
Pure Python: raster.py and pngread.py.
"""
import sys, os, re, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, resample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
CELL = 4                    # the blur: each CELL x CELL block is averaged
THRESH = 24                 # a block differs when any channel is off by more than this
REFUSE = 0.35               # more of the room than this changed: refuse
GROW = 24                   # the box is the region grown by this many pixels

NAME_RE = re.compile(r"^(pose_(.+?)__([a-z0-9]+?)(?:__([a-z0-9]+?))?)(?:_[ab])?(?:_\d+_?)?$")


def parse_name(text):
    """(stem, place, who, variant) from a file name or a --name value."""
    base = os.path.splitext(os.path.basename(text))[0]
    m = NAME_RE.match(base)
    if not m:
        raise SystemExit("can't tell the place and the person from %r: the name must be "
                         "pose_<place>__<who> or pose_<place>__<who>__<variant> (pass --name)" % base)
    return m.group(1), m.group(2), m.group(3), m.group(4) or ""


def place_bg(place):
    src = open(os.path.join(ROOT, "game", "sb_world.rpy"), encoding="utf-8").read()
    m = re.search(r'"%s":\s*dict\(\s*indoor=\w+,\s*name="[^"]*",\s*bg="bg (\w+)"' % re.escape(place), src)
    if not m:
        raise SystemExit("no place %r in game/sb_world.rpy (LOCATIONS); pass --bg for a picture of your own" % place)
    return m.group(1)


def rgb(im):
    if im.ch == 3:
        return im
    out = Img(im.w, im.h)
    b, o = im.buf, out.buf
    o[0::3], o[1::3], o[2::3] = b[0::4], b[1::4], b[2::4]
    return out


def fit(im):
    """The picture at exactly 1920x1080: cropped to 16:9 about its centre if
    it came back off-ratio, then resized."""
    im = rgb(im)
    if (im.w, im.h) == (W, H):
        return im
    target = W / float(H)
    if abs(im.w / float(im.h) - target) > 0.002:
        from raster import crop
        if im.w / float(im.h) > target:
            nw = int(im.h * target); x0 = (im.w - nw) // 2
            im = crop(im, x0, 0, x0 + nw, im.h)
        else:
            nh = int(im.w / target); y0 = (im.h - nh) // 2
            im = crop(im, 0, y0, im.w, y0 + nh)
    return resample(im, W, H)


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


def largest_region(grid, gw, gh):
    """(cells, x0, y0, x1, y1) of the largest connected region of changed
    blocks (8-connected), in block units; None when nothing changed."""
    seen = [bytearray(gw) for _y in range(gh)]
    best = None
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
            if best is None or n > best[0]:
                best = (n, x0, y0, x1, y1)
    return best


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


def write_sidecar(path, key, box):
    """Set poses[key] in the view sidecar, keeping everything else in it."""
    data = {}
    if os.path.exists(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except ValueError as e:
            raise SystemExit("%s is not JSON (%s): fix it or remove it first" % (path, e))
        if not isinstance(data, dict):
            raise SystemExit("%s must be a JSON object" % path)
    poses = data.get("poses")
    if not isinstance(poses, dict):
        poses = {}
    poses[key] = [int(v) for v in box]
    data["poses"] = poses
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def install(src, name=None, box=None, bg_path=None, root=None, dry=False):
    root = root or ROOT
    src = os.path.expanduser(src)
    if not os.path.exists(src):
        raise SystemExit("no picture at %s" % src)
    stem, place, who, variant = parse_name(name or src)
    if bg_path is None:
        bg_path = os.path.join(ROOT, "game", "images", "bg",
                               place_bg(place) + ("_" + variant if variant else "") + ".png")
    if not os.path.exists(bg_path):
        raise SystemExit("no room picture at %s to compare with" % bg_path)
    bg = fit(load(bg_path))
    pose = fit(load(src))

    grid, gw, gh = changed_cells(bg, pose)
    total = sum(sum(row) for row in grid)
    frac = total / float(gw * gh)
    region = largest_region(grid, gw, gh)
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
            print("   !! %d changed blocks lie outside the largest region (%d blocks): look at the preview; "
                  "if part of the person is outside the box, pass --box x,y,w,h" % (stray, region[0]))
    else:
        x, y, w, h = box
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
            raise SystemExit("--box %d,%d,%d,%d does not fit inside %dx%d" % (x, y, w, h, W, H))
    print("   box %d,%d  %dx%d" % box)
    preview(bg, pose, box, grid, prev)
    print("   preview -> %s" % prev)
    if dry:
        return box
    key = who + ("__" + variant if variant else "")
    side = os.path.join(root, "game", "layout", "view_%s.json" % place)
    write_sidecar(side, key, box)
    print("   box written -> %s (poses[%r])" % (side, key))
    dest = os.path.join(root, "game", "images", "place", stem + ".png")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    pose.save(dest)
    print("   installed -> %s" % dest)
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

    box, name, bg, root = opt("--box"), opt("--name"), opt("--bg"), opt("--root")
    dry = "--dry" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1 or [a for a in argv if a.startswith("--") and a != "--dry"]:
        print(__doc__); raise SystemExit(1)
    if box is not None:
        try:
            box = tuple(int(v) for v in box.split(","))
            assert len(box) == 4
        except (ValueError, AssertionError):
            raise SystemExit("--box takes four whole numbers: x,y,w,h")
    install(args[0], name=name, box=box, bg_path=bg, root=root, dry=dry)


if __name__ == "__main__":
    main(sys.argv[1:])
