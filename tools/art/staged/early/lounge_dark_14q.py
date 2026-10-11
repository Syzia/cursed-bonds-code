# The Staff Building Steps at Night: the editor's two tries at "the ground-floor windows of the teachers' house are
# dark" (art_14q.json) each changed something else as well (version A lit the office pavilion's screens; version B
# took the red curtain from the house's door). All three pictures share one camera, so the ground-floor strip of the
# teachers' house is taken from version A of the repaint, which darkened it and kept the curtain, and placed on the
# night picture the owner chose (art_14p's night A). Every other pixel is the chosen night's own.
import os, hashlib
from PIL import Image, ImageDraw, ImageFilter, ImageChops
E = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
SRC, FIX, OUT = "ui2_staff_yard_night_a_00001_.png", "ui2_staff_yard_night2_a_00001_.png", "ui2_staff_yard_night_lounge_00001_.png"
STRIP = (2236, 786, 2752, 968)          # the house's ground floor, in the render's own pixels (2752 x 1536)
src = Image.open(os.path.join(E, "renders", SRC)).convert("RGB"); fix = Image.open(os.path.join(E, "renders", FIX)).convert("RGB")
assert src.size == fix.size == (2752, 1536)
m = Image.new("L", src.size, 0); ImageDraw.Draw(m).rectangle(STRIP, fill=255); m = m.filter(ImageFilter.GaussianBlur(3))
out = Image.composite(fix, src, m); out.save(os.path.join(E, "renders", OUT))
box = ImageChops.difference(out, src).convert("L").point(lambda v: 255 if v else 0).getbbox()
print("written", OUT, "changed pixels lie within", box, "sha256", hashlib.sha256(open(os.path.join(E, "renders", OUT), "rb").read()).hexdigest()[:16])
z = (2050, 150, 2752, 1000)
a, b = [im.crop(z).resize((600, 727), Image.LANCZOS) for im in (src, out)]
s = Image.new("RGB", (1210, 727), (20, 20, 20)); s.paste(a, (0, 0)); s.paste(b, (610, 0)); s.save(os.path.join(E, "compare_staff_night_lounge_placed.jpg"), quality=90)
out.resize((1400, 781), Image.LANCZOS).save(os.path.join(E, "compare_staff_night_final.jpg"), quality=90)
