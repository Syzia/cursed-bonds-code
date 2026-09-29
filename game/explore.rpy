################################################################################
## Explore the campus: a look-around mode, on the main menu when run from the SDK (config.developer).
##
## Drops straight into free roam at the courtyard for judging locations and
## backgrounds. No story beats fire, every door is open, and a Time button
## steps through the day without spending it on anything. The people on
## campus still follow their schedules, so each time of day shows who would
## be where.
################################################################################

default explore_mode = False

init python:

    def explore_next_period():
        i = PERIODS.index(store.period)
        store.period = PERIODS[(i + 1) % len(PERIODS)]


label explore_campus:

    $ explore_mode = True
    $ day = 1
    $ period = "Morning"
    $ here = "courtyard"
    $ roll_gojo()
    $ flag("settled_in")

    scene expression graded_bg() with fade_slow
    call sandbox
    return


label sb_do_explore_time:

    $ explore_next_period()
    scene expression graded_bg()
    with Dissolve(0.4)
    return
