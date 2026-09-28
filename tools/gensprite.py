import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game", "images", "char")
os.makedirs(OUT, exist_ok=True)
W, H = 760, 1400
CX = W / 2.0


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


# ---------------------------------------------------------------- hair
def cap(im, cx, hy, rx, ry, c):
    """Skull cap of hair covering only the top of the head."""
    im.ellipse(cx, hy - ry * 0.04, rx * 1.07, ry * 1.02, c, ymax=hy + ry * 0.06)


def fringe(im, cx, hy, rx, ry, c, points=5, drop=0.34, seed=1):
    """Angular anime bangs hanging over the forehead."""
    rnd = random.Random(seed)
    pts = [(cx - rx * 1.04, hy - ry * 0.55)]
    for i in range(points * 2 + 1):
        t = i / float(points * 2)
        x = cx - rx * 1.04 + rx * 2.08 * t
        y = hy + ry * (drop if i % 2 == 0 else drop * 0.30) * rnd.uniform(0.82, 1.18)
        pts.append((x, y))
    pts.append((cx + rx * 1.04, hy - ry * 0.55))
    im.poly(pts, c)


def hair_spiky(im, cx, hy, rx, ry, c, n=9, length=0.95, seed=2, side=0.0):
    cap(im, cx, hy, rx, ry, c)
    rnd = random.Random(seed)
    for i in range(n):
        t = i / float(n - 1)
        a = math.pi * (0.10 + 0.80 * t)
        bx = cx - math.cos(a) * rx * 0.95
        by = hy - math.sin(a) * ry * 0.86
        l = ry * length * (0.45 + 0.85 * math.sin(math.pi * t)) * rnd.uniform(0.82, 1.14)
        tipx = bx - math.cos(a) * l * 0.55 + side * l
        tipy = by - math.sin(a) * l
        w = rx * 0.20
        im.poly([(bx - w, by + 16), (tipx, tipy), (bx + w, by + 16)], c)
    fringe(im, cx, hy, rx, ry, c, points=4, drop=0.24, seed=seed + 5)


def hair_bob(im, cx, hy, rx, ry, c, **kw):
    cap(im, cx, hy, rx, ry, c)
    im.rrect(cx - rx * 1.14, hy - ry * 0.42, cx - rx * 0.56, hy + ry * 1.02, 30, c)
    im.rrect(cx + rx * 0.56, hy - ry * 0.42, cx + rx * 1.14, hy + ry * 1.02, 30, c)
    fringe(im, cx, hy, rx, ry, c, points=4, drop=0.28, seed=8)


def hair_ponytail(im, cx, hy, rx, ry, c, **kw):
    cap(im, cx, hy, rx, ry, c)
    im.rrect(cx + rx * 0.80, hy - ry * 0.55, cx + rx * 1.46, hy + ry * 2.10, 32, c)
    im.ellipse(cx + rx * 1.13, hy + ry * 2.15, rx * 0.34, ry * 0.44, c)
    fringe(im, cx, hy, rx, ry, c, points=3, drop=0.20, seed=11)


def hair_swept(im, cx, hy, rx, ry, c, **kw):
    cap(im, cx, hy, rx, ry, c)
    im.poly([(cx - rx * 1.12, hy - ry * 0.25), (cx + rx * 1.12, hy - ry * 0.48),
             (cx + rx * 0.86, hy - ry * 1.02), (cx - rx * 0.98, hy - ry * 0.72)], c)
    fringe(im, cx, hy, rx, ry, c, points=3, drop=0.22, seed=14)


def hair_panda(im, cx, hy, rx, ry, c, **kw):
    im.ellipse(cx, hy - ry * 0.10, rx * 1.12, ry * 1.02, c, ymax=hy + ry * 0.10)
    im.ellipse(cx - rx * 0.94, hy - ry * 0.90, rx * 0.40, ry * 0.40, c)
    im.ellipse(cx + rx * 0.94, hy - ry * 0.90, rx * 0.40, ry * 0.40, c)


def hair_buzz(im, cx, hy, rx, ry, c, **kw):
    im.ellipse(cx, hy - ry * 0.16, rx * 1.02, ry * 0.94, c, ymax=hy + ry * 0.02)


HAIR = {"spiky": hair_spiky, "bob": hair_bob, "ponytail": hair_ponytail,
        "swept": hair_swept, "panda": hair_panda, "buzz": hair_buzz}


# ---------------------------------------------------------------- figure
# Standing height in cm, and the tallest member of the cast that the canvas is
# sized for. Kept in step with tools/keysprite.py — placeholders and finished
# art have to agree about how tall everyone is, or the cast changes height as
# each real sprite lands.
HEIGHT_CM = {
    "yuji": 173, "megumi": 175, "nobara": 160, "maki": 180, "panda": 200,
    "toge": 176, "shoko": 180, "gojo": 195, "yaga": 191, "ijichi": 175,
    "utahime": 167, "sana": 160, "mc": 172,
}
TALLEST_CM = 200.0


