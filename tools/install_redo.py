"""
Put a background into the game, and prove first that it may go in.

  A ROOM REDONE IN PLACE (the same camera, the same things, the new look):
    tools/py_art.sh tools/install_redo.py dorm_common <render a> <render b> --dry     # a verdict for each
    tools/py_art.sh tools/install_redo.py dorm_common <render a> <render b> --choose a  # installs that one only
  ITS EVENING OR NIGHT, relit from the day picture:
    tools/py_art.sh tools/install_redo.py --relight dorm_common evening <a> <b> [--choose a]
    tools/py_art.sh tools/install_redo.py dorm_common <hour picture> --dry --against <day picture>   # measure a pair
  THE CANARY (5.2): measure a render against the place's picture from before the overhaul; installs nothing:
    tools/py_art.sh tools/install_redo.py dorm_common <render> --dry --against-rev1
  A PICTURE COMPOSED AGAIN, OR A NEW PLACE, with its layout:
    tools/py_art.sh tools/install_redo.py --compose courtyard <render> --dry           # the OLD layout on the new picture
    tools/py_art.sh tools/install_redo.py --compose courtyard <render> --layout hot_courtyard.json view_courtyard.json
            [--refs refs.json] [--waive <fact id> --owner-said "<what the owner said>"] [--dry]
  options: --root <a copy of the project>  --layout-dump <file>  --keep <folder>  --record <campus.json>
           --batch <n>  --date <yyyy-mm-dd>      (a batch is 0, 3, ... or a file of one: 3a, 21b)

docs/UI2_DESIGN.md 5.4, 5.5, 5.6, 5.7, K6, K7, D18, D19. A picture is
installed only by the tool that proves it. Every render gets one of three
verdicts, in plain words:

  PASS      it can go in.
  LOOK      here is what changed; choose it or not. (A picture with a new
            window view or a named addition always comes back as a LOOK.)
  REFUSED   what moved, vanished or appeared. It cannot be chosen; if both
            versions are refused, run the pair once more.

IN PLACE, the proof is, on the 1920x1080 picture the game shows:
  1. FIT. Static and letterbox bars are refused. A 2752x1536 render is the
     room at 1920x1072, laid 4 px down.
  2. NOTHING MOVED. The whole picture is off by 0 or 1 px. Round every
     registered point of the place (each exit, each hotspot, the feet of
     every standing row, each pose box, the outline of each foreground and
     the outline of each traced shape, D60) a 192 px window must agree
     within 3 px. A window that moved refuses the picture and is named
     ("the outline of the shape traced for the hotspot tv moved 9 px
     right"); so does one that no longer lines up at all (the door an exit
     sits on moved further than the 24 px a shift is looked for, or was
     painted out). Two things are read as what they are:
       GLASS. A point that lies on glass (the keep list's `windows` rows:
       the panes of a door or a window) is held by what is round the glass,
       its post, its handle, its frame. The view through it may be changed
       on purpose, and is shown as a LOOK.
       A FLOOR. A point where people stand is not held by the lines between
       the boards: a floor drawn again has other boards, and a relight lays
       a window's grid of light across it. Such a point is refused only when
       the floor's outline and what stands on it moved (a wider window, on a
       coarse edge map); otherwise it is a LOOK ("the floor is drawn
       differently where people stand").
  3. NOTHING VANISHED. Every `keep` and `doors` row of the room's keep list
     (tools/bgs/keep/<picture>.json), a 110 px box round every hotspot and
     the box round every foreground object must still be there. A thing
     that sits a little way off is named as moved, not as gone. A door is
     kept by its frame, not by the view through its glass. The box round a
     hotspot is not judged where the room's named addition (`allow`) stands
     on that hotspot's own object (the laptop at the computer). A thing
     that reads as gone inside its own box while that box, 16 px wider,
     agrees as well as the picture does (a pale calendar on a wall that
     became lighter) is a LOOK: "fainter, or drawn differently inside its
     outline".
  4. NOTHING WAS ADDED. Every `empty` row, the floor among them, has not
     gained fine edge (a jacket, a cup, leaves), unless it is in `allow`.
     A wide zone (a floor) is judged whole and again in overlapping 160 px
     parts, so one bag set on a wide floor is found and its part named. A
     floor that is DRAWN AGAIN (its parts no longer agree with the game's:
     other boards, sunlight on it) cannot be read that way, and is a LOOK
     ("the floor is drawn again: look that nothing new stands on it").
  5. SHARPER, against the picture the place had BEFORE the overhaul
     (revision 1, from git by the manifest's `rev1_commit`), never against
     the installed one: twice as sharp passes, 1.3 to 2 is a LOOK, under 1.3
     is refused. Steps 2 to 4 are measured against the installed picture,
     which is what must not move.
  6. Anything else that changed is shown, not refused: LOOK. The picture is
     read in 320 px tiles and again in 120 px cells; one that no longer
     agrees with the game's picture (a new view through a window, a thing
     drawn on a wall) is named by its corner and tinted on the preview.
  7. A PREVIEW, shots/art/redo_<picture>_<version>.jpg: old beside new with
     every point and zone drawn on both.
  A `change` row is left out of steps 3 and 4; its outline must not move.
  A RELIGHT runs steps 1 and 2, and step 3 with a threshold of its own; a
  night picture loses edge in its dark corners and gains pools of light, and
  neither is a fault. It is NOT judged for added things (5.7), and never
  refused for one: A RELIGHT IS READ BY EYE BESIDE ITS DAY PICTURE for a lamp,
  a blanket, a bench. One case is shown as a LOOK, because it can be measured
  without a false alarm: a small `empty` row of the keep list (not a floor)
  that gained fine edge against what is round it ("something new may be on
  the sofa's near arm").

FOR THE VERSION THE OWNER NAMES (--choose), when it is a PASS or a LOOK:
  - the picture, game/images/bg/<picture>.png;
  - its row in game/layout/pictures.json: the revision, the render, the
    shift and the sharpness measured, `rev1_commit` (the commit that holds
    the place's first picture) and `from_commit` (the commit that holds the
    picture this one replaced), so the proof can be rerun from git alone;
  - the light people stand in, game/layout/light_<place>.json, measured from
    the picture (tools/sample_light.py);
  - the room's foregrounds, cut again from the new picture (tools/make_fg.py;
    for an hour with no outline of its own the day outline is copied first,
    which is right because the relight proved nothing moved). A foreground
    file is never deleted (K9);
  - in the campus record, the picture as chosen;
  - a copy of the render in ~/Desktop/JJK Game images/ui2/approved/.
  Nothing else. The old picture is not copied anywhere: it is in git. A
  room's hot_ and view_ files are not touched (they carry no `for_rev`).

COMPOSED, the proof is its layout: tools/check_layout.py (the screen's rules)
and tools/check_campus.py (no fixed fact of the campus record contradicted).
A layout that stands against a fixed fact is refused and the fact is named;
it goes in only with `--waive <that fact>` and the owner's own words, and the
record then holds a `waived` row. On success one step writes the picture,
its layout files stamped with `for_rev`, the facts the layout fixes in the
campus record, the manifest row stamped with the record's hash, and the
reference crops of the buildings it shows (tools/bgs/refs/, never over one
that exists: the first chosen picture that shows a building is its reference).

The game's numbers come from the layout dump (tools/game_layout.py), which
refuses a dump that is out of date; in a worktree pass --layout-dump <file>.
AN INSTALL WRITES FILES UNDER game/layout/, SO THE DUMP IS OUT OF DATE
AFTERWARDS: run tools/smoke.sh u2_dump before the next tool.

--root <dir> reads from and writes under a copy of the project: how an
install is tried without touching the game. Exit status 0 when a version
could go in (or went in), 1 when none can, 2 when the dump is out of date.
numpy, scipy and Pillow: started with plain python3 it starts itself again
through tools/py_art.sh.
"""
import sys, os

