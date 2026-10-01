## tools/smoke/wp11_dev.rpy -- WP11's harness: the review tools and explore mode
## (docs/PHASE1_DESIGN.md 4.13, D30, section 7 WP11 task 3).
##
##   tools/smoke.sh tools/smoke/wp11_dev.rpy
##
## A settled game (the prologue's flags, then arc_one_open played through),
## driven through the real `sandbox` loop by an overlay that answers its
## screens one step at a time, as wp7_ui does:
##
##   1. Explore mode, entered through `explore_campus` on a store where a story
##      step is available: no mission is offered anywhere, no story fires, and
##      the Time step, the map, a person, the journal and the review tools all
##      work. The panel's "Finish the next story step" plays nothing there.
##   2. The story buttons, from the place view's ("dev",): "Finish the next
##      story step" plays Roll Call (a step waiting for its day moves the day
##      forward first), "Recruit Utahime" plays her arrival, and "Finish the
##      next story step" plays the Sun Mall (a start-type mission, with its
##      fight). Each lands done, with its flags.
##   3. Every other panel button, run while the panel is up, with its effect
##      and its toast checked.
##   4. Arc Two: the journal's Missions tab offers "Begin Arc Two", and
##      arc_two_start shows the exact warning before it begins.
##   5. Outside a developer build, or before the campus opens, dev_tools
##      shows nothing.
##
## Scene phases run under autoplay. The panel closes itself under
## smoke_autoplay (so wp7_ui's loop drive is never left waiting on it), so this
## harness turns smoke_autoplay off as dev_tools starts and back on when a scene
## starts. Screenshots: panel_explore, panel, panel_after, journal_arc_two.

