################################################################################
## Cursed Bonds — the map (PHASE1_DESIGN.md 4.6, WP1).
##
## screen sb_map(layer="campus"), called by the loop (sb_travel, the protected
## `call screen sb_map`) and by the car action (sb_do_car, layer="tokyo").
##
##   Campus  the six AREAS as cards, one row per place: who is there now,
##           YOU ARE HERE, or why it is locked, plus mission_markers() on a
##           second line. A "Find someone" strip of face chips at the bottom.
##   Tokyo   the five districts as cards, and where Ijichi's car is. Opens
##           after Ijichi's ride-along (tokyo_open()).
##
## Returns ("go", loc), ("district", key) or ("cancel",).
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
        """WP1. A gold "!" after someone's name: a mission with them, or a new scene."""
        if missions_with(who, loc):
            return True
        return has_event("hangout", who, loc)

    def map_people(loc, budget):
        """WP1. ([(short, colour, news)], hidden): up to 3 of the people at loc
        whose names fit in `budget` pixels, then how many more there are."""
        folk = who_is_here(loc)
        shown, used = [], 0
        for w in folk:
            if len(shown) == 3:
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

    def map_waiting(area):
        """WP1. How many missions are waiting in an area now (missions_here)."""
        return sum(len(missions_here(l) or []) for l in places_in(area))

    def map_markers_text(marks, loc):
        """WP1. The row's second line, from mission_markers()."""
        return "  ·  ".join(t for t, k in (marks.get(loc) or []))

    def map_cards(marks):
        """WP1. [(area, x, y, [(loc, row_h)])]: each card's top-left corner,
        centred on its anchor and kept between the header and the strip."""
        out = []
        for a in AREAS:
            rows = [(l, MAP_ROW_H_MARKED if marks.get(l) else MAP_ROW_H) for l in a["places"]]
            h = 2 * MAP_CARD_PAD + MAP_CARD_HEAD + sum(MAP_CARD_GAP + rh for l, rh in rows)
            ax, ay = a["anchor"]
            y = int(ay - h / 2)
            y = max(MAP_TOP, min(y, MAP_BOTTOM - h))
            out.append((a, int(ax - MAP_CARD_W / 2), y, rows))
        return out

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


## The map ######################################################################

screen sb_map(layer="campus"):

    tag sandbox

    default view = layer

    key "game_menu" action Return(("cancel",))

    $ _topen = tokyo_open()
    $ _tip = GetTooltip()

    ## Ground ---------------------------------------------------------------------
    if view == "tokyo":
        add "bg map_tokyo"
        add Solid(gui.ink) alpha 0.30
    else:
        add "bg map_campus"
        add Solid(gui.ink) alpha 0.35

    ## Header: seal, title, tabs; then the subline --------------------------------
    vbox:
        xalign 0.5
        ypos 108
        spacing 6
        hbox:
            xalign 0.5
            spacing 16
            use seal("図", 44)
            text _("TOKYO JUJUTSU HIGH"):
                font gui.display_font
                color gui.paper
                size 28
                kerning 6
                yalign 0.5
            null width 14
            button:
                style "sb_map_tab"
                yalign 0.5
                selected (view == "campus")
                action SetScreenVariable("view", "campus")
                hbox:
                    spacing 10
                    yalign 0.5
                    text "校" font gui.display_heavy_font size 24 color gui.seal yalign 0.5
                    text _("Campus") font gui.body_medium_font size 20 color (gui.paper if view == "campus" else gui.dim) yalign 0.5
            button:
                style "sb_map_tab"
                yalign 0.5
                selected (view == "tokyo")
                sensitive _topen
                action SetScreenVariable("view", "tokyo")
                hbox:
                    spacing 10
                    yalign 0.5
                    text "東京" font gui.display_heavy_font size 24 color (gui.seal if _topen else gui.mute) yalign 0.5
                    if _topen:
                        text _("Tokyo") font gui.body_medium_font size 20 color (gui.paper if view == "tokyo" else gui.dim) yalign 0.5
                    else:
                        vbox:
                            yalign 0.5
                            spacing 0
                            text _("Tokyo") font gui.body_medium_font size 18 color gui.mute
                            text _("After Ijichi's ride-along") font gui.body_medium_font size 13 color gui.seal
        text _("Walking is free. Doing something takes time."):
            xalign 0.5
            color gui.dim
            size 18

    if view == "tokyo":
        use sb_map_tokyo
    else:
        use sb_map_campus

    ## Hover help (a lock's full reason, where someone is) ------------------------
    if _tip:
        frame:
            background Frame("gui/panel_dark.png", 4, 4)
            xalign 1.0
            xoffset -40
            yalign 1.0
            yoffset -104
            padding (18, 10, 18, 10)
            xmaximum 700
            text "[_tip!q]" size 18 color gui.paper

    ## Stay here, bottom right -----------------------------------------------------
    textbutton _("Stay here"):
        style "jjk_button"
        text_style "jjk_button_text"
        xfill False
        xalign 1.0
        xoffset -40
        yalign 1.0
        yoffset -30
        action Return(("cancel",))

    use sb_hud(on_map=True)


