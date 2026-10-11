"""
Draw a place as the game would, with the people standing in it: what a room is
judged on BEFORE its picture or its layout is installed.

    tools/py_art.sh tools/stage_preview.py dorm_common                       # the sheet, shots/stage/dorm_common.jpg
    tools/py_art.sh tools/stage_preview.py dorm_common evening --who megumi,yuji:happy,maki
    tools/py_art.sh tools/stage_preview.py courtyard --bg ~/ComfyUI-Shared/output/look2_courtyard_gateway_00001_.png \
            --staged tools/art/staged/courtyard                              # a picture and a layout that are only staged
    tools/py_art.sh tools/stage_preview.py dorm_common evening --who megumi,yuji,maki --plain \
            --beside shots/stage_ref/common_evening_3.png                    # laid beside a game screenshot

  <place>      a place's key, or its picture's name
  [hour]       day (the afternoon), morning, noon, afternoon, evening, night. With an hour, ONE frame is drawn at
               full size (shots/stage/<place>_<hour>.jpg); with none, the SHEET: one to four people by day and a
               frame for each hour, at half size, and for a shaped place two frames more, at full size
  --who a,b,c  who stands there, in stage order (one to four; "yuji:happy" names an expression; `none` for the
               empty room). Without it: whoever the timetable puts there at that hour on a weekday, else the
               first of the cast
  --bg <file>  the picture to draw on, of any size (a 2752 px render is fitted as the installer fits it). It
               stands for the picture of the hour asked for: for the evening or the night it is taken as that
               hour's own painted picture, so no tint is laid on it
  --staged <folder>   read hot_<place>.json, view_<place>.json, light_<place>.json and check_<place>.json from
               a folder such as tools/art/staged/<stem>/ before the game's own
  --dialogue   the scene case: the people as a story scene stands them (23% larger, feet on the bottom edge)
  --plain      no rings, outlines or labels: only what the game itself draws (to lay beside a screenshot)
  --beside <screenshot>   one sheet, the game's screenshot on the left and this drawing on the right
  --out <file>  --root <a copy of the project>  --layout-dump <file>

docs/UI2_DESIGN.md 6.2 and 6.5; D60 for a shaped place. WHAT IS DRAWN, in the game's own order
(game/sb_screens.rpy `sb_place`, game/view_stage.rpy, game/lighting.rpy, game/sb_world.rpy `graded_bg`):

  1. the picture for the hour: the hour's own painted picture when the place has one, else the day picture
     under the hour's tint (the dump's `grade`; brightness first, then the tint);
  2. the ink wash over it (10% of #07060c);
  3. each exit as its 72 px tile and each thing to do as a ring at its point, behind the people (--plain: none);
     FOR A SHAPED PLACE (its hot_ file holds `shapes`): each shape's outline instead, a front one dashed;
  4. the people, the furthest back first: the sprite at its slot's zoom, feet on the slot's floor line, its
     contact shadow under the soles at the room's shadow opacity, the room's light over both (brightness, then
     saturation, then tint), and a step back a little softer and 2% darker;
  5. the foreground the far people stand behind, cut from the room's own picture and tinted and washed like
     it; with --bg it is cut from that picture by the outline in tools/fg/<place>.json (or the staged
     check_<place>.json `fg`);
  6. the front things to do, over the foreground;
  7. the name tags on their line (y 1036), laid out as the game lays them.
  A SHAPED PLACE gets a second frame: every shape lit (the game's light: #fff0cc at 30%, its edge at 85%) and
  named where the game draws each name while names are shown (against the 72 px square at its point, on its
  `tips` side: check_layout.name_rect, the game's hot_name_rect), so two names that would meet are seen meeting.

THE LIGHT is the game's for that place and hour: the measured row of light_<place>.json (the staged one first)
for a painted picture, else the game's own table (the dump's `light`). With --bg and no measured row, the row
is measured on the given picture, as the installer would write it (tools/sample_light.py), and the sheet says so.

NOT DRAWN, because the game does not draw them yet (wave 1): the shadow's lean and stretch, a light of its own
for one standing spot (`slot_light`), a long cast shadow outdoors (`cast`), someone painted into the room (a
pose), the HUD. Breathing and blinking are motion. Nobody is ever drawn in water: the people are the game's
own dressed sprites, standing where the layout stands them (K16).

The game's numbers come from the layout dump (tools/game_layout.py); in a worktree, --layout-dump <file>.
Nothing is written but the sheet. Exit status 0, or 2 when the dump is out of date.
numpy and Pillow: started with plain python3 it starts itself again through tools/py_art.sh.
"""
import sys, os

