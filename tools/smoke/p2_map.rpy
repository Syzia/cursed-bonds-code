## tools/smoke/p2_map.rpy -- P1's package harness (PHASE2_DESIGN.md section 7,
## "P1"): the two-level map, the Library's pin and schedule, Tokyo's second
## level, person_now.
##
##   tools/smoke.sh tools/smoke/p2_map.rpy
##
## Every acceptance bullet of P1 is a named check, in the plan's order
## (sections 1 to 12 below; 13 saves on the map). What needs another package is a NOTE that says
## so: the "no toast over the map" half of the last bullet is P2's
## (toast_room()), and the saves bullet is tools/load_all_saves.sh, run
## outside a harness.
##
## The overlay tools/smoke/assets/p2_map/game/layout/area_school.json replaces
## the game's own sidecar in the scratch copy: it moves the Library's pin, and
## plants one point for a room the area doesn't have (the validator must
## report exactly that one).
##
## Screenshots (shots/p2_map/): worst_sb_map, worst_map_area, worst_map_tokyo,
## worst_map_district (zz_worst of each full screen), every area, the Tokyo
## views, and the stand-in path (no icon pictures, no area picture).

init 999 python:
    import os
    import time as zz_time
    import builtins as zz_builtins
    import json as zz_json

    ## The stand-in path for an area's picture: renpy.loadable says no for
    ## one file while bg area_grounds's displayable is built again.
    zz_loadable0 = renpy.loadable

    def zz_no_grounds(path, *args, **kwargs):
        if path == "images/bg/area_grounds.png":
            return False
        return zz_loadable0(path, *args, **kwargs)

    def zz_no_icons(path, *args, **kwargs):
        if str(path).startswith("images/icons/"):
            return False
        return zz_loadable0(path, *args, **kwargs)

    renpy.loadable = zz_no_grounds
    ZZ_STANDIN = world_area_bg("grounds")
    renpy.loadable = zz_loadable0

    def zz_on_map(a):
        """Run a button's action with sb_map as the current screen, as a
        click does (SetScreenVariable writes to renpy.current_screen())."""
        renpy.display.screen.push_current_screen(renpy.get_screen("sb_map"))
        try:
            return renpy.run(a)
        finally:
            renpy.display.screen.pop_current_screen()

    def zz_widget(wid):
        return renpy.get_widget("sb_map", wid)

    def zz_press(wid):
        """Press a map button by id: what its action returns ("zz_missing"
        when the button isn't there)."""
        w = zz_widget(wid)
        if w is None:
            return "zz_missing"
        return zz_on_map(w.action)

    def zz_tip(wid):
        w = zz_widget(wid)
        return getattr(w, "_tooltip", None) if w is not None else None

    def zz_zone():
        return renpy.get_screen("sb_map").scope.get("zone")

    def zz_map(**kw):
        """Show the map fresh and draw it. zz_settle() afterwards waits out
        the second level's zoom-in (for a screenshot)."""
        renpy.hide_screen("sb_map")
        renpy.show_screen("sb_map", **kw)
        zz_render(0.1)

    def zz_settle():
        zz_render(0.45)

    def zz_tree(root):
        out = zz_builtins.list()
        root.visit_all(out.append)
        return out

    def zz_ids(prefix):
        """The ids of sb_map's buttons that start with prefix."""
        sc = renpy.get_screen("sb_map")
        return sorted(k for k in sc.widgets if isinstance(k, str) and k.startswith(prefix) and sc.widgets[k] is not None
                      and any(f.widget is sc.widgets[k] or f.widget is sc.base_widgets.get(k) for f in renpy.display.focus.focus_list))

    def zz_faces(root):
        """Who is drawn as a face chip under root (a screen or a widget):
        one per picture images/side/<who>_neutral.png in its tree."""
        out = zz_builtins.list()
        for d in zz_tree(root):
            fn = getattr(d, "filename", None)
            if isinstance(fn, str) and fn.startswith("images/side/") and fn.endswith("_neutral.png"):
                out.append(fn[len("images/side/"):-len("_neutral.png")])
        return out

    def zz_icons(root):
        """The icon names drawn under root: a picture ic_<name>.png, or the
        stand-in's kanji (a Text in the style icon_glyph)."""
        out = zz_builtins.list()
        glyphs = zz_builtins.dict((row[0], n) for n, row in ICONS.items())
        for d in zz_tree(root):
            fn = getattr(d, "filename", None)
            if isinstance(fn, str) and fn.startswith("images/icons/ic_"):
                out.append(fn[len("images/icons/ic_"):-len(".png")])
            elif isinstance(d, renpy.text.text.Text) and zz_is_glyph(d):
                out.append(glyphs.get(zz_text_string(d), "?"))
        return out

    def zz_strings(root):
        return [zz_text_string(d) for d in zz_tree(root) if isinstance(d, renpy.text.text.Text)]

    def zz_tooltips():
        """Every tooltip on sb_map as it is drawn now."""
        return [d._tooltip for d in zz_tree(renpy.get_screen("sb_map")) if getattr(d, "_tooltip", None) is not None]

    def zz_tips_bad(tips):
        """What breaks D11 in a list of tooltips: one that isn't (text, key),
        or a key used twice."""
        bad = [t for t in tips if not (isinstance(t, tuple) and len(t) == 2 and isinstance(t[0], str) and t[0]
                                       and isinstance(t[1], str) and t[1])]
        keys = [t[1] for t in tips if isinstance(t, tuple) and len(t) == 2]
        dup = sorted(set(k for k in keys if keys.count(k) > 1))
        return bad, dup

    def zz_alpha():
        """The alpha of the second level's picture as last drawn (1.0 for a
        picture with no transform on it)."""
        base = renpy.get_displayable("sb_map", "map_zone_bg", base=True)
        if base is None:
            return None
        ## The id names the picture itself; the transform `at` put on it is
        ## the Transform in the screen's tree whose child it is.
        for d in zz_tree(renpy.get_screen("sb_map")):
            if isinstance(d, renpy.display.transform.Transform) and getattr(d, "child", None) is base:
                return float(d.state.alpha)
        return 1.0

    def zz_params(name):
        sc = renpy.display.screen.get_screen_variant(name)
        if sc is None:
            return None
        p = sc.parameters
        return [] if p is None else [x.name for x in p.parameters.values()]

    def zz_overlap(a, b):
        return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])

    def zz_everyone_in():
        """A late save: everyone met, every door that a flag opens is open."""
        settle(day=9, period="Noon", here="courtyard")
        store.roster = list(ROSTER_ORDER)
        for f in ("utahime_arrived", "intensive_done", "storehouse_access", "ijichi_rides"):
            flag(f)
        store.companion = None
        store.schedule_overrides = {}
        roll_gojo()

    def zz_source(rel):
        root = smoke_env("SMOKE_ROOT")
        if not root:
            return None
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read()

    def zz_moon_mountain():
        return {"mountain": "moon"}

    zz_who_is_here0 = who_is_here

    def zz_crowd(loc):
        """Five people in whichever room is asked about."""
        return ["yuji", "megumi", "nobara", "panda", "shoko"]

    def zz_night_yes(key):
        return (True, "")

    def zz_night_no(key):
        return (False, "Not two nights running")

    ## 0: not saved yet; 1: saving; 2: saved and loaded (section 13). Outside the store.
    ZZ_SAVE = zz_builtins.list([0])

    ## sb_night.rpy's own, to put back after a check patches the store name.
    zz_night_out_ok0 = night_out_ok
    zz_night_marks0 = night_marks


