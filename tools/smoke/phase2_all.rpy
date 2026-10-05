## tools/smoke/phase2_all.rpy -- the whole phase-2 game, played end to end
## (docs/PHASE2_DESIGN.md, 7 · P8; section 13 for the exits).
##
##   SMOKE_TIMEOUT=300 tools/smoke.sh tools/smoke/phase2_all.rpy
##
## Phase 1's driver (tools/smoke/phase1_all.rpy), extended. A 30-day run takes
## about a minute and a half on the owner's Mac; the driver stops itself after
## PHASE2_MAX_SECONDS (default 270) and still reports how far it got.
## PHASE2_DAYS sets how many days to play after the prologue (default 30).
##
## What it does:
##   1. A fresh game from label start, exactly as New Game plays it: the whole
##      prologue under autoplay ("Go with him." is always taken; every other
##      menu is picked at random).
##   2. Then the real sandbox loop (label sandbox), played by an overlay
##      driver. Each timer tick, if a loop screen is the one waiting, it does
##      what a player would. It only takes what the screen offers: a decision
##      is the value of a button that is on the screen and can be pressed.
##   3. Each day, in this order of preference:
##        - a walk already begun (one exit at a time);
##        - a gold mission offered here;
##        - the journal, once a day; on three days the full tour: the five
##          tabs, then one person's page, by pressing the buttons;
##        - the map, once a day, by pressing its buttons: an area marker,
##          Back, and once Tokyo is open the Tokyo tab and a district;
##        - the objective's place, while its mission can be started;
##        - one board job a day;
##        - in the Evening, once: a night in Shibuya (the club, then the
##          Black Market at the after-club menu, and one purchase);
##        - at Night: the ridge and "Train until morning" on the night Gojo
##          asks for; otherwise bed ("Go to bed" from where I stand on odd
##          days, the walk to my room and Sleep on even days);
##        - one person a day;
##        - once each, in spare hours: one page read on my computer, the
##          board cross-check, one cast at the river, one blackjack hand and
##          one poker hand, one ride into the city with Ijichi;
##        - otherwise Wait.
##      Journeys alternate: by the exits in the picture on odd days (plan 13),
##      by the map's two levels on even days (area marker, then the pin).
##      One mission to Nade is held until the Evening, so that the day turns
##      away from my room and the loop walks me home (D21).
##   4. It asserts that nothing raised (an exception anywhere fails the run
##      through _lib.rpy's handler), everything phase1_all asserts, and that
##      each of the things in the list above happened at least once.
##   5. Last, the one acceptance line plan 7.3 always deferred to P8: each of
##      the Black Market's talismans, bought, is refused below its grade,
##      refused on its checklist's unmet line, and goes on once it is met.
##
## store.smoke_autoplay stays on (fights answer themselves, as in phase 1)
## except inside the flows the driver plays by hand: the computer, the river,
## the card table and the night out. Text is fast-skipped throughout.
##
## Output in shots/phase2_all/: result.txt; days.txt (one block per day: the
## objective at the day's first stop, what played, the phase-2 things done,
## and how and where the day ended); driver_log.txt (every label and
## decision); a few screenshots.

