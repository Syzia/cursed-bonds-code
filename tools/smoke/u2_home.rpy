## tools/smoke/u2_home.rpy -- my room moves into the Boys' Dormitory (the second
## UI overhaul, package U0b: docs/UI2_DESIGN.md 4.2, 4.3, 4.4, 10.2 "U0b").
##
##   SMOKE_TIMEOUT=420 tools/smoke.sh u2_home
##
## My room keeps its key, "dorm", and everything that means "home" still
## says it by name. What moved is the door: my room opens onto the corridor
## of the Boys' Dormitory (boys_dorm), which opens onto the garden. Three
## friends' rooms open off the same corridor, behind doors that ask a Bond
## level, and at Night their owners are in them, awake or asleep.
##
## Part 1, read straight from the game's tables and functions:
##   A  home: the key, the picture, the label, the default; the house table
##   B  exits: the garden's seven, the corridor's five, my room's one; from my
##      room every place is reached by exits alone; the validators are clean,
##      and each new rule fails when its table is broken on purpose
##   C  label path_walk and the 24 old sb_do_path_ labels are textually what
##      they were before the overhaul (their block of room_paths.rpy, hashed)
##      and keep their statement names, as label sb_do_veil does
##   D  the Night: the four boys in their rooms on all seven days, the garden
##      and the Common Room empty; who is asleep; a sleeper is counted where
##      they are, is not on the stage, is captioned "asleep", and offers
##      nothing, a mission of theirs included; world_home_state; a companion,
##      a story pin and a flag schedule each keep someone awake; "asleep"
##      comes ahead of a story caption; screen map_area reads map_marks()
##   E  doors: shut at Bond 14 with their line, open at 15, at Noon with the
##      owner out and at Night with the owner asleep; the shared room on
##      either owner's Bond; the flag door_<place>
##   F  the map: six pins in the Dormitories, none for a room inside a house
## Part 2, the game's own labels under autoplay:
##   G  "Go to bed" from every place at Night ends in my room the next
##      morning; the day turning in each place walks me home with its line; a
##      Gojo night, a night out and the Sun Mall end in my room
## Part 3, inside the real loop (`jump sandbox`), driven by an overlay timer
## that presses what the screens offer:
##   H  on foot: garden -> corridor -> my room, a save made and loaded at each
##      step (each comes back on its own statement); a rollback through the
##      walk, step by step; back out to the garden; no time spent
##   I  by map: Dormitories, then my room's pin
##   J  walking into each friend's room at Night runs the walk and nothing
##      else (K16); who is on the stage there; I can always walk out
##   K  a shut door in the corridor: the lock, its line, and it does nothing
##   L  three of the saves made before the overhaul (tools/smoke/assets/
##      ui2_saves/, copied into the scratch save folder): the garden on a
##      weekday Night, the person view of Panda there, and the garden one
##      step after walking out of my room (a rollback lands in my room, and
##      my room's door now leads to the corridor)
##
## The driver's state is one builtins object (zzh): a load and a rollback
## leave it alone. Story beats are held back while it runs (pick_event answers
## None for the kind "story"). It presses buttons through their actions: it
## neither hovers nor moves the pointer.
##
## U0c1 (docs/UI2_DESIGN.md 10.2 "U0c1", 4.1 to 4.5) added the other seven
## places and the rest of the Night, and this harness follows them: the
## sections above also cover the two girls' rooms, the teachers' house, the
## Onsen with its sauna and the pool; and
##   M  a save made in each of the seven new places reloads there
##   N  Nobara's room in the Afternoon as her companion, with no Bond; Wait to
##      Evening; the way out works (a house is always open from its own rooms)
##   O  the Teachers' Dormitory at Night: Yaga up, Utahime and Ijichi asleep
##
## Screenshots (shots/u2_home/): worst_<place>.png for ten of the new
## places and the three yards that gained an exit (R6's worst case),
## park_<name>.png as each save is made,
## place_<room>.png, map_dorms.png and map_<area>.png for the three other
## areas that gained a pin.

