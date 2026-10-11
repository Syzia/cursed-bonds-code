"""
"The map flows": the campus record checked against itself, and every layout
checked against the record.

    python3 tools/check_campus.py                                  # the record, and what is installed
    python3 tools/check_campus.py --layout-dump shots/art/game_layout.json     # in a worktree
    python3 tools/check_campus.py --layout hot_training_yard.json [area_grounds.json ...]
                                                                   # a candidate's first-guess layout
    python3 tools/check_campus.py --sidecars <folder>              # every hot_/area_ file there, in full
    python3 tools/check_campus.py --selftest [--layout-dump <file>]

docs/UI2_DESIGN.md 5.2, K4, D14. The record is tools/bgs/campus.json
(tools/bgs/CAMPUS2.md is the same data as a page, and explains every key).
A FIXED row is a fact a picture the owner chose shows; a PROPOSED row is the
plan's words for what is not painted yet.

WHAT IT CHECKS

The record itself, always and in full:
  - every place of the game has a row, every building a look line, and no
    line a prompt may carry would fail tools/check_prompts.py;
  - the paths in the record are exactly the game's (PATH_LINKS: the yards an
    exit joins to another yard, read from the dump), no more and no fewer;
  - the fixed facts fit one ground plan: from each camera, every building an
    exit sits on lies on the side its row says, and things keep the order
    from left to right their rows give;
  - every yard of the game, and every place composed from a camera on the
    ground plan, has a view (its exit rows), and every exit the game has
    from it has its row;
  - a building named in a window line lies in the half of the ground plan
    that wall faces; in a room entered with the camera in the doorway the
    far wall faces away from the yard it is entered from; and a room's far,
    left and right walls face as its camera does (ahead, to its left, to
    its right);
  - a fixed landmark (a building that holds no place) is still named by a
    view or a window line;
  - no line a prompt may carry breaks the decency rule (K16), read as a
    line of the place it belongs to.

Each layout (an installed one from the dump, a candidate's first guess, a
test sidecar):
  - each exit's point lies in the third of the screen its side says (left of
    640, 640 to 1280, right of 1280); a place behind the camera has its exit
    in the bottom band (y 900 or lower down); exits to two things keep their
    order from left to right (two within 60 px across are not ordered);
  - a way a candidate file leaves out is checked by the point the game would
    keep for it (the dump's `default`); with no such point to read, a fixed
    way left out fails and a proposed one is reported;
  - on an area picture the pins keep the ground plan's relations (west is
    left, north is higher; 60 px of tolerance), and so do the six markers on
    the campus map (the Mountain's only as north of the other five).

WHAT COUNTS AS A FAILURE

  FAIL    a contradiction of a FIXED fact, in a candidate, a test sidecar or
          a picture at revision 2 or later. The tool names the fact in plain
          words, and such a version is not installable.
  REPORT  not a failure: a version that differs from a PROPOSAL (if the owner
          chooses it, the proposal is rewritten to match; the line names the
          proposal), and a fixed fact with a `waived` row (reported on every
          run).
  WAIT    not a failure: a yard or map whose picture is still at revision 1
          disagrees with the record on purpose; it "waits for batch N".
  NOTE    not a failure: something the game does not have yet.

Exit status 0 unless something failed; 2 when the dump is out of date ("the
game's layout has changed since the dump was written: run tools/smoke.sh
u2_dump").

FOR THE INSTALLER (tools/install_redo.py imports these): load_record,
save_record, record_hash, check_layout_files (the same check as --layout),
fix_from_layout (the facts a chosen layout fixes, written into the record),
rechoose (a picture chosen again: its facts name the new revision), add_waiver
and touched_by (the unmade pictures a rewritten proposal goes into).

Plain Python; reads tools/bgs/campus.json, the dump and game/layout/pictures.json;
writes nothing.
"""
import sys, os, json, math, hashlib, copy, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(ROOT, "tools", "bgs", "campus.json")
DUMP = os.path.join(ROOT, "tools", "art", "game_layout.json")
TESTS = os.path.join(ROOT, "tools", "bgs", "tests")
STALE = "the game's layout has changed since the dump was written: run tools/smoke.sh u2_dump"
SIDES = ("left", "ahead", "right", "bottom")
FACING = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}


# ---- reading ---------------------------------------------------------------------------------------------
def load_record(path=None):
    path = path or RECORD
    if not os.path.exists(path):
        raise SystemExit("no campus record at %s" % path)
    return json.load(open(path, encoding="utf-8"))


def save_record(record, path=None):
    """Written the one way, so the same record always has the same hash."""
    with open(path or RECORD, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=1, ensure_ascii=False)
        f.write("\n")


def record_hash(path=None):
    """sha256 of the record's bytes: what the manifest stamps a picture with."""
    return hashlib.sha256(open(path or RECORD, "rb").read()).hexdigest()


def dump_hash(files, root=None):
    """The hash u2_dump.rpy writes (docs/UI2_CONTRACTS.md A3), over the tree as it is now."""
    h = hashlib.sha256()
    game = os.path.join(root or ROOT, "game")
    for rel in files:
        with open(os.path.join(game, rel), "rb") as f:
            one = hashlib.sha256(f.read()).hexdigest()
        h.update(rel.encode("utf-8") + b"\0" + one.encode("ascii") + b"\n")
    return h.hexdigest()


def dump_files(root=None):
    game = os.path.join(root or ROOT, "game")
    out = [f for f in os.listdir(game) if f.endswith(".rpy") and not f.startswith("zz_") and not f.startswith("aa_zz_")]
    lay = os.path.join(game, "layout")
    if os.path.isdir(lay):
        out += ["layout/" + f for f in os.listdir(lay) if f.endswith(".json")]
    return sorted(out)


def load_dump(path=None, root=None, check_hash=True):
    """tools/art/game_layout.json, or the local copy a worktree names; refused when out of date."""
    path = path or DUMP
    if not os.path.exists(path):
        raise SystemExit("no layout dump at %s: run tools/smoke.sh u2_dump (in a worktree: --out <file>, then "
                         "--layout-dump <file>)" % path)
    dump = json.load(open(path, encoding="utf-8"))
    if check_hash:
        try:
            now = dump_hash(dump_files(root), root)
        except OSError:
            now = None
        if now != dump.get("hash"):
            print(STALE)
            raise SystemExit(2)
    return dump


def load_manifest(root=None, path=None):
    """game/layout/pictures.json; with no file every picture is revision 1."""
    path = path or os.path.join(root or ROOT, "game", "layout", "pictures.json")
    if not os.path.exists(path):
        return {"pictures": {}}
    return json.load(open(path, encoding="utf-8"))


def rev_of(manifest, stem):
    row = (manifest or {}).get("pictures", {}).get(stem) or {}
    return int(row.get("rev", 1))


class Rec(object):
    """The record with its rows indexed."""

    def __init__(self, record):
        self.r = record
        self.status = {}
        self.by_id = {}
        for status in ("fixed", "proposed"):
            for row in record.get(status, []):
                self.status[row["id"]] = status
                self.by_id[row["id"]] = row
        self.buildings = dict((r["key"], r) for r in self.rows("building"))
        self.places = dict((r["key"], r) for r in self.rows("place"))
        self.rules = record.get("rules", {})

    def rows(self, kind, **match):
        out = []
        for status in ("fixed", "proposed"):
            for row in self.r.get(status, []):
                if row.get("kind") == kind and all(row.get(k) == v for k, v in match.items()):
                    out.append(row)
        return out

    def is_fixed(self, row):
        return self.status.get(row["id"]) == "fixed"

    def at(self, place_or_building):
        """Where a place or a building stands on the ground plan."""
        p = self.places.get(place_or_building)
        if p is not None:
            if p.get("at"):
                return tuple(p["at"])
            b = self.buildings.get(p.get("building"))
            return tuple(b["at"]) if b else None
        b = self.buildings.get(place_or_building)
        return tuple(b["at"]) if b else None

    def building_of(self, place):
        p = self.places.get(place)
        return self.buildings.get(p["building"]) if p else None

    def chosen(self, place):
        """The record's row for the picture the owner chose of this place, or None."""
        p = self.places.get(place)
        return self.r.get("pictures", {}).get(p["stem"]) if p else None

    def waiver(self, fact_id, picture):
        for w in self.r.get("waived", []):
            if w.get("fact") == fact_id and w.get("picture") == picture:
                return w
        return None

    def name(self, key):
        row = self.places.get(key) or self.buildings.get(key)
        return row["name"] if row else key


