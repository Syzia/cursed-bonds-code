################################################################################
## Cursed Bonds — fishing at the riverside.
##
## Phase 2, P6 (PHASE2_DESIGN.md 4.13, D33, 6.1). Three casts for one period.
## A cast: the float sits, then dips; a marker sweeps a bar there and back,
## and I hook while it is inside the green zone. The zone is as wide as the
## fish is easy. A catch has a species and a length; it sells itself, the
## record book keeps my longest of each, and the day's first gives Control +1.
##
##   FISH_KINDS             six species, the River Lord and the pale thing
##   fish_roll(per)         what takes the hook next
##   fish_begin()           sits down, and rolls the sitting's three casts
##                          (fish_state["plan"]) so a save loaded during a
##                          cast finds the same fish on the line
##   fish_hit(kind, q)      whether a hook of quality q lands it
##   fish_length(kind, q)   how long it is
##   fish_land(kind, cm)    settles a catch: dict(id, cm, yen, record)
##   fish_cast_once(q)      one whole cast through the three above (the
##                          harness's simulated casts; the label takes the
##                          same steps one at a time)
##   fish_records()         the record book, [(name, cm or None)]
##   class fish_Hook        the Hook button's action: reads the clock at the
##                          click and returns ("hook", q)
##   screen fish_screen     returns ("hook", q), ("miss",), ("leave",)
##   label sb_do_fish_cast
##
## q runs from 0.0 to 1.0: how close the marker was to the middle of the zone
## (1.0 dead centre, falling by 0.2 for every tenth of the bar). A fish is
## landed when q >= 1 - its zone, so the River Lord (zone 0.10) needs 0.9.
##
## Each settled cast blocks rollback (a cast can't be taken again). Packing
## up while the float only sits is free; once it has dipped the zone has shown
## what is on the line, so packing up then is a miss and the cast is spent.
################################################################################

