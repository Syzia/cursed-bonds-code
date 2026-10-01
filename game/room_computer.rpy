################################################################################
## Cursed Bonds — the computer in my room.
##
## Phase 2 (PHASE2_DESIGN.md 4.11, D31, 6.1). P6 builds this file. P0 wrote
## the stubs below: no pages, no requests, nothing read.
################################################################################

init -1 python:

    def pc_has_read(page):
        """P6 (room_computer.rpy); P0's stub returns False. bool: the page
        has been read."""
        return False

    def pc_request(page, note=""):
        """P6; the stub does nothing. Returns None. Asks me to look a page
        up; it shows as a lead in the journal."""
        return None

    def pc_leads():
        """P6; stub []. A list of (page, note): the open requests, for the
        journal's Missions tab."""
        return []

    def pc_records():
        """P6; stub []. A list of str: the titles of the pages read, for the
        journal's Me page."""
        return []


## P6; P0's stub only returns.
label sb_do_pc_open:
    return


## Computer state (3.3).
default pc_read = set()          # page ids read
default pc_requests = []         # [(page, note)]
default pc_checked_week = -1     # the board_week already cross-checked
