"""
Build a ComfyUI workflow that paints a character's five other expressions.

    python3 tools/make_workflow.py "~/Desktop/JJK Game images/Krea2_turbo_00001_.png" yuji

Writes `<character>_expressions.json` beside the render. Drag it onto the Comfy
Cloud canvas, upload the render and its face mask into the two Load Image boxes,
press Run once, and every row paints one expression.

Nothing about the model has to be typed in. ComfyUI hides the whole workflow
that made a picture inside the PNG, so this reads the render's own metadata and
copies its model, text encoder, VAE, sampler, step count and prompt. The prompt
is kept word for word except the expression, which keeps the character looking
the same as the picture it came from.

How each row works: the render is encoded, the model is allowed to repaint only
inside the face mask (see tools/facemask.py) at a low denoise, and the result is
composited back over the untouched original — so the hair, body, uniform and
green backdrop come back byte-identical in all five.
"""
import sys, os, re, json, struct, zlib, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# (expression, words that replace the neutral phrase, denoise)
# Mouth-open expressions need more room to move than the ones that only change
# the eyes and brows. Past ~0.6 it stops being the same person.
EXPRESSIONS = [
    ("happy",     "smiling warmly, eyes slightly narrowed, raised brows",             0.40),
    ("serious",   "level stare, mouth a flat line, lowered brows",                    0.40),
    ("sad",       "downcast eyes, brows angled up at the inner ends, small frown",    0.42),
    ("angry",     "angry glare, furrowed brows, teeth showing slightly",              0.50),
    ("surprised", "wide eyes, raised brows, mouth open slightly",                     0.52),
]

NEUTRAL = re.compile(r"neutral[^,\n]*expression|neutral expression[^,\n]*", re.I)


# ------------------------------------------------------------ reading the PNG
def png_text(path):
    """Every text chunk in a PNG — where ComfyUI keeps the workflow."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("%s is not a PNG" % path)
    out, i = {}, 8
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        kind, body = data[i + 4:i + 8], data[i + 8:i + 8 + n]
        if kind == b"tEXt":
            k, v = body.split(b"\0", 1)
            out[k.decode()] = v.decode("latin1")
        elif kind == b"zTXt":
            k, rest = body.split(b"\0", 1)
            out[k.decode()] = zlib.decompress(rest[1:]).decode("utf8")
        elif kind == b"iTXt":
            k, rest = body.split(b"\0", 1)
            compressed, rest = rest[0], rest[2:]
            _, rest = rest.split(b"\0", 1)
            _, txt = rest.split(b"\0", 1)
            out[k.decode()] = (zlib.decompress(txt) if compressed else txt).decode("utf8")
        i += 12 + n
    return out


def recipe(path):
    """Model files, sampler settings and prompt that produced this render."""
    meta = png_text(path)
    if "prompt" not in meta:
        raise SystemExit("no workflow inside %s — was it saved by ComfyUI's Save "
                         "Image node, and not re-saved by another program since?" % path)
    graph = json.loads(meta["prompt"])

    def node(ref):
        return graph[ref[0]] if isinstance(ref, list) else None

    def resolve(v):
        """Follow a value through switches, previews and joins to the text."""
        if not isinstance(v, list):
            return v
        n = graph[v[0]]
        t, ins = n["class_type"], n["inputs"]
        if t.startswith("Primitive"):
            return ins["value"]
        if t == "PreviewAny":
            return resolve(ins["source"])
        if t == "ComfySwitchNode":
            return resolve(ins["on_true"] if resolve(ins["switch"]) else ins["on_false"])
        if t == "StringConcatenate":
            return (resolve(ins["string_a"]) or "") + ins.get("delimiter", "") + (resolve(ins["string_b"]) or "")
        raise SystemExit("the prompt runs through a %s node, which I can't read "
                         "back — pass it with --prompt-file instead" % t)

    ks = next(n for n in graph.values() if n["class_type"] == "KSampler")
    ki = ks["inputs"]

    def upstream(ref, want):
        """Walk model/switch/lora links back to the loader of type `want`."""
        seen = 0
        while isinstance(ref, list) and seen < 20:
            n = graph[ref[0]]
            if n["class_type"] == want:
                return n["inputs"]
            ins = n["inputs"]
            if n["class_type"] == "ComfySwitchNode":
                ref = ins["on_true"] if resolve(ins["switch"]) else ins["on_false"]
            else:
                ref = ins.get("model") or ins.get("clip") or ins.get("samples")
            seen += 1
        return None

    pos = node(ki["positive"])
    unet = upstream(ki["model"], "UNETLoader")
    clip = upstream(pos["inputs"]["clip"], "CLIPLoader")
    vae_ref = node(next(n for n in graph.values() if n["class_type"] == "VAEDecode")["inputs"]["vae"])
    return {
        "prompt":    resolve(pos["inputs"]["text"]),
        "unet":      [unet["unet_name"], unet.get("weight_dtype", "default")],
        "clip":      [clip["clip_name"], clip["type"], clip.get("device", "default")],
        "vae":       vae_ref["inputs"]["vae_name"],
        "steps":     ki["steps"],
        "cfg":       ki["cfg"],
        "sampler":   ki["sampler_name"],
        "scheduler": ki["scheduler"],
    }


# ------------------------------------------------------------ building the graph
class Graph(object):
    """Just enough of ComfyUI's saved-workflow format to lay out a graph."""

    def __init__(self):
        self.nodes, self.links, self.groups = [], [], []
        self._nid = self._lid = 0

    def add(self, kind, pos, size, widgets=None, ins=(), outs=(), title=None, **extra):
        self._nid += 1
        n = {
            "id": self._nid, "type": kind, "pos": list(pos), "size": list(size),
            "flags": {}, "order": self._nid, "mode": 0,
            "inputs": [{"name": a, "localized_name": a, "type": t, "link": None} for a, t in ins],
            "outputs": [{"name": a, "localized_name": a, "type": t, "links": [], "slot_index": i}
                        for i, (a, t) in enumerate(outs)],
            "properties": {"Node name for S&R": kind} if kind != "MarkdownNote" else {},
            "widgets_values": list(widgets or []),
        }
        if title:
            n["title"] = title
        n.update(extra)
        self.nodes.append(n)
        return n

    def wire(self, src, out_slot, dst, in_name):
        slot = next(i for i, x in enumerate(dst["inputs"]) if x["name"] == in_name)
        kind = src["outputs"][out_slot]["type"]
        want = dst["inputs"][slot]["type"]
        assert kind == want, "%s.%d is %s, %s.%s wants %s" % (
            src["type"], out_slot, kind, dst["type"], in_name, want)
        assert dst["inputs"][slot]["link"] is None, "%s.%s wired twice" % (dst["type"], in_name)
        self._lid += 1
        self.links.append([self._lid, src["id"], out_slot, dst["id"], slot, kind])
        src["outputs"][out_slot]["links"].append(self._lid)
        dst["inputs"][slot]["link"] = self._lid

    def group(self, title, x, y, w, h, color):
        self.groups.append({"id": len(self.groups) + 1, "title": title,
                            "bounding": [x, y, w, h], "color": color,
                            "font_size": 24, "flags": {}})

    def check(self):
        for n in self.nodes:
            for i in n["inputs"]:
                if i["link"] is None and i["name"] != "mask":
                    raise AssertionError("%s #%d: %s is not connected" % (n["type"], n["id"], i["name"]))

    def dump(self):
        self.check()
        return {
            "id": str(uuid.uuid4()), "revision": 0,
            "last_node_id": self._nid, "last_link_id": self._lid,
            "nodes": self.nodes, "links": self.links, "groups": self.groups,
            "config": {}, "version": 0.4,
            "extra": {"ds": {"scale": 0.5, "offset": [120, 520]}},
        }


