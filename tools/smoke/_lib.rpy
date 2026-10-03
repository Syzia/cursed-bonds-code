## tools/smoke/_lib.rpy -- the smoke-test library (docs/PHASE1_DESIGN.md, 8.2;
## docs/PHASE2_DESIGN.md 2.2 R5 and R6, section 8).
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
##                                 variable becomes a set). It raises
##                                 ZZFixtureError, which fails the run, for a
##                                 name the store doesn't have (a typo), and for
##                                 a shaped variable (ZZ_SHAPED: board_offers,
##                                 inventory, npc_state ...): build those with
##                                 their owner's functions (board_generate(),
##                                 give_item(), promote() ...), so a harness
##                                 never invents a record's shape (R5).
##   settle(**kw)                  fixture(**kw), then a post-prologue state:
##                                 flag settled_in, roll_gojo(), ensure_state()
##   smoke_env(name, default=None) reads an environment variable (SMOKE_SLOT...)
##
## Measuring helpers (phase 2). Each renders first when called from script (a
## short hard pause), so it sees the screens as they are now. They work over a
## modal screen too (their waits, and shot()'s, are not held by one):
##   zz_render(seconds=0.15)       one real interaction, skipping suspended
##   zz_rect(screen, wid)          (x, y, w, h) of the button with `id wid` on
##                                 a shown screen, from the focus list of the
##                                 last frame; None if it isn't there. Buttons
##                                 only: a plain frame has no rectangle here.
##   zz_buttons(screen)            how many focusable widgets the screen holds
##                                 (the screens it `use`s included)
##   zz_words(screen)              the tokens that contain a letter, from every
##                                 Text in the screen's tree whose style is not
##                                 icon_glyph (a stand-in icon's kanji). Text
##                                 tags are stripped; "+2" and "◆ 1" are not
##                                 words. It counts what is in the tree, drawn
##                                 see-through or not.
##   zz_texts(screen)              every Text's string in the screen's tree
##   zz_calls(fn_name, seconds)    wraps the store function of that name, runs
##                                 an interaction for that long by the wall
##                                 clock, and returns how often it was called.
##                                 It counts calls made through the store name;
##                                 a transform that already holds the function
##                                 itself is not seen.
##   zz_layer_tags(layer)          the set of tags showing on a layer
##   zz_worst(screen, *args, hover=None, name=None)
##                                 the worst case for a full screen (R6): four
##                                 toasts queued, the objective banner up,
##                                 skipping on, `screen` shown with *args, and
##                                 (hover=) the button with that id focused;
##                                 saves worst_<screen>.png (or <name>.png).
##                                 The screen stays up for measuring; the
##                                 banner and the skipping are put back.
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
                ## modal=False: a modal screen must not hold the wait open
                ## (config.modal_blocks_pause is True by default).
                renpy.pause(wait, hard=True, modal=False)
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

    ## Variables whose records have a shape their owner defines (R5). A
    ## harness builds them with the owner's functions: board_generate(),
    ## board_take(), give_item(), promote(), start_mission / the mission API,
    ## the combat labels, night_set_cost(), market_buy(), cards_new(),
    ## fish_land(), pc_request(). To empty one, assign the empty value directly
    ## (`store.inventory = {}`): an empty container has no shape to get wrong.
    ZZ_SHAPED = ("board_offers", "board_log", "npc_state", "inventory", "mission_state", "cb",
                 "cards_state", "fish_state", "fish_log", "pc_requests")

    class ZZFixtureError(Exception):
        """fixture() was asked for a name the store doesn't have, or for a
        shaped variable."""

    def fixture(**kw):
        """Set store variables, e.g. fixture(day=4, here="dojo", flags={"roll_call"}).
        A list or tuple given for a variable that holds a set becomes a set.
        Raises ZZFixtureError, setting nothing, for a name the store doesn't
        have (a typo) and for a shaped variable (ZZ_SHAPED, R5)."""
        shaped = [k for k in sorted(kw) if k in ZZ_SHAPED]
        if shaped:
            raise ZZFixtureError("fixture(): %s %s shaped; build %s with the owner's functions "
                                 "(see ZZ_SHAPED in tools/smoke/_lib.rpy)" % (
                                     ", ".join(shaped), "is" if len(shaped) == 1 else "are",
                                     "it" if len(shaped) == 1 else "them"))
        unknown = [k for k in sorted(kw) if not hasattr(store, k)]
        if unknown:
            raise ZZFixtureError("fixture(): the store has no variable named %s" % ", ".join(unknown))
        for k, v in sorted(kw.items()):
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

    ## Measuring helpers (phase 2) -------------------------------------------------

    import re as zz_re
    import unicodedata as zz_unicodedata

    ZZ_TEXT_TAG = zz_re.compile(r"\{[^{}]*\}")

    def zz_render(seconds=0.15):
        """One real interaction of `seconds`, with skipping and autoplay
        suspended, so every shown screen is built and drawn. Inside an
        interaction (a screen action, a callback) it does nothing."""
        ctx = renpy.game.context()
        if ctx.init_phase or ctx.interacting:
            return
        skipping, auto = config.skipping, zz_smoke_state.autoplay
        config.skipping = None
        zz_smoke_state.autoplay = False
        try:
            ## modal=False: over a modal screen (pc_screen, fish_screen, the
            ## review panel) a timed pause would otherwise never end.
            renpy.pause(seconds, hard=True, modal=False)
        finally:
            config.skipping, zz_smoke_state.autoplay = skipping, auto

    def zz_rect(screen, wid):
        """(x, y, w, h), as ints, of the button with `id wid` on a shown
        screen, read from the focus list after a render. None when the screen
        or the id isn't there, or the widget can't take focus (buttons only)."""
        zz_render()
        if renpy.get_screen(screen) is None:
            return None
        want = [renpy.get_displayable(screen, wid, base=True), renpy.get_displayable(screen, wid)]
        want = [w for w in want if w is not None]
        if not want:
            return None
        for f in renpy.display.focus.focus_list:
            if f.x is not None and any(f.widget is w for w in want):
                return (int(round(f.x)), int(round(f.y)), int(round(f.w)), int(round(f.h)))
        return None

    def zz_buttons(screen):
        """How many focusable widgets a shown screen holds, the screens it
        `use`s included, after a render."""
        zz_render()
        sc = renpy.get_screen(screen)
        if sc is None:
            return 0
        seen = builtins.set()
        for f in renpy.display.focus.focus_list:
            if f.screen is sc and f.widget is not None and f.x is not None:
                seen.add(id(f.widget))
        return len(seen)

    def zz_text_nodes(screen):
        """Every Text displayable in a shown screen's tree."""
        out = builtins.list()
        sc = renpy.get_screen(screen)
        if sc is None:
            return out

        def each(d):
            if isinstance(d, renpy.text.text.Text):
                out.append(d)

        sc.visit_all(each)
        return out

    def zz_text_string(d):
        try:
            return d.get_all_text()
        except Exception:
            return " ".join(x for x in (d.text or []) if isinstance(x, str))

    def zz_is_glyph(d):
        """True for a Text drawn in the style icon_glyph (a stand-in icon's
        kanji), or in a style that inherits from it."""
        name = getattr(d.style, "parent", None)
        for _i in range(8):
            if not name:
                return False
            if name[-1] == "icon_glyph":
                return True
            try:
                name = getattr(store.style, name[-1]).parent
            except Exception:
                return False
        return False

    def zz_is_word(tok):
        for ch in tok:
            if ch.isalpha() and zz_unicodedata.name(ch, "").startswith("LATIN"):
                return True
        return False

    def zz_texts(screen):
        """The string of every Text in a shown screen's tree (to assert that
        a line is there, or gone)."""
        zz_render()
        return [zz_text_string(d) for d in zz_text_nodes(screen)]

    def zz_words(screen):
        """The tokens that contain a letter, from every Text in a shown
        screen's tree whose style is not icon_glyph. len() of it is the
        screen's word count for the clutter budget (4.0)."""
        zz_render()
        out = builtins.list()
        for d in zz_text_nodes(screen):
            if zz_is_glyph(d):
                continue
            plain = ZZ_TEXT_TAG.sub(" ", zz_text_string(d).replace("{{", " "))
            out.extend(t for t in plain.split() if zz_is_word(t))
        return out

    def zz_calls(fn_name, seconds):
        """How many times the store function `fn_name` is called while an
        interaction runs for `seconds` by the wall clock. The function is
        wrapped under its store name for that span and then put back."""
        orig = getattr(store, fn_name)
        count = builtins.list([0])

        def zz_counting(*args, **kwargs):
            count[0] += 1
            return orig(*args, **kwargs)

        setattr(store, fn_name, zz_counting)
        try:
            t_end = time.time() + seconds
            zz_render(seconds)
            ## A pause can end early; keep rendering until the span is over.
            while time.time() < t_end - 0.01:
                zz_render(builtins.max(0.02, t_end - time.time()))
        finally:
            setattr(store, fn_name, orig)
        return count[0]

    def zz_layer_tags(layer="master"):
        """The set of tags showing on a layer."""
        return builtins.set(renpy.get_showing_tags(layer))

    def zz_worst(screen, *args, **kwargs):
        """The worst case for a full screen (R6): four toasts queued, the
        objective banner up, skipping on, `screen` shown with *args and, with
        hover=<id>, that button focused. Saves worst_<screen>.png (name= for
        another file name) and returns True if it was written. `screen` stays
        shown, for measuring; the banner, the indicator and the skipping are
        put back, and the toasts are cleared."""
        hover = kwargs.pop("hover", None)
        name = kwargs.pop("name", None) or ("worst_" + screen)
        skipping, auto = config.skipping, zz_smoke_state.autoplay
        toast_clear()
        for i, (kind, who) in enumerate((("grade", None), ("bond", "yuji"), ("item", None), ("stat", None))):
            toast("Worst case %d: a reward line long enough to wrap onto a second line" % (i + 1), kind, who)
        renpy.show_screen("objective_toast", "Worst case: an objective long enough to fill the banner from edge to edge")
        renpy.show_screen(screen, *args, **kwargs)
        ## Let the banner slide in and the toasts fade in before skipping starts.
        zz_render(0.7)
        if hover is not None:
            renpy.set_focus(screen, hover)
        zz_smoke_state.autoplay = False
        config.skipping = "slow"
        try:
            ## A bare timed interaction: a pause statement would be dismissed
            ## by the skipping before a frame with the indicator was drawn.
            renpy.ui.pausebehavior(0.4, False, modal=False)
            renpy.ui.interact(mouse="pause", type="pause", roll_forward=None)
            ok = shot(name, wait=0)
        finally:
            config.skipping, zz_smoke_state.autoplay = skipping, auto
            renpy.hide_screen("objective_toast")
            if not config.skipping:
                renpy.hide_screen("skip_indicator")
            toast_clear()
        return ok

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
