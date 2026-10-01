################################################################################
## Explore the campus: a look-around mode, on the main menu when run from the SDK (config.developer).
##
## Drops straight into free roam at the courtyard for judging locations and
## backgrounds. No story beats fire, every door is open, and a Time button
## steps through the day without spending it on anything. The people on
## campus still follow their schedules, so each time of day shows who would
## be where.
################################################################################

default explore_mode = False

init python:

    def explore_next_period():
        i = PERIODS.index(store.period)
        store.period = PERIODS[(i + 1) % len(PERIODS)]


label explore_campus:

    $ explore_mode = True
    $ day = 1
    $ period = "Morning"
    $ here = "courtyard"
    $ roll_gojo()
    $ flag("settled_in")
    $ ensure_state()

    scene expression graded_bg() with fade_slow
    call sandbox
    return


label sb_do_explore_time:

    $ explore_next_period()
    scene expression graded_bg()
    with Dissolve(0.4)
    return


## Review tools (4.13, D30) #####################################################
##
## WP11. A developer-only panel (config.developer: the game run from the SDK)
## for jumping ahead without playing hours. The place view's small "Review
## tools" button, bottom left, returns ("dev",); the loop calls dev_tools, which
## calls the panel in the main context, so everything it changes sticks and is
## saved with the game.
##
## Each button runs one dev_* function, and the function toasts what it did.
## "Finish the next story step" and "Recruit Utahime" play their scenes through
## start_mission (a scene sets the flags later steps need, so a step is never
## just marked done), then come back to the place view.
##
## Arc Two: "Mark the main story complete" sets dev_story_complete, which
## main_story_complete() honours in a developer build. The campus journal's
## Missions tab then offers "Begin Arc Two", and arc_two_start asks first.
##
## Explore mode never fires a mission: the two scene buttons are off there.
## Nothing here is saved state: the functions live at init, and the labels
## keep no variables of their own.