def build(render_path, char, prompt_override=None):
    r = recipe(render_path)
    base = prompt_override or r["prompt"]
    if not NEUTRAL.search(base):
        print("!! no 'neutral ... expression' phrase in the prompt — the expression "
              "words will be added at the front instead")

    render_name = os.path.basename(render_path)
    mask_name = char + "_face.png"
    g = Graph()

    note = g.add("MarkdownNote", (0, -470), (640, 400), title="Start here",
                 color="#222", bgcolor="#000", widgets=[
        "## %s: five expressions, one Run\n\n"
        "1. **Top Load Image box:** click it and upload `%s`.\n"
        "2. **Bottom Load Image box:** upload `%s` from the `masks` folder.\n"
        "3. Press **Run**. Each row on the right paints one expression.\n\n"
        "Each row has two settings you can change:\n\n"
        "- **The text box** holds your original prompt, word for word. Only the "
        "expression words differ.\n"
        "- **denoise** (bottom of the KSampler) sets how much the face can change. "
        "If it barely moved, go up by 0.05. If it looks like a different person, "
        "go down. Stay under 0.6.\n\n"
        "Nothing outside the face mask can change: hair, body and green all come "
        "back identical." % (char.capitalize(), render_name, mask_name)])

    # ---- shared column: model, pictures, mask
    unet = g.add("UNETLoader", (0, 0), (320, 82), r["unet"], outs=[("MODEL", "MODEL")])
    clip = g.add("CLIPLoader", (0, 110), (320, 106), r["clip"], outs=[("CLIP", "CLIP")])
    vae = g.add("VAELoader", (0, 245), (320, 58), [r["vae"]], outs=[("VAE", "VAE")])
    img = g.add("LoadImage", (0, 340), (320, 380), [render_name, "image"],
                outs=[("IMAGE", "IMAGE"), ("MASK", "MASK")], title="Load Image: the render")
    msk = g.add("LoadImage", (0, 750), (320, 380), [mask_name, "image"],
                outs=[("IMAGE", "IMAGE"), ("MASK", "MASK")], title="Load Image: the face mask")
    to_mask = g.add("ImageToMask", (360, 750), (260, 58), ["red"],
                    ins=[("image", "IMAGE")], outs=[("MASK", "MASK")])
    enc = g.add("VAEEncode", (360, 340), (210, 46),
                ins=[("pixels", "IMAGE"), ("vae", "VAE")], outs=[("LATENT", "LATENT")])
    noise = g.add("SetLatentNoiseMask", (360, 440), (240, 46),
                  ins=[("samples", "LATENT"), ("mask", "MASK")], outs=[("LATENT", "LATENT")])
    g.wire(msk, 0, to_mask, "image")
    g.wire(img, 0, enc, "pixels")
    g.wire(vae, 0, enc, "vae")
    g.wire(enc, 0, noise, "samples")
    g.wire(to_mask, 0, noise, "mask")
    g.group("Shared: model, the render, its face mask", -20, -40, 660, 1190, "#3f3f5a")

    # ---- one row per expression
    row_h, x0 = 400, 700
    colours = ["#3f5a4a", "#3f4f5a", "#4a3f5a", "#5a3f3f", "#5a513f"]
    for i, (expr, words, denoise) in enumerate(EXPRESSIONS):
        y = i * row_h
        text = NEUTRAL.sub(words, base, count=1) if NEUTRAL.search(base) else words + ", " + base
        pos = g.add("CLIPTextEncode", (x0, y), (440, 250), [text],
                    ins=[("clip", "CLIP")], outs=[("CONDITIONING", "CONDITIONING")],
                    title="Prompt: %s" % expr)
        neg = g.add("ConditioningZeroOut", (x0, y + 280), (240, 26),
                    ins=[("conditioning", "CONDITIONING")], outs=[("CONDITIONING", "CONDITIONING")])
        ks = g.add("KSampler", (x0 + 470, y), (300, 262),
                   [100000 + i * 7919, "randomize", r["steps"], r["cfg"],
                    r["sampler"], r["scheduler"], denoise],
                   ins=[("model", "MODEL"), ("positive", "CONDITIONING"),
                        ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
                   outs=[("LATENT", "LATENT")])
        dec = g.add("VAEDecode", (x0 + 800, y), (200, 46),
                    ins=[("samples", "LATENT"), ("vae", "VAE")], outs=[("IMAGE", "IMAGE")])
        comp = g.add("ImageCompositeMasked", (x0 + 800, y + 80), (290, 140), [0, 0, False],
                     ins=[("destination", "IMAGE"), ("source", "IMAGE"), ("mask", "MASK")],
                     outs=[("IMAGE", "IMAGE")], title="Paste face onto original")
        save = g.add("SaveImage", (x0 + 1120, y), (280, 340), ["%s_%s" % (char, expr)],
                     ins=[("images", "IMAGE")], outs=[])
        g.wire(clip, 0, pos, "clip")
        g.wire(pos, 0, neg, "conditioning")
        g.wire(unet, 0, ks, "model")
        g.wire(pos, 0, ks, "positive")
        g.wire(neg, 0, ks, "negative")
        g.wire(noise, 0, ks, "latent_image")
        g.wire(ks, 0, dec, "samples")
        g.wire(vae, 0, dec, "vae")
        g.wire(img, 0, comp, "destination")
        g.wire(dec, 0, comp, "source")
        g.wire(to_mask, 0, comp, "mask")
        g.wire(comp, 0, save, "images")
        g.group("%s  (denoise %.2f)" % (expr.upper(), denoise),
                x0 - 20, y - 40, 1440, row_h - 20, colours[i % len(colours)])

    return g.dump(), r


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); raise SystemExit(1)
    render = os.path.expanduser(args[0])
    char = args[1]
    override = None
    if "--prompt-file" in sys.argv:
        override = open(os.path.expanduser(sys.argv[sys.argv.index("--prompt-file") + 1])).read()

    wf, r = build(render, char, override)
    out = os.path.join(os.path.dirname(render), "%s_expressions.json" % char)
    with open(out, "w") as f:
        json.dump(wf, f, indent=1)

    print("model     %s" % r["unet"][0])
    print("encoder   %s (%s)" % (r["clip"][0], r["clip"][1]))
    print("vae       %s" % r["vae"])
    print("sampler   %s / %s, %d steps, cfg %s" % (r["sampler"], r["scheduler"], r["steps"], r["cfg"]))
    print("rows      %s" % ", ".join("%s %.2f" % (e, d) for e, _, d in EXPRESSIONS))
    print("\nworkflow -> %s" % out)
    print("drag it onto the Comfy Cloud canvas")
