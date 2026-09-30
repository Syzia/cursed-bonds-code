################################################################################
## Cursed Bonds — the map.
##
## WP0 moved the campus map here from sb_screens.rpy (without the old
## technique's line) and gave it the `layer` argument. WP1 owns this file from here: the
## six-area campus layer and the Tokyo layer (4.6).
##
## Returns ("go", loc) or ("cancel",) to sb_loop.rpy; WP1 adds ("district", key).
################################################################################

## Map styles ###################################################################

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


## Campus map ###################################################################

screen sb_map(layer="campus"):

    tag sandbox

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
        text _("Travel is free. Doing something there costs the period."):
            xalign 0.5
            color gui.dim
            size 19

    for _key in LOC_ORDER:

        $ _L = LOCATIONS[_key]
        $ _ok, _why = can_enter(_key)
        $ _cur = (_key == here)
        $ _folk = who_is_here(_key)
        $ _nm = _L["name"]
        $ _people = ("%d here" % len(_folk) if _folk else "")

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
