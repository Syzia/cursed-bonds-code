## tools/smoke/wp8_journal.rpy -- WP8's harness: the journal and the engine
## screens (docs/PHASE1_DESIGN.md, WP8 acceptance).
##
##   SMOKE_SHOTS=shots/wp8 tools/smoke.sh tools/smoke/wp8_journal.rpy
##
## (Without SMOKE_SHOTS the screenshots land in shots/wp8_journal/.)
##
## What it checks, each as a named check:
##   render     every tab of the journal for a fresh state and a rich fixture
##              (grade g3, items, promotions, memories, missions, the board),
##              plus the detail pane, the sub-tabs, the picker, the Sana
##              filter and the two wrappers. Screenshots go to shots/wp8/.
##   equipment  an equipment change made through the campus journal (the
##              picker's own buttons, in the main context) survives a save
##              taken during that interaction and a load; the journal opened
##              from a menu context is read-only.
##   replay     a memory replay started from the journal (the tile's own
##              button, from campus and from the quick menu's menu context)
##              returns to the journal, and leaves the save's state alone.
##   quick menu hidden on sb_place and in the journal, shown in dialogue,
##              with the D25 buttons.
##   portraits  every side portrait at zoom 0.8 fits inside the dialogue's
##              300px margin; an off-screen speaker gets one; the
##              "[mc_name]'s portrait: Hide" preference and the blackout
##              (hide_side_images) take it away.
##   arc two    the Begin Arc Two card returns ("arc_two",) from campus and
##              is absent from a menu context.
##   prologue   before the campus the default roster doesn't count as met
##              (each person waits for the step that introduces them), and
##              the portrait preference reads MY PORTRAIT until Gojo asks.
##   details    JOURNAL_CAST-only people's panes and short names, waiting
##              rows, "once a day" said once, the merit shown once, jr_wear
##              keeping slot order, ō from DejaVu Sans, and stress renders
##              (long ranks, a long given name, a long picker that scrolls).
##   round 2    every styled font (history, input, preferences, buttons ...)
##              carries ō, bold bases from DejaVu Sans Bold; a given name
##              with "[" renders on Stats and Preferences; during a replay
##              the quick menu has no JOURNAL and the journal says it isn't
##              kept; Maki's and Gojo's panes draw their special reserves;
##              slot wording; long item names stay inside their tiles.
##
## Other packages' APIs are still stubs in WP8's worktree. The rich fixture
## fakes their data at harness level: each faked store function switches
## between the fake (while zzj.rich is on) and whatever the game defines, so
## the fresh-state renders use the real functions. The equipment functions are
## faked only while WP6's are still WP0 stubs; after WP6 merges, the save and
## load check runs against WP6's own equip_*.
##
## The journal is driven the way a player drives it: the `zzj_driver` screen
## (zorder 500) runs one scripted step per timer tick during the journal's own
## interaction, finds the journal's buttons in the displayable tree and runs
## their actions.