# ---- the ground plan ---------------------------------------------------------------------------------------
def bearing(camera, facing, target):
    """Degrees to the right of straight ahead (negative: to the left), as seen from the camera."""
    fx, fy = FACING[facing]
    rx, ry = -fy, fx
    dx, dy = target[0] - camera[0], target[1] - camera[1]
    return math.degrees(math.atan2(dx * rx + dy * ry, dx * fx + dy * fy))


def side_fits(rules, side, deg):
    if side == "left":
        return deg <= rules.get("left_max_deg", -15)
    if side == "right":
        return deg >= rules.get("right_min_deg", 15)
    if side == "ahead":
        return abs(deg) <= rules.get("ahead_max_deg", 50)
    if side == "bottom":
        return abs(deg) >= rules.get("behind_min_deg", 90)
    return False


def plan_fits(rec, place, building, side):
    """Can the ground plan show this building on this side of this place's camera? None when it has no say."""
    p = rec.places.get(place) or {}
    target = rec.at(building)
    if not p.get("camera") or p.get("facing") not in FACING or target is None or tuple(p["camera"]) == target:
        return None
    return side_fits(rec.rules, side, bearing(tuple(p["camera"]), p["facing"], target))


def half_ok(faces, here, there):
    """Is `there` in the half of the plan a wall at `here` facing `faces` looks onto?"""
    fx, fy = FACING[faces]
    return (there[0] - here[0]) * fx + (there[1] - here[1]) * fy > 0


class Out(object):
    def __init__(self):
        self.lines = []

    def add(self, level, text):
        self.lines.append((level, text))

    def count(self, level):
        return sum(1 for l, _ in self.lines if l == level)

    def texts(self, level):
        return [t for l, t in self.lines if l == level]


def view_rows(rec, place):
    return rec.rows("exit", place=place) + rec.rows("seen", place=place)


# D14 and 5.2: what the two pictures the record starts from fix, whatever else changes. The last is the one
# fact a later picture is expected to meet first: the chosen Courtyard has the training hall on its right, so
# the hall is on the Courtyard's side of the Training Yard. A waiver stands beside such a fact; nothing demotes it.
START_FACTS = ("building.school_building", "building.gateway", "building.lodge_west", "building.lodge_east",
               "building.pagoda", "building.training_hall", "building.archive_wing", "building.library",
               "place.courtyard", "place.library", "exit.training_yard.training")


def viewed_places(rec, dump=None):
    """The places that must have a view in the record: every yard of the game (a hub in the dump), every
    place the record composes from a camera on the ground plan, and every place that has an exit row."""
    out = set(row["place"] for row in rec.rows("exit"))
    out.update(k for k, p in rec.places.items() if p.get("how") == "composed" and p.get("camera"))
    if dump is not None:
        out.update(p["key"] for p in dump["places"] if p["hub"])
    return sorted(out)


