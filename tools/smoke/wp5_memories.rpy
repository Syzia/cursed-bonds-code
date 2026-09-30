## tools/smoke/wp5_memories.rpy -- WP5's harness: memories and replay
## (PHASE1_DESIGN.md 3.9, D5, D6, D11, and WP5's acceptance list).
##
##   tools/smoke.sh tools/smoke/wp5_memories.rpy
##
## Checks, one named check (or group) per acceptance bullet:
##   catalogue    the contents 3.9 asks for, the validator is quiet, and it
##                does catch a broken entry;
##   legacy       an old-save fixture (flags and done_events only, then the
##                migrations) lists the right seen entries by person and by act;
##   recorder     the label callback records st_roll_call in normal play, but
##                not inside renpy.call_replay; record_act likewise;
##   scope        memory_scope has every key 3.9 names, as copies;
##   replay       replaying st_roll_call and act_confide("yuji") through
##                mem_play (and through the journal's action) leaves bonds,
##                flags, day and period unchanged, and raises no toasts;
##   sana         the three flashbacks show their hints, then "Written in a
##                later build" once each trigger is met;
##   migration 65 (memory part) backfills the prologue and is idempotent.
## Screenshots (shots/wp5_memories/): the memories by person and by act, as a
## harness-drawn board (the journal's real tab is WP8's), and a replayed scene.

init 999 python:
    import builtins

    ## Every label entered, with whether a replay was running. A builtins list
    ## made at init: replays, rollback and loads leave it alone.
    ZZ_LABELS = builtins.list()
    ZZ_TOASTS = builtins.list()
    ZZ_INSIDE = builtins.list()
    ZZ_SWEPT = builtins.list()

    ## The sweep leaves out scenes with a fight, which wait for input until
    ## WP2's smoke_autoplay timer is in combat_screen, and The Offer, whose
    ## "other road" ends in renpy.full_restart() until WP9's replay guard
    ## (5.2). WP11 can empty this once both have merged.
    ZZ_SWEEP_SKIP = ("ms_nade_1", "ms_nade_2", "chapter_one_b")

    def zz_label_spy(name, abnormal):
        ZZ_LABELS.append((name, bool(getattr(store, "_in_replay", None))))

    config.label_callbacks.append(zz_label_spy)

    def zz_toast_sink(text, kind, who, amount):
        ZZ_TOASTS.append((text, kind, who, amount))

    def zz_ids(entries, states=("seen", "later")):
        return set(e["id"] for e in entries if e["state"] in states)

    def zz_group(groups, title):
        for t, es in groups:
            if t == title:
                return es
        return None

    def zz_snapshot():
        import copy
        return dict(bonds=dict(store.bonds), flags=set(store.flags), day=store.day,
                    period=store.period, affection=dict(store.affection),
                    memories_seen=dict(store.memories_seen), seen_acts=set(store.seen_acts),
                    done_events=set(store.done_events), threads=copy.deepcopy(dict(store.threads)),
                    stamina=store.stamina, insight=store.insight)

    def zz_same(a, b):
        return [k for k in a if a[k] != b[k]]


## A harness-drawn view of memory_groups(): one line per group, each memory
## coloured by state, then Sana's group as thumbnail tiles at the journal's
## tile size (280x158), so the backgrounds and hints can be read.
screen zz_mem_board(mode):
    add Solid("#15131c")
    vbox:
        xpos 40 ypos 30 xmaximum 1840 spacing 6
        $ _c = memory_counts()
        text "Memories by [mode] · [_c[0]] of [_c[1]] found  (gold = seen, grey = unseen, violet = later)" size 24 color "#ffffff"
        for _t, _es in memory_groups(mode):
            hbox:
                spacing 10
                text _t size 17 color "#ffd27a" min_width 250
                text ", ".join(("{color=#ffd27a}" if e["state"] == "seen" else ("{color=#b89cff}" if e["state"] == "later" else "{color=#77737f}")) + e["title"] + "{/color}" for e in _es) size 15 xmaximum 1560
        null height 14
        text "Sana" size 22 color "#ffd27a"
        hbox:
            spacing 16
            for _e in memories_with("sana"):
                fixed:
                    xysize (280, 158)
                    add _e["bg"] fit "cover" xysize (280, 158)
                    if not _e["is_seen"]:
                        add Solid("#000000d8")
                        text "？" size 48 color "#ffffff" xalign 0.5 ypos 14
                    add Solid("#000000a0") ysize 56 yalign 1.0
                    vbox:
                        xpos 10 yalign 1.0 yoffset -6 xmaximum 260
                        text _e["title"] size 18 color "#ffffff"
                        text (_e["text"] or "Replay") size 14 color "#c8c4d0"


