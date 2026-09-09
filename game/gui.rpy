################################################################################
## Cursed Bonds — GUI tokens.
##
## Every colour, font and size the interface uses lives here. screens.rpy,
## jjk_screens.rpy and sb_screens.rpy read from this file and never hard-code
## a hex value of their own. Change a token here and re-run tools/gen_gui.py so
## the generated PNGs (panels, pips, textbox gradient) follow.
################################################################################

init offset = -2

init python:
    gui.init(1920, 1080)

define config.check_conflicting_properties = True


## Palette #####################################################################
##
## Semantic colour is separate from the accent. Violet is the player: cursed
## energy, selection, focus. Gold means "something new". Red means locked,
## danger, curses. Green is stamina. Nothing else gets a colour.

define gui.ink          = '#07060c'   # ground
define gui.panel        = '#14111d'   # raised surface
define gui.panel2       = '#1b1727'   # hovered surface
define gui.line         = '#2a2438'   # hairline
define gui.line2        = '#403854'   # hovered hairline

define gui.paper        = '#ece7f5'   # primary text
define gui.dim          = '#9d95ae'   # secondary text
define gui.mute         = '#6a6478'   # disabled / tertiary

define gui.violet       = '#a259ff'   # accent — the player's energy
define gui.violet2      = '#c79bff'   # accent, lifted (hover)
define gui.violet_deep  = '#2d1c52'   # accent as a fill
define gui.seal         = '#e8334f'   # locked / danger / curse
define gui.gold         = '#ffd166'   # new / attention
define gui.stamina      = '#77e0a0'
define gui.romance      = '#ff8fb0'

## Stock gui.* names, mapped onto the palette so every default style follows.
define gui.accent_color         = gui.violet
define gui.idle_color           = gui.dim
define gui.idle_small_color     = gui.dim
define gui.hover_color          = gui.paper
define gui.selected_color       = gui.paper
define gui.insensitive_color    = '#6a647880'
define gui.muted_color          = gui.line
define gui.hover_muted_color    = gui.line2
define gui.text_color           = gui.paper
define gui.interface_text_color = gui.paper


## Type ########################################################################
##
## Shippori Mincho carries titles, names and section heads — a mincho has the
## brush weight the subject wants. Zen Kaku Gothic New does everything else.
## Both are OFL and cover kanji, so UI strings may use them freely.

define gui.display_font       = "fonts/ShipporiMincho-Bold.ttf"
define gui.display_heavy_font = "fonts/ShipporiMincho-ExtraBold.ttf"
define gui.body_font          = "fonts/ZenKakuGothicNew-Regular.ttf"
define gui.body_medium_font   = "fonts/ZenKakuGothicNew-Medium.ttf"
define gui.body_bold_font     = "fonts/ZenKakuGothicNew-Bold.ttf"

define gui.text_font           = gui.body_font
define gui.name_text_font      = gui.display_font
define gui.interface_text_font = gui.body_font

define gui.text_size           = 31
define gui.name_text_size      = 42
define gui.interface_text_size = 26
define gui.label_text_size     = 30
define gui.notify_text_size    = 21
define gui.title_text_size     = 132

## Tracking for small uppercase labels (pixels added between glyphs).
define gui.track = 3.0


## Main and game menus #########################################################

define gui.main_menu_background = "images/bg/gate.png"
define gui.game_menu_background = "images/bg/veil.png"


## Dialogue ####################################################################

define gui.textbox_height = 340
define gui.textbox_yalign = 1.0

define gui.name_xpos   = 300
define gui.name_ypos   = 92
define gui.name_xalign = 0.0
define gui.namebox_width   = None
define gui.namebox_height  = None
define gui.namebox_borders = Borders(0, 0, 0, 0)
define gui.namebox_tile    = False

define gui.dialogue_xpos  = 300
define gui.dialogue_ypos  = 168
define gui.dialogue_width = 1320
define gui.dialogue_text_xalign = 0.0


## Buttons #####################################################################

define gui.button_width   = None
define gui.button_height  = None
define gui.button_borders = Borders(6, 6, 6, 6)
define gui.button_tile    = False
define gui.button_text_font = gui.interface_text_font
define gui.button_text_size = gui.interface_text_size
define gui.button_text_idle_color        = gui.idle_color
define gui.button_text_hover_color       = gui.hover_color
define gui.button_text_selected_color    = gui.selected_color
define gui.button_text_insensitive_color = gui.insensitive_color
define gui.button_text_xalign = 0.0

define gui.radio_button_borders = Borders(40, 6, 12, 6)
define gui.check_button_borders = Borders(40, 6, 12, 6)
define gui.confirm_button_text_xalign = 0.5
define gui.page_button_borders = Borders(14, 6, 14, 6)

define gui.quick_button_borders = Borders(12, 6, 12, 4)
define gui.quick_button_text_size = 18
define gui.quick_button_text_idle_color = gui.mute
define gui.quick_button_text_selected_color = gui.violet2