init 999 python:
    import builtins

    class ZZJState(builtins.object):
        """Harness state outside the store: not saved, not rolled back."""
        def __init__(self):
            self.rich = False
            self.story_complete = False
            self.script = builtins.list()
            self.menu_driver = False
            self.phase = ""
            self.no_retain = False
            self.replays = 0
            self.replay_flags = None
            self.stub6 = False
            self.after_load = None

    zzj = ZZJState()

    ## --- switching fakes ----------------------------------------------------

    def zzj_switch(name, fake):
        """Rebind store.<name> to call `fake` while zzj.rich, else the game's."""
        orig = getattr(store, name)
        def f(*a, **k):
            return (fake if zzj.rich else orig)(*a, **k)
        f.__name__ = name
        f.__doc__ = getattr(orig, "__doc__", None)
        setattr(store, name, f)

    ## --- missions (WP3) -----------------------------------------------------

    def zzj_m(id, kind, act, title, objective="", trigger="auto", where=None, with_who=None,
              who=None, periods=None, merit=0, group=None):
        return dict(id=id, kind=kind, act=act, title=title, objective=objective, trigger=trigger,
                    where=where, with_who=with_who, who=who, periods=periods, group=group,
                    rewards=dict(merit=merit))

    ZZJ_MISSIONS = [
        zzj_m("m_prologue", "story", "P", "The Offer and the Tour"),
        zzj_m("m_roll_call", "story", "I", "Roll Call", "Roll call with Principal Yaga", periods=("Morning",), merit=5),
        zzj_m("m_utahime", "story", "I", "The Room Next Door", "Someone is moving into the room next to Yaga's", periods=("Morning", "Noon", "Afternoon")),
        zzj_m("m_sunmall", "story", "I", "The Sun Mall", "Yaga has a mission for the first-years", "start", "office", "yaga", merit=30),
        zzj_m("m_aftermath", "story", "I", "Cursed Energy Debt", "Shoko wants to look at all four of us", periods=("Morning",), merit=5),
        zzj_m("m_kurose", "story", "I", "Auxiliary Management", "A man from auxiliary management is waiting outside Yaga's office", periods=("Afternoon", "Evening")),
        zzj_m("m_detention", "story", "I", "The Detention Center"),
        zzj_m("m_aftermath_2", "story", "I", "Aftermath"),
        zzj_m("m_infirmary", "story", "I", "The Infirmary"),
        zzj_m("m_second_years", "story", "II", "The Second-Years", "The second-years are back from wherever they were", periods=("Afternoon",)),
        zzj_m("m_noise", "story", "II", "Noise", "Stay on campus into the evening", periods=("Evening",), merit=10),
        zzj_m("m_intensive", "story", "II", "Eleven Minutes", "Gojo wants eleven minutes of my time", periods=("Afternoon",)),
        zzj_m("m_promo_g3", "promotion", "II", "Promotion: Grade 3", "Promotion fight: find Maki", "start", ("training", "dojo"), "maki"),
        zzj_m("m_nade_1", "story", "III", "A Name", "Yaga has a name", "start", "office", "yaga", merit=25, group="The Surveyor"),
        zzj_m("m_nade_2", "story", "III", "The Annexe", "Yaga wants the annexe looked at", "start", "office", "yaga", merit=25, group="The Surveyor"),
        zzj_m("m_nade_3", "story", "III", "Home Town", "Yaga knows where Nade is", "start", "office", "yaga", merit=30, group="The Surveyor"),
        zzj_m("cm_yuji_1", "character", "I", "Grandpa's Last Words", "Yuji wants to talk about his grandfather", "start", who="yuji"),
        zzj_m("cm_megumi_1", "character", "I", "The Hospital", "Go with Megumi to the hospital", "start", who="megumi"),
        zzj_m("cm_nobara_1", "character", "I", "Harajuku", "Nobara wants a day out, and a bag carrier", "start", who="nobara"),
        zzj_m("cm_maki_1", "character", "II", "The Armory", "Maki is opening the racks", "start", who="maki"),
        zzj_m("cm_gojo_1", "character", "II", "Infinity", "Gojo, in his office", "start", "gojo_office", "gojo", who="gojo"),
        zzj_m("cm_ijichi_1", "character", "I", "Ride-Along", "A day on the job with Ijichi", "start", "gate", "ijichi", who="ijichi"),
        zzj_m("cm_ijichi_2", "character", "II", "The Veil", "", "start", who="ijichi"),
    ]
    ZZJ_STATUS = dict(m_prologue="done", m_roll_call="done", m_utahime="done", m_sunmall="done",
                      m_aftermath="done", m_kurose="available", m_detention="unwritten",
                      m_aftermath_2="unwritten", m_infirmary="unwritten", m_second_years="waiting",
                      m_noise="locked", m_intensive="locked", m_promo_g3="done",
                      m_nade_1="locked", m_nade_2="locked", m_nade_3="locked",
                      cm_yuji_1="available", cm_megumi_1="locked", cm_nobara_1="active",
                      cm_maki_1="available", cm_gojo_1="unwritten", cm_ijichi_1="done",
                      cm_ijichi_2="locked")
    ZZJ_REASON = dict(m_second_years="tomorrow", m_noise="After The Second-Years",
                      m_intensive="After Noise", m_promo_g3="Try again tomorrow",
                      m_nade_1="After Eleven Minutes", m_nade_2="After A Name", m_nade_3="After The Annexe",
                      cm_megumi_1="Bond 35 with Megumi", cm_ijichi_2="Needs Grade 3")
    ZZJ_ACTS = [("P", "Prologue", "序", ""), ("I", "Grade Four", "壱", "Grade 4"),
                ("II", "The Ones Who Stay", "弐", "Grade 4 → Grade 3"),
                ("III", "Overtime", "参", "Grade 3 → Grade 2"),
                ("IV", "Goodwill", "四", "Grade 2"), ("V", "Cursed Womb", "五", "Grade 2 → Grade 1")]

    def zzj_missions_list(kind=None, status=None, act=None, who=None):
        out = []
        for m in ZZJ_MISSIONS:
            if kind and m["kind"] != kind:
                continue
            if act and m["act"] != act:
                continue
            if who and m["who"] != who:
                continue
            if status and ZZJ_STATUS.get(m["id"]) != status:
                continue
            out.append(m)
        return out

    def zzj_act_progress(act):
        rows = [m for m in ZZJ_MISSIONS if m["act"] == act and m["kind"] != "character"]
        written = [m for m in rows if ZZJ_STATUS.get(m["id"]) != "unwritten"]
        done = [m for m in written if ZZJ_STATUS.get(m["id"]) in ("done", "skipped")]
        return (len(done), len(written), len(rows))

    ZZJ_NEXT = dict(
        yuji=("Grandpa's Last Words: he wants to talk", "cafeteria"),
        megumi=("Spend time together", "classroom"),
        nobara=("Harajuku: a day out, and a bag carrier", "dorm_common"),
        maki=("The Armory: pick your first cursed tool", "storehouse"),
        panda=("Spend time together", "courtyard"),
        toge=("Talk", "cafeteria"),
        gojo=("Infinity: he's in his office today", "gojo_office"),
        utahime=("A Grade 3 job is waiting on her board", "utahime_office"),
        shoko=("Closer: Sit out with her — at Bond 50", "infirmary"),
        yaga=("Talk", "office"),
        ijichi=("Talk", "gate"),
        nanami=("Talk", None))

    ## --- memories (WP5) -----------------------------------------------------

    def zzj_mem(id, title, who, act, seen, hint="", bg=None, unlock=None, label=None):
        return dict(id=id, title=title, who=who, act=act, label=label or id, args=(), seen=seen,
                    hint=hint, unlock=unlock, bg=bg)

    ZZJ_MEMORIES = [
        zzj_mem("ch1_diner", "Nine Hundred Yen", ("sana",), "Prologue", ("label", "ch1_diner"), bg="bg diner"),
        zzj_mem("ch1_the_thing", "The Thing She Told Me", ("sana",), "Prologue", ("label", "ch1_the_thing"), bg="bg alley"),
        zzj_mem("ch1_gojo", "The Man in the Blindfold", ("gojo",), "Prologue", ("label", "ch1_gojo"), bg="bg alley dark"),
        zzj_mem("chapter_one_b", "The Offer", ("gojo",), "Prologue", ("label", "chapter_one_b"), bg="bg home_living"),
        zzj_mem("ch2_arrival", "The Strongest of Today", ("gojo", "ijichi"), "Prologue", ("label", "ch2_arrival"), bg="bg gate"),
        zzj_mem("ch2_the_veil", "The Veil on the Ridge", ("gojo",), "Prologue", ("label", "ch2_the_veil"), bg="bg ridge_veil"),
        zzj_mem("ch2_first_years", "Three First-Years", ("yuji", "megumi", "nobara"), "Prologue", ("label", "ch2_first_years"), bg="bg courtyard"),
        zzj_mem("st_roll_call", "Roll Call", ("yaga",), "I", ("event", "st_roll_call"), bg="bg classroom"),
        zzj_mem("zzj_mem_label", "The Vending Machine", ("yuji",), "Bonds", ("event", "zzj_mem_label"), bg="bg courtyard"),
        zzj_mem("ev_nobara_1", "Somebody Remembered", ("nobara",), "Bonds", ("event", "ev_nobara_1"), hint="Nobara, on a day off."),
        zzj_mem("ev_maki_1", "Dawn", ("maki",), "Bonds", ("event", "ev_maki_1"), hint="Maki trains at dawn."),
        zzj_mem("sana_mem_diner", "The Diner", ("sana",), "Sana", ("label", "sana_mem_diner"),
                hint="A trip home might bring this back.", unlock=("district", "yotsuka"), bg="bg diner"),
        zzj_mem("sana_mem_daisy", "The Daisy Clip", ("sana",), "Sana", ("label", "sana_mem_daisy"),
                hint="Something of hers.", unlock=("item", "daisy_clip")),
        zzj_mem("sana_mem_ranking", "The Teacher Ranking", ("sana",), "Sana", ("label", "sana_mem_ranking"),
                hint="Someone she ranked first.", unlock=("flag", "oda_letter_read")),
    ]

    def zzj_memory_groups(mode):
        groups = []
        if mode == "person":
            keys = ["sana"] + [w for w in ("yuji", "megumi", "nobara", "maki", "gojo", "yaga", "ijichi")]
            for w in keys:
                ms = [m for m in ZZJ_MEMORIES if w in m["who"]]
                if ms:
                    groups.append((CAST[w]["name"], ms))
        else:
            for a in ("Prologue", "I", "II", "Bonds", "Sana"):
                ms = [m for m in ZZJ_MEMORIES if m["act"] == a]
                if ms:
                    groups.append((a if a in ("Prologue", "Bonds", "Sana") else "Act " + a, ms))
        return groups

    def zzj_memory_counts():
        seen = len([m for m in ZZJ_MEMORIES if jr_mem_state(m) == "seen"])
        return (seen, len(ZZJ_MEMORIES))

    def zzj_memory_replay(m):
        return Replay("zzj_mem_label", scope=dict(mc_name=store.mc_name, zzj_scope_mark=True), locked=False)

    ## --- the board (WP4) ------------------------------------------------------

    ZZJ_BOARD = dict(
        offers=[dict(id="w1o1", grade="g3", true_grade="g3", case="A haunting", place="adachi",
                     title="The Ward on the Fourth Floor", curse="a call bell from a sealed room",
                     blurb="A haunting. A closed maternity ward in Adachi. The report says a call bell from a sealed room.",
                     merit=18, yen=(6000, 10000), senior_only=False),
                dict(id="w1o2", grade="g4", true_grade="g3", case="Residual clean-up", place="kita",
                     title="Stairwell, Third Landing", curse="something that eats light bulbs",
                     blurb="Residual clean-up. An apartment stairwell in Kita. The report says something that eats light bulbs.",
                     merit=10, yen=(3000, 6000), senior_only=False),
                dict(id="w1o3", grade="g2", true_grade="g2", case="Missing persons", place="ikebukuro",
                     title="The Platform Nobody Uses", curse="three commuters lost in a month",
                     blurb="Missing persons. A dead platform under Ikebukuro. The report says three commuters lost in a month.",
                     merit=28, yen=(10000, 15000), senior_only=True)],
        taken=[dict(taken_by="megumi", grade="g2", title="The Karaoke Box in Koenji")],
        ## Newest first, as WP4's board_summary gives it.
        log=[dict(day=15, grade="g3", partner="panda", outcome="withdrew", merit=0, title="Filed as Grade 3"),
             dict(day=13, grade="g4", partner="yuji", outcome="clean", merit=10, title="The Train Depot"),
             dict(day=11, grade="g3", partner="maki", outcome="costly", merit=11, title="The School Pool in Setagaya"),
             dict(day=9, grade="g4", partner="nobara", outcome="clean", merit=10, title="A Grudge the Size of a Dog")],
        misgrades=1)
    ## The stubs have no place table; WP4's real one is used when it exists.
    if not getattr(store, "BOARD_PLACE_BY_KEY", None):
        store.BOARD_PLACE_BY_KEY = dict(
            adachi=dict(key="adachi", phrase="a closed maternity ward in Adachi", short="The Adachi Ward"),
            kita=dict(key="kita", phrase="an apartment stairwell in Kita", short="The Kita Stairwell"),
            ikebukuro=dict(key="ikebukuro", phrase="a dead platform under Ikebukuro", short="The Dead Platform"))

    ## --- items (WP6) -----------------------------------------------------------

    def zzj_item(**kw):
        """A fixture item with every key WP6's _item() gives a record (its
        sync_keepsakes reads it["from_flag"] on every item)."""
        rec = dict(name="", kind="keepsake", grade=None, special=False, sealed=None, stack=False,
                   desc="", effect="", fx={}, source="", from_flag=None, hidden=False)
        rec.update(kw)
        return rec

    ZZJ_ITEMS = dict(
        photo=dict(name="The Photo", kind="keepsake", grade=None, desc="The four of us at the diner, last spring.", effect="", source="Packed the night I left home"),
        sealing_talisman=dict(name="Sealing Talisman", kind="sealing", grade="g4", stack=True, desc="Binds a curse for a moment.", effect="Binds a curse for a turn", source="Utahime's board"),
        first_aid=dict(name="First-Aid Kit", kind="supply", grade=None, stack=True, desc="Tape, gauze, and a note from Shoko.", effect="", source="The infirmary"),
        kurose_card=dict(name="Kurose's Card", kind="mission", grade=None, desc="Auxiliary management. A mobile number, handwritten.", effect="", source="Kurose"),
        slaughter_demon=dict(name="Slaughter Demon", kind="tool", grade="g4", desc="A short blade that cuts what a fist can't.", effect="Strikes leave a bleed", source="The armory"),
        nunchaku=dict(name="Nunchaku", kind="tool", grade="g3", desc="Maki's recommendation for a beginner. She was smiling.", effect="Chained strikes", source="The armory"),
        paper_ward=dict(name="Paper Ward", kind="talisman", grade="g4", desc="A folded ward that holds a little more.", effect="+10 reserve", source="Utahime"),
        steady_hand=dict(name="Steady Hand", kind="talisman", grade="g4", desc="Makes the technique cheaper to hold.", effect="Techniques cost 10% less", source="The board"),
        iron_seal=dict(name="Iron Seal", kind="talisman", grade="g3", desc="Hits harder, guards worse.", effect="+15% strike, -15% guard", source="The board"),
        spark=dict(name="Spark", kind="talisman", grade="g2", desc="A wider window for a perfect strike.", effect="Black Flash window +10%", source="The board"),
        unending_moment=dict(name="Unending Moment", kind="talisman", grade="sp", special=True, desc="Bound by story.", effect="", source="Story"),
        zzj_ward_a=dict(name="Kantō Ward", kind="talisman", grade="g4", desc="A test ward with a macron.", effect="+5 reserve, and a long effect line that has to wrap onto a second line inside the picker row to test its height", source="The board"),
        zzj_ward_b=dict(name="Quiet Ward", kind="talisman", grade="g4", desc="A test ward.", effect="+5 guard", source="The board"),
        zzj_ward_c=dict(name="Thin Ward", kind="talisman", grade="g4", desc="A test ward.", effect="+5 control", source="The board"),
        zzj_ward_d=dict(name="Last Ward", kind="talisman", grade="g4", desc="A test ward.", effect="+5 output", source="The board"),
    )
    for _k, _v in ZZJ_ITEMS.items():
        ITEMS.setdefault(_k, zzj_item(**_v))

    def zzj_can_wear(iid):
        it = ITEMS.get(iid, {})
        if it.get("special"):
            return (False, "Special: bound by story")
        if grade_rank(it.get("grade")) > grade_rank(player_grade() or "g4"):
            return (False, "Needs %s" % grade_label(it.get("grade")))
        if len(store.equipped_talismans) >= talisman_slots():
            return (False, "No free slot — opens at Grade 3")
        return (True, "")

    def zzj_retain():
        if not zzj.no_retain:
            renpy.retain_after_load()

    ## The shims return True/False as WP6's real functions do, so a picker
    ## button that passed that value on (and so closed the journal) fails here.
    def zzj_equip_talisman(iid):
        if iid in store.equipped_talismans or not zzj_can_wear(iid)[0]:
            return False
        store.equipped_talismans = store.equipped_talismans + [iid]
        zzj_retain()
        return True

    def zzj_unequip_talisman(iid):
        if iid not in store.equipped_talismans:
            return False
        store.equipped_talismans = [x for x in store.equipped_talismans if x != iid]
        zzj_retain()
        return True

    def zzj_equip_tool(iid):
        store.equipped_tool = iid
        zzj_retain()
        return True

    zzj.stub6 = "WP0 stub" in (equip_tool.__doc__ or "")
    if zzj.stub6:
        store.can_wear = zzj_can_wear
        store.equip_talisman = zzj_equip_talisman
        store.unequip_talisman = zzj_unequip_talisman
        store.equip_tool = zzj_equip_tool

    ## --- the switches -----------------------------------------------------------

    zzj_switch("missions_list", zzj_missions_list)
    zzj_switch("mission_status", lambda id: ZZJ_STATUS.get(id, "locked"))
    zzj_switch("mission_reason", lambda id: ZZJ_REASON.get(id, ""))
    zzj_switch("act_progress", zzj_act_progress)
    zzj_switch("objective_text", lambda: "A man from auxiliary management is waiting outside Yaga's office — afternoons and evenings, wherever I am")
    zzj_switch("next_for", lambda who: ZZJ_NEXT.get(who))
    zzj_switch("main_story_complete", lambda: zzj.story_complete)
    zzj_switch("board_summary", lambda: ZZJ_BOARD)
    zzj_switch("misgrade_count", lambda: 1)
    zzj_switch("memory_groups", zzj_memory_groups)
    zzj_switch("memory_counts", zzj_memory_counts)
    zzj_switch("memory_replay", zzj_memory_replay)
    zzj_switch("usual_places", lambda who: {"gojo": "Nowhere you can predict. His office on the days he's in.",
                                             "yuji": "Cafeteria (noon) · Courtyard (afternoons) · Dorm common room (evenings)"}.get(who, "Classroom (mornings) · Cafeteria (noon)"))
    zzj_switch("when_at", lambda who, loc: "weekday mornings to afternoons")
    zzj_switch("gojo_in_today", lambda: True)
    zzj_switch("recent_promotion", lambda who, days=3: who == "nobara")

    def zzj_rich(on):
        """Turn the rich fixture's fakes on or off (ACTS and MEMORIES are
        swapped in place, and put back)."""
        zzj.rich = on
        if on:
            zzj.saved_acts = builtins.list(ACTS)
            zzj.saved_mems = builtins.list(MEMORIES)
            zzj.saved_tech = TECHNIQUES["timestop"]
            ACTS[:] = ZZJ_ACTS
            MEMORIES[:] = ZZJ_MEMORIES
            ## WP2's Last Light (3.4): the macron in jp, "Once a day" in verb_desc.
            TECHNIQUES["timestop"] = builtins.dict(zzj.saved_tech, name="Last Light", jp="残光 · Zankō",
                verb="Hold", verb_desc="Once a day, spend most of my reserve and the hour does not pass.")
        else:
            ACTS[:] = zzj.saved_acts
            MEMORIES[:] = zzj.saved_mems
            TECHNIQUES["timestop"] = zzj.saved_tech

    ## --- driving the journal ---------------------------------------------------

    def zzj_buttons(screen="journal"):
        s = renpy.get_screen(screen)
        out = []
        if s is None:
            return out
        def cb(d):
            if isinstance(d, renpy.display.behavior.Button):
                out.append(d)
        s.visit_all(cb)
        return out

    def zzj_flat(a):
        if isinstance(a, (list, tuple)):
            r = []
            for x in a:
                r.extend(zzj_flat(x))
            return r
        return [a]

    def zzj_find(pred, screen="journal", raw=False):
        """The first button in `screen` whose action (or any action in its
        list) satisfies pred. raw=True tests the action itself (a single
        action, not one inside a list)."""
        for b in zzj_buttons(screen):
            try:
                if raw and pred(b.action):
                    return b
                if not raw and any(pred(a) for a in zzj_flat(b.action)):
                    return b
            except Exception:
                continue
        return None

    def zzj_is_setdict(a, key, value):
        return type(a).__name__ == "SetDict" and a.key == key and a.value == value

    def zzj_is_fn(a, fn, *args):
        """a is Function(<the store function named fn>, *args, ...)."""
        return (isinstance(a, Function) and a.callable is getattr(store, fn, None)
                and tuple(a.args[:len(args)]) == args)

    def zzj_texts(screen="journal"):
        """Every Text string shown in `screen`."""
        s = renpy.get_screen(screen)
        out = []
        if s is None:
            return out
        def cb(d):
            if isinstance(d, renpy.text.text.Text):
                out.append("".join(x for x in d.text if isinstance(x, str)))
        s.visit_all(cb)
        return out

    def zzj_js():
        s = renpy.get_screen("journal")
        return s.scope.get("js") if s is not None else None

    def zzj_click(pred, name, raw=False):
        """Run a journal button's action, as a click would. Returns what the
        action returns (a Return ends the interaction)."""
        b = zzj_find(pred, raw=raw)
        check(b is not None, "journal has a button: " + name)
        if b is None:
            return None
        return renpy.run(b.action)

    def zzj_tick():
        """One scripted step per timer tick. A step returning non-None ends
        the interaction with that value."""
        if not zzj.script:
            return None
        fn = zzj.script.pop(0)
        try:
            return fn()
        except Exception as e:
            import traceback
            check(False, "driver step raised", traceback.format_exc())
            zzj.script[:] = []
            return "zzj_error"

    def zzj_start_interact():
        """Menu contexts: make sure the driver is showing there too."""
        if zzj.menu_driver and renpy.context()._menu and not renpy.get_screen("zzj_driver"):
            renpy.show_screen("zzj_driver")

    config.start_interact_callbacks.append(zzj_start_interact)

    def zzj_after_load():
        fn = zzj.after_load
        zzj.after_load = None
        if fn:
            fn()

    config.after_load_callbacks.append(zzj_after_load)

    def zzj_done():
        return "zzj_done"

    def zzj_nil(*values):
        """A step that must not end the interaction, whatever it returns."""
        return None


