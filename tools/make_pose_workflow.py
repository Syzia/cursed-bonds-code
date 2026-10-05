"""
Build the ComfyUI workflow that paints one person into their room.

    python3 tools/make_pose_workflow.py dorm_common nobara evening
    python3 tools/make_pose_workflow.py utahime_office utahime
    python3 tools/make_pose_workflow.py --list        # the planned poses and what each costs
    python3 tools/make_pose_workflow.py --batch 3     # every pose of art batch 3, one file each

A pose is one whole 1920x1080 picture of the room with the person painted in,
doing what their caption says (PHASE2_DESIGN.md D36, section 5 row 6). The
game lays only a soft-edged box around the person over the room, so several
people can each use their own picture.

The workflow gives Nano Banana Pro two pictures and one instruction:
  1. the exact background the player sees at that hour
     (game/images/bg/<room>[_<variant>].png), and
  2. the person's neutral sprite on flat grey (never their name, never the
     series: closed editors refuse named characters),
and asks for the person in a named spot, doing the thing, "change nothing
else". Two candidates, fixed seeds.

It writes, into ~/Desktop/JJK Game images/phase2/:

    pose_<place>__<who>[__<variant>].json   drag it into the LOCAL ComfyUI, press Run
    pose_ref_<who>.png                      the sprite on grey (also copied to
                                            ComfyUI's input folder, with the background)

The results land in ~/ComfyUI-Shared/output as
`pose_<place>__<who>[__<variant>]_a_0000N_.png` and `..._b_...`. Then:

    python3 tools/install_pose.py <that picture>

which checks that only the person changed, measures the box, writes it to
game/layout/view_<place>.json and installs game/images/place/pose_....png.

POSES below is the plan (section 5's table). Each row was checked against the
schedule: tools/smoke/p2_view.rpy reads this table and fails if a row names a
place the person's routine never puts them (when_at), or a variant the room
has no picture for at an hour they are there. A row with `via` is produced
by something other than the routine (the Gojo night pins him on the ridge).

Cost: Nano Banana Pro is a paid partner node, about $0.16 a picture, and each
candidate is one picture: about $0.32 a pose. Nothing runs on this Mac's GPU.
"""
import sys, os, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
OUT = os.path.join(IMAGES, "phase2")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
CANDIDATES = 2
COST = 0.16
GREY = (128, 128, 128)

# The plan. who, place, variant ("" is the day picture), what they are doing
# (the caption the game shows), where in the picture and how, and the art
# batch it belongs to. Plain literals only: the harness reads this table.
# POSES-BEGIN
POSES = [
    {"who": "nobara", "place": "dorm_common", "variant": "evening", "batch": 3,
     "doing": "on the sofa, on her phone",
     "spot": "sitting on the sofa on the left of the room, leaning back into the cushions, legs crossed, "
             "looking down at a phone held in one hand"},
    {"who": "utahime", "place": "utahime_office", "variant": "", "batch": 3,
     "doing": "at her desk, buried in paperwork",
     "spot": "sitting in the chair behind the wooden desk on the left, leaning over the desk and writing on a "
             "sheet of paper, the stacks of paper beside her"},
    {"who": "yuji", "place": "cafeteria", "variant": "", "batch": 4,
     "doing": "halfway through an enormous bowl",
     "spot": "sitting on a chair at the second table from the front, on the right side of the room, facing the "
             "viewer, eating from a very large bowl of rice with chopsticks"},
    {"who": "megumi", "place": "classroom", "variant": "", "batch": 4,
     "doing": "reading at a desk by the window",
     "spot": "sitting at a desk in the row nearest the windows on the left, one elbow on the desk, reading an "
             "open book"},
    {"who": "shoko", "place": "infirmary", "variant": "", "batch": 4,
     "doing": "at the counter with coffee",
     "spot": "standing beside the desk on the left, leaning back against it, holding a coffee mug in one hand"},
    {"who": "maki", "place": "training", "variant": "", "batch": 4,
     "doing": "drilling with a staff",
     "spot": "standing in the middle of the open wooden floor in a low fighting stance, holding a long wooden "
             "staff in both hands"},
    {"who": "yaga", "place": "office", "variant": "", "batch": 4,
     "doing": "sewing a cursed doll",
     "spot": "sitting behind the desk, sewing a small stuffed toy animal with a needle and thread"},
    {"who": "ijichi", "place": "gate", "variant": "", "batch": 4,
     "doing": "on the phone beside the car",
     "spot": "standing to one side of the path in front of the gate, holding a mobile phone to his ear, the "
             "other hand holding a folder"},
    {"who": "toge", "place": "cafeteria", "variant": "", "batch": 4,
     "doing": "with onigiri, at the far table",
     "spot": "sitting at the table furthest from the viewer, near the serving counter, holding a rice ball in "
             "both hands"},
    {"who": "panda", "place": "courtyard", "variant": "", "batch": 4,
     "doing": "stretching, waiting for a sparring partner",
     "spot": "standing on the stone path in the middle of the courtyard, stretching one arm across the chest"},
    {"who": "yuji", "place": "courtyard", "variant": "", "batch": 4,
     "doing": "beside the vending machine, a can in his hand",
     "spot": "standing on the right side of the courtyard near the steps of the right-hand building, relaxed, "
             "holding a drink can in one hand"},
    {"who": "megumi", "place": "library", "variant": "", "batch": 4,
     "doing": "three books deep",
     "spot": "sitting at the reading table under the window in the middle of the room, three open books in "
             "front of him, reading"},
    {"who": "gojo", "place": "gojo_office", "variant": "", "batch": 4,
     "doing": "on the sofa, eating mochi in front of the TV",
     "spot": "sprawled on the sofa with his legs up, eating a small round rice cake, facing the television"},
    {"who": "gojo", "place": "ridge", "variant": "", "batch": 4, "via": "night_gojo",
     "doing": "sitting just outside the veil",
     "spot": "sitting cross-legged on the ground in the foreground, a little to the right, seen from the "
             "side, looking up towards the mountain"},
]
# POSES-END

