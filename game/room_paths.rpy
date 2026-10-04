################################################################################
## Cursed Bonds — walking between places: hubs and exits.
##
## Phase 2, P9 (PHASE2_DESIGN.md section 13, D53 to D56). Checkpoint B: "once
## you're in an area of the map we should have [things you can click] that
## lead to the other section".
##
## Every area has a hub, an outdoor place all its rooms open onto (PATH_HUBS).
## In every place the ways out are things to click in the picture:
##
##   from a room   one exit, to its area's hub
##   from a hub    one exit to each of its rooms, and one to each neighbouring
##                 hub (PATH_LINKS: as the paths on map_campus.png join the areas)
##
## Walking is free and instant, at any hour, and works in explore mode. The
## map still goes anywhere in two clicks.
##
## An exit is an action hotspot on the frozen framework (sb_hotspots.rpy, 4.10):
##
##   place action  "path_<to>"        one for each destination, offered in every
##                                    place that has an exit to it; cost 0
##   hotspot       "go_<from>__<to>"  at PATH_EXITS[from][to], drawn as the
##                                    destination's icon; it stands for that action
##   label         sb_do_path_<to>    walks there (label path_walk: the same
##                                    arrival as the map's and the journal's)
##
## (D55 names the action "go_<to>". Its label would be sb_do_go_<to>, which R1
## does not allow in this file: an action's id must carry the file's prefix.)
##
## When someone stands in front of an exit it moves to the icon column, like
## any hotspot (hot_covers / rail_actions).
##
## A locked destination (place_access refuses): the exit stays where it is,
## drawn as the lock icon; its hover label is the lock's reason; clicking it
## does nothing. The frozen hot_layer has no dim state for it (see the P8
## hand-off), so the two rows below read their label and icon when they are
## asked for them (path_ActionRow, path_SpotRow: by row[key], row.get(key),
## row.items(), row.values() or a dict(row) copy made now) and nothing is ever
## written to a registry at run time.
##
## Provides (frozen for P8, 13.2): path_exits(loc), path_hub(area_key),
## path_neighbours(loc). Plain values, never None.
##
## Where an exit sits (D56): a door, a gate or a path on the place's picture,
## inside x 40 to 1700 and y 180 to 1000, clear of the toast and banner lanes
## and of the arrival caption's panel (PATH_CAPTION_BOX), at least PATH_CLEAR px from every hotspot start point of 4.10's table
## (PATH_KEEP_CLEAR), and PATH_APART px from the place's other exits. P6's
## sidecar game/layout/hot_<place>.json can move one by its hotspot id, as it
## moves any hotspot. The five new hubs still show stand-in pictures, so their
## points follow one plan until the pictures are painted: rooms along the top
## at y 272 (below a two-line banner, above the people), between the arrival
## caption and the toast lane (x 850 to 1270), a room that can be locked
## leftmost (its long hover label opens to the left, over empty picture);
## neighbouring hubs at the sides.
################################################################################

