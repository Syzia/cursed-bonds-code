## tools/smoke/u2_lit.rpy -- rooms lit at Night, and the two late stays
## (docs/UI2_DESIGN.md 5.7a, D61; the owner's ruling of 11 Oct, O42, O47;
## package U0n, the last of wave 0).
##
##   SMOKE_TIMEOUT=600 tools/smoke.sh u2_lit
##
## Every sentence of 5.7a's "Acceptance" that speaks of the game is a line
## here. It does not need the pointer and may run beside other harnesses.
##
## Its overlay, tools/smoke/assets/u2_lit/game/images/bg/library_lit.png, is a
## plain TEST picture of the Library lit at Night (a flat card that says so):
## no picture of the owner's is in it, and it is never installed. The overlay
## holds no manifest: the rows a check needs are laid in place over an EMPTY
## manifest (zzl_blank), and every table is put back after each section.
##
## The lines are rules, so they stay true when an art sitting installs real
## pictures (where no harness may be edited) and when wave 1 builds on this:
##   - the test picture is registered by this file's own init block whenever
##     the game's own registration did not take it (a tree whose manifest has
##     the Library's day picture at a later revision and no row for the test
##     file), and section B says which of the two happened;
##   - the gates are read over an empty manifest with the Library's Night
##     cell set by the test (zzl_night), whatever hour pictures the tree has;
##   - whether a file "exists" is answered by the test for the few paths it
##     names (ZZL_FILES: a foreground cut, a pose), through renpy.loadable,
##     so no test cut or pose is laid in the overlay;
##   - who is where is compared with the table emptied, never with a copy of
##     today's schedule.
##
## Sections:
##   A  the names: `lit` as an hour's attribute (ART_HOURS, art_parent,
##      art_fresh, the manifest row) and every gate that builds a file name
##      or a key from the attribute (the foreground cut, the pose, the light
##      row, a view_ file's hour tables)
##   B  WORLD_LIT and its registration; WORLD_VARIANTS untouched; with no lit
##      picture registered nothing differs, whoever is where
##   C  the reader: bg_variant and bg_name at Night with the test picture
##      (lit, dark, the companion rule, asleep, stale, no cut, Evening), the
##      two cache rows and _light_key, a replay, no hour in the store
##   D  world_lit_bg, the helper for written scenes
##   E  the late stays: WORLD_LATE in char_location, awake and "out", a story
##      pin and a flag schedule win, what is offered, the stayer's own room,
##      the journal's line, and the tuple of places shut at Night
##   F  lint: each refusal of 5.7a, made to fire
##   G  two screenshots of the Library at Night, lit and dark

init 999 python:
    import builtins
    import copy
    import inspect

    ZZL_PATH = "images/bg/library_lit.png"
    ## What the game's own registration did at init, before this file adds
    ## the test picture where it was not taken.
    ZZL_INIT = builtins.dict(on=builtins.dict(WORLD_LIT_ON),
                             loadable=bool(renpy.loadable(ZZL_PATH)),
                             fresh=bool(art_fresh("library_lit", "library")))
    if ZZL_INIT["loadable"] and "library" not in WORLD_LIT_ON:
        if not renpy.has_image(("bg", "library", "lit"), exact=True):
            renpy.image("bg library lit", ZZL_PATH)
        WORLD_LIT_ON["library"] = ZZL_PATH

    class ZZLState(builtins.object):
        """What the tests change in place, so it can be put back. A builtins
        object: never saved, and rollback leaves it alone."""
        def __init__(self):
            self.held = None
            self.blank = False
            self.wrapped = False

    zzl = ZZLState()
    ZZL_FILES = builtins.dict()          ## path -> bool: what renpy.loadable answers for it
    ZZL_REAL = builtins.dict(loadable=renpy.loadable)

    def zzl_loadable(name, *args, **kwargs):
        if name in ZZL_FILES:
            return ZZL_FILES[name]
        return ZZL_REAL["loadable"](name, *args, **kwargs)

    def zzl_set_files(table):
        ZZL_FILES.clear()
        ZZL_FILES.update(table)
        renpy.loadable = zzl_loadable if ZZL_FILES else ZZL_REAL["loadable"]
        _BG_CACHE.clear()

    def zzl_hold():
        zzl.held = builtins.dict(
            art=copy.deepcopy(builtins.dict(art_rows())),
            layout=copy.deepcopy(builtins.dict(RULE_LAYOUT)),
            variant=copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items())),
            lit=builtins.dict(WORLD_LIT_ON),
            late=builtins.dict(WORLD_LATE),
            up=store.world_night_up)

    def zzl_back():
        """Every table as it was (the manifest empty while zzl_blank is on),
        every file what it is, and every picture graded_bg has built
        forgotten."""
        h = zzl.held
        ART_PICTURES.clear()
        if not zzl.blank:
            ART_PICTURES.update(copy.deepcopy(h["art"]))
        RULE_LAYOUT.clear()
        RULE_LAYOUT.update(copy.deepcopy(h["layout"]))
        TIME_VARIANT.clear()
        TIME_VARIANT.update(copy.deepcopy(h["variant"]))
        WORLD_LIT_ON.clear()
        WORLD_LIT_ON.update(h["lit"])
        WORLD_LATE.clear()
        WORLD_LATE.update(h["late"])
        store.world_night_up = h["up"]
        store._in_replay = None
        zzl_set_files({})

    def zzl_blank(on):
        zzl.blank = bool(on)
        zzl_back()

    def zzl_art(**rows):
        for k, r in rows.items():
            if r is None:
                ART_PICTURES.pop(k, None)
            else:
                ART_PICTURES[k] = builtins.dict(r)
        _BG_CACHE.clear()

    def zzl_night(attr):
        """The Library's Night cell, set for the test: "night" (a painted
        dark night, by name only) or None (the day picture, tinted)."""
        cells = builtins.dict(TIME_VARIANT.get("library", {}))
        cells.pop("Night", None)
        if attr:
            cells["Night"] = attr
        TIME_VARIANT["library"] = cells
        _BG_CACHE.clear()

    def zzl_day(wd):
        """The day of the second week that is this weekday (8 is a Monday)."""
        return 8 + WEEKDAYS.index(wd)

    def zzl_at(wd, per="Night", here="courtyard", companion=None):
        store.day = wd if isinstance(wd, int) else zzl_day(wd)
        store.period = per
        store.here = here
        store.companion = companion
        store.schedule_overrides = {}
        roll_gojo()
        mission_cache_clear()

    def zzl_no_lit(fn):
        """fn() with no lit picture registered: what the game answers
        without this package's pictures."""
        was = builtins.dict(WORLD_LIT_ON)
        WORLD_LIT_ON.clear()
        _BG_CACHE.clear()
        try:
            return fn()
        finally:
            WORLD_LIT_ON.update(was)
            _BG_CACHE.clear()

    def zzl_no_late(fn):
        was = builtins.dict(WORLD_LATE)
        WORLD_LATE.clear()
        try:
            return fn()
        finally:
            WORLD_LATE.update(was)

    def zzl_up_is(value, fn):
        """fn() with world_night_up answering `value` for every place."""
        was = store.world_night_up
        store.world_night_up = lambda loc, per=None: value
        _BG_CACHE.clear()
        try:
            return fn()
        finally:
            store.world_night_up = was
            _BG_CACHE.clear()

    def zzl_pictures():
        """bg_variant and bg_name for every place at every hour on each of
        the seven days of a week."""
        was = (store.day, store.period)
        out = []
        try:
            for d in range(8, 15):
                store.day = d
                roll_gojo()
                for per in PERIODS:
                    store.period = per
                    for loc in LOC_ORDER:
                        out.append((d, per, loc, bg_variant(loc, per), bg_name(loc, per)))
        finally:
            store.day, store.period = was
            roll_gojo()
        return out

    def zzl_where():
        """{(day, hour, who): place} for everyone on the roster, days 1 to 14."""
        was = (store.day, store.period)
        out = builtins.dict()
        try:
            for d in range(1, 15):
                store.day = d
                roll_gojo()
                for per in PERIODS:
                    for who in ROSTER_ORDER:
                        out[(d, per, who)] = char_location(who, per)
        finally:
            store.day, store.period = was
            roll_gojo()
        return out

    def zzl_late_cells():
        """The cells WORLD_LATE names on days 1 to 14: {(day, "Night", who): place}."""
        out = builtins.dict()
        for who, row in WORLD_LATE.items():
            for d in range(1, 15):
                if WEEKDAYS[(d - 1) % 7] in row[1]:
                    out[(d, "Night", who)] = row[0]
        return out

    def zzl_offered(who, loc):
        return builtins.sorted(a["id"] for a, ok, why in activities_for(who, loc) if ok)

    def zzl_owner(fn):
        return callable(fn) and fn.__code__.co_filename.replace("\\", "/").endswith("game/sb_world.rpy")

    ZZL_CALLS = builtins.list()

    def zzl_count_here(fn):
        """fn() with every call of who_is_here noted in ZZL_CALLS."""
        real = store.who_is_here

        def zzl_counting(*a, **k):
            ZZL_CALLS.append(a)
            return real(*a, **k)

        del ZZL_CALLS[:]
        store.who_is_here = zzl_counting
        try:
            return fn()
        finally:
            store.who_is_here = real

    def zzl_usual():
        """The routine's own words for everyone: what the journal's "usually" line is made of."""
        return [(w, usual_places(w), [routine_location(w, p, we) for p in PERIODS for we in (False, True)],
                 when_at(w, "library"), when_at(w, WORLD_HOMES.get(w))) for w in ROSTER_ORDER]

    def zzl_dark(loc="library"):
        """What bg_variant answers for the place tonight with no lit picture."""
        return zzl_no_lit(lambda: bg_variant(loc, "Night"))

    def zzl_has(findings, *words):
        """bool: one finding holds every one of these words."""
        return any(all(w in f for w in words) for f in findings)

    def zzl_open_all():
        """Every lock but the hour's opened: the flags that open the
        storehouse and the two offices, an invitation to the girls'
        corridor, and Bond enough for every door."""
        for f in ("storehouse_access", "utahime_arrived", "intensive_done", "invited_girls_dorm"):
            flag(f)
        store.bonds = builtins.dict((w, 100) for w in ROSTER_ORDER)


