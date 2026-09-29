"""Campus map art for the sandbox build: writes game/images/bg/map_campus.png.

It used to paint placeholder backgrounds too; those are now finished Krea
renders (tools/make_bg_workflow.py + tools/install_bg.py), so this script only
draws the map, and skips it if map_campus.png already exists. Pass --force to
redraw it.

    python3 tools/genworld.py [--force]
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, hexc, lerp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "images", "bg")
MAP = os.path.join(OUT, "map_campus.png")
W, H = 1920, 1080


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
    im.save(MAP)
    print("   map_campus")


if __name__ == "__main__":
    if os.path.exists(MAP) and "--force" not in sys.argv:
        print("map_campus.png exists; pass --force to redraw it")
    else:
        os.makedirs(OUT, exist_ok=True)
        print("campus map ->", OUT)
        bg_map()
