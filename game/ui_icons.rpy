################################################################################
## Cursed Bonds — icons and hover labels.
##
## Phase 2, P0 (PHASE2_DESIGN.md 4.3, D8 to D11, 6.1). Final: frozen after wave 0.
##
##   ICONS            {name: (kanji, word)}: the 114 icon names (88 of phase 2,
##                    and the 26 of the second UI overhaul, laid once by U0b:
##                    docs/UI2_DESIGN.md 4.8, K11). A wave package never adds
##                    one; it uses an existing name.
##   ICON_FOR         {(kind, id): name} for place actions ("act"), activities
##                    ("do"), journal tabs ("tab"), rooms ("place"), areas ("area")
##   ICON_GOLD        the names drawn in gold
##   icon(name, ...)  a displayable: images/icons/ic_<name>.png when it exists,
##                    else the kanji on the game's seal
##   screen icon_btn  one icon button with a hover label
##   screen hover_label   the one place hover labels are drawn (always shown)
##   icon_tip_side, icon_tip_place   where a label opens: by its key, and (after
##                    checkpoint D) for a tile of the place view's icon column
##                    by what stands beside the column
##   screen icon_sample   the style sample for checkpoint A
##   ui_do(fn, ...)   what a button calls: runs fn and returns None (R4)
##
## A tooltip is the tuple (text, key), the key unique on its screen (D11): the
## engine only re-captures the hovered rectangle when the tooltip's value
## changes. hover_label draws tuples only, so a plain-string tooltip is left
## to the screen that owns it.
################################################################################

