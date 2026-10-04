## tools/smoke/p2_view.rpy -- phase 2, P5: the place view alive
## (docs/PHASE2_DESIGN.md 4.5, section 7 "P5", R9, R10).
##
##   tools/smoke.sh tools/smoke/p2_view.rpy
##
## Every acceptance bullet of P5 is a named check here. The sections:
##   1  the light after Wait            7  the foreground: files, draw order,
##   2  slots, stage_x, the sidecar        the stand-in path
##   3  poses (the overlay's pictures)  8  lit_sprite: blink and talk layers
##   4  rectangles; view_stage alone    9  motion (zz_calls), no blur in a function
##   5  tools/install_pose.py          10  the name tags, the budget, hover labels
##   6  the pose plan against the      11  idle to talking: skipping, a replay,
##      schedule; the polygon files        the pickles
##                                     12  the save test, in real dialogue (last:
##                                         it loads, rolls back and ends the run)
##
## Test pictures (the asset overlay, tools/smoke/assets/p2_view/game/; they
## never reach the real game/images):
##   images/place/pose_dorm_common__nobara__evening.png   a plain figure on the
##       sofa of the evening common room (only the box around it is filled)
##   images/place/pose_dorm_common__yuji.png              a day pose, flat
##   layout/view_dorm_common.json                         their two boxes
##   images/char/fx/fx_yuji_blink.png, fx_yuji_talk.png   Yuji's neutral sprite
##       with the eyes shut / the mouth open
## install_pose.py's own test pictures are drawn when the harness runs (the
## script is ZZV_POSE_PY below), into shots/p2_view/pose_test/.

init 999 python:
    import builtins
    import os
    import pickle as zzv_pickle
    import subprocess as zzv_subprocess
    import ast as zzv_ast
    import re as zzv_re
    import json as zzv_json

    ZZV = builtins.dict(phase=0, loads=0, ticks=0, stmt=None, press=None, rb=None, t0=0.0)
    ZZV_LOADABLE = builtins.list([renpy.loadable])
    ZZV_FOLK = ("yuji", "megumi", "nobara", "maki", "panda", "toge")

    ## Two test hotspots in the common room, clear of four people (9: motion).
    register_hotspot("zzv_spot_a", "dorm_common", 1500, 600, "look", lines=["A test spot."], label="Test A", front=True)
    register_hotspot("zzv_spot_b", "dorm_common", 1600, 800, "look", lines=["A test spot."], label="Test B", front=True)

    def zzv_loaded():
        ZZV["loads"] += 1

    config.after_load_callbacks.append(zzv_loaded)

    def zzv_sweep():
        """Drop this harness's scratch variables (_zz...) from the store, so
        nothing of the harness goes into a save."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz")]:
            delattr(store, k)

    def zzv_fixture():
        settle(mc_name="Tester", mc_surname="Harness", day=3, period="Noon", here="dorm_common")
        for f in ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access"):
            flag(f)
        store.done_events.add("st_roll_call")
        for w in ROSTER_ORDER:
            if w not in store.roster:
                store.roster.append(w)
        store.companion = None
        mission_cache_clear()
        toast_clear()

    def zzv_put(loc, who, per=None):
        """Put exactly these people in a room (everyone else on the ridge)."""
        if per:
            store.period = per
        store.here = loc
        store.schedule_overrides = {}
        for w in ROSTER_ORDER:
            if w in store.roster:
                pin(w, "gate" if loc == "ridge" else "ridge")
        for w in who:
            pin(w, loc)
        mission_cache_clear()

    def zzv_label():
        """(x, y, w, h) of the hover label as it was last drawn, or None when
        no label is up."""
        sc = renpy.get_screen("hover_label")
        out = []

        def each(d):
            if isinstance(d, renpy.display.layout.NearRect) and d.child is not None:
                size = getattr(d.child, "window_size", None)
                offs = getattr(d, "offsets", None)
                if size and offs:
                    out.append((int(offs[0][0]), int(offs[0][1]), int(size[0]), int(size[1])))

        if sc is not None:
            sc.visit_all(each)
        return out[0] if out else None

    def zzv_quiet():
        """Nothing that moves by the clock: the caption faded, the objective
        read, no toast."""
        ARRIVAL[0] = (store.day, store.period, store.here)
        ARRIVAL[1] = 0.0
        store.last_objective = objective_text() or ""
        OBJ_UNSEEN[0] = None
        renpy.hide_screen("objective_toast")
        toast_clear()

    def zzv_with(patches, fn):
        """Run fn() with store names replaced, then put them back."""
        old = builtins.dict((k, getattr(store, k)) for k in patches)
        for k, v in patches.items():
            setattr(store, k, v)
        try:
            return fn()
        finally:
            for k, v in old.items():
                setattr(store, k, v)

    def zzv_no(prefix):
        """A renpy.loadable that says no for paths starting with `prefix`."""
        def zzv_loadable(path, *args, **kwargs):
            if builtins.str(path).startswith(prefix):
                return False
            return ZZV_LOADABLE[0](path, *args, **kwargs)
        return zzv_loadable

    def zzv_wid(screen, wid):
        return renpy.get_displayable(screen, wid, base=True) or renpy.get_displayable(screen, wid)

    def zzv_tip(screen, wid):
        d = zzv_wid(screen, wid)
        try:
            return d._get_tooltip() if d is not None else None
        except Exception:
            return None

    def zzv_order(screen):
        """Every displayable of a shown screen, in the order visit_all meets
        them (siblings in draw order)."""
        out = []
        sc = renpy.get_screen(screen)
        if sc is not None:
            sc.visit_all(out.append)
        return out

    def zzv_index(order, d):
        for i, x in enumerate(order):
            if x is d:
                return i
        return -1

    def zzv_under(d):
        """The Text strings under a displayable."""
        out = []
        def each(x):
            if isinstance(x, renpy.text.text.Text):
                out.append(zz_text_string(x))
        if d is not None:
            d.visit_all(each)
        return out

    def zzv_focus_at(x, y):
        """Put the pointer at (x, y) the way a mouse move does; the id of
        the button that takes the focus, or None."""
        renpy.display.focus.mouse_handler(None, int(x), int(y), default=False)
        return getattr(renpy.display.focus.get_focused(), "id", None)

    def zzv_both_marks(who, loc):
        return (True, True)

    def zzv_master(tag):
        """The displayable showing under a tag on the master layer, or None."""
        try:
            return renpy.game.context().scene_lists.get_displayable_by_tag("master", tag)
        except Exception:
            return None

    def zzv_atl(d):
        """The ATL block a shown displayable's transform runs, or None."""
        for _i in range(6):
            if d is None:
                return None
            if isinstance(d, renpy.display.transform.ATLTransform):
                return d.atl
            d = getattr(d, "child", None)
        return None

    def zzv_dumps(obj):
        try:
            return len(zzv_pickle.dumps(obj, zzv_pickle.HIGHEST_PROTOCOL)) > 0
        except Exception as e:
            return False

    def zzv_run(args):
        """Run a tool with the system python3; (exit status, output)."""
        env = builtins.dict((k, v) for k, v in os.environ.items() if not k.startswith("PYTHON"))
        try:
            p = zzv_subprocess.run(["python3"] + builtins.list(args), stdout=zzv_subprocess.PIPE,
                                   stderr=zzv_subprocess.STDOUT, env=env, timeout=120)
            return p.returncode, p.stdout.decode("utf-8", "replace")
        except Exception as e:
            return -1, repr(e)

    ## install_pose.py's test pictures: a flat room; 40% repainted; 10%
    ## repainted; 10% repainted with every pixel of the frame off by 6.
    ZZV_POSE_PY = r'''
import sys, os
tools, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, tools)
from raster import Img
W, H = 1920, 1080
os.makedirs(out, exist_ok=True)
bg = Img(W, H)
bg.vgrad(0, 0, W, H, (150, 160, 170), (70, 60, 50))
bg.save(os.path.join(out, "room.png"))
def variant(name, rect, noise=0):
    im = Img(W, H)
    if noise:
        im.buf = bytearray(bytes(bg.buf).translate(bytes(min(255, v + noise) for v in range(256))))
    else:
        im.buf = bytearray(bg.buf)
    x, y, w, h = rect
    im.rect(x, y, x + w, y + h, (230, 40, 60))
    im.save(os.path.join(out, name))
variant("pose_zzroom__nobara_a_00001_.png", (0, 0, 960, 864))
variant("pose_zzroom__yuji_b_00002_.png", (600, 300, 480, 432))
variant("pose_zzroom__megumi__evening_a_00001_.png", (600, 300, 480, 432), noise=6)
'''

    ## The driver: an overlay that answers the screens and the say lines of
    ## sections 3 and 12 from a timer, one step at a time.
    def zzv_line():
        return getattr(store, "_last_say_what", None) if renpy.get_screen("say") else None

    def zzv_tags_now():
        return builtins.set(renpy.get_showing_tags("master"))

    def zzv_step():
        Z = ZZV
        if len(renpy.game.contexts) != 1:
            return None
        ## Section 3: press one button of the place view.
        if Z["press"]:
            if renpy.get_screen("sb_place"):
                w = zzv_wid("sb_place", Z["press"])
                Z["press"] = None
                return w.action() if w is not None else ("zzv_missing",)
            return None
        if not Z["phase"]:
            return None
        Z["ticks"] += 1
        if Z["ticks"] > 90:
            check(False, "the save test runs to its end", (Z["phase"], zzv_line(), builtins.sorted(zzv_tags_now())))
            finish()
        line = zzv_line()
        tags = zzv_tags_now()
        if Z["phase"] == 1:
            if line == "ZZV BEFORE":
                check("view_fg" not in tags and "yuji" not in tags, "before stage_person nothing of it is showing", builtins.sorted(tags))
                Z["phase"] = 2
                return True
        elif Z["phase"] == 2:
            if line == "ZZV ONE":
                d = zzv_master("yuji")
                check("yuji" in tags and "view_fg" in tags,
                      "after stage_person the sprite and the foreground are on the master layer (view_fg in zz_layer_tags)",
                      builtins.sorted(tags))
                check(zzv_atl(d) is view_enter_ease.atl, "the sprite is shown with the ATL transform view_enter_ease", d)
                check(VIEW_SPEAKING[0] == "yuji", "the say callback notes who is speaking", builtins.list(VIEW_SPEAKING))
                check(all(zzv_dumps(e.displayable) for e in renpy.game.context().scene_lists.layers["master"]),
                      "pickle.dumps of everything view_enter put on the master layer succeeds")
                shot("dialogue_eased", wait=0)
                Z["stmt"] = renpy.game.context().current
                try:
                    renpy.take_screenshot()
                    renpy.save("zzv_talk_1")
                    ok = True
                except Exception as e:
                    ok = False
                    note("save 1", repr(e))
                check(ok, "the save test (R10): renpy.save on the first line after stage_person succeeds, the eased sprite, "
                          "its blink and talk layers and the foreground up")
                Z["phase"] = 3
                if ok:
                    renpy.load("zzv_talk_1")
        elif Z["phase"] == 3:
            if line == "ZZV ONE":
                check(Z["loads"] == 1 and renpy.game.context().current == Z["stmt"] and "view_fg" in tags and "yuji" in tags,
                      "renpy.load comes back on that statement, with the sprite and the foreground",
                      (Z["loads"], renpy.game.context().current, Z["stmt"], builtins.sorted(tags)))
                Z["phase"] = 4
                Z["rb"] = None
                renpy.rollback(force=True, checkpoints=1)
        elif Z["phase"] == 4:
            if line == "ZZV BEFORE":
                Z["rb"] = builtins.sorted(tags)
                check("view_fg" not in tags and "yuji" not in tags,
                      "rolling back through stage_person leaves no foreground (and no sprite) behind", Z["rb"])
                Z["phase"] = 5
                return True
            elif line == "ZZV ONE":
                note("rollback", "renpy.rollback(checkpoints=1, force=True) from the harness did not pass stage_person; "
                                 "the line moves to the owner check at C and to p2_saves")
                Z["phase"] = 5
        elif Z["phase"] == 5:
            if line == "ZZV ONE":
                check("view_fg" in tags and "yuji" in tags, "playing forward again after the rollback puts them back", builtins.sorted(tags))
                try:
                    renpy.take_screenshot()
                    renpy.save("zzv_talk_2")
                    ok = True
                except Exception as e:
                    ok = False
                    note("save 2", repr(e))
                check(ok, "the save succeeds again after a rollback through stage_person")
                Z["phase"] = 6
                if ok:
                    renpy.load("zzv_talk_2")
        elif Z["phase"] == 6:
            if line == "ZZV ONE":
                check(Z["loads"] == 2 and renpy.game.context().current == Z["stmt"] and "view_fg" in tags,
                      "and loads back on that statement", (Z["loads"], renpy.game.context().current, builtins.sorted(tags)))
                Z["phase"] = 7
                return True
        elif Z["phase"] == 7:
            if line == "ZZV TWO":
                Z["phase"] = 0
                return True
        return None

    config.overlay_screens.append("zzv_probe")


