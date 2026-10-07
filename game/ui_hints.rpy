################################################################################
## Cursed Bonds — one-time hints.
##
## The second UI overhaul (docs/UI2_DESIGN.md 7.5, 9.1, 9.3). This file is the
## scaffold's STUB (U0c2): the saved variable, the six ids, a hint_show that
## does nothing and an empty hint_layer, so that the place view and the map
## can `use hint_layer` from wave 0. U4 fills it.
##
##   hint_seen            the hint ids already shown (saved; a set of strings)
##   HINT_IDS             the six hints, in the order of 7.5
##   hint_show(id)        asks for a hint to be shown; returns None
##   screen hint_layer()  where a hint is drawn (the objective banner's lane)
##
## Frozen from this commit (9.1): the name and shape of hint_seen, the six
## ids, hint_show's signature and that it returns None, hint_layer's name
## and that it takes no parameter. hint_seen is changed only by a function
## that then calls renpy.retain_after_load(): it is changed from a screen,
## and a save loads to the start of the interaction it was made in.
################################################################################

init python:

    ## The six hints (7.5): the first place view; the names key; the first
    ## map; the first person on a stage; the first hour spent; the first
    ## Night.
    HINT_IDS = ("place", "names", "map", "person", "hour", "night")

    def hint_show(id):
        """U0c2 (ui_hints.rpy): a stub, filled by U4. Returns None, always.
        Asks for the one-time hint `id` (one of HINT_IDS) to be shown, if it
        has not been seen. The stub shows nothing."""
        return None


## The hints already shown (3.3): the one new saved variable of the overhaul.
default hint_seen = set()


## Where a hint is drawn. Used by sb_place and sb_map; empty until U4.
screen hint_layer():
    pass
