"""
Finish shoes that a render cut off at the bottom edge.

    python3 tools/fix_feet.py --prepare yuji megumi     # close-ups + feet.json
    python3 tools/fix_feet.py yuji <edited.png>         # patch it in, re-install all six

A figure whose sole touches the bottom of the frame ends in a flat-cut shoe
in the game, and keysprite can't tell how tall the figure really is.
`--prepare` adds a strip of backdrop green below the base render, cuts a 16:9
close-up of the lower legs and feet, with enough trouser above the shoes to
line things up afterwards, and writes feet.json. There, Nano Banana Pro
finishes the shoes in the new strip.

The second form lines the edit up with the close-up on the trousers, which
the edit must not move. It takes only the clipped foot and the new strip
below it, and pastes that into every expression of the character. Their feet
are pixel-identical, so one repair serves all six. It then re-installs the
sprites and side portraits through keysprite. The patched renders are kept
in `JJK Game images/feetfixed/`.
"""
import sys, os, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img, crop, resample
from pngread import load
from composite_face import rgb, score, sample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
OUT = os.path.join(IMAGES, "feetfixed")
PAD = 64                       # rows of backdrop added below the render
CLOSE_W, CLOSE_H = 768, 432    # 16:9, so the edit comes back the same shape
VERSIONS = 2
COST = 0.16
SCALES = [0.98 + 0.005 * i for i in range(9)]      # 0.98 .. 1.02
SHIFT = 10

# Every picture a character's sprites come from, the base first.
SOURCES = {
    "yuji": [("neutral", "Krea2_turbo_00001_.png")] +
            [(e, "yuji_%s_00001_.png" % e) for e in ("happy", "serious", "sad", "angry", "surprised")],
    "megumi": [("neutral", "megumi_head_a_00001_.png"),
               ("happy", "round2/megumi/megumi_happy_00001_.png")] +
              [(e, "composited/megumi_%s.png" % e) for e in ("serious", "sad", "angry", "surprised")],
}


def backdrop(im):
    """Median backdrop colour just above the bottom edge, where the added
    strip meets the render. (Carrying each column's own tone down instead
    streaks, and stretches the shoes' soft shadow into dark blocks.)"""
    px = []
    for y in range(im.h - 24, im.h):
        for x in range(0, im.w, 2):
            i = (y * im.w + x) * 3
            r, g, b = im.buf[i], im.buf[i + 1], im.buf[i + 2]
            if g - max(r, b) > 20:
                px.append((r, g, b))
    return tuple(sorted(p[k] for p in px)[len(px) // 2] for k in range(3))


def padded(im, green):
    out = Img(im.w, im.h + PAD, alpha=False, fill=green)
    out.buf[:len(im.buf)] = im.buf
    return out


def clipped_columns(base):
    """Columns where the figure runs into the bottom edge."""
    from keysprite import key_out
    keyed = key_out(base)
    y = base.h - 1
    cols = [x for x in range(base.w) if keyed.buf[(y * base.w + x) * 4 + 3] > 128]
    return (min(cols), max(cols)) if cols else None


def crop_record(char):
    return os.path.join(IMAGES, "masks", "%s_feet_crop.txt" % char)


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

    count = len(chars) * VERSIONS
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-900, -520], "size": [600, 400],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Finish the cut-off shoes: %s\n\n"
        "Run this in the **local ComfyUI** and press **Run**. Each row is a close-up "
        "of the feet with a strip of green added below; the model draws the rest of "
        "the shoe that the render cut off. %d versions each.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro).\n\n"
        "No need to save anything. Claude picks the results up from ComfyUI's output folder.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press "
        "**Run** again: finished pictures are reused, not paid for twice."
        % (", ".join(chars), VERSIONS, count, count * COST)]})

    gem = P["GeminiImage2Node"]["widgets_values"]
    row_h = 560
    for r, char in enumerate(chars):
        base = rgb(load(os.path.join(IMAGES, SOURCES[char][0][1])))
        cols = clipped_columns(base)
        if not cols:
            print("%s: nothing touches the bottom edge, skipping" % char)
            continue
        side = "right" if (cols[0] + cols[1]) / 2.0 > base.w / 2.0 else "left"
        pad = padded(base, backdrop(base))
        y0 = pad.h - CLOSE_H
        close = crop(pad, 0, y0, CLOSE_W, pad.h)
        close.save(os.path.join(IMAGES, "%s_feet_in.png" % char))
        staged = "feet_%s.png" % char
        close.save(os.path.join(COMFY_INPUT, staged))
        with open(crop_record(char), "w") as f:
            f.write("%d %d\n" % (y0, PAD))
        print("%-7s clipped foot at x %d-%d (%s); close-up rows %d-%d -> %s"
              % (char, cols[0], cols[1], side, y0, pad.h, staged))

        prompt = ("This is a close-up of the lower legs and shoes of a cartoon character, drawn on a "
                  "plain flat green background. The original picture was cut off at the bottom, so the "
                  "sole of the shoe on the %s is sliced off, and a strip of plain green was added below "
                  "it. Draw the missing bottom of that shoe into the green strip so both shoes are "
                  "complete, with whole soles standing flat on the same level, in exactly the same "
                  "drawing style, line weight and colours as the rest of the shoe. Keep everything else "
                  "exactly the same: the trousers, the other shoe, the framing, and the plain flat "
                  "green background, with plain green left below the soles." % side)
        y = r * row_h
        ld = add("LoadImage", (-900, y), (300, 320), title="Feet: %s" % char, widgets=[staged, "image"])
        for k in range(VERSIONS):
            w = list(gem)
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt, 700 + r * 10 + k, "fixed", "16:9", "1K", "IMAGE"
            n = add("GeminiImage2Node", (k * 820, y), (400, 360), title="%s feet (%d)" % (char, k + 1),
                    widgets=w)
            wire(ld, n, "images")
            s = add("SaveImage", (k * 820 + 420, y), (380, 360), widgets=["feet_%s" % char])
            wire(n, s, "images")
        groups.append(("%s: SHOES" % char.upper(), y))

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-920, gy - 50, 2560, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, gy) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [980, 560]}
    out = os.path.join(IMAGES, "feet.json")
    json.dump(wf, open(out, "w"), indent=1)
    print("workflow -> %s  (%d pictures, about $%.2f)" % (out, count, count * COST))


