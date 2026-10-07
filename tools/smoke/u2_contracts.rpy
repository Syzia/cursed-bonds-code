## tools/smoke/u2_contracts.rpy -- the second UI overhaul's contracts
## (docs/UI2_DESIGN.md section 9; docs/UI2_CONTRACTS.md), package U0c2.
##
##   SMOKE_TIMEOUT=600 tools/smoke.sh u2_contracts                              # with its overlay
##   SMOKE_TIMEOUT=600 SMOKE_ASSETS=/var/empty tools/smoke.sh u2_contracts      # the bare tree
##
## In every package's standard set. Not edited after wave 0: a wave package
## that fills a stub keeps the stub's name, signature, owning file and return
## shape, and this file goes on passing.
##
## It runs in two states and says which it is in ("NOTE state"):
##
##   overlay  tools/smoke/assets/u2_contracts/game/ is laid over the scratch
##            copy (the default): test pictures for the thirteen off-campus
##            names, a My Room evening picture, the main menu's and the menu
##            ground's pictures under test names, a test manifest row. The
##            checks that say "with an overlay" run here.
##   bare     no overlay (SMOKE_ASSETS=/var/empty): the tree as it ships. The
##            checks that say "without the file" run here.
## Everything else runs in both. The package's acceptance is both runs.
##
## Sections:
##   A  the manifest: art_rev, art_fresh, art_stem; the four gates (bg_variant,
##      view_fg_path, view_pose, light_for_place), each falling back as K7
##      says; WORLD_VARIANTS and its registration; rule_layout's for_rev
##   B  the sidecar readers: the keys of view_<place>.json with today's
##      behaviour as the default, faces.json before the tables, pose_ files,
##      path_keep_clear and the validator's applied points, hover-label sides
##   C  "Show names" and the held N key; SPOT_PLANNED and the points lint
##      accepts for it; the generic dim state; the faces at an exit's tile
##   D  the night's tables and night_club_bg; the three new actions and the
##      activity swim_pool, registered and closed; K16's test (no romance in
##      the baths or at the pool); "Ask them along" and a friend bound for Tokyo
##
## It changes init data in place to test a gate (ART_PICTURES, RULE_LAYOUT,
## TIME_VARIANT) and puts every table back before the next section.
##
## It sets the focus (renpy.set_focus) to read a hover label, so it takes the
## pointer lock:
## smoke-pointer

init 999 python:
    import builtins
    import copy
    import inspect
    import json
    import os

    ZZC_OVERLAY = renpy.loadable("images/bg/club.png")

    ## The eleven places the overhaul added (plan 4.1); every other place is
    ## one of the 24 the game had before it.
    ZZ_NEW_PLACES = ("boys_dorm", "yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room",
                     "teachers_lounge", "teachers_dorm", "bathhouse", "sauna", "pool")
    ZZ_OLD_PLACES = builtins.tuple(l for l in LOC_ORDER if l not in ZZ_NEW_PLACES)

    class ZZCState(builtins.object):
        """What a section changed, so it can be put back. A builtins object:
        never saved, and rollback leaves it alone."""
        def __init__(self):
            self.art = None
            self.layout = None
            self.variant = None

    zzc = ZZCState()

    def zzc_hold():
        """Remember the three init tables the tests change in place."""
        zzc.art = copy.deepcopy(builtins.dict(ART_PICTURES))
        zzc.layout = copy.deepcopy(builtins.dict(RULE_LAYOUT))
        zzc.variant = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))

    def zzc_back():
        """Put them back, and forget every picture graded_bg has built."""
        art_rows()
        ART_PICTURES.clear()
        ART_PICTURES.update(copy.deepcopy(zzc.art))
        RULE_LAYOUT.clear()
        RULE_LAYOUT.update(copy.deepcopy(zzc.layout))
        TIME_VARIANT.clear()
        TIME_VARIANT.update(copy.deepcopy(zzc.variant))
        _BG_CACHE.clear()

    def zzc_art(**rows):
        """Lay manifest rows over the real ones (a row of None removes one)."""
        art_rows()
        for k, r in rows.items():
            if r is None:
                ART_PICTURES.pop(k, None)
            else:
                ART_PICTURES[k] = builtins.dict(r)
        _BG_CACHE.clear()

    def zzc_layout(name, data):
        """Lay a sidecar over the real one (None: as if the file were absent)."""
        RULE_LAYOUT[name] = builtins.dict() if data is None else json.loads(json.dumps(data))

    def zzc_tree(d):
        """Every displayable under d, d included."""
        out = builtins.list()
        d.visit_all(out.append)
        return out

    def zzc_alpha(wid, screen="sb_place"):
        """The product of the alpha of every Transform round a button of the
        place view (1.0 for a plain one); None when it is not there."""
        sc = renpy.get_screen(screen)
        w = renpy.get_displayable(screen, wid) if sc is not None else None
        if w is None:
            return None
        a = 1.0
        for d in zzc_tree(sc):
            if isinstance(d, renpy.display.transform.Transform) and d is not w and w in zzc_tree(d):
                a *= float(d.alpha)
        return round(a, 2)

    def zzc_alone(loc, per="Noon"):
        """Stand in a place with nobody in it (everyone pinned off campus
        for the hour), the place view up."""
        store.companion = None
        store.here = loc
        store.period = per
        for w in ROSTER_ORDER:
            pin(w, "-")
        ARRIVAL[0] = None
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_place")
        zz_render(0.3)

    def zzc_key(down):
        """Post the names key going down or coming up, as the keyboard would."""
        import pygame_sdl2
        k = getattr(pygame_sdl2, ICON_NAMES_KEY)
        pygame_sdl2.event.post(pygame_sdl2.event.Event(pygame_sdl2.KEYDOWN if down else pygame_sdl2.KEYUP,
                                                       key=k, mod=0, unicode=("n" if down else ""), scancode=0, repeat=False))
        zz_render(0.3)

    def zzc_keymap_uses(key):
        """The config.keymap rows that bind a key ("K_n"), under any modifier."""
        out = builtins.list()
        letter = key[2:].lower()
        for name, rows in config.keymap.items():
            for b in (rows or ()):
                last = builtins.str(b).split("_")
                tail = "_".join(last[-2:]) if len(last) >= 2 and last[-2] == "K" else last[-1]
                if tail.lower() in (key.lower(), letter):
                    out.append((name, b))
        return out

    def zzc_face_count(who, screen="sb_place"):
        """How many face chips of this person a shown screen draws (a screen
        copies a Transform it is given, so they are told by what they crop)."""
        chip = face_chip(who, HOT_FACE_SIZE)
        sc = renpy.get_screen(screen)
        n = 0
        for d in (zzc_tree(sc) if sc is not None else ()):
            if (isinstance(d, renpy.display.transform.Transform) and d.crop is not None and d.crop == chip.crop
                    and builtins.str(getattr(d.child, "filename", "")).endswith("side/%s_neutral.png" % who)):
                n += 1
        return n

    def zz_dim_test():
        """A test dim function: the reason, or "" (ZZC_DIM[0])."""
        return ZZC_DIM[0]

    def zz_two_faces(to):
        """A test path_faces: two people inside the Boys' Dormitory."""
        return ["megumi", "yuji", "zz_nobody"] if to == "boys_dorm" else []

    ZZC_DIM = builtins.list([""])

    def zzc_owner(fn, file):
        return callable(fn) and fn.__code__.co_filename.replace("\\", "/").endswith("game/" + file)

    def zzc_sig(fn):
        return builtins.str(inspect.signature(fn))


