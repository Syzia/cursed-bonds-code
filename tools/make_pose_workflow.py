"""
Build the ComfyUI workflow that paints one person into their room.

    python3 tools/make_pose_workflow.py dorm_common nobara evening
    python3 tools/make_pose_workflow.py utahime_office utahime
    python3 tools/make_pose_workflow.py megumi_room megumi night --asleep    # the shape under the blanket
    python3 tools/make_pose_workflow.py --list        # the planned poses and what each costs
    python3 tools/make_pose_workflow.py --batch 5     # every pose of art batch 5, one file each
    python3 tools/make_pose_workflow.py dorm_common nobara evening --print   # the prompt only; writes nothing
    options: --out <folder>  --manifest <pictures.json>  --keep <folder of keep lists>  --record <campus.json>
             --layout-dump <file>  --root <a copy of the project>  --plan <rows.json, in place of POSES>

A pose is one whole 1920x1080 picture of the room with the person painted in,
doing what their caption says (PHASE2_DESIGN.md D36; docs/UI2_DESIGN.md 5.12,
7.2). The game lays only a soft-edged box around the person over the room, so
several people can each use their own picture.

The workflow gives Nano Banana Pro two pictures and one instruction:
  1. the exact background the player sees at that hour
     (game/images/bg/<room>[_<variant>].png), and
  2. the person's neutral sprite on flat grey (never their name, never the
     series: closed editors refuse named characters),
and asks for the person in a named spot, doing the thing, "change nothing
else". Two candidates, fixed seeds.

WHAT THE TOOL HOLDS TO (the second UI overhaul; all of it is checked before
anything is written, and a refusal is one plain line):

  - ORDER (K8). A pose is painted on the picture the player sees, so the room,
    and the hour picture the pose is seen on, must be installed in the new
    look first: revision 2 or later in game/layout/pictures.json, and not
    stale. A pose on an old picture would stop showing the day its room is
    installed (K7).
  - NEVER AT THE BATHS OR THE POOL (K16). A row at the Bathhouse, the Sauna
    or the Pool is refused.
  - SIZE. The prompt says how tall the person stands, in pixels, at that
    spot, so a seated person is not drawn large. The number comes from the
    room's `scale` (one door or post taken as 200 cm): its
    game/layout/view_<place>.json first, else the same triple in its keep
    list, tools/bgs/keep/<picture>.json. With neither the tool refuses.
  - THE CLOTHES SENTENCE IS FROZEN (K16): "Keep his face, hair, clothes and
    colours exactly as in the second picture". CLOTHES below is that
    sentence; do not edit it.
  - ASLEEP. A row whose `state` is "asleep" is not a figure. The tool writes
    one fixed sentence, ASLEEP below ("in the bed, a sleeper under a blanket,
    turned to the wall; only the top of the hair shows; no face, no arm, no
    shoulder"; for Panda "a very large mound under a blanket"), with the
    sprite as the reference for hair colour only. That sentence is frozen
    too. Such a picture is named pose_<place>__<who>__<variant>__asleep.
  - TOKYO. A row whose place is a district is accepted only when the game's
    away table (WORLD_AWAY, read from the layout dump) sends that person
    there. The order check is on the district's own picture, and the height
    comes from the `scale` in that picture's keep list.
  - THE PROMPT CHECK. A row's `spot` is read by tools/check_prompts.py as a
    line of its place: no banned word, no name, no count of movable things,
    nothing against the decency rule.

It writes, into ~/Desktop/JJK Game images/ui2/:

    pose_<place>__<who>[__<variant>][__asleep].json   drag it into the LOCAL ComfyUI, press Run
    pose_ref_<who>.png                                the sprite on grey (also copied to
                                                      ComfyUI's input folder, with the background)

The results land in ~/ComfyUI-Shared/output as `pose_..._a_0000N_.png` and
`..._b_...`. Then:

    python3 tools/install_pose.py <that picture>

which checks that only the person changed, measures the box, refuses a box
that covers an exit or overlaps another pose that can show with it, and
writes the box to game/layout/pose_<place>.json, the picture to
game/images/place/ and the pose's row to game/layout/pictures.json.

POSES below is the plan. Each row was checked against the schedule:
tools/smoke/p2_view.rpy reads this table and fails if a row names a place the
person's routine never puts them (when_at), or a variant the room has no
picture for at an hour they are there. A row with `via` is produced by
something other than the routine (the Gojo night pins him on the ridge).
A row may also carry `state` ("awake", the default, or "asleep"), `at` (the
one hotspot id of its room the person is painted at) and `days` ("weekdays"
or "weekends"). THE ROWS ARE U3'S TO RE-PICK (67 of them, docs/UI2_DESIGN.md
7.2); wave 0 changed the tooling only, and one number: Nobara's row is batch
5, which is where the plan now has it.

The game's numbers (which picture a place has, who is sent to Tokyo) come
from the layout dump through tools/game_layout.py, which refuses a dump that
is out of date; in a worktree pass --layout-dump <file> (5.4).

Cost: Nano Banana Pro is a paid partner node, about $0.16 a picture, and each
candidate is one picture: about $0.32 a pose. Nothing runs on this Mac's GPU,
and the tool queues nothing: the owner presses Run (K14).
"""
import sys, os, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_layout
import check_campus
import check_prompts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
OUT = os.path.join(IMAGES, "ui2")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
KEEP_DIR = os.path.join(ROOT, "tools", "bgs", "keep")
CANDIDATES = 2
COST = 0.16
GREY = (128, 128, 128)
SCALE_CM = 200.0            # the door or post a room's `scale` measures is taken as this tall


