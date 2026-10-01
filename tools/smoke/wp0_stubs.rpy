## tools/smoke/wp0_stubs.rpy -- the WP0 contract harness (PHASE1_DESIGN.md,
## section 6 and the WP0 acceptance list).
##
##   tools/smoke.sh tools/smoke/wp0_stubs.rpy
##
## Calls every section 6 symbol with its frozen signature and checks the stub
## behaviour, exercises the WP0 hooks (new day, event gates and done hooks,
## place actions, migrations, toasts, the prologue plan), and renders every
## stub screen once, with a screenshot of each in shots/wp0_stubs/.
##
## By default it checks signatures, hooks and renders only: every package has
## replaced its stub, so the "stub returns" checks no longer hold. Set
## SMOKE_STUBS_VALUES=1 to run them too (useful only on a tree where the WP0
## stubs are still in place). SMOKE_STUBS_ONLY_SIGS=1 is still accepted and
## always turns them off.

init 999 python:
    import inspect
    import os

    ZZ_HOOK_ORDER = []
    ZZ_DONE = []
    ZZ_SINK = []

    register_new_day(lambda: ZZ_HOOK_ORDER.append(60), order=60)
    register_new_day(lambda: ZZ_HOOK_ORDER.append(40), order=40)
    register_event_done(lambda e: ZZ_DONE.append(e["label"]))

    def zz_when_true():
        return True

    def zz_when_false():
        return False

    register_place_action("zzact", "Zed", "A test action.", cost=1, locs=("dorm",), when="zz_when_true", order=10)
    register_place_action("zzoff", "Off", "Never shown.", locs=("dorm",), when="zz_when_false")
    register_place_action("zzexp", "Exp", "Explore too.", locs="courtyard", explore=True)

    ev("zz_event", kind="zzkind", once=True, thread=None)

    def zz_sink(text, kind, who, amount):
        ZZ_SINK.append((text, kind, who, amount))

    ## The frozen signatures (section 6, with the parameter names of 3.1-3.10).
    ZZ_SIGS = [
        ## WP0 (final)
        ("toast", "(text, kind='info', who=None, amount=None)"),
        ("register_new_day", "(fn, order=50)"),
        ("run_new_day_hooks", "()"),
        ("register_event_gate", "(fn)"),
        ("event_allowed", "(e)"),
        ("register_event_done", "(fn)"),
        ("run_event_done", "(e)"),
        ("register_place_action", "(id, label, hint, cost=0, locs=None, when=None, order=50, explore=False)"),
        ("registered_place_actions", "(loc)"),
        ("register_migration", "(order, fn, name)"),
        ("run_migrations", "(block=False)"),
        ("ensure_state", "()"),
        ("register_validator", "(fn)"),
        ("legacy_story_point", "()"),
        ("prologue_plan", "(point)"),
        ## WP1
        ("area_of", "(loc)"),
        ("places_in", "(area)"),
        ("usual_places", "(who)"),
        ("when_at", "(who, loc)"),
        ("gojo_in_today", "()"),
        ("tokyo_open", "()"),
        ("district_state", "(key)"),
        ("trip_ok_now", "()"),
        ("car_action_ok", "()"),
        ## WP2
        ("grade_key", "(v)"),
        ("grade_rank", "(v)"),
        ("grade_label", "(v)"),
        ("player_grade", "()"),
        ("grade_cap", "(kind)"),
        ("talisman_slots", "(key=None)"),
        ("merit_needed", "(key=None)"),
        ("merit_progress", "()"),
        ("next_grade_text", "()"),
        ("add_merit", "(n, why='')"),
        ("promote", "(who, key, why='', quiet=False)"),
        ("recent_promotion", "(who, days=3)"),
        ("pop_remark", "(who)"),
        ("npc_stats", "(who)"),
        ("train_together", "(who, n=3, stat=None)"),
        ("sorcerer_power", "(who)"),
        ("pick_team", "(n, min_key=None)"),
        ("raise_reserve", "(n)"),
        ## WP3
        ("mission_status", "(id)"),
        ("mission_reason", "(id)"),
        ("missions_list", "(kind=None, status=None, act=None, who=None)"),
        ("missions_here", "(loc)"),
        ("missions_with", "(who, loc=None)"),
        ("mission_markers", "()"),
        ("next_for", "(who)"),
        ("current_objective", "()"),
        ("objective_text", "()"),
        ("act_done", "(act)"),
        ("acts_done", "()"),
        ("act_progress", "(act)"),
        ("main_story_complete", "()"),
        ("mission_fail", "(id)"),
        ("complete_mission", "(id)"),
        ("begin_arc_two", "()"),
        ## WP4
        ("board_open", "()"),
        ("board_host", "()"),
        ("board_summary", "()"),
        ("misgrade_count", "()"),
        ## WP5
        ("memory_groups", "(mode)"),
        ("memory_counts", "()"),
        ("memory_replay", "(mem)"),
        ("record_act", "(aid, who)"),
        ## WP6
        ("give_item", "(id, n=1, quiet=False)"),
        ("take_item", "(id, n=1)"),
        ("has_item", "(id)"),
        ("item_count", "(id)"),
        ("items_in", "(kind)"),
        ("can_wear", "(id)"),
        ("equip_talisman", "(id)"),
        ("unequip_talisman", "(id)"),
        ("equip_tool", "(id)"),
        ("armory_open_now", "()"),
        ("armory_tools", "()"),
        ("add_yen", "(n)"),
        ("sync_keepsakes", "()"),
        ## WP7
        ("toast_push", "(text, kind='info', who=None, amount=None)"),
        ("check_objective", "()"),
        ("place_actions", "(loc)"),
        ("ambient_of", "(who, loc)"),
        ("person_choices", "(who, loc=None)"),
        ## WP8
        ("kaito_card_image", "()"),
    ]

    ## Labels with their parameters ("" = no parameter list).
    ZZ_LABELS = [
        ("load_recover", None), ("return_recover", None), ("resume_story", None),
        ("sb_trip", "(key)"), ("sb_do_car", None),
        ("show_grade_card", "(key, kicker='PROMOTED')"),
        ("start_mission", "(mid)"), ("arc_two_start", None),
        ("sb_do_board", None), ("mem_play", None), ("sb_do_armory", None),
        ("stage_person", "(who, expr=None)"), ("dev_tools", None),
    ]

    ## Screens with their parameters.
    ZZ_SCREENS = [
        ("grade_card", ["key", "kicker"]), ("board_screen", []), ("board_partner", ["offer"]),
        ("armory", []), ("sb_hud", ["on_map", "person"]), ("toasts", []),
        ("objective_toast", ["text"]), ("sb_place", []), ("sb_char", ["who"]),
        ("sb_map", ["layer"]), ("journal", ["tab"]), ("jjk_status", []), ("jjk_journal", []),
    ]

    def zz_sig(name):
        fn = getattr(store, name, None)
        if fn is None or not callable(fn):
            return None
        try:
            return str(inspect.signature(fn))
        except Exception as e:
            return "<%r>" % (e,)

    def zz_label_params(name):
        node = renpy.game.script.lookup(name)
        p = getattr(node, "parameters", None)
        if p is None:
            return None
        out = []
        for param in p.parameters.values():
            if param.default is None:
                out.append(param.name)
            else:
                out.append("%s=%s" % (param.name, str(param.default).replace('"', "'")))
        return "(" + ", ".join(out) + ")"

    def zz_screen_params(name):
        sc = renpy.display.screen.get_screen_variant(name)
        if sc is None:
            return None
        p = sc.parameters
        if p is None:
            return []
        return [param.name for param in p.parameters.values()]

    ## Signatures only unless SMOKE_STUBS_VALUES=1 asks for the stub-value checks.
    ZZ_STUB_VALUES = (os.environ.get("SMOKE_STUBS_VALUES", "0") == "1"
        and os.environ.get("SMOKE_STUBS_ONLY_SIGS", "0") != "1")


