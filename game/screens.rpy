################################################################################
## Cursed Bonds — engine screens.
##
## Every screen Ren'Py expects (say, choice, menus, saves, prefs, history …)
## restyled against gui.rpy. No hex values here; see gui.rpy for the palette.
################################################################################


################################################################################
## Shared helpers
################################################################################

## The game's fonts (Shippori Mincho, Zen Kaku Gothic New) have no Latin
## Extended-A letters, so "Zankō", "Ryōsuke", "Kantō" and "Sōma" lost their
## ō. These font groups take those letters (and ✓ ◌ ∞) from Ren'Py's bundled
## DejaVu Sans (its Bold cut for the bold bases) and everything else from the
## base font. Built at init -1, after gui.rpy's fonts (-2) and before any style
## or screen that uses them. At init 999 every style whose font is still one of
## the plain base files (gui.text_properties() sets many) gets its group too.
init -1 python:

    MACRON_FONTS = {}

    def macron_fallback(base):
        """WP8. The DejaVu cut that matches `base`: Bold for a bold file."""
        if "Bold" in str(base):
            return "DejaVuSans-Bold.ttf"
        return "DejaVuSans.ttf"

    def macron_font(base):
        """WP8. `base` as a FontGroup that draws U+0100-017F (ō, ū, ā ...)
        and ✓ ◌ ∞ in DejaVu Sans. One group per base font, built at init."""
        fg = MACRON_FONTS.get(base)
        if fg is None:
            dv = macron_fallback(base)
            fg = FontGroup()
            fg.add(dv, 0x0100, 0x017F)
            for _c in (0x2713, 0x25CC, 0x221E):
                fg.add(dv, _c, _c)
            fg.add(base, None, None)
        return fg

    for _mf in (gui.text_font, gui.name_text_font, gui.interface_text_font,
                gui.display_font, gui.display_heavy_font, gui.body_font,
                gui.body_medium_font, gui.body_bold_font):
        MACRON_FONTS[_mf] = macron_font(_mf)
    del _mf

init 999 python:

    def macron_styles():
        """WP8. Give every style whose font (or prefixed font) is still a
        plain base file its macron group, in place. Returns how many it
        changed. The game's style statements are deferred (gui.init sets
        config.defer_styles), so this runs from config.init_system_styles,
        which Ren'Py calls right after it applies them and before it builds
        the styles, at startup and on every GUI rebuild."""
        n = 0
        for _s in list(renpy.style.styles.values()):
            for _d in (getattr(_s, "properties", None) or ()):
                for _k in list(_d.keys()):
                    if not _k.endswith("font") or "emoji" in _k:
                        continue
                    _v = _d[_k]
                    if isinstance(_v, str) and _v in MACRON_FONTS:
                        _d[_k] = MACRON_FONTS[_v]
                        n += 1
        macron_styles.changed = getattr(macron_styles, "changed", 0) + n
        return n

    def _macron_system_styles(_orig=config.init_system_styles):
        if _orig is not None:
            _orig()
        try:
            macron_styles()
        except Exception:
            pass

    config.init_system_styles = _macron_system_styles

init python:

    def mc_portrait_label():
        """WP8 (4.11). The portrait preference's label: "[mc_name]'S
        PORTRAIT" once Gojo has asked for the name, "MY PORTRAIT" on the
        main menu and before that (nobody says the name before he asks).
        The rule is the journal's jr_name_known(), which the Stats tab uses too."""
        if not jr_name_known():
            return _("MY PORTRAIT")
        return _("[mc_name!u]'S PORTRAIT")

    _speaker_cache = {}

    def speaker_color(who):
        """Colour of the character currently speaking, for the name underline.
        Falls back to the accent for the narrator and unknown names."""
        if not who:
            return gui.violet
        if who in _speaker_cache:
            return _speaker_cache[who]
        col = _find_speaker_color(who)
        _speaker_cache[who] = col
        return col

    def _find_speaker_color(who):
        for name in dir(store):
            obj = getattr(store, name, None)
            if isinstance(obj, renpy.character.ADVCharacter) and obj.name:
                try:
                    if renpy.substitute(obj.name) == who:
                        return obj.who_args.get("color", gui.violet)
                except Exception:
                    continue
        return gui.violet


