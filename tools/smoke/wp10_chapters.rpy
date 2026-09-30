## tools/smoke/wp10_chapters.rpy -- WP10's harness: the later chapters after
## their compatibility edits (docs/PHASE1_DESIGN.md, section 7, WP10).
##
##   tools/smoke.sh tools/smoke/wp10_chapters.rpy
##
## Part 1 reads WP10's eleven .rpy files (the scratch copy's game/) and checks
## the static acceptance bullets: the check_content rules --no-mc-on-screen,
## --one-technique and --no-deadline, the forbidden-pattern grep, the label
## counts and label names per file, and the flag("...") strings (a frozen copy
## of the set before WP10 is embedded below).
##
## Part 2 plays the scenes on a seeded, post-prologue store under autoplay:
## st_roll_call, st_intensive, st_roster, st_night_before, chapter_four,
## chapter_five, ms_nade_1 and act_eat("yuji") as the acceptance names them,
## plus every other story, mission, hangout and act label WP10 edited. The mc
## sprite is looked for at every line shown and every interaction.
##
## Test scaffolding, all in this file (nothing in game/ is changed):
##   - zz_wp10_force(k) makes the auto-chosen menu item deterministic (the
##     k-th choice, clamped), so both sides of a choice are played.
##   - config.label_overrides sends `call combat(...)` to zz_wp10_combat, which
##     drives the real combat functions (combat_begin / combat_player /
##     combat_enemy), always answering the tell. The fight screen needs a
##     click, and its smoke_autoplay timer is WP2's.
##   - config.say_menu_text_filter records every line shown, to check what
##     the player reads.
##   - An overlay screen takes a screenshot while a menu is up (the scene's
##     staging plus the choices), for the shots listed at the end.

