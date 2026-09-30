################################################################################
## Cursed Bonds — the Tokyo layer: districts and trips in Ijichi's car.
##
## WP1 owns this file (PHASE1_DESIGN.md 3.3). WP0 wrote the frozen signatures
## below as stubs, so other packages can code against them.
################################################################################

init -1 python:

    ## key -> dict(name, kanji, desc, places, bg, min_grade, needs_flag,
    ## locked_hint, lines). (WP0 stub: empty.)
    DISTRICT_ORDER = []
    DISTRICTS = {}

    def tokyo_open():
        """WP1. The Tokyo tab is open (after Ijichi's ride-along). (WP0 stub: False.)"""
        return False

    def district_state(key):
        """WP1. (open, reason) for a district, the reason in the player's
        words. (WP0 stub: (False, "Later").)"""
        return (False, "Later")

    def trip_ok_now():
        """WP1. Ijichi is at the gate and it is Morning, Noon or Afternoon. (WP0 stub: False.)"""
        return False

    def car_action_ok():
        """WP1. The "Ask Ijichi for a ride" action is offered. (WP0 stub: False.)"""
        return False


## WP1. Half a day in a district, then back at the gate. (WP0 stub: returns.)
label sb_trip(key):
    return

## WP1. The car action: the Tokyo layer of the map. (WP0 stub: returns.)
label sb_do_car:
    return
