################################################################################
## Cursed Bonds — sandbox interface: the place view and the person view.
##
## WP7 (PHASE1_DESIGN.md 4.4, 4.5).
##
## Screens return tuples to sb_loop.rpy:
##   sb_place  ("map",) ("journal", tab) ("char", who) ("act", id)
##             ("mission", mid) ("dev",)
##   sb_char   ("do", aid, who) ("mission", mid) ("act", id) ("cancel",)
## Nothing here changes game state.
##
## The HUD and the toasts are in ui_hud.rpy, the map in ui_map.rpy, and the
## journal in ui_journal.rpy. What someone is doing at a place (AMBIENT), how
## big people stand in each place (PLACE_STAGING) and the face they look up
## with (PERSON_GREET_EXPR) are tables below: add a row, no code.
################################################################################

init python:
    import builtins
    import time as _sb_time

    ## What people are doing (4.4) -------------------------------------------------
    ##
    ## (who, place) -> (caption, expression). (who, None) is that person's
    ## caption anywhere else. Expressions: neutral / happy / serious / angry /
    ## surprised / sad.

    AMBIENT = {
        ("yuji", "cafeteria"):      ("halfway through an enormous bowl", "happy"),
        ("yuji", "courtyard"):      ("at the vending machine", "neutral"),
        ("megumi", "classroom"):    ("reading", "serious"),
        ("megumi", "forest"):       ("with a Divine Dog", "neutral"),
        ("megumi", "riverside"):    ("with a Divine Dog", "neutral"),
        ("nobara", "dorm_common"):  ("on her phone", "neutral"),
        ("nobara", "rooftop"):      ("leaning on the railing", "neutral"),
        ("maki", "training"):       ("drilling with a staff", "serious"),
        ("maki", "dojo"):           ("drilling with a staff", "serious"),
        ("panda", "courtyard"):     ("sparring with Toge", "happy"),
        ("toge", "cafeteria"):      ("with onigiri", "happy"),
        ("gojo", "gojo_office"):    ("eating mochi in front of the TV", "happy"),
        ("gojo", "ridge"):          ("sitting just outside the veil", "serious"),
        ("utahime", None):          ("buried in paperwork", "serious"),
        ("shoko", None):            ("with coffee", "neutral"),
        ("yaga", "office"):         ("sewing a cursed doll", "serious"),
        ("ijichi", "gate"):         ("on the phone beside the car", "neutral"),

        ## Each person's fallback, anywhere else.
        ("yuji", None):             ("killing time, loudly", "happy"),
        ("megumi", None):           ("hands in his pockets", "neutral"),
        ("nobara", None):           ("waiting for something", "neutral"),
        ("maki", None):             ("a staff over one shoulder", "serious"),
        ("panda", None):            ("people-watching", "happy"),
        ("toge", None):             ("hands in his sleeves", "neutral"),
        ("gojo", None):             ("eating something sweet", "happy"),
        ("yaga", None):             ("arms folded", "serious"),
        ("ijichi", None):           ("checking his phone", "neutral"),
    }

    ## Anyone without a row at all.
    AMBIENT_FALLBACK = ("waiting for something", "neutral")

    ## Rows that name someone else: (who, place) -> (the person the caption
    ## needs, the caption while they're not there). The schedule never puts
    ## Toge in the courtyard when Panda is, so Panda usually waits.
    AMBIENT_NEEDS = {
        ("panda", "courtyard"): ("toge", ("waiting for a sparring partner", "happy")),
    }

    ## How big people stand in a place, and how far up (4.4). A place not
    ## listed uses zoom 0.52 and y 0.
    PLACE_STAGING = {
        "dorm":        dict(zoom=0.56, y=0),
        "infirmary":   dict(zoom=0.54, y=0),
        "rooftop":     dict(zoom=0.50, y=0),
        "gate":        dict(zoom=0.50, y=0),
        "forest":      dict(zoom=0.50, y=0),
        "riverside":   dict(zoom=0.50, y=0),
        "ridge":       dict(zoom=0.48, y=0),
    }

    ## The face someone looks up with when I walk over (4.4, 4.5, 5.1).
    PERSON_GREET_EXPR = {
        "yuji": "happy", "megumi": "neutral", "nobara": "happy", "maki": "serious",
        "panda": "happy", "toge": "happy", "gojo": "happy", "utahime": "serious",
        "shoko": "neutral", "yaga": "serious", "ijichi": "surprised",
    }

    EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")

    ## Where the stage puts 1-4 people (x centres, 4.4).
    STAGE_CENTRES = {1: [700], 2: [470, 930], 3: [330, 700, 1070], 4: [240, 540, 860, 1160]}

    def ambient_of(who, loc):
        """WP7. (caption, expression) for someone at a place, e.g.
        ("halfway through an enormous bowl", "happy") (4.4). A caption that
        names someone else (AMBIENT_NEEDS) only shows while they're there."""
        row = AMBIENT.get((who, loc))
        need = AMBIENT_NEEDS.get((who, loc))
        if row and need and need[0] not in who_is_here(loc):
            return need[1]
        return row or AMBIENT.get((who, None)) or AMBIENT_FALLBACK

    def greet_expr(who):
        """WP7. The expression someone looks up with (PERSON_GREET_EXPR)."""
        return PERSON_GREET_EXPR.get(who, "neutral")

    def person_image(who, expr=None):
        """WP7. The image name "<who> <expr>", or plain "<who>" when that
        expression has no picture."""
        name = "%s %s" % (who, expr or greet_expr(who))
        return name if renpy.has_image(name) else who

    def stage_people(loc=None):
        """WP7. (on stage, overflow): who is at the place, the companion first,
        at most four on stage."""
        folk = who_is_here(loc)
        c = store.companion
        if c in folk:
            folk.remove(c)
            folk.insert(0, c)
        return folk[:4], folk[4:]

    def stage_x(who, loc=None):
        """WP7. The x centre someone stands at in the place view (700 if
        they are not on the stage)."""
        on, _extra = stage_people(loc)
        if who in on:
            return STAGE_CENTRES[len(on)][on.index(who)]
        return 700

    ## Missions, as the screens draw them --------------------------------------------

    def _mget(rec, key, default=None):
        if isinstance(rec, dict):
            return rec.get(key, default)
        return getattr(rec, key, default)

    def mission_view(m):
        """WP7. (mid, title, hint) for an entry of missions_here() or
        missions_with(), which may be a mission id or a mission record."""
        if isinstance(m, str):
            rec = (getattr(store, "MISSION_BY_ID", None) or {}).get(m)
            mid = m
        else:
            rec = m
            mid = _mget(m, "id")
        title = (_mget(rec, "title") if rec is not None else None) or builtins.str(mid)
        hint = ""
        if rec is not None:
            hint = _mget(rec, "objective") or _mget(rec, "summary") or ""
        return mid, title, hint

    ## The action card (4.4) ---------------------------------------------------------

    def place_actions(loc):
        """WP7. (id, label, hint, period_cost) for everything I can do here
        (4.4): the place's own actions, Hold the hour, the registered actions
        (registered_place_actions), then Wait. Once-a-day actions drop out
        once used (D26). Explore mode: the Time step and explore actions."""
        if store.explore_mode:
            nxt = PERIODS[(PERIODS.index(store.period) + 1) % len(PERIODS)]
            return ([("explore_time", "Time: %s" % nxt, "Step to the next time of day. Nothing is spent.", 0)]
                    + registered_place_actions(loc))
        done = store.actions_today
        a = []
        if loc == "dorm":
            a.append(("sleep", "Sleep", "End the day. Everything comes back.", 0))
            a.append(("study", "Study", "Insight. Quiet. Nobody bothers me.", 1))
        if loc in ("training", "ridge", "forest", "dojo"):
            a.append(("train", "Train", "Push my cursed energy. Costs stamina.", 1))
        if loc == "riverside":
            a.append(("swim", "Swim", "Cold. Clears my head.", 1))
            a.append(("train", "Train", "Rough ground. Good footwork.", 1))
        if loc == "cafeteria":
            a.append(("eat", "Eat", "Stamina. Everyone's here at noon.", 0))
        if loc == "infirmary" and "rest" not in done:
            a.append(("rest", "Get patched up", "Rest, and Shoko if she's in. Once a day.", 0))
        if loc == "storehouse" and not has_flag("armory_open") and "racks" not in done:
            a.append(("tools", "Look through the racks", "Look, don't take. Once a day.", 0))
        if loc == "courtyard":
            a.append(("train", "Practice", "Forms, in the open, where people can see.", 1))
        if loc == "classroom":
            a.append(("study", "Study", "Insight. The textbook is four hundred pages.", 1))
        if loc == "rooftop":
            a.append(("think", "Sit a while", "Nothing happens. That's the point.", 1))
        if "hold" not in done:
            a.append(("hold", "Hold the hour", "Last Light. Once a day; costs reserve.", 0))
        a.extend(registered_place_actions(loc))
        a.append(("wait", "Wait", "Let the period pass.", 1))
        return a

    ## The arrival caption (4.3, D35) ------------------------------------------------
    ##
    ## Shown once per change of (day, period, here). The key lives outside the
    ## store (a builtins list made at init, never reassigned), so the caption
    ## also shows after a load.

    ARRIVAL = builtins.list([None, 0.0])
    ARRIVAL_IN, ARRIVAL_HOLD, ARRIVAL_OUT = 0.3, 2.5, 0.5

    def arrival_caption():
        """WP7. When the caption for the current (day, period, here) started
        (wall clock), or None once it has faded."""
        key = (store.day, store.period, store.here)
        now = _sb_time.time()
        if ARRIVAL[0] != key:
            if renpy.predicting():
                return None
            ARRIVAL[0] = key
            ARRIVAL[1] = now
        if now - ARRIVAL[1] < ARRIVAL_IN + ARRIVAL_HOLD + ARRIVAL_OUT:
            return ARRIVAL[1]
        return None

    def _arrival_reset():
        ARRIVAL[0] = None

    config.after_load_callbacks.append(_arrival_reset)

    def _arrival_fx_fn(t0):
        def fn(trans, st, at):
            age = _sb_time.time() - t0
            if age < ARRIVAL_IN:
                trans.alpha = age / ARRIVAL_IN
                return 0
            if age < ARRIVAL_IN + ARRIVAL_HOLD:
                trans.alpha = 1.0
                return ARRIVAL_IN + ARRIVAL_HOLD - age
            trans.alpha = max(0.0, 1.0 - (age - ARRIVAL_IN - ARRIVAL_HOLD) / ARRIVAL_OUT)
            return 0 if trans.alpha > 0 else None
        return fn

    def arrival_fx(t0):
        """WP7. Fades the arrival caption by the wall clock (0.3 in, 2.5
        held, 0.5 out)."""
        return Transform(function=_arrival_fx_fn(t0))

    ## The person view (4.5) -------------------------------------------------------------

    _YEAR_WORDS = {"1st year": "First-year", "2nd year": "Second-year", "3rd year": "Third-year"}

    def role_line(who):
        """WP7. "First-year · Grade 2", "Teacher · Off the scale", "Doctor"."""
        year = CAST.get(who, {}).get("year", "")
        year = _YEAR_WORDS.get(year, year)
        st = npc_stats(who) or {}
        if st.get("off_scale"):
            g = "Off the scale"
        elif st.get("grade") is not None:
            g = grade_label(st.get("grade"))
        else:
            return year or st.get("role", "")
        return " · ".join(p for p in (year, g) if p)

    def unlock_line(who):
        """WP7. The footer hint: "Closer: Sit out with them — at Bond 50"."""
        nx = next_unlock(who)
        if not nx:
            return ""
        return "Closer: %s — at %s" % (nx[1], nx[2])

    def person_thread(who):
        """WP7. (title, stage, stages) of someone's thread once it has
        started, or None."""
        tid = next((t for t in THREAD_ORDER if THREADS[t]["who"] == who), None)
        if not tid:
            return None
        stage = thread_stage(tid)
        if stage < 0:
            return None
        return THREADS[tid]["title"], stage, len(THREADS[tid]["stages"])

    ## The validator (WP7 task 5) -----------------------------------------------------

    def _validate_wp7_tables():
        out = []
        places = set(LOCATIONS)
        for (who, loc), (cap, expr) in AMBIENT.items():
            if who not in CAST:
                out.append("AMBIENT: %r is not a person" % who)
            if loc is not None and loc not in places:
                out.append("AMBIENT: %r is not a place" % loc)
            if expr not in EXPRESSIONS:
                out.append("AMBIENT (%s, %s): %r is not an expression" % (who, loc, expr))
            elif who in CAST and not renpy.has_image("%s %s" % (who, expr)):
                out.append("AMBIENT (%s, %s): no image '%s %s'" % (who, loc, who, expr))
        for (who, loc), (need, (cap, expr)) in AMBIENT_NEEDS.items():
            if (who, loc) not in AMBIENT:
                out.append("AMBIENT_NEEDS (%s, %s): no AMBIENT row" % (who, loc))
            if need not in CAST:
                out.append("AMBIENT_NEEDS (%s, %s): %r is not a person" % (who, loc, need))
            if expr not in EXPRESSIONS or not renpy.has_image("%s %s" % (who, expr)):
                out.append("AMBIENT_NEEDS (%s, %s): no image '%s %s'" % (who, loc, who, expr))
        for loc, st in PLACE_STAGING.items():
            if loc not in places:
                out.append("PLACE_STAGING: %r is not a place" % loc)
            if set(st) - {"zoom", "y"}:
                out.append("PLACE_STAGING %s: unknown keys %r" % (loc, sorted(set(st) - {"zoom", "y"})))
        for who, expr in PERSON_GREET_EXPR.items():
            if who not in CAST:
                out.append("PERSON_GREET_EXPR: %r is not a person" % who)
            elif expr not in EXPRESSIONS or not renpy.has_image("%s %s" % (who, expr)):
                out.append("PERSON_GREET_EXPR: no image '%s %s'" % (who, expr))
        for who in ROSTER_ORDER:
            if who not in PERSON_GREET_EXPR:
                out.append("PERSON_GREET_EXPR: no face for %r" % who)
        return out

    register_validator(_validate_wp7_tables)