TOOLS = os.path.dirname(os.path.abspath(__file__))
try:
    import numpy as np
    from PIL import Image
    import scipy                        # noqa: F401  (redo_measure needs it)
except ImportError:
    if os.environ.get("JJK_PY_ART"):
        raise SystemExit("numpy, scipy and Pillow are needed, and tools/py_art.sh's Python does not have them")
    os.execv("/bin/bash", ["/bin/bash", os.path.join(TOOLS, "py_art.sh"), os.path.abspath(__file__)] + sys.argv[1:])

import json, re, subprocess, datetime, shutil, copy

sys.path.insert(0, TOOLS)
import game_layout
import check_campus
import redo_measure as rm
import sample_light

ROOT = os.path.dirname(TOOLS)
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
KEEP_DIR = os.path.join(ROOT, "tools", "bgs", "keep")
HOURS = ("evening", "night")
AUTO_BOX = rm.AUTO_BOX


# ---- small readers ------------------------------------------------------------------------------------------
def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        return json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s is not JSON: %s" % (path, e))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(path + ".tmp", path)


def resolve(lay, name):
    """(place key, picture stem) for a place key or a picture's name."""
    if lay.has_place(name):
        return name, lay.bg_stem(name)
    place = lay.place_of_stem(name)
    if place:
        return place, name
    raise SystemExit("%s is not a place of the game, nor the name of a place's picture" % name)


def keep_list(stem, place, keep_dir=None):
    for name in (stem, place):
        got = read_json(os.path.join(keep_dir or KEEP_DIR, name + ".json"))
        if got is not None:
            for key in ("keep", "empty", "allow", "change", "doors", "windows"):
                for row in got.get(key, []):
                    if not row.get("name") or not (row.get("box") or row.get("poly")):
                        raise SystemExit("the keep list of %s: every `%s` row needs a name and a box or a poly" % (stem, key))
            return got
    return {}


