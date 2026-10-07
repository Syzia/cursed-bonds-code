################################################################################
## Cursed Bonds — sandbox interface: the place view and the person view.
##
## WP7 (PHASE1_DESIGN.md 4.4, 4.5); phase 2, P2 (PHASE2_DESIGN.md 4.4, 4.6, D19,
## D19b): the icon column in the place view, the lighter person view, and
## captions that follow the story (AMBIENT_STORY).
##
## Screens return tuples to sb_loop.rpy:
##   sb_place  ("map",) ("journal", tab) ("char", who) ("act", id)
##             ("mission", mid) ("dev",) ("hot", id)
##   sb_char   ("do", aid, who) ("mission", mid) ("act", id) ("cancel",)
## Nothing here changes game state.
##
## The HUD and the toasts are in ui_hud.rpy, the map in ui_map.rpy, and the
## journal in ui_journal.rpy. What someone is doing at a place (AMBIENT), how
## big people stand in each place (PLACE_STAGING) and the face they look up
## with (PERSON_GREET_EXPR) are tables below: add a row, no code.
################################################################################

init python:
    import builtins
    import time as _sb_time

    ## What people are doing (4.4) -------------------------------------------------
    ##
    ## (who, place) -> (caption, expression). (who, None) is that person's
    ## caption anywhere else. Expressions: neutral / happy / serious / angry /
    ## surprised / sad.

    AMBIENT = {
        ("yuji", "cafeteria"):      ("halfway through an enormous bowl", "happy"),
        ("yuji", "courtyard"):      ("at the vending machine", "neutral"),
        ("megumi", "classroom"):    ("reading", "serious"),
        ("megumi", "library"):      ("three books deep", "serious"),
        ("megumi", "forest"):       ("with a Divine Dog", "neutral"),
        ("megumi", "riverside"):    ("with a Divine Dog", "neutral"),
        ("nobara", "dorm_common"):  ("on her phone", "neutral"),
        ("nobara", "rooftop"):      ("leaning on the railing", "neutral"),
        ("maki", "training"):       ("drilling with a staff", "serious"),
        ("maki", "dojo"):           ("drilling with a staff", "serious"),
        ("panda", "courtyard"):     ("sparring with Toge", "happy"),
        ("toge", "cafeteria"):      ("with onigiri", "happy"),
        ("gojo", "gojo_office"):    ("eating mochi in front of the TV", "happy"),
        ("gojo", "ridge"):          ("sitting just outside the veil", "serious"),
        ("utahime", None):          ("buried in paperwork", "serious"),
        ("shoko", None):            ("with coffee", "neutral"),
        ("yaga", "office"):         ("sewing a cursed doll", "serious"),
        ("ijichi", "gate"):         ("on the phone beside the car", "neutral"),

        ## The five yards between the buildings (D57).
        ("nobara", "training_yard"): ("on her way to the training hall", "neutral"),
        ("toge", "school_yard"):    ("on the steps, onigiri in hand", "happy"),
        ("megumi", "trailhead"):    ("with a Divine Dog, heading up", "neutral"),
        ("shoko", "staff_yard"):    ("on the steps with coffee", "neutral"),
        ("yuji", "dorm_yard"):      ("by the pond, counting stars out loud", "happy"),

        ## After checkpoint D: the second years' evening in the library.
        ("panda", "library"):       ("turning pages very carefully", "happy"),
        ("toge", "library"):        ("a book open, hands in his sleeves", "neutral"),

        ## After that: Panda's Night in the garden, beside Yuji and his stars.
        ## Keyed on the place, not the hour: it also shows by day when he is
        ## brought along, so it names no hour.
        ("panda", "dorm_yard"):     ("out in the open air, looking up", "happy"),

        ## Each person's fallback, anywhere else.
        ("yuji", None):             ("killing time, loudly", "happy"),
        ("megumi", None):           ("hands in his pockets", "neutral"),
        ("nobara", None):           ("waiting for something", "neutral"),
        ("maki", None):             ("a staff over one shoulder", "serious"),
        ("panda", None):            ("people-watching", "happy"),
        ("toge", None):             ("hands in his sleeves", "neutral"),
        ("gojo", None):             ("eating something sweet", "happy"),
        ("yaga", None):             ("arms folded", "serious"),
        ("ijichi", None):           ("checking his phone", "neutral"),
    }

    ## Anyone without a row at all.
    AMBIENT_FALLBACK = ("waiting for something", "neutral")

    ## Rows that name someone else: (who, place) -> (the person the caption
    ## needs, the caption while they're not there). The schedule never puts
    ## Toge in the courtyard when Panda is, so Panda usually waits.
    AMBIENT_NEEDS = {
        ("panda", "courtyard"): ("toge", ("waiting for a sparring partner", "happy")),
    }

    ## How big people stand in a place, and how far up (4.4). A place not
    ## listed uses zoom 0.52 and y 0.
    PLACE_STAGING = {
        "dorm":        dict(zoom=0.56, y=0),
        "infirmary":   dict(zoom=0.54, y=0),
        "rooftop":     dict(zoom=0.50, y=0),
        "gate":        dict(zoom=0.50, y=0),
        "forest":      dict(zoom=0.50, y=0),
        "riverside":   dict(zoom=0.50, y=0),
        "ridge":       dict(zoom=0.48, y=0),
    }

    ## The face someone looks up with when I walk over (4.4, 4.5, 5.1).
    PERSON_GREET_EXPR = {
        "yuji": "happy", "megumi": "neutral", "nobara": "happy", "maki": "serious",
        "panda": "happy", "toge": "happy", "gojo": "happy", "utahime": "serious",
        "shoko": "neutral", "yaga": "serious", "ijichi": "surprised",
    }

    EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")

    ## Where the stage puts 1-4 people (x centres, 4.4).
    STAGE_CENTRES = {1: [700], 2: [470, 930], 3: [330, 700, 1070], 4: [240, 540, 860, 1160]}

    ## Captions that follow the story (phase 2, D19b). Rows are (who, place or
    ## None for anywhere, condition, caption, expression), read before AMBIENT:
    ## the LAST row whose condition holds wins, so later rows are later in the
    ## story. A condition is a flag name, "thread:<who>:<n>" (their thread has
    ## reached stage n) or "grade:<who>:<key>" (they are at least that grade;
    ## "mc" is me). Phase 4 adds rows per act: add a row, no code.
    AMBIENT_STORY = [
        ("megumi", "classroom",   "sunmall_done",       "writing up the Sun Mall, slowly", "serious"),
        ("nobara", "dorm_common", "sunmall_done",       "re-taping the grip of her hammer", "neutral"),
        ("yaga",   "office",      "sunmall_done",       "reading the Sun Mall report again", "serious"),
        ("utahime", "utahime_office", "mission_board_open", "pinning new jobs to the board", "serious"),
        ("yuji",   "training",    "grade:yuji:g3",      "working a combination he couldn't do last month", "happy"),
        ("yuji",   "dorm_common", "thread:yuji:1",      "by the window, quiet for once", "neutral"),
        ("megumi", "classroom",   "thread:megumi:2",    "going back through Tsumiki's folder", "serious"),
        ("nobara", "dorm_common", "thread:nobara:1",    "scrolling through old photos", "neutral"),
        ("maki",   "dojo",        "thread:maki:1",      "drilling with a staff, a second one set out", "serious"),
        ("panda",  "dorm_common", "thread:panda:1",     "a bag of crisps open beside him", "happy"),
        ## After checkpoint D his evening is in the library: the crisps go
        ## with him. His Night is in the garden now, so the row above shows
        ## only when I bring him into the common room myself. The garden has
        ## no row: his thread's crisps are an evening, indoors.
        ("panda",  "library",     "thread:panda:1",     "a bag of crisps open under the table", "happy"),
        ("toge",   "cafeteria",   "thread:toge:1",      "lining up onigiri by filling", "happy"),
        ("shoko",  "infirmary",   "thread:shoko:1",     "with coffee, an old photo face down on the desk", "neutral"),
    ]

    def rail_story_ok(cond):
        """P2 (sb_screens.rpy). bool: an AMBIENT_STORY condition holds now: a
        flag name, "thread:<who>:<n>" or "grade:<who>:<key>"."""
        if cond.startswith("thread:"):
            _kind, who, n = cond.split(":")
            tid = next((t for t in THREAD_ORDER if THREADS[t]["who"] == who), None)
            return tid is not None and thread_stage(tid) >= int(n)
        if cond.startswith("grade:"):
            _kind, who, key = cond.split(":")
            g = player_grade() if who == "mc" else (npc_stats(who) or {}).get("grade")
            return grade_rank(g) >= grade_rank(key)
        return has_flag(cond)

    def rail_story_caption(who, loc):
        """P2 (sb_screens.rpy). (caption, expression) from the last
        AMBIENT_STORY row for this person and place whose condition holds,
        or None."""
        found = None
        for w, place, cond, cap, expr in AMBIENT_STORY:
            if w == who and (place is None or place == loc) and rail_story_ok(cond):
                found = (cap, expr)
        return found

    def ambient_of(who, loc):
        """WP7. (caption, expression) for someone at a place, e.g.
        ("halfway through an enormous bowl", "happy") (4.4). Phase 2: a
        caption that follows the story (AMBIENT_STORY) comes first. A
        caption that names someone else (AMBIENT_NEEDS) only shows while
        they're there. The second overhaul (D48): someone asleep is
        ("asleep", None), ahead of everything else."""
        if world_asleep(who):
            return ("asleep", None)
        story = rail_story_caption(who, loc)
        if story:
            return story
        row = AMBIENT.get((who, loc))
        need = AMBIENT_NEEDS.get((who, loc))
        if row and need and need[0] not in who_is_here(loc):
            return need[1]
        return row or AMBIENT.get((who, None)) or AMBIENT_FALLBACK

    def greet_expr(who):
        """WP7. The expression someone looks up with (PERSON_GREET_EXPR)."""
        return PERSON_GREET_EXPR.get(who, "neutral")

    def person_image(who, expr=None):
        """WP7. The image name "<who> <expr>", or plain "<who>" when that
        expression has no picture."""
        name = "%s %s" % (who, expr or greet_expr(who))
        return name if renpy.has_image(name) else who

    def stage_people(loc=None):
        """WP7. (on stage, overflow): who is at the place, the companion first,
        at most four on stage. The second overhaul (D48): nobody asleep
        (world_asleep) is on the stage or in the overflow, so every screen
        that draws, lists or offers people takes the rule from here."""
        folk = [w for w in who_is_here(loc) if not world_asleep(w)]
        c = store.companion
        if c in folk:
            folk.remove(c)
            folk.insert(0, c)
        return folk[:4], folk[4:]

    def stage_x(who, loc=None):
        """WP7. The x centre someone stands at in the place view (700 if
        they are not on the stage)."""
        ## Phase 2: the row's own x (view_stage.rpy), so someone painted
        ## into the room answers with their pose's centre, not a slot's.
        row = [r for r in view_stage_rows(loc or store.here) if r["who"] == who]
        return row[0]["x"] if row else 700

    ## Missions, as the screens draw them --------------------------------------------

    def _mget(rec, key, default=None):
        if isinstance(rec, dict):
            return rec.get(key, default)
        return getattr(rec, key, default)

    def mission_view(m):
        """WP7. (mid, title, hint) for an entry of missions_here() or
        missions_with(), which may be a mission id or a mission record."""
        if isinstance(m, str):
            rec = (getattr(store, "MISSION_BY_ID", None) or {}).get(m)
            mid = m
        else:
            rec = m
            mid = _mget(m, "id")
        title = (_mget(rec, "title") if rec is not None else None) or builtins.str(mid)
        hint = ""
        if rec is not None:
            hint = _mget(rec, "objective") or _mget(rec, "summary") or ""
        return mid, title, hint

    ## The action card (4.4) ---------------------------------------------------------

    def place_actions(loc):
        """WP7. (id, label, hint, period_cost) for everything I can do here
        (4.4): the place's own actions, Hold the hour, the registered actions
        (registered_place_actions), then Wait. Once-a-day actions drop out
        once used (D26). Explore mode: the Time step and explore actions."""
        if store.explore_mode:
            nxt = PERIODS[(PERIODS.index(store.period) + 1) % len(PERIODS)]
            return ([("explore_time", "Time: %s" % nxt, "Step to the next time of day. Nothing is spent.", 0)]
                    + registered_place_actions(loc))
        done = store.actions_today
        a = []
        if loc == "dorm":
            a.append(("sleep", "Sleep", "End the day. Everything comes back.", 0))
            a.append(("study", "Study", "Insight. Quiet. Nobody bothers me.", 1))
        if loc in ("training", "ridge", "forest", "dojo"):
            a.append(("train", "Train", "Push my cursed energy. Costs stamina.", 1))
        if loc == "riverside":
            a.append(("swim", "Swim", "Cold. Clears my head.", 1))
            a.append(("train", "Train", "Rough ground. Good footwork.", 1))
        if loc == "cafeteria":
            a.append(("eat", "Eat", "Stamina. Everyone's here at noon.", 0))
        if loc == "infirmary" and "rest" not in done:
            a.append(("rest", "Get patched up", "Rest, and Shoko if she's in. Once a day.", 0))
        if loc == "storehouse" and not has_flag("armory_open") and "racks" not in done:
            a.append(("tools", "Look through the racks", "Look, don't take. Once a day.", 0))
        if loc == "courtyard":
            a.append(("train", "Practice", "Forms, in the open, where people can see.", 1))
        if loc == "classroom":
            a.append(("study", "Study", "Insight. The textbook is four hundred pages.", 1))
        if loc == "rooftop":
            a.append(("think", "Sit a while", "Nothing happens. That's the point.", 1))
        if "hold" not in done:
            a.append(("hold", "Hold the hour", "Last Light. Once a day; costs reserve.", 0))
        a.extend(registered_place_actions(loc))
        a.append(("wait", "Wait", "Let the period pass.", 1))
        return a

    def rail_actions(loc):
        """P0 (sb_screens.rpy), final (PHASE2_DESIGN.md 6.1, D30). What the
        place view offers here, as a list of (id, label, hint, cost, icon,
        gold): place_actions(loc) as the night rule leaves it
        (night_filter_actions), without the actions a visible hotspot already
        offers (hot_covers), and then, when someone is tagging along, the
        row ("release", "Let them go", hint, 0, "release", False), last.
        place_actions() itself is unchanged."""
        covered = hot_covers(loc)
        out = []
        for a in night_filter_actions(loc, place_actions(loc)):
            if a[0] in covered:
                continue
            name = icon_for("act", a[0])
            out.append((a[0], a[1], a[2], a[3], name, name in ICON_GOLD))
        if store.companion:
            out.append(("release", "Let them go", "They go back to their own day.", 0, "release", False))
        return out

    ## The icon column (phase 2, 4.4) ------------------------------------------------
    ##
    ## 72 px tiles down the right edge, bottom up: x 1808 to 1880; a second
    ## column at x 1726 to 1798 when the first is full. The first column never
    ## rises above y 360; a column further left sits under the toast lane
    ## (x 1330 to 1790) and stops at y 430, so a stack of four two-line toasts
    ## (which ends near y 416) still clears it (R6).
    RAIL_TILE = 72
    RAIL_GAP = 10
    RAIL_BOTTOM = 1040
    RAIL_TOP = 360
    RAIL_TOP_INNER = 430
    RAIL_MAX = 8            # tiles in a column
    RAIL_MAX_WORDS = 6      # while icons show their words underneath
    RAIL_COLUMNS = 2        # a third column would stand on the stage (x 40 to 1700)
    RAIL_CARD_Y = 250       # the person view's card: its top edge
    RAIL_MORE_POS = (1400, 1040)    # the "+N" chip: its bottom left corner

    def rail_tip(label, hint="", cost=0):
        """P2 (sb_screens.rpy). A hover label's text: "Train\nPush my cursed
        energy. Costs stamina. · 1 period" (the name, then the hint and
        what it costs)."""
        tail = hint or ""
        if cost:
            tail = (tail + u" · " if tail else "") + ("1 period" if cost == 1 else "%d periods" % cost)
        return (label + "\n" + tail) if tail else label

    def rail_missions(loc):
        """P2 (sb_screens.rpy). [(mid, title, hint)]: the missions the place
        view offers here now. None in explore mode or on a rest day
        (night_can_work), and only the ones the night allows. The second
        overhaul (D48): not a mission whose giver is asleep (the frozen
        missions_here finds its giver in who_is_here, which counts a
        sleeper)."""
        if store.explore_mode or not night_can_work():
            return []
        out = []
        for m in missions_here(loc):
            mv = mission_view(m)
            if world_asleep(_mget(MISSION_BY_ID.get(mv[0]), "with_who") or _mget(MISSION_BY_ID.get(mv[0]), "who")):
                continue
            if night_allows("mission:" + mv[0], (MISSION_BY_ID.get(mv[0]) or {}).get("cost", 0)):
                out.append(mv)
        return out

    def rail_asleep_line(loc):
        """U0b (sb_screens.rpy; D48, K16). "" unless the only people in the
        place are asleep; then the one plain line the empty stage shows in
        place of "Nobody here right now.": "Megumi is asleep." Nothing more
        is said of a sleeper than that."""
        folk = [w for w in who_is_here(loc) if world_asleep(w)]
        if not folk or stage_people(loc)[0]:
            return ""
        names = [CAST[w]["short"] for w in folk]
        if len(names) == 1:
            return "%s is asleep." % names[0]
        return "%s and %s are asleep." % (", ".join(names[:-1]), names[-1])

    def rail_rows(loc):
        """P2 (sb_screens.rpy). The icon column's tiles, top to bottom, as
        plain tuples (returns, icon, gold, hover text, cost, id): the gold
        missions first, then rail_actions(loc) in its own order (the
        actions, Wait or Go to bed, and "Let them go" last). `returns` is
        ("mission", mid) or ("act", id); the id is unique in the column."""
        out = []
        seen = set()

        def wid(base):
            name, n = base, 2
            while name in seen:
                name = "%s_%d" % (base, n)
                n += 1
            seen.add(name)
            return name

        for mid, title, hint in rail_missions(loc):
            out.append((("mission", mid), "mission", True, rail_tip(title, hint), 0, wid("rail_m_%s" % mid)))
        for aid, label, hint, cost, name, gold in rail_actions(loc):
            ## At Night one of the night's own actions takes what is left of
            ## the night, not a period: no diamond and no "1 period".
            shown = 0 if (aid in NIGHT_OK and night_on() and night_is_night()) else cost
            out.append((("act", aid), name, gold, rail_tip(label, hint, shown), shown, wid("rail_%s" % aid)))
        return out

    def rail_word(row):
        """P2 (sb_screens.rpy). The word under a tile while icons show their
        words: an action's own name (the first line of its hover text:
        "Practice", not the icon's "Train"), so two actions that share an
        icon read differently; a mission keeps the icon's word."""
        if row[0][0] == "act":
            return row[3].split("\n")[0]
        return icon_label(row[1])

    def rail_height(name, pips=0, word=None, words=True):
        """P2 (sb_screens.rpy). How tall one tile is, at most: 72, or more
        while icons show their words: the icon, its diamonds, and 20 px for
        each line of the word (`word`, or the icon's own; a 72 px tile fits
        about nine letters a line). `words` False: the column has dropped
        its words (rail_layout), so 72."""
        if not words or not icon_words_shown(name):
            return RAIL_TILE
        lines, used = 1, 0
        for word in (word or icon_label(name)).split():
            if used and used + 1 + len(word) > 9:
                lines += 1
                used = 0
            used += len(word) + (1 if used else 0)
        return max(RAIL_TILE, 8 + 50 + (14 if pips else 0) + 2 + 20 * lines)

    def rail_columns(rows, words=True):
        """P2 (sb_screens.rpy). rail_rows() split into columns, the one at
        the screen's edge first; each keeps the rows' order, and the last
        rows (Wait, "Let them go") stay at the foot of the edge column. A
        column takes eight tiles (six while words show) and never more
        than fit under its top line (RAIL_TOP, RAIL_TOP_INNER). There is
        room for two columns (fifteen tiles): a third would stand on the
        stage, and p2_hud fails a room that needs one. `words` False
        lays the tiles out without their words (rail_layout)."""
        cap = RAIL_MAX_WORDS if words and any(icon_words_shown(r[1]) for r in rows) else RAIL_MAX
        cols, cur, used = [], [], 0
        for r in reversed(rows):
            room = RAIL_BOTTOM - (RAIL_TOP_INNER if cols else RAIL_TOP)
            h = rail_height(r[1], r[4], rail_word(r), words)
            if cur and (len(cur) >= cap or used + RAIL_GAP + h > room):
                cols.append(cur[::-1])
                cur, used = [], 0
            used += h + (RAIL_GAP if cur else 0)
            cur.append(r)
        if cur:
            cols.append(cur[::-1])
        return cols

    def rail_layout(rows):
        """P2 (sb_screens.rpy). (columns, words): rail_columns(rows), and
        whether the tiles carry their words. While icons show words the
        tiles are taller, and long names can ask for a third column, which
        would stand on the stage: the column then drops its words (the
        hover label still names each tile) so that fifteen tiles fit in
        two columns, as they do with pictures."""
        cols = rail_columns(rows)
        if len(cols) > RAIL_COLUMNS:
            return rail_columns(rows, words=False), False
        return cols, True

    def rail_chip(who):
        """P2 (sb_screens.rpy). (grade key or None, text or None) for the
        person view's chip: ("g2", None) reads "GRADE 2"; Gojo is ("sp",
        "Off the scale"); someone with no grade shows their role in a plain
        chip (None, "Doctor"); (None, None) draws nothing."""
        st = npc_stats(who) or {}
        if st.get("off_scale"):
            return ("sp", "Off the scale")
        if st.get("grade") is not None:
            return (st.get("grade"), None)
        return (None, st.get("role") or None)

    ## The arrival caption (4.3, D35) ------------------------------------------------
    ##
    ## Shown once per change of (day, period, here). The key lives outside the
    ## store (a builtins list made at init, never reassigned), so the caption
    ## also shows after a load.

    ARRIVAL = builtins.list([None, 0.0])
    ARRIVAL_IN, ARRIVAL_HOLD, ARRIVAL_OUT = 0.3, 2.5, 0.5

    def arrival_caption():
        """WP7. When the caption for the current (day, period, here) started
        (wall clock), or None once it has faded."""
        key = (store.day, store.period, store.here)
        now = _sb_time.time()
        if ARRIVAL[0] != key:
            if renpy.predicting():
                return None
            ARRIVAL[0] = key
            ARRIVAL[1] = now
        if now - ARRIVAL[1] < ARRIVAL_IN + ARRIVAL_HOLD + ARRIVAL_OUT:
            return ARRIVAL[1]
        return None

    def _arrival_reset():
        ARRIVAL[0] = None

    config.after_load_callbacks.append(_arrival_reset)

    def _arrival_fx_fn(t0):
        def fn(trans, st, at):
            age = _sb_time.time() - t0
            if age < ARRIVAL_IN:
                trans.alpha = age / ARRIVAL_IN
                return 0
            if age < ARRIVAL_IN + ARRIVAL_HOLD:
                trans.alpha = 1.0
                return ARRIVAL_IN + ARRIVAL_HOLD - age
            trans.alpha = max(0.0, 1.0 - (age - ARRIVAL_IN - ARRIVAL_HOLD) / ARRIVAL_OUT)
            return 0 if trans.alpha > 0 else None
        return fn

    def arrival_fx(t0):
        """WP7. Fades the arrival caption by the wall clock (0.3 in, 2.5
        held, 0.5 out)."""
        return Transform(function=_arrival_fx_fn(t0))

    ## The person view (4.5) -------------------------------------------------------------

    _YEAR_WORDS = {"1st year": "First-year", "2nd year": "Second-year", "3rd year": "Third-year"}

    def role_line(who):
        """WP7. "First-year · Grade 2", "Teacher · Off the scale", "Doctor"."""
        year = CAST.get(who, {}).get("year", "")
        year = _YEAR_WORDS.get(year, year)
        st = npc_stats(who) or {}
        if st.get("off_scale"):
            g = "Off the scale"
        elif st.get("grade") is not None:
            g = grade_label(st.get("grade"))
        else:
            return year or st.get("role", "")
        return " · ".join(p for p in (year, g) if p)

    def unlock_line(who):
        """WP7. The footer hint: "Closer: Sit out with them — at Bond 50"."""
        nx = next_unlock(who)
        if not nx:
            return ""
        return "Closer: %s — at %s" % (nx[1], nx[2])

    def person_thread(who):
        """WP7. (title, stage, stages) of someone's thread once it has
        started, or None."""
        tid = next((t for t in THREAD_ORDER if THREADS[t]["who"] == who), None)
        if not tid:
            return None
        stage = thread_stage(tid)
        if stage < 0:
            return None
        return THREADS[tid]["title"], stage, len(THREADS[tid]["stages"])

    ## The validator (WP7 task 5) -----------------------------------------------------

    def _validate_wp7_tables():
        out = []
        places = set(LOCATIONS)
        for (who, loc), (cap, expr) in AMBIENT.items():
            if who not in CAST:
                out.append("AMBIENT: %r is not a person" % who)
            if loc is not None and loc not in places:
                out.append("AMBIENT: %r is not a place" % loc)
            if expr not in EXPRESSIONS:
                out.append("AMBIENT (%s, %s): %r is not an expression" % (who, loc, expr))
            elif who in CAST and not renpy.has_image("%s %s" % (who, expr)):
                out.append("AMBIENT (%s, %s): no image '%s %s'" % (who, loc, who, expr))
        for (who, loc), (need, (cap, expr)) in AMBIENT_NEEDS.items():
            if (who, loc) not in AMBIENT:
                out.append("AMBIENT_NEEDS (%s, %s): no AMBIENT row" % (who, loc))
            if need not in CAST:
                out.append("AMBIENT_NEEDS (%s, %s): %r is not a person" % (who, loc, need))
            if expr not in EXPRESSIONS or not renpy.has_image("%s %s" % (who, expr)):
                out.append("AMBIENT_NEEDS (%s, %s): no image '%s %s'" % (who, loc, who, expr))
        for row in AMBIENT_STORY:
            if not (isinstance(row, tuple) and len(row) == 5):
                out.append("AMBIENT_STORY: %r is not (who, place, condition, caption, expression)" % (row,))
                continue
            who, loc, cond, cap, expr = row
            if who not in CAST:
                out.append("AMBIENT_STORY: %r is not a person" % who)
            if loc is not None and loc not in places:
                out.append("AMBIENT_STORY: %r is not a place" % loc)
            if not cap:
                out.append("AMBIENT_STORY (%s, %s): no caption" % (who, loc))
            if expr not in EXPRESSIONS or (who in CAST and not renpy.has_image("%s %s" % (who, expr))):
                out.append("AMBIENT_STORY (%s, %s): no image '%s %s'" % (who, loc, who, expr))
            bits = str(cond).split(":")
            if bits[0] == "thread" and len(bits) == 3:
                tid = next((t for t in THREAD_ORDER if THREADS[t]["who"] == bits[1]), None)
                if tid is None or not bits[2].isdigit() or int(bits[2]) >= len(THREADS[tid]["stages"]):
                    out.append("AMBIENT_STORY (%s, %s): %r names no thread stage" % (who, loc, cond))
            elif bits[0] == "grade" and len(bits) == 3:
                if bits[2] not in GRADES or not (bits[1] == "mc" or bits[1] in NPC_BASE):
                    out.append("AMBIENT_STORY (%s, %s): %r names no grade" % (who, loc, cond))
                elif bits[1] != "mc" and NPC_BASE[bits[1]].get("grade") is None:
                    ## Shoko, Ijichi: grade_rank(None) is -1, so the row could never hold.
                    out.append("AMBIENT_STORY (%s, %s): %r names someone with no grade" % (who, loc, cond))
            elif len(bits) != 1 or not cond:
                out.append("AMBIENT_STORY (%s, %s): %r is not a flag, thread:<who>:<n> or grade:<who>:<key>" % (who, loc, cond))
        for loc, st in PLACE_STAGING.items():
            if loc not in places:
                out.append("PLACE_STAGING: %r is not a place" % loc)
            if set(st) - {"zoom", "y"}:
                out.append("PLACE_STAGING %s: unknown keys %r" % (loc, sorted(set(st) - {"zoom", "y"})))
        for who, expr in PERSON_GREET_EXPR.items():
            if who not in CAST:
                out.append("PERSON_GREET_EXPR: %r is not a person" % who)
            elif expr not in EXPRESSIONS or not renpy.has_image("%s %s" % (who, expr)):
                out.append("PERSON_GREET_EXPR: no image '%s %s'" % (who, expr))
        for who in ROSTER_ORDER:
            if who not in PERSON_GREET_EXPR:
                out.append("PERSON_GREET_EXPR: no face for %r" % who)
        return out

    register_validator(_validate_wp7_tables)