## A test place action's labels and a test event.
label sb_do_zzact:
    return
label sb_do_zzoff:
    return
label sb_do_zzexp:
    return
label zz_event:
    $ ZZ_DONE.append("inside")
    return


label zz_smoke:
    $ mc_name = "Tester"
    $ mc_surname = "Harness"

    ## --- mode --------------------------------------------------------------------
    python:
        note("mode", "stub values + signatures" if ZZ_STUB_VALUES else "signatures only (SMOKE_STUBS_VALUES=1 adds stub values)")
        check(ZZ_STUB_VALUES == (os.environ.get("SMOKE_STUBS_VALUES", "0") == "1" and os.environ.get("SMOKE_STUBS_ONLY_SIGS", "0") != "1"),
            "stub-value checks run only when SMOKE_STUBS_VALUES=1", ZZ_STUB_VALUES)

    ## --- signatures (section 6) ---------------------------------------------------
    python:
        for _n, _want in ZZ_SIGS:
            _got = zz_sig(_n)
            check(_got == _want, "signature " + _n + _want, "got %s" % (_got,))
        for _n, _want in ZZ_LABELS:
            check(renpy.has_label(_n), "label " + _n)
            if renpy.has_label(_n):
                _got = zz_label_params(_n)
                check(_got == _want, "label params %s %s" % (_n, _want or "()"), "got %s" % (_got,))
        for _n, _want in ZZ_SCREENS:
            check(renpy.has_screen(_n), "screen " + _n)
            if renpy.has_screen(_n):
                _got = zz_screen_params(_n)
                check(_got == _want, "screen params %s %s" % (_n, _want), "got %s" % (_got,))
        for _n in ("AREAS", "DISTRICTS", "DISTRICT_ORDER", "GRADE_ORDER", "GRADES", "JOURNAL_CAST", "ACTS",
                   "MEMORIES", "ITEMS", "TOAST_SINK", "TOAST_MUTE", "PROLOGUE_STEPS", "SAVE_VERSION"):
            check(hasattr(store, _n), "defined " + _n)

    ## --- WP0 defaults and definitions ---------------------------------------------
    python:
        check(save_version == 0, "default save_version 0", save_version)
        check(story_point is None, "default story_point")
        check(arc_start_day == 1, "default arc_start_day")
        check(actions_today == set(), "default actions_today")
        check(hide_side_images is False and smoke_autoplay is False, "defaults hide_side_images / smoke_autoplay")
        check(persistent.mc_face is True, "default persistent.mc_face")
        check(SAVE_VERSION == 1, "SAVE_VERSION 1")
        check(config.load_failed_label == "load_recover", "config.load_failed_label")
        check(config.return_not_found_label == "return_recover", "config.return_not_found_label")
        check(any(getattr(f, "__name__", "") == "<lambda>" for f in config.after_load_callbacks), "after_load migration callback")
        check(_run_validators in config.lint_hooks, "validators in config.lint_hooks")
        check(config.side_image_only_not_showing is True, "config.side_image_only_not_showing")
        check(config.say_attribute_transition is not None, "config.say_attribute_transition")
        check(not any(hasattr(store, n) for n in ("days" "_left", "KYOTO" "_DAY")), "no countdown symbols")
        for _t in ["mc", "yuji", "megumi", "nobara", "maki", "panda", "toge", "gojo", "yaga", "ijichi", "shoko", "utahime", "sana"]:
            check(getattr(store, _t).image_tag == _t, "image tag " + _t, getattr(store, _t).image_tag)
        check("ijichi" in CHARS and "sana" in CHARS, "CHARS gains ijichi and sana")
        check(all(k in CAST for k in ("utahime", "ijichi", "sana")), "CAST gains utahime, ijichi, sana")
        check(CAST["utahime"]["name"] == "Utahime Iori" and CAST["utahime"]["year"] == "Kyoto teacher", "CAST utahime")
        check(CAST["ijichi"]["name"] == "Kiyotaka Ijichi" and CAST["ijichi"]["year"] == "Assistant manager", "CAST ijichi")
        check(CAST["sana"]["name"] == "Sana Torii" and CAST["sana"]["year"] == "In memory", "CAST sana")
        check("utahime" in ROSTER_ORDER and "ijichi" in ROSTER_ORDER, "ROSTER_ORDER", ROSTER_ORDER)
        check("ijichi" in roster, "default roster has ijichi", roster)
        for _n in ["bg alley", "bg alley dark", "bg ridge_veil", "bg utahime_office", "bg gojo_office", "bg map_tokyo",
                   "bg shibuya", "bg harajuku", "bg shinjuku", "bg kawasaki", "bg yotsuka"]:
            check(renpy.has_image(_n, exact=True), "image " + _n)
            check(_n in BG_LIGHT, "BG_LIGHT " + _n)
        check(bg_placeholder("images/bg/courtyard.png", "x") == "images/bg/courtyard.png", "bg_placeholder real file")
        check(bg_placeholder("images/bg/zz_nope.png", "fallback") == "fallback", "bg_placeholder fallback")

    ## --- toasts (3.1, D34) ----------------------------------------------------------
    python:
        toast("plain toast, stock notify")
        TOAST_SINK[0] = zz_sink
        add_bond("yuji", 2)
        add_bond("yuji", 2)
        check(ZZ_SINK[:2] == [("Yuji  bond +2", "bond", "yuji", 2), ("Yuji  bond +2", "bond", "yuji", 2)], "add_bond toasts", ZZ_SINK)
        del ZZ_SINK[:]
        add_bond("megumi", 20)
        check(ZZ_SINK == [("Megumi  bond +20", "bond", "megumi", 20), ("Megumi — Acquaintance", "bond_rank", "megumi", None)], "bond rank toast", ZZ_SINK)
        del ZZ_SINK[:]
        bonds["nobara"] = 60
        add_aff("nobara", 5)
        check(ZZ_SINK and ZZ_SINK[0] == ("Nobara  ♡ +5", "aff", "nobara", 5), "aff toast", ZZ_SINK)
        del ZZ_SINK[:]
        bonds["shoko"] = 0
        affection["shoko"] = 0
        add_aff("shoko", 5)
        check(len(ZZ_SINK) <= 1 and all(s[1] == "info" for s in ZZ_SINK), "aff cap toast is info", ZZ_SINK)
        del ZZ_SINK[:]
        recruit("maki")
        check(ZZ_SINK == [("Maki Zenin joined my circle.", "info", "maki", None)], "recruit toast", ZZ_SINK)
        del ZZ_SINK[:]
        begin_together("nobara")
        check(len(ZZ_SINK) == 1 and ZZ_SINK[0][1:3] == ("aff", "nobara"), "begin_together toast", ZZ_SINK)
        together.remove("nobara")
        del ZZ_SINK[:]
        store._in_replay = "zz"
        toast("muted")
        store._in_replay = None
        TOAST_MUTE[0] += 1
        toast("muted")
        TOAST_MUTE[0] -= 1
        check(ZZ_SINK == [], "toasts muted in replay and while muted", ZZ_SINK)
        toast("heard", "grade", "mc", 3)
        check(ZZ_SINK == [("heard", "grade", "mc", 3)], "toast reaches the sink", ZZ_SINK)
        TOAST_SINK[0] = None
        del ZZ_SINK[:]
        toast_push("x", "info", None, None)
        check(TOAST_SINK[0] is None, "toast_push stub is not the sink yet")

    ## --- new day -------------------------------------------------------------------
    python:
        actions_today.add("hold")
        day = 1
        new_day()
        check(day == 2 and actions_today == set(), "new_day resets actions_today", actions_today)
        check(ZZ_HOOK_ORDER == [40, 60], "new-day hooks run in order", ZZ_HOOK_ORDER)
        day = 1
        period = "Morning"

    ## --- events: gates and D40 ---------------------------------------------------------
    python:
        _e = [e for e in EVENTS if e["label"] == "zz_event"][0]
        check(event_allowed(_e), "event_allowed with no refusing gate")
        register_event_gate(lambda e: e["label"] != "zz_event")
        check(not event_allowed(_e), "a gate refuses")
        check(not any(e["label"] == "zz_event" for e in find_events("zzkind")), "find_events drops a refused event")
        EVENT_GATES.pop()
        check(any(e["label"] == "zz_event" for e in find_events("zzkind")), "find_events keeps an allowed event")
        ## D40: find_events itself no longer reads min_day; a min_day beyond today
        ## only matters through a gate.
        _gates = list(EVENT_GATES)
        del EVENT_GATES[:]
        _late = dict(_e, label="zz_late", min_day=999)
        EVENTS.append(_late)
        check(any(e["label"] == "zz_late" for e in find_events("zzkind")), "find_events ignores min_day (D40)")
        EVENTS.remove(_late)
        EVENT_GATES.extend(_gates)

    ## --- place actions --------------------------------------------------------------------
    python:
        _ids = [a[0] for a in place_actions("dorm")]
        check(_ids[-2:] == ["zzact", "wait"] and "zzoff" not in _ids, "registered action goes before Wait", _ids)
        check("zzact" not in [a[0] for a in place_actions("cafeteria")], "registered action only at its places")
        _tech = technique
        technique = "emberfall"  # legacy-technique (migration test)
        check("temper" not in [a[0] for a in place_actions("storehouse")], "no Emberfall temper action")  # legacy-technique
        technique = _tech
        explore_mode = True
        _ids = [a[0] for a in place_actions("courtyard")]
        check(_ids == ["explore_time", "zzexp"], "explore mode keeps explore=True actions", _ids)
        explore_mode = False
        check("zzexp" in [a[0] for a in place_actions("courtyard")], "explore action also offered normally")
        check(registered_place_actions("dorm") == [("zzact", "Zed", "A test action.", 1)], "registered_place_actions tuples", registered_place_actions("dorm"))
        check(_validate_place_actions() == [], "place action validator is clean", _validate_place_actions())

    ## --- the prologue plan (3.13) -----------------------------------------------------------
    python:
        _subs = all(renpy.has_label(s) for s, c in PROLOGUE_STEPS)
        if _subs:
            check(prologue_plan("ch1_the_thing")[0] == "ch1_the_thing", "prologue_plan with sub-labels", prologue_plan("ch1_the_thing"))
        else:
            check(prologue_plan("ch1_the_thing") == ["chapter_one", "chapter_one_b", "chapter_two", "arc_one_open"], "prologue_plan pre-WP9", prologue_plan("ch1_the_thing"))
            check(prologue_plan("ch2_first_years") == ["chapter_two", "arc_one_open"], "prologue_plan ch2_first_years", prologue_plan("ch2_first_years"))
            check(prologue_plan("chapter_two") == ["chapter_two", "arc_one_open"], "prologue_plan takes a chapter name")
        check(prologue_plan("arc_one_open") == ["arc_one_open"], "prologue_plan arc_one_open")
        check(prologue_plan("sandbox") == [] and prologue_plan(None) == [], "prologue_plan sandbox / None")
        _saved = set(flags)
        _had_p = getattr(store, "_partner", None)
        store._partner = None
        flags.clear()
        check(legacy_story_point() == "ch1_diner", "legacy_story_point: no flags")
        flags.add("dinner_joked")
        check(legacy_story_point() == "ch1_the_thing", "legacy_story_point: dinner_*")
        flags.add("gojo_asked_sana")
        check(legacy_story_point() == "chapter_one_b", "legacy_story_point: gojo_asked_*")
        flags.add("chose_jujutsu")
        check(legacy_story_point() == "ch2_arrival", "legacy_story_point: chose_jujutsu")
        flags.add("enrolled")
        check(legacy_story_point() == "ch2_first_years", "legacy_story_point: enrolled")
        flags.add("ignored_wall")
        check(legacy_story_point() == "arc_one_open", "legacy_story_point: an old linear-build save in the Sun Mall")
        flags.add("settled_in")
        check(legacy_story_point() == "sandbox", "legacy_story_point: settled_in")
        ## The retired chapters one and two set these; a save made there still
        ## replays the prologue.
        for _f in ("evidence_entry", "gojo_challenged", "yaga_instinct", "spar_took_it"):
            flags.clear()
            flags.add(_f)
            check(legacy_story_point() == "ch1_diner", "legacy_story_point: retired-prologue " + _f)
        for _f in ("read_wall", "ignored_wall", "scouted_corridor", "saved_civilian",
                   "fought_first", "climax_strong", "climax_thin"):
            flags.clear()
            flags.add(_f)
            check(legacy_story_point() == "arc_one_open", "legacy_story_point: Sun Mall " + _f)
        flags.clear()
        store.partner = "megumi"
        check(legacy_story_point() == "arc_one_open", "legacy_story_point: an old save's partner")
        del store.partner
        store._partner = _had_p
        flags.update(_saved)
        ## Migration 5's Sun Mall step: an old mid-mission save's `partner`.
        _had = getattr(store, "_partner", None)
        store._partner = None
        store.partner = "megumi"
        run_migrations()
        check(store._partner == "megumi", "migration 5: _partner from an old save's partner", store._partner)
        store._partner = "yuji"
        run_migrations()
        check(store._partner == "yuji", "migration 5 leaves a set _partner alone", store._partner)
        store._partner = _had
        del store.partner

    ## --- migrations (3.12: order 5) --------------------------------------------------------
    scene bg black
    show mc at pos_c  ## first-person exception: migration 5 must hide a stale sprite
    python:
        quick_menu = False
        save_version = 0
        check(renpy.showing("mc"), "mc sprite showing before migration")
        _up = run_migrations(block=False)
        check(_up is True and save_version == SAVE_VERSION, "run_migrations upgrades", (_up, save_version))
        ## tname follows the save's own technique (Last Light once WP2 leaves only timestop).
        _tn = TECHNIQUES.get(technique, {}).get("name", "Last Light")
        check(quick_menu is True and not renpy.showing("mc") and tname == _tn, "migration 5 effects", (quick_menu, renpy.showing("mc"), tname, _tn))
        _snap = (quick_menu, bool(renpy.showing("mc")), tname, save_version)
        _up = run_migrations(block=False)
        check(_up is False and (quick_menu, bool(renpy.showing("mc")), tname, save_version) == _snap,
              "run_migrations is idempotent at the current version", (_up, _snap))
    ## Migration 5 runs on every load (D3, 3.12), not only on a save's first
    ## upgrade: an up-to-date save with the quick menu off and a stale sprite
    ## still gets both put right.
    show mc at pos_c  ## first-person exception: migration 5 must hide a stale sprite
    python:
        quick_menu = False
        check(save_version == SAVE_VERSION and renpy.showing("mc"), "an up-to-date save with a stale mc sprite", save_version)
        _up = run_migrations(block=False)
        check(_up is False and quick_menu is True and not renpy.showing("mc"), "migration 5 runs at the current version too", (_up, quick_menu, renpy.showing("mc")))
        quick_menu = False
        check(ensure_state() is False and quick_menu is False, "ensure_state is a no-op at the current version", quick_menu)
        save_version = 0
        check(ensure_state() is True and save_version == 1, "ensure_state upgrades an old version")
        quick_menu = True
        _ord = [m[0] for m in sorted(MIGRATIONS, key=lambda m: m[0])]
        check(5 in _ord, "migration 5 registered", _ord)
        ## Migration 10 (WP0 interim stub): only a technique the game no longer has.
        if ZZ_STUB_VALUES:
            _tech = technique
            technique = "zz_gone"
            run_migrations()
            check(technique == "timestop" and has_flag("technique_was_zz_gone"), "interim migration 10: unknown technique -> timestop", technique)
            flags.discard("technique_was_zz_gone")
            technique = "filament"  # legacy-technique
            run_migrations()
            check(technique == "filament", "interim migration 10 leaves a known technique alone", technique)  # legacy-technique
            technique = _tech
        register_validator(lambda: ["zz problem"])
        check(VALIDATORS[-1]() == ["zz problem"], "register_validator")
        VALIDATORS.pop()

    ## --- stubs: WP1 -------------------------------------------------------------------------
    python:
        _r = (area_of("gate"), places_in("heart"), usual_places("yuji"), when_at("yuji", "gate"), gojo_in_today(), AREAS)
        if ZZ_STUB_VALUES:
            check(_r == (None, [], "", "", False, []), "WP1 world stubs", _r)
        _r = (tokyo_open(), district_state("shibuya"), trip_ok_now(), car_action_ok(), DISTRICTS, DISTRICT_ORDER)
        if ZZ_STUB_VALUES:
            check(_r == (False, (False, "Later"), False, False, {}, []), "WP1 Tokyo stubs", _r)

    ## --- stubs: WP2 -------------------------------------------------------------------------
    python:
        check(grade_key(3) == "g3" and grade_key(0) == "sp" and grade_key("s1") == "s1" and grade_key(None) is None, "grade_key")
        check(grade_rank(None) == -1 and grade_rank("g2") == 2 and grade_rank(4) == 0, "grade_rank")
        check(grade_label(None) == "Not yet assessed" and grade_label(4) == "Grade 4" and grade_label("s1") == "Semi-Grade 1", "grade_label accepts None, int, key")
        _g = grade
        grade = None
        check(player_grade() is None and grade_cap("stat") == 40 and grade_cap("reserve") == 100 and talisman_slots() == 1, "Grade 4 numbers while unassessed (D16)")
        grade = _g
        check(talisman_slots("g3") == 2 and merit_needed("g2") == 150, "talisman_slots / merit_needed by key")
        _mp = merit_progress()
        check(len(_mp) == 3 and _mp[0] == merit, "merit_progress is (merit, need, next_key)", _mp)
        check(isinstance(next_grade_text(), str), "next_grade_text is text", next_grade_text())
        _m = merit
        add_merit(30, "zz")
        check(merit == _m + 30, "add_merit adds", merit)
        promote("nobara", "g2", "zz")
        check(npc_stats("nobara")["grade"] == "g2", "promote an NPC", npc_stats("nobara"))
        promote("mc", "g3", "zz", quiet=True)
        check(grade == "g3", "promote the player", grade)
        grade = _g
        _s = npc_stats("gojo")
        check(all(k in _s for k in ("grade", "ce_max", "control", "output", "off_scale", "restricted", "role", "note")), "npc_stats keys", _s)
        if ZZ_STUB_VALUES:
            check(recent_promotion("nobara") is False and pop_remark("nobara") is False, "recent_promotion / pop_remark stubs")
            check(sorcerer_power("mc") == 10 and pick_team(3) == [] and pick_team(2, "g3") == [], "sorcerer_power / pick_team stubs")
        train_together("yuji")
        train_together("yuji", 3, "output")
        _cm = ce_max
        raise_reserve(20)
        check(ce_max >= _cm, "raise_reserve never lowers", (_cm, ce_max))
        ce_max = _cm

    ## --- stubs: WP3 -------------------------------------------------------------------------
    python:
        _r = (mission_status("m_x"), mission_reason("m_x"), missions_list(), missions_list(kind="story", status="done", act="I", who="yuji"),
              missions_here("office"), missions_with("yaga"), missions_with("yaga", "office"), mission_markers(), next_for("yuji"))
        if ZZ_STUB_VALUES:
            check(_r == ("locked", "", [], [], [], [], [], {}, None), "WP3 query stubs", _r)
        _r = (current_objective(), objective_text(), act_done("I"), acts_done(), act_progress("I"), main_story_complete())
        if ZZ_STUB_VALUES:
            check(_r == (None, "", False, 0, (0, 0, 0), False), "WP3 objective / act stubs", _r)
        mission_fail("m_x")
        complete_mission("m_x")
        begin_arc_two()
        check(isinstance(JOURNAL_CAST, list) and len(JOURNAL_CAST) > 0 and isinstance(ACTS, list), "JOURNAL_CAST / ACTS")
        if ZZ_STUB_VALUES:
            check(ACTS == [], "ACTS stub empty")

    ## --- stubs: WP4, WP5 ---------------------------------------------------------------------
    python:
        _r = (board_open(), board_host(), board_summary(), misgrade_count())
        if ZZ_STUB_VALUES:
            check(_r == (False, ("utahime", "utahime_office"), {}, 0), "WP4 board stubs", _r)
        _r = (MEMORIES, memory_groups("person"), memory_groups("act"), memory_counts())
        if ZZ_STUB_VALUES:
            check(_r == ([], [], [], (0, 0)), "WP5 memory stubs", _r)
            check(isinstance(memory_replay({}), NullAction), "memory_replay stub is NullAction")
        record_act("talk", "yuji")

    ## --- stubs: WP6 -------------------------------------------------------------------------
    python:
        if ZZ_STUB_VALUES:
            check(ITEMS == {} and items_in("keepsake") == [] and can_wear("spark") == (False, "Later"), "WP6 item stubs")
            check(armory_open_now() is False and armory_tools() == [], "WP6 armory stubs")
        give_item("zz_photo", 2, quiet=True)
        check(item_count("zz_photo") == 2 and has_item("zz_photo"), "give_item counts")
        check(take_item("zz_photo") and item_count("zz_photo") == 1, "take_item one")
        check(not take_item("zz_photo", 5) and item_count("zz_photo") == 1, "take_item refuses too many")
        take_item("zz_photo")
        check("zz_photo" not in inventory and not has_item("zz_photo"), "take_item to zero removes it")
        _y = yen
        add_yen(1200)
        check(yen == _y + 1200, "add_yen")
        yen = _y
        equip_talisman("paper_ward")
        unequip_talisman("paper_ward")
        equip_tool(None)
        equip_tool("slaughter_demon")
        sync_keepsakes()

    ## --- stubs: WP7, WP8 ------------------------------------------------------------------------
    python:
        check_objective()
        _r = (ambient_of("yuji", "cafeteria"), person_choices("yuji"), person_choices("yuji", "cafeteria"))
        if ZZ_STUB_VALUES:
            check(_r == (("", "neutral"), [], []), "WP7 stubs", _r)
        check(isinstance(ambient_of("yuji", "cafeteria"), tuple) and len(ambient_of("yuji", "cafeteria")) == 2, "ambient_of is (caption, expression)")
        _had = has_flag("settled_in")
        flags.discard("settled_in")
        check(kaito_card_image() == "images/char/mcyotsuka_neutral.png", "kaito_card_image before settled_in")
        flags.add("settled_in")
        check(kaito_card_image() == "images/char/mc_neutral.png", "kaito_card_image after settled_in")
        check(renpy.loadable(kaito_card_image()), "kaito_card_image file exists")
        if not _had:
            flags.discard("settled_in")

    ## --- stub labels --------------------------------------------------------------------------
    call stage_person("yuji")
    call stage_person("yuji", "happy")
    ## dev_tools opens a waiting panel once settled_in is set; under
    ## smoke_autoplay the panel closes itself, whatever the flags are.
    $ zz_had_autoplay, smoke_autoplay = smoke_autoplay, True
    call dev_tools
    $ smoke_autoplay = zz_had_autoplay
    call sb_trip("shibuya")
    call sb_do_car
    call sb_do_board
    call sb_do_armory
    call mem_play
    call start_mission("m_roll_call")
    call arc_two_start
    call show_grade_card("g3")
    call show_grade_card("g4", "ASSESSED")
    $ check(True, "every stub label called and returned")

    ## --- play_event runs the done hooks after the scene -----------------------------------------
    $ _e = [e for e in EVENTS if e["label"] == "zz_event"][0]
    call play_event(_e)
    $ check(ZZ_DONE == ["inside", "zz_event"], "event done hook runs after the scene", ZZ_DONE)
    $ check("zz_event" in done_events, "play_event still marks the event done")

    ## --- placeholder backgrounds ------------------------------------------------------------------
    python:
        for _n in ["bg alley", "bg alley dark", "bg ridge_veil", "bg utahime_office", "bg gojo_office", "bg map_tokyo",
                   "bg shibuya", "bg harajuku", "bg shinjuku", "bg kawasaki", "bg yotsuka"]:
            renpy.scene()
            renpy.show(_n)
            shot("bg_" + _n[3:].replace(" ", "_"))
            check(True, "rendered " + _n)

    ## --- every stub screen, once ------------------------------------------------------------------
    scene black
    python:
        day = 3
        period = "Noon"
        here = "cafeteria"
        flags.add("settled_in")
        roll_gojo()
        for _s, _a, _k in [("sb_place", (), {}),
                           ("sb_char", ("yuji",), {}), ("sb_char", ("ijichi",), {}), ("sb_char", ("utahime",), {}),
                           ("sb_map", (), {}), ("sb_map", (), {"layer": "tokyo"}),
                           ("sb_hud", (), {}), ("sb_hud", (), {"on_map": True}), ("sb_hud", (), {"person": True}),
                           ("toasts", (), {}), ("objective_toast", ("Roll call — Classroom, mornings",), {}),
                           ("jjk_status", (), {}), ("jjk_journal", (), {}),
                           ("journal", (), {}), ("journal", ("stats",), {}), ("journal", (), {"tab": "missions"}),
                           ("journal", ("equipment",), {}),
                           ("grade_card", ("g4", "ASSESSED"), {}), ("board_screen", (), {}), ("board_partner", ({},), {}),
                           ("armory", (), {})]:
            renpy.show_screen(_s, *_a, **_k)
            _tag = "_".join([_s] + [str(x) for x in _a] + ["%s_%s" % kv for kv in sorted(_k.items())])
            shot("screen_" + "".join(c if c.isalnum() or c == "_" else "_" for c in _tag)[:60])
            renpy.hide_screen(_s)
            check(True, "rendered screen %s %r %r" % (_s, _a, _k))

    $ finish()
