## tools/smoke/_lib.rpy -- the smoke-test library (docs/PHASE1_DESIGN.md, 8.2).
##
## tools/smoke.sh installs this file as game/zz_smoke_lib.rpy and the harness
## as game/zz_smoke.rpy, in a scratch copy of the project. Never copy either
## into the real game/ folder.
##
## A harness is one file that defines `label zz_smoke`. The splash screen and
## the main menu are skipped, and "start" leads to zz_smoke, so the harness runs
## as soon as the game boots, in the main context, like a new game would:
##
##     label zz_smoke:
##         $ settle(day=3)                       # a post-prologue save
##         $ check(has_flag("settled_in"), "settled")
##         show screen sb_place
##         $ shot("place")                       # shots/<harness>/place.png
##         $ finish()                            # writes result.txt and quits
##
## What the library gives a harness:
##   check(cond, name, detail="")  records "PASS name" or "FAIL name: detail";
##                                 returns bool(cond)
##   note(name, detail="")         records "NOTE name: detail" (no verdict)
##   shot(name, wait=0.25)         saves $SMOKE_SHOTS/<name>.png. Outside an
##                                 interaction it first pauses `wait` seconds
##                                 (skipping suspended) so the frame is drawn.
##   finish()                      writes result.txt, ending "RESULT PASS" when
##                                 nothing failed, else "RESULT FAIL", and quits
##   abort(detail)                 records "FAIL abort: detail" and finishes
##   autoplay(on=True)             sets smoke_autoplay, auto-picks menu choices
##                                 after 0.05 s and fast-skips all text
##   fixture(**kw)                 sets store variables (a list given for a set
##                                 variable becomes a set)
##   settle(**kw)                  fixture(**kw), then a post-prologue state:
##                                 flag settled_in, roll_gojo(), ensure_state()
##   smoke_env(name, default=None) reads an environment variable (SMOKE_SLOT...)
##
## An uncaught exception anywhere in the script is caught by
## config.exception_handler: it records the traceback, writes RESULT FAIL and
## quits. A harness that returns without calling finish() fails as well.
##
## A harness never waits for input: a real window is open, and a stray click
## or key can end a plain renpy.pause() or say line at any moment. Use
## autoplay() to play script through, call the loop's functions directly, and
## use renpy.pause(n, hard=True) when a wait is really needed.
##
## This file's init runs at 999, after the game's own init code. A harness's
## own `init 999 python` block runs just before it (zz_smoke.rpy sorts before
## zz_smoke_lib.rpy, and lint rejects priorities above 999), so it may define
## functions and callbacks that use these helpers, but not call them at init.