init python:
    import builtins as path_builtins

    ## area -> its hub. The heart keeps the courtyard (the gate opens onto it).
    PATH_HUBS = {
        "heart":    "courtyard",
        "school":   "school_yard",
        "dorms":    "dorm_yard",
        "staff":    "staff_yard",
        "grounds":  "training_yard",
        "mountain": "trailhead",
    }

    ## Hubs that are one step apart, as the paths drawn on map_campus.png
    ## (tools/genworld.py, PATHS) join the areas. The picture has no path from
    ## the courtyard to the staff building: the office is reached from the
    ## training hall and from the girls' dormitory, so the staff steps join
    ## the training yard and the dormitory garden instead (D54: "adjusts if
    ## the picture says otherwise").
    PATH_LINKS = [
        ("courtyard", "school_yard"),
        ("courtyard", "dorm_yard"),
        ("courtyard", "training_yard"),
        ("dorm_yard", "staff_yard"),
        ("dorm_yard", "trailhead"),
        ("staff_yard", "training_yard"),
    ]

    ## from -> [(to, x, y)]: every exit, in the order path_exits() gives them
    ## (a room: its hub; a hub: its rooms, then the neighbouring hubs).
    PATH_EXITS = {
        ## Courtyard & Gate -------------------------------------------------------
        "gate":           [("courtyard", 960, 280)],        # through the torii, up to the hall
        "courtyard":      [("gate", 1180, 985),             # back down the flagstones (right of a lone person's name tag)
                           ("school_yard", 84, 600),        # past the west hall's veranda
                           ("dorm_yard", 960, 272),         # behind the main hall, uphill
                           ("training_yard", 1640, 780)],   # the east hall's steps
        ## School Building --------------------------------------------------------
        "school_yard":    [("classroom", 850, 272), ("cafeteria", 990, 272),
                           ("infirmary", 1130, 272), ("library", 1270, 272),
                           ("courtyard", 1640, 620)],
        "classroom":      [("school_yard", 1670, 620)],     # the sliding door, right wall
        "cafeteria":      [("school_yard", 230, 520)],      # the glass doors on the left
        "infirmary":      [("school_yard", 84, 500)],       # out past the desk
        "library":        [("school_yard", 1660, 880)],     # back the way I came in
        ## Dormitories ------------------------------------------------------------
        "dorm_yard":      [("dorm", 990, 272), ("dorm_common", 1130, 272),
                           ("girls_dorm", 850, 272), ("rooftop", 1270, 272),
                           ("courtyard", 1640, 800), ("staff_yard", 1640, 520),
                           ("trailhead", 84, 600)],
        "dorm":           [("dorm_yard", 150, 560)],        # my door
        "dorm_common":    [("dorm_yard", 84, 540)],         # the sliding door
        "girls_dorm":     [("dorm_yard", 1090, 560)],       # the far end of the corridor
        "rooftop":        [("dorm_yard", 1680, 640)],       # the stairs behind the pillar
        ## Staff Building ---------------------------------------------------------
        "staff_yard":     [("office", 1060, 272), ("utahime_office", 850, 272),
                           ("gojo_office", 1270, 272),
                           ("dorm_yard", 84, 600), ("training_yard", 1640, 620)],
        "office":         [("staff_yard", 84, 560)],        # the open side of the hall
        "utahime_office": [("staff_yard", 84, 520)],        # the sliding door
        "gojo_office":    [("staff_yard", 1680, 640)],      # the sliding door
        ## Training Grounds -------------------------------------------------------
        "training_yard":  [("training", 1060, 272), ("dojo", 1270, 272),
                           ("storehouse", 850, 272),
                           ("courtyard", 84, 600), ("staff_yard", 1640, 520)],
        "training":       [("training_yard", 230, 600)],    # the bright doorway, far left
        "dojo":           [("training_yard", 84, 620)],     # the open panel on the left
        "storehouse":     [("training_yard", 84, 520)],     # daylight at the door
        ## The Mountain -----------------------------------------------------------
        "trailhead":      [("forest", 850, 272), ("ridge", 1060, 272),
                           ("riverside", 1270, 272),
                           ("dorm_yard", 1640, 760)],
        "forest":         [("trailhead", 84, 600)],         # back down, where the trees open
        "riverside":      [("trailhead", 84, 760)],         # the sandy path on the bank
        "ridge":          [("trailhead", 84, 720)],         # down the slope
    }

    ## The hotspot start points of 4.10's table (P6's to settle): an exit
    ## keeps PATH_CLEAR px from each in its own place.
    PATH_KEEP_CLEAR = {
        "dorm":           [(1240, 600), (420, 760)],
        "dorm_common":    [(900, 800), (1420, 520)],
        "riverside":      [(1180, 820)],
        "library":        [(520, 520), (1480, 460)],
        "courtyard":      [(1500, 640)],
        "classroom":      [(760, 360)],
        "cafeteria":      [(1200, 560)],
        "infirmary":      [(640, 700)],
        "storehouse":     [(960, 560)],
        "utahime_office": [(1320, 420)],
        "ridge":          [(960, 420)],
    }
    PATH_CLEAR = 120
    PATH_APART = 110        # between two exits of one place (their rings are 96 px)

    ## The arrival caption's panel (screen sb_place: a frame at (40, 100), up
    ## to 744 wide, 157 tall with a two-line description). It lies over the
    ## picture for the first seconds in a place, so no exit sits under it.
    PATH_CAPTION_BOX = (40, 100, 744, 160)

    ## "To the School Courtyard": the few names that take no article.
    PATH_TO_WORDS = {
        "dorm":           "To My Room",
        "utahime_office": "To Utahime's Office",
        "gojo_office":    "To Gojo's Office",
    }

    ## Where a hidden exit's tile stands in the icon column.
    PATH_ACTION_ORDER = 5       # first among the registered place actions (the default is 50)

    def path_hub(area_key):
        """P9 (room_paths.rpy), frozen for P8. The place key of an area's hub
        ("school" -> "school_yard"); "" for a key that is not an area."""
        return PATH_HUBS.get(area_key, "")

    def path_is_hub(loc):
        """P9. bool: the place is its area's hub."""
        return bool(loc) and path_hub(area_of(loc) or "") == loc

    def path_neighbours(loc):
        """P9 (room_paths.rpy), frozen for P8. The place keys one step from
        `loc` by its exits, in exit order; [] for a place that has none."""
        return [row[0] for row in PATH_EXITS.get(loc, ())]

    def path_icon(to):
        """P9. The icon an exit to `to` is drawn as: area_<key> for a hub,
        place_<room> for a room (existing icon names only, D55)."""
        if path_is_hub(to):
            return "area_" + area_of(to)
        return "place_" + to

    def path_locked(to):
        """P9. The lock's reason when place_access refuses the place, else
        "" (the door is open)."""
        if to not in LOCATIONS:
            return ""
        ok, why, short = place_access(to)
        return "" if ok else (why or short or "Locked.")

    def path_words(to):
        """P9. An open exit's hover label: "To the School Courtyard"."""
        if to in PATH_TO_WORDS:
            return PATH_TO_WORDS[to]
        return "To the " + LOCATIONS[to]["name"]

    def path_label(to):
        """P9. An exit's hover label now: where it leads, or the lock's
        reason while the place is locked (D55)."""
        return path_locked(to) or path_words(to)

    def path_spot_id(frm, to):
        """P9. The hotspot id of the exit from `frm` to `to`."""
        return "go_%s__%s" % (frm, to)

    def path_exits(loc):
        """P9 (room_paths.rpy), frozen for P8. The exits of a place, in a
        stable order (PATH_EXITS): a list of dicts
        (to, label, icon, x, y, locked_reason).

          to             the place key it leads to
          label          the hover label now ("To the Dojo", or the lock's reason)
          icon           the destination's icon (a locked exit is drawn as "lock")
          x, y           where it sits (the sidecar hot_<loc>.json applied), ints
          locked_reason  "" when I can walk there now

        [] for a place with no exits (none ships)."""
        side = rule_layout("hot_" + str(loc)).get("spots")
        if not isinstance(side, path_builtins.dict):
            side = {}
        out = []
        for to, x, y in PATH_EXITS.get(loc, ()):
            p = side.get(path_spot_id(loc, to))
            if isinstance(p, (path_builtins.list, path_builtins.tuple)) and len(p) == 2 and hot_number(p[0]) and hot_number(p[1]):
                x, y = p[0], p[1]
            out.append(path_builtins.dict(to=to, label=path_label(to), icon=path_icon(to),
                                          x=int(x), y=int(y), locked_reason=path_locked(to)))
        return out

    def path_reach(start):
        """P9. The set of places reached from `start` by exits alone."""
        seen = path_builtins.set([start])
        todo = [start]
        while todo:
            for to in path_neighbours(todo.pop()):
                if to not in seen:
                    seen.add(to)
                    todo.append(to)
        return seen

    ## The registry rows (see the header) -----------------------------------------

    class path_LiveRow(path_builtins.dict):
        """P9. A registry row with a value that is read when it is asked
        for. Every way of reading it gives the value as it is now: row[key],
        row.get(key), row.items(), row.values(), and a dict(row) copy (which
        then keeps the value of the moment it was made). Init data, never
        saved."""

        def path_now(self, key):
            return path_builtins.dict.__getitem__(self, key)

        def __getitem__(self, key):
            return self.path_now(key)

        def get(self, key, default=None):
            return self.path_now(key) if key in self else default

        def __iter__(self):
            ## Defined so that dict(row) and dict.update(row) read each value
            ## through __getitem__ instead of copying the stored ones.
            return path_builtins.dict.__iter__(self)

        def items(self):
            return [(k, self.path_now(k)) for k in path_builtins.dict.keys(self)]

        def values(self):
            return [self.path_now(k) for k in path_builtins.dict.keys(self)]

        def copy(self):
            return path_builtins.dict(self.items())

    class path_ActionRow(path_LiveRow):
        """P9. A PLACE_ACTIONS row whose label is read when it is asked for:
        where the exit leads, or the lock's reason."""

        def path_now(self, key):
            if key == "label":
                return path_label(path_builtins.dict.__getitem__(self, "to"))
            return path_builtins.dict.__getitem__(self, key)

    class path_SpotRow(path_LiveRow):
        """P9. A HOT_SPOTS row whose icon is the lock while its destination
        is locked."""

        def path_now(self, key):
            if key == "icon" and path_locked(path_builtins.dict.__getitem__(self, "to")):
                return "lock"
            return path_builtins.dict.__getitem__(self, key)

    def path_register():
        """P9. Registers one place action for each destination and one
        hotspot for each exit; gives each action and each new hub its icon
        (ICON_FOR has no row for them, and the column would draw the generic
        icon). Called once, below."""
        froms = {}
        for frm in LOC_ORDER:
            for to, x, y in PATH_EXITS.get(frm, ()):
                froms.setdefault(to, []).append(frm)
        for to in LOC_ORDER:
            if to not in froms:
                continue
            register_place_action("path_" + to, path_words(to), "", cost=0, locs=tuple(froms[to]),
                                  order=PATH_ACTION_ORDER, explore=True)
            PLACE_ACTIONS[-1] = path_ActionRow(PLACE_ACTIONS[-1], to=to)
            ICON_FOR[("act", "path_" + to)] = path_icon(to)
        for frm in LOC_ORDER:
            for to, x, y in PATH_EXITS.get(frm, ()):
                register_hotspot(path_spot_id(frm, to), frm, x, y, path_icon(to), act="path_" + to)
                HOT_SPOTS[-1] = path_SpotRow(HOT_SPOTS[-1], to=to)
        for key, hub in PATH_HUBS.items():
            ICON_FOR.setdefault(("place", hub), "area_" + key)

    path_register()

    ## The validator (13.2) ---------------------------------------------------------

    def path_validate():
        """P9. Lint findings for the hubs and the exits: every area has a
        hub among its places; every place has an exit; a room's first exit
        is its hub; a hub leads to each of its rooms and each neighbouring
        hub and nowhere else; every exit has a way back; from my room every
        place is reached; each point keeps clear of 4.10's start points, of
        the place's other exits and of the arrival caption's panel (the
        sidecar's point too). (Bounds and lanes are hot_validate's.)"""
        out = []
        links = {}
        for a, b in PATH_LINKS:
            for x, y in ((a, b), (b, a)):
                links.setdefault(x, []).append(y)
        for area in AREAS:
            key = area["key"]
            hub = path_hub(key)
            if hub not in area["places"]:
                out.append("PATH_HUBS: area %r has no hub among its places (%r)" % (key, hub))
                continue
            want = [l for l in area["places"] if l != hub] + links.get(hub, [])
            got = path_neighbours(hub)
            for l in want:
                if l not in got:
                    out.append("exits: the hub %r has no exit to %r" % (hub, l))
            for l in got:
                if l not in want:
                    out.append("exits: the hub %r has an exit to %r, which is neither its room nor a neighbouring hub" % (hub, l))
            for l in area["places"]:
                if l != hub and path_neighbours(l)[:1] != [hub]:
                    out.append("exits: the first exit of %r must lead to its hub %r" % (l, hub))
        for a, b in PATH_LINKS:
            if not (path_is_hub(a) and path_is_hub(b)):
                out.append("PATH_LINKS: %r and %r must both be hubs" % (a, b))
        for loc in LOCATIONS:
            if not path_neighbours(loc):
                out.append("exits: %r has no exit" % loc)
        for frm, rows in sorted(PATH_EXITS.items()):
            if frm not in LOCATIONS:
                out.append("PATH_EXITS: %r is not a place" % frm)
                continue
            tos = [r[0] for r in rows]
            if len(tos) != len(path_builtins.set(tos)):
                out.append("PATH_EXITS %r: a destination is listed twice" % frm)
            for to, x, y in rows:
                if to not in LOCATIONS or to == frm:
                    out.append("PATH_EXITS %r: %r is not another place" % (frm, to))
                    continue
                if frm not in path_neighbours(to):
                    out.append("exits: %r leads to %r but there is no way back" % (frm, to))
                if not renpy.has_label("sb_do_path_" + to):
                    out.append("exits: no label sb_do_path_%s" % to)
                if path_icon(to) not in ICONS:
                    out.append("exits: %r has no icon (%r)" % (to, path_icon(to)))
                for px, py in PATH_KEEP_CLEAR.get(frm, ()):
                    if (x - px) ** 2 + (y - py) ** 2 < PATH_CLEAR ** 2:
                        out.append("exit %s at (%d, %d) is within %d px of the hotspot start point (%d, %d)"
                                   % (path_spot_id(frm, to), x, y, PATH_CLEAR, px, py))
                for to2, x2, y2 in rows:
                    if to2 > to and (x - x2) ** 2 + (y - y2) ** 2 < PATH_APART ** 2:
                        out.append("exits %s and %s of %r are less than %d px apart"
                                   % (path_spot_id(frm, to), path_spot_id(frm, to2), frm, PATH_APART))
        for frm in sorted(PATH_EXITS):
            if frm not in LOCATIONS:
                continue
            for r in path_exits(frm):
                if hot_overlap(hot_rect(r["x"], r["y"]), PATH_CAPTION_BOX):
                    out.append("exit %s at (%d, %d) lies under the arrival caption %r"
                               % (path_spot_id(frm, r["to"]), r["x"], r["y"], PATH_CAPTION_BOX))
        if "dorm" in LOCATIONS:
            lost = sorted(path_builtins.set(LOCATIONS) - path_reach("dorm"))
            if lost:
                out.append("exits: not reached from my room by exits alone: %s" % ", ".join(lost))
        return out

    register_validator(path_validate)


