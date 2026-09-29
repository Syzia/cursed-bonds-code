"""
Build a ComfyUI workflow that asks edit models for a character's expressions.

    python3 tools/make_edit_workflow.py megumi
    python3 tools/make_edit_workflow.py megumi --only angry,surprised --editors seedream

Loads `<character>_edit_in.png` (the head close-up from
`composite_face.py --prepare`) and, for each expression, sends it to each
editor with an instruction to change the face and nothing else. Every result
is saved as `<character>_<expression>_<editor>`, so a single Run compares the
editors side by side on the character's actual face.

Both editors are paid partner nodes -- they run on the provider's servers, not
this Mac -- so the file's note states what a Run costs before anyone presses it.

The node definitions are copied from the ComfyUI install's own templates
(tools/comfy_nodes/edit_nodes.json), so the widgets are in the order this
frontend expects rather than an order guessed from documentation.
"""
import sys, os, json, copy, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")

EDITORS = {
    # key: (node type, save node type, dollars per image at 1K, label)
    # Refuses recognisable characters from existing series -- see the default below.
    "seedream":   ("ByteDanceSeedreamNodeV3", "SaveImageAdvanced", 0.045, "Seedream 5.0 Pro"),
    "nanobanana": ("GeminiImage2Node",        "SaveImage",         0.16,  "Nano Banana Pro"),
}

# Describe only what changes. Never restate a character's resting look ("bored,
# heavy-lidded") -- editors copy it straight back. Never name the character or
# the series: closed APIs refuse named copyrighted characters.
EXPRESSIONS = {
    "happy":     "Change {his} facial expression to a genuine, warm smile: mouth curved clearly upward "
                 "with the corners lifted, cheeks slightly raised, lower eyelids pushed up so the eyes "
                 "soften, eyebrows relaxed and slightly raised.",
    "serious":   "Change {his} facial expression to sharp, focused seriousness: eyes fully open and alert "
                 "with a steady, direct stare, eyebrows lowered and drawn together into a straight firm "
                 "line, mouth pressed into a tight flat line, jaw set.",
    "sad":       "Change {his} facial expression to clear sadness: inner ends of the eyebrows raised and "
                 "pulled together, upper eyelids lowered with the gaze cast downward, eyes slightly "
                 "glossy, mouth corners turned down, lips pressed together.",
    "angry":     "Change {his} facial expression to intense anger: eyebrows pulled down hard into a sharp "
                 "V with a deep crease between them, eyes narrowed into a hard glare, lips pulled back "
                 "showing clenched teeth.",
    "surprised": "Change {his} facial expression to strong surprise: eyes opened wide so the whole round "
                 "iris shows with white visible around it, small pupils, eyebrows raised high and arched, "
                 "mouth dropped open in a small oval.",
}
KEEP = ("Change only the facial expression. Keep everything else exactly the same: same character, "
        "same framing, same head position and size, same hair, same clothes, same flat green "
        "background, and the same flat anime cel shading and line art.")

HER = {"nobara", "maki", "shoko", "utahime", "sana"}

