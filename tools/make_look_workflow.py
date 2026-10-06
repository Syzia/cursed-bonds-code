"""
Build the ComfyUI workflow that tries three looks on three places.

    python3 tools/make_look_workflow.py
    python3 tools/make_look_workflow.py --places courtyard,library
    python3 tools/make_look_workflow.py --treatments A,C
    python3 tools/make_look_workflow.py --list        # the treatments and what a Run costs

A look test is the picture the game already has, painted again IN PLACE: the
same camera, the same walls, doors and paths, only the way it is rendered
changes. In place matters because every icon, exit and standing spot in the
game is positioned on these pictures.

The workflow gives Nano Banana Pro one picture and one instruction for each
box: the background as it is today (game/images/bg/<place>.png) and one of
the treatments below. Every instruction starts with the same HEAD, which is
the "nothing moves" rule. One candidate for each, fixed seeds. No prompt
names the series or a character: closed editors refuse them.

    A  anime frame     a clean, sharp frame from a modern TV anime
    B  real place      an actual place you could walk into, lived in
    C  clean-up only   the same painting with the grain and the blur taken off

It writes, into ~/Desktop/JJK Game images/look_test/:

    look_test.json            drag it into the LOCAL ComfyUI, press Run
    look_in_<place>.png       the picture as it is today (also copied to
                              ComfyUI's input folder)

The workflow is a grid: one row for each place, the picture as it is now on
the left, then one column for each treatment. The results land in
~/ComfyUI-Shared/output as `look_<place>_<A|B|C>_0000N_.png`, so they sort
together. Nothing is installed from this test: it only settles the look.

Size: the node offers 1K, 2K and 4K. At 16:9 those are 1376x768, 2752x1536
and 5504x3072, so 2K is the smallest that is at least 1920 wide.

Cost: Nano Banana Pro is a paid partner node. 1K and 2K are the same price,
about $0.16 a picture; 4K is about $0.29. Each box is one picture at 2K: nine
boxes, about $1.45 a Run. Nothing runs on this Mac's GPU.
"""
import sys, os, json, copy, uuid, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
OUT = os.path.join(IMAGES, "look_test")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
COST = 0.1608          # gemini-3-pro-image-preview at 1K or 2K (4K is 0.288)
RESOLUTION = "2K"      # 2752x1536 at 16:9; 1K is 1376x768, too small
PLACES = ["courtyard", "dorm_common", "library"]
NAMES = {"courtyard": "Courtyard", "dorm_common": "Common Room", "library": "Library"}

HEAD = ("This is a background picture for a visual novel. Redraw this exact scene. Keep the camera position, "
        "angle and framing exactly as they are. Keep every wall, door, window, piece of furniture, building, "
        "path, rock and tree exactly where it is, at the same size and shape. No people, no animals, no text, "
        "no logos. Output a 16:9 picture.")

# letter: (short name, the instruction after HEAD). Plain literals only.
# TREATMENTS-BEGIN
TREATMENTS = {
    "A": ("anime frame",
          "Render it as a clean, sharp background frame from a modern high-budget TV anime: crisp precise "
          "edges, clean smooth colour with clear shapes of light and shadow, fine detail in the architecture "
          "and materials. Remove all film grain, noise, speckle, canvas texture and visible brush strokes. No "
          "soft-focus haze and no glow washing out detail. Through every window show a clear, in-focus view: "
          "tree trunks and leaves, the tiled roof of the next building, blue sky with a few clouds. Bright "
          "natural morning daylight. Do not add or remove any object."),
    "B": ("real place",
          "Make it feel like an actual place you could walk into, not an illustration: the realism of a "
          "background from an animated feature film that was painted over a photograph. Real materials (grain "
          "in the floorboards, plaster, reflections in glass, worn stone, moss), physically believable "
          "daylight with soft shadows and bounced light, true depth and atmosphere. It must still be "
          "hand-painted enough that cel-shaded anime characters can stand in it. No grain and no noise. "
          "Through every window show a clear, in-focus view of real trees, roofs and sky. You may add a few "
          "small signs that people live and study here (an umbrella by a door, a jacket over a chair, a cup "
          "on a table, fallen leaves on a path), only where they cover nothing that is already there."),
    "C": ("clean-up only",
          "Change nothing about the content or the painting style. Only clean the picture: remove film grain, "
          "noise and speckle, sharpen soft edges and fine detail, and make the view through every window "
          "clear and in focus instead of a pale blur. Everything else stays identical, pixel for pixel where "
          "possible."),
}
# TREATMENTS-END

# The grid. One cell is a Nano Banana Pro box with its result under it.
# The Nano Banana Pro box is tall enough for its eight widgets (two of them
# text boxes) without ComfyUI having to stretch it on load.
CELL_W, CELL_H = 600, 840
GEM_H, SAVE_H = 360, 400
ROW_H = CELL_H + 120


def stem(place, letter):
    return "look_%s_%s" % (place, letter)


def in_name(place):
    return "look_in_%s.png" % place


def bg_file(place):
    return os.path.join(ROOT, "game", "images", "bg", place + ".png")


def label(place):
    return NAMES.get(place, place.replace("_", " ").capitalize())


def prompt_for(letter):
    return HEAD + " " + TREATMENTS[letter][1]