label zz_smoke:

    $ settle(day=8, period="Night", here="courtyard")
    python:
        store.roster = builtins.list(ROSTER_ORDER)
        store.explore_mode = False
        zzl_hold()
        check(ZZL_INIT["loadable"] and "library" in WORLD_LIT_ON and renpy.has_image(("bg", "library", "lit"), exact=True),
              "the test picture of the Library lit is there (tools/smoke/assets/u2_lit, or an installed one) and registered",
              (ZZL_INIT, builtins.dict(WORLD_LIT_ON)))
        note("the tree's own lit pictures at init", builtins.sorted(ZZL_INIT["on"]) or "none")

    ## --- A. the names ---------------------------------------------------------------
    python:
        check(ART_HOURS[:2] == ("evening", "night") and "lit" in ART_HOURS and WORLD_LIT_ATTR == "lit" and "_" not in WORLD_LIT_ATTR,
              "A: ART_HOURS gains `lit` after the two hours, one token with no underscore", ART_HOURS)
        check(art_parent("library_lit") == "library" and art_parent("your_room_lit") == "your_room"
              and all(art_parent("%s_lit" % art_stem(l)) == art_stem(l) for l, p in WORLD_LIT)
              and art_parent("fg_library_lit") == "library_lit" and art_parent("fg_dorm_lit") == "your_room_lit"
              and art_parent("light_library_lit") == "library_lit" and art_parent("light_dorm_lit") == "your_room_lit"
              and art_parent("pose_library__megumi__lit") == "library_lit"
              and art_parent("pose_senpai_room__panda__lit__asleep") == "senpai_room_lit"
              and art_parent("pose_dorm__yuji__lit") == "your_room_lit"
              and art_parent("library") is None and art_parent("zz_lit") is None and art_parent("fg_zz_lit") is None
              ## the two hours are read as they were
              and art_parent("library_night") == "library" and art_parent("fg_library_night") == "library_night"
              and art_parent("pose_library__toge__evening") == "library_evening",
              "A: a lit name is read to its parent as an hour's name is: <picture>_lit to the day picture; fg_, light_ and pose_ names to <picture>_lit")
        zzl_blank(True)
        zzl_art(library=dict(rev=2, kind="inplace"))
        check(not art_fresh("library_lit") and not art_fresh("library_lit", "library") and not art_fresh("fg_library_lit")
              and not art_fresh("light_library_lit") and not art_fresh("pose_library__megumi__lit")
              and art_fresh("megumi_room_lit") and art_fresh("fg_megumi_room_lit"),
              "A: with the Library's day picture replaced and no other row, its lit picture and everything made from it are stale, and no other room's is")
        zzl_art(library_lit=dict(rev=2, kind="relight", of="library", of_rev=2))
        check(art_fresh("library_lit") and art_rev("library_lit") == 2 and not art_fresh("fg_library_lit")
              and not art_fresh("light_library_lit") and not art_fresh("pose_library__megumi__lit") and art_validate() == [],
              "A: the manifest row {rev, kind: relight, of, of_rev} makes the lit picture fresh again and lints clean; a cut, a light row and a pose made from the OLD lit picture stay stale",
              art_validate())
        zzl_art(fg_library_lit=dict(of="library_lit", of_rev=2), light_library_lit=dict(of="library_lit", of_rev=2),
                pose_library__megumi__lit=dict(of="library_lit", of_rev=2))
        check(art_fresh("fg_library_lit") and art_fresh("light_library_lit") and art_fresh("pose_library__megumi__lit")
              and art_validate() == [],
              "A: each fresh again with its own row {of: library_lit, of_rev}", art_validate())
        zzl_art(library_lit=dict(rev=3, kind="relight", of="library", of_rev=2))
        check(not art_fresh("fg_library_lit") and not art_fresh("light_library_lit") and not art_fresh("pose_library__megumi__lit"),
              "A: and stale again when the lit picture itself is repainted")
        zzl_back()

        ## -- every gate that builds a file name or a key from the attribute.
        ## Megumi is in the Library on a Sunday Night (section E), so the lit
        ## picture is the one showing; on the Saturday nobody is.
        zzl_night("night")
        zzl_set_files({"images/fg/fg_library.png": True, "images/fg/fg_library_lit.png": True, "images/fg/fg_library_night.png": True,
                       "images/place/pose_library__megumi__lit.png": True, "images/place/pose_library__megumi__night.png": True})
        RULE_LAYOUT["pose_library"] = builtins.dict(poses=builtins.dict(megumi__lit=[100, 200, 300, 400], megumi__night=[500, 200, 300, 400]))
        RULE_LAYOUT["light_library"] = {"": ["#ffffff", 0.0, 1.0, 0.4], "night": ["#8090c0", -0.1, 0.9, 0.3],
                                        "lit": ["#ffd9a0", -0.02, 0.97, 0.45, 12, 1.1]}
        _zz_table = {"": "day", "night": "dark", "lit": "lamps"}
        zzl_at("Sun")
        _zz_lit = (bg_variant("library", "Night"), view_fg_path("library", "Night"), view_pose("megumi", "library", "Night"),
                   light_for_place("library", "Night"), view_hour_row(_zz_table, "library", "Night"), light_for_bg("bg library lit"))
        zzl_at("Sat")
        _zz_dark = (bg_variant("library", "Night"), view_fg_path("library", "Night"), view_pose("megumi", "library", "Night"),
                    light_for_place("library", "Night"), view_hour_row(_zz_table, "library", "Night"), light_for_bg("bg library night"))
        check(_zz_lit[0] == "lit" and _zz_dark[0] == "night", "A: (the test: the Library shows `lit` on the Sunday Night and `night` on the Saturday)",
              (_zz_lit[0], _zz_dark[0]))
        check(_zz_lit[1] == "images/fg/fg_library_lit.png" and _zz_dark[1] == "images/fg/fg_library_night.png",
              "A: the foreground cut of a lit room is fg_<place>_lit.png (view_fg_path), and the dark room keeps fg_<place>_night.png", (_zz_lit[1], _zz_dark[1]))
        check(_zz_lit[2] == builtins.dict(image="images/place/pose_library__megumi__lit.png", box=(100, 200, 300, 400))
              and _zz_dark[2] == builtins.dict(image="images/place/pose_library__megumi__night.png", box=(500, 200, 300, 400)),
              "A: a pose in a lit room is the file pose_PLACE__WHO__lit.png with the box under the key WHO__lit (view_pose)", (_zz_lit[2], _zz_dark[2]))
        check(_zz_lit[3] == ("#ffd9a0", -0.02, 0.97, 0.45, 12, 1.1) and _zz_dark[3] == ("#8090c0", -0.1, 0.9, 0.3)
              and _zz_lit[5] == _zz_lit[3] and _zz_dark[5] == _zz_dark[3],
              "A: the light row of a lit room is the one under the key `lit` of light_<place>.json, for the place view (light_for_place) and for the picture shown by name (light_for_bg); the dark room keeps `night`",
              (_zz_lit[3], _zz_dark[3], _zz_lit[5]))
        check(_zz_lit[4] == "lamps" and _zz_dark[4] == "dark",
              "A: a view_ file's hour table is read under `lit` for a lit room and under `night` for the dark one (view_hour_row)", (_zz_lit[4], _zz_dark[4]))
        ## a stale cut, a stale pose and a stale light row are stepped round (K7)
        zzl_at("Sun")
        zzl_art(library_lit=dict(rev=2, kind="relight", of="library", of_rev=1))
        check(bg_variant("library", "Night") != "lit",
              "A: a lit picture at a later revision whose cut was made for the old one is not shown (a room with a foreground)",
              bg_variant("library", "Night"))
        zzl_art(fg_library_lit=dict(of="library_lit", of_rev=2))
        check(bg_variant("library", "Night") == "lit" and view_fg_path("library", "Night") == "images/fg/fg_library_lit.png"
              and view_pose("megumi", "library", "Night") is None and light_for_place("library", "Night") != ("#ffd9a0", -0.02, 0.97, 0.45, 12, 1.1),
              "A: recut, it shows; and a pose and a light row made for the old lit picture are not used (the standing sprite, the general row)",
              (bg_variant("library", "Night"), view_pose("megumi", "library", "Night"), light_for_place("library", "Night")))
        zzl_back()
        check(renpy.loadable is ZZL_REAL["loadable"] and not ZZL_FILES, "A: (tables and files put back)")

    ## --- B. the table and its registration -----------------------------------------
    python:
        check(isinstance(WORLD_LIT, builtins.tuple) and all(isinstance(r, builtins.tuple) and len(r) == 2 for r in WORLD_LIT)
              and all(l in LOCATIONS and p == "images/bg/%s_lit.png" % art_stem(l) for l, p in WORLD_LIT)
              and len(builtins.set(l for l, p in WORLD_LIT)) == len(WORLD_LIT)
              and builtins.set(l for l, p in WORLD_LIT) >= builtins.set(("library", "yuji_room", "megumi_room", "senpai_room",
                                                                         "nobara_room", "maki_room", "dorm", "dojo"))
              and builtins.dict(WORLD_LIT)["dorm"] == "images/bg/your_room_lit.png",
              "B: WORLD_LIT is ((place, images/bg/<stem>_lit.png), ...), each room once: the Library, the five friends' rooms, My Room (your_room_lit) and the dojo",
              WORLD_LIT)
        check(len(WORLD_VARIANTS) == 56 and all(a in ("evening", "night") for l, p, a, f in WORLD_VARIANTS)
              and not any("lit" in f for l, p, a, f in WORLD_VARIANTS)
              and not any(a == "lit" for cells in zzl.held["variant"].values() for a in cells.values()),
              "B: a table of its own: WORLD_VARIANTS keeps its 56 rows of evening and night, and no TIME_VARIANT cell is `lit`")
        check(zzl_owner(world_lit_register) and builtins.str(inspect.signature(world_lit_register)) == "()",
              "B: world_lit_register() lives in sb_world.rpy")
        ## what the game's own registration did at init, by its rule
        check(builtins.set(ZZL_INIT["on"]) <= builtins.set(l for l, p in WORLD_LIT)
              and all(ZZL_INIT["on"][l] == builtins.dict(WORLD_LIT)[l] for l in ZZL_INIT["on"])
              and (("library" in ZZL_INIT["on"]) == (ZZL_INIT["loadable"] and ZZL_INIT["fresh"]))
              and all(l in ZZL_INIT["on"] or l == "library" or not renpy.has_image(builtins.tuple(LOCATIONS[l]["bg"].split()) + ("lit",), exact=True)
                      for l, p in WORLD_LIT)
              and all(ZZL_REAL["loadable"](p) for l, p in ZZL_INIT["on"].items()),
              "B: at init a row registered exactly when its file was loadable and fresh against its day picture (the Library's test picture: %s), "
              "and a row with no file defined no image" % ("registered by the game" if "library" in ZZL_INIT["on"] else "stale in this tree's manifest, registered by the harness"),
              ZZL_INIT)
        check(world_lit_validate() == [] and world_late_validate() == [] and _validate_world() == [],
              "B: lint finds nothing in the tables as they are", world_lit_validate() + world_late_validate() + _validate_world())

        ## -- with no lit picture registered nothing differs, whoever is where
        _zz_true = zzl_no_lit(lambda: zzl_up_is(True, zzl_pictures))
        _zz_false = zzl_no_lit(lambda: zzl_up_is(False, zzl_pictures))
        _zz_real = zzl_no_lit(zzl_pictures)
        check(len(_zz_true) == len(LOC_ORDER) * 5 * 7 and _zz_true == _zz_false == _zz_real
              and not any(r[3] == "lit" or r[4].endswith(" lit") for r in _zz_true),
              "B: with no lit picture registered, bg_variant never answers `lit`, and its answer and bg_name's for every place (%d) at "
              "every hour on every day of the week are the same whoever is where (world_night_up made to answer True, then False, then left alone)"
              % len(LOC_ORDER), [a for a, b in zip(_zz_true, _zz_false) if a != b][:4])
        ## -- with the test picture registered, only the registered rooms' Night can differ
        _zz_with = zzl_up_is(True, zzl_pictures)
        _zz_diff = [a for a, b in zip(_zz_with, _zz_real) if a != b]
        check(_zz_diff and all(r[1] == "Night" and r[2] in WORLD_LIT_ON and r[3] == "lit" for r in _zz_diff)
              and builtins.set(r[2] for r in _zz_diff) == builtins.set(l for l in WORLD_LIT_ON if world_lit_ready(l)),
              "B: with a lit picture registered and somebody up everywhere, the only cells that differ are the Night of the rooms whose lit picture is ready",
              _zz_diff[:4])
        zzl_back()

    ## --- C. the reader ----------------------------------------------------------------
    python:
        zzl_blank(True)
        check(builtins.str(inspect.signature(bg_variant)) == "(loc, per)" and builtins.str(inspect.signature(bg_name)) == "(loc=None, per=None)"
              and builtins.str(inspect.signature(graded_bg)) == "(loc=None, per=None)"
              and builtins.str(inspect.signature(world_night_up)) == "(loc, per=None)"
              and builtins.str(inspect.signature(world_lit_bg)) == "(place)"
              and all(zzl_owner(f) for f in (bg_variant, world_night_up, world_lit_bg, world_lit_ready, world_late_cell,
                                             world_lit_validate, world_late_validate, char_location)),
              "C: bg_variant(loc, per) keeps its signature (B6); world_night_up(loc, per=None) and world_lit_bg(place) live in sb_world.rpy")
        for _zz_cell in ("night", None):
            zzl_night(_zz_cell)
            _zz_tag = "C (the dark Library is %s): " % ("a painted `night`" if _zz_cell else "the day picture, tinted")
            ## lit with Megumi there
            zzl_at("Sun")
            _zz_dark = zzl_no_lit(lambda: (bg_variant("library", "Night"), bg_name("library", "Night")))
            check(_zz_dark == (_zz_cell, "bg library" + (" night" if _zz_cell else "")), _zz_tag + "(the test's dark answer)", _zz_dark)
            check(char_location("megumi") == "library" and world_night_up("library") is True
                  and bg_variant("library", "Night") == "lit" and bg_name("library", "Night") == "bg library lit"
                  and graded_bg("library", "Night") == "bg library lit",
                  _zz_tag + "lit with Megumi there: bg_variant answers `lit`, bg_name `bg library lit`, and graded_bg the picture untinted",
                  (char_location("megumi"), bg_variant("library", "Night"), graded_bg("library", "Night")))
            ## lit still when he is walking with me in it
            zzl_at("Sun", here="library", companion="megumi")
            check(bg_variant("library", "Night") == "lit" and bg_name() == "bg library lit" and world_night_up("library")
                  and who_is_here("library").count("megumi") == 1,
                  _zz_tag + "lit still when he is walking with me in it", (bg_variant("library", "Night"), who_is_here("library")))
            ## dark with nobody
            zzl_at("Sat", here="library")
            check(not [w for w in ROSTER_ORDER if char_location(w) == "library"] and world_night_up("library") is False
                  and (bg_variant("library", "Night"), bg_name("library", "Night")) == _zz_dark,
                  _zz_tag + "dark with nobody there (I am standing in it, and do not count): exactly what it answers with no lit picture",
                  (bg_variant("library", "Night"), bg_name("library", "Night")))
            ## dark with someone walking with me whose table has them elsewhere
            zzl_at("Sat", here="library", companion="megumi")
            check(who_is_here("library") == ["megumi"] and char_location("megumi") == "megumi_room"
                  and (bg_variant("library", "Night"), bg_name("library", "Night")) == _zz_dark,
                  _zz_tag + "dark with someone walking with me whose own table has them elsewhere (who_is_here counts him there; the light does not)",
                  (who_is_here("library"), bg_variant("library", "Night")))
            ## nothing different at Evening, or at any other hour, with people there
            zzl_at("Sun", per="Evening", here="library")
            pin("megumi", "library")
            _zz_ev = [(p, bg_variant("library", p), bg_name("library", p)) for p in PERIODS if p != "Night"]
            check(builtins.len(who_is_here("library")) >= 2 and world_night_up("library") is False
                  and world_night_up("library", "Evening") is False
                  and _zz_ev == zzl_no_lit(lambda: [(p, bg_variant("library", p), bg_name("library", p)) for p in PERIODS if p != "Night"])
                  and not any(v == "lit" for p, v, n in _zz_ev),
                  _zz_tag + "nothing different at Evening or at any hour but Night, with three people in the room", (who_is_here("library"), _zz_ev))
            ## asked in the Evening about tonight
            check(world_night_up("library", "Night") is True and bg_variant("library", "Night") == "lit",
                  _zz_tag + "asked in the Evening about the Night, it answers for tonight (a Sunday: lit)")
            ## dark when the lit file is stale; lit again with its row
            zzl_at("Sun")
            zzl_art(library=dict(rev=2, kind="inplace"))
            check(world_night_up("library") and not world_lit_ready("library") and bg_variant("library", "Night") is None
                  and bg_name("library", "Night") == "bg library",
                  _zz_tag + "dark when the lit file is stale (the day picture replaced): the day picture tinted, as for any stale hour picture",
                  (bg_variant("library", "Night"), bg_name("library", "Night")))
            zzl_art(library_lit=dict(rev=2, kind="relight", of="library", of_rev=2))
            check(bg_variant("library", "Night") == "lit", _zz_tag + "lit again once the lit picture has a row made for the new day picture")
            zzl_art(library=None, library_lit=None)
            ## dark when its foreground cut is missing, in a room that has one
            zzl_set_files({"images/fg/fg_library.png": True, "images/fg/fg_library_lit.png": False, "images/fg/fg_library_night.png": True})
            check(world_fg_room("library") and world_night_up("library") and not world_lit_ready("library")
                  and (bg_variant("library", "Night"), bg_name("library", "Night")) == _zz_dark,
                  _zz_tag + "dark when the room has a foreground and the lit picture's own cut is missing", bg_variant("library", "Night"))
            zzl_set_files({"images/fg/fg_library.png": True, "images/fg/fg_library_lit.png": True, "images/fg/fg_library_night.png": True})
            check(bg_variant("library", "Night") == "lit", _zz_tag + "lit with its cut there")
            zzl_art(library_lit=dict(rev=2, kind="relight", of="library", of_rev=1))
            check((bg_variant("library", "Night"), bg_name("library", "Night")) == _zz_dark,
                  _zz_tag + "dark when the cut is stale (made for the lit picture of before)", bg_variant("library", "Night"))
            zzl_art(library_lit=None)
            ## dark when the file is gone
            zzl_set_files({ZZL_PATH: False})
            check(not world_lit_ready("library") and (bg_variant("library", "Night"), bg_name("library", "Night")) == _zz_dark,
                  _zz_tag + "dark when the lit file is not loadable", bg_variant("library", "Night"))
            zzl_set_files({})

            ## the two are two cache rows, and _light_key is unchanged
            zzl_at("Sun")
            _zz_a = graded_bg("library", "Night")
            zzl_at("Sat")
            _zz_b = graded_bg("library", "Night")
            zzl_at("Sun")
            check(("library", "Night", "lit") in _BG_CACHE and ("library", "Night", None) in _BG_CACHE
                  and _BG_CACHE[("library", "Night", "lit")] is _zz_a and _BG_CACHE[("library", "Night", None)] is _zz_b
                  and graded_bg("library", "Night") is _zz_a and _zz_a == "bg library lit" and _zz_a != _zz_b
                  and ("library", "Night") not in _BG_CACHE,
                  _zz_tag + "the two pictures of the Library's Night are two cache rows, (place, hour, `lit`) and (place, hour, None), each built once",
                  builtins.sorted(_BG_CACHE, key=builtins.str))
            check((isinstance(_zz_b, Transform) and getattr(_zz_b, "_light_key", None) == ("library", "Night")) if not _zz_cell
                  else (_zz_b == "bg library night"),
                  _zz_tag + ("the tinted one carries _light_key (place, hour), as before" if not _zz_cell else "the painted dark one is its name, as before"),
                  getattr(_zz_b, "_light_key", _zz_b))

        ## -- _light_key is (place, hour) on every tinted picture, and a painted one carries none
        zzl_back()
        zzl_at("Sun")
        _zz_keys = []
        for _zz_l in LOC_ORDER:
            for _zz_p in PERIODS:
                _zz_g = graded_bg(_zz_l, _zz_p)
                if isinstance(_zz_g, Transform):
                    _zz_keys.append((_zz_l, _zz_p, getattr(_zz_g, "_light_key", None)))
        check(_zz_keys and all(k == (l, p) for l, p, k in _zz_keys) and all(len(k) == 3 for k in _BG_CACHE)
              and not hasattr(graded_bg("library", "Night"), "_light_key"),
              "C: _light_key is unchanged: (place, hour) on every tinted picture (%d of them, all 35 places at five hours), while every cache key has three parts; "
              "a painted picture carries none and is lit by its own name" % len(_zz_keys), [r for r in _zz_keys if r[2] != (r[0], r[1])][:3])

        ## -- someone asleep lights nothing; a friend's room is lit only while they are up in it
        zzl_blank(True)
        WORLD_LIT_ON["megumi_room"] = builtins.dict(WORLD_LIT)["megumi_room"]
        zzl_set_files({builtins.dict(WORLD_LIT)["megumi_room"]: True})
        TIME_VARIANT["megumi_room"] = builtins.dict(Night="night")
        zzl_at("Tue", here="megumi_room")
        _zz_asleep = (char_location("megumi"), world_asleep("megumi"), who_is_here("megumi_room"), world_night_up("megumi_room"), bg_variant("megumi_room", "Night"))
        zzl_at("Sat", here="megumi_room")
        _zz_awake = (char_location("megumi"), world_asleep("megumi"), world_night_up("megumi_room"), bg_variant("megumi_room", "Night"))
        zzl_at("Sun", here="megumi_room")
        _zz_out = (char_location("megumi"), who_is_here("megumi_room"), world_night_up("megumi_room"), bg_variant("megumi_room", "Night"))
        check(_zz_asleep == ("megumi_room", True, ["megumi"], False, "night"),
              "C: dark with only someone asleep in it (Megumi's room on a Tuesday Night: he is counted there, asleep, and the room shows `night`)", _zz_asleep)
        check(_zz_awake == ("megumi_room", False, True, "lit"), "C: lit while he is up in it (a Saturday Night)", _zz_awake)
        check(_zz_out == ("library", [], False, "night"), "C: dark while he is out late (a Sunday Night: his room is empty)", _zz_out)
        ## walking a friend home lights their room: asked along, he is not asleep
        zzl_at("Tue", here="megumi_room", companion="megumi")
        check(world_asleep("megumi") is False and bg_variant("megumi_room", "Night") == "lit",
              "C: walking a friend home lights their room (a Tuesday Night, Megumi walking with me into his own room)", bg_variant("megumi_room", "Night"))
        ## a story pin lights the room it names
        zzl_at("Sat")
        pin("yuji", "library")
        check(world_night_up("library") and bg_variant("library", "Night") == "lit",
              "C: a story pin counts: someone pinned into the Library at Night lights it", bg_variant("library", "Night"))
        store.schedule_overrides = {}
        ## the roster is read, never who_is_here
        zzl_at("Sun", here="library", companion="megumi")
        _zz_v = zzl_count_here(lambda: (bg_variant("library", "Night"), world_night_up("library"), graded_bg("library", "Night")))
        _zz_calls = builtins.list(ZZL_CALLS)
        _zz_probe = zzl_count_here(lambda: who_is_here("library"))
        store.roster = ["megumi"]
        _zz_one = world_night_up("library")
        store.roster = [w for w in ROSTER_ORDER if w != "megumi"]
        _zz_none = (world_night_up("library"), bg_variant("library", "Night"))
        store.roster = builtins.list(ROSTER_ORDER)
        check(_zz_v[0] == "lit" and not _zz_calls and len(ZZL_CALLS) == 1 and _zz_one is True and _zz_none == (False, zzl_dark()),
              "C: the light reads the roster and each person's own place, never who_is_here (counted: no call); someone I have not met lights nothing",
              (_zz_v, _zz_calls, _zz_one, _zz_none))

        ## -- a replay is lit by the memory's own cast
        zzl_at("Sat")           ## by the weekday nobody is in the Library
        _zz_m = [m for m in MEMORIES if m["who"]][0]
        _zz_e = [m for m in MEMORIES if not m["who"]]
        store._mem_label, store._mem_args = _zz_m["label"], builtins.tuple(_zz_m["args"])
        store._in_replay = "mem_play"
        _BG_CACHE.clear()
        _zz_r1 = (world_night_up("library"), bg_variant("library", "Night"), bg_name("library", "Night"))
        store._mem_label, store._mem_args = "zz_no_such_memory", ()
        _BG_CACHE.clear()
        _zz_r2 = (world_night_up("library"), bg_variant("library", "Night"))
        if _zz_e:
            store._mem_label, store._mem_args = _zz_e[0]["label"], builtins.tuple(_zz_e[0]["args"])
        _zz_r3 = (world_night_up("library"), bg_variant("library", "Night")) if _zz_e else None
        ## and on a Sunday, where the weekday would light it, a memory with nobody in it does not
        zzl_at("Sun")
        store._mem_label, store._mem_args = "zz_no_such_memory", ()
        _zz_r4 = (world_night_up("library"), bg_variant("library", "Night"))
        store._in_replay = None
        del store._mem_label
        del store._mem_args
        _zz_night = zzl_dark()
        check(_zz_r1 == (True, "lit", "bg library lit"),
              "C: a replay of a memory that names a person (%s) shows the lit room, on a weekday on which nobody is there" % _zz_m["id"], _zz_r1)
        check(_zz_r2 == (False, _zz_night) and _zz_r4 == (False, _zz_night),
              "C: a replay of a memory that is not found shows `night`, on a Sunday too: a memory's room is lit by its cast, never by the weekday", (_zz_r2, _zz_r4))
        if _zz_e:
            check(_zz_r3 == (False, _zz_night), "C: and so does a memory that names nobody (%s)" % _zz_e[0]["id"], _zz_r3)
        else:
            note("C: a memory that names nobody", "there is none in MEMORIES today; the clause is read on a memory that is not found")
        check(not hasattr(store, "_mem_label") and not hasattr(store, "_mem_args") and store._in_replay is None, "C: (the replay's marks taken away again)")

        ## -- no hour in the store: bg_name answers as today (init, where the memory tiles are built)
        zzl_at("Sun")
        _zz_want = zzl_no_lit(lambda: (bg_variant("library", "Night"), bg_name("library", "Night")))
        _zz_per = store.period
        store.period = None
        _zz_got = (world_night_up("library", "Night"), bg_variant("library", "Night"), bg_name("library", "Night"))
        store.period = _zz_per
        check(_zz_got == (False,) + _zz_want and bg_variant("library", "Night") == "lit",
              "C: with no hour in the store (init: the memory tiles; lint) world_night_up is False and bg_name answers as today, the plain night", (_zz_got, _zz_want))
        check(all(m["bg"] == zzl_no_lit(lambda: bg_name(*m["place"])) for m in MEMORIES if m.get("place") and m["args"]),
              "C: every memory tile built from a place holds the picture bg_name answers with no lit picture (they are built at init)")
        zzl_blank(False)

    ## --- D. written scenes: world_lit_bg --------------------------------------------
    python:
        zzl_blank(True)
        zzl_night(None)
        zzl_at("Sat")
        check(world_lit_ready("library") and not world_night_up("library") and world_lit_bg("library") == "bg library lit",
              "D: world_lit_bg answers the lit picture by name when it is installed and fresh, and does not ask who is there (a Saturday: nobody)",
              world_lit_bg("library"))
        zzl_art(library=dict(rev=2, kind="inplace"))
        check(world_lit_bg("library") is graded_bg("library", "Night") and isinstance(world_lit_bg("library"), Transform),
              "D: stale, it answers graded_bg(place, \"Night\"): what the scene would have shown without it", world_lit_bg("library"))
        zzl_art(library=None)
        zzl_set_files({"images/fg/fg_library.png": True})
        check(world_lit_bg("library") is graded_bg("library", "Night"), "D: and so it does in a room with a foreground whose lit cut is missing")
        zzl_set_files({})
        check(all((world_lit_bg(l) == "%s lit" % LOCATIONS[l]["bg"]) if world_lit_ready(l) else (world_lit_bg(l) is graded_bg(l, "Night"))
                  for l in LOC_ORDER)
              and all(world_lit_bg(l) is graded_bg(l, "Night") for l in LOC_ORDER if l not in WORLD_LIT_ON),
              "D: for every place: the lit picture where one is ready, else graded_bg(place, \"Night\") (a place with no lit picture too)")
    ## shown by a scene, it sets the light from its own name
    python:
        RULE_LAYOUT["light_library"] = {"lit": ["#ffd9a0", -0.02, 0.97, 0.45]}
    scene expression world_lit_bg("library")
    python:
        zz_render(0.2)
        check(store.scene_light == ("#ffd9a0", -0.02, 0.97, 0.45) and renpy.showing("bg library lit"),
              "D: shown by a scene (scene expression world_lit_bg(\"library\")) the picture is up and the people's light is its own `lit` row",
              store.scene_light)
        shot("scene_world_lit_bg")
    scene black
    python:
        zzl_blank(False)

    ## --- E. the late stays ------------------------------------------------------------
    python:
        check(isinstance(WORLD_LATE, builtins.dict)
              and all(isinstance(r, builtins.tuple) and len(r) == 2 and r[0] in LOCATIONS and isinstance(r[1], builtins.tuple)
                      and r[1] and all(d in WEEKDAYS for d in r[1]) for r in WORLD_LATE.values())
              and WORLD_LATE.get("megumi") == ("library", ("Sun",)) and WORLD_LATE.get("toge") == ("library", ("Wed",)),
              "E: WORLD_LATE is {who: (place, weekdays)}, with the two rows the owner approved: Megumi in the Library on Sundays, Toge on Wednesdays (O47)",
              builtins.dict(WORLD_LATE))
        check(not any(d in ("Tue", "Fri", "Sat") for r in WORLD_LATE.values() for d in r[1]),
              "E: no stay falls on a Tuesday, a Friday or a Saturday, the Nights the frozen harnesses fix")
        zzl_at("Sun")
        _zz_sun = (char_location("megumi"), world_asleep("megumi"), world_home_state("megumi"), world_room_state("megumi_room"),
                   who_is_here("megumi_room"), who_is_here("library"), world_late_cell("megumi"), stage_people("library")[0])
        check(_zz_sun == ("library", False, "out", {"megumi": "out"}, [], ["megumi"], "library", ["megumi"]),
              "E: on a Sunday Night Megumi is in the Library, awake and \"out\" of his home; his room is empty and the Library's stage has him", _zz_sun)
        zzl_at("Sat")
        _zz_sat = (char_location("megumi"), world_asleep("megumi"), world_home_state("megumi"), world_late_cell("megumi"))
        check(_zz_sat == ("megumi_room", False, "awake", None), "E: on a Saturday Night he is at home, awake", _zz_sat)
        zzl_at("Wed")
        _zz_wed = (char_location("toge"), world_asleep("toge"), world_home_state("toge"), world_room_state("senpai_room"),
                   who_is_here("senpai_room"), stage_people("senpai_room")[0])
        check(_zz_wed == ("library", False, "out", {"panda": "asleep", "toge": "out"}, ["panda"], []),
              "E: on a Wednesday Night Toge is in the Library; the room he shares holds Panda, asleep, and nobody on its stage", _zz_wed)
        ## only at Night
        zzl_at("Sun")
        check(all(world_late_cell(w, p) is None for w in WORLD_LATE for p in PERIODS if p != "Night")
              and [char_location("megumi", p) for p in PERIODS if p != "Night"]
              == zzl_no_late(lambda: [char_location("megumi", p) for p in PERIODS if p != "Night"]),
              "E: the table speaks of the Night only: the other four hours of a late day are what they are without it")
        ## a story pin beats the table, and so does a flag schedule; the roster still decides
        pin("megumi", "cafeteria")
        _zz_pin = (char_location("megumi"), world_night_up("library"))
        pin("megumi", "-")
        _zz_pin2 = char_location("megumi")
        store.schedule_overrides = {}
        FLAG_SCHEDULES.append(("zz_u2l_flag", "megumi", {"Night": "dojo"}))
        flag("zz_u2l_flag")
        _zz_flag = char_location("megumi")
        FLAG_SCHEDULES.pop()
        store.flags.discard("zz_u2l_flag")
        store.roster = [w for w in ROSTER_ORDER if w != "megumi"]
        _zz_unmet = char_location("megumi")
        store.roster = builtins.list(ROSTER_ORDER)
        check(_zz_pin == ("cafeteria", False) and _zz_pin2 is None and _zz_flag == "dojo" and _zz_unmet is None and char_location("megumi") == "library",
              "E: a story pin beats the table (pinned to the cafeteria, or off campus), a flag schedule replaces it, and someone I have not met is nowhere",
              (_zz_pin, _zz_pin2, _zz_flag, _zz_unmet))
        ## the whole fortnight: exactly the cells the table names
        _zz_with = zzl_where()
        _zz_without = zzl_no_late(zzl_where)
        _zz_cells = zzl_late_cells()
        _zz_diff = builtins.dict((k, v) for k, v in _zz_with.items() if _zz_without[k] != v)
        check(len(_zz_with) == 14 * 5 * len(ROSTER_ORDER) and _zz_diff == _zz_cells and len(_zz_cells) >= 1
              and all(_zz_without[k] == WORLD_HOMES.get(k[2]) for k in _zz_cells),
              "E: with WORLD_LATE emptied, char_location for everyone on the roster at all five hours on days 1 to 14 (%d cells) is what it is with the table, "
              "except in exactly the cells the table names (%d: %s), where the person is at home without it"
              % (len(_zz_with), len(_zz_cells), ", ".join("%s day %d" % (k[2], k[0]) for k in builtins.sorted(_zz_cells))),
              (builtins.sorted(_zz_diff)[:6], builtins.sorted(_zz_cells)[:6]))
        ## the "usually" line is left alone
        check(zzl_usual() == zzl_no_late(zzl_usual) and "nights" not in when_at("megumi", "library"),
              "E: the routine's own words (usual_places, when_at, routine_location) do not know the table: a late stay is not usual")
        ## asleep lists: every stayer is awake on their Nights, and nobody out late is asleep
        _zz_bad = []
        for _zz_d in range(8, 15):
            zzl_at(_zz_d)
            for _zz_w in ROSTER_ORDER:
                if world_late_cell(_zz_w) and (world_asleep(_zz_w) or world_home_state(_zz_w) != "out" or char_location(_zz_w) == WORLD_HOMES.get(_zz_w)):
                    _zz_bad.append((weekday(), _zz_w))
                if world_asleep(_zz_w) and char_location(_zz_w) != WORLD_HOMES.get(_zz_w):
                    _zz_bad.append((weekday(), _zz_w, "asleep away from home"))
        check(not _zz_bad, "E: on each of the seven Nights whoever is out late is awake and \"out\", and nobody is asleep anywhere but at home", _zz_bad)

        ## -- the journal's "right now" line and the map's pin read char_location
        zzl_at("Sun")
        _zz_now = person_now("megumi")
        zzl_at("Sun", here="library")
        _zz_now2 = person_now("megumi")
        check(_zz_now["place"] == "library" and _zz_now["name"] == LOCATIONS["library"]["name"] and _zz_now["reachable"] is True
              and not _zz_now["hidden"] and _zz_now["doing"] and _zz_now["doing"] != "asleep" and _zz_now["doing"] == ambient_of("megumi", "library")[0]
              and _zz_now2["place"] == "library" and _zz_now2["reachable"] is False and builtins.sorted(_zz_now) == builtins.sorted(
                  ["place", "name", "doing", "reachable", "hidden", "with_me"]),
              "E: person_now says where he is that Night: the Library, open, with his caption there (\"%s\"), reachable unless I stand in it; its six keys as ever"
              % _zz_now["doing"], (_zz_now, _zz_now2))

        ## -- what is offered by someone out late: as in their own room at Night
        zzl_open_all()
        store.talked_today, store.spent_today = set(), set()
        _zz_off = builtins.dict()
        for _zz_w, _zz_row in builtins.sorted(WORLD_LATE.items()):
            zzl_at(_zz_row[1][0], here=_zz_row[0])
            _zz_late = (zzl_offered(_zz_w, _zz_row[0]), [c["id"] for c in person_choices(_zz_w, _zz_row[0])], missions_with(_zz_w, _zz_row[0]))
            ## a Night on which they are up at home
            _zz_hd = [d for d in WEEKDAYS if d not in _zz_row[1]
                      and _zz_w not in WORLD_ASLEEP["weekend" if d in ("Sat", "Sun") else "weekday"]]
            zzl_at(_zz_hd[0], here=WORLD_HOMES[_zz_w])
            _zz_home = (zzl_offered(_zz_w, WORLD_HOMES[_zz_w]), [c["id"] for c in person_choices(_zz_w, WORLD_HOMES[_zz_w])],
                        missions_with(_zz_w, WORLD_HOMES[_zz_w]), char_location(_zz_w), world_asleep(_zz_w))
            _zz_off[_zz_w] = (_zz_late, _zz_home, _zz_hd[0])
        check(all(late[0] == home[0] and "talk" in late[0] and "invite" in late[0]
                  and all(not ACT_BY_ID[a]["cost"] or a in NIGHT_OK for a in late[0])
                  and late[1] == home[1] and late[1][-1] == "talk" and late[2] == [] and home[3] == WORLD_HOMES[w] and home[4] is False
                  for w, (late, home, d) in _zz_off.items()),
              "E: what someone out late offers is what they offer up in their own room at Night: Talk and \"Ask them along\", nothing that costs time "
              "but what the night rule lets through, and no mission", _zz_off)
        note("E: offered by someone out late", "; ".join("%s: %s" % (w, ", ".join(v[0][0])) for w, v in builtins.sorted(_zz_off.items())))
        zzl_at("Sun", here="library")
        _zz_acts = [a[0] for a in night_filter_actions("library", place_actions("library"))]
        note("E: the Library's own actions on a late Night", _zz_acts)

        ## -- on a late Night the stayer's own room opens as it always does, empty
        store.flags = set(f for f in store.flags if not f.startswith("door_"))
        _zz_doors = []
        for _zz_b in (0, 15):
            store.bonds = builtins.dict((w, _zz_b) for w in ROSTER_ORDER)
            for _zz_w, _zz_row in builtins.sorted(WORLD_LATE.items()):
                zzl_at(_zz_row[1][0], here="boys_dorm")
                _zz_a = place_access(WORLD_HOMES[_zz_w])
                _zz_hd = [d for d in WEEKDAYS if d not in _zz_row[1]][0]
                zzl_at(_zz_hd, here="boys_dorm")
                _zz_doors.append((_zz_w, _zz_b, _zz_a, place_access(WORLD_HOMES[_zz_w])))
        check(all(a == b for w, n, a, b in _zz_doors) and all(a[0] == (n >= world_door_bond(WORLD_HOMES[w])) for w, n, a, b in _zz_doors),
              "E: on a late Night the stayer's own door answers as on any other Night: shut below its Bond, open at it, whoever is in", _zz_doors)

        ## -- the places shut at Night
        zzl_open_all()
        zzl_at("Sun")
        _zz_shut = [(l, place_access(l)[2]) for l in LOC_ORDER if not place_access(l)[0]]
        store.period = "Evening"
        _zz_shut_e = [l for l in LOC_ORDER if not place_access(l)[0]]
        store.period = "Night"
        check(isinstance(WORLD_SHUT_NIGHT, builtins.tuple) and builtins.sorted(l for l, t in _zz_shut) == builtins.sorted(WORLD_SHUT_NIGHT)
              and all(t == "Night" for l, t in _zz_shut) and not _zz_shut_e,
              "E: WORLD_SHUT_NIGHT is exactly the places place_access shuts at Night with every other lock open (the tag \"Night\"), and none of them is shut in the Evening",
              (_zz_shut, WORLD_SHUT_NIGHT, _zz_shut_e))
        check(not any(l in WORLD_SHUT_NIGHT for l, p in WORLD_LIT) and not any(r[0] in WORLD_SHUT_NIGHT for r in WORLD_LATE.values())
              and all(place_access(r[0])[0] for r in WORLD_LATE.values()),
              "E: no shut place has a lit picture or a late stay, and every late place is open that Night")
        store.flags = set(["settled_in"])
        store.bonds = {}

    ## --- F. lint: each refusal, made to fire -------------------------------------------
    python:
        _zz_f = builtins.dict(
            asleep=world_late_validate(late={"megumi": ("library", ("Mon",))}),
            asleep_weekend=world_late_validate(late={"toge": ("library", ("Wed", "Sat"))}),
            bond_door=world_late_validate(late={"megumi": ("girls_dorm", ("Sun",))}),
            home=world_late_validate(late={"megumi": ("infirmary", ("Sun",))}),
            home_and_door=world_late_validate(late={"megumi": ("yuji_room", ("Sun",))}),
            shut=world_late_validate(late={"megumi": ("office", ("Sun",))}),
            yard=world_late_validate(late={"megumi": ("dorm_yard", ("Sun",))}),
            no_lit=world_late_validate(late={"megumi": ("cafeteria", ("Sun",))}),
            unknown_place=world_late_validate(late={"megumi": ("zz_nowhere", ("Sun",))}),
            unknown_person=world_late_validate(late={"zz_nobody": ("library", ("Sun",))}),
            gojo=world_late_validate(late={"gojo": ("library", ("Sun",))}),
            shape=world_late_validate(late={"megumi": ("library", "Sun")}),
            day=world_late_validate(late={"megumi": ("library", ("Sunday",))}),
            ok=world_late_validate(late={"megumi": ("library", ("Sun",)), "yuji": ("library", ("Mon", "Thu"))}))
        check(zzl_has(_zz_f["asleep"], "megumi", "asleep", "Mon") and len(_zz_f["asleep"]) == 1
              and zzl_has(_zz_f["asleep_weekend"], "toge", "asleep", "Sat") and len(_zz_f["asleep_weekend"]) == 1,
              "F: lint refuses a stayer who is asleep that night (Megumi on a Monday; Toge on a Saturday, and not his Wednesday)", (_zz_f["asleep"], _zz_f["asleep_weekend"]))
        check(zzl_has(_zz_f["bond_door"], "girls_dorm", "Bond door") and not zzl_has(_zz_f["bond_door"], "home"),
              "F: lint refuses a place with a Bond door (the girls' corridor)", _zz_f["bond_door"])
        check(zzl_has(_zz_f["home"], "infirmary", "home") and len(_zz_f["home"]) == 2
              and zzl_has(_zz_f["home_and_door"], "yuji_room", "home") and zzl_has(_zz_f["home_and_door"], "yuji_room", "Bond door"),
              "F: lint refuses a home (the infirmary; and a friend's room, which is a home behind a Bond door)", (_zz_f["home"], _zz_f["home_and_door"]))
        check(zzl_has(_zz_f["shut"], "office", "shut at Night"), "F: lint refuses a place shut at Night (the principal's office)", _zz_f["shut"])
        check(zzl_has(_zz_f["yard"], "dorm_yard", "outdoors"), "F: lint refuses a yard (the Dormitory Garden)", _zz_f["yard"])
        check(_zz_f["no_lit"] and len(_zz_f["no_lit"]) == 1 and zzl_has(_zz_f["no_lit"], "cafeteria", "no WORLD_LIT row"),
              "F: lint refuses a place with no WORLD_LIT row (the Cafeteria: indoors, open, nobody's home, and that one finding)", _zz_f["no_lit"])
        check(zzl_has(_zz_f["unknown_place"], "unknown place") and zzl_has(_zz_f["unknown_person"], "zz_nobody") and zzl_has(_zz_f["gojo"], "gojo")
              and zzl_has(_zz_f["shape"], "is not (place") and zzl_has(_zz_f["day"], "is not (place") and _zz_f["ok"] == [],
              "F: and an unknown place or person, Gojo (whose place is drawn, not read from the table), a row or a weekday of the wrong shape; a good second row passes",
              (_zz_f["unknown_place"], _zz_f["unknown_person"], _zz_f["gojo"], _zz_f["shape"], _zz_f["day"], _zz_f["ok"]))
        ## a place loses its lit row, or becomes shut: the late table is refused through the other tables too
        check(zzl_has(world_late_validate(lit=builtins.tuple(r for r in WORLD_LIT if r[0] != "library")), "library", "no WORLD_LIT row")
              and zzl_has(world_late_validate(shut=WORLD_SHUT_NIGHT + ("library",)), "library", "shut at Night"),
              "F: the real table is refused when the Library loses its WORLD_LIT row, or joins the places shut at Night")
        _zz_l = builtins.dict(
            yard=world_lit_validate(lit=WORLD_LIT + (("dorm_yard", "images/bg/dorm_yard_lit.png"),)),
            shut=world_lit_validate(lit=WORLD_LIT + (("office", "images/bg/office_lit.png"),)),
            file=world_lit_validate(lit=(("dorm", "images/bg/dorm_lit.png"),), on={}),
            twice=world_lit_validate(lit=WORLD_LIT + (WORLD_LIT[0],)),
            shape=world_lit_validate(lit=(("library",), ("zz_nowhere", "x")), on={}),
            shut_name=world_lit_validate(shut=("zz_nowhere",)),
            on=world_lit_validate(on={"cafeteria": "images/bg/cafeteria_lit.png", "dojo": "images/bg/dojo_lit.png"}))
        check(zzl_has(_zz_l["yard"], "dorm_yard", "outdoors") and zzl_has(_zz_l["shut"], "office", "shut at Night")
              and zzl_has(_zz_l["file"], "your_room_lit.png") and len(_zz_l["file"]) == 1 and zzl_has(_zz_l["twice"], "listed twice") and len(_zz_l["shape"]) == 2
              and zzl_has(_zz_l["shut_name"], "WORLD_SHUT_NIGHT", "zz_nowhere")
              and zzl_has(_zz_l["on"], "cafeteria", "no WORLD_LIT row")
              and (zzl_has(_zz_l["on"], "dojo", "no image") or renpy.has_image(("bg", "dojo", "lit"), exact=True)),
              "F: WORLD_LIT's own lint: a yard, a shut place, a file that is not <stem>_lit.png (My Room's is your_room_lit), a room listed twice, "
              "a row of the wrong shape, an unknown shut place, a registered place with no row or no image", _zz_l)
        ## and lint itself reads both: a wrong row in the real table reaches _validate_world
        WORLD_LATE["megumi"] = ("dorm_yard", ("Mon",))
        _zz_v = _validate_world()
        zzl_back()
        check(zzl_has(_zz_v, "megumi", "outdoors") and zzl_has(_zz_v, "megumi", "asleep") and _validate_world() == [],
              "F: the game's lint (_validate_world) runs both: a wrong row laid in WORLD_LATE is reported, and the table as it is passes", _zz_v)

    ## --- G. the Library at Night, lit and dark, on the place view ----------------------
    python:
        zzl_blank(True)
        zzl_open_all()
        zzl_at("Sun", here="library")
        _zz_g1 = (bg_name(), graded_bg())
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        check(_zz_g1 == ("bg library lit", "bg library lit") and renpy.showing("bg library lit") and stage_people("library")[0] == ["megumi"],
              "G: a Sunday Night in the Library: the place view is drawn over the lit picture, with Megumi on its stage", (_zz_g1, stage_people("library")))
        shot("library_sunday_night_lit")
        zzl_at("Sat", here="library")
        _zz_g2 = (bg_name(), zzl_no_lit(lambda: bg_name("library", "Night")))
    scene expression graded_bg()
    python:
        zz_render(0.3)
        check(_zz_g2[0] == _zz_g2[1] and not renpy.showing("bg library lit") and stage_people("library")[0] == [],
              "G: a Saturday Night in the Library: nobody is there and the picture is the one shown with no lit picture", _zz_g2)
        shot("library_saturday_night_dark")
    hide screen sb_place
    scene black
    python:
        zzl_blank(False)
        zzl_back()
        check(builtins.dict(WORLD_LATE) == zzl.held["late"] and builtins.dict(WORLD_LIT_ON) == zzl.held["lit"]
              and builtins.dict(ART_PICTURES) == zzl.held["art"] and renpy.loadable is ZZL_REAL["loadable"]
              and store.world_night_up is zzl.held["up"] and _validate_world() == [],
              "(every table put back: the manifest, the sidecars, the hour cells, the two tables, renpy.loadable and world_night_up)")

    $ finish()
