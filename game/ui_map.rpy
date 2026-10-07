################################################################################
## Cursed Bonds — the map (PHASE1_DESIGN.md 4.6, WP1; PHASE2_DESIGN.md 4.1, P1).
##
## screen sb_map(layer="campus", area=None), called by the loop (sb_travel, the
## protected `call screen sb_map`) and by the car action (sb_do_car,
## layer="tokyo").
##
## Two levels, one screen. A screen variable, `zone`, says which is up:
##
##   Campus, level 1   "Jujutsu High": the six AREAS as markers (icon, name, up
##                     to three faces, what is waiting there, I'M HERE).
##                     Clicking one only opens it. A marker is 240 x 96 (D59,
##                     checkpoint B: "the black box is too big").
##   Campus, level 2   screen map_area(key): the area's own picture with one
##                     pin per place, its hub included (D53). Clicking a pin
##                     walks there: ("go", loc). The second UI overhaul (U0b):
##                     a room inside a house (WORLD_PINLESS in sb_world.rpy)
##                     has no pin; nobody asleep carries a gold mark, and a
##                     mission whose giver is asleep is not listed (D48).
##   Tokyo, level 1    the five districts as markers. Opens after Ijichi's
##                     ride-along (tokyo_open()).
##   Tokyo, level 2    screen map_district(key): the district's picture, its
##                     display-only pins, "Ride with Ijichi" and, in the
##                     Evening and at Night, "A night in ...".
##
## Esc: level 2 -> level 1 -> close. Every hover line is a tuple tooltip
## (text, key), drawn by hover_label (ui_icons.rpy).
##
## Returns ("go", loc), ("district", key), ("night", key) or ("cancel",).
##
## Pin positions: AREAS[...]["spots"] (sb_world.rpy) are the code's defaults;
## game/layout/area_<key>.json moves them (map_spots). tools/layout_sheet.py
## area_<key> draws them on the picture.
################################################################################

