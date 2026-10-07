################################################################################
## Cursed Bonds — the stage: the people standing in a room.
##
## Phase 2 (PHASE2_DESIGN.md 4.5, D17, D35 to D39, 6.1). P0 moved the stage
## here from sb_screens.rpy; P5 made it live.
##
##   screen view_stage(loc)   the people in a room (sprites, or a painted pose);
##                            returns ("char", who) through sb_place
##   screen view_fg(loc)      the foreground picture, then the name tags over it
##                            (sb_place uses it straight after view_stage, so the
##                            tags are above the table edge that hides the feet)
##   screen view_tags(loc)    the name tags: a short name, 「!」 and NEW
##   screen view_focus(who)   the person, eased in from where they stood, in
##                            the person view
##   VIEW_TICK, view_motion() the redraw delay of every looping transform, and
##                            the Preferences "Motion" switch (persistent.motion)
##   view_slots(loc, n)       where n people stand: (xcenter, yoffset, zoom, far)
##   view_person_rects(loc)   where people stand now, as rectangles (hotspots
##                            stay out from behind them)
##   view_pose(who, loc)      a painted pose, images/place/pose_<loc>__<who>.png
##   view_floor(loc), view_talk(loc), view_slot_light(...), view_cast(loc)
##                            the room's own data (the second overhaul, U0c2:
##                            docs/UI2_DESIGN.md 6.1), read from the sidecar
##                            game/layout/view_<loc>.json; every key is
##                            optional and without it the room is as before
##   view_blink_also(who), view_face_box(who, key)
##                            a person's blink faces and their eye and mouth
##                            boxes: game/layout/faces.json first, then the
##                            tables here (D57)
##   view_sync_light, view_before_person, view_after_scene, view_enter
##                            the loop's hooks: the light, and idle to talking
##
## What a save may hold (R10): view_enter shows the sprite with the ATL
## transform view_enter_ease and the foreground as a plain picture; every
## looping function here is top-level and curried. Nothing in a screen is kept
## in a variable except plain values (a pose is a dict of a path and a box).
################################################################################

default persistent.motion = True

