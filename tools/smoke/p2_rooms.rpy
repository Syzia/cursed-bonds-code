## tools/smoke/p2_rooms.rpy -- P6's harness: the hotspots in the rooms, the
## computer, the Library's shelves and fishing (docs/PHASE2_DESIGN.md, 7 · P6).
##
##   tools/smoke.sh tools/smoke/p2_rooms.rpy
##
## Every acceptance bullet of P6 is a named check below, in the plan's order:
##   A  the hotspot set and its validator; a visible hotspot's action leaves
##      the column and is a return of hot_layer; a look returns ("hot", id)
##      and its line changes with the day; a costed hotspot at Night
##   B  reachability: every room x period x one to four people, ordinary day
##      and rest day; then the same on the drawn screen, with zz_rect
##   C  a hotspot follows its action (the cot, the board, the veil, explore
##      mode, the storehouse's two rows, a rest day, the standalone)
##   D  the vending machine; a look's use is remembered for the day
##   E  the test sidecar (tools/smoke/assets/p2_rooms/game/layout/)
##   F  registration at init 0
##   G  the computer: reading, the hidden and the market pages, requests,
##      records, the pages' text
##   H  the cross-check of the board
##   I  fishing: 1,000 casts, the River Lord, the pale thing, the yen, the
##      first catch, a companion, fish_Hook, rollback (blocked when a cast
##      is dealt and again when it is settled; the rollback key at the bite),
##      packing up at the bite, Esc with the record book open, the opening
##      line, the screen's own timers, the rolled sitting,
##      the record book
##   J  the Library's shelves; a desk is unchanged
##   K  autoplay timers and the menu key; the saved variables; zz_worst
##
## 7.3's lines that wait for another package all run here, because wave 1 is
## merged: the market page against P4b's market_exists(), Leads and Records
## against P3's journal, the Night and rest-day halves against P4b's rule.
## Each says so in a NOTE.
##
## Offers come from board_generate(), catches from fish_land(), requests from
## pc_request() (R5). The asset overlay replaces game/layout/hot_dorm.json
## for section E; the real file is read back from the repository afterwards.
##
## Screenshots (shots/p2_rooms/): worst_pc_screen.png, worst_fish_screen.png,
## room_<place>.png for every room with a hotspot, room_dorm_standin.png (no
## icon pictures), room_riverside_night.png, pc_<page>.png for the twelve
## pages, pc_board_checked.png, fish_wait.png, fish_record_hover.png, fish_bite.png,
## fish_book.png.
##
## A run takes about a minute and a quarter (one sitting is left to the
## screen's own timers: three sweeps of three seconds).