## Sandbox styles ###############################################################

style sb_action_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (16, 8, 16, 8)
    xsize 392
    yminimum 62

style sb_mission_button is sb_action_button:
    background Frame("gui/panel_gold.png", 4, 4)
    hover_background Frame("gui/panel_gold.png", 4, 4)
    hover_foreground Solid("#ffd16618")

style sb_action_title is text:
    font gui.display_font
    color gui.paper
    size 22

style sb_action_hint is text:
    color gui.dim
    size 16

style sb_link_text is text:
    font gui.body_medium_font
    color gui.dim
    hover_color gui.paper
    size 19

style sb_choice_button is sb_action_button:
    xsize 600
    yminimum 60
    padding (16, 8, 16, 8)

style sb_choice_gold_button is sb_choice_button:
    background Frame("gui/panel_gold.png", 4, 4)
    hover_background Frame("gui/panel_gold.png", 4, 4)
    hover_foreground Solid("#ffd16618")

style sb_plate_name is text:
    font gui.display_font
    size 26
    outlines [(2, "#07060cc0", 0, 0)]

style sb_plate_caption is text:
    italic True
    color gui.dim
    size 18

style sb_arrival_text is text:
    outlines [(0, "#07060cd8", 2, 2)]


## Diamonds: one per period an action takes ###################################