init -1 python:
    import time as _fish_time

    FISH_CASTS = 3              # casts in a sitting
    FISH_SWEEP = 1.5            # seconds for one pass of the marker
    FISH_PASSES = 2             # there and back
    FISH_WAIT = (1.0, 3.0)      # seconds before the float dips
    FISH_BAR = (660, 860, 600, 28)      # x, y, w, h of the bar
    FISH_FLOAT = (1100, 700)
    FISH_LORD = "river_lord"
    FISH_PALE = "pale_thing"
    FISH_LORD_YEN = 5000        # once
    FISH_PALE_CHANCE = 0.2      # an Evening cast, in a week it hasn't come up yet
    FISH_PALE_ITEM = "sealing_talisman"
    FISH_BOND = 2               # a companion, once a day
    FISH_YEN = (100, 600)       # what an ordinary catch sells for (D33)

    ## id, name, shortest and longest cm, weight, zone (the green zone's width
    ## as a part of the bar), yen a cm, and the periods it bites in. The six
    ## ordinary species sell for cm x yen_per_cm, always inside FISH_YEN; the
    ## River Lord pays FISH_LORD_YEN once; the pale thing is not a fish.
    FISH_KINDS = [
        dict(id="oikawa", name="Pale chub", min_cm=9, max_cm=15, weight=0.30, zone=0.50, yen_per_cm=12,
             periods=("Morning", "Noon", "Afternoon", "Evening")),
        dict(id="ugui", name="Dace", min_cm=15, max_cm=30, weight=0.24, zone=0.42, yen_per_cm=8,
             periods=("Morning", "Noon", "Afternoon", "Evening")),
        dict(id="ayu", name="Ayu", min_cm=12, max_cm=24, weight=0.17, zone=0.34, yen_per_cm=20,
             periods=("Morning", "Noon", "Afternoon")),
        dict(id="yamame", name="Yamame trout", min_cm=15, max_cm=30, weight=0.12, zone=0.28, yen_per_cm=18,
             periods=("Morning", "Evening")),
        dict(id="iwana", name="Char", min_cm=18, max_cm=40, weight=0.08, zone=0.22, yen_per_cm=15,
             periods=("Morning", "Evening")),
        dict(id="carp", name="Carp", min_cm=30, max_cm=60, weight=0.06, zone=0.18, yen_per_cm=10,
             periods=("Afternoon", "Evening")),
        dict(id="river_lord", name="The River Lord", min_cm=110, max_cm=140, weight=0.03, zone=0.10, yen_per_cm=0,
             periods=("Evening",)),
        dict(id="pale_thing", name="Something pale", min_cm=0, max_cm=0, weight=0.0, zone=0.30, yen_per_cm=0,
             periods=("Evening",)),
    ]

    def fish_kind(kind):
        """P6 (room_fishing.rpy). The FISH_KINDS row of that id, or None."""
        for k in FISH_KINDS:
            if k["id"] == kind:
                return k
        return None

    def fish_species():
        """P6. The rows the record book lists: every fish (not the pale thing)."""
        return [k for k in FISH_KINDS if k["id"] != FISH_PALE]

    def fish_week():
        """P6. The week the cursed catch is counted in: the board's."""
        return board_week_now()

    ## What bites -------------------------------------------------------------------

    def fish_pool(per=None):
        """P6. The fish that can take the hook in a period: the ordinary
        species that bite then, and the River Lord in the Evening until it
        has been caught."""
        per = per or store.period
        out = []
        for k in FISH_KINDS:
            if k["id"] == FISH_PALE or per not in k["periods"] or k["weight"] <= 0:
                continue
            if k["id"] == FISH_LORD and has_flag("caught_river_lord"):
                continue
            out.append(k)
        return out

    def fish_roll(per=None):
        """P6. The id of what takes the hook next. In the Evening, in a week
        the pale thing hasn't come up yet, it may be that; else a fish from
        fish_pool, by weight."""
        per = per or store.period
        pale = fish_kind(FISH_PALE)
        if (per in pale["periods"] and store.fish_cursed_week != fish_week()
                and renpy.random.random() < FISH_PALE_CHANCE):
            return FISH_PALE
        pool = fish_pool(per)
        if not pool:
            return FISH_KINDS[0]["id"]
        pick = renpy.random.random() * sum(k["weight"] for k in pool)
        for k in pool:
            if pick < k["weight"]:
                return k["id"]
            pick -= k["weight"]
        return pool[-1]["id"]

    def fish_hit(kind, q):
        """P6. bool: a hook of quality q lands this one: the marker was
        inside its zone (q >= 1 - zone)."""
        k = fish_kind(kind)
        return bool(k is not None and q >= 1.0 - k["zone"] - 1e-9)

    def fish_length(kind, q):
        """P6. int cm, inside the species' range: longer the nearer the
        middle of the zone the hook was, with some luck in it."""
        k = fish_kind(kind)
        s = max(0.0, min(1.0, (q - (1.0 - k["zone"])) / k["zone"]))
        f = 0.65 * s + 0.35 * renpy.random.random()
        return int(round(k["min_cm"] + (k["max_cm"] - k["min_cm"]) * f))

    ## Settling ---------------------------------------------------------------------

    def fish_land(kind, cm):
        """P6 (room_fishing.rpy). Settles one catch and returns dict(id, cm,
        yen, record). It pays cm x yen_per_cm (the River Lord: FISH_LORD_YEN,
        once, and the flag caught_river_lord), raises fish_log when this is
        my longest of the species (it never falls), and gives the day's
        first catch its Control +1 ("fish_first" in actions_today), except
        on a rest day. The pale thing leaves a sealing talisman and marks
        the week."""
        cm = int(cm)
        k = fish_kind(kind)
        if k is None:
            return dict(id=kind, cm=cm, yen=0, record=False)
        if kind == FISH_PALE:
            store.fish_cursed_week = fish_week()
            give_item(FISH_PALE_ITEM)
            return dict(id=kind, cm=cm, yen=0, record=False)
        if kind == FISH_LORD:
            yen = 0 if has_flag("caught_river_lord") else FISH_LORD_YEN
            flag("caught_river_lord")
        else:
            yen = cm * k["yen_per_cm"]
        add_yen(yen)
        record = cm > store.fish_log.get(kind, 0)
        if record:
            store.fish_log[kind] = cm
        if "fish_first" not in store.actions_today and night_can_work():
            store.actions_today.add("fish_first")
            gain("control", 1)
        return dict(id=kind, cm=cm, yen=int(yen), record=bool(record))

    def fish_cast_once(q, per=None):
        """P6. One whole cast, start to finish, with a hook of quality q:
        fish_roll, fish_hit, fish_length, fish_land. Returns fish_land's dict,
        or None for a miss."""
        kind = fish_roll(per)
        if not fish_hit(kind, q):
            return None
        return fish_land(kind, fish_length(kind, q))

    def fish_records():
        """P6 (room_fishing.rpy). The record book: a list of (name, cm or
        None), one row per species, for the record panel and the journal.
        The River Lord has no name until it has been caught."""
        out = []
        for k in fish_species():
            best = store.fish_log.get(k["id"]) or None
            name = k["name"] if (best or k["id"] != FISH_LORD) else "???"
            out.append((name, best))
        return out

    ## The sitting (fish_state) -----------------------------------------------------

    def fish_plan(per=None):
        """P6. The sitting's casts, rolled before the first one: a list of
        FISH_CASTS rows [kind, spare, r, wait]. kind is what will bite;
        spare is an ordinary fish that bites in its place if kind can no
        longer come up by then (the pale thing already seen this week, the
        River Lord already caught); r, 0.0 to 1.0, places the zone on the
        bar; wait is how long the float sits. Plain lists and numbers."""
        per = per or store.period
        plain = [k for k in fish_pool(per) if k["id"] != FISH_LORD] or [FISH_KINDS[0]]
        total = sum(k["weight"] for k in plain)
        rows = []
        for i in range(FISH_CASTS):
            kind = fish_roll(per)
            pick = renpy.random.random() * total
            spare = plain[-1]["id"]
            for k in plain:
                if pick < k["weight"]:
                    spare = k["id"]
                    break
                pick -= k["weight"]
            rows.append([kind, spare, renpy.random.random(),
                         FISH_WAIT[0] + renpy.random.random() * (FISH_WAIT[1] - FISH_WAIT[0])])
        return rows

    def fish_begin():
        """P6. Returns None. Sits down: a fresh fish_state, with the
        sitting's casts already rolled (fish_plan)."""
        store.fish_state = dict(cast=0, settled=0, phase="idle", kind="", centre=0.5,
                                wait=1.0, t_cast=0.0, t0=0.0, left=False, plan=fish_plan())
        return None

    def fish_more():
        """P6. bool: there is another cast in this sitting."""
        st = store.fish_state
        return bool(st) and not st.get("left") and st.get("cast", FISH_CASTS) < FISH_CASTS

    def fish_next():
        """P6. Returns None. Casts: what will bite, where its zone lies on
        the bar, and how long the float sits first. It reads the row
        fish_begin rolled for this cast and rolls nothing itself, so a save
        loaded during the cast (which runs this again) finds the same fish.
        A sitting with no plan (none can be saved, but a harness may build
        one) is rolled here."""
        st = store.fish_state
        n = st.get("cast", 0)
        plan = st.get("plan") or []
        if n < len(plan):
            kind, spare, r, wait = plan[n]
            if ((kind == FISH_PALE and store.fish_cursed_week == fish_week())
                    or (kind == FISH_LORD and has_flag("caught_river_lord"))):
                kind = spare
        else:
            kind = fish_roll()
            r = renpy.random.random()
            wait = FISH_WAIT[0] + renpy.random.random() * (FISH_WAIT[1] - FISH_WAIT[0])
        zone = fish_kind(kind)["zone"]
        st["cast"] = n + 1
        st["kind"] = kind
        st["centre"] = zone / 2.0 + r * (1.0 - zone)
        st["wait"] = wait
        st["t_cast"] = _fish_time.time()
        st["t0"] = 0.0
        st["phase"] = "wait"
        return None

    def fish_phase():
        """P6. "wait" (the float sits), "bite" (the marker is sweeping) or
        "idle" (no cast in hand)."""
        st = store.fish_state
        if not st or not st.get("kind"):
            return "idle"
        return st.get("phase", "idle")

    def fish_strike():
        """P6. Returns None. The float dips: the sweep starts now."""
        st = store.fish_state
        if st and st.get("phase") == "wait":
            st["phase"] = "bite"
            st["t0"] = _fish_time.time()
        return None

    def fish_wait_left():
        """P6. Seconds until the float dips (at least a twentieth)."""
        st = store.fish_state
        return max(0.05, st.get("t_cast", 0.0) + st.get("wait", 1.0) - _fish_time.time())

    def fish_bite_left():
        """P6. Seconds of the sweep left (at least a twentieth): after it
        the fish is gone."""
        st = store.fish_state
        return max(0.05, st.get("t0", 0.0) + FISH_SWEEP * FISH_PASSES - _fish_time.time())

    def fish_marker(t):
        """P6. Where the marker is t seconds into the sweep, 0.0 to 1.0
        along the bar: across in FISH_SWEEP seconds, and back."""
        x = max(0.0, min(float(FISH_PASSES), t / FISH_SWEEP))
        whole = int(x)
        part = x - whole
        if whole >= FISH_PASSES:
            return 0.0 if FISH_PASSES % 2 == 0 else 1.0
        return part if whole % 2 == 0 else 1.0 - part

    def fish_quality(pos, centre):
        """P6. q, 0.0 to 1.0: 1.0 with the marker on the middle of the zone,
        0.2 less for every tenth of the bar away."""
        return max(0.0, min(1.0, 1.0 - 2.0 * abs(pos - centre)))

    def fish_marker_fn(trans, st, at):
        """P6. The marker's transform: its place on the bar by the wall
        clock, redrawn every frame while the sweep lasts (it is the game,
        not decoration, so it moves with the Motion switch off too).
        Top-level (R10)."""
        s = store.fish_state
        t0 = s.get("t0") or 0.0
        pos = fish_marker(_fish_time.time() - t0) if t0 else 0.0
        trans.xpos = int(pos * FISH_BAR[2]) - 3
        return 0

    class fish_Hook(Action):
        """P6 (room_fishing.rpy; PHASE2_DESIGN.md 4.13, R4). The Hook
        button's action. Called at the click, it reads the wall clock
        against the start of the sweep (fish_state["t0"]), works out where
        the marker is, and returns ("hook", q), q a float 0.0 to 1.0. A
        plain Return would carry the q of the last redraw."""

        def __call__(self):
            st = store.fish_state or {}
            t0 = st.get("t0") or 0.0
            pos = fish_marker(_fish_time.time() - t0) if t0 else 0.0
            return ("hook", round(fish_quality(pos, st.get("centre", 0.5)), 3))

    def fish_yen(n):
        return "¥{:,}".format(int(n))

    FISH_MISS_LINES = [
        "The float comes back up with nothing under it. Too early, or too late. The river doesn't say which.",
        "A tug, and then no tug. I reel in a bare hook.",
        "Whatever it was, it takes the bait and leaves the hook, which is fair.",
    ]

    def fish_miss_line(kind):
        if kind == FISH_LORD:
            return ("The line goes heavy, then heavier, then slack. Something very large turns over once "
                    "under the green water and is gone. I stand there holding the rod with both hands.")
        if kind == FISH_PALE:
            return ("The float goes under without a ripple and comes back up by itself. "
                    "For a moment the water beneath it is the wrong colour.")
        return FISH_MISS_LINES[(store.day + store.fish_state.get("cast", 0)) % len(FISH_MISS_LINES)]

    def fish_catch_line(res):
        k = fish_kind(res["id"])
        if res["id"] == FISH_PALE:
            return ("What comes up is not a fish. It is pale, with too many joints, and it lets go of the hook "
                    "by itself and sinks. It leaves a strip of sealed paper wound round the line: a sealing "
                    "talisman, wet through and still good.")
        if res["id"] == FISH_LORD:
            line = ("The line goes heavy, and stays heavy, and I walk it up the bank a step at a time. "
                    "A carp longer than my arm and a good deal older than I am. The River Lord, %d cm." % res["cm"])
            if res["yen"]:
                line += " The cook will pay %s for it and not ask where." % fish_yen(res["yen"])
            return line
        line = "%s, %d cm." % (k["name"], res["cm"])
        if res["record"]:
            line += " A new best."
        return line + " The kitchen will give me %s for it." % fish_yen(res["yen"])

    def fish_company():
        """P6. Returns None. Whoever is along gains Bond +2, once a day
        ("fish_bond" in actions_today)."""
        who = store.companion
        if who and "fish_bond" not in store.actions_today:
            store.actions_today.add("fish_bond")
            add_bond(who, FISH_BOND)
        return None

    def fish_settle(r):
        """P6. Settles the cast in hand from the screen's return, ("hook",
        q) or ("miss",), and returns the line to say. A landed fish goes
        through fish_land."""
        st = store.fish_state
        kind = st.get("kind") or FISH_KINDS[0]["id"]
        q = 0.0
        if isinstance(r, tuple) and len(r) == 2 and r[0] == "hook":
            try:
                q = max(0.0, min(1.0, float(r[1])))
            except Exception:
                q = 0.0
        st["settled"] = st.get("settled", 0) + 1
        st["phase"] = "idle"
        st["kind"] = ""
        fish_company()
        if fish_hit(kind, q):
            return fish_catch_line(fish_land(kind, fish_length(kind, q)))
        return fish_miss_line(kind)

    def fish_leave():
        """P6. Returns None. I pack up before the last cast. (A cast that
        has already bitten is settled as a miss first: the label does it.)"""
        if store.fish_state:
            store.fish_state["left"] = True
        return None

    def fish_end():
        """P6. bool: the sitting cost its period (a cast was settled).
        Clears fish_state."""
        used = bool(store.fish_state and store.fish_state.get("settled", 0) > 0)
        store.fish_state = {}
        return used

    def fish_bg():
        """P6. The riverside as it looks at this hour."""
        return graded_bg("riverside")

    def fish_float():
        """P6. The float, as a displayable: built in the line that shows
        it, never stored (R10)."""
        return Fixed(
            Solid(gui.paper, xysize=(2, 26), xpos=9, ypos=0),
            Solid(gui.seal, xysize=(20, 16), xpos=0, ypos=22),
            Solid(gui.paper, xysize=(20, 10), xpos=0, ypos=38),
            xysize=(20, 48))

    ## Validator (D29, D33) ---------------------------------------------------------

    def fish_best_sitting(per):
        """P6. The mean yen of a three-cast sitting in a period with every
        hook dead centre, the River Lord's one payment left out: the most
        fishing can earn, to hold against a board job."""
        pool = [k for k in fish_pool(per) if k["id"] != FISH_LORD]
        total = sum(k["weight"] for k in pool)
        if not total:
            return 0.0
        mean = sum(k["weight"] * k["yen_per_cm"] * (k["min_cm"] + (k["max_cm"] - k["min_cm"]) * 0.825)
                   for k in pool) / total
        return mean * FISH_CASTS

    def fish_validate():
        """P6. Lint findings for the species table."""
        out = []
        ids = [k["id"] for k in FISH_KINDS]
        if len(set(ids)) != len(ids):
            out.append("FISH_KINDS: an id is listed twice")
        for need in (FISH_LORD, FISH_PALE):
            if need not in ids:
                out.append("FISH_KINDS: no row %r" % need)
        plain = [k for k in FISH_KINDS if k["id"] not in (FISH_LORD, FISH_PALE)]
        if len(plain) != 6:
            out.append("FISH_KINDS: %d ordinary species (six)" % len(plain))
        for k in FISH_KINDS:
            if set(k) != {"id", "name", "min_cm", "max_cm", "weight", "zone", "yen_per_cm", "periods"}:
                out.append("FISH_KINDS %s: keys %r" % (k.get("id"), sorted(k)))
                continue
            if not (0.0 < k["zone"] <= 1.0):
                out.append("FISH_KINDS %s: zone %r" % (k["id"], k["zone"]))
            if k["min_cm"] > k["max_cm"]:
                out.append("FISH_KINDS %s: min_cm above max_cm" % k["id"])
            if not k["periods"] or any(p not in PERIODS for p in k["periods"]):
                out.append("FISH_KINDS %s: periods %r" % (k["id"], k["periods"]))
        for k in plain:
            lo, hi = k["min_cm"] * k["yen_per_cm"], k["max_cm"] * k["yen_per_cm"]
            if lo < FISH_YEN[0] or hi > FISH_YEN[1]:
                out.append("FISH_KINDS %s: sells for %d to %d yen (D33: %d to %d)" % (k["id"], lo, hi, FISH_YEN[0], FISH_YEN[1]))
        cap = BOARD_YEN["g4"][0] // BOARD_PERIODS
        for per in PERIODS:
            if fish_best_sitting(per) >= cap:
                out.append("fishing in the %s earns %d a period at best; the cheapest board job pays %d (D29)"
                           % (per, fish_best_sitting(per), cap))
        if FISH_PALE_ITEM not in ITEMS:
            out.append("FISH_PALE_ITEM %r is not an item" % FISH_PALE_ITEM)
        return out

    register_validator(fish_validate)

    register_place_action("fish_cast", "Fish", "Three casts. The river decides the rest.",
                          cost=1, locs=("riverside",))


