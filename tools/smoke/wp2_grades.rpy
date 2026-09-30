## tools/smoke/wp2_grades.rpy -- the WP2 package harness (PHASE1_DESIGN.md,
## section 7 "WP2", 3.4, 3.5, 3.12 orders 10/20/30, 4.10, 4.12).
##
##   tools/smoke.sh tools/smoke/wp2_grades.rpy
##
## Checks every WP2 acceptance bullet as a named check ("acc: ..."), plus the
## rest of the grade API, the NPC growth rules, the combat data and an old
## save's fight state. Screenshots go to shots/wp2_grades/: both grade cards
## and the combat screen (a new alley fight, the promotion fight, and an old
## save's fight state).

init 999 python:
    import builtins

    ZZ_TOASTS = builtins.list()
    ZZ_SINK_WAS = builtins.list([None])

    def zz_sink(text, kind, who, amount):
        ZZ_TOASTS.append((text, kind, who, amount))

    def zz_capture(on=True):
        """Route toasts into ZZ_TOASTS (on) or back to whatever sink was there."""
        if on:
            ZZ_SINK_WAS[0] = TOAST_SINK[0]
            TOAST_SINK[0] = zz_sink
            del ZZ_TOASTS[:]
        else:
            TOAST_SINK[0] = ZZ_SINK_WAS[0]

    def zz_texts(kind=None):
        return [t[0] for t in ZZ_TOASTS if kind is None or t[1] == kind]

    ZZ_STUDENTS = ["yuji", "megumi", "nobara", "maki", "panda", "toge"]
    ZZ_ROSTER = ZZ_STUDENTS + ["shoko", "gojo", "yaga", "ijichi"]

    def zz_npc_snapshot():
        out = {}
        for w in ZZ_ROSTER:
            s = npc_stats(w)
            out[w] = (grade_rank(s["grade"]), s["ce_max"], s["control"], s["output"])
        return out

    def zz_dropped(before, after):
        """Names whose grade rank or any stat went down."""
        bad = []
        for w in before:
            for a, b in zip(before[w], after[w]):
                if a is not None and b is not None and b < a:
                    bad.append(w)
                    break
        return bad


## combat_screen is modal, which also blocks the hard pause shot() waits in,
## so its screenshots come from this timer screen stacked above it.
screen zz_snap(name):
    zorder 200
    timer 0.4 action [Function(shot, name, 0), Return(True)]