## Returns a value into the interaction that is running (a called screen).
screen zz_map_press(wid, delay=0.4, first=None):
    zorder 200
    if first:
        timer delay action Function(ui_do, zz_press, first)
        timer (delay + 0.5) action [Hide("zz_map_press"), Function(zz_press, wid)]
    else:
        timer delay action [Hide("zz_map_press"), Function(zz_press, wid)]


label zz_smoke:

    python:
        fixture(mc_name="Tester", mc_surname="Harness")
        zz_everyone_in()
        _zz_icon_words0 = gui.icon_words
        _zz_motion0 = persistent.motion
        persistent.motion = True

    ## --- 1. level 1: six areas, nothing else ------------------------------------------------
    python:
        ## Five people in the School Building at noon: four in the cafeteria, Shoko in the infirmary.
        roster = ["yuji", "megumi", "nobara", "panda", "shoko"]
        gui.icon_words = "never"
        zz_map()
        _zz_areas = zz_ids("area_")
        check(_zz_areas == sorted("area_" + a["key"] for a in AREAS), "level 1 has exactly six area_<key> buttons", _zz_areas)
        check(zz_ids("row_") == [] and all(zz_widget("row_" + l) is None for l in LOCATIONS), "level 1 has no row_* button", zz_ids("row_"))
        _zz_t = zz_texts("sb_map")
        _zz_gone = [s for s in _zz_t for old in ("FIND SOMEONE", "Find someone", "Walking is free", "TOKYO JUJUTSU HIGH", "Doing something takes time")
                    if old in s]
        check(not _zz_gone, "level 1 holds none of 'Find someone', 'Walking is free' or the old header", _zz_gone)
        check("Jujutsu High" in _zz_t and _zz_t.count("Jujutsu High") == 1, "the title 'Jujutsu High' is written once", _zz_t)
        _zz_w = zz_words("sb_map")
        check(len(_zz_w) <= 20, "level 1: zz_words <= 20 (%d, the date chip and MENU included)" % len(_zz_w), _zz_w)
        _zz_b = zz_buttons("sb_map")
        check(_zz_b <= 10, "level 1: at most 6 markers + 4 buttons (%d)" % _zz_b)
        _zz_school = zz_widget("area_school")
        _zz_f = zz_faces(_zz_school)
        check(len(map_area_people("school")) == 5 and len(_zz_f) == 3 and "+2" in zz_strings(_zz_school),
              "five people in an area: three face chips, then '+2'", (map_area_people("school"), _zz_f, zz_strings(_zz_school)))
        roster = list(ROSTER_ORDER)
        _zz_over = []
        for _zz_p in PERIODS:
            for _zz_d in (9, 13):          ## a weekday and a Saturday
                day = _zz_d
                period = _zz_p
                roll_gojo()
                zz_map()
                for _zz_a in AREAS:
                    _zz_n = len(zz_faces(zz_widget("area_" + _zz_a["key"])))
                    if _zz_n > 3:
                        _zz_over.append((_zz_d, _zz_p, _zz_a["key"], _zz_n))
                if len(zz_faces(renpy.get_screen("sb_map"))) > 18:
                    _zz_over.append((_zz_d, _zz_p, "screen", len(zz_faces(renpy.get_screen("sb_map")))))
        check(not _zz_over, "no marker shows more than three face chips (5 periods x a weekday and a Saturday; 18 at most on the map)", _zz_over)
        day = 9
        period = "Noon"
        roll_gojo()
        zz_map()
        check(any("I'M HERE" in s for s in zz_strings(zz_widget("area_heart")))
              and not any("I'M HERE" in s for a in AREAS if a["key"] != "heart" for s in zz_strings(zz_widget("area_" + a["key"]))),
              "I'M HERE is on my area's marker only")
        ## Kaito narrates in "I": no second-person words on the map's levels.
        _zz_you = [s for s in zz_texts("sb_map") if zz_re.search(r"\b(you|your|you.re)\b", s, zz_re.I)]
        check(not _zz_you, "the campus map says nothing in the second person (the marker reads I'M HERE)", _zz_you)
        check(zz_press("area_school") is None and zz_zone() == "school" and here == "courtyard",
              "pressing an area marker returns nothing: it opens the area and I stay where I am", (zz_zone(), here))
        zz_render(0.5)
        check(zz_ids("row_") == sorted("row_" + l for l in places_in("school")) and zz_ids("area_") == [],
              "after the press the map shows that area's pins and no markers", (zz_ids("row_"), zz_ids("area_")))
        check(zz_press("map_back") is None and zz_zone() is None, "Back returns nothing and goes back to the six areas", zz_zone())
        _zz_stay = zz_widget("map_stay")
        check(_zz_stay is not None and zz_on_map(_zz_stay.action) == ("cancel",), "Stay here returns ('cancel',)")

    ## --- 2. level 2: an area's rooms --------------------------------------------------------
    python:
        zz_map(area="school")
        ## P9 (D53): the area's hub, the School Courtyard, has a pin too.
        check(zz_ids("row_") == ["row_cafeteria", "row_classroom", "row_infirmary", "row_library", "row_school_yard"],
              "sb_map(area='school') shows row_classroom, row_cafeteria, row_infirmary, row_library and the hub's row_school_yard", zz_ids("row_"))
        check("School Building" in zz_texts("sb_map") and AREA_BY_KEY["school"]["name"] == "School Building"
              and "library" in places_in("school"), "the school area is 'School Building' and holds the Library")
        _zz_bad = []
        _zz_words = {}
        _zz_btns = {}
        _zz_rects = {}
        for _zz_a in AREAS:
            for _zz_l in _zz_a["places"]:
                here = "courtyard" if _zz_l != "courtyard" else "gate"
                period = "Noon"
                zz_map(area=_zz_a["key"])
                _zz_r = zz_press("row_" + _zz_l)
                if _zz_r != ("go", _zz_l):
                    _zz_bad.append((_zz_l, _zz_r, place_access(_zz_l)))
            here = "dorm"
            zz_map(area=_zz_a["key"])
            _zz_words[_zz_a["key"]] = len(zz_words("sb_map"))
            _zz_btns[_zz_a["key"]] = zz_buttons("sb_map")
            for _zz_l in _zz_a["places"]:
                _zz_rects[_zz_l] = zz_rect("sb_map", "row_" + _zz_l)
            _zz_rects["back:" + _zz_a["key"]] = zz_rect("sb_map", "map_back")
            zz_settle()
            shot("area_" + _zz_a["key"], wait=0)
        check(not _zz_bad and len(LOCATIONS) == 24, "pressing an open pin returns ('go', loc), for every one of the 24 places (19 rooms, 5 new hubs)", _zz_bad)
        check(max(_zz_words.values()) <= 16, "level 2: zz_words <= 16 in every area", _zz_words)
        check(max(_zz_btns.values()) <= 10, "level 2: at most 5 pins (the hub's included) + 5 buttons in every area", _zz_btns)
        _zz_hits = [(a, b) for a in _zz_rects for b in _zz_rects if a < b and _zz_rects[a] and _zz_rects[b]
                    and (area_of(a) or a[5:]) == (area_of(b) or b[5:]) and zz_overlap(_zz_rects[a], _zz_rects[b])]
        check(all(_zz_rects.values()) and not _zz_hits, "no pin overlaps another pin of its area, or Back", (_zz_hits, [k for k, v in _zz_rects.items() if not v]))

        ## The game's own sidecars (the overlay above replaces area_school.json
        ## in the scratch copy, so the shipped points are read from the tree).
        _zz_close = []
        _zz_out = []
        _zz_miss = []
        for _zz_a in AREAS:
            _zz_raw = zz_source("game/layout/area_%s.json" % _zz_a["key"])
            if _zz_raw is None:
                _zz_miss.append(_zz_a["key"])
                continue
            _zz_pts = zz_json.loads(_zz_raw).get("spots", {})
            if sorted(_zz_pts) != sorted(_zz_a["places"]):
                _zz_miss.append((_zz_a["key"], sorted(_zz_pts)))
            for _zz_l, (_zz_x, _zz_y) in _zz_pts.items():
                if not (MAP_PIN_FRAME[0] <= _zz_x <= MAP_PIN_FRAME[2] and MAP_PIN_FRAME[1] <= _zz_y <= MAP_PIN_FRAME[3]):
                    _zz_out.append((_zz_l, _zz_x, _zz_y))
                for _zz_m, (_zz_x2, _zz_y2) in _zz_pts.items():
                    if _zz_l < _zz_m and abs(_zz_x - _zz_x2) < MAP_PIN_W and abs(_zz_y - _zz_y2) < 120:
                        _zz_close.append((_zz_l, _zz_m))
        check(not _zz_miss and not _zz_out and not _zz_close,
              "the shipped sidecars: every room of each area has a point inside the frame, and no two pins of an area "
              "are closer than 240 px across and 120 px down", (_zz_miss, _zz_out, _zz_close))
        _zz_wide = [(l, map_text_width(n, gui.display_font, map_fit(n, 22, MAP_PIN_W - 24)) + 20)
                    for l in LOCATIONS for n in (LOCATIONS[l]["name"], "Empty Office")]
        check(all(w <= MAP_PIN_W for l, w in _zz_wide), "every pin's name plate fits inside the pin's %d px button" % MAP_PIN_W,
              [x for x in _zz_wide if x[1] > MAP_PIN_W])

        ## A crowd on a pin near the left edge: its hover label opens on the
        ## right, so the faces are drawn on the left of the tile.
        who_is_here = zz_crowd
        zz_map(area="mountain")
        _zz_fx, _zz_fy = map_spots("mountain")["forest"]
        _zz_rx, _zz_ry = map_spots("mountain")["riverside"]
        _zz_fb = zz_widget("faces_forest")
        _zz_rb = zz_widget("faces_riverside")
        check(_zz_fx < MAP_FACES_LEFT_X and _zz_fb is not None and _zz_fb.style.xanchor == 1.0 and _zz_fb.style.xpos == _zz_fx - 46
              and len(zz_faces(_zz_fb)) == 3 and "+2" in zz_strings(_zz_fb),
              "five people on the Forest Trail: the faces box ends at x - 46, left of the tile, clear of a label on the right "
              "(nothing of it is past x + 120)", (_zz_fx, _zz_fb and (_zz_fb.style.xpos, _zz_fb.style.xanchor)))
        check(_zz_rx >= MAP_FACES_LEFT_X and _zz_rb is not None and not _zz_rb.style.xanchor and _zz_rb.style.xpos == _zz_rx + 46,
              "a pin on the right keeps its faces on the right of the tile", (_zz_rx, _zz_rb and (_zz_rb.style.xpos, _zz_rb.style.xanchor)))
        renpy.set_focus("sb_map", "row_forest")
        zz_render(0.5)
        shot("crowd_forest_hover", wait=0)
        who_is_here = zz_who_is_here0
        renpy.hide_screen("sb_map")

        ## My own room, and a locked one.
        here = "cafeteria"
        zz_map(area="school")
        check(zz_press("row_cafeteria") is None and zz_widget("row_cafeteria").action.__class__.__name__ == "NullAction",
              "the pin of the room I'm in does nothing")
        here = "courtyard"
        flags.discard("storehouse_access")
        zz_map(area="grounds")
        _zz_t = zz_tip("row_storehouse")
        check(zz_press("row_storehouse") is None and zz_widget("row_storehouse").action.__class__.__name__ == "NullAction",
              "a locked pin returns nothing")
        check(isinstance(_zz_t, tuple) and can_enter("storehouse")[1] in _zz_t[0] and "lock" in zz_icons(renpy.get_screen("sb_map")),
              "a locked pin has a tooltip with the reason, and a lock badge", (_zz_t, zz_icons(renpy.get_screen("sb_map"))))
        flag("storehouse_access")

    ## A real call: two presses to anywhere, and the value reaches the label.
    $ here = "courtyard"
    show screen zz_map_press("row_library", first="area_school")
    call screen sb_map
    $ check(_return == ("go", "library"), "call screen sb_map: School Building, then the Library -> ('go', 'library')", _return)
    show screen zz_map_press("map_stay")
    call screen sb_map
    $ check(_return == ("cancel",), "call screen sb_map: Stay here -> ('cancel',)", _return)

    ## --- 3. tooltips -------------------------------------------------------------------------
    python:
        zz_everyone_in()
        grade = "g2"
        districts_visited = {"shibuya"}
        night_out_ok = zz_night_no
        _zz_bad = []
        _zz_n = 0
        _zz_views = [dict()] + [dict(area=a["key"]) for a in AREAS] + [dict(layer="tokyo")] \
            + [dict(layer="tokyo", area=k) for k in DISTRICT_ORDER]
        for _zz_p in ("Noon", "Night"):
            period = _zz_p
            for _zz_kw in _zz_views:
                zz_map(**_zz_kw)
                _zz_tips = zz_tooltips()
                _zz_n += len(_zz_tips)
                _zz_b, _zz_dup = zz_tips_bad(_zz_tips)
                if _zz_b or _zz_dup or not _zz_tips:
                    _zz_bad.append((_zz_p, _zz_kw, _zz_b, _zz_dup))
        night_out_ok = zz_night_out_ok0
        check(not _zz_bad, "every tooltip on the map is a 2-tuple with a key unique on its screen; no plain string is left (%d tooltips, 13 views x Noon and Night)" % _zz_n, _zz_bad[:4])

    ## --- 4. the zoom-in ------------------------------------------------------------------------
    python:
        period = "Noon"
        zz_map()
        zz_render(1.0)              ## the map has been up for well over the zoom's 0.3 s
        zz_press("area_mountain")
        zz_render(0.03)
        _zz_a1 = zz_alpha()
        zz_render(0.5)
        _zz_a2 = zz_alpha()
        check(_zz_a1 is not None and _zz_a1 < 1.0, "the zoom-in starts at the press, not at the screen's start (alpha just after the press: %r)" % _zz_a1)
        check(_zz_a2 == 1.0, "half a second after pressing a marker the area picture's alpha is 1.0", _zz_a2)
        zz_press("map_back")
        zz_render(0.2)
        zz_press("area_mountain")
        zz_render(0.03)
        _zz_a3 = zz_alpha()
        zz_render(0.5)
        check(_zz_a3 < 1.0 and zz_alpha() == 1.0, "opening the same area again plays the zoom-in again", (_zz_a3, zz_alpha()))
        persistent.motion = False
        zz_map()
        zz_render(0.6)
        zz_press("area_mountain")
        zz_render(0.03)
        check(zz_alpha() == 1.0, "with persistent.motion False the picture is at alpha 1.0 at once", zz_alpha())
        persistent.motion = True
        _zz_crops = dict((a["key"], world_area_crop(a["key"])) for a in AREAS)
        check(all(x >= 0 and y >= 0 and x + w <= 1920 and y + h <= 1080 and (w, h) == (720, 405) for x, y, w, h in _zz_crops.values())
              and _zz_crops["heart"][1] == 1080 - 405,
              "the placeholder crop for every area lies inside 0 to 1920, 0 to 1080 (the heart's is clamped to the bottom)", _zz_crops)
        check(all(renpy.has_image(tuple(a["bg"].split()), exact=True) for a in AREAS), "bg area_<key> is defined for all six areas")
        check(isinstance(ZZ_STANDIN, Transform) and tuple(ZZ_STANDIN.crop) == world_area_crop("grounds")
              and isinstance(world_area_bg("grounds"), str),
              "with no area_grounds.png the picture is the clamped crop of map_campus.png; with it, the file", ZZ_STANDIN)

    ## --- 5. spots and the sidecar -----------------------------------------------------------
    python:
        _zz_seen = {}
        _zz_out = []
        for _zz_a in AREAS:
            for _zz_l, (_zz_x, _zz_y) in map_spots(_zz_a["key"]).items():
                _zz_seen.setdefault(_zz_l, []).append(_zz_a["key"])
                if not (200 <= _zz_x <= 1700 and 200 <= _zz_y <= 940):
                    _zz_out.append((_zz_l, _zz_x, _zz_y))
            for _zz_l, (_zz_x, _zz_y) in _zz_a["spots"].items():
                if not (200 <= _zz_x <= 1700 and 200 <= _zz_y <= 940):
                    _zz_out.append(("code default", _zz_l, _zz_x, _zz_y))
        check(sorted(_zz_seen) == sorted(LOCATIONS) and all(len(v) == 1 and v[0] == area_of(l) for l, v in _zz_seen.items()),
              "every room is in exactly one area's spots", _zz_seen)
        check(not _zz_out, "every spot (the code's and the sidecar's) is inside x 200 to 1700, y 200 to 940", _zz_out)
        _zz_code = AREA_BY_KEY["school"]["spots"]
        _zz_sp = map_spots("school")
        check(_zz_sp["library"] == (1420, 860) and _zz_code["library"] == (1340, 780)
              and all(_zz_sp[l] == _zz_code[l] for l in ("classroom", "cafeteria", "infirmary")) and "gate" not in _zz_sp,
              "the test sidecar area_school.json moves the Library's pin and nothing else", (_zz_sp, _zz_code))
        here = "courtyard"
        zz_map(area="school")
        _zz_r = zz_rect("sb_map", "row_library")
        check(_zz_r is not None and abs(_zz_r[0] + _zz_r[2] / 2.0 - 1420) <= 1 and _zz_r[1] == 860 - 36,
              "the Library's pin is drawn at the sidecar's point (the tile centred on it)", _zz_r)
        _zz_real = rule_layout("area_heart").get("spots") or {}
        check(_zz_real and all(map_spots("heart")[l] == tuple(p) for l, p in _zz_real.items()),
              "the game's own sidecars are applied (area_heart.json)", (_zz_real, map_spots("heart")))
        _zz_v = map_validate()
        check(len(_zz_v) == 1 and "'gate' is not a room of this area" in _zz_v[0],
              "the pin validator reports the sidecar's stray room, and nothing else", _zz_v)
        _zz_keep = RULE_LAYOUT.get("area_heart")
        RULE_LAYOUT["area_heart"] = {"spots": {"gate": [100, 960], "courtyard": "x"}}
        _zz_v = map_validate()
        RULE_LAYOUT["area_heart"] = _zz_keep
        check(any("outside x 200 to 1700" in s for s in _zz_v) and any("'courtyard' must be [x, y]" in s for s in _zz_v)
              and map_spots("heart") == dict((l, tuple(p)) for l, p in _zz_real.items()),
              "the pin validator rejects a spot outside the frame and a point that isn't [x, y]", _zz_v)

    ## --- 6. nobody behind a locked door -----------------------------------------------------
    python:
        zz_everyone_in()
        period = "Night"
        here = "dorm"
        flags.discard("invited_girls_dorm")
        _zz_in = who_is_here("girls_dorm")
        zz_map()
        _zz_m = zz_faces(renpy.get_screen("sb_map"))
        zz_map(area="dorms")
        _zz_p = zz_faces(renpy.get_screen("sb_map"))
        check(len(_zz_in) >= 2 and not place_access("girls_dorm")[0], "at Night the girls' dormitory is locked with people in it", _zz_in)
        check(not [w for w in _zz_in if w in _zz_m] and not [w for w in _zz_in if w in _zz_p]
              and not [w for w in _zz_in if w in map_area_people("dorms")] and map_pin_people("girls_dorm") == [],
              "a person in a locked room is on no marker and no pin", (_zz_in, _zz_m, _zz_p))
        ## P9 (D53, D57): the hub is an open place of the area too (Yuji is in
        ## the Dormitory Garden at night).
        check(sorted(_zz_p) == sorted(w for l in ("dorm_yard", "dorm", "dorm_common", "rooftop") for w in who_is_here(l)[:3])
              and "yuji" in who_is_here("dorm_yard"),
              "the open places' pins still show who is there", (_zz_p,))

    ## --- 7. the two new screens ---------------------------------------------------------------
    python:
        check(zz_params("map_area") == ["key"] and zz_params("map_district") == ["key"],
              "screens map_area(key) and map_district(key) exist with exactly those parameters",
              (zz_params("map_area"), zz_params("map_district")))
        check(isinstance(MAP_DISTRICT_SPOTS, dict) and sorted(MAP_DISTRICT_SPOTS) == sorted(DISTRICTS)
              and all(sorted(r) == ["icon", "id", "name", "note", "x", "y"] and r["icon"] in ICONS
                      for rows in MAP_DISTRICT_SPOTS.values() for r in rows)
              and MAP_NIGHT_DISTRICTS == ("shibuya", "shinjuku"),
              "MAP_DISTRICT_SPOTS rows are dict(id, name, icon, x, y, note); MAP_NIGHT_DISTRICTS is Shibuya and Shinjuku")

    ## --- 8. the moon ------------------------------------------------------------------------
    python:
        period = "Noon"
        here = "courtyard"
        zz_map()
        _zz_none = [a["key"] for a in AREAS if "moon" in zz_icons(zz_widget("area_" + a["key"]))]
        night_marks = zz_moon_mountain
        zz_map()
        _zz_moon = [a["key"] for a in AREAS if "moon" in zz_icons(zz_widget("area_" + a["key"]))]
        zz_settle()
        shot("level1_moon", wait=0)
    python:
        night_marks = zz_night_marks0
        check(_zz_none == [] and _zz_moon == ["mountain"],
              "with night_marks patched to {'mountain': 'moon'} the Mountain marker shows the moon and no other does", (_zz_none, _zz_moon))

    ## --- 9. Tokyo ---------------------------------------------------------------------------
    python:
        zz_everyone_in()
        grade = "g4"
        districts_visited = {"shibuya"}
        period = "Morning"
        here = "gate"
        zz_map(layer="tokyo")
        check(zz_ids("district_") == sorted("district_" + k for k in DISTRICT_ORDER) and len(DISTRICT_ORDER) == 5,
              "sb_map(layer='tokyo') shows five district_<key>", zz_ids("district_"))
        _zz_w = zz_words("sb_map")
        check(len(_zz_w) <= 20, "Tokyo, level 1: zz_words <= 20 (%d)" % len(_zz_w), _zz_w)
        check(zz_press("district_shibuya") is None and zz_zone() == "shibuya",
              "pressing an open district returns nothing and opens its view (zone is set)", zz_zone())
        zz_render(0.5)
        check(zz_ids("district_") == ["district_go"] and "Shibuya" in zz_texts("sb_map"),
              "an open district's view has district_go", zz_ids("district_"))
        check(zz_press("map_back") is None and zz_zone() is None, "Back ('Tokyo') returns to the five districts")
        zz_render(0.3)
        check(zz_press("district_shinjuku") is None and zz_zone() is None
              and "Grade 2" in zz_tip("district_shinjuku")[0],
              "a locked district (Shinjuku at Grade 4) does nothing and says why", zz_tip("district_shinjuku"))

        _zz_bad = []
        for _zz_p in PERIODS:
            for _zz_ij in (True, False):
                period = _zz_p
                schedule_overrides = {} if _zz_ij else {("ijichi", day, _zz_p): "office"}
                for _zz_k in ("shibuya", "harajuku", "yotsuka"):
                    zz_map(layer="tokyo", area=_zz_k)
                    _zz_r = zz_press("district_go")
                    if (_zz_r == ("district", _zz_k)) != bool(trip_ok_now()) or _zz_r not in (None, ("district", _zz_k)):
                        _zz_bad.append((_zz_p, _zz_ij, _zz_k, _zz_r, trip_ok_now()))
        schedule_overrides = {}
        check(not _zz_bad, "district_go returns ('district', key) exactly when trip_ok_now() (5 periods, Ijichi at the gate or not)", _zz_bad)

        ## The night button, with sb_night.rpy's own night_out_ok.
        grade = "g2"
        _zz_stub = night_out_ok("shibuya")
        _zz_seen = []
        for _zz_p in PERIODS:
            period = _zz_p
            zz_map(layer="tokyo")
            if zz_widget("district_night") is not None:
                _zz_seen.append((_zz_p, "level 1"))
            for _zz_k in DISTRICT_ORDER:
                zz_map(layer="tokyo", area=_zz_k)
                if zz_widget("district_night") is not None:
                    _zz_seen.append((_zz_p, _zz_k))
        if _zz_stub == (False, ""):
            check(not _zz_seen, "with the stub ((False, '')) no district_night button exists anywhere", _zz_seen)
        else:
            note("district_night with the stub", "night_out_ok is no longer the stub (P4b is in): %r; shown at %r" % (_zz_stub, _zz_seen))

        night_out_ok = zz_night_yes
        _zz_seen = []
        _zz_ret = {}
        for _zz_p in PERIODS:
            period = _zz_p
            for _zz_k in DISTRICT_ORDER:
                zz_map(layer="tokyo", area=_zz_k)
                if zz_widget("district_night") is not None:
                    _zz_seen.append((_zz_p, _zz_k))
                    _zz_ret[(_zz_p, _zz_k)] = zz_press("district_night")
        check(sorted(_zz_seen) == sorted((p, k) for p in ("Evening", "Night") for k in ("shibuya", "shinjuku"))
              and all(v == ("night", k[1]) for k, v in _zz_ret.items()),
              "night_out_ok patched to (True, ''): district_night exists only in Shibuya and Shinjuku at Evening or Night, and returns ('night', key)",
              (_zz_seen, _zz_ret))
        period = "Evening"
        zz_map(layer="tokyo")
        _zz_moons = [k for k in DISTRICT_ORDER if "moon" in zz_icons(zz_widget("district_" + k))]
        check(_zz_moons == [k for k in DISTRICT_ORDER if district_state(k)[0]] and "shibuya" in _zz_moons and "kawasaki" not in _zz_moons,
              "an open district's marker shows the moon when night_out_ok(key)[0]", _zz_moons)
        zz_map(layer="tokyo", area="shibuya")
        zz_settle()
        shot("district_shibuya_night", wait=0)

        night_out_ok = zz_night_no
        zz_map(layer="tokyo", area="shibuya")
        _zz_t = zz_tip("district_night")
        check(zz_widget("district_night") is not None and zz_press("district_night") is None
              and isinstance(_zz_t, tuple) and "Not two nights running" in _zz_t[0],
              "night_out_ok patched to (False, 'Not two nights running'): district_night exists, returns nothing and shows the reason", _zz_t)
        zz_map(layer="tokyo")
        check(not [k for k in DISTRICT_ORDER if "moon" in zz_icons(zz_widget("district_" + k))], "no moon on a district whose night can't start")

        ## A closed district opened by argument: no second level, no night.
        night_out_ok = zz_night_yes
        grade = "g4"
        zz_map(layer="tokyo", area="shinjuku")
        check(district_state("shinjuku")[0] is False and map_night_state("shinjuku") == (False, False, "")
              and zz_widget("district_night") is None and zz_widget("district_go") is None
              and zz_ids("district_") == sorted("district_" + k for k in DISTRICT_ORDER),
              "sb_map(layer='tokyo', area='shinjuku') at Grade 4: the five districts, no district_go and no district_night",
              (district_state("shinjuku"), map_night_state("shinjuku"), zz_ids("district_")))
        grade = "g2"
    python:
        night_out_ok = zz_night_out_ok0

    ## Real calls: the Tokyo layer through the protected-style statement.
    $ period = "Morning"
    $ grade = "g4"
    show screen zz_map_press("district_go", first="district_harajuku")
    call screen sb_map(layer="tokyo")
    $ check(_return == ("district", "harajuku"), "call screen sb_map(layer='tokyo'): Harajuku, then Ride with Ijichi -> ('district', 'harajuku')", _return)

    ## The Campus / Tokyo switch.
    python:
        zz_map()
        check(zz_press("map_tokyo") is None and renpy.get_screen("sb_map").scope["view"] == "tokyo",
              "the switch: Tokyo sets the layer and returns nothing")
        zz_render(0.3)
        check(zz_ids("district_") == sorted("district_" + k for k in DISTRICT_ORDER) and "Tokyo" in zz_texts("sb_map"),
              "the switch: the Tokyo layer shows the districts under 'Tokyo'")
        zz_press("district_shibuya")
        zz_render(0.3)
        check(zz_press("map_campus") is None and renpy.get_screen("sb_map").scope["view"] == "campus" and zz_zone() is None,
              "the switch: Campus sets the layer and clears the open district")
        flags.discard("ijichi_rides")
        zz_map()
        _zz_t = zz_tip("map_tokyo")
        check(zz_press("map_tokyo") is None and renpy.get_screen("sb_map").scope["view"] == "campus"
              and _zz_t == ("Tokyo — after Ijichi's ride-along", "map_tokyo"),
              "before Ijichi's ride-along the Tokyo button does nothing and says why", _zz_t)
        flag("ijichi_rides")

    ## --- 10. the frozen surface ----------------------------------------------------------------
    python:
        check(zz_params("sb_map") == ["layer", "area"], "the screen's parameters are ['layer', 'area']", zz_params("sb_map"))
        check(zz_params("sb_map_campus") == [] and zz_params("sb_map_tokyo") == [], "sb_map_campus and sb_map_tokyo keep their names")
        _zz_loop = zz_source("game/sb_loop.rpy")
        _zz_tok = zz_source("game/sb_tokyo.rpy")
        if _zz_loop is None:
            check(False, "the protected call statements: SMOKE_ROOT is not set (an old tools/smoke.sh?)")
        else:
            check("\n    call screen sb_map\n    $ _m = _return\n" in _zz_loop
                  and '\n    call screen sb_map(layer="tokyo")\n    $ _car = _return\n' in _zz_tok,
                  "both protected call statements are unchanged (sb_loop.rpy, sb_tokyo.rpy), each with the line after it")
        check(all(callable(getattr(store, n, None)) for n in ("face_chip", "map_who_where", "map_cards", "map_people", "map_row_action",
                                                               "map_district_action", "map_place_name", "map_has_news", "map_waiting"))
              and isinstance(FACE_BOX, dict) and MAP_CARD_W == 340 and MAP_ROW_W == 320,
              "face_chip, FACE_BOX, map_who_where, map_cards, map_people and the MAP_* tables stay defined")
        ## The gold "!" after a name follows the night rule, as the name tag
        ## in the place view does (view_tag_marks): the map promises nothing
        ## the place view then does not offer.
        _zz_keep_marks = (store.has_event, store.missions_with, store.night_can_work, store.night_allows, store.explore_mode)
        try:
            store.has_event = lambda kind, who=None, loc=None: kind == "hangout" and who == "yuji"
            store.missions_with = lambda who, loc=None: ["m_sunmall"] if who == "toge" else []
            store.night_can_work = lambda: True
            store.night_allows = lambda aid, cost=0: True
            store.explore_mode = False
            _zz_m0 = [map_has_news(w, "cafeteria") for w in ("yuji", "toge", "megumi")]
            store.night_can_work = lambda: False
            _zz_m1 = [map_has_news(w, "cafeteria") for w in ("yuji", "toge", "megumi")]
            store.night_can_work = lambda: True
            store.night_allows = lambda aid, cost=0: not str(aid).startswith("mission:")
            _zz_m2 = [map_has_news(w, "cafeteria") for w in ("yuji", "toge", "megumi")]
            store.night_allows = lambda aid, cost=0: aid != "hang"
            _zz_m3 = [map_has_news(w, "cafeteria") for w in ("yuji", "toge", "megumi")]
            store.night_allows = lambda aid, cost=0: True
            store.explore_mode = True
            _zz_m4 = [map_has_news(w, "cafeteria") for w in ("yuji", "toge", "megumi")]
            store.explore_mode = False
            _zz_m5 = [map_has_news(w, "cafeteria") == any(view_tag_marks(w, "cafeteria")) for w in ("yuji", "toge", "megumi")]
        finally:
            store.has_event, store.missions_with, store.night_can_work, store.night_allows, store.explore_mode = _zz_keep_marks
        check(_zz_m0 == [True, True, False] and all(type(v) is bool for v in _zz_m0),
              "map_has_news: a gold mark for a waiting scene and for a waiting mission, none for anyone else (a bool)", _zz_m0)
        check(_zz_m1 == [True, False, False],
              "on a rest day (night_can_work patched to False) the map promises no mission; the scene's mark stays", _zz_m1)
        check(_zz_m2 == [True, False, False] and _zz_m3 == [False, True, False],
              "when the night won't let the mission start its mark is gone; when it won't let a scene start, the scene's is", (_zz_m2, _zz_m3))
        check(_zz_m4 == [True, False, False] and all(_zz_m5),
              "no mission mark in explore mode; the map's mark is the place view's name-tag marks (view_tag_marks)", (_zz_m4, _zz_m5))
        del _zz_keep_marks
        note("load_all_saves.sh (auto-1 and auto-2 SAME)",
             "run outside a harness: tools/load_all_saves.sh loads the owner's 11 saves; the two parked on `call screen sb_map` reopen on the six areas")

    ## --- 11. the world, person_now ---------------------------------------------------------------
    python:
        check(_validate_world() == [], "_validate_world passes", _validate_world())
        zz_everyone_in()
        _zz_keys = {"place", "name", "doing", "reachable", "hidden", "with_me"}
        _zz_bad = []
        for _zz_p in PERIODS:
            period = _zz_p
            for _zz_c in JOURNAL_CAST:
                _zz_v = person_now(_zz_c["who"])
                if not (isinstance(_zz_v, dict) and set(_zz_v) == _zz_keys and isinstance(_zz_v["name"], str) and _zz_v["name"]
                        and isinstance(_zz_v["doing"], str) and (_zz_v["place"] is None or _zz_v["place"] in LOCATIONS)
                        and all(isinstance(_zz_v[k], bool) for k in ("reachable", "hidden", "with_me"))
                        and (not _zz_v["reachable"] or (_zz_v["place"] and can_enter(_zz_v["place"])[0] and _zz_v["place"] != here))):
                    _zz_bad.append((_zz_p, _zz_c["who"], _zz_v))
        check(len(JOURNAL_CAST) == 17 and not _zz_bad, "person_now returns its six keys for all 17 journal people, at every period", _zz_bad[:3])
        period = "Noon"
        here = "courtyard"
        _zz_v = person_now("yuji")
        check(_zz_v == dict(place="cafeteria", name="Cafeteria", doing=ambient_of("yuji", "cafeteria")[0], reachable=True, hidden=False, with_me=False),
              "person_now: someone in an open room: the room, what they're doing, reachable", _zz_v)
        here = "cafeteria"
        check(person_now("yuji")["reachable"] is False and person_now("yuji")["place"] == "cafeteria", "person_now: not reachable when I'm already in that room")
        here = "courtyard"
        period = "Night"
        _zz_v = person_now("nobara")
        check(char_location("nobara") == "girls_dorm" and _zz_v == dict(place=None, name="Somewhere I can't go right now", doing="",
                                                                       reachable=False, hidden=True, with_me=False),
              "person_now: hidden=True for someone in a locked room, and the room isn't given away", _zz_v)
        _zz_v = person_now("megumi")
        check(_zz_v == dict(place=None, name="Off campus", doing="", reachable=False, hidden=False, with_me=False),
              "person_now: someone off campus", _zz_v)
        check(person_now("nanami")["name"] == "Off campus" and person_now("sana")["name"] == "Off campus", "person_now: someone not on the roster is 'Off campus'")
        period = "Noon"
        companion = "megumi"
        _zz_v = person_now("megumi")
        check(_zz_v["with_me"] is True and _zz_v["place"] == here and _zz_v["name"] == "With me" and not _zz_v["reachable"] and not _zz_v["hidden"],
              "person_now: with_me=True for the companion", _zz_v)
        companion = None

        ## The Megumi row.
        day = 13            ## a Saturday
        check(weekday() == "Sat" and char_location("megumi", "Afternoon") == "library" and WEEKEND["megumi"]["Afternoon"] == "library",
              "Megumi reads in the Library on Saturday afternoons", char_location("megumi", "Afternoon"))
        day = 14
        check(weekday() == "Sun" and char_location("megumi", "Afternoon") == "library", "and on Sunday afternoons")
        day = 9
        check(char_location("megumi", "Afternoon") == "forest", "on a weekday afternoon he is where he was (the forest)")
        day = 13
        period = "Afternoon"
        here = "courtyard"
        zz_map(area="school")
        check("megumi" in zz_faces(renpy.get_screen("sb_map")) and person_now("megumi")["place"] == "library",
              "on a Saturday afternoon Megumi's face is beside the Library's pin", zz_faces(renpy.get_screen("sb_map")))
        zz_settle()
        shot("area_school_saturday", wait=0)
        day = 9

    ## --- 12. the worst case, and the pictures ---------------------------------------------------
    python:
        zz_everyone_in()
        gui.icon_words = _zz_icon_words0
        here = "office"
        gojo_in = True
        zz_map()
        renpy.set_focus("sb_map", "area_school")
        zz_render(0.5)
        _zz_tipnow = GetTooltip()
        _zz_lab = zz_texts("hover_label")
        renpy.hide_screen("sb_map")
        zz_worst("sb_map", hover="area_school")
        _zz_z = dict((n, int(renpy.display.screen.get_screen_variant(n).zorder)) for n in ("sb_map", "toasts", "hover_label"))
        check(isinstance(_zz_tipnow, tuple) and _zz_tipnow[1] == "area_school" and any(AREA_BY_KEY["school"]["blurb"] in s for s in _zz_lab)
              and _zz_z["hover_label"] > _zz_z["toasts"] > _zz_z["sb_map"],
              "the hover label is drawn by hover_label, above the map and the toasts (zorder %r)" % (_zz_z,), (_zz_tipnow, _zz_lab))
        ## Measured on the screens themselves, with the map still up: a
        ## queued toast and the objective banner must both draw nothing.
        toast("A reward", "stat")
        renpy.show_screen("objective_toast", "A banner over the map")
        zz_render(0.7)
        _zz_room = toast_room()
        _zz_drawn = (zz_texts("toasts"), zz_texts("objective_toast"))
        ## P2's objective_toast hides the banner with `showif hud_banner_ok()`:
        ## its words stay in the screen tree while nothing is drawn, so the
        ## banner is judged by P2's own test, not by the tree. Before P2 is
        ## in (no hud_banner_ok), an empty tree is the only proof there is.
        _zz_bok = getattr(store, "hud_banner_ok", None)
        _zz_nobanner = (not _zz_bok()) if callable(_zz_bok) else (not _zz_drawn[1])
        if _zz_room == (0, 0, 0):
            check(renpy.get_screen("sb_map") is not None and not any("A reward" in s for s in _zz_drawn[0]) and _zz_nobanner,
                  "zz_worst('sb_map'): no toast is drawn over the map and hud_banner_ok() is False (no objective banner)",
                  (_zz_drawn, callable(_zz_bok)))
        else:
            note("zz_worst('sb_map'): no toast drawn",
                 "waits for P2: toast_room() is still wave 0's stub over the map (%r), so toasts (and the objective banner) "
                 "draw over the map until P2's lanes are in; drawn now: %r" % (_zz_room, _zz_drawn))
        renpy.hide_screen("objective_toast")
        toast_clear()
        renpy.hide_screen("sb_map")
        zz_map(area="dorms")
        renpy.set_focus("sb_map", "row_dorm_common")
        zz_render(0.5)
        _zz_tipnow = GetTooltip()
        _zz_lab = zz_texts("hover_label")
        check(isinstance(_zz_tipnow, tuple) and _zz_tipnow[1] == "row_dorm_common" and "Dorm Common Room" in _zz_lab,
              "an area: the hovered pin's label is drawn by hover_label", (_zz_tipnow, _zz_lab))
        renpy.hide_screen("sb_map")
        zz_worst("sb_map", area="dorms", hover="row_dorm_common", name="worst_map_area")
        renpy.hide_screen("sb_map")
        here = "gate"
        period = "Morning"
        zz_worst("sb_map", layer="tokyo", hover="district_shibuya", name="worst_map_tokyo")
        renpy.hide_screen("sb_map")
        period = "Evening"
        night_out_ok = zz_night_yes
        zz_worst("sb_map", layer="tokyo", area="shibuya", hover="district_night", name="worst_map_district")
        renpy.hide_screen("sb_map")
    python:
        night_out_ok = zz_night_out_ok0

    ## The stand-in path: no icon pictures (the kanji seals, with their words),
    ## and no picture for one area (the clamped piece of the campus map).
    python:
        period = "Noon"
        here = "courtyard"
        renpy.loadable = zz_no_icons
        _zz_bg0 = AREA_BY_KEY["grounds"]["bg"]
        AREA_BY_KEY["grounds"]["bg"] = ZZ_STANDIN
        try:
            check(not icon_has_art("map") and not icon_has_art("place_library"), "stand-in: renpy.loadable says no for every icon picture")
            zz_map()
            zz_settle()
            shot("standin_level1", wait=0)
            _zz_unknown = [n for n in zz_icons(renpy.get_screen("sb_map")) if n == "?"]
            gui.icon_words = "never"
            zz_map()
            _zz_w1 = zz_words("sb_map")
            zz_map(area="dorms")
            _zz_w2 = zz_words("sb_map")
            gui.icon_words = _zz_icon_words0
            check(len(_zz_w1) <= 20 and len(_zz_w2) <= 16 and not _zz_unknown,
                  "stand-in: the word counts are the same without icon art (%d, %d), and no icon is a question mark" % (len(_zz_w1), len(_zz_w2)),
                  (_zz_w1, _zz_w2, _zz_unknown))
            zz_map(area="grounds")
            zz_settle()
            shot("standin_area", wait=0)
            check(zz_ids("row_") == ["row_dojo", "row_storehouse", "row_training", "row_training_yard"], "stand-in: the area view works on the stand-in picture", zz_ids("row_"))
            zz_map(layer="tokyo", area="harajuku")
            zz_settle()
            shot("standin_district", wait=0)
        finally:
            renpy.loadable = zz_loadable0
            AREA_BY_KEY["grounds"]["bg"] = _zz_bg0
            gui.icon_words = _zz_icon_words0

    ## Every icon name this screen draws is in ICONS (nothing automatic checks it).
    python:
        _zz_src = zz_source("game/ui_map.rpy") or ""
        _zz_names = set(zz_re.findall(r'icon(?:_btn)?\("([a-z_]+)"', _zz_src))
        check(_zz_names and all(n in ICONS or n in ("area_", "place_") for n in _zz_names)
              and all("area_" + a["key"] in ICONS for a in AREAS) and all(map_pin_icon(l) in ICONS for l in LOCATIONS)
              and all(map_pin_icon(l) == "area_" + area_of(l) for l in ("school_yard", "dorm_yard", "staff_yard", "training_yard", "trailhead")),
              "every literal icon name in ui_map.rpy is a key of ICONS", sorted(_zz_names))

    ## --- 13. a save on the map ---------------------------------------------------------------
    ## Screen scope is saved (R10): a save taken with an area open must
    ## pickle. This is a SHOWN map, whose scope is kept across a load; the
    ## game's own `call screen sb_map` is re-run on load with a fresh scope,
    ## so a player's save made with an area open reloads on level 1.
    python:
        renpy.hide_screen("sb_map")
        persistent.motion = _zz_motion0
        gui.icon_words = _zz_icon_words0
        zz_everyone_in()
        here = "courtyard"
        ## The harness's own scratch names (widgets, tooltips) are not the
        ## game's state: out of the store, two statements before the save,
        ## so the rollback entries it keeps don't hold them either.
        for _zz_k in [k for k in zz_builtins.list(store.__dict__) if k.startswith("_zz") and k != "_zz_k"]:
            delattr(store, _zz_k)
        del _zz_k
    show screen sb_map(area="dorms")
    $ zz_render(0.5)
    $ zz_render(0.1)
    python:
        if ZZ_SAVE[0] == 0:
            ZZ_SAVE[0] = 1
            del renpy.game.log.log[:-2]
            renpy.take_screenshot()
            renpy.save("zz_p1_map")
            check(renpy.can_load("zz_p1_map"), "a save made with an area open is written")
            ZZ_SAVE[0] = 2
            renpy.load("zz_p1_map")
    python:
        zz_render(0.4)
        check(ZZ_SAVE[0] == 2 and renpy.get_screen("sb_map") is not None and zz_zone() == "dorms"
              and zz_ids("row_") == sorted("row_" + l for l in places_in("dorms")),
              "...and a shown map reloads with its scope (nothing un-picklable is in the map's scope)", (ZZ_SAVE[0], zz_ids("row_")))
        renpy.hide_screen("sb_map")
        finish()
