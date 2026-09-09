"""Backgrounds for the pre-campus chapters: home, Yotsuka High, the town, the festival, the station."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp
from genworld import finish, treeline, hills, OUT, W, H


def bg_home_living():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("8a7f74"), hexc("3f3730"))
    im.rect(0, 0, W, H * 0.66, hexc("9a8e80"))
    # window with afternoon light
    im.rect(W * 0.58, H * 0.10, W * 0.94, H * 0.52, hexc("3a322c"))
    im.vgrad(W * 0.59, H * 0.11, W * 0.93, H * 0.51, hexc("a9d0ee"), hexc("e6f1f7"))
    im.rect(W * 0.755, H * 0.10, W * 0.765, H * 0.52, hexc("3a322c"))
    im.glow(W * 0.76, H * 0.30, 640, hexc("fff2d8"), 0.34, 2.0)
    # low table, sofa, tv
    im.rect(0, H * 0.66, W, H, hexc("6b5a46"))
    im.rrect(W * 0.04, H * 0.52, W * 0.46, H * 0.84, 18, hexc("5d6b78"))
    im.rrect(W * 0.06, H * 0.47, W * 0.44, H * 0.57, 16, hexc("6f7e8c"))
    im.rrect(W * 0.50, H * 0.70, W * 0.80, H * 0.80, 8, hexc("4d3d2c"))
    im.rrect(W * 0.08, H * 0.16, W * 0.30, H * 0.44, 6, hexc("1c1a20"))
    im.rrect(W * 0.09, H * 0.17, W * 0.29, H * 0.43, 4, hexc("2a3446"))
    finish(im, "home_living", 0.40)


def bg_home_bedroom():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("6d6a78"), hexc("2c2a34"))
    im.rect(0, 0, W, H * 0.68, hexc("7a7788"))
    im.rect(W * 0.06, H * 0.12, W * 0.36, H * 0.50, hexc("2e2c36"))
    im.vgrad(W * 0.07, H * 0.13, W * 0.35, H * 0.49, hexc("8fbce0"), hexc("d8e9f4"))
    im.glow(W * 0.21, H * 0.31, 520, hexc("fff4dc"), 0.30, 2.0)
    im.rect(0, H * 0.68, W, H, hexc("6a5a48"))
    im.rrect(W * 0.52, H * 0.56, W * 0.96, H * 0.88, 12, hexc("4a5a7a"))
    im.rrect(W * 0.54, H * 0.52, W * 0.66, H * 0.60, 10, hexc("e8e4ee"))
    im.rrect(W * 0.04, H * 0.58, W * 0.34, H * 0.66, 6, hexc("7d6647"))
    im.rrect(W * 0.08, H * 0.50, W * 0.20, H * 0.58, 4, hexc("2a3244"))
    # posters / shelf
    im.rrect(W * 0.42, H * 0.14, W * 0.50, H * 0.30, 3, hexc("b8555a"))
    im.rrect(W * 0.40, H * 0.36, W * 0.52, H * 0.40, 2, hexc("4a3d30"))
    finish(im, "home_bedroom", 0.42)


def bg_yotsuka_hall():
    """An ordinary school corridor by day — the un-cursed twin of ruin_hall."""
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("d9d4c8"), hexc("6f6a62"))
    for i in range(9):
        t = i / 8.0
        k = 1.0 - t
        x0 = W * 0.5 - (W * 0.5 + 60) * k
        x1 = W * 0.5 + (W * 0.5 + 60) * k
        y0 = H * 0.5 - (H * 0.5 + 40) * k
        y1 = H * 0.5 + (H * 0.52) * k
        im.rect(x0, y0, x1, y1, lerp(hexc("cfc9bb"), hexc("e9e5da"), t))
    for t in [0.0, 0.22, 0.42, 0.58]:
        k = 1.0 - t
        for sgn in (-1, 1):
            xa = W * 0.5 + sgn * (W * 0.5 + 60) * k
            xb = W * 0.5 + sgn * (W * 0.5 + 60) * (k * 0.82)
            ya = H * 0.5 - (H * 0.42) * k
            yb = H * 0.5 + (H * 0.42) * k
            im.poly([(xa, ya), (xb, ya * 0.94 + H * 0.03), (xb, yb * 0.96), (xa, yb)], hexc("8fa6b8"), 0.85)
    im.poly([(0, H), (W, H), (W * 0.5 + 90, H * 0.62), (W * 0.5 - 90, H * 0.62)], hexc("a89f8c"), 0.95)
    im.glow(W * 0.5, H * 0.5, 460, hexc("ffffff"), 0.30, 2.4)
    finish(im, "yotsuka_hall", 0.30, 4)


def bg_yotsuka_class():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("e6e1d6"), hexc("8c847a"))
    im.rect(0, 0, W, H * 0.64, hexc("ece8de"))
    for i in range(3):
        x = W * 0.10 + i * W * 0.29
        im.rect(x, H * 0.14, x + W * 0.20, H * 0.54, hexc("6c6a66"))
        im.vgrad(x + 8, H * 0.15, x + W * 0.20 - 8, H * 0.53, hexc("9fc8ec"), hexc("e6f2fa"))
        im.rect(x + W * 0.10 - 4, H * 0.15, x + W * 0.10 + 4, H * 0.53, hexc("6c6a66"))
    im.rect(0, H * 0.64, W, H, hexc("b9ad98"))
    for r in range(3):
        yy = H * (0.70 + r * 0.10)
        for c in range(5):
            x = W * (0.05 + c * 0.21) - r * 30
            im.rrect(x, yy, x + 250 + r * 40, yy + 26 + r * 8, 6, hexc("c9b48c"))
            im.rect(x + 20, yy + 26 + r * 8, x + 36, yy + 120, hexc("7d7568"))
    finish(im, "yotsuka_class", 0.30, 4)


def bg_town_street():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.60, hexc("7fb3e6"), hexc("dcecf6"), gamma=1.3)
    for cx, cy, r in [(400, 150, 120), (1300, 120, 150), (1700, 200, 90)]:
        im.ellipse(cx, cy, r, r * 0.42, (255, 255, 255), 0.8)
    # houses receding on both sides
    rnd = random.Random(21)
    for i in range(6):
        t = i / 5.0
        k = 1.0 - t * 0.7
        for sgn in (-1, 1):
            x = W * 0.5 + sgn * (W * 0.50) * k
            w = 220 * k
            top = H * (0.58 - 0.26 * k)
            im.rect(x - w, top, x + w * 0.2 * sgn + x - x, H * 0.62, lerp(hexc("d8d2c6"), hexc("9f9689"), rnd.random()))
            im.poly([(x - w - 16, top), (x + 16 * sgn, top), (x - w / 2, top - 60 * k)], hexc("5e4a3a"))
            im.rect(x - w * 0.7, top + 30 * k, x - w * 0.5, top + 80 * k, hexc("6f8fb0"), 0.9)
    im.rect(0, H * 0.60, W, H, hexc("8d8a84"))
    im.poly([(0, H), (W, H), (W * 0.62, H * 0.60), (W * 0.38, H * 0.60)], hexc("6f6c66"))
    im.rect(0, H * 0.60, W, H * 0.63, hexc("a9a59c"))
    # power poles
    for x in (W * 0.22, W * 0.80):
        im.rect(x - 6, H * 0.10, x + 6, H * 0.62, hexc("4a4038"))
        im.rect(x - 60, H * 0.14, x + 60, H * 0.15, hexc("4a4038"))
    finish(im, "town_street", 0.32, 4)


def bg_festival():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.62, hexc("1d1a3e"), hexc("6a3f5e"), gamma=1.4)
    # school building silhouette with lit windows
    im.rect(W * 0.10, H * 0.24, W * 0.90, H * 0.62, hexc("2a2436"))
    rnd = random.Random(8)
    for r in range(3):
        for c in range(14):
            x = W * 0.13 + c * W * 0.054
            y = H * (0.29 + r * 0.10)
            if rnd.random() < 0.7:
                im.rect(x, y, x + W * 0.036, y + H * 0.06, hexc("ffd98a"), rnd.uniform(0.6, 0.95))
    # strings of lanterns
    for row, y in enumerate([H * 0.16, H * 0.21]):
        for i in range(12):
            x = W * 0.06 + i * W * 0.08 + row * 40
            sag = math.sin(i / 11.0 * math.pi) * 24
            im.ellipse(x, y + sag, 22, 30, hexc("ff6a4a"), 0.95)
            im.glow(x, y + sag, 120, hexc("ffb070"), 0.45, 2.0)
    # stalls + crowd
    im.rect(0, H * 0.62, W, H, hexc("3a3040"))
    for i in range(5):
        x = W * 0.04 + i * W * 0.19
        im.rrect(x, H * 0.56, x + W * 0.15, H * 0.76, 6, lerp(hexc("c94b3a"), hexc("2f6fb0"), (i % 2)))
        im.rect(x - 10, H * 0.52, x + W * 0.15 + 10, H * 0.57, hexc("f2e6c8"))
        im.glow(x + W * 0.075, H * 0.60, 220, hexc("ffe6b0"), 0.35, 2.0)
    for i in range(40):
        x = rnd.uniform(0, W); y = rnd.uniform(H * 0.76, H * 0.98)
        im.ellipse(x, y, rnd.uniform(26, 40), rnd.uniform(60, 90), hexc("161220"), 0.9)
    finish(im, "festival", 0.42)


def bg_station():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("b9c4cc"), hexc("50575e"))
    im.rect(0, 0, W, H * 0.30, hexc("7b8890"))          # canopy
    im.rect(0, H * 0.30, W, H * 0.34, hexc("3d444a"))
    for i in range(7):
        x = i * W / 6.0
        im.rect(x - 10, H * 0.34, x + 10, H * 0.72, hexc("4a5258"))
    im.rect(0, H * 0.72, W, H, hexc("9a9a94"))          # platform
    im.rect(0, H * 0.80, W, H * 0.815, hexc("e0d24a"))  # yellow line
    im.rect(0, H * 0.86, W, H, hexc("3a3a3a"))          # track bed
    im.rect(0, H * 0.90, W, H * 0.905, hexc("8a8a8a"))
    im.rect(0, H * 0.95, W, H * 0.955, hexc("8a8a8a"))
    im.rrect(W * 0.36, H * 0.38, W * 0.64, H * 0.50, 6, hexc("1f2a3a"))
    im.rrect(W * 0.37, H * 0.39, W * 0.63, H * 0.49, 4, hexc("2f4a6a"))
    im.glow(W * 0.5, H * 0.20, 700, hexc("ffffff"), 0.18, 2.0)
    finish(im, "station", 0.34, 4)


def bg_car():
    """Inside Ijichi's car, mountain road going past."""
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("2a2a30"), hexc("0f0f13"))
    im.vgrad(W * 0.08, H * 0.06, W * 0.92, H * 0.56, hexc("8fb0d8"), hexc("d8e6f0"))
    hills(im, H * 0.40, 60, hexc("5b7a8a"), 91, 0.9)
    treeline(im, H * 0.56, 200, hexc("2c4a3a"), 92, 0.95)
    im.rect(0, 0, W * 0.08, H, hexc("1a1a20")); im.rect(W * 0.92, 0, W, H, hexc("1a1a20"))
    im.rect(0, 0, W, H * 0.06, hexc("1a1a20"))
    im.rect(0, H * 0.56, W, H, hexc("2b2b33"))
    im.rrect(W * 0.20, H * 0.58, W * 0.80, H * 0.70, 20, hexc("1f1f26"))
    im.rrect(W * 0.62, H * 0.60, W * 0.78, H * 0.66, 8, hexc("34343e"))
    im.rect(W * 0.49, H * 0.06, W * 0.51, H * 0.56, hexc("1a1a20"))
    finish(im, "car", 0.5)


if __name__ == "__main__":
    print("prologue art ->", OUT)
    bg_home_living(); bg_home_bedroom(); bg_yotsuka_hall(); bg_yotsuka_class()
    bg_town_street(); bg_festival(); bg_station(); bg_car()