init 999 python:
    import builtins
    import os
    import time

    class ZZSmokeState(builtins.object):
        """Harness state. A builtins.object holding builtins containers, made
        at init and never reassigned, so rollback, loading a save and
        full_restart all leave it alone, and it never goes into a save."""

        def __init__(self):
            self.lines = builtins.list()
            self.failed = False
            self.finished = False
            self.entered = False
            self.autoplay = False
            self.shots = os.environ.get("SMOKE_SHOTS") or os.path.join(config.basedir, "shots")
            self.harness = os.environ.get("SMOKE_HARNESS", "harness")
            self.t0 = time.time()

    zz_smoke_state = ZZSmokeState()

    def zz_smoke_one_line(v):
        return " ".join(str(v).split())

    def smoke_env(name, default=None):
        """The value of environment variable `name` (SMOKE_SLOT and friends)."""
        return os.environ.get(name, default)

    def check(cond, name, detail=""):
        """Record `PASS name` or `FAIL name: detail`. Returns bool(cond)."""
        ok = bool(cond)
        if ok:
            zz_smoke_state.lines.append("PASS " + zz_smoke_one_line(name))
        else:
            zz_smoke_state.failed = True
            line = "FAIL " + zz_smoke_one_line(name)
            if detail:
                line += ": " + zz_smoke_one_line(detail)
            zz_smoke_state.lines.append(line)
        return ok

    def note(name, detail=""):
        """Record an informational `NOTE name: detail` line. It never fails a run."""
        line = "NOTE " + zz_smoke_one_line(name)
        if detail != "":
            line += ": " + zz_smoke_one_line(detail)
        zz_smoke_state.lines.append(line)

    def shot(name, wait=0.25):
        """Save a screenshot as $SMOKE_SHOTS/<name>.png. Outside an interaction
        it pauses first (with skipping suspended) so what the script just
        showed is on screen. Inside one (a screen action or a callback) it
        captures the last frame drawn."""
        fn = os.path.join(zz_smoke_state.shots, str(name) + ".png")
        ctx = renpy.game.context()
        if wait and not ctx.init_phase and not ctx.interacting:
            skipping, auto = config.skipping, zz_smoke_state.autoplay
            config.skipping = None
            zz_smoke_state.autoplay = False
            try:
                renpy.pause(wait, hard=True)
            finally:
                config.skipping, zz_smoke_state.autoplay = skipping, auto
        try:
            if not os.path.isdir(zz_smoke_state.shots):
                os.makedirs(zz_smoke_state.shots)
            ok = renpy.screenshot(fn)
        except Exception as e:
            ok = False
            note("shot " + str(name), "screenshot failed: %r" % (e,))
            return False
        if not ok:
            note("shot " + str(name), "screenshot failed")
        return ok

    def zz_smoke_write(extra=()):
        st = zz_smoke_state
        path = os.path.join(st.shots, "result.txt")
        lines = builtins.list(st.lines) + builtins.list(extra)
        verdict = "RESULT FAIL" if (st.failed or any(l.startswith("FAIL") for l in lines)) else "RESULT PASS"
        header = "# %s · %.1f s · Ren'Py %s" % (st.harness, time.time() - st.t0, renpy.version_only)
        if not os.path.isdir(st.shots):
            os.makedirs(st.shots)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join([header] + lines + [verdict]) + "\n")
        os.replace(tmp, path)
        return verdict

    def finish():
        """Write result.txt (ending RESULT PASS or RESULT FAIL) and quit."""
        st = zz_smoke_state
        if not st.finished:
            st.finished = True
            verdict = zz_smoke_write()
        else:
            verdict = "RESULT FAIL" if st.failed else "RESULT PASS"
        renpy.quit(status=0 if verdict == "RESULT PASS" else 1)

    def abort(detail):
        """Fail the run now with `detail`, and quit."""
        check(False, "abort", detail)
        finish()

    def zz_smoke_exception(te):
        """config.exception_handler: record the traceback, fail, quit."""
        st = zz_smoke_state
        if st.finished:
            # Something broke after the result was written: just leave.
            renpy.quit(status=1)
        try:
            text = te.simple or te.full or str(te)
        except Exception:
            text = repr(te)
        st.failed = True
        st.lines.append("FAIL exception: uncaught exception (traceback follows)")
        for l in str(text).rstrip().splitlines():
            st.lines.append("    " + l)
        st.finished = True
        try:
            zz_smoke_write()
        finally:
            renpy.quit(status=1)
        return True

    config.exception_handler = zz_smoke_exception

    def autoplay(on=True):
        """Play through script unattended: store.smoke_autoplay, menus picked
        at random after 0.05 s, all text fast-skipped (seen or not, and on
        after choices). autoplay(False) turns it back off.

        Ren'Py's "fast" skipping ends at the next menu (ui.interact resets
        it), so while autoplay is on a start-interaction callback turns it
        back on for every interaction. Screens a harness calls still wait
        for their own input; renpy.input is skipped by the smoke_autoplay
        guard in the prologue (WP9)."""
        on = bool(on)
        zz_smoke_state.autoplay = on
        store.smoke_autoplay = on
        _preferences.skip_unseen = on
        _preferences.skip_after_choices = on
        config.auto_choice_delay = 0.05 if on else None
        config.skipping = "fast" if on else None

    def zz_smoke_autoplay_cb():
        if zz_smoke_state.autoplay and config.skipping != "fast":
            config.skipping = "fast"

    config.start_interact_callbacks.append(zz_smoke_autoplay_cb)

    def fixture(**kw):
        """Set store variables, e.g. fixture(day=4, here="dojo", flags={"roll_call"}).
        A list or tuple given for a variable that holds a set becomes a set.
        A name the store doesn't have yet is set anyway, with a NOTE (typo guard)."""
        for k, v in sorted(kw.items()):
            if not hasattr(store, k):
                note("fixture", "new store variable " + k)
            else:
                cur = getattr(store, k)
                if isinstance(cur, (set, frozenset)) and isinstance(v, (list, tuple)):
                    v = set(v)
            setattr(store, k, v)

    def settle(**kw):
        """A post-prologue state: fixture(**kw), flag settled_in, roll_gojo(),
        then ensure_state() (looked up when called, from sb_hooks.rpy)."""
        fixture(**kw)
        flag("settled_in")
        roll_gojo()
        fn = getattr(store, "ensure_state", None)
        if fn is None:
            note("settle", "ensure_state() is not defined yet; skipped")
        else:
            fn()

    ## Boot straight into the harness.
    config.label_overrides["splashscreen"] = "zz_skip"
    config.label_overrides["start"] = "zz_smoke"

    ## Quiet, quick and self-contained. These defaults apply because the
    ## scratch savedir starts with fresh preferences.
    config.window_title = "SMOKE: " + zz_smoke_state.harness
    config.default_music_volume = 0.0
    config.default_sfx_volume = 0.0
    config.default_voice_volume = 0.0
    config.default_text_cps = 0
    config.default_fullscreen = False
    config.has_autosave = False
    config.autosave_on_quit = False


## The main menu returns at once, so Ren'Py jumps to "start", that is, to
## zz_smoke. Arriving here a second time means the harness returned.
label main_menu:
    if zz_smoke_state.entered:
        $ abort("the harness returned without calling finish()")
    $ zz_smoke_state.entered = True
    return

label zz_skip:
    return