## A red hanko seal with a kanji in it. The one motif; used for section marks.
screen seal(k="呪", size=44):
    fixed:
        xysize (size, size)
        add "gui/seal_%d.png" % size
        text k:
            font gui.display_heavy_font
            color gui.seal
            size int(size * 0.58)
            xalign 0.5
            yalign 0.5


## A hairline rule with a small diamond at its left end.
screen rule(width=None):
    fixed:
        if width:
            xsize width
        else:
            xfill True
        ysize 12
        add Solid(gui.line) xsize 1.0 ysize 1 yalign 0.5
        add "gui/pip_small.png" xpos 0 yalign 0.5


################################################################################
## Base styles
################################################################################

style default:
    properties gui.text_properties()
    font macron_font(gui.text_font)
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")

style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5

style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")

style bar:
    ysize gui.bar_size
    left_bar Solid(gui.violet)
    right_bar Solid(gui.line)

style vbar:
    xsize gui.bar_size
    top_bar Solid(gui.violet)
    bottom_bar Solid(gui.line)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"

style frame:
    padding gui.frame_borders.padding
    background Frame("gui/panel.png", gui.frame_borders, tile=gui.frame_tile)


## Reusable text roles ---------------------------------------------------------

style jjk_display is text:
    font macron_font(gui.display_font)
    color gui.paper

style jjk_label is text:
    font macron_font(gui.body_medium_font)
    color gui.dim
    size 17
    kerning gui.track

style jjk_small is text:
    color gui.dim
    size 20


################################################################################
## In-game screens
################################################################################

## Say -------------------------------------------------------------------------
##
## No box. A gradient rises from the bottom of the screen; the speaker's name
## sits above the line in the display face with a short bar in their colour.

screen say(who, what):

    window:
        id "window"

        if who is not None:

            $ _wc = speaker_color(who)

            window:
                id "namebox"
                style "namebox"
                vbox:
                    spacing 6
                    text who id "who"
                    add Solid(_wc) xsize 56 ysize 3

        text what id "what"

    ## The speaker's portrait, when they are off screen (WP8, 4.11). At zoom
    ## 0.8 the widest portrait is 288x178, inside the 300px margin the name
    ## and the dialogue start at, so it never overlaps the text. The prologue's
    ## blackout hides every portrait (hide_side_images), and the player can
    ## hide their own (Preferences, "[mc_name]'s portrait").
    if not renpy.variant("small") and not hide_side_images:
        if persistent.mc_face or renpy.get_say_image_tag() != "mc":
            add SideImage() xpos 6 yalign 1.0 zoom 0.8 id "side_portrait"


init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label

style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height
    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    background None
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    font macron_font(gui.name_text_font)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")
    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos
    line_spacing 6
    adjust_spacing False


## Input -----------------------------------------------------------------------

screen input(prompt):

    style_prefix "input"

    window:

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos
            spacing 14

            text prompt style "input_prompt"
            input id "input"
            add Solid(gui.violet) xsize 320 ysize 2

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign
    properties gui.text_properties("input_prompt")
    color gui.dim

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width
    font macron_font(gui.display_font)
    size 40
    color gui.paper


## Choice ----------------------------------------------------------------------
##
## Left-aligned panels; the hovered one grows a violet rail.

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action

style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 200
    yanchor 0.0
    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")
    background Frame("gui/panel.png", 8, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 8, 4)

style choice_button_text is default:
    properties gui.text_properties("choice_button")
    font macron_font(gui.choice_button_text_font)


## Quick menu ------------------------------------------------------------------
##
## D25: BACK · HISTORY · SKIP · AUTO · SAVE · JOURNAL · MENU. It hides itself
## while any screen tagged sandbox (the campus) or menu (the journal, the game
## menu) is showing, so it only appears in dialogue. MENU opens the game menu,
## whose navigation column is the pause menu.

screen quick_menu():

    zorder 100

    if quick_menu and not renpy.get_screen(("sandbox", "menu")):

        hbox:
            id "quick_menu_bar"
            style_prefix "quick"
            style "quick_menu"

            textbutton _("BACK") action Rollback()
            textbutton _("HISTORY") action ShowMenu('history')
            textbutton _("SKIP") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("AUTO") action Preference("auto-forward", "toggle")
            textbutton _("SAVE") action ShowMenu('save')
            if not _in_replay:
                textbutton _("JOURNAL") action ShowMenu('journal')
            textbutton _("MENU") action ShowMenu()