init 999 python:
    import builtins
    import copy
    import json
    import os
    import pickle
    import re
    import time

    class ZZRoomState(builtins.object):
        """Harness state, outside the store."""

        def __init__(self):
            self.boot = None                    # the defaults at boot
            self.texts = builtins.list()        # every say and menu line of the script
            self.picks = builtins.list()        # menu choices to take, in order
            self.menus = builtins.list()        # (captions offered, the one taken)
            self.answers = None                 # what to answer pc_screen / fish_screen with
            self.seen = builtins.list()         # the screens the driver answered
            self.on_show = None                 # called with the screen's name before each answer
            self.own = None                     # when set: called with the screen's name, and ITS return is the answer
                                                # (None leaves the screen to its own timers)
            self.lines = builtins.list()        # every line fish_settle returned
            self.blocks = builtins.list()       # can_rollback() after each block_rollback()
            self.keep = builtins.dict()

    zz_r = ZZRoomState()

    ZZ_R_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                  "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                  "intensive_done", "ijichi_rides")
    ZZ_R_VARS = ("pc_read", "pc_requests", "pc_checked_week", "pc_noted", "fish_log", "fish_state", "fish_cursed_week")
    ZZ_R_NAMES = ("Kai" + "to", "Ama" + "giri")      # the default name, never written out (D29)
    ZZ_R_FILES = ("room_spots.rpy", "room_computer.rpy", "room_fishing.rpy", "room_library.rpy")

    ## 4.10's first set: hotspot id -> (place, kind, action).
    ZZ_R_TABLE = {
        "computer": ("dorm", "act", "pc_open"), "bed": ("dorm", "act", "sleep"),
        "card_table": ("dorm_common", "act", "cards_play"), "tv": ("dorm_common", "look", None),
        "bank": ("riverside", "act", "fish_cast"),
        "stacks": ("library", "act", "lib_study"), "locked_shelf": ("library", "look", None),
        "spot_vend": ("courtyard", "standalone", "spot_vend"),
        "blackboard": ("classroom", "look", None),
        "counter": ("cafeteria", "act", "eat"), "cot": ("infirmary", "act", "rest"),
        "racks": ("storehouse", "act", "tools"), "armory": ("storehouse", "act", "armory"),
        "board": ("utahime_office", "act", "board"), "veil": ("ridge", "act", "veil"),
    }

    ## --- capture ---------------------------------------------------------------

    zz_r_prev_filter = config.say_menu_text_filter

    def zz_r_text(s):
        zz_r.texts.append(s)
        return zz_r_prev_filter(s) if zz_r_prev_filter else s

    config.say_menu_text_filter = zz_r_text

    ## renpy.say() from python (a look hotspot's line) passes no text filter.
    zz_r_real_say = renpy.exports.say

    def zz_r_say(who, what, *args, **kwargs):
        zz_r.texts.append(what)
        return zz_r_real_say(who, what, *args, **kwargs)

    renpy.exports.say = zz_r_say

    ## The result line of every settled cast ("[_fish_line]" is all the text
    ## filter sees of it).
    zz_r_real_settle = fish_settle

    def zz_r_settle(r):
        line = zz_r_real_settle(r)
        zz_r.lines.append(line)
        return line

    setattr(store, "fish_settle", zz_r_settle)

    ## renpy.can_rollback() straight after every renpy.block_rollback().
    zz_r_real_block = renpy.exports.block_rollback

    def zz_r_block(*args, **kwargs):
        out = zz_r_real_block(*args, **kwargs)
        zz_r.blocks.append(renpy.exports.can_rollback())
        return out

    renpy.exports.block_rollback = zz_r_block

    def zz_r_false():
        return False

    def zz_r_phase(name):
        """An `own` driver that answers nothing: it only notes each new
        (cast, phase) fish_screen passes through."""
        row = (fish_state.get("cast"), fish_phase())
        if name == "fish_screen" and (not zz_r.keep["phases"] or zz_r.keep["phases"][-1] != row):
            zz_r.keep["phases"].append(row)
        return None

    def zz_r_leave_at_bite(name):
        """An `own` driver that packs up as soon as the float has dipped."""
        zz_r_phase(name)
        if name == "fish_screen" and fish_phase() == "bite":
            zz_r.keep["bite_kind"] = fish_state.get("kind")
            return ("leave",)
        return None

    def zz_r_esc_book(name):
        """An `own` driver that misses cast 1, opens the record book while
        cast 2's float sits, presses the player's own Esc / right-click
        (through the keymap) half a second later, notes what is left a
        quarter of a second after that, and then packs up."""
        if name != "fish_screen":
            return None
        k = zz_r.keep
        if fish_state.get("cast", 0) == 1:
            return ("miss",)
        s = renpy.get_screen("fish_screen")
        now = time.time()
        if "eb_t" not in k:
            k["eb_t"] = now
            fish_state["wait"] = 60.0
            k["eb_cast0"] = fish_state.get("t_cast")
            s.scope["fish_book"] = True
            renpy.restart_interaction()
            return None
        if now - k["eb_t"] > 0.5 and "eb_open" not in k:
            k["eb_open"] = (bool(s.scope.get("fish_book")), fish_state.get("cast"), fish_phase())
            k["eb_key"] = now
            renpy.queue_event("game_menu")
            return None
        if now - k["eb_t"] > 0.75 and "eb_open" in k and "eb_after" not in k:
            k["eb_after"] = (bool(s.scope.get("fish_book")), fish_state.get("cast"), fish_phase(), fish_state.get("settled"))
            k["eb_cast1"] = fish_state.get("t_cast")
            return ("leave",)
        return None

    def zz_r_roll_at_bite(name):
        """An `own` driver that, at the bite of cast 1, presses the player's
        own rollback key (through the keymap), then asks renpy.rollback()
        outright, then hooks dead centre; it packs up at cast 2."""
        zz_r_phase(name)
        if name != "fish_screen":
            return None
        k = zz_r.keep
        if fish_state.get("cast", 0) >= 2:
            return ("leave",)
        if fish_phase() != "bite":
            return None
        now = time.time()
        if "rb_t" not in k:
            k["rb_t"] = now
            k["rb_can"] = renpy.can_rollback()
            k["rb_settled"] = fish_state.get("settled")
            renpy.queue_event("rollback")
            return None
        if now - k["rb_t"] > 0.3 and "rb_asked" not in k:
            k["rb_asked"] = True
            renpy.rollback()
            return None
        if now - k["rb_t"] > 0.7:
            k["rb_after"] = (fish_state.get("cast"), fish_phase(), fish_state.get("settled"))
            return ("hook", 1.0)
        return None

    def zz_r_no_art(name):
        return False

    def zz_r_said(n, needle):
        return [t for t in zz_r.texts[n:] if needle in t]

    ## A menu is answered from zz_r.picks (the choice whose caption holds the
    ## next entry); with none queued it is the game's own menu.
    zz_r_real_menu = menu

    def zz_r_menu(items, **kwargs):
        caps = [lab for lab, val in items if val is not None]
        if zz_r.picks:
            want = zz_r.picks.pop(0)
            for lab, val in items:
                if val is not None and want in lab:
                    zz_r.menus.append((caps, lab))
                    return getattr(val, "value", val)
            zz_r.menus.append((caps, "MISSING " + want))
        else:
            zz_r.menus.append((caps, None))
        return zz_r_real_menu(items, **kwargs)

    ## (setattr: the store's own `menu` is replaced; it is not a new harness name.)
    setattr(store, "menu", zz_r_menu)

    ## --- the driver: answers pc_screen and fish_screen from zz_r.answers --------

    def zz_r_tick():
        if zz_r.answers is None:
            return None
        for name in ("pc_screen", "fish_screen"):
            if renpy.get_screen(name) is not None:
                zz_r.seen.append(name)
                if zz_r.on_show is not None:
                    zz_r.on_show(name)
                if zz_r.own is not None:
                    return zz_r.own(name)
                if zz_r.answers:
                    return zz_r.answers.pop(0)
                return ("close",) if name == "pc_screen" else ("leave",)
        return None

    config.overlay_screens.append("zz_r_driver")

    def zz_r_drive(answers, on_show=None, own=None):
        """Script plays through (text skipped), the two screens are answered
        from `answers`, then closed. With `own`, a function of the screen's
        name, the answer is whatever it returns: None leaves the screen
        waiting on its own timers."""
        zz_r.answers = builtins.list(answers)
        zz_r.on_show = on_show
        zz_r.own = own
        del zz_r.seen[:]
        autoplay(True)
        store.smoke_autoplay = False

    def zz_r_stop():
        autoplay(False)
        zz_r.answers = None
        zz_r.on_show = None
        zz_r.own = None

    ## --- fixtures --------------------------------------------------------------

    def zz_r_snapshot():
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

    def zz_r_restore():
        for k, v in zz_r.boot.items():
            setattr(store, k, copy.deepcopy(v))
        mission_cache_clear()
        toast_clear()

    def zz_r_fix(kind="rich", grade=None, **kw):
        """A settled game from the boot state. rich: everyone on the roster,
        Bond 60, the flags of a mid-game save, Grade 3 (or `grade`).
        fresh: day 3 of a new game, Grade 4."""
        zz_r_restore()
        renpy.random.seed(20261004)
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
            for f in ZZ_R_FLAGS:
                flag(f)
        else:
            for f in ZZ_R_FLAGS[:5]:
                flag(f)
        flag("saw_the_ridge_veil")
        store.done_events.add("st_roll_call")
        promote("mc", grade or ("g3" if kind == "rich" else "g4"), quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()

    def zz_r_rest_day():
        """Today is the day after a night with Gojo (P4b's own variables)."""
        fixture(night_cost_kind="gojo", night_cost_day=store.day)

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

    def zz_r_stage(loc, n, first=()):
        """Exactly n people in `loc` this period, placed with pin(); everyone
        else is pinned somewhere else. `first` are put on stage first."""
        store.companion = None
        away = "forest" if loc != "forest" else "gate"
        folk = [w for w in first if w in store.roster] + [w for w in ROSTER_ORDER if w in store.roster and w not in first]
        for i, w in enumerate(folk):
            pin(w, loc if i < n else away)
        return len(who_is_here(loc))

    def zz_r_spots():
        """The registered hotspots that are the game's own."""
        return [h for h in HOT_SPOTS if not h["id"].startswith(("zz", "go_"))]

    def zz_r_ids(rows):
        return [r[0] for r in rows]

    def zz_r_hot_ids(loc):
        return [h["id"] for h in hot_spots_for(loc) if not h["id"].startswith(("zz", "go_"))]

    def zz_r_rets(screen):
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

    def zz_r_src(name):
        with open(os.path.join(config.gamedir, name), encoding="utf-8") as f:
            return f.read()

    def zz_r_reach(loc):
        """The reachability rule for the room as it stands now: a list of
        what is wrong (empty when every action is in exactly one place)."""
        bad = []
        acts = zz_r_ids(place_actions(loc))
        filt = zz_r_ids(night_filter_actions(loc, place_actions(loc)))
        col = [a[0] for a in rail_actions(loc) if a[0] != "release"]
        rects = view_person_rects(loc)
        spots = [h for h in hot_spots_for(loc) if h["lines"] is None and not h["standalone"]]
        for h in spots:
            if any(hot_overlap(hot_rect(h["x"], h["y"]), p) for p in rects):
                bad.append(("behind someone", h["id"]))
        for a in filt:
            in_col = a in col
            in_hot = any(h["act"] == a for h in spots)
            if in_col == in_hot:
                bad.append(("both" if in_col else "neither", a))
            if in_hot and not all(hot_open(h) for h in spots if h["act"] == a):
                bad.append(("offered, but the hotspot is shut", a))
        for a in acts:
            if a in filt:
                continue
            if a in col or any(h["act"] == a and hot_open(h) for h in spots):
                bad.append(("dropped by the night rule but still offered", a))
        for a in col:
            if a not in filt:
                bad.append(("in the column, not in the filtered list", a))
        return bad

    def zz_r_scrub():
        """Take the harness's own scratch names out of the store (a save
        would have to pickle them)."""
        for k in [k for k in builtins.list(vars(store)) if k.startswith("_zz")]:
            try:
                delattr(store, k)
            except Exception:
                pass

    def zz_r_save(name):
        """Called by the driver while one of the two screens is waiting:
        a real save of the game as it stands."""
        zz_r_scrub()
        slot = "zz_rooms_" + name
        try:
            renpy.save(slot)
            zz_r.keep["save_" + name] = bool(renpy.can_load(slot))
        except Exception as e:
            zz_r.keep["save_" + name] = "%s: %s" % (type(e).__name__, e)


screen zz_r_driver():
    zorder 300
    timer 0.05 repeat True action Function(zz_r_tick)


label zz_smoke:

    python:
        zz_r.boot = zz_r_snapshot()
        check(market_exists() and night_exists(),
              "wave 1 is in: market_exists() and night_exists() are True (so 7.3's waiting lines run here)")

    ############################################################################
    ## E (first, while the overlay's sidecar is the one in force)
    ############################################################################
    python:
        zz_r_fix("fresh")
        here = "dorm"
        zz_r_stage("dorm", 0)
        _zz_reg = [_zz_h for _zz_h in HOT_SPOTS if _zz_h["id"] == "computer"][0]
        _zz_row = [_zz_h for _zz_h in hot_spots_for("dorm") if _zz_h["id"] == "computer"]
        check(rule_layout("hot_dorm") == {"spots": {"computer": [300, 300], "bed": [1330, 720]}},
              "E: the test sidecar hot_dorm.json is the one read (the asset overlay)", rule_layout("hot_dorm"))
        check(_zz_row and (_zz_row[0]["x"], _zz_row[0]["y"]) == (300, 300) and (_zz_reg["x"], _zz_reg["y"]) != (300, 300),
              "E: the test sidecar moves the computer's hotspot to (300, 300); the registered point is untouched",
              (_zz_row, (_zz_reg["x"], _zz_reg["y"])))
        check(rule_layout("view_dorm") == {"poses": {"zz_computer": [900, 900, 72, 72]}}
              and not [_zz_h for _zz_h in hot_spots_for("dorm") if (_zz_h["x"], _zz_h["y"]) == (900, 900)],
              "E: view_dorm.json beside it is read on its own name and never for a hotspot", rule_layout("view_dorm"))
        check(hot_validate() == [], "E: the validator passes with the test sidecar in force", hot_validate())
        ## Back to the repository's own file for the rest of the run.
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_real = None
        if _zz_root and os.path.isfile(os.path.join(_zz_root, "game", "layout", "hot_dorm.json")):
            with open(os.path.join(_zz_root, "game", "layout", "hot_dorm.json"), encoding="utf-8") as _zz_f:
                _zz_real = json.load(_zz_f)
            del _zz_f
        if check(_zz_real is not None, "E: the repository's own hot_dorm.json is readable (SMOKE_ROOT)"):
            RULE_LAYOUT["hot_dorm"] = _zz_real

    ############################################################################
    ## A. The set, the validator, visible hotspots
    ############################################################################
    python:
        zz_r_fix("rich")
        _zz_real = zz_r_spots()
        _zz_got = builtins.dict((_zz_h["id"], (_zz_h["place"], _zz_h["kind"], _zz_h["act"])) for _zz_h in _zz_real)
        check(_zz_got == ZZ_R_TABLE, "A: the first set of 4.10 is registered: fifteen hotspots in eleven rooms",
              builtins.sorted(set(_zz_got.items()) ^ set(ZZ_R_TABLE.items())))
        check(hot_validate() == [] and pc_validate() == [] and fish_validate() == [] and lib_validate() == [],
              "A: the hotspot validator passes (and the computer's, fishing's and the Library's)",
              hot_validate() + pc_validate() + fish_validate() + lib_validate())
        ## The toast lane is as tall as four two-line toasts (they end near
        ## y 416): a point just under the old lane (y 92 to 350) is a finding.
        _zz_look = [_zz_h for _zz_h in _zz_real if _zz_h["kind"] == "look"][0]
        check(HOT_LANES[0] == (1330, 92, 460, 330) and HOT_LANES[0][1] + HOT_LANES[0][3] >= TOAST_LANE[3]
              and len(hot_point_findings(_zz_look, 1500, 420)) == 1 and "lane" in hot_point_findings(_zz_look, 1500, 420)[0]
              and len(hot_point_findings(_zz_look, 1366, 457)) == 1
              and hot_point_findings(_zz_look, 1500, 459) == [] and hot_point_findings(_zz_look, 1293, 420) == [],
              "A: the validator's toast lane is x 1330 to 1790, y 92 to 422: a hotspot under the fourth toast is a finding",
              (HOT_LANES, hot_point_findings(_zz_look, 1500, 420), hot_point_findings(_zz_look, 1500, 459)))
        _zz_bad = [(_zz_h["id"], _zz_h["x"], _zz_h["y"]) for _zz_l in LOCATIONS for _zz_h in hot_spots_for(_zz_l)
                   if hot_overlap(hot_rect(_zz_h["x"], _zz_h["y"]), (1330, 92, 460, 330))]
        check(not _zz_bad, "A: no hotspot of any room (sidecar points and exits too) sits under four two-line toasts", _zz_bad)
        check(all(set(SPOT_LINES[_zz_h["id"]]) == set(_zz_h["lines"]) and len(_zz_h["lines"]) >= 2
                  for _zz_h in _zz_real if _zz_h["kind"] == "look") and len(SPOT_LINES) == 3,
              "A: SPOT_LINES holds the look hotspots' lines, at least two each")

        ## The shipped sidecars: every id registered for its room, the point the code's own.
        _zz_bad = []
        _zz_n = 0
        for _zz_p in builtins.sorted(set(_zz_h["place"] for _zz_h in _zz_real)):
            _zz_side = rule_layout("hot_" + _zz_p).get("spots") or {}
            for _zz_h in _zz_real:
                if _zz_h["place"] != _zz_p:
                    continue
                _zz_n += 1
                if _zz_side.get(_zz_h["id"]) != [_zz_h["x"], _zz_h["y"]]:
                    _zz_bad.append((_zz_p, _zz_h["id"], _zz_side.get(_zz_h["id"]), (_zz_h["x"], _zz_h["y"])))
        check(not _zz_bad and _zz_n == 15,
              "A: game/layout/hot_<place>.json holds the final point of every hotspot, and the code's default agrees", _zz_bad)

        ## Every room x period, as the schedule fills it: a visible action
        ## hotspot's action is out of the column and is what its button returns.
        _zz_bad = []
        _zz_seen = set()
        for _zz_kind in ("fresh", "rich"):
            zz_r_fix(_zz_kind)
            for _zz_l in LOCATIONS:
                for _zz_per in PERIODS:
                    period = _zz_per
                    here = _zz_l
                    _zz_col = zz_r_ids(rail_actions(_zz_l))
                    for _zz_h in hot_spots_for(_zz_l):
                        if _zz_h["id"].startswith("zz"):
                            continue
                        _zz_seen.add(_zz_h["id"])
                        _zz_a = hot_action(_zz_h)
                        if _zz_h["lines"] is not None:
                            if not (isinstance(_zz_a, Return) and _zz_a.value == ("hot", _zz_h["id"])):
                                _zz_bad.append((_zz_l, _zz_per, _zz_h["id"], "a look must return ('hot', id)"))
                            continue
                        if not _zz_h["standalone"] and _zz_h["act"] in _zz_col:
                            _zz_bad.append((_zz_l, _zz_per, _zz_h["id"], "its action is still in the column"))
                        if hot_open(_zz_h):
                            if not (isinstance(_zz_a, Return) and _zz_a.value == ("act", _zz_h["act"])):
                                _zz_bad.append((_zz_l, _zz_per, _zz_h["id"], "must return ('act', id)"))
                        elif not isinstance(_zz_a, NullAction):
                            _zz_bad.append((_zz_l, _zz_per, _zz_h["id"], "shut, but not a NullAction"))
        check(not _zz_bad, "A: every visible hotspot's action is absent from the column (rail_actions) and is its button's "
              "return; a look returns ('hot', id) (every room x period, two fixtures)", _zz_bad[:6])
        _zz_want = set(ZZ_R_TABLE)
        check(_zz_seen >= _zz_want - {"card_table"}, "A: every hotspot of the set was visible somewhere in that sweep "
              "(the card table only once P7's cards_ok() can be True)", builtins.sorted(_zz_want - _zz_seen))
        if "card_table" not in _zz_seen:
            note("A: the card table", "its hotspot never shows in this run: cards_play is offered only while P7's cards_ok() "
                 "is True (the stub says False); the row and its point are registered and linted")

        ## A look's line changes with the day.
        _zz_bad = []
        for _zz_h in _zz_real:
            if _zz_h["kind"] != "look":
                continue
            zz_r_fix("rich", day=9)
            _zz_l1 = hot_line(_zz_h["id"])
            day = 10
            _zz_l2 = hot_line(_zz_h["id"])
            if not (_zz_l1 and _zz_l2 and _zz_l1 != _zz_l2 and _zz_l1 in _zz_h["lines"] and _zz_l2 in _zz_h["lines"]):
                _zz_bad.append((_zz_h["id"], _zz_l1, _zz_l2))
        check(not _zz_bad, "A: a look hotspot's line changes with the day", _zz_bad)

        ## Night: a costed hotspot is there, dim, and returns nothing.
        _zz_bad = []
        for _zz_l, _zz_id in (("riverside", "bank"), ("library", "stacks")):
            zz_r_fix("rich", period=PERIODS[-1], here=_zz_l)
            zz_r_stage(_zz_l, 0)
            _zz_h = [_zz_h for _zz_h in hot_spots_for(_zz_l) if _zz_h["id"] == _zz_id]
            if not (_zz_h and _zz_h[0]["cost"] > 0 and not hot_open(_zz_h[0]) and isinstance(hot_action(_zz_h[0]), NullAction)
                    and _zz_h[0]["act"] not in zz_r_ids(rail_actions(_zz_l))):
                _zz_bad.append((_zz_l, _zz_h))
        check(not _zz_bad, "A: at Night a costed hotspot (the bank, the stacks) is still drawn, shut, and its button is a "
              "NullAction; the column doesn't offer it either", _zz_bad)
        zz_r_fix("rich", period=PERIODS[-1], here="riverside")
        zz_r_stage("riverside", 0)
        renpy.show_screen("sb_place")
        _zz_rets = zz_r_rets("sb_place")
        check(("act", "fish_cast") not in _zz_rets and zz_rect("sb_place", "hot_bank") is not None,
              "A: on the drawn place view at Night the bank's button is there and returns nothing", _zz_rets)
        renpy.set_focus("sb_place", "hot_bank")
        shot("room_riverside_night")
        renpy.hide_screen("sb_place")
        note("A: the Night half", "ran against P4b's real night rule (NIGHT_STRICT %r), not the stub" % (NIGHT_STRICT,))

    ############################################################################
    ## B. Reachability
    ############################################################################
    python:
        _zz_bad = []
        _zz_cases = 0
        _zz_hot = 0
        _zz_staged = True
        for _zz_kind, _zz_rest in (("rich", False), ("fresh", False), ("rich", True)):
            zz_r_fix(_zz_kind)
            if _zz_rest:
                zz_r_rest_day()
            for _zz_l in LOCATIONS:
                for _zz_per in PERIODS:
                    for _zz_n in (0, 1, 2, 3, 4):
                        period = _zz_per
                        here = _zz_l
                        if zz_r_stage(_zz_l, _zz_n) != _zz_n or len(view_person_rects(_zz_l)) != _zz_n:
                            _zz_staged = False
                        _zz_cases += 1
                        _zz_hot += len(hot_covers(_zz_l))
                        for _zz_b in zz_r_reach(_zz_l):
                            _zz_bad.append((_zz_kind, "rest day" if _zz_rest else "ordinary", _zz_l, _zz_per, _zz_n) + _zz_b)
        check(_zz_staged, "B: pin() puts exactly none to four people on each room's stage (view_person_rects agrees)")
        check(not _zz_bad and _zz_hot > 0,
              "B: reachability: in every room, period and stage of none to four people, on an ordinary day and on a rest day, "
              "each id of night_filter_actions(place_actions) is in the column or on a visible hotspot clear of everyone, "
              "never neither, never both; an id the night rule drops is offered by neither (%d cases, %d hotspot offers)"
              % (_zz_cases, _zz_hot), _zz_bad[:8])

        ## The same with night_can_work patched, as the plan words it.
        _zz_bad = []
        zz_r_fix("rich")
        for _zz_l in LOCATIONS:
            for _zz_per in PERIODS:
                period = _zz_per
                here = _zz_l
                zz_r_stage(_zz_l, 1)
                _zz_bad += [(_zz_l, _zz_per) + b for b in zz_with(dict(night_can_work=lambda: False), lambda: zz_r_reach(_zz_l))]
                _zz_off = zz_with(dict(night_can_work=lambda: False),
                                  lambda: [_zz_h["act"] for _zz_h in hot_spots_for(_zz_l) if _zz_h["act"] in NIGHT_REST_BLOCKS])
                if _zz_off:
                    _zz_bad.append((_zz_l, _zz_per, "a rest-day id on a hotspot", _zz_off))
        check(not _zz_bad, "B/C: with night_can_work patched to False the rule still holds, and no hotspot offers an id in "
              "NIGHT_REST_BLOCKS", _zz_bad[:6])
        note("B: the Night and rest-day half", "ran against P4b's real rule (fixture: the day after a Gojo night), and again "
             "with night_can_work patched as the plan words it; nothing is deferred to P8")

    ## On the drawn screen: the hotspot's rectangle from zz_rect.
    python:
        _zz_bad = []
        _zz_drawn = 0
        _zz_first = dict(utahime_office=("utahime",), infirmary=("shoko",))
        for _zz_l in builtins.sorted(set(v[0] for v in ZZ_R_TABLE.values())):
            for _zz_n in (0, 1, 2, 3, 4):
                zz_r_fix("fresh" if (_zz_l == "storehouse" and _zz_n % 2) else "rich", period="Afternoon", here=_zz_l)
                zz_r_stage(_zz_l, _zz_n, _zz_first.get(_zz_l, ()))
                renpy.show_screen("sb_place")
                _zz_rets = zz_r_rets("sb_place")
                _zz_rects = view_person_rects(_zz_l)
                for _zz_h in hot_spots_for(_zz_l):
                    if _zz_h["id"].startswith("zz"):
                        continue
                    _zz_box = zz_rect("sb_place", "hot_" + _zz_h["id"])
                    _zz_drawn += 1
                    if _zz_box is None:
                        _zz_bad.append((_zz_l, _zz_n, _zz_h["id"], "no button drawn"))
                        continue
                    if max(abs(a - b) for a, b in zip(_zz_box, hot_rect(_zz_h["x"], _zz_h["y"]))) > 2:
                        _zz_bad.append((_zz_l, _zz_n, _zz_h["id"], "drawn at", _zz_box, hot_rect(_zz_h["x"], _zz_h["y"])))
                    if not _zz_h["standalone"] and any(hot_overlap(_zz_box, p) for p in _zz_rects):
                        _zz_bad.append((_zz_l, _zz_n, _zz_h["id"], "meets a person", _zz_box))
                    _zz_ret = ("hot", _zz_h["id"]) if _zz_h["lines"] is not None else ("act", _zz_h["act"])
                    if _zz_ret not in _zz_rets:
                        _zz_bad.append((_zz_l, _zz_n, _zz_h["id"], "not a return of the screen", _zz_ret))
                    if _zz_h["lines"] is None and not _zz_h["standalone"] and _zz_h["act"] in zz_r_ids(rail_actions(_zz_l)):
                        _zz_bad.append((_zz_l, _zz_n, _zz_h["id"], "also in the column"))
                for _zz_a in rail_actions(_zz_l):
                    if ("act", _zz_a[0]) not in _zz_rets:
                        _zz_bad.append((_zz_l, _zz_n, _zz_a[0], "a column row with no return"))
                if _zz_n == (1 if _zz_l not in ("dorm", "library", "ridge", "riverside", "courtyard") else 0):
                    shot("room_" + _zz_l)
                renpy.hide_screen("sb_place")
        ## The "+N" chip (five or more in a room) and the card table beside it.
        _zz_chip = []
        for _zz_n in (5, len(store.roster)):
            zz_r_fix("rich", period="Afternoon", here="dorm_common")
            _zz_got = zz_r_stage("dorm_common", _zz_n)
            renpy.show_screen("sb_place")
            zz_render()
            _zz_box = zz_rect("sb_place", "hot_card_table")
            _zz_more = [zz_rect("sb_place", "rail_more_" + _zz_w) for _zz_w in who_is_here("dorm_common")]
            _zz_more = [_zz_m for _zz_m in _zz_more if _zz_m]
            _zz_top = min(_zz_m[1] for _zz_m in _zz_more) - 44 if _zz_more else None
            _zz_chip.append((_zz_n, _zz_got, _zz_box, _zz_more, _zz_top))
            if _zz_n == 5:
                shot("room_dorm_common_five")
                check(_zz_got == 5 and len(_zz_more) == 1 and (_zz_box is None or _zz_box[1] + _zz_box[3] <= _zz_top),
                      "B: five in the common room: the card table's hotspot is clear of the \"+1\" chip (or hidden by a person)",
                      _zz_chip[-1])
            else:
                shot("room_dorm_common_all")
                note("B: everyone in the common room: the card table and the \"+N\" chip", _zz_chip[-1])
            renpy.hide_screen("sb_place")
        check(not _zz_bad and _zz_drawn >= 30,
              "B: on the drawn place view (eleven rooms, none to four people) each visible hotspot's rectangle (zz_rect) is "
              "its 72 px square, meets no rectangle of view_person_rects, and its return is one of hot_layer's (%d buttons)"
              % _zz_drawn, _zz_bad[:8])

    ############################################################################
    ## C. A hotspot follows its action
    ############################################################################
    python:
        zz_r_fix("rich", here="infirmary")
        zz_r_stage("infirmary", 0)
        _zz_before = zz_r_hot_ids("infirmary")
        autoplay(True)
    call sb_do_rest
    python:
        autoplay(False)
        check("cot" in _zz_before and "cot" not in zz_r_hot_ids("infirmary") and "rest" not in zz_r_ids(rail_actions("infirmary")),
              "C: after sb_do_rest the cot is gone (and the column has no rest either)", (_zz_before, zz_r_hot_ids("infirmary")))

        zz_r_fix("rich", here="utahime_office")
        zz_r_stage("utahime_office", 1, ("utahime",))
        _zz_open = (board_open(), zz_r_hot_ids("utahime_office"))
        zz_r_stage("utahime_office", 0)
        _zz_shut = (board_open(), zz_r_hot_ids("utahime_office"))
        check(_zz_open == (True, ["board"]) and _zz_shut == (False, []),
              "C: with the board closed (Utahime out) its hotspot is gone; with her in, it is there", (_zz_open, _zz_shut))

        zz_r_fix("rich", here="ridge")
        zz_r_stage("ridge", 0)
        _zz_before = zz_r_hot_ids("ridge")
        autoplay(True)
    call sb_do_veil
    python:
        autoplay(False)
        check(_zz_before == ["veil"] and zz_r_hot_ids("ridge") == [], "C: after one look the veil hotspot is gone",
              (_zz_before, zz_r_hot_ids("ridge")))

        zz_r_fix("rich")
        store.explore_mode = True
        _zz_bad = []
        for _zz_l in LOCATIONS:
            for _zz_per in PERIODS:
                period = _zz_per
                here = _zz_l
                zz_r_stage(_zz_l, 0)
                _zz_bad += [(_zz_l, _zz_h["id"]) for _zz_h in hot_spots_for(_zz_l) if _zz_h["lines"] is None and not _zz_h["id"].startswith("go_")]
        _zz_looks = zz_r_hot_ids("classroom")
        store.explore_mode = False
        check(not _zz_bad and _zz_looks == ["blackboard"],
              "C: in explore mode hot_spots_for returns no action and no standalone hotspot (a look stays)", _zz_bad[:6])

        zz_r_fix("fresh", here="storehouse")
        zz_r_stage("storehouse", 0)
        _zz_a = zz_r_hot_ids("storehouse")
        flag("armory_open")
        _zz_b = zz_r_hot_ids("storehouse")
        check(_zz_a == ["racks"] and _zz_b == ["armory"],
              "C: the storehouse shows `tools` before armory_open and `armory` after, never both", (_zz_a, _zz_b))

        zz_r_fix("rich")
        zz_r_rest_day()
        _zz_bad = []
        for _zz_l in LOCATIONS:
            for _zz_per in PERIODS:
                period = _zz_per
                here = _zz_l
                zz_r_stage(_zz_l, 0)
                _zz_bad += [(_zz_l, _zz_h["id"]) for _zz_h in hot_spots_for(_zz_l) if _zz_h["act"] in NIGHT_REST_BLOCKS]
        check(not night_can_work() and not _zz_bad, "C: on a rest day no hotspot offers an id in NIGHT_REST_BLOCKS", _zz_bad[:6])

        zz_r_fix("rich", here="courtyard", period="Afternoon")
        zz_r_stage("courtyard", 1)
        _zz_pt = [_zz_h for _zz_h in HOT_SPOTS if _zz_h["id"] == "spot_vend"][0]
        _zz_box = (_zz_pt["x"] - 200, _zz_pt["y"] - 400, 400, 800)
        _zz_rows = zz_with(dict(view_person_rects=lambda loc: [_zz_box]),
                           lambda: [_zz_h for _zz_h in hot_spots_for("courtyard") if _zz_h["id"] == "spot_vend"])
        check(len(_zz_rows) == 1 and _zz_rows[0]["front"] is True and _zz_rows[0]["standalone"] is True,
              "C: the standalone is never hidden by a person: with view_person_rects patched to a box over the machine "
              "(pose 11's case) spot_vend is still in hot_spots_for('courtyard'), with front True", _zz_rows)
        _zz_bad = [n for n in (1, 2, 3, 4) if any(hot_overlap(hot_rect(_zz_pt["x"], _zz_pt["y"]), p)
                                                  for p in view_slot_rects("courtyard", n))]
        check(not _zz_bad, "C: the machine's point is clear of where one to four people stand today", _zz_bad)

    ############################################################################
    ## D. The vending machine; a look's use
    ############################################################################
    python:
        zz_r_fix("rich", here="courtyard", period="Afternoon", yen=1000, stamina=50)
        _zz_ok0 = spot_vend_ok()
        _zz_h = [_zz_h for _zz_h in hot_spots_for("courtyard") if _zz_h["id"] == "spot_vend"][0]
        _zz_act = hot_action(_zz_h)
        autoplay(True)
    call sb_do_spot_vend
    python:
        check(_zz_ok0 and isinstance(_zz_act, Return) and _zz_act.value == ("act", "spot_vend")
              and yen == 1000 - 150 and stamina == 60,
              "D: the vending machine: sb_do_spot_vend takes ¥150 and gives stamina +10", (yen, stamina))
        check(not spot_vend_ok() and "spot_vend" not in zz_r_hot_ids("courtyard"),
              "D: spot_vend_ok() is then False for the rest of the day, and the machine's hotspot is gone")
        _zz_was = (yen, stamina)
    call sb_do_spot_vend
    python:
        check((yen, stamina) == _zz_was, "D: a second can the same day is refused and costs nothing", (yen, stamina))
        new_day()
        check(spot_vend_ok() and "spot_vend" in zz_r_hot_ids("courtyard"), "D: …and True again the next day")
        yen = 100
        stamina = 50
        _zz_was = (yen, stamina, builtins.set(actions_today))
    call sb_do_spot_vend
    python:
        check((yen, stamina, builtins.set(actions_today)) == _zz_was and spot_vend_ok(),
              "D: with ¥100 it is refused and nothing changes", (yen, stamina, actions_today))
        zz_r_fix("rich", here="classroom", day=9)
        zz_r_stage("classroom", 0)
        _zz_n0 = len(zz_r.texts)
        _zz_line = hot_line("blackboard")
    call hot_use("blackboard")
    python:
        autoplay(False)
        check("hot:blackboard" in actions_today and zz_r_said(_zz_n0, _zz_line),
              "D: a look hotspot's use says today's line and adds hot:<id> to actions_today", builtins.sorted(actions_today))

    ############################################################################
    ## F. Registration
    ############################################################################
    python:
        _zz_src = zz_r_src("room_spots.rpy")
        _zz_at = [m.start() for m in re.finditer(r"register_hotspot\(", _zz_src)]
        _zz_blocks = [(m.start(), m.group(1)) for m in re.finditer(r"(?m)^init( -?\d+)? python:", _zz_src)]
        _zz_levels = [int(([b[1] for b in _zz_blocks if b[0] < at] or [None])[-1] or 0) for at in _zz_at]
        check(_zz_at and all(l >= 0 for l in _zz_levels),
              "F: every register_hotspot call of room_spots.rpy sits in an `init python:` block (init 0); the registry "
              "is made at init -5", _zz_levels)
        _zz_bad = [f for f in ZZ_R_FILES if "register_minigame(" in zz_r_src(f)]
        check(not _zz_bad, "F: none of P6's files registers a minigame", _zz_bad)

    ############################################################################
    ## G. The computer
    ############################################################################
    python:
        zz_r_fix("rich", here="dorm")
        check(("pc_open", "My computer") in [(a[0], a[1]) for a in place_actions("dorm")]
              and [a[3] for a in place_actions("dorm") if a[0] == "pc_open"] == [0]
              and "pc_open" not in zz_r_ids(place_actions("dorm_common")),
              "G: place action pc_open, 'My computer', free, in my room only")
        check(len(PC_PAGES) == 12 and len(PC_SITES) == 5 and len(pc_pages()) == 12,
              "G: five sites, twelve pages, all twelve counted with the market built and the veil seen", pc_pages())
        _zz_i0 = insight
        autoplay(True)
    call sb_do_pc_open
    python:
        autoplay(False)
        check(pc_has_read("home") and pc_read == {"home"} and has_flag("researched_home") and insight == _zz_i0 + 1,
              "G: sb_do_pc_open under autoplay returns; opening the computer reads Home (Insight +1, once)",
              (pc_read, insight - _zz_i0))

        ## Reading, through the label and the screen's own returns.
        _zz_i0 = insight
        zz_r_drive([("page", "techniques"), ("page", "clans"), ("page", "techniques"), ("page", "zz_no_such_page"), ("close",)])
    call sb_do_pc_open
    python:
        zz_r_stop()
        check(zz_r.seen == ["pc_screen"] * 5 and pc_read == {"home", "techniques", "clans"}
              and has_flag("researched_techniques") and has_flag("researched_clans")
              and insight == _zz_i0 + 2 + 1,
              "G: reading a page adds it to pc_read and sets researched_<page>; Insight comes once only "
              "(techniques +2 in place of the usual +1; a second read and a second Home give nothing)",
              (zz_r.seen, builtins.sorted(pc_read), insight - _zz_i0))
        check(all(pc_has_read(p) == (p in pc_read) for p in PC_PAGES) and pc_has_read("clans") and not pc_has_read("gojo"),
              "G: pc_has_read agrees with pc_read")
        check(pc_records() == [PC_PAGES[p]["title"] for p in ("home", "techniques", "clans")],
              "G: pc_records() returns the titles of the pages read", pc_records())
        check(pc_noted == "", "G: the Noted strip is cleared when the computer is closed", pc_noted)

        ## Every page renders.
        zz_r_fix("rich", here="dorm")
        _zz_bad = []
        for _zz_p in PC_PAGE_ORDER:
            pc_noted = pc_visit(_zz_p)
            renpy.show_screen("pc_screen", _zz_p)
            _zz_tx = zz_texts("pc_screen")
            if PC_PAGES[_zz_p]["title"] not in _zz_tx or not all(b in _zz_tx for b in PC_PAGES[_zz_p]["body"]):
                _zz_bad.append((_zz_p, "title or body missing"))
            if not [t for t in _zz_tx if t.startswith("Noted.")]:
                _zz_bad.append((_zz_p, "no Noted strip on a first read"))
            if zz_rect("pc_screen", "pc_close") is None or zz_rect("pc_screen", "pc_mark_" + _zz_p) is None:
                _zz_bad.append((_zz_p, "no close button or no bookmark"))
            shot("pc_" + _zz_p, wait=0.1)
            renpy.hide_screen("pc_screen")
        check(not _zz_bad and len(pc_read) == 12, "G: all twelve pages render (title, body, the Noted strip, the bookmarks)", _zz_bad)
        check(has_flag("market_found") and has_flag("researched_legends_market"),
              "G: legends_market sets market_found (in place of the Insight)")
        check(all(has_flag("researched_" + p) for p in PC_PAGES), "G: every page read set its researched_<page> flag")
        _zz_words = [len(" ".join(p["body"]).split()) for k, p in PC_PAGES.items() if k not in ("home", "board_reports")]
        note("G: page lengths", "the ten written pages run from %d to %d words" % (min(_zz_words), max(_zz_words)))
        check(min(_zz_words) >= 60 and max(_zz_words) <= 160, "G: each written page is about 100 words (60 to 160)", _zz_words)

        ## The hidden page.
        zz_r_fix("rich", here="dorm")
        flags.discard("saw_the_ridge_veil")
        renpy.show_screen("pc_screen", "sukuna_folk")
        _zz_a = ("sukuna" in pc_pages(), zz_rect("pc_screen", "pc_mark_sukuna"), zz_rect("pc_screen", "pc_link_sukuna"),
                 ("page", "sukuna") in zz_r_rets("pc_screen"), pc_leads())
        renpy.show_screen("pc_screen", "sukuna")
        _zz_home = PC_PAGES["home"]["title"] in zz_texts("pc_screen") and PC_PAGES["sukuna"]["title"] not in zz_texts("pc_screen")
        _zz_v = pc_visit("sukuna")
        flag("saw_the_ridge_veil")
        renpy.show_screen("pc_screen", "sukuna_folk")
        _zz_b = ("sukuna" in pc_pages(), zz_rect("pc_screen", "pc_mark_sukuna") is not None,
                 zz_rect("pc_screen", "pc_link_sukuna") is not None, ("page", "sukuna") in zz_r_rets("pc_screen"))
        renpy.hide_screen("pc_screen")
        check(_zz_a == (False, None, None, False, []) and _zz_home and _zz_v == "" and not pc_has_read("sukuna")
              and _zz_b == (True, True, True, True),
              "G: `sukuna` is hidden until saw_the_ridge_veil: not listed, not linked, not readable, no request; then all four",
              (_zz_a, _zz_home, _zz_v, _zz_b))
        check(pc_leads() == [("sukuna", "What was that on the ridge?")],
              "G: the one request that ships: once the ridge veil is seen and `sukuna` is unread", pc_leads())

        ## The market page, with market_exists() both ways.
        def _zz_market_view():
            renpy.show_screen("pc_screen", "legends")
            out = ("legends_market" in pc_pages(), len(pc_pages()), zz_rect("pc_screen", "pc_mark_legends_market") is not None,
                   zz_rect("pc_screen", "pc_link_legends_market") is not None,
                   [p for p in PC_PAGES if "legends_market" in pc_links(p)], pc_visit("legends_market") != "")
            renpy.hide_screen("pc_screen")
            return out
        _zz_off = zz_with(dict(market_exists=lambda: False), _zz_market_view)
        _zz_flag = has_flag("market_found")
        _zz_on = zz_with(dict(market_exists=lambda: True), _zz_market_view)
        del _zz_market_view
        check(_zz_off == (False, 11, False, False, [], False) and not _zz_flag,
              "G: with market_exists() False legends_market is not listed, no page links to it, it can't be read and "
              "eleven pages are counted", _zz_off)
        check(_zz_on == (True, 12, True, True, ["legends"], True) and has_flag("market_found"),
              "G: with market_exists() True it is listed, linked from the board's thread, and reading it sets market_found",
              _zz_on)
        note("G: the rumour page", "market_exists() is P4b's real function here (True): the page ships; nothing is deferred")

        ## A request.
        zz_r_fix("rich", here="dorm")
        _zz_ret = pc_request("clan_zenin", "Ask the register about Maki's family")
        pc_request("clan_zenin", "A second ask for the same page")
        pc_request("zz_no_such_page", "Nothing")
        renpy.show_screen("pc_screen", "home")
        _zz_tx = zz_texts("pc_screen")
        _zz_btn = zz_rect("pc_screen", "pc_lead_clan_zenin")
        _zz_fit = [zz_rect("pc_screen", "pc_site_" + _zz_k) for _zz_k in PC_SITE_ORDER]
        _zz_n = len(pc_leads())
        shot("pc_home_requests", wait=0.1)
        renpy.hide_screen("pc_screen")
        check(_zz_n == 2 and _zz_tx.index("REQUESTED READING") < _zz_tx.index(PC_PAGES["home"]["body"][0]) < _zz_tx.index("SITES")
              and all(r is not None and r[3] >= 30 and r[1] + r[3] <= 926 for r in _zz_fit),
              "G: on Home the requests come first, then the intranet's lines, then the sites; with two requests all five "
              "site cards are inside the page without a scroll (4.11)", (_zz_n, _zz_fit))
        pc_request("clan_gojo", "Who signs [the] 7-C {zz}forms")
        renpy.show_screen("pc_screen", "home")
        _zz_tx2 = zz_texts("pc_screen")
        _zz_btn2 = zz_rect("pc_screen", "pc_lead_clan_gojo")
        shot("pc_home_brackets", wait=0.1)
        renpy.hide_screen("pc_screen")
        check("Who signs [the] 7-C {{zz}forms" in _zz_tx2 and _zz_btn2 is not None and _zz_btn2[2] > 250,
              "G: a request's note is drawn as written: square brackets are not substituted and a brace is not a text tag "
              "(an unknown tag would raise)", _zz_tx2[:8])
        store.pc_requests = [r for r in pc_requests if r[0] != "clan_gojo"]
        check(_zz_ret is None and pc_requests == [("clan_zenin", "Ask the register about Maki's family")]
              and ("clan_zenin", "Ask the register about Maki's family") in pc_leads()
              and "Ask the register about Maki's family" in _zz_tx and "REQUESTED READING" in _zz_tx and _zz_btn is not None,
              "G: pc_request('clan_zenin', …) shows on Home and in pc_leads(); a repeat and an unknown page add nothing",
              (pc_requests, pc_leads()))
        _zz_lead = jr_leads()
        pc_visit("clan_zenin")
        pc_visit("sukuna")
        check(pc_leads() == [] and pc_requests == [("clan_zenin", "Ask the register about Maki's family")],
              "G: a request closes when its page is read (pc_leads() is the open ones)", pc_leads())
        check(any("Ask the register about Maki's family" in str(r) for r in _zz_lead) and any("ridge" in str(r) for r in _zz_lead),
              "G (7.3, with P3 in): the journal's Missions tab reads both leads through jr_leads()", _zz_lead)
        _zz_rec = builtins.dict(jr_records())
        ## P8: the record book is listed from my first catch on (ui_journal.rpy).
        _zz_caught = any(r[1] for r in fish_records())
        check(_zz_rec.get("PAGES I'VE READ") == pc_records()
              and len(_zz_rec.get("THE RECORD BOOK", [])) == (len(fish_records()) if _zz_caught else 0),
              "G (7.3, with P3 in): the journal's Me page lists the pages read through jr_records(), and the record book "
              "once something is caught", (_zz_caught, _zz_rec))

        ## The pages' text.
        _zz_bad = []
        for _zz_k, _zz_p in builtins.sorted(PC_PAGES.items()):
            for _zz_t in [_zz_p["title"]] + builtins.list(_zz_p["body"]):
                if re.search(r"\b(you|your|yours|yourself)\b", _zz_t, re.I) or any(n in _zz_t for n in ZZ_R_NAMES):
                    _zz_bad.append((_zz_k, _zz_t[:60]))
        for _zz_k, _zz_s in PC_SITES.items():
            if re.search(r"\b(you|your)\b", _zz_s["name"] + " " + _zz_s["tone"], re.I):
                _zz_bad.append((_zz_k, _zz_s["tone"]))
        check(not _zz_bad, "G: no page text says you or your to the reader, and none carries the protagonist's default name", _zz_bad)
        check(all(PC_PAGES[p]["body"][-1].lower().find("restricted") >= 0 for p in ("clan_gojo", "clan_kamo", "clan_zenin"))
              and all(n in " ".join(PC_PAGES["clans"]["body"]) for n in ("Gojo", "Kamo", "Zen'in")),
              "G: each clan page ends on a restricted line, and the overview names all three houses")
        check(all(Color(getattr(gui, "pc_" + k)) for k in ("wiki", "blog", "intra", "gene", "board"))
              and len(set(pc_color(s) for s in PC_SITES)) == 5, "G: each site has its own colour token (gui.pc_*)")

    ############################################################################
    ## H. The cross-check
    ############################################################################
    python:
        zz_r_fix("rich", here="dorm", period="Morning")
        _zz_week = None
        for _zz_w in range(board_week_now(), board_week_now() + 400):
            _zz_gen = board_generate(_zz_w)
            if any(o["true_grade"] != o["grade"] for o in _zz_gen) and any(o["true_grade"] == o["grade"] for o in _zz_gen):
                _zz_week = _zz_w
                break
        if check(_zz_week is not None, "H: the board's own generator posts a week with a misgraded job"):
            day = _zz_week * 7 + 2
            board_offers = board_generate(_zz_week)
            board_week = _zz_week
            roll_gojo()
        _zz_before = pc_offers()
        _zz_want = [(o["title"], o["grade"], o["true_grade"] != o["grade"]) for o in board_offers if not o.get("taken_by")]
        check(len(_zz_before) == len(_zz_want) == 3 and not any(r[2] for r in _zz_before) and pc_check_ok(),
              "H: before the check the page lists the week's three offers by title and posted grade, none marked", _zz_before)
        renpy.show_screen("pc_screen", "board_reports")
        _zz_btn = (zz_rect("pc_screen", "pc_check") is not None, ("check",) in zz_r_rets("pc_screen"))
        renpy.hide_screen("pc_screen")
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([("page", "board_reports"), ("check",), ("check",), ("close",)])
    call sb_do_pc_open
    python:
        zz_r_stop()
        check(_zz_btn == (True, True) and pc_checked_week == board_week_now() and period == "Noon"
              and zz_r.seen == ["pc_screen"] * 4,
              "H: 'Cross-check the reports' costs one period and sets pc_checked_week; a second check the same week costs "
              "nothing", (_zz_btn, pc_checked_week, period, zz_r.seen))
        check(pc_offers() == _zz_want and any(r[2] for r in pc_offers()) and not all(r[2] for r in pc_offers())
              and zz_r_said(_zz_n0, "doesn't add up"),
              "H: the checked view marks exactly the offers whose true_grade != grade", (pc_offers(), _zz_want))
        renpy.show_screen("pc_screen", "board_reports")
        _zz_tx = zz_texts("pc_screen")
        _zz_gone = zz_rect("pc_screen", "pc_check") is None
        shot("pc_board_checked", wait=0.1)
        renpy.hide_screen("pc_screen")
        check(_zz_tx.count("This one doesn't add up.") == len([r for r in _zz_want if r[2]]) and _zz_gone
              and "Cross-checked this week." in _zz_tx,
              "H: the page shows 'This one doesn't add up.' on those offers, and the button is gone for the week", _zz_tx[-8:])
        _zz_snap = copy.deepcopy(board_offers)
        pc_offers()
        check(board_offers == _zz_snap, "H: the page only reads board_offers")
        ## A taken card is left out.
        _zz_first = board_offers_open()[0]
        board_take(_zz_first["id"], "megumi")
        check(len(pc_offers()) == 2 and _zz_first["title"] not in [r[0] for r in pc_offers()],
              "H: a card already taken is not listed", pc_offers())

        ## At Night it is refused.
        zz_r_fix("rich", here="dorm", period=PERIODS[-1])
        board_offers = board_generate(board_week_now())
        board_week = board_week_now()
        _zz_day = day
        renpy.show_screen("pc_screen", "board_reports")
        _zz_shut = (pc_check_ok(), ("check",) in zz_r_rets("pc_screen"), zz_rect("pc_screen", "pc_check"),
                    "Too late. Bed." in zz_texts("pc_screen"),
                    "Cross-check the reports · 1 period" in zz_texts("pc_screen"))
        shot("pc_board_night", wait=0.1)
        renpy.hide_screen("pc_screen")
        check(_zz_shut == (True, False, None, True, True),
              "H: at Night the cross-check button is drawn shut (it takes no focus and returns nothing), with "
              "'Too late. Bed.' under it", _zz_shut)
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([("page", "board_reports"), ("check",), ("close",)])
    call sb_do_pc_open
    python:
        zz_r_stop()
        check(pc_checked_week == -1 and period == PERIODS[-1] and day == _zz_day and zz_r_said(_zz_n0, "Too late. Bed."),
              "H: at Night the cross-check is refused (\"Too late. Bed.\"): nothing is marked and no time passes",
              (pc_checked_week, period, day))

    ############################################################################
    ## I. Fishing
    ############################################################################
    python:
        zz_r_fix("rich", here="riverside", control=12)
        check(("fish_cast", "Fish", 1) in [(a[0], a[1], a[3]) for a in place_actions("riverside")],
              "I: place action fish_cast, 'Fish', one period, at the riverside")
        check([k["id"] for k in FISH_KINDS][-2:] == ["river_lord", "pale_thing"] and len(FISH_KINDS) == 8
              and all(set(k) == {"id", "name", "min_cm", "max_cm", "weight", "zone", "yen_per_cm", "periods"} for k in FISH_KINDS),
              "I: FISH_KINDS is six species, river_lord and pale_thing, in 3.1's shape")

        ## 1,000 casts through the game's own functions, hooks of every quality.
        _zz_rng = renpy.random.Random(20261004)
        _zz_bad = []
        _zz_yen = 0
        _zz_caught = builtins.dict()
        _zz_pale = builtins.dict()
        _zz_lord = []
        _zz_log = builtins.dict()
        _zz_days = set()
        for _zz_i in range(1000):
            day = 9 + _zz_i // 20
            if day not in _zz_days:
                _zz_days.add(day)
                actions_today = set()
                flags.discard("caught_river_lord")       # so it can come up again: every appearance is tested
            period = PERIODS[_zz_i % 4]
            _zz_q = _zz_rng.random()
            _zz_y0 = yen
            _zz_res = fish_cast_once(_zz_q)
            for _zz_k, _zz_v in fish_log.items():
                if _zz_v < _zz_log.get(_zz_k, 0):
                    _zz_bad.append(("fish_log fell", _zz_k, _zz_v))
            _zz_log = builtins.dict(fish_log)
            if _zz_res is None:
                continue
            _zz_kind = fish_kind(_zz_res["id"])
            _zz_caught[_zz_res["id"]] = _zz_caught.get(_zz_res["id"], 0) + 1
            if yen - _zz_y0 != _zz_res["yen"]:
                _zz_bad.append(("paid", _zz_res, yen - _zz_y0))
            if _zz_res["id"] == "pale_thing":
                _zz_pale[fish_week()] = _zz_pale.get(fish_week(), 0) + 1
                if period != "Evening":
                    _zz_bad.append(("the pale thing outside the Evening", period))
                continue
            if not (_zz_kind["min_cm"] <= _zz_res["cm"] <= _zz_kind["max_cm"]):
                _zz_bad.append(("length", _zz_res))
            if period not in _zz_kind["periods"]:
                _zz_bad.append(("period", _zz_res["id"], period))
            if _zz_q < 1.0 - _zz_kind["zone"] - 1e-9:
                _zz_bad.append(("landed outside its zone", _zz_res["id"], _zz_q))
            if _zz_res["id"] == "river_lord":
                _zz_lord.append((period, round(_zz_q, 3)))
                if _zz_res["yen"] != FISH_LORD_YEN:
                    _zz_bad.append(("the River Lord's pay", _zz_res))
            else:
                if _zz_res["yen"] != _zz_res["cm"] * _zz_kind["yen_per_cm"] or not (100 <= _zz_res["yen"] <= 600):
                    _zz_bad.append(("yen", _zz_res))
                _zz_yen += _zz_res["yen"]
        _zz_n = sum(_zz_caught.values())
        check(not _zz_bad and _zz_n > 200 and all(_zz_caught.get(k["id"]) for k in FISH_KINDS[:6]),
              "I: 1,000 simulated casts (fish_roll, fish_hit, fish_length, fish_land): every length is inside its species' "
              "range, each of the six species came up, a catch sells for cm x yen_per_cm (¥100 to ¥600), and fish_log only "
              "ever rose (%d landed)" % _zz_n, _zz_bad[:6])
        check(all(p == "Evening" and q >= 0.9 for p, q in _zz_lord),
              "I: the River Lord never appeared outside the Evening or below q 0.9 (%d times in the 1,000)" % len(_zz_lord), _zz_lord)
        check(_zz_pale and max(_zz_pale.values()) == 1,
              "I: the pale thing came up at most once a week (%d weeks, %d times)" % (len(set((d - 1) // 7 for d in _zz_days)), sum(_zz_pale.values())),
              _zz_pale)
        _zz_cap = BOARD_YEN["g4"][0] // BOARD_PERIODS
        _zz_mean = 3.0 * _zz_yen / 1000.0
        check(_zz_mean < _zz_cap, "I: the mean yen of a three-cast sitting (¥%d, hooks of every quality) is below "
              "BOARD_YEN['g4'][0] // BOARD_PERIODS (¥%d)" % (_zz_mean, _zz_cap))

        ## The River Lord and the pale thing, tested directly.
        zz_r_fix("rich", here="riverside")
        _zz_bad = []
        for _zz_per in PERIODS:
            period = _zz_per
            _zz_got = set(fish_roll() for _zz_i in range(1500))
            if ("river_lord" in _zz_got) != (_zz_per == "Evening") or ("pale_thing" in _zz_got) != (_zz_per == "Evening"):
                _zz_bad.append((_zz_per, builtins.sorted(_zz_got)))
        check(not _zz_bad and not fish_hit("river_lord", 0.89) and fish_hit("river_lord", 0.9) and fish_hit("river_lord", 1.0),
              "I: the River Lord and the pale thing bite only in the Evening (1,500 rolls a period); the Lord needs q >= 0.9", _zz_bad)
        period = "Evening"
        _zz_y0 = yen
        _zz_a = fish_land("river_lord", 131)
        _zz_b = fish_land("river_lord", 120)
        check(_zz_a["yen"] == FISH_LORD_YEN and _zz_b["yen"] == 0 and yen == _zz_y0 + FISH_LORD_YEN and has_flag("caught_river_lord")
              and "river_lord" not in set(fish_roll() for _zz_i in range(1500)) and fish_log["river_lord"] == 131,
              "I: the River Lord pays ¥5,000 once, sets caught_river_lord, and does not bite again", (_zz_a, _zz_b))
        _zz_t0 = item_count("sealing_talisman")
        _zz_a = fish_land("pale_thing", 0)
        _zz_again = "pale_thing" in set(fish_roll() for _zz_i in range(1500))
        day += 7
        _zz_next = "pale_thing" in set(fish_roll() for _zz_i in range(1500))
        check(item_count("sealing_talisman") == _zz_t0 + 1 and fish_cursed_week == board_week_now() - 1 and not _zz_again and _zz_next
              and "pale_thing" not in fish_log and _zz_a["yen"] == 0,
              "I: the pale thing leaves one sealing talisman, marks the week, and can come up again only the week after")

        ## The best a perfect angler can do.
        zz_r_fix("rich", here="riverside")
        _zz_best = builtins.dict()
        for _zz_per in PERIODS[:-1]:
            period = _zz_per
            _zz_y0 = yen
            for _zz_i in range(600):
                fish_cast_once(1.0)
            _zz_best[_zz_per] = int(3.0 * (yen - _zz_y0) / 600.0)
            yen = _zz_y0
        check(max(_zz_best.values()) < _zz_cap,
              "I (D29): with every hook dead centre a sitting still earns less a period than the cheapest board job "
              "(¥%d; the River Lord's one-off included)" % _zz_cap, _zz_best)
        note("I: yen a sitting, every hook dead centre", _zz_best)

        ## The first catch of the day.
        zz_r_fix("rich", here="riverside", control=12)
        _zz_c0 = control
        _zz_a = fish_land("ayu", 20)
        _zz_c1 = control
        fish_land("ayu", 22)
        check(_zz_c1 == _zz_c0 + 1 and control == _zz_c1 and "fish_first" in actions_today,
              "I: the day's first catch gives Control +1 once (fish_first); a second gives none", (_zz_c0, _zz_c1, control))
        check(_zz_a == dict(id="ayu", cm=20, yen=20 * fish_kind("ayu")["yen_per_cm"], record=True)
              and fish_land("ayu", 21)["record"] is False and fish_log["ayu"] == 22,
              "I: fish_land returns dict(id, cm, yen, record); the record is my longest and never falls", (_zz_a, fish_log))
        ## The result line: a species' first catch is "the first in the
        ## book"; "a new best" needs an earlier best to beat.
        _zz_said = []
        for _zz_old in (None, 1, 999):
            fish_log.pop("ayu", None)
            if _zz_old:
                fish_log["ayu"] = _zz_old
            fish_begin()
            fish_next()
            fish_state["kind"] = "ayu"
            _zz_said.append(fish_settle(("hook", 1.0)))
            fish_end()
        check("The first in the book." in _zz_said[0] and "A new best." not in _zz_said[0]
              and "A new best." in _zz_said[1] and "first in the book" not in _zz_said[1]
              and "A new best." not in _zz_said[2] and "first in the book" not in _zz_said[2]
              and all(t.startswith("Ayu, ") and "The kitchen will give me" in t for t in _zz_said),
              "I: a species' first catch says 'The first in the book.', a longer one later 'A new best.', a shorter "
              "one neither", _zz_said)
        new_day()
        _zz_c0 = control
        zz_with(dict(night_can_work=lambda: False), lambda: fish_land("ayu", 20))
        _zz_c1 = control
        zz_r_fix("rich", here="riverside", control=12)
        zz_r_rest_day()
        fish_land("ayu", 20)
        check(_zz_c1 == _zz_c0 and control == 12 and not night_can_work(),
              "I: on a rest day the first catch gives no Control (night_can_work patched to False, and P4b's real rest day)",
              (_zz_c0, _zz_c1, control))

        ## A companion.
        zz_r_fix("rich", here="riverside")
        companion = "yuji"
        _zz_b0 = bonds["yuji"]
        fish_begin()
        fish_next()
        fish_settle(("miss",))
        _zz_b1 = bonds["yuji"]
        fish_next()
        fish_settle(("hook", 1.0))
        check(_zz_b1 == _zz_b0 + 2 and bonds["yuji"] == _zz_b1 and "fish_bond" in actions_today,
              "I: a companion gains Bond +2 once a day (fish_bond)", (_zz_b0, _zz_b1, bonds["yuji"]))
        fish_end()
        companion = None

        ## fish_Hook.
        zz_r_fix("rich", here="riverside")
        fish_begin()
        fish_next()
        fish_strike()
        fish_state["centre"] = 0.3
        _zz_h1 = fish_Hook()()
        time.sleep(0.2)
        _zz_h2 = fish_Hook()()
        _zz_pos = fish_marker(time.time() - fish_state["t0"])
        check(isinstance(_zz_h1, tuple) and len(_zz_h1) == 2 and _zz_h1[0] == "hook" and isinstance(_zz_h1[1], float)
              and 0.0 <= _zz_h1[1] <= 1.0 and _zz_h2[0] == "hook" and _zz_h1[1] != _zz_h2[1],
              "I: fish_Hook()() returns ('hook', q), q a float 0.0 to 1.0 that follows the clock (two calls 0.2 s apart differ)",
              (_zz_h1, _zz_h2))
        check(abs(_zz_h2[1] - fish_quality(_zz_pos, fish_state["centre"])) < 0.08 and fish_marker(0) == 0.0
              and abs(fish_marker(FISH_SWEEP) - 1.0) < 1e-6 and fish_marker(FISH_SWEEP * 2) == 0.0
              and abs(fish_marker(FISH_SWEEP * 1.5) - 0.5) < 1e-6 and fish_quality(0.5, 0.5) == 1.0,
              "I: the marker crosses the bar and comes back (two passes), and q is 1.0 on the middle of the zone")
        fish_end()
        _zz_cls = []
        for _zz_f in ZZ_R_FILES:
            _zz_cls += re.findall(r"(?m)^\s*class\s+(\w+)\s*\(([^)]*)\)", zz_r_src(_zz_f))
        check(_zz_cls == [("fish_Hook", "Action")] and issubclass(fish_Hook, Action),
              "I: fish_Hook is the only action class the package adds (every other button is a Return, a "
              "SetScreenVariable or Function(ui_do, …))", _zz_cls)

        ## A whole sitting, through the label and the screen.
        zz_r_fix("rich", here="riverside", period="Morning", control=12)
        zz_r.keep["roll"] = []
        del zz_r.lines[:]
        del zz_r.blocks[:]
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([("hook", 1.0), ("hook", 0.0), ("hook", 1.0)],
                   on_show=lambda name: zz_r.keep["roll"].append((fish_state.get("cast"), fish_state.get("settled"), renpy.can_rollback())))
    call sb_do_fish_cast
    python:
        zz_r_stop()
        _zz_roll = zz_r.keep["roll"]
        check(zz_r.seen == ["fish_screen"] * 3 and period == "Noon" and fish_state == {} and len(fish_log) >= 1,
              "I: three casts are one sitting and cost one period (advance_period_soft); fish_state is {} afterwards",
              (zz_r.seen, period, fish_state))
        check([r[:2] for r in _zz_roll] == [(1, 0), (2, 1), (3, 2)] and not [r for r in _zz_roll if r[2]]
              and zz_r.blocks == [False] * 6,
              "I: rollback is blocked when a cast is dealt and again when it is settled (a catch or a miss): "
              "renpy.can_rollback() is False straight after each of the sitting's six renpy.block_rollback() calls, "
              "and already False while the first cast is on screen", (_zz_roll, zz_r.blocks))
        note("I: rollback", "the result line that follows a settled cast is a new checkpoint, so rollback can reach that "
             "line again but never the cast before it")
        check(len([t for t in zz_r.lines if " cm." in t]) == 2 and len([t for t in zz_r.lines if t in FISH_MISS_LINES]) == 1
              and len(zz_r_said(_zz_n0, "[_fish_line]")) >= 3,
              "I: each cast says its result line (two catches with their length, one miss)", (zz_r.lines, zz_r.texts[_zz_n0:]))

        ## Leaving: at once it is free; after a cast it costs the period.
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r_drive([("leave",)])
    call sb_do_fish_cast
    python:
        zz_r_stop()
        _zz_a = (period, fish_state)
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r_drive([("miss",), ("leave",)])
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(_zz_a == ("Morning", {}) and (period, fish_state) == ("Noon", {}),
              "I: packing up while the first cast's float still sits costs nothing; after one cast it costs the period",
              (_zz_a, period))

        ## Packing up once the float has dipped: the zone has shown what is
        ## on the line, so the cast is spent (D33: a cast can't be taken again).
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r.keep["wait"] = store.FISH_WAIT
        setattr(store, "FISH_WAIT", (0.2, 0.4))
        zz_r.keep["phases"] = []
        zz_r.keep["bite_kind"] = None
        del zz_r.lines[:]
        del zz_r.blocks[:]
        _zz_y0 = yen
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([], own=zz_r_leave_at_bite)
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(zz_r.keep["phases"] == [(1, "wait"), (1, "bite")] and period == "Noon" and fish_state == {} and yen == _zz_y0
              and len(zz_r.lines) == 1 and zz_r.lines[0] == zz_with(dict(fish_state=dict(cast=1)), lambda: fish_miss_line(zz_r.keep["bite_kind"]))
              and zz_r_said(_zz_n0, "I lift the rod while it is still making up its mind.")
              and not [t for t in zz_r.texts[_zz_n0:] if t in FISH_MISS_LINES]
              and len(zz_r_said(_zz_n0, "[_fish_line]")) <= 2
              and zz_r.blocks == [False, False],
              "I: Pack up once the float has dipped (the screen's own wait timer brought the bite) is a miss: the cast "
              "is settled as one, the line said is the put-the-rod-down one (not a struck-and-missed line), the period "
              "is charged, nothing is paid, and renpy.can_rollback() is False after the block",
              (zz_r.keep["phases"], period, fish_state, zz_r.lines, zz_r.texts[_zz_n0:], zz_r.blocks))

        ## Esc / right-click with the record book open closes the book; it
        ## does not pack up. The float's wait starts again when it closes.
        zz_r_fix("rich", here="riverside", period="Morning")
        for _zz_k in ("eb_t", "eb_open", "eb_key", "eb_after", "eb_cast0", "eb_cast1"):
            zz_r.keep.pop(_zz_k, None)
        del zz_r.lines[:]
        zz_r_drive([], own=zz_r_esc_book)
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(zz_r.keep.get("eb_open") == (True, 2, "wait") and zz_r.keep.get("eb_after") == (False, 2, "wait", 1)
              and zz_r.keep.get("eb_cast1", 0) >= zz_r.keep.get("eb_key", 1e18) - 0.01
              and zz_r.keep.get("eb_cast1", 0) > zz_r.keep.get("eb_cast0", 1e18)
              and len(zz_r.lines) == 1 and period == "Noon" and fish_state == {},
              "I: with the record book open in cast 2's wait, the game_menu key (queued through the keymap) closes the "
              "book and nothing else: fish_screen is still up on cast 2, nothing more is settled, and the float's wait "
              "starts again from the moment the book closed",
              (zz_r.keep.get("eb_open"), zz_r.keep.get("eb_after"), zz_r.keep.get("eb_cast0"), zz_r.keep.get("eb_key"),
               zz_r.keep.get("eb_cast1"), zz_r.lines, period))
        _zz_a = zz_with(dict(fish_state=dict(phase="bite", t_cast=5.0)), lambda: (fish_rewait(), fish_state["t_cast"]))
        _zz_b = zz_with(dict(fish_state={}), lambda: (fish_rewait(), dict(fish_state)))
        check(_zz_a == (None, 5.0) and _zz_b == (None, {}),
              "I: fish_rewait() returns None and leaves a cast that has already bitten, or no sitting, alone", (_zz_a, _zz_b))
        _zz_a = [zz_with(dict(day=_zz_d), fish_open_line) for _zz_d in range(1, 7)]
        check(len(set(_zz_a[:3])) == 3 == len(FISH_OPEN_LINES) and _zz_a[:3] == _zz_a[3:]
              and not [t for t in FISH_OPEN_LINES if "[" in t or "{" in t],
              "I: the sitting's opening line changes with the day (three lines, then round again)", _zz_a[:3])

        ## The rollback key at the bite (D33): the zone has shown what is on
        ## the line, so neither the key nor renpy.rollback() may take the
        ## cast back to its wait, or out of the sitting.
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r.keep["phases"] = []
        for _zz_k in ("rb_t", "rb_can", "rb_settled", "rb_asked", "rb_after"):
            zz_r.keep.pop(_zz_k, None)
        del zz_r.lines[:]
        zz_r_drive([], own=zz_r_roll_at_bite)
    "A line before the sitting, so there is somewhere to roll back to."
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(zz_r.keep.get("rb_can") is False and zz_r.keep.get("rb_asked")
              and zz_r.keep["phases"] == [(1, "wait"), (1, "bite"), (2, "wait")]
              and zz_r.keep.get("rb_after") == (1, "bite", zz_r.keep.get("rb_settled")) and zz_r.keep.get("rb_settled") == 0
              and len(zz_r.lines) == 1 and " cm." in zz_r.lines[0] and period == "Noon" and fish_state == {},
              "I (D33): at the bite of cast 1 the rollback key (queued through the keymap) and renpy.rollback() do "
              "nothing: the screen stays in its bite, never returns to the wait, nothing is settled by it; the hook "
              "that follows lands and the period is charged",
              (zz_r.keep.get("rb_can"), zz_r.keep["phases"], zz_r.keep.get("rb_after"), zz_r.lines, period))

        ## The screen's own timers, nothing answered: the wait timer brings
        ## the bite, the sweep's timer returns the miss, three times over.
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r.keep["phases"] = []
        del zz_r.lines[:]
        _zz_t0 = time.time()
        zz_r_drive([], own=zz_r_phase)
    call sb_do_fish_cast
    python:
        zz_r_stop()
        setattr(store, "FISH_WAIT", zz_r.keep.pop("wait"))
        _zz_dt = time.time() - _zz_t0
        check(zz_r.keep["phases"] == [(1, "wait"), (1, "bite"), (2, "wait"), (2, "bite"), (3, "wait"), (3, "bite")]
              and len(zz_r.lines) == 3 and not [t for t in zz_r.lines if " cm." in t]
              and period == "Noon" and fish_state == {} and _zz_dt >= 3 * FISH_SWEEP * FISH_PASSES,
              "I: left alone, fish_screen plays itself: its wait timer calls fish_strike, its sweep timer returns "
              "('miss',), three casts, three miss lines, one period (%.1f s)" % _zz_dt,
              (zz_r.keep["phases"], zz_r.lines, period))
        check(FISH_WAIT == (1.0, 3.0), "I: FISH_WAIT is back to the game's own (1.0, 3.0)", FISH_WAIT)

        ## The sitting is rolled when I sit down: running fish_next again from
        ## the same state (what a load during a cast does) deals the same cast.
        zz_r_fix("rich", here="riverside", period="Evening")
        fish_begin()
        _zz_plan = copy.deepcopy(fish_state["plan"])
        _zz_snap = copy.deepcopy(fish_state)
        _zz_deal = []
        for _zz_i in range(3):
            store.fish_state = copy.deepcopy(_zz_snap)
            fish_next()
            _zz_deal.append((fish_state["cast"], fish_state["kind"], fish_state["centre"], fish_state["wait"]))
        check(len(_zz_plan) == FISH_CASTS and all(len(r) == 4 and fish_kind(r[0]) and fish_kind(r[1]) and 0.0 <= r[2] <= 1.0
                                                 and FISH_WAIT[0] <= r[3] <= FISH_WAIT[1] for r in _zz_plan)
              and _zz_deal[0] == _zz_deal[1] == _zz_deal[2] and _zz_deal[0][:2] == (1, _zz_plan[0][0])
              and fish_state["plan"] == _zz_plan,
              "I: fish_begin() rolls the sitting's three casts (fish_state['plan']); fish_next() reads the row and rolls "
              "nothing, so a cast started again from the same state is the same fish, zone and wait", (_zz_plan, _zz_deal))
        ## A planned fish that can no longer come up gives way to its spare.
        fish_begin()
        fish_state["plan"][0][0] = FISH_PALE
        fish_state["plan"][1][0] = FISH_LORD
        fish_cursed_week = fish_week()
        flag("caught_river_lord")
        fish_next()
        _zz_a = (fish_state["kind"], fish_state["plan"][0][1])
        fish_settle(("miss",))
        fish_next()
        _zz_b = (fish_state["kind"], fish_state["plan"][1][1])
        check(_zz_a[0] == _zz_a[1] and _zz_b[0] == _zz_b[1] and _zz_a[0] not in (FISH_PALE, FISH_LORD)
              and _zz_b[0] not in (FISH_PALE, FISH_LORD),
              "I: a planned pale thing in a week it has already come up, or a planned River Lord once it is caught, "
              "gives way to the row's spare (an ordinary fish)", (_zz_a, _zz_b))
        fish_end()
        ## A sitting with no plan still casts.
        fish_begin()
        del fish_state["plan"]
        fish_next()
        check(fish_kind(fish_state["kind"]) is not None and fish_state["cast"] == 1, "I: a fish_state with no plan still casts (rolled then)")
        fish_end()

        ## A companion is on the next stone along.
        zz_r_fix("rich", here="riverside", period="Morning")
        companion = "yuji"
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([("leave",)])
    call sb_do_fish_cast
    python:
        zz_r_stop()
        _zz_a = len(zz_r_said(_zz_n0, "takes the next stone along"))      # a line may be captured twice
        companion = None
        _zz_n0 = len(zz_r.texts)
        zz_r_drive([("leave",)])
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(_zz_a >= 1 and not zz_r_said(_zz_n0, "takes the next stone along") and _fish_who == CAST["yuji"]["short"],
              "I: with a companion the sitting opens with a line about them (by name, no expression); alone it does not",
              (_zz_a, _fish_who))

        ## Under autoplay.
        zz_r_fix("rich", here="riverside", period="Morning")
        autoplay(True)
    call sb_do_fish_cast
    python:
        autoplay(False)
        check(period == "Noon" and fish_state == {}, "I: sb_do_fish_cast under autoplay returns (the timer hooks at q 0.5)", period)

        ## The record book.
        zz_r_fix("rich", here="riverside")
        fish_land("carp", 44)
        _zz_rows = fish_records()
        check(len(_zz_rows) == len(fish_species()) == 7 and all(isinstance(n, str) and (c is None or isinstance(c, int)) for n, c in _zz_rows)
              and ("Carp", 44) in _zz_rows and ("???", None) in _zz_rows and ("Ayu", None) in _zz_rows
              and "Something pale" not in [n for n, c in _zz_rows],
              "I: fish_records() has one row per species (the six and the River Lord, unnamed until caught; the pale thing "
              "is not a fish)", _zz_rows)

    ############################################################################
    ## J. The Library
    ############################################################################
    python:
        zz_r_fix("rich", here="library", period="Morning", insight=10, control=12, stamina=80)
        check(("lib_study", "Study in the stacks", 1) in [(a[0], a[1], a[3]) for a in place_actions("library")],
              "J: place action lib_study, 'Study in the stacks', one period, in the Library")
        zz_r.picks = ["Theory"]
        autoplay(True)
    call sb_do_lib_study
    python:
        check((insight, control, stamina, period) == (14, 12, 72, "Noon"),
              "J: the theory shelf gives Insight +4, costs stamina 8 and one period", (insight, control, stamina, period))
        zz_r_fix("rich", here="library", period="Morning", insight=10, control=12, stamina=80)
        zz_r.picks = ["Barrier craft"]
    call sb_do_lib_study
    python:
        check((insight, control, period) == (12, 14, "Noon"), "J: the barrier-craft shelf gives Control +2 and Insight +2",
              (insight, control, period))
        zz_r_fix("rich", here="library", period="Morning", insight=10, control=12, stamina=80)
        zz_r.picks = ["History"]
    call sb_do_lib_study
    python:
        check((insight, control, period) == (14, 12, "Noon"), "J: the history shelf gives Insight +4", (insight, control, period))
        zz_r_fix("rich", here="library", period="Morning", insight=10, control=12, stamina=80)
        zz_r.picks = ["Barrier craft"]
        _zz_n1 = len(zz_r.texts)
        zz_r.keep["ncw"] = store.night_can_work
        store.night_can_work = zz_r_false
    call sb_do_lib_study
    python:
        store.night_can_work = zz_r.keep.pop("ncw")
        _zz_a = (insight, control, period)
        zz_r_fix("rich", here="library", period="Morning", insight=10, control=12, stamina=80)
        zz_r_rest_day()
        zz_r.picks = ["Barrier craft"]
    call sb_do_lib_study
    python:
        check(len(zz_r_said(_zz_n1, "so I only read")) >= 2 and not zz_r_said(_zz_n1, "[_lib_line]"),
              "J: on a rest day the barrier-craft shelf says one line, of reading only (no shelf line about tracing or "
              "copying before it)", zz_r.texts[_zz_n1:])
        check(_zz_a == (12, 12, "Noon") and (insight, control, period) == (12, 12, "Noon"),
              "J: on a rest day the barrier-craft shelf gives Insight +2 only (night_can_work patched to False, and P4b's "
              "real rest day)", (_zz_a, (insight, control, period)))
        check([m[1] for m in zz_r.menus[-5:]] and all(m[1] and not str(m[1]).startswith("MISSING") for m in zz_r.menus[-5:])
              and len(zz_r.menus[-1][0]) == 3, "J: the shelf menu offers three shelves", zz_r.menus[-1:])
        zz_r_fix("rich", here="classroom", period="Morning", insight=10, control=12, stamina=80)
    call sb_do_study
    python:
        autoplay(False)
        check((insight, control, stamina, period) == (13, 12, 72, "Noon"),
              "J: sb_do_study in the classroom is unchanged (Insight +3, stamina 8, one period)", (insight, control, stamina, period))
        zz_r_fix("rich", here="library")
        check("study" in ACT_BY_ID and "library" in (ACT_BY_ID["study"].get("loc") or ()),
              "J: 'Study together' is offered in the Library (P2's row)", ACT_BY_ID["study"].get("loc"))

    ############################################################################
    ## K. The screens, the saved variables, the worst case
    ############################################################################
    python:
        _zz_bad = []
        for _zz_f, _zz_s in (("room_computer.rpy", "pc_screen"), ("room_fishing.rpy", "fish_screen")):
            _zz_body = zz_r_src(_zz_f).split("screen %s(" % _zz_s, 1)[1].split("\nlabel ", 1)[0]
            if not re.search(r"if smoke_autoplay:\s*\n\s*timer 0\.05 action Return\(", _zz_body):
                _zz_bad.append((_zz_s, "no autoplay timer"))
            if 'key "game_menu" action Return(' not in _zz_body:
                _zz_bad.append((_zz_s, "no game_menu key"))
            if "tag sandbox" not in _zz_body or "modal True" not in _zz_body:
                _zz_bad.append((_zz_s, "not tagged sandbox and modal"))
        check(not _zz_bad, "K: pc_screen and fish_screen are `tag sandbox`, modal, have an autoplay timer and answer "
              "key \"game_menu\"", _zz_bad)

        ## The statements saves rest on (2.3).
        _zz_pc, _zz_fi, _zz_li = zz_r_src("room_computer.rpy"), zz_r_src("room_fishing.rpy"), zz_r_src("room_library.rpy")
        check(re.search(r"\n +call screen pc_screen\(_pc_page\)\n +\$ _pc_r = _return\n", _zz_pc)
              and re.search(r"\n +call screen fish_screen\n +\$ _fish_r = _return\n", _zz_fi)
              and _zz_li.count("\n    menu:\n") == 1,
              "K: the protected statements are written as 2.3 gives them (the two `call screen` pairs, the shelf menu)")

        ## Icon names (an unknown one draws a question mark and nothing else catches it).
        _zz_names = set()
        for _zz_f in ZZ_R_FILES:
            _zz_names |= set(re.findall(r"icon(?:_btn)?\(\"([a-z_0-9]+)\"", zz_r_src(_zz_f)))
        _zz_names |= set(_zz_h["icon"] for _zz_h in zz_r_spots())
        check(_zz_names and all(n in ICONS for n in _zz_names) and all(icon_has_art(n) for n in _zz_names),
              "K: every icon name P6's files use is a key of ICONS, and has its picture", builtins.sorted(_zz_names))

        ## The saved variables.
        zz_r_fix("rich", here="riverside", period="Evening")
        pc_visit("home")
        pc_visit("gojo")
        pc_request("clan_kamo", "A test request")
        pc_check()
        fish_land("ayu", 20)
        fish_land("pale_thing", 0)
        fish_begin()
        fish_next()
        fish_strike()
        _zz_vals = builtins.dict((k, getattr(store, k)) for k in ZZ_R_VARS)
        _zz_back = pickle.loads(pickle.dumps(_zz_vals, pickle.HIGHEST_PROTOCOL))

        def _zz_plain(v):
            if isinstance(v, (str, int, float, bool)) or v is None:
                return True
            if isinstance(v, (list, tuple, set, frozenset)):
                return all(_zz_plain(x) for x in v)
            if isinstance(v, dict):
                return all(_zz_plain(k) and _zz_plain(x) for k, x in v.items())
            return False
        _zz_ok = all(_zz_plain(v) for v in _zz_vals.values())
        del _zz_plain
        check(_zz_back == _zz_vals and _zz_ok and fish_state.get("phase") == "bite",
              "K: every new variable holds plain values and pickles (pc_read, pc_requests, pc_checked_week, pc_noted, "
              "fish_log, fish_state mid-cast, fish_cursed_week)", _zz_vals)
        _zz_defs = set(getattr(d, "varname", None) for d in renpy.ast.default_statements)
        check(all(k in _zz_defs for k in ZZ_R_VARS), "K: each is a `default`")
        fish_end()

    ## A real save from inside each screen.
    python:
        zz_r_fix("rich", here="dorm", period="Morning")
        zz_r.keep.pop("save_pc_screen", None)
        zz_r.keep.pop("save_fish_screen", None)
        zz_r_drive([("page", "gojo"), ("close",)], on_show=lambda name: zz_r_save(name) if "save_" + name not in zz_r.keep else None)
    call sb_do_pc_open
    python:
        zz_r_stop()
        zz_r_fix("rich", here="riverside", period="Morning")
        zz_r_drive([("hook", 1.0), ("leave",)], on_show=lambda name: zz_r_save(name) if "save_" + name not in zz_r.keep else None)
    call sb_do_fish_cast
    python:
        zz_r_stop()
        check(zz_r.keep.get("save_pc_screen") is True and zz_r.keep.get("save_fish_screen") is True,
              "K: a save made while pc_screen is waiting, and one while fish_screen is waiting, is written and loadable "
              "(nothing un-picklable in the state, the screens' scope or the rollback log)",
              (zz_r.keep.get("save_pc_screen"), zz_r.keep.get("save_fish_screen")))
        note("K: loading those saves", "is P8's p2_saves (plan 7 · P8); this harness writes them and asks renpy.can_load")

    ## zz_worst and the screenshots.
    python:
        zz_r_fix("rich", here="dorm", period="Morning")
        pc_visit("home")
        pc_noted = pc_visit("sukuna_folk")
        zz_worst("pc_screen", "sukuna_folk", hover="pc_mark_gojo")
        _zz_room = toast_room()
        check(_zz_room == (0, 0, 0) and not toast_visible() and not hud_banner_ok(),
              "K: zz_worst('pc_screen'): no toast drawn, no banner (toast_room() is (0, 0, 0) over it)", (_zz_room, toast_visible()))
        _zz_w = len(zz_words("pc_screen"))
        _zz_b = zz_buttons("pc_screen")
        note("K: pc_screen", "%d words, %d buttons on a wiki page" % (_zz_w, _zz_b))
        renpy.hide_screen("pc_screen")
        pc_noted = ""

        zz_r_fix("rich", here="riverside", period="Morning")
        fish_begin()
        fish_next()
        fish_state["wait"] = 60.0
        renpy.show_screen("fish_screen")
        _zz_wait = (fish_phase(), zz_rect("fish_screen", "fish_hook"), zz_rect("fish_screen", "fish_leave"),
                    zz_rect("fish_screen", "fish_record"), zz_rect("fish_screen", "fish_water"))
        shot("fish_wait", wait=0.1)
        ## The record book's hover label, above Pack up (looked at, not measured).
        renpy.set_focus("fish_screen", "fish_record")
        shot("fish_record_hover")
        fish_state["t_cast"] = time.time() - 10.0
        fish_strike()
        fish_state["t0"] = time.time() - FISH_SWEEP * 0.4
        _zz_bite = (fish_phase(), zz_rect("fish_screen", "fish_water") is not None, ("leave",) in zz_r_rets("fish_screen"))
        shot("fish_bite", wait=0)
        renpy.hide_screen("fish_screen")
        check(_zz_wait[0] == "wait" and _zz_wait[2] is not None and _zz_wait[3] is not None and _zz_wait[4] is None
              and _zz_bite == ("bite", True, True),
              "K: fish_screen: while the float sits only Pack up and the record book answer; at the bite the water takes a "
              "click", (_zz_wait, _zz_bite))
        fish_end()

        fish_land("ayu", 21)
        fish_land("carp", 52)
        fish_begin()
        fish_next()
        fish_state["wait"] = 60.0
        renpy.show_screen("fish_screen")
        zz_render()
        renpy.get_screen("fish_screen").scope["fish_book"] = True
        renpy.restart_interaction()
        _zz_tx = zz_texts("fish_screen")
        shot("fish_book", wait=0.2)
        renpy.hide_screen("fish_screen")
        check("Record book" in _zz_tx and "21 cm" in " ".join(_zz_tx) and "???" in _zz_tx,
              "K: the record panel lists each species with my best, and ??? for one not caught", _zz_tx[-16:])
        fish_end()

        fish_begin()
        fish_next()
        fish_state["t_cast"] = time.time() - 10.0
        fish_strike()
        zz_worst("fish_screen")
        _zz_room = toast_room()
        check(_zz_room == (0, 0, 0) and not toast_visible() and not hud_banner_ok(),
              "K: zz_worst('fish_screen'): no toast drawn, no banner", (_zz_room, toast_visible()))
        _zz_w = len(zz_words("fish_screen"))
        note("K: fish_screen", "%d words, %d buttons" % (_zz_w, zz_buttons("fish_screen")))
        renpy.hide_screen("fish_screen")
        fish_end()

        ## The stand-in path: no icon pictures.
        zz_r_fix("rich", here="dorm", period="Morning")
        zz_r_stage("dorm", 0)
        zz_r.keep["art"] = store.icon_has_art
        store.icon_has_art = zz_r_no_art
        renpy.show_screen("sb_place")
        _zz_box = (zz_rect("sb_place", "hot_computer"), zz_rect("sb_place", "hot_bed"))
        shot("room_dorm_standin")
        renpy.hide_screen("sb_place")
        renpy.show_screen("pc_screen", "home")
        _zz_close = zz_rect("pc_screen", "pc_close")
        shot("pc_home_standin", wait=0.1)
        renpy.hide_screen("pc_screen")
        store.icon_has_art = zz_r.keep.pop("art")
        check(all(_zz_box) and _zz_close is not None and _zz_close[3] <= 44,
              "K: with no icon pictures (icon_has_art patched to False) the hotspots and the browser's close button still "
              "draw, as the stand-in seal", (_zz_box, _zz_close))

    python:
        zz_r_restore()
        finish()
    return
