## tools/smoke/u2_dump.rpy -- the game's layout numbers, in one file for the
## art tools (docs/UI2_DESIGN.md 5.4, D47; written by U0a).
##
##   tools/smoke.sh u2_dump                                    in the owner's folder:
##                                                             rewrites the committed
##                                                             tools/art/game_layout.json
##   tools/smoke.sh u2_dump --out shots/art/game_layout.json   in a worktree: a local
##                                                             copy, never committed
##
## smoke-out: game_layout.json -> tools/art/game_layout.json
##
## Every art tool reads the game's numbers from this file and from nothing
## else: no tool parses a .rpy table any more. It does not need the pointer
## and may run beside other harnesses.
##
## What the file holds (docs/UI2_CONTRACTS.md has the shape, key by key):
##
##   format        1
##   hash          sha256 over the files the numbers were read from: every
##                 game/*.rpy (a harness's own zz_* and aa_zz_* files left
##                 out) and every game/layout/*.json, in name order; for each,
##                 its path from game/, a NUL, the sha256 of its bytes, a
##                 newline. zz_dump_hash() below is the reference. A tool
##                 that finds the hash out of date refuses with one line:
##                 "the game's layout has changed since the dump was written:
##                 run tools/smoke.sh u2_dump".
##   files         the names the hash covers
##   screen        [1920, 1080]
##   places        in LOC_ORDER: key, name, indoor, bg (the image name), file
##                 (the day picture's path under game/), variants ({period:
##                 attribute}, TIME_VARIANT), area, hub (is it its area's hub),
##                 zoom and y (PLACE_STAGING, or the defaults)
##   exits         {place: [ {to, id, default: [x, y], applied: [x, y]} ]} in
##                 the order path_exits() gives them. `default` is the code's
##                 row (PATH_EXITS); `applied` is what the game draws (the
##                 sidecar hot_<place>.json laid over it).
##   hotspots      {place: [ {id, kind, act, icon, default, applied, front,
##                 standalone, when} ]}: every registered hotspot that is not
##                 an exit, the same two points
##   spot_planned  SPOT_PLANNED as [[id, place, kind]]; [] until the scaffold
##                 (U0c) defines it
##   slots         {place: {"1" to "4": [[x centre, y offset, zoom, far]]}}:
##                 what view_slots() answers at Noon (the sidecar first)
##   slots_code    VIEW_SLOTS, the code's own rows, for the rooms that have any
##   poses         {place: {key: [x, y, w, h]}}: the pose boxes the sidecars hold
##   areas         in AREAS order: key, name, places, hub, anchor, bg, and
##                 spots {place: {default, applied}}
##   frames        hot_bounds (x0, y0, x1, y1 a hotspot or exit must sit in),
##                 hot_size, hot_lanes (the toast lane, the banner lane; each
##                 x, y, w, h), caption_box (the arrival caption's panel),
##                 path_apart, path_clear, keep_clear (PATH_KEEP_CLEAR),
##                 map_pin_frame, map_mountain_box, map_pin (w), map_area (w,
##                 h), stage_x (40 to 1700), sprite (the canvas, 760 x 1400),
##                 tag_y, rail (the icon column's numbers)
##   people        {who: {file, canvas: [w, h], feet: [x centre, sole row,
##                 width]}}: each person's neutral sprite as lit_sprite is
##                 given it (game/jjk_sprites.rpy)
##   grade         outdoor, indoor: {period: [tint, brightness]}
##   light         neutral, outdoor, indoor ({period: row}), place ({"<place>"
##                 or "<place> <variant>": row}), bg ({image name: row})
##   schedule      SCHEDULE; weekend: WEEKEND; periods; weekdays
##   fg_rooms      VIEW_FG_ROOMS; fg_talk: VIEW_FG_TALK
##
## Keys the tree does not have yet are written empty and filled when U0c
## regenerates the file. Nothing in it depends on the day, the hour, a flag or
## the clock: two runs on one tree give the same bytes.