init 999 python:
    import builtins
    import os
    import re
    import time

    class ZZWP10State(builtins.object):
        def __init__(self):
            self.mc_seen = builtins.list()     # "file:line" where mc was showing
            self.labels = builtins.list()      # labels reached, in order
            self.texts = builtins.list()       # say and menu text shown
            self.combats = builtins.list()     # (enemy, outcome)
            self.snap = None                   # screenshot name, armed
            self.snapped = builtins.list()
            self.say_needle = None             # (needle, name): photograph that say line
            self.say_snap = None               # name, armed for the current say line
            self.say_t = 0.0
            self.menu_needle = None            # (needle, name): photograph that menu
            self.bounds = builtins.dict()      # say-shot name -> {tag: (x, y, w, h)}

    zz_wp10_state = ZZWP10State()

    WP10_FILES = ["events_arc1", "ch4_mission", "ch5_debrief", "missions_arc1",
                  "story_arc1", "story_kurose", "story_oda", "events_romance",
                  "events_activities", "events_stand", "events_intimate"]

    ## grep -c '^label' per file, on phase1 before WP10.
    WP10_LABELS_BEFORE = dict(events_arc1=27, ch4_mission=4, ch5_debrief=1,
        missions_arc1=3, story_arc1=8, story_kurose=2, story_oda=2,
        events_romance=3, events_activities=8, events_stand=1, events_intimate=4)

    ## Every flag("...") string in those files on phase1 before WP10.
    WP10_FLAGS_BEFORE = set("""
        accepted_sunmall aftermath_done annexe_cleared arc1_complete arc1_villain_revealed
        cartographer_seeded climax_strong climax_thin close_ confided_ end_committed
        end_honest end_turned_it_around first_day_asking fought_first found_nade_marks
        found_the_blotter found_the_phone gojo_purpose gojo_shoko gojo_test_fight
        gojo_test_measured gojo_test_retreat hard_lesson ignored_wall intensive_asked
        intensive_done intensive_tried kurose_argued kurose_asked_family kurose_asked_him
        kurose_card kurose_cold kurose_honest kurose_leak kurose_met kurose_read maki_hands
        maki_mai maki_positioning maki_reason maki_roster_open maki_truth megumi_demo
        megumi_philosophy megumi_sentence megumi_silence met_second_years mission_board_open
        nade_asked_direct nade_confronted_hard nade_map nade_named nade_prefigured nade_traced
        nobara_chose_you nobara_honest nobara_noticed nobara_philosophy nobara_saori
        nobara_scarf noise_front noise_read noise_reckless oda_answered oda_careful
        oda_corroborates oda_escalated oda_ignored oda_letter_read oda_recruited
        oda_thread_open oda_told_truth oda_warned_off panda_fear panda_named panda_named_her
        panda_origin panda_sisters panda_thanks read_wall roll_call rollcall_defiant
        rollcall_honest rollcall_tactical saori_resolved saved_civilian scouted_corridor
        shoko_emergency_contact shoko_geto shoko_lessons shoko_night shoko_open
        shoko_taught_limits shoko_weight shoko_worried storehouse_access strong_class
        sunmall_done suspected_grade talked_about_after_ toge_cost toge_learning toge_ridge
        toge_spoke told_gojo_wrong town_date_ tsumiki_lead tsumiki_promise visited_tsumiki
        wakuri_seeded warehouse_cleared warehouse_costly warehouse_withdrew
        will_remember_nobara will_speak_for_toge will_stand_with_maki yaga_asked_for_itadori
        yaga_blame yaga_blunt yaga_photo yaga_why yuji_afraid yuji_kindness yuji_number
        yuji_serious yuji_told_truth yuji_trained yuji_will_tell
    """.split())

    ## Removed by the spec itself (reported in WP10's result):
    ##   arc1_complete   story_arc1 5.4.2: `$ arc = 2` + `flag("arc1_complete")`
    ##                   become `flag("night_before_done")` (the night before
    ##                   Kyoto no longer ends the arc; migration 40 maps it)
    ##   found_the_phone missions_arc1 5.4.1: the Filament branch is deleted
    WP10_FLAGS_RETIRED = {"arc1_complete", "found_the_phone"}
    WP10_FLAGS_NEW = {"night_before_done", "recommended_g3"}

    ## The check_content.py rules (8.4), with their exemption tags.
    WP10_MC = re.compile(r"^\s*(show|hide)\s+mc\b")
    WP10_TECH = re.compile(r"filament|emberfall|aftersound|stillness", re.IGNORECASE)
    WP10_DEADLINE = re.compile(r"KYOTO_DAY|days_left\(|days until Kyoto|TO KYOTO|Three weeks from today"
                               r"|In three weeks|\barc\s*=\s*2\b|END OF ARC ONE")
    WP10_GREP = ["technique ==", "tname", "min_day", "arc = 2", "min(160", "min(140", "grade = "]

    def zz_wp10_read(name):
        with open(os.path.join(config.gamedir, name + ".rpy"), encoding="utf-8") as f:
            return f.read()

    ## --- scaffolding -----------------------------------------------------------

    def zz_wp10_force(k):
        """Auto-chosen menus pick choice k (clamped); None restores random."""
        r = renpy.random
        if k is None:
            r.__dict__.pop("choice", None)
        else:
            r.choice = lambda seq, _k=k: seq[min(_k, len(seq) - 1)]

    def zz_wp10_interact():
        if renpy.showing("mc"):
            zz_wp10_state.mc_seen.append("%s:%s" % renpy.get_filename_line())

    config.start_interact_callbacks.append(zz_wp10_interact)

    def zz_wp10_label_cb(name, abnormal):
        zz_wp10_state.labels.append(name)

    config.label_callbacks.append(zz_wp10_label_cb)

    _zz_wp10_prev_filter = config.say_menu_text_filter

    def zz_wp10_text(s):
        ## Called for every say and menu line, even while skipping (the
        ## start-interaction callback is not, under fast skip).
        zz_wp10_state.texts.append(s)
        zz_wp10_interact()
        if zz_wp10_state.menu_needle and zz_wp10_state.menu_needle[0] in s:
            zz_wp10_state.snap = zz_wp10_state.menu_needle[1]
            zz_wp10_state.menu_needle = None
            config.auto_choice_delay = 1.2
        if zz_wp10_state.say_needle and zz_wp10_state.say_needle[0] in s:
            ## Hold this one line on screen (skipping off) until the snapper
            ## has photographed it, then end it and fast-skip on.
            zz_wp10_state.say_snap = zz_wp10_state.say_needle[1]
            zz_wp10_state.say_needle = None
            zz_wp10_state.say_t = time.time()
            config.skipping = None
            zz_smoke_state.autoplay = False
        return _zz_wp10_prev_filter(s) if _zz_wp10_prev_filter else s

    config.say_menu_text_filter = zz_wp10_text

    def zz_wp10_try_snap():
        name = zz_wp10_state.say_snap
        if name and renpy.get_screen("say") and time.time() > zz_wp10_state.say_t + 1.2:
            zz_wp10_state.say_snap = None
            zz_wp10_state.bounds[name] = dict((t, renpy.get_image_bounds(t))
                for t in renpy.get_showing_tags() if t != "bg")
            if shot(name, wait=0):
                zz_wp10_state.snapped.append(name)
            zz_smoke_state.autoplay = True
            config.skipping = "fast"
            return True
        name = zz_wp10_state.snap
        if name and renpy.get_screen("choice"):
            zz_wp10_state.snap = None
            if shot(name, wait=0):
                zz_wp10_state.snapped.append(name)

    config.overlay_screens.append("zz_wp10_snapper")

    config.label_overrides["combat"] = "zz_wp10_combat"

    def zz_wp10_texts_since(n):
        return zz_wp10_state.texts[n:]

    def zz_wp10_saw(n, needle):
        return any(needle in t for t in zz_wp10_state.texts[n:])


