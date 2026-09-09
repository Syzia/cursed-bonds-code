################################################################################
## Cursed Bonds — sandbox interface: HUD, campus map, location view, status.
##
## Screens return tuples to sb_loop.rpy:
##   ("map",) ("char", who) ("act", id) ("go", loc) ("cancel",)
##   ("talk", who) ("hang", who) ("spar", who)
## Nothing here mutates game state.
################################################################################

init python:

    def place_actions(loc):
        """(id, label, hint, period_cost) for everything you can do here."""
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
        if store.technique == "aftersound":
            a.append(("replay", "Replay", "Hear the last hour of this place.", 0))
        if store.technique == "emberfall" and loc == "storehouse":
            a.append(("temper", "Temper a tool", "Work the forge.", 1))
        a.append(("wait", "Wait", "Let the period pass.", 1))
        return a

    def hud_date():
        """'DAY 6 · SAT' — the period is drawn as pips next to it."""
        return "DAY %d · %s" % (store.day, weekday().upper())


## Sandbox-only styles #########################################################

style sb_place_text is text:
    font gui.display_font
    color gui.paper
    size 30

style sb_hud_button is button:
    padding (6, 4)

style sb_hud_button_text is text:
    font gui.body_medium_font
    color gui.dim
    hover_color gui.paper
    selected_color gui.violet2
    size 17
    kerning gui.track

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

style sb_node_button is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (18, 9, 18, 9)

style sb_node_here is sb_node_button:
    background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_active.png", 4, 4)

style sb_node_name is text:
    font gui.display_font
    color gui.paper
    size 21
    text_align 0.5
    layout "subtitle"


## The period tracker: five diamonds, one per period. ##########################

screen period_pips():
    $ _pi = period_index()
    hbox:
        spacing 5
        yalign 0.5
        for _i, _p in enumerate(PERIODS):
            if _i < _pi:
                add "gui/pip_past.png" yalign 0.5
            elif _i == _pi:
                add "gui/pip_on.png" yalign 0.5
            else:
                add "gui/pip_off.png" yalign 0.5


## HUD ##########################################################################
##
## A 92px rail across the top. Left to right: where and when, the two things
## you spend, what you are, and the deadline. Navigation lives at the far right.

screen sb_hud(on_map=False):

    $ _tiername = tech_tier()[1]
    $ _tname = tech()["name"]
    $ _loc = _("Campus") if on_map else LOCATIONS[here]["name"]
    $ _date = hud_date()
    $ _per = store.period.upper()
    $ _left = days_left()

    frame:
        background Frame("gui/panel_dark.png", 4, 4)
        yalign 0.0
        xfill True
        ysize 92
        xpadding 40
        ypadding 0

        fixed:
            xfill True
            ysize 92

            hbox:
                spacing 26
                yalign 0.5
                xalign 0.0

                ## Where / when ---------------------------------------------------
                vbox:
                    spacing 4
                    yalign 0.5
                    text "[_loc]" style "sb_place_text"
                    hbox:
                        spacing 12
                        text "[_date]" style "jjk_label"
                        use period_pips
                        text "[_per]" style "jjk_label"
                        text "·" style "jjk_label"
                        text "[_left]":
                            color gui.gold
                            size 15
                            yalign 0.5
                        text _("TO KYOTO") style "jjk_label"

                ## Cursed energy -------------------------------------------------
                vbox:
                    spacing 7
                    yalign 0.5
                    hbox:
                        spacing 10
                        text _("CURSED ENERGY") style "jjk_label" yalign 1.0
                        text "[ce] / [ce_max]" style "jjk_value" size 17 yalign 1.0
                    use meter(ce, ce_max, width=200, height=6, fill=gui.violet)

                ## Stamina --------------------------------------------------------
                vbox:
                    spacing 7
                    yalign 0.5
                    hbox:
                        spacing 10
                        text _("STAMINA") style "jjk_label" yalign 1.0
                        text "[stamina]" style "jjk_value" size 17 yalign 1.0
                    use meter(stamina, stamina_max, width=150, height=6, fill=gui.stamina)

                ## Technique ------------------------------------------------------
                vbox:
                    spacing 3
                    yalign 0.5
                    text "[_tname]":
                        font gui.display_font
                        color "#8ed6ff"
                        size 22
                    text "[_tiername!u]" style "jjk_label" size 15

                hbox:
                    spacing 16
                    yalign 0.5
                    hbox:
                        spacing 6
                        text _("CTRL") style "jjk_label"
                        text "[control]" style "jjk_value" size 17
                    hbox:
                        spacing 6
                        text _("OUT") style "jjk_label"
                        text "[output]" style "jjk_value" size 17
                    hbox:
                        spacing 6
                        text _("INS") style "jjk_label"
                        text "[insight]" style "jjk_value" size 17

            ## Deadline + navigation, pushed to the right -------------------
            hbox:
                xalign 1.0
                yalign 0.5
                spacing 34

                hbox:
                    spacing 8
                    yalign 0.5
                    style_prefix "sb_hud"
                    if not on_map:
                        textbutton _("MAP") action Return(("map",))
                    textbutton _("JOURNAL") action ShowMenu("jjk_journal")
                    textbutton _("STATUS") action ShowMenu("jjk_status")
                    textbutton _("SAVE") action ShowMenu("save")
                    textbutton _("MENU") action ShowMenu("preferences")


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
            text _("There's nobody here right now."):
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


