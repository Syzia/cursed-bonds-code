################################################################################
## Cursed Bonds — the mission registry: the story chain, character missions,
## the objective, and Arc Two.
##
## WP3 owns this file (PHASE1_DESIGN.md 3.6). Every mission is one record,
## made by mission() at init and never changed; ids stay stable for ever.
##
## Status is computed from the save's state (never stored), cached for one
## interaction (D22). The queries below return mission ids (strings); look a
## record up with MISSION_BY_ID[mid] for its title, objective and so on.
##
## How the pieces meet the rest of the game:
##   - story beats are still ev() registrations in the chapter files. The
##     event gate below lets an ev() whose label is a mission's label fire
##     only while that mission is "available" (MISSION_BY_LABEL), and never
##     for RETIRED_LABELS;
##   - when play_event finishes such an event, the done hook completes the
##     mission (records the day, pays the rewards once);
##   - start-type missions (a gold button) run through label start_mission.
################################################################################

init -1 python:
    import builtins

    ## Acts: (id, title, kanji, grade band) --------------------------------------

    ACTS = [
        ("P",   "Prologue · The Lights",   "序", "No grade"),
        ("I",   "Grade Four",              "一", "Grade 4"),
        ("II",  "The Ones Who Stay",       "二", "Grade 4 → Grade 3"),
        ("III", "Overtime",                "三", "Grade 3 → Grade 2"),
        ("IV",  "Goodwill",                "四", "Grade 2"),
        ("V",   "Cursed Womb",             "五", "Grade 2 → Grade 1 candidate"),
    ]
    ACT_IDS = [a[0] for a in ACTS]
    ## No ACT_BY_ID here: that name is WP7's activity table (sb_activities.rpy).

    ## Who the journal's People tab shows, in order (3.6.2). name / color /
    ## role only for those without a CAST entry; met is ("roster",),
    ## ("flag", name) or ("always",); hint is the line an unmet card shows.
    JOURNAL_CAST = [
        dict(who="yuji",    met=("roster",), hint="A first-year. I'll hear him before I see him."),
        dict(who="megumi",  met=("roster",), hint="A first-year. One word when four would do."),
        dict(who="nobara",  met=("roster",), hint="A first-year from the countryside. Proud of it."),
        dict(who="maki",    met=("roster",), hint="A second-year. She trains at dawn."),
        dict(who="panda",   met=("roster",), hint="A second-year. Yes, really."),
        dict(who="toge",    met=("roster",), hint="A second-year who speaks in rice-ball fillings."),
        dict(who="gojo",    met=("roster",), hint="The strongest. Hard to pin down."),
        dict(who="utahime", met=("roster",), hint="Someone is clearing the room next to Yaga's."),
        dict(who="shoko",   met=("roster",), hint="The school doctor. The infirmary, most hours."),
        dict(who="yaga",    met=("roster",), hint="The principal. His office, most mornings."),
        dict(who="ijichi",  met=("roster",), hint="The driver. He waits at the gate."),
        dict(who="nanami",  met=("flag", "met_nanami"), name="Kento Nanami", color="#e8d27a",
             role="Grade 1 sorcerer", hint="A Grade 1 who hates overtime. Act III."),
        dict(who="todo",    met=("flag", "met_todo"), name="Aoi Todo", color="#d89a6a",
             role="Kyoto third-year", hint="Kyoto's loudest third-year. Act IV."),
        dict(who="miwa",    met=("flag", "met_miwa"), name="Kasumi Miwa", color="#8ab8e8",
             role="Kyoto second-year", hint="A Kyoto second-year. Act IV."),
        dict(who="mei_mei", met=("flag", "met_mei_mei"), name="Mei Mei", color="#c8b0e0",
             role="Grade 1 sorcerer", hint="Does nothing for free. Act V."),
        dict(who="yuta",    met=("flag", "met_yuta"), name="Yuta Okkotsu", color="#b8c8d8",
             role="Special grade", hint="A voice on Gojo's phone. Act V."),
        dict(who="sana",    met=("always",), hint=""),
    ]
    JOURNAL_CAST_BY_WHO = {c["who"]: c for c in JOURNAL_CAST}

    ## The record ------------------------------------------------------------------

    MISSIONS = []

    MISSION_KINDS = ("story", "character", "promotion")
    MISSION_TRIGGERS = ("auto", "start")
    MISSION_STATUSES = ("done", "skipped", "closed", "unwritten", "active",
                        "waiting", "available", "locked")

    _MS_GATE_DEFAULTS = dict(after=None, gap_days=0, flags=(), not_flags=(), min_bond=0,
                             min_grade=None, merit=0, thread=None, gojo_in=False, act_done=None)
    _MS_REWARD_DEFAULTS = dict(merit=0, bond={}, yen=0, items={}, flags=())

    def mission(id, kind, act, order, title, summary, objective,
                label=None, trigger="auto", where=None, with_who=None, who=None,
                periods=None, cost=0, gate=None, done_if=(), skip_if=(),
                optional=False, group=None, rewards=None, hidden_until_met=False):
        """WP3. Registers one mission record (3.6). Called at init only.

        gate and rewards are dicts; keys left out take their defaults
        (_MS_GATE_DEFAULTS / _MS_REWARD_DEFAULTS). A label that is None or
        doesn't exist makes the mission "unwritten"."""
        g = dict(_MS_GATE_DEFAULTS)
        g.update(gate or {})
        r = dict(_MS_REWARD_DEFAULTS)
        r.update(rewards or {})
        m = dict(id=id, kind=kind, act=act, order=order, title=title, summary=summary,
                 objective=objective, label=label, trigger=trigger, where=where,
                 with_who=with_who, who=who,
                 periods=(tuple(periods) if periods else None), cost=cost,
                 gate=g, done_if=tuple(done_if), skip_if=tuple(skip_if),
                 optional=optional, group=group, rewards=r,
                 hidden_until_met=hidden_until_met)
        MISSIONS.append(m)
        return m

    _M3 = ("Morning", "Noon", "Afternoon")

    ## 3.6.1 The main story -------------------------------------------------------
    ## Orders are spaced by 10 so phase 3 can insert beats. Unwritten rows have no
    ## label yet: they never block, and never complete an act (D20).

    mission("m_prologue", "story", "P", 0, "The Prologue",
            "The alley, the offer, the tour, the first night.", "",
            label="arc_one_open", done_if=("flag:settled_in",))

    ## skip_if (D20): a beat written in a later phase is skipped by a save that
    ## is already past the next written step, so it never turns up behind the
    ## player as a stale objective. Only event: and flag: clauses here (a
    ## mission: clause on a later row would make the chain recurse).
    _PAST_ACT_I = ("event:st_second_years", "flag:met_second_years")

    ## Act I · Grade Four
    mission("m_roll_call", "story", "I", 110, "Roll Call",
            "Yaga lines up the first-years and gives me a grade.",
            "Roll call with Principal Yaga",
            label="st_roll_call", periods=("Morning",), gate=dict(gap_days=1),
            done_if=("event:st_roll_call", "flag:roll_call"), rewards=dict(merit=5))
    mission("m_utahime", "story", "I", 120, "The Room Next Door",
            "Kyoto's teacher arrives early, and opens a board of graded jobs.",
            "Someone is moving into the room next to Yaga's",
            label="st_utahime_office", periods=_M3, gate=dict(gap_days=1),
            done_if=("event:st_utahime_office", "flag:utahime_arrived"),
            rewards=dict(items={"paper_ward": 1, "sealing_talisman": 2}))
    mission("m_sunmall", "story", "I", 130, "The Sun Mall",
            "Four storeys of dead escalators in Saitama, and three people missing.",
            "Yaga has a mission for the first-years",
            label="ev_mission_sunmall", trigger="start", where="office", with_who="yaga",
            gate=dict(gap_days=1), done_if=("event:ev_mission_sunmall", "flag:sunmall_done"),
            rewards=dict(merit=30))
    mission("m_aftermath", "story", "I", 140, "The Morning After",
            "Shoko on cursed-energy debt, the morning after the Sun Mall.",
            "Shoko wants to look at all four of us",
            label="st_aftermath", periods=("Morning",), gate=dict(gap_days=1),
            done_if=("event:st_aftermath", "flag:aftermath_done"), rewards=dict(merit=5))
    mission("m_kurose", "story", "I", 150, "The Cover Story",
            "A man from auxiliary management explains what the world was told about Sana.",
            "A man from auxiliary management wants a word",
            label="st_kurose", periods=("Afternoon", "Evening"), gate=dict(gap_days=0),
            done_if=("event:st_kurose", "flag:kurose_met"))
    mission("m_detention", "story", "I", 160, "The Detention Center",
            "Filed as Grade 3. It isn't.", "The detention center", skip_if=_PAST_ACT_I)
    mission("m_aftermath_2", "story", "I", 170, "Aftermath",
            "Megumi goes quiet, Nobara goes to the roof, Gojo goes cold.", "Aftermath",
            skip_if=_PAST_ACT_I)
    mission("m_infirmary", "story", "I", 180, "The Infirmary",
            "One last look at Yuji.", "The infirmary", skip_if=_PAST_ACT_I)

    ## Act II · The Ones Who Stay
    mission("m_second_years", "story", "II", 210, "The Second-Years",
            "Maki, Panda and Toge, back from wherever they were.",
            "The second-years are back from wherever they were",
            label="st_second_years", periods=("Afternoon",), gate=dict(gap_days=1),
            done_if=("event:st_second_years", "flag:met_second_years"))
    mission("m_noise", "story", "II", 220, "The Courtyard Curse",
            "Something on campus, after dark.", "Something is wrong on campus after dark",
            label="st_noise", periods=("Evening",), gate=dict(gap_days=1),
            done_if=("event:st_noise",), rewards=dict(merit=10))
    mission("m_oda_letter", "story", "II", 230, "A Letter from Home",
            "Oda-sensei writes.", "A letter is on its way from home",
            label="st_oda_letter", periods=("Evening",), gate=dict(gap_days=1),
            done_if=("event:st_oda_letter", "flag:oda_letter_read"))
    mission("m_intensive", "story", "II", 240, "Gojo's First Lesson",
            "Gojo's first lesson.", "Gojo wants eleven minutes of my time",
            label="st_intensive", periods=("Afternoon",), gate=dict(gap_days=2),
            done_if=("event:st_intensive", "flag:intensive_done"))
    mission("m_strongest", "story", "II", 250, "The Strongest",
            "Gojo takes me on an errand, and something attacks.", "\"The Strongest\"",
            skip_if=("flag:nade_named",))
    mission("m_secret", "story", "II", 260, "The Secret",
            "Only three people know.", "The secret", skip_if=("flag:nade_named",))
    mission("m_promo_g3", "promotion", "II", 270, "Promotion: Grade 3",
            "A graded fight in the training hall, with Maki watching.",
            "Promotion fight: find Maki (Dojo mornings, Training Hall afternoons)",
            label="st_promotion_g3", trigger="start", where=("training", "dojo"), with_who="maki",
            gate=dict(gap_days=1, merit=60), done_if=("grade:g3",))

    ## Act III · Overtime
    mission("m_nanami", "story", "III", 310, "Nanami",
            "A Grade 1 who hates overtime becomes my supervisor.", "Nanami",
            skip_if=("flag:nade_named",))
    mission("m_nade_1", "story", "III", 320, "The Warehouse",
            "A registered Grade 4 in Kawaguchi. It isn't.", "Yaga has a name",
            label="ms_nade_1", trigger="start", where="office", with_who="yaga",
            gate=dict(gap_days=1), group="The Surveyor",
            done_if=("event:ms_nade_1", "flag:nade_named"), rewards=dict(merit=25))
    mission("m_kurose_2", "story", "III", 330, "The Photocopy",
            "Something from Kurose, left in my room.",
            "Something from Kurose is waiting in my room",
            label="st_kurose_2", periods=("Evening",), gate=dict(gap_days=1),
            done_if=("event:st_kurose_2", "flag:kurose_leak"))
    mission("m_cinema", "story", "III", 340, "The Cinema",
            "Deaths in Kawasaki, bodies twisted into shapes.", "The cinema",
            skip_if=("flag:nade_traced",))
    mission("m_junpei", "story", "III", 350, "Junpei",
            "A boy at the cinema.", "Junpei", skip_if=("flag:nade_traced",))
    mission("m_nade_2", "story", "III", 360, "The Annexe",
            "The Saitama annexe, and whoever signed the forms.",
            "Yaga wants the annexe looked at",
            label="ms_nade_2", trigger="start", where="office", with_who="yaga",
            gate=dict(gap_days=2), group="The Surveyor",
            done_if=("event:ms_nade_2", "flag:nade_traced"), rewards=dict(merit=25))
    mission("m_oda_2", "story", "III", 370, "Oda-sensei Writes Back",
            "A second letter from home.", "Oda-sensei writes back",
            label="st_oda_2", periods=("Evening",), optional=True,
            gate=dict(gap_days=1, flags=("oda_answered",)),
            done_if=("event:st_oda_2", "flag:oda_thread_open"))
    mission("m_nade_3", "story", "III", 380, "The Map",
            "Yaga knows where Nade is.", "Yaga knows where Nade is",
            label="ms_nade_3", trigger="start", where="office", with_who="yaga",
            gate=dict(gap_days=2), group="The Surveyor",
            done_if=("event:ms_nade_3", "flag:nade_map"), rewards=dict(merit=30))
    mission("m_satozakura", "story", "III", 390, "Satozakura High",
            "Junpei's school.", "Satozakura High", skip_if=("event:st_roster",))
    mission("m_promo_g2", "promotion", "III", 395, "Promotion: Grade 2",
            "Grade 2, on a Grade 1's word.", "Grade 2, on a Grade 1's word",
            done_if=("grade:g2",))

    ## Act IV · Goodwill
    mission("m_roster", "story", "IV", 410, "The Roster",
            "The Goodwill Event is announced, and the roster goes up.",
            "The Kyoto roster is going up",
            label="st_roster", periods=("Noon",), gate=dict(gap_days=1),
            done_if=("event:st_roster",))
    mission("m_night_before", "story", "IV", 420, "The Night Before",
            "The night before Kyoto.", "The night before Kyoto",
            label="st_night_before", periods=("Evening", "Night"), gate=dict(gap_days=2),
            done_if=("event:st_night_before", "flag:arc1_complete", "flag:night_before_done"))
    mission("m_kyoto_arrives", "story", "IV", 430, "Kyoto Arrives",
            "Utahime leads the other side.", "Kyoto arrives")
    mission("m_team_battle", "story", "IV", 440, "The Team Battle",
            "Day one, in the forest.", "The team battle")
    mission("m_attack", "story", "IV", 450, "The Attack",
            "A veil drops over the event.", "The attack")
    mission("m_baseball", "story", "IV", 460, "Baseball",
            "Day two.", "Baseball")
    mission("m_new_faces", "story", "IV", 470, "New Faces",
            "Todo and Miwa.", "New faces")

    ## Act V · Cursed Womb
    mission("m_yasohachi", "story", "V", 510, "Yasohachi Bridge",
            "Eso and Kechizu.", "Yasohachi Bridge")
    mission("m_meimei", "story", "V", 520, "Mei Mei",
            "A Grade 1 who does nothing for free.", "Mei Mei")
    mission("m_recommended", "story", "V", 530, "The Recommendation",
            "Two Grade 1s put my name forward.", "The recommendation")
    mission("m_yuta_call", "story", "V", 540, "Yuta's Call",
            "A voice on Gojo's phone.", "Yuta's call")
    mission("m_sketchbook", "story", "V", 550, "The Sketchbook",
            "Why Sana could see them.", "The sketchbook")

    ## 3.6.2 Character missions ---------------------------------------------------
    ## Label and id cm_<who>_<n>; trigger "start" with `who`; `where` None means
    ## wherever they are. Unwritten until the label exists.
    ## (who, [(title, summary, gate, act)])

    _CM_TABLE = [
        ("yuji", [
            ("Grandpa's Last Words", "What his grandfather told him, the night he died.",
             dict(min_bond=30, thread=("yuji_countdown", 1)), "I"),
            ("The Basement", "Secret training, after his \"death\".",
             dict(flags=("yuji_secret",)), "II"),
            ("A Finger Retrieval", "One of Sukuna's fingers, somewhere it shouldn't be.",
             dict(min_grade="g3", min_bond=50), "III")]),
        ("megumi", [
            ("The Hospital", "Visiting his sister.",
             dict(min_bond=35, thread=("megumi_tsumiki", 1)), "I"),
            ("Divine Dogs", "A job with his shikigami.", dict(min_grade="g3"), "II"),
            ("What the Zenin Wanted", "What the Zenin wanted from him.", dict(min_bond=65), "III")]),
        ("nobara", [
            ("Harajuku", "A day out.", dict(min_bond=30, flags=("ijichi_rides",)), "I"),
            ("Straw Doll", "Resonance training.", dict(min_grade="g3"), "II"),
            ("Saori's Letter", "A letter from home.",
             dict(min_bond=60, thread=("nobara_saori", 1)), "III")]),
        ("maki", [
            ("The Armory", "Maki opens the racks; my grade decides what they release.",
             dict(min_bond=10, flags=("met_second_years",)), "II"),
            ("Mai, Before Kyoto", "Her sister is on the other team.",
             dict(after="m_roster"), "IV"),
            ("Playful Cloud, on Loan", "A special-grade staff, lent.",
             dict(min_bond=70, min_grade="g2"), "IV")]),
        ("panda", [
            ("Gorilla Core", "What he has in reserve.", dict(min_bond=30), "II"),
            ("Yaga's Son", "Where he came from.", dict(min_bond=45), "III"),
            ("Three Hearts", "What he's made of.",
             dict(min_bond=65, thread=("panda_made", 2)), "IV")]),
        ("toge", [
            ("Onigiri Words", "Guess what he means.", dict(min_bond=20), "II"),
            ("Throat Medicine", "What his voice costs him.", dict(min_bond=40), "III"),
            ("Don't Move", "His voice saves me.", dict(min_grade="g3"), "III")]),
        ("gojo", [
            ("Infinity", "A lesson on a day he's in.",
             dict(gojo_in=True, flags=("intensive_done",)), "II"),
            ("Unlimited Void, From Outside", "What he is, from the outside.",
             dict(act_done="II"), "III"),
            ("Under the Blindfold", "What he sees.", dict(min_bond=60), "IV")]),
        ("utahime", [
            ("What She's Helping Gojo With", "The thing neither of them will explain.",
             dict(min_bond=30), "I"),
            ("Rivals", "Her feud with Gojo.", dict(min_bond=45), "II"),
            ("Kyoto's Teacher", "Whose side she's on in Act IV.", dict(after="m_roster"), "IV")]),
        ("shoko", [
            ("Coffee in the Infirmary", "A quiet hour.", dict(min_bond=20), "I"),
            ("Reverse Cursed Technique, in Theory", "How she puts people back.",
             dict(min_bond=40), "II"),
            ("Old Friends", "Who she used to be friends with.",
             dict(min_bond=60, thread=("shoko_remembers", 1)), "III")]),
        ("yaga", [
            ("The Cursed Doll Workshop", "What he builds, and why.", dict(min_bond=30), "II"),
            ("Why Do You Do This?", "Asked again.", dict(min_bond=60), "III")]),
        ("ijichi", [
            ("Ride-Along", "A day on the job from his passenger seat.",
             dict(after="m_utahime"), "I"),
            ("The Veil", "Learn to raise one.", dict(min_bond=30, min_grade="g3"), "II")]),
        ("nanami", [
            ("The Bakery", "Overtime, and bread.", {}, "III"),
            ("Ratio", "The weak point at the 7:3 line.", {}, "III")]),
        ("todo", [
            ("What Type of Woman?", "The only question he asks.", {}, "IV"),
            ("Brother", "Boogie Woogie practice.", {}, "IV"),
            ("The Idol Handshake Event", "He needs a second.", {}, "IV")]),
        ("miwa", [
            ("Simple Domain", "A counter to a sure hit.", {}, "IV"),
            ("An Autograph from Gojo", "She's too shy to ask.", {}, "IV")]),
        ("mei_mei", [
            ("Everything Has a Price", "She does nothing for free.", {}, "V")]),
    ]

    _CM_HIDDEN = ("nanami", "todo", "miwa", "mei_mei")
    _MS_SHORT = {"nanami": "Nanami", "todo": "Todo", "miwa": "Miwa", "mei_mei": "Mei Mei",
                 "yuta": "Yuta"}

    def _ms_short(who):
        if who in CAST:
            return CAST[who]["short"]
        return _MS_SHORT.get(who, str(who).replace("_", " ").title())

    ## The two written in phase 1 (placeholders in missions_stubs.rpy).
    _CM_EXTRA = {
        "cm_ijichi_1": dict(where="gate", periods=_M3, cost=2,
                            objective="Ijichi has something for me",
                            rewards=dict(bond={"ijichi": 5})),
        "cm_maki_1": dict(objective="Maki wants to show me something in the storehouse",
                          rewards=dict(bond={"maki": 5}, items={"slaughter_demon": 1})),
    }

    for _i, (_who, _rows) in enumerate(_CM_TABLE):
        for _n, (_title, _summary, _gate, _act) in enumerate(_rows, 1):
            _id = "cm_%s_%d" % (_who, _n)
            _kw = dict(label=_id, trigger="start", who=_who, gate=_gate,
                       hidden_until_met=(_who in _CM_HIDDEN))
            _kw["objective"] = "%s has something for me" % _ms_short(_who)
            _kw.update(_CM_EXTRA.get(_id, {}))
            mission(_id, "character", _act, 1000 + _i * 100 + _n * 10, _title, _summary, **_kw)
    del _i, _who, _rows, _n, _title, _summary, _gate, _act, _id, _kw

    ## Lookups ------------------------------------------------------------------------

    MISSIONS.sort(key=lambda m: m["order"])
    MISSION_BY_ID = {m["id"]: m for m in MISSIONS}
    MISSION_BY_LABEL = {m["label"]: m for m in MISSIONS if m["label"]}
    RETIRED_LABELS = {"st_board_open", "ev_patrol"}
    STORY_ROWS = [m for m in MISSIONS if m["kind"] in ("story", "promotion")]

    def _ms_written(m):
        return bool(m["label"]) and renpy.has_label(m["label"])

    def _ms_giver(m):
        return m["with_who"] or m["who"]

    def _ms_is_story(m):
        return m["kind"] in ("story", "promotion")

    def _ms_granted():
        """merit_granted (WP2's default); created here if it isn't there yet."""
        s = getattr(store, "merit_granted", None)
        if s is None:
            store.merit_granted = s = set()
        return s

    def _ms_event(m):
        """The EVENTS entry that plays a mission's label, or None."""
        lab = m["label"]
        if not lab:
            return None
        for e in EVENTS:
            if e["label"] == lab:
                return e
        return None

    ## Status (cached per interaction, D22) ---------------------------------------
    ##
    ## The cache is a plain builtins dict made at init and never assigned, so it
    ## is neither saved nor rolled back. config.interact_callbacks clears it once
    ## per interaction; a fingerprint of the state status reads also clears it,
    ## so code that changes state and asks again within one interaction (a
    ## scene's python, a test harness) never sees a stale answer.

    _MS_CACHE = builtins.dict()
    _MS_FP = builtins.list([None])

    def mission_cache_clear():
        """WP3. Forget every cached status (the next query recomputes)."""
        _MS_CACHE.clear()
        _MS_FP[0] = None

    def _ms_fingerprint():
        s = store
        return (s.day, s.arc_start_day, len(s.flags), len(s.done_events),
                len(s.missions_done), builtins.tuple(sorted(s.mission_state.items())),
                builtins.tuple(sorted(s.mission_retry_day.items())),
                len(s.mission_done_day), sum(s.mission_done_day.values()),
                s.merit, s.grade, len(s.roster), sum(s.bonds.values()),
                sum(s.threads.values()), bool(gojo_in_today()))

    def _ms_check_fp():
        fp = _ms_fingerprint()
        if fp != _MS_FP[0]:
            _MS_CACHE.clear()
            _MS_FP[0] = fp

    config.interact_callbacks.append(mission_cache_clear)

    def _ms_cond(c):
        """One done_if / skip_if clause: event:, flag:, grade: or mission:."""
        kind, _, arg = c.partition(":")
        if kind == "event":
            return arg in store.done_events
        if kind == "flag":
            return has_flag(arg)
        if kind == "grade":
            need = grade_rank(arg)
            return need >= 0 and grade_rank(player_grade()) >= need
        if kind == "mission":
            return mission_status(arg) == "done"
        return False

    def _ms_done_day(mid):
        ## The prologue is done on the day the campus opened (D23); a step done
        ## with no recorded day (an old save, backfilled) counts as day 0.
        if mid == "m_prologue":
            return store.arc_start_day
        return store.mission_done_day.get(mid, 0)

    _MS_FLAG_REASONS = {
        "met_second_years": "After the second-years arrive",
        "ijichi_rides": "After Ijichi's ride-along",
        "intensive_done": "After Gojo's first lesson",
        "oda_answered": "Only if I answered Oda-sensei",
        "yuji_secret": "Later in the story",
    }

    def _ms_requirements(m):
        """(reason, need_day): reason is "" when every requirement but the day
        is met; need_day is the first day it can happen."""
        need = 0
        g = m["gate"]
        if _ms_is_story(m):
            prev = None
            for r in STORY_ROWS:
                if r["order"] >= m["order"]:
                    break
                if r["optional"]:
                    continue
                s = mission_status(r["id"])
                if s == "done":
                    prev = r
                elif s not in ("skipped", "unwritten"):
                    return ("After " + r["title"], 0)
            if prev is not None:
                need = _ms_done_day(prev["id"]) + g["gap_days"]
        if g["after"]:
            s = mission_status(g["after"])
            if s not in ("done", "skipped"):
                return ("After " + MISSION_BY_ID[g["after"]]["title"], 0)
            if s == "done":
                need = max(need, _ms_done_day(g["after"]) + g["gap_days"])
        for f in g["flags"]:
            if not has_flag(f):
                return (_MS_FLAG_REASONS.get(f, "Not yet"), 0)
        for f in g["not_flags"]:
            if has_flag(f):
                return ("Not now", 0)
        giver = _ms_giver(m)
        if m["kind"] == "character" and giver not in store.roster:
            return ("Not met yet", 0)
        if g["min_grade"] and grade_rank(player_grade()) < grade_rank(g["min_grade"]):
            return ("Needs " + grade_label(g["min_grade"]), 0)
        if g["min_bond"] and giver and store.bonds.get(giver, 0) < g["min_bond"]:
            return ("Bond %d with %s" % (g["min_bond"], _ms_short(giver)), 0)
        if g["merit"] and store.merit < g["merit"]:
            return ("Merit %d/%d" % (store.merit, g["merit"]), 0)
        if g["thread"]:
            tid, stage = g["thread"]
            if thread_stage(tid) < stage:
                return ("Further along: " + THREADS[tid]["title"], 0)
        if g["gojo_in"] and not gojo_in_today():
            return ("On a day Gojo is in", 0)
        if g["act_done"] and not act_done(g["act_done"]):
            return ("After Act " + g["act_done"], 0)
        return ("", need)

    def _ms_compute(m):
        """(status, reason, days to wait) for one mission (3.6, in order)."""
        mid = m["id"]
        if mid in store.missions_done or any(_ms_cond(c) for c in m["done_if"]):
            return ("done", "", 0)
        if any(_ms_cond(c) for c in m["skip_if"]):
            return ("skipped", "", 0)
        st = store.mission_state.get(mid)
        if st == "closed":
            return ("closed", "Closed when Arc Two began", 0)
        if not _ms_written(m):
            return ("unwritten", "Written in a later build", 0)
        if st == "active":
            return ("active", "", 0)
        reason, need = _ms_requirements(m)
        if reason:
            return ("locked", reason, 0)
        retry = store.mission_retry_day.get(mid, 0)
        if store.day < retry:
            n = retry - store.day
            return ("waiting", "Try again tomorrow" if n == 1 else "Try again in %d days" % n, n)
        if store.day < need:
            n = need - store.day
            return ("waiting", "Tomorrow" if n == 1 else "In %d days" % n, n)
        return ("available", "", 0)

    def _ms_entry(mid):
        _ms_check_fp()
        c = _MS_CACHE.get(mid)
        if c is None:
            m = MISSION_BY_ID.get(mid)
            if m is None:
                return ("locked", "", 0)
            c = _ms_compute(m)
            _MS_CACHE[mid] = c
        return c

    def mission_status(id):
        """WP3. done / skipped / closed / unwritten / active / waiting /
        available / locked, cached per interaction (D22). An unknown id is
        "locked"."""
        return _ms_entry(id)[0]

    def mission_reason(id):
        """WP3. Why a mission is locked or waiting, in the player's words:
        "Needs Grade 3", "Bond 40 with Megumi", "After The Sun Mall",
        "Merit 34/60", "Try again tomorrow", "Tomorrow", "Written in a later
        build". "" when it is available, active, done or skipped."""
        return _ms_entry(id)[1]

    def mission_wait_days(id):
        """WP3. Days until a waiting mission opens (0 if not waiting)."""
        return _ms_entry(id)[2]

    def mission_group_text(mid):
        """WP3. "The Surveyor 2/3" for a grouped mission, else ""."""
        m = MISSION_BY_ID.get(mid)
        if not m or not m["group"]:
            return ""
        rows = [r for r in MISSIONS if r["group"] == m["group"]]
        done = sum(1 for r in rows if mission_status(r["id"]) == "done")
        return "%s %d/%d" % (m["group"], done, len(rows))

    ## Words ---------------------------------------------------------------------

    _MS_PER_PLURAL = {"Morning": "mornings", "Noon": "middays", "Afternoon": "afternoons",
                      "Evening": "evenings", "Night": "nights"}
    _MS_PER_ONE = {"Noon": "at noon", "Night": "at night"}
    _MS_PER_TOMORROW = {"Morning": "tomorrow morning", "Noon": "tomorrow at noon",
                        "Afternoon": "tomorrow afternoon", "Evening": "tomorrow evening",
                        "Night": "tomorrow night"}

    def _ms_join(words):
        if len(words) <= 1:
            return "".join(words)
        return ", ".join(words[:-1]) + " and " + words[-1]

    def periods_text(pers):
        """WP3. "mornings", "mornings to afternoons", "afternoons or evenings",
        "at noon", "at night", "mornings, middays and evenings"."""
        pers = [p for p in PERIODS if p in (pers or ())]
        if not pers or len(pers) == len(PERIODS):
            return "any time"
        if len(pers) == 1:
            return _MS_PER_ONE.get(pers[0]) or _MS_PER_PLURAL[pers[0]]
        idx = [PERIODS.index(p) for p in pers]
        if len(pers) >= 3 and idx == list(range(idx[0], idx[-1] + 1)):
            return "%s to %s" % (_MS_PER_PLURAL[pers[0]], _MS_PER_PLURAL[pers[-1]])
        if len(pers) == 2:
            return "%s or %s" % (_MS_PER_PLURAL[pers[0]], _MS_PER_PLURAL[pers[1]])
        return _ms_join([_MS_PER_PLURAL[p] for p in pers])

    def _ms_periods(m):
        if m["periods"]:
            return m["periods"]
        e = _ms_event(m)
        if e and e["periods"]:
            return tuple(e["periods"])
        return ()

    def _ms_place_name(loc):
        if not loc:
            return ""
        return LOCATIONS.get(loc, {}).get("name", loc)

    def _ms_when(who, loc):
        """when_at (WP1), or a plain reading of the weekday schedule."""
        w = when_at(who, loc) if who and loc else ""
        if w:
            return w
        table = SCHEDULE.get(who, {})
        pers = [p for p in PERIODS if table.get(p) == loc]
        if not pers:
            return ""
        txt = periods_text(pers)
        if any(WEEKEND.get(who, {}).get(p, table.get(p)) != loc for p in pers):
            txt = "weekday " + txt
        return txt

    def _ms_place(m):
        """Where a start-type mission is given right now (or usually)."""
        locs = m["where"]
        if isinstance(locs, str):
            locs = (locs,)
        giver = _ms_giver(m)
        now = char_location(giver) if giver in store.roster else None
        if locs:
            return now if now in locs else locs[0]
        if now:
            return now
        for p in PERIODS:
            l = SCHEDULE.get(giver, {}).get(p)
            if l and l != "-":
                return l
        return None

    def _ms_period_ok(m):
        return not m["periods"] or store.period in m["periods"]

    ## Queries -------------------------------------------------------------------

    def missions_list(kind=None, status=None, act=None, who=None):
        """WP3. The ids of the missions matching every filter given, in order.
        kind and status may each be one value or a tuple of them (the story
        chain is kind=("story", "promotion")); who matches the mission's who
        or with_who."""
        if isinstance(kind, str):
            kind = (kind,)
        if isinstance(status, str):
            status = (status,)
        out = []
        for m in MISSIONS:
            if kind and m["kind"] not in kind:
                continue
            if act and m["act"] != act:
                continue
            if who and who not in (m["who"], m["with_who"]):
                continue
            if status and mission_status(m["id"]) not in status:
                continue
            out.append(m["id"])
        return out

    def _ms_startable(m, loc=None):
        """Start-type, available (or left "active" by a scene that never
        returned: a save recovered mid-mission, so it can be started again),
        its period fits and (with loc) its giver is at loc, which is a place it
        can be given."""
        if m["trigger"] != "start" or mission_status(m["id"]) not in ("available", "active"):
            return False
        if not _ms_period_ok(m):
            return False
        if loc is None:
            return True
        giver = _ms_giver(m)
        if giver not in who_is_here(loc):
            return False
        locs = m["where"]
        if isinstance(locs, str):
            locs = (locs,)
        return not locs or loc in locs

    def missions_here(loc):
        """WP3. Ids of the start-type missions that can be started at loc now:
        available (or a stranded "active"), `where` matches, the giver is
        present and the period fits. Never in explore mode."""
        if store.explore_mode:
            return []
        return [m["id"] for m in MISSIONS if _ms_startable(m, loc)]

    def missions_with(who, loc=None):
        """WP3. Ids of the start-type missions this person can give now (at
        loc, when given: they must be there, and it must be a place the
        mission is given). Never in explore mode."""
        if store.explore_mode:
            return []
        return [m["id"] for m in MISSIONS
                if _ms_giver(m) == who and _ms_startable(m, loc)]

    def mission_markers():
        """WP3. {loc: [(text, kind)]} for the map: "Yaga · The Sun Mall"
        (kind "mission") at the giver's place, only while the giver is there
        and it can be started now; "Board · 3 jobs" (kind "board") at the
        board's host; "Gojo is in" (kind "gojo") at his office."""
        out = {}
        if store.explore_mode:
            return out
        for m in MISSIONS:
            giver = _ms_giver(m)
            loc = char_location(giver) if giver in store.roster else None
            if loc and _ms_startable(m, loc):
                out.setdefault(loc, []).append(
                    ("%s · %s" % (_ms_short(giver), m["title"]), "mission"))
        host, hloc = board_host()
        if has_flag("mission_board_open") and host in store.roster:
            ## board_summary()'s shape isn't frozen (WP4): take a list of
            ## offers or a count.
            offers = (board_summary() or {}).get("offers")
            n = offers if isinstance(offers, int) else len(offers or ())
            if n > 0:
                out.setdefault(hloc, []).append(("Board · %d jobs" % n, "board"))
        if gojo_in_today():
            out.setdefault("gojo_office", []).append(("Gojo is in", "gojo"))
        return out

    def next_for(who):
        """WP3. (text, where): the next thing to do with someone, for the
        journal. A mission with them, then a new bond scene, then the next
        activity unlock, then "Talk". None for someone not met."""
        if who not in store.roster or who not in CAST:
            return None
        usual = usual_places(who) or _ms_place_name(char_location(who))
        for m in MISSIONS:
            if _ms_giver(m) == who and m["trigger"] == "start" \
                    and mission_status(m["id"]) in ("available", "active"):
                loc = _ms_place(m)
                when = _ms_when(who, loc)
                where = _ms_place_name(loc) + ((", " + when) if when else "")
                return (m["title"], where)
        if has_event("hangout", who):
            return ("Spend time together", usual)
        nu = next_unlock(who)
        if nu:
            return ("%s at %s" % (nu[1], nu[2]), usual)
        return ("Talk", usual)

    ## Acts ------------------------------------------------------------------------

    def act_done(act):
        """WP3. True when the act has at least one written story row and every
        non-optional written one is done or skipped."""
        written = [m for m in STORY_ROWS if m["act"] == act and _ms_written(m)]
        if not written:
            return False
        return all(mission_status(m["id"]) in ("done", "skipped")
                   for m in written if not m["optional"])

    def acts_done():
        """WP3. How many acts, from Act I, are done in a row."""
        n = 0
        for a in ACT_IDS:
            if a == "P":
                continue
            if not act_done(a):
                break
            n += 1
        return n

    def act_progress(act):
        """WP3. (done, written, total) story rows for an act; done counts the
        written rows that are done or skipped, so it never exceeds written."""
        rows = [m for m in STORY_ROWS if m["act"] == act]
        written = [m for m in rows if _ms_written(m)]
        done = [m for m in written if mission_status(m["id"]) in ("done", "skipped")]
        return (len(done), len(written), len(rows))

    def main_story_complete():
        """WP3. Every non-optional story row is written and done. Always False
        in phase 1, except with the review tools' flag dev_story_complete in
        a developer build."""
        if has_flag("dev_story_complete") and config.developer:
            return True
        for m in STORY_ROWS:
            if m["optional"]:
                continue
            if not _ms_written(m) or mission_status(m["id"]) not in ("done", "skipped"):
                return False
        return True

    ## The objective ------------------------------------------------------------------

    def _ms_objective_for(m, status):
        obj = m["objective"] or m["title"]
        n = mission_wait_days(m["id"])
        if m["trigger"] == "auto":
            pers = _ms_periods(m)
            ptxt = periods_text(pers)
            if status == "active":
                text, when = obj, ""
            elif status == "waiting":
                if n == 1 and len(pers) == 1:
                    when = _MS_PER_TOMORROW[pers[0]]
                else:
                    when = ("tomorrow" if n == 1 else "in %d days" % n) + ", " + ptxt
                text = "%s — %s, wherever I am" % (obj, when)
            else:
                when = ptxt
                text = "%s — %s, wherever I am" % (obj, when)
            return dict(text=text, where=None, when=when, mid=m["id"])
        giver = _ms_giver(m)
        loc = _ms_place(m)
        when = _ms_when(giver, loc)
        if isinstance(m["where"], tuple):
            text = obj                      # the objective names the places
        else:
            text = "%s — %s" % (obj, _ms_place_name(loc))
            if when:
                text += ", " + when
        if status == "waiting":
            r = mission_reason(m["id"])
            if r.startswith("Try"):
                text += " — " + r[0].lower() + r[1:]
            else:
                text += ", " + ("from tomorrow" if n == 1 else "in %d days" % n)
        return dict(text=text, where=loc, when=when, mid=m["id"])

    def current_objective():
        """WP3. dict(text, where, when, mid) for the NEXT line, or None before
        the campus opens. The first story row that is active, available or
        waiting; else a merit lock ("Earn merit on Utahime's board: 34/60 —
        then the promotion fight"); else, with only unwritten rows left, the
        best available character mission; else "the story continues"."""
        if not has_flag("settled_in"):
            return None
        for m in STORY_ROWS:
            s = mission_status(m["id"])
            if s in ("active", "available", "waiting"):
                return _ms_objective_for(m, s)
        for m in STORY_ROWS:
            if m["optional"]:
                continue
            if mission_status(m["id"]) != "locked":
                continue
            r = mission_reason(m["id"])
            if r.startswith("Merit"):
                host, hloc = board_host()
                return dict(text="Earn merit on %s's board: %d/%d — then the promotion fight"
                                 % (_ms_short(host), store.merit, m["gate"]["merit"]),
                            where=hloc, when="", mid=m["id"])
            return dict(text="%s — %s" % (m["objective"] or m["title"], r),
                        where=None, when="", mid=m["id"])
        for m in MISSIONS:
            if m["kind"] == "character" and mission_status(m["id"]) == "available":
                return _ms_objective_for(m, "available")
        return dict(text="The story continues in a later build. The board and everyone on campus are open.",
                    where=None, when="", mid=None)

    def objective_text():
        """WP3. The one-line objective ("" before the campus opens)."""
        o = current_objective()
        return o["text"] if o else ""

    ## Changing state ---------------------------------------------------------------

    def complete_mission(id):
        """WP3. Records the mission done (the day, missions_done), clears its
        active state, and pays its rewards once (merit_granted key
        "mission:<id>"): merit, bond, yen, items and flags. An unknown id does
        nothing."""
        m = MISSION_BY_ID.get(id)
        if m is None:
            return
        first = id not in store.missions_done
        if first:
            store.mission_done_day[id] = store.day
            store.missions_done.add(id)
        store.mission_state.pop(id, None)
        granted = _ms_granted()
        key = "mission:" + id
        if key not in granted:
            granted.add(key)
            r = m["rewards"]
            if r["merit"]:
                add_merit(r["merit"], m["title"])
            for who, n in sorted(r["bond"].items()):
                add_bond(who, n)
            if r["yen"]:
                add_yen(r["yen"])
            for item, n in sorted(r["items"].items()):
                give_item(item, n)
            for f in r["flags"]:
                flag(f)
        if first:
            toast("%s — done" % m["title"], "mission")
        mission_cache_clear()

    def mission_fail(id):
        """WP3. Not today: the mission can be retried tomorrow. Clears its
        active state and toasts "Not today. Try again tomorrow." An unknown id
        does nothing."""
        if id not in MISSION_BY_ID:
            return
        store.mission_retry_day[id] = store.day + 1
        store.mission_state.pop(id, None)
        toast("Not today. Try again tomorrow.", "mission")
        mission_cache_clear()

    def begin_arc_two():
        """WP3. Sets flag arc2_started and moves to the second arc, and closes
        every Arc One character mission that isn't done. Memories are
        untouched."""
        flag("arc2_started")
        store.arc = max(store.arc, 2)
        for m in MISSIONS:
            if m["kind"] == "character" and mission_status(m["id"]) != "done":
                store.mission_state[m["id"]] = "closed"
        mission_cache_clear()

    ## Hooks (3.6) --------------------------------------------------------------------

    def _ms_event_gate(e):
        """An event bound to a mission fires only while it is available (or
        "active": start_mission is playing it, or a recovered save left it
        so); a retired one never; after Arc Two begins, an arc-1 hangout
        whose thread is unfinished stops."""
        lab = e["label"]
        if lab in RETIRED_LABELS:
            return False
        m = MISSION_BY_LABEL.get(lab)
        if m is not None:
            return mission_status(m["id"]) in ("available", "active")
        if (e["kind"] == "hangout" and e.get("thread") and e.get("arc", 1) == 1
                and has_flag("arc2_started") and not thread_done(e["thread"][0])):
            return False
        return True

    def _ms_event_done(e):
        m = MISSION_BY_LABEL.get(e["label"])
        if m is not None:
            complete_mission(m["id"])

    register_event_gate(_ms_event_gate)
    register_event_done(_ms_event_done)

    ## Migrations (3.12) -------------------------------------------------------------

    ## A story scene marked done (done_events) whose flags later ev()s or
    ## gates need: a save that has the event but not the flag (one that left
    ## the scene through a recovery) gets the flag, or the next step would be
    ## "available" and never fire. Missions (the Sun Mall, Nade) are left
    ## alone: a save from inside one really hasn't finished it.
    _MS_BACKFILL = (
        ("st_roll_call", ("roll_call", "storehouse_access")),
        ("st_kurose", ("kurose_met",)),
        ("st_second_years", ("met_second_years",)),
        ("st_intensive", ("intensive_done",)),
    )

    def _migrate_40():
        """WP3, migration 40: Ijichi and Utahime on the roster; the old arc
        ending counts as the night before; finished story scenes get the flags
        the next steps require (_MS_BACKFILL)."""
        if has_flag("settled_in") and "ijichi" not in store.roster:
            recruit("ijichi")
        if has_flag("utahime_arrived") and "utahime" not in store.roster:
            recruit("utahime")
        if has_flag("arc1_complete"):
            flag("night_before_done")
        for lab, fl in _MS_BACKFILL:
            if lab in store.done_events:
                for f in fl:
                    if not has_flag(f):
                        flag(f)
        mission_cache_clear()

    def _migrate_50():
        """WP3, migration 50: the second arc is a choice now, not a date."""
        if store.arc != 1 and not has_flag("arc2_started"):
            store.arc = 1
        mission_cache_clear()

    def _migrate_60():
        """WP3, migration 60: merit for every mission already done, paid once
        (merit_granted), and the Sun Mall recommendation (20) for a save that
        finished the Sun Mall before ch5 paid it (the new ch5 sets
        recommended_g3 when it pays)."""
        mission_cache_clear()
        granted = _ms_granted()
        for m in MISSIONS:
            n = m["rewards"]["merit"]
            key = "mission:" + m["id"]
            if n and key not in granted and mission_status(m["id"]) == "done":
                granted.add(key)
                add_merit(n, m["title"])
        if has_flag("sunmall_done") and "ch5_recommendation" not in granted:
            granted.add("ch5_recommendation")
            if not has_flag("recommended_g3"):
                add_merit(20, "The Sun Mall")
        mission_cache_clear()

    def _migrate_65():
        """WP3 (mission part of migration 65): a story row done with no
        recorded day counts as day 0, so it adds no gap delay."""
        mission_cache_clear()
        for m in STORY_ROWS:
            if m["id"] not in store.mission_done_day and mission_status(m["id"]) == "done":
                store.mission_done_day[m["id"]] = 0
        mission_cache_clear()

    register_migration(40, _migrate_40, "roster: Ijichi, Utahime; night_before_done")
    register_migration(50, _migrate_50, "back to the first arc unless the second was begun")
    register_migration(60, _migrate_60, "merit for missions already done; ch5 recommendation")
    register_migration(65, _migrate_65, "done story rows get a done day")

    ## Validator (lint) ------------------------------------------------------------------

    _MS_COND_KINDS = ("event", "flag", "grade", "mission")

    def _validate_missions():
        out = []
        seen_ids, seen_orders = set(), {}
        people = set(CAST) | set(JOURNAL_CAST_BY_WHO)
        for m in MISSIONS:
            mid = m["id"]
            if mid in seen_ids:
                out.append("mission id %r is used twice" % mid)
            seen_ids.add(mid)
            if m["order"] in seen_orders:
                out.append("missions %r and %r share order %d" % (seen_orders[m["order"]], mid, m["order"]))
            seen_orders[m["order"]] = mid
            if m["kind"] not in MISSION_KINDS:
                out.append("mission %r: kind %r" % (mid, m["kind"]))
            if m["trigger"] not in MISSION_TRIGGERS:
                out.append("mission %r: trigger %r" % (mid, m["trigger"]))
            if m["act"] not in ACT_IDS:
                out.append("mission %r: act %r" % (mid, m["act"]))
            if m["label"] and not renpy.has_label(m["label"]) and m["kind"] != "character":
                out.append("mission %r: label %r does not exist" % (mid, m["label"]))
            locs = m["where"]
            if isinstance(locs, str):
                locs = (locs,)
            for l in (locs or ()):
                if l not in LOCATIONS:
                    out.append("mission %r: where %r is not a place" % (mid, l))
            for who in (m["with_who"], m["who"]):
                if who and who not in people:
                    out.append("mission %r: %r is not a person" % (mid, who))
            if m["trigger"] == "start" and not _ms_giver(m):
                out.append("mission %r: a start mission needs a giver" % mid)
            if _ms_is_story(m) and m["label"] and mid != "m_prologue" and not m["objective"]:
                out.append("mission %r: a written story step needs an objective" % mid)
            for p in (m["periods"] or ()):
                if p not in PERIODS:
                    out.append("mission %r: period %r" % (mid, p))
            for c in m["done_if"] + m["skip_if"]:
                kind, _, arg = c.partition(":")
                if kind not in _MS_COND_KINDS or not arg:
                    out.append("mission %r: bad condition %r" % (mid, c))
                elif kind == "grade" and arg not in GRADES:
                    out.append("mission %r: bad grade in %r" % (mid, c))
                elif kind == "mission" and arg not in MISSION_BY_ID:
                    out.append("mission %r: unknown mission in %r" % (mid, c))
                elif kind == "event" and not renpy.has_label(arg):
                    out.append("mission %r: no label for %r" % (mid, c))
            g = m["gate"]
            for k in g:
                if k not in _MS_GATE_DEFAULTS:
                    out.append("mission %r: unknown gate key %r" % (mid, k))
            if g["after"] and g["after"] not in MISSION_BY_ID:
                out.append("mission %r: gate after %r is not a mission" % (mid, g["after"]))
            if g["min_grade"] and g["min_grade"] not in GRADES:
                out.append("mission %r: gate min_grade %r" % (mid, g["min_grade"]))
            if g["thread"] and g["thread"][0] not in THREADS:
                out.append("mission %r: gate thread %r" % (mid, g["thread"]))
            if g["act_done"] and g["act_done"] not in ACT_IDS:
                out.append("mission %r: gate act_done %r" % (mid, g["act_done"]))
            for k in m["rewards"]:
                if k not in _MS_REWARD_DEFAULTS:
                    out.append("mission %r: unknown reward key %r" % (mid, k))
            for who in m["rewards"]["bond"]:
                if who not in CAST:
                    out.append("mission %r: bond reward for %r" % (mid, who))
        for mid in ("cm_ijichi_1", "cm_maki_1"):
            m = MISSION_BY_ID.get(mid)
            if not m or not renpy.has_label(m["label"]):
                out.append("character mission %r is written in phase 1 but has no label" % mid)
        for e in EVENTS:
            if e["kind"] in ("story", "mission"):
                if e["label"] not in MISSION_BY_LABEL and e["label"] not in RETIRED_LABELS:
                    out.append("ev(%r, kind=%r) is not bound to a mission or retired"
                               % (e["label"], e["kind"]))
        return out

    register_validator(_validate_missions)