screen zz_wp10_snapper():
    zorder 200
    if zz_wp10_state.snap or zz_wp10_state.say_snap:
        timer 0.1 repeat True action Function(zz_wp10_try_snap)


## The fight, without its screen: the real combat functions, always answering.
label zz_wp10_combat(enemy, ally=None, flee_ok=True, bg=None):
    $ combat_begin(enemy, ally, flee_ok, bg)
    python:
        _zz_n = 0
        while not cb["over"] and _zz_n < 80:
            _zz_n += 1
            if not combat_player(ANSWERS[cb["kind"]]):
                combat_enemy()
        if not cb["over"]:
            cb["over"] = "fled"
        zz_wp10_state.combats.append((enemy, cb["over"]))
    return cb["over"]


## Play one label under autoplay: k picks the menu choice (None = random);
## snap arms a screenshot at the first menu.
label zz_wp10_play(lbl, k=None, who=None, snap=None):
    scene black
    $ zz_wp10_state.snap = snap
    $ zz_wp10_force(k)
    $ autoplay()
    if snap:
        $ config.auto_choice_delay = 0.6
    if who is None:
        call expression lbl
    else:
        call expression lbl pass (who)
    $ autoplay(False)
    $ zz_wp10_force(None)
    python:
        if zz_wp10_state.snap:
            note("shot " + zz_wp10_state.snap, "no menu came up to photograph")
            zz_wp10_state.snap = None
        check(not renpy.showing("mc"), "%s: mc not showing at the end" % (lbl,))
    return


