################################################################################
## Cursed Bonds — custom screens.
################################################################################

## Shared styling ##############################################################

style jjk_panel is frame:
    background Frame(Solid("#12101acc"), 12, 12)
    padding (36, 30)

style jjk_head is text:
    color "#a259ff"
    size 34

style jjk_label is text:
    color "#cfc8dd"
    size 26

style jjk_value is text:
    color "#ffffff"
    size 26

style jjk_small is text:
    color "#9d95ae"
    size 21


## A thin flat meter, used for bonds and cursed energy. ########################

screen meter(value, maximum=100, width=320, height=12, fill="#a259ff", back="#2a2338"):

    $ _filled = max(1, int(width * (float(value) / float(maximum))))

    fixed:
        xysize (width, height)
        add Solid(back) xysize (width, height)
        add Solid(fill) xysize (_filled, height)


## Chapter card ################################################################

screen chapter_card(kicker, title, subtitle=""):

    zorder 80

    add Solid("#05040a")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 16

        text "[kicker]":
            xalign 0.5
            color "#a259ff"
            size 26

        text "[title]":
            xalign 0.5
            color "#ffffff"
            size 68

        if subtitle:
            text "[subtitle]":
                xalign 0.5
                color "#9d95ae"
                size 24


## End-of-prologue summary #####################################################

screen run_summary():

    modal True
    zorder 70

    add "bg veil"
    add Solid("#06040c") alpha 0.6

    frame:
        style "jjk_panel"
        xalign 0.5
        yalign 0.5
        xsize 940

        vbox:
            spacing 16

            text _("END OF THE PROLOGUE") style "jjk_head" xalign 0.5
            text "[mc_surname] [mc_name]" style "jjk_small" xalign 0.5

            null height 10

            for _key in BOND_ORDER:

                $ _info = CAST[_key]
                $ _val = bonds[_key]
                $ _short = _info["short"]
                $ _col = _info["color"]
                $ _rank = bond_rank(_val)[1]

                hbox:
                    spacing 16

                    fixed:
                        xysize (160, 34)
                        text "[_short]":
                            color _col
                            size 24
                            yalign 0.5

                    fixed:
                        xysize (420, 34)
                        use meter(_val, width=420, height=10, fill=_col)

                    text "[_rank]" style "jjk_small" yalign 0.5

            null height 18

            textbutton _("Continue") action Return(True) xalign 0.5