## The campus layer: six area cards and the Find someone strip.
screen sb_map_campus():

    $ _marks = mission_markers() or {}

    for _a, _x, _y, _rows in map_cards(_marks):
        $ _wait = map_waiting(_a["key"])
        frame:
            style "sb_map_card"
            xpos _x
            ypos _y
            xsize MAP_CARD_W
            vbox:
                spacing MAP_CARD_GAP
                fixed:
                    xsize MAP_ROW_W
                    ysize MAP_CARD_HEAD
                    hbox:
                        spacing 12
                        yalign 0.5
                        use seal(_a["seal"], 44)
                        text _a["name"] font gui.display_font size 24 color gui.paper yalign 0.5
                    if _wait:
                        text "◆ [_wait]" font gui.body_medium_font size 20 color gui.gold xalign 1.0 yalign 0.5

                for _k, _rh in _rows:
                    $ _L = LOCATIONS[_k]
                    $ _ok, _why, _short = place_access(_k)
                    $ _cur = (_k == here)
                    $ _nm = _L["name"]
                    $ _mk = map_markers_text(_marks, _k)
                    $ _budget = MAP_ROW_W - 28 - map_text_width(_nm, gui.display_font, 20) - 14
                    button:
                        style ("sb_map_row_here" if _cur else ("sb_map_row" if _ok else "sb_map_row_locked"))
                        xsize MAP_ROW_W
                        ysize _rh
                        sensitive (not _cur)
                        tooltip (_why if not _ok else None)
                        action (Return(("go", _k)) if _ok else NullAction())
                        fixed:
                            xfill True
                            yfill True
                            text "[_nm!q]":
                                style "sb_map_place"
                                color (gui.violet2 if _cur else (gui.paper if _ok else gui.mute))
                                ypos 22
                                yanchor 0.5
                            if _cur:
                                text _("YOU ARE HERE") style "jjk_label" size 12 kerning 1.0 color gui.violet2 xalign 1.0 ypos 22 yanchor 0.5
                            elif not _ok:
                                text "[_short!q]" font gui.body_medium_font size 15 color gui.seal xalign 1.0 ypos 22 yanchor 0.5
                            else:
                                $ _shown, _more = map_people(_k, _budget)
                                hbox:
                                    spacing 8
                                    xalign 1.0
                                    ypos 22
                                    yanchor 0.5
                                    for _sn, _sc, _news in _shown:
                                        hbox:
                                            spacing 1
                                            text "[_sn!q]" style "sb_map_who" color _sc
                                            if _news:
                                                text "!" style "sb_map_who" color gui.gold
                                    if _more:
                                        text "+[_more]" style "sb_map_who" color gui.dim
                            if _mk:
                                text "[_mk!q]":
                                    font gui.body_medium_font
                                    size 15
                                    color gui.gold
                                    ypos 38
                                    layout "nobreak"

    ## Find someone -----------------------------------------------------------------
    $ _folk = [w for w in ROSTER_ORDER if w in roster]
    if _folk:
        vbox:
            xpos 40
            ypos 968
            spacing 6
            text _("FIND SOMEONE") style "jjk_label" size 14
            hbox:
                spacing 8
                for _w in _folk:
                    $ _wl = char_location(_w)
                    $ _go = bool(_wl and _wl != here and _wl in LOCATIONS and can_enter(_wl)[0])
                    button:
                        style "sb_map_face"
                        tooltip map_who_where(_w)
                        action (Return(("go", _wl)) if _go else NullAction())
                        add face_chip(_w, 56) alpha (1.0 if _wl else 0.35)


## The Tokyo layer: the districts, and Ijichi's car.
screen sb_map_tokyo():

    $ _now = trip_ok_now()

    ## Jujutsu High — Ijichi's car (kept clear of the header).
    frame:
        style "sb_map_card"
        xanchor 0.5
        yanchor 0.5
        xpos CAR_POS[0]
        ypos max(CAR_POS[1], MAP_TOP + 60)
        xsize 360
        padding (20, 14, 20, 14)
        vbox:
            spacing 4
            hbox:
                spacing 12
                use seal("車", 44)
                vbox:
                    yalign 0.5
                    text _("Jujutsu High") font gui.display_font size 24 color gui.paper
                    text _("Ijichi's car") style "jjk_label" size 15
            if _now:
                text _("Ijichi is at the gate with the car.") size 16 color gui.gold
            else:
                text _("Ijichi drives from the gate, mornings to afternoons.") size 16 color gui.dim

    ## The districts. An open one starts a trip while Ijichi is driving; at
    ## other times it does nothing and says when he drives.
    for _dk in DISTRICT_ORDER:
        $ _d = DISTRICTS[_dk]
        $ _pos = DISTRICT_POS.get(_dk, (960, 540))
        $ _open, _reason = district_state(_dk)
        $ _seen = (_dk in districts_visited)
        $ _go = _open and _now
        button:
            style "sb_map_district"
            xanchor 0.5
            yanchor 0.5
            xpos _pos[0]
            ypos _pos[1]
            sensitive _open
            tooltip (None if _go else _("Ijichi drives from the gate, mornings to afternoons."))
            action (Return(("district", _dk)) if _go else NullAction())
            vbox:
                spacing 5
                hbox:
                    spacing 14
                    text _d["kanji"] font gui.display_heavy_font size 44 color (gui.seal if _go else gui.mute) yalign 0.5
                    text _d["name"] font gui.display_font size 24 color (gui.paper if _open else gui.dim) yalign 0.5
                hbox:
                    spacing 6
                    frame:
                        style "sb_map_chip"
                        text _("½ day") font gui.body_medium_font size 14 color gui.dim
                    if not _open:
                        frame:
                            style "sb_map_chip"
                            text "[_reason!q]" font gui.body_medium_font size 14 color gui.seal layout "nobreak"
                    elif not _now:
                        frame:
                            style "sb_map_chip"
                            text _("Not now") font gui.body_medium_font size 14 color gui.dim
                    if _seen:
                        frame:
                            style "sb_map_chip"
                            text _("VISITED") font gui.body_medium_font size 14 color gui.gold
                text _d["desc"] size 15 color (gui.paper if _open else gui.dim)
                text _d["places"] size 14 color gui.mute

    text _("A trip takes half a day. District scenes come in a later build."):
        xalign 0.5
        yalign 1.0
        yoffset -40
        size 17
        color gui.dim
