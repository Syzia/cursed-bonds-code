"""
Build a ComfyUI workflow that paints a character's five other expressions.

    python3 tools/make_workflow.py "~/Desktop/JJK Game images/Krea2_turbo_00001_.png" yuji
    python3 tools/make_workflow.py --head "~/Desktop/JJK Game images/megumi_base_00001_.png" megumi

`--only happy,angry` builds just those rows; `--ladder 0.08` makes two rows per
expression, the second allowed to change that much more (saved as
`<character>_<expression>_a` and `_b`).

`--head` writes `<character>_head.json` instead: four attempts at redrawing the
whole head -- hair and face -- through the mask from `facemask.py --head`,
each allowed to change a little more than the last, on a body that stays put.

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
    # Quieter in character, but each row still has to read as different from
    # the others at a glance. The first pass (denoise 0.50-0.58, soft wording)
    # came back as four versions of his neutral face.
    "megumi": {
        "happy":     ("small genuine smile, lips curved up at both corners, eyes softened "
                      "and slightly narrowed",                                                  0.58),
        "serious":   ("intense focused stare, eyebrows drawn down hard and together, eyes "
                      "narrowed, jaw set",                                                      0.66),
        "sad":       ("sad pained expression, eyebrows tilted steeply up at the inner ends, "
                      "eyes lowered and glistening, mouth turned down at the corners",          0.68),
        "angry":     ("furious scowl, eyebrows slammed down into a sharp V, eyes narrowed "
                      "into a hard glare, teeth clenched and slightly bared",                   0.70),
        "surprised": ("surprised expression, eyes opened wide showing the whole iris, "
                      "eyebrows raised high, mouth open",                                       0.70),
    },
}

# A one-line reminder of who the character is, used INSTEAD of their full
# description on expression rows. Megumi's full prompt is ~300 words, mostly
# hair; the expression was one clause in it and the model ignored it -- his
# faces changed as much in raw pixels as Yuji's (mean ~21) and all came back
# bored. Identity is already in the picture being repainted, so the prompt's
# only job on these rows is the expression. Characters without an entry keep
# their full description, which is fine when it is short (Yuji's is ~117).
FACE_BRIEF = {
    "megumi": "spiky jet-black hair with sharp pointed bangs over the forehead, dark blue-grey "
              "eyes, pale skin, tall dark navy funnel collar",
}

# Words in a character's description that pin their NEUTRAL face -- dropped
# from expression rows only. The base picture already carries the eye shape;
# saying "heavy drooping eyelids" again just drags every expression back to it.
NEUTRAL_TRAITS = {
    "megumi": ["and heavy drooping upper eyelids that\ncover the top of the irises"],
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


def closeup(base, words, what="face"):
    """The render's prompt, re-framed for a picture that is only the face.

    The framing paragraph describes a full-body sprite; handed a square that is
    all face, the model fights the description instead of drawing the
    expression. Keep every other paragraph word for word.
    """
    paras = re.split(r"\n\s*\n", base.strip())
    subject = re.search(r"single ([a-z' -]+?)(?: standing|,)", base, re.I)
    subject = subject.group(1) if subject else "anime character"
    frame = "close-up of the %s of a single %s, facing the viewer, %s" % (what, subject, words)
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


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A character's neutral face in words, for redrawing the whole head. Only
# needed where the shared default would flatten who they are.
NEUTRAL_FACE = {
    "megumi": "calm neutral bored expression, heavy half-lidded drowsy eyes looking straight "
              "at the viewer, mouth closed in a small flat line",
}
HEAD_DENOISE = [0.80, 0.85, 0.85, 0.90]     # one candidate per value


def base_prompt(char, r, override=None):
    """The canonical prompt file beats whatever is embedded in the render.

    Once a head has been redrawn, the render's own metadata holds the close-up
    prompt that drew it, not the full-body description the character is built
    from -- and the file is where corrections get made.
    """
    if override:
        return override
    f = os.path.join(ROOT, "tools", "chars", "prompts", char + ".txt")
    return open(f).read().strip() if os.path.exists(f) else r["prompt"]


def build(render_path, char, prompt_override=None, mask_path=None, head=False,
          only=None, ladder=0.0):
    r = recipe(render_path)
    base = base_prompt(char, r, prompt_override)
    kind = "head" if head else "face"
    mask_path = mask_path or os.path.join(os.path.dirname(render_path), "masks", "%s_%s.png" % (char, kind))
    if not os.path.exists(mask_path):
        raise SystemExit("no mask at %s — run tools/facemask.py%s first"
                         % (mask_path, " --head" if head else ""))
    cx, cy, side = crop_box(mask_path)

    render_name = os.path.basename(render_path)
    mask_name = os.path.basename(mask_path)
    g = Graph()

    if head:
        g.add("MarkdownNote", (0, -470), (640, 400), title="Start here",
              color="#222", bgcolor="#000", widgets=[
            "## %s: new hair and face, same body\n\n"
            "1. **Top Load Image box:** upload `%s`.\n"
            "2. **Bottom Load Image box:** upload `%s` from the `masks` folder. "
            "It should be black with a white dome over the head.\n"
            "3. Press **Run**. The four rows are four attempts, each allowed to "
            "change a little more than the last (A least, D most).\n\n"
            "Save the one whose hair and face look most like him. Everything "
            "below the chin comes back exactly as it was."
            % (char.capitalize(), render_name, mask_name)])
    else:
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
    if head:
        words = NEUTRAL_FACE.get(char, "calm neutral expression, mouth closed")
        rows = [("head_%s" % "abcd"[i], words, d) for i, d in enumerate(HEAD_DENOISE)]
        what = "head, hair and face"
    else:
        rows, what = expressions_for(char), "face"
        if only:
            rows = [r_ for r_ in rows if r_[0] in only]
        if ladder:
            # Two tries per expression, the second allowed to change more.
            # Saves a round trip when the right strength is a guess.
            rows = [(e + tag, w, d + k * ladder) for e, w, d in rows
                    for k, tag in ((0, "_a"), (1, "_b"))]
        for t in NEUTRAL_TRAITS.get(char, []):
            if t not in base:
                raise SystemExit("NEUTRAL_TRAITS[%r] no longer matches the prompt: %r" % (char, t))
            base = base.replace(t, "")
    for i, (expr, words, denoise) in enumerate(rows):
        y = i * row_h
        if not head and char in FACE_BRIEF:
            m = re.search(r"single ([a-z' -]+?)(?: standing|,)", base, re.I)
            style = re.split(r"\n\s*\n", base.strip())[-1]
            text = ("close-up of the face of a single %s, facing the viewer, %s\n\n%s\n\n%s\n\n%s"
                    % (m.group(1) if m else "anime character", words, FACE_BRIEF[char], style, words))
        else:
            text = closeup(base, words, what)
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
    VALUED = ("--prompt-file", "--only", "--ladder")
    opts, args, argv = {}, [], sys.argv[1:]
    while argv:
        a = argv.pop(0)
        if a in VALUED:
            opts[a] = argv.pop(0)
        elif a.startswith("--"):
            opts[a] = True
        else:
            args.append(a)
    if len(args) < 2:
        print(__doc__); raise SystemExit(1)
    render, char = os.path.expanduser(args[0]), args[1]
    override = open(os.path.expanduser(opts["--prompt-file"])).read() if "--prompt-file" in opts else None
    head = "--head" in opts
    only = opts["--only"].split(",") if "--only" in opts else None
    ladder = float(opts.get("--ladder", 0))
    wf, r, (cx, cy, side) = build(render, char, override, head=head, only=only, ladder=ladder)
    out = os.path.join(os.path.dirname(render), "%s_%s.json" % (char, "head" if head else "expressions"))
    with open(out, "w") as f:
        json.dump(wf, f, indent=1)

    print("model     %s" % r["unet"][0])
    print("encoder   %s (%s)" % (r["clip"][0], r["clip"][1]))
    print("vae       %s" % r["vae"])
    print("sampler   %s / %s, %d steps, cfg %s" % (r["sampler"], r["scheduler"], r["steps"], r["cfg"]))
    print("face crop %dx%d at (%d, %d), repainted at %d" % (side, side, cx, cy, WORK))
    if head:
        print("rows      four head candidates at denoise %s" % ", ".join("%.2f" % d for d in HEAD_DENOISE))
    else:
        print("rows      %s" % ", ".join("%s %.2f" % (n["title"].split(": ")[1], ks["widgets_values"][-1])
              for n, ks in zip([n for n in wf["nodes"] if n["type"] == "CLIPTextEncode"],
                               [n for n in wf["nodes"] if n["type"] == "KSampler"])))
    print("\nworkflow -> %s" % out)
    print("drag it onto the Comfy Cloud canvas")