screen sb_cost(n):
    if n:
        hbox:
            spacing 3
            yalign 0.5
            for _k in range(n):
                add "gui/pip_small.png" yalign 0.5


## One tile of the icon column (4.4): icon_btn's look, hover label and word
## rule (ui_icons.rpy), at a fixed 72 x 72: a 50 px icon with the cost as
## diamonds under it. (icon_btn itself is as tall as its icon plus its
## diamonds, so a column of them would be uneven.) While icons show their
## words the tile grows downward by the word's lines.
screen rail_btn(name, action, tip, wid, gold=False, pips=0, word=None, words=True):
    button:
        id wid
        style "icon_btn_button"
        xsize RAIL_TILE
        yminimum RAIL_TILE
        action action
        tooltip (tip, wid)
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 2
            add icon(name, 50, (gold or name in ICON_GOLD)) xalign 0.5
            if pips:
                hbox:
                    xalign 0.5
                    spacing 3
                    for _rail_k in range(pips):
                        add "gui/pip_small.png"
            if words and icon_words_shown(name):
                text (word or icon_label(name)):
                    style "icon_btn_word"
                    substitute False
                    xalign 0.5
                    xmaximum RAIL_TILE - 8


## Place view (4.4) #############################################################
##
## Bottom to top: the room; the hotspots behind the people; the people
## (view_stage.rpy); the foreground; the hotspots in front; the overflow chip;
## the arrival caption; the icon column down the right edge; the HUD.

