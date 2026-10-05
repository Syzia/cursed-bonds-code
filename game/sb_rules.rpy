################################################################################
## Cursed Bonds — small rules that sit between packages.
##
## Phase 2, P0 (PHASE2_DESIGN.md D5, D25, 6.1). Final: frozen after wave 0.
##
##   rule_hangout_gate(e)   character scenes wait for roll call (D25)
##   label rule_walk_to(loc)    walk somewhere, if the door is open (the
##                              journal's "Go there")
##   rule_layout(name)      a layout sidecar, game/layout/<name>.json, as a dict
##
## Sidecars (D5; schemas in 6.1, every key optional, lists not tuples):
##   area_<key>.json    {"spots": {"<loc>": [x, y]}}
##   view_<place>.json  {"slots": {"<n>": [[xcenter, yoffset, zoom, far], ...]},
##                       "poses": {"<who>" or "<who>__<variant>": [x, y, w, h]}}
##   hot_<place>.json   {"spots": {"<hotspot id>": [x, y]}}
################################################################################

init -5 python:
    import builtins
    import json as _rule_json

    ## The flag the character scenes wait for (D25). Roll call is day 2.
    RULE_HANGOUT_AFTER = "roll_call"

    ## name -> the sidecar's dict, read once. Outside the store: never saved.
    RULE_LAYOUT = builtins.dict()

    def rule_hangout_gate(e):
        """P0 (sb_rules.rpy), final. bool. An event gate: a `hangout` event
        is held until roll call (the flag RULE_HANGOUT_AFTER). A save that is
        already past it is never held: "st_roll_call" in done_events, or the
        flag sunmall_done, count too. Every other kind of event passes, and
        so does everything in explore mode, which has no story to wait for."""
        if e.get("kind") != "hangout":
            return True
        if store.explore_mode:
            return True
        return bool(has_flag(RULE_HANGOUT_AFTER)
                    or "st_roll_call" in store.done_events
                    or has_flag("sunmall_done"))

    register_event_gate(rule_hangout_gate)

    def rule_layout(name):
        """P0 (sb_rules.rpy), final. The layout sidecar game/layout/<name>.json
        as a dict; {} when there is no such file (or it doesn't hold a JSON
        object). `name` is the full stem: "area_school", "view_dorm_common",
        "hot_dorm_common". Each call returns a fresh copy."""
        if name not in RULE_LAYOUT:
            data = builtins.dict()
            path = "layout/%s.json" % name
            if renpy.loadable(path):
                try:
                    with renpy.open_file(path, encoding="utf-8") as f:
                        got = _rule_json.load(f)
                    if isinstance(got, builtins.dict):
                        data = got
                except Exception:
                    if config.developer:
                        raise
            RULE_LAYOUT[name] = data
        return _rule_json.loads(_rule_json.dumps(RULE_LAYOUT[name]))


## Walk to a room (the journal's "Go there", D6): moves only if can_enter(loc)
## lets me in, else says why and leaves me where I am. The loop calls it for
## the journal's ("go", loc).
label rule_walk_to(loc):
    if loc not in LOCATIONS or loc == here:
        return
    $ _rule_ok, _rule_why = can_enter(loc)
    if not _rule_ok:
        "[_rule_why]"
        return
    $ here = loc
    scene expression graded_bg()
    with Dissolve(0.4)
    return
