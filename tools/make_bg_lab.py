"""
Build a style test: one location painted by several approaches, side by side.

    python3 tools/make_bg_lab.py courtyard

Writes `bg_style_test.json` into ~/Desktop/JJK Game images. It runs in the local
ComfyUI (every approach is a paid partner node, so nothing runs on this Mac's
GPU) and the results land in ~/ComfyUI-Shared/output, where they can be read
directly. Each approach makes two versions, so a comparison is between
approaches rather than between one lucky roll and one unlucky one:

  A  Krea 2 Medium, from words alone                      ~$0.030 each
  B  Krea 2 Medium, steered by the reference screenshots   ~$0.035 each
  C  Nano Banana Pro, shown the reference screenshots      ~$0.16  each

The reference frames are tools-prepared crops of the user's anime screenshots
(subtitles, player bar and people removed) in references/style_refs/, copied
into ComfyUI's input folder.
"""
import sys, os, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_bg_workflow import bg_prompt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
REFS = os.path.join(IMAGES, "references", "style_refs")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
PER_APPROACH = 2
COST = {"A": 0.03, "B": 0.035, "C": 0.16}


def nano_prompt(name):
    scene = open(os.path.join(ROOT, "tools", "bgs", "prompts", name + ".txt")).read().strip()
    return (
        "Paint a brand-new anime background in exactly the same art style as these reference "
        "frames: the same soft painted look, diffused light, haze, brushwork and colour palette. "
        "Do not copy any of the reference pictures. The scene: " + scene.replace("\n", " ") +
        ". Framing: a 16:9 wide shot from a normal lens at standing eye level, level horizon, flat "
        "open ground across the lower third where people could stand. No people, no characters, "
        "no text, no subtitles, no user interface.")


def build(name):
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

    refs = sorted(f for f in os.listdir(REFS) if f.startswith("style_ref_") and f.endswith(".png"))
    if len(refs) < 3:
        raise SystemExit("need at least three style references in %s" % REFS)
    for f in refs:
        shutil.copy(os.path.join(REFS, f), os.path.join(COMFY_INPUT, f))

    total = PER_APPROACH * sum(COST.values())
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-900, -520], "size": [620, 460],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Style test: %s\n\n"
        "Press **Run**. Three rows, three ways of painting the same place, two "
        "versions each:\n\n"
        "- **A**: Krea 2, from words alone\n"
        "- **B**: Krea 2, steered by your anime screenshots\n"
        "- **C**: Nano Banana Pro, shown your anime screenshots\n\n"
        "**Cost:** 6 pictures, about **$%.2f** in total.\n\n"
        "No need to save anything. The results go to ComfyUI's output folder "
        "and Claude reads them from there." % (name, total)]})

    loads = []
    for i, f in enumerate(refs):
        loads.append(add("LoadImage", (-900, i * 330), (300, 310), title="Reference %d" % (i + 1),
                         widgets=[f, "image"]))

    krea_text = bg_prompt(name)
    row_h, x0 = 560, 0

    # Row A: Krea 2, words only
    for k in range(PER_APPROACH):
        n = add("Krea2ImageNode", (x0 + k * 820, 0), (400, 360), title="A: Krea 2, words only",
                widgets=[krea_text, "Krea 2 Medium", "16:9", "1K", "medium", "", 0.35, 101 + k, "randomize"])
        s = add("SaveImage", (x0 + k * 820 + 420, 0), (380, 360), widgets=["bglab_%s_A" % name])
        wire(n, s, "images")
    groups.append(("A  KREA 2, WORDS ONLY", 0))

    # Row B: Krea 2 with a chain of style references
    chain = None
    for i, ld in enumerate(loads):
        ref = add("Krea2StyleReferenceNode", (-560, row_h + i * 110), (240, 80),
                  title="Style reference %d" % (i + 1), widgets=[0.9])
        wire(ld, ref, "image")
        if chain is not None:
            wire(chain, ref, "style_reference")
        chain = ref
    for k in range(PER_APPROACH):
        n = add("Krea2ImageNode", (x0 + k * 820, row_h), (400, 360), title="B: Krea 2 + your screenshots",
                widgets=[krea_text, "Krea 2 Medium", "16:9", "1K", "medium", "", 0.35, 201 + k, "randomize"])
        wire(chain, n, "model.style_reference")
        s = add("SaveImage", (x0 + k * 820 + 420, row_h), (380, 360), widgets=["bglab_%s_B" % name])
        wire(n, s, "images")
    groups.append(("B  KREA 2 + YOUR SCREENSHOTS", row_h))

    # Row C: Nano Banana Pro shown three of the references
    batch = add("BatchImagesNode", (-560, 2 * row_h), (240, 120), title="Three references")
    for i, ld in enumerate(loads[:3]):
        wire(ld, batch, "images.image%d" % i)
    gem = P["GeminiImage2Node"]["widgets_values"]
    for k in range(PER_APPROACH):
        w = list(gem)
        w[0], w[2], w[4], w[5], w[6] = nano_prompt(name), 301 + k, "16:9", "1K", "IMAGE"
        n = add("GeminiImage2Node", (x0 + k * 820, 2 * row_h), (400, 360),
                title="C: Nano Banana Pro + your screenshots", widgets=w)
        wire(batch, n, "images")
        s = add("SaveImage", (x0 + k * 820 + 420, 2 * row_h), (380, 360), widgets=["bglab_%s_C" % name])
        wire(n, s, "images")
    groups.append(("C  NANO BANANA PRO + YOUR SCREENSHOTS", 2 * row_h))

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-20, y - 50, 1660, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, y) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.42, "offset": [980, 580]}
    return wf, total


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); raise SystemExit(1)
    wf, total = build(args[0])
    out = os.path.join(IMAGES, "bg_style_test.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("style test for %s: 3 approaches x %d, about $%.2f" % (args[0], PER_APPROACH, total))
    print("workflow -> %s" % out)