## Choice buttons ##############################################################

define gui.choice_button_width   = 1000
define gui.choice_button_height  = None
define gui.choice_button_tile    = False
define gui.choice_button_borders = Borders(40, 20, 34, 20)
define gui.choice_button_text_font = gui.text_font
define gui.choice_button_text_size = 29
define gui.choice_button_text_xalign = 0.0
define gui.choice_button_text_idle_color  = gui.dim
define gui.choice_button_text_hover_color = gui.paper
define gui.choice_button_text_insensitive_color = gui.insensitive_color


## File slots ##################################################################

define gui.slot_button_width   = 430
define gui.slot_button_height  = 318
define gui.slot_button_borders = Borders(14, 14, 14, 14)
define gui.slot_button_text_size = 19
define gui.slot_button_text_xalign = 0.0
define gui.slot_button_text_idle_color = gui.dim
define gui.slot_button_text_selected_idle_color  = gui.paper
define gui.slot_button_text_selected_hover_color = gui.paper

define config.thumbnail_width  = 402
define config.thumbnail_height = 226

define gui.file_slot_cols = 3
define gui.file_slot_rows = 2


## Positioning and spacing #####################################################

define gui.navigation_xpos = 150
define gui.skip_ypos   = 108
define gui.notify_ypos = 108

define gui.choice_spacing      = 14
define gui.navigation_spacing  = 10
define gui.pref_spacing        = 18
define gui.pref_button_spacing = 2
define gui.page_spacing        = 0
define gui.slot_spacing        = 18

define gui.main_menu_text_xalign = 0.0


## Frames ######################################################################

define gui.frame_borders         = Borders(4, 4, 4, 4)
define gui.confirm_frame_borders = Borders(60, 50, 60, 50)
define gui.skip_frame_borders    = Borders(24, 8, 60, 8)
define gui.notify_frame_borders  = Borders(24, 10, 40, 10)
define gui.frame_tile = False


## Bars, scrollbars, sliders ###################################################

define gui.bar_size       = 6
define gui.scrollbar_size = 6
define gui.slider_size    = 26

define gui.bar_tile = False
define gui.scrollbar_tile = False
define gui.slider_tile = False

define gui.bar_borders       = Borders(0, 0, 0, 0)
define gui.scrollbar_borders = Borders(0, 0, 0, 0)
define gui.slider_borders    = Borders(0, 0, 0, 0)
define gui.vbar_borders       = Borders(0, 0, 0, 0)
define gui.vscrollbar_borders = Borders(0, 0, 0, 0)
define gui.vslider_borders    = Borders(0, 0, 0, 0)

define gui.unscrollable = "hide"


## History #####################################################################

define config.history_length = 250
define gui.history_height  = None
define gui.history_spacing = 18

define gui.history_name_xpos   = 0
define gui.history_name_ypos   = 0
define gui.history_name_width  = 230
define gui.history_name_xalign = 0.0

define gui.history_text_xpos   = 260
define gui.history_text_ypos   = 4
define gui.history_text_width  = 1100
define gui.history_text_xalign = 0.0


## NVL #########################################################################

define gui.nvl_borders = Borders(0, 15, 0, 30)
define gui.nvl_list_length = 6
define gui.nvl_height  = 173
define gui.nvl_spacing = 15

define gui.nvl_name_xpos   = 645
define gui.nvl_name_ypos   = 0
define gui.nvl_name_width  = 225
define gui.nvl_name_xalign = 1.0

define gui.nvl_text_xpos   = 675
define gui.nvl_text_ypos   = 12
define gui.nvl_text_width  = 885
define gui.nvl_text_xalign = 0.0

define gui.nvl_thought_xpos   = 360
define gui.nvl_thought_ypos   = 0
define gui.nvl_thought_width  = 1170
define gui.nvl_thought_xalign = 0.0

define gui.nvl_button_xpos   = 675
define gui.nvl_button_xalign = 0.0


## Localisation ################################################################

define gui.language = "unicode"


################################################################################
## Mobile variants — kept minimal; the game targets desktop.
################################################################################

init python:

    @gui.variant
    def touch():
        gui.quick_button_borders = Borders(40, 16, 40, 8)

    @gui.variant
    def small():
        gui.text_size = 42
        gui.name_text_size = 50
        gui.notify_text_size = 34
        gui.interface_text_size = 38
        gui.button_text_size = 38
        gui.label_text_size = 44
        gui.textbox_height = 400
        gui.name_xpos = 120
        gui.name_ypos = 100
        gui.dialogue_xpos = 120
        gui.dialogue_ypos = 180
        gui.dialogue_width = 1680
        gui.choice_button_width = 1680
        gui.choice_button_text_size = 40
        gui.navigation_spacing = 24
        gui.pref_button_spacing = 12
        gui.quick_button_text_size = 28
        gui.file_slot_cols = 2
        gui.file_slot_rows = 2