label zz_smoke:

    $ settle(day=2, period="Noon", here="courtyard")
    $ note("state", "overlay (tools/smoke/assets/u2_contracts)" if ZZC_OVERLAY else "bare (no overlay)")

    ## --- A. the manifest and the four gates (5.5, K7) -------------------------------
    python:
        zzc_hold()
        check(zzc_owner(art_rev, "art_manifest.rpy") and zzc_owner(art_fresh, "art_manifest.rpy")
              and zzc_owner(art_validate, "art_manifest.rpy") and zzc_owner(art_stem, "art_manifest.rpy")
              and zzc_sig(art_rev) == "(stem)" and zzc_sig(art_fresh).startswith("(stem"),
              "A: art_rev(stem), art_fresh(stem), art_stem and art_validate live in art_manifest.rpy")
        check(art_rev("courtyard") in (1, 2, 3, 4, 5) and isinstance(art_rev("courtyard"), int)
              and art_rev("zz_no_such_picture") == 1 and art_fresh("zz_no_such_picture") is True,
              "A: a picture with no row is revision 1 and fresh")
        check(art_stem("dorm") == "your_room" and art_stem("courtyard") == "courtyard" and art_stem("zz") == "zz"
              and all(art_stem(l) == (l if l != "dorm" else "your_room") for l in LOCATIONS),
              "A: a place's picture stem is its key, and your_room for My Room (K1)")
        check(art_parent("dorm_common_evening") == "dorm_common" and art_parent("your_room_night") == "your_room"
              and art_parent("fg_dorm_common") == "dorm_common" and art_parent("fg_dorm_common_night") == "dorm_common_night"
              and art_parent("light_dorm") == "your_room" and art_parent("light_dorm_night") == "your_room_night"
              and art_parent("pose_dorm_common__nobara__evening") == "dorm_common_evening"
              and art_parent("pose_dorm__yuji") == "your_room" and art_parent("pose_senpai_room__panda__night__asleep") == "senpai_room_night"
              and art_parent("courtyard") is None and art_parent("map_campus") is None and art_parent("city_night") is None,
              "A: what a picture was made from is read from its name (hour pictures, fg_, light_, pose_)")
        if ZZC_OVERLAY:
            check(art_rev("zz_test_picture") == 3 and art_fresh("zz_test_child") is False and art_fresh("zz_test_fresh") is True
                  and art_rev("zz_test_child") == 1,
                  "A (overlay): pictures.json is read from game/layout/: a row's rev, a stale child, a fresh child",
                  builtins.dict(art_rows()))
        else:
            check(not renpy.loadable("layout/pictures.json") or isinstance(art_rows(), builtins.dict),
                  "A (bare): with no manifest, or the tree's own, the rows are a dict", builtins.sorted(art_rows()))

        ## -- the manifest's rules, on rows laid in place
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(art_rev("dorm_common") == 2
              and art_fresh("dorm_common") is True
              and art_fresh("dorm_common_evening") is False and art_fresh("dorm_common_night") is False
              and art_fresh("fg_dorm_common") is False and art_fresh("fg_dorm_common_evening") is False
              and art_fresh("light_dorm_common") is False
              and art_fresh("pose_dorm_common__nobara__evening") is False
              and art_fresh("rooftop_evening") is True and art_fresh("fg_cafeteria") is True,
              "A: with the Common Room at revision 2 and no other row, everything made from its old picture is stale, and nothing else is")
        zzc_art(dorm_common_evening=dict(rev=2, kind="relight", of="dorm_common", of_rev=2),
                fg_dorm_common=dict(of="dorm_common", of_rev=2),
                fg_dorm_common_evening=dict(of="dorm_common_evening", of_rev=2),
                light_dorm_common=dict(of="dorm_common", of_rev=2))
        check(art_fresh("dorm_common_evening") and art_fresh("fg_dorm_common") and art_fresh("fg_dorm_common_evening")
              and art_fresh("light_dorm_common") and not art_fresh("dorm_common_night")
              and not art_fresh("pose_dorm_common__nobara__evening"),
              "A: a row that names its parent at the parent's revision is fresh again; a pose painted on the old evening picture is not")
        zzc_art(dorm_common=dict(rev=3, kind="inplace"))
        check(not art_fresh("dorm_common_evening") and not art_fresh("fg_dorm_common")
              and not art_fresh("fg_dorm_common_evening") and not art_fresh("light_dorm_common"),
              "A: when the parent moves on again, each row made for revision 2 is stale (and what was cut from a stale picture is too)")
        zzc_art(zz_bad=dict(rev=0), zz_bad2=dict(of="dorm_common"), zz_bad3=dict(kind="inplace"))
        _zz_f = art_validate()
        check(len(_zz_f) == 3 and all("zz_bad" in f for f in _zz_f) and not any("stale" in f for f in _zz_f),
              "A: art_validate reports a malformed row by name, and a stale row is not a finding", _zz_f)
        zzc_back()
        check(art_validate() == [], "A: the tree's own manifest lints clean", art_validate())

        ## -- gate 1: bg_variant (a stale hour picture is not used: the day picture, tinted)
        _zz_before = [(l, p, bg_variant(l, p)) for l in LOC_ORDER for p in PERIODS]
        check(bg_variant("dorm_common", "Evening") == "evening" and bg_variant("dorm_common", "Night") == "night"
              and bg_variant("rooftop", "Night") == "night" and bg_variant("dorm_common", "Noon") is None
              and bg_variant("zz", "Night") is None and bg_name("dorm_common", "Night") == "bg dorm_common night",
              "A: gate 1, today: bg_variant answers the hour's attribute where a painted hour exists")
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(bg_variant("dorm_common", "Evening") is None and bg_variant("dorm_common", "Night") is None
              and bg_name("dorm_common", "Night") == "bg dorm_common"
              and isinstance(graded_bg("dorm_common", "Night"), Transform)
              and getattr(graded_bg("dorm_common", "Night"), "_light_key", None) == ("dorm_common", "Night")
              and bg_variant("rooftop", "Night") == "night",
              "A: gate 1: with the day picture replaced, its old evening and night are not used: the day picture, tinted for the hour")
        ## an hour picture that is fresh, in a room with a foreground whose cut for that hour is stale
        zzc_art(dorm_common_evening=dict(rev=2, kind="relight", of="dorm_common", of_rev=2))
        check(world_fg_room("dorm_common") and not world_fg_room("rooftop") and bg_variant("dorm_common", "Evening") is None,
              "A: gate 1: in a foreground room a fresh hour picture is not used until its own foreground cut is fresh")
        zzc_art(fg_dorm_common_evening=dict(of="dorm_common_evening", of_rev=2))
        check(bg_variant("dorm_common", "Evening") == "evening" and bg_variant("dorm_common", "Night") is None,
              "A: gate 1: with its cut remade the evening shows, and the night, still the old one, does not")
        zzc_back()
        check(_zz_before == [(l, p, bg_variant(l, p)) for l in LOC_ORDER for p in PERIODS], "A: (tables put back)")

        ## -- gate 2: view_fg_path (a stale foreground is not used)
        check(view_fg_path("dorm_common", "Noon") == "images/fg/fg_dorm_common.png"
              and view_fg_path("dorm_common", "Night") == "images/fg/fg_dorm_common_night.png"
              and view_fg_path("cafeteria", "Night") == "images/fg/fg_cafeteria.png" and view_fg_path("dorm", "Noon") is None,
              "A: gate 2, today: view_fg_path answers the cut for the hour's picture")
        _zz_slots = view_slots("dorm_common", 2)
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(view_fg_path("dorm_common", "Noon") is None and view_fg_path("dorm_common", "Night") is None
              and view_fg_path("cafeteria", "Noon") == "images/fg/fg_cafeteria.png",
              "A: gate 2: with the room's picture replaced, the old cut is not laid over the new one")
        zzc_layout("view_dorm_common", None)
        check(view_slots("dorm_common", 2) == view_default_slots("dorm_common", 2),
              "A: gate 2: and a room whose table rows stand people behind that object falls back to the plain slots")
        zzc_art(fg_dorm_common=dict(of="dorm_common", of_rev=2))
        check(view_fg_path("dorm_common", "Noon") == "images/fg/fg_dorm_common.png"
              and view_fg_path("dorm_common", "Night") == "images/fg/fg_dorm_common.png"
              and view_slots("dorm_common", 2) == [builtins.tuple(r) for r in VIEW_SLOTS["dorm_common"][2]],
              "A: gate 2: recut for the new picture, the day cut is used again, at Night too (the day picture tinted, and its cut with it)")
        zzc_back()
        check(view_slots("dorm_common", 2) == _zz_slots, "A: (slots put back)")

        ## -- gate 3: view_pose (a stale pose is not used: the standing sprite)
        zzc_layout("pose_utahime_office", None)
        zzc_layout("view_utahime_office", dict(poses=dict(utahime=[100, 200, 300, 400])))
        fixture(period="Noon")
        _zz_p = view_pose("utahime", "utahime_office", "Noon")
        check(_zz_p == dict(image="images/place/pose_utahime_office__utahime.png", box=(100, 200, 300, 400)),
              "A: gate 3, today: a pose with no row is shown on the picture it was painted on (the box from view_<place>.json)", _zz_p)
        zzc_layout("pose_utahime_office", dict(poses=dict(utahime=[110, 210, 310, 410])))
        check(view_pose("utahime", "utahime_office", "Noon")["box"] == (110, 210, 310, 410)
              and view_pose_box("utahime_office", "utahime") == [110, 210, 310, 410],
              "A: view_pose reads pose_<place>.json before the poses key of view_<place>.json")
        zzc_layout("pose_utahime_office", dict(poses=dict(zz_other=[1, 2, 3, 4])))
        check(view_pose("utahime", "utahime_office", "Noon")["box"] == (100, 200, 300, 400),
              "A: a pose_ file without that person's box leaves the view_ file's box in force")
        zzc_art(utahime_office=dict(rev=2, kind="inplace"))
        check(view_pose("utahime", "utahime_office", "Noon") is None,
              "A: gate 3: with the room's picture replaced, the old pose is not shown (the standing sprite)")
        zzc_art(pose_utahime_office__utahime=dict(of="utahime_office", of_rev=2))
        check(view_pose("utahime", "utahime_office", "Noon") is not None,
              "A: gate 3: a pose installed on the revised picture (its row names revision 2) shows")
        zzc_back()

        ## -- gate 4: light_for_place (a stale light row is not used: the general row)
        _zz_day = light_for_place("classroom", "Noon")
        _zz_night = light_for_place("classroom", "Night")
        check(light_row("classroom") is None and light_row("classroom", "night") is None
              and _zz_day == INDOOR_LIGHT["Noon"] and _zz_night == INDOOR_LIGHT["Night"],
              "A: gate 4, today: with no light_<place>.json a room takes the general row")
        zzc_layout("light_classroom", {"": ["#f0e8d8", -0.02, 0.96, 0.5], "night": ["#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3]})
        check(light_row("classroom") == ("#f0e8d8", -0.02, 0.96, 0.5) and light_row("classroom", "") == light_row("classroom")
              and light_row("classroom", "night") == ("#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3)
              and isinstance(light_row("classroom"), builtins.tuple)
              and light_for_place("classroom", "Noon") == ("#f0e8d8", -0.02, 0.96, 0.5)
              and light_for_place("classroom", "Morning") == ("#f0e8d8", -0.02, 0.96, 0.5),
              "A: gate 4: a measured row wins while the day picture shows as painted (a row of four values, or six)")
        check(light_for_place("classroom", "Night") == INDOOR_LIGHT["Night"] and light_for_place("classroom", "Evening") == INDOOR_LIGHT["Evening"],
              "A: gate 4: at an hour that is only a tint the general row stays (the night row waits for the night picture)")
        zzc_art(classroom=dict(rev=2, kind="inplace"))
        check(light_row("classroom") is None and light_for_place("classroom", "Noon") == INDOOR_LIGHT["Noon"],
              "A: gate 4: with the room's picture replaced, the row measured on the old one is not used: the general row")
        zzc_art(light_classroom=dict(of="classroom", of_rev=2))
        check(light_for_place("classroom", "Noon") == ("#f0e8d8", -0.02, 0.96, 0.5),
              "A: gate 4: measured again on the new picture (its row names revision 2), it is used")
        zzc_layout("light_classroom", {"": ["f0e8d8", 0, 1, 0.5], "night": ["#c0c8f0", -0.1, 0.8]})
        check(light_row("classroom") is None and light_row("classroom", "night") is None
              and not light_row_ok(["#ffffff", 0, 1, True]) and not light_row_ok(["#ffffff", 0, 1, 0.5, 1])
              and light_row_ok(["#ffffff", 0, 1, 0.5]) and light_row_ok(("#ffffff", 0, 1, 0.5, 0, 1.0)),
              "A: a malformed light row is not used")
        zzc_back()
        ## a place with a painted hour: the measured row for that picture
        zzc_layout("light_rooftop", {"night": ["#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2]})
        check(light_for_place("rooftop", "Night") == ("#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2)
              and light_for_place("rooftop", "Evening") == PLACE_LIGHT[("rooftop", "evening")]
              and light_for_bg("bg rooftop night") == ("#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2)
              and light_for_bg("bg rooftop evening") == PLACE_LIGHT[("rooftop", "evening")],
              "A: a painted hour takes its own measured row, by place and by image name; the hour beside it keeps the table's")
        zzc_art(rooftop=dict(rev=2, kind="inplace"))
        check(light_for_place("rooftop", "Night") == OUTDOOR_LIGHT["Night"] and bg_variant("rooftop", "Night") is None,
              "A: and with the rooftop's day picture replaced the old night picture and its row both step aside")
        zzc_back()
        ## light.json, and six values through the two functions a save reads with
        zzc_layout("light", {"bg alley": ["#101820", -0.2, 0.7, 0.3, 2, 1.1], "bg zz_bad": ["#101820", 0]})
        check(light_for_bg("bg alley") == ("#101820", -0.2, 0.7, 0.3, 2, 1.1) and light_for_bg("bg city") == BG_LIGHT["bg city"]
              and light_for_bg("bg zz_bad") == NEUTRAL_LIGHT and light_for_bg("bg zz_nothing") == NEUTRAL_LIGHT,
              "A: light.json's row for a story picture comes before BG_LIGHT; a malformed row is skipped")
        zzc_back()
        check(zzc_sig(light_for_place) == "(loc, per)" and zzc_sig(light_for_bg) == "(name)" and zzc_sig(light_row) == "(loc, variant=None)"
              and zzc_owner(light_row, "lighting.rpy")
              and light_matrix(("#ffeedd", -0.05, 0.9, 0.5)) is light_matrix(["#ffeedd", -0.05, 0.9, 0.5])
              and light_matrix(("#ffeedd", -0.05, 0.9, 0.5, 3, 1.2)) is not None,
              "A: light_for_place and light_for_bg keep their signatures; light_matrix takes a row of four or six values")
        _zz_old = store.scene_light
        _zz_t = Transform("images/fx/contact_shadow.png")
        store.scene_light = ("#ffeedd", -0.05, 0.9, 0.37, 5, 1.25)
        _zz_r1 = _sprite_light(_zz_t, 0, 0)
        _zz_r2 = _shadow_light(_zz_t, 0, 0)
        check(_zz_r1 == 0.25 and _zz_r2 == 0.25 and abs(_zz_t.alpha - 0.37) < 1e-6,
              "A: a six-value scene_light lights a sprite and its shadow without error (the shadow's opacity is the fourth value)")
        store.scene_light = ("#ffeedd", -0.05, 0.9, 0.41)
        _shadow_light(_zz_t, 0, 0)
        check(abs(_zz_t.alpha - 0.41) < 1e-6 and inspect.signature(_shadow_light).parameters.keys() == inspect.signature(_sprite_light).parameters.keys()
              and zzc_sig(_shadow_light) == "(trans, st, at)",
              "A: and a four-value one, which is what an old save holds, still does (K9: same names, same signatures)")
        store.scene_light = _zz_old

        ## -- WORLD_VARIANTS (3.2, 5.7)
        _zz_rows = builtins.list(WORLD_VARIANTS)
        _zz_static = builtins.dict(dorm=("Evening", "Night"), infirmary=("Night",), rooftop=("Evening", "Night"), riverside=("Evening",),
                                   dorm_common=("Evening", "Night"), girls_dorm=("Night",))
        check(len(_zz_rows) == 56 and len(builtins.set((r[0], r[1]) for r in _zz_rows)) == 56
              and all(r[0] in LOCATIONS and r[1] in ("Evening", "Night") and r[2] == r[1].lower()
                      and r[3] == "images/bg/%s_%s.png" % (art_stem(r[0]), r[2]) for r in _zz_rows)
              and len([r for r in _zz_rows if r[0] in ZZ_OLD_PLACES]) == 37 and len([r for r in _zz_rows if r[0] not in ZZ_OLD_PLACES]) == 19,
              "A: WORLD_VARIANTS holds the 56 planned hour pictures as (place, period, attribute, file): 37 on old places, 19 on new",
              len(_zz_rows))
        check(not any(r[0] == "sauna" for r in _zz_rows)
              and not any(r[1] == "Night" and r[0] in ("office", "utahime_office", "gojo_office", "pool") for r in _zz_rows)
              and ("dorm", "Evening", "evening", "images/bg/your_room_evening.png") in _zz_rows
              and all((l, p) not in builtins.set((r[0], r[1]) for r in _zz_rows) for l, ps in _zz_static.items() for p in ps
                      if not (l == "dorm" and p == "Evening")),
              "A: no row for the sauna, for a place locked at Night, or for a picture that exists today (My Room's Evening is the one static cell a row replaces)")
        _zz_have = [r for r in _zz_rows if renpy.loadable(r[3])]
        check(all(TIME_VARIANT.get(r[0], {}).get(r[1]) == r[2] and renpy.has_image(builtins.tuple(LOCATIONS[r[0]]["bg"].split()) + (r[2],), exact=True)
                  for r in _zz_have)
              and all(TIME_VARIANT.get(r[0], {}).get(r[1]) in (None, "night") and not renpy.has_image(builtins.tuple(LOCATIONS[r[0]]["bg"].split()) + (r[2],), exact=True)
                      for r in _zz_rows if r not in _zz_have),
              "A: a row whose file exists (%d) has its image and its cell; a row whose file is missing (%d) has neither" % (len(_zz_have), len(_zz_rows) - len(_zz_have)))
        if ZZC_OVERLAY:
            check(TIME_VARIANT["dorm"]["Evening"] == "evening" and TIME_VARIANT["dorm"]["Night"] == "night"
                  and bg_variant("dorm", "Evening") == "evening" and bg_name("dorm", "Evening") == "bg your_room evening"
                  and renpy.has_image(("bg", "your_room", "evening"), exact=True)
                  and graded_bg("dorm", "Evening") == "bg your_room evening",
                  "A (overlay): a My Room evening file turns the Evening cell from night to evening, and it is shown as painted")
        else:
            check(TIME_VARIANT["dorm"]["Evening"] == ("evening" if renpy.loadable("images/bg/your_room_evening.png") else "night"),
                  "A (bare): without a My Room evening file the Evening cell is the night picture, as before",
                  TIME_VARIANT["dorm"])
        ## the registration's own rules, on a row whose file is known to exist
        _zz_tv = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))
        check(_validate_world() == [], "A: the world's validator is clean", _validate_world())
        TIME_VARIANT.setdefault("classroom", {})["Night"] = "night"
        _zz_f = [f for f in _validate_world() if "TIME_VARIANT" in f]
        check(len(_zz_f) == 1 and "classroom" in _zz_f[0] and "bg classroom night" in _zz_f[0],
              "A: lint reports a TIME_VARIANT cell with no image", _zz_f)
        zzc_back()

        ## -- rule_layout's for_rev (3.2)
        check(zzc_sig(rule_layout) == "(name)" and zzc_owner(rule_layout, "sb_rules.rpy")
              and rule_layout("zz_no_such_file") == {} and isinstance(rule_layout("hot_courtyard"), builtins.dict),
              "A: rule_layout(name) keeps its signature; {} for a file that does not exist")
        _zz_spots = dict(spots=dict(spot_vend=[1500, 700]))
        zzc_layout("hot_courtyard", _zz_spots)
        check(rule_layout("hot_courtyard") == _zz_spots and rule_layout("hot_courtyard") is not rule_layout("hot_courtyard")
              and rule_layout_stale("hot_courtyard") == "",
              "A: a file with no for_rev is always read (each call a fresh copy)")
        zzc_art(courtyard=dict(rev=2, kind="composed"))
        check(rule_layout("hot_courtyard") == _zz_spots,
              "A: and still read when its picture moves on (a room redone in place carries no for_rev)")
        zzc_layout("hot_courtyard", dict(_zz_spots, for_rev=2))
        zzc_layout("view_courtyard", dict(slots={"1": [[800, -40, 0.5, 0]]}, for_rev=2))
        check(rule_layout("hot_courtyard")["spots"] == _zz_spots["spots"] and view_slots("courtyard", 1) == [(800, -40, 0.5, 0)]
              and rule_validate() == [] and hot_spots_for("courtyard") is not None,
              "A: a file whose for_rev is its picture's revision is read")
        zzc_art(courtyard=dict(rev=3, kind="composed"))
        _zz_f = rule_validate()
        check(rule_layout("hot_courtyard") == {} and rule_layout("view_courtyard") == {}
              and view_slots("courtyard", 1) == [builtins.tuple(r) for r in VIEW_SLOTS["courtyard"][1]]
              and [h["x"] for h in hot_spots_for("courtyard") if h["id"] == "spot_vend"] != [1500],
              "A: a file whose for_rev does not match is ignored: the code's own numbers stand in", rule_layout("hot_courtyard"))
        check(len([f for f in _zz_f if "hot_courtyard" in f]) == 1 and len(_zz_f) == 1 and view_validate() == [] and hot_validate() == [] and path_validate() == [],
              "A: the mismatch is no finding of view_validate, hot_validate or path_validate", (view_validate(), hot_validate(), path_validate()))
        check(rule_layout_stale("hot_courtyard") != "" and "revision 3" in rule_layout_stale("hot_courtyard")
              and rule_layout_stale("view_courtyard") != "",
              "A: and it is said, with the two revisions, by the one function lint's rule reads", rule_layout_stale("hot_courtyard"))
        zzc_layout("area_school", dict(spots={}, for_rev=4))
        zzc_layout("hot_dorm", dict(spots={}, for_rev=2))
        zzc_art(area_school=dict(rev=4, kind="composed"), your_room=dict(rev=2, kind="composed"))
        check(rule_layout_stale("area_school") == "" and rule_layout_stale("hot_dorm") == ""
              and rule_layout_picture("hot_dorm") == "your_room" and rule_layout_picture("area_school") == "area_school"
              and rule_layout_picture("pose_dorm") is None and rule_layout_picture("light") is None,
              "A: for_rev is compared with the right picture: your_room for hot_dorm, area_<key> for an area's map")
        zzc_art(your_room=None)
        check(rule_layout_stale("hot_dorm") != "" and rule_layout("hot_dorm") == {},
              "A: a for_rev of 2 on a picture still at revision 1 is a mismatch too")
        zzc_back()
        check(rule_validate() == [] and zzc_owner(rule_validate, "sb_rules.rpy"),
              "A: the tree's own layout files carry no mismatched for_rev (lint's rule, rule_validate, is clean)", rule_validate())

    ## --- B. the sidecar readers (6.1, 3.1, D57) ---------------------------------------
    python:
        zzc_hold()
        ## -- the keys of view_<place>.json, each with today's behaviour as its default
        for _zz_l in LOC_ORDER:
            zzc_layout("view_" + _zz_l, None)
        check(all(view_floor(l) is None and view_floor(l, off=True) is None for l in LOC_ORDER)
              and all(view_talk(l) == (l in VIEW_FG_TALK) for l in LOC_ORDER) and view_talk("cafeteria") is True
              and all(view_cast(l, p) is None for l in LOC_ORDER for p in PERIODS)
              and all(view_slot_light(l, n, i, p) is None for l in LOC_ORDER for p in PERIODS for n in (1, 2, 3, 4) for i in range(n)),
              "B: with no view_<place>.json no place has a floor, a cast shadow or a slot light, and the foreground stays up in dialogue only in VIEW_FG_TALK's rooms")
        _zz_sq = [[100, 900], [1700, 900], [1700, 1060], [100, 1060]]
        zzc_layout("view_classroom", dict(
            floor=dict(on=[_zz_sq], off=[[[400, 950], [600, 950], [500, 1000]]]),
            scale=[900, 300, 700],
            slot_light={"": {"2": [None, ["#ffe8c0", 0.04]]}, "Evening": {"1": [["#ffd0a0", -0.02]]}, "night": {"1": [["#000000", 0.5]]}},
            cast={"": [35, 1.4, 0.3], "Evening": [70, 2.2, 0.4]},
            talk=True))
        check(view_floor("classroom") == [[(100, 900), (1700, 900), (1700, 1060), (100, 1060)]]
              and view_floor("classroom", off=True) == [[(400, 950), (600, 950), (500, 1000)]]
              and zzc_sig(view_floor).startswith("(loc") and zzc_owner(view_floor, "view_stage.rpy"),
              "B: view_floor(loc) is the sidecar's floor as a list of polygons; off=True the parts people may not stand on")
        check(view_slot_light("classroom", 2, 1, "Noon") == ("#ffe8c0", 0.04) and view_slot_light("classroom", 2, 0, "Noon") is None
              and view_slot_light("classroom", 1, 0, "Noon") is None and view_slot_light("classroom", 1, 0, "Evening") == ("#ffd0a0", -0.02)
              and view_slot_light("classroom", 1, 0, "Night") is None and view_slot_light("classroom", 2, 5, "Noon") is None,
              "B: view_slot_light reads the hour's row for that many people: the day row by day, a period's own row first, and no night row while the room has no night picture")
        check(view_cast("classroom", "Noon") == (35, 1.4, 0.3) and view_cast("classroom", "Evening") == (70, 2.2, 0.4)
              and view_cast("classroom", "Night") == (35, 1.4, 0.3) and view_talk("classroom") is True,
              "B: view_cast and view_talk read their keys (an hour with no row of its own takes the row of the picture that shows)")
        zzc_layout("view_cafeteria", dict(talk=False, floor=[_zz_sq], cast={"": [1, 2]}, slot_light={"": {"2": [["#fff", 0]]}}))
        check(view_talk("cafeteria") is False and view_floor("cafeteria") is None and view_cast("cafeteria", "Noon") is None
              and view_slot_light("cafeteria", 2, 0, "Noon") is None,
              "B: talk=false takes the foreground down in dialogue in a room of VIEW_FG_TALK; a malformed floor, cast or slot light is not used")
        zzc_layout("view_cafeteria", dict(talk="yes"))
        check(view_talk("cafeteria") is True, "B: a talk that is not true or false leaves the table's answer")
        zzc_back()

        ## -- faces.json (D57): blink faces and boxes, the tables as the fallback
        zzc_layout("faces", None)
        check(all(view_face_box(w, k) == (builtins.tuple(VIEW_FACE[w][k]) if k in VIEW_FACE[w] else None)
                  for w in VIEW_FACE for k in ("eyes", "mouth"))
              and all(view_blink_also(w) == builtins.tuple(VIEW_BLINK_ALSO.get(w, ())) for w in CAST)
              and view_blink_also("yuji") == ("happy", "sad", "serious", "surprised")
              and view_face_box("gojo", "eyes") is None and view_face_box("zz", "eyes") is None,
              "B: with no faces.json a person's boxes are VIEW_FACE's and their blink faces VIEW_BLINK_ALSO's")
        zzc_layout("faces", dict(blink_also=dict(megumi=["happy", "angry"]),
                                 eyes=dict(megumi=[300, 280, 120, 40], yuji=[330, 290, 92, 46]),
                                 mouth=dict(yuji=[352, 348, 58, 32])))
        check(view_blink_also("megumi") == ("happy", "angry") and view_blink_also("yuji") == ("happy", "sad", "serious", "surprised")
              and view_face_box("megumi", "eyes") == (300, 280, 120, 40) and view_face_box("megumi", "mouth") == builtins.tuple(VIEW_FACE["megumi"]["mouth"])
              and view_face_box("yuji", "eyes") == (330, 290, 92, 46) and view_face_box("yuji", "mouth") == (352, 348, 58, 32)
              and view_face_box("maki", "eyes") == builtins.tuple(VIEW_FACE["maki"]["eyes"]),
              "B: a test row in faces.json moves that person's boxes and names their blink faces; everyone without a row keeps the table's")
        if renpy.loadable("images/char/fx/fx_megumi_blink.png"):
            _zz_a = view_face_layers("images/char/megumi_angry.png")
            _zz_n = view_face_layers("images/char/megumi_neutral.png")
            check(len(_zz_a) == 1 and builtins.tuple(_zz_a[0].crop) == (300, 280, 120, 40) and (_zz_a[0].xpos, _zz_a[0].ypos) == (300, 280)
                  and len(_zz_n) == 2 and builtins.tuple(_zz_n[1].crop) == builtins.tuple(VIEW_FACE["megumi"]["mouth"]),
                  "B (overlay): the blink layer is cut at the test row's box, on a face the test row names; the mouth layer stays at the table's box",
                  [(l.crop, l.xpos, l.ypos) for l in _zz_a + _zz_n])
            zzc_layout("faces", None)
            _zz_a = view_face_layers("images/char/megumi_angry.png")
            _zz_n = view_face_layers("images/char/megumi_neutral.png")
            check(_zz_a == [] and len(_zz_n) == 2 and builtins.tuple(_zz_n[0].crop) == builtins.tuple(VIEW_FACE["megumi"]["eyes"]),
                  "B (overlay): with the row gone the blink is back on VIEW_BLINK_ALSO's faces and at VIEW_FACE's box")
        else:
            check(view_face_layers("images/char/megumi_angry.png") == [] or renpy.loadable("images/char/fx/fx_megumi_blink.png"),
                  "B (bare): with no blink picture a sprite takes no layer, whatever faces.json says")
        zzc_layout("faces", None)
        check(view_validate() == [], "B: view_validate is clean on the tables", view_validate())
        zzc_layout("faces", dict(blink_also=dict(megumi=["zz_face"], zz_who=["happy"], gojo=["happy"], maki="happy"),
                                 eyes=dict(yuji=[330, 290, 92, 80], toge=[1, 2, 3]), mouth=dict(yuji=[352, 348, 58, 32])))
        _zz_f = view_validate()
        check(len(_zz_f) == 6 and any("zz_face" in f for f in _zz_f) and any("zz_who" in f for f in _zz_f)
              and any("gojo" in f and "no eye box" in f for f in _zz_f) and any("maki" in f for f in _zz_f)
              and any("toge" in f for f in _zz_f) and any("yuji" in f and "below" in f for f in _zz_f),
              "B: lint refuses a faces.json row that names no sprite, nobody, a person with no eye box, a row of the wrong shape, and a mouth box that does not lie below the eyes", _zz_f)
        zzc_back()
        check(zzc_sig(view_face_layers) == "(path)" and zzc_owner(view_face_layers, "view_stage.rpy")
              and zzc_sig(view_pose) == "(who, loc, per=None)" and zzc_sig(view_slots) == "(loc, n)",
              "B: view_face_layers, view_pose and view_slots keep their signatures")

        ## -- path_keep_clear and the validator's applied points (3.1)
        def _zz_live(loc):
            side = rule_layout("hot_" + loc).get("spots") or {}
            out = builtins.set()
            for h in HOT_SPOTS:
                if h["place"] == loc and not h["id"].startswith("go_") and not h["id"].startswith("zz"):
                    p = side.get(h["id"]) or (h["x"], h["y"])
                    out.add((p[0], p[1]))
            return out
        check(zzc_sig(path_keep_clear) == "(loc)" and zzc_owner(path_keep_clear, "room_paths.rpy")
              and all(isinstance(path_keep_clear(l), builtins.list) and all(isinstance(p, builtins.tuple) and len(p) == 2 for p in path_keep_clear(l))
                      and builtins.set(path_keep_clear(l)) == _zz_live(l) and len(path_keep_clear(l)) == len(_zz_live(l)) for l in LOC_ORDER)
              and path_keep_clear("zz") == [] and len(path_keep_clear("courtyard")) >= 1,
              "B: path_keep_clear(loc) is a list of (x, y): the place's own hotspots where they sit now, each point once",
              [(l, path_keep_clear(l)) for l in LOC_ORDER if path_keep_clear(l)])
        check(path_validate() == [], "B: path_validate is clean", path_validate())
        _zz_vend = path_keep_clear("courtyard")[0]
        _zz_exit = [r for r in path_exits("courtyard") if r["to"] == "training_yard"][0]
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {})["go_courtyard__training_yard"] = [_zz_vend[0] + 60, _zz_vend[1] + 30]
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = path_validate()
        check(len(_zz_f) == 1 and "go_courtyard__training_yard" in _zz_f[0] and "hotspot" in _zz_f[0],
              "B: the spacing rule reads the exit's applied point: a sidecar that puts an exit 67 px from the vending machine fails, by name", _zz_f)
        _zz_side["spots"]["go_courtyard__training_yard"] = [_zz_exit["x"], _zz_exit["y"]]
        _zz_side["spots"]["spot_vend"] = [_zz_exit["x"] + 40, _zz_exit["y"] - 40]
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = path_validate()
        check(path_keep_clear("courtyard") == [(_zz_exit["x"] + 40, _zz_exit["y"] - 40)]
              and len(_zz_f) == 1 and "go_courtyard__training_yard" in _zz_f[0],
              "B: and the hotspot's applied point: a sidecar that moves the machine onto an exit fails too", _zz_f)
        ## the code's row may be wrong where the sidecar puts it right
        zzc_back()
        _zz_rows = builtins.list(PATH_EXITS["courtyard"])
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {})["go_courtyard__training_yard"] = [_zz_exit["x"], _zz_exit["y"]]
        zzc_layout("hot_courtyard", _zz_side)
        PATH_EXITS["courtyard"] = [(to, (_zz_vend[0] + 10 if to == "training_yard" else x), (_zz_vend[1] + 10 if to == "training_yard" else y))
                                   for to, x, y in _zz_rows]
        _zz_f = path_validate()
        PATH_EXITS["courtyard"] = _zz_rows
        check(_zz_f == [], "B: a code row that would break the rule is no finding while the sidecar's point is clear (a picture carries its numbers, K2)", _zz_f)
        zzc_back()
        check(path_validate() == [] and path_faces("boys_dorm") == [] and zzc_owner(path_faces, "room_paths.rpy") and zzc_sig(path_faces) == "(to)",
              "B: (tables put back); path_faces(to) is a stub that returns nobody")

        ## -- hover-label sides: the sidecar's tips, then the table, then where the tile is
        fixture(here="courtyard", period="Noon")
        zzc_layout("hot_courtyard", dict(spots=dict(rule_layout("hot_courtyard").get("spots") or {})))
        check(icon_tip_side(("To the Main Gate", "hot_go_courtyard__gate")) == "top"
              and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "left"
              and icon_tip_side(("x", "hot_spot_vend")) == "left" and icon_tip_side(("x", "hud_map")) == "bottom"
              and icon_tip_side(("x", "tag_yuji")) == "top" and icon_tip_side(("x", "zz_unknown")) == "left"
              and icon_tip_side("plain") == "left" and icon_tip_hot("hot_go_courtyard__gate") is None,
              "B: with no tips in the sidecar every label opens on the side it opened on before")
        zzc_layout("hot_courtyard", dict(spots=dict(rule_layout("hot_courtyard").get("spots") or {}),
                                         tips={"go_courtyard__gate": "right", "go_courtyard__training_yard": "bottom",
                                               "spot_vend": "top", "go_courtyard__dorm_yard": "sideways"}))
        check(icon_tip_side(("x", "hot_go_courtyard__gate")) == "right" and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "bottom"
              and icon_tip_side(("x", "hot_spot_vend")) == "top" and icon_tip_side(("x", "hot_go_courtyard__dorm_yard")) == "top"
              and icon_tip_side(("x", "hot_go_courtyard__school_yard")) == "top" and icon_tip_side(("x", "hud_map")) == "bottom",
              "B: a hot_ sidecar's tips win over the table, for an exit and for a hotspot; a side that is no side is ignored")
        fixture(here="school_yard")
        check(icon_tip_side(("x", "hot_go_courtyard__gate")) == "top" and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "left",
              "B: and they are the sides of the place I stand in: another place's sidecar says nothing here")
        fixture(here="courtyard")
        zzc_back()

    scene expression graded_bg()
    show screen sb_place
    python:
        zzc_hold()
        zz_render(0.2)
        _zz_tip = ("Vending machine\nA can of something cold.", "hot_spot_vend")
        _zz_gate = ("To the Main Gate", "hot_go_courtyard__gate")
        _zz_ids = [h["id"] for h in hot_spots_for("courtyard")]
        check("spot_vend" in _zz_ids and "go_courtyard__gate" in _zz_ids
              and icon_tip_where(_zz_tip, "left") == "left" and icon_tip_where(_zz_gate, "top") == "top"
              and icon_tip_side(_zz_tip) == "left" and icon_tip_side(_zz_gate) == "top",
              "B: on the place view, where the label fits, a tile with no side of its own opens where it did (left of a hotspot, above an exit)", _zz_ids)
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {}).update({"spot_vend": [200, 690], "go_courtyard__gate": [1300, 40]})
        zzc_layout("hot_courtyard", _zz_side)
        check(icon_tip_side(_zz_tip) == "right" and icon_tip_side(_zz_gate) == "bottom",
              "B: and from where the tile is when it does not: right of a hotspot at the left edge, below an exit at the top")
        zzc_back()
    hide screen sb_place

    ## --- C. names shown, the planned hotspots, the dim state, faces at an exit (7.3, D36) ---
    python:
        zzc_hold()
        ## -- SPOT_PLANNED and the validator
        _zz_reg = builtins.dict((h["id"], h) for h in HOT_SPOTS)
        check(isinstance(SPOT_PLANNED, builtins.tuple) and len(SPOT_PLANNED) == len(builtins.set(r[0] for r in SPOT_PLANNED))
              and all(isinstance(r, builtins.tuple) and len(r) == 3 and r[1] in LOCATIONS and r[2] in ("look", "act") for r in SPOT_PLANNED)
              and all(builtins.sum(1 for r in SPOT_PLANNED if r[0] == "bed_" + w) == 1 for w in ("yuji", "megumi", "panda", "toge", "nobara", "maki"))
              and all(("bed_" + w, world_home(w), "look") in SPOT_PLANNED for w in ("yuji", "megumi", "panda", "toge", "nobara", "maki"))
              and all((i, l, "act") in SPOT_PLANNED for i, l in (("bath_soak", "bathhouse"), ("bath_sauna", "sauna"), ("pool_swim", "pool"))),
              "C: SPOT_PLANNED is (id, place, kind) rows, each id once: %d rows (%d looks, %d actions), the six bed tags and the three bath and pool actions among them"
              % (len(SPOT_PLANNED), len([r for r in SPOT_PLANNED if r[2] == "look"]), len([r for r in SPOT_PLANNED if r[2] == "act"])))
        _zz_things = builtins.dict((l, [r[0] for r in SPOT_PLANNED if r[1] == l] + [h["id"] for h in HOT_SPOTS if h["place"] == l and not h["id"].startswith(("go_", "zz"))])
                                   for l in LOC_ORDER)
        check(all(_zz_things[l] for l in LOC_ORDER) and len(LOC_ORDER) == 35,
              "C: with the planned ids every one of the 35 places has a thing in the picture besides its exits",
              [l for l in LOC_ORDER if not _zz_things[l]])
        check(all(r[0] not in _zz_reg or (_zz_reg[r[0]]["place"], _zz_reg[r[0]]["kind"]) == (r[1], r[2]) for r in SPOT_PLANNED)
              and hot_planned("sauna") == {"bucket": ("bucket", "sauna", "look"), "bath_sauna": ("bath_sauna", "sauna", "act")}
              and len(hot_planned()) == len(SPOT_PLANNED) and zzc_owner(hot_planned, "sb_hotspots.rpy"),
              "C: a planned id that is registered already is registered in its planned place as its planned kind")
        check(hot_validate() == [], "C: hot_validate is clean", hot_validate())
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {}).update({"gateway": [900, 520], "straw_posts": [420, 760]})
        zzc_layout("hot_courtyard", _zz_side)
        check(hot_validate() == [] and path_validate() == [],
              "C: lint accepts a sidecar point for a hotspot that is planned for the place and not registered yet", hot_validate() + path_validate())
        _zz_side["spots"].update({"zz_gone": [900, 700], "torii": [700, 700], "gateway": [1500, 200], "straw_posts": "here"})
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = hot_validate()
        check(len(_zz_f) == 4 and any("zz_gone" in f and "planned" in f for f in _zz_f) and any("torii" in f and "planned" in f for f in _zz_f)
              and any("gateway" in f and "lane" in f for f in _zz_f) and any("straw_posts" in f and "two numbers" in f for f in _zz_f),
              "C: and refuses a stale point (an id that is neither registered nor planned for that place; one planned for another place), a planned point in a lane, and a point that is not two numbers", _zz_f)
        zzc_back()

        ## -- names shown: the setting, the held key, and what reads them
        _zz_pers = persistent.show_names
        check(persistent.show_names is False and ICON_NAMES_KEY == "K_n" and zzc_keymap_uses(ICON_NAMES_KEY) == []
              and zzc_keymap_uses("K_TAB") != [] and ICON_NAMES_HELD[0] is False and icon_names_shown() is False,
              "C: persistent.show_names defaults to False; the names key is N and is in no config.keymap list (Tab is: the skip toggle)",
              zzc_keymap_uses(ICON_NAMES_KEY))
        _zz_w0 = [icon_words_shown(n) for n in builtins.sorted(ICONS)]
        persistent.show_names = True
        check(icon_names_shown() is True and all(icon_words_shown(n) for n in ICONS) and icon_words_shown("map", "never") is False,
              "C: with the setting on, names are shown and an icon button wears its word (not where a screen says never)")
        persistent.show_names = False
        _zz_kd = store.icon_names_key_down
        store.icon_names_key_down = lambda: True
        ICON_NAMES_HELD[0] = True
        _zz_a = icon_names_shown()
        store.icon_names_key_down = lambda: False
        _zz_b = icon_names_shown()
        check(_zz_a is True and _zz_b is False and ICON_NAMES_HELD[0] is False,
              "C: while the key is held names are shown; a key that is found up again (a key-up the window never saw) stops it")
        store.icon_names_key_down = _zz_kd
        check([icon_words_shown(n) for n in builtins.sorted(ICONS)] == _zz_w0 and zzc_owner(icon_names_shown, "ui_icons.rpy")
              and zzc_owner(icon_words_shown, "ui_icons.rpy") and zzc_sig(icon_words_shown) == "(name, words=None)",
              "C: and with neither, every icon's word shows exactly when it did before")

        ## -- on the place view
        fixture(day=2)
        zzc_alone("courtyard")
        _zz_rows = hot_spots_for("courtyard")
        _zz_names = [hot_name(h) for h in _zz_rows]
        _zz_t0 = zz_texts("sb_place")
        check(len(_zz_rows) >= 5 and "Vending machine" in _zz_names and "To the Main Gate" in _zz_names and "To the Training Yard" in _zz_names
              and not any(n in _zz_t0 for n in _zz_names),
              "C: with names not shown no exit or hotspot of the Courtyard wears its name", [n for n in _zz_names if n in _zz_t0])
        _zz_btn0 = zz_buttons("sb_place")
        _zz_r0 = [zz_rect("sb_place", "hot_" + h["id"]) for h in _zz_rows]
        shot("names_off")
        persistent.show_names = True
        renpy.restart_interaction()
        _zz_t1 = zz_texts("sb_place")
        check(all(n in _zz_t1 for n in _zz_names) and zz_buttons("sb_place") == _zz_btn0
              and [zz_rect("sb_place", "hot_" + h["id"]) for h in _zz_rows] == _zz_r0,
              "C: with the setting on every exit wears where it leads and every hotspot its name; no button is added and none moves",
              [n for n in _zz_names if n not in _zz_t1])
        shot("names_on")
        persistent.show_names = False
        renpy.restart_interaction()
        zz_render(0.2)
        ## the key itself, through the screen's own key statements
        store.icon_names_key_down = lambda: True
        zzc_key(True)
        _zz_held = ICON_NAMES_HELD[0]
        _zz_t2 = zz_texts("sb_place")
        zzc_key(False)
        _zz_t3 = zz_texts("sb_place")
        store.icon_names_key_down = _zz_kd
        check(_zz_held is True and all(n in _zz_t2 for n in _zz_names) and ICON_NAMES_HELD[0] is False and not any(n in _zz_t3 for n in _zz_names),
              "C: N going down on the place view shows the names, and coming up takes them away (the key statements in hot_layer)",
              (_zz_held, ICON_NAMES_HELD[0]))
        ## a locked exit wears where it leads, not its lock's sentence
        fixture(period="Night")
        _zz_lock = [h for h in hot_spots_for("staff_yard") if h["id"] == "go_staff_yard__office"]
        check(len(_zz_lock) == 1 and path_locked("office") != "" and hot_name(_zz_lock[0]) == "To the Principal's Office"
              and _zz_lock[0]["icon"] == "lock",
              "C: a locked exit wears where it leads (its hover label still says why it is shut)")
        fixture(period="Noon")

        ## -- the dim state
        check(HOT_DIM == {} and hot_dim_reason(_zz_rows[0]) == "" and HOT_DIM_ALPHA == 0.45 and zzc_owner(hot_set_dim, "sb_hotspots.rpy")
              and zzc_sig(hot_set_dim) == "(hot_id, fn)",
              "C: no hotspot names a dim function today; hot_set_dim(hot_id, fn) is how one does")
        zzc_alone("courtyard")
        _zz_w = renpy.get_displayable("sb_place", "hot_spot_vend")
        _zz_act0 = _zz_w.action
        _zz_tip0 = _zz_w.style.tooltip if hasattr(_zz_w.style, "tooltip") else None
        check(zzc_alpha("hot_spot_vend") == 1.0 and isinstance(_zz_act0, Return) and _zz_act0.value == ("act", "spot_vend"),
              "C: the vending machine, not dim: drawn at full strength, and pressing it returns its action", (zzc_alpha("hot_spot_vend"), _zz_act0))
        _zz_rv = hot_set_dim("spot_vend", "zz_dim_test")
        check(_zz_rv is None and hot_validate() == [], "C: hot_set_dim returns None, and lint accepts a dim function that exists", hot_validate())
        renpy.restart_interaction()
        zz_render(0.2)
        check(zzc_alpha("hot_spot_vend") == 1.0 and renpy.get_displayable("sb_place", "hot_spot_vend").action.value == ("act", "spot_vend"),
              "C: a dim function that returns \"\" changes nothing")
        ZZC_DIM[0] = "Sold out till morning."
        renpy.restart_interaction()
        zz_render(0.2)
        _zz_w = renpy.get_displayable("sb_place", "hot_spot_vend")
        check(zzc_alpha("hot_spot_vend") == HOT_DIM_ALPHA and isinstance(_zz_w.action, NullAction)
              and hot_dim_reason([h for h in hot_spots_for("courtyard") if h["id"] == "spot_vend"][0]) == "Sold out till morning."
              and zz_rect("sb_place", "hot_spot_vend") is not None,
              "C: while it returns a reason the hotspot is drawn at the dimmed strength and pressing it does nothing; it stays where it was",
              (zzc_alpha("hot_spot_vend"), _zz_w.action))
        renpy.set_focus("sb_place", "hot_spot_vend")
        zz_render(0.3)
        _zz_tip = GetTooltip()
        check(_zz_tip == ("Sold out till morning.", "hot_spot_vend") and "Sold out till morning." in zz_texts("hover_label"),
              "C: and its hover label says the reason, under the hotspot's own key", _zz_tip)
        shot("dim")
        renpy.set_focus(None, None)
        ZZC_DIM[0] = ""
        HOT_DIM["zz_nothing"] = "zz_no_fn"
        _zz_f = hot_validate()
        check(len(_zz_f) == 2 and all("zz_nothing" in f for f in _zz_f),
              "C: lint refuses a dim function that does not exist, and one named for an unknown hotspot", _zz_f)
        HOT_DIM.clear()
        check(hot_validate() == [], "C: (the dim table put back)")

        ## -- an exit's tile shows the faces path_faces returns
        zzc_alone("dorm_yard")
        _zz_exit = [h for h in hot_spots_for("dorm_yard") if h["id"] == "go_dorm_yard__boys_dorm"][0]
        _zz_sc = renpy.get_screen("sb_place")
        check(hot_faces(_zz_exit) == [] and path_faces("boys_dorm") == []
              and zzc_face_count("megumi") == 0 and zzc_face_count("yuji") == 0,
              "C: with the stub, no exit's tile shows a face")
        _zz_pf = store.path_faces
        store.path_faces = zz_two_faces
        renpy.restart_interaction()
        zz_render(0.3)
        _zz_sc = renpy.get_screen("sb_place")
        _zz_all = zzc_tree(_zz_sc)
        check(hot_faces(_zz_exit) == ["megumi", "yuji"]
              and zzc_face_count("megumi") == 1 and zzc_face_count("yuji") == 1 and zzc_face_count("panda") == 0
              and hot_faces([h for h in hot_spots_for("dorm_yard") if h["id"] == "go_dorm_yard__dorm_common"][0]) == []
              and zz_rect("sb_place", "hot_go_dorm_yard__boys_dorm") is not None,
              "C: with path_faces patched to return two people, their two faces are drawn on that exit's tile and on no other (someone who is not in the cast is left out)")
        shot("exit_faces")
        store.path_faces = _zz_pf
        persistent.show_names = _zz_pers
        store.schedule_overrides = {}
        zzc_back()
    hide screen sb_place

    ## --- D. the night, the activities and Tokyo: hooks, and the K16 test (3.1, 7.6, D34) ---
    python:
        settle(day=2, period="Noon", here="courtyard")
        store.schedule_overrides = {}
        for _zz_w in ROSTER_ORDER:
            if _zz_w not in store.roster:
                store.roster.append(_zz_w)
        ## -- the night's tables
        check({"pool_swim", "swim_pool", "swim", "train", "lesson", "hold"} <= builtins.set(NIGHT_REST_BLOCKS) and night_validate() == [],
              "D: pool_swim and swim_pool are in NIGHT_REST_BLOCKS, and the night's validator knows both ids", night_validate())
        check(NIGHT_CARRY_LINES["nobara_room"] == NIGHT_CARRY_LINES["girls_dorm"] == NIGHT_CARRY_LINES["maki_room"]
              and NIGHT_CARRY_LINES["girls_dorm"] != NIGHT_CARRY_LINES["dorms"],
              "D: the two girls' rooms take the girls' corridor's walk-home line")
        _zz_lines = {}
        for _zz_l in ("nobara_room", "maki_room", "girls_dorm", "yuji_room", "dorm_common"):
            store.night_carried = _zz_l
            _zz_lines[_zz_l] = night_carry_line()
        store.night_carried = ""
        check(_zz_lines["nobara_room"] == _zz_lines["maki_room"] == _zz_lines["girls_dorm"] == NIGHT_CARRY_LINES["girls_dorm"]
              and _zz_lines["yuji_room"] == _zz_lines["dorm_common"] == NIGHT_CARRY_LINES["dorms"],
              "D: night_carry_line says it for a day that turned in either room (a boy's room still takes the dormitories')", _zz_lines)
        check(zzc_owner(night_club_bg, "sb_night.rpy") and zzc_sig(night_club_bg) == "(key)"
              and all(isinstance(night_club_bg(k), str)
                      and night_club_bg(k) == ("bg club" if renpy.has_image("bg club", exact=True) else night_bg(k)) for k in NIGHT_DISTRICTS)
              and all(renpy.has_image(night_club_bg(k), exact=True) for k in NIGHT_DISTRICTS),
              "D: night_club_bg(key) is an image name that exists: bg club once that picture exists, else the district's own night",
              [night_club_bg(k) for k in NIGHT_DISTRICTS])

        ## -- the three new actions: registered, closed, labels that only return
        _zz_pa = builtins.dict((a["id"], a) for a in PLACE_ACTIONS)
        check(all(i in _zz_pa for i in ("bath_soak", "bath_sauna", "pool_swim"))
              and (_zz_pa["bath_soak"]["locs"], _zz_pa["bath_soak"]["when"], _zz_pa["bath_soak"]["cost"]) == (("bathhouse",), "bath_ok", 1)
              and (_zz_pa["bath_sauna"]["locs"], _zz_pa["bath_sauna"]["when"], _zz_pa["bath_sauna"]["cost"]) == (("sauna",), "bath_ok", 1)
              and (_zz_pa["pool_swim"]["locs"], _zz_pa["pool_swim"]["when"], _zz_pa["pool_swim"]["cost"]) == (("pool",), "pool_ok", 1)
              and all(renpy.has_label(l) for l in ("sb_do_bath_soak", "sb_do_bath_sauna", "sb_do_pool_swim", "act_swim_pool"))
              and zzc_owner(bath_ok, "room_bath.rpy") and zzc_owner(pool_ok, "room_pool.rpy")
              and isinstance(bath_ok(), bool) and isinstance(pool_ok(), bool)
              and all(icon_for("act", i) == i for i in ("bath_soak", "bath_sauna", "pool_swim")),
              "D: bath_soak, bath_sauna and pool_swim are registered place actions with their labels and icons; bath_ok() and pool_ok() are bools")
        _zz_filled = bath_ok() or pool_ok()
        if not _zz_filled:
            _zz_off = [(l, p) for l in LOC_ORDER for p in PERIODS
                       if fixture(period=p) or builtins.set(a[0] for a in place_actions(l)) & {"bath_soak", "bath_sauna", "pool_swim"}]
            check(_zz_off == [], "D (the stubs): with bath_ok() and pool_ok() False, none of the three is offered in any place at any hour", _zz_off)
            fixture(period="Noon")
            _zz_b, _zz_p = store.bath_ok, store.pool_ok
            store.bath_ok = store.pool_ok = lambda: True
            check([a[0] for a in place_actions("bathhouse") if a[0].startswith(("bath_", "pool_"))] == ["bath_soak"]
                  and [a[0] for a in place_actions("sauna") if a[0].startswith(("bath_", "pool_"))] == ["bath_sauna"]
                  and [a[0] for a in place_actions("pool") if a[0].startswith(("bath_", "pool_"))] == ["pool_swim"]
                  and not [a[0] for a in place_actions("riverside") if a[0].startswith(("bath_", "pool_"))],
                  "D (the stubs): and the day the two functions answer True, each is offered in its own place and nowhere else")
            store.bath_ok, store.pool_ok = _zz_b, _zz_p
        else:
            note("D", "bath_ok() or pool_ok() is filled (wave 1): the stub-only checks are skipped")

    ## the labels only return (the stubs): nothing is spent, nothing is shown
    if not (bath_ok() or pool_ok()):
        $ _zz_before = (store.period, store.day, store.stamina, store.here, builtins.sorted(store.actions_today))
        call sb_do_bath_soak
        call sb_do_bath_sauna
        call sb_do_pool_swim
        call act_swim_pool("yuji")
        $ check(_zz_before == (store.period, store.day, store.stamina, store.here, builtins.sorted(store.actions_today)),
                "D (the stubs): the four labels only return: no hour, no stamina, no mark")

    python:
        ## -- the swim_pool row
        _zz_row, _zz_swim = ACT_BY_ID.get("swim_pool"), ACT_BY_ID["swim"]
        check(_zz_row is not None and ACTIVITIES[-1] is _zz_row
              and all(_zz_row[k] == _zz_swim[k] for k in ("kind", "min_bond", "cost", "per", "label"))
              and _zz_row["loc"] == ("pool",) and _zz_row["when"] == "pool_ok" and _zz_swim["loc"] == ("riverside",) and "when" not in _zz_swim
              and icon_for("do", "swim_pool") == "swim" and icon_for("do", "swim_pool") in ICONS,
              "D: the activity swim_pool is appended last: swim's kind, Bond 35, cost and hours, at the pool, hidden by pool_ok; it takes the swim icon; swim stays at the riverside", _zz_row)
        store.bonds = builtins.dict((w, 100) for w in CAST)
        store.spent_today = builtins.set()
        store.stamina = 100
        if not pool_ok():
            _zz_seen = [(w, l, p) for w in ROSTER_ORDER for l in LOC_ORDER for p in PERIODS
                        if fixture(period=p, here=l) or activity_state(_zz_row, w, l) != (False, None)
                        or any(a["id"] == "swim_pool" for a, ok, why in activities_for(w, l))]
            check(_zz_seen == [], "D (the stub): \"Swim together\" at the pool is offered nowhere, with nobody, at no hour, at Bond 100", _zz_seen[:5])
            _zz_p = store.pool_ok
            store.pool_ok = lambda: True
            fixture(period="Afternoon", here="pool")
            check(activity_state(_zz_row, "yuji", "pool") == (True, None) and activity_state(_zz_row, "yuji", "riverside")[0] is False
                  and activity_state(_zz_swim, "yuji", "riverside") == (True, None),
                  "D (the stub): the day pool_ok() answers True it is offered at the pool, and swim at the river as before")
            store.pool_ok = _zz_p

        ## -- K16: no romance in the baths or at the pool
        check(ACT_NO_ROMANCE == ("bathhouse", "sauna", "pool") and builtins.set(ACT_ROMANCE_KINDS) == {"romance", "confession", "intimate"}
              and builtins.set(a["kind"] for a in ACTIVITIES) == {"friend", "romance", "confession", "intimate"},
              "D: the three kinds K16 names are every kind there is besides friend")
        store.affection = builtins.dict((w, 200) for w in CAST)
        store.together = ["maki", "shoko"]
        store.schedule_overrides = {}
        store.companion = None
        fixture(day=6, period="Evening", here="bathhouse")       # a Saturday
        _zz_here = who_is_here("bathhouse")
        _zz_at = activities_for("maki", "bathhouse")
        check(weekday() == "Sat" and "maki" in _zz_here and "maki" in stage_people("bathhouse")[0]
              and not any(a["kind"] in ACT_ROMANCE_KINDS for a, ok, why in _zz_at)
              and not any(a["id"] in ("rom_close", "int_night") for a, ok, why in _zz_at)
              and any(a["id"] == "talk" and ok for a, ok, why in _zz_at)
              and not any(c.get("romance") for c in person_choices("maki", "bathhouse")),
              "D (K16): with Maki at the Bathhouse on a weekend Evening, Bond and affection high and the two of us together, neither \"Stay a while longer\" nor \"Stay the night\" is offered there (Talk is)",
              [(a["id"], ok, why) for a, ok, why in _zz_at])
        _zz_leak = []
        for _zz_l in ACT_NO_ROMANCE:
            for _zz_p in PERIODS:
                fixture(period=_zz_p, here=_zz_l)
                for _zz_w in ROSTER_ORDER:
                    for _zz_tg in (["maki", "shoko", "nobara"], []):
                        store.together = _zz_tg
                        for a in ACTIVITIES:
                            if a["kind"] in ACT_ROMANCE_KINDS and activity_state(a, _zz_w, _zz_l) != (False, None):
                                _zz_leak.append((_zz_l, _zz_p, _zz_w, a["id"]))
        ## and not by asking about another place while I stand in one of the three
        fixture(period="Evening", here="sauna")
        store.together = ["maki"]
        _zz_leak += [("from the sauna", a["id"]) for a in ACTIVITIES
                     if a["kind"] in ACT_ROMANCE_KINDS and activity_state(a, "maki", "rooftop") != (False, None)]
        check(_zz_leak == [],
              "D (K16): no romance, confession or intimate activity is offered in the Bathhouse, the Sauna or at the Pool: with anyone, at any hour, before the confession or after", _zz_leak[:6])
        store.together = ["maki", "shoko"]
        fixture(day=6, period="Night", here="maki_room")
        _zz_at = builtins.dict((a["id"], (ok, why)) for a, ok, why in activities_for("maki", "maki_room"))
        check(not world_asleep("maki") and "maki" in stage_people("maki_room")[0]
              and _zz_at.get("rom_close") == (True, None) and _zz_at.get("int_night") == (True, None),
              "D (K16): both are offered in her room on a Night she is awake (a Saturday)", _zz_at)
        fixture(day=2, period="Night", here="maki_room")
        check(world_asleep("maki") and "maki" in who_is_here("maki_room") and stage_people("maki_room") == ([], [])
              and rail_missions("maki_room") == [],
              "D (K16): and on a Night she is asleep (a Tuesday) she is not on the stage, so nothing at all is offered with her")

        ## -- 7.6: "Ask them along" and a friend bound for Tokyo
        _zz_inv = ACT_BY_ID["invite"]
        store.together = []
        store.affection = builtins.dict((w, 0) for w in CAST)
        _zz_got = {}
        for _zz_d, _zz_p in ((7, "Morning"), (7, "Noon"), (7, "Afternoon"), (7, "Evening"), (6, "Noon"), (6, "Afternoon")):
            fixture(day=_zz_d, period=_zz_p, here="cafeteria")
            for _zz_w in ("nobara", "maki", "yuji", "megumi"):
                _zz_got[(_zz_d, _zz_p, _zz_w)] = activity_state(_zz_inv, _zz_w, "cafeteria")
        check(all(_zz_got[(7, p, w)] == (False, None) for p in ("Noon", "Afternoon") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(7, p, w)] == (True, None) for p in ("Morning", "Evening") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(6, p, w)] == (True, None) for p in ("Noon", "Afternoon") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(d, p, "megumi")] == (True, None) for d, p, w in _zz_got if w == "megumi"),
              "D (7.6): \"Ask them along\" is not offered with Nobara, Maki or Yuji on a Sunday at Noon or in the Afternoon; it is on Sunday Morning and Evening, on a Saturday, and always with Megumi",
              builtins.sorted((k, v) for k, v in _zz_got.items() if v != (True, None)))
        fixture(day=7, period="Noon", here="cafeteria")
        pin("nobara", "cafeteria", per="Afternoon")
        _zz_a = activity_state(_zz_inv, "nobara", "cafeteria")
        store.schedule_overrides = {}
        check(_zz_a == (True, None) and WORLD_AWAY["nobara"] == {("Sun", "Afternoon"): "harajuku"},
              "D (7.6): someone a story pin keeps on campus that afternoon can be asked along (the same test as the clock's)", _zz_a)
        settle(day=2, period="Noon", here="courtyard")
        store.bonds = builtins.dict((w, 0) for w in CAST)

    $ finish()
