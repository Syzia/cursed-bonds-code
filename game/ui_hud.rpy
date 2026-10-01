################################################################################
## Cursed Bonds — the HUD, toasts and the objective toast.
##
## WP7 (PHASE1_DESIGN.md 3.10, 4.1–4.3).
##
##   sb_hud(on_map, person)   the date chip and three buttons (4.1)
##   toasts                   the overlay stack of rewards at the top right (4.2)
##   objective_toast(text)    "NEXT" and the new objective, top centre (4.3)
##
## The toast queue lives outside the saved store (D7): a builtins object made at
## init and never reassigned, so it is not saved and not rolled back. toast()
## (sb_hooks.rpy) reaches it through TOAST_SINK[0], and renpy.notify reaches it
## through config.notify.
################################################################################

init python:
    import builtins
    import time as _hud_time

    ## The date chip ------------------------------------------------------------

    _WEEKDAY_FULL = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday",
                     "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}

    if not hasattr(store, "weekday_full"):
        def weekday_full():
            """WP7. The full weekday name ("Monday"). 4.1 names this helper;
            it is defined here only if the world file doesn't have one."""
            return _WEEKDAY_FULL.get(weekday(), weekday())

    def hud_date():
        """WP7. "Day 9 · Monday" for the date chip; "Explore · Morning" in
        explore mode."""
        if store.explore_mode:
            return "Explore · %s" % store.period
        return "Day %d · %s" % (store.day, weekday_full())

    ## Toasts (3.10, 4.2) ---------------------------------------------------------

    TOAST_LIFE = 3.2        # seconds on screen once visible
    TOAST_FADE = 0.2        # slide in / fade out
    TOAST_VISIBLE = 4       # at most this many at once; the rest wait
    TOAST_VISIBLE_PERSON = 2    # over the person view, where the card is below

    def toast_limit():
        """WP7. How many toasts show at once: four, or two over the person
        view (the stack moves up beside MENU there, above the card), and
        none through the prologue's blackout, where they wait."""
        if getattr(store, "hide_side_images", False):
            return 0
        if renpy.get_screen("sb_char"):
            return TOAST_VISIBLE_PERSON
        return TOAST_VISIBLE

    ## kind -> (kanji, gui colour name). None means "the character's colour".
    TOAST_KINDS = {
        "bond":      (u"縁", None),
        "bond_rank": (u"縁", None),
        "aff":       (u"恋", "romance"),
        "stat":      (u"術", "violet"),
        "grade":     (u"級", "gold"),
        "mission":   (u"任", "seal"),
        "item":      (u"品", "gold"),
        "thread":    (u"糸", "dim"),
        "info":      (u"報", "dim"),
    }

    class ToastQueue(builtins.object):
        """WP7. The toast queue (D7): a builtins.list of builtins.dict items
        {text, kind, who, amount, t_shown}, oldest first. Made once at init;
        never saved, never rolled back."""

        def __init__(self):
            self.items = builtins.list()

    TOASTQ = ToastQueue()

    def _toast_text(kind, who, amount):
        name = CAST.get(who, {}).get("short", who or "")
        if kind == "aff":
            return u"%s  ♡ %+d" % (name, amount)
        return u"%s  bond %+d" % (name, amount)

    def _toast_reveal(now):
        """Starts the clock on every toast that has just become visible."""
        changed = False
        for t in TOASTQ.items[:toast_limit()]:
            if t["t_shown"] is None:
                t["t_shown"] = now
                changed = True
        return changed

    def _toast_trim_skipping():
        """While the player skips (Ctrl, or skip after choices), keep only the
        newest four: nobody reads a toast from three skipped days ago, and a
        backlog would otherwise trickle over the next screens for minutes.
        Outside skipping nothing is dropped (4.2). True if it dropped any."""
        items = TOASTQ.items
        if not config.skipping or len(items) <= TOAST_VISIBLE:
            return False
        del items[:len(items) - TOAST_VISIBLE]
        return True

    def toast_push(text, kind="info", who=None, amount=None):
        """WP7. Queue a toast for the `toasts` overlay (3.10). toast() calls
        this through TOAST_SINK[0]. Consecutive bond or affection gains for
        the same person merge into one toast (D34). While skipping, only the
        newest four are kept."""
        items = TOASTQ.items
        now = _hud_time.time()
        if items and kind in ("bond", "aff") and amount is not None:
            last = items[-1]
            if (last["kind"], last["who"]) == (kind, who) and last["amount"] is not None:
                last["amount"] += amount
                last["text"] = _toast_text(kind, who, last["amount"])
                if last["t_shown"] is not None:
                    ## The new total gets a full read, without replaying the
                    ## slide-in (the toast stays put at full alpha).
                    last["t_shown"] = now - TOAST_FADE
                renpy.restart_interaction()
                return
        items.append(builtins.dict(text=builtins.str(text),
                                   kind=(kind if kind in TOAST_KINDS else "info"),
                                   who=who, amount=amount, t_shown=None))
        _toast_trim_skipping()
        _toast_reveal(now)
        renpy.restart_interaction()

    def toast_tick():
        """WP7. The `toasts` screen's timer: drops expired toasts and shows
        the next ones waiting. Restarts the interaction only on a change."""
        now = _hud_time.time()
        items = TOASTQ.items
        ## A backlog queued before skipping began goes too, once it does.
        trimmed = _toast_trim_skipping()
        ## Toasts the current limit hides (the person view shows two) stop
        ## their clocks and wait, so none expires unseen (4.2).
        for t in items[toast_limit():]:
            t["t_shown"] = None
        keep = [t for t in items if t["t_shown"] is None or now - t["t_shown"] < TOAST_LIFE]
        changed = trimmed or len(keep) != len(items)
        if changed:
            items[:] = keep
        if _toast_reveal(now) or changed:
            renpy.restart_interaction()

    def toast_visible():
        """WP7. The toasts on screen now, oldest (top) first."""
        return [t for t in TOASTQ.items[:toast_limit()] if t["t_shown"] is not None]

    def toast_clear():
        """WP7. Empties the queue (after a load, so an old stack doesn't linger)."""
        del TOASTQ.items[:]

    def toast_style(t):
        """WP7. (kanji, colour) for a queued toast."""
        k, col = TOAST_KINDS.get(t["kind"], TOAST_KINDS["info"])
        who = t["who"]
        if col is None or (t["kind"] == "grade" and who in CAST):
            ## Bond toasts, and someone else's promotion, wear that person's
            ## colour (3.4, 3.10).
            return k, CAST.get(who, {}).get("color", gui.dim)
        return k, getattr(gui, col)

    def _toast_fx_fn(t):
        def fn(trans, st, at):
            shown = t["t_shown"]
            age = (_hud_time.time() - shown) if shown is not None else 0.0
            a_in = min(1.0, max(0.0, age / TOAST_FADE))
            a_out = min(1.0, max(0.0, (TOAST_LIFE - age) / TOAST_FADE))
            trans.alpha = min(a_in, a_out)
            trans.xoffset = int(40 * (1.0 - a_in))
            if age < TOAST_FADE or age > TOAST_LIFE - TOAST_FADE:
                return 0
            return max(0.0, TOAST_LIFE - TOAST_FADE - age)
        return fn

    def toast_fx(t):
        """WP7. The slide-in and fade-out of one toast, timed by the wall
        clock from when it became visible, so a screen refresh never restarts
        it."""
        return Transform(function=_toast_fx_fn(t))

    import re as _hud_re

    _NOTIFY_STAT = _hud_re.compile(u"^((Control|Output|Insight) \\+\\d+|Technique advanced\\b)")

    def notify_kind(m):
        """WP7. The toast kind for a renpy.notify message: thread news
        (sb_threads) wears 糸, stat gains and technique tiers (gain()) wear
        術, anything else is 'info'."""
        m = builtins.str(m)
        if m.startswith(u"New thread") or m.endswith(u"— advanced"):
            return "thread"
        if _NOTIFY_STAT.match(m):
            return "stat"
        return "info"

    TOAST_SINK[0] = toast_push
    config.notify = lambda m: toast(m, notify_kind(m))
    config.overlay_screens.append("toasts")
    config.after_load_callbacks.append(toast_clear)

    ## The objective toast (3.10, 4.3) ---------------------------------------------

    OBJECTIVE_IN, OBJECTIVE_HOLD, OBJECTIVE_OUT = 0.3, 4.5, 0.5

    ## [shown at (wall clock), delay before it slides in]. A builtins list made
    ## at init and never reassigned: not saved, not rolled back.
    OBJ_SHOWN = builtins.list([0.0, 0.0])
    ## The objective text that was taken off screen before anyone could read
    ## it (the player left the place view during its delay); shown again.
    OBJ_UNSEEN = builtins.list([None])
    OBJ_SEEN_AFTER = 1.0    # on screen this long (after its delay) counts as read

    def objective_delay():
        """WP7. How long objective_toast waits before sliding in: until the
        arrival caption for the current (day, period, here) has faded, so the
        two never cover each other (4.3). Records when it was shown."""
        if renpy.predicting():
            return 0.0
        now = _hud_time.time()
        d = 0.0
        key = (store.day, store.period, store.here)
        if ARRIVAL[0] == key:
            d = max(0.0, ARRIVAL[1] + ARRIVAL_IN + ARRIVAL_HOLD + ARRIVAL_OUT - now)
        OBJ_SHOWN[0] = now
        OBJ_SHOWN[1] = d
        return d

    def check_objective():
        """WP7. Called by the loop before the place view: if objective_text()
        changed since last_objective, slide in objective_toast and remember
        the new text. last_objective starts as None, so it shows once after
        loading an old save. Skipped in explore mode. The toast waits for the
        arrival caption to fade (objective_delay)."""
        if store.explore_mode:
            return
        txt = objective_text() or ""
        if txt == getattr(store, "last_objective", None) and OBJ_UNSEEN[0] != txt:
            return
        store.last_objective = txt
        OBJ_UNSEEN[0] = None
        if txt:
            ## Start the arrival caption's clock now (the place view is next),
            ## so the toast's delay can be read from it.
            arrival_caption()
            objective_delay()
            renpy.show_screen("objective_toast", txt)

    def _objective_after_load():
        ## A load counts the objective as unread: the place view shows it
        ## again, even if a toast that was still waiting got saved away.
        OBJ_UNSEEN[0] = getattr(store, "last_objective", None)

    config.after_load_callbacks.append(_objective_after_load)

    def objective_leave():
        """WP7. Called by the loop as it leaves the place view: takes the
        objective toast down so it never sits over the person view or the
        map. If it hadn't been up long enough to read, it shows again the
        next time the place view does."""
        if not renpy.get_screen("objective_toast"):
            return
        up = _hud_time.time() - (OBJ_SHOWN[0] + OBJ_SHOWN[1])
        if up < OBJ_SEEN_AFTER:
            OBJ_UNSEEN[0] = getattr(store, "last_objective", None)
        renpy.hide_screen("objective_toast")


