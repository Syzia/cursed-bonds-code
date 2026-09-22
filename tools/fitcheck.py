"""
See characters standing in a background exactly as the game would show them.

    python3 tools/fitcheck.py <background.png> [yuji megumi ...] [--out file.png]

Resizes the background to 1920x1080 and places each character's neutral sprite
the way the game's stage transforms do (yalign 1.0, zoom ~0.62, spread across
the screen), so a background can be judged with people in it -- scale, the
ground they stand on, whether the lighting and style sit together -- without
launching Ren'Py.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, resample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
# The game's pos_l / pos_cl / pos_c / pos_cr / pos_r, as (xalign, zoom).
SLOTS = {1: [(0.5, 0.64)], 2: [(0.35, 0.62), (0.65, 0.62)],
         3: [(0.17, 0.62), (0.5, 0.64), (0.83, 0.62)]}


def rgb(im):
    if im.ch == 3:
        return im
    o = Img(im.w, im.h, alpha=False)
    for p in range(im.w * im.h):
        o.buf[p * 3:p * 3 + 3] = im.buf[p * im.ch:p * im.ch + 3]
    return o


def compose(bg_path, chars, out):
    canvas = resample(rgb(load(os.path.expanduser(bg_path))), W, H)
    for (xa, zoom), c in zip(SLOTS.get(len(chars), SLOTS[3]), chars):
        spr = load(os.path.join(ROOT, "game", "images", "char", "%s_neutral.png" % c))
        s = resample(spr, int(spr.w * zoom), int(spr.h * zoom))
        x = int((W - s.w) * xa)
        y = H - s.h                                     # yalign 1.0
        for sy in range(s.h):
            ty = y + sy
            if not (0 <= ty < H):
                continue
            for sx in range(s.w):
                a = s.buf[(sy * s.w + sx) * 4 + 3]
                tx = x + sx
                if a == 0 or not (0 <= tx < W):
                    continue
                i, j = (sy * s.w + sx) * 4, (ty * W + tx) * 3
                f = a / 255.0
                for k in range(3):
                    canvas.buf[j + k] = int(s.buf[i + k] * f + canvas.buf[j + k] * (1 - f))
    canvas.save(out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); raise SystemExit(1)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "fitcheck.png"
    args = [a for a in args if a != out]
    chars = args[1:] or ["yuji", "megumi"]
    print(compose(args[0], chars, out))
