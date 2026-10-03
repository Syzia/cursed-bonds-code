## tools/smoke/p2_gear.rpy -- P4a's package harness: grades on cards and gear
## requirements (docs/PHASE2_DESIGN.md section 7 "P4a", 4.8, 4.9, D27, D28).
##
##   tools/smoke.sh tools/smoke/p2_gear.rpy
##
## Every acceptance bullet of P4a is a check whose name starts "ACC". Items go
## in through give_item, grades through promote, stats through gain (R5). The
## acceptance line that needs another package is a NOTE that says so (7.3).
## Screenshots go to shots/p2_gear/: the board, the partner picker, the armory
## with its checklists, the grade card for Special Grade (with the sheen and
## with the flat stand-in), the combat header, and a worst-case picture
## (zz_worst) of each full screen P4a owns.

init 999 python:
    import builtins
    import json
    import os
    import re

    ZZ_GEAR_EVERYONE = ["yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "gojo", "yaga",
                        "utahime", "ijichi"]
    ZZ_GEAR_SHOTS = builtins.dict()

    def zz_gear_shot(name, **kw):
        ZZ_GEAR_SHOTS[name] = bool(shot(name, **kw))
        return ZZ_GEAR_SHOTS[name]

    def zz_gear_state(key=None, **kw):
        """A clean item state at a grade: nothing owned, held or worn, the
        grade reached through promote (which never lowers, so it starts from
        None), the stats given."""
        base = builtins.dict(grade=None, control=12, output=10, insight=10, arc=1,
                             equipped_tool=None, equipped_talismans=[])
        base.update(kw)
        fixture(**base)
        ## Emptied directly: an empty container has no shape to get wrong (R5).
        store.inventory = {}
        for f in ("spear_unsealed", "yaga_signature", "armory_open"):
            store.flags.discard(f)
        if key:
            promote("mc", key, quiet=True)
        toast_clear()

    def zz_gear_boom(*a, **kw):
        return 1 // 0

    def zz_gear_raise(stat, to):
        """Raise a stat to a value through gain, a point at a time."""
        for _i in range(400):
            if getattr(store, stat) >= to:
                break
            gain(stat, 1, quiet=True)
        return getattr(store, stat)

    def zz_gear_fills(screen):
        """The colour of every Solid in a shown screen's tree, as a set."""
        zz_render()
        out = builtins.set()
        sc = renpy.get_screen(screen)
        if sc is None:
            return out

        def each(d):
            if isinstance(d, renpy.display.imagelike.Solid):
                out.add(tuple(renpy.easy.color(d.color)))

        sc.visit_all(each)
        return out

    def zz_gear_rgba(c):
        return tuple(renpy.easy.color(c))

    def zz_gear_text_colors(screen, wanted):
        """The colour of every Text on a shown screen whose string is `wanted`."""
        zz_render()
        return [tuple(d.style.color) for d in zz_text_nodes(screen) if zz_text_string(d) == wanted]

    def zz_gear_board(**kw):
        """A Monday morning in Utahime's office with the board open."""
        base = builtins.dict(day=1, period="Morning", here="utahime_office", stamina=100,
                             roster=builtins.list(ZZ_GEAR_EVERYONE), board_week=-1, board_npc=None,
                             schedule_overrides={}, explore_mode=False)
        base.update(kw)
        fixture(**base)
        store.board_offers = []
        store.flags.discard("utahime_leads_kyoto")
        flag("mission_board_open")
        flag("utahime_arrived")
        roll_gojo()
        board_refresh()

    def zz_gear_returns(screen):
        """The value of every Return action on a shown screen's buttons."""
        zz_render()
        out = builtins.list()
        seen = builtins.set()

        def each(d):
            if id(d) in seen:
                return
            seen.add(id(d))
            a = getattr(d, "action", None)
            if a is None:
                return
            for x in (a if isinstance(a, (builtins.list, builtins.tuple)) else [a]):
                if isinstance(x, Return):
                    out.append(x.value)

        sc = renpy.get_screen(screen)
        if sc is not None:
            sc.visit_all(each)
        return out

    ZZ_GEAR_REAL_LOADABLE = builtins.list([None])

    def zz_gear_no_sheen(fn, *args, **kwargs):
        """renpy.loadable with the Special Grade strip reported missing."""
        if fn == GRADE_SHEEN:
            return False
        return ZZ_GEAR_REAL_LOADABLE[0](fn, *args, **kwargs)


