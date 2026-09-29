"""
Turn green-screen character renders into game-ready sprites.

    python3 tools/keysprite.py ~/Downloads/render.png yuji_neutral   # one file
    python3 tools/keysprite.py --batch "~/Desktop/JJK Game images"   # a whole folder

Keys out the chroma background, removes the green fringe that keying leaves in
hair edges, crops to the figure, and places it on the 760x1400 canvas the game
expects with the feet anchored near the bottom.

Batch mode takes every PNG named `<character>_<expression>.png`, keys it, and
runs a QA pass on each: a render whose backdrop was not actually green, whose
figure runs off the edge of the frame, or which still carries a green fringe is
reported rather than silently shipped. With 78 sprites to produce, the one bad
render needs to announce itself.

Characters are scaled against each other rather than each being stretched to
fill the canvas — see HEIGHT_CM. Feet land on the same line whatever the height,
so the sprites can be drawn at a common baseline.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc
from pngread import load

OUT_W, OUT_H = 760, 1400
HEAD_ROOM, FOOT_ROOM = 40, 34          # px of empty canvas above / below the figure

EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")

# Standing height in cm. The canvas is sized so the TALLEST character fills it;
# everyone else is scaled against that and keeps the leftover space above their
# head. Without this every figure gets stretched to the same pixel height and
# Nobara ends up eye to eye with Gojo.
#
# These are DRAWN heights: the figure's bounding box includes the hair. Where a
# hairstyle adds real height the canon figure is raised to compensate, measured
# so the chin-to-feet distance matches canon against Yuji -- Megumi's spikes
# take 16% of his drawn height, so a canon 175 is drawn at 181.
HEIGHT_CM = {
    "yuji": 173, "megumi": 181, "nobara": 160, "maki": 180, "panda": 200,
    "toge": 179, "shoko": 180, "gojo": 195, "yaga": 191, "ijichi": 180,
    "utahime": 178, "sana": 167, "mc": 172,
}
TALLEST_CM = 200.0

# Canvas width per character, where the default 760 would squeeze a wide
# build: Panda is about 0.6 as wide as he is tall, so at his full 200 cm he
# needs about 800 px plus margin.
CANVAS_W = {"panda": 880}


def sample_bg(im, n=12):
    """Average the corners — whatever colour the backdrop is, that is the key."""
    ch = im.ch
    acc = [0, 0, 0]
    cnt = 0
    for cy in (0, im.h - n):
        for cx in (0, im.w - n):
            for y in range(cy, cy + n):
                for x in range(cx, cx + n):
                    i = (y * im.w + x) * ch
                    acc[0] += im.buf[i]; acc[1] += im.buf[i + 1]; acc[2] += im.buf[i + 2]
                    cnt += 1
    return tuple(v // cnt for v in acc)


def _chroma(c):
    """How green a colour is, independent of how bright it is.

    RGB distance cannot separate a muted dark backdrop from dark navy clothing
    — both are simply dark. The green channel's lead over the other two can:
    a #3f6944 backdrop scores +37, navy trousers score -8.
    """
    return c[1] - max(c[0], c[2])


def screen_key(bg):
    """(kind, lean) for the backdrop colour bg: `lean(r, g, b)` is how far a
    pixel leans toward the screen's hue, independent of its brightness. Green
    is the house screen; magenta is for characters with green in them (Maki's
    dark green hair would lean toward a green screen); blue for completeness.
    None when the backdrop has no colour cast to key on.
    """
    r, g, b = bg
    if g - max(r, b) >= 12:
        return "green", lambda r, g, b: g - (r if r > b else b)
    if min(r, b) - g >= 12:
        return "magenta", lambda r, g, b: (r if r < b else b) - g
    if b - max(r, g) >= 12:
        return "blue", lambda r, g, b: b - (r if r > g else g)
    return None


PURE_GREEN = (0, 255, 0)


def rescreen(im, colour=PURE_GREEN):
    """The figure laid over a new flat backdrop, keyed off whatever it was
    rendered on. A character rendered on magenta goes onto pure green for the
    rest of the pipeline, whose key thresholds scale with the backdrop: on
    pure green only a green lean above 82 counts as backdrop, where Krea's
    muted green (64, 106, 68) keys from 12, and no hair reaches 82."""
    keyed = key_out(im)
    out = Img(im.w, im.h, alpha=False)
    for p in range(im.w * im.h):
        j = p * 4
        a = keyed.buf[j + 3] / 255.0
        for k in range(3):
            out.buf[p * 3 + k] = int(keyed.buf[j + k] * a + colour[k] * (1 - a) + 0.5)
    return out


def _dist(a, b):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


def backdrop_regions(im, bg, lo, lean=None):
    """Which green pixels are actually backdrop, as a bytearray over the image.

    Keying every green pixel would also key a character's own green parts:
    Megumi's sea-green eyes, a jade earring, a green tie. What separates them
    from the screen is connectivity. The backdrop is one region that touches
    the frame edge; gaps in a pose (between an arm and the body, a hand on a
    hip) are sealed off from it but are large, and are the backdrop's exact
    colour. An iris is small, sealed inside the face, and a different green.

    So a green region counts as backdrop if it touches the edge, OR is bigger
    than any eye could be, OR is close to the backdrop's own colour. Anything
    else is part of the character and stays opaque.
    """
    w, h, ch, buf = im.w, im.h, im.ch, im.buf
    n = w * h
    green = bytearray(n)
    lean = lean or (lambda r, g, b: g - (r if r > b else b))
    for p in range(n):
        i = p * ch
        if lean(buf[i], buf[i + 1], buf[i + 2]) > lo:
            green[p] = 1

    backdrop = bytearray(n)
    seen = bytearray(n)
    pocket = max(400, n // 2500)           # ~420px at 768x1368; an iris is ~120
    for start in range(n):
        if not green[start] or seen[start]:
            continue
        stack, region, edge = [start], [], False
        seen[start] = 1
        while stack:
            p = stack.pop()
            region.append(p)
            x, y = p % w, p // w
            if x == 0 or y == 0 or x == w - 1 or y == h - 1:
                edge = True
            for q in (p - 1 if x > 0 else -1, p + 1 if x < w - 1 else -1,
                      p - w if y > 0 else -1, p + w if y < h - 1 else -1):
                if q >= 0 and green[q] and not seen[q]:
                    seen[q] = 1
                    stack.append(q)
        keep = edge or len(region) >= pocket
        if not keep:
            sr = sg = sb = 0
            for p in region:
                i = p * ch
                sr += buf[i]; sg += buf[i + 1]; sb += buf[i + 2]
            k = float(len(region))
            keep = _dist((sr / k, sg / k, sb / k), bg) < 45
        if keep:
            for p in region:
                backdrop[p] = 1
    return backdrop


def key_out(im, bg=None, cut=0.62, feather=0.30):
    """RGB(A) -> RGBA, keying whatever colour the backdrop turns out to be.

    cut/feather are fractions of the backdrop's own chroma, so the key adapts
    to a vivid #00b140 screen and a muted #3f6944 one alike.
    """
    bg = bg or sample_bg(im)
    screen = screen_key(bg)
    kind, lean = screen if screen else (None, None)
    bg_chroma = lean(*bg) if lean else 0
    out = Img(im.w, im.h, alpha=True)
    ch = im.ch

    # A backdrop with no colour cast at all (grey/white) has to fall back to
    # plain distance; there is no hue to key on.
    use_chroma = lean is not None
    lo = bg_chroma * (cut - feather)
    hi = bg_chroma * cut
    # Connectivity protects a character's own green (an eye, a tie) from a
    # green key. Another screen colour is only chosen for a character with none
    # of it on them, so there is nothing to protect, and protecting would leave
    # backdrop trapped in thin gaps as coloured flecks: a thin sliver's mean
    # is mostly blended edge pixels, so it doesn't read as backdrop colour
    # (it happened between Maki's wrist and skirt).
    backdrop = backdrop_regions(im, bg, lo, lean) if kind == "green" else None

    for y in range(im.h):
        for x in range(im.w):
            p = y * im.w + x
            i = p * ch
            r, g, b = im.buf[i], im.buf[i + 1], im.buf[i + 2]

            if use_chroma:
                v = lean(r, g, b)
                if v <= lo or (backdrop is not None and not backdrop[p]):
                    a = 255                                   # figure, green or not
                elif v >= hi:
                    continue                                  # background
                else:
                    a = int(255 * (hi - v) / (hi - lo))
            else:
                d = _dist((r, g, b), bg)
                if d <= 60:
                    continue
                a = 255 if d >= 106 else int(255 * (d - 60) / 46)

            # despill: strip the backdrop's cast out of feathered edge pixels,
            # or every strand of hair carries a green fringe onto dark scenes
            if use_chroma and a < 255:
                if kind == "green" and g > max(r, b):
                    g = int(g - (g - max(r, b)) * 0.9)
                elif kind == "magenta" and min(r, b) > g:
                    e = (min(r, b) - g) * 0.9
                    r, b = int(r - e), int(b - e)
                elif kind == "blue" and b > max(r, g):
                    b = int(b - (b - max(r, g)) * 0.9)

            j = p * 4
            out.buf[j] = max(0, min(255, r))
            out.buf[j + 1] = max(0, min(255, g))
            out.buf[j + 2] = max(0, min(255, b))
            out.buf[j + 3] = a
    return out


def _edge_min(w):
    """How many opaque pixels in a row before it counts as part of the figure.

    A couple of stray pixels left behind by the key would otherwise drag the
    bounding box out to the frame edge, and every figure is scaled from that
    box — so one speck silently resizes the whole character.
    """
    return max(3, int(w * 0.01))


def bbox(im, alpha_min=24, min_px=None):
    if min_px is None:
        min_px = _edge_min(im.w)
    cols = [0] * im.w
    rows = [0] * im.h
    for y in range(im.h):
        row = y * im.w * 4
        n = 0
        for x in range(im.w):
            if im.buf[row + x * 4 + 3] >= alpha_min:
                n += 1
                cols[x] += 1
        rows[y] = n

    ys = [y for y, n in enumerate(rows) if n >= min_px]
    xs = [x for x, n in enumerate(cols) if n >= min_px]
    if not ys or not xs:
        return 0, 0, im.w, im.h
    return xs[0], ys[0], xs[-1] + 1, ys[-1] + 1


def fit(im, height_cm=None, out_w=OUT_W):
    """Crop to the figure and place it on the game canvas, feet anchored.

    height_cm scales the figure against the tallest member of the cast instead
    of stretching it to fill the canvas, so a 160cm first-year does not come out
    the same size as a 2m panda.
    """
    from raster import crop, smooth_scale, paste
    x0, y0, x1, y1 = bbox(im)
    fig = crop(im, x0, y0, x1, y1)

    target_h = OUT_H - HEAD_ROOM - FOOT_ROOM
    if height_cm:
        target_h *= height_cm / TALLEST_CM
    f = target_h / float(fig.h)
    if fig.w * f > out_w - 40:                     # don't let a wide pose overflow
        f = (out_w - 40) / float(fig.w)
    # Area-averaged, not nearest-neighbour: shrinking a render by ~0.85 with
    # nearest-neighbour drops about one row and column in six, which breaks
    # one-pixel line art into stair-steps.
    fig = smooth_scale(fig, f)

    out = Img(out_w, OUT_H, alpha=True)
    paste(out, fig, (out_w - fig.w) // 2, OUT_H - FOOT_ROOM - fig.h)
    return out


def qa(src, keyed, name):
    """Look for the ways a render goes wrong, and say which one happened.

    Returns a list of complaint strings — empty means the render is fine.
    """
    problems = []
    bg = sample_bg(src)
    screen = screen_key(bg)
    lean = screen[1] if screen else None
    if lean is None:
        problems.append("backdrop has no colour to key on (%d,%d,%d) — keyed on "
                        "plain distance, expect a rough cutout" % bg)

    total = keyed.w * keyed.h
    kept = fringe = 0
    for i in range(0, len(keyed.buf), 4):
        a = keyed.buf[i + 3]
        if a < 8:
            continue
        kept += 1
        # Only soft edge pixels can be fringe; an opaque green pixel is one the
        # key deliberately kept, like a green eye.
        if a < 255 and lean and lean(keyed.buf[i], keyed.buf[i + 1], keyed.buf[i + 2]) > 18:
            fringe += 1
    pct = 100.0 * kept / total
    if pct > 85:
        problems.append("kept %.0f%% of the frame — the key did not take" % pct)
    elif pct < 4:
        problems.append("kept only %.1f%% of the frame — the figure was keyed away" % pct)
    if fringe:
        problems.append("%d edge pixels still carry the backdrop's colour (%.3f%% of the figure)"
                        % (fringe, 100.0 * fringe / max(1, kept)))

    # A figure touching the frame edge was cropped by the renderer, so its real
    # height is unknown and scaling it against the cast is guesswork.
    x0, y0, x1, y1 = bbox(keyed)
    touching = [side for side, at in (("top", y0 <= 1), ("bottom", y1 >= keyed.h - 1),
                                      ("left", x0 <= 1), ("right", x1 >= keyed.w - 1)) if at]
    if touching:
        problems.append("figure runs off the %s of the frame — re-render with the "
                        "whole body inside it, or this sprite's scale is a guess"
                        % "/".join(touching))
    elif min(y0, keyed.h - y1) < keyed.h * 0.02:
        problems.append("only %dpx of clearance above/below the figure — close "
                        "enough to the edge that the next render will clip"
                        % min(y0, keyed.h - y1))
    return problems


def install(src_path, name, quiet=False):
    """Key one render and write both the sprite and its side portrait."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key = name.split("_")[0]

    im = load(os.path.expanduser(src_path))
    keyed = key_out(im)
    problems = qa(im, keyed, name)
    sprite = fit(keyed, HEIGHT_CM.get(key), CANVAS_W.get(key, OUT_W))

    cp = os.path.join(root, "game", "images", "char", name + ".png")
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    sprite.save(cp)

    sp = os.path.join(root, "game", "images", "side", name + ".png")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    side_portrait(sprite).save(sp)

    if not quiet:
        print("  %dx%d -> %s" % (im.w, im.h, cp))
    return problems


