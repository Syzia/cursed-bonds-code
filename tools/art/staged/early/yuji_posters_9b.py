# Yuji's posters, placed by tool (11 Oct 2026). The owner chose ui2_yuji_room_b (O60); its posters came back with
# lettering, one of them the name and likeness of a famous film monster, and no poster in the game carries either.
# art_9b.json painted the posters again twice (ui2_yuji_room_b_posters_a/b). Version B is the one used: version A
# drew a walking machine that is a known film's design. As every one-change repaint does, the editor also redrew
# the rest of the room a little, so only the posters are taken: inside a window round each group of posters, every
# large patch that changed is filled, grown by 8 px and feathered, and laid from the repaint onto the chosen render.
# Every pixel outside those patches is the chosen render's own (asserted below). Method note 37.
#
#   tools/py_art.sh tools/art/staged/early/yuji_posters_9b.py [a|b]      (default b)
#
# It writes ~/Desktop/JJK Game images/ui2/early/renders/ui2_yuji_room_b_placed_00001_.png and prints its sum.
import os, sys, hashlib
import numpy as np
from PIL import Image, ImageChops, ImageFilter
from scipy import ndimage as ndi

E = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
# a window round each group of posters, in the render's own 2752 x 1536 pixels
WINDOWS = [(526, 435, 646, 838),        # the poster on the left wall
           (676, 478, 1191, 903),       # the group of three on the far wall, left of the post
           (1236, 487, 1478, 818),      # the first right of the post
           (1468, 492, 1701, 815),      # the second right of the post
           (1708, 468, 1846, 823)]      # the poster on the right wall
version = (sys.argv[1:] or ["b"])[0]
base = Image.open(os.path.join(E, "renders", "ui2_yuji_room_b_00001_.png")).convert("RGB")
new = Image.open(os.path.join(E, "renders", "ui2_yuji_room_b_posters_%s_00001_.png" % version)).convert("RGB")
assert base.size == new.size == (2752, 1536), (base.size, new.size)
d = np.asarray(ImageChops.difference(new, base)).astype(float).mean(axis=2)
m = np.zeros(d.shape, bool)
for x0, y0, x1, y1 in WINDOWS:
    strong = ndi.binary_closing(d[y0:y1, x0:x1] > 30, iterations=10)
    lab, n = ndi.label(strong)
    if not n:
        raise SystemExit("nothing changed in the window %s: is this the right repaint?" % ((x0, y0, x1, y1),))
    sizes = ndi.sum(strong, lab, range(1, n + 1))
    keep = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s >= 1500])
    m[y0:y1, x0:x1] = ndi.binary_dilation(ndi.binary_fill_holes(keep), iterations=8)
mask = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(4))
out = Image.composite(new, base, mask)
outside = np.asarray(mask) == 0
assert float(np.asarray(ImageChops.difference(out, base)).astype(float).mean(axis=2)[outside].max()) == 0.0
path = os.path.join(E, "renders", "ui2_yuji_room_b_placed_00001_.png")
out.save(path)
print("posters of repaint %s placed: %.2f%% of the picture is from the repaint; everything else is the chosen render"
      % (version, (~outside).mean() * 100))
print(path, hashlib.sha256(open(path, "rb").read()).hexdigest())