screen sb_place():

    tag sandbox

    ## The objective check also runs as the view appears, so a save loaded
    ## onto this screen gets its NEXT toast straight away (3.10). It does
    ## nothing when the objective hasn't changed.
    on ("show", "replace") action Function(check_objective)

    $ _stage, _extra = stage_people(here)
    ## Phase 2: the column is rail_rows(here): the missions the night allows,
    ## then rail_actions (the night rule and the hotspots reach it).
    ## (rail_layout drops the tiles' words rather than open a third column.)
    $ _rail, _rail_words = rail_layout(rail_rows(here))
    $ _t0 = arrival_caption()
    $ _pname = LOCATIONS[here]["name"] if here in LOCATIONS else here
    $ _pdesc = LOCATIONS[here]["desc"] if here in LOCATIONS else ""
    $ _per = period

    add graded_bg()
    add Solid(gui.ink) alpha 0.10

    ## --- the stage (phase 2: view_stage.rpy) and the hotspots, behind and in
    ## front of the people (sb_hotspots.rpy) ------------------------------------
    use hot_layer(here)
    use view_stage(here)
    use view_fg(here)
    use hot_layer(here, front=True)

    ## More than four: a chip with the rest, at the foot of the screen
    ## between the fourth person (whose sprite ends at x 1358) and the
    ## icon column.
    if _extra:
        $ _more = "+%d" % len(_extra)
        vbox:
            id "rail_more"
            pos RAIL_MORE_POS
            yanchor 1.0
            spacing 4
            frame:
                background Frame("gui/panel_dark.png", 4, 4)
                padding (14, 6)
                text _more font gui.display_font color gui.paper size 22
            for _w in _extra:
                textbutton CAST[_w]["short"]:
                    id "rail_more_" + _w
                    background Frame("gui/panel_dark.png", 4, 4)
                    hover_background Frame("gui/panel_hover.png", 4, 4)
                    padding (14, 4)
                    text_font gui.display_font
                    text_color CAST[_w]["color"]
                    text_size 20
                    tooltip (rail_tip(CAST[_w]["short"], ambient_of(_w, here)[0]), "rail_more_" + _w)
                    action Return(("char", _w))

    ## Nobody home. (Not said in my own room, where it is the only line on
    ## the screen and I am the one who is there.) The second overhaul (D48):
    ## when the room's owner is in it asleep, the line says so, since they
    ## are not on the stage and "nobody" would be untrue.
    if not _stage and here != "dorm":
        $ _rail_asleep = rail_asleep_line(here)
        frame:
            xcenter 700
            ycenter 640
            background Frame("gui/panel_ghost.png", 4, 4)
            padding (28, 14)
            text (_rail_asleep or _("Nobody here right now.")):
                substitute False
                color gui.dim
                size 22

    ## --- the arrival caption (D35) -----------------------------------------------
    if _t0 is not None:
        frame at arrival_fx(_t0):
            pos (40, 100)
            background Frame("gui/panel_ghost.png", 4, 4)
            padding (22, 10, 22, 14)
            vbox:
                spacing 4
                hbox:
                    spacing 14
                    text "[_pname]" style "sb_arrival_text" font gui.display_font color gui.paper size 44
                    text "· [_per]" style "sb_arrival_text" font gui.body_medium_font color gui.dim size 20 kerning gui.track yalign 0.85
                if _pdesc:
                    text "[_pdesc]" style "sb_arrival_text" color gui.dim size 20 xmaximum 700

    ## --- the icon column (phase 2, 4.4) -------------------------------------------
    ## Gold missions first, then what I can do here, Wait (or Go to bed), and
    ## "Let them go" last. The name, the hint and the cost are the hover label.
    hbox:
        id "rail_column"
        xalign 1.0
        xoffset -40
        yalign 1.0
        yoffset -40
        spacing RAIL_GAP
        for _col in _rail[::-1]:
            vbox:
                yalign 1.0
                spacing RAIL_GAP
                for _row in _col:
                    $ _ret, _ic, _gold, _tip, _pips, _wid = _row
                    use rail_btn(_ic, Return(_ret), _tip, _wid, gold=_gold, pips=_pips, word=rail_word(_row), words=_rail_words)

    use sb_hud


