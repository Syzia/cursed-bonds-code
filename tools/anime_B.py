#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anime_B.py -- Approach B: layered-primitive cel-shaded character renderer.

A character is a "rig" of many anti-aliased polygons (bezier-edged hair
locks, almond eyes, rounded garment panels ...).  Every visible part is drawn
as FILL + dark LINE-ART outline, then flat cel shadows / highlights are
painted through a per-part clip mask so they never leak outside the shape.

    from anime_B import render_character, YUJI
    img = render_character(YUJI, "happy")      # raster.Img 760x1400 RGBA
    img.save("yuji_happy.png")

Pure Python 3 (no Pillow / numpy).  tools/raster.py supplies the Img
container, colour helpers and the PNG writer; the drawing here works
directly on the RGBA bytearray with an AA scanline filler (4 sub-scanlines,
fractional x coverage, slice-fill for fully covered runs).
"""
import sys, os, math, time

_TOOLS = os.path.dirname(os.path.abspath(__file__))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import raster
from raster import Img, hexc, lerp

W, H = 760, 1400
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")


# =========================================================================
# colour helpers
# =========================================================================
def C(c):
    """'#rrggbb' or (r,g,b) -> (r,g,b)."""
    if isinstance(c, str):
        return hexc(c)
    return tuple(int(v) for v in c)


def mul(c, f):
    return tuple(max(0, min(255, int(v * f + 0.5))) for v in c)


def mix(a, b, t):
    return lerp(a, b, t)


def cel_shadow(c, k=0.72):
    """Flat anime shadow tone: darker, slightly cooler / more saturated."""
    return mix(mul(c, k), (70, 40, 90), 0.10)


def cel_light(c, k=0.18):
    return mix(c, (255, 250, 245), k)


def line_of(c, k=0.34):
    """Line-art colour for a fill: a dark, slightly desaturated version."""
    d = mul(c, k)
    return mix(d, (30, 15, 25), 0.35)


# =========================================================================
# tiny AA rasteriser on top of raster.Img (RGBA) / Mask
# =========================================================================
class Mask(object):
    """8-bit coverage mask (0..255 per pixel) used for clipping."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = bytearray(w * h)

    def inverted(self):
        m = Mask(self.w, self.h)
        m.buf = self.buf.translate(bytes(255 - i for i in range(256)))
        return m


def _loops(pts):
    if pts and isinstance(pts[0][0], (tuple, list)):
        return pts
    return [pts]


def fill_poly(dst, pts, color, a=1.0, clip=None, S=4):
    """Anti-aliased even-odd polygon fill.  `pts` is a loop or a list of loops.
    dst may be an Img (RGBA) or a Mask (then color is ignored, coverage is
    max-combined).  `clip` is an optional Mask multiplied into the coverage."""
    loops = _loops(pts)
    allp = [p for lp in loops for p in lp]
    if len(allp) < 3 or a <= 0.0:
        return
    w, h = dst.w, dst.h
    ys = [p[1] for p in allp]
    xs = [p[0] for p in allp]
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(h - 1, int(math.ceil(max(ys))))
    bx0 = max(0, int(math.floor(min(xs))))
    bx1 = min(w - 1, int(math.ceil(max(xs))))
    if y1 < y0 or bx1 < bx0:
        return
    width = bx1 - bx0 + 1
    E = []
    for lp in loops:
        n = len(lp)
        for i in range(n):
            xa, ya = lp[i]
            xb, yb = lp[(i + 1) % n]
            if ya == yb:
                continue
            if ya > yb:
                xa, ya, xb, yb = xb, yb, xa, ya
            E.append((ya, yb, xa, (xb - xa) / float(yb - ya)))
    if not E:
        return
    # sort edges by y-start so we can skip cheaply
    E.sort()
    inv = 1.0 / S
    is_mask = isinstance(dst, Mask)
    buf = dst.buf
    cbuf = clip.buf if clip is not None else None
    if not is_mask:
        r, g, b = color
        pix = bytes((r, g, b, 255))
    fast = (a >= 1.0) and (cbuf is None) and (not is_mask)
    for y in range(y0, y1 + 1):
        diff = [0] * (width + 2)
        part = [0.0] * (width + 1)
        touched = False
        for k in range(S):
            sy = y + (k + 0.5) * inv
            xl = []
            for (ey0, ey1, ex, dx) in E:
                if ey0 > sy:
                    break
                if sy < ey1:
                    xl.append(ex + (sy - ey0) * dx)
            if len(xl) < 2:
                continue
            xl.sort()
            for i in range(0, len(xl) - 1, 2):
                xa = xl[i] - bx0
                xb = xl[i + 1] - bx0
                if xb <= 0.0 or xa >= width:
                    continue
                if xa < 0.0:
                    xa = 0.0
                if xb > width:
                    xb = float(width)
                ia = int(xa)
                ib = int(xb)
                if ia == ib:
                    part[ia] += xb - xa
                else:
                    part[ia] += ia + 1 - xa
                    if ib < width:
                        part[ib] += xb - ib
                    diff[ia + 1] += 1
                    diff[ib] -= 1
                touched = True
        if not touched:
            continue
        cov = [0.0] * width
        run = 0
        for x in range(width):
            run += diff[x]
            cov[x] = (run + part[x]) * inv
        base = y * w + bx0
        x = 0
        while x < width:
            c = cov[x]
            if c <= 0.004:
                x += 1
                continue
            if c >= 0.996:
                j = x + 1
                while j < width and cov[j] >= 0.996:
                    j += 1
                if fast:
                    buf[(base + x) * 4:(base + j) * 4] = pix * (j - x)
                    x = j
                    continue
                if is_mask and cbuf is None and a >= 1.0:
                    buf[base + x:base + j] = b'\xff' * (j - x)
                    x = j
                    continue
                # fall through: per-pixel with alpha / clip
                for xx in range(x, j):
                    aa = a
                    if cbuf is not None:
                        cv = cbuf[base + xx]
                        if cv == 0:
                            continue
                        aa = aa * cv / 255.0
                    _px(buf, base + xx, is_mask, color, aa)
                x = j
                continue
            aa = c * a
            if cbuf is not None:
                cv = cbuf[base + x]
                if cv == 0:
                    x += 1
                    continue
                aa = aa * cv / 255.0
            _px(buf, base + x, is_mask, color, aa)
            x += 1


def _px(buf, p, is_mask, color, aa):
    if aa <= 0.002:
        return
    if aa > 1.0:
        aa = 1.0
    if is_mask:
        v = int(aa * 255 + 0.5)
        if v > buf[p]:
            buf[p] = v
        return
    i = p * 4
    da = buf[i + 3]
    r, g, b = color
    if da == 0:
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b
        buf[i + 3] = int(aa * 255 + 0.5)
    elif da == 255:
        buf[i] = int(buf[i] + (r - buf[i]) * aa + 0.5)
        buf[i + 1] = int(buf[i + 1] + (g - buf[i + 1]) * aa + 0.5)
        buf[i + 2] = int(buf[i + 2] + (b - buf[i + 2]) * aa + 0.5)
    else:
        d = da / 255.0
        na = aa + d * (1.0 - aa)
        k = d * (1.0 - aa)
        buf[i] = int((r * aa + buf[i] * k) / na + 0.5)
        buf[i + 1] = int((g * aa + buf[i + 1] * k) / na + 0.5)
        buf[i + 2] = int((b * aa + buf[i + 2] * k) / na + 0.5)
        buf[i + 3] = int(na * 255 + 0.5)