def build(places, letters):
    proto = json.load(open(os.path.join(ROOT, "tools", "comfy_nodes", "edit_nodes.json")))
    P, shell = proto["nodes"], proto["shell"]
    nodes, links = [], []
    ids = {"n": 0, "l": 0}

    def add(kind, pos, size=None, title=None):
        ids["n"] += 1
        node = copy.deepcopy(P[kind])
        node["id"], node["pos"], node["order"] = ids["n"], list(pos), ids["n"]
        if size: node["size"] = list(size)
        for i in node.get("inputs", []): i["link"] = None
        for o in node.get("outputs", []): o["links"] = [] if o.get("links") is not None else None
        if title: node["title"] = title
        node["widgets_values"] = list(node.get("widgets_values") or [])
        node.pop("widgets_values_named", None)
        nodes.append(node)
        return node

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

    count = len(places) * len(letters)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [0, -560], "size": [CELL_W * 2 - 40, 460],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## The look test: %d places, %d looks\n\n"
        "Run this in the **local ComfyUI**. Press **Run** once.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, about $%.2f a picture, charged to your "
        "Comfy account).\n\n"
        "**Rows** are places: %s. The first box in each row is the picture **as it is now**. If it shows an "
        "error, click **choose file to upload** and pick the `look_in_...png` of that place from "
        "`JJK Game images/look_test`.\n\n"
        "**Columns** are looks, the same three for every place:\n\n%s\n\n"
        "In every one the camera, the walls, the doors and the furniture should be exactly where they are "
        "now. Only the way it is painted should change.\n\n"
        "Nothing in the game changes from this test. You don't need to save anything: the results go to "
        "ComfyUI's output folder and Claude picks them up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (len(places), len(letters), count, count * COST, COST,
           ", ".join("**%s**" % label(p) for p in places),
           "\n".join("- **%s, %s**" % (l, TREATMENTS[l][0]) for l in letters))]})

    groups = []
    for r, place in enumerate(places):
        y = r * ROW_H
        src = add("LoadImage", (0, y), (CELL_W - 40, GEM_H + 20 + SAVE_H),
                  title="Load Image: %s as it is now" % label(place))
        src["widgets_values"] = [in_name(place), "image"]
        for c, letter in enumerate(letters):
            x = (c + 1) * CELL_W
            g = add("GeminiImage2Node", (x, y), (CELL_W - 40, GEM_H),
                    title="Nano Banana Pro: %s, %s" % (letter, TREATMENTS[letter][0]))
            w = g["widgets_values"]
            # A fixed seed for each box, so a Run that stops on a rate limit can
            # be pressed again and reuse what finished. 16:9 is the picture's own
            # shape; 2K costs the same as 1K and is the smallest size that is at
            # least 1920 wide.
            seed = 2600 + sum(ord(ch) for ch in place) % 400 + "ABC".index(letter)
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt_for(letter), seed, "fixed", "16:9", RESOLUTION, "IMAGE"
            wire(src, 0, g, "images")
            s = add("SaveImage", (x, y + GEM_H + 60), (CELL_W - 40, SAVE_H),
                    title="%s: %s, %s" % (label(place), letter, TREATMENTS[letter][0]))
            s["widgets_values"] = [stem(place, letter)]
            wire(g, 0, s, "images")
        groups.append({"id": r + 1,
                       "title": "%s:  now  |  %s" % (label(place).upper(), "  |  ".join(
                           "%s %s" % (l, TREATMENTS[l][0]) for l in letters)),
                       "bounding": [-20, y - 50, (len(letters) + 1) * CELL_W, CELL_H + 70],
                       "color": "#3f4f5a", "font_size": 24, "flags": {}})

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links, "groups": groups})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.4, "offset": [80, 620]}
    return wf


def make(places, letters, out_dir=None):
    out_dir = out_dir or OUT
    for place in places:
        if not os.path.exists(bg_file(place)):
            raise SystemExit("no picture at %s" % bg_file(place))
    os.makedirs(out_dir, exist_ok=True)
    for place in places:
        shutil.copy(bg_file(place), os.path.join(out_dir, in_name(place)))
        if out_dir == OUT and os.path.isdir(COMFY_INPUT):
            shutil.copy(bg_file(place), os.path.join(COMFY_INPUT, in_name(place)))
    out = os.path.join(out_dir, "look_test.json")
    json.dump(build(places, letters), open(out, "w"), indent=1)
    count = len(places) * len(letters)
    for place in places:
        print("%-14s %s" % (place, "  ".join(stem(place, l) for l in letters)))
    print("%d pictures at %s, about $%.2f" % (count, RESOLUTION, count * COST))
    print("   workflow -> %s" % out)
    return out


def main(argv):
    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv):
                raise SystemExit("%s needs a value" % flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    out_dir, places, letters = opt("--out"), opt("--places"), opt("--treatments")
    places = [p for p in places.split(",") if p] if places else list(PLACES)
    letters = [l.upper() for l in letters.split(",") if l] if letters else sorted(TREATMENTS)
    if "--list" in argv:
        for l in sorted(TREATMENTS):
            print("%s  %-14s %s" % (l, TREATMENTS[l][0], TREATMENTS[l][1]))
        print("%d places x %d treatments, about $%.2f a Run" % (len(places), len(letters),
                                                               len(places) * len(letters) * COST))
        return
    if argv or not places or not letters:
        print(__doc__); raise SystemExit(1)
    for l in letters:
        if l not in TREATMENTS:
            raise SystemExit("no treatment %r: choose from %s" % (l, ",".join(sorted(TREATMENTS))))
    if len(set(places)) != len(places) or len(set(letters)) != len(letters):
        raise SystemExit("a place or a treatment is named twice")
    make(places, letters, out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
