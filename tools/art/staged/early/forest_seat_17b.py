# The Forest Trail's seat, placed by tool (11 Oct 2026). The owner chose ui2_forest2_a for its trail (O55); its seat
# is a sawn plank where the story has a root. art_17b.json repainted that one thing twice (ui2_forest2a_seat_a/b),
# and, as every one-change repaint does, the editor also redrew the rest of the picture a little (about 2% of it
# differs strongly, all over). So only the seat is taken: the largest connected patch that changed inside a window
# round the seat, grown by 22 px and feathered, is laid from the repaint onto the chosen render; every pixel outside
# that patch is the chosen render's own (asserted below). Method note 34.
#
#   tools/py_art.sh tools/art/staged/early/forest_seat_17b.py [a|b]      (default a)
#
# It writes ~/Desktop/JJK Game images/ui2/early/renders/ui2_forest2a_root_00001_.png and prints its sum.
import os, sys, hashlib
import numpy as np
from PIL import Image, ImageChops, ImageFilter
from scipy import ndimage as ndi

E = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
WIN = (380, 760, 1180, 1240)        # a window round the seat, in the render's own 2752 x 1536 pixels
version = (sys.argv[1:] or ["a"])[0]
base = Image.open(os.path.join(E, "renders", "ui2_forest2_a_00001_.png")).convert("RGB")
seat = Image.open(os.path.join(E, "renders", "ui2_forest2a_seat_%s_00001_.png" % version)).convert("RGB")
assert base.size == seat.size == (2752, 1536), (base.size, seat.size)
d = np.asarray(ImageChops.difference(seat, base)).astype(float).mean(axis=2)
strong = d[WIN[1]:WIN[3], WIN[0]:WIN[2]] > 30
lab, n = ndi.label(ndi.binary_closing(strong, iterations=6))
sizes = ndi.sum(strong, lab, range(1, n + 1))
blob = ndi.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)
m = np.zeros(d.shape, bool)
m[WIN[1]:WIN[3], WIN[0]:WIN[2]] = ndi.binary_dilation(blob, iterations=22)
mask = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(9))
out = Image.composite(seat, base, mask)
outside = np.asarray(mask) == 0
assert float(np.asarray(ImageChops.difference(out, base)).astype(float).mean(axis=2)[outside].max()) == 0.0
ys, xs = np.where(~outside)
path = os.path.join(E, "renders", "ui2_forest2a_root_00001_.png")
out.save(path)
print("seat %s placed: the patch is x %d to %d, y %d to %d (%.2f%% of the picture); everything else is the chosen render"
      % (version, xs.min(), xs.max(), ys.min(), ys.max(), (~outside).mean() * 100))
print(path, hashlib.sha256(open(path, "rb").read()).hexdigest())
