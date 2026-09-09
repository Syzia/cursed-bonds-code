################################################################################
## Cursed Bonds — the sandbox loop.
##
## Everything the player does on campus routes through here.
################################################################################

label sandbox:

    $ quick_menu = False

    while True:

        ## A story beat can be waiting at this location.
        $ _story = pick_event("story", loc=here)
        if _story:
            call play_event(_story)

        call screen sb_place
        $ _r = _return

        if _r[0] == "map":
            call sb_travel

        elif _r[0] == "char":
            call sb_person(_r[1])

        elif _r[0] == "act":
            call expression "sb_do_" + _r[1]

    return


label sb_travel:

    call screen sb_map
    $ _m = _return

    if _m[0] == "go":
        $ _ok, _why = can_enter(_m[1])
        if not _ok:
            "[_why]"
        else:
            $ here = _m[1]
            scene expression graded_bg()
            with Dissolve(0.4)
    return


label sb_person(who):

    call screen sb_char(who)
    $ _p = _return

    if _p[0] == "do":
        call sb_activity(_p[1], _p[2])

    return


label sb_activity(aid, who):
    """Run one activity, then charge the clock for it."""

    $ _a = ACT_BY_ID[aid]

    if aid == "talk":
        call sb_smalltalk(who)
        return

    if aid == "hang":
        $ _e = pick_event("hangout", who, here)
        if _e:
            $ spent_today.add(who)
            call play_event(_e)
            $ advance_period()
        else:
            "Nothing comes of it today."
        return

    if aid == "invite":
        call act_invite(who)
        return

    ## Everything else is a scene, then the clock.
    $ spent_today.add(who)
    call expression "act_" + aid pass (who)
    if _a["cost"]:
        $ advance_period(_a["cost"])
    return


################################################################################
## Location actions
################################################################################

label sb_do_wait:
    "You let the time pass."
    $ advance_period()
    return


label sb_do_sleep:
    scene expression graded_bg() with Dissolve(0.6)
    "You sleep."
    $ new_day()
    scene expression graded_bg() with Dissolve(0.6)
    "Day [day]. [period]."
    return


label sb_do_study:
    "You sit at the desk with the one textbook Ijichi gave you and read the same four hundred pages again."
    $ gain("insight", 3)
    $ spend_stamina(8)
    $ advance_period()
    return


label sb_do_eat:
    if stamina >= stamina_max:
        "You're not hungry."
        return
    "You eat. It is astonishing how much of being a sorcerer is remembering to eat."
    $ stamina = min(stamina_max, stamina + 35)
    $ restore_ce(10)
    return


label sb_do_rest:
    if "shoko" in who_is_here():
        shoko "Sit. Let me look at you."
        "She runs something warm and green over your forearms and the ache goes out of them."
        $ add_bond("shoko", 1)
    else:
        "The infirmary is empty. You lie down on the paper-covered bed for twenty minutes and it helps more than it should."
    $ stamina = stamina_max
    $ restore_ce(20)
    return


label sb_do_think:
    "You sit on the roof with your legs through the railing and do nothing at all."
    $ gain("insight", 2)
    $ restore_ce(15)
    $ advance_period()
    return


label sb_do_swim:
    if stamina < 15:
        "You are far too tired to get in that water."
        return
    scene bg riverside with Dissolve(0.5)
    $ _folk = [c for c in who_is_here() if c != "gojo"]
    if _folk:
        $ _w = renpy.random.choice(_folk)
        $ _n = CAST[_w]["short"]
        "[_n] is already in, and makes a noise you will be hearing for a week when you go under."
        $ add_bond(_w, 3)
        if is_romanceable(_w):
            $ add_aff(_w, 2)
    else:
        "The water is snowmelt cold and you lose about nine seconds of thinking to it."
    "You swim until your arms complain, and climb out onto the warm stones, and lie there."
    $ gain("output", 2)
    $ spend_stamina(12)
    $ restore_ce(12)
    $ advance_period()
    return


