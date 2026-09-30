## tools/smoke/wp9_prologue.rpy -- WP9's harness: the prologue in first person
## (docs/PHASE1_DESIGN.md, section 7, "WP9", and 5.2).
##
##   tools/smoke.sh tools/smoke/wp9_prologue.rpy
##
## 1. Plays the prologue as label start does (chapter_one, chapter_one_b,
##    chapter_two, arc_one_open) under autoplay, choosing "Go with him." at the
##    offer, and checks that the step labels ran in order, the new flags,
##    technique, story_point markers, the blackout flag, Last Light's grey-out
##    and warm lamp, the fight call, that no name was asked for, and that the
##    player's own sprite was never on screen.
## 2. Replays: ch1b_the_other_road comes back to the harness (no restart),
##    ch1_gojo asks for no name, and every step stands on its own as a memory.
## 3. Old saves: prologue_catch_up plays the steps a pre-split save would
##    otherwise skip, and does nothing in a new game.
## 4. Static checks on the four files: say-with-attribute count, attributes
##    only on the tagged cast, two expression changes per speaker per step,
##    and nobody saying [mc_name] before Gojo asks for it.
## 5. Staged screenshots of each scene's staging at 1920x1080 (shots/wp9_prologue/).
##
## The alley fight: until WP2 merges, the combat engine waits for real input,
## so the harness answers `call combat` itself (recording the arguments). Once
## WP2's alley_curse has rounds=4, the real fight runs under autoplay and the
## harness checks it ends "down".

