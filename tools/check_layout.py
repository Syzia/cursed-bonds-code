#!/usr/bin/env python3
"""
The check a layout must pass before its picture may be installed.

    python3 tools/check_layout.py tools/art/staged/courtyard          # a folder of candidate files
    python3 tools/check_layout.py some/hot_courtyard.json some/view_courtyard.json
    python3 tools/check_layout.py <folder> --layout-dump shots/art/game_layout.json     # in a worktree
    python3 tools/check_layout.py <folder> --front low_table,desk     # planned foreground objects (see below)
    python3 tools/check_layout.py --selftest [--layout-dump <file>]

docs/UI2_DESIGN.md 5.6 (step 4), 7.3 (D60, "The picture is what is clicked"),
6.3, 4.6, 3.2. It reads a candidate layout AS FILES, before they are in
game/layout/, and says in one plain line each what it refuses and what it
only reports. Exit status 0 only when nothing is refused; 1 when something
is; 2 when the layout dump is out of date. Plain Python: no Ren'Py, no Pillow.

WHAT IT READS

  the candidate   hot_<place>.json, view_<place>.json, area_<key>.json,
                  map_campus.json (3.2's keys). A candidate file REPLACES the
                  game's file of the same name, so a point it leaves out is
                  the code's own (the dump's `default`), not the point an
                  installed sidecar gives today. pose_, light_ and faces files
                  are the installers' own and are only looked at for their
                  shape. One more file may lie beside them, for this check
                  alone, and is never installed (it is read from a folder,
                  and also when it lies beside a hot_ or view_ file that is
                  named on its own, which is how the installer names them):
  check_<place>.json   what the check needs that the game does not read:
                    "front"    [ids]: the PLANNED hotspots that are their
                               room's foreground object. The game has no
                               layer for a planned hotspot yet (wave 1's U4
                               registers it front=True); the layout sitting
                               traces it as front and writes its id here.
                               --front id,id adds to the list.
                    "objects"  {id: [x, y, w, h]}: the box of the thing a
                               front shape is traced round, read off the
                               picture ("tight to its object")
                    "fg"       {"": [[x, y], ...]}: the room's foreground
                               outline while tools/fg/<place>.json is still
                               to be written (same shape as that file)
                    "doors"    [{"name", "box": [x, y, w, h]}]: the room's
                               painted doors, beside the keep list's own
                    "horizon"  y: the picture's eye line, for the scale rule
  the game's numbers   tools/art/game_layout.json, through game_layout.py:
                  every limit below comes from the dump (frames, hot_shape,
                  exits, hotspots, spot_planned, slots, name_rects, areas,
                  world, people). The few numbers the dump does not carry are
                  named constants below, each with the line of the game or of
                  a harness it stands for; --selftest reads those lines and
                  fails the day one differs.
  the shape rules   the text between the two "hot_shape:" marker lines of
                  game/sb_hotspots.rpy is run as it stands, so the counting
                  is the game's own (hot_shape_findings, then
                  hot_shape_layers: the game's lint is the two lists).
  the campus record   tools/check_campus.py is called on the hot_, area_ and
                  map_ files (5.2's fixed facts); nothing of it is rewritten.
  the room's doors   tools/bgs/keep/<picture>.json (`doors`), and the
                  foreground outline tools/fg/<place>.json.

WHAT IT REFUSES (each line starts REFUSED, then the place and the rule's name)

  file            a file is not what 3.2 says it holds (check_content.py's
                  --layout-files rule, run on the candidate)
  point           a point for an id that is neither an exit, a hotspot nor a
                  planned hotspot of the place; a point that is not two numbers
  bounds, lane    a point outside the frame; its 72 px square in the toast
                  lane or the banner lane
  standalone      a standalone hotspot (the vending machine) where someone
                  stands with one to four people in the place
  clear, apart    an exit within 120 px of a hotspot of its place; two exits
                  less than 110 px apart
  caption         an exit under the arrival caption's box
  top-row         an exit under the banner that starts above a two-line
                  banner; in a yard, more than one exit above y 300 or exits
                  at fewer than three heights
  exit-on-door    indoors, an exit the layout places that is neither inside a
                  painted door's box nor in the bottom band (never on a window)
  placed          a planned hotspot with no point, in a layout that is shaped
                  or made for a composed picture (5.6: each picture is laid
                  out once)
  stage-x         a standing slot whose rectangle leaves x 40 to 1700
  floor           a near slot's feet off the floor or on a no-stand polygon;
                  a far slot's feet off the floor or not behind the room's
                  foreground; no `floor` or `scale` in a composed layout
  scale           a person drawn more than 12% off what the room's `scale`
                  says they measure at that depth
  slot-hides      a row for one or two people over a hotspot; a row for one
                  to four people that hides every thing to click in the room
  column          the icon column would hold more than its eight tiles with
                  four people in the place (4.6)
  shape           every rule of 7.3, in the game's own words (polygons,
                  points, inside the picture, crossing, overlap, area, two
                  fifths, the point inside and under no smaller shape, buried,
                  unknown id, shaped all at once, keep_tile, the two layers)
  keep-tile-front a keep_tile id that is not front, whose point lies inside
                  a front shape (its button is drawn; the click is the shape's)
  front-shape     a front shape that is neither inside the room's foreground
                  outline nor tight to its object's box
  names-meet      two name plates that meet while names are shown
  spare           a house's `spare` list shorter than the record's count of
                  its spare doors; a spare point under 110 px from an exit or
                  from another spare point, or outside the frame
  pin, map        a map pin outside the pin frame or of a room that has none;
                  area markers that overlap or leave the map; the Mountain's
                  marker off the mountain
  lock-label      a door that can be locked whose reason (the hover label's
                  size as the game measures it: the dump's `lock_labels`),
                  opened on the side `tips` gives or the game would choose,
                  would leave the screen or cover another exit or the arrival
                  caption
  tag-x           a row whose name tags, each at its widest, do not fit
                  between x 179 and x 1700 (the dump's frames.tag_edges,
                  tag_gap and tag_w; not checked with a dump that lacks them)
  campus          a fixed fact of the campus record the layout breaks

WHAT IT ONLY REPORTS (REPORT): with a dump written before `lock_labels` was
added to it, lock-label, on a label at its largest (520 by 80 px); the part
of a shape above y 92, where no shape takes the pointer; the part inside the toast lane or the banner lane, which a
toast or the banner may cover; how many hotspots keep a button, and why; an
exit or a planned hotspot the file gives no point; a room that waits for its
layout sitting; a name plate or a label whose size is a guess until its
hotspot is registered; what check_campus only reports.

tools/install_redo.py --compose calls it as `check_layout.py --layout <files>
[--layout-dump <file>]`. --layout says the installer is asking: the files
follow it, the dump is taken as the installer has just checked it (against
the tree it installs into, which may be a scratch copy), and the campus
record is left to the installer, which reads it with the owner's waivers.

Options: --layout-dump <file>, --root <tree> (the tree whose dump, record,
keep lists and outlines are read), --keep <dir>, --fg <dir>, --record <file>,
--front id,id, --no-campus (leave the campus record out: a test layout on a
picture the record does not speak of), --quiet (no NOTE lines).
"""
import sys, os, json, re, shutil, tempfile, textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_campus
import game_layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEGIN, END = "## >>> hot_shape:", "## <<< hot_shape:"

# ---- the few numbers the dump does not carry -------------------------------------------------------------------
# Each stands for one line of the game or of a harness. PINNED below lists (file, the text that must be in it);
# --selftest fails the day one of those lines changes, so none of these can drift unseen.
BANNER_TWO_LINES = 234      # a two-line objective banner ends near y 233 (p2_paths.rpy: "r[\"y\"] - 36 >= 234")
BANNER_ROW_Y = 400          # ... for an exit above y 400 between the banner lane's ends
HUB_TOP_Y = 300             # in a yard at most one exit above y 300 ...
HUB_HEIGHTS = 3             # ... and the exits at three heights or more (p2_paths.rpy)
CAPTION_RING = 96           # an exit's ring is kept clear of the arrival caption (p2_paths.rpy)
TIP_W = 520                 # the hover label's widest (ui_icons.rpy: ICON_TIP_W)
TIP_H = 80                  # a lock's reason is up to two lines of 22 px and one of 18, padded 8: at most this (a guess)
TIP_GAP = 12                # the gap between a tile and its label (ui_icons.rpy: icon_tip_where)
RAIL_ALWAYS = 2             # "Hold the hour" and "Wait" are always in the column (4.6)
PERSON_PX, PERSON_CM, NEAR_ZOOM = 596.0, 173.0, 0.52    # 6.3: the near line draws a 173 cm person 596 px tall
SCALE_CM = 200.0            # `scale` is one door or post, taken as 200 cm (6.1)
SCALE_TOL = 0.12            # 6.3
HORIZON = (0.35, 0.45, 0.55)    # the eye line when the layout names none: "a little above the middle" (stage.txt),
                                # tried from 35% to 55% of the height; refused only if no such line fits
FG_INSIDE = 0.98            # a front shape "lies inside" the foreground outline when this much of it does
TIGHT = 12                  # ... or is "tight to its object": no point more than this far outside the object's box
NAME_GUESS = (150, 29)      # a planned hotspot's name plate, until it is registered and the dump measures it
PINNED = (
    ("tools/smoke/p2_paths.rpy", 'r["y"] - 36 >= 234 for f in LOCATIONS for r in path_exits(f) if 364 <= r["x"] <= 1336 and r["y"] < 400'),
    ("tools/smoke/p2_paths.rpy", "len([y for y in ys if y < 300]) <= 1 and len(set(ys)) >= 3"),
    ("tools/smoke/p2_paths.rpy", 'hot_overlap((r["x"] - 48, r["y"] - 48, 96, 96), PATH_CAPTION_BOX)'),
    ("game/ui_icons.rpy", "ICON_TIP_W = 520"),
    ("game/ui_icons.rpy", "ICON_TIP_PAD = (14, 8)"),
    ("game/ui_icons.rpy", "ICON_TIP_TEXT = (22, 18)"),
    ("game/ui_icons.rpy", 'if side == "top" and y - 12 - size[1] < 0:'),
    ("game/ui_icons.rpy", 'if side == "left" and x - 12 - size[0] < 0:'),
    ("game/view_stage.rpy", "x = max(want[i], edge + gap + half)"),
    ("game/view_stage.rpy", "out[i] = min(out[i], edge - gap - half)"),
    ("game/sb_hotspots.rpy", "hh = max(int(th) + 5, (HOT_FACE_SIZE + 5) if faces else 0)"),
    ("game/view_stage.rpy", "return (int(round(xc - w / 2.0)), int(config.screen_height + yoff - h), w, h)"),
    ("game/room_paths.rpy", 'hid.startswith("go_") or hid.startswith("zz")'),
)
# A door the game can lock that is not a Bond door (world.door_bond has those): place_access in sb_world.rpy,
# and the five p2_paths.rpy hovers. Names, not numbers.
LOCKABLE_ALSO = ("storehouse", "office", "utahime_office", "gojo_office", "girls_dorm", "pool")
SIDES = ("top", "bottom", "left", "right")
GAME_FILES = ("hot_", "view_", "area_", "pose_", "light_")