init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_menu is hbox
style quick_button is default
style quick_button_text is button_text

style quick_menu:
    xalign 1.0
    xoffset -48
    yalign 1.0
    yoffset -18
    spacing 8

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.text_properties("quick_button")
    font macron_font(gui.body_medium_font)
    kerning gui.track


################################################################################
## Main and game menus
################################################################################

## Navigation ------------------------------------------------------------------

screen navigation():

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        if main_menu:

            textbutton _("Start") action Start()

        else:

            if not _in_replay:
                textbutton _("Journal") action ShowMenu("journal")
            textbutton _("History") action ShowMenu("history")
            textbutton _("Save") action ShowMenu("save")

        textbutton _("Load") action ShowMenu("load")
        textbutton _("Preferences") action ShowMenu("preferences")

        if _in_replay:
            textbutton _("End Replay") action EndReplay(confirm=True)
        elif not main_menu:
            textbutton _("Main Menu") action MainMenu()

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
            textbutton _("Quit") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")
    left_padding 30
    ypadding 6
    hover_background Frame("gui/rail_only.png", 6, 4, 6, 4)
    selected_background Frame("gui/rail_only.png", 6, 4, 6, 4)

style navigation_button_text:
    properties gui.text_properties("navigation_button")
    font macron_font(gui.display_font)
    size 34
    kerning 1.5


## Main menu -------------------------------------------------------------------

screen main_menu():

    tag menu

    add gui.main_menu_background

    frame:
        style "main_menu_frame"

    ## Watermark: the game's two kanji, read top to bottom.
    vbox:
        xalign 1.0
        xoffset -120
        ypos 90
        spacing -70
        text "呪" style "main_menu_kanji"
        text "縛" style "main_menu_kanji"

    ## Navigation sits under the title block rather than centred on the screen.
    vbox:
        style_prefix "navigation"
        xpos gui.navigation_xpos
        ypos 640
        spacing gui.navigation_spacing

        textbutton _("Start") action Start()
        ## A background-review tool; only shown when run from the SDK.
        if config.developer:
            textbutton _("Explore the campus") action Start("explore_campus")
        textbutton _("Load") action ShowMenu("load")
        textbutton _("Preferences") action ShowMenu("preferences")
        textbutton _("About") action ShowMenu("about")
        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
            textbutton _("Quit") action Quit(confirm=False)

    if gui.show_name:

        vbox:
            style "main_menu_vbox"

            hbox:
                spacing 18
                yalign 0.5
                use seal("呪", 44)
                text _("JUJUTSU KAISEN · A FAN WORK") style "main_menu_kicker" yalign 0.5

            text "[config.name!t]" style "main_menu_title"

            text _("TOKYO JUJUTSU HIGH · ARC ONE") style "main_menu_sub"

            use rule(900)

    text "[config.version]" style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 1920
    yfill True
    background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xpos gui.navigation_xpos
    ypos 150
    xmaximum 1100
    spacing 14

style main_menu_kicker is main_menu_text:
    font macron_font(gui.body_medium_font)
    size 21
    color gui.violet2
    kerning 6

style main_menu_title is main_menu_text:
    font macron_font(gui.display_heavy_font)
    size gui.title_text_size
    color gui.paper
    line_spacing -22

style main_menu_sub is main_menu_text:
    size 21
    color gui.dim
    kerning 3

style main_menu_kanji is text:
    font macron_font(gui.display_heavy_font)
    size 400
    color "#a259ff12"

style main_menu_version:
    ## Bottom-right: the navigation list grew to six entries and reached the
    ## bottom-left corner this used to sit in.
    xalign 1.0
    xoffset -64
    yalign 1.0
    yoffset -40
    size 18
    color gui.mute
    kerning 2


