# Storehouse B: the editor repainted the view outside correctly (art_15s.json) but widened the doorway to do it.
# The two pictures share one camera, so the part of the repainted view that falls inside the ORIGINAL doorway is
# exactly what the narrow door would show. This puts those pixels, and only those, into the original render:
# everything inside the room, the door frame and both door leaves are the original's own pixels, untouched.
import os, sys, hashlib
from PIL import Image, ImageDraw, ImageFilter, ImageChops
E = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
SRC, VIEW = "ui2_storehouse2_b_00001_.png", "ui2_storehouse2b_view_a_00001_.png"
OUT = "ui2_storehouse2b_doorview_00001_.png"
# the doorway of the original, in its own pixels (2752 x 1536), read off a measuring grid: the opening inside the
# frame, less the two leaves (which swing outward, their free edges at x 1211 and x 1541)
OPENING = (1170, 689, 1583, 1088)
LEFT_LEAF = [(1164, 682), (1213, 709), (1213, 1057), (1164, 1093)]
RIGHT_LEAF = [(1589, 682), (1539, 711), (1539, 1054), (1589, 1091)]
src = Image.open(os.path.join(E, "renders", SRC)).convert("RGB"); view = Image.open(os.path.join(E, "renders", VIEW)).convert("RGB")
assert src.size == view.size == (2752, 1536)
S = 4                                                    # draw the mask four times over, for a clean edge
m = Image.new("L", (src.width * S, src.height * S), 0); d = ImageDraw.Draw(m)
d.rectangle([c * S for c in OPENING], fill=255)
for leaf in (LEFT_LEAF, RIGHT_LEAF): d.polygon([(x * S, y * S) for x, y in leaf], fill=0)
mask = m.resize(src.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
out = Image.composite(view, src, mask); out.save(os.path.join(E, "renders", OUT))
changed = ImageChops.difference(out, src).convert("L").point(lambda v: 255 if v else 0).getbbox()
print("written", OUT, "changed pixels lie within", changed)
print("sha256", hashlib.sha256(open(os.path.join(E, "renders", OUT), "rb").read()).hexdigest())
z = (1060, 620, 1700, 1180)
tiles = [im.crop(z).resize((900, 788), Image.LANCZOS) for im in (src, out)]
sheet = Image.new("RGB", (1810, 788), (20, 20, 20)); sheet.paste(tiles[0], (0, 0)); sheet.paste(tiles[1], (910, 0)); sheet.save(os.path.join(E, "compare_storehouse2b_doorview_zoom.jpg"), quality=90)
full = out.resize((1400, 781), Image.LANCZOS); full.save(os.path.join(E, "compare_storehouse2b_doorview_full.jpg"), quality=90)
