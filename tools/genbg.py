import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game", "images", "bg")
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080


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


def treeline(im, base_y, height, color, seed, alpha=1.0, count=46):
    rnd = random.Random(seed)
    for i in range(count):
        x = -40 + (W + 80) * i / float(count - 1) + rnd.uniform(-14, 14)
        h = height * rnd.uniform(0.62, 1.35)
        w = h * rnd.uniform(0.14, 0.26)
        im.poly([(x - w, base_y), (x, base_y - h), (x + w, base_y)], color, alpha)
        im.rect(x - w * 0.14, base_y - h * 0.2, x + w * 0.14, base_y + 20, color, alpha)


def building(im, x0, x1, top, color, win, seed, lit=0.5, wy=26, wx=18):
    im.rect(x0, top, x1, H, color)
    rnd = random.Random(seed)
    y = top + 22
    while y < H - 30:
        x = x0 + 14
        while x < x1 - wx - 6:
            if rnd.random() < lit:
                c = lerp(win, (255, 255, 255), rnd.uniform(0, 0.35))
                im.rect(x, y, x + wx, y + wy * 0.55, c, rnd.uniform(0.5, 0.95))
            x += wx + 12
        y += wy


def finish(im, name, vig=0.5, grain=6):
    im.vignette(vig)
    if grain:
        im.grain(grain, 2, seed=hash(name) % 999)
    im.save(os.path.join(OUT, name + ".png"))
    print("  ", name)


# ---------------------------------------------------------------- scenes
def bg_black():
    im = Img(W, H, fill=(0, 0, 0))
    im.save(os.path.join(OUT, "black.png"))
    print("   black")


def bg_ruin_hall():
    """Abandoned school corridor, sickly cursed green. Prologue."""
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("0a1410"), hexc("040806"))
    # receding corridor: nested rectangles
    for i in range(9):
        t = i / 8.0
        k = 1.0 - t
        x0 = W * 0.5 - (W * 0.5 + 60) * k
        x1 = W * 0.5 + (W * 0.5 + 60) * k
        y0 = H * 0.5 - (H * 0.5 + 40) * k
        y1 = H * 0.5 + (H * 0.52) * k
        c = lerp(hexc("16241c"), hexc("2c4a36"), t)
        im.rect(x0, y0, x1, y1, c, 1.0)
    # doorways along the walls
    for i, t in enumerate([0.0, 0.22, 0.42, 0.58]):
        k = 1.0 - t
        for sgn in (-1, 1):
            xa = W * 0.5 + sgn * (W * 0.5 + 60) * k
            xb = W * 0.5 + sgn * (W * 0.5 + 60) * (k * 0.82)
            ya = H * 0.5 - (H * 0.42) * k
            yb = H * 0.5 + (H * 0.42) * k
            im.poly([(xa, ya), (xb, ya * 0.94 + H * 0.03), (xb, yb * 0.96), (xa, yb)], hexc("07100b"), 0.85)
    # floor
    im.poly([(0, H), (W, H), (W * 0.5 + 90, H * 0.62), (W * 0.5 - 90, H * 0.62)], hexc("101a13"), 0.9)
    # cursed light at the far end
    im.glow(W * 0.5, H * 0.5, 460, hexc("4fe08a"), 0.34, 2.4)
    im.glow(W * 0.5, H * 0.5, 150, hexc("baffd4"), 0.5, 2.0)
    finish(im, "ruin_hall", 0.62)


def bg_gate():
    """Jujutsu High front gate at dusk."""
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.78, hexc("2a1b4d"), hexc("e8825a"), gamma=1.5)
    im.glow(W * 0.62, H * 0.60, 620, hexc("ffc98a"), 0.55, 2.0)
    hills(im, H * 0.60, 46, hexc("3a2c52"), 11)
    hills(im, H * 0.68, 34, hexc("241a38"), 12)
    treeline(im, H * 0.74, 150, hexc("15101f"), 13)
    im.rect(0, H * 0.73, W, H, hexc("120d1c"))
    # stone path
    im.poly([(W * 0.34, H), (W * 0.66, H), (W * 0.54, H * 0.73), (W * 0.46, H * 0.73)], hexc("241b32"))
    # gate: two pillars + crossbeam
    for x in (W * 0.30, W * 0.70):
        im.rect(x - 26, H * 0.30, x + 26, H * 0.76, hexc("0d0a14"))
    im.rect(W * 0.24, H * 0.28, W * 0.76, H * 0.335, hexc("0d0a14"))
    im.rect(W * 0.26, H * 0.365, W * 0.74, H * 0.395, hexc("0d0a14"))
    finish(im, "gate", 0.45)


