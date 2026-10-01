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
##        sb_char         equal
##        person_choices  equal on the seven fields the baseline has (a new
##                        key on a choice, such as `icon`, is a NOTE)
##        screenshots     pixel-identical
##   2. The measuring helpers of _lib.rpy, on a small screen of this file.
##   3. fixture(): an unknown name fails, a shaped variable is refused (R5).
##   4. tools/none_ok.txt: every example returns None in a settled fixture, and
##      every DEV_FUNCS key through dev_action(key), each in a fresh one (R4).

init 999 python:
    import builtins
    import copy
    import json
    import os
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
            for key in builtins.sorted(b["person_choices"]):
                old = b["choice_lists"][b["person_choices"][key]]
                i = n["person_choices"].get(key)
                new = n["choice_lists"][i] if i is not None else None
                if new != old:
                    bad.append((key, old, new))
            check(not bad, "baseline %s: person_choices is unchanged (%d person x room x period)"
                  % (kind, len(b["person_choices"])), bad[:3])
            if n["choice_keys"] != b["choice_keys"]:
                note("baseline %s: person_choices keys added" % kind,
                     builtins.sorted(set(n["choice_keys"]) - set(b["choice_keys"])))
        check(now["sb_char"] == base["sb_char"], "baseline: sb_char returns the same tuples for every person",
              [(w, now["sb_char"].get(w), base["sb_char"][w]) for w in base["sb_char"]
               if now["sb_char"].get(w) != base["sb_char"][w]][:3])
        check(now["shots"] == base["shots"], "baseline: the two screenshots show the same fixture",
              (now["shots"], base["shots"]))

    ZZ_P0_BOOT = builtins.list([None])
    ZZ_P0_NOW = builtins.dict()


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
            for _zz_n in ("place", "person"):
                _zz_ok, _zz_why = zz_png_same(os.path.join(zz_smoke_state.shots, "p0_%s.png" % _zz_n),
                                              os.path.join(_zz_base_dir, "baseline_shots", "%s.png" % _zz_n))
                check(_zz_ok, "baseline: the %s view is pixel-identical to baseline_shots/%s.png" % (_zz_n, _zz_n), _zz_why)

    $ finish()