# ------------------------------------------------------------------ geometry
def ellipse_pts(cx, cy, rx, ry, n=None, rot=0.0, a0=0.0, a1=2 * math.pi):
    if n is None:
        n = max(14, min(96, int((rx + ry) * 0.7)))
    out = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n + 1 if a1 - a0 < 2 * math.pi - 1e-6 else n):
        t = a0 + (a1 - a0) * i / float(n)
        x, y = math.cos(t) * rx, math.sin(t) * ry
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def circle_pts(cx, cy, r, n=None):
    return ellipse_pts(cx, cy, r, r, n)


def qbez(p0, p1, p2, n=10):
    out = []
    for i in range(n + 1):
        t = i / float(n)
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def cbez(p0, p1, p2, p3, n=12):
    out = []
    for i in range(n + 1):
        t = i / float(n)
        u = 1.0 - t
        out.append((u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                    u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]))
    return out


def smooth(pts, closed=True, n=8, tension=0.5):
    """Catmull-Rom spline through pts.  A point given as (x, y, 's') is a
    sharp corner (zero tangent)."""
    P = [(p[0], p[1]) for p in pts]
    SH = [len(p) > 2 and p[2] == 's' for p in pts]
    N = len(P)
    if N < 2:
        return P

    def tan(i):
        if SH[i]:
            return (0.0, 0.0)
        if closed:
            a, b = P[(i - 1) % N], P[(i + 1) % N]
        else:
            a, b = P[max(0, i - 1)], P[min(N - 1, i + 1)]
            if i == 0 or i == N - 1:
                return ((b[0] - a[0]) * tension * 2, (b[1] - a[1]) * tension * 2)
        return ((b[0] - a[0]) * tension, (b[1] - a[1]) * tension)

    out = []
    segs = N if closed else N - 1
    for i in range(segs):
        p0, p1 = P[i], P[(i + 1) % N]
        m0, m1 = tan(i), tan((i + 1) % N)
        for k in range(n):
            t = k / float(n)
            t2 = t * t
            t3 = t2 * t
            h00 = 2 * t3 - 3 * t2 + 1
            h10 = t3 - 2 * t2 + t
            h01 = -2 * t3 + 3 * t2
            h11 = t3 - t2
            out.append((h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0],
                        h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1]))
    if not closed:
        out.append(P[-1])
    return out


def lock_pts(a, b, tip, bulge=0.16, curl=0.0, n=9):
    """Tapered hair lock: base edge a->b, pointed tip, quadratic-bezier sides."""
    mx, my = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    dx, dy = tip[0] - mx, tip[1] - my
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    sa = (a[0] - mx) * px + (a[1] - my) * py
    sgn_a = 1.0 if sa >= 0 else -1.0

    def ctrl(base, sgn):
        return ((base[0] + tip[0]) * 0.5 + px * (sgn * bulge * L + curl * L),
                (base[1] + tip[1]) * 0.5 + py * (sgn * bulge * L + curl * L))

    s1 = qbez(a, ctrl(a, sgn_a), tip, n)
    s2 = qbez(tip, ctrl(b, -sgn_a), b, n)
    return s1 + s2[1:]


def widths_along(n, ws):
    """Interpolate a short list of widths across n points."""
    if not isinstance(ws, (list, tuple)):
        return [float(ws)] * n
    if len(ws) == 1:
        return [float(ws[0])] * n
    out = []
    for i in range(n):
        t = i / float(max(1, n - 1)) * (len(ws) - 1)
        k = min(len(ws) - 2, int(t))
        f = t - k
        out.append(ws[k] + (ws[k + 1] - ws[k]) * f)
    return out


def stroke_outline(pts, width, closed=False, miter_limit=2.5):
    """Offset a polyline into a fillable polygon (loops) for stroking."""
    n = len(pts)
    if n < 2:
        return None
    ws = widths_along(n, width)
    L, R = [], []
    for i in range(n):
        p = pts[i]
        if closed:
            pa, pb = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            pa = pts[i - 1] if i > 0 else None
            pb = pts[i + 1] if i < n - 1 else None

        def dirv(u, v):
            dx, dy = v[0] - u[0], v[1] - u[1]
            l = math.hypot(dx, dy)
            if l < 1e-9:
                return (1.0, 0.0)
            return (dx / l, dy / l)

        din = dirv(pa, p) if pa is not None else dirv(p, pb)
        dout = dirv(p, pb) if pb is not None else dirv(pa, p)
        nin = (-din[1], din[0])
        nout = (-dout[1], dout[0])
        mx, my = nin[0] + nout[0], nin[1] + nout[1]
        ml = math.hypot(mx, my)
        if ml < 1e-6:
            ox, oy, sc = nin[0], nin[1], 1.0
        else:
            mx, my = mx / ml, my / ml
            ch = mx * nin[0] + my * nin[1]
            sc = 1.0 / max(ch, 1.0 / miter_limit)
            ox, oy = mx, my
        hw = ws[i] * 0.5 * sc
        L.append((p[0] + ox * hw, p[1] + oy * hw))
        R.append((p[0] - ox * hw, p[1] - oy * hw))
    if closed:
        return [L, R[::-1]]
    return [L + R[::-1]]


# ------------------------------------------------------------------ painters
def stroke(img, pts, width, color, a=1.0, closed=False, clip=None, cap=True):
    loops = stroke_outline(pts, width, closed)
    if loops is None:
        return
    fill_poly(img, loops, color, a, clip)
    if cap and not closed:
        ws = widths_along(len(pts), width)
        for p, wdt in ((pts[0], ws[0]), (pts[-1], ws[-1])):
            if wdt > 2.2:
                fill_poly(img, circle_pts(p[0], p[1], wdt * 0.5, 10), color, a, clip)


def shape(img, pts, fill, line=None, lw=3.0, a=1.0, clip=None, mask=None, line_a=1.0):
    """Fill a closed polygon, then stroke its outline on top.  Optionally
    also accumulate the shape into `mask` (for later clipped shading)."""
    if fill is not None:
        fill_poly(img, pts, fill, a, clip)
    if mask is not None:
        fill_poly(mask, pts, None, 1.0)
    if line is not None and lw > 0:
        stroke(img, pts, lw, line, line_a, closed=True, clip=clip)


def shape_mask(w, h, pts, clip=None):
    m = Mask(w, h)
    fill_poly(m, pts, None, 1.0, clip)
    return m


