################################################################################
## Cursed Bonds — the Swimming Pool.
##
## The second UI overhaul (docs/UI2_DESIGN.md 4.7, 9.3, D34, K16). This file is
## the scaffold's STUB (U0c2): the action is registered, closed, and both
## labels only return, so that every id exists from wave 0. U5 fills it:
## pool_ok(), the labels' bodies and their lines.
##
##   pool_ok()               bool: the pool can be swum in now (the stub: never)
##   place action pool_swim  "Swim", at the pool; label sb_do_pool_swim
##   label act_swim_pool(who)   the scene of the activity swim_pool ("Swim
##                           together"; its row is in sb_activities.rpy and is
##                           hidden while pool_ok() is False)
##
## Frozen from this commit (2.3): the action id pool_swim, the activity id
## swim_pool, and the names of the two labels (the loop calls an activity as
## "act_" + its id).
##
## Anyone else at the pool is on the deck, dressed as their sprite (K16).
################################################################################

init python:

    def pool_ok():
        """U0c2 (room_pool.rpy): a stub, filled by U5. bool: the pool can be
        swum in now. False until the pool is built, so neither "Swim" nor
        "Swim together" is offered anywhere."""
        return False

    register_place_action("pool_swim", "Swim", "Lengths, until my arms stop arguing. An hour.",
                          cost=1, locs=("pool",), when="pool_ok")
    ICON_FOR[("act", "pool_swim")] = "pool_swim"


label sb_do_pool_swim:
    return

label act_swim_pool(who):
    return