init python:

    DEV_STUDENTS = ("yuji", "megumi", "nobara")

    ## The buttons, in the panel's order (three columns).
    DEV_BUTTONS = [
        ("merit", "+50 merit"),
        ("mc", "Promote me one grade"),
        ("story", "Finish the next story step"),
        ("yuji", "Promote Yuji one grade"),
        ("megumi", "Promote Megumi one grade"),
        ("nobara", "Promote Nobara one grade"),
        ("bond", "+20 bond with everyone"),
        ("tokyo", "Open Tokyo"),
        ("gojo", "Gojo in today"),
        ("utahime", "Recruit Utahime"),
        ("items", "Grant one of every item"),
        ("armory", "Open the armory"),
        ("complete", "Mark the main story complete"),
        ("week", "Jump to day +7"),
        ("veil", "The ridge veil, again today"),
        ## Phase 2 (4.16, D50): the rare states, for checkpoints B and C.
        ("night", "Jump to Night"),
        ("gojo_night", "Gojo night tonight"),
        ("rest", "Tomorrow is a rest day"),
        ("yen", "+¥20,000"),
        ("market", "Find the Black Market"),
        ("sample", "Style sample"),
    ]

    ## The buttons that play a scene (or, for "sample", open a screen): the
    ## panel returns their key to dev_tools.
    DEV_SCENES = ("story", "utahime", "sample")

    ## The scene buttons that never fire the story, so explore mode keeps them.
    DEV_EXPLORE_OK = ("sample",)

    ## A button's `when`: the NAME of a store function; the panel leaves the
    ## button out while it returns False (its feature isn't built yet).
    DEV_WHEN = dict(gojo_night="night_exists", rest="night_exists", market="market_exists")

    def _dev_short(text, n=90):
        text = text or ""
        return text if len(text) <= n else text[:n - 1].rstrip() + "…"

    def _dev_next_grade(cur):
        """The grade one step above cur (a key, a legacy int or None; None
        becomes Grade 4), or None at Grade 1 and above: Special Grade is off
        the scale, and nobody reaches it in Arc One."""
        k = grade_key(cur)
        if k is None:
            return "g4"
        i = GRADE_ORDER.index(k) + 1
        if i >= len(GRADE_ORDER) or GRADES[GRADE_ORDER[i]]["off_scale"]:
            return None
        return GRADE_ORDER[i]

    def _dev_grade_of(who):
        return store.grade if who == "mc" else _npc_grade(who)

    def _dev_after():
        ## Statuses depend on flags, grades and the day: recompute them now.
        mission_cache_clear()
        renpy.restart_interaction()

    ## The buttons ----------------------------------------------------------------

    def dev_merit():
        """WP11. +50 merit (toasted by add_merit)."""
        add_merit(50, "Review tools")
        _dev_after()

    def dev_promote(who):
        """WP11. Promote me ("mc") or a first-year one grade, up to Grade 1."""
        cur = _dev_grade_of(who)
        nxt = _dev_next_grade(cur)
        tag = None if who == "mc" else who
        name = "Me" if who == "mc" else _who_name(who)
        if nxt is None:
            toast("%s: already %s, as high as Arc One goes." % (name, grade_label(cur)), "grade", tag)
        elif not promote(who, nxt, "Review tools"):
            toast("%s: still %s." % (name, grade_label(cur)), "grade", tag)
        _dev_after()

    def dev_bond():
        """WP11. +20 bond with everyone on my roster, in one toast."""
        n = 0
        for who in list(store.roster):
            if who in CAST:
                add_bond(who, 20, quiet=True)
                n += 1
        toast("Bond +20 with everyone I know (%d)." % n, "bond", None, 20)
        _dev_after()

    def dev_tokyo():
        """WP11. Open Tokyo: the ride-along's flag, ijichi_rides."""
        if tokyo_open():
            toast("Tokyo is already open.", "info", "ijichi")
        else:
            flag("ijichi_rides")
            toast("Tokyo is open: the map's Tokyo tab.", "info", "ijichi")
        _dev_after()

    def dev_gojo_in():
        """WP11. Gojo keeps office hours today. roll_gojo resets gojo_in from
        the day's draw, then it is forced on, and his office hours go into
        today's plan. intensive_done is left alone: setting it would finish
        his first lesson (m_intensive), so until then his office stays locked."""
        roll_gojo()
        store.gojo_in = True
        for p in GOJO_IN_PERIODS:
            store.gojo_today[p] = "gojo_office"
        if has_flag("intensive_done"):
            toast("Gojo is in today: his office, mornings to afternoons.", "info", "gojo")
        else:
            toast("Gojo is in today, but his office stays locked until his first lesson.", "info", "gojo")
        _dev_after()

    def dev_items():
        """WP11. One of every item, hidden ones too, in one toast. Specials
        can be worn only once the story binds them (bound_specials), and the
        Inverted Spear stays sealed until Arc Two."""
        n = 0
        for i in all_item_ids(include_hidden=True):
            n += give_item(i, quiet=True)
        toast("One of every item (+%d). Specials wear once the story binds them." % n, "item", None, n)
        _dev_after()

    def dev_armory():
        """WP11. Set armory_open (Maki's The Armory sets it in play)."""
        flag("armory_open")
        if has_flag("storehouse_access"):
            toast("The armory is open: the storehouse, tools up to my grade.", "info", "maki")
        else:
            toast("The armory is open. The storehouse itself opens at roll call.", "info", "maki")
        _dev_after()

    def dev_complete():
        """WP11. Mark the main story complete (dev_story_complete), so the
        campus journal offers Arc Two."""
        flag("dev_story_complete")
        if has_flag("arc2_started"):
            toast("Main story marked complete. Arc Two has begun.", "mission")
        else:
            toast("Main story marked complete. Journal, Missions: Begin Arc Two.", "mission")
        _dev_after()

    def dev_week():
        """WP11. Seven new days, each through new_day() and its hooks."""
        for _ in range(7):
            new_day()
        toast("Day %d. A week has gone by." % store.day, "info")
        _dev_after()

    def dev_veil():
        """WP11. The ridge's "Look up at the veil" again today (and at all, for
        a save from before the tour set saw_the_ridge_veil)."""
        flag("saw_the_ridge_veil")
        store.actions_today.discard("veil")
        toast("The veil on the ridge can be looked at again today.", "info")
        _dev_after()

    def dev_night():
        """P0 (phase 2). The clock jumps to Night, today."""
        store.period = PERIODS[-1]
        toast("It is Night.", "info")
        _dev_after()

    def dev_gojo_night():
        """P0 (phase 2). A Gojo night is on tonight (night_dev, sb_night.rpy)."""
        night_dev("gojo")
        _dev_after()

    def dev_rest():
        """P0 (phase 2). Tomorrow is a rest day (night_dev, sb_night.rpy)."""
        night_dev("rest")
        _dev_after()

    def dev_yen():
        """P0 (phase 2). +20,000 yen, with a toast."""
        add_yen(20000)
        toast("+¥20,000 (¥%d now)." % store.yen, "item", None, 20000)
        _dev_after()

    def dev_market():
        """P0 (phase 2). The Black Market is found (night_dev, sb_night.rpy)."""
        night_dev("market")
        _dev_after()

    def dev_rows():
        """P0 (phase 2). The panel's buttons right now: DEV_BUTTONS without
        the rows whose `when` (DEV_WHEN) is False."""
        out = []
        for key, title in DEV_BUTTONS:
            when = DEV_WHEN.get(key)
            if when:
                fn = getattr(store, when, None)
                if fn is None or not fn():
                    continue
            out.append((key, title))
        return out

    def _dev_play(mid):
        """mid if its scene can play now; a waiting step first moves the days
        forward. Otherwise None, with a toast that says why."""
        m = MISSION_BY_ID.get(mid)
        if m is None:
            return None
        if store.explore_mode:
            toast("Explore mode never plays a story step.", "mission")
            return None
        s = mission_status(mid)
        if s == "waiting":
            n = mission_wait_days(mid)
            for _ in range(n):
                new_day()
            mission_cache_clear()
            s = mission_status(mid)
        if s in ("available", "active"):
            return mid
        if s in ("done", "skipped"):
            toast("%s: already done." % m["title"], "mission")
        else:
            toast("%s: %s" % (m["title"], mission_reason(mid) or s), "mission")
        return None

    def dev_story_mid():
        """WP11. The next story step's mission id if its scene can play now
        (for `call start_mission`), else None with a toast saying why. A
        step that is waiting for its day moves the days forward first."""
        o = current_objective()
        if o is None:
            toast("The campus isn't open yet.", "mission")
            return None
        if not o["mid"]:
            toast("No written story step is left.", "mission")
            return None
        return _dev_play(o["mid"])

    def dev_utahime_mid():
        """WP11. m_utahime (her arrival scene) if it can play now, else None
        with a toast."""
        return _dev_play("m_utahime")

    ## The panel's words ------------------------------------------------------------

    def dev_action(key):
        if key in DEV_SCENES:
            return Return(key)
        if key == "mc" or key in DEV_STUDENTS:
            return Function(dev_promote, key)
        return Function(DEV_FUNCS[key])

    DEV_FUNCS = dict(merit=dev_merit, bond=dev_bond, tokyo=dev_tokyo, gojo=dev_gojo_in,
                     items=dev_items, armory=dev_armory, complete=dev_complete,
                     week=dev_week, veil=dev_veil,
                     night=dev_night, gojo_night=dev_gojo_night, rest=dev_rest,
                     yen=dev_yen, market=dev_market)

    def dev_sensitive(key):
        return not (store.explore_mode and key in DEV_SCENES and key not in DEV_EXPLORE_OK)

    def dev_hint(key):
        """The small line under a button: what it will do, from here."""
        if key == "merit":
            m, need, nxt = merit_progress()
            if need:
                return "Merit %d (%s needs %d)" % (m, grade_label(nxt), need)
            return "Merit %d" % m
        if key == "mc" or key in DEV_STUDENTS:
            cur = _dev_grade_of(key)
            nxt = _dev_next_grade(cur)
            if nxt is None:
                return "%s: as high as Arc One goes" % grade_label(cur)
            return "%s → %s" % (grade_label(cur), grade_label(nxt))
        if key == "sample":
            return "Icons, hover labels and grade chips"
        if key in DEV_SCENES and store.explore_mode:
            return "Not in explore mode"
        if key == "story":
            o = current_objective()
            if o is None:
                return "The campus isn't open yet"
            if not o.get("mid"):
                return "No written story step left"
            txt = objective_text()
            return "Plays it: " + _dev_short(txt) if txt else "The campus isn't open yet"
        if key == "utahime":
            s = mission_status("m_utahime")
            if s in ("done", "skipped"):
                return "She's here"
            if s in ("available", "active", "waiting"):
                return "Plays The Room Next Door"
            return mission_reason("m_utahime") or "Plays The Room Next Door"
        if key == "bond":
            return "Everyone I've met (%d)" % len([w for w in store.roster if w in CAST])
        if key == "tokyo":
            return "Open" if tokyo_open() else "The ride-along's flag (ijichi_rides)"
        if key == "gojo":
            if gojo_in_today():
                return "He's in today"
            return "Office hours today" if has_flag("intensive_done") else "His office opens after his first lesson"
        if key == "items":
            return "Specials wear once bound; the Inverted Spear stays sealed (Arc Two)"
        if key == "armory":
            return "Open" if has_flag("armory_open") else "Maki's flag (armory_open): tools up to my grade"
        if key == "complete":
            if has_flag("arc2_started"):
                return "Arc Two has begun"
            if main_story_complete():
                return "Done: Journal, Missions, Begin Arc Two"
            return "Then Journal, Missions: Begin Arc Two"
        if key == "week":
            return "Day %d → Day %d" % (store.day, store.day + 7)
        if key == "veil":
            return "On the ridge, once more today"
        if key == "night":
            return "Already Night" if store.period == PERIODS[-1] else "%s → Night, today" % store.period
        if key == "gojo_night":
            return "He's on the ridge tonight"
        if key == "rest":
            return "No missions or training tomorrow"
        if key == "yen":
            return "¥%d → ¥%d" % (store.yen, store.yen + 20000)
        if key == "market":
            return "Found" if has_flag("market_found") else "Shibuya, after dark"
        return ""

    def dev_status():
        """The panel's top line: the day, my grade and merit, the objective."""
        when = hud_date() if store.explore_mode else "%s · %s" % (hud_date(), store.period)
        place = LOCATIONS.get(store.here, {}).get("name", store.here)
        obj = "Explore mode: no story" if store.explore_mode else (objective_text() or "No objective")
        return "%s · %s   ·   %s · merit %d   ·   %s" % (
            when, place, grade_label(player_grade()), store.merit, _dev_short(obj, 80))