def check_record(rec, dump, out):
    r = rec.r
    rules = rec.rules
    sheet = r.get("sheet", [1920, 1080])
    pictures = r.get("pictures", {})

    # shapes: a fixed row names its picture and revision, a proposed row names none
    seen_ids = set()
    for status in ("fixed", "proposed"):
        for row in r.get(status, []):
            if "id" not in row or "kind" not in row:
                out.add("FAIL", "a %s row has no id or no kind: %r" % (status, row)); continue
            if row["id"] in seen_ids:
                out.add("FAIL", "two rows share the id %s" % row["id"])
            seen_ids.add(row["id"])
            by = row.get("by")
            if status == "fixed":
                pic = pictures.get((by or {}).get("picture"))
                if not by or pic is None:
                    out.add("FAIL", "fixed row %s does not name the chosen picture that fixes it" % row["id"])
                elif by.get("rev") != pic.get("rev"):
                    out.add("FAIL", "fixed row %s names revision %r of %s; the record has it at %r"
                            % (row["id"], by.get("rev"), by["picture"], pic.get("rev")))
            elif by:
                out.add("FAIL", "proposed row %s names a picture: only a fixed row may" % row["id"])
    for stem, pic in pictures.items():
        if pic.get("place") not in rec.places:
            out.add("FAIL", "the chosen picture %s names a place the record has no row for" % stem)
        elif rec.places[pic["place"]]["stem"] != stem:
            out.add("FAIL", "the chosen picture %s is not the picture of %s" % (stem, pic["place"]))

    # what a chosen picture fixes stays fixed: a fact cannot slip back to a proposal, or out of the record
    for fid in START_FACTS:
        row = rec.by_id.get(fid)
        if row is None:
            out.add("FAIL", "the record has lost %s, a fact the first chosen pictures fix (D14)" % fid)
        elif not rec.is_fixed(row):
            out.add("FAIL", "%s is a fact the first chosen pictures fix (D14); the record has it as a proposal" % fid)
    for stem, pic in sorted(pictures.items()):
        p = rec.places.get(pic.get("place"))
        if p is None:
            continue
        if not rec.is_fixed(p):
            out.add("FAIL", "%s has a chosen picture, but its own row is a proposal" % p["name"])
        if p.get("indoor"):
            rows = rec.rows("interior", room=p["key"])
            if str(pic.get("batch")) == "0" and not rows:
                out.add("FAIL", "the chosen %s has no `interior` row saying what its picture shows" % p["name"])
            for row in rows:
                if not rec.is_fixed(row):
                    out.add("FAIL", "%s says what the chosen %s shows, but is a proposal" % (row["id"], p["name"]))
        elif p.get("how") == "composed" and str(pic.get("batch")) == "0":
            # the pictures the record starts from: everything they show is fixed. A later yard fixes what its
            # layout gives a point (fix_from_layout), so the rest of its view may still be a proposal.
            view = rec.rows("exit", place=p["key"]) + rec.rows("seen", place=p["key"])
            things = [rec.buildings.get(row.get("thing")) for row in view] + [rec.building_of(p["key"])]
            for row in view + [b for b in things if b is not None]:
                if not rec.is_fixed(row):
                    out.add("FAIL", "%s is part of what the chosen %s shows, but is a proposal" % (row["id"], p["name"]))

    # every place a row, every building a look line
    for key, b in sorted(rec.buildings.items()):
        if not (b.get("look") or "").strip():
            out.add("FAIL", "%s has no look line" % b["name"])
        if not (b.get("as") or "").strip():
            out.add("FAIL", "%s has no words a prompt may call it by (`as`)" % b["name"])
        at = b.get("at") or []
        if len(at) != 2 or not (0 <= at[0] <= sheet[0] and 0 <= at[1] <= sheet[1]):
            out.add("FAIL", "%s is not on the ground plan's sheet" % b["name"])
        if b.get("court_side") and not b.get("court_seen_from"):
            out.add("FAIL", "%s has a court side and no place that sees it" % b["name"])
        for p in b.get("holds", []):
            if p not in rec.places or rec.places[p].get("building") != key:
                out.add("FAIL", "%s holds %s, but that place's row does not say so" % (b["name"], p))
    for key, p in sorted(rec.places.items()):
        b = rec.buildings.get(p.get("building"))
        if b is None:
            out.add("FAIL", "%s stands in a building the record has no row for (%r)" % (p["name"], p.get("building")))
        elif key not in b.get("holds", []):
            out.add("FAIL", "%s says it is in %s, which does not hold it" % (p["name"], b["name"]))
        if p.get("area") not in r.get("areas", {}):
            out.add("FAIL", "%s is in an area the record does not have (%r)" % (p["name"], p.get("area")))
        for a in list(p.get("after", [])) + list(p.get("refs_also", [])):
            if a not in rec.places:
                out.add("FAIL", "%s is made after %r, which is not a place" % (p["name"], a))
        if p.get("how") == "composed" and not rec.chosen(key) and not (p.get("words") or "").strip():
            out.add("FAIL", "%s is composed again and has no words to compose it from" % p["name"])
    for key, a in r.get("areas", {}).items():
        if a.get("hub") not in rec.places:
            out.add("FAIL", "the area %s has no hub among the places" % key)

    # a yard with no exit row at all has no view: its prompt would name no building, door or path
    for place in viewed_places(rec, dump):
        if place in rec.places and not rec.rows("exit", place=place):
            out.add("FAIL", "%s has no view in the record: no row says which building, door or path is on which "
                    "side of it" % rec.name(place))

    if dump is not None:
        game = dict((p["key"], p) for p in dump["places"])
        for key, p in game.items():
            row = rec.places.get(key)
            if row is None:
                out.add("FAIL", "the game's place %s (%s) has no row in the record" % (key, p["name"])); continue
            stem = os.path.splitext(os.path.basename(p["file"]))[0]
            if row["stem"] != stem:
                out.add("FAIL", "%s: the record says its picture is %s.png, the game %s.png" % (p["name"], row["stem"], stem))
            if bool(row["indoor"]) != bool(p["indoor"]):
                out.add("FAIL", "%s: the record and the game disagree about whether it is indoors" % p["name"])
            if row["area"] != p["area"]:
                out.add("FAIL", "%s: the record puts it in %s, the game in %s" % (p["name"], row["area"], p["area"]))
        later = sorted(k for k in rec.places if k not in game)
        if later:
            out.add("NOTE", "%d place%s of the record %s not in the game yet (the scaffold adds them): %s"
                    % (len(later), "" if len(later) == 1 else "s", "is" if len(later) == 1 else "are", ", ".join(later)))
        # PATH_LINKS: the yards an exit joins to another yard
        hubs = set(p["key"] for p in dump["places"] if p["hub"])
        links = set()
        for a, exits in dump["exits"].items():
            for e in exits:
                if a in hubs and e["to"] in hubs:
                    links.add(tuple(sorted((a, e["to"]))))
        paths = set(tuple(sorted((row["a"], row["b"]))) for row in rec.rows("path"))
        for a, b in sorted(links - paths):
            out.add("FAIL", "the game has a path from %s to %s that the record does not" % (rec.name(a), rec.name(b)))
        for a, b in sorted(paths - links):
            out.add("FAIL", "the record has a path from %s to %s that the game does not" % (rec.name(a), rec.name(b)))
        # every exit the game has from a viewed place has its row
        for place in viewed_places(rec, dump):
            rows = rec.rows("exit", place=place)
            known = set()
            for row in rows:
                known.add(row["to"]); known.update(row.get("alias", []))
            have = [e["to"] for e in dump["exits"].get(place, [])]
            for to in have:
                if to not in known:
                    out.add("FAIL", "the game has an exit from %s to %s; the record's view of %s has no row for it"
                            % (rec.name(place), rec.name(to), rec.name(place)))
            missing = [row["to"] for row in rows if row["to"] not in have and not set(row.get("alias", [])) & set(have)]
            if missing and place in game:
                out.add("NOTE", "%s: the record has %s the game does not have yet: %s"
                        % (rec.name(place), "an exit" if len(missing) == 1 else "exits", ", ".join(missing)))
            elif missing:
                out.add("NOTE", "%s is not in the game yet" % rec.name(place))

    # the views fit one ground plan
    for place in sorted(set(row["place"] for row in rec.rows("exit") + rec.rows("seen"))):
        p = rec.places.get(place)
        if p is None:
            out.add("FAIL", "a view row names %r, which is not a place" % place); continue
        rows = view_rows(rec, place)
        for row in rows:
            if row.get("side") not in SIDES:
                out.add("FAIL", "%s: the side %r is not one of %s" % (row["id"], row.get("side"), ", ".join(SIDES)))
            if row["kind"] == "exit" and row.get("to") not in rec.places:
                out.add("FAIL", "%s leads to %r, which is not a place" % (row["id"], row.get("to")))
            if row.get("thing") and row["thing"] not in rec.buildings:
                out.add("FAIL", "%s sits on %r, which is not a building of the record" % (row["id"], row["thing"]))
        with_thing = [row for row in rows if row.get("thing") in rec.buildings]
        if not with_thing:
            continue
        if not p.get("camera") or p.get("facing") not in FACING:
            if all(row.get("side") == "bottom" for row in rows):
                continue
            out.add("FAIL", "%s has things on its sides and no camera to see them from" % p["name"]); continue
        cam = tuple(p["camera"])
        degs = {}
        where = {"left": "on the left", "right": "on the right", "ahead": "ahead", "bottom": "behind the camera"}
        for row in with_thing:
            target = rec.at(row["thing"])
            if target == cam:
                continue
            if row.get("plan") is False:
                out.add("REPORT", "off the ground plan (the chosen picture of %s has %s %s, and the ground plan "
                        "cannot place that beside the other chosen pictures): %s"
                        % (p["name"], rec.buildings[row["thing"]]["name"], where[row["side"]], row["id"]))
                continue
            deg = degs[row["id"]] = bearing(cam, p["facing"], target)
            if not side_fits(rules, row["side"], deg):
                if rec.is_fixed(row):
                    out.add("FAIL", "the record's fixed facts do not fit one ground plan: from %s, facing %s, %s "
                            "cannot be %s (%s)" % (p["name"], p["facing"], rec.buildings[row["thing"]]["name"],
                                                  where[row["side"]], row["id"]))
                else:
                    out.add("REPORT", "a proposal does not fit the ground plan as it stands now, and is rewritten "
                            "when its picture is chosen: from %s, %s cannot be %s (%s)"
                            % (p["name"], rec.buildings[row["thing"]]["name"], where[row["side"]], row["id"]))
        ordered = sorted((row for row in with_thing if row["id"] in degs and row.get("side") != "bottom"
                          and row.get("order") is not None), key=lambda row: row["order"])
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                if a["order"] < b["order"] and degs[a["id"]] >= degs[b["id"]]:
                    both = rec.is_fixed(a) and rec.is_fixed(b)
                    out.add("FAIL" if both else "REPORT",
                            "%s: from %s, %s cannot be left of %s (%s, %s)"
                            % ("the record's fixed facts do not fit one ground plan" if both else
                               "a proposal does not fit the ground plan as it stands now", p["name"],
                               rec.buildings[a["thing"]]["name"], rec.buildings[b["thing"]]["name"], a["id"], b["id"]))

    # windows
    walls = dict(((w["room"], w["wall"]), w) for w in rec.rows("window"))
    for (room, wall), w in sorted(walls.items()):
        if room not in rec.places:
            out.add("FAIL", "%s is a window in %r, which is not a place" % (w["id"], room))
        if w.get("faces") is not None and w["faces"] not in FACING:
            out.add("FAIL", "%s faces %r" % (w["id"], w["faces"]))
    for ln in rec.rows("line"):
        w = walls.get((ln["room"], ln["wall"]))
        if w is None:
            out.add("FAIL", "%s is a window line for a wall the record has no window on" % ln["id"]); continue
        if rec.is_fixed(ln) and not rec.is_fixed(w):
            out.add("FAIL", "%s is fixed but its wall is only proposed" % ln["id"])
        here = rec.at(ln["room"])
        for need in ln.get("needs", []):
            if need not in rec.places:
                out.add("FAIL", "%s waits for %r, which is not a place" % (ln["id"], need))
        for name in ln.get("names", []):
            there = rec.at(name)
            if there is None:
                out.add("FAIL", "%s names %r, which the record has no row for" % (ln["id"], name)); continue
            if w.get("faces") in FACING and here and not half_ok(w["faces"], here, there):
                firm = rec.is_fixed(ln) or rec.is_fixed(w)
                out.add("FAIL" if firm else "REPORT",
                        "%s%s's %s window faces %s and its line names %s, which is not on that side of it"
                        % ("" if firm else "a proposal does not fit the ground plan as it stands now, and is "
                           "rewritten before its room is made: ", rec.name(ln["room"]), ln["wall"], w["faces"],
                           rec.name(name)))
    turn = {"far": 0, "right": 1, "left": 3}
    compass = ("north", "east", "south", "west")
    for (room, wall), w in sorted(walls.items()):
        p = rec.places.get(room) or {}
        if wall in turn and p.get("facing") in FACING and w.get("faces") in FACING:
            want = compass[(compass.index(p["facing"]) + turn[wall]) % 4]
            if w["faces"] != want:
                out.add("FAIL", "%s: the camera faces %s, so the %s wall faces %s; the record has it facing %s (%s)"
                        % (p["name"], p["facing"], wall, want, w["faces"], w["id"]))
    for key, p in sorted(rec.places.items()):
        if p.get("camera_in") != "doorway":
            continue
        far = walls.get((key, "far"))
        yard = rec.at(p.get("entered_from"))
        if far is None or far.get("faces") not in FACING or yard is None:
            out.add("FAIL", "%s is seen from its doorway, and the record does not say which way its far wall faces "
                    "or which yard it is entered from" % p["name"]); continue
        if half_ok(far["faces"], rec.at(key), yard):
            out.add("FAIL", "%s is entered from %s with the camera in the doorway, so its far wall must face away "
                    "from that yard; the record has it facing %s, toward it"
                    % (p["name"], rec.name(p["entered_from"]), far["faces"]))

    # a fixed landmark (a building that holds no place) is named by a view or a window line: a chosen picture
    # shows it, and the record must go on saying where
    named = set(row.get("thing") for row in rec.rows("exit") + rec.rows("seen"))
    for ln in rec.rows("line"):
        named.update(ln.get("names", []))
    for key, b in sorted(rec.buildings.items()):
        if rec.is_fixed(b) and not b.get("holds") and not b.get("ground") and key not in named:
            out.add("FAIL", "%s is fixed by the chosen %s and no view or window line of the record names it any "
                    "more: the row that said where it is seen from has gone" % (b["name"], b["by"]["picture"]))

    # nothing a prompt may carry would fail the prompt check
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import check_prompts
    for status in ("fixed", "proposed"):
        for row in r.get(status, []):
            if row.get("kind") == "interior":
                continue
            for key, text in check_prompts.prompt_lines(row):
                for f in check_prompts.findings(text, r, check_prompts.row_place(r, row)):
                    out.add("FAIL", "%s.%s would fail the prompt check: %s" % (row["id"], key, f))

    # waivers
    for w in r.get("waived", []):
        row = rec.by_id.get(w.get("fact"))
        if row is None or not rec.is_fixed(row):
            out.add("FAIL", "a waived row names %r, which is not a fixed fact" % w.get("fact"))
        if not w.get("picture") or not w.get("date"):
            out.add("FAIL", "the waiver of %r does not name its picture and the date the owner accepted it" % w.get("fact"))