def batch_id(text):
    """--batch as the manifest holds it (5.5): the number 3 for a whole batch, the text "3a" for one file of a
    batch (the ids of tools/art/batches.json). Anything else is refused."""
    if text is None:
        return None
    if re.match(r"^(0|[1-9]\d?)$", text):
        return int(text)
    if re.match(r"^(0|[1-9]\d?)[a-z]$", text):
        return text
    raise SystemExit("--batch %s: a batch is a whole number (0, 3, 21) or one file of a batch (3a, 21b)" % text)


def fg_polygons(root, place):
    return read_json(os.path.join(root, "tools", "fg", place + ".json"), {}) or {}


def version_of(path, k):
    m = re.search(r"_([ab])_\d+_?\.png$", os.path.basename(path))
    return m.group(1) if m else "ab"[k]


def points_for(lay, place, root, polys, hour=""):
    """Every registered point of a place: where "nothing moved" is measured."""
    out = []
    for p in lay.points(place, root):
        out.append({"name": "the spot %s sits on" % p["name"], "at": p["at"], "kind": p["kind"], "id": p["id"]})
    seen = set()
    for n, x, y in lay.slot_feet(place):
        if (x, y) not in seen:
            seen.add((x, y))
            out.append({"name": "the floor where people stand (a row of %d, at x %d)" % (n, x), "at": (x, y), "kind": "feet"})
    for key, box in sorted(lay.poses(place).items()):
        out.append({"name": "the place of the painted pose %s" % key, "at": (box[0] + box[2] // 2, box[1] + box[3] // 2),
                    "kind": "pose"})
    poly = polys.get(hour) or polys.get("")
    if poly:
        n = len(poly)
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) // 96))
            for s in range(steps):
                x, y = x0 + (x1 - x0) * s / float(steps), y0 + (y1 - y0) * s / float(steps)
                if 0 <= x < rm.W and 0 <= y < rm.H:
                    out.append({"name": "the outline of the foreground object", "at": (int(x), int(y)), "kind": "fg"})
    # D60: the picture is what is clicked, so the wall under each traced shape's outline is held as well
    names = dict((p["id"], p["name"]) for p in lay.points(place, root))
    for hid, shape in sorted(lay.shapes(place).items()):
        for x, y in outline_samples(shape):
            out.append({"name": "the outline of the shape traced for %s" % names.get(hid, hid), "at": (x, y),
                        "kind": "shape", "id": hid})
    return out


def outline_samples(shape, step=96):
    """Points along the outline of a traced shape (its polygons), one at each corner and every `step` px between."""
    out = []
    for poly in shape:
        n = len(poly)
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) // step))
            for k in range(steps):
                x, y = x0 + (x1 - x0) * k / float(steps), y0 + (y1 - y0) * k / float(steps)
                if 0 <= x < rm.W and 0 <= y < rm.H and (int(x), int(y)) not in out:
                    out.append((int(x), int(y)))
    return out


def auto_keep(lay, place, root, polys, hour=""):
    """5.4: every hotspot's object and every foreground object is kept without being written down."""
    out = []
    h = AUTO_BOX // 2
    for p in lay.points(place, root):
        if p["kind"] == "hotspot":
            out.append({"name": "the thing at %s" % p["name"], "box": [p["at"][0] - h, p["at"][1] - h, AUTO_BOX, AUTO_BOX],
                        "auto": True})
    poly = polys.get(hour) or polys.get("")
    if poly:
        xs, ys = [q[0] for q in poly], [q[1] for q in poly]
        x0, y0 = max(0, int(min(xs))), max(0, int(min(ys)))
        out.append({"name": "the object the foreground is cut round", "auto": True,
                    "box": [x0, y0, min(rm.W, int(max(xs))) - x0, min(rm.H, int(max(ys))) - y0]})
    return out


# ---- git: where the old pictures are ------------------------------------------------------------------------
def _git(root, *args):
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout


def committed(root, rel):
    """(the commit that holds this file as it is on disk, or None; why not)."""
    path = os.path.join(root, rel)
    disk = open(path, "rb").read()
    for repo in dict.fromkeys([root, ROOT]):
        code, blob = _git(repo, "show", "HEAD:" + rel)
        if code == 0 and blob == disk:
            code, out = _git(repo, "log", "-1", "--format=%H", "--", rel)
            if code == 0 and out.strip():
                return out.decode().strip(), None
    return None, "%s is not committed as it stands" % rel


def rev1_picture(root, manifest, stem, hour=""):
    """(the picture the place had before the overhaul, as an array; where it came from)."""
    rel = "game/images/bg/%s.png" % stem
    row = (manifest.get("pictures") or {}).get(stem) or {}
    commit = row.get("rev1_commit")
    if commit and re.match(r"^[0-9a-f]{7,40}$", commit):
        for repo in dict.fromkeys([root, ROOT]):
            code, blob = _git(repo, "show", "%s:%s" % (commit, rel))
            if code == 0 and blob:
                import io
                return rm.fit(Image.open(io.BytesIO(blob)))[0], "git, commit %s" % commit[:10]
        raise SystemExit("%s: git has no such picture at commit %s (the manifest's rev1_commit)" % (rel, commit))
    if row:
        raise SystemExit("%s is at revision %s and its manifest row has no rev1_commit: the picture it had before the "
                         "overhaul cannot be taken from git" % (stem, row.get("rev")))
    return rm.load(os.path.join(root, rel))[0], "the game's file (nothing is installed yet, so it is revision 1)"


