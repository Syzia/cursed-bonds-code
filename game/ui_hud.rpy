################################################################################
## Cursed Bonds — the HUD, toasts and the objective toast.
##
## WP0 moved the HUD here from sb_screens.rpy, without the Kyoto countdown.
## WP7 owns this file from here: the new HUD (4.1), the toast queue and the
## overlay screen `toasts` (4.2), and `objective_toast` (4.3).
################################################################################

init python:

    def hud_date():
        """'DAY 6 · SAT' — the period is drawn as pips next to it."""
        return "DAY %d · %s" % (store.day, weekday().upper())

    def toast_push(text, kind="info", who=None, amount=None):
        """WP7. Queue a toast for the `toasts` overlay; WP7 puts this in
        TOAST_SINK[0] (3.10). (WP0 stub: no-op, and not yet the sink.)"""
        return

    def check_objective():
        """WP7. Called by the loop: if objective_text() changed since
        last_objective, slide in objective_toast. (WP0 stub: no-op.)"""
        return


## HUD styles ###################################################################

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
## you spend, and what you are. Navigation lives at the far right.

screen sb_hud(on_map=False, person=False):

    $ _tiername = tech_tier()[1]
    $ _tname = tech()["name"]
    $ _loc = _("Campus") if on_map else LOCATIONS[here]["name"]
    $ _date = hud_date()
    $ _per = store.period.upper()

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

            ## Navigation, pushed to the right ------------------------------
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


## Toasts #######################################################################
##
## WP7: the stack of toasts at the top right (4.2), an overlay screen. (WP0
## stub: empty, and not yet in config.overlay_screens.)

screen toasts():
    zorder 150
    pass


## Objective toast ##############################################################
##
## WP7: "NEXT" and the new objective, sliding in at the top centre (4.3).
## (WP0 stub: empty.)

screen objective_toast(text):
    zorder 140
    pass
