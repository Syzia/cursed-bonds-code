"""
Build the ComfyUI workflow that generates location backgrounds.

    python3 tools/make_bg_workflow.py classroom your_room

One row per location, two candidates each. Seeds are fixed so a run that
stops on a rate-limit error can simply be run again; pass --seed N for
different pictures of the same places. Writes `backgrounds.json` into
~/Desktop/JJK Game images; drag it into the LOCAL ComfyUI and press Run. The
results land in ~/ComfyUI-Shared/output as `bg_<name>_0000N_.png`, where
tools/install_bg.py can take them straight into the game.

The settings are the ones the style and blend tests settled on (see
tools/bgs/STYLE.md): Krea 2 Medium at 16:9, the scene description from
tools/bgs/prompts/<name>.txt plus a shared style paragraph, steered by crops of
the anime at strength 0.50. Outdoor locations use style.txt and four exterior
crops; rooms (INTERIORS) use style_interior.txt and interior crops; a few places
add a reference or a lighting paragraph of their own (LOCATION_REFS,
LOCATION_STYLE). Krea 2 is a paid partner node, about $0.035 a picture; nothing
runs on this Mac's GPU. Where each place is and what it looks out on:
tools/bgs/CAMPUS.md.
"""
import sys, os, json, copy, uuid, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
REFS = os.path.join(IMAGES, "references", "style_refs")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")

STYLE_REFS = ["style_ref_3_bridge.png", "style_ref_4_pagodas.png",
              "style_ref_5_hall_front.png", "style_ref_6_campus_aerial.png"]

# Rooms get their own style paragraph and references. The first classroom and
# bedroom came back half outdoors -- a missing wall onto a dirt yard, an
# open-air veranda -- because the shared style asked for sky, distant mist and
# open ground, and every reference was an exterior shot.
# Names are the game's image names (game/images/bg/<name>.png), so a render
# saved as bg_<name> installs straight into the right slot.
INTERIORS = {"classroom", "cafeteria", "training", "dojo", "dorm_common",
             "your_room", "your_room_night", "girls_dorm", "infirmary",
             "office", "storehouse"}
INTERIOR_REFS = ["style_ref_7_room_interior.png", "style_ref_5_hall_front.png"]

# The wild places get the anime's nature shots instead of its buildings, so no
# temple roofs creep into the forest.
NATURE_REFS = ["style_ref_10_mossy_stream.png", "style_ref_9_gate_approach.png",
               "style_ref_3_bridge.png", "style_ref_11_mountain_sky.png"]

# A few places have references of their own. Here copying a reference's
# framing is the point, where for the shared sets it is a leak: the gate is
# the anime's torii approach, the rooftop the view down from the veranda, and
# the office Yaga's candlelit hall. Four or fewer each, so the one that
# matters isn't diluted; Krea takes up to 10.
LOCATION_REFS = {
    "gate": ["style_ref_9_gate_approach.png", "style_ref_10_mossy_stream.png",
             "style_ref_5_hall_front.png", "style_ref_3_bridge.png"],
    "rooftop": ["style_ref_1_veranda_view.png", "style_ref_6_campus_aerial.png",
                "style_ref_4_pagodas.png", "style_ref_11_mountain_sky.png"],
    "office": ["style_ref_8_hall_interior.png", "style_ref_7_room_interior.png"],
    "forest": NATURE_REFS, "riverside": NATURE_REFS, "ridge": NATURE_REFS,
}
# Rooms lit by lamps or candles instead of daylight through windows.
LOCATION_STYLE = {"office": "style_dim.txt", "storehouse": "style_dim.txt"}
STRENGTH = 0.50
assert 0 < STRENGTH <= 1.0, "Krea's API rejects style-reference strength above 1.0"
CANDIDATES = 2
COST = 0.035


def refs_for(name):
    return LOCATION_REFS.get(name) or (INTERIOR_REFS if name in INTERIORS else STYLE_REFS)


def bg_prompt(name):
    """A location's scene description followed by the shared style paragraph.

    Kept in separate files so the style can be tuned once for every location.
    """
    scene = open(os.path.join(ROOT, "tools", "bgs", "prompts", name + ".txt")).read().strip()
    kind = LOCATION_STYLE.get(name) or ("style_interior.txt" if name in INTERIORS else "style.txt")
    style = open(os.path.join(ROOT, "tools", "bgs", kind)).read().strip()
    return scene + "\n\n" + style


