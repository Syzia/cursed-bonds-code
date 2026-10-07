## tools/smoke/u2_mksaves.rpy -- makes the nineteen saves the second UI
## overhaul is tested against (docs/UI2_DESIGN.md D42; 10.2, U0a step 3;
## written by U0a).
##
##   for m in campus sunmall warehouse roster prologue; do
##       U2_SAVES=$m SMOKE_SHOTS=<dir>/$m SMOKE_TIMEOUT=300 tools/smoke.sh u2_mksaves
##   done
##
## U0a ran this once, on commit d2eb9db (the tree before the overhaul), in a
## scratch copy that had the owner's .rpyc, and committed the saves under
## tools/smoke/assets/ui2_saves/. THEY ARE NOT MADE AGAIN: a save made by a
## later tree proves nothing about saves made by the old one. The harness is
## kept so that anyone can see exactly how each save was made.
##
## The owner's own eleven saves were all on day 1, none at Night, none in a
## file the overhaul's last package (U9) edits. These are the saves the
## overhaul is most likely to hurt. Each is named for what it holds; no test
## depends on what a slot of the owner's contains, because autosaves rotate.
##
## Each save is made from inside the interaction that is waiting, by the game
## as a New Game or the loop plays it (`jump start`, `jump sandbox`: no frame
## of this harness is on any save's call stack), then loaded at once and
## checked to come back on its own statement. The file is then copied to
## $SMOKE_SHOTS/saves/.
##
##   campus (one run inside the real loop)
##     u2-map-from-room     `call screen sb_map`, opened from my room
##     u2-room              `call screen sb_place`, standing in my room
##     u2-garden            the Dormitory Garden, one step after the exit in my room
##     u2-map-dorms         the map with the Dormitories area opened (the open
##                          area is a screen variable: it loads onto level 1)
##     u2-common-dialogue   the first line of dialogue in the Common Room, in
##                          the Evening, the sprite up (the room's foreground
##                          is not kept up in dialogue today: VIEW_FG_TALK)
##     u2-ev-scene          a spoken line inside an ev_* scene of
##                          events_arc1.rpy, the sprite up
##     u2-act-scene         a line inside an act_* scene (events_activities.rpy)
##                          reached through an activity
##     u2-girls-evening     `sb_place` in the Girls' Dormitory in the Evening,
##                          walked into during the Afternoon
##     u2-garden-night      `sb_place` in the garden on a weekday Night, Yuji
##                          and Panda on the stage
##     u2-garden-panda      `call screen sb_char("panda")` there
##     u2-night-arrival     night_out's arrival menu (Shibuya)
##     u2-after-club        night_out's after-club menu
##     u2-carry-garden      night_carry_home's line, the day having turned
##                          while I stood in the garden
##     u2-riverside-yuji    `call screen sb_char("yuji")` at the riverside on a
##                          weekend Afternoon
##   sunmall
##     u2-ch4-card          on chapter four's chapter card (ch4_mission.rpy:14, its
##                          timed pause; a load does not stop on a timed pause,
##                          so today this save lands two statements on, on the
##                          fade after the card: MOVED in the load report)
##     u2-ch4-menu          the menu at ch4_mission.rpy:117, reached from the
##                          office through start_mission and ev_mission_sunmall
##                          (its return stack holds the Pass after
##                          events_arc1.rpy:1051)
##   warehouse
##     u2-warehouse-fight   inside `call combat` at missions_arc1.rpy:67
##   roster
##     u2-roster-menu       the menu at story_arc1.rpy:353
##   prologue (label start, as a New Game plays it)
##     u2-prologue-mother   a line in ch1b_the_offer.rpy with `mother` on screen

