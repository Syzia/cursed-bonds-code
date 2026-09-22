"""
Build the Comfy Cloud workflow that generates location backgrounds.

    python3 tools/make_bg_workflow.py courtyard classroom your_room_night

One row per location, four candidates each, from tools/bgs/prompts/<name>.txt.
Writes `backgrounds.json` into ~/Desktop/JJK Game images. Drag it onto the Comfy
Cloud canvas and press Run; results are saved as `bg_<name>_0000N_.png`.

Model and sampler are copied from the reference character render, so the
backgrounds and the sprites come out of the same model with the same settings.
Pictures are made at 1408x792 -- exactly 16:9, about a megapixel, which is what
the model is comfortable at -- and enlarged to the game's 1920x1080 by
tools/install_bg.py.
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_workflow import Graph, recipe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
REFERENCE = os.path.join(IMAGES, "Krea2_turbo_00001_.png")
W, H = 1408, 792
CANDIDATES = 4


def bg_prompt(name):
    """A location's scene description followed by the shared style paragraph.

    Kept in separate files so the style can be tuned once for every location.
    """
    scene = open(os.path.join(ROOT, "tools", "bgs", "prompts", name + ".txt")).read().strip()
    style = open(os.path.join(ROOT, "tools", "bgs", "style.txt")).read().strip()
    return scene + "\n\n" + style


def build(names):
    r = recipe(REFERENCE)
    g = Graph()
    g.add("MarkdownNote", (0, -440), (640, 380), title="Start here",
          color="#222", bgcolor="#000", widgets=[
        "## Backgrounds: %s\n\n"
        "Press **Run**. Each row makes %d versions of one location, shown in "
        "its Save Image box.\n\n"
        "Save the best of each into `JJK Game images`, keeping Comfy's names "
        "(`bg_<location>_0000N_.png`). If you can't choose, save them all.\n\n"
        "What makes a good one: no people, an open floor or ground across the "
        "bottom where a character could stand, and a view at standing eye level."
        % (", ".join(names), CANDIDATES)])

    unet = g.add("UNETLoader", (0, 0), (320, 82), r["unet"], outs=[("MODEL", "MODEL")])
    clip = g.add("CLIPLoader", (0, 110), (320, 106), r["clip"], outs=[("CLIP", "CLIP")])
    vae = g.add("VAELoader", (0, 245), (320, 58), [r["vae"]], outs=[("VAE", "VAE")])
    size = g.add("EmptyLatentImage", (0, 340), (320, 106), [W, H, CANDIDATES],
                 outs=[("LATENT", "LATENT")], title="Picture size (16:9)")

    row_h = 700
    for i, name in enumerate(names):
        y = i * row_h
        prompt = bg_prompt(name)
        pos = g.add("CLIPTextEncode", (360, y), (460, 330), [prompt],
                    ins=[("clip", "CLIP")], outs=[("CONDITIONING", "CONDITIONING")],
                    title="Prompt: %s" % name)
        neg = g.add("ConditioningZeroOut", (360, y + 360), (240, 26),
                    ins=[("conditioning", "CONDITIONING")], outs=[("CONDITIONING", "CONDITIONING")])
        ks = g.add("KSampler", (850, y), (300, 262),
                   [20260922 + i * 101, "randomize", r["steps"], r["cfg"], r["sampler"], r["scheduler"], 1.0],
                   ins=[("model", "MODEL"), ("positive", "CONDITIONING"),
                        ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
                   outs=[("LATENT", "LATENT")])
        dec = g.add("VAEDecode", (850, y + 300), (200, 46),
                    ins=[("samples", "LATENT"), ("vae", "VAE")], outs=[("IMAGE", "IMAGE")])
        save = g.add("SaveImage", (1180, y), (1000, 640), ["bg_%s" % name],
                     ins=[("images", "IMAGE")], outs=[])
        g.wire(clip, 0, pos, "clip")
        g.wire(pos, 0, neg, "conditioning")
        g.wire(unet, 0, ks, "model")
        g.wire(pos, 0, ks, "positive")
        g.wire(neg, 0, ks, "negative")
        g.wire(size, 0, ks, "latent_image")
        g.wire(ks, 0, dec, "samples")
        g.wire(vae, 0, dec, "vae")
        g.wire(dec, 0, save, "images")
        g.group(name.replace("_", " ").upper(), 340, y - 40, 1860, row_h - 20, "#3f4f5a")
    wf = g.dump()
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [120, 480]}
    return wf


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        print(__doc__); raise SystemExit(1)
    for n in names:
        if not os.path.exists(os.path.join(ROOT, "tools", "bgs", "prompts", n + ".txt")):
            raise SystemExit("no prompt for %r in tools/bgs/prompts/" % n)
    wf = build(names)
    out = os.path.join(IMAGES, "backgrounds.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("rows      %s (%d candidates each, %dx%d)" % (", ".join(names), CANDIDATES, W, H))
    print("workflow -> %s" % out)
