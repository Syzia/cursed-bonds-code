################################################################################
## Cursed Bonds — hooks, save migrations and load recovery.
##
## WP0 (phase 1). Frozen after WP0: changes go through WP11.
##
## System files plug into the core loop through the registries here, so no
## package has to edit another package's code:
##
##   register_new_day(fn, order)          fn() at the end of new_day()
##   register_event_gate(fn)              find_events() drops an event any gate refuses
##   register_event_done(fn)              play_event runs fn(e) after the scene
##   register_place_action(id, ...)       an extra button in the place view
##   register_migration(order, fn, name)  upgrades an old save's state
##   register_validator(fn)               lint prints each problem as "VALIDATE: ..."
##
## Toasts: toast(text, kind, who, amount) is the one way to tell the player
## that something happened. The queue lives outside the saved store (D7).
################################################################################

init -5 python:
    import builtins

    SAVE_VERSION = 1

    NEW_DAY_HOOKS = []      # [(order, fn)]    fn() — run at the end of new_day()
    EVENT_GATES = []        # [fn(e) -> bool]  find_events() drops e if any gate says False
    EVENT_DONE_HOOKS = []   # [fn(e)]          play_event runs these after the label + thread advance
    MIGRATIONS = []         # [(order, name, fn)]
    PLACE_ACTIONS = []      # dicts, see register_place_action
    VALIDATORS = []         # [fn() -> [str]]  run by lint (config.lint_hooks)

    ## New day ------------------------------------------------------------------

    def register_new_day(fn, order=50):
        """WP0. Run fn() at the end of every new_day(), lowest order first."""
        NEW_DAY_HOOKS.append((order, fn))

    def run_new_day_hooks():
        """WP0. Called last in new_day() (sb_world.rpy)."""
        for order, fn in sorted(NEW_DAY_HOOKS, key=lambda h: h[0]):
            fn()

    ## Events -------------------------------------------------------------------

    def register_event_gate(fn):
        """WP0. fn(e) -> bool. find_events() drops an event when any gate says False."""
        EVENT_GATES.append(fn)

    def event_allowed(e):
        """WP0. True when every registered gate lets the event e fire."""
        for fn in EVENT_GATES:
            if not fn(e):
                return False
        return True

    def register_event_done(fn):
        """WP0. fn(e) runs after play_event has played e and advanced its thread."""
        EVENT_DONE_HOOKS.append(fn)

    def run_event_done(e):
        """WP0. Called by play_event (sb_events.rpy) after the scene."""
        for fn in EVENT_DONE_HOOKS:
            fn(e)

    ## Place actions ------------------------------------------------------------

    def register_place_action(id, label, hint, cost=0, locs=None, when=None, order=50, explore=False):
        """WP0. An extra button in the place view.

        id       the action runs `label sb_do_<id>`
        label    the button's title; hint is the line under it
        cost     periods it takes (drawn as diamonds; the label charges them)
        locs     a place key or a tuple of them; None means everywhere
        when     the NAME of a store function returning bool; None means always
        order    lower comes first
        explore  also offered in explore mode (otherwise hidden there)
        """
        if isinstance(locs, str):
            locs = (locs,)
        PLACE_ACTIONS.append(dict(
            id=id, label=label, hint=hint, cost=cost,
            locs=(tuple(locs) if locs is not None else None),
            when=when, order=order, explore=explore))

    def registered_place_actions(loc):
        """WP0. [(id, label, hint, cost)] offered at loc right now, sorted by order."""
        out = []
        for a in sorted(PLACE_ACTIONS, key=lambda a: a["order"]):
            if a["locs"] is not None and loc not in a["locs"]:
                continue
            if store.explore_mode and not a["explore"]:
                continue
            if a["when"]:
                fn = getattr(store, a["when"], None)
                if fn is None or not fn():
                    continue
            out.append((a["id"], a["label"], a["hint"], a["cost"]))
        return out

    ## Migrations ---------------------------------------------------------------

    def register_migration(order, fn, name):
        """WP0. fn() upgrades an old save's state. It runs on every load, so it
        must be idempotent. Orders are listed in PHASE1_DESIGN.md 3.12."""
        MIGRATIONS.append((order, name, fn))

    def run_migrations(block=False):
        """WP0. Run every migration, lowest order first, each in try/except
        (re-raised when config.developer). Toasts are muted while they run.
        Sets save_version and returns True if the save was upgraded; with
        block=True an upgrade also blocks rollback to the pre-migration state."""
        upgraded = getattr(store, "save_version", 0) < SAVE_VERSION
        TOAST_MUTE[0] += 1
        try:
            for order, name, fn in sorted(MIGRATIONS, key=lambda m: m[0]):
                try:
                    fn()
                except Exception:
                    if config.developer:
                        raise
                    import traceback
                    print("Migration %s (%s) failed:" % (order, name))
                    traceback.print_exc()
        finally:
            TOAST_MUTE[0] -= 1
        if upgraded:
            store.save_version = SAVE_VERSION
            if block:
                renpy.block_rollback()
        return upgraded

    def ensure_state():
        """WP0. Called by the sandbox on every pass (and by arc_one_open and
        explore mode). Does work only while save_version < SAVE_VERSION."""
        if getattr(store, "save_version", 0) < SAVE_VERSION:
            return run_migrations()
        return False

    ## Validators ---------------------------------------------------------------

    def register_validator(fn):
        """WP0. fn() -> [str]. Lint prints each string as "VALIDATE: <msg>"."""
        VALIDATORS.append(fn)

    def _run_validators():
        for fn in VALIDATORS:
            try:
                problems = fn() or []
            except Exception as e:
                problems = ["%s raised %s: %s" % (getattr(fn, "__name__", fn), type(e).__name__, e)]
            for p in problems:
                print("VALIDATE: %s" % p)

    ## Toasts (D7, D34) ---------------------------------------------------------
    ##
    ## Plain builtins lists made at init and never assigned at runtime: they are
    ## not saved and not rolled back.

    TOAST_SINK = builtins.list([None])  # WP7 puts toast_push here
    TOAST_MUTE = builtins.list([0])     # > 0 while migrations run

    def toast(text, kind="info", who=None, amount=None):
        """WP0 (final). Tell the player something happened.

        kind    bond, bond_rank, aff, stat, grade, mission, item, thread or info
        who     a CAST key, for the colour (and for merging bond/aff gains)
        amount  the number behind a gain, so consecutive gains can merge

        Muted during replays and migrations. Goes to TOAST_SINK[0] once WP7
        sets it, and to the stock notify screen until then.
        """
        if getattr(store, "_in_replay", None) or TOAST_MUTE[0]:
            return
        sink = TOAST_SINK[0]
        if sink is not None:
            sink(text, kind, who, amount)
        else:
            ## Never renpy.notify: WP7 routes config.notify back into toast().
            renpy.display_notify(text)

    ## The prologue, as steps (3.13) ---------------------------------------------
    ##
    ## (step label, the chapter label that plays it before WP9 splits the
    ## chapters into called sub-labels).

    PROLOGUE_STEPS = [("ch1_diner", "chapter_one"), ("ch1_the_thing", "chapter_one"),
                      ("ch1_gojo", "chapter_one"), ("chapter_one_b", "chapter_one_b"),
                      ("ch2_arrival", "chapter_two"), ("ch2_the_veil", "chapter_two"),
                      ("ch2_yaga", "chapter_two"), ("ch2_first_years", "chapter_two"),
                      ("arc_one_open", "arc_one_open")]

    def legacy_story_point():
        """WP0. The prologue step an old save (no story_point) resumes at,
        read from its flags. "sandbox" once it has settled in."""
        if has_flag("settled_in"):
            return "sandbox"
        ## An old linear-build save (before the sandbox) that reached the Sun
        ## Mall without ever setting settled_in: open the campus instead of
        ## replaying the prologue. The current build plays the Sun Mall only
        ## after settled_in, so its flags (or the pre-d06486a `partner`)
        ## without settled_in can only come from such a save. Every path
        ## through chapter_four sets one of these before its `return`.
        if (getattr(store, "partner", None) or getattr(store, "_partner", None)
                or any(has_flag(f) for f in ("read_wall", "ignored_wall", "scouted_corridor",
                                             "saved_civilian", "fought_first",
                                             "climax_strong", "climax_thin"))):
            return "arc_one_open"
        if has_flag("enrolled"):
            return "ch2_first_years"
        if has_flag("chose_jujutsu"):
            return "ch2_arrival"
        if any(has_flag(f) for f in ("gojo_asked_why", "gojo_asked_sana", "gojo_asked_advice")):
            return "chapter_one_b"
        if (any(has_flag(f) for f in ("reached_for_her", "stood_in_front", "listened_first"))
                or any(f.startswith("dinner_") for f in store.flags)):
            return "ch1_the_thing"
        return "ch1_diner"

    def prologue_plan(point):
        """WP0. The labels still to play from `point` (a step or chapter label),
        starting with point itself. Before the sub-labels exist (pre-WP9), the
        remaining chapters instead. [] for "sandbox" or anything unknown."""
        steps = [s for s, c in PROLOGUE_STEPS]
        chapters = [c for s, c in PROLOGUE_STEPS]
        if point in steps:
            i = steps.index(point)
        elif point in chapters:
            i = chapters.index(point)
        else:
            return []
        rest = PROLOGUE_STEPS[i:]
        if all(renpy.has_label(s) for s, c in rest):
            return [s for s, c in rest]
        out = []
        for s, c in rest:
            if c not in out:
                out.append(c)
        return out

    ## Migration 5 (WP0, D25) ---------------------------------------------------

    def _migrate_5():
        """WP0, migration 5. Runs on every load, like every migration, and
        each step is idempotent: the sandbox no longer switches the quick menu
        off (it hides itself instead, D25), a mid-scene save may still hold the
        player's own sprite, and the technique caption follows the save's
        technique (Last Light once WP2 leaves only timestop). A save made
        inside the Sun Mall mission before d06486a renamed its `partner` to
        `_partner` would stop at the next `if _partner` with a NameError, so
        the old name is copied across."""
        store.quick_menu = True
        if renpy.showing("mc"):
            renpy.hide("mc")
        store.tname = TECHNIQUES.get(store.technique, {}).get("name", "Last Light")
        if getattr(store, "_partner", None) is None and getattr(store, "partner", None):
            store._partner = store.partner

    register_migration(5, _migrate_5, "quick menu on, stale mc sprite, tname, Sun Mall _partner")

    ## WP0's validator ------------------------------------------------------------

    def _validate_place_actions():
        out = []
        seen = set()
        for a in PLACE_ACTIONS:
            if a["id"] in seen:
                out.append("place action %r is registered twice" % a["id"])
            seen.add(a["id"])
            if not renpy.has_label("sb_do_" + a["id"]):
                out.append("place action %r has no label sb_do_%s" % (a["id"], a["id"]))
            if a["when"] and not callable(getattr(store, a["when"], None)):
                out.append("place action %r: when=%r is not a store function" % (a["id"], a["when"]))
        return out

    register_validator(_validate_place_actions)

    config.after_load_callbacks.append(lambda: run_migrations(block=True))
    config.lint_hooks.append(_run_validators)


