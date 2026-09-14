"""A cheap late-night ramen counter. The last ordinary place in the game."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp
from genworld import finish, OUT, W, H


def bg_diner():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("3a2a22"), hexc("1a120e"))
    # back wall, warm, with a menu strip
    im.rect(0, 0, W, H * 0.58, hexc("4a362a"))
    im.rect(0, H * 0.10, W, H * 0.30, hexc("e8d9b8"), 0.94)
    rnd = random.Random(3)
    for i in range(14):
        x = W * 0.03 + i * W * 0.069
        im.rect(x, H * 0.12, x + W * 0.052, H * 0.28, hexc("f4ecd8"))
        for r in range(4):
            im.rect(x + 6, H * (0.14 + r * 0.033), x + W * 0.052 - 6, H * (0.148 + r * 0.033),
                    hexc("8a4a3a"), rnd.uniform(0.5, 0.9))
    # hanging lamps
    for i in range(4):
        x = W * (0.16 + i * 0.23)
        im.rect(x - 3, 0, x + 3, H * 0.06, hexc("2a1f18"))
        im.poly([(x - 44, H * 0.10), (x + 44, H * 0.10), (x + 26, H * 0.055), (x - 26, H * 0.055)],
                hexc("d8683a"))
        im.glow(x, H * 0.13, 340, hexc("ffb870"), 0.30, 2.0)
    # steam shelf / kitchen pass
    im.rect(0, H * 0.30, W, H * 0.36, hexc("6a5442"))
    im.rect(0, H * 0.355, W, H * 0.375, hexc("8a7258"))
    for i in range(7):
        x = W * 0.06 + i * W * 0.14
        im.ellipse(x, H * 0.335, 34, 18, hexc("cfc2a8"), 0.9)
        im.glow(x, H * 0.31, 90, hexc("ffffff"), 0.18, 2.0)
    # the counter, running across the foreground
    im.rect(0, H * 0.58, W, H, hexc("2a1e18"))
    im.rect(0, H * 0.60, W, H * 0.78, hexc("7a5638"))
    im.rect(0, H * 0.60, W, H * 0.625, hexc("9a7048"))
    for i in range(10):
        y = H * 0.64 + i * H * 0.014
        im.rect(0, y, W, y + 2, hexc("6a4a30"), 0.35)
    # two bowls and two glasses, set for two
    for x, warm in ((W * 0.30, True), (W * 0.66, True)):
        im.ellipse(x, H * 0.645, 86, 30, hexc("1e1a18"))
        im.ellipse(x, H * 0.635, 82, 27, hexc("d8443a"))
        im.ellipse(x, H * 0.632, 68, 21, hexc("c2a068"))
        if warm:
            im.glow(x, H * 0.60, 140, hexc("fff0d0"), 0.16, 2.2)
        im.rrect(x + 108, H * 0.585, x + 146, H * 0.648, 5, hexc("bcd0d8"), 0.75)
    im.vignette(0.46)
    im.grain(6, 2, seed=41)
    im.save(os.path.join(OUT, "diner.png"))
    print("   diner")


if __name__ == "__main__":
    bg_diner()
