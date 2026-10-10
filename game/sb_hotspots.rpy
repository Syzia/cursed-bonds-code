################################################################################
## Cursed Bonds — hotspots in rooms, and the minigame interface.
##
## Phase 2, P0 (PHASE2_DESIGN.md 4.10, 4.12, D30, 6.1). Final: frozen after
## wave 0. The content (which rooms have what) is room_spots.rpy's and the
## room_*.rpy files'; nothing is registered here.
##
##   register_hotspot(id, place, x, y, icon, ...)   a point and an icon in a room
##   hot_spots_for(loc)     the hotspots visible in a room right now
##   hot_covers(loc)        the action ids a visible hotspot offers (the icon
##                          column leaves those out: rail_actions)
##   screen hot_layer(loc, front=False)             draws them
##   hot_shapes_for(loc)    the traced shapes of a place whose new picture is
##                          in ({} for any other): there the picture itself is
##                          what is clicked (the second overhaul, D60; see
##                          "The picture is what is clicked", below)
##   hot_tip_rect(key)      the square a shaped hotspot's name opens against
##   label hot_use(hot_id)  a look hotspot's line
##   register_minigame(id, name, icon, min_people=1), mg_games()
##                          a game is `label mg_<id>(opponents, stake=0)`; it
##                          sets mg_result = dict(game, outcome, yen) and returns
##
## The registries are made at init -5 (as sb_hooks.rpy's are): every
## room_*.rpy sorts before this file and registers at init 0 or later.
##
## Three kinds of hotspot (4.10):
##   action      stands for a row of place_actions(place); it has no label,
##               hint or cost of its own, and exists only while that row does
##   look        carries its own lines; returns ("hot", id)
##   standalone  an action that is in no place_actions list (it needs `when`);
##               always drawn in front, never hidden by a person
## A hotspot is visible only while its 72 px square is clear of everyone
## standing in the room (view_person_rects); hidden, an action hotspot's
## action is back in the icon column.
################################################################################

