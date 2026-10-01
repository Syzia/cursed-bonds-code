################################################################################
## Cursed Bonds — the Black Market.
##
## Phase 2 (PHASE2_DESIGN.md 4.16, D24, D29, 6.1). P4b builds this file. P0
## wrote the stubs below: with them there is no market, and everything that
## would mention it (the review button, the rumour page, the night menu) asks
## market_exists() first.
################################################################################

init -1 python:

    def market_exists():
        """P4b (sb_market.rpy); P0's stub returns False. bool: the market
        is built."""
        return False

    def market_rows():
        """P4b; stub []. A list of (id, price, state, reason), state one of
        "buy", "sold", "poor"."""
        return []

    def market_buy(id):
        """P4b; stub False. bool: the item was bought (yen spent, item given)."""
        return False


## P4b; P0's stub is an empty screen that closes itself.
## Returns ("buy", id) or ("close",).
screen market_screen():
    tag sandbox
    timer 0.01 action Return(("close",))

## P4b; P0's stub only returns.
label market_open:
    return


## Market state (3.3).
default market_bought = set()    # once-only stock already bought