init 999 python:
    import builtins
    import hashlib
    import json
    import os
    import re

    def zz_dump_files():
        """The files the hash covers, as paths from game/, in name order."""
        game = config.gamedir
        out = [f for f in os.listdir(game)
               if f.endswith(".rpy") and not f.startswith("zz_") and not f.startswith("aa_zz_")]
        lay = os.path.join(game, "layout")
        if os.path.isdir(lay):
            out += ["layout/" + f for f in os.listdir(lay) if f.endswith(".json")]
        return builtins.sorted(out)

    def zz_dump_hash(files=None):
        h = hashlib.sha256()
        for rel in (files if files is not None else zz_dump_files()):
            with open(os.path.join(config.gamedir, rel), "rb") as f:
                one = hashlib.sha256(f.read()).hexdigest()
            h.update(rel.encode("utf-8") + b"\0" + one.encode("ascii") + b"\n")
        return h.hexdigest()

    def zz_dump_plain(v):
        """Tuples and sets as lists, all the way down, so json can hold it."""
        if isinstance(v, (builtins.dict, dict)):
            return builtins.dict((builtins.str(k), zz_dump_plain(x)) for k, x in v.items())
        if isinstance(v, (builtins.set, builtins.frozenset, set, frozenset)):
            return [zz_dump_plain(x) for x in builtins.sorted(v)]
        if isinstance(v, (builtins.list, builtins.tuple, list, tuple)):
            return [zz_dump_plain(x) for x in v]
        return v

    def zz_dump_people():
        out = builtins.dict()
        rx = re.compile(r'^image (\w+) = (?:ConditionSwitch\(.*"True", )?lit_sprite\("([^"]+)", \((\d+), (\d+)\), \((\d+), (\d+), (\d+)\)\)')
        path = os.path.join(config.gamedir, "jjk_sprites.rpy")
        if not os.path.isfile(path):
            return out
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = rx.match(line)
                if m:
                    out[m.group(1)] = builtins.dict(
                        file=m.group(2), canvas=[int(m.group(3)), int(m.group(4))],
                        feet=[int(m.group(5)), int(m.group(6)), int(m.group(7))])
        return out

    def zz_dump_build():
        S = store
        files = zz_dump_files()
        d = builtins.dict(format=1, hash=zz_dump_hash(files), files=files,
                          screen=[config.screen_width, config.screen_height])

        staging = getattr(S, "PLACE_STAGING", {})
        places = []
        for loc in LOC_ORDER:
            info = LOCATIONS[loc]
            bg = info["bg"]
            stem = bg[3:] if bg.startswith("bg ") else bg
            places.append(builtins.dict(
                key=loc, name=info["name"], indoor=bool(info["indoor"]), bg=bg,
                file="images/bg/%s.png" % stem.replace(" ", "_"),
                variants=zz_dump_plain(TIME_VARIANT.get(loc, {})),
                area=area_of(loc), hub=bool(path_is_hub(loc)),
                zoom=staging.get(loc, {}).get("zoom", 0.52), y=staging.get(loc, {}).get("y", 0)))
        d["places"] = places

        exits = builtins.dict()
        exit_ids = builtins.set()
        for loc in LOC_ORDER:
            rows = []
            applied = builtins.dict((r["to"], (r["x"], r["y"])) for r in path_exits(loc))
            for to, x, y in PATH_EXITS.get(loc, ()):
                hid = path_spot_id(loc, to)
                exit_ids.add(hid)
                rows.append(builtins.dict(to=to, id=hid, default=[int(x), int(y)],
                                          applied=[int(applied[to][0]), int(applied[to][1])]))
            exits[loc] = rows
        d["exits"] = exits

        hots = builtins.dict()
        seen = builtins.set()
        for h in HOT_SPOTS:
            if h["id"] in exit_ids or h["id"] in seen:
                continue
            seen.add(h["id"])
            side = rule_layout("hot_" + builtins.str(h["place"])).get("spots") or {}
            p = side.get(h["id"]) if isinstance(side, builtins.dict) else None
            ok = (isinstance(p, (builtins.list, builtins.tuple)) and len(p) == 2
                  and hot_number(p[0]) and hot_number(p[1]))
            hots.setdefault(h["place"], []).append(builtins.dict(
                id=h["id"], kind=h["kind"], act=h["act"], icon=builtins.dict.__getitem__(h, "icon"),
                default=[int(h["x"]), int(h["y"])],
                applied=[int(p[0]), int(p[1])] if ok else [int(h["x"]), int(h["y"])],
                front=bool(h["front"]), standalone=bool(h["standalone"]), when=h["when"]))
        d["hotspots"] = hots
        d["spot_planned"] = zz_dump_plain(getattr(S, "SPOT_PLANNED", []))

        ## Slots as the game answers them by day, with every picture in place.
        per0, here0 = S.period, S.here
        S.period = "Noon"
        try:
            d["slots"] = builtins.dict(
                (loc, builtins.dict((builtins.str(n), zz_dump_plain(view_slots(loc, n))) for n in (1, 2, 3, 4)))
                for loc in LOC_ORDER)
        finally:
            S.period, S.here = per0, here0
        d["slots_code"] = builtins.dict(
            (loc, builtins.dict((builtins.str(n), zz_dump_plain(rows)) for n, rows in table.items()))
            for loc, table in VIEW_SLOTS.items())
        poses = builtins.dict()
        for loc in LOC_ORDER:
            got = builtins.dict()
            for name in ("view_" + loc, "pose_" + loc):       ## the pose_ file wins (3.2)
                box = rule_layout(name).get("poses")
                if isinstance(box, builtins.dict):
                    got.update(box)
            if got:
                poses[loc] = zz_dump_plain(got)
        d["poses"] = poses

        areas = []
        for a in AREAS:
            applied = map_spots(a["key"])
            areas.append(builtins.dict(
                key=a["key"], name=a["name"], places=builtins.list(a["places"]), hub=path_hub(a["key"]),
                anchor=zz_dump_plain(a["anchor"]), bg=a["bg"],
                spots=builtins.dict((l, builtins.dict(default=zz_dump_plain(p),
                                                      applied=zz_dump_plain(applied.get(l, p))))
                                    for l, p in a["spots"].items())))
        d["areas"] = areas

        d["frames"] = zz_dump_plain(builtins.dict(
            hot_bounds=HOT_BOUNDS, hot_size=HOT_SIZE, hot_lanes=HOT_LANES,
            caption_box=PATH_CAPTION_BOX, path_apart=PATH_APART, path_clear=PATH_CLEAR,
            keep_clear=PATH_KEEP_CLEAR,
            map_pin_frame=MAP_PIN_FRAME, map_mountain_box=MAP_MOUNTAIN_BOX,
            map_pin=MAP_PIN_W, map_area=[MAP_AREA_W, MAP_AREA_H],
            stage_x=[40, 1700], sprite=VIEW_SPRITE, tag_y=VIEW_TAG_Y,
            rail=builtins.dict(tile=RAIL_TILE, gap=RAIL_GAP, bottom=RAIL_BOTTOM, top=RAIL_TOP,
                               top_inner=RAIL_TOP_INNER, max=RAIL_MAX, columns=RAIL_COLUMNS)))

        d["people"] = zz_dump_people()
        d["grade"] = zz_dump_plain(builtins.dict(outdoor=OUTDOOR_GRADE, indoor=INDOOR_GRADE))
        d["light"] = zz_dump_plain(builtins.dict(
            neutral=NEUTRAL_LIGHT, outdoor=OUTDOOR_LIGHT, indoor=INDOOR_LIGHT,
            place=builtins.dict(((k[0] if k[1] is None else "%s %s" % k), v) for k, v in PLACE_LIGHT.items()),
            bg=BG_LIGHT))
        d["schedule"] = zz_dump_plain(SCHEDULE)
        d["weekend"] = zz_dump_plain(WEEKEND)
        d["periods"] = builtins.list(PERIODS)
        d["weekdays"] = builtins.list(WEEKDAYS)
        d["fg_rooms"] = builtins.list(VIEW_FG_ROOMS)
        d["fg_talk"] = builtins.list(VIEW_FG_TALK)
        return d


