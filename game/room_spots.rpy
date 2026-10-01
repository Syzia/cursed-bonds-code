################################################################################
## Cursed Bonds — what is in the rooms: hotspots and their lines.
##
## Phase 2 (PHASE2_DESIGN.md 4.10, D30, 6.1). P6 builds this file (the
## hotspots of every room, the vending machine). P0 wrote the stubs below; no
## hotspot is registered yet.
################################################################################

init -1 python:

    def spot_vend_ok():
        """P6 (room_spots.rpy); P0's stub returns False. bool: the courtyard's
        vending machine can be used now."""
        return False


## P6; P0's stub only returns.
label sb_do_spot_vend:
    return