init 999 python:
    import os

    ZZ_LABELS = []          # labels entered, in order
    ZZ_TOASTS = []          # every toast's text, in order
    ZZ_SAID = []            # say and menu text (the Arc Two warning)
    ZZ_DRIVE = []           # what the driver answers the loop's screens with
    ZZ_DRIVE_LOG = []
    ZZ_PANEL_SEEN = []      # an interaction started with dev_panel up
    ZZ_ORIG = {}

    def zz_label_cb(name, abnormal):
        ZZ_LABELS.append(name)
        ## The panel closes itself under smoke_autoplay: keep it up while
        ## the driver answers it, and play scenes under autoplay.
        if name == "dev_tools":
            store.smoke_autoplay = False
        elif name in ("play_event", "start_mission"):
            store.smoke_autoplay = zz_smoke_state.autoplay

    config.label_callbacks.append(zz_label_cb)

    def zz_interact_cb():
        if renpy.get_screen("dev_panel"):
            ZZ_PANEL_SEEN.append(True)

    config.start_interact_callbacks.append(zz_interact_cb)

    def zz_say_filter(s):
        ZZ_SAID.append(s)
        return s

    config.say_menu_text_filters.append(zz_say_filter)

    def zz_sink(text, kind, who, amount):
        ZZ_TOASTS.append(text)
        if ZZ_ORIG.get("sink") is not None:
            ZZ_ORIG["sink"](text, kind, who, amount)

    def zz_menu(items):
        """Answers arc_two_start's menu: "Begin Arc Two"."""
        ZZ_SAID.append([l for l, v in items])
        for l, v in items:
            if l == "Begin Arc Two":
                return getattr(v, "value", v)
        return None

    def zz_texts(screen_name):
        """Every string drawn by a shown screen."""
        out = []
        seen = set()

        def walk(d, depth):
            if d is None or depth > 80 or id(d) in seen:
                return
            seen.add(id(d))
            if isinstance(d, renpy.text.text.Text):
                try:
                    out.append(d.get_all_text())
                except Exception:
                    out.append(" ".join(x for x in d.text if isinstance(x, str)))
            try:
                kids = d.visit() or []
            except Exception:
                kids = []
            for k in kids:
                walk(k, depth + 1)

        walk(renpy.get_screen(screen_name), 0)
        return out

    def zz_has_text(screen_name, s):
        return any(s in t for t in zz_texts(screen_name))

    ## The driver ----------------------------------------------------------------
    ##
    ## (screen, value): once `screen` is up, value is returned from the
    ## interaction, or, for a tuple naming a step:
    ##   ("finish", label)  jump to label (the loop is left)
    ##   ("shot", name)     a screenshot, then the next step
    ##   ("run", key)       run the panel button's action while it is up, and
    ##                      check its effect, then the next step
    ##   ("do", fn)         return fn() (None: nothing, the next step)

    ZZ_LOOP_SCREENS = ("sb_place", "sb_char", "sb_map", "journal", "dev_panel")

    def zz_drive():
        if not ZZ_DRIVE:
            return None
        want, value = ZZ_DRIVE[0]
        if not renpy.get_screen(want):
            return None
        ZZ_DRIVE.pop(0)
        step = value[0] if isinstance(value, tuple) and value else None
        ZZ_DRIVE_LOG.append((want, value if step != "do" else ("do", value[1].__name__)))
        if step == "finish":
            renpy.jump(value[1])
        if step == "shot":
            shot(value[1], wait=0)
            return None
        if step == "run":
            zz_run(value[1])
            return None
        if step == "do":
            return value[1]()
        return value

    config.overlay_screens.append("zz_driver")

    ## The panel buttons -----------------------------------------------------------

    def zz_snap():
        return dict(merit=store.merit, grade=store.grade, day=store.day,
                    npc={w: _npc_grade(w) for w in DEV_STUDENTS},
                    bonds=dict(store.bonds), flags=set(store.flags),
                    inv=dict(store.inventory))

    def zz_effect(key, b, new):
        """Check what one button did, from the snapshot b and its toasts."""
        t = " | ".join(new)
        if key == "merit":
            check(store.merit == b["merit"] + 50, "+50 merit adds 50", (b["merit"], store.merit))
            check("Merit +50" in t, "+50 merit toasts", t)
        elif key == "mc":
            want = _dev_next_grade(b["grade"])
            check(want is not None and store.grade == want, "promote me: one grade up",
                  (b["grade"], store.grade))
            check("Promoted to" in t, "promote me toasts", t)
        elif key in DEV_STUDENTS:
            want = _dev_next_grade(b["npc"][key])
            check(want is not None and _npc_grade(key) == want, "promote %s: one grade up" % key,
                  (b["npc"][key], _npc_grade(key)))
            check("promoted to" in t, "promote %s toasts" % key, t)
        elif key == "bond":
            bad = [w for w in store.roster if w in CAST
                   and store.bonds.get(w, 0) != min(100, b["bonds"].get(w, 0) + 20)]
            check(store.roster and not bad, "+20 bond with everyone on the roster", bad)
            check(len(new) == 1 and "Bond +20" in t, "+20 bond: one toast", new)
        elif key == "tokyo":
            check(tokyo_open() and has_flag("ijichi_rides"), "open Tokyo sets ijichi_rides")
            check("Tokyo" in t, "open Tokyo toasts", t)
        elif key == "gojo":
            check(gojo_in_today(), "Gojo in today: gojo_in_today()")
            check(all(char_location("gojo", p) == "gojo_office" for p in GOJO_IN_PERIODS),
                  "Gojo in today: in his office for his office hours",
                  [char_location("gojo", p) for p in PERIODS])
            check(not has_flag("intensive_done"), "Gojo in today leaves intensive_done alone")
            check(mission_status("m_intensive") != "done", "m_intensive is not completed by it",
                  mission_status("m_intensive"))
            check(not can_enter("gojo_office")[0] and "locked" in t,
                  "without his first lesson the office stays locked, and the toast says so", t)
        elif key == "items":
            ids = all_item_ids(include_hidden=True)
            miss = [i for i in ids if item_count(i) < 1]
            check(ids and not miss, "one of every item (%d, hidden ones too)" % len(ids), miss)
            check(len(new) == 1 and "every item" in t, "grant items: one toast", new)
        elif key == "armory":
            check(has_flag("armory_open") and armory_open_now() == (store.here == "storehouse"),
                  "open the armory sets armory_open")
            check("armory" in t, "open the armory toasts", t)
        elif key == "complete":
            check(has_flag("dev_story_complete") and main_story_complete(),
                  "mark the main story complete: main_story_complete()")
            check("Begin Arc Two" in t, "mark complete toasts the way to Arc Two", t)
        elif key == "week":
            check(store.day == b["day"] + 7 and store.period == PERIODS[0], "jump to day +7",
                  (b["day"], store.day, store.period))
            check(("Day %d" % store.day) in t, "jump to day +7 toasts the day", t)
        elif key == "veil":
            check(veil_ok(), "the ridge veil can be looked at again today")
            check("veil" in t, "the veil button toasts", t)

    def zz_run(key):
        act = dev_action(key)
        check(isinstance(act, Function), "%s is a Function action" % key, act)
        b = zz_snap()
        n0 = len(ZZ_TOASTS)
        renpy.run(act)
        zz_effect(key, b, ZZ_TOASTS[n0:])

    ## Explore mode -----------------------------------------------------------------

    def zz_explore_static():
        """No mission anywhere, at any time of day, for anyone."""
        bad = []
        per0 = store.period
        for per in PERIODS:
            store.period = per
            mission_cache_clear()
            for loc in LOCATIONS:
                if missions_here(loc):
                    bad.append(("here", per, loc, missions_here(loc)))
                for who in store.roster:
                    if missions_with(who, loc):
                        bad.append(("with", per, loc, who))
                    if any(c["kind"] == "mission" for c in person_choices(who, loc)):
                        bad.append(("choice", per, loc, who))
                    e = pick_event("hangout", who, loc)
                    if e and e["label"] in MISSION_BY_LABEL:
                        bad.append(("hangout", per, loc, who, e["label"]))
            if mission_markers():
                bad.append(("markers", per, mission_markers()))
        store.period = per0
        mission_cache_clear()
        check(not bad, "explore mode: no mission offered anywhere, any period, by anyone", bad[:6])
        ids = [a[0] for a in place_actions(store.here)]
        check(ids and ids[0] == "explore_time", "explore mode: the place view offers the Time step", ids)
        check(not dev_sensitive("story") and not dev_sensitive("utahime") and dev_sensitive("merit"),
              "explore mode: the two scene buttons are off")
        check(hud_date().startswith("Explore"), "explore mode: the HUD date says Explore", hud_date())
        return None

    ZZ_GO = [None]

    def zz_go():
        """The map: go wherever someone is right now."""
        for loc in LOCATIONS:
            if [w for w in who_is_here(loc) if w in CAST] and can_enter(loc)[0]:
                ZZ_GO[0] = loc
                return ("go", loc)
        ZZ_GO[0] = "office"
        return ("go", "office")

    def zz_pick_char():
        people = [w for w in who_is_here(store.here) if w in CAST]
        check(store.here == ZZ_GO[0], "explore: the map took me there", (store.here, ZZ_GO[0]))
        if not check(people, "explore: someone is here", (store.here, store.period)):
            abort("nobody to talk to")
        return ("char", people[0])

    def zz_char_check():
        who = renpy.get_screen("sb_char").scope.get("who") if renpy.get_screen("sb_char") else None
        check(who and not any(c["kind"] == "mission" for c in person_choices(who)),
              "explore mode: the person view offers no mission", who)
        return ("cancel",)

    def zz_journal_close():
        check(renpy.get_screen("journal") is not None, "explore mode: the journal opens")
        return ("close",)

    ## Story phase -----------------------------------------------------------------

    def zz_after_roll_call():
        check(mission_status("m_roll_call") == "done" and has_flag("roll_call"),
              "Finish the next story step played Roll Call (done, flag roll_call)",
              mission_status("m_roll_call"))
        check("st_roll_call" in ZZ_LABELS, "the Roll Call scene itself played")
        check(store.day >= 2, "a waiting step moved the day forward first", store.day)
        check(grade_key(store.grade) == "g4", "roll call graded me", store.grade)
        return None

    def zz_after_utahime():
        check(mission_status("m_utahime") == "done" and "utahime" in store.roster
              and has_flag("utahime_arrived"),
              "Recruit Utahime played her scene: on the roster, utahime_arrived",
              (mission_status("m_utahime"), store.roster))
        check("st_utahime_office" in ZZ_LABELS, "her arrival scene itself played")
        return None

    def zz_after_sunmall():
        check(mission_status("m_sunmall") == "done" and has_flag("sunmall_done"),
              "Finish the next story step played the Sun Mall (a start-type step): done, sunmall_done",
              (mission_status("m_sunmall"), has_flag("sunmall_done")))
        check("ev_mission_sunmall" in ZZ_LABELS, "the Sun Mall scene itself played")
        check(mission_status("m_utahime") == "done", "Recruit Utahime again: already done")
        return None

    ## Arc Two -----------------------------------------------------------------------

    ZZ_WARNING = "This begins Arc Two. Character stories you haven't finished in Arc One will close."

    def zz_journal_arc():
        check(zz_has_text("journal", "Begin Arc Two"), "the campus journal offers Begin Arc Two",
              [t for t in zz_texts("journal") if "Arc" in t][:4])
        shot("journal_arc_two", wait=0)
        ZZ_ORIG["menu"] = store.menu
        store.menu = zz_menu
        return ("arc_two",)

    def zz_after_arc_two():
        store.menu = ZZ_ORIG.get("menu", store.menu)
        check(ZZ_WARNING in ZZ_SAID, "arc_two_start shows the exact warning", [s for s in ZZ_SAID if "Arc Two" in str(s)][:4])
        check(store.arc == 2 and has_flag("arc2_started"), "Begin Arc Two: arc 2, arc2_started", store.arc)
        check(mission_status("cm_panda_1") in ("closed", "done"), "unfinished character stories closed",
              mission_status("cm_panda_1"))
        check(dev_hint("complete") == "Arc Two has begun", "after Arc Two the complete hint says so", dev_hint("complete"))
        _o = current_objective()
        if _o is not None and not _o.get("mid"):
            check(dev_hint("story") == "No written story step left", "with no step left the story hint says so", dev_hint("story"))
        return None