label sb_do_train:

    if stamina < 15:
        "You're too tired to get anything out of it. Eat, or sleep."
        return

    $ _spot = LOCATIONS[here]["name"]
    "You train. [_spot], alone, until the light goes."

    if here == "ridge":
        $ gain(tech()["scales"], 4)
        $ gain("output", 1)
    elif here == "dojo":
        $ gain("control", 2)
        $ gain("output", 2)
    elif here == "forest":
        $ gain("insight", 3)
    else:
        $ gain("control", 3)

    $ spend_stamina(18)
    $ ce_max = min(140, ce_max + 1)
    $ advance_period()
    return


label sb_spar(who):

    if stamina < 15:
        "You've got nothing left in the tank. Not today."
        return

    $ _n = CAST[who]["short"]

    if who == "maki":
        maki "Weapon or no weapon."
        mc "No weapon."
        maki "Wrong answer. Pick one up."
        "She puts you on the floor eleven times and explains exactly why each time, and the eleventh explanation is different from the first."
        $ gain("output", 3)
        $ gain("control", 1)
    elif who == "yuji":
        yuji "Okay — back foot! Remember the back foot!"
        "Yuji Itadori is a startlingly good teacher, because he explains everything twice in two different ways and never once makes you feel stupid."
        $ gain("output", 4)
    else:
        panda "Alright, come at me. I'm structurally very forgiving."
        "Hitting a two-metre cursed corpse turns out to be excellent for confidence and terrible for your knuckles."
        $ gain("output", 2)
        $ gain("control", 2)

    $ add_bond(who, 4)
    if is_romanceable(who):
        $ add_aff(who, 1)
    $ spend_stamina(20)
    $ advance_period()
    return


################################################################################
## Technique verbs
################################################################################

label sb_do_replay:

    if not spend_ce(10):
        "You don't have the reserve for it."
        return

    $ _folk_earlier = []
    python:
        _i = period_index()
        if _i > 0:
            _prev = PERIODS[_i - 1]
            _folk_earlier = [c for c in roster if char_location(c, _prev) == here]

    "You put your hand flat against the nearest surface and let the place play itself back."

    if _folk_earlier:
        $ _names = ", ".join(CAST[c]["short"] for c in _folk_earlier)
        "Earlier this [period.lower()], this room held: [_names]."
        $ _w = renpy.random.choice(_folk_earlier)
        $ _n = CAST[_w]["short"]
        $ add_bond(_w, 2)
        "You hear a minute of [_n] that [_n] would not have said to your face. You understand them slightly better for it, and feel slightly worse."
    else:
        "Nobody has been here for hours. Just wind, and the building settling, and something small in the walls."

    $ gain("insight", 2)
    return


label sb_do_temper:

    if not spend_ce(15):
        "Not enough reserve to hold a burn that long."
        return
    "You work the forge in the back of the storehouse, feeding Emberfall into a blade until the heat stops needing you."
    $ gain("output", 4)
    $ gain("control", 1)
    $ flag("tempered_a_tool")
    $ spend_stamina(15)
    $ advance_period()
    return


label sb_do_tools:
    "Racks of sealed boxes, each labelled in handwriting that has been getting worse for forty years."
    $ gain("insight", 1)
    return


################################################################################
## Missions
################################################################################

label sb_do_missions:

    if "yaga" not in who_is_here():
        "The office is empty. The mission board has three notices, all of them about laundry."
        return

    $ _story = pick_event("mission", loc="office")

    if _story:
        call play_event(_story)
        return

    yaga "Nothing that needs a first-year today."
    yaga "Train. Eat. Sleep. That is an order, and it's the one people ignore."
    return


## Repeatable low-grade work, so the sandbox never dead-ends. ###################

label sb_patrol:

    yaga "Grade four. Residual curse in a stairwell two stations out. Take someone."
    $ _p = closest_first_year()
    $ _pn = CAST[_p]["short"]

    scene bg city with fade_hard
    "You and [_pn] spend four hours in a stairwell that smells of wet concrete, and kill something the size of a dog, and fill in a form about it."

    $ add_bond(_p, 3)
    $ gain(tech()["scales"], 3)
    $ spend_stamina(25)
    $ advance_period(2)

    scene bg office with fade_hard
    yaga "Filed. Go eat something."
    return