## Sandbox styles ###############################################################

style sb_action_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (16, 8, 16, 8)
    xsize 392
    yminimum 62

style sb_mission_button is sb_action_button:
    background Frame("gui/panel_gold.png", 4, 4)
    hover_background Frame("gui/panel_gold.png", 4, 4)
    hover_foreground Solid("#ffd16618")

style sb_action_title is text:
    font gui.display_font
    color gui.paper
    size 22

style sb_action_hint is text:
    color gui.dim
    size 16

style sb_link_text is text:
    font gui.body_medium_font
    color gui.dim
    hover_color gui.paper
    size 19

style sb_choice_button is sb_action_button:
    xsize 780
    yminimum 72
    padding (22, 8, 22, 8)

style sb_choice_gold_button is sb_choice_button:
    background Frame("gui/panel_gold.png", 4, 4)
    hover_background Frame("gui/panel_gold.png", 4, 4)
    hover_foreground Solid("#ffd16618")

style sb_plate_name is text:
    font gui.display_font
    size 26
    outlines [(2, "#07060cc0", 0, 0)]

style sb_plate_caption is text:
    italic True
    color gui.dim
    size 18

style sb_arrival_text is text:
    outlines [(0, "#07060cd8", 2, 2)]


## Diamonds: one per period an action takes ###################################

