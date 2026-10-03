## tools/smoke/p2_hud.rpy -- P2's harness: the HUD, the icon column, the lighter
## person view and the toast lanes (docs/PHASE2_DESIGN.md section 7, "P2").
##
##   tools/smoke.sh tools/smoke/p2_hud.rpy
##
## Every acceptance bullet of P2 is a named check, in the plan's order:
##   1. the three corner buttons and the status chips beside the date
##   2. a hover label on every button, each key unique on its screen
##   3. the column offers exactly rail_actions and the missions, in every room
##      and period, with and without a companion; place_actions against the
##      baseline (tools/smoke/baseline_p0.json)
##   4. the column holds no words; nine actions clear the toast lane
##   5. the person view returns what the baseline recorded and shows no name,
##      thread pips, "Closer" or bars; at most 16 words
##   6. person_choices: at most four, Talk last, an icon on each
##   7. toast_room() over every kind of screen; toasts that wait keep
##   8. the toast lane and the banner never meet; the worst-case screenshots
##   9. ambient_of: a 2-tuple everywhere, and a caption that follows the story
## and then the stand-in path (no icon pictures), the icon names P2's files
## use, and last a save made with the objective banner drawn, loaded again
## (the banner waits for the arrival caption after a load too). Screenshots go to shots/p2_hud/: worst_sb_place.png, worst_sb_char.png
## and the others named below.
##
## The two fixtures are p2_contracts.rpy's ("fresh": day 3; "rich": day 9,
## everyone met, Grade 3), rebuilt here the same way, so the baseline's rows
## compare like for like. Records are built with their owners' functions
## (promote, board_generate), never by hand (R5).
##
## What waits for another package (7.3) is written as a NOTE:
##   - the stage's own buttons (the sprites and name tags, view_stage.rpy) get
##     their hover labels from P5;
##   - "Go to bed", the real moon chip and a Night with missions closed need
##     P4b's night rule: here they run against the stubs, with night_tag and
##     night_can_work swapped for the chip check only.