def mirror(pts, cx):
    return [(2 * cx - p[0], p[1]) + tuple(p[2:]) for p in pts]


# =========================================================================
# expressions
# =========================================================================
EXPR = {
    "neutral":   dict(eye_open=1.00, lower_lid=0.00, brow_in=0,   brow_out=0,  brow_raise=0,  mouth="neutral"),
    "happy":     dict(eye_open=0.92, lower_lid=0.42, brow_in=-2,  brow_out=-3, brow_raise=5,  mouth="grin"),
    "serious":   dict(eye_open=0.74, lower_lid=0.06, brow_in=7,   brow_out=-4, brow_raise=-5, mouth="flat"),
    "angry":     dict(eye_open=0.68, lower_lid=0.12, brow_in=16,  brow_out=-8, brow_raise=-7, mouth="grit"),
    "surprised": dict(eye_open=1.22, lower_lid=-0.10, brow_in=-2, brow_out=-2, brow_raise=17, mouth="o"),
    "sad":       dict(eye_open=0.84, lower_lid=0.10, brow_in=-9,  brow_out=7,  brow_raise=3,  mouth="sad"),
}


# =========================================================================
# face parts
# =========================================================================
def draw_eye(img, ex, ey, side, w, h, col, exp, line_c):
    """Parametric anime eye.  side = -1 viewer's left, +1 viewer's right
    (used so the outer corner / lashes point outward)."""
    op = exp.get("eye_open", 1.0)
    lr = exp.get("lower_lid", 0.0)
    iris = col["iris"]
    iris_dark = col["iris_dark"]
    iris_light = col["iris_light"]
    white = col.get("white", (247, 244, 243))
    inner = (ex - side * w * 0.50, ey + h * 0.14)
    outer = (ex + side * w * 0.52, ey + h * 0.02)
    top = ey - h * 0.58 * op
    up = cbez(inner, (ex - side * w * 0.34, top - h * 0.10 * op),
              (ex + side * w * 0.22, top - h * 0.12 * op), outer, 16)
    bot = ey + h * 0.46 - h * 0.40 * lr
    low = cbez(outer, (ex + side * w * 0.32, bot + h * 0.08 - h * 0.05 * lr),
               (ex - side * w * 0.22, bot + h * 0.02), inner, 14)
    almond = up + low[1:-1]
    m = shape_mask(img.w, img.h, almond)
    fill_poly(img, almond, white)
    # shadow of the upper lid on the eyeball
    sh = up + [(p[0], p[1] + h * 0.22) for p in up[::-1]]
    fill_poly(img, sh, (208, 198, 202), 0.9, m)
    # iris: tall ellipse clipped by the lids, vertical gradient in bands
    icx, icy = ex + side * w * 0.03, ey + h * 0.06
    irx, iry = w * 0.30, h * 0.54
    ipts = ellipse_pts(icx, icy, irx, iry, 40)
    im = shape_mask(img.w, img.h, ipts, m)
    bands = 7
    y_a, y_b = icy - iry, icy + iry
    for i in range(bands):
        t = i / float(bands - 1)
        c = mix(iris_dark, iris, min(1.0, t * 1.6)) if t < 0.55 else mix(iris, iris_light, (t - 0.55) / 0.45)
        ya = y_a + (y_b - y_a) * i / bands - 1
        yb = y_a + (y_b - y_a) * (i + 1) / bands + 1
        fill_poly(img, [(icx - irx - 2, ya), (icx + irx + 2, ya), (icx + irx + 2, yb), (icx - irx - 2, yb)], c, 1.0, im)
    # iris rim + pupil
    stroke(img, ipts, 2.2, iris_dark, 0.9, closed=True, clip=m)
    fill_poly(img, ellipse_pts(icx, icy + h * 0.02, irx * 0.42, iry * 0.40, 24), col.get("pupil", (28, 16, 12)), 1.0, m)
    # highlights
    fill_poly(img, ellipse_pts(icx - side * irx * 0.42, icy - iry * 0.42, irx * 0.30, iry * 0.20, 16), (255, 255, 255), 1.0, m)
    fill_poly(img, ellipse_pts(icx + side * irx * 0.35, icy + iry * 0.38, irx * 0.14, iry * 0.10, 12), (255, 255, 255), 0.9, m)
    # upper lid line (thick, heavier toward the outer corner)
    stroke(img, up, [2.4, 4.2, 5.6, 5.8, 4.6], line_c, 1.0)
    # lash flick at the outer corner
    ox, oy = outer
    stroke(img, [(ox - side * 3, oy + 1), (ox + side * 7, oy - 7)], [5.0, 0.8], line_c, 1.0)
    # lower lid: thin line on the outer 65 %
    k = int(len(low) * 0.65)
    stroke(img, low[:k], [2.6, 1.8, 0.8], line_c, 0.85)
    # inner-corner tear duct hint
    fill_poly(img, circle_pts(inner[0] + side * 2, inner[1] - 1, 1.8, 8), line_c, 0.5)
    # crease fold above the lid (subtle)
    if op > 0.6:
        fold = [(p[0], p[1] - h * 0.22 * op) for p in up[3:-3]]
        stroke(img, fold, [0.5, 1.6, 1.4, 0.4], line_c, 0.35)
    return (inner, outer, up, low)


def draw_undereye_marks(img, ex, ey, side, w, h, line_c, exp):
    """Yuji's signature little lines under each eye."""
    lr = exp.get("lower_lid", 0.0)
    yb = ey + h * 0.50 - h * 0.30 * lr
    pts = smooth([(ex - side * w * 0.30, yb + 7), (ex - side * w * 0.04, yb + 12), (ex + side * w * 0.25, yb + 9)],
                 closed=False, n=6)
    stroke(img, pts, [1.4, 2.6, 2.2, 1.0], line_c, 0.9)


def draw_brow(img, ex, ey, side, w, h, color, exp, thick=1.0):
    bi = exp.get("brow_in", 0)
    bo = exp.get("brow_out", 0)
    br = exp.get("brow_raise", 0)
    y0 = ey - h * 1.25 - br
    pts = [(ex - side * w * 0.46, y0 + 6 + bi),
           (ex - side * w * 0.05, y0 - 4 + bi * 0.35),
           (ex + side * w * 0.42, y0 - 3 + bo),
           (ex + side * w * 0.60, y0 + 2 + bo * 1.3)]
    pts = smooth(pts, closed=False, n=6)
    stroke(img, pts, [7.5 * thick, 9.5 * thick, 8.0 * thick, 3.0 * thick], color, 1.0)


def draw_nose(img, nx, ny, line_c, shadow_c, face_mask):
    fill_poly(img, ellipse_pts(nx - 9, ny - 5, 5, 10, 16, rot=0.15), shadow_c, 0.45, face_mask)
    pts = smooth([(nx - 3, ny - 18), (nx - 7, ny - 4), (nx - 3, ny + 3)], closed=False, n=6)
    stroke(img, pts, [0.6, 2.4, 2.6], line_c, 0.9)
    stroke(img, [(nx - 3, ny + 3), (nx + 4, ny + 4)], [2.4, 0.6], line_c, 0.75)