class Out(object):
    """REFUSED, REPORT and NOTE lines, in the order they were found."""

    def __init__(self):
        self.lines = []

    def add(self, level, where, rule, text):
        self.lines.append((level, where, rule, text))

    def refuse(self, where, rule, text):
        self.add("REFUSED", where, rule, text)

    def report(self, where, rule, text):
        self.add("REPORT", where, rule, text)

    def note(self, where, text):
        self.add("NOTE", where, "", text)

    def count(self, level):
        return sum(1 for l in self.lines if l[0] == level)

    def rules(self, level="REFUSED"):
        return [l[2] for l in self.lines if l[0] == level]

    def texts(self, level="REFUSED"):
        return ["%s [%s]: %s" % (l[1], l[2], l[3]) for l in self.lines if l[0] == level]


# ---- the game's own shape functions ------------------------------------------------------------------------------
def shape_block(root=None):
    """The text between the two marker lines of game/sb_hotspots.rpy, the init block's indent taken off."""
    path = os.path.join(root or ROOT, "game", "sb_hotspots.rpy")
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    a = [n for n, l in enumerate(lines) if l.strip().startswith(BEGIN)]
    b = [n for n, l in enumerate(lines) if l.strip().startswith(END)]
    if len(a) != 1 or len(b) != 1 or b[0] <= a[0]:
        raise SystemExit("check_layout.py: %s: the two 'hot_shape:' marker lines are not there once each" % path)
    return textwrap.dedent("\n".join(lines[a[0] + 1:b[0]])) + "\n"


_SHAPE_NS = {}


def shape_functions(root=None):
    """{name: function}: that block, run as plain Python (the game's lint counts with the same text)."""
    key = os.path.abspath(root or ROOT)
    if key not in _SHAPE_NS:
        ns = {}
        exec(compile(shape_block(root), "sb_hotspots.rpy (hot_shape block)", "exec"), ns)
        _SHAPE_NS[key] = ns
    return _SHAPE_NS[key]


# ---- small geometry (the game's: hot_rect, hot_overlap, view_slot_rect) ----------------------------------------
def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_point(v):
    return isinstance(v, (list, tuple)) and len(v) == 2 and num(v[0]) and num(v[1])


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