init 999 python:
    import builtins
    import os
    import time

    class ZZQState(builtins.object):
        """Driver state. A builtins.object made at init and never reassigned,
        so rollback and the store never touch it."""

        def __init__(self):
            self.on = False
            self.last_day = 30
            self.first_day = None
            self.cur_day = None
            self.days = builtins.list()        # one dict per day, for days.txt
            self.labels = builtins.list()
            self.played = builtins.dict()      # day -> watched labels played that day
            self.decisions = builtins.list()
            self.day_decisions = 0
            self.max_day_decisions = 260       # more than this in one day = stuck
            self.steps = 0
            self.max_steps = 40000
            self.max_seconds = 270
            self.t_start = None
            self.journal_done = False
            self.map_done = False
            self.board_done = False
            self.board_tried = False
            self.person_done = False
            self.missions = builtins.list()    # (day, period, id) started
            self.board_jobs = builtins.list()
            self.journals = 0
            self.maps = 0
            self.people = builtins.list()
            self.waits = 0
            self.objectives = builtins.list()
            self.shots_taken = builtins.set()
            self.menus = builtins.list()
            self.done_order = builtins.list()
            self.stuck = None
            self.went = builtins.set()
            self.board_held = builtins.list()
            self.last_place = None             # where I stood at the last place-view stop
            self.done_today = builtins.list()  # the phase-2 things done today (days.txt)
            ## Journeys.
            self.dest = None                   # where a walk by exits is heading
            self.dest_when = None              # (day, period) the walk began in
            self.hop = None                    # the place the exit just taken leads to
            self.walk_steps = builtins.list()  # (day, from, to)
            self.walk_bad = builtins.list()
            self.walk_kinds = builtins.set()   # "room>hub", "hub>room", "hub>hub"
            ## The map, by its buttons.
            self.map_plan = None               # None (look), ("go", loc), ("district", key), ("night", key)
            self.map_step = 0
            self.map_wait = 0
            self.map_tour = builtins.list()
            self.map_pressed = builtins.list() # every button id pressed
            self.map_go = builtins.list()      # (day, area, loc) reached through marker then pin
            self.map_missing = builtins.list()
            ## The journal's tour.
            self.jr_step = 0
            self.jr_tour = False
            self.jr_tours = 0
            self.jr_tabs = builtins.set()
            self.jr_person = builtins.list()   # (day, who) whose page opened
            self.jr_want = None
            ## Nights.
            self.marks = builtins.list()       # (day, label, here, night_carried)
            self.nights = builtins.dict(bed=[], bed_walk=[], carried=[], gojo=[], out=[], scene=[])
            self.gojo_forced = None
            self.rest_days = builtins.list()
            self.rest_decisions = builtins.dict()
            self.nade_held = builtins.list()
            ## The rooms.
            self.manual = None                 # the flow the driver is playing by hand
            self.pc_step = 0
            self.pc_want = None
            self.pc_read = builtins.list()     # (day, page)
            self.pc_check = builtins.list()    # (day, week)
            self.pc_check_try = None
            self.pc_tried = builtins.set()     # (day, period) the computer was opened in
            self.fish = builtins.list()        # (day, q)
            self.fish_step = 0
            self.fish_sat = builtins.set()
            self.cards = builtins.list()       # (day, game, result line)
            self.cards_step = 0
            self.cards_seq = builtins.list()
            self.cards_sat = builtins.set()
            self.market = builtins.list()      # (day, item, price, yen before)
            self.market_step = 0
            self.market_want = None
            self.trips = builtins.list()       # (day, district)
            self.trip_tried = builtins.set()

    zzq = ZZQState()

    ZZQ_WATCH = ("st_", "ev_", "ms_", "cm_", "act_", "sb_do_", "start_mission", "run_board_mission",
                 "sb_trip", "arc_one_open", "sandbox", "chapter_", "ch1", "ch2", "load_recover",
                 "return_recover", "resume_story", "play_event", "combat", "arc_two",
                 "night_", "market_open", "mg_", "hot_use", "rule_walk_to")
    ZZQ_STUDENTS = ("yuji", "megumi", "nobara", "maki", "panda", "toge")
    ZZQ_PLAYED = ("st_", "ev_", "cm_", "ms_", "act_", "run_board_mission", "sb_trip", "arc_two",
                  "night_carry_home", "night_out", "mg_", "market_open")
    ZZQ_NIGHT_LABELS = ("sb_do_sleep", "sb_do_night_bed", "sb_do_night_gojo", "night_out", "night_carry_home")
    ## Script that needs smoke_autoplay back on: fights answer themselves.
    ZZQ_STORY = ("st_", "ev_", "ms_", "cm_", "play_event", "start_mission", "run_board_mission", "combat")
    ZZQ_NIGHT_DISTRICT = "shibuya"

    def zzq_people():
        n = getattr(store, "day", 0) or 0
        k = n % len(ZZQ_STUDENTS)
        return ZZQ_STUDENTS[k:] + ZZQ_STUDENTS[:k]

    def zzq_label_cb(name, abnormal):
        if not zzq.on or not name.startswith(ZZQ_WATCH):
            return
        d = getattr(store, "day", 0)
        if len(zzq.labels) < 9000:
            zzq.labels.append("d%s %s %s %s" % (d, getattr(store, "period", "?"), getattr(store, "here", "?"), name))
        if name.startswith(ZZQ_PLAYED) and not name.startswith("sb_do_"):
            zzq.played.setdefault(d, builtins.list()).append(name)
        if name in ZZQ_NIGHT_LABELS:
            zzq.marks.append((d, name, getattr(store, "here", None), getattr(store, "night_carried", "")))
        if name.startswith(ZZQ_STORY) and not store.smoke_autoplay:
            store.smoke_autoplay = True

    config.label_callbacks.append(zzq_label_cb)

    def zzq_rets(screen):
        """[(value, sensitive)] for every button in `screen` whose action is
        (or ends with) a Return."""
        s = renpy.get_screen(screen)
        out = []
        if s is None:
            return out

        def flat(a):
            if isinstance(a, (list, tuple)):
                r = []
                for x in a:
                    r.extend(flat(x))
                return r
            return [a]

        def cb(d):
            act = getattr(d, "action", None)
            if act is None:
                return
            for a in flat(act):
                if isinstance(a, Return):
                    try:
                        sens = d.is_sensitive() if hasattr(d, "is_sensitive") else True
                    except Exception:
                        sens = True
                    out.append((a.value, sens))

        s.visit_all(cb)
        return out

    def zzq_offered(screen="sb_place"):
        """The values the screen's buttons would return now."""
        return [v for v, s in zzq_rets(screen) if s and isinstance(v, tuple)]

    def zzq_press(screen, wid):
        """Press a button by id, as a click does: its action is run with its
        screen current (SetScreenVariable writes there). Returns what the
        action returns; "zz_missing" when the button isn't on the screen."""
        sc = renpy.get_screen(screen)
        w = renpy.get_widget(screen, wid) if sc is not None else None
        if w is not None and not isinstance(w, renpy.display.behavior.Button):
            ## A textbutton's id names the Text inside it: take the button
            ## around it, which carries the action.
            found = []

            def around(d):
                if isinstance(d, renpy.display.behavior.Button) and w in d.visit():
                    found.append(d)

            sc.visit_all(around)
            w = found[0] if found else None
        if w is None or getattr(w, "action", None) is None:
            return "zz_missing"
        renpy.display.screen.push_current_screen(sc)
        try:
            return renpy.run(w.action)
        finally:
            renpy.display.screen.pop_current_screen()

    def zzq_objective():
        try:
            o = current_objective()
        except Exception as e:
            check(False, "current_objective raised on day %s" % store.day, repr(e))
            return None, "raised %r" % (e,), None
        if not o:
            return None, "", None
        return o, o.get("text") or "", o.get("mid")

    def zzq_step():
        try:
            sp = store.story_point or legacy_story_point()
        except Exception as e:
            sp = "raised %r" % (e,)
        o, text, mid = zzq_objective()
        st = ""
        if mid:
            try:
                st = mission_status(mid)
            except Exception as e:
                st = "raised %r" % (e,)
        return sp, mid, st, text

    def zzq_new_missions_done():
        for mid in sorted(store.missions_done, key=lambda m: (store.mission_done_day.get(m, 0), m)):
            if mid not in [m for d, m in zzq.done_order]:
                zzq.done_order.append((store.mission_done_day.get(mid, store.day), mid))

    def zzq_close_day(prev):
        """How and where day `prev` ended, from the night labels seen."""
        mine = [m for m in zzq.marks if m[0] == prev["day"]]
        carried = [m for m in zzq.marks if m[0] == prev["day"] + 1 and m[1] == "night_carry_home"]
        names = [m[1] for m in mine]
        at = prev.get("last_place") or "?"
        if carried:
            frm = carried[0][3] or carried[0][2] or at
            kind, how = "carried", "the day turned at %s; the loop walked me home" % frm
            at = frm
        elif "sb_do_night_gojo" in names and store.night_gojo_last == prev["day"]:
            kind, how = "gojo", "a night of training with Gojo on the ridge"
        elif "night_out" in names and store.night_out_last == prev["day"]:
            kind, how = "out", "out all night in the city"
        elif "sb_do_night_bed" in names:
            kind, how = "bed_walk", "Go to bed: the walk back to my room, then sleep"
        elif "sb_do_sleep" in names:
            kind, how = "bed", "Sleep, in my room"
        else:
            kind, how = "scene", "the day turned inside a scene (%s)" % ((zzq.played.get(prev["day"]) or ["?"])[-1])
        zzq.nights[kind].append(prev["day"])
        prev["end"] = "%s · last stood in %s" % (how, at)

    def zzq_day_row():
        """The day's entry for days.txt, opened at its first stop in the
        place view; the day before is closed here."""
        if zzq.days:
            zzq.days[-1]["last_place"] = zzq.last_place
            zzq.days[-1]["did"] = builtins.list(zzq.done_today)
            zzq_close_day(zzq.days[-1])
        zzq.cur_day = store.day
        zzq.day_decisions = 0
        zzq.journal_done = zzq.map_done = zzq.board_done = zzq.board_tried = zzq.person_done = False
        zzq.done_today = builtins.list()
        zzq.dest = None
        zzq_new_missions_done()
        sp, mid, st, text = zzq_step()
        zzq.objectives.append((store.day, text))
        tag = night_tag()
        if not night_can_work():
            zzq.rest_days.append(store.day)
        zzq.days.append(builtins.dict(
            day=store.day,
            head="day %2s %-9s %-15s grade=%-3s merit=%-4s yen=%-6s step=%s%s%s | %s" % (
                store.day, store.period, store.here, player_grade(), store.merit, store.yen,
                mid or "-", (" (%s)" % st) if st else "", (" [%s]" % tag) if tag else "",
                text or "(no objective)")))
        if zzq.first_day is not None and store.day in (zzq.first_day, zzq.first_day + 10, zzq.first_day + 20, zzq.last_day):
            zzq_shot("loop_place_day%02d" % store.day)

    def zzq_shot(name):
        if name in zzq.shots_taken:
            return
        zzq.shots_taken.add(name)
        shot(name, wait=0)

    def zzq_did(what):
        zzq.done_today.append(what)

    ## Journeys ----------------------------------------------------------------------

    def zzq_route(frm, to):
        """The places to pass through from frm to to by open exits, first
        hop first; [] when there is no way."""
        prev = builtins.dict()
        prev[frm] = None
        todo = [frm]
        while todo:
            cur = todo.pop(0)
            if cur == to:
                break
            for r in path_exits(cur):
                n = r["to"]
                if n in prev or r["locked_reason"]:
                    continue
                prev[n] = cur
                todo.append(n)
        if to not in prev:
            return []
        out = []
        cur = to
        while prev[cur] is not None:
            out.append(cur)
            cur = prev[cur]
        return out[::-1]

    def zzq_map_open(plan):
        zzq.map_plan = plan
        zzq.map_step = 0
        return ("map",)

    def zzq_go(loc):
        """Start a journey: by the exits on odd days, by the map on even
        days (and whenever the exits don't lead there)."""
        zzq.went.add((store.day, store.period, loc))
        if store.day % 2 == 1 and zzq_route(store.here, loc):
            zzq.dest = loc
            zzq.dest_when = (store.day, store.period)
            return zzq_walk()
        return zzq_map_open(("go", loc))

    def zzq_walk():
        """The next exit of the walk in hand, or the map when the exit isn't
        offered (None when I've arrived)."""
        loc = zzq.dest
        if loc is None or store.here == loc:
            zzq.dest = None
            return None
        if zzq.dest_when != (store.day, store.period):
            zzq.dest = None
            return None
        route = zzq_route(store.here, loc)
        want = ("act", "path_" + route[0]) if route else None
        if want is None or want not in zzq_offered():
            zzq.dest = None
            if want is not None:
                zzq.walk_bad.append("d%s %s: no exit to %s offered" % (store.day, store.here, route[0]))
            return zzq_map_open(("go", loc))
        a, b = path_is_hub(store.here), path_is_hub(route[0])
        zzq.walk_kinds.add("%s>%s" % ("hub" if a else "room", "hub" if b else "room"))
        zzq.hop = (store.here, route[0])
        zzq.walk_steps.append((store.day, store.here, route[0]))
        return want

    def zzq_may_go(loc):
        """Not to the same place twice in one period (no ping-pong)."""
        return loc != store.here and (store.day, store.period, loc) not in zzq.went

    def zzq_can_board():
        if zzq.board_done or zzq.board_tried or not has_flag("mission_board_open"):
            return False
        if store.period not in ("Morning", "Noon", "Afternoon") or not night_can_work():
            return False
        try:
            offers = board_offers_open()
        except Exception:
            offers = builtins.list(store.board_offers or ())
        if not offers:
            return False
        if not any(not board_take_reason(o) for o in offers):
            return False
        o, text, mid = zzq_objective()
        m = MISSION_BY_ID.get(mid) if mid else None
        if m and m["trigger"] == "auto" and mission_status(mid) == "available":
            i = PERIODS.index(store.period)
            skipped = PERIODS[i + 1:i + BOARD_PERIODS]
            if any(p in (m["periods"] or ()) for p in skipped):
                if (store.day, store.period, mid) not in zzq.board_held:
                    zzq.board_held.append((store.day, store.period, mid))
                return False
        return True

    def zzq_hold_nade(mid):
        """One mission to Nade waits for the Evening, so the day turns in
        Yaga's office and the loop walks me home."""
        if zzq.nights["carried"] or not str(mid).startswith("m_nade") or len(zzq.nade_held) >= 6:
            return False
        if any(m[1] == "night_carry_home" for m in zzq.marks):
            return False
        m = MISSION_BY_ID.get(mid) or {}
        if PERIODS.index(store.period) >= PERIODS.index("Evening"):
            return False
        ## Only on a day he will still be at his desk in the Evening.
        if not m.get("where") or m.get("with_who") not in who_is_here(m["where"], "Evening"):
            return False
        if (store.day, mid) not in zzq.nade_held:
            zzq.nade_held.append((store.day, mid))
        return True

    def zzq_beat_tonight():
        """An auto story beat is waiting for this Evening or tonight."""
        o, text, mid = zzq_objective()
        m = MISSION_BY_ID.get(mid) if mid else None
        if not m or m["trigger"] != "auto":
            return False
        try:
            if mission_status(mid) != "available":
                return False
        except Exception:
            return False
        return any(p in (m["periods"] or ()) for p in ("Evening", "Night"))

    def zzq_night_out_now():
        if zzq.nights["out"] or any(m[1] == "night_out" and m[0] == store.day for m in zzq.marks):
            return False
        if store.period != "Evening" or not tokyo_open():
            return False
        if not night_out_ok(ZZQ_NIGHT_DISTRICT)[0]:
            return False
        if store.yen < NIGHT_OUT["cover"] + min(r["price"] for r in MARKET_STOCK):
            return False
        return not zzq_beat_tonight()

    def zzq_manual(what):
        """The driver plays this flow by hand: the screens stop answering
        themselves."""
        zzq.manual = what
        store.smoke_autoplay = False

    def zzq_extra(offered):
        """One of the once-only things, when its hour and place fit. None
        when there is nothing to do now."""
        here = store.here
        per = store.period
        ## My computer: one page, and the cross-check once the board is posted.
        pc_page = not zzq.pc_read
        pc_cross = not zzq.pc_check and pc_check_ok()
        if (pc_page or pc_cross) and (store.day, per) not in zzq.pc_tried:
            if here == "dorm":
                if ("act", "pc_open") in offered:
                    zzq.pc_step = 0
                    zzq.pc_tried.add((store.day, per))
                    zzq_manual("pc")
                    return ("act", "pc_open")
            elif pc_cross and zzq_may_go("dorm"):
                return zzq_go("dorm")
        ## The card table.
        if not zzq.cards and store.day not in zzq.cards_sat and store.yen >= 3 * CARDS_STAKES[0]:
            if here == "dorm_common":
                if ("act", "cards_play") in offered:
                    zzq.cards_step = 0
                    zzq.cards_seq = builtins.list()
                    zzq.cards_sat.add(store.day)
                    zzq_manual("cards")
                    return ("act", "cards_play")
            elif who_is_here("dorm_common") and zzq_may_go("dorm_common"):
                return zzq_go("dorm_common")
        ## The river.
        if not zzq.fish and store.day not in zzq.fish_sat:
            if here == "riverside":
                if ("act", "fish_cast") in offered:
                    zzq.fish_step = 0
                    zzq.fish_sat.add(store.day)
                    zzq_manual("fish")
                    return ("act", "fish_cast")
            elif can_enter("riverside")[0] and zzq_may_go("riverside"):
                return zzq_go("riverside")
        ## One ride into the city.
        if (not zzq.trips and tokyo_open() and trip_ok_now() and store.day not in zzq.trip_tried
                and district_state(ZZQ_NIGHT_DISTRICT)[0] and not zzq_beat_tonight()):
            zzq.trip_tried.add(store.day)
            return zzq_map_open(("district", ZZQ_NIGHT_DISTRICT))
        return None

    def zzq_place():
        """What to do at sb_place."""
        store.smoke_autoplay = True
        zzq.manual = None
        if zzq.first_day is None:
            zzq.first_day = store.day
            zzq.last_day = store.day + zzq.last_day - 1
            check(has_flag("settled_in"), "the prologue ends settled in", "flags: %r" % sorted(store.flags))
        if zzq.cur_day != store.day:
            zzq_day_row()
        if store.day > zzq.last_day:
            return "finish"
        zzq.day_decisions += 1
        if not night_can_work():
            zzq.rest_decisions[store.day] = zzq.rest_decisions.get(store.day, 0) + 1
        if zzq.day_decisions > zzq.max_day_decisions:
            zzq.stuck = "day %s: %d decisions without a new day (at %s, %s)" % (
                store.day, zzq.day_decisions, store.here, store.period)
            return "finish"
        here = store.here
        zzq.last_place = here
        offered = zzq_offered()
        ## The exit just taken led where it said.
        if zzq.hop is not None:
            if here != zzq.hop[1]:
                zzq.walk_bad.append("d%s: the exit %s to %s left me in %s" % (store.day, zzq.hop[0], zzq.hop[1], here))
            zzq.hop = None
        ## 0. A walk in hand.
        if zzq.dest is not None:
            v = zzq_walk()
            if v is not None:
                return v
        ## 1. A gold mission offered here.
        ms = [v[1] for v in offered if v[0] == "mission"]
        ms = [m for m in ms if not zzq_hold_nade(m)]
        if ms:
            zzq.missions.append((store.day, store.period, ms[0]))
            return ("mission", ms[0])
        ## 2. The journal, once a day.
        if not zzq.journal_done and ("journal", "people") in offered:
            zzq.journal_done = True
            zzq.jr_step = 0
            zzq.jr_tour = (zzq.jr_tours < 3 and store.day in (zzq.first_day + 1, zzq.first_day + 11, zzq.first_day + 21)) or (
                zzq.jr_tours == 0 and store.day >= zzq.first_day + 22)
            return ("journal", "people")
        ## 3. The map, once a day, by its buttons.
        if not zzq.map_done and ("map",) in offered:
            zzq.map_done = True
            return zzq_map_open(None)
        ## 4. The objective's place, while its mission can be started.
        o, text, mid = zzq_objective()
        if o and o.get("where") and mid and store.period != PERIODS[-1] and night_can_work():
            try:
                st = mission_status(mid)
            except Exception:
                st = None
            w = o["where"]
            if isinstance(w, (list, tuple)):
                w = w[0]
            if st == "available" and w in LOCATIONS and zzq_may_go(w) and not zzq_hold_nade(mid):
                ok, why = can_enter(w)
                if ok:
                    return zzq_go(w)
        ## 5. One board job a day.
        if zzq_can_board():
            host, hloc = board_host()
            if board_open() and ("act", "board") in offered:
                zzq.board_tried = True
                return ("act", "board")
            if char_location(host) == hloc and zzq_may_go(hloc):
                return zzq_go(hloc)
        ## 6. Once: a night in the city.
        if zzq_night_out_now():
            zzq_manual("night_out")
            return zzq_map_open(("night", ZZQ_NIGHT_DISTRICT))
        ## 7. Night.
        if store.period == PERIODS[-1]:
            if store.night_gojo_day == store.day and not zzq.nights["gojo"]:
                if ("act", "night_gojo") in offered:
                    zzq_did("Train until morning, on the ridge")
                    return ("act", "night_gojo")
                if here != NIGHT_GOJO["place"] and zzq_may_go(NIGHT_GOJO["place"]):
                    return zzq_go(NIGHT_GOJO["place"])
            if here != "dorm":
                if store.day % 2 == 1 and ("act", "night_bed") in offered:
                    return ("act", "night_bed")
                if zzq_may_go("dorm"):
                    return zzq_go("dorm")
                if ("act", "night_bed") in offered:
                    return ("act", "night_bed")
            if ("act", "sleep") in offered:
                return ("act", "sleep")
            note("night", "day %s at %s: neither Sleep nor Go to bed is offered: %r" % (store.day, here, offered))
            return ("act", "sleep")
        ## 8. One person a day: someone here, else go and find a student.
        if not zzq.person_done:
            people = [v[1] for v in offered if v[0] == "char" and v[1] in store.roster]
            if people:
                zzq.person_done = True
                return ("char", people[0])
            for w in zzq_people():
                if w not in store.roster:
                    continue
                loc = char_location(w)
                if loc and loc in LOCATIONS and zzq_may_go(loc) and can_enter(loc)[0]:
                    return zzq_go(loc)
        ## 9. The once-only things, in spare hours.
        v = zzq_extra(offered)
        if v is not None:
            return v
        if ("act", "wait") in offered:
            zzq.waits += 1
            return ("act", "wait")
        note("wait", "day %s %s at %s: Wait is not offered: %r" % (store.day, store.period, here, offered))
        zzq.waits += 1
        return ("act", "wait")

    def zzq_char():
        """At sb_char: a mission they give, else an activity, else Talk."""
        vals = zzq_offered("sb_char")
        who = None
        s = renpy.get_screen("sb_char")
        try:
            who = s.scope.get("who") if s is not None else None
        except Exception:
            pass
        ms = [v for v in vals if v[0] == "mission" and not zzq_hold_nade(v[1])]
        if ms:
            zzq.missions.append((store.day, store.period, ms[0][1]))
            zzq.people.append((store.day, who, "mission " + ms[0][1]))
            return ms[0]
        dos = [v for v in vals if v[0] == "do" and v[1] not in ("talk", "invite")]
        if dos:
            zzq.people.append((store.day, who, dos[0][1]))
            return dos[0]
        talk = [v for v in vals if v[0] == "do" and v[1] == "talk"]
        if talk:
            zzq.people.append((store.day, who, "talk"))
            return talk[0]
        zzq.people.append((store.day, who, "nothing offered"))
        return ("cancel",)

    ## The map, by its buttons ---------------------------------------------------------

    def zzq_map_press(wid):
        v = zzq_press("sb_map", wid)
        if v == "zz_missing":
            zzq.map_missing.append("d%s %s: %s" % (store.day, store.period, wid))
            return None
        zzq.map_pressed.append(wid)
        return v

    def zzq_map():
        sc = renpy.get_screen("sb_map")
        zone = sc.scope.get("zone")
        view = sc.scope.get("view")
        plan = zzq.map_plan
        zzq.map_step += 1
        if zzq.map_step == 1:
            zzq.maps += 1
            zzq_shot("loop_map")
            if plan is None:
                zzq.map_tour = ["area_" + (area_of(store.here) or AREAS[0]["key"]), "map_back"]
                if tokyo_open():
                    zzq.map_tour += ["map_tokyo", "district_" + ZZQ_NIGHT_DISTRICT, "map_back", "map_campus"]
                zzq.map_tour.append("map_stay")
        if zzq.map_step > 14:
            note("map", "day %s: the plan %r did not finish in 14 presses (view %r, zone %r)" % (store.day, plan, view, zone))
            zzq.map_plan = None
            return ("cancel",)
        if plan is None:
            if not zzq.map_tour:
                return ("cancel",)
            wid = zzq.map_tour[0]
            if zone and wid == "map_back":
                ## The second level zooms in over 0.3 s: on the first tour,
                ## wait it out for the screenshot.
                name = "loop_map_district" if view == "tokyo" else "loop_map_area"
                if name not in zzq.shots_taken:
                    zzq.map_wait += 1
                    if zzq.map_wait < 6:
                        zzq.map_step -= 1
                        return None
                    zzq.map_wait = 0
                    zzq_shot(name)
            zzq.map_tour.pop(0)
            return zzq_map_press(wid)
        if plan[0] == "go":
            loc = plan[1]
            area = area_of(loc)
            if view != "campus":
                return zzq_map_press("map_campus")
            if zone != area:
                return zzq_map_press("area_" + area)
            v = zzq_map_press("row_" + loc)
            zzq.map_plan = None
            if isinstance(v, tuple):
                zzq.map_go.append((store.day, area, loc))
                return v
            note("map", "day %s: the pin of %s does nothing (%r)" % (store.day, loc, place_access(loc)))
            return ("cancel",)
        key = plan[1]
        if view != "tokyo":
            return zzq_map_press("map_tokyo")
        if zone != key:
            return zzq_map_press("district_" + key)
        v = zzq_map_press("district_go" if plan[0] == "district" else "district_night")
        zzq.map_plan = None
        if isinstance(v, tuple):
            if plan[0] == "district":
                zzq.trips.append((store.day, key))
                zzq_did("a ride into %s with Ijichi" % key)
            return v
        note("map", "day %s %s: %r could not start from the district's view" % (store.day, store.period, plan))
        return ("cancel",)

    def zzq_board():
        vals = zzq_offered("board_screen")
        zzq_shot("loop_board_screen")
        takes = [v for v in vals if v[0] == "take"]
        if takes and not zzq.board_done:
            return takes[0]
        zzq.board_done = True
        return ("close",)

    def zzq_partner():
        vals = zzq_offered("board_partner")
        zzq_shot("loop_board_partner")
        ps = [v for v in vals if v[0] == "partner"]
        zzq.board_done = True
        if ps:
            zzq.board_jobs.append((store.day, ps[0][1]))
            return ps[0]
        note("board job", "no partner offered on day %s: %r" % (store.day, vals))
        return ("cancel",)

    ## The journal: on a tour day the five tabs, then one person's page ---------------

    def zzq_journal():
        sc = renpy.get_screen("journal")
        js = sc.scope.get("js") or {}
        zzq.jr_step += 1
        if zzq.jr_step == 1:
            zzq.journals += 1
            zzq_shot("loop_journal")
            if not zzq.jr_tour:
                return True
            zzq.jr_tours += 1
            zzq.jr_tabs.add(js.get("tab"))
        if not zzq.jr_tour or zzq.jr_step > 12:
            return True
        tabs = [t[0] for t in JOURNAL_TABS]
        order = [t for t in tabs if t != "people"] + ["people"]
        k = zzq.jr_step - 1
        if zzq.jr_step > 1:
            zzq.jr_tabs.add(js.get("tab"))
        if k < len(order):
            if k > 0:
                zzq_shot("loop_journal_%s" % order[k - 1])
            if zzq_press("journal", "jr_tab_" + order[k]) == "zz_missing":
                note("journal", "day %s: no tab button jr_tab_%s" % (store.day, order[k]))
            return None
        if k == len(order):
            for w in store.roster:
                if renpy.get_widget("journal", "jr_card_" + w) is not None:
                    zzq.jr_want = w
                    zzq_press("journal", "jr_card_" + w)
                    return None
            note("journal", "day %s: no person card to open" % store.day)
            return True
        if zzq.jr_want is not None:
            if js.get("sel") == zzq.jr_want and js.get("tab") == "people":
                zzq.jr_person.append((store.day, zzq.jr_want))
                zzq_did("the journal's five tabs and %s's page" % zzq.jr_want)
                zzq_shot("loop_journal_person")
            else:
                note("journal", "day %s: %s's card did not open the page (sel %r)" % (store.day, zzq.jr_want, js.get("sel")))
            zzq.jr_want = None
        return True

    ## My computer ---------------------------------------------------------------------

    def zzq_pc_press(wid):
        v = zzq_press("pc_screen", wid)
        if v == "zz_missing":
            note("computer", "day %s: no button %s" % (store.day, wid))
            return ("close",)
        return v

    def zzq_pc():
        sc = renpy.get_screen("pc_screen")
        page = sc.scope.get("page")
        zzq.pc_step += 1
        if zzq.pc_want is not None:
            if pc_has_read(zzq.pc_want) and page == zzq.pc_want:
                zzq.pc_read.append((store.day, zzq.pc_want))
                zzq_did("read the page %s on my computer" % zzq.pc_want)
                zzq_shot("loop_pc_page")
            else:
                note("computer", "day %s: pressing the bookmark of %s did not open it (page %r)" % (store.day, zzq.pc_want, page))
            zzq.pc_want = None
        if zzq.pc_check_try == "pressed":
            zzq.pc_check_try = None
            if pc_checked():
                zzq.pc_check.append((store.day, store.pc_checked_week))
                zzq_did("cross-checked the board's reports")
        if zzq.pc_step > 10:
            return zzq_pc_press("pc_close")
        if not zzq.pc_read:
            unread = [p for p in pc_pages() if p not in (PC_HOME, PC_BOARD_PAGE) and not pc_has_read(p)]
            if unread:
                zzq.pc_want = unread[0]
                return zzq_pc_press("pc_mark_" + unread[0])
        if not zzq.pc_check and pc_check_ok() and store.period != PERIODS[-1]:
            if page != PC_BOARD_PAGE:
                return zzq_pc_press("pc_mark_" + PC_BOARD_PAGE)
            zzq_shot("loop_pc_board")
            zzq.pc_check_try = "pressed"
            return zzq_pc_press("pc_check")
        return zzq_pc_press("pc_close")

    ## The river -----------------------------------------------------------------------

    def zzq_fish():
        zzq.fish_step += 1
        if zzq.fish:
            v = zzq_press("fish_screen", "fish_leave")
            return ("leave",) if v == "zz_missing" else v
        if zzq.fish_step > 80:
            note("fishing", "day %s: no bite in 8 seconds (phase %r)" % (store.day, fish_phase()))
            return ("leave",)
        if fish_phase() != "bite":
            return None
        zzq_shot("loop_fish_bite")
        v = zzq_press("fish_screen", "fish_water")
        if isinstance(v, tuple) and v and v[0] == "hook":
            zzq.fish.append((store.day, v[1]))
            zzq_did("one cast at the river (q %.2f)" % v[1])
            return v
        note("fishing", "day %s: the water did not answer the hook (%r)" % (store.day, v))
        return None

    ## The card table ------------------------------------------------------------------

    def zzq_cards_press(screen, wid, fallback):
        v = zzq_press(screen, wid)
        if v == "zz_missing":
            note("cards", "day %s: no button %s on %s" % (store.day, wid, screen))
            return fallback
        return v

    def zzq_cards_table():
        zzq.cards_step += 1
        sc = renpy.get_screen("cards_table")
        stake = sc.scope.get("cards_pick") or CARDS_STAKES[0]
        opp = (store.cards_sit or {}).get("opponents") or cards_opponents()
        if zzq.cards_step > 60:
            return ("close",)
        for g in mg_games():
            if g["id"] in zzq.cards_seq:
                continue
            zzq.cards_seq.append(g["id"])
            if cards_game_open(g, stake, len(opp)):
                zzq_shot("loop_cards_table")
                return zzq_cards_press("cards_table", "cards_game_" + g["id"], ("close",))
            note("cards", "day %s: %s can't be played (%s)" % (store.day, g["id"], cards_game_note(g, stake, len(opp))))
        return zzq_cards_press("cards_table", "cards_leave", ("close",))

    def zzq_cards_hand(game, screen):
        """One hand: stand at blackjack; check, call and stand pat at poker.
        The move buttons are deaf for the screen's first 0.3 s (cards_guard):
        a press that does nothing is tried again on the next tick."""
        zzq.cards_step += 1
        st = store.cards_state or {}
        stage = st.get("stage")
        if zzq.cards_step > 200:
            return ("leave",)
        if game == "blackjack":
            wid = "cards_stand" if stage == "play" else None
        elif stage in ("bet1", "bet2"):
            wid = "cards_check"
        elif stage in ("call1", "call2"):
            wid = "cards_bet" if store.yen >= int(st.get("owed", 0)) else "cards_fold"
        elif stage == "draw":
            wid = "cards_draw"
        else:
            wid = None
        if wid is not None:
            return zzq_cards_press(screen, wid, ("leave",))
        v = zzq_cards_press(screen, "cards_leave", ("leave",))
        if v is not None and not [c for c in zzq.cards if c[0] == store.day and c[1] == game]:
            try:
                line = cards_result_line()
            except Exception as e:
                line = "raised %r" % (e,)
            zzq.cards.append((store.day, game, line, int(st.get("hands", 0))))
            zzq_did("one hand of %s (%s)" % (game, line))
            zzq_shot("loop_cards_" + game)
        return v

    ## The Black Market ----------------------------------------------------------------

    def zzq_market():
        zzq.market_step += 1
        if zzq.market_want is not None:
            iid, price, yen0, n0 = zzq.market_want
            zzq.market_want = None
            if store.yen == yen0 - price and item_count(iid) == n0 + 1:
                zzq.market.append((store.day, iid, price, yen0))
                zzq_did("bought %s at the Black Market for %d yen" % (iid, price))
            else:
                note("market", "day %s: Buy on %s changed nothing (yen %s to %s)" % (store.day, iid, yen0, store.yen))
        if not zzq.market and zzq.market_step < 6:
            rows = [r for r in market_rows() if r[2] == "buy"]
            if rows:
                zzq_shot("loop_market")
                iid, price = rows[0][0], rows[0][1]
                v = zzq_press("market_screen", "market_buy_" + iid)
                if isinstance(v, tuple):
                    zzq.market_want = (iid, price, store.yen, item_count(iid))
                    return v
                note("market", "day %s: no Buy button for %s (%r)" % (store.day, iid, v))
        v = zzq_press("market_screen", "market_close")
        return ("close",) if v == "zz_missing" else v

    def zzq_tick():
        if not zzq.on:
            return None
        ctx = renpy.game.context()
        if not ctx.interacting:
            return None
        zzq.steps += 1
        if zzq.steps > zzq.max_steps or time.time() - zzq.t_start > zzq.max_seconds:
            zzq.stuck = "driver limit reached (%d ticks, %.0f s) at day %s %s %s; last: %r" % (
                zzq.steps, time.time() - zzq.t_start, store.day, store.period, store.here, zzq.decisions[-6:])
            zzq_finish()
            return None
        try:
            ## A fight met while a flow is played by hand answers itself.
            if renpy.get_screen("combat_screen") is not None and not store.smoke_autoplay:
                store.smoke_autoplay = True
                renpy.restart_interaction()
                return None
            for scr, fn in (("market_screen", zzq_market), ("pc_screen", zzq_pc), ("fish_screen", zzq_fish),
                            ("cards_poker", lambda: zzq_cards_hand("poker", "cards_poker")),
                            ("cards_blackjack", lambda: zzq_cards_hand("blackjack", "cards_blackjack")),
                            ("cards_table", zzq_cards_table),
                            ("board_partner", zzq_partner), ("board_screen", zzq_board),
                            ("journal", zzq_journal), ("sb_map", zzq_map), ("sb_char", zzq_char),
                            ("sb_place", zzq_place)):
                if renpy.get_screen(scr) is not None:
                    v = fn()
                    if v == "finish":
                        zzq_finish()
                        return None
                    if v is not None:
                        zzq.decisions.append("d%s %s %s: %s -> %r" % (store.day, store.period, store.here, scr, v))
                    return v
        except renpy.game.CONTROL_EXCEPTIONS:
            raise
        except Exception:
            import traceback
            check(False, "driver raised", traceback.format_exc())
            zzq.on = False
            finish()
        return None

    def zzq_write_logs():
        d = zz_smoke_state.shots
        try:
            if not os.path.isdir(d):
                os.makedirs(d)
            rows = []
            for r in zzq.days:
                rows.append(r["head"])
                if r["day"] <= zzq.last_day:
                    rows.append("    played: %s" % (", ".join(zzq.played.get(r["day"], ())) or "nothing"))
                    if r.get("did"):
                        rows.append("    did:    %s" % "; ".join(r["did"]))
                    rows.append("    ended:  %s" % r.get("end", "(the run stopped during this day)"))
            with open(os.path.join(d, "days.txt"), "w", encoding="utf-8") as f:
                f.write("phase2_all · %d days from day %s · %s\n" % (
                    (zzq.last_day - (zzq.first_day or 0) + 1), zzq.first_day, time.strftime("%Y-%m-%d %H:%M")))
                f.write("\n".join(rows) + "\n\n## missions finished, in the order found (day done, id)\n")
                f.write("\n".join("day %s %s" % x for x in zzq.done_order) + "\n")
                f.write("\n## nights\n" + "\n".join("%s: %s" % (k, ", ".join(str(x) for x in v) or "none")
                                                     for k, v in sorted(zzq.nights.items())) + "\n")
            with open(os.path.join(d, "driver_log.txt"), "w", encoding="utf-8") as f:
                f.write("## labels\n" + "\n".join(zzq.labels) +
                        "\n\n## decisions\n" + "\n".join(zzq.decisions) + "\n")
        except Exception as e:
            check(False, "writes days.txt and driver_log.txt", repr(e))

    def zzq_finish():
        zzq.on = False
        store.smoke_autoplay = True
        zzq_new_missions_done()
        if zzq.days and "end" not in zzq.days[-1] and store.day > zzq.days[-1]["day"]:
            zzq.days[-1]["last_place"] = zzq.last_place
            zzq.days[-1]["did"] = builtins.list(zzq.done_today)
            zzq_close_day(zzq.days[-1])
        zzq_write_logs()
        renpy.jump("zzq_report")

    config.overlay_screens.append("zzq_driver")