init 999 python:
    import builtins
    import os
    import shutil
    import time

    class ZZMState(builtins.object):
        """Driver state: made at init, never reassigned, never in the store."""

        def __init__(self):
            self.mode = os.environ.get("U2_SAVES", "campus")
            self.on = False
            self.stage = 0
            self.loads = 0
            self.pending = None
            self.parked = builtins.dict()
            self.recover = builtins.list()
            self.t0 = 0.0
            self.t_stage = 0.0
            self.keep = builtins.dict()
            self.trace = builtins.list()
            self.story = None       # the story event the loop is handed, once
            self.hang = None        # the hangout event sb_activity is handed

    zzm = ZZMState()

    ZZM_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                 "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                 "intensive_done", "ijichi_rides")
    ZZM_NAMES = builtins.dict(
        campus=("room", "map-from-room", "garden", "map-dorms", "common-dialogue", "ev-scene", "act-scene",
                "girls-evening", "garden-night", "garden-panda", "night-arrival", "after-club",
                "carry-garden", "riverside-yuji"),
        sunmall=("ch4-card", "ch4-menu"),
        warehouse=("warehouse-fight",),
        roster=("roster-menu",),
        prologue=("prologue-mother",),
    )
    ZZM_SCREENS = ("combat_screen", "market_screen", "journal", "sb_map", "sb_char", "sb_place")

    def zzm_loaded():
        zzm.loads += 1

    config.after_load_callbacks.append(zzm_loaded)

    def zzm_label_cb(name, abnormal):
        if zzm.on and name in ("load_recover", "return_recover"):
            zzm.recover.append(name)

    config.label_callbacks.append(zzm_label_cb)

    ## Story beats are held back, except the one a mode asks for; a hangout
    ## is the ev_* scene the campus run names. Set at init, so the wrapper is
    ## the game's pick_event for the whole run and never a saved variable.
    zzm_real_pick = pick_event

    def zzm_pick(kind, *args, **kwargs):
        if zzm.on and kind == "story":
            e, zzm.story = zzm.story, None
            return e
        if zzm.on and kind == "hangout" and zzm.hang is not None:
            e, zzm.hang = zzm.hang, None
            return e
        return zzm_real_pick(kind, *args, **kwargs)

    def zzm_patch():
        setattr(store, "pick_event", zzm_pick)

    zzm_patch()

    def zzm_event(label):
        rows = [e for e in EVENTS if e["label"] == label]
        return rows[0] if rows else None

    def zzm_ui():
        for s in ZZM_SCREENS:
            if renpy.get_screen(s) is not None:
                return s
        if renpy.get_screen("choice") is not None:
            return "choice"
        if renpy.get_screen("input") is not None:
            return "input"
        sc = renpy.get_screen("say")
        if sc is not None and sc.scope.get("what"):
            return "say"
        if renpy.get_screen("chapter_card") is not None:
            return "card"
        return "pause"

    def zzm_sig():
        ctx = renpy.game.context()
        return (ctx.current, renpy.call_stack_depth(), store.day, store.period, store.here)

    def zzm_where():
        fn, ln = renpy.get_filename_line()
        return "%s:%d" % (fn, ln)

    def zzm_scrub():
        """Nothing of the harness goes into a save."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz")]:
            try:
                delattr(store, k)
            except Exception:
                pass

    def zzm_park(name, moves=False):
        """True once the save `name` has been made, loaded and compared. The
        first call makes the save and loads it (and does not return).
        moves=True for a save that is known to land past its statement (a
        timed pause is not somewhere a load stops): where it lands is noted,
        not checked."""
        if name in zzm.parked:
            return True
        want = zzm_sig()
        ui = zzm_ui()
        tags = builtins.sorted(renpy.get_showing_tags("master"))
        frames = [builtins.str(r) for r in renpy.game.context().return_stack]
        zzm_scrub()
        check(not store.smoke_autoplay and not store.explore_mode,
              "%s: saved as a player would save it (no test switch is on in the store)" % name)
        try:
            renpy.take_screenshot()
            renpy.save("u2-" + name)
            ok = bool(renpy.can_load("u2-" + name))
            why = "" if ok else "no file"
        except Exception:
            import traceback
            ok = False
            why = traceback.format_exc()[-1200:]
        check(ok, "%s: the save is written, from inside the interaction that is waiting" % name, why)
        note("made u2-" + name, "%s · %s · depth %d · day %s (%s) %s · here %s · waiting: %s · showing: %s" % (
            want[0], zzm_where(), want[1], want[2], weekday(), want[3], want[4], ui, ", ".join(tags)))
        note("stack u2-" + name, "; ".join(frames) or "empty")
        check(not [f for f in frames if "zz_smoke" in f], "%s: no frame of the harness is on its call stack" % name, frames)
        if not ok:
            zzm.parked[name] = False
            return True
        shot("made_" + name, wait=0)
        zzm.pending = builtins.dict(name=name, sig=want, ui=ui, loads=zzm.loads + 1, recover=len(zzm.recover), moves=moves)
        renpy.load("u2-" + name)

    def zzm_verify():
        p = zzm.pending
        zzm.pending = None
        name = p["name"]
        got = zzm_sig()
        if p["moves"]:
            check(got[1:] == p["sig"][1:], "%s: the load comes back at the same depth, day, hour and place" % name,
                  "%r, saved %r" % (got, p["sig"]))
            note("u2-%s lands past its statement" % name, "saved on %r, landed on %r at %s (a load does not stop on a timed pause)"
                 % (p["sig"][0], got[0], zzm_where()))
        else:
            check(got == p["sig"], "%s: the load comes back on its own statement, at the same depth, day, hour and place" % name,
                  "%r, saved %r" % (got, p["sig"]))
            check(zzm_ui() == p["ui"], "%s: the same thing is waiting (%s)" % (name, p["ui"]), repr(zzm_ui()))
        check(len(zzm.recover) == p["recover"], "%s: neither load_recover nor return_recover ran" % name, repr(zzm.recover))
        zzm.parked[name] = True

    def zzm_next(n=1):
        zzm.stage += n
        zzm.t_stage = time.time()
        zzm.trace.append("stage %d at day %s %s %s" % (zzm.stage, store.day, store.period, store.here))

    def zzm_button(screen, wid):
        sc = renpy.get_screen(screen)
        w = renpy.get_widget(screen, wid) if sc is not None else None
        if w is not None and not isinstance(w, renpy.display.behavior.Button):
            found = []

            def around(d):
                if isinstance(d, renpy.display.behavior.Button) and w in d.visit():
                    found.append(d)

            sc.visit_all(around)
            w = found[0] if found else None
        return w

    def zzm_must(screen, wid):
        """Press a button by id, as a click does."""
        w = zzm_button(screen, wid)
        if w is None or getattr(w, "action", None) is None:
            check(False, "stage %d: the button %s is on %s" % (zzm.stage, wid, screen))
            zzm_stop()
        renpy.display.screen.push_current_screen(renpy.get_screen(screen))
        try:
            return renpy.run(w.action)
        finally:
            renpy.display.screen.pop_current_screen()

    def zzm_offered(screen="sb_place"):
        out = []
        sc = renpy.get_screen(screen)
        if sc is None:
            return out

        def flat(a):
            if isinstance(a, (list, tuple)):
                r = []
                for x in a:
                    r.extend(flat(x))
                return r
            return [a]

        def each(d):
            for a in flat(getattr(d, "action", None)):
                if isinstance(a, Return) and isinstance(a.value, tuple):
                    out.append(a.value)

        sc.visit_all(each)
        return out

    def zzm_take(ret, what, screen="sb_place"):
        """A decision, taken only when a button of the screen offers it."""
        if ret not in zzm_offered(screen):
            check(False, "stage %d: %s offers %s" % (zzm.stage, screen, what), "%r at %s %s: %r" % (
                ret, store.here, store.period, zzm_offered(screen)))
            zzm_stop()
        return ret

    def zzm_choose(prefix=None):
        """Pick the menu choice whose caption starts with `prefix` (the first
        choice when there is none, or no prefix)."""
        ch = renpy.get_screen("choice")
        items = [i for i in ch.scope.get("items", ()) if i.action is not None]
        for i in items:
            if prefix and i.caption.startswith(prefix):
                return i.action()
        if prefix and prefix != "?":
            check(False, "stage %d: the menu offers \"%s\"" % (zzm.stage, prefix), repr([i.caption for i in items]))
            zzm_stop()
        return items[0].action()

    def zzm_set(loc, per, who=None, day=None):
        """Put me somewhere at an hour and let the loop come round again:
        "Let them go" with nobody along does nothing."""
        if day is not None and day != store.day:
            store.day = day
            store.talked_today = set()
            store.spent_today = set()
            store.actions_today = set()
            roll_gojo()
        store.here = loc
        store.period = per
        if who:
            pin(who, loc, store.day, per)
        return ("act", "release")

    def zzm_stop():
        zzm.on = False
        names = ZZM_NAMES.get(zzm.mode, ())
        missing = [n for n in names if zzm.parked.get(n) is not True]
        check(not missing, "%s: every save was made, loaded and compared (%d)" % (zzm.mode, len(names)),
              "missing: %r · stage %d · %r" % (missing, zzm.stage, zzm.trace[-4:]))
        check(not zzm.recover, "no recover label ran in the whole run", repr(zzm.recover))
        out = os.path.join(zz_smoke_state.shots, "saves")
        if not os.path.isdir(out):
            os.makedirs(out)
        n = 0
        for name in names:
            fn = "u2-" + name + renpy.savegame_suffix
            src = os.path.join(config.savedir, fn)
            if zzm.parked.get(name) is True and os.path.isfile(src):
                shutil.copyfile(src, os.path.join(out, fn))
                n += 1
        check(n == len(names), "%d save file%s copied to %s" % (n, "" if n == 1 else "s", out))
        note("run", "%s: %d loads in %.0f s; ended at stage %d" % (zzm.mode, zzm.loads, time.time() - zzm.t0, zzm.stage))
        finish()

    ## --- the campus run ----------------------------------------------------------------------

    def zzm_campus(ui):
        s = zzm.stage
        here = store.here
        if ui == "say" and s not in (11, 14, 17, 34):
            return True
        if ui in ("pause", "card"):
            return None
        if s == 0:
            ## (Not the run's very first interaction: a save needs a little
            ## history behind it to load, as every player's has.)
            if ui == "sb_place" and here == "dorm":
                zzm_next()
                return ("map",)
        elif s == 1:
            if ui == "sb_map":
                if zzm_park("map-from-room"):
                    zzm_next()
                    return zzm_must("sb_map", "map_stay")
        elif s == 2:
            if ui == "sb_place" and here == "dorm":
                if zzm_park("room"):
                    zzm.keep["clock"] = (store.day, store.period)
                    zzm_next()
                    return zzm_must("sb_place", "hot_go_dorm__dorm_yard")
        elif s == 3:
            if ui == "sb_place":
                if "garden" not in zzm.parked:
                    check(here == "dorm_yard" and (store.day, store.period) == zzm.keep["clock"],
                          "the exit in my room walks to the Dormitory Garden", (here, store.period))
                if zzm_park("garden"):
                    zzm_next()
                    return ("map",)
        elif s == 4:
            if ui == "sb_map":
                zone = renpy.get_screen("sb_map").scope.get("zone")
                if "map-dorms" not in zzm.parked:
                    if zone != "dorms":
                        zzm_must("sb_map", "area_dorms")
                        return None
                    zzm_park("map-dorms")
                zzm_next()
                return zzm_must("sb_map", "map_stay")
        ## --- the Common Room in the Evening: the first line of dialogue ------------------
        elif s == 5:
            if ui == "sb_place":
                zzm_next()
                return zzm_set("dorm_common", "Evening")
        elif s == 6:
            if ui == "sb_place":
                check(here == "dorm_common" and "yuji" in stage_people(here)[0] and view_fg_path("dorm_common"),
                      "(fixture) the Common Room in the Evening: Yuji is there, and the room has its foreground",
                      (stage_people(here), view_fg_path("dorm_common")))
                zzm_next(4)
                return zzm_take(("char", "yuji"), "Yuji")
        elif s == 10:
            if ui == "sb_char":
                zzm_next()
                return zzm_take(("do", "talk", "yuji"), "Talk", "sb_char")
        elif s == 11:
            if ui == "say":
                if "common-dialogue" not in zzm.parked:
                    check(renpy.showing("yuji") and "sb_events.rpy" in zzm_where(),
                          "the first line of dialogue in the Common Room, Yuji's sprite up", (zzm_where(), renpy.get_showing_tags("master")))
                if zzm_park("common-dialogue"):
                    zzm_next()
                    return True
        ## --- an ev_* scene, through "Spend time together" -------------------------------
        elif s == 12:
            if ui == "sb_place":
                rows = [e for e in find_events("hangout", "yuji", here) if e["label"].startswith("ev_")]
                check(bool(rows), "(fixture) an ev_* scene with Yuji is ready here", (here, store.period))
                if not rows:
                    zzm_stop()
                zzm.hang = rows[0]
                zzm.keep["ev"] = rows[0]["label"]
                zzm_next()
                return zzm_take(("char", "yuji"), "Yuji")
        elif s == 13:
            if ui == "sb_char":
                zzm_next()
                return zzm_take(("do", "hang", "yuji"), "Spend time together", "sb_char")
        elif s == 14:
            if ui == "say":
                if "ev-scene" not in zzm.parked:
                    if not ("events_arc1.rpy" in zzm_where() and renpy.showing("yuji")
                            and renpy.get_screen("say").scope.get("who")):
                        return True
                    note("ev-scene", "%s, in %s" % (zzm.keep["ev"], zzm_where()))
                if zzm_park("ev-scene"):
                    zzm_next()
                    return True
            elif ui == "choice":
                return zzm_choose()
            elif ui == "sb_place":
                check(False, "the ev_* scene stopped on a spoken line with the sprite up", zzm.keep.get("ev"))
                zzm_stop()
        ## --- an act_* scene, through an activity ---------------------------------------------
        elif s == 15:
            if ui == "choice":
                return zzm_choose()
            if ui == "sb_place":
                zzm_next()
                return zzm_set("classroom", "Morning", "megumi", day=store.day + 3)
        elif s == 16:
            if ui == "sb_place":
                zzm_next()
                return zzm_take(("char", "megumi"), "Megumi")
            if ui == "sb_char":
                return None
        elif s == 17:
            if ui == "sb_char":
                return zzm_take(("do", "study", "megumi"), "Study together", "sb_char")
            if ui == "say":
                if "act-scene" not in zzm.parked:
                    if "events_activities.rpy" not in zzm_where():
                        return True
                if zzm_park("act-scene"):
                    zzm_next()
                    return True
        ## --- the girls' corridor, walked into in the Afternoon, now the Evening ----------
        elif s == 18:
            if ui == "sb_place":
                zzm_next()
                return zzm_set("girls_dorm", "Afternoon")
        elif s == 19:
            if ui == "sb_place":
                check(here == "girls_dorm" and store.period == "Afternoon", "in the girls' corridor in the Afternoon", (here, store.period))
                store.period = "Evening"
                zzm_next()
                return ("act", "release")
        elif s == 20:
            if ui == "sb_place":
                if "girls-evening" not in zzm.parked:
                    check(here == "girls_dorm" and store.period == "Evening" and not place_access("girls_dorm")[0],
                          "the Evening finds me still inside, the corridor now closed to someone outside",
                          (here, store.period, place_access("girls_dorm")))
                if zzm_park("girls-evening"):
                    zzm_next()
                    return zzm_set("dorm_yard", "Night")
        ## --- the garden on a weekday Night ----------------------------------------------------
        elif s == 21:
            if ui == "sb_place":
                if "garden-night" not in zzm.parked:
                    check(here == "dorm_yard" and store.period == "Night" and not is_weekend()
                          and stage_people(here)[0] == ["yuji", "panda"],
                          "the garden on a weekday Night: Yuji and Panda on the stage", (weekday(), stage_people(here)))
                if zzm_park("garden-night"):
                    zzm_next()
                    return zzm_take(("char", "panda"), "Panda")
        elif s == 22:
            if ui == "sb_char":
                if zzm_park("garden-panda"):
                    zzm_next()
                    return zzm_take(("cancel",), "Back", "sb_char")
        ## --- the night out: its two menus ----------------------------------------------------
        elif s == 23:
            if ui == "sb_place":
                store.period = "Evening"
                zzm_next()
                return zzm_take(("map",), "the map")
        elif s == 24:
            if ui == "sb_map":
                sc = renpy.get_screen("sb_map")
                if sc.scope.get("view") != "tokyo":
                    zzm_must("sb_map", "map_tokyo")
                    return None
                if sc.scope.get("zone") != "shibuya":
                    zzm_must("sb_map", "district_shibuya")
                    return None
                zzm_next()
                return zzm_must("sb_map", "district_night")
        elif s == 25:
            if ui == "choice":
                if zzm_park("night-arrival"):
                    zzm_next()
                    return zzm_choose("The club")
        elif s == 26:
            if ui == "choice":
                if zzm_park("after-club"):
                    zzm_next()
                    return zzm_choose("Home")
        ## --- the day turns in the garden: night_carry_home's line ------------------------
        elif s == 27:
            if ui == "sb_place":
                zzm.keep["carry_day"] = store.day
                store.here = "dorm_yard"
                new_day()
                check(store.night_carried == "dorm_yard" and store.day == zzm.keep["carry_day"] + 1 and night_pending(),
                      "the day turns in the garden: the walk home is pending", (store.night_carried, store.day, store.here))
                zzm_next(7)
                return ("act", "release")
        elif s == 34:
            if ui == "say":
                if "carry-garden" not in zzm.parked:
                    if not ("sb_night.rpy" in zzm_where() and store.night_carried):
                        return True
                    check(store.here == "dorm_yard" and store.night_carried == "dorm_yard",
                          "the loop stops on the carry line, still in the garden", (store.here, store.night_carried))
                if zzm_park("carry-garden"):
                    zzm_next()
                    return True
        ## --- the riverside on a weekend Afternoon ------------------------------------------
        elif s == 35:
            if ui == "sb_place":
                day = store.day
                while WEEKDAYS[(day - 1) % 7] != "Sat":
                    day += 1
                zzm_next()
                return zzm_set("riverside", "Afternoon", day=day)
        elif s == 36:
            if ui == "sb_place":
                check(here == "riverside" and is_weekend() and "yuji" in stage_people(here)[0],
                      "the riverside on a weekend Afternoon: Yuji is on the stage", (weekday(), stage_people(here)))
                zzm_next()
                return zzm_take(("char", "yuji"), "Yuji")
        elif s == 37:
            if ui == "sb_char":
                if zzm_park("riverside-yuji"):
                    zzm_stop()
        return None

    ## --- the story runs ----------------------------------------------------------------------

    def zzm_story(ui):
        """sunmall, warehouse, roster: from the loop into one story scene."""
        s = zzm.stage
        mode = zzm.mode
        if s == 0:
            if ui == "sb_place":
                zzm_next()
                if mode == "roster":
                    zzm.story = zzm_event("st_roster")
                    check(zzm.story is not None, "(fixture) st_roster is a registered story event")
                    return ("act", "release")
                mid = "m_sunmall" if mode == "sunmall" else "m_nade_1"
                check(mission_status(mid) in ("available", "active") and ("mission", mid) in zzm_offered(),
                      "(fixture) the mission %s is offered in the office (%s)" % (mid, mission_status(mid)),
                      (mission_reason(mid), zzm_offered()))
                return zzm_take(("mission", mid), "the mission")
            return None
        if mode == "sunmall":
            if ui == "card" and "ch4_mission.rpy" in zzm_where():
                ## On the card's own pause, not in the fade before it.
                if type(renpy.game.script.lookup(renpy.game.context().current)).__name__ == "Python":
                    zzm_park("ch4-card", moves=True)
                return None
            if ui == "choice":
                if "ch4_mission.rpy" in zzm_where():
                    note("ch4-menu", zzm_where())
                    if zzm_park("ch4-menu"):
                        zzm_stop()
                    return None
                return zzm_choose()
        elif mode == "warehouse":
            if ui == "combat_screen":
                check("sb_combat.rpy" in zzm_where() and store.cb and store.cb.get("bg") == "bg city",
                      "inside the warehouse fight, on the picture it was handed", (zzm_where(), (store.cb or {}).get("bg")))
                if zzm_park("warehouse-fight"):
                    zzm_stop()
                return None
            if ui == "choice":
                return zzm_choose()
        elif mode == "roster":
            if ui == "choice":
                check("story_arc1.rpy" in zzm_where(), "the menu in st_roster", zzm_where())
                if zzm_park("roster-menu"):
                    zzm_stop()
                return None
        if ui == "say":
            return True
        if ui == "sb_place" and time.time() - zzm.t_stage > 6:
            check(False, "%s: the scene was entered" % mode, "back on the place view at stage %d" % s)
            zzm_stop()
        return None

    def zzm_prologue(ui):
        if ui == "say":
            if (renpy.showing("mother") and "ch1b_the_offer.rpy" in zzm_where()):
                if zzm_park("prologue-mother"):
                    zzm_stop()
                return None
            return True
        if ui == "choice":
            caps = [i.caption for i in renpy.get_screen("choice").scope.get("items", ())]
            go = [c for c in caps if c.startswith("Go with him")]
            return zzm_choose(go[0] if go else None)
        if ui == "input":
            return "Tester" if not zzm.keep.get("named") and not zzm.keep.update(named=True) else "Harness"
        if ui == "combat_screen":
            ## Read the tell, as a careful player does.
            return (ANSWERS[store.cb["kind"]],)
        if ui == "sb_place":
            check(False, "prologue: `mother` was on screen on a line of ch1b_the_offer.rpy", "the campus opened first")
            zzm_stop()
        return None

    def zzm_tick():
        if not zzm.on:
            return None
        if len(renpy.game.contexts) != 1 or not renpy.game.context().interacting:
            return None
        now = time.time()
        if now - zzm.t0 > 270 or now - zzm.t_stage > 90:
            check(False, "the driver reaches its end", "stage %d for %.0f s; %s; waiting: %r; pending %r; %r" % (
                zzm.stage, now - zzm.t_stage, zzm_where(), zzm_ui(), (zzm.pending or {}).get("name"), zzm.trace[-4:]))
            zzm_stop()
            return None
        ui = zzm_ui()
        if zzm.pending is not None:
            if zzm.loads < zzm.pending["loads"]:
                return None
            zzm_verify()
        try:
            if zzm.mode == "campus":
                return zzm_campus(ui)
            if zzm.mode == "prologue":
                return zzm_prologue(ui)
            return zzm_story(ui)
        except renpy.game.CONTROL_EXCEPTIONS:
            raise
        except Exception:
            import traceback
            check(False, "driver raised at stage %d" % zzm.stage, traceback.format_exc())
            zzm_stop()
        return None

    config.overlay_screens.append("zzm_driver")


screen zzm_driver():
    zorder 400
    if zzm.on:
        timer 0.12 repeat True action Function(zzm_tick)


label zz_smoke:
    python:
        renpy.random.seed(20261007)
        if zzm.mode not in ZZM_NAMES:
            abort("U2_SAVES must be one of %s" % ", ".join(builtins.sorted(ZZM_NAMES)))
        if zzm.mode != "prologue":
            settle(mc_name="Tester", mc_surname="Harness", day=9, period="Noon", here="dorm", yen=40000)
            for _zz_w in ROSTER_ORDER:
                if _zz_w not in store.roster:
                    store.roster.append(_zz_w)
                store.bonds[_zz_w] = 60
            for _zz_f in ZZM_FLAGS:
                if not (zzm.mode == "sunmall" and _zz_f == "sunmall_done"):
                    flag(_zz_f)
            store.done_events.add("st_roll_call")
            promote("mc", "g3", quiet=True)
            if zzm.mode == "warehouse":
                ## The story so far, recorded done by its owner's function:
                ## every story mission before The Warehouse, with the flag
                ## or event each is known by.
                for _zz_m in builtins.sorted(MISSIONS, key=lambda m: m["order"]):
                    if _zz_m["id"] == "m_nade_1":
                        break
                    if _zz_m["kind"] == "story" and mission_status(_zz_m["id"]) not in ("done", "skipped", "unwritten"):
                        for _zz_c in (_zz_m.get("done_if") or ()):
                            if _zz_c.startswith("flag:"):
                                flag(_zz_c[5:])
                            elif _zz_c.startswith("event:"):
                                store.done_events.add(_zz_c[6:])
                        complete_mission(_zz_m["id"])
                        mission_cache_clear()
                store.merit = max(store.merit, 200)
                store.day += 3
            if zzm.mode in ("sunmall", "warehouse"):
                store.here = "office"
                pin("yaga", "office", store.day, store.period)
            roll_gojo()
            refresh_vitals()
            mission_cache_clear()
            toast_clear()
        zzm_scrub()
        ## A load rolls back to here at the earliest: begin only once.
        if not zzm.on and not zzm.loads:
            zzm.on = True
            zzm.t0 = zzm.t_stage = time.time()
            if zzm.mode == "prologue":
                del config.label_overrides["start"]
    if zzm.mode == "prologue":
        jump start
    jump sandbox
