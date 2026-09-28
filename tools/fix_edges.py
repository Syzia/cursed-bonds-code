"""
Finish a figure that a render cut off at the top or bottom edge, on the base
picture, before any expressions are made from it.

    python3 tools/fix_edges.py --prepare nobara         # close-ups of each cut edge + edges.json
    python3 tools/fix_edges.py nobara bottom <edit.png>  # patch the finished shoes in
    python3 tools/fix_edges.py nobara top <edit.png>     # patch the finished top of the hair in
    python3 tools/fix_edges.py nobara --install          # key the repaired base into the game

Krea-2 Turbo fills the frame whatever the prompt says, so a base render often
has the crown of the hair or a sole sliced off by the edge, and a wide figure
(Panda) can graze the left and right edges too; those get a 9:16 close-up
down the side. `--prepare` pads
each cut edge with a strip of backdrop green, cuts a 16:9 close-up there, and
writes edges.json. In it, Nano Banana Pro draws the missing hair or shoe into
the strip.

Each patch lines the edit up with the close-up on the parts it must not move:
the face and shoulders for the top, the legs for the bottom. It takes only the
cut part and the new strip, and writes it into the working base,
`JJK Game images/fixed/<character>_base.png`, which the expression tools then
start from. tools/fix_feet.py did the same for Yuji's and Megumi's finished
expression sets, bottom edge only.

Two more repairs for a base the model got nearly right:

- **HAIR_SHIFT** recolours the hair when it comes out a few degrees off the
  references. It is applied to the working base before anything else.
- **HEAD_FIX** redraws the face and the top of the hair when the base model
  doesn't know the character well enough. That happened with Shoko, where it
  drew a generic face twice. The fix is a "head" row in the same workflow
  (Nano Banana on a head close-up, which also finishes a cut crown), composited
  back through the head mask:

      python3 tools/fix_edges.py shoko head <edit.png>

- **HAIR_FIX** restyles the hair along its whole length, keeping the face:

      python3 tools/fix_edges.py --prepare-hair shoko    # hair.json
      python3 tools/fix_edges.py shoko hair <edit.png>

- **BODY_FIX** reshapes the body on the full picture and pastes back only
  the body from the collar down, keeping the approved head:

      python3 tools/fix_edges.py --prepare-body yaga     # body.json
      python3 tools/fix_edges.py yaga body <edit.png>

`--prepare` refuses to overwrite a working base that already has repairs
pasted in, unless given --force.
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
SIDE_W, SIDE_H = 432, 768      # 9:16, for a cut down the left or right edge
VERSIONS = 2
COST = 0.16
SCALES = [0.98 + 0.005 * i for i in range(9)]      # 0.98 .. 1.02
SHIFT = 10

# The chosen base render for each character.
BASES = {
    "nobara": "nobara_named_base_00001_.png",
    "gojo": "gojo_base_00001_.png",
    "shoko": "shoko_base_00003_.png",
    "yaga": "yaga_base_00001_.png",
    "maki": "maki_base_00001_.png",
    "panda": "panda_base_00004_.png",
    "toge": "toge_base_00004_.png",
}

HER = {"nobara", "maki", "shoko", "utahime", "sana"}

# Skin graded to the official art: (hue in degrees, saturation, median
# lightness). Yaga is tan in his design sheet, (227, 184, 150), and came out
# pale peach, (240, 203, 177). Applied to all his skin, so the fists match
# the face.
SKIN_TARGET = {"yaga": (26.0, 0.56, 0.74)}

# Rows added below the chin to the head mask, for a beard that may reach
# below the drawn chin.
HEAD_CHIN_EXTRA = {"yaga": 16}

# (hue shift in degrees, saturation factor) for the hair. Shoko's measured
# +3 degrees against the anime's +7 to +18 and the design sheet's +11, and a
# touch more saturated than the anime's 0.22-0.24.
HAIR_SHIFT = {"shoko": (9.0, 0.82)}

# Faces the base model got wrong, redrawn on the head close-up. Described,
# never named: this goes to Google.
HEAD_FIX = {
    "shoko": ("Redraw her face and the top of her hair so she looks like a tired, deadpan doctor in "
              "her late twenties, in exactly the same anime drawing style and colours: her hair "
              "parted exactly in the centre of her head, so that her whole high forehead is bare, "
              "falling straight down both sides of her face; a long, slim oval face with a narrow "
              "chin; narrow, sleepy, half-closed eyes, the upper eyelids lowered halfway over dark "
              "brown irises, with dark upper lash lines; two thin curved lines under each eye like "
              "tired bags, with faint grey shading; a small dark round mole just below her right "
              "eye, which is the eye on the left side of the picture; thin, straight dark brown "
              "eyebrows; a flat, calm, expressionless mouth, closed, with pale pink lips."),
}
HEAD_FIX["yaga"] = (
    "Redraw his face so it matches this description, in exactly the same anime drawing style: "
    "narrow rectangular sunglasses like thin horizontal slits, with thick black frames and dark red "
    "lenses, across his eyes, much narrower and darker than now, with no shine; a bold dark brown "
    "goatee drawn as solid dark shapes with crisp edges, a thick moustache whose ends curve down "
    "around the corners of his mouth to join a short pointed beard on his chin; a heavy square jaw; "
    "deep lines down his cheeks; a stern mouth closed in a firm line. Keep his tan skin colour, his "
    "spiky hair, the shaved sides of his head and his ears exactly as they are.")
HEAD_FIX["toge"] = (
    "Redraw his hair and face so they match this description, in exactly the same anime drawing style: "
    "his hair the same pale silvery ash-blond, almost white, but messy and spiky, with short thick tufts "
    "standing up and out in soft pointed spikes all over his head, a few spiky strands falling over his "
    "forehead, and spiky tufts over the tops of his ears; a slim young man's face with a narrower chin; "
    "calm, slightly sleepy half-lidded violet-grey eyes with heavy upper eyelids; his mouth closed in a "
    "small neutral line; and on each cheek, just beside the corners of his mouth, a small hollow ring "
    "with a thick dark outline, each joined to the corner of his mouth by a short dark line, like the "
    "fangs of a snake, the two sides matching.")
# Room for the redraw to grow: hair that changes shape (spikes) reaches past
# the old outline, so the head mask's dome is wider (a fraction of the head's
# width) and the close-up starts higher above the head (px).
HEAD_MARGIN = {"toge": 0.35}
HEAD_ROOM_ABOVE = {"toge": 80}
# What a head fix must keep, where the hair is meant to change.
HEAD_KEEP_FOR = {
    "toge": ("Keep the hair colour. Keep everything else exactly the same: the framing, the head's size "
             "and position, the ears, the tall collar of his jacket sitting under his chin, the clothes, the "
             "plain flat green background, and the flat cel shading and line art."),
}
HEAD_VERSIONS = 3
HEAD_KEEP = ("Keep {his} hair colour, the outline of {his} hair and all the hair beside and below {his} "
             "face exactly as they are. Keep everything else exactly the same: the framing, the "
             "head's size and position, the clothes, the plain flat green background, and the flat "
             "cel shading and line art.")


def pronoun(char):
    return ("her", "a woman") if char in HER else ("his", "a man")

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
WHAT["side"] = ("the outer edge of the body on the %s side (the arm's outline) is sliced off by the frame "
                "edge, and a strip of plain green was added beside it. Draw the missing outer edge into the "
                "green strip so the outline is complete and curves back in naturally, in exactly the same "
                "drawing style, line weight, colours and fur or cloth texture. Keep everything else exactly "
                "the same: the rest of the body, the framing, and the plain flat green background, with plain "
                "green left beyond the outline.")
CLOSE_SUBJECT = {"top": "the head and shoulders", "bottom": "the lower legs and shoes",
                 "left": "the side of the body and arm", "right": "the side of the body and arm"}


# Hair the base model got wrong, restyled on a close-up covering its whole
# length. Shoko's came out dark and slicked flat; the anime's is a lighter brown
# with highlight streaks, softer, framing her forehead.
HAIR_FIX = {
    "shoko": ("Restyle only her hair: a warm medium brown, clearly lighter than it is now, like milk "
              "chocolate, with long lighter caramel highlight streaks running down the strands; still "
              "parted in the centre with her forehead bare in the middle, but the hair at the front "
              "sweeping away from the part in soft curves that frame her forehead and cover the edges "
              "of her temples, with a few fine loose strands at the temples; the rest of her hair soft "
              "and full, falling straight past her shoulders to mid-chest in slightly separated "
              "strands, a little fuller at the sides than now."),
}
HAIR_VERSIONS = 3

# The colour the restyled hair is graded to: (hue in degrees, saturation,
# median lightness), measured off the character's references. Nano Banana
# gets the style right but overshoots the colour: Shoko's came back +22
# degrees, saturation 0.37, lightness 0.37, against the anime stills' +7 to +18,
# 0.20-0.24 and 0.23-0.31.
HAIR_TARGET = {"shoko": (14.0, 0.24, 0.31)}
HAIR_KEEP = ("Keep {his} face exactly as it is: the same eyes, eyebrows, nose, mouth, expression and any "
             "marks on the skin. Keep everything else exactly the same: the framing, the head's size and "
             "position, the clothes, the plain flat green background, and the flat cel shading and line art.")


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
    """{edge: span} for each edge the figure runs into: (x0, x1) along the top
    or bottom edge, (y0, y1) down the left or right edge."""
    from keysprite import key_out
    keyed = key_out(im)
    out = {}
    for edge, y in (("top", 0), ("bottom", im.h - 1)):
        cols = [x for x in range(im.w) if keyed.buf[(y * im.w + x) * 4 + 3] > 128]
        if cols:
            out[edge] = (min(cols), max(cols))
    for edge, x in (("left", 0), ("right", im.w - 1)):
        rows = [y for y in range(im.h) if keyed.buf[(y * im.w + x) * 4 + 3] > 128]
        if rows:
            out[edge] = (min(rows), max(rows))
    return out


def side_pads(cuts):
    return (PAD if "left" in cuts else 0), (PAD if "right" in cuts else 0)


def side_backdrop(im, cols):
    """Median backdrop colour over the given columns."""
    px = []
    for y in range(0, im.h, 2):
        for x in cols:
            i = (y * im.w + x) * 3
            r, g, b = im.buf[i], im.buf[i + 1], im.buf[i + 2]
            if g - max(r, b) > 20:
                px.append((r, g, b))
    return tuple(sorted(p[k] for p in px)[len(px) // 2] for k in range(3))


def pad(im, top, bottom, left=0, right=0):
    """The render with `top` and `bottom` rows and `left` and `right` columns
    of backdrop added, each strip in the backdrop colour next to it."""
    out = Img(im.w, im.h + top + bottom, alpha=False)
    if top:
        c = backdrop(im, range(0, 24))
        out.buf[:top * im.w * 3] = bytes(c) * (top * im.w)
    out.buf[top * im.w * 3:(top + im.h) * im.w * 3] = im.buf
    if bottom:
        c = backdrop(im, range(im.h - 24, im.h))
        out.buf[(top + im.h) * im.w * 3:] = bytes(c) * (bottom * im.w)
    if not (left or right):
        return out
    cl = side_backdrop(out, range(0, 24)) if left else None
    cr = side_backdrop(out, range(out.w - 24, out.w)) if right else None
    W = out.w + left + right
    wide = Img(W, out.h, alpha=False)
    for y in range(out.h):
        row = bytearray()
        if left:
            row += bytes(cl) * left
        row += out.buf[y * out.w * 3:(y + 1) * out.w * 3]
        if right:
            row += bytes(cr) * right
        wide.buf[y * W * 3:(y + 1) * W * 3] = row
    return wide


def recolour_hair(im, rows, shift_deg, sat_factor):
    """Shift the hue and scale the saturation of dark, warm, saturated pixels
    in the given rows: hair, not skin (too light), lips (too light), the coat
    (grey) or the turtleneck (teal)."""
    import colorsys
    n = 0
    for y in rows:
        for x in range(im.w):
            i = (y * im.w + x) * 3
            r, g, b = im.buf[i] / 255.0, im.buf[i + 1] / 255.0, im.buf[i + 2] / 255.0
            h, l, sat = colorsys.rgb_to_hls(r, g, b)
            if not (0.04 < l < 0.5 and sat > 0.12 and (h < 25 / 360.0 or h > 335 / 360.0)):
                continue
            h = (h + shift_deg / 360.0) % 1.0
            r, g, b = colorsys.hls_to_rgb(h, l, min(1.0, sat * sat_factor))
            im.buf[i], im.buf[i + 1], im.buf[i + 2] = int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)
            n += 1
    return n


def start(char):
    """The working base as it is before any edit is pasted in: the chosen
    render, padded at each cut edge, hair recoloured. Deterministic, so apply()
    can rebuild the untouched version to line edits up against."""
    src = rgb(load(os.path.join(IMAGES, BASES[char])))
    # A character rendered on another screen colour (magenta, for Maki's green
    # hair) goes onto pure green first, so everything below stays green-based.
    from keysprite import screen_key, sample_bg, rescreen
    screen = screen_key(sample_bg(src))
    if screen and screen[0] != "green":
        src = rgb(rescreen(src))
        print("%-7s rendered on %s; moved onto pure green" % (char, screen[0]))
    cuts = cut_columns(src)
    top, bottom = (PAD if "top" in cuts else 0), (PAD if "bottom" in cuts else 0)
    left, right = side_pads(cuts)
    work = pad(src, top, bottom, left, right)
    if char in HAIR_SHIFT:
        shift, factor = HAIR_SHIFT[char]
        n = recolour_hair(work, range(top, top + int(src.h * 0.45)), shift, factor)
        print("%-7s hair recoloured: %+.0f degrees, saturation x%.2f, %d pixels" % (char, shift, factor, n))
    if char in SKIN_TARGET:
        grade_skin(work, SKIN_TARGET[char], char)
    return src, cuts, top, bottom, work


def grade_skin(work, target, char):
    """Grade every skin pixel on the figure to target (hue, saturation, median
    lightness), keeping the shading: lightness and saturation are scaled,
    hue shifted."""
    import colorsys
    from facemask import is_skin
    from keysprite import key_out
    keyed = key_out(work)
    idx, hls = [], []
    for p in range(work.w * work.h):
        if keyed.buf[p * 4 + 3] < 200:
            continue
        r, g, b = work.buf[p * 3:p * 3 + 3]
        if is_skin(r, g, b):
            idx.append(p)
            hls.append(colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0))
    th, ts, tl = target
    hs = sorted(h if h < 0.5 else h - 1.0 for h, l, sat in hls)
    ls = sorted(l for h, l, sat in hls)
    ss = sorted(sat for h, l, sat in hls)
    mh, ml, ms = hs[len(hs) // 2], ls[len(ls) // 2], ss[len(ss) // 2]
    dh, fl, fs = th / 360.0 - mh, tl / ml, ts / ms
    for p, (h, l, sat) in zip(idx, hls):
        r, g, b = colorsys.hls_to_rgb((h + dh) % 1.0, min(1.0, l * fl), min(1.0, sat * fs))
        work.buf[p * 3:p * 3 + 3] = bytes((int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)))
    print("%-7s skin graded: hue %+.0f -> %+.0f deg, saturation %.2f -> %.2f, lightness %.2f -> %.2f (%d pixels)"
          % (char, mh * 360, th, ms, ts, ml, tl, len(idx)))


def head_closeup(work, top, char=None):
    """The square around the head for the head fix, with room above a cut
    crown for the model to finish it. Returns (X, Y, side)."""
    from facemask import head_box
    from keysprite import key_out
    x0, y0, x1, cut, (fx0, fy0, fx1, fy1) = head_box(work, key_out(work))
    side = max(x1 - x0, cut - y0, int((fx1 - fx0) * 2.8)) + 40
    side = min(work.w, work.h, (side + 63) // 64 * 64)
    cx = (fx0 + fx1) // 2
    X = max(0, min(work.w - side, cx - side // 2))
    room = HEAD_ROOM_ABOVE.get(char, 40 if top else 12)
    Y = max(0, min(work.h - side, y0 - room))
    return X, Y, side


def record_path(char):
    return os.path.join(IMAGES, "masks", "%s_edges.txt" % char)


def read_record(char):
    """(render, top, bottom, left, right) pads; older records have no sides."""
    parts = open(record_path(char)).read().split("\t")
    nums = [int(v) for v in parts[1:]] + [0, 0]
    return (parts[0],) + tuple(nums[:4])


def close_size(w):
    """A 16:9 close-up across the whole working width: 768 x 432 for a render
    with no side padding, as before."""
    return w, int(round(w * 9 / 16.0))


def close_rows(edge, h, ch=CLOSE_H):
    return (0, ch) if edge == "top" else (h - ch, h)


def side_box(edge, y0, y1, top, work):
    """(X, Y) of the 9:16 close-up for a cut down the left or right edge,
    centred on the cut rows."""
    cy = top + (y0 + y1) // 2
    Y = max(0, min(work.h - SIDE_H, cy - SIDE_H // 2))
    X = 0 if edge == "left" else work.w - SIDE_W
    return X, Y


def write_workflow(rows, heading, blurb, out_name):
    """rows: (char, kind, staged image, prompt, versions, aspect). One row per
    close-up, each version saved as `edge_<char>_<kind>`."""
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

    count = sum(r[4] for r in rows)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-900, -520], "size": [600, 400],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## %s\n\n"
        "Run this in the **local ComfyUI** and press **Run**. %s\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro).\n\n"
        "No need to save anything. Claude picks the results up from ComfyUI's output folder.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press "
        "**Run** again: finished pictures are reused, not paid for twice."
        % (heading, blurb, count, count * COST)]})
    gem = P["GeminiImage2Node"]["widgets_values"]
    row_h = 560
    for r, (char, kind, staged, prompt, versions, aspect) in enumerate(rows):
        y = r * row_h
        ld = add("LoadImage", (-900, y), (300, 320), title="%s: %s" % (char, kind), widgets=[staged, "image"])
        for k in range(versions):
            w = list(gem)
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt, 900 + r * 10 + k, "fixed", aspect, "1K", "IMAGE"
            n = add("GeminiImage2Node", (k * 820, y), (400, 360), title="%s %s (%d)" % (char, kind, k + 1),
                    widgets=w)
            wire(ld, n, "images")
            sv = add("SaveImage", (k * 820 + 420, y), (380, 360), widgets=["edge_%s_%s" % (char, kind)])
            wire(n, sv, "images")
        groups.append(("%s: %s" % (char.upper(), kind.upper()) if kind in ("head", "hair") else
                       "%s: %s EDGE" % (char.upper(), kind.upper()), y))

    widest = max(r[4] for r in rows)
    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links,
               "groups": [{"id": i + 1, "title": t, "bounding": [-920, gy - 50, 940 + 820 * widest, row_h - 30],
                           "color": "#3f4f5a", "font_size": 24, "flags": {}} for i, (t, gy) in enumerate(groups)]})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.45, "offset": [980, 560]}
    out = os.path.join(IMAGES, out_name)
    json.dump(wf, open(out, "w"), indent=1)
    print("workflow -> %s  (%d pictures, about $%.2f)" % (out, count, count * COST))


def prepare(chars, force=False):
    rows = []
    os.makedirs(FIXED, exist_ok=True)
    for char in chars:
        src, cuts, top, bottom, work = start(char)
        work_path = os.path.join(FIXED, "%s_base.png" % char)
        if os.path.exists(work_path) and not force:
            old = rgb(load(work_path))
            if (old.w, old.h) != (work.w, work.h) or old.buf != work.buf:
                raise SystemExit("%s already has repairs pasted in; starting again would throw them "
                                 "away. Pass --force to do that." % work_path)
        work.save(work_path)
        left, right = side_pads(cuts)
        with open(record_path(char), "w") as f:
            f.write("%s\t%d\t%d\t%d\t%d" % (BASES[char], top, bottom, left, right))
        if not cuts and char not in HEAD_FIX:
            print("%-7s nothing touches the top or bottom edge; working base written" % char)
            continue
        if char in HEAD_FIX:
            from raster import resample
            X, Y, side = head_closeup(work, top, char)
            close = resample(crop(work, X, Y, X + side, Y + side), 1024, 1024)
            staged = "head_%s.png" % char
            close.save(os.path.join(COMFY_INPUT, staged))
            close.save(os.path.join(FIXED, staged))
            os.makedirs(os.path.join(FIXED, "masks"), exist_ok=True)
            with open(os.path.join(FIXED, "masks", "%s_edit_crop.txt" % char), "w") as f:
                f.write("%d %d %d\n" % (X, Y, side))
            his, who = pronoun(char)
            crown = (" The picture was cut off at the top, so the top of %s head is sliced off and a "
                     "strip of plain green was added above it: finish the top of %s head naturally "
                     "into that strip, with plain green left above it." % (his, his) if "top" in cuts else "")
            keep = HEAD_KEEP_FOR.get(char) or HEAD_KEEP.format(his=his)
            prompt = ("This is a close-up of a cartoon character, %s on a plain flat green "
                      "background. " % who + HEAD_FIX[char] + crown + " " + keep)
            rows.append((char, "head", staged, prompt, HEAD_VERSIONS, "1:1"))
            print("%-7s head   close-up %dx%d at (%d, %d) -> %s" % (char, side, side, X, Y, staged))
        for edge, (x0, x1) in sorted(cuts.items()):
            if edge == "top" and char in HEAD_FIX:
                continue                     # the head fix finishes the crown
            if edge in ("left", "right"):
                X, Y = side_box(edge, x0, x1, top, work)
                close = crop(work, X, Y, X + SIDE_W, Y + SIDE_H)
                staged = "edge_%s_%s.png" % (char, edge)
                close.save(os.path.join(COMFY_INPUT, staged))
                close.save(os.path.join(FIXED, staged))
                prompt = ("This is a close-up of %s of a cartoon character, drawn on a plain flat green "
                          "background. The original picture was cut off at the %s, so %s"
                          % (CLOSE_SUBJECT[edge], edge, WHAT["side"] % edge))
                rows.append((char, edge, staged, prompt, VERSIONS, "9:16"))
                print("%-7s %-6s cut at rows %d-%d; close-up %dx%d at (%d, %d) -> %s"
                      % (char, edge, x0, x1, SIDE_W, SIDE_H, X, Y, staged))
                continue
            cw, ch = close_size(work.w)
            r0, r1 = close_rows(edge, work.h, ch)
            close = crop(work, 0, r0, cw, r1)
            staged = "edge_%s_%s.png" % (char, edge)
            close.save(os.path.join(COMFY_INPUT, staged))
            close.save(os.path.join(FIXED, staged))
            side = "right" if (x0 + x1) / 2.0 > src.w / 2.0 else "left"
            what = WHAT[edge] % side if "%s" in WHAT[edge] else WHAT[edge]
            prompt = ("This is a close-up of %s of a cartoon character, drawn on a plain flat green "
                      "background. The original picture was cut off at the %s, so %s"
                      % (CLOSE_SUBJECT[edge], edge, what))
            rows.append((char, edge, staged, prompt, VERSIONS, "16:9"))
            print("%-7s %-6s cut at x %d-%d; close-up rows %d-%d -> %s" % (char, edge, x0, x1, r0, r1, staged))
    if not rows:
        print("nothing to repair: no workflow needed; install with --install")
        return
    write_workflow(rows, "Repair the base picture: %s" % ", ".join(chars),
                   "Each row is a close-up: a cut edge with a strip of green added, where the model "
                   "draws the missing hair or shoe, or a head to redraw.", "edges.json")


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
    return align_pts(close, ed, pts)


def align_pts(close, ed, pts):
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


def extend_chin(mask_path, rows):
    """Carry the head mask's lowest row down `rows` more, fading out, so a
    beard drawn below the chin comes across."""
    m = rgb(load(mask_path))
    last = max(y for y in range(m.h) if any(m.buf[(y * m.w + x) * 3] > 128 for x in range(m.w)))
    xs = [x for x in range(m.w) if m.buf[(last * m.w + x) * 3] > 128]
    x0, x1 = min(xs), max(xs)
    for k in range(1, rows + 1):
        y = last + k
        if y >= m.h:
            break
        v = int(255 * (1.0 - k / float(rows + 1)))
        for x in range(x0, x1 + 1):
            i = (y * m.w + x) * 3
            if m.buf[i] < v:
                m.buf[i:i + 3] = bytes((v, v, v))
    m.save(mask_path)
    print("   head mask carried %d rows below the chin (x %d-%d from row %d)" % (rows, x0, x1, last))


def apply_head(char, edited):
    """Composite a redrawn head into the working base through the head mask:
    the dome over the hair and upper face, then only the skin of the lower
    face, so long hair beside and below the face stays as drawn."""
    import shutil
    from facemask import build_head
    import composite_face
    work_path = os.path.join(FIXED, "%s_base.png" % char)
    mask = build_head(work_path, char, out_dir=os.path.join(FIXED, "masks"),
                      margin=HEAD_MARGIN.get(char, 0.14))
    if HEAD_CHIN_EXTRA.get(char):
        extend_chin(mask, HEAD_CHIN_EXTRA[char])
    path, params = composite_face.run(work_path, edited, char, "headfix", mask_path=mask, install=False)
    shutil.copy(path, work_path)
    print("   head redrawn -> %s" % work_path)


def apply(char, edge, edited):
    if edge == "head":
        return apply_head(char, edited)
    srcname, top, bottom, left, right = read_record(char)
    src, cuts, top2, bottom2, pristine = start(char)
    assert (srcname, top, bottom, left, right) == (BASES[char], top2, bottom2) + side_pads(cuts), \
        "run --prepare again"
    if edge not in cuts:
        raise SystemExit("%s: the %s edge isn't cut" % (char, edge))
    work_path = os.path.join(FIXED, "%s_base.png" % char)
    work = rgb(load(work_path))
    assert (work.w, work.h) == (pristine.w, pristine.h), "run --prepare again"
    if edge in ("left", "right"):
        return apply_side(char, edge, edited, src, cuts, top, left, right, pristine, work, work_path)
    cw, ch = close_size(pristine.w)
    r0, r1 = close_rows(edge, pristine.h, ch)
    close = crop(pristine, 0, r0, cw, r1)

    raw = rgb(load(os.path.expanduser(edited)))
    ed = rgb(resample(raw, cw, ch))
    # The cut, in close-up rows, and the rows to line up on: well away from it.
    if edge == "top":
        cut = top
        ref_rows = range(min(ch - 40, cut + 110), ch, 3)
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
    px0, px1 = max(0, x0 + left - SIDE), min(pristine.w - 1, x1 + left + SIDE)
    if edge == "top":
        ys = range(0, top + INTO + 1)
        inner = lambda y: (top + INTO - y) / float(FEATHER)
    else:
        first = top + src.h - 1 - INTO
        ys = range(first, pristine.h)
        inner = lambda y: (y - first) / float(FEATHER)
    kx, ky = raw.w / float(cw), raw.h / float(ch)
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


def apply_side(char, edge, edited, src, cuts, top, left, right, pristine, work, work_path):
    """Paste a finished outline down the left or right edge: the new strip and
    a little of the figure beside it, over the cut rows, lined up on the
    figure well away from the cut and feathered into it."""
    y0, y1 = cuts[edge]
    X, Y = side_box(edge, y0, y1, top, pristine)
    close = crop(pristine, X, Y, X + SIDE_W, Y + SIDE_H)
    raw = rgb(load(os.path.expanduser(edited)))
    ed = rgb(resample(raw, SIDE_W, SIDE_H))
    padw = left if edge == "left" else right
    cols = (range(padw + 110, SIDE_W, 3) if edge == "left" else range(0, max(3, SIDE_W - padw - 110), 3))
    pts = []
    for yy in range(0, SIDE_H, 3):
        for xx in cols:
            i = (yy * SIDE_W + xx) * 3
            r, g, b = close.buf[i], close.buf[i + 1], close.buf[i + 2]
            if g - max(r, b) > 20:
                continue
            pts.append((xx, yy))
    (err, s, dx, dy), before, c = align_pts(close, ed, pts)
    print("%s %s: lined up at scale %.4f, shift (%d, %d); mismatch %.1f -> %.1f"
          % (char, edge, s, dx, dy, before, err))
    if err > 12:
        raise SystemExit("the edit moved the figure too much to trust (mismatch %.1f)" % err)

    FEATHER, INTO, MARGIN = 20, 60, 40
    if edge == "left":
        xs = range(0, left + INTO + 1)
        inner = lambda x: (left + INTO - x) / float(FEATHER)
    else:
        first = pristine.w - right - 1 - INTO
        xs = range(first, pristine.w)
        inner = lambda x: (x - first) / float(FEATHER)
    ry0, ry1 = max(Y, top + y0 - MARGIN), min(Y + SIDE_H - 1, top + y1 + MARGIN)
    kx, ky = raw.w / float(SIDE_W), raw.h / float(SIDE_H)
    cx, cy = c
    patch = {}
    for y in range(ry0, ry1 + 1):
        wy = min(1.0, (y - ry0) / float(FEATHER), (ry1 - y) / float(FEATHER))
        for x in xs:
            a = max(0.0, min(wy, min(1.0, inner(x))))
            if a <= 0:
                continue
            ex = cx + (x - X - cx) * s + dx
            ey = cy + (y - Y - cy) * s + dy
            patch[(x, y)] = (a, sample(raw, (ex + 0.5) * kx - 0.5, (ey + 0.5) * ky - 0.5))
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


# Bodies the base model drew the wrong build, reshaped by Nano Banana on the
# full picture; only the body from the collar down is pasted back, so the
# approved head is kept exactly. Yaga came out about 11-16% wider through the
# chest and stomach than his design sheet, bulging at the middle.
BODY_FIX = {
    "yaga": ("Make his build muscular rather than heavy, as in his design: keep his shoulders just as "
             "broad, but make his chest and waist narrower and his stomach flat, so his black jacket "
             "hangs straight down from his shoulders to his hips instead of bulging at the middle; make "
             "his arms and legs a little slimmer to match."),
}
BODY_VERSIONS = 3


def prepare_body(chars):
    rows = []
    for char in chars:
        work = rgb(load(os.path.join(FIXED, "%s_base.png" % char)))
        staged = "body_%s.png" % char
        work.save(os.path.join(COMFY_INPUT, staged))
        his, who = pronoun(char)
        prompt = ("This is a full-body picture of a cartoon character, %s on a plain flat green background. "
                  % who + BODY_FIX[char] + " Keep %s head, face, sunglasses, beard and hair exactly as they "
                  "are, and keep %s pose, the positions of %s hands and feet, %s height, the clothes and "
                  "their colours, the framing and the plain flat green background exactly the same, in the "
                  "same flat cel shading and line art." % (his, his, his, his))
        rows.append((char, "body", staged, prompt, BODY_VERSIONS, "9:16"))
        print("%-7s body   full picture %dx%d -> %s" % (char, work.w, work.h, staged))
    write_workflow(rows, "Reshape the body: %s" % ", ".join(chars),
                   "Each version reshapes the body on the full picture; only the body is kept.", "body.json")


def apply_body(char, edited):
    """Paste the reshaped body from the collar down, lined up on the head and
    collar (which the edit must not move), fading in across the collar so no
    seam shows. The approved head above stays exactly as it is."""
    from facemask import head_box
    from keysprite import key_out
    work_path = os.path.join(FIXED, "%s_base.png" % char)
    work = rgb(load(work_path))
    raw = rgb(load(os.path.expanduser(edited)))
    ed = rgb(resample(raw, work.w, work.h))
    x0, y0, x1, cut, (fx0, fy0, fx1, fy1) = head_box(work, key_out(work))
    seam = fy1 + 50                  # inside the collar, clear of the chin and a beard's point
    band = 20
    pts = [(x, y) for y in range(y0, seam, 2) for x in range(0, work.w, 2)
           if work.buf[(y * work.w + x) * 3 + 1] - max(work.buf[(y * work.w + x) * 3],
                                                       work.buf[(y * work.w + x) * 3 + 2]) <= 20]
    c = ((fx0 + fx1) / 2.0, (fy0 + fy1) / 2.0)
    best = (score(work, ed, pts, c, 1.0, 0, 0), 1.0, 0, 0)
    for sc in [0.98 + 0.005 * i for i in range(9)]:
        for dy in range(-10, 11, 2):
            for dx in range(-10, 11, 2):
                e = score(work, ed, pts, c, sc, dx, dy)
                if e < best[0]:
                    best = (e, sc, dx, dy)
    err, sc, dx, dy = best
    print("%s body: lined up on the head at scale %.3f, shift (%d, %d); mismatch %.1f" % (char, sc, dx, dy, err))
    if err > 14:
        raise SystemExit("the edit moved the head too much to join the body on cleanly (mismatch %.1f)" % err)
    kx, ky = raw.w / float(work.w), raw.h / float(work.h)
    for y in range(seam - band, work.h):
        t = min(1.0, (y - (seam - band)) / float(band))
        for x in range(work.w):
            ex, ey = c[0] + (x - c[0]) * sc + dx, c[1] + (y - c[1]) * sc + dy
            v = sample(raw, (ex + 0.5) * kx - 0.5, (ey + 0.5) * ky - 0.5)
            i = (y * work.w + x) * 3
            for k in range(3):
                work.buf[i + k] = max(0, min(255, int(work.buf[i + k] * (1 - t) + v[k] * t + 0.5)))
    work.save(work_path)
    print("   body from row %d down (fading in over %d rows) -> %s" % (seam - band, band, work_path))


def hairlike(r, g, b):
    """Brown hair, dark or light, highlights included; not skin, the coat,
    the turtleneck or the backdrop."""
    import colorsys
    h, l, sat = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    h = h if h < 0.5 else h - 1.0
    if not (-15 / 360.0 < h < 45 / 360.0 and 0.05 < l < 0.68 and sat > 0.10):
        return False
    from facemask import is_skin
    return not is_skin(r, g, b)          # shadowed skin (a hand, the neck) is brown too


def hair_extent(work):
    """(top of the figure, lowest row with hair, x range of the hair)."""
    from keysprite import key_out, bbox
    keyed = key_out(work)
    x0, y0, x1, y1 = bbox(keyed)
    last, xs = y0, []
    for y in range(y0, y0 + int((y1 - y0) * 0.36)):     # hair ends by mid-chest
        row = [x for x in range(work.w) if keyed.buf[(y * work.w + x) * 4 + 3] > 128 and
               hairlike(*work.buf[(y * work.w + x) * 3:(y * work.w + x) * 3 + 3])]
        if len(row) >= 12:
            last = y
            xs += [row[0], row[-1]]
    return y0, last, (min(xs), max(xs))


def prepare_hair(chars):
    from raster import resample
    from facemask import face_box
    from keysprite import key_out
    rows = []
    for char in chars:
        work = rgb(load(os.path.join(FIXED, "%s_base.png" % char)))
        top, bottom, (hx0, hx1) = hair_extent(work)
        fx0, fy0, fx1, fy1 = face_box(work, key_out(work))
        side = max(bottom + 40 - (top - 24), hx1 - hx0 + 100)
        side = min(work.w, work.h, (side + 63) // 64 * 64)
        cx = (fx0 + fx1) // 2
        X = max(0, min(work.w - side, cx - side // 2))
        Y = max(0, min(work.h - side, top - 24))
        close = resample(crop(work, X, Y, X + side, Y + side), 1024, 1024)
        staged = "hair_%s.png" % char
        close.save(os.path.join(COMFY_INPUT, staged))
        close.save(os.path.join(FIXED, staged))
        with open(os.path.join(FIXED, "masks", "%s_hair_crop.txt" % char), "w") as f:
            f.write("%d %d %d %d\n" % (X, Y, side, bottom))
        his, who = pronoun(char)
        prompt = ("This is a close-up of a cartoon character, %s on a plain flat green background. " % who
                  + HAIR_FIX[char] + " " + HAIR_KEEP.format(his=his))
        rows.append((char, "hair", staged, prompt, HAIR_VERSIONS, "1:1"))
        print("%-7s hair   rows %d-%d, x %d-%d; close-up %dx%d at (%d, %d) -> %s"
              % (char, top, bottom, hx0, hx1, side, side, X, Y, staged))
    write_workflow(rows, "Restyle the hair: %s" % ", ".join(chars),
                   "Each version restyles the hair on a close-up and keeps the face.", "hair.json")


def dilate(mask, w, h, r):
    """Max filter, separable, on a 0/1 bytearray."""
    tmp = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            if mask[row + x]:
                for xx in range(max(0, x - r), min(w, x + r + 1)):
                    tmp[row + xx] = 1
    out = bytearray(w * h)
    for x in range(w):
        for y in range(h):
            if tmp[y * w + x]:
                for yy in range(max(0, y - r), min(h, y + r + 1)):
                    out[yy * w + x] = 1
    return out


def box_blur(vals, w, h, r):
    """Box blur of a float list, separable."""
    def one(src, n, stride, count, step):
        out = [0.0] * len(src)
        for c in range(count):
            base = c * step
            acc, win = 0.0, []
            line = [src[base + i * stride] for i in range(n)]
            pre = [0.0]
            for v in line:
                pre.append(pre[-1] + v)
            for i in range(n):
                a, b = max(0, i - r), min(n, i + r + 1)
                out[base + i * stride] = (pre[b] - pre[a]) / (b - a)
        return out
    rows = one(vals, w, 1, h, w)
    return one(rows, h, w, w, 1)


def apply_hair(char, edited):
    """Paste a restyled head of hair into the working base. The mask is the
    hair before and after (so hair that moved outward and gaps it left are both
    covered), grown a little for outlines, minus the inner face, which stays as
    approved."""
    from facemask import face_box
    from keysprite import key_out
    work_path = os.path.join(FIXED, "%s_base.png" % char)
    work = rgb(load(work_path))
    raw = rgb(load(os.path.expanduser(edited)))
    X, Y, side, hair_bottom = [int(v) for v in
                               open(os.path.join(FIXED, "masks", "%s_hair_crop.txt" % char)).read().split()]
    ed = rgb(resample(raw, side, side))
    base_sq = crop(work, X, Y, X + side, Y + side)

    # Line up on what must not move: clothes and the face. Not hair or backdrop
    # in either picture, since restyled hair can cover coat or temple that used
    # to show, and its edges.
    near_hair = bytearray(side * side)
    for p in range(side * side):
        if hairlike(*base_sq.buf[p * 3:p * 3 + 3]) or hairlike(*ed.buf[p * 3:p * 3 + 3]):
            near_hair[p] = 1
    near_hair = dilate(near_hair, side, side, 4)
    pts = []
    for y in range(0, side, 3):
        for x in range(0, side, 3):
            i = (y * side + x) * 3
            r, g, b = base_sq.buf[i], base_sq.buf[i + 1], base_sq.buf[i + 2]
            if g - max(r, b) > 20 or near_hair[y * side + x]:
                continue
            pts.append((x, y))
    c = (side / 2.0, side / 2.0)
    best = (score(base_sq, ed, pts, c, 1.0, 0, 0), 1.0, 0, 0)
    for sc in (0.99, 0.995, 1.0, 1.005, 1.01):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                e = score(base_sq, ed, pts, c, sc, dx, dy)
                if e < best[0]:
                    best = (e, sc, dx, dy)
    err, sc, dx, dy = best
    print("%s hair: lined up at scale %.3f, shift (%d, %d); mismatch on clothes and face %.1f"
          % (char, sc, dx, dy, err))
    if err > 12:
        raise SystemExit("the edit moved the clothes or face too much to trust (mismatch %.1f)" % err)

    kx, ky = raw.w / float(side), raw.h / float(side)
    def from_edit(u, v):
        eu, ev = c[0] + (u - c[0]) * sc + dx, c[1] + (v - c[1]) * sc + dy
        return sample(raw, (eu + 0.5) * kx - 0.5, (ev + 0.5) * ky - 0.5)

    edit_px = [from_edit(u, v) for v in range(side) for u in range(side)]
    hair = bytearray(side * side)
    for p in range(side * side):
        b0 = base_sq.buf[p * 3:p * 3 + 3]
        e = edit_px[p]
        if hairlike(*b0) or hairlike(int(e[0]), int(e[1]), int(e[2])):
            hair[p] = 1
    hair = dilate(hair, side, side, 6)
    a = [float(v) for v in hair]
    # Nothing below where the hair ends (plus room for it to grow a little).
    stop = hair_bottom + 40 - Y
    for v in range(max(0, stop), side):
        for u in range(side):
            a[v * side + u] = 0.0

    # The inner face stays exactly as approved.
    fx0, fy0, fx1, fy1 = face_box(work, key_out(work))
    fw, fh = fx1 - fx0, fy1 - fy0
    ecx, ecy = (fx0 + fx1) / 2.0 - X, fy0 + 0.60 * fh - Y
    erx, ery = 0.40 * fw, 0.46 * fh
    for v in range(side):
        for u in range(side):
            d = ((u - ecx) / erx) ** 2 + ((v - ecy) / ery) ** 2
            if d < 1.25:
                a[v * side + u] *= max(0.0, min(1.0, (d - 1.0) / 0.25))
    a = box_blur(a, side, side, 3)
    edge = 14
    for v in range(side):
        for u in range(side):
            k = min(u, v, side - 1 - u, side - 1 - v)
            if k < edge:
                a[v * side + u] *= k / float(edge)

    # Grade the new hair to the references (only hair inside the mask; the
    # face is already masked out).
    if char in HAIR_TARGET:
        import colorsys
        th, ts, tl = HAIR_TARGET[char]
        idx = [p for p in range(side * side)
               if a[p] > 0 and hairlike(int(edit_px[p][0]), int(edit_px[p][1]), int(edit_px[p][2]))]
        hls = [colorsys.rgb_to_hls(*(max(0.0, min(255.0, c)) / 255.0 for c in edit_px[p])) for p in idx]
        hs = sorted(h if h < 0.5 else h - 1.0 for h, l, sat in hls)
        ls = sorted(l for h, l, sat in hls)
        ss = sorted(sat for h, l, sat in hls)
        mh, ml, ms = hs[len(hs) // 2], ls[len(ls) // 2], ss[len(ss) // 2]
        dh, fl, fs = th / 360.0 - mh, tl / ml, ts / ms
        for p, (h, l, sat) in zip(idx, hls):
            r, g, b = colorsys.hls_to_rgb((h + dh) % 1.0, min(1.0, l * fl), min(1.0, sat * fs))
            edit_px[p] = [r * 255.0, g * 255.0, b * 255.0]
        print("   hair graded: hue %+.0f -> %+.0f deg, saturation %.2f -> %.2f, lightness %.2f -> %.2f (%d pixels)"
              % (mh * 360, th, ms, ts, ml, tl, len(idx)))

    # Colour: take out any overall cast of the edit, judged on clothes at the
    # mask's soft edge (never on hair, whose colour is meant to change).
    diffs = [[], [], []]
    for p in range(side * side):
        if 0.05 < a[p] < 0.95:
            b0 = base_sq.buf[p * 3:p * 3 + 3]
            if b0[1] - max(b0[0], b0[2]) > 20 or hairlike(*b0):
                continue
            for k in range(3):
                diffs[k].append(b0[k] - edit_px[p][k])
    shift = [0.0, 0.0, 0.0]
    if len(diffs[0]) > 40:
        shift = [max(-15.0, min(15.0, sorted(d)[len(d) // 2])) for d in diffs]
    print("   colour shift %s over %d clothing pixels at the mask edge" % ([round(v, 1) for v in shift], len(diffs[0])))

    n = 0
    for v in range(side):
        for u in range(side):
            t = a[v * side + u]
            if t <= 0.0:
                continue
            n += 1
            i = ((Y + v) * work.w + X + u) * 3
            e = edit_px[v * side + u]
            for k in range(3):
                work.buf[i + k] = max(0, min(255, int(work.buf[i + k] * (1 - t) + (e[k] + shift[k]) * t + 0.5)))
    work.save(work_path)
    print("   %d pixels from the edit -> %s" % (n, work_path))


def install(char):
    from keysprite import install as key_install
    path = os.path.join(FIXED, "%s_base.png" % char)
    problems = key_install(path, "%s_neutral" % char)
    print("installed %s_neutral from %s" % (char, path))
    for p in problems:
        print("   !! " + p)
    return problems


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    if len(args) >= 2 and args[0] == "--prepare":
        prepare(args[1:], force="--force" in sys.argv)
    elif len(args) >= 2 and args[0] == "--prepare-hair":
        prepare_hair(args[1:])
    elif len(args) >= 2 and args[0] == "--prepare-body":
        prepare_body(args[1:])
    elif len(args) == 3 and args[1] == "body":
        apply_body(args[0], args[2])
    elif len(args) == 3 and args[1] == "hair":
        apply_hair(args[0], args[2])
    elif len(args) == 2 and args[1] == "--install":
        install(args[0])
    elif len(args) == 3 and args[1] in ("top", "bottom", "left", "right", "head"):
        apply(args[0], args[1], args[2])
    else:
        print(__doc__); raise SystemExit(1)