## Game menu -------------------------------------------------------------------

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0):

    style_prefix "game_menu"

    if main_menu:
        add gui.main_menu_background
    else:
        add gui.game_menu_background

    frame:
        style "game_menu_outer_frame"

        hbox:

            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True
                        side_yfill True

                        vbox:
                            spacing spacing
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial yinitial
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        pagekeys True
                        side_yfill True
                        spacing spacing
                        transclude

                else:

                    transclude

    use navigation

    ## Title: seal + display-face heading + a rule, top left.
    vbox:
        style "game_menu_label"
        spacing 12
        hbox:
            spacing 18
            use seal("術", 44)
            text title style "game_menu_label_text" yalign 0.5
        use rule(320)

    textbutton _("Return"):
        style "return_button"
        action Return()


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 60
    top_padding 200
    background "gui/overlay/game_menu.png"

style game_menu_navigation_frame:
    xsize 460
    yfill True

style game_menu_content_frame:
    left_margin 40
    right_margin 60
    top_margin 0
    bottom_margin 30

style game_menu_viewport:
    xsize 1340

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 20

style game_menu_label:
    xpos gui.navigation_xpos
    ypos 78

style game_menu_label_text:
    font macron_font(gui.display_font)
    size 46
    color gui.paper

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -50


## About -----------------------------------------------------------------------

screen about():

    tag menu

    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:
            spacing 14

            text "[config.name!t]" style "jjk_display" size 40
            text _("Version [config.version!t]") style "jjk_small"

            null height 12

            text "[gui.about!t]" size 24 line_spacing 4

            null height 12
            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]") style "jjk_small"


## Save / load -----------------------------------------------------------------

screen save():
    tag menu
    use file_slots(_("Save"))

screen load():
    tag menu
    use file_slots(_("Load"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("Page {}"), auto=_("Automatic saves"), quick=_("Quick saves"))

    use game_menu(title):

        fixed:

            ## Page name / rename.
            order_reverse True

            button:
                style "page_label"
                key_events True
                xalign 0.5
                action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileAction(slot)

                        has vbox
                        spacing 8

                        add FileScreenshot(slot) xalign 0.5

                        hbox:
                            spacing 14
                            text FileSlotName(slot, gui.file_slot_cols * gui.file_slot_rows):
                                style "slot_name_text"
                            text FileTime(slot, format=_("{#file_time}%d %b · %H:%M"), empty=_("empty")):
                                style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_save_text"

                        key "save_delete" action FileDelete(slot)

            ## Pager.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                textbutton _("<") action FilePagePrevious()
                key "save_page_prev" action FilePagePrevious()

                if config.has_autosave:
                    textbutton _("{#auto_page}A") action FilePage("auto")

                if config.has_quicksave:
                    textbutton _("{#quick_page}Q") action FilePage("quick")

                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                textbutton _(">") action FilePageNext()
                key "save_page_next" action FilePageNext()

            if config.has_sync:
                if CurrentScreenName() == "save":
                    textbutton _("Upload Sync"):
                        action UploadSync()
                        xalign 0.5
                        yalign 1.0
                        yoffset -60
                else:
                    textbutton _("Download Sync"):
                        action DownloadSync()
                        xalign 0.5
                        yalign 1.0
                        yoffset -60


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text

style page_label:
    xpadding 60
    ypadding 8

style page_label_text:
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color
    font macron_font(gui.body_medium_font)
    size 20
    color gui.dim
    kerning gui.track

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")
    font macron_font(gui.body_medium_font)
    size 22

style slot_button:
    properties gui.button_properties("slot_button")
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    selected_idle_background Frame("gui/panel_active.png", 4, 4)
    selected_hover_background Frame("gui/panel_active.png", 4, 4)

style slot_button_text:
    properties gui.text_properties("slot_button")

style slot_name_text is slot_button_text:
    font macron_font(gui.body_medium_font)
    color gui.paper
    size 19
    kerning 1

style slot_time_text is slot_button_text:
    color gui.dim
    size 17

style slot_save_text is slot_button_text:
    color gui.dim
    size 17


## Preferences -----------------------------------------------------------------

screen preferences():

    tag menu

    use game_menu(_("Preferences"), scroll="viewport"):

        vbox:
            spacing 36

            hbox:
                box_wrap True
                spacing 48

                if renpy.variant("pc") or renpy.variant("web"):

                    vbox:
                        style_prefix "radio"
                        label _("DISPLAY")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

                vbox:
                    style_prefix "check"
                    label _("SKIP")
                    textbutton _("Unseen text") action Preference("skip", "toggle")
                    textbutton _("After choices") action Preference("after choices", "toggle")
                    textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                vbox:
                    style_prefix "radio"
                    label _("ROLLBACK SIDE")
                    textbutton _("Disable") action Preference("rollback side", "disable")
                    textbutton _("Left") action Preference("rollback side", "left")
                    textbutton _("Right") action Preference("rollback side", "right")

                ## WP8 (4.11): my own side portrait beside my lines.
                vbox:
                    style_prefix "radio"
                    label mc_portrait_label()
                    textbutton _("Show") action SetField(persistent, "mc_face", True)
                    textbutton _("Hide") action SetField(persistent, "mc_face", False)

                ## Phase 2 (D17): the looping motion (the Special Grade sheen,
                ## breathing, the glow on things in a room). view_motion() reads it.
                vbox:
                    style_prefix "radio"
                    label _("MOTION")
                    textbutton _("On") action SetField(persistent, "motion", True)
                    textbutton _("Off") action SetField(persistent, "motion", False)

            use rule()

            hbox:
                style_prefix "slider"
                box_wrap True
                spacing 48

                vbox:

                    label _("TEXT SPEED")
                    bar value Preference("text speed")

                    label _("AUTO-FORWARD TIME")
                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("MUSIC VOLUME")
                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:
                        label _("SOUND VOLUME")
                        hbox:
                            bar value Preference("sound volume")
                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)

                    if config.has_voice:
                        label _("VOICE VOLUME")
                        hbox:
                            bar value Preference("voice volume")
                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height 8
                        textbutton _("Mute all"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 6

style pref_label_text:
    font macron_font(gui.body_medium_font)
    size 17
    color gui.dim
    kerning gui.track
    yalign 1.0

style pref_vbox:
    xsize 380

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")
    size 24

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")
    size 24

style slider_slider:
    xsize 420

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 16

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 520


## History ---------------------------------------------------------------------

screen history():

    tag menu

    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

        style_prefix "history"

        for h in _history_list:

            window:

                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"
                        substitute False

                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                text what:
                    substitute False

        if not _history_list:
            label _("The dialogue history is empty.")


define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }

