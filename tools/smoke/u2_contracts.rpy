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
##
## It changes init data in place to test a gate (ART_PICTURES, RULE_LAYOUT,
## TIME_VARIANT) and puts every table back before the next section.

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

    $ finish()