init -3 python:
    import builtins

    ICONS = {
        ## HUD (9)
        "map":           (u"図", "Map"),
        "journal":       (u"記", "Journal"),
        "menu":          (u"設", "Menu"),
        "back":          (u"戻", "Back"),
        "close":         (u"閉", "Close"),
        "stay":          (u"留", "Stay here"),
        "stamina_low":   (u"疲", "Running on empty"),
        "moon":          (u"月", "Night"),
        "skip":          (u"飛", "Skipping"),
        ## journal (9)
        "people":        (u"人", "People"),
        "missions":      (u"任", "Missions"),
        "stats":         (u"力", "Stats"),
        "equipment":     (u"装", "Equipment"),
        "inventory":     (u"品", "Inventory"),
        "story":         (u"物", "Their story"),
        "memories":      (u"憶", "Memories"),
        "now":           (u"今", "Right now"),
        "go":            (u"行", "Go there"),
        ## map (11)
        "area_heart":    (u"門", "Courtyard & Gate"),
        "area_school":   (u"校", "School Building"),
        "area_dorms":    (u"寮", "Dormitories"),
        "area_staff":    (u"職", "Staff Building"),
        "area_grounds":  (u"練", "Training Grounds"),
        "area_mountain": (u"山", "The Mountain"),
        "campus":        (u"校", "Campus"),
        "tokyo":         (u"京", "Tokyo"),
        "district":      (u"街", "District"),
        "lock":          (u"錠", "Locked"),
        "news":          (u"新", "Something new"),
        ## places (20)
        "place_gate":           (u"門", "Main Gate"),
        "place_courtyard":      (u"庭", "Courtyard"),
        "place_classroom":      (u"教", "Classroom"),
        "place_cafeteria":      (u"食", "Cafeteria"),
        "place_training":       (u"鍛", "Training Hall"),
        "place_dojo":           (u"道", "Dojo"),
        "place_dorm_common":    (u"居", "Common Room"),
        "place_dorm":           (u"室", "My Room"),
        "place_girls_dorm":     (u"女", "Girls' Dormitory"),
        "place_rooftop":        (u"屋", "Rooftop"),
        "place_infirmary":      (u"医", "Infirmary"),
        "place_office":         (u"長", "Principal's Office"),
        "place_utahime_office": (u"歌", "Utahime's Office"),
        "place_gojo_office":    (u"五", "Gojo's Office"),
        "place_storehouse":     (u"蔵", "Storehouse"),
        "place_forest":         (u"森", "Forest Trail"),
        "place_riverside":      (u"川", "Riverside"),
        "place_ridge":          (u"峰", "Mountain Ridge"),
        "place_library":        (u"書", "Library"),
        "place_later":          (u"後", "Later build"),
        ## actions (18)
        "sleep":         (u"眠", "Sleep"),
        "night_bed":     (u"床", "Go to bed"),
        "wait":          (u"待", "Wait"),
        "study":         (u"学", "Study"),
        "train":         (u"技", "Train"),
        "swim":          (u"泳", "Swim"),
        "eat":           (u"膳", "Eat"),
        "rest":          (u"休", "Get patched up"),
        "think":         (u"想", "Sit a while"),
        "hold":          (u"刻", "Hold the hour"),
        "tools":         (u"具", "Look through the racks"),
        "armory":        (u"武", "Armory"),
        "veil":          (u"帳", "Look up at the veil"),
        "car":           (u"車", "Ask for a ride"),
        "board":         (u"札", "Mission board"),
        "release":       (u"放", "Let them go"),
        "mission":       (u"命", "Mission"),
        "act":           (u"為", "Do it"),
        ## person choices (9)
        "talk":          (u"話", "Talk"),
        "hang":          (u"遊", "Spend time together"),
        "lesson":        (u"授", "Take the lesson"),
        "walk":          (u"歩", "Walk with them"),
        "stargaze":      (u"星", "Sit out with them"),
        "confide":       (u"告", "Tell them something true"),
        "stand":         (u"頼", "They asked me for something"),
        "heart":         (u"恋", "Something closer"),
        "invite":        (u"誘", "Ask them along"),
        ## rooms and night (12)
        "pc_open":       (u"電", "My computer"),
        "cards_play":    (u"賭", "Cards"),
        "fish_cast":     (u"釣", "Fish"),
        "lib_study":     (u"読", "Study in the stacks"),
        "look":          (u"見", "Look"),
        "spot_vend":     (u"販", "Vending machine"),
        "night_gojo":    (u"夜", "Train until morning"),
        "night_out":     (u"宵", "A night in town"),
        "market":        (u"市", "The Black Market"),
        "buy":           (u"買", "Buy"),
        "take":          (u"取", "Take"),
        "record":        (u"録", "Record book"),
        ## The second UI overhaul (docs/UI2_DESIGN.md 4.8; U0b): 26 more, all
        ## on sheet 4 (tools/icons/sheet_4.txt), in this order.
        ## the new places (11)
        "place_boys_dorm":       (u"男", "Boys' Dormitory"),
        "place_yuji_room":       (u"悠", "Yuji's Room"),
        "place_megumi_room":     (u"恵", "Megumi's Room"),
        "place_senpai_room":     (u"輩", "Panda and Toge's Room"),
        "place_nobara_room":     (u"野", "Nobara's Room"),
        "place_maki_room":       (u"真", "Maki's Room"),
        "place_teachers_lounge": (u"憩", "Teachers' Lounge"),
        "place_teachers_dorm":   (u"師", "Teachers' Dormitory"),
        "place_bathhouse":       (u"湯", "Onsen"),
        "place_sauna":           (u"蒸", "Sauna"),
        "place_pool":            (u"水", "Swimming Pool"),
        ## the five yards (5): used once the picture is cut (path_icon in
        ## room_paths.rpy, map_pin_icon in ui_map.rpy); until then a yard
        ## keeps its area's icon, as in phase 2
        "place_school_yard":     (u"舎", "School Courtyard"),
        "place_dorm_yard":       (u"園", "Dormitory Garden"),
        "place_staff_yard":      (u"階", "Staff Building Steps"),
        "place_training_yard":   (u"場", "Training Yard"),
        "place_trailhead":       (u"径", "Mountain Path"),
        ## actions (4)
        "bath_soak":     (u"浴", "Soak"),
        "bath_sauna":    (u"熱", "Sit it out"),
        "pool_swim":     (u"游", "Swim"),
        "cards_invite":  (u"招", "Ask someone to the table"),
        ## the three the quick menu has no icon for (3), and three more (3)
        "history":       (u"歴", "History"),
        "auto":          (u"自", "Auto"),
        "save":          (u"保", "Save"),
        "help":          (u"助", "How to play"),
        "continue":      (u"続", "Continue"),
        "at_home":       (u"宅", "At home"),
    }

    ## (kind, id) -> icon name. Kinds: "act" a place action id, "do" an
    ## activity id, "tab" a journal tab, "place" a room, "area" a map area.
    ## A mission ("mission", any id) always gets the `mission` icon, and
    ## anything not listed gets `act` (icon_for).
    ICON_FOR = {
        ("act", "sleep"): "sleep", ("act", "study"): "study", ("act", "train"): "train",
        ("act", "swim"): "swim", ("act", "eat"): "eat", ("act", "rest"): "rest",
        ("act", "tools"): "tools", ("act", "think"): "think", ("act", "hold"): "hold",
        ("act", "wait"): "wait", ("act", "explore_time"): "wait", ("act", "veil"): "veil",
        ("act", "car"): "car", ("act", "board"): "board", ("act", "armory"): "armory",
        ("act", "release"): "release", ("act", "night_bed"): "night_bed",
        ("act", "night_gojo"): "night_gojo", ("act", "pc_open"): "pc_open",
        ("act", "cards_play"): "cards_play", ("act", "fish_cast"): "fish_cast",
        ("act", "lib_study"): "lib_study", ("act", "spot_vend"): "spot_vend",

        ("do", "talk"): "talk", ("do", "hang"): "hang", ("do", "eat"): "eat",
        ("do", "train"): "train", ("do", "study"): "study", ("do", "swim"): "swim",
        ("do", "walk"): "walk", ("do", "invite"): "invite", ("do", "stargaze"): "stargaze",
        ("do", "lesson"): "lesson", ("do", "confide"): "confide", ("do", "stand"): "stand",
        ("do", "rom_town"): "heart", ("do", "rom_close"): "heart", ("do", "rom_say"): "heart",
        ("do", "int_night"): "heart", ("do", "int_morning"): "heart", ("do", "int_day"): "heart",
        ("do", "int_after"): "heart",
        ## "Swim together" at the pool takes the river's icon (4.8: no new icon).
        ("do", "swim_pool"): "swim",

        ("tab", "people"): "people", ("tab", "missions"): "missions", ("tab", "memories"): "memories",
        ("tab", "stats"): "stats", ("tab", "equipment"): "equipment", ("tab", "inventory"): "inventory",

        ("area", "heart"): "area_heart", ("area", "school"): "area_school",
        ("area", "dorms"): "area_dorms", ("area", "staff"): "area_staff",
        ("area", "grounds"): "area_grounds", ("area", "mountain"): "area_mountain",
    }
    for _icon_loc in ("gate", "courtyard", "classroom", "cafeteria", "training", "dojo", "dorm_common",
                      "dorm", "girls_dorm", "rooftop", "infirmary", "office", "utahime_office",
                      "gojo_office", "storehouse", "forest", "riverside", "ridge", "library",
                      ## the eleven places of the second overhaul (a row for a
                      ## place that is not built yet is never read)
                      "boys_dorm", "yuji_room", "megumi_room", "senpai_room",
                      "nobara_room", "maki_room", "teachers_lounge", "teachers_dorm",
                      "bathhouse", "sauna", "pool"):
        ICON_FOR[("place", _icon_loc)] = "place_" + _icon_loc
    del _icon_loc

    ICON_GOLD = {"mission", "night_gojo"}

    ICON_ART = "images/icons/ic_%s.png"     # a 96x96 picture drops in by name
    ICON_SEAL = "gui/seal_44.png"           # the stand-in's ground

    def ui_do(fn, *args, **kwargs):
        """P0 (ui_icons.rpy), final. Calls fn(*args, **kwargs) and returns
        None, always, whatever fn returned: a button's
        Function(ui_do, fn, ...) can never end its screen's interaction by
        accident (R4)."""
        fn(*args, **kwargs)
        return None

    def icon_has_art(name):
        """P0 (ui_icons.rpy), final. bool: the icon's picture
        (images/icons/ic_<name>.png) is on disk."""
        return bool(renpy.loadable(ICON_ART % name))

    def icon_label(name):
        """P0 (ui_icons.rpy), final. The icon's word as a str ("Map"), or
        the name itself for one the table doesn't have."""
        row = ICONS.get(name)
        return row[1] if row else str(name)

    ## The twelve icons on the style sample's rows: one-word names, so every
    ## button in a row is the same height in the two word modes.
    ICON_SAMPLE = ("map", "journal", "menu", "train", "study", "eat",
                   "sleep", "talk", "wait", "mission", "look", "fish_cast")

    def icon_for(kind, id):
        """P0 (ui_icons.rpy), final. The icon name (a str, never None) for a
        place action ("act"), an activity ("do"), a journal tab ("tab"), a
        room ("place") or an area ("area"). A mission ("mission", any id) is
        always "mission"; anything unmapped is "act"."""
        if kind == "mission":
            return "mission"
        return ICON_FOR.get((kind, id), "act")

    def icon(name, size=40, gold=False):
        """P0 (ui_icons.rpy), final. The icon as a displayable, size x size:
        its picture when icon_has_art(name) (tinted gold when asked: the
        pictures are white, D23), else the kanji on the seal (a Text in the
        style icon_glyph, gold when asked). An unknown name draws a question
        mark. Build it in the line that uses it and never store it: screen
        scope is saved (R10)."""
        size = int(size)
        if name in ICONS and icon_has_art(name):
            if gold:
                return Transform(ICON_ART % name, xysize=(size, size), matrixcolor=TintMatrix(gui.gold))
            return Transform(ICON_ART % name, xysize=(size, size))
        glyph = ICONS[name][0] if name in ICONS else u"？"
        return Fixed(
            Transform(ICON_SEAL, xysize=(size, size)),
            Text(glyph, style="icon_glyph", size=max(8, int(size * 0.55)),
                 color=(gui.gold if gold else gui.paper), xalign=0.5, yalign=0.5),
            xysize=(size, size))

    def icon_words_shown(name, words=None):
        """P0 (ui_icons.rpy). bool: an icon button shows its word under the
        icon. words="always" forces it and any other value hides it; None
        follows gui.icon_words ("always", "never", or "auto": only while
        the icon has no picture)."""
        if words is not None:
            return words == "always"
        if gui.icon_words == "always":
            return True
        return gui.icon_words == "auto" and not icon_has_art(name)

    def icon_tip_parts(tip):
        """P0 (ui_icons.rpy). (first line, the rest) of a hover label's text,
        or None when the tooltip isn't hover_label's to draw: it draws only
        the tuple (text, key) (D11)."""
        if not (isinstance(tip, tuple) and len(tip) == 2 and tip[0]):
            return None
        head, _sep, rest = str(tip[0]).partition("\n")
        return head, rest

    ## Which side of its button a hover label opens on, by the tooltip key's
    ## first letters (the first row that fits wins; any other key: "left").
    ## After checkpoint D a tile of the place view's icon column (a "rail_"
    ## key) is not placed by this table alone: icon_tip_place() looks at what
    ## stands beside the column.
    ## A label on the left would cover the neighbour in a row: the next
    ## corner button or status chip, the next name tag, the next exit.
    ## Two district markers open to the right, clear of the markers below them.
    ## A room pin on the map's area level opens above, centred on the pin
    ## (ICON_TIP_CENTRED), clear of the next pin; the rows before ("row_",)
    ## are the pins with another pin above them, as the pins stand in
    ## game/layout/area_*.json today (tools/smoke/p2_map.rpy measures all six
    ## areas: re-check these rows if a pin moves).
    ##
    ## The second overhaul (U0c2; docs/UI2_DESIGN.md 3.1): this table is no
    ## longer the only source for the place view's hotspots and exits. A
    ## picture's sidecar may carry its own sides ("tips" in
    ## game/layout/hot_<place>.json) and those win; see icon_tip_side.
    ICON_TIP_SIDES = (
        (("sample_auto_", "sample_always_", "sample_never_"), "top"),
        (("hud_map", "hud_journal", "hud_menu", "hud_chip_"), "bottom"),
        (("tag_", "stage_"), "top"),
        (("hot_go_courtyard__training_yard",), "left"),
        ## The second UI overhaul (U0b): "To the Boys' Dormitory" is wider than
        ## "To My Room" was, and above its exit it would lie over the garden's
        ## exit to the Mountain Path. It opens to the right, where the garden
        ## is clear. (The garden's own picture brings its sidecar's sides.)
        (("hot_go_dorm_yard__boys_dorm",), "right"),
        (("hot_go_", "hot_computer"), "top"),
        (("map_campus", "map_tokyo"), "bottom"),
        (("row_school_yard", "row_staff_yard", "row_training_yard"), "left"),
        (("row_trailhead",), "right"),
        (("row_dorm_common", "row_storehouse", "row_library"), "bottom"),
        (("row_",), "top"),
        (("district_go", "district_night"), "left"),
        (("district_shinjuku", "district_harajuku"), "right"),
        (("district_",), "bottom"),
        (("jr_now", "jr_stage_", "jr_chapter_", "jr_unmet_", "jr_strength"), "bottom"),
        (("jr_card_",), "top"),
    )

    ## The table's general row for exits (and the computer): a key that only
    ## this row fits has no side of its own, and is placed from where its
    ## tile is (icon_tip_where).
    ICON_TIP_GENERAL = ("hot_go_", "hot_computer")

    ## Keys whose label is centred on its button when it opens above or below.
    ICON_TIP_CENTRED = ("row_",)

    def icon_tip_centred(tip):
        """P8 (ui_icons.rpy). 0.5 when the hovered button's label is centred
        on it (a map pin), else 0.0 (its left edge on the button's)."""
        if isinstance(tip, tuple) and len(tip) > 1 and str(tip[1]).startswith(ICON_TIP_CENTRED):
            return 0.5
        return 0.0

    ICON_SIDES = ("top", "bottom", "left", "right")

    def icon_tip_hot(key):
        """U0c2 (ui_icons.rpy). The side the hover label of a hotspot or an
        exit of the place I stand in opens on, from the picture's own
        numbers, or None when they give none (docs/UI2_DESIGN.md 3.1, K2):
        the key "tips" of game/layout/hot_<here>.json, {id: side}, the id
        being the hotspot's or the exit's ("go_<from>__<to>"), without the
        "hot_" its tooltip key starts with."""
        if not key.startswith("hot_"):
            return None
        tips = rule_layout("hot_" + str(store.here)).get("tips")
        side = tips.get(key[len("hot_"):]) if isinstance(tips, builtins.dict) else None
        return side if side in ICON_SIDES else None

    def icon_tip_where(tip, side):
        """U0c2 (ui_icons.rpy). The side a hotspot's or an exit's label opens
        on when neither its sidecar nor a row of its own in ICON_TIP_SIDES
        says: `side` (the table's general answer: above an exit, left of
        anything else), unless the label would leave the screen there, and
        then the opposite side. Worked out from where the tile is: its
        point as the place shows it now, and the label's own size."""
        key = str(tip[1])
        size = icon_tip_size(tip)
        if size is None or renpy.get_screen("sb_place") is None:
            return side
        for h in hot_spots_for(store.here):
            if "hot_" + str(h["id"]) == key:
                x, y, w, hh = hot_rect(h["x"], h["y"])
                if side == "top" and y - 12 - size[1] < 0:
                    return "bottom"
                if side == "left" and x - 12 - size[0] < 0:
                    return "right"
                break
        return side

    def icon_tip_side(tip):
        """P8 (ui_icons.rpy). "left", "right", "top" or "bottom": the side of the
        hovered button hover_label opens on, from the tooltip's key (D11:
        the tooltip stays the tuple (text, key)). A tile of the icon column
        answers "left" here; icon_tip_place() then decides where its label
        really goes.

        The second overhaul (U0c2): for a hotspot or an exit of the place
        view (a "hot_" key) the picture's sidecar is asked first (the key
        "tips" of hot_<place>.json, icon_tip_hot); then this table, as
        before; and a hotspot or exit with no row of its own here (only the
        general "hot_go_" row, or none) is placed from where its tile is
        (icon_tip_where)."""
        if isinstance(tip, tuple) and len(tip) > 1:
            key = str(tip[1])
            side = icon_tip_hot(key)
            if side:
                return side
            for heads, side in ICON_TIP_SIDES:
                if key.startswith(heads):
                    if key.startswith("hot_") and heads == ICON_TIP_GENERAL:
                        return icon_tip_where(tip, side)
                    return side
            if key.startswith("hot_"):
                return icon_tip_where(tip, "left")
        return "left"

    ## The hover label's own measures (screen hover_label draws with them and
    ## icon_tip_size() measures with them): the frame's widest, its padding,
    ## the title's and the hint's text size, the gap between the two.
    ICON_TIP_W = 520
    ICON_TIP_PAD = (14, 8)
    ICON_TIP_TEXT = (22, 18)
    ICON_TIP_GAP = 2

    ## After checkpoint D (5 Oct 2026, the owner: "Make the label open
    ## above."). A tile of the place view's icon column used to open its
    ## label to the left, over whatever stood beside the column: an exit, a
    ## hotspot, the riverside's bank. Opening the first tile's label above
    ## its icon clears the courtyard, but not the library (the label above
    ## still lands on the exit) nor the riverside (the tiles that hide the
    ## bank are the second and third). So the label looks before it opens:
    ##   - the top tile of a column opens its label above the tile, its
    ##     right edge on the tile's, when nothing is there;
    ##   - otherwise, and for every other tile, the label stays beside the
    ##     column and moves up or down to the nearest height where it hides
    ##     nothing.
    ## "Nothing" is: every exit and hotspot the place shows now (their 72 px
    ## buttons), the toast lane with the corner buttons above it, and the
    ## screen's edges. A label never covers its own tile either way.

    def icon_tip_column(tip):
        """After checkpoint D (ui_icons.rpy). bool: the tooltip belongs to a
        tile of the place view's icon column (a "rail_" key; the "+N"
        chip's names, "rail_more_", are not tiles)."""
        if not (isinstance(tip, tuple) and len(tip) == 2):
            return False
        key = str(tip[1])
        return key.startswith("rail_") and not key.startswith("rail_more_") and renpy.get_screen("sb_place") is not None

    def icon_tip_size(tip):
        """After checkpoint D (ui_icons.rpy). (w, h) in pixels of the hover
        label hover_label draws for this tooltip, measured without drawing
        it; None when it draws none."""
        parts = icon_tip_parts(tip)
        if not parts:
            return None
        room = ICON_TIP_W - 2 * ICON_TIP_PAD[0]
        w, h = Text(parts[0], style="text", substitute=False, font=gui.display_font, size=ICON_TIP_TEXT[0]).size(room, config.screen_height)
        if parts[1]:
            w2, h2 = Text(parts[1], style="text", substitute=False, size=ICON_TIP_TEXT[1]).size(room, config.screen_height)
            w, h = max(w, w2), h + ICON_TIP_GAP + h2
        return (int(w) + 2 * ICON_TIP_PAD[0], int(h) + 2 * ICON_TIP_PAD[1])

    def icon_tip_blocks(loc):
        """After checkpoint D (ui_icons.rpy). The (x, y, w, h) rectangles a
        column tile's label keeps off in a place: the exits and hotspots
        showing now, and the screen's top right corner down to the foot of
        the toast lane (the toasts, and the corner buttons above them)."""
        out = [hot_rect(h["x"], h["y"]) for h in hot_spots_for(loc)]
        out.append((TOAST_LANE[0], 0, config.screen_width - TOAST_LANE[0], TOAST_LANE[3]))
        return out

    def icon_tip_spot(rect, size, top, blocks):
        """After checkpoint D (ui_icons.rpy). Where a column tile's label
        goes: (side, x anchor, y shift). `rect` is the tile, `size` the
        label, `top` whether the tile is the first of its column, `blocks`
        what the label keeps off. ("top", 1.0, 0): above the tile, right
        edges together. ("left", 0.0, n): beside the tile, n pixels down
        (up when negative) from the tile's top edge."""
        x, y, w, h = [int(v) for v in rect]
        lw, lh = size

        def clear(r):
            return (r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= config.screen_width and r[1] + r[3] <= config.screen_height
                    and not any(hot_overlap(r, b) for b in blocks))

        if top and y - lh > 0 and clear((x + w - lw, y - lh, lw, lh)):
            return ("top", 1.0, 0)
        for d in range(config.screen_height):
            for dy in (-d, d):
                if clear((x - lw, y + dy, lw, lh)):
                    return ("left", 0.0, dy)
        return ("left", 0.0, 0)

    def icon_tip_place(tip):
        """After checkpoint D (ui_icons.rpy). (side, x anchor, y shift): how
        hover_label places the label of the hovered button. Any button but
        a tile of the icon column: (icon_tip_side(tip),
        icon_tip_centred(tip), 0), as before. A column tile: icon_tip_spot's
        answer for the tile as it is drawn now. Plain values only (the
        screen keeps them)."""
        plain = (icon_tip_side(tip), icon_tip_centred(tip), 0)
        if not icon_tip_column(tip):
            return plain
        rect = GetFocusRect("tooltip")
        size = icon_tip_size(tip)
        if not rect or not size:
            return plain
        loc = store.here
        tops = [col[0][5] for col in rail_layout(rail_rows(loc))[0] if col]
        return icon_tip_spot(rect, size, tip[1] in tops, icon_tip_blocks(loc))

    def icon_validate():
        """P0 (ui_icons.rpy). Lint findings for the icon tables."""
        out = []
        for key, name in sorted(ICON_FOR.items()):
            if name not in ICONS:
                out.append("ICON_FOR %r names an unknown icon %r" % (key, name))
        for name in sorted(ICON_GOLD):
            if name not in ICONS:
                out.append("ICON_GOLD names an unknown icon %r" % name)
        for name, row in sorted(ICONS.items()):
            if not (isinstance(row, tuple) and len(row) == 2 and row[0] and row[1]):
                out.append("ICONS[%r] must be (kanji, word)" % name)
        if gui.icon_words not in ("auto", "always", "never"):
            out.append("gui.icon_words is %r (auto, always or never)" % (gui.icon_words,))
        return out

