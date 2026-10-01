################################################################################
## Cursed Bonds — the night.
##
## Phase 2 (PHASE2_DESIGN.md 4.15, D20 to D26, 6.1). P4b builds this file. P0
## wrote the stubs below: every function and label of the contract, each
## returning the frozen shape, and every saved variable at its default. With
## the stubs the night changes nothing: no rule, no Gojo night, no night out.
################################################################################

init -1 python:

    def night_exists():
        """P4b (sb_night.rpy); P0's stub returns False. bool: the night rule
        is built. The review panel hides its two night buttons until it is."""
        return False

    def night_pending():
        """P4b; stub False. bool: the day turned while I was away from my
        room, and the loop should walk me home (night_carry_home)."""
        return False

    def night_can_work():
        """P4b; stub True. bool: missions, board jobs and training can be
        started today (False the day after a Gojo night)."""
        return True

    def night_block_reason():
        """P4b; stub "". str: why I can't work today, "" when clear."""
        return ""

    def night_tag():
        """P4b; stub "". str: the status chip's words ("Worn out",
        "Rough morning"), "" when clear."""
        return ""

    def night_filter_actions(loc, acts):
        """P4b; the stub returns acts unchanged. A list of (id, label, hint,
        cost): the place's actions as the night rule leaves them."""
        return acts

    def night_allows(id, cost):
        """P4b; stub True. bool: the night lets this start now. id is an
        action or activity id, or "mission:" + mid; cost is its periods."""
        return True

    def night_blocks(id):
        """P4b; stub False. bool: this action or activity is closed today
        because of a rest day."""
        return False

    def night_marks():
        """P4b; stub {}. dict {area key: "moon"}: the map's night badges."""
        return {}

    def night_out_ok(key):
        """P4b; stub (False, ""). (bool, str): a night in this district can
        start now, and the reason when it can't. (False, "") hides the map's
        night button."""
        return (False, "")

    def night_gojo_ok():
        """P4b; stub False. bool: "Train until morning" is offered here, now."""
        return False

    def night_gojo_due():
        """P4b; stub False. bool: a Gojo night is due this morning."""
        return False

    def night_day_best():
        """P4b; stub 0. int: the Control the best day of training would add
        from my Control now."""
        return 0

    def night_gojo_gain():
        """P4b; stub (0, 0). (int, int): the Control and reserve a Gojo
        night gives from where I stand."""
        return (0, 0)

    def night_set_cost(kind):
        """P4b; the stub does nothing. Returns None. Sets tomorrow's cost:
        "gojo" (a rest day) or "out" (a rough morning)."""
        return None

    def night_dev(kind):
        """P4b; the stub does nothing. Returns None. The review tools'
        switches: "gojo", "rest", "market"."""
        return None


## P4b; P0's stubs only return. night_carry_home walks me back to my room
## when the day turned somewhere else; night_out(key) is a night in a Tokyo
## district; sb_do_night_gojo is "Train until morning".
label night_carry_home:
    return

label night_out(key):
    return

label sb_do_night_gojo:
    return

## "Go to bed" (the stub is Sleep).
label sb_do_night_bed:
    call sb_do_sleep
    return


## Night state (3.3). P0 wrote the defaults; P4b gives them their meaning.
default night_carried = ""       # the place where the day turned while I wasn't in my room; "" when none
default night_cost_day = 0       # the day a next-day cost applies to
default night_cost_kind = ""     # "gojo" or "out"
default night_gojo_last = -99    # day of the last Gojo night
default night_gojo_day = 0       # the day tonight's invitation is for
default night_out_last = -99     # day of the last night out