label zz_smoke:
    python:
        settle()
        _zz_d = zz_dump_build()
        _zz_text = json.dumps(_zz_d, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        _zz_again = json.dumps(zz_dump_build(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        check(_zz_text == _zz_again, "the dump is the same when built twice")
        check(json.loads(_zz_text)["hash"] == zz_dump_hash() and len(_zz_d["hash"]) == 64,
              "the hash covers %d files (the .rpy files and game/layout/*.json)" % len(_zz_d["files"]))
        check([p["key"] for p in _zz_d["places"]] == builtins.list(LOC_ORDER) and len(_zz_d["places"]) == len(LOCATIONS),
              "every place is in it, in LOC_ORDER (%d)" % len(_zz_d["places"]))
        check(builtins.sorted(_zz_d["exits"]) == builtins.sorted(LOCATIONS)
              and all(_zz_d["exits"][l] for l in LOCATIONS)
              and all([r["to"] for r in _zz_d["exits"][l]] == path_neighbours(l) for l in LOCATIONS)
              and all(r["applied"] == [x["x"], x["y"]] for l in LOCATIONS for r, x in zip(_zz_d["exits"][l], path_exits(l))),
              "every place's exits are in it, in path_exits' order, with the point the game draws (%d exits)"
              % sum(len(v) for v in _zz_d["exits"].values()))
        _zz_n = sum(len(v) for v in _zz_d["hotspots"].values())
        _zz_live = builtins.dict((h["id"], (h["x"], h["y"])) for l in LOCATIONS for h in HOT_SPOTS if h["place"] == l)
        check(_zz_n == len([h for h in HOT_SPOTS if not builtins.str(h["id"]).startswith("go_")])
              and all(isinstance(r["applied"], builtins.list) and len(r["applied"]) == 2
                      for v in _zz_d["hotspots"].values() for r in v),
              "every registered hotspot that is not an exit is in it (%d)" % _zz_n)
        check(all(len(_zz_d["slots"][l][builtins.str(n)]) == n for l in LOCATIONS for n in (1, 2, 3, 4)),
              "one to four slots for every place")
        check(len(_zz_d["people"]) >= len(ROSTER_ORDER) and all(w in _zz_d["people"] for w in ROSTER_ORDER),
              "every person's sprite canvas and feet (%d images)" % len(_zz_d["people"]))
        check(isinstance(_zz_d["spot_planned"], builtins.list), "spot_planned is a list (%d rows; empty until the scaffold defines SPOT_PLANNED)"
              % len(_zz_d["spot_planned"]))
        _zz_path = os.path.join(zz_smoke_state.shots, "game_layout.json")
        with open(_zz_path, "w", encoding="utf-8") as _zz_f:
            _zz_f.write(_zz_text)
        check(os.path.isfile(_zz_path), "game_layout.json is written (%d bytes); tools/smoke.sh copies it to its place" % len(_zz_text.encode("utf-8")))
        note("hash", _zz_d["hash"])
        ## The committed copy, when this run was started from a tree that has one.
        _zz_root = smoke_env("SMOKE_ROOT")
        _zz_old = os.path.join(_zz_root, "tools", "art", "game_layout.json") if _zz_root else None
        if _zz_old and os.path.isfile(_zz_old):
            with open(_zz_old, encoding="utf-8") as _zz_f:
                _zz_was = _zz_f.read()
            note("the committed tools/art/game_layout.json", "the same" if _zz_was == _zz_text else
                 "differs from this run's (hash %s there)" % json.loads(_zz_was).get("hash", "?")[:12])
        else:
            note("the committed tools/art/game_layout.json", "not there yet")
        finish()
