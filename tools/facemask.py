"""
Build the face-oval mask that expression variants are inpainted through.

    python3 tools/facemask.py "~/Desktop/JJK Game images/render.png" yuji

Writes `masks/<name>_face.png` beside the render: a white oval on black, the
same pixel size as the render, to be loaded into ComfyUI as the inpaint mask.

The point of the oval is what it EXCLUDES. ComfyUI's ImageCompositeMasked
returns the destination pixel wherever the mask is zero, so any region the oval
does not cover comes back byte-identical -- hair silhouette, uniform, and the
flat green backdrop all survive untouched across all six expressions. That is
what makes the six variants composite-match: they are literally the same body.

So the oval has to sit strictly inside the hairline. It is found by locating
skin in the upper part of the figure and insetting from there, then feathered
inward so the whole soft edge lands on skin rather than on hair.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img
from pngread import load
from keysprite import key_out, bbox

INSET_X = 0.92    # shrink the skin box horizontally before drawing the shape
INSET_Y = 0.99    # ...and vertically. Kept close to 1: the box top IS skin.
SQUARENESS = 2.8  # superellipse exponent. 2.0 is a plain ellipse, and a plain
                  # ellipse cuts the eyebrows off at its corners -- a furrowed
                  # brow being most of what an angry expression is. Higher
                  # fills the corners in without widening the waist.
FEATHER = 10      # px of soft edge, entirely inside the shape


def is_skin(r, g, b):
    """Warm, light, red-leading — face, not hair and not uniform.

    `r > g > b` alone is not enough: salmon-pink hair and a red hoodie both
    satisfy it. What separates them is where green sits between blue and red.
    Measured off the first render — pink hair 0.08-0.11, red hoodie 0.01-0.04,
    facial skin 0.39-0.46 — so green being at least a quarter of the way up is
    a clean cut with a wide margin on both sides.
    """
    if not (r > 115 and r > g > b):
        return False
    span = r - b
    return 22 < span < 130 and (g - b) >= 0.28 * span


def superellipse(cx, cy, rx, ry, n=None, steps=96):
    """Points on |x/rx|^n + |y/ry|^n = 1 — an oval with fuller corners."""
    n = SQUARENESS if n is None else n
    pts = []
    for i in range(steps):
        t = 2.0 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + rx * math.copysign(abs(c) ** (2.0 / n), c),
                    cy + ry * math.copysign(abs(s) ** (2.0 / n), s)))
    return pts


def face_box(im, keyed):
    """Bounding box of the face, in the render's own coordinates."""
    fx0, fy0, fx1, fy1 = bbox(keyed)
    fh = fy1 - fy0
    # The head lives in the top third; going lower starts collecting hands.
    limit = fy0 + int(fh * 0.34)

    xs, ys = [], []
    for y in range(fy0, min(limit, im.h)):
        for x in range(fx0, fx1):
            if keyed.buf[(y * keyed.w + x) * 4 + 3] < 200:
                continue
            i = (y * im.w + x) * im.ch
            if is_skin(im.buf[i], im.buf[i + 1], im.buf[i + 2]):
                xs.append(x); ys.append(y)
    if len(xs) < 200:
        raise SystemExit("could not find a face — is this render keyed on green "
                         "and is the head in the top third of the figure?")

    # Trim the tails: stray skin pixels (an ear lobe through hair, a hand raised
    # to the chin) would otherwise stretch the box well past the face.
    xs.sort(); ys.sort()
    k = max(1, len(xs) // 50)
    return xs[k], ys[k], xs[-k], ys[-k]


def build(src_path, name, out_dir=None):
    src_path = os.path.expanduser(src_path)
    im = load(src_path)
    keyed = key_out(im)
    x0, y0, x1, y1 = face_box(im, keyed)

    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rx, ry = (x1 - x0) / 2.0 * INSET_X, (y1 - y0) / 2.0 * INSET_Y

    mask = Img(im.w, im.h, alpha=False)
    mask.rect(0, 0, im.w, im.h, (0, 0, 0))
    # Feather inward: concentric shrinking copies from the rim to the core, so
    # every partially-lit pixel of the mask lies on skin.
    steps = max(1, FEATHER)
    for s in range(steps + 1):
        v = int(255 * s / float(steps))
        d = steps - s
        mask.poly(superellipse(cx, cy, rx - d, ry - d), (v, v, v))

    out_dir = out_dir or os.path.join(os.path.dirname(src_path), "masks")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, name + "_face.png")
    mask.save(out)

    print("face box  x %d..%d  y %d..%d" % (x0, x1, y0, y1))
    print("shape     centre (%d, %d)  radii %d x %d  squareness %.1f"
          % (cx, cy, rx, ry, SQUARENESS))
    print("mask   -> %s" % out)
    print("\ncrop for the inpaint (square, power-of-two friendly):")
    side = 1
    while side < max(rx, ry) * 2 * 1.3:
        side *= 2
    cxi, cyi = int(cx - side / 2), int(cy - side / 2)
    print("  ImageCrop  x=%d  y=%d  width=%d  height=%d" % (max(0, cxi), max(0, cyi), side, side))
    print("  ImageCompositeMasked must use the SAME x,y with resize_source=false")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); raise SystemExit(1)
    build(sys.argv[1], sys.argv[2])
