################################################################################
## Cursed Bonds — custom screens shared by the prologue and the sandbox.
##
## Text roles (jjk_display / jjk_label / jjk_small) live in screens.rpy next to
## the base styles. This file adds the panel, the section head, the meter, and
## the chapter card.
################################################################################

## Shared styling ##############################################################

style jjk_panel is frame:
    background Frame("gui/panel.png", 4, 4)
    padding (34, 28)

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
