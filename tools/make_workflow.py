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

How each row works: the face is cut out of the render in a square around the
mask, scaled up to 1024, and repainted there — only inside the face mask (see
tools/facemask.py). The result is shrunk back and composited over the untouched
original, so the hair, body, uniform and green backdrop come back byte-identical
in all five.

The cut-out-and-enlarge step is not optional polish. The first run repainted
the face at its real size, where Yuji's mouth is about 25px wide — three cells
of the model's working grid. Every expression came back nearly neutral, because
there was no room to draw an open mouth or bared teeth. At four times the size
there is.
"""
import sys, os, re, json, struct, zlib, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# (expression, words that replace the neutral phrase, denoise)
# Anime faces are drawn big: the first run's polite wording ("smiling warmly",
# "mouth open slightly") produced five near-identical faces. Say what the face
# is doing in the terms the art style uses. Mouth-open expressions need more
# room to move; past ~0.7 it stops being the same person.
EXPRESSIONS = [
    ("happy",     "big cheerful open-mouthed grin, eyes squeezed shut into happy upturned arcs, "
                  "raised eyebrows",                                                            0.60),
    ("serious",   "serious determined look, mouth a firm straight line, eyebrows lowered and "
                  "drawn together, steady narrowed eyes",                                       0.55),
    ("sad",       "sad expression, eyes downcast and glistening, eyebrows raised and pinched "
                  "together at the inner ends, mouth turned down at the corners",               0.58),
    ("angry",     "fierce angry shout, mouth open showing clenched teeth, eyebrows sharply "
                  "furrowed into a V, glaring eyes",                                            0.62),
    ("surprised", "shocked expression, eyes wide open with small pupils, eyebrows raised high, "
                  "mouth open in a round O",                                                    0.62),
]

WORK = 1024       # side of the square the face is repainted at

# Some characters don't emote at the shared table's volume. Megumi's canon
# happy is barely a smile and his anger is cold rather than shouted, so a big
# open-mouthed grin would read as someone else. Only the rows listed here
# change; the rest fall through to EXPRESSIONS.
CHARACTER_EXPRESSIONS = {
    "megumi": {
        "happy":     ("faint reluctant half-smile, one corner of the mouth lifted slightly, "
                      "eyes softened a little",                                                 0.50),
        "serious":   ("intense focused stare, eyebrows drawn hard together, jaw set",          0.55),
        "sad":       ("quiet sad expression, eyes lowered, eyebrows tilted up at the inner "
                      "ends, mouth turned down slightly",                                       0.58),
        "angry":     ("cold angry glare, eyebrows pulled down hard into a V, jaw clenched, "
                      "lips pressed tight",                                                     0.58),
        "surprised": ("startled expression, eyes widened, eyebrows raised, lips parted "
                      "slightly",                                                               0.58),
    },
}


def expressions_for(char):
    own = CHARACTER_EXPRESSIONS.get(char, {})
    return [(e,) + own[e] if e in own else (e, w, d) for e, w, d in EXPRESSIONS]

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


def crop_box(mask_path):
    """Square around the white part of the mask, with room for the model to see
    hair and collar around the face. Returns (x, y, side) in render pixels."""
    from pngread import load
    m = load(mask_path)
    xs, ys = [], []
    for y in range(m.h):
        row = y * m.w * m.ch
        for x in range(m.w):
            if m.buf[row + x * m.ch] > 0:
                xs.append(x); ys.append(y)
    if not xs:
        raise SystemExit("%s is all black — rebuild it with tools/facemask.py" % mask_path)
    cx, cy = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    need = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.3
    side = 64
    while side < need:
        side += 64
    side = min(side, m.w, m.h)
    x = max(0, min(m.w - side, cx - side // 2))
    y = max(0, min(m.h - side, cy - side // 2))
    return x, y, side


def closeup(base, words):
    """The render's prompt, re-framed for a picture that is only the face.

    The framing paragraph describes a full-body sprite; handed a square that is
    all face, the model fights the description instead of drawing the
    expression. Keep every other paragraph word for word.
    """
    paras = re.split(r"\n\s*\n", base.strip())
    subject = re.search(r"single ([a-z' -]+?)(?: standing|,)", base, re.I)
    subject = subject.group(1) if subject else "anime character"
    frame = "close-up of the face of a single %s, facing the viewer, %s" % (subject, words)
    for i, p in enumerate(paras):
        if re.search(r"full[- ]body|sprite", p, re.I):
            paras[i] = frame
            return "\n\n".join(paras)
    return frame + "\n\n" + base


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


def build(render_path, char, prompt_override=None, mask_path=None):
    r = recipe(render_path)
    base = prompt_override or r["prompt"]
    mask_path = mask_path or os.path.join(os.path.dirname(render_path), "masks", char + "_face.png")
    if not os.path.exists(mask_path):
        raise SystemExit("no mask at %s — run tools/facemask.py first" % mask_path)
    cx, cy, side = crop_box(mask_path)

    render_name = os.path.basename(render_path)
    mask_name = os.path.basename(mask_path)
    g = Graph()

    g.add("MarkdownNote", (0, -470), (640, 400), title="Start here",
          color="#222", bgcolor="#000", widgets=[
        "## %s: five expressions, one Run\n\n"
        "1. **Top Load Image box:** click the folder icon and upload `%s`.\n"
        "2. **Bottom Load Image box:** upload `%s` from the `masks` folder. "
        "It should be black with a small white oval.\n"
        "3. Press **Run**. Each row on the right paints one expression.\n\n"
        "Each row has two settings you can change:\n\n"
        "- **The text box** holds the prompt. Only the expression words differ.\n"
        "- **denoise** (bottom of the KSampler) sets how much the face can change. "
        "If it barely moved, go up by 0.05. If it stops looking like %s, go "
        "down. Stay under 0.7.\n\n"
        "The face is cut out, repainted 4x bigger, then shrunk back in. Nothing "
        "outside the white oval can change."
        % (char.capitalize(), render_name, mask_name, char.capitalize())])

    # ---- shared column: model, pictures, the cut-out face
    unet = g.add("UNETLoader", (0, 0), (320, 82), r["unet"], outs=[("MODEL", "MODEL")])
    clip = g.add("CLIPLoader", (0, 110), (320, 106), r["clip"], outs=[("CLIP", "CLIP")])
    vae = g.add("VAELoader", (0, 245), (320, 58), [r["vae"]], outs=[("VAE", "VAE")])
    img = g.add("LoadImage", (0, 340), (320, 380), [render_name, "image"],
                outs=[("IMAGE", "IMAGE"), ("MASK", "MASK")], title="Load Image: the render")
    msk = g.add("LoadImage", (0, 750), (320, 380), [mask_name, "image"],
                outs=[("IMAGE", "IMAGE"), ("MASK", "MASK")], title="Load Image: the face mask")

    cut = g.add("ImageCrop", (360, 340), (260, 130), [side, side, cx, cy],
                ins=[("image", "IMAGE")], outs=[("IMAGE", "IMAGE")], title="Cut out the face")
    big = g.add("ImageScale", (360, 500), (260, 130), ["lanczos", WORK, WORK, "disabled"],
                ins=[("image", "IMAGE")], outs=[("IMAGE", "IMAGE")], title="Enlarge to %d" % WORK)
    enc = g.add("VAEEncode", (360, 660), (210, 46),
                ins=[("pixels", "IMAGE"), ("vae", "VAE")], outs=[("LATENT", "LATENT")])
    to_mask = g.add("ImageToMask", (360, 750), (260, 58), ["red"],
                    ins=[("image", "IMAGE")], outs=[("MASK", "MASK")])
    cut_mask = g.add("CropMask", (360, 840), (260, 130), [cx, cy, side, side],
                     ins=[("mask", "MASK")], outs=[("MASK", "MASK")], title="Cut out the mask")
    # SetLatentNoiseMask resizes the mask to the latent itself, so the cut-out
    # mask can go straight in; the composite at the end wants it at cut-out size.
    noise = g.add("SetLatentNoiseMask", (360, 1000), (240, 46),
                  ins=[("samples", "LATENT"), ("mask", "MASK")], outs=[("LATENT", "LATENT")])
    g.wire(img, 0, cut, "image")
    g.wire(cut, 0, big, "image")
    g.wire(big, 0, enc, "pixels")
    g.wire(vae, 0, enc, "vae")
    g.wire(msk, 0, to_mask, "image")
    g.wire(to_mask, 0, cut_mask, "mask")
    g.wire(enc, 0, noise, "samples")
    g.wire(cut_mask, 0, noise, "mask")
    g.group("Shared: model, the render, its face mask", -20, -40, 660, 1190, "#3f3f5a")

    # ---- one row per expression
    row_h, x0 = 420, 700
    colours = ["#3f5a4a", "#3f4f5a", "#4a3f5a", "#5a3f3f", "#5a513f"]
    for i, (expr, words, denoise) in enumerate(expressions_for(char)):
        y = i * row_h
        pos = g.add("CLIPTextEncode", (x0, y), (440, 250), [closeup(base, words)],
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
        small = g.add("ImageScale", (x0 + 800, y + 70), (260, 130), ["lanczos", side, side, "disabled"],
                      ins=[("image", "IMAGE")], outs=[("IMAGE", "IMAGE")], title="Shrink back to %d" % side)
        comp = g.add("ImageCompositeMasked", (x0 + 800, y + 220), (290, 140), [cx, cy, False],
                     ins=[("destination", "IMAGE"), ("source", "IMAGE"), ("mask", "MASK")],
                     outs=[("IMAGE", "IMAGE")], title="Paste face onto original")
        save = g.add("SaveImage", (x0 + 1120, y), (280, 360), ["%s_%s" % (char, expr)],
                     ins=[("images", "IMAGE")], outs=[])
        g.wire(clip, 0, pos, "clip")
        g.wire(pos, 0, neg, "conditioning")
        g.wire(unet, 0, ks, "model")
        g.wire(pos, 0, ks, "positive")
        g.wire(neg, 0, ks, "negative")
        g.wire(noise, 0, ks, "latent_image")
        g.wire(ks, 0, dec, "samples")
        g.wire(vae, 0, dec, "vae")
        g.wire(dec, 0, small, "image")
        g.wire(img, 0, comp, "destination")
        g.wire(small, 0, comp, "source")
        g.wire(cut_mask, 0, comp, "mask")
        g.wire(comp, 0, save, "images")
        g.group("%s  (denoise %.2f)" % (expr.upper(), denoise),
                x0 - 20, y - 40, 1440, row_h - 20, colours[i % len(colours)])

    return g.dump(), r, (cx, cy, side)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__); raise SystemExit(1)
    render = os.path.expanduser(args[0])
    char = args[1]
    override = None
    if "--prompt-file" in sys.argv:
        override = open(os.path.expanduser(sys.argv[sys.argv.index("--prompt-file") + 1])).read()

    wf, r, (cx, cy, side) = build(render, char, override)
    out = os.path.join(os.path.dirname(render), "%s_expressions.json" % char)
    with open(out, "w") as f:
        json.dump(wf, f, indent=1)

    print("model     %s" % r["unet"][0])
    print("encoder   %s (%s)" % (r["clip"][0], r["clip"][1]))
    print("vae       %s" % r["vae"])
    print("sampler   %s / %s, %d steps, cfg %s" % (r["sampler"], r["scheduler"], r["steps"], r["cfg"]))
    print("face crop %dx%d at (%d, %d), repainted at %d" % (side, side, cx, cy, WORK))
    print("rows      %s" % ", ".join("%s %.2f" % (e, d) for e, _, d in expressions_for(char)))
    print("\nworkflow -> %s" % out)
    print("drag it onto the Comfy Cloud canvas")