class Refused(Exception):
    """Why a pose cannot be made, in one plain line."""


# The plan. who, place, variant ("" is the day picture), what they are doing
# (the caption the game shows), where in the picture and how, and the art
# batch it belongs to. Plain literals only: the harness reads this table.
# POSES-BEGIN
POSES = [
    {"who": "nobara", "place": "dorm_common", "variant": "evening", "batch": 5,
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

# FROZEN (K16, docs/UI2_DESIGN.md 2.2): the sentence that keeps a person as their sprite. Not to be edited.
CLOTHES = ("Keep {his} face, hair, clothes and colours exactly as in the second picture, in the same flat anime "
           "cel shading and line art.")
# FROZEN (K16, 5.12): what an asleep row is. Not to be edited. Not a figure: nothing of a person is drawn
# but the top of the hair.
ASLEEP = "in the bed, a sleeper under a blanket, turned to the wall; only the top of the hair shows; no face, no arm, no shoulder"
ASLEEP_PANDA = "in the bed, a very large mound under a blanket"

# What the sprite alone does not carry across, in plain words (AUDIT P12: the editor drew a stranger).
LOOKS = {"utahime": "{he} has long dark hair, a ribbon and a scar across the face."}

PROMPT = ("The first picture is a room. The second picture is a character on a plain grey background. "
          "Paint that same character into the room: {spot}. {size} Draw {him} in the room's own light, in the "
          "same clean flat anime cel shading as the reference figure, with a soft contact shadow only where {he} "
          "touches the furniture or the floor. " + CLOTHES + "{looks} Change nothing else: every other part of "
          "the room must stay exactly as it is in the first picture, pixel for pixel, with the same framing, the "
          "same furniture and the same light. One person only. No text.")
SIZE = ("Size: standing upright at that spot {he} would be about {px} pixels tall in the first picture, which is "
        "{pct} percent of its height (a door there is about {door} pixels tall); sitting, crouching or leaning "
        "{he} is shorter than that. Do not draw {him} larger.")
PROMPT_ASLEEP = ("The first picture is a room at night. The second picture is a reference for one hair colour "
                 "only; draw nothing else from it. Change one thing in the room: {shape}.{where} The blanket is "
                 "plain and lies in the room's own light, in the same clean flat anime shading as the room. "
                 "Change nothing else: every other part of the room must stay exactly as it is in the first "
                 "picture, pixel for pixel, with the same framing, the same furniture and the same light. No text.")
PROMPT_ASLEEP_PLAIN = ("The first picture is a room at night. Change one thing in the room: {shape}.{where} The "
                       "blanket is plain and lies in the room's own light, in the same clean flat anime shading "
                       "as the room. Change nothing else: every other part of the room must stay exactly as it "
                       "is in the first picture, pixel for pixel, with the same framing, the same furniture and "
                       "the same light. No text.")


def state_of(row):
    return row.get("state") or "awake"


def stem(place, who, variant="", state="awake"):
    return "pose_%s__%s%s%s" % (place, who, "__" + variant if variant else "", "__asleep" if state == "asleep" else "")


def row_stem(row):
    return stem(row["place"], row["who"], row["variant"], state_of(row))


def find(who, place, variant="", state="awake"):
    for row in POSES:
        if (row["who"], row["place"], row["variant"], state_of(row)) == (who, place, variant, state):
            return row
    return None


def is_district(lay, place):
    return not lay.has_place(place) and place in (lay.districts() or [])


def bg_stem(lay, row):
    """The file stem of the picture a row is painted on: dorm_common_evening, harajuku."""
    place = row["place"]
    base = lay.bg_stem(place) if lay.has_place(place) else place
    return base + ("_" + row["variant"] if row["variant"] else "")


def bg_file(lay, row, root=None):
    return os.path.join(root or ROOT, "game", "images", "bg", bg_stem(lay, row) + ".png")


def check_place(lay, row):
    """K16 and 5.12: where a pose may be painted at all."""
    who, place = row["who"], row["place"]
    if place in game_layout.NO_POSE_PLACES:
        raise Refused("no pose is ever made at the Bathhouse, the Sauna or the Pool (K16): %s is refused" % row_stem(row))
    if lay.has_place(place):
        return
    districts = lay.districts()
    if districts is None:
        raise Refused("%s is not a place of the game, and the layout dump has no away table (world_away), so "
                      "nobody is known to be sent to a Tokyo district: %s is refused" % (place, row_stem(row)))
    sent = sorted(set(d for day, per in lay.cells() for d in [lay.away(who, day, per)] if d))
    if place not in sent:
        raise Refused("%s is refused: the game never sends %s to %s (WORLD_AWAY sends %s)"
                      % (row_stem(row), who, place, "them to " + " and ".join(sent) if sent else "them nowhere"))
    if state_of(row) == "asleep":
        raise Refused("%s is refused: nobody is asleep in a street" % row_stem(row))


def order_check(lay, manifest, row, root=None):
    """K8: the picture a pose is painted on is installed in the new look, and fresh."""
    name = bg_stem(lay, row)
    pics = (manifest or {}).get("pictures", {})
    line = pics.get(name) or {}
    rev = check_campus.rev_of(manifest, name)
    what = "%s.png" % name
    if rev < 2:
        raise Refused("%s cannot be made yet: the picture it is painted on, %s, is not installed in the new "
                      "look (it is at revision %d). A pose is made after its room and the hour picture it is seen "
                      "on (K8)." % (row_stem(row), what, rev))
    if line.get("of") and line.get("of_rev") != check_campus.rev_of(manifest, line["of"]):
        raise Refused("%s cannot be made yet: %s was made for revision %s of %s.png, which is now at revision %d; "
                      "that hour picture is remade first (K7, K8)."
                      % (row_stem(row), what, line.get("of_rev"), line["of"], check_campus.rev_of(manifest, line["of"])))
    path = bg_file(lay, row, root)
    if not os.path.exists(path):
        raise Refused("no picture at %s: a pose is painted on the picture the player sees, so make the room "
                      "first" % path)
    return path


def scale_for(lay, row, root=None, keep_dir=None):
    """(the `scale` triple [x, y top, y bottom], where it was read from) for the room a row is painted in."""
    place = row["place"]
    base = lay.bg_stem(place) if lay.has_place(place) else place
    tried = []
    side = os.path.join(root or ROOT, "game", "layout", "view_%s.json" % place)
    keeps = [os.path.join(keep_dir or KEEP_DIR, n + ".json") for n in dict.fromkeys([base, place])]
    for path in [side] + keeps:
        tried.append(path)
        if not os.path.exists(path):
            continue
        try:
            sc = json.load(open(path, encoding="utf-8")).get("scale")
        except ValueError as e:
            raise Refused("%s is not JSON: %s" % (path, e))
        if sc is None:
            continue
        if not (isinstance(sc, list) and len(sc) == 3 and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                                              for v in sc) and sc[2] > sc[1]):
            raise Refused("%s: `scale` must be [x, y top, y bottom] of a door or post, the bottom below the top" % path)
        return sc, path
    raise Refused("%s has no `scale` (a door or post taken as 200 cm) in game/layout/view_%s.json or in its keep "
                  "list tools/bgs/keep/%s.json: without it the prompt cannot say how tall the person stands"
                  % (lay.name(place), place, base))


def height_px(who, scale):
    """How many pixels tall this person stands beside the room's door or post."""
    from keysprite import HEIGHT_CM
    if who not in HEIGHT_CM:
        raise Refused("%s has no height in tools/keysprite.py (HEIGHT_CM)" % who)
    return int(round(HEIGHT_CM[who] * (scale[2] - scale[1]) / SCALE_CM))


def words(row):
    her = row["who"] in HER
    return {"him": "her" if her else "him", "he": "she" if her else "he", "his": "her" if her else "his"}


def prompt_for(row, scale=None):
    """The prompt of one row. scale: the room's `scale` triple (an awake row needs it)."""
    w = words(row)
    if state_of(row) == "asleep":
        where = (" The bed: %s." % row["spot"].rstrip(".")) if row.get("spot") else ""
        if row["who"] == "panda":
            return PROMPT_ASLEEP_PLAIN.format(shape=ASLEEP_PANDA, where=where)
        return PROMPT_ASLEEP.format(shape=ASLEEP, where=where)
    if scale is None:
        raise Refused("%s: the room's `scale` is needed for the height in the prompt" % row_stem(row))
    px = height_px(row["who"], scale)
    size = SIZE.format(px=px, pct=int(round(100.0 * px / 1080)), door=int(round(scale[2] - scale[1])), **w)
    looks = LOOKS.get(row["who"])
    looks = (" " + looks.format(**w)[0].upper() + looks.format(**w)[1:]) if looks else ""
    return PROMPT.format(spot=row["spot"], size=size, looks=looks, **w)


def check_words(row, record=None):
    """The prompt check on what is this row's own: its spot, as a line of its place; and no name anywhere."""
    bad = []
    if row.get("spot"):
        bad += check_prompts.findings(row["spot"], record, row["place"])
    if bad:
        raise Refused("the prompt for %s is refused (tools/check_prompts.py):\n  - %s" % (row_stem(row), "\n  - ".join(bad)))


def write_ref(who, path, root=None):
    """The neutral sprite flattened onto grey, so the editor is never handed
    whatever colour hides under the sprite's see-through pixels."""
    from pngread import load
    from raster import Img
    src = os.path.join(root or ROOT, "game", "images", "char", who + "_neutral.png")
    if not os.path.exists(src):
        raise Refused("no sprite at %s" % src)
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


def build(row, bg_name, ref_name, prompt):
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

    name = row_stem(row)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-1060, -40], "size": [460, 470],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## A pose: %s, %s\n\n"
        "Run this in the **local ComfyUI**.\n\n"
        "1. The two **Load Image** boxes should already show `%s` (the room) and `%s` (the person on grey). "
        "If one shows an error, click **choose file to upload** and pick it from `JJK Game images/ui2`.\n"
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
        % (row["who"].capitalize(), "asleep" if state_of(row) == "asleep" else row.get("doing", ""), bg_name, ref_name, CANDIDATES, CANDIDATES * COST)]})

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
        w[0], w[2], w[3], w[4], w[5], w[6] = prompt, seed + k, "fixed", "16:9", "2K", "IMAGE"
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


