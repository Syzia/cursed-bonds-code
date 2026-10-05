## tools/smoke/core_flow.rpy -- the core-flow harness every package must pass
## (PHASE1_DESIGN.md, section 7, standard acceptance (d)).
##
##   tools/smoke.sh tools/smoke/core_flow.rpy
##
## A post-prologue fixture (names set, the prologue's flags), then
## arc_one_open, then one stretch of the campus loop driven through the loop's
## own functions and dispatch statements:
##   - three sb_do_* place actions, each taken from place_actions(here);
##   - new_day(), then pick_event("story") and play_event;
##   - two more new_day() (three in all);
##   - sb_place, sb_char("yuji") and sb_map rendered once each.
## It must finish with no exception. It doesn't play the prologue: its name
## input blocks a harness until WP9 adds the smoke_autoplay guard, and WP9's
## own harness covers it.

init 999 python:

    ZZ_CF_DAYS = []

    register_new_day(lambda: ZZ_CF_DAYS.append(store.day), order=99)

    ## The flags a player has by the end of chapter two, one per choice.
    ZZ_CF_PROLOGUE_FLAGS = (
        "dinner_listened", "listened_first", "gojo_asked_why", "chose_jujutsu",
        "told_parents_truth", "took_photo", "enrolled", "yaga_honest",
        "first_day_asking",
    )

    def zz_cf_pick_action(prefer):
        """The first id in `prefer` that place_actions(here) offers."""
        ids = [a[0] for a in place_actions(store.here)]
        for p in prefer:
            if p in ids and renpy.has_label("sb_do_" + p):
                return p
        return None


label zz_smoke:

    ## --- the fixture: the end of the prologue ------------------------------------
    python:
        fixture(mc_name="Tester", mc_surname="Harness")
        for _f in ZZ_CF_PROLOGUE_FLAGS:
            flag(_f)
        check(not has_flag("settled_in"), "fixture: not settled yet")

    ## --- arc_one_open, played through --------------------------------------------
    $ autoplay()
    call arc_one_open
    $ autoplay(False)
    python:
        check(has_flag("settled_in"), "arc_one_open settles in")
        check(day == 1 and period == "Morning", "arc_one_open starts day 1, Morning", (day, period))
        check(here in LOCATIONS, "arc_one_open puts me somewhere real", here)
        check(set(gojo_today) >= set(PERIODS), "Gojo's day is rolled", gojo_today)
        ensure_state()
        check(save_version == SAVE_VERSION, "ensure_state brings a new game up to date", save_version)
        ## After checkpoint D (5 Oct 2026): the build folder is version 0.4,
        ## like the game. Only the distribution's folder and archive name
        ## read build.version; saves keep their own folder.
        check(build.version == "0.4" and build.directory_name == "CursedBonds-0.4" and " " not in build.directory_name
              and config.version.startswith("0.4") and config.save_directory == "JJKgamemd-1788928056",
              "the build folder is version 0.4 (CursedBonds-0.4), the game says 0.4, and the save folder is as it was",
              (build.version, build.directory_name, config.version, config.save_directory))
    $ shot("after_arc_one_open")

    ## --- three place actions, through the loop's dispatch -------------------------
    ## (The loop runs `call expression "sb_do_" + _r[1]` for ("act", id).)
    $ autoplay()
    $ _stamina0 = stamina

    $ here = "courtyard"
    $ _id = zz_cf_pick_action(("train", "study", "think", "wait"))
    $ check(_id is not None, "an action at the courtyard", place_actions(here))
    $ _p0 = period
    $ _r = ("act", _id)
    call expression "sb_do_" + _r[1]
    $ check(True, "sb_do_%s ran" % _id)

    $ here = "cafeteria"
    $ _id = zz_cf_pick_action(("eat", "wait"))
    $ check(_id is not None, "an action at the cafeteria", place_actions(here))
    $ _r = ("act", _id)
    call expression "sb_do_" + _r[1]
    $ check(True, "sb_do_%s ran" % _id)

    $ here = "dorm"
    $ _id = zz_cf_pick_action(("study", "wait"))
    $ check(_id is not None, "an action in the dorm", place_actions(here))
    $ _r = ("act", _id)
    call expression "sb_do_" + _r[1]
    $ check(True, "sb_do_%s ran" % _id)
    $ autoplay(False)

    python:
        check(day == 1, "still day 1 after the actions", day)
        check(PERIODS.index(period) > PERIODS.index(_p0), "the actions moved the clock", (_p0, period))
        note("after actions", "day %d %s, stamina %d -> %d" % (day, period, _stamina0, stamina))

    ## --- new day 1, then the story -----------------------------------------------------
    python:
        new_day()
        check(day == 2 and period == PERIODS[0], "new_day() 1 -> day 2, first period", (day, period))
        check(actions_today == set() and stamina == stamina_max, "new_day() resets the day", (actions_today, stamina))
        here = "courtyard"
        _story = None
        for _per in PERIODS:
            period = _per
            _story = pick_event("story")
            if _story:
                break
        check(_story is not None, "pick_event(\"story\") finds a story beat on day 2")
        if _story:
            note("story", "%s at %s" % (_story["label"], period))

    if _story:
        $ autoplay()
        call play_event(_story)
        $ autoplay(False)
        python:
            check(_story["label"] in done_events, "play_event marks %s done" % _story["label"], sorted(done_events))
            check(pick_event("story") is None or pick_event("story")["label"] != _story["label"],
                  "the same beat doesn't fire twice")

    ## --- two more days ------------------------------------------------------------------
    python:
        new_day()
        new_day()
        check(day == 4, "new_day() x3 -> day 4", day)
        check(ZZ_CF_DAYS == [2, 3, 4], "new-day hooks ran once per day", ZZ_CF_DAYS)
        check(set(gojo_today) >= set(PERIODS), "Gojo's day is rolled each morning")

    ## --- the three loop screens, once each ---------------------------------------------------
    scene expression graded_bg()
    python:
        here = "cafeteria"
        period = "Noon"
        for _s, _a in (("sb_place", ()), ("sb_char", ("yuji",)), ("sb_map", ())):
            renpy.show_screen(_s, *_a)
            shot("screen_" + _s)
            check(renpy.get_screen(_s) is not None, "rendered " + _s)
            renpy.hide_screen(_s)

    $ finish()