init 999 python:
    import builtins
    import copy
    import hashlib
    import json
    import os
    import shutil
    import time

    class ZZHState(builtins.object):
        """Driver state: made at init, never reassigned, never in the store."""

        def __init__(self):
            self.on = False
            self.stage = 0
            self.loads = 0
            self.pending = None
            self.parked = builtins.dict()
            self.recover = builtins.list()
            self.labels = builtins.list()
            self.said = builtins.list()       # lines said from python (renpy.say)
            self.texts = builtins.list()      # lines and captions of statements
            self.tries = 0
            self.t0 = 0.0
            self.t_stage = 0.0
            self.keep = builtins.dict()
            self.trace = builtins.list()
            self.boot = None
            self.i = 0
            self.rows = builtins.list()

    zzh = ZZHState()

    ZZH_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                 "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                 "intensive_done", "ijichi_rides", "met_second_years")
    ZZH_SCREENS = ("journal", "sb_map", "sb_char", "sb_place")
    ZZH_ROOMS = ("yuji_room", "megumi_room", "senpai_room")
    ## U0c1's seven, in the order they were appended.
    ZZH_SEVEN = ("nobara_room", "maki_room", "teachers_lounge", "teachers_dorm", "bathhouse", "sauna", "pool")
    ZZH_GIRLS = ("nobara_room", "maki_room")
    ## Everyone who lives on campus, and where (WORLD_HOMES, 3.2).
    ZZH_HOMES = builtins.dict(yuji="yuji_room", megumi="megumi_room", panda="senpai_room", toge="senpai_room",
                              nobara="nobara_room", maki="maki_room", shoko="infirmary",
                              yaga="teachers_dorm", utahime="teachers_dorm", ijichi="teachers_dorm")
    ZZH_CORRIDOR = ("I am not walking into the girls' dormitory after dark uninvited. "
                    "That is how people get nailed to things.")
    ZZH_KNOCK = "I don't know her well enough to knock."
    ZZH_OLD_LABELS = ("gate", "courtyard", "classroom", "cafeteria", "training", "dojo", "dorm_common", "dorm",
                      "girls_dorm", "rooftop", "infirmary", "office", "utahime_office", "gojo_office",
                      "storehouse", "forest", "riverside", "ridge", "library", "school_yard", "dorm_yard",
                      "staff_yard", "training_yard", "trailhead")
    ## label path_walk and the 24 labels after it, as they were at commit
    ## 42cfd6d (the tree before the overhaul touched a game file): the sha256
    ## of that block of game/room_paths.rpy, and its length.
    ZZH_WALK_BLOCK = ("f8b818a8cf1e6852115065cd10f37370db5272baeee7a331610af76f516c6001", 1845)
    ## The statement names of that block and of label sb_do_veil, as the
    ## owner's .rpyc held them before the overhaul: (how many, a hash of the
    ## sorted names and kinds; a line of dialogue's kind reads TranslateSay
    ## in a running game). Both were read back from the owner's own
    ## room_paths.rpyc and sb_world.rpyc of before U0b and are the same 102
    ## and 30 names. A tree with no .rpyc copied in from the
    ## owner's folder gets new names and fails these two lines (as
    ## u2_baseline's names do, for the same reason).
    ZZH_WALK_NAMES = (102, "5ef4c1b6e6c3953fc4a8f537")
    ZZH_VEIL_NAMES = (30, "694e4af07c07143b8fcdafea")
    ZZH_SAVES = ("u2-garden-night", "u2-garden-panda", "u2-garden")

    def zzh_loaded():
        zzh.loads += 1

    config.after_load_callbacks.append(zzh_loaded)

    def zzh_label_cb(name, abnormal):
        if len(zzh.labels) < 4000:
            zzh.labels.append(name)
        if zzh.on and name in ("load_recover", "return_recover"):
            zzh.recover.append(name)

    config.label_callbacks.append(zzh_label_cb)

    ## Every line said, by a statement or by python (the walk home's line is
    ## renpy.say from python).
    zzh_real_say = renpy.exports.say

    def zzh_say(who, what, *args, **kwargs):
        zzh.said.append(what)
        return zzh_real_say(who, what, *args, **kwargs)

    renpy.exports.say = zzh_say

    zzh_prev_filter = config.say_menu_text_filter

    def zzh_text(s):
        zzh.texts.append(s)
        return zzh_prev_filter(s) if zzh_prev_filter else s

    config.say_menu_text_filter = zzh_text

    ## No story beat is picked while the driver runs.
    zzh_real_pick = pick_event

    def zzh_no_story(kind, *args, **kwargs):
        if zzh.on and kind == "story":
            return None
        return zzh_real_pick(kind, *args, **kwargs)

    def zzh_patch():
        """Set at init, so the wrapper is the game's pick_event for the whole
        run and never a saved variable."""
        store.pick_event = zzh_no_story

    zzh_patch()

    ## --- fixtures ----------------------------------------------------------------

    def zzh_snapshot():
        """Every `default` variable of the game, deep-copied."""
        out = builtins.dict()
        for d in renpy.ast.default_statements:
            if getattr(d, "store", "store") != "store":
                continue
            k = getattr(d, "varname", None)
            if not k or not hasattr(store, k):
                continue
            try:
                out[k] = copy.deepcopy(getattr(store, k))
            except Exception:
                pass
        return out

    def zzh_fix(bond=60, **kw):
        """A settled mid-game state from the boot state: everyone met, the
        given Bond with everyone, Grade 3, nobody walking with me, no pin."""
        for k, v in zzh.boot.items():
            setattr(store, k, copy.deepcopy(v))
        renpy.random.seed(20261007)
        base = dict(mc_name="Tester", mc_surname="Harness", day=12, period="Noon", here="dorm", yen=5000)
        base.update(kw)
        settle(**base)
        for w in ROSTER_ORDER:
            if w not in store.roster:
                store.roster.append(w)
            store.bonds[w] = bond
        for f in ZZH_FLAGS:
            flag(f)
        store.done_events.add("st_roll_call")
        promote("mc", "g3", quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()

    def zzh_day(name):
        """The first day from 8 on that is this weekday ("Fri", "Sat")."""
        for d in range(8, 15):
            if WEEKDAYS[(d - 1) % 7] == name:
                return d

    def zzh_at(day, per):
        store.day = day
        store.period = per
        roll_gojo()
        mission_cache_clear()

    def zzh_with_status(mid, fn):
        """fn() with the mission `mid` reading "available" (a test mission:
        the game's own row, opened for the length of the call)."""
        real = store.mission_status

        def zzh_status(id):
            return "available" if id == mid else real(id)

        store.mission_status = zzh_status
        try:
            return fn()
        finally:
            store.mission_status = real

    def zzh_findings(fn, change, undo):
        """What a validator says after `change`, which `undo` takes back."""
        change()
        try:
            return builtins.list(fn())
        finally:
            undo()

    def zzh_exits(loc):
        return [r["to"] for r in path_exits(loc)]

    def zzh_exit_table():
        """A copy of PATH_EXITS, each row list its own."""
        return builtins.dict((k, builtins.list(v)) for k, v in PATH_EXITS.items())

    def zzh_restore_exits():
        """PATH_EXITS as it was when the tests on it began (zzh.keep)."""
        PATH_EXITS.clear()
        PATH_EXITS.update((k, builtins.list(v)) for k, v in zzh.keep["exits"].items())

    def zzh_mission_view(room, who):
        """What the place view and the map say about the missions in a room."""
        mission_cache_clear()
        return builtins.dict(
            here=builtins.list(missions_here(room)),
            rail=[m[0] for m in rail_missions(room)],
            rows=[r[0] for r in rail_rows(room) if r[0][0] == "mission"],
            raw=builtins.list(builtins.dict(mission_markers()).get(room) or ()),
            marks=builtins.list(map_marks().get(room) or ()),
            news=map_has_news(who, room),
            badge=map_pin_news(room, map_marks()),
            waiting=map_waiting(area_of(room)),
            tag=view_tag_marks(who, room)[0])

    def zzh_panda_view():
        return zzh_mission_view("senpai_room", "panda")

    def zzh_heard():
        """How many lines have been said so far, by statements and by python."""
        return len(zzh.said) + len(zzh.texts)

    def zzh_carry_said(n):
        lines = builtins.set(NIGHT_CARRY_LINES.values())
        return [t for t in zzh.said[n:] if t in lines]

    def zzh_names(fn, first, last):
        """The statement names of file `fn` on lines first..last, sorted, as
        [json name, kind]. Ren'Py gives a node of an edited file its old name
        when the old .rpyc is beside it (renpy/script.py, merge_names), and
        tools/smoke.sh copies the owner's .rpyc into the scratch copy."""
        out, seen = [], builtins.set()
        for node in renpy.game.script.namemap.values():
            key = getattr(node, "name", None)
            if (getattr(node, "filename", None) != fn or id(node) in seen
                    or not isinstance(key, (builtins.str, builtins.tuple))
                    or not (first <= node.linenumber <= last)):
                continue
            seen.add(id(node))
            out.append([json.dumps(key), type(node).__name__])
        return builtins.sorted(out)

    def zzh_names_hash(rows):
        return hashlib.sha256(json.dumps(rows).encode("utf-8")).hexdigest()[:24]

    def zzh_old_exits():
        """The exits as they were before the overhaul: {place: [[to, x, y]]}
        from tools/smoke/baseline_u2.json (U0a's baseline)."""
        root = os.environ.get("SMOKE_ROOT") or ""
        with open(os.path.join(root, "tools", "smoke", "baseline_u2.json"), encoding="utf-8") as f:
            return json.load(f)["exits"]

    def zzh_offer_exits(loc):
        """(in the picture, in the column): the exits the place view offers."""
        room = builtins.sorted(h["act"] for h in hot_spots_for(loc) if str(h["act"]).startswith("path_"))
        col = builtins.sorted(a[0] for a in rail_actions(loc) if a[0].startswith("path_"))
        return room, col

    def zzh_copy_saves():
        """The saves made before the overhaul, into the scratch save folder
        (never the owner's: config.savedir is the run's own)."""
        root = os.environ.get("SMOKE_ROOT") or ""
        src = os.path.join(root, "tools", "smoke", "assets", "ui2_saves")
        ok = []
        for name in ZZH_SAVES:
            f = os.path.join(src, name + "-LT1.save")
            dst = os.path.join(config.savedir, name + "-LT1.save")
            if os.path.isfile(f) and "jjk_smoke." in config.savedir:
                if not os.path.exists(dst):
                    shutil.copy(f, dst)
                ok.append(name)
        try:
            renpy.loadsave.location.scan()
            renpy.loadsave.clear_cache()
        except Exception:
            pass
        return ok

    ## --- the driver ---------------------------------------------------------------

    def zzh_ui():
        """What is waiting: a loop screen, "choice", "say", or None."""
        for s in ZZH_SCREENS:
            if renpy.get_screen(s) is not None:
                return s
        if renpy.get_screen("choice") is not None:
            return "choice"
        sc = renpy.get_screen("say")
        if sc is not None and sc.scope.get("what"):
            return "say"
        return None

    def zzh_sig():
        ctx = renpy.game.context()
        return (ctx.current, renpy.call_stack_depth(), store.day, store.period, store.here)

    def zzh_where():
        fn, ln = renpy.get_filename_line()
        return "%s:%d" % (fn, ln)

    def zzh_scrub():
        """Nothing of the harness goes into a save."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz")]:
            try:
                delattr(store, k)
            except Exception:
                pass

    def zzh_park(name):
        """True once the save `name` has been made, loaded and compared. The
        first call makes the save and loads it (and does not return); the
        tick after the load compares. (Its lines read "H:", whichever
        section parks: M's saves are named new_<place>.)"""
        if name in zzh.parked:
            return True
        want = zzh_sig()
        ui = zzh_ui()
        zzh_scrub()
        try:
            renpy.take_screenshot()
            renpy.save("zzh_" + name)
            ok = bool(renpy.can_load("zzh_" + name))
            why = "" if ok else "no file"
        except Exception:
            import traceback
            ok = False
            why = traceback.format_exc()[-1200:]
        check(ok, "H: %s: the save is written, from inside the interaction" % name, why)
        note("parked " + name, "%s · %s · depth %d · day %s %s %s · %s" % (
            want[0], zzh_where(), want[1], want[2], want[3], want[4], ui))
        if not ok:
            zzh.parked[name] = False
            return True
        shot("park_" + name, wait=0)
        zzh.pending = builtins.dict(name=name, sig=want, ui=ui, loads=zzh.loads + 1, stage=zzh.stage,
                                    recover=len(zzh.recover), own=True)
        renpy.load("zzh_" + name)

    def zzh_load(slot):
        """Load one of the saves made before the overhaul."""
        if not renpy.can_load(slot):
            check(False, "L: the save %s is in the scratch save folder" % slot, config.savedir)
            zzh_stop()
            return
        zzh.pending = builtins.dict(name=slot, sig=None, ui=None, loads=zzh.loads + 1, stage=zzh.stage,
                                    recover=len(zzh.recover), own=False)
        renpy.load(slot)

    def zzh_verify():
        p = zzh.pending
        zzh.pending = None
        name = p["name"]
        if p["own"]:
            got = zzh_sig()
            check(got == p["sig"] and zzh_ui() == p["ui"],
                  "H: %s: the load comes back on its own statement, at the same depth, day, hour and place, the place view up" % name,
                  "%r %r, saved %r %r" % (got, zzh_ui(), p["sig"], p["ui"]))
        check(len(zzh.recover) == p["recover"], "%s: neither load_recover nor return_recover ran" % name, repr(zzh.recover))
        check(zzh.stage == p["stage"] and zzh.loads == p["loads"],
              "%s: the driver's own counter survives the load" % name, (zzh.stage, p["stage"], zzh.loads, p["loads"]))
        zzh.parked[name] = True

    def zzh_next(n=1):
        zzh.stage += n
        zzh.t_stage = time.time()
        zzh.trace.append("stage %d at %s %s %s" % (zzh.stage, store.day, store.period, store.here))

    def zzh_button(screen, wid):
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

    def zzh_press(screen, wid):
        """Press a button by id, as a click does. "zz_missing" when it isn't
        there."""
        w = zzh_button(screen, wid)
        if w is None or getattr(w, "action", None) is None:
            return "zz_missing"
        renpy.display.screen.push_current_screen(renpy.get_screen(screen))
        try:
            return renpy.run(w.action)
        finally:
            renpy.display.screen.pop_current_screen()

    def zzh_offered(screen="sb_place"):
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

    def zzh_walk(to):
        """Take the exit to `to`: its button in the picture when it is there,
        else its tile in the icon column (someone stands in front of it)."""
        wid = "hot_" + path_spot_id(store.here, to)
        v = zzh_press("sb_place", wid)
        if v != "zz_missing":
            return v
        ret = ("act", "path_" + to)
        if ret not in zzh_offered():
            check(False, "stage %d: %s offers the exit to %s, in the picture or in the column" % (zzh.stage, store.here, to),
                  "%r: %r" % (wid, zzh_offered()))
            zzh_stop()
            return None
        return ret

    def zzh_prep(bond):
        """Inside the loop: everyone met, this Bond with everyone, nobody
        walking with me, no pin, no door flag."""
        for w in ROSTER_ORDER:
            if w not in store.roster:
                store.roster.append(w)
            store.bonds[w] = bond
        for f in ZZH_FLAGS:
            flag(f)
        for f in [f for f in store.flags if f.startswith("door_") or f == "invited_girls_dorm"]:
            store.flags.discard(f)
        store.companion = None
        store.schedule_overrides = {}
        toast_clear()

    def zzh_set(loc, per, day=None):
        """Put me somewhere at an hour and let the loop come round again:
        "Let them go" with nobody along does nothing."""
        store.here = loc
        store.period = per
        if day is not None:
            store.day = day
            roll_gojo()
        mission_cache_clear()
        return ("act", "release")

    def zzh_clock():
        return (store.day, store.period, store.stamina, store.ce, store.yen)

    def zzh_marks():
        """What a scene, a beat or an activity would leave behind."""
        return (zzh_clock(), builtins.sorted(store.done_events), builtins.sorted(store.flags),
                builtins.sorted(store.talked_today), builtins.sorted(store.spent_today),
                builtins.sorted(store.actions_today), builtins.dict(store.bonds), store.companion)

    def zzh_stop():
        zzh.on = False
        check(not zzh.recover, "no recover label ran in the whole run", repr(zzh.recover))
        note("run", "%d loads in %.0f s; ended at stage %d, day %s %s %s" % (
            zzh.loads, time.time() - zzh.t0, zzh.stage, store.day, store.period, store.here))
        finish()

    def zzh_step(ui):
        s = zzh.stage
        here = store.here
        k = zzh.keep

        if ui == "say":
            return True         ## a line is clicked on

        ## --- H. on foot, a save at each step ---------------------------------------
        if s == 0:
            if ui == "sb_place":
                zzh_next()
                return zzh_set("dorm_yard", "Noon")
        elif s == 1:
            if ui == "sb_place" and here == "dorm_yard":
                if "garden" not in zzh.parked:
                    k["clock"] = zzh_clock()
                    room, col = zzh_offer_exits(here)
                    check(builtins.sorted(room + col) == builtins.sorted("path_" + t for t in zzh_exits(here)) and len(room + col) == 7,
                          "H: in the garden every one of its seven exits is offered once, in the picture or in the column", (room, col))
                if zzh_park("garden"):
                    del zzh.labels[:]
                    zzh_next()
                    return zzh_walk("boys_dorm")
        elif s == 2:
            if ui == "sb_place":
                if "corridor" not in zzh.parked:
                    k["walk_labels"] = builtins.list(zzh.labels)
                    check(here == "boys_dorm" and zzh_clock() == k["clock"],
                          "H: the garden's first exit walks into the Boys' Dormitory, no time spent", (here, zzh_clock(), k["clock"]))
                    shot("place_boys_dorm", wait=0)
                if zzh_park("corridor"):
                    zzh_next()
                    return zzh_walk("dorm")
        elif s == 3:
            if ui == "sb_place":
                if "room" not in zzh.parked:
                    check(here == "dorm" and zzh_clock() == k["clock"],
                          "H: the door at the end of the corridor walks into my room, no time spent", (here, zzh_clock()))
                    check(("act", "sleep") in zzh_offered() and renpy.get_widget("sb_place", "hot_go_dorm__boys_dorm") is not None
                          and renpy.get_widget("sb_place", "hot_go_dorm__dorm_yard") is None,
                          "H: my room offers Sleep and one exit, to the Boys' Dormitory", zzh_offered())
                if zzh_park("room"):
                    zzh_next()
                    zzh.tries = 1
                    renpy.rollback(force=True, checkpoints=1)
        elif s == 4:
            if ui == "sb_place":
                if here == "dorm" and zzh.tries < 3:
                    zzh.tries += 1
                    renpy.rollback(force=True, checkpoints=1)
                check(here == "boys_dorm" and zzh_clock() == k["clock"],
                      "H: a rollback from my room lands in the corridor", (here, zzh_where(), zzh.tries))
                note("rollback", "from my room to the corridor in %d checkpoint(s)" % zzh.tries)
                zzh_next()
                zzh.tries = 1
                renpy.rollback(force=True, checkpoints=1)
        elif s == 5:
            if ui == "sb_place":
                if here == "boys_dorm" and zzh.tries < 3:
                    zzh.tries += 1
                    renpy.rollback(force=True, checkpoints=1)
                check(here == "dorm_yard" and zzh_clock() == k["clock"],
                      "H: and one more lands in the garden: the whole walk rolls back, step by step", (here, zzh_where(), zzh.tries))
                zzh_next()
                return zzh_walk("boys_dorm")
        elif s == 6:
            if ui == "sb_place":
                check(here == "boys_dorm", "H: forward again after the rollback: the corridor", here)
                zzh_next()
                return zzh_walk("dorm")
        elif s == 7:
            if ui == "sb_place":
                check(here == "dorm", "H: forward again: my room", here)
                zzh_next()
                return zzh_walk("boys_dorm")
        elif s == 8:
            if ui == "sb_place":
                check(here == "boys_dorm", "H: back out of my room: the corridor", here)
                zzh_next()
                return zzh_walk("dorm_yard")
        elif s == 9:
            if ui == "sb_place":
                check(here == "dorm_yard" and zzh_clock() == k["clock"] and renpy.call_stack_depth() == 0,
                      "H: and the stairs lead back to the garden: there and back cost no time", (here, zzh_clock(), k["clock"]))
                zzh_next()
                return ("map",)
        ## --- I. by map --------------------------------------------------------------
        elif s == 10:
            if ui == "sb_map":
                zone = renpy.get_screen("sb_map").scope.get("zone")
                if zone != "dorms":
                    zzh_press("sb_map", "area_dorms")
                    return None
                rows = [l for l in LOC_ORDER if renpy.get_widget("sb_map", "row_" + l) is not None]
                check(builtins.sorted(rows) == builtins.sorted(["dorm_yard", "dorm", "dorm_common", "girls_dorm", "rooftop", "boys_dorm"]),
                      "I: the Dormitories view has six pins: the garden, my room, the Common Room, the girls' corridor, the rooftop "
                      "and the Boys' Dormitory; none for a friend's room", rows)
                shot("map_dorms", wait=0)
                zzh_next()
                v = zzh_press("sb_map", "row_dorm")
                check(v == ("go", "dorm"), "I: pressing my room's pin returns ('go', 'dorm')", repr(v))
                return v if v != "zz_missing" else ("cancel",)
        elif s == 11:
            if ui == "sb_place":
                check(here == "dorm" and zzh_clock() == k["clock"],
                      "I: by map, Dormitories then my room's pin: two clicks to my room, no time spent", (here, zzh_clock()))
                k["room"] = 0
                zzh_next()
                return zzh_set("boys_dorm", "Night", zzh_day("Fri"))
        ## --- J. into each friend's room at Night ------------------------------------
        elif s == 12:
            if ui == "sb_place" and here == "boys_dorm":
                room = ZZH_ROOMS[k["room"]]
                check(weekday() == "Fri" and store.period == "Night" and place_access(room)[0],
                      "J: a weekday Night in the corridor, %s's door open (Bond 60)" % room, (weekday(), store.period, place_access(room)))
                k["marks"] = zzh_marks()
                k["said"] = zzh_heard()
                del zzh.labels[:]
                zzh_next()
                return zzh_walk(room)
        elif s == 13:
            if ui == "sb_place":
                room = ZZH_ROOMS[k["room"]]
                want = [l.replace("boys_dorm", room) for l in k["walk_labels"]]
                check(here == room and zzh.labels == want and "sb_do_path_" + room in want and "path_walk" in want,
                      "J: walking into %s at Night calls the walk and nothing else (%s)" % (room, ", ".join(want)), (here, zzh.labels))
                check(zzh_marks() == k["marks"] and zzh_heard() == k["said"],
                      "J: and it leaves nothing behind: no line said, no time, no flag, no scene, nobody talked to (K16)",
                      (zzh.said[-2:], zzh.texts[-2:], zzh_marks() == k["marks"]))
                on = builtins.list(stage_people(here)[0])
                folk = builtins.list(who_is_here(here))
                chars = builtins.sorted(builtins.set(v[1] for v in zzh_offered() if v[0] == "char"))
                jobs = [v for v in zzh_offered() if v[0] == "mission"]
                if room == "yuji_room":
                    check(folk == ["yuji"] and on == ["yuji"] and chars == ["yuji"],
                          "J: Yuji is in his room and up: on the stage, to be talked to", (folk, on, chars))
                elif room == "megumi_room":
                    check(folk == ["megumi"] and on == [] and chars == [] and jobs == [],
                          "J: Megumi is in his room, asleep: counted there, not on the stage, nothing to click with him, no mission tile",
                          (folk, on, chars, jobs))
                else:
                    check(folk == ["panda", "toge"] and on == ["toge"] and chars == ["toge"] and jobs == [],
                          "J: in the shared room Toge is up and on the stage; Panda is asleep, counted there and nowhere to be clicked",
                          (folk, on, chars, jobs))
                shot("place_" + room, wait=0)
                zzh_next()
                return zzh_walk("boys_dorm")
        elif s == 14:
            if ui == "sb_place":
                room = ZZH_ROOMS[k["room"]]
                check(here == "boys_dorm" and zzh_marks() == k["marks"],
                      "J: and I walk out of %s again, into the corridor" % room, here)
                k["room"] += 1
                if k["room"] < len(ZZH_ROOMS):
                    zzh.stage = 12
                    zzh.t_stage = time.time()
                    return ("act", "release")
                zzh_next()
                store.bonds["megumi"] = 14
                return ("act", "release")
        ## --- K. a shut door ---------------------------------------------------------
        elif s == 15:
            if ui == "sb_place" and here == "boys_dorm":
                row = [r for r in path_exits(here) if r["to"] == "megumi_room"][0]
                hot = [h for h in hot_spots_for(here) if h["id"] == path_spot_id(here, "megumi_room")]
                rail = [a for a in rail_actions(here) if a[0] == "path_megumi_room"]
                check(row["locked_reason"] == "I don't know Megumi well enough to let myself in." and row["label"] == row["locked_reason"]
                      and ((hot and hot[0]["icon"] == "lock") or (rail and rail[0][1] == row["locked_reason"])),
                      "K: at Bond 14 Megumi's door is drawn as the lock, and its label is its line", (row, hot, rail))
                k["marks"] = zzh_marks()
                k["said"] = zzh_heard()
                v = zzh_press("sb_place", "hot_" + path_spot_id(here, "megumi_room"))
                check(v is None and ("act", "path_megumi_room") not in zzh_offered(),
                      "K: pressing it returns nothing: the place view does not offer the walk", repr(v))
                zzh_next()
                return ("act", "path_megumi_room")
        elif s == 16:
            if ui == "sb_place":
                check(here == "boys_dorm" and zzh_marks() == k["marks"] and zzh_heard() == k["said"],
                      "K: and if the walk is asked for all the same, label path_walk refuses it: still in the corridor, "
                      "nothing said, no time spent", (here, zzh.said[-2:], zzh.texts[-2:]))
                zzh_next()
                zzh_load("u2-garden-night")
        ## --- L. three saves made before the overhaul ---------------------------------
        elif s == 17:
            if ui == "sb_place":
                here_folk = builtins.list(who_is_here(here))
                check(here == "dorm_yard" and store.period == "Night" and not is_weekend(),
                      "L: u2-garden-night loads in the garden on a weekday Night, on the place view", (here, store.period, weekday()))
                check(here_folk == [] and builtins.list(stage_people(here)[0]) == []
                      and not [v for v in zzh_offered() if v[0] == "char"],
                      "L: the garden shows nobody now (the save had Yuji and Panda on its stage)", (here_folk, zzh_offered()))
                check(char_location("yuji") == "yuji_room" and not world_asleep("yuji") and world_home_state("yuji") == "awake"
                      and char_location("panda") == "senpai_room" and world_asleep("panda") and world_home_state("panda") == "asleep"
                      and "panda" in who_is_here("senpai_room") and "panda" not in stage_people("senpai_room")[0]
                      and ambient_of("panda", "senpai_room") == ("asleep", None),
                      "L: Yuji is in his room, awake; Panda is in the shared room, asleep: counted there, off its stage",
                      (char_location("yuji"), char_location("panda"), world_asleep("yuji"), world_asleep("panda")))
                room, col = zzh_offer_exits(here)
                check(builtins.sorted(room + col) == builtins.sorted("path_" + t for t in zzh_exits(here))
                      and "path_boys_dorm" in room + col and "path_dorm" not in room + col
                      and renpy.get_widget("sb_place", "hot_go_dorm_yard__dorm") is None,
                      "L: its exits are rebuilt from the table: the left house is the Boys' Dormitory", (room, col))
                zzh_next()
                zzh_load("u2-garden-panda")
        elif s == 18:
            if ui == "sb_char":
                who = renpy.get_screen("sb_char").scope.get("who")
                check(who == "panda" and here == "dorm_yard" and "sb_loop.rpy" in zzh_where(),
                      "L: u2-garden-panda loads on the person view of Panda, in the garden, with no exception", (who, here, zzh_where()))
                zzh_next()
                return ("cancel",)
        elif s == 19:
            if ui == "sb_place":
                check(here == "dorm_yard" and renpy.call_stack_depth() == 0 and builtins.list(stage_people(here)[0]) == []
                      and world_asleep("panda"),
                      "L: the person view closes onto the garden's place view, which shows nobody; Panda is asleep in his room",
                      (here, renpy.call_stack_depth(), stage_people(here)))
                zzh_next()
                zzh_load("u2-garden")
        elif s == 20:
            if ui == "sb_place":
                check(here == "dorm_yard" and "boys_dorm" in zzh_exits(here),
                      "L: u2-garden loads in the garden, one step after walking out of my room by the old exit", (here, zzh_where()))
                zzh_next()
                zzh.tries = 1
                renpy.rollback(force=True, checkpoints=1)
        elif s == 21:
            if ui == "sb_place":
                if here == "dorm_yard" and zzh.tries < 3:
                    zzh.tries += 1
                    renpy.rollback(force=True, checkpoints=1)
                check(here == "dorm" and renpy.get_widget("sb_place", "hot_go_dorm__boys_dorm") is not None,
                      "L: rolling back from it lands in my room, whose door now leads to the corridor", (here, zzh_where(), zzh.tries))
                zzh_next()
                return zzh_walk("boys_dorm")
        elif s == 22:
            if ui == "sb_place":
                check(here == "boys_dorm", "L: and from there the old save walks on, into the corridor", here)
                zzh_prep(60)
                k["new"] = 0
                zzh_next()
                return zzh_set(ZZH_SEVEN[0], "Noon", zzh_day("Fri"))
        ## --- M. a save made in each of the seven new places reloads there ---------------
        elif s == 23:
            place = ZZH_SEVEN[k["new"]]
            if ui == "sb_place" and here == place:
                if ("new_" + place) not in zzh.parked:
                    shot("place_" + place, wait=0)
                if zzh_park("new_" + place):
                    check(zzh.parked.get("new_" + place) is True and store.here == place and renpy.get_screen("sb_place") is not None
                          and zzh_exits(place)[0] in [v[1][5:] for v in zzh_offered() if v[0] == "act" and v[1].startswith("path_")],
                          "M: a save made in %s reloads there, on the place view, its way out offered" % LOCATIONS[place]["name"],
                          (store.here, zzh.parked.get("new_" + place), zzh_offered()))
                    k["new"] += 1
                    if k["new"] < len(ZZH_SEVEN):
                        zzh.t_stage = time.time()
                        return zzh_set(ZZH_SEVEN[k["new"]], "Noon")
                    zzh_prep(0)
                    zzh_next()
                    return zzh_set("dorm_yard", "Afternoon", zzh_day("Fri"))
        ## --- N. into Nobara's room as her companion, and out after dark -----------------
        elif s == 24:
            if ui == "sb_place" and here == "dorm_yard":
                ## (set here, not before the loop came round: zzh_set comes
                ## round by "Let them go", which would let her go)
                store.companion = "nobara"
                check(store.period == "Afternoon" and store.companion == "nobara" and store.bonds["nobara"] == 0 and store.bonds["maki"] == 0
                      and not has_flag("invited_girls_dorm") and place_access("girls_dorm")[0] and place_access("nobara_room")[0]
                      and place_access("maki_room") == (False, ZZH_KNOCK, "Bond 15"),
                      "N: a weekday Afternoon in the garden, Nobara walking with me, Bond 0 with everyone: the corridor is open by day "
                      "and her door opens for her; Maki's does not", (store.period, store.companion, place_access("nobara_room"), place_access("maki_room")))
                zzh_next()
                return zzh_walk("girls_dorm")
        elif s == 25:
            if ui == "sb_place":
                check(here == "girls_dorm", "N: into the girls' corridor", here)
                shot("place_girls_dorm", wait=0)
                k["marks"] = zzh_marks()
                k["said"] = zzh_heard()
                del zzh.labels[:]
                zzh_next()
                return zzh_walk("nobara_room")
        elif s == 26:
            if ui == "sb_place":
                want = [l.replace("boys_dorm", "nobara_room") for l in k["walk_labels"]]
                check(here == "nobara_room" and zzh.labels == want and zzh_marks() == k["marks"] and zzh_heard() == k["said"],
                      "N: and into Nobara's room: the walk and nothing else, nothing said, no time spent (K16)", (here, zzh.labels))
                zzh_next()
                return ("act", "wait")
        elif s == 27:
            if ui == "sb_place" and store.period == "Evening":
                row = path_exits(here)[0]
                store.here = "dorm_yard"
                outside = (place_access("girls_dorm"), place_access("nobara_room"))
                store.here = "nobara_room"
                check(here == "nobara_room" and store.companion == "nobara" and not has_flag("invited_girls_dorm")
                      and outside == ((False, ZZH_CORRIDOR, "After dark"), (False, ZZH_CORRIDOR, "After dark"))
                      and place_access("girls_dorm") == (True, "", "") and row["to"] == "girls_dorm" and row["locked_reason"] == ""
                      and row["label"] == "To the Girls' Dormitory",
                      "N: Wait, and it is Evening in her room: from the garden the corridor would refuse me (and her room with it: the "
                      "house first), but from inside it the way out is open", (store.period, outside, place_access("girls_dorm"), row))
                zzh_next()
                return zzh_walk("girls_dorm")
        elif s == 28:
            if ui == "sb_place":
                check(here == "girls_dorm" and store.period == "Evening",
                      "N: the exit works: I walk out of her room into the corridor, after dark, with no Bond and no flag", (here, store.period))
                check(place_access("nobara_room")[0] and place_access("maki_room") == (False, ZZH_KNOCK, "Bond 15")
                      and place_access("dorm_yard")[0],
                      "N: standing in the corridor, her door is still open to her companion and Maki's says its own line "
                      "(not the corridor's)", (place_access("nobara_room"), place_access("maki_room")))
                zzh_next()
                return zzh_walk("dorm_yard")
        elif s == 29:
            if ui == "sb_place":
                row = [r for r in path_exits(here) if r["to"] == "girls_dorm"]
                check(here == "dorm_yard" and row and row[0]["locked_reason"] == ZZH_CORRIDOR and row[0]["label"] == ZZH_CORRIDOR
                      and ("act", "path_girls_dorm") not in zzh_offered(),
                      "N: and out to the garden; behind me the corridor is locked again, with its own sentence", (here, row))
                zzh_prep(60)
                zzh_next()
                return zzh_set("teachers_lounge", "Night", zzh_day("Fri"))
        ## --- O. the teachers' house at Night ---------------------------------------------
        elif s == 30:
            if ui == "sb_place" and here == "teachers_lounge":
                check(store.period == "Night" and who_is_here(here) == [] and zzh_exits(here) == ["staff_yard", "teachers_dorm"],
                      "O: a weekday Night in the Teachers' Lounge: open, and empty", (store.period, who_is_here(here)))
                k["marks"] = zzh_marks()
                zzh_next()
                return zzh_walk("teachers_dorm")
        elif s == 31:
            if ui == "sb_place":
                on = builtins.list(stage_people(here)[0])
                folk = builtins.list(who_is_here(here))
                chars = builtins.sorted(builtins.set(v[1] for v in zzh_offered() if v[0] == "char"))
                jobs = [v for v in zzh_offered() if v[0] == "mission"]
                check(here == "teachers_dorm" and zzh_marks() == k["marks"] and folk == ["yaga", "utahime", "ijichi"]
                      and on == ["yaga"] and chars == ["yaga"] and jobs == [],
                      "O: upstairs, Yaga is up at his workbench; Utahime and Ijichi are in the Teachers' Dormitory, asleep: "
                      "counted there, not on its stage, nothing to click with them, no mission tile", (here, folk, on, chars, jobs))
                shot("place_teachers_dorm_night", wait=0)
                zzh_next()
                return zzh_walk("teachers_lounge")
        elif s == 32:
            if ui == "sb_place":
                check(here == "teachers_lounge", "O: and down the stairs again", here)
                zzh_next()
                zzh_stop()
        return None

    def zzh_tick():
        if not zzh.on:
            return None
        if len(renpy.game.contexts) != 1 or not renpy.game.context().interacting:
            return None
        now = time.time()
        if now - zzh.t0 > 300 or now - zzh.t_stage > 45:
            check(False, "the driver reaches its end", "stage %d for %.0f s; %s; waiting: %r; pending %r; %r" % (
                zzh.stage, now - zzh.t_stage, zzh_where(), zzh_ui(), (zzh.pending or {}).get("name"), zzh.trace[-4:]))
            zzh_stop()
            return None
        ui = zzh_ui()
        if ui is None:
            return None
        if zzh.pending is not None:
            if zzh.loads < zzh.pending["loads"]:
                return None
            zzh_verify()
        try:
            return zzh_step(ui)
        except renpy.game.CONTROL_EXCEPTIONS:
            raise
        except Exception:
            import traceback
            check(False, "driver raised at stage %d" % zzh.stage, traceback.format_exc())
            zzh_stop()
        return None

    config.overlay_screens.append("zzh_driver")


screen zzh_driver():
    zorder 400
    if zzh.on:
        timer 0.15 repeat True action Function(zzh_tick)


label zz_smoke:

    ## A load rolls back to here at the earliest: the checks below run once.
    if zzh.on or zzh.loads:
        jump sandbox

    python:
        zzh.boot = zzh_snapshot()
        zzh_fix()

        ########################################################################
        ## A. Home
        ########################################################################
        check("dorm" in LOCATIONS and LOCATIONS["dorm"]["bg"] == "bg your_room" and LOCATIONS["dorm"]["name"] == "My Room"
              and renpy.has_label("sb_do_path_dorm") and zzh.boot["here"] == "dorm" and area_of("dorm") == "dorms",
              "A: home is the key dorm: its picture bg your_room, its label sb_do_path_dorm, default here, the Dormitories (K1)",
              (LOCATIONS["dorm"]["bg"], zzh.boot.get("here"), area_of("dorm")))
        check(world_inside("dorm") == "boys_dorm" and all(world_inside(r) == "boys_dorm" for r in ZZH_ROOMS)
              and world_inside("boys_dorm") is None and world_inside("dorm_yard") is None and world_inside("zz") is None,
              "A: WORLD_INSIDE: my room and the three friends' rooms open off the Boys' Dormitory, one level deep", builtins.dict(WORLD_INSIDE))
        check(world_pinned("dorm") and world_pinned("boys_dorm") and not any(world_pinned(r) for r in ZZH_ROOMS)
              and all(r in WORLD_PINLESS for r in ZZH_ROOMS) and not world_pinned("zz"),
              "A: my room keeps its pin, the corridor has one, the three friends' rooms have none (D3)", WORLD_PINLESS)
        _zz_new = ("boys_dorm",) + ZZH_ROOMS
        check(all(k in LOCATIONS and LOCATIONS[k]["indoor"] and LOCATIONS[k]["bg"] == "bg " + k
                  and renpy.has_image(("bg", k), exact=True) and area_of(k) == "dorms" for k in _zz_new)
              and [l for l in LOC_ORDER if l in _zz_new] == builtins.list(_zz_new)
              and all(LOC_ORDER.index(k) > LOC_ORDER.index("trailhead") for k in _zz_new)
              and len(LOC_ORDER) == len(LOCATIONS) == len(builtins.set(LOC_ORDER)),
              "A: the four new places are rows appended after the old 24, indoors, each with its picture bg <key>, in the Dormitories",
              LOC_ORDER[24:])
        ## U0c1: the other seven.
        check(LOC_ORDER[24:] == builtins.list(_zz_new + ZZH_SEVEN) and len(LOCATIONS) == 35
              and all(k in LOCATIONS and LOCATIONS[k]["bg"] == "bg " + k and renpy.has_image(("bg", k), exact=True) for k in ZZH_SEVEN)
              and [k for k in ZZH_SEVEN if not LOCATIONS[k]["indoor"]] == ["pool"]
              and [area_of(k) for k in ZZH_SEVEN] == ["dorms", "dorms", "staff", "staff", "mountain", "mountain", "grounds"]
              and all(places_in(area_of(k))[-1] in ZZH_SEVEN for k in ZZH_SEVEN),
              "A: 35 places: U0c1's seven are appended after U0b's four, each with its picture bg <key>; all indoors but the pool; "
              "the girls' rooms in the Dormitories, the teachers' house in the Staff Building, the Onsen and its sauna on the "
              "Mountain, the pool in the Training Grounds", LOC_ORDER[24:])
        check([LOCATIONS[k]["name"] for k in ZZH_SEVEN] == ["Nobara's Room", "Maki's Room", "Teachers' Lounge", "Teachers' Dormitory",
                                                            "Onsen", "Sauna", "Swimming Pool"],
              "A: their names; the place with the key bathhouse is shown as Onsen (O16)", [LOCATIONS[k]["name"] for k in ZZH_SEVEN])
        check(builtins.dict(WORLD_INSIDE) == builtins.dict(dorm="boys_dorm", yuji_room="boys_dorm", megumi_room="boys_dorm",
                                                            senpai_room="boys_dorm", nobara_room="girls_dorm", maki_room="girls_dorm",
                                                            teachers_dorm="teachers_lounge", sauna="bathhouse")
              and builtins.tuple(WORLD_PINLESS) == ("yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room", "teachers_dorm", "sauna")
              and all(world_pinned(k) for k in ("teachers_lounge", "bathhouse", "pool", "girls_dorm")),
              "A: WORLD_INSIDE is whole (3.2): the girls' rooms off their corridor, the Teachers' Dormitory off the lounge, the Sauna "
              "off the Onsen; those four have no pin, and the lounge, the Onsen and the pool have one",
              (builtins.dict(WORLD_INSIDE), WORLD_PINLESS))
        note("stand-ins in use", [k for k in ("boys_dorm",) + ZZH_ROOMS + ZZH_SEVEN if not renpy.loadable("images/bg/%s.png" % k)])

        ########################################################################
        ## B. Exits and the validators
        ########################################################################
        check(zzh_exits("dorm_yard") == ["boys_dorm", "dorm_common", "girls_dorm", "rooftop", "courtyard", "staff_yard", "trailhead"],
              "B: the garden has exactly seven exits, the Boys' Dormitory in my room's old place", zzh_exits("dorm_yard"))
        _zz_old = zzh_old_exits()
        _zz_pt = builtins.dict(yard=builtins.tuple(_zz_old["dorm_yard"][0][1:]), room=builtins.tuple(_zz_old["dorm"][0][1:]))
        check(_zz_old["dorm_yard"][0][0] == "dorm" and [r[0] for r in _zz_old["dorm"]] == ["dorm_yard"]
              and [(r["to"], r["x"], r["y"]) for r in path_exits("dorm_yard")][0] == ("boys_dorm",) + _zz_pt["yard"]
              and [(r["to"], r["x"], r["y"]) for r in path_exits("dorm")] == [("boys_dorm",) + _zz_pt["room"]]
              and [[r["to"], r["x"], r["y"]] for r in path_exits("dorm_yard")][1:] == _zz_old["dorm_yard"][1:],
              "B: both exits keep the points they had before the overhaul (U0a's baseline): the left house's steps in the garden, "
              "my door in my room; the garden's other six are as they were", (path_exits("dorm_yard")[0], path_exits("dorm")))
        check(zzh_exits("boys_dorm") == ["dorm_yard", "dorm", "yuji_room", "megumi_room", "senpai_room"]
              and all(zzh_exits(r) == ["boys_dorm"] for r in ZZH_ROOMS),
              "B: the corridor leads to the garden, my room and the three rooms; each room leads back to it", zzh_exits("boys_dorm"))
        _zz_houses = builtins.sorted(builtins.set(WORLD_INSIDE.values()))
        check("boys_dorm" in _zz_houses and all(1 < len(zzh_exits(h)) <= PATH_HOUSE_EXITS == 7 for h in _zz_houses),
              "B: a house holds at most seven exits (K11); the Boys' Dormitory has five", [(h, len(zzh_exits(h))) for h in _zz_houses])
        check(path_reach("dorm") == builtins.set(LOCATIONS) and len(LOCATIONS) == 35,
              "B: from my room every one of the %d places is reached by exits alone" % len(LOCATIONS),
              builtins.sorted(builtins.set(LOCATIONS) - path_reach("dorm")))
        check(all(l in path_reach(r) for r in ZZH_ROOMS + ("boys_dorm",) + ZZH_SEVEN for l in ("dorm", "courtyard", "ridge")),
              "B: and from each new place my room, the Courtyard and the ridge are reached")
        ## U0c1: the exits of 4.5.
        _zz_want = builtins.dict(
            girls_dorm=["dorm_yard", "nobara_room", "maki_room"], nobara_room=["girls_dorm"], maki_room=["girls_dorm"],
            staff_yard=["office", "utahime_office", "gojo_office", "teachers_lounge", "dorm_yard", "training_yard"],
            teachers_lounge=["staff_yard", "teachers_dorm"], teachers_dorm=["teachers_lounge"],
            training_yard=["training", "dojo", "storehouse", "pool", "courtyard", "staff_yard"], pool=["training_yard"],
            trailhead=["forest", "ridge", "riverside", "bathhouse", "dorm_yard"],
            bathhouse=["trailhead", "sauna"], sauna=["bathhouse"])
        _zz_got = builtins.dict((l, zzh_exits(l)) for l in _zz_want)
        check(_zz_got == _zz_want, "B: the exits of 4.5: the girls' corridor to its two rooms, the staff steps to the lounge and the "
              "lounge upstairs, the Training Yard to the pool, the Mountain Path to the Onsen and the Onsen to its sauna, each with its way back",
              [(l, _zz_got[l]) for l in _zz_want if _zz_got[l] != _zz_want[l]])
        _zz_yards = [path_hub(a["key"]) for a in AREAS]
        check(sum(len(zzh_exits(l)) for l in LOC_ORDER) == 70 and sum(len(zzh_exits(y)) for y in _zz_yards) == 33
              and [len(zzh_exits(y)) for y in _zz_yards] == [4, 5, 7, 6, 6, 5],
              "B: 70 exits in all, 33 of them from the six yards: the garden still has seven, the staff steps and the Training Yard six, "
              "the Mountain Path five (D6)", [(y, len(zzh_exits(y))) for y in _zz_yards])
        ## K12: on the old pictures the old exits stay where they were; only
        ## the three new ones (and the two doors in the girls' corridor) are added.
        _zz_moved = [(l, r) for l in ("staff_yard", "training_yard", "trailhead", "girls_dorm") for r in _zz_old[l]
                     if builtins.tuple(r) not in [(x["to"], x["x"], x["y"]) for x in path_exits(l)]]
        _zz_order = [l for l in ("staff_yard", "training_yard", "trailhead", "girls_dorm")
                     if [x["to"] for x in path_exits(l) if x["to"] not in ZZH_SEVEN] != [r[0] for r in _zz_old[l]]]
        check(not _zz_moved and not _zz_order,
              "B: in the three yards that gained an exit, and in the girls' corridor, every old exit keeps its point and its order (K12)",
              (_zz_moved, _zz_order))
        check(_zz_houses == ["bathhouse", "boys_dorm", "girls_dorm", "teachers_lounge"]
              and [len(zzh_exits(h)) for h in _zz_houses] == [2, 5, 3, 2],
              "B: four houses: the Onsen (2 exits), the Boys' Dormitory (5), the girls' corridor (3), the Teachers' Lounge (2)",
              [(h, len(zzh_exits(h))) for h in _zz_houses])
        check([path_words(k) for k in ZZH_SEVEN] == ["To Nobara's Room", "To Maki's Room", "To the Teachers' Lounge",
                                                     "To the Teachers' Dormitory", "To the Onsen", "To the Sauna", "To the Swimming Pool"],
              "B: the new exits' words", [path_words(k) for k in ZZH_SEVEN])
        check(path_words("boys_dorm") == "To the Boys' Dormitory" and path_words("dorm") == "To My Room"
              and path_words("yuji_room") == "To Yuji's Room" and path_words("megumi_room") == "To Megumi's Room"
              and path_words("senpai_room") == "To Panda and Toge's Room",
              "B: the exits' words: To the Boys' Dormitory, To My Room, To Yuji's Room, To Megumi's Room, To Panda and Toge's Room")
        _zz_acts = builtins.dict((a["id"], builtins.sorted(a["locs"])) for a in PLACE_ACTIONS if a["id"].startswith("path_"))
        check(_zz_acts["path_dorm"] == ["boys_dorm"]
              and _zz_acts["path_boys_dorm"] == ["dorm", "dorm_yard", "megumi_room", "senpai_room", "yuji_room"]
              and "dorm" not in _zz_acts["path_dorm_yard"],
              "B: the action path_dorm is offered from the corridor only; my room no longer offers path_dorm_yard",
              (_zz_acts["path_dorm"], _zz_acts["path_boys_dorm"]))
        check(path_validate() == [] and map_validate() == [] and _validate_world() == [] and hot_validate() == [],
              "B: the exits', the map's, the world's and the hotspots' validators find nothing",
              (path_validate(), map_validate(), _validate_world(), hot_validate())[:3])

        ## Each new rule fails when its table is broken on purpose.
        zzh.keep["exits"] = zzh_exit_table()
        _zz_f = zzh_findings(path_validate, lambda: PATH_EXITS.__setitem__("dorm", [("dorm_yard",) + _zz_pt["room"]]), zzh_restore_exits)
        check(any("first exit of 'dorm' must lead to its house" in x for x in _zz_f),
              "B (broken on purpose): my room opening onto the garden again fails lint", _zz_f)
        ## (the two test exits below stand at a made-up point: only where they lead is tested)
        _zz_f = zzh_findings(path_validate, lambda: PATH_EXITS["dorm_yard"].append(("yuji_room", 700, 900)), zzh_restore_exits)
        check(any("the hub 'dorm_yard' has an exit to 'yuji_room'" in x for x in _zz_f),
              "B (broken on purpose): a yard with an exit to a room inside a house fails lint", _zz_f)
        _zz_f = zzh_findings(path_validate, lambda: PATH_EXITS["dorm_common"].append(("rooftop", 700, 900)), zzh_restore_exits)
        check(any("'dorm_common' has an exit to 'rooftop'" in x for x in _zz_f),
              "B (broken on purpose): a room leading on to a place that is not inside it fails lint", _zz_f)
        check(path_validate() == [] and zzh_exit_table() == zzh.keep["exits"],
              "B: the table is whole again after the three tests", path_validate())

        _zz_wk = WORLD_ASLEEP["weekday"]
        _zz_f = zzh_findings(_validate_world, lambda: WORLD_ASLEEP.__setitem__("weekday", _zz_wk + ("zz_nobody",)),
                             lambda: WORLD_ASLEEP.__setitem__("weekday", _zz_wk))
        check(any("'zz_nobody' has no WORLD_HOMES row" in x for x in _zz_f),
              "B (broken on purpose): a name on an asleep list with no home row fails lint", _zz_f)
        _zz_f = zzh_findings(_validate_world, lambda: WORLD_HOMES.__setitem__("yaga", "office"),
                             lambda: WORLD_HOMES.__setitem__("yaga", "teachers_dorm"))
        check(any("WORLD_HOMES[yaga]" in x and "Night cell" in x for x in _zz_f),
              "B (broken on purpose): a home that is not the person's Night cell fails lint", _zz_f)
        _zz_f = zzh_findings(_validate_world, lambda: WEEKEND["yuji"].__setitem__("Night", "dorm_yard"), lambda: WEEKEND["yuji"].pop("Night"))
        check(any("WEEKEND[yuji] has a Night cell" in x for x in _zz_f),
              "B (broken on purpose): a weekend Night cell fails lint (the Night is the same on all seven days)", _zz_f)
        _zz_f = zzh_findings(_validate_world, lambda: WORLD_DOOR_BOND.__setitem__("zz_room", 20), lambda: WORLD_DOOR_BOND.pop("zz_room"))
        check(any("WORLD_DOOR_BOND has unknown place 'zz_room'" in x for x in _zz_f),
              "B (broken on purpose): a door level for a place that does not exist fails lint", _zz_f)
        _zz_spots = AREA_BY_KEY["dorms"]["spots"]
        _zz_mine = _zz_spots["boys_dorm"]
        _zz_f = zzh_findings(_validate_world, lambda: _zz_spots.__setitem__("yuji_room", _zz_spots["dorm_yard"]),
                             lambda: _zz_spots.pop("yuji_room"))
        _zz_g = zzh_findings(map_validate, lambda: _zz_spots.__setitem__("yuji_room", _zz_spots["dorm_yard"]),
                             lambda: _zz_spots.pop("yuji_room"))
        check(any("spots and its pinned places disagree" in x for x in _zz_f) and any("'yuji_room' is in 1 areas' spots" in x for x in _zz_g),
              "B (broken on purpose): a pin for a room that has none fails lint, in the world's validator and the map's", (_zz_f, _zz_g))
        _zz_g = zzh_findings(map_validate, lambda: _zz_spots.pop("boys_dorm"),
                             lambda: _zz_spots.__setitem__("boys_dorm", _zz_mine))
        check(any("'boys_dorm' is in 0 areas' spots" in x for x in _zz_g),
              "B (broken on purpose): a pinned place with no spot fails lint", _zz_g)
        ## U0c1's rules: the away table, and a house in another area.
        _zz_away = WORLD_AWAY["yuji"]
        _zz_f = zzh_findings(_validate_world, lambda: WORLD_AWAY.__setitem__("yuji", {("Sun", "Afternoon"): "zz_town"}),
                             lambda: WORLD_AWAY.__setitem__("yuji", _zz_away))
        _zz_g = zzh_findings(_validate_world, lambda: WORLD_AWAY.__setitem__("yuji", {("Sunday", "Afternoon"): "shibuya"}),
                             lambda: WORLD_AWAY.__setitem__("yuji", _zz_away))
        check(any("WORLD_AWAY[yuji]: unknown district 'zz_town'" in x for x in _zz_f) and any("is not (weekday, period)" in x for x in _zz_g),
              "B (broken on purpose): a WORLD_AWAY district that is not in DISTRICTS, or a cell that is not (weekday, period), fails lint",
              (_zz_f, _zz_g))
        _zz_f = zzh_findings(path_validate, lambda: PATH_EXITS.__setitem__("sauna", [("trailhead", 84, 520)]), zzh_restore_exits)
        check(any("first exit of 'sauna' must lead to its house 'bathhouse'" in x for x in _zz_f),
              "B (broken on purpose): the sauna opening onto the Mountain Path fails lint (the house rule holds for the new houses)", _zz_f)
        check(_validate_world() == [] and map_validate() == [] and path_validate() == [] and WORLD_HOMES["yaga"] == "teachers_dorm"
              and zzh_exit_table() == zzh.keep["exits"],
              "B: the tables are whole again", (_validate_world(), map_validate(), path_validate()))

        ########################################################################
        ## C. The protected walk
        ########################################################################
        _zz_src = renpy.file("room_paths.rpy").read().decode("utf-8").replace("\r\n", "\n")
        _zz_a = _zz_src.find("label path_walk(path_to):")
        _zz_end = '    call path_walk("trailhead")\n    return\n'
        _zz_b = _zz_src.find(_zz_end)
        _zz_block = _zz_src[_zz_a:_zz_b + len(_zz_end)] if (_zz_a >= 0 and _zz_b > _zz_a) else ""
        check((hashlib.sha256(_zz_block.encode("utf-8")).hexdigest(), len(_zz_block)) == ZZH_WALK_BLOCK,
              "C: label path_walk and the 24 old sb_do_path_ labels are textually what they were before the overhaul "
              "(their block of room_paths.rpy, %d characters, by sha256)" % ZZH_WALK_BLOCK[1],
              (len(_zz_block), hashlib.sha256(_zz_block.encode("utf-8")).hexdigest()))
        ## The same, by statement name (what a save's return sites and its
        ## rollback entries hold): every statement of that block, and of label
        ## sb_do_veil in sb_world.rpy, has the name it had before the overhaul.
        _zz_l0 = _zz_src[:_zz_a].count("\n") + 1
        _zz_l1 = _zz_src[:_zz_b + len(_zz_end)].count("\n")
        _zz_n = zzh_names("game/room_paths.rpy", _zz_l0, _zz_l1)
        check((len(_zz_n), zzh_names_hash(_zz_n)) == ZZH_WALK_NAMES,
              "C: the %d statements of path_walk and the 24 old labels keep their names (the scratch copy compiles over the "
              "owner's .rpyc, so these are the names the owner's saves hold)" % ZZH_WALK_NAMES[0],
              (len(_zz_n), zzh_names_hash(_zz_n), _zz_n[:3]))
        _zz_ws = renpy.file("sb_world.rpy").read().decode("utf-8").replace("\r\n", "\n").split("\n")
        _zz_v0 = _zz_ws.index("label sb_do_veil:") + 1
        _zz_v1 = next((i for i in range(_zz_v0, len(_zz_ws)) if _zz_ws[i][:1] not in ("", " ", "#")), len(_zz_ws))
        _zz_n = zzh_names("game/sb_world.rpy", _zz_v0, _zz_v1)
        check((len(_zz_n), zzh_names_hash(_zz_n)) == ZZH_VEIL_NAMES,
              "C: the %d statements of label sb_do_veil (sb_world.rpy) keep their names" % ZZH_VEIL_NAMES[0],
              (len(_zz_n), zzh_names_hash(_zz_n), _zz_v0, _zz_v1, _zz_n[:3]))
        check(len(ZZH_OLD_LABELS) == 24 and all(renpy.has_label("sb_do_path_" + l) for l in ZZH_OLD_LABELS)
              and all(('label sb_do_path_%s:\n    call path_walk("%s")\n    return\n' % (l, l)) in _zz_block for l in ZZH_OLD_LABELS)
              and renpy.has_label("path_walk"),
              "C: each of the 24 is there, with its one line")
        check(all(renpy.has_label("sb_do_path_" + l) and _zz_src.find("label sb_do_path_%s:" % l) > _zz_b
                  and ('label sb_do_path_%s:\n    call path_walk("%s")\n    return\n' % (l, l)) in _zz_src
                  for l in ("boys_dorm",) + ZZH_ROOMS),
              "C: the four new labels are appended after them, each with its line call path_walk(\"<to>\")")
        ## U0b's four are protected from the commit they landed in (2.3):
        ## their block is textually what it was, and U0c1's seven come after it.
        _zz_four = "".join('label sb_do_path_%s:\n    call path_walk("%s")\n    return\n\n' % (l, l) for l in ("boys_dorm",) + ZZH_ROOMS)
        _zz_c = _zz_src.find(_zz_four[:-1])
        _zz_at = [_zz_src.find('label sb_do_path_%s:\n    call path_walk("%s")\n    return\n' % (l, l)) for l in ZZH_SEVEN]
        check(_zz_c > _zz_b and all(a > _zz_c + len(_zz_four) - 1 for a in _zz_at) and _zz_at == builtins.sorted(_zz_at)
              and all(renpy.has_label("sb_do_path_" + l) for l in ZZH_SEVEN)
              and _zz_src.count("\nlabel sb_do_path_") == 35 and _zz_src.rstrip("\n").endswith('call path_walk("pool")\n    return'),
              "C: U0b's four labels are textually what they were, in one block; U0c1's seven are appended after them, in order, "
              "each with its line; 35 walk labels in all, and nothing after the last", (_zz_c, _zz_at, _zz_src.count("\nlabel sb_do_path_")))

        ########################################################################
        ## D. The Night
        ########################################################################
        _zz_want = ZZH_HOMES
        _zz_bad, _zz_sleep, _zz_never = [], builtins.dict(), []
        for _zz_d in range(8, 15):
            zzh_at(_zz_d, "Night")
            for _zz_w, _zz_l in _zz_want.items():
                ## U0n (plan 5.7a; docs/UI2_PINS.md Part 2c): at home, or in
                ## the room WORLD_LATE has them out late in that Night.
                if char_location(_zz_w) != (world_late_cell(_zz_w) or _zz_l) or world_home(_zz_w) != _zz_l:
                    _zz_bad.append((weekday(), _zz_w, char_location(_zz_w)))
            if who_is_here("dorm_yard") or who_is_here("dorm_common") or who_is_here("girls_dorm") or who_is_here("teachers_lounge"):
                _zz_bad.append((weekday(), "garden or common room", who_is_here("dorm_yard"), who_is_here("dorm_common")))
            _zz_out = [(weekday(), w, char_location(w)) for w in ROSTER_ORDER if w not in _zz_want and w != "gojo" and char_location(w)]
            _zz_bad += _zz_out
            _zz_sleep[weekday()] = builtins.sorted(w for w in ROSTER_ORDER if world_asleep(w))
            for _zz_p in PERIODS:
                store.period = _zz_p
                _zz_never += [(weekday(), _zz_p, w) for w in ("yaga", "gojo", "shoko") if world_asleep(w)]
                if _zz_p != "Night":
                    _zz_never += [(weekday(), _zz_p, w) for w in ROSTER_ORDER if world_asleep(w) or world_asleep(w, _zz_p)]
        check(not _zz_bad and len(_zz_want) == 10,
              "D: on each of the seven Nights everyone who lives on campus is in their own home, or where WORLD_LATE puts them that Night "
              "(the four boys, the two girls, Shoko, the three teachers), and the garden, the Common Room, the girls' corridor and the lounge are empty", _zz_bad[:6])
        check(all(_zz_sleep[d] == ["ijichi", "maki", "megumi", "panda", "utahime"] for d in ("Mon", "Tue", "Wed", "Thu", "Fri"))
              and all(_zz_sleep[d] == ["ijichi", "nobara", "toge", "utahime", "yuji"] for d in ("Sat", "Sun")) and len(_zz_sleep) == 7,
              "D: on weekday Nights Megumi, Maki and Panda are asleep, at weekends Yuji, Nobara and Toge: each can be found both ways; "
              "Utahime and Ijichi on all seven", _zz_sleep)
        check(not _zz_never,
              "D: nobody is asleep at any hour but Night; Yaga, Shoko and Gojo never",
              _zz_never[:6])
        check(builtins.dict(WORLD_HOMES) == ZZH_HOMES and "gojo" not in WORLD_HOMES and world_home("gojo") is None
              and world_home("maki") == "maki_room" and world_home("ijichi") == "teachers_dorm"
              and builtins.dict(WORLD_ASLEEP) == builtins.dict(weekday=("megumi", "maki", "panda", "utahime", "ijichi"),
                                                               weekend=("yuji", "nobara", "toge", "utahime", "ijichi")),
              "D: WORLD_HOMES holds the ten who live on campus (Shoko in the infirmary, the three teachers in the Teachers' Dormitory); "
              "Gojo has no home; WORLD_ASLEEP is the plan's two lists (3.2)", (builtins.dict(WORLD_HOMES), builtins.dict(WORLD_ASLEEP)))

        ## U0c1: the two girls and the teachers at Night
        zzh_at(zzh_day("Fri"), "Night")
        _zz_c = [who_is_here("maki_room"), stage_people("maki_room"), rail_asleep_line("maki_room"),
                 who_is_here("nobara_room"), stage_people("nobara_room"), rail_asleep_line("nobara_room"),
                 who_is_here("teachers_dorm"), stage_people("teachers_dorm"), rail_asleep_line("teachers_dorm"),
                 ambient_of("utahime", "teachers_dorm"), ambient_of("ijichi", "teachers_dorm"), ambient_of("yaga", "teachers_dorm")[0] != "asleep"]
        check(_zz_c == [["maki"], ([], []), "Maki is asleep.", ["nobara"], (["nobara"], []), "",
                        ["yaga", "utahime", "ijichi"], (["yaga"], []), "", ("asleep", None), ("asleep", None), True],
              "D: a weekday Night: Maki is in her room asleep and Nobara in hers, up; in the Teachers' Dormitory Yaga is up and on its "
              "stage, Utahime and Ijichi are counted there, asleep, and not on it", _zz_c)
        check(world_room_state("teachers_dorm") == builtins.dict(yaga="awake", utahime="asleep", ijichi="asleep")
              and world_room_state("senpai_room") == builtins.dict(panda="asleep", toge="awake")
              and world_room_state("maki_room") == builtins.dict(maki="asleep") and world_room_state("infirmary") == builtins.dict(shoko="awake")
              and world_room_state("dorm") == {} and world_room_state("girls_dorm") == {} and world_room_state("zz") == {},
              "D: world_room_state: {owner: awake, asleep or out} for a room, {} for a place that is nobody's home (D49)",
              (world_room_state("teachers_dorm"), world_room_state("senpai_room")))
        zzh_at(zzh_day("Sat"), "Night")
        _zz_c = [stage_people("maki_room"), stage_people("nobara_room"), rail_asleep_line("nobara_room"), stage_people("teachers_dorm"),
                 world_room_state("nobara_room"), world_room_state("teachers_dorm")]
        check(_zz_c == [(["maki"], []), ([], []), "Nobara is asleep.", (["yaga"], []), builtins.dict(nobara="asleep"),
                        builtins.dict(yaga="awake", utahime="asleep", ijichi="asleep")],
              "D: a weekend Night: Maki is up and Nobara asleep; the teachers are as on a weekday", _zz_c)
        zzh_at(zzh_day("Fri"), "Noon")
        check(world_room_state("teachers_dorm") == builtins.dict(yaga="out", utahime="out", ijichi="out")
              and world_room_state("nobara_room") == builtins.dict(nobara="out"),
              "D: and at a weekday Noon they are all out", world_room_state("teachers_dorm"))

        ## U0c1: the rest of 4.3's cells
        zzh_at(zzh_day("Sat"), "Noon")
        _zz_c = builtins.dict(
            morning=[char_location(w, "Morning") for w in ("nobara", "maki", "yaga")],
            afternoon=[who_is_here("pool", "Afternoon"), who_is_here("riverside", "Afternoon"), char_location("utahime", "Afternoon"),
                       char_location("yaga", "Afternoon")],
            evening=[who_is_here("bathhouse", "Evening"), who_is_here("dorm_yard", "Evening"), who_is_here("teachers_lounge", "Evening"),
                     who_is_here("dojo", "Evening")],
            noon=[char_location("yaga", "Noon"), char_location("maki", "Noon")])
        check(_zz_c == builtins.dict(morning=["nobara_room", "maki_room", "teachers_dorm"],
                                     afternoon=[["yuji", "nobara", "panda"], ["maki", "toge"], "teachers_lounge", None],
                                     evening=[["nobara", "maki", "utahime"], ["yuji"], ["yaga", "ijichi"], []],
                                     noon=["teachers_lounge", "dojo"]),
              "D: a Saturday: Nobara and Maki at home in the Morning, Yaga at his workbench; the pool holds three in the Afternoon and "
              "the river two; in the Evening Nobara, Maki and Utahime are at the Onsen, Yuji by the pond, Yaga and Ijichi in the lounge", _zz_c)
        zzh_at(zzh_day("Fri"), "Noon")
        _zz_c = [char_location("ijichi", p) for p in PERIODS] + [char_location("yaga", "Night"), char_location("utahime", "Night"),
                                                                  char_location("maki", "Evening"), char_location("nobara", "Morning")]
        check(_zz_c == ["gate", "gate", "gate", "teachers_lounge", "teachers_dorm", "teachers_dorm", "teachers_dorm", "riverside", "training_yard"],
              "D: a weekday: Ijichi keeps the gate from Morning to Afternoon, then the lounge, then the Teachers' Dormitory; "
              "the daytime cells nobody moved are as they were", _zz_c)

        ## U0c1: in Tokyo on Sunday afternoons (WORLD_AWAY, 7.6)
        zzh_at(zzh_day("Sun"), "Afternoon")
        _zz_c = [[(w, char_location(w), world_away(w)) for w in ("nobara", "maki", "yuji")],
                 who_is_here("pool"), who_is_here("riverside"), builtins.sorted(w for w in ROSTER_ORDER if world_away(w)),
                 [world_away(w, "Noon") or char_location(w, "Noon") for w in ("nobara", "maki", "yuji")],
                 [world_away(w, "Evening") or char_location(w, "Evening") for w in ("nobara", "maki", "yuji")],
                 person_now("nobara")["place"], person_now("nobara")["hidden"]]
        check(_zz_c == [[("nobara", None, "harajuku"), ("maki", None, "harajuku"), ("yuji", None, "shibuya")],
                        ["panda"], ["toge"], ["maki", "nobara", "yuji"], ["cafeteria", "dojo", "yuji_room"],
                        ["bathhouse", "bathhouse", "dorm_yard"], None, False],
              "D: on a Sunday Afternoon Nobara and Maki are in Harajuku and Yuji in Shibuya: off campus (the pool holds Panda, the river "
              "Toge); at Noon each is still where the weekend puts them, and they are back for the Evening", _zz_c)
        zzh_at(zzh_day("Sat"), "Afternoon")
        _zz_c = [[world_away(w) for w in ROSTER_ORDER if world_away(w)], char_location("nobara")]
        zzh_at(zzh_day("Sun"), "Afternoon")
        pin("nobara", "courtyard")
        _zz_c += [char_location("nobara"), world_away("nobara"), world_away("maki")]
        store.schedule_overrides = {}
        FLAG_SCHEDULES.append(("zz_flag", "maki", {"Afternoon": "dojo"}))
        store.flags.add("zz_flag")
        try:
            _zz_c += [char_location("maki"), world_away("maki")]
        finally:
            store.flags.discard("zz_flag")
            FLAG_SCHEDULES.pop()
        store.roster.remove("yuji")
        _zz_c += [world_away("yuji"), char_location("yuji")]
        store.roster.append("yuji")
        _zz_c += [world_away("megumi"), world_away("zz"), world_away("yuji", "Night")]
        check(_zz_c == [[], "pool", "courtyard", None, "harajuku", "dojo", None, None, None, None, None, None],
              "D: nobody is away on a Saturday; a story pin and a flag schedule each win over the away table; someone I have not met, "
              "someone the table does not send, and any other hour: world_away is None", _zz_c)

        ## U0c1: a companion bound for Tokyo goes when their hour, or the one before it, begins (7.6)
        _zz_c = []
        for _zz_d, _zz_p, _zz_w in (("Sun", "Morning", "nobara"), ("Sun", "Noon", "yuji"), ("Sun", "Morning", "megumi"),
                                    ("Sat", "Morning", "nobara"), ("Sun", "Afternoon", "maki"), ("Sun", "Evening", "nobara")):
            zzh_at(zzh_day(_zz_d), _zz_p)
            store.here = "courtyard"
            store.companion = _zz_w
            toast_clear()
            advance_period()
            _zz_c.append((_zz_d, store.period, store.companion, [t["text"] for t in TOASTQ.items]))
            store.companion = None
        zzh_at(zzh_day("Sun"), "Morning")
        store.companion = "maki"
        toast_clear()
        advance_period_soft(1)
        _zz_c.append(("soft", store.period, store.companion, [t["text"] for t in TOASTQ.items]))
        store.companion = None
        toast_clear()
        check(_zz_c == [("Sun", "Noon", None, ["Nobara heads off to catch the train into town."]),
                        ("Sun", "Afternoon", None, ["Yuji heads off to catch the train into town."]),
                        ("Sun", "Noon", "megumi", []), ("Sat", "Noon", "nobara", []),
                        ("Sun", "Evening", "maki", []), ("Sun", "Night", "nobara", []),
                        ("soft", "Noon", None, ["Maki heads off to catch the train into town."])],
              "D: on a Sunday, when Noon or the Afternoon begins, a companion the away table sends to Tokyo goes, with one toast; "
              "Megumi stays, and so does anyone on a Saturday or once they are back (advance_period and advance_period_soft alike)", _zz_c)

        ## the starred weekend cells and Yuji's weekend Evening
        zzh_at(zzh_day("Sat"), "Noon")
        _zz_c = [char_location("yuji", "Noon"), char_location("megumi", "Morning"), char_location("panda", "Morning"),
                 char_location("toge", "Morning"), char_location("yuji", "Evening")]
        zzh_at(zzh_day("Fri"), "Noon")
        _zz_c += [char_location("yuji", "Noon"), char_location("megumi", "Morning"), char_location("yuji", "Evening")]
        check(_zz_c == ["yuji_room", "megumi_room", "senpai_room", "senpai_room", "dorm_yard", "cafeteria", "classroom", "dorm_common"],
              "D: at weekends each of the four has a daytime hour at home (Yuji at Noon; Megumi, Panda and Toge in the Morning), "
              "and Yuji's weekend Evening is the garden; the weekdays are as they were", _zz_c)

        ## a sleeper, on a weekday Night: Panda
        zzh_at(zzh_day("Fri"), "Night")
        check(who_is_here("senpai_room") == ["panda", "toge"] and stage_people("senpai_room") == (["toge"], [])
              and ambient_of("panda", "senpai_room") == ("asleep", None) and ambient_of("toge", "senpai_room")[0] != "asleep"
              and world_home_state("panda") == "asleep" and world_home_state("toge") == "awake",
              "D: a weekday Night: Panda is in who_is_here('senpai_room'), absent from its stage, captioned asleep; Toge is up",
              (who_is_here("senpai_room"), stage_people("senpai_room"), ambient_of("panda", "senpai_room")))
        check(who_is_here("megumi_room") == ["megumi"] and stage_people("megumi_room") == ([], [])
              and who_is_here("yuji_room") == ["yuji"] and stage_people("yuji_room") == (["yuji"], []),
              "D: Megumi's room holds him, asleep, and its stage is empty; Yuji's holds him, on its stage",
              (stage_people("megumi_room"), stage_people("yuji_room")))
        check(rail_asleep_line("megumi_room") == "Megumi is asleep." and rail_asleep_line("senpai_room") == ""
              and rail_asleep_line("yuji_room") == "" and rail_asleep_line("dorm_yard") == "" and rail_asleep_line("dorm_common") == "",
              "D: an empty stage whose room holds a sleeper reads 'Megumi is asleep.', not 'Nobody here right now.'; "
              "no such line where someone is up, or where nobody is",
              (rail_asleep_line("megumi_room"), rail_asleep_line("senpai_room")))
        check(person_now("panda")["place"] == "senpai_room" and person_now("panda")["doing"] == "asleep"
              and builtins.sorted(person_now("panda")) == ["doing", "hidden", "name", "place", "reachable", "with_me"],
              "D: the journal reads him in the shared room, asleep (person_now keeps its six keys)", person_now("panda"))

        ## a mission whose giver is asleep
        _zz_mid = "cm_panda_1"
        _zz_m = MISSION_BY_ID[_zz_mid]

        check(_zz_m["who"] == "panda" and _zz_m["trigger"] == "start" and not _zz_m["where"] and not _zz_m["cost"],
              "D (fixture): cm_panda_1 is a character mission of Panda's with no place and no cost, which the night rule lets through",
              (_zz_m["who"], _zz_m["where"], _zz_m["cost"]))
        _zz_row = ("Panda · " + _zz_m["title"], "mission")
        _zz_0 = zzh_panda_view()
        _zz_v = zzh_with_status(_zz_mid, zzh_panda_view)
        check(_zz_mid not in _zz_0["here"] and _zz_mid in _zz_v["here"] and _zz_row in _zz_v["raw"] and _zz_v["tag"],
              "D (fixture): made available, the frozen missions_here and mission_markers list it with Panda asleep "
              "(they count a sleeper)", _zz_v)
        check(_zz_mid not in _zz_v["rail"] and ("mission", _zz_mid) not in _zz_v["rows"] and _zz_row not in _zz_v["marks"]
              and not _zz_v["news"] and _zz_v["badge"] == _zz_0["badge"] and _zz_v["waiting"] == _zz_0["waiting"]
              and _zz_v["rail"] == _zz_0["rail"] and _zz_v["marks"] == _zz_0["marks"],
              "D: on a weekday Night, Panda asleep: rail_missions('senpai_room') leaves his mission out, and the map shows no job mark, "
              "no gold badge and nothing more waiting for him", (_zz_v, _zz_0))
        zzh_at(zzh_day("Sat"), "Night")
        _zz_0 = zzh_panda_view()
        _zz_v = zzh_with_status(_zz_mid, zzh_panda_view)
        check(not world_asleep("panda") and stage_people("senpai_room") == (["panda"], []) and world_asleep("toge")
              and _zz_mid in _zz_v["rail"] and ("mission", _zz_mid) in _zz_v["rows"] and _zz_row in _zz_v["marks"]
              and _zz_v["marks"] == _zz_v["raw"] and _zz_v["news"] and _zz_v["badge"] and _zz_v["waiting"] == _zz_0["waiting"] + 1,
              "D: on a weekend Night he is awake and Toge asleep: the mission is offered in the column and marked on the map",
              (_zz_v, _zz_0))
        mission_cache_clear()

        ## never asleep: a companion, a story pin
        zzh_at(zzh_day("Fri"), "Night")
        store.here = "courtyard"
        store.companion = "panda"
        _zz_c = (world_asleep("panda"), world_home_state("panda"), "panda" in stage_people("courtyard")[0])
        store.here = "senpai_room"
        _zz_c += (world_asleep("panda"), world_home_state("panda"))
        store.companion = None
        check(_zz_c == (False, "out", True, False, "awake"),
              "D: whoever walks with me is never asleep: out with me, on the stage; awake when we stand in their room", _zz_c)
        pin("megumi", "megumi_room")
        _zz_c = (world_asleep("megumi"), stage_people("megumi_room")[0])
        pin("megumi", "rooftop")
        _zz_c += (world_asleep("megumi"), world_home_state("megumi"), who_is_here("megumi_room"))
        store.schedule_overrides = {}
        check(_zz_c == (False, ["megumi"], False, "out", []),
              "D: someone a story pin has placed is never asleep, in their own room or anywhere else", _zz_c)

        ## never asleep: a flag schedule, even one that puts them in their own room
        _zz_c = (world_asleep("megumi"), stage_people("megumi_room")[0])
        FLAG_SCHEDULES.append(("zz_flag", "megumi", {"Night": "megumi_room"}))
        store.flags.add("zz_flag")
        try:
            _zz_c += (char_location("megumi"), world_asleep("megumi"), world_home_state("megumi"),
                      stage_people("megumi_room")[0], ambient_of("megumi", "megumi_room")[0] != "asleep")
        finally:
            store.flags.discard("zz_flag")
            FLAG_SCHEDULES.pop()
        _zz_c += (world_asleep("megumi"), builtins.len([r for r in FLAG_SCHEDULES if r[0] == "zz_flag"]))
        check(_zz_c == (True, [], "megumi_room", False, "awake", ["megumi"], True, True, 0),
              "D: someone a flag schedule has placed is never asleep, although it puts him in his own room at Night: "
              "he is awake and on its stage (and asleep again once the flag is gone)", _zz_c)

        ## the asleep test comes ahead of the story caption (3.1: the function's first statement)
        _zz_real = store.rail_story_caption
        store.rail_story_caption = lambda who, loc: ("zz story", None)
        try:
            _zz_c = (world_asleep("panda"), ambient_of("panda", "senpai_room"), ambient_of("toge", "senpai_room"))
        finally:
            store.rail_story_caption = _zz_real
        check(_zz_c == (True, ("asleep", None), ("zz story", None)),
              "D: a sleeper is captioned asleep even when the story has a caption for them; "
              "someone awake takes the story's caption", _zz_c)

        ## the map's second level reads its marks through map_marks(), so a sleeper's job stays off the pins
        _zz_ms = renpy.file("ui_map.rpy").read().decode("utf-8").replace("\r\n", "\n")
        _zz_a = _zz_ms.find("\nscreen map_area(key):")
        _zz_b = _zz_ms.find("\nscreen ", _zz_a + 1)
        _zz_scr = _zz_ms[_zz_a:_zz_b] if _zz_a >= 0 and _zz_b > _zz_a else ""
        check(_zz_scr and "map_marks()" in _zz_scr and "mission_markers(" not in _zz_scr,
              "D: screen map_area takes its job marks from map_marks() and never from mission_markers() itself",
              (_zz_a, _zz_b, _zz_scr.count("map_marks()"), _zz_scr.count("mission_markers(")))
        zzh_at(zzh_day("Fri"), "Noon")
        check([world_home_state(w) for w in ("yuji", "megumi", "panda", "toge", "shoko", "gojo", "maki")]
              == ["out", "out", "out", "out", "awake", "out", "out"],
              "D: world_home_state at a weekday Noon: the boys and Maki are out, Shoko is in and awake, Gojo has no home",
              [world_home_state(w) for w in ("yuji", "megumi", "panda", "toge", "shoko", "gojo", "maki")])
        store.here = "dorm"

        ########################################################################
        ## E. Doors
        ########################################################################
        _zz_lines = builtins.dict(yuji_room="I don't know Yuji well enough to let myself in.",
                                  megumi_room="I don't know Megumi well enough to let myself in.",
                                  senpai_room="I don't know Panda or Toge well enough to let myself in.")
        _zz_bad = []
        for _zz_d, _zz_p in ((zzh_day("Fri"), "Noon"), (zzh_day("Fri"), "Night"), (zzh_day("Sat"), "Night"), (zzh_day("Sat"), "Morning")):
            zzh_at(_zz_d, _zz_p)
            for _zz_room in ZZH_ROOMS:
                _zz_own = world_door_owners(_zz_room)
                for _zz_w in _zz_own:
                    for _zz_o in _zz_own:
                        store.bonds[_zz_o] = 0
                    store.bonds[_zz_w] = 14
                    if place_access(_zz_room) != (False, _zz_lines[_zz_room], "Bond 15") or can_enter(_zz_room) != (False, _zz_lines[_zz_room]) \
                            or path_locked(_zz_room) != _zz_lines[_zz_room]:
                        _zz_bad.append((weekday(), _zz_p, _zz_room, _zz_w, 14, place_access(_zz_room)))
                    store.bonds[_zz_w] = 15
                    if place_access(_zz_room) != (True, "", "") or path_locked(_zz_room) != "":
                        _zz_bad.append((weekday(), _zz_p, _zz_room, _zz_w, 15, place_access(_zz_room)))
                    _zz_state = [world_home_state(o) for o in _zz_own]
                    zzh.rows.append((weekday(), _zz_p, _zz_room, _zz_w, _zz_state))
        check(not _zz_bad and len(zzh.rows) == 16,
              "E: each of the three doors is shut at Bond 14 with its line and the tag Bond 15, and open at Bond 15; "
              "the shared room on Panda's Bond alone and on Toge's alone (4 hours x 4 owners)", _zz_bad[:4])
        check(any(r[1] == "Noon" and r[4] == ["out"] for r in zzh.rows)
              and any(r[1] == "Night" and r[2] == "megumi_room" and r[4] == ["asleep"] for r in zzh.rows)
              and any(r[1] == "Night" and r[2] == "yuji_room" and r[4] == ["awake"] for r in zzh.rows)
              and any(r[1] == "Morning" and r[2] == "megumi_room" and r[4] == ["awake"] for r in zzh.rows)
              and any(r[1] == "Night" and r[2] == "senpai_room" and builtins.sorted(r[4]) == ["asleep", "awake"] for r in zzh.rows),
              "E: those hours cover an owner out (Noon), asleep (Night), up (Night) and at home by day (a weekend Morning): "
              "the door follows the Bond, never its owner", zzh.rows[:6])
        check(world_door_bond("yuji_room") == 15 and world_door_bond("senpai_room") == 15 and world_door_bond("dorm") is None
              and world_door_bond("boys_dorm") is None and world_door_bond("girls_dorm") == 15 and world_door_bond("nobara_room") == 15
              and world_door_owners("girls_dorm") == ["nobara", "maki"] and world_door_owners("maki_room") == ["maki"]
              and world_door_bond("teachers_dorm") is None and world_door_bond("pool") is None
              and world_door_owners("senpai_room") == ["panda", "toge"] and world_door_owners("megumi_room") == ["megumi"]
              and world_door_owners("dorm") == [] and builtins.dict(WORLD_DOOR_BOND) == {None: 15},
              "E: the level is one table entry, 15, for the five rooms and for the girls' corridor after dark; world_door_bond is None "
              "for a place with no Bond door (my room, the boys' corridor, the teachers' house, the pool)",
              builtins.dict(WORLD_DOOR_BOND))
        for _zz_w in ROSTER_ORDER:
            store.bonds[_zz_w] = 0
        WORLD_DOOR_BOND["megumi_room"] = 0
        _zz_c = (place_access("megumi_room")[0], place_access("yuji_room")[0], world_door_bond("megumi_room"))
        del WORLD_DOOR_BOND["megumi_room"]
        WORLD_DOOR_BOND[None] = 0
        _zz_c += (place_access("yuji_room")[0], place_access("senpai_room")[0])
        WORLD_DOOR_BOND[None] = 15
        check(_zz_c == (True, False, 0, True, True) and not place_access("yuji_room")[0],
              "E: a row for one door moves that door alone, and changing the one entry moves them all", _zz_c)
        ## The Bond clause is for a room inside a house. A corridor that is
        ## given owners later (3.2: girls_dorm, Nobara and Maki) is not closed
        ## by it: its door's rule is written beside the corridor's own test.
        _zz_was = (store.day, store.period)
        WORLD_DOOR_OWNERS["boys_dorm"] = ("yuji",)
        try:
            _zz_c = [world_door_owners("boys_dorm"), world_door_bond("boys_dorm"), []]
            for _zz_p in ("Morning", "Night"):
                zzh_at(zzh_day("Fri"), _zz_p)
                _zz_c[2].append(place_access("boys_dorm"))
            _zz_c = builtins.tuple(_zz_c) + (place_access("yuji_room")[0],)
        finally:
            del WORLD_DOOR_OWNERS["boys_dorm"]
            zzh_at(*_zz_was)
        check(_zz_c == (["yuji"], 15, [(True, "", ""), (True, "", "")], False)
              and world_door_owners("boys_dorm") == [] and world_door_bond("boys_dorm") is None
              and [l for l in WORLD_DOOR_OWNERS if not world_inside(l)] == ["girls_dorm"],
              "E: owners named for a corridor lock nothing by themselves (a test row for the Boys' Dormitory, Bond 0: "
              "open by day and at Night); the Bond clause closes only a room inside a house, and the one corridor with owners, "
              "the girls', has its own rule (below)",
              _zz_c)
        _zz_c = [place_access("megumi_room")[0]]
        flag("door_megumi_room")
        _zz_c += [place_access("megumi_room"), place_access("yuji_room")[0]]
        store.flags.discard("door_megumi_room")
        flag("door_office")
        zzh_at(zzh_day("Fri"), "Night")
        _zz_c += [place_access("office")[0]]
        store.flags.discard("door_office")
        _zz_c += [place_access("office")[0], place_access("megumi_room")[0]]
        check(_zz_c == [False, (True, "", ""), False, True, False, False],
              "E: with the flag door_megumi_room and Bond 0 Megumi's door opens, and only his; "
              "the flag door_<place> opens any place (Yaga's office at Night)", _zz_c)
        store.companion = "toge"
        _zz_c = [place_access("senpai_room")[0], place_access("megumi_room")[0]]
        store.companion = None
        _zz_c += [place_access("senpai_room")[0]]
        check(_zz_c == [True, False, False], "E: an owner walking with me opens their own door, at Bond 0", _zz_c)
        store.explore_mode = True
        _zz_c = [place_access(r)[0] for r in ZZH_ROOMS]
        store.explore_mode = False
        check(all(_zz_c), "E: explore mode opens every door, as it opens everything", _zz_c)
        check(place_access("dorm") == (True, "", "") and place_access("boys_dorm") == (True, "", "") and place_access("dorm_yard") == (True, "", ""),
              "E: my room, the corridor and the garden are always open (Bond 0, at Night)")
        zzh_at(zzh_day("Fri"), "Night")
        check(person_now("megumi")["hidden"] and person_now("megumi")["place"] is None,
              "E: behind a door I can't open, someone is hidden from the journal's Go there (the name is U1's)", person_now("megumi"))

        ## --- U0c1: the girls' rooms, the corridor after dark, the house first, the pool ---
        zzh_fix(bond=0)
        _zz_bad = []
        del zzh.rows[:]
        for _zz_d, _zz_p in ((zzh_day("Fri"), "Noon"), (zzh_day("Fri"), "Night"), (zzh_day("Sat"), "Night"), (zzh_day("Sat"), "Morning")):
            zzh_at(_zz_d, _zz_p)
            store.here = "girls_dorm"       ## standing in the corridor, so each door answers for itself
            for _zz_room, _zz_w, _zz_o in (("nobara_room", "nobara", "maki"), ("maki_room", "maki", "nobara")):
                store.bonds[_zz_o] = 100
                store.bonds[_zz_w] = 14
                if place_access(_zz_room) != (False, ZZH_KNOCK, "Bond 15") or path_locked(_zz_room) != ZZH_KNOCK:
                    _zz_bad.append((weekday(), _zz_p, _zz_room, 14, place_access(_zz_room)))
                store.bonds[_zz_w] = 15
                if place_access(_zz_room) != (True, "", "") or path_locked(_zz_room) != "":
                    _zz_bad.append((weekday(), _zz_p, _zz_room, 15, place_access(_zz_room)))
                zzh.rows.append((weekday(), _zz_p, _zz_room, world_home_state(_zz_w)))
                store.bonds[_zz_o] = store.bonds[_zz_w] = 0
        check(not _zz_bad and len(zzh.rows) == 8
              and builtins.sorted(builtins.set(r[3] for r in zzh.rows)) == ["asleep", "awake", "out"],
              "E: each girl's door is shut at Bond 14 with her line (\"I don't know her well enough to knock.\", Bond 15) and open at 15, "
              "whether she is out, in or asleep; the other girl's Bond (100) does not open it", (_zz_bad[:4], zzh.rows))
        del zzh.rows[:]
        store.here = "dorm_yard"
        _zz_c = []
        for _zz_p in PERIODS:
            zzh_at(zzh_day("Fri"), _zz_p)
            store.bonds["nobara"] = store.bonds["maki"] = 14
            _zz_r = [place_access("girls_dorm")]
            store.bonds["nobara"] = 15
            _zz_r.append(place_access("girls_dorm")[0])
            store.bonds["nobara"], store.bonds["maki"] = 0, 15
            _zz_r.append(place_access("girls_dorm")[0])
            store.bonds["maki"] = 0
            flag("invited_girls_dorm")
            _zz_r.append(place_access("girls_dorm")[0])
            store.flags.discard("invited_girls_dorm")
            store.companion = "nobara"
            _zz_r.append(place_access("girls_dorm")[0])
            store.companion = None
            _zz_c.append(_zz_r)
        _zz_shut = (False, ZZH_CORRIDOR, "After dark")
        check(_zz_c == [[(True, "", ""), True, True, True, True]] * 3 + [[_zz_shut, True, True, True, False]] * 2,
              "E: the girls' corridor is open by day; in the Evening and at Night it is shut at Bond 14 with both, with its old sentence, "
              "and open at Bond 15 with Nobara alone, with Maki alone, or with the flag invited_girls_dorm (D10); "
              "walking with one of them does not open it", _zz_c)
        ## the house first, and its two exceptions (4.2)
        zzh_at(zzh_day("Fri"), "Night")
        store.bonds["nobara"] = store.bonds["maki"] = 0
        _zz_c = [place_access("nobara_room"), can_enter("maki_room")]
        store.here = "girls_dorm"
        _zz_c += [place_access("nobara_room")]
        store.here = "maki_room"
        _zz_c += [place_access("nobara_room"), place_access("girls_dorm")]
        store.here = "dorm_yard"
        flag("door_nobara_room")
        _zz_c += [place_access("nobara_room"), place_access("maki_room")[0], place_access("girls_dorm")[0]]
        store.flags.discard("door_nobara_room")
        store.bonds["maki"] = 15
        _zz_c += [place_access("maki_room"), place_access("nobara_room")]
        store.bonds["maki"] = 0
        zzh_at(zzh_day("Fri"), "Noon")
        _zz_c += [place_access("nobara_room")]
        check(_zz_c == [_zz_shut, _zz_shut[:2], (False, ZZH_KNOCK, "Bond 15"), (False, ZZH_KNOCK, "Bond 15"), (True, "", ""),
                        (True, "", ""), False, False, (True, "", ""), (False, ZZH_KNOCK, "Bond 15"), (False, ZZH_KNOCK, "Bond 15")],
              "E: a room inside a house asks its house first: at Night from the garden, Nobara's room answers with the corridor's "
              "sentence; standing in the corridor or in Maki's room it answers with its own line (and the corridor is open from a room "
              "inside it); its flag door_nobara_room opens it past the corridor, and only it; Bond 15 with Maki opens the corridor and "
              "her door but not Nobara's; by day the corridor is open and the room says its own line", _zz_c)
        _zz_c = []
        for _zz_room, _zz_house in (("dorm", "boys_dorm"), ("yuji_room", "boys_dorm"), ("nobara_room", "girls_dorm"),
                                    ("teachers_dorm", "teachers_lounge"), ("sauna", "bathhouse")):
            for _zz_p in ("Evening", "Night"):
                zzh_at(zzh_day("Fri"), _zz_p)
                store.here = _zz_room
                _zz_c.append(place_access(_zz_house) == (True, "", "") and path_locked(_zz_house) == ""
                             and path_exits(_zz_room)[0]["to"] == _zz_house and path_exits(_zz_room)[0]["locked_reason"] == "")
        store.here = "dorm_yard"
        check(all(_zz_c) and len(_zz_c) == 10,
              "E: once inside I am never locked in: from a room inside it each house is open, after dark, at Bond 0 (my room, a boy's "
              "room, Nobara's, the Teachers' Dormitory, the Sauna)", _zz_c)
        _zz_c = []
        for _zz_p in PERIODS:
            zzh_at(zzh_day("Fri"), _zz_p)
            _zz_c.append((place_access("pool"), [place_access(l)[0] for l in ("teachers_lounge", "teachers_dorm", "bathhouse", "sauna")]))
        store.here = "pool"
        _zz_c.append((place_access("training_yard"), path_exits("pool")[0]["locked_reason"]))
        store.here = "dorm_yard"
        flag("door_pool")
        _zz_c.append(place_access("pool")[0])
        store.flags.discard("door_pool")
        check(_zz_c == [((True, "", ""), [True] * 4)] * 4 + [((False, "The gate's chained after dark.", "Night"), [True] * 4),
                                                              ((True, "", ""), ""), True],
              "E: the pool is closed at Night (\"The gate's chained after dark.\", Night) and open at every other hour; the teachers' "
              "house, the Onsen and its sauna are always open; standing at the pool at Night I can still walk out; the flag opens it", _zz_c)
        zzh_at(zzh_day("Fri"), "Night")
        store.explore_mode = True
        _zz_c = [place_access(r)[0] for r in ZZH_SEVEN + ("girls_dorm",)]
        store.explore_mode = False
        check(all(_zz_c), "E: explore mode opens the seven new places and the corridor, at Night", _zz_c)
        _zz_c = [person_now(w) for w in ("nobara", "maki", "utahime", "yaga")]
        check(_zz_c[0]["hidden"] and _zz_c[0]["place"] is None and _zz_c[1]["hidden"]
              and _zz_c[2]["place"] == "teachers_dorm" and _zz_c[2]["doing"] == "asleep" and not _zz_c[2]["hidden"]
              and _zz_c[3]["place"] == "teachers_dorm" and _zz_c[3]["doing"] != "asleep"
              and all(builtins.sorted(v) == ["doing", "hidden", "name", "place", "reachable", "with_me"] for v in _zz_c),
              "E: at Night, Bond 0: the two girls are hidden behind their doors (the name is U1's); Utahime reads in the Teachers' "
              "Dormitory, asleep, and Yaga there, up (person_now keeps its six keys)", _zz_c)

        ########################################################################
        ## F. The map's pins
        ########################################################################
        zzh_fix()
        check(map_pins("dorms") == ["dorm_yard", "dorm", "dorm_common", "girls_dorm", "rooftop", "boys_dorm"]
              and builtins.sorted(map_spots("dorms")) == builtins.sorted(map_pins("dorms"))
              and all(map_pins(a["key"]) == [l for l in a["places"] if l not in WORLD_PINLESS] for a in AREAS)
              and map_pins("staff") == ["staff_yard", "office", "utahime_office", "gojo_office", "teachers_lounge"]
              and map_pins("grounds") == ["training_yard", "training", "dojo", "storehouse", "pool"]
              and map_pins("mountain") == ["trailhead", "forest", "riverside", "ridge", "bathhouse"]
              and builtins.max(len(map_pins(a["key"])) for a in AREAS) == 6 and sum(len(map_pins(a["key"])) for a in AREAS) == 28,
              "F: the Dormitories have six pins, my room's and the Boys' Dormitory's among them, and none for the girls' rooms; "
              "the Staff Building gains the lounge's, the Training Grounds the pool's, the Mountain the Onsen's (five each; 28 pins "
              "for 35 places); the Teachers' Dormitory and the Sauna have none",
              [(a["key"], map_pins(a["key"])) for a in AREAS])
        _zz_near = []
        for _zz_a in AREAS:
            _zz_sp = map_spots(_zz_a["key"])
            _zz_near += [(a, b) for a in _zz_sp for b in _zz_sp
                         if a < b and abs(_zz_sp[a][0] - _zz_sp[b][0]) < 240 and abs(_zz_sp[a][1] - _zz_sp[b][1]) < 120]
            _zz_near += [(a,) for a, (x, y) in _zz_sp.items()
                         if not (MAP_PIN_FRAME[0] <= x <= MAP_PIN_FRAME[2] and MAP_PIN_FRAME[1] <= y <= MAP_PIN_FRAME[3])]
        check(not _zz_near and all(builtins.sorted(map_spots(a["key"])) == builtins.sorted(map_pins(a["key"])) for a in AREAS),
              "F: in every area each pin, the three new ones among them, stands clear of every other (240 px across or 120 px down), "
              "inside the pin frame, on today's area pictures", _zz_near)
        _zz_sp = map_spots("dorms")
        _zz_near = [(a, b) for a in _zz_sp for b in _zz_sp
                    if a < b and abs(_zz_sp[a][0] - _zz_sp[b][0]) < 240 and abs(_zz_sp[a][1] - _zz_sp[b][1]) < 120]
        check(not _zz_near and all(MAP_PIN_FRAME[0] <= x <= MAP_PIN_FRAME[2] and MAP_PIN_FRAME[1] <= y <= MAP_PIN_FRAME[3] for x, y in _zz_sp.values()),
              "F: the new pin stands clear of my room's and of every other (240 px across or 120 px down), inside the pin frame", (_zz_near, _zz_sp))
        check(map_pin_icon("dorm") == "place_dorm" and map_pin_icon("boys_dorm") == "place_boys_dorm"
              and map_pin_icon("dorm_yard") == ("place_dorm_yard" if icon_has_art("place_dorm_yard") else "area_dorms")
              and path_icon("dorm_yard") == map_pin_icon("dorm_yard") and "place_dorm_yard" in ICONS,
              "F: a yard keeps its area's icon, on its pin and on an exit to it, until its own picture is cut",
              (map_pin_icon("dorm_yard"), path_icon("dorm_yard")))
        ## The Courtyard is the heart's hub and has had a picture of its own
        ## since phase 2 (ic_place_courtyard.png), but it is not one of the
        ## five yards (3.1, 4.8): an exit to it stays area_heart and its pin
        ## stays place_courtyard, as before the overhaul.
        _zz_yards = ("school_yard", "dorm_yard", "staff_yard", "training_yard", "trailhead")
        _zz_to_ct = [(f, r["icon"]) for f in LOC_ORDER for r in path_exits(f) if r["to"] == "courtyard"]
        check(builtins.tuple(PATH_YARD_ICONS) == _zz_yards and icon_has_art("place_courtyard")
              and path_icon("courtyard") == "area_heart" and map_pin_icon("courtyard") == "place_courtyard"
              and icon_for("act", "path_courtyard") == "area_heart"
              and len(_zz_to_ct) == 4 and all(i == "area_heart" for f, i in _zz_to_ct)
              and all(path_icon(y) == "area_" + area_of(y) and map_pin_icon(y) == "area_" + area_of(y)
                      for y in _zz_yards if not icon_has_art("place_" + y)),
              "F: no exit changed its icon: the four exits to the Courtyard are still area_heart though its own picture exists, "
              "its pin is still place_courtyard, and each of the five yards wears its area's until its picture is cut",
              (_zz_to_ct, path_icon("courtyard"), map_pin_icon("courtyard")))
        check(len(ICONS) == 114 and icon_for("do", "swim_pool") == "swim"
              and all(("place_" + k) in ICONS and icon_for("place", k) == "place_" + k
                      for k in ("boys_dorm", "yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room",
                                "teachers_lounge", "teachers_dorm", "bathhouse", "sauna", "pool"))
              and all(k in ICONS for k in ("bath_soak", "bath_sauna", "pool_swim", "cards_invite", "history", "auto", "save",
                                           "help", "continue", "at_home")),
              "F: ICONS holds 114 names: the eleven places, the five yards, four actions, History, Auto, Save, help, continue, at_home; "
              "swim_pool takes the swim icon", len(ICONS))
        check(map_area_tip("dorms")[0].split("\n")[0]
              == "Dormitory Garden · My Room · Dorm Common Room · Girls' Dormitory · Rooftop · Boys' Dormitory",
              "F: the Dormitories marker's hover line names its six pinned places", map_area_tip("dorms")[0])
        check(map_area_tip("staff")[0].split("\n")[0].endswith("Gojo's Office · Teachers' Lounge")
              and map_area_tip("grounds")[0].split("\n")[0].endswith("Storehouse · Swimming Pool")
              and map_area_tip("mountain")[0].split("\n")[0].endswith("Mountain Ridge · Onsen")
              and [map_pin_icon(l) for l in ("teachers_lounge", "pool", "bathhouse")] == ["place_teachers_lounge", "place_pool", "place_bathhouse"],
              "F: the other three markers' hover lines name their new pinned place, last; each new pin wears its own icon name",
              [map_area_tip(k)[0].split("\n")[0] for k in ("staff", "grounds", "mountain")])

    ############################################################################
    ## G. Every way home still ends in my room
    ############################################################################
    $ zzh.i = 0
    while zzh.i < len(LOC_ORDER):
        python:
            zzh_fix(day=zzh_day("Fri"), period="Night", here=LOC_ORDER[zzh.i])
            zzh.keep["day"] = day
            zzh.keep["said"] = len(zzh.texts)
            autoplay(True)
        call sb_do_night_bed
        python:
            autoplay(False)
            _zz_l = LOC_ORDER[zzh.i]
            _zz_said = zzh.texts[zzh.keep["said"]:]
            if not (here == "dorm" and day == zzh.keep["day"] + 1 and period == PERIODS[0] and not night_pending()
                    and _zz_said.count("I walk back while I can still feel my feet.") == (0 if _zz_l == "dorm" else 1)
                    and _zz_said.count("I sleep.") == 1):
                zzh.rows.append(("bed", _zz_l, here, day, period, _zz_said[-3:]))
            ## the day turns here, and the loop walks me home
            zzh_fix(day=zzh_day("Fri"), period="Night", here=_zz_l)
            new_day()
            zzh.keep["pending"] = night_pending()
            zzh.keep["line"] = night_carry_line()
            zzh.keep["said"] = len(zzh.said)
            autoplay(True)
        if zzh.keep["pending"]:
            call night_carry_home
        python:
            autoplay(False)
            _zz_l = LOC_ORDER[zzh.i]
            _zz_said = zzh_carry_said(zzh.keep["said"])
            _zz_line = NIGHT_CARRY_LINES.get(_zz_l) or NIGHT_CARRY_LINES[area_of(_zz_l)]
            if not (here == "dorm" and night_carried == "" and not night_pending()
                    and zzh.keep["pending"] == (_zz_l != "dorm")
                    and (_zz_l == "dorm" or (zzh.keep["line"] == _zz_line and _zz_said == [_zz_line]))):
                zzh.rows.append(("carry", _zz_l, here, zzh.keep["line"], _zz_said))
            zzh.i += 1
    python:
        _zz_bad = [r for r in zzh.rows if r[0] in ("bed", "carry")]
        check(not _zz_bad and zzh.i == len(LOC_ORDER),
              "G: from every one of the %d places at Night, Go to bed ends in my room the next morning (one walking line, none from my room)" % zzh.i,
              [r for r in _zz_bad if r[0] == "bed"][:3])
        check(not [r for r in _zz_bad if r[0] == "carry"],
              "G: and when the day turns in any of them the loop walks me home with that place's own line, or its area's",
              [r for r in _zz_bad if r[0] == "carry"][:3])
        check(all(NIGHT_CARRY_LINES.get(r) is None for r in ("boys_dorm",) + ZZH_ROOMS)
              and "one that isn't. Mine." in NIGHT_CARRY_LINES["dorms"],
              "G: the corridor and the boys' rooms take the Dormitories' line (\"a row of closed doors and one that isn't. Mine.\")")
        note("G: the girls' rooms' own walk-home line (the corridor's) is U0c2's, in sb_night.rpy; until then they take",
             [NIGHT_CARRY_LINES.get(r) or NIGHT_CARRY_LINES[area_of(r)] for r in ZZH_GIRLS])

        ## a Gojo night
        zzh_fix(day=zzh_day("Fri"), period="Night", here=NIGHT_GOJO["place"], control=30)
        gojo_in = True
        night_gojo_invite()
        zzh.keep["day"] = day
        zzh.keep["ok"] = night_gojo_ok()
        autoplay(True)
    call sb_do_night_gojo
    python:
        autoplay(False)
        check(zzh.keep["ok"] and here == "dorm" and day == zzh.keep["day"] + 1 and period == PERIODS[0] and not night_pending(),
              "G: a Gojo night on the ridge ends in my room the next morning", (zzh.keep["ok"], here, day, period))

        ## a night out
        zzh_fix(day=zzh_day("Fri"), period="Evening", here="gate", yen=2000)
        zzh.keep["day"] = day
        autoplay(True)
    call night_out("shibuya")
    python:
        autoplay(False)
        check(here == "dorm" and day == zzh.keep["day"] + 1 and period == PERIODS[0] and yen < 2000 and not night_pending(),
              "G: a night out in Shibuya ends in my room the next morning", (here, day, period, yen))

        ## the Sun Mall
        zzh_fix(day=zzh_day("Thu"), period="Morning", here="office")
        store.flags.discard("sunmall_done")
        autoplay(True)
    scene black
    call ev_mission_sunmall
    python:
        autoplay(False)
        check(has_flag("sunmall_done") and here == "dorm" and period == "Night",
              "G: the Sun Mall ends in my room, at Night", (has_flag("sunmall_done"), here, period))

    ############################################################################
    ## The worst case for the new places' place views (R6): four toasts, the
    ## banner, skipping. worst_boys_dorm.png, worst_megumi_room.png (a weekday
    ## Night, Megumi asleep), worst_senpai_room.png (a weekend Morning, both in).
    ############################################################################
    ## U0c1: and of the seven: worst_nobara_room.png (a weekend Morning, her at
    ## home), worst_maki_room.png (a weekday Night, Maki asleep),
    ## worst_teachers_lounge.png (a weekend Evening, Yaga and Ijichi),
    ## worst_teachers_dorm.png (a weekday Night), worst_bathhouse.png (a weekend
    ## Evening: three people), worst_sauna.png, worst_pool.png (a Saturday
    ## Afternoon: three people). And the three yards that gained an exit, on
    ## today's pictures (K12): worst_staff_yard.png, worst_training_yard.png,
    ## worst_trailhead.png.
    $ zzh.i = 0
    while zzh.i < 13:
        python:
            _zz_l, _zz_d, _zz_p = (("boys_dorm", "Fri", "Noon"), ("megumi_room", "Fri", "Night"), ("senpai_room", "Sat", "Morning"),
                                   ("nobara_room", "Sat", "Morning"), ("maki_room", "Fri", "Night"), ("teachers_lounge", "Sat", "Evening"),
                                   ("teachers_dorm", "Fri", "Night"), ("bathhouse", "Sat", "Evening"), ("sauna", "Fri", "Noon"),
                                   ("pool", "Sat", "Afternoon"), ("staff_yard", "Fri", "Noon"), ("training_yard", "Fri", "Noon"),
                                   ("trailhead", "Fri", "Noon"))[zzh.i]
            zzh_fix(day=zzh_day(_zz_d), period=_zz_p, here=_zz_l)
            renpy.scene()
            renpy.show("bg", what=graded_bg())
            _zz_ok = zz_worst("sb_place", name="worst_" + _zz_l)
            _zz_t = zz_texts("sb_place")
            check(_zz_ok and here == _zz_l
                  and (("Megumi is asleep." in _zz_t and "Nobody here right now." not in _zz_t) if _zz_l == "megumi_room" else True)
                  and (("Nobody here right now." in _zz_t) if _zz_l == "boys_dorm" else True)
                  and ((stage_people(_zz_l)[0] == ["panda", "toge"]) if _zz_l == "senpai_room" else True)
                  and (("Maki is asleep." in _zz_t and "Nobody here right now." not in _zz_t) if _zz_l == "maki_room" else True)
                  and stage_people(_zz_l)[0] == {"nobara_room": ["nobara"], "teachers_lounge": ["yaga", "ijichi"], "teachers_dorm": ["yaga"],
                                                 "bathhouse": ["nobara", "maki", "utahime"], "pool": ["yuji", "nobara", "panda"]}.get(
                                                     _zz_l, stage_people(_zz_l)[0]),
                  "the place view of %s in the worst case is drawn (four toasts, the banner, skipping)%s" % (
                      _zz_l, {"megumi_room": ", and the line 'Megumi is asleep.'", "boys_dorm": ", nobody in the corridor",
                              "senpai_room": ", Panda and Toge at home on a weekend Morning",
                              "nobara_room": ", Nobara at home on a weekend Morning", "maki_room": ", and the line 'Maki is asleep.'",
                              "teachers_lounge": ", Yaga and Ijichi on a weekend Evening", "teachers_dorm": ", Yaga up at Night",
                              "bathhouse": ", Nobara, Maki and Utahime in the rest hall on a weekend Evening",
                              "pool": ", Yuji, Nobara and Panda on the deck on a Saturday Afternoon"}.get(_zz_l, "")),
                  [t for t in _zz_t if "asleep" in t or "Nobody" in t] + [stage_people(_zz_l)[0]])
            renpy.hide_screen("sb_place")
            zzh.i += 1

    ## U0c1: the three other area views that gained a pin, as drawn.
    $ zzh.i = 0
    while zzh.i < 3:
        python:
            _zz_a, _zz_l, _zz_no = (("staff", "teachers_lounge", "teachers_dorm"), ("grounds", "pool", None),
                                    ("mountain", "bathhouse", "sauna"))[zzh.i]
            zzh_fix(day=zzh_day("Sat"), period="Evening", here="courtyard")
            renpy.scene()
            renpy.show_screen("sb_map", area=_zz_a)
            zz_render(0.6)
            _zz_rows = [l for l in LOC_ORDER if renpy.get_widget("sb_map", "row_" + l) is not None]
            check(builtins.sorted(_zz_rows) == builtins.sorted(map_pins(_zz_a)) and _zz_l in _zz_rows and _zz_no not in _zz_rows
                  and len(_zz_rows) == 5,
                  "the %s view is drawn with five pins, the new one (%s) among them%s" % (
                      AREA_BY_KEY[_zz_a]["name"], LOCATIONS[_zz_l]["name"],
                      (", and none for the %s" % LOCATIONS[_zz_no]["name"]) if _zz_no else ""), _zz_rows)
            shot("map_" + _zz_a, wait=0)
            renpy.hide_screen("sb_map")
            zzh.i += 1

    ############################################################################
    ## H to O: the real loop
    ############################################################################
    scene black
    python:
        _zz_got = zzh_copy_saves()
        check(builtins.sorted(_zz_got) == builtins.sorted(ZZH_SAVES) and all(renpy.can_load(s) for s in ZZH_SAVES),
              "L (fixture): the three saves made before the overhaul are in the scratch save folder",
              (_zz_got, [renpy.can_load(s) for s in ZZH_SAVES]))
        zzh_fix(day=zzh_day("Fri"), period="Noon", here="dorm", yen=40000)
        zzh_scrub()
        del zzh.rows[:]
        zzh.on = True
        zzh.t0 = zzh.t_stage = time.time()
    jump sandbox