label zz_smoke:

    ## ================================================================ part 1
    python:
        _texts = dict((n, zz_wp10_read(n)) for n in WP10_FILES)

        _mc, _tech, _dead, _grep = [], [], [], []
        for n, t in sorted(_texts.items()):
            for i, line in enumerate(t.splitlines(), 1):
                where = "%s:%d" % (n, i)
                if WP10_MC.search(line) and "## first-person exception" not in line:
                    _mc.append(where)
                if WP10_TECH.search(line) and "# legacy-technique" not in line:
                    _tech.append(where)
                if WP10_DEADLINE.search(line):
                    _dead.append(where)
                for pat in WP10_GREP:
                    if pat in line:
                        _grep.append("%s %r" % (where, pat))
        check(not _mc, "static: no-mc-on-screen finds nothing", _mc)
        check(not _tech, "static: one-technique finds nothing", _tech)
        check(not _dead, "static: no-deadline finds nothing", _dead)
        check(not _grep, "static: no technique==/tname/min_day/arc = 2/min(160/min(140/grade = ", _grep)

        _bad = []
        for n, t in sorted(_texts.items()):
            c = len(re.findall(r"(?m)^label\b", t))
            if c != WP10_LABELS_BEFORE[n]:
                _bad.append("%s %d -> %d" % (n, WP10_LABELS_BEFORE[n], c))
        check(not _bad, "static: label count per file unchanged", _bad)

        _flags_now = set()
        for t in _texts.values():
            _flags_now |= set(re.findall(r'flag\(\s*"([^"]+)"', t))
        _lost = WP10_FLAGS_BEFORE - _flags_now
        check(_lost <= WP10_FLAGS_RETIRED, "static: every flag string is still present (except the two the spec retires)",
              sorted(_lost - WP10_FLAGS_RETIRED))
        note("flags retired by the spec", sorted(_lost))
        note("flags added", sorted(_flags_now - WP10_FLAGS_BEFORE))
        check(WP10_FLAGS_NEW <= _flags_now, "static: night_before_done and recommended_g3 are set somewhere")

    ## Registrations: min_day gone from every story/mission ev(), the two
    ## retired events unregistered, their labels kept.
    python:
        _ev = [e for e in EVENTS if e["kind"] in ("story", "mission")]
        _dated = [e["label"] for e in _ev if e.get("min_day", 0) or e.get("max_day", 9999) != 9999]
        _mine = set()
        for n in ("story_arc1", "story_kurose", "story_oda", "missions_arc1", "events_arc1"):
            _mine |= set(re.findall(r'ev\("(\w+)"', _texts[n]))
        check(not [l for l in _dated if l in _mine], "no story/mission ev() of WP10's has a min_day",
              [l for l in _dated if l in _mine])
        _labels_reg = set(e["label"] for e in EVENTS)
        check("st_board_open" not in _labels_reg and "ev_patrol" not in _labels_reg,
              "st_board_open and ev_patrol are not registered")
        check(renpy.has_label("st_board_open") and renpy.has_label("ev_patrol"),
              "st_board_open and ev_patrol labels still exist")
        for _l in ("st_roll_call", "st_noise", "st_second_years", "st_aftermath", "st_intensive",
                   "st_roster", "st_night_before", "st_kurose", "st_kurose_2", "st_oda_letter",
                   "st_oda_2", "ms_nade_1", "ms_nade_2", "ms_nade_3", "ev_mission_sunmall"):
            if _l not in _labels_reg:
                check(False, "%s is still registered" % _l)

    ## ================================================================ part 2
    ## A seeded store: after the prologue, second-years not met yet.
    python:
        settle(day=5, here="classroom", period="Morning", mc_name="Tester", mc_surname="Harness",
               roster=["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "ijichi"],
               bonds={"yuji": 12, "megumi": 8, "nobara": 6, "gojo": 6, "yaga": 5, "shoko": 4},
               arc=1, ce=60, ce_max=60, control=20, output=18, insight=20)
        for _f in ("dinner_listened", "listened_first", "gojo_asked_why", "chose_jujutsu",
                   "told_parents_truth", "took_photo", "enrolled", "yaga_honest", "first_day_asking"):
            flag(_f)
        _grade0 = grade
        note("grade before roll call", repr(_grade0))
        check(_grade0 != "g4", "grade is not the g4 key before roll call", repr(_grade0))

    ## --- st_roll_call ------------------------------------------------------------
    $ _n0 = len(zz_wp10_state.labels)
    $ _t0 = len(zz_wp10_state.texts)
    call zz_wp10_play("st_roll_call", 0, snap="roll_call_menu")
    python:
        check(grade == "g4", 'roll call: grade == "g4" afterwards', repr(grade))
        check("show_grade_card" in zz_wp10_state.labels[_n0:], "roll call: the grade card is shown (show_grade_card)")
        check(has_flag("roll_call") and has_flag("storehouse_access") and has_flag("rollcall_defiant"),
              "roll call: roll_call, storehouse_access and the first choice's flag")
        check(zz_wp10_saw(_t0, "Then I'd better start now."), "roll call: the new first choice")
        check(zz_wp10_saw(_t0, "Look, don't take."), "roll call: the storehouse line (D10)")
        check(zz_wp10_saw(_t0, "Kyoto's teacher arrives tomorrow"), "roll call: the board line names Kyoto's teacher")
        check(zz_wp10_saw(_t0, "stops on me"), "roll call: narration in the first person")
        check(not zz_wp10_saw(_t0, "three weeks") and not zz_wp10_saw(_t0, "Three weeks"),
              "roll call: no 'three weeks'")
    ## The other two choices play too.
    $ grade = _grade0
    call zz_wp10_play("st_roll_call", 1)
    $ check(has_flag("rollcall_honest") and grade == "g4", "roll call, second choice: flag and grade")
    call zz_wp10_play("st_roll_call", 2)
    $ check(has_flag("rollcall_tactical"), "roll call, third choice: flag")
    $ check(zz_wp10_saw(_t0, "Wrong day for it"), "roll call: 'Wrong day for it'")
    ## An old save parked on roll call's menu resumes after the promote: after
    ## migration 20 its grade is None and roll_call is unset. It still ends g4.
    python:
        _node = renpy.game.script.namemap["st_roll_call"]
        while _node is not None and not isinstance(_node, renpy.ast.Menu):
            _node = _node.next
        check(_node is not None, "roll call: its menu node found")
        _rc_menu = _node.name
        grade = None
        flags.discard("roll_call")
    call zz_wp10_play(_rc_menu, 1)
    $ check(grade == "g4", 'roll call resumed from its menu: grade == "g4" afterwards', repr(grade))
    $ check(has_flag("roll_call"), "roll call resumed from its menu: roll_call set")

    ## --- st_second_years, st_noise, st_aftermath ---------------------------------------
    $ period = "Afternoon"
    call zz_wp10_play("st_second_years", 0)
    $ check(has_flag("met_second_years") and "maki" in roster, "st_second_years: met, Maki recruited")
    call zz_wp10_play("st_second_years", 1)
    $ period = "Evening"
    $ here = "courtyard"
    call zz_wp10_play("st_noise")
    $ flag("sunmall_done")
    $ period = "Morning"
    call zz_wp10_play("st_aftermath")

    ## --- st_intensive: raise_reserve, both choices -----------------------------------------
    $ period = "Afternoon"
    $ ce_max = 60
    $ _t0 = len(zz_wp10_state.texts)
    call zz_wp10_play("st_intensive", 0, snap="intensive_menu")
    $ check(ce_max == 80 and has_flag("intensive_tried"), "st_intensive, try it: raise_reserve(20) (60 -> 80)", ce_max)
    $ ce_max = 60
    call zz_wp10_play("st_intensive", 1)
    $ check(ce_max == 72 and has_flag("intensive_asked"), "st_intensive, ask why: raise_reserve(12) (60 -> 72)", ce_max)
    $ check(has_flag("intensive_done"), "st_intensive: intensive_done")
    $ check(not zz_wp10_saw(_t0, "fortnight") and zz_wp10_saw(_t0, "one of these days"), "st_intensive: no fortnight, no 'in a week'")

    ## --- st_roster --------------------------------------------------------------------------------
    $ period = "Noon"
    $ _t0 = len(zz_wp10_state.texts)
    call zz_wp10_play("st_roster", 0, snap="roster_menu")
    call zz_wp10_play("st_roster", 1)
    python:
        check(zz_wp10_saw(_t0, "Not long now.") and zz_wp10_saw(_t0, "at noon one day"), "st_roster: no Thursday, no 'Four days'")
        check(not zz_wp10_saw(_t0, "four days"), "st_roster: no 'four days'")

    ## --- st_night_before: arc stays 1 ---------------------------------------------------------------
    $ period = "Evening"
    $ arc = 1
    $ _t0 = len(zz_wp10_state.texts)
    call zz_wp10_play("st_night_before")
    python:
        check(arc == 1, "st_night_before: arc == 1 afterwards", arc)
        check(has_flag("night_before_done"), "st_night_before: flag night_before_done")
        check(not has_flag("arc1_complete"), "st_night_before: no arc1_complete")
        ## (The card is a screen, shown during a pause that skipping passes
        ## over, so it is checked in the source.)
        _nb = _texts["story_arc1"].split("label st_night_before:")[1].split("\nlabel ")[0]
        check('chapter_card("THE NIGHT BEFORE", "Goodwill", "The Kyoto Goodwill Event — coming in a later build.")' in _nb
              and "END OF ARC ONE" not in _nb, "st_night_before: the card is THE NIGHT BEFORE / Goodwill")
    ## The quieter branch of the mcthink lines.
    python:
        _saved_threads = dict(threads)
        threads.clear()
    call zz_wp10_play("st_night_before")
    python:
        threads.update(_saved_threads)
        check(zz_wp10_saw(_t0, "I've spent almost all of my time here alone"), "st_night_before: the alone line, no 'three weeks'")
        check(arc == 1, "st_night_before (again): arc == 1", arc)

    ## --- chapter_four: both choices, Maki not in the roster -----------------------------------------
    python:
        if "maki" in roster:
            roster.remove("maki")
        bonds.pop("maki", None)
        tname = "sentinel"
        technique = "filament"
        _t0 = len(zz_wp10_state.texts)
    ## choice 0: read the wall, then go for her (partner Yuji)
    $ bonds["yuji"] = 30
    call zz_wp10_play("chapter_four", 0)
    $ check(has_flag("read_wall") and has_flag("saved_civilian"), "chapter_four, choice 0: read_wall + saved_civilian")
    ## choice 2 / 1: Last Light on the corridor, then kill it first (partner Megumi)
    $ bonds["megumi"] = 40
    $ _t1 = len(zz_wp10_state.texts)
    $ zz_wp10_state.say_needle = ("It is not a grade three.", "ch4_curse_reveal")
    $ zz_wp10_state.menu_needle = ("You have perhaps four seconds", "ch4_atrium_menu")
    call zz_wp10_play("chapter_four", 2, snap="ch4_corridor_menu")
    python:
        check("ch4_curse_reveal" in zz_wp10_state.snapped, "chapter_four: shot at 'It is not a grade three.'")
        check("ch4_atrium_menu" in zz_wp10_state.snapped, "chapter_four: shot at the atrium menu")
        _b = zz_wp10_state.bounds.get("ch4_curse_reveal", {})
        note("ch4 curse reveal bounds", repr(_b))
        _pb, _cb = _b.get("megumi"), _b.get("curse")
        check(_pb and _cb and (_pb[0] + _pb[2] / 2.0) < _cb[0] + _cb[2] * 0.25,
              "chapter_four: the partner stands clear of the curse (centre left of the curse's left quarter)", repr(_b))
    python:
        check(has_flag("scouted_corridor") and has_flag("fought_first"), "chapter_four, choice 2: scouted_corridor + fought_first")
        check("maki" not in bonds or bonds.get("maki", 0) == 0, "chapter_four: no Maki bond while she's not in the roster", bonds.get("maki"))
        check(zz_wp10_saw(_t1, "Hold the corridor with Last Light."), "chapter_four: the Last Light choice")
        check(zz_wp10_saw(_t1, "You hold the second and walk into it."), "chapter_four: the corridor passage")
        check(zz_wp10_saw(_t1, "It swings, and you stop the second on the swing."), "chapter_four: the fight-first passage")
        check(zz_wp10_saw(_t1, "The second stops."), "chapter_four: the climax passage")
        check(zz_wp10_saw(_t0, "You stop the atrium."), "chapter_four: the rescue passage")
        check(tname == "sentinel", "chapter_four no longer sets tname", tname)
    ## Maki in the roster: the bond is paid.
    python:
        roster.append("maki")
        bonds["maki"] = 10
        _m0 = bonds["maki"]
    call zz_wp10_play("chapter_four", 1)
    $ check(bonds.get("maki", 0) == _m0 + 4, "chapter_four, kill it first with Maki rostered: Maki +4", (_m0, bonds.get("maki")))
    ## Every partner through both branches.
    python:
        _partners = ["yuji", "megumi", "nobara"]
    python:
        _pi = 0
    while _pi < 3:
        $ _partner = _partners[_pi]
        call zz_wp10_play("ch4_save_first")
        $ _partner = _partners[_pi]
        call zz_wp10_play("ch4_fight_first")
        $ _pi += 1
    python:
        check(not zz_wp10_saw(_t0, "[tname]"), "chapter_four: no [tname] left")

    ## --- chapter_five: a recommendation, not a grade -------------------------------------------------
    python:
        grade = "g4"
        _merit0 = merit
        if not hasattr(store, "merit_granted"):
            store.merit_granted = set()
        merit_granted.discard("ch5_recommendation")
        _t0 = len(zz_wp10_state.texts)
    call zz_wp10_play("chapter_five", 0, snap="ch5_rooftop_menu")
    python:
        check(grade == "g4", "chapter_five: the grade is unchanged", repr(grade))
        check(merit == _merit0 + 20, "chapter_five: merit +20", (_merit0, merit))
        check(has_flag("recommended_g3"), "chapter_five: flag recommended_g3")
        check("ch5_recommendation" in merit_granted, "chapter_five: records ch5_recommendation")
        check(zz_wp10_saw(_t0, "I am putting your name forward for Grade 3."), "chapter_five: the recommendation line")
        check(not zz_wp10_saw(_t0, "Effective immediately") and not zz_wp10_saw(_t0, "fortnight"),
              "chapter_five: no promotion, no fortnight")
    call zz_wp10_play("chapter_five", 2)
    $ check(merit == _merit0 + 20, "chapter_five twice: merit paid once", (_merit0, merit))

    ## --- the whole Sun Mall, from Yaga's office ------------------------------------------------------------
    $ here = "office"
    call zz_wp10_play("ev_mission_sunmall")
    $ check(has_flag("sunmall_done") and here == "dorm", "ev_mission_sunmall plays through")

    ## --- Nade: the Last Light passages are unconditional ------------------------------------------------------
    python:
        technique = "filament"
        _t0 = len(zz_wp10_state.texts)
        del zz_wp10_state.combats[:]
    call zz_wp10_play("ms_nade_1", 0)
    python:
        check(has_flag("nade_named") and has_flag("found_nade_marks"), "ms_nade_1: nade_named, found_nade_marks (any technique)")
        check(zz_wp10_state.combats and zz_wp10_state.combats[0][0] == "warehouse", "ms_nade_1: the warehouse fight ran", zz_wp10_state.combats)
    call zz_wp10_play("ms_nade_2", 0)
    $ check(has_flag("nade_traced") and has_flag("found_the_blotter"), "ms_nade_2: nade_traced, found_the_blotter (any technique)")
    call zz_wp10_play("ms_nade_3", 1)
    $ check(has_flag("nade_map"), "ms_nade_3: nade_map")

    ## --- Kurose and Oda ---------------------------------------------------------------------------------------
    $ period = "Afternoon"
    call zz_wp10_play("st_kurose")
    $ period = "Evening"
    call zz_wp10_play("st_kurose_2")
    call zz_wp10_play("st_oda_letter")
    $ flag("oda_answered")
    call zz_wp10_play("st_oda_2")

    ## --- every hangout, re-staged ---------------------------------------------------------------------------------
    python:
        _hangouts = [l for l in re.findall(r"(?m)^label (ev_\w+):", _texts["events_arc1"])
                     if l not in ("ev_mission_sunmall", "ev_patrol")]
        _hi = 0
        _t0 = len(zz_wp10_state.texts)
        technique = "filament"
        for _w in ("yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "gojo", "yaga"):
            if _w not in roster:
                roster.append(_w)
    while _hi < len(_hangouts):
        $ _h = _hangouts[_hi]
        if _h == "ev_yuji_1":
            call zz_wp10_play(_h, 1, snap="hangout_yuji_menu")
        elif _h == "ev_yaga_1":
            call zz_wp10_play(_h, 1)
        else:
            call zz_wp10_play(_h, 0)
        $ _hi += 1
    python:
        check(len(_hangouts) == 25, "all 25 hangouts in events_arc1 played", len(_hangouts))
        check(zz_wp10_saw(_t0, "You hold a second, out of curiosity"), "ev_megumi_1: the Last Light text, whatever the technique")
        check(zz_wp10_saw(_t0, "a good deal less than that from being sent somewhere"), "ev_yaga_1: no 'three weeks'")

    ## --- acts: people stay on screen --------------------------------------------------------------------------------
    $ here = "cafeteria"
    $ period = "Noon"
    scene expression graded_bg()
    call stage_person("yuji")
    show yuji at pos_c
    with None
    $ autoplay()
    call act_eat("yuji")
    $ autoplay(False)
    python:
        check(renpy.showing("yuji"), "act_eat(\"yuji\"): Yuji is still on screen afterwards")
        check(not renpy.showing("mc"), "act_eat(\"yuji\"): mc not showing")
    $ shot("act_eat_yuji")

    python:
        _stay = [("act_stand", "yuji"), ("act_int_night", "nobara"), ("act_int_morning", "maki")]
        _show = [("act_swim", "megumi"), ("act_int_day", "shoko"), ("act_rom_town", "nobara")]
        _ai = 0
    while _ai < len(_stay):
        $ _lbl, _w = _stay[_ai]
        scene expression graded_bg()
        $ renpy.show(_w, at_list=[pos_c])
        $ autoplay()
        call expression _lbl pass (_w)
        $ autoplay(False)
        $ check(renpy.showing(_w), "%s(%r): the person is still on screen" % (_lbl, _w))
        $ check(not renpy.showing("mc"), "%s(%r): mc not showing" % (_lbl, _w))
        $ _ai += 1
    $ _ai = 0
    while _ai < len(_show):
        $ _lbl, _w = _show[_ai]
        scene black
        $ autoplay()
        call expression _lbl pass (_w)
        $ autoplay(False)
        $ check(renpy.showing(_w), "%s(%r): shows the person after its scene change" % (_lbl, _w))
        $ check(not renpy.showing("mc"), "%s(%r): mc not showing" % (_lbl, _w))
        $ _ai += 1
    $ shot("act_rom_town_end")

    ## ================================================================ verdicts
    python:
        check(not zz_wp10_state.mc_seen, "mc never showing, on any interaction", zz_wp10_state.mc_seen[:10])
        _techs = [t for t in zz_wp10_state.texts if WP10_TECH.search(t)]
        check(not _techs, "no line shown names Filament, Emberfall, Aftersound or Stillness", _techs[:5])
        _dl = [t for t in zz_wp10_state.texts if WP10_DEADLINE.search(t) or "three weeks from" in t.lower()]
        check(not _dl, "no line shown is a deadline", _dl[:5])
        check(arc == 1, "arc == 1 at the end", arc)
        note("combats", zz_wp10_state.combats)
        note("lines shown", len(zz_wp10_state.texts))
        note("shots", zz_wp10_state.snapped)

    $ finish()
