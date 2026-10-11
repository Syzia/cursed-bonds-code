"""
Measure the light people stand in, from the picture itself.

    tools/py_art.sh tools/sample_light.py dorm_common               # the day picture: prints the row
    tools/py_art.sh tools/sample_light.py dorm_common evening       # an hour: evening, night, or lit (5.7a)
    tools/py_art.sh tools/sample_light.py dorm_common --bg <render.png>     # a render not installed yet
    tools/py_art.sh tools/sample_light.py dorm_common --write       # into game/layout/light_dorm_common.json
    tools/py_art.sh tools/sample_light.py --check                   # every light_<place>.json against its picture
    options: --root <a copy of the project>   --layout-dump <file>

docs/UI2_DESIGN.md 6.5, 6.2 row 1, D29. A sprite is tinted by a light row,
[tint, brightness, saturation, shadow opacity] or the same with [shadow lean
in px, shadow stretch] after it. Until this overhaul every row was set by
hand and people glowed in dark rooms. This reads the row off the picture:

  - where people stand comes from the room's standing rows (the layout dump);
  - the band of floor under their soles and the band of wall behind their
    heads are what light them;
  - TINT is those bands' colour (their mean, and their brightest tenth,
    which carries the light's own colour), pulled halfway to white: people
    are lit by the room, not painted with it. Green is held back: a lawn or
    a wall of trees does not tint a face;
  - BRIGHTNESS is the two bands' lightness against a mid-lit room, clamped
    to what a face can take (-0.14 to +0.02);
  - SATURATION falls a little as the room darkens;
  - SHADOW OPACITY is higher on a bright floor and under a lamp, lower in
    flat dim light;
  - LEAN and STRETCH of the shadow: it leans away from the brighter side at
    head height, and stretches when the light is low and warm.

tools/install_redo.py writes the row with the picture; a person may tune it.
--check fails a row that has drifted more than 0.12 in brightness or 0.15 in
any tint channel from what the picture gives, unless the file says why in a
"note": so "matched to the room" stays a measured claim, and a room that is
redone cannot keep the old room's light.

numpy and Pillow: start it through tools/py_art.sh.
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import numpy as np
    from PIL import Image
except ImportError:
    raise SystemExit("numpy and Pillow are needed: start this with tools/py_art.sh")
import game_layout
import redo_measure as rm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOURS = ("", "evening", "night", "lit")    # lit: the room at Night with someone up in it (5.7a)
MID_LEVEL = 120.0           # the lightness of a mid-lit room (the floor band and the wall band together), of 255
DRIFT_BRIGHT, DRIFT_TINT = 0.12, 0.15


def _bands(lay, place):
    """[(floor box, wall box, side)] for every standing spot of the room; with no rows, three spots across the floor."""
    W, H = rm.W, rm.H
    cw, ch = lay.d.get("frames", {}).get("sprite", [760, 1400])
    spots = []
    for _n, rows in sorted((lay.slots(place) if lay.has_place(place) else {}).items()):
        for row in rows:
            spots.append((row[0], row[1], row[2]))
    if not spots:
        spots = [(480, -40, 0.52), (960, -40, 0.52), (1440, -40, 0.52)]
    out = []
    for xc, yoff, zoom in sorted(set(spots)):
        w, h = cw * zoom, ch * zoom
        feet = H + yoff - (ch - 1365) * zoom
        head = H + yoff - h + 0.08 * h
        fx0, fx1 = int(max(0, xc - 0.22 * w)), int(min(W, xc + 0.22 * w))
        fy0, fy1 = int(max(0, feet - 8)), int(min(H - rm.EDGE_ROWS, feet + 34))
        wy0, wy1 = int(max(rm.EDGE_ROWS, head)), int(max(rm.EDGE_ROWS + 4, head + 0.16 * h))
        out.append(((fx0, fy0, fx1, fy1), (fx0, wy0, fx1, wy1), xc))
    return out


def sample(picture, lay, place):
    """The light row a picture gives the people who stand in it: [tint, brightness, saturation, shadow
    opacity, shadow lean, shadow stretch]. picture: a fitted 1080x1920x3 array."""
    floor, wall, left, right = [], [], [], []
    for fb, wb, xc in _bands(lay, place):
        f = picture[fb[1]:fb[3], fb[0]:fb[2]].reshape(-1, 3)
        w_ = picture[wb[1]:wb[3], wb[0]:wb[2]].reshape(-1, 3)
        if len(f):
            floor.append(f)
        if len(w_):
            wall.append(w_)
            (left if xc < rm.W / 2 else right).append(w_)
    if not floor:
        raise SystemExit("no floor to sample in %s" % place)
    floor = np.concatenate(floor)
    wall = np.concatenate(wall) if wall else floor
    both = np.concatenate([floor, wall])
    weights = np.array([0.299, 0.587, 0.114])
    lum = lambda px: float((px @ weights).mean())

    def hue_of(c):
        # Light is warm or cool, never green: a lawn or a wall of trees must not tint a face. Green is held to
        # the larger of red and blue, and the colour is then taken at full strength.
        c = np.array([c[0], min(c[1], max(c[0], c[2])), c[2]], float)
        return c / max(float(c.max()), 1.0) * 255.0

    # The colour of the light: halfway between what the surfaces are on average and what their brightest
    # tenth is (highlights carry the light's colour more than the surface's), then pulled halfway to white.
    l_all = both @ weights
    top = both[l_all >= np.percentile(l_all, 90)].mean(axis=0)
    hue = (hue_of(both.mean(axis=0)) + hue_of(top)) / 2.0
    tint = (hue + 255.0) / 2.0
    lf, lw = lum(floor), lum(wall)
    level = (lf + lw) / 2.0             # a dark wooden floor under a bright wall is still a bright room
    bright = min(0.02, max(-0.14, (level - MID_LEVEL) / 255.0 * 0.4))
    sat = min(1.0, max(0.7, 0.8 + 0.2 * level / MID_LEVEL))
    spread = float(np.percentile(floor @ weights, 90) - np.percentile(floor @ weights, 10)) / 255.0
    opacity = min(0.58, max(0.35, 0.39 + 0.12 * level / 200.0 + 0.10 * spread))
    lean, stretch = 0.0, 1.0
    if left and right:
        ll, lr = lum(np.concatenate(left)), lum(np.concatenate(right))
        lean = max(-30.0, min(30.0, (ll - lr) / 255.0 * 90.0))      # away from the brighter side
    warm = float(hue[0] - hue[2]) / 255.0
    stretch = 1.0 + max(0.0, min(0.35, warm * 0.9))
    return ["#%02x%02x%02x" % tuple(int(round(v)) for v in tint), round(bright, 2) + 0.0, round(sat, 2), round(opacity, 2),
            int(round(lean)), round(stretch, 2)]


def light_path(root, place):
    return os.path.join(root, "game", "layout", "light_%s.json" % place)


def write_row(root, place, hour, row):
    """Set one hour's row in game/layout/light_<place>.json, keeping the others."""
    path = light_path(root, place)
    data = {}
    if os.path.exists(path):
        data = json.load(open(path, encoding="utf-8"))
    data[hour] = row
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(path + ".tmp", path)
    return path