def draw_mouth(img, mx, my, kind, line_c, skin_shadow, face_mask):
    if kind == "neutral":
        pts = smooth([(mx - 13, my - 1), (mx - 4, my + 2), (mx + 6, my + 2), (mx + 14, my - 2)], closed=False, n=6)
        stroke(img, pts, [1.2, 3.0, 3.0, 1.2], line_c, 0.95)
        stroke(img, [(mx - 8, my + 9), (mx + 8, my + 9)], [0.6, 2.0, 0.6], line_c, 0.25)
    elif kind == "flat":
        stroke(img, [(mx - 14, my + 1), (mx, my + 1), (mx + 14, my)], [1.2, 3.0, 1.2], line_c, 0.95)
    elif kind == "sad":
        pts = smooth([(mx - 12, my + 4), (mx - 4, my - 1), (mx + 5, my - 1), (mx + 12, my + 4)], closed=False, n=6)
        stroke(img, pts, [1.2, 3.0, 3.0, 1.2], line_c, 0.95)
    elif kind == "o":
        pts = ellipse_pts(mx, my + 3, 8, 11, 24)
        shape(img, pts, (78, 30, 36), line_c, 2.4)
        fill_poly(img, ellipse_pts(mx, my + 9, 5, 4, 14), (170, 70, 80), 0.9)
    elif kind == "grin":
        upper = smooth([(mx - 26, my - 6), (mx - 10, my - 2), (mx + 8, my - 2), (mx + 26, my - 7)], closed=False, n=6)
        lower = smooth([(mx + 26, my - 7), (mx + 16, my + 12), (mx, my + 18), (mx - 16, my + 12), (mx - 26, my - 6)], closed=False, n=6)
        poly = upper + lower[1:-1]
        mm = shape_mask(img.w, img.h, poly)
        fill_poly(img, poly, (86, 32, 40))
        # tongue
        fill_poly(img, ellipse_pts(mx + 2, my + 16, 13, 9, 20), (190, 80, 90), 1.0, mm)
        # teeth strip under the upper lip
        teeth = upper + [(p[0], p[1] + 7) for p in upper[::-1]]
        fill_poly(img, teeth, (250, 248, 246), 1.0, mm)
        stroke(img, [(p[0], p[1] + 7) for p in upper[2:-2]], 1.2, line_c, 0.35)
        stroke(img, poly, [2.6], line_c, 1.0, closed=True)
        # cheek dimples
        stroke(img, [(mx - 30, my - 12), (mx - 28, my - 4)], [0.4, 1.8], line_c, 0.5)
        stroke(img, [(mx + 30, my - 13), (mx + 28, my - 5)], [0.4, 1.8], line_c, 0.5)
    elif kind == "grit":
        poly = smooth([(mx - 22, my - 5, 's'), (mx + 22, my - 6, 's'), (mx + 20, my + 8, 's'), (mx - 20, my + 8, 's')], closed=True, n=4)
        shape(img, poly, (246, 242, 240), line_c, 2.6)
        stroke(img, [(mx - 20, my + 1), (mx + 20, my + 1)], 1.6, line_c, 0.8)
        for tx in (-12, -4, 4, 12):
            stroke(img, [(mx + tx, my - 4), (mx + tx, my + 7)], 1.2, line_c, 0.6)


# =========================================================================
# hair
# =========================================================================
def draw_hair_undercut_spiky(img, R, hair, hair_mask, layer):
    """Yuji-style: dark shaved sides + a pink cap whose top bursts into
    tapered locks pushed up / back.  `layer` = 'back' (before the face) or
    'front' (after the face)."""
    cx, cy = R["cx"], R["cap_cy"]
    rx, ry = R["cap_rx"], R["cap_ry"]
    col = C(hair["color"])
    sh = C(hair.get("shadow") or cel_shadow(col, 0.74))
    li = C(hair.get("line") or line_of(col))
    hi = C(hair.get("light") or cel_light(col, 0.30))
    locks = hair.get("locks", [])

    def lock_geom(ang, length, curl, wdt, base_r=0.80, tip_lean=0.0):
        length, wdt = length * R["hs"], wdt * R["hs"]
        a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a)
        bx, by = cx + ux * rx * base_r, cy + uy * ry * base_r
        ex, ey = cx + ux * rx * 1.0, cy + uy * ry * 1.0
        tip = (ex + ux * length + tip_lean * length, ey + uy * length)
        px, py = -uy, ux
        a_ = (bx + px * wdt * 0.5, by + py * wdt * 0.5)
        b_ = (bx - px * wdt * 0.5, by - py * wdt * 0.5)
        return lock_pts(a_, b_, tip, bulge=0.13, curl=curl)

    if layer == "back":
        # locks that sit behind the cap silhouette (drawn darker)
        for (ang, length, curl, wdt) in locks:
            pts = lock_geom(ang, length, curl, wdt)
            shape(img, pts, mix(col, sh, 0.35), li, 3.0, mask=hair_mask)
        return

    # ---- front layer ------------------------------------------------
    # cap: elliptical top + jagged hairline across the forehead
    hl = R["hairline"]
    top = ellipse_pts(cx, cy, rx, ry, 48, a0=math.radians(200), a1=math.radians(340))
    cap = top + hl
    shape(img, cap, col, li, 3.2, mask=hair_mask)
    # front tufts that cross the cap edge (pushed-up crest)
    for (ang, length, curl, wdt) in hair.get("front_locks", []):
        pts = lock_geom(ang, length, curl, wdt, base_r=0.55)
        shape(img, pts, col, li, 3.0, mask=hair_mask)
    # cel shading: shadow band above the hairline + underside of the mass
    band = [(p[0], p[1]) for p in hl] + [(p[0], p[1] - 22 * R["hs"]) for p in hl[::-1]]
    fill_poly(img, band, sh, 0.85, hair_mask)
    fill_poly(img, ellipse_pts(cx, cy + ry * 0.78, rx * 1.1, ry * 0.42, 40), sh, 0.55, hair_mask)
    # strand lines from the crown
    for (x0, y0, x1, y1) in hair.get("strands", []):
        stroke(img, smooth([(x0, y0), ((x0 + x1) / 2 + 6, (y0 + y1) / 2), (x1, y1)], closed=False, n=6),
               [0.4, 2.2, 0.6], li, 0.55, clip=hair_mask)
    # zig-zag highlight across the top
    zz = []
    xs = list(range(int(cx - rx * 0.78), int(cx + rx * 0.80), 14))
    for i, x in enumerate(xs):
        zz.append((x, cy - ry * 0.34 + (6 if i % 2 else -6)))
    zz2 = [(x, y + 15) for (x, y) in zz[::-1]]
    fill_poly(img, zz + zz2, hi, 0.75, hair_mask)