def person(name, skin, hair_c, hair_style, uniform, accent, aura, scale=1.0,
           glasses=None, collar_up=False, **hair_kw):
    im = Img(W, H, alpha=True)

    # `scale` is mass — how broad the character is. Height is separate, and is
    # taken from the cast table so the figures stand in correct proportion to
    # each other. Widths follow height at a softened rate; scaling a short
    # character down uniformly gives them a doll's head.
    hf = HEIGHT_CM.get(name, 173) / TALLEST_CM
    wf = scale * (hf ** 0.5)

    foot_y = H * 0.995
    def up(frac):
        """A landmark at `frac` of the full canvas, pulled down toward the feet."""
        return foot_y - (foot_y - H * frac) * hf

    hy = up(0.125)
    rx, ry = 104 * wf, 118 * wf
    sh_y = up(0.268)
    hip_y = up(0.615)
    sh_w = 152 * wf
    hip_w = 114 * wf

    uni_hi = shade(uniform, 1.18)
    uni_lo = shade(uniform, 0.66)
    pant = shade(uniform, 0.52)

    im.glow(CX, H * 0.50, 520 * wf, aura, 0.26, 2.0)
    im.glow(CX, hy + 30, 300 * wf, aura, 0.20, 2.1)

    # legs
    for sgn in (-1, 1):
        x = CX + sgn * hip_w * 0.42
        im.rrect(x - 48 * wf, hip_y - 30, x + 48 * wf, foot_y, 36, pant)
    im.rect(CX - 5, hip_y + 60, CX + 5, foot_y - 30, shade(uniform, 0.34))
    for sgn in (-1, 1):
        x = CX + sgn * hip_w * 0.42
        im.rrect(x - 52 * wf, foot_y - 44, x + 50 * wf, foot_y, 16, shade(uniform, 0.30))

    # arms (behind torso)
    for sgn in (-1, 1):
        x = CX + sgn * (sh_w - 22 * wf)
        im.rrect(x - 34 * wf, sh_y - 4, x + 34 * wf, hip_y + 26, 34, uni_lo)
        im.ellipse(x, hip_y + 50, 31 * wf, 37 * wf, skin)

    # torso
    im.poly([(CX - sh_w, sh_y + 20), (CX - sh_w * 0.86, sh_y - 8),
             (CX + sh_w * 0.86, sh_y - 8), (CX + sh_w, sh_y + 20),
             (CX + hip_w, hip_y + 24), (CX - hip_w, hip_y + 24)], uniform)
    # jacket seam + thin accent trim
    im.poly([(CX - 12, sh_y), (CX + 12, sh_y), (CX + 8, hip_y + 20), (CX - 8, hip_y + 20)], shade(uniform, 0.42))
    im.poly([(CX - 40 * wf, sh_y + 4), (CX - 22 * wf, sh_y + 4),
             (CX - 14 * wf, hip_y + 18), (CX - 28 * wf, hip_y + 18)], accent, 0.95)
    im.rect(CX - hip_w * 1.02, hip_y - 6, CX + hip_w * 1.02, hip_y + 26, uni_lo)
    im.rect(CX - 34 * wf, hip_y + 2, CX + 34 * wf, hip_y + 20, accent, 0.9)

    # neck
    im.rrect(CX - 30 * wf, hy + ry * 0.66, CX + 30 * wf, sh_y + 10, 16, shade(skin, 0.78))
    # collar
    if collar_up:
        im.poly([(CX - 84 * wf, sh_y + 34), (CX + 84 * wf, sh_y + 34),
                 (CX + 62 * wf, sh_y - 72 * wf), (CX - 62 * wf, sh_y - 72 * wf)], uni_hi)
        im.rect(CX - 62 * wf, sh_y - 72 * wf, CX + 62 * wf, sh_y - 60 * wf, accent, 0.9)
    else:
        im.poly([(CX - 88 * wf, sh_y - 4), (CX + 88 * wf, sh_y - 4),
                 (CX + 24 * wf, sh_y + 62), (CX - 24 * wf, sh_y + 62)], uni_hi)

    # head
    im.ellipse(CX, hy, rx, ry, skin)
    im.poly([(CX - rx * 0.80, hy + ry * 0.40), (CX + rx * 0.80, hy + ry * 0.40),
             (CX, hy + ry * 1.08)], skin)

    # eyes, then hair on top
    ey = hy + ry * 0.44
    if glasses:
        for sgn in (-1, 1):
            gx = CX + sgn * rx * 0.46
            im.rrect(gx - rx * 0.40, ey - 17, gx + rx * 0.40, ey + 15, 10, glasses, 0.94)
        im.rect(CX - rx * 0.10, ey - 4, CX + rx * 0.10, ey + 2, glasses, 0.94)
    else:
        for sgn in (-1, 1):
            ex = CX + sgn * rx * 0.42
            im.rrect(ex - 17 * wf, ey - 8, ex + 17 * wf, ey + 12, 8, shade(skin, 0.30))
            im.rrect(ex - 17 * wf, ey - 14, ex + 17 * wf, ey - 8, 3, shade(hair_c, 0.7))

    HAIR[hair_style](im, CX, hy, rx, ry, hair_c, **hair_kw)

    im.save(os.path.join(OUT, name + ".png"))
    print("  ", name)