# ---- the report ---------------------------------------------------------------------------------------------
def report(letter, path, note, got):
    print("version %s   %s" % (letter, os.path.basename(path)))
    if note:
        print("  %-9s %s" % ("fit", note))
    for key, text in (got or {}).get("lines", []):
        print("  %-9s %s" % (key, text))
    v = got["verdict"]
    if v == "PASS":
        print("  VERDICT   PASS: it can go in")
    elif v == "LOOK":
        print("  VERDICT   LOOK: here is what changed; choose it or not")
        for line in got["look"]:
            print("            - %s" % line)
    else:
        print("  VERDICT   REFUSED: it cannot be chosen")
        for line in got["refused"]:
            print("            - %s" % line)
        for line in got.get("look", [])[:4]:
            print("            (also: %s)" % line)
        if len(got.get("look", [])) > 4:
            print("            (and %d more parts of the picture that are drawn differently)" % (len(got["look"]) - 4))


def refused_fit(e):
    return {"verdict": "REFUSED", "refused": [str(e)], "look": [], "lines": [], "figures": {}, "marks": {}}


# ---- writing --------------------------------------------------------------------------------------------------
def load_manifest(root):
    return check_campus.load_manifest(root)


def manifest_path(root):
    return os.path.join(root, "game", "layout", "pictures.json")


def record_path(root, given=None):
    return given or os.path.join(root, "tools", "bgs", "campus.json")


def keep_approved(root, render):
    dest = os.path.join(IMAGES, "ui2", "approved") if os.path.abspath(root) == os.path.abspath(ROOT) else os.path.join(root, "approved")
    os.makedirs(dest, exist_ok=True)
    shutil.copy(render, os.path.join(dest, os.path.basename(render)))
    return os.path.join(dest, os.path.basename(render))


def write_light(root, lay, place, hour, picture, pics, parent, parent_rev):
    row = sample_light.sample(picture, lay, place)
    path = sample_light.write_row(root, place, hour, row)
    pics["light_%s%s" % (place, "_" + hour if hour else "")] = {"of": parent, "of_rev": parent_rev}
    print("   light     %s -> %s (%s)" % (json.dumps(row), os.path.relpath(path, root), hour or "day"))


def recut(root, place, stem, hour, pics, parent, parent_rev):
    """The room's foreground for this picture, cut again from it. Never deletes one (K9)."""
    path = os.path.join(root, "tools", "fg", place + ".json")
    polys = fg_polygons(root, place)
    if not polys:
        return
    if hour not in polys:
        if "" not in polys:
            return
        polys[hour] = polys[""]         # valid: the relight proved nothing moved (5.4 step 8)
        with open(path, "w", encoding="utf-8") as f:
            f.write("{\n" + ",\n".join('  %s: %s' % (json.dumps(k), json.dumps(v)) for k, v in sorted(polys.items())) + "\n}\n")
        print("   foreground the day outline is copied to the %s key of tools/fg/%s.json" % (hour, place))
    import make_fg
    make_fg.cut(place, hour, polys[hour], bg_stem=stem, root=root)
    pics["fg_%s%s" % (place, "_" + hour if hour else "")] = {"of": parent, "of_rev": parent_rev}


def cut_refs(root, picture, refs):
    """5.2: a crop of each building the picture shows; the first chosen picture is the reference from then on."""
    folder = os.path.join(root, "tools", "bgs", "refs")
    for key, box in sorted((refs or {}).items()):
        dest = os.path.join(folder, key + ".png")
        if os.path.exists(dest):
            print("   reference %s.png is kept (an earlier chosen picture already shows it)" % key)
            continue
        x, y, w, h = [int(v) for v in box]
        rm.save(picture[max(0, y):y + h, max(0, x):x + w], dest)
        print("   reference %s.png cut (%dx%d)" % (key, w, h))


