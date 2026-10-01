## tools/smoke/phase1_all.rpy -- the whole phase-1 game, played end to end
## (docs/PHASE1_DESIGN.md, 7 · WP11 task 4).
##
##   tools/smoke.sh tools/smoke/phase1_all.rpy
##
## A 30-day run takes about 65 s on the owner's Mac, inside smoke.sh's default
## 180 s. The driver stops itself after PHASE1_MAX_SECONDS (default 160) and
## still reports how far it got; for a longer run raise both, e.g.
## PHASE1_DAYS=60 PHASE1_MAX_SECONDS=400 SMOKE_TIMEOUT=450.
## PHASE1_DAYS sets how many days to play after the prologue (default 30).
##
## What it does:
##   1. A fresh game from label start, exactly as New Game plays it: the whole
##      prologue under autoplay. The offer has two endings and one of them
##      leaves the game, so the menu choice "Go with him." is always taken;
##      every other menu is picked at random by autoplay.
##   2. Then the real sandbox loop (label sandbox), played by an overlay
##      driver: each timer tick, if a loop screen is the one waiting, it picks
##      what a player would and ends that screen's interaction with the value
##      the screen's own button would return. So every story event, mission,
##      board job, activity and new_day() runs through the loop's own labels.
##   3. Each day, in this order of preference:
##        - a start-type mission offered here (the gold button);
##        - the journal, rendered once a day (people tab);
##        - the map, rendered once a day (opened and closed);
##        - the objective's place, when it names one (so the story's
##          start-type missions are reached; auto-type story events fire by
##          themselves wherever I am);
##        - one board job a day, when the board is open, a card can be taken
##          and someone can come along (mornings to afternoons);
##        - one person a day: an activity with them (or a mission they give);
##        - at Night, the dorm and Sleep, which calls new_day();
##        - otherwise Wait.
##   4. It asserts that nothing raised (an exception anywhere fails the run
##      through _lib.rpy's exception handler), that all the days were played,
##      that no day got stuck, that story rows finished in their order, and
##      that every mission started also finished.
##
## Output in shots/phase1_all/: result.txt; objectives.txt (one line per day,
## at the day's first stop in the place view: day, period, place, grade,
## merit, story step (the story row the objective points at, with its status),
## story_point and the objective; then the scenes that played that day); driver_log.txt (every label and
## decision); a few screenshots (loop_*.png as it plays, view_*.png at the
## end).

