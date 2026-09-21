"""
Put an edit model's new face onto the original sprite, and nothing else.

    python3 tools/composite_face.py <base.png> <edited.png> <character> <expression>

Instruction-based edit models ("make him look angry") change expressions far
better than inpainting did, but they redraw the whole picture: the output can
come back a different size, nudged a few pixels, zoomed a percent or two, with
the uniform or the green subtly altered. None of that may reach the game --
switching expression must not make the body shimmer.

So this takes only the face. The edited picture is resized to the base's
dimensions, then lined up with it by searching scale and position for the best
match on the hair, ears and collar immediately around the face -- the parts an
expression edit should not move. The face mask from tools/facemask.py decides
what comes across; outside it every pixel is the base's own. A slight colour
cast on the new face is matched to the base along the mask's soft edge so no
seam shows.

Writes composited/<character>_<expression>.png beside the base for the record,
and installs the game sprite and side portrait through keysprite.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img
from pngread import load

SCALES = [0.96 + 0.005 * i for i in range(17)]     # 0.96 .. 1.04
SHIFT = 14                                          # px either way


def rgb(im):
    if im.ch == 3:
        return im
    out = Img(im.w, im.h, alpha=False)
    for p in range(im.w * im.h):
        out.buf[p * 3:p * 3 + 3] = im.buf[p * im.ch:p * im.ch + 3]
    return out


def resize(im, w, h):
    """Bilinear resize to exactly w x h (aspect may change slightly)."""
    if (im.w, im.h) == (w, h):
        return im
    out = Img(w, h, alpha=False)
    sx, sy = im.w / float(w), im.h / float(h)
    for y in range(h):
        fy = (y + 0.5) * sy - 0.5
        y0 = max(0, min(im.h - 1, int(fy))); y1 = min(im.h - 1, y0 + 1); ty = fy - y0
        for x in range(w):
            fx = (x + 0.5) * sx - 0.5
            x0 = max(0, min(im.w - 1, int(fx))); x1 = min(im.w - 1, x0 + 1); tx = fx - x0
            a, b = (y0 * im.w + x0) * 3, (y0 * im.w + x1) * 3
            c, d = (y1 * im.w + x0) * 3, (y1 * im.w + x1) * 3
            j = (y * w + x) * 3
            for k in range(3):
                top = im.buf[a + k] + (im.buf[b + k] - im.buf[a + k]) * tx
                bot = im.buf[c + k] + (im.buf[d + k] - im.buf[c + k]) * tx
                out.buf[j + k] = int(top + (bot - top) * ty + 0.5)
    return out


def ring(mask, base, width=40, step=2):
    """Sample points just outside the face mask: hair, ears, collar.

    Flat backdrop is skipped -- it matches at any offset and would only dilute
    the score.
    """
    m = mask
    ys = [p // m.w for p in range(m.w * m.h) if m.buf[p * m.ch] > 0]
    xs = [p % m.w for p in range(m.w * m.h) if m.buf[p * m.ch] > 0]
    x0, x1, y0, y1 = min(xs) - width, max(xs) + width, min(ys) - width, max(ys) + width
    pts = []
    for y in range(max(0, y0), min(m.h, y1), step):
        for x in range(max(0, x0), min(m.w, x1), step):
            if m.buf[(y * m.w + x) * m.ch]:
                continue
            i = (y * base.w + x) * 3
            r, g, b = base.buf[i], base.buf[i + 1], base.buf[i + 2]
            if g - max(r, b) > 20:              # backdrop green
                continue
            pts.append((x, y))
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    return pts, (cx, cy)


def score(base, ed, pts, c, s, dx, dy):
    cx, cy = c
    tot = 0
    W, H = ed.w, ed.h
    for x, y in pts:
        ex = int(cx + (x - cx) * s + dx + 0.5)
        ey = int(cy + (y - cy) * s + dy + 0.5)
        if not (0 <= ex < W and 0 <= ey < H):
            tot += 255
            continue
        i, j = (y * base.w + x) * 3, (ey * W + ex) * 3
        tot += abs(base.buf[i] - ed.buf[j]) + abs(base.buf[i + 1] - ed.buf[j + 1]) + abs(base.buf[i + 2] - ed.buf[j + 2])
    return tot / (3.0 * len(pts))


def align(base, ed, mask):
    pts, c = ring(mask, base)
    if len(pts) < 200:
        raise SystemExit("not enough hair/collar around the face to line the pictures up")
    coarse = pts[::3]
    best = (score(base, ed, coarse, c, 1.0, 0, 0), 1.0, 0, 0)
    for s in SCALES:
        for dy in range(-SHIFT, SHIFT + 1, 2):
            for dx in range(-SHIFT, SHIFT + 1, 2):
                e = score(base, ed, coarse, c, s, dx, dy)
                if e < best[0]:
                    best = (e, s, dx, dy)
    _, s0, dx0, dy0 = best
    best = (score(base, ed, pts, c, s0, dx0, dy0), s0, dx0, dy0)
    for s in (s0 - 0.0025, s0, s0 + 0.0025):
        for dy in range(dy0 - 2, dy0 + 3):
            for dx in range(dx0 - 2, dx0 + 3):
                e = score(base, ed, pts, c, s, dx, dy)
                if e < best[0]:
                    best = (e, s, dx, dy)
    before = score(base, ed, pts, c, 1.0, 0, 0)
    return best, before, c


def sample(ed, fx, fy):
    x0, y0 = int(fx), int(fy)
    if x0 < 0 or y0 < 0 or x0 + 1 >= ed.w or y0 + 1 >= ed.h:
        x0, y0 = max(0, min(ed.w - 1, x0)), max(0, min(ed.h - 1, y0))
        return ed.buf[(y0 * ed.w + x0) * 3:(y0 * ed.w + x0) * 3 + 3]
    tx, ty = fx - x0, fy - y0
    a, b = (y0 * ed.w + x0) * 3, (y0 * ed.w + x0 + 1) * 3
    c, d = ((y0 + 1) * ed.w + x0) * 3, ((y0 + 1) * ed.w + x0 + 1) * 3
    out = []
    for k in range(3):
        top = ed.buf[a + k] + (ed.buf[b + k] - ed.buf[a + k]) * tx
        bot = ed.buf[c + k] + (ed.buf[d + k] - ed.buf[c + k]) * tx
        out.append(top + (bot - top) * ty)
    return out


def composite(base, raw, mask, params, c):
    """Sample the face straight from the edit model's own pixels.

    Alignment is searched on a copy resized to the base's size, but the face is
    taken from the original output in one resampling step -- resize and shift
    folded together -- so crisp line art is interpolated once, not twice.
    """
    _, s, dx, dy = params
    cx, cy = c
    kx, ky = raw.w / float(base.w), raw.h / float(base.h)
    face = [p for p in range(base.w * base.h) if mask.buf[p * mask.ch] > 0]
    warped = {}
    for p in face:
        x, y = p % base.w, p // base.w
        ex, ey = cx + (x - cx) * s + dx, cy + (y - cy) * s + dy
        warped[p] = sample(raw, (ex + 0.5) * kx - 0.5, (ey + 0.5) * ky - 0.5)

    # Colour: edit models often warm or cool a face slightly. Match the new
    # face to the base along the mask's soft edge, where they must meet.
    # Median, not mean: the soft edge also crosses fringe strands and
    # eyebrows, and an eyebrow the expression moved is an outlier, not a
    # colour cast. (Filtering to "skin on both sides" was tried and was worse:
    # the cast itself changes which pixels pass the skin test.)
    edge = [p for p in face if mask.buf[p * mask.ch] < 255]
    shift = [0.0, 0.0, 0.0]
    if len(edge) > 50:
        for k in range(3):
            d = sorted(base.buf[p * 3 + k] - warped[p][k] for p in edge)
            shift[k] = max(-20.0, min(20.0, d[len(d) // 2]))
    out = Img(base.w, base.h, alpha=False)
    out.buf = bytearray(base.buf)
    for p in face:
        a = mask.buf[p * mask.ch] / 255.0
        for k in range(3):
            v = warped[p][k] + shift[k]
            out.buf[p * 3 + k] = max(0, min(255, int(base.buf[p * 3 + k] * (1 - a) + v * a + 0.5)))
    return out, shift


def run(base_path, edited_path, char, expr, mask_path=None, install=True):
    base_path, edited_path = os.path.expanduser(base_path), os.path.expanduser(edited_path)
    folder = os.path.dirname(base_path)
    mask_path = mask_path or os.path.join(folder, "masks", char + "_face.png")
    base, mask = rgb(load(base_path)), load(mask_path)
    raw = rgb(load(edited_path))
    if (mask.w, mask.h) != (base.w, base.h):
        raise SystemExit("mask is %dx%d but the base is %dx%d" % (mask.w, mask.h, base.w, base.h))
    ed = resize(raw, base.w, base.h)
    params, before, c = align(base, ed, mask)
    err, s, dx, dy = params
    out, shift = composite(base, raw, mask, params, c)

    dest = os.path.join(folder, "composited")
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, "%s_%s.png" % (char, expr))
    out.save(path)
    print("edited    %dx%d -> resized to %dx%d" % (raw.w, raw.h, base.w, base.h))
    print("aligned   scale %.4f, shift (%+d, %+d); mismatch around the face %.1f -> %.1f"
          % (s, dx, dy, before, err))
    print("colour    new face shifted by (%+.1f, %+.1f, %+.1f) to meet the base" % tuple(shift))
    if err > 18:
        print("!! the hair and collar around the face still differ a lot after lining up -- "
              "the edit may have moved the head or restyled the hair. Look before trusting it.")
    print("composite -> %s" % path)
    if install:
        from keysprite import install as key_install
        for pr in key_install(path, "%s_%s" % (char, expr), quiet=True):
            if "runs off the bottom" not in pr:
                print("   !! " + pr)
        print("installed -> game/images/char/%s_%s.png (run tools/gen_sprite_defs.py)" % (char, expr))
    return path, params


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 4:
        print(__doc__); raise SystemExit(1)
    run(args[0], args[1], args[2], args[3], install="--no-install" not in sys.argv)