# ---- a layout against the record ----------------------------------------------------------------------------
def map_name(area):
    """"Mountain" for "The Mountain", so a sentence can say "the Mountain map"."""
    return area["name"][4:] if area["name"].startswith("The ") else area["name"]


def seen_side(rules, point):
    x, y = point
    if y >= rules.get("bottom_band", 900):
        return "bottom"
    lo, hi = rules.get("thirds", [640, 1280])
    return "left" if x < lo else ("ahead" if x < hi else "right")


def third(rules, x):
    lo, hi = rules.get("thirds", [640, 1280])
    return "left" if x < lo else ("ahead" if x < hi else "right")


SIDE_WORDS = {"left": "on the left", "ahead": "in the middle", "right": "on the right",
              "bottom": "at the bottom of the picture"}


def _judge(rec, out, row_ids, what, picture, strict, batch, against=None):
    """One disagreement between a layout and the record's rows, filed by what it stands against."""
    rows = [rec.by_id[i] for i in row_ids]
    fixed = [row for row in rows if rec.is_fixed(row)]
    if not strict:
        out.add("WAIT", "waits for batch %s: %s" % (batch, what))
        return
    if fixed and len(fixed) == len(rows):
        waivers = [rec.waiver(row["id"], picture) for row in fixed]
        if all(waivers):
            out.add("REPORT", "waived (the owner accepted it on %s): %s [%s]"
                    % (waivers[0].get("date"), what, ", ".join(row["id"] for row in fixed)))
        else:
            out.add("FAIL", "%s [against the fixed fact %s]" % (against or what, ", ".join(row["id"] for row in fixed)))
    else:
        loose = [row for row in rows if not rec.is_fixed(row)]
        out.add("REPORT", "differs from a proposal, which is not a fault: %s. If this version is chosen, the "
                "record's %s rewritten to match: %s" % (what, "proposal is" if len(loose) == 1 else "proposals are",
                                                        ", ".join(row["id"] for row in loose)))


def _against(row, old):
    words = row.get("against")
    return words + old[row["id"]] if words and row["id"] in old else words


def check_exits(rec, place, spots, out, strict, batch="?", picture=None, kept=()):
    """spots: {to: (x, y)}. The exits of one place against the record's rows for it.
    kept: the keys in `spots` that a candidate file left out, so the point is the one the game would keep."""
    rules = rec.rules
    picture = picture or (rec.places[place]["stem"] if place in rec.places else place)
    rows = rec.rows("exit", place=place)
    pts, old = {}, {}
    for row in rows:
        for key in [row["to"]] + list(row.get("alias", [])):
            if key in spots:
                pts[row["id"]] = tuple(spots[key])
                if key in kept:
                    old[row["id"]] = (" (the file has no point for this way, so the game would keep its old one)")
                break
    pname = rec.name(place)
    for row in rows:
        pt = pts.get(row["id"])
        if pt is None:
            continue
        to = rec.name(row["to"])
        if row["side"] == "bottom":
            if seen_side(rules, pt) != "bottom":
                _judge(rec, out, [row["id"]], "%s: the way to %s is behind the camera, so it belongs at the bottom "
                       "of the picture; here it is at (%d, %d)%s" % (pname, to, pt[0], pt[1], old.get(row["id"], "")),
                       picture, strict, batch, _against(row, old))
            elif row.get("half") and ("left" if pt[0] < rec.r.get("sheet", [1920])[0] / 2 else "right") != row["half"]:
                _judge(rec, out, [row["id"]], "%s: the way to %s is at the bottom %s in the record; here it is at "
                       "the bottom %s%s" % (pname, to, row["half"], "left" if row["half"] == "right" else "right",
                                            old.get(row["id"], "")), picture, strict, batch, _against(row, old))
        elif third(rules, pt[0]) != row["side"]:
            now = third(rules, pt[0])
            b = rec.buildings.get(row.get("thing"))
            extra = ""
            if b is not None and rec.is_fixed(b) and plan_fits(rec, place, b["key"], now) is False:
                by = b["by"]["picture"]
                extra = (" (%s is fixed by the chosen %s, and the ground plan cannot place it %s from %s)"
                         % (b["name"], rec.name(rec.r["pictures"][by]["place"]) if by in rec.r.get("pictures", {})
                            else by, SIDE_WORDS[now], pname))
            _judge(rec, out, [row["id"]], "%s: the way to %s is %s in the record; here it is %s, at (%d, %d)%s%s"
                   % (pname, to, SIDE_WORDS[row["side"]], SIDE_WORDS[now], pt[0], pt[1], extra, old.get(row["id"], "")),
                   picture, strict, batch, _against(row, old))
    apart = rules.get("apart", 60)
    ordered = [row for row in rows if row["id"] in pts and row["side"] != "bottom" and row.get("order") is not None]
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if a["order"] == b["order"]:
                continue
            lo, hi = (a, b) if a["order"] < b["order"] else (b, a)
            xl, xh = pts[lo["id"]][0], pts[hi["id"]][0]
            if abs(xl - xh) <= apart or xl < xh:
                continue
            if third(rules, xl) != lo["side"] or third(rules, xh) != hi["side"]:
                continue        # already said, as a side
            _judge(rec, out, [lo["id"], hi["id"]], "%s: the way to %s is left of the way to %s in the record; here "
                   "it is right of it" % (pname, rec.name(lo["to"]), rec.name(hi["to"])), picture, strict, batch)


def check_pins(rec, title, pins, out, strict, batch="?", picture=None, mountain=None):
    """pins: {key: (x, y)} on one map; keys are places (an area picture) or hubs (the campus map)."""
    apart = rec.rules.get("apart", 60)
    plan = rec.rules.get("plan_apart", 60)
    keys = sorted(k for k in pins if rec.at(k) is not None)

    def rows_of(a, b):
        ids = []
        for k in (a, b):
            bd = rec.building_of(k)
            if bd is not None:
                ids.append(bd["id"])
        return ids

    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            pa, pb = rec.places.get(a), rec.places.get(b)
            if pa and pb and pa.get("building") == pb.get("building") and not (pa.get("at") or pb.get("at")):
                continue
            (ax, ay), (bx, by) = rec.at(a), rec.at(b)
            (px, py), (qx, qy) = pins[a], pins[b]
            if mountain in (a, b):
                m, o = (a, b) if mountain == a else (b, a)
                if pins[m][1] > pins[o][1] + apart:
                    _judge(rec, out, rows_of(a, b), "%s: %s's marker is not north of %s's" % (title, rec.name(m), rec.name(o)),
                           picture, strict, batch)
                continue
            for west, east, wx, ex in ((a, b, px, qx), (b, a, qx, px)):
                if rec.at(east)[0] - rec.at(west)[0] > plan and wx > ex + apart:
                    _judge(rec, out, rows_of(a, b), "%s: %s is west of %s on the ground plan, and its pin is to the "
                           "right of it" % (title, rec.name(west), rec.name(east)), picture, strict, batch)
            for north, south, ny, sy in ((a, b, py, qy), (b, a, qy, py)):
                if rec.at(south)[1] - rec.at(north)[1] > plan and ny > sy + apart:
                    _judge(rec, out, rows_of(a, b), "%s: %s is north of %s on the ground plan, and its pin is below "
                           "it" % (title, rec.name(north), rec.name(south)), picture, strict, batch)


