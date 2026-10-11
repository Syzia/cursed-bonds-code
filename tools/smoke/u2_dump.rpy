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
## Added by the scaffold (U0c2); none of the keys above changed shape:
##   variants_planned  WORLD_VARIANTS as [[place, period, attribute, file]]:
##                 every planned new hour picture
##   keep_clear    {place: [[x, y]]}: path_keep_clear(place), the live points
##                 an exit keeps clear of (frames.keep_clear is the old table)
##   tips          {place: {id: side}}: the hover-label sides a hot_ sidecar gives
##   faces         {who: {eyes, mouth, blink_also}} as the game reads them
##                 (faces.json first, then the tables in view_stage.rpy)
##   world         inside, pinless, homes, asleep, away ({who: {"<weekday>
##                 <period>": district}}), door_bond and door_owners by place
##   standins      copies ({lender: file}), names ({image key: lender}),
##                 if_file ({image name: file}), people (the five stand-in names)
##   names_key     the key held to show names ("K_n")
## Added by the scaffold's second sitting (D60, "the picture is what is
## clicked"; game/sb_hotspots.rpy):
##   hot_shape     HOT_SHAPE: the limits both validators read (polys, points,
##                 area_min, area_max, buried_max, grid), the HUD's row
##                 (top: above that y no shape takes the pointer) and the
##                 light's default look (color, wash, edge, dim, names, blur,
##                 line). Whether a hotspot is in the front layer, which the
##                 layers' rule reads (hot_shape_layers), is the `front` of
##                 its row under hotspots.
##   hot_look      the look in force: HOT_SHAPE's, with what
##                 game/layout/hot_look.json replaces; look_keys: the keys
##                 that file may hold
##   shapes        {place: {id: [polygon, ...]}}: the "shapes" each hot_
##                 sidecar holds, as written, whatever the picture's revision
##                 (a room redone in place waits with its shapes traced)
##   keep_tile     {place: {id: reason}}: the few that keep a button
##   shaped        the places that are shaped now (hot_shapes_for answers)
##   name_rects    {place: {id: [x, y, w, h]}}: where the name plate of every
##                 registered hotspot and exit would be drawn in a shaped
##                 place while names are shown (hot_name_rect, at its applied
##                 point), so that a layout tool can refuse two that meet.
##                 Measured standing in each place in turn, so a place's own
##                 "tips" rows decide the side its plates lie on
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

        ## What the scaffold (U0c2) added. New keys only: none above changed shape.
        d["variants_planned"] = zz_dump_plain(WORLD_VARIANTS)
        d["keep_clear"] = builtins.dict((loc, zz_dump_plain(path_keep_clear(loc))) for loc in LOC_ORDER if path_keep_clear(loc))
        tips = builtins.dict()
        for loc in LOC_ORDER:
            got = rule_layout("hot_" + loc).get("tips")
            if isinstance(got, builtins.dict) and got:
                tips[loc] = zz_dump_plain(got)
        d["tips"] = tips
        d["faces"] = builtins.dict(
            (who, builtins.dict(eyes=zz_dump_plain(view_face_box(who, "eyes")), mouth=zz_dump_plain(view_face_box(who, "mouth")),
                                blink_also=builtins.list(view_blink_also(who))))
            for who in builtins.sorted(CAST) if view_face_box(who, "eyes") or view_face_box(who, "mouth"))
        d["world"] = zz_dump_plain(builtins.dict(
            inside=WORLD_INSIDE, pinless=WORLD_PINLESS, homes=WORLD_HOMES, asleep=WORLD_ASLEEP,
            away=builtins.dict((who, builtins.dict(("%s %s" % k, v) for k, v in cells.items())) for who, cells in WORLD_AWAY.items()),
            door_bond=builtins.dict((loc, world_door_bond(loc)) for loc in LOC_ORDER if world_door_bond(loc) is not None),
            door_owners=builtins.dict((loc, world_door_owners(loc)) for loc in LOC_ORDER if world_door_owners(loc))))
        d["standins"] = zz_dump_plain(builtins.dict(
            copies=builtins.dict((n, "images/bg/" + standin_copy(n)) for n in STANDIN_COPIES),
            names=builtins.dict(STANDIN_NAMES), if_file=builtins.dict(STANDIN_IF_FILE),
            people=[k for k, path, tint in STANDIN_PEOPLE]))
        d["names_key"] = ICON_NAMES_KEY

        ## The second sitting (D60): the limits, the look, each place's shapes.
        d["hot_shape"] = zz_dump_plain(HOT_SHAPE)
        d["hot_look"] = zz_dump_plain(hot_look())
        d["look_keys"] = builtins.list(HOT_LOOK_KEYS)
        shapes, keep, rects = builtins.dict(), builtins.dict(), builtins.dict()
        ## A name plate lies on the side its hover label opens on, and that is
        ## read from the `tips` of the sidecar of the place I stand in
        ## (icon_tip_hot): so the dump stands in each place in turn.
        was_here = store.here
        for loc in LOC_ORDER:
            store.here = loc
            side = rule_layout("hot_" + loc)
            if isinstance(side.get("shapes"), builtins.dict) and side["shapes"]:
                shapes[loc] = zz_dump_plain(side["shapes"])
            if isinstance(side.get("keep_tile"), builtins.dict) and side["keep_tile"]:
                keep[loc] = zz_dump_plain(side["keep_tile"])
            pts = hot_place_points(loc)
            got = builtins.dict()
            for h in HOT_SPOTS:
                if h["place"] == loc and h["id"] not in got and h["id"] in pts:
                    row = builtins.dict((k, h[k]) for k in HOT_KEYS)
                    row["x"], row["y"] = pts[h["id"]]
                    got[h["id"]] = [int(v) for v in hot_name_rect(row)]
            rects[loc] = got
        store.here = was_here
        d["shapes"] = shapes
        d["keep_tile"] = keep
        d["shaped"] = [loc for loc in LOC_ORDER if hot_shapes_for(loc)]
        d["name_rects"] = rects
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
        check(isinstance(_zz_d["spot_planned"], builtins.list) and len(_zz_d["spot_planned"]) == len(SPOT_PLANNED) >= 1
              and all(isinstance(r, builtins.list) and len(r) == 3 for r in _zz_d["spot_planned"]),
              "spot_planned holds SPOT_PLANNED as [id, place, kind] rows (%d)" % len(_zz_d["spot_planned"]))
        check(len(_zz_d["variants_planned"]) == len(WORLD_VARIANTS) and builtins.sorted(_zz_d["world"]) ==
              ["asleep", "away", "door_bond", "door_owners", "homes", "inside", "pinless"]
              and builtins.sorted(_zz_d["standins"]) == ["copies", "if_file", "names", "people"]
              and all(k in _zz_d for k in ("keep_clear", "tips", "faces", "names_key")),
              "the scaffold's keys are in it: variants_planned (%d), keep_clear, tips, faces (%d people), world, standins, names_key"
              % (len(_zz_d["variants_planned"]), len(_zz_d["faces"])))
        check(builtins.sorted(_zz_d["hot_shape"]) == builtins.sorted(HOT_SHAPE)
              and all(k in _zz_d["hot_shape"] for k in ("polys", "points", "area_min", "area_max", "buried_max", "grid", "top"))
              and all(isinstance(h["front"], bool) for v in _zz_d["hotspots"].values() for h in v)
              and builtins.sorted(_zz_d["hot_look"]) == builtins.sorted(_zz_d["look_keys"]) == builtins.sorted(HOT_LOOK_KEYS)
              and builtins.sorted(_zz_d["shapes"]) == builtins.sorted(l for l in LOC_ORDER if rule_layout("hot_" + l).get("shapes"))
              and all(_zz_d["shapes"][l] == rule_layout("hot_" + l)["shapes"] for l in _zz_d["shapes"])
              and _zz_d["shaped"] == [l for l in LOC_ORDER if hot_shapes_for(l)] and builtins.set(_zz_d["shaped"]) <= builtins.set(_zz_d["shapes"])
              and builtins.sorted(_zz_d["name_rects"]) == builtins.sorted(LOCATIONS)
              and all(len(r) == 4 for v in _zz_d["name_rects"].values() for r in v.values())
              and sum(len(v) for v in _zz_d["name_rects"].values()) == len(builtins.set(h["id"] for h in HOT_SPOTS)),
              "D60: the limits and the light's look (HOT_SHAPE, hot_look), each place's shapes and keep_tile rows as its sidecar holds them (%d places; %d shaped now), and a name plate's rectangle for every hotspot and exit (%d)"
              % (len(_zz_d["shapes"]), len(_zz_d["shaped"]), sum(len(v) for v in _zz_d["name_rects"].values())))
        ## A `tips` row of a place I do not stand in moves that place's plates
        ## (and no other's): the dump stands in each place while it measures.
        _zz_side = rule_layout("hot_courtyard")
        _zz_had = "hot_courtyard" in RULE_LAYOUT
        _zz_real = RULE_LAYOUT.get("hot_courtyard")
        _zz_side["tips"] = {"go_courtyard__gate": "left", "spot_vend": "bottom"}
        RULE_LAYOUT["hot_courtyard"] = _zz_side
        _zz_here = store.here
        _zz_t = zz_dump_build()
        if _zz_had:
            RULE_LAYOUT["hot_courtyard"] = _zz_real
        else:
            RULE_LAYOUT.pop("hot_courtyard", None)
        _zz_a, _zz_b = _zz_d["name_rects"]["courtyard"], _zz_t["name_rects"]["courtyard"]
        _zz_g, _zz_v = hot_place_points("courtyard")["go_courtyard__gate"], hot_place_points("courtyard")["spot_vend"]
        check(_zz_here != "courtyard" and store.here == _zz_here
              and _zz_b["go_courtyard__gate"][0] + _zz_b["go_courtyard__gate"][2] == int(_zz_g[0]) - 36 and _zz_b["go_courtyard__gate"][1] == int(_zz_g[1]) - 36
              and _zz_b["spot_vend"][:2] == [int(_zz_v[0]) - 36, int(_zz_v[1]) + 36]
              and _zz_a["go_courtyard__gate"] != _zz_b["go_courtyard__gate"] and _zz_a["spot_vend"] != _zz_b["spot_vend"]
              and all(_zz_a[k] == _zz_b[k] for k in _zz_a if k not in ("go_courtyard__gate", "spot_vend"))
              and all(_zz_d["name_rects"][l] == _zz_t["name_rects"][l] for l in LOC_ORDER if l != "courtyard")
              and _zz_t["tips"].get("courtyard") == _zz_side["tips"]
              and json.dumps(zz_dump_build(), sort_keys=True) == json.dumps(_zz_d, sort_keys=True),
              "D60: name_rects is measured standing in each place: a test `tips` row for the Courtyard, a place I do not stand in (I am in %s), puts the gate's plate left of its square and the machine's under it, and moves no other plate" % _zz_here,
              (_zz_a.get("go_courtyard__gate"), _zz_b.get("go_courtyard__gate"), _zz_a.get("spot_vend"), _zz_b.get("spot_vend")))
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
