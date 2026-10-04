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
            for hid in builtins.sorted(spots):
                pt = spots[hid]
                if hid not in rows:
                    out.append("hotspot %r: no hotspot of that id is registered in %s%s" % (hid, place, where))
                elif not (isinstance(pt, (builtins.list, builtins.tuple)) and len(pt) == 2
                          and hot_number(pt[0]) and hot_number(pt[1])):
                    out.append("hotspot %r: its point is not two numbers%s" % (hid, where))
                else:
                    out.extend(hot_point_findings(rows[hid], int(pt[0]), int(pt[1]), where))
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
screen hot_layer(loc, front=False):
    for _hot_h in hot_spots_for(loc):
        if bool(_hot_h["front"]) == bool(front):
            $ _hot_ok = hot_open(_hot_h)
            $ _hot_lock = path_locked(_hot_h["act"][5:]) if str(_hot_h["act"]).startswith("path_") else ""
            fixed:
                pos (int(_hot_h["x"]) - 48, int(_hot_h["y"]) - 48)
                xysize (96, 96)
                add Transform(hot_ring(), xysize=(96, 96), function=hot_pulse_fn)
                fixed at Transform(alpha=(1.0 if (_hot_ok and not _hot_lock) else 0.45)):
                    pos (12, 12)
                    xysize (72, 72)
                    use icon_btn(_hot_h["icon"], (NullAction() if _hot_lock else hot_action(_hot_h)),
                                 tip=(hot_tip(_hot_h) if _hot_ok else "Too late. Bed."),
                                 size=60, w=72, wid="hot_" + _hot_h["id"], words="never")


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
