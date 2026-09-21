"""Tiny dependency-free raster + PNG writer used to generate placeholder art."""
import zlib, struct, math, random


def hexc(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Img(object):
    def __init__(self, w, h, alpha=False, fill=(0, 0, 0)):
        self.w, self.h = w, h
        self.ch = 4 if alpha else 3
        if alpha:
            self.buf = bytearray(w * h * 4)
        else:
            self.buf = bytearray(bytes(fill) * (w * h))

    # --- low level -------------------------------------------------------
    def blend(self, x, y, color, a):
        if a <= 0.0 or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        if a > 1.0:
            a = 1.0
        i = (y * self.w + x) * self.ch
        b = self.buf
        if self.ch == 4:
            da = b[i + 3] / 255.0
            na = a + da * (1 - a)
            if na <= 0:
                return
            for k in range(3):
                src = color[k] * a
                dst = b[i + k] * da * (1 - a)
                b[i + k] = int(max(0, min(255, (src + dst) / na)))
            b[i + 3] = int(na * 255)
        else:
            for k in range(3):
                b[i + k] = int(b[i + k] + (color[k] - b[i + k]) * a)

    def row_fill(self, y, x0, x1, color, a=1.0):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, int(x0)); x1 = min(self.w, int(x1))
        if x1 <= x0:
            return
        if a >= 1.0 and self.ch == 3:
            i = (y * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)
        else:
            for x in range(x0, x1):
                self.blend(x, y, color, a)

    # --- shapes ----------------------------------------------------------
    def vgrad(self, x0, y0, x1, y1, c0, c1, a=1.0, gamma=1.0):
        y0, y1 = int(y0), int(y1)
        span = max(1, y1 - y0)
        for y in range(max(0, y0), min(self.h, y1)):
            t = ((y - y0) / span) ** gamma
            self.row_fill(y, x0, x1, lerp(c0, c1, t), a)

    def hgrad(self, x0, y0, x1, y1, c0, c1, a=1.0):
        x0, x1 = int(x0), int(x1)
        span = max(1, x1 - x0)
        for x in range(max(0, x0), min(self.w, x1)):
            c = lerp(c0, c1, (x - x0) / span)
            for y in range(max(0, int(y0)), min(self.h, int(y1))):
                self.blend(x, y, c, a)

    def rect(self, x0, y0, x1, y1, color, a=1.0):
        for y in range(max(0, int(y0)), min(self.h, int(y1))):
            self.row_fill(y, x0, x1, color, a)

    def ellipse(self, cx, cy, rx, ry, color, a=1.0, soft=2.0, ymin=None, ymax=None):
        x0, x1 = int(cx - rx - 2), int(cx + rx + 3)
        y0, y1 = int(cy - ry - 2), int(cy + ry + 3)
        if ymin is not None:
            y0 = max(y0, int(ymin))
        if ymax is not None:
            y1 = min(y1, int(ymax))
        edge = max(1.0, soft) / max(rx, ry)
        for y in range(max(0, y0), min(self.h, y1)):
            dy = (y - cy) / ry
            for x in range(max(0, x0), min(self.w, x1)):
                dx = (x - cx) / rx
                d = math.sqrt(dx * dx + dy * dy)
                if d > 1.0 + edge:
                    continue
                cov = min(1.0, max(0.0, (1.0 + edge - d) / (2 * edge)))
                self.blend(x, y, color, a * cov)

    def rrect(self, x0, y0, x1, y1, r, color, a=1.0, soft=1.5):
        for y in range(max(0, int(y0 - 2)), min(self.h, int(y1 + 2))):
            for x in range(max(0, int(x0 - 2)), min(self.w, int(x1 + 2))):
                dx = max(x0 + r - x, 0, x - (x1 - r))
                dy = max(y0 + r - y, 0, y - (y1 - r))
                d = math.sqrt(dx * dx + dy * dy) - r
                if d > soft:
                    continue
                cov = min(1.0, max(0.0, (soft - d) / (2 * soft) + 0.5))
                self.blend(x, y, color, a * cov)

    def poly(self, pts, color, a=1.0):
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h, int(max(ys)) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.row_fill(y, xs[i], xs[i + 1] + 1, color, a)

    def glow(self, cx, cy, r, color, strength=0.6, power=2.0):
        x0, x1 = int(cx - r), int(cx + r + 1)
        y0, y1 = int(cy - r), int(cy + r + 1)
        for y in range(max(0, y0), min(self.h, y1)):
            dy = y - cy
            for x in range(max(0, x0), min(self.w, x1)):
                dx = x - cx
                d = math.sqrt(dx * dx + dy * dy) / r
                if d >= 1.0:
                    continue
                self.blend(x, y, color, strength * ((1.0 - d) ** power))

    def vignette(self, strength=0.55, power=1.6):
        cx, cy = self.w / 2.0, self.h / 2.0
        m = math.sqrt(cx * cx + cy * cy)
        b = self.buf
        for y in range(self.h):
            dy = (y - cy) ** 2
            for x in range(self.w):
                d = math.sqrt(dy + (x - cx) ** 2) / m
                f = 1.0 - strength * (d ** power)
                i = (y * self.w + x) * self.ch
                b[i] = int(b[i] * f)
                b[i + 1] = int(b[i + 1] * f)
                b[i + 2] = int(b[i + 2] * f)

    def grain(self, amount=7, step=1, seed=3):
        rnd = random.Random(seed)
        b = self.buf
        for y in range(0, self.h, step):
            for x in range(0, self.w, step):
                n = rnd.randint(-amount, amount)
                i = (y * self.w + x) * self.ch
                for k in range(3):
                    b[i + k] = max(0, min(255, b[i + k] + n))

    def save(self, path):
        raw = bytearray()
        stride = self.w * self.ch
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 6)

        def chunk(tag, data):
            c = struct.pack('>I', len(data)) + tag + data
            return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

        ihdr = struct.pack('>IIBBBBB', self.w, self.h, 8, 6 if self.ch == 4 else 2, 0, 0, 0)
        with open(path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')
            f.write(chunk(b'IHDR', ihdr))
            f.write(chunk(b'IDAT', comp))
            f.write(chunk(b'IEND', b''))


# --- compositing helpers (added for the sprite pipeline) --------------------

def crop(im, x0, y0, x1, y1):
    """Return a new Img holding the rectangle [x0,x1) x [y0,y1) of `im`."""
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(im.w, int(x1)), min(im.h, int(y1))
    out = Img(x1 - x0, y1 - y0, alpha=(im.ch == 4))
    ch = im.ch
    for y in range(y0, y1):
        src = (y * im.w + x0) * ch
        dst = ((y - y0) * out.w) * ch
        out.buf[dst:dst + (x1 - x0) * ch] = im.buf[src:src + (x1 - x0) * ch]
    return out


def paste(dst, src, x, y):
    """Alpha-composite `src` (RGBA) onto `dst` at (x, y)."""
    for sy in range(src.h):
        dy = y + sy
        if dy < 0 or dy >= dst.h:
            continue
        for sx in range(src.w):
            dx = x + sx
            if dx < 0 or dx >= dst.w:
                continue
            i = (sy * src.w + sx) * src.ch
            a = src.buf[i + 3] / 255.0 if src.ch == 4 else 1.0
            if a <= 0:
                continue
            dst.blend(dx, dy, (src.buf[i], src.buf[i + 1], src.buf[i + 2]), a)


def _weights(n_src, n_dst):
    """For each destination index, the (source index, weight) pairs it covers.

    Area coverage when shrinking, linear interpolation when enlarging.
    """
    f = n_dst / float(n_src)
    out = []
    if f < 1.0:
        span = 1.0 / f
        for d in range(n_dst):
            a, b = d * span, (d + 1) * span
            ws, i = [], int(a)
            while i < b and i < n_src:
                w = min(b, i + 1) - max(a, i)
                if w > 1e-6:
                    ws.append((i, w / span))
                i += 1
            out.append(ws)
    else:
        for d in range(n_dst):
            x = (d + 0.5) / f - 0.5
            i0 = max(0, min(n_src - 1, int(x))); i1 = min(n_src - 1, i0 + 1)
            t = max(0.0, min(1.0, x - i0))
            out.append([(i0, 1 - t), (i1, t)] if i1 != i0 else [(i0, 1.0)])
    return out


def resample(im, w2, h2):
    """Resize to w2 x h2 by area averaging (shrink) or bilinear (enlarge).

    RGBA is averaged premultiplied: a half-transparent edge pixel contributes
    half its colour, so the colour hidden under transparent pixels -- keyed
    backdrop -- cannot bleed a fringe into the edge.
    """
    ch = im.ch
    alpha = ch == 4
    wx, wy = _weights(im.w, w2), _weights(im.h, h2)
    # horizontal pass into floats
    tmp = [0.0] * (w2 * im.h * ch)
    for y in range(im.h):
        row = y * im.w * ch
        for x in range(w2):
            acc = [0.0] * ch
            for i, wt in wx[x]:
                j = row + i * ch
                if alpha:
                    a = im.buf[j + 3] * wt
                    acc[0] += im.buf[j] * a; acc[1] += im.buf[j + 1] * a
                    acc[2] += im.buf[j + 2] * a; acc[3] += a
                else:
                    for k in range(ch):
                        acc[k] += im.buf[j + k] * wt
            t = (y * w2 + x) * ch
            tmp[t:t + ch] = acc
    out = Img(w2, h2, alpha=alpha)
    for y in range(h2):
        for x in range(w2):
            acc = [0.0] * ch
            for i, wt in wy[y]:
                t = (i * w2 + x) * ch
                for k in range(ch):
                    acc[k] += tmp[t + k] * wt
            j = (y * w2 + x) * ch
            if alpha:
                a = acc[3]
                if a > 0.5:
                    out.buf[j] = min(255, int(acc[0] / a + 0.5))
                    out.buf[j + 1] = min(255, int(acc[1] / a + 0.5))
                    out.buf[j + 2] = min(255, int(acc[2] / a + 0.5))
                    out.buf[j + 3] = min(255, int(a + 0.5))
            else:
                for k in range(ch):
                    out.buf[j + k] = min(255, int(acc[k] + 0.5))
    return out


def smooth_scale(im, factor):
    """Proportional resize with proper filtering -- use this for final art."""
    return resample(im, max(1, int(im.w * factor)), max(1, int(im.h * factor)))


def scale(im, factor):
    """Nearest-neighbour resample (fast, adequate for thumbnails)."""
    w2, h2 = max(1, int(im.w * factor)), max(1, int(im.h * factor))
    out = Img(w2, h2, alpha=(im.ch == 4))
    ch = im.ch
    for y in range(h2):
        sy = min(im.h - 1, int(y / factor))
        for x in range(w2):
            sx = min(im.w - 1, int(x / factor))
            i, j = (sy * im.w + sx) * ch, (y * w2 + x) * ch
            out.buf[j:j + ch] = im.buf[i:i + ch]
    return out