def static_waits(rec, manifest, out):
    for w in rec.r.get("waits", []):
        if rev_of(manifest, w["picture"]) < int(w.get("until_rev", 2)):
            out.add("WAIT", "waits for batch %s: %s" % (w.get("batch", "?"), w["what"]))


def check_installed(rec, dump, manifest, out):
    """What the game draws today, from the dump: failures only from revision 2."""
    for place in sorted(set(row["place"] for row in rec.rows("exit"))):
        if place not in dump["exits"]:
            continue
        p = rec.places[place]
        spots = dict((e["to"], e["applied"]) for e in dump["exits"][place])
        check_exits(rec, place, spots, out, rev_of(manifest, p["stem"]) >= 2, p.get("batch", "?"))
    for area in dump["areas"]:
        a = rec.r.get("areas", {}).get(area["key"])
        if a is None:
            out.add("FAIL", "the game's area %s has no row in the record" % area["key"]); continue
        pins = dict((k, v["applied"]) for k, v in area["spots"].items())
        check_pins(rec, "the %s map" % map_name(area), pins, out, rev_of(manifest, a["stem"]) >= 2,
                   a.get("batch", "?"), a["stem"])
    cm = rec.r.get("campus_map", {})
    anchors = dict((rec.r["areas"][a["key"]]["hub"], a["anchor"]) for a in dump["areas"] if a["key"] in rec.r.get("areas", {}))
    hub = rec.r.get("areas", {}).get("mountain", {}).get("hub") if cm.get("mountain_only_north") else None
    check_pins(rec, "the campus map", anchors, out, rev_of(manifest, cm.get("stem", "map_campus")) >= 2,
               cm.get("batch", "?"), cm.get("stem", "map_campus"), mountain=hub)
    static_waits(rec, manifest, out)


def read_layout_file(path):
    """(kind, key, spots) for a hot_<place>.json, an area_<key>.json or a map_campus.json."""
    name = os.path.basename(path)
    data = json.load(open(path, encoding="utf-8"))
    m = re.match(r"hot_(\w+)\.json$", name)
    if m:
        place, spots = m.group(1), {}
        for key, pt in (data.get("spots") or {}).items():
            g = re.match(r"go_%s__(\w+)$" % re.escape(place), key)
            if g:
                spots[g.group(1)] = pt
        return "exits", place, spots
    m = re.match(r"area_(\w+)\.json$", name)
    if m:
        return "pins", m.group(1), dict(data.get("spots") or {})
    if name == "map_campus.json":
        return "campus", None, dict(data.get("anchors") or {})
    return None, None, None


def check_layout_files(rec, paths, out, dump=None):
    """Candidates and test sidecars: checked in full, whatever revision is installed."""
    for path in paths:
        kind, key, spots = read_layout_file(path)
        if kind == "exits":
            if key not in rec.places:
                out.add("FAIL", "%s is a layout for %r, which is not a place of the record" % (path, key)); continue
            # A way the file leaves out is not passed over: the game falls back to the point in its code
            # (the dump's `default`), so that point is checked like any other; with no such point to read,
            # the file cannot be said to agree with the record.
            spots, kept = dict(spots), set()
            defaults = dict((e["to"], e["default"]) for e in (dump or {}).get("exits", {}).get(key, [])
                            if e.get("default"))
            for row in rec.rows("exit", place=key):
                keys = [row["to"]] + list(row.get("alias", []))
                if any(k in spots for k in keys):
                    continue
                have = [k for k in keys if k in defaults]
                if have:
                    spots[have[0]] = defaults[have[0]]
                    kept.add(have[0])
                else:
                    out.add("FAIL" if rec.is_fixed(row) else "REPORT",
                            "%s: no point for the way to %s; %s%s"
                            % (os.path.basename(path), rec.name(row["to"]),
                               "the game would use its old point" if dump is not None else
                               "with no layout dump, the point the game would use instead cannot be checked",
                               " [against the fixed fact %s]" % row["id"] if rec.is_fixed(row) else
                               " (a proposal: %s)" % row["id"]))
            check_exits(rec, key, spots, out, True, rec.places[key].get("batch", "?"), kept=kept)
        elif kind == "pins":
            a = rec.r.get("areas", {}).get(key)
            if a is None:
                out.add("FAIL", "%s is a layout for the area %r, which the record does not have" % (path, key)); continue
            check_pins(rec, "the %s map" % map_name(a), spots, out, True, a.get("batch", "?"), a["stem"])
        elif kind == "campus":
            cm = rec.r.get("campus_map", {})
            anchors = {}
            if dump is not None:
                anchors = dict((rec.r["areas"][a["key"]]["hub"], a["anchor"]) for a in dump["areas"]
                               if a["key"] in rec.r.get("areas", {}))
            for akey, pt in spots.items():
                if akey in rec.r.get("areas", {}):
                    anchors[rec.r["areas"][akey]["hub"]] = pt
            hub = rec.r.get("areas", {}).get("mountain", {}).get("hub") if cm.get("mountain_only_north") else None
            check_pins(rec, "the campus map", anchors, out, True, cm.get("batch", "?"), cm.get("stem"), mountain=hub)
        # view_, pose_ and light_ files hold nothing the record speaks of