style history_window is empty
style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text
style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    font macron_font(gui.display_font)
    size 24
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")
    size 24
    color gui.paper

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## Help ------------------------------------------------------------------------

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("Help"), scroll="viewport"):

        style_prefix "help"

        vbox:
            spacing 24

            hbox:
                spacing 10
                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
                textbutton _("Mouse") action SetScreenVariable("device", "mouse")
                if GamepadExists():
                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")

            if device == "keyboard":
                use keyboard_help
            elif device == "mouse":
                use mouse_help
            elif device == "gamepad":
                use gamepad_help


screen keyboard_help():

    hbox:
        label _("Enter")
        text _("Advances dialogue and activates the interface.")
    hbox:
        label _("Space")
        text _("Advances dialogue without selecting choices.")
    hbox:
        label _("Arrow Keys")
        text _("Navigate the interface.")
    hbox:
        label _("Escape")
        text _("Accesses the game menu.")
    hbox:
        label _("Ctrl")
        text _("Skips dialogue while held down.")
    hbox:
        label _("Tab")
        text _("Toggles dialogue skipping.")
    hbox:
        label _("Page Up")
        text _("Rolls back to earlier dialogue.")
    hbox:
        label _("Page Down")
        text _("Rolls forward to later dialogue.")
    hbox:
        label "H"
        text _("Hides the user interface.")
    hbox:
        label "S"
        text _("Takes a screenshot.")
    hbox:
        label "V"
        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")
    hbox:
        label "Shift+A"
        text _("Opens the accessibility menu.")


screen mouse_help():

    hbox:
        label _("Left Click")
        text _("Advances dialogue and activates the interface.")
    hbox:
        label _("Middle Click")
        text _("Hides the user interface.")
    hbox:
        label _("Right Click")
        text _("Accesses the game menu.")
    hbox:
        label _("Mouse Wheel Up")
        text _("Rolls back to earlier dialogue.")
    hbox:
        label _("Mouse Wheel Down")
        text _("Rolls forward to later dialogue.")