init 999 python:
    import os
    import json
    import copy
    import builtins
    import re as zz_hud_re

    ZZ_HUD_SEED = 20261001
    ZZ_HUD_FLAGS = dict(
        fresh=("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access"),
        rich=("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
              "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
              "intensive_done", "ijichi_rides"),
    )
    ZZ_HUD_BOOT = builtins.list([None])
    ZZ_HUD_WANT = builtins.list([None])     # the screen the probe waits for
    ZZ_HUD_SEEN = builtins.list()           # what the probe saw

    def zz_hud_snapshot():
        """Every store variable that has ever been set, deep-copied."""
        sd = renpy.python.store_dicts["store"]
        out = builtins.dict()
        for k in builtins.sorted(sd.ever_been_changed):
            if k.startswith("__") or k in ("_return", "_args", "_kwargs", "suppress_overlay", "_history_list"):
                continue
            if k not in sd:
                continue
            try:
                out[k] = copy.deepcopy(sd[k])
            except Exception:
                pass
        return out

    def zz_hud_fixture(kind):
        """p2_contracts.rpy's two baseline fixtures, built the same way."""
        for k, v in ZZ_HUD_BOOT[0].items():
            setattr(store, k, copy.deepcopy(v))
        mission_cache_clear()
        toast_clear()
        renpy.random.seed(ZZ_HUD_SEED)
        if kind == "fresh":
            settle(mc_name="Tester", mc_surname="Harness", day=3, period="Morning", here="courtyard")
        else:
            settle(mc_name="Tester", mc_surname="Harness", day=9, period="Morning", here="courtyard",
                   yen=5000)
            for w in ROSTER_ORDER:
                if w not in store.roster:
                    store.roster.append(w)
            for w in ROSTER_ORDER:
                store.bonds[w] = 60
                if is_romanceable(w):
                    store.affection[w] = 40
        for f in ZZ_HUD_FLAGS[kind]:
            flag(f)
        store.done_events.add("st_roll_call")
        promote("mc", "g4", quiet=True)
        if kind == "rich":
            promote("mc", "g3", quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()

    def zz_hud_quiet():
        """Nothing that moves by the wall clock: the arrival caption faded,
        the objective read, no toast."""
        ARRIVAL[0] = (store.day, store.period, store.here)
        ARRIVAL[1] = 0.0
        store.last_objective = objective_text() or ""
        OBJ_UNSEEN[0] = None
        renpy.hide_screen("objective_toast")
        toast_clear()

    def zz_hud_swap(name, fn):
        """Replace a store function; returns the original."""
        old = getattr(store, name)
        setattr(store, name, fn)
        return old

    def zz_hud_returns(d):
        """The value of every Return action under a displayable, in tree
        order, tuples as they are."""
        out = []
        seen = builtins.set()

        def each(x):
            if id(x) in seen:
                return
            seen.add(id(x))
            a = getattr(x, "action", None)
            if a is None:
                return
            for y in (a if isinstance(a, (builtins.list, builtins.tuple)) else [a]):
                if isinstance(y, Return):
                    out.append(y.value)

        if d is not None:
            d.visit_all(each)
        return out

    def zz_hud_buttons(screen):
        """[(widget, (x, y, w, h))] for every focusable widget of a shown
        screen (the screens it uses included), after a render."""
        zz_render()
        sc = renpy.get_screen(screen)
        out = []
        seen = builtins.set()
        if sc is None:
            return out
        for f in renpy.display.focus.focus_list:
            if f.screen is sc and f.widget is not None and f.x is not None and id(f.widget) not in seen:
                seen.add(id(f.widget))
                out.append((f.widget, (int(round(f.x)), int(round(f.y)), int(round(f.w)), int(round(f.h)))))
        return out

    def zz_hud_meets(a, b):
        """True when two (x, y, w, h) rectangles overlap."""
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

    def zz_hud_toasts():
        """(x, y, w, h) of the toast stack as drawn (the frames' own sizes
        from the last render, 8 px apart, under toast_room()'s corner), or
        None when none is drawn."""
        zz_render()
        sc = renpy.get_screen("toasts")
        hs = []

        def each(d):
            ws = getattr(d, "window_size", None)
            if isinstance(d, renpy.display.layout.Window) and ws and int(round(ws[0])) == 460:
                hs.append(int(round(ws[1])))

        if sc is not None:
            sc.visit_all(each)
        if not hs:
            return None
        x, y, _n = toast_room()
        return (x - 460, y, 460, sum(hs) + 8 * (len(hs) - 1))

    def zz_hud_banner():
        """(alpha, yoffset) of the objective banner's slide as drawn now, or
        None when the screen is not up."""
        zz_render()
        sc = renpy.get_screen("objective_toast")
        out = []

        def each(d):
            if isinstance(d, renpy.display.transform.ATLTransform):
                out.append((round(d.state.alpha, 2), d.state.yoffset))

        if sc is not None:
            sc.visit_all(each)
        return out[0] if out else None

    def zz_hud_tip(w):
        """A displayable's tooltip, as the engine reads it when it is focused."""
        try:
            return w._get_tooltip()
        except Exception:
            return None

    def zz_hud_wid(screen, wid):
        """The button with `id wid` on a shown screen."""
        return renpy.get_displayable(screen, wid, base=True) or renpy.get_displayable(screen, wid)

    def zz_hud_tips(screen):
        """(keys, the buttons with no tuple tooltip) for a shown screen."""
        keys, bare = [], []
        for w, r in zz_hud_buttons(screen):
            t = zz_hud_tip(w)
            if isinstance(t, builtins.tuple) and len(t) == 2 and t[0]:
                keys.append(t[1])
            else:
                bare.append((w, r))
        return keys, bare

    def zz_hud_under(screen, wid):
        """(the Text strings, the word tokens) under one displayable of a
        shown screen, icon glyphs left out of both."""
        zz_render()
        d = renpy.get_displayable(screen, wid)
        texts = []

        def each(x):
            if isinstance(x, renpy.text.text.Text) and not zz_is_glyph(x):
                texts.append(zz_text_string(x))

        if d is not None:
            d.visit_all(each)
        words = [t for s in texts for t in ZZ_TEXT_TAG.sub(" ", s.replace("{{", " ")).split() if zz_is_word(t)]
        return texts, words

    def zz_hud_images(screen):
        """The file names of every picture in a shown screen's tree."""
        out = []
        sc = renpy.get_screen(screen)

        def each(x):
            fn = getattr(x, "filename", None)
            if isinstance(fn, str):
                out.append(fn)

        if sc is not None:
            sc.visit_all(each)
        return out

    def zz_hud_noon_place(who):
        """Where the schedule has someone at Noon; the courtyard if nowhere."""
        for loc in LOC_ORDER:
            if who in who_is_here(loc, "Noon"):
                return loc
        return "courtyard"

    def zz_hud_subsequence(old, new):
        it = builtins.iter(new)
        return builtins.all(any(r == x for x in it) for r in old)

    def zz_hud_missions(loc):
        """What the column should offer as missions: missions_here(loc) as
        the night rule leaves it, worked out without rail_missions()."""
        if store.explore_mode or not night_can_work():
            return []
        out = []
        for m in missions_here(loc):
            mid = mission_view(m)[0]
            if night_allows("mission:" + mid, (MISSION_BY_ID.get(mid) or {}).get("cost", 0)):
                out.append(mid)
        return out

    def zz_hud_probe_fn():
        """The probe overlay's timer: once the wanted screen is up, record
        toast_room() and what the toasts screen draws, and end the call."""
        want = ZZ_HUD_WANT[0]
        if not want or not renpy.get_screen(want):
            return None
        ZZ_HUD_SEEN.append((want, toast_room(), len(zz_text_nodes("toasts"))))
        ZZ_HUD_WANT[0] = None
        return ("probe",)

    def zz_hud_menu_cb():
        """As an interaction starts inside the game menu's own context (the
        one the Menu button opens): record toast_room() and every toast's
        clock, then leave the menu the way its Return button does."""
        if ZZ_HUD_WANT[0] != "menu" or not getattr(renpy.context(), "_menu", False):
            return
        ZZ_HUD_WANT[0] = None
        ZZ_HUD_SEEN.append(("menu", toast_room(), [t["t_shown"] for t in TOASTQ.items],
                            bool(renpy.get_screen("menu"))))
        renpy.jump("_return")

    config.start_interact_callbacks.append(zz_hud_menu_cb)

    def zz_hud_no_art(path, *args, **kwargs):
        """renpy.loadable with every icon picture missing (the stand-in path)."""
        if builtins.str(path).startswith("images/icons/ic_"):
            return False
        return ZZ_HUD_LOADABLE[0](path, *args, **kwargs)

    ZZ_HUD_LOADABLE = builtins.list([renpy.loadable])

    ## The last section: save on the place view with the banner drawn, load,
    ## and read the banner again. It runs from a timer inside the real loop
    ## (label sandbox), because a load restarts the script where it was saved.
    ZZ_HUD_LOAD = builtins.list([0, 0, 0])      # phase, loads seen, ticks

    def zz_hud_loaded():
        if ZZ_HUD_LOAD[0]:
            ZZ_HUD_LOAD[1] += 1

    config.after_load_callbacks.append(zz_hud_loaded)

    def zz_hud_sweep():
        """Drop this harness's own scratch variables (_zz_...) from the
        store: an open file or a lambda among them cannot go into a save."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz_")]:
            delattr(store, k)

    def zz_hud_banner_now():
        """zz_hud_banner() without the render (for use inside an interaction)."""
        sc = renpy.get_screen("objective_toast")
        out = []

        def each(d):
            if isinstance(d, renpy.display.transform.ATLTransform):
                out.append((round(d.state.alpha, 2), d.state.yoffset))

        if sc is not None:
            sc.visit_all(each)
        return out[0] if out else None

    def zz_hud_load_step():
        L = ZZ_HUD_LOAD
        if not L[0] or len(renpy.game.contexts) != 1:
            return None
        L[2] += 1
        if L[2] > 75:
            check(False, "the save / load section runs to its end", (builtins.list(L), zz_hud_banner_now(), store.here))
            finish()
        b = zz_hud_banner_now()
        ## First a turn of the real loop (a person and back), so the save is
        ## made as the owner makes one: with a finished interaction behind
        ## it, which is where a load starts running from.
        if L[0] == 1:
            if renpy.get_screen("sb_place"):
                L[0] = 11
                return ("char", stage_people(store.here)[0][0])
            return None
        if L[0] == 11:
            if renpy.get_screen("sb_char"):
                L[0] = 12
                return ("cancel",)
            return None
        if not renpy.get_screen("sb_place"):
            return None
        if L[0] == 12:
            if b != (1.0, 0) or arrival_caption() is not None:
                return None
            check(True, "fixture: in the loop, back on the place view, the banner is fully drawn when the save is made")
            renpy.take_screenshot()
            renpy.save("zz_hud_banner")
            L[0], L[2] = 2, 0
            renpy.load("zz_hud_banner")
        elif L[0] == 2:
            check(L[1] == 1 and (store.day, store.period, store.here) == (9, "Noon", "cafeteria"),
                  "the save loads onto the same place view", (L[1], store.day, store.period, store.here))
            check(arrival_caption() is not None and b is not None and b[0] == 0.0,
                  "after a load the banner waits for the arrival caption again (alpha 0)", b)
            _tags = [t for t in renpy.get_showing_tags("screens") if t == "objective_toast"]
            check(len(_tags) == 1, "one banner screen after the load", _tags)
            shot("banner_after_load", wait=0)
            L[0] = 3
        elif L[0] == 3:
            if arrival_caption() is not None or b != (1.0, 0):
                return None
            check(True, "once the caption has faded after the load, the banner has slid in (alpha 1)")
            finish()
        return None

    config.overlay_screens.append("zz_hud_probe")


screen zz_hud_probe():
    zorder 200
    if ZZ_HUD_WANT[0]:
        timer 0.3 repeat True action Function(zz_hud_probe_fn)
    if ZZ_HUD_LOAD[0]:
        timer 0.4 repeat True action Function(zz_hud_load_step)


label zz_smoke:

    python:
        ZZ_HUD_BOOT[0] = zz_hud_snapshot()
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_base = None
        if _zz_root and os.path.isfile(os.path.join(_zz_root, "tools", "smoke", "baseline_p0.json")):
            with open(os.path.join(_zz_root, "tools", "smoke", "baseline_p0.json"), encoding="utf-8") as _zz_f:
                _zz_base = json.load(_zz_f)
            del _zz_f       # an open file may not reach the rollback log (the last section saves)
        check(_zz_base is not None and {"fresh", "rich", "sb_char"} <= set(_zz_base),
              "the baseline file loads (tools/smoke/baseline_p0.json)", _zz_root)

    ## --- 1. the corner buttons and the status chips ---------------------------------
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        mission_cache_clear()
        zz_hud_quiet()
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_r = [zz_rect("sb_place", w) for w in ("hud_map", "hud_journal", "hud_menu")]
        check(_zz_r == [(1668, 26, 64, 52), (1742, 26, 64, 52), (1816, 26, 64, 52)],
              "the three HUD buttons sit at x 1668 / 1742 / 1816, y 26, each 64 x 52", _zz_r)
        _zz_a = [getattr(zz_hud_wid("sb_place", w), "action", None) for w in ("hud_map", "hud_journal", "hud_menu")]
        check(isinstance(_zz_a[0], Return) and _zz_a[0].value == ("map",)
              and isinstance(_zz_a[1], Return) and _zz_a[1].value == ("journal", "people")
              and isinstance(_zz_a[2], ShowMenu),
              "they return ('map',), ('journal', 'people') and open the menu", _zz_a)
        _zz_t = [zz_hud_tip(zz_hud_wid("sb_place", w)) for w in ("hud_map", "hud_journal", "hud_menu")]
        check(_zz_t == [("Map (M)", "hud_map"), ("Journal (J)", "hud_journal"), ("Menu", "hud_menu")],
              "their hover labels read Map (M), Journal (J), Menu", _zz_t)
        check(not any(s in ("MAP", "JOURNAL", "MENU") for s in zz_texts("sb_place")),
              "the old word buttons are gone from the place view")
        check(zz_rect("sb_place", "hud_chip_moon") is None and zz_rect("sb_place", "hud_chip_stamina") is None
              and zz_rect("sb_place", "hud_chip_skip") is None, "at rest no status chip shows")

        ## All three chips, and the longest date.
        for _zz_day in range(100, 107):
            day = _zz_day
            if weekday_full() == "Wednesday":
                break
        stamina = 20
        _zz_o_tag = zz_hud_swap("night_tag", lambda: "Worn out")
        _zz_o_work = zz_hud_swap("night_can_work", lambda: False)
        _zz_o_skip = renpy.is_skipping
        renpy.is_skipping = lambda: True
        zz_hud_quiet()
        zz_render(0.2)
        _zz_date = renpy.get_displayable("sb_place", "hud_date")
        _zz_dsize = getattr(_zz_date, "window_size", None)
        _zz_chips = [zz_rect("sb_place", w) for w in ("hud_chip_moon", "hud_chip_stamina", "hud_chip_skip")]
        check(hud_date() == "Day %d · Wednesday" % _zz_day and any(hud_date() in s for s in zz_texts("sb_place")),
              "the longest date is on the chip", hud_date())
        check(_zz_dsize is not None and all(_zz_chips), "the date chip and all three status chips are drawn",
              (_zz_dsize, _zz_chips))
        if _zz_dsize is not None and all(_zz_chips):
            _zz_drect = (40, 26, int(_zz_dsize[0]), int(_zz_dsize[1]))
            check(not any(zz_hud_meets(c, _zz_drect) for c in _zz_chips)
                  and all(c[0] >= _zz_drect[0] + _zz_drect[2] + 10 for c in _zz_chips)
                  and not any(zz_hud_meets(_zz_chips[i], _zz_chips[j]) for i in range(3) for j in range(i)),
                  "with the longest date and three chips, no chip meets the date chip or another chip",
                  (_zz_drect, _zz_chips))
            check(all(c[0] + c[2] < 1330 and abs((c[1] + c[3] / 2.0) - (26 + _zz_drect[3] / 2.0)) <= 2 for c in _zz_chips),
                  "the chips sit in the date's row, well clear of the corner buttons", _zz_chips)
        _zz_t = dict((c[2], c[1]) for c in hud_chips())
        check(_zz_t == {"hud_chip_moon": u"Worn out — no missions or training today",
                        "hud_chip_stamina": "Running on empty. Eat or sleep.", "hud_chip_skip": "Skipping"},
              "the chips' hover labels (a rest day, low stamina, skipping)", _zz_t)
        check(not any("running on empty" in s for s in zz_texts("sb_place")),
              "the running-on-empty line is no longer above the actions")
        shot("hud_chips", wait=0.2)
        zz_hud_swap("night_can_work", _zz_o_work)
        zz_hud_swap("night_tag", lambda: "Rough morning")
        check(hud_chips()[0][:2] == ("moon", "Rough morning"), "a rough morning's chip says only that", hud_chips())
        zz_hud_swap("night_tag", _zz_o_tag)
        renpy.is_skipping = _zz_o_skip
        explore_mode = True
        check([c[0] for c in hud_chips()] == [], "explore mode shows no stamina chip", hud_chips())
        explore_mode = False
        note("the moon chip", "checked with night_tag() and night_can_work() swapped; P4b's real words arrive with its night rule (7.3)")

    ## --- 2. a hover label on every button, each key unique on its screen ------------
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        stamina = 20
        mission_cache_clear()
        zz_hud_quiet()
        zz_render(0.2)
        _zz_stage, _zz_extra = stage_people(here)
        _zz_keys, _zz_bare = zz_hud_tips("sb_place")
        _zz_bare_ret = [getattr(getattr(w, "action", None), "value", None) for w, r in _zz_bare]
        check(len(_zz_keys) == len(set(_zz_keys)) and len(_zz_keys) >= 5 + len(_zz_extra),
              "sb_place: every hover label's key is unique on the screen (%d buttons)" % len(_zz_keys), sorted(_zz_keys))
        check(all(isinstance(v, tuple) and v[0] == "char" and v[1] in _zz_stage for v in _zz_bare_ret)
              and len(_zz_bare) == 2 * len(_zz_stage),
              "sb_place: the only buttons without a hover label are the stage's own (sprites and name tags)",
              _zz_bare_ret)
        note("sb_place: the stage's buttons", "%d sprites and name tags (view_stage.rpy) get their hover labels from P5 (4.5, 7.3)"
             % len(_zz_bare))
        check(_zz_extra and all(("rail_more_" + w) in _zz_keys for w in _zz_extra) and "hud_dev" in _zz_keys
              and "hud_chip_stamina" in _zz_keys,
              "the overflow chip's names, Review tools and a status chip carry hover labels too", sorted(_zz_keys))
        ## The "+N" chip stands between the fourth person and the column.
        _zz_mr = [zz_rect("sb_place", "rail_more_" + w) for w in _zz_extra]
        _zz_people = view_slot_rects(here, len(_zz_stage))
        check(all(_zz_mr) and not any(zz_hud_meets(r, p) for r in _zz_mr for p in _zz_people)
              and min(r[0] for r in _zz_mr) >= RAIL_MORE_POS[0] and max(r[0] + r[2] for r in _zz_mr) <= 1700
              and max(r[1] + r[3] for r in _zz_mr) == RAIL_MORE_POS[1] == 1040,
              "the +N chip's names stand on no sprite: right of the fourth person, left of x 1700, on the bottom line",
              (_zz_mr, _zz_people))
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_char", _zz_stage[0])
        zz_render(0.5)
        _zz_keys, _zz_bare = zz_hud_tips("sb_char")
        check(not _zz_bare and len(_zz_keys) == len(set(_zz_keys)) and len(_zz_keys) >= 4,
              "sb_char: every button has a hover label with a key unique on the screen", (sorted(_zz_keys), len(_zz_bare)))
        renpy.hide_screen("sb_char")

    ## --- 3. the column offers exactly rail_actions and the missions ------------------
    python:
        _zz_seen_m = set()
        _zz_most_rows = 0
        _zz_bad = []
        _zz_n = 0
        ## By the functions, on both fixtures.
        for _zz_kind in ("fresh", "rich"):
            zz_hud_fixture(_zz_kind)
            for _zz_comp in (None, "nobara"):
                companion = _zz_comp
                for _zz_loc in LOC_ORDER:
                    for _zz_per in PERIODS:
                        period = _zz_per
                        here = _zz_loc
                        mission_cache_clear()
                        _zz_rows = rail_rows(_zz_loc)
                        _zz_n += 1
                        _zz_want = ([("mission", m) for m in zz_hud_missions(_zz_loc)]
                                    + [("act", a[0]) for a in rail_actions(_zz_loc)])
                        _zz_seen_m.update(m for k, m in _zz_want if k == "mission")
                        if [r[0] for r in _zz_rows] != _zz_want:
                            _zz_bad.append((_zz_kind, _zz_comp, _zz_loc, _zz_per, [r[0] for r in _zz_rows], _zz_want))
                        if len(set(r[5] for r in _zz_rows)) != len(_zz_rows):
                            _zz_bad.append(("ids repeat", _zz_loc, _zz_per, [r[5] for r in _zz_rows]))
                        if any(r[1] not in ICONS for r in _zz_rows):
                            _zz_bad.append(("icon", _zz_loc, _zz_per, [r[1] for r in _zz_rows]))
                        if bool(_zz_comp) != bool(_zz_rows and _zz_rows[-1][0] == ("act", "release")):
                            _zz_bad.append(("release last", _zz_kind, _zz_comp, _zz_loc, _zz_per))
                        if sorted(r for c in rail_columns(_zz_rows) for r in c) != sorted(_zz_rows):
                            _zz_bad.append(("columns lose a row", _zz_loc, _zz_per))
                        _zz_most_rows = max(_zz_most_rows, len(_zz_rows))
                        ## Two columns at most, with pictures and with stand-in
                        ## words: a third would stand on the stage (4.4).
                        for _zz_la in (ZZ_HUD_LOADABLE[0], zz_hud_no_art):
                            renpy.loadable = _zz_la
                            if len(rail_columns(_zz_rows)) > RAIL_COLUMNS:
                                _zz_bad.append(("a third column", _zz_loc, _zz_per, len(_zz_rows)))
                        renpy.loadable = ZZ_HUD_LOADABLE[0]
        check(not _zz_bad, "rail_rows: the missions first, then rail_actions in order, the release row last with a companion "
              "(%d room x period x companion x fixture)" % _zz_n, _zz_bad[:4])
        check(_zz_seen_m, "at least one room offered a mission in the column", sorted(_zz_seen_m))
        check(RAIL_COLUMNS == 2 and _zz_most_rows <= RAIL_MAX + RAIL_MAX - 1,
              "no room x period needs a third column (the most tiles anywhere: %d; room for 15)" % _zz_most_rows)

        ## By the screen itself, as drawn, on the rich fixture.
        zz_hud_fixture("rich")
        _zz_bad = []
        _zz_n = 0
        _zz_top = 1080
        _zz_gold = 0
    show screen sb_place
    python:
        for _zz_comp in (None, "nobara"):
            companion = _zz_comp
            for _zz_loc in LOC_ORDER:
                for _zz_per in PERIODS:
                    period = _zz_per
                    here = _zz_loc
                    mission_cache_clear()
                    zz_hud_quiet()
                    zz_render(0.02)
                    _zz_n += 1
                    _zz_got = zz_hud_returns(renpy.get_displayable("sb_place", "rail_column"))
                    _zz_acts = [("act", a[0]) for a in rail_actions(_zz_loc)]
                    _zz_miss = [("mission", m) for m in zz_hud_missions(_zz_loc)]
                    _zz_gold += len(_zz_miss)
                    if set(_zz_got) != set(_zz_acts + _zz_miss) or len(_zz_got) != len(_zz_acts + _zz_miss):
                        _zz_bad.append((_zz_comp, _zz_loc, _zz_per, _zz_got, _zz_acts + _zz_miss))
                    _zz_all = zz_hud_returns(renpy.get_screen("sb_place"))
                    if any(v[0] in ("act", "mission") for v in _zz_all if isinstance(v, tuple) and v not in _zz_got):
                        _zz_bad.append(("an action outside the column", _zz_loc, _zz_per, _zz_all))
        check(not _zz_bad, "sb_place, as drawn: the column's returns are exactly rail_actions and the missions "
              "(%d room x period x companion; %d gold tiles seen)" % (_zz_n, _zz_gold), _zz_bad[:3])
        check(_zz_gold > 0, "the drawn column showed a gold mission tile somewhere", _zz_gold)

        ## The release row is the last tile: the foot of the edge column.
        here = "dorm"
        period = "Morning"
        companion = "nobara"
        mission_cache_clear()
        zz_hud_quiet()
        zz_render(0.1)
        _zz_rows = rail_rows(here)
        _zz_r = [zz_rect("sb_place", r[5]) for r in _zz_rows]
        check(all(_zz_r) and _zz_r[-1] == (1808, 968, 72, 72) and _zz_rows[-1][5] == "rail_release"
              and all(r[0] == 1808 and r[2:] == (72, 72) for r in _zz_r)
              and [r[1] for r in _zz_r] == [1040 - 72 - 82 * (len(_zz_r) - 1 - i) for i in range(len(_zz_r))],
              "the column is 72 x 72 tiles at x 1808, 10 apart, ending at y 1040; 'Let them go' is the last", (_zz_r, [r[5] for r in _zz_rows]))
        check(not any("is with me" in s for s in zz_texts("sb_place")),
              "the separate 'let them go' link is gone")
        _zz_tip = zz_hud_tip(zz_hud_wid("sb_place", "rail_study"))
        check(_zz_tip == (u"Study\nInsight. Quiet. Nobody bothers me. · 1 period", "rail_study"),
              "a tile's hover label is its name, then its hint and cost", _zz_tip)
        shot("place_dorm_companion", wait=0.2)
        companion = None
        renpy.hide_screen("sb_place")

    ## place_actions against the baseline.
    python:
        if _zz_base is None:
            note("baseline", "no baseline file: the place_actions comparison was skipped")
        else:
            _zz_reg = set(a["id"] for a in PLACE_ACTIONS)
            for _zz_kind in ("fresh", "rich"):
                zz_hud_fixture(_zz_kind)
                _zz_lost = []
                _zz_extra_rows = []
                _zz_b = _zz_base[_zz_kind]["place_actions"]
                for _zz_key in sorted(_zz_b):
                    _zz_loc, _zz_per = _zz_key.split("|")
                    period = _zz_per
                    here = _zz_loc
                    mission_cache_clear()
                    _zz_new = [list(r) for r in place_actions(_zz_loc)]
                    if not zz_hud_subsequence(_zz_b[_zz_key], _zz_new):
                        _zz_lost.append((_zz_key, _zz_b[_zz_key], _zz_new))
                    _zz_extra_rows.extend((_zz_key, r[0]) for r in _zz_new if r not in _zz_b[_zz_key] and r[0] not in _zz_reg)
                check(not _zz_lost, "baseline %s: every place_actions row is still there, in the same order (%d room x period)"
                      % (_zz_kind, len(_zz_b)), _zz_lost[:3])
                check(not _zz_extra_rows, "baseline %s: any extra place_actions row is a registered place action" % _zz_kind,
                      _zz_extra_rows[:6])

    ## --- 4. no words in the column; nine actions clear the toast lane ---------------
    python:
        zz_hud_fixture("rich")
        period = "Morning"
        here = "courtyard"
        mission_cache_clear()
        zz_hud_quiet()
        _zz_pa = list(PLACE_ACTIONS)
        for _zz_i in range(6):
            register_place_action("zz_hud_%d" % _zz_i, "Harness action %d" % _zz_i, "Only in this harness.",
                                  cost=(_zz_i % 3), locs=("courtyard",))
        _zz_rows = rail_rows(here)
        check(len(_zz_rows) == 9, "fixture: nine actions in the courtyard", [r[5] for r in _zz_rows])
        _zz_words0 = gui.icon_words
        gui.icon_words = "never"
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        _zz_t, _zz_w = zz_hud_under("sb_place", "rail_column")
        check(_zz_t == [] and _zz_w == [], "with icon words off the column holds no Text but icon glyphs (zz_words is 0)", _zz_t)
        for _zz_i in range(4):
            toast("Lane test %d: a reward line long enough to wrap onto a second line" % (_zz_i + 1),
                  ("grade", "stat", "item", "info")[_zz_i])
        zz_render(0.5)
        check(len(toast_visible()) == 4 and toast_room() == (1790, 92, 4), "four toasts are up over the place view",
              (len(toast_visible()), toast_room()))
        _zz_r = [zz_rect("sb_place", r[5]) for r in _zz_rows]
        _zz_lane = (TOAST_LANE[0], TOAST_LANE[1], TOAST_LANE[2] - TOAST_LANE[0], TOAST_LANE[3] - TOAST_LANE[1])
        check(all(_zz_r) and not any(zz_hud_meets(r, _zz_lane) for r in _zz_r) and min(r[1] for r in _zz_r) >= 360,
              "nine actions, four toasts: no tile meets the toast lane and none rises above y 360", _zz_r)
        _zz_drawn = zz_hud_toasts()
        check(_zz_drawn is not None and _zz_drawn[:3] == (1330, 92, 460)
              and not any(zz_hud_meets(r, _zz_drawn) for r in _zz_r)
              and _zz_drawn[1] + _zz_drawn[3] <= RAIL_TOP_INNER,
              "no tile meets the four toasts as drawn (they end above the second column's top line, y 430)", _zz_drawn)
        _zz_xs = sorted(set(r[0] for r in _zz_r))
        check(_zz_xs == [1726, 1808] and sum(1 for r in _zz_r if r[0] == 1808) == 8
              and max(r[1] + r[3] for r in _zz_r) == 1040 and all(r[1] >= RAIL_TOP_INNER for r in _zz_r if r[0] == 1726),
              "eight tiles at the edge (x 1808 to 1880) and the ninth in a second column at x 1726 to 1798", _zz_r)
        check(_zz_rows[-1][5] == "rail_wait" and _zz_r[-1] == (1808, 968, 72, 72),
              "Wait keeps the foot of the edge column", _zz_r[-1])
        check(not any(zz_hud_meets(a, b) for i, a in enumerate(_zz_r) for b in _zz_r[:i]), "no two tiles overlap")
        check(max(r[0] + r[2] for w, r in zz_hud_buttons("sb_place") if getattr(getattr(w, "action", None), "value", ("",))[0] == "char") <= 1700,
              "the stage keeps x 40 to 1700, left of both columns")
        shot("place_nine_actions", wait=0.2)
        toast_clear()

        ## The same nine with every icon's picture missing: the words show,
        ## six to a column, and still nothing above the line.
        gui.icon_words = "auto"
        renpy.loadable = zz_hud_no_art
        check(not icon_has_art("train") and icon_words_shown("train"), "fixture: with no pictures, icons show their words")
        zz_render(0.3)
        _zz_r = [zz_rect("sb_place", r[5]) for r in _zz_rows]
        _zz_cols = rail_columns(_zz_rows)
        check(all(_zz_r) and min(r[1] for r in _zz_r) >= 360 and not any(zz_hud_meets(r, _zz_lane) for r in _zz_r)
              and max(r[1] + r[3] for r in _zz_r) == 1040 and max(len(c) for c in _zz_cols) <= RAIL_MAX_WORDS
              and all(r[1] >= RAIL_TOP_INNER for r in _zz_r if r[0] < 1808),
              "stand-in icons with their words: at most six to a column, none above y 360, clear of the toast lane",
              (_zz_r, [len(c) for c in _zz_cols]))
        check(all(r[3] <= rail_height(row[1], row[4], rail_word(row)) for r, row in zip(_zz_r, _zz_rows)),
              "rail_height() is never less than a tile's drawn height",
              [(r[3], rail_height(row[1], row[4], rail_word(row))) for r, row in zip(_zz_r, _zz_rows)])
        check(not any(zz_hud_meets(a, b) for i, a in enumerate(_zz_r) for b in _zz_r[:i]), "no two stand-in tiles overlap")
        _zz_t, _zz_w = zz_hud_under("sb_place", "rail_column")
        check("Wait" in _zz_t and u"？" not in zz_texts("sb_place"),
              "the stand-in tiles carry their words, and no icon is a question mark", _zz_t)
        check(len(set(_zz_t)) == len(_zz_rows) and all(rail_word(r) in _zz_t for r in _zz_rows)
              and "Harness action 0" in _zz_t and "Do it" not in _zz_t,
              "a tile's word is its action's own name, so no two tiles read the same", _zz_t)
        shot("place_standin_nine", wait=0.2)

        ## Fourteen tiles with long names and words showing would need a
        ## third column, on the stage: the column drops its words instead.
        for _zz_i in range(5):
            register_place_action("zz_hud_long_%d" % _zz_i, "A long harness action name number %d" % _zz_i,
                                  "Only in this harness.", cost=1, locs=("courtyard",))
        _zz_rows14 = rail_rows(here)
        _zz_cols14, _zz_words14 = rail_layout(_zz_rows14)
        check(len(_zz_rows14) == 14 and len(rail_columns(_zz_rows14)) > RAIL_COLUMNS,
              "fixture: fourteen tiles with their words would need a third column",
              [len(c) for c in rail_columns(_zz_rows14)])
        check(len(_zz_cols14) == RAIL_COLUMNS and _zz_words14 is False
              and sorted(r for c in _zz_cols14 for r in c) == sorted(_zz_rows14),
              "rail_layout: two columns, the words dropped, no tile lost", [len(c) for c in _zz_cols14])
        check(rail_layout(_zz_rows) == (rail_columns(_zz_rows), True), "rail_layout keeps the words while two columns hold them")
        zz_render(0.3)
        _zz_r14 = [zz_rect("sb_place", r[5]) for r in _zz_rows14]
        _zz_t14, _zz_w14 = zz_hud_under("sb_place", "rail_column")
        check(all(_zz_r14) and sorted(set(r[0] for r in _zz_r14)) == [1726, 1808] and _zz_w14 == []
              and all(r[3] == RAIL_TILE for r in _zz_r14) and min(r[1] for r in _zz_r14) >= 360
              and all(r[1] >= RAIL_TOP_INNER for r in _zz_r14 if r[0] == 1726)
              and not any(zz_hud_meets(a, b) for i, a in enumerate(_zz_r14) for b in _zz_r14[:i]),
              "as drawn: fourteen 72 px tiles in two columns, no words, none on the stage (x under 1726)",
              (_zz_r14, _zz_w14))
        shot("place_standin_fourteen", wait=0.2)
        gui.icon_words = "never"
        zz_render(0.2)
        _zz_t, _zz_w = zz_hud_under("sb_place", "rail_column")
        check(_zz_t == [], "stand-in icons with words off: only the kanji, which is not a word", _zz_t)
        renpy.loadable = ZZ_HUD_LOADABLE[0]
        gui.icon_words = _zz_words0
        PLACE_ACTIONS[:] = _zz_pa
        renpy.hide_screen("sb_place")

    ## --- 5. the person view ----------------------------------------------------------
    python:
        zz_hud_fixture("rich")
        _zz_now = {}
        _zz_bad = []
        _zz_most = (0, None)
        _zz_words0 = gui.icon_words
        gui.icon_words = "never"
        ZZ_HUD_WHO = builtins.list(ROSTER_ORDER)
    scene expression graded_bg()
    while ZZ_HUD_WHO:
        python:
            _zz_who = ZZ_HUD_WHO.pop(0)
            period = "Noon"
            here = zz_hud_noon_place(_zz_who)
            mission_cache_clear()
            zz_hud_quiet()
            renpy.show_screen("sb_char", _zz_who)
            zz_render(0.1)
            _zz_ret = [list(v) if isinstance(v, tuple) else v for v in zz_hud_returns(renpy.get_screen("sb_char"))]
            _zz_now[_zz_who] = dict(here=here, returns=_zz_ret)
            _zz_t = zz_texts("sb_char")
            _zz_dw = zz_hud_under("sb_char", "hud_date")[1]
            _zz_w = len(zz_words("sb_char")) - len(_zz_dw)
            if _zz_w > _zz_most[0]:
                _zz_most = (_zz_w, _zz_who)
            _zz_img = zz_hud_images("sb_char")
            _zz_bars = []
            renpy.get_screen("sb_char").visit_all(lambda d: _zz_bars.append(d) if isinstance(d, renpy.display.behavior.Bar) else None)
            if any(s in (CAST[_zz_who]["name"], CAST[_zz_who]["short"]) for s in _zz_t):
                _zz_bad.append((_zz_who, "the name"))
            if any("Closer" in s for s in _zz_t):
                _zz_bad.append((_zz_who, "Closer"))
            if any(s in ("BOND", "AFFECTION") for s in _zz_t) or _zz_bars:
                _zz_bad.append((_zz_who, "a bar"))
            if any("pip_gold" in f or "pip_off" in f for f in _zz_img):
                _zz_bad.append((_zz_who, "thread pips"))
            if ambient_of(_zz_who, here)[0] in _zz_t or role_line(_zz_who) in _zz_t:
                _zz_bad.append((_zz_who, "the caption or the role line"))
            if _zz_w > 16:
                _zz_bad.append((_zz_who, "%d words" % _zz_w))
            _zz_chip = rail_chip(_zz_who)
            _zz_chip_text = (_zz_chip[1] or grade_label(_zz_chip[0])).upper()
            if _zz_chip_text not in _zz_t:
                _zz_bad.append((_zz_who, "no chip %r" % _zz_chip_text))
            _zz_back = zz_rect("sb_char", "sb_char_back")
            if not _zz_back or _zz_back[1] < RAIL_CARD_Y or _zz_back[1] + _zz_back[3] > 1040 or _zz_back[0] < 1180:
                _zz_bad.append((_zz_who, "Back at %r" % (_zz_back,)))
            renpy.hide_screen("sb_char")
    python:
        gui.icon_words = _zz_words0
        check(all(r["returns"] and r["returns"][-1] == ["cancel"] for r in _zz_now.values()),
              "sb_char: every person's card was read, Back last in tree order")
        if _zz_base is not None:
            _zz_diff = [(w, _zz_now.get(w), _zz_base["sb_char"][w]) for w in _zz_base["sb_char"]
                        if _zz_now.get(w) != _zz_base["sb_char"][w]]
            check(not _zz_diff and set(_zz_now) == set(_zz_base["sb_char"]),
                  "sb_char returns the baseline's tuples for every person, in the baseline's order", _zz_diff[:3])
        check(not _zz_bad, "sb_char shows no name, caption, role line, thread pips, 'Closer' or bar; a chip; Back on the card; "
              "at most 16 words (the most: %d, %s)" % _zz_most, _zz_bad[:6])
        note("sb_char: pips", "the thread's diamonds (pip_gold / pip_off) are gone; a choice's cost still shows as diamonds, as 4.6 asks")
        check(rail_chip("gojo") == ("sp", "Off the scale") and rail_chip("shoko") == (None, "Doctor")
              and rail_chip("megumi")[1] is None and grade_tier(rail_chip("megumi")[0]) is not None,
              "the chip: Gojo is off the scale on the sheen, Shoko shows her role, a student a grade",
              (rail_chip("gojo"), rail_chip("shoko"), rail_chip("megumi")))

    ## One card with a mission, a milestone and a romance choice, and its rectangles.
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        bonds["nobara"] = 72
        affection["nobara"] = 55
        _zz_tall = dict(id="zz_hud_tall", title="Nobara's errand in Harajuku",
                        objective="She wants backup for something she refuses to explain until we're on the train.")
        _zz_o_mw = zz_hud_swap("missions_with", lambda who, loc=None: [_zz_tall] if who == "nobara" else [])
        mission_cache_clear()
        zz_hud_quiet()
        _zz_cs = person_choices("nobara", here)
        check(len(_zz_cs) == 4 and _zz_cs[0]["kind"] == "mission" and _zz_cs[0]["icon"] == "mission",
              "fixture: a full card (a mission and three more)", [c["id"] for c in _zz_cs])
    show screen sb_char("nobara")
    python:
        zz_render(0.6)
        _zz_r = [zz_rect("sb_char", "sb_char_%d" % i) for i in range(4)] + [zz_rect("sb_char", "sb_char_invite"), zz_rect("sb_char", "sb_char_back")]
        check(all(_zz_r) and all(r[2] == 600 and r[0] == 1200 for r in _zz_r[:4]) and min(r[1] for r in _zz_r) >= RAIL_CARD_Y
              and max(r[1] + r[3] for r in _zz_r) <= 1040 and max(r[0] + r[2] for r in _zz_r) <= 1820,
              "the card's four choices are 600 wide, inside x 1180 to 1820, from y 250 down, all on screen", _zz_r)
        _zz_tip = zz_hud_tip(zz_hud_wid("sb_char", "sb_char_0"))
        check(_zz_tip == (u"Nobara's errand in Harajuku\nShe wants backup for something she refuses to explain until we're on the train.", "sb_char_0"),
              "a choice's hint is its hover label", _zz_tip)
        check(not any("refuses to explain" in s for s in zz_texts("sb_char")), "and is no longer written on the card")
        shot("person_full_card", wait=0.2)
        ## Two three-line toasts beside Menu still end above the card.
        toast_clear()
        toast("Back on the rack: the Slaughter Demon; in my hand: the Playful Cloud, three sections and all of them heavy", "item")
        toast("Nobara — I'd have to know them better first, and that is going to take more than one afternoon in town", "info")
        zz_render(0.5)
        _zz_drawn = zz_hud_toasts()
        check(RAIL_CARD_Y == 250 and len(toast_visible()) == 2 and _zz_drawn is not None and _zz_drawn[3] > 180
              and _zz_drawn[1] + _zz_drawn[3] <= RAIL_CARD_Y,
              "two three-line toasts over the person view end above the card (y 250)", _zz_drawn)
        shot("person_long_toasts", wait=0.2)
        toast_clear()
        renpy.hide_screen("sb_char")
        zz_hud_swap("missions_with", _zz_o_mw)

    ## --- 6. person_choices -----------------------------------------------------------
    python:
        _zz_bad = []
        _zz_n = 0
        _zz_kinds = set()
        for _zz_kind in ("fresh", "rich"):
            zz_hud_fixture(_zz_kind)
            for _zz_loc in LOC_ORDER:
                for _zz_per in PERIODS:
                    period = _zz_per
                    here = _zz_loc
                    mission_cache_clear()
                    for _zz_who in ROSTER_ORDER:
                        _zz_cs = person_choices(_zz_who, _zz_loc)
                        _zz_n += 1
                        _zz_kinds.update(c["kind"] for c in _zz_cs)
                        if not (1 <= len(_zz_cs) <= 4) or _zz_cs[-1]["id"] != "talk":
                            _zz_bad.append((_zz_kind, _zz_who, _zz_loc, _zz_per, [c["id"] for c in _zz_cs]))
                        for _zz_c in _zz_cs:
                            if _zz_c.get("icon") not in ICONS:
                                _zz_bad.append(("icon", _zz_who, _zz_loc, _zz_c.get("id"), _zz_c.get("icon")))
                            if _zz_c["kind"] == "mission" and _zz_c.get("icon") != "mission":
                                _zz_bad.append(("mission icon", _zz_who, _zz_loc, _zz_c.get("icon")))
        check(not _zz_bad, "person_choices: at most four, Talk last, an icon in ICONS on each, a mission's is `mission` "
              "(%d person x room x period x fixture)" % _zz_n, _zz_bad[:4])
        check({"do", "mission", "act"} <= _zz_kinds, "the sweep met do, mission and act choices", sorted(_zz_kinds))
        zz_hud_fixture("rich")
        period = "Afternoon"
        check("study" in [c["id"] for c in person_choices("megumi", "library")],
              "Study together is offered in the Library", [c["id"] for c in person_choices("megumi", "library")])
        check("library" in ACT_BY_ID["study"]["loc"] and AMBIENT[("megumi", "library")] == ("three books deep", "serious"),
              "the study activity's places and AMBIENT have their Library rows")

    ## --- 7. toast_room() ---------------------------------------------------------------
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        mission_cache_clear()
        zz_hud_quiet()
        board_offers = board_generate()
    scene expression graded_bg()
    python:
        zz_render(0.2)
        check(toast_room() == (1880, 92, 4) and toast_limit() == 4, "a scene: (1880, 92, 4)", toast_room())
        _zz_bad = []
        ## Drawn: the toasts screen must stay empty over each of these.
        for _zz_s, _zz_args in (("journal", ()), ("sb_map", ()), ("board_screen", ()), ("armory", ()), ("icon_sample", ())):
            toast_clear()
            toast("Waiting over %s" % _zz_s, "grade")
            _zz_shown0 = TOASTQ.items[0]["t_shown"]
            renpy.show_screen(_zz_s, *_zz_args)
            zz_render(0.3)
            _zz_room = toast_room()
            _zz_drawn = zz_texts("toasts")
            _zz_clock = [t["t_shown"] for t in TOASTQ.items]
            renpy.hide_screen(_zz_s)
            if _zz_room != (0, 0, 0) or _zz_drawn or _zz_clock != [None] or _zz_shown0 is None:
                _zz_bad.append((_zz_s, _zz_room, _zz_drawn, _zz_clock, _zz_shown0))
        check(not _zz_bad, "toast_room() is (0, 0, 0) over journal, sb_map, board_screen, armory and icon_sample: "
              "nothing draws and a toast already up stops its clock", _zz_bad)
        ## By the tag alone (these need a record to draw; toast_room() only asks what is up).
        toast_clear()
        _zz_bad = []
        combat_begin("alley_curse", None, False, "bg alley")
        for _zz_s, _zz_args, _zz_want in (("board_partner", (None,), (0, 0, 0)), ("combat_screen", (), (1880, 92, 4)),
                                          ("market_screen", (), (0, 0, 0)), ("preferences", (), (0, 0, 0))):
            renpy.show_screen(_zz_s, *_zz_args)
            if toast_room() != _zz_want:
                _zz_bad.append((_zz_s, toast_room(), _zz_want))
            renpy.hide_screen(_zz_s)
        check(not _zz_bad, "toast_room(): (0, 0, 0) with board_partner, the market or a game-menu screen up; "
              "(1880, 92, 4) over combat_screen", _zz_bad)
        store.cb = {}
        zz_render(0.1)

        ## The game menu itself, in its own context.
        toast("Up before the menu", "item")
        zz_render(0.3)
        check(TOASTQ.items[0]["t_shown"] is not None, "fixture: a toast is up before the menu opens")
        del ZZ_HUD_SEEN[:]
        ZZ_HUD_WANT[0] = "menu"
        renpy.call_in_new_context("_game_menu", _game_menu_screen="preferences")
        check(ZZ_HUD_SEEN and ZZ_HUD_SEEN[0][1] == (0, 0, 0) and ZZ_HUD_SEEN[0][2] == [None] and ZZ_HUD_SEEN[0][3],
              "the game menu (its own context): (0, 0, 0), and the toast's clock is stopped", ZZ_HUD_SEEN)
        zz_render(0.3)
        check(len(toast_visible()) == 1 and toast_room() == (1880, 92, 4), "back in the scene the toast gets its full turn",
              (toast_room(), TOASTQ.items))
        toast_clear()

        ## The grade card: no tag, tested by name. As the game shows it...
        renpy.show_screen("grade_card", "g3", "PROMOTED")
        toast("Behind the grade card", "grade")
        zz_render(0.3)
        check(toast_room() == (0, 0, 0) and not zz_texts("toasts") and TOASTQ.items[0]["t_shown"] is None,
              "grade_card shown over a scene: (0, 0, 0), the toast waits", (toast_room(), zz_texts("toasts")))
        renpy.hide_screen("grade_card")
        zz_render(0.3)
        check(len(toast_visible()) == 1, "and shows once the card is gone", TOASTQ.items)
        del ZZ_HUD_SEEN[:]
        ZZ_HUD_WANT[0] = "grade_card"
    ## ... and by `call screen` over a scene.
    call screen grade_card("g3", "PROMOTED")
    python:
        check(_return == ("probe",) and ZZ_HUD_SEEN and ZZ_HUD_SEEN[0][1] == (0, 0, 0) and ZZ_HUD_SEEN[0][2] == 0,
              "grade_card by `call screen` over a scene: (0, 0, 0), nothing drawn", (_return, ZZ_HUD_SEEN))
        toast_clear()

        ## The review panel: no tag, so the scene row; its buttons report through toasts.
        renpy.show_screen("dev_panel")
        zz_render(0.3)
        _zz_room = toast_room()
        dev_action("merit")()
        zz_render(0.4)
        _zz_drawn = zz_texts("toasts")
        check(_zz_room == (1880, 92, 4) and any("erit" in s for s in _zz_drawn) and len(toast_visible()) >= 1,
              "dev_panel: (1880, 92, 4), and a review button's toast is drawn while the panel is up", (_zz_room, _zz_drawn))
        shot("dev_panel_toast", wait=0)
        renpy.hide_screen("dev_panel")
        toast_clear()
        zz_render(0.1)

    show screen sb_place
    python:
        zz_render(0.2)
        check(toast_room() == (1790, 92, 4) and hud_banner_ok(), "sb_place: (1790, 92, 4), and the banner may draw", toast_room())
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_char", "yuji")
        zz_render(0.5)
        check(toast_room() == (1722, 26, 2) and not hud_banner_ok(), "sb_char: (1722, 26, 2), and the banner may not draw", toast_room())
        for _zz_i in range(4):
            toast("Card notice %d" % (_zz_i + 1))
        zz_render(0.3)
        check([t["text"] for t in toast_visible()] == ["Card notice 1", "Card notice 2"]
              and all(t["t_shown"] is None for t in TOASTQ.items[2:]),
              "over the person view two show and the other two wait", [t["t_shown"] for t in TOASTQ.items])
        renpy.hide_screen("sb_char")
        toast_clear()
        hide_side_images = True
        check(toast_room() == (0, 0, 0), "the prologue's blackout: (0, 0, 0)", toast_room())
        hide_side_images = False

        ## A toast queued where toasts wait is still there, unexpired, 10 s later.
        renpy.show_screen("journal")
        zz_render(0.3)
        toast("Queued under the journal", "item")
        toast("And a second one", "stat")
        _zz_t0 = time.time()
    $ renpy.pause(10.0, hard=True, modal=False)
    python:
        check(time.time() - _zz_t0 >= 9.5 and [t["text"] for t in TOASTQ.items] == ["Queued under the journal", "And a second one"]
              and all(t["t_shown"] is None for t in TOASTQ.items) and not zz_texts("toasts") and toast_visible() == [],
              "queued under limit 0: both toasts are still queued and unexpired 10 s later, and nothing drew",
              (time.time() - _zz_t0, TOASTQ.items))
        renpy.hide_screen("journal")
        zz_render(0.4)
        check(len(toast_visible()) == 2 and all(time.time() - t["t_shown"] < 1.5 for t in TOASTQ.items),
              "once the journal closes both show, with a full turn", TOASTQ.items)
        toast_clear()

    ## --- 8. the lanes, and the worst-case screenshots ---------------------------------
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        mission_cache_clear()
        zz_hud_quiet()
        _zz_lane = (TOAST_LANE[0], TOAST_LANE[1], TOAST_LANE[2] - TOAST_LANE[0], TOAST_LANE[3] - TOAST_LANE[1])
        _zz_banner = (HUD_BANNER_X, 96, HUD_BANNER_W, 170 - 96)
        check(TOAST_LANE == (1330, 92, 1790, 350) and (HUD_BANNER_X, HUD_BANNER_X + HUD_BANNER_W) == (400, 1300)
              and not zz_hud_meets(_zz_lane, _zz_banner) and HUD_BANNER_X + HUD_BANNER_W <= TOAST_LANE[0],
              "the toast lane (x 1330 to 1790, y 92 to 350) and the banner (x 400 to 1300) do not intersect",
              (TOAST_LANE, _zz_banner))
    scene expression graded_bg()
    python:
        ## The banner waits for the arrival caption (4.3): read what is
        ## drawn, as the loop shows it (check_objective, then the place view).
        zz_hud_quiet()
        _zz_o_ot = zz_hud_swap("objective_text", lambda: "Harness: wait for the arrival caption")
        day += 1
        store.last_objective = None
        check_objective()
        renpy.show_screen("sb_place")
        zz_render(1.0)
        _zz_b1 = zz_hud_banner()
        check(arrival_caption() is not None and _zz_b1 is not None and _zz_b1[0] == 0.0,
              "while the arrival caption is up the objective banner is not drawn (alpha 0)", _zz_b1)
        shot("banner_waits", wait=0)
        zz_render(3.2)
        _zz_b2 = zz_hud_banner()
        check(arrival_caption() is None and _zz_b2 is not None and _zz_b2 == (1.0, 0),
              "once the caption has faded the banner has slid in (alpha 1)", _zz_b2)
        shot("banner_after_caption", wait=0)
        renpy.hide_screen("objective_toast")
        renpy.hide_screen("sb_place")
        zz_hud_swap("objective_text", _zz_o_ot)
        store.last_objective = objective_text() or ""
        ## zz_worst shows the banner itself: no caption in its way.
        arrival_caption()
        ARRIVAL[1] -= 10
        _zz_ok = zz_worst("sb_place", hover="rail_wait")
        check(_zz_ok and renpy.get_screen("sb_place") and os.path.isfile(os.path.join(zz_smoke_state.shots, "worst_sb_place.png")),
              "zz_worst(sb_place): four toasts, the banner, skipping, a tile hovered: on file")
        check(toast_room()[0] == TOAST_LANE[2] and toast_room()[0] - 460 == TOAST_LANE[0],
              "over sb_place the stack is anchored at the lane's right edge, 460 wide", toast_room())
        renpy.show_screen("objective_toast", "Worst case: an objective long enough to fill the banner from edge to edge")
        zz_render(0.6)
        _zz_bt = [d for d in zz_text_nodes("objective_toast") if "Worst case" in zz_text_string(d)]
        _zz_bf = [d for d in [renpy.get_screen("objective_toast")] if d is not None]
        _zz_sizes = []
        renpy.get_screen("objective_toast").visit_all(
            lambda d: _zz_sizes.append(d.window_size) if getattr(d, "window_size", None) else None)
        check(_zz_bt and _zz_sizes and max(s[0] for s in _zz_sizes) == HUD_BANNER_W and hud_banner_ok(),
              "the banner over sb_place is 900 wide from x 400: its line is clear of the toast lane to its end",
              _zz_sizes)
        renpy.hide_screen("objective_toast")
        renpy.hide_screen("sb_place")
        _zz_ok = zz_worst("sb_char", "yuji", hover="sb_char_0")
        check(_zz_ok and renpy.get_screen("sb_char"), "zz_worst(sb_char): the person view's worst case is on file")
        renpy.show_screen("objective_toast", "Never over the person view")
        zz_render(0.3)
        check(not hud_banner_ok(), "the objective banner does not draw over the person view")
        shot("person_no_banner", wait=0)
        renpy.hide_screen("objective_toast")
        renpy.hide_screen("sb_char")
        renpy.show_screen("objective_toast", "Never over a scene either")
        zz_render(0.3)
        check(not hud_banner_ok(), "nor over a scene")
        renpy.hide_screen("objective_toast")

    ## --- 9. captions ---------------------------------------------------------------------
    python:
        zz_hud_fixture("fresh")
        flags.discard("sunmall_done")
        period = "Morning"
        _zz_bad = []
        _zz_fresh = {}
        for _zz_who in ROSTER_ORDER:
            for _zz_loc in LOC_ORDER:
                _zz_v = ambient_of(_zz_who, _zz_loc)
                _zz_fresh[(_zz_who, _zz_loc)] = _zz_v
                if not (isinstance(_zz_v, tuple) and len(_zz_v) == 2 and _zz_v[0] and _zz_v[1] in EXPRESSIONS):
                    _zz_bad.append((_zz_who, _zz_loc, _zz_v))
        check(not _zz_bad, "ambient_of is a (caption, expression) 2-tuple for every person x room (%d)" % len(_zz_fresh), _zz_bad[:4])
        _zz_off = [(k, _zz_fresh[k]) for k in sorted(_zz_fresh) if k not in AMBIENT_NEEDS
                   and _zz_fresh[k] != (AMBIENT.get(k) or AMBIENT.get((k[0], None)) or AMBIENT_FALLBACK)]
        check(not _zz_off, "on a fresh game every caption is the AMBIENT one (no story row holds yet)", _zz_off[:4])
        flag("sunmall_done")
        _zz_diff = sorted(k for k in _zz_fresh if ambient_of(*k) != _zz_fresh[k])
        check(_zz_diff, "with sunmall_done set at least one caption differs from the fresh game's", _zz_diff)
        note("captions after the Sun Mall", [(k, ambient_of(*k)[0]) for k in _zz_diff])
        check(len(AMBIENT_STORY) == 12 and _validate_wp7_tables() == [], "AMBIENT_STORY ships twelve rows and the validator passes",
              (len(AMBIENT_STORY), _validate_wp7_tables()))
        _zz_before = ambient_of("nobara", "dorm_common")
        threads["nobara_saori"] = 1
        check(ambient_of("nobara", "dorm_common") == ("scrolling through old photos", "neutral") != _zz_before,
              "a thread stage changes a caption, and the last row that holds wins", (_zz_before, ambient_of("nobara", "dorm_common")))
        _zz_before = ambient_of("yuji", "training")
        promote("yuji", "g3", quiet=True)
        check(ambient_of("yuji", "training")[0] != _zz_before[0] and rail_story_ok("grade:yuji:g3") and not rail_story_ok("grade:yuji:g2")
              and rail_story_ok("grade:mc:g4"),
              "a grade condition changes a caption", (_zz_before, ambient_of("yuji", "training")))
        _zz_o = list(AMBIENT_STORY)
        AMBIENT_STORY.append(("nobody", "nowhere", "thread:yuji:9", "", "smug"))
        check(len(_validate_wp7_tables()) >= 4, "the validator reports a bad AMBIENT_STORY row", _validate_wp7_tables())
        AMBIENT_STORY[:] = _zz_o
        AMBIENT_STORY.append(("shoko", "infirmary", "grade:shoko:g2", "never", "neutral"))
        check(any("no grade" in f for f in _validate_wp7_tables()) and len(_validate_wp7_tables()) == 1,
              "the validator reports a grade condition on someone with no grade", _validate_wp7_tables())
        AMBIENT_STORY[:] = _zz_o

    ## --- the stand-in path, and the icon names P2's files use ---------------------------
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        stamina = 20
        mission_cache_clear()
        zz_hud_quiet()
        renpy.loadable = zz_hud_no_art
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.4)
        _zz_t = zz_texts("sb_place")
        check(u"？" not in _zz_t and ICONS["map"][0] in _zz_t and ICONS["wait"][0] in _zz_t and "Map" in _zz_t and "Wait" in _zz_t,
              "no icon pictures: the place view draws kanji seals with their words, none a question mark", _zz_t)
        _zz_r = [zz_rect("sb_place", w) for w in ("hud_map", "hud_journal", "hud_menu")]
        check(all(_zz_r) and [r[0] for r in _zz_r] == [1668, 1742, 1816] and all(r[1] == 26 for r in _zz_r),
              "the corner buttons keep their places with words under them", _zz_r)
        shot("standin_place", wait=0.2)
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_char", "yuji")
        zz_render(0.6)
        _zz_t = zz_texts("sb_char")
        check(u"？" not in _zz_t and ICONS["talk"][0] in _zz_t and ICONS["back"][0] in _zz_t,
              "no icon pictures: the person view draws kanji seals, none a question mark", _zz_t)
        shot("standin_person", wait=0.2)
        renpy.hide_screen("sb_char")
        renpy.loadable = ZZ_HUD_LOADABLE[0]

        _zz_names = set()
        for _zz_fn in ("ui_hud.rpy", "sb_screens.rpy", "sb_activities.rpy"):
            _zz_src = open(os.path.join(config.gamedir, _zz_fn), encoding="utf-8").read()
            _zz_names.update(zz_hud_re.findall(r'\bicon(?:_btn)?\(\s*"([a-z_0-9]+)"', _zz_src))
        check(_zz_names and _zz_names <= set(ICONS) and all(icon_has_art(n) for n in _zz_names),
              "every literal icon name in P2's files is in ICONS and has its picture", sorted(_zz_names))
        _zz_all = set(r[1] for k in ("fresh", "rich") for l in LOC_ORDER for r in [("", icon_for("act", a["id"])) for a in PLACE_ACTIONS])
        check(_zz_all <= set(ICONS), "every registered place action maps to an icon", sorted(_zz_all))

    ## --- a save made with the banner drawn, loaded again ---------------------------------
    ## (zz_hud_load_step drives it from here and calls finish().)
    python:
        zz_hud_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        mission_cache_clear()
        toast_clear()
        renpy.hide_screen("objective_toast")
        ARRIVAL[0] = None
        OBJ_UNSEEN[0] = None
        store.last_objective = None
        check(bool(objective_text()) and not explore_mode, "fixture: there is an objective to show", objective_text())
        ZZ_HUD_LOAD[:] = [1, 0, 0]
        zz_hud_sweep()
    scene expression graded_bg()
    jump sandbox