def curse(name, body, glow_c, eyes=3, seed=1, scale=1.0):
    im = Img(W, H, alpha=True)
    rnd = random.Random(seed)
    im.glow(CX, H * 0.5, 520 * scale, glow_c, 0.32, 2.0)
    for i in range(26):
        a = rnd.uniform(0, 6.283)
        r = rnd.uniform(0, 180) * scale
        x = CX + math.cos(a) * r
        y = H * 0.54 + math.sin(a) * r * 1.5
        im.ellipse(x, y, rnd.uniform(90, 200) * scale, rnd.uniform(110, 250) * scale,
                   shade(body, rnd.uniform(0.7, 1.15)), 0.94)
    for i in range(eyes):
        x = CX + rnd.uniform(-150, 150) * scale
        y = H * (0.34 + rnd.uniform(-0.05, 0.13))
        rr = rnd.uniform(26, 46) * scale
        im.glow(x, y, rr * 4.5, glow_c, 0.38, 2.0)
        im.ellipse(x, y, rr, rr, glow_c)
        im.ellipse(x, y, rr * 0.40, rr * 0.62, (8, 5, 10))
    for i in range(44):
        x = CX + rnd.uniform(-250, 250) * scale
        y = H * 0.5 + rnd.uniform(-340, 340) * scale
        im.ellipse(x, y, rnd.uniform(3, 10), rnd.uniform(3, 10), glow_c, rnd.uniform(0.2, 0.7))
    im.save(os.path.join(OUT, name + ".png"))
    print("  ", name)


CAST = [
    ("mc",      "e3b892", "6b5aa8", "swept",    "2b2b33", "a259ff", "a259ff", dict(collar_up=True)),
    ("yuji",    "e3b892", "f2748c", "spiky",    "2b2b33", "d9536e", "ff8fa3", dict(n=9,  length=0.80, seed=3)),
    ("megumi",  "f0cdb0", "1b2233", "spiky",    "2b2b33", "39507a", "6f8fd0", dict(n=12, length=1.05, seed=6, collar_up=True)),
    ("nobara",  "f0cdb0", "c96a2e", "bob",      "2b2b33", "e0873f", "ffb066", dict()),
    ("maki",    "e3b892", "2f5d43", "ponytail", "2b2b33", "3d8f5f", "77e0a0", dict(glasses="b03a3a")),
    ("panda",   "f2f2ee", "efefe9", "panda",    "1a1a1e", "3a3a42", "d8d8e8", dict(scale=1.18)),
    ("toge",    "f0cdb0", "d8dfe2", "swept",    "2b2b33", "8fa6ad", "bfe3ea", dict(collar_up=True)),
    ("gojo",    "f0cdb0", "f2f4f8", "spiky",    "2b2b33", "6f8fd0", "8ed6ff", dict(scale=1.10, n=11, length=0.92, seed=21, glasses="14161f", collar_up=True)),
    ("yaga",    "c99a72", "14141a", "buzz",     "2a2f38", "4a5260", "b0b8c8", dict(scale=1.22, glasses="2a2f38")),
    ("ijichi",  "e3b892", "2a2a30", "swept",    "32323a", "55555f", "9aa0b0", dict(glasses="222228")),
    ("shoko",   "f0cdb0", "6b4a33", "bob",      "d8d8d2", "8a6a4a", "e0c8b0", dict()),
    ("utahime", "f0cdb0", "2e2440", "ponytail", "e2e2de", "c0392b", "d9a0c0", dict()),
    ("sana",    "e8c49c", "1e1e26", "ponytail", "5a5f6b", "c0392b", "ffd9a0", dict()),
]

if __name__ == "__main__":
    print("sprites ->", OUT)
    for name, skin, hair, style, uni, acc, aura, kw in CAST:
        if "glasses" in kw:
            kw = dict(kw); kw["glasses"] = hexc(kw["glasses"])
        person(name, hexc(skin), hexc(hair), style, hexc(uni), hexc(acc), hexc(aura), **kw)
    curse("curse_small", hexc("2c4a36"), hexc("6cff9e"), eyes=2, seed=4, scale=0.75)
    curse("curse_big", hexc("3a1f4a"), hexc("ff5f8a"), eyes=4, seed=9, scale=1.15)
