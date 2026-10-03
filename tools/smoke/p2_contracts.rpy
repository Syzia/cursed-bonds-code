## tools/smoke/p2_contracts.rpy -- phase 2's standing harness
## (docs/PHASE2_DESIGN.md: 2.2 R2 to R5, section 6, P0a task 4, P0b task 13).
##
##   tools/smoke.sh tools/smoke/p2_contracts.rpy
##
## Two halves. P0a wrote the tooling half; P0b adds the contracts half below
## the marker near the end of the file. After wave 0 nobody edits this file:
## it runs, unchanged, in every worktree and on the merged tree.
##
## The tooling half:
##   1. The baseline. zz_p0_dump() reads, through the game's own functions,
##        place_actions(loc)        every room x period
##        armory_tools()            the racks
##        sb_char(who)              the Return values of every button
##        person_choices(who, loc)  every person x room x period
##      on two fixtures ("fresh": day 3, Grade 4, just past roll call; "rich":
##      day 9, everyone met, the armory and the board open), and takes the two
##      baseline screenshots (the place view and the person view). The dump
##      goes to shots/p2_contracts/p0_now.json, the screenshots to p0_place.png
##      and p0_person.png, every run.
##      tools/smoke/baseline_p0.json and tools/smoke/baseline_shots/ are that
##      output on the tree before phase 2 changed anything (1d3a9db). The run
##      compares today's dump with them: "unchanged" in the plan always means
##      "equal to these files", never "as I remember it".
##        place_actions   every baseline row still there, in order (new rows
##                        and new rooms are listed as NOTE lines)
##        armory_tools    equal
##        sb_char         the same Return values for every person (in any
##                        order: P2 moves `invite` to the card's footer)
##        person_choices  equal on the seven fields the baseline has (a new
##                        key on a choice, such as `icon`, is a NOTE). Once
##                        night_exists(), the Night rows are left out: the
##                        night rule takes costed choices away there (P4b)
##        screenshots     wave 0 only (see SMOKE_P0_STRICT)
##
##      SMOKE_P0_STRICT=1 is wave 0's own run: "the game looks and plays as
##      before" in full. It adds four hard checks that later packages break by
##      design, which is why they are NOTE lines in every other run:
##        - the two screenshots are pixel-identical to baseline_shots/
##          (P2 redraws the HUD, the action card and the person card; P5 the
##          stage);
##        - sb_char's Return values are in the baseline's tree order;
##        - person_choices is equal at Night as well;
##        - the toast timer keeps ticking while toasts wait over the sample.
##      The baseline screenshots are 2666x1499, the window of the Mac they were
##      taken on. A window of another size cannot be compared with them: point
##      SMOKE_P0_SHOTS at a folder holding place.png and person.png taken in
##      today's window (p0_place.png and p0_person.png as this harness's
##      tooling half writes them when run on a copy of the tree at 1d3a9db)
##      and the strict run compares with those instead.
##      tools/smoke/baseline_shots/1818x1022/ holds such a pair, taken in
##      review round 1 from a scratch rebuild of the tree at 1d3a9db (its dump
##      equalled baseline_p0.json): give SMOKE_P0_SHOTS its absolute path when
##      the window is 1818x1022.
##   2. The measuring helpers of _lib.rpy, on a small screen of this file.
##   3. fixture(): an unknown name fails, a shaped variable is refused (R5).
##   4. tools/none_ok.txt: every example returns None in a settled fixture, and
##      every DEV_FUNCS key through dev_action(key), each in a fresh one (R4).
##
## The contracts half (P0b, task 13; everything from section 5 of the label on):
##   5. ZZ_RETURNS: every function row of 6.1 has its frozen signature, lives in
##      its owner's file (fn.__code__.co_filename) and returns the frozen type
##      or shape for an example call. Shapes, never stub values: the table runs
##      unchanged against the stubs and against every package's real code.
##      Then the screens' parameter lists, the labels, the tables and defaults.
##   6. Grades and icons: the tiers and colours; the 88 names; every activity,
##      place action, tab, area and room maps to an icon in the table.
##   7. The registries: aa_zz_order.rpy's two rows are there (init order), a
##      duplicate id is a finding, hot_spots_for / hot_covers / rail_actions
##      on test rows, the release row, the card against the baseline.
##   8. Sidecars: the two overlay files in tools/smoke/assets/p2_contracts/ are
##      read independently by rule_layout; the code defaults are dumped to
##      <repo>/shots/layout/defaults.json for tools/layout_sheet.py.
##   9. The rules: the soft clock, the hangout gate, rule_walk_to, the item
##      requirement validator, the motion switch.
##  10. The screens: the Library renders, the old map shows one label for a
##      hovered row, SKIPPING hides over the map, the Motion row, the review
##      panel's buttons, and the hover label held across 20 toast ticks.
##  11. A save made on the place view reloads (R10).
##
## smoke-with: aa_zz_order.rpy

init 999 python:
    import builtins
    import copy
    import json
    import os
    import re
    import struct
    import zlib

    ZZ_P0_SEED = 20261001
    ZZ_P0_FIELDS = ("kind", "id", "label", "hint", "cost", "gold", "romance")
    ZZ_P0_FLAGS = dict(
        fresh=("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access"),
        rich=("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
              "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
              "intensive_done", "ijichi_rides"),
    )

    ## Wave 0's own run (the header says what it adds).
    ZZ_P0_STRICT = os.environ.get("SMOKE_P0_STRICT") == "1"

    def zz_p0_check(cond, name, detail=""):
        """A check in wave 0's strict run; a NOTE that says whether it still
        holds in every other run."""
        if ZZ_P0_STRICT:
            return check(cond, name, detail)
        note(name, "still holds" if cond else "no longer holds (wave 0 only; expected once P2, P4b or P5 is in): %s"
             % zz_smoke_one_line(detail)[:300])
        return bool(cond)

    def zz_root():
        """The repository the harness was started from (smoke.sh exports it),
        or None under an older smoke.sh."""
        return os.environ.get("SMOKE_ROOT") or None

    def zz_p0_snapshot():
        """Every store variable that has ever been set, deep-copied: the
        state a later zz_p0_restore() goes back to."""
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

    def zz_p0_restore(snap):
        for k, v in snap.items():
            setattr(store, k, copy.deepcopy(v))
        mission_cache_clear()
        toast_clear()

    def zz_p0_fixture(kind):
        """The two baseline fixtures. Both start from the store as the harness
        found it (ZZ_P0_BOOT), so they do not depend on what ran before."""
        zz_p0_restore(ZZ_P0_BOOT[0])
        renpy.random.seed(ZZ_P0_SEED)
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
        for f in ZZ_P0_FLAGS[kind]:
            flag(f)
        store.done_events.add("st_roll_call")
        promote("mc", "g4", quiet=True)
        if kind == "rich":
            promote("mc", "g3", quiet=True)
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()

    def zz_p0_rows(rows):
        return [builtins.list(r) for r in rows]

    def zz_p0_quiet_view():
        """Nothing that moves by the wall clock: the arrival caption already
        faded, the objective already read, no toast."""
        ARRIVAL[0] = (store.day, store.period, store.here)
        ARRIVAL[1] = 0.0
        store.last_objective = objective_text() or ""
        OBJ_UNSEEN[0] = None
        renpy.hide_screen("objective_toast")
        toast_clear()

    def zz_p0_render(seconds=0.2):
        """One real interaction, so the shown screens are built and drawn."""
        skipping, auto = config.skipping, zz_smoke_state.autoplay
        config.skipping = None
        zz_smoke_state.autoplay = False
        try:
            renpy.pause(seconds, hard=True)
        finally:
            config.skipping, zz_smoke_state.autoplay = skipping, auto

    def zz_p0_returns(screen):
        """The value of every Return action on a shown screen's buttons, in
        tree order. (`key` statements are not buttons and are not listed.)"""
        out = []
        seen = builtins.set()

        def each(d):
            if id(d) in seen:
                return
            seen.add(id(d))
            a = getattr(d, "action", None)
            if a is None:
                return
            for x in (a if isinstance(a, (builtins.list, builtins.tuple)) else [a]):
                if isinstance(x, Return):
                    v = x.value
                    out.append(builtins.list(v) if isinstance(v, builtins.tuple) else v)

        d = renpy.get_screen(screen)
        if d is not None:
            d.visit_all(each)
        return out

    def zz_p0_noon_place(who):
        """Where the schedule has someone at Noon; the courtyard if nowhere."""
        for loc in LOC_ORDER:
            if who in who_is_here(loc, "Noon"):
                return loc
        return "courtyard"

    def zz_p0_dump_tables(kind):
        """place_actions, armory_tools and person_choices on one fixture."""
        zz_p0_fixture(kind)
        out = builtins.dict(day=store.day, grade=store.grade, roster=builtins.list(store.roster),
                            flags=builtins.sorted(store.flags))
        acts = {}
        lists = []
        index = {}
        keys = builtins.set()
        for loc in LOC_ORDER:
            for per in PERIODS:
                store.period = per
                store.here = loc
                mission_cache_clear()
                acts["%s|%s" % (loc, per)] = zz_p0_rows(place_actions(loc))
                for who in ROSTER_ORDER:
                    cs = person_choices(who, loc)
                    for c in cs:
                        keys.update(c)
                    row = [[c.get(f) for f in ZZ_P0_FIELDS] for c in cs]
                    if row not in lists:
                        lists.append(row)
                    index["%s|%s|%s" % (who, loc, per)] = lists.index(row)
        out["place_actions"] = acts
        out["choice_keys"] = builtins.sorted(keys)
        out["choice_lists"] = lists
        out["person_choices"] = index
        store.period = "Noon"
        store.here = "storehouse"
        out["armory_tools"] = zz_p0_rows(armory_tools())
        return out

    def zz_png_raw(path):
        """(width, height, the unfiltered-on-load scanline bytes) of a PNG.
        Two screenshots written by this Ren'Py hold the same pixels exactly
        when these are equal."""
        with open(path, "rb") as f:
            d = f.read()
        pos, w, h, idat = 8, 0, 0, b""
        while pos < len(d):
            ln = struct.unpack(">I", d[pos:pos + 4])[0]
            tag = d[pos + 4:pos + 8]
            data = d[pos + 8:pos + 8 + ln]
            if tag == b"IHDR":
                w, h = struct.unpack(">II", data[:8])
            elif tag == b"IDAT":
                idat += data
            pos += 12 + ln
        return w, h, zlib.decompress(idat)

    def zz_png_same(a, b):
        """(same, detail) for two PNG files."""
        if not os.path.isfile(a) or not os.path.isfile(b):
            return False, "missing: %s" % (a if not os.path.isfile(a) else b)
        wa, ha, ra = zz_png_raw(a)
        wb, hb, rb = zz_png_raw(b)
        if (wa, ha) != (wb, hb):
            return False, "sizes differ: %dx%d and %dx%d" % (wa, ha, wb, hb)
        if ra == rb:
            return True, "%dx%d" % (wa, ha)
        n = builtins.sum(1 for i in range(0, builtins.min(len(ra), len(rb)), 997) if ra[i] != rb[i])
        return False, "%dx%d, pixels differ (%d of the sampled bytes)" % (wa, ha, n)

    def zz_subsequence(old, new):
        """True when every row of old is in new, in old's order."""
        it = builtins.iter(new)
        return builtins.all(any(r == x for x in it) for r in old)

    def zz_p0_compare(base, now):
        """Today's dump against the baseline (the header says how)."""
        for kind in ("fresh", "rich"):
            b, n = base[kind], now[kind]
            lost = []
            grew = []
            for key in builtins.sorted(b["place_actions"]):
                old = b["place_actions"][key]
                new = n["place_actions"].get(key)
                if new is None or not zz_subsequence(old, new):
                    lost.append((key, old, new))
                elif new != old:
                    grew.append((key, [r[0] for r in new if r not in old]))
            check(not lost, "baseline %s: every place_actions row still there, in order (%d room x period)"
                  % (kind, len(b["place_actions"])), lost[:4])
            if grew:
                note("baseline %s: place_actions rows added" % kind, grew[:12])
            extra = builtins.sorted(set(n["place_actions"]) - set(b["place_actions"]))
            if extra:
                note("baseline %s: place_actions for new rooms" % kind,
                     builtins.sorted(set(k.split("|")[0] for k in extra)))
            check(n["armory_tools"] == b["armory_tools"], "baseline %s: armory_tools() is unchanged" % kind,
                  [r for r in n["armory_tools"] if r not in b["armory_tools"]][:4])
            bad = []
            bad_night = []
            for key in builtins.sorted(b["person_choices"]):
                old = b["choice_lists"][b["person_choices"][key]]
                i = n["person_choices"].get(key)
                new = n["choice_lists"][i] if i is not None else None
                if new != old:
                    (bad_night if key.endswith("|Night") else bad).append((key, old, new))
            n_night = builtins.sum(1 for key in b["person_choices"] if key.endswith("|Night"))
            if ZZ_P0_STRICT or not night_exists():
                check(not bad and not bad_night, "baseline %s: person_choices is unchanged (%d person x room x period)"
                      % (kind, len(b["person_choices"])), (bad + bad_night)[:3])
            else:
                check(not bad, "baseline %s: person_choices is unchanged outside Night (%d person x room x period)"
                      % (kind, len(b["person_choices"]) - n_night), bad[:3])
                note("baseline %s: person_choices at Night" % kind,
                     "%d of %d rows differ from the baseline (the night rule is in)" % (len(bad_night), n_night))
            if n["choice_keys"] != b["choice_keys"]:
                note("baseline %s: person_choices keys added" % kind,
                     builtins.sorted(set(n["choice_keys"]) - set(b["choice_keys"])))
        def loose(row):
            return row and (row.get("here"), builtins.sorted(row.get("returns") or [], key=repr))
        diff = [(w, now["sb_char"].get(w), base["sb_char"][w]) for w in base["sb_char"]
                if loose(now["sb_char"].get(w)) != loose(base["sb_char"][w])]
        check(not diff and set(now["sb_char"]) == set(base["sb_char"]),
              "baseline: sb_char returns the same tuples for every person", diff[:3])
        zz_p0_check(now["sb_char"] == base["sb_char"], "baseline: sb_char's buttons are in the baseline's order",
                    [(w, now["sb_char"].get(w), base["sb_char"][w]) for w in base["sb_char"]
                     if now["sb_char"].get(w) != base["sb_char"][w]][:3])
        check(now["shots"] == base["shots"], "baseline: the two screenshots show the same fixture",
              (now["shots"], base["shots"]))

    ZZ_P0_BOOT = builtins.list([None])
    ZZ_P0_NOW = builtins.dict()

    ## The tooling half's own pieces ---------------------------------------------

    ## icon_glyph is P0b's style (ui_icons.rpy). Until it exists the helpers
    ## are tried on a stand-in of the same name; afterwards on the real one.
    try:
        style.icon_glyph
    except Exception:
        style.icon_glyph = Style(style.default)
    style.zz_tool_glyph_child = Style(style.icon_glyph)

    ZZ_TOOL_TICKS = builtins.list([0])

    def zz_tool_tick():
        ZZ_TOOL_TICKS[0] += 1

    def zz_none_ok_rows():
        """[(name, example)] from tools/none_ok.txt."""
        rows = []
        with open(os.path.join(zz_root(), "tools", "none_ok.txt"), encoding="utf-8") as f:
            for raw in f:
                raw = raw.rstrip("\n")
                if not raw.strip() or raw.startswith("#"):
                    continue
                name, _tab, example = raw.partition("\t")
                rows.append((name.strip(), example.strip()))
        return rows

    def zz_none_ok_run(example, **names):
        """Run one example on a fresh settled fixture; what it returned."""
        zz_p0_fixture("rich")
        return eval(example, store.__dict__, builtins.dict(names))


