"""
Move a scar from one version of a face close-up onto another, pixel by pixel.

    python3 tools/transplant_scar.py utahime           # move the scar into the working base
    python3 tools/transplant_scar.py utahime --mask    # then: add the whole scar to the face mask

Made for Utahime (2026-09-28). The user chose the scar from head-fix box 1 (a
wide diagonal band, as in the anime) and the softer face of box 3. The two
drawings differ across the whole face, and Nano Banana, given both, returned
the second picture whole, so the scar is moved directly instead. Both
close-ups show the same square of the same base and are lined up (each head
fix composited at scale 1.0, shift 0), so no warping is needed:

1. heal box 3's scar band and scratch marks with its own nearby skin, shading
   included;
2. paint in box 1's scar band and scratch marks only (never its plain skin),
   feathered, with neither version's lashes, hair or outlines crossing over.

What is what is told apart by colour: skin is light and peach (lightness about
0.86, hue 15-24 degrees), the scar darker and pinker (0.55-0.75, hue 0-12), and
the line art purple-black. The lips match the scar's colour, so the search is
limited to the band under the eyes.
"""
import sys, os, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img
from composite_face import rgb
import fix_edges as F

W = H = 1024
BAND = (370, 300, 670, 425)          # x0, y0, x1, y1: under the eyes, above the lips
SCRATCH = (555, 335, 665, 425)       # the right cheek, where both versions draw scratch marks

def hls(buf, p):
    r, g, b = buf[p * 3:p * 3 + 3]
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return (h if h < 0.5 else h - 1) * 360, l, s

def inside(p, box):
    x, y = p % W, p // W
    return box[0] <= x < box[2] and box[1] <= y < box[3]

def skin(buf, p):
    h, l, s = hls(buf, p)
    return l > 0.83 and 10 <= h <= 30

def skin_or_shade(buf, p):          # skin including the cheek's shading, for healing
    h, l, s = hls(buf, p)
    return l > 0.62 and 12 <= h <= 30

def line_art(buf, p):                # lashes, hair, outlines: purple-black here
    h, l, s = hls(buf, p)
    return l < 0.5 and h < -30

def scar_fill(buf, p):
    h, l, s = hls(buf, p)
    return 0.45 <= l <= 0.84 and -8 <= h <= 11

def scratch(buf, p):
    h, l, s = hls(buf, p)
    return 0.15 <= l < 0.80 and 0 <= h <= 28

def components(mask, minimum):
    seen = bytearray(W * H); keep = bytearray(W * H)
    for s0 in range(W * H):
        if not mask[s0] or seen[s0]:
            continue
        st, comp = [s0], []
        seen[s0] = 1
        while st:
            p = st.pop(); comp.append(p)
            for q in (p - 1, p + 1, p - W, p + W):
                if 0 <= q < W * H and mask[q] and not seen[q]:
                    seen[q] = 1; st.append(q)
        if len(comp) >= minimum:
            for p in comp:
                keep[p] = 1
    return keep

def scar_mask(im):
    """The scar band (big pink pieces) and the scratch marks, grown a little to
    take in their rims, never touching the line art."""
    fill = bytearray(W * H); scr = bytearray(W * H); line = bytearray(W * H)
    for p in range(W * H):
        if not inside(p, BAND):
            continue
        if line_art(im.buf, p):
            line[p] = 1
        elif scar_fill(im.buf, p):
            fill[p] = 1
        elif inside(p, SCRATCH) and scratch(im.buf, p) and not skin(im.buf, p):
            scr[p] = 1
    near_line = F.dilate(line, W, H, 2)
    near_edge = F.dilate(line, W, H, 12)      # scratches stop short of hair and outlines
    scr = bytearray(1 if (scr[p] and not near_edge[p]) else 0 for p in range(W * H))
    band = components(fill, 60)
    marks = components(scr, 6)
    m = bytearray(a | b for a, b in zip(band, marks))
    m = F.dilate(m, W, H, 2)
    return bytearray(1 if (m[p] and not near_line[p]) else 0 for p in range(W * H)), band