HAIR_STYLES = {"undercut_spiky": draw_hair_undercut_spiky}


# =========================================================================
# body / outfit
# =========================================================================
def draw_uniform_jjk(img, R, spec):
    """Tokyo Jujutsu High uniform: dark stand-collar jacket worn open over a
    red hoodie, dark trousers, white sneakers."""
    o = spec["outfit"]
    cx = R["cx"]
    jk = C(o.get("jacket", "#262a40"))
    jk_sh = C(o.get("jacket_shadow") or cel_shadow(jk, 0.62))
    jk_li = C(o.get("jacket_line", "#0a0b14"))
    hd = C(o.get("hoodie", "#c9302e"))
    hd_sh = C(o.get("hoodie_shadow") or cel_shadow(hd, 0.66))
    hd_li = C(o.get("hoodie_line", "#3a0c10"))
    tr = C(o.get("trousers", "#24283c"))
    tr_sh = C(o.get("trousers_shadow") or cel_shadow(tr, 0.62))
    tr_li = jk_li
    sh_c = C(o.get("shoes", "#f1f1f1"))
    sh_li = C(o.get("shoes_line", "#2c2c36"))
    skin = C(spec["skin"])
    skin_sh = C(spec.get("skin_shadow") or cel_shadow(skin, 0.80))
    skin_li = C(spec.get("skin_line") or line_of(skin, 0.42))
    bw = spec.get("build", {}).get("shoulders", 1.0)
    lw_ = spec.get("build", {}).get("legs", 1.0)

    sh_y = R["shoulder_y"]
    hem = R["hem_y"]

    # ---------------- shoes (drawn first: trouser cuffs overlap them)
    for sgn in (-1, 1):
        fx = cx + sgn * R["foot_dx"]
        top, bot = R["shoe_top"], R["shoe_bot"]
        pts = smooth([(fx - 44, top), (fx + 44, top), (fx + 56, top + 22), (fx + 58, bot - 14),
                      (fx + 50, bot), (fx - 50, bot), (fx - 58, bot - 14), (fx - 56, top + 22)], closed=True, n=6)
        m = shape_mask(img.w, img.h, pts)
        shape(img, pts, sh_c, sh_li, 3.0)
        # sole
        fill_poly(img, [(fx - 70, bot - 14), (fx + 70, bot - 14), (fx + 70, bot + 4), (fx - 70, bot + 4)], (214, 214, 220), 1.0, m)
        stroke(img, [(fx - 60, bot - 14), (fx + 60, bot - 14)], 2.4, sh_li, 0.9, clip=m)
        # toe cap + lace lines
        stroke(img, smooth([(fx - 30, bot - 26), (fx, bot - 34), (fx + 30, bot - 26)], closed=False, n=6), 2.0, sh_li, 0.55, clip=m)
        for i in range(3):
            yy = top + 12 + i * 10
            stroke(img, [(fx - 12, yy), (fx + 12, yy)], 2.0, sh_li, 0.55, clip=m)
        fill_poly(img, [(fx - 38, bot - 10), (fx + 38, bot - 10), (fx + 30, bot - 2), (fx - 30, bot - 2)], (170, 170, 178), 0.5, m)

    # ---------------- legs
    hip_y = R["hip_y"]
    ank = R["ankle_y"]
    for sgn in (-1, 1):
        x_hip = cx + sgn * R["leg_dx_hip"]
        x_ank = cx + sgn * R["leg_dx_ankle"]
        wh, wa = R["leg_w_hip"] * lw_, R["leg_w_ankle"] * lw_
        pts = smooth([(x_hip - wh * 0.5, hip_y - 20), (x_hip + wh * 0.5, hip_y - 20),
                      (x_hip + wh * 0.50, hip_y + 140), (x_ank + wa * 0.5, hip_y + 400),
                      (x_ank + wa * 0.52, ank), (x_ank - wa * 0.52, ank),
                      (x_ank - wa * 0.5, hip_y + 400), (x_hip - wh * 0.50, hip_y + 140)], closed=True, n=6)
        m = shape_mask(img.w, img.h, pts)
        shape(img, pts, tr, tr_li, 3.2)
        # inner-leg shadow (toward the centre) and knee crease
        inner = -sgn
        band = [(x_hip + inner * wh * 0.5, hip_y - 20), (x_hip + inner * wh * 0.18, hip_y - 20),
                (x_ank + inner * wa * 0.14, ank), (x_ank + inner * wa * 0.5, ank)]
        fill_poly(img, band, tr_sh, 0.85, m)
        ky = hip_y + 300
        stroke(img, smooth([(x_hip - 22, ky - 4), (x_hip, ky + 4), (x_hip + 22, ky - 4)], closed=False, n=6), [0.4, 2.0, 0.4], tr_li, 0.55, clip=m)
    # hips block (crotch) + shadow under the jacket hem
    hips = [(cx - R["hip_w"] * 0.5, hem - 40), (cx + R["hip_w"] * 0.5, hem - 40),
            (cx + R["hip_w"] * 0.5 + 4, hip_y + 30), (cx + 26, hip_y + 34), (cx, hip_y + 62),
            (cx - 26, hip_y + 34), (cx - R["hip_w"] * 0.5 - 4, hip_y + 30)]
    hips = smooth(hips, closed=True, n=5)
    m = shape_mask(img.w, img.h, hips)
    fill_poly(img, hips, tr)
    fill_poly(img, [(cx - 200, hem - 40), (cx + 200, hem - 40), (cx + 200, hem + 26), (cx - 200, hem + 26)], tr_sh, 0.9, m)
    stroke(img, [(cx, hip_y + 62), (cx, hip_y + 130)], [2.6, 0.6], tr_li, 0.7)

    # ---------------- hood (behind the neck)
    ny = R["neck_top"]
    hood = smooth([(cx - 104, sh_y + 16), (cx - 100, ny + 44), (cx - 78, ny + 6), (cx - 40, ny - 14),
                   (cx + 40, ny - 14), (cx + 78, ny + 6), (cx + 100, ny + 44), (cx + 104, sh_y + 16)], closed=True, n=6)
    hm = shape_mask(img.w, img.h, hood)
    shape(img, hood, hd, hd_li, 3.0)
    fill_poly(img, smooth([(cx - 90, ny + 34), (cx - 40, ny + 14), (cx + 40, ny + 14), (cx + 90, ny + 34),
                           (cx + 108, sh_y + 20), (cx - 108, sh_y + 20)], closed=True, n=5), hd_sh, 0.85, hm)
    stroke(img, smooth([(cx - 88, ny + 40), (cx - 52, ny + 12), (cx, ny + 2), (cx + 52, ny + 12), (cx + 88, ny + 40)], closed=False, n=6),
           [0.6, 2.4, 2.4, 2.4, 0.6], hd_li, 0.5, clip=hm)
    for sgn in (-1, 1):
        stroke(img, smooth([(cx + sgn * 92, sh_y + 10), (cx + sgn * 82, ny + 30), (cx + sgn * 66, ny + 6)], closed=False, n=6),
               [0.5, 2.0, 0.5], hd_li, 0.45, clip=hm)

    # ---------------- neck
    neck = smooth([(cx - 32, ny - 30, 's'), (cx + 32, ny - 30, 's'), (cx + 40, sh_y + 6), (cx - 40, sh_y + 6)], closed=True, n=6)
    nm = shape_mask(img.w, img.h, neck)
    fill_poly(img, neck, skin)
    fill_poly(img, [(cx - 60, ny - 40), (cx + 60, ny - 40), (cx + 60, ny + 36), (cx - 60, ny + 30)], skin_sh, 0.9, nm)
    stroke(img, [(cx - 32, ny - 20), (cx - 40, sh_y + 6)], 2.6, skin_li, 1.0)
    stroke(img, [(cx + 32, ny - 20), (cx + 40, sh_y + 6)], 2.6, skin_li, 1.0)

    # ---------------- hoodie front (visible between the open jacket)
    strip = smooth([(cx - 46, sh_y - 14, 's'), (cx + 46, sh_y - 14, 's'), (cx + 58, hem + 6, 's'), (cx - 58, hem + 6, 's')], closed=True, n=4)
    sm = shape_mask(img.w, img.h, strip)
    fill_poly(img, strip, hd)
    # hoodie collar (rounded neckline) and shading
    coll = smooth([(cx - 46, sh_y - 14), (cx - 20, sh_y + 4), (cx, sh_y + 10), (cx + 20, sh_y + 4), (cx + 46, sh_y - 14),
                   (cx + 46, sh_y - 30), (cx - 46, sh_y - 30)], closed=True, n=6)
    fill_poly(img, coll, hd_sh, 0.9, sm)
    stroke(img, smooth([(cx - 46, sh_y - 14), (cx - 20, sh_y + 4), (cx, sh_y + 10), (cx + 20, sh_y + 4), (cx + 46, sh_y - 14)], closed=False, n=6),
           2.6, hd_li, 0.9, clip=sm)
    fill_poly(img, [(cx - 60, sh_y + 40), (cx - 30, sh_y + 40), (cx - 26, hem + 6), (cx - 60, hem + 6)], hd_sh, 0.9, sm)
    fill_poly(img, [(cx - 60, hem - 26), (cx + 60, hem - 26), (cx + 60, hem + 8), (cx - 60, hem + 8)], hd_sh, 0.7, sm)
    # drawstrings
    for sgn in (-1, 1):
        sx = cx + sgn * 13
        pts = smooth([(sx, sh_y + 8), (sx + sgn * 4, sh_y + 60), (sx + sgn * 2, sh_y + 108)], closed=False, n=6)
        stroke(img, pts, 4.6, hd_li, 0.9, clip=sm)
        stroke(img, pts, 2.6, (238, 232, 228), 1.0, clip=sm)
        fill_poly(img, circle_pts(sx + sgn * 2, sh_y + 112, 4, 10), (238, 232, 228), 1.0, sm)
        stroke(img, circle_pts(sx + sgn * 2, sh_y + 112, 4, 10), 1.4, hd_li, 0.9, closed=True, clip=sm)

    # ---------------- jacket panels (left = viewer's left)
    sw = R["shoulder_w"] * bw
    for sgn in (-1, 1):
        panel = smooth([(cx + sgn * 40, sh_y - 22, 's'), (cx + sgn * 120, sh_y - 8), (cx + sgn * sw * 0.86, sh_y + 2),
                        (cx + sgn * sw, sh_y + 44), (cx + sgn * (sw - 8), sh_y + 96), (cx + sgn * (sw - 34), sh_y + 240),
                        (cx + sgn * (sw - 44), hem - 20), (cx + sgn * (sw - 44), hem, 's'),
                        (cx + sgn * 48, hem, 's'), (cx + sgn * 44, hem - 200), (cx + sgn * 40, sh_y + 80)], closed=True, n=6)
        pm = shape_mask(img.w, img.h, panel)
        shape(img, panel, jk, jk_li, 3.4)
        # shadow along the inner (open) edge and under the arm
        inner_band = [(cx + sgn * 40, sh_y - 30), (cx + sgn * 78, sh_y - 30), (cx + sgn * 82, hem + 4), (cx + sgn * 40, hem + 4)]
        fill_poly(img, inner_band, jk_sh, 0.9, pm)
        arm_band = [(cx + sgn * (sw - 60), sh_y + 40), (cx + sgn * (sw + 10), sh_y + 40), (cx + sgn * (sw + 10), hem + 4), (cx + sgn * (sw - 60), hem + 4)]
        fill_poly(img, arm_band, jk_sh, 0.55, pm)
        # shoulder seam + a hint of the lapel edge lighter rim
        stroke(img, [(cx + sgn * 118, sh_y - 8), (cx + sgn * (sw - 26), sh_y + 8)], 1.8, jk_li, 0.6, clip=pm)
        stroke(img, [(cx + sgn * 46, sh_y - 10), (cx + sgn * 50, hem - 8)], 2.0, mix(jk, (140, 145, 170), 0.35), 0.8, clip=pm)
    # collar flaps (stand collar, unhooked, folded slightly outward)
    for sgn in (-1, 1):
        flap = smooth([(cx + sgn * 40, sh_y - 22, 's'), (cx + sgn * 44, sh_y - 60, 's'), (cx + sgn * 82, sh_y - 66, 's'),
                       (cx + sgn * 112, sh_y - 4, 's')], closed=True, n=4)
        fm = shape_mask(img.w, img.h, flap)
        shape(img, flap, jk, jk_li, 3.2)
        fill_poly(img, [(cx + sgn * 70, sh_y - 80), (cx + sgn * 140, sh_y - 80), (cx + sgn * 140, sh_y + 10), (cx + sgn * 70, sh_y + 10)], jk_sh, 0.7, fm)
        stroke(img, [(cx + sgn * 48, sh_y - 54), (cx + sgn * 80, sh_y - 60)], 1.6, mix(jk, (150, 155, 180), 0.4), 0.7, clip=fm)

    # ---------------- hands (under the cuffs) then sleeves
    wrist_y = R["wrist_y"]
    for sgn in (-1, 1):
        S_ = (cx + sgn * (sw - 12), sh_y + 34)          # shoulder joint
        E_ = (cx + sgn * (sw + 18), sh_y + 226)         # elbow
        Wr = (cx + sgn * (sw + 10), wrist_y - 8)        # wrist
        # hand centred under the cuff
        hx, hy_ = Wr[0], Wr[1] - 2
        hand = smooth([(hx - 19, hy_), (hx + 19, hy_), (hx + 24, hy_ + 26), (hx + 20, hy_ + 46), (hx + 13, hy_ + 58),
                       (hx + 3, hy_ + 62), (hx - 6, hy_ + 60), (hx - 15, hy_ + 52), (hx - 22, hy_ + 30)], closed=True, n=6)
        hm2 = shape_mask(img.w, img.h, hand)
        shape(img, hand, skin, skin_li, 2.8)
        fill_poly(img, [(hx - 40, hy_ - 4), (hx + 40, hy_ - 4), (hx + 40, hy_ + 14), (hx - 40, hy_ + 16)], skin_sh, 0.9, hm2)
        th = ellipse_pts(hx - sgn * 20, hy_ + 20, 8, 15, 16, rot=sgn * 0.35)
        fill_poly(img, th, skin, 1.0)
        stroke(img, th, 2.4, skin_li, 1.0, closed=True, clip=hm2.inverted())
        for i in range(3):
            fx = hx - 8 + i * 9
            stroke(img, [(fx + 1, hy_ + 40), (fx, hy_ + 58)], [0.5, 2.0], skin_li, 0.7, clip=hm2)
        # sleeve = tube around the centre line, tapering toward the cuff
        centre = smooth([S_, E_, Wr], closed=False, n=10)
        tube = stroke_outline(centre, [78, 70, 58], closed=False)[0]
        capr = 39
        am = shape_mask(img.w, img.h, tube)
        fill_poly(am, circle_pts(S_[0], S_[1], capr, 24), None)
        fill_poly(img, tube, jk)
        fill_poly(img, circle_pts(S_[0], S_[1], capr, 24), jk)
        stroke(img, tube, 3.4, jk_li, closed=True, clip=shape_mask(img.w, img.h, circle_pts(S_[0], S_[1], capr, 24)).inverted())
        stroke(img, circle_pts(S_[0], S_[1], capr, 24), 3.4, jk_li, closed=True,
               clip=shape_mask(img.w, img.h, tube).inverted())
        # shading: inner side of the sleeve (toward the body) + cuff
        inner = [(p[0] - sgn * 40, p[1]) for p in centre] + [(p[0] - sgn * 10, p[1]) for p in centre[::-1]]
        fill_poly(img, inner, jk_sh, 0.8, am)
        cuff = [(Wr[0] - 40, Wr[1] - 18), (Wr[0] + 40, Wr[1] - 18), (Wr[0] + 40, Wr[1] + 6), (Wr[0] - 40, Wr[1] + 6)]
        fill_poly(img, cuff, jk_sh, 0.6, am)
        stroke(img, [(Wr[0] - 34, Wr[1] - 18), (Wr[0] + 34, Wr[1] - 18)], 2.4, jk_li, 0.8, clip=am)
        stroke(img, smooth([(E_[0] - sgn * 26, E_[1] - 10), (E_[0] - sgn * 6, E_[1] + 6), (E_[0] + sgn * 14, E_[1])], closed=False, n=6),
               [0.4, 2.2, 0.4], jk_li, 0.55, clip=am)