init 999 python:
    import builtins
    import os
    import time

    class ZZPState(builtins.object):
        """Driver state. A builtins.object made at init and never reassigned,
        so rollback and the store never touch it."""

        def __init__(self):
            self.on = False
            self.last_day = 30
            self.first_day = None
            self.cur_day = None
            self.rows = builtins.list()        # objectives.txt lines
            self.labels = builtins.list()      # every watched label, with the day
            self.played = builtins.dict()      # day -> watched labels played that day
            self.decisions = builtins.list()
            self.day_decisions = 0
            self.max_day_decisions = 120       # more than this in one day = stuck
            self.steps = 0
            self.max_steps = 20000
            self.max_seconds = 160
            self.t_start = None
            self.journal_done = False
            self.map_done = False
            self.board_done = False
            self.board_tried = False
            self.person_done = False
            self.map_target = None
            self.missions = builtins.list()    # (day, period, id) started
            self.board_jobs = builtins.list()  # (day, partner)
            self.journals = 0
            self.maps = 0
            self.people = builtins.list()      # (day, who, what)
            self.waits = 0
            self.objectives = builtins.list()  # (day, objective text)
            self.shots_taken = builtins.set()
            self.menus = builtins.list()
            self.done_order = builtins.list()  # (day, mission id) in the order they finished
            self.stuck = None
            self.went = builtins.set()         # (day, period, place) travelled to
            self.board_held = builtins.list()  # (day, period, mission) a job would have skipped

    zzp = ZZPState()

    ZZP_WATCH = ("st_", "ev_", "ms_", "cm_", "act_", "sb_do_", "start_mission", "run_board_mission",
                 "sb_trip", "arc_one_open", "sandbox", "chapter_", "ch1", "ch2", "load_recover",
                 "return_recover", "resume_story", "play_event", "combat", "arc_two")
    ## Who the driver goes looking for, rotating by day so it meets several.
    ZZP_STUDENTS = ("yuji", "megumi", "nobara", "maki", "panda", "toge")

    class _ZZPPeople(builtins.object):
        def __iter__(self):
            n = getattr(store, "day", 0) or 0
            k = n % len(ZZP_STUDENTS)
            return iter(ZZP_STUDENTS[k:] + ZZP_STUDENTS[:k])

    ZZP_PEOPLE = _ZZPPeople()
    ZZP_PLAYED = ("st_", "ev_", "cm_", "ms_", "act_", "run_board_mission", "sb_trip", "arc_two")

    def zzp_label_cb(name, abnormal):
        if not zzp.on or not name.startswith(ZZP_WATCH):
            return
        if len(zzp.labels) < 6000:
            zzp.labels.append("d%s %s %s %s" % (getattr(store, "day", "?"), getattr(store, "period", "?"),
                                                getattr(store, "here", "?"), name))
        if name.startswith(ZZP_PLAYED) and not name.startswith("sb_do_"):
            zzp.played.setdefault(getattr(store, "day", 0), builtins.list()).append(name)

    config.label_callbacks.append(zzp_label_cb)

    def zzp_rets(screen):
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

    def zzp_objective():
        try:
            o = current_objective()
        except Exception as e:
            check(False, "current_objective raised on day %s" % store.day, repr(e))
            return None, "raised %r" % (e,), None
        if not o:
            return None, "", None
        return o, o.get("text") or "", o.get("mid")

    def zzp_step():
        """The current story step: the prologue step (story_point, or the
        legacy reading), then the story row the objective points at, with its
        status."""
        try:
            sp = store.story_point or legacy_story_point()
        except Exception as e:
            sp = "raised %r" % (e,)
        o, text, mid = zzp_objective()
        st = ""
        if mid:
            try:
                st = mission_status(mid)
            except Exception as e:
                st = "raised %r" % (e,)
        return sp, mid, st, text

    def zzp_new_missions_done():
        for mid in sorted(store.missions_done, key=lambda m: (store.mission_done_day.get(m, 0), m)):
            if mid not in [m for d, m in zzp.done_order]:
                zzp.done_order.append((store.mission_done_day.get(mid, store.day), mid))

    def zzp_day_row():
        """The day's line in objectives.txt, logged at its first stop in the
        place view (story events that fire at the top of the loop have
        already played)."""
        zzp.cur_day = store.day
        zzp.day_decisions = 0
        zzp.journal_done = zzp.map_done = zzp.board_done = zzp.board_tried = zzp.person_done = False
        zzp_new_missions_done()
        sp, mid, st, text = zzp_step()
        zzp.objectives.append((store.day, text))
        zzp.rows.append((store.day, "day %2s %-9s %-15s grade=%-3s merit=%-4s step=%s%s story_point=%s | %s" % (
            store.day, store.period, store.here, player_grade(), store.merit,
            mid or "-", (" (%s)" % st) if st else "", sp, text or "(no objective)")))
        if store.day in (zzp.first_day, zzp.first_day + 10, zzp.first_day + 20, zzp.last_day):
            zzp_shot("loop_place_day%02d" % store.day)

    def zzp_shot(name):
        if name in zzp.shots_taken:
            return
        zzp.shots_taken.add(name)
        shot(name, wait=0)

    def zzp_go(loc):
        zzp.map_target = loc
        zzp.went.add((store.day, store.period, loc))
        return ("map",)

    def zzp_may_go(loc):
        """Not to the same place twice in one period (no ping-pong)."""
        return loc != store.here and (store.day, store.period, loc) not in zzp.went

    def zzp_can_board():
        if zzp.board_done or zzp.board_tried or not has_flag("mission_board_open"):
            return False
        if store.period not in ("Morning", "Noon", "Afternoon"):
            return False
        try:
            offers = board_offers_open()
        except Exception:
            offers = builtins.list(store.board_offers or ())
        if not offers:
            return False
        if not any(not board_take_reason(o) for o in offers):
            return False
        ## A job costs two periods. Don't jump over the period an auto story
        ## beat is waiting for (a player reading the objective wouldn't).
        o, text, mid = zzp_objective()
        m = MISSION_BY_ID.get(mid) if mid else None
        if m and m["trigger"] == "auto" and mission_status(mid) == "available":
            i = PERIODS.index(store.period)
            skipped = PERIODS[i + 1:i + BOARD_PERIODS]
            if any(p in (m["periods"] or ()) for p in skipped):
                if (store.day, store.period, mid) not in zzp.board_held:
                    zzp.board_held.append((store.day, store.period, mid))
                return False
        return True

    def zzp_place():
        """What to do at sb_place."""
        if zzp.first_day is None:
            zzp.first_day = store.day
            zzp.last_day = store.day + zzp.last_day - 1
            check(has_flag("settled_in"), "the prologue ends settled in", "flags: %r" % sorted(store.flags))
        if zzp.cur_day != store.day:
            zzp_day_row()
        if store.day > zzp.last_day:
            return "finish"
        zzp.day_decisions += 1
        if zzp.day_decisions > zzp.max_day_decisions:
            zzp.stuck = "day %s: %d decisions without a new day (at %s, %s)" % (
                store.day, zzp.day_decisions, store.here, store.period)
            return "finish"
        here = store.here
        ## 1. A start-type mission offered here.
        try:
            ms = missions_here(here)
        except Exception as e:
            check(False, "missions_here raised", repr(e))
            ms = []
        if ms:
            zzp.missions.append((store.day, store.period, ms[0]))
            return ("mission", ms[0])
        ## 2. The journal, once a day.
        if not zzp.journal_done:
            zzp.journal_done = True
            return ("journal", "people")
        ## 3. The map, once a day, just to look.
        if not zzp.map_done:
            zzp.map_done = True
            zzp.map_target = None
            return ("map",)
        ## 4. The objective's place, while its mission can be started.
        o, text, mid = zzp_objective()
        if o and o.get("where") and mid and store.period != PERIODS[-1]:
            try:
                st = mission_status(mid)
            except Exception:
                st = None
            w = o["where"]
            if isinstance(w, (list, tuple)):
                w = w[0]
            if st == "available" and w in LOCATIONS and zzp_may_go(w):
                ok, why = can_enter(w)
                if ok:
                    return zzp_go(w)
        ## 5. One board job a day.
        if zzp_can_board():
            host, hloc = board_host()
            if board_open():
                zzp.board_tried = True
                return ("act", "board")
            if char_location(host) == hloc and zzp_may_go(hloc):
                return zzp_go(hloc)
        ## 6. Night: to bed.
        if store.period == PERIODS[-1]:
            if here != "dorm" and zzp_may_go("dorm"):
                return zzp_go("dorm")
            return ("act", "sleep")
        ## 7. One person a day: someone here, else go and find a student.
        if not zzp.person_done:
            people = [w for w in who_is_here() if w in store.roster]
            if people:
                zzp.person_done = True
                return ("char", people[0])
            for w in ZZP_PEOPLE:
                if w not in store.roster:
                    continue
                loc = char_location(w)
                if loc and loc in LOCATIONS and zzp_may_go(loc) and can_enter(loc)[0]:
                    return zzp_go(loc)
        zzp.waits += 1
        return ("act", "wait")

    def zzp_char():
        """At sb_char: a mission they give, else an activity, else Talk."""
        vals = [v for v, s in zzp_rets("sb_char") if s and isinstance(v, tuple)]
        who = None
        s = renpy.get_screen("sb_char")
        try:
            who = s.scope.get("who") if s is not None else None
        except Exception:
            pass
        ms = [v for v in vals if v[0] == "mission"]
        if ms:
            zzp.missions.append((store.day, store.period, ms[0][1]))
            zzp.people.append((store.day, who, "mission " + ms[0][1]))
            return ms[0]
        dos = [v for v in vals if v[0] == "do" and v[1] not in ("talk", "invite")]
        if dos:
            zzp.people.append((store.day, who, dos[0][1]))
            return dos[0]
        talk = [v for v in vals if v[0] == "do" and v[1] == "talk"]
        if talk:
            zzp.people.append((store.day, who, "talk"))
            return talk[0]
        zzp.people.append((store.day, who, "nothing offered"))
        return ("cancel",)

    def zzp_map():
        vals = [v for v, s in zzp_rets("sb_map") if s and isinstance(v, tuple)]
        t = zzp.map_target
        zzp.map_target = None
        zzp.maps += 1
        zzp_shot("loop_map")
        if t:
            if ("go", t) not in vals:
                note("map", "no sensitive Go button for %s (day %s %s); going anyway" % (t, store.day, store.period))
            return ("go", t)
        return ("cancel",)

    def zzp_board():
        vals = [v for v, s in zzp_rets("board_screen") if s and isinstance(v, tuple)]
        zzp_shot("loop_board_screen")
        takes = [v for v in vals if v[0] == "take"]
        if takes and not zzp.board_done:
            return takes[0]
        zzp.board_done = True
        return ("close",)

    def zzp_partner():
        vals = [v for v, s in zzp_rets("board_partner") if s and isinstance(v, tuple)]
        zzp_shot("loop_board_partner")
        ps = [v for v in vals if v[0] == "partner"]
        zzp.board_done = True
        if ps:
            zzp.board_jobs.append((store.day, ps[0][1]))
            return ps[0]
        note("board job", "no partner offered on day %s: %r" % (store.day, vals))
        return ("cancel",)

    def zzp_journal():
        zzp.journals += 1
        zzp_shot("loop_journal")
        return True

    def zzp_tick():
        if not zzp.on:
            return None
        ctx = renpy.game.context()
        if not ctx.interacting:
            return None
        zzp.steps += 1
        if zzp.steps > zzp.max_steps or time.time() - zzp.t_start > zzp.max_seconds:
            zzp.stuck = "driver limit reached (%d ticks, %.0f s) at day %s %s %s" % (
                zzp.steps, time.time() - zzp.t_start, store.day, store.period, store.here)
            zzp_finish()
            return None
        try:
            for scr, fn in (("board_partner", zzp_partner), ("board_screen", zzp_board),
                            ("journal", zzp_journal), ("sb_map", zzp_map), ("sb_char", zzp_char),
                            ("sb_place", zzp_place)):
                if renpy.get_screen(scr) is not None:
                    v = fn()
                    if v == "finish":
                        zzp_finish()
                        return None
                    zzp.decisions.append("d%s %s %s: %s -> %r" % (store.day, store.period, store.here, scr, v))
                    return v
        except renpy.game.CONTROL_EXCEPTIONS:
            raise
        except Exception:
            import traceback
            check(False, "driver raised", traceback.format_exc())
            zzp.on = False
            finish()
        return None

    def zzp_write_logs():
        d = zz_smoke_state.shots
        try:
            if not os.path.isdir(d):
                os.makedirs(d)
            rows = []
            for dn, line in zzp.rows:
                rows.append(line)
                if dn <= zzp.last_day:
                    rows.append("    played: %s" % (", ".join(zzp.played.get(dn, ())) or "nothing"))
            with open(os.path.join(d, "objectives.txt"), "w", encoding="utf-8") as f:
                f.write("phase1_all · %d days from day %s · %s\n" % (
                    (zzp.last_day - (zzp.first_day or 0) + 1), zzp.first_day, time.strftime("%Y-%m-%d %H:%M")))
                f.write("\n".join(rows) + "\n\n## missions finished, in the order found (day done, id)\n")
                f.write("\n".join("day %s %s" % x for x in zzp.done_order) + "\n")
            with open(os.path.join(d, "driver_log.txt"), "w", encoding="utf-8") as f:
                f.write("## labels\n" + "\n".join(zzp.labels) +
                        "\n\n## decisions\n" + "\n".join(zzp.decisions) + "\n")
        except Exception as e:
            check(False, "writes objectives.txt and driver_log.txt", repr(e))

    def zzp_finish():
        zzp.on = False
        zzp_new_missions_done()
        zzp_write_logs()
        renpy.jump("zzp_report")

    config.overlay_screens.append("zzp_driver")


