################################################################################
## Cursed Bonds — memories and replay.
##
## WP5 owns this file (PHASE1_DESIGN.md 3.9, D5, D6, D11).
##
## The journal's Memories tab replays any scene this save has seen. Three
## things live here:
##
##   MEMORIES          the catalogue: every scene that can be relived, with
##                     who is in it, which act it belongs to, how to tell
##                     whether this save has seen it, and a hint for when it
##                     hasn't.
##   the recorder      config.label_callbacks notes catalogued labels in
##                     memories_seen as they play (never during a replay), and
##                     record_act() notes activity scenes in seen_acts. Old
##                     saves are read from done_events and flags instead.
##   the replay        memory_replay(m) is a Replay(locked=False) of
##                     `label mem_play` with a scope copied from the save.
##                     Replays run in their own store, so nothing that happens
##                     in one reaches the save, and toasts are muted.
##
## Nothing here is written to persistent: whether a memory is seen is a fact
## about this save, not about the machine (D5, D6).
##
## A catalogue entry:
##   dict(id, title, who=(), act, label, args=(), seen=[rules], hint,
##        unlock=None, bg)
##   act      "Prologue", "I".."V", "Bonds" or "Sana"
##   seen     a list of rules, any of which will do:
##              ("label", name)      name is in memories_seen
##              ("event", label)     label is in done_events
##              ("flag", name)       the flag is set
##              ("act", "aid:who")   the activity scene is in seen_acts
##              ("together", who)    the confession has happened
##            A memory without args also counts as seen once its label is in
##            memories_seen.
##   unlock   None, or a rule that opens the memory: ("flag", name),
##            ("district", key) or ("item", id). Sana's flashbacks. Until it
##            is met the tile shows the hint; once it is met the memory
##            replays, or reads "Written in a later build" while its label
##            doesn't exist yet.
##
## For the journal (WP8): memory_groups(mode) gives the tiles, each a
## memory_entry() with "state" ("seen" / "unseen" / "later"), "is_seen" and
## "text" (the hint, or "Written in a later build"); memory_replay(m) is the
## tile's action; memories_with(who) gives one person's memories.
##
## To add a memory, add a line to the catalogue below. The lint validator
## checks its label, people, act, rules and background.
################################################################################

