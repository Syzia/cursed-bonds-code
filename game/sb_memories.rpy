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
##        unlock=None, bg, place=None, stage=None)
##   act      "Prologue", "I".."V", "Bonds" or "Sana"
##   bg       the tile's picture (an image name)
##   place    None, or (location, period): where the scene happens. A replay
##            sets `here` and `period` to it and opens on graded_bg() of it,
##            for scenes that draw the place they are played in (graded_bg(),
##            who_is_here()) or that start without a scene of their own.
##   stage    None, or the image a replay opens on when it isn't the tile's
##            bg. Without a place, a replay opens on stage or bg; a scene
##            that sets its own background replaces it at once.
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
## memory_entry() with "state" ("seen" / "unseen" / "later"), "seen" and
## "is_seen" (both True only when the tile can be replayed) and "text" (the
## hint, or "Written in a later build"); memory_replay(m) is the tile's
## action; memories_with(who) gives one person's memories. In a tile the
## catalogue's rules are under "seen_rules", so "seen" can be tested as is.
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

    ## The hint on an unseen Bonds tile with someone the player hasn't met,
    ## so the tab doesn't name them before the People tab does.
    MEMORY_UNMET_HINT = "Someone you haven't met yet."

    ## Labels other wave-1 packages add, one set per package: the prologue's
    ## sub-labels (WP9, D39) and the two new story scenes (WP3). A set is
    ## pending only while none of its labels exists: the validator lets a
    ## pending set be missing, and once one label of a set has landed it
    ## requires the whole set, so the exemption ends by itself when the
    ## package merges. The journal shows a missing label as "later".
    MEMORY_PENDING_SETS = (
        ("WP9", frozenset(["ch1_diner", "ch1_the_thing", "ch1_gojo", "ch2_arrival",
                           "ch2_the_veil", "ch2_yaga", "ch2_first_years"])),
        ("WP3", frozenset(["st_utahime_office", "st_promotion_g3"])),
    )
    MEMORY_PENDING_LABELS = frozenset().union(*[s for p, s in MEMORY_PENDING_SETS])

    def _mem_pending_labels(has_label=None):
        """WP5. The labels the validator may find missing right now: every
        set of MEMORY_PENDING_SETS none of whose labels exists yet."""
        has_label = has_label or renpy.has_label
        out = set()
        for pkg, labs in MEMORY_PENDING_SETS:
            if not any(has_label(l) for l in labs):
                out |= labs
        return frozenset(out)

    ## Sana's flashbacks are written in phase 4 (D11).
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

    def _mem(id, title, act, label, who=(), args=(), seen=None, hint="", unlock=None, bg="bg black",
             place=None, stage=None):
        MEMORIES.append(dict(id=id, title=title, who=tuple(who), act=act, label=label,
                             args=tuple(args), seen=list(seen or [("label", label)]),
                             hint=hint, unlock=unlock, bg=bg, place=place, stage=stage))

    def _mem_story(label, title, act, who, bg, hint, flags=(), place=None):
        ## A main-story row: seen once its label has played or its event is
        ## done, or (old saves) once a flag the scene sets is set.
        _mem(label, title, act, label, who=who, bg=bg, hint=hint, place=place,
             seen=[("label", label), ("event", label)] + [("flag", f) for f in flags])

    ## --- The prologue (D39) ------------------------------------------------------
    ## Seen once its label plays, or once the save has settled in: every
    ## settled save played the whole prologue, including the step an old save
    ## was loaded in the middle of (whose label ran before the save was made).

    def _mem_pro(label, title, who, bg, stage=None):
        _mem(label, title, "Prologue", label, who=who, bg=bg, stage=stage, hint="The prologue.",
             seen=[("label", label), ("flag", "settled_in")])

    _mem_pro("ch1_diner", "Nine Hundred Yen", ("sana",), "bg diner")
    _mem_pro("ch1_the_thing", "The Thing She Told Me", ("sana",), "bg alley")
    _mem_pro("ch1_gojo", "The Man in the Blindfold", ("gojo",), "bg alley dark")
    _mem_pro("chapter_one_b", "The Offer", ("gojo",), "bg alley")
    ## Gojo's four lines play in the konbini, before the scene moves home.
    _mem_pro("ch1b_goodbye", "Breakfast for Four", ("gojo",), "bg home_living", stage="bg konbini")
    _mem_pro("ch2_arrival", "The Strongest of Today", ("gojo", "ijichi"), "bg gate")
    _mem_pro("ch2_the_veil", "The Veil on the Ridge", ("gojo",), "bg ridge_veil")
    _mem_pro("ch2_yaga", "Why Are You Here?", ("yaga",), "bg office")
    _mem_pro("ch2_first_years", "Three First-Years", ("yuji", "megumi", "nobara"), "bg training")

    ## --- The main story: every written story row (3.6.1) --------------------------
    ## The hints are the rows' objectives. The Sun Mall row plays as two
    ## scenes, recorded through their own labels; old saves read the row's
    ## closing flag sunmall_done and each chapter's own flags. Not the row's
    ## event: play_event marks ev_mission_sunmall done before Yaga's briefing
    ## starts, so the chapters would open before either has played.

    _mem_story("st_roll_call", "Roll Call", "I", ("yaga", "yuji", "megumi", "nobara"),
               "bg classroom", "Roll call with Principal Yaga.", flags=("roll_call",))
    _mem_story("st_utahime_office", "The Room Next to Yaga's", "I", ("utahime",),
               "bg utahime_office", "Someone is moving into the room next to Yaga's.",
               flags=("utahime_arrived",))
    _mem("chapter_four", "Kawagoe Sun Mall", "I", "chapter_four",
         who=("yuji", "megumi", "nobara", "ijichi"), bg="bg city",
         hint="Yaga has a mission for the first-years.",
         seen=[("label", "chapter_four"), ("flag", "sunmall_done")]
              + [("flag", f) for f in ("read_wall", "ignored_wall", "scouted_corridor", "saved_civilian",
                                       "fought_first", "climax_strong", "climax_thin")])
    _mem("chapter_five", "What Should Have Happened", "I", "chapter_five",
         who=("yaga", "gojo"), bg="bg rooftop evening", hint="After the Sun Mall.",
         seen=[("label", "chapter_five"), ("flag", "sunmall_done")]
              + [("flag", f) for f in ("end_committed", "end_honest", "end_turned_it_around")])
    _mem_story("st_aftermath", "Cursed-Energy Debt", "I", ("shoko",),
               "bg infirmary", "Shoko wants to look at all four of us.", flags=("aftermath_done",))
    _mem_story("st_kurose", "Four Forms and Nine Minutes", "I", (),
               "bg office", "A man from auxiliary management wants a word.",
               flags=("kurose_met",))

    _mem_story("st_second_years", "Nobody Cares About the Technique", "II", ("maki", "panda", "toge", "yuji"),
               "bg training", "The second-years are back from wherever they were.",
               flags=("met_second_years",))
    ## st_noise picks its ally from who is around (who_is_here()) and plays in
    ## the evening, so a replay stands in the courtyard at Evening.
    _mem_story("st_noise", "Something Eating the Lights", "II", ("ijichi",),
               "bg courtyard", "Something is wrong on campus after dark.", place=("courtyard", "Evening"))
    _mem_story("st_oda_letter", "A Letter from Oda-sensei", "II", (),
               "bg your_room night", "A letter is on its way from home.", flags=("oda_letter_read",))
    _mem_story("st_intensive", "Eleven Minutes", "II", ("gojo",),
               "bg ridge", "Gojo wants eleven minutes of my time.", flags=("intensive_done",))
    _mem("st_promotion_g3", "Grade Three, with Maki Watching", "II", "st_promotion_g3",
         who=("maki",), bg="bg training", hint="The promotion fight, once the merit is there.")

    ## The Nade missions open with Yaga's briefing over the office, where the
    ## board hands them out, before their first scene.
    _mem_story("ms_nade_1", "Sixty-One Surveys", "III", ("yaga", "yuji", "megumi", "nobara"),
               "bg city", "Yaga has a name.", flags=("nade_named",), place=("office", "Morning"))
    _mem_story("st_kurose_2", "Under My Door", "III", (),
               "bg your_room night", "Something from Kurose is waiting in my room.", flags=("kurose_leak",))
    _mem_story("ms_nade_2", "The Annexe", "III", ("yaga",),
               "bg ruin", "Yaga wants the annexe looked at.", flags=("nade_traced",), place=("office", "Morning"))
    _mem_story("st_oda_2", "Counted Twice", "III", ("yaga",),
               "bg your_room night", "Oda-sensei writes back.", flags=("oda_thread_open",))
    _mem_story("ms_nade_3", "A Flat in Toda", "III", ("yaga",),
               "bg town_street", "Yaga knows where Nade is.", flags=("nade_map",), place=("office", "Morning"))

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
    ##
    ## In normal play most of these scenes borrow the place view they are
    ## started from: act_confide, act_rom_close, act_rom_say and act_int_after
    ## run no `scene` of their own, and act_stand, act_int_night and
    ## act_int_morning draw graded_bg() of wherever the player stands. So each
    ## gets a place, (location, period), where it is set: the replay stands
    ## there, and the tile shows the same picture (bg_name() of the place).
    ## act_rom_town and act_int_day set their own scene and keep a plain bg.

    def _mem_act(aid, who, title, hint, legacy=(), place=None, bg=None):
        _mem("%s:%s" % (aid, who), title, "Bonds", "act_" + aid, who=(who,), args=(who,),
             bg=bg or bg_name(*place), place=place, hint=hint,
             seen=[("act", "%s:%s" % (aid, who))] + list(legacy))

    def _mem_add_acts():
        ## Something true (Bond 65): the scene sets confided_<who>, sb_activity
        ## did_confide_<who>. Written for these nine.
        for _w, _t, _p in [
                ("yuji",   "The Whole Trick",              ("rooftop", "Evening")),
                ("megumi", "The Fight I Lost",             ("forest", "Afternoon")),
                ("nobara", "Under the Paper",              ("courtyard", "Afternoon")),
                ("maki",   "The Boring Part",              ("dojo", "Morning")),
                ("panda",  "The Boy in the Car",           ("dorm_common", "Evening")),
                ("toge",   "Sitting Here Instead",         ("rooftop", "Night")),
                ("shoko",  "The Sitting on the Roof",      ("infirmary", "Night")),
                ("gojo",   "Enough, Together",             ("rooftop", "Night")),
                ("yaga",   "Not Knowing Is the Condition", ("office", "Morning"))]:
            _mem_act("confide", _w, _t, "Something true, told at Bond 65.", place=_p,
                     legacy=[("flag", "confided_" + _w), ("flag", "did_confide_" + _w)])

        ## Their ask (Bond 80): sb_activity sets did_stand_<who>.
        for _w, _t, _p in [
                ("yuji",   "Tell Them",                    ("rooftop", "Afternoon")),
                ("megumi", "Every Three Weeks",            ("forest", "Afternoon")),
                ("nobara", "Out Loud, for Years",          ("courtyard", "Afternoon")),
                ("maki",   "The Four Seconds After",       ("dojo", "Morning")),
                ("panda",  "Two People Is the Difference", ("dorm_common", "Afternoon")),
                ("toge",   "Speak Instead",                ("rooftop", "Afternoon")),
                ("shoko",  "The Empty Line",               ("infirmary", "Afternoon")),
                ("gojo",   "Say I'm Wrong",                ("rooftop", "Noon")),
                ("yaga",   "The Room",                     ("office", "Morning"))]:
            _mem_act("stand", _w, _t, "An ask, at Bond 80, after something true.", place=_p,
                     legacy=[("flag", "did_stand_" + _w)])

        ## Romance and after (Nobara, Maki, Shoko). The flag prefix each scene
        ## (or sb_activity) sets, or None; then per person a title and a place
        ## (location, period), or a plain bg for a scene that sets its own.
        ## Nobara's "In a Corridor" is the girls' dormitory corridor, at night.
        for _aid, _hint, _prefix, _rows in [
                ("rom_town", "Into town together, at ♡ 30.", "town_date_", [
                    ("nobara", "You Carry the Bags",          "bg city"),
                    ("maki",   "After the List",              "bg town_street"),
                    ("shoko",  "A Different Coffee Place",    "bg city")]),
                ("rom_close", "Staying a while longer, at ♡ 45.", "close_", [
                    ("nobara", "Not Going Anywhere",          ("rooftop", "Night")),
                    ("maki",   "Six in the Morning",          ("dojo", "Morning")),
                    ("shoko",  "The Lamp Turned Down",        ("infirmary", "Night"))]),
                ("rom_say", "Saying it, at ♡ 100.", "did_rom_say_", [
                    ("nobara", "In a Corridor",               ("girls_dorm", "Night")),
                    ("maki",   "Then Ask Me",                 ("dojo", "Afternoon")),
                    ("shoko",  "Pass Me That Form",           ("infirmary", "Afternoon"))]),
                ("int_night", "After saying it, at ♡ 110.", None, [
                    ("nobara", "The Spare Futon",             ("girls_dorm", "Night")),
                    ("maki",   "The Good Blanket",            ("girls_dorm", "Night")),
                    ("shoko",  "The Second Bed",              ("infirmary", "Night"))]),
                ("int_morning", "After saying it, at ♡ 130.", None, [
                    ("nobara", "Very Loud Thoughts About Tea", ("girls_dorm", "Morning")),
                    ("maki",   "Awake Since Five",            ("girls_dorm", "Morning")),
                    ("shoko",  "Forty Minutes",               ("dorm", "Morning"))]),
                ("int_day", "After saying it, at ♡ 150.", None, [
                    ("nobara", "A Four, Like a Medal",        "bg riverside"),
                    ("maki",   "The Point of a River",        "bg riverside"),
                    ("shoko",  "Days Like Before",            "bg riverside")]),
                ("int_after", "After saying it, at ♡ 175.", "talked_about_after_", [
                    ("nobara", "Big Window, Terrible Rent",   ("rooftop", "Evening")),
                    ("maki",   "Somewhere with a Garden",     ("riverside", "Evening")),
                    ("shoko",  "An Alongside",                ("infirmary", "Night"))])]:
            for _w, _t, _where in _rows:
                _legacy = [("flag", _prefix + _w)] if _prefix else []
                if _aid == "rom_say":
                    _legacy.append(("together", _w))
                if isinstance(_where, tuple):
                    _mem_act(_aid, _w, _t, _hint, legacy=_legacy, place=_where)
                else:
                    _mem_act(_aid, _w, _t, _hint, legacy=_legacy, bg=_where)

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

    def _mem_met(who):
        """WP5. Whether the player has met someone, by the journal cast's met
        rule (3.6.2: ("roster",), ("flag", name) or ("always",)); anyone
        without one counts as met once in the roster. Sana always counts."""
        if who == "sana":
            return True
        rule = None
        for c in (getattr(store, "JOURNAL_CAST", None) or ()):
            if isinstance(c, dict) and c.get("who") == who:
                rule = c.get("met")
                break
        if isinstance(rule, (tuple, list)) and rule:
            if rule[0] == "always":
                return True
            if rule[0] == "flag" and len(rule) > 1:
                return has_flag(rule[1])
        return who in (store.roster or ())

    def memory_entry(mem):
        """WP5. A copy of the catalogue entry for the journal, plus "state"
        ("seen" / "unseen" / "later"), "seen" and "is_seen" (True only when
        the tile can be replayed; the catalogue's rules move to "seen_rules")
        and "text": the hint on an unseen tile (a generic one on a Bonds tile
        with someone not met yet), "Written in a later build" on a later one,
        "" on a seen one."""
        m = _mem_lookup(mem)
        if m is None:
            return None
        e = dict(m)
        e["state"] = memory_state(m)
        e["is_seen"] = (e["state"] == "seen")
        e["seen_rules"] = m["seen"]
        e["seen"] = e["is_seen"]
        hint = m["hint"]
        if m["act"] == "Bonds" and not all(_mem_met(w) for w in m["who"]):
            hint = MEMORY_UNMET_HINT
        e["text"] = {"seen": "", "later": MEMORY_LATER}.get(e["state"], hint)
        return e

    def memories_with(who):
        """WP5. The memory_entry() of every memory with `who` in it, in
        catalogue order."""
        return [memory_entry(m) for m in MEMORIES if who in m["who"]]

    def memory_groups(mode):
        """WP5. [(group title, [entry])] for the Memories tab, each entry a
        memory_entry(). "person": Sana first, then the journal's cast order,
        then "Everyone else" (a memory with two people is in both groups);
        someone not met yet has no group until one of their memories is
        reached. "act": Prologue, Act I-V, Bonds, Sana. Empty groups are
        left out."""
        out = []
        if mode == "person":
            people = list(MEMORY_PEOPLE)
            for m in MEMORIES:
                for w in m["who"]:
                    if w not in people:
                        people.append(w)
            for w in people:
                ms = [memory_entry(m) for m in MEMORIES if w in m["who"]]
                if ms and (_mem_met(w) or any(e["state"] != "unseen" for e in ms)):
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
    ## where, for st_noise and the graded backgrounds), what the seen rules
    ## read (so a journal opened inside a replay shows the save's memories;
    ## the recorder does nothing there, and these are copies anyway), plus
    ## smoke_autoplay so that a harness replay plays its fights through.
    ## Everything else starts at its default: the replay store is a clean one.
    MEMORY_SCOPE_KEYS = (
        "mc_name", "mc_surname", "flags", "roster", "bonds", "affection", "together",
        "threads", "technique", "grade", "control", "output", "insight", "ce", "ce_max",
        "hp", "hp_max", "stamina", "done_events", "here", "period",
    )
    MEMORY_SCOPE_EXTRA = (
        "day", "stamina_max", "gojo_today", "schedule_overrides", "companion", "arc",
        "tname", "merit", "gojo_in", "memories_seen", "seen_acts", "inventory",
        "districts_visited", "smoke_autoplay",
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
        _mem_args for label mem_play, and what the replay opens on:
        _mem_place (the memory's place, which also sets here and period) and
        _mem_bg (its stage or tile picture)."""
        m = _mem_lookup(mem)
        scope = {}
        for k in MEMORY_SCOPE_KEYS:
            scope[k] = _mem_copy(getattr(store, k, None))
        for k in MEMORY_SCOPE_EXTRA:
            if hasattr(store, k):
                scope[k] = _mem_copy(getattr(store, k))
        scope["_mem_label"] = m["label"] if m else None
        scope["_mem_args"] = tuple(m["args"]) if m else ()
        place = m.get("place") if m else None
        scope["_mem_place"] = tuple(place) if place else None
        scope["_mem_bg"] = (m.get("stage") or m["bg"]) if m else None
        if place:
            scope["here"], scope["period"] = place
        return scope

    class MemoryReplay(Replay):
        """WP5. Replay("mem_play", scope=memory_scope(mem), locked=False). The
        action holds only the memory's id: the scope is copied from the save
        when the action runs (so a tile replayed twice starts from the save
        both times) and dropped when the replay ends, so building and
        comparing the journal's tiles stays cheap."""

        def __init__(self, mem_id):
            Replay.__init__(self, "mem_play", scope={}, locked=False)
            self.mem_id = mem_id

        def __call__(self):
            if getattr(store, "_in_replay", None):
                return None
            self.scope = memory_scope(self.mem_id)
            try:
                return Replay.__call__(self)
            finally:
                self.scope = {}

    def memory_replay(mem):
        """WP5. The action that replays a memory: a Replay of label mem_play
        with locked=False (D5). NullAction() for a memory that can't be
        replayed (unknown, unseen, or its scene not written yet), and inside
        a replay, so one replay never starts another."""
        m = _mem_lookup(mem)
        if m is None or getattr(store, "_in_replay", None) or memory_state(m) != "seen":
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
        pending = _mem_pending_labels()
        ids = set()
        for m in MEMORIES:
            i = m["id"]
            if i in ids:
                out.append("memory %r is catalogued twice" % i)
            ids.add(i)
            lab = m["label"]
            if (not renpy.has_label(lab) and lab not in pending
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
            p = m.get("place")
            if p is not None and not (isinstance(p, tuple) and len(p) == 2
                                      and p[0] in LOCATIONS and p[1] in PERIODS):
                out.append("memory %r: bad place %r" % (i, p))
            if m.get("stage") and not renpy.has_image(m["stage"], exact=True):
                out.append("memory %r: stage %r does not exist" % (i, m["stage"]))
        hangouts = [m for m in MEMORIES if m["act"] == "Bonds" and not m["args"]]
        if len(hangouts) != 25:
            out.append("expected the 25 hangouts (D37), catalogued %d" % len(hangouts))
        return out

    register_validator(_validate_memories)


## WP5. Every replay enters here (Replay("mem_play", ...), D5): it opens on
## the memory's place (graded for its hour) or its picture, since a replay
## starts with nothing on screen and several scenes borrow the view they are
## played from; then it calls _mem_label with _mem_args, and the return ends
## the replay. A scene that sets its own background replaces the opening one.
## Outside a replay it just returns.
label mem_play:
    if _in_replay and renpy.has_label(getattr(store, "_mem_label", None) or ""):
        if getattr(store, "_mem_place", None):
            scene expression graded_bg(_mem_place[0], _mem_place[1])
        elif getattr(store, "_mem_bg", None):
            scene expression _mem_bg
        call expression _mem_label pass (*_mem_args)
    return


## WP5's state (3.11).
default memories_seen = {}   # label -> the day it first played (0 = backfilled)
default seen_acts = set()    # "aid:who" for every activity scene seen (record_act)
