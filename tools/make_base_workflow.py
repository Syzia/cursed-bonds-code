"""
Build the Comfy Cloud workflow that generates a character's base picture.

    python3 tools/make_base_workflow.py megumi

Reads the prompt from tools/chars/prompts/<character>.txt and writes
`<character>_base.json` into ~/Desktop/JJK Game images. Drag it onto the
canvas and press Run: it makes four candidates at once, saved as
`<character>_base_0000N_.png`, so there is a choice instead of a re-roll.

Every character must come out in the same art style, so nothing about the
model is chosen here. The model, text encoder, VAE, sampler, step count and
picture size are copied out of the reference render — the first Yuji picture,
whose look everyone else has to match.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_workflow import Graph, recipe
from pngread import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
REFERENCE = os.path.join(IMAGES, "Krea2_turbo_00001_.png")
CANDIDATES = 4


def build(char, prompt):
    r = recipe(REFERENCE)
    ref = load(REFERENCE)
    g = Graph()

    g.add("MarkdownNote", (0, -380), (640, 320), title="Start here",
          color="#222", bgcolor="#000", widgets=[
        "## %s: base picture\n\n"
        "Press **Run**. It makes %d versions at once, in the Save Image box.\n\n"
        "Save the one you like best into `JJK Game images` and keep the name "
        "Comfy gives it. If you can't choose, save them all and I'll compare.\n\n"
        "What makes a good one: the whole body inside the picture with green "
        "above the head and below the feet, facing forward, a calm face. The "
        "face gets repainted for the other expressions, but hair, clothes and "
        "pose are permanent." % (char.capitalize(), CANDIDATES)])

    unet = g.add("UNETLoader", (0, 0), (320, 82), r["unet"], outs=[("MODEL", "MODEL")])
    clip = g.add("CLIPLoader", (0, 110), (320, 106), r["clip"], outs=[("CLIP", "CLIP")])
    vae = g.add("VAELoader", (0, 245), (320, 58), [r["vae"]], outs=[("VAE", "VAE")])
    size = g.add("EmptyLatentImage", (0, 340), (320, 106), [ref.w, ref.h, CANDIDATES],
                 outs=[("LATENT", "LATENT")], title="Picture size (same as Yuji)")

    pos = g.add("CLIPTextEncode", (360, 0), (460, 330), [prompt],
                ins=[("clip", "CLIP")], outs=[("CONDITIONING", "CONDITIONING")],
                title="Prompt: %s" % char)
    neg = g.add("ConditioningZeroOut", (360, 360), (240, 26),
                ins=[("conditioning", "CONDITIONING")], outs=[("CONDITIONING", "CONDITIONING")])
    ks = g.add("KSampler", (850, 0), (300, 262),
               [424242, "randomize", r["steps"], r["cfg"], r["sampler"], r["scheduler"], 1.0],
               ins=[("model", "MODEL"), ("positive", "CONDITIONING"),
                    ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
               outs=[("LATENT", "LATENT")])
    dec = g.add("VAEDecode", (850, 300), (200, 46),
                ins=[("samples", "LATENT"), ("vae", "VAE")], outs=[("IMAGE", "IMAGE")])
    save = g.add("SaveImage", (1180, 0), (700, 760), ["%s_base" % char],
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
    wf = g.dump()
    wf["extra"]["ds"] = {"scale": 0.6, "offset": [80, 420]}
    return wf, r, (ref.w, ref.h)


if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit(1)
    char = sys.argv[1]
    pfile = os.path.join(ROOT, "tools", "chars", "prompts", char + ".txt")
    if not os.path.exists(pfile):
        raise SystemExit("no prompt at %s" % pfile)
    prompt = open(pfile).read().strip()

    wf, r, (w, h) = build(char, prompt)
    out = os.path.join(IMAGES, "%s_base.json" % char)
    with open(out, "w") as f:
        json.dump(wf, f, indent=1)
    print("model     %s, %s / %s, %d steps, cfg %s" % (r["unet"][0], r["sampler"], r["scheduler"], r["steps"], r["cfg"]))
    print("size      %dx%d, %d candidates per Run" % (w, h, CANDIDATES))
    print("workflow -> %s" % out)