# ---- in place, and a relight ----------------------------------------------------------------------------------
def run_inplace(o):
    root = o["root"]
    lay = game_layout.load(o["dump"], root)
    place, stem = resolve(lay, o["picture"])
    hour = o["hour"] or ""
    relight = bool(hour) or bool(o["against"])
    day_path = os.path.join(root, "game", "images", "bg", stem + ".png")
    target = stem + ("_" + hour if hour else "")
    manifest = load_manifest(root)
    if o["against"]:
        base_path, base_words = os.path.expanduser(o["against"]), "the picture named by --against"
    else:
        base_path, base_words = day_path, ("the day picture in the game" if hour else "the picture in the game")
    if not os.path.exists(base_path):
        raise SystemExit("no picture at %s to measure against" % base_path)
    if hour and not o["against"] and not o["dry"] and check_campus.rev_of(manifest, stem) < 2:
        raise SystemExit("%s's %s cannot be installed yet: its day picture is not installed in the new look (K8)"
                         % (lay.name(place), hour))
    old = rm.load(base_path)[0]
    rev1, rev1_from = (None, None) if relight else rev1_picture(root, manifest, stem)
    if o["against_rev1"]:
        if relight:
            raise SystemExit("--against-rev1 is for a day picture")
        old, base_words = rev1, "the picture the place had before the overhaul (%s)" % rev1_from
    kl = keep_list(stem, place, o["keep"])
    polys = fg_polygons(root, place)
    points = points_for(lay, place, root, polys, hour)
    # the room's painted doors are held by "nothing vanished" as well: an exit sits on one (5.4 step 2)
    keep = list(kl.get("keep", [])) + list(kl.get("doors", [])) + auto_keep(lay, place, root, polys, hour)
    print("%s (%s.png), %s; measured against %s" % (lay.name(place), target, "a relight" if relight else "redone in place", base_words))
    if not kl:
        print("  note      no keep list at tools/bgs/keep/%s.json: only the registered points and hotspots are held" % stem)
    results = {}
    for k, path in enumerate(o["renders"]):
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            raise SystemExit("no render at %s" % path)
        letter = version_of(path, k)
        if letter in results:
            # two renders whose names carry the same letter: the second takes the letter still free
            letter = next((l for l in "abcdefgh" if l not in results), "r%d" % (k + 1))
        try:
            new, note = rm.load(path)
            got = rm.judge(old, new, points, keep, kl.get("empty", []), kl.get("allow", []), kl.get("change", []),
                           rev1=rev1, relight=relight, windows=kl.get("windows", []))
        except rm.Refused as e:
            new, note, got = None, None, refused_fit(e)
        report(letter, path, note, got)
        if new is not None:
            prev = os.path.join(root, "shots", "art", "redo_%s_%s.jpg" % (target, letter))
            rm.preview(old, new, prev, points, keep, kl.get("empty", []), kl.get("allow", []), kl.get("change", []),
                       got["marks"], "%s, version %s: %s" % (target, letter, got["verdict"]), windows=kl.get("windows", []))
            print("  preview   %s" % prev)
        if o["against_rev1"] or o["dry"]:
            print("  figures   %s" % json.dumps(got["figures"], sort_keys=True))
        results[letter] = (path, new, got)
    can = sorted(l for l, r in results.items() if r[2]["verdict"] != "REFUSED")
    if o["dry"] or o["against_rev1"] or o["against"]:
        if not o["dry"]:
            print("(measured only: nothing is installed with --against or --against-rev1)")
        return 0 if can else 1
    if not can:
        print("%s refused: run the pair once more" % ("it is" if len(results) == 1 else "both versions are"))
        return 1
    choose = o["choose"]
    if choose is None:
        print("to install one, say which: --choose %s" % " or --choose ".join(can))
        return 0
    if choose not in results:
        raise SystemExit("--choose %s: there is no version %s here (there %s %s)"
                         % (choose, choose, "is" if len(results) == 1 else "are", " and ".join(sorted(results))))
    path, new, got = results[choose]
    if got["verdict"] == "REFUSED":
        raise SystemExit("version %s was REFUSED and cannot be chosen: %s" % (choose, "; ".join(got["refused"])))

    # everything is decided before anything is written
    rel = "game/images/bg/%s.png" % target
    dest = os.path.join(root, rel)
    pics = dict(manifest.get("pictures") or {})
    old_row = pics.get(target) or {}
    from_commit, why = (None, None)
    if os.path.exists(dest):
        from_commit, why = committed(root, rel)
        if from_commit is None and os.path.abspath(root) == os.path.abspath(ROOT):
            raise SystemExit("%s: commit it first. The row records the commit that holds the picture this install "
                             "replaces, so that the proof can be rerun from git alone." % why)
    rev = check_campus.rev_of(manifest, target) + 1
    date = o["date"]
    row = {"rev": rev, "kind": "relight" if hour else "inplace", "render": os.path.basename(path),
           "shift": got["figures"].get("shift", [0, 0])}
    if o["batch"] is not None:
        row["batch"] = o["batch"]
    elif "batch" in old_row:
        row["batch"] = old_row["batch"]
    if from_commit:
        row["from_commit"] = from_commit
    if hour:
        row["of"], row["of_rev"] = stem, check_campus.rev_of(manifest, stem)
    else:
        row["rev1_commit"] = old_row.get("rev1_commit") or from_commit or "not committed (a copy)"
        if got["figures"].get("sharp"):
            row["sharp"] = got["figures"]["sharp"]
    record = None
    if not hour:
        rpath = record_path(root, o["record"])
        if os.path.exists(rpath):
            record = check_campus.load_record(rpath)
            rec = check_campus.Rec(record)
            if place in rec.places:
                if rec.chosen(place) is None:
                    check_campus.fix_from_layout(record, place, {}, rev, date, os.path.basename(path), "inplace", row.get("batch"))
                else:
                    check_campus.rechoose(record, stem, rev, os.path.basename(path), date)
            else:
                record = None
    print("installing version %s of %s as revision %d" % (choose, target, rev))
    rm.save(new, dest)
    print("   picture   -> %s" % rel)
    pics[target] = row
    write_light(root, lay, place, hour, new, pics, target, rev)
    recut(root, place, stem, hour, pics, target, rev)
    write_json(manifest_path(root), {"pictures": pics})
    print("   manifest  -> game/layout/pictures.json (%s: %s)" % (target, json.dumps(row, sort_keys=True)))
    if record is not None:
        check_campus.save_record(record, record_path(root, o["record"]))
        print("   record    -> the campus record has %s as chosen, at revision %d" % (stem, rev))
    if o["refs"]:
        cut_refs(root, new, read_json(o["refs"], {}))
    print("   approved  -> %s" % keep_approved(root, path))
    stale = sorted(k for k, r in pics.items() if r.get("of") == target and r.get("of_rev") != rev)
    if stale:
        print("   now stale (made for the picture this replaced; the game falls back until each is remade): %s" % ", ".join(stale))
    print("   the layout dump is now out of date: run tools/smoke.sh u2_dump before the next tool")
    return 0