# =========================================================================
# head
# =========================================================================
def draw_head(img, R, spec, expression):
    exp = EXPR[expression]
    cx = R["cx"]
    skin = C(spec["skin"])
    skin_sh = C(spec.get("skin_shadow") or cel_shadow(skin, 0.80))
    skin_li = C(spec.get("skin_line") or line_of(skin, 0.42))
    hair = spec["hair"]
    hcol = C(hair["color"])
    hline = C(hair.get("line") or line_of(hcol))
    eyes = spec["eyes"]
    eye_col = dict(iris=C(eyes["iris"]),
                   iris_dark=C(eyes.get("iris_dark") or mul(C(eyes["iris"]), 0.55)),
                   iris_light=C(eyes.get("iris_light") or mix(C(eyes["iris"]), (255, 230, 200), 0.35)),
                   pupil=C(eyes.get("pupil", "#1a100c")))
    line_eye = C(eyes.get("line", "#2a1712"))
    brow_c = C(spec.get("brow", hair.get("line") or line_of(hcol)))

    face = R["face"]
    hair_mask = Mask(img.w, img.h)

    # hair layer behind the head
    HAIR_STYLES[hair.get("style", "undercut_spiky")](img, R, hair, hair_mask, "back")

    # ears
    for sgn in (-1, 1):
        ex_, ey_ = cx + sgn * R["ear_dx"], R["ear_y"]
        pts = ellipse_pts(ex_, ey_, 13 * R["hs"], 21 * R["hs"], 20, rot=sgn * 0.12)
        em = shape_mask(img.w, img.h, pts)
        shape(img, pts, skin, skin_li, 2.8)
        stroke(img, smooth([(ex_ + sgn * 4, ey_ - 12), (ex_ + sgn * 7, ey_), (ex_ + sgn * 2, ey_ + 9)], closed=False, n=6), [0.6, 2.0, 1.0], skin_li, 0.7, clip=em)
        fill_poly(img, ellipse_pts(ex_ + sgn * 2, ey_ + 4, 8, 12, 14), skin_sh, 0.6, em)

    # face
    fm = shape_mask(img.w, img.h, face)
    shape(img, face, skin, skin_li, 3.2)
    # cel shadow: side of the face away from the light + under the fringe
    hs = R["hs"]
    side_sh = smooth([(cx - 86 * hs, R["eye_y"] - 60 * hs), (cx - 76 * hs, R["eye_y"] + 20 * hs), (cx - 60 * hs, R["chin_y"] - 20 * hs),
                      (cx - 28 * hs, R["chin_y"] + 4), (cx - 46 * hs, R["chin_y"] + 12), (cx - 90 * hs, R["chin_y"] - 30 * hs),
                      (cx - 100 * hs, R["eye_y"] - 40 * hs)], closed=True, n=5)
    fill_poly(img, side_sh, skin_sh, 0.8, fm)
    hl = R["hairline"]
    fringe_sh = [(p[0], p[1]) for p in hl] + [(p[0], p[1] + 14) for p in hl[::-1]]
    fill_poly(img, fringe_sh, skin_sh, 0.85, fm)
    # temples (undercut skin edge) - drawn by the hair style; chin shadow
    fill_poly(img, ellipse_pts(cx + 4, R["chin_y"] - 10 * hs, 30 * hs, 9 * hs, 20), skin_sh, 0.35, fm)

    # undercut (dark shaved sides) sits on the skull above the ears
    uc = hair.get("undercut")
    if uc:
        ucol = C(uc)
        uli = C(hair.get("undercut_line") or mul(ucol, 0.5))
        hs = R["hs"]
        cb = R["cap_cy"] + 20 * hs
        ey0 = R["ear_y"]
        for sgn in (-1, 1):
            pts = smooth([(cx + sgn * 72 * hs, cb - 6), (cx + sgn * 88 * hs, cb - 14), (cx + sgn * 93 * hs, cb + 10),
                          (cx + sgn * 92 * hs, ey0 - 6), (cx + sgn * 86 * hs, ey0 + 30), (cx + sgn * 80 * hs, ey0 + 20),
                          (cx + sgn * 78 * hs, ey0 - 10), (cx + sgn * 74 * hs, cb + 16)], closed=True, n=6)
            um = shape_mask(img.w, img.h, pts)
            shape(img, pts, ucol, uli, 2.6)
            for k in range(3):
                yy = cb + 12 + k * 12 * hs
                stroke(img, [(cx + sgn * 78 * hs, yy), (cx + sgn * 90 * hs, yy - 5)], 1.4, uli, 0.35, clip=um)

    # ---- features
    ey, edx, ew, eh = R["eye_y"], R["eye_dx"], R["eye_w"], R["eye_h"]
    for sgn in (-1, 1):
        draw_eye(img, cx + sgn * edx, ey, sgn, ew, eh, eye_col, exp, line_eye)
        if spec.get("undereye_marks"):
            draw_undereye_marks(img, cx + sgn * edx, ey, sgn, ew, eh, line_eye, exp)
        draw_brow(img, cx + sgn * edx, ey, sgn, ew, eh, brow_c, exp, spec.get("brow_thick", 1.0))
    draw_nose(img, R["nose"][0], R["nose"][1], skin_li, skin_sh, fm)
    draw_mouth(img, R["mouth"][0], R["mouth"][1], exp["mouth"], skin_li, skin_sh, fm)
    # blush / cheek warmth for happy
    if expression == "happy":
        for sgn in (-1, 1):
            fill_poly(img, ellipse_pts(cx + sgn * 52 * hs, ey + 34 * hs, 20 * hs, 9 * hs, 16), (232, 140, 130), 0.28, fm)

    # hair in front
    HAIR_STYLES[hair.get("style", "undercut_spiky")](img, R, hair, hair_mask, "front")