init -1 python:
    import builtins as _map_builtins

    ## The face on a side portrait (images/side/<who>_neutral.png, 360 wide),
    ## as a crop box (x, y, w, h), for the Find someone chips. The box is
    ## squared and kept inside the picture.
    FACE_BOX = {
        "yuji":    (126, 0, 112, 112),
        "megumi":  (122, 0, 116, 116),
        "nobara":  (124, 0, 112, 112),
        "maki":    (122, 0, 116, 116),
        "panda":   (108, 0, 144, 144),
        "toge":    (124, 0, 112, 112),
        "gojo":    (120, 0, 120, 120),
        "yaga":    (116, 0, 128, 128),
        "shoko":   (122, 0, 116, 116),
        "utahime": (122, 0, 116, 116),
        "ijichi":  (122, 0, 116, 116),
        "sana":    (124, 0, 112, 112),
    }

    ## Tokyo layer: card centres, and Ijichi's car.
    DISTRICT_POS = {
        "shinjuku": (500, 300),
        "harajuku": (520, 540),
        "shibuya":  (560, 780),
        "kawasaki": (1120, 820),
        "yotsuka":  (1340, 440),
    }
    CAR_POS = (1500, 220)

    ## Campus card geometry. Row heights are fixed, so a card's height is
    ## known before it is drawn and it can be kept clear of the header.
    MAP_CARD_W = 340
    MAP_ROW_W = 320
    MAP_ROW_H = 44
    MAP_ROW_H_MARKED = 64
    MAP_CARD_PAD = 10
    MAP_CARD_HEAD = 44
    MAP_CARD_GAP = 6
    MAP_TOP = 200          # below the header
    MAP_BOTTOM = 960       # above the Find someone strip

    _MAP_FACES = _map_builtins.dict()
    _MAP_TEXT_W = _map_builtins.dict()

    def face_chip(who, size=56):
        """WP1. A square face crop of someone's side portrait, size x size."""
        key = (who, size)
        d = _MAP_FACES.get(key)
        if d is not None:
            return d
        path = "images/side/%s_neutral.png" % who
        if not renpy.loadable(path):
            d = Text("？", font=gui.display_font, size=int(size * 0.6), color=gui.mute,
                     xalign=0.5, yalign=0.5)
        else:
            x, y, w, h = FACE_BOX.get(who, (68, 0, 223, 223))
            try:
                iw, ih = renpy.image_size(path)
                w = max(1, min(w, iw - x))
                h = max(1, min(h, ih - y))
            except Exception:
                pass
            s = min(w, h)
            x += (w - s) // 2
            d = Transform(path, crop=(x, y, s, s), xysize=(size, size))
        _MAP_FACES[key] = d
        return d

    def map_text_width(s, font, size):
        """WP1. The drawn width of one line of text, cached."""
        k = (s, font, size)
        w = _MAP_TEXT_W.get(k)
        if w is None:
            try:
                w = Text(s, font=font, size=size).size()[0]
            except Exception:
                w = len(s) * size * 0.6
            _MAP_TEXT_W[k] = w
        return w

    def map_has_news(who, loc):
        """WP1. A gold "!" after someone's name: a mission with them, or a
        new scene, that the place view would offer now (view_tag_marks: no
        mission mark in explore mode, on a rest day, or when the night
        won't let me start it; no scene the night won't let me start).
        Never for someone asleep (D48): nothing is offered with them."""
        if world_asleep(who):
            return False
        job, new = view_tag_marks(who, loc)
        return bool(job or new)

    def map_people(loc, budget, cap=3):
        """WP1. ([(short, colour, news)], hidden): up to `cap` of the people at
        loc whose names fit in `budget` pixels, then how many more there are."""
        folk = who_is_here(loc)
        shown, used = [], 0
        for w in folk:
            if len(shown) == cap:
                break
            c = CAST.get(w, {})
            nm = c.get("short", w.title())
            news = map_has_news(w, loc)
            wd = map_text_width(nm + ("!" if news else ""), gui.body_medium_font, 16) + (8 if shown else 0)
            rest = len(folk) - len(shown) - 1
            more = (map_text_width("+%d" % rest, gui.body_medium_font, 16) + 8) if rest else 0
            if shown and used + wd + more > budget:
                break
            shown.append((nm, c.get("color", gui.paper), news))
            used += wd
        return shown, len(folk) - len(shown)

    def map_mission_asleep(mid):
        """U0b (D48). bool: the giver of this mission is asleep. The frozen
        missions_here() finds a giver in who_is_here(), which still counts a
        sleeper; the map leaves such a mission out, as the place view's
        column does (rail_missions)."""
        m = MISSION_BY_ID.get(mid) or {}
        return bool(world_asleep(m.get("with_who") or m.get("who")))

    def map_waiting(area):
        """WP1. How many missions are waiting in an area now (missions_here),
        not counting one whose giver is asleep (D48)."""
        return sum(len([m for m in (missions_here(l) or []) if not map_mission_asleep(m)])
                   for l in places_in(area))

    def map_marks():
        """U0b (D48). mission_markers() for the map's second level, in the
        same shape ({loc: [(text, kind)]}), without the "mission" rows of a
        giver who is asleep (such a row's text begins with the giver's short
        name: "Maki · The Armory")."""
        out = {}
        asleep = [CAST[w]["short"] + u" · " for w in ROSTER_ORDER if w in CAST and world_asleep(w)]
        for loc, rows in (mission_markers() or {}).items():
            keep = [(t, k) for t, k in rows
                    if not (k == "mission" and any(t.startswith(a) for a in asleep))]
            if keep:
                out[loc] = keep
        return out

    def map_pins(key):
        """U0b. The places of an area that have a pin, in map order: every
        place but the rooms of WORLD_PINLESS, which are reached on foot."""
        return [l for l in places_in(key) if world_pinned(l)]

    def map_markers_text(marks, loc):
        """WP1. The row's second line, from mission_markers()."""
        return "  ·  ".join(t for t, k in (marks.get(loc) or []))

    def map_place_name(loc):
        """WP1. A place's name on the map. Utahime's office reads "Empty
        Office" until she arrives (LOCATIONS keeps the real name)."""
        if loc == "utahime_office" and not has_flag("utahime_arrived"):
            return "Empty Office"
        return LOCATIONS[loc]["name"]

    def map_name_budget(loc):
        """WP1. The pixels left for names beside a place's name on its row."""
        return MAP_ROW_W - 28 - map_text_width(map_place_name(loc), gui.display_font, 20) - 14

    def map_row_below(loc, marks):
        """WP1. True when a row shows its people on a second line: nothing
        else is there (no markers), the row is open and not mine, and more
        than one person wouldn't fit beside the name."""
        if marks.get(loc) or loc == store.here or not place_access(loc)[0]:
            return False
        folk = who_is_here(loc)
        return len(folk) > 1 and map_people(loc, map_name_budget(loc))[1] > 0

    def map_row_action(loc):
        """WP1. What a place's row does: ("go", loc) when it's open and not
        where I am; a locked row does nothing (it only shows its reason)."""
        if loc == store.here or not place_access(loc)[0]:
            return NullAction()
        return Return(("go", loc))

    def map_district_action(key):
        """WP1. What a district card does: ("district", key) when it's open
        and Ijichi is driving now (trip_ok_now()), else nothing."""
        if district_state(key)[0] and trip_ok_now():
            return Return(("district", key))
        return NullAction()

    def map_cards(marks):
        """WP1. [(area, x, y, [(loc, row_h, below)])]: each card's top-left
        corner, centred on its anchor and kept between the header and the
        strip. below: the row's people go on its second line."""
        out = []
        for a in AREAS:
            rows = []
            for l in a["places"]:
                below = map_row_below(l, marks)
                rows.append((l, MAP_ROW_H_MARKED if (marks.get(l) or below) else MAP_ROW_H, below))
            h = 2 * MAP_CARD_PAD + MAP_CARD_HEAD + sum(MAP_CARD_GAP + rh for l, rh, b in rows)
            ax, ay = a["anchor"]
            y = int(ay - h / 2)
            y = max(MAP_TOP, min(y, MAP_BOTTOM - h))
            out.append((a, int(ax - MAP_CARD_W / 2), y, rows))
        return out

    ## Phase 2 (4.1) -------------------------------------------------------------

    ## Where a pin may sit on an area's picture: clear of the top row, the
    ## Back button and the bottom corners.
    MAP_PIN_FRAME = (200, 200, 1700, 940)

    ## A marker (an area, a district) and a room's pin.
    MAP_MARKER_W = 300
    MAP_MARKER_H = 132
    MAP_PIN_W = 240
    MAP_DISC = 72
    MAP_FACE = 36
    MAP_FACE_CAP = 3
    ## An area's marker on level 1 (D59): smaller than a district's. The name
    ## on one line; under it up to three faces, "+n", the gold mark and the
    ## moon; under those, I'M HERE.
    MAP_AREA_W = 240
    MAP_AREA_H = 96
    MAP_AREA_FACE = 30
    ## The mountain as tools/genworld.py paints it on map_campus.png (the
    ## peak's triangle around (1290, 215)): x0, y0, x1, y1. The Mountain
    ## marker's centre stays inside it (D59; map_validate checks).
    MAP_MOUNTAIN_BOX = (1160, 119, 1420, 285)
    ## A pin left of this x has its hover label on its right (hover_label
    ## has no room on the left), so its faces go on the left of the tile.
    MAP_FACES_LEFT_X = 700

    ## Tokyo's second level: what a district has, as display-only pins
    ## ("Later build"). {district: [dict(id, name, icon, x, y, note)]}.
    MAP_DISTRICT_SPOTS = {
        "shibuya": [
            dict(id="shibuya_crossing", name="The scramble crossing", icon="place_later", x=560, y=560, note="Later build"),
            dict(id="shibuya_station",  name="The station",           icon="place_later", x=980, y=380, note="Later build"),
            dict(id="shibuya_arcade",   name="An arcade",             icon="place_later", x=1420, y=500, note="Later build"),
            dict(id="shibuya_cafe",     name="A café",                icon="place_later", x=760, y=800, note="Later build"),
        ],
        "harajuku": [
            dict(id="harajuku_street", name="Takeshita Street",  icon="place_later", x=640, y=520, note="Later build"),
            dict(id="harajuku_crepes", name="The crêpe stands",  icon="place_later", x=1080, y=640, note="Later build"),
            dict(id="harajuku_shop",   name="A talisman shop down a side street", icon="place_later", x=1460, y=420, note="Later build"),
        ],
        "shinjuku": [
            dict(id="shinjuku_streets", name="The neon streets", icon="place_later", x=600, y=640, note="Later build"),
            dict(id="shinjuku_station", name="The station",      icon="place_later", x=1000, y=460, note="Later build"),
            dict(id="shinjuku_roofs",   name="The rooftops",     icon="place_later", x=1400, y=300, note="Later build"),
        ],
        "kawasaki": [
            dict(id="kawasaki_river",  name="The river",  icon="place_later", x=520, y=700, note="Later build"),
            dict(id="kawasaki_cinema", name="The cinema", icon="place_later", x=1020, y=480, note="Later build"),
        ],
        "yotsuka": [
            dict(id="yotsuka_house", name="My parents' house", icon="place_later", x=1240, y=420, note="Later build"),
            dict(id="yotsuka_diner", name="The diner",         icon="place_later", x=620, y=520, note="Later build"),
            dict(id="yotsuka_alley", name="The alley behind the arcade", icon="place_later", x=900, y=780, note="Later build"),
        ],
    }

    ## The districts a night out can start in (D24). night_out_ok(key)
    ## (sb_night.rpy) says whether one can start now.
    MAP_NIGHT_DISTRICTS = ("shibuya", "shinjuku")

    def map_spots(key):
        """P1 (ui_map.rpy). dict {loc: (x, y)}: where an area's rooms are
        pinned on its picture. The code's defaults (AREAS[...]["spots"]),
        with the points of the sidecar game/layout/area_<key>.json laid over
        them (D5). A sidecar point that isn't two numbers, or names a room
        the area doesn't have, is ignored (map_validate reports it)."""
        a = AREA_BY_KEY.get(key)
        if a is None:
            return {}
        out = dict((l, (int(p[0]), int(p[1]))) for l, p in a["spots"].items())
        side = rule_layout("area_" + key).get("spots")
        if isinstance(side, (dict, _map_builtins.dict)):
            for l, p in side.items():
                if l in a["places"] and world_pinned(l) and map_point_ok(p):
                    out[l] = (int(p[0]), int(p[1]))
        return out

    def map_point_ok(p):
        """P1. True for a sidecar point: a list of two numbers."""
        return (isinstance(p, (list, tuple, _map_builtins.list)) and len(p) == 2
                and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in p))

    def map_zone_ok(view, zone):
        """P1. The level-2 key that is really open: `zone` when it is an
        area (campus) or a district (Tokyo), else None (level 1)."""
        if view == "tokyo":
            ## A closed district has no second level, however the map was
            ## opened (a caller's area= included).
            return zone if zone in DISTRICTS and district_state(zone)[0] else None
        return zone if zone in AREA_BY_KEY else None

    def map_title(view, zone):
        """P1. The one line at the top of the map."""
        if view == "tokyo":
            return DISTRICTS[zone]["name"] if zone else "Tokyo"
        return AREA_BY_KEY[zone]["name"] if zone else "Jujutsu High"

    def map_fit(s, size, width, font=None):
        """P1. The largest text size, at most `size` and at least 16, at
        which one line of `s` is no wider than `width` pixels."""
        font = font or gui.display_font
        while size > 16 and map_text_width(s, font, size) > width:
            size -= 1
        return size

    def map_faces(folk, cap=MAP_FACE_CAP):
        """P1. (shown, more): the first `cap` of a list of people, and how
        many are left over (drawn as "+n")."""
        folk = list(folk)
        return folk[:cap], max(0, len(folk) - cap)

    def map_pin_icon(loc):
        """P9. The icon on a place's pin: place_<loc>, or for a hub that has
        no picture of its own, its area's (D55: existing names only). The
        second overhaul gives each of the five yards (PATH_YARD_ICONS) an
        icon name of its own; its pin wears it once that picture is cut, as
        its exits do (path_icon). The Courtyard's pin is place_courtyard, as
        it always was."""
        if loc in PATH_YARD_ICONS:
            return path_icon(loc)
        name = "place_" + str(loc)
        if name in ICONS:
            return name
        return "area_" + str(area_of(loc))

    def map_area_rect(key):
        """P9. (x, y, w, h): where an area's marker is drawn on level 1."""
        ax, ay = AREA_BY_KEY[key]["anchor"]
        return (int(ax - MAP_AREA_W // 2), int(ay - MAP_AREA_H // 2), MAP_AREA_W, MAP_AREA_H)

    def map_area_people(key):
        """P1. Everyone in an area's rooms that I can enter now, in room
        order. Someone behind a locked door is on no marker."""
        out = []
        for l in places_in(key):
            if not place_access(l)[0]:
                continue
            for w in who_is_here(l):
                if w not in out:
                    out.append(w)
        return out

    def map_pin_people(loc):
        """P1. Who is in a room, for its pin; nobody when the door is locked."""
        if not place_access(loc)[0]:
            return []
        return list(who_is_here(loc))

    def map_pin_news(loc, marks):
        """P1. A pin's gold badge: a mission marker on the room, or someone
        there with a mission or a new scene (map_has_news)."""
        if not place_access(loc)[0]:
            return False
        if marks.get(loc):
            return True
        return any(map_has_news(w, loc) for w in who_is_here(loc))

    def map_names(folk):
        """P1. "Yuji, Megumi": short names, for a hover line."""
        return ", ".join(CAST.get(w, {}).get("short", w.title()) for w in folk)

    def map_area_tip(key):
        """P1. An area marker's hover line: its rooms (the ones with a pin:
        a room inside a house is found through its house), then its blurb."""
        a = AREA_BY_KEY[key]
        rooms = " · ".join(map_place_name(l) for l in map_pins(key))
        return (rooms + "\n" + a["blurb"], "area_" + key)

    def map_pin_tip(loc, marks):
        """P1. A pin's hover line: the room's name, then the lock's full
        reason, or what is waiting there, who is there and the room's
        description."""
        ok, why, short = place_access(loc)
        lines = [map_place_name(loc)]
        if not ok:
            lines.append(why)
        else:
            mk = map_markers_text(marks, loc)
            if mk:
                lines.append(mk)
            folk = who_is_here(loc)
            if folk:
                lines.append("Here now: " + map_names(folk))
            if loc == store.here:
                lines.append("I'm here.")
            lines.append(LOCATIONS[loc]["desc"])
        return ("\n".join(lines), "row_" + loc)

    def map_trip_wait():
        """P1. Why Ijichi isn't driving now: out of hours, or elsewhere in them."""
        if store.period in TRIP_PERIODS:
            return "Ijichi isn't at the gate right now."
        return "Ijichi drives from the gate, mornings to afternoons."

    def map_district_tip(key):
        """P1. A district marker's hover line."""
        d = DISTRICTS[key]
        ok, reason = district_state(key)
        if not ok:
            return ("%s\nNot open to me yet: %s." % (d["name"], reason), "district_" + key)
        return ("%s\n%s\nHalf a day by car." % (d["name"], d["desc"]), "district_" + key)

    def map_go_tip(key):
        """P1. The hover line of "Ride with Ijichi" in a district's view."""
        if trip_ok_now():
            return ("Ride with Ijichi\nHalf a day in the city, then back at the gate.", "district_go")
        return ("Ride with Ijichi\n" + map_trip_wait(), "district_go")

    def map_night_state(key):
        """P1. (shown, ok, reason) for a district's "A night in ..." button:
        shown only in a night district, in the Evening or at Night, and only
        when night_out_ok(key) has something to say (the stub's (False, "")
        hides it, so an unbuilt night out leaves no dead button). Never in a
        district that is still closed."""
        if key not in MAP_NIGHT_DISTRICTS or store.period not in ("Evening", "Night"):
            return (False, False, "")
        if not district_state(key)[0]:
            return (False, False, "")
        ok, reason = night_out_ok(key)
        return (bool(ok or reason), bool(ok), reason or "")

    def map_validate():
        """P1. Lint findings for the pins: every room is in exactly one
        area's spots (a room of WORLD_PINLESS in none: it has no pin), each
        point (the code's and the sidecar's) is inside MAP_PIN_FRAME, a
        sidecar names only its area's pinned rooms; the district pins have
        known icons and sit inside the frame."""
        out = []
        x0, y0, x1, y1 = MAP_PIN_FRAME
        seen = {}
        for a in AREAS:
            key = a["key"]
            for l in a["spots"]:
                seen.setdefault(l, []).append(key)
            side = rule_layout("area_" + key)
            for k in side:
                if k != "spots":
                    out.append("layout/area_%s.json: unknown key %r (only \"spots\")" % (key, k))
            pts = side.get("spots") or {}
            if not isinstance(pts, (dict, _map_builtins.dict)):
                out.append("layout/area_%s.json: \"spots\" must be an object" % key)
                pts = {}
            for l, p in sorted(pts.items()):
                if l not in a["places"]:
                    out.append("layout/area_%s.json: %r is not a room of this area" % (key, l))
                elif not world_pinned(l):
                    out.append("layout/area_%s.json: %r has no pin (WORLD_PINLESS)" % (key, l))
                elif not map_point_ok(p):
                    out.append("layout/area_%s.json: %r must be [x, y]" % (key, l))
            for l, (x, y) in sorted(map_spots(key).items()):
                if not (x0 <= x <= x1 and y0 <= y <= y1):
                    out.append("map pin %r at (%d, %d) is outside x %d to %d, y %d to %d"
                               % (l, x, y, x0, x1, y0, y1))
                if map_pin_icon(l) not in ICONS:
                    out.append("map pin %r has no icon" % l)
        for l in LOCATIONS:
            n = len(seen.get(l, []))
            if n != (1 if world_pinned(l) else 0):
                out.append("room %r is in %d areas' spots (must be exactly one, or none for a room without a pin)" % (l, n))
        ids = set()
        for dk, rows in sorted(MAP_DISTRICT_SPOTS.items()):
            if dk not in DISTRICTS:
                out.append("MAP_DISTRICT_SPOTS: unknown district %r" % dk)
            for r in rows:
                if sorted(r) != ["icon", "id", "name", "note", "x", "y"]:
                    out.append("MAP_DISTRICT_SPOTS %s: a row needs id, name, icon, x, y, note" % dk)
                    continue
                if r["id"] in ids:
                    out.append("MAP_DISTRICT_SPOTS: id %r is used twice" % r["id"])
                ids.add(r["id"])
                if r["icon"] not in ICONS:
                    out.append("MAP_DISTRICT_SPOTS %s: unknown icon %r" % (r["id"], r["icon"]))
                if not (x0 <= r["x"] <= x1 and y0 <= r["y"] <= y1):
                    out.append("MAP_DISTRICT_SPOTS %s: (%d, %d) is outside the pin frame" % (r["id"], r["x"], r["y"]))
        for dk in DISTRICT_ORDER:
            if dk not in DISTRICT_POS:
                out.append("DISTRICT_POS has no marker for %r" % dk)
        for dk in MAP_NIGHT_DISTRICTS:
            if dk not in DISTRICTS:
                out.append("MAP_NIGHT_DISTRICTS: unknown district %r" % dk)
        ## Level 1 (D59): no two area markers overlap, each keeps clear of
        ## the top row, and the Mountain's sits on the mountain.
        rects = [(a["key"], map_area_rect(a["key"])) for a in AREAS]
        for i, (ka, ra) in enumerate(rects):
            if ra[0] < 0 or ra[1] < 96 or ra[0] + ra[2] > 1920 or ra[1] + ra[3] > 1080:
                out.append("area marker %r at %r runs off the map or under its top row" % (ka, ra))
            for kb, rb in rects[i + 1:]:
                if ra[0] < rb[0] + rb[2] and rb[0] < ra[0] + ra[2] and ra[1] < rb[1] + rb[3] and rb[1] < ra[1] + ra[3]:
                    out.append("area markers %r and %r overlap" % (ka, kb))
        if "mountain" in AREA_BY_KEY:
            mx, my = AREA_BY_KEY["mountain"]["anchor"]
            x0, y0, x1, y1 = MAP_MOUNTAIN_BOX
            if not (x0 <= mx <= x1 and y0 <= my <= y1):
                out.append("the Mountain marker's centre (%d, %d) is not on the mountain %r" % (mx, my, MAP_MOUNTAIN_BOX))
        return out

    register_validator(map_validate)

    def map_who_where(who):
        """WP1. A Find someone chip's hover line: "Yuji — Cafeteria" or "Yuji — Off campus"."""
        name = CAST.get(who, {}).get("short", who.title())
        loc = char_location(who)
        if loc is None or loc not in LOCATIONS:
            return "%s — Off campus" % name
        return "%s — %s" % (name, LOCATIONS[loc]["name"])


## Map styles ###################################################################

style sb_node_button is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (18, 9, 18, 9)

style sb_node_here is sb_node_button:
    background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_active.png", 4, 4)

style sb_node_name is text:
    font gui.display_font
    color gui.paper
    size 21
    text_align 0.5
    layout "subtitle"

style sb_map_card is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (10, 10, 10, 10)

style sb_map_row is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (14, 0, 14, 0)

style sb_map_row_here is sb_map_row:
    background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_active.png", 4, 4)

## A locked row stays hoverable (so its full reason shows) but does nothing.
style sb_map_row_locked is sb_map_row:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_ghost.png", 4, 4)

style sb_map_place is text:
    font gui.display_font
    size 20
    color gui.paper

style sb_map_who is text:
    font gui.body_medium_font
    size 16

style sb_map_tab is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    selected_background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (18, 6, 18, 6)
    ysize 52

style sb_map_chip is frame:
    background Frame("gui/panel_ghost.png", 4, 4)
    padding (10, 3, 10, 3)

style sb_map_face is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (0, 0, 0, 0)
    xysize (56, 56)

style sb_map_district is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    insensitive_background Frame("gui/panel_dark.png", 4, 4)
    padding (18, 12, 18, 12)
    xsize 360


## Phase 2 (4.1): the two-level map's own styles.

## A district marker: 300 x 132. (An area's is map_area_marker, below.)
style map_marker is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (12, 10, 12, 10)
    xsize 300
    ysize 132

style map_marker_here is map_marker:
    background Frame("gui/panel_active.png", 4, 4)

style map_marker_locked is map_marker:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_ghost.png", 4, 4)

style map_marker_name is text:
    font gui.display_font
    size 26
    color gui.paper
    layout "nobreak"

## An area's marker on level 1 (D59): 240 x 96.
style map_area_marker is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (10, 8, 10, 8)
    xsize 240
    ysize 96

style map_area_marker_here is map_area_marker:
    background Frame("gui/panel_active.png", 4, 4)

style map_more is text:
    font gui.body_medium_font
    size 16
    color gui.dim

## A room's pin: the 72 px tile with its icon, and the name plate under it.
style map_pin is button:
    background None
    padding (0, 0, 0, 0)
    xsize 240

style map_pin_disc is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (0, 0, 0, 0)
    xysize (72, 72)

style map_pin_disc_here is map_pin_disc:
    background Frame("gui/panel_active.png", 4, 4)

style map_pin_disc_locked is map_pin_disc:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_ghost.png", 4, 4)

style map_pin_plate is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (10, 3, 10, 3)

style map_pin_name is text:
    font gui.display_font
    size 22
    color gui.paper
    hover_color gui.violet2
    layout "nobreak"

## The Campus / Tokyo switch: 124 x 52, two 56 x 44 icon buttons.
style map_switch is frame:
    background Frame("gui/panel_ghost.png", 4, 4)
    padding (4, 4, 4, 4)

## Back, and the two buttons of a district's view.
style map_wide is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (14, 8, 14, 8)

style map_wide_off is map_wide:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_ghost.png", 4, 4)

style map_wide_text is text:
    font gui.display_font
    size 24
    color gui.paper


## The second level's picture moves in when it appears (D17: a one-shot is
## ATL). A displayable that newly appears in a screen starts its ATL from
## zero, so this starts at the press that opened the area, not when the map
## was opened.
transform map_zoom_in:
    subpixel True
    xalign 0.5
    yalign 0.5
    zoom 1.12
    alpha 0.0
    easeout 0.3 zoom 1.0 alpha 1.0
    zoom 1.0 alpha 1.0      # exactly: the warper ends a hair short of 1.0


## The map ######################################################################

## Phase 2 (4.0, 4.1): `area` opens the map on one area's rooms (or, on the
## Tokyo layer, one district). `view` is the layer; `zone` is the area or
## district that is open, None on level 1.
screen sb_map(layer="campus", area=None):

    tag sandbox

    default view = layer
    default zone = area

    $ _map_tokyo = (view == "tokyo")
    $ _map_zone = map_zone_ok(view, zone)
    $ _topen = tokyo_open()

    ## Esc: an area or district -> the level above -> close.
    key "game_menu" action (SetScreenVariable("zone", None) if _map_zone else Return(("cancel",)))

    ## Ground ---------------------------------------------------------------------
    if _map_tokyo:
        add "bg map_tokyo"
        add Solid(gui.ink) alpha 0.30
    else:
        add "bg map_campus"
        add Solid(gui.ink) alpha 0.35

    ## The level -------------------------------------------------------------------
    if _map_tokyo:
        if _map_zone:
            use map_district(_map_zone)
        else:
            use sb_map_tokyo
    else:
        if _map_zone:
            use map_area(_map_zone)
        else:
            use sb_map_campus

    ## Top row: the title, written once; the Campus / Tokyo switch ------------------
    text map_title(view, _map_zone):
        substitute False
        xalign 0.5
        ypos 28
        font gui.display_font
        size 36
        color gui.paper

    frame:
        style "map_switch"
        xpos 1560
        ypos 26
        hbox:
            spacing 4
            use icon_btn("campus", [SelectedIf(not _map_tokyo), SetScreenVariable("view", "campus"), SetScreenVariable("zone", None)],
                         size=32, w=56, wid="map_campus")
            if _topen:
                use icon_btn("tokyo", [SelectedIf(_map_tokyo), SetScreenVariable("view", "tokyo"), SetScreenVariable("zone", None)],
                             size=32, w=56, wid="map_tokyo")
            else:
                use icon_btn("tokyo", NullAction(), tip="Tokyo — after Ijichi's ride-along", size=32, w=56, wid="map_tokyo")

    ## Stay here, bottom right -------------------------------------------------------
    hbox:
        xalign 1.0
        xoffset -40
        yalign 1.0
        yoffset -30
        use icon_btn("stay", Return(("cancel",)), tip="Stay here\nWalking is free. Doing something takes time.", wid="map_stay")

    use sb_hud(on_map=True)


## Campus, level 1: the six areas.
screen sb_map_campus():

    $ _map_moons = night_marks() or {}
    $ _map_mine = area_of(here)

    for _a in AREAS:
        $ _k = _a["key"]
        $ _faces, _more = map_faces(map_area_people(_k))
        $ _wait = map_waiting(_k)
        $ _cur = (_k == _map_mine)
        button:
            id ("area_" + _k)
            style ("map_area_marker_here" if _cur else "map_area_marker")
            xanchor 0.5
            yanchor 0.5
            xpos _a["anchor"][0]
            ypos _a["anchor"][1]
            tooltip map_area_tip(_k)
            action SetScreenVariable("zone", _k)
            fixed:
                ## The name, on one line.
                hbox:
                    spacing 8
                    add icon("area_" + _k, 30) yalign 0.5
                    text _a["name"] style "map_marker_name" size map_fit(_a["name"], 22, 180) yalign 0.5
                ## Who is there, on the left; what is waiting, on the right.
                hbox:
                    ypos 34
                    spacing 3
                    for _w in _faces:
                        add face_chip(_w, MAP_AREA_FACE)
                    if _more:
                        text "+[_more]" style "map_more" yalign 0.5 xoffset 3
                hbox:
                    ypos 34
                    xalign 1.0
                    ysize MAP_AREA_FACE
                    spacing 6
                    if _wait:
                        text "◆ [_wait]" font gui.body_medium_font size 16 color gui.gold yalign 0.5
                    if _map_moons.get(_k):
                        add icon("moon", 22) yalign 0.5
                if _cur:
                    text _("I'M HERE") style "jjk_label" size 12 kerning 1.0 color gui.violet2 ypos 66


## Campus, level 2: one area's picture, a pin for each of its rooms.
screen map_area(key):

    $ _a = AREA_BY_KEY[key]
    $ _marks = map_marks()
    $ _spots = map_spots(key)

    if view_motion():
        add _a["bg"] at map_zoom_in id "map_zone_bg"
    else:
        add _a["bg"] id "map_zone_bg"
    add Solid(gui.ink) alpha 0.30

    use map_back("Jujutsu High")

    for _l in map_pins(key):
        $ _x, _y = _spots[_l]
        $ _ok = place_access(_l)[0]
        $ _cur = (_l == here)
        $ _faces, _more = map_faces(map_pin_people(_l))
        $ _nm = map_place_name(_l)

        ## A violet ring on the room I'm in.
        if _cur:
            add "gui/hot_ring.png":
                xysize (104, 104)
                xanchor 0.5
                yanchor 0.5
                xpos _x
                ypos _y
                matrixcolor TintMatrix(gui.violet2)

        button:
            id ("row_" + _l)
            style "map_pin"
            xanchor 0.5
            xpos _x
            ypos (_y - 36)
            tooltip map_pin_tip(_l, _marks)
            action map_row_action(_l)
            vbox:
                xalign 0.5
                spacing 6
                frame:
                    style ("map_pin_disc_here" if _cur else ("map_pin_disc" if _ok else "map_pin_disc_locked"))
                    xalign 0.5
                    add icon(map_pin_icon(_l), 52) xalign 0.5 yalign 0.5 alpha (1.0 if _ok else 0.45)
                frame:
                    style "map_pin_plate"
                    xalign 0.5
                    text "[_nm!q]" style "map_pin_name" size map_fit(_nm, 22, MAP_PIN_W - 24) color (gui.violet2 if _cur else (gui.paper if _ok else gui.mute))

        ## Badges on the tile's corners: locked, or something new.
        if not _ok:
            add icon("lock", 30) xanchor 0.5 yanchor 0.5 xpos (_x + 34) ypos (_y + 30)
        elif map_pin_news(_l, _marks):
            add icon("news", 30, True) xanchor 0.5 yanchor 0.5 xpos (_x + 34) ypos (_y - 32)

        ## Who is there, beside the tile: on its right, or on its left when
        ## the hover label will open on the right (a pin near the left edge).
        if _faces and _x < MAP_FACES_LEFT_X:
            hbox:
                id ("faces_" + _l)
                xpos (_x - 46)
                xanchor 1.0
                ypos _y
                yanchor 0.5
                spacing 4
                if _more:
                    text "+[_more]" style "map_more" yalign 0.5 xoffset -4 color gui.paper
                for _w in _faces:
                    add face_chip(_w, MAP_FACE)
        elif _faces:
            hbox:
                id ("faces_" + _l)
                xpos (_x + 46)
                ypos _y
                yanchor 0.5
                spacing 4
                for _w in _faces:
                    add face_chip(_w, MAP_FACE)
                if _more:
                    text "+[_more]" style "map_more" yalign 0.5 xoffset 4 color gui.paper


## Back to level 1, at (40, 96): the back arrow and where it leads.
screen map_back(where):
    button:
        id "map_back"
        style "map_wide"
        xpos 40
        ypos 96
        xminimum 220
        tooltip ("Back to " + where, "map_back")
        action SetScreenVariable("zone", None)
        hbox:
            spacing 12
            add icon("back", 36) yalign 0.5
            text where style "map_wide_text" substitute False yalign 0.5


## Tokyo, level 1: the five districts.
screen sb_map_tokyo():

    for _dk in DISTRICT_ORDER:
        $ _d = DISTRICTS[_dk]
        $ _pos = DISTRICT_POS.get(_dk, (960, 540))
        $ _open, _reason = district_state(_dk)
        $ _seen = (_dk in districts_visited)
        button:
            id ("district_" + _dk)
            style ("map_marker" if _open else "map_marker_locked")
            xanchor 0.5
            yanchor 0.5
            xpos _pos[0]
            ypos _pos[1]
            tooltip map_district_tip(_dk)
            action (SetScreenVariable("zone", _dk) if _open else NullAction())
            fixed:
                hbox:
                    spacing 12
                    text _d["kanji"] font gui.display_heavy_font size 40 color (gui.seal if _open else gui.mute) yalign 0.5
                    text _d["name"] style "map_marker_name" size map_fit(_d["name"], 24, 180) color (gui.paper if _open else gui.dim) yalign 0.5
                hbox:
                    ypos 70
                    spacing 10
                    if not _open:
                        frame:
                            style "sb_map_chip"
                            text "[_reason!q]" font gui.body_medium_font size 14 color gui.seal layout "nobreak"
                    elif _seen:
                        frame:
                            style "sb_map_chip"
                            text _("VISITED") font gui.body_medium_font size 14 color gui.gold
                    if _open and night_out_ok(_dk)[0]:
                        add icon("moon", 24) yalign 0.5


## Tokyo, level 2: one district. Its places are display only; the car, and in
## the Evening and at Night a night out, start from here.
screen map_district(key):

    $ _d = DISTRICTS[key]
    $ _go = (district_state(key)[0] and trip_ok_now())
    $ _nshow, _nok, _nwhy = map_night_state(key)

    if view_motion():
        add _d["bg"] at map_zoom_in id "map_zone_bg"
    else:
        add _d["bg"] id "map_zone_bg"
    add Solid(gui.ink) alpha 0.45

    use map_back("Tokyo")

    for _s in MAP_DISTRICT_SPOTS.get(key, ()):
        button:
            id ("spot_" + _s["id"])
            style "map_pin"
            xsize 72
            xanchor 0.5
            xpos _s["x"]
            ypos (_s["y"] - 36)
            tooltip (_s["name"] + "\n" + _s["note"], "spot_" + _s["id"])
            action NullAction()
            frame:
                style "map_pin_disc_locked"
                add icon(_s["icon"], 52) xalign 0.5 yalign 0.5 alpha 0.5

    vbox:
        xpos 1180
        ypos 760
        spacing 10
        button:
            id "district_go"
            style ("map_wide" if _go else "map_wide_off")
            xsize 560
            tooltip map_go_tip(key)
            action map_district_action(key)
            hbox:
                spacing 14
                add icon("car", 40) yalign 0.5 alpha (1.0 if _go else 0.45)
                text _("Ride with Ijichi · half a day") style "map_wide_text" color (gui.paper if _go else gui.mute) yalign 0.5
        if _nshow:
            $ _nname = _d["name"]
            button:
                id "district_night"
                style ("map_wide" if _nok else "map_wide_off")
                xsize 560
                tooltip (("A night in %s\nI stay out until morning." % _nname) if _nok else ("A night in %s\n%s" % (_nname, _nwhy)), "district_night")
                action (Return(("night", key)) if _nok else NullAction())
                hbox:
                    spacing 14
                    add icon("moon", 40) yalign 0.5 alpha (1.0 if _nok else 0.45)
                    text "A night in [_nname!q]" style "map_wide_text" color (gui.paper if _nok else gui.mute) yalign 0.5