init 999 python:
    import builtins
    import os
    import re

    ZZ9 = builtins.dict(
        labels=builtins.list(), mc_seen=builtins.list(), interacts=0,
        dark_hidden=0, dark_bad=builtins.list(), still_seen=0, lamp_seen=0,
        inputs=0, combat=None, recording=False)

    ZZ9_STEPS = ["ch1_diner", "ch1_the_thing", "ch1_gojo", "ch1b_goodbye",
                 "ch2_arrival", "ch2_the_veil", "ch2_yaga", "ch2_first_years",
                 "arc_one_open"]
    ZZ9_WATCH = set(ZZ9_STEPS) | {"chapter_one", "chapter_one_b", "chapter_two",
                                  "ch1b_the_other_road", "prologue_catch_up"}
    ZZ9_FILES = ["ch1_alley.rpy", "ch1b_the_offer.rpy", "ch2_tour.rpy", "script.rpy"]
    ZZ9_TAGGED = {"mc", "yuji", "megumi", "nobara", "maki", "panda", "toge", "gojo",
                  "yaga", "ijichi", "shoko", "utahime", "sana"}
    ZZ9_EXPR = "neutral|happy|serious|angry|surprised|sad"

    def zz9_label_cb(name, abnormal):
        if name in ZZ9_WATCH:
            ZZ9["labels"].append(name)

    config.label_callbacks.append(zz9_label_cb)

    def zz9_master_at():
        sl = renpy.game.context().scene_lists
        return list(sl.layer_at_list.get("master", (None, []))[1])

    def zz9_interact_cb():
        """Every interaction: the player's own sprite is never up, the side
        images are hidden only while the alley is black, and Last Light's
        grey-out comes with its warm lamp."""
        ZZ9["interacts"] += 1
        where = renpy.get_filename_line()
        if renpy.showing("mc"):
            ZZ9["mc_seen"].append(where)
        if store.hide_side_images:
            ZZ9["dark_hidden"] += 1
            if not renpy.showing("bg black"):
                ZZ9["dark_bad"].append(where)
        if zz9_master_at():
            ZZ9["still_seen"] += 1
            if renpy.get_screen("last_light_lamp"):
                ZZ9["lamp_seen"] += 1

    ## Under autoplay's fast skipping a say line doesn't interact at all; it
    ## calls the fast-skipping callbacks instead. Watch both.
    config.start_interact_callbacks.insert(0, zz9_interact_cb)
    config.fast_skipping_callbacks.append(zz9_interact_cb)

    ## The name input never blocks the harness: count every call instead.
    def zz9_input(prompt="", default="", *args, **kwargs):
        ZZ9["inputs"] += 1
        return default

    renpy.input = zz9_input

    ## Menus: pick these captions when offered, otherwise autoplay's random pick.
    ZZ9_FORCE = builtins.list(["Go with him.", "\"Get behind me.\"", "Say nothing.",
                               "\"Why was it in an alley?\""])
    zz9_real_menu = menu

    def zz9_menu(items, **kwargs):
        for want in ZZ9_FORCE:
            for lab, val in items:
                if val is not None and lab == want:
                    return getattr(val, "value", val)
        return zz9_real_menu(items, **kwargs)

    menu = zz9_menu

    ## The fight (see the header).
    ZZ9_REAL_FIGHT = "rounds" in ENEMIES.get("alley_curse", {})
    if not ZZ9_REAL_FIGHT:
        config.label_overrides["combat"] = "zz9_combat"

    def zz9_read(fn):
        with open(os.path.join(config.gamedir, fn), encoding="utf-8") as f:
            return f.read().splitlines()

    def zz9_static():
        """(say-with-attribute count, [bad attribute uses], [labels short of
        two changes per speaker], [mc_name before the input])"""
        say = re.compile(r'^\s+([a-z_]\w*)(\s+@)?((?:\s+(?:%s))+)\s+"' % ZZ9_EXPR)
        plain = re.compile(r'^\s+([a-z_]\w*)\s+"')
        show = re.compile(r'^\s+show\s+([a-z_]\w*)\s+(%s)\b' % ZZ9_EXPR)
        n_attr = 0
        bad = []
        short = []
        early_name = []
        for fn in ZZ9_FILES:
            lab = None
            lines = {}
            changes = {}

            def close():
                if lab:
                    for w, n in lines.items():
                        if w in ZZ9_TAGGED and changes.get(w, 0) < min(2, n):
                            short.append("%s:%s (%d lines, %d changes)" % (lab, w, n, changes.get(w, 0)))

            asked = False
            for i, l in enumerate(zz9_read(fn), 1):
                m = re.match(r"^label\s+(\w+)", l)
                if m:
                    close()
                    lab, lines, changes = m.group(1), {}, {}
                    continue
                if fn == "ch1_alley.rpy":
                    if "renpy.input" in l:
                        asked = True
                    if not asked and "[mc_name]" in l and not l.lstrip().startswith("#"):
                        early_name.append("%s:%d" % (fn, i))
                m = say.match(l)
                if m and m.group(1) not in ("show", "scene", "hide", "with"):
                    n_attr += 1
                    who = m.group(1)
                    if who not in ZZ9_TAGGED:
                        bad.append("%s:%d %s" % (fn, i, who))
                    lines[who] = lines.get(who, 0) + 1
                    changes[who] = changes.get(who, 0) + 1
                    continue
                m = plain.match(l)
                if m and m.group(1) in ZZ9_TAGGED:
                    lines[m.group(1)] = lines.get(m.group(1), 0) + 1
                m = show.match(l)
                if m:
                    if m.group(1) not in ZZ9_TAGGED:
                        bad.append("%s:%d show %s" % (fn, i, m.group(1)))
                    changes[m.group(1)] = changes.get(m.group(1), 0) + 1
            close()
        return n_attr, bad, short, early_name

    def zz9_steps_seen(since=0):
        return [l for l in ZZ9["labels"][since:] if l in ZZ9_STEPS]


label zz9_combat(enemy, ally=None, flee_ok=True, bg=None):
    $ ZZ9["combat"] = (enemy, ally, flee_ok, bg, renpy.showing("curse big"))
    return "down"