## The contracts half's own pieces (P0b) ---------------------------------------------

init 999 python:
    import inspect

    ZZ_DISP = renpy.display.displayable.Displayable

    ## The review panel is modal, and a modal screen holds a timed pause open:
    ## in this harness a pause ends on time whatever is up.
    config.modal_blocks_pause = False

    ## Survives a load: made at init, never reassigned, never saved.
    ZZ_SAVE = builtins.list([0])

    def zz_is_str(v):
        return isinstance(v, str)

    def zz_is_bool(v):
        return isinstance(v, bool)

    def zz_is_int(v):
        return isinstance(v, int) and not isinstance(v, bool)

    def zz_is_num(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def zz_is_none(v):
        return v is None

    def zz_is_disp(v):
        return isinstance(v, ZZ_DISP)

    def zz_seq(v, n=None):
        return isinstance(v, (builtins.list, builtins.tuple)) and (n is None or len(v) == n)

    def zz_rows4(v):
        """A list of (id, label, hint, cost)."""
        return isinstance(v, builtins.list) and all(
            zz_seq(a, 4) and zz_is_str(a[0]) and zz_is_str(a[1]) and zz_is_str(a[2]) and zz_is_int(a[3]) for a in v)

    def zz_rows6(v):
        """A list of (id, label, hint, cost, icon, gold)."""
        return isinstance(v, builtins.list) and all(
            isinstance(a, builtins.tuple) and len(a) == 6 and zz_rows4([a[:4]]) and a[4] in ICONS
            and zz_is_bool(a[5]) for a in v)

    ZZ_HOT_KEYS = {"id", "x", "y", "icon", "label", "hint", "cost", "act", "lines", "standalone", "front"}

    def zz_hot_rows(v):
        return isinstance(v, builtins.list) and all(isinstance(h, builtins.dict) and set(h) == ZZ_HOT_KEYS for h in v)

    def zz_person_now(v):
        return (isinstance(v, builtins.dict)
                and set(v) == {"place", "name", "doing", "reachable", "hidden", "with_me"}
                and (v["place"] is None or v["place"] in LOCATIONS)
                and zz_is_str(v["name"]) and zz_is_str(v["doing"])
                and zz_is_bool(v["reachable"]) and zz_is_bool(v["hidden"]) and zz_is_bool(v["with_me"]))

    def zz_spots(v):
        return isinstance(v, builtins.dict) and all(
            k in LOCATIONS and zz_seq(p, 2) and zz_is_num(p[0]) and zz_is_num(p[1]) for k, p in v.items())

    def zz_choices(v):
        need = {"kind", "id", "label", "hint", "cost", "gold", "romance", "icon"}
        return (isinstance(v, builtins.list) and v and all(
            isinstance(c, builtins.dict) and need <= set(c) and c["icon"] in ICONS
            and c["icon"] == icon_for(c["kind"], c["id"]) for c in v))

    def zz_story_rows(v):
        need = {"kind", "title", "line", "state", "where", "next"}
        return isinstance(v, builtins.list) and all(isinstance(r, builtins.dict) and need <= set(r) for r in v)

    def zz_reqs(v):
        return isinstance(v, builtins.list) and all(
            zz_seq(r, 2) and zz_is_str(r[0]) and zz_is_bool(r[1]) for r in v)

    def zz_market_rows(v):
        return isinstance(v, builtins.list) and all(
            zz_seq(r, 4) and r[0] in ITEMS and zz_is_int(r[1]) and r[2] in ("buy", "sold", "poor") and zz_is_str(r[3])
            for r in v)

    def zz_slots(v, n=2):
        return isinstance(v, builtins.list) and len(v) == n and all(
            zz_seq(t, 4) and zz_is_num(t[0]) and zz_is_num(t[1]) and zz_is_num(t[2]) and zz_is_int(t[3]) for t in v)

    def zz_rects(v):
        return isinstance(v, builtins.list) and all(zz_seq(r, 4) and all(zz_is_num(x) for x in r) for r in v)

    def zz_pose(v):
        return v is None or (isinstance(v, builtins.dict) and zz_is_str(v.get("image"))
                             and isinstance(v.get("box"), builtins.tuple) and len(v["box"]) == 4
                             and all(zz_is_int(x) for x in v["box"]))

    def zz_fish(v):
        return (isinstance(v, builtins.dict) and set(v) == {"id", "cm", "yen", "record"}
                and zz_is_int(v["yen"]) and zz_is_bool(v["record"]))

    def zz_fish_kind():
        """A species id fish_land accepts: P6's first, or a made-up one for the stub."""
        kinds = getattr(store, "FISH_KINDS", None)
        return kinds[0]["id"] if kinds else "ayu"

    def zz_game_id():
        """A game cards_new accepts: the first real one registered, else "blackjack"."""
        real = [g["id"] for g in mg_games() if not g["id"].startswith("zz")]
        return real[0] if real else "blackjack"

    def zz_pc_page():
        pages = getattr(store, "PC_PAGES", None)
        return builtins.sorted(pages)[0] if pages else "sukuna"

    def zz_event(kind="hangout"):
        """An event record of that kind from the game's own table."""
        return next(e for e in EVENTS if e["kind"] == kind)

    ## (name, owning file, signature, example call, what the result must be).
    ## The example runs in a fresh "rich" fixture, in the Morning, in my room.
    ZZ_RETURNS = [
        ("ui_do", "ui_icons.rpy", "(fn, *args, **kwargs)", "ui_do(len, 'abc')", zz_is_none),
        ("icon", "ui_icons.rpy", "(name, size=40, gold=False)", "icon('map')", zz_is_disp),
        ("icon_label", "ui_icons.rpy", "(name)", "icon_label('map')", zz_is_str),
        ("icon_for", "ui_icons.rpy", "(kind, id)", "icon_for('act', 'train')", lambda v: v in ICONS),
        ("icon_has_art", "ui_icons.rpy", "(name)", "icon_has_art('map')", zz_is_bool),
        ("grade_tier", "sb_grades.rpy", "(v)", "grade_tier('s1')", lambda v: v in ("g4", "g3", "g2", "g1", "sp")),
        ("grade_color", "sb_grades.rpy", "(v)", "grade_color('g2')", lambda v: zz_is_str(v) and v.startswith("#")),
        ("grade_fill", "sb_grades.rpy", "(v)", "grade_fill('sp')", zz_is_disp),
        ("grade_is_special", "sb_grades.rpy", "(v)", "grade_is_special('sp')", zz_is_bool),
        ("advance_period_soft", "sb_world.rpy", "(n=1, loc=None)", "advance_period_soft(1)", zz_is_bool),
        ("rule_hangout_gate", "sb_rules.rpy", "(e)", "rule_hangout_gate(zz_event())", zz_is_bool),
        ("rule_layout", "sb_rules.rpy", "(name)", "rule_layout('zz_no_such_file')", lambda v: v == {}),
        ("register_hotspot", "sb_hotspots.rpy",
         "(id, place, x, y, icon, act=None, lines=None, label='', hint='', cost=0, when=None, standalone=False, front=False)",
         None, None),
        ("hot_spots_for", "sb_hotspots.rpy", "(loc)", "hot_spots_for('dorm')", zz_hot_rows),
        ("hot_covers", "sb_hotspots.rpy", "(loc)", "hot_covers('dorm')", lambda v: isinstance(v, builtins.set)),
        ("register_minigame", "sb_hotspots.rpy", "(id, name, icon, min_people=1)", None, None),
        ("mg_games", "sb_hotspots.rpy", "()", "mg_games()",
         lambda v: isinstance(v, builtins.list) and all(set(g) == {"id", "name", "icon", "min_people"} for g in v)),
        ("rail_actions", "sb_screens.rpy", "(loc)", "rail_actions('dorm')", zz_rows6),
        ("view_motion", "view_stage.rpy", "()", "view_motion()", zz_is_bool),
        ("view_person_rects", "view_stage.rpy", "(loc)", "view_person_rects('cafeteria')", zz_rects),
        ("place_actions", "sb_screens.rpy", "(loc)", "place_actions('dorm')", zz_rows4),
        ("toast_room", "ui_hud.rpy", "()", "toast_room()", lambda v: zz_seq(v, 3) and all(zz_is_int(x) for x in v)),
        ("person_now", "sb_world.rpy", "(who)", "person_now('yuji')", zz_person_now),
        ("map_spots", "ui_map.rpy", "(key)", "map_spots('school')", zz_spots),
        ("ambient_of", "sb_screens.rpy", "(who, loc)", "ambient_of('yuji', 'cafeteria')",
         lambda v: zz_seq(v, 2) and zz_is_str(v[0]) and v[1] in EXPRESSIONS),
        ("person_choices", "sb_activities.rpy", "(who, loc=None)", "person_choices('yuji', 'cafeteria')", zz_choices),
        ("jr_story_rows", "ui_journal.rpy", "(who)", "jr_story_rows('nobara')", zz_story_rows),
        ("item_requirements", "sb_items.rpy", "(id)", "item_requirements('playful_cloud')", zz_reqs),
        ("item_requirements_met", "sb_items.rpy", "(id)", "item_requirements_met('playful_cloud')", zz_is_bool),
        ("item_validate_reqs", "sb_items.rpy", "()", "item_validate_reqs()",
         lambda v: isinstance(v, builtins.list) and all(zz_is_str(x) for x in v)),
        ("market_exists", "sb_market.rpy", "()", "market_exists()", zz_is_bool),
        ("market_rows", "sb_market.rpy", "()", "market_rows()", zz_market_rows),
        ("market_buy", "sb_market.rpy", "(id)", "market_buy('first_aid')", zz_is_bool),
        ("night_pending", "sb_night.rpy", "()", "night_pending()", zz_is_bool),
        ("night_can_work", "sb_night.rpy", "()", "night_can_work()", zz_is_bool),
        ("night_exists", "sb_night.rpy", "()", "night_exists()", zz_is_bool),
        ("night_block_reason", "sb_night.rpy", "()", "night_block_reason()", zz_is_str),
        ("night_tag", "sb_night.rpy", "()", "night_tag()", zz_is_str),
        ("night_filter_actions", "sb_night.rpy", "(loc, acts)", "night_filter_actions('dorm', place_actions('dorm'))", zz_rows4),
        ("night_allows", "sb_night.rpy", "(id, cost)", "night_allows('train', 1)", zz_is_bool),
        ("night_blocks", "sb_night.rpy", "(id)", "night_blocks('train')", zz_is_bool),
        ("night_marks", "sb_night.rpy", "()", "night_marks()",
         lambda v: isinstance(v, builtins.dict) and all(k in AREA_BY_KEY and x == "moon" for k, x in v.items())),
        ("night_out_ok", "sb_night.rpy", "(key)", "night_out_ok('shibuya')",
         lambda v: zz_seq(v, 2) and zz_is_bool(v[0]) and zz_is_str(v[1])),
        ("night_gojo_ok", "sb_night.rpy", "()", "night_gojo_ok()", zz_is_bool),
        ("night_gojo_due", "sb_night.rpy", "()", "night_gojo_due()", zz_is_bool),
        ("night_day_best", "sb_night.rpy", "()", "night_day_best()", zz_is_int),
        ("night_gojo_gain", "sb_night.rpy", "()", "night_gojo_gain()",
         lambda v: zz_seq(v, 2) and zz_is_int(v[0]) and zz_is_int(v[1])),
        ("night_set_cost", "sb_night.rpy", "(kind)", "night_set_cost('out')", zz_is_none),
        ("night_dev", "sb_night.rpy", "(kind)", "night_dev('rest')", zz_is_none),
        ("view_slots", "view_stage.rpy", "(loc, n)", "view_slots('cafeteria', 2)", zz_slots),
        ("view_pose", "view_stage.rpy", "(who, loc, per=None)", "view_pose('yuji', 'cafeteria')", zz_pose),
        ("view_sync_light", "view_stage.rpy", "()", "view_sync_light()", zz_is_none),
        ("view_before_person", "view_stage.rpy", "(who)", "view_before_person('yuji')", zz_is_none),
        ("view_after_scene", "view_stage.rpy", "()", "view_after_scene()", zz_is_none),
        ("view_enter", "view_stage.rpy", "(who, expr=None)", "view_enter('yuji')", zz_is_none),
        ("pc_has_read", "room_computer.rpy", "(page)", "pc_has_read(zz_pc_page())", zz_is_bool),
        ("pc_request", "room_computer.rpy", "(page, note='')", "pc_request(zz_pc_page(), 'A test note')", zz_is_none),
        ("pc_leads", "room_computer.rpy", "()", "pc_leads()",
         lambda v: isinstance(v, builtins.list) and all(zz_seq(r, 2) for r in v)),
        ("pc_records", "room_computer.rpy", "()", "pc_records()",
         lambda v: isinstance(v, builtins.list) and all(zz_is_str(x) for x in v)),
        ("fish_land", "room_fishing.rpy", "(kind, cm)", "fish_land(zz_fish_kind(), 20)", zz_fish),
        ("fish_records", "room_fishing.rpy", "()", "fish_records()",
         lambda v: isinstance(v, builtins.list) and all(
             zz_seq(r, 2) and zz_is_str(r[0]) and (r[1] is None or zz_is_num(r[1])) for r in v)),
        ("cards_ok", "room_cards.rpy", "()", "cards_ok()", zz_is_bool),
        ("cards_new", "room_cards.rpy", "(game, opponents, stake)", "cards_new(zz_game_id(), ['yuji'], 100)",
         lambda v: isinstance(v, builtins.dict)),
        ("cards_records", "room_cards.rpy", "()", "cards_records()",
         lambda v: isinstance(v, builtins.dict) and zz_is_int(v.get("today"))),
        ("spot_vend_ok", "room_spots.rpy", "()", "spot_vend_ok()", zz_is_bool),
    ]

    ## Screens and their parameter lists (4.0, 6.1).
    ZZ_P2_SCREENS = [
        ("icon_btn", ["name", "action", "tip", "size", "w", "gold", "selected", "pips", "wid", "words"]),
        ("hover_label", []), ("icon_sample", []),
        ("grade_chip", ["v", "size", "text", "dim"]),
        ("hot_layer", ["loc", "front"]),
        ("sb_map", ["layer", "area"]), ("sb_hud", ["on_map", "person"]), ("sb_place", []), ("sb_char", ["who"]),
        ("journal", ["tab"]),
        ("view_stage", ["loc"]), ("view_focus", ["who"]), ("view_fg", ["loc"]),
        ("market_screen", []),
    ]

    ## Labels and how many parameters each takes.
    ZZ_P2_LABELS = [
        ("rule_walk_to", 1), ("hot_use", 1), ("night_carry_home", 0), ("night_out", 1),
        ("sb_do_night_bed", 0), ("sb_do_night_gojo", 0), ("market_open", 0),
        ("sb_do_pc_open", 0), ("sb_do_fish_cast", 0), ("sb_do_lib_study", 0),
        ("sb_do_spot_vend", 0), ("sb_do_cards_play", 0), ("stage_person", 2), ("mg_zz_order", 2),
    ]

    ## Every `default` of 3.3 and the type it holds.
    ZZ_P2_DEFAULTS = [
        ("night_carried", str), ("night_cost_day", int), ("night_cost_kind", str), ("night_gojo_last", int),
        ("night_gojo_day", int), ("night_out_last", int), ("market_bought", builtins.set),
        ("mg_result", builtins.dict), ("pc_read", builtins.set), ("pc_requests", builtins.list),
        ("pc_checked_week", int), ("fish_log", builtins.dict), ("fish_state", builtins.dict),
        ("fish_cursed_week", int), ("cards_state", builtins.dict), ("cards_won_day", int), ("cards_won", int),
    ]

    def zz_screen_params(name):
        sc = renpy.display.screen.get_screen_variant(name)
        if sc is None:
            return None
        p = sc.parameters
        if p is None:
            return []
        return [param.name for param in p.parameters.values()]

    def zz_label_nparams(name):
        if not renpy.has_label(name):
            return None
        p = getattr(renpy.game.script.lookup(name), "parameters", None)
        return 0 if p is None else len(p.parameters)

    def zz_hot_drop(*ids):
        """Take the harness's own test rows back out of the registries."""
        HOT_SPOTS[:] = [h for h in HOT_SPOTS if h["id"] not in ids]
        MG_GAMES[:] = [g for g in MG_GAMES if g["id"] not in ids]

    def zz_hot_real():
        """The registered hotspots that are a package's, not a harness's."""
        return [h for h in HOT_SPOTS if not h["id"].startswith("zz")]

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

    def zz_soft(per, n, here="dojo", waiting=None, **kw):
        """advance_period_soft(n, **kw) from a period, with exactly the story
        events whose label is in `waiting` let through the gates. Returns
        (rolled, the period it stopped at, the day)."""
        store.period = per
        store.here = here
        store.day = 22      ## a Monday
        want = builtins.set(waiting or ())
        for lab in want:
            store.done_events.discard(lab)
        rv = zz_with(dict(event_allowed=lambda e: e["label"] in want), lambda: advance_period_soft(n, **kw))
        return rv, store.period, store.day

    def zz_skip_texts():
        """What the SKIPPING indicator draws while the game is skipping: one
        timed interaction with skipping on (as zz_worst does), then every
        Text in the indicator's tree."""
        skipping, auto = config.skipping, zz_smoke_state.autoplay
        zz_smoke_state.autoplay = False
        config.skipping = "slow"
        try:
            renpy.ui.pausebehavior(0.3, False)
            renpy.ui.interact(mouse="pause", type="pause", roll_forward=None)
            out = [zz_text_string(d) for d in zz_text_nodes("skip_indicator")]
            shown = renpy.get_screen("skip_indicator") is not None
        finally:
            config.skipping, zz_smoke_state.autoplay = skipping, auto
            if not config.skipping:
                renpy.hide_screen("skip_indicator")
        return out if shown else ["<the indicator is not up>"]

    class ZZTrans(builtins.object):
        """Stands in for the Transform a transform function is handed."""
        alpha = 1.0
        crop = None

    def zz_layout_defaults():
        """The code defaults, through the contract functions, with every
        sidecar out of the way: view_slots for every room and 1 to 4 people,
        map_spots for every area, the registered point of every hotspot."""
        saved = builtins.dict(RULE_LAYOUT)
        RULE_LAYOUT.clear()
        try:
            for loc in LOC_ORDER:
                RULE_LAYOUT["view_" + loc] = {}
                RULE_LAYOUT["hot_" + loc] = {}
            for a in AREAS:
                RULE_LAYOUT["area_" + a["key"]] = {}
            slots = builtins.dict((loc, builtins.dict((str(n), [builtins.list(t) for t in view_slots(loc, n)])
                                                       for n in (1, 2, 3, 4))) for loc in LOC_ORDER)
            areas = builtins.dict((a["key"], builtins.dict((k, builtins.list(p)) for k, p in map_spots(a["key"]).items()))
                                  for a in AREAS)
        finally:
            RULE_LAYOUT.clear()
            RULE_LAYOUT.update(saved)
        hots = builtins.dict()
        for h in zz_hot_real():
            hots.setdefault(h["place"], builtins.dict())[h["id"]] = [h["x"], h["y"]]
        return builtins.dict(
            about=("Written by tools/smoke/p2_contracts.rpy: the layout defaults in the code, with no sidecar "
                   "applied, for tools/layout_sheet.py. slots: place -> {\"1\"..\"4\": [[xcenter, yoffset, zoom, far]]} "
                   "(view_slots). areas: area key -> {loc: [x, y]} (map_spots). hotspots: place -> {hotspot id: [x, y]} "
                   "(the registered points). The same shapes as the sidecars view_<place>.json, area_<key>.json and "
                   "hot_<place>.json (PHASE2_DESIGN.md 6.1)."),
            slots=slots, areas=areas, hotspots=hots)


## The screen the measuring helpers are tried on. Nine words, three buttons.
screen zz_tool():
    frame:
        pos (100, 200)
        background Solid("#07060cd8")
        padding (20, 20)
        vbox:
            spacing 6
            text "Three plain words"
            text "+2 ◆ 1"
            text "{b}Bold{/b} and {color=#f66}red{/color}"
            text u"縁" style "icon_glyph"
            text u"Glyph 任" style "zz_tool_glyph_child"
            text u"縁 kanji"
            textbutton "Go now" id "zz_tool_a" action NullAction() tooltip ("Go now", "zz_tool_a")
            use zz_tool_inner
    button:
        id "zz_tool_b"
        pos (700, 400)
        xysize (120, 50)
        background Solid("#7b2fd6")
        action NullAction()
    timer 0.05 repeat True action Function(zz_tool_tick)

screen zz_tool_inner():
    textbutton "Inner" id "zz_tool_c" action NullAction()

## A modal screen, for the helpers' waits (pc_screen and fish_screen are modal).
screen zz_tool_modal():
    modal True
    button:
        id "zz_tool_m"
        pos (900, 600)
        xysize (100, 40)
        background Solid("#2f7bd6")
        action NullAction()


label zz_smoke:

    ## --- 1. the baseline -----------------------------------------------------------
    python:
        ZZ_P0_BOOT[0] = zz_p0_snapshot()
        ZZ_P0_NOW["fresh"] = zz_p0_dump_tables("fresh")
        ZZ_P0_NOW["rich"] = zz_p0_dump_tables("rich")
        check(len(ZZ_P0_NOW["rich"]["place_actions"]) == len(LOC_ORDER) * len(PERIODS)
              and len(ZZ_P0_NOW["rich"]["person_choices"]) == len(LOC_ORDER) * len(PERIODS) * len(ROSTER_ORDER),
              "the dump covers every room x period and every person x room x period",
              (len(LOC_ORDER), len(PERIODS), len(ROSTER_ORDER)))

    ## sb_char's return tuples, every person, where the schedule has them at Noon.
    python:
        zz_p0_fixture("rich")
        ZZ_P0_NOW["sb_char"] = {}
        ZZ_WHO = builtins.list(ROSTER_ORDER)
    while ZZ_WHO:
        python:
            _zz_who = ZZ_WHO.pop(0)
            period = "Noon"
            here = zz_p0_noon_place(_zz_who)
            mission_cache_clear()
            zz_p0_quiet_view()
            renpy.show_screen("sb_char", _zz_who)
            zz_p0_render(0.1)
            ZZ_P0_NOW["sb_char"][_zz_who] = dict(here=here, returns=zz_p0_returns("sb_char"))
            renpy.hide_screen("sb_char")
    python:
        check(all(r["returns"] and r["returns"][-1] == ["cancel"] for r in ZZ_P0_NOW["sb_char"].values()),
              "sb_char: every person's card was read, Back last", ZZ_P0_NOW["sb_char"])

    ## The two screenshots: the cafeteria at Noon, then the first person there.
    python:
        zz_p0_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        mission_cache_clear()
        _zz_stage, _zz_extra = stage_people(here)
        zz_p0_quiet_view()
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_p0_render(0.3)
        zz_p0_quiet_view()
        shot("p0_place", wait=1.0)
        renpy.show_screen("sb_char", _zz_stage[0])
        zz_p0_render(1.0)
        zz_p0_quiet_view()
        shot("p0_person", wait=1.0)
        renpy.hide_screen("sb_char")
        renpy.hide_screen("sb_place")
        ZZ_P0_NOW["shots"] = dict(place=dict(here=here, period=period, day=day, stage=_zz_stage, extra=_zz_extra),
                                  person=dict(who=_zz_stage[0], here=here, period=period))
        ZZ_P0_NOW["about"] = ("Written by tools/smoke/p2_contracts.rpy (zz_p0_dump_tables and the label). "
                              "place_actions: 'room|period' -> [[id, label, hint, cost]]. "
                              "person_choices: 'who|room|period' -> an index into choice_lists, "
                              "each a list of [kind, id, label, hint, cost, gold, romance]. "
                              "sb_char: who -> the place they were shown in and the Return values of the card's buttons. "
                              "armory_tools: [[id, state, reason]] at the fixture's grade.")
        with open(os.path.join(zz_smoke_state.shots, "p0_now.json"), "w", encoding="utf-8") as _zz_f:
            json.dump(ZZ_P0_NOW, _zz_f, indent=1, sort_keys=True, ensure_ascii=False)
            _zz_f.write("\n")

    python:
        _zz_base_dir = os.path.join(zz_root(), "tools", "smoke") if zz_root() else None
        if _zz_base_dir is None or not os.path.isfile(os.path.join(_zz_base_dir, "baseline_p0.json")):
            note("baseline", "no tools/smoke/baseline_p0.json to compare with (SMOKE_ROOT unset, or not written yet)")
        else:
            with open(os.path.join(_zz_base_dir, "baseline_p0.json"), encoding="utf-8") as _zz_f:
                _zz_base = json.load(_zz_f)
            check(set(_zz_base) >= {"fresh", "rich", "sb_char", "shots"}, "the baseline file loads", sorted(_zz_base))
            ## Through JSON, so tuples and lists compare alike.
            zz_p0_compare(_zz_base, json.loads(json.dumps(ZZ_P0_NOW)))
            ## Wave 0 only (the header): later packages redraw both views.
            _zz_shots_dir = smoke_env("SMOKE_P0_SHOTS") or os.path.join(_zz_base_dir, "baseline_shots")
            for _zz_n in ("place", "person"):
                _zz_ok, _zz_why = zz_png_same(os.path.join(zz_smoke_state.shots, "p0_%s.png" % _zz_n),
                                              os.path.join(_zz_shots_dir, "%s.png" % _zz_n))
                zz_p0_check(_zz_ok, "baseline: the %s view is pixel-identical to %s/%s.png"
                            % (_zz_n, os.path.basename(_zz_shots_dir), _zz_n), _zz_why)

    ## --- 2. the measuring helpers of _lib.rpy --------------------------------------
    python:
        zz_p0_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        zz_p0_quiet_view()
    scene expression graded_bg()
    show yuji happy at pos_c
    show screen zz_tool
    python:
        _zz_w = zz_words("zz_tool")
        check(_zz_w == ["Three", "plain", "words", "Bold", "and", "red", "kanji", "Go", "now", "Inner"],
              "zz_words: letter-bearing tokens, tags stripped, icon_glyph texts skipped, used screens counted", _zz_w)
        _zz_t = zz_texts("zz_tool")
        check("Three plain words" in _zz_t and "+2 ◆ 1" in _zz_t and u"縁" in _zz_t and "Inner" in _zz_t
              and "Not on this screen" not in _zz_t, "zz_texts: every Text's string, glyphs included", _zz_t)
        check(zz_buttons("zz_tool") == 3, "zz_buttons: three focusable widgets (one in a used screen)", zz_buttons("zz_tool"))
        check(zz_rect("zz_tool", "zz_tool_b") == (700, 400, 120, 50), "zz_rect: a button's rectangle by id",
              zz_rect("zz_tool", "zz_tool_b"))
        _zz_ra = zz_rect("zz_tool", "zz_tool_a")
        _zz_rc = zz_rect("zz_tool", "zz_tool_c")
        check(_zz_ra is not None and _zz_rc is not None and _zz_ra[0] == 120 and _zz_ra[2] > 40
              and _zz_rc[1] > _zz_ra[1], "zz_rect: a textbutton, and one inside a used screen", (_zz_ra, _zz_rc))
        check(zz_rect("zz_tool", "zz_no_such_id") is None and zz_rect("zz_no_such_screen", "zz_tool_b") is None
              and zz_buttons("zz_no_such_screen") == 0 and zz_words("zz_no_such_screen") == [],
              "the helpers answer None / 0 / [] for what isn't there")
        ## Over a modal screen, with Ren'Py's default (a modal screen holds a
        ## timed pause open) put back for the span: the helpers' own waits
        ## still end, or this run stops at the watchdog.
        config.modal_blocks_pause = True
        renpy.show_screen("zz_tool_modal")
        _zz_rm = zz_rect("zz_tool_modal", "zz_tool_m")
        _zz_sm = shot("modal_helper")
        renpy.hide_screen("zz_tool_modal")
        zz_render()
        config.modal_blocks_pause = False
        check(_zz_rm == (900, 600, 100, 40) and _zz_sm,
              "the measuring helpers and shot() work over a modal screen", (_zz_rm, _zz_sm))
        _zz_n = zz_calls("zz_tool_tick", 0.6)
        check(4 <= _zz_n <= 14 and zz_tool_tick.__name__ == "zz_tool_tick",
              "zz_calls: a 0.05 s timer is counted over 0.6 s, and the function is put back", _zz_n)
        check("yuji" in zz_layer_tags("master") and "zz_tool" in zz_layer_tags("screens")
              and "yuji" not in zz_layer_tags("screens"), "zz_layer_tags: what a layer shows",
              (zz_layer_tags("master"), zz_layer_tags("screens")))

        ## The worst case, on the helper screen (with a button hovered) and on
        ## the place view as it is today.
        _zz_ok = zz_worst("zz_tool", hover="zz_tool_a")
        _zz_foc = renpy.display.focus.get_focused()
        check(_zz_ok and os.path.isfile(os.path.join(zz_smoke_state.shots, "worst_zz_tool.png")),
              "zz_worst: the screenshot is written")
        check(_zz_foc is not None and _zz_foc is renpy.get_displayable("zz_tool", "zz_tool_a", base=True),
              "zz_worst(hover=...): that button holds the focus", _zz_foc)
        check(not TOASTQ.items and not renpy.get_screen("objective_toast") and not config.skipping
              and renpy.get_screen("zz_tool"), "zz_worst: toasts, banner and skipping are put back; the screen stays")
        renpy.hide_screen("zz_tool")
        renpy.hide("yuji")
        zz_p0_quiet_view()
        _zz_ok = zz_worst("sb_place")
        check(_zz_ok and renpy.get_screen("sb_place"), "zz_worst(sb_place): the place view's worst case is on file")
        renpy.hide_screen("sb_place")

    ## --- 3. fixture() is strict (R5) -----------------------------------------------
    python:
        zz_p0_fixture("fresh")
        _zz_day = day
        try:
            fixture(day=_zz_day + 5, zz_no_such_variable=1)
            _zz_err = None
        except ZZFixtureError as _zz_e:
            _zz_err = str(_zz_e)
        check(_zz_err and "zz_no_such_variable" in _zz_err and day == _zz_day
              and not hasattr(store, "zz_no_such_variable"),
              "fixture() fails on an unknown name and sets nothing", (_zz_err, day))
        _zz_refused = []
        for _zz_k in ZZ_SHAPED:
            try:
                fixture(**{_zz_k: {}})
            except ZZFixtureError:
                _zz_refused.append(_zz_k)
        check(_zz_refused == list(ZZ_SHAPED) and set(ZZ_SHAPED) >= {
            "board_offers", "board_log", "npc_state", "inventory", "mission_state", "cb",
            "cards_state", "fish_state", "fish_log", "pc_requests"},
            "fixture() refuses every shaped variable (R5)", _zz_refused)
        try:
            fixture(day=_zz_day + 5, inventory={"paper_ward": 1})
        except ZZFixtureError:
            pass
        check(day == _zz_day and not has_item("paper_ward"), "a refused fixture() sets none of its other names")
        fixture(day=_zz_day + 1, flags=["zz_flag"], here="dojo")
        check(day == _zz_day + 1 and flags == {"zz_flag"} and here == "dojo",
              "fixture() still sets plain variables, a list becoming a set", (day, flags, here))

    ## --- 4. tools/none_ok.txt: every example returns None (R4) ---------------------
    python:
        if zz_root() is None:
            check(False, "none_ok.txt: SMOKE_ROOT is not set (an old tools/smoke.sh?)")
        else:
            _zz_rows = zz_none_ok_rows()
            _zz_names = [r[0] for r in _zz_rows]
            check({"toast_tick", "check_objective", "jr_go", "jr_toggle", "jr_wear", "jr_hold", "jr_takeoff",
                   "dev_promote", "DEV_FUNCS[key]"} <= set(_zz_names) and len(set(_zz_names)) == len(_zz_names),
                  "none_ok.txt lists the phase-1 button functions, each once", _zz_names)
            _zz_bad = []
            _zz_ran = 0
            for _zz_name, _zz_ex in _zz_rows:
                if not _zz_ex:
                    _zz_bad.append((_zz_name, "no example"))
                    continue
                if re.search(r"\bkey\b", _zz_ex):
                    ## One run for every review button, as the panel calls it.
                    for _zz_key in sorted(DEV_FUNCS):
                        _zz_rv = zz_none_ok_run(_zz_ex, key=_zz_key)
                        _zz_ran += 1
                        if _zz_rv is not None:
                            _zz_bad.append((_zz_name, _zz_key, _zz_rv))
                else:
                    if not callable(getattr(store, _zz_name, None)):
                        _zz_bad.append((_zz_name, "not a store function"))
                        continue
                    _zz_rv = zz_none_ok_run(_zz_ex)
                    _zz_ran += 1
                    if _zz_rv is not None:
                        _zz_bad.append((_zz_name, _zz_rv))
            check(not _zz_bad, "every none_ok.txt example returns None in a fresh settled fixture (%d calls)" % _zz_ran, _zz_bad)

            ## Every review button, through dev_action(key): a scene button
            ## returns its key to dev_tools; every other one runs a function
            ## that returns None.
            _zz_bad = []
            for _zz_key, _zz_title in DEV_BUTTONS:
                zz_p0_fixture("rich")
                _zz_a = dev_action(_zz_key)
                if _zz_key in DEV_SCENES:
                    if not (isinstance(_zz_a, Return) and _zz_a.value == _zz_key):
                        _zz_bad.append((_zz_key, "a scene button returns its key", _zz_a))
                elif not isinstance(_zz_a, Function):
                    _zz_bad.append((_zz_key, "not a Function", _zz_a))
                elif _zz_a() is not None:
                    _zz_bad.append((_zz_key, "did not return None"))
            check(not _zz_bad and set(DEV_FUNCS) <= set(k for k, t in DEV_BUTTONS),
                  "dev_action(key) for every review button (%d) returns None, or its key for a scene" % len(DEV_BUTTONS),
                  _zz_bad)
            zz_p0_fixture("rich")
            toast_clear()

    ## ================================================================================
    ## The contracts half (P0b, task 13). Shapes and rules only, never a stub's own
    ## value, so it runs unchanged in every worktree and on the merged tree.
    ## ================================================================================

    ## --- 5. ZZ_RETURNS: signature, owning file, return shape (R2, R3) ----------------
    python:
        _zz_bad_sig, _zz_bad_file, _zz_bad_ret = [], [], []
        for _zz_name, _zz_file, _zz_sig, _zz_ex, _zz_ok in ZZ_RETURNS:
            _zz_fn = getattr(store, _zz_name, None)
            if not callable(_zz_fn):
                _zz_bad_sig.append((_zz_name, "not defined"))
                continue
            if str(inspect.signature(_zz_fn)) != _zz_sig:
                _zz_bad_sig.append((_zz_name, str(inspect.signature(_zz_fn)), _zz_sig))
            if not _zz_fn.__code__.co_filename.replace("\\", "/").endswith("game/" + _zz_file):
                _zz_bad_file.append((_zz_name, _zz_fn.__code__.co_filename, _zz_file))
            if not (_zz_fn.__doc__ or "").strip():
                _zz_bad_sig.append((_zz_name, "no docstring"))
            if _zz_ex is None:
                continue
            zz_p0_fixture("rich")
            period = "Morning"
            here = "dorm"
            mission_cache_clear()
            try:
                _zz_rv = eval(_zz_ex, store.__dict__)
                if not _zz_ok(_zz_rv):
                    _zz_bad_ret.append((_zz_name, _zz_ex, repr(_zz_rv)[:200]))
            except Exception as _zz_e:
                _zz_bad_ret.append((_zz_name, _zz_ex, "raised %r" % (_zz_e,)))
            renpy.hide("yuji")
        check(not _zz_bad_sig, "ZZ_RETURNS: every contract function has its frozen signature and a docstring (%d)"
              % len(ZZ_RETURNS), _zz_bad_sig)
        check(not _zz_bad_file, "ZZ_RETURNS: every contract function lives in its owner's file", _zz_bad_file)
        check(not _zz_bad_ret, "ZZ_RETURNS: every example call returns the frozen type or shape", _zz_bad_ret)
        check(len(set(r[0] for r in ZZ_RETURNS)) == len(ZZ_RETURNS) >= 65, "ZZ_RETURNS: each function once", len(ZZ_RETURNS))

        _zz_bad = [(n, zz_screen_params(n), want) for n, want in ZZ_P2_SCREENS if zz_screen_params(n) != want]
        check(not _zz_bad, "the contract screens exist with exactly their parameters (%d)" % len(ZZ_P2_SCREENS), _zz_bad)
        _zz_bad = [(n, zz_label_nparams(n), want) for n, want in ZZ_P2_LABELS if zz_label_nparams(n) != want]
        check(not _zz_bad, "the contract labels exist with their parameter counts (%d)" % len(ZZ_P2_LABELS), _zz_bad)
        zz_p0_restore(ZZ_P0_BOOT[0])
        _zz_bad = [(n, type(getattr(store, n, None)).__name__) for n, t in ZZ_P2_DEFAULTS
                   if not isinstance(getattr(store, n, None), t) or isinstance(getattr(store, n, None), bool)]
        check(not _zz_bad, "every default of 3.3 is defined, with its type (%d)" % len(ZZ_P2_DEFAULTS), _zz_bad)
        check(VIEW_TICK == 0.05 and isinstance(ITEM_REQS, builtins.dict) and RULE_HANGOUT_AFTER == "roll_call"
              and isinstance(HOT_SPOTS, builtins.list) and isinstance(MG_GAMES, builtins.list)
              and isinstance(RULE_LAYOUT, builtins.dict) and persistent.motion in (True, False),
              "VIEW_TICK is 0.05; ITEM_REQS, HOT_SPOTS, MG_GAMES, RULE_LAYOUT, RULE_HANGOUT_AFTER, persistent.motion exist")
        check(all({"key", "name", "seal", "places", "anchor", "bg", "blurb", "spots"} <= set(a) for a in AREAS)
              and all(isinstance(a["spots"], builtins.dict) and isinstance(a["blurb"], str) and isinstance(a["bg"], str)
                      for a in AREAS), "AREAS rows have bg, blurb and spots", [sorted(a) for a in AREAS][:1])
        check("library" in LOCATIONS and "library" in LOC_ORDER and "library" in AREA_BY_KEY["school"]["places"]
              and area_of("library") == "school" and renpy.has_image("bg library", exact=True)
              and _validate_world() == [], "the Library is a place in the School Building, with a picture",
              _validate_world())
        check(config.always_shown_screens.count("hover_label") == 1, "hover_label is always shown, once",
              config.always_shown_screens)

    ## --- 6. grades and icons (4.3, 4.8) ----------------------------------------------
    python:
        zz_p0_fixture("rich")
        check(grade_color("s1") == grade_color("g1") and grade_tier("s1") == "g1",
              "grade_color('s1') == grade_color('g1')", (grade_color("s1"), grade_color("g1")))
        check(grade_tier(0) == "sp" and grade_is_special(0) and grade_is_special("sp") and not grade_is_special("g1"),
              "grade_tier(0) == 'sp' (a legacy enemy grade)", grade_tier(0))
        check([grade_tier(k) for k in GRADE_ORDER] == ["g4", "g3", "g2", "g1", "g1", "sp"]
              and grade_tier(None) is None and grade_tier("zz") is None and grade_tier(4) == "g4",
              "grade_tier for every grade, None when ungraded", [grade_tier(k) for k in GRADE_ORDER])
        check([grade_color(k) for k in ("g4", "g3", "g2", "g1", "sp")]
              == [gui.grade_g4, gui.grade_g3, gui.grade_g2, gui.grade_g1, gui.grade_sp]
              == ["#4fbf7a", "#4a90e2", "#9b5de5", "#e5383b", "#9fe8d8"] and grade_color(None) == gui.dim
              and gui.grade_sp_base == "#16121f", "the grade tokens (D15), gui.dim when ungraded")
        check(all(zz_is_disp(grade_fill(k)) for k in list(GRADE_ORDER) + [None, 0]), "grade_fill is a displayable for every grade")

        check(len(ICONS) == 88 and all(isinstance(r, builtins.tuple) and len(r) == 2 and r[0] and r[1] for r in ICONS.values()),
              "ICONS holds the 88 names, each (kanji, word)", len(ICONS))
        check(ICON_GOLD == {"mission", "night_gojo"} and gui.icon_words in ("auto", "always", "never")
              and icon_validate() == [], "ICON_GOLD, gui.icon_words, and the icon validator is clean", icon_validate())
        _zz_miss = []
        for _zz_a in ACTIVITIES:
            if ("do", _zz_a["id"]) not in ICON_FOR:
                _zz_miss.append(("do", _zz_a["id"]))
        for _zz_a in PLACE_ACTIONS:
            if ("act", _zz_a["id"]) not in ICON_FOR:
                _zz_miss.append(("act", _zz_a["id"]))
        for _zz_k, _zz_kan, _zz_lab in JOURNAL_TABS:
            if ("tab", _zz_k) not in ICON_FOR:
                _zz_miss.append(("tab", _zz_k))
        for _zz_a in AREAS:
            if ("area", _zz_a["key"]) not in ICON_FOR:
                _zz_miss.append(("area", _zz_a["key"]))
        for _zz_l in LOC_ORDER:
            if ("place", _zz_l) not in ICON_FOR:
                _zz_miss.append(("place", _zz_l))
        for _zz_kind in ("fresh", "rich", "explore"):
            zz_p0_fixture("rich" if _zz_kind == "explore" else _zz_kind)
            store.explore_mode = (_zz_kind == "explore")
            for _zz_l in LOC_ORDER:
                for _zz_per in PERIODS:
                    period = _zz_per
                    here = _zz_l
                    for _zz_a in place_actions(_zz_l):
                        if ("act", _zz_a[0]) not in ICON_FOR and ("act", _zz_a[0]) not in _zz_miss:
                            _zz_miss.append(("act", _zz_a[0]))
            store.explore_mode = False
        check(not _zz_miss and all(v in ICONS for v in ICON_FOR.values()),
              "icon coverage: every activity, place action (every room x period), tab, area and room maps to an icon",
              _zz_miss)
        check(icon_for("mission", "m_anything") == "mission" and icon_for("act", "zz_unmapped") == "act"
              and icon_for("do", "rom_say") == "heart" and icon_label("map") == "Map"
              and icon_label("zz_unknown") == "zz_unknown" and zz_is_disp(icon("zz_unknown")),
              "icon_for: a mission is `mission`, unmapped is `act`; an unknown icon still draws")
        check(icon_words_shown("map", "always") and not icon_words_shown("map", "never")
              and icon_words_shown("map") == (gui.icon_words == "always" or (gui.icon_words == "auto" and not icon_has_art("map"))),
              "words under an icon: always, never, or auto while it has no picture")
        check(ui_do(lambda: 7) is None and ui_do(max, 1, 2) is None, "ui_do returns None whatever its function returns")

    ## --- 7. the registries, the hotspots, rail_actions ---------------------------------
    python:
        zz_p0_fixture("fresh")
        check(ZZ_ORDER_HOTSPOT in [h["id"] for h in HOT_SPOTS] and ZZ_ORDER_GAME in [g["id"] for g in mg_games()],
              "init order: aa_zz_order.rpy registered its hotspot and its game at init 0 (the registries exist by init -5)")
        check(hot_validate() == [], "the hotspot and minigame validator is clean", hot_validate())
        check(ZZ_ORDER_HOTSPOT not in [h["id"] for h in hot_spots_for("dorm")],
              "a look hotspot whose `when` is False is not visible")

        ## Duplicates are findings (R2).
        _zz_rv1 = register_hotspot(ZZ_ORDER_HOTSPOT, "dorm", 300, 500, "look", lines=["Twice."], label="Twice")
        _zz_rv2 = register_minigame(ZZ_ORDER_GAME, "Twice", "act")
        _zz_v = hot_validate()
        check(_zz_rv1 is None and _zz_rv2 is None and any("hotspot" in x and "registered twice" in x for x in _zz_v)
              and any("minigame" in x and "registered twice" in x for x in _zz_v),
              "a duplicate hotspot id and a duplicate minigame id are each a finding", _zz_v)
        del HOT_SPOTS[-1]
        del MG_GAMES[-1]
        check(hot_validate() == [], "…and gone again once the duplicates are", hot_validate())

        ## The validator's other rules, on bad rows.
        register_hotspot("zz_bad_place", "zz_nowhere", 300, 500, "look", lines=["x"])
        register_hotspot("zz_bad_icon", "dorm", 300, 500, "zz_no_icon", lines=["x"])
        register_hotspot("zz_bad_act", "dorm", 300, 500, "look", act="zz_no_action")
        register_hotspot("zz_bad_label", "dorm", 300, 500, "sleep", act="sleep", label="Mine")
        register_hotspot("zz_bad_alone", "dorm", 1500, 640, "look", act="sleep", standalone=True)
        register_hotspot("zz_bad_lane", "dorm", 1500, 200, "look", lines=["x"])
        register_hotspot("zz_bad_point", "dorm", 1800, 100, "look", lines=["x"])
        register_hotspot("zz_bad_when", "dorm", 300, 500, "look", lines=["x"], when="zz_no_such_function")
        _zz_v = hot_validate()
        _zz_want = ["zz_bad_place", "zz_bad_icon", "zz_bad_act", "zz_bad_label", "zz_bad_alone", "zz_bad_lane",
                    "zz_bad_point", "zz_bad_when"]
        check(all(any(repr(k) in x for x in _zz_v) for k in _zz_want),
              "the hotspot validator: place, icon, action label, own label, standalone without `when`, lane, bounds, `when`",
              _zz_v)
        zz_hot_drop(*_zz_want)

        ## A look hotspot, an action hotspot, a standalone, on test rows.
        period = "Morning"
        here = "dorm"
        companion = None
        _zz_base_rail = rail_actions("dorm")
        check("study" in [a[0] for a in _zz_base_rail] and "study" in [a[0] for a in place_actions("dorm")],
              "before: Study is in my room's column")
        register_hotspot("zz_look", "dorm", 300, 500, "look", lines=["A.", "B.", "C."], label="A test thing")
        register_hotspot("zz_desk", "dorm", 700, 600, "study", act="study")
        register_hotspot("zz_alone", "dorm", 1500, 640, "spot_vend", act="wait", label="Alone", hint="A test.",
                         cost=0, when="zz_order_never", standalone=True)
        _zz_rows = builtins.dict((h["id"], h) for h in hot_spots_for("dorm"))
        check(zz_hot_rows(list(_zz_rows.values())) and "zz_look" in _zz_rows and "zz_desk" in _zz_rows
              and "zz_alone" not in _zz_rows, "hot_spots_for: the visible rows, as dicts with the eleven keys",
              sorted(_zz_rows))
        _zz_d = _zz_rows.get("zz_desk", {})
        _zz_study = [a for a in place_actions("dorm") if a[0] == "study"][0]
        check((_zz_d.get("label"), _zz_d.get("hint"), _zz_d.get("cost")) == _zz_study[1:4] and _zz_d.get("act") == "study"
              and _zz_d.get("lines") is None and _zz_d.get("front") is False,
              "an action hotspot takes its label, hint and cost from its place_actions row", _zz_d)
        _zz_l = _zz_rows.get("zz_look", {})
        check(_zz_l.get("lines") == ["A.", "B.", "C."] and _zz_l.get("act") is None and _zz_l.get("label") == "A test thing"
              and (_zz_l.get("x"), _zz_l.get("y")) == (300, 500), "a look hotspot carries its own lines and label", _zz_l)
        check("study" in hot_covers("dorm") and "study" not in [a[0] for a in rail_actions("dorm")]
              and "study" in [a[0] for a in place_actions("dorm")]
              and [a for a in rail_actions("dorm")] == [a for a in _zz_base_rail if a[0] != "study"],
              "a visible action hotspot covers its action: gone from rail_actions, still in place_actions",
              (hot_covers("dorm"), [a[0] for a in rail_actions("dorm")]))
        check(isinstance(hot_action(_zz_l), Return) and hot_action(_zz_l).value == ("hot", "zz_look")
              and (not hot_open(_zz_d) or (isinstance(hot_action(_zz_d), Return) and hot_action(_zz_d).value == ("act", "study"))),
              "a look returns ('hot', id); an action hotspot returns ('act', id)")
        check(hot_tip(_zz_d) == "%s\n%s · 1 period" % (_zz_study[1], _zz_study[2]) and hot_tip(_zz_l) == "A test thing",
              "the hover label of a hotspot: label, then hint and cost", hot_tip(_zz_d))
        check(hot_line("zz_look") == ["A.", "B.", "C."][day % 3] and hot_line("zz_desk") is None and hot_line("zz_none") is None,
              "hot_line: today's line of a look hotspot", hot_line("zz_look"))

        ## Someone standing in front hides it, and the action is back in the column.
        if "yuji" not in roster:
            roster.append("yuji")
        companion = "yuji"
        _zz_rects = view_person_rects("dorm")
        ## Wherever the room's slots put them (P5 moves the slots): the desk
        ## hotspot goes to the middle of the first person for this check.
        _zz_hd = [h for h in HOT_SPOTS if h["id"] == "zz_desk"][0]
        _zz_was = (_zz_hd["x"], _zz_hd["y"])
        if _zz_rects:
            _zz_hd["x"] = _zz_rects[0][0] + _zz_rects[0][2] // 2
            _zz_hd["y"] = _zz_rects[0][1] + _zz_rects[0][3] // 2
        _zz_rail = rail_actions("dorm")
        check(len(_zz_rects) == len(stage_people("dorm")[0]) >= 1
              and "zz_desk" not in [h["id"] for h in hot_spots_for("dorm")]
              and "study" not in hot_covers("dorm") and "study" in [a[0] for a in _zz_rail],
              "a hotspot behind someone is not visible, and its action is back in the column", (_zz_rects, hot_covers("dorm")))
        check(_zz_rail and _zz_rail[-1][0] == "release" and _zz_rail[-1][1] == "Let them go" and _zz_rail[-1][3] == 0
              and _zz_rail[-1][4] == "release" and _zz_rail[-1][5] is False and zz_is_str(_zz_rail[-1][2]) and _zz_rail[-1][2]
              and [a[0] for a in _zz_rail].count("release") == 1 and zz_rows6(_zz_rail),
              "rail_actions with a companion ends in the release row", _zz_rail[-1:])
        check(len(view_person_rects("dorm")) == len(stage_people("dorm")[0]),
              "view_person_rects: one rectangle a person on stage", view_person_rects("dorm"))
        _zz_hd["x"], _zz_hd["y"] = _zz_was
        companion = None
        check(not rail_actions("dorm") or rail_actions("dorm")[-1][0] != "release", "…and without one it doesn't")

    ## hot_use: today's line is said, and the spot is marked used today.
    $ zz_p0_fixture("fresh")
    $ _zz_texts0 = []
    $ _zz_prev_filter = config.say_menu_text_filter
    python:
        def _zz_say_filter(s):
            _zz_texts0.append(s)
            return _zz_prev_filter(s) if _zz_prev_filter else s
        config.say_menu_text_filter = _zz_say_filter
    $ autoplay()
    python:
        _zz_said = []
        _zz_real_say = renpy.say
        def _zz_say(who, what, *args, **kwargs):
            _zz_said.append(what)
            return _zz_real_say(who, what, *args, **kwargs)
        renpy.say = _zz_say
    call hot_use("zz_look")
    call hot_use("zz_desk")
    $ renpy.say = _zz_real_say
    $ autoplay(False)
    python:
        check(_zz_said == [hot_line("zz_look")] and "hot:zz_look" in actions_today and "hot:zz_desk" not in actions_today,
              "label hot_use says today's line and adds 'hot:<id>' to actions_today; an action hotspot has no line",
              (_zz_said, sorted(actions_today)))
        zz_hot_drop("zz_look", "zz_desk", "zz_alone")
        check(hot_validate() == [], "the test rows are out of the registry again", [h["id"] for h in HOT_SPOTS])

    ## rail_actions against place_actions, and the card against the baseline.
    python:
        _zz_bad = []
        _zz_card = builtins.dict()
        for _zz_kind in ("fresh", "rich"):
            zz_p0_fixture(_zz_kind)
            for _zz_l in LOC_ORDER:
                for _zz_per in PERIODS:
                    period = _zz_per
                    here = _zz_l
                    mission_cache_clear()
                    _zz_rail = rail_actions(_zz_l)
                    _zz_cov = hot_covers(_zz_l)
                    _zz_want = [tuple(a) for a in night_filter_actions(_zz_l, place_actions(_zz_l)) if a[0] not in _zz_cov]
                    if [a[:4] for a in _zz_rail] != _zz_want or not zz_rows6(_zz_rail):
                        _zz_bad.append((_zz_kind, _zz_l, _zz_per))
                    ## What the phase-1 action card reads (sb_place's own line).
                    _zz_card["%s|%s|%s" % (_zz_kind, _zz_l, _zz_per)] = [builtins.list(a[:4]) for a in _zz_rail if a[0] != "release"]
        check(not _zz_bad, "rail_actions is night_filter_actions(place_actions) without hot_covers, each row with its icon, "
              "for every room x period", _zz_bad[:6])
        if _zz_base_dir is None or not os.path.isfile(os.path.join(_zz_base_dir, "baseline_p0.json")):
            note("the action card", "no baseline to compare with")
        elif zz_hot_real() or night_exists():
            note("the action card", "hotspots or the night rule are in: the card no longer equals the pre-phase-2 baseline "
                 "(%d hotspots, night_exists %r)" % (len(zz_hot_real()), night_exists()))
        else:
            _zz_bad = []
            for _zz_kind in ("fresh", "rich"):
                for _zz_key, _zz_old in _zz_base[_zz_kind]["place_actions"].items():
                    if _zz_card.get("%s|%s" % (_zz_kind, _zz_key)) != _zz_old:
                        _zz_bad.append((_zz_kind, _zz_key))
            check(not _zz_bad, "the phase-1 action card shows the baseline's rows for every baseline room x period "
                  "(it now reads rail_actions)", _zz_bad[:6])
            _zz_lib = [k for k in ZZ_P0_NOW["rich"]["place_actions"] if k.split("|")[0] not in
                       set(x.split("|")[0] for x in _zz_base["rich"]["place_actions"])]
            check(sorted(set(k.split("|")[0] for k in _zz_lib)) == ["library"],
                  "place_actions equals the baseline apart from the Library's own rows", sorted(set(k.split("|")[0] for k in _zz_lib)))

    ## --- 8. sidecars and the layout dump (D5) --------------------------------------------
    python:
        zz_p0_fixture("fresh")
        _zz_view = rule_layout("view_dorm_common")
        _zz_hot = rule_layout("hot_dorm_common")
        check(set(_zz_view) == {"slots", "poses"} and _zz_view["slots"]["2"][1] == [1060, -52, 0.48, 1]
              and _zz_view["poses"]["nobara__evening"] == [300, 380, 420, 640],
              "rule_layout('view_dorm_common') reads the view sidecar (slots and pose boxes)", _zz_view)
        check(set(_zz_hot) == {"spots"} and _zz_hot["spots"] == {"zz_tv": [1420, 520]},
              "rule_layout('hot_dorm_common') reads the hotspot sidecar, and only it", _zz_hot)
        _zz_view["slots"]["2"] = "changed"
        check(rule_layout("view_dorm_common")["slots"]["2"] != "changed" and rule_layout("zz_no_such_file") == {}
              and rule_layout("hot_dorm") == rule_layout("hot_dorm"),
              "rule_layout returns a fresh copy each time, and {} when there is no file")
        ## The hotspot sidecar moves a hotspot's point; the view sidecar doesn't.
        period = "Morning"
        here = "dorm_common"
        ## (aa_zz_order.rpy registers zz_tv at (300, 300), never visible; here its `when` is lifted.)
        _zz_tv = [h for h in HOT_SPOTS if h["id"] == "zz_tv"][0]
        _zz_tv["when"] = None
        ## (With nobody on stage: where people stand in this room is P5's to
        ## change, and this check is about the point alone.)
        _zz_rows = [h for h in zz_with(dict(view_person_rects=lambda loc: []), lambda: hot_spots_for("dorm_common"))
                    if h["id"] == "zz_tv"]
        check(len(_zz_rows) == 1 and (_zz_rows[0]["x"], _zz_rows[0]["y"]) == (1420, 520)
              and (_zz_tv["x"], _zz_tv["y"]) == (300, 300),
              "hot_<place>.json moves a hotspot's point", _zz_rows)
        ## The validator reads the sidecar's points too (R6): the sidecar is
        ## where the final positions are set.
        _zz_side = RULE_LAYOUT["hot_dorm_common"]
        _zz_found = []
        for _zz_spots in ({"zz_tv": [1500, 200]}, {"zz_tv": [30, 600]}, {"zz_tv": ["a", 2]}, {"zz_tv": [300, 300, 4]},
                          {"zz_tv": [1420, 520], "zz_no_such_spot": [600, 600]}, "zz_not_a_dict"):
            RULE_LAYOUT["hot_dorm_common"] = {"spots": _zz_spots}
            _zz_found.append(hot_validate())
        RULE_LAYOUT["hot_dorm_common"] = _zz_side
        check(len(_zz_found[0]) == 1 and "lane" in _zz_found[0][0] and "sidecar hot_dorm_common.json" in _zz_found[0][0],
              "a sidecar point inside the toast lane is one finding", _zz_found[0])
        check(len(_zz_found[1]) == 1 and "outside" in _zz_found[1][0]
              and len(_zz_found[2]) == 1 and "not two numbers" in _zz_found[2][0]
              and len(_zz_found[3]) == 1 and "not two numbers" in _zz_found[3][0]
              and len(_zz_found[4]) == 1 and "zz_no_such_spot" in _zz_found[4][0]
              and len(_zz_found[5]) == 1 and "spots" in _zz_found[5][0],
              "…and so is one out of bounds, one that is not two numbers, an id nobody registered, and a file of the wrong shape",
              _zz_found[1:])
        check(hot_validate() == [], "with the overlay's own sidecar back the validator is clean", hot_validate())
        _zz_tv["when"] = "zz_order_never"
        del _zz_tv

        _zz_def = zz_layout_defaults()
        check(set(_zz_def["slots"]) == set(LOC_ORDER) and all(
                  set(v) == {"1", "2", "3", "4"} and all(zz_slots(v[str(n)], n) for n in (1, 2, 3, 4))
                  for v in _zz_def["slots"].values())
              and set(_zz_def["areas"]) == set(a["key"] for a in AREAS),
              "the layout dump: view_slots for every room and 1 to 4 people, map_spots for every area")
        if zz_root():
            _zz_dir = os.path.join(zz_root(), "shots", "layout")
            if not os.path.isdir(_zz_dir):
                os.makedirs(_zz_dir)
            with open(os.path.join(_zz_dir, "defaults.json"), "w", encoding="utf-8") as _zz_f:
                json.dump(_zz_def, _zz_f, indent=1, sort_keys=True, ensure_ascii=False)
                _zz_f.write("\n")
            check(os.path.isfile(os.path.join(_zz_dir, "defaults.json")), "the code defaults are in shots/layout/defaults.json")
            note("layout dump", "%d rooms, %d areas with spots, %d hotspots" % (
                len(_zz_def["slots"]), len([k for k, v in _zz_def["areas"].items() if v]),
                sum(len(v) for v in _zz_def["hotspots"].values())))
        else:
            check(False, "the layout dump needs SMOKE_ROOT (an old tools/smoke.sh?)")

    ## --- 9. the rules -------------------------------------------------------------------
    ## The soft clock (D26).
    python:
        zz_p0_fixture("rich")
        check(zz_soft("Morning", 2, waiting=["st_roster"]) == (False, "Noon", 22),
              "advance_period_soft(2) from Morning, st_roster waiting at Noon: stops at Noon, returns False",
              zz_soft("Morning", 2, waiting=["st_roster"]))
        check(zz_soft("Morning", 2) == (False, "Afternoon", 22),
              "advance_period_soft(2) from Morning, nothing waiting: reaches Afternoon", zz_soft("Morning", 2))
        check(zz_soft("Evening", 2) == (False, "Night", 22), "advance_period_soft(2) from Evening stops at Night",
              zz_soft("Evening", 2))
        check(zz_soft("Night", 1) == (True, "Morning", 23), "advance_period_soft(1) at Night rolls the day and returns True",
              zz_soft("Night", 1))
        check(zz_soft("Afternoon", 3) == (False, "Night", 22) and zz_soft("Noon", 1, waiting=["st_roster"]) == (False, "Afternoon", 22),
              "three periods from the Afternoon stop at Night; the last step is never cut")
        check(zz_with(dict(advance_period=lambda n=1: "explore"), lambda: (setattr(store, "explore_mode", True),
                                                                      advance_period_soft(2))[1]) == "explore",
              "in explore mode the soft clock is advance_period")
        store.explore_mode = False

        ## A beat waiting at the gate while I stand elsewhere, and no random draw.
        zz_p0_fixture("rich")
        period = "Morning"
        here = "dojo"
        _zz_asked = []
        def _zz_has_event(kind, who=None, loc=None):
            _zz_asked.append((kind, who, loc))
            return loc == "gate"
        _zz_state = renpy.random.getstate()
        _zz_rv = zz_with(dict(has_event=_zz_has_event), lambda: advance_period_soft(2, loc="gate"))
        check(_zz_rv is False and period == "Noon" and _zz_asked == [("story", None, "gate")],
              "advance_period_soft(2, loc='gate') stops for a beat waiting at the gate while I stand in the dojo",
              (_zz_rv, period, _zz_asked))
        period = "Morning"
        del _zz_asked[:]
        _zz_rv = zz_with(dict(has_event=_zz_has_event), lambda: advance_period_soft(2))
        check(_zz_rv is False and period == "Afternoon" and _zz_asked == [("story", None, "dojo")],
              "…and with no loc it looks where I stand", (_zz_rv, period, _zz_asked))
        check(renpy.random.getstate() == _zz_state, "the soft clock makes no renpy.random call")

    ## The hangout gate (D25).
    python:
        zz_p0_restore(ZZ_P0_BOOT[0])
        settle(mc_name="Tester", mc_surname="Harness", day=1, period="Noon", here="courtyard")
        _zz_hang = [e for e in EVENTS if e["kind"] == "hangout"]
        _zz_who = sorted(set(e["who"] for e in _zz_hang if e["who"]))
        check(_zz_hang and not any(rule_hangout_gate(e) for e in _zz_hang) and rule_hangout_gate in EVENT_GATES
              and all(rule_hangout_gate(e) for e in EVENTS if e["kind"] != "hangout"),
              "rule_hangout_gate is False for every hangout on a fresh settled fixture (%d scenes, %d people), "
              "True for every other event" % (len(_zz_hang), len(_zz_who)), _zz_who)
        check(not any(has_event("hangout", w, l) for w in ROSTER_ORDER for l in LOC_ORDER),
              "no character scene is offered before roll call")
        flag(RULE_HANGOUT_AFTER)
        check(all(rule_hangout_gate(e) for e in _zz_hang), "…True once roll_call is set")
        zz_p0_restore(ZZ_P0_BOOT[0])
        settle(mc_name="Tester", mc_surname="Harness", day=3, period="Noon", here="courtyard")
        store.done_events.add("st_roll_call")
        check(not has_flag("roll_call") and all(rule_hangout_gate(e) for e in _zz_hang),
              "…and True for a save that lacks the flag but has st_roll_call in done_events")
        zz_p0_restore(ZZ_P0_BOOT[0])
        settle(mc_name="Tester", mc_surname="Harness", day=3, period="Noon", here="courtyard")
        flag("sunmall_done")
        check(all(rule_hangout_gate(e) for e in _zz_hang), "…or the flag sunmall_done")
        zz_p0_restore(ZZ_P0_BOOT[0])
        settle(mc_name="Tester", mc_surname="Harness", day=1, period="Noon", here="courtyard")
        store.explore_mode = True
        check(all(rule_hangout_gate(e) for e in _zz_hang), "explore mode has no roll call to wait for: the gate is open")
        store.explore_mode = False

    ## rule_walk_to: an open room, then a locked one.
    $ zz_p0_fixture("fresh")
    $ period = "Morning"
    $ here = "courtyard"
    $ del _zz_texts0[:]
    $ autoplay()
    call rule_walk_to("library")
    $ check(here == "library", "rule_walk_to('library') sets `here`", here)
    $ _zz_why = can_enter("gojo_office")
    call rule_walk_to("gojo_office")
    $ autoplay(False)
    python:
        check(_zz_why[0] is False and _zz_why[1] and here == "library"
              and any("_rule_why" in t or _zz_why[1] in t for t in _zz_texts0),
              "rule_walk_to to a locked room says why and leaves `here` alone", (here, _zz_why, _zz_texts0))
        config.say_menu_text_filter = _zz_prev_filter
    scene black

    ## The requirement validator (D27).
    python:
        zz_p0_fixture("rich")
        _zz_saved = builtins.dict(ITEM_REQS)
        check(item_validate_reqs in VALIDATORS, "item_validate_reqs is a registered validator")
        check(item_validate_reqs() == [], "item_validate_reqs() is clean on the table as shipped", item_validate_reqs())
        ITEM_REQS.clear()
        check(item_validate_reqs() == [], "item_validate_reqs() returns [] on the empty table")
        ITEM_REQS["nunchaku"] = [("grade", "g3"), ("stat", "control", GRADES["g3"]["stat"] + 5)]
        _zz_v = item_validate_reqs()
        check(len(_zz_v) == 1 and "nunchaku" in _zz_v[0] and "Control" in _zz_v[0],
              "one finding for a row whose Control threshold is above its grade's cap", _zz_v)
        ITEM_REQS["nunchaku"] = [("grade", "g3"), ("stat", "control", GRADES["g3"]["stat"]), ("stat", "insight", 100),
                                 ("flag", "zz_flag", "The words"), ("arc", 2)]
        check(item_validate_reqs() == [], "a threshold at the cap, Insight 100, a flag with words and an arc pass",
              item_validate_reqs())
        ITEM_REQS["nunchaku"] = [("stat", "insight", 101), ("flag", "zz_flag", ""), ("zz_kind", 1)]
        ITEM_REQS["zz_no_item"] = []
        check(len(item_validate_reqs()) == 4, "Insight above 100, a flag with no words, an unknown kind and an unknown item "
              "are each a finding", item_validate_reqs())
        ITEM_REQS.clear()
        ITEM_REQS.update(_zz_saved)

    ## The motion switch (D17, R9).
    python:
        _zz_motion = persistent.motion
        _zz_t = ZZTrans()
        persistent.motion = False
        check(view_motion() is False and grade_sheen_fn(_zz_t, 0.0, 0.0) is None and hot_pulse_fn(_zz_t, 0.0, 0.0) is None,
              "with persistent.motion False the sheen and pulse functions return None")
        persistent.motion = True
        check(view_motion() is True and grade_sheen_fn(_zz_t, 0.0, 0.0) == VIEW_TICK and hot_pulse_fn(_zz_t, 0.0, 0.0) == VIEW_TICK
              and 0.45 <= _zz_t.alpha <= 0.8 and _zz_t.crop[2:] == (512, 64) and 0 <= _zz_t.crop[0] < 1024,
              "with it on they return VIEW_TICK (0.05), never 0", (_zz_t.alpha, _zz_t.crop))
        persistent.motion = _zz_motion

    ## --- 10. the screens -----------------------------------------------------------------
    ## The Library renders.
    python:
        zz_p0_fixture("rich")
        period = "Noon"
        here = "library"
        mission_cache_clear()
        zz_p0_quiet_view()
    scene expression graded_bg()
    show screen sb_place
    python:
        zz_render(0.3)
        zz_p0_quiet_view()
        check(renpy.get_screen("sb_place") is not None and zz_buttons("sb_place") >= 3,
              "here = 'library' renders sb_place", zz_buttons("sb_place"))
        shot("library_place", wait=0.6)
        renpy.hide_screen("sb_place")

    ## The old map: a hovered row shows one label, not two. (The locked office
    ## has a reason to show; after P1 the same reason is the hover label's.)
    python:
        zz_p0_fixture("fresh")
        period = "Noon"
        here = "courtyard"
        _zz_why = can_enter("gojo_office")[1]
        renpy.show_screen("sb_map", area=area_of("gojo_office"))
        zz_render(0.4)
        renpy.set_focus("sb_map", "row_gojo_office")
        zz_render(0.5)
        _zz_tip = GetTooltip()
        _zz_n = len([t for t in zz_texts("sb_map") + zz_texts("hover_label") if _zz_why and _zz_why in t])
        check(_zz_tip is not None and _zz_n == 1,
              "hovering a locked row on the map shows one label, not two", (_zz_tip, _zz_n))
        check((icon_tip_parts(_zz_tip) is None) == isinstance(_zz_tip, str) and icon_tip_parts("plain") is None
              and icon_tip_parts(("Title\nhint", "k")) == ("Title", "hint") and icon_tip_parts(None) is None,
              "hover_label draws tuple tooltips only; a plain string is left to its own screen")
        shot("map_hover", wait=0)

        ## SKIPPING: not over the map (a sandbox screen), back over a scene.
        _zz_over = "SKIPPING" in zz_skip_texts()
        renpy.hide_screen("sb_map")
        _zz_scene = "SKIPPING" in zz_skip_texts()
        check(not _zz_over and _zz_scene, "the SKIPPING tag is hidden over the map and shown over a scene", (_zz_over, _zz_scene))

    ## Preferences has the Motion row, and it switches view_motion().
    python:
        renpy.show_screen("preferences")
        zz_render(0.4)
        _zz_t = zz_texts("preferences")
        check("MOTION" in _zz_t and "On" in _zz_t and "Off" in _zz_t, "Preferences has a Motion row", _zz_t[:40])
        renpy.hide_screen("preferences")
        SetField(persistent, "motion", False)()
        _zz_off = view_motion()
        SetField(persistent, "motion", True)()
        check(_zz_off is False and view_motion() is True, "the Motion row's actions switch view_motion()")

    ## The review panel: the six new buttons, the ones whose feature isn't built left out.
    python:
        zz_p0_fixture("rich")
        _zz_keys = [k for k, t in DEV_BUTTONS]
        check(all(k in _zz_keys for k in ("night", "gojo_night", "rest", "yen", "market", "sample")) and "sample" in DEV_SCENES
              and len(_zz_keys) == len(set(_zz_keys)), "the review panel has the six phase-2 buttons", _zz_keys)
        _zz_rows = [k for k, t in dev_rows()]
        check(("market" in _zz_rows) == bool(market_exists()) and ("gojo_night" in _zz_rows) == bool(night_exists())
              and ("rest" in _zz_rows) == bool(night_exists()) and all(k in _zz_rows for k in ("night", "yen", "sample")),
              "a review button whose feature isn't built is left out (market_exists, night_exists)", _zz_rows)
        _zz_y = yen
        dev_action("yen")()
        dev_action("night")()
        check(yen == _zz_y + 20000 and period == "Night" and isinstance(dev_action("sample"), Return)
              and dev_action("sample").value == "sample" and dev_sensitive("sample"),
              "+¥20,000 and Jump to Night work; Style sample returns 'sample' to dev_tools", (yen, period))
        toast_clear()
        period = "Noon"
        here = "courtyard"
        zz_p0_quiet_view()
        renpy.show_screen("dev_panel")
        zz_render(0.4)
        check(zz_buttons("dev_panel") == len(_zz_rows) + 1, "the panel draws one button a row, and Close",
              (zz_buttons("dev_panel"), len(_zz_rows)))
        shot("dev_panel", wait=0)
        ## With the night and the market built it is 3 x 7: it must still fit.
        def _zz_panel_full():
            zz_render(0.3)
            return zz_buttons("dev_panel"), zz_rect("dev_panel", "dev_close")
        _zz_n, _zz_r = zz_with(dict(night_exists=lambda: True, market_exists=lambda: True), _zz_panel_full)
        check(_zz_n == len(DEV_BUTTONS) + 1 and _zz_r is not None and _zz_r[1] + _zz_r[3] <= 1060,
              "with every feature built the panel is 3 x 7 and still fits the screen", (_zz_n, _zz_r))
        shot("dev_panel_full", wait=0)
        renpy.hide_screen("dev_panel")

    ## dev_tools opens the style sample and comes back (autoplay closes both).
    $ zz_p0_fixture("rich")
    $ autoplay()
    $ _zz_seen = []
    python:
        def _zz_sample_seen():
            if renpy.get_screen("icon_sample") and not _zz_seen:
                _zz_seen.append(True)
        config.start_interact_callbacks.append(_zz_sample_seen)
    call screen icon_sample
    $ check(_return == ("close",) and _zz_seen, "icon_sample returns ('close',)", _return)
    $ autoplay(False)
    $ config.start_interact_callbacks.remove(_zz_sample_seen)

    ## The hover label: one button hovered, four toasts queued, held across 20
    ## ticks of the toast timer.
    python:
        zz_p0_fixture("rich")
        period = "Noon"
        here = "cafeteria"
        zz_p0_quiet_view()
        ## Eight, so four are still up (or waiting, where toasts wait) to the end.
        for _zz_i in range(8):
            toast("Hover test %d: a reward line long enough to wrap onto a second line" % (_zz_i + 1),
                  ("info", "stat", "item", "grade")[_zz_i % 4])
        _zz_queued = len(TOASTQ.items)
    scene expression graded_bg()
    show screen icon_sample
    python:
        zz_render(0.5)
        check(zz_rect("icon_sample", "sample_auto_train") is not None and zz_rect("icon_sample", "sample_close") is not None,
              "the style sample draws its icon buttons", zz_rect("icon_sample", "sample_auto_train"))
        _zz_w = zz_words("icon_sample")
        ## The first sample icon that still has no picture (art batch 1 installs
        ## pictures for most of them; a picture has no kanji to look for).
        _zz_n = next((n for n in ICON_SAMPLE if not icon_has_art(n)), None)
        if _zz_n is None:
            note("the style sample", "every sample icon has its picture: no stand-in kanji left to check")
        else:
            _zz_g = ICONS[_zz_n][0]
            check(not any(_zz_g in t for t in _zz_w) and _zz_g in zz_texts("icon_sample"),
                  "a stand-in icon's kanji is in the style icon_glyph (zz_words skips it)", (_zz_n, _zz_g))
        check("Train" in _zz_w, "an icon's word is counted on the row that always shows words", _zz_w[:20])
        renpy.set_focus("icon_sample", "sample_auto_train")
        zz_render(0.3)
        _zz_before = zz_texts("hover_label")
        _zz_ticks = zz_calls("toast_tick", 3.6)
        _zz_left = len(TOASTQ.items)
        _zz_after = zz_texts("hover_label")
        _zz_tip = GetTooltip()
        check(_zz_queued == 8 and _zz_left >= 4 and _zz_before == ["Train"] and _zz_after == ["Train"]
              and _zz_tip == ("Train", "sample_auto_train"),
              "the hover label holds for 3.6 seconds with eight toasts queued (%d toast-timer ticks)" % _zz_ticks,
              (_zz_queued, _zz_left, _zz_ticks, _zz_before, _zz_after, _zz_tip))
        ## While toasts draw over the sample (wave 0) the timer must be seen
        ## ticking; once they wait here (P2: toast_room() is (0, 0, 0)) the
        ## screen may stop its timer.
        if toast_room()[2] or ZZ_P0_STRICT:
            check(_zz_ticks >= 20, "the toast timer ticked at least 20 times under the hover label", _zz_ticks)
        else:
            note("the toast timer under the hover label", "%d ticks while toasts wait over the sample" % _zz_ticks)
        _zz_r = zz_rect("icon_sample", "sample_auto_train")
        shot("hover_sample", wait=0)
        renpy.set_focus("icon_sample", "sample_choice")
        zz_render(0.4)
        check(len(zz_texts("hover_label")) == 2 and zz_texts("hover_label")[0] == "Spend time together",
              "'Title\\nhint' draws two lines, and the label follows the focus to the next button", zz_texts("hover_label"))
        shot("hover_sample_choice", wait=0)
        toast_clear()
        renpy.hide_screen("icon_sample")
        zz_render(0.2)
        check(zz_texts("hover_label") == [], "with nothing hovered the label draws nothing", zz_texts("hover_label"))

    ## --- 11. a save made on the place view reloads (R10) ------------------------------------
    ## The harness's own scratch names (closed file handles, lambdas) are not
    ## the game's state. They leave the store here, and the rollback log that
    ## still remembers them is cut short just before the save, so the save
    ## holds what a player's would: the store, the scene and the screens.
    python:
        if ZZ_SAVE[0] == 0:
            for _zz_k in [k for k in builtins.list(store.__dict__) if k.startswith("_zz")]:
                if _zz_k != "_zz_k":
                    delattr(store, _zz_k)
            del _zz_k
    ## (An entry of the log ends at an interaction: two, so the names above
    ## are in an entry of their own, behind the two the save keeps.)
    $ zz_render(0.1)
    $ zz_render(0.1)
    python:
        if ZZ_SAVE[0] == 0:
            zz_p0_fixture("rich")
            period = "Noon"
            here = "cafeteria"
            mission_cache_clear()
            zz_p0_quiet_view()
            ## A point nobody on stage covers, wherever this room's slots put
            ## them (P5 moves the slots): the first clear one of these.
            _zz_pts = ((1500, 520), (1620, 700), (120, 700), (960, 240), (300, 240), (1620, 420), (120, 420))
            _zz_people = view_person_rects(here)
            _zz_pt = ([p for p in _zz_pts if not any(hot_overlap(hot_rect(*p), r) for r in _zz_people)] or _zz_pts[:1])[0]
            register_hotspot("zz_save_spot", "cafeteria", _zz_pt[0], _zz_pt[1], "look", lines=["Saved."], label="A test spot")
    scene expression graded_bg()
    show screen sb_place
    $ zz_render(0.4)
    python:
        if ZZ_SAVE[0] == 0:
            ZZ_SAVE[0] = 1
            _zz_stage = stage_people(here)[0]
            check(len(_zz_stage) >= 1 and "zz_save_spot" in [h["id"] for h in hot_spots_for(here)],
                  "the place view to be saved has people on stage and a hotspot", _zz_stage)
            ## The harness's own scratch names (file handles, lambdas) are not
            ## the game's state: out of the store before it is pickled.
            for _zz_k in [k for k in builtins.list(store.__dict__) if k.startswith("_zz") and k != "_zz_k"]:
                delattr(store, _zz_k)
            del _zz_k
            import pickle as _zz_pickle
            _zz_bad = []
            for _zz_k in builtins.sorted(renpy.python.store_dicts["store"].ever_been_changed):
                if _zz_k.startswith("_zz") or _zz_k not in store.__dict__:
                    continue
                try:
                    _zz_pickle.dumps(getattr(store, _zz_k), _zz_pickle.HIGHEST_PROTOCOL)
                except Exception as _zz_e:
                    _zz_bad.append((_zz_k, repr(_zz_e)[:120]))
            check(not _zz_bad, "every store variable the save will hold pickles", _zz_bad)
            del renpy.game.log.log[:-2]
            renpy.take_screenshot()
            renpy.save("zz_p0b_place")
            check(renpy.can_load("zz_p0b_place"), "a save made on the place view is written")
            ZZ_SAVE[0] = 2
            renpy.load("zz_p0b_place")
    python:
        zz_render(0.4)
        check(ZZ_SAVE[0] == 2 and renpy.get_screen("sb_place") is not None and here == "cafeteria" and period == "Noon"
              and zz_buttons("sb_place") >= 3,
              "…and it reloads onto the place view (nothing un-picklable was added)", (ZZ_SAVE[0], here, period))
        shot("place_reloaded", wait=0)
        renpy.hide_screen("sb_place")
        zz_hot_drop("zz_save_spot")
        zz_p0_fixture("rich")
        toast_clear()

    $ finish()
