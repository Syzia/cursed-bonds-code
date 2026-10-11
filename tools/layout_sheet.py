"""
Draw a layout on its background, to look at before it is approved.

    python3 tools/layout_sheet.py view_dorm_common      # where people stand, the floor, the scale, pose boxes, foreground
    python3 tools/layout_sheet.py hot_dorm_common       # the room's exits and hotspots; its shapes when it has any
    python3 tools/layout_sheet.py area_school           # the map pins of an area

    python3 tools/layout_sheet.py view_dorm_common --sidecar some/view_dorm_common.json
    python3 tools/layout_sheet.py view_dorm_common --fg some/dorm_common.json
    python3 tools/layout_sheet.py view_dorm_common --no-sidecar --out shots/layout/x.png

    # a layout that is still only STAGED: its files in a folder, its picture given by path
    python3 tools/layout_sheet.py hot_courtyard --staged tools/art/staged/courtyard \
        --bg ~/ComfyUI-Shared/output/look2_courtyard_gateway_00001_.png
    python3 tools/layout_sheet.py hot_courtyard --layout-dump shots/art/game_layout.json     # in a worktree

The name is a layout's full stem, as `rule_layout(name)` takes it in the game
(PHASE2_DESIGN.md D5, 6.1; UI2_DESIGN.md 3.2). What is drawn is what the game
would use: the code's own numbers, with the sidecar's laid over them.

  * The game's numbers come from the layout dump, tools/art/game_layout.json,
    through tools/game_layout.py: the frame, the two lanes, the stage's edges,
    the sprite canvas, every exit and hotspot with the code's own point, the
    planned hotspots, the code's slots, the map pins. The sheet keeps no copy
    of any of them. (Until U0d3 it read shots/layout/defaults.json and typed
    the lanes itself; its toast lane had fallen 72 px short of the game's.)
  * The sidecar is `game/layout/<name>.json` when it exists, or the file given
    with --sidecar, or `<name>.json` in the folder given with --staged;
    --no-sidecar draws the code's numbers alone. Its keys (3.2):
        hot_<place>.json   spots {"<hotspot or exit id>": [x, y]}, tips {"<id>": side},
                           shapes {"<id>": [polygon, ...]} (D60), keep_tile {"<id>": reason},
                           spare [[x, y], ...] (the three houses), for_rev
        view_<place>.json  slots {"<n>": [[xcenter, yoffset, zoom, far], ...]},
                           poses {"<who>" or "<who>__<variant>": [x, y, w, h]},
                           floor {"on": [polygons], "off": [polygons]}, scale [x, y top, y bottom],
                           slot_light, cast, talk, for_rev
        area_<key>.json    spots {"<loc>": [x, y]}, for_rev
  * Foreground polygons are tool input, never read by the game:
    `tools/fg/<place>.json` (or --fg): {"<variant, or "" for the day picture>":
    [[x, y], ...]}. A view sheet draws them. A staged folder's
    check_<place>.json (tools/check_layout.py) may hold the same under "fg",
    and the planned front ids under "front".

A view sheet is four half-size panels (one, two, three and four people: the
sprite's box at each slot, with its feet line), then one full-size panel for
each picture that has pose boxes, a foreground polygon, a floor or a scale:
the floor people may stand on in green, the parts they may not in red, the
scale as a bar taken as 200 cm. A hotspot sheet shows each 72 px square with
the side its name opens on, the frame they must stay inside, the two lanes
they must stay out of, the spare doors, and where people stand. FOR A SHAPED
PLACE (the sidecar holds `shapes`, D60) the first frame draws every shape's
outline over the picture (a front shape dashed, a hotspot that keeps its
button marked so), and a SECOND FRAME shows every shape lit and named, each
name where its plate is drawn while names are shown. An area sheet shows each
72 px pin with its room, and the frame pins must stay inside.

The picture is the place's own (`game/images/bg/`), or the file --bg names (a
render of any size, fitted to 1920 x 1080), or, while neither exists, a plain
ground; the sheet says which. Writes `shots/layout/<name>.png`
(`<name>__sidecar.png` with --sidecar, `<name>__staged.png` with --staged),
or --out. Pure Python: raster.py and pngread.py.
"""
import sys, os, re, json, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, crop
import game_layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "game", "images", "bg")
W, H = 1920, 1080
SPRITE = (760, 1400)                     # the sprite canvas (view_stage.rpy, VIEW_SPRITE)

# What the validators allow (PHASE2_DESIGN.md 4.1, 4.10, R6). Each is read from the layout dump when the tool
# starts (use_dump): the values here are only what the names hold before that, and nothing draws with them.
PIN_FRAME = (200, 200, 1700, 940)
HOT_FRAME = (40, 180, 1700, 1000)
TOAST_LANE = (1330, 92, 1790, 422)      # x0, y0, x1, y1
BANNER_LANE = (400, 96, 1300, 170)
STAGE_X = (40, 1700)
HOT_SIZE = 72
HUD_TOP = 92                             # above this y no shape takes the pointer (HOT_SHAPE["top"])
LIGHT = (255, 240, 204)                  # the light of a shaped hotspot (hot_look.color)
LAY = None                               # the dump, as game_layout.Layout