class Game(object):
    """The numbers of the dump a layout is checked against."""

    def __init__(self, lay):
        self.lay = lay
        d = lay.d
        self.W, self.H = lay.screen()
        self.size = lay.frame("hot_size", 72)
        self.bounds = tuple(lay.frame("hot_bounds"))
        self.lanes = [tuple(l) for l in lay.frame("hot_lanes")]
        self.caption = tuple(lay.frame("caption_box"))
        self.apart, self.clear = lay.frame("path_apart"), lay.frame("path_clear")
        self.stage_x = tuple(lay.frame("stage_x"))
        self.sprite = tuple(lay.frame("sprite"))
        self.rail_max = lay.frame("rail")["max"]
        self.pin_frame = tuple(lay.frame("map_pin_frame"))
        self.mountain_box = tuple(lay.frame("map_mountain_box"))
        self.map_area = tuple(lay.frame("map_area"))
        limits = lay.hot_shape()
        self.limits = dict(limits, polys=tuple(limits["polys"]), points=tuple(limits["points"]))
        self.top = limits["top"]
        soles = sorted(p["feet"][1] for p in d.get("people", {}).values()) or [1365]
        self.sole = soles[len(soles) // 2]
        self.world = d.get("world") or {}
        self.lockable = set(self.world.get("door_bond") or {}) | set(LOCKABLE_ALSO)
        # {place: {exit id: [w, h]}}: each locked exit's reason as the game measures it; None in a dump written
        # before the key was added (the lock-label rule is then a REPORT, on a largest-case box)
        locks = d.get("lock_labels")
        self.lock_labels = locks if isinstance(locks, dict) else None
        self.tag_edges = lay.frame("tag_edges")
        self.tag_gap, self.tag_w = lay.frame("tag_gap"), lay.frame("tag_w")

    def rect(self, pt):
        """The square a hotspot at a point takes (hot_rect)."""
        return (int(pt[0]) - self.size // 2, int(pt[1]) - self.size // 2, self.size, self.size)

    def slot_rect(self, slot):
        """The rectangle one standing slot covers (view_slot_rect)."""
        xc, yoff, zoom = slot[0], slot[1], slot[2]
        w, h = int(round(self.sprite[0] * zoom)), int(round(self.sprite[1] * zoom))
        return (int(round(xc - w / 2.0)), int(self.H + yoff - h), w, h)

    def feet(self, slot):
        """Where the soles of someone at a slot touch the ground."""
        return (slot[0], self.H + slot[1] - (self.sprite[1] - self.sole) * slot[2])


def tag_xs(rects, w, gap, lo, hi):
    """The x centre of each name tag of a row, as the game lays them (view_stage.rpy: view_tag_xs), every tag
    `w` wide: under its person, pushed right where two would touch, then pushed back inside the edges."""
    want = [int(r[0] + r[2] / 2) for r in rects]
    order = sorted(range(len(rects)), key=want.__getitem__)
    out = list(want)
    half = (w + 1) // 2
    edge = lo - gap
    for i in order:
        x = max(want[i], edge + gap + half)
        out[i] = x
        edge = x + half
    edge = hi + gap
    for i in order[::-1]:
        out[i] = min(out[i], edge - gap - half)
        edge = out[i] - half
    return out


def slots_ok(rows, n):
    return (isinstance(rows, list) and len(rows) == n
            and all(isinstance(r, list) and len(r) in (3, 4) and all(num(q) for q in r) for r in rows))


# ---- reading a candidate -------------------------------------------------------------------------------------------
def read_candidate(paths, out):
    """{stem: (path, data)} for the .json files of a folder, or the files named."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, n) for n in sorted(os.listdir(p)) if n.endswith(".json") and not n.startswith(".")]
        elif os.path.exists(p):
            files.append(p)
        else:
            raise SystemExit("check_layout.py: no file or folder at %s" % p)
    # A layout named file by file (as tools/install_redo.py --compose names it: only what goes into the game)
    # is still judged with the check_<place>.json that lies beside it: the eye line, the object boxes and the
    # planned front ids are part of what the sitting measured, and the installer may not hand that file on.
    named = set(os.path.abspath(f) for f in files)
    for path in list(files):
        m = re.match(r"(?:hot|view)_(\w+)\.json$", os.path.basename(path))
        beside = os.path.join(os.path.dirname(os.path.abspath(path)), "check_%s.json" % m.group(1)) if m else None
        if beside and os.path.exists(beside) and beside not in named:
            named.add(beside)
            files.append(beside)
    got = {}
    for path in files:
        stem = os.path.basename(path)[:-5]
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except ValueError as e:
            out.refuse(stem, "file", "%s is not JSON (%s)" % (os.path.basename(path), " ".join(str(e).split())[:80]))
            continue
        if not isinstance(data, dict):
            out.refuse(stem, "file", "%s must hold one JSON object" % os.path.basename(path))
            continue
        if stem in got:
            out.refuse(stem, "file", "%s is given twice" % os.path.basename(path))
            continue
        got[stem] = (path, data)
    return got


def file_shapes(cand, game, rec, root, out):
    """check_content.py's --layout-files rule on the candidate's own files (3.2's keys and what each holds)."""
    import check_content
    work = tempfile.mkdtemp(prefix="check_layout_")
    try:
        names = {}
        for stem, (path, data) in sorted(cand.items()):
            if stem.startswith("check_") or stem == "pictures":
                continue
            shutil.copyfile(path, os.path.join(work, stem + ".json"))
            names[os.path.join(work, stem + ".json")] = stem
        # for_rev is for a composed picture or a new place (3.2): the record says which places are.
        pictures = dict(check_campus.load_manifest(root).get("pictures") or {})
        if rec is not None:
            for key, row in rec.places.items():
                if row.get("how") == "composed":
                    pictures.setdefault(key, {"rev": 2, "kind": "composed"})
        with open(os.path.join(work, "pictures.json"), "w") as f:
            json.dump({"pictures": pictures}, f)
        for path, text in check_content.layout_file_findings(work, {}):
            stem = names.get(path)
            if stem is not None:
                out.refuse(stem, "file", text)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if "pictures" in cand:
        out.refuse("pictures", "file", "pictures.json is the installer's alone: a layout never carries the manifest")


# ---- a place: its points -------------------------------------------------------------------------------------------
class Place(object):
    """One place of the candidate, with the game's rows under it."""

    def __init__(self, game, place, hot, view, extra, front, root, keep_dir, fg_dir):
        lay = game.lay
        self.game, self.place = game, place
        self.name = lay.name(place)
        self.hot, self.view, self.extra = hot, view, extra or {}
        self.info = lay.place(place)
        self.exits = lay.exits(place)                       # [{id, to, default, applied}]
        self.hots = [h for h in lay.hotspots(place) if not str(h["id"]).startswith("zz")]
        self.planned = dict((pid, kind) for pid, kind in lay.planned(place) if pid not in set(h["id"] for h in self.hots))
        self.exit_ids = [e["id"] for e in self.exits]
        self.kind = dict((h["id"], h["kind"]) for h in self.hots)
        self.kind.update(self.planned)
        self.known = set(self.exit_ids) | set(self.kind)
        spots = (hot or {}).get("spots")
        self.spots = spots if isinstance(spots, dict) else {}
        self.points = {}                                    # {id: (x, y)}: where the game would draw each
        self.from_file = set()
        for row in self.exits + self.hots:
            if hot is None:
                self.points[row["id"]] = tuple(row["applied"])
            else:
                self.points[row["id"]] = tuple(row["default"])
        for hid in self.known:
            if is_point(self.spots.get(hid)):
                self.points[hid] = (self.spots[hid][0], self.spots[hid][1])
                self.from_file.add(hid)
        if hot is None:                                     # no hot_ file given: the installed sidecar's points
            side = os.path.join(root, "game", "layout", "hot_%s.json" % place)
            if os.path.exists(side):
                try:
                    inst = json.load(open(side, encoding="utf-8")).get("spots") or {}
                except ValueError:
                    inst = {}
                for hid in self.planned:
                    if is_point(inst.get(hid)):
                        self.points[hid] = tuple(inst[hid])
        self.front = set(lay.front_ids(place)) | set(self.extra.get("front") or []) | set(front or [])
        self.slots = {}
        self.slots_from = {}
        vs = (view or {}).get("slots") if isinstance((view or {}).get("slots"), dict) else {}
        for n in (1, 2, 3, 4):
            rows = vs.get(str(n))
            if slots_ok(rows, n):
                self.slots[n], self.slots_from[n] = rows, "the layout"
            elif view is not None and slots_ok((lay.d.get("slots_code", {}).get(place) or {}).get(str(n)), n):
                self.slots[n], self.slots_from[n] = lay.d["slots_code"][place][str(n)], "the code"
            else:
                self.slots[n], self.slots_from[n] = lay.slots(place).get(str(n)) or [], "the game today"
        stem = lay.bg_stem(place)
        self.keep = {}
        kp = os.path.join(keep_dir, stem + ".json")
        if os.path.exists(kp):
            try:
                self.keep = json.load(open(kp, encoding="utf-8"))
            except ValueError:
                self.keep = {}
        self.doors = [d for d in list(self.keep.get("doors") or []) + list(self.extra.get("doors") or [])
                      if isinstance(d, dict) and isinstance(d.get("box"), list) and len(d["box"]) == 4]
        self.fg = []
        fg = self.extra.get("fg")
        if not isinstance(fg, dict):
            fp = os.path.join(fg_dir, place + ".json")
            fg = {}
            if os.path.exists(fp):
                try:
                    fg = json.load(open(fp, encoding="utf-8"))
                except ValueError:
                    fg = {}
        poly = fg.get("") if isinstance(fg, dict) else None
        if isinstance(poly, list) and len(poly) >= 3 and all(is_point(p) for p in poly):
            self.fg = [poly]

    def things(self):
        """The ids of the place's hotspots that are not exits and have a point."""
        return [hid for hid in sorted(self.kind) if hid in self.points]

    def words(self, hid):
        if hid in self.exit_ids:
            to = [e["to"] for e in self.exits if e["id"] == hid][0]
            return "the way to %s" % self.game.lay.name(to)
        return "%s%s" % ("the planned hotspot " if hid in self.planned else "the hotspot ", hid)


def check_points(p, out):
    g, place = p.game, p.place
    x0, y0, x1, y1 = g.bounds
    for hid in sorted(p.spots):
        pt = p.spots[hid]
        if hid not in p.known:
            out.refuse(place, "point", "%r: no exit or hotspot of that id is registered in %s, or planned for it" % (hid, p.name))
        elif not is_point(pt):
            out.refuse(place, "point", "%s: its point is not two numbers" % p.words(hid))
    for hid in sorted(p.points):
        x, y = p.points[hid]
        kept = "" if (hid in p.from_file or p.hot is None) else " (the layout gives it no point: this is the code's own)"
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            out.refuse(place, "bounds", "%s at (%d, %d) is outside the frame, x %d to %d and y %d to %d%s"
                       % (p.words(hid), x, y, x0, x1, y0, y1, kept))
        r = g.rect((x, y))
        for lane, lname in zip(g.lanes, ("the toast lane", "the banner lane")):
            if overlap(r, lane):
                out.refuse(place, "lane", "%s at (%d, %d) sits in %s (x %d to %d, y %d to %d), where a %s is drawn%s"
                           % (p.words(hid), x, y, lname, lane[0], lane[0] + lane[2], lane[1], lane[1] + lane[3],
                              "toast" if "toast" in lname else "banner", kept))
        if p.kind.get(hid) == "standalone":
            for n in (1, 2, 3, 4):
                if any(overlap(r, g.slot_rect(s)) for s in p.slots[n]):
                    out.refuse(place, "standalone", "%s at (%d, %d) is where someone stands with %d in the place; it has no "
                               "tile to fall back to, so it stays clear of every standing row" % (p.words(hid), x, y, n))
                    break
    if p.hot is not None:
        firm = bool(p.hot.get("shapes")) or "for_rev" in p.hot
        for e in p.exits:
            if e["id"] not in p.from_file:
                out.report(place, "kept", "%s: the layout gives it no point, so the game would use its code's (%d, %d)"
                           % (p.words(e["id"]), e["default"][0], e["default"][1]))
        for hid in sorted(p.planned):
            if hid not in p.points:
                if firm:
                    out.refuse(place, "placed", "the planned hotspot %r has no point under spots: a picture is laid out once, "
                               "with every thing planned for it placed (5.6)" % hid)
                else:
                    out.report(place, "placed", "the planned hotspot %r has no point yet" % hid)


def check_paths(p, out):
    g, place = p.game, p.place
    exits = [(e["id"], e["to"], p.points[e["id"]]) for e in p.exits]
    keep = [(hid, p.points[hid]) for hid in p.things()]
    for hid, to, pt in exits:
        for kid, kp in keep:
            if dist2(pt, kp) < g.clear ** 2:
                out.refuse(place, "clear", "%s at (%d, %d) is within %d px of %s at (%d, %d)"
                           % (p.words(hid), pt[0], pt[1], g.clear, p.words(kid), kp[0], kp[1]))
        for hid2, to2, pt2 in exits:
            if to2 > to and dist2(pt, pt2) < g.apart ** 2:
                out.refuse(place, "apart", "%s and %s are less than %d px apart" % (p.words(hid), p.words(hid2), g.apart))
        ring = (pt[0] - CAPTION_RING // 2, pt[1] - CAPTION_RING // 2, CAPTION_RING, CAPTION_RING)
        if overlap(ring, g.caption):
            out.refuse(place, "caption", "%s at (%d, %d) lies under the arrival caption (x %d to %d, y %d to %d), which is "
                       "over the picture for my first seconds in a place"
                       % (p.words(hid), pt[0], pt[1], g.caption[0], g.caption[0] + g.caption[2], g.caption[1], g.caption[1] + g.caption[3]))
        banner = g.lanes[1]
        half = g.size // 2
        if banner[0] - half <= pt[0] <= banner[0] + banner[2] + half and pt[1] < BANNER_ROW_Y and pt[1] - half < BANNER_TWO_LINES:
            out.refuse(place, "top-row", "%s at (%d, %d) starts above a two-line banner: under the banner an exit sits at "
                       "y %d or lower" % (p.words(hid), pt[0], pt[1], BANNER_TWO_LINES + half))
    if p.info.get("hub") and exits:
        ys = sorted(pt[1] for _h, _t, pt in exits)
        if len([y for y in ys if y < HUB_TOP_Y]) > 1 or len(set(ys)) < min(HUB_HEIGHTS, len(ys)):
            out.refuse(place, "top-row", "the exits of a yard are spread over the picture, not in a row: at most one above "
                       "y %d and at least %d heights (here: %s)" % (HUB_TOP_Y, HUB_HEIGHTS, ", ".join(str(int(y)) for y in ys)))
    # a door that can be locked: its reason, hovered, is on the screen, hides no other exit, and is off the caption
    labels = g.lock_labels
    for hid, to, pt in exits:
        if labels is None:
            # an older dump, without the labels' measured sizes: the label at its largest, and only a REPORT
            if to not in g.lockable:
                continue
            (lw, lh), say, size_words = (TIP_W, TIP_H), out.report, "up to %d by %d px" % (TIP_W, TIP_H)
        else:
            if hid not in labels.get(place, {}):
                continue
            (lw, lh), say = labels[place][hid], out.refuse
            size_words = "%d by %d px" % (lw, lh)
        sx, sy, sw, sh = g.rect(pt)
        tips = (p.hot or {}).get("tips")
        own = isinstance(tips, dict) and tips.get(hid) in SIDES
        side = tip_side(p, hid, exit_=True)
        if not own:
            # the game's own answer (icon_tip_where): above, or to the left; the other side where that leaves the screen
            if side == "top" and sy - TIP_GAP - lh < 0:
                side = "bottom"
            elif side == "left" and sx - TIP_GAP - lw < 0:
                side = "right"
        if side in ("top", "bottom"):
            r = (max(0, min(sx, g.W - lw)), sy - lh if side == "top" else sy + sh, lw, lh)
        else:
            r = (sx - lw if side == "left" else sx + sw, max(0, min(sy, g.H - lh)), lw, lh)
        where = {"top": "above it", "bottom": "below it", "left": "to its left", "right": "to its right"}[side]
        if not (r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= g.W and r[1] + r[3] <= g.H):
            say(place, "lock-label", "%s can be locked, and its reason (%s), opened %s, would leave the screen: give it "
                "another side under tips, or move it" % (p.words(hid), size_words, where))
            continue
        hit = [p.words(h2) for h2, _t2, pt2 in exits if h2 != hid and overlap(r, g.rect(pt2))]
        if overlap(r, g.caption):
            hit.append("the arrival caption")
        if hit:
            say(place, "lock-label", "%s can be locked, and its reason (%s), opened %s, would cover %s: give it another "
                "side under tips, or move it" % (p.words(hid), size_words, where, " and ".join(hit)))


def check_doors(p, out, band):
    """7.3: indoors, an exit sits on a painted door, or in the bottom band as the way back."""
    if not p.info.get("indoor") or p.hot is None:
        return
    placed = [e for e in p.exits if e["id"] in p.from_file]
    if not placed:
        out.report(p.place, "exit-on-door", "%s waits for its layout sitting: the layout places none of its exits" % p.name)
        return
    for e in placed:
        x, y = p.points[e["id"]]
        if y >= band:
            continue
        on = [d for d in p.doors if d["box"][0] <= x <= d["box"][0] + d["box"][2] and d["box"][1] <= y <= d["box"][1] + d["box"][3]]
        if not on:
            names = ", ".join(str(d.get("name", "a door")) for d in p.doors)
            out.refuse(p.place, "exit-on-door", "%s at (%d, %d) is on no painted door of the room (%s) and not in the bottom band "
                       "(y %d or lower): indoors an exit sits on a door, never on a window or a wall"
                       % (p.words(e["id"]), x, y, ("its doors: " + names) if names else "the keep list names no door", band))


def check_spare(p, out, rec):
    """D50: the painted doors that lead nowhere yet."""
    if p.hot is None:
        return
    want = (rec.places.get(p.place) or {}).get("spare_doors") if rec is not None else None
    spare = p.hot.get("spare")
    if not want and spare is None:
        return
    pts = [tuple(q) for q in (spare if isinstance(spare, list) else []) if is_point(q)]
    g = p.game
    if want and len(pts) < want:
        out.refuse(p.place, "spare", "%s is painted with %d spare door%s (the campus record), and the layout's `spare` list "
                   "holds %d point%s" % (p.name, want, "" if want == 1 else "s", len(pts), "" if len(pts) == 1 else "s"))
    x0, y0, x1, y1 = g.bounds
    for i, pt in enumerate(pts):
        if not (x0 <= pt[0] <= x1 and y0 <= pt[1] <= y1):
            out.refuse(p.place, "spare", "the spare door at (%d, %d) is outside the frame, x %d to %d and y %d to %d: an exit "
                       "could never be put on it" % (pt[0], pt[1], x0, x1, y0, y1))
        for e in p.exits:
            if dist2(pt, p.points[e["id"]]) < g.apart ** 2:
                out.refuse(p.place, "spare", "the spare door at (%d, %d) is under %d px from %s at (%d, %d)"
                           % (pt[0], pt[1], g.apart, p.words(e["id"]), p.points[e["id"]][0], p.points[e["id"]][1]))
        for q in pts[i + 1:]:
            if dist2(pt, q) < g.apart ** 2:
                out.refuse(p.place, "spare", "the spare doors at (%d, %d) and (%d, %d) are under %d px apart"
                           % (pt[0], pt[1], q[0], q[1], g.apart))


# ---- a place: where people stand ---------------------------------------------------------------------------------
def check_stage(p, out, ns):
    g, place = p.game, p.place
    lo, hi = g.stage_x
    for n in (1, 2, 3, 4):
        for s in p.slots[n]:
            x, _y, w, _h = g.slot_rect(s)
            if x < lo or x + w > hi:
                out.refuse(place, "stage-x", "with %d in the place, the slot at x %s leaves the stage (x %d to %d): the person's "
                           "picture runs from x %d to %d" % (n, s[0], lo, hi, x, x + w))
    # 6.3: name tags stay between the Review tools link and the icon column. The game moves the tags itself
    # (view_tag_xs: under each person, pushed apart by their widths, pushed back inside the edges); what a layout
    # can still break is the room for them, so each row is laid out here with every tag at its widest.
    if g.tag_edges and g.tag_w:
        t_lo, t_hi = g.tag_edges
        for n in (1, 2, 3, 4):
            xs = tag_xs([g.slot_rect(s) for s in p.slots[n]], g.tag_w, g.tag_gap or 0, t_lo, t_hi)
            half = (g.tag_w + 1) // 2
            ends = sorted((x - half, x + half) for x in xs)
            if ends and (ends[0][0] < t_lo or ends[-1][1] > t_hi
                         or any(b[0] - a[1] < (g.tag_gap or 0) - 1 for a, b in zip(ends, ends[1:]))):
                out.refuse(place, "tag-x", "with %d in the place, the name tags (each up to %d px wide, %d px apart) do not fit "
                           "between x %d and x %d under the people: they would run from x %d to x %d"
                           % (n, g.tag_w, g.tag_gap or 0, t_lo, t_hi, ends[0][0], ends[-1][1]))
    if p.view is None:
        return
    composed = "for_rev" in p.view
    floor = p.view.get("floor") if isinstance(p.view.get("floor"), dict) else None
    on = [poly for poly in (floor or {}).get("on", []) if isinstance(poly, list) and len(poly) >= 3]
    off = [poly for poly in (floor or {}).get("off", []) if isinstance(poly, list) and len(poly) >= 3]
    inside = ns["hot_shape_inside"]

    def behind(x, y):
        """A step back means behind the room's foreground object: inside the box round its outline (the
        floor under a table is open between its legs, and is behind it all the same)."""
        xs, ys = [q[0] for q in p.fg[0]], [q[1] for q in p.fg[0]]
        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

    if not on:
        (out.refuse if composed else out.report)(place, "floor", "the layout has no `floor`: where people may stand is not checked"
                                                 + (" (a composed picture's layout carries one, 6.1)" if composed else ""))
    else:
        for n in (1, 2, 3, 4):
            for k, s in enumerate(p.slots[n]):
                fx, fy = g.feet(s)
                far = len(s) > 3 and bool(s[3])
                who = "with %d in the place, person %d (x %s%s)" % (n, k + 1, s[0], ", a step back" if far else "")
                if not inside(on, fx, fy):
                    out.refuse(place, "floor", "%s: the feet, at (%d, %d), are not on the floor" % (who, fx, fy))
                elif inside(off, fx, fy) if off else False:
                    out.refuse(place, "floor", "%s: the feet, at (%d, %d), are on a part of the floor nobody may stand on"
                               % (who, fx, fy))
                elif far and p.fg and not behind(fx, fy):
                    out.refuse(place, "floor", "%s: a person a step back stands behind the room's foreground, and these feet, at "
                               "(%d, %d), are not behind it" % (who, fx, fy))
    scale = p.view.get("scale")
    if not (isinstance(scale, list) and len(scale) == 3 and all(num(q) for q in scale) and scale[1] < scale[2]):
        (out.refuse if composed else out.report)(place, "scale", "the layout has no `scale`: the size of people is not checked"
                                                 + (" (a composed picture's layout carries one, 6.1)" if composed else ""))
        return
    per_cm = (scale[2] - scale[1]) / SCALE_CM
    given = p.extra.get("horizon")
    lines = [given] if num(given) else [g.H * f for f in HORIZON]
    for n in (1, 2, 3, 4):
        for k, s in enumerate(p.slots[n]):
            fx, fy = g.feet(s)
            drawn = PERSON_PX / PERSON_CM * s[2] / NEAR_ZOOM
            offs = []
            for hz in lines:
                if scale[2] - hz <= 0 or fy - hz <= 0:
                    continue
                want = per_cm * (fy - hz) / (scale[2] - hz)
                offs.append((drawn - want) / want)
            if not offs:
                out.report(place, "scale", "`scale` ends above the eye line: the size of people is not checked")
                return
            best = min(offs, key=abs)
            if abs(best) > SCALE_TOL:
                out.refuse(place, "scale", "with %d in the place, person %d (x %s, zoom %s) is drawn %d%% %s than the room's `scale` "
                           "says a person measures there (a 200 cm door or post is %d px tall at y %d; within %d%% is allowed)"
                           % (n, k + 1, s[0], s[2], round(abs(best) * 100), "larger" if best > 0 else "smaller",
                              scale[2] - scale[1], scale[2], SCALE_TOL * 100))
            elif not num(given) and abs(offs[len(offs) // 2]) > SCALE_TOL:
                out.report(place, "scale", "with %d in the place, person %d (x %s) fits the room's `scale` only if the eye line is "
                           "not at y %d: name it (\"horizon\" in check_%s.json) to have this checked exactly"
                           % (n, k + 1, s[0], lines[len(lines) // 2], place))


def check_hidden(p, out):
    """6.3 and 4.6, read on the 72 px square at each point."""
    g, place = p.game, p.place
    things = p.things()
    rows = dict((n, [g.slot_rect(s) for s in p.slots[n]]) for n in (1, 2, 3, 4))
    covered = dict((n, [hid for hid in things if any(overlap(g.rect(p.points[hid]), r) for r in rows[n])]) for n in rows)
    for n in (1, 2):
        for hid in covered[n]:
            if p.kind.get(hid) == "standalone":
                continue        # said once, as `standalone`
            out.refuse(place, "slot-hides", "with %d in the place (the row from %s), someone stands over %s at (%d, %d): no row "
                       "for one or two people hides a hotspot of the room"
                       % (n, p.slots_from[n], p.words(hid), p.points[hid][0], p.points[hid][1]))
    for n in (3, 4):
        if things and len(covered[n]) == len(things) and not any(len(covered[m]) for m in (1, 2)):
            out.refuse(place, "slot-hides", "with %d in the place, the row hides every thing to click in the room (%s)"
                       % (n, ", ".join(things)))
    drop = [e["id"] for e in p.exits] + [hid for hid in things if p.kind.get(hid) == "act"]
    hidden = [hid for hid in drop if any(overlap(g.rect(p.points[hid]), r) for r in rows[4])]
    if RAIL_ALWAYS + len(hidden) > g.rail_max:
        out.refuse(place, "column", "with four people in the place %d things drop into the icon column (%s), and with Hold the "
                   "hour and Wait that is %d tiles: the column holds %d. Put %d of them where no person's picture reaches"
                   % (len(hidden), ", ".join(hidden), RAIL_ALWAYS + len(hidden), g.rail_max,
                      RAIL_ALWAYS + len(hidden) - g.rail_max))
    elif p.info.get("hub"):
        out.note(place, "the icon column with four people here: %d of %d things drop into it (%d tiles of %d)"
                 % (len(hidden), len(drop), RAIL_ALWAYS + len(hidden), g.rail_max))


# ---- a place: the picture is what is clicked (D60) ---------------------------------------------------------------
def tip_side(p, hid, exit_=False):
    """The side a hotspot's name opens on: the layout's `tips`, else the game's own answer today, read back
    from where the dump drew its plate (the screen's edges aside), else above an exit and left of a thing."""
    tips = (p.hot or {}).get("tips")
    if isinstance(tips, dict) and tips.get(hid) in SIDES:
        return tips[hid]
    g = p.game
    base = "top" if (exit_ or hid in p.exit_ids) else "left"
    rect = g.lay.name_rects(p.place).get(hid)
    old = None
    for row in p.exits + p.hots:
        if row["id"] == hid:
            old = row["applied"]
    if rect is None or old is None or hid in g.lay.tips(p.place):
        return base
    sx, sy = old[0] - g.size // 2, old[1] - g.size // 2
    x, y, w, h = rect
    if y + h == sy:
        side = "top"
    elif y == sy + g.size:
        side = "bottom"
    elif x + w == sx:
        side = "left"
    elif x == sx + g.size:
        side = "right"
    else:
        return base
    # hot_name_rect turns a plate round at the screen's edge: that is not the hotspot's own side
    if (side == "right" and sx - w < 0) or (side == "bottom" and sy - h < 0):
        return base
    return side


def name_rect(p, hid):
    """((x, y, w, h), measured): hot_name_rect at the layout's point. `measured` is False for a planned
    hotspot, whose plate the game cannot measure until it is registered."""
    g = p.game
    rect = g.lay.name_rects(p.place).get(hid)
    w, hh = (rect[2], rect[3]) if rect else NAME_GUESS
    sx, sy, sw, sh = g.rect(p.points[hid])
    side = tip_side(p, hid)
    if side == "left" and sx - w < 0:
        side = "right"
    elif side == "right" and sx + sw + w > g.W:
        side = "left"
    elif side == "top" and sy - hh < 0:
        side = "bottom"
    elif side == "bottom" and sy + sh + hh > g.H:
        side = "top"
    if side == "left":
        x, y = sx - w, sy
    elif side == "right":
        x, y = sx + sw, sy
    else:
        x = max(0, min(sx, g.W - w))
        y = sy - hh if side == "top" else sy + sh
    return (x, y, w, hh), rect is not None


def well_formed(ns, shape, limits, size):
    p_lo, p_hi = limits["polys"]
    n_lo, n_hi = limits["points"]
    return (isinstance(shape, (list, tuple)) and p_lo <= len(shape) <= p_hi
            and all(ns["hot_shape_poly"](poly) and n_lo <= len(poly) <= n_hi
                    and all(0 <= q[0] <= size[0] and 0 <= q[1] <= size[1] for q in poly)
                    and not ns["hot_shape_crossed"](poly) for poly in shape))


def check_shapes(p, out, ns):
    g, place = p.game, p.place
    hot = p.hot
    if hot is None or ("shapes" not in hot and "keep_tile" not in hot):
        return
    shapes = hot.get("shapes", {})
    keep = hot.get("keep_tile")
    size = (g.W, g.H)
    need = set(h for h in p.known if not str(h).startswith("zz"))
    for line in (list(ns["hot_shape_findings"](place, shapes, keep, p.points, p.known, need, g.limits, size))
                 + list(ns["hot_shape_layers"](place, shapes, p.points, p.front, g.limits, size))):
        out.refuse(place, "shape", line.replace(" (hot_%s.json)" % place, ""))
    if not isinstance(shapes, dict):
        return
    good = dict((hid, s) for hid, s in shapes.items() if well_formed(ns, s, g.limits, size))
    grid = g.limits["grid"]
    cols = int(size[0] // grid)
    cells = dict((hid, ns["hot_shape_cells"](good[hid], size, grid)[0]) for hid in good)

    def centre(c):
        return ((c % cols) * grid + grid / 2.0, (c // cols) * grid + grid / 2.0)

    def share(part, whole):
        pc = 100.0 * part / whole
        return "under 1%" if pc < 1 else "%d%%" % round(pc)

    # reported, not refused: what the HUD's row and the two lanes take of a shape
    for hid in sorted(good):
        n = len(cells[hid]) or 1
        above = sum(1 for c in cells[hid] if centre(c)[1] < g.top)
        if above:
            out.report(place, "above-hud", "shape %r: %s of it is above y %d, where no shape takes the pointer (it is lit "
                       "there, and dead)" % (hid, share(above, n), g.top))
        for lane, lname in zip(g.lanes, ("the toast lane", "the banner lane")):
            inl = sum(1 for c in cells[hid]
                      if lane[0] <= centre(c)[0] < lane[0] + lane[2] and lane[1] <= centre(c)[1] < lane[1] + lane[3])
            if inl:
                out.report(place, "in-lane", "shape %r: %s of it is inside %s, which a %s may cover"
                           % (hid, share(inl, n), lname, "toast" if "toast" in lname else "banner"))
    if isinstance(keep, dict) and keep:
        out.report(place, "keep-tile", "%d hotspot%s keep%s a button in %s: %s"
                   % (len(keep), "" if len(keep) == 1 else "s", "s" if len(keep) == 1 else "", p.name,
                      "; ".join("%s (%s)" % (k, keep[k]) for k in sorted(keep))))
        for hid in sorted(keep):
            pt = p.points.get(hid)
            if hid in p.front or pt is None:
                continue
            for other in sorted(good):
                if other in p.front and ns["hot_shape_inside"](good[other], pt[0], pt[1]):
                    out.refuse(place, "keep-tile-front", "keep_tile %r: its button, at (%d, %d), lies inside the front shape %r: "
                               "the button is drawn and the click goes to the shape. Move its point, or trace the shape round it"
                               % (hid, pt[0], pt[1], other))
    else:
        out.note(place, "no hotspot keeps a button in %s" % p.name)
    # a front shape is inside the room's foreground outline, or tight to its object
    objects = p.extra.get("objects") if isinstance(p.extra.get("objects"), dict) else {}
    for hid in sorted(good):
        if hid not in p.front:
            continue
        mine = cells[hid]
        if p.fg and mine:
            inside = sum(1 for c in mine if ns["hot_shape_inside"](p.fg, centre(c)[0], centre(c)[1]))
            if inside >= FG_INSIDE * len(mine):
                continue
        box = objects.get(hid)
        if isinstance(box, list) and len(box) == 4 and all(num(q) for q in box):
            far = [q for poly in good[hid] for q in poly
                   if not (box[0] - TIGHT <= q[0] <= box[0] + box[2] + TIGHT and box[1] - TIGHT <= q[1] <= box[1] + box[3] + TIGHT)]
            if not far:
                continue
            out.refuse(place, "front-shape", "shape %r is in front of the people, and it is not traced tight to its object: the "
                       "point (%d, %d) is more than %d px outside the object's box %r. Whatever a front shape covers of a person "
                       "is its click and not theirs" % (hid, far[0][0], far[0][1], TIGHT, box))
            continue
        out.refuse(place, "front-shape", "shape %r is in front of the people, and it is neither inside the room's foreground "
                   "outline (%s) nor tight to its object (give the object's box under \"objects\" in check_%s.json). Whatever a "
                   "front shape covers of a person is its click and not theirs"
                   % (hid, "tools/fg/%s.json" % place if p.fg else "the room has none", place))
    # while names are shown, no two name plates meet
    plates = []
    for hid in sorted(good):
        if hid in p.points and hid in p.known:
            plates.append((hid,) + name_rect(p, hid))
    for i, (a, ra, ma) in enumerate(plates):
        for b, rb, mb in plates[i + 1:]:
            if p.points[a] == p.points[b]:
                continue        # two hotspots at one point are never offered together
            if overlap(ra, rb):
                text = ("while names are shown the names of %s and %s meet: their plates are at (%d, %d, %d x %d) and "
                        "(%d, %d, %d x %d). Give one of them another side under tips, or move a point"
                        % (p.words(a), p.words(b), ra[0], ra[1], ra[2], ra[3], rb[0], rb[1], rb[2], rb[3]))
                if ma and mb:
                    out.refuse(place, "names-meet", text)
                else:
                    out.report(place, "names-meet", text + " (a planned hotspot's plate is a guess of %d px until it is "
                               "registered: check again then)" % NAME_GUESS[0])


# ---- the maps --------------------------------------------------------------------------------------------------------
def check_area(game, key, data, out):
    areas = dict((a["key"], a) for a in game.lay.d.get("areas", []))
    where = "area_" + key
    if key not in areas:
        out.refuse(where, "pin", "%r is not an area of the game" % key)
        return
    a = areas[key]
    if "for_rev" in data:
        out.refuse(where, "pin", "the file carries for_rev, and the game's lint (map_validate) takes only \"spots\" in an "
                   "area file today: installed like this, lint would fail")
    spots = data.get("spots") if isinstance(data.get("spots"), dict) else {}
    pinless = set(game.world.get("pinless") or [])
    x0, y0, x1, y1 = game.pin_frame
    pts = dict((l, tuple(s["default"])) for l, s in a["spots"].items())
    for l in sorted(spots):
        if l not in a["places"]:
            out.refuse(where, "pin", "%r is not a room of this area" % l)
        elif l in pinless:
            out.refuse(where, "pin", "%s has no pin on the map (it is reached on foot)" % game.lay.name(l))
        elif is_point(spots[l]):
            pts[l] = tuple(spots[l])
    for l in sorted(pts):
        x, y = pts[l]
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            out.refuse(where, "pin", "the pin of %s at (%d, %d) is outside x %d to %d, y %d to %d"
                       % (game.lay.name(l), x, y, x0, x1, y0, y1))
    for l in sorted(a["spots"]):
        if l not in spots:
            out.report(where, "kept", "the pin of %s: the layout gives it no point, so the game would use its code's (%d, %d)"
                       % (game.lay.name(l), a["spots"][l]["default"][0], a["spots"][l]["default"][1]))


def check_campus_map(game, data, out):
    where = "map_campus"
    areas = game.lay.d.get("areas", [])
    anchors = dict((a["key"], tuple(a["anchor"])) for a in areas)
    given = data.get("anchors") if isinstance(data.get("anchors"), dict) else {}
    for k in sorted(given):
        if k not in anchors:
            out.refuse(where, "map", "%r is not an area of the game" % k)
        elif is_point(given[k]):
            anchors[k] = tuple(given[k])
    w, h = game.map_area
    rects = [(a["key"], a["name"], (int(anchors[a["key"]][0] - w // 2), int(anchors[a["key"]][1] - h // 2), w, h)) for a in areas]
    for i, (ka, na, ra) in enumerate(rects):
        if ra[0] < 0 or ra[1] < game.lanes[1][1] or ra[0] + ra[2] > game.W or ra[1] + ra[3] > game.H:
            out.refuse(where, "map", "the marker of %s at %r runs off the map or under its top row" % (na, ra))
        for kb, nb, rb in rects[i + 1:]:
            if overlap(ra, rb):
                out.refuse(where, "map", "the markers of %s and %s overlap" % (na, nb))
    box = data.get("mountain_box")
    box = tuple(box) if isinstance(box, list) and len(box) == 4 and all(num(q) for q in box) else game.mountain_box
    if "mountain" in anchors:
        mx, my = anchors["mountain"]
        if not (box[0] <= mx <= box[2] and box[1] <= my <= box[3]):
            out.refuse(where, "map", "the Mountain marker's centre (%d, %d) is not on the mountain %r" % (mx, my, box))


# ---- the whole check ---------------------------------------------------------------------------------------------------
def check(cand, lay, root=None, record=None, keep_dir=None, fg_dir=None, front=(), campus=True, out=None):
    """Every rule, on a candidate ({stem: (path, data)}); returns the Out."""
    out = out or Out()
    root = root or ROOT
    game = Game(lay)
    ns = shape_functions(root)
    rec = None
    try:
        rec = check_campus.Rec(check_campus.load_record(record or os.path.join(root, "tools", "bgs", "campus.json")))
    except SystemExit:
        out.report("the record", "campus", "no campus record: its fixed facts and the spare doors are not checked")
    keep_dir = keep_dir or os.path.join(root, "tools", "bgs", "keep")
    fg_dir = fg_dir or os.path.join(root, "tools", "fg")
    file_shapes(cand, game, rec, root, out)
    places = []
    for stem in sorted(cand):
        m = re.match(r"(hot|view|check)_(\w+)$", stem)
        if m and m.group(2) not in places and stem != "hot_look":
            places.append(m.group(2))
    band = (rec.rules.get("bottom_band", 900) if rec is not None else 900)
    for place in places:
        if not lay.has_place(place):
            out.refuse(place, "file", "%r is not a place of the game" % place)
            continue
        hot = cand.get("hot_" + place, (None, None))[1]
        view = cand.get("view_" + place, (None, None))[1]
        extra = cand.get("check_" + place, (None, None))[1]
        if hot is None and view is None:
            out.report(place, "file", "check_%s.json stands alone: there is no hot_ or view_ file for it to speak of" % place)
            continue
        p = Place(game, place, hot, view, extra, front, root, keep_dir, fg_dir)
        for hid in sorted(p.front - p.known):
            out.refuse(place, "file", "front id %r is no hotspot of %s, registered or planned" % (hid, p.name))
        for hid in sorted(p.front & set(p.exit_ids)):
            out.refuse(place, "file", "front id %r is an exit: an exit is never in the front layer" % hid)
        if hot is not None and "for_rev" in hot and rec is not None:
            pic = rec.r.get("pictures", {}).get(lay.bg_stem(place))
            if pic and isinstance(hot["for_rev"], int) and hot["for_rev"] != pic.get("rev"):
                out.refuse(place, "file", "hot_%s.json is made for revision %s, and the picture the owner chose is revision %s "
                           "in the campus record" % (place, hot["for_rev"], pic.get("rev")))
        check_points(p, out)
        check_paths(p, out)
        check_doors(p, out, band)
        check_spare(p, out, rec)
        check_stage(p, out, ns)
        check_hidden(p, out)
        check_shapes(p, out, ns)
    for stem in sorted(cand):
        if stem.startswith("area_"):
            check_area(game, stem[len("area_"):], cand[stem][1], out)
        elif stem == "map_campus":
            check_campus_map(game, cand[stem][1], out)
    if campus and rec is not None:
        cc = check_campus.Out()
        files = [cand[s][0] for s in sorted(cand) if re.match(r"(hot_|area_)\w+$", s) and s != "hot_look" or s == "map_campus"]
        files = [f for f in files if not re.match(r"hot_(\w+)\.json$", os.path.basename(f))
                 or lay.has_place(os.path.basename(f)[4:-5])]
        try:
            check_campus.check_layout_files(rec, files, cc, lay.d)
        except Exception as e:     # a malformed file has its own `file` line above
            out.report("the record", "campus", "the campus record could not be read against these files (%s)" % e)
        for level, text in cc.lines:
            if level == "FAIL":
                out.refuse("the record", "campus", text)
            elif level == "REPORT":
                out.report("the record", "campus", text)
            else:
                out.note("the record", text)
    return out


def show(out, title, quiet=False):
    for level in ("REFUSED", "REPORT", "NOTE"):
        if level == "NOTE" and quiet:
            continue
        for l, where, rule, text in out.lines:
            if l == level:
                print("%-8s %s%s: %s" % (level, where, " [%s]" % rule if rule else "", text))
    n, r = out.count("REFUSED"), out.count("REPORT")
    print("check_layout: %s: %s" % (title, ("PASS (%d reported)" % r) if not n else
                                      "REFUSED (%d refused, %d reported): this layout may not be installed" % (n, r)))
    return 1 if n else 0


# ---- the self-test -------------------------------------------------------------------------------------------------
# One whole layout that passes, written for the Courtyard's present picture (game/images/bg/courtyard.png as it
# is before batch 0: the west hall, the main hall and the east hall round the flagstones, the pagoda behind), and
# small layouts that must each be refused BY NAME. tools/test_art_tools.py runs every one through the command
# line, a line apiece; --selftest runs them here.
def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def base_courtyard():
    """{file stem: data}: the whole layout. Every exit and thing of the Courtyard has its point and its shape."""
    hot = {
        "spots": {
            "go_courtyard__gate": [1300, 985], "go_courtyard__school_yard": [84, 600],
            "go_courtyard__dorm_yard": [960, 540], "go_courtyard__training_yard": [1640, 850],
            "spot_vend": [1600, 690], "gateway": [690, 250], "straw_posts": [1620, 980]},
        "tips": {"go_courtyard__training_yard": "left", "straw_posts": "bottom"},
        "shapes": {
            "go_courtyard__school_yard": [[[0, 215], [300, 350], [620, 600], [620, 830], [0, 840]]],       # the west hall
            "go_courtyard__dorm_yard": [[[735, 590], [800, 470], [1150, 470], [1190, 600], [1240, 780], [700, 790]]],   # the main hall
            "go_courtyard__training_yard": [[[1400, 560], [1920, 200], [1920, 880], [1450, 880]]],       # the east hall
            "go_courtyard__gate": [_rect(500, 940, 1560, 1080)],                                        # the flagstones, behind me
            "spot_vend": [_rect(1560, 620, 1640, 760)],                                                 # under the east porch
            "gateway": [[[600, 300], [690, 150], [780, 300], [790, 560], [590, 560]]],                  # the pagoda
            "straw_posts": [_rect(1380, 900, 1700, 1060)]},                                             # the lawn on the right
    }
    view = {
        "slots": {"1": [[700, -40, 0.52, 0]], "2": [[480, -40, 0.52, 0], [960, -70, 0.49, 1]],
                  "3": [[340, -40, 0.52, 0], [720, -80, 0.48, 1], [1090, -40, 0.52, 0]],
                  "4": [[250, -40, 0.52, 0], [545, -80, 0.48, 1], [850, -80, 0.48, 1], [1160, -40, 0.52, 0]]},
        "floor": {"on": [[[0, 850], [640, 800], [1300, 800], [1920, 860], [1920, 1080], [0, 1080]]]},
    }
    extra = {"objects": {"spot_vend": [1556, 616, 88, 148]}}
    return {"hot_courtyard": hot, "view_courtyard": view, "check_courtyard": extra}


def _copy(v):
    return json.loads(json.dumps(v))


def cases():
    """[(name, {stem: data}, the rule that must refuse it or None for a pass, words its line must hold, the
    other rules that may speak of the same fault)]. Nothing else may be refused in a case."""
    out = [("the whole layout, written for the Courtyard's present picture, passes", base_courtyard(), None, "", ())]

    def case(name, rule, words, edit, files=None, also=()):
        got = _copy(files if files is not None else base_courtyard())
        edit(got)
        out.append((name, got, rule, words, also))

    def hot(d):
        return d["hot_courtyard"]

    def shapes(d):
        return d["hot_courtyard"]["shapes"]

    # 7.3: an indoor exit on a window (the infirmary's is there today)
    case("an indoor exit on a window", "exit-on-door", "never on a window",
         lambda d: None, {"hot_infirmary": {"spots": {"go_infirmary__school_yard": [84, 500]}}})
    case("the same exit in the bottom band, as the way back, passes", None, "",
         lambda d: None, {"hot_infirmary": {"spots": {"go_infirmary__school_yard": [420, 960]}}})
    # 6.3: a slot row over a hotspot
    case("a slot row for one person over a hotspot", "slot-hides", "straw_posts",
         lambda d: d["view_courtyard"]["slots"].__setitem__("1", [[1620, -40, 0.2, 0]]))
    # D50: the spare doors of a house
    # (the stand-in corridor's own points: Yuji's door is given a side, so that its lock's reason, once the dump
    # measures it, opens clear of the door to My Room)
    dorm = {"hot_boys_dorm": {"spare": [[640, 620], [1030, 640], [1320, 760]], "tips": {"go_boys_dorm__yuji_room": "bottom"}}}
    case("a house with its three spare doors measured passes", None, "", lambda d: None, dorm)
    case("a house whose spare list is shorter than the record's count of its spare doors", "spare", "holds 2 points",
         lambda d: d["hot_boys_dorm"]["spare"].pop(), dorm)
    case("a spare point under 110 px from an exit", "spare", "from the way to",
         lambda d: d["hot_boys_dorm"]["spare"].__setitem__(0, [500, 660]), dorm)
    case("a spare point under 110 px from another spare point", "spare", "px apart",
         lambda d: d["hot_boys_dorm"]["spare"].__setitem__(1, [700, 680]), dorm)
    case("a spare point outside the frame", "spare", "outside the frame",
         lambda d: d["hot_boys_dorm"]["spare"].__setitem__(2, [1810, 760]), dorm)
    # 7.3, "The rules": one test apiece
    case("shape rule: four polygons", "shape", "a shape is 1 to 3 polygons",
         lambda d: shapes(d).__setitem__("straw_posts", [_rect(1380, 900, 1450, 1060), _rect(1460, 900, 1530, 1060),
                                                         _rect(1540, 900, 1650, 1060), _rect(1660, 900, 1700, 1060)]), also=("file",))
    case("shape rule: a polygon of two points", "shape", "has 2 points",
         lambda d: shapes(d).__setitem__("straw_posts", [[[1380, 900], [1700, 1060]]]), also=("file",))
    case("shape rule: a polygon of 61 points", "shape", "has 61 points",
         lambda d: shapes(d).__setitem__("straw_posts", [[[1380 + 5 * k, 900] for k in range(59)] + [[1700, 1060], [1380, 1060]]]), also=("file",))
    case("shape rule: a polygon that leaves the picture", "shape", "leaves the picture",
         lambda d: shapes(d).__setitem__("straw_posts", [_rect(1380, 900, 1700, 1100)]))
    case("shape rule: a polygon that crosses itself", "shape", "crosses itself",
         lambda d: shapes(d).__setitem__("straw_posts", [[[1380, 900], [1700, 1060], [1700, 900], [1380, 1060]]]))
    case("shape rule: two polygons of one shape overlap", "shape", "two of its polygons overlap",
         lambda d: shapes(d).__setitem__("straw_posts", [_rect(1380, 900, 1700, 1060), _rect(1500, 950, 1690, 1050)]))
    case("shape rule: smaller than a button", "shape", "smaller than a button",
         lambda d: shapes(d).__setitem__("straw_posts", [_rect(1590, 950, 1650, 1010)]))
    case("shape rule: more than two fifths of the picture", "shape", "of the picture (at most 40%)",
         lambda d: shapes(d).__setitem__("go_courtyard__gate", [_rect(0, 560, 1920, 1080)]))
    case("shape rule: the point outside its own shape", "shape", "is outside its own shape",
         lambda d: shapes(d).__setitem__("gateway", [[[600, 300], [690, 280], [780, 300], [790, 560], [590, 560]]]))
    case("shape rule: the point under a smaller shape", "shape", "is under the smaller shape 'straw_posts'",
         lambda d: shapes(d).__setitem__("straw_posts", _copy([_rect(1250, 940, 1700, 1060)])))
    case("shape rule: more than half of a shape under smaller shapes", "shape", "is under smaller shapes (at most 50%)",
         lambda d: (shapes(d).__setitem__("go_courtyard__gate", [_rect(1240, 940, 1700, 1080)]),
                    shapes(d).__setitem__("straw_posts", [_rect(1390, 900, 1700, 1060)])))
    case("shape rule: an id that is no hotspot or exit of the place", "shape", "no hotspot or exit of that id",
         lambda d: shapes(d).__setitem__("blackboard", [_rect(100, 880, 300, 1000)]))
    case("shape rule: a place is shaped all at once", "shape", "'gateway' has no shape and is not under keep_tile",
         lambda d: shapes(d).pop("gateway"))
    case("a hotspot that keeps its button, with its reason, passes (and is counted)", None, "",
         lambda d: (shapes(d).pop("gateway"), hot(d).__setitem__("keep_tile", {"gateway": "a test: its roof is not painted yet"})))
    case("shape rule: keep_tile without its reason", "shape", "it needs its reason, in words",
         lambda d: (shapes(d).pop("gateway"), hot(d).__setitem__("keep_tile", {"gateway": " "})), also=("file",))
    case("shape rule: keep_tile and a shape for one id", "shape", "it has a shape as well",
         lambda d: hot(d).__setitem__("keep_tile", {"gateway": "a test"}), also=("file",))
    case("shape rule (the two layers): a back hotspot's point under a front shape", "shape", "is under the front shape 'spot_vend'",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__training_yard", [1700, 590]),
                    hot(d)["spots"].__setitem__("spot_vend", [1650, 760]),
                    shapes(d).__setitem__("spot_vend", [[[1400, 400], [1920, 400], [1920, 800], [1400, 800]]]),
                    shapes(d).__setitem__("go_courtyard__training_yard", [_rect(1640, 520, 1920, 880)]),
                    d["check_courtyard"]["objects"].__setitem__("spot_vend", [1400, 400, 520, 400])))
    # check_layout's own: a keep_tile button inside a front shape
    case("a keep_tile id that is not front, its point inside a front shape", "keep-tile-front", "lies inside the front shape 'spot_vend'",
         lambda d: (shapes(d).pop("straw_posts"), hot(d).__setitem__("keep_tile", {"straw_posts": "a test"}),
                    shapes(d).__setitem__("spot_vend", [_rect(1560, 620, 1636, 1000)]),
                    d["check_courtyard"]["objects"].__setitem__("spot_vend", [1556, 616, 88, 388])))
    # a front shape: inside the foreground outline, or tight to its object
    case("a front shape that is neither inside its foreground outline nor tight to its object", "front-shape",
         "not traced tight to its object", lambda d: shapes(d).__setitem__("spot_vend", [_rect(1500, 600, 1680, 780)]))
    case("a front shape with no outline and no object's box to be tight to", "front-shape", "neither inside",
         lambda d: d.pop("check_courtyard"))
    case("a front shape inside the room's foreground outline passes", None, "",
         lambda d: d.__setitem__("check_courtyard", {"fg": {"": _rect(500, 600, 1680, 1000)}}))
    # while names are shown, two names meet
    case("a place where two names meet while names are shown", "names-meet", "meet",
         lambda d: (hot(d)["tips"].update({"go_courtyard__training_yard": "top", "spot_vend": "bottom"}),
                    hot(d)["spots"].__setitem__("go_courtyard__training_yard", [1600, 812])))
    # 5.6, step 4: the rules of where a point may be
    case("an exit outside the frame", "bounds", "outside the frame",
         lambda d: hot(d)["spots"].__setitem__("go_courtyard__school_yard", [20, 600]))
    case("a thing in the toast lane", "lane", "the toast lane",
         lambda d: (hot(d)["spots"].__setitem__("gateway", [1500, 300]), shapes(d).__setitem__("gateway", [_rect(1440, 240, 1560, 360)])))
    case("two exits under 110 px apart", "apart", "less than 110 px apart",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__gate", [1640, 945]),
                    shapes(d).__setitem__("go_courtyard__gate", [_rect(500, 940, 1700, 1080)]),
                    hot(d)["spots"].__setitem__("straw_posts", [1420, 1000]),
                    shapes(d).__setitem__("straw_posts", [_rect(1380, 900, 1560, 1060)])))
    case("an exit within 120 px of a thing", "clear", "within 120 px",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__training_yard", [1640, 790])))
    case("an exit under the arrival caption", "caption", "the arrival caption",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__school_yard", [300, 280]),
                    shapes(d).__setitem__("go_courtyard__school_yard", [[[0, 215], [330, 215], [620, 600], [620, 830], [0, 840]]])))
    case("an exit that starts above a two-line banner", "top-row", "two-line banner",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__dorm_yard", [1000, 250]),
                    shapes(d).__setitem__("go_courtyard__dorm_yard", [_rect(900, 200, 1200, 780)])))
    case("a standalone thing where someone stands", "standalone", "it has no tile to fall back to",
         lambda d: d["view_courtyard"]["slots"].__setitem__("4", [[250, -40, 0.52, 0], [545, -80, 0.48, 1], [850, -80, 0.48, 1], [1480, -40, 0.52, 0]]))
    case("a slot that leaves the stage", "stage-x", "leaves the stage",
         lambda d: d["view_courtyard"]["slots"].__setitem__("3", [[200, -40, 0.52, 0], [720, -80, 0.48, 1], [1090, -40, 0.52, 0]]))
    case("feet that are not on the floor", "floor", "are not on the floor",
         lambda d: d["view_courtyard"]["floor"].__setitem__("on", [_rect(600, 800, 1920, 1080)]))
    case("feet on a part of the floor nobody may stand on", "floor", "nobody may stand on",
         lambda d: d["view_courtyard"]["floor"].__setitem__("off", [_rect(640, 960, 760, 1060)]))
    case("people who fit the room's scale pass", None, "",
         lambda d: d["view_courtyard"].__setitem__("scale", [1750, 340, 1030]))
    case("people drawn far larger than the room's scale", "scale", "larger than the room's `scale`",
         lambda d: d["view_courtyard"].__setitem__("scale", [1750, 700, 1030]))
    case("a planned hotspot left without a point in a shaped layout", "placed", "has no point under spots",
         lambda d: (hot(d)["spots"].pop("straw_posts"), shapes(d).pop("straw_posts")), also=("shape",))
    case("a point for an id the place does not have", "point", "no exit or hotspot of that id",
         lambda d: hot(d)["spots"].__setitem__("blackboard", [300, 900]))
    case("a file with a key 3.2 does not give it", "file", "unknown key",
         lambda d: hot(d).__setitem__("front", ["spot_vend"]))
    case("a layout that breaks a fixed fact of the campus record", "campus", "at the bottom",
         lambda d: (hot(d)["spots"].__setitem__("go_courtyard__gate", [1300, 870]),
                    shapes(d).__setitem__("go_courtyard__gate", [_rect(500, 840, 1560, 1080)]),
                    hot(d)["spots"].__setitem__("straw_posts", [1640, 1000])))
    case("a map pin outside the pin frame", "pin", "outside x",
         lambda d: None, {"area_heart": {"spots": {"gate": [960, 990]}}})
    # 4.6: the icon column, in the yard with seven exits
    yard = {"hot_dorm_yard": {"spots": dict(("go_dorm_yard__" + to, [200 + 190 * k, 640 + 40 * (k % 3)]) for k, to in enumerate(
        ("boys_dorm", "dorm_common", "girls_dorm", "rooftop", "courtyard", "staff_yard", "trailhead"))),
        "tips": {"go_dorm_yard__girls_dorm": "bottom"}}}
    case("a yard whose seven exits all drop into the icon column with four people", "column", "the column holds 8",
         lambda d: None, yard)
    # ---- review 1: the refusals that had no negative test. One apiece.
    # 5.6 step 4, the yard rule: at most one exit above y 300, and three heights. The Training Yard, as the
    # campus record's own good test layout has it.
    tyard = {"hot_training_yard": {"spots": {
        "go_training_yard__training": [300, 620], "go_training_yard__courtyard": [150, 860],
        "go_training_yard__storehouse": [900, 620], "go_training_yard__staff_yard": [1180, 600],
        "go_training_yard__dojo": [1420, 620], "go_training_yard__pool": [1650, 700]},
        "tips": {"go_training_yard__storehouse": "bottom", "go_training_yard__pool": "bottom"}}}
    ty = lambda d: d["hot_training_yard"]["spots"]
    case("that yard, its six exits spread over three heights and more, passes", None, "", lambda d: None, tyard)
    case("a yard with two exits above y 300", "top-row", "at most one above y 300",
         lambda d: ty(d).update({"go_training_yard__storehouse": [900, 285], "go_training_yard__staff_yard": [1180, 285]}), tyard)
    case("a yard whose exits stand in a row (two heights for six exits)", "top-row", "not in a row",
         lambda d: ty(d).update(dict((k, [v[0], 620]) for k, v in ty(d).items() if v[1] != 860)), tyard)
    # 6.3: with three or four people, the row may not hide EVERY thing of the room
    case("a row of three, drawn very large, that hides every thing to click in the room", "slot-hides", "hides every thing",
         lambda d: d["view_courtyard"]["slots"].__setitem__("3", [[400, -40, 0.9, 0], [690, -40, 0.9, 0], [1358, -40, 0.9, 0]]),
         also=("standalone",))
    # 6.1: a person a step back stands behind the room's foreground
    case("a room with a foreground outline, and the people a step back not behind it", "floor", "are not behind it",
         lambda d: d["check_courtyard"].__setitem__("fg", {"": _rect(1200, 600, 1700, 1000)}))
    # the tool's own file (check_<place>.json): a planned front id must be a hotspot of the place, never an exit
    case("a front id that is no hotspot of the place", "file", "front id 'nope' is no hotspot",
         lambda d: d["check_courtyard"].__setitem__("front", ["nope"]))
    case("a front id that is an exit", "file", "an exit is never in the front layer",
         lambda d: d["check_courtyard"].__setitem__("front", ["go_courtyard__gate"]), also=("front-shape",))
    case("a layout made for a revision the campus record does not have for its picture", "file", "is made for revision 3",
         lambda d: hot(d).__setitem__("for_rev", 3))
    # the maps
    case("the campus map with two markers on one spot", "map", "overlap",
         lambda d: None, {"map_campus": {"anchors": {"school": [600, 500], "heart": [600, 500]}}})
    case("the campus map with a marker that runs off the map", "map", "runs off the map",
         lambda d: None, {"map_campus": {"anchors": {"school": [40, 500]}}})
    case("the campus map with the Mountain's marker off the mountain", "map", "is not on the mountain",
         lambda d: None, {"map_campus": {"anchors": {"mountain": [1290, 400]}}})
    case("an area map with a pin for a room of another area", "pin", "is not a room of this area",
         lambda d: None, {"area_heart": {"spots": {"classroom": [960, 500]}}})
    case("an area map that carries for_rev (the game's lint takes only spots there today)", "pin", "the file carries for_rev",
         lambda d: None, {"area_heart": {"spots": {}, "for_rev": 2}}, also=("file",))
    return out


# The numbers the dump gained with U0d3 (tools/smoke/u2_dump.rpy: lock_labels, frames.tag_*), as a test lays
# them over whatever dump it runs with: the cases below then read the same on a dump written before and after.
TEST_LOCK = {"training_yard": {"go_training_yard__storehouse": [484, 82]}}
TEST_TAGS = {"tag_edges": [179, 1700], "tag_gap": 8, "tag_w": 224}


def patched(dump, patch):
    """TEST ONLY: a copy of a dump's dict with a case's keys laid in: `frames` key by key; `lock_labels` whole,
    or taken out when the patch gives None."""
    d = dict(dump)
    d["frames"] = dict(d.get("frames") or {}, **patch.get("frames", {}))
    if "lock_labels" in patch:
        if patch["lock_labels"] is None:
            d.pop("lock_labels", None)
            for k in list(TEST_TAGS):
                d["frames"].pop(k, None)
        else:
            d["lock_labels"] = patch["lock_labels"]
    return d


def dump_cases():
    """[(name, files, patch for the dump, want, words)]: the two rules that read numbers the dump gained with
    U0d3. `want` is a rule that must refuse (and nothing else may), "" for a layout that passes, or
    "REPORT <rule>" for one that passes with that line reported."""
    # the yard as the campus record's own good test layout has it (tools/bgs/tests/good), the storehouse's door
    # moved 60 px down: its reason, above it, then reaches the steps to the Staff Building
    yard = {"hot_training_yard": {"spots": {
        "go_training_yard__training": [300, 620], "go_training_yard__courtyard": [150, 860],
        "go_training_yard__storehouse": [900, 620], "go_training_yard__staff_yard": [1180, 600],
        "go_training_yard__dojo": [1420, 620], "go_training_yard__pool": [1650, 700]}}}
    sided = _copy(yard)
    sided["hot_training_yard"]["tips"] = {"go_training_yard__storehouse": "left"}
    both = {"lock_labels": TEST_LOCK, "frames": TEST_TAGS}
    # (review 1) the storehouse's door at the right edge, its reason opened to the right; and high on the left,
    # its reason opened above it, where the arrival caption is
    edge = _copy(yard)
    edge["hot_training_yard"]["spots"].update({"go_training_yard__storehouse": [1650, 700], "go_training_yard__pool": [900, 620]})
    edge["hot_training_yard"]["tips"] = {"go_training_yard__storehouse": "right"}
    capt = _copy(yard)
    capt["hot_training_yard"]["spots"].update({"go_training_yard__storehouse": [300, 330]})
    capt["hot_training_yard"]["tips"] = {"go_training_yard__storehouse": "top"}
    return [
        ("a door that can be locked whose reason, opened above it, would cover another exit", yard, both,
         "lock-label", "would cover the way to"),
        ("the same door with its reason opened to its left (tips) passes", sided, both, "", ""),
        ("with a dump written before the labels were measured, the same door is only reported", yard,
         {"lock_labels": None}, "REPORT lock-label", "up to 520 by 80 px"),
        ("a door that can be locked whose reason, opened to its right, would leave the screen", edge, both,
         "lock-label", "would leave the screen"),
        ("a door that can be locked whose reason, opened above it, would lie on the arrival caption", capt, both,
         "lock-label", "would cover the arrival caption"),
        ("the whole Courtyard layout passes with the name tags' real edges", base_courtyard(), both, "", ""),
        ("a row of four whose name tags have no room between the edges", base_courtyard(),
         {"lock_labels": TEST_LOCK, "frames": dict(TEST_TAGS, tag_edges=[179, 900])}, "tag-x", "with 4 in the place"),
    ]


def dump_case_ok(want, words, out_lines, rc):
    """One dump case's verdict from the tool's printed lines and exit status."""
    refused = [l for l in out_lines if l.startswith("REFUSED")]
    if want.startswith("REPORT "):
        return rc == 0 and not refused and any(l.startswith("REPORT") and "[%s]" % want[7:] in l and words in l for l in out_lines)
    if not want:
        return rc == 0 and not refused
    return rc == 1 and bool(refused) and all("[%s]" % want in l for l in refused) and any(words in l for l in refused)


def write_case(files, folder):
    os.makedirs(folder, exist_ok=True)
    paths = []
    for stem, data in files.items():
        path = os.path.join(folder, stem + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        paths.append(path)
    return paths


def shape_cases(root=None):
    """[(what, ok)]: the game's counting functions, run here, give the answers tools/smoke/hot_shape_cases.json
    holds for its three shapes (the game's harness u2_contracts asserts the same file in the game)."""
    ns = shape_functions(root)
    with open(os.path.join(root or ROOT, "tools", "smoke", "hot_shape_cases.json"), encoding="utf-8") as f:
        c = json.load(f)
    pts = dict((k, tuple(v)) for k, v in c["points"].items())
    size, grid = tuple(c["size"]), c["grid"]
    limits = dict(c["limits"], polys=tuple(c["limits"]["polys"]), points=tuple(c["limits"]["points"]))
    count = ns["hot_shape_count"](c["shapes"], pts, size, grid)
    known = set(c["shapes"])
    find = list(ns["hot_shape_findings"]("zz_cases", c["shapes"], None, pts, known, known, limits, size))
    layers = list(ns["hot_shape_layers"]("zz_cases", c["shapes"], pts, set(c["layers"]["front"]), limits, size))
    return [
        ("hot_shape_count gives the three shapes' area, cells, twice, buried, point and under as the cases file holds them",
         dict((k, dict(v)) for k, v in count.items()) == c["expect"]),
        ("hot_shape_order puts the smallest on top (%s)" % ", ".join(c["order"]), list(ns["hot_shape_order"](c["shapes"])) == c["order"]),
        ("hot_shape_findings says the one thing the cases file expects", find == c["findings"]),
        ("hot_shape_layers, with the hall in front, says the two things the cases file expects", layers == c["layers"]["findings"]),
        ("and nothing with no shape in front, or every shape",
         ns["hot_shape_layers"]("zz_cases", c["shapes"], pts, set(), limits, size) == []
         and ns["hot_shape_layers"]("zz_cases", c["shapes"], pts, known, limits, size) == []),
    ]


def pinned(root=None):
    """[(what, ok)]: each number typed in this file still stands in the line of the game or harness it is from."""
    out = []
    for rel, text in PINNED:
        path = os.path.join(root or ROOT, rel)
        try:
            with open(path, encoding="utf-8") as f:
                ok = text in f.read()
        except OSError:
            ok = False
        out.append(("%s still holds: %s" % (rel, text[:70]), ok))
    return out


def selftest(lay, root=None):
    bad = 0
    n = 0

    def line(what, ok, detail=""):
        nonlocal bad, n
        n += 1
        if not ok:
            bad += 1
        print("%s  %s%s" % ("PASS" if ok else "FAIL", what, ("\n        | " + detail) if detail and not ok else ""))

    for what, ok in shape_cases(root) + pinned(root):
        line(what, ok)
    work = tempfile.mkdtemp(prefix="check_layout_selftest_")
    try:
        for k, (name, files, rule, words, also) in enumerate(cases()):
            out = check(read_candidate(write_case(files, os.path.join(work, "c%02d" % k)), Out()), lay, root=root)
            got = out.rules()
            if rule is None:
                line(name, not got, "; ".join(out.texts()))
            else:
                hit = [t for t in out.texts() if "[%s]" % rule in t and words in t]
                line("REFUSED by name [%s]: %s" % (rule, name), bool(hit) and set(got) <= set((rule,) + tuple(also)),
                     "refused: " + ("; ".join(out.texts()) or "nothing"))
        for k, (name, files, patch, want, words) in enumerate(dump_cases()):
            out = check(read_candidate(write_case(files, os.path.join(work, "d%02d" % k)), Out()),
                        game_layout.Layout(patched(lay.d, patch), lay.path), root=root)
            lines = ["REFUSED " + t for t in out.texts()] + ["REPORT " + t for t in out.texts("REPORT")]
            line(("REFUSED by name [%s]: %s" % (want, name)) if want and not want.startswith("REPORT") else name,
                 dump_case_ok(want, words, lines, 1 if out.rules() else 0), "; ".join(lines))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("check_layout selftest: %s (%d checks%s)" % ("FAIL" if bad else "PASS", n, ", %d failed" % bad if bad else ""))
    return 1 if bad else 0


def main(argv):
    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv):
                raise SystemExit("check_layout.py: %s needs a value" % flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    dump = game_layout.pop_dump_arg(argv)
    root, record, keep_dir, fg_dir, front = opt("--root"), opt("--record"), opt("--keep"), opt("--fg"), opt("--front")
    flags = [a for a in argv if a.startswith("--")]
    paths = [a for a in argv if not a.startswith("--")]
    # --layout is how tools/install_redo.py --compose names the files it hands over: the files follow it
    if [f for f in flags if f not in ("--selftest", "--no-campus", "--quiet", "--layout")] or (not paths and "--selftest" not in flags):
        print(__doc__)
        raise SystemExit(2)
    # Called by the installer (--layout): it has just read this dump against the tree it installs into, which
    # need not be this one (a scratch copy), and it checks the campus record itself, with the owner's waivers.
    by_installer = "--layout" in flags
    lay = game_layout.load(dump, root, check_hash=not by_installer)
    if "--selftest" in flags:
        raise SystemExit(selftest(lay, root))
    out = Out()
    cand = read_candidate(paths, out)
    if not cand and not out.lines:
        raise SystemExit("check_layout.py: no .json file in %s" % ", ".join(paths))
    check(cand, lay, root=root, record=record, keep_dir=keep_dir, fg_dir=fg_dir,
          front=[f for f in (front or "").split(",") if f], campus="--no-campus" not in flags and not by_installer, out=out)
    title = ", ".join(sorted(cand)) or ", ".join(paths)
    raise SystemExit(show(out, title, quiet="--quiet" in flags))


if __name__ == "__main__":
    main(sys.argv[1:])
