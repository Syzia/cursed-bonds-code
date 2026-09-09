import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anime import Cel, hexc
import char_rig as rig
import char_hair as hair

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "game", "images", "char")

SPECS = {
    "yuji": dict(skin="#f6d3b4", iris="#7a4a2c", hair="#f2748c", hair_dark="#8f3d52",
                 style="undercut", uniform="#1c1f2e", inner="#b8323c",
                 eye_marks=True, hood=True, build=1.04),
    "megumi": dict(skin="#f7dcc4", iris="#2f6f63", hair="#1b2233", hair_dark="#0e1420",
                   style="spiky_black", uniform="#1c1f2e", inner="#22283a",
                   build=0.96),
    "nobara": dict(skin="#fadfc8", iris="#8a5a34", hair="#d2762e", hair_dark="#8f4d1c",
                   style="bob", uniform="#1c1f2e", inner="#2a2f42", build=0.92),
}


def render(key, expr="neutral", path=None):
    spec = SPECS[key]
    c = Cel()
    hair.STYLES[spec["style"]](c, hexc(spec["hair"]), hexc(spec["hair_dark"]), back=True)
    rig.body(c, spec)
    rig.face(c, spec, expr)
    hair.STYLES[spec["style"]](c, hexc(spec["hair"]), hexc(spec["hair_dark"]), back=False)
    p = path or os.path.join(OUT, "_test_%s_%s.png" % (key, expr))
    c.save(p)
    return p


if __name__ == "__main__":
    keys = sys.argv[1:] or ["yuji"]
    for k in keys:
        t = time.time()
        p = render(k)
        print("  %-8s %5.1fs  %s" % (k, time.time()-t, p))