## Campus map ###################################################################

screen sb_map():

    tag sandbox

    $ _sense = (technique == "filament" and control >= 20)

    add "bg map_campus"
    add Solid(gui.ink) alpha 0.32

    ## Title.
    vbox:
        xalign 0.5
        ypos 118
        spacing 8
        hbox:
            xalign 0.5
            spacing 16
            use seal("図", 44)
            text _("TOKYO JUJUTSU HIGH"):
                font gui.display_font
                color gui.paper
                size 30
                kerning 8
                yalign 0.5
        if _sense:
            text _("Filament — you can feel where everyone is."):
                xalign 0.5
                color gui.dim
                size 19
        else:
            text _("Pick somewhere to go. Most trips are free; being there costs the period."):
                xalign 0.5
                color gui.dim
                size 19

    for _key in LOC_ORDER:

        $ _L = LOCATIONS[_key]
        $ _ok, _why = can_enter(_key)
        $ _cur = (_key == here)
        $ _folk = who_is_here(_key) if _sense else []
        $ _nm = _L["name"]
        $ _people = ", ".join(CAST[c]["short"] for c in _folk)

        vbox:
            xpos _L["x"]
            ypos _L["y"]
            xanchor 0.5
            yanchor 0.5
            spacing 4

            button:
                style ("sb_node_here" if _cur else "sb_node_button")
                xalign 0.5
                action Return(("go", _key))
                sensitive (_ok and not _cur)

                vbox:
                    spacing 2
                    text "[_nm]":
                        style "sb_node_name"
                        color (gui.paper if _ok else gui.mute)
                    if _cur:
                        text _("YOU ARE HERE"):
                            style "jjk_label"
                            size 12
                            color gui.violet2
                            xalign 0.5
                    elif _people:
                        text "[_people]":
                            color gui.gold
                            size 15
                            xalign 0.5
                    elif not _ok:
                        text _("LOCKED"):
                            style "jjk_label"
                            size 12
                            color gui.seal
                            xalign 0.5

            add ("gui/pin_here.png" if _cur else "gui/pin.png") xalign 0.5

    ## Legend, bottom right.
    frame:
        background Frame("gui/panel_dark.png", 4, 4)
        xalign 1.0
        yalign 1.0
        xoffset -40
        yoffset -110
        padding (20, 14)
        vbox:
            spacing 8
            hbox:
                spacing 10
                add "gui/pin_here.png" yalign 0.5
                text _("You are here") style "jjk_small" size 16
            hbox:
                spacing 10
                add "gui/pip_gold.png" yalign 0.5
                text _("Someone's there") style "jjk_small" size 16
            hbox:
                spacing 10
                add "gui/pip_seal.png" yalign 0.5
                text _("Locked this period") style "jjk_small" size 16

    ## Stay / status, bottom left — clear of the gate node at the bottom centre.
    frame:
        background Frame("gui/panel_dark.png", 4, 4)
        xalign 0.0
        yalign 1.0
        xoffset 40
        yoffset -40
        padding (18, 14, 18, 14)
        hbox:
            spacing 14
            textbutton _("Stay here"):
                style "jjk_button"
                text_style "jjk_button_text"
                xfill False
                action Return(("cancel",))
            textbutton _("Status"):
                style "jjk_button"
                text_style "jjk_button_text"
                xfill False
                action ShowMenu("jjk_status")

    use sb_hud(on_map=True)


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
    $ _has = has_event("hangout", who, here)
    $ _spent = (who in spent_today)
    $ _can_spar = (who in ("maki", "yuji", "panda") and here in ("dojo", "training", "ridge"))

    add graded_bg()
    add Solid(gui.ink) alpha 0.62

    add who:
        xalign 0.16
        yalign 1.0
        zoom 0.66

    frame:
        style "jjk_panel_solid"
        xalign 0.88
        yalign 0.5
        xsize 780
        padding (40, 36)

        vbox:
            spacing 16

            hbox:
                spacing 16
                use seal("縁", 44)
                text "[_nm]":
                    font gui.display_font
                    color _col
                    size 38
                    yalign 0.5
            text "[_year!u]" style "jjk_label"
            text "[_blurb]" style "jjk_small" xsize 700

            use rule()

            ## Bond.
            vbox:
                spacing 8
                hbox:
                    spacing 12
                    text _("BOND") style "jjk_label" yalign 1.0
                    text "[_brank]" style "jjk_value" size 20 yalign 1.0
                    text "[_b] / 100" style "jjk_small" size 17 yalign 1.0
                use meter(_b, width=700, height=8, fill=_col)

            ## Affection, capped by bond. The marker shows the ceiling.
            if _rom:
                vbox:
                    spacing 8
                    hbox:
                        spacing 12
                        text _("AFFECTION") style "jjk_label" yalign 1.0
                        text "[_arank]" style "jjk_value" size 20 yalign 1.0
                        text "[_a] / [_cap]" style "jjk_small" size 17 yalign 1.0
                    use meter(_a, 100, width=700, height=8, fill=gui.romance, marker=_cap)
                    if _a >= _cap:
                        text _("You'd have to know them better before this goes further."):
                            color gui.dim
                            size 17

            null height 4

            ## Actions.
            vbox:
                spacing 8
                style_prefix "jjk"

                textbutton _("Talk") action Return(("talk", who))

                if _has and not _spent:
                    textbutton _("Spend time together") action Return(("hang", who))
                elif _spent:
                    textbutton _("Spend time together — already today") action NullAction() sensitive False
                else:
                    textbutton _("Nothing new to do together today") action NullAction() sensitive False

                if _can_spar:
                    textbutton _("Train together") action Return(("spar", who))

            null height 4

            textbutton _("Back"):
                style "sb_hud_button"
                text_style "sb_hud_button_text"
                xalign 1.0
                text_size 17
                action Return(("cancel",))

    use sb_hud(on_map=True)


