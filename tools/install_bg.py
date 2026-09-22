"""
Put a generated background into the game.

    python3 tools/install_bg.py "~/Desktop/JJK Game images/bg_courtyard_00002_.png"
    python3 tools/install_bg.py <render.png> courtyard

Enlarges the render (1408x792 from make_bg_workflow.py) to 1920x1080 with
Catmull-Rom and writes game/images/bg/<name>.png, replacing the placeholder.
The name comes from the file (bg_<name>_0000N_.png) unless given.
"""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, resample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080


def looks_like_static(im):
    ch = im.ch
    diff = n = 0
    for y in range(0, im.h - 1, 7):
        for x in range(0, im.w - 1, 7):
            i, j = (y * im.w + x) * ch, (y * im.w + x + 1) * ch
            diff += abs(im.buf[i] - im.buf[j]) + abs(im.buf[i + 1] - im.buf[j + 1])
            n += 2
    rows = []
    for y in range(0, im.h, max(1, im.h // 40)):
        t = 0
        for x in range(0, im.w, 5):
            i = (y * im.w + x) * ch
            t += im.buf[i] + im.buf[i + 1] + im.buf[i + 2]
        rows.append(t / (3.0 * len(range(0, im.w, 5))))
    mean = sum(rows) / len(rows)
    spread = (sum((r - mean) ** 2 for r in rows) / len(rows)) ** 0.5
    # Measured: static 13.6-13.8 / 6.5-7.7, real 3.6-5.1 / 24-48. Both must
    # fail, so a genuinely dark, even night scene (low spread, smooth) passes.
    return diff / float(n) > 9 and spread < 15


def install(src, name=None):
    src = os.path.expanduser(src)
    if not name:
        m = re.match(r"bg_(.+?)_\d+_?\.png$", os.path.basename(src))
        if not m:
            raise SystemExit("can't tell the location from %r -- pass it as the second argument"
                             % os.path.basename(src))
        name = m.group(1)
    im = load(src)
    if im.ch == 4:
        rgb = Img(im.w, im.h, alpha=False)
        for p in range(im.w * im.h):
            rgb.buf[p * 3:p * 3 + 3] = im.buf[p * 4:p * 4 + 3]
        im = rgb
    # Crop to exactly 16:9 before enlarging, should a render come back off-ratio.
    target = W / float(H)
    if abs(im.w / float(im.h) - target) > 0.002:
        from raster import crop
        if im.w / float(im.h) > target:
            nw = int(im.h * target); x0 = (im.w - nw) // 2
            im = crop(im, x0, 0, x0 + nw, im.h)
        else:
            nh = int(im.w / target); y0 = (im.h - nh) // 2
            im = crop(im, 0, y0, im.w, y0 + nh)
    # A failed render comes back as blotchy coloured static (it happened to all
    # four night-room candidates in the first batch): neighbouring pixels differ
    # far more than in a real picture, and there is no large-scale structure --
    # every row averages to much the same grey, where a real picture runs from
    # sky to ground.
    if looks_like_static(im):
        raise SystemExit("%s looks like static, not a picture -- the render failed; re-run it"
                         % os.path.basename(src))
    out = resample(im, W, H)
    dest = os.path.join(ROOT, "game", "images", "bg", name + ".png")
    out.save(dest)
    print("%dx%d -> %s" % (im.w, im.h, dest))
    return dest


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); raise SystemExit(1)
    install(args[0], args[1] if len(args) > 1 else None)
