## tools/smoke/load_slot.rpy -- load one of the owner's saves and report where
## it lands (docs/PHASE1_DESIGN.md, 8.3).
##
##   SMOKE_SAVES=1 SMOKE_SLOT=1-1 tools/smoke.sh tools/smoke/load_slot.rpy
##
## SMOKE_SLOT takes the slot name ("1-1", "auto-3", "_tracesave-2") or the file
## name ("1-1-LT1.save"). tools/load_all_saves.sh runs this for every save.
##
## Before loading, it reads the save's own rollback log to find the statement
## it was saved at and the statement Ren'Py will roll back to (the newest one
## that still exists in the script). Then it loads the slot with renpy.load. A
## config.label_callbacks watcher notes whether load_recover or return_recover
## ran. At the first interaction after the load it records where the game
## stands (renpy.get_filename_line()) and the state that the migrations in
## 3.12 touch, takes a screenshot a moment later, and quits.
##
## It then notes a summary for the report (report.*): version, technique,
## grade, arc, day, roster size, merit, the story step (story_point, or
## legacy_story_point() for a save without one, then the story row the
## objective points at), the objective, the keepsakes in the inventory, and
## where it landed (a statement, or load_recover / return_recover first).
##
## The result notes a status:
##   SAME            landed on the statement it was saved at
##   EARLIER         the saved statement is gone; it rolled back to an older one
##                   (rollback_target) and stopped at the next interaction
##   MOVED           the saved statement exists but it landed elsewhere
##   RECOVER <label> load_recover / return_recover ran
##   UNKNOWN         the save's own log couldn't be read before loading
## Any exception during or after the load fails the run (the "raised" case).
##
## It also notes dead_return_sites: call-stack frames whose return site is gone
## from the script. A `return` that reaches one lands in return_recover later
## in play, after the first stop this harness sees; on_dead_return says where
## return_recover would then send the save.