screen zzj_driver():
    zorder 500
    timer 0.35 repeat True action Function(zzj_tick)


## A label replayed from the journal (the fake memory_replay points here).
label zzj_mem_label:
    $ zzj.replays += 1
    $ zzj.replay_flags = (bool(_in_replay), bool(getattr(store, "zzj_scope_mark", False)))
    $ day = 999
    $ flag("zzj_replay_changed_this")
    "(A replayed memory.)"
    return


## Review round 2: what a replay sees. Replays run in a clean store (3.9),
## so the journal must not be offered, and says so if it is opened anyway.
label zzj_replay_probe:
    $ zzj.rp = builtins.dict(in_replay=bool(_in_replay), editable=journal_editable())
    show screen zzj_driver
    $ zzj.script[:] = [
        lambda: zzj_say_probe("replay_say"),
        lambda: zzj_nil(shot("replay_say", wait=0)),
        zzj_done,
    ]
    "(A line in a replay.)"
    $ zzj.script[:] = [
        lambda: zzj_nil(shot("replay_journal", wait=0)),
        lambda: zzj_nil(zzj.rp.update(journal_texts=zzj_texts(),
                                      tabs_sensitive=[bool(b.is_sensitive()) for b in zzj_buttons() if zzj_is_setdict(zzj_flat(b.action)[-1], "tab", "stats")])),
        zzj_done,
    ]
    call screen journal("stats")
    python:
        renpy.show_screen("preferences")
        renpy.pause(0.3, hard=True)
        zzj.rp["nav"] = zzj_texts("preferences")
        renpy.hide_screen("preferences")
    hide screen zzj_driver
    return


