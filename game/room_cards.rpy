################################################################################
## Cursed Bonds — the card table.
##
## Phase 2 (PHASE2_DESIGN.md 4.12, D32, 6.1). P7 builds this file (blackjack,
## then poker). P0 wrote the stubs below: the table is closed, and no game is
## registered (register_minigame, sb_hotspots.rpy).
################################################################################

init -1 python:

    def cards_ok():
        """P7 (room_cards.rpy); P0's stub returns False. bool: the card
        table can be sat at now."""
        return False

    def cards_new(game, opponents, stake):
        """P7; stub {}. The fresh cards_state dict for a sitting."""
        return {}

    def cards_records():
        """P7; stub dict(today=0). dict(today=int): the yen won at cards
        today, for the journal's Me page."""
        return dict(today=0)


## P7; P0's stub only returns.
label sb_do_cards_play:
    return


## Card state (3.3).
default cards_state = {}         # the sitting in progress (deck as a list of ints); {} otherwise
default cards_won_day = 0        # the day cards_won counts for
default cards_won = 0            # yen won at cards that day
