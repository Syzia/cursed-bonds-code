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
