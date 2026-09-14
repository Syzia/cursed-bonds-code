"""
Turn a green-screen character render into a game-ready sprite.

    python3 tools/keysprite.py ~/Downloads/yuji.png yuji_neutral

Keys out the chroma background, removes the green fringe that keying leaves in
hair edges, crops to the figure, and places it on the 760x1400 canvas the game
expects with the feet anchored near the bottom.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc
from pngread import load

OUT_W, OUT_H = 760, 1400
HEAD_ROOM, FOOT_ROOM = 40, 34          # px of empty canvas above / below the figure


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


def _dist(a, b):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


def key_out(im, tol=88.0, soft=46.0, bg=None):
    """RGB(A) -> RGBA, keying against the sampled backdrop colour.

    tol  — distance from the backdrop that still counts as background
    soft — width of the feathered edge beyond that, which is what keeps hair
           from turning into a hard jagged cutout
    """
    bg = bg or sample_bg(im)
    out = Img(im.w, im.h, alpha=True)
    ch = im.ch
    green_bg = bg[1] > bg[0] and bg[1] > bg[2]
    for y in range(im.h):
        for x in range(im.w):
            i = (y * im.w + x) * ch
            r, g, b = im.buf[i], im.buf[i + 1], im.buf[i + 2]
            d = _dist((r, g, b), bg)

            if d <= tol:
                continue                                     # background
            a = 255 if d >= tol + soft else int(255 * (d - tol) / soft)

            # despill: kill the backdrop's cast in the feathered edge pixels
            if green_bg and a < 255 and g > max(r, b):
                g = int(g - (g - max(r, b)) * 0.85)

            j = (y * out.w + x) * 4
            out.buf[j] = r
            out.buf[j + 1] = max(0, min(255, g))
            out.buf[j + 2] = b
            out.buf[j + 3] = a
    return out


def bbox(im, alpha_min=24):
    x0, y0, x1, y1 = im.w, im.h, 0, 0
    for y in range(im.h):
        row = y * im.w * 4
        for x in range(im.w):
            if im.buf[row + x * 4 + 3] >= alpha_min:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    if x1 < x0:
        return 0, 0, im.w, im.h
    return x0, y0, x1 + 1, y1 + 1


def fit(im):
    """Crop to the figure and place it on the game canvas, feet anchored."""
    from raster import crop, scale, paste
    x0, y0, x1, y1 = bbox(im)
    fig = crop(im, x0, y0, x1, y1)

    target_h = OUT_H - HEAD_ROOM - FOOT_ROOM
    f = target_h / float(fig.h)
    if fig.w * f > OUT_W - 40:                     # don't let a wide pose overflow
        f = (OUT_W - 40) / float(fig.w)
    fig = scale(fig, f)

    out = Img(OUT_W, OUT_H, alpha=True)
    paste(out, fig, (OUT_W - fig.w) // 2, OUT_H - FOOT_ROOM - fig.h)
    return out


def side_portrait(sprite, size=360):
    """Head-and-shoulders crop for the dialogue box."""
    from raster import crop, scale
    x0, y0, x1, y1 = bbox(sprite)
    head_h = int((y1 - y0) * 0.34)
    cx = (x0 + x1) // 2
    half = max(head_h, (x1 - x0) // 2)
    cut = crop(sprite, max(0, cx - half), max(0, y0 - 12),
               min(sprite.w, cx + half), min(sprite.h, y0 + head_h + 20))
    return scale(cut, size / float(max(1, cut.w)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); raise SystemExit(1)
    src, name = sys.argv[1], sys.argv[2]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("reading", src)
    im = load(os.path.expanduser(src))
    print("  %dx%d -> keying" % (im.w, im.h))
    keyed = key_out(im)
    sprite = fit(keyed)

    cp = os.path.join(root, "game", "images", "char", name + ".png")
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    sprite.save(cp)
    print("  sprite ->", cp)

    sp = os.path.join(root, "game", "images", "side", name + ".png")
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    side_portrait(sprite).save(sp)
    print("  side   ->", sp)
    print("\nnow run: python3 tools/gen_sprite_defs.py")
