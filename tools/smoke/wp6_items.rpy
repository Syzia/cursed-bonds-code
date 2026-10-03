## tools/smoke/wp6_items.rpy -- WP6's package harness: items, equipment and
## the armory (PHASE1_DESIGN.md 3.8, 4.9, section 7 "WP6").
##
##   tools/smoke.sh tools/smoke/wp6_items.rpy
##
## Checks every WP6 acceptance bullet by name ("ACC ..."), plus the rest of
## the package: the catalogue, the D24 sync paths (new day, event done,
## migration 70), the D4 retain_after_load calls, the place action, and the
## armory label driven through its own screen. Screenshots of the armory go
## to shots/wp6_items/.

init 999 python:
    import builtins
    import pickle

    ## Armory driver: while `screen armory` is up, each tick pops the next
    ## (screenshot name or None, return value) and returns the value, which
    ## ends the `call screen armory` interaction just as a click would.
    ZZ_ARMORY_Q = builtins.list()
    ZZ_TOASTS = builtins.list()
    ZZ_RETAIN = builtins.list([0])

    def zz_armory_step():
        if not renpy.get_screen("armory"):
            return None
        if not ZZ_ARMORY_Q:
            return ("close",)
        name, val = ZZ_ARMORY_Q.pop(0)
        if name:
            shot(name)
        return val

    def zz_sink(text, kind, who, amount):
        ZZ_TOASTS.append((text, kind, who, amount))

    def zz_reset(**kw):
        """A clean item state, at a grade."""
        store.inventory = {}
        store.items_granted = set()
        store.equipped_tool = None
        store.equipped_talismans = []
        store.bound_specials = set()
        store.yen = 0
        for f in ("took_photo", "took_hachimaki", "took_watch", "oda_letter_read", "kurose_card",
                  "kurose_leak", "nade_traced", "nade_map", "armory_open"):
            store.flags.discard(f)
        store.grade = kw.pop("grade", None)
        fixture(**kw)

    def zz_counting_retain():
        ZZ_RETAIN[0] += 1

    ## Counts give_item calls (sync_keepsakes looks give_item up in the store,
    ## so swapping store.give_item catches every grant it makes).
    ZZ_GIVES = builtins.list()

    def zz_counting_give(orig):
        def wrapped(id, n=1, quiet=False):
            ZZ_GIVES.append(id)
            return orig(id, n, quiet)
        return wrapped

    ## The 3.8 table: id -> (kind, grade).
    ZZ_TABLE = {
        "photo": ("keepsake", None), "hachimaki": ("keepsake", None), "watch": ("keepsake", None),
        "oda_letter": ("keepsake", None), "daisy_clip": ("keepsake", None),
        "kurose_card": ("mission", None), "kurose_photocopy": ("mission", None),
        "presigned_form": ("mission", None), "nade_map": ("mission", None),
        "sealing_talisman": ("sealing", "g4"), "first_aid": ("supply", None),
        "slaughter_demon": ("tool", "g4"), "nunchaku": ("tool", "g3"), "playful_cloud": ("tool", "g2"),
        "split_soul": ("tool", "s1"), "inverted_spear": ("tool", "sp"),
        "paper_ward": ("talisman", "g4"), "steady_hand": ("talisman", "g4"),
        "deep_well": ("talisman", "g3"), "iron_seal": ("talisman", "g3"),
        "spark": ("talisman", "g2"), "held_breath": ("talisman", "g2"),
        "afterglow": ("talisman", "g1"), "black_sun": ("talisman", "g1"),
        "unending_moment": ("talisman", "sp"), "the_zone": ("talisman", "sp"),
        "finger_wrap": ("talisman", "sp"), "tengens_seal": ("talisman", "sp"),
    }
    ## The fx numbers the table fixes.
    ZZ_FX = {
        "slaughter_demon": {"bleed": 3}, "nunchaku": {"chain": 1},
        "paper_ward": {"reserve": 10}, "steady_hand": {"tech_cost": -0.1},
        "deep_well": {"reserve": 20, "recover": -0.1}, "iron_seal": {"strike": 0.15, "guard": -0.15},
        "spark": {"bf_window": 0.1}, "held_breath": {"hold_cost": -0.15, "hold_beats": 1},
        "afterglow": {"bf_refill": 0.5}, "black_sun": {"bf_mult": 3.0, "bf_window": -0.1},
    }
    ZZ_FROM_FLAG = {"photo": "took_photo", "hachimaki": "took_hachimaki", "watch": "took_watch",
                    "oda_letter": "oda_letter_read", "kurose_card": "kurose_card",
                    "kurose_photocopy": "kurose_leak", "presigned_form": "nade_traced",
                    "nade_map": "nade_map"}

    ## An event whose scene sets a keepsake flag (the event-done sync path).
    ev("zz_w6_event", kind="zzkind", once=True, thread=None)