## A small label with dialogue, for the portrait and quick-menu checks.
label zzj_dialogue:
    show screen zzj_driver
    yuji "The vending machine ate my coin again."
    mc "It does that to everyone."
    hide screen zzj_driver
    return


label zz_smoke:

    $ fixture(mc_name="Tester", mc_surname="Harness")

    ## =====================================================================
    ## 1. Static: portraits fit the margin, the preference exists
    ## =====================================================================
    python:
        _bad = []
        _widest = (0, 0)
        for _f in renpy.list_files():
            if _f.startswith("images/side/") and _f.endswith(".png"):
                _w, _h = renpy.image_size(_f)
                _w8, _h8 = _w * 0.8, _h * 0.8
                _widest = (max(_widest[0], _w8), max(_widest[1], _h8))
                if 6 + _w8 > min(gui.dialogue_xpos, gui.name_xpos) or _h8 > gui.textbox_height:
                    _bad.append((_f, _w8, _h8))
        check(not _bad, "every side portrait at zoom 0.8 stays inside the 300px dialogue margin", _bad)
        note("widest side portrait at 0.8", "%dx%d" % _widest)
        check(persistent.mc_face is True, "persistent.mc_face defaults to True")
        ## The fonts have no ō: dialogue, names, choices and the journal take it
        ## (and ✓ ◌ ∞) from DejaVu Sans through macron_font().
        _fg = [style.default.font, style.say_label.font, style.choice_button_text.font, JR_DISPLAY_FONT, JR_BODY_FONT]
        check(all(isinstance(f, FontGroup) and f.map.get(0x14D) in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")
                  and f.map.get(0x221E) == f.map.get(0x14D) and f.map.get(ord("a")) is None for f in _fg),
              "ō (U+014D) comes from DejaVu Sans in dialogue, names, choices and the journal")
        ## Review round 2: every style that draws text, not only default.
        _plain = []
        for _n in ("history_text", "history_name_text", "input", "input_prompt", "pref_label_text", "radio_button_text",
                   "check_button_text", "button_text", "label_text", "gui_text", "quick_button_text",
                   "navigation_button_text", "game_menu_label_text", "slot_name_text", "slot_time_text",
                   "confirm_prompt_text", "confirm_button_text", "say_dialogue", "namebox_label", "notify_text"):
            _f = getattr(style, _n).font
            if not (isinstance(_f, FontGroup) and _f.map.get(0x14D) in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")):
                _plain.append((_n, _f))
        check(not _plain, "ō comes from DejaVu Sans in history, input, preferences, buttons and every other text style", _plain)
        _allplain = [k for k, v in renpy.style.styles.items() if isinstance(v.font, str) and v.font in MACRON_FONTS]
        check(not _allplain, "no style is left on a plain base font", _allplain[:10])
        note("style fonts given their macron group", getattr(macron_styles, "changed", None))
        check(style.say_label.font.map.get(0x14D) == "DejaVuSans-Bold.ttf" and style.history_name_text.font.map.get(0x14D) == "DejaVuSans-Bold.ttf"
              and style.input.font.map.get(0x14D) == "DejaVuSans-Bold.ttf" and JR_BOLD_FONT.map.get(0x14D) == "DejaVuSans-Bold.ttf",
              "bold bases (the name box, history names, input, the journal's bold) take ō from DejaVu Sans Bold")
        check(style.default.font.map.get(0x14D) == "DejaVuSans.ttf" and style.history_text.font.map.get(0x14D) == "DejaVuSans.ttf"
              and style.pref_label_text.font.map.get(0x14D) == "DejaVuSans.ttf",
              "regular and medium bases take ō from DejaVu Sans")

    ## =====================================================================
    ## 2. Fresh state (a new game, before the campus): every tab renders
    ## =====================================================================
    python:
        for _tab in ("people", "missions", "memories", "stats", "equipment", "inventory"):
            renpy.show_screen("journal", _tab)
            shot("fresh_" + _tab)
            _js = zzj_js()
            check(_js is not None and _js["tab"] == _tab, "fresh: journal(%r) renders on its tab" % _tab)
            renpy.hide_screen("journal")
        check(kaito_card_image() == "images/char/mcyotsuka_neutral.png", "Stats picture before the campus: the Yotsuka outfit")

    ## Before the campus: the default roster doesn't make anyone "met" early,
    ## the NEXT line stays neutral and the preference doesn't use the name.
    python:
        _c = dict((e["who"], e["met"]) for e in journal_cast())
        check(not _c["yuji"] and not _c["gojo"] and not _c["shoko"] and _c["sana"],
              "prologue start: rostered people are not met yet", _c)
        check(mc_portrait_label() == "MY PORTRAIT", "prologue start: the preference reads MY PORTRAIT", mc_portrait_label())
        check(not jr_on_campus(), "prologue start: not on campus")
        ## Review round 3: the Stats tab follows the same two rules.
        _yn = [r[0] for r in jr_year()]
        check(jr_stats_title() == "My journal" and _yn == ["Me"], "prologue start: Stats says My journal and Me, and names nobody unmet", (jr_stats_title(), _yn))
        renpy.show_screen("journal", "stats")
        shot("prologue_start_stats")
        _tx = zzj_texts()
        _leak = [t for t in _tx if any(w in t for w in ("Tester", "Harness", "Yuji", "Megumi", "Nobara", "Gojo"))]
        check(zzj_js()["tab"] == "stats" and "My journal" in _tx and "Me" in _tx and not _leak,
              "prologue start: the Stats tab doesn't show the name or unmet people", _leak)
        renpy.hide_screen("journal")
        fixture(story_point="chapter_one_b")
        _c = dict((e["who"], e["met"]) for e in journal_cast())
        check(_c["gojo"] and not _c["yuji"] and not _c["ijichi"], "chapter_one_b: Gojo met, the first-years not", _c)
        check("mc_name" in mc_portrait_label(), "after Gojo asks the name, the preference uses it", mc_portrait_label())
        _yn = [r[0] for r in jr_year()]
        check(jr_stats_title() == "Harness Tester" and _yn == ["Tester", "Gojo"], "chapter_one_b: Stats uses the name; the year strip shows Gojo, not the first-years", (jr_stats_title(), _yn))
        renpy.show_screen("journal", "stats")
        shot("chapter_one_b_stats")
        _tx = zzj_texts()
        check("Harness Tester" in _tx and not any(w in t for t in _tx for w in ("Yuji", "Megumi", "Nobara")),
              "chapter_one_b: the Stats tab shows the name and Gojo only")
        renpy.hide_screen("journal")
        fixture(story_point="ch2_first_years")
        _c = dict((e["who"], e["met"]) for e in journal_cast())
        check(_c["yuji"] and _c["ijichi"] and _c["yaga"] and not _c["shoko"] and not _c["maki"],
              "ch2_first_years: first-years, Ijichi and Yaga met, Shoko not", _c)
        _yn = [r[0] for r in jr_year()]
        check(_yn == ["Tester", "Yuji", "Megumi", "Nobara", "Gojo"], "ch2_first_years: the year strip names all four", _yn)
        renpy.show_screen("journal", "people")
        shot("prologue_people")
        renpy.hide_screen("journal")
        ## An old save without story_point: its flags place it (legacy_story_point).
        fixture(story_point=None, flags={"reached_for_her", "gojo_asked_why"})
        _c = dict((e["who"], e["met"]) for e in journal_cast())
        check(_c["gojo"] and not _c["yuji"], "old save in chapter_one_b (flags only): Gojo met, Yuji not", _c)
        fixture(flags=set())

    ## The wrappers.
    python:
        renpy.show_screen("jjk_status")
        shot("wrapper_jjk_status")
        check(renpy.get_screen("jjk_status") is not None, "jjk_status renders (use journal(\"stats\"))")
        renpy.hide_screen("jjk_status")
        renpy.show_screen("jjk_journal")
        shot("wrapper_jjk_journal")
        check(renpy.get_screen("jjk_journal") is not None, "jjk_journal renders (use journal(\"people\"))")
        renpy.hide_screen("jjk_journal")

    ## Settled, day 1.
    $ settle(day=1)
    python:
        check(kaito_card_image() == "images/char/mc_neutral.png", "Stats picture on campus: the uniform")
        for _tab in ("people", "stats"):
            renpy.show_screen("journal", _tab)
            shot("settled_" + _tab)
            _js = zzj_js()
            check(_js is not None and _js["tab"] == _tab, "settled: journal(%r) renders" % _tab)
            renpy.hide_screen("journal")
        _c = dict((e["who"], e["met"]) for e in journal_cast())
        check(_c["yuji"] and _c["shoko"] and jr_on_campus(), "settled: the roster counts as met", _c)

    ## =====================================================================
    ## 3. The rich fixture
    ## =====================================================================
    python:
        zzj_rich(True)
        for _w in ("maki", "panda", "toge", "utahime"):
            if _w not in roster:
                roster.append(_w)
        bonds.update(dict(yuji=62, megumi=41, nobara=47, maki=28, panda=22, toge=18, gojo=35,
                          utahime=12, shoko=24, yaga=15, ijichi=30))
        affection.update(dict(nobara=35, maki=12, shoko=8))
        threads.update(dict(yuji_countdown=2, megumi_tsumiki=1, nobara_saori=1, maki_zenin=0, gojo_measure=1))
        for _f in ("roll_call", "met_nanami", "sunmall_done", "mission_board_open", "utahime_arrived"):
            flag(_f)
        done_events.add("st_roll_call")
        done_events.add("zzj_mem_label")
        fixture(technique="timestop", day=16, period="Afternoon", here="courtyard", merit=84, ce=90, ce_max=130,
                control=47, output=38, insight=31, stamina=62,
                memories_seen={"ch1_diner": 0, "ch1_the_thing": 0, "ch1_gojo": 0, "chapter_one_b": 0,
                               "ch2_arrival": 0, "ch2_the_veil": 0, "ch2_first_years": 0},
                districts_visited={"yotsuka"}, yen=12000,
                inventory=dict(photo=1, sealing_talisman=3, first_aid=2, kurose_card=1, slaughter_demon=1,
                               nunchaku=1, paper_ward=1, steady_hand=1, iron_seal=1, spark=1,
                               zzj_ward_a=1, zzj_ward_b=1, zzj_ward_c=1, zzj_ward_d=1),
                equipped_tool="slaughter_demon", equipped_talismans=["paper_ward"])
        promote("mc", "g3", quiet=True)
        promote("nobara", "g2", quiet=True)
        if not [p for p in (getattr(store, "promotions_log", None) or []) if jr_get(p, "who") == "nobara"]:
            fixture(promotions_log=[dict(day=16, who="nobara", grade="g2", why="")])
        refresh_vitals()
        hp = max(1, hp_max - 12)
        check(player_grade() == "g3" and talisman_slots() == 2, "rich fixture: Grade 3, two slots", (player_grade(), talisman_slots()))

    python:
        for _tab in ("people", "missions", "memories", "stats", "equipment", "inventory"):
            renpy.show_screen("journal", _tab)
            shot("rich_" + _tab)
            _js = zzj_js()
            check(_js is not None and _js["tab"] == _tab, "rich: journal(%r) renders" % _tab)
            renpy.hide_screen("journal")

    ## Data checks on the rich fixture.
    python:
        _cards = dict((e["who"], e) for e in journal_cast())
        check(_cards["yuji"]["met"] and _cards["maki"]["met"], "met cards: rostered people")
        check(_cards["nanami"]["met"] and not _cards["nanami"]["art"], "nanami met by flag, no art: the 「？」 card")
        check(not _cards["todo"]["met"] and _cards["todo"]["hint"], "todo unmet, with his hint")
        check(_cards["sana"]["met"], "sana always shown")
        check(jr_grade_line("gojo") == "Off the scale", "Gojo's chip reads Off the scale", jr_grade_line("gojo"))
        check(jr_grade_line("shoko") == "Doctor", "the ungraded show their role", jr_grade_line("shoko"))
        check(jr_grade_line("nobara") == "Grade 2", "a promoted NPC shows the new grade", jr_grade_line("nobara"))
        check(jr_next("maki") == "Next: The Armory: pick your first cursed tool — Storehouse" or jr_next("maki").startswith("Next: The Armory"), "Next line with where", jr_next("maki"))
        ## Review round 3: a long Next keeps its place whole on the card.
        _nx0 = ZZJ_NEXT["nobara"]
        _nx_m0 = ZZJ_NEXT.get("megumi")
        ZZJ_NEXT["nobara"] = ("The Teacher Ranking: a letter from someone I haven't thought about in years, and what it says", "dorm_common")
        _ln = jr_next("nobara", 74)
        _pl = jr_place_name("dorm_common")
        check(_ln.endswith(" — " + _pl) and len(_ln) <= 76 and "…" in _ln, "a long Next is clipped in its text and keeps the place", _ln)
        renpy.show_screen("journal", "people")
        shot("rich_people_long_next")
        _tx = zzj_texts()
        check(_ln in _tx, "the card draws the clipped Next with its place", [t for t in _tx if t.startswith("Next:")][:4])
        renpy.hide_screen("journal")
        ## Integration round: WP3's real next_for passes WP1's whole weekly
        ## schedule as the where; the card line still fits its two lines.
        ZZJ_NEXT["nobara"] = ("Spend time together", "Classroom Building (mornings) · Cafeteria (noon) · Courtyard (afternoons) · Dorm Common Room (evenings) · Girls' Dormitory (nights)")
        ZZJ_NEXT["megumi"] = ("Eat together at the Cafeteria", "Classroom Building (mornings) · Cafeteria (noon) · Training Grounds (afternoons) · Dorm Common Room (evenings) · Boys' Dormitory (nights)")
        _ln = jr_next("nobara", 74)
        _lm = jr_next("megumi", 74)
        check(len(_ln) <= 74 and _ln.startswith("Next: Spend time together — Classroom Building (mornings)") and _ln.endswith(" …"),
              "a schedule-long where keeps its first places and the whole text", _ln)
        check(len(_lm) <= 74 and _lm.startswith("Next: Eat together at the Cafeteria — "), "a second schedule-long Next fits too", _lm)
        renpy.show_screen("journal", "people")
        shot("rich_people_schedule_next")
        _tx = zzj_texts()
        check(_ln in _tx and _lm in _tx, "the cards draw the shortened schedule lines", [t for t in _tx if t.startswith("Next:")][:4])
        renpy.hide_screen("journal")
        ## WP11: the " …" after a shortened schedule counts, and the where is
        ## clipped before the text, so "Bond 10" keeps its number (the real
        ## Utahime and Yaga lines).
        ZZJ_NEXT["nobara"] = ("Eat together at Bond 10", "Utahime's Office (mornings to afternoons) · Cafeteria (evenings)")
        ZZJ_NEXT["megumi"] = ("Eat together at Bond 10", "Principal's Office (mornings, noon and evenings) · Storehouse (afternoons)")
        _ln = jr_next("nobara", 74)
        _lm = jr_next("megumi", 74)
        check(len(_ln) <= 74 and _ln.startswith("Next: Eat together at Bond 10 — Utahime's Office") and _ln.endswith("…"),
              "a long where is clipped before the text", _ln)
        check(len(_lm) <= 74 and _lm.startswith("Next: Eat together at Bond 10 — Principal's"), "the text keeps its number", _lm)
        renpy.show_screen("journal", "people")
        shot("rich_people_where_clipped")
        _tx = zzj_texts()
        check(_ln in _tx and _lm in _tx, "the cards draw the lines with the where clipped", [t for t in _tx if t.startswith("Next:")][:4])
        renpy.hide_screen("journal")
        ZZJ_NEXT["nobara"] = ("Spend time together", "Mountain Ridge (mornings) · Cafeteria (noon) · Rooftop (afternoons) · Dorm Common Room (evenings)")
        _ln = jr_next("nobara", 74)
        check(_ln == "Next: Spend time together — Mountain Ridge (mornings) · Cafeteria (noon) …",
              "a second place goes in when it fits with the …", _ln)
        ZZJ_NEXT["nobara"] = ("Spend time together", "Classroom Building (mornings) · Rooftop (noon) · Courtyard (afternoons)")
        _ln = jr_next("nobara", 74)
        check(len(_ln) <= 74 and _ln == "Next: Spend time together — Classroom Building (mornings) …",
              "the … counts toward the line", (_ln, len(_ln)))
        ZZJ_NEXT["nobara"] = _nx0
        ZZJ_NEXT["megumi"] = _nx_m0
        ## Integration round: the Board tab against WP4's real shapes.
        _bd = jr_board()
        check([jr_get(r, "day") for r in _bd["log"]] == [15, 13, 11, 9],
              "Board tab: LAST JOBS newest first, as board_summary gives it", [jr_get(r, "day") for r in _bd["log"]])
        check(jr_offer_line(ZZJ_BOARD["offers"][1]) == "Residual clean-up · an apartment stairwell in Kita",
              "Board tab: an offer's place key reads as its phrase", jr_offer_line(ZZJ_BOARD["offers"][1]))
        check(jr_board_place("somewhere else") == "somewhere else", "a place that isn't a key shows as it is")
        _d = jr_person("nobara")
        check(any("Promoted to Grade 2 on Day 16" == p for p in _d["promotions"]), "People detail: promotion line (promoted today, day 16)", _d["promotions"])
        check(jr_person("maki")["restricted"], "Maki's reserve reads Heavenly Restriction")
        check(jr_person("gojo")["off_scale"], "Gojo's bars run off the scale")
        _t = jr_tech()
        note("Last Light panel", "%s · %s · next: %s" % (_t["name"], _t["tier"], _t["next"]))
        _slots = [jr_slot_opens(i) for i in range(4)]
        check(_slots[1:] == ["Opens at Grade 3", "Opens at Grade 2", "Opens at Semi-Grade 1"], "slot cards name the grade that opens them", _slots)
        _sg = jr_story_groups("all")
        check([a["id"] for a, n, r in _sg] == ["P", "I", "II", "III"], "story groups by act", [a["id"] for a, n, r in _sg])
        _i = [r for a, n, r in _sg if a["id"] == "I"][0]
        check([r["status"] for r in _i].count("unwritten") == 3 and _i[-1]["line"] == "Coming in a later build", "unwritten rows: Coming in a later build")
        _iii = [r for a, n, r in _sg if a["id"] == "III"][0]
        check(_iii[0]["group"] == "The Surveyor 0/3", "group rows show The Surveyor n/3", _iii[0]["group"])
        _av = jr_story_groups("available")
        check(sum(len(r) for a, n, r in _av) == 2, "Available filter: available and waiting rows", [(r["id"], r["status"]) for a, n, r in _av for r in r])
        check(jr_mem_state([m for m in ZZJ_MEMORIES if m["id"] == "sana_mem_diner"][0]) == "later", "a triggered, unwritten Sana memory: Written in a later build")
        check(jr_mem_state([m for m in ZZJ_MEMORIES if m["id"] == "sana_mem_ranking"][0]) == "locked", "an untriggered memory stays locked")
        check(jr_memory_counts() == (9, 14), "memory counter", jr_memory_counts())

        ## Review round 1.
        _n = jr_person("nanami")
        _ns = npc_stats("nanami") or {}
        _nw = grade_label(_ns["grade"]) if _ns.get("grade") else "Grade 1 sorcerer"
        check(_n["name"] == "Kento Nanami" and _n["grade"] == _nw,
              "a JOURNAL_CAST-only person's pane: full name, and his grade (the role when he has none)", (_n["name"], _n["grade"], _nw))
        check(jr_short("nanami") == "Nanami" and jr_short("mei_mei") == "Mei Mei" and jr_short("yuta") == "Yuta",
              "short names for JOURNAL_CAST-only people", (jr_short("nanami"), jr_short("mei_mei"), jr_short("yuta")))
        _w = jr_mission_row([m for m in ZZJ_MISSIONS if m["id"] == "m_second_years"][0])
        check(_w["status"] == "waiting" and _w["line"] == "The second-years are back from wherever they were — afternoons, wherever I am, tomorrow",
              "a waiting row: objective, where and when, then when it opens", _w["line"])
        _t = jr_tech()
        check(_t["jp"] == "残光 · Zankō" and _t["verb_desc"].lower().count("once a day") == 1,
              "Last Light: WP2's jp, and 'once a day' said once", (_t["jp"], _t["verb_desc"]))
        _pm = jr_promotion()
        check(jr_merit_label(*[_pm[0], _pm[1], "Merit 84/150, then a promotion mission — Maki will watch."]) == ""
              and jr_merit_label(_pm[0], _pm[1], "") == "Merit %s / %s" % (_pm[0], _pm[1]),
              "promotion box: the merit shows once", (_pm, next_grade_text()))

        ## jr_wear keeps the other talismans where they are.
        _eq0 = (equipped_tool, list(equipped_talismans))
        if zzj.stub6:
            fixture(equipped_talismans=["paper_ward", "steady_hand"])
            jr_wear(0, "iron_seal")
            check(jr_worn() == ["iron_seal", "steady_hand"], "replacing slot 1 keeps slot 2 in place", jr_worn())
            jr_wear(1, "paper_ward")
            check(jr_worn() == ["iron_seal", "paper_ward"], "replacing slot 2 keeps slot 1 in place", jr_worn())
            jr_wear(0, "unending_moment")
            check(jr_worn() == ["iron_seal", "paper_ward"], "a refused talisman puts everything back in order", jr_worn())
        fixture(equipped_tool=_eq0[0], equipped_talismans=_eq0[1])

        ## The pre-campus NEXT fallback is gone on campus; the rich state is on campus.
        check(jr_on_campus(), "rich fixture: on campus")

    ## Detail panes, sub-tabs, filters, links: through the journal's own buttons.
    python:
        renpy.show_screen("journal", "people")
        shot("rich_people_again", wait=0.3)
    $ zzj.script[:] = [
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", "yuji"), "Yuji's card"),
        lambda: zzj_nil(shot("rich_people_detail_yuji", wait=0)),
        lambda: zzj_nil(check(zzj_js()["sel"] == "yuji", "clicking a met card opens the detail pane")),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", None), "Back", raw=True),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", "gojo"), "Gojo's card"),
        lambda: zzj_nil(shot("rich_people_detail_gojo", wait=0)),
        lambda: zzj_nil(check("∞" in zzj_texts(), "Gojo's pane draws his bars off the scale, ending in ∞", [t for t in zzj_texts() if len(t) < 4])),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", None), "Back", raw=True),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", "maki"), "Maki's card"),
        lambda: zzj_nil(shot("rich_people_detail_maki", wait=0)),
        lambda: zzj_nil(check("Heavenly Restriction" in zzj_texts(), "Maki's pane shows Heavenly Restriction for her reserve")),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", None), "Back", raw=True),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", "nanami"), "Nanami's card"),
        lambda: zzj_nil(shot("rich_people_detail_nanami", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", None), "Back", raw=True),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "sel", "nobara"), "Nobara's card"),
        lambda: zzj_nil(shot("rich_people_detail_nobara", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_go") and a.kwargs.get("mem_who") == "nobara", "Memories with them"),
        lambda: zzj_nil(check(zzj_js()["tab"] == "memories" and zzj_js()["mem_who"] == "nobara", "Memories with them opens the Memories tab filtered to her", dict(zzj_js()))),
        lambda: zzj_nil(shot("rich_memories_nobara", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "people"), "People tab"),
        lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_go") and a.kwargs.get("mem_who") == "sana", "Sana's card"),
        lambda: zzj_nil(check(zzj_js()["tab"] == "memories" and zzj_js()["mem_who"] == "sana", "Sana's card links to Memories filtered to her")),
        lambda: zzj_nil(shot("rich_memories_sana", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "mem_mode", "act"), "By act"),
        lambda: zzj_nil(shot("rich_memories_by_act", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "missions"), "Missions tab"),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "mfilter", "all"), "All filter"),
        lambda: zzj_nil(shot("rich_missions_story_all", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_toggle", zzj_js(), "collapsed", "I"), "Act I header"),
        lambda: zzj_nil(check(zzj_js()["collapsed"].get("I") is True, "act headers collapse")),
        lambda: zzj_nil(shot("rich_missions_story_collapsed", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "msub", "character"), "Character sub-tab"),
        lambda: zzj_nil(shot("rich_missions_character_all", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "msub", "board"), "Board sub-tab"),
        lambda: zzj_nil(shot("rich_missions_board", wait=0)),
        ## WP11: an offer card says the case and place once (the offer line),
        ## then what was reported, as the board does; not WP4's blurb, which
        ## repeats the case and place.
        lambda: zzj_nil(check("Reported: a call bell from a sealed room" in zzj_texts()
                              and not any(t.startswith("A haunting. A closed") for t in zzj_texts()),
                              "Board offer cards show the report, not the blurb",
                              [t for t in zzj_texts() if t.startswith(("Reported", "A haunting"))])),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "inventory"), "Inventory tab"),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "inv_sel", "slaughter_demon"), "an inventory tile"),
        lambda: zzj_nil(shot("rich_inventory_selected", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "inv_cat", "talisman"), "Talismans chip"),
        lambda: zzj_nil(check(zzj_js()["inv_cat"] == "talisman", "inventory category chips filter")),
        lambda: zzj_nil(shot("rich_inventory_talismans", wait=0)),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "equipment"), "Equipment tab"),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", ("talisman", 0)), "talisman slot 1"),
        lambda: zzj_nil(shot("rich_picker_many", wait=0)),
        lambda: zzj_nil(check(len(jr_pick_options("talisman", 0)) == 8, "the picker lists every talisman I own", len(jr_pick_options("talisman", 0)))),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", None), "Close", raw=True),
        ## Integration round: WP6's real equip functions return True/False;
        ## Unequip and Bare hands must keep the journal open all the same.
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", ("talisman", 0)), "talisman slot 1"),
        lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_takeoff", "paper_ward"), "Unequip"),
        lambda: zzj_nil(check(jr_worn() == [] and zzj_js()["pick"] is None and zzj_js()["tab"] == "equipment",
                              "Unequip takes the talisman off and the journal stays open", (jr_worn(), zzj_js()["pick"]))),
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", ("tool", 0)), "Change (tool)"),
        lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_hold", None), "Bare hands"),
        lambda: zzj_nil(check(jr_tool() is None and zzj_js()["pick"] is None, "Bare hands empties my hand and the journal stays open", jr_tool())),
        lambda: zzj_nil(shot("rich_equipment_bare", wait=0)),
        lambda: zzj_nil(fixture(equipped_tool="slaughter_demon", equipped_talismans=["paper_ward"])),
        zzj_done,
    ]
    show screen zzj_driver
    $ _r = ui.interact()
    hide screen zzj_driver
    $ renpy.hide_screen("journal")
    $ check(_r == "zzj_done", "the scripted walk through the journal finished", _r)

    ## Stress renders: long ranks and a promotion chip on the cards, a long
    ## given name in "Your year", an empty picker. Screenshots only; every
    ## one also checks it is on its tab.
    python:
        _b0, _a0, _t0, _n0 = dict(bonds), dict(affection), list(together), mc_name
        bonds.update(dict(maki=100, shoko=100, nobara=100))
        affection.update(dict(maki=100, shoko=100, nobara=100))
        ## Review round 3: the heart meter's scale follows the cap.
        check(jr_aff_scale("maki") == 100 and jr_aff_marker("maki") == aff_cap("maki"),
              "before the confession the heart meter runs 0-100 with the cap marker", (jr_aff_scale("maki"), jr_aff_marker("maki")))
        for _w in ("maki", "shoko", "nobara"):
            if _w not in together:
                together.append(_w)
        affection.update(dict(maki=200, shoko=150, nobara=175))
        _d = jr_person("shoko")
        check(jr_aff_scale("maki") == AFF_TRUE_MAX and jr_aff_marker("maki") is None and _d["aff_max"] == AFF_TRUE_MAX and _d["aff_marker"] is None,
              "together: the heart meter runs 0-200 with no cap marker", (jr_aff_scale("maki"), _d["aff_max"], _d["aff_marker"]))
        check(jr_meter_px(110, jr_aff_scale("maki"), 170) < jr_meter_px(195, jr_aff_scale("maki"), 170) < 170,
              "together: 110 and 195 affection draw different lengths")
        renpy.show_screen("journal", "people")
        shot("stress_people")
        check(zzj_js()["tab"] == "people", "stress: long ranks render")
        renpy.hide_screen("journal")
        fixture(mc_name="Maximiliana-Alexa")
        renpy.show_screen("journal", "stats")
        shot("stress_stats")
        check(zzj_js()["tab"] == "stats", "stress: a long given name renders")
        renpy.hide_screen("journal")
        ## Review round 2: the name prompt accepts "[", and a player-typed
        ## name must never be read as an interpolation.
        for _ni, _nm in enumerate(("Ōta", "Ren [", "[x]")):
            fixture(mc_name=_nm)
            renpy.show_screen("journal", "stats")
            shot("stress_stats_name_%d" % _ni)
            _tx = zzj_texts()
            check(zzj_js()["tab"] == "stats" and jr_clip(_nm, 14) in _tx,
                  "stress: the given name %r renders on Stats as typed" % _nm)
            renpy.hide_screen("journal")
            renpy.show_screen("preferences")
            shot("stress_prefs_name_%d" % _ni)
            _tx = zzj_texts("preferences")
            check(any(t.endswith("'S PORTRAIT") for t in _tx), "stress: Preferences renders with the given name %r" % _nm,
                  [t for t in _tx if "PORTRAIT" in t])
            renpy.hide_screen("preferences")
        renpy.show_screen("jjk_status")
        shot("stress_status_wrapper_name")
        check(renpy.get_screen("jjk_status") is not None, "stress: the jjk_status wrapper renders with that name")
        renpy.hide_screen("jjk_status")
        ## A long item name stays in two lines inside its tile.
        ITEMS["zzj_long"] = zzj_item(name="The Extraordinarily Long-Winded Keepsake of Ōsaka", kind="keepsake", grade="g4",
                                     desc="A test item.", effect="", source="The harness")
        inventory["zzj_long"] = 3
        renpy.show_screen("journal", "inventory")
        shot("stress_inventory_long_name")
        _tx = zzj_texts()
        _ln = [t for t in _tx if t.startswith("The Extraordinarily")]
        check(_ln and len(_ln[0]) <= 34, "stress: a long item name is clipped for its tile", _ln)
        renpy.hide_screen("journal")
        del inventory["zzj_long"]
        renpy.show_screen("journal", "equipment")
        shot("rich_equipment_kicker")
        _tx = zzj_texts()
        _k = [t for t in _tx if t.startswith("TALISMANS")]
        check(_k and _k[0] == "TALISMANS · %s at my grade" % ("1 slot" if talisman_slots() == 1 else "%d slots" % talisman_slots()),
              "the Equipment kicker counts slots in words, no (s)", _k)
        renpy.hide_screen("journal")
        fixture(mc_name=_n0, together=_t0)
        bonds.clear(); bonds.update(_b0)
        affection.clear(); affection.update(_a0)

    ## =====================================================================
    ## 4. Arc Two card (D38): from campus it returns ("arc_two",)
    ## =====================================================================
    $ zzj.story_complete = True
    $ zzj.script[:] = [
        lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "missions"), "Missions tab"),
        lambda: zzj_nil(shot("rich_missions_arc_two", wait=0)),
        lambda: zzj_nil(check(journal_editable(), "journal opened by `call screen` on campus is editable")),
        lambda: zzj_click(lambda a: type(a).__name__ == "Return" and a.value == ("arc_two",), "Begin Arc Two"),
    ]
    show screen zzj_driver
    call screen journal("people")
    hide screen zzj_driver
    $ check(_return == ("arc_two",), "Begin Arc Two returns (\"arc_two\",) to the loop", _return)

    ## Return (the rail button) returns None.
    $ zzj.script[:] = [
        lambda: zzj_click(lambda a: type(a).__name__ == "Return" and a.value is None, "Return"),
    ]
    show screen zzj_driver
    call screen journal("stats")
    hide screen zzj_driver
    $ check(_return not in (("arc_two",), "zzj_done", None), "the rail's Return leaves the journal (Ren'Py returns True)", _return)

    ## =====================================================================
    ## 5. Equipment through the campus journal survives save and load
    ## =====================================================================
    python:
        note("equip functions", "WP6 stubs, harness fakes (with retain_after_load)" if zzj.stub6 else "WP6's own")
    call zzj_equip_roundtrip("equip_retain", False)
    if zzj.stub6:
        ## The same round trip without retain_after_load, to show the check
        ## can fail (D4's second safeguard is what keeps the change).
        call zzj_equip_roundtrip("equip_noretain", True)

    ## Menu context: read-only equipment, no Arc Two card, replay returns.
    python:
        fixture(equipped_tool="slaughter_demon", equipped_talismans=["paper_ward"])
        zzj.menu_driver = True
        zzj.script[:] = [
            lambda: zzj_nil(check(renpy.context()._menu and not journal_editable(), "journal from a menu context is not editable")),
            lambda: zzj_nil(shot("menu_equipment_readonly", wait=0)),
            lambda: zzj_nil(check(zzj_find(lambda a: zzj_is_setdict(a, "pick", ("tool", 0))) is None, "menu context: no Change button")),
            lambda: zzj_nil(check(all(not b.is_sensitive() for b in zzj_buttons() if any(zzj_is_setdict(a, "pick", ("talisman", 0)) for a in zzj_flat(b.action))), "menu context: slots are not clickable")),
            lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "missions"), "Missions tab"),
            lambda: zzj_nil(check(zzj_find(lambda a: type(a).__name__ == "Return" and a.value == ("arc_two",)) is None, "menu context: no Begin Arc Two button")),
            lambda: zzj_nil(shot("menu_missions_arc_two_note", wait=0)),
            lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "memories"), "Memories tab"),
            lambda: zzj_menu_replay(),
            lambda: zzj_nil(check(renpy.get_screen("journal") is not None and zzj_js()["tab"] == "memories", "menu context: after the replay, the journal is back on Memories")),
            lambda: zzj_nil(shot("menu_after_replay", wait=0)),
            lambda: zzj_click(lambda a: type(a).__name__ == "Return" and a.value is None, "Return"),
        ]
        zzj.replays = 0
        _day0, _flags0 = day, set(flags)
        ShowMenu("journal", "equipment")()
        zzj.menu_driver = False
        renpy.hide_screen("zzj_driver")
        check(zzj.replays == 1, "menu context: the replay ran once", zzj.replays)
        check(day == _day0 and flags == _flags0, "menu context: the replay left the save's state alone", (day, _day0))

    ## =====================================================================
    ## 6. A replay started from the campus journal returns to the journal
    ## =====================================================================
    python:
        zzj.replays = 0
        zzj.replay_flags = None
        _day0, _flags0, _bonds0 = day, set(flags), dict(bonds)
        zzj.script[:] = [
            lambda: zzj_click(lambda a: zzj_is_setdict(a, "tab", "memories"), "Memories tab"),
            lambda: zzj_nil(shot("campus_memories_before_replay", wait=0)),
            lambda: zzj_replay_click("a seen memory tile"),
            lambda: zzj_nil(check(renpy.get_screen("journal") is not None, "after the replay the journal is still showing")),
            lambda: zzj_nil(check(zzj_js() is not None and zzj_js()["tab"] == "memories", "after the replay the journal is still on Memories")),
            lambda: zzj_nil(shot("campus_after_replay", wait=0)),
            zzj_done,
        ]
    show screen zzj_driver
    call screen journal("people")
    hide screen zzj_driver
    python:
        check(_return == "zzj_done", "campus replay: the journal interaction carried on after the replay", _return)
        check(zzj.replays == 1, "campus replay: the memory played once", zzj.replays)
        check(zzj.replay_flags == (True, True), "campus replay: it ran as a replay, with its scope", zzj.replay_flags)
        check(day == _day0 and flags == _flags0 and bonds == _bonds0, "campus replay: day, flags and bonds unchanged")

    ## =====================================================================
    ## 7. Quick menu and side portraits
    ## =====================================================================
    python:
        zzj_rich(False)
        here = "cafeteria"
        period = "Noon"
        quick_menu = True
        renpy.show_screen("sb_place")
        shot("quick_menu_sb_place")
        check(renpy.get_screen("sb_place") is not None and renpy.get_widget("quick_menu", "quick_menu_bar") is None,
              "quick menu hidden on sb_place")
        renpy.hide_screen("sb_place")
        renpy.show_screen("journal", "people")
        shot("quick_menu_journal", wait=0.3)
        check(renpy.get_widget("quick_menu", "quick_menu_bar") is None, "quick menu hidden over the journal")
        renpy.hide_screen("journal")
        scene_before = None

    scene expression graded_bg()
    python:
        zzj.say = []
        zzj.script[:] = [
            lambda: zzj_say_probe("yuji_offscreen"),
            lambda: zzj_nil(shot("say_yuji_offscreen", wait=0)),
            zzj_done,
            lambda: zzj_say_probe("mc_face_on"),
            lambda: zzj_nil(shot("say_mc_face_on", wait=0)),
            zzj_done,
        ]
    call zzj_dialogue
    python:
        _p = dict(zzj.say)
        check(_p.get("yuji_offscreen", (None,))[0] is not None, "quick menu shown in dialogue", _p.get("yuji_offscreen"))
        check(_p.get("yuji_offscreen", (None, None, []))[2] == ["BACK", "HISTORY", "SKIP", "AUTO", "SAVE", "JOURNAL", "MENU"],
              "quick menu: BACK · HISTORY · SKIP · AUTO · SAVE · JOURNAL · MENU", _p.get("yuji_offscreen"))
        check(_p.get("yuji_offscreen", (None, False))[1], "an off-screen speaker gets a side portrait")
        check(_p.get("mc_face_on", (None, False))[1], "my own portrait shows by default (mc_face on)")

    ## The preference: Hide.
    python:
        renpy.show_screen("preferences")
        shot("preferences_portrait_option", wait=0.3)
        _b = zzj_find(lambda a: type(a).__name__ == "SetField" and a.field == "mc_face" and a.value is False, "preferences")
        check(_b is not None, "Preferences has \"[mc_name]'s portrait: Hide\"")
        if _b is not None:
            renpy.run(_b.action)
        check(persistent.mc_face is False, "Hide sets persistent.mc_face False", persistent.mc_face)
        renpy.hide_screen("preferences")
        zzj.say = []
        zzj.script[:] = [
            lambda: zzj_say_probe("yuji_face_off"),
            zzj_done,
            lambda: zzj_say_probe("mc_face_off"),
            lambda: zzj_nil(shot("say_mc_face_off", wait=0)),
            zzj_done,
        ]
    call zzj_dialogue
    python:
        _p = dict(zzj.say)
        check(not _p.get("mc_face_off", (None, True))[1], "mc_face Hide: no portrait on my own lines")
        check(_p.get("yuji_face_off", (None, False))[1], "mc_face Hide: other speakers keep theirs")
        persistent.mc_face = True
        hide_side_images = True
        zzj.say = []
        zzj.script[:] = [
            lambda: zzj_say_probe("blackout_yuji"),
            lambda: zzj_nil(shot("say_blackout", wait=0)),
            zzj_done,
            zzj_done,
        ]
    call zzj_dialogue
    python:
        _p = dict(zzj.say)
        check(not _p.get("blackout_yuji", (None, True))[1], "hide_side_images hides every portrait (the blackout)")
        hide_side_images = False

    ## Review round 2: the journal during a replay.
    python:
        zzj.say = []
        zzj.rp = {}
        renpy.call_replay("zzj_replay_probe", scope={})
        _rp = zzj.rp
        _p = dict(zzj.say)
        check(_rp.get("in_replay") and not _rp.get("editable"), "replay: the probe ran as a replay, read-only", _rp)
        _q = _p.get("replay_say", (None, None, []))
        check(_q[0] is not None and "JOURNAL" not in _q[2] and "MENU" in _q[2],
              "replay: the quick menu has no JOURNAL button", _q[2])
        _jt = _rp.get("journal_texts", [])
        check("The journal isn't kept during a replay." in _jt and not any(t.startswith("◆ NEXT") for t in _jt),
              "replay: the journal says it isn't kept, instead of a wiped save", _jt[:12])
        check(_rp.get("tabs_sensitive") == [False], "replay: the journal's tabs can't be clicked", _rp.get("tabs_sensitive"))
        _nv = _rp.get("nav", [])
        check("End Replay" in _nv and "Journal" not in _nv, "replay: the game menu has no Journal entry", _nv[:12])

    $ finish()