## HUD styles ###################################################################

style sb_place_text is text:
    font gui.display_font
    color gui.paper
    size 30

style sb_hud_button is button:
    padding (6, 4)

style sb_hud_button_text is text:
    font gui.body_medium_font
    color gui.dim
    hover_color gui.paper
    selected_color gui.violet2
    size 17
    kerning gui.track

style sb_hud_nav_button is jjk_button:
    xfill False
    xysize (148, 52)
    padding (0, 0)

style sb_hud_nav_button_text is jjk_button_text:
    xalign 0.5
    yalign 0.5
    size 19
    kerning gui.track


## The period tracker: five diamonds, one per period. ##########################
## (No longer on the HUD; kept for anything that still wants it.)

screen period_pips():
    $ _pi = period_index()
    hbox:
        spacing 5
        yalign 0.5
        for _i, _p in enumerate(PERIODS):
            if _i < _pi:
                add "gui/pip_past.png" yalign 0.5
            elif _i == _pi:
                add "gui/pip_on.png" yalign 0.5
            else:
                add "gui/pip_off.png" yalign 0.5


## HUD (4.1) ####################################################################
##
## The date, and three buttons: MAP and JOURNAL in the place view, MENU always.
## The map (on_map) and the person view (person) show the date and MENU.
## The time of day is in the picture; grade, energy and health are in the
## journal's Stats tab and in combat.