## Person view (4.5; phase 2: 4.6) ##############################################
## (The focus transform, char_focus, moved to view_stage.rpy with the stage.)
##
## The grade chip, the choices (an icon, the name, the cost; the hint is the
## hover label), then "Ask them along" and Back. The name, the caption, the
## bond and affection bars, the thread and the "Closer" hint are on the
## person's journal page (D19).

screen sb_char(who):

    tag sandbox

    $ _chip = rail_chip(who)
    $ _choices = person_choices(who, here)
    $ _inv_ok = activity_state(ACT_BY_ID["invite"], who, here)[0]
    $ _inv_tip = (rail_tip(_("Let them go"), _("They go back to their own day.")) if companion == who
                  else rail_tip(_("Ask them along"), ACT_BY_ID["invite"]["hint"]))

    add graded_bg()
    add Solid(gui.ink) alpha 0.35

    use view_focus(who)

    ## The card starts at y 250: two toasts sit above it, beside Menu, and
    ## two three-line ones (26 + 97 + 8 + 97) still end above it.
    frame:
        style "jjk_panel"
        xpos 1180
        ypos RAIL_CARD_Y
        xsize 640
        ymaximum 1040 - RAIL_CARD_Y
        padding (20, 20)

        vbox:
            spacing 14

            ## --- their grade (or their role) ---------------------------------
            if _chip[0] is not None or _chip[1]:
                hbox:
                    use grade_chip(_chip[0], size=18, text=_chip[1])

            ## --- what I can do with them ------------------------------------
            vbox:
                spacing 8
                for _i, _ch in enumerate(_choices):
                    $ _gold = _ch.get("gold")
                    $ _romc = _ch.get("romance")
                    $ _ret = (("do", _ch["id"], who) if _ch["kind"] == "do" else (_ch["kind"], _ch["id"]))
                    $ _lbl = _ch["label"]
                    button:
                        id "sb_char_%d" % _i
                        style ("sb_choice_gold_button" if _gold else "sb_choice_button")
                        action Return(_ret)
                        tooltip (rail_tip(_lbl, _ch.get("hint") or "", _ch.get("cost") or 0), "sb_char_%d" % _i)
                        hbox:
                            xfill True
                            hbox:
                                spacing 14
                                yalign 0.5
                                add icon(_ch["icon"], 40, _gold) yalign 0.5
                                text _lbl:
                                    substitute False
                                    font gui.display_font
                                    size 24
                                    yalign 0.5
                                    xmaximum 440
                                    color (gui.gold if _gold else (gui.romance if _romc else gui.paper))
                            if _ch.get("cost"):
                                hbox:
                                    xalign 1.0
                                    yalign 0.5
                                    use sb_cost(_ch["cost"])

            ## --- footer: ask them along (or let them go), and Back -------------
            hbox:
                xfill True
                if _inv_ok or companion == who:
                    use icon_btn("invite", Return(("do", "invite", who)), tip=_inv_tip, size=40, w=64, wid="sb_char_invite")
                hbox:
                    xalign 1.0
                    use icon_btn("back", Return(("cancel",)), tip=_("Back"), size=40, w=64, wid="sb_char_back")

    key "game_menu" action Return(("cancel",))

    use sb_hud(person=True)
