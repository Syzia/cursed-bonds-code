################################################################################
## Cursed Bonds — the Onsen: a soak in the spring, and the sauna.
##
## The second UI overhaul (docs/UI2_DESIGN.md 4.7, 9.3, K16, K17). This file is
## the scaffold's STUB (U0c2): the two actions are registered, closed, with
## labels that only return, so that every id exists from wave 0 (the night's
## validator and the contracts know them). U5 fills it: bath_ok(), the two
## labels' bodies and their lines.
##
##   bath_ok()               bool: a bath can be taken now (the stub: never)
##   place action bath_soak  "Soak", in the Bathhouse; label sb_do_bath_soak
##   place action bath_sauna "Sit it out", in the Sauna; label sb_do_bath_sauna
##
## Frozen from this commit (2.3): the action ids bath_soak and bath_sauna and
## the names of their two labels. Neither label ever holds a menu or a called
## screen.
##
## The baths are optional (K17): nothing anywhere else in the game may read
## whether I bathed. My own soak is told as heat, water and tiredness, and
## nobody else is shown or described in the water (K16).
################################################################################

init python:

    def bath_ok():
        """U0c2 (room_bath.rpy): a stub, filled by U5. bool: a bath can be
        taken now. False until the baths are built, so neither action is
        offered anywhere."""
        return False

    register_place_action("bath_soak", "Soak", "The spring, as hot as I can stand. An hour.",
                          cost=1, locs=("bathhouse",), when="bath_ok")
    register_place_action("bath_sauna", "Sit it out", "The heat, then the cold. An hour.",
                          cost=1, locs=("sauna",), when="bath_ok")
    ICON_FOR[("act", "bath_soak")] = "bath_soak"
    ICON_FOR[("act", "bath_sauna")] = "bath_sauna"


label sb_do_bath_soak:
    return

label sb_do_bath_sauna:
    return