init python:

    register_validator(icon_validate)

    ## The hover label sits over everything, in every context (D10).
    config.always_shown_screens.append("hover_label")


## The kanji of a stand-in icon. tools/smoke's zz_words skips this style, so a
## screen's word count is the same with and without icon art (D48).
style icon_glyph is text:
    font gui.display_heavy_font
    color gui.paper

style icon_btn_button is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    selected_background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (4, 4, 4, 4)

style icon_btn_word is text:
    font gui.body_medium_font
    color gui.dim
    size 13
    text_align 0.5


## One icon button (4.3). `w or size + 12` wide; the icon centred; `pips` cost
## diamonds under it; its word under that while words show (icon_words_shown).
## The hover label is `tip`, or the icon's word. `wid` is both the button's id
## and the tooltip's key, so two buttons with one icon on a screen need one each.
screen icon_btn(name, action, tip=None, size=52, w=None, gold=False, selected=False, pips=0, wid=None, words=None):
    $ _icon_w = (w or size + 12)
    button:
        id wid
        style "icon_btn_button"
        xsize _icon_w
        yminimum size + 12
        action action
        selected (True if selected else None)
        tooltip ((tip or icon_label(name)), (wid or name))
        vbox:
            xalign 0.5
            yalign 0.5
            spacing 2
            add icon(name, size, (gold or name in ICON_GOLD)) xalign 0.5
            if pips:
                hbox:
                    xalign 0.5
                    spacing 3
                    for _icon_k in range(pips):
                        add "gui/pip_small.png"
            if icon_words_shown(name, words):
                text icon_label(name):
                    style "icon_btn_word"
                    substitute False
                    xalign 0.5
                    xmaximum max(_icon_w - 8, 40)