def transplant(now, ref):
    out = Img(W, H); out.buf = bytearray(now.buf)
    old, _ = scar_mask(now)
    new, new_band = scar_mask(ref)
    # 1. heal box 3's scar with its own nearby skin
    healed = 0
    for p in range(W * H):
        if not old[p]:
            continue
        x, y = p % W, p // W
        acc = [0, 0, 0]; n = 0
        for yy in range(y - 16, y + 17, 2):
            for xx in range(x - 16, x + 17, 2):
                q = yy * W + xx
                if 0 <= q < W * H and not old[q] and skin_or_shade(now.buf, q):
                    for k in range(3):
                        acc[k] += now.buf[q * 3 + k]
                    n += 1
        if n >= 6:
            out.buf[p * 3:p * 3 + 3] = bytes(int(v / n + 0.5) for v in acc)
            healed += 1
    # 2. paint box 1's scar in, feathered, keeping box 3's line art on top
    a = F.box_blur([float(v) for v in new], W, H, 1)
    line3 = F.dilate(bytearray(1 if (inside(p, BAND) and line_art(now.buf, p)) else 0 for p in range(W * H)), W, H, 1)
    line1 = F.dilate(bytearray(1 if (inside(p, BAND) and line_art(ref.buf, p)) else 0 for p in range(W * H)), W, H, 2)
    painted = 0
    for p in range(W * H):
        t = a[p]
        if t <= 0.0 or line3[p] or line1[p]:   # neither version's hair or outlines crosses over
            continue
        if skin(ref.buf, p):                    # box 1's plain skin stays behind: only scar comes across
            continue
        for k in range(3):
            out.buf[p * 3 + k] = int(out.buf[p * 3 + k] * (1 - t) + ref.buf[p * 3 + k] * t + 0.5)
        painted += 1
    return out, healed, painted, old, new

def apply_to_base(char, out, now, square):
    """Write the changed pixels of the 1024 close-up back into the working
    base's square, as a difference, so untouched pixels stay exactly as they
    were."""
    from raster import resample
    X, Y, side = square
    base_path = os.path.join(F.FIXED, "%s_base.png" % char)
    base = rgb(load(base_path))
    o = resample(out, side, side)
    n = resample(now, side, side)
    k = W // side
    written = 0
    for y in range(side):
        for x in range(side):
            changed = any(out.buf[((y * k + dy) * W + x * k + dx) * 3 + c] != now.buf[((y * k + dy) * W + x * k + dx) * 3 + c]
                          for dy in range(k) for dx in range(k) for c in range(3))
            if not changed:
                continue
            i = ((Y + y) * base.w + X + x) * 3
            j = (y * side + x) * 3
            for c in range(3):
                base.buf[i + c] = max(0, min(255, base.buf[i + c] + o.buf[j + c] - n.buf[j + c]))
            written += 1
    base.save(base_path)
    return written

def add_scar_to_face_mask(char, box=(300, 170, 470, 260), grow=3):
    """The face mask follows skin, and the scar isn't skin-coloured, so the
    mask's edge would cut across the scar. Add the whole scar (in the base's
    own coordinates; box is x0, y0, x1, y1) so every expression redraws all of
    it or none of it."""
    base = rgb(load(os.path.join(F.FIXED, "%s_base.png" % char)))
    mpath = os.path.join(F.FIXED, "masks", "%s_face.png" % char)
    m = load(mpath)
    Wb, Hb = base.w, base.h
    scar = bytearray(Wb * Hb)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            p = y * Wb + x
            h, l, s_ = hls(base.buf, p)
            if 0.45 <= l <= 0.84 and -8 <= h <= 11:
                scar[p] = 1
    # the band itself: its biggest pieces, grown to take in rim and scratches
    seen = bytearray(Wb * Hb); keep = bytearray(Wb * Hb)
    for s0 in range(Wb * Hb):
        if not scar[s0] or seen[s0]:
            continue
        st, comp = [s0], []
        seen[s0] = 1
        while st:
            p = st.pop(); comp.append(p)
            for q in (p - 1, p + 1, p - Wb, p + Wb):
                if 0 <= q < Wb * Hb and scar[q] and not seen[q]:
                    seen[q] = 1; st.append(q)
        if len(comp) >= 30:
            for p in comp:
                keep[p] = 1
    keep = F.dilate(keep, Wb, Hb, grow)
    added = 0
    for p in range(Wb * Hb):
        if keep[p] and m.buf[p * m.ch] < 255:
            m.buf[p * m.ch:p * m.ch + 3] = b"\xff\xff\xff"
            added += 1
    m.save(mpath)
    return added


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--mask":
        print("added %d scar pixels to the face mask" % add_scar_to_face_mask(sys.argv[1]))
        raise SystemExit(0)
    char = sys.argv[1] if len(sys.argv) > 1 else "utahime"
    I = os.path.expanduser("~/ComfyUI-Shared/input")
    now = rgb(load(os.path.join(I, "ref_%s_face.png" % char)))
    ref = rgb(load(os.path.join(I, "ref_%s_ref.png" % char)))
    out, healed, painted, old, new = transplant(now, ref)
    print("healed %d pixels of the old scar; painted %d pixels of the new one" % (healed, painted))
    square = tuple(int(v) for v in open(os.path.join(F.FIXED, "masks", "%s_ref_crop.txt" % char)).read().split())
    out.save(os.path.join(F.FIXED, "%s_scar_close.png" % char))
    print("wrote %d pixels into the working base (square %s)" % (apply_to_base(char, out, now, square), square))
