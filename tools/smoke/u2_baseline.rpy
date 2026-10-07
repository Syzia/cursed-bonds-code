## tools/smoke/u2_baseline.rpy -- the second UI overhaul's baselines: what the
## game answered, and looked like, before the overhaul changed anything
## (docs/UI2_DESIGN.md 10.2, U0a step 4; written by U0a).
##
##   tools/smoke.sh u2_baseline            compare this tree with the baselines
##   U2_BASELINE_WRITE=1 tools/smoke.sh u2_baseline
##                                         write them afresh into
##                                         $SMOKE_SHOTS/baseline/ (U0a did this
##                                         once, on commit d2eb9db, and copied
##                                         the files into tools/smoke/; nobody
##                                         else replaces them, except U0c2 the
##                                         one entry named below)
##
## smoke-pointer
## (It parks the pointer away from every button before each screenshot, so a
## button under a pointer left anywhere is not drawn lit; it takes its turn
## with the other pointer harnesses.)
##
## This is a tool, not a member of any package's standard set: from U0b on,
## parts of it differ ON PURPOSE, and each check below says which part it is.
## A package reads the part it promised to keep.
##
## The baselines (tools/smoke/):
##
##   baseline_u2.json
##       fixture    the state everything below was read in (zz_b_fixture)
##       where      {weekday: {period: {who: place or null}}} for a whole week
##                  (days 8 to 14, Mon to Sun), char_location for the eleven
##       here       {weekday: {period: {place: [who]}}}, who_is_here
##       actions    {"Tue" / "Sat": {period: {place: [[id, label, hint, cost]]}}},
##                  place_actions(place) with me standing there
##       rail       the same shape, the ids rail_actions(place) leaves in the
##                  icon column
##       exits      {place: [[to, x, y]]}, path_exits (the point the game draws)
##       links, hubs   PATH_LINKS, PATH_HUBS
##   baseline_story_names.json
##       {file: {statement name: [kind, line, hash of diff_info()]}} for every
##       node of the frozen story files and of U9's files (docs/UI2_DESIGN.md
##       2.1, 8.1): sb_loop, sb_tokyo, sb_missions, sb_events, sb_hooks,
##       explore, script, sb_combat, jjk_screens, sb_threads, and every ch*,
##       story_*, missions_* and events_* file. NOT sb_night.rpy: U0c2 adds
##       that file's entry as its last step, after its own edits (8.1).
##   baseline_night_names_u0a.json
##       the same for sb_night.rpy as it was before U0c2, for U0c2 to check
##       itself against (every node outside the init blocks keeps its name).
##   baseline_sprite_tree.txt
##       the text of what lit_sprite builds for Yuji (K9), with and without
##       the blink and talk pictures, and the hash of its pickle
##   baseline_shots/ui2/
##       place.png, person.png, map_campus.png, map_area.png, main_menu.png
##       and shots.json (the window's size and each file's sha256)
##
## A statement's name is what a save rests on. Ren'Py gives a node of a
## changed file its old name when its diff_info() is unchanged
## (renpy/script.py, merge_names), so "every baseline name still exists with
## the same diff_info()" is the test that no save lost its place. The names
## are the owner's: tools/smoke.sh copies the owner's .rpyc into the scratch
## copy, and so must any tree this runs in (a worktree gets `cp -p` copies).