## Sets the flag, as st_kurose does, and returns.
label zz_w6_event:
    $ flag("kurose_card")
    return

screen zz_armory_driver():
    zorder 200
    timer 0.7 repeat True action Function(zz_armory_step)


label zz_smoke:

    $ settle(day=3, mc_name="Tester", mc_surname="Harness")
    $ TOAST_SINK[0] = zz_sink

    ## --- the catalogue ----------------------------------------------------------------
    python:
        _missing = sorted(set(ZZ_TABLE) - set(ITEMS))
        check(not _missing, "every 3.8 item is in ITEMS", _missing)
        _bad = [(i, (ITEMS[i]["kind"], ITEMS[i]["grade"]), ZZ_TABLE[i]) for i in ZZ_TABLE
                if i in ITEMS and (ITEMS[i]["kind"], ITEMS[i]["grade"]) != ZZ_TABLE[i]]
        check(not _bad, "kinds and grades match the 3.8 table", _bad)
        _bad = [(i, ITEMS[i]["fx"]) for i in ZZ_FX if ITEMS[i]["fx"] != ZZ_FX[i]]
        check(not _bad, "fx numbers match the 3.8 table", _bad)
        _bad = [(i, ITEMS[i]["from_flag"]) for i in ZZ_FROM_FLAG if ITEMS[i]["from_flag"] != ZZ_FROM_FLAG[i]]
        check(not _bad, "keepsakes and mission items name their flags", _bad)
        _fields = ("name", "kind", "grade", "special", "sealed", "stack", "desc", "effect", "fx",
                   "source", "from_flag", "hidden")
        _bad = [i for i, it in ITEMS.items() if tuple(sorted(it)) != tuple(sorted(_fields))]
        check(not _bad, "every item has exactly the 3.8 fields", _bad)
        _spec = sorted(i for i, it in ITEMS.items() if it["special"])
        check(_spec == ["finger_wrap", "tengens_seal", "the_zone", "unending_moment"], "the four specials", _spec)
        check(ITEMS["tengens_seal"]["sealed"] == "Arc Two" and ITEMS["inverted_spear"]["sealed"] == "Arc Two",
              "Tengen's Seal and the Inverted Spear are sealed until Arc Two")
        _st = sorted(i for i, it in ITEMS.items() if it["stack"])
        check(_st == ["first_aid", "sealing_talisman"], "only sealing talismans and first aid stack", _st)
        check(ITEMS["daisy_clip"]["hidden"] and "daisy_clip" not in all_item_ids()
              and "daisy_clip" in all_item_ids(include_hidden=True), "the daisy clip is hidden until owned")
        _names = ("Kai" + "to", "Ama" + "giri")   # spelled apart so check_content stays clean
        _lit = [i for i, it in ITEMS.items()
                for k in ("name", "desc", "effect", "source") for nm in _names if nm in it[k]]
        check(not _lit, "no literal name in item text", _lit)
        ## The validator reads every .rpy in game/, this harness included: its
        ## only finding must be the made-up id in the regex test below.
        _vp = _validate_items()
        check([p for p in _vp if not p.startswith("zz_smoke.rpy:")] == [], "the WP6 validator finds nothing in the game", _vp)
        check(len(_vp) == 1 and "'zz_nope'" in _vp[0], "the validator reads the scripts (it flags this harness's made-up id)", _vp)
        check(any(f.endswith(".rpy") for f in renpy.list_files()), "the validator can see the scripts")
        check(_ITEM_CALL_RE.findall('give_item("zz_nope", 2) and has_item(\'paper_ward\')') == ["zz_nope", "paper_ward"],
              "the validator spots literal item ids in scripts")
        ## WP11: the board's own drop tables (sb_board.rpy) are tied to
        ## BOARD_DROP_ITEMS, and the validator catches a board drop it misses.
        _bd = set([BOARD_SEALING[0]])
        for _t in list(BOARD_TALISMAN_DROPS.values()) + list(BOARD_TOOL_DROPS.values()):
            _bd.update(_t)
        check(_bd == set(BOARD_ITEM_NAMES) and set(BOARD_ITEM_NAMES) <= set(BOARD_DROP_ITEMS),
              "BOARD_DROP_ITEMS lists every drop in the board's tables", (sorted(_bd), BOARD_DROP_ITEMS))
        check("slaughter_demon" in BOARD_DROP_ITEMS and "nunchaku" in BOARD_DROP_ITEMS,
              "BOARD_DROP_ITEMS lists the two cursed tools the board drops", BOARD_DROP_ITEMS)
        BOARD_ITEM_NAMES["zz_board_only"] = "ZZ"
        try:
            _vb = [p for p in _validate_items() if "zz_board_only" in p]
        finally:
            del BOARD_ITEM_NAMES["zz_board_only"]
        check(_vb == ["board can drop 'zz_board_only' but BOARD_DROP_ITEMS doesn't list it"],
              "the validator flags a board drop BOARD_DROP_ITEMS doesn't list", _vb)

    ## --- ACC 1: keepsakes from flags, exactly once across three syncs (D24) ----------------
    python:
        zz_reset()
        flag("took_watch")
        flag("kurose_leak")
        del ZZ_TOASTS[:]
        del ZZ_GIVES[:]
        _orig_give = store.give_item
        store.give_item = zz_counting_give(_orig_give)
        try:
            sync_keepsakes()
            sync_keepsakes()
            sync_keepsakes()
        finally:
            store.give_item = _orig_give
        check(item_count("watch") == 1 and item_count("kurose_photocopy") == 1
              and sorted(ZZ_GIVES) == ["kurose_photocopy", "watch"]
              and [t[1] for t in ZZ_TOASTS] == ["item", "item"]
              and items_granted == {"flag:took_watch", "flag:kurose_leak"},
              "ACC flags took_watch and kurose_leak grant watch and kurose_photocopy exactly once across three syncs",
              (dict(inventory), ZZ_GIVES, ZZ_TOASTS, items_granted))
        check(items_granted == {"flag:took_watch", "flag:kurose_leak"}, "grants are keyed flag:<f>", items_granted)
        check([t[1] for t in ZZ_TOASTS] == ["item", "item"], "one item toast per grant", ZZ_TOASTS)
        check(set(inventory) == {"watch", "kurose_photocopy"}, "nothing else is granted", dict(inventory))
        take_item("watch")
        sync_keepsakes()
        check(not has_item("watch"), "a used keepsake is never granted again")

        ## the new-day hook
        _d = day
        flag("oda_letter_read")
        new_day()
        check(day == _d + 1 and has_item("oda_letter"), "the new-day hook syncs (oda_letter_read -> oda_letter)")

        ## migration 70
        _m = [(o, n) for o, n, fn in MIGRATIONS if fn is sync_keepsakes]
        check(len(_m) == 1 and _m[0][0] == 70, "sync_keepsakes is migration 70", _m)
        flag("took_photo")
        flag("nade_map")
        flag("nade_traced")
        del ZZ_TOASTS[:]
        run_migrations()
        check(has_item("photo") and has_item("nade_map") and has_item("presigned_form"),
              "migration 70 grants from an old save's flags", dict(inventory))
        check(ZZ_TOASTS == [], "migration grants are silent", ZZ_TOASTS)
        _inv = dict(inventory)
        run_migrations()
        check(dict(inventory) == _inv, "a second migration run changes nothing")

        ## the event-done hook
        _e = [e for e in EVENTS if e["label"] == "zz_w6_event"][0]

    call play_event(_e)
    $ check(has_item("kurose_card"), "a scene that sets a flag grants its item when the event is done")

    ## --- inventory basics ---------------------------------------------------------------
    python:
        zz_reset()
        del ZZ_TOASTS[:]
        give_item("paper_ward")
        check(ZZ_TOASTS[-1:] == [("Paper Ward", "item", None, 1)], "give_item toasts kind item", ZZ_TOASTS)
        give_item("paper_ward")
        check(item_count("paper_ward") == 1, "an item that doesn't stack stays at one")
        give_item("sealing_talisman", 2)
        give_item("sealing_talisman")
        check(item_count("sealing_talisman") == 3, "sealing talismans stack")
        check(ZZ_TOASTS[-2][0] == "Sealing talisman ×2", "a stack toasts its count", ZZ_TOASTS)
        del ZZ_TOASTS[:]
        give_item("first_aid", quiet=True)
        check(ZZ_TOASTS == [], "quiet gives don't toast")
        check(items_in("talisman") == ["paper_ward"] and items_in("sealing") == ["sealing_talisman"],
              "items_in by kind", (items_in("talisman"), items_in("sealing")))
        add_yen(4500)
        add_yen(-10000)
        check(yen == 0, "yen never goes below zero", yen)
        add_yen(12000)
        check(yen == 12000, "add_yen adds", yen)
        _s = pickle.dumps((inventory, items_granted, yen, equipped_tool, equipped_talismans, bound_specials))
        check(bool(_s), "the item state pickles")

        ## take_item's edges: nothing to take, a take-all of nothing, a negative n.
        zz_reset()
        give_item("sealing_talisman", 2, quiet=True)
        _inv = dict(inventory)
        try:
            _r = (take_item("photo", 0), take_item("first_aid", item_count("first_aid")))
            _err = None
        except Exception as _e:
            _r, _err = None, repr(_e)
        check(_err is None and _r == (True, True) and dict(inventory) == _inv,
              "take_item of zero (and a take-all of an unowned item) takes nothing and doesn't raise", (_r, _err))
        check(take_item("sealing_talisman", -2) is False and dict(inventory) == _inv,
              "take_item with a negative n is refused and adds nothing", dict(inventory))
        check(take_item("sealing_talisman", 3) is False and item_count("sealing_talisman") == 2,
              "take_item of more than I have takes nothing")
        check(take_item("sealing_talisman", 2) is True and "sealing_talisman" not in inventory,
              "taking the whole stack removes the entry")

        ## An id that isn't in ITEMS: counted, as WP0's contract check requires,
        ## but never toasted; the catalogue readers skip it.
        _bogus = "zz_" + "bogus"      # built, so the validator's script scan doesn't see it
        del ZZ_TOASTS[:]
        check(give_item(_bogus) == 1 and item_count(_bogus) == 1 and ZZ_TOASTS == [],
              "give_item on an unknown id: counted (WP0 contract), no toast", (dict(inventory), ZZ_TOASTS))
        check(all(_bogus not in items_in(k) for k in ITEM_KINDS) and _bogus not in all_item_ids(True),
              "an unknown id never shows in items_in or all_item_ids")
        take_item(_bogus)

    ## --- ACC 2: Grade 4 ------------------------------------------------------------------
    python:
        zz_reset(grade="g4")
        for _i in ("paper_ward", "steady_hand", "spark", "unending_moment", "the_zone", "tengens_seal"):
            give_item(_i, quiet=True)
        check(talisman_slots() == 1, "ACC at g4: one slot", talisman_slots())
        check(equip_talisman("paper_ward") and equipped_talismans == ["paper_ward"], "at g4 a Grade 4 talisman goes on")
        check(can_wear("steady_hand") == (False, "No free slot — opens at Grade 3"),
              "at g4 a second talisman: No free slot — opens at Grade 3", can_wear("steady_hand"))
        check(can_wear("spark") == (False, "Needs Grade 2") and not equip_talisman("spark"),
              "ACC at g4: spark refused with Needs Grade 2", can_wear("spark"))
        unequip_talisman("paper_ward")
        check(can_wear("unending_moment") == (False, "Special: bound by story"),
              "ACC at g4: a special refused unless bound", can_wear("unending_moment"))
        bound_specials.update(("unending_moment", "the_zone", "tengens_seal"))
        check(equip_talisman("unending_moment"), "at g4 a bound special goes on (specials skip the grade rule)",
              can_wear("unending_moment"))
        check(can_wear("the_zone") == (False, "A special is already worn") and not equip_talisman("the_zone"),
              "ACC at g4: a second special refused", can_wear("the_zone"))
        check(can_wear("tengens_seal") == (False, "Sealed — Arc Two"), "Tengen's Seal: Sealed — Arc Two",
              can_wear("tengens_seal"))
        check(can_wear("unending_moment") == (False, "Already worn"), "a worn talisman reads Already worn")
        check(can_wear("deep_well")[1] == "Needs Grade 3" and can_wear("slaughter_demon")[1] == "Not a talisman",
              "grade and kind reasons", (can_wear("deep_well"), can_wear("slaughter_demon")))
        zz_reset(grade=None)
        give_item("paper_ward", quiet=True)
        give_item("steady_hand", quiet=True)
        check(talisman_slots() == 1 and equip_talisman("paper_ward") and can_wear("iron_seal")[1] == "Needs Grade 3",
              "unassessed (grade None): Grade 4's rules")
        check(can_wear("steady_hand")[1] == "No free slot — opens at Grade 3", "unassessed: one slot")

    ## --- ACC 3: Grade 3 ------------------------------------------------------------------
    python:
        zz_reset(grade="g4")
        for _i in ("paper_ward", "iron_seal", "unending_moment", "the_zone"):
            give_item(_i, quiet=True)
        equip_talisman("paper_ward")
        check(can_wear("iron_seal")[1] == "Needs Grade 3", "iron_seal waits for Grade 3")
        promote("mc", "g3")
        check(talisman_slots() == 2, "Grade 3: two slots", talisman_slots())
        check(equip_talisman("iron_seal") and equipped_talismans == ["paper_ward", "iron_seal"]
              and equipped_talismans.index("iron_seal") == 1,
              "ACC after promote(mc, g3): iron_seal equips into slot 2", equipped_talismans)
        check(can_wear("the_zone")[1] == "Special: bound by story", "g3: an unbound special still refused")
        bound_specials.update(("unending_moment", "the_zone"))
        unequip_talisman("iron_seal")
        check(equip_talisman("unending_moment") and can_wear("the_zone")[1] == "A special is already worn",
              "g3 with a free slot: a second special still refused", (equipped_talismans, can_wear("the_zone")))
        check(can_wear("iron_seal")[1] == "No free slot — opens at Grade 2", "g3 full: opens at Grade 2")
        take_item("unending_moment")
        check(equipped_talismans == ["paper_ward"], "taking the last one off the inventory unequips it",
              equipped_talismans)

    ## --- tools and D4 (retain_after_load) ------------------------------------------------------
    python:
        ## Phase 2 (P4a, 4.9): Playful Cloud has a checklist now (Grade 2,
        ## Output 50), so at Grade 4 it no longer jumps into an empty hand.
        ## The first-tool checks use the two tools with no checklist.
        zz_reset(grade="g4")
        give_item("playful_cloud", quiet=True)
        check(equipped_tool is None and can_hold("playful_cloud") == (False, "Needs Grade 2"),
              "phase 2: a tool whose checklist I don't meet stays out of an empty hand", (equipped_tool, can_hold("playful_cloud")))
        zz_reset(grade="g4")
        give_item("nunchaku", quiet=True)
        check(equipped_tool == "nunchaku", "a first tool goes straight into an empty hand", equipped_tool)
        give_item("slaughter_demon", quiet=True)
        check(equipped_tool == "nunchaku", "a second tool doesn't take the hand", equipped_tool)
        check(equip_tool("slaughter_demon") and equipped_tool == "slaughter_demon", "equip_tool swaps the tool")
        check(can_hold("playful_cloud") == (False, "Not in my inventory") and not equip_tool("playful_cloud")
              and equipped_tool == "slaughter_demon", "an unowned tool can't be held", can_hold("playful_cloud"))
        give_item("inverted_spear", quiet=True)
        check(can_hold("inverted_spear") == (False, "Sealed — Arc Two") and not equip_tool("inverted_spear"),
              "a sealed tool can't be held")
        check(equip_tool(None) and equipped_tool is None, "equip_tool(None) is bare hands")
        _orig = renpy.retain_after_load
        renpy.retain_after_load = zz_counting_retain
        try:
            ZZ_RETAIN[0] = 0
            equip_tool("slaughter_demon")
            _a = ZZ_RETAIN[0]
            give_item("paper_ward", quiet=True)
            equip_talisman("paper_ward")
            _b = ZZ_RETAIN[0]
            unequip_talisman("paper_ward")
            _c = ZZ_RETAIN[0]
        finally:
            renpy.retain_after_load = _orig
        check((_a, _b, _c) == (1, 2, 3), "equip_tool / equip_talisman / unequip_talisman each call retain_after_load (D4)",
              (_a, _b, _c))

    ## --- phase 2 (P4a): requirements, pinned here; tools/smoke/p2_gear.rpy has the rest ------
    python:
        zz_reset(grade="g4")
        check(len(_ITEM_FIELDS) == 12 and all(len(it) == 12 for it in ITEMS.values()),
              "phase 2: every ITEMS record still has exactly 12 fields (requirements live in ITEM_REQS)")
        check(sorted(ITEM_REQS) == ["afterglow", "black_sun", "inverted_spear", "playful_cloud", "split_soul"]
              or set(ITEM_REQS) > {"afterglow", "black_sun", "inverted_spear", "playful_cloud", "split_soul"},
              "phase 2: ITEM_REQS has the three tools and the two Grade 1 talismans (more once the market is in)",
              sorted(ITEM_REQS))
        check(item_requirements("slaughter_demon") == [] and item_requirements_met("slaughter_demon")
              and [l for l, ok in item_requirements("inverted_spear")]
                  == ["Arc Two", "Special Grade", "The seal broken", "Yaga's signature"],
              "phase 2: item_requirements: nothing for a plain tool, four lines for the spear",
              item_requirements("inverted_spear"))
        zz_reset(grade="g1", control=62)
        give_item("afterglow", quiet=True)
        check(can_wear("afterglow") == (False, "Control 80 · I have 62") and not equip_talisman("afterglow"),
              "phase 2: can_wear refuses on the first unmet line, after its own checks", can_wear("afterglow"))
        control = 80
        check(can_wear("afterglow") == (True, "") and equip_talisman("afterglow"), "phase 2: and allows it once the line is met")
        control = 62
        check(equipped_talismans == ["afterglow"] and can_wear("afterglow") == (False, "Already worn"),
              "phase 2: a talisman already worn stays worn (D28)", equipped_talismans)
        zz_reset(grade="g2", output=50)
        give_item("playful_cloud", quiet=True)
        output = 30
        give_item("slaughter_demon", quiet=True)
        check(equipped_tool == "playful_cloud" and can_hold("playful_cloud") == (True, ""),
              "phase 2: the tool in my hand is never asked again (D28)", (equipped_tool, can_hold("playful_cloud")))
        equip_tool("slaughter_demon")
        check(can_hold("playful_cloud") == (False, "Output 50 · I have 30") and not equip_tool("playful_cloud"),
              "phase 2: can_hold refuses an owned tool that isn't in hand, with the unmet line", can_hold("playful_cloud"))
        check(item_validate_reqs() == [] and bound_specials == set(), "phase 2: the requirement rows pass their validator",
              item_validate_reqs())

    ## --- ACC 4: the armory at Grade 4 ------------------------------------------------------
    python:
        zz_reset(grade="g4")
        _t = dict((i, s) for i, s, r in armory_tools())
        check(_t.get("slaughter_demon") == "take" and _t.get("nunchaku") == "sealed"
              and _t.get("playful_cloud") == "story" and _t.get("inverted_spear") == "arcii",
              "ACC the armory at g4: slaughter_demon take, nunchaku sealed, playful_cloud story, inverted_spear arcii", _t)
        _r = dict((i, r) for i, s, r in armory_tools())
        check(_r["nunchaku"] == "Sealed until Grade 3" and _r["playful_cloud"] == "Story reward"
              and _r["inverted_spear"] == "Sealed — Arc Two" and _t.get("split_soul") == "story",
              "armory reasons", _r)
        check([i for i, s, r in armory_tools()] == [i for i, k in ARMORY_RACK], "one row per rack tool, in order")
        check(not armory_take("nunchaku") and not has_item("nunchaku"), "a sealed tool can't be taken")
        zz_reset(grade=None)
        check(dict((i, s) for i, s, r in armory_tools()) == _t, "unassessed: the armory uses Grade 4's rules")

        ## The place action (D10): only in the storehouse, only with armory_open.
        here = "storehouse"
        check("armory" not in [a[0] for a in registered_place_actions("storehouse")] and not armory_open_now(),
              "no armory before armory_open")
        flag("armory_open")
        check("armory" in [a[0] for a in registered_place_actions("storehouse")] and armory_open_now(),
              "the armory action at the storehouse once armory_open is set")
        here = "courtyard"
        check("armory" not in [a[0] for a in registered_place_actions("courtyard")] and not armory_open_now(),
              "no armory anywhere else")
        _pa = [a for a in PLACE_ACTIONS if a["id"] == "armory"]
        check(len(_pa) == 1 and _pa[0]["label"] == "Armory" and _pa[0]["cost"] == 0
              and _pa[0]["locs"] == ("storehouse",) and _pa[0]["when"] == "armory_open_now",
              "the armory registration matches 3.8", _pa)
        check(_pa and _pa[0].get("hint") == "Cursed tools, released up to my grade.",
              "the armory hint is in the first person (D9)", _pa)

    ## --- the armory label, through its screen ------------------------------------------------
    scene expression graded_bg("storehouse")
    python:
        zz_reset(grade="g4")
        flag("armory_open")
        here = "storehouse"
        _per = period
        _day = day
        ZZ_ARMORY_Q[:] = [("armory_g4", ("take", "slaughter_demon")),
                          ("armory_g4_taken", ("close",))]
    show screen zz_armory_driver
    call sb_do_armory
    python:
        check(has_item("slaughter_demon") and equipped_tool == "slaughter_demon",
              "armory at g4: Take puts the Slaughter Demon in my hand", (dict(inventory), equipped_tool))
        check(ZZ_ARMORY_Q == [], "the armory label looped until Close")
        promote("mc", "g3")
        give_item("playful_cloud", quiet=True)
        ZZ_ARMORY_Q[:] = [("armory_g3", ("take", "nunchaku")),
                          (None, ("return", "slaughter_demon")),
                          ("armory_g3_after", ("close",))]
    call sb_do_armory
    hide screen zz_armory_driver
    python:
        check(has_item("nunchaku") and not has_item("slaughter_demon") and equipped_tool == "nunchaku",
              "armory at g3: Take puts the Nunchaku in my hand; returning the Slaughter Demon leaves it there",
              (dict(inventory), equipped_tool))
        check(dict((i, s) for i, s, r in armory_tools()).get("slaughter_demon") == "take",
              "a returned tool is back on the rack")
        check(armory_return("playful_cloud") is False and has_item("playful_cloud"), "a story tool can't be returned")
        check((day, period) == (_day, _per), "the armory costs no time", (day, period))

        ## Returning the tool in my hand hands me the next one I own, in rack order.
        zz_reset(grade="g3")
        give_item("playful_cloud", quiet=True)
        give_item("nunchaku", quiet=True)
        give_item("slaughter_demon", quiet=True)
        equip_tool("slaughter_demon")
        del ZZ_TOASTS[:]
        armory_return("slaughter_demon")
        check(equipped_tool == "nunchaku", "returning the tool in hand: the next owned tool (rack order) takes its place",
              equipped_tool)
        check(ZZ_TOASTS[-1:] and "Nunchaku in my hand" in ZZ_TOASTS[-1][0], "the return toast says what is in my hand now",
              ZZ_TOASTS)
        armory_return("nunchaku")
        check(equipped_tool is None and has_item("playful_cloud"),
              "phase 2: a story tool whose checklist I don't meet doesn't take its place (bare hands)", equipped_tool)
        ## Phase 2 (P4a, 4.9): the story tool takes the hand once I meet its
        ## checklist (Grade 2, Output 50).
        zz_reset(grade="g2", output=50)
        give_item("playful_cloud", quiet=True)
        give_item("nunchaku", quiet=True)
        equip_tool("nunchaku")
        armory_return("nunchaku")
        check(equipped_tool == "playful_cloud", "then a story tool, if that is all I own", equipped_tool)
        give_item("nunchaku", quiet=True)
        armory_return("nunchaku")
        check(equipped_tool == "playful_cloud", "returning a tool that wasn't in hand leaves the hand alone", equipped_tool)
        zz_reset(grade="g4")
        give_item("slaughter_demon", quiet=True)
        armory_return("slaughter_demon")
        check(equipped_tool is None, "returning my only tool leaves bare hands", equipped_tool)

        ## Taking from the rack is choosing to carry it, even with a tool in hand.
        zz_reset(grade="g4")
        give_item("playful_cloud", quiet=True)
        del ZZ_TOASTS[:]
        check(armory_take("slaughter_demon") and equipped_tool == "slaughter_demon" and has_item("playful_cloud"),
              "armory_take puts the tool in hand; the one it replaces stays in the inventory", (equipped_tool, dict(inventory)))
        check(ZZ_TOASTS == [("Slaughter Demon — in my hand", "item", None, 1)], "one toast for a take, saying where it went",
              ZZ_TOASTS)
        check(give_item("nunchaku", quiet=True) == 1 and equipped_tool == "slaughter_demon",
              "a story grant (give_item) still never replaces the tool in hand")

        ## An owned sealed tool (review tools can grant one) still reads Sealed — Arc Two.
        zz_reset(grade="g4")
        for _i in all_item_ids(include_hidden=True):
            give_item(_i, quiet=True)
        check(armory_state("inverted_spear") == ("arcii", "Sealed — Arc Two"),
              "an owned Inverted Spear still reads Sealed — Arc Two", armory_state("inverted_spear"))
        check(not armory_take("inverted_spear"), "the Arc Two spear can't be taken, even when owned")
        flag("armory_open")
        here = "storehouse"
        ZZ_ARMORY_Q[:] = [("armory_all_owned", ("close",))]
    show screen zz_armory_driver
    call sb_do_armory
    hide screen zz_armory_driver
    python:
        flags.discard("armory_open")
    call sb_do_armory
    $ check(True, "sb_do_armory returns at once when the armory isn't open")

    ## A still of the screen as the stub harness renders it (no driver).
    python:
        zz_reset(grade="g4")
        here = "storehouse"
        renpy.show_screen("armory")
        shot("armory_static_g4")
        renpy.hide_screen("armory")
        check(True, "screen armory renders")

    $ TOAST_SINK[0] = None
    $ finish()
