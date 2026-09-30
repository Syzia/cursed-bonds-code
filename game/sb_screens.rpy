################################################################################
## Cursed Bonds — sandbox interface: the place view and the person view.
##
## Screens return tuples to sb_loop.rpy:
##   ("map",) ("char", who) ("act", id) ("go", loc) ("cancel",)
##   ("talk", who) ("hang", who) ("spar", who)
## Nothing here mutates game state.
##
## The HUD is in ui_hud.rpy, the map in ui_map.rpy, and the Status and
## Journal screens in ui_journal.rpy. WP7 owns this file (4.4, 4.5).
################################################################################

init python:

    def place_actions(loc):
        """WP7. (id, label, hint, period_cost) for everything you can do here.
        (WP0: the old list, then registered_place_actions(loc), then Wait.)"""
        if store.explore_mode:
            nxt = PERIODS[(PERIODS.index(store.period) + 1) % len(PERIODS)]
            return ([("explore_time", "Time: %s" % nxt, "Step to the next time of day. Nothing is spent.", 0)]
                    + registered_place_actions(loc))
        a = []
        if loc == "dorm":
            a.append(("sleep", "Sleep", "End the day. Restore everything.", 0))
            a.append(("study", "Study", "Insight. Quiet. Nobody bothers you.", 1))
        if loc in ("training", "ridge", "forest", "dojo"):
            a.append(("train", "Train", "Push your cursed energy. Costs stamina.", 1))
        if loc == "riverside":
            a.append(("swim", "Swim", "Cold. Clears your head.", 1))
            a.append(("train", "Train", "Rough ground. Good footwork.", 1))
        if loc == "cafeteria":
            a.append(("eat", "Eat", "Stamina. Everyone's here at noon.", 0))
        if loc == "infirmary":
            a.append(("rest", "Get patched up", "Shoko will look you over.", 0))
        if loc == "office":
            a.append(("missions", "Mission board", "See what Yaga has.", 0))
        if loc == "storehouse":
            a.append(("tools", "Cursed tools", "Look through the racks.", 0))
        if loc == "courtyard":
            a.append(("train", "Practice", "Forms, in the open, where people can see.", 1))
        if loc == "classroom":
            a.append(("study", "Study", "Insight. The textbook is four hundred pages.", 1))
        if loc == "rooftop":
            a.append(("think", "Sit a while", "Nothing happens. That's the point.", 1))
        if store.technique == "timestop":
            a.append(("hold", "Hold the hour", "Spend deep reserve; the period does not pass.", 0))
        a.extend(registered_place_actions(loc))
        a.append(("wait", "Wait", "Let the period pass.", 1))
        return a

    def ambient_of(who, loc):
        """WP7. (caption, expression) for someone at a place, e.g.
        ("halfway through an enormous bowl", "happy"). (WP0 stub.)"""
        return ("", "neutral")


## Sandbox-only styles #########################################################

style sb_action_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (22, 14, 22, 14)
    xsize 250

style sb_action_travel is sb_action_button:
    background Frame("gui/panel_active.png", 4, 4)
    hover_background Frame("gui/panel_active.png", 4, 4)

style sb_action_title is text:
    font gui.display_font
    color gui.paper
    size 24

style sb_action_hint is text:
    color gui.dim
    size 16


## Location view ################################################################

screen sb_place():

    tag sandbox

    $ _here = LOCATIONS[here]
    $ _folk = who_is_here()
    $ _acts = place_actions(here)
    $ _desc = _here["desc"]

    add graded_bg()
    add Solid(gui.ink) alpha 0.14

    ## Flavour line for the place, just under the rail.
    ## Sits over sky or stone depending on the location, so it carries its own
    ## backing rather than relying on the scene behind it.
    frame:
        xalign 0.5
        ypos 112
        background Frame("gui/panel_ghost.png", 4, 4)
        padding (26, 8)
        text "[_desc]":
            font gui.display_font
            color gui.paper
            size 24
            text_align 0.5
            layout "subtitle"
            xmaximum 1050

    ## Everyone standing around, clickable.
    hbox:
        yalign 1.0
        xalign 0.5
        yoffset -170
        spacing 80

        for _i, _who in enumerate(_folk[:4]):

            $ _c = CAST[_who]
            $ _nm = _c["short"]
            $ _col = _c["color"]
            $ _new = has_event("hangout", _who, here)

            button:
                style "empty"
                action Return(("char", _who))
                xysize (300, 620)

                fixed:
                    add _who:
                        xalign 0.5
                        yalign 1.0
                        yoffset -48
                        zoom 0.46

                    frame:
                        xalign 0.5
                        yalign 1.0
                        background Frame("gui/panel_gold.png" if _new else "gui/panel_dark.png", 4, 4)
                        padding (20, 8)
                        hbox:
                            spacing 12
                            text "[_nm]":
                                font gui.display_font
                                color _col
                                size 24
                                yalign 0.5
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

    ## Nobody home.
    if not _folk:
        frame:
            xalign 0.5
            yalign 1.0
            yoffset -300
            background Frame("gui/panel_ghost.png", 4, 4)
            padding (28, 14)
            text _("Nobody here right now. Check the map — it shows where people are."):
                color gui.dim
                size 22

    ## Action bar.
    frame:
        background Frame("gui/panel_dark.png", 4, 4)
        yalign 1.0
        xfill True
        padding (40, 22, 40, 22)

        hbox:
            xalign 0.0
            spacing 14

            button:
                style "sb_action_travel"
                action Return(("map",))
                vbox:
                    spacing 4
                    text _("Travel") style "sb_action_title"
                    text _("Go somewhere else on campus.") style "sb_action_hint"

            for _a in _acts:
                $ _aid, _alabel, _ahint, _acost = _a
                button:
                    style "sb_action_button"
                    action Return(("act", _aid))
                    fixed:
                        fit_first True
                        vbox:
                            spacing 4
                            text "[_alabel]" style "sb_action_title"
                            text "[_ahint]" style "sb_action_hint"
                        ## One diamond per period this costs.
                        if _acost:
                            hbox:
                                xalign 1.0
                                ypos 6
                                spacing 3
                                for _k in range(_acost):
                                    add "gui/pip_small.png"

    use sb_hud