## The float's idle bob and its dip (ATL, R10).
transform fish_bob:
    yoffset 0
    ease 0.9 yoffset 4
    ease 0.9 yoffset 0
    repeat

transform fish_still:
    yoffset 0

transform fish_dip:
    yoffset 0
    easein 0.12 yoffset 22
    block:
        ease 0.25 yoffset 14
        ease 0.25 yoffset 22
        repeat


style fish_text is text:
    font gui.display_font
    color gui.paper
    size 26
    outlines [(2, "#07060ccc", 0, 0)]

style fish_row_text is text:
    font gui.body_medium_font
    color gui.paper
    size 24


## A cast (4.13). Returns ("hook", q), ("miss",) or ("leave",). The label has
## already rolled the cast into fish_state; the screen only keeps the clock.
screen fish_screen():

    tag sandbox
    modal True

    default fish_book = False

    $ _fish_phase = fish_phase()
    $ _fish_kind = fish_kind(fish_state.get("kind", "")) if fish_state else None
    $ _fish_n = (fish_state.get("cast", 0) if fish_state else 0)

    add fish_bg()
    add Solid(gui.ink) alpha 0.12

    key "game_menu" action Return(("leave",))

    ## A harness's autoplay never waits on it.
    if smoke_autoplay:
        timer 0.05 action Return(("hook", 0.5))
    elif not fish_book and _fish_phase == "wait":
        timer fish_wait_left() action Function(ui_do, fish_strike)
    elif _fish_phase == "bite":
        timer fish_bite_left() action Return(("miss",))

    ## A click anywhere on the water, or Space, is the hook.
    if _fish_phase == "bite" and not fish_book:
        button:
            id "fish_water"
            xysize (1920, 1080)
            background None
            action fish_Hook()
        key "K_SPACE" action fish_Hook()

    ## The float.
    fixed:
        pos (FISH_FLOAT[0] - 10, FISH_FLOAT[1] - 40)
        xysize (20, 48)
        if _fish_phase == "bite":
            add fish_float() at fish_dip
        elif view_motion():
            add fish_float() at fish_bob
        else:
            add fish_float() at fish_still
    add Solid(gui.paper) xysize (64, 2) pos (FISH_FLOAT[0] - 32, FISH_FLOAT[1] + 2) alpha 0.35

    ## Top left: the casts, and the record book.
    hbox:
        pos (60, 56)
        ysize 56
        spacing 14
        for _fish_i in range(FISH_CASTS):
            add icon("fish_cast", 48) alpha (0.3 if _fish_i + 1 < _fish_n else 1.0) yalign 0.5
        if _fish_n:
            text "Cast [_fish_n] of [FISH_CASTS]" style "fish_text" yalign 0.5
        if _fish_phase != "bite":
            use icon_btn("record", SetScreenVariable("fish_book", True), tip="Record book",
                         size=48, wid="fish_record", words="never")

    ## The bar: the zone, and the marker crossing it and coming back.
    if _fish_phase == "bite" and _fish_kind:
        $ _fish_zw = int(_fish_kind["zone"] * FISH_BAR[2])
        $ _fish_zx = int((fish_state.get("centre", 0.5) - _fish_kind["zone"] / 2.0) * FISH_BAR[2])
        fixed:
            pos (FISH_BAR[0], FISH_BAR[1])
            xysize (FISH_BAR[2], FISH_BAR[3])
            add Solid(gui.ink) alpha 0.8
            add Solid(gui.stamina) xysize (_fish_zw, FISH_BAR[3]) xpos _fish_zx alpha 0.85
            add Solid(gui.paper) xysize (6, FISH_BAR[3] + 16) ypos -8 at Transform(function=fish_marker_fn)

    textbutton "Hook!":
        id "fish_hook"
        style "jjk_button"
        xsize 220
        xpos FISH_BAR[0] + FISH_BAR[2] // 2
        xanchor 0.5
        ypos FISH_BAR[1] + 56
        text_xalign 0.5
        text_color gui.gold
        text_hover_color gui.paper
        action (fish_Hook() if (_fish_phase == "bite" and not fish_book) else None)

    textbutton "Pack up":
        id "fish_leave"
        style "jjk_button"
        xsize 220
        xanchor 1.0
        xpos 1810
        ypos 1000
        yanchor 0.5
        text_xalign 0.5
        action Return(("leave",))

    ## The record book (cuttable, 7 · P6).
    if fish_book:
        button:
            xysize (1920, 1080)
            background Solid("#07060cb0")
            action SetScreenVariable("fish_book", False)
        frame:
            style "jjk_panel"
            pos (610, 240)
            xysize (700, 600)
            vbox:
                spacing 10
                hbox:
                    spacing 16
                    add icon("record", 44) yalign 0.5
                    text "Record book" font gui.display_font size 34 color gui.paper yalign 0.5
                use rule()
                for _fish_name, _fish_cm in fish_records():
                    fixed:
                        ysize 40
                        text _fish_name style "fish_row_text" yalign 0.5 color (gui.paper if _fish_cm else gui.dim)
                        if _fish_cm:
                            text "[_fish_cm] cm" style "fish_row_text" xalign 1.0 yalign 0.5 color gui.gold
                        else:
                            text "???" style "fish_row_text" xalign 1.0 yalign 0.5 color gui.mute
            textbutton "Close":
                id "fish_book_close"
                style "jjk_button"
                xsize 180
                xalign 1.0
                yalign 1.0
                text_xalign 0.5
                action SetScreenVariable("fish_book", False)


