"""
Draw a layout on its background, to look at before it is approved.

    python3 tools/layout_sheet.py view_dorm_common      # where people stand, pose boxes, foreground
    python3 tools/layout_sheet.py hot_dorm_common       # the room's hotspots
    python3 tools/layout_sheet.py area_school           # the map pins of an area

    python3 tools/layout_sheet.py view_dorm_common --sidecar some/view_dorm_common.json
    python3 tools/layout_sheet.py view_dorm_common --fg some/dorm_common.json
    python3 tools/layout_sheet.py view_dorm_common --no-sidecar --out shots/layout/x.png

The name is a layout's full stem, as `rule_layout(name)` takes it in the game
(PHASE2_DESIGN.md D5, 6.1). What is drawn is what the game would use: the
code's own numbers, with the sidecar's laid over them.

  * The code's numbers come from `shots/layout/defaults.json`, which the
    harness writes: `tools/smoke.sh tools/smoke/p2_contracts.rpy` (run it again
    after the code's numbers change).
  * The sidecar is `game/layout/<name>.json` when it exists, or the file given
    with --sidecar; --no-sidecar draws the code's numbers alone.
        area_<key>.json    {"spots": {"<loc>": [x, y]}}
        view_<place>.json  {"slots": {"<n>": [[xcenter, yoffset, zoom, far], ...]},
                            "poses": {"<who>" or "<who>__<variant>": [x, y, w, h]}}
        hot_<place>.json   {"spots": {"<hotspot id>": [x, y]}}
  * Foreground polygons are tool input, never read by the game:
    `tools/fg/<place>.json` (or --fg): {"<variant, or "" for the day picture>":
    [[x, y], ...]}. A view sheet draws them.

A view sheet is four half-size panels (one, two, three and four people: the
sprite's box at each slot, with its feet line), then one full-size panel for
each picture that has pose boxes or a foreground polygon. A hotspot sheet
shows each 72 px button, the frame hotspots must stay inside, the two lanes
they must stay out of, and where people stand. An area sheet shows each
72 px pin with its room, and the frame pins must stay inside.

The picture is the place's own (`game/images/bg/`), or, while that isn't
painted yet, the same stand-in the game borrows; the sheet says which. Writes
`shots/layout/<name>.png` (`<name>__sidecar.png` with --sidecar), or --out.
Pure Python: raster.py and pngread.py.
"""
import sys, os, re, json, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, crop

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = os.path.join(ROOT, "game", "images", "bg")
W, H = 1920, 1080
SPRITE = (760, 1400)                     # the sprite canvas (view_stage.rpy, VIEW_SPRITE)

# What the validators allow (PHASE2_DESIGN.md 4.1, 4.10, R6).
PIN_FRAME = (200, 200, 1700, 940)
HOT_FRAME = (40, 180, 1700, 1000)
TOAST_LANE = (1330, 92, 1790, 350)
BANNER_LANE = (400, 96, 1300, 170)
STAGE_X = (40, 1700)

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
    """(place -> bg picture name, place -> display name, area key -> (anchor, places))
    read from game/sb_world.rpy, so the sheet never keeps its own copy."""
    src = open(os.path.join(ROOT, "game", "sb_world.rpy"), encoding="utf-8").read()
    bgs, names = {}, {}
    for m in re.finditer(r'"(\w+)":\s*dict\(\s*indoor=\w+,\s*name="([^"]*)",\s*bg="bg (\w+)"', src):
        bgs[m.group(1)], names[m.group(1)] = m.group(3), m.group(2)
    areas = {}
    for m in re.finditer(r'dict\(key="(\w+)",.*?places=\[([^\]]*)\],\s*anchor=\((\d+),\s*(\d+)\)', src, re.S):
        areas[m.group(1)] = ((int(m.group(3)), int(m.group(4))), re.findall(r'"(\w+)"', m.group(2)))
    return bgs, names, areas


def place_picture(place, variant, bgs):
    """(picture at 1920x1080, a note on where it came from) for a room."""
    name = bgs.get(place)
    if name is None:
        raise SystemExit("no place %r in game/sb_world.rpy (LOCATIONS)" % place)
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
        raise SystemExit("no area %r in game/sb_world.rpy (AREAS)" % key)
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
    variants = sorted(set(list(fg) + [k.split("__", 1)[1] if "__" in k else "" for k in poses]))
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