def drift(row, want):
    """Why a row is too far from the sample: [words]."""
    out = []
    if abs(float(row[1]) - float(want[1])) > DRIFT_BRIGHT:
        out.append("its brightness is %+.2f and the picture gives %+.2f" % (row[1], want[1]))
    a, b = [int(row[0][i:i + 2], 16) for i in (1, 3, 5)], [int(want[0][i:i + 2], 16) for i in (1, 3, 5)]
    if max(abs(x - y) for x, y in zip(a, b)) / 255.0 > DRIFT_TINT:
        out.append("its tint is %s and the picture gives %s" % (row[0], want[0]))
    return out


def check(lay, root):
    bad = 0
    folder = os.path.join(root, "game", "layout")
    names = sorted(n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if n.startswith("light_") and n.endswith(".json"))
    for name in names:
        place = name[len("light_"):-len(".json")]
        data = json.load(open(os.path.join(folder, name), encoding="utf-8"))
        if not lay.has_place(place):
            print("FAIL  %s: %r is not a place of the game" % (name, place)); bad += 1
            continue
        for hour in HOURS:
            if hour not in data:
                continue
            pic = lay.bg_path(place, hour, root)
            if not os.path.exists(pic):
                print("FAIL  %s: a row for %s and no picture at %s" % (name, hour or "the day", pic)); bad += 1
                continue
            want = sample(rm.load(pic)[0], lay, place)
            why = drift(data[hour], want)
            if why and not data.get("note"):
                print("FAIL  %s, %s: %s (no \"note\" says why)" % (name, hour or "day", "; ".join(why))); bad += 1
            else:
                print("ok    %s, %s: %s%s" % (name, hour or "day", data[hour], "  (differs, with a note)" if why else ""))
    print("sample_light --check: %s (%d file%s)" % ("FAIL" if bad else "PASS", len(names), "" if len(names) == 1 else "s"))
    return 1 if bad else 0


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

    root, bg = opt("--root") or ROOT, opt("--bg")
    lay = game_layout.load(game_layout.pop_dump_arg(argv), root)
    if "--check" in argv:
        raise SystemExit(check(lay, root))
    write = "--write" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) not in (1, 2) or [a for a in argv if a.startswith("--") and a != "--write"]:
        print(__doc__); raise SystemExit(1)
    place, hour = args[0], (args[1] if len(args) == 2 else "")
    if hour not in HOURS:
        raise SystemExit("the hour is evening, night or lit, not %r" % hour)
    pic = bg or lay.bg_path(place, hour, root)
    if not os.path.exists(pic):
        raise SystemExit("no picture at %s" % pic)
    row = sample(rm.load(pic)[0], lay, place)
    print("%s%s: %s   (from %s)" % (place, " " + hour if hour else "", json.dumps(row), pic))
    if write:
        print("   written -> %s" % write_row(root, place, hour, row))


if __name__ == "__main__":
    main(sys.argv[1:])
