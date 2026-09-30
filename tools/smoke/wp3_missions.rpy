## tools/smoke/wp3_missions.rpy -- WP3's package harness: the mission registry,
## the story chain, the new stub scenes and the event engine changes
## (PHASE1_DESIGN.md 3.6, 3.12, 5.3 and the WP3 acceptance list in section 7).
##
##   SMOKE_SHOTS=shots/wp3 tools/smoke.sh tools/smoke/wp3_missions.rpy
##
## 1. An old-save fixture, migrated twice (m_utahime current, merit 60, arc 1).
## 2. A fresh post-prologue game driven day by day through the whole written
##    story: every period, the story event that fires (played under autoplay),
##    then any start-type mission whose giver is present (start_mission).
##    Statuses are watched at every period; the objective is logged to
##    objectives.txt whenever it changes. Fights go to a stand-in label that
##    answers "down" once for the promotion and "win" otherwise.
## 3. The end state: acts, main_story_complete, Arc Two, the smalltalk and
##    promotion lines, the validator. Screenshots of the new scenes.

init 999 python:
    import builtins
    import os

    ## Fights: a stand-in, so the harness never waits on the combat screen.
    ZZ_COMBATS = builtins.list()
    ZZ_PROMO_PLAN = builtins.list(["down", "win"])
    config.label_overrides["combat"] = "zz_fake_combat"

    ## Ijichi and Utahime get schedules from WP1; until that merges, give the
    ## harness the ones section 3.2 lists, so their missions can be started.
    if "ijichi" not in SCHEDULE:
        SCHEDULE["ijichi"] = {"Morning": "gate", "Noon": "gate", "Afternoon": "gate",
                              "Evening": "-", "Night": "-"}
    if "utahime" not in SCHEDULE:
        SCHEDULE["utahime"] = {"Morning": "office", "Noon": "office", "Afternoon": "office",
                               "Evening": "cafeteria", "Night": "-"}

    ## What the drive saw: mid -> {status: (day, period) first seen}.
    ZZ_SEEN = builtins.dict()
    ZZ_OBJ = builtins.list()          # [(day, period, text, mid)]
    ZZ_OBJ_MIDS = builtins.set()
    ZZ_FLAGS = builtins.dict()        # named one-off observations
    ZZ_CHAIN_BAD = builtins.list()
    ZZ_RETIRED_FIRED = builtins.list()
    ZZ_POPS = builtins.list()

    def zz_story_written():
        return [m for m in STORY_ROWS if m["label"] and renpy.has_label(m["label"])]

    def zz_obj_log(tag=""):
        o = current_objective()
        text = o["text"] if o else "(none)"
        mid = o["mid"] if o else None
        if mid:
            ZZ_OBJ_MIDS.add(mid)
        if not ZZ_OBJ or ZZ_OBJ[-1][2] != text or tag:
            ZZ_OBJ.append((store.day, store.period, text, mid, tag))

    def zz_observe():
        """Statuses of every story row at this (day, period), plus the
        invariants that must hold at every step."""
        for m in MISSIONS:
            s = mission_status(m["id"])
            ZZ_SEEN.setdefault(m["id"], builtins.dict()).setdefault(s, (store.day, store.period))
        for m in STORY_ROWS:
            s = mission_status(m["id"])
            if s not in ("available", "waiting", "active"):
                continue
            ## The chain: every earlier non-optional written row is finished.
            for r in STORY_ROWS:
                if r["order"] >= m["order"]:
                    break
                if r["optional"]:
                    continue
                rs = mission_status(r["id"])
                if rs not in ("done", "skipped", "unwritten"):
                    ZZ_CHAIN_BAD.append("%s %s while %s is %s (day %d)" % (m["id"], s, r["id"], rs, store.day))
        if store.day == 1:
            av = [i for i in missions_list(status="available")]
            if av:
                ZZ_CHAIN_BAD.append("available on day 1: %r" % av)
        ## Retired events never fire, even with their old conditions met.
        for kind, loc in (("story", None), ("mission", "office")):
            for e in find_events(kind, loc=loc):
                if e["label"] in RETIRED_LABELS:
                    ZZ_RETIRED_FIRED.append((store.day, e["label"]))
        zz_obj_log()

    def zz_next_start():
        """(mid, loc): the first start-type mission available now whose giver
        is somewhere on campus at a place it can be given."""
        for m in MISSIONS:
            if m["trigger"] != "start" or mission_status(m["id"]) != "available":
                continue
            giver = m["with_who"] or m["who"]
            loc = char_location(giver)
            if loc and m["id"] in missions_here(loc):
                return (m["id"], loc)
        return None

    def zz_done_day(mid):
        if mid == "m_prologue":
            return store.arc_start_day
        return store.mission_done_day.get(mid)

    def zz_reset():
        """A clean slate for the next fixture."""
        store.flags = set()
        store.done_events = set()
        store.missions_done = set()
        store.mission_done_day = {}
        store.mission_state = {}
        store.mission_retry_day = {}
        store.merit = 0
        store.merit_granted = set()
        store.grade = ZZ_GRADE0[0]
        store.arc = 1
        store.roster = ["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "ijichi"]
        store.bonds = {}
        store.affection = {}
        store.threads = {}
        store.inventory = {}
        store.day = 1
        store.period = "Morning"
        store.here = "courtyard"
        store.save_version = 0
        store.arc_start_day = 1
        store.talked_today = set()
        store.spent_today = set()
        mission_cache_clear()

    ZZ_GRADE0 = builtins.list([None])

    def zz_write_objectives():
        path = os.path.join(zz_smoke_state.shots, "objectives.txt")
        if not os.path.isdir(zz_smoke_state.shots):
            os.makedirs(zz_smoke_state.shots)
        with open(path, "w", encoding="utf-8") as f:
            f.write("# current_objective() at every step of a fresh game (WP3 harness)\n")
            for d, p, text, mid, tag in ZZ_OBJ:
                f.write("Day %2d %-9s %-16s %s%s\n" % (d, p, mid or "-", text, ("   [" + tag + "]") if tag else ""))


label zz_fake_combat(enemy, ally=None, flee_ok=True, bg=None):
    $ ZZ_COMBATS.append(enemy)
    if enemy == "promo_g3" and ZZ_PROMO_PLAN:
        $ _zz_out = ZZ_PROMO_PLAN.pop(0)
    else:
        $ _zz_out = "win"
    return _zz_out


## One day: each period, the story beat that fires, then start missions. A
## scene that rolls the day over (advance_period at Night) ends the day early.
label zz_drive_day:
    $ _zz_pi = 0
    $ _zz_day0 = day
    while _zz_pi < len(PERIODS) and day == _zz_day0:
        $ period = PERIODS[_zz_pi]
        $ here = "courtyard"
        $ zz_observe()
        $ zz_hooks()
        $ _zz_e = pick_event("story", loc=here)
        if _zz_e:
            $ _zz_lab = _zz_e["label"]
            $ autoplay()
            call play_event(_zz_e)
            $ autoplay(False)
            $ zz_obj_log("played " + _zz_lab)
        if day == _zz_day0:
            $ period = PERIODS[_zz_pi]
            $ _zz_s = zz_next_start()
            $ _zz_n = 0
            while _zz_s and day == _zz_day0 and _zz_n < 4:
                $ _zz_n += 1
                $ here = _zz_s[1]
                $ _zz_p0 = period
                $ _zz_d0 = day
                $ autoplay()
                call start_mission(_zz_s[0])
                $ autoplay(False)
                $ zz_after_start(_zz_s[0], _zz_d0, _zz_p0)
                $ zz_obj_log("started " + _zz_s[0])
                if day == _zz_day0:
                    $ period = PERIODS[_zz_pi]
                $ _zz_s = zz_next_start()
            if _zz_n >= 4:
                $ check(False, "start missions settle within a period", (day, period, _zz_s))
        $ _zz_pi += 1
    if day == _zz_day0:
        $ new_day()
    return


init 999 python:

    def zz_hooks():
        """One-off checks at the moment they become possible."""
        st = mission_status
        ## m_sunmall is offered in the office only while Yaga is there.
        if st("m_sunmall") == "available" and "sunmall_here" not in ZZ_FLAGS:
            ZZ_FLAGS["sunmall_here"] = True
            p0, ok, seen = store.period, True, set()
            for p in PERIODS:
                store.period = p
                yaga_in = "yaga" in who_is_here("office")
                shown = "m_sunmall" in missions_here("office")
                seen.add(yaga_in)
                if yaga_in != shown:
                    ok = False
            store.period = p0
            check(ok and seen == {True, False},
                  "m_sunmall shows in missions_here(\"office\") only while Yaga is there", seen)
            mk = mission_markers()
            check(any(t == "Yaga · The Sun Mall" for t, k in mk.get("office", [])),
                  "mission_markers: \"Yaga · The Sun Mall\" at the office", mk)
            check("m_sunmall" in missions_with("yaga") and "m_sunmall" not in missions_with("yuji"),
                  "missions_with(\"yaga\") offers the Sun Mall")
        ## The promotion: locked on merit, then open at 60.
        if st("m_intensive") == "done" and "promo_merit" not in ZZ_FLAGS:
            ZZ_FLAGS["promo_merit"] = True
            note("merit when Gojo's lesson is done", store.merit)
            store.merit = 50
            check(st("m_promo_g3") == "locked" and mission_reason("m_promo_g3") == "Merit 50/60",
                  "m_promo_g3 locked with \"Merit 50/60\" at merit 50",
                  (st("m_promo_g3"), mission_reason("m_promo_g3")))
            check(objective_text() == "Earn merit on Utahime's board: 50/60 — then the promotion fight",
                  "objective at merit 50 points at the board", objective_text())
            zz_obj_log("merit set to 50")
            store.merit = 60
            check(st("m_promo_g3") in ("available", "waiting"), "m_promo_g3 unlocks at merit 60",
                  (st("m_promo_g3"), mission_reason("m_promo_g3")))
            zz_obj_log("merit set to 60")
        if st("m_promo_g3") == "available" and "promo_avail" not in ZZ_FLAGS:
            ZZ_FLAGS["promo_avail"] = (store.day, store.merit)
            check(store.merit >= 60, "m_promo_g3 available at merit 60", store.merit)
        ## The second-years are in: make Maki's armory mission reachable.
        if has_flag("met_second_years") and store.bonds.get("maki", 0) < 10:
            store.bonds["maki"] = 10
        ## Retry: the day after a failed promotion it is available again.
        if "promo_failed" in ZZ_FLAGS and "promo_retry" not in ZZ_FLAGS \
                and store.day > ZZ_FLAGS["promo_failed"]:
            ZZ_FLAGS["promo_retry"] = True
            check(st("m_promo_g3") == "available", "after mission_fail, m_promo_g3 is available the next day",
                  (st("m_promo_g3"), mission_reason("m_promo_g3")))

    def zz_after_start(mid, d0, p0):
        st = mission_status
        if mid == "m_promo_g3" and "promo_failed" not in ZZ_FLAGS:
            ZZ_FLAGS["promo_failed"] = store.day
            check(st(mid) == "waiting" and mission_reason(mid) == "Try again tomorrow",
                  "mission_fail makes m_promo_g3 waiting until the next day", (st(mid), mission_reason(mid)))
            check(store.mission_retry_day.get(mid) == store.day + 1, "mission_fail sets the retry day",
                  store.mission_retry_day)
            check(objective_text().endswith("— try again tomorrow"), "objective after a failed promotion",
                  objective_text())
            check(mid not in store.missions_done and store.grade != "g3", "a lost fight is no promotion")
        elif mid == "m_promo_g3":
            check(st(mid) == "done" and store.grade == "g3", "winning the promotion fight: Grade 3, done",
                  (st(mid), store.grade))
        elif mid == "cm_ijichi_1":
            elapsed = (store.day - d0) * len(PERIODS) + PERIODS.index(store.period) - PERIODS.index(p0)
            check(st(mid) == "done" and has_flag("ijichi_rides"), "Ride-Along: done, ijichi_rides set")
            check(elapsed == 2, "Ride-Along costs 2 periods", (d0, p0, store.day, store.period))
            check(store.here == "gate", "Ride-Along ends at the gate", store.here)
        elif mid == "cm_maki_1":
            check(st(mid) == "done" and has_flag("armory_open"), "The Armory: done, armory_open set")
            check(item_count("slaughter_demon") == 1, "The Armory: the Slaughter Demon, once", store.inventory)
        else:
            check(st(mid) == "done", "start_mission completes " + mid, st(mid))


label zz_smoke:

    $ ZZ_GRADE0[0] = grade
    $ fixture(mc_name="Tester", mc_surname="Harness")

    ## --- 0. the event engine and the registry --------------------------------------------
    python:
        check(not any(getattr(f, "__name__", "") == "_calendar_gate" for f in EVENT_GATES)
              and not hasattr(store, "_calendar_gate"), "WP0's transitional _calendar_gate is gone")
        _bad = [e["label"] for e in EVENTS if e["kind"] in ("story", "mission")
                and e["label"] not in MISSION_BY_LABEL and e["label"] not in RETIRED_LABELS]
        check(not _bad, "every story/mission ev() is bound to a mission or retired", _bad)
        _v = _validate_missions()
        check(_v == [], "the WP3 validator finds nothing", _v)
        check(len(MISSION_BY_ID) == len(MISSIONS), "mission ids are unique")
        check(len(set(m["order"] for m in MISSIONS)) == len(MISSIONS), "mission orders are unique")
        _w = zz_story_written()
        check(all(m["objective"] for m in _w if m["id"] != "m_prologue"), "every written story step has an objective")
        _unw = [m["id"] for m in STORY_ROWS if not m["label"]]
        check(len(_unw) >= 18, "the unwritten storyboard beats have rows", len(_unw))
        check(mission_status("m_nope") == "locked" and mission_reason("m_nope") == "", "an unknown id is locked")
        complete_mission("m_nope")
        mission_fail("m_nope")
        check([a[0] for a in ACTS] == ["P", "I", "II", "III", "IV", "V"], "ACTS")
        check([c["who"] for c in JOURNAL_CAST] == ["yuji", "megumi", "nobara", "maki", "panda", "toge", "gojo",
              "utahime", "shoko", "yaga", "ijichi", "nanami", "todo", "miwa", "mei_mei", "yuta", "sana"],
              "JOURNAL_CAST order")
        check(all(c.get("hint") for c in JOURNAL_CAST if c["who"] != "sana"), "JOURNAL_CAST: every card has a hint")
        check(len(SMALLTALK.get("utahime", [])) == 4 and len(SMALLTALK.get("ijichi", [])) == 4,
              "SMALLTALK: 4 lines each for Utahime and Ijichi")
        check(set(PROMO_LINES) >= {"yuji", "megumi", "nobara", "maki", "panda", "toge"}, "PROMO_LINES: one per student")
        check(all(m["kind"] == "character" and m["label"] == m["id"] for m in MISSIONS if m["id"].startswith("cm_")),
              "character missions are labelled cm_<who>_<n>")
        check(all(renpy.has_label(l) for l in ("cm_ijichi_1", "cm_maki_1", "st_utahime_office", "st_promotion_g3")),
              "the four new scenes exist")

    ## --- 1. an old save ---------------------------------------------------------------------
    python:
        zz_reset()
        done_events = {"st_roll_call", "st_board_open", "st_second_years", "ev_mission_sunmall", "st_aftermath"}
        flags = {"settled_in", "roll_call", "storehouse_access", "mission_board_open", "met_second_years",
                 "sunmall_done", "arc1_complete"}
        grade = "g3"
        setattr(store, "arc", 2)
        day = 12
        roster = ["yuji", "megumi", "nobara", "shoko", "gojo", "yaga", "maki", "panda", "toge"]
        _up = run_migrations()
        check(_up, "old save: migrations upgrade it")
        _o = current_objective()
        check(_o and _o["mid"] == "m_utahime", "old save: m_utahime is the current step", _o)
        check(mission_status("m_utahime") == "available", "old save: m_utahime available now", mission_reason("m_utahime"))
        check(mission_status("m_promo_g3") == "done", "old save: m_promo_g3 is done (grade g3)")
        check(merit == 60, "old save: merit backfilled to 5 + 30 + 5 + 20 = 60", merit)
        check(arc == 1, "old save: arc 2 -> 1", arc)
        check("ijichi" in roster, "migration 40: Ijichi on the roster", roster)
        check(has_flag("night_before_done"), "migration 40: arc1_complete -> night_before_done")
        check(all(mission_done_day.get(m) == 0 for m in ("m_roll_call", "m_sunmall", "m_aftermath", "m_second_years")),
              "migration 65: done rows get day 0", mission_done_day)
        _snap = (merit, set(merit_granted), dict(mission_done_day), arc, list(roster))
        run_migrations()
        run_migrations(block=False)
        check((merit, set(merit_granted), dict(mission_done_day), arc, list(roster)) == _snap,
              "old save: a second migration run adds nothing", (merit, _snap[0]))
        ## A save the new ch5 already paid (recommended_g3) gets no second 20.
        zz_reset()
        flags = {"settled_in", "sunmall_done", "recommended_g3"}
        done_events = {"st_roll_call", "st_utahime_office", "ev_mission_sunmall"}
        merit = 20
        run_migrations()
        check(merit == 20 + 5 + 30, "migration 60: no second ch5 payment after recommended_g3", merit)
        ## Utahime met in an old save stays on the roster.
        zz_reset()
        flags = {"settled_in", "utahime_arrived"}
        run_migrations()
        check("utahime" in roster, "migration 40: utahime_arrived puts her on the roster", roster)
        ## Arc Two, once begun, is kept.
        zz_reset()
        flags = {"settled_in", "arc2_started"}
        setattr(store, "arc", 2)
        run_migrations()
        check(arc == 2, "migration 50 keeps a begun Arc Two", arc)

    ## --- 2. a fresh game, day by day ----------------------------------------------------------
    python:
        zz_reset()
        settle(day=1, arc_start_day=1)
        check(has_flag("settled_in") and day == 1 and arc_start_day == 1, "fresh post-prologue state")
        check(mission_status("m_prologue") == "done", "the prologue step is done")
        check(missions_list(status="available") == [], "nothing is available on day 1", missions_list(status="available"))
        check(mission_status("m_roll_call") == "waiting" and mission_reason("m_roll_call") == "Tomorrow",
              "day 1: roll call waits for tomorrow", (mission_status("m_roll_call"), mission_reason("m_roll_call")))
        _found = []
        for _p in PERIODS:
            period = _p
            if pick_event("story"):
                _found.append(_p)
        period = "Morning"
        check(_found == [], "no story event fires on day 1", _found)
        check(all(mission_status(m["id"]) == "locked" for m in zz_story_written()
                  if m["order"] > 110), "day 1: every later written step is locked")
        check(objective_text() == "Roll call with Principal Yaga — tomorrow morning, wherever I am",
              "day 1 objective", objective_text())
        zz_obj_log("day 1")

    call zz_drive_day
    python:
        check(day == 2 and not (done_events - {"zz_none"}), "day 1 passes with no story event", sorted(done_events))
    call zz_drive_day
    python:
        check(ZZ_SEEN.get("m_roll_call", {}).get("available", (0,))[0] == 2, "on day 2, m_roll_call is available",
              ZZ_SEEN.get("m_roll_call"))
        _roll_day = mission_done_day.get("m_roll_call")
        check(_roll_day == 2, "roll call is played on day 2", _roll_day)
        check(merit >= 5, "roll call pays merit 5", merit)

    $ _zz_days = 0
    while not mission_status("m_night_before") == "done" and _zz_days < 45:
        call zz_drive_day
        $ _zz_days += 1
    python:
        _w = zz_story_written()
        _nonopt = [m for m in _w if not m["optional"]]
        check(all(mission_status(m["id"]) == "done" for m in _nonopt), "the whole written story plays through",
              [(m["id"], mission_status(m["id"]), mission_reason(m["id"])) for m in _nonopt if mission_status(m["id"]) != "done"])
        note("days to finish the written story", day)
        ## Order and gaps.
        _days = [(m["id"], zz_done_day(m["id"])) for m in _nonopt]
        note("done days", _days)
        check(all(d is not None for _, d in _days), "every step recorded a done day")
        _order_ok = all(_days[i][1] <= _days[i + 1][1] for i in range(len(_days) - 1))
        check(_order_ok, "steps finish in table order", _days)
        _gap_bad, _seq_bad, _late = [], [], []
        for _i in range(1, len(_nonopt)):
            _m, _prev = _nonopt[_i], _nonopt[_i - 1]
            _need = zz_done_day(_prev["id"]) + _m["gate"]["gap_days"]
            _seen = ZZ_SEEN.get(_m["id"], {})
            _av = _seen.get("available", (None,))[0]
            if _av is None or _av < _need or zz_done_day(_m["id"]) < _need:
                _gap_bad.append((_m["id"], _need, _av, zz_done_day(_m["id"])))
            ## Only the merit-gated promotion may open later than its gap.
            if _av is not None and _av != _need and _m["id"] != "m_promo_g3":
                _late.append((_m["id"], _need, _av))
            ## locked (or waiting) first, then available, then done.
            _first = min([_seen[s] for s in ("locked", "waiting") if s in _seen] or [(999, "")])
            if not (_first[0] <= (_av or 999) <= zz_done_day(_m["id"])):
                _seq_bad.append((_m["id"], _seen))
            if _m["gate"]["gap_days"] >= 1 and _need - 1 >= 2:
                if "waiting" not in _seen:
                    _seq_bad.append((_m["id"], "never seen waiting"))
        check(not _gap_bad, "each gap is respected", _gap_bad)
        check(not _late, "each step opens on the day its gap ends", _late)
        check(not _seq_bad, "steps go locked -> available/waiting -> done", _seq_bad)
        check(not ZZ_CHAIN_BAD, "no step is ever open ahead of an unfinished earlier one", ZZ_CHAIN_BAD[:5])
        ## Unwritten rows never block.
        _unw = [m["id"] for m in STORY_ROWS if mission_status(m["id"]) in ("unwritten", "skipped")]
        check("m_detention" in _unw and "m_infirmary" in _unw and mission_status("m_second_years") == "done",
              "no unwritten row ever blocks (Act II follows Act I's unwritten beats)", _unw)
        _sd = ZZ_SEEN.get("m_detention", {})
        check("unwritten" in _sd and "skipped" in _sd and _sd["unwritten"] < _sd["skipped"],
              "D20: an unwritten beat is skipped once the save is past it", _sd)
        check(mission_status("m_kyoto_arrives") == "unwritten", "a beat nobody is past stays unwritten")
        check(not ZZ_RETIRED_FIRED, "st_board_open and ev_patrol never fire", ZZ_RETIRED_FIRED[:3])
        _missing = [m["id"] for m in _nonopt if m["id"] != "m_prologue" and m["id"] not in ZZ_OBJ_MIDS]
        check(not _missing, "every written step was the objective at some point", _missing)
        check("sunmall_here" in ZZ_FLAGS and "promo_merit" in ZZ_FLAGS and "promo_failed" in ZZ_FLAGS
              and "promo_retry" in ZZ_FLAGS, "the Sun Mall, merit and retry checks all ran", sorted(ZZ_FLAGS))
        check(ZZ_COMBATS.count("promo_g3") == 2, "the promotion fight was fought twice (lost, then won)", ZZ_COMBATS)
        check(mission_status("cm_ijichi_1") == "done" and mission_status("cm_maki_1") == "done",
              "both written character missions were played")
        check("utahime" in roster and has_flag("mission_board_open") and has_flag("utahime_arrived"),
              "Utahime's scene recruits her and opens the board")
        check(item_count("paper_ward") == 1 and item_count("sealing_talisman") == 2,
              "Utahime's rewards: a Paper Ward and two sealing talismans", inventory)
        ## Paid once.
        _m0 = merit
        complete_mission("m_roll_call")
        complete_mission("m_sunmall")
        check(merit == _m0, "complete_mission pays only once", (merit, _m0))
        ## Acts.
        check(act_done("I") and act_done("II") and act_done("III") and act_done("IV") and not act_done("V"),
              "act_done: I-IV done, V has nothing written", [act_done(a) for a in ("I", "II", "III", "IV", "V")])
        check(acts_done() == 4, "acts_done() == 4", acts_done())
        check(act_progress("I") == (5, 5, 8), "act_progress(\"I\") == (5, 5, 8)", act_progress("I"))
        check(main_story_complete() is False, "main_story_complete() is False")
        _o = objective_text()
        check(_o == "The story continues in a later build. The board and everyone on campus are open.",
              "the objective once only unwritten steps remain", _o)
        zz_obj_log("end of the written story")
        ## Markers and next_for.
        check(isinstance(mission_markers(), dict), "mission_markers() is a dict")
        _nf = next_for("yuji")
        check(isinstance(_nf, tuple) and len(_nf) == 2 and _nf[0], "next_for(\"yuji\") is (text, where)", _nf)
        check(next_for("nanami") is None, "next_for someone not met is None")

    ## --- 3. Arc Two -------------------------------------------------------------------------------
    ## Not complete: arc_two_start returns without its menu (with autoplay off,
    ## a menu here would stall the harness).
    call arc_two_start
    python:
        check(not has_flag("arc2_started"), "arc_two_start does nothing before the main story is complete")
        _hang_before = has_event("hangout", "yuji")
        begin_arc_two()
        _open = [m["id"] for m in MISSIONS if m["kind"] == "character" and mission_status(m["id"]) not in ("done", "closed")]
        check(not _open, "begin_arc_two() closes every unfinished character mission", _open)
        check(mission_status("cm_ijichi_1") == "done" and mission_status("cm_maki_1") == "done",
              "begin_arc_two() leaves finished ones done")
        check(has_flag("arc2_started") and arc == 2, "begin_arc_two() sets arc2_started and arc 2")
        check(_hang_before and not has_event("hangout", "yuji"),
              "after Arc Two begins, arc-1 hangouts with unfinished threads stop", _hang_before)
        run_migrations()
        check(arc == 2, "migration 50 keeps Arc Two after begin_arc_two()")

    ## --- 4. talk: the promotion remark --------------------------------------------------------------
    python:
        _real_pop = pop_remark
        def pop_remark(who):
            ZZ_POPS.append(who)
            return True
        _l = promo_line("nobara")
        check(_l is not None and _l.startswith(grade_label(npc_stats("nobara")["grade"]) + "."),
              "promo_line(\"nobara\") names her grade", _l)
        check(promo_line("shoko") is None and "shoko" not in ZZ_POPS, "no promotion line (or pop) for non-students")
        talked_today = set()
    $ autoplay()
    call sb_smalltalk("megumi")
    call sb_smalltalk("megumi")
    $ autoplay(False)
    python:
        check(ZZ_POPS.count("megumi") == 1 and "megumi" in talked_today, "sb_smalltalk speaks the remark once",
              ZZ_POPS)
        pop_remark = _real_pop

    ## --- 5. screenshots of the new scenes -----------------------------------------------------------
    scene bg utahime_office
    show utahime serious at pos_c
    $ renpy.say(utahime, "Three. You always take someone. I don't care how easy the file looks.", interact=False)
    $ shot("scene_utahime", wait=0.6)
    scene bg training
    show maki serious at pos_c
    $ renpy.say(maki, "Beat it and you're Grade 3. Don't, and you come back tomorrow. Nobody writes anything bad down either way.", interact=False)
    $ shot("scene_promotion", wait=0.6)
    scene bg town_street
    show ijichi serious at pos_c
    $ renpy.say(ijichi, "Please stand behind me. It isn't dangerous. It's just rude to stand in front.", interact=False)
    $ shot("scene_ride_along", wait=0.6)
    scene bg storehouse
    show maki happy at pos_c
    $ renpy.say(maki, "It was my first one too. Try not to lose it inside something.", interact=False)
    $ shot("scene_armory", wait=0.6)
    scene black

    $ zz_write_objectives()
    $ check(True, "objectives written to objectives.txt", len(ZZ_OBJ))
    $ finish()
