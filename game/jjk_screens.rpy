################################################################################
## Cursed Bonds — custom screens shared by the prologue and the sandbox.
##
## Text roles (jjk_display / jjk_label / jjk_small) live in screens.rpy next to
## the base styles. This file adds the panel, the section head, the meter, and
## the two full-screen cards.
################################################################################

## Shared styling ##############################################################

style jjk_panel is frame:
    background Frame("gui/panel.png", 4, 4)
    padding (34, 28)

style jjk_panel_solid is jjk_panel:
    background Frame("gui/panel_solid.png", 4, 4)

style jjk_head is text:
    font gui.display_font
    color gui.paper
    size 32

style jjk_value is text:
    font gui.body_medium_font
    color gui.paper
    size 26

style jjk_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    xfill True
    padding (24, 14)

style jjk_button_text is text:
    font gui.body_medium_font
    color gui.dim
    hover_color gui.paper
    insensitive_color gui.mute
    size 23

style jjk_button_primary is jjk_button:
    background Frame("gui/panel_active.png", 4, 4)
    hover_background Frame("gui/panel_active.png", 4, 4)

style jjk_button_primary_text is jjk_button_text:
    color gui.paper


## Section head: seal + title, optional trailing note, then a rule. ############

screen section(title, k="術", note=""):
    vbox:
        spacing 10
        xfill True
        hbox:
            spacing 16
            use seal(k, 44)
            text title style "jjk_head" yalign 0.5
            if note:
                text note style "jjk_small" yalign 0.5
        use rule()


## A thin flat meter, used for bonds and cursed energy. ########################

screen meter(value, maximum=100, width=320, height=8, fill=gui.violet, back=gui.line, marker=None):

    $ _filled = max(0, min(width, int(width * (float(value) / float(max(1, maximum))))))

    fixed:
        xysize (width, height)
        add Solid(back) xysize (width, height)
        if _filled:
            add Solid(fill) xysize (_filled, height)
        ## Optional cap marker — a hairline showing where the meter is allowed to reach.
        if marker is not None:
            $ _mx = max(0, min(width - 2, int(width * (float(marker) / float(max(1, maximum))))))
            add Solid(gui.paper) xpos _mx xysize (2, height)


## Chapter card ################################################################

screen chapter_card(kicker, title, subtitle=""):

    zorder 80

    add Solid(gui.ink)

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 20

        hbox:
            xalign 0.5
            spacing 16
            use seal("章", 44)
            text "[kicker]":
                yalign 0.5
                font gui.body_medium_font
                color gui.violet2
                size 22
                kerning 6

        text "[title]":
            xalign 0.5
            font gui.display_heavy_font
            color gui.paper
            size 80

        if subtitle:
            text "[subtitle]":
                xalign 0.5
                color gui.dim
                size 24

        null height 8
        use rule(360)


## End-of-prologue summary #####################################################

screen run_summary():

    modal True
    zorder 70

    add "bg veil"
    add Solid(gui.ink) alpha 0.72

    frame:
        style "jjk_panel_solid"
        xalign 0.5
        yalign 0.5
        xsize 960

        vbox:
            spacing 18

            use section(_("End of the Prologue"), k="序", note="[mc_surname] [mc_name]")

            null height 6

            for _key in BOND_ORDER:

                $ _info = CAST[_key]
                $ _val = bonds[_key]
                $ _short = _info["short"]
                $ _col = _info["color"]
                $ _rank = bond_rank(_val)[1]

                hbox:
                    spacing 18
                    fixed:
                        xysize (170, 30)
                        text "[_short]":
                            font gui.display_font
                            color _col
                            size 24
                            yalign 0.5
                    fixed:
                        xysize (440, 30)
                        use meter(_val, width=440, height=6, fill=_col)
                    text "[_rank]" style "jjk_small" yalign 0.5

            null height 14

            textbutton _("Continue"):
                style "jjk_button_primary"
                text_style "jjk_button_primary_text"
                xfill False
                xalign 1.0
                action Return(True)