## Walking (D55) ###############################################################
##
## One label does the walking; each destination's action label calls it.
## A locked door does nothing: the exit's hover label already says why.
## Otherwise it is rule_walk_to, the walk the journal's "Go there" takes and
## the same statements as the map's sb_travel: `here` changes, the new
## place's picture dissolves in, and the loop then shows the arrival caption,
## sets the light (view_sync_light) and plays any story beat waiting there.

label path_walk(path_to):
    if path_to not in LOCATIONS or path_locked(path_to):
        return
    call rule_walk_to(path_to)
    return


label sb_do_path_gate:
    call path_walk("gate")
    return

label sb_do_path_courtyard:
    call path_walk("courtyard")
    return

label sb_do_path_classroom:
    call path_walk("classroom")
    return

label sb_do_path_cafeteria:
    call path_walk("cafeteria")
    return

label sb_do_path_training:
    call path_walk("training")
    return

label sb_do_path_dojo:
    call path_walk("dojo")
    return

label sb_do_path_dorm_common:
    call path_walk("dorm_common")
    return

label sb_do_path_dorm:
    call path_walk("dorm")
    return

label sb_do_path_girls_dorm:
    call path_walk("girls_dorm")
    return

label sb_do_path_rooftop:
    call path_walk("rooftop")
    return

label sb_do_path_infirmary:
    call path_walk("infirmary")
    return

label sb_do_path_office:
    call path_walk("office")
    return

label sb_do_path_utahime_office:
    call path_walk("utahime_office")
    return

label sb_do_path_gojo_office:
    call path_walk("gojo_office")
    return

label sb_do_path_storehouse:
    call path_walk("storehouse")
    return

label sb_do_path_forest:
    call path_walk("forest")
    return

label sb_do_path_riverside:
    call path_walk("riverside")
    return

label sb_do_path_ridge:
    call path_walk("ridge")
    return

label sb_do_path_library:
    call path_walk("library")
    return

label sb_do_path_school_yard:
    call path_walk("school_yard")
    return

label sb_do_path_dorm_yard:
    call path_walk("dorm_yard")
    return

label sb_do_path_staff_yard:
    call path_walk("staff_yard")
    return

label sb_do_path_training_yard:
    call path_walk("training_yard")
    return

label sb_do_path_trailhead:
    call path_walk("trailhead")
    return