# ---- composed --------------------------------------------------------------------------------------------------
LAYOUT_NAMES = re.compile(r"^(hot|view|area|light|pose|fg)_(\w+)\.json$|^map_campus\.json$")


def run_compose(o):
    root = o["root"]
    lay = game_layout.load(o["dump"], root)
    name = o["picture"]
    is_map = name.startswith("area_") or name == "map_campus"
    place, stem = (None, name) if is_map else resolve(lay, name)
    if len(o["renders"]) != 1:
        raise SystemExit("--compose takes the one render the owner chose")
    render = os.path.expanduser(o["renders"][0])
    if not os.path.exists(render):
        raise SystemExit("no render at %s" % render)
    try:
        new, note = rm.load(render)
    except rm.Refused as e:
        print("REFUSED: %s" % e)
        return 1
    manifest = load_manifest(root)
    rev = check_campus.rev_of(manifest, stem) + 1
    print("%s (%s.png), composed again; %s" % (lay.name(place) if place else stem, stem, note))
    files = [os.path.expanduser(f) for f in o["layout"]]
    for f in files:
        if not os.path.exists(f):
            raise SystemExit("no layout file at %s" % f)
        if not LAYOUT_NAMES.match(os.path.basename(f)):
            raise SystemExit("%s is not a layout file's name (hot_<place>.json, view_<place>.json, area_<key>.json, "
                             "map_campus.json, fg_<place>.json)" % os.path.basename(f))
        read_json(f)
    dest = os.path.join(root, "game", "images", "bg", stem + ".png")
    old = rm.load(dest)[0] if os.path.exists(dest) else new
    prev = os.path.join(root, "shots", "art", "redo_%s.jpg" % stem)

    def drawn(spots_file):
        pts = []
        if place:
            for p in lay.points(place, root):
                pts.append({"name": p["name"], "at": p["at"]})
            got = read_json(spots_file, {}) if spots_file else {}
            if got.get("spots"):
                pts = [{"name": k, "at": tuple(v)} for k, v in sorted(got["spots"].items())]
        return pts

    if not files:
        if not o["dry"]:
            raise SystemExit("a composed picture is installed only together with its layout: pass --layout <files>, "
                             "or --dry to see the old layout drawn on the new picture")
        rm.preview(old, new, prev, drawn(None), title="%s: the OLD layout on the new picture" % stem)
        print("  layout    none given: the OLD layout is drawn on the new picture")
        print("  preview   %s  (what still sits on its thing is kept; the rest is moved at the layout sitting)" % prev)
        return 0

    refused = []
    # the screen's rules (tools/check_layout.py, U0d3)
    checker = os.path.join(TOOLS, "check_layout.py")
    if os.path.exists(checker):
        cmd = [sys.executable if not os.environ.get("JJK_PY_ART") else "python3", checker, "--layout"] + files
        if o["dump"]:
            cmd += ["--layout-dump", o["dump"]]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = p.stdout.decode("utf-8", "replace").strip()
        for line in text.splitlines():
            print("  layout    %s" % line)
        if p.returncode != 0:
            refused.append("its layout does not pass the screen's rules (tools/check_layout.py; the lines above say which)")
    else:
        print("  layout    tools/check_layout.py is not built yet: the screen's rules were NOT checked")
        if os.path.abspath(root) == os.path.abspath(ROOT) and not o["dry"]:
            refused.append("the screen's rules cannot be checked (tools/check_layout.py is missing), so nothing is "
                           "installed into the game")
    # the campus record
    rpath = record_path(root, o["record"])
    record = check_campus.load_record(rpath)
    date = o["date"]
    trial = copy.deepcopy(record)
    for fact in o["waive"]:
        if not o["owner_said"]:
            raise SystemExit("--waive is refused without the owner's own word: add --owner-said \"<what the owner said "
                             "in this session>\". A waiver says a chosen picture may stand against a fact an earlier "
                             "chosen picture fixed; only the owner can accept that.")
        check_campus.add_waiver(trial, fact, stem, rev, date, o["owner_said"])
    out = check_campus.Out()
    campus_files = [f for f in files if re.match(r"^(hot_|area_)\w+\.json$|^map_campus\.json$", os.path.basename(f))]
    check_campus.check_layout_files(check_campus.Rec(trial), campus_files, out, lay.d)
    for text in out.texts("FAIL"):
        print("  campus    FAIL    %s" % text)
        refused.append(text)
    for level in ("REPORT", "WAIT"):
        for text in out.texts(level):
            print("  campus    %-7s %s" % (level, text))
    against = sorted(set(re.findall(r"against the fixed fact ([^\]]+)\]", " ".join(out.texts("FAIL")))))
    hot = [f for f in files if place and os.path.basename(f) == "hot_%s.json" % place]
    rm.preview(old, new, prev, drawn(hot[0] if hot else None), title="%s: the new layout on the new picture" % stem)
    print("  preview   %s" % prev)
    if refused:
        print("  VERDICT   REFUSED: it cannot be installed")
        for line in refused:
            print("            - %s" % line)
        if against:
            print("            To install it all the same the owner must accept that, in their own words: --waive %s "
                  "--owner-said \"...\"" % " --waive ".join(a.split(",")[0].strip() for a in against))
        return 1
    print("  VERDICT   %s" % ("LOOK: it stands against a fact the owner has waived" if o["waive"] else "PASS: its layout fits the screen and the campus record"))
    if o["dry"]:
        return 0

    # the facts this layout fixes, in a copy first: the record must still pass in full afterwards
    fixed = {"rewritten": [], "moved": [], "off_plan": []}
    batch = o["batch"]
    if place and place in check_campus.Rec(trial).places:
        kind, key, spots = (None, None, {})
        if hot:
            kind, key, spots = check_campus.read_layout_file(hot[0])
        # A fixed fact a waiver stands beside is not rewritten by the picture that stands against it: not its
        # side, and not its place in the order from left to right either.
        t0 = check_campus.Rec(trial)
        held = dict((r["id"], dict((k, r.get(k)) for k in ("side", "order", "half", "plan")))
                    for r in t0.rows("exit", place=place) if t0.is_fixed(r) and t0.waiver(r["id"], stem))
        fixed = check_campus.fix_from_layout(trial, place, spots, rev, date, os.path.basename(render), "composed", batch)
        for row in check_campus.Rec(trial).rows("exit", place=place):
            for k, v in held.get(row["id"], {}).items():
                if v is None:
                    row.pop(k, None)
                else:
                    row[k] = v
        fixed["off_plan"] = [i for i in fixed["off_plan"] if i not in held]
        rec = check_campus.Rec(trial)
        for bkey in sorted((read_json(o["refs"], {}) if o["refs"] else {})):
            b = rec.buildings.get(bkey)
            if b is not None and not rec.is_fixed(b):
                trial["proposed"].remove(b); trial["fixed"].append(b)
                b["by"] = {"picture": stem, "rev": rev}
                rec = check_campus.Rec(trial)
        touches = check_campus.touched_by(trial, fixed["rewritten"] + fixed["moved"])
        if touches:
            trial["pictures"][stem]["touches"] = touches
        after = check_campus.Out()
        check_campus.check_record(check_campus.Rec(trial), lay.d, after)
        if after.count("FAIL"):
            for text in after.texts("FAIL"):
                print("  record    FAIL    %s" % text)
            print("  VERDICT   REFUSED: with this picture's facts written in, the campus record would no longer pass "
                  "tools/check_campus.py; nothing was written")
            return 1
    elif is_map:
        print("  record    a map fixes no fact and is not written into the campus record")
    from_commit = None
    rel = "game/images/bg/%s.png" % stem
    if os.path.exists(dest):
        from_commit, why = committed(root, rel)
        if from_commit is None and os.path.abspath(root) == os.path.abspath(ROOT):
            raise SystemExit("%s: commit it first, so that the picture this install replaces can be taken from git" % why)

    print("installing %s as revision %d" % (stem, rev))
    rm.save(new, dest)
    print("   picture   -> %s" % rel)
    pics = dict(manifest.get("pictures") or {})
    for f in files:
        base = os.path.basename(f)
        data = read_json(f)
        if base.startswith("fg_"):
            target = os.path.join(root, "tools", "fg", base[3:])
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy(f, target)
            print("   layout    -> tools/fg/%s" % base[3:])
            continue
        if re.match(r"^(hot|view|area)_", base):
            data["for_rev"] = rev
        write_json(os.path.join(root, "game", "layout", base), data)
        print("   layout    -> game/layout/%s%s" % (base, " (for_rev %d)" % rev if "for_rev" in data else ""))
    check_campus.save_record(trial, rpath)
    row = {"rev": rev, "kind": "composed", "render": os.path.basename(render), "record": check_campus.record_hash(rpath)}
    if batch is not None:
        row["batch"] = batch
    if from_commit:
        row["from_commit"] = from_commit
        row["rev1_commit"] = (pics.get(stem) or {}).get("rev1_commit") or from_commit
    if o["waive"]:
        row["waiver"] = ", ".join(o["waive"])
    pics[stem] = row
    if place:
        write_light(root, lay, place, "", new, pics, stem, rev)
        recut(root, place, stem, "", pics, stem, rev)
    write_json(manifest_path(root), {"pictures": pics})
    print("   manifest  -> game/layout/pictures.json (%s: %s)" % (stem, json.dumps(row, sort_keys=True)))
    print("   record    -> %s: %d fact%s written; hash %s..." % (os.path.relpath(rpath, root), len(fixed["rewritten"]) + 1,
                                                                 "" if not fixed["rewritten"] else "s", row["record"][:12]))
    if fixed["rewritten"]:
        print("             proposals rewritten to match the picture: %s" % ", ".join(fixed["rewritten"]))
    if fixed["moved"]:
        print("             buildings moved on the ground plan: %s" % ", ".join(fixed["moved"]))
    if fixed["off_plan"]:
        print("             the ground plan cannot place these beside the other chosen pictures (reported on every run): %s"
              % ", ".join(fixed["off_plan"]))
    if place and trial.get("pictures", {}).get(stem, {}).get("touches"):
        print("             unmade pictures whose prompt this changes: %s" % ", ".join(trial["pictures"][stem]["touches"]))
    if o["waive"]:
        print("             waived, with the owner's word: %s" % ", ".join(o["waive"]))
    if o["refs"]:
        cut_refs(root, new, read_json(o["refs"], {}))
    print("   approved  -> %s" % keep_approved(root, render))
    stale = sorted(k for k, r in pics.items() if r.get("of") == stem and r.get("of_rev") != rev)
    if stale:
        print("   now stale (the game falls back until each is remade): %s" % ", ".join(stale))
    print("   the layout dump is now out of date: run tools/smoke.sh u2_dump before the next tool")
    return 0