def prepare(row, lay, manifest, root=None, keep_dir=None, record=None):
    """Every check a row must pass, then (prompt, the picture it is painted on). Raises Refused."""
    check_place(lay, row)
    check_words(row, record)
    bg = order_check(lay, manifest, row, root)
    scale = None
    if state_of(row) != "asleep":
        scale, _where = scale_for(lay, row, root, keep_dir)
    return prompt_for(row, scale), bg


def make(row, lay, manifest, out_dir=None, root=None, keep_dir=None, record=None, show=False):
    out_dir = out_dir or OUT
    prompt, bg = prepare(row, lay, manifest, root, keep_dir, record)
    name = row_stem(row)
    if show:
        print("%s\n%s\npicture 1: the room  <- %s\npicture 2: the person on grey  <- %s_neutral.png\n"
              % (name, prompt, bg, row["who"]))
        return None
    os.makedirs(out_dir, exist_ok=True)
    bg_name = "pose_room_" + os.path.basename(bg)
    ref_name = "pose_ref_%s.png" % row["who"]
    shutil.copy(bg, os.path.join(out_dir, bg_name))
    write_ref(row["who"], os.path.join(out_dir, ref_name), root)
    if os.path.abspath(out_dir) == os.path.abspath(OUT) and os.path.isdir(COMFY_INPUT):
        shutil.copy(os.path.join(out_dir, bg_name), os.path.join(COMFY_INPUT, bg_name))
        shutil.copy(os.path.join(out_dir, ref_name), os.path.join(COMFY_INPUT, ref_name))
    out = os.path.join(out_dir, name + ".json")
    json.dump(build(row, bg_name, ref_name, prompt), open(out, "w"), indent=1)
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

    def flag(name):
        if name in argv:
            argv.remove(name)
            return True
        return False

    out_dir, batch, root, keep_dir = opt("--out"), opt("--batch"), opt("--root"), opt("--keep")
    manifest_path, record_path = opt("--manifest"), opt("--record")
    dump_path = game_layout.pop_dump_arg(argv)
    show, asleep = flag("--print"), flag("--asleep")
    plan = opt("--plan")
    if plan:                    # a test table in place of POSES (tools/test_art_tools.sh)
        global POSES
        POSES = json.load(open(plan, encoding="utf-8"))
    if "--list" in argv:
        for k, row in enumerate(POSES):
            print("%2d  batch %-2s  %-46s %s%s" % (k + 1, row["batch"], row_stem(row), row.get("doing", ""),
                                                 "  (via %s)" % row["via"] if row.get("via") else ""))
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
        ## <place> <who> [variant], as the plan writes it; the two the other
        ## way round are understood too.
        place, who = args[0], args[1]
        variant = args[2] if len(args) == 3 else ""
        state = "asleep" if asleep else "awake"
        row = find(who, place, variant, state) or find(place, who, variant, state)
        if row is None:
            raise SystemExit("%s is not in the plan (POSES): add a row saying where in the room and doing "
                             "what, or see --list" % stem(place, who, variant, state))
        rows = [row]
    else:
        print(__doc__); raise SystemExit(1)
    lay = game_layout.load(dump_path, root)
    manifest = check_campus.load_manifest(root, manifest_path)
    record = check_campus.load_record(record_path) if record_path else check_prompts.load_record()
    # Nothing at all is written when any row of a batch is refused.
    try:
        for row in rows:
            prepare(row, lay, manifest, root, keep_dir, record)
    except Refused as e:
        raise SystemExit(str(e))
    for row in rows:
        make(row, lay, manifest, out_dir, root, keep_dir, record, show)


if __name__ == "__main__":
    main(sys.argv[1:])