screen sb_cost(n):
    if n:
        hbox:
            spacing 3
            yalign 0.5
            for _k in range(n):
                add "gui/pip_small.png" yalign 0.5


## Place view (4.4) #############################################################

screen sb_place():

    tag sandbox

    ## The objective check also runs as the view appears, so a save loaded
    ## onto this screen gets its NEXT toast straight away (3.10). It does
    ## nothing when the objective hasn't changed.
    on ("show", "replace") action Function(check_objective)

    $ _stage, _extra = stage_people(here)
    $ _xs = STAGE_CENTRES.get(len(_stage), [])
    $ _st = PLACE_STAGING.get(here, {})
    $ _zoom = _st.get("zoom", 0.52)
    $ _yoff = -40 + _st.get("y", 0)
    $ _acts = place_actions(here)
    $ _wait = [a for a in _acts if a[0] == "wait"]
    $ _acts = [a for a in _acts if a[0] != "wait"]
    $ _missions = [] if explore_mode else [mission_view(m) for m in missions_here(here)]
    $ _t0 = arrival_caption()
    $ _pname = LOCATIONS[here]["name"] if here in LOCATIONS else here
    $ _pdesc = LOCATIONS[here]["desc"] if here in LOCATIONS else ""
    $ _per = period

    add graded_bg()
    add Solid(gui.ink) alpha 0.10

    ## --- the stage: the people here, clickable --------------------------------
    for _i, _who in enumerate(_stage):
        $ _cap, _expr = ambient_of(_who, here)
        $ _img = person_image(_who, _expr)
        imagebutton:
            idle Transform(_img, zoom=_zoom)
            hover Transform(_img, zoom=_zoom, matrixcolor=BrightnessMatrix(0.08))
            focus_mask True
            xcenter _xs[_i]
            yalign 1.0
            yoffset _yoff
            action Return(("char", _who))

    ## Nameplates go over every sprite, so a neighbour never covers one.
    for _i, _who in enumerate(_stage):
        $ _c = CAST[_who]
        $ _nm = _c["short"]
        $ _cap = ambient_of(_who, here)[0]
        $ _job = (not explore_mode) and bool(missions_with(_who, here))
        $ _new = has_event("hangout", _who, here)
        button:
            xcenter _xs[_i]
            ypos 944
            background Frame("gui/panel_dark.png", 4, 4)
            hover_background Frame("gui/panel_hover.png", 4, 4)
            padding (18, 6, 18, 8)
            xmaximum 300
            action Return(("char", _who))
            vbox:
                spacing 0
                xalign 0.5
                hbox:
                    spacing 10
                    xalign 0.5
                    text "[_nm]" style "sb_plate_name" color _c["color"] yalign 0.5
                    if _job:
                        text u"「!」" font gui.display_heavy_font color gui.gold size 22 yalign 0.5
                    if _new:
                        frame:
                            background Solid(gui.gold)
                            padding (6, 2)
                            yalign 0.5
                            text _("NEW"):
                                font gui.body_bold_font
                                color gui.ink
                                size 11
                                kerning 2
                if _cap:
                    text "[_cap]" style "sb_plate_caption" xalign 0.5 text_align 0.5

    ## More than four: a chip with the rest.
    if _extra:
        $ _more = "+%d" % len(_extra)
        vbox:
            pos (1300, 900)
            yanchor 1.0
            spacing 4
            frame:
                background Frame("gui/panel_dark.png", 4, 4)
                padding (14, 6)
                text _more font gui.display_font color gui.paper size 22
            for _w in _extra:
                textbutton CAST[_w]["short"]:
                    background Frame("gui/panel_dark.png", 4, 4)
                    hover_background Frame("gui/panel_hover.png", 4, 4)
                    padding (14, 4)
                    text_font gui.display_font
                    text_color CAST[_w]["color"]
                    text_size 20
                    action Return(("char", _w))

    ## Nobody home.
    if not _stage:
        frame:
            xcenter 700
            ycenter 640
            background Frame("gui/panel_ghost.png", 4, 4)
            padding (28, 14)
            text _("Nobody here right now. The map shows who's where."):
                color gui.dim
                size 22

    ## --- the arrival caption (D35) -----------------------------------------------
    if _t0 is not None:
        frame at arrival_fx(_t0):
            pos (40, 100)
            background Frame("gui/panel_ghost.png", 4, 4)
            padding (22, 10, 22, 14)
            vbox:
                spacing 4
                hbox:
                    spacing 14
                    text "[_pname]" style "sb_arrival_text" font gui.display_font color gui.paper size 44
                    text "· [_per]" style "sb_arrival_text" font gui.body_medium_font color gui.dim size 20 kerning gui.track yalign 0.85
                if _pdesc:
                    text "[_pdesc]" style "sb_arrival_text" color gui.dim size 20 xmaximum 700

    ## --- the action card ----------------------------------------------------------
    vbox:
        xpos 1440
        yalign 1.0
        yoffset -40
        xsize 440
        spacing 10

        if stamina < 25 and not explore_mode:
            frame:
                xalign 1.0
                background Frame("gui/panel_ghost.png", 4, 4)
                padding (16, 6)
                text _("I'm running on empty. Eat or sleep."):
                    color gui.seal
                    size 20

        frame:
            background Frame("gui/panel_dark.png", 4, 4)
            padding (24, 20)
            xfill True

            vbox:
                spacing 8

                for _mid, _mtitle, _mhint in _missions:
                    button:
                        style "sb_mission_button"
                        action Return(("mission", _mid))
                        vbox:
                            spacing 2
                            text "[_mtitle]" style "sb_action_title" color gui.gold
                            if _mhint:
                                text "[_mhint]" style "sb_action_hint"

                for _aid, _alabel, _ahint, _acost in _acts:
                    button:
                        style "sb_action_button"
                        action Return(("act", _aid))
                        hbox:
                            xfill True
                            vbox:
                                spacing 2
                                xmaximum 320
                                text "[_alabel]" style "sb_action_title"
                                text "[_ahint]" style "sb_action_hint"
                            if _acost:
                                hbox:
                                    xalign 1.0
                                    yalign 0.5
                                    use sb_cost(_acost)

                if _wait:
                    button:
                        style "empty"
                        padding (4, 6)
                        action Return(("act", "wait"))
                        hbox:
                            spacing 10
                            text _("Wait") style "sb_link_text"
                            use sb_cost(_wait[0][3])

                if companion and not explore_mode:
                    $ _cn = CAST[companion]["short"]
                    textbutton _("[_cn] is with me · let them go"):
                        padding (4, 2)
                        background None
                        text_style "sb_link_text"
                        text_size 17
                        action Return(("act", "release"))

    use sb_hud


