## tools/smoke/wp4_board.rpy -- WP4's harness: Utahime's board
## (PHASE1_DESIGN.md 3.7, 4.8, D12, D13 and the WP4 acceptance list).
##
##   tools/smoke.sh tools/smoke/wp4_board.rpy
##
## Checks every WP4 acceptance bullet as a named check, plays whole jobs
## through label sb_do_board (the two screens answered by a scripted
## call_screen) and through run_board_mission, and saves screenshots of both
## board screens and a line of narration to shots/wp4_board/. Every narration
## a run can produce (partner x outcome x twist x misgrade) is written to
## shots/wp4_board/narration.txt for a read-through.
##
## Harness-level stand-ins, used only while the real package isn't merged:
##   - WP1: Utahime's office in LOCATIONS and her schedule (3.2);
##   - WP2: sorcerer_power with the 3.4 formula (the stub returns 10);
##   - train_together and the toast sink are wrapped to record calls.

init 999 python:
    import os

    import time
    ZZ_STANDINS = []    # noted at the start of the run (note() can't run at init)

    ## Every screenshot, with whether it was saved (shot() only notes a
    ## failure, so the harness checks these at the end).
    ZZ_SHOTS = {}
    ZZ_T0 = [time.time()]

    def zz_shot(name, **kw):
        ZZ_SHOTS[name] = bool(shot(name, **kw))
        return ZZ_SHOTS[name]

    def zz_mark(what):
        """Progress, written at once (a hang leaves the last step behind)."""
        with open(os.path.join(zz_smoke_state.shots, "progress.txt"), "a") as f:
            f.write(str(what) + "\n")

    ## WP1 stand-in: the office and Utahime's schedule (3.2).
    if "utahime_office" not in LOCATIONS:
        LOCATIONS["utahime_office"] = dict(indoor=True, name="Utahime's Office", bg="bg utahime_office",
                                           x=1480, y=560, desc="Neat, traditional, and a mission board already fuller than Yaga's ever was.")
        LOC_ORDER.append("utahime_office")
        ZZ_STANDINS.append("WP1 not merged: utahime_office added to LOCATIONS by the harness")
    if "utahime" not in SCHEDULE:
        SCHEDULE["utahime"] = {"Morning": "utahime_office", "Noon": "utahime_office",
                               "Afternoon": "utahime_office", "Evening": "cafeteria", "Night": "-"}
        WEEKEND["utahime"] = {"Afternoon": "-", "Evening": "courtyard"}
        ZZ_STANDINS.append("WP1 not merged: Utahime's schedule added by the harness")

    ## WP2 stand-in: sorcerer_power as 3.4 has it.
    def zz_power(who):
        if who == "mc":
            return (store.control + store.output) / 2.0 + store.insight / 4.0 + 6 * tech_tier()[0]
        s = npc_stats(who)
        if s.get("off_scale"):
            return 999
        return ((s.get("control") or 0) + (s.get("output") or 0)) / 2.0

    if "WP0 stub" in (sorcerer_power.__doc__ or ""):
        sorcerer_power = zz_power
        ZZ_STANDINS.append("WP2 not merged: sorcerer_power uses the 3.4 formula in the harness")

    ## Recorders.
    ZZ_TRAIN = []
    _zz_train_real = train_together

    def zz_train(who, n=3, stat=None):
        ZZ_TRAIN.append((who, n, stat))
        return _zz_train_real(who, n, stat)

    train_together = zz_train

    ZZ_TOASTS = []

    def zz_sink(text, kind="info", who=None, amount=None):
        ZZ_TOASTS.append((text, kind, who, amount))

    ## Scripted answers for `call screen`: (screen name, return value). Each
    ## scripted screen is shown, photographed and hidden, then answered.
    ZZ_SCREEN_SCRIPT = []
    _zz_call_screen_real = renpy.call_screen

    def zz_call_screen(_screen_name, *args, **kwargs):
        if ZZ_SCREEN_SCRIPT and ZZ_SCREEN_SCRIPT[0][0] == _screen_name:
            name, value, shotname = ZZ_SCREEN_SCRIPT.pop(0)
            zz_mark("scripted " + name)
            renpy.show_screen(_screen_name, *args, **kwargs)
            if shotname:
                zz_shot(shotname)
            renpy.hide_screen(_screen_name)
            return value(*args) if callable(value) else value
        abort("unscripted call screen %s" % _screen_name)

    ## The run label clears its result when it returns, so the harness keeps
    ## its own copy of the last board_take() result.
    ZZ_LAST_RES = [None]
    _zz_board_take_real = board_take

    def zz_board_take(offer_id, who):
        res = _zz_board_take_real(offer_id, who)
        ZZ_LAST_RES[0] = res
        return res

    board_take = zz_board_take

    ZZ_STUDENTS = ["yuji", "megumi", "nobara", "maki", "panda", "toge"]
    ZZ_EVERYONE = ["yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "gojo", "yaga", "utahime", "ijichi"]

    def zz_sig(o):
        return (o["grade"], o["true_grade"], o["case"], o["place"], o["curse"], o["twist"], o["senior_only"])

    def zz_open_state(**kw):
        """A Grade 4 player on a Monday morning in Utahime's office, board open."""
        base = dict(day=1, period="Morning", here="utahime_office", grade="g4", technique="timestop",
                    control=12, output=10, insight=10, stamina=100, merit=0, yen=0,
                    roster=list(ZZ_EVERYONE), bonds={}, board_week=-1, board_npc=None,
                    board_misgrades=0, schedule_overrides={}, explore_mode=False)
        base.update(kw)
        fixture(**base)
        ## The shaped variables are emptied directly: fixture() refuses them
        ## (PHASE2 R5), and an empty container has no shape to get wrong.
        store.inventory = {}
        store.npc_state = {}
        store.board_offers = []
        store.board_log = []
        for f in ("utahime_leads_kyoto", "wakuri_clue", "armory_open"):
            flags.discard(f)
        flag("mission_board_open")
        flag("utahime_arrived")
        roll_gojo()

    def zz_fake_res(who, outcome, twist, misgraded, period="Morning"):
        o = dict(id="zz", grade="g4", true_grade="g3" if misgraded else "g4", case="Missing persons",
                 place="nerima", curse=BOARD_CURSES["g4"][0], twist=twist, title="The Nerima Tunnel",
                 merit=10, yen=(3000, 6000), drop=["sealing_talisman"], senior_only=False)
        r = board_resolve(o, who, 1, period)
        r["outcome"] = outcome
        return r


label zz_smoke:

    $ ZZ_T0[0] = time.time()
    python:
        for _s in ZZ_STANDINS:
            note("stand-in", _s)
    $ settle(mc_name="Tester", mc_surname="Harness")
    $ zz_open_state()

    ## --- host and open (D13) ---------------------------------------------------------------
    python:
        check(board_host() == ("utahime", "utahime_office"), "board_host is Utahime's office", board_host())
        check(board_open(), "board_open: flag, at her office, she is in, weekday morning")
        check("board" in [a[0] for a in registered_place_actions("utahime_office")], "the Mission board action is offered at utahime_office when open")
        flags.discard("mission_board_open")
        check(not board_open(), "board closed without mission_board_open")
        check("board" not in [a[0] for a in registered_place_actions("utahime_office")], "no Mission board action while closed")
        flag("mission_board_open")
        here = "office"
        check(not board_open(), "board closed at Yaga's office while Utahime hosts")
        here = "utahime_office"
        roster.remove("utahime")
        check(not board_open(), "an old save's mission_board_open opens nothing until Utahime is rostered")
        roster.append("utahime")
        period = "Evening"
        check(not board_open(), "board closed in the Evening (Utahime is at the cafeteria)")
        period = "Morning"
        flag("utahime_leads_kyoto")
        check(board_host() == ("ijichi", "office"), "board_host() switches to Ijichi at Yaga's office with utahime_leads_kyoto", board_host())
        here = "office"
        pin("ijichi", "office")
        check(board_open(), "with utahime_leads_kyoto the board opens at Yaga's office when Ijichi is there")
        check(board_host_note() and "Kyoto" in board_host_note() and board_summary()["note"] == board_host_note(),
              "under Ijichi the board says it has moved (D13), on the screen and in board_summary", board_host_note())
        board_refresh()
        renpy.show_screen("board_screen")
    $ zz_shot("board_screen_ijichi")
    $ renpy.hide_screen("board_screen")
    python:
        flags.discard("utahime_leads_kyoto")
        check(board_host_note() == "", "and says nothing while it is Utahime's")
        schedule_overrides = {}
        here = "utahime_office"
        check(board_host() == ("utahime", "utahime_office"), "board_host() switches back without the flag")
        board_offers = []
        board_week = -1

    ## --- the day the board opens, and a brand-new game (no board yet) -------------------------------------------
    python:
        zz_open_state()
        check(board_offers == [] and len(board_summary()["offers"]) == 3 and board_offers == [] and board_week == -1,
              "the day the board opens, board_summary already lists this week's 3 offers, and changes nothing", (len(board_summary()["offers"]), board_offers, board_week))
        flags.discard("mission_board_open")
        check(board_summary()["offers"] == [] and board_npc_card() is None and board_summary()["taken"] == [],
              "in a new game (no board yet) the summary has no offers and no taken card", board_summary()["taken"])
        flag("mission_board_open")

    ## --- an old save with mission_board_open, before Utahime's scene -----------------------------------------------
    python:
        zz_open_state(grade="g3", roster=["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "ijichi"])
        ## A save from before her scene has no utahime_arrived either: WP3's real
        ## migration 40 recruits her from that flag, so keep it off here.
        flags.discard("utahime_arrived")
        run_migrations()
        check("utahime" not in roster, "(an old save without utahime_arrived stays without her after migrations)", roster)
        check(len(board_offers) == 3, "(migration 80 still posts offers for an old save's flag)", len(board_offers))
        _s = board_summary()
        check(not board_open() and _s["offers"] == [] and _s["taken"] == [] and board_npc_card() is None,
              "before Utahime is met, the summary shows no offers and no taken card", (_s["offers"][:1], _s["taken"]))
        roster.append("utahime")
        check(len(board_summary()["offers"]) == 3 and board_summary()["taken"], "once she is rostered, the board appears in the summary")

    ## --- the board reads NPC grades through its own helper, never a global _npc_grade ---------------------------
    ## A static check: WP2's own npc_stats calls its global _npc_grade, so a
    ## trap on store._npc_grade can't tell the board's calls from WP2's.
    python:
        zz_open_state()
        board_refresh()
        _zz_fns = [("_board_npc_grade", _board_npc_grade), ("board_partner_rows", board_partner_rows),
                   ("_board_students", _board_students), ("board_npc_card", board_npc_card),
                   ("board_summary", board_summary)]
        _zz_bad = [n for n, fn in _zz_fns if "_npc_grade" in fn.__code__.co_names]
        check(not _zz_bad, "no board function names the global _npc_grade (they read npc_stats via _board_npc_grade)", _zz_bad)
        _zz_rows = board_partner_rows(board_offers[0])
        check(_zz_rows and all(_board_npc_grade(w) == npc_stats(w).get("grade") for w in ZZ_STUDENTS),
              "board grades come from npc_stats via _board_npc_grade, and the partner rows are filled",
              ([(w, _board_npc_grade(w), npc_stats(w).get("grade")) for w in ZZ_STUDENTS], len(_zz_rows)))

    ## --- a promotion mid-week: the summary's senior_only follows my grade now ---------------------------------
    python:
        zz_open_state()
        board_refresh()
        check([o["senior_only"] for o in board_summary()["offers"]].count(True) == 1, "at g4 the summary has one senior-only offer")
        grade = "g3"
        check(not [o for o in board_summary()["offers"] if o["senior_only"]] and [o for o in board_offers if o.get("senior_only")],
              "promoted to g3 mid-week, no summary offer asks for a senior partner (the posted cards are unchanged)",
              [(o["grade"], o["senior_only"]) for o in board_summary()["offers"]])
        grade = "g4"

    ## --- offers: same week identical, different weeks differ ---------------------------------
    python:
        _a, _b = board_generate(3), board_generate(3)
        check(_a == _b, "offers are identical for the same week")
        _sigs = [[zz_sig(o) for o in board_generate(w)] for w in range(40)]
        _same = [w for w in range(39) if _sigs[w] == _sigs[w + 1]]
        check(not _same and len(set(tuple(s) for s in _sigs)) == 40, "offers differ across weeks (40 weeks, all distinct)", _same)
        _bad = []
        for _g in ("g4", None):
            grade = _g
            for _w in range(60):
                _o = board_generate(_w)
                _low = [o for o in _o if grade_rank(o["grade"]) <= 0 and not o["senior_only"]]
                _up = [o for o in _o if o["grade"] == "g3" and o["senior_only"]]
                if len(_o) != 3 or len(_low) != 2 or len(_up) != 1:
                    _bad.append((_g, _w, [(o["grade"], o["senior_only"]) for o in _o]))
        check(not _bad, "at g4 (and unassessed) the offers are two <= g4 and one g3 senior_only (60 weeks each)", _bad[:3])
        grade = "g3"
        _o = board_generate(5)
        check([o["grade"] for o in _o][2] == "g2" and _o[2]["senior_only"] and all(grade_rank(o["grade"]) <= 1 for o in _o[:2]),
              "at g3: two <= g3 and one g2 senior_only", [(o["grade"], o["senior_only"]) for o in _o])
        grade = "g4"

    ## --- misgrades: 12-22% of g4/g3 offers ---------------------------------------------------------
    python:
        _all = []
        _w = 0
        while len(_all) < 500:
            _all += [o for o in board_generate(_w) if o["grade"] in ("g4", "g3")]
            _w += 1
        _all = _all[:500]
        _mis = [o for o in _all if o["true_grade"] != o["grade"]]
        _rate = 100.0 * len(_mis) / len(_all)
        check(12.0 <= _rate <= 22.0, "over 500 generated offers, 12-22%% of the g4/g3 offers are misgraded (%.1f%%)" % _rate, _rate)
        check(all(o["true_grade"] == ("g3" if o["grade"] == "g4" else "g2") for o in _mis), "a misgrade is exactly one step higher")
        grade = "g3"
        _hi = [o for w in range(100) for o in board_generate(w) if o["grade"] in ("g2", "s1")]
        check(_hi and all(o["true_grade"] == o["grade"] for o in _hi), "g2 postings are never misgraded", len(_hi))
        grade = "g4"

    ## --- parts that fit together ---------------------------------------------------------------------------
    python:
        zz_open_state()
        _misfit = []
        for _g in ("g4", "g3", "g2"):
            grade = _g
            for _w in range(150):
                for _o in board_generate(_w):
                    _tc = board_resolve(_o, "megumi", _w * 7 + 1, "Morning")["true_curse"]
                    for _k in (_o["curse"], _tc):
                        if not (_board_fits(_k, BOARD_CURSE_FITS, _o["place"]) and _board_fits(_k, BOARD_CURSE_CASE, _o["case"])):
                            _misfit.append((_w, _o["title"], _o["case"], _k))
                    if not _board_fits(_o["case"], BOARD_CASE_FITS, _o["place"]):
                        _misfit.append((_w, _o["title"], _o["case"]))
        grade = "g4"
        check(not _misfit, "every card's case and curse (and a misgrade's real curse) fit its place (450 boards)", _misfit[:4])

    ## --- partners -------------------------------------------------------------------------------------
    python:
        zz_open_state()
        _never = ("gojo", "yaga", "utahime", "shoko", "ijichi")
        _leak, _offc, _seen_off = [], [], set()
        for _d in range(1, 15):
            day = _d
            roll_gojo()
            for _per in PERIODS:
                period = _per
                _p = board_partners()
                _leak += [(_d, _per, w) for w in _p if w in _never]
                _offc += [(_d, _per, w) for w in _p if char_location(w) is None]
                _seen_off |= set(w for w in ZZ_STUDENTS if char_location(w) is None)
        check(not _leak, "gojo, yaga, utahime, shoko and ijichi are never offered as partners (14 days x 5 periods)", _leak[:5])
        check(not _offc, "nobody off campus is ever offered as a partner", _offc[:5])
        check(_seen_off, "the sweep met students off campus (so the rule was exercised)", sorted(_seen_off))
        zz_open_state()
        _senior_offer = [o for o in board_generate(0) if o["senior_only"]][0]
        _sp = board_partners(_senior_offer)
        check(_sp and all(grade_rank(npc_stats(w)["grade"]) > 0 for w in _sp) and "yuji" not in _sp,
              "a senior-only job offers only partners who outrank me", _sp)
        _rows = dict((r[0], r) for r in board_partner_rows(_senior_offer))
        check("yuji" in _rows and not _rows["yuji"][1] and "senior" in _rows["yuji"][2], "Yuji is listed as unable to come on a senior job, with the reason", _rows.get("yuji"))
        roster = ["shoko", "gojo", "yaga", "utahime", "ijichi"]
        check(board_partners() == [], "with no student on the roster there is no partner (no going alone)", board_partners())
        check(board_take_reason(board_generate(0)[0]) == "Nobody on campus to take along", "and the card says so", board_take_reason(board_generate(0)[0]))
        roster = ["yuji", "shoko", "gojo", "yaga", "utahime", "ijichi"]
        period = "Night"
        check(board_take_reason(board_generate(0)[0]) == "Evenings: Utahime doesn't send anyone out after dark",
              "at Night the card gives the after-dark reason first", board_take_reason(board_generate(0)[0]))

    ## --- tool drops wait for the armory (D10) ------------------------------------------------------------------
    python:
        zz_open_state()
        _g4 = [o for o in board_generate(0) if o["grade"] == "g4"][0]
        _g3 = [o for o in board_generate(0) if o["grade"] == "g3"][0]
        check("slaughter_demon" not in board_drops_now(_g4), "no cursed tool drops before Maki opens the armory", board_drops_now(_g4))
        _ktool = [r for r in (board_resolve(_g4, "maki", d) for d in range(1, 400)) if "slaughter_demon" in r["drops"]]
        check(not _ktool, "and none is ever rolled (400 runs)", len(_ktool))
        flag("armory_open")
        check("slaughter_demon" in board_drops_now(_g4) and "nunchaku" not in board_drops_now(_g3),
              "with the armory open: the Grade 4 tool can drop, a Grade 3 tool can't while I'm Grade 4", (board_drops_now(_g4), board_drops_now(_g3)))
        _ktool = [r for r in (board_resolve(_g4, "maki", d) for d in range(1, 400)) if "slaughter_demon" in r["drops"]]
        check(_ktool, "and it does drop now (400 runs)", len(_ktool))
        inventory = {"slaughter_demon": 1, "paper_ward": 1}
        check("slaughter_demon" not in board_drops_now(_g4) and "paper_ward" not in board_drops_now(_g4) and "sealing_talisman" in board_drops_now(_g4),
              "a card never lists a talisman or tool I already own", board_drops_now(_g4))
        board_offers = [dict(_g4)]
        board_week = 0
        check(board_summary()["offers"][0]["drop"] == board_drops_now(_g4), "the summary's offers list only what can still drop")
        zz_open_state()

    ## --- 200 trials: a g4 job with Megumi -------------------------------------------------------------
    python:
        zz_open_state()
        _trials, _w = [], 0
        while len(_trials) < 200:
            for _o in board_generate(_w):
                if _o["grade"] == "g4" and len(_trials) < 200:
                    _trials.append(board_resolve(_o, "megumi", _w * 7 + 1 + len(_trials) % 5, PERIODS[len(_trials) % 3]))
            _w += 1
        _clean = len([r for r in _trials if r["outcome"] == "clean"])
        _true4 = [r for r in _trials if r["true_grade"] == "g4"]
        note("200 trials", "fresh Grade 4 player (power %.1f) with Megumi (%.1f): clean %d, costly %d, withdrew %d; misgraded %d; clean on true-g4 jobs %d/%d" % (
            zz_power("mc"), zz_power("megumi"), _clean, len([r for r in _trials if r["outcome"] == "costly"]),
            len([r for r in _trials if r["outcome"] == "withdrew"]), len([r for r in _trials if r["misgraded"]]),
            len([r for r in _true4 if r["outcome"] == "clean"]), len(_true4)))
        check(_clean >= 160, "over 200 trials, a g4 job with Megumi is clean at least 80%% of the time (%d/200)" % _clean, _clean)
        _r = board_resolve(board_generate(0)[0], "megumi", 3, "Noon")
        check(_r == board_resolve(board_generate(0)[0], "megumi", 3, "Noon"), "a run's result is fixed by offer id and day")

    ## --- narration: every combination, 6-10 lines, first person -----------------------------------------------
    python:
        _nl, _badn, _exprs = [], [], set()
        for _who in BOARD_PARTNER_KEYS:
            for _out in ("clean", "costly", "withdrew"):
                for _tw in BOARD_TWIST_ORDER:
                    for _mis in (False, True):
                        for _per in (("Morning", "Afternoon") if _tw == "daylight" else ("Morning",)):
                            _res = zz_fake_res(_who, _out, _tw, _mis, _per)
                            _sc = board_script(_res)
                            _says = [s for s in _sc if s[0] == "say"]
                            if not 6 <= len(_says) <= 10:
                                _badn.append((_who, _out, _tw, _mis, len(_says)))
                            _exprs |= set((s[1], s[2]) for s in _sc if s[0] == "show")
                            if True:     # every twist, for a full read-through
                                _nl.append("== %s · %s · twist %s · %s%s" % (_who, _out, _tw, "misgraded" if _mis else "as filed", " · " + _per if _tw == "daylight" else ""))
                                for s in _says:
                                    _nl.append("%s: %s" % (s[1] or "narration", s[2]))
                                _nl.append("")
        check(not _badn, "every run's narration is 6-10 lines (%d combinations)" % (len(BOARD_PARTNER_KEYS) * 3 * 7 * 2), _badn[:4])
        _ok_expr = ("neutral", "happy", "serious", "angry", "surprised", "sad")
        _tagged = ("yuji", "megumi", "nobara", "maki", "panda", "toge", "utahime", "ijichi")
        check(all(w in _tagged and e in _ok_expr for w, e in _exprs), "narration shows only tagged characters with the six expressions", sorted(_exprs))
        _txt = " ".join(s[2] for s in board_script(zz_fake_res("nobara", "clean", "dark", True)) if s[0] == "say")
        _lit = ("Ka" + "ito", "Ama" + "giri")     # spelled apart so check_content doesn't flag the harness
        check(not any(n in _txt for n in _lit) and "mc" not in [s[1] for s in board_script(zz_fake_res("nobara", "clean", "dark", True)) if s[0] == "show"],
              "no literal name, and I never appear on screen")
        with open(os.path.join(zz_smoke_state.shots, "narration.txt"), "w") as _f:
            _f.write("\n".join(_nl) + "\n")
        check(_validate_board() == [], "the WP4 validator finds nothing", _validate_board())
        _pl = [l for w in BOARD_PARTNER_KEYS for k in ("arrive", "win", "hurt") for l in (PARTNER_LINES[w][k][0], PARTNER_LINES[w][k][2])]
        check(not [l for l in _pl if "Grade" in l], "no partner line names a grade (the job may be any grade)")
        _wd = [s[2] for s in board_script(zz_fake_res("nobara", "withdrew", "none", False)) if s[0] == "say"]
        check(not [l for l in _wd if "dead" in l.lower()], "a withdrawal never says the curse is dead", _wd)
        _wc = " ".join(s[2] for s in board_script(zz_fake_res("yuji", "withdrew", "civilian", False)) if s[0] == "say")
        check("the man clear" in _wc, "a withdrawal with someone inside gets them out too")
        check("guard" not in _wc and "night" not in BOARD_TWIST_LINES["civilian"].lower(),
              "the civilian inside fits any place and any hour (no night guard)", BOARD_TWIST_LINES["civilian"])
        check("card warned" in BOARD_TWIST_LINES["split"] and "file said one" not in BOARD_TWIST_LINES["split"].lower(),
              "the split twist agrees with the card that warned of two", BOARD_TWIST_LINES["split"])
        check("the second" not in BOARD_TWIST_LINES["split"], "the split line doesn't say 'the second' (Last Light's word)", BOARD_TWIST_LINES["split"])
        check("Dad" not in PARTNER_LINES["panda"]["hurt"][2] and "Yaga" in PARTNER_LINES["panda"]["hurt"][2],
              "Panda calls Yaga by name", PARTNER_LINES["panda"]["hurt"][2])
        check(PARTNER_LINES["toge"]["hurt"][0].endswith("before I can thank him."), "Toge waves off my thanks", PARTNER_LINES["toge"]["hurt"][0])
        ## Expressions follow the beat: surprised at the misgrade, serious when it goes wrong.
        _sc = board_script(zz_fake_res("panda", "costly", "none", True))
        _i_mis = [i for i, st in enumerate(_sc) if st[0] == "say" and st[2].startswith("Whoever wrote the report")][0]
        _i_out = [i for i, st in enumerate(_sc) if st[0] == "say" and st[2] == BOARD_OUTCOME_LINES["costly"]][0]
        check(_sc[_i_mis - 1] == ("show", "panda", "surprised") and _sc[_i_out - 1] == ("show", "panda", "serious"),
              "the partner looks surprised at the misgrade and serious when it goes wrong", (_sc[_i_mis - 1], _sc[_i_out - 1]))
        _sc = board_script(zz_fake_res("panda", "clean", "none", False))
        check(("show", "panda", "serious") not in _sc and ("show", "panda", "surprised") not in _sc,
              "a clean, as-filed job keeps the partner's own expressions")
        ## A new rostered student without lines shows up in the validator.
        ROSTER_ORDER.append("zz_newkid")
        _v = _validate_board()
        ROSTER_ORDER.remove("zz_newkid")
        check(any("zz_newkid" in v for v in _v), "the validator names a rostered student with no PARTNER_LINES", _v)
        ## Placeholder marker (2.3) and the 'later build' line (section 9, risk 8).
        _src = open(os.path.join(config.gamedir, "sb_board.rpy"), encoding="utf-8").read().splitlines()
        _li = [i for i, l in enumerate(_src) if l.startswith("label run_board_mission(")][0]
        _mk = [i for i in range(max(0, _li - 6), _li) if _src[i].strip() == "## PLACEHOLDER — rewrite in phase 3"]
        check(_mk, "the run is marked '## PLACEHOLDER — rewrite in phase 3' above its label", _src[max(0, _li - 6):_li])
        _scr = "\n".join(_src[[i for i, l in enumerate(_src) if l.startswith("screen board_screen(")][0]:])
        _scr = _scr[:_scr.find("\nscreen ", 1)]
        check("later build" in _scr, "board_screen tells the player the fights come in a later build")
        check(PARTNER_LINES["toge"]["arrive"][2] == "Salmon.", "Toge's words are the English onigiri words")

    ## --- a whole job through sb_do_board: Grade 4 with Nobara -------------------------------------------------------
    python:
        zz_open_state()
        board_refresh()
        _o = [o for o in board_offers_open() if not o["senior_only"]][0]
        _oid = _o["id"]
        _before = dict(merit=merit, yen=yen, bond=bonds.get("nobara", 0), log=len(board_log), period=period,
                       stamina=stamina, inv=dict(inventory))
        del ZZ_TRAIN[:]
        del ZZ_TOASTS[:]
        TOAST_SINK[0] = zz_sink
        renpy.call_screen = zz_call_screen
        ZZ_SCREEN_SCRIPT[:] = [("board_screen", ("take", _oid), "board_screen"),
                               ("board_partner", ("partner", "nobara"), "board_partner")]
    $ zz_mark("sb_do_board")
    $ autoplay()
    call sb_do_board
    $ zz_mark("sb_do_board returned")
    $ autoplay(False)
    python:
        renpy.call_screen = _zz_call_screen_real
        TOAST_SINK[0] = None
        check(not ZZ_SCREEN_SCRIPT, "sb_do_board showed board_screen, then board_partner", ZZ_SCREEN_SCRIPT)
        _res = ZZ_LAST_RES[0]
        check(_bl is None and _bres is None and _bs is None and _bp is None,
              "after a job the labels' scratch values are cleared (saves don't carry the script)", (_bl is None, _bres is None, _bs is None, _bp is None))
        check(_res and _res["id"] == _oid and _res["partner"] == "nobara", "the job ran with Nobara", _res and (_res["id"], _res["partner"]))
        note("the Nobara job", "%s (%s, twist %s, %s): power %.1f vs %d -> %s; merit %d, yen %d, drops %s" % (
            _res["title"], grade_label(_res["grade"]), _res["twist"], "misgraded" if _res["misgraded"] else "as filed",
            _res["power"], _res["difficulty"], _res["outcome"], _res["merit"], _res["yen"], _res["drops"]))
        check(PERIODS.index(period) - PERIODS.index(_before["period"]) == 2, "exactly 2 periods pass (Morning -> Afternoon)", (_before["period"], period))
        check(stamina == _before["stamina"] - 25, "the job costs 25 stamina", (_before["stamina"], stamina))
        check(merit - _before["merit"] == _res["merit"] and yen - _before["yen"] == _res["yen"],
              "merit and yen paid once, as resolved", (merit - _before["merit"], _res["merit"], yen - _before["yen"], _res["yen"]))
        check(bonds.get("nobara", 0) - _before["bond"] == BOARD_BOND[_res["outcome"]], "partner bond paid once", bonds.get("nobara"))
        check(ZZ_TRAIN == [("nobara", 6, None)], "train_together(partner, 6) called once", ZZ_TRAIN)
        _got = dict((k, inventory.get(k, 0) - _before["inv"].get(k, 0)) for k in set(inventory) | set(_before["inv"]))
        _want = {}
        for _d in _res["drops"]:
            _want[_d] = _want.get(_d, 0) + 1
        check(dict((k, v) for k, v in _got.items() if v) == _want, "drops paid once", (_got, _want))
        check(len(board_log) == _before["log"] + 1 and board_log[-1]["id"] == _oid, "one log row", len(board_log))
        check(any(t[1] == "bond" and t[2] == "nobara" for t in ZZ_TOASTS) and (not _res["yen"] or any(t[0].startswith("¥") for t in ZZ_TOASTS)),
              "the run toasts its rewards", ZZ_TOASTS)
        _snap = (merit, yen, dict(bonds), len(board_log), period, stamina, dict(inventory), len(ZZ_TRAIN))
        check(board_pay(_res) is False, "paying the same run again is refused")
        check(board_clock(_res) is False, "charging the same run's time again is refused")
        check((merit, yen, dict(bonds), len(board_log), period, stamina, dict(inventory), len(ZZ_TRAIN)) == _snap, "a second board_pay changes nothing")
        check(board_find(_oid) is None, "the taken card is off the board")
        check([c for c in board_taken_cards() if c.get("taken_by") == "mc" and c.get("id") == _oid], "my taken card shows, read-only", board_taken_cards())
        _mine = [c for c in board_taken_cards() if c.get("taken_by") == "mc"]
        check(_mine and board_card_line(_mine[0]) == "Grade 4 · taken by me and Nobara", "it reads 'Grade 4 · taken by me and Nobara'", _mine and board_card_line(_mine[0]))
        period = "Morning"
        stamina = 100
    $ autoplay()
    call run_board_mission(_oid, "nobara")
    $ autoplay(False)
    python:
        check((merit, yen, len(board_log)) == _snap[:2] + (_snap[3],), "taking the same card again pays nothing", (merit, yen, len(board_log)))
        check(period == "Morning", "a refused run takes no time", period)
        _slot = [i for i, o in enumerate(board_offers) if o.get("taken_by") == "mc"][0]
        new_day()
        check(not [o for o in board_offers if o.get("taken_by")] and len(board_offers_open()) == 3
              and board_offers[_slot]["id"] != _oid, "a replacement card goes up the next day", [o["id"] for o in board_offers])
        board_refresh()
        check(len(board_offers_open()) == 3, "board_refresh is idempotent within a day")

    ## --- the debrief comes before the clock: an Afternoon job -------------------------------------------------------
    python:
        zz_open_state(period="Afternoon")
        board_refresh()
        _o = [o for o in board_offers_open() if not o["senior_only"]][0]
        _d0 = day
        _r = board_take(_o["id"], "nobara")
        _heard = []
        for _st in board_script(_r):
            if _st[0] == "say":
                _heard.append((_st[1], period))
            elif _st[0] in ("pay", "clock"):
                board_play(_st, _r)
        _hostsay = [p for w, p in _heard if w == "utahime"]
        check(_hostsay == ["Afternoon"], "an Afternoon job's debrief plays in the Afternoon, during Utahime's hours", _heard)
        check(all(p == "Afternoon" for w, p in _heard), "no line of the job plays after dark", _heard)
        check(period == "Night" and day == _d0 and stamina == 75, "and then the 2 periods and 25 stamina are charged once", (period, day, stamina))
        check(board_clock(_r) is False and period == "Night", "the clock is charged only once")

    ## --- the clock stops where a story beat is waiting (WP11) ------------------------------------------------------
    ## A job costs two periods; one taken in the Morning must not jump a
    ## Noon-only beat (m_roster's st_roster), so the clock stops at Noon when a
    ## beat is waiting there, the way the sandbox loop would find it.
    python:
        def zz_clock_run(beat_periods, beat_loc=None, explore=False, start="Morning"):
            """Take and clock one job with a stand-in story beat registered;
            returns (period, day, stamina, the loop's pick at the end, charged again?)."""
            zz_open_state(period=start, explore_mode=explore)
            board_refresh()
            _d = day
            ev("zz_beat", kind="story", loc=beat_loc, periods=beat_periods, priority=999)
            _e = EVENTS[-1]
            try:
                _o = [o for o in board_offers_open() if not o["senior_only"]][0]
                _r = board_take(_o["id"], "nobara")
                board_pay(_r)
                board_clock(_r)
                _pick = None if explore_mode else pick_event("story", loc=here)
                _again = board_clock(_r)
            finally:
                EVENTS.remove(_e)
            return (period, day - _d, stamina, _pick and _pick["label"], _again)

        zz_open_state()
        check(not board_beat_waiting() and not has_event("story", loc=here),
              "(no real story beat waits in the fixture, so the stand-in is the only one)")
        _c = zz_clock_run(["Noon"])
        check(_c[:4] == ("Noon", 0, 75, "zz_beat"),
              "a Morning job stops at Noon when a Noon-only beat is waiting, and the loop then plays it", _c)
        check(_c[4] is False, "a job stopped early is still charged once", _c)
        _c = zz_clock_run(["Afternoon"])
        check(_c[:4] == ("Afternoon", 0, 75, "zz_beat"),
              "an Afternoon-only beat doesn't shorten a Morning job: 2 periods pass and the beat is there", _c)
        _c = zz_clock_run(["Noon"], beat_loc="zz_elsewhere")
        check(_c[:3] == ("Afternoon", 0, 75), "a Noon beat somewhere else doesn't stop the clock", _c)
        _c = zz_clock_run(["Noon"], explore=True)
        check(_c[:3] == ("Afternoon", 0, 75), "in explore mode (no story beats) the job takes its 2 periods", _c)
        _c = zz_clock_run(["Afternoon"], start="Noon")
        check(_c[:4] == ("Afternoon", 0, 75, "zz_beat"),
              "a Noon job stops at Afternoon for an Afternoon-only beat (m_second_years, m_intensive)", _c)
        _c = zz_clock_run(["Evening"], start="Afternoon")
        check(_c[:4] == ("Evening", 0, 75, "zz_beat"), "an Afternoon job stops at Evening for an Evening beat", _c)
        check(not [e for e in EVENTS if e["label"] == "zz_beat"], "(the stand-in beat is gone again)")

    ## --- a narration frame, for the eye ----------------------------------------------------------
    python:
        _res2 = zz_fake_res("nobara", "clean", "dark", False)
        _sc = board_script(_res2)
        renpy.scene()
        renpy.show(_res2["bg"])
        store.scene_light = light_for_bg(_res2["bg"])
        renpy.show("nobara neutral", at_list=[pos_c])
        renpy.say(nobara, [s for s in _sc if s[0] == "say" and s[1] == "nobara"][0][2], interact=False)
    $ zz_shot("narration_line", wait=0.4)
    scene black

    ## --- refused in the Evening -------------------------------------------------------------------------
    python:
        zz_open_state(period="Evening")
        pin("utahime", "utahime_office")
        board_refresh()
        check(board_open(), "(Utahime pinned to her office for the Evening)")
        _o = board_offers_open()[0]
        _why = board_take_reason(_o)
        check("after dark" in _why and _why.startswith("Evenings:"), "the card says why: Evenings, not after dark", _why)
        _snap = (merit, yen, len(board_log), period, stamina, [o.get("id") for o in board_offers_open()])
        renpy.show_screen("board_screen")
    $ zz_shot("board_screen_evening")
    $ renpy.hide_screen("board_screen")
    $ autoplay()
    call run_board_mission(_o["id"], "nobara")
    $ autoplay(False)
    python:
        check((merit, yen, len(board_log), period, stamina, [o.get("id") for o in board_offers_open()]) == _snap,
              "a job is refused in the Evening: nothing paid, no time, the card stays", (merit, period))
        check(board_refusal(_o, "nobara") == "Utahime doesn't send anyone out after dark.", "the refusal line", board_refusal(_o, "nobara"))
        period = "Night"
        check("after dark" in board_take_reason(_o), "and at Night")
        period = "Morning"
        stamina = 20
        check(board_take_reason(_o) == "Too tired — 25 stamina", "too tired below 25 stamina", board_take_reason(_o))
        stamina = 100

    ## --- the misgrade reveal -----------------------------------------------------------------------------
    python:
        _found = None
        for _w in range(200):
            for _o in board_generate(_w):
                if _o["true_grade"] != _o["grade"] and not _o["senior_only"] and _o["grade"] == "g4":
                    _found = (_w, _o)
                    break
            if _found:
                break
        zz_open_state(day=_found[0] * 7 + 1)
        board_refresh()
        _mid = _found[1]["id"]
        check(board_find(_mid) is not None, "(a misgraded g4 card is on this week's board)")
        _m0 = misgrade_count()
        del ZZ_TOASTS[:]
        TOAST_SINK[0] = zz_sink
    $ autoplay()
    call run_board_mission(_mid, "megumi")
    $ autoplay(False)
    python:
        TOAST_SINK[0] = None
        _bres_m = ZZ_LAST_RES[0]
        check(_bres_m["misgraded"] and misgrade_count() == _m0 + 1, "a misgraded job counts in misgrade_count()", misgrade_count())
        check(has_flag("wakuri_clue"), "a misgraded job sets wakuri_clue")
        check(("Filed as Grade 4. It wasn't.", "mission", None, None) in ZZ_TOASTS, "the toast: Filed as Grade 4. It wasn't.", ZZ_TOASTS)
        check(any(s[0] == "say" and s[1] == "mcthink" and s[2].endswith("It isn't.") for s in board_script(_bres_m)), "the misgrade gets its own narration beat")
        _mis_lines = [s[2] for s in board_script(_bres_m) if s[0] == "say"]
        check(sum(1 for l in _mis_lines if "It isn't" in l) == 1 and any(l.startswith("Whoever wrote the report") for l in _mis_lines),
              "the misgrade beat says \"It isn't\" once (no echo)", [l for l in _mis_lines if "isn't" in l])
        check(board_log[-1]["misgraded"] and board_summary()["misgrades"] == misgrade_count(), "the log and the summary carry the misgrade")

    ## --- the taken card (D12) -----------------------------------------------------------------------------
    python:
        zz_open_state(grade="g3", roster=["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "utahime", "ijichi"])
        _c = board_npc_card()
        check(_c is not None and _c["taken_by"] == "megumi" and _c["grade"] == "g2", "a taken card appears when Megumi outranks me", _c)
        check(_c and board_card_line(_c) == "Grade 2 · taken by Megumi", "it reads 'Grade 2 · taken by Megumi'", _c and board_card_line(_c))
        check(_c in board_taken_cards() and _c in board_summary()["taken"], "it is among the taken cards and in board_summary")
        grade = "g2"
        check(board_npc_card() is None, "no taken card once nobody outranks me", board_npc_card())
        grade = "g3"
        promote("nobara", "g2", "zz", quiet=True)
        check(board_npc_card() and board_npc_card()["taken_by"] in ("megumi", "nobara"), "a newly promoted student can take it too", board_npc_card())
        npc_state = {}

        ## Once the week posts, the card stays when a student joins mid-week.
        zz_open_state(grade="g3", roster=["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "utahime", "ijichi"])
        board_refresh()
        _c1 = board_npc_card()
        check(_c1 and _c1["taken_by"] == "megumi" and board_npc and board_npc.get("taken_by") == "megumi",
              "board_refresh keeps the week's senior card", (_c1, board_npc))
        roster.extend(["maki", "panda", "toge"])
        store.day += 1
        board_refresh()
        check(board_npc_card() == _c1, "the senior card doesn't change when students join mid-week", (_c1, board_npc_card()))
        grade = "g2"
        check(board_npc_card() != _c1, "the card is picked again once its taker no longer outranks me", board_npc_card())
        grade = "g3"
        npc_state = {}
        board_npc = None

    ## --- weekly regeneration and migration 80 --------------------------------------------------------------
    python:
        zz_open_state(day=7)
        board_refresh()
        check(board_week == 0, "day 7 is week 0", board_week)
        new_day()
        check(weekday() == "Mon" and board_week == 1 and [zz_sig(o) for o in board_offers] == [zz_sig(o) for o in board_generate(1)],
              "offers regenerate on Monday (new-day hook)", (weekday(), board_week))
        new_day()
        check(board_week == 1 and [zz_sig(o) for o in board_offers] == [zz_sig(o) for o in board_generate(1)], "and stay put on Tuesday")
        zz_open_state(day=10)
        run_migrations()
        check(len(board_offers) == 3 and board_week == 1, "migration 80: an open board with no offers gets this week's", (len(board_offers), board_week))
        _snap = [dict(o) for o in board_offers]
        run_migrations()
        check(board_offers == _snap, "migration 80 is idempotent")
        zz_open_state(day=10)
        flags.discard("mission_board_open")
        run_migrations()
        check(board_offers == [], "migration 80 leaves a closed board alone")

    ## --- summary and log -------------------------------------------------------------------------------------
    python:
        zz_open_state()
        board_log = [dict(id="zz%d" % i, day=i, grade="g4", true_grade="g4", title="T%d" % i, partner="yuji",
                          outcome="clean", merit=10, yen=3000, drops=[], misgraded=False) for i in range(30)]
        board_refresh()
        _s = board_summary()
        check(set(_s) >= set(["offers", "taken", "log", "misgrades"]), "board_summary has offers, taken, log, misgrades", sorted(_s))
        check(len(_s["log"]) == 10 and _s["log"][0]["id"] == "zz29" and _s["log"][-1]["id"] == "zz20", "the summary's log is the last 10 runs, newest first")
        check(len(_s["offers"]) == 3, "the summary lists this week's offers")
        board_pay(zz_fake_res("yuji", "clean", "none", False))
        check(len(board_log) == 30 and board_log[-1]["id"] == "zz", "board_log keeps the last 30 runs", len(board_log))

    ## --- sb_do_board when closed returns at once --------------------------------------------------------------
    $ here = "courtyard"
    $ _snap = (period, len(board_log), [dict(o) for o in board_offers], merit, stamina)
    call sb_do_board
    $ check((period, len(board_log), [dict(o) for o in board_offers], merit, stamina) == _snap, "sb_do_board returns at once when the board is closed, changing nothing")

    ## --- screens --------------------------------------------------------------------------------------------------
    python:
        zz_open_state(day=4, roster=list(ZZ_EVERYONE))
        board_refresh()
        _mid_card = board_offers[1]
        board_take(_mid_card["id"], "yuji")
        _order = [o.get("id") for o in board_offers]
        store._return = None
        renpy.scene()
        renpy.show_screen("board_screen")
    $ zz_shot("board_screen_taken")
    $ check(board_offers[1].get("taken_by") == "mc" and [o.get("id") for o in board_offers] == _order, "a taken card keeps its slot (the others don't move)", _order)
    $ renpy.hide_screen("board_screen")
    python:
        _sen = [o for o in board_offers_open() if o["senior_only"]][0]
        renpy.show_screen("board_partner", _sen)
    $ zz_shot("board_partner_senior")
    $ renpy.hide_screen("board_partner")
    $ renpy.show_screen("board_partner", {})
    $ zz_shot("board_partner_empty")
    $ renpy.hide_screen("board_partner")
    python:
        grade = None
        board_offers = []
        board_week = -1
        board_refresh()
        renpy.show_screen("board_screen")
    $ zz_shot("board_screen_unassessed")
    $ renpy.hide_screen("board_screen")
    python:
        _want = ["board_screen", "board_screen_taken", "board_screen_evening", "board_screen_unassessed", "board_screen_ijichi",
                 "board_partner", "board_partner_senior", "board_partner_empty", "narration_line"]
        _missing = []
        for _n in _want:
            _fn = os.path.join(zz_smoke_state.shots, _n + ".png")
            if not ZZ_SHOTS.get(_n) or not os.path.exists(_fn) or os.path.getmtime(_fn) < ZZ_T0[0] - 1:
                _missing.append(_n)
        check(not _missing, "screenshots are saved (%d, all taken this run)" % len(_want), _missing)

    $ finish()
