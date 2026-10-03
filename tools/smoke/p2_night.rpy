## tools/smoke/p2_night.rpy -- P4b's harness: the night rule, the Gojo night,
## the night in Tokyo and the Black Market (docs/PHASE2_DESIGN.md, 7 · P4b).
##
##   tools/smoke.sh tools/smoke/p2_night.rpy
##
## Every acceptance bullet of P4b is a named check below, in the plan's order:
##   A  the night rule's filter (night_filter_actions, rail_actions, the
##      phase-1 action card, NIGHT_STRICT off)
##   B  night_allows for missions and activities; the person view at Night;
##      the confession
##   C  explore mode and an unsettled game
##   D  the walk home: the loop itself is run (label sandbox) and stopped at
##      the place view
##   E  the net after scenes that roll the day themselves
##   F  when a Gojo night is due, the ceiling (past_cap 6 and 0), the marks
##   G  the owner's sentence: the night against every real day of training,
##      measured through sb_do_train, sb_do_hold, the lesson and the spars
##   H  one point of room (past_cap 0)
##   I  the day after a Gojo night
##   J  the night in Tokyo
##   K  the market
##   L  phase1_all (a NOTE: it is its own harness)
##   M  the saved variables pickle and are harmless in a replay
## Lines that wait for another package are NOTEs that say so (7.3).
##
## Costs are set through night_set_cost() and the night's own labels;
## purchases through market_buy() and label market_open (R5). Balance is
## asserted against the game's own labels and tables, never literals.
##
## Screenshots: worst_market_screen.png (R6), market_reqs.png (the checklist
## chips, with item_requirements patched in until P4a's are merged),
## night_card_ridge.png, night_gojo_offer.png, night_out_menu.png,
## rest_day_place.png.
##
## A run takes about 15 seconds.

