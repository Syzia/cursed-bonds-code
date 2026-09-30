################################################################################
## Cursed Bonds — memories and replay.
##
## WP5 owns this file (PHASE1_DESIGN.md 3.9). WP0 wrote the frozen signatures
## below as stubs, so other packages can code against them.
################################################################################

init -1 python:

    ## The catalogue: dict(id, title, who, act, label, args, seen, hint,
    ## unlock, bg). (WP0 stub: empty.)
    MEMORIES = []

    def memory_groups(mode):
        """WP5. [(group title, [memory])] by "person" (Sana first) or "act". (WP0 stub: [].)"""
        return []

    def memory_counts():
        """WP5. (seen, total). (WP0 stub: (0, 0).)"""
        return (0, 0)

    def memory_replay(mem):
        """WP5. The action that replays a memory (Replay, locked=False). (WP0 stub: NullAction().)"""
        return NullAction()

    def record_act(aid, who):
        """WP5. Records that an activity scene was seen with someone; called
        by sb_activity. (WP0 stub: no-op.)"""
        return


## WP5. Every replay enters here: calls _mem_label with _mem_args, then ends
## the replay. (WP0 stub: returns.)
label mem_play:
    return