def use_dump(lay):
    """Take every number the sheets draw with from the layout dump (docs/UI2_DESIGN.md 10.1: the sheet's own
    copy was out of step)."""
    global LAY, W, H, SPRITE, PIN_FRAME, HOT_FRAME, TOAST_LANE, BANNER_LANE, STAGE_X, HOT_SIZE, HUD_TOP, LIGHT
    LAY = lay
    W, H = lay.screen()
    SPRITE = tuple(lay.frame("sprite", SPRITE))
    PIN_FRAME = tuple(lay.frame("map_pin_frame", PIN_FRAME))
    HOT_FRAME = tuple(lay.frame("hot_bounds", HOT_FRAME))
    lanes = lay.frame("hot_lanes")
    if lanes and len(lanes) == 2:
        TOAST_LANE, BANNER_LANE = [(l[0], l[1], l[0] + l[2], l[1] + l[3]) for l in lanes]
    STAGE_X = tuple(lay.frame("stage_x", STAGE_X))
    HOT_SIZE = lay.frame("hot_size", HOT_SIZE)
    HUD_TOP = lay.hot_shape().get("top", HUD_TOP)
    colour = str((lay.d.get("hot_look") or {}).get("color", ""))
    if re.match(r"#[0-9a-fA-F]{6}$", colour):
        LIGHT = tuple(int(colour[k:k + 2], 16) for k in (1, 3, 5))

# The stand-ins the game borrows until a picture exists (bg_placeholders.rpy):
# name -> (picture, crop x, y, w, h or None, mirrored).
STAND_INS = {
    "library": ("classroom", (120, 60, 1280, 720), False),
    "utahime_office": ("dojo", (0, 40, 1120, 630), False),
    "gojo_office": ("dorm_common", None, True),
}

INK, PAPER, GOLD, VIOLET, SEAL = (7, 6, 12), (236, 231, 245), (255, 209, 102), (162, 89, 255), (232, 51, 79)
CYAN, GREY, GREEN = (90, 220, 230), (150, 150, 160), (110, 220, 140)
SLOT_COLOURS = [GOLD, CYAN, (255, 140, 200), GREEN]


# --- a 5x7 face, so a sheet can name what it draws without any font library -----------
# Five columns a glyph, the top row in the lowest bit.
FONT = {
    " ": "0000000000", "!": "00005F0000", "#": "147F147F14", "%": "2313086462", "&": "3649552250",
    "'": "0005030000", "(": "001C224100", ")": "0041221C00", "*": "14083E0814", "+": "08083E0808",
    ",": "0050300000", "-": "0808080808", ".": "0060600000", "/": "2010080402",
    "0": "3E5149453E", "1": "00427F4000", "2": "4261514946", "3": "2141454B31", "4": "1814127F10",
    "5": "2745454539", "6": "3C4A494930", "7": "0171090503", "8": "3649494936", "9": "064949291E",
    ":": "0036360000", "<": "0814224100", "=": "1414141414", ">": "0041221408", "?": "0201510906",
    "A": "7E1111117E", "B": "7F49494936", "C": "3E41414122", "D": "7F4141221C", "E": "7F49494941",
    "F": "7F09090901", "G": "3E4149497A", "H": "7F0808087F", "I": "00417F4100", "J": "2040413F01",
    "K": "7F08142241", "L": "7F40404040", "M": "7F020C027F", "N": "7F0408107F", "O": "3E4141413E",
    "P": "7F09090906", "Q": "3E4151215E", "R": "7F09192946", "S": "4649494931", "T": "01017F0101",
    "U": "3F4040403F", "V": "1F2040201F", "W": "3F4038403F", "X": "6314081463", "Y": "0708700807",
    "Z": "6151494543", "[": "007F414100", "]": "0041417F00", "_": "4040404040",
}


def text_size(s, scale=2):
    return len(s) * 6 * scale, 8 * scale


def fill(im, x0, y0, x1, y1, c, a=1.0):
    """A filled rectangle [x0, x1) x [y0, y1), see-through when a < 1."""
    x0, y0, x1, y1 = max(0, int(x0)), max(0, int(y0)), min(im.w, int(x1)), min(im.h, int(y1))
    if x1 <= x0 or y1 <= y0:
        return
    if a >= 1.0 and im.ch == 3:
        row = bytes(c) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * im.w + x0) * 3
            im.buf[i:i + len(row)] = row
        return
    for y in range(y0, y1):
        for x in range(x0, x1):
            im.blend(x, y, c, a)


def text(im, x, y, s, c=PAPER, scale=2, back=INK, back_a=0.8):
    """Capital letters, digits and a little punctuation, on a dark plate."""
    s = str(s).upper()
    w, h = text_size(s, scale)
    if back is not None:
        fill(im, x - 2 * scale, y - 2 * scale, x + w + scale, y + h + scale, back, back_a)
    for k, ch in enumerate(s):
        cols = FONT.get(ch, FONT["?"])
        for cx in range(5):
            bits = int(cols[cx * 2:cx * 2 + 2], 16)
            for cy in range(7):
                if bits >> cy & 1:
                    fill(im, x + (k * 6 + cx) * scale, y + cy * scale,
                         x + (k * 6 + cx + 1) * scale, y + (cy + 1) * scale, c)
    return w, h


