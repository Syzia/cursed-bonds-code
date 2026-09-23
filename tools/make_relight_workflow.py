"""
Build a ComfyUI workflow that relights chosen backgrounds for another time of day.

    python3 tools/make_relight_workflow.py your_room night
    python3 tools/make_relight_workflow.py classroom your_room clean   # tidy up, same layout
    python3 tools/make_relight_workflow.py girls_dorm:clean infirmary:night rooftop:evening --versions 1

Takes the approved daytime picture from `JJK Game images/backgrounds_chosen/`
and asks Nano Banana Pro to change only the light, so evening and night are
recognisably the same place: same furniture, same angle, same art style. A
fresh generation would give a different room at night. Saved as
`bg_<name>_<time>`, two versions each unless --versions says otherwise;
install the pick with

    python3 tools/install_bg.py <file> <name>_<time>

Runs in the local ComfyUI (a paid partner node, ~$0.16 a picture).
"""
import sys, os, json, copy, uuid, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
CHOSEN = os.path.join(IMAGES, "backgrounds_chosen")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
VERSIONS = 2
COST = 0.16

KEEP = ("Keep everything else exactly the same: the same place, layout, furniture, camera angle, "
        "framing and soft painted anime art style. No people, no characters, no text.")

# Rooms and outdoor places get lit differently at night; a room needs its own
# lamps on. Lights are only ever switched on where the picture already has
# them: asked for "lanterns" by name, the model would put stone lanterns on a
# riverbank.
TIMES = {
    ("night", True): "Change the time of day to night. Outside the windows it is dark, with a deep blue "
                     "night sky. The room's own ceiling lights are switched on and fill it with warm "
                     "yellow light and soft shadows.",
    ("night", False): "Change the time of day to night: a deep blue night sky with a few stars and a "
                      "faint moon, and cool blue moonlight on everything, with soft shadows. Any windows "
                      "or lanterns already in the picture glow warm yellow; do not add new ones.",
    ("evening", True): "Change the time of day to early evening. Warm orange sunset light slants in "
                       "through the windows, long soft shadows cross the floor, and the sky outside "
                       "glows orange and pink.",
    ("evening", False): "Change the time of day to early evening: a warm orange and pink sunset sky, "
                        "low golden sunlight with long soft shadows. Any windows already in the picture "
                        "catch the light or begin to glow; do not add new ones.",
    # Not a time of day: a tidy-up of an approved picture, for rooms that came
    # out looking neglected, without losing a layout that was liked. Described
    # as the finished state, never as "remove ... water mark": Google's filter
    # reads that as a request to strip a watermark and blocks the picture.
    ("clean", True): "Make this room look freshly decorated and well cared for: the walls and ceiling "
                     "are smooth, evenly painted plaster in one soft, even colour, spotless, with no "
                     "stains, damp patches, specks or grime; the wooden floor is clean and polished; "
                     "the light is slightly fresher, with clean, bright daylight.",
    ("clean", False): "Make this place look well cared for: walls and surfaces clean and evenly "
                      "coloured, with no stains or grime, keeping natural moss and weathered wood.",
}

# Wording for one place in particular. The user asked for the bedroom's
# windows to be shut and covered at night.
PLACE_TIMES = {
    ("your_room", "night"): "Change the time of day to night. Outside the windows it is dark, with a deep "
                            "blue night sky. The windows are closed, with pale curtains drawn across "
                            "them. The ceiling lamp is switched on and fills the room with warm yellow "
                            "light and soft shadows, and a small lamp glows on the desk.",
}


