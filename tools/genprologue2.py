"""Remaining pre-campus backgrounds: Sana's room, the konbini kerb, the street."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp
from genworld import finish, treeline, hills, OUT, W, H


def sana_room(night):
    im = Img(W, H)
    if night:
        im.vgrad(0, 0, W, H, hexc("2b2a3c"), hexc("14131e"))
        im.rect(0, 0, W, H * 0.70, hexc("332f45"))
        wall, floor, bed = hexc("332f45"), hexc("3a3348"), hexc("4a4060")
    else:
        im.vgrad(0, 0, W, H, hexc("cfc3b4"), hexc("8b8073"))
        im.rect(0, 0, W, H * 0.70, hexc("d8ccbc"))
        wall, floor, bed = hexc("d8ccbc"), hexc("c2ab86"), hexc("e0d0dc")

    # curtained window
    im.rect(W * 0.56, H * 0.12, W * 0.92, H * 0.52, hexc("6a5f52") if not night else hexc("221f2e"))
    if night:
        im.vgrad(W * 0.57, H * 0.13, W * 0.91, H * 0.51, hexc("2a3352"), hexc("161b30"))
        im.glow(W * 0.74, H * 0.30, 300, hexc("cfd8ff"), 0.30, 2.0)   # street light
    else:
        im.vgrad(W * 0.57, H * 0.13, W * 0.91, H * 0.51, hexc("bcd8ea"), hexc("eef4f8"))
        im.glow(W * 0.74, H * 0.30, 460, hexc("fff6e2"), 0.26, 2.0)
    for i in range(2):
        x = W * (0.555 + i * 0.335)
        im.rect(x, H * 0.11, x + W * 0.035, H * 0.53, hexc("b0708a") if not night else hexc("4a3348"))

    # tatami floor
    im.rect(0, H * 0.70, W, H, floor)
    for i in range(6):
        y = H * 0.74 + i * H * 0.045
        im.rect(0, y, W, y + 3, lerp(floor, hexc("000000"), 0.18), 0.5)

    # low bed / futon
    im.rrect(W * 0.04, H * 0.56, W * 0.44, H * 0.84, 14, bed)
    im.rrect(W * 0.06, H * 0.52, W * 0.18, H * 0.60, 10, hexc("f4eef4") if not night else hexc("cfc6d8"))
    # desk + lamp
    im.rrect(W * 0.50, H * 0.62, W * 0.76, H * 0.70, 6, hexc("8a6b46") if not night else hexc("4a3a28"))
    im.rect(W * 0.60, H * 0.52, W * 0.63, H * 0.62, hexc("6a6a72"))
    im.poly([(W*0.575, H*0.52), (W*0.655, H*0.52), (W*0.64, H*0.47), (W*0.59, H*0.47)],
            hexc("f0e4c8") if not night else hexc("6a6250"))
    if not night:
        im.glow(W * 0.615, H * 0.53, 260, hexc("fff2cc"), 0.30, 2.0)
    # photos scattered on the floor
    rnd = random.Random(12)
    for i in range(9):
        x = rnd.uniform(W*0.10, W*0.86); y = rnd.uniform(H*0.86, H*0.97)
        im.rrect(x, y, x + 78, y + 56, 2, hexc("efe8dc") if not night else hexc("8f8798"), 0.95)
        im.rect(x+6, y+6, x+72, y+44, lerp(hexc("6a8fb0"), hexc("c88a6a"), rnd.random()), 0.9)
    finish(im, "sana_room_night" if night else "sana_room", 0.50 if night else 0.34, 5)


def konbini_night():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("0e0f1a"), hexc("1c1d2c"))
    # store front: the one bright thing on the street
    im.rect(W * 0.16, H * 0.16, W * 0.86, H * 0.66, hexc("14151f"))
    im.rect(W * 0.18, H * 0.22, W * 0.84, H * 0.62, hexc("e8f2ea"), 0.96)
    im.rect(W * 0.16, H * 0.16, W * 0.86, H * 0.225, hexc("f2f6f4"))
    im.rect(W * 0.16, H * 0.225, W * 0.86, H * 0.245, hexc("2f8f5a"))
    im.rect(W * 0.16, H * 0.245, W * 0.86, H * 0.262, hexc("d84a3a"))
    for i in range(5):
        x = W * (0.20 + i * 0.135)
        im.rect(x, H * 0.30, x + W * 0.10, H * 0.60, hexc("cfe0d4"), 0.8)
        im.rect(x, H * 0.30, x + W * 0.10, H * 0.32, hexc("9fb8a8"), 0.8)
    im.glow(W * 0.51, H * 0.40, 900, hexc("dff4e6"), 0.34, 1.8)
    # vending machines
    for i, col in enumerate([hexc("c8342e"), hexc("2f5fa8")]):
        x = W * (0.02 + i * 0.075)
        im.rect(x, H * 0.34, x + W * 0.066, H * 0.66, col)
        im.rect(x + 6, H * 0.37, x + W * 0.066 - 6, H * 0.52, hexc("f0f4f2"), 0.9)
        im.glow(x + W * 0.033, H * 0.44, 200, col, 0.5, 2.0)
    # kerb + road
    im.rect(0, H * 0.66, W, H * 0.72, hexc("3a3a44"))
    im.rect(0, H * 0.70, W, H * 0.715, hexc("6a6a74"))
    im.rect(0, H * 0.72, W, H, hexc("1e1e28"))
    im.rect(W * 0.30, H * 0.88, W * 0.70, H * 0.90, hexc("8a8a70"), 0.5)
    # street light pooling on the left
    im.rect(W * 0.90, H * 0.02, W * 0.915, H * 0.66, hexc("2a2a34"))
    im.glow(W * 0.90, H * 0.10, 420, hexc("ffe6b0"), 0.32, 2.0)
    finish(im, "konbini", 0.50)


def street_morning():
    im = Img(W, H)
    im.vgrad(0, 0, W, H * 0.52, hexc("8fbfe8"), hexc("e2eef6"), gamma=1.3)
    im.ellipse(W * 0.20, H * 0.14, 150, 52, (255, 255, 255), 0.8)
    im.ellipse(W * 0.78, H * 0.10, 190, 60, (255, 255, 255), 0.7)
    # the family house, front on
    im.rect(W * 0.08, H * 0.26, W * 0.62, H * 0.70, hexc("ded4c4"))
    im.poly([(W * 0.04, H * 0.27), (W * 0.66, H * 0.27), (W * 0.35, H * 0.14)], hexc("5a4a44"))
    im.rect(W * 0.13, H * 0.34, W * 0.24, H * 0.48, hexc("7fa0c0"), 0.92)
    im.rect(W * 0.30, H * 0.34, W * 0.41, H * 0.48, hexc("7fa0c0"), 0.92)
    im.rect(W * 0.46, H * 0.36, W * 0.56, H * 0.70, hexc("6b4f3a"))   # front door
    im.rect(W * 0.06, H * 0.56, W * 0.62, H * 0.60, hexc("c4b8a6"))
    # neighbours receding to the corner on the right
    for i in range(3):
        x = W * (0.66 + i * 0.12)
        im.rect(x, H * (0.34 + i * 0.03), x + W * 0.11, H * 0.68, lerp(hexc("cfc6b8"), hexc("9f968a"), i/2.0))
        im.poly([(x - 10, H * (0.34 + i*0.03)), (x + W*0.11 + 10, H * (0.34 + i*0.03)),
                 (x + W*0.055, H * (0.28 + i*0.03))], hexc("4a4038"))
    im.rect(0, H * 0.68, W, H * 0.74, hexc("b8b2a6"))     # pavement
    im.rect(0, H * 0.74, W, H, hexc("6e6e74"))            # road
    im.rect(W * 0.30, H * 0.86, W * 0.70, H * 0.875, hexc("d8d2b0"), 0.6)
    for x in (W * 0.04, W * 0.72):
        im.rect(x - 6, H * 0.20, x + 6, H * 0.70, hexc("4a4038"))
        im.rect(x - 52, H * 0.24, x + 52, H * 0.25, hexc("4a4038"))
    finish(im, "street_morning", 0.30, 4)


def home_bedroom_night():
    im = Img(W, H)
    im.vgrad(0, 0, W, H, hexc("22202e"), hexc("101018"))
    im.rect(0, 0, W, H * 0.68, hexc("2a2736"))
    im.rect(W * 0.06, H * 0.12, W * 0.36, H * 0.50, hexc("191826"))
    im.vgrad(W * 0.07, H * 0.13, W * 0.35, H * 0.49, hexc("1e2742"), hexc("30395c"))
    im.glow(W * 0.21, H * 0.28, 300, hexc("aab8e8"), 0.20, 2.0)
    im.rect(0, H * 0.68, W, H, hexc("2e2620"))
    im.rrect(W * 0.52, H * 0.56, W * 0.96, H * 0.88, 12, hexc("39304a"))
    im.rrect(W * 0.54, H * 0.52, W * 0.66, H * 0.60, 10, hexc("b8b0c0"))
    im.rrect(W * 0.04, H * 0.58, W * 0.34, H * 0.66, 6, hexc("4a3c2c"))
    # the hall light under the door
    im.rect(W * 0.40, H * 0.20, W * 0.50, H * 0.70, hexc("1a1622"))
    im.rect(W * 0.40, H * 0.685, W * 0.50, H * 0.706, hexc("ffe8b0"), 0.85)
    im.glow(W * 0.45, H * 0.70, 200, hexc("ffd98a"), 0.30, 2.2)
    finish(im, "home_bedroom_night", 0.55)


if __name__ == "__main__":
    print("prologue art 2 ->", OUT)
    sana_room(False); sana_room(True); konbini_night(); street_morning(); home_bedroom_night()