def line(im, x0, y0, x1, y1, c, t=2, dash=0):
    """A straight line t pixels thick; dash > 0 draws that many on, that many off."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    h = t // 2
    for k in range(n + 1):
        if dash and (k // dash) % 2:
            continue
        x = x0 + (x1 - x0) * k // n
        y = y0 + (y1 - y0) * k // n
        fill(im, x - h, y - h, x - h + t, y - h + t, c)


def box(im, x, y, w, h, c, t=2, dash=0):
    """The outline of the rectangle at (x, y), w by h."""
    line(im, x, y, x + w, y, c, t, dash)
    line(im, x, y + h, x + w, y + h, c, t, dash)
    line(im, x, y, x, y + h, c, t, dash)
    line(im, x + w, y, x + w, y + h, c, t, dash)


def polygon(im, pts, c, a=0.30, t=3):
    """A see-through filled polygon with its outline and corners."""
    if len(pts) >= 3:
        im.poly([(float(x), float(y)) for x, y in pts], c, a)
    for k in range(len(pts)):
        (xa, ya), (xb, yb) = pts[k], pts[(k + 1) % len(pts)]
        line(im, xa, ya, xb, yb, c, t)
    for x, y in pts:
        fill(im, x - 5, y - 5, x + 5, y + 5, c)


def cross(im, x, y, c, r=10, t=2):
    line(im, x - r, y, x + r, y, c, t)
    line(im, x, y - r, x, y + r, c, t)


def ring(im, cx, cy, r, c, t=3):
    """A circle's outline, t pixels thick."""
    for k in range(int(8 * r)):
        a = k * math.pi / (4 * r)
        fill(im, cx + r * math.cos(a) - t / 2.0, cy + r * math.sin(a) - t / 2.0,
             cx + r * math.cos(a) + t / 2.0, cy + r * math.sin(a) + t / 2.0, c)


# --- pictures ----------------------------------------------------------------------
def rgb(im):
    if im.ch == 3:
        return im
    out = Img(im.w, im.h)
    for p in range(im.w * im.h):
        out.buf[p * 3:p * 3 + 3] = im.buf[p * 4:p * 4 + 3]
    return out


