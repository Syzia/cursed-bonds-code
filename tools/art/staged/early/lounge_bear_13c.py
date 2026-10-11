# The lounge's bear, placed by tool (11 Oct 2026). The owner chose ui2_teachers_lounge_b (O67). On its sofa sat a rag
# doll with hair and a dress, and the Principal's dolls are stuffed creatures (O67). art_13c.json changed that one
# thing twice (ui2_teachers_lounge_b_bear_a/b): a half-sewn cloth bear. As every one-change repaint does, the editor
# also redrew the rest of the room a little, so only the bear is taken: inside a window round the doll, every large
# patch that changed is filled, grown by 8 px and feathered, and laid from the repaint onto the chosen render. Every
# pixel outside those patches is the chosen render's own (asserted below). Method notes 37 and 38.
#
#   tools/py_art.sh tools/art/staged/early/lounge_bear_13c.py [a|b]      (default a)
#
# It writes ~/Desktop/JJK Game images/ui2/early/renders/ui2_teachers_lounge_b_placed_00001_.png and prints its sum.
import os, sys, hashlib
import numpy as np
from PIL import Image, ImageChops, ImageFilter
from scipy import ndimage as ndi

E = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
WIN = (1540, 820, 1860, 1110)        # a window round the doll on the sofa, in the render's own 2752 x 1536 pixels
version = (sys.argv[1:] or ["a"])[0]
base = Image.open(os.path.join(E, "renders", "ui2_teachers_lounge_b_00001_.png")).convert("RGB")
new = Image.open(os.path.join(E, "renders", "ui2_teachers_lounge_b_bear_%s_00001_.png" % version)).convert("RGB")
assert base.size == new.size == (2752, 1536), (base.size, new.size)
d = np.asarray(ImageChops.difference(new, base)).astype(float).mean(axis=2)
x0, y0, x1, y1 = WIN
strong = ndi.binary_closing(d[y0:y1, x0:x1] > 30, iterations=10)
lab, n = ndi.label(strong)
if not n:
    raise SystemExit("nothing changed in the window: is this the right repaint?")
sizes = ndi.sum(strong, lab, range(1, n + 1))
keep = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s >= 600])
m = np.zeros(d.shape, bool)
m[y0:y1, x0:x1] = ndi.binary_dilation(ndi.binary_fill_holes(keep), iterations=8)
mask = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(4))
out = Image.composite(new, base, mask)
outside = np.asarray(mask) == 0
assert float(np.asarray(ImageChops.difference(out, base)).astype(float).mean(axis=2)[outside].max()) == 0.0
ys, xs = np.where(~outside)
path = os.path.join(E, "renders", "ui2_teachers_lounge_b_placed_00001_.png")
out.save(path)
print("bear %s placed: the patch is x %d to %d, y %d to %d (%.2f%% of the picture); everything else is the chosen render"
      % (version, xs.min(), xs.max(), ys.min(), ys.max(), (~outside).mean() * 100))
print(path, hashlib.sha256(open(path, "rb").read()).hexdigest())