# Gojo's eyes are under a blindfold, so his expressions live in his mouth and
# jaw, as they do in the anime. Asked for eyes or brows, an editor draws eyes on
# the cloth or takes it off.
CHAR_EXPRESSIONS = {
    "gojo": {
        "happy":     "Change his facial expression to a big delighted grin: mouth wide open in a broad "
                     "smile showing his upper teeth, cheeks lifted.",
        "serious":   "Change his facial expression to cold, flat seriousness: the grin gone, mouth "
                     "closed in a straight firm line, jaw set.",
        "sad":       "Change his facial expression to quiet sadness: the grin gone, mouth closed with "
                     "the corners turned down, lips pressed together.",
        "angry":     "Change his facial expression to cold anger: lips drawn back tight in a snarl "
                     "showing clenched teeth, jaw clenched.",
        "surprised": "Change his facial expression to open surprise: mouth dropped open in a round "
                     "'o', jaw slack.",
    },
    # Shoko is deadpan: her happy is a wry half-smile and her sad is exhaustion
    # (tools/chars/CANON.md), and her anger is cold rather than shouting.
    "shoko": {
        "happy":     "Change her facial expression to a small, wry, knowing half-smile: one corner of her "
                     "mouth lifted, lips closed, her heavy-lidded eyes staying sleepy and relaxed.",
        "serious":   "Change her facial expression to cool, clinical focus: eyes a little more open with a "
                     "steady, level stare, eyebrows level and slightly lowered, mouth pressed into a flat line.",
        "sad":       "Change her facial expression to quiet, exhausted sadness: eyelids drooping almost "
                     "closed with the gaze cast down, the inner ends of the eyebrows raised slightly, mouth "
                     "flat with the corners turned slightly down.",
        "angry":     "Change her facial expression to cold, contained anger: eyebrows pulled down into a hard "
                     "frown, eyes narrowed into a flat, cold glare, mouth pressed into a tight line, jaw "
                     "clenched.",
        "surprised": "Change her facial expression to surprise: eyes opened wide so the irises show fully, "
                     "eyebrows raised high, lips parted in a small 'o'.",
    },
    # Yaga's eyes are behind narrow red-lensed sunglasses: his expressions are
    # his brows above the frames, his mouth and his beard. Happy is rare and
    # small ("the beard moving", tools/chars/CANON.md).
    "yaga": {
        "happy":     "Change his facial expression to a rare, small smile: the corners of his mouth lift "
                     "slightly under the moustache so the beard moves, and his eyebrows relax above the "
                     "sunglasses.",
        "serious":   "Change his facial expression to stern seriousness: eyebrows lowered and drawn together "
                     "above the sunglasses, mouth pressed into a hard flat line, jaw set.",
        "sad":       "Change his facial expression to quiet sadness: the inner ends of his eyebrows raised "
                     "above the sunglasses, mouth closed with the corners turned down, lips pressed together.",
        "angry":     "Change his facial expression to fierce anger: eyebrows pulled down hard into a deep frown "
                     "above the sunglasses, deep creases across the forehead, lips drawn back showing clenched "
                     "teeth, jaw clenched.",
        "surprised": "Change his facial expression to surprise: eyebrows raised high above the sunglasses with "
                     "deep lines across the forehead, mouth dropped open.",
    },
    # Maki rarely smiles: her happy is a smirk (tools/chars/CANON.md). Her
    # anger is fierce, her sadness held in.
    "maki": {
        "happy":     "Change her facial expression to a confident, cocky smirk: one corner of her mouth "
                     "lifted, lips closed, eyes relaxed and a little narrowed.",
        "serious":   "Change her facial expression to a hard, focused stare: eyebrows lowered and drawn "
                     "together, eyes steady and direct, mouth pressed into a flat line.",
        "sad":       "Change her facial expression to quiet, held-in sadness: the inner ends of her eyebrows "
                     "raised slightly, gaze lowered, mouth closed with the corners turned slightly down.",
        "angry":     "Change her facial expression to fierce anger: eyebrows pulled down hard into a sharp V, "
                     "eyes narrowed into a glare, lips drawn back showing clenched teeth.",
        "surprised": "Change her facial expression to surprise: eyes opened wide, eyebrows raised high, "
                     "lips parted.",
    },
    # Panda has no eyebrows: the short fur lines above his eye patches do their
    # job. Happy is a broad smile; angry shows small fangs (CANON.md).
    "panda": {
        "happy":     "Change his facial expression to a big, broad, happy smile with his mouth open and his "
                     "cheeks lifted, his small eyes squeezed into happy curved lines inside the black eye "
                     "patches.",
        "serious":   "Change his facial expression to a serious, focused look: the short fur lines above his "
                     "eye patches pulled down and together into a frown, his small eyes steady and alert, "
                     "mouth closed in a firm flat line.",
        "sad":       "Change his facial expression to a sad look: the short fur lines above his eye patches "
                     "angled up in the middle, his small eyes glossy and looking down, mouth closed and turned "
                     "down at the corners.",
        "angry":     "Change his facial expression to anger: the short fur lines above his eye patches pulled "
                     "down hard into a scowl, his small eyes narrowed into a glare, mouth open in a snarl "
                     "showing small sharp fangs.",
        "surprised": "Change his facial expression to surprise: his small eyes opened wide and round, the "
                     "short fur lines above his eye patches raised high, mouth dropped open.",
    },
    # Toge's collar sits under his chin (the user's choice, so his seal marks
    # show), so his mouth can move; the marks move with its corners.
    "toge": {
        "happy":     "Change his facial expression to a small, warm smile: the corners of his mouth lifted, "
                     "his eyes softened into gentle upturned arcs, eyebrows relaxed.",
        "serious":   "Change his facial expression to a serious, focused look: eyebrows lowered and drawn "
                     "together, eyes steady and direct, mouth closed in a flat line.",
        "sad":       "Change his facial expression to sadness: the inner ends of his eyebrows raised and pulled "
                     "together, eyes glossy with the gaze lowered, mouth closed and turned down at the corners.",
        "angry":     "Change his facial expression to anger: eyebrows pulled down hard into a sharp V, eyes "
                     "narrowed into a glare, mouth open showing clenched teeth.",
        "surprised": "Change his facial expression to surprise: eyes opened wide, eyebrows raised high, mouth "
                     "dropped open.",
    },
    # Utahime is prim and quick to irritation (mostly at Gojo), but warm with
    # her students, so her happy is a real smile and her anger is a fuming glare.
    "utahime": {
        "happy":     "Change her facial expression to a warm, gentle smile: the corners of her mouth lifted, "
                     "lips closed, eyes softened, eyebrows relaxed.",
        "serious":   "Change her facial expression to stern, composed seriousness: eyebrows level and drawn "
                     "slightly together, eyes steady and direct, mouth pressed into a firm line.",
        "sad":       "Change her facial expression to quiet sadness: the inner ends of her eyebrows raised and "
                     "pulled together, gaze lowered, mouth closed with the corners turned down.",
        "angry":     "Change her facial expression to fuming irritation: eyebrows pulled down hard into a sharp "
                     "V with a crease between them, eyes narrowed into a glare, teeth clenched in a scowl.",
        "surprised": "Change her facial expression to surprise: eyes opened wide, eyebrows raised high, lips "
                     "parted.",
    },
    # Ijichi is permanently anxious: surprised and sad are his home expressions
    # (tools/chars/CANON.md), his happy is relief, and his anger is a stressed,
    # flustered grimace rather than rage.
    "ijichi": {
        "happy":     "Change his facial expression to a small, relieved smile: the corners of his mouth lifted a "
                     "little, eyebrows relaxed and slightly raised, eyes softened.",
        "serious":   "Change his facial expression to a focused, professional look: eyebrows level and drawn "
                     "slightly together, eyes steady, mouth closed in a firm line.",
        "sad":       "Change his facial expression to anxious, dejected sadness: the inner ends of his eyebrows "
                     "raised high and pulled together, gaze lowered, mouth closed with the corners turned down.",
        "angry":     "Change his facial expression to stressed, flustered frustration: eyebrows pulled down and "
                     "together into a tense frown, eyes narrowed, teeth gritted in a grimace.",
        "surprised": "Change his facial expression to startled alarm: eyes opened wide, eyebrows raised high, "
                     "mouth dropped open.",
    },
    # Sana rests on a gentle, teasing smile, so her happy is a big open grin.
    # She's opinionated: her anger is indignant, mid-argument (CANON.md).
    "sana": {
        "happy":     "Change her facial expression to a big, bright grin: mouth open in a wide smile showing her "
                     "upper teeth, cheeks lifted, lower eyelids pushed up so her eyes crinkle happily, eyebrows "
                     "raised.",
        "serious":   "Change her facial expression to earnest seriousness: the smile gone, eyes fully open with a "
                     "steady, direct look, eyebrows level and drawn slightly together, mouth closed in a flat line.",
        "sad":       "Change her facial expression to clear sadness: the smile gone, the inner ends of her eyebrows "
                     "raised and pulled together, eyes glossy with the gaze lowered, mouth closed with the corners "
                     "turned down.",
        "angry":     "Change her facial expression to indignant anger: eyebrows pulled down hard into a sharp V with "
                     "a crease between them, eyes narrowed into a glare, mouth open mid-shout showing her teeth.",
        "surprised": "Change her facial expression to strong surprise: eyes opened wide so the whole round iris "
                     "shows, eyebrows raised high and arched, mouth dropped open in a small oval.",
    },
    # Kaito is a cool, watchful lead (the user asked for a Sung Jin-Woo type):
    # his happy is a confident smile rather than a grin, his anger cold.
    "mc": {
        "happy":     "Change his facial expression to a warm, confident smile: the corners of his mouth lifted, "
                     "lips closed, his eyes softened, eyebrows relaxed.",
        "serious":   "Change his facial expression to intense focus: eyebrows lowered and drawn together, eyes "
                     "narrowed slightly with a sharp, steady stare, mouth pressed into a firm line, jaw set.",
        "sad":       "Change his facial expression to quiet, held-in sadness: the inner ends of his eyebrows raised "
                     "and pulled together, gaze lowered, mouth closed with the corners turned slightly down.",
        "angry":     "Change his facial expression to cold fury: eyebrows pulled down hard into a sharp V with a "
                     "crease between them, eyes narrowed into a piercing glare, teeth clenched, jaw tight.",
        "surprised": "Change his facial expression to surprise: eyes opened wide, eyebrows raised high, lips "
                     "parted.",
    },
}
CHAR_KEEP = {
    "mc": "Keep his side-swept fringe and the loose lock across his forehead exactly where they are, and keep "
          "his eyes the same grey-violet.",
    "sana": "Keep the loose strands of hair that fall across her face and between her eyes exactly where they "
            "are, keep her eyes the same bright green, and keep the white daisy clip in her hair.",
    "ijichi": "Keep his glasses on exactly as they are, with the same frames and lenses, and keep his hair "
              "exactly as it is.",
    "utahime": "Keep the scar across her face exactly where it is, and keep her fringe exactly as it is.",
    "toge": "Keep the seal marks beside his mouth (a small ring on each cheek joined to the corner of his "
            "mouth by a short line) at the corners of his mouth, keep his spiky hair exactly as it is, and "
            "keep the collar of his jacket under his chin.",
    "panda": "Keep his ears, the outline of his head, his black nose and his black eye patches in the "
             "same place and size.",
    "maki": "Keep her thin silver wire-framed glasses on exactly as they are, and keep her straight bangs "
            "exactly as they are.",
    "yaga": "Keep his narrow rectangular sunglasses on exactly as they are, with the same thin frames and "
            "dark red lenses, and do not draw his eyes over them.",
    "gojo": "His eyes stay completely hidden behind the wide black cloth blindfold: keep the blindfold, "
            "and everything above the nose, exactly as it is, and do not draw any eyes.",
    "shoko": "Keep the tired lines under her eyes and the small dark mole under her right eye, the eye on "
             "the left side of the picture, exactly where they are.",
}


