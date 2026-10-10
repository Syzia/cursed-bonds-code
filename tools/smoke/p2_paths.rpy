## tools/smoke/p2_paths.rpy -- P9's package harness (PHASE2_DESIGN.md section
## 13: walking between places, and the checkpoint B touch-ups).
##
##   tools/smoke.sh tools/smoke/p2_paths.rpy
##
## Every acceptance bullet of 13.2 is a named check, in the plan's order
## (sections 1 to 7 below; 8 is a walk through real clicks, 9 the worst case,
## 10 a save, a load and a rollback through exit walks inside the real loop,
## which ends the run from label sandbox). What
## is run outside a harness is a NOTE that says so: phase1_all, wp3_missions
## and the 11 saves (bullet 7).
##
## P8: the five hubs' exits sit on the doors and paths of their painted
## pictures; no exit is within 120 px of a room's own hotspot (P6's final
## points); a locked exit is the lock icon drawn dim (alpha 0.45); the hover
## label checks hold whichever side of its icon a label opens on.
##
## The overlay tools/smoke/assets/p2_paths/game/images/bg/ holds a test
## picture for each of the five new hubs, so in this run `bg <hub>` is the
## dropped-in picture; the stand-in path is tested by making renpy.loadable
## say no for the file and building the picture again (world_hub_bg).
##
## Screenshots (shots/p2_paths/): worst_sb_map and worst_sb_place (zz_worst),
## every hub with its test picture and with its stand-in, the campus map with
## three faces and a gold mark on every marker, each area view, a locked
## exit (and the longest lock's hover label), every hub on arrival (the
## caption up), four people in front of the exits, the walk from my room to
## the training hall, and the place view after a load.