screen zzq_driver():
    zorder 400
    if zzq.on:
        timer 0.1 repeat True action Function(zzq_tick)

init 999 python:
    ## The offer has two endings; the other road ends the game. The rest are
    ## the menus of the flows the driver plays by hand: the club before the
    ## market, then the market at the after-club menu.
    ZZQ_FORCE = builtins.list(["Go with him.", "Stay.", "Go.", "The club · ¥[_night_cover]", "The Black Market"])
    zzq_real_menu = menu

    def zzq_menu(items, **kwargs):
        for want in ZZQ_FORCE:
            for lab, val in items:
                if val is not None and lab == want:
                    zzq.menus.append(lab)
                    return getattr(val, "value", val)
        return zzq_real_menu(items, **kwargs)

    def zzq_patch():
        """Menus go through zzq_menu. Set at init, so it is the game's `menu`
        for the whole run and never a saved variable."""
        store.menu = zzq_menu

    zzq_patch()

    ## A Gojo night is due only when it would beat a day of training. When
    ## the run has not seen one by its twenty-second day, the review tools'
    ## switch asks for tonight (night_dev, "Gojo night tonight").
    def zzq_gojo_hook():
        if not zzq.on or zzq.first_day is None or zzq.nights["gojo"] or zzq.gojo_forced is not None:
            return
        if store.day < zzq.first_day + 21 or store.night_gojo_day == store.day:
            return
        if "gojo" not in store.roster:
            return
        zzq.gojo_forced = store.day
        night_dev("gojo")

    register_new_day(zzq_gojo_hook, order=99)

