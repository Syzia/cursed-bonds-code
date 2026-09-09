"""anime_A.py - Approach A: vector-path cel-shaded anime character renderer.

Pure Python (no Pillow/numpy). Builds on tools/raster.py (Img + PNG writer) and
adds a small vector engine:

  Path        - move/line/curve(cubic)/close, flatten() to polylines, transforms
  smooth()    - Catmull-Rom style smooth closed/open path through control points;
                a point may be tagged 'c' for a sharp corner (hair tips etc.)
  coverage()  - anti-aliased scanline rasteriser (non-zero winding, vertical
                supersampling + exact horizontal span coverage) -> Mask
  Canvas      - fill(path) / stroke(path, width profile) / clip masks

Everything on the character (hair locks, face, eyes, uniform, hands, shoes) is a
filled path + a dark outline stroke, with one flat shadow tone per region
clipped to that region's mask (cel shading).

Public API:
  render_character(spec: dict, expression: str) -> raster.Img (760x1400 RGBA)
  EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")
  YUJI - example spec dict.
"""
import sys, os, math

_TOOLS = os.path.dirname(os.path.abspath(__file__))
for _p in (_TOOLS, "/Users/hunterjolly/Desktop/JJKgame.md/tools"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from raster import Img, hexc, lerp  # noqa: E402

W, H = 760, 1400
SUB = 4          # vertical sub-scanlines per pixel (AA quality vs speed)
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")


# =============================================================================
# geometry helpers
# =============================================================================
def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _bezier_pts(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / float(n)
        mt = 1.0 - t
        a = mt * mt * mt
        b = 3.0 * mt * mt * t
        c = 3.0 * mt * t * t
        d = t * t * t
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


class Path(object):
    """A list of sub-paths made of line / cubic-bezier segments."""

    def __init__(self):
        self.subs = []   # [start(x,y), segs, closed]

    def move(self, x, y):
        self.subs.append([(float(x), float(y)), [], False])
        return self

    def line(self, x, y):
        self.subs[-1][1].append(('L', (float(x), float(y))))
        return self

    def curve(self, x1, y1, x2, y2, x, y):
        self.subs[-1][1].append(('C', (x1, y1), (x2, y2), (float(x), float(y))))
        return self

    def close(self):
        if self.subs:
            self.subs[-1][2] = True
        return self

    def add(self, other):
        self.subs.extend(other.subs)
        return self

    def flatten(self, quality=3.0):
        polys = []
        for start, segs, closed in self.subs:
            pts = [start]
            cur = start
            for s in segs:
                if s[0] == 'L':
                    pts.append(s[1])
                    cur = s[1]
                else:
                    p1, p2, p3 = s[1], s[2], s[3]
                    L = _dist(cur, p1) + _dist(p1, p2) + _dist(p2, p3)
                    n = max(3, min(60, int(L / quality) + 1))
                    pts.extend(_bezier_pts(cur, p1, p2, p3, n))
                    cur = p3
            # drop duplicate consecutive points
            clean = [pts[0]]
            for p in pts[1:]:
                if abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6:
                    clean.append(p)
            if closed and len(clean) > 2 and _dist(clean[0], clean[-1]) < 1e-6:
                clean.pop()
            polys.append((clean, closed))
        return polys

    def transform(self, fn):
        out = Path()
        for start, segs, closed in self.subs:
            ns = []
            for s in segs:
                if s[0] == 'L':
                    ns.append(('L', fn(*s[1])))
                else:
                    ns.append(('C', fn(*s[1]), fn(*s[2]), fn(*s[3])))
            out.subs.append([fn(*start), ns, closed])
        return out

    def mirror(self, cx=W / 2.0):
        return self.transform(lambda x, y: (2 * cx - x, y))

    def translate(self, dx, dy):
        return self.transform(lambda x, y: (x + dx, y + dy))

    def scale(self, sx, sy=None, ox=0.0, oy=0.0):
        if sy is None:
            sy = sx
        return self.transform(lambda x, y: (ox + (x - ox) * sx, oy + (y - oy) * sy))

    def bbox(self):
        xs, ys = [], []
        for pts, _ in self.flatten(6.0):
            for p in pts:
                xs.append(p[0]); ys.append(p[1])
        return min(xs), min(ys), max(xs), max(ys)


def smooth(pts, closed=True, tension=1.0):
    """Smooth path through points. Point = (x, y) or (x, y, 'c') for a corner.

    Smooth points get a Catmull-Rom tangent; corner points use one-sided
    tangents so the outline comes to a sharp tip (hair spikes, eye corners).
    """
    P = [(float(p[0]), float(p[1])) for p in pts]
    corner = [len(p) > 2 and p[2] == 'c' for p in pts]
    n = len(P)
    if n < 2:
        raise ValueError("need >= 2 points")

    def tan_out(i):
        j = (i + 1) % n
        if corner[i]:
            return ((P[j][0] - P[i][0]) * tension, (P[j][1] - P[i][1]) * tension)
        if not closed and i == 0:
            return ((P[1][0] - P[0][0]) * tension, (P[1][1] - P[0][1]) * tension)
        k = (i - 1) % n
        return ((P[j][0] - P[k][0]) * 0.5 * tension, (P[j][1] - P[k][1]) * 0.5 * tension)

    def tan_in(i):
        k = (i - 1) % n
        if corner[i]:
            return ((P[i][0] - P[k][0]) * tension, (P[i][1] - P[k][1]) * tension)
        if not closed and i == n - 1:
            return ((P[i][0] - P[k][0]) * tension, (P[i][1] - P[k][1]) * tension)
        j = (i + 1) % n
        return ((P[j][0] - P[k][0]) * 0.5 * tension, (P[j][1] - P[k][1]) * 0.5 * tension)

    path = Path().move(*P[0])
    segs = n if closed else n - 1
    for i in range(segs):
        j = (i + 1) % n
        t0 = tan_out(i)
        t1 = tan_in(j)
        p0, p3 = P[i], P[j]
        path.curve(p0[0] + t0[0] / 3.0, p0[1] + t0[1] / 3.0,
                   p3[0] - t1[0] / 3.0, p3[1] - t1[1] / 3.0, p3[0], p3[1])
    if closed:
        path.close()
    return path


def polyline(pts, closed=False):
    path = Path().move(pts[0][0], pts[0][1])
    for p in pts[1:]:
        path.line(p[0], p[1])
    if closed:
        path.close()
    return path


def ellipse_path(cx, cy, rx, ry, rot=0.0):
    k = 0.5522847498
    pts = [(cx + rx, cy), (cx + rx, cy + ry * k), (cx + rx * k, cy + ry), (cx, cy + ry),
           (cx - rx * k, cy + ry), (cx - rx, cy + ry * k), (cx - rx, cy),
           (cx - rx, cy - ry * k), (cx - rx * k, cy - ry), (cx, cy - ry),
           (cx + rx * k, cy - ry), (cx + rx, cy - ry * k), (cx + rx, cy)]
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        pts = [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]
    p = Path().move(*pts[0])
    for i in range(0, 12, 3):
        p.curve(pts[i + 1][0], pts[i + 1][1], pts[i + 2][0], pts[i + 2][1], pts[i + 3][0], pts[i + 3][1])
    return p.close()


# =============================================================================
# rasteriser
# =============================================================================
class Mask(object):
    __slots__ = ('x0', 'y0', 'w', 'h', 'rows')

    def __init__(self, x0, y0, w, h, rows):
        self.x0, self.y0, self.w, self.h, self.rows = x0, y0, w, h, rows

    def get(self, x, y):
        x -= self.x0; y -= self.y0
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return 0.0
        return self.rows[y][x]

    def intersect(self, other):
        """Return a new mask = self * other (used for nested clips)."""
        x0 = max(self.x0, other.x0); y0 = max(self.y0, other.y0)
        x1 = min(self.x0 + self.w, other.x0 + other.w)
        y1 = min(self.y0 + self.h, other.y0 + other.h)
        if x1 <= x0 or y1 <= y0:
            return Mask(0, 0, 0, 0, [])
        rows = []
        for y in range(y0, y1):
            a = self.rows[y - self.y0]; b = other.rows[y - other.y0]
            oa = x0 - self.x0; ob = x0 - other.x0
            rows.append([a[oa + i] * b[ob + i] for i in range(x1 - x0)])
        return Mask(x0, y0, x1 - x0, y1 - y0, rows)

    def inverted_within(self, other):
        """other * (1 - self): everything in `other` not covered by self."""
        rows = []
        for y in range(other.y0, other.y0 + other.h):
            b = other.rows[y - other.y0]
            r = []
            for i in range(other.w):
                x = other.x0 + i
                r.append(b[i] * (1.0 - self.get(x, y)))
            rows.append(r)
        return Mask(other.x0, other.y0, other.w, other.h, rows)


_EMPTY = Mask(0, 0, 0, 0, [])


def coverage(polys, clip_box=(0, 0, W, H)):
    """Anti-aliased non-zero-winding coverage of closed polylines -> Mask."""
    edges = []
    minx = miny = 1e9
    maxx = maxy = -1e9
    for pts, _closed in polys:
        m = len(pts)
        if m < 2:
            continue
        for i in range(m):
            a = pts[i]; b = pts[(i + 1) % m]
            if a[0] < minx: minx = a[0]
            if a[0] > maxx: maxx = a[0]
            if a[1] < miny: miny = a[1]
            if a[1] > maxy: maxy = a[1]
            if a[1] == b[1]:
                continue
            if a[1] < b[1]:
                edges.append((a[1], b[1], a[0], (b[0] - a[0]) / (b[1] - a[1]), 1))
            else:
                edges.append((b[1], a[1], b[0], (a[0] - b[0]) / (a[1] - b[1]), -1))
    if not edges:
        return _EMPTY
    x0 = max(clip_box[0], int(math.floor(minx)))
    y0 = max(clip_box[1], int(math.floor(miny)))
    x1 = min(clip_box[2], int(math.ceil(maxx)) + 1)
    y1 = min(clip_box[3], int(math.ceil(maxy)) + 1)
    if x1 <= x0 or y1 <= y0:
        return _EMPTY
    bw, bh = x1 - x0, y1 - y0
    rows = [[0.0] * (bw + 2) for _ in range(bh)]
    edges.sort()
    ne = len(edges)
    ei = 0
    active = []
    inv = 1.0 / SUB
    fx0 = float(x0); fx1 = float(x1)
    for sy in range(y0 * SUB, y1 * SUB):
        y = (sy + 0.5) * inv
        while ei < ne and edges[ei][0] <= y:
            active.append(edges[ei]); ei += 1
        if not active:
            continue
        xs = []
        keep = []
        for e in active:
            if e[1] <= y:
                continue
            keep.append(e)
            xs.append((e[2] + (y - e[0]) * e[3], e[4]))
        active = keep
        if len(xs) < 2:
            continue
        xs.sort()
        row = rows[sy // SUB - y0]
        wind = 0
        for k in range(len(xs) - 1):
            wind += xs[k][1]
            if wind == 0:
                continue
            xa = xs[k][0]; xb = xs[k + 1][0]
            if xa < fx0: xa = fx0
            if xb > fx1: xb = fx1
            if xb <= xa:
                continue
            xa -= fx0; xb -= fx0
            ia = int(xa); fa = xa - ia
            ib = int(xb); fb = xb - ib
            row[ia] += (1.0 - fa) * inv
            row[ia + 1] += fa * inv
            row[ib] -= (1.0 - fb) * inv
            row[ib + 1] -= fb * inv
    # prefix sums -> coverage
    out = []
    for row in rows:
        acc = 0.0
        r = [0.0] * bw
        for i in range(bw):
            acc += row[i]
            if acc > 0.002:
                r[i] = acc if acc < 1.0 else 1.0
        out.append(r)
    return Mask(x0, y0, bw, bh, out)


def _width_fn(width):
    if callable(width):
        return width
    if isinstance(width, (int, float)):
        w = float(width)
        return lambda t: w
    keys = list(width)

    def f(t):
        if t <= keys[0][0]:
            return keys[0][1]
        for i in range(1, len(keys)):
            if t <= keys[i][0]:
                t0, w0 = keys[i - 1]; t1, w1 = keys[i]
                u = (t - t0) / (t1 - t0) if t1 > t0 else 1.0
                u = u * u * (3 - 2 * u)   # smoothstep
                return w0 + (w1 - w0) * u
        return keys[-1][1]
    return f


def stroke_polys(polys, width, cap='round'):
    """Convert polylines into closed outline polygons of the stroke."""
    wf = _width_fn(width)
    out = []
    for pts, closed in polys:
        n = len(pts)
        if n < 2:
            continue
        m = n if closed else n - 1
        segn = []
        total = 0.0
        cum = [0.0]
        for i in range(m):
            a = pts[i]; b = pts[(i + 1) % n]
            dx = b[0] - a[0]; dy = b[1] - a[1]
            L = math.hypot(dx, dy) or 1e-9
            segn.append((-dy / L, dx / L))
            total += L
            cum.append(total)
        total = total or 1.0
        left, right = [], []
        for i in range(n):
            if closed:
                n0 = segn[(i - 1) % m]; n1 = segn[i % m]
            else:
                n0 = segn[max(0, i - 1)]; n1 = segn[min(m - 1, i)]
            sx = n0[0] + n1[0]; sy = n0[1] + n1[1]
            L = math.hypot(sx, sy)
            if L < 1e-6:
                ux, uy = n1
            else:
                ux, uy = sx / L, sy / L
                d = ux * n1[0] + uy * n1[1]
                s = 1.0 / max(d, 0.45)
                ux *= s; uy *= s
            hw = 0.5 * wf(cum[i] / total if i < len(cum) else 1.0)
            p = pts[i]
            left.append((p[0] + ux * hw, p[1] + uy * hw))
            right.append((p[0] - ux * hw, p[1] - uy * hw))
        if closed:
            out.append((left, True))
            right.reverse()
            out.append((right, True))
        else:
            poly = list(left)
            if cap == 'round':
                poly.extend(_cap(pts[-1], pts[-2], 0.5 * wf(1.0)))
            poly.extend(reversed(right))
            if cap == 'round':
                poly.extend(_cap(pts[0], pts[1], 0.5 * wf(0.0)))
            out.append((poly, True))
    return out


def _cap(p, prev, hw):
    if hw < 0.6:
        return []
    dx = p[0] - prev[0]; dy = p[1] - prev[1]
    L = math.hypot(dx, dy) or 1e-9
    dx /= L; dy /= L
    # left normal is (-dy, dx); sweep from left through forward to right
    base = math.atan2(dx, -dy)
    pts = []
    steps = 6
    for i in range(1, steps):
        a = base - math.pi * i / steps
        pts.append((p[0] + math.cos(a) * hw, p[1] + math.sin(a) * hw))
    return pts


# =============================================================================
# canvas: paints masks onto raster.Img
# =============================================================================
class Canvas(object):
    def __init__(self, img):
        self.img = img

    # -- painting -------------------------------------------------------------
    def paint(self, mask, color, alpha=1.0, clip=None):
        if mask.w == 0:
            return
        img = self.img
        buf = img.buf
        IW = img.w
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        full = bytes((r, g, b, 255))
        for j in range(mask.h):
            y = mask.y0 + j
            row = mask.rows[j]
            bw = mask.w
            if clip is not None:
                cy = y - clip.y0
                if cy < 0 or cy >= clip.h:
                    continue
                crow = clip.rows[cy]
                off = mask.x0 - clip.x0
                cw = clip.w
                row = [row[i] * crow[i + off] if 0 <= i + off < cw else 0.0 for i in range(bw)]
            base = (y * IW + mask.x0) * 4
            x = 0
            while x < bw:
                c = row[x]
                if c <= 0.003:
                    x += 1
                    continue
                a = c * alpha
                if a >= 0.995:
                    xs = x
                    x += 1
                    while x < bw and row[x] * alpha >= 0.995:
                        x += 1
                    buf[base + xs * 4: base + x * 4] = full * (x - xs)
                    continue
                i = base + x * 4
                da = buf[i + 3] / 255.0
                na = a + da * (1.0 - a)
                if na > 0:
                    k = da * (1.0 - a)
                    buf[i] = int((r * a + buf[i] * k) / na + 0.5)
                    buf[i + 1] = int((g * a + buf[i + 1] * k) / na + 0.5)
                    buf[i + 2] = int((b * a + buf[i + 2] * k) / na + 0.5)
                    buf[i + 3] = int(na * 255 + 0.5)
                x += 1

    def mask(self, path, quality=3.0):
        return coverage(path.flatten(quality))

    def fill(self, path, color, alpha=1.0, clip=None, quality=3.0):
        m = coverage(path.flatten(quality))
        self.paint(m, color, alpha, clip)
        return m

    def stroke(self, path, color, width=3.0, alpha=1.0, clip=None, cap='round', quality=2.0):
        polys = stroke_polys(path.flatten(quality), width, cap)
        m = coverage(polys)
        self.paint(m, color, alpha, clip)
        return m

    def shape(self, path, fill, line=None, lw=3.0, shadows=(), lights=(), clip=None, line_alpha=1.0):
        """Cel-shaded region: base fill, shadow/light layers clipped to it, outline."""
        m = self.fill(path, fill, clip=clip)
        for spath, scol, *rest in shadows:
            a = rest[0] if rest else 1.0
            self.fill(spath, scol, a, clip=m)
        for lpath, lcol, *rest in lights:
            a = rest[0] if rest else 1.0
            self.fill(lpath, lcol, a, clip=m)
        if line is not None and lw > 0:
            self.stroke(path, line, lw, alpha=line_alpha, clip=clip)
        return m


# =============================================================================
# colour helpers
# =============================================================================
def C(s):
    return hexc(s) if isinstance(s, str) else tuple(s)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def mix(a, b, t):
    return lerp(a, b, t)


# =============================================================================
# character parts
# =============================================================================
def _mirror_pts(pts, cx=W / 2.0):
    out = []
    for p in reversed(pts):
        out.append((2 * cx - p[0], p[1]) + tuple(p[2:]))
    return out


def _sym(left_pts, cx=W / 2.0):
    """Symmetric closed outline: left side points (top->bottom) + mirrored."""
    return left_pts + _mirror_pts(left_pts, cx)


def _box(x0, y0, x1, y1):
    return polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True)


class Fig(object):
    """Figure anchors (canvas px) derived from the build params. Front view."""

    def __init__(self, spec):
        b = spec.get('build', {})
        self.cx = W / 2.0
        self.sh = b.get('shoulder', 1.0)      # shoulder width multiplier
        self.bulk = b.get('bulk', 1.0)        # torso / limb thickness
        self.headscale = b.get('head', 1.0)
        # head
        self.head_top = 104.0
        self.chin = 366.0
        self.head_rx = 97.0 * self.headscale
        self.eye_y = 254.0
        self.eye_dx = 50.0
        self.brow_y = 218.0
        self.mouth_y = 328.0
        self.neck_hw = 42.0 * self.bulk
        self.neck_bot = 416.0
        self.shoulder_y = 414.0
        self.sx = 178.0 * self.sh             # shoulder half width
        self.hem = 806.0
        self.foot_y = 1382.0


# ---------------------------------------------------------------- legs / shoes
def draw_legs(cv, F, spec, LINE):
    o = spec['outfit']
    pants = C(o.get('pants', '#262a3b'))
    pants_sh = C(o.get('pants_shadow', '#171a28'))
    shoe = C(o.get('shoes', '#f3f3f1'))
    shoe_sh = C(o.get('shoes_shadow', '#c9cbd2'))
    sole = C(o.get('sole', '#8d9099'))
    cx = F.cx
    bk = F.bulk
    masks = []
    for sgn in (-1, 1):
        s = sgn
        leg = smooth([(cx + s * 146 * bk, 760, 'c'), (cx + s * 138 * bk, 900), (cx + s * 116 * bk, 1050),
                      (cx + s * 106 * bk, 1160), (cx + s * 90 * bk, 1312, 'c'), (cx + s * 34, 1312, 'c'),
                      (cx + s * 32, 1150), (cx + s * 30, 1040), (cx + s * 22, 920), (cx + s * 4, 846, 'c'),
                      (cx + s * 4, 760, 'c')])
        # shadow: inner half of each leg + band under the jacket hem
        inner = smooth([(cx + s * 4, 846, 'c'), (cx + s * 62 * bk, 900), (cx + s * 66 * bk, 1050),
                        (cx + s * 62 * bk, 1180), (cx + s * 58 * bk, 1312, 'c'), (cx + s * 34, 1312, 'c'),
                        (cx + s * 32, 1150), (cx + s * 30, 1040), (cx + s * 22, 920)])
        hemband = _box(cx - 220, 740, cx + 220, F.hem + 30)
        m = cv.shape(leg, pants, LINE, 3.2, shadows=[(inner, pants_sh), (hemband, pants_sh)])
        masks.append(m)
        # knee crease + a fold line at the shin
        cv.stroke(smooth([(cx + s * 50 * bk, 1048), (cx + s * 78 * bk, 1040), (cx + s * 104 * bk, 1050)], closed=False),
                  pants_sh, [(0, 0.8), (0.5, 2.4), (1, 0.8)], clip=m)
        cv.stroke(smooth([(cx + s * 40, 1210), (cx + s * 44, 1260), (cx + s * 60 * bk, 1300)], closed=False),
                  pants_sh, [(0, 0.6), (1, 2.2)], clip=m)
    # centre seam (crotch), clipped to the legs
    for m in masks:
        cv.stroke(polyline([(cx, 846), (cx, 1000)]), shade(pants_sh, 0.7), 2.0, clip=m)
    # shoes (wide sneakers, front view)
    for sgn in (-1, 1):
        x = cx + sgn * 64 * bk
        sp = smooth([(x - 40, 1304, 'c'), (x - 56, 1330), (x - 62, 1358), (x - 54, F.foot_y, 'c'),
                     (x + 54, F.foot_y, 'c'), (x + 62, 1358), (x + 56, 1330), (x + 40, 1304, 'c')])
        toe_sh = smooth([(x - 60, 1346), (x - 20, 1338), (x + 24, 1340), (x + 60, 1346), (x + 56, F.foot_y, 'c'), (x - 56, F.foot_y, 'c')])
        sm = cv.shape(sp, shoe, LINE, 3.0, shadows=[(toe_sh, shoe_sh, 0.9)])
        # sole
        cv.fill(_box(x - 70, 1362, x + 70, F.foot_y + 4), sole, clip=sm)
        cv.stroke(smooth([(x - 60, 1362), (x, 1360), (x + 60, 1362)], closed=False), LINE, 2.4, clip=sm)
        # toe cap + tongue/lace hint
        cv.stroke(smooth([(x - 44, 1348), (x, 1338), (x + 44, 1348)], closed=False), shade(shoe_sh, 0.85), 2.2, clip=sm)
        cv.stroke(smooth([(x - 22, 1306), (x - 14, 1322), (x - 6, 1334)], closed=False), shade(shoe_sh, 0.8), 2.0, clip=sm)
        cv.stroke(smooth([(x + 22, 1306), (x + 14, 1322), (x + 6, 1334)], closed=False), shade(shoe_sh, 0.8), 2.0, clip=sm)
        # dark heel tab / logo tick
        cv.fill(smooth([(x + sgn * 30, 1312), (x + sgn * 44, 1322), (x + sgn * 52, 1350), (x + sgn * 36, 1346)]), shade(shoe_sh, 0.75), clip=sm)


# ---------------------------------------------------------------- hands
def draw_hand(cv, F, spec, hx, wy, sgn, LINE, skin, skin_sh):
    """Relaxed hand hanging at the side; hx = wrist centre x, wy = wrist y."""
    inn = -sgn   # direction towards the body
    pts = [(hx + sgn * 27, wy, 'c'), (hx + sgn * 33, wy + 44), (hx + sgn * 30, wy + 80), (hx + sgn * 20, wy + 104),
           (hx + sgn * 4, wy + 110), (hx + inn * 14, wy + 104), (hx + inn * 27, wy + 86),
           (hx + inn * 36, wy + 60), (hx + inn * 40, wy + 36, 'c'), (hx + inn * 32, wy + 18), (hx + inn * 27, wy, 'c')]
    hand = smooth(pts)
    # shadow on the side away from the light (viewer's right side of each hand)
    if sgn > 0:
        sh = smooth([(hx + 8, wy, 'c'), (hx + 12, wy + 60), (hx + 8, wy + 106), (hx + 20, wy + 104), (hx + 30, wy + 80),
                     (hx + 33, wy + 44), (hx + 27, wy, 'c')])
    else:
        sh = smooth([(hx + 14, wy + 16), (hx + 18, wy + 60), (hx + 14, wy + 100), (hx + 27, wy + 86), (hx + 36, wy + 60),
                     (hx + 40, wy + 36, 'c'), (hx + 32, wy + 18)])
    m = cv.shape(hand, skin, LINE, 3.0, shadows=[(sh, skin_sh, 0.9)])
    # fingers
    for fx in (sgn * 20, sgn * 6, inn * 8):
        cv.stroke(smooth([(hx + fx, wy + 80), (hx + fx + sgn * 1, wy + 96), (hx + fx, wy + 108)], closed=False),
                  LINE, [(0, 0.8), (0.4, 2.2), (1, 1.4)], clip=m)
    # knuckle ridge
    cv.stroke(smooth([(hx + sgn * 26, wy + 78), (hx + sgn * 6, wy + 74), (hx + inn * 18, wy + 80)], closed=False),
              mix(LINE, skin, 0.5), [(0, 0.6), (0.5, 1.8), (1, 0.6)], clip=m)
    # thumb crease
    cv.stroke(smooth([(hx + inn * 28, wy + 22), (hx + inn * 22, wy + 48), (hx + inn * 30, wy + 72)], closed=False),
              LINE, [(0, 0.6), (0.5, 2.0), (1, 1.2)], clip=m)
    return m


# ---------------------------------------------------------------- torso
def draw_torso(cv, F, spec, LINE, skin, skin_sh):
    o = spec['outfit']
    jk = C(o.get('jacket', '#232838'))
    jk_sh = C(o.get('jacket_shadow', '#141726'))
    jk_hi = C(o.get('jacket_light', '#3b4360'))
    trim = C(o.get('trim', '#4d5578'))
    hood = C(o.get('hoodie', '#c8323b'))
    hood_sh = C(o.get('hoodie_shadow', '#8a1f27'))
    hood_hi = C(o.get('hoodie_light', '#e04a52'))
    cx, sy, sx, hem = F.cx, F.shoulder_y, F.sx, F.hem
    bk = F.bulk
    nh = F.neck_hw
    # --- neck ---------------------------------------------------------------
    neck = smooth([(cx - nh + 4, 330, 'c'), (cx - nh, 380), (cx - nh - 6, F.neck_bot + 10, 'c'),
                   (cx + nh + 6, F.neck_bot + 10, 'c'), (cx + nh, 380), (cx + nh - 4, 330, 'c')])
    nm = cv.shape(neck, skin, LINE, 3.0)
    cv.fill(_box(cx - nh - 10, 320, cx + nh + 10, 392), skin_sh, clip=nm)        # chin shadow
    cv.stroke(smooth([(cx - nh + 6, 392), (cx - nh + 14, 404), (cx - 10, 416)], closed=False), skin_sh, 2.0, clip=nm)
    # --- hood (behind the neck / collar) -----------------------------------
    if o.get('hood', True):
        # back of the hood, bunched behind the neck
        hd = smooth([(cx - 118, sy + 40, 'c'), (cx - 116, 392), (cx - 96, 352), (cx - 48, 332), (cx, 326),
                     (cx + 48, 332), (cx + 96, 352), (cx + 116, 392), (cx + 118, sy + 40, 'c')])
        hd_sh = smooth([(cx - 60, 346), (cx, 352), (cx + 60, 346), (cx + 66, 440, 'c'), (cx - 66, 440, 'c')])
        hd_rim = smooth([(cx - 116, 392), (cx - 96, 352), (cx - 48, 332), (cx, 326), (cx + 48, 332), (cx + 96, 352),
                         (cx + 116, 392), (cx + 106, 400, 'c'), (cx + 88, 364), (cx + 46, 346), (cx, 340), (cx - 46, 346),
                         (cx - 88, 364), (cx - 106, 400, 'c')])
        cv.shape(hd, hood, LINE, 3.0, shadows=[(hd_sh, hood_sh)], lights=[(hd_rim, hood_hi, 0.8)])
        for s in (-1, 1):
            cv.stroke(smooth([(cx + s * 104, 410), (cx + s * 82, 380), (cx + s * 56, 362)], closed=False), hood_sh, [(0, 2.6), (1, 0.8)])
    # --- jacket body --------------------------------------------------------
    body = smooth([(cx - sx + 14, sy - 2, 'c'), (cx - sx + 12, 520), (cx - sx + 44 * bk, 690), (cx - sx + 36 * bk, hem, 'c'),
                   (cx + sx - 36 * bk, hem, 'c'), (cx + sx - 44 * bk, 690), (cx + sx - 12, 520), (cx + sx - 14, sy - 2, 'c'),
                   (cx + 70, sy - 12), (cx, sy - 18), (cx - 70, sy - 12)])
    side_sh = smooth([(cx + 50, sy + 40), (cx + 92, 640), (cx + 84, hem, 'c'), (cx + sx - 36 * bk + 3, hem, 'c'),
                      (cx + sx - 44 * bk + 3, 690), (cx + sx - 12 + 3, 520), (cx + sx - 14 + 3, sy - 2, 'c'), (cx + 70, sy - 12)])
    bm = cv.shape(body, jk, None, 0, shadows=[(side_sh, jk_sh)])
    # --- hoodie visible in the V opening ---------------------------------------
    v_open = smooth([(cx - 40, sy - 20, 'c'), (cx - 40, 500), (cx - 20, 600), (cx, 646, 'c'),
                     (cx + 20, 600), (cx + 40, 500), (cx + 40, sy - 20, 'c')])
    v_sh = smooth([(cx - 44, sy - 24, 'c'), (cx - 42, 480), (cx, 500), (cx + 42, 480), (cx + 44, sy - 24, 'c')])
    v_sh2 = smooth([(cx + 2, 470, 'c'), (cx + 26, 560), (cx + 8, 640, 'c'), (cx - 2, 640, 'c')])
    vm = cv.shape(v_open, hood, None, 0, shadows=[(v_sh, hood_sh), (v_sh2, hood_sh, 0.9)])
    # drawstrings
    for s in (-1, 1):
        cv.stroke(smooth([(cx + s * 12, 436), (cx + s * 18, 500), (cx + s * 14, 560), (cx + s * 8, 600)], closed=False),
                  shade(hood, 1.45), [(0, 3.0), (0.7, 2.6), (1, 1.6)], clip=vm)
        cv.fill(ellipse_path(cx + s * 8, 604, 4, 6), shade(hood, 0.55), clip=vm)
    # --- jacket panels (lighter facing along the open edge) ------------------
    panel_l = smooth([(cx - 44, sy - 22, 'c'), (cx - 44, 500), (cx - 24, 600), (cx - 4, 646, 'c'), (cx - 4, hem + 4, 'c'),
                      (cx - 22, hem + 4, 'c'), (cx - 30, 640), (cx - 58, 520), (cx - 64, sy - 20, 'c')])
    panel_r = panel_l.mirror(cx)
    cv.fill(panel_l, jk_hi, clip=bm)
    cv.fill(panel_r, jk_hi, clip=bm)
    cv.fill(smooth([(cx + 4, 646, 'c'), (cx + 22, hem + 4, 'c'), (cx + 2, hem + 4, 'c'), (cx - 6, 700)]), jk_sh, clip=bm)
    for s in (-1, 1):
        cv.stroke(smooth([(cx + s * 42, sy - 22, 'c'), (cx + s * 42, 500), (cx + s * 22, 600), (cx + s * 2, 646, 'c')], closed=False), LINE, 3.0)
    cv.stroke(polyline([(cx + 2, 646), (cx + 2, hem)]), LINE, 2.6)
    # buttons
    for by in (696, 752):
        cv.fill(ellipse_path(cx + 12, by, 7, 7), trim)
        cv.stroke(ellipse_path(cx + 12, by, 7, 7), LINE, 1.8)
    # body outline (drawn after panels so it sits on top), hem fold
    cv.stroke(body, LINE, 3.2)
    cv.stroke(smooth([(cx - sx + 40 * bk, hem - 26), (cx, hem - 22), (cx + sx - 40 * bk, hem - 26)], closed=False), jk_sh, 2.2, clip=bm)
    # chest fold lines under the arms
    cv.stroke(smooth([(cx - sx + 20, 470), (cx - sx + 60, 500), (cx - sx + 90, 560)], closed=False), jk_sh, [(0, 2.4), (1, 0.6)], clip=bm)
    # --- hood front edge draped over the shoulders (on top of the jacket) ---
    if o.get('hood', True):
        for s in (-1, 1):
            drape = smooth([(cx + s * 44, sy - 14, 'c'), (cx + s * 90, sy - 2), (cx + s * 134, sy + 18),
                            (cx + s * 158, sy + 44, 'c'), (cx + s * 130, sy + 40), (cx + s * 92, sy + 26),
                            (cx + s * 52, sy + 14, 'c')])
            dsh = smooth([(cx + s * 44, sy + 2), (cx + s * 92, sy + 12), (cx + s * 158, sy + 44, 'c'), (cx + s * 130, sy + 40),
                          (cx + s * 92, sy + 26), (cx + s * 52, sy + 14, 'c')])
            dm = cv.shape(drape, hood, LINE, 2.8, shadows=[(dsh, hood_sh, 0.9)])
            cv.stroke(smooth([(cx + s * 60, sy - 6), (cx + s * 100, sy + 8), (cx + s * 140, sy + 30)], closed=False), hood_hi, 2.0, clip=dm, alpha=0.9)
    # --- stand collar (front tabs of the jacket) --------------------------------
    col_l = smooth([(cx - 78, sy + 8, 'c'), (cx - 74, 374, 'c'), (cx - 42, 364, 'c'), (cx - 30, 404, 'c'), (cx - 36, sy + 18, 'c')])
    col_l_sh = smooth([(cx - 74, 374, 'c'), (cx - 42, 364, 'c'), (cx - 30, 404, 'c'), (cx - 36, 440, 'c'), (cx - 56, 440, 'c'), (cx - 54, 376, 'c')])
    for s in (-1, 1):
        cp = col_l if s < 0 else col_l.mirror(cx)
        csh = col_l_sh if s < 0 else col_l_sh.mirror(cx)
        cm = cv.shape(cp, jk_hi, LINE, 3.0, shadows=[(csh, jk, 0.85)])
        cv.stroke(smooth([(cx + s * 72, 382), (cx + s * 46, 372)], closed=False), trim, 2.0, clip=cm)
    # --- sleeves -----------------------------------------------------------------
    for s in (-1, 1):
        ax = cx + s * sx
        # relaxed arm: rounded deltoid, slight bend at the elbow, forearm angled a little outward
        sl = smooth([(ax - s * 48, sy - 2, 'c'), (ax - s * 16, sy - 12), (ax + s * 14, sy + 20), (ax + s * 26 * bk, 520),
                     (ax + s * 28 * bk, 610), (ax + s * 32 * bk, 700), (ax + s * 30 * bk, 784, 'c'),
                     (ax - s * 32 * bk, 790, 'c'), (ax - s * 34 * bk, 700), (ax - s * 32 * bk, 600),
                     (ax - s * 40 * bk, 490)])
        if s < 0:   # lit side: shadow only on the inner edge
            ssh = smooth([(ax - s * 18 * bk, 480), (ax - s * 12 * bk, 600), (ax - s * 12 * bk, 700), (ax - s * 8 * bk, 794, 'c'),
                          (ax - s * 34 * bk, 794, 'c'), (ax - s * 36 * bk, 700), (ax - s * 34 * bk, 600), (ax - s * 42 * bk, 490)])
        else:       # shaded side: most of the sleeve
            ssh = smooth([(ax - s * 8, sy + 30), (ax + s * 10 * bk, 520), (ax + s * 14 * bk, 640), (ax + s * 12 * bk, 720),
                          (ax + s * 10 * bk, 794, 'c'), (ax - s * 34 * bk, 794, 'c'), (ax - s * 36 * bk, 700),
                          (ax - s * 34 * bk, 600), (ax - s * 42 * bk, 490)])
        sm = cv.shape(sl, jk, LINE, 3.2, shadows=[(ssh, jk_sh)])
        # shoulder seam + elbow fold + cuff
        cv.stroke(smooth([(ax - s * 44, sy + 8), (ax - s * 30, 470), (ax - s * 36 * bk, 520)], closed=False), jk_sh, 2.0, clip=sm)
        cv.stroke(smooth([(ax + s * 26 * bk, 596), (ax + s * 4, 614), (ax - s * 22 * bk, 602)], closed=False), jk_sh, [(0, 2.2), (1, 0.6)], clip=sm)
        cv.stroke(smooth([(ax + s * 30 * bk, 758), (ax, 752), (ax - s * 32 * bk, 762)], closed=False), jk_sh, 2.2, clip=sm)
        # hand hanging from the cuff
        draw_hand(cv, F, spec, ax - s * 1 * bk, 786, s, LINE, skin, skin_sh)


# ---------------------------------------------------------------- head
def head_path(F):
    cx = F.cx
    rx = F.head_rx
    left = [(cx - rx * 0.60, F.head_top + 14), (cx - rx * 0.95, 176), (cx - rx * 1.0, 240),
            (cx - rx * 0.96, 292), (cx - rx * 0.82, 334), (cx - rx * 0.44, 359)]
    return smooth([(cx, F.head_top, 'c')] + left + [(cx, F.chin)] + _mirror_pts(left, cx))


def draw_head_base(cv, F, spec, LINE, skin, skin_sh):
    cx = F.cx
    rx = F.head_rx
    hp = head_path(F)
    # ears
    for s in (-1, 1):
        ex = cx + s * rx * 1.0
        ear = smooth([(ex - s * 12, 232, 'c'), (ex + s * 8, 234), (ex + s * 16, 258), (ex + s * 10, 284),
                      (ex - s * 8, 296, 'c')])
        ear_sh = smooth([(ex - s * 4, 244), (ex + s * 8, 260), (ex, 284), (ex - s * 12, 290, 'c'), (ex - s * 12, 250, 'c')])
        em = cv.shape(ear, skin, LINE, 3.0, shadows=[(ear_sh, skin_sh)])
        cv.stroke(smooth([(ex + s * 4, 246), (ex + s * 8, 262), (ex + s * 2, 278)], closed=False), shade(skin_sh, 0.85), 2.0, clip=em)
    # face + jaw shadow (light from the viewer's upper-left)
    jaw_sh = smooth([(cx + rx * 0.62, 298), (cx + rx * 0.96, 292), (cx + rx * 0.82, 334), (cx + rx * 0.44, 359),
                     (cx, F.chin), (cx - rx * 0.30, 358), (cx - rx * 0.1, 346), (cx + rx * 0.36, 328)])
    cheek_sh = smooth([(cx + rx * 0.80, 240), (cx + rx * 1.0, 240), (cx + rx * 0.96, 292), (cx + rx * 0.7, 294)])
    hm = cv.shape(hp, skin, LINE, 3.6, shadows=[(jaw_sh, skin_sh, 0.9), (cheek_sh, skin_sh, 0.7)])
    return hm


# ---------------------------------------------------------------- eyes / face
def _expr_params(expression):
    e = dict(open=1.0, lower=0.0, brow_in=0, brow_out=0, brow_w=1.0, pupil=1.0, iris_dy=0,
             mouth='neutral', lid=0.0)
    if expression == 'happy':
        e.update(open=0.90, lower=0.36, brow_in=-4, brow_out=-8, mouth='grin', iris_dy=1)
    elif expression == 'serious':
        e.update(open=0.86, brow_in=8, brow_out=-4, brow_w=1.1, mouth='flat', lid=0.22)
    elif expression == 'angry':
        e.update(open=0.84, brow_in=20, brow_out=-10, brow_w=1.3, mouth='snarl', lid=0.34, pupil=0.85)
    elif expression == 'surprised':
        e.update(open=1.30, lower=-0.12, brow_in=-16, brow_out=-18, mouth='oh', pupil=0.7)
    elif expression == 'sad':
        e.update(open=0.88, brow_in=-12, brow_out=8, mouth='frown', lid=0.26, iris_dy=2)
    return e


def draw_eye(cv, F, spec, ex, ey, sgn, e, LINE):
    eyes = spec.get('eyes', {})
    skin = C(spec.get('skin', '#f1c9a5'))
    iris_c = C(eyes.get('color', '#8a552a'))
    iris_dk = C(eyes.get('dark', '#4a2a12'))
    iris_lt = C(eyes.get('light', '#c78a4a'))
    white = C(eyes.get('white', '#f8f6f2'))
    white_sh = C(eyes.get('white_shadow', '#d8d0ca'))
    ew = 27.0 * eyes.get('width', 1.0)                 # half width
    up = 20.0 * e['open'] * eyes.get('height', 1.0)    # upper lid height above centre
    lo = 12.0 * (1.0 - e['lower']) * eyes.get('height', 1.0)
    inner = (ex - sgn * ew, ey + 4)
    outer = (ex + sgn * ew * 1.0, ey - 5)
    top = [(ex - sgn * ew * 0.48, ey - up * 0.74), (ex + sgn * ew * 0.08, ey - up), (ex + sgn * ew * 0.62, ey - up * 0.74)]
    bot = [(ex + sgn * ew * 0.55, ey + lo * 0.78), (ex, ey + lo), (ex - sgn * ew * 0.5, ey + lo * 0.70)]
    eye = smooth([(inner[0], inner[1], 'c')] + top + [(outer[0], outer[1], 'c')] + bot)
    em = cv.fill(eye, white)
    # thin lid shadow across the top of the white
    lid_sh = smooth([(inner[0], inner[1], 'c')] + top + [(outer[0], outer[1], 'c'),
                     (ex + sgn * ew * 0.5, ey - up * 0.52), (ex, ey - up * 0.55), (ex - sgn * ew * 0.5, ey - up * 0.45)])
    cv.fill(lid_sh, white_sh, clip=em)
    # iris
    ir = 16.0 * eyes.get('iris', 1.0)
    icx, icy = ex + sgn * 1.0, ey + 1 + e['iris_dy']
    iris = ellipse_path(icx, icy, ir, ir * 1.1)
    im = cv.fill(iris, iris_c, clip=em)
    cv.fill(ellipse_path(icx, icy - ir * 0.40, ir * 0.98, ir * 0.78), iris_dk, clip=im)
    cv.fill(ellipse_path(icx, icy + ir * 0.50, ir * 0.66, ir * 0.48), iris_lt, 0.8, clip=im)
    cv.stroke(iris, iris_dk, 2.4, clip=em)
    pr = ir * 0.40 * e['pupil']
    cv.fill(ellipse_path(icx, icy, pr, pr * 1.25), (22, 12, 10), clip=em)
    # highlights
    cv.fill(ellipse_path(icx - sgn * ir * 0.40, icy - ir * 0.42, ir * 0.30, ir * 0.30), (255, 255, 255), clip=em)
    cv.fill(ellipse_path(icx + sgn * ir * 0.38, icy + ir * 0.48, ir * 0.15, ir * 0.15), (255, 255, 255), 0.9, clip=em)
    # heavy lid (serious/angry/sad): skin drops over the top of the eye
    if e['lid'] > 0:
        drop = up * e['lid']
        top2 = [(ex - sgn * ew * 0.48, ey - up * 0.74 + drop), (ex + sgn * ew * 0.08, ey - up + drop * 1.1),
                (ex + sgn * ew * 0.62, ey - up * 0.74 + drop * 0.9)]
        lidp = smooth([(inner[0] - sgn * 3, inner[1] - 2, 'c')] + top2 + [(outer[0] + sgn * 4, outer[1] - 4, 'c'),
                      (outer[0] + sgn * 6, outer[1] - 34, 'c'), (inner[0] - sgn * 6, inner[1] - 34, 'c')])
        cv.fill(lidp, skin)
        top = top2
    # upper lash line: thick, tapering at the inner corner, flick at the outer corner
    lash = [(inner[0] - sgn * 1, inner[1] - 1)] + [(p[0], p[1] - 1.5) for p in top] + [(outer[0] + sgn * 6, outer[1] - 5)]
    cv.stroke(smooth(lash, closed=False), LINE, [(0, 1.6), (0.35, 5.0), (0.8, 5.4), (1.0, 2.2)])
    # lower lid: thin
    low = [(inner[0] + sgn * 5, inner[1] + 1)] + [(p[0], p[1] + 1) for p in reversed(bot)] + [(outer[0] - sgn * 1, outer[1] + 2)]
    cv.stroke(smooth(low, closed=False), mix(LINE, iris_c, 0.2), [(0, 1.0), (0.5, 2.0), (1.0, 1.8)])
    # crease
    cr = [(ex - sgn * ew * 0.35, ey - up - 8), (ex + sgn * ew * 0.15, ey - up - 10), (ex + sgn * ew * 0.72, ey - up - 5)]
    cv.stroke(smooth(cr, closed=False), mix(LINE, skin, 0.45), [(0, 0.8), (0.5, 1.8), (1, 0.8)])
    # under-eye marks (Yuji's signature)
    if spec.get('eye_marks', False):
        mk = C(spec.get('eye_mark_color', '#5b3a36'))
        m1 = [(ex - sgn * ew * 0.62, ey + lo + 8), (ex - sgn * ew * 0.10, ey + lo + 12), (ex + sgn * ew * 0.50, ey + lo + 9)]
        cv.stroke(smooth(m1, closed=False), mk, [(0, 1.2), (0.5, 3.0), (1, 1.2)])
        m2 = [(ex - sgn * ew * 0.30, ey + lo + 18), (ex + sgn * ew * 0.05, ey + lo + 20), (ex + sgn * ew * 0.36, ey + lo + 18)]
        cv.stroke(smooth(m2, closed=False), mk, [(0, 0.6), (0.5, 2.0), (1, 0.6)], alpha=0.8)


def draw_brow(cv, F, spec, ex, ey, sgn, e, LINE):
    bc = C(spec.get('brow_color', '#3a2624'))
    bw = spec.get('brow_weight', 1.0) * e['brow_w']
    inner = (ex - sgn * 28, ey + e['brow_in'])
    outer = (ex + sgn * 34, ey + e['brow_out'])
    mid = ((inner[0] + outer[0]) / 2.0 + sgn * 4, min(inner[1], outer[1]) - 5)
    path = smooth([inner, mid, outer], closed=False)
    prof = [(0, 4.5 * bw), (0.4, 8.5 * bw), (1.0, 3.0 * bw)]
    cv.stroke(path, bc, prof)


def draw_mouth(cv, F, spec, e, LINE, skin_sh):
    cx, my = F.cx, F.mouth_y
    kind = e['mouth']
    inside = (78, 32, 40)
    teeth = (250, 246, 240)
    tongue = (200, 80, 90)
    lip = mix(LINE, (140, 60, 60), 0.3)
    prof = [(0, 1.2), (0.5, 2.8), (1, 1.2)]
    if kind == 'neutral':
        cv.stroke(smooth([(cx - 22, my - 3), (cx, my + 3), (cx + 22, my - 3)], closed=False), lip, prof)
    elif kind == 'flat':
        cv.stroke(smooth([(cx - 22, my), (cx, my + 1), (cx + 22, my)], closed=False), lip, prof)
    elif kind == 'frown':
        cv.stroke(smooth([(cx - 20, my + 4), (cx, my - 3), (cx + 20, my + 4)], closed=False), lip, prof)
    elif kind == 'grin':
        mp = smooth([(cx - 38, my - 12, 'c'), (cx, my - 2), (cx + 38, my - 12, 'c'), (cx + 26, my + 22), (cx, my + 30), (cx - 26, my + 22)])
        mm = cv.fill(mp, inside)
        cv.fill(smooth([(cx - 38, my - 12, 'c'), (cx, my - 2), (cx + 38, my - 12, 'c'), (cx + 28, my + 6), (cx, my + 10), (cx - 28, my + 6)]), teeth, clip=mm)
        cv.fill(ellipse_path(cx, my + 30, 18, 10), tongue, clip=mm)
        cv.stroke(mp, lip, [(0, 2.8), (0.5, 2.0), (1, 2.8)])
        cv.stroke(polyline([(cx - 38, my - 12), (cx - 46, my - 20)]), lip, 2.4)
        cv.stroke(polyline([(cx + 38, my - 12), (cx + 46, my - 20)]), lip, 2.4)
    elif kind == 'snarl':
        mp = smooth([(cx - 32, my - 2, 'c'), (cx, my + 4), (cx + 32, my - 2, 'c'), (cx + 24, my + 18), (cx, my + 22), (cx - 24, my + 18)])
        mm = cv.fill(mp, inside)
        cv.fill(smooth([(cx - 32, my - 2, 'c'), (cx, my + 4), (cx + 32, my - 2, 'c'), (cx + 24, my + 9), (cx, my + 12), (cx - 24, my + 9)]), teeth, clip=mm)
        for tx in (-18, -7, 4, 15):
            cv.stroke(polyline([(cx + tx, my + 1), (cx + tx, my + 11)]), (170, 150, 145), 1.4, clip=mm)
        cv.stroke(mp, lip, 2.6)
    elif kind == 'oh':
        mp = ellipse_path(cx, my + 6, 14, 18)
        cv.fill(mp, inside)
        cv.stroke(mp, lip, 2.6)
    cv.stroke(smooth([(cx - 10, my + 28), (cx, my + 30), (cx + 10, my + 28)], closed=False), skin_sh, [(0, 0.8), (0.5, 2.0), (1, 0.8)], alpha=0.8)


def draw_face(cv, F, spec, expression, LINE, skin, skin_sh):
    e = _expr_params(expression)
    cx = F.cx
    # nose: bridge shadow on the shaded side + small tip line
    cv.fill(smooth([(cx + 5, 262), (cx + 13, 282), (cx + 15, 298), (cx + 6, 303), (cx + 2, 294)]), skin_sh, 0.85)
    cv.stroke(smooth([(cx + 7, 270), (cx + 14, 288), (cx + 13, 300), (cx + 2, 303)], closed=False), LINE, [(0, 0.6), (0.6, 1.6), (1.0, 2.2)], alpha=0.9)
    cv.stroke(polyline([(cx - 9, 302), (cx - 3, 304)]), LINE, 1.6, alpha=0.6)
    for s in (-1, 1):
        ex = cx + s * F.eye_dx
        draw_eye(cv, F, spec, ex, F.eye_y, s, e, LINE)
        draw_brow(cv, F, spec, ex, F.brow_y, s, e, LINE)
    draw_mouth(cv, F, spec, e, LINE, skin_sh)


# ---------------------------------------------------------------- hair
def _ell(cx, cy, rx, ry, ang_deg):
    a = math.radians(ang_deg)
    return (cx + rx * math.sin(a), cy - ry * math.cos(a))


def spiky_outline(cx, cy, rx, ry, spikes, bulge=0.16):
    """Points (for smooth()) of a spiky cap. spikes: (angle, length, lean, half_width_deg).

    angle 0 = straight up, negative = viewer's left; lean rotates the tip
    direction; the outline runs left base -> over the top -> right base.
    """
    pts = []
    for ang, length, lean, hw in spikes:
        bl = _ell(cx, cy, rx, ry, ang - hw)
        br = _ell(cx, cy, rx, ry, ang + hw)
        bm = _ell(cx, cy, rx, ry, ang)
        d = math.radians(ang + lean)
        tip = (bm[0] + length * math.sin(d), bm[1] - length * math.cos(d))

        def mid(b):
            mx, my = (b[0] + tip[0]) / 2.0, (b[1] + tip[1]) / 2.0
            px, py = b[0] - bm[0], b[1] - bm[1]
            L = math.hypot(px, py) or 1.0
            return (mx + px / L * length * bulge, my + py / L * length * bulge)
        pts.append((bl[0], bl[1], 'c'))
        pts.append(mid(bl))
        pts.append((tip[0], tip[1], 'c'))
        pts.append(mid(br))
        pts.append((br[0], br[1], 'c'))
    return pts


def _arc_pts(cx, cy, rx, ry, a0, a1, n):
    return [_ell(cx, cy, rx, ry, a0 + (a1 - a0) * i / float(n)) for i in range(n + 1)]


def draw_hair_yuji(cv, F, spec, LINE, head_mask, skin_sh):
    hair = spec['hair']
    hc = C(hair.get('color', '#f4a3a6'))
    hs = C(hair.get('shadow', '#d9767f'))
    hl = C(hair.get('line', '#5a2c36'))
    hh = C(hair.get('highlight', '#fbc9c8'))
    uc = C(hair.get('undercut', '#3b2c2c'))
    uc_l = C(hair.get('undercut_line', '#1f1616'))
    cx = F.cx
    rx = F.head_rx
    ccx, ccy, crx, cry = cx, 206.0, rx * 1.10, 134.0     # hair cap ellipse (top ~72)
    # --- undercut: dark band on the sides of the skull, above the ears ------
    for s in (-1, 1):
        u = smooth([(cx + s * rx * 0.70, 150), (cx + s * rx * 0.96, 168), (cx + s * rx * 1.02, 210),
                    (cx + s * rx * 1.0, 240, 'c'), (cx + s * rx * 0.88, 240, 'c'), (cx + s * rx * 0.80, 210),
                    (cx + s * rx * 0.74, 180)])
        um = cv.shape(u, uc, uc_l, 2.6)
        cv.fill(smooth([(cx + s * rx * 0.86, 176), (cx + s * rx * 1.04, 200), (cx + s * rx * 1.02, 242, 'c'), (cx + s * rx * 0.92, 242, 'c')]), shade(uc, 0.75), clip=um)
    # --- forehead: shadow cast by the hair ---------------------------------
    hairline = [(cx - rx * 0.96, 184, 'c'), (cx - rx * 0.86, 166), (cx - rx * 0.55, 158), (cx - rx * 0.26, 160),
                (cx - rx * 0.10, 164), (cx, 176, 'c'), (cx + rx * 0.10, 164), (cx + rx * 0.26, 160), (cx + rx * 0.55, 158),
                (cx + rx * 0.86, 166), (cx + rx * 0.96, 184, 'c')]
    sh_pts = [(p[0], p[1] + 16) + tuple(p[2:]) for p in hairline]
    cv.fill(smooth([(cx - rx * 1.2, 90, 'c')] + sh_pts + [(cx + rx * 1.2, 90, 'c')]), skin_sh, 0.9, clip=head_mask)
    # --- main pink mass ------------------------------------------------------
    spikes = hair.get('spikes', [
        (-82, 26, -30, 9), (-56, 40, -18, 12), (-30, 50, -8, 12), (-4, 54, 0, 12), (22, 50, 6, 12),
        (48, 42, 14, 12), (74, 30, 26, 10)])
    top = spiky_outline(ccx, ccy, crx, cry, spikes, bulge=0.10)
    right_side = [(cx + rx * 1.08, 176), (cx + rx * 1.10, 196, 'c'), (cx + rx * 0.98, 186, 'c')]
    left_side = [(cx - rx * 0.98, 186, 'c'), (cx - rx * 1.10, 196, 'c'), (cx - rx * 1.08, 176)]
    mass = smooth(top + right_side + list(reversed(hairline)) + left_side)
    band_sh = smooth([(cx - rx * 1.2, 128), (cx - rx * 0.6, 122), (cx, 126), (cx + rx * 0.6, 122), (cx + rx * 1.2, 128),
                      (cx + rx * 1.25, 210, 'c'), (cx - rx * 1.25, 210, 'c')])
    right_sh = smooth([(cx + rx * 0.45, 60, 'c'), (cx + rx * 0.7, 80), (cx + rx * 1.2, 120), (cx + rx * 1.25, 210, 'c'),
                       (cx + rx * 0.7, 210, 'c'), (cx + rx * 0.6, 120)])
    hm = cv.shape(mass, hc, hl, 3.0, shadows=[(band_sh, hs), (right_sh, hs, 0.75)])
    # zig-zag highlight band following the cap
    outer = _arc_pts(ccx, ccy, crx * 0.80, cry * 0.80, -70, 70, 12)
    inner = _arc_pts(ccx, ccy, crx * 0.70, cry * 0.70, 70, -70, 12)
    zz = []
    for i, p in enumerate(outer):
        q = _ell(ccx, ccy, crx * (0.80 if i % 2 else 0.74), cry * (0.80 if i % 2 else 0.74), -70 + 140 * i / 12.0)
        zz.append((q[0], q[1], 'c'))
    for i, p in enumerate(inner):
        q = _ell(ccx, ccy, crx * (0.66 if i % 2 else 0.70), cry * (0.66 if i % 2 else 0.70), 70 - 140 * i / 12.0)
        zz.append((q[0], q[1], 'c'))
    cv.fill(polyline(zz, closed=True), hh, 1.0, clip=hm)
    # --- lock lines: from each valley between spikes down toward the hairline --
    for i in range(len(spikes) - 1):
        a = (spikes[i][0] + spikes[i + 1][0]) / 2.0
        v = _ell(ccx, ccy, crx, cry, a)                       # valley point on the cap
        e = _ell(ccx, ccy, crx * 0.62, cry * 0.62, a * 0.8)  # end lower inside the mass
        mid = ((v[0] + e[0]) / 2 - a * 0.10, (v[1] + e[1]) / 2)
        cv.stroke(smooth([v, mid, e], closed=False), hl, [(0, 2.8), (1, 0.5)], alpha=0.9, clip=hm)
        # a darker sliver on the shaded side of each valley
        cv.stroke(smooth([(v[0] + 4, v[1] + 2), (mid[0] + 5, mid[1]), (e[0] + 3, e[1])], closed=False), hs, [(0, 5.0), (1, 1.0)], alpha=0.9, clip=hm)
    # short bangs poking down at the temples and centre
    for s in (-1, 1):
        t = smooth([(cx + s * rx * 0.80, 162, 'c'), (cx + s * rx * 0.98, 178), (cx + s * rx * 1.0, 214, 'c'),
                    (cx + s * rx * 0.90, 196), (cx + s * rx * 0.70, 178, 'c')])
        cv.shape(t, hc, hl, 2.4, shadows=[(_box(cx + s * rx * 0.85 - 40, 150, cx + s * rx * 0.85 + 40, 230), hs)])
        t2 = smooth([(cx + s * rx * 0.50, 158, 'c'), (cx + s * rx * 0.62, 176), (cx + s * rx * 0.60, 198, 'c'),
                     (cx + s * rx * 0.50, 182), (cx + s * rx * 0.36, 166, 'c')])
        cv.shape(t2, hc, hl, 2.2, shadows=[(_box(cx + s * rx * 0.3, 176, cx + s * rx * 0.8, 230), hs, 0.9)])
    cf = smooth([(cx - rx * 0.16, 156, 'c'), (cx - rx * 0.06, 176), (cx - rx * 0.02, 200, 'c'), (cx + rx * 0.06, 176),
                 (cx + rx * 0.16, 156, 'c')])
    cv.shape(cf, hc, hl, 2.4, shadows=[(_box(cx, 150, cx + 40, 220), hs, 0.9)])
    # lock separation lines inside the mass
    for (x0, y0, x1, y1) in ((cx - rx * 0.78, 168, cx - rx * 0.86, 128), (cx + rx * 0.74, 168, cx + rx * 0.84, 126),
                             (cx - rx * 0.22, 160, cx - rx * 0.28, 124), (cx + rx * 0.44, 158, cx + rx * 0.50, 124)):
        cv.stroke(smooth([(x0, y0), ((x0 + x1) / 2 - 3, (y0 + y1) / 2), (x1, y1)], closed=False), hl, [(0, 2.4), (1, 0.6)], alpha=0.85)


HAIR_STYLES = {'yuji': draw_hair_yuji}


# =============================================================================
# main entry
# =============================================================================
def render_character(spec, expression='neutral'):
    """Render one character (front view, full body) -> raster.Img 760x1400 RGBA."""
    if expression not in EXPRESSIONS:
        raise ValueError("unknown expression %r (want one of %s)" % (expression, EXPRESSIONS))
    img = Img(W, H, alpha=True)
    cv = Canvas(img)
    F = Fig(spec)
    LINE = C(spec.get('line', '#241a1e'))
    skin = C(spec.get('skin', '#f1c9a5'))
    skin_sh = C(spec.get('skin_shadow', '#d9a17e'))
    draw_legs(cv, F, spec, LINE)
    draw_torso(cv, F, spec, LINE, skin, skin_sh)
    head_mask = draw_head_base(cv, F, spec, LINE, skin, skin_sh)
    draw_face(cv, F, spec, expression, LINE, skin, skin_sh)
    style = spec.get('hair', {}).get('style', 'yuji')
    HAIR_STYLES[style](cv, F, spec, LINE, head_mask, skin_sh)
    return img


YUJI = {
    'name': 'yuji',
    'skin': '#f2cba6',
    'skin_shadow': '#d9a07c',
    'line': '#2a1b1f',
    'brow_color': '#3d2624',
    'brow_weight': 1.15,
    'eye_marks': True,
    'eye_mark_color': '#5b3632',
    'eyes': {'color': '#8a5326', 'dark': '#4b2a10', 'light': '#c98d4c', 'width': 1.0, 'height': 1.0, 'iris': 1.0},
    'hair': {'style': 'yuji', 'color': '#f4a3a6', 'shadow': '#d8737d', 'line': '#5a2b36',
             'highlight': '#fbcbc9', 'undercut': '#3c2c2d', 'undercut_line': '#1f1517'},
    'outfit': {'jacket': '#232838', 'jacket_shadow': '#141726', 'jacket_light': '#3a4261', 'trim': '#5a6285',
               'hoodie': '#c9313b', 'hoodie_shadow': '#8a1e27', 'hoodie_light': '#e0474f', 'hood': True,
               'pants': '#262a3c', 'pants_shadow': '#161928', 'shoes': '#f3f3f1', 'shoes_shadow': '#cbcdd4', 'sole': '#8b8e98'},
    'build': {'shoulder': 1.0, 'bulk': 1.0, 'head': 1.0},
}


if __name__ == '__main__':
    import time
    out_dir = os.path.join(os.path.dirname(_TOOLS), 'game', 'images', 'char')
    os.makedirs(out_dir, exist_ok=True)
    exprs = sys.argv[1:] or ['neutral', 'happy']
    for expr in exprs:
        fname = '_test_yuji_A.png' if expr == 'neutral' else '_test_yuji_A_%s.png' % expr
        t0 = time.time()
        img = render_character(YUJI, expr)
        path = os.path.join(out_dir, fname)
        img.save(path)
        print("%s  %.1fs" % (path, time.time() - t0))