label zz_smoke:

    ## --- the catalogue (3.9) ----------------------------------------------------------
    python:
        _acts = {}
        for _m in MEMORIES:
            _acts[_m["act"]] = _acts.get(_m["act"], 0) + 1
        note("catalogue", "%d memories: %s" % (len(MEMORIES), sorted(_acts.items())))
        check(len(MEMORY_BY_ID) == len(MEMORIES), "catalogue ids are unique")
        _pro = [m["label"] for m in MEMORIES if m["act"] == "Prologue"]
        check(_pro == ["ch1_diner", "ch1_the_thing", "ch1_gojo", "chapter_one_b", "ch1b_goodbye",
                       "ch2_arrival", "ch2_the_veil", "ch2_yaga", "ch2_first_years"],
              "catalogue: the prologue sub-labels (D39)", _pro)
        check(MEMORY_BY_ID["ch1_diner"]["title"] == "Nine Hundred Yen" and "sana" in MEMORY_BY_ID["ch1_diner"]["who"]
              and MEMORY_BY_ID["ch1_the_thing"]["title"] == "The Thing She Told Me"
              and "sana" in MEMORY_BY_ID["ch1_the_thing"]["who"],
              "catalogue: Sana's two prologue memories")
        check(MEMORY_BY_ID["chapter_four"]["title"] == "Kawagoe Sun Mall"
              and MEMORY_BY_ID["chapter_five"]["title"] == "What Should Have Happened",
              "catalogue: the Sun Mall as chapter_four and chapter_five")
        _story = set(m["label"] for m in MEMORIES if m["act"] in ("I", "II", "III", "IV", "V"))
        _rows = {"st_roll_call", "st_utahime_office", "chapter_four", "chapter_five", "st_aftermath", "st_kurose",
                 "st_second_years", "st_noise", "st_oda_letter", "st_intensive", "st_promotion_g3",
                 "ms_nade_1", "st_kurose_2", "ms_nade_2", "st_oda_2", "ms_nade_3", "st_roster", "st_night_before"}
        check(_story == _rows, "catalogue: every written story row (3.6.1)", sorted(_story ^ _rows))
        _hang = set(e["label"] for e in EVENTS if e["kind"] == "hangout")
        _mhang = set(m["label"] for m in MEMORIES if m["act"] == "Bonds" and not m["args"])
        check(len(_hang) == 25 and _mhang == _hang, "catalogue: all 25 hangouts (D37)", sorted(_hang ^ _mhang))
        _acts_w = set(m["id"] for m in MEMORIES if m["args"])
        _want = set("%s:%s" % (a, w) for a in ("confide", "stand")
                    for w in ("yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "gojo", "yaga"))
        _want |= set("%s:%s" % (a, w) for a in ("rom_town", "rom_close", "rom_say", "int_night", "int_morning",
                                               "int_day", "int_after") for w in ("nobara", "maki", "shoko"))
        check(_acts_w == _want, "catalogue: act_confide, act_stand, act_rom_*, act_int_* per person", sorted(_acts_w ^ _want))
        check(all(m["args"] == (m["who"][0],) and m["label"].startswith("act_") for m in MEMORIES if m["args"]),
              "catalogue: activity memories replay with args=(who,)")
        _sana = [(m["label"], m["unlock"]) for m in MEMORIES if m["act"] == "Sana"]
        check(_sana == [("sana_mem_diner", ("district", "yotsuka")), ("sana_mem_daisy", ("item", "daisy_clip")),
                        ("sana_mem_ranking", ("flag", "oda_letter_read"))],
              "catalogue: Sana's three flashbacks and their triggers (D11)", _sana)
        _v = _validate_memories()
        check(_v == [], "validator is quiet on the catalogue", _v)
        _mem("zz_bad", "Bad", "VI", "zz_no_such_label", who=("nobody",), seen=[("smell", "x")], hint="", bg="bg nowhere")
        _v = _validate_memories()
        MEMORIES.pop()
        check(len(_v) >= 5 and any("zz_no_such_label" in p for p in _v), "validator catches a broken entry", _v)
        _missing = sorted(m["label"] for m in MEMORIES if not renpy.has_label(m["label"]))
        note("labels not in this tree yet (WP9, WP3, phase 3)", _missing)
        check(set(_missing) <= (MEMORY_PENDING_LABELS | MEMORY_UNWRITTEN_LABELS), "only pending labels are missing", _missing)
        check(all(renpy.has_image(m["bg"], exact=True) for m in MEMORIES), "every memory background exists")

    ## --- a fresh game: nothing seen, the stub contract still holds --------------------------
    python:
        check(memories_seen == {} and seen_acts == set(), "defaults: memories_seen {} and seen_acts set()")
        check(memory_counts() == (0, len(MEMORIES)), "fresh game: nothing found", memory_counts())
        check(isinstance(memory_replay({}), NullAction) and isinstance(memory_replay("st_roll_call"), NullAction),
              "memory_replay is NullAction for an unknown or unseen memory")
        _g = memory_groups("person")
        check(_g and _g[0][0] == "Sana", "by person: Sana's group comes first", [t for t, es in _g])
        check([t for t, es in memory_groups("act")] == ["Prologue · The Lights", "Act I · Grade Four",
              "Act II · The Ones Who Stay", "Act III · Overtime", "Act IV · Goodwill", "Bonds", "Sana"],
              "by act: the acts in order, empty ones left out", [t for t, es in memory_groups("act")])
        check(all(e["state"] == "unseen" and e["text"] == e["hint"] and not e["is_seen"]
                  for t, es in _g for e in es), "fresh game: every tile unseen, with its hint")
    call mem_play
    $ check(True, "mem_play outside a replay just returns")

    ## --- migration 65, the memory part ---------------------------------------------------------
    python:
        store.story_point = "ch2_arrival"
        _migrate_65_memories()
        check(set(memories_seen) == {"ch1_diner", "ch1_the_thing", "ch1_gojo", "chapter_one_b", "ch1b_goodbye"}
              and set(memories_seen.values()) == {0},
              "migration 65: a save resuming at ch2_arrival has seen the steps before it", memories_seen)
        store.story_point = None
        memories_seen.clear()
        _migrate_65_memories()
        check(memories_seen == {}, "migration 65: a brand-new game has seen nothing", memories_seen)

    ## --- the legacy fixture: an old save, read from flags and done_events -----------------------
    python:
        fixture(day=12, period="Noon", here="courtyard",
                roster=["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "maki", "panda", "toge"],
                bonds={"yuji": 70, "megumi": 82, "nobara": 55, "maki": 62, "panda": 66, "shoko": 90},
                affection={"shoko": 120, "nobara": 32, "maki": 50},
                together=["shoko"],
                done_events={"st_roll_call", "st_board_open", "ev_mission_sunmall", "st_aftermath", "st_kurose",
                             "ev_yuji_1", "ev_panda_1", "ev_shoko_1"},
                memories_seen={}, seen_acts=set(), save_version=0)
        for _f in ("chose_jujutsu", "enrolled", "roll_call", "sunmall_done", "aftermath_done", "kurose_met",
                   "confided_yuji", "did_confide_panda", "did_stand_megumi", "town_date_nobara", "close_maki",
                   "talked_about_after_shoko"):
            flag(_f)
    $ settle()
    python:
        run_migrations()
        _m1 = dict(memories_seen)
        run_migrations()
        check(memories_seen == _m1, "migration 65 is idempotent", (memories_seen, _m1))
        check(set(memories_seen) == set(MEMORY_PROLOGUE_ORDER) and set(memories_seen.values()) == {0},
              "migration 65: a settled save has seen the whole prologue (day 0)", memories_seen)

        _S = set(MEMORY_PROLOGUE_ORDER) | {
            "st_roll_call", "chapter_four", "chapter_five", "st_aftermath", "st_kurose",
            "ev_yuji_1", "ev_panda_1", "ev_shoko_1",
            "confide:yuji", "confide:panda", "stand:megumi", "rom_town:nobara", "rom_close:maki",
            "rom_say:shoko", "int_after:shoko"}
        _seen_now = set(m["id"] for m in MEMORIES if memory_seen(m))
        check(_seen_now == _S, "legacy: exactly the right memories are seen", sorted(_seen_now ^ _S))

        _gp = memory_groups("person")
        _bad = []
        for _t, _es in _gp:
            _who = [w for w in MEMORY_PEOPLE if CAST[w]["short"] == _t]
            _mine = [m for m in MEMORIES if (_who and _who[0] in m["who"]) or (_t == MEMORY_NOBODY and not m["who"])]
            if zz_ids(_es) != set(m["id"] for m in _mine) & _S or len(_es) != len(_mine):
                _bad.append(_t)
        check(not _bad, "legacy by person: every group lists its seen entries", _bad)
        check(zz_ids(zz_group(_gp, "Yuji")) == {"ch2_first_years", "st_roll_call", "chapter_four", "ev_yuji_1", "confide:yuji"},
              "legacy by person: Yuji", sorted(zz_ids(zz_group(_gp, "Yuji"))))
        check(zz_ids(zz_group(_gp, "Toge")) == {"ev_panda_1"}, "legacy by person: Toge (in Panda's hangout)",
              sorted(zz_ids(zz_group(_gp, "Toge"))))
        check(zz_ids(zz_group(_gp, "Shoko")) == {"st_aftermath", "ev_shoko_1", "rom_say:shoko", "int_after:shoko"},
              "legacy by person: Shoko (the confession from `together`)", sorted(zz_ids(zz_group(_gp, "Shoko"))))
        check(zz_ids(zz_group(_gp, "Sana")) == {"ch1_diner", "ch1_the_thing"}, "legacy by person: Sana",
              sorted(zz_ids(zz_group(_gp, "Sana"))))
        check(zz_ids(zz_group(_gp, "Utahime")) == set() and len(zz_group(_gp, "Utahime")) == 1,
              "legacy by person: Utahime not met yet, her memory unseen")
        check(zz_ids(zz_group(_gp, MEMORY_NOBODY)) == {"ch1b_goodbye", "st_kurose"},
              "legacy by person: everyone else", sorted(zz_ids(zz_group(_gp, MEMORY_NOBODY))))

        _ga = memory_groups("act")
        check(zz_ids(zz_group(_ga, "Prologue · The Lights")) == set(MEMORY_PROLOGUE_ORDER), "legacy by act: the prologue")
        check(zz_ids(zz_group(_ga, "Act I · Grade Four")) == {"st_roll_call", "chapter_four", "chapter_five", "st_aftermath", "st_kurose"},
              "legacy by act: Act I", sorted(zz_ids(zz_group(_ga, "Act I · Grade Four"))))
        check(zz_ids(zz_group(_ga, "Act II · The Ones Who Stay")) == set(), "legacy by act: nothing in Act II yet")
        check(zz_ids(zz_group(_ga, "Bonds")) == {"ev_yuji_1", "ev_panda_1", "ev_shoko_1", "confide:yuji", "confide:panda",
              "stand:megumi", "rom_town:nobara", "rom_close:maki", "rom_say:shoko", "int_after:shoko"},
              "legacy by act: Bonds", sorted(zz_ids(zz_group(_ga, "Bonds"))))
        check(zz_ids(zz_group(_ga, "Sana")) == set(), "legacy by act: Sana's flashbacks locked")
        _later = set(m["id"] for m in MEMORIES if memory_state(m) == "later")
        check(_later == set(m["id"] for m in MEMORIES if memory_seen(m) and not renpy.has_label(m["label"])),
              "a seen memory whose label isn't in this tree yet reads 'later'", sorted(_later))
        check(memory_counts() == (len(_S) - len(_later), len(MEMORIES)), "memory_counts", memory_counts())
        check(isinstance(memory_replay("st_roll_call"), Replay) and isinstance(memory_replay("confide:yuji"), Replay),
              "memory_replay is a Replay for a seen memory")
        _a = memory_replay("st_roll_call")
        check(_a.label == "mem_play" and _a.locked is False and _a.get_sensitive(), "the Replay is mem_play, locked=False (D5)")
        check(all(isinstance(memory_replay(i), NullAction) for i in _later), "a 'later' memory can't be replayed")
        renpy.show("bg courtyard")
    show screen zz_mem_board("person")
    $ shot("legacy_by_person")
    hide screen zz_mem_board
    show screen zz_mem_board("act")
    $ shot("legacy_by_act")
    hide screen zz_mem_board

    ## --- memory_scope (3.9) --------------------------------------------------------------------
    python:
        _sc = memory_scope("confide:yuji")
        _need = ["mc_name", "mc_surname", "flags", "roster", "bonds", "affection", "together", "threads",
                 "technique", "grade", "control", "output", "insight", "ce", "ce_max", "hp", "hp_max",
                 "stamina", "done_events", "here", "period", "_mem_label", "_mem_args"]
        check(all(k in _sc for k in _need), "memory_scope contains every required key", [k for k in _need if k not in _sc])
        check(_sc["_mem_label"] == "act_confide" and _sc["_mem_args"] == ("yuji",), "memory_scope: label and args", _sc["_mem_label"])
        check(_sc["flags"] == flags and _sc["flags"] is not flags and _sc["bonds"] is not bonds
              and _sc["done_events"] is not done_events and _sc["together"] is not together,
              "memory_scope copies the save's containers")
        _sc["flags"].add("zz_scope_leak")
        _sc["bonds"]["yuji"] = 1
        check(not has_flag("zz_scope_leak") and bonds["yuji"] == 70, "changing the scope doesn't touch the save")
        check(type(_sc["flags"]) is type(flags) and type(_sc["bonds"]) is type(bonds), "the copies keep the store's container types")
        check(memory_scope("st_roll_call")["_mem_args"] == (), "a story memory has no args")

    ## --- the recorder: normal play ----------------------------------------------------------------
    python:
        memories_seen.pop("st_roll_call", None)
        seen_acts.discard("confide:yuji")
        store._in_replay = None
        _mem_label_cb("st_roll_call", False)
        check(memories_seen.get("st_roll_call") == 12, "label callback records st_roll_call with the day", memories_seen.get("st_roll_call"))
        memories_seen.pop("st_roll_call", None)
        store._in_replay = "mem_play"
        _mem_label_cb("st_roll_call", False)
        record_act("confide", "yuji")
        store._in_replay = None
        check("st_roll_call" not in memories_seen and "confide:yuji" not in seen_acts,
              "the recorder and record_act do nothing while _in_replay is set")
        record_act("confide", "yuji")
        record_act("confide", "yuji")
        check("confide:yuji" in seen_acts and len([k for k in seen_acts if k == "confide:yuji"]) == 1,
              "record_act notes the activity once", seen_acts)
        _mem_label_cb("ev_toge_1", False)
        _mem_label_cb("act_confide", False)
        _mem_label_cb("sb_do_wait", False)
        check("ev_toge_1" in memories_seen and "act_confide" not in memories_seen and "sb_do_wait" not in memories_seen,
              "only catalogued labels without args are recorded")
        memories_seen.pop("ev_toge_1", None)
        del ZZ_LABELS[:]
    $ autoplay()
    call st_roll_call
    $ autoplay(False)
    python:
        check(("st_roll_call", False) in ZZ_LABELS, "st_roll_call played in the main context")
        check(memories_seen.get("st_roll_call") == 12, "normal play records st_roll_call (day 12)", memories_seen.get("st_roll_call"))

    ## --- replays: nothing reaches the save, no toasts, not recorded --------------------------------
    python:
        _old_notify = config.notify
        config.notify = lambda m: toast(m)
        TOAST_SINK[0] = zz_toast_sink
        toast("zz sanity")
        check(ZZ_TOASTS == [("zz sanity", "info", None, None)], "the toast recorder works outside a replay", ZZ_TOASTS)
        del ZZ_TOASTS[:]
        memories_seen.pop("st_roll_call", None)
        seen_acts.discard("confide:yuji")
        _bonds_obj, _flags_obj = bonds, flags
        _before = zz_snapshot()
        del ZZ_LABELS[:]
    $ autoplay()
    $ renpy.call_replay("mem_play", memory_scope("st_roll_call"))
    $ autoplay(False)
    python:
        check(("mem_play", True) in ZZ_LABELS and ("st_roll_call", True) in ZZ_LABELS,
              "renpy.call_replay('mem_play') played st_roll_call as a replay", ZZ_LABELS[:6])
        _d = zz_same(_before, zz_snapshot())
        check(not _d, "replaying st_roll_call leaves bonds, flags, day, period (and the rest) unchanged", _d)
        check("st_roll_call" not in memories_seen, "the label callback didn't record inside renpy.call_replay")
        check(not ZZ_TOASTS, "no toasts during the st_roll_call replay", ZZ_TOASTS)
        check(bonds is _bonds_obj and flags is _flags_obj, "the save's own objects are still in place")
        check(not _in_replay, "the replay has ended", _in_replay)
        del ZZ_LABELS[:]
        seen_acts.add("confide:yuji")
        _before = zz_snapshot()
        _act = memory_replay("confide:yuji")
    $ autoplay()
    $ _act()
    $ autoplay(False)
    python:
        check(("act_confide", True) in ZZ_LABELS, "memory_replay('confide:yuji') played act_confide('yuji') as a replay", ZZ_LABELS[:6])
        _d = zz_same(_before, zz_snapshot())
        check(not _d, "replaying act_confide('yuji') leaves bonds, flags, day, period (and the rest) unchanged", _d)
        check(not ZZ_TOASTS, "no toasts during the act_confide replay (it adds bond and insight)", ZZ_TOASTS)
        del ZZ_LABELS[:]
    ## The same action again: it copies the save afresh.
    $ autoplay()
    $ _act()
    $ autoplay(False)
    python:
        check(("act_confide", True) in ZZ_LABELS and not zz_same(_before, zz_snapshot()) and not ZZ_TOASTS,
              "the same tile replays twice, the save unchanged both times")
        del ZZ_LABELS[:]

    ## A screenshot inside a replay: a harness label that shows a line, run as a memory.
    python:
        MEMORY_BY_ID["zz_shot"] = dict(id="zz_shot", title="Shot", who=(), act="I", label="zz_replay_shot",
                                       args=(), seen=[("label", "zz_replay_shot")], hint="h", unlock=None, bg="bg black")
        memories_seen["zz_replay_shot"] = 1
        _before = zz_snapshot()
    $ memory_replay("zz_shot")()
    python:
        del MEMORY_BY_ID["zz_shot"]
        memories_seen.pop("zz_replay_shot", None)
        _before.pop("memories_seen")
        _after = zz_snapshot()
        _after.pop("memories_seen")
        check(ZZ_INSIDE == [(75, True)], "inside the replay the scene gains bond (70 -> 75)", ZZ_INSIDE)
        check(not zz_same(_before, _after) and not ZZ_TOASTS and bonds["yuji"] == 70,
              "a replay that gains bond shows it only inside the replay")

    ## Every memory whose scene is in this tree, replayed once: none raises,
    ## each plays its own label, the save is unchanged and nothing toasts.
    python:
        for _r, _t in (("maki", 60), ("panda", 60), ("toge", 60), ("utahime", 30)):
            if _r not in roster:
                roster.append(_r)
            bonds[_r] = _t
        _sweep = [m["id"] for m in MEMORIES if renpy.has_label(m["label"]) and m["label"] not in ZZ_SWEEP_SKIP]
        _nsweep = len(_sweep)
        _before = zz_snapshot()
        del ZZ_LABELS[:]
        del ZZ_SWEPT[:]
    $ autoplay()
    while _sweep:
        $ _sid = _sweep.pop(0)
        $ renpy.call_replay("mem_play", memory_scope(_sid))
        $ ZZ_SWEPT.append(_sid)
    $ autoplay(False)
    python:
        _played = set(n for n, r in ZZ_LABELS if r)
        _miss = [i for i in ZZ_SWEPT if MEMORY_BY_ID[i]["label"] not in _played]
        check(len(ZZ_SWEPT) == _nsweep and not _miss,
              "sweep: all %d replayable memories replay without an exception" % _nsweep, _miss)
        note("sweep skipped (until WP2 and WP9 merge)", ", ".join(ZZ_SWEEP_SKIP))
        _d = zz_same(_before, zz_snapshot())
        check(not _d, "sweep: the save (memories_seen and seen_acts too) is unchanged after every replay", _d)
        check(not ZZ_TOASTS, "sweep: no toasts in any replay", ZZ_TOASTS[:5])
        config.notify = _old_notify
        TOAST_SINK[0] = None

    ## --- Sana's flashbacks (D11) --------------------------------------------------------------------
    python:
        _sn = dict((e["id"], e) for e in memories_with("sana"))
        check([_sn[i]["text"] for i in ("sana_mem_diner", "sana_mem_daisy", "sana_mem_ranking")]
              == ["A trip home might bring this back.", "Something of hers.", "Someone she ranked first."]
              and all(_sn[i]["state"] == "unseen" for i in ("sana_mem_diner", "sana_mem_daisy", "sana_mem_ranking")),
              "Sana's flashbacks show their hints until triggered", [(_sn[i]["state"], _sn[i]["text"]) for i in _sn])
        store.districts_visited = set(["yotsuka"])
        check(memory_entry("sana_mem_diner")["text"] == "Written in a later build"
              and memory_state("sana_mem_diner") == "later", "The Diner: a trip home triggers it (written later)")
        give_item("daisy_clip", quiet=True)
        check(memory_entry("sana_mem_daisy")["text"] == "Written in a later build", "The Daisy Clip: the keepsake triggers it")
        check(memory_entry("sana_mem_ranking")["state"] == "unseen", "The Teacher Ranking waits for Oda's letter")
        flag("oda_letter_read")
        check(memory_entry("sana_mem_ranking")["text"] == "Written in a later build", "The Teacher Ranking: Oda's letter triggers it")
        check(all(isinstance(memory_replay(i), NullAction) for i in ("sana_mem_diner", "sana_mem_daisy", "sana_mem_ranking")),
              "an unwritten flashback can't be replayed")
        _c = memory_counts()
        note("counts after the fixture", "%d of %d found" % _c)
    show screen zz_mem_board("person")
    $ shot("sana_triggered")
    hide screen zz_mem_board

    ## --- no persistent writes (D6) ---------------------------------------------------------------------
    python:
        import inspect
        _src = inspect.getsource(_mem_label_cb) + inspect.getsource(record_act) + inspect.getsource(memory_seen)
        check("persistent" not in _src, "the recorder and the seen rules never touch persistent")

    $ finish()


## Harness-only: a memory that shows a line and gains bond, for the replay shot.
label zz_replay_shot:
    scene bg rooftop evening
    show yuji happy at pos_c
    $ add_bond("yuji", 5)
    $ ZZ_INSIDE.append((bonds.get("yuji"), bool(_in_replay)))
    $ shot("inside_a_replay", wait=0.4)
    return