screen zz_driver():
    zorder 200
    if ZZ_DRIVE:
        timer 0.35 repeat True action Function(zz_drive)


label zz_smoke:

    python:
        ZZ_ORIG["sink"] = TOAST_SINK[0]
        TOAST_SINK[0] = zz_sink
        check(config.developer, "the harness runs as a developer build", config.developer)
        check(renpy.has_label("dev_tools") and renpy.has_screen("dev_panel"), "dev_tools and dev_panel exist")
        _keys = [k for k, t in DEV_BUTTONS]
        _want = ["merit", "mc", "yuji", "megumi", "nobara", "story", "bond", "tokyo", "gojo",
                 "utahime", "items", "armory", "complete", "week"]
        check(all(k in _keys for k in _want), "the panel has every 4.13 button", _keys)
        check(all(isinstance(dev_action(k), Return) for k in DEV_SCENES), "the scene buttons return to dev_tools")
        check(_dev_next_grade(None) == "g4" and _dev_next_grade("g4") == "g3"
              and _dev_next_grade("s1") == "g1" and _dev_next_grade("g1") is None
              and _dev_next_grade("sp") is None, "one grade up: Grade 4 to Grade 1, never Special Grade")
        fixture(mc_name="Tester", mc_surname="Harness")
        for _f in ("dinner_listened", "listened_first", "gojo_asked_why", "chose_jujutsu",
                   "told_parents_truth", "took_photo", "enrolled", "yaga_honest", "first_day_asking"):
            flag(_f)

    ## --- a settled game ---------------------------------------------------------------
    $ autoplay()
    call arc_one_open
    python:
        check(has_flag("settled_in") and day == 1, "a settled game (arc_one_open played)", day)
        _done0 = set(missions_done)
        _ev0 = set(done_events)
        ## A story step that is available on day 1, so explore mode has
        ## something to hold back.
        arc_start_day = 0
        mission_cache_clear()
        period = "Morning"
        here = "courtyard"
        check(mission_status("m_roll_call") == "available" and pick_event("story", loc="courtyard"),
              "outside explore mode a story step would fire here", mission_status("m_roll_call"))

    ## --- 1. explore mode -----------------------------------------------------------------
    python:
        del ZZ_LABELS[:]
        ZZ_DRIVE[:] = [
            ("sb_place", ("do", zz_explore_static)),
            ("sb_place", ("act", "explore_time")),
            ("sb_place", ("act", "explore_time")),
            ("sb_place", ("map",)),
            ("sb_map", ("do", zz_go)),
            ("sb_place", ("do", zz_explore_static)),
            ("sb_place", ("do", zz_pick_char)),
            ("sb_char", ("do", zz_char_check)),
            ("sb_place", ("journal", "missions")),
            ("journal", ("do", zz_journal_close)),
            ("sb_place", ("dev",)),
            ("dev_panel", ("shot", "panel_explore")),
            ("dev_panel", "story"),
            ("sb_place", ("finish", "zz_after_explore")),
        ]
    call explore_campus
    $ abort("explore_campus returned")