# =========================================================================
# rig layout
# =========================================================================
def build_rig(spec):
    b = spec.get("build", {})
    hs = b.get("head", 1.0) * 0.92
    cx = W * 0.5
    R = {"cx": cx, "hs": hs}
    head_cy = 232
    R["head_cy"] = head_cy
    R["chin_y"] = head_cy + 100 * hs
    R["neck_top"] = R["chin_y"] - 22
    R["eye_y"] = head_cy + 22 * hs
    R["eye_dx"] = 44 * hs
    R["eye_w"] = 52 * hs
    R["eye_h"] = 34 * hs
    R["nose"] = (cx + 5 * hs, head_cy + 54 * hs)
    R["mouth"] = (cx + 1 * hs, head_cy + 78 * hs)
    R["ear_dx"] = 85 * hs
    R["ear_y"] = head_cy + 18 * hs
    # face outline (front view, strong jaw, flat-ish chin)
    fpts = [(0, -100), (-58, -90), (-82, -40), (-84, 14), (-78, 52), (-60, 84), (-30, 100), (0, 103),
            (30, 100), (60, 84), (78, 52), (84, 14), (82, -40), (58, -90)]
    R["face"] = smooth([(cx + x * hs, head_cy + y * hs) for (x, y) in fpts], closed=True, n=7)
    # hair cap (ellipse) + hairline with a down-pointing temple lock each side
    R["cap_cy"] = head_cy - 64 * hs
    R["cap_rx"] = 93 * hs
    R["cap_ry"] = 66 * hs
    hy = R["cap_cy"]
    hpts = [(92, 16), (86, 56), (74, 30), (60, 50), (46, 28), (34, 44), (20, 30), (4, 52), (-12, 32), (-26, 44),
            (-42, 26), (-54, 46), (-70, 28), (-86, 56), (-92, 16)]
    R["hairline"] = [(cx + x * hs, hy + y * hs) for (x, y) in hpts]
    # body
    R["shoulder_y"] = 392
    R["shoulder_w"] = 186
    R["hem_y"] = 790
    R["hip_y"] = 802
    R["hip_w"] = 236
    R["wrist_y"] = 800
    R["leg_dx_hip"] = 62
    R["leg_dx_ankle"] = 76
    R["leg_w_hip"] = 104
    R["leg_w_ankle"] = 74
    R["ankle_y"] = 1332
    R["foot_dx"] = 80
    R["shoe_top"] = 1318
    R["shoe_bot"] = 1384
    return R