HER = {"nobara", "maki", "shoko", "utahime"}

PROMPT = ("The first picture is a room. The second picture is a character on a plain grey background. "
          "Paint that same character into the room: {spot}. Draw {him} at the right size for where {he} is in "
          "the room, with the room's own light and a soft shadow where {he} touches the furniture or the floor. "
          "Keep {his} face, hair, clothes and colours exactly as in the second picture, in the same flat anime "
          "cel shading and line art. Change nothing else: every other part of the room must stay exactly as it "
          "is in the first picture, pixel for pixel, with the same framing, the same furniture and the same "
          "light. One person only. No text.")


def stem(place, who, variant=""):
    return "pose_%s__%s%s" % (place, who, "__" + variant if variant else "")


def place_bg(place):
    """The background's file stem for a place, read from game/sb_world.rpy."""
    import re
    src = open(os.path.join(ROOT, "game", "sb_world.rpy"), encoding="utf-8").read()
    m = re.search(r'"%s":\s*dict\(\s*indoor=\w+,\s*name="[^"]*",\s*bg="bg (\w+)"' % re.escape(place), src)
    if not m:
        raise SystemExit("no place %r in game/sb_world.rpy (LOCATIONS)" % place)
    return m.group(1)


def bg_file(place, variant=""):
    name = place_bg(place) + ("_" + variant if variant else "")
    return os.path.join(ROOT, "game", "images", "bg", name + ".png")


def find(who, place, variant=""):
    for row in POSES:
        if (row["who"], row["place"], row["variant"]) == (who, place, variant):
            return row
    return None


def write_ref(who, path):
    """The neutral sprite flattened onto grey, so the editor is never handed
    whatever colour hides under the sprite's see-through pixels."""
    from pngread import load
    from raster import Img
    src = os.path.join(ROOT, "game", "images", "char", who + "_neutral.png")
    if not os.path.exists(src):
        raise SystemExit("no sprite at %s" % src)
    im = load(src)
    out = Img(im.w, im.h, fill=GREY)
    if im.ch == 3:
        out.buf[:] = im.buf
    else:
        b, o = im.buf, out.buf
        for p in range(im.w * im.h):
            a = b[p * 4 + 3]
            if a:
                for k in range(3):
                    o[p * 3 + k] = (b[p * 4 + k] * a + GREY[k] * (255 - a)) // 255
    out.save(path)


def prompt_for(row):
    her = row["who"] in HER
    return PROMPT.format(spot=row["spot"], him="her" if her else "him", he="she" if her else "he",
                         his="her" if her else "his")