init -5 python:
    import builtins
    import math as _hot_math
    import time as _hot_time

    HOT_SPOTS = []      # dicts, see register_hotspot
    MG_GAMES = []       # dicts, see register_minigame

    HOT_SIZE = 72                   # the square a hotspot takes
    HOT_RING = "gui/hot_ring.png"   # drawn by tools/gen_gui.py; a seal until then
    HOT_PULSE = 2.4                 # seconds for one pulse of the ring
    HOT_BOUNDS = (40, 180, 1700, 1000)      # x0, y0, x1, y1 a point must sit in
    ## The two lanes other things draw in over the place view (R6): the toast
    ## stack and the objective banner. (x, y, w, h). The toast lane runs to
    ## y 422: four two-line toasts end near y 416 (ui_hud.rpy).
    HOT_LANES = ((1330, 92, 460, 330), (400, 96, 900, 74))
    HOT_KEYS = ("id", "x", "y", "icon", "label", "hint", "cost", "act", "lines", "standalone", "front")

    ## The second UI overhaul (U0c2; docs/UI2_DESIGN.md 3.2, 7.3, 9.1). Every
    ## hotspot this overhaul will register, as (id, place, kind), frozen here
    ## so that a picture's layout can be made before the package that
    ## registers its hotspots has run: hot_validate accepts a sidecar point
    ## for a planned id. Wave 1 (U4; U5 for the baths and the pool) registers
    ## exactly these ids, in these places, as these kinds. The fifteen that
    ## exist today are not repeated (room_spots.rpy registers them); the card
    ## table keeps its id and only its point moves.
    ##   look   a thing to look at, with its own lines (the six bed tags
    ##          among them: each shows only while its owner is asleep there)
    ##   act    a place action that moves onto the object it belongs to, or a
    ##          new place's own action; the id after the comment is the
    ##          action it stands for
    SPOT_PLANNED = (
        ## Courtyard & Gate
        ("gate_pond",      "gate",            "look"),
        ("gateway",        "courtyard",       "look"),
        ("straw_posts",    "courtyard",       "act"),     # train ("Practice")
        ## School Building
        ("pine_bench",     "school_yard",     "look"),
        ("notices",        "classroom",       "look"),
        ("front_desk",     "classroom",       "act"),     # study
        ("water_cooler",   "cafeteria",       "look"),
        ("shoko_desk",     "infirmary",       "look"),
        ("reading_table",  "library",         "look"),
        ## Dormitories
        ("pond",           "dorm_yard",       "look"),
        ("lit_windows",    "dorm_yard",       "look"),    # at Night
        ("wardrobe",       "dorm",            "look"),
        ("window",         "dorm",            "look"),
        ("desk",           "dorm",            "act"),     # study
        ("fridge",         "dorm_common",     "look"),
        ("game_boxes",     "dorm_common",     "look"),
        ("manga_shelf",    "dorm_common",     "look"),
        ("plant",          "girls_dorm",      "look"),
        ("rooftop_view",   "rooftop",         "look"),
        ("railing",        "rooftop",         "act"),     # think ("Sit a while")
        ("shoe_rack",      "boys_dorm",       "look"),
        ("notice_board",   "boys_dorm",       "look"),
        ("film_shelf",     "yuji_room",       "look"),
        ("bed_yuji",       "yuji_room",       "look"),
        ("bookshelf",      "megumi_room",     "look"),
        ("bed_megumi",     "megumi_room",     "look"),
        ("shogi_board",    "senpai_room",     "look"),
        ("bed_panda",      "senpai_room",     "look"),
        ("bed_toge",       "senpai_room",     "look"),
        ("mirror",         "nobara_room",     "look"),
        ("bed_nobara",     "nobara_room",     "look"),
        ("weapon_case",    "maki_room",       "look"),
        ("bed_maki",       "maki_room",       "look"),
        ## Staff Building
        ("stone_lanterns", "staff_yard",      "look"),
        ("dolls",          "office",          "look"),
        ("photograph",     "office",          "look"),
        ("binders",        "utahime_office",  "look"),
        ("gojo_tv",        "gojo_office",     "look"),
        ("sweets",         "gojo_office",     "look"),
        ("rota",           "teachers_lounge", "look"),
        ("kettle",         "teachers_lounge", "look"),
        ("workbench",      "teachers_dorm",   "look"),
        ("name_plates",    "teachers_dorm",   "look"),
        ## Training Grounds
        ("striking_posts", "training_yard",   "act"),     # train
        ("mats",           "training",        "look"),
        ("straw_bundles",  "training",        "act"),     # train
        ("wall_shrine",    "dojo",            "look"),
        ("weapon_rack",    "dojo",            "act"),     # train
        ("big_chest",      "storehouse",      "look"),
        ("lane_board",     "pool",            "look"),
        ("pool_swim",      "pool",            "act"),     # pool_swim
        ## The Mountain
        ("standing_stone", "trailhead",       "look"),
        ("stone_markers",  "forest",          "look"),
        ("waterfall",      "riverside",       "look"),
        ("deep_pool",      "riverside",       "act"),     # swim
        ("milk_fridge",    "bathhouse",       "look"),
        ("bath_soak",      "bathhouse",       "act"),     # bath_soak
        ("bucket",         "sauna",           "look"),
        ("bath_sauna",     "sauna",           "act"),     # bath_sauna
    )

    ## hotspot id -> the NAME of a store function that says why the hotspot
    ## is spent for now (hot_set_dim). See hot_dim_reason.
    HOT_DIM = builtins.dict()

    ## How strongly a hotspot is drawn while it cannot be used: locked, shut
    ## by the night, or spent (hot_dim_reason).
    HOT_DIM_ALPHA = 0.45

    ## The faces on an exit's tile (hot_faces), and the plate a hotspot wears
    ## while names are shown: a plate is centred under its tile, and near the
    ## left or the right edge of the screen it lines up with the tile's own
    ## edge so that it stays on screen.
    HOT_FACE_SIZE = 30
    HOT_NAME_EDGE = 150

    ## The picture is what is clicked (D60; docs/UI2_DESIGN.md 7.3). One table
    ## for the limits both validators read (hot_validate here, and
    ## tools/check_layout.py: the dump carries it) and for the light's
    ## default look, which game/layout/hot_look.json may replace key by key
    ## (HOT_LOOK_KEYS: that file is how "stronger" and "weaker" are answered
    ## now that this file is final).
    ##   polys       the fewest and the most polygons a shape is made of
    ##   points      the fewest and the most points of a polygon
    ##   area_min    the smallest area of a shape, px2 (a button's square)
    ##   area_max    the most of the picture a shape may cover (two fifths)
    ##   buried_max  the most of a shape that may lie under smaller shapes
    ##   grid        the side of a cell, px: "two fifths" and "under smaller
    ##               shapes" are counted by cell centres (hot_shape_count)
    ##   color       the light's colour, "#rrggbb"
    ##   wash        how strongly the shape's inside is lit under the pointer
    ##   edge        how strongly its outline is drawn under the pointer
    ##   dim         what both are multiplied by for a shape that cannot be
    ##               used now (locked, shut by the night, spent)
    ##   names       what both are multiplied by for a shape that is lit
    ##               because names are shown, not because the pointer is on it
    ##   blur, line  the glow's softness and the outline's width, px
    HOT_SHAPE = builtins.dict(
        polys=(1, 3), points=(3, 60), area_min=HOT_SIZE * HOT_SIZE, area_max=0.4, buried_max=0.5, grid=4,
        color="#fff0cc", wash=0.30, edge=0.85, dim=0.4, names=0.5,
        blur=9, line=2)
    HOT_LOOK_KEYS = ("color", "wash", "edge", "dim", "names")
    HOT_LOOK_FILE = "hot_look"      # game/layout/hot_look.json

    ## A room's foreground cut-out covers what is behind it, and it is not a
    ## button: a back shape asks the cut-out's own pixels (hot_fg_covers).
    ## path -> the picture, read once; init data, never saved.
    HOT_FG_SEEN = builtins.dict()
    HOT_FG_ALPHA = 128      # from this opacity up the cut-out covers a point

    def register_hotspot(id, place, x, y, icon, act=None, lines=None, label="", hint="", cost=0, when=None, standalone=False, front=False):
        """P0 (sb_hotspots.rpy), final. Returns None. Registers a hotspot
        at (x, y) in a room, drawn as `icon`.

        act         an action hotspot: the place action it stands for (the
                    default kind when lines is None, with act = id)
        lines       a look hotspot: its first-person lines, one said a day
        standalone  an action in no place_actions list; it carries its own
                    label, hint and cost, and must carry `when`
        label, hint, cost   for a look or standalone hotspot only
        when        the NAME of a store function returning bool
        front       drawn in front of the people (a standalone always is)
        """
        row = builtins.dict(
            id=id, place=place, x=x, y=y, icon=icon, kind="act", act=act, lines=lines,
            label=label, hint=hint, cost=cost, when=when, standalone=bool(standalone),
            front=bool(front or standalone))
        if lines is not None:
            row["kind"] = "look"
            row["lines"] = builtins.list(lines)
        elif standalone:
            row["kind"] = "standalone"
        if row["kind"] != "look" and act is None:
            row["act"] = id
        HOT_SPOTS.append(row)

    def hot_set_dim(hot_id, fn):
        """U0c2 (sb_hotspots.rpy), final. Returns None. Names the dim
        function of a registered hotspot: `fn` is the NAME of a store
        function that takes nothing and returns a string, the reason the
        thing cannot be used for now ("The table's closed for today."), or
        "" when it can. While it returns a reason, screen hot_layer draws
        the hotspot at the dimmed strength, its hover label says the
        reason, and pressing it does nothing (7.3: the generic "spent"
        state; the card table's is U5's). It is separate from
        register_hotspot because that function's signature is frozen."""
        HOT_DIM[hot_id] = fn
        return None

    def hot_dim_reason(h):
        """U0c2. Why a hotspot is spent for now, a str; "" when it is not
        (it names no dim function, the function is missing, or it says
        "")."""
        name = HOT_DIM.get(h["id"])
        if not name:
            return ""
        fn = getattr(store, name, None)
        if not callable(fn):
            return ""
        why = fn()
        return why if isinstance(why, str) else ""

    def hot_planned(place=None):
        """U0c2. {id: (id, place, kind)} for the rows of SPOT_PLANNED, all
        of them or one place's."""
        return builtins.dict((r[0], r) for r in SPOT_PLANNED if place is None or r[1] == place)

    def hot_name(h):
        """U0c2. What a hotspot wears while names are shown: where an exit
        leads ("To the Dojo", locked or not), else the hotspot's own name."""
        act = str(h["act"] or "")
        if act.startswith("path_") and act[5:] in LOCATIONS:
            return path_words(act[5:])
        return h["label"] or icon_label(h["icon"])

    def hot_name_align(x):
        """U0c2. Where a name plate sits under a tile at x: 0.5 (centred),
        or 0.0 / 1.0 near the left / right edge of the screen."""
        if x < HOT_NAME_EDGE:
            return 0.0
        if x > config.screen_width - HOT_NAME_EDGE:
            return 1.0
        return 0.5

    def hot_faces(h):
        """U0c2. The people whose faces an exit's tile shows: path_faces(to)
        for an exit, three at most; [] for anything else. (path_faces is a
        stub in room_paths.rpy until U2 fills it: nobody.)"""
        act = str(h["act"] or "")
        if not act.startswith("path_"):
            return []
        return [w for w in path_faces(act[5:]) if w in CAST][:3]

    def register_minigame(id, name, icon, min_people=1):
        """P0 (sb_hotspots.rpy), final. Returns None. Registers a game for
        the card table: it plays as `label mg_<id>(opponents, stake=0)`."""
        MG_GAMES.append(builtins.dict(id=id, name=name, icon=icon, min_people=min_people))

    def mg_games():
        """P0 (sb_hotspots.rpy), final. The registered games, in order, as a
        list of dict copies (id, name, icon, min_people)."""
        return [builtins.dict(g) for g in MG_GAMES]

    ## What is visible -------------------------------------------------------------

    def hot_rect(x, y):
        """P0. The square a hotspot at (x, y) takes: (x, y, w, h)."""
        return (int(x) - HOT_SIZE // 2, int(y) - HOT_SIZE // 2, HOT_SIZE, HOT_SIZE)

    def hot_overlap(a, b):
        """P0. bool: two (x, y, w, h) rectangles overlap."""
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

    def hot_when(h):
        """P0. bool: the hotspot's `when` holds (always, when it has none)."""
        if not h["when"]:
            return True
        fn = getattr(store, h["when"], None)
        return bool(fn is not None and fn())

    def hot_spots_for(loc):
        """P0 (sb_hotspots.rpy), final. The hotspots visible in a room right
        now: a list of dicts with the keys id, x, y, icon, label, hint, cost,
        act, lines, standalone, front. The sidecar's point
        (game/layout/hot_<loc>.json) is applied, and an action hotspot
        takes its label, hint and cost from its place_actions row (4.10)."""
        rows = [h for h in HOT_SPOTS if h["place"] == loc]
        if not rows:
            return []
        acts = {}
        for a in place_actions(loc):
            acts.setdefault(a[0], a)
        people = view_person_rects(loc)
        points = rule_layout("hot_" + loc).get("spots") or {}
        out = []
        seen = builtins.set()
        for h in rows:
            if h["id"] in seen:
                continue                    # a duplicate id: lint reports it
            seen.add(h["id"])
            row = builtins.dict((k, h[k]) for k in HOT_KEYS)
            p = points.get(h["id"])
            if isinstance(p, (builtins.list, builtins.tuple)) and len(p) == 2 and hot_number(p[0]) and hot_number(p[1]):
                row["x"], row["y"] = p[0], p[1]
            if h["kind"] == "act":
                a = acts.get(h["act"])
                if a is None or night_blocks(h["act"]):
                    continue
                row["label"], row["hint"], row["cost"] = a[1], a[2], a[3]
            elif h["kind"] == "standalone":
                if store.explore_mode or not hot_when(h):
                    continue
            elif not hot_when(h):
                continue
            if h["kind"] != "standalone":
                r = hot_rect(row["x"], row["y"])
                if any(hot_overlap(r, p) for p in people):
                    continue
            if row["lines"] is not None:
                row["lines"] = builtins.list(row["lines"])
            out.append(row)
        return out

    def hot_covers(loc):
        """P0 (sb_hotspots.rpy), final. The set of place-action ids a visible
        action hotspot offers in this room right now."""
        if not HOT_SPOTS:
            return builtins.set()
        return builtins.set(h["act"] for h in hot_spots_for(loc)
                            if h["act"] and h["lines"] is None and not h["standalone"])

    def hot_line(hot_id):
        """P0. Today's line of a look hotspot (lines[day % len(lines)]), or
        None when there is no such look hotspot."""
        for h in HOT_SPOTS:
            if h["id"] == hot_id and h["lines"]:
                return h["lines"][store.day % len(h["lines"])]
        return None

    def hot_tip(h):
        """P0. A hotspot's hover label: "Train\\nPush my cursed energy. · 1 period"."""
        parts = [p for p in (h["hint"], ("%d period%s" % (h["cost"], "" if h["cost"] == 1 else "s")) if h["cost"] else "") if p]
        if not parts:
            return h["label"] or icon_label(h["icon"])
        return "%s\n%s" % (h["label"] or icon_label(h["icon"]), " · ".join(parts))

    def hot_open(h):
        """P0. bool: the hotspot can be used now (a look always can; an
        action when the night allows it)."""
        if h["lines"] is not None:
            return True
        return bool(night_allows(h["act"], h["cost"]))

    def hot_action(h):
        """P0. What a hotspot's button does: Return(("hot", id)) for a look,
        Return(("act", act)) for an action the night allows, else NullAction()."""
        if h["lines"] is not None:
            return Return(("hot", h["id"]))
        if hot_open(h):
            return Return(("act", h["act"]))
        return NullAction()

    def hot_ring():
        """P0. The ring under a hotspot: gui/hot_ring.png, or the seal until
        that file exists."""
        return HOT_RING if renpy.loadable(HOT_RING) else "gui/seal_44.png"

    def hot_pulse_fn(trans, st, at):
        """P0. The ring's pulse: alpha 0.45 to 0.8 over HOT_PULSE seconds, by
        the wall clock. Returns VIEW_TICK as the redraw delay, or None (and a
        still ring) when view_motion() is False. Top-level (R10)."""
        if not view_motion():
            trans.alpha = 0.8
            return None
        f = 0.5 + 0.5 * _hot_math.sin(_hot_time.time() * 2.0 * _hot_math.pi / HOT_PULSE)
        trans.alpha = 0.45 + 0.35 * f
        return VIEW_TICK

    ## The picture is what is clicked (D60; docs/UI2_DESIGN.md 7.3) ----------------
    ##
    ## In a place that has its new picture no button sits on the picture: each
    ## way out and each thing to do is a SHAPE, one to three polygons traced on
    ## the picture and written to game/layout/hot_<place>.json under "shapes".
    ## A place keeps its buttons until its picture is at revision 2 or later
    ## and its sidecar holds shapes and is not stale (hot_shapes_for).
    ##
    ## The functions between the two marker lines below are plain Python: they
    ## use nothing of Ren'Py and nothing of this file, so that
    ## tools/check_layout.py can carry the same text (or read it from here)
    ## and count exactly as the game's lint counts. The three test shapes of
    ## tools/smoke/hot_shape_cases.json are given to both.

    ## >>> hot_shape: plain Python, the same text in tools/check_layout.py (begin)
    import builtins     # list, dict and tuple are asked for by this name: Ren'Py's store has its own

    def hot_shape_num(v):
        """bool: v is a plain number."""
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def hot_shape_poly(v):
        """bool: v is a list of three or more [x, y] points of plain numbers."""
        return (isinstance(v, (builtins.list, builtins.tuple)) and len(v) >= 3
                and all(isinstance(p, (builtins.list, builtins.tuple)) and len(p) == 2 and hot_shape_num(p[0]) and hot_shape_num(p[1]) for p in v))

    def hot_shape_area(shape):
        """The area of a shape in px2: the shoelace sum of each of its
        polygons, added up."""
        total = 0.0
        for poly in shape:
            a = 0.0
            n = len(poly)
            for k in range(n):
                x1, y1 = poly[k][0], poly[k][1]
                x2, y2 = poly[(k + 1) % n][0], poly[(k + 1) % n][1]
                a += x1 * y2 - x2 * y1
            total += abs(a) / 2.0
        return total

    def hot_shape_box(shape):
        """(x, y, w, h): the whole-pixel box round a shape."""
        xs = [p[0] for poly in shape for p in poly]
        ys = [p[1] for poly in shape for p in poly]
        x0, y0 = int(min(xs) // 1), int(min(ys) // 1)
        x1, y1 = int(-((-max(xs)) // 1)), int(-((-max(ys)) // 1))
        return (x0, y0, max(1, x1 - x0), max(1, y1 - y0))

    def hot_shape_inside(shape, x, y):
        """bool: the point is inside one of the shape's polygons (even-odd;
        an edge belongs to the side below and to the right of it)."""
        for poly in shape:
            inside = False
            n = len(poly)
            for k in range(n):
                x1, y1 = poly[k][0], poly[k][1]
                x2, y2 = poly[(k + 1) % n][0], poly[(k + 1) % n][1]
                if (y1 <= y) != (y2 <= y) and x < x1 + (y - y1) * (x2 - x1) / float(y2 - y1):
                    inside = not inside
            if inside:
                return True
        return False

    def hot_shape_turn(a, b, c):
        """> 0, < 0 or 0: which way the path a, b, c turns."""
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return (v > 0) - (v < 0)

    def hot_shape_between(a, b, c):
        """bool: c, on the line through a and b, lies on the stretch a to b."""
        return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0])) and (min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))

    def hot_shape_meet(a, b, c, d):
        """bool: the stretches a-b and c-d touch or cross."""
        t1, t2 = hot_shape_turn(a, b, c), hot_shape_turn(a, b, d)
        t3, t4 = hot_shape_turn(c, d, a), hot_shape_turn(c, d, b)
        if t1 != t2 and t3 != t4:
            return True
        return ((t1 == 0 and hot_shape_between(a, b, c)) or (t2 == 0 and hot_shape_between(a, b, d))
                or (t3 == 0 and hot_shape_between(c, d, a)) or (t4 == 0 and hot_shape_between(c, d, b)))

    def hot_shape_crossed(poly):
        """bool: the polygon crosses or touches itself: two of its sides
        that are not neighbours meet, a point is given twice running, or a
        side folds straight back along the one before it."""
        n = len(poly)
        for k in range(n):
            a, b, c = poly[k], poly[(k + 1) % n], poly[(k + 2) % n]
            if a[0] == b[0] and a[1] == b[1]:
                return True
            if hot_shape_turn(a, b, c) == 0 and (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]) < 0:
                return True
        for k in range(n):
            for m in range(k + 2, n):
                if k == 0 and m == n - 1:
                    continue
                if hot_shape_meet(poly[k], poly[(k + 1) % n], poly[m], poly[(m + 1) % n]):
                    return True
        return False

    def hot_shape_cells(shape, size, grid):
        """(cells, twice): the grid cells whose CENTRE is inside the shape,
        as a frozenset of numbers (row * columns + column), and how many of
        them are inside two of its polygons at once. A cell is `grid` px
        square; the grid starts at the picture's top left corner and stops
        at its edges (`size`, (w, h))."""
        cols, rows = int(size[0] // grid), int(size[1] // grid)
        half = grid / 2.0
        seen = frozenset()
        twice = 0
        for poly in shape:
            cells = []
            n = len(poly)
            ys = [p[1] for p in poly]
            j0 = max(0, int((min(ys) - half) // grid))
            j1 = min(rows - 1, int((max(ys) - half) // grid) + 1)
            for j in range(j0, j1 + 1):
                cy = j * grid + half
                xs = []
                for k in range(n):
                    x1, y1 = poly[k][0], poly[k][1]
                    x2, y2 = poly[(k + 1) % n][0], poly[(k + 1) % n][1]
                    if (y1 <= cy) != (y2 <= cy):
                        xs.append(x1 + (cy - y1) * (x2 - x1) / float(y2 - y1))
                xs.sort()
                for k in range(0, len(xs) - 1, 2):
                    ## the centres cx = i * grid + half with xs[k] < cx <= xs[k + 1]
                    i0 = int((xs[k] - half) // grid) + 1
                    i1 = int((xs[k + 1] - half) // grid) + 1
                    for i in range(max(i0, 0), min(i1, cols)):
                        cells.append(j * cols + i)
            cells = frozenset(cells)
            twice += len(cells & seen)
            seen = seen | cells
        return seen, twice

    def hot_shape_order(shapes):
        """The ids of {id: shape}, the one on top first: the smaller shape
        is on top (by hot_shape_area), and of two of the same area the one
        whose id sorts first."""
        return [hid for _a, hid in sorted((hot_shape_area(shapes[hid]), hid) for hid in shapes)]

    def hot_shape_count(shapes, points, size, grid):
        """What the rules count, for the shapes of one place: {id: dict}.

          area     hot_shape_area, px2
          cells    how many grid cells have their centre inside the shape
          twice    how many of those are inside two of its own polygons
          buried   how many of those are also inside a shape that is on top
                   of it (hot_shape_order: a smaller one)
          point    its hotspot's point is inside it (True, False; None when
                   `points` has no point for it)
          under    the ids of the shapes on top of it that hold its point

        `shapes` is {id: [polygon, ...]}, every polygon well formed
        (hot_shape_poly); `points` is {id: (x, y)}. Two hotspots whose
        points are equal share a shape and are never offered together:
        nothing is read between the two (neither `buried` nor `under`)."""
        order = hot_shape_order(shapes)
        cells = {}
        out = {}
        for hid in order:
            got, twice = hot_shape_cells(shapes[hid], size, grid)
            cells[hid] = got
            pt = points.get(hid)
            out[hid] = {"area": hot_shape_area(shapes[hid]), "cells": len(got), "twice": twice, "buried": 0,
                        "point": (None if pt is None else hot_shape_inside(shapes[hid], pt[0], pt[1])), "under": []}
        for n, hid in enumerate(order):
            pt = points.get(hid)
            above = frozenset()
            for other in order[:n]:
                po = points.get(other)
                if pt is not None and po is not None and pt[0] == po[0] and pt[1] == po[1]:
                    continue
                above = above | cells[other]
                if pt is not None and hot_shape_inside(shapes[other], pt[0], pt[1]):
                    out[hid]["under"].append(other)
            out[hid]["buried"] = len(cells[hid] & above)
        return out

    def hot_shape_findings(place, shapes, keep, points, known, need, limits, size):
        """What is wrong with the shapes of one place: a list of sentences,
        each naming the id it is about; [] when nothing is.

          shapes   the sidecar's "shapes", as it was read
          keep     its "keep_tile" ({id: reason}), or None
          points   {id: (x, y)}: where each hotspot and exit of the place
                   sits (the sidecar's point, else the code's)
          known    the ids that may carry a shape: every hotspot and exit
                   registered in the place or planned for it
          need     the ids that must carry one, or be under keep_tile, once
                   the place holds any shape: `known` without a test
                   harness's own (ids that begin "zz")
          limits   the game's table of limits: polys, points, area_min,
                   area_max, buried_max, grid
          size     the picture's (w, h)
        """
        out = []
        where = " (hot_%s.json)" % place
        if not isinstance(shapes, builtins.dict):
            return ["shapes must be {\"<hotspot or exit id>\": [polygon, ...]}, a polygon being a list of [x, y]" + where]
        if keep is None:
            keep = {}
        if not isinstance(keep, builtins.dict):
            out.append("keep_tile must be {\"<hotspot or exit id>\": \"<why it keeps its button>\"}" + where)
            keep = {}
        p_lo, p_hi = limits["polys"]
        n_lo, n_hi = limits["points"]
        grid = limits["grid"]
        good = {}
        for hid in sorted(shapes):
            shape = shapes[hid]
            ok = True
            if hid not in known:
                out.append("shape %r: no hotspot or exit of that id is registered in %s, or planned for it%s" % (hid, place, where))
            if not (isinstance(shape, (builtins.list, builtins.tuple)) and p_lo <= len(shape) <= p_hi):
                out.append("shape %r: a shape is %d to %d polygons%s" % (hid, p_lo, p_hi, where))
                continue
            for n, poly in enumerate(shape):
                if not (isinstance(poly, (builtins.list, builtins.tuple)) and all(
                        isinstance(p, (builtins.list, builtins.tuple)) and len(p) == 2 and hot_shape_num(p[0]) and hot_shape_num(p[1]) for p in poly)):
                    out.append("shape %r: polygon %d is not a list of [x, y] points%s" % (hid, n + 1, where))
                    ok = False
                elif not (n_lo <= len(poly) <= n_hi):
                    out.append("shape %r: polygon %d has %d points (a polygon has %d to %d)%s" % (hid, n + 1, len(poly), n_lo, n_hi, where))
                    ok = False
                elif not all(0 <= p[0] <= size[0] and 0 <= p[1] <= size[1] for p in poly):
                    out.append("shape %r: polygon %d leaves the picture (%d x %d)%s" % (hid, n + 1, size[0], size[1], where))
                    ok = False
                elif hot_shape_crossed(poly):
                    out.append("shape %r: polygon %d crosses itself%s" % (hid, n + 1, where))
                    ok = False
            if ok:
                good[hid] = shape
        count = hot_shape_count(good, points, size, grid)
        for hid in sorted(good):
            c = count[hid]
            pt = points.get(hid)
            if c["twice"]:
                out.append("shape %r: two of its polygons overlap%s" % (hid, where))
            if c["area"] < limits["area_min"]:
                out.append("shape %r: its area is %d px2, smaller than a button (%d px2)%s" % (hid, c["area"], limits["area_min"], where))
            if c["cells"] * grid * grid > limits["area_max"] * size[0] * size[1]:
                out.append("shape %r: it covers %d%% of the picture (at most %d%%)%s"
                           % (hid, 100.0 * c["cells"] * grid * grid / (size[0] * size[1]), 100 * limits["area_max"], where))
            if hid in known and c["point"] is None:
                out.append("shape %r: its hotspot has no point (give it one under spots)%s" % (hid, where))
            elif c["point"] is False:
                out.append("shape %r: its hotspot's point (%d, %d) is outside its own shape%s" % (hid, pt[0], pt[1], where))
            for other in c["under"]:
                out.append("shape %r: its hotspot's point (%d, %d) is under the smaller shape %r%s" % (hid, pt[0], pt[1], other, where))
            if c["cells"] and c["buried"] > limits["buried_max"] * c["cells"]:
                out.append("shape %r: %d%% of it is under smaller shapes (at most %d%%)%s"
                           % (hid, 100.0 * c["buried"] / c["cells"], 100 * limits["buried_max"], where))
        for hid in sorted(keep):
            if hid not in known:
                out.append("keep_tile %r: no hotspot or exit of that id is registered in %s, or planned for it%s" % (hid, place, where))
            if not (isinstance(keep[hid], str) and keep[hid].strip()):
                out.append("keep_tile %r: it needs its reason, in words%s" % (hid, where))
            if hid in shapes:
                out.append("keep_tile %r: it has a shape as well (one or the other)%s" % (hid, where))
        if shapes:
            for hid in sorted(need):
                if hid not in shapes and hid not in keep:
                    out.append("%s is shaped, and %r has no shape and is not under keep_tile%s" % (place, hid, where))
        elif keep:
            out.append("keep_tile means nothing in a file that holds no shapes%s" % where)
        return out
    ## <<< hot_shape: plain Python, the same text in tools/check_layout.py (end)

    def hot_shape_size():
        """(w, h) of the picture a shape is traced on: the screen's."""
        return (config.screen_width, config.screen_height)

    def hot_shape_rows(loc):
        """D60. {hotspot id: (polygon, ...)} for a shaped place, each polygon
        a tuple of (x, y); {} for any other. The sidecar itself is read (it
        is not copied), and only what is well formed is kept: one to three
        polygons of three or more points of plain numbers. Lint reports the
        rest (hot_validate)."""
        name = "hot_" + str(loc)
        raw = rule_layout_raw(name)
        got = raw.get("shapes") if isinstance(raw, builtins.dict) else None
        if not got or not isinstance(got, builtins.dict):
            return builtins.dict()
        if art_rev(art_stem(loc)) < 2 or rule_layout_stale(name):
            return builtins.dict()
        out = builtins.dict()
        for hid, shape in got.items():
            if (isinstance(shape, (builtins.list, builtins.tuple)) and HOT_SHAPE["polys"][0] <= len(shape) <= HOT_SHAPE["polys"][1]
                    and all(hot_shape_poly(poly) for poly in shape)):
                out[str(hid)] = builtins.tuple(builtins.tuple((p[0], p[1]) for p in poly) for poly in shape)
        return out

    def hot_shapes_for(loc):
        """U0c2 (sb_hotspots.rpy), final. D60. {hotspot id: [polygon, ...]}
        for a shaped place, a polygon being a list of [x, y]; {} for a place
        that is not shaped. A place is shaped when its sidecar
        game/layout/hot_<loc>.json holds "shapes", the file is not stale
        (its for_rev, if it carries one, is its picture's revision) and its
        picture is at revision 2 or later: art_rev of the file stem of
        LOCATIONS[loc]["bg"], which is "your_room" for "dorm". An exit's id
        is "go_<from>__<to>". Each call returns a fresh copy."""
        return builtins.dict((hid, [[[p[0], p[1]] for p in poly] for poly in shape])
                             for hid, shape in hot_shape_rows(loc).items())

    def hot_keep_tile(loc):
        """D60. {hotspot id: reason}: the few hotspots of a place that keep
        their button once it is shaped (the sidecar's "keep_tile"); {} when
        it names none. (Any visible hotspot with no shape is drawn as its
        button; this is the list lint asks a reason for.)"""
        got = rule_layout("hot_" + str(loc)).get("keep_tile")
        if not isinstance(got, builtins.dict):
            return builtins.dict()
        return builtins.dict((str(k), v) for k, v in got.items() if isinstance(v, str))

    def hot_colour(v):
        """bool: v is "#rrggbb"."""
        if not (isinstance(v, str) and len(v) == 7 and v[0] == "#"):
            return False
        return all(c in "0123456789abcdefABCDEF" for c in v[1:])

    def hot_look():
        """D60. The light's look: a dict with the keys of HOT_LOOK_KEYS
        (color, wash, edge, dim, names), HOT_SHAPE's values unless
        game/layout/hot_look.json gives another. A value that is not a
        colour, or not a number from 0 to 1, is left out (lint reports
        it)."""
        out = builtins.dict((k, HOT_SHAPE[k]) for k in HOT_LOOK_KEYS)
        raw = rule_layout_raw(HOT_LOOK_FILE)
        for k in HOT_LOOK_KEYS:
            if k in raw:
                v = raw[k]
                if (hot_colour(v) if k == "color" else (hot_number(v) and 0 <= v <= 1)):
                    out[k] = v
        return out

    def hot_look_findings():
        """D60. Lint findings for game/layout/hot_look.json."""
        out = []
        raw = rule_layout_raw(HOT_LOOK_FILE)
        for k in builtins.sorted(raw):
            v = raw[k]
            if k not in HOT_LOOK_KEYS:
                out.append("hot_look.json: unknown key %r (the keys are %s)" % (k, ", ".join(HOT_LOOK_KEYS)))
            elif k == "color":
                if not hot_colour(v):
                    out.append("hot_look.json: color must be \"#rrggbb\"")
            elif not (hot_number(v) and 0 <= v <= 1):
                out.append("hot_look.json: %s must be a number from 0 to 1" % k)
        return out

    def hot_place_points(place):
        """D60. {id: (x, y)}: where each hotspot and exit registered in a
        place sits (the sidecar's point, else the code's), and the
        sidecar's point for an id that is only planned. Whether a hotspot
        shows this hour does not matter."""
        side = rule_layout("hot_" + str(place)).get("spots")
        if not isinstance(side, builtins.dict):
            side = builtins.dict()
        out = builtins.dict()
        ids = [h["id"] for h in HOT_SPOTS if h["place"] == place]
        for h in HOT_SPOTS:
            if h["place"] == place and h["id"] not in out and hot_number(h["x"]) and hot_number(h["y"]):
                out[h["id"]] = (h["x"], h["y"])
        for hid in ids + builtins.list(hot_planned(place)):
            p = side.get(hid)
            if isinstance(p, (builtins.list, builtins.tuple)) and len(p) == 2 and hot_number(p[0]) and hot_number(p[1]):
                out[hid] = (p[0], p[1])
        return out

    def hot_shape_validate(place):
        """D60. Lint findings for the shapes of one place's sidecar (7.3,
        "The rules"); [] for a sidecar that holds neither "shapes" nor
        "keep_tile". The rules are read whatever the picture's revision:
        the shapes of a room redone in place wait in its file."""
        data = rule_layout("hot_" + str(place))
        if "shapes" not in data and "keep_tile" not in data:
            return []
        known = builtins.set(h["id"] for h in HOT_SPOTS if h["place"] == place) | builtins.set(hot_planned(place))
        need = builtins.set(hid for hid in known if not str(hid).startswith("zz"))
        return hot_shape_findings(place, data.get("shapes", builtins.dict()), data.get("keep_tile"), hot_place_points(place),
                                  known, need, HOT_SHAPE, hot_shape_size())

    ## Drawing a shaped place (D60) --------------------------------------------------

    class hot_ShapeLight(renpy.Displayable):
        """D60. One part of a shaped hotspot's light, drawn from its polygons
        when it is asked for: no picture file is made and nothing moves.
        `part` is "wash" (the polygons filled) or "line" (their outlines,
        `width` px wide). It is drawn on a canvas `pad` px larger than the
        shape's box on every side, because a blur stops at its displayable's
        border. A plain top-level class holding plain values, so that an
        instance pickles (R10)."""

        def __init__(self, shape, box, pad, part, color, width=0, **properties):
            super(hot_ShapeLight, self).__init__(**properties)
            self.shape = shape
            self.box = box
            self.pad = pad
            self.part = part
            self.color = color
            self.width = width

        def __eq__(self, other):
            return (type(other) is hot_ShapeLight and self.shape == other.shape and self.box == other.box and self.pad == other.pad
                    and self.part == other.part and self.color == other.color and self.width == other.width)

        def __ne__(self, other):
            return not (self == other)

        def __hash__(self):
            return hash((self.shape, self.box, self.pad, self.part, self.color, self.width))

        def render(self, width, height, st, at):
            x0, y0, w, h = self.box
            pad = self.pad
            rv = renpy.Render(w + 2 * pad, h + 2 * pad)
            canvas = rv.canvas()
            for poly in self.shape:
                pts = [(int(round(p[0] - x0 + pad)), int(round(p[1] - y0 + pad))) for p in poly]
                if self.part == "wash":
                    canvas.polygon(self.color, pts)
                else:
                    canvas.lines(self.color, True, pts, self.width)
                    for p in pts:
                        canvas.circle(self.color, p, max(1, self.width // 2))
            return rv

    def hot_light_pad():
        """D60. How far a light's canvas reaches beyond its shape's box."""
        return int(2 * HOT_SHAPE["blur"] + HOT_SHAPE["line"] + 4)

    def hot_light(shape, part, strength):
        """D60. One layer of a shape's light, a new displayable each call
        (build it in the line that uses it, R10). Three layers make the
        light, drawn in this order at the shape's box less hot_light_pad():

          "dark"  a soft dark rim along the outline, so that the light
                  shows on a white wall
          "glow"  the warm wash inside the outline, soft at its edge and
                  ADDED to the picture, so that it reads as light
          "line"  the outline itself, in the light's colour

        The blur is the inner transform and the adding is the outer one: an
        additive picture shows only when it is drawn straight onto the
        opaque picture. `strength` is 1.0 under the pointer (hot_strength).
        No function transform: a lit shape is still."""
        look = hot_look()
        box = hot_shape_box(shape)
        pad = hot_light_pad()
        line = HOT_SHAPE["line"]
        if part == "glow":
            return Transform(Transform(hot_ShapeLight(shape, box, pad, "wash", look["color"]), blur=HOT_SHAPE["blur"]),
                             additive=1.0, alpha=look["wash"] * strength)
        if part == "dark":
            return Transform(Transform(hot_ShapeLight(shape, box, pad, "line", "#0b0a10", line + 4), blur=3.0),
                             alpha=min(1.0, 0.75 * look["edge"] * strength))
        return Transform(Transform(hot_ShapeLight(shape, box, pad, "line", look["color"], line), blur=1.0),
                         alpha=look["edge"] * strength)

    def hot_fg_covers(path, x, y):
        """D60. bool: the room's foreground cut-out (the picture `path`,
        laid over the whole room) covers the point: a back shape takes no
        click there, as a button behind the cut-out would be covered by it.
        The picture is read once."""
        if path not in HOT_FG_SEEN:
            try:
                HOT_FG_SEEN[path] = renpy.load_surface(path)
            except Exception:
                HOT_FG_SEEN[path] = None
        surf = HOT_FG_SEEN[path]
        if surf is None:
            return False
        w, h = surf.get_size()
        x, y = int(x), int(y)
        if not (0 <= x < w and 0 <= y < h):
            return False
        return surf.get_at((x, y))[3] >= HOT_FG_ALPHA

    def hot_shape_hit(shape, box, fg, x, y):
        """D60. The focus test of a shape's button (its focus_mask, curried
        with the first three: a top-level function, so that it pickles).
        (x, y) is a point in the button's own box. True inside one of the
        shape's polygons, unless the room's foreground cut-out `fg` (a back
        shape's; None for a front one) covers the point."""
        px, py = x + box[0], y + box[1]
        if not hot_shape_inside(shape, px, py):
            return False
        return not (fg and hot_fg_covers(fg, px, py))

    def hot_no_point(x, y):
        """D60. The focus test of a shaped hotspot's square: it refuses
        every point. The square is there for the keyboard, for
        renpy.set_focus and for the rules; the pointer's is the shape."""
        return False

    def hot_tip_id(key):
        """D60. The hotspot id a tooltip key belongs to: "hot_<id>" (the
        square, or a button) and "hotshape_<id>" (the shape) both answer
        <id>; None for any other key."""
        key = str(key)
        if key.startswith("hotshape_"):
            return key[len("hotshape_"):]
        if key.startswith("hot_"):
            return key[len("hot_"):]
        return None

    def hot_lit_id():
        """D60. The id of the hotspot whose tooltip is in force, under
        either of its keys, or None. A shape is lit by this and never by its
        own button's hover state, so it lights from the keyboard and from
        renpy.set_focus as it does under the pointer."""
        tip = GetTooltip()
        if isinstance(tip, builtins.tuple) and len(tip) == 2:
            return hot_tip_id(tip[1])
        return None

    def hot_shaped_row(key):
        """D60. The hot_spots_for row of the shaped hotspot a tooltip key
        belongs to, in the place I stand in; None for any other key, for a
        hotspot that has no shape and for one that is not showing."""
        hid = hot_tip_id(key)
        if hid is None or store.here not in LOCATIONS or hid not in hot_shape_rows(store.here):
            return None
        for h in hot_spots_for(store.here):
            if h["id"] == hid:
                return h
        return None

    def hot_tip_rect(key):
        """U0c2 (sb_hotspots.rpy), final. D60. (x, y, w, h): the 72 px
        square at a shaped hotspot's point, for either of its tooltip keys,
        "hot_<id>" (the square) and "hotshape_<id>" (the shape); None for
        any other key. The hover label opens against this square whichever
        of the two has the focus (screen hover_label)."""
        h = hot_shaped_row(key)
        return None if h is None else hot_rect(h["x"], h["y"])

    def hot_tip_faces(key):
        """D60. The people whose faces the hover label draws beside a
        shaped exit's name (hot_faces: the people inside the house it leads
        to); [] for any other key. An exit that still has its button shows
        them on its tile instead."""
        h = hot_shaped_row(key)
        return [] if h is None else hot_faces(h)

    def hot_strength(hid, lit, names, dim):
        """D60. How strongly a shape is lit now: 1.0 under the pointer (the
        tooltip in force is its hotspot's), HOT_SHAPE's "names" while names
        are shown and it is not, else 0.0 (not drawn); times "dim" for one
        that cannot be used now."""
        look = hot_look()
        s = 1.0 if lit == hid else (look["names"] if names else 0.0)
        return s * (look["dim"] if dim else 1.0)

    def hot_layer_rows(loc, front, shapes):
        """D60. The rows hot_layer draws in one layer, in drawing order: the
        shaped ones first, the largest shape first, so that the smaller is
        on top (hot_shape_order); then every hotspot with no shape, which is
        drawn as its button above the shapes."""
        rows = [h for h in hot_spots_for(loc) if bool(h["front"]) == bool(front)]
        if not shapes:
            return rows
        order = hot_shape_order(builtins.dict((h["id"], shapes[h["id"]]) for h in rows if h["id"] in shapes))
        by = builtins.dict((h["id"], h) for h in rows)
        return [by[hid] for hid in reversed(order)] + [h for h in rows if h["id"] not in shapes]

    def hot_name_rect(h):
        """D60. (x, y, w, h): where a shaped hotspot's name plate is drawn
        while names are shown: against the 72 px square at its point, on
        the side its hover label opens on (icon_tip_side: the sidecar's
        "tips", else the table), its left edge on the square's when it is
        above or below and its top on the square's when it is beside it, as
        the hover label lies; on the other side when it would leave the
        screen. `h` is a hot_spots_for row."""
        name = hot_name(h)
        faces = len(hot_faces(h))
        tw, th = Text(name, style="hot_name_text", substitute=False).size(220, config.screen_height)
        w = int(tw) + 16 + (faces * (HOT_FACE_SIZE + 2) + 6 if faces else 0)
        hh = max(int(th) + 5, (HOT_FACE_SIZE + 5) if faces else 0)
        sx, sy, sw, sh = hot_rect(h["x"], h["y"])
        side = icon_tip_side((name, "hot_" + str(h["id"])))
        if side == "left" and sx - w < 0:
            side = "right"
        elif side == "right" and sx + sw + w > config.screen_width:
            side = "left"
        elif side == "top" and sy - hh < 0:
            side = "bottom"
        elif side == "bottom" and sy + sh + hh > config.screen_height:
            side = "top"
        if side == "left":
            x, y = sx - w, sy
        elif side == "right":
            x, y = sx + sw, sy
        else:
            x = max(0, min(sx, config.screen_width - w))
            y = sy - hh if side == "top" else sy + sh
        return (x, y, w, hh)

    ## The validator (4.10) --------------------------------------------------------

    def hot_point_findings(h, x, y, where=""):
        """P0. Lint findings for one hotspot's point: inside HOT_BOUNDS,
        clear of the toast and banner lanes (R6) and, for a standalone,
        clear of where people stand by default. `where` names the source
        when it is not the registered point (" (sidecar hot_dorm.json)")."""
        out = []
        hid = h["id"]
        x0, y0, x1, y1 = HOT_BOUNDS
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            out.append("hotspot %r: (%d, %d) is outside x %d to %d, y %d to %d%s" % (hid, x, y, x0, x1, y0, y1, where))
        r = hot_rect(x, y)
        if any(hot_overlap(r, lane) for lane in HOT_LANES):
            out.append("hotspot %r: (%d, %d) sits in the toast lane or the banner lane%s" % (hid, x, y, where))
        if h["kind"] == "standalone" and h["place"] in LOCATIONS:
            ## It has no column row to fall back to: keep it clear of
            ## where one to four people stand by default.
            for n in (1, 2, 3, 4):
                if any(hot_overlap(r, p) for p in view_slot_rects(h["place"], n)):
                    out.append("hotspot %r: (%d, %d) is where someone stands with %d in the room%s" % (hid, x, y, n, where))
                    break
        return out

    def hot_number(v):
        """P0. bool: v is a plain number (a sidecar's JSON may hold anything)."""
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def hot_validate():
        """P0 (sb_hotspots.rpy). Lint findings for the hotspot and minigame
        registries, a duplicate id among them (R2), and for the points the
        sidecars game/layout/hot_<place>.json put in their place (D5): the
        sidecar is where the final positions live, so its points pass the
        same tests as the registered ones."""
        out = []
        seen = builtins.set()
        for h in HOT_SPOTS:
            hid = h["id"]
            if hid in seen:
                out.append("hotspot %r is registered twice" % hid)
            seen.add(hid)
            if h["place"] not in LOCATIONS:
                out.append("hotspot %r: %r is not a place" % (hid, h["place"]))
            if h["icon"] not in ICONS:
                out.append("hotspot %r: unknown icon %r" % (hid, h["icon"]))
            if h["when"] and not callable(getattr(store, h["when"], None)):
                out.append("hotspot %r: when=%r is not a store function" % (hid, h["when"]))
            if h["kind"] == "look":
                if not h["lines"] or not all(isinstance(l, str) and l for l in h["lines"]):
                    out.append("hotspot %r: a look hotspot needs at least one line" % hid)
                if h["standalone"] or h["act"] is not None:
                    out.append("hotspot %r: a look hotspot is neither standalone nor an action" % hid)
            else:
                if not renpy.has_label("sb_do_" + str(h["act"])):
                    out.append("hotspot %r has no label sb_do_%s" % (hid, h["act"]))
            if h["kind"] == "act" and (h["label"] or h["hint"] or h["cost"]):
                out.append("hotspot %r: an action hotspot takes its label, hint and cost from its action" % hid)
            if h["kind"] == "standalone" and not h["when"]:
                out.append("hotspot %r: a standalone hotspot needs `when`" % hid)
            try:
                x, y = int(h["x"]), int(h["y"])
            except Exception:
                out.append("hotspot %r: its point is not two numbers" % hid)
                continue
            out.extend(hot_point_findings(h, x, y))
        ## The sidecars: hot_spots_for() draws a hotspot at the sidecar's point.
        for place in builtins.sorted(builtins.set(h["place"] for h in HOT_SPOTS) | builtins.set(LOCATIONS)):
            data = rule_layout("hot_" + str(place))
            if not data:
                continue
            where = " (sidecar hot_%s.json)" % place
            spots = data.get("spots")
            if not isinstance(spots, builtins.dict):
                out.append("hot_%s.json: it must hold {\"spots\": {\"<hotspot id>\": [x, y]}}" % place)
                continue
            rows = builtins.dict()
            for h in HOT_SPOTS:
                if h["place"] == place:
                    rows.setdefault(h["id"], h)
            ## U0c2: a point for a hotspot that is planned for this place
            ## (SPOT_PLANNED) and not registered yet is accepted, and passes
            ## the same tests; a point for an id that is neither is refused.
            for hid, row in hot_planned(place).items():
                rows.setdefault(hid, builtins.dict(id=hid, place=place, kind=row[2]))
            for hid in builtins.sorted(spots):
                pt = spots[hid]
                if hid not in rows:
                    out.append("hotspot %r: no hotspot of that id is registered in %s, or planned for it%s" % (hid, place, where))
                elif not (isinstance(pt, (builtins.list, builtins.tuple)) and len(pt) == 2
                          and hot_number(pt[0]) and hot_number(pt[1])):
                    out.append("hotspot %r: its point is not two numbers%s" % (hid, where))
                else:
                    out.extend(hot_point_findings(rows[hid], int(pt[0]), int(pt[1]), where))
        ## U0c2 (D60): the shapes, place by place, and the light's look.
        for place in builtins.sorted(LOCATIONS):
            out.extend(hot_shape_validate(place))
        out.extend(hot_look_findings())
        ## U0c2: the planned ids, and the dim functions.
        seen = builtins.set()
        for row in SPOT_PLANNED:
            if not (isinstance(row, builtins.tuple) and len(row) == 3 and row[2] in ("look", "act", "standalone")):
                out.append("SPOT_PLANNED: %r must be (id, place, \"look\", \"act\" or \"standalone\")" % (row,))
                continue
            if row[0] in seen:
                out.append("SPOT_PLANNED: %r is planned twice" % (row[0],))
            seen.add(row[0])
            if row[1] not in LOCATIONS:
                out.append("SPOT_PLANNED %r: %r is not a place" % (row[0], row[1]))
            for h in HOT_SPOTS:
                if h["id"] == row[0] and (h["place"] != row[1] or h["kind"] != row[2]):
                    out.append("hotspot %r is registered in %s as %s, and planned for %s as %s"
                               % (row[0], h["place"], h["kind"], row[1], row[2]))
        known = builtins.set(h["id"] for h in HOT_SPOTS) | seen
        for hid, name in builtins.sorted(HOT_DIM.items()):
            if hid not in known:
                out.append("hot_set_dim: %r is not a registered or planned hotspot" % (hid,))
            if not callable(getattr(store, str(name), None)):
                out.append("hot_set_dim %r: %r is not a store function" % (hid, name))
        seen = builtins.set()
        for g in MG_GAMES:
            if g["id"] in seen:
                out.append("minigame %r is registered twice" % g["id"])
            seen.add(g["id"])
            if not renpy.has_label("mg_" + str(g["id"])):
                out.append("minigame %r has no label mg_%s" % (g["id"], g["id"]))
            if g["icon"] not in ICONS:
                out.append("minigame %r: unknown icon %r" % (g["id"], g["icon"]))
        return out

    register_validator(hot_validate)


## The hotspots of a room (4.10). `front=False` is the layer behind the people,
## `front=True` the one in front. Each is a 72 px icon button on a pulsing
## ring; its returns go through the screen that uses it (sb_place).
##
## The second overhaul (U0c2; 7.3, D36):
##   - a hotspot may be spent for now (hot_set_dim): it is drawn at the dimmed
##     strength, as a locked exit and an action the night has closed are, its
##     hover label says why, and pressing it does nothing;
##   - while names are shown (icon_names_shown: the setting, or N held) an
##     exit wears where it leads and a hotspot its name, on a small plate
##     under its tile;
##   - an exit's tile shows the faces of the people inside the house it leads
##     to (hot_faces; nobody until U2 fills path_faces).
## The names key is listened for here, once (the back layer), so it is live
## exactly where there are names to show.
##
## The picture is what is clicked (U0c2, second sitting; D60, 7.3). In a
## SHAPED place (hot_shapes_for answers) a hotspot that has a shape draws no
## ring and no icon:
##   - its 72 px square stays at its point, inside today's alpha wrapper, with
##     its id hot_<id>, its action and its hover label under the key hot_<id>;
##     it is empty and its focus mask refuses every point (hot_no_point), so it
##     is the keyboard's and renpy.set_focus's, never the pointer's;
##   - its shape is a second focus area, hotshape_<id>, over the same action,
##     with the same words under the tooltip key hotshape_<id>; the keyboard
##     skips it; its focus test is the polygons themselves (hot_shape_hit);
##   - the shape is lit whenever the tooltip in force is its hotspot's under
##     either key (hot_lit_id), at full strength; at the "dim" strength when it
##     cannot be used now; and every shape is lit at the "names" strength,
##     with its name on a plate against its square, while names are shown;
##   - within a layer the smaller shape is drawn last, so it is on top; a back
##     shape is under the people, under a painted pose's box and (by its focus
##     test) under the room's foreground cut-out;
##   - a visible hotspot with no shape (a keep_tile row, a harness's own) is
##     drawn as its button, exactly as in a place with buttons, above the
##     shapes.
## No function transform is added: a shaped hotspot has no ring to pulse.
style hot_name_frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (8, 2, 8, 3)

## A shaped hotspot's two focus areas (D60): the shape, and the empty square.
## Neither draws anything.
style hot_shape_button is default:
    background None
    hover_background None
    padding (0, 0, 0, 0)
    margin (0, 0, 0, 0)

style hot_name_text is text:
    font gui.body_medium_font
    color gui.paper
    size 16
    text_align 0.5

screen hot_layer(loc, front=False):
    $ _hot_names = icon_names_shown()
    if not front:
        key ("keydown_" + ICON_NAMES_KEY) action Function(ui_do, icon_names_hold, True)
        key ("keyup_" + ICON_NAMES_KEY) action Function(ui_do, icon_names_hold, False)
    ## D60: the place's shapes ({} for a place that keeps its buttons), the
    ## hotspot whose tooltip is in force, and what covers a back shape.
    $ _hot_shapes = hot_shape_rows(loc)
    $ _hot_lit = hot_lit_id() if _hot_shapes else None
    $ _hot_fg = view_fg_path(loc) if (_hot_shapes and not front) else None
    $ _hot_pad = hot_light_pad()
    for _hot_h in hot_layer_rows(loc, front, _hot_shapes):
        $ _hot_ok = hot_open(_hot_h)
        $ _hot_lock = path_locked(_hot_h["act"][5:]) if str(_hot_h["act"]).startswith("path_") else ""
        $ _hot_dim = hot_dim_reason(_hot_h)
        $ _hot_faces = hot_faces(_hot_h)
        if _hot_h["id"] in _hot_shapes:
            ## A shaped hotspot (D60): nothing is drawn until it is lit. The
            ## light, then the shape's own focus area, then the square.
            $ _hot_shape = _hot_shapes[_hot_h["id"]]
            $ _hot_box = hot_shape_box(_hot_shape)
            $ _hot_off = bool(_hot_lock or _hot_dim or not _hot_ok)
            $ _hot_str = hot_strength(_hot_h["id"], _hot_lit, _hot_names, _hot_off)
            $ _hot_say = (_hot_dim or (hot_tip(_hot_h) if _hot_ok else "Too late. Bed."))
            if _hot_str > 0:
                add hot_light(_hot_shape, "dark", _hot_str) pos (_hot_box[0] - _hot_pad, _hot_box[1] - _hot_pad)
                add hot_light(_hot_shape, "glow", _hot_str) pos (_hot_box[0] - _hot_pad, _hot_box[1] - _hot_pad)
                add hot_light(_hot_shape, "line", _hot_str) pos (_hot_box[0] - _hot_pad, _hot_box[1] - _hot_pad)
            button:
                id "hotshape_" + _hot_h["id"]
                style "hot_shape_button"
                pos (_hot_box[0], _hot_box[1])
                xysize (_hot_box[2], _hot_box[3])
                focus_mask renpy.partial(hot_shape_hit, _hot_shape, _hot_box, _hot_fg)
                keyboard_focus False
                action (NullAction() if (_hot_lock or _hot_dim) else hot_action(_hot_h))
                tooltip (_hot_say, "hotshape_" + _hot_h["id"])
                null
            fixed:
                pos (int(_hot_h["x"]) - 48, int(_hot_h["y"]) - 48)
                xysize (96, 96)
                fixed at Transform(alpha=(1.0 if (_hot_ok and not _hot_lock and not _hot_dim) else HOT_DIM_ALPHA)):
                    pos (12, 12)
                    xysize (72, 72)
                    button:
                        id "hot_" + _hot_h["id"]
                        style "hot_shape_button"
                        xysize (72, 72)
                        focus_mask hot_no_point
                        action (NullAction() if (_hot_lock or _hot_dim) else hot_action(_hot_h))
                        tooltip (_hot_say, "hot_" + _hot_h["id"])
                        null
            if _hot_names:
                $ _hot_nr = hot_name_rect(_hot_h)
                frame:
                    style "hot_name_frame"
                    pos (_hot_nr[0], _hot_nr[1])
                    hbox:
                        spacing 6
                        text hot_name(_hot_h):
                            style "hot_name_text"
                            substitute False
                            xmaximum 220
                            yalign 0.5
                        if _hot_faces:
                            hbox:
                                spacing 2
                                yalign 0.5
                                for _hot_w in _hot_faces:
                                    add face_chip(_hot_w, HOT_FACE_SIZE)
        else:
            fixed:
                pos (int(_hot_h["x"]) - 48, int(_hot_h["y"]) - 48)
                xysize (96, 96)
                add Transform(hot_ring(), xysize=(96, 96), function=hot_pulse_fn)
                fixed at Transform(alpha=(1.0 if (_hot_ok and not _hot_lock and not _hot_dim) else HOT_DIM_ALPHA)):
                    pos (12, 12)
                    xysize (72, 72)
                    use icon_btn(_hot_h["icon"], (NullAction() if (_hot_lock or _hot_dim) else hot_action(_hot_h)),
                                 tip=(_hot_dim or (hot_tip(_hot_h) if _hot_ok else "Too late. Bed.")),
                                 size=60, w=72, wid="hot_" + _hot_h["id"], words="never")
                if _hot_faces:
                    hbox:
                        xalign 1.0
                        ypos -6
                        spacing 2
                        for _hot_w in _hot_faces:
                            add face_chip(_hot_w, HOT_FACE_SIZE)
                if _hot_names:
                    frame:
                        style "hot_name_frame"
                        xalign hot_name_align(_hot_h["x"])
                        ypos 90
                        text hot_name(_hot_h):
                            style "hot_name_text"
                            substitute False
                            xmaximum 220


## A look hotspot (4.10): says today's line and notes that it was used today.
## The loop's `elif _r[0] == "hot"` calls it.
label hot_use(hot_id):
    $ _hot_line = hot_line(hot_id)
    if _hot_line is None:
        return
    $ renpy.say(None, _hot_line)
    $ actions_today.add("hot:" + hot_id)
    return


default mg_result = {}      # the last game's dict(game, outcome, yen)