screen zzp_driver():
    zorder 400
    if zzp.on:
        timer 0.1 repeat True action Function(zzp_tick)

init 999 python:
    ## The offer has two endings; the other road ends the game. Take Gojo's.
    ZZP_FORCE = builtins.list(["Go with him."])
    zzp_real_menu = menu

    def zzp_menu(items, **kwargs):
        for want in ZZP_FORCE:
            for lab, val in items:
                if val is not None and lab == want:
                    zzp.menus.append(lab)
                    return getattr(val, "value", val)
        return zzp_real_menu(items, **kwargs)

    menu = zzp_menu

label zz_smoke:
    python:
        zzp.last_day = int(smoke_env("PHASE1_DAYS", "30"))
        zzp.max_seconds = int(smoke_env("PHASE1_MAX_SECONDS", "160"))
        autoplay(True)
        zzp.on = True
        zzp.t_start = time.time()
        del config.label_overrides["start"]
    ## label start, exactly as a New Game plays it: the prologue, then the
    ## sandbox loop, which the overlay driver plays.
    call start
    $ abort("label start returned (the game ended before the campus opened?)")

## The verdict, and a few screenshots from wherever the loop stopped.
label zzp_report:
    $ autoplay(False)
    $ zzp.on = False
    scene expression graded_bg()
    python:
        _secs = time.time() - zzp.t_start
        note("played", "%d days (day %s to %s) in %.0f s, %d decisions" % (
            max(0, store.day - (zzp.first_day or store.day)), zzp.first_day, store.day, _secs, len(zzp.decisions)))
        check("Go with him." in zzp.menus, "the offer took \"Go with him.\"", repr(zzp.menus))
        check(zzp.first_day is not None, "the prologue reached the sandbox loop")
        check(zzp.stuck is None, "no day got stuck", zzp.stuck or "")
        check(zzp.first_day is not None and store.day > zzp.last_day,
              "played every day to day %s" % zzp.last_day, "stopped on day %s" % store.day)

        ## Story rows finish in their order: a row found done never has a
        ## lower order than one found done before it.
        _order = {m["id"]: m["order"] for m in STORY_ROWS}
        _seq = [(d, m) for d, m in zzp.done_order if m in _order]
        _bad = [(a, b) for a, b in builtins.zip(_seq, _seq[1:]) if _order[b[1]] < _order[a[1]]]
        check(not _bad, "story rows finish in order", repr(_bad))
        note("story rows done", ", ".join("%s (day %s)" % (m, store.mission_done_day.get(m, "?")) for d, m in _seq))

        ## Every mission started also finished.
        _started = [m for d, p, m in zzp.missions]
        _open = [m for m in _started if m not in store.missions_done]
        check(not _open, "every mission started finished", repr(_open))
        note("missions started", repr(zzp.missions))

        ## The objective moved.
        _texts = [t for d, t in zzp.objectives]
        _distinct = builtins.len(builtins.set(_texts))
        check(_distinct > 3, "the objective changes over the days", "%d distinct objectives" % _distinct)
        _run, _longest, _prev = 0, (0, None), None
        for d, t in zzp.objectives:
            _run = _run + 1 if t == _prev else 1
            _prev = t
            if _run > _longest[0]:
                _longest = (_run, t)
        note("longest unchanged objective", "%d days: %s" % _longest)

        _days = builtins.len(zzp.objectives)
        note("journal renders", "%d (days logged %d)" % (zzp.journals, _days))
        note("map renders", zzp.maps)
        check(zzp.journals >= _days - 1, "the journal renders every day")
        check(zzp.maps >= _days - 1, "the map renders every day")
        note("board jobs", repr(zzp.board_jobs))
        note("board jobs held back for a story beat", repr(zzp.board_held))
        check(builtins.len(zzp.board_jobs) >= 1, "at least one board job ran")
        note("people", "; ".join("d%s %s: %s" % x for x in zzp.people))
        note("waits", zzp.waits)
        note("end state", "day %s %s at %s · grade %s · merit %s · roster %r · inventory %r" % (
            day, period, here, player_grade(), merit, roster, dict(inventory)))

        renpy.show_screen("sb_place")
        shot("view_place", wait=0.6)
        check(renpy.get_screen("sb_place") is not None, "renders sb_place at the end")
        renpy.hide_screen("sb_place")
        objective_leave()
        renpy.show_screen("journal", "missions")
        shot("view_journal_missions", wait=0.6)
        check(renpy.get_screen("journal") is not None, "renders journal(missions) at the end")
        renpy.hide_screen("journal")
        renpy.show_screen("journal", "stats")
        shot("view_journal_stats", wait=0.6)
        renpy.hide_screen("journal")
        renpy.show_screen("sb_map", layer="campus")
        shot("view_map", wait=0.6)
        check(renpy.get_screen("sb_map") is not None, "renders sb_map at the end")
        renpy.hide_screen("sb_map")
    $ finish()