define config.load_failed_label = "load_recover"
define config.return_not_found_label = "return_recover"

default story_point = None       # the prologue step playing (set at the top of each step label)
default save_version = 0
default arc_start_day = 1        # set by arc_one_open
default actions_today = set()    # once-a-day actions ("hold", "rest", "racks", "veil", "lesson", "cap:control"…)
default hide_side_images = False # the prologue's blackout
default smoke_autoplay = False   # test harness hook (8.1): skips renpy.input, auto-answers combat
default persistent.mc_face = True


################################################################################
## Load recovery (3.13)
################################################################################

## Ren'Py jumps here when a save's position no longer exists anywhere in its
## rollback log. load_failed() skips the default statements and the after-load
## callbacks (D1), so both run here first.
label load_recover:
    $ renpy.execute_default_statement(False)   # D1: load_failed() skipped this
    $ _in_replay = None
    $ run_migrations(block=True)
    scene black
    if has_flag("settled_in"):
        "(This save came from an older version of the game. Picking up on campus.)"
        jump sandbox
    "(This save came from an older version of the game. The prologue has been rewritten, so it picks up at the start of the scene.)"
    jump resume_story

## A `return` whose return site was rewritten lands here (D2), with the call
## stack popped to one frame.
label return_recover:
    $ run_migrations(block=True)
    if has_flag("settled_in"):
        jump sandbox
    jump resume_story

## Plays the rest of the prologue from the step the save was in, then opens the
## campus, as label start does.
label resume_story:
    $ _plan = prologue_plan(story_point or legacy_story_point())
    while _plan:
        $ _next = _plan.pop(0)
        call expression _next
    jump sandbox


################################################################################
## Retired labels (2.1.2)
################################################################################

## An old technique's place action, removed with the prologue rewrite
## (b33f000). A save made while it played rolls back to the loop's
## `call expression "sb_do_" + _r[1]` and calls it again; it now returns
## straight to the place view.
label sb_do_replay:
    return
