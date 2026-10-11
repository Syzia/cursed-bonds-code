################################################################################
## Jujutsu Kaisen: Cursed Bonds
## Definitions — characters, images, transforms, transitions.
################################################################################

## Characters ##################################################################
##
## image="<tag>" ties a speaker to their sprite tag: say-with-attributes
## (`yuji happy "..."`) changes their face, and when they are not on screen
## their side portrait shows beside the line.

define mc      = Character("[mc_name]", color="#c9a6ff", image="mc")
define mcthink = Character(None, what_prefix="{i}", what_suffix="{/i}", what_color="#c8c2d8")

## The player names him when Gojo asks in the alley; these cover a fresh start.
default mc_name    = "Kaito"
default mc_surname = "Amagiri"

define yuji    = Character("Yuji",    color="#ff8fa3", image="yuji")
define megumi  = Character("Megumi",  color="#8fb0ff", image="megumi")
define nobara  = Character("Nobara",  color="#ffb066", image="nobara")
define maki    = Character("Maki",    color="#77e0a0", image="maki")
define panda   = Character("Panda",   color="#e6e6f0", image="panda")
define toge    = Character("Toge",    color="#bfe3ea", image="toge")
define gojo    = Character("Gojo",    color="#8ed6ff", image="gojo")
define yaga    = Character("Principal Yaga", color="#b0b8c8", image="yaga")
define ijichi  = Character("Ijichi",  color="#9aa0b0", image="ijichi")
define shoko   = Character("Shoko",   color="#e0c8b0", image="shoko")
define utahime = Character("Utahime", color="#c9a0d8", image="utahime")

## Pre-campus cast
define sana    = Character("Sana",        color="#ffd27a", image="sana")
define mother  = Character("Mom",         color="#d8c8b8")
define oda     = Character("Oda-sensei",  color="#a9a2b8")
define kurose  = Character("Kurose",      color="#8f8aa0")
define nade    = Character("Nade",        color="#9a8f7a")

define curse2  = Character("???",     color="#ff5f8a")
define voice_  = Character("Voice",   color="#8f8aa0")

## A side portrait only for a speaker who is not on screen, and a quick
## dissolve when a line changes someone's face.
define config.side_image_only_not_showing = True
define config.say_attribute_transition = Dissolve(0.12)


## Backgrounds #################################################################

image bg black      = "images/bg/black.png"
image bg ruin       = "images/bg/ruin_hall.png"
image bg gate       = "images/bg/gate.png"
image bg courtyard  = "images/bg/courtyard.png"
image bg classroom  = "images/bg/classroom.png"
image bg training   = "images/bg/training.png"
image bg forest     = "images/bg/forest.png"
image bg city       = "images/bg/city_night.png"
image bg rooftop    = "images/bg/rooftop.png"
image bg veil       = "images/bg/veil.png"
image bg infirmary  = "images/bg/infirmary.png"

## Sandbox locations
image bg your_room   = "images/bg/your_room.png"
image bg your_room night = "images/bg/your_room_night.png"
image bg infirmary night = "images/bg/infirmary_night.png"
image bg rooftop evening = "images/bg/rooftop_evening.png"
image bg rooftop night   = "images/bg/rooftop_night.png"
image bg riverside evening = "images/bg/riverside_evening.png"
image bg dorm_common evening = "images/bg/dorm_common_evening.png"
image bg dorm_common night   = "images/bg/dorm_common_night.png"
image bg girls_dorm night    = "images/bg/girls_dorm_night.png"
image bg dorm_common = "images/bg/dorm_common.png"
image bg girls_dorm  = "images/bg/girls_dorm.png"
image bg cafeteria   = "images/bg/cafeteria.png"
image bg dojo        = "images/bg/dojo.png"
image bg riverside   = "images/bg/riverside.png"
image bg ridge       = "images/bg/ridge.png"
image bg storehouse  = "images/bg/storehouse.png"
image bg office      = "images/bg/office.png"
image bg map_campus  = "images/bg/map_campus.png"

## Pre-campus (prologue) locations
image bg home_living   = "images/bg/home_living.png"
image bg town_street   = "images/bg/town_street.png"
image bg car           = "images/bg/car.png"
image bg konbini         = "images/bg/konbini.png"
image bg diner           = "images/bg/diner.png"
image bg street_morning  = "images/bg/street_morning.png"
image bg home_bedroom_night = "images/bg/home_bedroom_night.png"


## Sprites #####################################################################
##
## The main cast's sprites live in jjk_sprites.rpy.

## Pre-campus cast: stand-in art until each person's own sprite set lands.
##
## The second UI overhaul (U0c2; docs/UI2_DESIGN.md 8.2): five `image` lines
## became this one guarded block. Each of the five names is defined as
## today's tinted figure only when nothing else has defined it, so the day
## tools/gen_sprite_defs.py writes `image mother = lit_sprite(...)` into
## jjk_sprites.rpy that sprite takes over, in old saves too (a sprite on
## screen is saved by its image name), and no scene line changes. The guard
## is on the image, not on the file: while mother_neutral.png has landed and
## the generator has not been run, nothing else defines `mother`, and the
## stand-in still does.
##
## It runs at init 501: an `image` statement runs at init 500 (the generated
## ones too), so this is the first moment every other definition is in.
init 501 python:

    ## key -> (the campus sprite it borrows, its tint).
    STANDIN_PEOPLE = (
        ("mother", "images/char/shoko.png",   "#f0e6db"),
        ("father", "images/char/ijichi.png",  "#ebf0ff"),
        ("oda",    "images/char/utahime.png", "#e0e0eb"),
        ("kurose", "images/char/ijichi.png",  "#9e9eb3"),
        ("nade",   "images/char/yaga.png",    "#b0a894"),
    )

    def standin_person(path, tint):
        """U0c2. A stand-in person: a campus sprite under a tint, lit by
        the scene. What `image mother = ...` built before the overhaul."""
        return lit(Transform(path, matrixcolor=TintMatrix(tint)))

    def standin_people_define():
        """U0c2. Defines each of the five stand-in names that nothing else
        has defined (renpy.has_image, exact). Returns the keys it defined.
        Called once, below."""
        out = []
        for key, path, tint in STANDIN_PEOPLE:
            if not renpy.has_image(key, exact=True):
                renpy.image(key, standin_person(path, tint))
                out.append(key)
        return out

    STANDIN_DEFINED = tuple(standin_people_define())

image curse small = lit("images/char/curse_small.png")
image curse big = lit("images/char/curse_big.png")


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
        "yaga": yaga, "utahime": utahime, "ijichi": ijichi, "sana": sana,
    }