## Three casts at the river (4.13). `call screen fish_screen` and the line
## after it are protected (2.3).
label sb_do_fish_cast:

    $ fish_begin()
    "There's a rod in the reeds that belongs to nobody, or to everybody. I bait the hook and find a flat stone to stand on."
    if companion and companion in CAST:
        $ _fish_who = CAST[companion]["short"]
        "[_fish_who] takes the next stone along and watches the float as if it owed us both money."

    while fish_more():
        $ fish_next()
        call screen fish_screen
        $ _fish_r = _return
        if not isinstance(_fish_r, tuple) or not _fish_r or _fish_r[0] == "leave":
            ## Once the float has dipped the cast is spent: the zone has
            ## shown what was on the line.
            if fish_phase() == "bite":
                $ _fish_line = fish_settle(("miss",))
                $ renpy.block_rollback()
                "[_fish_line]"
            $ fish_leave()
        else:
            $ _fish_line = fish_settle(_fish_r)
            ## A settled cast can't be taken again.
            $ renpy.block_rollback()
            "[_fish_line]"

    if fish_end():
        $ advance_period_soft(1)
    return


## Fishing state (3.3).
default fish_log = {}            # species id -> longest cm (int)
default fish_state = {}          # the sitting in progress; {} otherwise
default fish_cursed_week = -1    # the week the cursed catch last came up