## Status #######################################################################

screen jjk_status():

    tag menu

    $ _t = tech()
    $ _ti, _tname, _tdesc = tech_tier()
    $ _nx = next_tier()
    $ _tline = _t["name"]
    $ _tjp = _t["jp"]
    $ _grade = grade_name()
    $ _tblurb = _t["blurb"]
    $ _tverb = _t["verb"]
    $ _tverbd = _t["verb_desc"]
    $ _ttag = _t["tag"]
    $ _nxname = _nx[0] if _nx else ""
    $ _nxreq = _nx[1] if _nx else 0

    use game_menu(_("Status"), scroll="viewport"):

        vbox:
            spacing 26

            ## Who you are.
            frame:
                style "jjk_panel"
                xfill True
                vbox:
                    spacing 10
                    text "[mc_surname] [mc_name]":
                        font gui.display_font
                        color gui.paper
                        size 40
                    text "FIRST-YEAR · [_grade!u] · DAY [day]" style "jjk_label"

            ## Technique.
            frame:
                style "jjk_panel"
                xfill True
                vbox:
                    spacing 12

                    use section(_("Technique"), k="術")

                    hbox:
                        spacing 16
                        text "[_tline]":
                            font gui.display_font
                            color "#8ed6ff"
                            size 30
                        text "[_tjp]" style "jjk_small" yalign 1.0
                    text "[_tblurb]" style "jjk_small" xsize 1100 size 21

                    null height 4

                    hbox:
                        spacing 60
                        vbox:
                            spacing 4
                            text _("CURRENT TIER") style "jjk_label"
                            text "[_tname]" style "jjk_value"
                            text "[_tdesc]" style "jjk_small" size 18 xsize 480
                        if _nx:
                            vbox:
                                spacing 4
                                text _("NEXT") style "jjk_label"
                                text "[_nxname]" style "jjk_value"
                                text "at [_ttag] [_nxreq]" style "jjk_small" size 18

                    null height 4

                    hbox:
                        spacing 12
                        text "[_tverb!u]" style "jjk_label" color gui.violet2 yalign 1.0
                        text "[_tverbd]" style "jjk_small" size 19 xsize 900 yalign 1.0

                    null height 8

                    hbox:
                        spacing 40
                        vbox:
                            spacing 8
                            hbox:
                                spacing 10
                                text _("CONTROL") style "jjk_label"
                                text "[control]" style "jjk_value" size 18
                            use meter(control, width=300, height=8, fill=gui.violet)
                        vbox:
                            spacing 8
                            hbox:
                                spacing 10
                                text _("OUTPUT") style "jjk_label"
                                text "[output]" style "jjk_value" size 18
                            use meter(output, width=300, height=8, fill="#ff8f6a")
                        vbox:
                            spacing 8
                            hbox:
                                spacing 10
                                text _("INSIGHT") style "jjk_label"
                                text "[insight]" style "jjk_value" size 18
                            use meter(insight, width=300, height=8, fill="#8ed6ff")

            ## Bonds.
            frame:
                style "jjk_panel"
                xfill True
                vbox:
                    spacing 18

                    use section(_("Bonds"), k="縁")

                    for _key in ROSTER_ORDER:
                        if _key in roster:
                            $ _info = CAST[_key]
                            $ _nm2 = _info["name"]
                            $ _col2 = _info["color"]
                            $ _v = bonds.get(_key, 0)
                            $ _r = bond_rank(_v)[1]
                            $ _av = affection.get(_key, 0)
                            $ _ar = aff_rank(_av)[1]
                            $ _cap2 = aff_cap(_key)

                            hbox:
                                spacing 24
                                fixed:
                                    xysize (260, 30)
                                    text "[_nm2]":
                                        font gui.display_font
                                        color _col2
                                        size 24
                                        yalign 0.5
                                vbox:
                                    spacing 6
                                    yalign 0.5
                                    hbox:
                                        spacing 12
                                        use meter(_v, width=520, height=8, fill=_col2)
                                        text "[_r]" style "jjk_small" size 17 yalign 0.5
                                    if is_romanceable(_key):
                                        hbox:
                                            spacing 12
                                            use meter(_av, width=520, height=5, fill=gui.romance, marker=_cap2)
                                            text "♡ [_ar]":
                                                color gui.romance
                                                size 15
                                                yalign 0.5


