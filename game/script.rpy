################################################################################
## Jujutsu Kaisen: Cursed Bonds
##
## Prologue -> open campus. Entry point.
################################################################################

label splashscreen:

    scene bg black
    with None
    $ renpy.pause(0.4, hard=True)

    show text "{size=28}{color=#9d95ae}An unofficial, non-commercial fan work.\nJujutsu Kaisen is created by Gege Akutami.{/color}{/size}" with dissolve
    $ renpy.pause(2.4)
    hide text with dissolve
    $ renpy.pause(0.3)

    show text "{size=28}{color=#9d95ae}All art in this build is placeholder art,\ngenerated procedurally. Replace it freely.{/color}{/size}" with dissolve
    $ renpy.pause(2.2)
    hide text with dissolve
    $ renpy.pause(0.4)

    return


label start:

    $ mc_name = "Kaito"
    $ mc_surname = "Amagiri"

    ## --- Prologue: how you got here -----------------------------------------
    call chapter_one

    ## The four days between the corridor and the car.
    call chapter_one_b

    call chapter_one_c

    call chapter_one_d

    call chapter_two

    ## --- The campus opens up ------------------------------------------------
    call arc_one_open

    call sandbox

    return


label arc_one_open:

    scene bg black with fade_slow

    show screen chapter_card("ARC ONE", "Tokyo Jujutsu High", "The campus is yours. So is the clock.")
    with fade_slow
    $ renpy.pause(3.0)
    hide screen chapter_card
    with fade_slow

    $ day = 1
    $ period = "Morning"
    $ here = "dorm"
    $ roll_gojo()
    $ flag("settled_in")

    scene bg your_room with fade_slow
    show mc at pos_c with dissolve

    "A room with a bed, a desk, and a window that faces a mountain that is also, somehow, Tokyo."

    mcthink "Right."

    mcthink "Nobody's told me what to do today. Nobody's going to."

    "Gojo's version of a timetable, delivered yesterday in full, was: {i}go and have some boring afternoons.{/i}"

    "Yaga's version was longer and contained the phrase 'I will be checking'."

    hide mc with dissolve

    "Three weeks until the exchange event with Kyoto. Until then the campus is open, the clock runs whether you use it or not, and everyone here has somewhere they'll be."

    mcthink "So. Find them."

    return
