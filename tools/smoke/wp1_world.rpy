## tools/smoke/wp1_world.rpy -- WP1's package harness (PHASE1_DESIGN.md,
## section 7, "WP1"): the world, the offices, Gojo's in-days, Tokyo, the
## ridge veil and the map.
##
##   tools/smoke.sh tools/smoke/wp1_world.rpy
##
## Every acceptance bullet is a named check. Screenshots of both map layers go
## to shots/wp1/ (as well as this harness's own shots/wp1_world/), with more
## of the placeholder backgrounds and the map in other states.

init 999 python:
    import os
    import random as zz_random

    ## --- a frozen copy of the world before phase 1 (commit 57eb3db) ----------
    ## The regression check compares today's char_location against this.
    ZZ_OLD_SCHEDULE = {
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
    ZZ_OLD_WEEKEND = {
        "yuji":   {"Morning": "dorm_common", "Afternoon": "riverside", "Evening": "cafeteria"},
        "megumi": {"Morning": "forest",      "Afternoon": "ridge"},
        "nobara": {"Morning": "girls_dorm",  "Afternoon": "riverside", "Evening": "courtyard"},
        "maki":   {"Morning": "dojo",        "Afternoon": "riverside", "Evening": "dojo"},
        "panda":  {"Afternoon": "riverside"},
        "toge":   {"Morning": "rooftop",     "Afternoon": "riverside"},
        "shoko":  {"Afternoon": "rooftop"},
        "yaga":   {"Morning": "-", "Noon": "-", "Afternoon": "-", "Evening": "-"},
    }
    ZZ_OLD_GOJO_SPOTS = ["-", "-", "-", "rooftop", "courtyard", "office", "cafeteria", "training"]
    ZZ_OLD_PERIODS = ["Morning", "Noon", "Afternoon", "Evening", "Night"]

    def zz_old_location(who, per, d, roster):
        """char_location as it was: roll_gojo seeded by the day, SCHEDULE,
        WEEKEND, the roster."""
        if who == "gojo":
            rnd = zz_random.Random(d * 977 + 13)
            today = {p: rnd.choice(ZZ_OLD_GOJO_SPOTS) for p in ZZ_OLD_PERIODS}
            loc = today.get(per, "-")
        else:
            loc = ZZ_OLD_SCHEDULE.get(who, {}).get(per, "-")
            if ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][(d - 1) % 7] in ("Sat", "Sun"):
                loc = ZZ_OLD_WEEKEND.get(who, {}).get(per, loc)
        if loc == "-" or who not in roster:
            return None
        return loc

    ## --- toasts, captured -------------------------------------------------------
    ZZ_TOASTS = []

    def zz_sink(text, kind, who, amount):
        ZZ_TOASTS.append((text, kind, who, amount))

    ## --- in-day log -------------------------------------------------------------
    ZZ_GOJO_LOG = []

    def zz_gojo_hook():
        ZZ_GOJO_LOG.append((store.day, store.gojo_in, store.gojo_today.get("Morning"),
                            char_location("gojo", "Morning"), store.hp == store.hp_max))

    register_new_day(zz_gojo_hook, order=99)

    ## --- screenshots into shots/wp1/ as well ---------------------------------------
    def zz_shot(name):
        shot(name)
        d = os.path.join(os.path.dirname(zz_smoke_state.shots.rstrip("/")), "wp1")
        try:
            if not os.path.isdir(d):
                os.makedirs(d)
            renpy.screenshot(os.path.join(d, name + ".png"))
        except Exception as e:
            note("shot wp1/" + name, repr(e))

    ## Stand-ins for WP3's queries, so the markers and badges show in a screenshot.
    def zz_fake_markers():
        return {"office": [("Yaga · The Sun Mall", "mission")],
                "utahime_office": [("Board · 3 jobs", "board")],
                "gojo_office": [("Gojo is in", "info")]}

    def zz_no_markers():
        return {}

    def zz_fake_missions_here(loc):
        return ["m_sunmall"] if loc == "office" else []

    def zz_fake_missions_with(who, loc=None):
        return ["m_sunmall"] if who == "yaga" else []


    ## --- what the script says (narration and dialogue), captured -----------------
    import builtins as zz_builtins
    ZZ_SAID = zz_builtins.list()
    _zz_filter0 = config.say_menu_text_filter

    def zz_said_filter(t):
        ZZ_SAID.append(t)
        return _zz_filter0(t) if _zz_filter0 else t

    config.say_menu_text_filter = zz_said_filter

    def zz_said(*bits):
        """True when some captured line contains every bit."""
        return any(all(b in t for b in bits) for t in ZZ_SAID)

    ## --- pressing the map's real buttons ---------------------------------------------
    ## zz_press finds a button on sb_map by its id and runs the action the
    ## screen gave it, so these checks test what the map's rows and cards do.
    ZZ_PRESSED = zz_builtins.list()

    def zz_press_fn(wid):
        w = renpy.get_widget("sb_map", wid)
        if w is None:
            ZZ_PRESSED.append((wid, None, None))
            return ("zz_missing", wid)
        a = getattr(w, "action", None)
        ZZ_PRESSED.append((wid, a, getattr(w, "_tooltip", None)))
        rv = renpy.run(a)
        return rv if rv is not None else ("zz_nothing", wid)

    def zz_pressed(wid):
        """(action, tooltip) of the last press of wid."""
        for w, a, t in reversed(ZZ_PRESSED):
            if w == wid:
                return a, t
        return None, None


