"""
The one reader of tools/art/game_layout.json: how every art tool learns the
game's numbers.

    import game_layout
    lay = game_layout.load(game_layout.pop_dump_arg(argv))     # refuses, in one line, a dump that is out of date
    lay.bg_stem("dorm")                # "your_room"
    lay.points("dorm_common")          # every exit and hotspot of the room, with the point the game draws
    python3 tools/game_layout.py [--layout-dump <file>]        # says whether the dump is fresh, and what it holds

docs/UI2_DESIGN.md 5.4 and D47. The dump is written by a small harness
(`tools/smoke.sh u2_dump`) and carries a hash of the files it was read from:
every `game/*.rpy` and every `game/layout/*.json`. A tool that finds the hash
out of date prints exactly

    the game's layout has changed since the dump was written: run tools/smoke.sh u2_dump

and exits with status 2, so nothing is ever proved round an old set of points.

IN A WORKTREE the committed dump is out of date by design (every package
edits files it is read from), and it is never committed from there. Write a
local copy and name it:

    tools/smoke.sh u2_dump --out shots/art/game_layout.json
    python3 tools/<tool>.py ... --layout-dump shots/art/game_layout.json

This file replaces the regular expressions make_fg.py, install_pose.py and
make_pose_workflow.py each used to read game/sb_world.rpy with.

WHAT THE DUMP DOES NOT HOLD YET. The asleep, away and home tables
(WORLD_ASLEEP, WORLD_AWAY, WORLD_HOMES) are read from the keys `world_asleep`
({"weekday": [who], "weekend": [who]}), `world_away` ({who: [[weekday,
period, district], ...]}) and `world_homes` ({who: place}) when the dump has
them. Until u2_dump writes them, `asleep` and `away` below answer None ("not
known"), and the pose tools take the careful side: two boxes are assumed to
show together, and a row in a Tokyo district is refused.

Plain Python.
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_campus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = check_campus.DUMP
STALE = check_campus.STALE
WEEKEND_DAYS = ("Sat", "Sun")
HOURS = ("", "evening", "night")
# K16: nobody is painted here, ever.
NO_POSE_PLACES = ("bathhouse", "sauna", "pool")


def pop_dump_arg(argv):
    """The value of --layout-dump, taken out of argv; None when it is not given."""
    if "--layout-dump" not in argv:
        return None
    i = argv.index("--layout-dump")
    if i + 1 >= len(argv):
        raise SystemExit("--layout-dump needs a file: the local dump tools/smoke.sh u2_dump --out <file> wrote")
    v = argv[i + 1]
    del argv[i:i + 2]
    return v


def load(path=None, root=None, check_hash=True):
    """The dump as a Layout. `root` is the tree the dump describes (default: this one)."""
    return Layout(check_campus.load_dump(path, root, check_hash), path or DUMP)


class Layout(object):
    def __init__(self, dump, path=None):
        self.d = dump
        self.path = path
        self._places = dict((p["key"], p) for p in dump.get("places", []))

    # ---- places and their pictures
    def has_place(self, key):
        return key in self._places

    def place(self, key):
        p = self._places.get(key)
        if p is None:
            raise SystemExit("no place %r in the game (the layout dump's `places`)" % key)
        return p

    def name(self, key):
        return self._places[key]["name"] if key in self._places else key

    def bg_stem(self, key):
        """The file stem of a place's day picture: "your_room" for "dorm"."""
        return os.path.splitext(os.path.basename(self.place(key)["file"]))[0]

    def bg_path(self, key, variant="", root=None):
        """game/images/bg/<stem>[_<variant>].png under `root`."""
        rel = os.path.dirname(self.place(key)["file"])
        return os.path.join(root or ROOT, "game", rel, self.bg_stem(key) + ("_" + variant if variant else "") + ".png")

    def place_of_stem(self, stem):
        for key, p in self._places.items():
            if os.path.splitext(os.path.basename(p["file"]))[0] == stem:
                return key
        return None

    def indoor(self, key):
        return bool(self.place(key)["indoor"])

    def periods_showing(self, key, variant):
        """The periods at which the picture `variant` of a place is the one on screen, as far as the dump
        knows, on the wide side: an hour picture that is not made yet is counted for its own hour too."""
        variants = self.place(key).get("variants") or {}
        out = set(p for p in self.d.get("periods", []) if (variants.get(p) or "") == variant)
        if variant == "evening":
            out.add("Evening")
        if variant == "night":
            out.add("Night")
        return out

    # ---- the points of a room
    def exits(self, place):
        return list(self.d.get("exits", {}).get(place, []))

    def hotspots(self, place):
        return list(self.d.get("hotspots", {}).get(place, []))

    def planned(self, place):
        """[(id, kind)] of SPOT_PLANNED for a place (empty until the scaffold defines it)."""
        return [(row[0], row[2]) for row in self.d.get("spot_planned", []) if row[1] == place]

    def points(self, place, root=None):
        """Every exit and hotspot of a place, as {kind, id, name, at}: `at` is the point the game draws.
        A planned hotspot that is not registered yet is read from the room's hot_ sidecar under `root`."""
        out = []
        for e in self.exits(place):
            out.append({"kind": "exit", "id": e["id"], "name": "the way to %s" % self.name(e["to"]),
                        "at": tuple(e["applied"])})
        seen = set()
        for h in self.hotspots(place):
            seen.add(h["id"])
            out.append({"kind": "hotspot", "id": h["id"], "name": "the hotspot %s" % h["id"],
                        "at": tuple(h["applied"])})
        planned = [pid for pid, _kind in self.planned(place) if pid not in seen]
        if planned:
            side = os.path.join(root or ROOT, "game", "layout", "hot_%s.json" % place)
            spots = {}
            if os.path.exists(side):
                try:
                    spots = json.load(open(side, encoding="utf-8")).get("spots") or {}
                except ValueError:
                    spots = {}
            for pid in planned:
                pt = spots.get(pid)
                if isinstance(pt, list) and len(pt) == 2:
                    out.append({"kind": "hotspot", "id": pid, "name": "the planned hotspot %s" % pid,
                                "at": (pt[0], pt[1])})
        return out

    def slots(self, place):
        return self.d.get("slots", {}).get(place, {})

    def slot_feet(self, place):
        """[(n people, x, y)]: where the soles of each standing row touch the floor."""
        H = self.d.get("screen", [1920, 1080])[1]
        ch = self.d.get("frames", {}).get("sprite", [760, 1400])[1]
        out = []
        for n, rows in sorted(self.slots(place).items()):
            for row in rows:
                xc, yoff, zoom = row[0], row[1], row[2]
                out.append((int(n), int(round(xc)), int(round(H + yoff - (ch - 1365) * zoom))))
        return out

    def poses(self, place):
        return dict(self.d.get("poses", {}).get(place, {}))

    def fg_rooms(self):
        return list(self.d.get("fg_rooms", []))

    # ---- who is where
    def districts(self):
        """The Tokyo districts WORLD_AWAY sends anyone to; None when the dump has no such table."""
        away = self.d.get("world_away")
        if away is None:
            return None
        return sorted(set(cell[2] for rows in away.values() for cell in rows))

    def away(self, who, day, period):
        """The district a person is in at that hour, "" for none, None when the dump has no table."""
        away = self.d.get("world_away")
        if away is None:
            return None
        for cell in away.get(who, []):
            if cell[0] == day and cell[1] == period:
                return cell[2]
        return ""

    def where(self, who, day, period):
        """The place the routine puts a person at (a district when they are away); None for nowhere."""
        d = self.away(who, day, period)
        if d:
            return d
        cell = None
        if day in WEEKEND_DAYS:
            cell = (self.d.get("weekend", {}).get(who) or {}).get(period)
        if cell is None:
            cell = (self.d.get("schedule", {}).get(who) or {}).get(period)
        return None if cell in (None, "-", "") else cell

    def asleep(self, who, day, period):
        """True, False, or None when the dump has no asleep table."""
        if period != "Night":
            return False
        table = self.d.get("world_asleep")
        if table is None:
            return None
        if who not in table.get("weekend" if day in WEEKEND_DAYS else "weekday", []):
            return False
        homes = self.d.get("world_homes") or {}
        return homes.get(who) is None or self.where(who, day, period) == homes.get(who)

    def cells(self):
        return [(day, per) for day in self.d.get("weekdays", []) for per in self.d.get("periods", [])]


def main(argv):
    path = pop_dump_arg(argv)
    if argv:
        print(__doc__); raise SystemExit(1)
    lay = load(path)
    d = lay.d
    print("%s is up to date (hash %s...)" % (lay.path, d.get("hash", "")[:12]))
    print("  %d places, %d exits, %d hotspots, %d planned hotspots, %d pose boxes"
          % (len(d.get("places", [])), sum(len(v) for v in d.get("exits", {}).values()),
             sum(len(v) for v in d.get("hotspots", {}).values()), len(d.get("spot_planned", [])),
             sum(len(v) for v in d.get("poses", {}).values())))
    for key, words in (("world_asleep", "the asleep table"), ("world_away", "the away table"),
                       ("world_homes", "the home table")):
        print("  %s: %s" % (words, "in the dump" if key in d else "NOT in the dump yet (see the top of this file)"))


if __name__ == "__main__":
    main(sys.argv[1:])