# =========================================================================
# public API
# =========================================================================
def render_character(spec, expression="neutral"):
    """Render one full-body 760x1400 RGBA sprite.  `spec` is a plain dict
    (see YUJI below); `expression` is one of EXPRESSIONS."""
    if expression not in EXPR:
        raise ValueError("unknown expression %r (want one of %s)" % (expression, ", ".join(EXPRESSIONS)))
    img = Img(W, H, alpha=True)
    R = build_rig(spec)
    draw_uniform_jjk(img, R, spec)
    draw_head(img, R, spec, expression)
    return img


YUJI = {
    "name": "yuji",
    "skin": "#f4c9a3",
    "skin_shadow": "#dda07c",
    "skin_line": "#5a2f24",
    "hair": {
        "style": "undercut_spiky",
        "color": "#f39aa9",
        "shadow": "#d86f82",
        "light": "#fbc6cf",
        "line": "#5e2438",
        "undercut": "#3b2b31",
        "undercut_line": "#1a1114",
        # (angle deg from +x, ccw with y up; length px; curl; base width px)
        "locks": [(142, 44, -0.12, 40), (125, 66, -0.08, 46), (108, 80, -0.04, 50), (92, 84, 0.00, 50),
                  (76, 78, 0.04, 48), (60, 64, 0.08, 44), (44, 44, 0.12, 38)],
        "front_locks": [(114, 40, -0.06, 34), (92, 46, 0.00, 36), (70, 38, 0.06, 32)],
        "strands": [(362, 126, 334, 190), (398, 118, 402, 192), (430, 134, 452, 184), (380, 116, 372, 180)],
    },
    "eyes": {"iris": "#8c5a34", "iris_dark": "#3f2412", "iris_light": "#d9a874", "pupil": "#1c1009", "line": "#2b1712"},
    "brow": "#5a2a30",
    "brow_thick": 1.1,
    "undereye_marks": True,
    "build": {"shoulders": 1.0, "legs": 1.0, "head": 1.0},
    "outfit": {
        "type": "jjk_uniform",
        "jacket": "#252a41", "jacket_shadow": "#141727", "jacket_line": "#090a12",
        "hoodie": "#cc2f2d", "hoodie_shadow": "#8a1c1f", "hoodie_line": "#3a0c10",
        "trousers": "#252a40", "trousers_shadow": "#141727",
        "shoes": "#f2f2f2", "shoes_line": "#2b2b35",
    },
}


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(_TOOLS), "game", "images", "char")
    os.makedirs(out_dir, exist_ok=True)
    for expr, fname in (("neutral", "_test_yuji_B.png"), ("happy", "_test_yuji_B_happy.png")):
        t = time.time()
        im = render_character(YUJI, expr)
        path = os.path.join(out_dir, fname)
        im.save(path)
        print("%-10s %-28s %.1fs" % (expr, path, time.time() - t))