## Returns a value from whatever interaction is running (a called screen).
screen zz_ret(value, delay=0.4):
    zorder 200
    timer delay action [Hide("zz_ret"), Return(value)]

## Presses one of sb_map's buttons (by id) inside the running interaction.
screen zz_press(wid, delay=0.4):
    zorder 200
    timer delay action [Hide("zz_press"), Function(zz_press_fn, wid)]


label zz_smoke:

    python:
        fixture(mc_name="Tester", mc_surname="Harness")
        settle(day=1, period="Morning", here="courtyard")
        _sink0 = TOAST_SINK[0]
        TOAST_SINK[0] = zz_sink

    ## --- 1. the places and areas ------------------------------------------------------
    python:
        check("utahime_office" in LOCATIONS and "gojo_office" in LOCATIONS, "offices in LOCATIONS")
        check(LOC_ORDER.index("office") < LOC_ORDER.index("utahime_office") < LOC_ORDER.index("gojo_office"),
              "offices in LOC_ORDER after the principal's office", LOC_ORDER)
        check(LOCATIONS["utahime_office"]["bg"] == "bg utahime_office" and LOCATIONS["gojo_office"]["bg"] == "bg gojo_office"
              and LOCATIONS["utahime_office"]["indoor"] and LOCATIONS["gojo_office"]["indoor"], "office backgrounds, indoor")
        check((LOCATIONS["utahime_office"]["x"], LOCATIONS["utahime_office"]["y"]) == (1480, 560)
              and (LOCATIONS["gojo_office"]["x"], LOCATIONS["gojo_office"]["y"]) == (1640, 560), "office x/y")
        check(LOCATIONS["utahime_office"]["desc"] == "Neat, traditional, and a mission board already fuller than Yaga's ever was."
              and LOCATIONS["gojo_office"]["desc"] == "Sweets on every surface and a television the size of a door.", "office descriptions")
        check(LOCATIONS["ridge"]["desc"] == "Above the treeline, as far as the rope markers. Higher up, the veil.", "ridge description")
        check([a["key"] for a in AREAS] == ["heart", "school", "dorms", "staff", "grounds", "mountain"], "AREAS order")
        check([a["seal"] for a in AREAS] == ["門", "校", "寮", "職", "練", "山"], "AREAS seals")
        check([a["anchor"] for a in AREAS] == [(960, 900), (420, 740), (900, 560), (1560, 440), (1560, 760), (740, 290)], "AREAS anchors")
        check(places_in("staff") == ["office", "utahime_office", "gojo_office"] and places_in("dorms") == ["dorm", "dorm_common", "girls_dorm", "rooftop"],
              "places_in", (places_in("staff"), places_in("dorms")))
        check(area_of("gate") == "heart" and area_of("ridge") == "mountain" and area_of("gojo_office") == "staff" and area_of("zz") is None, "area_of")
        _counts = {l: sum(1 for a in AREAS if l in a["places"]) for l in LOCATIONS}
        check(all(n == 1 for n in _counts.values()), "every place is in exactly one area", _counts)
        check(_validate_world() == [], "the WP1 validator finds nothing", _validate_world())

    ## --- 2. regression: the original nine keep their routine --------------------------
    python:
        _nine = ["yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "yaga", "gojo"]
        _bad = []
        for _roster in (list(roster), _nine + ["ijichi"]):
            roster = list(_roster)
            schedule_overrides = {}
            for _d in range(1, 15):
                day = _d
                roll_gojo()
                for _p in PERIODS:
                    for _w in _nine:
                        _new = char_location(_w, _p)
                        _old = zz_old_location(_w, _p, _d, roster)
                        if _new != _old:
                            _bad.append((_d, _p, _w, _new, _old))
        check(not has_flag("intensive_done") and not _bad,
              "regression: days 1-14 x 5 periods, the original 9 match the pre-phase-1 schedule and Gojo's roll",
              _bad[:6])
        roster = _nine + ["ijichi"]

    ## --- 3. the offices lock correctly -----------------------------------------------------
    python:
        day = 1
        flags.discard("utahime_arrived")
        flags.discard("intensive_done")
        _res = []
        for _p in PERIODS:
            period = _p
            _res.append(can_enter("utahime_office")[0])
        check(_res == [False] * 5, "Utahime's office locked before utahime_arrived", _res)
        flag("utahime_arrived")
        _res = []
        for _p in PERIODS:
            period = _p
            _res.append(can_enter("utahime_office"))
        check([r[0] for r in _res] == [True, True, True, True, False], "Utahime's office open after she arrives, locked at Night", _res)
        check(_res[-1][1] == "Her door is shut. There's light under it.", "Utahime's Night line", _res[-1][1])
        _res = []
        for _p in PERIODS:
            period = _p
            _res.append(can_enter("gojo_office"))
        check([r[0] for r in _res] == [False] * 5, "Gojo's office locked before intensive_done", _res)
        check(_res[0][1] == "Locked. A note on the door says SOON! and has a drawing of him on it.", "Gojo's SOON! note", _res[0][1])
        flag("intensive_done")
        _res = []
        for _p in PERIODS:
            period = _p
            _res.append(can_enter("gojo_office")[0])
        check(_res == [True, True, True, True, False], "Gojo's office open after intensive_done, locked at Night", _res)
        flags.discard("intensive_done")
        flags.discard("utahime_arrived")
        explore_mode = True
        check(can_enter("gojo_office")[0] and can_enter("utahime_office")[0], "explore mode opens every door")
        explore_mode = False
        period = "Night"
        check(can_enter("office") == (False, "Yaga's office is dark and locked."), "the old rules stand: office at Night")
        period = "Morning"
        check(not can_enter("storehouse")[0] and can_enter("storehouse")[1].startswith("The storehouse is sealed."), "the old rules stand: storehouse sealed")

    ## --- 4. Utahime once recruited ----------------------------------------------------------
    python:
        check(char_location("utahime", "Morning") is None, "Utahime is nowhere before she's recruited")
        recruit("utahime")
        flag("utahime_arrived")
        day = 1   # a Monday
        check(char_location("utahime", "Morning") == "utahime_office", "recruited Utahime is in her office on a weekday morning",
              char_location("utahime", "Morning"))
        check([char_location("utahime", p) for p in PERIODS] == ["utahime_office"] * 3 + ["cafeteria", None],
              "Utahime's weekday", [char_location("utahime", p) for p in PERIODS])
        day = 6   # a Saturday
        check([char_location("utahime", p) for p in PERIODS] == ["utahime_office", "utahime_office", None, "courtyard", None],
              "Utahime's weekend", [char_location("utahime", p) for p in PERIODS])
        day = 1
        check([char_location("ijichi", p) for p in PERIODS] == ["gate"] * 3 + [None, None], "Ijichi at the gate, mornings to afternoons")
        day = 7
        check([char_location("ijichi", p) for p in PERIODS] == ["gate"] * 3 + [None, None], "Ijichi keeps his hours on weekends")
        day = 1

    ## --- 5. the helpers ------------------------------------------------------------------------
    python:
        check(when_at("yaga", "office") == "weekday mornings, noon and evenings", "when_at yaga office", when_at("yaga", "office"))
        check(when_at("ijichi", "gate") == "mornings to afternoons", "when_at ijichi gate", when_at("ijichi", "gate"))
        check(when_at("maki", "dojo") == "weekday mornings and noon; weekend mornings, noon and evenings", "when_at maki dojo", when_at("maki", "dojo"))
        check(when_at("yuji", "ridge") == "", "when_at: never there is empty")
        check(when_at("gojo", "gojo_office") == "on the days he's in, mornings to afternoons", "when_at gojo office", when_at("gojo", "gojo_office"))
        _had = has_flag("intensive_done")
        flags.discard("intensive_done")
        check(usual_places("gojo") == "Nowhere I can predict.", "usual_places gojo before his first lesson", usual_places("gojo"))
        flag("intensive_done")
        check(usual_places("gojo") == "Nowhere I can predict. His office on the days he's in.", "usual_places gojo after it", usual_places("gojo"))
        if not _had:
            flags.discard("intensive_done")
        check(usual_places("maki") == "Dojo (mornings and noon) · Training Hall (afternoons) · Riverside (evenings) · Girls' Dormitory (nights)",
              "usual_places maki", usual_places("maki"))
        check(usual_places("utahime").startswith("Utahime's Office (mornings to afternoons)"), "usual_places utahime", usual_places("utahime"))
        check(usual_places("shoko") == "Infirmary (mornings to afternoons and nights) · Rooftop (evenings)", "usual_places shoko", usual_places("shoko"))
        check(periods_phrase(["Morning", "Noon", "Afternoon", "Evening", "Night"]) == "all day" and periods_phrase([]) == "", "periods_phrase ends")
        note("usual_places", " | ".join("%s: %s" % (w, usual_places(w)) for w in ROSTER_ORDER))

    ## --- 6. flag schedules (D13) --------------------------------------------------------------
    python:
        day = 1
        check(FLAG_SCHEDULES == [], "FLAG_SCHEDULES ships empty")
        FLAG_SCHEDULES.append(("zz_moved", "yuji", {"Morning": "ridge", "Noon": "ridge"}))
        check(char_location("yuji", "Morning") == "training", "flag schedule inactive without its flag")
        flag("zz_moved")
        check([char_location("yuji", p) for p in PERIODS] == ["ridge", "ridge", None, None, None],
              "a FLAG_SCHEDULES test entry moves a character", [char_location("yuji", p) for p in PERIODS])
        check(usual_places("yuji") == "Mountain Ridge (mornings and noon)", "usual_places follows the flag schedule", usual_places("yuji"))
        day = 6
        check(char_location("yuji", "Morning") == "ridge", "a flag schedule replaces the weekend too")
        pin("yuji", "cafeteria", 6, "Morning")
        check(char_location("yuji", "Morning") == "cafeteria", "a story pin still wins over a flag schedule")
        schedule_overrides = {}
        FLAG_SCHEDULES.append(("zz_gone", "yuji", None))
        flag("zz_gone")
        check([char_location("yuji", p) for p in PERIODS] == [None] * 5, "a None flag schedule takes someone off campus")
        del FLAG_SCHEDULES[:]
        flags.discard("zz_moved")
        flags.discard("zz_gone")
        day = 1
        check(char_location("yuji", "Morning") == "training", "back to normal without the entries")

    ## --- 7. Gojo's in-days -----------------------------------------------------------------------
    python:
        settle(day=1, period="Morning", here="courtyard")
        flag("intensive_done")
        del ZZ_GOJO_LOG[:]
        del ZZ_TOASTS[:]
        for _i in range(60):
            new_day()
        _in = [d for d, g, m, loc, hp in ZZ_GOJO_LOG if g]
        check(7 <= len(_in) <= 14, "with intensive_done, Gojo is in 7-14 times in 60 days", _in)
        check(not any(b - a == 1 for a, b in zip(_in, _in[1:])), "never on consecutive days", _in)
        check(all(m == "gojo_office" and loc == "gojo_office" for d, g, m, loc, hp in ZZ_GOJO_LOG if g),
              "on an in-day he's in his office in the morning")
        check(gojo_in_today() == gojo_in, "gojo_in_today() reports gojo_in")
        _gt = [t for t in ZZ_TOASTS if t[0] == "Gojo is in today."]
        check(len(_gt) == len(_in) and all(t[1] == "info" for t in _gt), "new_day() toasts 'Gojo is in today.' (info) on each in-day",
              (len(_gt), len(_in)))
        note("in-days", _in)
        _chain = [d for d in range(1, 400) if gojo_in_on(d)]
        _gaps = [b - a for a, b in zip([0] + _chain, _chain)]
        check(max(_gaps) <= GOJO_MAX_GAP + 1 and min(_gaps) >= 2, "over 400 days: never two running, never more than 8 days without",
              (min(_gaps), max(_gaps)))
        note("in-day rate over 400 days", "%.3f" % (len(_chain) / 399.0))
        flags.discard("intensive_done")
        del ZZ_GOJO_LOG[:]
        for _i in range(60):
            new_day()
        check(sum(1 for d, g, m, loc, hp in ZZ_GOJO_LOG if g) == 0, "without intensive_done: 0 in-days in 60")
        check(all(m != "gojo_office" for d, g, m, loc, hp in ZZ_GOJO_LOG), "without it, Gojo never keeps office hours")

    ## --- 8. the clock: vitals and HP at dawn --------------------------------------------------------
    python:
        hp = 1
        output = 30
        control = 30
        new_day()
        check(hp == hp_max and hp_max == 50 + output + control // 3, "new_day() restores hp (after refresh_vitals)", (hp, hp_max))
        check(all(h for d, g, m, l, h in ZZ_GOJO_LOG), "hp is full when the new-day hooks run")
        check(actions_today == set() and period == "Morning", "new_day() still resets the day")

    ## --- 9. migration 15 -----------------------------------------------------------------------------
    python:
        gojo_today = {"Morning": "-"}
        here = "zz_torn_down"
        _migrate_15()
        check(set(gojo_today) == set(PERIODS), "migration 15 re-rolls a partial Gojo day", gojo_today)
        check(here == "courtyard", "migration 15 moves a settled save out of a missing place", here)
        _gt0 = dict(gojo_today)
        _migrate_15()
        check(gojo_today == _gt0 and here == "courtyard", "migration 15 is idempotent")
        check(any(o == 15 for o, n, f in MIGRATIONS), "migration 15 registered")

        ## The whole ordered list, twice, on a legacy save.
        fixture(save_version=0, flags={"settled_in", "roll_call"}, gojo_today={"Morning": "-"},
                here="zz_old_gone_place", day=5, period="Noon")
        gojo_in = False
        _up = run_migrations()
        _snap = lambda: (day, period, here, dict(gojo_today), gojo_in, set(districts_visited), set(flags))
        _s1 = _snap()
        check(_up and here == "courtyard" and set(gojo_today) == set(PERIODS),
              "run_migrations() on a legacy save: migration 15 re-rolls Gojo and moves me", _s1)
        run_migrations()
        check(_snap() == _s1, "run_migrations() twice: the second pass changes nothing", (_s1, _snap()))
        gojo_today = None
        run_migrations()
        check(isinstance(gojo_today, dict) and set(gojo_today) == set(PERIODS), "migration 15 re-rolls gojo_today=None", gojo_today)
        flags.discard("settled_in")
        here = None
        gojo_today = {p: "-" for p in PERIODS}
        run_migrations()
        check(here is None, "an unsettled save with here=None keeps None", here)
        flag("settled_in")
        here = "courtyard"

    ## --- 10. the ridge veil (D15) ----------------------------------------------------------------------
    python:
        settle(day=3, period="Afternoon", here="ridge")
        flags.discard("saw_the_ridge_veil")
        check(not veil_ok() and "veil" not in [a[0] for a in registered_place_actions("ridge")], "no veil action before the tour shows it")
        flag("saw_the_ridge_veil")
        check(veil_ok() and ("veil", "Look up at the veil", "Free. Once a day.", 0) in registered_place_actions("ridge"),
              "the veil action at the ridge", registered_place_actions("ridge"))
        check("veil" not in [a[0] for a in registered_place_actions("courtyard")], "the veil action is only at the ridge")

    python:
        _vn = veil_bg("Night")
        check(getattr(_vn, "_light_key", None) == ("ridge", "Night"), "the veil picture is graded for Night, lit as the ridge", _vn)
        check(getattr(veil_bg("Evening"), "_light_key", None) == ("ridge", "Evening"), "the veil picture is graded for the Evening")
        for _f in ("asked_dead", "asked_why_here", "watched_the_box"):
            flags.discard(_f)
        flag("asked_why_here")

    $ autoplay()
    $ _vp = (day, period)
    $ del ZZ_SAID[:]
    call sb_do_veil
    $ check(has_flag("looked_at_veil_1") and not has_flag("looked_at_veil_2"), "first look: passage 1")
    $ check(zz_said("The grass inside it doesn't move"), "passage 1: the grass, not trees, inside the veil")
    $ check(zz_said("it's still there in the middle of it", "exactly where Gojo showed me") and not zz_said("there is a shape"),
            "passage 1 remembers the figure from the tour")
    $ check((day, period) == _vp and not veil_ok(), "the veil costs no time, and once a day", (day, period))
    $ actions_today.discard("veil")
    $ del ZZ_SAID[:]
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(has_flag("looked_at_veil_2") and not has_flag("looked_at_veil_3"), "second look: passage 2")
    $ check(zz_said("Somebody at this school is holding it up") and not zz_said("Nine people"),
            "passage 2 without asked_dead doesn't quote Gojo", [t for t in ZZ_SAID][:4])
    $ check(zz_said("Today the light is flat"), "passage 2 in daylight")
    $ del ZZ_SAID[:]
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(has_flag("looked_at_veil_3"), "third look: passage 3")
    $ check(zz_said("Something is different") and zz_said("It's facing the school."),
            "passage 3, first time (not watched_the_box): the discovery, ending 'It's facing the school.'")
    $ day = 5          # (5 % 3) + 1 == 3: the rotation lands on passage 3 again
    $ del ZZ_SAID[:]
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check((day, period) == (5, _vp[1]), "a fourth look rotates, still free")
    $ check(zz_said("I keep telling myself") and not zz_said("Something is different") and zz_said("It's facing the school."),
            "passage 3 again: no second discovery, still ends 'It's facing the school.'")

    ## The other tour choices, and Night.
    python:
        for _f in ("looked_at_veil_1", "looked_at_veil_2", "looked_at_veil_3", "asked_why_here"):
            flags.discard(_f)
        flag("watched_the_box")
        flag("looked_at_veil_1")
        flag("looked_at_veil_2")
        del ZZ_SAID[:]
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(zz_said("I keep telling myself") and not zz_said("Something is different"),
            "watched_the_box: passage 3 is something I already know")
    python:
        flags.discard("looked_at_veil_2")
        flags.discard("watched_the_box")
        flag("asked_dead")
        period = "Night"
        del ZZ_SAID[:]
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(zz_said("Nine people take turns holding it up, Gojo said."), "asked_dead: passage 2 quotes Gojo")
    $ check(zz_said("After dark it is almost nothing") and not zz_said("Today the light is flat"), "passage 2 at Night")
    $ autoplay(False)
    python:
        renpy.scene()
        renpy.show("ridge_veil_night", what=veil_bg("Night"))
        shot("veil_night")
        renpy.scene()
        renpy.show("ridge_veil_noon", what=veil_bg("Noon"))
        shot("veil_noon")
        renpy.scene()
        flags.discard("asked_dead")
        period = "Afternoon"

    ## --- 11. Tokyo: the districts ------------------------------------------------------------------------
    python:
        settle(day=1, period="Morning", here="courtyard")
        flags.discard("ijichi_rides")
        flags.discard("kawasaki_open")
        check(DISTRICT_ORDER == ["shibuya", "harajuku", "shinjuku", "kawasaki", "yotsuka"], "DISTRICT_ORDER")
        check(all(set(DISTRICTS[k]) >= {"name", "kanji", "desc", "places", "bg", "min_grade", "needs_flag", "locked_hint", "lines"}
                  for k in DISTRICT_ORDER), "every district has every field")
        check(all(2 <= len(DISTRICTS[k]["lines"]) <= 3 for k in DISTRICT_ORDER), "2-3 arrival lines each")
        check([DISTRICTS[k]["kanji"] for k in DISTRICT_ORDER] == ["渋谷", "原宿", "新宿", "川崎", "四塚"], "district kanji")
        check(not tokyo_open(), "Tokyo closed without ijichi_rides")
        check(all(district_state(k) == (False, "After Ijichi's ride-along") for k in DISTRICT_ORDER),
              "every district is locked without ijichi_rides", [district_state(k) for k in DISTRICT_ORDER])
        flag("ijichi_rides")
        grade = "g4"
        check(tokyo_open(), "Tokyo opens with ijichi_rides")
        check(all(district_state(k)[0] for k in ("shibuya", "harajuku", "yotsuka")), "Shibuya, Harajuku and Yotsuka open with it")
        check(district_state("shinjuku") == (False, "Grade 2"), "Shinjuku locked below Grade 2 (g4)", district_state("shinjuku"))
        grade = "g3"
        check(district_state("shinjuku") == (False, "Grade 2"), "Shinjuku locked at Grade 3")
        grade = None
        check(district_state("shinjuku") == (False, "Grade 2"), "Shinjuku locked while unassessed")
        grade = "g2"
        check(district_state("shinjuku") == (True, ""), "Shinjuku open at Grade 2")
        grade = "g4"
        check(district_state("kawasaki") == (False, "Act III"), "Kawasaki locked without kawasaki_open")
        flag("kawasaki_open")
        check(district_state("kawasaki") == (True, ""), "Kawasaki open with kawasaki_open")
        flags.discard("kawasaki_open")
        check(district_state("zz") == (False, "Later"), "an unknown district is closed")

    ## --- 12. Tokyo: the car -------------------------------------------------------------------------------
    python:
        here = "courtyard"
        period = "Morning"
        check(trip_ok_now() and not car_action_ok(), "trip_ok_now at the courtyard; the car action needs the gate")
        here = "gate"
        check(car_action_ok() and ("car", "Ask Ijichi for a ride", "Into the city. Half a day.", 2) in registered_place_actions("gate"),
              "the car action at the gate", registered_place_actions("gate"))
        period = "Evening"
        check(not trip_ok_now() and not car_action_ok(), "no trips in the Evening")
        period = "Morning"
        roster = [w for w in roster if w != "ijichi"]
        check(not trip_ok_now(), "no trips while Ijichi isn't on campus")
        roster.append("ijichi")
        flags.discard("ijichi_rides")
        check(not car_action_ok(), "no car action before ijichi_rides")
        flag("ijichi_rides")

    ## sb_trip under autoplay, from the Morning.
    $ day = 2
    $ period = "Morning"
    $ here = "courtyard"
    $ districts_visited = set()
    $ autoplay()
    call sb_trip("shibuya")
    $ autoplay(False)
    $ check((day, period, here) == (2, "Afternoon", "gate"), "sb_trip started in the Morning under autoplay ends in the Afternoon, at the gate", (day, period, here))
    $ check(districts_visited == {"shibuya"}, "the trip is recorded in districts_visited", districts_visited)
    $ check(zz_said("I walk down to the gate.") and zz_said("Seatbelt, please."), "a trip from the courtyard walks to the gate; the first trip's Ijichi line")
    $ check(not hasattr(store, "_trip"), "the trip keeps no district dict in the store")

    ## The "Go." / "Not today." menu, picked at random (not the autoplay shortcut).
    python:
        _outs = []
    $ _zz_i = 0
    while _zz_i < 12:
        python:
            day = 10 + _zz_i
            period = "Morning"
            here = "courtyard"
            districts_visited = {"shibuya"}
            del ZZ_SAID[:]
            autoplay()
            smoke_autoplay = False
        call sb_trip("harajuku")
        python:
            autoplay(False)
            _outs.append((period, here, "harajuku" in districts_visited, zz_said("Half a day in "),
                          zz_said("Seatbelt, please.")))
            _zz_i += 1
    python:
        _gone = [o for o in _outs if o[:3] == ("Afternoon", "gate", True)]
        _stay = [o for o in _outs if o[:3] == ("Morning", "courtyard", False)]
        check(len(_gone) + len(_stay) == len(_outs) and all(o[3] for o in _outs),
              "the trip menu: every outcome is 'Go.' (Afternoon, gate, visited) or 'Not today.' (unchanged)", _outs)
        check(_gone and _stay, "the trip menu: both choices came up in 12 tries", (len(_gone), len(_stay)))
        check(not any(o[4] for o in _gone), "later trips play a different Ijichi line")

    ## A companion stays behind at the gate (the car has one spare seat).
    python:
        day = 4
        period = "Morning"
        here = "courtyard"
        districts_visited = {"shibuya"}
        companion = "yuji"
        del ZZ_SAID[:]
        autoplay()
    call sb_trip("harajuku")
    $ autoplay(False)
    $ check(companion is None and zz_said("waves me off at the gate") and "yuji" not in who_is_here("gate"),
            "a trip leaves the companion behind", (companion, who_is_here("gate")))

    ## Two trips on one day play different Ijichi lines.
    python:
        _zz_lines = []
        _IJ = ("Back at the gate by the usual time", "Please don't tell Gojo-san", "walk away from it first")
        day = 4
        period = "Morning"
        here = "gate"
        districts_visited = {"shibuya"}
        del ZZ_SAID[:]
        autoplay()
    call sb_trip("harajuku")
    python:
        _zz_lines.append([b for b in _IJ if zz_said(b)])
        del ZZ_SAID[:]
    call sb_trip("yotsuka")
    python:
        autoplay(False)
        _zz_lines.append([b for b in _IJ if zz_said(b)])
        check(period == "Night" and len(_zz_lines[0]) == 1 and len(_zz_lines[1]) == 1 and _zz_lines[0] != _zz_lines[1],
              "two trips on one day (Morning, then Afternoon) play different Ijichi lines", (period, _zz_lines))
        companion = None

    ## A trip that can't start does nothing.
    $ districts_visited = {"shibuya"}
    $ here = "gate"
    $ period = "Evening"
    call sb_trip("harajuku")
    $ check(period == "Evening" and "harajuku" not in districts_visited, "no trip in the Evening")
    $ period = "Morning"
    $ grade = "g4"
    call sb_trip("shinjuku")
    $ check(period == "Morning" and "shinjuku" not in districts_visited, "no trip to a locked district")

    ## The car action: pressing the Yotsuka card on the Tokyo map starts the trip.
    $ day = 3
    $ period = "Noon"
    $ here = "gate"
    $ grade = "g4"
    $ autoplay()
    show screen zz_press("district_yotsuka")
    call sb_do_car
    $ autoplay(False)
    $ check((day, period, here) == (3, "Evening", "gate") and "yotsuka" in districts_visited,
            "the car: pressing a district card -> half a day (Noon -> Evening)", (day, period, here, districts_visited))

    ## sb_do_car's other returns (the Campus tab's walk, cancel), fed by a
    ## timer: these test sb_do_car's handling, not the map's buttons.
    $ period = "Morning"
    $ here = "gate"
    show screen zz_ret(("go", "courtyard"))
    call sb_do_car
    $ check((period, here) == ("Morning", "courtyard"), "sb_do_car: a returned ('go', place) walks there for free", (period, here))
    $ here = "gate"
    show screen zz_ret(("cancel",))
    call sb_do_car
    $ check((period, here) == ("Morning", "gate"), "sb_do_car: a returned cancel stays put")

    ## The map's real buttons, pressed inside the protected-style call.
    $ here = "gate"
    $ period = "Morning"
    $ flags.discard("storehouse_access")
    show screen zz_press("row_cafeteria")
    call screen sb_map
    $ check(_return == ("go", "cafeteria"), "sb_map: pressing an open row returns ('go', place) to the call", _return)
    show screen zz_press("row_storehouse")
    call screen sb_map
    $ _a, _t = zz_pressed("row_storehouse")
    $ check(_return == ("zz_nothing", "row_storehouse") and _a.__class__.__name__ == "NullAction",
            "sb_map: a locked row's action is NullAction", (_return, _a))
    $ check(_t == can_enter("storehouse")[1], "sb_map: a locked row's tooltip is can_enter's reason", _t)
    show screen zz_press("row_gate")
    call screen sb_map
    $ _a, _t = zz_pressed("row_gate")
    $ check(_a.__class__.__name__ == "NullAction", "sb_map: my own row does nothing", _a)
    show screen zz_press("district_harajuku")
    call screen sb_map(layer="tokyo")
    $ check(_return == ("district", "harajuku"), "sb_map(layer='tokyo'): pressing an open district returns ('district', key)", _return)
    show screen zz_press("district_shinjuku")
    call screen sb_map(layer="tokyo")
    $ _a, _t = zz_pressed("district_shinjuku")
    $ check(_a.__class__.__name__ == "NullAction", "sb_map(layer='tokyo'): a locked district (Shinjuku at g4) does nothing", _a)
    $ period = "Evening"
    show screen zz_press("district_harajuku")
    call screen sb_map(layer="tokyo")
    $ _a, _t = zz_pressed("district_harajuku")
    $ check(_a.__class__.__name__ == "NullAction" and _t == "Ijichi drives from the gate, mornings to afternoons.",
            "sb_map(layer='tokyo'): an open district in the Evening does nothing and says when he drives", (_a, _t))
    $ period = "Morning"
    $ pin("ijichi", "office")
    show screen zz_press("district_harajuku")
    call screen sb_map(layer="tokyo")
    $ _a, _t = zz_pressed("district_harajuku")
    $ check(_a.__class__.__name__ == "NullAction" and _t == "Ijichi isn't at the gate right now.",
            "sb_map(layer='tokyo'): in the morning with Ijichi elsewhere, a district says he isn't at the gate", (_a, _t))
    $ schedule_overrides.pop(("ijichi", day, "Morning"), None)
    python:
        check(not any(("Junpei" in DISTRICTS[k]["places"]) or ("(later)" in DISTRICTS[k]["places"]) or ("at night" in DISTRICTS[k]["places"])
                      for k in DISTRICT_ORDER), "the districts' places lines name nothing the player can't know or do yet",
              [DISTRICTS[k]["places"] for k in DISTRICT_ORDER])

    ## --- 13. screenshots: the map ------------------------------------------------------------------------------
    ## Day 1, the way a new game sees it: six areas, who is where, Tokyo locked.
    python:
        settle(day=1, period="Morning", here="dorm")
        roster = ["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "ijichi"]
        for _f in ("ijichi_rides", "utahime_arrived", "intensive_done", "storehouse_access"):
            flags.discard(_f)
        roll_gojo()
        _L = [a["key"] for a in AREAS]
        renpy.scene()
        renpy.show_screen("sb_map")
        zz_shot("map_campus_day1")
        _s = renpy.get_screen("sb_map")
        check(_s is not None, "the campus map renders (day 1)")
        check(not tokyo_open(), "day 1: the Tokyo tab is locked")
        check(map_place_name("utahime_office") == "Empty Office" and LOCATIONS["utahime_office"]["name"] == "Utahime's Office",
              "before she arrives, the map calls Utahime's office 'Empty Office'")
        renpy.hide_screen("sb_map")

    ## A busier campus: everyone recruited, Utahime in, Gojo in, markers, noon.
    python:
        settle(day=9, period="Noon", here="office")
        roster = list(ROSTER_ORDER)
        for _f in ("utahime_arrived", "intensive_done", "storehouse_access", "ijichi_rides"):
            flag(_f)
        gojo_in = True
        roll_gojo()
        gojo_in = True
        _mm, _mh, _mw = mission_markers, missions_here, missions_with
        mission_markers, missions_here, missions_with = zz_fake_markers, zz_fake_missions_here, zz_fake_missions_with
        renpy.show_screen("sb_map")
        zz_shot("map_campus_busy")
        check(renpy.get_screen("sb_map") is not None, "the campus map renders (busy, with markers)")
        renpy.hide_screen("sb_map")
        check(map_place_name("utahime_office") == "Utahime's Office", "after she arrives, the map names her office")
        ## A weekday Evening: the common room is the busiest row.
        mission_markers = zz_no_markers
        period = "Evening"
        here = "courtyard"
        _rows = dict((l, (h, b)) for a, x, y, rs in map_cards({}) for l, h, b in rs)
        check(_rows["dorm_common"] == (MAP_ROW_H_MARKED, True), "a crowded row puts its people on a second line", _rows["dorm_common"])
        _sh, _mo = map_people("dorm_common", MAP_ROW_W - 28, cap=6)
        check(len(_sh) >= 3, "the crowded row shows at least three names", (_sh, _mo, who_is_here("dorm_common")))
        renpy.show_screen("sb_map")
        zz_shot("map_campus_evening")
        renpy.hide_screen("sb_map")
        mission_markers = zz_fake_markers
        period = "Night"
        here = "dorm"
        renpy.show_screen("sb_map")
        zz_shot("map_campus_night")
        renpy.hide_screen("sb_map")
        mission_markers, missions_here, missions_with = _mm, _mh, _mw

    ## Tokyo: open, a trip possible now, one district visited, Shinjuku and Kawasaki locked.
    python:
        period = "Morning"
        here = "gate"
        grade = "g4"
        districts_visited = {"shibuya"}
        renpy.show_screen("sb_map", layer="tokyo")
        zz_shot("map_tokyo")
        check(renpy.get_screen("sb_map") is not None, "the Tokyo map renders")
        renpy.hide_screen("sb_map")
        period = "Evening"
        renpy.show_screen("sb_map", layer="tokyo")
        zz_shot("map_tokyo_evening")
        renpy.hide_screen("sb_map")
        flags.discard("ijichi_rides")
        period = "Morning"
        renpy.show_screen("sb_map", layer="tokyo")
        zz_shot("map_tokyo_closed")
        renpy.hide_screen("sb_map")

    ## --- 14. screenshots: the placeholder backgrounds as they are lit -------------------------------------
    python:
        for _n in ("bg alley", "bg alley dark", "bg ridge_veil", "bg map_tokyo",
                   "bg shibuya", "bg harajuku", "bg shinjuku", "bg kawasaki", "bg yotsuka"):
            renpy.scene()
            renpy.show(_n)
            shot("bg_" + _n[3:].replace(" ", "_"))
        for _loc in ("utahime_office", "gojo_office"):
            for _p in ("Morning", "Evening"):
                here = _loc
                period = _p
                renpy.scene()
                config.show("graded", what=graded_bg(_loc, _p))     # as `scene expression graded_bg()` does
                renpy.show("utahime neutral" if _loc == "utahime_office" else "gojo happy", at_list=[pos_c])
                shot("office_%s_%s" % (_loc, _p.lower()))
                check(scene_light == light_for_place(_loc, _p), "%s lit by PLACE_LIGHT (%s)" % (_loc, _p), scene_light)
        renpy.scene()

    python:
        TOAST_SINK[0] = _sink0
        finish()
