################################################################################
## Cursed Bonds — sandbox interface: HUD, campus map, location view, status.
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


## HUD ##########################################################################

screen sb_hud(on_map=False):

    $ _tiername = tech_tier()[1]
    $ _loc = LOCATIONS[here]["name"]
    $ _datestr = date_line()
    $ _left = days_left()

    frame:
        background Frame(Solid("#0b0913ee"), 6, 6)
        yalign 0.0
        xfill True
        ypadding 10
        xpadding 26

        fixed:
            xfill True
            ysize 56

            hbox:
                spacing 34
                xalign 0.0
                yalign 0.5

                vbox:
                    spacing 1
                    text "[_loc]":
                        color "#ffffff"
                        size 26
                    text "[_datestr]":
                        color "#9d95ae"
                        size 18
                    text "[_left] days to Kyoto":
                        color "#8b7fa8"
                        size 16

                vbox:
                    spacing 3
                    yalign 0.5
                    text "Cursed energy  [ce]/[ce_max]":
                        color "#cfc8dd"
                        size 17
                    use meter(ce, ce_max, width=180, height=9, fill="#a259ff")

                vbox:
                    spacing 3
                    yalign 0.5
                    text "Stamina  [stamina]":
                        color "#cfc8dd"
                        size 17
                    use meter(stamina, stamina_max, width=140, height=9, fill="#77e0a0")

                vbox:
                    spacing 1
                    yalign 0.5
                    text "[_tiername]":
                        color "#8ed6ff"
                        size 19
                    text "C [control] · O [output] · I [insight]":
                        color "#9d95ae"
                        size 17

            hbox:
                xalign 1.0
                yalign 0.5
                spacing 14
                if not on_map:
                    textbutton "Map" action Return(("map",)) text_size 22
                textbutton "Journal" action ShowMenu("jjk_journal") text_size 22
                textbutton "Status" action ShowMenu("jjk_status") text_size 22
                textbutton "Save" action ShowMenu("save") text_size 22
                textbutton "Menu" action ShowMenu("preferences") text_size 22


## Location view ################################################################

screen sb_place():

    tag sandbox

    $ _here = LOCATIONS[here]
    $ _folk = who_is_here()
    $ _acts = place_actions(here)
    $ _desc = _here["desc"]

    add graded_bg()
    add Solid("#000000") alpha 0.12

    ## Everyone standing around, clickable.
    hbox:
        yalign 1.0
        xalign 0.5
        yoffset -150
        spacing 30

        for _i, _who in enumerate(_folk[:4]):

            $ _c = CAST[_who]
            $ _nm = _c["short"]
            $ _col = _c["color"]
            $ _mark = "!" if has_event("hangout", _who, here) else ""

            button:
                style "empty"
                action Return(("char", _who))
                xysize (330, 640)

                fixed:
                    add _who:
                        xalign 0.5
                        yalign 1.0
                        zoom 0.50

                    frame:
                        xalign 0.5
                        yalign 1.0
                        background Frame(Solid("#0b0913cc"), 6, 6)
                        padding (16, 6)
                        hbox:
                            spacing 8
                            text "[_nm]":
                                color _col
                                size 24
                            if _mark:
                                text "!":
                                    color "#ffd166"
                                    size 24

    ## Nobody home.
    if not _folk:
        frame:
            xalign 0.5
            ypos 300
            background Frame(Solid("#0b0913bb"), 6, 6)
            padding (30, 18)
            text _("There's nobody here right now."):
                color "#9d95ae"
                size 24

    ## Flavour line for the place.
    frame:
        xalign 0.5
        ypos 108
        background Frame(Solid("#0b0913aa"), 6, 6)
        padding (26, 12)
        text "[_desc]":
            color "#cfc8dd"
            size 21
            xsize 900
            text_align 0.5

    ## Action bar.
    frame:
        background Frame(Solid("#0b0913e6"), 6, 6)
        yalign 1.0
        xfill True
        ypadding 14
        xpadding 26

        hbox:
            xalign 0.5
            spacing 14

            button:
                background Frame(Solid("#3a2168ee"), 6, 6)
                hover_background Frame(Solid("#5b32a8ee"), 6, 6)
                padding (20, 10)
                action Return(("map",))
                vbox:
                    spacing 2
                    text _("Travel"):
                        color "#ffffff"
                        size 23
                    text _("Go somewhere else on campus."):
                        color "#b6a8d8"
                        size 17

            for _a in _acts:
                $ _aid, _alabel, _ahint, _acost = _a
                button:
                    background Frame(Solid("#1b1528dd"), 6, 6)
                    hover_background Frame(Solid("#33234fee"), 6, 6)
                    padding (20, 10)
                    action Return(("act", _aid))
                    vbox:
                        spacing 2
                        text "[_alabel]":
                            color "#e8e2f2"
                            size 23
                        text "[_ahint]":
                            color "#8b8399"
                            size 17

    use sb_hud


