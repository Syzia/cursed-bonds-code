## tools/smoke/p2_saves.rpy -- saves are tested by saving (docs/PHASE2_DESIGN.md,
## 7 · P8; D44; R10; section 8).
##
##   SMOKE_TIMEOUT=300 tools/smoke.sh tools/smoke/p2_saves.rpy
##
## One scratch run, inside the real loop (`jump sandbox`), driven by an overlay
## timer. At each of the places below it saves from inside the interaction
## that is waiting, with the rollback log as the game left it (nothing is
## purged), loads that save at once, and compares. Each save must come back
## on its own statement, at the same call depth, day, period and place, with
## the same screen up and the same state in hand, and without load_recover or
## return_recover having run.
##
##   armory, armory_taken `call screen armory`, before and after taking a tool
##   board, board_partner `call screen board_screen`, and `call screen
##                        board_partner(...)` with a card picked
##   hub                  standing in a hub (the Dormitory Garden) after taking
##                        the exit in my room (plan 13)
##   map_area             `call screen sb_map` with an area opened by pressing
##                        its marker (the load comes back on level 1: the open
##                        area is a screen variable)
##   computer             inside `call screen pc_screen(_pc_page)`, on a page
##   journal              `call screen journal(_r[1])` with a person's page open
##   person_view          `call screen sb_char(who)`
##   dialogue             the first line of dialogue after stage_person, the
##                        eased sprite (view_enter_ease) and the foreground up
##   dialogue_rollback    the same line, reached again after a rollback through
##                        stage_person
##   blackjack            inside `call screen cards_blackjack`, a hand dealt
##   fishing_bite         `call screen fish_screen` at the bite
##   night_arrival_menu   night_out's three-way menu
##   after_club_menu      night_out's after-club menu (the Black Market / Home)
##   market               `call screen market_screen`, before a purchase
##   market_bought        the same, after one
##   ridge_night          `call screen sb_place` at Night on the ridge, on the
##                        night Gojo asked for
##   gojo_menu            sb_do_night_gojo's menu
##   gojo_morning         the line "Day N. Morning." that follows the night
##   rest_day             `call screen sb_place` on the rest day after it
##
## Not here: a save inside a fight (combat_screen) or on the grade card. Both
## are phase 1's, the owner's phase-1 saves cover them (tools/load_all_saves.sh),
## and phase 3 rebuilds the fight.
##
## The driver's own state is one builtins object made at init (zzs): a load
## and a rollback leave it alone. Its stage counter is compared across every
## load ("a builtins stage counter survives the load"): a counter kept in the
## store would be rolled back with the game.
##
## Text is not skipped (the eased sprite needs that): the driver clicks each
## line on, and picks each menu's choice itself. Story beats are held back
## (pick_event answers None for the kind "story") so the fixture stays where
## the driver puts it; everything else is the game's own code.
##
## Screenshots (shots/p2_saves/): park_<name>.png as each save is made.