def main(argv):
    def opt(flag, n=1):
        if flag not in argv:
            return None
        i = argv.index(flag)
        vals = argv[i + 1:i + 1 + n]
        if len(vals) < n or any(v.startswith("--") for v in vals):
            raise SystemExit("%s needs %s" % (flag, "a value" if n == 1 else "%d values" % n))
        del argv[i:i + 1 + n]
        return vals[0] if n == 1 else vals

    def many(flag):
        out = []
        while flag in argv:
            i = argv.index(flag)
            j = i + 1
            while j < len(argv) and not argv[j].startswith("--"):
                out.append(argv[j]); j += 1
            if j == i + 1:
                raise SystemExit("%s needs a value" % flag)
            del argv[i:j]
        return out

    def flag(name):
        if name in argv:
            argv.remove(name)
            return True
        return False

    o = {"dump": game_layout.pop_dump_arg(argv), "root": opt("--root") or ROOT, "keep": opt("--keep"),
         "record": opt("--record"), "batch": opt("--batch"), "choose": opt("--choose"), "against": opt("--against"),
         "refs": opt("--refs"), "owner_said": opt("--owner-said"),
         "date": opt("--date") or datetime.date.today().isoformat()}
    relight = opt("--relight", 2)
    o["waive"] = many("--waive")
    o["layout"] = many("--layout")
    o["dry"], o["against_rev1"], compose = flag("--dry"), flag("--against-rev1"), flag("--compose")
    o["hour"] = None
    if relight:
        if relight[1] not in HOURS:
            raise SystemExit("--relight needs a place and an hour: --relight dorm_common evening|night")
        o["hour"] = relight[1]
        argv.insert(0, relight[0])
    if [a for a in argv if a.startswith("--")] or len(argv) < 2:
        print(__doc__); raise SystemExit(1)
    o["picture"], o["renders"] = argv[0], argv[1:]
    o["batch"] = batch_id(o["batch"])
    if o["choose"] is not None and o["choose"] not in ("a", "b"):
        raise SystemExit("--choose is a or b")
    if compose:
        raise SystemExit(run_compose(o))
    if len(o["renders"]) > 2:
        raise SystemExit("one picture has two versions: give one or two renders")
    raise SystemExit(run_inplace(o))


if __name__ == "__main__":
    main(sys.argv[1:])
