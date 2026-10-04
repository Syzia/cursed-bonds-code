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
        ## The desk at the front of the middle row (x 943 to 1229, y 726 to
        ## 810) is the foreground.
        "classroom": {
            1: [(620, -40, 0.52, 0)],
            2: [(520, -40, 0.52, 0), (1085, -130, 0.48, 1)],
            3: [(360, -40, 0.52, 0), (1085, -130, 0.48, 1), (1450, -40, 0.52, 0)],
            4: [(250, -40, 0.52, 0), (540, -40, 0.52, 0), (820, -40, 0.52, 0), (1085, -130, 0.48, 1)],
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

    ## Who is speaking, and until when the mouth moves (the wall clock). Init
    ## data, never saved: a say statement sets it again.
    VIEW_SPEAKING = builtins.list([None, 0.0])

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
        the phase-1 centres with the middle people a step back. [] when n
        is not 1 to 4."""
        if n not in (1, 2, 3, 4):
            return []
        rows = (rule_layout("view_" + str(loc)).get("slots") or {})
        rows = rows.get(str(n)) if isinstance(rows, builtins.dict) else None
        if not view_slot_ok(rows, n):
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

    ## Poses (D36) -------------------------------------------------------------------

    def view_pose(who, loc, per=None):
        """P5 (view_stage.rpy). dict(image, box) for a painted pose, or None
        for the standing sprite. `image` is the picture's path (a str, never
        a displayable: a screen may keep the dict), `box` the (x, y, w, h)
        of the person in it, as ints.

        The picture is images/place/pose_<loc>__<who>__<variant>.png when
        the room has a painted picture for the hour (bg_variant), else
        pose_<loc>__<who>.png: a day pose is never laid on a night room. The
        box comes from the sidecar game/layout/view_<loc>.json ("poses");
        with no box the whole picture is used, and only when that person is
        alone on the stage."""
        v = bg_variant(loc, per or store.period)
        key = "%s__%s" % (who, v) if v else str(who)
        path = "images/place/pose_%s__%s.png" % (loc, key)
        if not renpy.loadable(path):
            return None
        box = (rule_layout("view_" + str(loc)).get("poses") or {})
        box = box.get(key) if isinstance(box, builtins.dict) else None
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

    def view_pick_slots(loc, k, boxes):
        """P5. The slots for the k people who stand while others are painted
        into the room (`boxes`, their pose boxes). With no pose it is
        view_slots(loc, k). Otherwise it is the k slots, from the layouts
        for k to four people, whose bodies cover the pose boxes least, so
        nobody stands in front of someone sitting on the sofa."""
        if not boxes or k < 1:
            return view_slots(loc, k)
        import itertools
        best = None
        for m in range(k, 5):
            layout = view_slots(loc, m)
            for combo in itertools.combinations(range(len(layout)), k):
                cost = 0
                for i in combo:
                    x, y, w, h = view_slot_rect(layout[i])
                    bx0, bx1 = x + 0.2 * w, x + 0.8 * w      # the body, not the canvas
                    for px, py, pw, ph in boxes:
                        ox = min(bx1, px + pw) - max(bx0, px)
                        oy = min(y + h, py + ph) - max(y, py)
                        if ox > 0 and oy > 0:
                            cost += ox * oy
                key = (cost, m, combo)
                if best is None or key < best[0]:
                    best = (key, [layout[i] for i in combo])
        return best[1] if best else view_slots(loc, k)

    def view_tag_xs(rows, gap=170, lo=250, hi=1640):
        """P5. The x centre of each row's name tag, in the rows' order: under
        the person, moved apart where two would touch (someone standing by a
        painted pose), and kept between the Review tools link and the column."""
        want = [int(r["rect"][0] + r["rect"][2] / 2) for r in rows]
        order = sorted(range(len(rows)), key=want.__getitem__)
        out = builtins.list(want)
        last = None
        for i in order:                 # left to right: push apart
            x = max(lo, want[i])
            if last is not None and x < last + gap:
                x = last + gap
            out[i] = last = x
        limit = hi
        for i in order[::-1]:           # right to left: back inside
            out[i] = min(out[i], limit)
            limit = out[i] - gap
        return out

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
        for the hour, else images/fg/fg_<loc>.png."""
        v = bg_variant(loc, per or store.period)
        path = "images/fg/fg_%s_%s.png" % (loc, v) if v else "images/fg/fg_%s.png" % loc
        return path if renpy.loadable(path) else None

    def view_fg_image(path, loc, ink=0.0):
        """P5. The foreground picture, tinted like the room. A new
        displayable each call. With no ink it is a plain picture under
        graded_bg's own matrix, which a save may hold."""
        return view_tinted(Image(path), view_room_matrix(loc, ink))

    ## The loop's hooks (6.3) ---------------------------------------------------------

    def view_sync_light():
        """P5 (view_stage.rpy). Returns None. Sets the sprite light for the
        room and hour before the place view opens: Wait, Study and the rest
        change the hour without a scene statement."""
        if store.here in LOCATIONS:
            store.scene_light = light_for_place(store.here, store.period)
        return None

    def view_eased():
        """P5. bool: the joins between idle and talking may move: not while
        skipping, and not in a replay."""
        return not (config.skipping or getattr(store, "_in_replay", None))

    def view_before_person(who):
        """P5 (view_stage.rpy). Returns None. Called before the person view
        opens: the place view dissolves into it."""
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
        is still in front of someone that close (VIEW_FG_TALK). In a replay it is
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
        path = view_fg_path(store.here) if store.here in VIEW_FG_TALK else None
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

    def view_face_layers(path):
        """P5. The blink and talk layers lit_sprite adds to a sprite (D39):
        the eye box cut from images/char/fx/fx_<who>_blink.png and the mouth
        box cut from fx_<who>_talk.png, each where it sits on the canvas.
        [] unless the file exists, VIEW_FACE has the box, and the expression
        is one the edit sits on (VIEW_BLINK_OK, VIEW_TALK_OK), so without
        the files a sprite is built exactly as before."""
        who, expr = view_face_of(path)
        face = VIEW_FACE.get(who)
        if not face:
            return []
        out = []
        for kind, key, ok, fn in (("blink", "eyes", VIEW_BLINK_OK, view_blink_fn),
                                  ("talk", "mouth", VIEW_TALK_OK, view_talk_fn)):
            box = face.get(key)
            fx = "images/char/fx/fx_%s_%s.png" % (who, kind)
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
    $ _view_xs = view_tag_xs(_view_rows)

    for _view_i, _view_r in enumerate(_view_rows):
        $ _view_who = _view_r["who"]
        $ _view_c = CAST[_view_who]
        $ _view_job, _view_new = view_tag_marks(_view_who, loc)
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


## The foreground (4.5): the table edge people stand behind, cut from the
## room's own picture (tools/make_fg.py), then the name tags above it.
screen view_fg(loc):

    $ _view_fgp = view_fg_path(loc)
    if _view_fgp:
        add view_fg_image(_view_fgp, loc, VIEW_INK)

    use view_tags(loc)