label zz_smoke:

    ## An old-save-like starting point: another technique, no story point.
    python:
        fixture(technique="filament", mc_name="Ren", mc_surname="Tachibana")
        check(story_point is None and hide_side_images is False, "fresh defaults", (story_point, hide_side_images))
        check(all(renpy.has_label(s) for s, c in PROLOGUE_STEPS), "every PROLOGUE_STEPS label exists",
              [s for s, c in PROLOGUE_STEPS if not renpy.has_label(s)])
        check(renpy.has_label("ch1b_goodbye") and renpy.has_label("ch1b_the_other_road"), "the ch1b labels exist")
        check(prologue_plan("ch1_the_thing") == [s for s, c in PROLOGUE_STEPS][1:],
              "prologue_plan resumes at a sub-label", prologue_plan("ch1_the_thing"))
        check(prologue_plan("chapter_two") == ["ch2_arrival", "ch2_the_veil", "ch2_yaga", "ch2_first_years", "arc_one_open"],
              "prologue_plan maps a chapter to its steps", prologue_plan("chapter_two"))
        note("fight", "real WP2 fight under autoplay" if ZZ9_REAL_FIGHT else "answered by the harness (pre-WP2 engine)")

    ## --- 1. the prologue, as label start plays it ----------------------------------
    $ autoplay()
    call chapter_one
    python:
        check(story_point == "chapter_one_b", "chapter one ends pointing at the offer", story_point)
        check(technique == "timestop", "technique is timestop after the alley", technique)
        check(has_flag("sana_told_the_thing") and has_flag("sana_sketchbook"), "Sana tells the thing (flags)")
        check(has_flag("last_light_woke"), "Last Light wakes (flag)")
        check(has_flag("stood_in_front"), "the alley menu's flag stays on its choice")
        check(not zz9_master_at() and not renpy.get_screen("last_light_lamp"), "the grey-out is lifted after the moment", zz9_master_at())
        check(hide_side_images is False, "side images back on after the blackout")
    call chapter_one_b
    $ check(story_point == "ch2_arrival", "the goodbye ends pointing at the arrival", story_point)
    call chapter_two
    $ check(story_point == "arc_one_open", "chapter two ends pointing at the campus", story_point)
    call arc_one_open
    $ autoplay(False)

    python:
        _seen = zz9_steps_seen()
        check(_seen == ZZ9_STEPS, "the steps ran in order", _seen)
        check(ZZ9["labels"][:1] == ["chapter_one"] and "ch1b_the_other_road" not in ZZ9["labels"],
              "the road taken, not the other one", ZZ9["labels"])
        check(technique == "timestop", "technique == timestop", technique)
        for _f in ("sana_told_the_thing", "last_light_woke", "named_last_light", "saw_the_ridge_veil",
                   "chose_jujutsu", "enrolled", "settled_in", "watched_the_box", "wakuri_seeded"):
            check(has_flag(_f), "flag " + _f)
        check(not has_flag("saw_the_casket"), "the casket flag is gone")
        check(not ZZ9["mc_seen"], "mc never showing", ZZ9["mc_seen"][:5])
        note("lines and interactions watched", ZZ9["interacts"])
        check(ZZ9["interacts"] > 200, "the watcher saw the prologue", ZZ9["interacts"])
        check(ZZ9["dark_hidden"] >= 5 and not ZZ9["dark_bad"], "side images hidden only in the blackout",
              (ZZ9["dark_hidden"], ZZ9["dark_bad"][:3]))
        check(ZZ9["still_seen"] >= 3 and ZZ9["lamp_seen"] == ZZ9["still_seen"],
              "Last Light's grey-out, with the warm lamp, over the held second", (ZZ9["still_seen"], ZZ9["lamp_seen"]))
        check(ZZ9["inputs"] == 0, "no name input under autoplay", ZZ9["inputs"])
        check(mc_name == "Ren" and mc_surname == "Tachibana", "the names are kept when the input is skipped", (mc_name, mc_surname))
        if ZZ9_REAL_FIGHT:
            check(cb.get("key") == "alley_curse" and cb.get("over") == "down" and cb.get("bg") == "bg alley dark",
                  "the alley fight ends down, on the dark alley", (cb.get("key"), cb.get("over"), cb.get("bg")))
        else:
            check(ZZ9["combat"] == ("alley_curse", None, False, "bg alley dark", True),
                  "the alley fight: combat(alley_curse, None, False, bg alley dark), curse on screen", ZZ9["combat"])
        check(story_point == "arc_one_open", "story_point marks the campus", story_point)
        check(day == 1 and arc_start_day == day, "arc_start_day = day (D23)", (day, arc_start_day))
        check(save_version == SAVE_VERSION, "arc_one_open brings the state up to date", save_version)
        check(here == "courtyard" and period == "Morning", "the campus opens in the courtyard, morning", (here, period))

    ## --- 2. replays --------------------------------------------------------------------
    python:
        ## A replay's store is fresh, so smoke_autoplay is False inside it unless
        ## the scope sets it: the name-input replay leaves it out on purpose, to
        ## prove the _in_replay guard; the step replays set it so a real (WP2)
        ## fight answers itself.
        _scope = dict(mc_name="Ren", mc_surname="Tachibana", flags=set(["chose_jujutsu"]))
        _scope_auto = dict(_scope, smoke_autoplay=True)
        _inputs0 = ZZ9["inputs"]
        _sp0 = story_point
        _mark = len(ZZ9["labels"])
        autoplay()
    $ renpy.call_replay("ch1b_the_other_road", scope=_scope)
    python:
        autoplay(False)
        check("ch1b_the_other_road" in ZZ9["labels"][_mark:], "the other road played in a replay", ZZ9["labels"][_mark:])
        check(True, "call_replay(ch1b_the_other_road) returns to the harness (no restart)")
        autoplay()
    $ renpy.call_replay("ch1_gojo", scope=_scope)
    python:
        autoplay(False)
        check(ZZ9["inputs"] == _inputs0, "call_replay(ch1_gojo) asks for no name", ZZ9["inputs"] - _inputs0)
        _mark = len(ZZ9["labels"])
        _replays = ["ch1_diner", "ch1_the_thing", "chapter_one_b", "ch1b_goodbye", "ch2_arrival",
                    "ch2_the_veil", "ch2_yaga", "ch2_first_years"]
        autoplay()
    while _replays:
        $ _rl = _replays.pop(0)
        $ renpy.call_replay(_rl, scope=_scope_auto)
    python:
        autoplay(False)
        _got = [l for l in ZZ9["labels"][_mark:] if l in ZZ9_STEPS or l == "chapter_one_b"]
        check(_got == ["ch1_diner", "ch1_the_thing", "chapter_one_b", "ch1b_goodbye", "ch1b_goodbye",
                       "ch2_arrival", "ch2_the_veil", "ch2_yaga", "ch2_first_years"],
              "every step replays on its own", _got)
        check(story_point == _sp0 and has_flag("settled_in"), "replays leave the save alone", story_point)
        check(not ZZ9["mc_seen"], "mc never showing in the replays", ZZ9["mc_seen"][:5])
        check(ZZ9["inputs"] == _inputs0, "no name input in any replay", ZZ9["inputs"] - _inputs0)

    ## --- 3. old saves: the catch-up --------------------------------------------------------
    python:
        _mark = len(ZZ9["labels"])
        story_point = "ch2_yaga"      # as a pre-split save leaves it after ch2_the_veil
        autoplay()
    call arc_one_open
    python:
        autoplay(False)
        _got = zz9_steps_seen(_mark)
        ## arc_one_open's label comes first; its first statement is the catch-up.
        check(_got == ["arc_one_open", "ch2_yaga", "ch2_first_years"]
              and ZZ9["labels"][_mark:_mark + 2] == ["arc_one_open", "prologue_catch_up"],
              "arc_one_open first plays the steps an old save skipped", ZZ9["labels"][_mark:])
        check(story_point == "arc_one_open" and has_flag("enrolled"), "then opens the campus", story_point)
        _mark = len(ZZ9["labels"])
        story_point = None
        autoplay()
    call arc_one_open
    python:
        autoplay(False)
        _got = zz9_steps_seen(_mark)
        check(_got == ["arc_one_open"], "no story_point: the catch-up does nothing", _got)
        _mark = len(ZZ9["labels"])
        story_point = "ch2_arrival"
        autoplay()
    call prologue_catch_up("ch2_arrival")
    python:
        autoplay(False)
        check(zz9_steps_seen(_mark) == [], "a new game's chapter head: nothing to catch up", zz9_steps_seen(_mark))

    ## --- 4. static checks on the four files ----------------------------------------------------
    python:
        _n, _bad, _short, _early = zz9_static()
        check(_n >= 30, "at least 30 say-with-attribute uses", _n)
        note("say-with-attribute uses", _n)
        check(not _bad, "attributes only on the 13 tagged characters", _bad)
        check(not _short, "two expression changes per speaking character per step", _short)
        check(not _early, "nobody says [mc_name] before Gojo asks", _early)

    ## --- 5. staged screenshots ---------------------------------------------------------------
    python:
        mc_name, mc_surname = "Ren", "Tachibana"
        flags.discard("settled_in")

    scene bg diner
    show sana happy at pos_c
    $ sana("That's leadership. I'd follow that woman into a war.", interact=False)
    $ shot("01_diner")

    $ hide_side_images = True
    scene bg black
    $ sana("There's one at the end of this alley.", interact=False)
    $ shot("02_blackout_sana")
    $ hide_side_images = False

    scene bg alley dark
    show curse big at pos_loom
    $ curse2("She could see me too. She kept looking right at me.", interact=False)
    $ shot("03_alley_dark_curse")

    show layer master at last_light_still
    show screen last_light_lamp
    $ narrator("One light stays on: the lamp over the fire door, caught in the instant before it went out. Warm. The only warm thing left.", interact=False)
    $ shot("04_last_light", wait=1.2)
    python:
        check(bool(zz9_master_at()) and renpy.get_screen("last_light_lamp") is not None, "staged Last Light renders")
    hide screen last_light_lamp
    show layer master

    scene bg alley
    show gojo serious at pos_c
    $ mc("[mc_surname]. [mc_surname] [mc_name].", interact=False)
    $ shot("05_gojo_alley_mc_side")

    show gojo happy at pos_c
    $ gojo("Zankō. Last Light. Somebody has to put something on the form.", interact=False)
    $ shot("06_offer")

    scene bg home_living
    show mother at pos_cl
    show father at pos_r
    $ mother("They said it was the power cut. That she fell.", interact=False)
    $ shot("07_parents")

    scene bg car
    show ijichi surprised at pos_c
    $ ijichi("Oh — sorry. I should have said. Kiyotaka Ijichi.", interact=False)
    $ shot("08_car_ijichi")

    scene bg ridge_veil
    show gojo serious at pos_c
    $ gojo("Don't go near it. Not the ridge path past the rope markers.", interact=False)
    $ shot("09_ridge_veil")

    scene bg office
    show yaga serious at pos_c
    $ yaga("So I'll ask you directly. Why do you want to be here?", interact=False)
    $ shot("10_yaga")

    scene bg training
    show gojo happy at pos_fl
    show yuji happy at pos_l
    show nobara neutral at pos_c
    show megumi neutral at pos_r
    $ gojo("Right — first-years. There are three of them and now there are four of you.", interact=False)
    $ shot("11_first_years_with_gojo")

    hide gojo
    $ nobara("Tomorrow you're doing something, though. I'm not running a hospice.", interact=False)
    $ shot("12_first_years_trio")

    scene bg your_room
    $ narrator("My room: a bed, a desk, and a window that faces a mountain that is also, somehow, Tokyo.", interact=False)
    $ shot("13_arc_one_open")

    $ check(not renpy.showing("mc"), "mc not showing at the end")
    $ finish()