# ---- for the installer ----------------------------------------------------------------------------------------
def fix_from_layout(record, place, spots, rev, date=None, render=None, kind="composed", batch=None):
    """The facts a chosen picture's layout fixes, written into `record` (in memory).

    spots: {to: (x, y)}, the exits as laid out on the chosen picture. Each
    exit row of the place takes the side the layout shows and becomes fixed,
    with the place's own row and its ground. Returns {"rewritten": the ids of
    the proposals whose side or half changed, "moved": the buildings whose
    place on the ground plan followed, "off_plan": rows the ground plan cannot
    place beside the other chosen pictures}, so the caller can list the unmade
    pictures each touches (touched_by) and tell the owner. The caller has
    already run check_layout_files: this does not judge, it records."""
    rec = Rec(record)
    p = rec.places[place]
    stem = p["stem"]
    pic = record.setdefault("pictures", {}).setdefault(stem, {"place": place})
    pic.update({"place": place, "rev": rev, "kind": kind})
    if batch is not None: pic["batch"] = str(batch)
    if date: pic["chosen"] = date
    if render: pic["render"] = render
    by = {"picture": stem, "rev": rev}
    rewritten = []

    def fix(row):
        if row in record["proposed"]:
            record["proposed"].remove(row)
            record["fixed"].append(row)
        if not rec.waiver(row["id"], stem) or row.get("by", {}).get("picture") == stem:
            row["by"] = dict(by)

    width = record.get("sheet", [1920])[0]
    apart = rec.rules.get("apart", 60)
    placed = []
    was_fixed = set(row["id"] for row in rec.rows("exit", place=place) if rec.is_fixed(row))
    for row in rec.rows("exit", place=place):
        pt = None
        for key in [row["to"]] + list(row.get("alias", [])):
            if key in spots:
                pt = tuple(spots[key]); break
        if pt is None:
            continue
        placed.append((row, pt))
        if rec.is_fixed(row):
            continue        # a fixed fact is never rewritten here: a waiver stands beside it
        # as check_exits reads it: a row for the bottom is held to the bottom band, any other to its third
        side = seen_side(rec.rules, pt) if row["side"] == "bottom" else third(rec.rules, pt[0])
        half = ("left" if pt[0] < width / 2 else "right") if side == "bottom" and row.get("half") else None
        if side != row["side"] or (half is not None and half != row["half"]):
            rewritten.append(row["id"])
            row["side"] = side
            if half:
                row["half"] = half
            if side != "bottom":
                row.pop("half", None)
        fix(row)
    # their order from left to right, as the picture has them (two within `apart` px are not ordered).
    # Where every exit placed was already a fixed fact with its order (the Courtyard and the Library, fixed at
    # the look test), those orders stand: they are numbered among the place's `seen` rows too (the pagoda and
    # the two lodges lie between the Courtyard's exits), and a count of the exits alone would write the gateway
    # left of the lodge beside it. The caller has already checked that the layout agrees with them.
    across = sorted(((row, pt) for row, pt in placed if row["side"] != "bottom"), key=lambda rp: rp[1][0])
    stands = bool(across) and all(row["id"] in was_fixed and isinstance(row.get("order"), int) for row, pt in across) \
        and all(a[0]["order"] <= b[0]["order"] for a, b in zip(across, across[1:]))
    rank, last = 0, None
    for row, pt in ([] if stands else across):
        if last is None or pt[0] - last > apart:
            rank += 1
        last = pt[0]
        row["order"] = rank
    for row, pt in placed:
        if row["side"] == "bottom":
            row.pop("order", None)
    for row in [p] + ([rec.building_of(place)] if rec.building_of(place) is not None
                      and rec.building_of(place).get("ground") else []):
        if not rec.is_fixed(row):
            fix(row)
    # the ground plan follows the picture: a building that is still a proposal moves to the side the picture
    # has it on; one a chosen picture has already placed cannot, and the row is marked off the plan (reported
    # by check_campus.py on every run, never silently)
    moved, off = [], []
    rec = Rec(record)
    p = rec.places[place]
    if p.get("camera") and p.get("facing") in FACING:
        cam = tuple(p["camera"])
        fx, fy = FACING[p["facing"]]
        mine = [row for row, pt in placed if row.get("thing") in rec.buildings and row["side"] != "bottom"]
        for row in sorted(mine, key=lambda row: row.get("order") or 0):
            b = rec.buildings[row["thing"]]
            if plan_fits(rec, place, b["key"], row["side"]) is not False:
                continue
            if rec.is_fixed(b) or b.get("ground"):
                row["plan"] = False
                off.append(row["id"])
                continue
            same = [r2 for r2 in mine if r2["side"] == row["side"]]
            spread = (sorted(same, key=lambda r2: r2.get("order") or 0).index(row) - (len(same) - 1) / 2.0) * 22
            deg = math.radians({"left": -60, "ahead": 0, "right": 60}[row["side"]] + spread)
            dist = max(180.0, math.hypot(b["at"][0] - cam[0], b["at"][1] - cam[1]))
            ahead, right = math.cos(deg) * dist, math.sin(deg) * dist
            W, H = record.get("sheet", [1920, 1080])
            b["at"] = [int(round(min(W - 20, max(20, cam[0] + fx * ahead - fy * right)))),
                       int(round(min(H - 20, max(20, cam[1] + fy * ahead + fx * right))))]
            moved.append(b["id"])
        rec = Rec(record)
        live = [row for row in mine if row.get("plan") is not False and row.get("order") is not None]
        degs = dict((row["id"], bearing(cam, p["facing"], rec.at(row["thing"]))) for row in live)
        for a in live:
            for b2 in live:
                if a["order"] < b2["order"] and degs[a["id"]] >= degs[b2["id"]]:
                    for row in (a, b2):
                        if row["id"] in rewritten and row.get("plan") is not False:
                            row["plan"] = False
                            off.append(row["id"])
    # a proposed window in a building that moved turns to face what its line names
    if moved:
        rec = Rec(record)
        walls = dict(((w["room"], w["wall"]), w) for w in rec.rows("window"))
        for ln in rec.rows("line"):
            w = walls.get((ln["room"], ln["wall"]))
            b = rec.building_of(ln["room"])
            if w is None or b is None or b["id"] not in moved or rec.is_fixed(w) or w.get("faces") not in FACING:
                continue
            here = rec.at(ln["room"])
            there = [rec.at(n) for n in ln.get("names", []) if rec.at(n) is not None]
            if there and not all(half_ok(w["faces"], here, t) for t in there):
                dx, dy = there[0][0] - here[0], there[0][1] - here[1]
                w["faces"] = ("east" if dx > 0 else "west") if abs(dx) >= abs(dy) else ("south" if dy > 0 else "north")
                rewritten.append(w["id"])
    rechoose(record, stem, rev)       # rows this picture fixed at an earlier revision follow it
    return {"rewritten": rewritten, "moved": moved, "off_plan": off}


def rechoose(record, stem, rev, render=None, date=None):
    """The owner chose this picture again (a room rerun for its window line, an "again"): the record's row for
    it, and every fact it fixes, now name the new revision. The facts themselves do not change here."""
    pic = record.get("pictures", {}).get(stem)
    if pic is None:
        raise SystemExit("%s is not a chosen picture of the record" % stem)
    pic["rev"] = rev
    if render: pic["render"] = render
    if date: pic["chosen"] = date
    for row in record.get("fixed", []):
        if row.get("by", {}).get("picture") == stem:
            row["by"]["rev"] = rev


def add_waiver(record, fact_id, picture, rev, date, words):
    """The last rung of 5.2's ladder: a chosen picture stands against a fixed fact, with the owner's word."""
    rec = Rec(record)
    row = rec.by_id.get(fact_id)
    if row is None or not rec.is_fixed(row):
        raise SystemExit("%r is not a fixed fact of the record: only a fixed fact can be waived" % fact_id)
    if not date or not words:
        raise SystemExit("a waiver needs the date the owner accepted it and what was said to them")
    record.setdefault("waived", []).append({"fact": fact_id, "picture": picture, "rev": rev, "date": date, "words": words})


def touched_by(record, row_ids):
    """Places with no chosen picture yet whose prompt a changed row goes into."""
    rec = Rec(record)
    out = set()
    for rid in row_ids:
        row = rec.by_id.get(rid)
        if row is None:
            continue
        near = set()
        if row["kind"] in ("exit", "seen"):
            near.update([row["place"], row.get("to")])
        elif row["kind"] in ("window", "line"):
            near.add(row["room"])
        elif row["kind"] == "building":
            near.update(row.get("holds", []))
            near.update(r2["place"] for r2 in rec.rows("exit") + rec.rows("seen") if r2.get("thing") == row["key"])
        elif row["kind"] == "place":
            near.add(row["key"])
        for key in near:
            if key in rec.places and not rec.chosen(key):
                out.add(key)
        for key, area in record.get("areas", {}).items():
            if any(rec.places.get(k, {}).get("area") == key for k in near if k):
                out.add(area["stem"])
    return sorted(out)


# ---- the run ----------------------------------------------------------------------------------------------
def run(record, dump, manifest, layouts=(), sidecars=()):
    rec = Rec(record)
    out = Out()
    check_record(rec, dump, out)
    if dump is not None:
        check_installed(rec, dump, manifest, out)
    else:
        static_waits(rec, manifest, out)
    files = list(layouts)
    for folder in sidecars:
        for base, _, names in sorted(os.walk(folder)):
            files += [os.path.join(base, n) for n in sorted(names)
                      if re.match(r"(hot_|area_)\w+\.json$", n) or n == "map_campus.json"]
    check_layout_files(rec, files, out, dump)
    return out


def show(out, quiet=False):
    order = ("FAIL", "REPORT", "WAIT", "NOTE")
    for level in order:
        for text in out.texts(level):
            if not (quiet and level == "NOTE"):
                print("%-7s %s" % (level, text))
    fails = out.count("FAIL")
    tail = "%d reported, %d waiting for a batch" % (out.count("REPORT"), out.count("WAIT"))
    print("check_campus: %s" % ("PASS (%s)" % tail if not fails else "FAIL (%d; %s)" % (fails, tail)))
    return 1 if fails else 0


