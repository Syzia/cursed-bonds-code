"""
Cut a room's foreground layer out of its own background.

    python3 tools/make_fg.py dorm_common            # every variant in tools/fg/dorm_common.json
    python3 tools/make_fg.py dorm_common evening    # one variant
    python3 tools/make_fg.py --all                  # every file in tools/fg/
    python3 tools/make_fg.py cafeteria --dry        # preview only, install nothing

People on the place view stand behind this layer: a table edge, a desk
(PHASE2_DESIGN.md D38, 4.5). The layer is the background's own pixels inside
one polygon, so it costs nothing and can never drift from the picture.

The polygons are tool input, never read by the game: tools/fg/<place>.json,

    {"": [[x, y], ...], "evening": [[x, y], ...]}

one polygon a picture, keyed by the picture's variant ("" is the day picture;
"evening" / "night" are game/images/bg/<name>_<variant>.png). Points are in
the 1920x1080 frame and may lie outside it. Trace the object a pixel or two
inside its outline: a loose polygon carries a rim of floor over the person's
legs. Look at it first with `python3 tools/layout_sheet.py view_<place>`.

Writes game/images/fg/fg_<place>.png or fg_<place>_<variant>.png (1920x1080,
see-through outside the polygon, the edge softened over about a pixel) and a
preview, shots/art/fg_<place>[_<variant>].png: the cut on a flat colour beside
the picture with the cut tinted. Pure Python: raster.py and pngread.py.

Which picture a place has is read from the game's layout dump
(tools/game_layout.py), which refuses in one line when it is out of date; in
a worktree pass --layout-dump <file> (docs/UI2_DESIGN.md 5.4). A foreground
file is never deleted (K9): a save made in dialogue in that room holds its
path. tools/install_redo.py recuts a room's foregrounds itself after every
install of the room or of one of its hours.
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img
import game_layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FG = os.path.join(ROOT, "tools", "fg")
W, H = 1920, 1080
SUB = 4                                   # sub-rows a pixel row, for a soft edge


def read_polygons(place, path=None):
    path = path or os.path.join(FG, place + ".json")
    if not os.path.exists(path):
        raise SystemExit("no polygon file at %s" % path)
    try:
        data = json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s is not JSON: %s" % (path, e))
    if not isinstance(data, dict) or not data:
        raise SystemExit("%s must be a JSON object, {\"<variant>\": [[x, y], ...]}" % path)
    for v, pts in data.items():
        ok = isinstance(pts, list) and len(pts) >= 3 and all(
            isinstance(p, list) and len(p) == 2
            and all(isinstance(q, (int, float)) and not isinstance(q, bool) for q in p) for p in pts)
        if not ok:
            raise SystemExit("%s: %r must be a list of at least three [x, y] points" % (path, v))
    return data


def coverage(pts, w=W, h=H):
    """{y: [alpha 0..255 for x in x0..x1], x0} for the rows the polygon
    touches: how much of each pixel lies inside it (even-odd rule), from SUB
    sub-rows a row with exact spans along x."""
    ys = [p[1] for p in pts]
    y_lo, y_hi = max(0, int(min(ys))), min(h - 1, int(max(ys)) + 1)
    n = len(pts)
    rows = {}
    for y in range(y_lo, y_hi + 1):
        acc = None
        for s in range(SUB):
            sy = y + (s + 0.5) / SUB
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if y1 == y2:
                    continue
                if min(y1, y2) <= sy < max(y1, y2):
                    xs.append(x1 + (sy - y1) * (x2 - x1) / float(y2 - y1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                a, b = max(0.0, xs[k]), min(float(w), xs[k + 1])
                if b <= a:
                    continue
                if acc is None:
                    acc = [0.0] * w
                ia, ib = int(a), int(b)
                if ia == ib:
                    acc[ia] += b - a
                else:
                    acc[ia] += ia + 1 - a
                    for x in range(ia + 1, ib):
                        acc[x] += 1.0
                    if ib < w:
                        acc[ib] += b - ib
        if acc is not None:
            rows[y] = [min(255, int(v * 255.0 / SUB + 0.5)) for v in acc]
    return rows


def cut(place, variant, pts, dry=False, bg_stem=None, root=None, lay=None):
    """Cut one foreground. bg_stem: the place's picture name, when the caller
    already knows it (the installer does; otherwise it is read from the
    dump). root: another tree to read the picture from and write under."""
    root = root or ROOT
    if bg_stem is None:
        bg_stem = (lay or game_layout.load()).bg_stem(place)
    stem = bg_stem + ("_" + variant if variant else "")
    src = os.path.join(root, "game", "images", "bg", stem + ".png")
    if not os.path.exists(src):
        raise SystemExit("no picture at %s for the %s variant of %s" % (src, variant or "day", place))
    bg = load(src)
    if (bg.w, bg.h) != (W, H):
        raise SystemExit("%s is %dx%d, not %dx%d" % (src, bg.w, bg.h, W, H))
    rows = coverage([(float(x), float(y)) for x, y in pts])
    out = Img(W, H, alpha=True)
    prev = Img(W * 2, H, fill=(190, 60, 160))
    ch = bg.ch
    kept = 0
    for y in range(H):
        line = bg.buf[y * W * ch:(y + 1) * W * ch]
        rgb = bytearray(W * 3)
        if ch == 3:
            rgb[:] = line
        else:
            for x in range(W):
                rgb[x * 3:x * 3 + 3] = line[x * 4:x * 4 + 3]
        # Right half of the preview: the picture, darkened outside the cut.
        dim = bytearray(v // 3 for v in rgb)
        cov = rows.get(y)
        if cov:
            for x in range(W):
                a = cov[x]
                if a:
                    kept += 1
                    j = (y * W + x) * 4
                    out.buf[j:j + 3] = rgb[x * 3:x * 3 + 3]
                    out.buf[j + 3] = a
                    for k in range(3):
                        p = (y * W * 2 + x) * 3 + k
                        prev.buf[p] = (rgb[x * 3 + k] * a + prev.buf[p] * (255 - a)) // 255
                        dim[x * 3 + k] = (rgb[x * 3 + k] * a + dim[x * 3 + k] * (255 - a)) // 255
        p = (y * W * 2 + W) * 3
        prev.buf[p:p + W * 3] = dim
    if not kept:
        raise SystemExit("the %s polygon of %s covers nothing inside the frame" % (variant or "day", place))
    name = "fg_%s%s.png" % (place, "_" + variant if variant else "")
    shots = os.path.join(root, "shots", "art")
    os.makedirs(shots, exist_ok=True)
    prev.save(os.path.join(shots, name))
    print("%-28s %5.1f%% of the frame, from %s.png" % (name, 100.0 * kept / (W * H), stem))
    print("   preview -> %s" % os.path.join(shots, name))
    if not dry:
        dest = os.path.join(root, "game", "images", "fg")
        os.makedirs(dest, exist_ok=True)
        out.save(os.path.join(dest, name))
        print("   installed -> game/images/fg/%s" % name)
    return name


def main(argv):
    lay = game_layout.load(game_layout.pop_dump_arg(argv))
    dry = "--dry" in argv
    everything = "--all" in argv
    args = [a for a in argv if not a.startswith("--")]
    if [a for a in argv if a.startswith("--") and a not in ("--dry", "--all")] or (not args and not everything):
        print(__doc__); raise SystemExit(1)
    if everything:
        places = sorted(f[:-5] for f in os.listdir(FG) if f.endswith(".json"))
        want = None
    else:
        places, want = [args[0]], (args[1] if len(args) > 1 else None)
    for place in places:
        polys = read_polygons(place)
        if want is not None and want not in polys:
            raise SystemExit("tools/fg/%s.json has no %r polygon (it has %s)"
                             % (place, want, ", ".join(repr(k) for k in sorted(polys))))
        for variant in sorted(polys):
            if want is None or variant == want:
                cut(place, variant, polys[variant], dry=dry, lay=lay)


if __name__ == "__main__":
    main(sys.argv[1:])
