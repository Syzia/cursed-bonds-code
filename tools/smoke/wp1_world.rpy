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

    def zz_fake_missions_here(loc):
        return ["m_sunmall"] if loc == "office" else []

    def zz_fake_missions_with(who, loc=None):
        return ["m_sunmall"] if who == "yaga" else []


## Returns a value from whatever interaction is running (a called screen).
screen zz_ret(value, delay=0.4):
    zorder 200
    timer delay action [Hide("zz_ret"), Return(value)]


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
        check(usual_places("gojo") == "Nowhere you can predict. His office on the days he's in.", "usual_places gojo")
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

    ## --- 10. the ridge veil (D15) ----------------------------------------------------------------------
    python:
        settle(day=3, period="Afternoon", here="ridge")
        flags.discard("saw_the_ridge_veil")
        check(not veil_ok() and "veil" not in [a[0] for a in registered_place_actions("ridge")], "no veil action before the tour shows it")
        flag("saw_the_ridge_veil")
        check(veil_ok() and ("veil", "Look up at the veil", "Free. Once a day.", 0) in registered_place_actions("ridge"),
              "the veil action at the ridge", registered_place_actions("ridge"))
        check("veil" not in [a[0] for a in registered_place_actions("courtyard")], "the veil action is only at the ridge")

    $ autoplay()
    $ _vp = (day, period)
    call sb_do_veil
    $ check(has_flag("looked_at_veil_1") and not has_flag("looked_at_veil_2"), "first look: passage 1")
    $ check((day, period) == _vp and not veil_ok(), "the veil costs no time, and once a day", (day, period))
    $ actions_today.discard("veil")
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(has_flag("looked_at_veil_2") and not has_flag("looked_at_veil_3"), "second look: passage 2")
    call sb_do_veil
    $ actions_today.discard("veil")
    $ check(has_flag("looked_at_veil_3"), "third look: passage 3 (It's facing the school.)")
    call sb_do_veil
    $ check((day, period) == _vp, "a fourth look rotates, still free")
    $ autoplay(False)

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

    ## A trip that can't start does nothing.
    $ period = "Evening"
    call sb_trip("harajuku")
    $ check(period == "Evening" and "harajuku" not in districts_visited, "no trip in the Evening")
    $ period = "Morning"
    $ grade = "g4"
    call sb_trip("shinjuku")
    $ check(period == "Morning" and "shinjuku" not in districts_visited, "no trip to a locked district")

    ## The car action: the Tokyo map returns a district, then the trip plays.
    $ day = 3
    $ period = "Noon"
    $ here = "gate"
    $ autoplay()
    show screen zz_ret(("district", "yotsuka"))
    call sb_do_car
    $ autoplay(False)
    $ check((day, period, here) == (3, "Evening", "gate") and "yotsuka" in districts_visited,
            "the car: Tokyo map -> district -> half a day (Noon -> Evening)", (day, period, here, districts_visited))

    ## The car action: the Campus tab walks me somewhere instead.
    $ period = "Morning"
    $ here = "gate"
    show screen zz_ret(("go", "courtyard"))
    call sb_do_car
    $ check((period, here) == ("Morning", "courtyard"), "the car: a campus place walks there for free", (period, here))
    $ here = "gate"
    show screen zz_ret(("cancel",))
    call sb_do_car
    $ check((period, here) == ("Morning", "gate"), "the car: cancel stays put")

    ## sb_map returns what the loop expects, from both layers.
    $ here = "gate"
    $ period = "Morning"
    show screen zz_ret(("go", "cafeteria"))
    call screen sb_map
    $ check(_return == ("go", "cafeteria"), "sb_map returns to the protected call", _return)
    show screen zz_ret(("district", "harajuku"))
    call screen sb_map(layer="tokyo")
    $ check(_return == ("district", "harajuku"), "sb_map(layer='tokyo') returns a district", _return)

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