init 999 python:
    import os
    import subprocess as zz_subprocess
    import builtins as zz_builtins
    ## Imported at init (zz_re is _lib.rpy's): a module imported into the
    ## running store would reach section 10's save.
    import pickle as zz_pickle

    ZZ_HUBS = ("school_yard", "dorm_yard", "staff_yard", "training_yard", "trailhead")
    ZZ_HUB_NAMES = {"school_yard": "School Courtyard", "dorm_yard": "Dormitory Garden",
                    "staff_yard": "Staff Building Steps", "training_yard": "Training Yard",
                    "trailhead": "Mountain Path"}
    ZZ_HUB_AREA = {"school_yard": "school", "dorm_yard": "dorms", "staff_yard": "staff",
                   "training_yard": "grounds", "trailhead": "mountain"}

    ## The stand-in path: renpy.loadable says no for the five hub pictures.
    zz_loadable0 = renpy.loadable

    def zz_no_hubs(path, *args, **kwargs):
        if str(path) in ["images/bg/%s.png" % h for h in ZZ_HUBS]:
            return False
        return zz_loadable0(path, *args, **kwargs)

    zz_who_is_here0 = who_is_here
    ZZ_CROWD = zz_builtins.list([0])

    def zz_crowd(loc=None, per=None):
        """ZZ_CROWD[0] people in whichever room is asked about."""
        return ["yuji", "megumi", "nobara", "panda", "toge"][:ZZ_CROWD[0]]

    def zz_tree(root):
        out = zz_builtins.list()
        root.visit_all(out.append)
        return out

    def zz_strings(root):
        return [zz_text_string(d) for d in zz_tree(root) if isinstance(d, renpy.text.text.Text)]

    def zz_faces(root):
        out = zz_builtins.list()
        for d in zz_tree(root):
            fn = getattr(d, "filename", None)
            if isinstance(fn, str) and fn.startswith("images/side/") and fn.endswith("_neutral.png"):
                out.append(fn)
        return out

    def zz_icons(root):
        """The icon pictures drawn under root, by name."""
        out = zz_builtins.list()
        for d in zz_tree(root):
            fn = getattr(d, "filename", None)
            if isinstance(fn, str) and fn.startswith("images/icons/ic_"):
                out.append(fn[len("images/icons/ic_"):-len(".png")])
        return out

    def zz_tooltips(screen):
        """Every tuple tooltip's text on a shown screen."""
        sc = renpy.get_screen(screen)
        out = zz_builtins.list()
        if sc is None:
            return out
        for d in zz_tree(sc):
            t = getattr(d, "_tooltip", None)
            if isinstance(t, tuple) and t and isinstance(t[0], str):
                out.append(t[0])
        return out

    def zz_place(loc, per=None):
        """Stand somewhere and draw the place view."""
        store.here = loc
        if per:
            store.period = per
        ARRIVAL[0] = (store.day, store.period, store.here)
        ARRIVAL[1] -= 10            # the arrival caption has faded
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_place")
        zz_render(0.15)

    def zz_hot(wid):
        """The button of a hotspot (or a column tile) in the place view."""
        return renpy.get_widget("sb_place", wid)

    def zz_press(wid):
        """Press a place-view button by id: what its action returns
        ("zz_missing" when it isn't there)."""
        w = zz_hot(wid)
        if w is None:
            return "zz_missing"
        return renpy.run(w.action)

    def zz_action_value(wid):
        """The tuple a place-view button returns, without pressing it; None
        for a button that does nothing."""
        w = zz_hot(wid)
        a = getattr(w, "action", None)
        if isinstance(a, Return):
            return a.value
        return None

    def zz_tip(wid):
        w = zz_hot(wid)
        t = getattr(w, "_tooltip", None) if w is not None else None
        return t[0] if isinstance(t, tuple) else t

    def zz_exits_offered(loc):
        """(in the room, in the column): the exit actions the place view
        offers at loc right now."""
        room = [h["act"] for h in hot_spots_for(loc) if str(h["act"]).startswith("path_")]
        column = [a[0] for a in rail_actions(loc) if a[0].startswith("path_")]
        return room, column

    def zz_overlap(a, b):
        return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])

    def zz_open_campus():
        """A late save: everyone met, every door that a flag opens is open."""
        settle(day=9, period="Noon", here="dorm")
        store.roster = list(ROSTER_ORDER)
        for f in ("roll_call", "utahime_arrived", "intensive_done", "storehouse_access", "ijichi_rides", "invited_girls_dorm"):
            flag(f)
        store.done_events.add("st_roll_call")
        store.companion = None
        store.schedule_overrides = {}
        roll_gojo()

    def zz_two(key):
        return 2

    def zz_arrive(loc, per=None):
        """Stand somewhere, just arrived: the place view with its caption up."""
        store.here = loc
        if per:
            store.period = per
        ARRIVAL[0] = None
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_place")
        zz_render(0.6)

    def zz_caption_box(loc):
        """The arrival caption's panel in a place, from its texts (screen
        sb_place: a frame at (40, 100), padding (22, 10, 22, 14), the name at
        44 beside the period, the description at 20 wrapped at 700)."""
        d = Text(LOCATIONS[loc]["desc"], style="sb_arrival_text", size=20, xmaximum=700)
        dw, dh = renpy.render(d, 700, 400, 0, 0).get_size()
        n = Text(LOCATIONS[loc]["name"], style="sb_arrival_text", font=gui.display_font, size=44)
        nw, nh = renpy.render(n, 1200, 400, 0, 0).get_size()
        pw = max(renpy.render(Text("· " + p, style="sb_arrival_text", font=gui.body_medium_font, size=20, kerning=gui.track), 600, 400, 0, 0).get_size()[0]
                 for p in PERIODS)
        return (40, 100, int(max(dw, nw + 14 + pw) + 44), int(10 + nh + 4 + dh + 14))

    def zz_hover_rect():
        """The hover label's rectangle as it was last drawn, (x, y, w, h);
        None when no label is up."""
        sc = renpy.get_screen("hover_label")
        if sc is None:
            return None
        for d in zz_tree(sc):
            if isinstance(d, renpy.display.layout.NearRect) and d.child is not None:
                size = getattr(d.child, "window_size", None)
                offs = getattr(d, "offsets", None)
                if size and offs:
                    return (int(offs[0][0]), int(offs[0][1]), int(size[0]), int(size[1]))
        return None

    def zz_alpha(wid):
        """How see-through a place-view button is drawn: the product of the
        alpha of every Transform around it (1.0 for a plain button); None
        when the button isn't there."""
        w = zz_hot(wid)
        sc = renpy.get_screen("sb_place")
        if w is None or sc is None:
            return None
        a = 1.0
        for d in zz_tree(sc):
            if isinstance(d, renpy.display.transform.Transform) and d is not w and w in zz_tree(d):
                a *= float(d.alpha)
        return round(a, 2)

    def zz_keep_clear(loc):
        """K3. The points an exit of `loc` keeps PATH_CLEAR px from:
        path_keep_clear(loc) once the scaffold defines it (the live hotspot
        points), and until then the live points themselves, which is what
        that function will answer."""
        fn = getattr(store, "path_keep_clear", None)
        if callable(fn):
            return [(p[0], p[1]) for p in fn(loc)]
        return [(x, y) for i, x, y in zz_room_spots(loc)]

    def zz_dist(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def zz_in_frame(x, y):
        return HOT_BOUNDS[0] <= x <= HOT_BOUNDS[2] and HOT_BOUNDS[1] <= y <= HOT_BOUNDS[3]

    def zz_room_spots(loc):
        """[(id, x, y)]: a place's own hotspots (every one that is not an
        exit), where they sit: the sidecar hot_<loc>.json applied."""
        side = rule_layout("hot_" + loc).get("spots") or {}
        out = zz_builtins.list()
        for h in HOT_SPOTS:
            if h["place"] == loc and not h["id"].startswith("go_") and not h["id"].startswith("zz_"):
                p = side.get(h["id"])
                x, y = (p[0], p[1]) if isinstance(p, (zz_builtins.list, zz_builtins.tuple)) and len(p) == 2 else (h["x"], h["y"])
                out.append((h["id"], int(x), int(y)))
        return out

    def zz_lock_label(hub, to):
        """Hover the exit hub -> to in the place view as it stands and
        measure: (the hover label's rectangle, the buttons of the hub's
        other exits it covers). The rectangle is None unless the label is
        drawn next to that exit's own button (within 24 px of it): a label
        still laid out for another button is not measured."""
        own = zz_rect("sb_place", "hot_" + path_spot_id(hub, to))
        hr = None
        for n in (0, 1, 2):
            if n:
                ## The label's place is taken when the focus changes: step
                ## onto another exit and back.
                away = [t for t in path_neighbours(hub) if t != to and zz_hot("hot_" + path_spot_id(hub, t)) is not None]
                if away:
                    renpy.set_focus("sb_place", "hot_" + path_spot_id(hub, away[0]))
                    zz_render(0.2)
            renpy.set_focus("sb_place", "hot_" + path_spot_id(hub, to))
            zz_render(0.4)
            hr = zz_hover_rect()
            if hr is not None and own is not None and hot_overlap(hr, (own[0] - 24, own[1] - 24, own[2] + 48, own[3] + 48)):
                break
            hr = None
        others = [(t, zz_rect("sb_place", "hot_" + path_spot_id(hub, t))) for t in path_neighbours(hub) if t != to]
        hit = [t for t, r in others if hr is not None and r is not None and hot_overlap(hr, r)]
        return hr, hit

    def zz_row_reads():
        """How the storehouse exit's two registry rows read right now, each
        way a reader may take them: (labels, icons, the rest holds). Plain
        values: the rows themselves never become store variables here (a
        harness variable would carry them into a save)."""
        ar = [a for a in PLACE_ACTIONS if a["id"] == "path_storehouse"][0]
        sr = [h for h in HOT_SPOTS if h["id"] == "go_training_yard__storehouse"][0]
        labels = [ar["label"], ar.get("label"), zz_builtins.dict(ar)["label"], zz_builtins.dict(ar.items())["label"], ar.copy()["label"]]
        icons = [sr["icon"], sr.get("icon"), zz_builtins.dict(sr)["icon"], zz_builtins.dict(sr.items())["icon"], sr.copy()["icon"]]
        rest = (ar["label"] in ar.values() and ar.get("zz_none", 7) == 7 and ar.get("zz_none") is None
                and sorted(sr) == sorted(zz_builtins.dict.keys(sr)) and len(sr) == len(zz_builtins.dict(sr))
                and type(sr.copy()) is zz_builtins.dict and sr.get("id") == "go_training_yard__storehouse")
        return labels, icons, bool(rest)

    def zz_cover_storehouse(loc):
        """Someone standing right in front of the training yard's storehouse exit."""
        x, y = [(r["x"], r["y"]) for r in path_exits("training_yard") if r["to"] == "storehouse"][0]
        return [(x - 100, y - 100, 200, 800)]

    ## Section 10: a state machine driven by a timer, inside `jump sandbox`.
    ## Init-made builtins, so a load and a rollback leave them alone.
    ZZ_LOOP = zz_builtins.list([0, 0, 0, None])     # phase, loads seen, ticks, the clock at the start

    def zz_loop_loaded():
        if ZZ_LOOP[0]:
            ZZ_LOOP[1] += 1

    config.after_load_callbacks.append(zz_loop_loaded)

    def zz_loop_press(wid):
        w = renpy.get_widget("sb_place", wid)
        if w is None:
            check(False, "the loop: button %s is there" % wid, (store.here, [h["id"] for h in hot_spots_for(store.here)]))
            finish()
        return renpy.run(w.action)

    def zz_loop_save_names(slot):
        data, _sig = renpy.loadsave.location.load(slot)
        return [n for n in (b"path_ActionRow", b"path_SpotRow", b"path_LiveRow", b"path_builtins") if n in data]

    def zz_loop_step():
        L = ZZ_LOOP
        if not L[0] or len(renpy.game.contexts) != 1:
            return None
        L[2] += 1
        if L[2] > 60:
            check(False, "the loop: the run reaches its end", (zz_builtins.list(L), store.here, renpy.get_screen("sb_place") is not None))
            finish()
        if not renpy.get_screen("sb_place"):
            return None
        h = store.here
        tm = (store.day, store.period, store.stamina)
        ## The second UI overhaul (4.4; U0b): my room opens onto the corridor
        ## of the Boys' Dormitory, and the corridor onto the garden (state 15
        ## is the corridor, between the old states 1 and 2).
        if L[0] == 1 and h == "dorm":
            L[3] = tm
            L[0], L[2] = 15, 0
            return zz_loop_press("hot_go_dorm__boys_dorm")
        if L[0] == 15 and h == "boys_dorm":
            check(tm == L[3], "in the real loop (label sandbox): the exit in my room walks to the Boys' Dormitory, no time spent", (tm, L[3]))
            L[0], L[2] = 2, 0
            return zz_loop_press("hot_go_boys_dorm__dorm_yard")
        if L[0] == 2 and h == "dorm_yard":
            check(tm == L[3], "and the corridor's stairs walk on to the Dormitory Garden, no time spent", (tm, L[3]))
            renpy.take_screenshot()
            renpy.save("zz_p9_walk")
            check(not zz_loop_save_names("zz_p9_walk"), "a save made in a hub after an exit walk holds no registry row class", zz_loop_save_names("zz_p9_walk"))
            L[0], L[2] = 3, 0
            renpy.load("zz_p9_walk")
        if L[0] == 3:
            room = [x["id"] for x in hot_spots_for(h)]
            col = [a[0] for a in rail_actions(h) if a[0].startswith("path_")]
            ## K3 (docs/UI2_DESIGN.md): the count is the table's, and a yard has at most seven.
            check(L[1] == 1 and h == "dorm_yard" and tm == L[3] and len(room) + len(col) == len(path_exits("dorm_yard")) <= 7,
                  "that save loads onto the same place view: the Dormitory Garden, every one of its exits offered (%d; at most seven)"
                  % len(path_exits("dorm_yard")), (L[1], h, tm, room, col))
            shot("after_load_dorm_yard", wait=0)
            L[0], L[2] = 4, 0
            return zz_loop_press("hot_go_dorm_yard__courtyard")
        if L[0] == 4 and h == "courtyard":
            check(tm == L[3], "after the load, walking on works: Dormitory Garden to Courtyard")
            L[0], L[2] = 5, 0
            return zz_loop_press("hot_go_courtyard__training_yard")
        if L[0] == 5 and h == "training_yard":
            L[0], L[2] = 6, 0
            renpy.rollback(force=True, checkpoints=1)
        if L[0] == 6:
            check(h == "courtyard" and tm == L[3], "rolling back one step through an exit walk: I am back in the courtyard", (h, tm))
            L[0], L[2] = 7, 0
            renpy.rollback(force=True, checkpoints=1)
        if L[0] == 7:
            check(h == "dorm_yard" and tm == L[3], "rolling back a second step: back in the Dormitory Garden", (h, tm))
            L[0], L[2] = 8, 0
            return zz_loop_press("hot_go_dorm_yard__trailhead")
        if L[0] == 8 and h == "trailhead":
            check(tm == L[3], "after two rollbacks, walking on works: Dormitory Garden to Mountain Path")
            finish()
        return None

    config.overlay_screens.append("zz_paths_loop")

    def zz_all_moons():
        return dict((a["key"], "moon") for a in AREAS)

    ZZ_WALK = zz_builtins.list()


## Presses a place-view button from inside the running interaction (the real
## `call screen sb_place`), so its Return value comes back as _return.
screen zz_paths_press(wid, delay=0.5):
    zorder 200
    timer delay action [Hide("zz_paths_press"), Function(zz_press, wid)]


## Section 10's driver: idle until ZZ_LOOP[0] is set.
screen zz_paths_loop():
    zorder 200
    if ZZ_LOOP[0]:
        timer 0.4 repeat True action Function(zz_loop_step)


label zz_smoke:

    python:
        fixture(mc_name="Tester", mc_surname="Harness")
        zz_open_campus()

    ## --- 0. what P9 provides (13.2) ------------------------------------------------------------
    python:
        for _zz_n in ("path_exits", "path_hub", "path_neighbours"):
            check(getattr(store, _zz_n).__code__.co_filename.endswith("room_paths.rpy"), "%s is room_paths.rpy's" % _zz_n)
        _zz_bad = []
        for _zz_l in list(LOCATIONS) + ["zz_nowhere"]:
            _zz_e = path_exits(_zz_l)
            _zz_nb = path_neighbours(_zz_l)
            if not (isinstance(_zz_e, zz_builtins.list) and isinstance(_zz_nb, zz_builtins.list)
                    and all(isinstance(r, zz_builtins.dict) and sorted(r) == ["icon", "label", "locked_reason", "to", "x", "y"]
                            and isinstance(r["to"], str) and isinstance(r["label"], str) and r["label"] and r["icon"] in ICONS
                            and type(r["x"]) is int and type(r["y"]) is int and isinstance(r["locked_reason"], str) for r in _zz_e)
                    and [r["to"] for r in _zz_e] == _zz_nb and path_exits(_zz_l) == _zz_e):
                _zz_bad.append((_zz_l, _zz_e))
        check(not _zz_bad, "path_exits(loc) is a list of dicts (to, label, icon, x, y, locked_reason) in a stable order; path_neighbours(loc) is its `to`s", _zz_bad[:2])
        check(path_exits("zz_nowhere") == [] and path_neighbours("zz_nowhere") == [] and path_hub("zz_nowhere") == ""
              and [path_hub(a["key"]) for a in AREAS] == ["courtyard", "school_yard", "dorm_yard", "staff_yard", "training_yard", "trailhead"],
              "path_hub(area) is the hub's key; nothing here returns None", [path_hub(a["key"]) for a in AREAS])
        check(path_validate() == [] and hot_validate() == [] and map_validate() == [] and _validate_world() == [] and _validate_place_actions() == [],
              "the path, hotspot, map, world and place-action validators find nothing",
              path_validate() + hot_validate() + map_validate() + _validate_world() + _validate_place_actions())

    ## --- 1. the graph ----------------------------------------------------------------------------
    python:
        ## K3: the number of places is LOC_ORDER's (K11 raises it once, in the table).
        check(all(path_neighbours(l) for l in LOCATIONS) and len(LOCATIONS) == len(LOC_ORDER) == len(set(LOC_ORDER)),
              "every place has at least one exit (%d places, the ones in LOC_ORDER)" % len(LOC_ORDER),
              [l for l in LOCATIONS if not path_neighbours(l)])
        ## The second UI overhaul (4.4, the house rule; U0b): a room inside a
        ## house (WORLD_INSIDE) leads to its house first; every other room to
        ## its area's hub.
        _zz_bad = [(l, path_neighbours(l)) for l in LOCATIONS
                   if path_hub(area_of(l)) != l and path_neighbours(l)[:1] != [world_inside(l) or path_hub(area_of(l))]]
        check(not _zz_bad and world_inside("dorm") == "boys_dorm",
              "every room's first exit leads to its area's hub, or to its house when it is a room inside one (my room: the Boys' Dormitory)", _zz_bad)
        _zz_links = {}
        for _zz_a, _zz_b in PATH_LINKS:
            _zz_links.setdefault(_zz_a, []).append(_zz_b)
            _zz_links.setdefault(_zz_b, []).append(_zz_a)
        _zz_bad = []
        for _zz_ar in AREAS:
            _zz_h = path_hub(_zz_ar["key"])
            _zz_want = [l for l in _zz_ar["places"] if l != _zz_h and not world_inside(l)] + _zz_links.get(_zz_h, [])
            if sorted(_zz_want) != sorted(path_neighbours(_zz_h)):
                _zz_bad.append((_zz_h, _zz_want, path_neighbours(_zz_h)))
            ## a house: its yard first, then exactly the rooms inside it
            for _zz_l in _zz_ar["places"]:
                _zz_inside = [r for r in _zz_ar["places"] if world_inside(r) == _zz_l]
                if _zz_l != _zz_h and sorted(path_neighbours(_zz_l)[1:]) != sorted(_zz_inside):
                    _zz_bad.append((_zz_l, _zz_inside, path_neighbours(_zz_l)))
        check(not _zz_bad, "every hub has an exit to each of its rooms (not to a room inside a house) and to each neighbouring hub, "
              "and no other; a room leads on only to the rooms inside it", _zz_bad)
        check(("gate", "courtyard") not in PATH_LINKS and path_neighbours("gate") == ["courtyard"] and "gate" in path_neighbours("courtyard"),
              "the gate opens onto the courtyard, and the courtyard leads back to it")
        check(path_reach("dorm") == set(LOCATIONS), "the graph is connected: from my room every place is reached by exits alone",
              sorted(set(LOCATIONS) - path_reach("dorm")))
        note("hubs joined as map_campus.png's paths join the areas (tools/genworld.py PATHS)",
             "%r. D54 listed courtyard to staff_yard; the picture draws no such path (the office is joined to the training hall, "
             "the girls' dormitory and the ridge), so staff_yard joins training_yard and dorm_yard instead" % (PATH_LINKS,))
        ## The registrations behind them (D55).
        _zz_acts = dict((a["id"], a) for a in PLACE_ACTIONS if a["id"].startswith("path_"))
        _zz_spots = [h for h in HOT_SPOTS if h["id"].startswith("go_")]
        check(sorted(_zz_acts) == sorted("path_" + l for l in LOCATIONS)
              and all(a["cost"] == 0 and a["explore"] is True and a["when"] is None
                      and sorted(a["locs"]) == sorted(f for f in LOCATIONS if a["id"][5:] in path_neighbours(f))
                      for a in _zz_acts.values())
              and all(renpy.has_label("sb_do_" + k) for k in _zz_acts),
              "one place action per destination: cost 0, offered in explore mode, in exactly the places that have an exit to it, with its label")
        check(len(_zz_spots) == sum(len(v) for v in PATH_EXITS.values())
              and all(h["kind"] == "act" and h["id"] == "go_%s__%s" % (h["place"], h["act"][5:])
                      and not h["standalone"] and not h["front"] and h["icon"] in ICONS and h["icon"] != "back" for h in _zz_spots),
              "one action hotspot per exit, go_<from>__<to>, on the frozen framework; no exit uses the back icon", len(_zz_spots))
        _zz_ic = dict((l, path_icon(l)) for l in LOCATIONS)
        ## The second UI overhaul (3.1): each of the five yards has an icon name
        ## of its own, place_<yard>, and wears it once that picture is cut;
        ## until then its area's, as before. The Courtyard, the heart's hub,
        ## is not one of the five: an exit to it stays area_heart.
        check(all(_zz_ic[l] == (("place_" + l if (l in PATH_YARD_ICONS and icon_has_art("place_" + l)) else "area_" + area_of(l))
                                if l == path_hub(area_of(l)) else "place_" + l)
                  for l in LOCATIONS)
              and all(icon_for("act", "path_" + l) == _zz_ic[l] and _zz_ic[l] in ICONS for l in LOCATIONS),
              "icons are existing names: place_<room> for a room, and for a hub area_<key> until its own picture is cut "
              "(in the room and in the column)", _zz_ic)
        note("action ids", "D55 says go_<to>; they are path_<to> (label sb_do_path_<to>), because R1's --prefixes "
             "rejects a label sb_do_go_<to> in room_paths.rpy. The hotspot ids are D55's go_<from>__<to>.")
        ## The registry's own rows leave the store with this statement: a
        ## harness variable still holding one would carry it into section
        ## 10's save (through the rollback log), which the game never does.
        del _zz_acts, _zz_spots

    ## --- 2. taking an exit ------------------------------------------------------------------------
    python:
        zz_place("dorm", "Noon")
        ## The second UI overhaul (4.4; U0b): my room's one exit is my door,
        ## onto the corridor of the Boys' Dormitory.
        check(zz_action_value("hot_go_dorm__boys_dorm") == ("act", "path_boys_dorm") and zz_hot("hot_go_dorm__dorm_yard") is None,
              "the exit in my room is a button in the picture that returns ('act', 'path_boys_dorm')", zz_action_value("hot_go_dorm__boys_dorm"))
        check(zz_tip("hot_go_dorm__boys_dorm") == "To the Boys' Dormitory", "its hover label reads To the Boys' Dormitory", zz_tip("hot_go_dorm__boys_dorm"))
        check(zz_hot("rail_path_boys_dorm") is None, "and it is not in the icon column as well")
        zz_place("boys_dorm", "Noon")
        check(zz_tip("hot_go_boys_dorm__dorm") == "To My Room" and zz_action_value("hot_go_boys_dorm__dorm") == ("act", "path_dorm")
              and zz_tip("hot_go_boys_dorm__dorm_yard") == "To the Dormitory Garden",
              "in the corridor the door at the end reads To My Room, and the stairs To the Dormitory Garden",
              (zz_tip("hot_go_boys_dorm__dorm"), zz_tip("hot_go_boys_dorm__dorm_yard")))
        zz_place("dorm_yard", "Noon")
        check([zz_tip("hot_go_dorm_yard__" + l) for l in ("boys_dorm", "utahime_office", "courtyard")][::2] == ["To the Boys' Dormitory", "To the Courtyard"]
              and zz_hot("hot_go_dorm_yard__dorm") is None
              and path_words("utahime_office") == "To Utahime's Office" and path_words("girls_dorm") == "To the Girls' Dormitory",
              "hover labels read naturally: To the Boys' Dormitory, To the Courtyard, To Utahime's Office")
        _zz_log = []
    ## At every period: free, instant, the same arrival as a map trip.
    $ _zz_i = 0
    while _zz_i < len(PERIODS):
        python:
            zz_open_campus()
            period = PERIODS[_zz_i]
            day = 9
            here = "dorm"
            _zz_before = (day, period, stamina, ce)
            _zz_room, _zz_col = zz_exits_offered("dorm")
        call sb_do_path_boys_dorm
        python:
            _zz_log.append((PERIODS[_zz_i], here, (day, period, stamina, ce) == _zz_before, _zz_room, _zz_col,
                            night_allows("path_boys_dorm", 0)))
        call sb_do_path_courtyard
        python:
            _zz_log[-1] = _zz_log[-1] + (here,)
            _zz_i += 1
    python:
        check(all(r[1] == "boys_dorm" and r[2] and r[6] == "courtyard" for r in _zz_log),
              "taking an exit changes `here` and costs no time, stamina or energy, at every period", _zz_log)
        check(NIGHT_STRICT and _zz_log[-1][0] == "Night" and _zz_log[-1][3] == ["path_boys_dorm"] and _zz_log[-1][5] and _zz_log[-1][1] == "boys_dorm",
              "at Night under the strict rule the exit is still offered and still walks", _zz_log[-1])
        zz_open_campus()
        zz_place("dorm", "Night")
        check(night_is_night() and zz_action_value("hot_go_dorm__boys_dorm") == ("act", "path_boys_dorm") and zz_tip("hot_go_dorm__boys_dorm") == "To the Boys' Dormitory",
              "the Night's place view draws it as a live button (not 'Too late. Bed.')", (zz_action_value("hot_go_dorm__boys_dorm"), zz_tip("hot_go_dorm__boys_dorm")))
        zz_place("dorm_yard", "Night")
        ## (Before the second overhaul Yuji and Panda stood here at Night and
        ## covered some exits; the garden is empty at Night now. An exit that
        ## someone covers is in the icon column, as the rule has it.)
        _zz_room, _zz_col = zz_exits_offered("dorm_yard")
        check("path_boys_dorm" in _zz_room + _zz_col and "path_dorm" not in _zz_room + _zz_col
              and len(_zz_room) + len(_zz_col) == len(path_exits("dorm_yard")) <= 7
              and "night_bed" in [a[0] for a in rail_actions("dorm_yard")],
              "a hub at Night offers its exits beside Go to bed", (_zz_room, _zz_col))
        ## Explore mode.
        zz_open_campus()
        explore_mode = True
        here = "office"
        period = "Night"
        _zz_ex = zz_exits_offered("office")
    call sb_do_path_staff_yard
    python:
        _zz_h1 = here
    call sb_do_path_gojo_office
    python:
        check(_zz_ex == (["path_staff_yard"], []) and _zz_h1 == "staff_yard" and here == "gojo_office" and period == "Night",
              "explore mode: exits are offered and walk, and no door is locked there", (_zz_ex, _zz_h1, here))
        check([a[0] for a in place_actions("staff_yard")][:1] == ["explore_time"], "explore mode keeps its Time step beside the exits")
        explore_mode = False
        ## The arrival caption, as after a map trip.
        zz_open_campus()
        here = "courtyard"
        period = "Noon"
        ARRIVAL[0] = (day, period, here)
        ARRIVAL[1] -= 10
        renpy.show_screen("sb_place")
        zz_render(0.2)
        _zz_none = arrival_caption()
    call sb_do_path_school_yard
    python:
        zz_render(0.3)
        _zz_cap = arrival_caption()
        _zz_t = zz_texts("sb_place")
        check(_zz_none is None and here == "school_yard" and _zz_cap is not None and ARRIVAL[0] == (day, period, "school_yard")
              and any("School Courtyard" in s for s in _zz_t) and any(LOCATIONS["school_yard"]["desc"] in s for s in _zz_t),
              "walking shows the arrival caption of the new place (its name and its first-person line)", [s for s in _zz_t if "School" in s or "earth" in s])
        shot("arrival_school_yard", wait=0)
        ## The walk's `scene expression graded_bg()` cleared the picture this
        ## harness had shown under the tag bg and put up the new place's alone.
        check(len(renpy.get_showing_tags("master")) == 1 and "bg" not in renpy.get_showing_tags("master")
              and LOCATIONS["school_yard"]["bg"] == "bg school_yard" and renpy.has_image("bg school_yard", exact=True),
              "the walk replaces the picture with the new place's (bg school_yard: see arrival_school_yard.png)",
              (sorted(renpy.get_showing_tags("master")), LOCATIONS["school_yard"]["bg"]))

    ## A locked destination (D55).
    python:
        zz_open_campus()
        flags.discard("storehouse_access")
        zz_place("training_yard", "Noon")
        _zz_why = place_access("storehouse")[1]
        _zz_row = [r for r in path_exits("training_yard") if r["to"] == "storehouse"][0]
        check(_zz_why and _zz_row["locked_reason"] == _zz_why and _zz_row["label"] == _zz_why,
              "an exit to a locked place: path_exits gives the lock's reason", _zz_row)
        check(_zz_row["icon"] == "place_storehouse", "path_exits keeps the destination's icon for a locked exit (only the hotspot is drawn as the lock)", _zz_row["icon"])
        check(zz_tip("hot_go_training_yard__storehouse") == _zz_why, "its hover label is the lock's reason", zz_tip("hot_go_training_yard__storehouse"))
        ## The second overhaul (D60; docs/UI2_PINS.md Part 2b): a rule that holds
        ## in both kinds of place. Where the place draws buttons the locked
        ## exit is drawn as the lock icon, as before. Where the picture itself
        ## is clicked (the exit has a traced shape: hot_shapes_for) no icon is
        ## drawn for either exit; there the lock is the reason its square and
        ## its shape both say, and neither of the two can be pressed, while the
        ## open exit's two still walk.
        _zz_shaped = getattr(store, "hot_shapes_for", lambda loc: {})("training_yard")
        if "go_training_yard__storehouse" in _zz_shaped and "go_training_yard__dojo" in _zz_shaped:
            _zz_drawn = (zz_icons(zz_hot("hot_go_training_yard__storehouse")) == [] and zz_icons(zz_hot("hot_go_training_yard__dojo")) == []
                         and zz_tip("hotshape_go_training_yard__storehouse") == _zz_why
                         and zz_action_value("hot_go_training_yard__storehouse") is None
                         and zz_action_value("hotshape_go_training_yard__storehouse") is None
                         and zz_action_value("hot_go_training_yard__dojo") == zz_action_value("hotshape_go_training_yard__dojo") == ("act", "path_dojo"))
        else:
            _zz_drawn = ("lock" in zz_icons(zz_hot("hot_go_training_yard__storehouse")) and "place_storehouse" not in zz_icons(zz_hot("hot_go_training_yard__storehouse"))
                         and "place_dojo" in zz_icons(zz_hot("hot_go_training_yard__dojo")))
        check(_zz_drawn,
              "it is drawn as the lock icon (an open exit keeps its place's icon)", zz_icons(zz_hot("hot_go_training_yard__storehouse")))
        check(zz_alpha("hot_go_training_yard__storehouse") == 0.45 and zz_alpha("hot_go_training_yard__dojo") == 1.0,
              "a locked exit's icon is drawn dim (alpha 0.45); an open one is not",
              (zz_alpha("hot_go_training_yard__storehouse"), zz_alpha("hot_go_training_yard__dojo")))
        shot("locked_exit")
        _zz_before = (day, period, here, stamina)
        _zz_said = []
        _zz_say0 = renpy.say
        renpy.say = lambda who, what, *a, **k: _zz_said.append(what)
    call sb_do_path_storehouse
    python:
        renpy.say = _zz_say0
        check((day, period, here, stamina) == _zz_before and not _zz_said, "clicking it does nothing: I stay, no time passes, nothing is said", (here, _zz_said))
        ## In the column it still reads the reason: as the registry gives the
        ## row, and with someone standing right in front of the exit.
        _zz_reg = [a for a in registered_place_actions("training_yard") if a[0] == "path_storehouse"]
        check(len(_zz_reg) == 1 and _zz_reg[0][1] == _zz_why and _zz_reg[0][3] == 0,
              "the locked exit's place action reads the lock's reason (registered_place_actions)", _zz_reg)
        _zz_vpr0 = view_person_rects
        store.view_person_rects = zz_cover_storehouse
        try:
            _zz_col = [r for r in rail_rows("training_yard") if r[0] == ("act", "path_storehouse")]
            zz_place("training_yard", "Noon")
            check(len(_zz_col) == 1 and _zz_col[0][3] == _zz_why and "path_storehouse" not in zz_exits_offered("training_yard")[0]
                  and zz_hot("hot_go_training_yard__storehouse") is None and zz_tip("rail_path_storehouse") == _zz_why,
                  "with someone in front of it the locked exit is a column tile, and its hover label is still the lock's reason",
                  (_zz_col, zz_tip("rail_path_storehouse")))
        finally:
            store.view_person_rects = _zz_vpr0
        ## However a reader takes the row, it reads the lock (and the open door again afterwards).
        _zz_reads = zz_row_reads()
        check(set(_zz_reads[0]) == set([_zz_why]) and set(_zz_reads[1]) == set(["lock"]) and _zz_reads[2],
              "the registry rows read the lock through row[key], row.get, row.items, row.values, row.copy and a dict(row) copy alike", _zz_reads)
        flag("storehouse_access")
        check(path_exits("training_yard")[2]["locked_reason"] == "" and path_exits("training_yard")[2]["label"] == "To the Storehouse"
              and set(zz_row_reads()[0]) == set(["To the Storehouse"]) and set(zz_row_reads()[1]) == set(["place_storehouse"]),
              "once the door opens the exit reads To the Storehouse again", path_exits("training_yard")[2])
        ## The other locks read their own reasons.
        period = "Night"
        _zz_n = dict((r["to"], r["locked_reason"]) for r in path_exits("staff_yard"))
        check(all(_zz_n[l] == place_access(l)[1] and _zz_n[l] for l in ("office", "utahime_office", "gojo_office")) and not _zz_n["dorm_yard"],
              "at Night the three office exits on the staff steps are locked, each with its own reason; the way out is open", _zz_n)
        period = "Noon"
        ## The longest lock (the one met every evening from day 1): the girls'
        ## dormitory after dark, from the Dormitory Garden.
        flags.discard("invited_girls_dorm")
        zz_place("dorm_yard", "Evening")
        _zz_why = place_access("girls_dorm")[1]
        check(_zz_why and zz_tip("hot_go_dorm_yard__girls_dorm") == _zz_why and zz_action_value("hot_go_dorm_yard__girls_dorm") is None,
              "in the evening the girls' dormitory exit reads its lock's reason (%d characters)" % len(_zz_why), zz_tip("hot_go_dorm_yard__girls_dorm"))
        _zz_hr, _zz_hit = zz_lock_label("dorm_yard", "girls_dorm")
        _zz_own = zz_rect("sb_place", "hot_go_dorm_yard__girls_dorm")
        check(_zz_hr is not None and _zz_hr[0] >= 0 and _zz_hr[1] >= 0 and _zz_hr[0] + _zz_hr[2] <= 1920 and _zz_hr[1] + _zz_hr[3] <= 1080
              and _zz_hr[2] <= 520 and not any(hot_overlap(_zz_hr, ln) for ln in HOT_LANES if ln[0] >= 1300),
              "its hover label fits: on screen, at most 520 wide, clear of the toast lane (hover check: needs the pointer)", _zz_hr)
        check(_zz_hr is not None and _zz_own is not None and not _zz_hit and not hot_overlap(_zz_hr, _zz_own)
              and not hot_overlap(_zz_hr, PATH_CAPTION_BOX),
              "and it opens over empty picture: beside or under its own icon, hiding none of the garden's other exits, clear of the arrival caption",
              (_zz_hr, _zz_own, _zz_hit))
        shot("locked_girls_dorm_hover", wait=0)
        _zz_before = (day, period, here, stamina)
    call sb_do_path_girls_dorm
    python:
        check((day, period, here, stamina) == _zz_before, "and clicking it leaves me in the garden", here)
        flag("invited_girls_dorm")
        period = "Noon"
        renpy.hide_screen("sb_place")

    ## --- 3. where exits sit -------------------------------------------------------------------------
    python:
        _zz_x0, _zz_y0, _zz_x1, _zz_y1 = HOT_BOUNDS
        _zz_out, _zz_lane, _zz_near, _zz_close, _zz_live = [], [], [], [], []
        for _zz_f in LOCATIONS:
            _zz_rows = path_exits(_zz_f)
            for _zz_r in _zz_rows:
                _zz_id = path_spot_id(_zz_f, _zz_r["to"])
                _zz_x, _zz_y = _zz_r["x"], _zz_r["y"]
                if not (40 <= _zz_x <= 1700 and 180 <= _zz_y <= 1000 and (_zz_x0, _zz_y0, _zz_x1, _zz_y1) == (40, 180, 1700, 1000)):
                    _zz_out.append((_zz_id, _zz_x, _zz_y))
                if any(hot_overlap(hot_rect(_zz_x, _zz_y), ln) for ln in HOT_LANES):
                    _zz_lane.append((_zz_id, _zz_x, _zz_y))
                for _zz_p in zz_keep_clear(_zz_f):
                    if (_zz_x - _zz_p[0]) ** 2 + (_zz_y - _zz_p[1]) ** 2 < PATH_CLEAR ** 2:
                        _zz_near.append((_zz_id, _zz_p))
                for _zz_r2 in _zz_rows:
                    if _zz_r2["to"] > _zz_r["to"] and abs(_zz_r2["x"] - _zz_x) < 96 and abs(_zz_r2["y"] - _zz_y) < 96:
                        _zz_close.append((_zz_id, _zz_r2["to"]))
                for _zz_hid, _zz_hx, _zz_hy in zz_room_spots(_zz_f):
                    _zz_d = ((_zz_x - _zz_hx) ** 2 + (_zz_y - _zz_hy) ** 2) ** 0.5
                    if _zz_d < 120:
                        _zz_live.append((_zz_id, _zz_hid, int(_zz_d)))
        check(not _zz_out, "every exit point is inside x 40 to 1700, y 180 to 1000", _zz_out)
        check(not _zz_lane and len(HOT_LANES) == 2, "no exit point lies in the toast lane or the banner lane", _zz_lane)
        ## K3: no hand copy of the points. What an exit keeps clear of is where
        ## the room's own hotspots sit now (path_keep_clear once the scaffold
        ## has it; zz_keep_clear above), and that list is checked against the
        ## live points, not against numbers written here.
        check(not _zz_near and PATH_CLEAR == 120,
              "no exit is within PATH_CLEAR (120 px) of a point its place keeps clear", _zz_near)
        _zz_stale = [(l, sorted(set((x, y) for i, x, y in zz_room_spots(l))), sorted(zz_keep_clear(l)))
                     for l in LOCATIONS if sorted(set((x, y) for i, x, y in zz_room_spots(l))) != sorted(set(zz_keep_clear(l)))]
        check(not _zz_stale, "what each place keeps clear is exactly where its own hotspots sit now (the sidecars applied)", _zz_stale)
        if not callable(getattr(store, "path_keep_clear", None)):
            _zz_old = [l for l in LOCATIONS if sorted(set((x, y) for i, x, y in zz_room_spots(l))) != sorted(PATH_KEEP_CLEAR.get(l, ()))]
            note("PATH_KEEP_CLEAR (the code's fallback table, until path_keep_clear reads the live points)",
                 "agrees with the live points" if not _zz_old else "is out of date for %s" % ", ".join(_zz_old))
        check(not _zz_close, "no two exits of one place overlap (their 96 px rings are clear of each other)", _zz_close)
        check(not _zz_live, "no exit is within 120 px of a hotspot of its room, as registered and placed now", _zz_live)
        ## K3: the rule, not the point: clear of the machine, inside the frame.
        _zz_vend = [(x, y) for i, x, y in zz_room_spots("courtyard") if i == "spot_vend"]
        _zz_pc = [(x, y) for i, x, y in zz_room_spots("dorm") if i == "computer"]
        check(len(_zz_vend) == 1 and len(_zz_pc) == 1
              and all(zz_dist((r["x"], r["y"]), _zz_vend[0]) >= PATH_CLEAR and zz_in_frame(r["x"], r["y"]) for r in path_exits("courtyard"))
              and all(zz_dist((r["x"], r["y"]), _zz_pc[0]) >= PATH_CLEAR and zz_in_frame(r["x"], r["y"]) for r in path_exits("dorm")),
              "the courtyard's exits are clear of the vending machine and inside the frame; my door is clear of the laptop",
              (path_exits("courtyard"), _zz_vend, path_exits("dorm"), _zz_pc))
        ## The hubs' exits sit on their pictures, not in a row along the top.
        _zz_rows = dict((h, sorted(r["y"] for r in path_exits(h))) for h in ZZ_HUBS)
        check(all(len([y for y in ys if y < 300]) <= 1 and len(set(ys)) >= 3 for ys in _zz_rows.values()),
              "in each of the five hubs the exits are spread over the picture (at most one above y 300, at least three heights)", _zz_rows)
        ## A two-line objective banner ends near y 233: the exits along the top stay under it.
        check(all(r["y"] - 36 >= 234 for f in LOCATIONS for r in path_exits(f) if 364 <= r["x"] <= 1336 and r["y"] < 400),
              "an exit under the banner starts below a two-line banner (y 234)")
        ## The arrival caption lies over the picture for my first seconds in
        ## a place: no exit sits under it (and the box the validator keeps
        ## clear really holds the caption of every place).
        _zz_boxes = dict((l, zz_caption_box(l)) for l in LOCATIONS)
        _zz_big = [(l, b) for l, b in sorted(_zz_boxes.items())
                   if b[0] + b[2] > PATH_CAPTION_BOX[0] + PATH_CAPTION_BOX[2] or b[1] + b[3] > PATH_CAPTION_BOX[1] + PATH_CAPTION_BOX[3]]
        check(PATH_CAPTION_BOX == (40, 100, 744, 160) and not _zz_big,
              "every place's arrival caption fits inside PATH_CAPTION_BOX (the tallest is %d px, the widest %d)"
              % (max(b[3] for b in _zz_boxes.values()), max(b[2] for b in _zz_boxes.values())), _zz_big)
        _zz_under = [(f, r["to"], r["x"], r["y"]) for f in LOCATIONS for r in path_exits(f)
                     if hot_overlap((r["x"] - 48, r["y"] - 48, 96, 96), PATH_CAPTION_BOX)]
        check(not _zz_under, "no exit sits under the arrival caption (its 96 px ring is clear of the caption's box)", _zz_under)
        _zz_bad, _zz_hubrects = [], {}
        for _zz_h in ZZ_HUBS:
            zz_arrive(_zz_h, "Noon")
            shot("arrival_" + _zz_h, wait=0)
            _zz_hubrects[_zz_h] = dict((t, zz_rect("sb_place", "hot_" + path_spot_id(_zz_h, t))) for t in path_neighbours(_zz_h))
            _zz_bad += [(_zz_h, t, r) for t, r in sorted(_zz_hubrects[_zz_h].items()) if r is None or hot_overlap(r, zz_caption_box(_zz_h))]
        check(not _zz_bad and len(_zz_hubrects["trailhead"]) == len(PATH_EXITS["trailhead"]) >= 4,
              "on arrival (the caption up) every exit button of each of the five hubs, as drawn, is clear of it", (_zz_bad, _zz_hubrects["trailhead"]))
        ARRIVAL[1] -= 10
        renpy.hide_screen("sb_place")
        ## A locked exit's label (the lock's reason, up to two lines) hides no
        ## other exit of its hub and stays off the arrival caption's panel,
        ## whichever side of the icon it opens on.
        _zz_bad, _zz_seen = [], {}
        _zz_keep = set(flags)
        for _zz_h, _zz_t, _zz_per in (("dorm_yard", "girls_dorm", "Evening"), ("training_yard", "storehouse", "Noon"),
                                      ("staff_yard", "office", "Night"), ("staff_yard", "utahime_office", "Night"),
                                      ("staff_yard", "gojo_office", "Night")):
            flags.discard("invited_girls_dorm")
            flags.discard("storehouse_access")
            zz_place(_zz_h, _zz_per)
            _zz_hr, _zz_hit = zz_lock_label(_zz_h, _zz_t)
            _zz_own = zz_rect("sb_place", "hot_" + path_spot_id(_zz_h, _zz_t))
            _zz_seen[_zz_t] = _zz_hr
            if not (path_locked(_zz_t) and _zz_hr is not None and _zz_own is not None and not _zz_hit
                    and not hot_overlap(_zz_hr, _zz_own) and not hot_overlap(_zz_hr, PATH_CAPTION_BOX)
                    and _zz_hr[0] >= 0 and _zz_hr[1] >= 0 and _zz_hr[0] + _zz_hr[2] <= 1920 and _zz_hr[1] + _zz_hr[3] <= 1080):
                _zz_bad.append((_zz_h, _zz_t, path_locked(_zz_t), _zz_hr, _zz_own, _zz_hit))
            shot("locked_label_" + _zz_t, wait=0)
        flags.clear(); flags.update(_zz_keep)
        period = "Noon"
        renpy.hide_screen("sb_place")
        check(not _zz_bad, "each of the five exits that can be locked: its lock's reason, hovered, is on screen, hides no other exit of its hub "
              "and is clear of the arrival caption's panel (hover check: needs the pointer)", _zz_bad)
        note("where each locked exit's label was drawn (x, y, w, h)", _zz_seen)
        ## And open: in every hub, with nobody on stage, no exit's hover
        ## label covers another exit of that hub.
        _zz_bad, _zz_n = [], 0
        store.who_is_here = zz_crowd
        ZZ_CROWD[0] = 0
        try:
            for _zz_h in [path_hub(a["key"]) for a in AREAS]:
                zz_place(_zz_h, "Noon")
                for _zz_t in path_neighbours(_zz_h):
                    _zz_hr, _zz_hit = zz_lock_label(_zz_h, _zz_t)
                    _zz_n += 1
                    if (_zz_hr is None or _zz_hit or _zz_hr[0] < 0 or _zz_hr[1] < 0
                            or _zz_hr[0] + _zz_hr[2] > 1920 or _zz_hr[1] + _zz_hr[3] > 1080):
                        _zz_bad.append((_zz_h, _zz_t, _zz_hr, _zz_hit))
        finally:
            store.who_is_here = zz_who_is_here0
        renpy.hide_screen("sb_place")
        ## K3: counted from the table.
        check(not _zz_bad and _zz_n == sum(len(path_neighbours(path_hub(a["key"]))) for a in AREAS) > 0, "in the six hubs every exit's hover label (%d of them) is on screen and covers no other exit of its hub "
              "(hover check: needs the pointer)" % _zz_n, _zz_bad)
        ## Four people on stage: every exit is still offered, once.
        store.who_is_here = zz_crowd
        _zz_bad, _zz_moved = [], 0
        try:
            for _zz_n in (0, 1, 2, 3, 4, 5):
                ZZ_CROWD[0] = _zz_n
                for _zz_per in ("Noon", "Night"):
                    period = _zz_per
                    for _zz_f in LOCATIONS:
                        _zz_room, _zz_col = zz_exits_offered(_zz_f)
                        _zz_want = sorted("path_" + t for t in path_neighbours(_zz_f))
                        if sorted(_zz_room + _zz_col) != _zz_want or set(_zz_room) & set(_zz_col):
                            _zz_bad.append((_zz_n, _zz_per, _zz_f, _zz_room, _zz_col))
                        if _zz_n == 4 and _zz_per == "Noon":
                            _zz_moved += len(_zz_col)
            ZZ_CROWD[0] = 4
            period = "Noon"
            check(not _zz_bad, "with 0 to 5 people in the room, at Noon and at Night, every exit of every place is offered in the room "
                  "or in the column, never neither and never both", _zz_bad[:4])
            check(_zz_moved > 0, "(with four people some exits do move to the column: %d of %d)" % (_zz_moved, sum(len(v) for v in PATH_EXITS.values())))
            _zz_tiles = max(len(rail_rows(f)) for f in LOCATIONS)
            check(_zz_tiles <= RAIL_MAX and RAIL_MAX == 8, "even then no place needs more than one column of tiles (RAIL_MAX, 8)", _zz_tiles)
            zz_place("courtyard", "Noon")
            _zz_room, _zz_col = zz_exits_offered("courtyard")
            check(all(zz_hot("hot_go_courtyard__" + a[5:]) is not None for a in _zz_room)
                  and all(zz_hot("rail_" + a) is not None and zz_action_value("rail_" + a) == ("act", a) for a in _zz_col)
                  and not any(zz_hot("rail_" + a) is not None for a in _zz_room),
                  "the courtyard with four people: the place view draws each exit once, in the picture or as a column tile", (_zz_room, _zz_col))
            check(all(zz_tip("rail_" + a) == path_words(a[5:]) and icon_for("act", a) in zz_icons(zz_hot("rail_" + a)) for a in _zz_col),
                  "a column tile keeps the exit's hover label and the destination's icon", [(a, zz_tip("rail_" + a)) for a in _zz_col])
            shot("four_people_courtyard")
        finally:
            store.who_is_here = zz_who_is_here0
            ZZ_CROWD[0] = 0

    ## --- 4. the five new places ---------------------------------------------------------------------
    python:
        zz_open_campus()
        check(all(h in LOCATIONS and LOCATIONS[h]["name"] == ZZ_HUB_NAMES[h] and LOCATIONS[h]["indoor"] is False
                  and LOCATIONS[h]["bg"] == "bg " + h and h in LOC_ORDER for h in ZZ_HUBS),
              "the five new places are LOCATIONS rows with D53's names, outdoors", [LOCATIONS[h]["name"] for h in ZZ_HUBS if h in LOCATIONS])
        check(all([a["key"] for a in AREAS if h in a["places"]] == [ZZ_HUB_AREA[h]] and AREA_BY_KEY[ZZ_HUB_AREA[h]]["places"][0] == h for h in ZZ_HUBS)
              and AREA_BY_KEY["heart"]["places"] == ["gate", "courtyard"],
              "each is in exactly one area, first in its list; the heart keeps the courtyard as its hub")
        _zz_bad = []
        flags.clear()
        flag("settled_in")
        for _zz_p in PERIODS:
            period = _zz_p
            for _zz_h in ZZ_HUBS + ("courtyard",):
                if place_access(_zz_h) != (True, "", "") or can_enter(_zz_h) != (True, ""):
                    _zz_bad.append((_zz_p, _zz_h))
        check(not _zz_bad, "each is always enterable: at every period, with no flag set", _zz_bad)
        zz_open_campus()
        check(all(LOCATIONS[h]["desc"] and not zz_re.search(r"\b(you|your|you're)\b", LOCATIONS[h]["desc"] + LOCATIONS[h]["name"], zz_re.I)
                  and zz_re.search(r"\b(I|me|my)\b", LOCATIONS[h]["desc"]) for h in ZZ_HUBS),
              "each has a first-person description", [LOCATIONS[h]["desc"] for h in ZZ_HUBS])
        ## The test picture (the asset overlay) and the stand-in.
        _zz_real = [world_hub_bg(h) for h in ZZ_HUBS]
        check(_zz_real == ["images/bg/%s.png" % h for h in ZZ_HUBS] and all(renpy.has_image("bg " + h, exact=True) for h in ZZ_HUBS),
              "with a picture dropped in (the asset overlay), bg <hub> is images/bg/<hub>.png", _zz_real)
        renpy.loadable = zz_no_hubs
        try:
            _zz_stand = [world_hub_bg(h) for h in ZZ_HUBS]
        finally:
            renpy.loadable = zz_loadable0
        check(all(isinstance(d, renpy.display.transform.Transform) for d in _zz_stand)
              and len(set((v[0], v[1], v[4], v[5]) for v in WORLD_HUB_STANDINS.values())) == 5
              and all(v[0] in ("courtyard.png", "forest.png") and zz_loadable0("images/bg/" + v[0]) for v in WORLD_HUB_STANDINS.values()),
              "without one, bg <hub> is its stand-in: the courtyard or the forest, and no two alike", sorted(WORLD_HUB_STANDINS.items()))
    $ _zz_i = 0
    while _zz_i < len(ZZ_HUBS):
        python:
            _zz_h = ZZ_HUBS[_zz_i]
            zz_place(_zz_h, "Noon")
            _zz_ok1 = sorted(h["id"] for h in hot_spots_for(_zz_h)) == sorted(path_spot_id(_zz_h, t) for t in path_neighbours(_zz_h)) \
                and all(zz_hot("hot_" + path_spot_id(_zz_h, t)) is not None for t in path_neighbours(_zz_h))
            shot("hub_%s_test_picture" % _zz_h)
            ## The stand-in, under the same place view (the place view draws
            ## graded_bg() itself, so that is what hands it the stand-in).
            _zz_graded0 = graded_bg
            store.graded_bg = lambda loc=None, per=None: _zz_stand[_zz_i]
            try:
                zz_place(_zz_h, "Noon")
                _zz_ok2 = "?" not in "".join(zz_texts("sb_place")) and len(hot_spots_for(_zz_h)) == len(path_neighbours(_zz_h))
                shot("hub_%s_standin" % _zz_h)
            finally:
                store.graded_bg = _zz_graded0
            check(_zz_ok1 and _zz_ok2, "%s renders with its test picture and with its stand-in, every exit a button in the picture" % _zz_h)
            _zz_i += 1
    python:
        renpy.hide_screen("sb_place")
        ## Pins on the area views.
        _zz_bad = []
        for _zz_h in ZZ_HUBS + ("courtyard",):
            here = "dorm" if _zz_h != "dorm_yard" else "gate"
            renpy.hide_screen("sb_map")
            renpy.show_screen("sb_map", area=area_of(_zz_h))
            zz_render(0.5)
            _zz_w = renpy.get_widget("sb_map", "row_" + _zz_h)
            _zz_x, _zz_y = map_spots(area_of(_zz_h))[_zz_h]
            _zz_fr = MAP_PIN_FRAME
            if (_zz_w is None or renpy.run(_zz_w.action) != ("go", _zz_h) or LOCATIONS[_zz_h]["name"] not in zz_texts("sb_map")
                    or not (_zz_fr[0] <= _zz_x <= _zz_fr[2] and _zz_fr[1] <= _zz_y <= _zz_fr[3])
                    or (_zz_h in ZZ_HUBS and "area_" + area_of(_zz_h) not in zz_icons(_zz_w))):
                _zz_bad.append(_zz_h)
            shot("area_" + area_of(_zz_h), wait=0)
        check(not _zz_bad, "each hub is a pin on its area view: it walks there, shows its name, and wears its area's icon", _zz_bad)
        renpy.hide_screen("sb_map")
        here = "dorm"
        ## make_bg_workflow.py accepts the five names (built without writing or copying anything).
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_code = ("import sys, shutil; sys.path.insert(0, 'tools'); import make_bg_workflow as m; "
                    "shutil.copy = lambda *a, **k: None; "
                    "names = %r; wf, n = m.build(list(names)); "
                    "assert n == 10 and not (set(names) & m.INTERIORS) and all(m.bg_prompt(x) for x in names); print('OK', n)" % (ZZ_HUBS,))
        _zz_py = [p for p in ("/usr/bin/python3", "/opt/homebrew/bin/python3", "/usr/local/bin/python3") if os.path.exists(p)]
        _zz_prompts = bool(_zz_root) and all(os.path.exists(os.path.join(_zz_root, "tools", "bgs", "prompts", h + ".txt")) for h in ZZ_HUBS)
        check(_zz_prompts, "tools/bgs/prompts/ holds a prompt for each of the five hubs")
        if _zz_py and _zz_root:
            _zz_env = dict(os.environ)
            for _zz_k in ("PYTHONHOME", "PYTHONPATH"):
                _zz_env.pop(_zz_k, None)
            _zz_p = zz_subprocess.run([_zz_py[0], "-c", _zz_code], cwd=_zz_root, capture_output=True, text=True, env=_zz_env)
            check(_zz_p.returncode == 0 and _zz_p.stdout.strip() == "OK 10",
                  "make_bg_workflow.py accepts the five new names: ten pictures, outdoor style", (_zz_p.stdout[-200:], _zz_p.stderr[-400:]))
        else:
            note("make_bg_workflow.py accepts the five new names", "no python3 found to run it from the harness; run it by hand")

    ## --- 5. the campus map --------------------------------------------------------------------------
    python:
        zz_open_campus()
        here = "courtyard"
        ZZ_CROWD[0] = 5
        store.who_is_here = zz_crowd
        _zz_mw0, _zz_nm0 = map_waiting, night_marks
        store.map_waiting = zz_two
        store.night_marks = zz_all_moons
        try:
            renpy.hide_screen("sb_map")
            renpy.show_screen("sb_map")
            zz_render(0.3)
            _zz_rects = dict((a["key"], zz_rect("sb_map", "area_" + a["key"])) for a in AREAS)
            _zz_full = [a["key"] for a in AREAS
                        if len(zz_faces(renpy.get_widget("sb_map", "area_" + a["key"]))) == 3
                        and any(s.startswith("◆") for s in zz_strings(renpy.get_widget("sb_map", "area_" + a["key"])))
                        and any(s.startswith("+") for s in zz_strings(renpy.get_widget("sb_map", "area_" + a["key"])))]
            check(len(_zz_full) == 6, "(fixture) every marker carries three faces, '+2', a gold mark and the moon", _zz_full)
            _zz_hit = [(a, b) for a in _zz_rects for b in _zz_rects if a < b and zz_overlap(_zz_rects[a], _zz_rects[b])]
            check(all(_zz_rects.values()) and not _zz_hit, "the campus map: no two markers overlap with three faces and a gold mark on each", (_zz_hit, _zz_rects))
            check(all(r[2] == 240 and r[3] == 96 for r in _zz_rects.values()) and all(_zz_rects[k] == map_area_rect(k) for k in _zz_rects),
                  "every area marker is 240 by 96 (it was 300 by 132)", _zz_rects)
            _zz_other = [zz_rect("sb_map", w) for w in ("map_campus", "map_tokyo", "map_stay")]
            check(all(_zz_other) and not [(k, o) for k, r in _zz_rects.items() for o in _zz_other if zz_overlap(r, o)]
                  and all(r[1] >= 96 for r in _zz_rects.values()),
                  "no marker touches the top row, the Campus/Tokyo switch or Stay here", _zz_rects)
            _zz_heart = zz_strings(renpy.get_widget("sb_map", "area_heart"))
            check(any("I'M HERE" in s for s in _zz_heart) and LOCATIONS and AREA_BY_KEY["heart"]["name"] in _zz_heart,
                  "the marker I stand in still reads I'M HERE, under its one-line name", _zz_heart)
            shot("map_markers_full")
            zz_worst("sb_map", hover="area_mountain")
        finally:
            store.who_is_here = zz_who_is_here0
            store.map_waiting = _zz_mw0
            store.night_marks = _zz_nm0
            ZZ_CROWD[0] = 0
        _zz_mx, _zz_my = AREA_BY_KEY["mountain"]["anchor"]
        _zz_box = MAP_MOUNTAIN_BOX
        _zz_c = _zz_rects["mountain"]
        ## K3: the box is the picture's own number: game/layout/map_campus.json
        ## ("mountain_box") when the map has one, else the code's.
        _zz_side = rule_layout("map_campus").get("mountain_box")
        if isinstance(_zz_side, (zz_builtins.list, zz_builtins.tuple)) and len(_zz_side) == 4:
            _zz_box = zz_builtins.tuple(_zz_side)
        check(len(_zz_box) == 4 and _zz_box[0] < _zz_box[2] and _zz_box[1] < _zz_box[3]
              and 0 <= _zz_box[0] and _zz_box[2] <= 1920 and 0 <= _zz_box[1] and _zz_box[3] <= 1080
              and _zz_box[0] <= _zz_mx <= _zz_box[2] and _zz_box[1] <= _zz_my <= _zz_box[3]
              and (_zz_c[0] + _zz_c[2] // 2, _zz_c[1] + _zz_c[3] // 2) == (_zz_mx, _zz_my),
              "the Mountain marker's centre lies on the mountain: inside the box measured on the campus map's picture",
              (_zz_mx, _zz_my, _zz_c))
        ## The lake stays unmarked.
        check(not [a["key"] for a in AREAS if abs(a["anchor"][0] - 640) < 128 + 120 and abs(a["anchor"][1] - 225) < 56 + 48],
              "no marker sits over the lake any more (the lake is unmarked)")
        renpy.hide_screen("sb_map")

    ## --- 6. "Classroom Building" and "Closer: after roll call" appear nowhere ---------------------------
    python:
        zz_open_campus()
        _zz_seen = []
        check(LOCATIONS["classroom"]["name"] == "Classroom" and "classroom" in LOCATIONS and LOCATIONS["classroom"]["bg"] == "bg classroom",
              "the place's name is Classroom; its key and picture are as they were")
        ## The map: level 1 (the marker's hover lists the rooms), the school area, the pins' hovers.
        here = "dorm"
        renpy.hide_screen("sb_map")
        renpy.show_screen("sb_map")
        zz_render(0.2)
        _zz_seen += zz_texts("sb_map") + zz_tooltips("sb_map")
        _zz_tip1 = map_area_tip("school")[0]
        renpy.hide_screen("sb_map")
        renpy.show_screen("sb_map", area="school")
        zz_render(0.5)
        _zz_seen += zz_texts("sb_map") + zz_tooltips("sb_map")
        check("Classroom" in zz_texts("sb_map") and _zz_tip1.startswith("School Courtyard · Classroom · Cafeteria"),
              "the map prints Classroom on its pin and in the School Building's hover", _zz_tip1)
        renpy.hide_screen("sb_map")
        ## The place view: the classroom's arrival caption, the school courtyard's exits.
        period = "Morning"
        day = 9
        here = "classroom"
        ARRIVAL[0] = None
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        renpy.show_screen("sb_place")
        zz_render(0.4)
        _zz_seen += zz_texts("sb_place") + zz_tooltips("sb_place")
        check("Classroom" in zz_texts("sb_place"), "the place view's arrival caption reads Classroom", [s for s in zz_texts("sb_place") if "lass" in s])
        zz_place("school_yard")
        _zz_seen += zz_texts("sb_place") + zz_tooltips("sb_place")
        check("To the Classroom" in zz_tooltips("sb_place"), "the exit's hover label reads To the Classroom")
        renpy.hide_screen("sb_place")
        ## The journal: the People grid and its hovers, Megumi's and Nobara's pages (their usual places), before and after roll call.
        _zz_keep = (set(flags), set(done_events))
        for _zz_before_rc in (True, False):
            if _zz_before_rc:
                flags.discard("roll_call")
                done_events.discard("st_roll_call")
                flags.discard("sunmall_done")
                for _zz_e in [e["label"] for e in EVENTS if e["kind"] == "hangout"]:
                    done_events.discard(_zz_e)
            for _zz_sel in (None, "megumi", "nobara", "yuji"):
                renpy.hide_screen("journal")
                renpy.show_screen("journal", "people")
                zz_render(0.15)
                _zz_js = renpy.get_screen("journal").scope["js"]
                _zz_js["sel"] = _zz_sel
                _zz_js["psub"] = "story"
                zz_render(0.2)
                _zz_seen += zz_texts("journal") + zz_tooltips("journal")
                if _zz_before_rc and _zz_sel == "megumi":
                    _zz_page = zz_texts("journal")
                    shot("journal_megumi_before_roll_call", wait=0)
            if _zz_before_rc:
                check(not rule_hangout_gate(dict(kind="hangout")) and jr_closer("megumi") == ""
                      and not [t for t in _zz_page if "Closer" in t] and [t for t in _zz_page if t.startswith("After roll call")],
                      "before roll call a person's page shows no Closer line at all; the NEXT row keeps After roll call",
                      [t for t in _zz_page if "loser" in t or "roll call" in t])
                _zz_seen += [usual_places(w) for w in ROSTER_ORDER] + [jr_card_tip(w) for w in ROSTER_ORDER] + [jr_closer(w) for w in ROSTER_ORDER]
            flags.clear(); flags.update(_zz_keep[0])
            done_events.clear(); done_events.update(_zz_keep[1])
        renpy.hide_screen("journal")
        check(jr_closer("megumi") == unlock_line("megumi") and jr_closer("megumi").startswith("Closer: "),
              "after roll call the Closer line is back as it was", jr_closer("megumi"))
        _zz_seen += [usual_places(w) for w in ROSTER_ORDER] + [LOCATIONS[l]["name"] for l in LOCATIONS] + [objective_text() or ""]
        check(len(_zz_seen) > 300 and not [s for s in _zz_seen if "Classroom Building" in s],
              "'Classroom Building' appears nowhere on screen (the map, the place view and the journal: %d strings read)" % len(_zz_seen),
              [s for s in _zz_seen if "Classroom Building" in s][:3])
        check(not [s for s in _zz_seen if "closer: after roll call" in s.lower()],
              "'Closer: after roll call' appears nowhere", [s for s in _zz_seen if "closer: after roll call" in s.lower()][:3])

    ## --- 7. people in the hubs; what runs outside this harness --------------------------------------------
    python:
        zz_open_campus()
        _zz_in = {}
        for _zz_d in (9, 13):                     ## a Tuesday and a Saturday
            day = _zz_d
            roll_gojo()
            for _zz_p in PERIODS:
                for _zz_h in ZZ_HUBS + ("courtyard",):
                    for _zz_w in ROSTER_ORDER:
                        if _zz_w != "gojo" and char_location(_zz_w, _zz_p) == _zz_h:
                            _zz_in.setdefault(_zz_h, []).append((weekday(), _zz_p, _zz_w))
        ## The second UI overhaul (4.3; U0b): Megumi's weekend Morning is his
        ## own room now (it was the Mountain Path), and the garden's people at
        ## Night went home: the garden keeps Yuji, on weekend Evenings, and
        ## the Mountain Path has nobody by routine until the places off it
        ## bring people past (U0c1). No yard holds more than two.
        _zz_n = dict((h, len(set(w for d, p, w in _zz_in.get(h, [])))) for h in ZZ_HUBS)
        check(all(n <= 2 for n in _zz_n.values()) and all(_zz_n[h] >= 1 for h in ZZ_HUBS if h != "trailhead")
              and [x for x in _zz_in.get("dorm_yard", []) if x[1] == "Night"] == [],
              "no yard has more than two people in its week, and four of the five have someone (D57; "
              "the Mountain Path has %d, the garden nobody at Night)" % _zz_n["trailhead"], _zz_in)
        note("who stands in the hubs", _zz_in)
        note("their captions", "; ".join("%s in %s: %r" % (w, h, ambient_of(w, h)[0]) for h in ZZ_HUBS for w in sorted(set(x[2] for x in _zz_in.get(h, [])))))
        check(not [e["label"] for e in EVENTS if e["who"] and e["loc"]],
              "no written scene asks for a person at a place (no ev() has both who and loc), so no move can lose one")
        ## What each old place offered that needs the place (an activity with
        ## a `loc`): the person can still be found somewhere it is offered.
        ## After checkpoint D Panda and Toge left the common room in the
        ## Evening for the library: the second list is theirs. Panda's Night
        ## left it for the garden after that (the same pair covers it).
        ## The second UI overhaul (4.3; U0b): the four boys went home at
        ## Night and for one weekend hour; the third list is the places they
        ## left (the garden, the cafeteria at a weekend Noon and Evening, the
        ## Mountain Path, the Courtyard and the rooftop on a weekend Morning).
        _zz_moved = [("yuji", "dorm_common"), ("nobara", "classroom"), ("toge", "rooftop"), ("megumi", "forest"), ("shoko", "rooftop"),
                     ("panda", "dorm_common"), ("toge", "dorm_common"),
                     ("yuji", "dorm_yard"), ("panda", "dorm_yard"), ("yuji", "cafeteria"), ("megumi", "trailhead"), ("panda", "courtyard")]
        ## U0c1 (the rest of 4.3): the two girls went home at Night and for a
        ## weekend Morning (Nobara left the corridor, Maki the corridor and the
        ## dojo), and their weekend Evenings are the Onsen (Nobara left the
        ## Courtyard, Maki the dojo). The three who left the weekend river for
        ## the pool (Yuji, Nobara, Panda) are not in this list yet: "Swim
        ## together" comes to the pool in wave 1, as swim_pool, and they are
        ## added then, in the commit that brings it (the ledger, 10.3).
        _zz_moved += [("nobara", "girls_dorm"), ("maki", "girls_dorm"), ("maki", "dojo"), ("nobara", "courtyard")]
        _zz_lost = []
        for _zz_w, _zz_l in sorted(_zz_moved):
            _zz_at = set(routine_location(_zz_w, p, we) for p in PERIODS for we in (False, True))
            for _zz_a in ACTIVITIES:
                if _zz_a.get("loc") and _zz_l in _zz_a["loc"] and not (_zz_at & set(_zz_a["loc"])):
                    _zz_lost.append((_zz_w, _zz_l, _zz_a["id"]))
        check(not _zz_lost, "nobody who moved lost an activity that needs a place: each is still offered somewhere in their week", _zz_lost)
        ## U0c1, reported and not hidden: Utahime's weekend Evening left the
        ## Courtyard for the Onsen (the plan's cell, 4.3), and the Courtyard
        ## was the one walk place in her week. By her routine "Walk with
        ## them" is offered with her nowhere now; walking with me ("Ask them
        ## along") she can still be taken to one. The owner's to rule on.
        _zz_uta = set(routine_location("utahime", p, we) for p in PERIODS for we in (False, True))
        note("Utahime left the Courtyard (weekend Evenings); activities with a place that her routine no longer reaches",
             [a["id"] for a in ACTIVITIES if a.get("loc") and "courtyard" in a["loc"] and not (_zz_uta & set(a["loc"]))])
        ## Panda's Night, the room he shares against the common room, with
        ## every bond full: under the night rule the same things can be
        ## started with him. The second UI overhaul (4.3, D48; U0b): his Night
        ## is the shared room (it was the garden), and on a weekday he is
        ## asleep there, so this is read on a weekend Night, when he is up;
        ## on a weekday Night he is counted there and is not on its stage.
        _zz_b0, _zz_s0 = bonds.get("panda", 0), set(spent_today)
        day = 13
        period = "Night"
        roll_gojo()
        bonds["panda"] = 100
        spent_today.discard("panda")
        _zz_was = [(a["id"], ok, why) for a, ok, why in activities_for("panda", "dorm_common") if ok]
        _zz_now = [(a["id"], ok, why) for a, ok, why in activities_for("panda", "senpai_room") if ok]
        check(night_on() and is_weekend() and char_location("panda") == "senpai_room" and "panda" in stage_people("senpai_room")[0]
              and _zz_now == _zz_was and ("talk", True, None) in _zz_now,
              "on a weekend Night whatever can be started with Panda in the common room can be started with him in the room he shares (Bond 100)",
              (_zz_was, _zz_now))
        day = 9
        roll_gojo()
        check(not is_weekend() and char_location("panda") == "senpai_room" and "panda" in who_is_here("senpai_room")
              and "panda" not in stage_people("senpai_room")[0] and ambient_of("panda", "senpai_room")[0] == "asleep",
              "on a weekday Night he is in that room asleep: counted there, not on its stage, so nothing can be started with him",
              (who_is_here("senpai_room"), stage_people("senpai_room")))
        bonds["panda"] = _zz_b0
        spent_today.clear(); spent_today.update(_zz_s0)
        period = "Noon"
        day = 9
        check(char_location("nobara", "Afternoon") == "courtyard" and char_location("yuji", "Afternoon") == "courtyard"
              and char_location("ijichi", "Morning") == "gate",
              "the courtyard and the gate keep their people (Yuji and Nobara in the afternoon, Ijichi and the car)")
        ## The courtyard's commonest crowd: two people. The gate exit stays in
        ## the picture and its hover label covers neither name tag nor
        ## another exit, whichever side of the icon it opens on.
        zz_place("courtyard", "Afternoon")
        _zz_hr, _zz_hit = zz_lock_label("courtyard", "gate")
        _zz_tags = [zz_rect("sb_place", "tag_" + w) for w in who_is_here("courtyard")]
        check(who_is_here("courtyard") == ["yuji", "nobara"] or sorted(who_is_here("courtyard")) == ["nobara", "yuji"],
              "a weekday afternoon in the courtyard: Yuji and Nobara", who_is_here("courtyard"))
        check(zz_hot("hot_go_courtyard__gate") is not None and _zz_hr is not None and len(_zz_tags) == 2 and all(_zz_tags)
              and not [r for r in _zz_tags if hot_overlap(_zz_hr, r)] and not _zz_hit
              and _zz_hr[0] >= 0 and _zz_hr[0] + _zz_hr[2] <= 1920 and _zz_hr[1] + _zz_hr[3] <= 1080,
              "with two people the gate exit is in the picture and its hover label, on screen, covers neither name tag nor another exit "
              "(hover check: needs the pointer)", (_zz_hr, _zz_tags, _zz_hit))
        shot("courtyard_two_people_hover_gate", wait=0)
        renpy.hide_screen("sb_place")
        period = "Noon"
        day = 9
        roll_gojo()
        note("phase1_all (30 days), wp3_missions, and the 11 saves", "run outside this harness: tools/smoke.sh and tools/load_all_saves.sh")

    ## --- 8. the walk: my room to the training hall, by real clicks, no map ------------------------------
    python:
        zz_open_campus()
        day = 9
        period = "Morning"
        here = "dorm"
        ## The second UI overhaul (4.4; U0b): one click more than before, the
        ## corridor of the Boys' Dormitory ("is one more click to my door on
        ## foot fine?" is checkpoint A's question to the owner).
        _zz_route = ["hot_go_dorm__boys_dorm", "hot_go_boys_dorm__dorm_yard", "hot_go_dorm_yard__courtyard",
                     "hot_go_courtyard__training_yard", "hot_go_training_yard__training"]
        _zz_i = 0
        del ZZ_WALK[:]
        autoplay()
    while _zz_i < len(_zz_route):
        scene expression graded_bg()
        $ view_sync_light()
        show screen zz_paths_press(_zz_route[_zz_i])
        call screen sb_place
        $ _r = _return
        python:
            ZZ_WALK.append((here, _r))
            if not (isinstance(_r, tuple) and _r[0] == "act" and _r[1].startswith("path_")):
                abort("the walk's click %r returned %r" % (_zz_route[_zz_i], _r))
        call expression "sb_do_" + _r[1]
        python:
            if here == "training_yard":
                shot("walk_training_yard", wait=0.3)
            _zz_i += 1
    python:
        autoplay(False)
        check(here == "training" and [w[0] for w in ZZ_WALK] == ["dorm", "boys_dorm", "dorm_yard", "courtyard", "training_yard"]
              and (day, period) == (9, "Morning"),
              "owner's walk: from my room to the training hall in five clicks in the picture (the corridor is the one more), "
              "the map never opened, no time spent", (here, ZZ_WALK))
        check(who_is_here("training_yard") == ["nobara"], "and on a weekday morning Nobara is standing in the training yard on the way", who_is_here("training_yard"))
        here = "gate"
        zz_place("gate", "Morning")
        check(zz_action_value("hot_go_gate__courtyard") == ("act", "path_courtyard") and zz_tip("hot_go_gate__courtyard") == "To the Courtyard",
              "at the gate, the exit clicks through to the courtyard")

    ## --- 9. worst case, and what a save holds ---------------------------------------------------------------
    python:
        ## The second UI overhaul (4.3; U0b): the garden is empty at Night on
        ## every day (Yuji and Panda are in their rooms); its busiest hour by
        ## routine is a weekend Evening, with Yuji by the pond.
        zz_open_campus()
        day = 9
        period = "Night"
        roll_gojo()
        check(who_is_here("dorm_yard") == [], "the Dormitory Garden on a weekday night: nobody (it held Yuji and Panda)", who_is_here("dorm_yard"))
        day = 13
        period = "Evening"
        roll_gojo()
        here = "dorm_yard"
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        arrival_caption()
        ARRIVAL[1] -= 10
        zz_worst("sb_place", hover="hot_go_dorm_yard__staff_yard")
        check(who_is_here("dorm_yard") == ["yuji"] and len(hot_spots_for("dorm_yard")) + len([a for a in rail_actions("dorm_yard") if a[0].startswith("path_")]) == len(path_exits("dorm_yard")) <= 7,
              "the Dormitory Garden on a weekend evening: Yuji outside, every exit offered (at most seven)", (who_is_here("dorm_yard"), [h["id"] for h in hot_spots_for("dorm_yard")]))
        ## Nothing un-picklable reaches a save (R10): the registry rows are
        ## init data; the screen's scope holds plain copies.
        _zz_rows = hot_spots_for("dorm_yard")
        check(all(type(h) is zz_builtins.dict for h in _zz_rows) and zz_pickle.loads(zz_pickle.dumps(_zz_rows)) == _zz_rows
              and zz_pickle.loads(zz_pickle.dumps(path_exits("dorm_yard"))) == path_exits("dorm_yard"),
              "what the place view holds of an exit is a plain dict that pickles")
        _zz_bad = []
        for _zz_k in sorted(renpy.python.store_dicts["store"].ever_been_changed):
            if _zz_k.startswith("_zz") or _zz_k.startswith("zz"):
                continue
            _zz_v = getattr(store, _zz_k, None)
            if isinstance(_zz_v, (path_ActionRow, path_SpotRow)) or (isinstance(_zz_v, (list, tuple)) and any(isinstance(x, (path_ActionRow, path_SpotRow)) for x in _zz_v)):
                _zz_bad.append(_zz_k)
        check(not _zz_bad, "no saved store variable holds a registry row", _zz_bad)
        for _zz_k in [k for k in list(vars(store)) if k.startswith("_zz_")]:
            delattr(store, _zz_k)
        renpy.take_screenshot()
        renpy.save("zz_p9_hub")
        check(renpy.can_load("zz_p9_hub"), "a save made standing in a hub, with the place view up, is written")
        renpy.hide_screen("sb_place")

    ## --- 10. the real loop: walk, save, load, walk on, roll back --------------------------------------------
    ## From here the run is label sandbox's own `call screen sb_place`; the
    ## timer of screen zz_paths_loop presses the exits, and zz_loop_step ends
    ## the run with finish().
    python:
        zz_open_campus()
        day = 9
        period = "Noon"
        here = "dorm"
        explore_mode = False
        toast_clear()
        note("the loop: a story beat waiting in my room (None is wanted)", repr(pick_event("story", loc=here)))
        ZZ_LOOP[:] = [1, 0, 0, None]
    scene expression graded_bg()
    jump sandbox