init 999 python:
    import builtins
    import hashlib
    import json
    import os

    ZZ_B_WRITE = os.environ.get("U2_BASELINE_WRITE") == "1"
    ZZ_B_FLAGS = ("dinner_listened", "chose_jujutsu", "enrolled", "roll_call", "storehouse_access",
                  "sunmall_done", "armory_open", "mission_board_open", "utahime_arrived",
                  "intensive_done", "ijichi_rides")
    ZZ_B_FROZEN = ("sb_loop.rpy", "sb_tokyo.rpy", "sb_missions.rpy", "sb_events.rpy", "sb_hooks.rpy",
                   "explore.rpy", "script.rpy", "sb_combat.rpy", "jjk_screens.rpy", "sb_threads.rpy")
    ZZ_B_STORY = ("ch", "story_", "missions_", "events_")
    ZZ_B_NIGHT = "sb_night.rpy"
    ZZ_B_SHOTS = ("place", "person", "map_campus", "map_area", "main_menu")
    ZZ_B_WHO = "megumi"
    ZZ_B_ROOM = "classroom"
    ZZ_B_AREA = "school"
    ## Where the pointer waits while a picture is taken: the top of the
    ## screen's middle, where no screen of the five has a button.
    ZZ_B_PARK = (960, 150)

    def zz_b_fixture(day=9, period="Morning", here="dorm"):
        """A settled game with the whole campus open and everyone met: the
        state every baseline is read in."""
        settle(mc_name="Tester", mc_surname="Harness", day=day, period=period, here=here, yen=40000)
        for w in ROSTER_ORDER:
            if w not in store.roster:
                store.roster.append(w)
            store.bonds[w] = 60
        for f in ZZ_B_FLAGS:
            flag(f)
        store.done_events.add("st_roll_call")
        promote("mc", "g3", quiet=True)
        store.schedule_overrides = {}
        store.actions_today = set()
        store.companion = None
        store.explore_mode = False
        roll_gojo()
        refresh_vitals()
        mission_cache_clear()
        toast_clear()

    def zz_b_at(day, period, here=None):
        store.day = day
        store.period = period
        if here is not None:
            store.here = here
        store.actions_today = set()
        roll_gojo()

    def zz_b_plain(v):
        if isinstance(v, (builtins.dict, dict)):
            return builtins.dict((builtins.str(k), zz_b_plain(x)) for k, x in v.items())
        if isinstance(v, (builtins.list, builtins.tuple, list, tuple)):
            return [zz_b_plain(x) for x in v]
        return v

    def zz_b_world():
        """baseline_u2.json."""
        zz_b_fixture()
        out = builtins.dict(fixture=builtins.dict(
            flags=builtins.list(ZZ_B_FLAGS), roster=builtins.list(ROSTER_ORDER), bond=60, grade="g3",
            days="8 to 14 (Mon to Sun); actions on day 9 (Tue) and day 13 (Sat)"))
        where, here = builtins.dict(), builtins.dict()
        for day in range(8, 15):
            zz_b_at(day, "Morning", "dorm")
            wd = weekday()
            where[wd], here[wd] = builtins.dict(), builtins.dict()
            for per in PERIODS:
                store.period = per
                where[wd][per] = builtins.dict((w, char_location(w, per)) for w in ROSTER_ORDER)
                here[wd][per] = builtins.dict((l, builtins.list(who_is_here(l, per))) for l in LOC_ORDER)
        out["where"], out["here"] = where, here
        acts, rail = builtins.dict(), builtins.dict()
        for day in (9, 13):
            zz_b_at(day, "Morning", "dorm")
            wd = weekday()
            acts[wd], rail[wd] = builtins.dict(), builtins.dict()
            for per in PERIODS:
                acts[wd][per], rail[wd][per] = builtins.dict(), builtins.dict()
                for l in LOC_ORDER:
                    zz_b_at(day, per, l)
                    acts[wd][per][l] = [[a[0], builtins.str(a[1]), builtins.str(a[2]), a[3]] for a in place_actions(l)]
                    rail[wd][per][l] = [a[0] for a in rail_actions(l)]
        out["actions"], out["rail"] = acts, rail
        zz_b_at(9, "Noon", "dorm")
        out["exits"] = builtins.dict((l, [[r["to"], r["x"], r["y"]] for r in path_exits(l)]) for l in LOC_ORDER)
        out["links"] = zz_b_plain(PATH_LINKS)
        out["hubs"] = zz_b_plain(PATH_HUBS)
        return out

    def zz_b_names(files):
        """{file: {name: [kind, line, hash]}} for every node of `files`."""
        want = builtins.set("game/" + f for f in files)
        out = builtins.dict(("game/" + f, builtins.dict()) for f in files)
        seen = builtins.set()
        for node in renpy.game.script.namemap.values():
            fn = getattr(node, "filename", None)
            key = getattr(node, "name", None)
            if fn not in want or id(node) in seen or not isinstance(key, (builtins.str, builtins.tuple)):
                continue
            seen.add(id(node))
            try:
                info = node.diff_info()
            except Exception as e:
                info = ("<no diff_info>", repr(e))
            info = (type(node).__name__,) + builtins.tuple(info[1:])
            h = hashlib.sha1(repr(info).encode("utf-8")).hexdigest()[:16]
            out[fn][json.dumps(key)] = [type(node).__name__, node.linenumber, h]
        return out

    def zz_b_story_files():
        game = config.gamedir
        out = [f for f in os.listdir(game) if f.endswith(".rpy") and f.startswith(ZZ_B_STORY)]
        out += [f for f in ZZ_B_FROZEN if os.path.isfile(os.path.join(game, f))]
        return builtins.sorted(builtins.set(f for f in out if f != ZZ_B_NIGHT))

    ## The saved sprite (K9) -------------------------------------------------------

    def zz_b_tree(d, depth, out):
        pad = "  " * depth
        cls = type(d).__name__
        if isinstance(d, renpy.display.transform.Transform):
            fn = d.function
            if fn is None:
                what = ""
            elif type(fn).__name__ in ("Curry", "Partial"):
                inner = getattr(fn, "callable", None) or getattr(fn, "func", None)
                what = " function=%s curried(%s)" % (getattr(inner, "__name__", "?"),
                                                     ", ".join(builtins.sorted(getattr(fn, "kwargs", None) or getattr(fn, "keywords", None) or ())))
            else:
                what = " function=" + fn.__name__
            out.append("%s%s%s" % (pad, cls, what))
            if d.child is not None:
                zz_b_tree(d.child, depth + 1, out)
        elif isinstance(d, renpy.display.im.Image):
            out.append("%s%s %s" % (pad, cls, d.filename))
        elif isinstance(d, renpy.display.image.ImageReference):
            out.append("%s%s %s" % (pad, cls, " ".join(d.name) if isinstance(d.name, builtins.tuple) else d.name))
        elif hasattr(d, "children"):
            out.append("%s%s (%d children)" % (pad, cls, len(d.children)))
            for c in d.children:
                zz_b_tree(c, depth + 1, out)
        else:
            out.append("%s%s" % (pad, cls))
        return out

    def zz_b_sprite():
        """baseline_sprite_tree.txt: the tree for Yuji's neutral sprite and
        the hash of its pickle, with the blink and talk pictures taken away
        and with them said to be there (whatever is installed today)."""
        real = renpy.loadable
        path, size, feet = "images/char/yuji_neutral.png", (760, 1400), (383, 1365, 330)
        lines = ["# lit_sprite(%r, %r, %r)" % (path, size, feet),
                 "# each node: its class, its function's name, its curried argument names, its file",
                 "# (docs/UI2_DESIGN.md K9; written by tools/smoke/u2_baseline.rpy)"]
        for label, fx in (("without the blink and talk pictures", False), ("with the blink and talk pictures", True)):
            def zz_fake(name, *a, **k):
                if builtins.str(name).startswith("images/char/fx/"):
                    return fx
                return real(name, *a, **k)
            renpy.loadable = zz_fake
            try:
                d = lit_sprite(path, size, feet)
                d2 = lit_sprite(path, size, feet)
            finally:
                renpy.loadable = real
            lines.append("")
            lines.append("## " + label)
            zz_b_tree(d, 0, lines)
            p1, p2 = renpy.compat.pickle.dumps(d), renpy.compat.pickle.dumps(d2)
            lines.append("pickle: %d bytes, sha256 %s%s" % (
                len(p1), hashlib.sha256(p1).hexdigest(), "" if p1 == p2 else " (NOT the same when built twice)"))
        return "\n".join(lines) + "\n"

    ## The five pictures ----------------------------------------------------------

    def zz_b_park():
        """The pointer away from every button, and nothing focused."""
        try:
            renpy.set_mouse_pos(ZZ_B_PARK[0], ZZ_B_PARK[1])
        except Exception as e:
            note("park", "set_mouse_pos failed: %r" % (e,))
        zz_render(0.3)

    def zz_b_quiet():
        toast_clear()
        renpy.hide_screen("objective_toast")
        zz_b_park()

    def zz_b_load(name):
        """A committed baseline (tools/smoke/<name>) of the tree this run was
        started from, or None."""
        p = os.path.join(smoke_env("SMOKE_ROOT") or "", "tools", "smoke", name)
        if not os.path.isfile(p):
            return None
        with open(p, encoding="utf-8") as f:
            return f.read() if name.endswith(".txt") else json.load(f)

    def zz_b_png_size(path):
        """[width, height] of a PNG, in pixels (a screenshot is as large as
        the window is on this screen)."""
        import struct
        with open(path, "rb") as f:
            head = f.read(24)
        return builtins.list(struct.unpack(">II", head[16:24]))

    def zz_b_sha(path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()


label zz_smoke:
    python:
        renpy.random.seed(20261007)
        _zz_motion0 = persistent.motion
        persistent.motion = False          ## nothing breathes, blinks or pulses in a picture
        _zz_dir = os.path.join(zz_smoke_state.shots, "baseline")
        if not os.path.isdir(_zz_dir):
            os.makedirs(_zz_dir)

        ## --- the data ------------------------------------------------------------------------
        _zz_world = zz_b_world()
        _zz_story = zz_b_names(zz_b_story_files())
        _zz_night = zz_b_names([ZZ_B_NIGHT])
        _zz_sprite = zz_b_sprite()
        check(zz_b_world() == _zz_world, "the world's answers are the same when read twice")
        check(zz_b_sprite() == _zz_sprite and "NOT the same" not in _zz_sprite,
              "lit_sprite's tree and its pickle are the same when built twice")
        _zz_n = sum(len(v) for v in _zz_story.values())
        check(_zz_n > 1000 and all(_zz_story.values()) and len(_zz_night["game/" + ZZ_B_NIGHT]) > 50,
              "statement names: %d nodes in %d story files, %d in sb_night.rpy"
              % (_zz_n, len(_zz_story), len(_zz_night["game/" + ZZ_B_NIGHT])))
        for _zz_name, _zz_data in (("baseline_u2.json", _zz_world), ("baseline_story_names.json", _zz_story),
                                   ("baseline_night_names_u0a.json", _zz_night)):
            with open(os.path.join(_zz_dir, _zz_name), "w", encoding="utf-8") as _zz_f:
                json.dump(_zz_data, _zz_f, indent=None if "names" in _zz_name else 1, sort_keys=True,
                          ensure_ascii=False, separators=(",", ":") if "names" in _zz_name else (",", ": "))
                _zz_f.write("\n")
        with open(os.path.join(_zz_dir, "baseline_sprite_tree.txt"), "w", encoding="utf-8") as _zz_f:
            _zz_f.write(_zz_sprite)

    ## --- the pictures ---------------------------------------------------------------------
    python:
        _zz_shots = os.path.join(_zz_dir, "ui2")
        if not os.path.isdir(_zz_shots):
            os.makedirs(_zz_shots)
        _zz_keep = zz_smoke_state.shots
        zz_smoke_state.shots = _zz_shots
        zz_b_fixture(day=9, period="Morning", here=ZZ_B_ROOM)
        check(ZZ_B_WHO in who_is_here(ZZ_B_ROOM), "(fixture) %s is in the %s on a weekday Morning" % (ZZ_B_WHO, ZZ_B_ROOM), who_is_here(ZZ_B_ROOM))
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        view_sync_light()
        arrival_caption()
        ARRIVAL[1] -= 10
        renpy.show_screen("sb_place")
        zz_render(1.2)
        zz_b_quiet()
        shot("place", wait=0.4)
        renpy.hide_screen("sb_place")

        view_before_person(ZZ_B_WHO)
        renpy.show_screen("sb_char", ZZ_B_WHO)
        zz_render(1.8)
        zz_b_quiet()
        shot("person", wait=0.4)
        renpy.hide_screen("sb_char")

        renpy.show_screen("sb_map")
        zz_render(1.5)
        zz_b_quiet()
        shot("map_campus", wait=0.4)
        renpy.hide_screen("sb_map")
        zz_render(0.2)
        renpy.show_screen("sb_map", area=ZZ_B_AREA)
        zz_render(2.0)
        zz_b_quiet()
        shot("map_area", wait=0.4)
        renpy.hide_screen("sb_map")

        renpy.scene()
        renpy.show_screen("main_menu")
        zz_render(1.2)
        zz_b_quiet()
        shot("main_menu", wait=0.4)
        renpy.hide_screen("main_menu")
        zz_smoke_state.shots = _zz_keep

        _zz_meta = builtins.dict(
            size=zz_b_png_size(os.path.join(_zz_shots, ZZ_B_SHOTS[0] + ".png")),
            fixture="day 9 (Tue), Morning, the %s with %s in it; the map opened from there, then its %s area; "
                    "persistent.motion off; the pointer parked at %r" % (ZZ_B_ROOM, ZZ_B_WHO, ZZ_B_AREA, ZZ_B_PARK),
            sha256=builtins.dict((n, zz_b_sha(os.path.join(_zz_shots, n + ".png"))) for n in ZZ_B_SHOTS
                                 if os.path.isfile(os.path.join(_zz_shots, n + ".png"))))
        check(len(_zz_meta["sha256"]) == len(ZZ_B_SHOTS), "the five pictures are taken", builtins.sorted(_zz_meta["sha256"]))
        with open(os.path.join(_zz_shots, "shots.json"), "w", encoding="utf-8") as _zz_f:
            json.dump(_zz_meta, _zz_f, indent=1, sort_keys=True)
            _zz_f.write("\n")
        persistent.motion = _zz_motion0

    ## --- compare --------------------------------------------------------------------------
    python:
        if ZZ_B_WRITE:
            note("written", "the baselines are in %s; nothing was compared" % _zz_dir)
        else:
            _zz_old = zz_b_load("baseline_u2.json")
            if check(_zz_old is not None, "tools/smoke/baseline_u2.json is there"):
                _zz_new = json.loads(json.dumps(_zz_world))
                for _zz_k, _zz_say in (("where", "who is where, for the eleven, every hour of a week"),
                                       ("here", "who is in each place, every hour of a week"),
                                       ("exits", "every place's exits and where they are drawn"),
                                       ("links", "PATH_LINKS"), ("hubs", "PATH_HUBS"),
                                       ("rail", "what the icon column offers, place by place")):
                    _zz_diff = []
                    if _zz_old.get(_zz_k) != _zz_new.get(_zz_k):
                        _zz_a, _zz_b2 = json.dumps(_zz_old.get(_zz_k), sort_keys=True), json.dumps(_zz_new.get(_zz_k), sort_keys=True)
                        _zz_diff = ["%d chars then, %d now" % (len(_zz_a), len(_zz_b2))]
                        if isinstance(_zz_old.get(_zz_k), builtins.dict) and isinstance(_zz_new.get(_zz_k), builtins.dict):
                            _zz_diff += builtins.sorted(k for k in builtins.set(_zz_old[_zz_k]) | builtins.set(_zz_new[_zz_k])
                                                        if _zz_old[_zz_k].get(k) != _zz_new[_zz_k].get(k))[:12]
                    check(not _zz_diff, "baseline: %s (%s)" % (_zz_say, _zz_k), _zz_diff)
                ## place_actions: whole, and for the places the baseline has
                ## with the exits (path_*) left out, which is what U0c2 keeps.
                _zz_bad, _zz_bad2 = [], []
                for _zz_wd in _zz_old["actions"]:
                    for _zz_p in _zz_old["actions"][_zz_wd]:
                        for _zz_l, _zz_rows in _zz_old["actions"][_zz_wd][_zz_p].items():
                            _zz_got = _zz_new["actions"].get(_zz_wd, {}).get(_zz_p, {}).get(_zz_l)
                            if _zz_got != _zz_rows:
                                _zz_bad.append("%s %s %s" % (_zz_wd, _zz_p, _zz_l))
                            if ([r for r in (_zz_got or []) if not r[0].startswith("path_")]
                                    != [r for r in _zz_rows if not r[0].startswith("path_")]):
                                _zz_bad2.append("%s %s %s" % (_zz_wd, _zz_p, _zz_l))
                check(not _zz_bad, "baseline: place_actions for every place and period", _zz_bad[:8])
                check(not _zz_bad2, "baseline: place_actions for the %d places of the baseline, apart from exits"
                      % len(_zz_old["exits"]), _zz_bad2[:8])
            for _zz_name, _zz_now in (("baseline_story_names.json", _zz_story), ("baseline_night_names_u0a.json", _zz_night)):
                _zz_old = zz_b_load(_zz_name)
                if not check(_zz_old is not None, "tools/smoke/%s is there" % _zz_name):
                    continue
                for _zz_fn in builtins.sorted(_zz_old):
                    _zz_have = _zz_now.get(_zz_fn)
                    if _zz_have is None:
                        ## An entry another package wrote (U0c2's, for sb_night.rpy).
                        _zz_have = zz_b_names([_zz_fn[len("game/"):]])[_zz_fn]
                    _zz_gone = [k for k in _zz_old[_zz_fn] if k not in _zz_have]
                    _zz_moved = [k for k in _zz_old[_zz_fn] if k in _zz_have
                                 and (_zz_old[_zz_fn][k][0], _zz_old[_zz_fn][k][2]) != (_zz_have[k][0], _zz_have[k][2])]
                    _zz_added = [k for k in _zz_have if k not in _zz_old[_zz_fn]]
                    check(not _zz_gone and not _zz_moved,
                          "names: every statement of %s keeps its name and its identity (%d; %d new)"
                          % (_zz_fn, len(_zz_old[_zz_fn]), len(_zz_added)),
                          "gone: %r · changed: %r" % (
                              [(k, _zz_old[_zz_fn][k][:2]) for k in _zz_gone[:5]],
                              [(k, _zz_old[_zz_fn][k][:2]) for k in _zz_moved[:5]]))
                    if _zz_added:
                        note("new names in " + _zz_fn, [(k, _zz_have[k][:2]) for k in _zz_added[:8]])
            _zz_old = zz_b_load("baseline_sprite_tree.txt")
            if check(_zz_old is not None, "tools/smoke/baseline_sprite_tree.txt is there"):
                _zz_t0 = [l for l in _zz_old.splitlines() if not l.startswith("pickle:")]
                _zz_t1 = [l for l in _zz_sprite.splitlines() if not l.startswith("pickle:")]
                check(_zz_t0 == _zz_t1, "K9: lit_sprite builds the tree it built (class, function, curried names, file)",
                      [(a, b) for a, b in zip(_zz_t0, _zz_t1) if a != b][:4])
                check(_zz_old == _zz_sprite, "K9: and its pickle is byte for byte what it was",
                      [l for l in _zz_sprite.splitlines() if l.startswith("pickle:")])
            _zz_old = zz_b_load(os.path.join("baseline_shots", "ui2", "shots.json"))
            if check(_zz_old is not None, "tools/smoke/baseline_shots/ui2/shots.json is there"):
                if _zz_old.get("size") != _zz_meta["size"]:
                    note("pictures", "the window is %r now and was %r: the pictures cannot be compared byte for byte"
                         % (_zz_meta["size"], _zz_old.get("size")))
                for _zz_n in ZZ_B_SHOTS:
                    check(_zz_old["sha256"].get(_zz_n) == _zz_meta["sha256"].get(_zz_n),
                          "picture: %s.png is pixel for pixel the baseline's" % _zz_n,
                          "compare %s with tools/smoke/baseline_shots/ui2/%s.png" % (os.path.join(_zz_shots, _zz_n + ".png"), _zz_n))
        finish()
