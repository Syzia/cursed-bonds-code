#!/usr/bin/env python3
"""anime_C.py -- proportion-driven, cel-shaded anime sprite renderer (approach C).

Pure Python (no Pillow / numpy).  Builds a 760x1400 RGBA sprite from a plain
dict "spec" describing one character, using a 6.5-head anime proportion chart
and reusable parametric parts (head, eyes, brows, mouth, hair, body, jacket,
arms, hands, legs, shoes).  Everything is drawn on a 2x supersampled canvas
that is box-downsampled at the end so all edges are anti-aliased; every *part*
first paints its dilated silhouette in a dark line colour and then its flat
fill, which produces the ~3px line-art outline of classic cel animation
wherever two parts meet.

Public API
----------
    render_character(spec: dict, expression: str) -> raster.Img
    EXPRESSIONS  -- tuple of supported expression names
    YUJI         -- example spec (Yuji Itadori); CAST -- {name: spec}
    HAIR_STYLES  -- registry {style name: draw function}; add your own.

Spec format (all colours '#rrggbb' or (r,g,b); everything optional except
skin / hair.color -- see YUJI at the bottom for a complete example):

    {
      "skin": .., "skin_shadow": .., "skin_line": .., "line": ..,
      "face":  {"jaw": 1.0, "chin": 1.0},                 # 1 = square-ish male
      "hair":  {"style": "undercut_spiky", "color": .., "shadow": .., "highlight": ..,
                "line": .., "undercut": .., "spikes": 7, "spike_len": 46,
                "lean": 0.0, "fringe": [(x_frac, drop, dir), ...]},
      "eyes":  {"iris": .., "iris_dark": .., "white": .., "size": 1.0, "spacing": 41,
                "bags": True, "brow": .., "brow_thick": 1.0},
      "build": {"shoulder": 1.0, "waist": 1.0, "hip": 1.0, "neck": 1.0, "arm": 1.0,
                "leg": 1.0, "height": 1.0, "width": 1.0},
      "outfit":{"jacket": .., "jacket_shadow": .., "jacket_light": .., "open": True,
                "hoodie": .., "hoodie_shadow": .., "hood": True,
                "trousers": .., "trousers_shadow": .., "shoes": .., "sole": ..,
                "shoe_accent": ..},
      "pose":  {"arms": "relaxed", "hands": "relaxed"},
    }

Usage: python3 anime_C.py [expression ...]   -> renders the Yuji test sprites.
"""
import sys, os, math, time
TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import raster
from raster import Img, hexc

W, H = 760, 1400
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")


# =============================================================================
#  Small vector helpers
# =============================================================================
def vadd(a, b): return (a[0] + b[0], a[1] + b[1])
def vsub(a, b): return (a[0] - b[0], a[1] - b[1])
def vmul(a, s): return (a[0] * s, a[1] * s)
def vlerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def vlen(a): return math.hypot(a[0], a[1])


def vnorm(a):
    l = vlen(a)
    return (a[0] / l, a[1] / l) if l > 1e-9 else (0.0, 0.0)


def qbez(p0, c, p1, n=10):
    """Quadratic bezier, returns n points *excluding* p0, including p1."""
    out = []
    for i in range(1, n + 1):
        t = i / float(n)
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
                    u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]))
    return out


def cbez(p0, c1, c2, p1, n=12):
    """Cubic bezier, returns n points *excluding* p0, including p1."""
    out = []
    for i in range(1, n + 1):
        t = i / float(n)
        u = 1.0 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p1[0],
                    u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p1[1]))
    return out


def ellipse_pts(cx, cy, rx, ry, n=40, a0=0.0, a1=2 * math.pi):
    """Polygon approximating an ellipse arc (angles in *image* space: y down,
    a=pi/2 is the TOP of the ellipse)."""
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / float(n)
        out.append((cx + rx * math.cos(a), cy - ry * math.sin(a)))
    return out


class Path(object):
    """Tiny SVG-ish path builder producing a flattened polygon."""

    def __init__(self, start):
        self.pts = [start]

    def L(self, p):
        self.pts.append(p); return self

    def Q(self, c, p, n=10):
        self.pts += qbez(self.pts[-1], c, p, n); return self

    def C(self, c1, c2, p, n=12):
        self.pts += cbez(self.pts[-1], c1, c2, p, n); return self

    def arc(self, cx, cy, rx, ry, a0, a1, n=24):
        self.pts += ellipse_pts(cx, cy, rx, ry, n, a0, a1)[1:]; return self

    def done(self):
        return self.pts


def mirror(pts, cx):
    return [(2 * cx - x, y) for (x, y) in pts]


def symmetric(left, cx):
    """left: points running down the LEFT half from the top-centre to the
    bottom-centre; returns the closed, mirrored polygon."""
    return list(left) + mirror(list(reversed(left)), cx)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def col(v):
    """Accept '#rrggbb' or an (r,g,b) tuple."""
    if isinstance(v, str):
        return hexc(v)
    return tuple(v)


def ribbon(pts, widths, cap0=True, cap1=True):
    """Polygon of a variable-width ribbon along polyline `pts`.
    widths: number, (w0, w1) linear taper, or one width per point."""
    n = len(pts)
    if isinstance(widths, (int, float)):
        ws = [float(widths)] * n
    elif len(widths) == 2 and n != 2:
        ws = [widths[0] + (widths[1] - widths[0]) * i / (n - 1.0) for i in range(n)]
    else:
        ws = list(widths)
    left, right = [], []
    for i in range(n):
        if i == 0:
            d = vnorm(vsub(pts[1], pts[0]))
        elif i == n - 1:
            d = vnorm(vsub(pts[-1], pts[-2]))
        else:
            d = vnorm(vadd(vnorm(vsub(pts[i], pts[i - 1])), vnorm(vsub(pts[i + 1], pts[i]))))
            if d == (0.0, 0.0):
                d = vnorm(vsub(pts[i + 1], pts[i]))
        nrm = (-d[1], d[0])
        hw = ws[i] * 0.5
        left.append(vadd(pts[i], vmul(nrm, hw)))
        right.append(vsub(pts[i], vmul(nrm, hw)))
    poly = list(left)
    if cap1:
        d = vnorm(vsub(pts[-1], pts[-2])); hw = ws[-1] * 0.5
        ang = math.atan2(-d[1], d[0])
        for k in range(1, 6):
            t = ang + math.pi / 2 - math.pi * k / 6.0
            poly.append((pts[-1][0] + hw * math.cos(t), pts[-1][1] - hw * math.sin(t)))
    poly += right[::-1]
    if cap0:
        d = vnorm(vsub(pts[0], pts[1])); hw = ws[0] * 0.5
        ang = math.atan2(-d[1], d[0])
        for k in range(1, 6):
            t = ang + math.pi / 2 - math.pi * k / 6.0
            poly.append((pts[0][0] + hw * math.cos(t), pts[0][1] - hw * math.sin(t)))
    return poly


# =============================================================================
#  Span geometry (scanline intervals at supersampled resolution)
#  A "spans" object is {row: [(x0, x1), ...]} with sorted, disjoint floats.
# =============================================================================
def spans_from_poly(pts):
    n = len(pts)
    if n < 3:
        return {}
    edges = []
    ymin, ymax = 1e9, -1e9
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if y1 == y2:
            continue
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        edges.append((y1, y2, x1, (x2 - x1) / (y2 - y1)))
        ymin = min(ymin, y1); ymax = max(ymax, y2)
    if not edges:
        return {}
    edges.sort()
    spans = {}
    ei = 0
    active = []
    y = int(math.floor(ymin))
    yend = int(math.ceil(ymax))
    ne = len(edges)
    while y <= yend:
        yc = y + 0.5
        while ei < ne and edges[ei][0] <= yc:
            active.append(edges[ei]); ei += 1
        if active:
            xs = []
            keep = []
            for e in active:
                if yc < e[1]:
                    keep.append(e)
                    if yc >= e[0]:
                        xs.append(e[2] + (yc - e[0]) * e[3])
            active = keep
            if len(xs) >= 2:
                xs.sort()
                row = []
                for i in range(0, len(xs) - 1, 2):
                    if xs[i + 1] > xs[i]:
                        row.append((xs[i], xs[i + 1]))
                if row:
                    spans[y] = row
        y += 1
    return spans


