"""Backgrounds + map art for the sandbox build."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "images", "bg")
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080


def finish(im, name, vig=0.5, grain=6):
    im.vignette(vig)
    if grain:
        im.grain(grain, 2, seed=abs(hash(name)) % 999)
    im.save(os.path.join(OUT, name + ".png"))
    print("  ", name)


def treeline(im, base_y, height, color, seed, alpha=1.0, count=46):
    rnd = random.Random(seed)
    for i in range(count):
        x = -40 + (W + 80) * i / float(count - 1) + rnd.uniform(-14, 14)
        h = height * rnd.uniform(0.62, 1.35)
        w = h * rnd.uniform(0.14, 0.26)
        im.poly([(x - w, base_y), (x, base_y - h), (x + w, base_y)], color, alpha)


def hills(im, base_y, amp, color, seed, alpha=1.0, step=24):
    rnd = random.Random(seed)
    pts = [(-20, H + 40)]
    x = -20
    ph = rnd.random() * 6.28
    while x <= W + 20:
        y = base_y + math.sin(x / 260.0 + ph) * amp + math.sin(x / 77.0 + ph * 2) * amp * 0.28
        pts.append((x, y))
        x += step
    pts.append((W + 20, H + 40))
    im.poly(pts, color, alpha)


# ---------------------------------------------------------------- locations
def bg_dorm_common():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("3a2f34"), hexc("1a1418"))
    im.rect(0, 0, W, H * 0.68, hexc("43363c"))
    im.rect(0, H * 0.66, W, H * 0.70, hexc("2a2126"))
    im.rect(0, H * 0.68, W, H, hexc("53412e"))
    for i in range(9):
        y = H * 0.72 + i * H * 0.04
        im.rect(0, y, W, y + 3, hexc("42331f"), 0.7)
    # couch + low table + tv
    im.rrect(W * 0.06, H * 0.55, W * 0.42, H * 0.86, 18, hexc("6a4550"))
    im.rrect(W * 0.08, H * 0.50, W * 0.40, H * 0.60, 16, hexc("7d5260"))
    im.rrect(W * 0.47, H * 0.68, W * 0.72, H * 0.80, 8, hexc("4a3826"))
    im.rrect(W * 0.78, H * 0.30, W * 0.97, H * 0.58, 6, hexc("14121a"))
    im.rrect(W * 0.79, H * 0.315, W * 0.96, H * 0.565, 4, hexc("2b3a52"))
    im.glow(W * 0.875, H * 0.44, 420, hexc("7fa8e0"), 0.22, 2.0)
    im.glow(W * 0.25, H * 0.20, 560, hexc("ffcf96"), 0.20, 2.2)
    finish(im, "dorm_common", 0.5)


def bg_girls_dorm():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("2e2634"), hexc("161220"))
    im.rect(0, 0, W, H * 0.72, hexc("362b3e"))
    im.rect(0, H * 0.70, W, H, hexc("2a2130"))
    # corridor of doors receding
    for i in range(6):
        t = i / 5.0
        k = 1.0 - t * 0.72
        for sgn in (-1, 1):
            x = W * 0.5 + sgn * (W * 0.46) * k
            xw = 92 * k
            im.rect(x - xw, H * (0.5 - 0.30 * k), x + xw, H * (0.5 + 0.30 * k), hexc("241c2c"))
            im.rect(x - xw * 0.82, H * (0.5 - 0.26 * k), x + xw * 0.82, H * (0.5 + 0.28 * k), hexc("4a3a54"))
            im.ellipse(x + xw * 0.55, H * 0.5, 7 * k, 7 * k, hexc("c9a0d8"))
    im.poly([(0, H), (W, H), (W * 0.5 + 120, H * 0.60), (W * 0.5 - 120, H * 0.60)], hexc("241c2c"), 0.9)
    im.glow(W * 0.5, H * 0.46, 380, hexc("e0b8ff"), 0.20, 2.2)
    finish(im, "girls_dorm", 0.58)


def bg_cafeteria():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("5b4f42"), hexc("241d18"))
    im.rect(0, 0, W, H * 0.62, hexc("6b5c4c"))
    # serving counter
    im.rect(0, H * 0.34, W * 0.34, H * 0.62, hexc("3f3428"))
    im.rect(0, H * 0.40, W * 0.34, H * 0.44, hexc("8fa0a8"))
    im.glow(W * 0.16, H * 0.42, 320, hexc("ffe0a8"), 0.30, 2.0)
    # windows
    for i in range(3):
        x = W * 0.44 + i * W * 0.19
        im.rect(x, H * 0.14, x + W * 0.14, H * 0.50, hexc("2f271f"))
        im.rect(x + 6, H * 0.15, x + W * 0.14 - 6, H * 0.49, hexc("bcd6e2"), 0.9)
    im.rect(0, H * 0.62, W, H, hexc("4a3c2c"))
    # long tables
    for r in range(2):
        y = H * (0.68 + r * 0.15)
        im.rrect(W * (0.06 - r * 0.05), y, W * (0.94 + r * 0.05), y + H * 0.05, 8, hexc("7a6144"))
        im.rect(W * 0.14, y + H * 0.05, W * 0.18, y + H * 0.13, hexc("3a2e20"))
        im.rect(W * 0.82, y + H * 0.05, W * 0.86, y + H * 0.13, hexc("3a2e20"))
    finish(im, "cafeteria", 0.45)


def bg_dojo():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("2b2620"), hexc("14110d"))
    im.rect(0, 0, W, H * 0.60, hexc("332c24"))
    # shoji panels
    for i in range(7):
        x = i * W / 6.0
        im.rect(x - 8, 0, x + 8, H * 0.60, hexc("1d1913"))
        im.rect(x + 8, H * 0.10, x + W / 6.0 - 8, H * 0.55, hexc("cbbb96"), 0.30)
    im.rect(0, H * 0.58, W, H * 0.62, hexc("18140f"))
    im.rect(0, H * 0.60, W, H, hexc("6a5636"))
    for i in range(7):
        y = H * 0.64 + i * H * 0.06
        im.rect(0, y, W, y + 4, hexc("52411f"), 0.6)
    # weapon rack
    im.rect(W * 0.72, H * 0.22, W * 0.98, H * 0.28, hexc("241d14"))
    for i in range(5):
        x = W * 0.745 + i * W * 0.05
        im.rect(x - 5, H * 0.22, x + 5, H * 0.60, hexc("8f7a52"))
        im.rect(x - 9, H * 0.20, x + 9, H * 0.245, hexc("c8b98f"))
    im.glow(W * 0.35, H * 0.24, 620, hexc("ffdca8"), 0.20, 2.2)
    finish(im, "dojo", 0.52)


def bg_riverside():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.52, hexc("5fa8e8"), hexc("d6f0f8"), gamma=1.3)
    for cx, cy, r in [(350, 130, 130), (1500, 110, 150), (950, 90, 80)]:
        im.ellipse(cx, cy, r, r * 0.42, (255, 255, 255), 0.8)
    hills(im, H * 0.44, 52, hexc("7f9ab0"), 61, 0.85)
    treeline(im, H * 0.56, 210, hexc("2c5238"), 62, 0.95)
    # far bank + water
    im.rect(0, H * 0.54, W, H * 0.60, hexc("4a6b44"))
    im.rect(0, H * 0.58, W, H * 0.90, hexc("2f6f8f"))
    for i in range(38):
        rnd = random.Random(i * 7)
        y = H * (0.60 + 0.29 * (i / 38.0))
        x = rnd.uniform(0, W)
        wdt = rnd.uniform(60, 300)
        im.rect(x, y, x + wdt, y + rnd.uniform(2, 5), hexc("bfe6f2"), rnd.uniform(0.15, 0.5))
    im.glow(W * 0.62, H * 0.68, 480, hexc("ffffff"), 0.16, 2.0)
    # near bank
    im.poly([(0, H), (W, H), (W, H * 0.88), (0, H * 0.92)], hexc("6b7a4a"))
    im.poly([(0, H), (W, H), (W, H * 0.94), (0, H * 0.97)], hexc("8f9a63"))
    finish(im, "riverside", 0.40)


def bg_ridge():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.60, hexc("2b3f6b"), hexc("f2b070"), gamma=1.5)
    im.ellipse(W * 0.24, H * 0.30, 62, 62, hexc("fff4d0"), 0.95)
    im.glow(W * 0.24, H * 0.30, 400, hexc("ffd9a0"), 0.35, 2.0)
    hills(im, H * 0.50, 70, hexc("54608f"), 71, 0.75)
    hills(im, H * 0.58, 54, hexc("38406b"), 72, 0.85)
    treeline(im, H * 0.70, 190, hexc("1c2440"), 73, 0.95)
    im.rect(0, H * 0.70, W, H, hexc("2a2c3a"))
    im.poly([(0, H), (W, H), (W * 0.78, H * 0.72), (W * 0.20, H * 0.74)], hexc("3b3d4c"))
    for i in range(14):
        rnd = random.Random(i * 3 + 1)
        x = rnd.uniform(0, W); y = rnd.uniform(H * 0.76, H)
        r = rnd.uniform(18, 54)
        im.ellipse(x, y, r, r * 0.6, hexc("4a4c5c"), 0.9)
    finish(im, "ridge", 0.45)


def bg_storehouse():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("241f2b"), hexc("0d0b12"))
    im.rect(0, 0, W, H * 0.66, hexc("2b2433"))
    # shelving
    for c in range(5):
        x = W * 0.04 + c * W * 0.196
        im.rect(x, H * 0.10, x + W * 0.16, H * 0.66, hexc("1a1622"))
        for r in range(4):
            y = H * (0.16 + r * 0.13)
            im.rect(x, y, x + W * 0.16, y + 10, hexc("3d3450"))
            rnd = random.Random(c * 10 + r)
            for i in range(3):
                bx = x + W * 0.02 + i * W * 0.048
                bh = rnd.uniform(30, 74)
                im.rrect(bx, y - bh, bx + W * 0.036, y, 4, hexc("5a4a30"))
    im.rect(0, H * 0.66, W, H, hexc("342b3f"))
    im.glow(W * 0.5, H * 0.20, 700, hexc("b48cff"), 0.18, 2.2)
    finish(im, "storehouse", 0.58)


def bg_office():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("3a3128"), hexc("1a1610"))
    im.rect(0, 0, W, H * 0.64, hexc("44392c"))
    im.rect(W * 0.62, H * 0.10, W * 0.96, H * 0.52, hexc("241d16"))
    im.rect(W * 0.63, H * 0.11, W * 0.95, H * 0.51, hexc("9fc0d0"), 0.85)
    im.glow(W * 0.79, H * 0.30, 420, hexc("fff0cc"), 0.26, 2.0)
    # bookshelf
    im.rect(W * 0.02, H * 0.08, W * 0.34, H * 0.64, hexc("2b2219"))
    for r in range(5):
        y = H * (0.14 + r * 0.10)
        im.rect(W * 0.02, y, W * 0.34, y + 8, hexc("4a3c2a"))
        rnd = random.Random(r)
        for i in range(10):
            bx = W * 0.03 + i * W * 0.031
            im.rect(bx, y - rnd.uniform(30, 62), bx + W * 0.022, y, lerp(hexc("6b3f3f"), hexc("3f5a6b"), rnd.random()))
    im.rect(0, H * 0.64, W, H, hexc("3a2e20"))
    im.rrect(W * 0.28, H * 0.62, W * 0.86, H * 0.78, 6, hexc("55402a"))
    im.rect(W * 0.34, H * 0.78, W * 0.40, H, hexc("2e2418"))
    im.rect(W * 0.76, H * 0.78, W * 0.82, H, hexc("2e2418"))
    finish(im, "office", 0.48)


def bg_your_room():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("2a2434"), hexc("13101a"))
    im.rect(0, 0, W, H * 0.70, hexc("332a42"))
    im.rect(W * 0.56, H * 0.14, W * 0.90, H * 0.50, hexc("110e18"))
    im.rect(W * 0.57, H * 0.15, W * 0.89, H * 0.49, hexc("1c2450"))
    im.ellipse(W * 0.80, H * 0.25, 46, 46, hexc("f2f0e0"), 0.95)
    im.glow(W * 0.80, H * 0.25, 200, hexc("cfd6ff"), 0.28, 2.0)
    im.rect(W * 0.72, H * 0.14, W * 0.735, H * 0.50, hexc("110e18"))
    im.rect(0, H * 0.70, W, H, hexc("3a2c22"))
    im.rrect(W * 0.02, H * 0.58, W * 0.38, H * 0.88, 12, hexc("46384e"))
    im.rrect(W * 0.04, H * 0.54, W * 0.15, H * 0.62, 10, hexc("d8cfd8"))
    im.rrect(W * 0.44, H * 0.60, W * 0.70, H * 0.68, 6, hexc("55402a"))
    im.rrect(W * 0.47, H * 0.545, W * 0.58, H * 0.60, 4, hexc("2a3550"))
    im.glow(W * 0.52, H * 0.52, 300, hexc("ffc98a"), 0.26, 2.0)
    finish(im, "your_room", 0.52)


# ---------------------------------------------------------------- campus map
## (name, x, y, kind) -- MUST stay in sync with LOCATIONS in game/sb_world.rpy
NODES = [
    ("gate",       960,  975, "gate"),
    ("courtyard",  960,  815, "open"),
    ("classroom",  600,  735, "hall"),
    ("cafeteria",  330,  860, "hall"),
    ("training",  1330,  735, "hall"),
    ("dojo",      1640,  845, "hall"),
    ("dorm",       735,  545, "dorm"),
    ("dorm_common",735,  660, "small"),
    ("girls_dorm",1175,  545, "dorm"),
    ("rooftop",    960,  455, "small"),
    ("infirmary",  350,  610, "hall"),
    ("office",    1560,  560, "hall"),
    ("storehouse",1745,  675, "small"),
    ("forest",     290,  335, "tree"),
    ("riverside",  640,  225, "water"),
    ("ridge",     1290,  215, "peak"),
]

PATHS = [
    ("gate", "courtyard"), ("courtyard", "classroom"), ("classroom", "cafeteria"),
    ("courtyard", "training"), ("training", "dojo"), ("courtyard", "dorm_common"),
    ("dorm_common", "dorm"), ("dorm", "girls_dorm"), ("dorm", "rooftop"),
    ("girls_dorm", "rooftop"), ("classroom", "infirmary"), ("training", "office"),
    ("office", "storehouse"), ("infirmary", "forest"), ("forest", "riverside"),
    ("riverside", "rooftop"), ("rooftop", "ridge"), ("ridge", "office"),
    ("girls_dorm", "office"), ("dorm_common", "classroom"), ("cafeteria", "infirmary"),
]


def bg_map():
    im = Img(W, H)
    pos = {n[0]: (n[1], n[2]) for n in NODES}

    # ground: forested mountain shoulder, lighter toward the centre of campus
    im.vgrad(0, 0, W, H, hexc("16211c"), hexc("0c1310"))
    im.glow(960, 640, 1150, hexc("3c5a48"), 0.55, 1.6)
    rnd = random.Random(5)
    for i in range(340):
        x = rnd.uniform(-40, W + 40); y = rnd.uniform(-40, H + 40)
        d = math.hypot(x - 960, y - 620) / 1000.0
        if rnd.random() < 0.25 + d * 0.7:
            r = rnd.uniform(12, 30)
            im.ellipse(x, y + 6, r * 0.9, r * 0.5, hexc("0a120d"), 0.5)
            im.poly([(x - r * 0.6, y), (x, y - r * 1.7), (x + r * 0.6, y)],
                    lerp(hexc("1d3326"), hexc("2f4a35"), rnd.random()), 0.95)

    # paths
    for a, b in PATHS:
        ax, ay = pos[a]; bx, by = pos[b]
        steps = int(math.hypot(bx - ax, by - ay) / 5)
        for s in range(steps + 1):
            t = s / float(max(1, steps))
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            im.ellipse(x, y, 9, 9, hexc("4a4436"), 0.55, soft=3)

    # building footprints
    for name, x, y, kind in NODES:
        if kind in ("hall", "dorm"):
            w, h = (128, 82) if kind == "hall" else (112, 96)
            im.rect(x - w / 2 + 7, y - h / 2 + 9, x + w / 2 + 7, y + h / 2 + 9, hexc("07100b"), 0.55)
            im.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, hexc("342b3c"))
            im.poly([(x - w / 2 - 14, y - h / 2), (x + w / 2 + 14, y - h / 2), (x, y - h / 2 - 34)], hexc("1e1826"))
            for i in range(4):
                wx = x - w / 2 + 18 + i * (w - 30) / 3.0
                im.rect(wx, y - 8, wx + 12, y + 16, hexc("d8b46a"), 0.8)
        elif kind == "small":
            im.rect(x - 42, y - 30, x + 42, y + 30, hexc("2e2836"))
            im.poly([(x - 52, y - 30), (x + 52, y - 30), (x, y - 56)], hexc("1c1724"))
        elif kind == "gate":
            im.rect(x - 96, y - 46, x + 96, y - 34, hexc("2a1f2e"))
            im.rect(x - 74, y - 34, x - 62, y + 26, hexc("2a1f2e"))
            im.rect(x + 62, y - 34, x + 74, y + 26, hexc("2a1f2e"))
        elif kind == "water":
            im.ellipse(x, y, 128, 56, hexc("2f6f8f"), 0.95)
            im.ellipse(x, y - 8, 110, 40, hexc("58a8c4"), 0.6)
        elif kind == "peak":
            im.poly([(x - 130, y + 70), (x, y - 96), (x + 130, y + 70)], hexc("3c4258"))
            im.poly([(x - 44, y - 14), (x, y - 96), (x + 44, y - 14)], hexc("cdd6e8"), 0.9)
        elif kind == "tree":
            for i, (ox, oy, s) in enumerate([(-52, 16, 1.1), (0, -12, 1.35), (54, 20, 1.0)]):
                im.poly([(x + ox - 34 * s, y + oy + 34), (x + ox, y + oy - 62 * s),
                         (x + ox + 34 * s, y + oy + 34)], hexc("24422f"))
        elif kind == "open":
            im.ellipse(x, y, 118, 58, hexc("54604d"), 0.9)
            im.ellipse(x, y, 96, 44, hexc("6b7359"), 0.8)

    im.vignette(0.42)
    im.grain(4, 2, seed=11)
    im.save(os.path.join(OUT, "map_campus.png"))
    print("   map_campus")


if __name__ == "__main__":
    print("world art ->", OUT)
    bg_your_room(); bg_dorm_common(); bg_girls_dorm(); bg_cafeteria()
    bg_dojo(); bg_riverside(); bg_ridge(); bg_storehouse(); bg_office()
    bg_map()