## Campus map ###################################################################

screen sb_map():

    tag sandbox

    $ _sense = (technique == "filament" and control >= 20)

    add "bg map_campus"
    add Solid("#05040a") alpha 0.25

    text _("CAMPUS"):
        xalign 0.5
        ypos 96
        color "#a259ff"
        size 34

    if _sense:
        text _("Filament — you can feel where everyone is."):
            xalign 0.5
            ypos 152
            color "#8b8399"
            size 19

    for _key in LOC_ORDER:

        $ _L = LOCATIONS[_key]
        $ _ok, _why = can_enter(_key)
        $ _cur = (_key == here)
        $ _folk = who_is_here(_key) if _sense else []
        $ _nm = _L["name"]
        $ _people = ", ".join(CAST[c]["short"] for c in _folk)

        button:
            xpos _L["x"]
            ypos _L["y"]
            xanchor 0.5
            yanchor 0.5
            padding (14, 7)
            background Frame(Solid("#0b0913d8" if not _cur else "#4a2b8ce8"), 6, 6)
            hover_background Frame(Solid("#6a3fc0ee"), 6, 6)
            action Return(("go", _key))
            sensitive (_ok and not _cur)

            vbox:
                spacing 1
                text "[_nm]":
                    color ("#ffffff" if _ok else "#6a6478")
                    size 21
                    xalign 0.5
                if _people:
                    text "[_people]":
                        color "#ffd166"
                        size 16
                        xalign 0.5
                elif not _ok:
                    text _("locked"):
                        color "#6a6478"
                        size 15
                        xalign 0.5

    frame:
        background Frame(Solid("#0b0913e6"), 6, 6)
        yalign 1.0
        xfill True
        ypadding 14
        hbox:
            xalign 0.5
            spacing 20
            textbutton _("Stay here") action Return(("cancel",)) text_size 24
            textbutton _("Status") action ShowMenu("jjk_status") text_size 24

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

    add graded_bg()
    add Solid("#05040a") alpha 0.55

    add who:
        xalign 0.14
        yalign 1.0
        zoom 0.66

    frame:
        style "jjk_panel"
        xalign 0.86
        yalign 0.5
        xsize 760

        vbox:
            spacing 14

            text "[_nm]":
                color _col
                size 38
            text "[_year] — [_blurb]":
                color "#9d95ae"
                size 20
                xsize 700

            null height 8

            text "Bond — [_brank]  ([_b]/100)":
                color "#cfc8dd"
                size 21
            use meter(_b, width=680, height=12, fill=_col)

            if _rom:
                text "Affection — [_arank]  ([_a]/[_cap])":
                    color "#cfc8dd"
                    size 21
                use meter(_a, 100, width=680, height=12, fill="#ff8fb0")
                if _a >= _cap:
                    text _("You'd have to know them better before this goes further."):
                        color "#8b8399"
                        size 18

            null height 14

            textbutton _("Talk") action Return(("talk", who)) text_size 25

            if _has and not _spent:
                textbutton _("Spend time together  (1 period)") action Return(("hang", who)) text_size 25
            elif _spent:
                textbutton _("Spend time together") action NullAction() sensitive False text_size 25
            else:
                textbutton _("Nothing new to do together today") action NullAction() sensitive False text_size 25

            if who in ("maki", "yuji", "panda") and here in ("dojo", "training", "ridge"):
                textbutton _("Train together  (1 period)") action Return(("spar", who)) text_size 25

            null height 10
            textbutton _("Back") action Return(("cancel",)) text_size 24

    use sb_hud(on_map=True)


