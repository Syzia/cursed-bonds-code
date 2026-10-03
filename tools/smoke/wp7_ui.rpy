## tools/smoke/wp7_ui.rpy -- WP7's harness: the HUD, toasts, place view,
## person view and loop (PHASE1_DESIGN.md, section 7, WP7 acceptance).
##
##   tools/smoke.sh tools/smoke/wp7_ui.rpy
##
## Checks every WP7 acceptance bullet by name, plus the task list: once-a-day
## actions, staging during activities, Gojo's lesson, the loop's new branches
## (driven through the real `sandbox` loop by an overlay that answers its
## screens), the objective toast, the arrival caption and the tables'
## validator. Screenshots go to shots/wp7_ui/.
##
## Phase 2 (P2, PHASE2_DESIGN.md 4.2, 4.4, 4.6): the HUD's three buttons are
## icons, what I can do in a room is an icon column (rail_rows), and the person
## view shows a grade chip and the choices only; the checks below read button
## ids and hover labels where they used to read words. tools/smoke/p2_hud.rpy
## holds P2's own acceptance.
##
## Other packages' functions are the WP0 stubs here; where a check needs one to
## say yes (a mission, the board, Gojo's in-day), the harness swaps in a
## stand-in for that check only and puts the original back.

init 999 python:
    import os

    ZZ_LABELS = []          # labels entered, in order (config.label_callbacks)
    ZZ_SHOWING = []         # (scene label, watched person showing?) as each scene starts
    ZZ_WATCH = [None]       # whose sprite ZZ_SHOWING watches
    ZZ_DRIVE = []           # what the driver answers the loop's screens with
    ZZ_DRIVE_LOG = []
    ZZ_CALLS = []           # record_act / train_together / raise_reserve, as recorded

    def zz_label_cb(name, abnormal):
        ZZ_LABELS.append(name)
        ## Is the watched person on screen as the scene itself starts? (Fast
        ## skipping never displays say lines, so they can't be watched.)
        if ZZ_WATCH[0] and (name == "sb_smalltalk" or name.startswith("act_")):
            ZZ_SHOWING.append((name, renpy.showing(ZZ_WATCH[0])))

    config.label_callbacks.append(zz_label_cb)

    ## zz_texts(screen) is the library's (tools/smoke/_lib.rpy).

    def zz_has_text(screen_name, s):
        return any(s in t for t in zz_texts(screen_name))

    def zz_tip(screen_name, wid):
        """The hover label (text, key) of the button with `id wid`, or None."""
        d = renpy.get_displayable(screen_name, wid, base=True) or renpy.get_displayable(screen_name, wid)
        try:
            return d._get_tooltip() if d is not None else None
        except Exception:
            return None

    def zz_swap(name, fn):
        """Replace a store function; returns the original."""
        old = getattr(store, name)
        setattr(store, name, fn)
        return old

    ## The driver: an overlay that answers the loop's screens, one step at a
    ## time, so the real `sandbox` loop runs its dispatch.
    ZZ_LOOP_SCREENS = ("sb_place", "sb_char", "sb_map", "journal")

    def zz_drive():
        if not ZZ_DRIVE:
            return None
        want, value = ZZ_DRIVE[0]
        if not renpy.get_screen(want):
            return None
        ZZ_DRIVE.pop(0)
        ZZ_DRIVE_LOG.append((want, value))
        if value == "finish":
            renpy.jump("zz_after_loop")
        return value

    config.overlay_screens.append("zz_driver")

    ## A mission record for the checks that need one (3.6's record format).
    ZZ_MISSION = dict(id="m_sunmall", title="The Sun Mall", objective="Yaga has a mission for the first-years",
                      kind="story")

    ZZ_PROTECTED = [
        "call screen sb_place", "$ _r = _return", "call screen sb_map", "$ _m = _return",
        "call screen sb_char(who)", "$ _p = _return", "call sb_activity(_p[1], _p[2])",
        "call play_event(_story)", 'call expression "sb_do_" + _r[1]',
        'call expression "act_" + aid pass (who)',
    ]


screen zz_driver():
    zorder 200
    if ZZ_DRIVE:
        timer 0.35 repeat True action Function(zz_drive)