def build(names, seed=1000):
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

    for f in set(sum((refs_for(n) for n in names), [])):
        shutil.copy(os.path.join(REFS, f), os.path.join(COMFY_INPUT, f))
    count = len(names) * CANDIDATES
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-1260, -520], "size": [620, 400],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Backgrounds: %s\n\n"
        "Run this in the **local ComfyUI**. Press **Run**: each row makes %d "
        "versions of one location.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Krea 2, charged to your Comfy account).\n\n"
        "No need to save anything. The results go to ComfyUI's output folder "
        "and Claude picks them up from there.\n\n"
        "**If it stops with a rate-limit or \"high demand\" error**, wait a "
        "minute and press **Run** again. ComfyUI sends every picture to Krea at "
        "once, and Krea sometimes turns some away. Pictures that already finished "
        "are reused rather than made again (and aren't charged twice), as long as "
        "ComfyUI hasn't been restarted in between.\n\n"
        "**Please don't change the reference boxes.** The pictures are cleaned "
        "crops with no characters, subtitles or player bar, which the model would "
        "copy. Krea also rejects any strength above 1.0, even though the box "
        "allows 2.0."
        % (", ".join(names), CANDIDATES, count, count * COST)]})

    # One chain of style references per kind of scene; each row uses its own.
    def make_chain(refs, x, label):
        chain = None
        for i, f in enumerate(refs):
            ld = add("LoadImage", (x, i * 330), (300, 310), title="%s reference %d" % (label, i + 1),
                     widgets=[f, "image"])
            ref = add("Krea2StyleReferenceNode", (x + 340, i * 330 + 100), (240, 80),
                      title="%s %d at %.2f" % (label, i + 1, STRENGTH), widgets=[STRENGTH])
            wire(ld, ref, "image")
            if chain is not None:
                wire(chain, ref, "style_reference")
            chain = ref
        return chain
    # One column per distinct set, laid out leftwards from the rows.
    chains = {}
    for n in names:
        key = tuple(refs_for(n))
        if key in chains:
            continue
        label = {tuple(STYLE_REFS): "Outdoor", tuple(INTERIOR_REFS): "Indoor",
                 tuple(NATURE_REFS): "Nature"}.get(key) or n.replace("_", " ").capitalize()
        chains[key] = make_chain(list(key), -1260 - 700 * len(chains), label)

    row_h = 560
    for r, name in enumerate(names):
        y = r * row_h
        text = bg_prompt(name)
        for k in range(CANDIDATES):
            # Fixed seeds, so a re-run hits ComfyUI's cache for every picture
            # that already finished; see the note in the "Start here" box.
            n = add("Krea2ImageNode", (k * 820, y), (400, 360), title="%s (%d)" % (name, k + 1),
                    widgets=[text, "Krea 2 Medium", "16:9", "1K", "medium", "", 0.35,
                             seed + r * 10 + k, "fixed"])
            wire(chains[tuple(refs_for(name))], n, "model.style_reference")
            s = add("SaveImage", (k * 820 + 420, y), (380, 360), widgets=["bg_%s" % name])
            wire(n, s, "images")
        groups.append((name.replace("_", " ").upper(), y))

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-20, gy - 50, 1660, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, gy) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.4, "offset": [1340, 580]}
    return wf, count


if __name__ == "__main__":
    argv = sys.argv[1:]
    seed = 1000
    if "--seed" in argv:
        i = argv.index("--seed")
        seed = int(argv[i + 1])
        del argv[i:i + 2]
    names = [a for a in argv if not a.startswith("--")]
    if not names:
        print(__doc__); raise SystemExit(1)
    for n in names:
        if not os.path.exists(os.path.join(ROOT, "tools", "bgs", "prompts", n + ".txt")):
            raise SystemExit("no prompt for %r in tools/bgs/prompts/" % n)
    wf, count = build(names, seed)
    out = os.path.join(IMAGES, "backgrounds.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("rows      %s (%d each)" % (", ".join(names), CANDIDATES))
    print("cost      %d pictures, about $%.2f" % (count, count * COST))
    print("workflow -> %s" % out)
