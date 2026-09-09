"""
Cel-shaded anime character renderer — pure Python, no image libraries.

Everything is drawn into a 2x supersampled buffer and box-downsampled at the
end, which is what gives the line art clean edges. Shapes are closed paths
(polylines, usually produced by flattening cubic beziers); every visible region
is drawn twice — once dilated in the line colour to make an outline, then the
fill on top.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp

SS = 2                      # supersample factor
W, H = 760, 1400            # output size


# ---------------------------------------------------------------- geometry
def bez(p0, p1, p2, p3, steps=24):
    """Flatten a cubic bezier to a polyline."""
    out = []
    for i in range(steps + 1):
        t = i / float(steps)
        u = 1 - t
        x = u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0]
        y = u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]
        out.append((x, y))
    return out


def curve(pts, steps=20):
    """Catmull-Rom through pts -> smooth polyline (endpoints duplicated)."""
    if len(pts) < 3:
        return list(pts)
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(len(p) - 3):
        p0, p1, p2, p3 = p[i], p[i+1], p[i+2], p[i+3]
        for s in range(steps):
            t = s / float(steps)
            t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n)


def dilate(pts, amount):
    """Push every point away from the centroid — a cheap outline offset."""
    cx, cy = centroid(pts)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1.0
        out.append((x + dx/d*amount, y + dy/d*amount))
    return out


def offset_along(pts, amount):
    """Outline offset using local normals — better than dilate for long shapes."""
    n = len(pts)
    out = []
    for i in range(n):
        x0, y0 = pts[(i - 1) % n]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        dx, dy = x2 - x0, y2 - y0
        d = math.hypot(dx, dy) or 1.0
        nx, ny = dy/d, -dx/d          # left normal
        out.append((x1 + nx*amount, y1 + ny*amount))
    # keep winding consistent: if the offset shrank the shape, flip
    if _area(out) < _area(pts):
        out = [(pts[i][0] - (out[i][0]-pts[i][0]), pts[i][1] - (out[i][1]-pts[i][1])) for i in range(n)]
    return out


def _area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i+1) % n]
        a += x1*y2 - x2*y1
    return abs(a) * 0.5


# ---------------------------------------------------------------- canvas
class Cel(object):
    """A supersampled RGBA drawing surface."""

    def __init__(self, w=W, h=H, line="#241d33"):
        self.w, self.h = w, h
        self.im = Img(w * SS, h * SS, alpha=True)
        self.line = hexc(line)

    def s(self, v):
        return v * SS

    # -- primitives (all take 1x coordinates) --------------------------------
    def poly(self, pts, color, a=1.0):
        self.im.poly([(x*SS, y*SS) for x, y in pts], color, a)

    def outlined(self, pts, fill, lw=3.0, line=None, a=1.0):
        """Fill a closed path with a line-art outline around it."""
        self.im.poly([(x*SS, y*SS) for x, y in offset_along(pts, lw)], line or self.line, a)
        self.im.poly([(x*SS, y*SS) for x, y in pts], fill, a)

    def ellipse(self, cx, cy, rx, ry, color, a=1.0, soft=2.0, ymin=None, ymax=None):
        self.im.ellipse(cx*SS, cy*SS, rx*SS, ry*SS, color, a, soft*SS,
                        None if ymin is None else ymin*SS,
                        None if ymax is None else ymax*SS)

    def outlined_ellipse(self, cx, cy, rx, ry, fill, lw=3.0, line=None, a=1.0):
        self.ellipse(cx, cy, rx+lw, ry+lw, line or self.line, a)
        self.ellipse(cx, cy, rx, ry, fill, a)

    def rrect(self, x0, y0, x1, y1, r, color, a=1.0, soft=1.5):
        self.im.rrect(x0*SS, y0*SS, x1*SS, y1*SS, r*SS, color, a, soft*SS)

    def stroke(self, pts, width, color=None, a=1.0):
        """Thick polyline: a quad per segment plus a dot at each joint."""
        c = color or self.line
        hw = width * 0.5
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            dx, dy = x2-x1, y2-y1
            d = math.hypot(dx, dy)
            if d < 1e-6:
                continue
            nx, ny = -dy/d*hw, dx/d*hw
            self.poly([(x1+nx, y1+ny), (x2+nx, y2+ny), (x2-nx, y2-ny), (x1-nx, y1-ny)], c, a)
        for x, y in pts:
            self.ellipse(x, y, hw, hw, c, a, soft=1.0)

    def taper(self, pts, w_start, w_end, color=None, a=1.0):
        """Polyline whose width eases from w_start to w_end — hair strands."""
        c = color or self.line
        n = len(pts) - 1
        for i in range(n):
            t0, t1 = i/float(n), (i+1)/float(n)
            hw0 = (w_start + (w_end-w_start)*t0) * 0.5
            hw1 = (w_start + (w_end-w_start)*t1) * 0.5
            x1, y1 = pts[i]
            x2, y2 = pts[i+1]
            dx, dy = x2-x1, y2-y1
            d = math.hypot(dx, dy)
            if d < 1e-6:
                continue
            nx, ny = -dy/d, dx/d
            self.poly([(x1+nx*hw0, y1+ny*hw0), (x2+nx*hw1, y2+ny*hw1),
                       (x2-nx*hw1, y2-ny*hw1), (x1-nx*hw0, y1-ny*hw0)], c, a)

    def glow(self, cx, cy, r, color, strength=0.3, power=2.0):
        self.im.glow(cx*SS, cy*SS, r*SS, color, strength, power)

    # -- output ---------------------------------------------------------------
    def resolve(self):
        """Box-downsample the supersampled buffer to the output size."""
        out = Img(self.w, self.h, alpha=True)
        src, dst = self.im.buf, out.buf
        sw = self.w * SS
        n = SS * SS
        for y in range(self.h):
            base = y * self.w * 4
            for x in range(self.w):
                r = g = b = al = 0
                for oy in range(SS):
                    row = ((y*SS + oy) * sw + x*SS) * 4
                    for ox in range(SS):
                        i = row + ox*4
                        av = src[i+3]
                        r += src[i] * av
                        g += src[i+1] * av
                        b += src[i+2] * av
                        al += av
                j = base + x*4
                if al:
                    dst[j] = r // al
                    dst[j+1] = g // al
                    dst[j+2] = b // al
                    dst[j+3] = al // n
        return out

    def save(self, path):
        self.resolve().save(path)
