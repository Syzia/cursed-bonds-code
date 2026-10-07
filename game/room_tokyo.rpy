################################################################################
## Cursed Bonds — friends in Tokyo at weekends.
##
## The second UI overhaul (docs/UI2_DESIGN.md 7.6, 9.3, D51). This file is the
## scaffold's STUB (U0c2); U5 fills it.
##
## The frozen label sb_trip (sb_tokyo.rpy) calls `label district_<key>` when
## one exists, after the arrival lines and before the drive back. The two
## labels below are that hook. As stubs they only return, so a ride plays
## exactly as it did before this file existed. Who is in which district, and
## when, is the table WORLD_AWAY (sb_world.rpy).
##
##   tky_here(key)           who a ride begun now finds in a district: a list
##                           of person keys (the stub: nobody)
##   tky_caption(who, key)   what a friend is doing there, one first-person
##                           line; "" when they have none (the stub: "")
##   TKY_LINES, TKY_BOND     the lines of "Spend the afternoon together", and
##                           the Bond it gives
##   label district_harajuku, label district_shibuya, label tky_people(key)
##   screen tky_meet(key)    returns ("talk", who), ("with", who) or ("back",)
##
## Frozen from this commit (2.3): the names of the three labels and of the
## screen, and the screen's three return tuples.
##
## A caption says what a friend is doing in the street, dressed as their
## sprite (K16).
################################################################################

init python:

    ## who -> district -> the lines of an afternoon spent together there
    ## (filled by U5), and the Bond it gives: the figure a night out already
    ## gives a companion.
    TKY_LINES = {}
    TKY_BOND = 4

    def tky_here(key):
        """U0c2 (room_tokyo.rpy): a stub, filled by U5. A list of person
        keys: who a ride begun now finds in the district `key`. The stub:
        nobody."""
        return []

    def tky_caption(who, key):
        """U0c2 (room_tokyo.rpy): a stub, filled by U5. A caption string:
        what `who` is doing in the district `key`; "" when that person has
        none there. The stub: ""."""
        return ""


label district_harajuku:
    return

label district_shibuya:
    return

label tky_people(key):
    return


## The friends met in a district (7.6): a tile for each, and "Head back".
## The stub answers ("back",) at once, so nothing can wait on it.
screen tky_meet(key):
    timer 0.01 action Return(("back",))