def nearest(im, w2, h2):
    """A quick resize: these are working sheets, and the stand-ins are blurry anyway."""
    if (im.w, im.h) == (w2, h2):
        return im
    out = Img(w2, h2)
    cols = [min(im.w - 1, x * im.w // w2) * 3 for x in range(w2)]
    for y in range(h2):
        src = min(im.h - 1, y * im.h // h2) * im.w * 3
        row = im.buf[src:src + im.w * 3]
        line_ = bytearray(w2 * 3)
        for x, c in enumerate(cols):
            line_[x * 3:x * 3 + 3] = row[c:c + 3]
        out.buf[y * w2 * 3:(y + 1) * w2 * 3] = line_
    return out


def mirror(im):
    out = Img(im.w, im.h)
    for y in range(im.h):
        row = im.buf[y * im.w * 3:(y + 1) * im.w * 3]
        flipped = bytearray(len(row))
        for x in range(im.w):
            flipped[(im.w - 1 - x) * 3:(im.w - x) * 3] = row[x * 3:x * 3 + 3]
        out.buf[y * im.w * 3:(y + 1) * im.w * 3] = flipped
    return out


def dim(im, f):
    table = bytes(int(v * f) for v in range(256))
    im.buf = bytearray(bytes(im.buf).translate(table))
    return im


def game_facts():
    """(place -> bg picture name, place -> display name, area key -> (anchor, places)), from the layout dump,
    so the sheet never keeps its own copy."""
    bgs = dict((p["key"], LAY.bg_stem(p["key"])) for p in LAY.d.get("places", []))
    names = dict((p["key"], p["name"]) for p in LAY.d.get("places", []))
    areas = dict((a["key"], (tuple(a["anchor"]), list(a["places"]))) for a in LAY.d.get("areas", []))
    return bgs, names, areas


def code_numbers():
    """The code's own numbers, from the dump, in the shape the sheets read: slots ({place: {"<n>": rows}}: the
    code's rows, else what the game answers), hotspots ({place: {id: [x, y]}}: every exit and registered
    hotspot at the code's point) and areas ({key: {place: [x, y]}})."""
    d = LAY.d
    slots = dict((place, (d.get("slots_code") or {}).get(place) or rows) for place, rows in (d.get("slots") or {}).items())
    hots = {}
    for place in (d.get("exits") or {}):
        hots[place] = dict((r["id"], r["default"]) for r in LAY.exits(place) + LAY.hotspots(place))
    areas = dict((a["key"], dict((l, sp["default"]) for l, sp in a["spots"].items())) for a in d.get("areas", []))
    return {"slots": slots, "hotspots": hots, "areas": areas}


BG_FILE = [None]        # --bg: a picture given by path, used for the day picture of the place


def place_picture(place, variant, bgs):
    """(picture at 1920x1080, a note on where it came from) for a room."""
    name = bgs.get(place)
    if name is None:
        raise SystemExit("no place %r in the game (the layout dump's `places`)" % place)
    if BG_FILE[0] and not variant:
        if not os.path.exists(BG_FILE[0]):
            raise SystemExit("no picture at %s" % BG_FILE[0])
        im = rgb(load(BG_FILE[0]))
        return nearest(im, W, H), "%s (%dx%d, given with --bg)" % (os.path.basename(BG_FILE[0]), im.w, im.h)
    tries = ([name + "_" + variant] if variant else []) + [name]
    for t in tries:
        p = os.path.join(BG, t + ".png")
        if os.path.exists(p):
            note = t + ".png"
            if variant and t == name:
                note += " (no %s picture: the day one)" % variant
            return nearest(rgb(load(p)), W, H), note
    if name in STAND_INS:
        src, box_, flip = STAND_INS[name]
        if os.path.exists(os.path.join(BG, src + ".png")):
            im = rgb(load(os.path.join(BG, src + ".png")))
            if box_:
                im = crop(im, box_[0], box_[1], box_[0] + box_[2], box_[1] + box_[3])
            im = nearest(im, W, H)
            if flip:
                im = mirror(im)
            return im, "%s.png not painted yet: stand-in from %s.png" % (name, src)
    return Img(W, H, fill=(40, 38, 50)), "%s.png not painted yet: no picture" % name


def area_picture(key, areas):
    p = os.path.join(BG, "area_%s.png" % key)
    if os.path.exists(p):
        return nearest(rgb(load(p)), W, H), "area_%s.png" % key
    if key not in areas:
        raise SystemExit("no area %r in the game (the layout dump's `areas`)" % key)
    # The game's stand-in (4.1): a 720x405 piece of the campus map around the
    # area's anchor, kept inside the picture, enlarged and darkened.
    (ax, ay), _places = areas[key]
    x0 = max(0, min(W - 720, ax - 360))
    y0 = max(0, min(H - 405, ay - 202))
    im = rgb(load(os.path.join(BG, "map_campus.png")))
    return dim(nearest(crop(im, x0, y0, x0 + 720, y0 + 405), W, H), 0.7), \
        "area_%s.png not painted yet: stand-in from map_campus.png" % key


# --- the three kinds of sheet --------------------------------------------------------
def slot_rect(slot):
    """(x, y, w, h) of the sprite canvas at a slot, as view_slot_rects has it."""
    xc, yoff, zoom = slot[0], slot[1], slot[2]
    w, h = int(round(SPRITE[0] * zoom)), int(round(SPRITE[1] * zoom))
    return int(round(xc - w / 2.0)), int(H + yoff - h), w, h


def header(sheet, title, notes):
    fill(sheet, 0, 0, sheet.w, 44, INK)
    w, _h = text(sheet, 16, 12, title, GOLD, 3, back=None)
    text(sheet, 16 + w + 30, 16, "   ".join(notes), PAPER, 2, back=None)


def view_sheet(place, code, side, fg, bgs, notes):
    code_slots = (code.get("slots") or {}).get(place) or {}
    side_slots = side.get("slots") or {}
    poses = side.get("poses") or {}
    floor = side.get("floor") if isinstance(side.get("floor"), dict) else {}
    scale = side.get("scale") if numbers(side.get("scale"), (3,)) else None
    variants = sorted(set(list(fg) + [k.split("__", 1)[1] if "__" in k else "" for k in poses]
                          + ([""] if floor or scale else [])))
    day, day_note = place_picture(place, "", bgs)

    sheet = Img(W, 44 + H + (H + 8) * len(variants))
    header(sheet, "view_" + place, notes + [day_note])

    # Four half-size panels: one to four people.
    half = nearest(day, W // 2, H // 2)
    for n in range(1, 5):
        ox, oy = ((n - 1) % 2) * (W // 2), 44 + ((n - 1) // 2) * (H // 2)
        panel = Img(W // 2, H // 2)
        panel.buf[:] = half.buf
        dim(panel, 0.8)
        slots = side_slots.get(str(n)) or code_slots.get(str(n)) or []
        where = "sidecar" if side_slots.get(str(n)) else "code"
        for x in STAGE_X:
            line(panel, x // 2, 0, x // 2, H // 2, GREY, 1, dash=6)
        for k, slot in enumerate(slots):
            c = SLOT_COLOURS[k % len(SLOT_COLOURS)]
            x, y, w, h = slot_rect(slot)
            far = len(slot) > 3 and slot[3]
            box(panel, x // 2, y // 2, w // 2, h // 2, c, 2, dash=(8 if far else 0))
            line(panel, x // 2 - 10, (H + slot[1]) // 2, (x + w) // 2 + 10, (H + slot[1]) // 2, c, 1)
            cross(panel, int(slot[0]) // 2, (H + slot[1]) // 2, c, 8, 2)
            text(panel, x // 2 + 6, y // 2 + 6, "%d  x %d" % (k + 1, slot[0]), c, 2)
            text(panel, x // 2 + 6, y // 2 + 28, "y %d  zoom %s%s" % (slot[1], slot[2], "  far" if far else ""), c, 1)
        text(panel, 12, 12, "%d %s  (%s)%s" % (n, "person" if n == 1 else "people", where,
                                             "" if slots else "  no slots"), PAPER, 2)
        if len(slots) != n and slots:
            text(panel, 12, 40, "%d slots for %d people" % (len(slots), n), SEAL, 2)
        box(panel, 0, 0, W // 2 - 1, H // 2 - 1, INK, 2)
        for y in range(H // 2):
            i = ((oy + y) * W + ox) * 3
            sheet.buf[i:i + (W // 2) * 3] = panel.buf[y * (W // 2) * 3:(y + 1) * (W // 2) * 3]

    # One full-size panel a picture that has pose boxes or a foreground polygon.
    for v, variant in enumerate(variants):
        pic, note = (day, day_note) if not variant else place_picture(place, variant, bgs)
        panel = Img(W, H)
        panel.buf[:] = pic.buf
        if not variant:
            # the room's own data (6.1): the floor people may stand on, the parts they may not, the scale
            for poly in floor.get("on") or []:
                polygon(panel, [(int(q[0]), int(q[1])) for q in poly], GREEN, 0.18, 2)
                text(panel, int(min(q[0] for q in poly)) + 8, int(max(q[1] for q in poly)) - 26, "floor: people may stand here", GREEN, 2)
            for poly in floor.get("off") or []:
                polygon(panel, [(int(q[0]), int(q[1])) for q in poly], SEAL, 0.28, 2)
                text(panel, int(min(q[0] for q in poly)) + 8, int(min(q[1] for q in poly)) + 8, "nobody stands here", SEAL, 2)
            if scale:
                sx, sy0, sy1 = int(scale[0]), int(scale[1]), int(scale[2])
                line(panel, sx, sy0, sx, sy1, VIOLET, 5)
                line(panel, sx - 14, sy0, sx + 14, sy0, VIOLET, 3)
                line(panel, sx - 14, sy1, sx + 14, sy1, VIOLET, 3)
                text(panel, sx + 18, (sy0 + sy1) // 2, "scale: 200 cm = %d px" % (sy1 - sy0), VIOLET, 2)
            if floor:
                # where each row's feet touch the ground, for one to four people
                for n in range(1, 5):
                    for slot in side_slots.get(str(n)) or code_slots.get(str(n)) or []:
                        fx, fy = int(slot[0]), int(H + slot[1] - (SPRITE[1] - 1365) * slot[2])
                        cross(panel, fx, fy, SLOT_COLOURS[(n - 1) % len(SLOT_COLOURS)], 9, 2)
            words = []
            if "talk" in side:
                words.append("talk: the foreground %s up in dialogue" % ("stays" if side["talk"] else "does not stay"))
            for key in ("slot_light", "cast"):
                if isinstance(side.get(key), dict) and side[key]:
                    words.append("%s: %s" % (key, ", ".join(sorted(k or "day" for k in side[key]))))
            if "for_rev" in side:
                words.append("for_rev %s" % side["for_rev"])
            for k, wline in enumerate(words):
                text(panel, 12, 40 + 26 * k, wline, PAPER, 2)
        if variant in fg:
            pts = [(int(p[0]), int(p[1])) for p in fg[variant]]
            polygon(panel, pts, CYAN)
            if pts:
                text(panel, min(p[0] for p in pts) + 8, min(p[1] for p in pts) + 8,
                     "foreground  %d points" % len(pts), CYAN, 2)
        for key in sorted(poses):
            who, _sep, pv = key.partition("__")
            if pv != variant:
                continue
            x, y, w, h = [int(q) for q in poses[key]]
            box(panel, x, y, w, h, GOLD, 3)
            box(panel, x + 24, y + 24, w - 48, h - 48, GOLD, 1, dash=6)     # inside the 24 px feather
            text(panel, x + 8, y + 8, "pose %s  %d,%d  %dx%d" % (who, x, y, w, h), GOLD, 2)
        text(panel, 12, 12, "%s  -  %s" % (variant or "day", note), PAPER, 2)
        oy = 44 + H + v * (H + 8) + 8
        sheet.buf[oy * W * 3:(oy + H) * W * 3] = panel.buf
    return sheet


SHAPE_COLOURS = [GOLD, CYAN, (255, 140, 200), GREEN, VIOLET, (255, 170, 90), (150, 200, 255), (230, 230, 120)]


def outline(im, shape, c, t=3, dash=0):
    """The outline of a shape: each of its polygons, closed."""
    for poly in shape:
        for k in range(len(poly)):
            (xa, ya), (xb, yb) = poly[k], poly[(k + 1) % len(poly)]
            line(im, xa, ya, xb, yb, c, t, dash)


def plate(x, y, w, hh, side, size=None):
    """(x, y) of a name plate w by hh against the square at (x, y), on `side`: game/sb_hotspots.rpy's
    hot_name_rect, the turn at the screen's edge included."""
    size = size or HOT_SIZE
    sx, sy = int(x) - size // 2, int(y) - size // 2
    if side == "left" and sx - w < 0:
        side = "right"
    elif side == "right" and sx + size + w > W:
        side = "left"
    elif side == "top" and sy - hh < 0:
        side = "bottom"
    elif side == "bottom" and sy + size + hh > H:
        side = "top"
    if side == "left":
        return sx - w, sy
    if side == "right":
        return sx + size, sy
    return max(0, min(sx, W - w)), (sy - hh if side == "top" else sy + size)


def hot_sheet(place, code, side, bgs, notes, extra=None):
    extra = extra or {}
    pic, note = place_picture(place, "", bgs)
    shapes = side.get("shapes") if isinstance(side.get("shapes"), dict) else {}
    shapes = dict((hid, sh) for hid, sh in shapes.items()
                  if isinstance(sh, list) and sh and all(isinstance(poly, list) and len(poly) >= 3
                                                         and all(numbers(q, (2,)) for q in poly) for poly in sh))
    keep = side.get("keep_tile") if isinstance(side.get("keep_tile"), dict) else {}
    tips = side.get("tips") if isinstance(side.get("tips"), dict) else {}
    sheet = Img(W, 44 + H + ((H + 8) if shapes else 0))
    panel = Img(W, H)
    panel.buf[:] = pic.buf
    # Where people stand, for one to four of them: a hotspot behind one is hidden.
    code_slots = (code.get("slots") or {}).get(place) or {}
    for n in range(1, 5):
        for slot in code_slots.get(str(n)) or []:
            x, y, w, h = slot_rect(slot)
            box(panel, x, y, w, h, GREY, 1, dash=5)
    x0, y0, x1, y1 = HOT_FRAME
    box(panel, x0, y0, x1 - x0, y1 - y0, GREEN, 2, dash=12)
    text(panel, x0 + 8, y1 - 26, "points stay inside this frame", GREEN, 2)
    for (lx0, ly0, lx1, ly1), label in ((TOAST_LANE, "toast lane"), (BANNER_LANE, "banner lane")):
        fill(panel, lx0, ly0, lx1, ly1, SEAL, 0.22)
        box(panel, lx0, ly0, lx1 - lx0, ly1 - ly0, SEAL, 2)
        text(panel, lx0 + 8, ly0 + 8, label + ": keep out", SEAL, 2)
    spots = dict((code.get("hotspots") or {}).get(place) or {})
    from_side = dict((k, v) for k, v in (side.get("spots") or {}).items() if numbers(v, (2,)))
    spots.update(from_side)
    front = set(LAY.front_ids(place)) | set(extra.get("front") or []) if LAY is not None else set(extra.get("front") or [])
    planned = set(pid for pid, _k in LAY.planned(place)) if LAY is not None else set()
    half = HOT_SIZE // 2
    colour = dict((hid, SHAPE_COLOURS[k % len(SHAPE_COLOURS)]) for k, hid in enumerate(sorted(shapes)))
    # the shapes' outlines, under the squares (D60): a front shape dashed
    for hid in sorted(shapes):
        outline(panel, shapes[hid], colour[hid], 3, dash=(10 if hid in front else 0))
    if shapes:
        line(panel, 0, HUD_TOP, W, HUD_TOP, GREY, 1, dash=8)
        text(panel, 12, HUD_TOP - 22, "above y %d no shape takes the pointer" % HUD_TOP, GREY, 2)
    for k, hid in enumerate(sorted(spots)):
        x, y = int(spots[hid][0]), int(spots[hid][1])
        c = colour.get(hid) or (GOLD if hid in from_side else CYAN)
        bad = not (x0 <= x <= x1 and y0 <= y <= y1) or any(
            lx0 - half < x < lx1 + half and ly0 - half < y < ly1 + half for lx0, ly0, lx1, ly1 in (TOAST_LANE, BANNER_LANE))
        box(panel, x - half, y - half, HOT_SIZE, HOT_SIZE, SEAL if bad else c, 3, dash=(6 if hid in shapes else 0))
        cross(panel, x, y, c, 12, 2)
        words = "%s  %d,%d%s" % (hid, x, y, "  out of bounds" if bad else "")
        if hid in planned:
            words += "  planned"
        if hid in front:
            words += "  front"
        if hid in keep:
            words += "  keeps its button"
        if tips.get(hid):
            words += "  name: %s" % tips[hid]
        text(panel, max(4, min(x - half, W - text_size(words, 2)[0] - 8)), y + half + 8, words, SEAL if bad else c, 2)
    for k, pt in enumerate(side.get("spare") or []):
        if numbers(pt, (2,)):
            x, y = int(pt[0]), int(pt[1])
            ring(panel, x, y, 30, VIOLET, 3)
            cross(panel, x, y, VIOLET, 8, 2)
            text(panel, x - 30, y + 38, "spare door %d  %d,%d" % (k + 1, x, y), VIOLET, 2)
    if not spots:
        text(panel, 60, 200, "no hotspots registered for this room yet", PAPER, 3)
    legend = "gold: from the sidecar   blue: from the code   grey: where people stand"
    if shapes:
        legend = ("each shape's outline in its hotspot's colour (dashed: in front of the people). The 72 px square at its "
                  "point takes no pointer")
    text(panel, 12, 12, legend, PAPER, 2)
    header(sheet, "hot_" + place, notes + [note])
    sheet.buf[44 * W * 3:(44 + H) * W * 3] = panel.buf
    if shapes:
        # the second frame: every shape lit and named, as while names are shown
        lit = Img(W, H)
        lit.buf[:] = pic.buf
        dim(lit, 0.72)
        order = sorted(shapes, key=lambda hid: -sum(abs(sum(poly[k][0] * poly[(k + 1) % len(poly)][1]
                                                                - poly[(k + 1) % len(poly)][0] * poly[k][1]
                                                                for k in range(len(poly)))) / 2.0 for poly in shapes[hid]))
        for hid in order:                                   # the largest first: the smaller shape is on top
            for poly in shapes[hid]:
                lit.poly([(float(q[0]), float(q[1])) for q in poly], LIGHT, 0.34)
        for hid in order:
            outline(lit, shapes[hid], INK, 4)
            outline(lit, shapes[hid], LIGHT, 2)
        names = dict((pp["key"], pp["name"]) for pp in LAY.d.get("places", [])) if LAY is not None else {}
        exits = dict((e["id"], e["to"]) for e in LAY.exits(place)) if LAY is not None else {}
        for hid in sorted(shapes):
            if hid not in spots:
                continue
            x, y = int(spots[hid][0]), int(spots[hid][1])
            name = ("to %s" % names.get(exits[hid], exits[hid])) if hid in exits else hid.replace("_", " ")
            tw, th = text_size(name, 2)
            sidew = tips.get(hid) if tips.get(hid) in ("top", "bottom", "left", "right") else ("top" if hid in exits else "left")
            px, py = plate(x, y, tw + 10, th + 10, sidew)
            box(lit, x - half, y - half, HOT_SIZE, HOT_SIZE, GREY, 1, dash=4)
            text(lit, px + 6, py + 6, name, PAPER, 2, back=INK, back_a=0.85)
        for hid in sorted(keep):
            if hid in spots:
                x, y = int(spots[hid][0]), int(spots[hid][1])
                box(lit, x - half, y - half, HOT_SIZE, HOT_SIZE, GOLD, 3)
                text(lit, x - half, y + half + 8, "%s keeps its button: %s" % (hid, keep[hid]), GOLD, 2)
        text(lit, 12, 12, "every shape lit and named, as while names are shown (%d shape%s). A name opens against the square "
             "at its point, on its tips side" % (len(shapes), "" if len(shapes) == 1 else "s"), PAPER, 2)
        oy = 44 + H + 8
        sheet.buf[oy * W * 3:(oy + H) * W * 3] = lit.buf
    return sheet


def area_sheet(key, code, side, areas, names, notes):
    pic, note = area_picture(key, areas)
    sheet = Img(W, 44 + H)
    panel = Img(W, H)
    panel.buf[:] = pic.buf
    x0, y0, x1, y1 = PIN_FRAME
    box(panel, x0, y0, x1 - x0, y1 - y0, GREEN, 2, dash=12)
    text(panel, x0 + 8, y1 - 26, "pins stay inside this frame", GREEN, 2)
    spots = dict((code.get("areas") or {}).get(key) or {})
    from_side = side.get("spots") or {}
    spots.update(from_side)
    for loc in sorted(spots):
        x, y = int(spots[loc][0]), int(spots[loc][1])
        c = GOLD if loc in from_side else CYAN
        bad = not (x0 <= x <= x1 and y0 <= y <= y1)
        panel.ellipse(x, y, 36, 36, INK, 0.6)                # the 72 px disc
        ring(panel, x, y, 36, SEAL if bad else c)
        cross(panel, x, y, c, 10, 2)
        label = "%s  %d,%d%s" % (names.get(loc, loc), x, y, "  out of bounds" if bad else "")
        tw, _th = text_size(label, 2)
        text(panel, x - tw // 2, y + 46, label, SEAL if bad else c, 2)
    if not spots:
        text(panel, 240, 240, "no pins for this area yet", PAPER, 3)
    text(panel, 12, 12, "gold: from the sidecar   blue: from the code", PAPER, 2)
    header(sheet, "area_" + key, notes + [note])
    sheet.buf[44 * W * 3:] = panel.buf
    return sheet


def short(path):
    """A path as the sheet prints it: from the project when it is inside it."""
    path = os.path.abspath(path)
    if path.startswith(ROOT + os.sep):
        return os.path.relpath(path, ROOT)
    return os.path.join("...", os.path.basename(os.path.dirname(path)), os.path.basename(path))


def read_json(path, what):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s %s is not JSON: %s" % (what, path, e))
    if not isinstance(data, dict):
        raise SystemExit("%s %s must be a JSON object" % (what, path))
    return data


def numbers(v, counts):
    """True when v is a list of numbers whose length is one of counts."""
    return (isinstance(v, list) and len(v) in counts
            and all(isinstance(q, (int, float)) and not isinstance(q, bool) for q in v))


def check_shapes(kind, data, path, fg=False):
    """Stop with a plain message, not a traceback, when a sidecar (or a
    foreground file) doesn't have the shape the header gives."""
    def bad(what):
        raise SystemExit("%s: %s" % (path, what))
    if fg:
        for variant, pts in data.items():
            if not isinstance(pts, list) or not all(numbers(q, (2,)) for q in pts):
                bad("%r must be a list of [x, y] points" % variant)
        return
    allowed = {"hot": ("spots", "tips", "shapes", "keep_tile", "spare", "for_rev"),
               "area": ("spots", "for_rev"),
               "view": ("slots", "poses", "floor", "scale", "slot_light", "cast", "talk", "for_rev")}[kind]
    for k in data:
        if k not in allowed:
            bad("unknown key %r (a %s sidecar holds %s)" % (k, kind, ", ".join(allowed)))
    if kind in ("hot", "area"):
        spots = data.get("spots", {})
        if not isinstance(spots, dict):
            bad("spots must be an object, {\"<id>\": [x, y]}")
        for k, v in spots.items():
            if not numbers(v, (2,)):
                bad("spots[%r] must be [x, y]" % k)
        shapes = data.get("shapes", {})
        if not isinstance(shapes, dict):
            bad("shapes must be an object, {\"<id>\": [polygon, ...]}")
        for k, v in shapes.items():
            if not (isinstance(v, list) and v and all(isinstance(poly, list) and len(poly) >= 3
                                                      and all(numbers(q, (2,)) for q in poly) for poly in v)):
                bad("shapes[%r] must be a list of polygons, each a list of three or more [x, y] points" % k)
        if not isinstance(data.get("keep_tile", {}), dict):
            bad("keep_tile must be an object, {\"<id>\": \"<why it keeps its button>\"}")
        if not isinstance(data.get("tips", {}), dict):
            bad("tips must be an object, {\"<id>\": \"top\", \"bottom\", \"left\" or \"right\"}")
        if not (isinstance(data.get("spare", []), list) and all(numbers(q, (2,)) for q in data.get("spare", []))):
            bad("spare must be a list of [x, y] points")
        return
    floor = data.get("floor", {})
    if not (isinstance(floor, dict) and all(k in ("on", "off") and isinstance(v, list) and all(
            isinstance(poly, list) and len(poly) >= 3 and all(numbers(q, (2,)) for q in poly) for poly in v)
            for k, v in floor.items())):
        bad("floor must be {\"on\": [polygons], \"off\": [polygons]}, a polygon being three or more [x, y] points")
    if "scale" in data and not numbers(data["scale"], (3,)):
        bad("scale must be [x, y top, y bottom]")
    slots, poses = data.get("slots", {}), data.get("poses", {})
    if not isinstance(slots, dict):
        bad("slots must be an object, {\"<n>\": [[xcenter, yoffset, zoom, far], ...]}")
    for n, rows in slots.items():
        if n not in ("1", "2", "3", "4"):
            bad("slots[%r]: the key is how many people stand there, \"1\" to \"4\"" % n)
        if not isinstance(rows, list) or not all(numbers(r, (3, 4)) for r in rows):
            bad("slots[%r] must be a list of [xcenter, yoffset, zoom] or [xcenter, yoffset, zoom, far]" % n)
        if len(rows) != int(n):
            bad("slots[%r] must hold %s slot%s, not %d" % (n, n, "" if n == "1" else "s", len(rows)))
    if not isinstance(poses, dict):
        bad("poses must be an object, {\"<who>\": [x, y, w, h]}")
    for k, v in poses.items():
        if not numbers(v, (4,)):
            bad("poses[%r] must be [x, y, w, h]" % k)


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

    dump = game_layout.pop_dump_arg(argv)
    sidecar, fg_path = opt("--sidecar"), opt("--fg")
    staged, bg = opt("--staged"), opt("--bg")
    out = opt("--out")
    if opt("--defaults"):
        print("layout_sheet.py: --defaults is no longer read: the code's numbers come from the layout dump (--layout-dump)")
    no_side = "--no-sidecar" in argv
    names_ = [a for a in argv if not a.startswith("--")]
    if len(names_) != 1 or [a for a in argv if a.startswith("--") and a != "--no-sidecar"]:
        print(__doc__); raise SystemExit(1)
    name = names_[0]
    kind, _sep, key = name.partition("_")
    if kind not in ("view", "hot", "area") or not key:
        raise SystemExit("%r is not a layout name: view_<place>, hot_<place> or area_<key>" % name)
    if staged and sidecar:
        raise SystemExit("--staged and --sidecar both name the layout's file: give one")
    if staged and not os.path.isdir(staged):
        raise SystemExit("no staged folder at %s" % staged)

    use_dump(game_layout.load(dump))
    code = code_numbers()
    BG_FILE[0] = os.path.expanduser(bg) if bg else None
    if bg and kind == "area":
        raise SystemExit("--bg gives a place's picture: an area sheet draws game/images/bg/area_<key>.png")

    notes = []
    side, extra = {}, {}
    if staged:
        sidecar = os.path.join(staged, name + ".json")
        more = os.path.join(staged, "check_%s.json" % key)
        if os.path.exists(more):
            extra = read_json(more, "the check file")
    if not no_side:
        path = sidecar or os.path.join(ROOT, "game", "layout", name + ".json")
        if sidecar and not os.path.exists(path):
            raise SystemExit("no sidecar at %s" % path)
        if os.path.exists(path):
            side = read_json(path, "the sidecar")
            check_shapes(kind, side, short(path))
            notes.append("%s %s" % ("staged" if staged else "sidecar", short(path)))
    if not side:
        notes.append("the code's numbers (no sidecar)")
    if BG_FILE[0]:
        notes.append("picture %s (--bg)" % os.path.basename(BG_FILE[0]))

    bgs, names, areas = game_facts()
    if kind == "area":
        sheet = area_sheet(key, code, side, areas, names, notes)
    elif kind == "hot":
        if staged and os.path.exists(os.path.join(staged, "view_%s.json" % key)):
            # the grey boxes are where people stand in THIS layout
            view = read_json(os.path.join(staged, "view_%s.json" % key), "the staged view file")
            if isinstance(view.get("slots"), dict):
                code = dict(code, slots=dict(code["slots"], **{key: dict(code["slots"].get(key) or {}, **view["slots"])}))
        sheet = hot_sheet(key, code, side, bgs, notes, extra)
    else:
        fg = {}
        path = fg_path or os.path.join(ROOT, "tools", "fg", key + ".json")
        if fg_path and not os.path.exists(path):
            raise SystemExit("no foreground file at %s" % path)
        if isinstance(extra.get("fg"), dict) and not fg_path:
            fg = extra["fg"]
            check_shapes(kind, fg, "check_%s.json (fg)" % key, fg=True)
            notes.append("foreground from check_%s.json" % key)
        elif os.path.exists(path):
            fg = read_json(path, "the foreground file")
            check_shapes(kind, fg, short(path), fg=True)
            notes.append("foreground %s" % short(path))
        sheet = view_sheet(key, code, side, fg, bgs, notes)

    out = out or os.path.join(ROOT, "shots", "layout", name + ("__staged" if staged else "__sidecar" if sidecar else "") + ".png")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out)
    print("%s  %dx%d  %s" % (name, sheet.w, sheet.h, "; ".join(notes)))
    print("sheet -> %s" % out)
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