## Person view (4.5) ############################################################

transform char_focus(x0):
    xcenter x0 yalign 1.0 yoffset -40 zoom 0.52
    easein 0.35 xcenter 520 yoffset -20 zoom 0.66

screen sb_char(who):

    tag sandbox

    $ _c = CAST[who]
    $ _nm = _c["name"]
    $ _col = _c["color"]
    $ _role = role_line(who)
    $ _b = bonds.get(who, 0)
    $ _brank = bond_rank(_b)[1]
    $ _rom = is_romanceable(who)
    $ _a = affection.get(who, 0)
    $ _arank = aff_rank(_a)[1]
    $ _cap = aff_cap(who)
    $ _thr = person_thread(who)
    $ _amb = ambient_of(who, here)[0]
    $ _choices = person_choices(who, here)
    $ _inv_ok = activity_state(ACT_BY_ID["invite"], who, here)[0]
    $ _inv_label = _("Let them go") if companion == who else _("Ask them along")
    $ _unlock = unlock_line(who)
    $ _x0 = stage_x(who, here)

    add graded_bg()
    add Solid(gui.ink) alpha 0.35

    add person_image(who) at char_focus(_x0)

    ## The card fits its worst case (a mission with a two-line hint, three
    ## more choices, affection at the cap, a thread) with room to spare:
    ## ymaximum keeps it on screen whatever grows.
    frame:
        style "jjk_panel"
        xpos 1000
        ypos 150
        xsize 820
        ymaximum 890
        padding (20, 22)

        vbox:
            spacing 12

            ## --- who they are, and what they're doing --------------------------
            vbox:
                spacing 2
                text "[_nm]" font gui.display_font color _col size 46
                if _role:
                    text "[_role]" style "jjk_label" size 20
                if _amb:
                    text "[_amb]" italic True color gui.dim size 20

            ## --- bond, affection, thread -----------------------------------
            vbox:
                spacing 6
                hbox:
                    spacing 12
                    text _("BOND") style "jjk_label" yalign 0.5
                    text "[_brank]" color gui.paper size 20 yalign 0.5
                    text "([_b]/100)" style "jjk_label" yalign 0.5
                use meter(_b, width=740, height=10, fill=_col)

            if _rom and _a > 0:
                ## The note shows only while the bond is what holds affection
                ## back; at the pre-confession ceiling the rest is up to me.
                $ _capped = _a >= _cap and _cap < AFF_BASE_MAX
                $ _ready = confession_ready(who)
                vbox:
                    spacing 6
                    hbox:
                        spacing 12
                        text _("AFFECTION") style "jjk_label" yalign 0.5
                        text "[_arank]" color gui.romance size 20 yalign 0.5
                        if _capped:
                            text _("([_a]/[_cap] · I'd have to know them better)") style "jjk_label" yalign 0.5
                        elif _ready:
                            text _("([_a]/[_cap] · the rest is up to me)") style "jjk_label" yalign 0.5
                        else:
                            text "([_a]/[_cap])" style "jjk_label" yalign 0.5
                    use meter(_a, max(1, _cap), width=740, height=10, fill=gui.romance)

            if _thr:
                $ _ttitle, _tstage, _ttotal = _thr
                hbox:
                    spacing 12
                    text "[_ttitle]" color gui.gold size 19 yalign 0.5
                    hbox:
                        spacing 4
                        yalign 0.5
                        for _k in range(_ttotal):
                            add ("gui/pip_gold.png" if _k <= _tstage else "gui/pip_off.png") yalign 0.5

            ## --- what I can do with them ------------------------------------
            vbox:
                spacing 8
                for _ch in _choices:
                    $ _gold = _ch.get("gold")
                    $ _romc = _ch.get("romance")
                    $ _ret = (("do", _ch["id"], who) if _ch["kind"] == "do" else (_ch["kind"], _ch["id"]))
                    $ _lbl = (u"♡ " + _ch["label"]) if _romc else _ch["label"]
                    $ _hint = _ch.get("hint") or ""
                    button:
                        style ("sb_choice_gold_button" if _gold else "sb_choice_button")
                        action Return(_ret)
                        hbox:
                            xfill True
                            vbox:
                                spacing 2
                                xmaximum 660
                                yalign 0.5
                                text "[_lbl]":
                                    font gui.display_font
                                    size 26
                                    color (gui.gold if _gold else (gui.romance if _romc else gui.paper))
                                if _hint:
                                    text "[_hint]" color gui.dim size 18
                            if _ch.get("cost"):
                                hbox:
                                    xalign 1.0
                                    yalign 0.5
                                    use sb_cost(_ch["cost"])

            ## --- footer: the Closer hint, then invite and Back on one line ----
            if _unlock:
                text "[_unlock]" color gui.gold size 18
            hbox:
                xfill True
                if _inv_ok or companion == who:
                    textbutton _inv_label:
                        padding (2, 2)
                        background None
                        text_style "sb_link_text"
                        yalign 0.5
                        action Return(("do", "invite", who))
                textbutton _("Back"):
                    id "sb_char_back"
                    xalign 1.0
                    yalign 0.5
                    padding (2, 2)
                    background None
                    text_style "sb_link_text"
                    text_size 22
                    action Return(("cancel",))

    key "game_menu" action Return(("cancel",))

    use sb_hud(person=True)