def _merge_row(a, b):
    ivs = sorted(a + b)
    out = []
    for x0, x1 in ivs:
        if out and x0 <= out[-1][1]:
            if x1 > out[-1][1]:
                out[-1] = (out[-1][0], x1)
        else:
            out.append((x0, x1))
    return out


def spans_union(a, b):
    out = dict(a)
    for y, row in b.items():
        if y in out:
            out[y] = _merge_row(out[y], row)
        else:
            out[y] = list(row)
    return out


def _intersect_row(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        x0 = max(a[i][0], b[j][0]); x1 = min(a[i][1], b[j][1])
        if x1 > x0:
            out.append((x0, x1))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def spans_intersect(a, b):
    out = {}
    for y, row in a.items():
        if y in b:
            r = _intersect_row(row, b[y])
            if r:
                out[y] = r
    return out


def _subtract_row(a, b):
    out = []
    for x0, x1 in a:
        cur = x0
        for bx0, bx1 in b:
            if bx1 <= cur or bx0 >= x1:
                continue
            if bx0 > cur:
                out.append((cur, bx0))
            cur = max(cur, bx1)
            if cur >= x1:
                break
        if cur < x1:
            out.append((cur, x1))
    return out


def spans_subtract(a, b):
    out = {}
    for y, row in a.items():
        if y in b:
            r = _subtract_row(row, b[y])
            if r:
                out[y] = r
        else:
            out[y] = row
    return out


# =============================================================================
#  Supersampled RGBA canvas
# =============================================================================
class Canvas(object):
    def __init__(self, w=W, h=H, ss=2):
        self.S = ss
        self.W, self.H = w * ss, h * ss
        self.w, self.h = w, h
        self.buf = bytearray(self.W * self.H * 4)
        self.bb = [self.W, self.H, 0, 0]
        # figure transform (1x space): x' = cx + (x-cx)*sx ; y' = yb - (yb-y)*sy
        self.tf = (1.0, 1.0, w / 2.0, h - 15.0)

    def set_transform(self, sx=1.0, sy=1.0, cx=None, yb=None):
        _, _, ocx, oyb = self.tf
        self.tf = (sx, sy, ocx if cx is None else cx, oyb if yb is None else yb)

    def xf(self, p):
        sx, sy, cx, yb = self.tf
        return ((cx + (p[0] - cx) * sx) * self.S, (yb - (yb - p[1]) * sy) * self.S)

    def poly_spans(self, pts):
        return spans_from_poly([self.xf(p) for p in pts])

    def shape(self, *polys):
        sp = {}
        for p in polys:
            sp = spans_union(sp, self.poly_spans(p))
        return sp

    # --- painting -----------------------------------------------------------
    def _blend(self, i, color, a):
        b = self.buf
        da = b[i + 3] / 255.0
        na = a + da * (1.0 - a)
        if na <= 0.0:
            return
        k = da * (1.0 - a)
        b[i] = int((color[0] * a + b[i] * k) / na + 0.5)
        b[i + 1] = int((color[1] * a + b[i + 1] * k) / na + 0.5)
        b[i + 2] = int((color[2] * a + b[i + 2] * k) / na + 0.5)
        b[i + 3] = int(na * 255.0 + 0.5)

    def fill(self, spans, color, a=1.0, dx=0.0, dy=0):
        """Paint spans (supersampled coords) with fractional end coverage."""
        buf = self.buf
        Wd = self.W
        Hd = self.H
        px = bytes((color[0], color[1], color[2], 255))
        bb = self.bb
        blend = self._blend
        for y, row in spans.items():
            yy = y + dy
            if yy < 0 or yy >= Hd:
                continue
            base = yy * Wd * 4
            if yy < bb[1]: bb[1] = yy
            if yy + 1 > bb[3]: bb[3] = yy + 1
            for x0, x1 in row:
                x0 += dx; x1 += dx
                if x1 <= 0.0 or x0 >= Wd:
                    continue
                if x0 < 0.0: x0 = 0.0
                if x1 > Wd: x1 = float(Wd)
                ix0 = int(x0); ix1 = int(x1)
                if ix0 < bb[0]: bb[0] = ix0
                if ix1 + 1 > bb[2]: bb[2] = min(Wd, ix1 + 1)
                if ix0 == ix1:
                    blend(base + ix0 * 4, color, a * (x1 - x0))
                    continue
                f0 = x0 - ix0
                if f0 > 0.002:
                    blend(base + ix0 * 4, color, a * (1.0 - f0))
                    start = ix0 + 1
                else:
                    start = ix0
                if ix1 > start:
                    if a >= 1.0:
                        buf[base + start * 4: base + ix1 * 4] = px * (ix1 - start)
                    else:
                        for x in range(start, ix1):
                            blend(base + x * 4, color, a)
                f1 = x1 - ix1
                if f1 > 0.002 and ix1 < Wd:
                    blend(base + ix1 * 4, color, a * f1)

    def outline(self, spans, width, color):
        """Dilate the silhouette by `width` (1x px) and paint it in `color`."""
        r = width * self.S
        self.fill(spans, color)
        n = 16 if r > 3 else 10
        for i in range(n):
            a = 2 * math.pi * i / n
            self.fill(spans, color, dx=r * math.cos(a), dy=int(round(r * math.sin(a))))
        if r > 4:
            r2 = r * 0.5
            for i in range(8):
                a = 2 * math.pi * (i + 0.5) / 8
                self.fill(spans, color, dx=r2 * math.cos(a), dy=int(round(r2 * math.sin(a))))

    def part(self, spans, color, line=None, width=3.0):
        """Outline (dilated silhouette in `line`) then flat fill. Returns spans."""
        if line is not None and width > 0:
            self.outline(spans, width, line)
        self.fill(spans, color)
        return spans

    def clipfill(self, spans, polys, color, a=1.0):
        """Fill the intersection of `spans` with the union of polys (1x)."""
        self.fill(spans_intersect(spans, self.shape(*polys)), color, a)

    def stroke(self, pts, width, color, a=1.0, cap=True, closed=False):
        """Paint a polyline as a ribbon. width: number, (w0, w1) taper, or list."""
        if closed:
            pts = list(pts) + [pts[0]]
        if len(pts) < 2:
            return
        self.fill(self.poly_spans(ribbon(pts, width, cap, cap)), color, a)

    def dot(self, c, r, color, a=1.0):
        self.fill(self.poly_spans(ellipse_pts(c[0], c[1], r, r, 16)), color, a)

    # --- output ---------------------------------------------------------------
    def downsample(self):
        out = Img(self.w, self.h, alpha=True)
        S = self.S
        Wd = self.W
        buf = self.buf
        ob = out.buf
        x0, y0, x1, y1 = self.bb
        if x1 <= x0 or y1 <= y0:
            return out
        X0, X1 = x0 // S, min(self.w, (x1 + S - 1) // S)
        Y0, Y1 = y0 // S, min(self.h, (y1 + S - 1) // S)
        n = S * S
        offs = [(j * Wd + i) * 4 for j in range(S) for i in range(S)]
        ow = self.w
        for y in range(Y0, Y1):
            rowbase = (y * S) * Wd * 4
            obase = y * ow * 4
            for x in range(X0, X1):
                b0 = rowbase + x * S * 4
                asum = 0; r = 0; g = 0; bl = 0
                for o in offs:
                    i = b0 + o
                    a = buf[i + 3]
                    if a:
                        asum += a
                        r += buf[i] * a; g += buf[i + 1] * a; bl += buf[i + 2] * a
                if asum:
                    j = obase + x * 4
                    ob[j] = r // asum; ob[j + 1] = g // asum; ob[j + 2] = bl // asum
                    ob[j + 3] = asum // n
        return out


# =============================================================================
#  Proportion chart (1x pixels, figure centred at CX)
#  6.5-head anime figure; HU = one head unit (chin to skull top).
#  Hair volume/spikes rise ~55px above SKULL_TOP into the top margin.
# =============================================================================
CX = W / 2.0
HU = 196.0
SKULL_TOP = 96.0
CHIN = SKULL_TOP + HU                 # 292
HEAD_RX, HEAD_RY = 82.0, 92.0
HEAD_CY = SKULL_TOP + HEAD_RY         # 188 skull ellipse centre
BROW_Y = SKULL_TOP + HU * 0.470       # 188
EYE_Y = SKULL_TOP + HU * 0.565        # 207
NOSE_Y = SKULL_TOP + HU * 0.760       # 245
MOUTH_Y = SKULL_TOP + HU * 0.870      # 266
HAIRLINE_Y = SKULL_TOP + 54           # 150 (centre of forehead)
SHOULDER_Y = SKULL_TOP + HU * 1.310   # 353 (neck base / trapezius)
CHEST_Y = SKULL_TOP + HU * 1.780      # 445
WAIST_Y = SKULL_TOP + HU * 2.850      # 655
HIP_Y = SKULL_TOP + HU * 3.500        # 782
HEM_Y = SKULL_TOP + HU * 3.720        # 825 jacket hem
CROTCH_Y = SKULL_TOP + HU * 3.800     # 841
KNEE_Y = SKULL_TOP + HU * 5.100       # 1096
ANKLE_Y = SKULL_TOP + HU * 6.250      # 1321
FEET_Y = SKULL_TOP + HU * 6.560       # 1382


# =============================================================================
#  Expressions (what changes: eyes, brows, mouth)
# =============================================================================
EXPR = {
    # eye_open: upper-lid openness; low_lid: lower lid raised (squint/smile);
    # iris: iris scale; brow_in/out: +down (px) of inner/outer brow ends;
    # arch: brow curvature; tilt: upper-lid slant (+ = outer corner up);
    # mouth: style name
    "neutral":   dict(eye_open=1.00, low_lid=0.00, iris=1.00, brow_in=0,   brow_out=0,   arch=1.0, tilt=0.0,  mouth="neutral"),
    "happy":     dict(eye_open=0.96, low_lid=0.22, iris=1.00, brow_in=-4,  brow_out=-6,  arch=1.4, tilt=0.0,  mouth="grin"),
    "serious":   dict(eye_open=0.82, low_lid=0.00, iris=0.96, brow_in=8,   brow_out=-2,  arch=0.4, tilt=0.06, mouth="flat"),
    "angry":     dict(eye_open=0.70, low_lid=0.05, iris=0.90, brow_in=16,  brow_out=-8,  arch=0.1, tilt=0.16, mouth="grit"),
    "surprised": dict(eye_open=1.28, low_lid=0.00, iris=0.78, brow_in=-14, brow_out=-12, arch=1.3, tilt=0.0,  mouth="o"),
    "sad":       dict(eye_open=0.82, low_lid=0.06, iris=1.00, brow_in=-9,  brow_out=6,   arch=0.7, tilt=-0.1, mouth="frown"),
}


# =============================================================================
#  Resolved render context (colours + rig of key points)
# =============================================================================
class Ctx(object):
    def __init__(self, spec, expression):
        self.spec = spec
        self.ex = EXPR[expression]
        b = spec.get("build", {})
        self.shoulder = 178.0 * b.get("shoulder", 1.0)     # half width at shoulder caps
        self.waist = 140.0 * b.get("waist", 1.0)
        self.hip = 134.0 * b.get("hip", 1.0)
        self.neck = 31.0 * b.get("neck", 1.0)               # half width
        self.arm = b.get("arm", 1.0)                        # sleeve thickness scale
        self.leg = b.get("leg", 1.0)                        # trouser width scale
        self.head = b.get("head", 1.0)
        self.hrx, self.hry = HEAD_RX * self.head, HEAD_RY * self.head
        self.hcy = HEAD_CY
        face = spec.get("face", {})
        self.jaw = face.get("jaw", 1.0)
        self.chin_w = 24.0 * face.get("chin", 1.0)

        self.skin = col(spec["skin"])
        self.skin_sh = col(spec.get("skin_shadow", shade(self.skin, 0.82)))
        self.line = col(spec.get("line", "#17131a"))
        self.skin_line = col(spec.get("skin_line", "#5a3630"))
        hair = spec["hair"]
        self.hair = hair
        self.hair_c = col(hair["color"])
        self.hair_sh = col(hair.get("shadow", shade(self.hair_c, 0.78)))
        self.hair_line = col(hair.get("line", "#3a2028"))
        self.hair_hi = col(hair.get("highlight", shade(self.hair_c, 1.12)))
        eyes = spec.get("eyes", {})
        self.eyes = eyes
        self.iris = col(eyes.get("iris", "#7a4a2a"))
        self.iris_dk = col(eyes.get("iris_dark", shade(self.iris, 0.55)))
        self.eye_white = col(eyes.get("white", "#f7f6f8"))
        self.brow_c = col(eyes.get("brow", self.hair_line))
        o = spec.get("outfit", {})
        self.outfit = o
        self.jac = col(o.get("jacket", "#232636"))
        self.jac_sh = col(o.get("jacket_shadow", shade(self.jac, 0.70)))
        self.jac_hi = col(o.get("jacket_light", shade(self.jac, 1.35)))
        self.hood_c = col(o.get("hoodie", "#b8303a")) if o.get("hoodie") else None
        self.hood_sh = col(o.get("hoodie_shadow", shade(self.hood_c, 0.70))) if self.hood_c else None
        self.tro = col(o.get("trousers", "#1c1f2b"))
        self.tro_sh = col(o.get("trousers_shadow", shade(self.tro, 0.70)))
        self.shoe = col(o.get("shoes", "#f3f3f1"))
        self.sole = col(o.get("sole", "#e2e0da"))
        self.shoe_acc = col(o.get("shoe_accent", "#c2323f"))
        self.pose = spec.get("pose", {})
        if isinstance(self.pose, str):
            self.pose = {"arms": self.pose}

        # ---- rig: key points shared by parts (1x) ----
        sh = self.shoulder
        self.rig = {}
        for s in (-1, 1):
            self.rig[("shoulder", s)] = (CX + s * sh * 0.80, SHOULDER_Y + 44)
            self.rig[("elbow", s)] = (CX + s * sh * 1.06, SHOULDER_Y + 250)
            self.rig[("wrist", s)] = (CX + s * sh * 0.99, SHOULDER_Y + 452)
            self.rig[("leg_cx", s)] = CX + s * self.hip * 0.60


# =============================================================================
#  Parts.  Each takes (canvas, ctx) and paints; render_character() calls them
#  back-to-front.  Light comes from the upper-LEFT; shadow tones sit on the
#  viewer's right and under overhangs.
# =============================================================================

# ----------------------------------------------------------------- head/face
def head_poly(c):
    rx, ry, cy = c.hrx, c.hry, c.hcy
    jaw = c.jaw
    chin = c.chin_w
    jx = CX - rx * (0.72 + 0.10 * jaw)          # jaw corner x
    jy = cy + ry * 0.78                          # jaw corner y
    p = Path((CX - rx, cy + 8))
    p.C((CX - rx - 1, cy + ry * 0.42), (jx - 6 * jaw, jy - 20), (jx, jy), 12)             # cheek
    p.C((jx + 10, jy + 18), (CX - chin - 12, CHIN - 4), (CX, CHIN), 10)                    # to chin
    left = p.done()
    poly = symmetric(left, CX)
    # close over the top with the skull arc (right side -> left side)
    top = ellipse_pts(CX, cy, rx, ry, 40, math.radians(-5), math.radians(185))
    return poly + top[1:-1]


def draw_head(cv, c):
    sp = cv.part(cv.poly_spans(head_poly(c)), c.skin, c.skin_line, 3.0)
    c.head_spans = sp
    rx, cy = c.hrx, c.hcy
    # cel shadow: right side of the face (light from upper-left)
    cv.clipfill(sp, [[(CX + rx * 0.80, cy - 40), (CX + rx + 10, cy - 40), (CX + rx + 10, CHIN + 10),
                      (CX + 12, CHIN + 10), (CX + rx * 0.62, CHIN - 40), (CX + rx * 0.80, cy + 20)]], c.skin_sh)
    # shadow under the hairline
    cv.clipfill(sp, [[(CX - rx - 10, HAIRLINE_Y - 40), (CX + rx + 10, HAIRLINE_Y - 40),
                      (CX + rx + 10, HAIRLINE_Y + 6), (CX + 40, HAIRLINE_Y + 14), (CX - 30, HAIRLINE_Y + 10),
                      (CX - rx - 10, HAIRLINE_Y + 2)]], c.skin_sh)
    return sp


def draw_ears(cv, c):
    rx, cy = c.hrx, c.hcy
    for s in (-1, 1):
        ex, ey = CX + s * (rx + 1), EYE_Y + 6
        pts = ellipse_pts(ex, ey, 12, 19, 24)
        sp = cv.part(cv.poly_spans(pts), c.skin, c.skin_line, 2.4)
        if s > 0:
            cv.clipfill(sp, [[(ex - 20, ey - 30), (ex + 20, ey - 30), (ex + 20, ey + 30), (ex - 20, ey + 30)]], c.skin_sh)
        # inner ear curve
        cv.stroke([(ex + s * 4, ey - 9), (ex + s * 7, ey + 1), (ex + s * 1, ey + 9)], 1.8, c.skin_line, 0.85)


def draw_neck(cv, c):
    nw = c.neck
    top = CHIN - 34
    bot = SHOULDER_Y + 26
    poly = [(CX - nw, top), (CX + nw, top), (CX + nw * 1.18, bot), (CX - nw * 1.18, bot)]
    sp = cv.part(cv.poly_spans(poly), c.skin, c.skin_line, 2.8)
    # cel shadow under the chin + right side
    cv.clipfill(sp, [[(CX - nw - 6, top), (CX + nw + 6, top), (CX + nw + 6, CHIN + 30),
                      (CX + 4, CHIN + 26), (CX - nw * 0.5, CHIN + 20), (CX - nw - 6, CHIN + 6)]], c.skin_sh)
    cv.clipfill(sp, [[(CX + nw * 0.45, CHIN), (CX + nw * 1.4, CHIN), (CX + nw * 1.4, bot + 5), (CX + nw * 0.55, bot + 5)]],
                c.skin_sh)
    # tendon hint
    cv.stroke([(CX - nw * 0.45, CHIN + 26), (CX - nw * 0.62, SHOULDER_Y + 2)], (1.6, 0.8), c.skin_line, 0.45)


def draw_eyes(cv, c):
    ex_ = c.ex
    e = c.eyes
    size = e.get("size", 1.0)
    w = 50.0 * size                       # eye width
    h = 26.0 * size * ex_["eye_open"]     # height above the eye-line
    sep = e.get("spacing", 41.0)
    ey = EYE_Y
    tilt = ex_["tilt"]
    low = ex_["low_lid"]
    for s in (-1, 1):                     # s=-1 viewer-left eye; +s -> nose
        ex = CX + s * sep
        outer = (ex - s * w * 0.50, ey + 2 - tilt * 20)
        inner = (ex + s * w * 0.46, ey + 5 + tilt * 12)
        top = (ex - s * w * 0.05, ey - h)
        bottom_y = ey + 14 * size * (1.0 - low)
        # upper lid: flattened male lid, near-straight from the peak to the inner corner
        up = [outer] + qbez(outer, (ex - s * w * 0.42, ey - h * 1.02), top, 8) + \
             qbez(top, (ex + s * w * 0.30, ey - h * 0.90 + tilt * 10), inner, 8)
        lowc = qbez(inner, (ex + s * w * 0.04, bottom_y + 4), outer, 12)
        eye_poly = up + lowc
        esp = cv.poly_spans(eye_poly)
        cv.fill(esp, c.eye_white)
        # iris (clipped to the eye opening)
        ir = 15.5 * size * ex_["iris"]
        icx, icy = ex + s * 1.0, ey + 1
        iris_pts = ellipse_pts(icx, icy, ir, ir * 1.15, 28)
        iris_sp = spans_intersect(esp, cv.poly_spans(iris_pts))
        cv.fill(iris_sp, c.iris)
        # upper part of the iris darker (lid shadow) + rim
        cv.fill(spans_intersect(iris_sp, cv.poly_spans(
            [(icx - 30, icy - 40), (icx + 30, icy - 40), (icx + 30, icy - ir * 0.30), (icx - 30, icy - ir * 0.30)])),
            c.iris_dk)
        rim = spans_subtract(iris_sp, cv.poly_spans(ellipse_pts(icx, icy, ir * 0.84, ir * 1.15 * 0.84, 28)))
        cv.fill(rim, c.iris_dk)
        # pupil
        cv.fill(spans_intersect(esp, cv.poly_spans(ellipse_pts(icx, icy + 1, ir * 0.36, ir * 0.48, 20))), (18, 10, 12))
        # highlights (same side on both eyes, light from upper-left)
        cv.fill(spans_intersect(esp, cv.poly_spans(ellipse_pts(icx - ir * 0.40, icy - ir * 0.42, ir * 0.30, ir * 0.30, 16))), (255, 255, 255))
        cv.fill(spans_intersect(esp, cv.poly_spans(ellipse_pts(icx + ir * 0.38, icy + ir * 0.48, ir * 0.13, ir * 0.13, 12))), (255, 255, 255), 0.9)
        # eye-white shadow under the upper lid
        cv.fill(spans_intersect(esp, cv.poly_spans(
            [(ex - w, ey - h * 2), (ex + w, ey - h * 2), (ex + w, ey - h * 0.58), (ex - w, ey - h * 0.58)])),
            (150, 140, 160), 0.30)
        # upper lash line: thick, heaviest at the outer third
        ws = [3.2] + [4.4 + 2.2 * math.sin(math.pi * (i / 16.0) ** 0.8) for i in range(1, 16)] + [1.8]
        cv.stroke(up, ws, c.line)
        cv.stroke([outer, (outer[0] - s * 8, outer[1] - 5)], (4.0, 1.2), c.line)      # lash flick
        # lower lid: thin, outer 3/4
        cv.stroke(lowc[2:], (1.3, 2.4), c.line, 0.85)
        if low > 0.05:   # smiling squint: cheek pushes a bold lower line
            cv.stroke(lowc[1:], (2.0, 3.0), c.line, 0.9)
        # signature under-eye marks (Yuji): a short bold curve hugging the lower lid
        if e.get("bags"):
            by = bottom_y + 8
            cv.stroke([(ex - s * w * 0.42, by - 3), (ex - s * w * 0.20, by + 1), (ex + s * w * 0.06, by + 1.5),
                       (ex + s * w * 0.26, by - 1)], (2.4, 3.0, 3.0, 1.8), c.line, 0.95)
        draw_brow(cv, c, s, ex, ey - h - 9 * size)


def draw_brow(cv, c, s, ex, base_y):
    ex_ = c.ex
    e = c.eyes
    th = 10.0 * e.get("brow_thick", 1.0)
    length = 56.0
    arch = ex_["arch"]
    inner = (ex + s * length * 0.40, base_y + ex_["brow_in"])
    outer = (ex - s * length * 0.62, base_y + ex_["brow_out"] + 2)
    mid = vlerp(inner, outer, 0.45)
    top_c = (mid[0], mid[1] - 9 * arch)
    p = Path((inner[0], inner[1] - th * 0.45))
    p.Q((top_c[0], top_c[1] - th * 0.45), (outer[0], outer[1] - th * 0.10), 10)
    p.L((outer[0] - s * 2, outer[1] + th * 0.25))
    p.Q((top_c[0], top_c[1] + th * 0.55), (inner[0] + s * 3, inner[1] + th * 0.55), 10)
    cv.fill(cv.poly_spans(p.done()), c.brow_c)


def draw_nose_mouth(cv, c):
    m = c.ex["mouth"]
    ny = NOSE_Y
    # nose: short bracket on the shadow side + tiny shadow under the tip
    cv.stroke([(CX + 4, ny - 12), (CX + 9, ny), (CX + 3, ny + 4)], (1.4, 2.2, 1.6), c.skin_line, 0.9)
    cv.clipfill(c.head_spans, [[(CX - 5, ny - 2), (CX + 10, ny + 4), (CX - 1, ny + 7)]], c.skin_sh, 0.8)
    my = MOUTH_Y
    if m == "neutral":
        cv.stroke([(CX - 13, my - 1), (CX - 4, my + 2), (CX + 5, my + 2), (CX + 13, my - 1)], (1.6, 2.6, 2.6, 1.6), c.line)
    elif m == "flat":
        cv.stroke([(CX - 14, my), (CX + 14, my)], (2.2, 2.2), c.line)
    elif m == "frown":
        cv.stroke([(CX - 13, my + 4), (CX - 4, my - 1), (CX + 5, my - 1), (CX + 13, my + 4)], (1.6, 2.6, 2.6, 1.6), c.line)
    elif m == "grin":
        p = Path((CX - 26, my - 8)).Q((CX, my + 1), (CX + 26, my - 8), 10)
        p.Q((CX + 14, my + 24), (CX, my + 24), 8).Q((CX - 14, my + 24), (CX - 26, my - 8), 8)
        mp = p.done()
        sp = cv.poly_spans(mp)
        cv.fill(sp, (122, 40, 54))
        cv.fill(spans_intersect(sp, cv.poly_spans([(CX - 30, my - 12), (CX + 30, my - 12), (CX + 30, my + 5), (CX - 30, my + 5)])), (250, 248, 246))
        cv.stroke(mp, 2.2, c.line, closed=True)
        cv.stroke([(CX - 29, my - 14), (CX - 33, my - 5)], (2.2, 1.2), c.line, 0.8)   # cheek lift
        cv.stroke([(CX + 29, my - 14), (CX + 33, my - 5)], (2.2, 1.2), c.line, 0.8)
    elif m == "grit":
        mp = [(CX - 21, my - 7), (CX + 21, my - 7), (CX + 19, my + 8), (CX - 19, my + 8)]
        sp = cv.poly_spans(mp)
        cv.fill(sp, (250, 248, 246))
        cv.stroke(mp, 2.2, c.line, closed=True)
        cv.stroke([(CX - 19, my + 1), (CX + 19, my + 1)], 1.6, c.line)
        for x in (-11, -4, 4, 11):
            cv.stroke([(CX + x, my - 6), (CX + x, my + 7)], 1.1, c.line, 0.7)
    elif m == "o":
        mp = ellipse_pts(CX, my + 3, 8, 10, 20)
        cv.fill(cv.poly_spans(mp), (110, 36, 48))
        cv.stroke(mp, 2.0, c.line, closed=True)
    if m in ("neutral", "flat", "frown"):
        cv.stroke([(CX - 4, my + 9), (CX + 5, my + 9)], (1.2, 1.2), c.skin_line, 0.5)


# ----------------------------------------------------------------- hair
def spiked_top(cx, cy, Rx, Ry, a_left, a_right, n, base_len, lens, lean, up_bias, curl, tip_w=0.0):
    """Points along the top of a volume ellipse, replaced by `n` spikes (locks)
    between angles a_left..a_right (math angles, image space).  Each spike is
    two concave quadratic edges meeting at a tip.  Returns (points, valleys)."""
    pts = []
    bases = []
    for i in range(n + 1):
        a = a_left + (a_right - a_left) * i / float(n)
        bases.append((a, (cx + Rx * math.cos(a), cy - Ry * math.sin(a))))
    valleys = []
    for i in range(n):
        a0, b0 = bases[i]
        a1, b1 = bases[i + 1]
        am = 0.5 * (a0 + a1)
        L = base_len * lens[i % len(lens)]
        # direction: radial, biased upward (pushed up) with a global lean
        dx = math.cos(am) * (1.0 - up_bias) + lean
        dy = -math.sin(am) - up_bias * 0.8
        d = vnorm((dx, dy))
        mid = vlerp(b0, b1, 0.5)
        tip = (mid[0] + d[0] * L, mid[1] + d[1] * L)
        # concave edges: control point pulled toward the base midpoint
        c0 = vadd(vlerp(b0, tip, 0.45), vmul(vsub(mid, b0), curl))
        c1 = vadd(vlerp(tip, b1, 0.55), vmul(vsub(mid, b1), curl))
        if i == 0:
            pts.append(b0)
        pts += qbez(b0, c0, tip, 7)
        pts += qbez(tip, c1, b1, 7)
        valleys.append((b1, am, tip))
    return pts, valleys


def hair_undercut_spiky(cv, c):
    """Yuji-style: dark shaved sides/back (undercut) + a cap of hair on top
    swept up and back into spikes.  Spikes only span the crown (not the
    sides), a darker back layer peeks between them, short tufts at the
    hairline, lock lines swept upward.

    hair keys: color, shadow, highlight, line, undercut, spikes, spike_len,
    lean, up_bias, curl, spike_lens, fringe [(x_frac, drop, dir), ...]"""
    h = c.hair
    rx, ry, cy = c.hrx, c.hry, c.hcy
    under_c = col(h.get("undercut", "#3a2b2d"))
    under_hi = col(h.get("undercut_light", shade(under_c, 1.35)))
    HL = HAIRLINE_Y + h.get("hairline", 0)
    temple = (CX - rx * 0.70, HL + 12)                 # where the cap meets the temple

    # --- 1. undercut: shaved sides, seen at the temples/sideburns and as a
    #        dark rim around the skull silhouette ---------------------------
    left = [(CX, cy - ry - 9)]
    left += ellipse_pts(CX, cy, rx + 9, ry + 8, 20, math.radians(90), math.radians(182))[1:]
    p = Path(left[-1])
    p.Q((CX - rx - 10, cy + 30), (CX - rx - 3, cy + 46), 6)                       # down beside the ear
    p.Q((CX - rx + 4, cy + 58), (CX - rx + 14, cy + 52), 4)                        # sideburn tip
    p.Q((CX - rx + 14, cy + 20), (CX - rx * 0.78, cy - 4), 6)                      # front boundary
    p.Q((CX - rx * 0.76, HL + 10), temple, 4)
    p.Q((CX - rx * 0.55, HL - 20), (CX, HL - 30), 6)                              # hidden under the cap
    left = p.done()
    usp = cv.part(cv.poly_spans(symmetric(left, CX)), under_c, c.hair_line, 2.6)
    # shaved texture: short strokes following the skull
    for s in (-1, 1):
        for i in range(4):
            x = CX + s * (rx - 2 - i * 5)
            y0 = cy - 6 + i * 9
            cv.stroke([(x, y0), (x - s * 3, y0 + 26)], 1.2, under_hi, 0.45)

    # --- 2. back layer of locks (darker) --------------------------------------
    n = int(h.get("spikes", 7))
    base_len = float(h.get("spike_len", 46))
    lean = float(h.get("lean", 0.0))
    up_bias = float(h.get("up_bias", 0.35))
    curl = float(h.get("curl", 0.30))
    lens = h.get("spike_lens") or [0.80, 1.05, 1.25, 1.0, 1.2, 1.0, 0.85]
    Rx, Ry = rx + 12.0, ry + 12.0
    vcy = cy - 4
    a_l, a_r = math.radians(150), math.radians(30)
    back_pts, _ = spiked_top(CX + 3, vcy - 10, Rx - 4, Ry - 2, a_l + 0.16, a_r + 0.16, n,
                             base_len * 0.95, lens[1:] + lens[:1], lean, up_bias, curl)
    back = [(CX - rx - 4, cy - 10)] + back_pts + [(CX + rx + 4, cy - 10)]
    cv.part(cv.poly_spans(back), c.hair_sh, c.hair_line, 3.0)

    # --- 3. main cap with spikes across the crown ----------------------------
    top_pts, valleys = spiked_top(CX, vcy, Rx, Ry, a_l, a_r, n, base_len, lens, lean, up_bias, curl)
    poly = [(CX - rx - 9, cy - 14)]
    poly += ellipse_pts(CX, vcy, Rx, Ry, 6, math.radians(172), a_l)[:-1]
    poly += top_pts
    poly += ellipse_pts(CX, vcy, Rx, Ry, 6, a_r, math.radians(8))[1:]
    poly.append((CX + rx + 9, cy - 14))
    # lower edge (hairline) right temple -> tufts -> left temple
    fr = h.get("fringe") or [(0.62, 12, 1), (0.30, 24, 1), (-0.02, 18, -1), (-0.34, 26, -1), (-0.60, 12, -1)]
    p = Path(poly[-1])
    p.Q((CX + rx * 0.86, HL + 30), (CX + rx * 0.70, HL + 12), 6)                 # right temple point
    p.Q((CX + rx * 0.72, HL - 6), (CX + rx * 0.66, HL - 2), 3)
    prev = (CX + rx * 0.66, HL - 2)
    for (tx, drop, d) in fr:
        bx = CX + rx * tx
        tip = (bx + d * 6, HL + drop)
        nxt = (bx - rx * 0.13, HL - 2)
        p.Q((prev[0] - 4, HL + drop * 0.55), tip, 6)
        p.Q((bx - rx * 0.10, HL + drop * 0.35), nxt, 6)
        prev = nxt
    p.Q((CX - rx * 0.72, HL - 6), (CX - rx * 0.70, HL + 12), 4)                  # left temple point
    p.Q((CX - rx * 0.86, HL + 30), poly[0], 6)
    poly += p.done()[1:-1]
    hsp = cv.part(cv.poly_spans(poly), c.hair_c, c.hair_line, 3.0)
    c.hair_spans = hsp

    # cel shading on the cap ---------------------------------------------------
    # band above the hairline (the fringe overhangs the forehead)
    band = [(CX - rx - 20, HL + 40), (CX - rx - 20, HL - 6), (CX - rx * 0.5, HL - 16), (CX, HL - 6),
            (CX + rx * 0.5, HL - 18), (CX + rx + 20, HL - 8), (CX + rx + 20, HL + 40)]
    cv.clipfill(hsp, [band], c.hair_sh)
    # right side of the cap in shadow
    cv.clipfill(hsp, [[(CX + rx * 0.72, cy - ry - 80), (CX + rx + 40, cy - ry - 80), (CX + rx + 40, cy + 40),
                       (CX + rx * 0.72, cy + 40), (CX + rx * 0.58, cy - ry * 0.6)]], c.hair_sh, 0.9)
    # undersides of the spikes (the edge facing right/down)
    for (v, am, tip) in valleys:
        d = vnorm(vsub(tip, v))
        cv.clipfill(hsp, [[v, (tip[0] + 1, tip[1] + 1), (tip[0] + 12, tip[1] + 14), (v[0] + 10, v[1] + 10)]], c.hair_sh, 0.9)
    # angular highlight band across the upper cap
    zig = []
    x0, x1 = CX - rx * 0.62, CX + rx * 0.40
    yb = cy - ry * 0.62
    k = 6
    for i in range(k + 1):
        x = x0 + (x1 - x0) * i / k
        zig.append((x, yb - (8 if i % 2 else 0) + (x - CX) * 0.08))
    for i in range(k, -1, -1):
        x = x0 + (x1 - x0) * i / k
        zig.append((x, yb + 10 + (0 if i % 2 else 8) + (x - CX) * 0.08))
    cv.clipfill(hsp, [zig], c.hair_hi, 0.75)
    # lock lines swept up from the hairline toward the tips
    for (v, am, tip) in valleys[:-1]:
        d = vnorm(vsub(tip, v))
        inner = (v[0] - d[0] * 30, v[1] - d[1] * 30 + 4)
        cv.stroke([v, inner], (2.8, 0.6), c.hair_line, 0.85)
    for i in range(1, len(valleys) - 1):
        v, am, tip = valleys[i]
        base = (v[0] * 0.5 + CX * 0.5, HL + 2)
        mid = vlerp(base, v, 0.5)
        cv.stroke([base, (mid[0] + 4, mid[1]), (v[0] - 4, v[1] - 6)], (1.0, 2.2, 0.6), c.hair_line, 0.55)

    # --- 4. forelocks laid over the hairline (their own outline layers them) --
    for (tx, drop, d) in fr:
        bx = CX + rx * tx
        lp = Path((bx + 16, HL - 18)).Q((bx + 12, HL + drop * 0.45), (bx + d * 5, HL + drop + 6), 6)
        lp.Q((bx - 6, HL + drop * 0.4), (bx - 14, HL - 16), 6)
        lsp = cv.part(cv.poly_spans(lp.done()), c.hair_c, c.hair_line, 2.2)
        cv.clipfill(lsp, [[(bx - 30, HL + 2), (bx + 30, HL + 2), (bx + 30, HL + 60), (bx - 30, HL + 60)]], c.hair_sh)


HAIR_STYLES = {"undercut_spiky": hair_undercut_spiky}


# ----------------------------------------------------------------- body
def torso_poly(c):
    sh, nw, wa, hip = c.shoulder, c.neck, c.waist, c.hip
    p = Path((CX, SHOULDER_Y - 4))
    p.L((CX - nw * 1.45, SHOULDER_Y - 4))
    p.Q((CX - sh * 0.60, SHOULDER_Y + 2), (CX - sh * 0.93, SHOULDER_Y + 26), 8)          # trapezius slope
    p.C((CX - sh * 1.05, SHOULDER_Y + 40), (CX - sh * 1.04, SHOULDER_Y + 78), (CX - sh * 0.95, CHEST_Y + 8), 8)  # deltoid
    p.C((CX - sh * 0.90, CHEST_Y + 90), (CX - wa * 1.0, WAIST_Y - 70), (CX - wa, WAIST_Y), 8)
    p.C((CX - wa, WAIST_Y + 70), (CX - hip * 1.0, HIP_Y - 30), (CX - hip * 1.02, HEM_Y), 8)
    p.Q((CX - hip * 0.5, HEM_Y + 10), (CX, HEM_Y + 8), 6)
    return symmetric(p.done(), CX)


def draw_torso(cv, c):
    sp = cv.part(cv.poly_spans(torso_poly(c)), c.jac, c.line, 3.0)
    c.torso_spans = sp
    sh, wa, hip, nw = c.shoulder, c.waist, c.hip, c.neck
    # shadow: viewer-right side + under the arm + hem band
    cv.clipfill(sp, [[(CX + sh * 0.62, SHOULDER_Y + 20), (CX + sh * 1.2, SHOULDER_Y + 20), (CX + sh * 1.2, HEM_Y + 20),
                      (CX + hip * 0.70, HEM_Y + 20), (CX + wa * 0.68, WAIST_Y), (CX + sh * 0.70, CHEST_Y)]], c.jac_sh)
    cv.clipfill(sp, [[(CX - sh, HEM_Y - 26), (CX + sh, HEM_Y - 26), (CX + sh, HEM_Y + 20), (CX - sh, HEM_Y + 20)]], c.jac_sh)
    o = c.outfit
    if c.hood_c and o.get("open", True):
        # hoodie showing through the open jacket front
        x0, x1 = nw * 1.42, hip * 0.46
        strip = [(CX - x0, SHOULDER_Y - 10), (CX + x0, SHOULDER_Y - 10), (CX + x1, HEM_Y + 12), (CX - x1, HEM_Y + 12)]
        ssp = spans_intersect(sp, cv.poly_spans(strip))
        cv.part(ssp, c.hood_c, c.line, 2.6)
        cv.clipfill(ssp, [[(CX + 8, SHOULDER_Y - 10), (CX + x1 + 10, SHOULDER_Y - 10), (CX + x1 + 10, HEM_Y + 20), (CX + 12, HEM_Y + 20)]], c.hood_sh)
        # kangaroo pocket + a fold
        cv.stroke([(CX - x1 * 0.9, HIP_Y - 40), (CX + x1 * 0.9, HIP_Y - 44)], 2.0, c.hood_sh, 0.9)
        cv.stroke([(CX - 10, CHEST_Y + 60), (CX - 4, WAIST_Y - 30)], (1.8, 0.6), c.hood_sh, 0.7)
        # jacket panel edges: light seam line so the open front reads on dark cloth
        for s in (-1, 1):
            cv.stroke([(CX + s * (x0 + 5), SHOULDER_Y - 8), (CX + s * (x1 + 5), HEM_Y + 8)], 2.2, c.jac_hi, 0.75)
            cv.stroke([(CX + s * (x0 + 16), SHOULDER_Y + 40), (CX + s * (x1 + 16), HEM_Y - 30)], (1.6, 0.8), c.jac_sh, 0.9)
    else:
        cv.stroke([(CX, SHOULDER_Y + 44), (CX, HEM_Y + 8)], 2.0, c.jac_hi, 0.6)
        for k in range(5):
            cv.dot((CX + 2, SHOULDER_Y + 70 + k * 72), 3.4, c.line)
    # jacket hem highlight line + side seams
    cv.stroke([(CX - hip * 0.98, HEM_Y - 2), (CX, HEM_Y + 4), (CX + hip * 0.98, HEM_Y - 2)], 1.6, c.jac_hi, 0.35)


def draw_hood(cv, c):
    """The red hood bunched behind the neck, lying over the shoulders."""
    if not (c.hood_c and c.outfit.get("hood", True)):
        return
    nw, sh = c.neck, c.shoulder
    top = CHIN - 10
    p = Path((CX - sh * 0.60, SHOULDER_Y + 34))
    p.C((CX - sh * 0.70, SHOULDER_Y - 30), (CX - nw * 2.9, top + 10), (CX - nw * 1.2, top), 12)
    p.Q((CX, top - 12), (CX + nw * 1.2, top), 8)
    p.C((CX + nw * 2.9, top + 10), (CX + sh * 0.70, SHOULDER_Y - 30), (CX + sh * 0.60, SHOULDER_Y + 34), 12)
    p.Q((CX, SHOULDER_Y + 56), (CX - sh * 0.60, SHOULDER_Y + 34), 10)
    hsp = cv.part(cv.poly_spans(p.done()), c.hood_c, c.line, 3.0)
    cv.clipfill(hsp, [[(CX - sh, SHOULDER_Y - 6), (CX + sh, SHOULDER_Y - 6), (CX + sh, SHOULDER_Y + 80), (CX - sh, SHOULDER_Y + 80)]], c.hood_sh)
    cv.clipfill(hsp, [[(CX + nw * 0.8, top - 30), (CX + sh, top - 30), (CX + sh, SHOULDER_Y + 80), (CX + nw * 1.4, SHOULDER_Y + 80)]], c.hood_sh, 0.6)
    for s in (-1, 1):
        cv.stroke([(CX + s * nw * 1.6, top + 6), (CX + s * nw * 2.4, SHOULDER_Y - 10)], (2.4, 1.0), c.line, 0.7)
        cv.stroke([(CX + s * nw * 3.2, SHOULDER_Y - 18), (CX + s * sh * 0.52, SHOULDER_Y + 22)], (2.0, 0.8), c.line, 0.6)


def draw_neckline_and_collar(cv, c):
    """Hoodie crew neck (in front of the neck) + jacket stand-collar flaps."""
    nw, sh = c.neck, c.shoulder
    ny = SHOULDER_Y + 4
    if c.hood_c:
        p = Path((CX - nw * 1.36, ny - 16)).Q((CX, ny + 24), (CX + nw * 1.36, ny - 16), 12)
        p.L((CX + nw * 1.50, ny - 2)).Q((CX, ny + 44), (CX - nw * 1.50, ny - 2), 12)
        cv.part(cv.poly_spans(p.done()), c.hood_sh, c.line, 2.4)
        for s in (-1, 1):   # drawstrings
            cv.stroke([(CX + s * 11, ny + 24), (CX + s * 15, ny + 78)], 2.4, (236, 232, 226))
            cv.dot((CX + s * 15, ny + 80), 2.8, c.line, 0.9)
    # stand collar: two flaps either side of the neck, opening outward
    for s in (-1, 1):
        p = Path((CX + s * nw * 1.10, ny - 44))
        p.Q((CX + s * nw * 2.0, ny - 50), (CX + s * sh * 0.46, ny - 26), 8)
        p.L((CX + s * sh * 0.55, ny + 6))
        p.Q((CX + s * sh * 0.30, ny + 28), (CX + s * nw * 1.55, ny + 30), 8)
        csp = cv.part(cv.poly_spans(p.done()), c.jac, c.line, 2.8)
        cv.clipfill(csp, [[(CX + s * nw * 1.1, ny - 50), (CX + s * sh * 0.5, ny - 40), (CX + s * sh * 0.5, ny - 24), (CX + s * nw * 1.1, ny - 30)]],
                    c.jac_hi, 0.55)


def draw_arms(cv, c):
    t = 30.0 * c.arm                       # half thickness at the shoulder
    for s in (-1, 1):
        P0 = c.rig[("shoulder", s)]
        P1 = c.rig[("elbow", s)]
        P2 = c.rig[("wrist", s)]
        # smooth centre line through shoulder -> elbow -> wrist
        pts = [P0] + qbez(P0, (P0[0] + s * 10, P0[1] + 100), P1, 8) + qbez(P1, (P1[0] - s * 2, P1[1] + 110), P2, 8)
        n = len(pts)
        ws = []
        for i in range(n):
            u = i / (n - 1.0)
            ws.append(2 * (t * (1.0 - u) + t * 0.66 * u) if u < 0.5 else 2 * (t * 0.83 * (1 - (u - 0.5) * 2) + t * 0.62 * (u - 0.5) * 2))
        poly = ribbon(pts, ws, True, False)
        sp = cv.part(cv.poly_spans(poly), c.jac, c.line, 3.0)
        # inner (torso-facing) shadow + forearm underside
        cv.clipfill(sp, [[(P0[0] - s * t * 1.2, P0[1] - 40), (P0[0] - s * t * 0.15, P0[1] - 40),
                          (P1[0] - s * t * 0.1, P1[1]), (P2[0] - s * t * 0.05, P2[1] + 10), (P2[0] - s * t * 1.2, P2[1] + 10)]], c.jac_sh)
        if s > 0:
            cv.clipfill(sp, [[(P0[0] + s * t * 0.5, P0[1] + 30), (P0[0] + s * t * 1.3, P0[1] + 30),
                              (P2[0] + s * t * 1.3, P2[1] + 10), (P2[0] + s * t * 0.4, P2[1] + 10)]], c.jac_sh)
        # shoulder seam, elbow folds, cuff
        cv.stroke([(P0[0] - s * t * 0.9, P0[1] - 2), (P0[0] + s * t * 0.95, P0[1] + 12)], (1.4, 1.4), c.line, 0.45)
        cv.stroke([(P1[0] - s * t * 0.55, P1[1] + 8), (P1[0] + s * t * 0.25, P1[1] + 18)], (2.0, 0.8), c.line, 0.6)
        cv.stroke([(P1[0] - s * t * 0.45, P1[1] + 30), (P1[0] + s * t * 0.15, P1[1] + 36)], (1.6, 0.6), c.line, 0.45)
        cv.stroke([(P2[0] - s * t * 0.62, P2[1] - 18), (P2[0] + s * t * 0.62, P2[1] - 16)], 1.8, c.line, 0.6)
        draw_hand(cv, c, s, P2)


def draw_hand(cv, c, s, wrist):
    hw = 21.0 * c.arm
    top = wrist[1] - 4
    x = wrist[0]
    p = Path((x - s * hw * 0.85, top))
    p.L((x + s * hw * 0.95, top))
    p.C((x + s * hw * 1.15, top + 30), (x + s * hw * 1.05, top + 66), (x + s * hw * 0.62, top + 82), 8)   # outer edge
    p.Q((x + s * hw * 0.1, top + 90), (x - s * hw * 0.55, top + 82), 6)                                # knuckles
    p.Q((x - s * hw * 0.95, top + 74), (x - s * hw * 0.98, top + 56), 6)                               # inner edge
    p.Q((x - s * hw * 1.55, top + 42), (x - s * hw * 1.25, top + 22), 6)                               # thumb
    p.Q((x - s * hw * 1.05, top + 8), (x - s * hw * 0.85, top), 4)
    sp = cv.part(cv.poly_spans(p.done()), c.skin, c.skin_line, 2.6)
    cv.clipfill(sp, [[(x - s * hw * 2, top + 58), (x + s * hw * 2, top + 58), (x + s * hw * 2, top + 100), (x - s * hw * 2, top + 100)]], c.skin_sh)
    if s > 0:
        cv.clipfill(sp, [[(x + s * hw * 0.55, top - 5), (x + s * hw * 2, top - 5), (x + s * hw * 2, top + 100), (x + s * hw * 0.55, top + 100)]], c.skin_sh)
    # finger separations + thumb crease
    for k in range(3):
        fx = x + s * hw * (0.62 - k * 0.36)
        cv.stroke([(fx, top + 58 + k * 1.5), (fx - s * 2, top + 84 - k * 2)], (1.8, 1.0), c.skin_line, 0.8)
    cv.stroke([(x - s * hw * 1.2, top + 24), (x - s * hw * 0.75, top + 44)], (1.8, 0.8), c.skin_line, 0.65)


def draw_legs(cv, c):
    hip = c.hip
    tw = 52.0 * c.leg      # half width at the thigh
    kw = 42.0 * c.leg      # knee
    aw = 37.0 * c.leg      # ankle / hem
    for s in (-1, 1):
        xc = c.rig[("leg_cx", s)]
        p = Path((CX + s * hip * 1.0, HIP_Y - 40))
        p.C((CX + s * (hip + 4), KNEE_Y - 170), (xc + s * (tw - 6), KNEE_Y - 50), (xc + s * kw, KNEE_Y), 8)
        p.C((xc + s * (kw - 2), KNEE_Y + 80), (xc + s * aw, ANKLE_Y - 70), (xc + s * aw, ANKLE_Y + 8), 8)
        p.Q((xc, ANKLE_Y + 16), (xc - s * aw, ANKLE_Y + 8), 6)                     # hem sag
        p.C((xc - s * (aw + 1), ANKLE_Y - 70), (xc - s * (kw - 1), KNEE_Y + 80), (xc - s * kw, KNEE_Y), 8)
        p.C((xc - s * (kw + 2), KNEE_Y - 70), (CX + s * 12, CROTCH_Y + 50), (CX + s * 3, CROTCH_Y), 8)
        p.L((CX + s * 3, HIP_Y - 40))
        sp = cv.part(cv.poly_spans(p.done()), c.tro, c.line, 3.0)
        # shadow: inner side of each leg + under the jacket hem
        cv.clipfill(sp, [[(CX + s * 2, CROTCH_Y - 10), (CX + s * 32, CROTCH_Y + 20), (xc - s * 8, ANKLE_Y + 20), (CX - s * 6, ANKLE_Y + 20)]], c.tro_sh)
        cv.clipfill(sp, [[(CX - 200, HEM_Y - 10), (CX + 200, HEM_Y - 10), (CX + 200, HEM_Y + 40), (CX - 200, HEM_Y + 40)]], c.tro_sh)
        if s > 0:
            cv.clipfill(sp, [[(xc + s * kw * 0.45, HEM_Y), (xc + s * 80, HEM_Y), (xc + s * 80, ANKLE_Y + 20), (xc + s * aw * 0.55, ANKLE_Y + 20)]], c.tro_sh, 0.8)
        # crease + knee folds + hem line
        cv.stroke([(xc + s * 6, HEM_Y + 30), (xc + s * 2, KNEE_Y - 30)], (1.8, 0.8), c.tro_sh, 1.0)
        cv.stroke([(xc - s * 22, KNEE_Y + 6), (xc + s * 10, KNEE_Y + 10)], (2.0, 0.8), c.line, 0.5)
        cv.stroke([(xc - s * 16, KNEE_Y + 26), (xc + s * 6, KNEE_Y + 32)], (1.6, 0.6), c.line, 0.4)
        cv.stroke([(xc - s * aw * 0.9, ANKLE_Y - 14), (xc + s * aw * 0.9, ANKLE_Y - 18)], (1.4, 1.4), c.line, 0.35)


def draw_shoes(cv, c):
    top = ANKLE_Y - 10
    bot = FEET_Y
    for s in (-1, 1):
        xs = c.rig[("leg_cx", s)] + s * 8
        p = Path((xs - s * 36, top)).L((xs + s * 36, top))
        p.C((xs + s * 56, top + 12), (xs + s * 62, bot - 16), (xs + s * 44, bot), 8)      # outer toe
        p.L((xs - s * 40, bot))
        p.C((xs - s * 54, bot - 8), (xs - s * 50, top + 18), (xs - s * 36, top), 8)      # inner heel
        sp = cv.part(cv.poly_spans(p.done()), c.shoe, c.line, 3.0)
        # sole band
        cv.clipfill(sp, [[(xs - 80, bot - 12), (xs + 80, bot - 12), (xs + 80, bot + 4), (xs - 80, bot + 4)]], c.sole)
        cv.stroke([(xs - s * 52, bot - 12), (xs + s * 58, bot - 13)], 1.8, c.line, 0.75)
        # tongue / laces
        cv.clipfill(sp, [[(xs - s * 16, top - 2), (xs + s * 18, top - 2), (xs + s * 22, top + 34), (xs - s * 20, top + 34)]], shade(c.shoe, 0.9))
        for k in range(3):
            y = top + 8 + k * 9
            cv.stroke([(xs - s * 12, y), (xs + s * 14, y + 2)], 1.4, c.line, 0.55)
        # accent stripe along the side
        cv.clipfill(sp, [[(xs - s * 30, top + 24), (xs + s * 36, top + 28), (xs + s * 40, top + 38), (xs - s * 32, top + 34)]], c.shoe_acc)
        cv.clipfill(sp, [[(xs + s * 20, top + 4), (xs + s * 60, top + 20), (xs + s * 60, bot - 12), (xs + s * 30, bot - 12)]], shade(c.shoe, 0.88), 0.7)


# =============================================================================
#  Character assembly
# =============================================================================
def render_character(spec, expression="neutral", ss=2):
    """Render one character to a raster.Img (760x1400 RGBA)."""
    if expression not in EXPR:
        raise ValueError("unknown expression %r (want one of %s)" % (expression, ", ".join(EXPRESSIONS)))
    c = Ctx(spec, expression)
    cv = Canvas(W, H, ss)
    b = spec.get("build", {})
    cv.set_transform(sx=b.get("width", 1.0), sy=b.get("height", 1.0))

    # back to front
    draw_shoes(cv, c)
    draw_legs(cv, c)
    draw_torso(cv, c)
    draw_hood(cv, c)
    draw_arms(cv, c)
    draw_neck(cv, c)
    draw_neckline_and_collar(cv, c)
    draw_head(cv, c)
    draw_eyes(cv, c)
    draw_nose_mouth(cv, c)
    HAIR_STYLES[c.hair.get("style", "undercut_spiky")](cv, c)
    draw_ears(cv, c)
    return cv.downsample()


# =============================================================================
#  Cast specs (data only)
# =============================================================================
YUJI = {
    "name": "yuji",
    "skin": "#f3cda9", "skin_shadow": "#dba884", "skin_line": "#5a3129",
    "line": "#17131a",
    "face": {"jaw": 1.0, "chin": 1.0},
    "hair": {
        "style": "undercut_spiky",
        "color": "#f0a0a4", "shadow": "#cf6f7c", "highlight": "#f9c4c2", "line": "#4a2430",
        "undercut": "#3b2b2e", "undercut_light": "#54403f",
        "spikes": 7, "spike_len": 48, "lean": 0.0, "up_bias": 0.35, "curl": 0.30,
        "fringe": [(0.62, 12, 1), (0.30, 24, 1), (-0.02, 18, -1), (-0.34, 26, -1), (-0.60, 12, -1)],
    },
    "eyes": {"iris": "#8a5a2c", "iris_dark": "#4e2e14", "size": 1.0, "spacing": 41,
             "bags": True, "brow": "#33221f", "brow_thick": 1.15},
    "build": {"shoulder": 1.0, "waist": 1.0, "hip": 1.0, "arm": 1.0, "leg": 1.0, "neck": 1.05, "head": 1.0,
              "height": 1.0, "width": 1.0},
    "outfit": {
        "jacket": "#232838", "jacket_shadow": "#171a27", "jacket_light": "#3a4056", "open": True,
        "hoodie": "#c22b34", "hoodie_shadow": "#851c25", "hood": True,
        "trousers": "#1e2232", "trousers_shadow": "#12151f",
        "shoes": "#f4f3f0", "shoe_accent": "#c9323f", "sole": "#dedbd4",
    },
    "pose": {"arms": "relaxed", "hands": "relaxed"},
}

CAST = {"yuji": YUJI}


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(TOOLS), "game", "images", "char")
    os.makedirs(out_dir, exist_ok=True)
    jobs = [("neutral", "_test_yuji_C.png"), ("happy", "_test_yuji_C_happy.png")]
    if len(sys.argv) > 1:
        jobs = [(a, "_test_yuji_C_%s.png" % a) for a in sys.argv[1:]]
    for expr, fn in jobs:
        t0 = time.time()
        im = render_character(YUJI, expr)
        path = os.path.join(out_dir, fn)
        im.save(path)
        print("%-28s %5.1fs" % (path, time.time() - t0))
