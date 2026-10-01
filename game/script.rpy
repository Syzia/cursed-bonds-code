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

    show text "{size=28}{color=#9d95ae}The art in this fan game was made with ComfyUI.\nSome placeholder art remains.{/color}{/size}" with dissolve
    $ renpy.pause(2.2)
    hide text with dissolve
    $ renpy.pause(0.4)

    return


label start:

    $ mc_name = "Kaito"
    $ mc_surname = "Amagiri"

    ## --- Prologue: the alley, the offer, the school -------------------------
    call chapter_one

    call chapter_one_b

    call chapter_two

    ## --- The campus opens up ------------------------------------------------
    call arc_one_open

    call sandbox

    return


label arc_one_open:

    call prologue_catch_up("arc_one_open")

    $ story_point = "arc_one_open"

    scene bg black with fade_slow

    show screen chapter_card("ARC ONE", "Tokyo Jujutsu High", "The campus is yours. So is the clock.")
    with fade_slow
    $ renpy.pause(3.0)
    hide screen chapter_card
    with fade_slow

    $ day = 1
    $ period = "Morning"
    $ here = "courtyard"
    $ roll_gojo()
    $ flag("settled_in")
    $ arc_start_day = day
    $ ensure_state()

    scene bg your_room with fade_slow

    "For about two seconds after I wake up, it is Thursday, and I am late, and Sana is going to have something to say about it. Then it isn't."

    "My room: a bed, a desk, and a window that faces a mountain that is also, somehow, Tokyo."

    "The ridge is in the corner of the window. I don't look at it for long."

    mcthink "Right."

    mcthink "No bell. No timetable on the door."

    "Gojo's version of a timetable, delivered yesterday in full, was: {i}you four do something.{/i}"

    "Yaga's version was longer and contained the phrase 'I will be checking'."

    "Nobody has given me a deadline. The campus is open, the clock runs whether I use it or not, and the three of them have somewhere they'll be."

    mcthink "So. Find them."

    "I go out into the courtyard, because it is the middle of everything and somebody is always crossing it."

    return


################################################################################
## Keeping old saves on the rails (WP9)
################################################################################

## Before phase 1 the prologue was three long chapters. A save made inside one
## of them has only label start's frame on its call stack, so when the step it
## now lands in returns, play goes straight back to label start and the rest
## of that chapter would be skipped. Each step marks the next one in
## story_point as it ends; the chapter heads (chapter_one_b, chapter_two,
## arc_one_open) call this first, and it plays whatever was skipped. In a
## new game story_point already names the chapter's first step, so it does
## nothing. With no story_point (an old save still mid-step) it does nothing
## either: the step marks its successor when it ends.
##
## The work list is dynamic (local to each call): chapter_one_b is itself a
## step and calls this at its top, and a shared list would lose every step
## queued after it.
label prologue_catch_up(upto):
    $ renpy.dynamic("_catch_up", "_catch_step", "_steps")
    python:
        _steps = [s for s, c in PROLOGUE_STEPS]
        _catch_up = []
        if story_point in _steps and upto in _steps:
            _catch_up = _steps[_steps.index(story_point):_steps.index(upto)]
    while _catch_up:
        $ _catch_step = _catch_up.pop(0)
        call expression _catch_step
    return