label zz_smoke:
    python:
        zzq.last_day = int(smoke_env("PHASE2_DAYS", "30"))
        zzq.max_seconds = int(smoke_env("PHASE2_MAX_SECONDS", "270"))
        autoplay(True)
        zzq.on = True
        zzq.t_start = time.time()
        del config.label_overrides["start"]
    ## label start, exactly as a New Game plays it: the prologue, then the
    ## sandbox loop, which the overlay driver plays.
    call start
    $ abort("label start returned (the game ended before the campus opened?)")

## The verdict, and a few screenshots from wherever the loop stopped.
label zzq_report:
    $ autoplay(False)
    $ zzq.on = False
    scene expression graded_bg()
    python:
        _secs = time.time() - zzq.t_start
        note("played", "%d days (day %s to %s) in %.0f s, %d decisions" % (
            max(0, store.day - (zzq.first_day or store.day)), zzq.first_day, store.day, _secs, len(zzq.decisions)))
        check("Go with him." in zzq.menus, "the offer took \"Go with him.\"", repr(zzq.menus))
        check(zzq.first_day is not None, "the prologue reached the sandbox loop")
        check(zzq.stuck is None, "no day got stuck", zzq.stuck or "")
        check(zzq.first_day is not None and store.day > zzq.last_day,
              "played every day to day %s" % zzq.last_day, "stopped on day %s" % store.day)

        ## Story rows finish in their order.
        _order = {m["id"]: m["order"] for m in STORY_ROWS}
        _seq = [(d, m) for d, m in zzq.done_order if m in _order]
        _bad = [(a, b) for a, b in builtins.zip(_seq, _seq[1:]) if _order[b[1]] < _order[a[1]]]
        check(not _bad, "story rows finish in order", repr(_bad))
        note("story rows done", ", ".join("%s (day %s)" % (m, store.mission_done_day.get(m, "?")) for d, m in _seq))

        _started = [m for d, p, m in zzq.missions]
        _open = [m for m in _started if m not in store.missions_done]
        check(not _open, "every mission started finished", repr(_open))
        note("missions started", repr(zzq.missions))

        _texts = [t for d, t in zzq.objectives]
        _distinct = builtins.len(builtins.set(_texts))
        check(_distinct > 3, "the objective changes over the days", "%d distinct objectives" % _distinct)
        _run, _longest, _prev = 0, (0, None), None
        for d, t in zzq.objectives:
            _run = _run + 1 if t == _prev else 1
            _prev = t
            if _run > _longest[0]:
                _longest = (_run, t)
        note("longest unchanged objective", "%d days: %s" % _longest)

        _days = builtins.len(zzq.objectives)
        note("journal renders", "%d (days logged %d)" % (zzq.journals, _days))
        note("map renders", zzq.maps)
        check(zzq.journals >= _days - 1, "the journal renders every day")
        check(zzq.maps >= _days - 1, "the map renders every day")
        note("board jobs", repr(zzq.board_jobs))
        note("board jobs held back for a story beat", repr(zzq.board_held))
        check(builtins.len(zzq.board_jobs) >= 1, "at least one board job ran")
        note("people", "; ".join("d%s %s: %s" % x for x in zzq.people))
        note("waits", zzq.waits)

        ## Phase 2 ---------------------------------------------------------------
        ## The map's two levels, by pressing buttons.
        _areas = builtins.sorted(builtins.set(w for w in zzq.map_pressed if w.startswith("area_")))
        _pins = builtins.sorted(builtins.set(w for w in zzq.map_pressed if w.startswith("row_")))
        check(not zzq.map_missing, "every map button the driver went for was on the map", repr(zzq.map_missing[:8]))
        check(_areas and _pins and zzq.map_go,
              "the campus map's two levels by pressing buttons: an area marker, then a pin, walks there",
              "areas %r, pins %r" % (_areas, _pins))
        note("map journeys (day, area, place)", repr(zzq.map_go))
        check("map_tokyo" in zzq.map_pressed and ("district_" + ZZQ_NIGHT_DISTRICT) in zzq.map_pressed
              and "map_back" in zzq.map_pressed,
              "Tokyo's two levels by pressing buttons: the Tokyo tab, a district, Back",
              repr(builtins.sorted(builtins.set(zzq.map_pressed))))
        note("rides with Ijichi (day, district)", repr(zzq.trips))

        ## Walking by the exits (plan 13).
        check(builtins.len(zzq.walk_steps) >= 10 and not zzq.walk_bad,
              "walking by the exits: every exit taken led where its label said",
              "%d exits; %r" % (builtins.len(zzq.walk_steps), zzq.walk_bad[:6]))
        check({"room>hub", "hub>room", "hub>hub"} <= zzq.walk_kinds,
              "exits of all three kinds were taken: room to hub, hub to room, hub to hub", repr(builtins.sorted(zzq.walk_kinds)))
        note("exits taken", "%d, through %d places" % (
            builtins.len(zzq.walk_steps), builtins.len(builtins.set(s[2] for s in zzq.walk_steps))))

        ## One night of each kind.
        note("nights", repr(dict(zzq.nights)))
        check(zzq.nights["bed"] and zzq.nights["bed_walk"],
              "a night in bed: Sleep in my room, and Go to bed from somewhere else", repr((zzq.nights["bed"][:3], zzq.nights["bed_walk"][:3])))
        check(zzq.nights["carried"], "a night carried home: the day turned away from my room and the loop walked me back",
              "Nade missions held for the Evening: %r" % (zzq.nade_held,))
        check(zzq.nights["gojo"], "a night with Gojo on the ridge", "night_gojo_day %r, forced on day %r" % (store.night_gojo_day, zzq.gojo_forced))
        if zzq.gojo_forced is not None:
            note("Gojo night", "none came due by day %s, so the review tools' switch (night_dev) asked for it" % zzq.gojo_forced)
        _rest = [d for d in zzq.rest_days if (d - 1) in zzq.nights["gojo"]]
        check(bool(zzq.nights["gojo"]) and bool(_rest), "the day after the Gojo night is a rest day, and it was played through",
              "rest days %r, decisions on them %r" % (zzq.rest_days, dict(zzq.rest_decisions)))
        check(zzq.nights["out"], "a night out in the city", "Tokyo open: %r, yen %r, night_out_ok %r" % (
            tokyo_open(), store.yen, night_out_ok(ZZQ_NIGHT_DISTRICT)))
        check("The club · ¥[_night_cover]" in zzq.menus and "The Black Market" in zzq.menus,
              "the night out took the club, then the Black Market at the after-club menu", repr(zzq.menus))
        check(zzq.market, "one purchase at the Black Market: the yen went and the item came", repr(zzq.market))
        note("market", repr(zzq.market))

        ## The rooms.
        check(zzq.pc_read, "one page read on my computer", repr(sorted(store.pc_read)))
        check(zzq.pc_check, "one cross-check of the board's reports", "pc_checked_week %r" % (store.pc_checked_week,))
        check(zzq.fish, "one cast at the river, hooked by pressing the water", repr(zzq.fish))
        _games = [c[1] for c in zzq.cards]
        check("blackjack" in _games, "one hand of blackjack", repr(zzq.cards))
        check("poker" in _games, "one hand of poker", repr(zzq.cards))
        note("cards", repr(zzq.cards))

        ## The journal.
        check(builtins.set(t[0] for t in JOURNAL_TABS) <= zzq.jr_tabs,
              "the journal's five tabs, by pressing each", repr(builtins.sorted(str(t) for t in zzq.jr_tabs)))
        check(zzq.jr_person, "a person's page in the journal, by pressing their card", repr(zzq.jr_person))

        ## The day log.
        _logged = [r for r in zzq.days if r["day"] <= zzq.last_day]
        check(builtins.len(_logged) >= zzq.last_day - (zzq.first_day or 0) + 1 and all("end" in r for r in _logged),
              "days.txt holds every day's objective and where the day ended",
              "%d days logged; without an end: %r" % (builtins.len(_logged), [r["day"] for r in _logged if "end" not in r]))

        note("end state", "day %s %s at %s · grade %s · merit %s · yen %s · roster %r · inventory %r" % (
            day, period, here, player_grade(), merit, yen, roster, dict(inventory)))

        renpy.show_screen("sb_place")
        shot("view_place", wait=0.6)
        check(renpy.get_screen("sb_place") is not None, "renders sb_place at the end")
        renpy.hide_screen("sb_place")
        objective_leave()
        renpy.show_screen("journal", "missions")
        shot("view_journal_missions", wait=0.6)
        check(renpy.get_screen("journal") is not None, "renders journal(missions) at the end")
        renpy.hide_screen("journal")
        renpy.show_screen("sb_map", layer="campus")
        shot("view_map", wait=0.6)
        check(renpy.get_screen("sb_map") is not None, "renders sb_map at the end")
        renpy.hide_screen("sb_map")

        ## The acceptance line 7.3 always deferred to P8 (P4b's market and
        ## P4a's checklist were built side by side): each market talisman,
        ## bought, is refused below its grade by can_wear's own grade test,
        ## refused on the unmet line of its checklist, and goes on once the
        ## checklist is met. Last, because it changes my grade and my stats.
        _bad = []
        _specials = builtins.list(bound_specials)
        store.yen = max(store.yen, sum(r["price"] for r in MARKET_STOCK))
        for _iid in [r["item"] for r in MARKET_STOCK if ITEMS[r["item"]]["kind"] == "talisman"]:
            store.equipped_talismans = []
            if not has_item(_iid) and not market_buy(_iid):
                _bad.append((_iid, "not bought"))
                continue
            _grade = [r[1] for r in ITEM_REQS[_iid] if r[0] == "grade"][0]
            _stat = [r for r in ITEM_REQS[_iid] if r[0] == "stat"][0]
            _was = can_wear(_iid)
            if grade_rank(player_grade()) < grade_rank(_grade) and (_was != (False, "Needs " + grade_label(_grade)) or equip_talisman(_iid)):
                _bad.append((_iid, "below its grade", _was))
            if grade_rank(player_grade()) < grade_rank(_grade):
                promote("mc", _grade, quiet=True)
            setattr(store, _stat[1], _stat[2] - 1)
            _short = can_wear(_iid)
            _lines = [l for l, ok in item_requirements(_iid) if not ok]
            if _short[0] or builtins.len(_lines) != 1 or _short[1] != _lines[0] or equip_talisman(_iid) or _iid in equipped_talismans:
                _bad.append((_iid, "the stat one short", _short, _lines))
            setattr(store, _stat[1], _stat[2])
            _met = can_wear(_iid)
            if _met != (True, "") or not item_requirements_met(_iid) or not equip_talisman(_iid) or _iid not in equipped_talismans:
                _bad.append((_iid, "the checklist met", _met, item_requirements(_iid)))
            note("market talisman " + _iid, "%r, then %r, then %r" % (_was, _short, _met))
        check(not _bad and builtins.list(bound_specials) == _specials,
              "7.3's deferred line: each market talisman is refused below its grade, refused on its checklist's unmet line, "
              "and goes on through can_wear and equip_talisman once the checklist is met", repr(_bad))
        toast_clear()
    $ finish()