def align(close, ed, cut_row):
    """Best scale and shift of the edit onto the close-up, judged on the trousers."""
    pts = []
    for y in range(0, max(40, cut_row - 110), 3):
        for x in range(0, close.w, 3):
            i = (y * close.w + x) * 3
            r, g, b = close.buf[i], close.buf[i + 1], close.buf[i + 2]
            if g - max(r, b) > 20:                 # backdrop: matches anywhere
                continue
            pts.append((x, y))
    if len(pts) < 300:
        raise SystemExit("not enough trouser in the close-up to line the pictures up")
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


def apply(char, edited):
    from keysprite import install
    src = [(e, rgb(load(os.path.join(IMAGES, f)))) for e, f in SOURCES[char]]
    base = src[0][1]
    green = backdrop(base)
    cols = clipped_columns(base)
    if not cols:
        raise SystemExit("%s: nothing touches the bottom edge" % char)
    y0, pad_rows = [int(v) for v in open(crop_record(char)).read().split()]
    assert pad_rows == PAD, "the close-up was cut with a different PAD; run --prepare again"
    pad = padded(base, green)
    close = crop(pad, 0, y0, CLOSE_W, pad.h)

    raw = rgb(load(os.path.expanduser(edited)))
    ed = rgb(resample(raw, CLOSE_W, CLOSE_H))
    cut_row = base.h - 1 - y0
    (err, s, dx, dy), before, c = align(close, ed, cut_row)
    print("%s: lined up at scale %.4f, shift (%d, %d); trouser mismatch %.1f -> %.1f"
          % (char, s, dx, dy, before, err))
    if err > 12:
        raise SystemExit("the edit moved the trousers too much to trust (mismatch %.1f)" % err)

    # The patch: the clipped foot's columns, from a little above the cut down
    # through the new strip, feathered at the top and sides.
    FEATHER, ABOVE, SIDE = 20, 60, 30
    px0, px1 = max(0, cols[0] - SIDE), min(base.w - 1, cols[1] + SIDE)
    py0 = base.h - 1 - ABOVE
    kx, ky = raw.w / float(CLOSE_W), raw.h / float(CLOSE_H)
    cx, cy = c
    patch = {}
    for y in range(py0, pad.h):
        wy = min(1.0, (y - py0) / float(FEATHER))
        for x in range(px0, px1 + 1):
            wx = min(1.0, (x - px0) / float(FEATHER), (px1 - x) / float(FEATHER))
            a = max(0.0, min(wy, wx))
            if a <= 0:
                continue
            ex = cx + (x - cx) * s + dx
            ey = cy + (y - y0 - cy) * s + dy
            patch[(x, y)] = (a, sample(raw, (ex + 0.5) * kx - 0.5, (ey + 0.5) * ky - 0.5))

    # Match the edit's colour to the base where they overlap on the figure.
    band = [(p, v) for p, (a, v) in patch.items() if a < 1.0 and p[1] < base.h]
    shift = [0.0, 0.0, 0.0]
    fig = []
    for (x, y), v in band:
        i = (y * pad.w + x) * 3
        if pad.buf[i + 1] - max(pad.buf[i], pad.buf[i + 2]) <= 20:
            fig.append((i, v))
    if len(fig) > 40:
        for k in range(3):
            d = sorted(pad.buf[i + k] - v[k] for i, v in fig)
            shift[k] = max(-20.0, min(20.0, d[len(d) // 2]))
    print("   colour shift %s over %d edge pixels" % ([round(v, 1) for v in shift], len(fig)))

    os.makedirs(OUT, exist_ok=True)
    flagged = []
    for expr, im in src:
        out = padded(im, green)
        for (x, y), (a, v) in patch.items():
            i = (y * out.w + x) * 3
            for k in range(3):
                out.buf[i + k] = max(0, min(255, int(out.buf[i + k] * (1 - a) + (v[k] + shift[k]) * a + 0.5)))
        path = os.path.join(OUT, "%s_%s.png" % (char, expr))
        out.save(path)
        problems = install(path, "%s_%s" % (char, expr), quiet=True)
        print("   %-10s -> %s%s" % (expr, path, "" if not problems else "   !! " + "; ".join(problems)))
        if problems:
            flagged.append(expr)
    return flagged


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--prepare" and len(args) > 1:
        bad = [c for c in args[1:] if c not in SOURCES]
        if bad:
            raise SystemExit("no sources listed for %s" % ", ".join(bad))
        prepare(args[1:])
    elif len(args) == 2 and args[0] in SOURCES:
        apply(args[0], args[1])
    else:
        print(__doc__); raise SystemExit(1)