## The hover label (4.3, D10): always shown, above everything. It draws only a
## tuple tooltip (text, key), beside the hovered button, on the left when there
## is room. "Title\nhint": the first line large, the rest small and dim.
## Over the style sample's icon rows it sits above the icon instead: on the
## left it would hide the neighbouring icon the owner is comparing. The same
## goes for every row of buttons: icon_tip_side() picks the side by the key.
## After checkpoint D a tile of the place view's icon column is placed by
## icon_tip_place(): the column's top tile opens its label above the tile
## when nothing is there; any other column label sits beside the column, moved
## up or down until it hides no exit, no hotspot and no toast.
screen hover_label():
    zorder 190

    $ _hover_tip = GetTooltip()
    $ _hover_t = icon_tip_parts(_hover_tip)
    $ _hover_side, _hover_mid, _hover_dy = icon_tip_place(_hover_tip)
    if _hover_t:
        nearrect:
            focus "tooltip"
            preferred_side _hover_side
            frame:
                background Frame("gui/panel_dark.png", 4, 4)
                padding ICON_TIP_PAD
                xmaximum ICON_TIP_W
                xpos _hover_mid
                xanchor _hover_mid
                ypos _hover_dy
                vbox:
                    spacing ICON_TIP_GAP
                    text _hover_t[0]:
                        substitute False
                        font gui.display_font
                        color gui.paper
                        size ICON_TIP_TEXT[0]
                    if _hover_t[1]:
                        text _hover_t[1]:
                            substitute False
                            color gui.dim
                            size ICON_TIP_TEXT[1]