screen zzv_probe():
    zorder 200
    if ZZV["phase"] or ZZV["press"]:
        timer 0.3 repeat True action Function(zzv_step)

## view_stage used from a screen that defines none of _stage, _xs, _zoom, _yoff.
screen zzv_bare(loc):
    use view_stage(loc)
    use view_fg(loc)

screen zzv_focus_one():
    add "megumi" at char_focus(300)


## A replay's body (section 11): what a memory's scene does first.
label zzv_replay:
    call stage_person("megumi")
    python:
        ZZV["replay"] = (bool(_in_replay), zzv_atl(zzv_master("megumi")) is pos_c.atl, "view_fg" in zz_layer_tags("master"),
                         here, view_fg_path(here) is not None)
    $ renpy.end_replay()


init 999 python:
    def zzv_room_is(m):
        """m (what a master tag shows) is graded_bg() for here and now: the
        tinted Transform itself, or the painted picture by its name."""
        g = graded_bg()
        for d in (m, getattr(m, "child", None)):
            if d is None:
                continue
            if d is g or getattr(d, "name", None) is g or (isinstance(g, str) and getattr(d, "name", None) == tuple(g.split())):
                return True
        return False

label zz_smoke:

    $ zzv_fixture()

    ## --- 1. the light after Wait ------------------------------------------------------------
    python:
        zzv_put("rooftop", ["megumi"], "Afternoon")
        scene_light = light_for_place("rooftop", "Afternoon")
        _zz_before = scene_light
        autoplay(True)
    call sb_do_wait
    python:
        autoplay(False)
        check(period == "Evening" and scene_light == _zz_before and scene_light != light_for_place(here, period),
              "fixture: sb_do_wait has no scene statement, so the light is the last hour's until the hook runs",
              (period, scene_light))
        _zz_r = view_sync_light()
        check(_zz_r is None and scene_light == light_for_place(here, period),
              "after sb_do_wait, scene_light == light_for_place(here, period) when the place view opens (view_sync_light)",
              (scene_light, light_for_place(here, period)))
        _zz_src = open(os.path.join(config.gamedir, "sb_loop.rpy"), encoding="utf-8").read()
        check(0 <= _zz_src.find("\n        $ view_sync_light()\n") < _zz_src.find("\n        call screen sb_place\n"),
              "the loop calls view_sync_light() before call screen sb_place")
        ## Integration: the master layer is the room at THIS hour when the person
        ## view's dissolve starts (the place view is already hidden by then).
        _zz_m = zzv_master("view_room") or zzv_master("bg")
        check(_zz_m is not None and zzv_room_is(_zz_m)
              and zz_layer_tags("master") <= {"view_room", "bg"} and len(zz_layer_tags("master")) == 1,
              "after sb_do_wait, the master layer holds graded_bg() for the new hour, and nothing else, once view_sync_light has run",
              (_zz_m, graded_bg(), zz_layer_tags("master")))
        renpy.game.interface.transition.clear()
        VIEW_FROM_PERSON[0] = False
        view_sync_light()
        _zz_t0 = renpy.game.interface.transition.get(None)
        view_before_person("megumi")
        _zz_m2 = zzv_master("view_room") or zzv_master("bg")
        renpy.game.interface.transition.clear()
        view_sync_light()
        _zz_t1 = renpy.game.interface.transition.get(None)
        renpy.game.interface.transition.clear()
        view_sync_light()
        _zz_t2 = renpy.game.interface.transition.get(None)
        check(zzv_room_is(_zz_m2), "and it is still that picture when view_before_person queues its dissolve", (_zz_m2, _zz_m))
        check(_zz_t0 is None and _zz_t1 is not None and _zz_t2 is None and VIEW_FROM_PERSON[0] is False,
              "leaving the person view eases back: the place view's next opening queues a dissolve, once (Back returns with no scene)",
              (_zz_t0, _zz_t1, _zz_t2))
        view_before_person("megumi")
        renpy.game.interface.transition.clear()
        config.skipping = "fast"
        view_sync_light()
        config.skipping = None
        check(renpy.game.interface.transition.get(None) is None and VIEW_FROM_PERSON[0] is False, "but not while skipping")
        zzv_put("rooftop", ["megumi"], "Night")
        view_sync_light()
        _zz_m = zzv_master("view_room") or zzv_master("bg")
        check(_zz_m is not None and zzv_room_is(_zz_m),
              "a painted picture for the hour or a tinted one: either is shown as scene expression graded_bg() shows it",
              (_zz_m, graded_bg()))
        check(zzv_dumps(_zz_m), "and what it shows pickles")
        _zz_tint = [(l, p) for l in LOCATIONS for p in PERIODS if not isinstance(graded_bg(l, p), str)]
        if _zz_tint:
            zzv_put(_zz_tint[0][0], [], _zz_tint[0][1])
            view_sync_light()
            _zz_m = zzv_master("view_room")
            check(zzv_room_is(_zz_m) and zz_layer_tags("master") == {"view_room"} and zzv_dumps(_zz_m),
                  "a tinted room (%s, %s) goes up under the tag view_room, and pickles" % _zz_tint[0], (_zz_m, zz_layer_tags("master")))
        else:
            check(False, "fixture: no tinted room to test")
        renpy.game.interface.transition.clear()
        period = "Evening"
        here = "nowhere_at_all"
        _zz_tags = zz_layer_tags("master")
        check(view_sync_light() is None and zz_layer_tags("master") == _zz_tags, "view_sync_light does nothing outside the campus")
        here = "dorm_common"

    ## --- 2. slots ------------------------------------------------------------------------------
    python:
        _zz_bad = []
        for _zz_loc in LOCATIONS:
            for _zz_n in (1, 2, 3, 4):
                _zz_s = view_slots(_zz_loc, _zz_n)
                if not (isinstance(_zz_s, builtins.list) and len(_zz_s) == _zz_n
                        and all(isinstance(t, builtins.tuple) and len(t) == 4 and isinstance(t[3], int) for t in _zz_s)):
                    _zz_bad.append((_zz_loc, _zz_n, _zz_s))
                elif any(r[0] < 0 or r[0] + r[2] > 1700 for r in view_slot_rects(_zz_loc, _zz_n)):
                    _zz_bad.append((_zz_loc, _zz_n, "leaves the stage"))
        check(not _zz_bad, "view_slots(loc, n) returns n 4-tuples for every room (%d, read from LOCATIONS) and n from 1 to 4, "
                           "left of x 1700" % len(LOCATIONS), _zz_bad)
        check(view_slots("dorm_common", 0) == [] and view_slots("dorm_common", 5) == [], "and [] for 0 or 5 people")
        ## 4.4 keeps the stage inside x 40 to 1700. view_validate holds VIEW_SLOTS
        ## to that; a room with no row keeps its phase-1 centres, and these start
        ## left of x 40 (each wants a VIEW_SLOTS row or a sidecar, if it matters).
        _zz_left = ["%s/%d: x %d" % (l, n, min(r[0] for r in view_slot_rects(l, n)))
                    for l in LOCATIONS for n in (1, 2, 3, 4) if min(r[0] for r in view_slot_rects(l, n)) < 40]
        note("slots left of x 40 (phase-1 defaults, rooms with no VIEW_SLOTS row)", ", ".join(_zz_left) or "none")
        check(not [t for t in _zz_left if t.split("/")[0] in VIEW_SLOTS], "no room with a VIEW_SLOTS row starts left of x 40", _zz_left)
        _zz_bad = []
        for _zz_loc in ("dorm_common", "cafeteria", "dorm", "gate"):
            for _zz_n in (1, 2, 3, 4):
                zzv_put(_zz_loc, ZZV_FOLK[:_zz_n], "Noon")
                _zz_on = stage_people(_zz_loc)[0]
                _zz_xs = [stage_x(w, _zz_loc) for w in _zz_on]
                _zz_rows = view_stage_rows(_zz_loc)
                if len(_zz_on) != _zz_n or _zz_xs != [r["x"] for r in _zz_rows]:
                    _zz_bad.append((_zz_loc, _zz_n, _zz_xs))
                elif not any(r["pose"] for r in _zz_rows) and _zz_xs != [s[0] for s in view_slots(_zz_loc, _zz_n)]:
                    _zz_bad.append((_zz_loc, _zz_n, _zz_xs, "slots"))
        check(not _zz_bad and stage_x("sana", "dorm_common") == 700,
              "stage_x is each row's own x: view_slots while nobody is a painted pose (and 700 off the stage)", _zz_bad)
        ## P8: someone painted into the room answers with the pose's centre.
        zzv_put("dorm_common", ["yuji", "megumi", "nobara", "panda"], "Evening")
        _zz_rows = view_stage_rows("dorm_common")
        _zz_posed = [r for r in _zz_rows if r["pose"]]
        check(all(stage_x(r["who"], "dorm_common") == r["x"] for r in _zz_rows)
              and all(stage_x(r["who"], "dorm_common") == int(r["rect"][0] + r["rect"][2] / 2) for r in _zz_posed),
              "stage_x with a painted pose on stage (%d posed): the pose's centre, and every row's own x" % len(_zz_posed),
              [(r["who"], r["x"], stage_x(r["who"], "dorm_common")) for r in _zz_rows])
        del _zz_rows, _zz_posed
        check(set(VIEW_SLOTS) == {"dorm_common", "cafeteria", "classroom", "courtyard", "training", "infirmary",
                                  "library", "utahime_office"} and view_validate() == [],
              "VIEW_SLOTS has rows for the eight rooms, and they validate", (sorted(VIEW_SLOTS), view_validate()))
        _zz_d = view_slots("dorm", 3)
        _zz_z = PLACE_STAGING["dorm"]["zoom"]
        check([s[3] for s in _zz_d] == [0, 1, 0] and _zz_d[1][1] == _zz_d[0][1] - 10 and abs(_zz_d[1][2] - _zz_z * 0.96) < 1e-6
              and [s[0] for s in _zz_d] == STAGE_CENTRES[3] and _zz_d[0][2] == _zz_z,
              "a room with no row: the phase-1 centres, the middle person 4% smaller, 10 px higher, far 1", _zz_d)
        check([s[3] for s in view_slots("dorm", 4)] == [0, 1, 1, 0] and [s[3] for s in view_slots("dorm", 2)] == [0, 0],
              "with four the two in the middle step back; with two nobody does")
        RULE_LAYOUT["view_library"] = {"slots": {"1": [[900, -44, 0.5, 2]], "2": [[1, 2, 3]], "3": "nonsense"}}
        check(view_slots("library", 1) == [(900, -44, 0.5, 2)], "a sidecar's slots win over VIEW_SLOTS", view_slots("library", 1))
        check(view_slots("library", 2) == VIEW_SLOTS["library"][2] and view_slots("library", 3) == VIEW_SLOTS["library"][3],
              "a sidecar row of the wrong length or shape is ignored", (view_slots("library", 2), view_slots("library", 3)))
        del RULE_LAYOUT["view_library"]
        check(view_slot_rects("dorm_common", 2) == [view_slot_rect(s) for s in view_slots("dorm_common", 2)]
              and all(isinstance(v, int) for r in view_slot_rects("dorm_common", 4) for v in r),
              "view_slot_rects(loc, n) keeps its signature: n int rectangles from view_slots")

    ## --- 3. poses -------------------------------------------------------------------------------
    python:
        zzv_put("dorm_common", ["megumi", "nobara", "maki"], "Noon")
        zzv_quiet()
        _zz_file = "images/place/pose_dorm_common__nobara__evening.png"
        check(renpy.loadable(_zz_file) and renpy.loadable("images/place/pose_dorm_common__yuji.png")
              and rule_layout("view_dorm_common").get("poses", {}).get("nobara__evening") == [270, 410, 400, 460],
              "fixture: the overlay's two pose pictures and their sidecar boxes are in the scratch game")
        check(view_pose("megumi", "dorm_common") is None and view_pose("megumi", "cafeteria", "Noon") is None,
              "with no pose file view_pose is None")
        check(view_pose("nobara", "dorm_common") is None and view_pose("nobara", "dorm_common", "Noon") is None,
              "at Noon (no day file) Nobara has no pose")
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_w = zzv_wid("sb_place", "stage_nobara")
        _zz_m = zzv_wid("sb_place", "stage_megumi")
        check(isinstance(_zz_w, renpy.display.behavior.ImageButton) and isinstance(_zz_m, renpy.display.behavior.ImageButton),
              "and the stage draws the sprite (at Noon; and for someone with no pose file)", (_zz_w, _zz_m))
        _zz_rects = view_person_rects(here)
        check(_zz_rects == view_slot_rects(here, 3) and len(_zz_rects) == len(stage_people(here)[0]) == 3,
              "view_person_rects(loc) returns one rectangle per person on stage (the slots' rectangles)", _zz_rects)
        shot("common_room_three", wait=0.3)
    hide screen sb_place
    python:
        zzv_put("dorm_common", ["megumi", "nobara", "maki"], "Evening")
        zzv_quiet()
        _zz_p = view_pose("nobara", "dorm_common")
        check(_zz_p == dict(image=_zz_file, box=(270, 410, 400, 460)) and isinstance(_zz_p["image"], str)
              and all(isinstance(v, int) for v in _zz_p["box"]) and isinstance(_zz_p["box"], builtins.tuple),
              "at Evening view_pose is dict(image, box): the variant's file (a str) and the sidecar's box (ints)", _zz_p)
        check(zzv_dumps(_zz_p) and zzv_pickle.loads(zzv_pickle.dumps(_zz_p)) == _zz_p, "view_pose's dict pickles")
        check(view_pose("yuji", "dorm_common") is None and view_pose("yuji", "dorm_common", "Noon") is not None,
              "a day file alone is not used at Evening (it is at Noon)", view_pose("yuji", "dorm_common", "Noon"))
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_w = zzv_wid("sb_place", "stage_nobara")
        check(isinstance(_zz_w, renpy.display.behavior.Button) and not isinstance(_zz_w, renpy.display.behavior.ImageButton)
              and zz_rect("sb_place", "stage_nobara") == (270, 410, 400, 460),
              "at Evening the stage draws a patch at the box", (_zz_w, zz_rect("sb_place", "stage_nobara")))
        check(isinstance(zzv_wid("sb_place", "stage_megumi"), renpy.display.behavior.ImageButton),
              "while the others in the room keep their sprites")
        _zz_rects = view_person_rects(here)
        _zz_on = stage_people(here)[0]
        check(len(_zz_rects) == len(_zz_on) == 3 and _zz_rects[_zz_on.index("nobara")] == (270, 410, 400, 460),
              "view_person_rects gives the pose's box when a pose is drawn", _zz_rects)
        _zz_body = [(r[0] + 0.2 * r[2], r[1], 0.6 * r[2], r[3]) for w, r in zip(_zz_on, _zz_rects) if w != "nobara"]
        check(len(_zz_body) == 2 and not any(hot_overlap(b, (270, 410, 400, 460)) for b in _zz_body),
              "the people who stand take slots clear of the pose's box (nobody stands in front of the sofa)", _zz_rects)
        _zz_tr = [zz_rect("sb_place", "tag_" + w) for w in _zz_on]
        check(all(_zz_tr) and not any(hot_overlap(a, b) for a in _zz_tr for b in _zz_tr if a is not b),
              "and no two name tags touch", _zz_tr)
        check(view_tip("nobara", here) == zzv_tip("sb_place", "stage_nobara")[0], "the patch carries the same hover label")
        shot("common_room_pose", wait=0.3)
    hide screen sb_place
    python:
        ## Four in the room, one of them the pose: the three who stand.
        zzv_put("dorm_common", ["yuji", "megumi", "nobara", "maki"], "Evening")
        zzv_quiet()
        _zz_rows = view_stage_rows(here)
        _zz_cost = [(r["who"], view_pose_cost((r["x"], r["yoff"], r["zoom"], r["far"]), [(270, 410, 400, 460)]))
                    for r in _zz_rows if not r["pose"]]
        _zz_xs = sorted(r["x"] for r in _zz_rows if not r["pose"])
        note("four in the common room, Nobara the pose: each standing body's overlap with her box, in square px", _zz_cost)
        check(len(_zz_cost) == 3 and not any(c for _w, c in _zz_cost) and all(b - a >= 170 for a, b in zip(_zz_xs, _zz_xs[1:])),
              "with four people the three who stand are still clear of the pose's box (slots drawn from all the "
              "room's layouts, 170 px apart)", (_zz_cost, _zz_xs))
        check(view_pick_slots("dorm_common", 2, [(270, 410, 400, 460)]) == [VIEW_SLOTS["dorm_common"][3][1], VIEW_SLOTS["dorm_common"][3][2]],
              "while a layout with a clear set is used as it is (three people: the layout for three, less its left slot)",
              view_pick_slots("dorm_common", 2, [(270, 410, 400, 460)]))
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_tr = [zz_rect("sb_place", "tag_" + r["who"]) for r in _zz_rows]
        check(all(_zz_tr) and not any(hot_overlap(a, b) for a in _zz_tr for b in _zz_tr if a is not b),
              "and their four name tags do not touch", _zz_tr)
        shot("common_room_pose_four", wait=0.3)
    hide screen sb_place
    $ ZZV["press"] = "stage_nobara"
    call screen sb_place
    python:
        check(_return == ("char", "nobara"), "pressing the patch returns ('char', 'nobara')", _return)
        ## No box in the sidecar: the whole picture, and only for someone alone.
        RULE_LAYOUT["view_dorm_common"] = {}
        check(view_pose("nobara", "dorm_common") is None, "with no box and others on stage there is no pose")
        zzv_put("dorm_common", ["nobara"], "Evening")
        check(view_pose("nobara", "dorm_common") == dict(image=_zz_file, box=(0, 0, 1920, 1080)),
              "with no box the whole picture is used, and only when that person is alone on the stage",
              view_pose("nobara", "dorm_common"))
        del RULE_LAYOUT["view_dorm_common"]
        companion = "nobara"
        check(view_stage_rows("dorm_common")[0]["pose"] is None, "whoever is tagging along never takes their pose")
        companion = None
        renpy.loadable = zzv_no("images/place/")
        check(view_pose("nobara", "dorm_common") is None, "the stand-in path: with the file gone, view_pose is None (the sprite)")
        renpy.loadable = ZZV_LOADABLE[0]

    ## --- 4. view_stage on its own ------------------------------------------------------------
    python:
        zzv_put("cafeteria", ["yuji", "toge", "megumi"], "Noon")
        zzv_quiet()
    show screen zzv_bare("cafeteria")
    python:
        zz_render(0.3)
        check(zz_buttons("zzv_bare") == 6 and all(zzv_wid("zzv_bare", "stage_" + w) is not None for w in ("yuji", "toge", "megumi")),
              "view_stage('cafeteria') used from a screen that defines none of _stage, _xs, _zoom, _yoff renders "
              "(it computes its own)", zz_buttons("zzv_bare"))
    hide screen zzv_bare

    ## --- 5. tools/install_pose.py ------------------------------------------------------------
    python:
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_tool = os.path.join(_zz_root or "", "tools", "install_pose.py")
        _zz_dir = os.path.join(zz_smoke_state.shots, "pose_test")
        _zz_out = os.path.join(_zz_dir, "root")
        if not (_zz_root and os.path.isfile(_zz_tool)):
            check(False, "install_pose.py is there to run", _zz_tool)
        else:
            import shutil as _zz_shutil
            if os.path.isdir(_zz_dir):
                _zz_shutil.rmtree(_zz_dir)
            os.makedirs(os.path.join(_zz_out, "game", "layout"))
            _zz_hot = os.path.join(_zz_out, "game", "layout", "hot_zzroom.json")
            with open(_zz_hot, "w") as _zz_f:
                _zz_f.write('{"spots": {"zz_thing": [640, 480]}}\n')
            del _zz_f
            _zz_hot_before = open(_zz_hot, "rb").read()
            _zz_rc, _zz_log = zzv_run(["-c", ZZV_POSE_PY, os.path.join(_zz_root, "tools"), _zz_dir])
            check(_zz_rc == 0 and os.path.isfile(os.path.join(_zz_dir, "room.png")), "fixture: the test pictures are drawn", _zz_log)
            _zz_side = os.path.join(_zz_out, "game", "layout", "view_zzroom.json")
            _zz_base = [_zz_tool, "--bg", os.path.join(_zz_dir, "room.png"), "--root", _zz_out]

            _zz_rc, _zz_log = zzv_run(_zz_base + [os.path.join(_zz_dir, "pose_zzroom__nobara_a_00001_.png")])
            check(_zz_rc != 0 and "REFUSED" in _zz_log and "40.0%" in _zz_log and not os.path.exists(_zz_side)
                  and not os.path.exists(os.path.join(_zz_out, "game", "images", "place", "pose_zzroom__nobara.png")),
                  "install_pose.py refuses a test picture with 40% changed, and installs nothing", _zz_log)

            _zz_rc, _zz_log = zzv_run(_zz_base + [os.path.join(_zz_dir, "pose_zzroom__yuji_b_00002_.png")])
            _zz_sc = zzv_json.load(open(_zz_side)) if os.path.exists(_zz_side) else {}
            check(_zz_rc == 0 and _zz_sc.get("poses", {}).get("yuji") == [576, 276, 528, 480]
                  and os.path.isfile(os.path.join(_zz_out, "game", "images", "place", "pose_zzroom__yuji.png"))
                  and os.path.isfile(os.path.join(_zz_out, "shots", "art", "pose_zzroom__yuji.png")),
                  "and accepts one with 10%, writing the box (the patch grown by 24 px) to view_<place>.json, the preview "
                  "and the picture", (_zz_log, _zz_sc))

            _zz_rc, _zz_log = zzv_run(_zz_base + [os.path.join(_zz_dir, "pose_zzroom__megumi__evening_a_00001_.png")])
            _zz_sc = zzv_json.load(open(_zz_side)) if os.path.exists(_zz_side) else {}
            check(_zz_rc == 0 and _zz_sc.get("poses", {}).get("megumi__evening") == [576, 276, 528, 480]
                  and _zz_sc.get("poses", {}).get("yuji") == [576, 276, 528, 480] and "10.0%" in _zz_log,
                  "faint noise over the whole frame (every pixel off by 6) and one real 10% patch: accepted, the box "
                  "around the patch only, the other pose's box kept", (_zz_log, _zz_sc))

            _zz_rc, _zz_log = zzv_run(_zz_base + [os.path.join(_zz_dir, "pose_zzroom__yuji_b_00002_.png"), "--box", "400,300,500,700"])
            _zz_sc = zzv_json.load(open(_zz_side)) if os.path.exists(_zz_side) else {}
            check(_zz_rc == 0 and _zz_sc.get("poses", {}).get("yuji") == [400, 300, 500, 700],
                  "--box 400,300,500,700 writes that box", (_zz_log, _zz_sc))
            check(open(_zz_hot, "rb").read() == _zz_hot_before and sorted(os.listdir(os.path.join(_zz_out, "game", "layout")))
                  == ["hot_zzroom.json", "view_zzroom.json"],
                  "an existing hot_<place>.json beside it is byte-identical afterwards")
            check(builtins.set(_zz_sc) == {"poses"}, "the sidecar holds only what layout_sheet.py allows (slots, poses)", sorted(_zz_sc))

    ## --- 6. the pose plan against the schedule; the foreground polygons ----------------
    python:
        _zz_src = open(os.path.join(_zz_root, "tools", "make_pose_workflow.py"), encoding="utf-8").read()
        _zz_m = zzv_re.search(r"# POSES-BEGIN\nPOSES = (\[.*?\n\])\n# POSES-END", _zz_src, zzv_re.S)
        _zz_plan = zzv_ast.literal_eval(_zz_m.group(1)) if _zz_m else []
        _zz_bad = []
        for _zz_row in _zz_plan:
            _zz_w, _zz_l, _zz_v = _zz_row["who"], _zz_row["place"], _zz_row["variant"]
            if _zz_w not in CAST or _zz_l not in LOCATIONS:
                _zz_bad.append((_zz_w, _zz_l, "unknown"))
                continue
            if not renpy.has_image(tuple((LOCATIONS[_zz_l]["bg"] + (" " + _zz_v if _zz_v else "")).split()), exact=True):
                _zz_bad.append((_zz_w, _zz_l, "no picture for " + (_zz_v or "day")))
            if _zz_row.get("via"):
                continue
            _zz_pers = [p for p in PERIODS if _zz_l in (routine_location(_zz_w, p), routine_location(_zz_w, p, weekend=True))]
            if _zz_w == "gojo" and _zz_l == "gojo_office":
                _zz_pers = builtins.list(GOJO_IN_PERIODS) if when_at(_zz_w, _zz_l) else []
            if not when_at(_zz_w, _zz_l) or not any((bg_variant(_zz_l, p) or "") == _zz_v for p in _zz_pers):
                _zz_bad.append((_zz_w, _zz_l, _zz_v, when_at(_zz_w, _zz_l), _zz_pers))
        check(len(_zz_plan) == 14 and not _zz_bad,
              "the pose plan (tools/make_pose_workflow.py, 14 rows): the schedule puts every person at their place "
              "(when_at), at an hour with the picture the pose is painted on", _zz_bad)
        check([r.get("via") for r in _zz_plan if r.get("via")] == ["night_gojo"] and NIGHT_GOJO["place"] == "ridge",
              "the one row the routine never produces is the Gojo night's (he is pinned on the ridge)")
        check(not when_at("nobara", "rooftop") and not when_at("megumi", "riverside"),
              "the storyboard's two extras stay out: the schedule never puts Nobara on the rooftop or Megumi at the riverside")
        note("the pose plan", "re-run on the merged tree: P9 moves a few schedule slots into the hubs (D57)")
        _zz_fgdir = os.path.join(_zz_root, "tools", "fg")
        _zz_want = []
        for _zz_fn in sorted(os.listdir(_zz_fgdir)):
            if _zz_fn.endswith(".json"):
                for _zz_v in zzv_json.load(open(os.path.join(_zz_fgdir, _zz_fn))):
                    _zz_want.append("images/fg/fg_%s%s.png" % (_zz_fn[:-5], "_" + _zz_v if _zz_v else ""))
        check(sorted(_zz_want) == ["images/fg/fg_cafeteria.png", "images/fg/fg_dorm_common.png",
                                   "images/fg/fg_dorm_common_evening.png", "images/fg/fg_dorm_common_night.png",
                                   "images/fg/fg_utahime_office.png"]
              and all(renpy.loadable(p) for p in _zz_want),
              "the five foreground files load, one for every polygon in tools/fg/ (the classroom has none: round 1)", _zz_want)
        check(sorted(VIEW_FG_ROOMS) == sorted(builtins.set(os.path.splitext(f)[0] for f in os.listdir(_zz_fgdir) if f.endswith(".json"))),
              "VIEW_FG_ROOMS names the rooms that have a polygon file", VIEW_FG_ROOMS)

    ## --- 7. the foreground on the place view ----------------------------------------------
    python:
        check(view_fg_path("dorm_common", "Noon") == "images/fg/fg_dorm_common.png"
              and view_fg_path("dorm_common", "Evening") == "images/fg/fg_dorm_common_evening.png"
              and view_fg_path("dorm_common", "Night") == "images/fg/fg_dorm_common_night.png"
              and view_fg_path("cafeteria", "Night") == "images/fg/fg_cafeteria.png"
              and view_fg_path("dorm", "Night") is None and view_fg_path("riverside", "Noon") is None,
              "view_fg picks the variant's file for the hour, the day file where the room has one picture, none elsewhere")
        zzv_put("dorm_common", ["megumi", "nobara", "maki"], "Noon")
        zzv_quiet()
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_o = zzv_order("sb_place")
        _zz_fg = [i for i, d in enumerate(_zz_o) if builtins.str(getattr(d, "filename", "")).startswith("images/fg/")]
        _zz_st = [zzv_index(_zz_o, zzv_wid("sb_place", "stage_" + w)) for w in stage_people(here)[0]]
        _zz_tg = [zzv_index(_zz_o, zzv_wid("sb_place", "tag_" + w)) for w in stage_people(here)[0]]
        check(len(_zz_fg) == 1 and min(_zz_st) >= 0 and max(_zz_st) < _zz_fg[0] < min(_zz_tg),
              "view_fg draws above the stage and below the name tags", (_zz_st, _zz_fg, _zz_tg))
        _zz_far = [r for r in view_stage_rows(here) if r["far"]]
        check(len(_zz_far) == 1 and _zz_st[[r["who"] for r in view_stage_rows(here)].index(_zz_far[0]["who"])] == min(_zz_st),
              "the person a step back is drawn first, behind the others",
              (_zz_far, _zz_st, [r["who"] for r in view_draw_order(view_stage_rows(here))], stage_people(here)[0]))
        renpy.loadable = zzv_no("images/fg/")
    hide screen sb_place
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_o = zzv_order("sb_place")
        check(view_fg_path(here) is None and not [d for d in _zz_o if builtins.str(getattr(d, "filename", "")).startswith("images/fg/")]
              and all(zzv_wid("sb_place", "tag_" + w) is not None for w in stage_people(here)[0]),
              "the stand-in path: with no foreground file the screen draws none, and the tags are still there")
        check(all(view_slots(l, n) == view_default_slots(l, n) and not any(s[1] < -60 for s in view_slots(l, n))
                  for l in VIEW_FG_ROOMS for n in (1, 2, 3, 4))
              and view_slots("library", 3) == VIEW_SLOTS["library"][3]
              and view_person_rects(here) == [view_slot_rect(s) for s in view_default_slots(here, 3)],
              "and nobody stands up on the table: a foreground room uses the plain default slots while its picture is "
              "missing (other rooms keep their rows)", [view_slots(l, 3) for l in VIEW_FG_ROOMS])
        shot("standin_no_foreground", wait=0.2)
        renpy.loadable = ZZV_LOADABLE[0]
        check(view_slots("dorm_common", 3) == VIEW_SLOTS["dorm_common"][3], "with the file back the room's own slots return")
    hide screen sb_place

    ## Integration: the classroom. Nobody's legs among the near desks (they
    ## reach the feet's line from x 950 on), with the pictures to look at.
    python:
        check(all(r[0] + 60 <= 960 and r[3] == 0 for n in (1, 2, 3, 4) for r in view_slots("classroom", n)),
              "the classroom's slots keep everyone on the clear floor left of the near desks (x 950), nobody a step back",
              [view_slots("classroom", n) for n in (1, 2, 3, 4)])
        for _zz_n in (2, 3, 4):
            zzv_put("classroom", ["megumi", "nobara", "yuji", "maki"][:_zz_n], "Morning")
            zzv_quiet()
            renpy.scene()
            renpy.show("zzv_bg", what=graded_bg())
            renpy.show_screen("sb_place")
            shot("classroom_%d" % _zz_n, wait=0.3)
            renpy.hide_screen("sb_place")
        renpy.scene()

    ## --- 8. lit_sprite: blink and talk -------------------------------------------------------
    python:
        _zz_args = ((760, 1400), (380, 1365, 300))
        _zz_n = lit_sprite("images/char/yuji_neutral.png", *_zz_args)
        _zz_h = lit_sprite("images/char/yuji_happy.png", *_zz_args)
        _zz_o = lit_sprite("images/char/megumi_neutral.png", *_zz_args)
        check(renpy.loadable("images/char/fx/fx_yuji_blink.png") and renpy.loadable("images/char/fx/fx_yuji_talk.png")
              and len(_zz_n.child.children) == 4 and len(_zz_h.child.children) == 3 and len(_zz_o.child.children) == 2,
              "with the overlay's fx_yuji_blink.png / fx_yuji_talk.png, lit_sprite adds the two layers on a compatible "
              "expression (neutral), only the blink on Yuji's happy face (VIEW_BLINK_ALSO: integration), and none for "
              "someone with no files", (len(_zz_n.child.children), len(_zz_h.child.children), len(_zz_o.child.children)))
        _zz_a = lit_sprite("images/char/yuji_angry.png", *_zz_args)
        _zz_also = zzv_with(dict(VIEW_BLINK_ALSO={}), lambda: lit_sprite("images/char/yuji_happy.png", *_zz_args))
        check(len(_zz_a.child.children) == 2 and len(_zz_also.child.children) == 2
              and tuple(_zz_h.child.children[2].state.crop) == VIEW_FACE["yuji"]["eyes"]
              and "happy" in VIEW_BLINK_ALSO["yuji"] and "angry" not in VIEW_BLINK_ALSO["yuji"] and VIEW_TALK_OK == ("neutral",)
              and zzv_dumps(_zz_h),
              "the happy layer is the eye box (the face Yuji greets with), it pickles; an expression outside his row "
              "(angry: the brows cross the box) gets none, and without the row happy gets none (the plan's line)")
        _zz_l = _zz_n.child.children[2:]
        check([tuple(d.state.crop) for d in _zz_l] == [VIEW_FACE["yuji"]["eyes"], VIEW_FACE["yuji"]["mouth"]]
              and [(d.state.xpos, d.state.ypos) for d in _zz_l] == [VIEW_FACE["yuji"]["eyes"][:2], VIEW_FACE["yuji"]["mouth"][:2]],
              "the layers are the eye box and the mouth box, each where it sits on the canvas")
        renpy.loadable = zzv_no("images/char/fx/")
        _zz_plain = lit_sprite("images/char/yuji_neutral.png", *_zz_args)
        renpy.loadable = ZZV_LOADABLE[0]
        check(len(_zz_plain.child.children) == 2 and isinstance(_zz_plain.child, renpy.display.layout.MultiBox)
              and _zz_plain.function is _zz_o.function,
              "without the files the structure is today's: the shadow and the picture under the light")
        check(len(renpy.display.image.images[("yuji", "neutral")].child.children) == 4
              and len(renpy.display.image.images[("megumi", "neutral")].child.children) == 2,
              "the game's own image yuji neutral carries the layers (jjk_sprites.rpy is not edited)")
        check(all(zzv_dumps(d) for d in (_zz_n, _zz_h, _zz_o, _zz_plain)),
              "pickle.dumps of every displayable lit_sprite returns succeeds, blink and talk layers included")
        check(sorted(VIEW_FACE) == sorted(["yuji", "megumi", "nobara", "maki", "panda", "toge", "gojo", "utahime", "shoko",
                                           "yaga", "ijichi"])
              and "eyes" not in VIEW_FACE["gojo"] and "eyes" not in VIEW_FACE["yaga"]
              and all("mouth" in f for f in VIEW_FACE.values()),
              "VIEW_FACE has the eleven on campus; Gojo and Yaga get talk only")
        _zz_t = Transform()
        VIEW_SPEAKING[:] = ["yuji", time.time() + 5.0]
        _zz_seen = set()
        for _zz_k in range(12):
            view_talk_fn(_zz_t, 0.0, 0.0, who="yuji")
            _zz_seen.add(_zz_t.alpha)
            time.sleep(0.03)
        check(_zz_seen == {0.0, 1.0} and view_talk_fn(_zz_t, 0, 0, who="yuji") == VIEW_TICK,
              "view_talk_fn opens and shuts the mouth while that person is speaking, and asks for VIEW_TICK", _zz_seen)
        view_talk_fn(_zz_t, 0.0, 0.0, who="megumi")
        _zz_other = _zz_t.alpha
        VIEW_SPEAKING[:] = [None, 0.0]
        view_talk_fn(_zz_t, 0.0, 0.0, who="yuji")
        check(_zz_other == 0.0 and _zz_t.alpha == 0.0, "and keeps it shut for everyone else, and when nobody speaks")
        check(view_blink_fn(_zz_t, 0, 0, who="yuji") == VIEW_TICK and _zz_t.alpha in (0.0, 1.0), "view_blink_fn asks for VIEW_TICK")

    ## --- 9. motion ---------------------------------------------------------------------------------
    python:
        zzv_put("dorm_common", ["megumi", "nobara", "maki", "panda"], "Noon")
        zzv_quiet()
        persistent.motion = True
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.8)       # any transition has ended
        _zz_hot = [h["id"] for h in hot_spots_for(here)]
        check(len(stage_people(here)[0]) == 4 and len([h for h in _zz_hot if h.startswith("zzv_spot_")]) == 2,
              "fixture: the common room with four people and two hotspots", (stage_people(here), _zz_hot))
        _zz_c = zz_calls("view_breathe_fn", 3)
        check(0 < _zz_c <= 4 * 22 * 3, "motion: zz_calls('view_breathe_fn', 3) is at most 4 x 22 x 3 (%d)" % _zz_c, _zz_c)
        persistent.motion = False
    hide screen sb_place
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_c0 = zz_calls("view_breathe_fn", 1.5)
        check(_zz_c0 == 0, "and 0 with persistent.motion off", _zz_c0)
        _zz_t = Transform()
        _zz_r = [view_breathe_fn(_zz_t, 0, 0, phase=0.3), view_blink_fn(_zz_t, 0, 0, who="yuji"), view_talk_fn(_zz_t, 0, 0, who="yuji")]
        check(_zz_r == [None, None, None] and _zz_t.yzoom == 1.0 and _zz_t.alpha == 0.0,
              "with motion off the three functions return None: no breath, eyes open, mouth shut", _zz_r)
        _zz_off = view_sprite("megumi", "neutral", 0.43, 1)
        persistent.motion = True
        _zz_r = [view_breathe_fn(_zz_t, 0, 0, phase=0.3), view_blink_fn(_zz_t, 0, 0, who="yuji"), view_talk_fn(_zz_t, 0, 0, who="yuji")]
        check(_zz_r == [VIEW_TICK] * 3 and 1.0 <= _zz_t.yzoom <= 1.006 and not _zz_t.blur,
              "with it on they return VIEW_TICK (0.05), yzoom stays within 1.0 to 1.006, and none sets blur", (_zz_r, _zz_t.yzoom, _zz_t.blur))
        _zz_on = view_sprite("megumi", "neutral", 0.43, 1)
        check(_zz_on.function is not None and not _zz_on.blur and _zz_on.child.function is None
              and abs(_zz_on.child.blur - 0.8) < 1e-6 and _zz_off.function is None and abs(_zz_off.blur - 0.8) < 1e-6
              and not view_sprite("megumi", "neutral", 0.52, 0).child.blur,
              "the depth blur (0.8 a step) is a fixed property under the breathing transform, never inside one")
        check(view_phase("yuji") != view_phase("megumi") and 0 <= view_phase("nobara") < 1, "each person breathes on their own phase")
    hide screen sb_place

    ## --- 10. name tags, the budget, hover labels ---------------------------------------------
    python:
        zzv_put("cafeteria", ["yuji", "toge", "megumi"], "Noon")
        zzv_quiet()
        _zz_words_were = gui.icon_words
        gui.icon_words = "never"
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_on = stage_people(here)[0]
        _zz_all = zz_words("sb_place")
        _zz_rest = builtins.list(_zz_all)
        for _zz_tok in [t for t in hud_date().split() if zz_is_word(t)] + ["Review", "tools"]:
            if _zz_tok in _zz_rest:
                _zz_rest.remove(_zz_tok)
        check(len(_zz_rest) <= 2 * len(_zz_on) and builtins.set(_zz_rest) <= builtins.set([CAST[w]["short"] for w in _zz_on] + ["NEW"])
              and all(CAST[w]["short"] in _zz_rest for w in _zz_on),
              "zz_words('sb_place') <= 2 per person on stage (P2's icon column is merged; the date chip and Review tools "
              "are not counted): %d words for %d people" % (len(_zz_rest), len(_zz_on)), _zz_all)
        _zz_texts = zz_texts("sb_place")
        check(not any(ambient_of(w, here)[0] in s for w in _zz_on for s in _zz_texts),
              "the caption is no longer printed under the name", _zz_texts)
        _zz_tr = [zz_rect("sb_place", "tag_" + w) for w in _zz_on]
        _zz_xs = [s[0] for s in view_slots(here, 3)]
        check(all(_zz_tr) and all(r[1] == 1036 and r[3] == 36 for r in _zz_tr)
              and all(abs(r[0] + r[2] / 2.0 - x) <= 2 for r, x in zip(_zz_tr, _zz_xs)),
              "a 36-high tag for each person at ypos 1036, centred under them", _zz_tr)
        _zz_dev = zz_rect("sb_place", "hud_dev")
        check(_zz_dev is None or not any(hot_overlap(r, _zz_dev) for r in _zz_tr), "no tag runs over Review tools", (_zz_dev, _zz_tr))
        _zz_keys = [zzv_tip("sb_place", p + w) for w in _zz_on for p in ("stage_", "tag_")]
        check(all(isinstance(t, tuple) and len(t) == 2 for t in _zz_keys) and len(set(t[1] for t in _zz_keys)) == 6
              and all(zzv_tip("sb_place", "stage_" + w) == (rail_tip(CAST[w]["short"], ambient_of(w, here)[0]), "stage_" + w)
                      and zzv_tip("sb_place", "tag_" + w)[0] == zzv_tip("sb_place", "stage_" + w)[0] for w in _zz_on),
              "the sprite and the tag carry tuple tooltips (name, then the caption) with keys unique on sb_place", _zz_keys)
        check(all(getattr(zzv_wid("sb_place", p + w).action, "value", None) == ("char", w) for w in _zz_on for p in ("stage_", "tag_")),
              "both return ('char', who)")
        gui.icon_words = _zz_words_were
    hide screen sb_place
    python:
        ## The pointer on a sprite: a breathing transform over a (blurred) transform
        ## under focus_mask True still takes the focus where the person is painted,
        ## and not in the empty corner of the canvas.
        _zz_bad = []
        for _zz_loc, _zz_who in (("dorm_common", ["megumi", "nobara", "maki"]), ("dorm_common", ["yuji", "megumi", "nobara", "maki"]),
                                 ("classroom", ["yuji", "megumi", "nobara", "maki"]), ("cafeteria", ["yuji", "toge", "megumi"])):
            zzv_put(_zz_loc, _zz_who, "Afternoon")
            zzv_quiet()
            renpy.scene()
            renpy.show("zzv_bg", what=graded_bg())
            renpy.show_screen("sb_place")
            zz_render(0.3)
            for _zz_row in view_stage_rows(_zz_loc):
                _zz_x, _zz_y, _zz_w, _zz_h = _zz_row["rect"]
                _zz_f = zzv_focus_at(_zz_x + _zz_w // 2, _zz_y + int(_zz_h * 0.42))
                zz_render(0.1)
                _zz_tt = GetTooltip("sb_place")
                _zz_f2 = zzv_focus_at(_zz_x + 6, _zz_y + 6)
                if not (_zz_f == "stage_" + _zz_row["who"] and isinstance(_zz_tt, tuple) and _zz_tt[1] == _zz_f
                        and _zz_tt[0] == view_tip(_zz_row["who"], _zz_loc)
                        and (_zz_f2 == _zz_f) == bool(_zz_row["pose"])):
                    _zz_bad.append((_zz_loc, len(_zz_who), _zz_row["who"], _zz_f, _zz_tt, _zz_f2))
            if _zz_loc == "dorm_common" and len(_zz_who) == 3:
                _zz_far = [r for r in view_stage_rows(_zz_loc) if r["far"]][0]
                zzv_focus_at(_zz_far["rect"][0] + _zz_far["rect"][2] // 2, _zz_far["rect"][1] + int(_zz_far["rect"][3] * 0.42))
                zz_render(0.2)
                shot("hover_sprite_far", wait=0)
            renpy.hide_screen("sb_place")
        check(not _zz_bad, "the pointer on a person's chest focuses stage_<who> and GetTooltip('sb_place') is their label; "
              "the empty corner of a sprite's canvas does not, while a painted pose (Yuji's day test pose) is its whole box "
              "(four stages, 14 people; needs this window to hold the pointer)", _zz_bad)

        ## Tags by their real width: every room, four people with the longest
        ## short names, every tag carrying both marks (the widest a tag gets).
        _zz_long = sorted([w for w in ROSTER_ORDER if w in VIEW_FACE], key=lambda w: (-len(CAST[w]["short"]), w))[:4]
        _zz_bad = []
        _zz_wbad = []
        _zz_real_marks = store.view_tag_marks
        for _zz_forced in (False, True):
            store.view_tag_marks = zzv_both_marks if _zz_forced else _zz_real_marks
            for _zz_loc in LOCATIONS:
                zzv_put(_zz_loc, _zz_long, "Noon")
                zzv_quiet()
                renpy.show_screen("sb_place")
                zz_render(0.05)
                _zz_on = stage_people(_zz_loc)[0]
                _zz_tr = [zz_rect("sb_place", "tag_" + w) for w in _zz_on]
                _zz_dev = zz_rect("sb_place", "hud_dev")
                if (len(_zz_on) != 4 or not all(_zz_tr) or _zz_dev is None
                        or any(hot_overlap(a, b) for a in _zz_tr for b in _zz_tr if a is not b)
                        or any(hot_overlap(r, _zz_dev) for r in _zz_tr)
                        or any(r[0] < VIEW_TAG_EDGES[0] or r[0] + r[2] > VIEW_TAG_EDGES[1] for r in _zz_tr)
                        or any(b[0] - (a[0] + a[2]) < VIEW_TAG_GAP - 1 for a, b in zip(sorted(_zz_tr), sorted(_zz_tr)[1:]))):
                    _zz_bad.append((_zz_forced, _zz_loc, _zz_dev, _zz_tr))
                for _zz_w, _zz_r in zip(_zz_on, _zz_tr):
                    _zz_m = view_tag_marks(_zz_w, _zz_loc)
                    if _zz_r and abs(_zz_r[2] - view_tag_w(CAST[_zz_w]["short"], *_zz_m)) > 2:
                        _zz_wbad.append((_zz_w, _zz_m, _zz_r[2], view_tag_w(CAST[_zz_w]["short"], *_zz_m)))
                if _zz_forced and _zz_loc in ("dorm_common", "library"):
                    shot("tags_both_marks_" + _zz_loc, wait=0.1)
                renpy.hide_screen("sb_place")
        store.view_tag_marks = _zz_real_marks
        check(not _zz_bad, "with the four longest names on stage, in every room (%d, from LOCATIONS), plain and with both marks "
              "forced on every tag: no two tags overlap (8 px apart), none touches Review tools, none leaves x 179 to 1700"
              % len(LOCATIONS), _zz_bad[:4])
        check(not _zz_wbad, "view_tag_w is the tag's real width on screen (within 2 px)", _zz_wbad[:6])
        _zz_rows = [dict(rect=(x - 100, 0, 200, 10)) for x in (300, 320, 1650, 900)]
        check(view_tag_xs(_zz_rows, [100, 200, 120, 80]) == [300, 458, 1640, 900]
              and view_tag_xs([dict(rect=(100, 0, 200, 10))], [224]) == [291] and view_tag_xs([], []) == [],
              "view_tag_xs: under the person; pushed right by the two widths plus the gap; held inside the edges",
              view_tag_xs(_zz_rows, [100, 200, 120, 80]))
        zzv_put("cafeteria", ["yuji", "toge", "megumi"], "Noon")
        zzv_quiet()
    scene expression graded_bg()
    python:
        ## The badges: NEW follows night_allows('hang', 1); the mission mark the night's rules.
        _zz_patch = dict(has_event=lambda kind, who=None, loc=None: kind == "hangout" and who == "yuji",
                         missions_with=lambda who, loc=None: ["m_sunmall"] if who == "toge" else [])
        check(zzv_with(_zz_patch, lambda: (view_tag_marks("yuji", here), view_tag_marks("toge", here), view_tag_marks("megumi", here)))
              == ((False, True), (True, False), (False, False)),
              "a tag shows NEW for a waiting scene and the mark for a waiting mission")
        _zz_p2 = dict(_zz_patch, night_allows=lambda aid, cost: False)
        check(zzv_with(_zz_p2, lambda: (view_tag_marks("yuji", here), view_tag_marks("toge", here))) == ((False, False), (False, False)),
              "NEW is hidden while night_allows('hang', 1) is False, and the mission mark while the night won't let it start")
        _zz_p3 = dict(_zz_patch, night_can_work=lambda: False)
        check(zzv_with(_zz_p3, lambda: view_tag_marks("toge", here)) == (False, False), "no mission mark on a rest day")
        explore_mode = True
        check(zzv_with(_zz_patch, lambda: view_tag_marks("toge", here)) == (False, False), "nor in explore mode")
        explore_mode = False
        _zz_orig = (store.has_event, store.missions_with)
        store.has_event, store.missions_with = _zz_patch["has_event"], _zz_patch["missions_with"]
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_y = zzv_under(zzv_wid("sb_place", "tag_yuji"))
        _zz_g = zzv_under(zzv_wid("sb_place", "tag_toge"))
        check(_zz_y == ["Yuji", "NEW"] and _zz_g[0] == CAST["toge"]["short"] and _zz_g[1] == u"「!」" and len(_zz_g) == 2,
              "on the screen: the short name, then NEW or the gold mark (two words a person at most)", (_zz_y, _zz_g))
        shot("tags_badges", wait=0.2)
        store.has_event, store.missions_with = _zz_orig
    hide screen sb_place
    python:
        check(has_event.__code__.co_filename.endswith("sb_events.rpy"), "fixture: the patched functions are put back")
        zzv_put("dorm_common", ["yuji", "megumi", "nobara", "maki"], "Evening")
    scene expression graded_bg()
    python:
        check(zz_worst("sb_place", hover="tag_megumi"), "zz_worst screenshot: sb_place, four people, a name tag hovered")
        ## P8: with four people a tag's label opens above the tag, a person's
        ## above their head: neither covers another tag.
        zzv_quiet()
        _zz_on = stage_people(here)[0]
        _zz_tr = dict((w, zz_rect("sb_place", "tag_" + w)) for w in _zz_on)
        _zz_bad = []
        for _zz_w in _zz_on:
            for _zz_p in ("tag_", "stage_"):
                renpy.set_focus("sb_place", _zz_p + _zz_w)
                zz_render(0.4)
                _zz_lab = zzv_label()
                if (_zz_lab is None or _zz_lab[0] < 0 or _zz_lab[1] < 0 or _zz_lab[0] + _zz_lab[2] > 1920 or _zz_lab[1] + _zz_lab[3] > 1080
                        or any(r is None or hot_overlap(_zz_lab, r) for k, r in _zz_tr.items() if k != _zz_w)
                        or (_zz_p == "tag_" and hot_overlap(_zz_lab, _zz_tr[_zz_w]))):
                    _zz_bad.append((_zz_p + _zz_w, _zz_lab))
                if (_zz_p, _zz_w) == ("tag_", _zz_on[1]):
                    shot("hover_tag_four", wait=0)
        check(len(_zz_on) == 4 and not _zz_bad and icon_tip_side(("x", "tag_megumi")) == "top" and icon_tip_side(("x", "stage_megumi")) == "top",
              "four people: no name tag's or person's hover label meets another person's tag (hover check: needs the pointer)",
              (_zz_bad, _zz_tr))
        del _zz_tr
        renpy.hide_screen("sb_place")

    ## --- 11. idle to talking -------------------------------------------------------------------
    python:
        _zz_sp = renpy.game.script.lookup("stage_person")
        _zz_par = [p for p in _zz_sp.parameters.parameters] if _zz_sp.parameters is not None else []
        _zz_names = [getattr(p, "name", p if isinstance(p, str) else (p[0] if isinstance(p, tuple) else p)) for p in _zz_par]
        check([builtins.str(n) for n in _zz_names] == ["who", "expr"], "stage_person's signature is unchanged: (who, expr=None)", _zz_names)
    show screen zzv_focus_one
    python:
        zz_render(0.6)
        _zz_f = [d for d in zzv_order("zzv_focus_one") if isinstance(d, renpy.display.transform.ATLTransform)]
        check(len(_zz_f) == 1 and _zz_f[0].state.xcenter == 520 and abs(_zz_f[0].state.zoom - 0.66) < 1e-6 and _zz_f[0].state.yoffset == -20,
              "char_focus(x0) with one argument still works, and ends at xcenter 520, zoom 0.66",
              [(d.state.xcenter, d.state.zoom) for d in _zz_f])
    hide screen zzv_focus_one
    python:
        zzv_put("dorm_common", ["megumi", "nobara", "maki"], "Noon")
        zzv_quiet()
    scene expression graded_bg()
    show screen sb_char("nobara")
    $ shot("person_view_mid_ease", wait=0.15)
    python:
        zz_render(0.5)
        _zz_f = [d for d in zzv_order("sb_char") if isinstance(d, renpy.display.transform.ATLTransform) and d.atl is char_focus.atl]
        _zz_row = [r for r in view_stage_rows(here) if r["who"] == "nobara"][0]
        check(len(_zz_f) == 1 and _zz_f[0].state.xcenter == 520 and abs(_zz_f[0].state.zoom - 0.66) < 1e-6
              and _zz_row["far"] == 1 and _zz_f[0].context.context.get("z0") == _zz_row["zoom"] and _zz_f[0].context.context.get("y0") == _zz_row["yoff"],
              "the person view starts the person from their own slot (its zoom and height) and ends at xcenter 520, zoom 0.66",
              (_zz_row, [d.context.context for d in _zz_f]))
        check(zz_worst("sb_char", "nobara"), "zz_worst screenshot: sb_char (the focused person)")
        renpy.hide_screen("sb_char")
        zzv_put("dorm_common", ["megumi", "nobara", "maki"], "Evening")
    show screen sb_char("nobara")
    python:
        zz_render(0.8)
        _zz_o = zzv_order("sb_char")
        _zz_out = [d for d in _zz_o if isinstance(d, renpy.display.transform.ATLTransform) and d.atl is view_pose_out.atl]
        _zz_in = [d for d in _zz_o if isinstance(d, renpy.display.transform.ATLTransform) and d.atl is view_focus_in.atl]
        check(len(_zz_out) == 1 and len(_zz_in) == 1 and _zz_out[0].state.alpha == 0.0 and _zz_in[0].state.alpha == 1.0
              and _zz_in[0].state.xcenter == 520,
              "someone who was a painted pose: the pose fades out as the talking sprite fades in",
              [(d.state.alpha) for d in _zz_out + _zz_in])
    hide screen sb_char
    python:
        zzv_put("cafeteria", ["yuji", "megumi"], "Noon")
        ## The two dissolves.
        renpy.game.interface.transition.clear()
        _zz_r = [view_before_person("megumi"), view_after_scene()]
        _zz_tr = renpy.game.interface.transition.get(None)
        check(_zz_r == [None, None] and _zz_tr is not None, "view_before_person and view_after_scene queue a transition "
              "for the next interaction (renpy.transition, not a with statement)", _zz_tr)
        renpy.game.interface.transition.clear()
        config.skipping = "fast"
        _zz_r = [view_before_person("megumi"), view_after_scene()]
        _zz_tr = renpy.game.interface.transition.get(None)
        view_enter("megumi")
        _zz_d = zzv_master("megumi")
        config.skipping = None
        check(_zz_tr is None and zzv_atl(_zz_d) is pos_c.atl and "view_fg" in zz_layer_tags("master"),
              "under skipping no transition runs, and the sprite goes straight to pos_c (the foreground still over it)",
              (_zz_tr, _zz_d))
    scene expression graded_bg()
    python:
        check("view_fg" not in zz_layer_tags("master") and "megumi" not in zz_layer_tags("master"),
              "and nothing is left after the scene statement", zz_layer_tags("master"))
        store._in_replay = "zzv_replay"
        _zz_r = [view_before_person("megumi"), view_after_scene()]
        _zz_tr = renpy.game.interface.transition.get(None)
        view_enter("megumi")
        _zz_d = zzv_master("megumi")
        _zz_tags = zz_layer_tags("master")
        store._in_replay = None
        check(zzv_atl(_zz_d) is pos_c.atl and "view_fg" not in _zz_tags and _zz_tr is None,
              "inside a replay view_enter shows the sprite at pos_c with no foreground (and no dissolve)", (_zz_d, _zz_tags))
        ## The same in a real replay: a new context started from memory_scope.
        _zz_mem = MEMORIES[0]["id"]
        _zz_scope = memory_scope(_zz_mem)
        _zz_scope.update(here="cafeteria", period="Noon")
        ZZV["replay"] = None
        renpy.call_replay("zzv_replay", scope=_zz_scope)
        check(ZZV["replay"] == (True, True, False, "cafeteria", True) and not _in_replay,
              "a real replay (renpy.call_replay with memory_scope's scope, in the cafeteria): stage_person shows the sprite "
              "at pos_c with no foreground", ZZV["replay"])
    scene expression graded_bg()
    python:
        persistent.motion = False
        view_enter("megumi", "serious")
        _zz_d = zzv_master("megumi")
        persistent.motion = True
        check(zzv_atl(_zz_d) is pos_c.atl and "view_fg" in zz_layer_tags("master") and view_enter("megumi") is None,
              "with motion off the sprite is shown at pos_c, as before")
        here = "riverside"
    scene expression graded_bg()
    python:
        view_enter("megumi")
        check("megumi" in zz_layer_tags("master") and "view_fg" not in zz_layer_tags("master"),
              "in a room with no foreground file view_enter shows only the sprite")
        here = "dorm_common"
    scene expression graded_bg()
    python:
        view_enter("megumi")
        check(view_fg_path(here) is not None and "view_fg" not in zz_layer_tags("master") and VIEW_FG_TALK == ("cafeteria",),
              "nor in a room whose foreground object stands mid-room (the coffee table): someone at pos_c is in front of it")
    scene expression graded_bg()
    python:
        period = "Evening"
        _zz_img = view_fg_image(view_fg_path("cafeteria", "Evening"), "cafeteria")
        check(isinstance(_zz_img, Transform) and zzv_dumps(_zz_img) and zzv_dumps(view_fg_image(view_fg_path(here), here)),
              "the foreground view_enter shows pickles, tinted (the cafeteria in the Evening) or not")
        check(zzv_dumps(renpy.curry(view_breathe_fn)(phase=0.2)) and zzv_dumps(renpy.curry(view_blink_fn)(who="yuji"))
              and zzv_dumps(renpy.curry(view_talk_fn)(who="yuji")) and zzv_dumps(view_enter_ease),
              "the curried transform functions and view_enter_ease pickle (top-level, R10)")
        period = "Noon"

    ## --- 12. the save test, in real dialogue (it loads and rolls back: last) ------------
    python:
        zzv_fixture()
        zzv_put("cafeteria", ["yuji", "megumi"], "Noon")
        zzv_quiet()
        VIEW_SPEAKING[:] = [None, 0.0]
        renpy.loadable = ZZV_LOADABLE[0]
        zzv_sweep()
        if ZZV.get("began"):
            abort("the save test began twice: a rollback or a load went back past its start")
        ZZV.update(phase=1, loads=0, ticks=0, began=True)
    ## The harness's own scratch objects (screens' displayables, modules) are in
    ## the rollback log by now, and a save pickles the log: start it afresh.
    ## The game's log holds only game state; p2_saves tests it untrimmed.
    $ renpy.block_rollback(purge=True)
    scene expression graded_bg()
    megumi "ZZV BEFORE"
    call stage_person("yuji", "neutral")
    yuji "ZZV ONE"
    yuji "ZZV TWO"
    show megumi neutral at pos_l
    python:
        check(ZZV["phase"] == 0, "the save test ran every step", ZZV["phase"])
        check({"yuji", "megumi", "view_fg"} <= zz_layer_tags("master"), "a scene that then shows a second character",
              zz_layer_tags("master"))
    scene expression graded_bg()
    python:
        check(not ({"yuji", "megumi", "view_fg"} & zz_layer_tags("master")), "still clears on scene: a scene statement "
              "clears the foreground", zz_layer_tags("master"))
        zzv_sweep()
    $ finish()