screen sb_hud(on_map=False, person=False):

    $ _place_view = not on_map and not person
    $ _date = hud_date()

    frame:
        pos (40, 26)
        background Frame("gui/panel_ghost.png", 4, 4)
        padding (22, 8)
        text "[_date]":
            font gui.display_font
            color gui.paper
            size 28

    hbox:
        xalign 1.0
        xoffset -40
        ypos 26
        spacing 10
        style_prefix "sb_hud_nav"
        if _place_view:
            textbutton _("MAP") action Return(("map",))
            textbutton _("JOURNAL") action Return(("journal", "people"))
        textbutton _("MENU") action ShowMenu()

    if _place_view:
        key "m" action Return(("map",))
        key "j" action Return(("journal", "people"))

        ## Review tools (D30): developer builds only.
        if config.developer:
            textbutton _("Review tools"):
                pos (40, 1040)
                padding (0, 0)
                background None
                text_style "jjk_label"
                text_hover_color gui.paper
                action Return(("dev",))


## Toasts (4.2) #################################################################
##
## Top right, newest at the bottom, four at a time; the rest wait their turn.
## An overlay screen, so it is up during scenes as well as on campus.

screen toasts():
    zorder 150

    ## Through the prologue's blackout (hide_side_images) toast_limit() is 0:
    ## nothing draws, and the timer keeps every toast's clock stopped, so they
    ## all wait and get their full turn after it (4.2).
    if not _in_replay and TOASTQ.items:

        timer 0.1 repeat True action Function(toast_tick, _update_screens=False)

        ## Over the person view the stack sits beside MENU, above the card.
        $ _over_card = bool(renpy.get_screen("sb_char"))
        vbox:
            xpos (1722 if _over_card else 1880)
            xanchor 1.0
            ypos (26 if _over_card else 92)
            spacing 8

            for _t in toast_visible():
                $ _k, _col = toast_style(_t)
                $ _txt = _t["text"]
                frame at toast_fx(_t):
                    background Solid("#0d0b14e8")
                    foreground Transform(Solid(_col), xsize=6)
                    padding (18, 8, 16, 8)
                    xsize 460
                    yminimum 56
                    hbox:
                        spacing 12
                        yalign 0.5
                        fixed:
                            xysize (36, 36)
                            yalign 0.5
                            add "gui/seal_44.png" zoom (36.0 / 44.0)
                            text _k:
                                font gui.display_heavy_font
                                color _col
                                size 21
                                xalign 0.5
                                yalign 0.5
                        text _txt:
                            substitute False
                            font gui.body_medium_font
                            color gui.paper
                            size 20
                            yalign 0.5
                            xmaximum 378


## Objective toast (4.3) #########################################################

transform objective_slide(d=0.0):
    on show:
        yoffset -40 alpha 0.0
        pause d
        easein OBJECTIVE_IN yoffset 0 alpha 1.0
        pause OBJECTIVE_HOLD
        linear OBJECTIVE_OUT alpha 0.0
    on hide:
        linear 0.2 alpha 0.0

screen objective_toast(text):
    zorder 140

    ## Wait for the arrival caption to fade (4.3; they share the top left).
    default _od = objective_delay()

    frame at objective_slide(_od):
        xalign 0.5
        ypos 96
        xsize 900
        background Solid("#0d0b14ee")
        padding (0, 0)
        vbox:
            xfill True
            add Solid(gui.gold) xysize (900, 2)
            frame:
                background None
                xfill True
                padding (28, 14)
                vbox:
                    spacing 4
                    text _("NEXT") style "jjk_label" color gui.gold
                    text text:
                        substitute False
                        font gui.display_font
                        color gui.paper
                        size 26
                        xmaximum 844

    timer (_od + OBJECTIVE_IN + OBJECTIVE_HOLD + OBJECTIVE_OUT) action Hide("objective_toast")
