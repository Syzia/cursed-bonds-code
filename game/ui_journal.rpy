################################################################################
## Cursed Bonds — the journal.
##
## WP0 moved the Status and Journal screens here from sb_screens.rpy (without
## the countdown) and added the `journal` stub. WP8 owns this file from here:
## `journal(tab)` with its six tabs (4.7), with `jjk_status` and
## `jjk_journal` becoming wrappers around it.
################################################################################

init python:

    def kaito_card_image():
        """WP8. The unlit full picture on the Stats tab: the Yotsuka outfit
        until the campus opens, the uniform after."""
        if has_flag("settled_in"):
            return "images/char/mc_neutral.png"
        return "images/char/mcyotsuka_neutral.png"


## The journal ##################################################################
##
## tab: people, missions, memories, stats, equipment or inventory.
## (WP0 stub: the old Status screen for "stats", the old Journal otherwise.)

screen journal(tab="people"):

    tag menu

    if tab == "stats":
        use jjk_status
    else:
        use jjk_journal


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


## Journal ######################################################################

screen jjk_journal():

    tag menu

    $ _open = threads_open()

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
                        text "DAY [day]" style "jjk_label"

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