## An equipment change through the campus journal, a save taken inside that
## interaction (as an autosave or a quit-save would be), then a load.
##
## A load puts the game back at the start of the statements that followed the
## last checkpoint, with the store as it was there, plus whatever
## retain_after_load kept. In the loop that checkpoint is `call screen
## sb_place`; here an explicit renpy.checkpoint() stands in for it, after the
## equipment is cleared, so the statements a load re-runs are only the ones
## the loop has too: the journal's `call screen`.
label zzj_equip_roundtrip(tag, noretain):
    python:
        zzj.no_retain = noretain
        zzj.phase = tag
        fixture(equipped_tool=None, equipped_talismans=[])
        renpy.checkpoint()
    python:
        if zzj.phase == tag + ":loaded":
            ## Re-run after the load: just let the reloaded journal close.
            zzj.script[:] = [zzj_done]
        else:
            zzj.script[:] = [
                lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", ("tool", 0)), "Change (tool)"),
                lambda: zzj_nil(shot(tag + "_picker_tool", wait=0)),
                lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_hold", "slaughter_demon"), "the Slaughter Demon row"),
                lambda: zzj_click(lambda a: zzj_is_setdict(a, "pick", ("talisman", 0)), "talisman slot 1"),
                lambda: zzj_nil(shot(tag + "_picker_talisman", wait=0)),
                lambda: zzj_click(lambda a: zzj_is_fn(a, "jr_wear", 0, "paper_ward"), "the Paper Ward row"),
                lambda: zzj_nil(shot(tag + "_equipped", wait=0)),
                lambda: zzj_nil(check(jr_tool() == "slaughter_demon" and jr_worn() == ["paper_ward"],
                                      tag + ": the picker changed the equipment", (jr_tool(), jr_worn()))),
                lambda: zzj_nil(renpy.save("9-9", "wp8 " + tag)),
                lambda: zzj_save_then_load(tag),
            ]
    show screen zzj_driver
    $ _r = ("journal", "equipment")
    call screen journal(_r[1])
    hide screen zzj_driver
    $ check(zzj.phase == tag + ":loaded", tag + ": the save was loaded and the journal closed again", zzj.phase)
    return


