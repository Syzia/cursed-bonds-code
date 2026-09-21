"""
Build the face-oval mask that expression variants are inpainted through.

    python3 tools/facemask.py "~/Desktop/JJK Game images/render.png" yuji
    python3 tools/facemask.py --head "~/Desktop/JJK Game images/render.png" megumi

`--head` writes `masks/<name>_head.png` instead: the whole head, hair and all,
for redrawing a character's hair and face on a body you want to keep.

Otherwise writes `masks/<name>_face.png` beside the render: a white oval on black, the
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


def face_spans(im, keyed):
    """Row-by-row extent of the face itself, as {y: (left, right)}.

    A box-shaped oval fits a round face and fails a pointed one: on Megumi its
    lower corners ran past the jaw onto the green and the top of his collar, so
    every expression would have redrawn a slightly different collar edge. This
    follows the skin instead. The face is the patch of skin connected to the
    middle of the face box -- ears, hands and neck-through-a-collar are skin
    too, but separated from it by hair or line work, so they fall away.

    Each row is filled edge to edge so eyes, brows and mouth (not skin) are
    inside; above the widest row of the upper face the width is held, so
    eyebrows half-hidden under a fringe stay in.
    """
    x0, y0, x1, y1 = face_box(im, keyed)
    bx0, by0 = max(0, x0 - 10), max(0, y0 - 10)
    bx1, by1 = min(im.w, x1 + 10), min(im.h, y1 + 10)
    w = bx1 - bx0

    def skin_at(x, y):
        if keyed.buf[(y * keyed.w + x) * 4 + 3] < 200:
            return False
        i = (y * im.w + x) * im.ch
        return is_skin(im.buf[i], im.buf[i + 1], im.buf[i + 2])

    skin = bytearray(w * (by1 - by0))
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            if skin_at(x, y):
                skin[(y - by0) * w + (x - bx0)] = 1

    # Seed: the skin pixel nearest the middle of the face box.
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    seed = None
    for r in range(0, max(w, by1 - by0)):
        for dy in range(-r, r + 1):
            for dx in (-r, r) if abs(dy) != r else range(-r, r + 1):
                x, y = cx + dx, cy + dy
                if bx0 <= x < bx1 and by0 <= y < by1 and skin[(y - by0) * w + (x - bx0)]:
                    seed = (x, y)
                    break
            if seed: break
        if seed: break
    if not seed:
        raise SystemExit("could not find the face's skin near the middle of the face box")

    seen = bytearray(len(skin))
    stack = [(seed[1] - by0) * w + (seed[0] - bx0)]
    seen[stack[0]] = 1
    rows = {}
    while stack:
        p = stack.pop()
        x, y = p % w, p // w
        l, r = rows.get(y, (x, x))
        rows[y] = (min(l, x), max(r, x))
        # Four neighbours, not eight: a jaw line drawn one pixel thick has
        # diagonal gaps, and through them the face leaks down the neck.
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < by1 - by0:
                q = ny * w + nx
                if skin[q] and not seen[q]:
                    seen[q] = 1
                    stack.append(q)

    ys = sorted(rows)
    top, bot = ys[0], ys[-1]
    # Smooth: a lash line or a strand of fringe can nick one row short.
    spans = {}
    for y in range(top, bot + 1):
        near = [rows[k] for k in range(y - 2, y + 3) if k in rows]
        if not near:
            continue
        ls = sorted(a for a, _ in near); rs = sorted(b for _, b in near)
        spans[y] = (ls[len(ls) // 2], rs[len(rs) // 2])
    # Hold the upper face's widest row up to the top, for the brows.
    upper = [y for y in spans if y <= top + (bot - top) * 0.55]
    if upper:
        wide = max(upper, key=lambda y: spans[y][1] - spans[y][0])
        for y in spans:
            if y < wide:
                spans[y] = (min(spans[y][0], spans[wide][0]), max(spans[y][1], spans[wide][1]))
    return {y + by0: (l + bx0, r + bx0) for y, (l, r) in spans.items()}


def build(src_path, name, out_dir=None, inset=2):
    src_path = os.path.expanduser(src_path)
    im = load(src_path)
    keyed = key_out(im)
    spans = face_spans(im, keyed)

    # Pull in from the face outline so the jaw line itself is never redrawn:
    # it is the edge the key cuts along, and it must match across expressions.
    spans = {y: (l + inset, r - inset) for y, (l, r) in spans.items() if r - l > 2 * inset}
    ys = sorted(spans)
    ys = ys[inset:len(ys) - inset]
    spans = {y: spans[y] for y in ys}
    colmin, colmax = {}, {}
    for y, (l, r) in spans.items():
        for x in range(l, r + 1):
            colmin[x] = min(colmin.get(x, y), y)
            colmax[x] = max(colmax.get(x, y), y)

    mask = Img(im.w, im.h, alpha=False)
    mask.rect(0, 0, im.w, im.h, (0, 0, 0))
    # Feather inward: the soft band lies entirely inside the face.
    for y, (l, r) in spans.items():
        row = y * im.w * 3
        for x in range(l, r + 1):
            d = min(x - l, r - x, y - colmin[x], colmax[x] - y)
            v = 255 if d >= FEATHER else int(255 * d / float(FEATHER))
            mask.buf[row + x * 3:row + x * 3 + 3] = bytes((v, v, v))

    out_dir = out_dir or os.path.join(os.path.dirname(src_path), "masks")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, name + "_face.png")
    mask.save(out)

    xs = [x for l, r in spans.values() for x in (l, r)]
    print("face      x %d..%d  y %d..%d, following the skin" % (min(xs), max(xs), ys[0], ys[-1]))
    print("mask   -> %s" % out)
    return out


def head_box(im, keyed):
    """Where the head is, and where the clothing starts around it.

    Returns (x0, y0, x1, cut, face): the hair-and-face extent; `cut`, the first
    row where clothing appears beside the head -- the narrowest point below the
    face, which is the jaw with a collar or hood rising either side of it; and
    the face box, whose bottom can sit lower than `cut` when a tall collar
    wraps up round the chin.
    """
    face = face_box(im, keyed)
    fx0, fy0, fx1, fy1 = face
    alpha_min = 128

    def span(y):
        row = y * keyed.w * 4
        xs = [x for x in range(keyed.w) if keyed.buf[row + x * 4 + 3] >= alpha_min]
        return (xs[0], xs[-1]) if xs else None

    mid = (fy0 + fy1) // 2
    best, cut = None, fy1
    for y in range(mid, min(keyed.h, fy1 + 40)):
        sp = span(y)
        if sp and (best is None or sp[1] - sp[0] < best):
            best, cut = sp[1] - sp[0], y
    cut += 3

    top = bbox(keyed)[1]
    xs0, xs1 = keyed.w, 0
    for y in range(top, cut):
        sp = span(y)
        if sp:
            xs0, xs1 = min(xs0, sp[0]), max(xs1, sp[1])
    return xs0, top, xs1, cut, face


def build_head(src_path, name, out_dir=None, margin=0.14):
    """Mask for redrawing the whole head -- hair and face -- on a body you keep.

    Above the clothing line it is a dome reaching past the current hair into
    the green on every side, so a fuller hairstyle has somewhere to go. Below
    that line it follows only the skin of the chin and neck, row by row, so a
    collar that rises up either side of the jaw is left exactly as it was.
    """
    src_path = os.path.expanduser(src_path)
    im = load(src_path)
    keyed = key_out(im)
    x0, y0, x1, cut, (fx0, fy0, fx1, fy1) = head_box(im, keyed)
    pad = int((x1 - x0) * margin)
    left, right, top = max(0, x0 - pad), min(im.w, x1 + pad), max(0, y0 - pad)

    mask = Img(im.w, im.h, alpha=False)
    mask.rect(0, 0, im.w, im.h, (0, 0, 0))
    cx, rx, ry = (left + right) / 2.0, (right - left) / 2.0, cut - top
    steps = max(1, FEATHER)
    for s in range(steps + 1):
        v = int(255 * s / float(steps))
        d = steps - s
        mask.poly(superellipse(cx, cut, rx - d, ry - d, n=3.2), (v, v, v))
    for y in range(cut, im.h):
        row = y * im.w * 3
        mask.buf[row:row + im.w * 3] = bytes(im.w * 3)

    # Chin and neck: whatever skin sits between the collar's sides, plus the
    # outline around it. The collar's own edge is a drawn dark line, so a hard
    # mask boundary along it hides in the line work.
    chin = fy1 + 3
    for y in range(cut, min(im.h, chin)):
        xs = []
        for x in range(max(0, fx0 - 20), min(im.w, fx1 + 20)):
            i = (y * im.w + x) * im.ch
            if keyed.buf[(y * keyed.w + x) * 4 + 3] >= 200 and \
               is_skin(im.buf[i], im.buf[i + 1], im.buf[i + 2]):
                xs.append(x)
        if not xs:
            continue
        row = y * im.w * 3
        for x in range(max(0, xs[0] - 3), min(im.w, xs[-1] + 4)):
            mask.buf[row + x * 3:row + x * 3 + 3] = b"\xff\xff\xff"

    out_dir = out_dir or os.path.join(os.path.dirname(src_path), "masks")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, name + "_head.png")
    mask.save(out)
    print("head      x %d..%d  from y %d; collar beside the jaw from y %d; chin to y %d"
          % (x0, x1, y0, cut, chin))
    print("mask   -> %s" % out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); raise SystemExit(1)
    if "--head" in sys.argv:
        build_head(args[0], args[1])
    else:
        build(args[0], args[1])
