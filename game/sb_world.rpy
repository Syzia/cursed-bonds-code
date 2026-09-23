################################################################################
## Cursed Bonds — the world: clock, campus map, character schedules.
################################################################################

init -2 python:

    PERIODS = ["Morning", "Noon", "Afternoon", "Evening", "Night"]
    PERIOD_ICON = {"Morning": "☀", "Noon": "☀", "Afternoon": "☁",
                   "Evening": "☾", "Night": "☾"}
    WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    ## Campus ------------------------------------------------------------------
    ## x/y MUST stay in sync with NODES in tools/genworld.py.

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
            desc="A corridor of doors. You do not go in uninvited."),
        "rooftop": dict(
            indoor=False, name="Rooftop", bg="bg rooftop", x=960, y=455,
            desc="A hundred kilometres of view and nobody to interrupt."),
        "infirmary": dict(
            indoor=True, name="Infirmary", bg="bg infirmary", x=350, y=610,
            desc="Shoko Ieiri's domain. Smells of antiseptic and, faintly, cigarettes."),
        "office": dict(
            indoor=True, name="Principal's Office", bg="bg office", x=1560, y=560,
            desc="Where missions are handed out and excuses are not accepted."),
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
            desc="Above the treeline. The only place nobody watches you fail."),
    }

    LOC_ORDER = ["gate", "courtyard", "classroom", "cafeteria", "training", "dojo",
                 "dorm_common", "dorm", "girls_dorm", "rooftop", "infirmary",
                 "office", "storehouse", "forest", "riverside", "ridge"]

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
    }

    ## Gojo is never where you expect him.
    GOJO_SPOTS = ["-", "-", "-", "rooftop", "courtyard", "office", "cafeteria", "training"]

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
        _BG_CACHE[key] = d
        return d

    ## Arc 1 runs on a deadline: the Kyoto exchange.
    KYOTO_DAY = 22

    def days_left():
        return max(0, KYOTO_DAY - store.day)

    ## Clock -------------------------------------------------------------------

    def period_index():
        return PERIODS.index(store.period)

    def weekday():
        return WEEKDAYS[(store.day - 1) % 7]

    def is_weekend():
        return weekday() in ("Sat", "Sun")

    def date_line():
        return "Day %d · %s · %s" % (store.day, weekday(), store.period)

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
        day that rolls over because you waited through Night behaves the same."""
        store.day += 1
        store.period = PERIODS[0]
        store.talked_today = set()
        store.spent_today = set()
        store.companion = None
        store.stamina = store.stamina_max
        store.ce = store.ce_max
        roll_gojo()

    def roll_gojo():
        import random as _r
        rnd = _r.Random(store.day * 977 + 13)
        store.gojo_today = {p: rnd.choice(GOJO_SPOTS) for p in PERIODS}

    ## Presence ----------------------------------------------------------------

    def char_location(who, per=None):
        """Where a character is during a given period, or None if off campus."""
        per = per or store.period
        if who == "gojo":
            loc = store.gojo_today.get(per, "-")
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

    def can_enter(loc):
        """(allowed, reason) — some places are not always open to you."""
        if store.explore_mode:
            return True, ""
        if loc == "girls_dorm" and store.period in ("Evening", "Night"):
            if not has_flag("invited_girls_dorm"):
                return False, "You are not walking into the girls' dormitory after dark uninvited. That is how people get nailed to things."
        if loc == "office" and store.period == "Night":
            return False, "Yaga's office is dark and locked."
        if loc == "storehouse" and not has_flag("storehouse_access"):
            return False, "The storehouse is sealed. You'd need Yaga to open it."
        return True, ""


## Clock state #################################################################

default day = 1
default period = "Morning"
default here = "dorm"
default gojo_today = {}
default schedule_overrides = {}
default talked_today = set()
default stamina = 100
default stamina_max = 100