init 999 python:
    import builtins
    import time

    class ZZSState(builtins.object):
        """Driver state: made at init, never reassigned, never in the store."""

        def __init__(self):
            self.on = False
            self.stage = -8
            self.loads = 0
            self.pending = None
            self.parked = builtins.dict()      # name -> True when its round trip was checked
            self.recover = builtins.list()     # recover labels seen
            self.labels = builtins.list()
            self.t0 = 0.0
            self.t_stage = 0.0
            self.ticks = 0
            self.rb_tries = 0
            self.keep = builtins.dict()
            self.trace = builtins.list()

    zzs = ZZSState()

    ZZS_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                 "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                 "intensive_done", "ijichi_rides")
    ZZS_WHO = "yuji"
    ZZS_DISTRICT = "shibuya"
    ZZS_SCREENS = ("market_screen", "pc_screen", "fish_screen", "cards_blackjack", "cards_poker",
                   "cards_table", "armory", "board_partner", "board_screen", "journal", "sb_map", "sb_char", "sb_place")
    ZZS_NAMES = ("armory", "armory_taken", "board", "board_partner", "hub", "map_area", "computer", "journal",
                 "person_view", "dialogue", "dialogue_rollback", "blackjack",
                 "fishing_bite", "night_arrival_menu", "after_club_menu", "market", "market_bought",
                 "ridge_night", "gojo_menu", "gojo_morning", "rest_day")

    def zzs_loaded():
        zzs.loads += 1

    config.after_load_callbacks.append(zzs_loaded)

    def zzs_label_cb(name, abnormal):
        if not zzs.on:
            return
        if len(zzs.labels) < 600:
            zzs.labels.append(name)
        if name in ("load_recover", "return_recover"):
            zzs.recover.append(name)

    config.label_callbacks.append(zzs_label_cb)

    ## No story beat is picked while the driver runs.
    zzs_real_pick = pick_event

    def zzs_no_story(kind, *args, **kwargs):
        if zzs.on and kind == "story":
            return None
        return zzs_real_pick(kind, *args, **kwargs)

    def zzs_patch():
        """Set at init, so the wrapper is the game's pick_event for the whole
        run and never a saved variable."""
        store.pick_event = zzs_no_story

    zzs_patch()

    def zzs_ui():
        """What is waiting: a loop screen, "choice", "say", or None."""
        for s in ZZS_SCREENS:
            if renpy.get_screen(s) is not None:
                return s
        if renpy.get_screen("choice") is not None:
            return "choice"
        sc = renpy.get_screen("say")
        if sc is not None and sc.scope.get("what"):
            return "say"
        return None

    def zzs_sig():
        ctx = renpy.game.context()
        return (ctx.current, renpy.call_stack_depth(), store.day, store.period, store.here)

    def zzs_where():
        fn, ln = renpy.get_filename_line()
        return "%s:%d" % (fn, ln)

    def zzs_scrub():
        """Nothing of the harness goes into a save."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz")]:
            try:
                delattr(store, k)
            except Exception:
                pass

    def zzs_park(name, state=None):
        """True once the save `name` has been made, loaded and compared.
        The first call makes the save and loads it (and does not return);
        the tick after the load compares (zzs_verify)."""
        if name in zzs.parked:
            return True
        want = zzs_sig()
        ui = zzs_ui()
        st = state() if state is not None else None
        entries = len(renpy.game.log.log)
        zzs_scrub()
        try:
            renpy.take_screenshot()
            renpy.save("zzs_" + name)
            ok = bool(renpy.can_load("zzs_" + name))
            why = "" if ok else "no file"
        except Exception as e:
            import traceback
            ok = False
            why = traceback.format_exc()[-1200:]
        check(ok, "%s: the save is written, from inside the interaction, the rollback log untrimmed" % name, why)
        note("parked " + name, "%s · %s · depth %d · day %s %s %s · %s · log %d entries" % (
            want[0], zzs_where(), want[1], want[2], want[3], want[4], ui, entries))
        if not ok:
            zzs.parked[name] = False
            return True
        shot("park_" + name, wait=0)
        zzs.pending = builtins.dict(name=name, sig=want, ui=ui, state=st, fn=state, loads=zzs.loads + 1,
                                    stage=zzs.stage, recover=len(zzs.recover))
        renpy.load("zzs_" + name)

    def zzs_verify():
        p = zzs.pending
        zzs.pending = None
        name = p["name"]
        got = zzs_sig()
        check(got[0] == p["sig"][0], "%s: the load comes back on its own statement" % name, "%r, saved on %r" % (got[0], p["sig"][0]))
        check(got[1:] == p["sig"][1:], "%s: the same call depth, day, period and place" % name, "%r, saved %r" % (got[1:], p["sig"][1:]))
        check(zzs_ui() == p["ui"], "%s: the same screen is waiting (%s)" % (name, p["ui"]), repr(zzs_ui()))
        if p["fn"] is not None:
            st = p["fn"]()
            check(st == p["state"], "%s: the state in hand is as saved" % name, "%r, saved %r" % (st, p["state"]))
        check(len(zzs.recover) == p["recover"], "%s: neither load_recover nor return_recover ran" % name, repr(zzs.recover))
        check(zzs.stage == p["stage"] and zzs.loads == p["loads"],
              "%s: the builtins stage counter survives the load" % name, "stage %r (was %r), loads %r" % (zzs.stage, p["stage"], zzs.loads))
        zzs.parked[name] = True

    def zzs_next(n=1):
        zzs.stage += n
        zzs.t_stage = time.time()
        zzs.trace.append("stage %d at %s %s %s" % (zzs.stage, store.day, store.period, store.here))

    def zzs_button(screen, wid):
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

    def zzs_press(screen, wid):
        """Press a button by id, as a click does. "zz_missing" when it isn't
        there."""
        w = zzs_button(screen, wid)
        if w is None or getattr(w, "action", None) is None:
            return "zz_missing"
        renpy.display.screen.push_current_screen(renpy.get_screen(screen))
        try:
            return renpy.run(w.action)
        finally:
            renpy.display.screen.pop_current_screen()

    def zzs_must(screen, wid):
        v = zzs_press(screen, wid)
        if v == "zz_missing":
            check(False, "stage %d: the button %s is on %s" % (zzs.stage, wid, screen))
            zzs_stop()
        return v

    def zzs_offered(screen="sb_place"):
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

    def zzs_take(ret, what):
        """A place-view decision, taken only when a button offers it."""
        if ret not in zzs_offered():
            check(False, "stage %d: the place view offers %s" % (zzs.stage, what), "%r at %s %s: %r" % (
                ret, store.here, store.period, zzs_offered()))
            zzs_stop()
        return ret

    def zzs_choose(prefix):
        """Pick the menu choice whose caption starts with `prefix`."""
        ch = renpy.get_screen("choice")
        items = [i for i in ch.scope.get("items", ()) if i.action is not None]
        for i in items:
            if i.caption.startswith(prefix):
                return i.action()
        check(False, "stage %d: the menu offers \"%s\"" % (zzs.stage, prefix), repr([i.caption for i in items]))
        zzs_stop()

    def zzs_captions():
        ch = renpy.get_screen("choice")
        if ch is None:
            return None
        return [i.caption for i in ch.scope.get("items", ()) if i.action is not None]

    def zzs_tags():
        return builtins.sorted(builtins.set(renpy.get_showing_tags("master")) & builtins.set([ZZS_WHO, "view_fg"]))

    def zzs_eased():
        """The sprite's transform is the ATL transform view_enter_ease."""
        try:
            d = renpy.game.context().scene_lists.get_displayable_by_tag("master", ZZS_WHO)
        except Exception:
            d = None
        for _i in range(6):
            if d is None:
                return False
            if isinstance(d, renpy.display.transform.ATLTransform):
                return d.atl is view_enter_ease.atl
            d = getattr(d, "child", None)
        return False

    def zzs_st_dialogue():
        return (zzs_tags(), zzs_eased())

    def zzs_st_hub():
        room = builtins.sorted(h["id"] for h in hot_spots_for(store.here) if str(h["act"]).startswith("path_"))
        col = builtins.sorted(a[0] for a in rail_actions(store.here) if a[0].startswith("path_"))
        return (room, col)

    def zzs_st_pc():
        sc = renpy.get_screen("pc_screen")
        return (sc.scope.get("page") if sc is not None else None, builtins.sorted(store.pc_read), store._pc_page)

    def zzs_st_cards():
        st = store.cards_state or {}
        sit = store.cards_sit or {}
        return (st.get("game"), st.get("stage"), builtins.list(st.get("mine") or ()), builtins.list(st.get("dealer") or ()),
                st.get("stake"), st.get("hands"), builtins.list(sit.get("opponents") or ()), store.yen)

    def zzs_st_fish():
        st = store.fish_state or {}
        return (st.get("cast"), st.get("kind"), st.get("centre"), st.get("settled"), fish_phase())

    def zzs_st_market():
        return (store.yen, builtins.sorted(store.market_bought), [(r[0], r[2]) for r in market_rows()])

    def zzs_st_gear():
        return (store.equipped_tool, builtins.list(store.equipped_talismans), builtins.sorted(store.inventory.items()),
                builtins.sorted(v for v in zzs_offered("armory") + zzs_offered("board_screen") + zzs_offered("board_partner")))

    def zzs_st_place():
        return (builtins.sorted(set(v for v in zzs_offered() if v[0] in ("act", "mission"))),
                builtins.list(stage_people(store.here)[0]), night_tag(), night_can_work())

    def zzs_talk():
        """Talk, from the person view, when its button is there."""
        ret = ("do", "talk", ZZS_WHO)
        if ret not in zzs_offered("sb_char"):
            check(False, "stage %d: the person view offers Talk" % zzs.stage, zzs_offered("sb_char"))
            zzs_stop()
        return ret

    def zzs_set(loc, per, who=None):
        """Put me somewhere at an hour, with someone there, and let the loop
        come round again: "Let them go" with nobody along does nothing."""
        store.here = loc
        store.period = per
        if who:
            pin(who, loc, store.day, per)
        return ("act", "release")

    def zzs_stop():
        zzs.on = False
        missing = [n for n in ZZS_NAMES if zzs.parked.get(n) is not True]
        check(not missing, "every save was made, loaded and compared (%d)" % len(ZZS_NAMES), "missing: %r · stage %d · %r" % (
            missing, zzs.stage, zzs.trace[-4:]))
        check(not zzs.recover, "no recover label ran in the whole run", repr(zzs.recover))
        check(zzs.loads == len([n for n in zzs.parked if zzs.parked[n] is True]),
              "one load for each save", "%d loads, %d saves" % (zzs.loads, len(zzs.parked)))
        note("run", "%d loads in %.0f s; ended at stage %d, day %s %s %s" % (
            zzs.loads, time.time() - zzs.t0, zzs.stage, store.day, store.period, store.here))
        finish()

    def zzs_step(ui):
        s = zzs.stage
        here = store.here

        ## Lines are clicked on, except where a stage parks on one.
        if ui == "say" and s not in (12, 14, 33):
            return True

        ## --- the armory, a tool taken ---------------------------------------------------
        if s == -8:
            if ui == "sb_place":
                zzs_next()
                return zzs_set("storehouse", "Noon")
        elif s == -7:
            if ui == "sb_place":
                zzs_next()
                return zzs_take(("act", "armory"), "the armory")
        elif s == -6:
            if ui == "armory":
                if zzs_park("armory", zzs_st_gear):
                    if "armory_taken" not in zzs.parked and not zzs.keep.get("tool"):
                        takes = [v for v in zzs_offered("armory") if v[0] == "take"]
                        check(bool(takes), "the armory offers a tool to take", zzs_offered("armory"))
                        if not takes:
                            zzs_stop()
                        zzs.keep["tool"] = takes[0][1]
                        return takes[0]
                    if "armory_taken" not in zzs.parked:
                        check(has_item(zzs.keep["tool"]), "taking a tool puts it in my inventory", zzs.keep["tool"])
                    if zzs_park("armory_taken", zzs_st_gear):
                        check(has_item(zzs.keep["tool"]), "armory_taken: the tool is still mine after the load", zzs.keep["tool"])
                        zzs_next()
                        return ("close",)
        ## --- the board, and who comes ---------------------------------------------------
        elif s == -5:
            if ui == "sb_place":
                zzs_next()
                return zzs_set("utahime_office", "Noon", "utahime")
        elif s == -4:
            if ui == "sb_place":
                zzs_next()
                return zzs_take(("act", "board"), "the board")
        elif s == -3:
            if ui == "board_screen":
                if zzs_park("board", zzs_st_gear):
                    takes = [v for v in zzs_offered("board_screen") if v[0] == "take"]
                    check(bool(takes), "the board offers a card to take", zzs_offered("board_screen"))
                    if not takes:
                        zzs_stop()
                    zzs_next()
                    return takes[0]
        elif s == -2:
            if ui == "board_partner":
                if zzs_park("board_partner", zzs_st_gear):
                    zzs_next()
                    return ("cancel",)
        elif s == -1:
            if ui == "board_screen":
                return ("close",)
            if ui == "sb_place":
                zzs_next()
                return zzs_set("dorm", "Noon")
        ## --- a hub, after an exit ---------------------------------------------------
        elif s == 0:
            if ui == "sb_place" and here == "dorm":
                zzs.keep["clock"] = (store.day, store.period, store.stamina)
                zzs_next()
                return zzs_must("sb_place", "hot_go_dorm__dorm_yard")
        elif s == 1:
            if ui == "sb_place":
                if "hub" not in zzs.parked:
                    check(here == "dorm_yard" and (store.day, store.period, store.stamina) == zzs.keep["clock"],
                          "the exit in my room walks to the Dormitory Garden, no time spent", (here, store.period))
                if zzs_park("hub", zzs_st_hub):
                    zzs_next()
                    return ("map",)
        ## --- the map, an area open ---------------------------------------------------
        elif s == 2:
            if ui == "sb_map":
                zone = renpy.get_screen("sb_map").scope.get("zone")
                if "map_area" not in zzs.parked:
                    if zone != "dorms":
                        zzs_must("sb_map", "area_dorms")
                        return None
                    zzs_park("map_area")
                check(zone is None, "map_area: the load comes back on level 1 (the open area is a screen variable)", repr(zone))
                zzs_next()
                zzs_must("sb_map", "area_dorms")
        elif s == 3:
            if ui == "sb_map":
                zzs_next()
                return zzs_must("sb_map", "row_dorm")
        ## --- my computer ---------------------------------------------------------------
        elif s == 4:
            if ui == "sb_place":
                check(here == "dorm", "the map's pin, pressed after the load, walks to my room", here)
                zzs_next()
                return zzs_take(("act", "pc_open"), "My computer")
        elif s == 5:
            if ui == "pc_screen":
                page = renpy.get_screen("pc_screen").scope.get("page")
                if page == PC_HOME and "computer" not in zzs.parked:
                    todo = [p for p in pc_pages() if p not in (PC_HOME, PC_BOARD_PAGE)]
                    zzs.keep["page"] = todo[0]
                    return zzs_must("pc_screen", "pc_mark_" + todo[0])
                if "computer" not in zzs.parked:
                    check(page == zzs.keep.get("page") and pc_has_read(page), "the bookmark opens its page, and the page is read", page)
                if zzs_park("computer", zzs_st_pc):
                    zzs_next()
                    return zzs_must("pc_screen", "pc_close")
        ## --- the journal, a person's page ----------------------------------------------
        elif s == 6:
            if ui == "sb_place":
                zzs_next()
                return zzs_take(("journal", "people"), "the journal")
        elif s == 7:
            if ui == "journal":
                js = renpy.get_screen("journal").scope.get("js") or {}
                if "journal" not in zzs.parked:
                    if js.get("sel") != ZZS_WHO:
                        zzs_must("journal", "jr_card_" + ZZS_WHO)
                        return None
                    zzs_park("journal")
                check(js.get("sel") is None and js.get("tab") == "people",
                      "journal: the load comes back on the People tab, no page open (the view state is the screen's)",
                      (js.get("tab"), js.get("sel")))
                zzs_next()
                return zzs_must("journal", "jr_return")
        ## --- the first line after stage_person ----------------------------------------
        elif s == 8:
            if ui == "sb_place":
                zzs_next()
                return zzs_set("cafeteria", "Noon", ZZS_WHO)
        elif s == 9:
            if ui == "sb_place":
                check(here == "cafeteria" and view_fg_path("cafeteria"), "the cafeteria has a foreground picture", view_fg_path("cafeteria"))
                zzs_next()
                return zzs_take(("char", ZZS_WHO), "Yuji")
        elif s == 10:
            if ui == "sb_char":
                if zzs_park("person_view", lambda: builtins.sorted(zzs_offered("sb_char"))):
                    check(not zzs_tags(), "in the person view nothing of stage_person is on the master layer", zzs_tags())
                    zzs_next(2)
                    return zzs_talk()
        elif s == 12:
            if ui == "say":
                if "dialogue" not in zzs.parked:
                    zzs.keep["line"] = zzs_sig()[0]
                    check(zzs_tags() == builtins.sorted([ZZS_WHO, "view_fg"]) and zzs_eased() and "sb_events.rpy" in zzs_where(),
                          "the first line after stage_person: the eased sprite (view_enter_ease) and the foreground are up",
                          (zzs_tags(), zzs_eased(), zzs_where()))
                if zzs_park("dialogue", zzs_st_dialogue):
                    zzs_next()
                    zzs.rb_tries = 1
                    renpy.rollback(force=True, checkpoints=1)
        elif s == 13:
            if ui == "sb_char":
                check(not zzs_tags(), "rolling back through stage_person leaves no sprite and no foreground behind", zzs_tags())
                note("rollback", "back on the person view after %d checkpoint(s)" % zzs.rb_tries)
                zzs_next()
                return zzs_talk()
            if ui == "sb_place":
                check(not zzs_tags(), "rolling back through stage_person leaves no sprite and no foreground behind", zzs_tags())
                note("rollback", "back on the place view after %d checkpoint(s)" % zzs.rb_tries)
                return ("char", ZZS_WHO)
            if ui == "say":
                if zzs.rb_tries >= 4:
                    check(False, "a rollback from the line passes stage_person", "still on the line after %d tries" % zzs.rb_tries)
                    zzs_next()
                    return None
                zzs.rb_tries += 1
                renpy.rollback(force=True, checkpoints=zzs.rb_tries)
        elif s == 14:
            if ui == "sb_char":
                return zzs_talk()
            if ui == "say":
                if "dialogue_rollback" not in zzs.parked:
                    check(zzs_sig()[0] == zzs.keep.get("line") and zzs_tags() == builtins.sorted([ZZS_WHO, "view_fg"]) and zzs_eased(),
                          "playing forward again reaches the same line, the eased sprite and the foreground back",
                          (zzs_sig()[0], zzs.keep.get("line"), zzs_tags(), zzs_eased()))
                if zzs_park("dialogue_rollback", zzs_st_dialogue):
                    zzs_next()
                    return True
        ## --- blackjack -------------------------------------------------------------------
        elif s == 15:
            if ui == "sb_place":
                check(not zzs_tags(), "back in the place view the scene's sprite and foreground are gone", zzs_tags())
                zzs_next()
                return zzs_set("dorm_common", "Afternoon", ZZS_WHO)
        elif s == 16:
            if ui == "sb_place":
                zzs_next()
                return zzs_take(("act", "cards_play"), "Play cards")
        elif s == 17:
            if ui == "cards_table":
                zzs_next()
                return zzs_must("cards_table", "cards_game_blackjack")
        elif s == 18:
            if ui == "cards_blackjack":
                if zzs_park("blackjack", zzs_st_cards):
                    ## The move buttons are deaf for the screen's first 0.3 s.
                    stage = (store.cards_state or {}).get("stage")
                    v = zzs_must("cards_blackjack", "cards_stand" if stage == "play" else "cards_leave")
                    if v is not None and stage != "play":
                        zzs_next()
                    return v
        elif s == 19:
            if ui == "cards_table":
                zzs_next()
                return zzs_must("cards_table", "cards_leave")
        ## --- the river, at the bite ---------------------------------------------------
        elif s == 20:
            if ui == "sb_place":
                zzs_next()
                return zzs_set("riverside", "Afternoon")
        elif s == 21:
            if ui == "sb_place":
                zzs_next()
                return zzs_take(("act", "fish_cast"), "Fish")
        elif s == 22:
            if ui == "fish_screen":
                if "fishing_bite" not in zzs.parked and fish_phase() != "bite":
                    return None
                if zzs_park("fishing_bite", zzs_st_fish):
                    if fish_phase() != "bite":
                        return None
                    zzs_next()
                    return zzs_must("fish_screen", "fish_water")
        elif s == 23:
            if ui == "fish_screen":
                zzs_next()
                return zzs_must("fish_screen", "fish_leave")
        ## --- the night out: its two menus, and the market ---------------------------
        elif s == 24:
            if ui == "sb_place":
                store.period = "Evening"
                zzs_next()
                return zzs_take(("map",), "the map")
        elif s == 25:
            if ui == "sb_map":
                sc = renpy.get_screen("sb_map")
                if sc.scope.get("view") != "tokyo":
                    zzs_must("sb_map", "map_tokyo")
                    return None
                if sc.scope.get("zone") != ZZS_DISTRICT:
                    zzs_must("sb_map", "district_" + ZZS_DISTRICT)
                    return None
                zzs_next()
                return zzs_must("sb_map", "district_night")
        elif s == 26:
            if ui == "choice":
                if zzs_park("night_arrival_menu", zzs_captions):
                    zzs_next()
                    return zzs_choose("The club")
        elif s == 27:
            if ui == "choice":
                if "after_club_menu" not in zzs.parked:
                    check(zzs_captions() == ["The Black Market", "Home"] and has_flag("market_found"),
                          "after the club the market is found, and the menu offers it", zzs_captions())
                if zzs_park("after_club_menu", zzs_captions):
                    zzs_next()
                    return zzs_choose("The Black Market")
        elif s == 28:
            if ui == "market_screen":
                if zzs_park("market", zzs_st_market):
                    rows = [r for r in market_rows() if r[2] == "buy"]
                    zzs.keep["buy"] = (rows[-1][0], rows[-1][1], store.yen, item_count(rows[-1][0]))
                    zzs_next()
                    return zzs_must("market_screen", "market_buy_" + rows[-1][0])
        elif s == 29:
            if ui == "market_screen":
                iid, price, yen0, n0 = zzs.keep["buy"]
                if "market_bought" not in zzs.parked:
                    check(store.yen == yen0 - price and item_count(iid) == n0 + 1, "Buy takes the yen and gives the item", (iid, store.yen, yen0))
                if zzs_park("market_bought", zzs_st_market):
                    check(store.yen == yen0 - price and item_count(iid) == n0 + 1, "market_bought: the purchase is still made after the load",
                          (iid, store.yen, yen0, item_count(iid)))
                    zzs_next()
                    return zzs_must("market_screen", "market_close")
        ## --- Night on the ridge, Gojo's menu, the rest day ----------------------------
        elif s == 30:
            if ui == "sb_place":
                check(here == "dorm" and night_tag() == NIGHT_TAGS["out"], "the morning after the night out: my room, a rough morning", (here, night_tag()))
                zzs.keep["day"] = store.day
                night_dev("gojo")
                zzs_next()
                return zzs_set(NIGHT_GOJO["place"], PERIODS[-1])
        elif s == 31:
            if ui == "sb_place":
                if "ridge_night" not in zzs.parked:
                    check(here == NIGHT_GOJO["place"] and store.period == PERIODS[-1] and ("act", "night_gojo") in zzs_offered()
                          and "gojo" in stage_people(here)[0],
                          "Night on the ridge, the night he asked for: Gojo is there and Train until morning is offered",
                          (here, store.period, zzs_offered(), stage_people(here)))
                if zzs_park("ridge_night", zzs_st_place):
                    zzs_next()
                    return zzs_take(("act", "night_gojo"), "Train until morning")
        elif s == 32:
            if ui == "choice":
                if zzs_park("gojo_menu", zzs_captions):
                    zzs_next()
                    return zzs_choose("Stay.")
        elif s == 33:
            if ui == "say":
                ## "Day N. Morning.", the line after the night's new_day().
                if "sb_night.rpy" in zzs_where() and store.day == zzs.keep["day"] + 1:
                    if zzs_park("gojo_morning", lambda: (night_tag(), store.night_gojo_last, store.control, store.ce_max)):
                        return True
                    return None
                return True
            if ui == "sb_place":
                if "rest_day" not in zzs.parked:
                    check(here == "dorm" and store.day == zzs.keep["day"] + 1 and not night_can_work() and night_tag() == NIGHT_TAGS["gojo"],
                          "the morning after: my room, a rest day", (here, store.day, night_tag()))
                if zzs_park("rest_day", zzs_st_place):
                    check(not night_can_work() and night_tag() == NIGHT_TAGS["gojo"], "rest_day: still a rest day after the load", night_tag())
                    zzs_next()
                    zzs_stop()
        return None

    def zzs_tick():
        if not zzs.on:
            return None
        if len(renpy.game.contexts) != 1 or not renpy.game.context().interacting:
            return None
        zzs.ticks += 1
        now = time.time()
        if now - zzs.t0 > 240 or now - zzs.t_stage > 45:
            check(False, "the driver reaches its end", "stage %d for %.0f s; %s; waiting: %r; pending %r; %r" % (
                zzs.stage, now - zzs.t_stage, zzs_where(), zzs_ui(), (zzs.pending or {}).get("name"), zzs.trace[-4:]))
            zzs_stop()
            return None
        ui = zzs_ui()
        if ui is None:
            return None
        if zzs.pending is not None:
            if zzs.loads < zzs.pending["loads"]:
                return None
            zzs_verify()
        try:
            return zzs_step(ui)
        except renpy.game.CONTROL_EXCEPTIONS:
            raise
        except Exception:
            import traceback
            check(False, "driver raised at stage %d" % zzs.stage, traceback.format_exc())
            zzs_stop()
        return None

    config.overlay_screens.append("zzs_driver")


screen zzs_driver():
    zorder 400
    if zzs.on:
        timer 0.15 repeat True action Function(zzs_tick)


label zz_smoke:
    python:
        renpy.random.seed(20261004)
        settle(mc_name="Tester", mc_surname="Harness", day=12, period="Noon", here="dorm", yen=40000)
        for _zz_w in ROSTER_ORDER:
            if _zz_w not in store.roster:
                store.roster.append(_zz_w)
            store.bonds[_zz_w] = 60
        for _zz_f in ZZS_FLAGS:
            flag(_zz_f)
        store.done_events.add("st_roll_call")
        promote("mc", "g3", quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()
        zzs_scrub()
        ## A load rolls back to here at the earliest: begin only once.
        if not zzs.on and not zzs.loads:
            zzs.on = True
            zzs.t0 = zzs.t_stage = time.time()
    jump sandbox