init 999 python:

    def zzj_save_then_load(tag):
        """Leave the interaction as it is, wipe the equipment in memory, load
        the save made inside the interaction, and check what came back."""
        def after():
            got = (jr_tool(), jr_worn())
            want = ("slaughter_demon", ["paper_ward"])
            if zzj.no_retain:
                note(tag + ": without retain_after_load the load gives back", repr(got))
                check(got != want, tag + ": (control) without retain_after_load the change is lost", got)
            else:
                check(got == want, tag + ": the equipment change survives a save and a load", got)
            zzj.phase = tag + ":loaded"
            zzj.script[:] = [zzj_done]
        zzj.after_load = after
        store.equipped_tool = None
        store.equipped_talismans = []
        renpy.load("9-9")

    def zzj_replay_click(name):
        """Click a seen memory tile. The replayed scene's lines are skipped
        (autoplay) so the replay plays through unattended."""
        autoplay(True)
        try:
            zzj_click(lambda a: type(a).__name__ == "Replay", name)
        finally:
            autoplay(False)
        return None

    def zzj_menu_replay():
        return zzj_replay_click("a seen memory tile (menu context)")

    def zzj_say_probe(name):
        """During a say: is the quick menu bar there, is a side portrait
        there, and what the quick menu's buttons say."""
        bar = renpy.get_widget("quick_menu", "quick_menu_bar")
        side = renpy.get_widget("say", "side_portrait")
        labels = []
        if bar is not None:
            def cb(d):
                if isinstance(d, renpy.display.behavior.Button):
                    t = []
                    def tc(x):
                        if isinstance(x, renpy.text.text.Text):
                            t.append("".join(s for s in x.text if isinstance(s, str)))
                    d.visit_all(tc)
                    labels.append(t[0] if t else "")
            bar.visit_all(cb)
        zzj.say.append((name, (bar, side is not None, labels)))
        return None