def batch(folder):
    """Ingest every `<character>_<expression>.png` in a folder."""
    folder = os.path.expanduser(folder)
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    done, skipped, flagged = [], [], []

    for f in names:
        stem = os.path.splitext(f)[0]
        bits = stem.split("_")
        if len(bits) < 2 or bits[0] not in HEIGHT_CM or bits[1] not in EXPRESSIONS:
            skipped.append(f)
            continue
        name = bits[0] + "_" + bits[1]
        print("%-28s -> %s" % (f, name))
        problems = install(os.path.join(folder, f), name)
        for pr in problems:
            print("   !! " + pr)
        (flagged if problems else done).append(name)

    print("\n%d keyed, %d flagged, %d ignored" % (len(done) + len(flagged), len(flagged), len(skipped)))
    if skipped:
        print("ignored (name them <character>_<expression>.png to pick them up):")
        for f in skipped:
            print("   " + f)
    if flagged:
        print("flagged — these were written anyway, look at them before you trust them:")
        for n in flagged:
            print("   " + n)
    return done, flagged


def side_portrait(sprite, size=360):
    """Head-and-shoulders crop for the dialogue box."""
    from raster import crop, smooth_scale
    x0, y0, x1, y1 = bbox(sprite)
    head_h = int((y1 - y0) * 0.34)
    cx = (x0 + x1) // 2
    half = max(head_h, (x1 - x0) // 2)
    cut = crop(sprite, max(0, cx - half), max(0, y0 - 12),
               min(sprite.w, cx + half), min(sprite.h, y0 + head_h + 20))
    return smooth_scale(cut, size / float(max(1, cut.w)))


if __name__ == "__main__":
    args = sys.argv[1:]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args and args[0] == "--batch":
        if len(args) < 2:
            print(__doc__); raise SystemExit(1)
        batch(args[1])
    elif len(args) >= 2:
        print("reading", args[0])
        for pr in install(args[0], args[1]):
            print("   !! " + pr)
    else:
        print(__doc__); raise SystemExit(1)

    print("\nnow run: python3 tools/gen_sprite_defs.py")