label zz_smoke:

    $ settle(mc_name="Tester", mc_surname="Harness", day=3, period="Morning", here="courtyard")
    $ _zz_bound0 = builtins.set(bound_specials)

    ## --- ACC 1: the racks at Grade 4 equal the baseline --------------------------------------
    python:
        for _zz_f in ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access"):
            flag(_zz_f)
        done_events.add("st_roll_call")
        zz_gear_state("g4")
        period = "Noon"
        here = "storehouse"
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_path = os.path.join(_zz_root or "", "tools", "smoke", "baseline_p0.json")
        if _zz_root and os.path.isfile(_zz_path):
            with open(_zz_path, encoding="utf-8") as _zz_fh:
                _zz_base = json.load(_zz_fh)
            _zz_want = [tuple(r) for r in _zz_base["fresh"]["armory_tools"]]
            check(_zz_base["fresh"]["grade"] == "g4" and len(_zz_want) == 5,
                  "the baseline's fresh fixture is Grade 4 with five rack rows", _zz_base["fresh"]["grade"])
            check(armory_tools() == _zz_want,
                  "ACC armory_tools() gives the five (state, reason) pairs of baseline_p0.json at Grade 4",
                  (armory_tools(), _zz_want))
            promote("mc", "g3", quiet=True)
            check(armory_tools() == [tuple(r) for r in _zz_base["rich"]["armory_tools"]],
                  "armory_tools() also equals the baseline's Grade 3 rows", armory_tools())
        else:
            check(False, "ACC armory_tools() against baseline_p0.json: SMOKE_ROOT has no baseline", _zz_path)

    ## --- ACC 2: the tools' checklists -----------------------------------------------------------
    python:
        zz_gear_state("g4")
        _zz_spear = item_requirements("inverted_spear")
        check(len(_zz_spear) == 4 and not any(ok for line, ok in _zz_spear),
              "ACC item_requirements('inverted_spear') has four lines, all unmet on a fresh game", _zz_spear)
        check([line for line, ok in _zz_spear] == ["Arc Two", "Special Grade", "The seal broken", "Yaga's signature"],
              "the spear asks for Arc Two, Special Grade, the seal and Yaga's signature (D27)", _zz_spear)
        check(all(isinstance(line, str) and line and isinstance(ok, bool)
                  for i in ITEM_REQS for line, ok in item_requirements(i)),
              "item_requirements returns (str, bool) pairs for every row")
        check(item_requirements("paper_ward") == [] and item_requirements_met("paper_ward") is True
              and item_requirements("zz_nothing") == [] and item_requirements_met("zz_nothing") is True,
              "an item with no row has no checklist and meets it")
        check(not item_requirements_met("inverted_spear") and item_first_unmet("inverted_spear")[1] == "Arc Two",
              "the spear's checklist is unmet; its first unmet line is Arc Two", item_first_unmet("inverted_spear"))

        zz_gear_state("g2", output=46)
        _zz_a = item_requirements("playful_cloud")
        zz_gear_raise("output", 49)
        _zz_b = item_requirements("playful_cloud")
        gain("output", 1, quiet=True)
        _zz_c = item_requirements("playful_cloud")
        check(_zz_a == [("Grade 2", True), ("Output 50 · I have 46", False)]
              and _zz_b == [("Grade 2", True), ("Output 50 · I have 49", False)]
              and output == 50 and _zz_c == [("Grade 2", True), ("Output 50", True)],
              "ACC Playful Cloud's Output line flips when output crosses 50 (through gain)", (_zz_a, _zz_b, _zz_c, output))
        check(item_requirements_met("playful_cloud") is True, "and then its checklist is met")
        check(item_requirements("split_soul") == [("Semi-Grade 1", False), ("Insight 60 · I have 10", False)],
              "Split Soul Katana: Semi-Grade 1, Insight 60 (D27)", item_requirements("split_soul"))

        _zz_bad = []
        _zz_n = 0
        for _zz_id, _zz_rows in ITEM_REQS.items():
            _zz_cap = GRADES[ITEMS[_zz_id]["grade"]]["stat"]
            for _zz_r in _zz_rows:
                if _zz_r[0] == "stat" and _zz_r[1] in ("control", "output"):
                    _zz_n += 1
                    if _zz_cap is not None and not _zz_r[2] <= _zz_cap:
                        _zz_bad.append((_zz_id, _zz_r, _zz_cap))
        check(_zz_n >= 3 and not _zz_bad,
              "ACC every Control or Output threshold is at most GRADES[<the item's grade>]['stat'] (%d rows)" % _zz_n, _zz_bad)
        check(item_validate_reqs() == [], "item_validate_reqs() passes P4a's rows", item_validate_reqs())
        check(builtins.set(ITEM_REQS) >= {"inverted_spear", "playful_cloud", "split_soul", "afterglow", "black_sun"},
              "ITEM_REQS holds the three tools and the two Grade 1 talismans", builtins.sorted(ITEM_REQS))
        check(ITEM_REQS["black_sun"] == [("grade", "g1"), ("stat", "output", 80)], "Black Sun: Grade 1, Output 80",
              ITEM_REQS["black_sun"])

    ## --- ACC 3: a talisman has a checklist ---------------------------------------------------------
    python:
        zz_gear_state("g4", control=30)
        _zz_ag = item_requirements("afterglow")
        check(len(_zz_ag) == 2 and [l for l, ok in _zz_ag] == ["Grade 1", "Control 80 · I have 30"]
              and not any(ok for l, ok in _zz_ag),
              "ACC item_requirements('afterglow') has two lines (Grade 1, Control 80)", _zz_ag)
        give_item("afterglow", quiet=True)
        check(can_wear("afterglow") == (False, "Needs Grade 1"),
              "below Grade 1 the existing grade check still answers first", can_wear("afterglow"))

        zz_gear_state("g1", control=62)
        check(can_wear("afterglow") == (False, "Not in my inventory"),
              "not owned: the existing check answers before the checklist", can_wear("afterglow"))
        give_item("afterglow", quiet=True)
        check(can_wear("afterglow") == (False, "Control 80 · I have 62") and not equip_talisman("afterglow")
              and equipped_talismans == [],
              "ACC can_wear('afterglow') refuses with the first unmet line after its existing checks",
              (can_wear("afterglow"), equipped_talismans))
        give_item("paper_ward", quiet=True)
        give_item("steady_hand", quiet=True)
        give_item("deep_well", quiet=True)
        give_item("iron_seal", quiet=True)
        for _zz_t in ("paper_ward", "steady_hand", "deep_well", "iron_seal"):
            equip_talisman(_zz_t)
        check(len(equipped_talismans) == 4 and can_wear("afterglow")[1].startswith("No free slot"),
              "with every slot full the slot reason answers before the checklist", can_wear("afterglow"))
        unequip_talisman("iron_seal")
        zz_gear_raise("control", 80)
        check(control == 80 and can_wear("afterglow") == (True, "") and equip_talisman("afterglow")
              and "afterglow" in equipped_talismans,
              "at Control 80 Afterglow goes on", (control, can_wear("afterglow"), equipped_talismans))
        gain("control", -30, quiet=True)
        check(control == 50 and not item_requirements_met("afterglow"), "Control drops to 50: the checklist is unmet now")
        ensure_state()
        _zz_worn1 = builtins.list(equipped_talismans)
        fixture(save_version=0)
        ensure_state()
        check("afterglow" in _zz_worn1 and "afterglow" in equipped_talismans and save_version == SAVE_VERSION
              and can_wear("afterglow") == (False, "Already worn"),
              "ACC a talisman already worn stays worn after ensure_state(), whatever its checklist says (D28)",
              (_zz_worn1, equipped_talismans, can_wear("afterglow")))
        unequip_talisman("afterglow")
        check(can_wear("afterglow") == (False, "Control 80 · I have 50") and not equip_talisman("afterglow"),
              "taken off, it can't go back on until the checklist is met again (putting on anew)", can_wear("afterglow"))
        toast_clear()

    ## --- ACC 4: a tool in my hand stays; taking one in hand anew is gated ---------------------------
    python:
        zz_gear_state("g2", output=46)
        zz_gear_raise("output", 50)
        give_item("playful_cloud", quiet=True)
        check(equipped_tool == "playful_cloud", "with the checklist met, a first tool goes straight into an empty hand",
              equipped_tool)
        gain("output", -20, quiet=True)
        check(output == 30 and not item_requirements_met("playful_cloud"), "Output drops to 30: the checklist is unmet now")
        ensure_state()
        _zz_tool1 = equipped_tool
        fixture(save_version=0)
        ensure_state()
        check(_zz_tool1 == "playful_cloud" and equipped_tool == "playful_cloud" and save_version == SAVE_VERSION
              and can_hold("playful_cloud") == (True, ""),
              "ACC a tool equipped before an unmet requirement is still equipped_tool after ensure_state() (D28)",
              (_zz_tool1, equipped_tool, can_hold("playful_cloud")))
        give_item("slaughter_demon", quiet=True)
        check(equip_tool("slaughter_demon") and equipped_tool == "slaughter_demon", "I can still put it down for another tool")
        check(has_item("playful_cloud") and can_hold("playful_cloud") == (False, "Output 50 · I have 30")
              and not equip_tool("playful_cloud") and equipped_tool == "slaughter_demon",
              "ACC can_hold refuses a tool that is owned but not in hand, with the unmet line as its reason",
              (can_hold("playful_cloud"), equipped_tool))
        zz_gear_state("g4")
        give_item("playful_cloud", quiet=True)
        check(equipped_tool is None and can_hold("playful_cloud") == (False, "Needs Grade 2"),
              "below its grade a granted tool stays out of my hand: Needs Grade 2", (equipped_tool, can_hold("playful_cloud")))
        _zz_none = "zz_nothing"     ## not a literal in the call: _validate_items reads the scripts
        check(can_hold(None) == (True, "") and can_hold(_zz_none) == (False, "Not a cursed tool")
              and can_hold("nunchaku") == (False, "Not in my inventory")
              and can_hold("inverted_spear") == (False, "Sealed — Arc Two"),
              "can_hold's earlier reasons are unchanged",
              (can_hold(None), can_hold(_zz_none), can_hold("nunchaku"), can_hold("inverted_spear")))

    ## --- 4.9: the racks hold a tool back on an unmet line -------------------------------------------
    python:
        zz_gear_state("g3", control=30)
        _zz_saved = builtins.dict(ITEM_REQS)
        try:
            ITEM_REQS["nunchaku"] = [("grade", "g3"), ("stat", "control", 50)]
            _zz_s1 = armory_state("nunchaku")
            _zz_take1 = armory_take("nunchaku")
            ITEM_REQS["nunchaku"] = [("grade", "g2"), ("stat", "control", 50)]
            _zz_s2 = armory_state("nunchaku")
            ITEM_REQS["nunchaku"] = [("grade", "g3"), ("stat", "control", 30)]
            _zz_s3 = armory_state("nunchaku")
        finally:
            ITEM_REQS.clear()
            ITEM_REQS.update(_zz_saved)
        check(_zz_s1 == ("sealed", "Control 50 · I have 30") and not _zz_take1 and not has_item("nunchaku"),
              "a rack tool with an unmet line is sealed, with that line as its reason, and can't be taken", (_zz_s1, _zz_take1))
        check(_zz_s2 == ("sealed", "Sealed until Grade 2"), "an unmet grade still reads 'Sealed until Grade 2'", _zz_s2)
        check(_zz_s3 == ("take", ""), "with every line met it can be taken", _zz_s3)
        check(armory_state("nunchaku") == ("take", "") and armory_state("playful_cloud") == ("story", "Story reward")
              and armory_state("inverted_spear") == ("arcii", "Sealed — Arc Two"),
              "sealed-until-Arc-Two, owned and story rows are decided before the checklist, as before")
        check(armory_checklist("nunchaku") == [("Grade 3", True)] and armory_checklist("slaughter_demon") == [("Grade 4", True)]
              and armory_checklist("playful_cloud") == item_requirements("playful_cloud"),
              "the armory's checklist for a tool with no row is its grade", armory_checklist("nunchaku"))
        ## Review round 1: an owned tool with no row never shows a cross (can_hold allows it).
        zz_gear_state("g4")
        _zz_before = armory_checklist("nunchaku")
        give_item("nunchaku", quiet=True)
        check(_zz_before == [("Grade 3", False)] and armory_checklist("nunchaku") == [("Grade 3", True)]
              and can_hold("nunchaku") == (True, ""),
              "the armory's stand-in line is a cross below the grade, and a tick once I own the tool",
              (_zz_before, armory_checklist("nunchaku"), can_hold("nunchaku")))

    ## --- Review round 1: a rearrange never loses a talisman worn under D28 --------------------------
    python:
        zz_gear_state("g1", control=62)
        zz_gear_raise("control", 80)
        for _zz_t in ("paper_ward", "afterglow", "steady_hand"):
            give_item(_zz_t, quiet=True)
        equip_talisman("paper_ward")
        equip_talisman("afterglow")
        gain("control", -60, quiet=True)
        check(control == 20 and equipped_talismans == ["paper_ward", "afterglow"] and not item_requirements_met("afterglow"),
              "an old-save state: Afterglow worn in slot 2 with its checklist unmet", (control, equipped_talismans))
        ## What the journal's jr_wear does for slot 0: take off the slot and the later ones, wear the new one, put the later ones back.
        unequip_talisman("paper_ward")
        unequip_talisman("afterglow")
        _zz_new = equip_talisman("steady_hand")
        _zz_plain = equip_talisman("afterglow")
        _zz_mid = builtins.list(equipped_talismans)
        _zz_back = item_wear_again("afterglow")
        check(_zz_new and not _zz_plain and _zz_mid == ["steady_hand"] and _zz_back
              and equipped_talismans == ["steady_hand", "afterglow"] and item_wear_again("afterglow")
              and equipped_talismans == ["steady_hand", "afterglow"],
              "item_wear_again puts a talisman back whatever its checklist says (equip_talisman alone would not)",
              (_zz_new, _zz_plain, _zz_mid, _zz_back, equipped_talismans))
        unequip_talisman("afterglow")
        check(can_wear("afterglow") == (False, "Control 80 · I have 20") and item_wear_check("afterglow") == can_wear("afterglow")
              and item_wear_check("afterglow", checklist=False) == (True, ""),
              "can_wear itself still asks the checklist", can_wear("afterglow"))
        zz_gear_state("g4", control=30)
        give_item("afterglow", quiet=True)
        give_item("black_sun", quiet=True)
        _zz_none2 = "zz_nothing"
        check(not item_wear_again("afterglow") and not item_wear_again(_zz_none2) and equipped_talismans == []
              and item_wear_check("afterglow", checklist=False) == (False, "Needs Grade 1"),
              "item_wear_again keeps every other test of can_wear (grade, kind)", (equipped_talismans,))
        zz_gear_state("g1", control=30)
        give_item("paper_ward", quiet=True)
        give_item("steady_hand", quiet=True)
        give_item("deep_well", quiet=True)
        give_item("iron_seal", quiet=True)
        give_item("afterglow", quiet=True)
        for _zz_t in ("paper_ward", "steady_hand", "deep_well", "iron_seal"):
            equip_talisman(_zz_t)
        check(len(equipped_talismans) == talisman_slots() and not item_wear_again("afterglow")
              and "afterglow" not in equipped_talismans,
              "item_wear_again keeps the slot test", (equipped_talismans, talisman_slots()))
        toast_clear()

    ## --- Review round 1: a bad checklist row reads "?", a real error is not hidden --------------------
    python:
        zz_gear_state("g4")
        check(item_req_line(("stat", "control")) == ("?", False) and item_req_line(("zz_kind", 1)) == ("?", False)
              and item_req_line(("stat", "zz_no_such_stat", 5)) == ("?", False) and item_req_line(None) == ("?", False),
              "a malformed requirement (short row, unknown kind, unknown stat, not a row) reads '?' and unmet")
        _zz_saved_label = store.grade_label
        _zz_raised = False
        try:
            store.grade_label = zz_gear_boom
            try:
                item_req_line(("grade", "g2"))
            except ZeroDivisionError:
                _zz_raised = True
        finally:
            store.grade_label = _zz_saved_label
        check(_zz_raised and item_req_line(("grade", "g2")) == ("Grade 2", False),
              "an error that is not a malformed row is raised, not turned into '?'", _zz_raised)

    ## --- ACC 5: the catalogue is untouched -----------------------------------------------------------
    python:
        _zz_short = [i for i, it in ITEMS.items() if len(it) != 12 or builtins.set(it) != builtins.set(_ITEM_FIELDS)]
        check(len(_ITEM_FIELDS) == 12 and not _zz_short, "ACC every ITEMS record still has exactly 12 fields", _zz_short)
        check(_validate_items() == [], "ACC _validate_items passes", _validate_items())
        _zz_writes = []
        _zz_re = re.compile(r"bound_specials\s*(=[^=]|\.(add|update|discard|remove|clear|pop)\b|\|=|-=)")
        for _zz_fn in renpy.list_files():
            if not _zz_fn.endswith(".rpy") or _zz_fn.startswith("zz_smoke"):
                continue
            with renpy.open_file(_zz_fn, encoding="utf-8") as _zz_fh:
                for _zz_ln, _zz_line in enumerate(_zz_fh.read().splitlines(), 1):
                    if _zz_re.search(_zz_line) and not _zz_line.startswith("default bound_specials = set()"):
                        _zz_writes.append("%s:%d" % (_zz_fn, _zz_ln))
        check(not _zz_writes and bound_specials == _zz_bound0 == builtins.set(),
              "ACC bound_specials is never written (no game file writes it; it is still empty after every check above)",
              (_zz_writes, bound_specials))

    ## --- 7.3: what waits for another package -----------------------------------------------------------
    python:
        note("deferred to P8 (7.3)", "putting a Black Market talisman on through this checklist needs P4b's sb_market.rpy "
             "rows (ITEM_REQS.update) and stock; with P4b's stub market_exists() is %r here" % (market_exists(),))
        note("owner check, P3's screen", "a talisman's checklist in the journal's Equipment and Inventory tabs is drawn "
             "by ui_journal.rpy (P3) from item_requirements(); it is not on any screen P4a owns")

    ## --- 4.8: the board's chips ---------------------------------------------------------------------------
    scene black
    python:
        zz_gear_state("g4")
        zz_gear_board()
        check(BOARD_GRADE_COLOR == {"g4": gui.grade_g4, "g3": gui.grade_g3, "g2": gui.grade_g2, "s1": gui.grade_g1},
              "BOARD_GRADE_COLOR stays defined, re-pointed at the gui.grade_* tokens", BOARD_GRADE_COLOR)
        check(builtins.sorted(o["grade"] for o in board_offers) == ["g3", "g4", "g4"],
              "at Grade 4 the board posts two Grade 4 cards and one Grade 3", [o["grade"] for o in board_offers])
        renpy.show_screen("board_screen")
        _zz_fills = zz_gear_fills("board_screen")
        _zz_texts = zz_texts("board_screen")
        check(zz_gear_rgba(gui.grade_g4) in _zz_fills and zz_gear_rgba(gui.grade_g3) in _zz_fills
              and zz_gear_rgba("#c79bff") not in _zz_fills and zz_gear_rgba("#9d95ae") not in _zz_fills,
              "ACC the board's chips: Grade 4 green, Grade 3 blue (and the old chip colours are gone)",
              builtins.sorted(_zz_fills))
        check(_zz_texts.count("GRADE 4") == 2 and _zz_texts.count("GRADE 3") == 1,
              "each card's chip names its grade", [t for t in _zz_texts if "GRADE" in t])
        check(builtins.sorted(v for v in zz_gear_returns("board_screen")) == builtins.sorted(
              [("take", o["id"]) for o in board_offers] + [("close",)]),
              "board_screen's return values are unchanged: a Take for each card and Close", zz_gear_returns("board_screen"))
    $ zz_gear_shot("board_g4")
    $ check(zz_worst("board_screen"), "zz_worst('board_screen') is saved")
    $ renpy.hide_screen("board_screen")
    python:
        zz_gear_board()
        _zz_senior = [o for o in board_offers_open() if o["senior_only"]][0]
        renpy.show_screen("board_partner", _zz_senior)
        _zz_fills = zz_gear_fills("board_partner")
        _zz_texts = zz_texts("board_partner")
        check(zz_gear_rgba(gui.grade_g2) in _zz_fills and zz_gear_rgba(gui.grade_g1) in _zz_fills
              and "GRADE 2" in _zz_texts and "SEMI-GRADE 1" in _zz_texts,
              "the partner picker's chips: Megumi and Panda purple, Toge red (Semi-Grade 1 shares Grade 1's colour)",
              (builtins.sorted(_zz_fills), [t for t in _zz_texts if "GRADE" in t]))
    $ zz_gear_shot("board_partner_senior")
    $ check(zz_worst("board_partner", _zz_senior), "zz_worst('board_partner') is saved")
    $ renpy.hide_screen("board_partner")

    ## --- 4.9: the armory with its checklists ------------------------------------------------------------
    scene expression graded_bg("storehouse")
    python:
        zz_gear_state("g2", output=32)
        flag("armory_open")
        fixture(here="storehouse", period="Noon")
        give_item("slaughter_demon", quiet=True)
        renpy.show_screen("armory")
        _zz_texts = zz_texts("armory")
        _zz_fills = zz_gear_fills("armory")
        _zz_ticks = _zz_texts.count("✓")
        _zz_cross = _zz_texts.count("✗")
        check("Output 50 · I have 32" in _zz_texts and "Grade 2" in _zz_texts and "Arc Two" in _zz_texts
              and "Yaga's signature" in _zz_texts and "Insight 60 · I have 10" in _zz_texts,
              "the armory draws each tool's checklist under it", [t for t in _zz_texts if len(t) < 30])
        check((_zz_ticks, _zz_cross) == (3, 7),
              "at Grade 2 with Output 32: three ticks (Grade 4, Grade 3, Grade 2) and seven crosses", (_zz_ticks, _zz_cross))
        check(_zz_texts.count("MY GRADE") == 1 and _zz_texts.count("GRADE 2") == 2 and "SPECIAL GRADE" in _zz_texts
              and zz_gear_rgba(gui.grade_g2) in _zz_fills and zz_gear_rgba(gui.grade_g4) in _zz_fills
              and zz_gear_rgba(gui.grade_g1) in _zz_fills,
              "the armory's rows and MY GRADE use the grade chips", ([t for t in _zz_texts if "GRADE" in t], builtins.sorted(_zz_fills)))
        check(builtins.sorted(zz_gear_returns("armory")) == builtins.sorted(
              [("return", "slaughter_demon"), ("take", "nunchaku"), ("close",)]),
              "the armory's return values are unchanged", zz_gear_returns("armory"))
    $ zz_gear_shot("armory_checklists")
    $ check(zz_worst("armory"), "ACC zz_worst('armory') is saved")
    $ renpy.hide_screen("armory")
    python:
        zz_gear_state("g4")
        flag("armory_open")
        renpy.show_screen("armory")
    $ zz_gear_shot("armory_g4")
    $ renpy.hide_screen("armory")

    ## --- 4.8: the grade card ------------------------------------------------------------------------------
    scene expression graded_bg("classroom")
    python:
        renpy.show_screen("grade_card", "sp", "PROMOTED")
        _zz_col = zz_gear_text_colors("grade_card", "Special Grade")
        check(_zz_col == [zz_gear_rgba(grade_color("sp"))] and grade_has_sheen(),
              "the grade card's 64 px label takes grade_color('sp'), with the sheen strip on disk", _zz_col)
    $ zz_gear_shot("grade_card_sp")
    $ check(zz_worst("grade_card", "sp", "PROMOTED"), "zz_worst('grade_card') is saved")
    $ renpy.hide_screen("grade_card")
    python:
        ZZ_GEAR_REAL_LOADABLE[0] = renpy.loadable
        renpy.loadable = zz_gear_no_sheen
        try:
            check(not grade_has_sheen(), "stand-in: with gui/grade_sheen.png missing, grade_has_sheen() is False")
            renpy.show_screen("grade_card", "sp", "PROMOTED")
            zz_gear_shot("grade_card_sp_no_sheen")
            check(zz_gear_rgba(gui.grade_sp) in zz_gear_fills("grade_card"),
                  "stand-in: the Special Grade card still draws, its rule a flat gui.grade_sp",
                  builtins.sorted(zz_gear_fills("grade_card")))
            renpy.hide_screen("grade_card")
        finally:
            renpy.loadable = ZZ_GEAR_REAL_LOADABLE[0]
        for _zz_k, _zz_name in (("g4", "Grade 4"), ("g3", "Grade 3"), ("g2", "Grade 2"), ("s1", "Semi-Grade 1"), ("g1", "Grade 1")):
            renpy.show_screen("grade_card", _zz_k, "PROMOTED")
            _zz_col = zz_gear_text_colors("grade_card", _zz_name)
            check(_zz_col == [zz_gear_rgba(grade_color(_zz_k))], "the grade card's label for %s is in its colour" % _zz_name, _zz_col)
            if _zz_k == "g3":
                zz_gear_shot("grade_card_g3")
            renpy.hide_screen("grade_card")
        renpy.show_screen("grade_card", None, "ASSESSED")
        check(zz_gear_text_colors("grade_card", "Grade 4") == [zz_gear_rgba(gui.grade_g4)],
              "grade_card(None) still shows Grade 4's card, in Grade 4's colour")
        renpy.hide_screen("grade_card")

    ## --- 4.8: the combat header -----------------------------------------------------------------------------
    scene expression "bg alley"
    python:
        zz_gear_state("g4", control=35, output=20)
        fixture(ce=90, ce_max=90, hp=60)
        combat_begin("nade_curse", None, True, "bg alley")
        renpy.show_screen("combat_screen")
        _zz_texts = zz_texts("combat_screen")
        check("GRADE 3" in _zz_texts and "ROUND 1" in _zz_texts and not any("·" in t and "ROUND" in t for t in _zz_texts)
              and zz_gear_rgba(gui.grade_g3) in zz_gear_fills("combat_screen"),
              "the combat header: a grade chip left of ROUND n", [t for t in _zz_texts if "ROUND" in t or "GRADE" in t])
        check(zz_gear_text_colors("combat_screen", "Nade's Shikigami") == [zz_gear_rgba(gui.seal)],
              "the enemy's name stays red", zz_gear_text_colors("combat_screen", "Nade's Shikigami"))
    $ zz_gear_shot("combat_header_g3")
    $ renpy.hide_screen("combat_screen")
    python:
        combat_begin("alley_curse", None, False, "bg alley")
        renpy.show_screen("combat_screen")
        check("GRADE 1" in zz_texts("combat_screen") and zz_gear_rgba(gui.grade_g1) in zz_gear_fills("combat_screen"),
              "a Grade 1 curse's chip is red")
    $ check(zz_worst("combat_screen"), "zz_worst('combat_screen') is saved")
    $ renpy.hide_screen("combat_screen")
    python:
        combat_begin(dict(name="Stray curse", hp=40, power=8, sprite="curse small",
                          tells=[("It twitches toward me.", "fast")]), None, True, "bg alley")
        renpy.show_screen("combat_screen")
        check("UNGRADED" in zz_texts("combat_screen"), "an enemy with no grade reads UNGRADED on a ghost chip",
              [t for t in zz_texts("combat_screen") if "GRADE" in t])
    $ zz_gear_shot("combat_header_ungraded")
    $ renpy.hide_screen("combat_screen")
    $ cb = {}

    ## --- the screenshots ---------------------------------------------------------------------------------------
    python:
        _zz_wantshots = ["board_g4", "board_partner_senior", "armory_checklists", "armory_g4", "grade_card_sp",
                         "grade_card_sp_no_sheen", "grade_card_g3", "combat_header_g3", "combat_header_ungraded",
                         "worst_board_screen", "worst_board_partner", "worst_armory", "worst_grade_card",
                         "worst_combat_screen"]
        _zz_missing = [n for n in _zz_wantshots
                       if not os.path.exists(os.path.join(zz_smoke_state.shots, n + ".png"))
                       or os.path.getmtime(os.path.join(zz_smoke_state.shots, n + ".png")) < zz_smoke_state.t0 - 1]
        check(not _zz_missing,
              "ACC screenshots: the board (g4 green, g3 blue), the armory with checklists, the grade card for sp, "
              "the combat header (%d files, all from this run)" % len(_zz_wantshots), _zz_missing)
        check(bound_specials == builtins.set(), "bound_specials is still empty at the end", bound_specials)

    $ finish()