TOOLS = os.path.dirname(os.path.abspath(__file__))
try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    import scipy                        # noqa: F401  (redo_measure needs it)
except ImportError:
    if os.environ.get("JJK_PY_ART"):
        raise SystemExit("numpy, scipy and Pillow are needed, and tools/py_art.sh's Python does not have them")
    os.execv("/bin/bash", ["/bin/bash", os.path.join(TOOLS, "py_art.sh"), os.path.abspath(__file__)] + sys.argv[1:])

import json

sys.path.insert(0, TOOLS)
import game_layout
import check_layout
import redo_measure as rm
import sample_light

ROOT = os.path.dirname(TOOLS)
W, H = rm.W, rm.H
INK = (0x07, 0x06, 0x0c)            # gui.ink
PAPER = (240, 236, 220)
GOLD = (255, 209, 102)
VIEW_INK = 0.10                     # sb_place: `add Solid(gui.ink) alpha 0.10`
FAR_BLUR, FAR_DIM = 0.8, 0.02       # view_stage.rpy: VIEW_FAR_BLUR, VIEW_FAR_DIM
SOLE = 1365                         # the sole row of every sprite canvas (the dump's people[].feet[1])
DAY_HOURS = ("Morning", "Noon", "Afternoon")        # lighting.rpy: LIGHT_DAY_HOURS
HOUR_WORDS = {"day": "Afternoon", "morning": "Morning", "noon": "Noon", "afternoon": "Afternoon",
              "evening": "Evening", "night": "Night"}
# jjk_defs.rpy: pos_c, pos_l and pos_r, pos_cl and pos_cr with the outer two (xalign, zoom)
DIALOGUE = {1: [(0.50, 0.64)], 2: [(0.17, 0.62), (0.83, 0.62)], 3: [(0.17, 0.62), (0.50, 0.64), (0.83, 0.62)],
            4: [(0.17, 0.62), (0.35, 0.62), (0.65, 0.62), (0.83, 0.62)]}
STOCK = ("megumi", "nobara", "yuji", "maki", "toge", "panda")


# ---- colour, as the game's matrices do it ---------------------------------------------------------------------
def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def grade(a, tint, bright):
    """TintMatrix(tint) * BrightnessMatrix(bright): the right-hand one first. `a` is 0..1."""
    return (a + bright) * hex_rgb(tint)


