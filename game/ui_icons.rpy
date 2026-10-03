################################################################################
## Cursed Bonds — icons and hover labels.
##
## Phase 2, P0 (PHASE2_DESIGN.md 4.3, D8 to D11, 6.1). Final: frozen after wave 0.
##
##   ICONS            {name: (kanji, word)}: the 88 icon names. A wave package
##                    never adds one; it uses an existing name.
##   ICON_FOR         {(kind, id): name} for place actions ("act"), activities
##                    ("do"), journal tabs ("tab"), rooms ("place"), areas ("area")
##   ICON_GOLD        the names drawn in gold
##   icon(name, ...)  a displayable: images/icons/ic_<name>.png when it exists,
##                    else the kanji on the game's seal
##   screen icon_btn  one icon button with a hover label
##   screen hover_label   the one place hover labels are drawn (always shown)
##   screen icon_sample   the style sample for checkpoint A
##   ui_do(fn, ...)   what a button calls: runs fn and returns None (R4)
##
## A tooltip is the tuple (text, key), the key unique on its screen (D11): the
## engine only re-captures the hovered rectangle when the tooltip's value
## changes. hover_label draws tuples only, so a plain-string tooltip is left
## to the screen that owns it.
################################################################################

init -3 python:

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

        ("tab", "people"): "people", ("tab", "missions"): "missions", ("tab", "memories"): "memories",
        ("tab", "stats"): "stats", ("tab", "equipment"): "equipment", ("tab", "inventory"): "inventory",

        ("area", "heart"): "area_heart", ("area", "school"): "area_school",
        ("area", "dorms"): "area_dorms", ("area", "staff"): "area_staff",
        ("area", "grounds"): "area_grounds", ("area", "mountain"): "area_mountain",
    }
    for _icon_loc in ("gate", "courtyard", "classroom", "cafeteria", "training", "dojo", "dorm_common",
                      "dorm", "girls_dorm", "rooftop", "infirmary", "office", "utahime_office",
                      "gojo_office", "storehouse", "forest", "riverside", "ridge", "library"):
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
        its picture when icon_has_art(name), else the kanji on the seal (a
        Text in the style icon_glyph, gold when asked). An unknown name
        draws a question mark. Build it in the line that uses it and never
        store it: screen scope is saved (R10)."""
        size = int(size)
        if name in ICONS and icon_has_art(name):
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
## left it would hide the neighbouring icon the owner is comparing.
screen hover_label():
    zorder 190

    $ _hover_tip = GetTooltip()
    $ _hover_t = icon_tip_parts(_hover_tip)
    $ _hover_side = "left"
    if isinstance(_hover_tip, tuple) and len(_hover_tip) > 1 and str(_hover_tip[1]).startswith(("sample_auto_", "sample_always_", "sample_never_")):
        $ _hover_side = "top"
    if _hover_t:
        nearrect:
            focus "tooltip"
            preferred_side _hover_side
            frame:
                background Frame("gui/panel_dark.png", 4, 4)
                padding (14, 8)
                xmaximum 520
                vbox:
                    spacing 2
                    text _hover_t[0]:
                        substitute False
                        font gui.display_font
                        color gui.paper
                        size 22
                    if _hover_t[1]:
                        text _hover_t[1]:
                            substitute False
                            color gui.dim
                            size 18


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
