################################################################################
## Cursed Bonds — Utahime's board of graded jobs.
##
## WP4 owns this file (PHASE1_DESIGN.md 3.7, 4.8). WP0 wrote the frozen
## signatures below as stubs, so other packages can code against them.
################################################################################

init -1 python:

    def board_host():
        """WP4. (who, place) running the board: Utahime at her office, or
        Ijichi at Yaga's once utahime_leads_kyoto is set."""
        return ("utahime", "utahime_office")

    def board_open():
        """WP4. True when the board can be used here and now. (WP0 stub: False.)"""
        return False

    def board_summary():
        """WP4. What the journal's Board tab needs: offers, taken cards, the
        last 10 runs and the misgrade count. (WP0 stub: {}.)"""
        return {}

    def misgrade_count():
        """WP4. How many misgraded jobs the player has found. (WP0 stub: 0.)"""
        return 0


## WP4. The board action: board_screen, then board_partner, then the run.
## (WP0 stub: returns.)
label sb_do_board:
    return

## WP4. Three job cards and the taken cards. (WP0 stub: empty.)
screen board_screen():
    tag sandbox
    pass

## WP4. Who can come along on a job. (WP0 stub: empty.)
screen board_partner(offer):
    tag sandbox
    pass