style dev_frame is frame:
    background Frame("gui/panel.png", 4, 4)
    padding (40, 30, 40, 30)
    xsize 1300

style dev_title is text:
    font gui.display_font
    color gui.paper
    size 40

style dev_note is text:
    font gui.body_medium_font
    color gui.dim
    size 18


screen dev_panel():

    modal True
    zorder 100

    ## Under a harness's autoplay the panel closes itself, so a harness that
    ## drives the loop through ("dev",) is never left waiting on it.
    if smoke_autoplay:
        timer 0.05 action Return("close")

    key "game_menu" action Return("close")

    add graded_bg()
    add Solid("#07060cd8")

    ## Three columns; the rows a `when` hides are left out (3 x 6 until the
    ## night and the market are built, then 3 x 7, drawn tighter so it fits).
    $ _dev_rows = dev_rows()
    $ _dev_n = (len(_dev_rows) + 2) // 3
    $ _dev_tight = _dev_n > 6

    ## Left of centre, so the toast stack (top right) never covers it.
    frame:
        style "dev_frame"
        xpos 80
        yalign 0.5
        padding ((40, 16, 40, 16) if _dev_tight else (40, 30, 40, 30))

        vbox:
            spacing (8 if _dev_tight else 16)

            hbox:
                spacing 24
                text _("Review tools") style "dev_title"
                text _("Developer build only. Changes stick to this game.") style "dev_note" yalign 0.8

            text dev_status() style "dev_note" color gui.gold substitute False

            grid 3 _dev_n:
                xspacing 12
                yspacing (4 if _dev_tight else 12)
                for _k, _t in _dev_rows:
                    $ _on = dev_sensitive(_k)
                    button:
                        style "sb_action_button"
                        action dev_action(_k)
                        sensitive _on
                        vbox:
                            spacing 2
                            text _t style "sb_action_title" color (gui.paper if _on else gui.mute)
                            text dev_hint(_k) style "sb_action_hint" substitute False
                for _dev_pad in range(-len(_dev_rows) % 3):
                    null

            hbox:
                spacing 24
                text _("The two story buttons play their scenes, then return to campus.") style "dev_note" yalign 0.5 xsize 1040
                textbutton _("Close"):
                    id "dev_close"
                    style "sb_hud_nav_button"
                    action Return("close")


label dev_tools:
    ## The loop calls this for the place view's ("dev",) (D30): a developer
    ## build, on campus (settled_in; explore mode sets it too).
    if not (config.developer and has_flag("settled_in")):
        return
    call screen dev_panel
    if _return == "story":
        call start_mission(dev_story_mid())
        scene expression graded_bg()
    elif _return == "utahime":
        call start_mission(dev_utahime_mid())
        scene expression graded_bg()
    elif _return == "sample":
        call screen icon_sample
    return