def hot_sheet(place, code, side, bgs, notes):
    pic, note = place_picture(place, "", bgs)
    sheet = Img(W, 44 + H)
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
    text(panel, x0 + 8, y1 - 26, "hotspots stay inside this frame", GREEN, 2)
    for (lx0, ly0, lx1, ly1), label in ((TOAST_LANE, "toast lane"), (BANNER_LANE, "banner lane")):
        fill(panel, lx0, ly0, lx1, ly1, SEAL, 0.22)
        box(panel, lx0, ly0, lx1 - lx0, ly1 - ly0, SEAL, 2)
        text(panel, lx0 + 8, ly0 + 8, label + ": keep out", SEAL, 2)
    spots = dict((code.get("hotspots") or {}).get(place) or {})
    from_side = side.get("spots") or {}
    spots.update(from_side)
    for k, hid in enumerate(sorted(spots)):
        x, y = int(spots[hid][0]), int(spots[hid][1])
        c = GOLD if hid in from_side else CYAN
        bad = not (x0 <= x <= x1 and y0 <= y <= y1) or any(
            lx0 - 36 < x < lx1 + 36 and ly0 - 36 < y < ly1 + 36 for lx0, ly0, lx1, ly1 in (TOAST_LANE, BANNER_LANE))
        box(panel, x - 36, y - 36, 72, 72, SEAL if bad else c, 3)
        cross(panel, x, y, c, 12, 2)
        text(panel, x - 36, y + 44, "%s  %d,%d%s" % (hid, x, y, "  out of bounds" if bad else ""),
             SEAL if bad else c, 2)
    if not spots:
        text(panel, 60, 200, "no hotspots registered for this room yet", PAPER, 3)
    text(panel, 12, 12, "gold: from the sidecar   blue: from the code   grey: where people stand", PAPER, 2)
    header(sheet, "hot_" + place, notes + [note])
    sheet.buf[44 * W * 3:] = panel.buf
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
    allowed = ("spots",) if kind in ("hot", "area") else ("slots", "poses")
    for k in data:
        if k not in allowed:
            bad("unknown key %r (a %s sidecar holds %s)" % (k, kind, " and ".join(allowed)))
    if kind in ("hot", "area"):
        spots = data.get("spots", {})
        if not isinstance(spots, dict):
            bad("spots must be an object, {\"<id>\": [x, y]}")
        for k, v in spots.items():
            if not numbers(v, (2,)):
                bad("spots[%r] must be [x, y]" % k)
        return
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

    sidecar, fg_path = opt("--sidecar"), opt("--fg")
    out, defaults = opt("--out"), opt("--defaults")
    no_side = "--no-sidecar" in argv
    names_ = [a for a in argv if not a.startswith("--")]
    if len(names_) != 1 or [a for a in argv if a.startswith("--") and a != "--no-sidecar"]:
        print(__doc__); raise SystemExit(1)
    name = names_[0]
    kind, _sep, key = name.partition("_")
    if kind not in ("view", "hot", "area") or not key:
        raise SystemExit("%r is not a layout name: view_<place>, hot_<place> or area_<key>" % name)

    defaults = defaults or os.path.join(ROOT, "shots", "layout", "defaults.json")
    if not os.path.exists(defaults):
        raise SystemExit("no %s -- write it with: tools/smoke.sh tools/smoke/p2_contracts.rpy" % defaults)
    code = read_json(defaults, "the defaults file")

    notes = []
    side = {}
    if not no_side:
        path = sidecar or os.path.join(ROOT, "game", "layout", name + ".json")
        if sidecar and not os.path.exists(path):
            raise SystemExit("no sidecar at %s" % path)
        if os.path.exists(path):
            side = read_json(path, "the sidecar")
            check_shapes(kind, side, short(path))
            notes.append("sidecar %s" % short(path))
    if not side:
        notes.append("the code's numbers (no sidecar)")

    bgs, names, areas = game_facts()
    if kind == "area":
        sheet = area_sheet(key, code, side, areas, names, notes)
    elif kind == "hot":
        sheet = hot_sheet(key, code, side, bgs, notes)
    else:
        fg = {}
        path = fg_path or os.path.join(ROOT, "tools", "fg", key + ".json")
        if fg_path and not os.path.exists(path):
            raise SystemExit("no foreground file at %s" % path)
        if os.path.exists(path):
            fg = read_json(path, "the foreground file")
            check_shapes(kind, fg, short(path), fg=True)
            notes.append("foreground %s" % short(path))
        sheet = view_sheet(key, code, side, fg, bgs, notes)

    out = out or os.path.join(ROOT, "shots", "layout", name + ("__sidecar" if sidecar else "") + ".png")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out)
    print("%s  %dx%d  %s" % (name, sheet.w, sheet.h, "; ".join(notes)))
    print("sheet -> %s" % out)
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
