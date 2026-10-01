################################################################################
## Cursed Bonds — fishing at the riverside.
##
## Phase 2 (PHASE2_DESIGN.md 4.13, D33, 6.1). P6 builds this file. P0 wrote
## the stubs below: nothing can be caught yet.
################################################################################

init -1 python:

    def fish_land(kind, cm):
        """P6 (room_fishing.rpy); P0's stub changes nothing. Settles one
        catch and returns dict(id, cm, yen, record)."""
        return dict(id=kind, cm=cm, yen=0, record=False)

    def fish_records():
        """P6; stub []. A list of (name, cm or None): the record book, for
        its panel and the journal's Me page."""
        return []


## P6; P0's stub only returns.
label sb_do_fish_cast:
    return


## Fishing state (3.3).
default fish_log = {}            # species id -> longest cm (int)
default fish_state = {}          # the sitting in progress; {} otherwise
default fish_cursed_week = -1    # the week the cursed catch last came up
