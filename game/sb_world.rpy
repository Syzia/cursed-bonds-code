################################################################################
## Cursed Bonds — the world: clock, campus map, character schedules.
################################################################################

init -2 python:

    PERIODS = ["Morning", "Noon", "Afternoon", "Evening", "Night"]
    WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    ## Campus ------------------------------------------------------------------
    ## The map groups these places into AREAS (below); it no longer reads x/y.
    ## x/y are kept only for tools/genworld.py, which paints map_campus.png
    ## (its NODES list).

    LOCATIONS = {
        "gate": dict(
            indoor=False, name="Main Gate", bg="bg gate", x=960, y=975,
            desc="The torii, the long stone path, and the only road down the mountain."),
        "courtyard": dict(
            indoor=False, name="Courtyard", bg="bg courtyard", x=960, y=815,
            desc="The middle of everything. Somebody is always crossing it."),
        "classroom": dict(
            indoor=True, name="Classroom Building", bg="bg classroom", x=600, y=735,
            desc="Rows of desks for a class of thirty. Four of them are used. Lessons are rare and unannounced."),
        "cafeteria": dict(
            indoor=True, name="Cafeteria", bg="bg cafeteria", x=330, y=860,
            desc="Everyone passes through here at noon. Nobody misses a meal twice."),
        "training": dict(
            indoor=True, name="Training Hall", bg="bg training", x=1330, y=735,
            desc="Bigger inside than the building it's in. Nobody explains this."),
        "dojo": dict(
            indoor=True, name="Dojo", bg="bg dojo", x=1640, y=845,
            desc="Wooden floor, weapon rack, and Maki Zenin's standing appointment."),
        "dorm_common": dict(
            indoor=True, name="Dorm Common Room", bg="bg dorm_common", x=735, y=660,
            desc="Sofa, low table, a television nobody agrees on."),
        "dorm": dict(
            indoor=True, name="Your Room", bg="bg your_room", x=735, y=545,
            desc="A bed, a desk, and a window that faces the mountain."),
        "girls_dorm": dict(
            indoor=True, name="Girls' Dormitory", bg="bg girls_dorm", x=1175, y=545,
            desc="A corridor of doors. I don't go in uninvited."),
        "rooftop": dict(
            indoor=False, name="Rooftop", bg="bg rooftop", x=960, y=455,
            desc="A hundred kilometres of view and nobody to interrupt."),
        "infirmary": dict(
            indoor=True, name="Infirmary", bg="bg infirmary", x=350, y=610,
            desc="Shoko Ieiri's domain. Smells of antiseptic and, faintly, cigarettes."),
        "office": dict(
            indoor=True, name="Principal's Office", bg="bg office", x=1560, y=560,
            desc="Where missions are handed out and excuses are not accepted."),
        "utahime_office": dict(
            indoor=True, name="Utahime's Office", bg="bg utahime_office", x=1480, y=560,
            desc="Neat, traditional, and a mission board already fuller than Yaga's ever was."),
        "gojo_office": dict(
            indoor=True, name="Gojo's Office", bg="bg gojo_office", x=1640, y=560,
            desc="Sweets on every surface and a television the size of a door."),
        "storehouse": dict(
            indoor=True, name="Storehouse", bg="bg storehouse", x=1745, y=675,
            desc="Cursed tools, sealed boxes, and a smell like a struck match."),
        "forest": dict(
            indoor=False, name="Forest Trail", bg="bg forest", x=290, y=335,
            desc="Forty minutes of trees. Megumi comes here to find the edge of himself."),
        "riverside": dict(
            indoor=False, name="Riverside", bg="bg riverside", x=640, y=225,
            desc="Cold, clear, and deep enough to swim if you're brave about it."),
        "ridge": dict(
            indoor=False, name="Mountain Ridge", bg="bg ridge", x=1290, y=215,
            desc="Above the treeline, as far as the rope markers. Higher up, the veil."),
    }

    LOC_ORDER = ["gate", "courtyard", "classroom", "cafeteria", "training", "dojo",
                 "dorm_common", "dorm", "girls_dorm", "rooftop", "infirmary",
                 "office", "utahime_office", "gojo_office", "storehouse",
                 "forest", "riverside", "ridge"]

    ## Areas (3.2, WP1) ----------------------------------------------------------
    ## The map's six cards, in order. anchor is the card centre on
    ## map_campus.png. Every LOCATIONS key belongs to exactly one area (the
    ## validator checks it).

    AREAS = [
        dict(key="heart",    name="Courtyard & Gate",  seal="門",
             places=["gate", "courtyard"],                              anchor=(960, 900)),
        dict(key="school",   name="Classrooms",        seal="校",
             places=["classroom", "cafeteria", "infirmary"],            anchor=(420, 740)),
        dict(key="dorms",    name="Dormitories",       seal="寮",
             places=["dorm", "dorm_common", "girls_dorm", "rooftop"],   anchor=(900, 560)),
        dict(key="staff",    name="Staff Building",    seal="職",
             places=["office", "utahime_office", "gojo_office"],        anchor=(1560, 440)),
        dict(key="grounds",  name="Training Grounds",  seal="練",
             places=["training", "dojo", "storehouse"],                 anchor=(1560, 760)),
        dict(key="mountain", name="The Mountain",      seal="山",
             places=["forest", "riverside", "ridge"],                   anchor=(740, 290)),
    ]

    AREA_BY_KEY = {a["key"]: a for a in AREAS}

    ## Schedules ---------------------------------------------------------------
    ## Weekday routine. "-" means the character is off campus this period.

    SCHEDULE = {
        "yuji":   {"Morning": "training",  "Noon": "cafeteria", "Afternoon": "courtyard",
                   "Evening": "dorm_common", "Night": "dorm_common"},
        "megumi": {"Morning": "classroom", "Noon": "cafeteria", "Afternoon": "forest",
                   "Evening": "dorm_common", "Night": "-"},
        "nobara": {"Morning": "classroom", "Noon": "cafeteria", "Afternoon": "courtyard",
                   "Evening": "dorm_common", "Night": "girls_dorm"},
        "maki":   {"Morning": "dojo",      "Noon": "dojo",      "Afternoon": "training",
                   "Evening": "riverside", "Night": "girls_dorm"},
        "panda":  {"Morning": "courtyard", "Noon": "cafeteria", "Afternoon": "training",
                   "Evening": "dorm_common", "Night": "dorm_common"},
        "toge":   {"Morning": "ridge",     "Noon": "cafeteria", "Afternoon": "rooftop",
                   "Evening": "dorm_common", "Night": "-"},
        "shoko":  {"Morning": "infirmary", "Noon": "infirmary", "Afternoon": "infirmary",
                   "Evening": "rooftop",   "Night": "infirmary"},
        "yaga":   {"Morning": "office",    "Noon": "office",    "Afternoon": "storehouse",
                   "Evening": "office",    "Night": "-"},
        "gojo":   {"Morning": "-",         "Noon": "-",         "Afternoon": "-",
                   "Evening": "-",         "Night": "-"},
        "utahime": {"Morning": "utahime_office", "Noon": "utahime_office",
                    "Afternoon": "utahime_office", "Evening": "cafeteria", "Night": "-"},
        "ijichi": {"Morning": "gate",      "Noon": "gate",      "Afternoon": "gate",
                   "Evening": "-",         "Night": "-"},
    }

    ## Weekends shake the board up.
    WEEKEND = {
        "yuji":   {"Morning": "dorm_common", "Afternoon": "riverside", "Evening": "cafeteria"},
        "megumi": {"Morning": "forest",      "Afternoon": "ridge"},
        "nobara": {"Morning": "girls_dorm",  "Afternoon": "riverside", "Evening": "courtyard"},
        "maki":   {"Morning": "dojo",        "Afternoon": "riverside", "Evening": "dojo"},
        "panda":  {"Afternoon": "riverside"},
        "toge":   {"Morning": "rooftop",     "Afternoon": "riverside"},
        "shoko":  {"Afternoon": "rooftop"},
        "yaga":   {"Morning": "-", "Noon": "-", "Afternoon": "-", "Evening": "-"},
        "utahime": {"Afternoon": "-", "Evening": "courtyard"},
    }

    ## Schedules by flag (D13). Entries are (flag, who, table_or_None): while
    ## the flag is set, the table ({period: place or "-"}) replaces that
    ## character's whole routine, weekends included, and None means off
    ## campus. The last matching entry wins; story pins (schedule_overrides)
    ## still win over it. Phase 3 adds Utahime leaving to lead Kyoto and
    ## Yuji's absence here; phase 1 ships it empty.
    FLAG_SCHEDULES = []

    ## Gojo is never where you expect him.
    GOJO_SPOTS = ["-", "-", "-", "rooftop", "courtyard", "office", "cafeteria", "training"]

    ## On the days he's in (D17), Gojo keeps office hours for these periods
    ## and roams the rest.
    GOJO_IN_PERIODS = ("Morning", "Noon", "Afternoon")

    ## An in-day comes about 1 day in 6 (a draw seeded by the day), never two
    ## days running, and never more than GOJO_MAX_GAP days in a row without one.
    GOJO_IN_CHANCE = 1.0 / 6
    GOJO_MAX_GAP = 8

    ## Lighting ----------------------------------------------------------------
    ##
    ## One authored image per place, tinted at runtime so a room reads as the
    ## hour you are actually standing in it. Interiors get a gentler curve than
    ## outdoors, because a lit corridor at midnight is not a blue field.

    OUTDOOR_GRADE = {
        "Morning":   ("#ffe9d0", 0.02),
        "Noon":      ("#ffffff", 0.05),
        "Afternoon": ("#ffdcb4", 0.00),
        "Evening":   ("#ff9d6b", -0.12),
        "Night":     ("#6f86d8", -0.34),
    }
    INDOOR_GRADE = {
        "Morning":   ("#fff2e0", 0.00),
        "Noon":      ("#ffffff", 0.03),
        "Afternoon": ("#ffeeda", 0.00),
        "Evening":   ("#ffd0a8", -0.06),
        "Night":     ("#a8b4e0", -0.20),
    }

    ## Places with a genuinely different picture for an hour, not just a tint:
    ## period -> the image's attribute ("bg rooftop evening"). Each is relit
    ## from the day picture, so it is recognisably the same place.
    TIME_VARIANT = {
        "dorm":      {"Evening": "night", "Night": "night"},
        "infirmary": {"Night": "night"},
        "rooftop":   {"Evening": "evening", "Night": "night"},
        "riverside": {"Evening": "evening"},
        "dorm_common": {"Evening": "evening", "Night": "night"},
        "girls_dorm":  {"Night": "night"},
    }

    def bg_variant(loc, per):
        return TIME_VARIANT.get(loc, {}).get(per)

    def bg_name(loc=None, per=None):
        loc = loc or store.here
        per = per or store.period
        if loc not in LOCATIONS:
            return "bg black"          # story scenes may sit outside the campus
        base = LOCATIONS[loc]["bg"]
        v = bg_variant(loc, per)
        if v:
            base += " " + v
        return base

    ## Built once per (place, period) and held outside the store, so screens
    ## don't churn a new Transform every interaction and saves stay small.
    _BG_CACHE = {}

    def graded_bg(loc=None, per=None):
        """The location background, lit for the current period."""
        loc = loc or store.here
        per = per or store.period
        key = (loc, per)
        if key in _BG_CACHE:
            return _BG_CACHE[key]
        img = bg_name(loc, per)
        if loc not in LOCATIONS:
            return img
        v = bg_variant(loc, per)
        if v:
            ## The image is already painted for its hour; grading it again
            ## crushes it. A night picture standing in for the evening gets
            ## a warm touch.
            tint, bright = (("#ffd8b8", -0.04) if (v == "night" and per == "Evening") else ("#ffffff", 0.0))
        else:
            table = INDOOR_GRADE if LOCATIONS.get(loc, {}).get("indoor") else OUTDOOR_GRADE
            tint, bright = table.get(per, ("#ffffff", 0.0))
        if tint == "#ffffff" and abs(bright) < 0.001:
            _BG_CACHE[key] = img
            return img
        d = Transform(img, matrixcolor=TintMatrix(tint) * BrightnessMatrix(bright))
        d._light_key = key          # lets lighting.rpy light the characters to match
        _BG_CACHE[key] = d
        return d

    ## Clock -------------------------------------------------------------------

    def period_index():
        return PERIODS.index(store.period)

    def weekday():
        return WEEKDAYS[(store.day - 1) % 7]

    def is_weekend():
        return weekday() in ("Sat", "Sun")

    def advance_period(n=1):
        """Move the clock forward. Returns True if the day rolled over."""
        rolled = False
        for _ in range(n):
            i = period_index()
            if i >= len(PERIODS) - 1:
                rolled = True
                new_day()
            else:
                store.period = PERIODS[i + 1]
        renpy.restart_interaction()
        return rolled

    def new_day():
        """Everything that resets, resets here — not in the sleep action, so a
        day that rolls over because you waited through Night behaves the same.
        (WP1 adds the vitals and the dawn HP refill, D26, and Gojo's in-day
        toast, D17.)"""
        store.day += 1
        store.period = PERIODS[0]
        store.talked_today = set()
        store.spent_today = set()
        store.actions_today = set()
        store.companion = None
        store.stamina = store.stamina_max
        store.ce = store.ce_max
        refresh_vitals()
        store.hp = store.hp_max
        roll_gojo()
        if gojo_in_today():
            toast("Gojo is in today.", "info", "gojo")
        run_new_day_hooks()     # keep last: hooks see the finished new day

    def roll_gojo():
        """Where Gojo roams today, one spot per period (seeded by the day).
        On his in-days (gojo_in_on) he keeps office hours instead for
        GOJO_IN_PERIODS. The roaming draws are unchanged from before phase 1."""
        import random as _r
        rnd = _r.Random(store.day * 977 + 13)
        spots = {p: rnd.choice(GOJO_SPOTS) for p in PERIODS}
        store.gojo_in = gojo_in_on(store.day)
        if store.gojo_in:
            for p in GOJO_IN_PERIODS:
                spots[p] = "gojo_office"
        store.gojo_today = spots

    ## Gojo's in-days (D17) --------------------------------------------------------
    ##
    ## A fixed chain over day numbers, so it never depends on when you look:
    ## _GOJO_CHAIN[d] is True when day d would be an in-day. It is built once
    ## outside the saved store (a builtins list, like the toast queue) and
    ## only ever extended.

    import builtins as _gojo_builtins
    _GOJO_CHAIN = _gojo_builtins.list([False])      # day 0: never

    def _gojo_draw(d):
        import random as _r
        return _r.Random(d * 131 + 7).random() < GOJO_IN_CHANCE

    def _gojo_chain(d):
        c = _GOJO_CHAIN
        while len(c) <= d:
            i = len(c)
            if c[i - 1]:
                v = False                       # never two days running
            else:
                last = 0
                for j in range(i - 1, 0, -1):
                    if c[j]:
                        last = j
                        break
                v = _gojo_draw(i) or (i - last > GOJO_MAX_GAP)
            c.append(v)
        return c[d]

    def gojo_in_on(day):
        """WP1. True when Gojo keeps office hours on this day: about 1 day in 6,
        seeded by the day, never two days running (D17). Always False until
        his first lesson (flag intensive_done)."""
        if not has_flag("intensive_done"):
            return False
        try:
            day = int(day)
        except Exception:
            return False
        if day < 1:
            return False
        return _gojo_chain(day)

    def gojo_in_today():
        """WP1. True on the days Gojo is in his office (set each morning by
        roll_gojo, D17)."""
        return bool(store.gojo_in)

    ## Presence ----------------------------------------------------------------

    def flag_schedule(who):
        """WP1. (True, table_or_None) when a FLAG_SCHEDULES entry for who is
        active (its flag is set), else (False, None). The last match wins."""
        found, table = False, None
        for f, w, t in FLAG_SCHEDULES:
            if w == who and has_flag(f):
                found, table = True, t
        return found, table

    def routine_location(who, per, weekend=False):
        """WP1. Where someone's routine puts them in a period, ignoring story
        pins and the roster: a place key or "-". Flag schedules apply;
        Gojo's roaming does not (see char_location)."""
        found, table = flag_schedule(who)
        if found:
            return "-" if table is None else table.get(per, "-")
        loc = SCHEDULE.get(who, {}).get(per, "-")
        if weekend:
            loc = WEEKEND.get(who, {}).get(per, loc)
        return loc

    def char_location(who, per=None):
        """Where a character is during a given period, or None if off campus.
        (WP1: a FLAG_SCHEDULES entry replaces the routine, and Gojo keeps
        office hours on his in-days; story pins still win.)"""
        per = per or store.period
        found, table = flag_schedule(who)
        if found:
            loc = "-" if table is None else table.get(per, "-")
        elif who == "gojo":
            loc = store.gojo_today.get(per, "-")
            if store.gojo_in and per in GOJO_IN_PERIODS:
                loc = "gojo_office"
        else:
            table = SCHEDULE.get(who, {})
            loc = table.get(per, "-")
            if is_weekend():
                loc = WEEKEND.get(who, {}).get(per, loc)
        loc = store.schedule_overrides.get((who, store.day, per), loc)
        if loc == "-" or who not in store.roster:
            return None
        return loc

    def who_is_here(loc=None, per=None):
        """Everyone at a location — including whoever is currently tagging along."""
        loc = loc or store.here
        out = [c for c in ROSTER_ORDER
               if c in store.roster and char_location(c, per) == loc]
        if store.companion and loc == store.here and store.companion not in out:
            out.append(store.companion)
        return out

    def pin(who, loc, day=None, per=None):
        """Force a character somewhere — used by story events."""
        store.schedule_overrides[(who, day or store.day, per or store.period)] = loc

    ## Access ------------------------------------------------------------------

    def place_access(loc):
        """WP1. (allowed, reason, short): can_enter's answer plus a short tag
        for the map row ("Night", "Sealed", "SOON!")."""
        if store.explore_mode:
            return True, "", ""
        per = store.period
        if loc == "girls_dorm" and per in ("Evening", "Night"):
            if not has_flag("invited_girls_dorm"):
                return False, "I am not walking into the girls' dormitory after dark uninvited. That is how people get nailed to things.", "After dark"
        if loc == "office" and per == "Night":
            return False, "Yaga's office is dark and locked.", "Night"
        if loc == "storehouse" and not has_flag("storehouse_access"):
            return False, "The storehouse is sealed. I'd need Yaga to open it.", "Sealed"
        if loc == "utahime_office":
            if not has_flag("utahime_arrived"):
                return False, "The room next to Yaga's is locked. Someone has been carrying boxes in.", "Locked"
            if per == "Night":
                return False, "Her door is shut. There's light under it.", "Night"
        if loc == "gojo_office":
            if not has_flag("intensive_done"):
                return False, "Locked. A note on the door says SOON! and has a drawing of him on it.", "SOON!"
            if per == "Night":
                return False, "Gojo's office is locked. The television is on in there anyway.", "Night"
        return True, "", ""

    def can_enter(loc):
        """(allowed, reason) — some places are not always open to you."""
        ok, why, short = place_access(loc)
        return ok, why

    ## Areas and presence helpers (3.2, WP1) ----------------------------------------

    def area_of(loc):
        """WP1. The AREAS key that holds the place loc, or None."""
        for a in AREAS:
            if loc in a["places"]:
                return a["key"]
        return None

    def places_in(area):
        """WP1. The place keys in an area (a key or an AREAS entry), in map order."""
        a = area if isinstance(area, dict) else AREA_BY_KEY.get(area)
        return list(a["places"]) if a else []

    ## How each period reads in a phrase: "mornings", "noon", "evenings".
    PERIOD_WORDS = {"Morning": "mornings", "Noon": "noon", "Afternoon": "afternoons",
                    "Evening": "evenings", "Night": "nights"}

    def periods_phrase(pers):
        """WP1. A set of periods in words. Runs of three or more read "X to
        Y": "mornings to afternoons", "mornings to afternoons and nights";
        otherwise a list: "mornings, noon and evenings". All five: "all day"."""
        idx = sorted(set(PERIODS.index(p) for p in pers if p in PERIODS))
        if not idx:
            return ""
        if len(idx) == len(PERIODS):
            return "all day"
        runs = []
        for i in idx:
            if runs and i == runs[-1][-1] + 1:
                runs[-1].append(i)
            else:
                runs.append([i])
        words = []
        for r in runs:
            if len(r) >= 3:
                words.append("%s to %s" % (PERIOD_WORDS[PERIODS[r[0]]], PERIOD_WORDS[PERIODS[r[-1]]]))
            else:
                words.extend(PERIOD_WORDS[PERIODS[i]] for i in r)
        if len(words) == 1:
            return words[0]
        return ", ".join(words[:-1]) + " and " + words[-1]

    def usual_places(who):
        """WP1. Where someone can usually be found on a weekday, e.g.
        "Dojo (mornings and noon) · Training Hall (afternoons) · Riverside
        (evenings)". Places in first-seen order."""
        if who == "gojo" and not flag_schedule("gojo")[0]:
            return "Nowhere you can predict. His office on the days he's in."
        found, table = flag_schedule(who)
        if found and table is None:
            return "Away from campus."
        order, when = [], {}
        for p in PERIODS:
            loc = routine_location(who, p)
            if loc == "-" or loc not in LOCATIONS:
                continue
            if loc not in when:
                order.append(loc)
                when[loc] = []
            when[loc].append(p)
        return " · ".join("%s (%s)" % (LOCATIONS[l]["name"], periods_phrase(when[l])) for l in order)

    def when_at(who, loc):
        """WP1. When someone's routine has them at a place, e.g. "weekday
        mornings, noon and evenings" (Yaga, his office), "mornings to
        afternoons" (Ijichi, the gate), or "" when never."""
        if who == "gojo" and not flag_schedule("gojo")[0]:
            if loc == "gojo_office":
                return "on the days he's in, %s" % periods_phrase(GOJO_IN_PERIODS)
            return ""
        wk = [p for p in PERIODS if routine_location(who, p) == loc]
        we = [p for p in PERIODS if routine_location(who, p, weekend=True) == loc]
        if wk == we:
            return periods_phrase(wk)
        parts = []
        if wk:
            parts.append("weekday " + periods_phrase(wk))
        if we:
            parts.append("weekend " + periods_phrase(we))
        return "; ".join(parts)

    ## The ridge veil (D15) ----------------------------------------------------------

    def veil_ok():
        """WP1. The ridge's "Look up at the veil" action is offered: I have seen
        the veil on the tour, and haven't looked yet today."""
        return has_flag("saw_the_ridge_veil") and "veil" not in store.actions_today

    register_place_action("veil", "Look up at the veil", "Free. Once a day.",
                          locs=("ridge",), when="veil_ok")

    ## Migration 15 (3.12) --------------------------------------------------------

    def _migrate_15():
        """WP1, migration 15. A save whose Gojo roll is missing a period gets
        a fresh roll (which also sets gojo_in); a settled save standing in a
        place that no longer exists moves to the courtyard. Idempotent."""
        gt = getattr(store, "gojo_today", None)
        if not isinstance(gt, dict) or any(p not in gt for p in PERIODS):
            roll_gojo()
        if store.here not in LOCATIONS and has_flag("settled_in"):
            store.here = "courtyard"

    register_migration(15, _migrate_15, "Gojo's roll, a missing place")

    ## Validator (WP1) ---------------------------------------------------------------

    def _validate_world():
        out = []
        seen = {}
        for a in AREAS:
            for l in a["places"]:
                if l not in LOCATIONS:
                    out.append("area %s lists unknown place %r" % (a["key"], l))
                seen.setdefault(l, []).append(a["key"])
        for l in LOCATIONS:
            n = len(seen.get(l, []))
            if n != 1:
                out.append("place %r is in %d areas (must be exactly one)" % (l, n))
        if sorted(LOC_ORDER) != sorted(LOCATIONS):
            out.append("LOC_ORDER and LOCATIONS disagree")
        for name, tables in (("SCHEDULE", SCHEDULE), ("WEEKEND", WEEKEND)):
            for who, t in tables.items():
                for p, l in t.items():
                    if p not in PERIODS:
                        out.append("%s[%s] has unknown period %r" % (name, who, p))
                    if l != "-" and l not in LOCATIONS:
                        out.append("%s[%s][%s] is unknown place %r" % (name, who, p, l))
        for f, who, t in FLAG_SCHEDULES:
            for p, l in (t or {}).items():
                if l != "-" and l not in LOCATIONS:
                    out.append("FLAG_SCHEDULES %s/%s: unknown place %r" % (f, who, l))
        for l in GOJO_SPOTS:
            if l != "-" and l not in LOCATIONS:
                out.append("GOJO_SPOTS has unknown place %r" % l)
        for l, info in LOCATIONS.items():
            base = tuple(info["bg"].split())
            if not renpy.has_image(base, exact=True):
                out.append("place %r: no image %r" % (l, info["bg"]))
        for k in DISTRICT_ORDER:
            if k not in DISTRICTS:
                out.append("DISTRICT_ORDER lists unknown district %r" % k)
        for k, d in DISTRICTS.items():
            if not renpy.has_image(tuple(d["bg"].split()), exact=True):
                out.append("district %r: no image %r" % (k, d["bg"]))
            if not (2 <= len(d["lines"]) <= 3):
                out.append("district %r needs 2-3 arrival lines" % k)
        return out

    register_validator(_validate_world)