## Status #######################################################################

screen jjk_status():

    tag menu

    $ _t = tech()
    $ _ti, _tname, _tdesc = tech_tier()
    $ _nx = next_tier()
    $ _tline = "%s  (%s)" % (_t["name"], _t["jp"])
    $ _grade = grade_name()
    $ _tblurb = _t["blurb"]
    $ _tverb = _t["verb"]
    $ _tverbd = _t["verb_desc"]
    $ _ttag = _t["tag"]
    $ _nxname = _nx[0] if _nx else ""
    $ _nxreq = _nx[1] if _nx else 0

    use game_menu(_("Status"), scroll="viewport"):

        vbox:
            spacing 24

            frame:
                style "jjk_panel"
                xfill True
                vbox:
                    spacing 10
                    text "[mc_surname] [mc_name]" style "jjk_head"
                    text "First-year · [_grade] · Day [day]" style "jjk_small"

                    null height 8
                    text "[_tline]":
                        color "#8ed6ff"
                        size 27
                    text "[_tblurb]" style "jjk_small" xsize 900

                    null height 6
                    text "Current tier — [_tname]":
                        color "#ffffff"
                        size 23
                    text "[_tdesc]" style "jjk_small"
                    if _nx:
                        text "Next — [_nxname] at [_ttag] [_nxreq]" style "jjk_small"

                    null height 6
                    text "[_tverb] — [_tverbd]" style "jjk_small" xsize 900

                    null height 12
                    hbox:
                        spacing 26
                        vbox:
                            text _("Control") style "jjk_label"
                            use meter(control, width=260, height=12, fill="#a259ff")
                        vbox:
                            text _("Output") style "jjk_label"
                            use meter(output, width=260, height=12, fill="#ff8f6a")
                        vbox:
                            text _("Insight") style "jjk_label"
                            use meter(insight, width=260, height=12, fill="#8ed6ff")

            frame:
                style "jjk_panel"
                xfill True
                vbox:
                    spacing 18
                    text _("Bonds") style "jjk_head"

                    for _key in ROSTER_ORDER:
                        if _key in roster:
                            $ _info = CAST[_key]
                            $ _nm2 = _info["name"]
                            $ _col2 = _info["color"]
                            $ _v = bonds.get(_key, 0)
                            $ _r = bond_rank(_v)[1]
                            $ _av = affection.get(_key, 0)
                            $ _ar = aff_rank(_av)[1]

                            vbox:
                                spacing 6
                                hbox:
                                    spacing 14
                                    text "[_nm2]":
                                        color _col2
                                        size 25
                                    text "— [_r]" style "jjk_small" yalign 1.0
                                use meter(_v, width=520, height=11, fill=_col2)
                                if is_romanceable(_key):
                                    hbox:
                                        spacing 12
                                        text "♡ [_ar]":
                                            color "#ff8fb0"
                                            size 18
                                        use meter(_av, width=380, height=8, fill="#ff8fb0") 
                                null height 4


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
                vbox:
                    spacing 6
                    text _("Arc One — Tokyo Jujutsu High") style "jjk_head"
                    text "Day [day] · [_left2] days until the Kyoto exchange" style "jjk_small"

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

                    frame:
                        style "jjk_panel"
                        xfill True

                        vbox:
                            spacing 10

                            hbox:
                                spacing 14
                                text "[_title]":
                                    color _col
                                    size 28
                                text "[_owner]" style "jjk_small" yalign 1.0
                                if _fin:
                                    text _("· resolved"):
                                        color "#77e0a0"
                                        size 19
                                        yalign 1.0

                            use meter(_st + 1, _total, width=420, height=8, fill=_col)

                            null height 4

                            for _line in _shown:
                                text "— [_line]":
                                    color "#cfc8dd"
                                    size 20
                                    xsize 900