def build(row, bg_name, ref_name):
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

    name = stem(row["place"], row["who"], row["variant"])
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-1060, -40], "size": [460, 470],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## A pose: %s, %s\n\n"
        "Run this in the **local ComfyUI**.\n\n"
        "1. The two **Load Image** boxes should already show `%s` (the room) and `%s` (the person on grey). "
        "If one shows an error, click **choose file to upload** and pick it from `JJK Game images/phase2`.\n"
        "2. Press **Run**.\n\n"
        "The two coloured boxes each paint the picture once, so there are two versions to choose from: "
        "**A** on top, **B** under it.\n\n"
        "**What to look for:** the room must look untouched everywhere except where the person is. If the "
        "whole room was redrawn, Claude's install step will say so and use the other version.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, charged to your Comfy account).\n\n"
        "You don't need to save anything. The results go to ComfyUI's output folder and Claude picks them "
        "up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (row["who"].capitalize(), row["doing"], bg_name, ref_name, CANDIDATES, CANDIDATES * COST)]})

    room = add("LoadImage", (-1060, 470), (440, 360), title="Load Image: the room")
    room["widgets_values"] = [bg_name, "image"]
    ref = add("LoadImage", (-1060, 880), (440, 520), title="Load Image: the person on grey")
    ref["widgets_values"] = [ref_name, "image"]
    batch = add("BatchImagesNode", (-560, 470), (225, 120), title="Both pictures: the room first")
    wire(room, 0, batch, "images.image0")
    wire(ref, 0, batch, "images.image1")

    groups = []
    seed = 1500 + sum(ord(c) for c in name) % 400
    for k in range(CANDIDATES):
        letter = "ab"[k]
        y = k * 620
        g = add("GeminiImage2Node", (0, y), (420, 540), title="Nano Banana Pro: version %s" % letter.upper())
        w = g["widgets_values"]
        # A fixed seed for each box, so a Run that stops on a rate limit can be
        # pressed again and reuse what finished. 16:9 is the room's own shape;
        # 2K costs the same as 1K and install_pose.py brings it to 1920x1080.
        w[0], w[2], w[3], w[4], w[5], w[6] = prompt_for(row), seed + k, "fixed", "16:9", "2K", "IMAGE"
        wire(batch, 0, g, "images")
        s = add("SaveImage", (440, y), (620, 540), title="Version %s" % letter.upper())
        s["widgets_values"] = ["%s_%s" % (name, letter)]
        wire(g, 0, s, "images")
        groups.append({"id": k + 1, "title": "VERSION %s" % letter.upper(),
                       "bounding": [-20, y - 50, 1100, 600], "color": "#3f4f5a", "font_size": 24, "flags": {}})

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links, "groups": groups})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.5, "offset": [1120, 120]}
    return wf


def make(row, out_dir=None):
    out_dir = out_dir or OUT
    bg = bg_file(row["place"], row["variant"])
    if not os.path.exists(bg):
        raise SystemExit("no picture at %s: a pose is painted on the picture the player sees, so make the "
                         "room first" % bg)
    os.makedirs(out_dir, exist_ok=True)
    name = stem(row["place"], row["who"], row["variant"])
    bg_name = "pose_room_" + os.path.basename(bg)
    ref_name = "pose_ref_%s.png" % row["who"]
    shutil.copy(bg, os.path.join(out_dir, bg_name))
    write_ref(row["who"], os.path.join(out_dir, ref_name))
    if out_dir == OUT and os.path.isdir(COMFY_INPUT):
        shutil.copy(os.path.join(out_dir, bg_name), os.path.join(COMFY_INPUT, bg_name))
        shutil.copy(os.path.join(out_dir, ref_name), os.path.join(COMFY_INPUT, ref_name))
    out = os.path.join(out_dir, name + ".json")
    json.dump(build(row, bg_name, ref_name), open(out, "w"), indent=1)
    print("%-44s %d versions, about $%.2f" % (name, CANDIDATES, CANDIDATES * COST))
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

    out_dir, batch = opt("--out"), opt("--batch")
    if "--list" in argv:
        for k, row in enumerate(POSES):
            print("%2d  batch %d  %-42s %s%s" % (k + 1, row["batch"], stem(row["place"], row["who"], row["variant"]),
                                               row["doing"], "  (via %s)" % row["via"] if row.get("via") else ""))
        print("%d poses, about $%.2f" % (len(POSES), len(POSES) * CANDIDATES * COST))
        return
    args = [a for a in argv if not a.startswith("--")]
    if [a for a in argv if a.startswith("--")]:
        print(__doc__); raise SystemExit(1)
    if batch is not None:
        rows = [r for r in POSES if str(r["batch"]) == batch]
        if not rows:
            raise SystemExit("no pose in batch %s" % batch)
    elif len(args) in (2, 3):
        ## <place> <who> [variant], as the plan writes it (section 5, row 6);
        ## the two the other way round are understood too.
        place, who = args[0], args[1]
        variant = args[2] if len(args) == 3 else ""
        row = find(who, place, variant) or find(place, who, variant)
        if row is None:
            raise SystemExit("%s is not in the plan (POSES): add a row saying where in the room and doing "
                             "what, or see --list" % stem(place, who, variant))
        rows = [row]
    else:
        print(__doc__); raise SystemExit(1)
    for row in rows:
        make(row, out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
