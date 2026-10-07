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
            indoor=True, name="Classroom", bg="bg classroom", x=600, y=735,
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
            indoor=True, name="My Room", bg="bg your_room", x=735, y=545,
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
            desc="Cold, clear, and deep enough to swim if I'm brave about it."),
        "ridge": dict(
            indoor=False, name="Mountain Ridge", bg="bg ridge", x=1290, y=215,
            desc="Above the treeline, as far as the rope markers. Higher up, the veil."),
        ## Phase 2 (D34): a new room in the School Building. x/y sit beside the
        ## classroom building on map_campus.png.
        "library": dict(
            indoor=True, name="Library", bg="bg library", x=250, y=640,
            desc="Shelves to the ceiling and a smell of dust and ink. Nobody talks above a murmur."),
        ## Phase 2 (D53, P9): every area has an outdoor place its rooms open
        ## onto, its hub (PATH_HUBS in room_paths.rpy; the heart's is the
        ## courtyard). Always open. x/y sit beside the area on map_campus.png.
        "school_yard": dict(
            indoor=False, name="School Courtyard", bg="bg school_yard", x=470, y=800,
            desc="Packed earth between the school buildings. Built for a few hundred students to cross at once; most days it's me and my own footsteps."),
        "dorm_yard": dict(
            indoor=False, name="Dormitory Garden", bg="bg dorm_yard", x=950, y=560,
            desc="A stone path between the dormitories, and a garden somebody else looks after. I cross it half asleep most mornings."),
        "staff_yard": dict(
            indoor=False, name="Staff Building Steps", bg="bg staff_yard", x=1560, y=640,
            desc="Wide stone steps below the principal's hall. I stand up straighter here without meaning to."),
        "training_yard": dict(
            indoor=False, name="Training Yard", bg="bg training_yard", x=1480, y=790,
            desc="Bare dirt and striking posts between the hall, the dojo and the storehouse. I usually hear this place before I see it."),
        "trailhead": dict(
            indoor=False, name="Mountain Path", bg="bg trailhead", x=960, y=330,
            desc="Where the stone path gives out and the mountain starts. I can go level into the forest, down to the river, or up the steps to the ridge."),
        ## The second UI overhaul (docs/UI2_DESIGN.md 4.1, D5; U0b): the Boys'
        ## Dormitory, the left house of the garden. My room is the door at
        ## the end of its corridor (WORLD_INSIDE, below); three friends'
        ## rooms open off it. Appended: a key that has reached a save is
        ## never removed. x/y are dead data (tools/genworld.py is not run).
        "boys_dorm": dict(
            indoor=True, name="Boys' Dormitory", bg="bg boys_dorm", x=735, y=600,
            desc="The first-year corridor, upstairs. A shoe rack at the head of the stairs, doors down both sides, and mine at the far end."),
        "yuji_room": dict(
            indoor=True, name="Yuji's Room", bg="bg yuji_room", x=700, y=600,
            desc="Film posters, a floor cushion and a small television. The window faces the garden."),
        "megumi_room": dict(
            indoor=True, name="Megumi's Room", bg="bg megumi_room", x=770, y=600,
            desc="Spare and tidy. A full bookshelf, and shoes in a line by the door."),
        "senpai_room": dict(
            indoor=True, name="Panda and Toge's Room", bg="bg senpai_room", x=735, y=640,
            desc="The big corner room. One very large futon, one neat one, and a shogi board between them."),
    }

    LOC_ORDER = ["gate", "courtyard", "classroom", "cafeteria", "training", "dojo",
                 "dorm_common", "dorm", "girls_dorm", "rooftop", "infirmary",
                 "office", "utahime_office", "gojo_office", "storehouse",
                 "forest", "riverside", "ridge", "library",
                 "school_yard", "dorm_yard", "staff_yard", "training_yard", "trailhead",
                 "boys_dorm", "yuji_room", "megumi_room", "senpai_room"]

    ## Areas (3.2, WP1) ----------------------------------------------------------
    ## The map's six cards, in order. anchor is the card centre on
    ## map_campus.png. Every LOCATIONS key belongs to exactly one area (the
    ## validator checks it).
    ##
    ## Phase 2 (6.1, 4.1): every row also has bg (the area's own picture, for
    ## the map's second level), blurb (one first-person line, the marker's
    ## hover) and spots ({loc: (x, y)}: where each room's pin sits on that
    ## picture, 1920x1080). spots are the code's defaults; a sidecar,
    ## game/layout/area_<key>.json, moves them without a script change
    ## (map_spots in ui_map.rpy reads both).
    ##
    ## Phase 2 (D53, D59, P9): each area's hub is the first of its places (the
    ## heart keeps its order; its hub is the courtyard). The Mountain's anchor
    ## sits on the peak drawn on map_campus.png (it sat over the lake).
    ##
    ## The second UI overhaul (D1, D3; U0b): a building with rooms inside is
    ## not a new area. The Boys' Dormitory and the rooms off its corridor are
    ## places of the Dormitories, appended. `spots` holds a pin for every
    ## place that has one: the rooms of WORLD_PINLESS (below) have none and
    ## are reached on foot. My room keeps its own pin.

    AREAS = [
        dict(key="heart",    name="Courtyard & Gate",  seal="門",
             places=["gate", "courtyard"],                              anchor=(960, 900),
             bg="bg area_heart",
             blurb="The stone path up from the torii, and the yard everything else hangs off.",
             spots={"courtyard": (960, 460), "gate": (960, 820)}),
        dict(key="school",   name="School Building",   seal="校",
             places=["school_yard", "classroom", "cafeteria", "infirmary", "library"], anchor=(420, 740),
             bg="bg area_school",
             blurb="Built for a few hundred students. There are four of us, and it echoes.",
             spots={"school_yard": (940, 560), "classroom": (520, 380), "cafeteria": (1300, 420),
                    "infirmary": (620, 760), "library": (1340, 780)}),
        dict(key="dorms",    name="Dormitories",       seal="寮",
             places=["dorm_yard", "dorm", "dorm_common", "girls_dorm", "rooftop",
                     "boys_dorm", "yuji_room", "megumi_room", "senpai_room"], anchor=(900, 560),
             bg="bg area_dorms",
             blurb="Where I sleep, and where everyone ends up by evening.",
             spots={"dorm_yard": (960, 520), "rooftop": (960, 260), "dorm": (480, 440),
                    "girls_dorm": (1440, 440), "dorm_common": (960, 640),
                    ## the near end of the left house on today's picture, clear
                    ## of my room's pin (4.8's points arrive with the new map)
                    "boys_dorm": (380, 790)}),
        dict(key="staff",    name="Staff Building",    seal="職",
             places=["staff_yard", "office", "utahime_office", "gojo_office"], anchor=(1560, 440),
             bg="bg area_staff",
             blurb="The principal's hall and the offices beside it. I knock first.",
             spots={"staff_yard": (950, 480), "office": (960, 340),
                    "utahime_office": (520, 660), "gojo_office": (1400, 660)}),
        dict(key="grounds",  name="Training Grounds",  seal="練",
             places=["training_yard", "training", "dojo", "storehouse"], anchor=(1560, 760),
             bg="bg area_grounds",
             blurb="The hall, the dojo and the storehouse. Most of my bruises come from here.",
             spots={"training_yard": (1180, 620), "training": (620, 420),
                    "dojo": (1320, 420), "storehouse": (960, 780)}),
        dict(key="mountain", name="The Mountain",      seal="山",
             places=["trailhead", "forest", "riverside", "ridge"],      anchor=(1290, 215),
             bg="bg area_mountain",
             blurb="Trees, cold water, and the ridge above them. It's further up than it looks.",
             spots={"trailhead": (520, 870), "ridge": (960, 280),
                    "forest": (480, 700), "riverside": (1380, 640)}),
    ]

    AREA_BY_KEY = {a["key"]: a for a in AREAS}

    ## An area's stand-in picture (4.1), until images/bg/area_<key>.png is
    ## painted: a 720x405 piece of map_campus.png around the area's anchor,
    ## kept inside the 1920x1080 picture, enlarged and darkened.
    WORLD_AREA_PIECE = (720, 405)

    def world_area_crop(key):
        """P1. (x, y, w, h): the piece of map_campus.png that stands in for
        an area's picture, around its anchor and clamped to the picture (the
        heart's anchor at y 900 would otherwise run off the bottom)."""
        ax, ay = AREA_BY_KEY[key]["anchor"]
        w, h = WORLD_AREA_PIECE
        x = max(0, min(1920 - w, int(ax - w // 2)))
        y = max(0, min(1080 - h, int(ay - h // 2)))
        return (x, y, w, h)

    def world_area_standin(key):
        """P1. The stand-in for an area's picture (world_area_crop, enlarged
        to 1920x1080 and darkened)."""
        return Transform("images/bg/map_campus.png", crop=world_area_crop(key),
                         xysize=(1920, 1080), matrixcolor=TintMatrix("#d0d0d0"))

    def world_area_bg(key):
        """P1. What `bg area_<key>` shows: images/bg/area_<key>.png when it
        exists, else the stand-in (bg_placeholders.rpy defines the six
        images from this)."""
        return bg_placeholder("images/bg/area_%s.png" % key, world_area_standin(key))

    ## A hub's stand-in picture (D58), until images/bg/<name>.png is painted:
    ## an existing outdoor picture, cropped, mirrored or tinted so that no
    ## two hubs look alike and none reads as the place it was borrowed from.
    ## name -> (picture, tint, saturation, brightness, crop or None, mirrored).
    WORLD_HUB_STANDINS = {
        ## the courtyard, mirrored, in warm morning light
        "school_yard":   ("courtyard.png", "#ffeed2", 0.92, 0.0, None, True),
        ## the courtyard's left half (the veranda, the pagoda), cooler and greener
        "dorm_yard":     ("courtyard.png", "#dcf0e6", 1.05, -0.02, (0, 240, 1280, 720), False),
        ## the hall at the far side of the courtyard, close up: its steps
        "staff_yard":    ("courtyard.png", "#e9e2f6", 0.80, -0.03, (420, 330, 1080, 608), False),
        ## the courtyard's right half, mirrored, dusty and bleached
        "training_yard": ("courtyard.png", "#ffe6c6", 0.70, 0.03, (640, 240, 1280, 720), True),
        ## the forest trail, mirrored, deeper green
        "trailhead":     ("forest.png", "#dcf4d4", 0.90, -0.04, None, True),
    }

    def world_hub_standin(name):
        """P9. The stand-in for a hub's picture (WORLD_HUB_STANDINS), 1920x1080."""
        src, tint, sat, bright, crop, mirror = WORLD_HUB_STANDINS[name]
        kw = dict(matrixcolor=TintMatrix(tint) * SaturationMatrix(sat) * BrightnessMatrix(bright))
        if crop:
            kw.update(crop=crop, xysize=(1920, 1080))
        if mirror:
            kw.update(xzoom=-1.0)
        return Transform("images/bg/" + src, **kw)

    def world_hub_bg(name):
        """P9. What `bg <hub>` shows: images/bg/<name>.png when it exists,
        else the stand-in (bg_placeholders.rpy defines the five images from
        this)."""
        return bg_placeholder("images/bg/%s.png" % name, world_hub_standin(name))

    ## Schedules ---------------------------------------------------------------
    ## Weekday routine. "-" means the character is off campus this period.
    ##
    ## Phase 2 (D57, P9): a few slots stand in the hubs, so the yards are not
    ## empty. Each was picked where the move takes nothing away that only
    ## that slot offered (no written scene asks for the person at the old
    ## place; ev() rows with a person have no place): Yuji outside the
    ## dormitories at night, Nobara in the training yard in the
    ## morning, Toge in the school courtyard in the afternoon; at weekends
    ## Megumi at the foot of the mountain in the morning and Shoko on the
    ## staff building's steps in the afternoon.
    ##
    ## After checkpoint D (5 Oct 2026, the owner's word): in the Evening the
    ## common room holds the first years only. Panda and Toge are in the
    ## library instead, on all seven days (WEEKEND has no Evening cell for
    ## either, so it falls back to these two). The library because it is a
    ## study room, as the common room is: "Study together" is still offered
    ## with both, and nobody else is there in the Evening.
    ##
    ## After that (the owner's word, the same day: "Put Panda in the garden
    ## for now"): Panda's Night is the dormitory garden, beside Yuji, on all
    ## seven days (WEEKEND has no Night cell for anyone). The common room is
    ## then empty at Night by routine. "For now": until there are
    ## dormitories for him to sleep in (asked for after phase 2).

    ##
    ## The second UI overhaul (docs/UI2_DESIGN.md 4.3, O18; U0b): at Night
    ## everyone who lives on campus is in their own room, on all seven days
    ## (WEEKEND still has no Night cell for anyone, and _validate_world now
    ## says so). U0b moves the four boys: Yuji and Megumi to their rooms,
    ## Panda and Toge to the room they share; the garden is then empty at
    ## Night, as the common room is. Who is asleep there is WORLD_ASLEEP,
    ## below. At weekends each of the four has one daytime hour at home
    ## (Yuji at Noon; Megumi, Panda and Toge in the Morning), and Yuji's
    ## weekend Evening is the garden, by the pond.

    SCHEDULE = {
        "yuji":   {"Morning": "training",  "Noon": "cafeteria", "Afternoon": "courtyard",
                   "Evening": "dorm_common", "Night": "yuji_room"},
        "megumi": {"Morning": "classroom", "Noon": "cafeteria", "Afternoon": "forest",
                   "Evening": "dorm_common", "Night": "megumi_room"},
        "nobara": {"Morning": "training_yard", "Noon": "cafeteria", "Afternoon": "courtyard",
                   "Evening": "dorm_common", "Night": "girls_dorm"},
        "maki":   {"Morning": "dojo",      "Noon": "dojo",      "Afternoon": "training",
                   "Evening": "riverside", "Night": "girls_dorm"},
        "panda":  {"Morning": "courtyard", "Noon": "cafeteria", "Afternoon": "training",
                   "Evening": "library",   "Night": "senpai_room"},
        "toge":   {"Morning": "ridge",     "Noon": "cafeteria", "Afternoon": "school_yard",
                   "Evening": "library",   "Night": "senpai_room"},
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
        "yuji":   {"Morning": "dorm_common", "Noon": "yuji_room", "Afternoon": "riverside", "Evening": "dorm_yard"},
        ## Phase 2 (D34): Megumi reads in the Library on weekend afternoons.
        "megumi": {"Morning": "megumi_room", "Afternoon": "library"},
        "nobara": {"Morning": "girls_dorm",  "Afternoon": "riverside", "Evening": "courtyard"},
        "maki":   {"Morning": "dojo",        "Afternoon": "riverside", "Evening": "dojo"},
        "panda":  {"Morning": "senpai_room", "Afternoon": "riverside"},
        "toge":   {"Morning": "senpai_room", "Afternoon": "riverside"},
        "shoko":  {"Afternoon": "staff_yard"},
        "yaga":   {"Morning": "-", "Noon": "-", "Afternoon": "-", "Evening": "-"},
        "utahime": {"Afternoon": "-", "Evening": "courtyard"},
    }

    ## Schedules by flag (D13). Entries are (flag, who, table_or_None): while
    ## the flag is set, the table ({period: place or "-"}) replaces that
    ## character's whole routine, weekends included, and None means off
    ## campus. The last matching entry wins; story pins (schedule_overrides)
    ## still win over it. Phase 4 adds Utahime leaving to lead Kyoto and
    ## Yuji's absence here; phase 1 ships it empty.
    FLAG_SCHEDULES = []

    ## Houses, homes, doors and the Night (the second UI overhaul) -------------
    ## docs/UI2_DESIGN.md 3.2, 4.2, 4.3; D1, D10, D48, D49. Init data, never
    ## saved. U0b lays these with the Boys' Dormitory; U0c1 adds the rows of
    ## the other houses and people.

    ## room -> the place it opens off (its house), one level deep. A room
    ## inside a house has its house as its first exit and no exit to the
    ## yard (path_validate in room_paths.rpy holds the rule).
    WORLD_INSIDE = {
        "dorm":        "boys_dorm",
        "yuji_room":   "boys_dorm",
        "megumi_room": "boys_dorm",
        "senpai_room": "boys_dorm",
    }

    ## Places with no pin on their area's map: reached on foot, or by the
    ## journal's "Go there". My room is not one of them (D3).
    WORLD_PINLESS = ("yuji_room", "megumi_room", "senpai_room")

    ## who -> the place they live in. Gojo has no row.
    WORLD_HOMES = {
        "yuji":   "yuji_room",
        "megumi": "megumi_room",
        "panda":  "senpai_room",
        "toge":   "senpai_room",
        "shoko":  "infirmary",
    }

    ## A door that asks a Bond level (4.2): the place -> whose Bond it asks
    ## (any one of them opens it).
    WORLD_DOOR_OWNERS = {
        "yuji_room":   ("yuji",),
        "megumi_room": ("megumi",),
        "senpai_room": ("panda", "toge"),
    }

    ## The level a door asks. None is the one entry every door reads today;
    ## a row for a place ({"maki_room": 25}) sets that door apart.
    WORLD_DOOR_BOND = {None: 15}

    ## Who is asleep at Night, by the kind of day. world_asleep() is the
    ## only reader.
    WORLD_ASLEEP = {
        "weekday": ("megumi", "panda"),
        "weekend": ("yuji", "toge"),
    }

    def world_inside(loc):
        """U0b (sb_world.rpy). The key of the house a place opens off
        (WORLD_INSIDE), or None for a place that opens onto its yard."""
        return WORLD_INSIDE.get(loc)

    def world_pinned(loc):
        """U0b. bool: the place has a pin on its area's map."""
        return loc in LOCATIONS and loc not in WORLD_PINLESS

    def world_home(who):
        """U0b. The place key someone lives in (WORLD_HOMES), or None."""
        return WORLD_HOMES.get(who)

    def world_door_owners(loc):
        """U0b. A list of person keys: whose Bond the door of this place
        asks; [] for a place with no Bond door. place_access applies its
        Bond clause (any hour, "Bond 15") only to a place that also has a
        house (world_inside): a row for a corridor, such as
        "girls_dorm": ("nobara", "maki"), names its owners and locks
        nothing by itself; the rule for that door is written in
        place_access beside the corridor's own test."""
        return list(WORLD_DOOR_OWNERS.get(loc, ()))

    def world_door_bond(loc):
        """U0b. The Bond level the door of this place asks, an int
        (WORLD_DOOR_BOND: the place's own row, else the one under None), or
        None for a place with no Bond door."""
        if loc not in WORLD_DOOR_OWNERS:
            return None
        return int(WORLD_DOOR_BOND.get(loc, WORLD_DOOR_BOND[None]))

    def world_asleep(who, per=None):
        """U0b (D48). bool: this person is asleep. True only at Night, for
        someone on today's list of WORLD_ASLEEP who is in their home
        (WORLD_HOMES) by their routine. Never for whoever is walking with
        me, and never for someone a story pin or a flag schedule has placed.
        A sleeper is still counted where they are (who_is_here); they are
        not on the stage (stage_people) and nothing is offered with them."""
        per = per or store.period
        if per != "Night" or not who or who == store.companion:
            return False
        home = WORLD_HOMES.get(who)
        if home is None:
            return False
        if who not in WORLD_ASLEEP["weekend" if is_weekend() else "weekday"]:
            return False
        if flag_schedule(who)[0] or (who, store.day, per) in store.schedule_overrides:
            return False
        return char_location(who, per) == home

    def world_home_state(who, per=None):
        """U0b (D49, a hook for later quests). "awake", "asleep" or "out":
        this person against their home. "out" also for someone who has no
        home, and for whoever walks with me unless we stand in their home."""
        per = per or store.period
        home = WORLD_HOMES.get(who)
        if home is None:
            return "out"
        if who == store.companion:
            return "awake" if store.here == home else "out"
        if char_location(who, per) != home:
            return "out"
        return "asleep" if world_asleep(who, per) else "awake"

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

    def advance_period_soft(n=1, loc=None):
        """P0 (sb_world.rpy), final (PHASE2_DESIGN.md D26). Move the clock
        forward up to n periods, one at a time. Returns True if the day
        rolled over, as advance_period does.

        It stops early, with steps left, when a story beat is waiting at
        `loc` (default: where I stand; the Tokyo trip passes "gate", where it
        is about to put me), and when it arrives at Night. The time it didn't
        charge is forgiven, silently. Called at Night it rolls the day
        exactly as advance_period does. The waiting-beat test is
        has_event("story", loc=...), as board_beat_waiting's, never
        pick_event (which draws from renpy.random). Explore mode has no
        story: there it is advance_period(n)."""
        if store.explore_mode:
            return advance_period(n)
        rolled = False
        for i in range(n):
            idx = period_index()
            if idx >= len(PERIODS) - 1:
                rolled = True
                new_day()
            else:
                store.period = PERIODS[idx + 1]
            if i + 1 >= n:
                break
            if period_index() >= len(PERIODS) - 1:
                break       ## Night, with steps left: a long activity can't carry me past bedtime
            if has_event("story", loc=(loc or store.here)):
                break       ## stop the clock where a story beat is waiting
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

    def person_now(who):
        """P1 (sb_world.rpy). Where someone is right now, for the journal's
        "Right now" line and its "Go there" button (D6): dict(place=key or
        None, name=str, doing=str, reachable=bool, hidden=bool,
        with_me=bool). Never None.

          tagging along     place=here, name "With me", with_me=True
          in an open room   place=its key, name the room's, doing the
                            caption ambient_of gives; reachable unless it is
                            the room I'm standing in
          in a room I can't enter (place_access refuses)
                            hidden=True, name "Somewhere I can't go right
                            now"; place is None, so no caller can walk
                            there or say where it is
          anything else     (off campus, not met) name is "Off campus"."""
        out = dict(place=None, name="Off campus", doing="", reachable=False, hidden=False, with_me=False)
        if store.companion and who == store.companion and store.here in LOCATIONS:
            out.update(place=store.here, name="With me", doing="tagging along", with_me=True)
            return out
        loc = char_location(who)
        if loc is None or loc not in LOCATIONS:
            return out
        if not place_access(loc)[0]:
            out.update(name="Somewhere I can't go right now", hidden=True)
            return out
        doing = ambient_of(who, loc)[0] or ""
        out.update(place=loc, name=LOCATIONS[loc]["name"], doing=str(doing),
                   reachable=bool(loc != store.here))
        return out

    ## Access ------------------------------------------------------------------

    def place_access(loc):
        """WP1. (allowed, reason, short): can_enter's answer plus a short tag
        for the map row ("Night", "Sealed", "SOON!"). The second overhaul
        (U0b): the flag door_<place> opens any place; a friend's room asks
        world_door_bond of one of world_door_owners ("Bond 15")."""
        if store.explore_mode:
            return True, "", ""
        ## A story quest can open any door, whatever its Bond, the hour or
        ## its other locks (D49; no quest sets one in the second overhaul).
        if has_flag("door_" + str(loc)):
            return True, "", ""
        per = store.period
        ## A friend's room asks a Bond level of one of its owners, and is
        ## then open at any hour, whether they are in, out or asleep (4.2,
        ## D10). An owner walking with me opens it too. It reads Bond, flags
        ## and the companion only, never char_location.
        ## The clause is for a room inside a house only (world_inside): a
        ## corridor that gets owners later (the plan's 3.2 gives girls_dorm
        ## Nobara and Maki) is not closed by it and writes its own rule below.
        need = world_door_bond(loc)
        if need is not None and world_inside(loc):
            owners = world_door_owners(loc)
            if not (store.companion in owners
                    or any(store.bonds.get(w, 0) >= need for w in owners)):
                names = " or ".join(CAST[w]["short"] for w in owners)
                return False, "I don't know %s well enough to let myself in." % names, "Bond %d" % need
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
            if not has_flag("intensive_done"):
                return "Nowhere I can predict."
            return "Nowhere I can predict. His office on the days he's in."
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

    def veil_bg(per=None):
        """WP1. The veil picture (bg ridge_veil) lit for the period, the way
        graded_bg() lights the ridge outside, so a look at Night stays night.
        Marked with _light_key ("ridge", per) so sprites are lit to match."""
        per = per or store.period
        key = ("ridge_veil", per)
        if key in _BG_CACHE:
            return _BG_CACHE[key]
        tint, bright = OUTDOOR_GRADE.get(per, ("#ffffff", 0.0))
        if tint == "#ffffff" and abs(bright) < 0.001:
            d = "bg ridge_veil"
        else:
            d = Transform("bg ridge_veil", matrixcolor=TintMatrix(tint) * BrightnessMatrix(bright))
            d._light_key = ("ridge", per)
        _BG_CACHE[key] = d
        return d

    ## Migration 15 (3.12) --------------------------------------------------------

    def _migrate_15():
        """WP1, migration 15. A save whose Gojo roll is missing a period gets
        a fresh roll (which also sets gojo_in); a settled save standing in a
        place that no longer exists moves to the courtyard; a settled save
        without saw_the_ridge_veil gets it. Idempotent."""
        gt = getattr(store, "gojo_today", None)
        if not isinstance(gt, dict) or any(p not in gt for p in PERIODS):
            roll_gojo()
        if store.here not in LOCATIONS and has_flag("settled_in"):
            store.here = "courtyard"
        ## A settled save gets the flag, so the ridge offers "Look up at the
        ## veil". ch2_tour sets it today; a save toured before the veil (it saw
        ## the casket) gets it too, and passage 1's "where Gojo showed me" is
        ## slightly off for it. Explore mode never took the tour and never
        ## offers the veil, so it is left alone.
        if (has_flag("settled_in") and not store.explore_mode
                and not has_flag("saw_the_ridge_veil")):
            flag("saw_the_ridge_veil")

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
        for a in AREAS:
            if not renpy.has_image(tuple(a["bg"].split()), exact=True):
                out.append("area %r: no image %r" % (a["key"], a["bg"]))
            if not a["blurb"]:
                out.append("area %r has no blurb" % a["key"])
            if sorted(a["spots"]) != sorted(l for l in a["places"] if l not in WORLD_PINLESS):
                out.append("area %r: spots and its pinned places disagree" % a["key"])
        ## The second overhaul (3.2): the houses, homes, doors and the Night.
        for room, house in sorted(WORLD_INSIDE.items()):
            if room not in LOCATIONS or house not in LOCATIONS:
                out.append("WORLD_INSIDE: %r -> %r names an unknown place" % (room, house))
            elif house in WORLD_INSIDE or room == house:
                out.append("WORLD_INSIDE: %r -> %r must be one level deep" % (room, house))
            elif area_of(room) != area_of(house):
                out.append("WORLD_INSIDE: %r and its house %r are in different areas" % (room, house))
        for l in WORLD_PINLESS:
            if l not in LOCATIONS:
                out.append("WORLD_PINLESS has unknown place %r" % l)
            elif l not in WORLD_INSIDE:
                out.append("WORLD_PINLESS: %r opens off no house (a place without a pin is a room inside one)" % l)
        for who, l in sorted(WORLD_HOMES.items()):
            if who not in CAST:
                out.append("WORLD_HOMES has unknown person %r" % who)
            if l not in LOCATIONS:
                out.append("WORLD_HOMES[%s] is unknown place %r" % (who, l))
            elif SCHEDULE.get(who, {}).get("Night") != l:
                out.append("WORLD_HOMES[%s] is %r but SCHEDULE's Night cell is %r" % (who, l, SCHEDULE.get(who, {}).get("Night")))
        for who, t in sorted(WEEKEND.items()):
            if "Night" in t:
                out.append("WEEKEND[%s] has a Night cell (the Night is the same on all seven days)" % who)
        if sorted(WORLD_ASLEEP) != ["weekday", "weekend"]:
            out.append("WORLD_ASLEEP needs exactly the lists \"weekday\" and \"weekend\"")
        for kind, names in sorted(WORLD_ASLEEP.items()):
            for who in names:
                if who not in WORLD_HOMES:
                    out.append("WORLD_ASLEEP[%s]: %r has no WORLD_HOMES row" % (kind, who))
        for l in sorted(WORLD_DOOR_BOND, key=str):
            if l is not None and l not in LOCATIONS:
                out.append("WORLD_DOOR_BOND has unknown place %r" % l)
            if not isinstance(WORLD_DOOR_BOND[l], int) or isinstance(WORLD_DOOR_BOND[l], bool):
                out.append("WORLD_DOOR_BOND[%r] must be a whole number" % l)
        if None not in WORLD_DOOR_BOND:
            out.append("WORLD_DOOR_BOND needs the entry under None (the level every door reads)")
        for l, owners in sorted(WORLD_DOOR_OWNERS.items()):
            if l not in LOCATIONS:
                out.append("WORLD_DOOR_OWNERS has unknown place %r" % l)
            if not owners or any(w not in CAST for w in owners):
                out.append("WORLD_DOOR_OWNERS[%s] must name at least one person of CAST" % l)
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
## The lines follow the tour: only the "dead" choice (asked_dead) heard Gojo
## say who holds the veil, and the "say nothing" choice (watched_the_box)
## already saw which way the body faces, so the discovery in passage 3 plays
## once, for the others, and the rest of the time it is something I know.

label sb_do_veil:
    ## PLACEHOLDER — rewrite in phase 4
    $ actions_today.add("veil")
    $ _veil_n = next((n for n in (1, 2, 3) if not has_flag("looked_at_veil_%d" % n)), (day % 3) + 1)
    $ _veil_new = not has_flag("looked_at_veil_%d" % _veil_n)
    $ flag("looked_at_veil_%d" % _veil_n)
    scene expression veil_bg()
    with Dissolve(0.6)

    if _veil_n == 1:
        "I look up past the rope markers."
        "The veil sits on the top of the ridge like weather that has decided not to move: a dome, dark, faintly violet at its edges. The grass inside it doesn't move when the grass outside does."
        "If I let my eyes do the new thing they do, it's still there in the middle of it. Sitting cross-legged, the way a monk sits, exactly where Gojo showed me."
        "I stop letting my eyes do the new thing."

    elif _veil_n == 2:
        if period == "Night":
            "The veil again. After dark it is almost nothing, a patch of the ridge where the stars don't quite reach."
        else:
            "The veil again. Today the light is flat and it is almost nothing, a smudge on the ridge, like heat over a road in summer."
        if has_flag("asked_dead"):
            "Nine people take turns holding it up, Gojo said. I wonder which one of them is holding it now, and whether they can feel me looking."
        else:
            "Somebody at this school is holding it up right now. I wonder who, and whether they can feel me looking."
        "The figure hasn't moved. Its hands are still in its lap, and they are still missing their fingers."

    elif _veil_new and not has_flag("watched_the_box"):
        "I look up at the veil the way I've started to, the way I check a stove I already know is off."
        "Same dome. Same held quiet. Same dry brown shape in the middle of it, sitting with its hands in its lap."
        "Something is different, and it takes me a long moment to work out what."
        mcthink "It's facing the school."

    else:
        "I look up at the veil the way I've started to, the way I check a stove I already know is off."
        "Same dome. Same held quiet. Same dry brown shape in the middle of it, hands in its lap."
        "I keep telling myself it faces the valley. Out, away, at nothing in particular."
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