## Interacting with one person ##################################################

screen sb_char(who):

    tag sandbox

    $ _c = CAST[who]
    $ _nm = _c["name"]
    $ _col = _c["color"]
    $ _b = bonds.get(who, 0)
    $ _brank = bond_rank(_b)[1]
    $ _rom = is_romanceable(who)
    $ _a = affection.get(who, 0)
    $ _arank = aff_rank(_a)[1]
    $ _cap = aff_cap(who)
    $ _blurb = _c["blurb"]
    $ _year = _c["year"]
    $ _acts = activities_for(who)
    $ _next = next_unlock(who)
    $ _nextline = ("Next: %s at %s" % (_next[1], _next[2])) if _next else ""
    $ _tid = next((t for t in THREAD_ORDER if THREADS[t]["who"] == who), None)
    $ _tstage = thread_stage(_tid) if _tid else -1
    $ _ttitle = THREADS[_tid]["title"] if _tid else ""
    $ _ttotal = len(THREADS[_tid]["stages"]) if _tid else 1

    add graded_bg()
    add Solid(gui.ink) alpha 0.62

    add who:
        xalign 0.12
        yalign 1.0
        zoom 0.66

    frame:
        style "jjk_panel"
        xalign 0.90
        ypos 96
        xsize 820
        ymaximum 950

        vbox:
            spacing 10

            text "[_nm]":
                color _col
                size 38
            text "[_year] — [_blurb]":
                color gui.dim
                size 20
                xsize 760

            null height 4

            ## --- relationship meters ---------------------------------------
            hbox:
                spacing 12
                text _("BOND") style "jjk_label" yalign 0.5
                text "[_brank]":
                    color gui.paper
                    size 20
                    yalign 0.5
                text "([_b]/100)" style "jjk_label" yalign 0.5
            use meter(_b, width=740, height=10, fill=_col)

            if _rom:
                hbox:
                    spacing 12
                    text _("AFFECTION") style "jjk_label" yalign 0.5
                    text "[_arank]":
                        color gui.romance
                        size 20
                        yalign 0.5
                    text "([_a]/[_cap])" style "jjk_label" yalign 0.5
                use meter(_a, _cap, width=740, height=10, fill=gui.romance)
                if _a >= _cap and _cap < AFF_TRUE_MAX:
                    text _("You'd have to know them better before this goes further.") style "jjk_label"

            if _tid and _tstage >= 0:
                null height 2
                hbox:
                    spacing 10
                    text "[_ttitle]":
                        color gui.gold
                        size 18
                        yalign 0.5
                    use meter(_tstage + 1, _ttotal, width=180, height=6, fill=gui.gold)

            null height 10

            ## --- what you can do -------------------------------------------
            viewport:
                ymaximum 470
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    spacing 4
                    xsize 740

                    for _a, _ok, _why in _acts:

                        $ _alabel = _a["label"]
                        $ _ahint = _a["hint"]
                        $ _acost = _a["cost"]
                        $ _arom = (_a["kind"] == "romance")
                        $ _acol = (gui.romance if _arom else gui.paper) if _ok else gui.mute

                        button:
                            xfill True
                            padding (14, 7)
                            background None
                            hover_background Frame(Solid(gui.panel2), 4, 4)
                            action Return(("do", _a["id"], who))
                            sensitive _ok

                            hbox:
                                spacing 12
                                xfill True

                                vbox:
                                    spacing 1
                                    text "[_alabel]":
                                        color _acol
                                        size 23
                                    if _ok:
                                        text "[_ahint]" style "jjk_label"

                                null width 20

                                if _ok and _acost:
                                    text "[_acost]p" style "jjk_label" yalign 0.5 xalign 1.0
                                elif not _ok:
                                    text "[_why]":
                                        color gui.mute
                                        size 18
                                        yalign 0.5
                                        xalign 1.0

            if _nextline:
                null height 6
                text "[_nextline]":
                    color gui.gold
                    size 18

            null height 8
            textbutton _("Back") action Return(("cancel",)) text_size 23

    use sb_hud(on_map=True)
