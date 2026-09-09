################################################################################
## Jujutsu Kaisen: Cursed Bonds
## Definitions — characters, images, transforms, transitions.
################################################################################

## Characters ##################################################################

define mc      = Character("[mc_name]", color="#c9a6ff")
define mcthink = Character(None, what_prefix="{i}", what_suffix="{/i}", what_color="#c8c2d8")

define yuji    = Character("Yuji",    color="#ff8fa3")
define megumi  = Character("Megumi",  color="#8fb0ff")
define nobara  = Character("Nobara",  color="#ffb066")
define maki    = Character("Maki",    color="#77e0a0")
define panda   = Character("Panda",   color="#e6e6f0")
define toge    = Character("Toge",    color="#bfe3ea")
define gojo    = Character("Gojo",    color="#8ed6ff")
define yaga    = Character("Principal Yaga", color="#b0b8c8")
define ijichi  = Character("Ijichi",  color="#9aa0b0")
define shoko   = Character("Shoko",   color="#e0c8b0")
define utahime = Character("Utahime", color="#c9a0d8")

define curse   = Character("???",     color="#6cff9e")
define curse2  = Character("???",     color="#ff5f8a")
define teacher = Character("Teacher", color="#a9a2b8")
define voice_  = Character("Voice",   color="#8f8aa0")


## Backgrounds #################################################################

image bg black      = "images/bg/black.png"
image bg ruin       = "images/bg/ruin_hall.png"
image bg gate       = "images/bg/gate.png"
image bg courtyard  = "images/bg/courtyard.png"
image bg classroom  = "images/bg/classroom.png"
image bg training   = "images/bg/training.png"
image bg dorm       = "images/bg/dorm.png"
image bg forest     = "images/bg/forest.png"
image bg city       = "images/bg/city_night.png"
image bg rooftop    = "images/bg/rooftop.png"
image bg veil       = "images/bg/veil.png"
image bg infirmary  = "images/bg/infirmary.png"

## Sandbox locations
image bg your_room   = "images/bg/your_room.png"
image bg your_room night = "images/bg/your_room_night.png"
image bg dorm_common = "images/bg/dorm_common.png"
image bg girls_dorm  = "images/bg/girls_dorm.png"
image bg cafeteria   = "images/bg/cafeteria.png"
image bg dojo        = "images/bg/dojo.png"
image bg riverside   = "images/bg/riverside.png"
image bg ridge       = "images/bg/ridge.png"
image bg storehouse  = "images/bg/storehouse.png"
image bg office      = "images/bg/office.png"
image bg map_campus  = "images/bg/map_campus.png"


## Sprites #####################################################################

image mc          = "images/char/mc.png"
image yuji        = "images/char/yuji.png"
image megumi      = "images/char/megumi.png"
image nobara      = "images/char/nobara.png"
image maki        = "images/char/maki.png"
image panda       = "images/char/panda.png"
image toge        = "images/char/toge.png"
image gojo        = "images/char/gojo.png"
image yaga        = "images/char/yaga.png"
image ijichi      = "images/char/ijichi.png"
image shoko       = "images/char/shoko.png"
image utahime     = "images/char/utahime.png"
image curse small = "images/char/curse_small.png"
image curse big   = "images/char/curse_big.png"


## Stage positions #############################################################

transform pos_fl:
    xalign 0.01 yalign 1.0 zoom 0.60

transform pos_l:
    xalign 0.17 yalign 1.0 zoom 0.62

transform pos_cl:
    xalign 0.35 yalign 1.0 zoom 0.62

transform pos_c:
    xalign 0.50 yalign 1.0 zoom 0.64

transform pos_cr:
    xalign 0.65 yalign 1.0 zoom 0.62

transform pos_r:
    xalign 0.83 yalign 1.0 zoom 0.62

transform pos_fr:
    xalign 0.99 yalign 1.0 zoom 0.60

## Looming: used for curses, so they read as bigger than a person.
transform pos_loom:
    xalign 0.5 yalign 1.0 zoom 0.90

transform pos_loom_r:
    xalign 0.72 yalign 1.0 zoom 0.80


## Small motion ################################################################

transform shake:
    linear 0.04 xoffset 22
    linear 0.04 xoffset -22
    linear 0.04 xoffset 14
    linear 0.04 xoffset -14
    linear 0.04 xoffset 6
    linear 0.04 xoffset 0

transform breathe:
    block:
        linear 2.2 yoffset -6
        linear 2.2 yoffset 0
        repeat

transform pulse_in:
    alpha 0.0 zoom 0.86
    parallel:
        linear 0.35 alpha 1.0
    parallel:
        easeout 0.45 zoom 0.64


## Transitions #################################################################

define fade_slow  = Fade(0.8, 0.4, 0.8)
define fade_hard  = Fade(0.25, 0.1, 0.25, color="#000")
define fade_curse = Fade(0.5, 0.25, 0.7, color="#0e2a19")
define flash_white = Fade(0.08, 0.0, 0.45, color="#ffffff")
define flash_purple = Fade(0.12, 0.0, 0.6, color="#7b2fd6")
define slowdissolve = Dissolve(1.2)


## Key -> Character, so systems code can make anyone speak ######################

init 1 python:
    CHARS = {
        "yuji": yuji, "megumi": megumi, "nobara": nobara, "maki": maki,
        "panda": panda, "toge": toge, "shoko": shoko, "gojo": gojo,
        "yaga": yaga, "utahime": utahime,
    }