## The ridge veil (D15) ########################################################
##
## "Look up at the veil": free, once a day, on the ridge, after the tour has
## shown it (flag saw_the_ridge_veil). Three short passages, in order the
## first three times (flags looked_at_veil_1..3), then rotating by the day.

label sb_do_veil:
    $ actions_today.add("veil")
    $ _veil_n = next((n for n in (1, 2, 3) if not has_flag("looked_at_veil_%d" % n)), (day % 3) + 1)
    $ flag("looked_at_veil_%d" % _veil_n)
    scene bg ridge_veil
    with Dissolve(0.6)

    if _veil_n == 1:
        "I look up past the rope markers."
        "The veil sits on the top of the ridge like weather that has decided not to move: a dome, dark, faintly violet at its edges. The trees inside it stand a little too still."
        "If I let my eyes do the new thing they do, there is a shape in the middle of it. Sitting. Cross-legged, the way a monk sits."
        "I stop letting my eyes do the new thing."

    elif _veil_n == 2:
        "The veil again. In daylight it is almost nothing, a smudge on the ridge, like heat over a road in summer."
        "Nine people take turns holding it up, Gojo said. I wonder which one of them is holding it now, and whether they can feel me looking."
        "The figure hasn't moved. Its hands are still in its lap, and they are still missing their fingers."

    else:
        "I look up at the veil the way I've started to, the way I check a stove I already know is off."
        "Same dome. Same held quiet. Same dry brown shape in the middle of it, sitting with its hands in its lap."
        "Something is different, and it takes me a long moment to work out what."
        mcthink "It's facing the school."

    scene expression graded_bg()
    with Dissolve(0.6)
    return


## Clock state #################################################################

default day = 1
default period = "Morning"
default here = "dorm"
default gojo_today = {}
default schedule_overrides = {}
default talked_today = set()
default stamina = 100
default stamina_max = 100
default gojo_in = False          # WP1: Gojo keeps office hours today (D17)