init -1 python:

    import copy as _mem_copy_mod

    ## Acts, in the order the By act view shows them.
    MEMORY_ACTS = [
        ("Prologue", "Prologue · The Lights"),
        ("I",        "Act I · Grade Four"),
        ("II",       "Act II · The Ones Who Stay"),
        ("III",      "Act III · Overtime"),
        ("IV",       "Act IV · Goodwill"),
        ("V",        "Act V · Cursed Womb"),
        ("Bonds",    "Bonds"),
        ("Sana",     "Sana"),
    ]

    ## People, in the order the By person view shows them: Sana first, then
    ## the journal's cast order (3.6.2). Memories with nobody from the cast in
    ## them come last, under MEMORY_NOBODY.
    MEMORY_PEOPLE = ["sana", "yuji", "megumi", "nobara", "maki", "panda", "toge",
                     "gojo", "utahime", "shoko", "yaga", "ijichi"]
    MEMORY_NOBODY = "Everyone else"

    ## The tile text for a memory whose scene is still to be written.
    MEMORY_LATER = "Written in a later build"

    ## Labels other wave-1 packages add: the prologue's sub-labels (WP9, D39)
    ## and the two new story scenes (WP3). The validator lets them be missing
    ## until those packages merge; the journal shows them as "later" meanwhile.
    MEMORY_PENDING_LABELS = frozenset([
        "ch1_diner", "ch1_the_thing", "ch1_gojo", "ch2_arrival", "ch2_the_veil",
        "ch2_yaga", "ch2_first_years", "st_utahime_office", "st_promotion_g3",
    ])

    ## Sana's flashbacks are written in phase 3 (D11).
    MEMORY_UNWRITTEN_LABELS = frozenset(["sana_mem_diner", "sana_mem_daisy", "sana_mem_ranking"])

    ## The prologue's memories in the order they play (3.9, D39). Migration 65
    ## marks a settled save as having seen all of them, and a save still in
    ## the prologue as having seen every step before the one it resumes at.
    MEMORY_PROLOGUE_ORDER = ["ch1_diner", "ch1_the_thing", "ch1_gojo", "chapter_one_b",
                             "ch1b_goodbye", "ch2_arrival", "ch2_the_veil", "ch2_yaga",
                             "ch2_first_years"]

    MEMORY_RULE_KINDS = ("label", "event", "flag", "act", "together")
    MEMORY_UNLOCK_KINDS = ("flag", "district", "item")

    MEMORIES = []

    def _mem(id, title, act, label, who=(), args=(), seen=None, hint="", unlock=None, bg="bg black"):
        MEMORIES.append(dict(id=id, title=title, who=tuple(who), act=act, label=label,
                             args=tuple(args), seen=list(seen or [("label", label)]),
                             hint=hint, unlock=unlock, bg=bg))

    def _mem_story(label, title, act, who, bg, hint, flags=()):
        ## A main-story row: seen once its label has played or its event is
        ## done, or (old saves) once a flag the scene sets is set.
        _mem(label, title, act, label, who=who, bg=bg, hint=hint,
             seen=[("label", label), ("event", label)] + [("flag", f) for f in flags])

    ## --- The prologue (D39) ------------------------------------------------------

    _mem("ch1_diner", "Nine Hundred Yen", "Prologue", "ch1_diner", who=("sana",),
         bg="bg diner", hint="The prologue.")
    _mem("ch1_the_thing", "The Thing She Told Me", "Prologue", "ch1_the_thing", who=("sana",),
         bg="bg alley", hint="The prologue.")
    _mem("ch1_gojo", "The Man in the Blindfold", "Prologue", "ch1_gojo", who=("gojo",),
         bg="bg alley dark", hint="The prologue.")
    _mem("chapter_one_b", "The Offer", "Prologue", "chapter_one_b", who=("gojo",),
         bg="bg alley", hint="The prologue.")
    _mem("ch1b_goodbye", "Breakfast for Four", "Prologue", "ch1b_goodbye",
         bg="bg home_living", hint="The prologue.")
    _mem("ch2_arrival", "The Strongest of Today", "Prologue", "ch2_arrival", who=("gojo", "ijichi"),
         bg="bg gate", hint="The prologue.")
    _mem("ch2_the_veil", "The Veil on the Ridge", "Prologue", "ch2_the_veil", who=("gojo",),
         bg="bg ridge_veil", hint="The prologue.")
    _mem("ch2_yaga", "Why Are You Here?", "Prologue", "ch2_yaga", who=("yaga",),
         bg="bg office", hint="The prologue.")
    _mem("ch2_first_years", "Three First-Years", "Prologue", "ch2_first_years",
         who=("yuji", "megumi", "nobara"), bg="bg training", hint="The prologue.")

    ## --- The main story: every written story row (3.6.1) --------------------------
    ## The hints are the rows' objectives. The Sun Mall row plays as two
    ## scenes, recorded through their own labels; old saves read the row's
    ## event and flag (and, for a pre-sandbox save, the chapter's own flags).

    _mem_story("st_roll_call", "Roll Call", "I", ("yaga", "yuji", "megumi", "nobara"),
               "bg classroom", "Roll call with Principal Yaga.", flags=("roll_call",))
    _mem_story("st_utahime_office", "The Room Next to Yaga's", "I", ("utahime",),
               "bg utahime_office", "Someone is moving into the room next to Yaga's.",
               flags=("utahime_arrived",))
    _mem("chapter_four", "Kawagoe Sun Mall", "I", "chapter_four",
         who=("yuji", "megumi", "nobara", "ijichi"), bg="bg city",
         hint="Yaga has a mission for the first-years.",
         seen=[("label", "chapter_four"), ("event", "ev_mission_sunmall"), ("flag", "sunmall_done")]
              + [("flag", f) for f in ("read_wall", "ignored_wall", "scouted_corridor", "saved_civilian",
                                       "fought_first", "climax_strong", "climax_thin")])
    _mem("chapter_five", "What Should Have Happened", "I", "chapter_five",
         who=("yaga", "gojo"), bg="bg rooftop evening", hint="After the Sun Mall.",
         seen=[("label", "chapter_five"), ("event", "ev_mission_sunmall"), ("flag", "sunmall_done")])
    _mem_story("st_aftermath", "Cursed-Energy Debt", "I", ("shoko",),
               "bg infirmary", "Shoko wants to look at all four of us.", flags=("aftermath_done",))
    _mem_story("st_kurose", "Four Forms and Nine Minutes", "I", (),
               "bg office", "A man from auxiliary management is waiting outside Yaga's office.",
               flags=("kurose_met",))

    _mem_story("st_second_years", "Nobody Cares About the Technique", "II", ("maki", "panda", "toge"),
               "bg training", "The second-years are back from wherever they were.",
               flags=("met_second_years",))
    _mem_story("st_noise", "Something Eating the Lights", "II", (),
               "bg courtyard", "Stay on campus into the evening.")
    _mem_story("st_oda_letter", "A Letter from Oda-sensei", "II", (),
               "bg your_room night", "A letter is on its way from home.", flags=("oda_letter_read",))
    _mem_story("st_intensive", "Eleven Minutes", "II", ("gojo",),
               "bg ridge", "Gojo wants eleven minutes of my time.", flags=("intensive_done",))
    _mem("st_promotion_g3", "Grade Three, with Maki Watching", "II", "st_promotion_g3",
         who=("maki",), bg="bg training", hint="The promotion fight, once the merit is there.")

    _mem_story("ms_nade_1", "Sixty-One Surveys", "III", ("yaga",),
               "bg city", "Yaga has a name.", flags=("nade_named",))
    _mem_story("st_kurose_2", "Under My Door", "III", (),
               "bg your_room night", "Something from Kurose is waiting in my room.", flags=("kurose_leak",))
    _mem_story("ms_nade_2", "The Annexe", "III", ("yaga",),
               "bg ruin", "Yaga wants the annexe looked at.", flags=("nade_traced",))
    _mem_story("st_oda_2", "Counted Twice", "III", (),
               "bg your_room night", "Oda-sensei writes back.", flags=("oda_thread_open",))
    _mem_story("ms_nade_3", "A Flat in Toda", "III", ("yaga",),
               "bg town_street", "Yaga knows where Nade is.", flags=("nade_map",))

    _mem_story("st_roster", "The Kyoto Roster", "IV", ("maki",),
               "bg courtyard", "The Kyoto roster is going up.")
    _mem_story("st_night_before", "The Night Before Kyoto", "IV", ("yuji", "megumi", "nobara", "maki"),
               "bg rooftop night", "The night before Kyoto.", flags=("arc1_complete", "night_before_done"))

    ## --- Bonds: the 25 hangouts (D37) ------------------------------------------------
    ## The scenes behind "Spend time together", seen once played.

    def _mem_hang(label, title, who, bg, hint):
        _mem(label, title, "Bonds", label, who=who, bg=bg, hint=hint,
             seen=[("label", label), ("event", label)])

    _mem_hang("ev_yuji_1", "Strawberry Ones", ("yuji",), "bg rooftop", "Time with Yuji.")
    _mem_hang("ev_megumi_1", "The Edge of Myself", ("megumi",), "bg forest", "Time with Megumi.")
    _mem_hang("ev_nobara_1", "Rule One", ("nobara",), "bg city", "Time with Nobara.")
    _mem_hang("ev_maki_1", "Four Hundred Times", ("maki",), "bg training", "Time with Maki.")
    _mem_hang("ev_panda_1", "Welfare Check", ("panda", "toge"), "bg your_room night", "Time with Panda.")
    _mem_hang("ev_toge_1", "Six Words", ("toge",), "bg rooftop", "Time with Toge.")
    _mem_hang("ev_shoko_1", "Ninety Seconds", ("shoko",), "bg infirmary", "Time with Shoko.")
    _mem_hang("ev_yuji_2", "The Other Half", ("yuji",), "bg cafeteria", "Time with Yuji, at Bond 35.")
    _mem_hang("ev_megumi_2", "Tsumiki", ("megumi",), "bg forest", "Time with Megumi, at Bond 35.")
    _mem_hang("ev_nobara_2", "Saori", ("nobara",), "bg courtyard", "Time with Nobara, at Bond 35.")
    _mem_hang("ev_maki_2", "Mai", ("maki",), "bg dojo", "Time with Maki, at Bond 35.")
    _mem_hang("ev_shoko_2", "There Were Three of Us", ("shoko",), "bg rooftop evening", "Time with Shoko, at Bond 35.")
    _mem_hang("ev_panda_2", "The Third Core", ("panda",), "bg dorm_common", "Time with Panda, at Bond 35.")
    _mem_hang("ev_toge_2", "Twenty to Six on the Ridge", ("toge",), "bg ridge", "Time with Toge, at Bond 35.")
    _mem_hang("ev_nobara_r1", "The Scarf", ("nobara",), "bg riverside", "Time with Nobara, at Bond 50 and ♡ 20.")
    _mem_hang("ev_maki_r1", "Wrapped Hands", ("maki",), "bg dojo", "Time with Maki, at Bond 50 and ♡ 20.")
    _mem_hang("ev_shoko_r1", "Two in the Morning", ("shoko",), "bg infirmary night", "Time with Shoko, at Bond 50 and ♡ 20.")
    _mem_hang("ev_yuji_3", "The Number", ("yuji",), "bg rooftop", "Time with Yuji, at Bond 60.")
    _mem_hang("ev_megumi_3", "Eleven Tuesdays", ("megumi",), "bg dorm_common night", "Time with Megumi, at Bond 60.")
    _mem_hang("ev_nobara_3", "The Crossing", ("nobara",), "bg shibuya", "Time with Nobara, at Bond 60.")
    _mem_hang("ev_shoko_3", "Four in the Morning", ("shoko",), "bg infirmary night", "Time with Shoko, at Bond 60.")
    _mem_hang("ev_gojo_1", "Allowed to Lose", ("gojo",), "bg courtyard", "Time with Gojo, at Bond 20, after the Sun Mall.")
    _mem_hang("ev_yaga_1", "A Soul, on Purpose", ("yaga",), "bg storehouse", "Time with Yaga, at Bond 20.")
    _mem_hang("ev_gojo_2", "Never in a Room", ("gojo",), "bg rooftop night", "Time with Gojo, at Bond 40.")
    _mem_hang("ev_yaga_2", "The Photograph", ("yaga",), "bg office", "Time with Yaga, at Bond 40.")

    ## --- Bonds: the activity scenes, per person ---------------------------------------
    ## They replay through mem_play with args=(who,). Seen once record_act()
    ## noted them, or (old saves) from the flag the scene or sb_activity sets.
    ## act_int_night / _morning / _day set no flag, so for old saves they count
    ## from the first time they play in this build.

    def _mem_act(aid, who, title, bg, hint, legacy=()):
        _mem("%s:%s" % (aid, who), title, "Bonds", "act_" + aid, who=(who,), args=(who,),
             bg=bg, hint=hint, seen=[("act", "%s:%s" % (aid, who))] + list(legacy))

    def _mem_add_acts():
        ## Something true (Bond 65): the scene sets confided_<who>, sb_activity
        ## did_confide_<who>. Written for these nine.
        for _w, _t, _b in [
                ("yuji",   "The Whole Trick",              "bg rooftop evening"),
                ("megumi", "The Fight I Lost",             "bg forest"),
                ("nobara", "Under the Paper",              "bg courtyard"),
                ("maki",   "The Boring Part",              "bg dojo"),
                ("panda",  "The Boy in the Car",           "bg dorm_common evening"),
                ("toge",   "Sitting Here Instead",         "bg rooftop night"),
                ("shoko",  "The Sitting on the Roof",      "bg infirmary night"),
                ("gojo",   "Enough, Together",             "bg rooftop night"),
                ("yaga",   "Not Knowing Is the Condition", "bg office")]:
            _mem_act("confide", _w, _t, _b, "Something true, told at Bond 65.",
                     legacy=[("flag", "confided_" + _w), ("flag", "did_confide_" + _w)])

        ## Their ask (Bond 80): sb_activity sets did_stand_<who>.
        for _w, _t, _b in [
                ("yuji",   "Tell Them",                    "bg rooftop"),
                ("megumi", "Every Three Weeks",            "bg town_street"),
                ("nobara", "Out Loud, for Years",          "bg courtyard"),
                ("maki",   "The Four Seconds After",       "bg dojo"),
                ("panda",  "Two People Is the Difference", "bg dorm_common"),
                ("toge",   "Speak Instead",                "bg rooftop"),
                ("shoko",  "The Empty Line",               "bg infirmary"),
                ("gojo",   "Say I'm Wrong",                "bg rooftop"),
                ("yaga",   "The Room",                     "bg office")]:
            _mem_act("stand", _w, _t, _b, "An ask, at Bond 80, after something true.",
                     legacy=[("flag", "did_stand_" + _w)])

        ## Romance and after (Nobara, Maki, Shoko). The flag prefix each scene
        ## (or sb_activity) sets, or None.
        for _aid, _hint, _prefix, _rows in [
                ("rom_town", "Into town together, at ♡ 30.", "town_date_", [
                    ("nobara", "You Carry the Bags",          "bg city"),
                    ("maki",   "After the List",              "bg town_street"),
                    ("shoko",  "A Different Coffee Place",    "bg city")]),
                ("rom_close", "Staying a while longer, at ♡ 45.", "close_", [
                    ("nobara", "Not Going Anywhere",          "bg rooftop night"),
                    ("maki",   "Six in the Morning",          "bg dojo"),
                    ("shoko",  "The Lamp Turned Down",        "bg infirmary night")]),
                ("rom_say", "Saying it, at ♡ 100.", "did_rom_say_", [
                    ("nobara", "In a Corridor",               "bg dorm_common night"),
                    ("maki",   "Then Ask Me",                 "bg dojo"),
                    ("shoko",  "Pass Me That Form",           "bg infirmary")]),
                ("int_night", "After saying it, at ♡ 110.", None, [
                    ("nobara", "The Spare Futon",             "bg girls_dorm night"),
                    ("maki",   "The Good Blanket",            "bg girls_dorm night"),
                    ("shoko",  "The Second Bed",              "bg infirmary night")]),
                ("int_morning", "After saying it, at ♡ 130.", None, [
                    ("nobara", "Very Loud Thoughts About Tea", "bg girls_dorm"),
                    ("maki",   "Awake Since Five",            "bg girls_dorm"),
                    ("shoko",  "Forty Minutes",               "bg your_room")]),
                ("int_day", "After saying it, at ♡ 150.", None, [
                    ("nobara", "A Four, Like a Medal",        "bg riverside"),
                    ("maki",   "The Point of a River",        "bg riverside"),
                    ("shoko",  "Days Like Before",            "bg riverside")]),
                ("int_after", "After saying it, at ♡ 175.", "talked_about_after_", [
                    ("nobara", "Big Window, Terrible Rent",   "bg rooftop evening"),
                    ("maki",   "Somewhere with a Garden",     "bg riverside evening"),
                    ("shoko",  "An Alongside",                "bg infirmary night")])]:
            for _w, _t, _b in _rows:
                _legacy = [("flag", _prefix + _w)] if _prefix else []
                if _aid == "rom_say":
                    _legacy.append(("together", _w))
                _mem_act(_aid, _w, _t, _b, _hint, legacy=_legacy)

    _mem_add_acts()

    ## --- Sana: her flashbacks, opened by places and things (D11) --------------------------
    ## "Nine Hundred Yen" and "The Thing She Told Me" are hers too (above).

    _mem("sana_mem_diner", "The Diner", "Sana", "sana_mem_diner", who=("sana",),
         unlock=("district", "yotsuka"), bg="bg diner",
         hint="A trip home might bring this back.")
    _mem("sana_mem_daisy", "The Daisy Clip", "Sana", "sana_mem_daisy", who=("sana",),
         unlock=("item", "daisy_clip"), bg="bg town_street",
         hint="Something of hers.")
    _mem("sana_mem_ranking", "The Teacher Ranking", "Sana", "sana_mem_ranking", who=("sana",),
         unlock=("flag", "oda_letter_read"), bg="bg classroom",
         hint="Someone she ranked first.")

    MEMORY_BY_ID = {m["id"]: m for m in MEMORIES}

    ## The labels the recorder notes as they play: every memory without args.
    MEMORY_LABELS = frozenset(m["label"] for m in MEMORIES if not m["args"])

    ## --- Seen rules -------------------------------------------------------------------

    def _mem_lookup(mem):
        if isinstance(mem, str):
            return MEMORY_BY_ID.get(mem)
        if isinstance(mem, dict):
            return MEMORY_BY_ID.get(mem.get("id"))
        return None

    def _mem_rule(rule):
        kind, arg = rule
        if kind == "label":
            return arg in store.memories_seen
        if kind == "event":
            return arg in store.done_events
        if kind == "flag":
            return has_flag(arg)
        if kind == "act":
            return arg in store.seen_acts
        if kind == "together":
            return arg in store.together
        if kind == "district":
            return arg in (getattr(store, "districts_visited", None) or ())
        if kind == "item":
            return bool(has_item(arg))
        return False

    def memory_seen(mem):
        """WP5. True when this save has seen the memory (for Sana's
        flashbacks: when its trigger is met)."""
        m = _mem_lookup(mem)
        if m is None:
            return False
        if m["unlock"] is not None:
            return _mem_rule(m["unlock"])
        if not m["args"] and m["label"] in store.memories_seen:
            return True
        return any(_mem_rule(r) for r in m["seen"])

    def memory_state(mem):
        """WP5. "seen" (replayable), "unseen" (a dark tile with its hint) or
        "later" (reached, but the scene is written in a later build)."""
        m = _mem_lookup(mem)
        if m is None or not memory_seen(m):
            return "unseen"
        if not renpy.has_label(m["label"]):
            return "later"
        return "seen"

    def memory_entry(mem):
        """WP5. A copy of the catalogue entry for the journal, plus "state"
        ("seen" / "unseen" / "later"), "is_seen" and "text": the hint on an
        unseen tile, "Written in a later build" on a later one, "" on a seen
        one."""
        m = _mem_lookup(mem)
        if m is None:
            return None
        e = dict(m)
        e["state"] = memory_state(m)
        e["is_seen"] = (e["state"] == "seen")
        e["text"] = {"seen": "", "later": MEMORY_LATER}.get(e["state"], m["hint"])
        return e

    def memories_with(who):
        """WP5. The memory_entry() of every memory with `who` in it, in
        catalogue order."""
        return [memory_entry(m) for m in MEMORIES if who in m["who"]]

    def memory_groups(mode):
        """WP5. [(group title, [entry])] for the Memories tab, each entry a
        memory_entry(). "person": Sana first, then the journal's cast order,
        then "Everyone else" (a memory with two people is in both groups).
        "act": Prologue, Act I-V, Bonds, Sana. Empty groups are left out."""
        out = []
        if mode == "person":
            people = list(MEMORY_PEOPLE)
            for m in MEMORIES:
                for w in m["who"]:
                    if w not in people:
                        people.append(w)
            for w in people:
                ms = [memory_entry(m) for m in MEMORIES if w in m["who"]]
                if ms:
                    out.append((CAST[w]["short"] if w in CAST else w.capitalize(), ms))
            rest = [memory_entry(m) for m in MEMORIES if not m["who"]]
            if rest:
                out.append((MEMORY_NOBODY, rest))
        else:
            for aid, title in MEMORY_ACTS:
                ms = [memory_entry(m) for m in MEMORIES if m["act"] == aid]
                if ms:
                    out.append((title, ms))
        return out

    def memory_counts():
        """WP5. (seen, total), as in "14 of 94 found". Seen counts the
        memories that can be replayed now."""
        return (sum(1 for m in MEMORIES if memory_state(m) == "seen"), len(MEMORIES))

    ## --- Recording (D6) ---------------------------------------------------------------

    def _mem_label_cb(name, abnormal):
        """WP5. config.label_callbacks: notes a catalogued label, with the day,
        the first time it plays in this save. Never during a replay (D6)."""
        if name not in MEMORY_LABELS or getattr(store, "_in_replay", None):
            return
        seen = getattr(store, "memories_seen", None)
        if seen is not None and name not in seen:
            seen[name] = store.day

    config.label_callbacks.append(_mem_label_cb)

    def record_act(aid, who):
        """WP5. Records that an activity scene was seen with someone; called
        by sb_activity after the scene (WP7). Never during a replay."""
        if getattr(store, "_in_replay", None):
            return
        key = "%s:%s" % (aid, who)
        if key not in store.seen_acts:
            store.seen_acts.add(key)

    ## --- Replay (D5) --------------------------------------------------------------------

    ## What a replayed scene starts with, copied from the save. The first list
    ## is 3.9's; the second is what the scenes also read (the day and who is
    ## where, for st_noise and the graded backgrounds), plus smoke_autoplay so
    ## that a harness replay plays its fights through. Everything else starts
    ## at its default, because the replay store is a clean one.
    MEMORY_SCOPE_KEYS = (
        "mc_name", "mc_surname", "flags", "roster", "bonds", "affection", "together",
        "threads", "technique", "grade", "control", "output", "insight", "ce", "ce_max",
        "hp", "hp_max", "stamina", "done_events", "here", "period",
    )
    MEMORY_SCOPE_EXTRA = (
        "day", "stamina_max", "gojo_today", "schedule_overrides", "companion", "arc",
        "tname", "merit", "gojo_in", "smoke_autoplay",
    )

    def _mem_copy(v):
        ## A deep copy that keeps the store's own (revertable) containers.
        if v is None or isinstance(v, (str, int, float, bool)):
            return v
        if isinstance(v, dict):
            return dict((k, _mem_copy(x)) for k, x in v.items())
        if isinstance(v, list):
            return list(_mem_copy(x) for x in v)
        if isinstance(v, (set, frozenset)):
            return set(_mem_copy(x) for x in v)
        if isinstance(v, tuple):
            return tuple(_mem_copy(x) for x in v)
        return _mem_copy_mod.deepcopy(v)

    def memory_scope(mem):
        """WP5. The variables a replay starts with: copies of the save's values
        (so nothing a scene does can reach the save), plus _mem_label and
        _mem_args for label mem_play."""
        m = _mem_lookup(mem)
        scope = {}
        for k in MEMORY_SCOPE_KEYS:
            scope[k] = _mem_copy(getattr(store, k, None))
        for k in MEMORY_SCOPE_EXTRA:
            if hasattr(store, k):
                scope[k] = _mem_copy(getattr(store, k))
        scope["_mem_label"] = m["label"] if m else None
        scope["_mem_args"] = tuple(m["args"]) if m else ()
        return scope

    class MemoryReplay(Replay):
        """WP5. Replay("mem_play", scope=memory_scope(mem), locked=False). The
        scope is copied from the save again each time the action runs, so a
        tile replayed twice starts from the save both times."""

        def __init__(self, mem_id):
            Replay.__init__(self, "mem_play", scope=memory_scope(mem_id), locked=False)
            self.mem_id = mem_id

        def __call__(self):
            self.scope = memory_scope(self.mem_id)
            return Replay.__call__(self)

    def memory_replay(mem):
        """WP5. The action that replays a memory: a Replay of label mem_play
        with locked=False (D5). NullAction() for a memory that can't be
        replayed (unknown, unseen, or its scene not written yet)."""
        m = _mem_lookup(mem)
        if m is None or memory_state(m) != "seen":
            return NullAction()
        return MemoryReplay(m["id"])

    ## --- Migration 65, the memory part (3.12) -------------------------------------------

    def _migrate_65_memories():
        """WP5, migration 65. A settled save has played the whole prologue, so
        its memories are marked seen (day 0). A save still in the prologue has
        seen every step before the one it resumes at. Idempotent: it only adds
        what is missing."""
        if has_flag("settled_in"):
            upto = len(MEMORY_PROLOGUE_ORDER)
        else:
            point = store.story_point or legacy_story_point()
            point = {"chapter_one": "ch1_diner", "chapter_two": "ch2_arrival"}.get(point, point)
            if point in ("arc_one_open", "sandbox"):
                upto = len(MEMORY_PROLOGUE_ORDER)
            elif point in MEMORY_PROLOGUE_ORDER:
                upto = MEMORY_PROLOGUE_ORDER.index(point)
            else:
                upto = 0
        for lab in MEMORY_PROLOGUE_ORDER[:upto]:
            if lab not in store.memories_seen:
                store.memories_seen[lab] = 0

    register_migration(65, _migrate_65_memories, "WP5: prologue memories backfill")

    ## --- The validator (lint) ------------------------------------------------------------

    def _validate_memories():
        out = []
        acts = [a for a, t in MEMORY_ACTS]
        ids = set()
        for m in MEMORIES:
            i = m["id"]
            if i in ids:
                out.append("memory %r is catalogued twice" % i)
            ids.add(i)
            lab = m["label"]
            if (not renpy.has_label(lab) and lab not in MEMORY_PENDING_LABELS
                    and lab not in MEMORY_UNWRITTEN_LABELS):
                out.append("memory %r: label %s does not exist" % (i, lab))
            if m["act"] not in acts:
                out.append("memory %r: unknown act %r" % (i, m["act"]))
            for w in m["who"]:
                if w not in CAST:
                    out.append("memory %r: %r is not in CAST" % (i, w))
            if m["args"] and renpy.has_label(lab):
                params = renpy.game.script.lookup(lab).parameters
                n = len(params.parameters) if params is not None else 0
                if n < len(m["args"]):
                    out.append("memory %r: label %s takes %d argument(s), given %d" % (i, lab, n, len(m["args"])))
            if not m["seen"]:
                out.append("memory %r has no seen rule" % i)
            for r in m["seen"]:
                if not (isinstance(r, tuple) and len(r) == 2 and r[0] in MEMORY_RULE_KINDS):
                    out.append("memory %r: bad seen rule %r" % (i, r))
            u = m["unlock"]
            if u is not None and not (isinstance(u, tuple) and len(u) == 2 and u[0] in MEMORY_UNLOCK_KINDS):
                out.append("memory %r: bad unlock rule %r" % (i, u))
            if not m["title"] or not m["hint"]:
                out.append("memory %r needs a title and a hint" % i)
            if not renpy.has_image(m["bg"], exact=True):
                out.append("memory %r: background %r does not exist" % (i, m["bg"]))
        hangouts = [m for m in MEMORIES if m["act"] == "Bonds" and not m["args"]]
        if len(hangouts) != 25:
            out.append("expected the 25 hangouts (D37), catalogued %d" % len(hangouts))
        return out

    register_validator(_validate_memories)


## WP5. Every replay enters here (Replay("mem_play", ...), D5): it calls
## _mem_label with _mem_args, and the return ends the replay. Outside a
## replay it just returns.
label mem_play:
    if _in_replay and renpy.has_label(getattr(store, "_mem_label", None) or ""):
        call expression _mem_label pass (*_mem_args)
    return


## WP5's state (3.11).
default memories_seen = {}   # label -> the day it first played (0 = backfilled)
default seen_acts = set()    # "aid:who" for every activity scene seen (record_act)