init -2 python:
    import builtins
    import math as view_math
    import time as view_time

    ## Every looping function transform asks for a redraw this often, never
    ## every frame (D17, R9).
    VIEW_TICK = 0.05

    ## The sprite canvas (jjk_sprites.rpy: every sprite is 760 x 1400, Panda's
    ## is wider; a person's rectangle uses this size).
    VIEW_SPRITE = (760, 1400)

    ## The ink sb_place and sb_char lay over the room (sb_screens.rpy:
    ## `add Solid(gui.ink) alpha 0.10` and `alpha 0.35`). A foreground or a
    ## pose is cut from the room's picture, so it takes the same wash or it
    ## would stand out lighter than the room around it.
    VIEW_INK = 0.10
    VIEW_INK_PERSON = 0.35

    ## Breathing (4.5): yzoom 1.0 to 1.006 over 4.2 s.
    VIEW_BREATH = (0.006, 4.2)

    ## How far a step of depth goes: blur 0.8 and 2% darker a step.
    VIEW_FAR_BLUR = 0.8
    VIEW_FAR_DIM = 0.02

    ## The rooms whose foreground also stays over the person once we talk
    ## (view_enter): only an object that reaches the bottom edge of the frame
    ## is still in front of someone standing at pos_c. A coffee table in the
    ## middle of the room is not: they have stepped in front of it.
    VIEW_FG_TALK = ("cafeteria",)

    ## The name tags' line (under the feet, so the contact shadow shows).
    VIEW_TAG_Y = 1036

    ## Where people stand, room by room: {place: {n: [(xcenter, yoffset, zoom,
    ## far)]}}. yoffset is the feet's distance above the bottom edge, as a
    ## negative number; far 1 or 2 is a step back (smaller, softer, dimmer).
    ## A room with a foreground picture (images/fg/) stands its far people
    ## behind that object. A sidecar game/layout/view_<place>.json wins over
    ## this table; a room with no row uses view_default_slots.
    VIEW_SLOTS = {
        ## The coffee table (x 760 to 1150, y 700 to 910) is the foreground.
        "dorm_common": {
            1: [(560, -40, 0.52, 0)],
            2: [(480, -40, 0.52, 0), (955, -228, 0.43, 1)],
            3: [(400, -40, 0.52, 0), (955, -228, 0.43, 1), (1400, -40, 0.52, 0)],
            4: [(280, -40, 0.52, 0), (590, -40, 0.52, 0), (870, -228, 0.43, 1), (1045, -228, 0.43, 1)],
        },
        ## The near table (from x 1160, y 880 down) is the foreground.
        "cafeteria": {
            1: [(700, -40, 0.52, 0)],
            2: [(520, -40, 0.52, 0), (1380, -40, 0.52, 0)],
            3: [(330, -40, 0.52, 0), (760, -50, 0.50, 1), (1380, -40, 0.52, 0)],
            4: [(250, -40, 0.52, 0), (530, -50, 0.50, 1), (800, -40, 0.52, 0), (1075, -40, 0.52, 0)],
        },
        ## Everyone on the clear floor at the left and the front, nearer us
        ## than the desks' legs: the desks are too thin-legged to hide anyone
        ## behind (no foreground here). From x 950 on, the near desks reach
        ## the feet's line, and the blackboard's hotspot is at x 1450.
        "classroom": {
            1: [(500, -40, 0.52, 0)],
            2: [(330, -40, 0.52, 0), (720, -40, 0.52, 0)],
            3: [(290, -40, 0.52, 0), (570, -40, 0.52, 0), (850, -40, 0.52, 0)],
            4: [(240, -40, 0.52, 0), (460, -40, 0.52, 0), (680, -40, 0.52, 0), (900, -40, 0.52, 0)],
        },
        ## Open ground; the vending machine's corner (x 1464 on) stays clear.
        "courtyard": {
            1: [(700, -40, 0.52, 0)],
            2: [(480, -40, 0.52, 0), (960, -70, 0.49, 1)],
            3: [(340, -40, 0.52, 0), (720, -80, 0.48, 1), (1090, -40, 0.52, 0)],
            4: [(250, -40, 0.52, 0), (545, -80, 0.48, 1), (850, -80, 0.48, 1), (1160, -40, 0.52, 0)],
        },
        "training": {
            1: [(760, -40, 0.52, 0)],
            2: [(520, -40, 0.52, 0), (1020, -90, 0.47, 1)],
            3: [(340, -40, 0.52, 0), (760, -100, 0.46, 1), (1150, -40, 0.52, 0)],
            4: [(250, -40, 0.52, 0), (560, -100, 0.46, 1), (860, -100, 0.46, 1), (1160, -40, 0.52, 0)],
        },
        ## The floor between the desk and the beds.
        "infirmary": {
            1: [(700, -40, 0.54, 0)],
            2: [(560, -40, 0.54, 0), (960, -60, 0.51, 1)],
            3: [(400, -40, 0.54, 0), (760, -70, 0.50, 1), (1100, -40, 0.54, 0)],
            4: [(260, -40, 0.54, 0), (560, -70, 0.50, 1), (860, -70, 0.50, 1), (1150, -40, 0.54, 0)],
        },
        "library": {
            1: [(760, -40, 0.52, 0)],
            2: [(620, -40, 0.52, 0), (1080, -90, 0.47, 1)],
            3: [(560, -40, 0.52, 0), (930, -110, 0.45, 1), (1290, -40, 0.52, 0)],
            4: [(480, -40, 0.52, 0), (760, -110, 0.45, 1), (1000, -110, 0.45, 1), (1190, -40, 0.52, 0)],
        },
        ## Her desk (x 156 to 779, y 556 to 968) is the foreground: whoever
        ## stands first stands behind it.
        "utahime_office": {
            1: [(470, -120, 0.52, 0)],
            2: [(470, -120, 0.52, 0), (1080, -40, 0.52, 0)],
            3: [(470, -120, 0.52, 0), (960, -40, 0.52, 0), (1330, -40, 0.52, 0)],
            4: [(350, -120, 0.52, 0), (600, -120, 0.52, 0), (960, -40, 0.52, 0), (1190, -40, 0.52, 0)],
        },
    }

    ## The rooms whose VIEW_SLOTS rows stand someone behind the foreground
    ## object. Without the foreground picture for the hour (a new painted
    ## variant of the room with no fg file yet) those slots would put a person
    ## on top of the table, so the room falls back to view_default_slots.
    VIEW_FG_ROOMS = ("dorm_common", "cafeteria", "utahime_office")

    ## The name tags: the gap kept between two, the left edge (the Review
    ## tools link ends at x 171) and the right edge (the stage's, x 1700; a
    ## second icon column starts at 1726).
    VIEW_TAG_GAP = 8
    VIEW_TAG_EDGES = (179, 1700)
    VIEW_TAG_W = builtins.dict()     # (short name, mark, NEW) -> width; init data

    ## Blink and talk (D39). The eye box and the mouth box of each person, on
    ## the sprite canvas (x, y, w, h), measured on <who>_neutral.png. Gojo's
    ## eyes are under the blindfold and Yaga's behind his glasses: talk only.
    VIEW_FACE = {
        "yuji":    dict(eyes=(336, 296, 88, 44),  mouth=(350, 345, 60, 34)),
        "megumi":  dict(eyes=(308, 283, 114, 44), mouth=(345, 338, 48, 28)),
        "nobara":  dict(eyes=(347, 372, 88, 44),  mouth=(366, 424, 44, 30)),
        "maki":    dict(eyes=(332, 271, 80, 36),  mouth=(346, 325, 44, 28)),
        "panda":   dict(eyes=(400, 165, 125, 32), mouth=(378, 256, 160, 56)),
        "toge":    dict(eyes=(327, 287, 84, 40),  mouth=(338, 340, 60, 40)),
        "gojo":    dict(mouth=(326, 226, 54, 34)),
        "utahime": dict(eyes=(341, 256, 80, 40),  mouth=(352, 318, 48, 26)),
        "shoko":   dict(eyes=(332, 250, 88, 38),  mouth=(354, 312, 48, 40)),
        "yaga":    dict(mouth=(330, 226, 100, 54)),
        "ijichi":  dict(eyes=(322, 247, 76, 30),  mouth=(332, 300, 54, 36)),
    }

    ## The expressions the two edits (made from the neutral sprite) sit on
    ## without a seam. The others keep their own eyes and mouth.
    VIEW_BLINK_OK = ("neutral",)
    VIEW_TALK_OK = ("neutral",)

    ## The other faces a person's blink also sits on: the rim of their eye box
    ## on that sprite matches the neutral sprite's (a mean difference under 4
    ## of 255, and no eyebrow crossing it). Measured face by face, so a row is
    ## added when that person's blink picture arrives; Yuji's is the test.
    ## His greeting and most of his room faces are "happy". The mouth is not
    ## shared: a small open mouth on a grin would show.
    VIEW_BLINK_ALSO = {
        "yuji": ("happy", "sad", "serious", "surprised"),
    }

    ## Who is speaking, and until when the mouth moves (the wall clock). Init
    ## data, never saved: a say statement sets it again.
    VIEW_SPEAKING = builtins.list([None, 0.0])

    ## True from the moment the person view opens until the place view is
    ## next shown: that return eases (view_sync_light). Init data, never saved.
    VIEW_FROM_PERSON = builtins.list([False])

    def view_motion():
        """P0 (view_stage.rpy), final. bool: looping motion is on
        (persistent.motion, the Preferences "Motion" row). A transform
        function returns None instead of VIEW_TICK when it is False."""
        return bool(persistent.motion)

    ## Slots -------------------------------------------------------------------------

    def view_default_slots(loc, n):
        """P5. The slots of a room with no row of its own: the phase-1
        centres and the room's zoom, with the middle people 4% smaller,
        10 px higher and a step back."""
        st = PLACE_STAGING.get(loc, {})
        zoom = st.get("zoom", 0.52)
        yoff = -40 + st.get("y", 0)
        xs = STAGE_CENTRES.get(n, [])
        out = []
        for i, x in enumerate(xs):
            if 0 < i < len(xs) - 1:
                out.append((x, yoff - 10, round(zoom * 0.96, 4), 1))
            else:
                out.append((x, yoff, zoom, 0))
        return out

    def view_slot_ok(rows, n):
        """P5. bool: `rows` is n slots of three or four plain numbers (a
        sidecar's JSON may hold anything)."""
        if not isinstance(rows, (builtins.list, builtins.tuple)) or len(rows) != n:
            return False
        for r in rows:
            if not isinstance(r, (builtins.list, builtins.tuple)) or len(r) not in (3, 4):
                return False
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in r):
                return False
            if not r[2] > 0:
                return False
        return True

    def view_slots(loc, n):
        """P5 (view_stage.rpy). A list of n tuples (xcenter, yoffset, zoom,
        far): where n people stand in a room. The sidecar
        game/layout/view_<loc>.json ("slots") first, then VIEW_SLOTS, then
        the phase-1 centres with the middle people a step back. A room
        whose table rows stand people behind its foreground (VIEW_FG_ROOMS)
        uses those centres too while the foreground picture for the hour is
        missing. [] when n is not 1 to 4."""
        if n not in (1, 2, 3, 4):
            return []
        rows = (rule_layout("view_" + str(loc)).get("slots") or {})
        rows = rows.get(str(n)) if isinstance(rows, builtins.dict) else None
        if not view_slot_ok(rows, n):
            if loc in VIEW_FG_ROOMS and view_fg_path(loc) is None:
                return view_default_slots(loc, n)
            rows = VIEW_SLOTS.get(loc, {}).get(n)
        if not view_slot_ok(rows, n):
            return view_default_slots(loc, n)
        return [(r[0], r[1], r[2], int(r[3]) if len(r) > 3 else 0) for r in rows]

    def view_slot_rect(slot):
        """P5. The rectangle (x, y, w, h), as ints, one slot covers: the
        sprite canvas at the slot's zoom, feet on the bottom edge plus the
        slot's y offset."""
        xc, yoff, zoom = slot[0], slot[1], slot[2]
        w = int(round(VIEW_SPRITE[0] * zoom))
        h = int(round(VIEW_SPRITE[1] * zoom))
        return (int(round(xc - w / 2.0)), int(config.screen_height + yoff - h), w, h)

    def view_slot_rects(loc, n):
        """P0 (view_stage.rpy). The rectangles (x, y, w, h), as ints, that n
        people standing in view_slots(loc, n) cover."""
        return [view_slot_rect(s) for s in view_slots(loc, n)]

    ## The room's own data (U0c2; 6.1) -------------------------------------------------
    ##
    ## game/layout/view_<place>.json, written at the place's layout sitting.
    ## Every key is optional, and a key that is missing or malformed leaves
    ## the room exactly as it was before the key existed:
    ##   slots       where 1 to 4 people stand (view_slots, above)
    ##   poses       pose boxes (view_pose, below; pose_<place>.json comes first)
    ##   floor       {"on": [polygons], "off": [polygons]}: the ground people
    ##               may stand on, and the parts of it they may not. For the
    ##               review tools (view_floor); nothing in the game reads it
    ##   scale       [x, y top, y bottom] of one door or post, taken as 200 cm.
    ##               For the tools only
    ##   slot_light  {hour: {"<n>": [one entry a slot: null, or [tint,
    ##               brightness]]}}: a small light of its own for a slot in a
    ##               sun patch or in shade (view_slot_light)
    ##   cast        {hour: [direction, length, darkness]}: a long shadow on
    ##               the ground outdoors (view_cast)
    ##   talk        true or false: the foreground stays up in dialogue
    ##               (view_talk; without it, the rooms of VIEW_FG_TALK)
    ## An hour is "" (the day picture), "evening" or "night" (the hour's own
    ## picture); a period's name ("Evening") may be used as well and is read
    ## first.

    def view_number(v):
        """U0c2. bool: v is a plain number (a sidecar's JSON may hold anything)."""
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def view_polygon(v):
        """U0c2. bool: v is a polygon: three or more [x, y] points."""
        return (isinstance(v, (builtins.list, builtins.tuple)) and len(v) >= 3
                and all(isinstance(q, (builtins.list, builtins.tuple)) and len(q) == 2
                        and view_number(q[0]) and view_number(q[1]) for q in v))

    def view_floor(loc, off=False):
        """U0c2 (view_stage.rpy), final. The ground people may stand on in a
        place: a list of polygons, each a list of (x, y), from the key
        "floor" of game/layout/view_<loc>.json ({"on": [...], "off":
        [...]}); with off=True the parts of it they may not stand on (the
        pond, a table top). None when the room has no floor traced (or it
        is malformed). For the review tools: the game stands people by
        view_slots and does not read this."""
        data = rule_layout("view_" + str(loc)).get("floor")
        if not isinstance(data, builtins.dict) or not isinstance(data.get("on"), builtins.list) or not data["on"]:
            return None
        rows = data.get("off", []) if off else data["on"]
        if not isinstance(rows, builtins.list) or not all(view_polygon(p) for p in rows):
            return None
        return [[(q[0], q[1]) for q in p] for p in rows]

    def view_hour_row(table, loc, per=None):
        """U0c2. The entry of a sidecar's {hour: value} table for the picture
        a place shows now: under the period's own name when the table has
        one, else under the hour ("evening" or "night" where that picture
        is painted and fresh, "" otherwise). None when there is none."""
        if not isinstance(table, builtins.dict):
            return None
        per = per or store.period
        if per in table:
            return table[per]
        return table.get(bg_variant(loc, per) or "")

    def view_slot_light(loc, n, i, per=None):
        """U0c2. (tint, brightness) for the i-th of n standing slots in a
        place at this hour, from the key "slot_light" of view_<loc>.json, or
        None (no light of its own: the room's row alone, as before)."""
        rows = view_hour_row(rule_layout("view_" + str(loc)).get("slot_light"), loc, per)
        rows = rows.get(str(n)) if isinstance(rows, builtins.dict) else None
        if not isinstance(rows, builtins.list) or len(rows) != n or not (0 <= i < n):
            return None
        e = rows[i]
        if (isinstance(e, builtins.list) and len(e) == 2 and isinstance(e[0], str) and len(e[0]) == 7
                and e[0].startswith("#") and view_number(e[1])):
            return (e[0], e[1])
        return None

    def view_cast(loc, per=None):
        """U0c2. (direction, length, darkness) of the long shadow people cast
        on the ground in a place at this hour, from the key "cast" of
        view_<loc>.json, or None (no cast shadow, as before)."""
        e = view_hour_row(rule_layout("view_" + str(loc)).get("cast"), loc, per)
        if isinstance(e, builtins.list) and len(e) == 3 and all(view_number(q) for q in e):
            return (e[0], e[1], e[2])
        return None

    def view_talk(loc):
        """U0c2. bool: the room's foreground stays over the person once we
        talk: the key "talk" of view_<loc>.json when it is true or false,
        else whether the room is in VIEW_FG_TALK."""
        v = rule_layout("view_" + str(loc)).get("talk")
        if isinstance(v, bool):
            return v
        return loc in VIEW_FG_TALK

    ## Poses (D36) -------------------------------------------------------------------

    def view_pose_box(loc, key):
        """U0c2. The box a pose's sidecar gives for `key` ("<who>" or
        "<who>__<variant>"), whatever it holds, or None: pose_<loc>.json
        first, then the key "poses" of view_<loc>.json."""
        for name in ("pose_" + str(loc), "view_" + str(loc)):
            boxes = rule_layout(name).get("poses")
            if isinstance(boxes, builtins.dict) and key in boxes:
                return boxes[key]
        return None

    def view_pose(who, loc, per=None):
        """P5 (view_stage.rpy). dict(image, box) for a painted pose, or None
        for the standing sprite. `image` is the picture's path (a str, never
        a displayable: a screen may keep the dict), `box` the (x, y, w, h)
        of the person in it, as ints.

        The picture is images/place/pose_<loc>__<who>__<variant>.png when
        the room has a painted picture for the hour (bg_variant), else
        pose_<loc>__<who>.png: a day pose is never laid on a night room. The
        box comes from game/layout/pose_<loc>.json ("poses"), the file the
        pose installer writes (the second overhaul, K15), and then from the
        older key "poses" of view_<loc>.json; with no box the whole picture
        is used, and only when that person is alone on the stage. None as
        well for a pose that is stale (art_fresh)."""
        v = bg_variant(loc, per or store.period)
        key = "%s__%s" % (who, v) if v else str(who)
        path = "images/place/pose_%s__%s.png" % (loc, key)
        if not renpy.loadable(path):
            return None
        ## U0c2 (5.5, K7): a pose painted on a picture that has since been
        ## replaced is not shown: the standing sprite.
        if not art_fresh("pose_%s__%s" % (loc, key), art_stem(loc) + ("_" + v if v else "")):
            return None
        box = view_pose_box(loc, key)
        if (isinstance(box, (builtins.list, builtins.tuple)) and len(box) == 4
                and all(isinstance(q, (int, float)) and not isinstance(q, bool) for q in box)
                and box[2] > 0 and box[3] > 0):
            return builtins.dict(image=path, box=(int(box[0]), int(box[1]), int(box[2]), int(box[3])))
        if stage_people(loc)[0] == [who]:
            return builtins.dict(image=path, box=(0, 0, config.screen_width, config.screen_height))
        return None

    def view_stage_rows(loc):
        """P5. The people on stage in a room now, in stage order: a list of
        dicts (who, x, yoff, zoom, far, pose, rect), all plain values. `pose`
        is view_pose's dict or None; `rect` is the pose's box when a pose is
        drawn, else the slot's rectangle. Whoever is tagging along stands
        with me, so they never take their pose."""
        on, _extra = stage_people(loc)
        poses = [None if who == store.companion else view_pose(who, loc) for who in on]
        slots = view_pick_slots(loc, len([p for p in poses if p is None]), [p["box"] for p in poses if p])
        rows = []
        k = 0
        for who, pose in zip(on, poses):
            if pose:
                x, y, w, h = pose["box"]
                rows.append(builtins.dict(who=who, x=int(x + w / 2), yoff=-40, zoom=0.52, far=0, pose=pose,
                                          rect=builtins.tuple(pose["box"])))
            else:
                slot = slots[k]
                k += 1
                rows.append(builtins.dict(who=who, x=slot[0], yoff=slot[1], zoom=slot[2], far=slot[3], pose=None,
                                          rect=view_slot_rect(slot)))
        return rows

    def view_pose_cost(slot, boxes):
        """P5. How much of the pose boxes a person standing in `slot` covers,
        in square pixels (the body: the middle 60% of the canvas)."""
        x, y, w, h = view_slot_rect(slot)
        bx0, bx1 = x + 0.2 * w, x + 0.8 * w
        cost = 0
        for px, py, pw, ph in boxes:
            ox = min(bx1, px + pw) - max(bx0, px)
            oy = min(y + h, py + ph) - max(y, py)
            if ox > 0 and oy > 0:
                cost += ox * oy
        return int(cost)

    def view_pick_slots(loc, k, boxes):
        """P5. The slots for the k people who stand while others are painted
        into the room (`boxes`, their pose boxes). With no pose it is
        view_slots(loc, k). Otherwise it is the k slots that cover the pose
        boxes least: k slots of one layout (for k to four people) when one
        such set is clear of the boxes, else k slots drawn from all of the
        room's layouts, left to right and at least 170 px apart. So nobody
        stands in front of someone on the sofa while the room has a clear
        slot left; in a room with none, the overlap is the smallest there is."""
        if not boxes or k < 1:
            return view_slots(loc, k)
        import itertools
        best = None
        pool = []
        for m in range(k, 5):
            layout = view_slots(loc, m)
            for s in layout:
                if s not in pool:
                    pool.append(s)
            for combo in itertools.combinations(range(len(layout)), k):
                key = (sum(view_pose_cost(layout[i], boxes) for i in combo), 0, m, combo)
                if best is None or key < best[0]:
                    best = (key, [layout[i] for i in combo])
        if best is not None and best[0][0] > 0:
            pool.sort(key=lambda s: (s[0], s[1]))
            for combo in itertools.combinations(range(len(pool)), k):
                if any(pool[j][0] - pool[i][0] < 170 for i, j in zip(combo, combo[1:])):
                    continue
                key = (sum(view_pose_cost(pool[i], boxes) for i in combo), 1, 0, combo)
                if key < best[0]:
                    best = (key, [pool[i] for i in combo])
        return best[1] if best else view_slots(loc, k)

    def view_tag_est(short, job=False, new=False):
        """P5. A name tag's width from the length of the name (used until
        the text can be measured)."""
        return 28 + 13 * len(short) + (48 if job else 0) + (56 if new else 0)

    def view_tag_w(short, job=False, new=False):
        """P5. The width of a name tag (screen view_tags): the padding, the
        short name, and the mission mark and the NEW chip when it has them.
        Measured once for each tag (Text.size) and kept."""
        key = (short, bool(job), bool(new))
        if key not in VIEW_TAG_W:
            try:
                w = 28 + Text(short, style="view_tag_name", substitute=False).size()[0]
                if job:
                    w += 8 + Text(u"\u300c!\u300d", font=gui.display_heavy_font, size=20).size()[0]
                if new:
                    w += 8 + 12 + Text(__("NEW"), font=gui.body_bold_font, size=11, kerning=2).size()[0]
                VIEW_TAG_W[key] = int(w + 0.999)
            except Exception:
                return view_tag_est(short, job, new)
        return VIEW_TAG_W[key]

    def view_tag_xs(rows, widths=None, gap=None, lo=None, hi=None):
        """P5. The x centre of each row's name tag, in the rows' order: under
        the person, moved apart by the tags' own widths where two would
        touch, and kept between the Review tools link and the icon column
        (VIEW_TAG_EDGES). `widths` is each tag's width (view_tag_w); without
        it every tag is taken as 170 wide."""
        gap = VIEW_TAG_GAP if gap is None else gap
        lo = VIEW_TAG_EDGES[0] if lo is None else lo
        hi = VIEW_TAG_EDGES[1] if hi is None else hi
        ws = builtins.list(widths) if widths is not None else [170] * len(rows)
        want = [int(r["rect"][0] + r["rect"][2] / 2) for r in rows]
        order = sorted(range(len(rows)), key=want.__getitem__)
        out = builtins.list(want)
        edge = lo - gap                 # the right edge of the tag before
        for i in order:                 # left to right: push apart
            half = (ws[i] + 1) // 2
            x = max(want[i], edge + gap + half)
            out[i] = x
            edge = x + half
        edge = hi + gap                 # the left edge of the tag after
        for i in order[::-1]:           # right to left: back inside
            half = (ws[i] + 1) // 2
            out[i] = min(out[i], edge - gap - half)
            edge = out[i] - half
        return out

    def view_asleep(loc):
        """U0c2 (view_stage.rpy): a stub, filled by U3. A list of (who,
        patch) for the room's sleepers whose asleep picture is installed
        and fresh (docs/UI2_DESIGN.md 6.2 row 12): `patch` is a pose dict
        as view_pose gives one, dict(image, box). The stage lays each on
        the room before the people; it takes no focus. The stub: none."""
        return []

    def view_draw_key(row):
        return (0 if row["pose"] else 1, -row["far"])

    def view_draw_order(rows):
        """P5. The rows in the order they are drawn: painted poses (they are
        part of the room), then the people furthest back, then the nearest."""
        return sorted(rows, key=view_draw_key)

    def view_person_rects(loc):
        """P5 (view_stage.rpy). A list of (x, y, w, h), one for each person
        on stage in the room right now: the slot's rectangle, or the pose's
        box when a pose is drawn."""
        return [r["rect"] for r in view_stage_rows(loc)]

    ## The room's colour, for what is cut from its picture ----------------------------

    def view_ink_matrix(a):
        """P5. The colour matrix that does what `add Solid(gui.ink) alpha a`
        does to the picture under it."""
        r, g, b = Color(gui.ink).rgb
        k = 1.0 - a
        return Matrix([k, 0, 0, r * a,
                       0, k, 0, g * a,
                       0, 0, k, b * a,
                       0, 0, 0, 1.0])

    def view_room_matrix(loc, ink=0.0, bright=0.0, per=None):
        """P5. The matrixcolor for a piece of the room's own picture (a
        foreground, a pose): the tint graded_bg gives the room at this hour,
        then the screen's ink wash, then `bright` (a hover). None when
        nothing changes. With no ink and no hover it is graded_bg's own
        matrix, which is what a save may hold."""
        bg = graded_bg(loc, per)
        m = getattr(bg, "matrixcolor", None) if isinstance(bg, Transform) else None
        if not ink and not bright:
            return m
        if m is not None and not isinstance(m, Matrix):
            m = m(None, 1.0)
        if ink:
            m = view_ink_matrix(ink) if m is None else view_ink_matrix(ink) * m
        if bright:
            b = BrightnessMatrix(bright)(None, 1.0)
            m = b if m is None else b * m
        return m

    def view_tinted(d, m):
        """P5. `d` under the matrix `m` (d itself when m is None)."""
        return d if m is None else Transform(d, matrixcolor=m)

    ## What the stage draws -----------------------------------------------------------

    def view_phase(who):
        """P5. A person's own offset into the breath, 0 to 1, from their name."""
        return (sum(ord(ch) for ch in str(who)) % 97) / 97.0

    def view_breathe_fn(trans, st, at, phase=0.0):
        """P5. Breathing: yzoom 1.0 to 1.006 over 4.2 s by the wall clock,
        about the feet (the sprite is placed by its bottom edge). Returns
        VIEW_TICK, or None (and a still sprite) when view_motion() is False.
        Top-level and curried with the phase (R10)."""
        if not view_motion():
            trans.yzoom = 1.0
            return None
        depth, period = VIEW_BREATH
        f = 0.5 - 0.5 * view_math.cos(2.0 * view_math.pi * (view_time.time() / period + phase))
        trans.yzoom = 1.0 + depth * f
        return VIEW_TICK

    def view_sprite(who, expr, zoom, far=0, hover=False):
        """P5. A person standing on the stage: their sprite at the slot's
        zoom, softer and dimmer a step back (a fixed property, under the
        motion), breathing when motion is on. A new displayable each call:
        use it in an `add` or a button's line, never keep it."""
        kw = builtins.dict(zoom=zoom)
        if far:
            kw["blur"] = VIEW_FAR_BLUR * far
        b = (0.08 if hover else 0.0) - VIEW_FAR_DIM * far
        if b:
            kw["matrixcolor"] = BrightnessMatrix(b)
        d = Transform(person_image(who, expr), **kw)
        if not view_motion():
            return d
        return Transform(d, function=renpy.curry(view_breathe_fn)(phase=view_phase(who)))

    def view_soft_box(w, h):
        """P5. The mask that feathers a pose's edge: gui/soft_box.png
        stretched over the box, or a hard edge until that file exists."""
        if renpy.loadable("gui/soft_box.png"):
            return Frame("gui/soft_box.png", 24, 24, xysize=(w, h))
        return Solid("#fff", xysize=(w, h))

    def view_pose_patch(pose, loc, hover=False, ink=None):
        """P5. The piece of a pose picture the stage lays on the room: the
        box cropped out, its edge feathered, tinted like the room. A new
        displayable each call."""
        x, y, w, h = pose["box"]
        d = AlphaMask(Transform(pose["image"], crop=(x, y, w, h)), view_soft_box(w, h))
        ink = VIEW_INK if ink is None else ink
        return view_tinted(d, view_room_matrix(loc, ink, 0.08 if hover else 0.0))

    def view_tip(who, loc):
        """P5. A person's hover text: their name, then what they're doing."""
        return rail_tip(CAST[who]["short"], ambient_of(who, loc)[0])

    def view_tag_marks(who, loc):
        """P5. (a mission is waiting with them, a new scene is waiting with
        them), as the name tag shows them: no mission mark in explore mode,
        on a rest day, or when the night won't let me start it; no NEW for
        a scene the night won't let me start."""
        job = False
        if not store.explore_mode and night_can_work():
            for m in missions_with(who, loc):
                mid = mission_view(m)[0]
                if night_allows("mission:" + str(mid), (MISSION_BY_ID.get(mid) or {}).get("cost", 0)):
                    job = True
                    break
        new = bool(has_event("hangout", who, loc)) and bool(night_allows("hang", 1))
        return job, new

    ## The foreground (D38) -----------------------------------------------------------

    def view_fg_path(loc, per=None):
        """P5. The foreground picture for a room at this hour, or None:
        images/fg/fg_<loc>_<variant>.png when the room has a painted picture
        for the hour, else images/fg/fg_<loc>.png. None as well for a cut
        that is stale (art_fresh)."""
        v = bg_variant(loc, per or store.period)
        path = "images/fg/fg_%s_%s.png" % (loc, v) if v else "images/fg/fg_%s.png" % loc
        if not renpy.loadable(path):
            return None
        ## U0c2 (5.5, K7): a cut made from a picture that has since been
        ## replaced is not laid over the new one.
        if not art_fresh("fg_%s%s" % (loc, "_" + v if v else ""), art_stem(loc) + ("_" + v if v else "")):
            return None
        return path

    def view_fg_image(path, loc, ink=0.0):
        """P5. The foreground picture, tinted like the room. A new
        displayable each call. With no ink it is a plain picture under
        graded_bg's own matrix, which a save may hold."""
        return view_tinted(Image(path), view_room_matrix(loc, ink))

    ## The loop's hooks (6.3) ---------------------------------------------------------

    def view_sync_light():
        """P5 (view_stage.rpy). Returns None. Called before the place view
        opens. Wait, Study and the rest change the hour without a scene
        statement, so this sets the sprite light for the room and hour and
        puts the room's picture for this hour on the master layer: whatever
        dissolves next (into the person view, into a scene) starts from the
        right room. Coming back from the person view, the place view eases
        in (VIEW_FROM_PERSON)."""
        if store.here in LOCATIONS:
            store.scene_light = light_for_place(store.here, store.period)
            view_room_show()
        if VIEW_FROM_PERSON[0]:
            VIEW_FROM_PERSON[0] = False
            if view_eased():
                renpy.transition(Dissolve(0.25))
        return None

    def view_room_show():
        """P5. Returns None. Clears the master layer and shows the room as
        `scene expression graded_bg()` would: a painted picture under its
        own name, a tinted one under the tag view_room."""
        d = graded_bg()
        renpy.scene()
        if isinstance(d, str):
            renpy.show(d)
        else:
            renpy.show("view_room", what=d)
        return None

    def view_eased():
        """P5. bool: the joins between idle and talking may move: not while
        skipping, and not in a replay."""
        return not (config.skipping or getattr(store, "_in_replay", None))

    def view_before_person(who):
        """P5 (view_stage.rpy). Returns None. Called before the person view
        opens: the room dissolves into it, and the place view eases back
        in when we leave it (view_sync_light)."""
        VIEW_FROM_PERSON[0] = True
        if view_eased():
            renpy.transition(Dissolve(0.25))
        return None

    def view_after_scene():
        """P5 (view_stage.rpy). Returns None. Called when a scene hands back
        to the place view: the next interaction (the place view) dissolves
        in from the last line of the scene."""
        if view_eased():
            renpy.transition(Dissolve(0.25))
        return None

    def view_enter(who, expr=None):
        """P5 (view_stage.rpy). Returns None. Puts the person on screen
        before we talk, with the face they look up with (or `expr`): eased
        from where the person view left them to pos_c, with the room's
        foreground over them (tag view_fg, zorder 5) in the rooms where it
        is still in front of someone that close (view_talk). In a replay it is
        what stage_person always did: the sprite at pos_c, no foreground.
        While skipping, or with motion off, the sprite goes straight to
        pos_c."""
        name = person_image(who, expr)
        if getattr(store, "_in_replay", None):
            renpy.show(name, at_list=[pos_c])
            return None
        if view_motion() and not config.skipping:
            renpy.show(name, at_list=[view_enter_ease])
        else:
            renpy.show(name, at_list=[pos_c])
        path = view_fg_path(store.here) if view_talk(store.here) else None
        if path:
            renpy.show("view_fg", what=view_fg_image(path, store.here), zorder=5)
        return None

    ## Blink and talk (D39) -----------------------------------------------------------

    def view_blink_fn(trans, st, at, who=""):
        """P5. The eye layer of a sprite: shown for 0.12 s every 3 to 6 s
        (each person keeps their own rhythm), by the wall clock. Returns
        VIEW_TICK, or None (eyes open) when view_motion() is False.
        Top-level and curried with who (R10)."""
        if not view_motion():
            trans.alpha = 0.0
            return None
        ph = view_phase(who)
        gap = 3.0 + 3.0 * ph
        trans.alpha = 1.0 if ((view_time.time() + 7.0 * ph) % gap) < 0.12 else 0.0
        return VIEW_TICK

    def view_talk_fn(trans, st, at, who=""):
        """P5. The mouth layer of a sprite: on and off every 0.12 s while
        that person is speaking (VIEW_SPEAKING). Returns VIEW_TICK, or None
        (mouth shut) when view_motion() is False. Top-level and curried
        with who (R10)."""
        if not view_motion():
            trans.alpha = 0.0
            return None
        now = view_time.time()
        on = VIEW_SPEAKING[0] == who and now < VIEW_SPEAKING[1] and int(now / 0.12) % 2 == 0
        trans.alpha = 1.0 if on else 0.0
        return VIEW_TICK

    def view_face_of(path):
        """P5. (who, expression) from a sprite's path,
        "images/char/yuji_happy.png" -> ("yuji", "happy"); (None, None)
        for a path that isn't <who>_<expression>.png."""
        stem = str(path).rsplit("/", 1)[-1].rsplit(".", 1)[0]
        who, sep, expr = stem.partition("_")
        if not sep or not who or not expr:
            return None, None
        return who, expr

    ## The second overhaul (U0c2; D57, 3.2): game/layout/faces.json, written
    ## only by the face installer, wins over the two tables above:
    ##   {"blink_also": {who: [faces]},
    ##    "eyes":  {who: [x, y, w, h]},
    ##    "mouth": {who: [x, y, w, h]}}
    ## so a person's blink faces and boxes can change with their drawing and
    ## no script does. A person with no row, or a malformed one, keeps the
    ## table's.

    def view_blink_also(who):
        """U0c2. The other faces a person's blink sits on, a tuple of
        expression names: their row of "blink_also" in faces.json when it
        is a list of names, else VIEW_BLINK_ALSO's."""
        rows = rule_layout("faces").get("blink_also")
        row = rows.get(who) if isinstance(rows, builtins.dict) else None
        if isinstance(row, builtins.list) and all(isinstance(e, str) for e in row):
            return builtins.tuple(row)
        return builtins.tuple(VIEW_BLINK_ALSO.get(who, ()))

    def view_face_box(who, key):
        """U0c2. A person's eye box (key "eyes") or mouth box ("mouth") on
        the sprite canvas, (x, y, w, h) as ints, or None when they have
        none: their row under that key in faces.json when it is four
        numbers with a width and a height, else VIEW_FACE's."""
        rows = rule_layout("faces").get(key)
        box = rows.get(who) if isinstance(rows, builtins.dict) else None
        if (isinstance(box, builtins.list) and len(box) == 4 and all(view_number(q) for q in box)
                and box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0):
            return (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
        box = VIEW_FACE.get(who, {}).get(key)
        return builtins.tuple(box) if box else None

    def view_face_layers(path):
        """P5. The blink and talk layers lit_sprite adds to a sprite (D39):
        the eye box cut from images/char/fx/fx_<who>_blink.png and the mouth
        box cut from fx_<who>_talk.png, each where it sits on the canvas.
        [] unless the file exists, the person has the box (view_face_box:
        faces.json, then VIEW_FACE), and the expression is one the edit sits
        on (VIEW_BLINK_OK and the person's blink faces, view_blink_also:
        faces.json, then VIEW_BLINK_ALSO; VIEW_TALK_OK), so without the
        files a sprite is built exactly as before. The layers are the same
        two whatever the data says (K9)."""
        who, expr = view_face_of(path)
        if not who:
            return []
        out = []
        for kind, key, ok, fn in (("blink", "eyes", VIEW_BLINK_OK, view_blink_fn),
                                  ("talk", "mouth", VIEW_TALK_OK, view_talk_fn)):
            box = view_face_box(who, key)
            fx = "images/char/fx/fx_%s_%s.png" % (who, kind)
            if kind == "blink":
                ok = builtins.tuple(ok) + view_blink_also(who)
            if box and expr in ok and renpy.loadable(fx):
                out.append(Transform(fx, crop=builtins.tuple(box), xpos=box[0], ypos=box[1],
                                     function=renpy.curry(fn)(who=who)))
        return out

    def view_say_cb(event, interact=True, **kwargs):
        """P5. A character callback (config.all_character_callbacks): notes
        who is speaking, and for how long their mouth moves. Text is shown
        at once in this game, so the time comes from the line's length."""
        if event == "show":
            what = kwargs.get("what") or getattr(store, "_last_say_what", "") or ""
            VIEW_SPEAKING[0] = renpy.get_say_image_tag()
            VIEW_SPEAKING[1] = view_time.time() + max(0.6, min(2.4, 0.035 * len(what)))
        elif event == "end":
            VIEW_SPEAKING[0] = None

    config.all_character_callbacks.append(view_say_cb)

    ## Lint ---------------------------------------------------------------------------

    def view_validate():
        """P5. Lint findings for VIEW_SLOTS and VIEW_FACE."""
        out = []
        for loc, table in VIEW_SLOTS.items():
            if loc not in LOCATIONS:
                out.append("VIEW_SLOTS: %r is not a place" % (loc,))
            for n in (1, 2, 3, 4):
                rows = table.get(n)
                if not view_slot_ok(rows, n) or any(len(r) != 4 for r in rows):
                    out.append("VIEW_SLOTS %s: %d people need %d slots of (xcenter, yoffset, zoom, far)" % (loc, n, n))
                    continue
                for r in rows:
                    x, _y, w, _h = view_slot_rect(r)
                    if x < 40 or x + w > 1700:
                        out.append("VIEW_SLOTS %s, %d people: the slot at x %s leaves the stage (x 40 to 1700)" % (loc, n, r[0]))
        for who, exprs in VIEW_BLINK_ALSO.items():
            if "eyes" not in VIEW_FACE.get(who, {}):
                out.append("VIEW_BLINK_ALSO: %r has no eye box in VIEW_FACE" % (who,))
            for e in exprs:
                if not renpy.loadable("images/char/%s_%s.png" % (who, e)):
                    out.append("VIEW_BLINK_ALSO %s: no sprite for the expression %r" % (who, e))
        ## U0c2: faces.json. A row the readers would not use is a finding;
        ## the eye box and the mouth box of one person never overlap, and
        ## the mouth lies below the eyes.
        faces = rule_layout("faces")
        named = builtins.set(VIEW_FACE)
        for key in ("blink_also", "eyes", "mouth"):
            rows = faces.get(key, {})
            if not isinstance(rows, builtins.dict):
                out.append("faces.json: %r must be {who: ...}" % (key,))
                continue
            for who in builtins.sorted(rows):
                row = rows[who]
                named.add(who)
                if who not in CAST:
                    out.append("faces.json %s: %r is not in the cast" % (key, who))
                elif key == "blink_also":
                    if not (isinstance(row, builtins.list) and all(isinstance(e, str) for e in row)):
                        out.append("faces.json blink_also: %r must be a list of faces" % (who,))
                        continue
                    for e in row:
                        if not renpy.loadable("images/char/%s_%s.png" % (who, e)):
                            out.append("faces.json blink_also %s: no sprite for the expression %r" % (who, e))
                    if not view_face_box(who, "eyes"):
                        out.append("faces.json blink_also: %r has no eye box" % (who,))
                elif not (isinstance(row, builtins.list) and len(row) == 4 and all(view_number(q) for q in row)
                          and row[0] >= 0 and row[1] >= 0 and row[2] > 0 and row[3] > 0):
                    out.append("faces.json %s: %r must be [x, y, w, h] on the sprite canvas" % (key, who))
        for who in builtins.sorted(named):
            e, m = view_face_box(who, "eyes"), view_face_box(who, "mouth")
            if e and m and m[1] < e[1] + e[3]:
                out.append("the face of %s: the mouth box (from y %d) must lie below the eye box (to y %d)" % (who, m[1], e[1] + e[3]))
        for who, face in VIEW_FACE.items():
            if who not in CAST:
                out.append("VIEW_FACE: %r is not in the cast" % (who,))
            for key, box in face.items():
                if key not in ("eyes", "mouth") or len(box) != 4:
                    out.append("VIEW_FACE %s: %r must be eyes or mouth, (x, y, w, h)" % (who, key))
        return out


init 5 python:
    register_validator(view_validate)


## The person view's focus (D35): from where they stood in the room to the left
## of the card. One argument still works (the phase-1 call).
transform char_focus(x0, y0=-40, z0=0.52):
    xcenter x0 yalign 1.0 yoffset y0 zoom z0
    easein 0.35 xcenter 520 yoffset -20 zoom 0.66

## The same, fading in: for someone who was a painted pose in the room.
transform view_focus_in(x0, y0=-40, z0=0.52):
    xcenter x0 yalign 1.0 yoffset y0 zoom z0 alpha 0.0
    parallel:
        easein 0.35 xcenter 520 yoffset -20 zoom 0.66
    parallel:
        linear 0.3 alpha 1.0

## The pose, fading out under them.
transform view_pose_out:
    alpha 1.0
    linear 0.3 alpha 0.0

## Into dialogue (4.5): from where the person view left them (x 520, zoom 0.66)
## to pos_c's place. ATL, timed by st, so a save made mid-ease loads (R10).
transform view_enter_ease:
    xanchor 0.5 xpos 520 yalign 1.0 yoffset -20 zoom 0.66
    easein 0.35 xpos 960 yoffset 0 zoom 0.64


style view_tag_button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (14, 0, 14, 0)
    ysize 36

style view_tag_name is text:
    font gui.display_font
    size 20
    outlines [(2, "#07060cc0", 0, 0)]
    yalign 0.5


## The stage (4.5): the people in the room. A used screen with parameters sees
## only its parameters, so it works out the stage itself.
screen view_stage(loc):

    $ _view_rows = view_draw_order(view_stage_rows(loc))

    ## Someone asleep is painted as part of the room, under everyone and
    ## everything that can be clicked (the second overhaul, 6.2 row 12).
    ## view_asleep answers nobody until U3 fills it.
    for _view_sw, _view_sp in view_asleep(loc):
        add view_pose_patch(_view_sp, loc):
            pos (_view_sp["box"][0], _view_sp["box"][1])

    for _view_r in _view_rows:
        $ _view_who = _view_r["who"]
        if _view_r["pose"]:
            ## Painted into the room: only the box around them is laid on.
            button:
                id "stage_" + _view_who
                pos (_view_r["rect"][0], _view_r["rect"][1])
                xysize (_view_r["rect"][2], _view_r["rect"][3])
                padding (0, 0)
                background view_pose_patch(_view_r["pose"], loc)
                hover_background view_pose_patch(_view_r["pose"], loc, hover=True)
                tooltip (view_tip(_view_who, loc), "stage_" + _view_who)
                action Return(("char", _view_who))
        else:
            $ _view_expr = ambient_of(_view_who, loc)[1]
            imagebutton:
                id "stage_" + _view_who
                idle view_sprite(_view_who, _view_expr, _view_r["zoom"], _view_r["far"])
                hover view_sprite(_view_who, _view_expr, _view_r["zoom"], _view_r["far"], hover=True)
                focus_mask True
                xcenter _view_r["x"]
                yalign 1.0
                yoffset _view_r["yoff"]
                tooltip (view_tip(_view_who, loc), "stage_" + _view_who)
                action Return(("char", _view_who))


## The name tags (4.5): one line under the feet. The caption is the hover
## label, over the person or the tag.
screen view_tags(loc):

    $ _view_rows = view_stage_rows(loc)
    $ _view_marks = [view_tag_marks(_view_r["who"], loc) for _view_r in _view_rows]
    $ _view_xs = view_tag_xs(_view_rows, [view_tag_w(CAST[_view_r["who"]]["short"], *_view_m) for _view_r, _view_m in zip(_view_rows, _view_marks)])

    for _view_i, _view_r in enumerate(_view_rows):
        $ _view_who = _view_r["who"]
        $ _view_c = CAST[_view_who]
        $ _view_job, _view_new = _view_marks[_view_i]
        button:
            id "tag_" + _view_who
            style "view_tag_button"
            xcenter _view_xs[_view_i]
            ypos VIEW_TAG_Y
            tooltip (view_tip(_view_who, loc), "tag_" + _view_who)
            action Return(("char", _view_who))
            hbox:
                spacing 8
                yalign 0.5
                text _view_c["short"] style "view_tag_name" color _view_c["color"] substitute False
                if _view_job:
                    text u"「!」" font gui.display_heavy_font color gui.gold size 20 yalign 0.5
                if _view_new:
                    frame:
                        background Solid(gui.gold)
                        padding (6, 2)
                        yalign 0.5
                        text _("NEW"):
                            font gui.body_bold_font
                            color gui.ink
                            size 11
                            kerning 2


## The person in the person view (4.5): eased from their own place on the
## stage. Someone who was a painted pose fades out of it as they come forward.
screen view_focus(who):

    $ _view_row = ([r for r in view_stage_rows(here) if r["who"] == who] or [None])[0]
    if _view_row is None:
        add person_image(who) at char_focus(stage_x(who, here))
    elif _view_row["pose"]:
        add view_pose_patch(_view_row["pose"], here, ink=VIEW_INK_PERSON) at view_pose_out:
            pos (_view_row["rect"][0], _view_row["rect"][1])
        add person_image(who) at view_focus_in(_view_row["x"])
    else:
        add person_image(who) at char_focus(_view_row["x"], _view_row["yoff"], _view_row["zoom"])


## The others in the room while I look at one person (the second overhaul:
## docs/UI2_DESIGN.md 6.2 row 7, D30). sb_char uses it under view_focus. The
## scaffold's STUB (U0c2): empty until U3 draws them, dimmed and a step back.
screen view_others(loc, who):
    pass


## The foreground (4.5): the table edge people stand behind, cut from the
## room's own picture (tools/make_fg.py), then the name tags above it.
screen view_fg(loc):

    $ _view_fgp = view_fg_path(loc)
    if _view_fgp:
        add view_fg_image(_view_fgp, loc, VIEW_INK)

    use view_tags(loc)
