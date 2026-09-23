"""
Finish a figure that a render cut off at the top or bottom edge, on the base
picture, before any expressions are made from it.

    python3 tools/fix_edges.py --prepare nobara         # close-ups of each cut edge + edges.json
    python3 tools/fix_edges.py nobara bottom <edit.png>  # patch the finished shoes in
    python3 tools/fix_edges.py nobara top <edit.png>     # patch the finished top of the hair in
    python3 tools/fix_edges.py nobara --install          # key the repaired base into the game

Krea-2 Turbo fills the frame whatever the prompt says, so a base render often
has the crown of the hair or a sole sliced off by the edge. `--prepare` pads
each cut edge with a strip of backdrop green, cuts a 16:9 close-up there, and
writes edges.json. In it, Nano Banana Pro draws the missing hair or shoe into
the strip.

Each patch lines the edit up with the close-up on the parts it must not move:
the face and shoulders for the top, the legs for the bottom. It takes only the
cut part and the new strip, and writes it into the working base,
`JJK Game images/fixed/<character>_base.png`, which the expression tools then
start from. tools/fix_feet.py did the same for Yuji's and Megumi's finished
expression sets, bottom edge only.
"""
import sys, os, json, copy, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, crop, resample
from pngread import load
from composite_face import rgb, score, sample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
FIXED = os.path.join(IMAGES, "fixed")
PAD = 64                       # rows of backdrop added beyond a cut edge
CLOSE_W, CLOSE_H = 768, 432    # 16:9, so the edit comes back the same shape
VERSIONS = 2
COST = 0.16
SCALES = [0.98 + 0.005 * i for i in range(9)]      # 0.98 .. 1.02
SHIFT = 10

# The chosen base render for each character.
BASES = {
    "nobara": "nobara_named_base_00001_.png",
    "gojo": "gojo_base_00001_.png",
}

WHAT = {
    "top": ("the top of the hair is sliced off by the top edge, and a strip of plain green was "
            "added above it. Draw the missing top of the hair into the green strip so the hair is "
            "whole, continuing its existing shape naturally (a smooth crown stays smooth, spikes "
            "end in points), in exactly the same drawing style, line weight, colour and highlights "
            "as the rest of the hair. Keep everything else exactly the same: the face, the rest of "
            "the hair, the clothes, the framing, and the plain flat green background, with plain "
            "green left above the hair."),
    "bottom": ("the sole of the shoe on the %s is sliced off by the bottom edge, and a strip of plain "
               "green was added below it. Draw the missing bottom of that shoe into the green strip so "
               "both shoes are complete, with whole soles standing flat on the same level, in exactly "
               "the same drawing style, line weight and colours as the rest of the shoe. Keep "
               "everything else exactly the same: the legs, the other shoe, the framing, and the plain "
               "flat green background, with plain green left below the soles."),
}
CLOSE_SUBJECT = {"top": "the head and shoulders", "bottom": "the lower legs and shoes"}