def bg_courtyard():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.72, hexc("4d8fd6"), hexc("cfe6f5"), gamma=1.3)
    for cx, cy, r in [(300, 170, 120), (420, 200, 90), (1450, 140, 140), (1600, 180, 100), (900, 110, 80)]:
        im.ellipse(cx, cy, r, r * 0.45, (255, 255, 255), 0.75)
        im.ellipse(cx + r * 0.5, cy + 18, r * 0.7, r * 0.36, (255, 255, 255), 0.6)
    hills(im, H * 0.56, 60, hexc("6f86a8"), 21, 0.8)
    treeline(im, H * 0.70, 190, hexc("22412f"), 22)
    # main hall building
    im.rect(W * 0.06, H * 0.30, W * 0.44, H * 0.71, hexc("3a3340"))
    im.poly([(W * 0.02, H * 0.31), (W * 0.48, H * 0.31), (W * 0.25, H * 0.19)], hexc("221d28"))
    for i in range(6):
        x = W * 0.09 + i * W * 0.058
        im.rect(x, H * 0.40, x + W * 0.036, H * 0.55, hexc("9fc6d8"), 0.85)
    im.rect(0, H * 0.70, W, H, hexc("58604d"))
    im.rect(0, H * 0.70, W, H * 0.735, hexc("6b7359"))
    finish(im, "courtyard", 0.4)


def bg_classroom():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("6a5f52"), hexc("30291f"))
    im.rect(0, 0, W, H * 0.66, hexc("7a6d5c"))
    for i in range(3):
        x = W * 0.10 + i * W * 0.29
        im.rect(x, H * 0.16, x + W * 0.20, H * 0.55, hexc("2b2620"))
        im.rect(x + 8, H * 0.17, x + W * 0.20 - 8, H * 0.54, hexc("cfe3ee"), 0.92)
        im.rect(x + W * 0.10 - 4, H * 0.17, x + W * 0.10 + 4, H * 0.54, hexc("2b2620"))
        im.glow(x + W * 0.10, H * 0.35, 260, hexc("fff2d0"), 0.30, 2.0)
    im.rect(0, H * 0.66, W, H, hexc("4a3d2c"))
    for r in range(3):
        yy = H * (0.72 + r * 0.10)
        for c in range(5):
            x = W * (0.05 + c * 0.21) - r * 30
            im.rrect(x, yy, x + 250 + r * 40, yy + 26 + r * 8, 6, hexc("6b563a"))
            im.rect(x + 20, yy + 26 + r * 8, x + 36, yy + 120, hexc("2e2519"))
    finish(im, "classroom", 0.5)


def bg_training():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("1c1a24"), hexc("0a090e"))
    im.rect(0, 0, W, H * 0.58, hexc("241f2c"))
    for i in range(9):
        x = i * W / 8.0
        im.rect(x - 10, 0, x + 10, H * 0.58, hexc("15121c"))
    im.rect(0, H * 0.56, W, H * 0.60, hexc("0e0c14"))
    # floor mats
    im.rect(0, H * 0.58, W, H, hexc("3f3348"))
    for i in range(8):
        y = H * 0.62 + i * H * 0.06
        im.rect(0, y, W, y + 3, hexc("2a2233"), 0.8)
    im.glow(W * 0.5, H * 0.16, 640, hexc("cbb6ff"), 0.22, 2.2)
    finish(im, "training", 0.55)


def bg_dorm():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("2a2130"), hexc("14101a"))
    im.rect(0, 0, W, H * 0.70, hexc("332942"))
    # window with moon
    im.rect(W * 0.58, H * 0.12, W * 0.90, H * 0.52, hexc("100d18"))
    im.rect(W * 0.585, H * 0.128, W * 0.895, H * 0.512, hexc("1b2450"))
    im.ellipse(W * 0.80, H * 0.24, 52, 52, hexc("f2f0e0"), 0.95)
    im.glow(W * 0.80, H * 0.24, 210, hexc("cfd6ff"), 0.30, 2.0)
    im.rect(W * 0.735, H * 0.12, W * 0.745, H * 0.52, hexc("100d18"))
    # bed + desk
    im.rect(0, H * 0.70, W, H, hexc("3a2c22"))
    im.rrect(W * 0.03, H * 0.60, W * 0.40, H * 0.86, 12, hexc("4c3a4e"))
    im.rrect(W * 0.05, H * 0.56, W * 0.16, H * 0.63, 10, hexc("d8cfd8"))
    im.rrect(W * 0.56, H * 0.62, W * 0.94, H * 0.70, 6, hexc("5b4632"))
    im.glow(W * 0.20, H * 0.30, 520, hexc("ffb870"), 0.26, 2.2)
    finish(im, "dorm", 0.55)