def selftest(dump_path=None, check_hash=True):
    fails = []

    def ok(what, cond, detail=None):
        print("  %s  %s" % ("ok  " if cond else "FAIL", what))
        if not cond:
            fails.append(what)
            for d in (detail or [])[:6]:
                print("          %s" % d)

    import tempfile, subprocess
    record = load_record()
    dump = load_dump(dump_path, check_hash=check_hash)
    manifest = {"pictures": {}}
    rec0 = Rec(record)

    out = run(record, dump, manifest)
    ok("the record passes in full, with nothing reported", out.count("FAIL") == 0 and out.count("REPORT") == 0,
       out.texts("FAIL") + out.texts("REPORT"))
    waits = " | ".join(out.texts("WAIT"))
    ok("today's Training Yard sides wait for batch 1",
       re.search(r"waits for batch 1: Training Yard: the way to Training Hall", waits) is not None, out.texts("WAIT"))
    ok("the two offices on the Staff map wait for batch 21",
       re.search(r"waits for batch 21b: the Staff Building map: (Gojo's Office is west of Utahime's Office|"
                 r"Utahime's Office is west)", waits) is not None, out.texts("WAIT"))
    ok("the hall behind today's gate waits for batch 2", "waits for batch 2: today's gate picture shows a large hall" in waits)
    lib = Rec(record)
    far = lib.by_id["window.library.far"]
    line = lib.by_id["line.library.far"]
    ok("the Library's far wall faces north and names nothing south of it",
       far["faces"] == "north" and all(lib.at(n)[1] < lib.at("library")[1] for n in line["names"]))

    swapped = os.path.join(TESTS, "swapped", "hot_training_yard.json")
    out = run(record, dump, manifest, layouts=[swapped])
    f = out.texts("FAIL")
    ok("two exits swapped against a fixed fact fail, and the fact is named",
       len(f) == 1 and "the training hall is on the far side of the yard from the Courtyard you chose" in f[0]
       and "exit.training_yard.training" in f[0], f)
    waived = copy.deepcopy(record)
    add_waiver(waived, "exit.training_yard.training", "training_yard", 2, "2026-10-07",
               "in this picture the training hall is on the far side of the yard from the Courtyard you chose")
    out = run(waived, dump, manifest, layouts=[swapped])
    ok("the same sidecar with its waived row is reported, not failed",
       out.count("FAIL") == 0 and any(t.startswith("waived") and "exit.training_yard.training" in t
                                      for t in out.texts("REPORT")), out.texts("FAIL") + out.texts("REPORT"))
    waived["waived"] = []
    out = run(waived, dump, manifest, layouts=[swapped])
    ok("with the waived row taken out it fails again", out.count("FAIL") == 1, out.texts("FAIL"))
    try:
        add_waiver(copy.deepcopy(record), "exit.training_yard.dojo", "training_yard", 2, "2026-10-07", "x")
        ok("a proposal cannot be waived", False)
    except SystemExit:
        ok("a proposal cannot be waived", True)

    proposal = os.path.join(TESTS, "proposal", "hot_training_yard.json")
    out = run(record, dump, manifest, layouts=[proposal])
    rep = out.texts("REPORT")
    ok("a layout that differs only from a proposal is accepted, and the proposal it would rewrite is reported",
       out.count("FAIL") == 0 and any("exit.training_yard.dojo" in t for t in rep)
       and any("exit.training_yard.storehouse" in t for t in rep), out.texts("FAIL") + rep)
    good = os.path.join(TESTS, "good")
    out = run(record, dump, manifest, sidecars=[good])
    ok("a layout and a map that agree with the record pass with nothing to report",
       out.count("FAIL") == 0 and out.count("REPORT") == 0, out.texts("FAIL") + out.texts("REPORT"))
    out = run(record, dump, manifest, layouts=[os.path.join(TESTS, "swapped", "area_school.json")])
    ok("a map whose pins contradict two fixed buildings fails", out.count("FAIL") >= 1, out.texts("REPORT"))
    out = run(record, dump, manifest, layouts=[os.path.join(TESTS, "swapped", "hot_library.json")])
    ok("a Library whose way out is not at the bottom of the picture fails",
       any("shows no door" in t for t in out.texts("FAIL")), out.texts("FAIL") + out.texts("REPORT"))

    # the installer's helper: choosing the proposal layout rewrites the proposals and fixes them
    chosen = copy.deepcopy(record)
    kind, key, spots = read_layout_file(proposal)
    done = fix_from_layout(chosen, key, spots, 2, date="2026-10-07", render="test_a.png", batch=1)
    rewritten = done["rewritten"]
    out = run(chosen, dump, manifest, layouts=[proposal])
    ok("fix_from_layout rewrites those proposals as fixed facts, moves the two buildings on the ground plan, and "
       "the record still passes with nothing to report",
       sorted(rewritten) == ["exit.training_yard.dojo", "exit.training_yard.storehouse", "window.dojo.side"]
       and sorted(done["moved"]) == ["building.dojo", "building.storehouse"] and not done["off_plan"]
       and out.count("FAIL") == 0 and out.count("REPORT") == 0
       and Rec(chosen).is_fixed(Rec(chosen).by_id["exit.training_yard.dojo"]),
       [repr(done)] + out.texts("FAIL") + out.texts("REPORT"))
    ok("and names the unmade pictures the change touches",
       "area_grounds" in touched_by(record, rewritten) and "dojo" in touched_by(record, rewritten), touched_by(record, rewritten))
    yard = copy.deepcopy(record)
    kind, key, spots = read_layout_file(os.path.join(TESTS, "proposal", "hot_school_yard.json"))
    done = fix_from_layout(yard, key, spots, 2, date="2026-10-07")
    out = run(yard, dump, manifest)
    ok("a chosen yard that puts a fixed building where the ground plan cannot is reported on every run, not failed",
       done["off_plan"] == ["exit.school_yard.classroom"] and out.count("FAIL") == 0
       and any("off the ground plan" in t and "exit.school_yard.classroom" in t for t in out.texts("REPORT")),
       [repr(done)] + out.texts("FAIL") + out.texts("REPORT"))
    cand = run(record, dump, manifest, layouts=[os.path.join(TESTS, "proposal", "hot_school_yard.json")])
    ok("and the owner is told so before choosing such a version",
       cand.count("FAIL") == 0 and any("School Building is fixed by the chosen Courtyard" in t for t in cand.texts("REPORT")),
       cand.texts("FAIL") + cand.texts("REPORT"))
    out = run(chosen, dump, manifest, layouts=[os.path.join(TESTS, "good", "hot_training_yard.json")])
    ok("after that, the layout the old proposals described contradicts fixed facts", out.count("FAIL") >= 1)

    court = copy.deepcopy(record)
    orders = dict((r["id"], r.get("order")) for r in Rec(court).rows("exit", place="courtyard"))
    done = fix_from_layout(court, "courtyard", {"school_yard": (330, 700), "dorm_yard": (1078, 720),
                                                "training_yard": (1530, 865), "gate": (1300, 985)}, 2, date="2026-10-11")
    out = run(court, dump, manifest)
    ok("a place whose exits were fixed before its layout sitting (the Courtyard, at the look test) keeps their order "
       "among the things seen between them, and the record still passes with the layout's facts written in",
       orders == dict((r["id"], r.get("order")) for r in Rec(court).rows("exit", place="courtyard"))
       and orders.get("exit.courtyard.dorm_yard") == 4 and not done["rewritten"] and out.count("FAIL") == 0,
       [repr(orders), repr(done)] + out.texts("FAIL"))

    again = copy.deepcopy(record)
    rechoose(again, "dorm_common", 3, render="ui2_dorm_common_a_00001_.png")
    out = run(again, dump, manifest)
    ok("a picture chosen again takes its facts to the new revision, and the record still passes",
       out.count("FAIL") == 0 and Rec(again).by_id["window.dorm_common.far"]["by"]["rev"] == 3
       and Rec(again).by_id["window.library.far"]["by"]["rev"] == 2, out.texts("FAIL"))

    # the record's own rules bite
    def broken(what, change, needle):
        bad = copy.deepcopy(record)
        change(Rec(bad), bad)
        o = run(bad, dump, manifest)
        ok(what, any(needle in t for t in o.texts("FAIL")), o.texts("FAIL"))

    broken("a window line naming something behind its wall fails",
           lambda rc, b: rc.by_id["line.library.far"]["names"].append("cafeteria"), "not on that side of it")
    broken("a far wall that faces the yard the room is entered from fails",
           lambda rc, b: rc.by_id["window.library.far"].__setitem__("faces", "south"), "must face away from that yard")
    broken("fixed facts that cannot share one ground plan fail",
           lambda rc, b: rc.by_id["building.training_hall"].__setitem__("at", [700, 760]), "not fit one ground plan")
    broken("a path the game has and the record lacks fails",
           lambda rc, b: b["proposed"].remove(rc.by_id["path.dorm_yard.trailhead"]), "that the record does not")
    broken("a path the record has and the game lacks fails",
           lambda rc, b: b["proposed"].append({"id": "path.courtyard.staff_yard", "kind": "path", "a": "courtyard",
                                               "b": "staff_yard", "words": "x"}), "that the game does not")
    broken("a building with no look line fails",
           lambda rc, b: rc.by_id["building.dojo"].__setitem__("look", ""), "has no look line")
    broken("a place of the game with no row fails",
           lambda rc, b: b["proposed"].remove(rc.by_id["place.forest"]), "has no row in the record")
    broken("a fixed row that names no picture fails",
           lambda rc, b: rc.by_id["building.pagoda"].pop("by"), "does not name the chosen picture")
    broken("a record line with a banned word fails",
           lambda rc, b: rc.by_id["building.storehouse"].__setitem__("look", "an old mossy kura"), "would fail the prompt check")

    broken("a room whose camera and whose left wall cannot both face as the record says fails",
           lambda rc, b: rc.by_id["place.cafeteria"].__setitem__("facing", "west"), "so the left wall faces south")
    broken("so does one whose far wall does not face the way the camera does",
           lambda rc, b: (rc.by_id["place.dorm_common"].pop("camera_in"),
                          rc.by_id["place.dorm_common"].__setitem__("facing", "east")), "so the far wall faces east")
    broken("a fixed landmark that no view names any more fails",
           lambda rc, b: b["fixed"].remove(rc.by_id["seen.courtyard.pagoda"]), "no view or window line of the record names it")
    broken("so does a lodge",
           lambda rc, b: b["fixed"].remove(rc.by_id["seen.courtyard.lodge_east"]), "no view or window line of the record names it")
    broken("one exit of the game with no row in the record's view fails",
           lambda rc, b: b["fixed"].remove(rc.by_id["exit.courtyard.gate"]), "the record's view of Courtyard has no row for it")

    def no_view(rc, b):
        for row in rc.rows("exit", place="school_yard"):
            b["fixed" if rc.is_fixed(row) else "proposed"].remove(row)

    broken("a yard whose whole view has gone from the record fails", no_view, "School Courtyard has no view in the record")
    gone = copy.deepcopy(record)
    no_view(Rec(gone), gone)
    o = run(gone, None, manifest)
    ok("and fails with no layout dump too", any("School Courtyard has no view" in t for t in o.texts("FAIL")), o.texts("FAIL"))
    broken("a record line against the decency rule fails",
           lambda rc, b: rc.by_id["building.pool"].__setitem__("look", "an open-air pool with students swimming in the water"),
           "K16")
    broken("so does somebody in a bedroom's words",
           lambda rc, b: rc.by_id["place.maki_room"].__setitem__("words", "a bedroom, and a girl at the desk"), "K16")

    # a candidate that leaves a way out is not passed: the point the game would keep is checked
    with tempfile.TemporaryDirectory() as tmp:
        def less(name, *drop, **kw):
            data = json.load(open(os.path.join(TESTS, "good", name), encoding="utf-8"))
            for key in drop:
                del data["spots"][key]
            if kw.get("empty"):
                data["spots"] = {}
            path = os.path.join(tmp, name)
            json.dump(data, open(path, "w"))
            return path

        o = run(record, dump, manifest, layouts=[less("hot_training_yard.json", "go_training_yard__training")])
        f = o.texts("FAIL")
        ok("a layout that leaves out the way to the Training Hall fails against the fixed fact, by the point the "
           "game would keep", len(f) == 1 and "exit.training_yard.training" in f[0]
           and "the file has no point for this way" in f[0], f + o.texts("REPORT"))
        o = run(record, dump, manifest, layouts=[less("hot_training_yard.json", empty=True)])
        ok("a layout with no points at all fails the same way",
           any("exit.training_yard.training" in t for t in o.texts("FAIL")), o.texts("FAIL"))
        o = run(record, dump, manifest, layouts=[less("hot_training_yard.json", "go_training_yard__pool")])
        ok("a way the game does not have yet, left out, is reported when its row is a proposal",
           o.count("FAIL") == 0 and any("no point for the way to Swimming Pool" in t for t in o.texts("REPORT")),
           o.texts("FAIL") + o.texts("REPORT"))
        o = run(record, None, manifest, layouts=[less("hot_training_yard.json", "go_training_yard__training")])
        ok("with no layout dump, a fixed way left out fails outright",
           any("no point for the way to Training Hall" in t and "exit.training_yard.training" in t for t in o.texts("FAIL")),
           o.texts("FAIL"))

    # a fact a chosen picture fixes cannot be moved to the proposals, or dropped
    def demoted(rid):
        r2 = copy.deepcopy(record)
        row = [r for r in r2["fixed"] if r["id"] == rid][0]
        r2["fixed"].remove(row)
        row.pop("by", None)
        r2["proposed"].append(row)
        return run(r2, dump, manifest)

    def dropped(rid):
        r2 = copy.deepcopy(record)
        r2["fixed"] = [r for r in r2["fixed"] if r["id"] != rid]
        return run(r2, dump, manifest)

    for rid in ("building.training_hall", "exit.training_yard.training", "exit.courtyard.dorm_yard",
                "seen.courtyard.lodge_west", "building.archive_wing", "place.dorm_common", "interior.cafeteria"):
        o = demoted(rid)
        token = "%s has a chosen picture" % rec0.by_id[rid]["name"] if rid.startswith("place.") else rid
        ok("%s moved to the proposals fails" % rid,
           any(token in t and "proposal" in t for t in o.texts("FAIL")), o.texts("FAIL"))
    o = dropped("interior.library")
    ok("the chosen Library's interior row removed fails",
       any("the chosen Library has no `interior` row" in t for t in o.texts("FAIL")), o.texts("FAIL"))
    o = dropped("exit.training_yard.training")
    ok("the Training Yard's fixed fact removed fails",
       any("has lost exit.training_yard.training" in t for t in o.texts("FAIL")), o.texts("FAIL"))

    # a picture at revision 2 is held to the fixed facts; at revision 1 it waits
    d2 = copy.deepcopy(dump)
    for e in d2["exits"]["courtyard"]:
        if e["to"] == "training_yard":
            e["applied"] = [200, 700]
    o1 = run(record, d2, {"pictures": {}})
    o2 = run(record, d2, {"pictures": {"courtyard": {"rev": 2, "kind": "composed"}}})
    ok("an installed yard against a fixed fact waits at revision 1 and fails from revision 2",
       o1.count("FAIL") == 0 and any("Courtyard: the way to Training Yard" in t for t in o1.texts("WAIT"))
       and any("not on the right of the Courtyard" in t for t in o2.texts("FAIL")), o1.texts("FAIL") + o2.texts("FAIL"))

    # an out-of-date dump is refused in one line
    with tempfile.TemporaryDirectory() as tmp:
        stale = copy.deepcopy(dump)
        stale["hash"] = "0" * 64
        path = os.path.join(tmp, "game_layout.json")
        json.dump(stale, open(path, "w"))
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--layout-dump", path],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        ok("a dump whose hash is out of date is refused in one line", p.returncode == 2 and p.stdout.strip() == STALE,
           [p.stdout])
    print("check_campus selftest: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


def main(argv):
    def opt(flag, many=False):
        vals = []
        while flag in argv:
            i = argv.index(flag)
            j = i + 1
            while j < len(argv) and not argv[j].startswith("--"):
                vals.append(argv[j]); j += 1
                if not many:
                    break
            if j == i + 1:
                raise SystemExit("%s needs a value" % flag)
            del argv[i:j]
        return vals if many else (vals[0] if vals else None)

    dump_path = opt("--layout-dump")
    record_path = opt("--record")
    manifest_path = opt("--manifest")
    layouts = opt("--layout", many=True)
    sidecars = opt("--sidecars", many=True)
    no_hash = "--no-hash" in argv
    if no_hash: argv.remove("--no-hash")
    quiet = "--quiet" in argv
    if quiet: argv.remove("--quiet")
    if "--selftest" in argv:
        raise SystemExit(selftest(dump_path, not no_hash))
    if argv:
        print(__doc__); raise SystemExit(2)
    for path in layouts:
        if not os.path.exists(path):
            raise SystemExit("no layout file at %s" % path)
    record = load_record(record_path)
    dump = load_dump(dump_path, check_hash=not no_hash)
    manifest = load_manifest(path=manifest_path)
    out = run(record, dump, manifest, layouts, sidecars + [TESTS + "/good"] if os.path.isdir(TESTS + "/good") else sidecars)
    raise SystemExit(show(out, quiet))


if __name__ == "__main__":
    main(sys.argv[1:])
