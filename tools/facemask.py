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
    facial skin 0.39-0.46 (Gojo's paler skin 0.23-0.31) — so green being at
    least 0.18 of the way up is a clean cut with a margin on both sides.

    Orange-brown hair passes that test too, so skin must also be pale, with
    (r - b) / r at most 0.40.
    """
    if not (r > 115 and r > g > b):
        return False
    span = r - b
    # Ginger hair has skin's hue exactly, so hue can't separate them;
    # saturation can. Nobara's face measures 0.19-0.21 and her hair 0.43-0.68,
    # highlights included.
    # Gojo's pale, pinkish skin sits at 0.23-0.31 on the green test, so the cut
    # is 0.18: still twice the pink hair's 0.08-0.11.
    return 22 < span < 130 and (g - b) >= 0.18 * span and span <= 0.40 * r


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
        fur = fur_face_box(im, keyed)
        if fur:
            return fur
        raise SystemExit("could not find a face — is this render keyed on green "
                         "and is the head in the top third of the figure?")

    xs, ys = _head_skin(xs, ys)

    # Trim the tails: stray skin pixels (an ear lobe through hair, a hand raised
    # to the chin) would otherwise stretch the box well past the face.
    xs.sort(); ys.sort()
    k = max(1, len(xs) // 50)
    return xs[k], ys[k], xs[-k], ys[-k]


def _head_skin(xs, ys):
    """Only the skin that belongs to the head. Hands raised to the chest (Ijichi
    checking his watch) sit inside the top third of the figure too, and pulled
    the face box down over his whole chest. The face is the highest sizeable
    patch of skin; ears and a neck start beside or just under it and stay,
    and a patch that starts more than half a face below the chin is dropped."""
    pts = set(zip(xs, ys))
    comps, seen = [], set()
    for start in pts:
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in pts and q not in seen:
                    seen.add(q)
                    stack.append(q)
        comps.append(comp)
    big = [c for c in comps if len(c) >= 200] or comps
    face = min(big, key=lambda c: min(p[1] for p in c))
    top = min(p[1] for p in face)
    bottom = max(p[1] for p in face)
    cutoff = bottom + 0.5 * (bottom - top)
    kept = [p for c in comps if min(q[1] for q in c) <= cutoff for p in c]
    return [p[0] for p in kept], [p[1] for p in kept]


def is_white_fur(r, g, b):
    """Light and nearly colourless: Panda's face fur, not skin (warm) and not
    the green backdrop."""
    return min(r, g, b) > 170 and max(r, g, b) - min(r, g, b) < 45


def fur_face_box(im, keyed):
    """For a face made of white fur (Panda): the topmost large patch of white
    in the upper part of the figure, which is the head between the ears.
    None if there is no such patch."""
    fx0, fy0, fx1, fy1 = bbox(keyed)
    limit = min(im.h, fy0 + int((fy1 - fy0) * 0.40))
    W = im.w
    white = {}
    for y in range(fy0, limit):
        for x in range(fx0, fx1):
            if keyed.buf[(y * keyed.w + x) * 4 + 3] < 200:
                continue
            i = (y * W + x) * im.ch
            if is_white_fur(im.buf[i], im.buf[i + 1], im.buf[i + 2]):
                white[(x, y)] = 1
    best = None
    seen = set()
    for start in white:
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            p = stack.pop()
            comp.append(p)
            x, y = p
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in white and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if len(comp) < 2000:
            continue
        top = min(p[1] for p in comp)
        if best is None or top < best[0]:
            best = (top, comp)
    if best is None:
        return None
    xs = sorted(p[0] for p in best[1]); ys = sorted(p[1] for p in best[1])
    k = max(1, len(xs) // 100)
    return xs[k], ys[k], xs[-k], ys[-k]


def build_fur(src_path, name, out_dir=None):
    """Face mask for a fur face (Panda): a feathered oval inside the white of
    the head, over the eye patches, the brow lines, the nose and the mouth,
    clear of the ears and the head's outline, which stay exactly as drawn.

    Writes masks/<name>_face.png, the file the expression composites use.
    """
    src_path = os.path.expanduser(src_path)
    im = load(src_path)
    keyed = key_out(im)
    hx0, hy0, hx1, hy1 = fur_face_box(im, keyed) or face_box(im, keyed)
    # The white patch runs on down the throat, so its height says nothing
    # about the face; its width is the head's. Brow lines to below the mouth.
    w = hx1 - hx0
    cx, cy = (hx0 + hx1) / 2.0, hy0 + 0.48 * w
    rx, ry = 0.40 * w, 0.37 * w
    mask = Img(im.w, im.h, alpha=False)
    mask.rect(0, 0, im.w, im.h, (0, 0, 0))
    steps = max(1, FEATHER)
    for s in range(steps + 1):
        v = int(255 * s / float(steps))
        d = steps - s
        mask.poly(superellipse(cx, cy, rx - d, ry - d, n=2.6), (v, v, v))
    out_dir = out_dir or os.path.join(os.path.dirname(src_path), "masks")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, name + "_face.png")
    mask.save(out)
    print("fur face  head white x %d..%d  y %d..%d; oval centre (%.0f, %.0f), radii %.0f x %.0f"
          % (hx0, hx1, hy0, hy1, cx, cy, rx, ry))
    print("mask   -> %s" % out)
    return out


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

    # Raise the top edge by a feather's width. Skin starts where hair stops,
    # so on a character with a fringe the eyebrows sit exactly at the top of
    # the skin -- and the feather band put Megumi's at 20-70% strength, so no
    # expression could move them. This lands the soft band on the fringe and
    # the brows at full strength; a few fringe strands get redrawn per
    # expression, which costs far less than eyebrows that can't move.
    top = min(spans)
    for y in range(max(0, top - FEATHER - 2), top):
        spans[y] = spans[top]

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
    # Outermost (faintest) first, each smaller one brighter on top, so the
    # edge fades in over FEATHER px. Drawn the other way round, the last and
    # largest shape was solid white and covered the fade.
    steps = max(1, FEATHER)
    for s in range(steps + 1):
        v = int(255 * s / float(steps))
        mask.poly(superellipse(cx, cut, rx - s, ry - s, n=3.2), (v, v, v))
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


def build_below_hairline(src_path, name, out_dir=None, chin_extra=16, feather=6):
    """Face mask for a character whose eyes are hidden behind glasses or a
    blindfold, where the frame cuts the skin in two and face_spans' flood fill
    can't reach the forehead. Takes the whole-head mask (build_head) from the
    top of the forehead down, carried chin_extra rows below the chin for a
    beard, so the brows above the frames and everything down to the beard's
    point can move, while the hair above the hairline stays as drawn.

    Writes masks/<name>_face.png, the file the expression composites use.
    """
    src_path = os.path.expanduser(src_path)
    im = load(src_path)
    keyed = key_out(im)
    out_dir = out_dir or os.path.join(os.path.dirname(src_path), "masks")
    head = load(build_head(src_path, name, out_dir=out_dir))
    x0, y0, x1, cut, (fx0, fy0, fx1, fy1) = head_box(im, keyed)
    cx = (fx0 + fx1) // 2
    hairline = None
    for y in range(y0, fy1):
        row = sum(1 for x in range(cx - 30, cx + 31)
                  if is_skin(*im.buf[(y * im.w + x) * im.ch:(y * im.w + x) * im.ch + 3]))
        if row >= 30:
            hairline = y
            break
    mask = Img(im.w, im.h, alpha=False)
    mask.buf = bytearray(head.buf[:im.w * im.h * 3]) if head.ch == 3 else bytearray(
        b for p in range(im.w * im.h) for b in (head.buf[p * head.ch],) * 3)
    for y in range(0, im.h):
        k = 1.0 if y >= hairline + feather else max(0.0, (y - hairline + 2) / float(feather + 2))
        if k >= 1.0:
            continue
        row = y * im.w * 3
        for i in range(row, row + im.w * 3):
            mask.buf[i] = int(mask.buf[i] * k)
    # carry the lowest row down for a beard's point
    last = max(y for y in range(im.h) if any(mask.buf[(y * im.w + x) * 3] > 128 for x in range(im.w)))
    xs = [x for x in range(im.w) if mask.buf[(last * im.w + x) * 3] > 128]
    for k in range(1, chin_extra + 1):
        y = last + k
        if y >= im.h:
            break
        v = int(255 * (1.0 - k / float(chin_extra + 1)))
        for x in range(min(xs), max(xs) + 1):
            i = (y * im.w + x) * 3
            if mask.buf[i] < v:
                mask.buf[i:i + 3] = bytes((v, v, v))
    out = os.path.join(out_dir, name + "_face.png")
    mask.save(out)
    print("face      from the hairline at y %d down past the chin at y %d (+%d rows)" % (hairline, last, chin_extra))
    print("mask   -> %s" % out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); raise SystemExit(1)
    if "--head" in sys.argv:
        build_head(args[0], args[1])
    elif "--below-hairline" in sys.argv:
        build_below_hairline(args[0], args[1])
    elif "--fur" in sys.argv:
        build_fur(args[0], args[1])
    else:
        build(args[0], args[1])