def bg_forest():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("8fa6a4"), hexc("22322c"), gamma=1.2)
    treeline(im, H * 0.60, 300, hexc("5d7370"), 31, 0.55, 34)
    im.rect(0, H * 0.40, W, H, hexc("9db1ad"), 0.22)
    treeline(im, H * 0.74, 420, hexc("2f4440"), 32, 0.8, 28)
    im.rect(0, H * 0.55, W, H, hexc("8ea5a1"), 0.16)
    treeline(im, H * 0.95, 620, hexc("14211e"), 33, 0.95, 20)
    im.rect(0, H * 0.90, W, H, hexc("101a17"))
    finish(im, "forest", 0.5)


def bg_city_night():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.8, hexc("120e26"), hexc("4a2a52"), gamma=1.4)
    im.glow(W * 0.30, H * 0.72, 700, hexc("ff8ad0"), 0.20, 2.2)
    rnd = random.Random(41)
    x = -60
    seed = 0
    while x < W + 60:
        w = rnd.randint(90, 210)
        top = H * rnd.uniform(0.28, 0.62)
        building(im, x, x + w, top, lerp(hexc("0d0a18"), hexc("241c38"), rnd.random() * 0.5),
                 hexc("ffd98a"), seed, lit=rnd.uniform(0.25, 0.6))
        x += w + rnd.randint(6, 26)
        seed += 1
    im.rect(0, H * 0.92, W, H, hexc("07050d"))
    finish(im, "city_night", 0.5)


def bg_rooftop():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.70, hexc("30265c"), hexc("f0a06a"), gamma=1.6)
    im.ellipse(W * 0.72, H * 0.58, 90, 90, hexc("fff1c8"), 0.9)
    im.glow(W * 0.72, H * 0.58, 520, hexc("ffb877"), 0.45, 2.0)
    rnd = random.Random(55)
    x = -40
    while x < W + 40:
        w = rnd.randint(70, 160)
        top = H * rnd.uniform(0.50, 0.66)
        im.rect(x, top, x + w, H * 0.72, hexc("2a2038"), 0.9)
        x += w + rnd.randint(4, 18)
    im.rect(0, H * 0.70, W, H, hexc("3b3346"))
    im.rect(0, H * 0.70, W, H * 0.725, hexc("4a4256"))
    # railing
    for i in range(26):
        x = i * W / 25.0
        im.rect(x - 5, H * 0.52, x + 5, H * 0.72, hexc("1b1725"))
    im.rect(0, H * 0.505, W, H * 0.53, hexc("1b1725"))
    finish(im, "rooftop", 0.45)


def bg_veil():
    """Inside a curtain / domain. Deep violet void."""
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("120423"), hexc("020106"))
    im.glow(W * 0.5, H * 0.48, 900, hexc("7b2fd6"), 0.42, 2.0)
    im.glow(W * 0.5, H * 0.48, 380, hexc("c98cff"), 0.30, 2.4)
    rnd = random.Random(7)
    for i in range(160):
        a = rnd.uniform(0, 6.283)
        r = rnd.uniform(120, 950)
        x = W * 0.5 + math.cos(a) * r * 1.5
        y = H * 0.5 + math.sin(a) * r * 0.8
        im.ellipse(x, y, rnd.uniform(2, 7), rnd.uniform(2, 7), hexc("e0c0ff"), rnd.uniform(0.2, 0.8))
    finish(im, "veil", 0.35)


def bg_infirmary():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("dfe7e6"), hexc("8fa19f"))
    im.rect(0, 0, W, H * 0.66, hexc("e6eeed"))
    im.rect(0, H * 0.64, W, H * 0.67, hexc("aebbb9"))
    im.rect(0, H * 0.66, W, H, hexc("b9c3bf"))
    im.rect(W * 0.05, H * 0.20, W * 0.30, H * 0.50, hexc("cfe0e8"))
    im.glow(W * 0.17, H * 0.34, 340, hexc("ffffff"), 0.4, 2.0)
    im.rrect(W * 0.42, H * 0.55, W * 0.95, H * 0.70, 10, hexc("f2f5f4"))
    im.rrect(W * 0.42, H * 0.68, W * 0.95, H * 0.86, 8, hexc("9aa8a5"))
    finish(im, "infirmary", 0.35, 4)


if __name__ == "__main__":
    print("backgrounds ->", OUT)
    bg_black(); bg_ruin_hall(); bg_gate(); bg_courtyard(); bg_classroom()
    bg_training(); bg_dorm(); bg_forest(); bg_city_night(); bg_rooftop()
    bg_veil(); bg_infirmary()