screen gamepad_help():

    hbox:
        label _("Right Trigger\nA/Bottom Button")
        text _("Advances dialogue and activates the interface.")
    hbox:
        label _("Left Trigger\nLeft Shoulder")
        text _("Rolls back to earlier dialogue.")
    hbox:
        label _("Right Shoulder")
        text _("Rolls forward to later dialogue.")
    hbox:
        label _("D-Pad, Sticks")
        text _("Navigate the interface.")
    hbox:
        label _("Start, Guide, B/Right Button")
        text _("Accesses the game menu.")
    hbox:
        label _("Y/Top Button")
        text _("Hides the user interface.")

    textbutton _("Calibrate") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size 22
    xalign 1.0
    text_align 1.0
    font macron_font(gui.body_medium_font)
    color gui.dim

style help_text:
    size 22


################################################################################
## Additional screens
################################################################################

## Confirm ---------------------------------------------------------------------

screen confirm(message, yes_action, no_action):

    modal True
    zorder 200

    style_prefix "confirm"

    add "gui/overlay/confirm.png"

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 34

            hbox:
                xalign 0.5
                spacing 18
                use seal("問", 44)
                label _(message) style "confirm_prompt" yalign 0.5

            hbox:
                xalign 0.5
                spacing 40

                textbutton _("Yes") action yes_action
                textbutton _("No") action no_action

    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    background Frame("gui/panel_solid.png", 4, 4)
    padding gui.confirm_frame_borders.padding
    xalign .5
    yalign .5

style confirm_prompt_text:
    font macron_font(gui.display_font)
    size 30
    text_align 0.5
    layout "subtitle"
    color gui.paper

style confirm_button:
    properties gui.button_properties("confirm_button")
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/panel_active.png", 4, 4)
    xpadding 44
    ypadding 10

style confirm_button_text:
    properties gui.text_properties("confirm_button")
    font macron_font(gui.body_medium_font)
    size 22
    kerning 2


## Skip indicator --------------------------------------------------------------

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    ## Phase 2 (D13): scenes only. Hidden while a `sandbox` or `menu` screen
    ## is up (the map, the journal, the place view), as the quick menu is.
    if not renpy.get_screen(("sandbox", "menu")):

        frame:

            hbox:
                spacing 10

                text _("SKIPPING") style "skip_text"

                text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
                text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
                text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


transform delayed_blink(delay, cycle):
    alpha .5
    pause delay
    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    xpos 48
    ypos gui.skip_ypos
    background Frame("gui/rail_violet.png", 10, 4)
    padding gui.skip_frame_borders.padding

style skip_text:
    font macron_font(gui.body_medium_font)
    size 18
    color gui.dim
    kerning gui.track

style skip_triangle:
    color gui.violet


## Notify ----------------------------------------------------------------------

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text "[message!tq]"

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        xoffset 24
        linear .2 alpha 1 xoffset 0
    on hide:
        linear .4 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    xalign 1.0
    xoffset -48
    ypos gui.notify_ypos
    background Frame("gui/rail_violet.png", 10, 4)
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")
    color gui.paper


## NVL -------------------------------------------------------------------------

screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        use nvl_dialogue(dialogue)

        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    ## The same portrait rules as the say screen.
    if not hide_side_images:
        if persistent.mc_face or renpy.get_say_image_tag() != "mc":
            add SideImage() xpos 6 yalign 1.0 zoom 0.8


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True
    background Solid("#07060cd8")
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    text_align gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    text_align gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    text_align gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## Bubble ----------------------------------------------------------------------

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xpos 10
    xanchor 0.0
    yalign 0.5
    color gui.accent_color

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },
    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },
    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },
    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },
    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}


################################################################################
## Mobile variants
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu and not renpy.get_screen(("sandbox", "menu")):

        hbox:
            id "quick_menu_bar"
            style "quick_menu"
            style_prefix "quick"

            textbutton _("BACK") action Rollback()
            textbutton _("SKIP") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("AUTO") action Preference("auto-forward", "toggle")
            if not _in_replay:
                textbutton _("JOURNAL") action ShowMenu('journal')
            textbutton _("MENU") action ShowMenu()

style game_menu_navigation_frame:
    variant "small"
    xsize 400

style game_menu_viewport:
    variant "small"
    xsize 1305

style pref_vbox:
    variant "small"
    xsize 600