label zz_smoke:

    python:
        settle(mc_name="Tester", mc_surname="Harness", day=1, period="Morning", here="courtyard")
        for _f in ("dinner_listened", "chose_jujutsu", "enrolled", "storehouse_access"):
            flag(_f)

    ## --- static: the loop file (task 4) -------------------------------------------
    python:
        _src = open(os.path.join(config.gamedir, "sb_loop.rpy"), encoding="utf-8").read()
        _lines = [l.strip() for l in _src.splitlines()]
        check("$ quick_menu = False" not in _lines, "sb_loop no longer sets quick_menu = False")
        _miss = [p for p in ZZ_PROTECTED if p not in _lines]
        check(not _miss, "protected loop statements are textually intact (2.1.1)", _miss)
        _sa = _src[_src.index("label sb_activity"):_src.index("label sb_do_wait")]
        check('"""' not in _sa, "sb_activity has no docstring said as a line")
        check(renpy.has_label("sb_do_temper") and renpy.has_label("sb_do_missions") and renpy.has_label("sb_patrol"),
              "retired labels kept (D31, 2.1.2)")
        check(renpy.has_label("sb_do_release") and renpy.has_label("act_lesson") and renpy.has_label("stage_person"),
              "new labels exist")
        check(_validate_wp7_tables() == [], "WP7 validator: AMBIENT / PLACE_STAGING / faces are valid", _validate_wp7_tables())

    ## --- acceptance: place_actions ---------------------------------------------------
    python:
        _places = list(LOCATIONS) + [p for p in ("utahime_office", "gojo_office") if p not in LOCATIONS]
        _bad = []
        for _pl in _places:
            _ids = [a[0] for a in place_actions(_pl)]
            if "temper" in _ids or "missions" in _ids:  # legacy-technique (the retired forge)
                _bad.append((_pl, _ids))
            if not _ids or _ids[-1] != "wait":
                _bad.append((_pl, "wait not last", _ids))
        check(not _bad, "place_actions has no temper or missions anywhere, Wait last", _bad)
        if not any(a["id"] == "board" for a in PLACE_ACTIONS):
            register_place_action("board", "Mission board", "Graded jobs. Bring someone.",
                                  locs=("utahime_office", "office"), when="board_open")
            note("board", "registered a stand-in for WP4's board action")
        _old = zz_swap("board_open", lambda: True)
        check("board" in [a[0] for a in place_actions("utahime_office")], "place_actions includes board at utahime_office when open")
        zz_swap("board_open", lambda: False)
        check("board" not in [a[0] for a in place_actions("utahime_office")], "no board when it's closed")
        zz_swap("board_open", _old)
        _ids = [a[0] for a in place_actions("storehouse")]
        check("tools" in _ids and dict((a[0], a[1]) for a in place_actions("storehouse"))["tools"] == "Look through the racks",
              "storehouse offers Look through the racks", _ids)
        flag("armory_open")
        check("tools" not in [a[0] for a in place_actions("storehouse")], "racks give way to the armory once armory_open")
        flags.discard("armory_open")
        check("hold" in [a[0] for a in place_actions("dorm")], "Hold the hour offered everywhere")
        _lbl = dict((a[0], a[1]) for a in place_actions("courtyard"))
        check(_lbl.get("train") == "Practice", "courtyard: train shows as Practice", _lbl)
        explore_mode = True
        _ids = [a[0] for a in place_actions("courtyard")]
        check(_ids[0] == "explore_time" and "wait" not in _ids, "explore mode: Time only (plus explore actions)", _ids)
        explore_mode = False

    ## --- acceptance: person_choices over everyone x every place x every period -------
    python:
        _roster0 = list(roster)
        for _w in ROSTER_ORDER:
            if _w not in roster:
                roster.append(_w)
        _old_gojo = zz_swap("gojo_in_today", lambda: True)
        _old_mw = zz_swap("missions_with", lambda who, loc=None: [ZZ_MISSION] if who == "yaga" else [])
        _old_car = zz_swap("car_action_ok", lambda: True)
        _old_bo = zz_swap("board_open", lambda: True)
        _problems = []
        _count = 0
        _seen_kinds = set()
        _seen_ids = set()

        def _zz_valid(ch, who, loc):
            if ch["kind"] == "do":
                return activity_state(ACT_BY_ID[ch["id"]], who, loc)[0]
            if ch["kind"] == "mission":
                return ch["id"] in [mission_view(m)[0] for m in missions_with(who, loc)]
            if ch["kind"] == "act":
                return ch["id"] in ("board", "car")
            return False

        for _fx in ("fresh", "rich"):
            if _fx == "fresh":
                bonds = {w: 0 for w in roster}
                affection = {w: 0 for w in roster if is_romanceable(w)}
                together = []
            else:
                bonds = {w: 100 for w in roster}
                affection = {w: 100 for w in roster if is_romanceable(w)}
                together = ["maki"]
                affection["maki"] = 160
                flag("confided_yuji")
            spent_today = set()
            actions_today = set()
            stamina = stamina_max
            for _who in roster:
                for _pl in _places:
                    for _per in PERIODS:
                        period = _per
                        _cs = person_choices(_who, _pl)
                        _count += 1
                        _ids = [c["id"] for c in _cs]
                        _seen_ids.update(_ids)
                        _seen_kinds.update(c["kind"] for c in _cs)
                        if not (1 <= len(_cs) <= 4):
                            _problems.append(("count", _fx, _who, _pl, _per, _ids))
                        if _cs[-1]["id"] != "talk" or _ids.count("talk") != 1:
                            _problems.append(("talk last", _fx, _who, _pl, _per, _ids))
                        if "invite" in _ids:
                            _problems.append(("invite is the footer", _fx, _who, _pl, _per, _ids))
                        for _c in _cs:
                            if not _zz_valid(_c, _who, _pl):
                                _problems.append(("unavailable", _fx, _who, _pl, _per, _c["id"]))
                            if not {"kind", "id", "label", "hint", "cost", "gold", "romance"} <= set(_c):
                                _problems.append(("shape", _c))
        check(not _problems, "person_choices: <= 4, ends with talk, only available ones (%d cases)" % _count, _problems[:8])
        note("person_choices ids seen", sorted(_seen_ids))
        check({"do", "mission", "act"} <= _seen_kinds, "person_choices produced do, mission and act entries", _seen_kinds)
        check({"lesson", "board", "car", "rom_say", "stand", "eat", "train", "talk"} <= _seen_ids,
              "the ranking reaches the lesson, board, car, a milestone and place activities", sorted(_seen_ids))

        ## A few exact rankings.
        period = "Noon"
        bonds["yaga"] = 30
        _cs = person_choices("yaga", "office")
        check(_cs[0]["kind"] == "mission" and _cs[0]["gold"] and _cs[0]["label"] == "The Sun Mall",
              "a mission comes first, in gold", _cs)
        _cs = person_choices("gojo", "gojo_office")
        check([c["id"] for c in _cs][0] == "lesson", "Gojo in his office on an in-day offers the lesson first", [c["id"] for c in _cs])
        _cs = person_choices("ijichi", "gate")
        check(_cs[0]["id"] == "car" and _cs[0]["kind"] == "act", "Ijichi at the gate offers the car", [c["id"] for c in _cs])
        _cs = person_choices("utahime", "utahime_office")
        check(_cs[0]["id"] == "board" and _cs[0]["kind"] == "act", "Utahime at her office offers the board", [c["id"] for c in _cs])
        ## WP11 (WP5-h2): confide and stand only for the nine who have scenes.
        _cf = {w: [a["id"] for a, ok, why in activities_for(w, "office")] for w in ("ijichi", "utahime", "yaga")}
        check(not ({"confide", "stand"} & set(_cf["ijichi"] + _cf["utahime"])) and "confide" in _cf["yaga"],
              "at bond 100, Ijichi and Utahime get no confide/stand (they'd play Yaga's lines); Yaga does", _cf)
        ## WP11 (WP7-h11): the offices are real places now; no stand-in list.
        check({"gojo_office", "utahime_office"} <= set(LOCATIONS) and not hasattr(store, "_WP7_NEW_PLACES"),
              "both offices are in LOCATIONS; the WP7 stand-in list is gone")
        bonds = {w: 12 for w in roster}
        affection = {w: 0 for w in roster if is_romanceable(w)}
        together = []
        flags.discard("confided_yuji")
        _cs = person_choices("yuji", "cafeteria")
        check([c["id"] for c in _cs][-2:] == ["eat", "talk"] and len(_cs) <= 4,
              "Yuji at noon in the cafeteria: (a bond scene,) Eat together, Talk", [c["id"] for c in _cs])
        actions_today.add("lesson")
        check("lesson" not in [c["id"] for c in person_choices("gojo", "gojo_office")], "the lesson is once a day")
        actions_today.discard("lesson")
        zz_swap("gojo_in_today", lambda: False)
        check("lesson" not in [c["id"] for c in person_choices("gojo", "gojo_office")], "no lesson when Gojo isn't in")
        zz_swap("gojo_in_today", _old_gojo)
        zz_swap("missions_with", _old_mw)
        zz_swap("car_action_ok", _old_car)
        zz_swap("board_open", _old_bo)
        roster[:] = _roster0
        bonds = {}
        affection = {}
        spent_today = set()
        actions_today = set()
        period = "Morning"

    ## --- acceptance: toasts ---------------------------------------------------------------
    python:
        check(TOAST_SINK[0] is toast_push, "toast_push is the sink (TOAST_SINK[0])")
        toast_clear()
        for _i in range(8):
            renpy.notify("Notice %d" % (_i + 1))
        _texts = [t["text"] for t in TOASTQ.items]
        check(_texts == ["Notice %d" % (i + 1) for i in range(8)], "8 rapid renpy.notify calls all queue, in order", _texts)
        check([t["text"] for t in toast_visible()] == ["Notice 1", "Notice 2", "Notice 3", "Notice 4"],
              "four visible at once, oldest on top", [t["text"] for t in toast_visible()])
        for _t in TOASTQ.items[:4]:
            _t["t_shown"] -= TOAST_LIFE + 0.1
        toast_tick()
        check([t["text"] for t in toast_visible()] == ["Notice 5", "Notice 6", "Notice 7", "Notice 8"],
              "the next four show when the first expire; none dropped", [t["text"] for t in TOASTQ.items])
        toast_clear()
        ## While skipping, a backlog would trickle over later screens for
        ## minutes (the trial merge saw day 2's roll-call merit on day 6):
        ## only the newest four are kept then, all showing.
        _sk = config.skipping
        config.skipping = "fast"
        try:
            for _i in range(12):
                toast("Skipped %d" % (_i + 1), "grade")
            _sk_push = [t["text"] for t in TOASTQ.items]
            _sk_vis = [t["text"] for t in toast_visible()]
            config.skipping = None
            toast_clear()
            for _i in range(10):
                toast("Queued %d" % (_i + 1))
            config.skipping = "fast"
            toast_tick()
            _sk_tick = [t["text"] for t in toast_visible()]
        finally:
            config.skipping = _sk
        check(_sk_push == ["Skipped %d" % i for i in range(9, 13)] and _sk_vis == _sk_push,
              "while skipping, only the newest four toasts are kept, all showing", (_sk_push, _sk_vis))
        check(_sk_tick == ["Queued %d" % i for i in range(7, 11)],
              "a backlog queued before skipping began is cut to the newest four once it does", _sk_tick)
        toast_clear()
        add_bond("yuji", 2)
        add_bond("yuji", 2)
        _b = [t for t in TOASTQ.items if t["kind"] == "bond"]
        check(len(_b) == 1 and _b[0]["amount"] == 4 and _b[0]["text"] == "Yuji  bond +4",
              "two add_bond(yuji, 2) merge into +4", [(t["kind"], t["text"]) for t in TOASTQ.items])
        _age = _hud_time.time() - _b[0]["t_shown"]
        _fx = Transform()
        _toast_fx_fn(_b[0])(_fx, 0, 0)
        check(_age >= TOAST_FADE - 0.01 and _fx.alpha == 1.0 and _fx.xoffset == 0,
              "a merge restarts the toast's life without replaying its slide-in", (_age, _fx.alpha, _fx.xoffset))
        toast_clear()
        roster.append("maki")
        affection["maki"] = 10
        bonds["maki"] = 60
        add_aff("maki", 2)
        add_aff("maki", 1)
        _b = [t for t in TOASTQ.items if t["kind"] == "aff"]
        check(len(_b) == 1 and "+3" in _b[0]["text"], "affection gains merge too", [t["text"] for t in TOASTQ.items])
        add_bond("megumi", 3)
        add_bond("yuji", 1)
        check([t["kind"] + ":" + str(t["who"]) for t in TOASTQ.items][-2:] == ["bond:megumi", "bond:yuji"],
              "different people don't merge")
        check(toast_style(TOASTQ.items[-1])[1] == CAST["yuji"]["color"], "a bond toast wears the person's colour")
        check(toast_style(dict(kind="stat", who=None))[1] == gui.violet and toast_style(dict(kind="grade", who=None))[1] == gui.gold,
              "kinds are colour-coded")
        toast_clear()
        renpy.notify(u"New thread — Somebody Remembered")
        renpy.notify(u"Somebody Remembered — advanced")
        renpy.notify("Control +2")
        renpy.notify(u"Technique advanced — Held Breath")
        renpy.notify("Saved.")
        _k = [t["kind"] for t in TOASTQ.items]
        check(_k == ["thread", "thread", "stat", "stat", "info"],
              "renpy.notify sorts thread news (糸) and stat gains (術) from plain notices", _k)
        toast_clear()
        store._in_replay = "zz"
        _n = len(TOASTQ.items)
        toast("muted in replay")
        store._in_replay = None
        check(len(TOASTQ.items) == _n, "no toasts during a replay")
        roster.remove("maki")
        toast_clear()

        ## WP11 (WP9-h6): the prologue's blackout holds toasts; they wait.
        toast("Before the dark")
        check(len(toast_visible()) == 1, "a toast shows before the blackout")
        hide_side_images = True
        toast("In the dark")
        toast_tick()
        check(toast_visible() == [] and all(t["t_shown"] is None for t in TOASTQ.items),
              "blackout: no toast shows, and every clock stops (a shown one too)", TOASTQ.items)
    $ renpy.pause(TOAST_LIFE + 0.4, hard=True)
    python:
        check([t["text"] for t in TOASTQ.items] == ["Before the dark", "In the dark"] and not zz_texts("toasts"),
              "blackout: after a toast's lifetime both still wait, and nothing draws", ([t["text"] for t in TOASTQ.items], zz_texts("toasts")))
        hide_side_images = False
        toast_tick()
        check([t["text"] for t in toast_visible()] == ["Before the dark", "In the dark"],
              "after the blackout both show, with a full turn", [t["text"] for t in toast_visible()])
        toast_clear()

    ## --- the place view with four people (acceptance), toasts on top ----------------------
    python:
        roster.append("panda")
        day = 1
        period = "Evening"
        here = "dorm_common"
        stamina = 20
        _on, _extra = stage_people(here)
        check(len(_on) == 4 and not _extra, "four people in the Dorm Common Room on a weekday evening", (_on, _extra))
        toast("Yuji  bond +4", "bond", "yuji", 4)
        toast("Merit +30 — The Sun Mall", "grade")
        toast("Paper Ward", "item")
        toast("Control is at the Grade 4 limit — a promotion lifts it", "stat")
    scene expression graded_bg()
    show screen sb_place
    $ shot("place_four_people", wait=0.6)
    python:
        _t = zz_texts("sb_place")
        _names = [CAST[w]["short"] for w in _on]
        check(all(any(n in s for s in _t) for n in _names), "sb_place renders four people with nameplates", _t)
        _caps = [ambient_of(w, here)[0] for w in _on]
        check(any("on her phone" in s for s in _t), "nameplates carry what they're doing", _caps)
        check(any("Dorm Common Room" in s for s in _t), "the arrival caption names the place")
        check(zz_rect("sb_place", "hud_chip_stamina") is not None
              and zz_tip("sb_place", "hud_chip_stamina") == ("Running on empty. Eat or sleep.", "hud_chip_stamina")
              and not any("running on empty" in s for s in _t),
              "below 25 stamina the running-on-empty chip sits by the date (phase 2: no longer a line)")
        check(all(zz_rect("sb_place", w) is not None for w in ("hud_map", "hud_journal", "hud_menu"))
              and not any(s in ("MAP", "JOURNAL", "MENU") for s in _t),
              "the place view's HUD: Map, Journal, Menu, as icons (phase 2)")
        check(not any("STATUS" in s or "SAVE" == s or "CURSED ENERGY" in s for s in _t), "the old HUD readouts are gone")
        check(any("Day 1 · Monday" in s for s in _t), "the date chip reads Day 1 · Monday")
        check(zz_rect("sb_place", "rail_wait") is not None and (zz_tip("sb_place", "rail_wait") or ("",))[0].startswith("Wait\n"),
              "Wait is in the icon column (phase 2), named by its hover label", zz_tip("sb_place", "rail_wait"))
        check(bool(renpy.get_screen(("sandbox", "menu"))) and not (quick_menu and not renpy.get_screen(("sandbox", "menu"))),
              "renpy.get_screen((sandbox, menu)) hides the quick menu over the place view")
        _t0 = arrival_caption()
        check(_t0 is not None and arrival_caption() == _t0, "the arrival caption shows once per (day, period, here)")
    $ renpy.pause(3.6, hard=True)
    python:
        check(arrival_caption() is None, "the arrival caption fades after about 3 s")
        check(len(toast_visible()) == 0, "toasts expire on their own", [t["text"] for t in TOASTQ.items])
        roster.append("toge")
        stamina = stamina_max
    hide screen sb_place
    show screen sb_place
    $ shot("place_overflow", wait=0.4)
    python:
        _on, _extra = stage_people(here)
        check(len(_on) == 4 and _extra == ["toge"], "a fifth person goes to the +N chip", (_on, _extra))
        check(any(s == "+1" for s in zz_texts("sb_place")), "the +1 chip shows")
        check(zz_rect("sb_place", "hud_chip_stamina") is None, "no running-on-empty chip at full stamina")
        roster.remove("toge")
        companion = "nobara"
        _on, _extra = stage_people(here)
        check(_on[0] == "nobara", "the companion stands first", _on)
    hide screen sb_place
    show screen sb_place
    $ shot("place_companion", wait=0.3)
    python:
        check(zz_rect("sb_place", "rail_release") is not None and rail_rows(here)[-1][0] == ("act", "release")
              and zz_tip("sb_place", "rail_release") == ("Let them go\nThey go back to their own day.", "rail_release"),
              "with a companion, 'Let them go' is the column's last tile (phase 2)", zz_tip("sb_place", "rail_release"))
        companion = None
        here = "office"
        period = "Morning"
        _old_mh = zz_swap("missions_here", lambda loc: [ZZ_MISSION] if loc == "office" else [])
        _old_mw = zz_swap("missions_with", lambda who, loc=None: [ZZ_MISSION] if who == "yaga" else [])
    hide screen sb_place
    scene expression graded_bg()
    show screen sb_place
    $ shot("place_mission", wait=0.4)
    python:
        _t = zz_texts("sb_place")
        check(zz_rect("sb_place", "rail_m_m_sunmall") is not None and rail_rows(here)[0][:3] == (("mission", "m_sunmall"), "mission", True)
              and (zz_tip("sb_place", "rail_m_m_sunmall") or ("",))[0].startswith("The Sun Mall\n"),
              "a mission is the column's first tile, gold (phase 2)", (rail_rows(here)[0], zz_tip("sb_place", "rail_m_m_sunmall")))
        check(any(u"「!」" in s for s in _t), "the giver's nameplate shows the 「!」 badge")
        zz_swap("missions_here", _old_mh)
        zz_swap("missions_with", _old_mw)
        here = "riverside"
        period = "Night"
    hide screen sb_place
    scene expression graded_bg()
    show screen sb_place
    $ shot("place_empty", wait=0.4)
    python:
        check(not stage_people(here)[0] and "Nobody here right now." in zz_texts("sb_place"),
              "an empty place says nobody is here, and no more than that (phase 2)", zz_texts("sb_place"))
    hide screen sb_place

    ## --- the person view ---------------------------------------------------------------------
    python:
        here = "cafeteria"
        period = "Noon"
        bonds["yuji"] = 47
        spent_today = set()
    scene expression graded_bg()
    show screen sb_char("yuji")
    $ shot("person_yuji", wait=0.6)
    python:
        _t = zz_texts("sb_char")
        check(not any("Yuji" in s for s in _t), "sb_char no longer shows the name (phase 2, D19)", _t)
        check("GRADE 4" in _t and not any("First-year" in s for s in _t),
              "sb_char shows the grade as a chip, not the role line", _t)
        check(zz_rect("sb_char", "sb_char_invite") is not None
              and (zz_tip("sb_char", "sb_char_invite") or ("",))[0].startswith("Ask them along\n"),
              "the invite button is in the footer", zz_tip("sb_char", "sb_char_invite"))
        check(not any(s.startswith("Closer:") for s in _t) and not any(s in ("BOND", "AFFECTION") for s in _t),
              "no Closer hint and no bond bar on the card (they are on the journal page)", _t)
        check(zz_rect("sb_char", "hud_menu") is not None and zz_rect("sb_char", "hud_map") is None
              and zz_rect("sb_char", "hud_journal") is None, "the person view's HUD: date and Menu")
        check(any("Eat together" in s for s in _t) and any(s == "Talk" for s in _t), "the choices are drawn")
        check(zz_tip("sb_char", "sb_char_%d" % (len(person_choices("yuji", here)) - 1)) == ("Talk\nA few minutes. Costs nothing.", "sb_char_%d" % (len(person_choices("yuji", here)) - 1)),
              "a choice's hint is its hover label")
        bonds["nobara"] = 70
        affection["nobara"] = 55
    hide screen sb_char
    scene expression graded_bg()
    show screen sb_char("nobara")
    $ shot("person_nobara", wait=0.6)
    python:
        check(not any("AFFECTION" in s for s in zz_texts("sb_char")), "no affection meter on the card either (phase 2)")
    hide screen sb_char
    python:
        here = "infirmary"
        period = "Morning"
    scene expression graded_bg()
    show screen sb_char("shoko")
    $ shot("person_shoko", wait=0.5)
    python:
        check("DOCTOR" in zz_texts("sb_char"), "the ungraded show their role in a plain chip (DOCTOR)", zz_texts("sb_char"))
    hide screen sb_char

    ## --- the person view's worst case: it must fit on screen, Back included ----------------
    python:
        here = "cafeteria"
        period = "Noon"
        bonds["nobara"] = 72
        affection["nobara"] = aff_cap("nobara")
        _ntid = next(t for t in THREAD_ORDER if THREADS[t]["who"] == "nobara")
        threads[_ntid] = 1
        spent_today = set()
        _zz_tall = dict(id="m_nobara_tall", title="Nobara's errand in Harajuku",
                        objective=("She wants backup for something she refuses to explain until we're on the train, "
                                   "and she has already bought both tickets, which is its own kind of answer."))
        _old_mw = zz_swap("missions_with", lambda who, loc=None: [_zz_tall] if who == "nobara" else [])
        _cs = person_choices("nobara", here)
        note("tall card choices", [c["id"] for c in _cs])
        check(len(_cs) == 4 and _cs[0]["kind"] == "mission", "the worst case has a mission and four choices", [c["id"] for c in _cs])
    scene expression graded_bg()
    show screen sb_char("nobara")
    $ shot("person_tall_nobara", wait=0.8)
    python:
        _back = zz_rect("sb_char", "sb_char_back")
        _fs = [f for f in renpy.display.focus.focus_list if f.widget is not None and f.x is not None]
        check(_back and _back[1] + _back[3] <= 1060, "the tallest person card keeps Back on screen (ends above y 1060)", _back)
        _low = max([f.y + f.h for f in _fs if f.screen is not None and f.screen.screen_name[0] == "sb_char"] or [0])
        check(_low <= 1060, "every button on the tallest card is on screen", _low)
        check(not any("know them better" in s for s in zz_texts("sb_char")),
              "the affection row and its cap note are off the card (phase 2: the journal page has them)")
    hide screen sb_char
    ## Toasts over the person view: two at a time, beside MENU, above the card.
    ## Four already showing on campus: the two it hides wait, and none is lost.
    python:
        toast_clear()
        for _i in range(4):
            toast("Card notice %d" % (_i + 1))
        check(len(toast_visible()) == 4, "four toasts up on campus", [t["text"] for t in toast_visible()])
        _zz_seen = set(t["text"] for t in toast_visible())
    show screen sb_char("nobara")
    python:
        toast_tick()
        check([t["text"] for t in toast_visible()] == ["Card notice 1", "Card notice 2"],
              "over the person view, two toasts at a time", [t["text"] for t in toast_visible()])
        check(all(t["t_shown"] is None for t in TOASTQ.items[2:]),
              "the toasts the person view hides stop their clocks and wait", [t["t_shown"] for t in TOASTQ.items])
    $ shot("person_tall_toasts", wait=0.5)
    python:
        for _t in TOASTQ.items[:2]:
            _t["t_shown"] -= TOAST_LIFE + 0.1
        toast_tick()
        _zz_seen.update(t["text"] for t in toast_visible())
        check([t["text"] for t in toast_visible()] == ["Card notice 3", "Card notice 4"],
              "then the waiting two show over the card", [t["text"] for t in toast_visible()])
    hide screen sb_char
    python:
        toast_tick()
        _zz_seen.update(t["text"] for t in toast_visible())
        check(_zz_seen == set("Card notice %d" % (i + 1) for i in range(4)) and len(toast_visible()) == 2,
              "every toast gets its full turn; none is lost to the person view", (sorted(_zz_seen), [t["text"] for t in TOASTQ.items]))
        for _i in range(3):
            toast("Late notice %d" % (_i + 1))
        toast_tick()
        check(len(toast_visible()) == 4, "back on campus, four at a time again", [t["text"] for t in toast_visible()])
        toast_clear()
        zz_swap("missions_with", _old_mw)
        del threads[_ntid]
        ## At the confession ceiling the card doesn't say "know them better".
        here = "rooftop"
        period = "Evening"
        bonds["nobara"] = 90
        affection["nobara"] = 100
        together = []
        spent_today = set()
        stamina = stamina_max
        check(confession_ready("nobara"), "fixture: Nobara is ready for the confession")
    scene expression graded_bg()
    show screen sb_char("nobara")
    $ shot("person_confession_ready", wait=0.5)
    python:
        _t = zz_texts("sb_char")
        check(any(u"Say it" in s for s in _t) and not any("know them better" in s or "the rest is up to me" in s for s in _t),
              "at the ceiling the card offers Say it, with no affection notes (phase 2)", [s for s in _t if "Say" in s])
    hide screen sb_char
    python:
        bonds["nobara"] = 0
        affection["nobara"] = 0
        ## Panda's courtyard caption names Toge, so it needs Toge there (4.4).
        _r0 = list(roster)
        for _w in ("panda", "toge"):
            if _w not in roster:
                roster.append(_w)
        period = "Morning"
        check("toge" not in who_is_here("courtyard"), "fixture: Toge isn't in the courtyard on a morning")
        check(ambient_of("panda", "courtyard")[0] == "waiting for a sparring partner",
              "Panda in the courtyard without Toge is waiting for a sparring partner", ambient_of("panda", "courtyard"))
        pin("toge", "courtyard")
        check(ambient_of("panda", "courtyard")[0] == "sparring with Toge",
              "with Toge there, Panda is sparring with Toge", ambient_of("panda", "courtyard"))
        schedule_overrides.pop(("toge", day, period), None)
        roster[:] = _r0

    ## --- the map's HUD ----------------------------------------------------------------------
    show screen sb_map
    $ shot("map_hud", wait=0.3)
    python:
        check(zz_rect("sb_map", "hud_menu") is not None and zz_rect("sb_map", "hud_map") is None
              and zz_rect("sb_map", "hud_journal") is None, "the map's HUD: date and Menu (D33)")
    hide screen sb_map

    ## --- the objective toast, and the arrival caption it waits for ---------------------------
    python:
        _old_ot = zz_swap("objective_text", lambda: "Roll call with Principal Yaga — Classroom Building, mornings")
        last_objective = None
        here = "office"
        period = "Morning"
        day = 2
        ## As the loop does it: check_objective(), then the place view.
        check_objective()
        check(renpy.get_screen("objective_toast") is not None and last_objective.startswith("Roll call"),
              "check_objective shows the new objective and remembers it")
    scene expression graded_bg()
    show screen sb_place
    $ shot("arrival_plus_objective", wait=0.8)
    python:
        _t0 = arrival_caption()
        _left = ARRIVAL[1] + ARRIVAL_IN + ARRIVAL_HOLD + ARRIVAL_OUT - OBJ_SHOWN[0]
        check(_t0 is not None and OBJ_SHOWN[1] >= _left - 0.01,
              "the objective toast waits until the arrival caption has faded", (OBJ_SHOWN[1], _left))
    $ renpy.pause(3.4, hard=True)
    $ shot("objective_toast", wait=0.4)
    python:
        check(arrival_caption() is None and renpy.get_screen("objective_toast") is not None,
              "then the objective toast slides in on its own")
        ## Leaving the place view takes it down; read by now, so it stays gone.
        OBJ_SHOWN[0] -= 10
        objective_leave()
        check(renpy.get_screen("objective_toast") is None and OBJ_UNSEEN[0] is None,
              "leaving the place view takes the objective toast down")
        check_objective()
        check(renpy.get_screen("objective_toast") is None, "the same objective doesn't show twice")
        ## Left before it could be read: it comes back next time.
        zz_swap("objective_text", lambda: "Report to Utahime's office")
        check_objective()
        objective_leave()
        check(renpy.get_screen("objective_toast") is None and OBJ_UNSEEN[0] == "Report to Utahime's office",
              "an objective taken down unread is remembered")
        check_objective()
        check(renpy.get_screen("objective_toast") is not None and OBJ_UNSEEN[0] is None,
              "and shows again the next time the place view does")
        renpy.hide_screen("objective_toast")
        zz_swap("objective_text", lambda: "Someone is moving into the room next to Yaga's")
        explore_mode = True
        check_objective()
        check(renpy.get_screen("objective_toast") is None, "no objective toast in explore mode")
        explore_mode = False
        check_objective()
        check(renpy.get_screen("objective_toast") is not None, "a changed objective shows")
        renpy.hide_screen("objective_toast")
    hide screen sb_place
    ## A save loaded onto `call screen sb_place` (an old one: last_objective
    ## None) gets NEXT as the view appears, without the loop's check.
    python:
        last_objective = None
        OBJ_UNSEEN[0] = None
        zz_swap("objective_text", lambda: "Roll call with Principal Yaga — Classroom Building, mornings")
    show screen sb_place
    $ renpy.pause(0.3, hard=True)
    python:
        check(renpy.get_screen("objective_toast") is not None and (last_objective or "").startswith("Roll call"),
              "the place view runs the objective check as it appears (a loaded save)", last_objective)
        renpy.hide_screen("objective_toast")
    hide screen sb_place
    python:
        ## A load counts the objective as unread, even if a waiting toast was
        ## saved away before it slid in.
        _objective_after_load()
        check(OBJ_UNSEEN[0] == last_objective, "after a load the objective counts as unread", OBJ_UNSEEN[0])
    show screen sb_place
    $ renpy.pause(0.3, hard=True)
    python:
        check(renpy.get_screen("objective_toast") is not None, "so the loaded place view shows it again")
        renpy.hide_screen("objective_toast")
        OBJ_UNSEEN[0] = None
    hide screen sb_place
    show screen sb_place
    $ renpy.pause(0.3, hard=True)
    python:
        check(renpy.get_screen("objective_toast") is None, "but not every time the place view appears")
        zz_swap("objective_text", _old_ot)
        last_objective = None
        OBJ_UNSEEN[0] = None
        day = 1
    hide screen sb_place

    ## --- staging and the activities --------------------------------------------------------
    python:
        here = "cafeteria"
        period = "Noon"
        bonds["yuji"] = 30
        stamina = 60
        spent_today = set()
        talked_today = set()
        ZZ_WATCH[0] = "yuji"
        del ZZ_SHOWING[:]
    $ autoplay()
    call stage_person("yuji")
    $ check(renpy.showing("yuji"), "stage_person shows them")
    call sb_activity("talk", "yuji")
    $ _talk = list(ZZ_SHOWING)
    $ del ZZ_SHOWING[:]
    $ _p0 = period
    call sb_activity("eat", "yuji")
    $ _eat = list(ZZ_SHOWING)
    $ autoplay(False)
    python:
        check(_talk and all(s for w, s in _talk), "Yuji stays on screen while we talk", _talk)
        _ae = open(os.path.join(config.gamedir, "events_activities.rpy"), encoding="utf-8").read()
        _ae = _ae[_ae.index("label act_eat"):].splitlines()[1].strip()
        if _ae.startswith("scene"):
            note("eat staging", "act_eat still opens with a scene reset (WP10 removes it, 5.1): %r; lines seen %r" % (_ae, _eat))
        else:
            check(_eat and all(s for w, s in _eat), "and while we eat", _eat)
        check(not renpy.showing("yuji"), "the scene resets after the activity")
        check(PERIODS.index(period) == PERIODS.index(_p0) + 1, "the activity charged its period", (_p0, period))
        ZZ_WATCH[0] = None

    ## record_act, train_together and raise_reserve are called (task 4)
    python:
        del ZZ_CALLS[:]
        _o_rec = zz_swap("record_act", lambda aid, who: ZZ_CALLS.append(("rec", aid, who)))
        _o_tt = zz_swap("train_together", lambda who, n=3, stat=None: ZZ_CALLS.append(("tt", who, n, stat)))
        _o_rr = zz_swap("raise_reserve", lambda n: ZZ_CALLS.append(("rr", n)))
        here = "classroom"
        period = "Morning"
        bonds["yuji"] = 30
        stamina = stamina_max
        spent_today = set()
    $ autoplay()
    call sb_activity("study", "yuji")
    $ autoplay(False)
    python:
        check(("rec", "study", "yuji") in ZZ_CALLS, "sb_activity records the act (record_act)", ZZ_CALLS)
        check([c for c in ZZ_CALLS if c[0] == "tt"] == [("tt", "yuji", 2, "insight")],
              "studying together trains them too: train_together(yuji, 2, insight)", ZZ_CALLS)
        del ZZ_CALLS[:]
        here = "dojo"
        period = "Morning"
        stamina = stamina_max
        spent_today = set()
        _before = (period, day)
    $ autoplay()
    call sb_activity("train", "yuji")
    $ autoplay(False)
    python:
        ## WP11 (WP7-o4, WP11-r1): one period, as the card's single diamond says.
        check((period, day) == ("Noon", _before[1]) and ACT_BY_ID["train"]["cost"] == 1,
              "a spar charges one period (Morning -> Noon), matching its card", (_before, period, day))
        check([c for c in ZZ_CALLS if c[0] == "tt"] == [("tt", "yuji", 3, "output")],
              "a spar calls train_together(yuji, 3, output) exactly once", ZZ_CALLS)
        check(("rec", "train", "yuji") in ZZ_CALLS, "and records the act", ZZ_CALLS)
        del ZZ_CALLS[:]
        here = "dojo"
        period = "Morning"
        stamina = 12
        spent_today = set()
        _pc = [c["id"] for c in person_choices("yuji", "dojo")]
        check("train" not in _pc, "at stamina 12 the person view doesn't offer Train together", _pc)
        ## WP11 (WP7-o5): activity_state agrees, so the journal does too.
        check(activity_state(ACT_BY_ID["train"], "yuji", "dojo") == (False, "Too tired"),
              "at stamina 12 activity_state calls Train together too tired", activity_state(ACT_BY_ID["train"], "yuji", "dojo"))
        stamina = 15
        check(activity_state(ACT_BY_ID["train"], "yuji", "dojo") == (True, None), "at stamina 15 it's available")
        stamina = 12
        _before = (period, day)
    $ autoplay()
    call sb_activity("train", "yuji")
    $ autoplay(False)
    python:
        check(ZZ_CALLS == [] and (period, day) == _before and "yuji" not in spent_today and stamina == 12,
              "a refused spar (stamina 12) records nothing, moves no clock and spends nobody",
              (ZZ_CALLS, period, day, sorted(spent_today), stamina))
        del ZZ_CALLS[:]
        here = "courtyard"
        period = "Morning"
        stamina = stamina_max
    $ autoplay()
    call sb_do_train
    $ autoplay(False)
    python:
        check(ZZ_CALLS == [("rr", 1)], "training alone deepens the reserve: raise_reserve(1)", ZZ_CALLS)
        zz_swap("record_act", _o_rec)
        zz_swap("train_together", _o_tt)
        zz_swap("raise_reserve", _o_rr)
        del ZZ_CALLS[:]

    ## once a day: hold, rest, racks
    python:
        here = "infirmary"
        period = "Morning"
        ce = ce_max
        stamina = 50
    $ autoplay()
    call sb_do_hold
    call sb_do_rest
    $ here = "storehouse"
    call sb_do_tools
    $ autoplay(False)
    python:
        check({"hold", "rest", "racks"} <= actions_today, "hold, rest and racks are recorded once used", actions_today)
        check("hold" not in [a[0] for a in place_actions("dorm")] and "rest" not in [a[0] for a in place_actions("infirmary")]
              and "tools" not in [a[0] for a in place_actions("storehouse")], "and are not offered again today")
        _ce = ce
    $ autoplay()
    call sb_do_hold
    $ autoplay(False)
    python:
        check(ce == _ce, "a second hold the same day spends nothing")
        new_day()
        check({"hold", "rest"} <= set(a[0] for a in place_actions("infirmary")), "they come back the next day")

    ## Gojo's lesson
    python:
        _old_gojo = zz_swap("gojo_in_today", lambda: True)
        here = "gojo_office"
        period = "Morning"
        stamina = 80
        spent_today = set()
        _c0, _r0 = control, ce_max
        ZZ_WATCH[0] = "gojo"
        del ZZ_SHOWING[:]
        check("lesson" in [c["id"] for c in person_choices("gojo", "gojo_office")], "the lesson is offered on an in-day")
    $ autoplay()
    call sb_activity("lesson", "gojo")
    $ autoplay(False)
    python:
        check(control > _c0 and ce_max == _r0 + 5, "the lesson trains control and the reserve", (_c0, control, _r0, ce_max))
        check("lesson" in actions_today and period == "Noon", "the lesson takes a period and is done for the day", (actions_today, period))
        check(ZZ_SHOWING and all(s for w, s in ZZ_SHOWING), "Gojo is on screen for the lesson")
        ZZ_WATCH[0] = None
        zz_swap("gojo_in_today", _old_gojo)

    ## release, and the retired forge
    python:
        companion = "yuji"
        _before = (ce, period, output, control, stamina)
    $ autoplay()
    call sb_do_release
    call sb_do_temper
    $ autoplay(False)
    python:
        check(companion is None, "sb_do_release lets the companion go")
        check((ce, period, output, control, stamina) == _before,
              "sb_do_temper (retired) spends nothing, takes no time, grows nothing", (_before, (ce, period, output, control, stamina)))
        _tp = _src[_src.index("label sb_do_temper"):]
        _tp = _tp[:_tp.index("\nlabel ")]
        check("The forge is cold." in _tp and "Emberfall" not in _tp and "gain(" not in _tp and "advance_period" not in _tp,
              "sb_do_temper is the two-line retired form (D31)", _tp)

    ## --- acceptance: the loop, driven through its real dispatch --------------------------------
    python:
        here = "courtyard"
        period = "Morning"
        stamina = stamina_max
        ce = ce_max
        spent_today = set()
        talked_today = set()
        actions_today = set()
        _zz_p0 = period
        del ZZ_LABELS[:]
        ZZ_DRIVE[:] = [
            ("sb_place", ("act", "wait")),
            ("sb_place", ("char", "yuji")),
            ("sb_char", ("do", "talk", "yuji")),
            ("sb_place", ("char", "yuji")),
            ("sb_char", ("act", "hold")),
            ("sb_place", ("journal", "people")),
            ("journal", ("arc_two",)),
            ("sb_place", ("mission", "m_roll_call")),
            ("sb_place", ("dev",)),
            ("sb_place", ("map",)),
            ("sb_map", ("district", "shibuya")),
            ("sb_place", "finish"),
        ]
    python:
        for _e in EVENTS:
            if _e["kind"] == "story":
                done_events.add(_e["label"])
        quick_menu = True
    $ autoplay()
    call sandbox
    $ abort("the sandbox loop returned")

label zz_after_loop:
    $ autoplay(False)
    python:
        _L = ZZ_LABELS
        note("loop labels", [l for l in _L if not l.startswith("_")][:40])
        check("sb_do_wait" in _L, "a returned (act, wait) still works")
        check(PERIODS.index(period) >= 1, "Wait moved the clock", period)
        check("sb_person" in _L and "sb_activity" in _L and "sb_smalltalk" in _L, "char -> person view -> Talk")
        check("sb_do_hold" in _L, "the person view's (act, id) runs the action")
        check("arc_two_start" in _L, "journal returning (arc_two,) calls arc_two_start (D38)")
        check("start_mission" in _L, "(mission, mid) calls start_mission")
        check("dev_tools" in _L, "(dev,) calls dev_tools")
        check("sb_travel" in _L and "sb_trip" in _L, "the map's (district, key) calls sb_trip")
        check(len(ZZ_DRIVE_LOG) == 12, "every driven step was answered", ZZ_DRIVE_LOG)
        check(quick_menu is True, "the loop doesn't switch the quick menu off", quick_menu)
    $ finish()