def backdrop(im, rows):
    """Median backdrop colour over the given rows (next to the edge being extended)."""
    px = []
    for y in rows:
        for x in range(0, im.w, 2):
            i = (y * im.w + x) * 3
            r, g, b = im.buf[i], im.buf[i + 1], im.buf[i + 2]
            if g - max(r, b) > 20:
                px.append((r, g, b))
    return tuple(sorted(p[k] for p in px)[len(px) // 2] for k in range(3))


def cut_columns(im):
    """{edge: (x0, x1)} for each edge the figure runs into."""
    from keysprite import key_out
    keyed = key_out(im)
    out = {}
    for edge, y in (("top", 0), ("bottom", im.h - 1)):
        cols = [x for x in range(im.w) if keyed.buf[(y * im.w + x) * 4 + 3] > 128]
        if cols:
            out[edge] = (min(cols), max(cols))
    return out


def pad(im, top, bottom):
    """The render with `top` and `bottom` rows of backdrop added, each strip in
    the backdrop colour next to it."""
    out = Img(im.w, im.h + top + bottom, alpha=False)
    if top:
        c = backdrop(im, range(0, 24))
        out.buf[:top * im.w * 3] = bytes(c) * (top * im.w)
    out.buf[top * im.w * 3:(top + im.h) * im.w * 3] = im.buf
    if bottom:
        c = backdrop(im, range(im.h - 24, im.h))
        out.buf[(top + im.h) * im.w * 3:] = bytes(c) * (bottom * im.w)
    return out


def record_path(char):
    return os.path.join(IMAGES, "masks", "%s_edges.txt" % char)


def read_record(char):
    src, top, bottom = open(record_path(char)).read().split("\t")
    return src, int(top), int(bottom)


def close_rows(edge, h):
    return (0, CLOSE_H) if edge == "top" else (h - CLOSE_H, h)


def prepare(chars):
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

    rows = []
    os.makedirs(FIXED, exist_ok=True)
    for char in chars:
        src = rgb(load(os.path.join(IMAGES, BASES[char])))
        cuts = cut_columns(src)
        if not cuts:
            print("%s: nothing touches the top or bottom edge" % char)
            continue
        top, bottom = (PAD if "top" in cuts else 0), (PAD if "bottom" in cuts else 0)
        work = pad(src, top, bottom)
        work.save(os.path.join(FIXED, "%s_base.png" % char))
        with open(record_path(char), "w") as f:
            f.write("%s\t%d\t%d" % (BASES[char], top, bottom))
        for edge, (x0, x1) in sorted(cuts.items()):
            r0, r1 = close_rows(edge, work.h)
            close = crop(work, 0, r0, CLOSE_W, r1)
            staged = "edge_%s_%s.png" % (char, edge)
            close.save(os.path.join(COMFY_INPUT, staged))
            close.save(os.path.join(FIXED, staged))
            side = "right" if (x0 + x1) / 2.0 > src.w / 2.0 else "left"
            what = WHAT[edge] % side if "%s" in WHAT[edge] else WHAT[edge]
            prompt = ("This is a close-up of %s of a cartoon character, drawn on a plain flat green "
                      "background. The original picture was cut off at the %s, so %s"
                      % (CLOSE_SUBJECT[edge], edge, what))
            rows.append((char, edge, staged, prompt))
            print("%-7s %-6s cut at x %d-%d; close-up rows %d-%d -> %s" % (char, edge, x0, x1, r0, r1, staged))

    count = len(rows) * VERSIONS
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-900, -520], "size": [600, 400],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Finish what the render cut off: %s\n\n"
        "Run this in the **local ComfyUI** and press **Run**. Each row is a close-up of "
        "a cut edge with a strip of green added; the model draws the missing hair or "
        "shoe into it. %d versions each.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro).\n\n"
        "No need to save anything. Claude picks the results up from ComfyUI's output folder.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press "
        "**Run** again: finished pictures are reused, not paid for twice."
        % (", ".join(chars), VERSIONS, count, count * COST)]})
    gem = P["GeminiImage2Node"]["widgets_values"]
    row_h = 560
    for r, (char, edge, staged, prompt) in enumerate(rows):
        y = r * row_h
        ld = add("LoadImage", (-900, y), (300, 320), title="%s: %s" % (char, edge), widgets=[staged, "image"])
        for k in range(VERSIONS):
            w = list(gem)
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt, 900 + r * 10 + k, "fixed", "16:9", "1K", "IMAGE"
            n = add("GeminiImage2Node", (k * 820, y), (400, 360), title="%s %s (%d)" % (char, edge, k + 1),
                    widgets=w)
            wire(ld, n, "images")
            s = add("SaveImage", (k * 820 + 420, y), (380, 360), widgets=["edge_%s_%s" % (char, edge)])
            wire(n, s, "images")
        groups.append(("%s: %s EDGE" % (char.upper(), edge.upper()), y))

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-920, gy - 50, 2560, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, gy) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [980, 560]}
    out = os.path.join(IMAGES, "edges.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("workflow -> %s  (%d pictures, about $%.2f)" % (out, count, count * COST))


def align(close, ed, rows):
    """Best scale and shift of the edit onto the close-up, judged on the given
    rows of the figure (the parts the edit must not move)."""
    pts = []
    for y in rows:
        for x in range(0, close.w, 3):
            i = (y * close.w + x) * 3
            r, g, b = close.buf[i], close.buf[i + 1], close.buf[i + 2]
            if g - max(r, b) > 20:                 # backdrop: matches anywhere
                continue
            pts.append((x, y))
    if len(pts) < 300:
        raise SystemExit("not enough of the figure in the close-up to line the pictures up")
    c = (close.w / 2.0, close.h / 2.0)
    coarse = pts[::3]
    best = (score(close, ed, coarse, c, 1.0, 0, 0), 1.0, 0, 0)
    for s in SCALES:
        for dy in range(-SHIFT, SHIFT + 1, 2):
            for dx in range(-SHIFT, SHIFT + 1, 2):
                e = score(close, ed, coarse, c, s, dx, dy)
                if e < best[0]:
                    best = (e, s, dx, dy)
    _, s0, dx0, dy0 = best
    best = (score(close, ed, pts, c, s0, dx0, dy0), s0, dx0, dy0)
    for s in (s0 - 0.0025, s0, s0 + 0.0025):
        for dy in range(dy0 - 2, dy0 + 3):
            for dx in range(dx0 - 2, dx0 + 3):
                e = score(close, ed, pts, c, s, dx, dy)
                if e < best[0]:
                    best = (e, s, dx, dy)
    return best, score(close, ed, pts, c, 1.0, 0, 0), c


def apply(char, edge, edited):
    srcname, top, bottom = read_record(char)
    src = rgb(load(os.path.join(IMAGES, srcname)))
    cuts = cut_columns(src)
    if edge not in cuts:
        raise SystemExit("%s: the %s edge isn't cut" % (char, edge))
    pristine = pad(src, top, bottom)
    work_path = os.path.join(FIXED, "%s_base.png" % char)
    work = rgb(load(work_path))
    assert (work.w, work.h) == (pristine.w, pristine.h), "run --prepare again"
    r0, r1 = close_rows(edge, pristine.h)
    close = crop(pristine, 0, r0, CLOSE_W, r1)

    raw = rgb(load(os.path.expanduser(edited)))
    ed = rgb(resample(raw, CLOSE_W, CLOSE_H))
    # The cut, in close-up rows, and the rows to line up on: well away from it.
    if edge == "top":
        cut = top
        ref_rows = range(min(CLOSE_H - 40, cut + 110), CLOSE_H, 3)
    else:
        cut = top + src.h - 1 - r0
        ref_rows = range(0, max(40, cut - 110), 3)
    (err, s, dx, dy), before, c = align(close, ed, ref_rows)
    print("%s %s: lined up at scale %.4f, shift (%d, %d); mismatch %.1f -> %.1f"
          % (char, edge, s, dx, dy, before, err))
    if err > 12:
        raise SystemExit("the edit moved the figure too much to trust (mismatch %.1f)" % err)

    # The patch, in working-image rows: from the new strip across the cut and
    # a little into the figure, over the cut columns, feathered on the sides
    # and on the edge that faces into the figure.
    FEATHER, INTO, SIDE = 20, 60, 30
    x0, x1 = cuts[edge]
    px0, px1 = max(0, x0 - SIDE), min(src.w - 1, x1 + SIDE)
    if edge == "top":
        ys = range(0, top + INTO + 1)
        inner = lambda y: (top + INTO - y) / float(FEATHER)
    else:
        first = top + src.h - 1 - INTO
        ys = range(first, pristine.h)
        inner = lambda y: (y - first) / float(FEATHER)
    kx, ky = raw.w / float(CLOSE_W), raw.h / float(CLOSE_H)
    cx, cy = c
    patch = {}
    for y in ys:
        wy = min(1.0, inner(y))
        for x in range(px0, px1 + 1):
            wx = min(1.0, (x - px0) / float(FEATHER), (px1 - x) / float(FEATHER))
            a = max(0.0, min(wy, wx))
            if a <= 0:
                continue
            ex = cx + (x - cx) * s + dx
            ey = cy + (y - r0 - cy) * s + dy
            patch[(x, y)] = (a, sample(raw, (ex + 0.5) * kx - 0.5, (ey + 0.5) * ky - 0.5))

    # Match the edit's colour to the render where they overlap on the figure.
    shift = [0.0, 0.0, 0.0]
    fig = []
    for (x, y), (a, v) in patch.items():
        if a >= 1.0:
            continue
        i = (y * pristine.w + x) * 3
        if pristine.buf[i + 1] - max(pristine.buf[i], pristine.buf[i + 2]) <= 20:
            fig.append((i, v))
    if len(fig) > 40:
        for k in range(3):
            d = sorted(pristine.buf[i + k] - v[k] for i, v in fig)
            shift[k] = max(-20.0, min(20.0, d[len(d) // 2]))
    print("   colour shift %s over %d edge pixels" % ([round(v, 1) for v in shift], len(fig)))

    for (x, y), (a, v) in patch.items():
        i = (y * work.w + x) * 3
        for k in range(3):
            work.buf[i + k] = max(0, min(255, int(work.buf[i + k] * (1 - a) + (v[k] + shift[k]) * a + 0.5)))
    work.save(work_path)
    print("   %s edge repaired -> %s" % (edge, work_path))


def install(char):
    from keysprite import install as key_install
    path = os.path.join(FIXED, "%s_base.png" % char)
    problems = key_install(path, "%s_neutral" % char)
    print("installed %s_neutral from %s" % (char, path))
    for p in problems:
        print("   !! " + p)
    return problems


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--prepare":
        prepare(args[1:])
    elif len(args) == 2 and args[1] == "--install":
        install(args[0])
    elif len(args) == 3 and args[1] in ("top", "bottom"):
        apply(args[0], args[1], args[2])
    else:
        print(__doc__); raise SystemExit(1)