label zz_after_explore:
    python:
        _L = [l for l in ZZ_LABELS if not l.startswith("_")]
        note("explore labels", _L[:40])
        check(explore_mode, "explore_campus set explore mode")
        check(len(ZZ_DRIVE_LOG) == 14 and not ZZ_DRIVE, "explore: every driven step was answered", ZZ_DRIVE_LOG[-3:])
        check("sb_do_explore_time" in _L and "sb_travel" in _L and "sb_person" in _L and "dev_tools" in _L,
              "explore: Time, the map, a person, the journal and the review tools all ran")
        _ml = [l for l in _L if l in MISSION_BY_LABEL or l == "play_event"]
        check(not _ml, "explore: no mission or story scene played", _ml)
        check(missions_done == _done0 and done_events == _ev0, "explore: nothing was marked done")
        check("Explore mode never plays a story step." in ZZ_TOASTS, "explore: the story button says why",
              ZZ_TOASTS[-3:])
        check(bool(ZZ_PANEL_SEEN), "the panel was up (driven from the place view's (dev,))")

        ## Back to the settled game, day 1: Roll Call waits for tomorrow.
        explore_mode = False
        arc_start_day = 1
        day = 1
        period = "Morning"
        here = "courtyard"
        roll_gojo()
        mission_cache_clear()
        check(mission_status("m_roll_call") == "waiting", "Roll Call waits for day 2", mission_status("m_roll_call"))

    ## --- 2. the story buttons, through the loop ----------------------------------------------
    python:
        del ZZ_LABELS[:]
        del ZZ_DRIVE_LOG[:]
        ZZ_DRIVE[:] = [
            ("sb_place", ("dev",)),
            ("dev_panel", ("shot", "panel")),
            ("dev_panel", "story"),
            ("sb_place", ("do", zz_after_roll_call)),
            ("sb_place", ("dev",)),
            ("dev_panel", "utahime"),
            ("sb_place", ("do", zz_after_utahime)),
            ("sb_place", ("dev",)),
            ("dev_panel", "story"),
            ("sb_place", ("do", zz_after_sunmall)),

            ## --- 3. every other button, while the panel is up
            ("sb_place", ("dev",)),
            ("dev_panel", ("run", "merit")),
            ("dev_panel", ("run", "mc")),
            ("dev_panel", ("run", "yuji")),
            ("dev_panel", ("run", "megumi")),
            ("dev_panel", ("run", "nobara")),
            ("dev_panel", ("run", "bond")),
            ("dev_panel", ("run", "tokyo")),
            ("dev_panel", ("run", "gojo")),
            ("dev_panel", ("run", "items")),
            ("dev_panel", ("run", "armory")),
            ("dev_panel", ("run", "complete")),
            ("dev_panel", ("run", "veil")),
            ("dev_panel", ("run", "week")),
            ("dev_panel", ("shot", "panel_after")),
            ("dev_panel", "close"),

            ## --- 4. Arc Two, from the campus journal
            ("sb_place", ("journal", "missions")),
            ("journal", ("do", zz_journal_arc)),
            ("sb_place", ("do", zz_after_arc_two)),
            ("sb_place", ("finish", "zz_after_story")),
        ]
        _n_drive = len(ZZ_DRIVE)
    $ autoplay()
    call sandbox
    $ abort("the sandbox loop returned")

label zz_after_story:
    python:
        store.menu = ZZ_ORIG.get("menu", store.menu)
        _L = [l for l in ZZ_LABELS if not l.startswith("_")]
        note("story labels", _L[:60])
        check(len(ZZ_DRIVE_LOG) == _n_drive and not ZZ_DRIVE, "story: every driven step was answered",
              ZZ_DRIVE_LOG[-3:])
        check(_L.count("dev_tools") == 4, "the place view's (dev,) called dev_tools each time", _L.count("dev_tools"))
        check("arc_two_start" in _L, "journal (arc_two,) reached arc_two_start")

    ## --- 5. outside a developer build ------------------------------------------------------
    python:
        del ZZ_PANEL_SEEN[:]
        config.developer = False
        smoke_autoplay = True
    call dev_tools
    python:
        config.developer = True
        check(not ZZ_PANEL_SEEN, "outside a developer build dev_tools shows nothing")
        flags.discard("settled_in")
    call dev_tools
    python:
        flag("settled_in")
        check(not ZZ_PANEL_SEEN, "before the campus opens (no settled_in) dev_tools shows nothing")
    $ autoplay(False)
    $ finish()