def build(char, exprs, editors):
    src = json.load(open(os.path.join(ROOT, "tools", "comfy_nodes", "edit_nodes.json")))
    proto = src["nodes"]
    nodes, links = [], []
    ids = {"n": 0, "l": 0}

    def add(kind, pos, size=None, title=None):
        ids["n"] += 1
        n = copy.deepcopy(proto[kind])
        n["id"], n["pos"], n["order"] = ids["n"], list(pos), ids["n"]
        if size:
            n["size"] = list(size)
        for i in n.get("inputs", []):
            i["link"] = None
        for o in n.get("outputs", []):
            o["links"] = [] if o.get("links") is not None else None
        if title:
            n["title"] = title
        nodes.append(n)
        return n

    def wire(a, a_slot, b, b_input):
        ids["l"] += 1
        slot = next(i for i, x in enumerate(b["inputs"]) if x["name"] == b_input)
        kind = a["outputs"][a_slot]["type"]
        assert kind == b["inputs"][slot]["type"], (a["type"], b["type"], b_input)
        links.append([ids["l"], a["id"], a_slot, b["id"], slot, kind])
        if a["outputs"][a_slot]["links"] is None:
            a["outputs"][a_slot]["links"] = []
        a["outputs"][a_slot]["links"].append(ids["l"])
        b["inputs"][slot]["link"] = ids["l"]

    his = "her" if char in HER else "his"
    image_name = "%s_edit_in.png" % char
    cost = sum(EDITORS[e][2] for e in editors) * len(exprs)

    ids["n"] += 1
    nodes.append({
        "id": ids["n"], "type": "MarkdownNote", "pos": [-520, -40], "size": [440, 420],
        "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
        "title": "Start here", "color": "#222", "bgcolor": "#000",
        "widgets_values": [
            "## %s: expressions with edit models\n\n"
            "1. The **Load Image** box should already show `%s`. If it shows an "
            "error, click **choose file to upload** and pick it from `JJK Game images`.\n"
            "2. Press **Run**.\n\n"
            "Each row is one expression. Each coloured box in a row is a different "
            "editor, with its result saved next to it.\n\n"
            "**Cost:** %d edits, about **$%.2f** in total, charged to your Comfy "
            "account (%s).\n\n"
            "You don't need to save anything. The results land in ComfyUI's output "
            "folder, where Claude picks them up.\n\n"
            "If it stops with a rate-limit or \"high demand\" error, wait a minute and "
            "press **Run** again: finished pictures are reused, not paid for twice."
            % (char.capitalize(), image_name, len(exprs) * len(editors), cost,
               ", ".join("%s ~$%.3f each" % (EDITORS[e][3], EDITORS[e][2]) for e in editors))]})

    load = add("LoadImage", (-520, 420), (440, 500), title="Load Image: the close-up")
    load["widgets_values"] = [image_name, "image"]

    row_h = 560
    groups = []
    colours = {"happy": "#3f5a4a", "serious": "#3f4f5a", "sad": "#4a3f5a", "angry": "#5a3f3f", "surprised": "#5a513f"}
    for r, expr in enumerate(exprs):
        y = r * row_h
        prompt = (CHAR_EXPRESSIONS.get(char, {}).get(expr) or EXPRESSIONS[expr].format(his=his)) + " " + KEEP
        if char in CHAR_KEEP:
            prompt += " " + CHAR_KEEP[char]
        x = 0
        for ed in editors:
            node_t, save_t, _, label = EDITORS[ed]
            n = add(node_t, (x, y), (400, 470), title="%s: %s" % (label, expr))
            n["widgets_values"] = list(n["widgets_values"])
            n["widgets_values"][0] = prompt
            if node_t == "GeminiImage2Node":
                # A fixed seed per row, so a Run that stops on a rate limit can
                # be pressed again and reuse what finished. Aspect 1:1 and 1K,
                # as the close-up is square; IMAGE only.
                n["widgets_values"][2] = 300 + r
                n["widgets_values"][3] = "fixed"
                n["widgets_values"][4] = "1:1"
                n["widgets_values"][5] = "1K"
                n["widgets_values"][6] = "IMAGE"
                wire(load, 0, n, "images")
            else:
                n["widgets_values"][2] = "(1K) 1024x1024 (1:1)"
                wire(load, 0, n, "model.images.image_1")
            s = add(save_t, (x + 420, y), (360, 470))
            s["widgets_values"] = list(s["widgets_values"])
            s["widgets_values"][0] = "%s_%s_%s" % (char, expr, ed)
            wire(n, 0, s, "images")
            x += 820
        groups.append({"id": len(groups) + 1, "title": expr.upper(), "bounding": [-20, y - 50, x, row_h - 30],
                       "color": colours.get(expr, "#444"), "font_size": 24, "flags": {}})

    wf = dict(src["shell"])
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"],
               "last_link_id": ids["l"], "nodes": nodes, "links": links, "groups": groups})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [620, 120]}
    return wf, cost


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); raise SystemExit(1)
    char = args[0]
    def opt(name, default):
        return sys.argv[sys.argv.index(name) + 1].split(",") if name in sys.argv else default
    exprs = opt("--only", ["serious", "sad", "angry", "surprised"])
    # Nano Banana Pro by default: in the first side-by-side run on Megumi it
    # produced four clear, on-model expressions with zero geometry drift, and
    # Seedream's output filter refused the character outright ("may be related
    # to copyright restrictions").
    editors = opt("--editors", ["nanobanana"])
    for e in exprs:
        if e not in EXPRESSIONS: raise SystemExit("unknown expression %r" % e)
    for e in editors:
        if e not in EDITORS: raise SystemExit("unknown editor %r" % e)

    inp = os.path.join(IMAGES, "%s_edit_in.png" % char)
    if not os.path.exists(inp):
        raise SystemExit("no close-up at %s -- run composite_face.py --prepare first" % inp)
    if os.path.isdir(COMFY_INPUT):
        import shutil
        shutil.copy(inp, os.path.join(COMFY_INPUT, os.path.basename(inp)))

    wf, cost = build(char, exprs, editors)
    out = os.path.join(IMAGES, "%s_edit.json" % char)
    json.dump(wf, open(out, "w"), indent=1)
    print("rows      %s" % ", ".join(exprs))
    print("editors   %s" % ", ".join(EDITORS[e][3] for e in editors))
    print("cost      %d edits, about $%.2f" % (len(exprs) * len(editors), cost))
    print("workflow -> %s" % out)