################################################################################
## Starting a mission
################################################################################

## WP3. Plays a mission's scene, then completes it and charges its cost.
## A mission bound to an ev() plays through play_event, which keeps
## done_events and the thread advance as before; its done hook completes the
## mission. Otherwise the label is called, and the mission completes unless
## the scene called mission_fail(). Does nothing unless the mission is
## available (or already active).
label start_mission(mid):
    if mid not in MISSION_BY_ID or mission_status(mid) not in ("available", "active"):
        return
    $ mission_state[mid] = "active"
    $ mission_cache_clear()
    $ _sm_event = _ms_event(MISSION_BY_ID[mid])
    ## SAVE-PROTECTED: saves made inside a mission scene return to the two
    ## calls below and the `if` after the second. Keep these three statements
    ## textually identical (a comment doesn't change statement names).
    if _sm_event:
        call play_event(_sm_event)
    else:
        call expression MISSION_BY_ID[mid]["label"]
        if mission_state.get(mid) == "active":
            $ complete_mission(mid)
    $ _sm_event = None
    if MISSION_BY_ID[mid]["cost"]:
        $ advance_period(MISSION_BY_ID[mid]["cost"])
    return


################################################################################
## Arc Two (3.6.3)
################################################################################

## WP3. The "This begins Arc Two" warning and card, reached from the campus
## journal (D38), and only while main_story_complete().
label arc_two_start:
    if not main_story_complete():
        return
    menu:
        "This begins Arc Two. Character stories you haven't finished in Arc One will close."  ## you-ok (system message, exact text)

        "Begin Arc Two":
            $ begin_arc_two()

        "Not yet":
            return

    scene bg black with fade_slow
    show screen chapter_card("ARC TWO", "Shibuya Is a Long Way Off", "Arc Two arrives in a later build. Everything you finished stays in your journal.")
    with fade_slow
    $ renpy.pause(4.0)
    hide screen chapter_card
    with fade_slow
    scene expression graded_bg() with fade_slow
    return


## Mission state (3.11) #########################################################

default mission_state = {}        # id -> "active" | "closed"
default missions_done = set()
default mission_done_day = {}     # id -> day
default mission_retry_day = {}    # id -> first day it can be tried again
default last_objective = None     # the objective text last shown (WP7)
default _sm_event = None          # the EVENTS entry start_mission is playing