init 999 python:
    import builtins
    import copy
    import os
    import pickle
    import re
    import time

    class ZZNightState(builtins.object):
        """Harness state, outside the store."""

        def __init__(self):
            self.boot = None                    # the defaults at boot
            self.texts = builtins.list()        # every say and menu line of the script
            self.said = builtins.list()         # every line said, renpy.say() from python included
            self.toasts = builtins.list()       # every toast (text, kind)
            self.labels = builtins.list()       # every label reached
            self.picks = builtins.list()        # menu choices to take, in order
            self.menus = builtins.list()        # (captions offered, the one taken)
            self.after_loop = None              # where to go when the loop reaches the place view
            self.real_pick = None
            self.market_plan = None             # what to answer market_screen with
            self.market_seen = 0
            self.plan = builtins.list()         # steps for label zz_n_run
            self.snap = None
            self.snap_t = 0.0
            self.g_cases = builtins.list()
            self.g_case = None
            self.g_days = builtins.list()
            self.g_fix = None
            self.g_day = None
            self.g_real = builtins.list()
            self.g_c0 = 0
            self.g_r0 = 0
            self.g_want = None
            self.g_best = 0
            self.days = 0
            self.keep = builtins.dict()

    zz_n = ZZNightState()

    ZZ_N_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                  "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                  "intensive_done", "ijichi_rides")
    ZZ_N_VARS = ("night_carried", "night_cost_day", "night_cost_kind", "night_gojo_last",
                 "night_gojo_day", "night_out_last", "market_bought")
    ZZ_N_GRADES = ("g4", "g3", "g2", "s1", "g1", "sp")

    ## --- capture ---------------------------------------------------------------

    zz_n_prev_filter = config.say_menu_text_filter

    def zz_n_text(s):
        zz_n.texts.append(s)
        if zz_n.snap and zz_n.snap[0] in s:
            config.auto_choice_delay = 1.5
            zz_n.snap_t = time.time()
        return zz_n_prev_filter(s) if zz_n_prev_filter else s

    config.say_menu_text_filter = zz_n_text

    ## renpy.say() from python (the walk home's line) passes no text filter:
    ## every line said, by a statement or by python, is recorded here.
    zz_n_real_say = renpy.exports.say

    def zz_n_say(who, what, *args, **kwargs):
        zz_n.said.append(what)
        return zz_n_real_say(who, what, *args, **kwargs)

    renpy.exports.say = zz_n_say

    def zz_n_label_cb(name, abnormal):
        zz_n.labels.append(name)

    config.label_callbacks.append(zz_n_label_cb)

    zz_n_real_sink = TOAST_SINK[0]

    def zz_n_sink(text, kind="info", who=None, amount=None):
        zz_n.toasts.append((builtins.str(text), kind))
        if zz_n_real_sink is not None:
            zz_n_real_sink(text, kind, who, amount)

    TOAST_SINK[0] = zz_n_sink

    def zz_n_said(n, needle):
        return [t for t in zz_n.texts[n:] if needle in t]

    def zz_n_carry_said(n):
        lines = builtins.set(NIGHT_CARRY_LINES.values())
        return [t for t in zz_n.said[n:] if t in lines]

    ## --- menus -----------------------------------------------------------------
    ## With store.smoke_autoplay off the night's menus are shown; the choice
    ## whose caption holds the next entry of zz_n.picks is taken.

    zz_n_real_menu = menu

    def zz_n_menu(items, **kwargs):
        caps = [lab for lab, val in items if val is not None]
        if zz_n.picks:
            want = zz_n.picks.pop(0)
            for lab, val in items:
                if val is not None and want in lab:
                    zz_n.menus.append((caps, lab))
                    return getattr(val, "value", val)
            zz_n.menus.append((caps, "MISSING " + want))
        else:
            zz_n.menus.append((caps, None))
        return zz_n_real_menu(items, **kwargs)

    ## (setattr: the store's own `menu` is replaced; it is not a new harness name.)
    setattr(store, "menu", zz_n_menu)

    def zz_n_play(menus=False):
        """Fast-skip the script. menus=True: the night's menus are shown
        (store.smoke_autoplay off) and answered from zz_n.picks."""
        autoplay(True)
        if menus:
            store.smoke_autoplay = False

    def zz_n_stop():
        autoplay(False)

    ## --- fixtures ----------------------------------------------------------------

    def zz_n_snapshot():
        """Every `default` variable of the game, deep-copied."""
        out = builtins.dict()
        for d in renpy.ast.default_statements:
            if getattr(d, "store", "store") != "store":
                continue
            k = getattr(d, "varname", None)
            if not k or not hasattr(store, k):
                continue
            try:
                out[k] = copy.deepcopy(getattr(store, k))
            except Exception:
                pass
        return out

    def zz_n_restore(snap=None):
        for k, v in (snap or zz_n.boot).items():
            setattr(store, k, copy.deepcopy(v))
        store.NIGHT_STRICT = True
        NIGHT_GOJO["past_cap"] = ZZ_N_PAST
        mission_cache_clear()
        toast_clear()

    ZZ_N_PAST = NIGHT_GOJO["past_cap"]

    def zz_n_fix(kind="rich", grade=None, **kw):
        """A settled game from the boot state. rich: everyone on the roster,
        Bond 60, the story flags of a mid-game save, Grade 3 (or `grade`).
        fresh: day 3 of a new game, Grade 4."""
        zz_n_restore()
        renpy.random.seed(20261003)
        base = dict(mc_name="Tester", mc_surname="Harness", day=9, period="Morning", here="courtyard", yen=5000)
        if kind == "fresh":
            base.update(day=3, yen=0)
        base.update(kw)
        settle(**base)
        if kind == "rich":
            for w in ROSTER_ORDER:
                if w not in store.roster:
                    store.roster.append(w)
            for w in ROSTER_ORDER:
                store.bonds[w] = 60
                if is_romanceable(w):
                    store.affection[w] = 40
            for f in ZZ_N_FLAGS:
                flag(f)
        else:
            for f in ZZ_N_FLAGS[:5]:
                flag(f)
        store.done_events.add("st_roll_call")
        promote("mc", grade or ("g3" if kind == "rich" else "g4"), quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()
        del zz_n.toasts[:]

    def zz_with(patches, fn):
        """Run fn() with store names replaced, then put them back."""
        old = builtins.dict((k, getattr(store, k)) for k in patches)
        for k, v in patches.items():
            setattr(store, k, v)
        try:
            return fn()
        finally:
            for k, v in old.items():
                setattr(store, k, v)

    def zz_n_rets(screen):
        """The value of every Return action on a shown screen's buttons."""
        zz_render()
        s = renpy.get_screen(screen)
        out = builtins.list()
        if s is None:
            return out
        seen = builtins.set()

        def flat(a):
            if isinstance(a, (builtins.list, builtins.tuple)):
                r = builtins.list()
                for x in a:
                    r.extend(flat(x))
                return r
            return [a]

        def each(d):
            if id(d) in seen:
                return
            seen.add(id(d))
            act = getattr(d, "action", None)
            if act is None:
                return
            for a in flat(act):
                if isinstance(a, Return):
                    out.append(a.value)

        s.visit_all(each)
        return out

    def zz_n_ids(rows):
        return [r[0] for r in rows]

    ## --- the loop ----------------------------------------------------------------
    ## zz_n_loop(target): the next statement must be `jump sandbox`. The real
    ## loop runs from its top (ensure_state, the walk home, the story pick,
    ## the place view); when the place view is waiting the driver jumps to
    ## `target`. No story beat is picked while it runs.

    def zz_n_no_event(*args, **kwargs):
        return None

    def zz_n_loop(target):
        zz_n.after_loop = target
        zz_n.real_pick = store.pick_event
        store.pick_event = zz_n_no_event
        zz_n_play()

    def zz_n_loop_done():
        zz_n_stop()
        if zz_n.real_pick is not None:
            store.pick_event = zz_n.real_pick
            zz_n.real_pick = None

    def zz_n_tick():
        if zz_n.after_loop and renpy.get_screen("sb_place") is not None:
            t = zz_n.after_loop
            zz_n.after_loop = None
            renpy.jump(t)
        if zz_n.market_plan is not None and renpy.get_screen("market_screen") is not None:
            zz_n.market_seen += 1
            if zz_n.market_plan:
                return zz_n.market_plan.pop(0)
            return ("close",)
        if zz_n.snap and renpy.get_screen("choice") is not None and time.time() > zz_n.snap_t + 0.6:
            name = zz_n.snap[1]
            zz_n.snap = None
            shot(name, wait=0)
            config.auto_choice_delay = 0.05
        return None

    config.overlay_screens.append("zz_n_driver")

    ## The harness's own action hotspot (P6's are not in yet): Train, in the
    ## training hall. It proves the hotspot path of the rest day.
    register_hotspot("zz_n_train", "training", 300, 420, "train", act="train")

    ## --- the owner's sentence (section G) ---------------------------------------

    def zz_n_train_places():
        """Every place whose place_actions offers Train (or Practice)."""
        out = []
        old = store.period, store.here
        store.period = PERIODS[0]
        for l in LOC_ORDER:
            store.here = l
            if "train" in zz_n_ids(place_actions(l)):
                out.append(l)
        store.period, store.here = old
        return out

    def zz_n_room(c0):
        """A settled fixture at Control c0, promoted until the whole night
        fits under the ceiling (so its gain can be compared with
        night_gojo_gain() itself), Gojo in, the lesson on offer."""
        for g in ZZ_N_GRADES:
            zz_n_fix("rich", grade=g, control=c0, ce=60, ce_max=60, period=PERIODS[0], here=NIGHT_GOJO["place"])
            store.gojo_in = True
            want = night_gojo_gain()
            cap, rcap = grade_cap("stat"), grade_cap("reserve")
            if (cap is None or cap - c0 >= want[0]) and (rcap is None or rcap - store.ce_max >= want[1]):
                return g
        return None

    def zz_n_g_setup():
        c0, strict = zz_n.g_case
        g = zz_n_room(c0)
        store.NIGHT_STRICT = strict
        zz_n.g_fix = zz_n_snapshot()
        zz_n.g_want = night_gojo_gain()
        zz_n.g_best = night_day_best()
        zz_n.g_real = builtins.list()
        n = len(PERIODS)
        days = builtins.list()
        for l in zz_n_train_places():
            days.append(("%s, hold first" % l, [("hold",)] + [("train", l)] * n))
            days.append(("%s, hold last" % l, [("train", l)] * n + [("hold",)]))
        ridge = NIGHT_GOJO["place"]
        days.append(("the lesson day, hold first", [("hold",), ("lesson",)] + [("train", ridge)] * (n - 1)))
        days.append(("the lesson day, hold last", [("lesson",)] + [("train", ridge)] * (n - 1) + [("hold",)]))
        for w in ACT_BY_ID["train"]["who"]:
            days.append(("Train together, %s" % w, [("spar", w)] * n))
        zz_n.g_days = days
        zz_n.keep["grade"] = g

    def zz_n_g_begin():
        zz_n_restore(zz_n.g_fix)
        store.NIGHT_STRICT = zz_n.g_case[1]
        store.gojo_in = True
        zz_n.g_day = zz_n.g_days.pop(0)
        zz_n.plan = builtins.list(zz_n.g_day[1])
        zz_n.g_c0, zz_n.g_r0 = store.control, store.ce_max

    def zz_n_g_end():
        zz_n.g_real.append((zz_n.g_day[0], store.control - zz_n.g_c0, store.ce_max - zz_n.g_r0))
        zz_n.days += 1

    def zz_n_g_night_begin():
        zz_n_restore(zz_n.g_fix)
        store.NIGHT_STRICT = zz_n.g_case[1]
        store.gojo_in = True
        store.period = PERIODS[-1]
        store.here = NIGHT_GOJO["place"]
        night_dev("gojo")
        zz_n.g_c0, zz_n.g_r0 = store.control, store.ce_max
        zz_n.keep["day"] = store.day

    def zz_n_g_verdict():
        c0, strict = zz_n.g_case
        tag = "Control %d, %s, NIGHT_STRICT %s" % (c0, grade_label(zz_n.keep["grade"]), strict)
        got = (store.control - zz_n.g_c0, store.ce_max - zz_n.g_r0)
        best_c = builtins.max(r[1] for r in zz_n.g_real)
        best_r = builtins.max(r[2] for r in zz_n.g_real)
        top = [r for r in zz_n.g_real if r[1] == best_c][0]
        check(zz_n.keep["grade"] is not None and len(zz_n.g_real) == 2 * len(zz_n_train_places()) + 2 + len(ACT_BY_ID["train"]["who"]),
              "the owner's sentence (%s): every real day ran" % tag, len(zz_n.g_real))
        check(zz_n.g_best >= best_c,
              "the owner's sentence (%s): (1) night_day_best() %d is at least the best real day's Control +%d (%s)"
              % (tag, zz_n.g_best, best_c, top[0]), zz_n.g_real)
        check(got[0] > best_c and got[1] > best_r,
              "the owner's sentence (%s): (2) the night gives Control +%d and reserve +%d, each more than the best day's +%d and +%d"
              % (tag, got[0], got[1], best_c, best_r), (got, zz_n.g_real))
        check(got == zz_n.g_want,
              "the owner's sentence (%s): (3) the night's gains are night_gojo_gain() %r" % (tag, zz_n.g_want), got)
        check(store.day == zz_n.keep["day"] + 1 and store.here == "dorm" and not night_can_work(),
              "the owner's sentence (%s): the night ends in my room the next morning, on a rest day" % tag,
              (store.day, store.here, night_can_work()))
        zz_n_restore()


screen zz_n_driver():
    zorder 300
    timer 0.05 repeat True action Function(zz_n_tick)


## Runs zz_n.plan: ("train", place), ("hold",), ("lesson",), ("spar", who).
## Stamina and cursed energy are refilled before each step. The lesson and
## the spar go through sb_activity, as the person view does.
label zz_n_run:
    while zz_n.plan:
        $ _zz_step = zz_n.plan.pop(0)
        $ stamina = stamina_max
        $ ce = ce_max
        if _zz_step[0] == "train":
            $ here = _zz_step[1]
            call sb_do_train
        elif _zz_step[0] == "hold":
            $ actions_today.discard("hold")
            call sb_do_hold
        elif _zz_step[0] == "lesson":
            $ here = "gojo_office"
            $ actions_today.discard("lesson")
            call sb_activity("lesson", "gojo")
        elif _zz_step[0] == "spar":
            $ here = "dojo"
            $ spent_today.discard(_zz_step[1])
            call sb_activity("train", _zz_step[1])
    return


label zz_smoke:

    python:
        zz_n.boot = zz_n_snapshot()
        check(night_exists() and market_exists(), "night_exists() and market_exists() are True")
        check(NIGHT_STRICT is True and NIGHT_GOJO["past_cap"] == 6,
              "the owner's rulings are the shipped values: NIGHT_STRICT True, past_cap 6", (NIGHT_STRICT, NIGHT_GOJO))
        check(night_validate() == [] and market_validate() == [], "the night's and the market's validators are clean",
              night_validate() + market_validate())

    ## The statements saves sit on (2.3), read from the source.
    python:
        with open(os.path.join(config.gamedir, "sb_night.rpy"), encoding="utf-8") as _zz_f:
            _zz_src = _zz_f.read()
        with open(os.path.join(config.gamedir, "sb_market.rpy"), encoding="utf-8") as _zz_f:
            _zz_msrc = _zz_f.read()
        _zz_caps = ('"A whole night with Gojo. Tomorrow I won\'t be fit for missions or training."',
                    '"[_night_name], after dark."', '"The night isn\'t over yet."')
        check(len(re.findall(r"^ +menu:$", _zz_src, re.M)) == 3 and all(("menu:\n" in _zz_src and c in _zz_src) for c in _zz_caps)
              and all(re.search(r"menu:\n +" + re.escape(c), _zz_src) for c in _zz_caps),
              "2.3: sb_night.rpy holds exactly three menus, each opening with its caption")
        check(_zz_src.count("call market_open\n") == 2
              and 'call market_open\n        $ _night_pick = "market_done"\n' in _zz_src
              and 'call market_open\n                    $ _night_pick = "club_market"\n' in _zz_src,
              "2.3: sb_night.rpy holds two `call market_open`, each with its line after it")
        check("        call screen market_screen\n        $ _market_r = _return\n" in _zz_msrc and len(re.findall(r"^ +call screen market_screen$", _zz_msrc, re.M)) == 1,
              "2.3: sb_market.rpy holds `call screen market_screen` / `$ _market_r = _return`")
        check("## PLACEHOLDER — rewrite in phase 4" in _zz_src.split("label sb_do_night_gojo:")[1][:80]
              and "## PLACEHOLDER — rewrite in phase 4" in _zz_src.split("label night_out(key):")[1][:80],
              "the two placeholder scenes are marked '## PLACEHOLDER — rewrite in phase 4'")
        for _zz_name in ("night_carry_home", "night_out", "sb_do_night_bed", "sb_do_night_gojo", "market_open"):
            check(renpy.has_label(_zz_name), "label %s exists" % _zz_name)

    ############################################################################
    ## A. The filter
    ############################################################################
    python:
        zz_n_fix("rich")
        _zz_bad = []
        for _zz_l in LOC_ORDER:
            here = _zz_l
            period = PERIODS[-1]
            _zz_f = night_filter_actions(_zz_l, place_actions(_zz_l))
            _zz_ids = zz_n_ids(_zz_f)
            if "wait" in _zz_ids:
                _zz_bad.append((_zz_l, "wait"))
            if ("night_bed" in _zz_ids) != (_zz_l != "dorm"):
                _zz_bad.append((_zz_l, "night_bed"))
            if _zz_l == "dorm" and "sleep" not in _zz_ids:
                _zz_bad.append((_zz_l, "no sleep"))
            for _zz_a in _zz_f:
                if _zz_a[3] and _zz_a[0] not in NIGHT_OK:
                    _zz_bad.append((_zz_l, _zz_a[0]))
                if len(_zz_a) != 4:
                    _zz_bad.append((_zz_l, "shape", _zz_a))
        check(not _zz_bad, "A: at Night the filter has no wait anywhere, night_bed everywhere but dorm, sleep in dorm, "
              "and no costed id outside NIGHT_OK (%d rooms)" % len(LOC_ORDER), _zz_bad[:6])

        ## P7's card table is not in yet: its row is checked as a row.
        _zz_f = night_filter_actions("dorm_common", [("cards_play", "Play cards", "", 1), ("wait", "Wait", "", 1)])
        check(zz_n_ids(_zz_f) == ["night_bed"], "A: a costed cards_play row is dropped at Night", _zz_f)
        note("A: cards_play", "P7's card table arrives in wave 2; the row above stands in for it (7.3: 'closed at Night' is P7's line)")

        ## rail_actions
        _zz_bad = []
        for _zz_comp in (None, "yuji"):
            companion = _zz_comp
            for _zz_l in LOC_ORDER:
                here = _zz_l
                for _zz_per in PERIODS:
                    period = _zz_per
                    _zz_cov = hot_covers(_zz_l)
                    _zz_want = [tuple(a) for a in night_filter_actions(_zz_l, place_actions(_zz_l)) if a[0] not in _zz_cov]
                    _zz_rail = rail_actions(_zz_l)
                    _zz_tail = [r for r in _zz_rail if r[0] == "release"]
                    _zz_body = [tuple(r[:4]) for r in _zz_rail if r[0] != "release"]
                    if _zz_body != _zz_want or bool(_zz_tail) != bool(_zz_comp) or (_zz_tail and _zz_rail[-1][0] != "release"):
                        _zz_bad.append((_zz_comp, _zz_l, _zz_per))
        companion = None
        check(not _zz_bad, "A: rail_actions is the filtered list minus hot_covers, plus release (last) when someone is along",
              _zz_bad[:6])
        here = "training"
        period = PERIODS[0]
        _zz_cov = zz_with(dict(view_person_rects=lambda loc: []), lambda: (hot_covers("training"), zz_n_ids(rail_actions("training"))))
        check("train" in _zz_cov[0] and "train" not in _zz_cov[1],
              "A: a hotspot that covers train takes it out of the column (the harness's own hotspot)", _zz_cov)

        ## every other period, an ordinary day: unchanged
        _zz_bad = []
        for _zz_l in LOC_ORDER:
            here = _zz_l
            for _zz_per in PERIODS[:-1]:
                period = _zz_per
                _zz_acts = place_actions(_zz_l)
                _zz_f = night_filter_actions(_zz_l, _zz_acts)
                if _zz_f is not _zz_acts or _zz_f != place_actions(_zz_l):
                    _zz_bad.append((_zz_l, _zz_per))
        check(not _zz_bad, "A: before Night, on an ordinary day, night_filter_actions returns acts unchanged", _zz_bad[:6])

        ## place_actions itself
        _zz_bad = []
        for _zz_l in LOC_ORDER:
            here = _zz_l
            for _zz_per in PERIODS:
                period = _zz_per
                _zz_ids = zz_n_ids(place_actions(_zz_l))
                if _zz_ids[-1] != "wait" or "night_bed" in _zz_ids:
                    _zz_bad.append((_zz_l, _zz_per, _zz_ids))
        period = PERIODS[-1]
        here = "dorm"
        check(not _zz_bad and "study" in zz_n_ids(place_actions("dorm")),
              "A: place_actions is unchanged at every period (Wait last, the costed rows there, no night_bed)", _zz_bad[:4])

        ## NIGHT_STRICT off
        store.NIGHT_STRICT = False
        _zz_bad = []
        for _zz_l in LOC_ORDER:
            here = _zz_l
            _zz_acts = place_actions(_zz_l)
            _zz_f = night_filter_actions(_zz_l, _zz_acts)
            _zz_cost = [a[0] for a in _zz_acts if a[3] and a[0] != "wait"]
            _zz_back = [a for a in _zz_f if a[3]]
            if [a[0] for a in _zz_back] != _zz_cost or "wait" in zz_n_ids(_zz_f):
                _zz_bad.append((_zz_l, _zz_cost, _zz_back))
            if any(not a[2].endswith("ends the night") for a in _zz_back if a[0] not in NIGHT_OK):
                _zz_bad.append((_zz_l, "hint"))
        check(not _zz_bad, "A: with NIGHT_STRICT False the costed rows return, marked 'ends the night'; Wait is still Go to bed",
              _zz_bad[:4])
        check(night_allows("train", 1) and night_allows("hang", 1), "A: with NIGHT_STRICT False night_allows is True at Night")
        store.NIGHT_STRICT = True

        ## the icons the two new rows use
        check(icon_for("act", "night_bed") in ICONS and icon_for("act", "night_gojo") in ICONS
              and icon_for("act", "night_gojo") in ICON_GOLD,
              "A: night_bed and night_gojo have icons; night_gojo is gold",
              (icon_for("act", "night_bed"), icon_for("act", "night_gojo")))

    ## The phase-1 action card, rendered (no P2 needed).
    scene expression graded_bg("ridge", "Night")
    python:
        zz_n_fix("rich", here="ridge", period=PERIODS[-1])
        renpy.show_screen("sb_place")
        _zz_r = zz_n_rets("sb_place")
        check(("act", "night_bed") in _zz_r and ("act", "wait") not in _zz_r and ("act", "train") not in _zz_r,
              "A: the place view at Night on the ridge offers Go to bed, and neither Wait nor Train", _zz_r)
        note("A: the place view's words at Night", [t for t in zz_texts("sb_place") if t in ("Wait", "Go to bed", "Train")])
        shot("night_card_ridge")
        period = "Evening"
        _zz_r = zz_n_rets("sb_place")
        check(("act", "wait") in _zz_r and ("act", "train") in _zz_r and ("act", "night_bed") not in _zz_r,
              "A: the same view in the Evening still has Wait and Train", _zz_r)
        renpy.hide_screen("sb_place")
        objective_leave()

    ############################################################################
    ## B. night_allows
    ############################################################################
    python:
        zz_n_fix("rich", period=PERIODS[-1])
        _zz_bad = []
        _zz_n_night = 0
        for _zz_m in MISSIONS:
            _zz_has = PERIODS[-1] in (_zz_m["periods"] or ())
            _zz_n_night += int(_zz_has)
            for _zz_cost in (_zz_m["cost"], 0, 2):
                if night_allows("mission:" + _zz_m["id"], _zz_cost) != bool(_zz_has or not _zz_cost):
                    _zz_bad.append((_zz_m["id"], _zz_cost))
        check(not _zz_bad and _zz_n_night >= 1 and not night_allows("mission:cm_ijichi_1", MISSION_BY_ID["cm_ijichi_1"]["cost"]),
              "B: night_allows('mission:' + mid, cost) is True at Night exactly when the periods include Night or it costs nothing "
              "(%d missions, %d with Night)" % (len(MISSIONS), _zz_n_night), _zz_bad[:6])
        _zz_night = night_allows("hang", 1)
        period = "Evening"
        check(not _zz_night and night_allows("hang", 1) and night_allows("mission:cm_ijichi_1", 2),
              "B: night_allows('hang', 1) is False at Night and True in the Evening")

        ## the person view at Night
        period = PERIODS[-1]
        _zz_bad = []
        _zz_seen = 0
        for _zz_w in ROSTER_ORDER:
            for _zz_l in LOC_ORDER:
                here = _zz_l
                for _zz_c in person_choices(_zz_w, _zz_l):
                    _zz_seen += 1
                    if _zz_c["kind"] == "mission" and not night_allows("mission:" + _zz_c["id"], MISSION_BY_ID[_zz_c["id"]]["cost"]):
                        _zz_bad.append((_zz_w, _zz_l, _zz_c["id"]))
                    if _zz_c["kind"] == "do" and _zz_c["cost"] and _zz_c["id"] not in NIGHT_OK:
                        _zz_bad.append((_zz_w, _zz_l, _zz_c["id"]))
        check(not _zz_bad and _zz_seen, "B: at Night person_choices holds no mission the night refuses and no costed activity "
              "outside NIGHT_OK (%d people x %d rooms)" % (len(ROSTER_ORDER), len(LOC_ORDER)), _zz_bad[:6])

        ## cm_ijichi_1 (cost 2), offered at the gate
        here = "gate"
        _zz_offer = dict(missions_with=lambda who, loc=None: (["cm_ijichi_1"] if who == "ijichi" else []))
        _zz_at_night = zz_with(_zz_offer, lambda: [c["id"] for c in person_choices("ijichi", "gate") if c["kind"] == "mission"])
        period = "Evening"
        _zz_at_eve = zz_with(_zz_offer, lambda: [c["id"] for c in person_choices("ijichi", "gate") if c["kind"] == "mission"])
        check(MISSION_BY_ID["cm_ijichi_1"]["cost"] == 2 and _zz_at_night == [] and _zz_at_eve == ["cm_ijichi_1"],
              "B: cm_ijichi_1 (cost 2), offered at the gate, is not on Ijichi at Night and is in the Evening",
              (_zz_at_night, _zz_at_eve))

        ## the confession
        _zz_w = [w for w in ROSTER_ORDER if is_romanceable(w)][0]
        bonds[_zz_w] = 100
        affection[_zz_w] = AFF_BASE_MAX
        _zz_eve = activity_state(ACT_BY_ID["rom_say"], _zz_w)
        period = PERIODS[-1]
        _zz_night = activity_state(ACT_BY_ID["rom_say"], _zz_w)
        check(confession_ready(_zz_w) and _zz_eve[0] and _zz_night == (False, "Too late"),
              "B: activity_state refuses rom_say at Night for someone who is confession_ready (%s)" % _zz_w, (_zz_eve, _zz_night))
        _zz_ok = [a for a in NIGHT_OK if a in ACT_BY_ID]
        check(all(night_allows(a, ACT_BY_ID[a]["cost"]) for a in _zz_ok) and len(_zz_ok) == 3,
              "B: stargaze, rom_close and int_night are still allowed at Night", _zz_ok)

    ############################################################################
    ## C. Explore mode and an unsettled game
    ############################################################################
    python:
        zz_n_fix("rich", here="ridge", period=PERIODS[-1])
        explore_mode = True
        _zz_acts = [("train", "Train", "", 1), ("wait", "Wait", "", 1)]
        _zz_same = night_filter_actions("ridge", _zz_acts) is _zz_acts
        _zz_allow = night_allows("train", 1)
        night_carried = "ridge"
        _zz_pend = night_pending()
        night_carried = ""
        new_day()
        check(_zz_same and _zz_allow and not _zz_pend and night_carried == "" and not night_pending()
              and night_out_ok("shibuya") == (False, "") and night_marks() == {} and not night_gojo_due(),
              "C: explore mode: no filter, no pending, no night out, no Gojo night",
              (_zz_same, _zz_allow, _zz_pend, night_carried))
        explore_mode = False

        zz_n_restore()
        fixture(here="ridge", period=PERIODS[-1])
        _zz_acts = [("train", "Train", "", 1), ("wait", "Wait", "", 1)]
        _zz_same = night_filter_actions("ridge", _zz_acts) is _zz_acts
        _zz_allow = night_allows("train", 1)
        new_day()
        check(not has_flag("settled_in") and _zz_same and _zz_allow and night_carried == "" and not night_pending(),
              "C: an unsettled game: no filter, no pending", (_zz_same, _zz_allow, night_carried))

    ############################################################################
    ## D. The walk home
    ############################################################################
    python:
        zz_n_fix("rich", here="ridge", period=PERIODS[-1])
        _zz_day = day
        _zz_rolled = advance_period()
        check(_zz_rolled and day == _zz_day + 1 and night_pending() and night_carried == "ridge",
              "D: advance_period() from Night on the ridge sets night_pending()", (day, night_carried))
        zz_n.keep["t"] = len(zz_n.said)
        zz_n_loop("zz_n_d2")
    jump sandbox

label zz_n_d2:
    python:
        zz_n_loop_done()
        _zz_said = zz_n_carry_said(zz_n.keep["t"])
        check(here == "dorm" and not night_pending() and night_carried == ""
              and _zz_said == [NIGHT_CARRY_LINES["mountain"]] and "night_carry_home" in zz_n.labels,
              "D: one turn of the loop leaves here == 'dorm', nothing pending, and exactly one carry line said", (here, _zz_said))

        zz_n_fix("rich", here="dorm", period=PERIODS[-1])
        advance_period()
        check(not night_pending() and night_carried == "", "D: the same from dorm never sets it", night_carried)

        zz_n_fix("rich", here="training", period="Noon")
        for _zz_i in range(7):
            new_day()
        check(night_pending() and night_carried == "training", "D: seven new_day() calls in a row leave a pending walk", night_carried)
        zz_n.keep["t"] = len(zz_n.said)
        del zz_n.labels[:]
        zz_n_loop("zz_n_d3")
    jump sandbox

label zz_n_d3:
    python:
        zz_n_loop_done()
        _zz_said = zz_n_carry_said(zz_n.keep["t"])
        check(here == "dorm" and not night_pending() and _zz_said == [NIGHT_CARRY_LINES["grounds"]]
              and zz_n.labels.count("night_carry_home") == 1,
              "D: ...and exactly one walk: one carry line, night_carry_home once", (here, _zz_said))
        zz_n.keep["t"] = len(zz_n.said)
        del zz_n.labels[:]
        zz_n_loop("zz_n_d4")
    jump sandbox

label zz_n_d4:
    python:
        zz_n_loop_done()
        check(zz_n_carry_said(zz_n.keep["t"]) == [] and "night_carry_home" not in zz_n.labels,
              "D: the next turn of the loop says nothing more")

        zz_n_fix("rich", here="ridge", period="Evening")
        _zz_day = day
        _zz_rolled = advance_period_soft(2)
        check(not _zz_rolled and period == PERIODS[-1] and day == _zz_day and not night_pending() and night_carried == "",
              "D: a two-period action started in the Evening ends at Night with nothing pending", (period, day, night_carried))

        ## a mark left by a scene that took me to my room itself is dropped
        zz_n_fix("rich", here="ridge", period=PERIODS[-1])
        new_day()
        here = "dorm"
        _zz_p = night_pending()
        here = "ridge"
        check(not _zz_p and not night_pending() and night_carried == "",
              "D: a scene that already took me to my room leaves no walk behind for later")

    ## Go to bed, from the ridge.
    python:
        zz_n_fix("rich", here="ridge", period=PERIODS[-1])
        zz_n.keep["day"] = day
        zz_n.keep["t"] = len(zz_n.texts)
        zz_n_play()
    call sb_do_night_bed
    python:
        zz_n_stop()
        check(here == "dorm" and day == zz_n.keep["day"] + 1 and period == PERIODS[0] and not night_pending()
              and len(zz_n_said(zz_n.keep["t"], "I walk back while I can still feel my feet.")) == 1
              and len(zz_n_said(zz_n.keep["t"], "I sleep.")) == 1,
              "D: Go to bed from the ridge: one line, my room, the sleep text, a new day, nothing pending", (here, day, period))
        zz_n_fix("rich", here="dorm", period=PERIODS[-1])
        zz_n.keep["t"] = len(zz_n.texts)
        zz_n_play()
    call sb_do_night_bed
    python:
        zz_n_stop()
        check(zz_n_said(zz_n.keep["t"], "I walk back") == [] and here == "dorm",
              "D: sb_do_night_bed in my room says no walking line")

    ############################################################################
    ## E. The net after scenes that roll the day themselves
    ############################################################################
    python:
        zz_n_fix("rich", here="office", period="Evening")
        zz_n.keep["day"] = day
        zz_n_play()
    call ms_nade_1
    python:
        zz_n_stop()
        check(day == zz_n.keep["day"] + 1 and here == "office" and night_pending(),
              "E: a Nade mission started in the Evening rolls the day at the office: a walk is pending", (day, here, night_carried))
        zz_n.keep["t"] = len(zz_n.said)
        zz_n_loop("zz_n_e2")
    jump sandbox

label zz_n_e2:
    python:
        zz_n_loop_done()
        _zz_said = zz_n_carry_said(zz_n.keep["t"])
        check(here == "dorm" and _zz_said == [NIGHT_CARRY_LINES["staff"]],
              "E: ...and the loop ends with here == 'dorm' and one carry line", (here, _zz_said))

        _zz_w = [w for w in ROSTER_ORDER if is_romanceable(w)][0]
        zz_n_fix("rich", here="girls_dorm", period=PERIODS[-1])
        zz_n.keep["day"] = day
        zz_n.keep["who"] = _zz_w
        zz_n_play()
    call sb_activity("int_night", zz_n.keep["who"])
    python:
        zz_n_stop()
        check(day == zz_n.keep["day"] + 1 and night_pending() and night_carried == "girls_dorm",
              "E: int_night at Night rolls the day in someone's room: a walk is pending", (day, here, night_carried))
        zz_n.keep["t"] = len(zz_n.said)
        zz_n_loop("zz_n_e3")
    jump sandbox

label zz_n_e3:
    python:
        zz_n_loop_done()
        _zz_said = zz_n_carry_said(zz_n.keep["t"])
        check(here == "dorm" and _zz_said == ["I let myself out before the corridor wakes."],
              "E: ...and the loop says 'I let myself out before the corridor wakes.' once, and I'm in my room", (here, _zz_said))

        zz_n_fix("rich", here="courtyard", period=PERIODS[-1])
        zz_n.keep["day"] = day
        zz_n.keep["ev"] = [e for e in EVENTS if e["label"] == "st_second_years"][0]
        done_events.discard("st_second_years")
        zz_n_play()
    call play_event(zz_n.keep["ev"])
    python:
        zz_n_stop()
        check(day == zz_n.keep["day"] + 1 and night_pending(),
              "E: a story beat that ends in advance_period() at Night rolls the day in the courtyard: a walk is pending",
              (day, here, night_carried))
        zz_n.keep["t"] = len(zz_n.said)
        zz_n_loop("zz_n_e4")
    jump sandbox

label zz_n_e4:
    python:
        zz_n_loop_done()
        _zz_said = zz_n_carry_said(zz_n.keep["t"])
        check(here == "dorm" and _zz_said == [NIGHT_CARRY_LINES["heart"]],
              "E: ...and the loop ends with here == 'dorm' and one carry line", (here, _zz_said))
        ## the line is the place's own before its area's
        _zz_bad = []
        for _zz_p, _zz_k in (("girls_dorm", "girls_dorm"), ("rooftop", "dorms"), ("dorm_common", "dorms"),
                             ("ridge", "mountain"), ("office", "staff"), ("no_such_place", "")):
            night_carried = _zz_p
            if night_carry_line() != NIGHT_CARRY_LINES[_zz_k]:
                _zz_bad.append((_zz_p, night_carry_line()))
        night_carried = ""
        check(not _zz_bad and NIGHT_CARRY_LINES["dorms"] != NIGHT_CARRY_LINES["girls_dorm"],
              "E: the corridor line is the girls' dormitory's alone: the rooftop and the common room get the area's line, "
              "and an unknown place the fallback", _zz_bad)
        note("E: a beat picked by the loop", "the loop picks a story beat after it asks night_pending() (sb_loop.rpy), so a "
             "Night beat that rolls the day would be walked home one action late; no Arc One beat does (hand-off to P8)")
        note("E: board jobs", "not a case: the board refuses in the Evening and at Night (board_take_reason)")

    ############################################################################
    ## F. When a Gojo night is due
    ############################################################################
    python:
        zz_n_fix("rich", control=30)
        gojo_in = True
        _zz_due = night_gojo_due()
        flags.discard("intensive_done")
        _zz_no_flag = night_gojo_due()
        flag("intensive_done")
        gojo_in = False
        _zz_out = night_gojo_due()
        gojo_in = True
        night_gojo_last = day - (NIGHT_GOJO["gap"] - 1)
        _zz_soon = night_gojo_due()
        night_gojo_last = day - NIGHT_GOJO["gap"]
        _zz_gap = night_gojo_due()
        check(_zz_due and not _zz_no_flag and not _zz_out and not _zz_soon and _zz_gap,
              "F: night_gojo_due() is False without intensive_done, on a day Gojo is out, and within %d days of the last; True otherwise"
              % NIGHT_GOJO["gap"], (_zz_due, _zz_no_flag, _zz_out, _zz_soon, _zz_gap))

        ## past_cap 6: every grade, every Control
        _zz_bad = []
        for _zz_g in ZZ_N_GRADES:
            zz_n_fix("rich", grade=_zz_g)
            gojo_in = True
            _zz_ceil = grade_cap("stat") or 100
            _zz_rcap = grade_cap("reserve")
            for _zz_res in (60, _zz_rcap or 300):
                ce_max = _zz_res
                for _zz_c in range(0, 101):
                    control = _zz_c
                    try:
                        _zz_d = night_gojo_due()
                    except Exception as _zz_e:
                        _zz_bad.append((_zz_g, _zz_c, repr(_zz_e)))
                        continue
                    ## under 100 the night is due until Control sits past_cap
                    ## above the ceiling; at a ceiling of 100 only while it
                    ## can still beat a day (it never takes Control past 100)
                    _zz_top = _zz_ceil + NIGHT_GOJO["past_cap"]
                    _zz_want = (_zz_c < _zz_top) if _zz_top <= 100 else (100 - _zz_c > night_day_best())
                    if _zz_d != _zz_want:
                        _zz_bad.append((_zz_g, _zz_res, _zz_c, _zz_d))
        check(not _zz_bad, "F: with past_cap 6 a night is due at every grade and every Control, at the Control and reserve "
              "ceilings too, and not once Control sits 6 above the ceiling; at a ceiling of 100 only while a night still beats a day; "
              "Special Grade does not raise", _zz_bad[:6])

        ## past_cap 0, against the rule written out
        NIGHT_GOJO["past_cap"] = 0
        _zz_bad = []
        for _zz_g in ZZ_N_GRADES:
            zz_n_fix("rich", grade=_zz_g)
            NIGHT_GOJO["past_cap"] = 0
            gojo_in = True
            _zz_ceil = grade_cap("stat") or 100
            _zz_rcap = grade_cap("reserve")
            for _zz_res in (60, (_zz_rcap or 300) - night_gojo_gain()[1] + 1):
                ce_max = _zz_res
                for _zz_c in range(0, 101):
                    control = _zz_c
                    _zz_fits = _zz_rcap is None or ce_max + night_gojo_gain()[1] <= _zz_rcap
                    _zz_want = (_zz_ceil - _zz_c > night_day_best()) and _zz_fits
                    if night_gojo_due() != _zz_want:
                        _zz_bad.append((_zz_g, _zz_res, _zz_c))
        check(not _zz_bad, "F: with past_cap 0 a night is due only when ceiling - control > night_day_best() and the reserve gain fits",
              _zz_bad[:6])

        ## the two cases section 0 tells the owner about
        zz_n_fix("rich", grade="g2", control=55)
        gojo_in = True
        NIGHT_GOJO["past_cap"] = 0
        _zz_a0 = night_gojo_due()
        NIGHT_GOJO["past_cap"] = ZZ_N_PAST
        _zz_a6 = night_gojo_due()
        _zz_got = night_gojo_apply()
        _zz_end = control
        zz_n_fix("rich", grade="s1", control=70)
        gojo_in = True
        NIGHT_GOJO["past_cap"] = 0
        _zz_b0 = night_gojo_due()
        NIGHT_GOJO["past_cap"] = ZZ_N_PAST
        _zz_b6 = night_gojo_due()
        check(not _zz_a0 and _zz_b0 and _zz_a6 and _zz_b6 and 70 < _zz_end <= 76,
              "F: past_cap 0: Control 55 just promoted to Grade 2 is not offered a night, Control 70 at Semi-Grade 1 is; "
              "past_cap 6: both are, and the first ends above 70 and at most at 76 (%d)" % _zz_end,
              (_zz_a0, _zz_b0, _zz_a6, _zz_b6, _zz_got))

        ## Special Grade
        zz_n_fix("rich", grade="sp", control=90)
        gojo_in = True
        _zz_d = night_gojo_due()
        _zz_got = night_gojo_apply()
        check(grade_cap("stat") is None and _zz_d and _zz_got[0] > 0 and control <= 100 and _zz_got[1] == night_gojo_gain()[1],
              "F: at Special Grade (grade_cap is None) nothing raises; Control stops at 100, the reserve has no ceiling",
              (_zz_d, _zz_got, control))

        ## night_dev keeps every button a None
        zz_n_fix("rich")
        check(night_dev("gojo") is None and night_dev("rest") is None and night_dev("market") is None and night_dev("?") is None
              and night_set_cost("out") is None and night_set_cost("?") is None,
              "F: night_dev() and night_set_cost() return None for every kind")
        check(night_gojo_day == day and night_cost_day == day + 1 and has_flag("market_found")
              and char_location("gojo", PERIODS[-1]) == NIGHT_GOJO["place"],
              "F: night_dev: the invitation is for today (Gojo on the ridge at Night), tomorrow has a cost, the market is found",
              (night_gojo_day, night_cost_kind, night_cost_day))

    ## The ceiling cases, with the real best day measured from the same fixture.
    python:
        zz_n.g_cases = [("g4", 40), ("g3", 55)]
    while zz_n.g_cases:
        python:
            zz_n.g_case = zz_n.g_cases.pop(0)
            zz_n_fix("rich", grade=zz_n.g_case[0], control=zz_n.g_case[1])
            ce_max = grade_cap("reserve")
            ce = ce_max
            gojo_in = True
            here = NIGHT_GOJO["place"]
            zz_n.g_fix = zz_n_snapshot()
            zz_n.g_c0, zz_n.g_r0 = control, ce_max
            zz_n.keep["due"] = night_gojo_due()
            zz_n.plan = [("hold",), ("lesson",)] + [("train", NIGHT_GOJO["place"])] * (len(PERIODS) - 1)
            zz_n_play()
        call zz_n_run
        python:
            zz_n.keep["real"] = (control - zz_n.g_c0, ce_max - zz_n.g_r0)
            zz_n_restore(zz_n.g_fix)
            gojo_in = True
            period = PERIODS[-1]
            night_dev("gojo")
        call sb_do_night_gojo
        python:
            zz_n_stop()
            _zz_g, _zz_c = zz_n.g_case
            _zz_first = (control, ce_max)
            _zz_rest = not night_can_work()
            ## a second night on the same fixture
            gojo_in = True
            night_gojo_last = -99
            _zz_due2 = night_gojo_due()
            _zz_add2 = night_gojo_apply()
            check(zz_n.keep["due"] and zz_n.keep["real"] == (0, 0)
                  and _zz_first == (GRADES[_zz_g]["stat"] + NIGHT_GOJO["past_cap"], GRADES[_zz_g]["reserve"] + NIGHT_GOJO["reserve_over"])
                  and _zz_rest and not _zz_due2 and _zz_add2 == (0, 0),
                  "F: %s, Control %d at both ceilings: a real lesson day gives 0, the night is due and leaves Control exactly 6 "
                  "and the reserve exactly 3 above their ceilings (%d, %d); a second night adds nothing and is not offered"
                  % (grade_label(_zz_g), _zz_c, _zz_first[0], _zz_first[1]),
                  (zz_n.keep["due"], zz_n.keep["real"], _zz_first, _zz_rest, _zz_due2, _zz_add2))

    ## An invitation day, through new_day().
    python:
        zz_n_fix("rich", control=30)
        _zz_d = day + 1
        while not gojo_in_on(_zz_d):
            _zz_d += 1
        day = _zz_d - 1
        del zz_n.toasts[:]
        new_day()
        _zz_t = [t for t in zz_n.toasts if t[0] == "Gojo: the ridge, tonight"]
        night_gojo_morning()
        _zz_t2 = [t for t in zz_n.toasts if t[0] == "Gojo: the ridge, tonight"]
        check(gojo_in_today() and night_gojo_day == day and night_marks() == {"mountain": "moon"}
              and len(_zz_t) == 1 and len(_zz_t2) == 1 and "night_toast" in actions_today
              and char_location("gojo", PERIODS[-1]) == "ridge",
              "F: on an invitation day night_marks() is {'mountain': 'moon'}, the morning toast is queued once, and Gojo is on the ridge at Night",
              (night_gojo_day, night_marks(), _zz_t2, char_location("gojo", PERIODS[-1])))
        here = "ridge"
        _zz_early = night_gojo_ok()
        period = PERIODS[-1]
        _zz_rail = rail_actions("ridge")
        _zz_row = [r for r in _zz_rail if r[0] == "night_gojo"]
        check(not _zz_early and night_gojo_ok() and len(_zz_row) == 1 and _zz_row[0][5] is True and _zz_row[0][3] == 1
              and _zz_row[0][1] == "Train until morning" and "gojo" in who_is_here("ridge"),
              "F: that Night the ridge's column has a gold 'Train until morning' (cost 1, allowed by NIGHT_OK); not before Night",
              _zz_rail[:3])
        here = "forest"
        check(not night_gojo_ok() and "night_gojo" not in zz_n_ids(place_actions("forest")), "F: ...and only on the ridge")
        here = "ridge"
        new_day()
        check(night_marks() == {} and not night_gojo_ok(), "F: the next day the mark is gone")
        note("F: wp1_world.rpy", "its schedule regression is run as its own harness; it passes unchanged with this package (see the report)")
        note("F: the map's moon badge and the night button", "drawn by P1 from night_marks() and night_out_ok() (7.3: checked in p2_map / P8)")

    scene expression graded_bg("ridge", "Night")
    python:
        zz_n_fix("rich", control=30, here="ridge", period=PERIODS[-1])
        night_dev("gojo")
        toast_clear()
        renpy.show_screen("sb_place")
        _zz_r = zz_n_rets("sb_place")
        check(("act", "night_gojo") in _zz_r and ("act", "night_bed") in _zz_r,
              "F: the place view on the ridge that Night offers Train until morning and Go to bed", _zz_r)
        shot("night_gojo_offer")
        renpy.hide_screen("sb_place")
        objective_leave()

    ## "Not tonight."
    python:
        zz_n.keep["st"] = (day, control, ce_max, here)
        zz_n.picks = ["Not tonight."]
        del zz_n.menus[:]
        zz_n_play(menus=True)
    call sb_do_night_gojo
    python:
        zz_n_stop()
        check(zz_n.keep["st"] == (day, control, ce_max, here) and night_can_work() and len(zz_n.menus) == 1
              and zz_n.menus[0][1] == "Not tonight.",
              "F: 'Not tonight.' at the Gojo night's menu changes nothing", (zz_n.menus, day, control))

    ############################################################################
    ## G. The owner's sentence
    ############################################################################
    python:
        ## (4) night_step against gain itself (Special Grade: no ceiling in the way)
        zz_n_fix("rich", grade="sp")
        _zz_bad = []
        for _zz_c in range(0, 100):
            for _zz_a in (2, 4, 5):
                control = _zz_c
                gain("control", _zz_a, quiet=True)
                if control - _zz_c != night_step(_zz_c, _zz_a):
                    _zz_bad.append((_zz_c, _zz_a, control - _zz_c, night_step(_zz_c, _zz_a)))
        check(not _zz_bad and night_step(85, 4) == 1 and night_step(60, 4) == 2 and night_step(59, 4) == 4,
              "G: (4) night_step equals what gain really adds for every Control from 0 to 99 and amounts 2, 4 and 5 "
              "(both cuts compound at 85)", _zz_bad[:6])
        _zz_best = []
        for _zz_c in (30, 55, 70):
            control = _zz_c
            _zz_best.append(night_day_best())
        check(_zz_best == [23, 16, 12], "G: night_day_best() is 23 from Control 30, 16 from 55, 12 from 70 (the plan's figures)", _zz_best)
        control = 30
        check(night_gojo_gain() == (29, 12), "G: night_gojo_gain() from Control 30 is (29, 12)", night_gojo_gain())
        toast_clear()

        zz_n.g_cases = [(c, s) for s in (True, False) for c in (30, 58, 60, 80)]
        zz_n.days = 0
        zz_n_play()

    while zz_n.g_cases:
        $ zz_n.g_case = zz_n.g_cases.pop(0)
        $ zz_n_g_setup()
        while zz_n.g_days:
            $ zz_n_g_begin()
            call zz_n_run
            $ zz_n_g_end()
        $ zz_n_g_night_begin()
        call sb_do_night_gojo
        $ zz_n_g_verdict()

    python:
        zz_n_stop()
        note("G: real days measured", "%d days of training through sb_do_train, sb_do_hold and sb_activity (the lesson, the spars)" % zz_n.days)

    ############################################################################
    ## H. One point of room (past_cap 0)
    ############################################################################
    python:
        ## Find a Control with exactly night_day_best() + 1 of room, and one
        ## with exactly night_day_best(), under some grade's ceiling.
        zz_n.keep["h"] = None
        for _zz_g in ZZ_N_GRADES[:-1]:
            _zz_ceil = GRADES[_zz_g]["stat"]
            _zz_one = _zz_none = None
            for _zz_c in range(_zz_ceil - 1, 0, -1):
                control = _zz_c
                _zz_b = night_day_best()
                if _zz_one is None and _zz_ceil - _zz_c == _zz_b + 1:
                    _zz_one = _zz_c
                if _zz_none is None and _zz_ceil - _zz_c == _zz_b:
                    _zz_none = _zz_c
            if _zz_one is not None and _zz_none is not None:
                zz_n.keep["h"] = (_zz_g, _zz_one, _zz_none)
                break
        check(zz_n.keep["h"] is not None, "H: a Control with exactly night_day_best() + 1 of room exists", zz_n.keep["h"])
        _zz_g, _zz_one, _zz_none = zz_n.keep["h"]
        zz_n_fix("rich", grade=_zz_g, control=_zz_none, period=PERIODS[-1], here=NIGHT_GOJO["place"])
        NIGHT_GOJO["past_cap"] = 0
        gojo_in = True
        _zz_not = night_gojo_due()
        zz_n_fix("rich", grade=_zz_g, control=_zz_one, period=PERIODS[-1], here=NIGHT_GOJO["place"])
        NIGHT_GOJO["past_cap"] = 0
        gojo_in = True
        zz_n.keep["h_due"] = night_gojo_due()
        zz_n.keep["h_not"] = _zz_not
        zz_n.keep["h_best"] = night_day_best()
        zz_n.keep["h_c0"] = control
        night_gojo_invite()
        zz_n_play()
    call sb_do_night_gojo
    python:
        zz_n_stop()
        _zz_g, _zz_one, _zz_none = zz_n.keep["h"]
        _zz_gain = control - zz_n.keep["h_c0"]
        check(zz_n.keep["h_due"] and not zz_n.keep["h_not"] and _zz_gain == zz_n.keep["h_best"] + 1
              and control == GRADES[_zz_g]["stat"] and not night_can_work(),
              "H: past_cap 0, %s: with night_day_best() + 1 of room (Control %d) the night is offered, gains that one point more "
              "than the clipped day (+%d) and sets its cost; with night_day_best() of room (Control %d) it is not offered"
              % (grade_label(_zz_g), _zz_one, _zz_gain, _zz_none),
              (zz_n.keep["h_due"], zz_n.keep["h_not"], _zz_gain, zz_n.keep["h_best"], control))
        NIGHT_GOJO["past_cap"] = ZZ_N_PAST

    ## No gain, no cost: Control already 6 above the ceiling, the reserve 3 above.
    python:
        zz_n_fix("rich", grade="g3", control=GRADES["g3"]["stat"] + ZZ_N_PAST, period=PERIODS[-1], here=NIGHT_GOJO["place"])
        ce_max = GRADES["g3"]["reserve"] + NIGHT_GOJO["reserve_over"]
        night_gojo_invite()
        zz_n_play()
    call sb_do_night_gojo
    python:
        zz_n_stop()
        check(night_can_work() and night_tag() == "" and here == "dorm",
              "H: a night whose gains come to nothing sets no cost", (night_cost_kind, night_cost_day, day))

    ############################################################################
    ## I. The day after
    ############################################################################
    python:
        zz_n_fix("rich", control=30, period=PERIODS[-1], here=NIGHT_GOJO["place"])
        gojo_in = True
        night_gojo_invite()
        zz_n.keep["avail"] = builtins.set(missions_list(status="available"))
        zz_n.keep["day"] = day
        del zz_n.toasts[:]
        zz_n_play()
    call sb_do_night_gojo
    python:
        zz_n_stop()
        check(day == zz_n.keep["day"] + 1 and here == "dorm" and period == PERIODS[0] and not night_can_work()
              and night_tag() == NIGHT_TAGS["gojo"] and night_block_reason() == NIGHT_REST_REASON
              and not night_pending() and night_gojo_last == zz_n.keep["day"],
              "I: the day after: I wake in my room, night_can_work() is False, night_tag() and night_block_reason() are non-empty",
              (day, here, night_tag(), night_block_reason()))
        check((NIGHT_TAGS["gojo"], "info") in zz_n.toasts and len([t for t in zz_n.toasts if "A night on the ridge" in t[0]]) == 1,
              "I: one toast gives the night's totals and one says what today costs", zz_n.toasts)

        ## the column and the hotspots, every room, every period
        _zz_bad = []
        _zz_hot = 0
        for _zz_l in LOC_ORDER:
            here = _zz_l
            for _zz_per in PERIODS:
                period = _zz_per
                for _zz_r in rail_actions(_zz_l):
                    if _zz_r[0] in NIGHT_REST_BLOCKS:
                        _zz_bad.append(("rail", _zz_l, _zz_per, _zz_r[0]))
                _zz_spots = zz_with(dict(view_person_rects=lambda loc: []), lambda: hot_spots_for(_zz_l))
                for _zz_h in _zz_spots:
                    _zz_hot += 1
                    if _zz_h["act"] in NIGHT_REST_BLOCKS:
                        _zz_bad.append(("hot", _zz_l, _zz_per, _zz_h["id"]))
        check(not _zz_bad, "I: no id in NIGHT_REST_BLOCKS is offered in any column or hotspot (rail_actions, hot_spots_for; "
              "%d rooms x %d periods)" % (len(LOC_ORDER), len(PERIODS)), _zz_bad[:6])

        ## the person view
        _zz_bad = []
        _zz_offer = dict(missions_with=lambda who, loc=None: ["cm_ijichi_1"])
        for _zz_w in ROSTER_ORDER:
            for _zz_l in LOC_ORDER:
                here = _zz_l
                for _zz_per in PERIODS:
                    period = _zz_per
                    for _zz_c in zz_with(_zz_offer, lambda: person_choices(_zz_w, _zz_l)):
                        if _zz_c["kind"] == "mission" or (_zz_c["kind"] == "do" and _zz_c["id"] in NIGHT_REST_BLOCKS):
                            _zz_bad.append((_zz_w, _zz_l, _zz_per, _zz_c["id"]))
                    for _zz_a in NIGHT_REST_BLOCKS:
                        if _zz_a in ACT_BY_ID and activity_state(ACT_BY_ID[_zz_a], _zz_w, _zz_l)[0]:
                            _zz_bad.append(("state", _zz_w, _zz_l, _zz_per, _zz_a))
        check(not _zz_bad, "I: no person view offers train, lesson or swim, or a mission (person_choices, activity_state; "
              "every person, room and period)", _zz_bad[:6])

        ## the same three, each where it is on offer on an ordinary day
        _zz_rows = (("train", "maki", "dojo", "Morning"), ("lesson", "gojo", "gojo_office", "Morning"),
                    ("swim", "yuji", "riverside", "Noon"))
        _zz_rest = []
        for _zz_a, _zz_w, _zz_l, _zz_per in _zz_rows:
            here, period, gojo_in = _zz_l, _zz_per, True
            _zz_rest.append(activity_state(ACT_BY_ID[_zz_a], _zz_w, _zz_l))
        _zz_kind, _zz_cday = night_cost_kind, night_cost_day
        night_cost_kind = ""
        _zz_plain = []
        for _zz_a, _zz_w, _zz_l, _zz_per in _zz_rows:
            here, period, gojo_in = _zz_l, _zz_per, True
            _zz_plain.append(activity_state(ACT_BY_ID[_zz_a], _zz_w, _zz_l))
        _zz_hot_plain = zz_with(dict(view_person_rects=lambda loc: []), lambda: [h["act"] for h in hot_spots_for("training")])
        night_cost_kind, night_cost_day = _zz_kind, _zz_cday
        _zz_hot_rest = zz_with(dict(view_person_rects=lambda loc: []), lambda: [h["act"] for h in hot_spots_for("training")])
        check(all(s == (True, None) for s in _zz_plain) and all(s == (False, NIGHT_REST_REASON) for s in _zz_rest)
              and "train" in _zz_hot_plain and "train" not in _zz_hot_rest,
              "I: Train together, the lesson and Swim together are refused with the night's reason, and the train hotspot is gone, "
              "exactly where an ordinary day offers them", (_zz_plain, _zz_rest, _zz_hot_plain, _zz_hot_rest))

        ## the board
        here, period = "utahime_office", "Morning"
        _zz_offers = board_generate()
        _zz_o = (_zz_offers[0] if isinstance(_zz_offers, (list, tuple)) and _zz_offers else (board_offers[0] if board_offers else {}))
        check(board_take_reason(_zz_o) == NIGHT_REST_REASON and board_refusal(_zz_o, "yuji") == NIGHT_REST_REASON,
              "I: board_take_reason and board_refusal give the night's reason", (board_take_reason(_zz_o),))

        ## what stays
        here, period = "dorm", "Morning"
        _zz_dorm = zz_n_ids(rail_actions("dorm"))
        here = "cafeteria"
        _zz_caf = zz_n_ids(rail_actions("cafeteria"))
        here, period = "classroom", "Noon"
        _zz_study = activity_state(ACT_BY_ID["study"], "megumi", "classroom")
        _zz_talk = [c["id"] for c in person_choices("megumi", "classroom")]
        check("study" in _zz_dorm and "sleep" in _zz_dorm and "eat" in _zz_caf and _zz_study == (True, None) and "talk" in _zz_talk,
              "I: study, eat and talk are still offered", (_zz_dorm, _zz_caf, _zz_study, _zz_talk))

    ## no mission button in the place view
    scene expression graded_bg("gate", "Morning")
    python:
        here, period = "gate", "Morning"
        zz_n.keep["mh"] = store.missions_here
        store.missions_here = lambda loc: ["cm_ijichi_1"]
        renpy.show_screen("sb_place")
        _zz_rest = [r for r in zz_n_rets("sb_place") if isinstance(r, tuple) and r and r[0] == "mission"]
        shot("rest_day_place")
        _zz_kind = night_cost_kind
        night_cost_kind = ""
        renpy.restart_interaction()
        _zz_plain = [r for r in zz_n_rets("sb_place") if isinstance(r, tuple) and r and r[0] == "mission"]
        period = PERIODS[-1]
        _zz_night = [r for r in zz_n_rets("sb_place") if isinstance(r, tuple) and r and r[0] == "mission"]
        period = "Morning"
        night_cost_kind = _zz_kind
        renpy.hide_screen("sb_place")
        objective_leave()
        store.missions_here = zz_n.keep["mh"]
        check(_zz_rest == [] and _zz_plain == [("mission", "cm_ijichi_1")] and _zz_night == [],
              "I: no mission button in the place view on a rest day (an offered cm_ijichi_1 shows on an ordinary morning, "
              "and not at Night: it costs 2)", (_zz_rest, _zz_plain, _zz_night))

        ## a waiting story beat still plays
        _zz_ev = [e for e in EVENTS if e["label"] == "st_second_years"][0]
        done_events.discard("st_second_years")
        here, period = "courtyard", "Afternoon"
        _zz_beat = zz_with(dict(event_allowed=lambda e: e["label"] == "st_second_years"), lambda: pick_event("story", loc=here))
        check(_zz_beat is not None and _zz_beat["label"] == "st_second_years" and not night_can_work(),
              "I: pick_event('story') still returns a waiting beat on a rest day", _zz_beat and _zz_beat["label"])
        done_events.add("st_second_years")

        ## two days later, and the day after that
        here, period = "dorm", PERIODS[-1]
        mission_cache_clear()
        new_day()
        mission_cache_clear()
        _zz_avail = builtins.set(missions_list(status="available"))
        check(day == zz_n.keep["day"] + 2 and night_can_work() and night_tag() == "" and night_block_reason() == ""
              and night_cost_kind == "" and night_cost_day == 0,
              "I: the day after that, all clear", (night_cost_kind, night_cost_day))
        check(_zz_avail == zz_n.keep["avail"],
              "I: the missions available two days later are the ones available before the night (nothing was missed)",
              (builtins.sorted(zz_n.keep["avail"] - _zz_avail), builtins.sorted(_zz_avail - zz_n.keep["avail"])))
        here = "training"
        period = "Morning"
        check("train" in zz_n_ids(place_actions("training")) and activity_state(ACT_BY_ID["train"], "maki", "training")[0] in (True, False)
              and "hold" in zz_n_ids(night_filter_actions("training", place_actions("training"))),
              "I: ...and Train and Hold the hour are back")
        note("I: the Library shelf and the first catch", "they test night_can_work() themselves in P6's files (7.3: checked in p2_rooms)")

    ############################################################################
    ## J. The night in Tokyo
    ############################################################################
    python:
        zz_n_fix("rich", grade="g3", period="Evening", here="gate", yen=2000)
        check(night_out_ok("shibuya") == (True, "") and not night_out_ok("shinjuku")[0] and night_out_ok("shinjuku")[1] != ""
              and night_out_ok("harajuku") == (False, ""),
              "J: night_out_ok: Shibuya is open in the Evening; Shinjuku is closed below Grade 2, with a reason; "
              "a district with no night out is hidden", (night_out_ok("shibuya"), night_out_ok("shinjuku"), night_out_ok("harajuku")))
        period = "Afternoon"
        _zz_aft = night_out_ok("shibuya")
        period = PERIODS[-1]
        _zz_ngt = night_out_ok("shibuya")
        flags.discard("ijichi_rides")
        _zz_shut = night_out_ok("shibuya")
        flag("ijichi_rides")
        promote("mc", "g2", quiet=True)
        check(_zz_aft == (False, "") and _zz_ngt == (True, "") and not _zz_shut[0] and night_out_ok("shinjuku") == (True, ""),
              "J: night_out_ok: hidden before the Evening, open at Night, closed while Tokyo is; Shinjuku opens at Grade 2",
              (_zz_aft, _zz_ngt, _zz_shut))

        zz_n_fix("rich", grade="g3", period="Evening", here="gate", yen=2000)
        companion = "yuji"
        zz_n.keep["st"] = (day, bonds["yuji"], builtins.set(bound_specials))
        zz_n.keep["t"] = len(zz_n.texts)
        del zz_n.labels[:]
        del zz_n.menus[:]
        del zz_n.toasts[:]
        zz_n.market_plan = None
        zz_n.market_seen = 0
        zz_n_play()
    call night_out("shibuya")
    python:
        zz_n_stop()
        _zz_day, _zz_bond, _zz_bs = zz_n.keep["st"]
        check(yen == 2000 - NIGHT_OUT["cover"] and yen == 500 and here == "dorm" and day == _zz_day + 1 and period == PERIODS[0]
              and stamina == int(stamina_max * NIGHT_OUT["stamina"]) and stamina * 2 == stamina_max
              and ce == int(ce_max * NIGHT_OUT["ce"]) and has_flag("market_found") and night_can_work()
              and night_tag() == NIGHT_TAGS["out"] and not night_pending(),
              "J: night_out('shibuya') under autoplay with ¥2,000: yen down 1,500, in my room, day +1, stamina at half, "
              "cursed energy at 70%, market_found set, night_can_work() True, a Rough morning",
              (yen, here, day, stamina, stamina_max, ce, ce_max, night_tag()))
        check(bonds["yuji"] == _zz_bond + NIGHT_OUT["bond"] and companion is None,
              "J: whoever came along gains Bond +%d" % NIGHT_OUT["bond"], (bonds["yuji"], _zz_bond))
        check(len(zz_n_said(zz_n.keep["t"], "pulls me onto the floor")) == 1
              and zz_n_said(zz_n.keep["t"], "finds a wall to stand against") == [],
              "J: Yuji is one of the two who pull me onto the floor")
        check("market_open" not in zz_n.labels and zz_n.menus == [] and zz_n.market_seen == 0
              and len(zz_n_said(zz_n.keep["t"], "I take the wrong stairs")) == 1,
              "J: autoplay takes Home at the second (after-club) menu: the market is found, not opened", (zz_n.menus, zz_n.labels[-6:]))
        check((NIGHT_TAGS["out"], "info") in zz_n.toasts, "J: the morning toast says Rough morning", zz_n.toasts)

        ## refused the next night
        period = "Evening"
        yen = 5000
        _zz_ok = night_out_ok("shibuya")
        zz_n.keep["st"] = (day, yen, here)
        zz_n_play()
    call night_out("shibuya")
    python:
        zz_n_stop()
        check(_zz_ok == (False, "Not two nights running") and zz_n.keep["st"] == (day, yen, here),
              "J: refused the next night ('Not two nights running'): the label returns at once", (_zz_ok, day, yen, here))
        new_day()
        period = "Evening"
        check(night_out_ok("shibuya") == (True, "") and night_tag() == "" and night_cost_kind == "",
              "J: ...and allowed again the night after; the rough morning has cleared", (night_out_ok("shibuya"), night_cost_kind))

        ## ¥0: autoplay heads home
        zz_n_fix("rich", grade="g3", period="Evening", here="gate", yen=0)
        zz_n.keep["st"] = (day, yen, here, period)
        zz_n_play()
    call night_out("shibuya")
    python:
        zz_n_stop()
        check(zz_n.keep["st"] == (day, yen, here, period) and night_cost_kind == "" and night_out_last == -99
              and not has_flag("market_found"),
              "J: with ¥0 autoplay heads home: yen, day and here unchanged, no cost set", (day, yen, here, night_cost_kind))

        ## the menus themselves: not enough yen, then home
        zz_n.picks = ["Not enough yen", "Head home"]
        del zz_n.menus[:]
        zz_n.keep["t"] = len(zz_n.texts)
        zz_n_play(menus=True)
    call night_out("shibuya")
    python:
        zz_n_stop()
        check(len(zz_n.menus) == 2 and zz_n.menus[0][1].endswith("Not enough yen") and zz_n.menus[1][1] == "Head home"
              and not any(c == "The Black Market" for c in zz_n.menus[0][0])
              and not any(c.startswith("The club") and "Not enough" not in c for c in zz_n.menus[0][0])
              and len(zz_n_said(zz_n.keep["t"], "I count what's in my wallet twice")) == 1
              and zz_n.keep["st"] == (day, yen, here, period) and night_cost_kind == "",
              "J: with ¥0 the club reads 'Not enough yen' and choosing it only says a line; Head home charges nothing; "
              "the market is not on the menu before it is found", zz_n.menus)

    ## The arrival menu as the player sees it (a screenshot; the real choice
    ## screen, whatever autoplay then picks).
    python:
        zz_n_fix("rich", grade="g3", period="Evening", here="gate", yen=2000)
        flag("market_found")
        zz_n.picks = []
        zz_n.market_plan = []
        zz_n.snap = ("after dark.", "night_out_menu")
        zz_n_play(menus=True)
    call night_out("shibuya")
    python:
        zz_n_stop()
        check(zz_n.snap is None, "J: the arrival menu was drawn (night_out_menu.png)")
        zz_n.snap = None
        zz_n.market_plan = None
        config.auto_choice_delay = None

        ## market_exists patched to False
        zz_n_fix("rich", grade="g3", period="Evening", here="gate", yen=2000)
        zz_n.keep["me"] = store.market_exists
        store.market_exists = lambda: False
        zz_n.picks = ["The club"]
        del zz_n.menus[:]
        del zz_n.labels[:]
        zz_n.keep["t"] = len(zz_n.texts)
        zz_n.keep["day"] = day
        zz_n_play(menus=True)
    call night_out("shibuya")
    python:
        zz_n_stop()
        store.market_exists = zz_n.keep["me"]
        check(day == zz_n.keep["day"] + 1 and yen == 500 and not has_flag("market_found")
              and zz_n_said(zz_n.keep["t"], "I take the wrong stairs") == [] and len(zz_n.menus) == 1
              and "market_open" not in zz_n.labels,
              "J: with market_exists patched to False the club night neither sets market_found nor says the stairs line, "
              "and no second menu appears", (zz_n.menus, has_flag("market_found")))

        ## the club, then the market at the second menu
        zz_n_fix("rich", grade="g3", period=PERIODS[-1], here="dorm", yen=3000)
        zz_n.picks = ["The club", "The Black Market"]
        companion = "megumi"
        zz_n.keep["mb"] = bonds["megumi"]
        zz_n.keep["t"] = len(zz_n.texts)
        zz_n.market_plan = [("buy", "first_aid"), ("close",)]
        zz_n.market_seen = 0
        del zz_n.menus[:]
        del zz_n.labels[:]
        zz_n.keep["day"] = day
        zz_n.keep["price"] = market_row("first_aid")["price"]
        zz_n_play(menus=True)
    call night_out("shibuya")
    python:
        zz_n_stop()
        zz_n.market_plan = None
        check(len(zz_n_said(zz_n.keep["t"], "finds a wall to stand against")) == 1
              and zz_n_said(zz_n.keep["t"], "pulls me onto the floor") == []
              and bonds["megumi"] == zz_n.keep["mb"] + NIGHT_OUT["bond"],
              "J: anyone else who comes along gets the quiet line, and the same Bond +%d" % NIGHT_OUT["bond"],
              (bonds["megumi"], zz_n.keep["mb"]))
        check(len(zz_n.menus) == 2 and zz_n.menus[1][0] == ["The Black Market", "Home"] and zz_n.menus[1][1] == "The Black Market"
              and zz_n.labels.count("market_open") == 1 and zz_n.market_seen == 2
              and yen == 3000 - NIGHT_OUT["cover"] - zz_n.keep["price"] and item_count("first_aid") == 1
              and day == zz_n.keep["day"] + 1 and here == "dorm" and night_tag() == NIGHT_TAGS["out"],
              "J: the first club night in Shibuya finds the stairs; the second menu is The Black Market / Home; the market opens, "
              "a kit is bought through the screen, and the night still ends in my room", (zz_n.menus, yen, item_count("first_aid")))

        ## the market alone
        new_day()
        new_day()
        period = "Evening"
        zz_n.picks = ["The Black Market"]
        zz_n.market_plan = []
        zz_n.market_seen = 0
        del zz_n.menus[:]
        zz_n.keep["st"] = (day, yen)
        zz_n_play(menus=True)
    call night_out("shibuya")
    python:
        zz_n_stop()
        zz_n.market_plan = None
        _zz_day, _zz_yen = zz_n.keep["st"]
        check(len(zz_n.menus) == 1 and "The Black Market" in zz_n.menus[0][0] and zz_n.market_seen == 1 and yen == _zz_yen
              and day == _zz_day + 1 and here == "dorm" and night_tag() == NIGHT_TAGS["out"] and night_out_last == _zz_day
              and stamina == int(stamina_max * NIGHT_OUT["stamina"]),
              "J: choosing the market alone: no yen taken at the door, the day rolls, the cost is set", (zz_n.menus, yen, day, night_tag()))

        ## the market is Shibuya's only
        zz_n_fix("rich", grade="g2", period="Evening", here="gate", yen=0)
        flag("market_found")
        check(night_market_here("shibuya") and not night_market_here("shinjuku") and NIGHT_OUT["market"] == "shibuya",
              "J: the Black Market is in Shibuya, not Shinjuku")
        check(night_bg("shibuya") == DISTRICTS["shibuya"]["bg"] and renpy.has_image(night_bg("shinjuku"), exact=True),
              "J: with no night picture painted the district's own picture stands in (drop-in: 'bg shibuya night')", night_bg("shibuya"))

    ############################################################################
    ## K. The market
    ############################################################################
    python:
        zz_n_fix("rich", grade="g3", yen=0)
        _zz_before = (yen, dict(inventory), builtins.set(market_bought), builtins.set(bound_specials))
        _zz_no = [market_buy(r["item"]) for r in MARKET_STOCK] + [market_buy("unending_moment"), market_buy("nothing")]
        check(not any(_zz_no) and all(r is False for r in _zz_no)
              and _zz_before == (yen, dict(inventory), builtins.set(market_bought), builtins.set(bound_specials))
              and all(r[2] == "poor" and r[3] == "Can't afford it" for r in market_rows()),
              "K: market_buy returns False and changes nothing when yen < price (and for an item that isn't stock)", (_zz_no, market_rows()))

        yen = 100000
        _zz_bs = builtins.set(bound_specials)
        _zz_bad = []
        for _zz_r in MARKET_STOCK:
            _zz_y, _zz_n = yen, item_count(_zz_r["item"])
            _zz_ok = market_buy(_zz_r["item"])
            if _zz_ok is not True or yen != _zz_y - _zz_r["price"] or item_count(_zz_r["item"]) != _zz_n + 1:
                _zz_bad.append((_zz_r["item"], _zz_ok, yen, item_count(_zz_r["item"])))
        check(not _zz_bad, "K: market_buy returns True and moves the yen and the item, for every stock row", _zz_bad)
        _zz_rows = dict((r[0], r) for r in market_rows())
        _zz_y = yen
        _zz_again = [market_buy(r["item"]) for r in MARKET_STOCK if r["once"]]
        check(all(_zz_rows[r["item"]][2:] == ("sold", "Sold") for r in MARKET_STOCK if r["once"])
              and all(_zz_rows[r["item"]][2] == "buy" for r in MARKET_STOCK if not r["once"])
              and not any(_zz_again) and yen == _zz_y
              and market_bought == builtins.set(r["item"] for r in MARKET_STOCK if r["once"]),
              "K: a once-only row then reads 'Sold' and can't be bought again; sealing talismans and first aid can", market_rows())
        check(market_buy("first_aid") and item_count("first_aid") == 2, "K: a supply stacks: a second kit is a second kit")
        check(bound_specials == _zz_bs and not any(ITEMS[r["item"]]["special"] for r in MARKET_STOCK)
              and not any(i in [r["item"] for r in MARKET_STOCK] for i in ("unending_moment", "the_zone", "finger_wrap")),
              "K: MARKET_STOCK holds no item with special=True, and bound_specials is unchanged by any purchase")

        ## prices (D29), against the board's own table
        _zz_bad = []
        for _zz_r in MARKET_STOCK:
            _zz_g = ITEMS[_zz_r["item"]]["grade"]
            _zz_cap = (BOARD_YEN["g4"][0] if _zz_g is None else 3 * BOARD_YEN[_zz_g][1])
            if market_price_cap(_zz_r["item"]) != _zz_cap or not 0 < _zz_r["price"] <= _zz_cap:
                _zz_bad.append((_zz_r["item"], _zz_r["price"], _zz_cap))
        _zz_caps = (market_price_cap("second_wind"), market_price_cap("sealing_talisman"), market_price_cap("first_aid"),
                    market_price_cap("afterglow"), market_price_cap("finger_wrap"))
        check(not _zz_bad and market_validate() == []
              and _zz_caps == (3 * BOARD_YEN["s1"][1], 3 * BOARD_YEN["g4"][1], BOARD_YEN["g4"][0], 3 * BOARD_YEN["s1"][1], 6 * BOARD_YEN["s1"][1]),
              "K: every price obeys D29's rule for its tier; the validator runs without a KeyError for s1, g4, an ungraded supply, "
              "g1 and sp", (_zz_bad, _zz_caps))
        _zz_old = MARKET_STOCK[0]["price"]
        MARKET_STOCK[0]["price"] = market_price_cap(MARKET_STOCK[0]["item"]) + 1
        _zz_over = market_validate()
        MARKET_STOCK[0]["price"] = _zz_old
        MARKET_STOCK.append(dict(item="finger_wrap", price=100, once=True))
        _zz_sp = market_validate()
        MARKET_STOCK.pop()
        check(len(_zz_over) == 1 and "above its ceiling" in _zz_over[0] and any("Special Grade" in f for f in _zz_sp)
              and market_validate() == [],
              "K: the validator reports a price above its ceiling, and a Special Grade row", (_zz_over, _zz_sp))

        ## the four talismans
        _zz_four = ("borrowed_luck", "night_eyes", "debt_marker", "second_wind")
        _zz_fields = builtins.set(("name", "kind", "grade", "special", "sealed", "stack", "desc", "effect", "fx", "source",
                                   "from_flag", "hidden"))
        check(all(i in ITEMS and ITEMS[i]["kind"] == "talisman" and ITEMS[i]["source"] == "The Black Market"
                  and not ITEMS[i]["special"] and ITEMS[i]["fx"] for i in _zz_four)
              and [ITEMS[i]["grade"] for i in _zz_four] == ["g3", "g3", "g2", "s1"]
              and all(grade_rank(ITEMS[i]["grade"]) <= grade_rank("s1") for i in _zz_four),
              "K: the four talismans are Grade 3, Grade 3, Grade 2 and Semi-Grade 1 (none above Semi-Grade 1), from The Black Market")
        check(all(ITEM_REQS.get(i) for i in _zz_four) and not [f for f in item_validate_reqs() if any(repr(i) in f for i in _zz_four)]
              and ITEM_REQS["borrowed_luck"] == [("grade", "g3"), ("stat", "insight", 30)]
              and ITEM_REQS["night_eyes"] == [("grade", "g3"), ("stat", "insight", 35)]
              and ITEM_REQS["debt_marker"] == [("grade", "g2"), ("stat", "control", 50)]
              and ITEM_REQS["second_wind"] == [("grade", "s1"), ("stat", "output", 60)],
              "K: each has its ITEM_REQS row (D27's), and the cap validator passes them", item_validate_reqs())
        check(all(builtins.set(it) == _zz_fields for it in ITEMS.values()) and len(_zz_fields) == 12,
              "K: every ITEMS record still has exactly 12 fields",
              [i for i, it in ITEMS.items() if builtins.set(it) != _zz_fields])
        note("K: putting a market talisman on through its checklist", "needs P4a's can_wear (7.3: always deferred to P8)")
        note("K: the rumour page and the review button", "P6's page and explore.rpy's button ask market_exists(), now True (7.3)")
        check(market_outfits() == [] and MARKET_OUTFITS == [], "K: the outfits shelf is empty until an outfit's sprite files exist")
        MARKET_OUTFITS.append(dict(name="A test outfit", files=["images/zz_no_such_sprite.png"]))
        _zz_none = market_outfits()
        MARKET_OUTFITS[0]["files"] = ["gui/seal_44.png"]
        _zz_some = market_outfits()
        MARKET_OUTFITS.pop()
        check(_zz_none == [] and len(_zz_some) == 1, "K: an outfit row shows only when its files exist", (_zz_none, _zz_some))

    ## the screen
    scene black
    python:
        zz_n_fix("rich", grade="g3", yen=30000)
        market_buy("borrowed_luck")
        toast_clear()
        zz_worst("market_screen", hover="market_buy_night_eyes")
        _zz_rows = market_rows()
        _zz_r = zz_n_rets("market_screen")
        _zz_want = [("close",)] + [("buy", r[0]) for r in _zz_rows if r[2] == "buy"] + [("close",)]
        check(builtins.sorted(_zz_r, key=repr) == builtins.sorted(_zz_want[1:], key=repr)
              or builtins.sorted(_zz_r, key=repr) == builtins.sorted(_zz_want, key=repr),
              "K: market_screen returns ('buy', id) for each row that can be bought, and ('close',)", _zz_r)
        _zz_texts = zz_texts("market_screen")
        check("The Black Market" in _zz_texts and "Effects wake up with the combat update." in _zz_texts
              and market_yen(yen) in _zz_texts and "Sold" in _zz_texts and "Can't afford it" in _zz_texts
              and all(ITEMS[r[0]]["name"] in _zz_texts and ITEMS[r[0]]["effect"] in _zz_texts and market_yen(r[1]) in _zz_texts
                      for r in _zz_rows),
              "K: the screen shows the header, my yen, each row's name, effect and price, 'Sold', 'Can't afford it' and the footer",
              [t for t in _zz_texts if len(t) < 40])
        _zz_close = zz_rect("market_screen", "market_close")
        _zz_buys = [zz_rect("market_screen", "market_buy_" + r[0]) for r in _zz_rows if r[2] == "buy"]
        check(_zz_close is not None and _zz_close[0] == 1590 and _zz_close[0] + _zz_close[2] == 1810
              and abs(_zz_close[1] + _zz_close[3] // 2 - 1000) <= 2,
              "K: Close sits at (1590, 1000)", _zz_close)
        check(_zz_buys and all(b is not None and b[0] >= 110 and b[0] + b[2] <= 1810 and b[1] + b[3] + 40 <= _zz_close[1] for b in _zz_buys),
              "K: every Buy button sits inside the panel, and the panel ends above Close (the last row's button is 40 px or more "
              "above it)", (_zz_buys, _zz_close))
        note("K: worst_market_screen.png", "toasts are still drawn over the market in this worktree: toast_room() is P2's "
             "(R6: they wait over the market; hand-off to P2 and P8). toast_room() here: %r" % (toast_room(),))
        renpy.hide_screen("market_screen")

        ## the checklist chips, with P4a's function stood in for
        zz_n.keep["ir"] = store.item_requirements
        store.item_requirements = lambda id: [("Grade 3", True), ("Insight 35", False)] if id in ITEM_REQS else []
        renpy.show_screen("market_screen")
        _zz_texts = zz_texts("market_screen")
        shot("market_reqs")
        check("✓ Grade 3" in _zz_texts and "Insight 35" in _zz_texts,
              "K: each talisman row shows its requirement chips, ticked or not (item_requirements stood in for)",
              [t for t in _zz_texts if len(t) < 24])
        renpy.hide_screen("market_screen")
        store.item_requirements = zz_n.keep["ir"]
        note("K: the requirement chips", "item_requirements() is P4a's (a stub returning [] in this worktree): the chips show once "
             "P4a is merged (7.3: P8)")

    ## label market_open, driven through the screen
    python:
        zz_n_fix("rich", grade="g3", yen=1000)
        zz_n.market_plan = [("buy", "first_aid"), ("buy", "night_eyes"), ("close",)]
        zz_n.market_seen = 0
        zz_n_play(menus=True)
    call market_open
    python:
        zz_n_stop()
        zz_n.market_plan = None
        check(zz_n.market_seen == 3 and yen == 1000 - market_row("first_aid")["price"] and item_count("first_aid") == 1
              and not has_item("night_eyes"),
              "K: label market_open loops until Close: a kit is bought, a row I can't afford is not", (zz_n.market_seen, yen))
        zz_n_play()
    call market_open
    python:
        zz_n_stop()
        check(True, "K: under autoplay the market closes itself (label market_open returns)")

    ############################################################################
    ## L, M
    ############################################################################
    python:
        note("L: phase1_all.rpy", "completes its 30 days with the rule on: run as its own harness (see the report); neither it nor "
             "core_flow.rpy needed an edit")

        ## M. The saved variables
        zz_n_fix("rich", grade="g3", period="Evening", yen=50000)
        night_set_cost("out")
        night_carried = "ridge"
        night_gojo_last, night_gojo_day, night_out_last = day - 3, day, day - 1
        market_buy("night_eyes")
        _zz_vals = dict((k, getattr(store, k)) for k in ZZ_N_VARS)
        _zz_back = pickle.loads(pickle.dumps(_zz_vals, pickle.HIGHEST_PROTOCOL))
        check(_zz_back == _zz_vals and all(isinstance(_zz_vals[k], (str, int)) for k in ZZ_N_VARS[:6])
              and isinstance(market_bought, (set, frozenset)) and all(isinstance(i, str) for i in market_bought),
              "M: the six night_* variables and market_bought hold plain values and pickle", _zz_vals)

        ## a replay: the memory's own scope, the seven at their defaults
        _zz_mem = MEMORIES[0]["id"] if isinstance(MEMORIES, (list, tuple)) else builtins.sorted(MEMORIES)[0]
        _zz_scope = memory_scope(_zz_mem)
        check(not any(k in _zz_scope for k in ZZ_N_VARS), "M: a replay's scope carries none of the seven (they start at their defaults)",
              [k for k in ZZ_N_VARS if k in _zz_scope])
        zz_n_restore()
        for _zz_k, _zz_v in _zz_scope.items():
            if hasattr(store, _zz_k):
                setattr(store, _zz_k, _zz_v)
        store._in_replay = "mem_play"
        here, period = "ridge", PERIODS[-1]
        _zz_acts = place_actions("ridge")
        _zz_res = (night_filter_actions("ridge", _zz_acts) is _zz_acts, night_allows("train", 1), night_blocks("train"),
                   night_can_work(), night_tag(), night_block_reason(), night_pending(), night_marks(), night_out_ok("shibuya"),
                   night_gojo_ok(), night_gojo_due())
        _zz_day = day
        new_day()
        _zz_after = (night_carried, night_cost_kind, night_cost_day, night_gojo_day, day - _zz_day)
        store._in_replay = None
        check(_zz_res == (True, True, False, True, "", "", False, {}, (False, ""), False, False)
              and _zz_after == ("", "", 0, 0, 1) and market_rows() and isinstance(night_day_best(), int),
              "M: at their defaults in a replay the rule does nothing: no filter, no pending, no cost, no invitation; "
              "new_day() leaves them alone", (_zz_res, _zz_after))
        zz_n_restore()

    $ finish()