label zz_smoke:

    python:
        settle(mc_name="Tester", mc_surname="Harness", day=3, here="classroom")
        check(technique == "timestop" and grade is None, "a new game: Last Light, not yet assessed", (technique, grade))
        check(_validate_grades() == [], "the WP2 validator finds nothing", _validate_grades())

    ## --- Last Light ------------------------------------------------------------------------
    python:
        technique = "filament"  # legacy-technique
        check(tech()["name"] == "Last Light", "acc: tech()['name'] == 'Last Light' with technique = 'filament'", tech()["name"])  # legacy-technique
        check(list(TECHNIQUES) == ["timestop"], "TECHNIQUES holds only timestop", list(TECHNIQUES))
        check(TECHNIQUES["filament"]["name"] == "Last Light" and TECHNIQUES.get("filament") is None,  # legacy-technique
              "an old technique key read by an unconverted scene gets Last Light; .get() still misses")
        check(tech()["jp"] == "残光 · Zankō" and tech()["verb"] == "Hold" and len(tech()["tiers"]) == 4, "Last Light's record", tech())
        technique = "timestop"
        check(len(MOVES) == 1 and list(MOVES) == ["timestop"], "acc: MOVES has one key", list(MOVES))
        control = 12
        check([m["id"] for m in moves_available()] == ["stutter"], "moves at tier 0", [m["id"] for m in moves_available()])
        ## Tier reach with the caps: Held Second at Grade 4, Arrest from Grade 2, the fourth tier only at Grade 1.
        _reach = {}
        for _k in ("g4", "g3", "g2", "s1", "g1"):
            grade = _k
            control = 12
            for _i in range(80):
                gain("control", 5, quiet=True)
            _reach[_k] = tech_tier()[0]
        check(_reach == {"g4": 1, "g3": 1, "g2": 2, "s1": 2, "g1": 3}, "Last Light's tier reach by grade", _reach)
        grade = None
        control = 12

    ## --- grade lookups -----------------------------------------------------------------------
    python:
        check(grade_name() == "Not yet assessed", "grade_name() before roll call", grade_name())
        check(next_grade_text() == "Not yet assessed. Roll call comes first.", "next_grade_text before roll call (D16's wording, as grade_label)", next_grade_text())
        check(grade_cap("stat") == 40 and grade_cap("reserve") == 100 and talisman_slots() == 1, "Grade 4's numbers while unassessed (D16)")
        grade = 3
        check(grade_name() == "Grade 3" and grade_cap("stat") == 55, "a legacy int grade still reads", grade_name())
        grade = "g4"
        check(grade_name() == "Grade 4", "grade_name() is grade_label(grade)", grade_name())
        check(grade_label(1) == "Grade 1" and grade_label("sp") == "Special Grade" and grade_label(None) == "Not yet assessed", "grade_label")
        check(grade_key(0) == "sp" and grade_key("zz") is None and grade_rank("s1") == 3 and grade_rank(None) == -1, "grade_key / grade_rank")
        check(grade_opens_text("g3") == "Board: Grade 3 jobs · Reserve up to 140 · 2 talisman slots", "grade card line, Grade 3", grade_opens_text("g3"))
        check(grade_opens_text("g4") == "Board: Grade 4 jobs · Reserve up to 100 · 1 talisman slot", "grade card line, Grade 4", grade_opens_text("g4"))
        merit = 34
        check(merit_progress() == (34, 60, "g3"), "merit_progress at Grade 4", merit_progress())
        check(next_grade_text() == "Merit 34/60, then a promotion mission — Maki will watch.", "next_grade_text at Grade 4", next_grade_text())
        merit = 70
        check(next_grade_text() == "Merit 70/60. Ready: a promotion mission — Maki will watch.", "next_grade_text once merit is met (70 at Grade 4)", next_grade_text())
        merit = 60
        check(next_grade_text().startswith("Merit 60/60. Ready: "), "next_grade_text at exactly the requirement", next_grade_text())
        merit = 34
        grade = "s1"
        check(merit_progress() == (34, None, "g1") and "recommendations" in next_grade_text(), "next grade from Semi-Grade 1", (merit_progress(), next_grade_text()))
        grade = "g1"
        check(merit_progress() == (34, None, None) and next_grade_text() == "", "nothing above Grade 1 (Special Grade is off the scale)", merit_progress())
        grade = "g4"
        zz_capture()
        merit = 0
        add_merit(30, "The Sun Mall")
        add_merit(5)
        check(merit == 35, "add_merit adds", merit)
        check(zz_texts("grade") == ["Merit +30 — The Sun Mall", "Merit +5"], "add_merit toasts (kind grade)", ZZ_TOASTS)
        zz_capture(False)
        merit = 0

    ## --- migrations 10, 20, 30 --------------------------------------------------------------
    python:
        _orders = sorted(m[0] for m in MIGRATIONS)
        check(len([o for o in _orders if o == 10]) == 1 and 20 in _orders and 30 in _orders,
              "exactly one migration 10, plus 20 and 30", _orders)

        ## acc: the legacy grade migration.
        for _val, _rc, _want in [(3, False, "g3"), (3, True, "g3"), (4, True, "g4"), (4, False, None),
                                 ("g2", False, "g2"), (None, True, None), (2, True, "g4")]:
            grade = _val
            if _rc:
                flag("roll_call")
            else:
                flags.discard("roll_call")
            run_migrations()
            check(grade == _want, "acc: grade migration %r (roll_call %s) -> %r" % (_val, _rc, _want), grade)
        flags.discard("roll_call")

        ## acc: migration 10 on an Emberfall fixture, twice.
        technique = "emberfall"  # legacy-technique
        control = 20
        output = 45
        run_migrations()
        check(technique == "timestop" and control >= output and control == 45 and has_flag("technique_was_emberfall"),  # legacy-technique
              "acc: migration 10 on Emberfall gives control >= output", (technique, control, output))
        _snap = (technique, control, output, sorted(flags), grade, hp, hp_max, ce_max, save_version)
        run_migrations()
        check((technique, control, output, sorted(flags), grade, hp, hp_max, ce_max, save_version) == _snap,
              "acc: a second migration run changes nothing")
        technique = "filament"  # legacy-technique
        control = 30
        output = 10
        run_migrations()
        check(technique == "timestop" and control == 30 and has_flag("technique_was_filament"),  # legacy-technique
              "migration 10 on Filament: Last Light, control unchanged", (technique, control))
        technique = "stillness"  # legacy-technique
        run_migrations()
        check(technique == "timestop" and tname == "Last Light", "any other technique -> timestop; migration 5's tname reads Last Light", (technique, tname))
        _mig_flags = [f for f in flags if f.startswith("technique_was_")]
        for _f in _mig_flags:
            flags.discard(_f)

        ## migration 30: vitals refreshed, a save at 0 HP gets it back.
        control = 30
        output = 20
        hp = 0
        run_migrations()
        check(hp_max == 50 + 20 + 10 and hp == hp_max, "migration 30: refresh_vitals, 0 HP restored", (hp, hp_max))
        hp = 40
        run_migrations()
        check(hp == 40, "migration 30 leaves a living save's HP alone", hp)

    ## --- caps: gain() and raise_reserve() -------------------------------------------------
    python:
        grade = "g4"
        actions_today = set()
        zz_capture()
        control = 35
        gain("control", 50)
        check(control == 40, "acc: at g4, control 35 + gain('control', 50) -> 40", control)
        control = 47
        gain("control", 5)
        check(control == 47, "acc: at g4, a control of 47 is never lowered", control)
        _cap_toasts = [t for t in zz_texts("stat") if "limit" in t]
        check(_cap_toasts == ["Control is at the Grade 4 limit — a promotion lifts it"] and "cap:control" in actions_today,
              "the cap toast comes once a day per stat", ZZ_TOASTS)
        check("Control +5" in zz_texts("stat"), "gain toasts the stat (kind stat)", ZZ_TOASTS)
        output = 39
        gain("output", 3)
        check(output == 40 and len([t for t in zz_texts() if "limit" in t]) == 2, "output has its own cap toast", ZZ_TOASTS)
        actions_today = set()
        del ZZ_TOASTS[:]
        gain("output", 2, quiet=True)
        check(ZZ_TOASTS == [] and output == 40, "quiet: no toasts", ZZ_TOASTS)
        insight = 97
        gain("insight", 10)
        check(insight == 100, "insight stops at 100, not the grade cap", insight)
        insight = 70
        gain("insight", -5, quiet=True)
        check(insight == 65, "a negative gain lowers (no diminishing-returns flip)", insight)
        zz_capture(False)

        ce_max = 60
        _r = raise_reserve(100)
        check(ce_max == 100 and _r == 40, "acc: at g4, raise_reserve(100) from 60 -> 100", ce_max)
        ce_max = 120
        raise_reserve(10)
        check(ce_max == 120, "raise_reserve never lowers a reserve above the cap", ce_max)
        grade = None
        ce_max = 95
        raise_reserve(20)
        check(ce_max == 100, "raise_reserve uses Grade 4's cap while unassessed", ce_max)
        grade = "g4"
        ce_max = 60

    ## --- promotion ------------------------------------------------------------------------------
    python:
        zz_capture()
        promotions_log = []
        grade = "g4"
        _up = promote("mc", "g3")
        check(_up and grade == "g3" and talisman_slots() == 2 and grade_cap("stat") == 55,
              "acc: promote('mc', 'g3') -> talisman_slots() == 2 and grade_cap('stat') == 55", (grade, talisman_slots(), grade_cap("stat")))
        check(grade_cap("reserve") == 140, "Grade 3's reserve cap", grade_cap("reserve"))
        check(promote("mc", "g4") is False and grade == "g3", "promote never lowers the player", grade)
        check(zz_texts("grade") == ["Promoted to Grade 3"], "the player's promotion toast", ZZ_TOASTS)
        check(promotions_log[-1]["who"] == "mc" and promotions_log[-1]["grade"] == "g3" and len(promotions_log) == 1, "promotions_log", promotions_log)
        del ZZ_TOASTS[:]
        grade = None
        promote("mc", "g4", "Assessed at roll call", quiet=True)
        check(grade == "g4" and ZZ_TOASTS == [], "roll call's quiet assessment", (grade, ZZ_TOASTS))
        grade = 3
        promote("mc", "g3", quiet=True)
        check(grade == "g3", "promote to the same grade turns a legacy int into its key", grade)

        npc_state = {}
        pending_remarks = {}
        del ZZ_TOASTS[:]
        check(promote("nobara", "g2", "test"), "promote an NPC", npc_state)
        check(npc_stats("nobara")["grade"] == "g2" and pending_remarks.get("nobara") is True, "the NPC's grade and pending remark", (npc_state, pending_remarks))
        check(ZZ_TOASTS == [("Nobara — promoted to Grade 2", "grade", "nobara", None)], "the NPC's toast, in their colour", ZZ_TOASTS)
        check(recent_promotion("nobara") and not recent_promotion("megumi"), "recent_promotion")
        _d = day
        day = _d + 3
        check(not recent_promotion("nobara"), "recent_promotion ends after 3 days")
        day = _d
        check(pop_remark("nobara") is True and pop_remark("nobara") is False, "pop_remark once")
        check(promote("nobara", "g3") is False and npc_stats("nobara")["grade"] == "g2", "promote never lowers an NPC")
        zz_capture(False)

        ## npc_stats: base + min(30, xp // 6); never None-crashes.
        npc_state = {"yuji": dict(grade="g4", xp=60, promoted_day=None), "maki": dict(grade="g4", xp=600, promoted_day=None)}
        _y = npc_stats("yuji")
        check((_y["ce_max"], _y["control"], _y["output"]) == (120, 38, 72), "npc_stats: base + xp // 6", _y)
        _m = npc_stats("maki")
        check(_m["ce_max"] == 0 and _m["output"] == 118 and _m["restricted"] and "Heavenly Restriction" in _m["note"],
              "Maki: the bonus caps at 30; her reserve stays at 0", _m)
        _g = npc_stats("gojo")
        check(_g["off_scale"] and _g["ce_max"] is None and _g["grade"] == "sp", "Gojo is off the scale", _g)
        check(npc_stats("yaga")["role"] == "Principal" and npc_stats("shoko")["grade"] is None, "roles and ungraded staff")
        check(npc_stats("nanami")["hidden"] and npc_stats("nanami")["grade"] == "g1", "Nanami is registered, hidden")
        check(npc_stats("zz_nobody")["grade"] is None, "an unknown name reads as nothing")
        _n0 = dict(npc_state)
        npc_stats("megumi")
        check("megumi" not in npc_state, "reading npc_stats doesn't write saved state")

        check(sorcerer_power("gojo") == 999, "sorcerer_power: off the scale = 999")
        check(sorcerer_power("yuji") == (38 + 72) / 2.0, "sorcerer_power: an NPC", sorcerer_power("yuji"))
        control, output, insight = 30, 20, 40
        check(sorcerer_power("mc") == 25 + 10 + 6 * tech_tier()[0], "sorcerer_power: the player", sorcerer_power("mc"))
        check(sorcerer_power("nanami") == 100, "sorcerer_power: unknown numbers use the grade's cap", sorcerer_power("nanami"))

        npc_state = {}
        output = 20
        train_together("yuji", 3, "output")
        check(npc_state["yuji"]["xp"] == 6 and output == 21, "train_together: 2n xp, and gain(stat, 1)", (npc_state, output))
        train_together("gojo", 6)
        check("gojo" not in npc_state, "train_together: staff and Gojo don't grow")

        roster = list(ZZ_ROSTER)
        bonds = {"panda": 50, "megumi": 10}
        check(pick_team(3) == ["toge", "panda", "megumi"], "pick_team: grade, then bond", pick_team(3))
        check(pick_team(9, "g2") == ["toge", "panda", "megumi"], "pick_team: min_key", pick_team(9, "g2"))
        check(pick_team(2, "g1") == [] and pick_team(0) == [], "pick_team: nobody that high / n = 0")
        grade = "g4"

    ## --- growth: 60 days with acts_done stubbed to 1 ----------------------------------------
    python:
        _acts_was = acts_done
        roster = list(ZZ_ROSTER)
        npc_state = {}
        promotions_log = []
        pending_remarks = {}
        zz_capture()

        store.acts_done = lambda: 0
        _before = zz_npc_snapshot()
        for _i in range(20):
            new_day()
        check(promotions_log == [], "no NPC promotions while no act is done", promotions_log)
        check(npc_state["yuji"]["xp"] >= 60, "xp accrues anyway (cumulative)", npc_state.get("yuji"))

        npc_state = {}
        store.acts_done = lambda: 1
        _before = zz_npc_snapshot()
        _dropped = []
        for _i in range(60):
            new_day()
            _now = zz_npc_snapshot()
            _dropped += zz_dropped(_before, _now)
            _before = _now
        _promos = [e for e in promotions_log if e["who"] != "mc"]
        note("promotions in 60 days", ["%s %s day %d" % (e["who"], e["grade"], e["day"]) for e in _promos])
        check(len(_promos) >= 1, "acc: 60 days (acts_done = 1) give at least one NPC promotion", _promos)
        check(all(grade_rank(e["grade"]) <= grade_rank("g3") for e in _promos), "acc: no promotion above g3 with one act done", _promos)
        check(all(grade_rank(e["grade"]) <= grade_rank(NPC_BASE[e["who"]]["max_grade"]) for e in _promos),
              "acc: no promotion above the NPC's max grade", _promos)
        check(_dropped == [], "acc: NPC stats and grades never decrease", _dropped)
        check(not any(e["who"] == "maki" for e in _promos), "Maki stays Grade 4", _promos)
        check(all(p in pending_remarks for p in set(e["who"] for e in _promos)), "each promoted NPC has a pending remark", pending_remarks)
        check(len([t for t in ZZ_TOASTS if t[1] == "grade"]) == len(_promos), "growth toasts only on promotion", ZZ_TOASTS)
        check(set(npc_state) <= set(ZZ_STUDENTS), "only students grow", sorted(npc_state))
        zz_capture(False)
        store.acts_done = _acts_was
        check(acts_done() == 0, "acts_done restored to WP3's stub")
        npc_state = {}
        promotions_log = []
        pending_remarks = {}
        grade = "g4"

    ## --- combat data ------------------------------------------------------------------------------
    python:
        check(all(ENEMIES[k]["grade"] == g for k, g in (("alley_curse", "g1"), ("nade_curse", "g3"), ("warehouse", "g2"), ("promo_g3", "g3"))),
              "enemy grades are keys")
        _p = ENEMIES["promo_g3"]
        check((_p["name"], _p["hp"], _p["power"], _p["sprite"], sorted(set(t[1] for t in _p["tells"])))
              == ("Grade 3 assessment curse", 100, 16, "curse small", ["fast", "grab", "heavy"]), "promo_g3's entry", _p)

        ## The HP floor.
        control, output, insight = 12, 10, 10
        hp = 1
        combat_begin("alley_curse", None, False, "bg alley")
        check(hp == hp_max // 2 and cb["grade"] == "g1" and cb["rounds"] == 4 and "burn" not in cb, "combat_begin: HP floored at half; grade key; rounds", (hp, hp_max, cb.get("grade"), cb.get("rounds")))

        ## acc: four rounds of any action end the alley fight "down".
        hp_max = hp = 9999
        _acts = ["read", "guard", "step", "strike"]
        _ended_early = None
        for _i, _act in enumerate(_acts):
            _done = combat_player(_act)
            if not _done:
                combat_enemy()
            if cb["over"] and _i < 3:
                _ended_early = (_i, cb["over"])
                break
        check(_ended_early is None and cb["over"] == "down" and cb["round"] == 4 and cb["log"][0] == "It stops playing with me.",
              "acc: combat_begin('alley_curse') + 4 rounds of any action -> cb['over'] == 'down'", (cb["over"], cb["round"], cb["log"], _ended_early))
        check(hp > 0, "the alley ends on the round limit, not on HP", hp)

        ## An enemy dict (phase 2's board fights).
        refresh_vitals()
        combat_begin(dict(name="Board curse", grade="g4", hp=40, power=8, sprite="curse small",
                          tells=[("It lunges.", "fast")]), "megumi", True, "bg alley")
        check(cb["key"] == "custom" and cb["grade"] == "g4" and cb["rounds"] is None, "combat_begin accepts an enemy dict", cb.get("key"))
        combat_player("step")
        combat_enemy()
        check(cb["ehp"] < 40 and cb["over"] in (None, "win"), "an ally still goes in (no ally_buff)", cb["ehp"])

        ## An old save's fight state: int grade, burn / ally_buff, no rounds.
        cb = dict(key="alley_curse", name="Something in the alley", grade=1, ehp=880, ehp_max=900, power=26,
                  sprite="curse big", tells=list(ENEMIES["alley_curse"]["tells"]), tell="It takes hold of your forearm.",
                  kind="grab", ally=None, flee_ok=False, bg=Transform("bg alley", matrixcolor=BrightnessMatrix(-0.05)), read=False, burn=6, stagger=0,
                  freedodge=False, ally_buff=2, answered=False, punish=False, log=["Ember — 9."], round=4, over=None)
        hp = hp_max = 9999
        combat_player("move", dict(id="suture", name="Suture", tier=1, ce=0, desc="", scale="control", mult=0.0, heal=True))  # legacy-technique
        combat_enemy()
        check(cb["over"] == "down", "an old save's alley fight gets the round limit too", (cb["over"], cb["round"]))
        cb["over"] = None
        ce = 60

    ## --- screenshots: the combat screen ----------------------------------------------------------
    scene expression "bg alley"
    show screen combat_screen
    call screen zz_snap("combat_old_save_state")
    hide screen combat_screen
    python:
        control, output, insight = 35, 20, 10
        ce_max = ce = 90
        hp = 60
        combat_begin("alley_curse", None, False, "bg alley")
        clog("I stop and listen. I can read it now — but it doesn't wait.")
    show screen combat_screen
    call screen zz_snap("combat_alley")
    $ check(renpy.get_screen("combat_screen") is not None, "combat_screen renders (alley)")
    hide screen combat_screen
    ## All three moves (Arrest from control 60) plus Read it and Withdraw must fit at 1920.
    $ control = 65
    $ combat_begin("promo_g3", None, True, None)
    $ check(len(moves_available()) == 3, "three moves at control 65")
    python:
        def _wp2_builtin(v):
            if v is None or isinstance(v, (str, bool, int)):
                return True
            if isinstance(v, (list, tuple, set)):
                return all(_wp2_builtin(x) for x in v)
            if isinstance(v, dict):
                return all(_wp2_builtin(k) and _wp2_builtin(x) for k, x in v.items())
            return False
        _bad = sorted(k for k, v in cb.items() if not _wp2_builtin(v))
        check(not _bad and cb["bg"] is None and cb["bg_loc"] == here and cb["bg_per"] == period,
              "2.1.6: the fight state holds only builtins (bg kept as a name, lit at draw time)", (_bad, cb.get("bg_loc"), cb.get("bg_per")))
    show screen combat_screen
    call screen zz_snap("combat_promo_g3")
    $ check(renpy.get_screen("combat_screen") is not None, "combat_screen renders (promo_g3)")
    hide screen combat_screen
    ## A phase-2 board fight passing displayables: only plain values are saved.
    python:
        combat_begin(dict(name="Stray curse", hp=40, power=8,
                          sprite=Transform("curse small", zoom=0.9),
                          tells=[("It twitches toward me.", "fast")]),
                     None, True, Transform("bg classroom", zoom=1.0))
        _bad = sorted(k for k, v in cb.items() if not _wp2_builtin(v))
        check(not _bad and cb["bg"] is None and cb["sprite"] == "curse small" and cb["grade"] is None,
              "2.1.6: a displayable sprite and bg from an enemy dict leave only builtins in the fight state",
              (_bad, cb.get("bg"), cb.get("sprite"), cb.get("grade")))
    show screen combat_screen
    call screen zz_snap("combat_ungraded_enemy")
    $ _gshown = renpy.get_screen("combat_screen").scope.get("_grade")
    $ check(_gshown == "Ungraded", "an enemy with no grade reads 'Ungraded', not the player's 'Not yet assessed'", _gshown)
    hide screen combat_screen

    ## --- the fights through the combat label, under autoplay ----------------------------------------
    python:
        control, output, insight = 12, 10, 10
        refresh_vitals()
        hp = hp_max
        quick_menu = True
    $ autoplay()
    call combat("alley_curse", None, False, None)
    $ _res = _return
    $ autoplay(False)
    $ check(_res == "down" and cb["round"] == 4 and quick_menu is True, "the alley fight (autoplay, every tell answered) ends after four exchanges", (_res, cb["round"], quick_menu))
    $ check(hp == hp_max, "answered every time: never hit", (hp, hp_max))

    $ autoplay()
    call combat("promo_g3", None, True, None)
    $ _res = _return
    $ autoplay(False)
    $ check(_res == "win", "acc: promo_g3 answered correctly every round (autoplay) -> 'win'", (_res, cb.get("round"), cb.get("ehp")))
    $ note("promo_g3", "won in %d rounds at output %d" % (cb["round"], output))

    ## --- the grade card ------------------------------------------------------------------------------
    scene expression "bg classroom"
    show screen grade_card("g4", "ASSESSED")
    $ shot("grade_card_assessed")
    hide screen grade_card
    show screen grade_card("g3", "PROMOTED")
    $ shot("grade_card_promoted")
    hide screen grade_card
    show screen grade_card(None, "ASSESSED")
    $ shot("grade_card_none")
    $ _gl = renpy.get_screen("grade_card").scope.get("_gl")
    $ check(_gl == "Grade 4", "grade_card(None) shows Grade 4 (D16), never 'ASSESSED / Not yet assessed'", _gl)
    hide screen grade_card
    python:
        ## Stand in for the card's 3-second pause: record the quick menu while
        ## the card is up (a real pause could be ended by a stray click).
        _wp2_seen = builtins.list()
        _wp2_pause = renpy.pause
        def _wp2_watch(*a, **kw):
            if renpy.get_screen("grade_card") is not None:
                _wp2_seen.append(store.quick_menu)
            return _wp2_pause(0, hard=True)
        renpy.pause = _wp2_watch
        quick_menu = True
    $ autoplay()
    call show_grade_card("g3")
    call show_grade_card(None, "ASSESSED")
    $ autoplay(False)
    $ check(renpy.get_screen("grade_card") is None, "show_grade_card shows the card and takes it away")
    $ check(_wp2_seen and not any(_wp2_seen) and quick_menu is True,
            "the quick menu is hidden while the card shows, and restored after", (len(_wp2_seen), builtins.sorted(builtins.set(_wp2_seen)), quick_menu))
    python:
        quick_menu = False
        del _wp2_seen[:]
    $ autoplay()
    call show_grade_card("g4", "ASSESSED")
    $ autoplay(False)
    python:
        renpy.pause = _wp2_pause
        check(quick_menu is False, "a quick menu already off stays off after the card", quick_menu)
        quick_menu = True

    $ finish()