default spent_today = set()


## Journal ######################################################################

screen jjk_journal():

    tag menu

    $ _open = threads_open()
    $ _left2 = days_left()

    use game_menu(_("Journal"), scroll="viewport"):

        vbox:
            spacing 22

            frame:
                style "jjk_panel"
                xfill True
                hbox:
                    spacing 24
                    vbox:
                        spacing 8
                        text _("Arc One — Tokyo Jujutsu High"):
                            font gui.display_font
                            color gui.paper
                            size 32
                        text "DAY [day] · [_left2] DAYS UNTIL THE KYOTO EXCHANGE" style "jjk_label"

            if not _open:
                frame:
                    style "jjk_panel"
                    xfill True
                    text _("Nothing open yet. Go and talk to people.") style "jjk_small"

            for _tid in THREAD_ORDER:

                $ _st = thread_stage(_tid)

                if _st >= 0:

                    $ _T = THREADS[_tid]
                    $ _who = _T["who"]
                    $ _title = _T["title"]
                    $ _col = CAST[_who]["color"]
                    $ _owner = CAST[_who]["name"]
                    $ _total = len(_T["stages"])
                    $ _shown = _T["stages"][:_st + 1]
                    $ _fin = thread_done(_tid)
                    $ _stn = _st + 1

                    frame:
                        style "jjk_panel"
                        xfill True

                        vbox:
                            spacing 12

                            hbox:
                                spacing 16
                                text "[_title]":
                                    font gui.display_font
                                    color _col
                                    size 28
                                text "[_owner!u]" style "jjk_label" yalign 1.0
                                if _fin:
                                    frame:
                                        background Solid(gui.stamina)
                                        padding (6, 2)
                                        yalign 1.0
                                        text _("RESOLVED"):
                                            font gui.body_bold_font
                                            color gui.ink
                                            size 11
                                            kerning 2

                            hbox:
                                spacing 12
                                use meter(_st + 1, _total, width=420, height=6, fill=_col)
                                text "[_stn] / [_total]" style "jjk_small" size 15 yalign 0.5

                            null height 2

                            for _line in _shown:
                                hbox:
                                    spacing 12
                                    add "gui/pip_small.png" ypos 8
                                    text "[_line]":
                                        color gui.paper
                                        size 20
                                        xsize 1000
