################################################################################
## Cursed Bonds — the stage: the people standing in a room.
##
## Phase 2 (PHASE2_DESIGN.md 4.5, D17, D35, 6.1). P0 moved today's stage loop,
## name plates and focus transform here from sb_screens.rpy, unchanged, and
## wrote the motion switch; P5 makes the stage live (slots, poses, breathing,
## the foreground, the eased entrance).
##
##   screen view_stage(loc)   the people in a room and their name plates;
##                            returns ("char", who) through sb_place
##   screen view_focus(who)   the person, eased in, in the person view
##   screen view_fg(loc)      the foreground layer (empty until P5)
##   VIEW_TICK, view_motion() the redraw delay of every looping transform, and
##                            the Preferences "Motion" switch (persistent.motion)
##   view_person_rects(loc)   where people stand, as rectangles (hotspots stay
##                            out from behind them)
##   view_slots, view_pose, view_sync_light, view_before_person,
##   view_after_scene, view_enter          P5's; P0 wrote the stubs
################################################################################

default persistent.motion = True

init -2 python:

    ## Every looping function transform asks for a redraw this often, never
    ## every frame (D17, R9).
    VIEW_TICK = 0.05

    ## The sprite canvas (jjk_sprites.rpy: every sprite is 760 x 1400).
    VIEW_SPRITE = (760, 1400)

    def view_motion():
        """P0 (view_stage.rpy), final. bool: looping motion is on
        (persistent.motion, the Preferences "Motion" row). A transform
        function returns None instead of VIEW_TICK when it is False."""
        return bool(persistent.motion)

    def view_slots(loc, n):
        """P5 (view_stage.rpy); P0's stub is today's stage. A list of n
        tuples (xcenter, yoffset, zoom, far): where n people stand in a
        room. Today's centres (STAGE_CENTRES), the room's zoom and y
        (PLACE_STAGING), far 0. [] when n is not 1 to 4."""
        st = PLACE_STAGING.get(loc, {})
        zoom = st.get("zoom", 0.52)
        yoff = -40 + st.get("y", 0)
        return [(x, yoff, zoom, 0) for x in STAGE_CENTRES.get(n, [])]

    def view_slot_rects(loc, n):
        """P0 (view_stage.rpy). The rectangles (x, y, w, h), as ints, that n
        people standing in view_slots(loc, n) cover: the sprite canvas at the
        slot's zoom, feet on the bottom edge plus the slot's y offset."""
        out = []
        for xc, yoff, zoom, far in view_slots(loc, n):
            w = int(round(VIEW_SPRITE[0] * zoom))
            h = int(round(VIEW_SPRITE[1] * zoom))
            out.append((int(round(xc - w / 2.0)), int(config.screen_height + yoff - h), w, h))
        return out

    def view_person_rects(loc):
        """P0 (view_stage.rpy), from the stage centres and the sprite size;
        P5 from its slots and pose boxes. A list of (x, y, w, h), one for
        each person on stage in the room right now."""
        on, _extra = stage_people(loc)
        return view_slot_rects(loc, len(on))

    def view_pose(who, loc, per=None):
        """P5 (view_stage.rpy); P0's stub returns None. dict(image, box) for
        a painted pose (image a path str, box a 4-tuple of int), or None for
        the standing sprite."""
        return None

    def view_sync_light():
        """P5 (view_stage.rpy); P0's stub does nothing. Returns None. Sets
        the sprite light for the room before the place view opens."""
        return None

    def view_before_person(who):
        """P5 (view_stage.rpy); P0's stub does nothing. Returns None. Called
        before the person view opens."""
        return None

    def view_after_scene():
        """P5 (view_stage.rpy); P0's stub does nothing. Returns None. Called
        when a scene hands back to the place view."""
        return None

    def view_enter(who, expr=None):
        """P5 (view_stage.rpy); P0's stub is what stage_person did. Returns
        None. Puts the person on screen at pos_c, with the face they look
        up with (or `expr`), before we talk."""
        renpy.show(person_image(who, expr), at_list=[pos_c])
        return None


## The person view's focus (moved from sb_screens.rpy, D35): from where they
## stood in the room to the left of the card.
transform char_focus(x0):
    xcenter x0 yalign 1.0 yoffset -40 zoom 0.52
    easein 0.35 xcenter 520 yoffset -20 zoom 0.66


## The stage (4.5). P0: today's loop, as it stood in sb_place. A used screen
## with parameters sees only its parameters, so it works out the stage itself.
screen view_stage(loc):

    $ _stage, _extra = stage_people(loc)
    $ _xs = STAGE_CENTRES.get(len(_stage), [])
    $ _st = PLACE_STAGING.get(loc, {})
    $ _zoom = _st.get("zoom", 0.52)
    $ _yoff = -40 + _st.get("y", 0)

    ## --- the stage: the people here, clickable --------------------------------
    for _i, _who in enumerate(_stage):
        $ _cap, _expr = ambient_of(_who, loc)
        $ _img = person_image(_who, _expr)
        imagebutton:
            idle Transform(_img, zoom=_zoom)
            hover Transform(_img, zoom=_zoom, matrixcolor=BrightnessMatrix(0.08))
            focus_mask True
            xcenter _xs[_i]
            yalign 1.0
            yoffset _yoff
            action Return(("char", _who))

    ## Nameplates go over every sprite, so a neighbour never covers one.
    for _i, _who in enumerate(_stage):
        $ _c = CAST[_who]
        $ _nm = _c["short"]
        $ _cap = ambient_of(_who, loc)[0]
        $ _job = (not explore_mode) and bool(missions_with(_who, loc))
        $ _new = has_event("hangout", _who, loc)
        button:
            xcenter _xs[_i]
            ypos 944
            background Frame("gui/panel_dark.png", 4, 4)
            hover_background Frame("gui/panel_hover.png", 4, 4)
            padding (18, 6, 18, 8)
            xmaximum 300
            action Return(("char", _who))
            vbox:
                spacing 0
                xalign 0.5
                hbox:
                    spacing 10
                    xalign 0.5
                    text "[_nm]" style "sb_plate_name" color _c["color"] yalign 0.5
                    if _job:
                        text u"「!」" font gui.display_heavy_font color gui.gold size 22 yalign 0.5
                    if _new:
                        frame:
                            background Solid(gui.gold)
                            padding (6, 2)
                            yalign 0.5
                            text _("NEW"):
                                font gui.body_bold_font
                                color gui.ink
                                size 11
                                kerning 2
                if _cap:
                    text "[_cap]" style "sb_plate_caption" xalign 0.5 text_align 0.5


## The person in the person view (4.5): eased from their place on the stage.
screen view_focus(who):
    $ _x0 = stage_x(who, here)
    add person_image(who) at char_focus(_x0)


## The foreground layer (4.5): empty until P5 cuts the pictures.
screen view_fg(loc):
    pass