## The style sample (checkpoint A): Review tools, "Style sample". Twelve icon
## buttons in each of the three gui.icon_words modes, the five grade chips at
## two sizes, and one person-view choice button. Returns ("close",).
screen icon_sample():

    tag sandbox

    ## A harness's autoplay never waits on it.
    if smoke_autoplay:
        timer 0.05 action Return(("close",))

    key "game_menu" action Return(("close",))

    add graded_bg()
    add Solid("#07060cd8")

    frame:
        style "jjk_panel"
        xpos 110
        ypos 60
        ## 110 to 1400: clear of the toast stack (x 1420 to 1880), which still
        ## draws over this screen until toast_room() makes toasts wait here.
        xsize 1290
        padding (40, 30)

        vbox:
            spacing 20

            hbox:
                spacing 24
                text _("Style sample") font gui.display_font color gui.paper size 40
                text _("Rest the pointer on an icon for its name. Nothing here changes the game.") color gui.dim size 18 yalign 0.8

            for _icon_mode, _icon_note in (("auto", _("Words while an icon has no picture (the default)")),
                                           ("always", _("Words always")),
                                           ("never", _("Icons only"))):
                vbox:
                    spacing 6
                    text _icon_note style "jjk_label"
                    hbox:
                        spacing 10
                        for _icon_n in ICON_SAMPLE:
                            use icon_btn(_icon_n, NullAction(), size=52, w=90,
                                         wid="sample_%s_%s" % (_icon_mode, _icon_n),
                                         words=(None if _icon_mode == "auto" else _icon_mode))

            vbox:
                spacing 8
                text _("Grade chips") style "jjk_label"
                for _icon_size in (13, 18):
                    hbox:
                        spacing 12
                        for _icon_g in ("g4", "g3", "g2", "s1", "g1", "sp"):
                            use grade_chip(_icon_g, size=_icon_size)
                        use grade_chip("sp", size=_icon_size, text="Off the scale")
                        use grade_chip(None, size=_icon_size, text="Doctor")
                        use grade_chip("g2", size=_icon_size, dim=True)

            vbox:
                spacing 8
                text _("A choice in the person view") style "jjk_label"
                button:
                    id "sample_choice"
                    style "sb_action_button"
                    xsize 600
                    action NullAction()
                    tooltip ("Spend time together\nWhatever they're doing, do it with them. · 1 period", "sample_choice")
                    fixed:
                        ysize 44
                        hbox:
                            spacing 14
                            yalign 0.5
                            add icon("hang", 40) yalign 0.5
                            text _("Spend time together") font gui.display_font color gui.paper size 24 yalign 0.5
                        add "gui/pip_small.png" xalign 1.0 yalign 0.5

            hbox:
                xfill True
                text _("Which icon mode reads best, and do the chips look right?") color gui.dim size 18 yalign 0.5
                textbutton _("Close"):
                    id "sample_close"
                    xalign 1.0
                    style "sb_hud_nav_button"
                    action Return(("close",))