init 999 python:
    import builtins
    import os
    import time

    class ZZLoadState(builtins.object):
        """Load-test state; outlives the load because nothing replaces it."""

        def __init__(self):
            slot = (os.environ.get("SMOKE_SLOT") or "").strip()
            slot = os.path.basename(slot)
            if slot.endswith(renpy.savegame_suffix):
                slot = slot[:-len(renpy.savegame_suffix)]
            elif slot.endswith(".save"):
                slot = slot[:-len(".save")]
            self.slot = slot
            self.armed = False
            self.after_load = False
            self.labels = builtins.list()
            self.quit_at = None
            self.dumped = False
            self.saved_at = None
            self.target = None
            self.mc_before = None   # renpy.showing("mc") before the migrations ran
            self.game_version = None  # the game version the save was made with

    zz_load = ZZLoadState()

    ## What 3.11/3.12 care about. Names missing from the store (a package
    ## that hasn't landed yet) print as <missing>.
    ZZ_LOAD_FIELDS = (
        "save_version", "story_point", "day", "period", "here", "arc",
        "arc_start_day", "technique", "tname", "grade", "merit",
        "merit_granted", "quick_menu", "hp", "hp_max", "ce", "ce_max",
        "control", "output", "insight", "stamina", "stamina_max", "companion",
        "explore_mode", "mc_name", "mc_surname", "roster", "bonds", "affection",
        "flags", "threads", "done_events", "gojo_today", "gojo_in",
        "actions_today", "hide_side_images", "npc_state", "promotions_log",
        "pending_remarks", "mission_state", "missions_done", "mission_done_day",
        "mission_retry_day", "last_objective", "board_offers", "board_week",
        "memories_seen", "inventory", "items_granted", "yen", "equipped_tool",
        "equipped_talismans", "districts_visited", "_in_replay",
    )

    def zz_load_fmt(v, limit=600):
        if isinstance(v, (set, frozenset)):
            try:
                v = sorted(v)
            except Exception:
                v = builtins.list(v)
            text = "{" + ", ".join(repr(i) for i in v) + "}"
        elif isinstance(v, dict):
            try:
                keys = sorted(v)
            except Exception:
                keys = builtins.list(v)
            text = "{" + ", ".join("%r: %r" % (k, v[k]) for k in keys) + "}"
        else:
            text = repr(v)
        text = " ".join(text.split())
        if len(text) > limit:
            text = text[:limit] + " ... (%d chars)" % len(text)
        return text

    def zz_load_where(name):
        """file:line of a statement name, or None if the script no longer has it."""
        if name is None or not renpy.game.script.has_label(name):
            return None
        node = renpy.game.script.lookup(name)
        return "%s:%d" % (node.filename, node.linenumber)

    def zz_load_inspect(slot):
        """Where the save was, read from its own rollback log before loading."""
        try:
            info = renpy.slot_json(slot) or {}
            ctime = info.get("_ctime")
            zz_load.game_version = info.get("_version")
            note("saved", "%s, game version %s, Ren'Py %s" % (
                time.strftime("%Y-%m-%d %H:%M", time.localtime(ctime)) if ctime else "?",
                info.get("_version", "?"), info.get("_renpy_version", "?")))
        except Exception as e:
            note("saved", "slot json unreadable: %r" % (e,))
        try:
            log_data, _sig = renpy.loadsave.location.load(slot)
            roots, log = renpy.loadsave.loads(log_data)
            entries = builtins.list(log.log)
            last = entries[-1].context.current if entries else None
            zz_load.saved_at = zz_load_where(last) or "(statement gone: %r)" % (last,)
            for rb in reversed(entries):
                w = zz_load_where(rb.context.current)
                if w:
                    zz_load.target = w
                    break
            else:
                zz_load.target = "(none: load_failed_label)"
            note("saved_at", zz_load.saved_at)
            note("rollback_target", zz_load.target)
            note("saved_store", "save_version=%s story_point=%s day=%s flags=%d" % (
                zz_load_fmt(roots.get("store.save_version", "<unset>")),
                zz_load_fmt(roots.get("store.story_point", "<unset>")),
                zz_load_fmt(roots.get("store.day", "<unset>")),
                len(roots.get("store.flags", ()) or ())))
        except Exception as e:
            note("saved_at", "could not read the save's log: %r" % (e,))

    def zz_load_label_cb(name, abnormal):
        if zz_load.armed and not zz_load.dumped and len(zz_load.labels) < 60:
            zz_load.labels.append(name)
            # load_failed() skips the after-load callbacks; load_recover runs
            # the migrations itself, after this.
            if name == "load_recover" and zz_load.mc_before is None:
                zz_load.mc_before = bool(renpy.showing("mc"))

    def zz_load_after_load_cb():
        # Inserted at index 0, so this runs ahead of the migrations.
        if zz_load.armed:
            zz_load.after_load = True
            zz_load.mc_before = bool(renpy.showing("mc"))

    def zz_load_dump():
        zz_load.dumped = True
        fn, ln = renpy.get_filename_line()
        landed = "%s:%d" % (fn, ln)
        recover = [l for l in zz_load.labels if l in ("load_recover", "return_recover")]
        saved = zz_load.saved_at
        if recover:
            status = "RECOVER " + recover[0]
        elif saved is None or saved.startswith("could not"):
            status = "UNKNOWN"
        elif saved.startswith("(statement gone"):
            # Rolled back to rollback_target; `landed` is the first stop after it.
            status = "EARLIER"
        elif landed == saved:
            status = "SAME"
        else:
            status = "MOVED"
        note("status", status)
        note("landed", landed)
        note("statement", zz_load_fmt(renpy.game.context().current))
        note("call_stack_depth", renpy.call_stack_depth())
        zz_load_dead_frames()
        note("after_load_callbacks", "ran" if zz_load.after_load else "did not run")
        note("recover_labels", ", ".join(recover) or "none")
        note("labels_after_load", ", ".join(zz_load.labels) or "none")
        note("showing mc before migrations", zz_load.mc_before)
        note("showing mc", bool(renpy.showing("mc")))
        for name in ZZ_LOAD_FIELDS:
            if hasattr(store, name):
                note("state." + name, zz_load_fmt(getattr(store, name)))
            else:
                note("state." + name, "<missing>")
        zz_load_report(landed, recover)
        check(True, "loads without an exception")

    def zz_load_get(fn, fallback="?"):
        """fn(), or a short "<error>" text: the report never raises."""
        try:
            v = fn()
        except Exception as e:
            return "<%s: %s>" % (type(e).__name__, " ".join(str(e).split())[:80])
        return fallback if v is None else v

    def zz_load_report(landed, recover):
        """The per-slot summary the load report shows (7 · WP11 task 5), as
        report.* notes. Every field is read defensively: a save the game can
        load but a helper can't read shows "<error>", never a failed run."""
        def version():
            return "save_version %s · game %s" % (getattr(store, "save_version", "?"),
                                                    zz_load.game_version or "?")

        def technique():
            t = getattr(store, "technique", None)
            n = getattr(store, "tname", None)
            return "%s (%s)" % (t, n) if n else str(t)

        def grade():
            return getattr(store, "grade", None) or "unassessed"

        def step():
            sp = getattr(store, "story_point", None)
            src = "story_point"
            if not sp:
                sp = legacy_story_point()
                src = "legacy"
            row = ""
            o = current_objective() if has_flag("settled_in") else None
            if o and o.get("mid"):
                row = " · %s (%s)" % (o["mid"], mission_status(o["mid"]))
            return "%s [%s]%s" % (sp, src, row)

        def objective():
            try:
                t = objective_text()
            except Exception:
                o = current_objective()
                t = o.get("text") if o else ""
            return t or "(none: before the campus opens)"

        def keepsakes():
            inv = getattr(store, "inventory", None) or {}
            ks = [ITEMS[i]["name"] for i in sorted(inv)
                  if i in ITEMS and ITEMS[i].get("kind") == "keepsake" and inv[i]]
            return ", ".join(ks) or "none"

        def where():
            if recover:
                return "%s -> %s" % (" -> ".join(recover), landed)
            return "statement %s" % landed

        note("report.version", zz_load_get(version))
        note("report.technique", zz_load_get(technique))
        note("report.grade", zz_load_get(grade))
        note("report.arc", zz_load_get(lambda: getattr(store, "arc", "?")))
        note("report.day", zz_load_get(lambda: "%s %s" % (store.day, store.period)))
        note("report.roster", zz_load_get(lambda: len(store.roster)))
        note("report.merit", zz_load_get(lambda: store.merit))
        note("report.story_step", zz_load_get(step))
        note("report.objective", zz_load_get(objective))
        note("report.keepsakes", zz_load_get(keepsakes))
        note("report.where", zz_load_get(where))

    def zz_load_dead_frames():
        """Call-stack frames whose return site is gone from the script. The
        load itself is fine; the `return` that pops down to such a frame lands
        in return_recover (D2), which the first stop after the load can't show.
        Notes them, and where return_recover would then send the save."""
        ctx = renpy.game.context()
        script = renpy.game.script
        dead = []
        for i, (rs, cl) in enumerate(builtins.zip(ctx.return_stack, ctx.call_location_stack)):
            if not script.has_label(rs) and not script.has_label(cl):
                dead.append("frame %d of %d: %r" % (i + 1, len(ctx.return_stack), rs))
        note("dead_return_sites", "; ".join(dead) or "none")
        if not dead:
            return
        try:
            if has_flag("settled_in"):
                where = "sandbox"
            else:
                point = store.story_point or legacy_story_point()
                where = "resume_story from %s, playing %s" % (point, ", ".join(prologue_plan(point)) or "nothing")
        except Exception as e:
            where = "could not work it out: %r" % (e,)
        note("on_dead_return", "return_recover -> " + where)

    def zz_load_done():
        zz_load.quit_at = None
        shot("landed")
        finish()

    def zz_load_interact_cb():
        # Only the main context counts: a yes/no prompt during the load runs
        # in a context of its own.
        if not zz_load.armed or len(renpy.game.contexts) != 1:
            return
        if zz_load.quit_at is not None:
            zz_load_done()
        elif not zz_load.dumped:
            zz_load_dump()
            zz_load.quit_at = time.time() + 1.0

    def zz_load_periodic_cb():
        if zz_load.quit_at is not None and time.time() >= zz_load.quit_at:
            zz_load_done()

    config.label_callbacks.append(zz_load_label_cb)
    config.after_load_callbacks.insert(0, zz_load_after_load_cb)
    config.start_interact_callbacks.append(zz_load_interact_cb)
    config.periodic_callbacks.append(zz_load_periodic_cb)


label zz_smoke:
    python:
        if not zz_load.slot:
            abort("SMOKE_SLOT is not set")
        note("slot", zz_load.slot)
        if not renpy.can_load(zz_load.slot):
            abort("no save in slot %s (run with SMOKE_SAVES=1)" % zz_load.slot)
        zz_load_inspect(zz_load.slot)
        zz_load.armed = True
        renpy.load(zz_load.slot)
    ## renpy.load only returns when the load was refused.
    $ abort("renpy.load returned without loading (the save token was refused?)")