def lit(a, row):
    """light_matrix: TintMatrix * SaturationMatrix * BrightnessMatrix, the right-hand one first."""
    a = a + row[1]
    lum = (a * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(axis=-1, keepdims=True)
    a = lum + (a - lum) * row[2]
    return a * hex_rgb(row[0])


def ink(a, amount):
    return a * (1.0 - amount) + np.array(INK, np.float32) / 255.0 * amount


def to_image(a):
    return Image.fromarray(np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")


def read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s is not JSON: %s" % (path, e))


def font(size, bold=False):
    for name in (("ShipporiMincho-Bold.ttf",) if bold else ("ZenKakuGothicNew-Medium.ttf", "ZenKakuGothicNew-Regular.ttf")):
        p = os.path.join(ROOT, "game", "fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except (IOError, OSError):
                pass
    return ImageFont.load_default()


# ---- the room ---------------------------------------------------------------------------------------------------
class Room(object):
    """One place, with whatever is staged laid over what the game has."""

    def __init__(self, lay, place, root, staged=None, bg=None):
        self.lay, self.place, self.root, self.staged, self.bg = lay, place, root, staged, bg
        self.stem = lay.bg_stem(place)
        self.notes = []
        self.hot = self._file("hot") or {}
        self.view = self._file("view") or {}
        self.light = self._file("light") or {}
        self.extra = read_json(os.path.join(staged, "check_%s.json" % place)) if staged else None
        self.extra = self.extra or {}
        self.sprite = tuple(lay.frame("sprite", [760, 1400]))
        self._sampled = {}

    def _file(self, kind):
        name = "%s_%s.json" % (kind, self.place)
        if self.staged and os.path.exists(os.path.join(self.staged, name)):
            self.notes.append("%s from the staged folder" % name)
            return read_json(os.path.join(self.staged, name))
        return read_json(os.path.join(self.root, "game", "layout", name))

    # -- the picture
    def variant(self, period):
        return (self.lay.place(self.place).get("variants") or {}).get(period) or ""

    def picture(self, period):
        """(the picture as 0..1, the variant it is, words saying what it is)."""
        v = self.variant(period)
        if self.bg:
            own = "evening" if period == "Evening" else ("night" if period == "Night" else "")
            a = rm.load(self.bg)[0] / 255.0
            return a, own, "%s, taken as the %s picture" % (os.path.basename(self.bg), own or "day")
        path = self.lay.bg_path(self.place, v, self.root)
        if v and not os.path.exists(path):
            v, path = "", self.lay.bg_path(self.place, "", self.root)
        if not os.path.exists(path):
            raise SystemExit("no picture at %s: give one with --bg" % path)
        return rm.load(path)[0] / 255.0, v, "the game's %s" % os.path.basename(path)

    def room_grade(self, period, v):
        """(tint, brightness) graded_bg lays on the picture at this hour."""
        if v:
            return ("#ffd8b8", -0.04) if (v == "night" and period == "Evening") else ("#ffffff", 0.0)
        table = self.lay.d.get("grade", {}).get("indoor" if self.lay.indoor(self.place) else "outdoor", {})
        row = table.get(period, ["#ffffff", 0.0])
        return row[0], row[1]

    def light_row(self, period, v, picture):
        """(the row, where it came from): light_for_place."""
        tables = self.lay.d.get("light", {})
        if v or period in DAY_HOURS:
            row = self.light.get(v)
            if isinstance(row, list) and len(row) in (4, 6):
                return row, "the measured row of light_%s.json" % self.place
            if self.bg:
                if v not in self._sampled:
                    self._sampled[v] = sample_light.sample(picture * 255.0, self.lay, self.place)
                return self._sampled[v], "measured on this picture, as the installer would write it"
        place_rows = tables.get("place", {})
        for key in ("%s %s" % (self.place, v) if v else None, self.place):
            if key and key in place_rows:
                return place_rows[key], "the game's own row for the place"
        row = tables.get("indoor" if self.lay.indoor(self.place) else "outdoor", {}).get(period)
        return (row or tables.get("neutral") or ["#ffffff", 0.0, 1.0, 0.55]), "the game's general row for the hour"

    # -- where people stand
    def slots(self, n):
        rows = (self.view.get("slots") or {}).get(str(n))
        if isinstance(rows, list) and len(rows) == n and all(isinstance(r, list) and len(r) in (3, 4) for r in rows):
            return [(r[0], r[1], r[2], int(r[3]) if len(r) > 3 else 0) for r in rows]
        rows = self.lay.slots(self.place).get(str(n)) or []
        return [(r[0], r[1], r[2], int(r[3]) if len(r) > 3 else 0) for r in rows]

    # -- what can be clicked
    def points(self):
        """[{kind, id, name, at, front}] with the staged points laid over the game's."""
        spots = self.hot.get("spots") or {}
        front = set(self.lay.front_ids(self.place)) | set(self.extra.get("front") or [])
        out = []
        for p in self.lay.points(self.place, self.root):
            at = spots.get(p["id"], p["at"])
            out.append(dict(p, at=(at[0], at[1]), front=p["id"] in front))
        seen = set(p["id"] for p in out)
        for pid, _kind in self.lay.planned(self.place):
            if pid not in seen and isinstance(spots.get(pid), list):
                out.append({"kind": "hotspot", "id": pid, "name": "the planned hotspot %s" % pid,
                            "at": (spots[pid][0], spots[pid][1]), "front": pid in front})
        return out

    def shapes(self):
        got = self.hot.get("shapes")
        if isinstance(got, dict) and got:
            return got
        return self.lay.shapes(self.place)

    # -- the foreground
    def foreground(self, v, picture):
        """The foreground layer as RGBA 0..1 (not yet tinted), or None."""
        poly = (self.extra.get("fg") or {})
        polys = dict(read_json(os.path.join(self.root, "tools", "fg", self.place + ".json")) or {}, **poly)
        if self.bg or poly:
            pts = polys.get(v) or polys.get("")
            if not pts:
                return None
            m = Image.new("L", (W * 2, H * 2), 0)
            ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
            alpha = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
            return np.dstack([picture, alpha])
        path = os.path.join(self.root, "game", "images", "fg", "fg_%s%s.png" % (self.place, "_" + v if v else ""))
        if not os.path.exists(path):
            return None
        im = Image.open(path).convert("RGBA")
        if im.size != (W, H):
            return None
        return np.asarray(im).astype(np.float32) / 255.0


def over(base, layer, x=0, y=0):
    """Lay an RGBA 0..1 layer on an RGB 0..1 picture at (x, y), in place."""
    h, w = layer.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    part = layer[y0 - y:y1 - y, x0 - x:x1 - x]
    a = part[..., 3:4]
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1.0 - a) + part[..., :3] * a


def sprite_layer(lay, root, who, expr, zoom, far, row):
    """A person as the stage draws them: (RGBA 0..1 at the slot's size, a note or None)."""
    info = lay.d.get("people", {}).get(who)
    if info is None:
        raise SystemExit("%s is not one of the game's people (the dump's `people`: %s)"
                         % (who, ", ".join(sorted(lay.d.get("people", {})))))
    cw, ch = info["canvas"]
    base = os.path.join(root, "game", os.path.dirname(info["file"]))
    path = os.path.join(base, "%s_%s.png" % (who, expr or "neutral"))
    note = None
    if not os.path.exists(path):
        note = "%s has no %s picture: neutral is drawn" % (who, expr)
        path = os.path.join(root, "game", info["file"])
    im = Image.open(path).convert("RGBA")
    if im.size != (cw, ch):
        im = im.resize((cw, ch), Image.LANCZOS)
    canvas = np.zeros((ch, cw, 4), np.float32)
    # the contact shadow, under the soles (lighting.rpy: lit_sprite)
    fx, fy, fw = info["feet"]
    sh_path = os.path.join(root, "game", "images", "fx", "contact_shadow.png")
    if os.path.exists(sh_path):
        sw, shh = int(fw * 1.6), max(14, int(fw * 0.2))
        sh = np.asarray(Image.open(sh_path).convert("RGBA").resize((sw, shh), Image.LANCZOS)).astype(np.float32) / 255.0
        sh[..., 3] *= row[3]
        x0, y0 = int(round(fx - sw / 2.0)), int(round(fy + 2 - shh / 2.0))
        ys, xs = slice(max(0, y0), min(ch, y0 + shh)), slice(max(0, x0), min(cw, x0 + sw))
        canvas[ys, xs] = sh[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    sp = np.asarray(im).astype(np.float32) / 255.0
    a = sp[..., 3:4]
    canvas[..., :3] = canvas[..., :3] * (1.0 - a) + sp[..., :3] * a
    canvas[..., 3:4] = canvas[..., 3:4] * (1.0 - a) + a
    canvas[..., :3] = np.clip(lit(canvas[..., :3], row), 0.0, 1.0)      # the room's light, over sprite and shadow
    if far:
        canvas[..., :3] = np.clip(canvas[..., :3] - FAR_DIM * far, 0.0, 1.0)
    w, h = int(round(cw * zoom)), int(round(ch * zoom))
    # scaled with alpha premultiplied, as a renderer does, so no light fringe is drawn round the figure
    pre = canvas.copy()
    pre[..., :3] *= pre[..., 3:4]
    out = Image.fromarray(np.clip(pre * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS)
    if far:
        out = out.filter(ImageFilter.GaussianBlur(FAR_BLUR * far))
    out = np.asarray(out).astype(np.float32) / 255.0
    al = np.maximum(out[..., 3:4], 1e-6)
    out[..., :3] = np.clip(out[..., :3] / al, 0.0, 1.0)
    return out, note


def people_rows(room, who, dialogue=False):
    """[{who, expr, x, yoff, zoom, far, rect}] in stage order."""
    n = len(who)
    rows = []
    if dialogue:
        for (name, expr), (xa, zoom) in zip(who, DIALOGUE[n]):
            cw = room.lay.d["people"].get(name, {}).get("canvas", room.sprite)[0]
            w = cw * zoom
            rows.append(dict(who=name, expr=expr, x=int(round(xa * (W - w) + w / 2.0)), yoff=0, zoom=zoom, far=0))
    else:
        slots = room.slots(n)
        if len(slots) != n:
            raise SystemExit("%s has no standing row for %d people" % (room.place, n))
        for (name, expr), s in zip(who, slots):
            rows.append(dict(who=name, expr=expr, x=s[0], yoff=s[1], zoom=s[2], far=s[3]))
    for r in rows:
        cw, ch = room.lay.d["people"].get(r["who"], {}).get("canvas", room.sprite)
        w, h = int(round(cw * r["zoom"])), int(round(ch * r["zoom"]))
        r["rect"] = (int(round(r["x"] - w / 2.0)), int(H + r["yoff"] - h), w, h)
    return rows


# ---- marks: what can be clicked ---------------------------------------------------------------------------------
def dashed(d, pts, fill, width=3, dash=14):
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        length = max(1.0, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        k = 0.0
        while k < length:
            e = min(length, k + dash)
            d.line([x0 + (x1 - x0) * k / length, y0 + (y1 - y0) * k / length,
                    x0 + (x1 - x0) * e / length, y0 + (y1 - y0) * e / length], fill=fill, width=width)
            k += dash * 2


def label(d, x, y, text, fnt, fill=PAPER, anchor="mm"):
    box = d.textbbox((x, y), text, font=fnt, anchor=anchor)
    d.rectangle([box[0] - 8, box[1] - 5, box[2] + 8, box[3] + 5], fill=INK + (215,))
    d.text((x, y), text, font=fnt, fill=fill + (255,), anchor=anchor)


def short_name(room, p):
    if p["kind"] == "exit":
        return p["name"].replace("the way to ", "to ")
    return p["id"].replace("_", " ")


def draw_marks(im, room, front, shaped, names=False):
    """Exits as tiles and things to do as rings (an unshaped place), or each shape's outline (a shaped one).
    front: the layer drawn (behind the people, or over the foreground). names: only the names, of both layers,
    which go on last so that nobody stands in front of one."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = room.lay.frame("hot_size", 72)
    shapes = room.shapes() if shaped else {}
    look = hex_to_tuple((room.lay.d.get("hot_look") or {}).get("color", "#fff0cc"))
    for p in room.points():
        x, y = p["at"]
        if names:
            label(d, x, y + (22 if p["id"] in shapes else size // 2 + 14), short_name(room, p), font(15))
            continue
        if bool(p["front"]) != front:
            continue
        if p["id"] in shapes:
            for poly in shapes[p["id"]]:
                pts = [(q[0], q[1]) for q in poly]
                if p["front"]:
                    dashed(d, pts, look + (255,))
                else:
                    d.line(pts + [pts[0]], fill=look + (255,), width=3, joint="curve")
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=look + (255,), outline=INK + (255,))
        elif p["kind"] == "exit":
            d.rectangle([x - size // 2, y - size // 2, x + size // 2, y + size // 2], fill=INK + (200,), outline=PAPER + (255,), width=2)
            d.text((x, y), "exit", font=font(16), fill=PAPER + (255,), anchor="mm")
        else:
            d.ellipse([x - size // 2, y - size // 2, x + size // 2, y + size // 2], outline=GOLD + (255,), width=3)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD + (255,))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def hex_to_tuple(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def draw_lit(im, room):
    """Every shape lit and named, as while names are shown (D60)."""
    lk = room.lay.d.get("hot_look") or {}
    col = hex_to_tuple(lk.get("color", "#fff0cc"))
    wash, edge = float(lk.get("wash", 0.3)), float(lk.get("edge", 0.85))
    shapes = room.shapes()
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for hid, shape in sorted(shapes.items()):
        for poly in shape:
            pts = [(q[0], q[1]) for q in poly]
            d.polygon(pts, fill=col + (int(255 * wash),))
            d.line(pts + [pts[0]], fill=col + (int(255 * edge),), width=3, joint="curve")
    out = Image.alpha_composite(im.convert("RGBA"), layer)
    d = ImageDraw.Draw(out)
    f = font(20, bold=True)
    top = room.lay.hot_shape().get("top", 92)
    d.line([0, top, W, top], fill=PAPER + (120,), width=1)
    # Each name where the game draws its plate while names are shown (hot_name_rect, through check_layout's
    # copy of it: against the 72 px square at the point, on its `tips` side, turned round at the screen's edge),
    # so that two names that would meet are seen meeting here. A planned hotspot's plate is a guess of its size.
    place = check_layout.Place(check_layout.Game(room.lay), room.place, room.hot or None, room.view or None, room.extra,
                               (), room.root, os.path.join(room.root, "tools", "bgs", "keep"), os.path.join(room.root, "tools", "fg"))
    for p in room.points():
        if p["id"] in shapes and p["id"] in place.points:
            (x, y, w, h), _measured = check_layout.name_rect(place, p["id"])
            words = p["name"].replace("the way to ", "") if p["kind"] == "exit" else p["id"].replace("_", " ")
            size = 20
            while size > 11 and d.textlength(words, font=font(size, bold=True)) > w - 10:
                size -= 1
            d.rectangle([x, y, x + w, y + h], fill=INK + (225,), outline=PAPER + (160,), width=1)
            d.text((x + w / 2.0, y + h / 2.0), words, font=font(size, bold=True), fill=PAPER + (255,), anchor="mm")
        elif p["id"] in shapes:
            label(d, p["at"][0], p["at"][1], short_name(room, p), f)
        else:
            label(d, p["at"][0], p["at"][1], short_name(room, p) + " (keeps its button)", font(15), fill=GOLD)
    return out.convert("RGB")


def draw_tags(im, room, rows, plain=False):
    if not rows:
        return im
    lo, hi = room.lay.frame("tag_edges", [179, 1700])
    f = font(20, bold=True)
    d0 = ImageDraw.Draw(im)
    names = [r["who"].capitalize() for r in rows]
    widths = [28 + int(d0.textlength(n, font=f)) for n in names]
    xs = check_layout.tag_xs([r["rect"] for r in rows], max(widths), room.lay.frame("tag_gap", 8), lo, hi)
    y = room.lay.frame("tag_y", 1036)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r, n, w, x in zip(rows, names, widths, xs):
        d.rectangle([x - w // 2, y, x + w // 2, y + 36], fill=INK + (225,), outline=(60, 54, 80, 255))
        d.text((x, y + 18), n, font=f, fill=PAPER + (255,), anchor="mm")
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


# ---- one frame ----------------------------------------------------------------------------------------------------
def frame(room, period, who, plain=False, dialogue=False, lit_shapes=False):
    """(the frame as an RGB image, the lines that say what it is)."""
    said = []
    plain = plain or dialogue           # a story scene shows nothing to click
    picture, v, words = room.picture(period)
    tint, bright = room.room_grade(period, v)
    row, row_from = room.light_row(period, v, picture)
    said.append("%s; %s" % (words, "as painted" if (tint, bright) == ("#ffffff", 0.0) else "under the hour's tint %s %+.2f" % (tint, bright)))
    said.append("light %s (%s)" % (json.dumps(row), row_from))
    base = np.clip(ink(np.clip(grade(picture, tint, bright), 0, 1), VIEW_INK), 0, 1).astype(np.float32)
    shaped = bool(room.shapes())
    im = to_image(base)
    if not plain and not lit_shapes:
        im = draw_marks(im, room, front=False, shaped=shaped)
    base = np.asarray(im).astype(np.float32) / 255.0
    rows = people_rows(room, who, dialogue) if who else []
    for r in sorted(rows, key=lambda r: -r["far"]):
        layer, note = sprite_layer(room.lay, room.root, r["who"], r["expr"], r["zoom"], r["far"], row)
        if note:
            said.append(note)
        over(base, layer, r["rect"][0], r["rect"][1])
    fg = None if dialogue and room.place not in (room.lay.d.get("fg_talk") or []) and not room.view.get("talk") else room.foreground(v, picture)
    if fg is not None:
        fg = fg.copy()
        fg[..., :3] = np.clip(ink(np.clip(grade(fg[..., :3], tint, bright), 0, 1), VIEW_INK), 0, 1)
        over(base, fg)
        said.append("the foreground is laid over the people")
    im = to_image(base)
    if lit_shapes:
        im = draw_lit(im, room)
    elif not plain:
        im = draw_marks(im, room, front=True, shaped=shaped)
        im = draw_marks(im, room, front=True, shaped=shaped, names=True)
    if not dialogue:
        im = draw_tags(im, room, rows, plain)
    return im, said


def titled(im, title, scale=1.0):
    """A frame with a line of words over it."""
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    out = Image.new("RGB", (im.width, im.height + 30), (20, 18, 28))
    out.paste(im, (0, 30))
    ImageDraw.Draw(out).text((8, 15), title, font=font(16), fill=PAPER, anchor="lm")
    return out


def stack(panels, cols):
    w = max(p.width for p in panels)
    h = max(p.height for p in panels)
    rows = (len(panels) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), (20, 18, 28))
    for i, p in enumerate(panels):
        sheet.paste(p, ((i % cols) * (w + 8), (i // cols) * (h + 8)))
    return sheet


def default_who(lay, place, period, n=None):
    """Who the timetable puts there at that hour on a weekday; else the first of the cast."""
    got = [w for w in sorted(lay.d.get("schedule", {})) if lay.where(w, "Wed", period) == place and w in lay.d.get("people", {})]
    pool = got + [w for w in STOCK if w not in got and w in lay.d.get("people", {})]
    return [(w, None) for w in pool[:n if n else max(1, min(4, len(got)))]]


def parse_who(text, lay):
    if text == "none":
        return []
    out = []
    for part in [t for t in text.split(",") if t]:
        name, _, expr = part.partition(":")
        out.append((name, expr or None))
    if not 1 <= len(out) <= 4:
        raise SystemExit("--who names one to four people (or `none` for the empty room)")
    return out


def main(argv):
    def opt(flag):
        if flag not in argv:
            return None
        i = argv.index(flag)
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            raise SystemExit("%s needs a value" % flag)
        v = argv[i + 1]
        del argv[i:i + 2]
        return v

    def flag(name):
        if name in argv:
            argv.remove(name)
            return True
        return False

    dump = game_layout.pop_dump_arg(argv)
    root = os.path.abspath(opt("--root") or ROOT)
    who_arg, bg, staged, beside, out_path = opt("--who"), opt("--bg"), opt("--staged"), opt("--beside"), opt("--out")
    dialogue, plain = flag("--dialogue"), flag("--plain")
    if [a for a in argv if a.startswith("--")] or not 1 <= len(argv) <= 2:
        print(__doc__)
        raise SystemExit(1)
    lay = game_layout.load(dump, root)
    name = argv[0]
    place = name if lay.has_place(name) else lay.place_of_stem(name)
    if not place:
        raise SystemExit("%s is not a place of the game, nor the name of a place's picture" % name)
    hour = argv[1].lower() if len(argv) > 1 else None
    if hour is not None and hour not in HOUR_WORDS:
        raise SystemExit("the hour is one of: %s" % ", ".join(sorted(HOUR_WORDS)))
    for f in (bg, beside):
        if f and not os.path.exists(os.path.expanduser(f)):
            raise SystemExit("no picture at %s" % f)
    if staged and not os.path.isdir(staged):
        raise SystemExit("no folder at %s" % staged)
    room = Room(lay, place, root, staged, os.path.expanduser(bg) if bg else None)
    title = "%s (%s)" % (lay.name(place), place)
    out_dir = os.path.join(root, "shots", "stage")

    if hour is not None:
        period = HOUR_WORDS[hour]
        who = parse_who(who_arg, lay) if who_arg else default_who(lay, place, period)
        im, said = frame(room, period, who, plain=plain, dialogue=dialogue)
        if room.shapes():
            print("  shaped: %d shapes; their outlines are drawn (the sheet, with no hour, also lights and names them)" % len(room.shapes()))
        words = "%s, %s, %s%s" % (title, period, ", ".join(w for w, _e in who) or "nobody", ", as a story scene stands them" if dialogue else "")
        if beside:
            shot = Image.open(os.path.expanduser(beside)).convert("RGB").resize((W, H), Image.LANCZOS)
            sheet = stack([titled(shot, "THE GAME: %s" % os.path.basename(beside), 0.5),
                           titled(im, "tools/stage_preview.py: %s" % words, 0.5)], 2)
            full = stack([titled(shot, "THE GAME, full size"), titled(im, "tools/stage_preview.py, full size")], 1)
            sheet = stack_down([sheet, full])
        else:
            sheet = titled(im, "%s  |  %s" % (words, "  |  ".join(said + room.notes))[:300])
        out_path = out_path or os.path.join(out_dir, "%s_%s%s.jpg" % (place, hour, "_beside" if beside else ""))
    else:
        panels = []
        said_all = []
        for n in (1, 2, 3, 4):
            who = (parse_who(who_arg, lay) if who_arg and who_arg != "none" else default_who(lay, place, "Afternoon", 4))[:n]
            who = who + [w for w in default_who(lay, place, "Afternoon", 6) if w[0] not in [x[0] for x in who]][:n - len(who)]
            im, said = frame(room, "Afternoon", who, plain=plain, dialogue=dialogue)
            said_all = said
            panels.append(titled(im, "%s, by day, %d: %s" % (title, n, ", ".join(w for w, _e in who)), 0.5))
        for period in ("Evening", "Night"):
            who = parse_who(who_arg, lay) if who_arg else default_who(lay, place, period)
            im, said = frame(room, period, who, plain=plain, dialogue=dialogue)
            panels.append(titled(im, ("%s, %s: %s  |  %s" % (title, period, ", ".join(w for w, _e in who), said[0]))[:150], 0.5))
        sheet = stack(panels, 2)
        if room.shapes():
            who = parse_who(who_arg, lay) if who_arg else default_who(lay, place, "Afternoon", 2)
            a, _s = frame(room, "Afternoon", who)
            b, _s = frame(room, "Afternoon", [], lit_shapes=True)
            sheet = stack_down([sheet, titled(a, "%s: every shape's outline (a front shape dashed), with the people" % title),
                                titled(b, "%s: every shape lit and named, as while names are shown (D60)" % title)])
            print("  shaped: %d shapes; two frames more, their outlines and every shape lit and named" % len(room.shapes()))
        print("  %s" % "; ".join(said_all))
        out_path = out_path or os.path.join(out_dir, "%s.jpg" % place)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    sheet.save(out_path, quality=90)
    if hour is not None:
        for line in said:
            print("  %s" % line)
    for line in room.notes:
        print("  %s" % line)
    if place in game_layout.NO_POSE_PLACES:
        print("  K16: the people here are the game's dressed sprites on the floor; nobody is ever drawn in the water")
    print("wrote %s (%dx%d)" % (out_path, sheet.width, sheet.height))
    return 0


def stack_down(parts):
    w = max(p.width for p in parts)
    sheet = Image.new("RGB", (w, sum(p.height for p in parts) + 8 * (len(parts) - 1)), (20, 18, 28))
    y = 0
    for p in parts:
        sheet.paste(p, (0, y))
        y += p.height + 8
    return sheet


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
