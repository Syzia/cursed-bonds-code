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
}
CHAR_KEEP = {
    "gojo": "His eyes stay completely hidden behind the wide black cloth blindfold: keep the blindfold, "
            "and everything above the nose, exactly as it is, and do not draw any eyes.",
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