def build(jobs, versions=VERSIONS):
    """jobs: (name, when) pairs, one row each."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from make_bg_workflow import INTERIORS
    proto = json.load(open(os.path.join(ROOT, "tools", "comfy_nodes", "edit_nodes.json")))
    P, shell = proto["nodes"], proto["shell"]
    nodes, links, groups = [], [], []
    ids = {"n": 0, "l": 0}

    def add(kind, pos, size=None, title=None, widgets=None):
        ids["n"] += 1
        n = copy.deepcopy(P[kind])
        n["id"], n["pos"], n["order"] = ids["n"], list(pos), ids["n"]
        if size: n["size"] = list(size)
        for i in n.get("inputs", []): i["link"] = None
        for o in n.get("outputs", []): o["links"] = []
        if title: n["title"] = title
        if widgets is not None: n["widgets_values"] = widgets
        nodes.append(n)
        return n

    def wire(a, b, b_input, a_slot=0):
        ids["l"] += 1
        slot = next(i for i, x in enumerate(b["inputs"]) if x["name"] == b_input)
        kind = a["outputs"][a_slot]["type"]
        assert kind == b["inputs"][slot]["type"], (a["type"], b["type"], b_input)
        links.append([ids["l"], a["id"], a_slot, b["id"], slot, kind])
        a["outputs"][a_slot]["links"].append(ids["l"])
        b["inputs"][slot]["link"] = ids["l"]

    count = len(jobs) * versions
    listing = "\n".join("- %s: %s" % (name.replace("_", " "), "clean-up" if when == "clean" else when)
                         for name, when in jobs)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-900, -520], "size": [600, 420],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Relight and clean-up\n\n%s\n\n"
        "Run this in the **local ComfyUI** and press **Run**. Each row takes the "
        "approved picture and changes only the light (or tidies it up), keeping "
        "the layout, %d version%s each.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro).\n\n"
        "No need to save anything. Claude picks the results up from ComfyUI's output folder.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press "
        "**Run** again: finished pictures are reused, not paid for twice."
        % (listing, versions, "" if versions == 1 else "s", count, count * COST)]})

    gem = P["GeminiImage2Node"]["widgets_values"]
    row_h = 560
    for r, (name, when) in enumerate(jobs):
        src = os.path.join(CHOSEN, name + ".png")
        if not os.path.exists(src):
            raise SystemExit("no approved daytime picture at %s" % src)
        staged = "day_%s.png" % name
        shutil.copy(src, os.path.join(COMFY_INPUT, staged))
        y = r * row_h
        ld = add("LoadImage", (-900, y), (300, 320), title="Daytime: %s" % name, widgets=[staged, "image"])
        prompt = (PLACE_TIMES.get((name, when)) or TIMES[(when, name in INTERIORS)]) + " " + KEEP
        for k in range(versions):
            w = list(gem)
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt, 500 + r * 10 + k, "fixed", "16:9", "1K", "IMAGE"
            n = add("GeminiImage2Node", (k * 820, y), (400, 360), title="%s at %s (%d)" % (name, when, k + 1),
                    widgets=w)
            wire(ld, n, "images")
            s = add("SaveImage", (k * 820 + 420, y), (380, 360), widgets=["bg_%s_%s" % (name, when)])
            wire(n, s, "images")
        groups.append(("%s: %s" % (name.replace("_", " ").upper(), when.upper()), y))

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-920, gy - 50, 2560, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, gy) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [980, 560]}
    return wf, count


if __name__ == "__main__":
    argv = sys.argv[1:]
    versions = VERSIONS
    if "--versions" in argv:
        i = argv.index("--versions")
        versions = int(argv[i + 1])
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    whens = ("night", "evening", "clean")
    if args and all(":" in a for a in args):
        jobs = [tuple(a.split(":", 1)) for a in args]
    elif len(args) >= 2 and args[-1] in whens:
        jobs = [(n, args[-1]) for n in args[:-1]]
    else:
        print(__doc__); raise SystemExit(1)
    for name, when in jobs:
        if when not in whens:
            raise SystemExit("%r: the time must be one of %s" % (name, ", ".join(whens)))
    wf, count = build(jobs, versions)
    out = os.path.join(IMAGES, "relight.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("relight   %s, %d version%s each, about $%.2f" % (
        ", ".join("%s:%s" % j for j in jobs), versions, "" if versions == 1 else "s", count * COST))
    print("workflow -> %s" % out)
