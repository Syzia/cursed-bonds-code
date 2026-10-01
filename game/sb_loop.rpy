################################################################################
## Cursed Bonds — the sandbox loop.
##
## Everything the player does on campus routes through here.
##
## WP7 (PHASE1_DESIGN.md 2.1, 4.4, 4.5, D9, D26, D31). Saves sit on the
## statements the loop waits at, so these stay textually identical (2.1.1):
## `call screen sb_place`, `$ _r = _return`, `call screen sb_map`,
## `$ _m = _return`, `call screen sb_char(who)`, `$ _p = _return`,
## `call sb_activity(_p[1], _p[2])`, `call play_event(_story)`,
## `call expression "sb_do_" + _r[1]` and `call expression "act_" + aid pass (who)`.
## New branches are new elif lines. Retired labels stay (2.1.2).
################################################################################

label sandbox:

    while True:

        $ ensure_state()

        ## A story beat can be waiting at this location.
        $ _story = None if explore_mode else pick_event("story", loc=here)
        if _story:
            call play_event(_story)

        $ check_objective()
        call screen sb_place
        $ _r = _return
        $ objective_leave()

        if _r[0] == "map":
            call sb_travel

        elif _r[0] == "char":
            call sb_person(_r[1])

        elif _r[0] == "act":
            call expression "sb_do_" + _r[1]

        elif _r[0] == "mission":
            call start_mission(_r[1])

        elif _r[0] == "journal":
            call screen journal(_r[1])
            $ _j = _return
            if isinstance(_j, tuple) and _j and _j[0] == "arc_two":
                call arc_two_start

        elif _r[0] == "dev":
            call dev_tools

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

    elif _m[0] == "district":
        call sb_trip(_m[1])
    return


label sb_person(who):

    call screen sb_char(who)
    $ _p = _return

    if _p[0] == "do":
        call sb_activity(_p[1], _p[2])

    elif _p[0] == "mission":
        call start_mission(_p[1])

    elif _p[0] == "act":
        call expression "sb_do_" + _p[1]

    return


label sb_activity(aid, who):
    ## Run one activity, then charge the clock for it.

    $ _a = ACT_BY_ID[aid]

    if aid == "talk":
        call stage_person(who)
        call sb_smalltalk(who)
        scene expression graded_bg()
        return

    if aid == "hang":
        $ _e = pick_event("hangout", who, here)
        if _e:
            $ spent_today.add(who)
            call play_event(_e)
            $ advance_period()
        else:
            "Nothing comes of it today."
        scene expression graded_bg()
        return

    if aid == "invite":
        call stage_person(who)
        call act_invite(who)
        scene expression graded_bg()
        return

    ## A spar needs something left in the tank; refusing it costs nothing.
    if aid == "train" and stamina < 15:
        "I've got nothing left in the tank. Not today."
        return

    ## Everything else is a scene, then the clock.
    $ spent_today.add(who)
    call stage_person(who)
    call expression "act_" + aid pass (who)
    $ record_act(aid, who)
    if aid in TRAIN_TOGETHER:
        $ train_together(who, *TRAIN_TOGETHER[aid])
    if _a.get("once"):
        $ flag("did_%s_%s" % (aid, who))
    if _a["cost"] and aid != "train":    ## sb_spar charges its own period
        $ advance_period(_a["cost"])
    scene expression graded_bg()
    return


################################################################################
## Location actions
################################################################################

label sb_do_wait:
    "I let the time pass."
    $ advance_period()
    return


label sb_do_sleep:
    scene expression graded_bg() with Dissolve(0.6)
    "I sleep."
    $ new_day()
    scene expression graded_bg() with Dissolve(0.6)
    "Day [day]. [period]."
    return


label sb_do_study:
    "I sit at the desk with the one textbook Ijichi gave me and read the same four hundred pages again."
    $ gain("insight", 3)
    $ spend_stamina(8)
    $ advance_period()
    return


label sb_do_eat:
    if stamina >= stamina_max:
        "I'm not hungry."
        return
    "I eat. It is astonishing how much of being a sorcerer is remembering to eat."
    $ stamina = min(stamina_max, stamina + 35)
    $ restore_ce(10)
    return


label sb_do_rest:
    if "rest" in actions_today:
        "I've already been patched up today. The infirmary doesn't do seconds."
        return
    $ actions_today.add("rest")
    if "shoko" in who_is_here():
        shoko "Sit. Let me look at you."
        "She runs something warm and green over my forearms and the ache goes out of them."
        $ add_bond("shoko", 1)
    else:
        "The infirmary is empty. I lie down on the paper-covered bed for twenty minutes and it helps more than it should."
    $ stamina = stamina_max
    $ restore_ce(20)
    return


label sb_do_think:
    "I sit on the roof with my legs through the railing and do nothing at all."
    $ gain("insight", 2)
    $ restore_ce(15)
    $ advance_period()
    return


label sb_do_swim:
    if stamina < 15:
        "I am far too tired to get in that water."
        return
    scene bg riverside with Dissolve(0.5)
    $ _folk = [c for c in who_is_here() if c != "gojo"]
    if _folk:
        $ _w = renpy.random.choice(_folk)
        $ _n = CAST[_w]["short"]
        "[_n] is already in, and makes a noise I will be hearing for a week when I go under."
        $ add_bond(_w, 3)
        if is_romanceable(_w):
            $ add_aff(_w, 2)
    else:
        "The water is snowmelt cold and I lose about nine seconds of thinking to it."
    "I swim until my arms complain, and climb out onto the warm stones, and lie there."
    $ gain("output", 2)
    $ spend_stamina(12)
    $ restore_ce(12)
    $ advance_period()
    return


label sb_do_train:

    if stamina < 15:
        "I'm too tired to get anything out of it. Eat, or sleep."
        return

    $ _spot = LOCATIONS[here]["name"]
    "I train. [_spot], alone, until the light goes."

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
    $ raise_reserve(1)
    $ advance_period()
    return


label sb_spar(who):

    if stamina < 15:
        "I've got nothing left in the tank. Not today."
        return

    $ _n = CAST[who]["short"]

    if who == "maki":
        maki "Weapon or no weapon."
        mc "No weapon."
        maki "Wrong answer. Pick one up."
        "She puts me on the floor eleven times and explains exactly why each time, and the eleventh explanation is different from the first."
    elif who == "yuji":
        yuji "Okay — back foot! Remember the back foot!"
        "Yuji Itadori is a startlingly good teacher, because he explains everything twice in two different ways and never once makes me feel stupid."
    elif who == "megumi":
        megumi "No dogs. You won't learn anything if I call the dogs."
        "He barely says another word for an hour. He just keeps being a step to the left of wherever I aim, until I finally start aiming there."
    elif who == "nobara":
        nobara "No hammer, no nails. I'm going easy on you, so don't make it weird."
        "She is not going easy on me. She fights like she's settling a grudge she had before I arrived, and she laughs every time I get back up."
    elif who == "toge":
        toge "Tuna mayo!"
        "He taps the collar over his mouth, which I take to mean no Cursed Speech, and then spends an hour being very quick and very hard to find."
    elif who == "panda":
        panda "Alright, come at me. I'm structurally very forgiving."
        "Hitting a two-metre cursed corpse turns out to be excellent for confidence and terrible for my knuckles."
    else:
        "[_n] doesn't go easy on me, which is the kindest thing anyone does for me all day."

    ## Training together grows them as well as me (3.4).
    $ train_together(who, 3, "output")
    $ add_bond(who, 4)
    if is_romanceable(who):
        $ add_aff(who, 1)
    $ spend_stamina(20)
    $ advance_period()
    return


## A companion peels off (4.4: "[name] is with me · let them go"). ##############

label sb_do_release:
    if companion:
        $ _n = CAST[companion]["short"]
        $ companion = None
        "[_n] peels off with a half-wave and goes back to their own day."
    return


################################################################################
## Technique verbs
################################################################################

label sb_do_hold:

    if "hold" in actions_today:
        "I've already held one hour today. A second one won't come."
        return

    $ _cost = max(20, ce_max // 2)

    if not spend_ce(_cost):
        "Not nearly enough reserve. Holding an hour costs most of everything I have."
        return

    $ actions_today.add("hold")

    "Last Light. I find the instant the lights went out, the one I keep, and put my weight on it."

    "Colour goes out of everything. The dust hangs where it is. One light stays warm, the way it did in the alley, and nothing else moves."

    "I stand in it alone for as long as I can hold it, and then I let it go, and the hour arrives exactly where it was."

    $ gain("control", 2)
    $ spend_stamina(12)
    $ flag("held_an_hour")

    "The hour does not pass. I have it twice."

    return


## Retired (D31): the old technique's forge. Kept so a save made inside it
## still has somewhere to be.
label sb_do_temper:
    "The forge is cold."
    return


label sb_do_tools:
    if "racks" in actions_today:
        "I've looked already today. The racks haven't changed."
        return
    $ actions_today.add("racks")
    "Racks of sealed boxes, each labelled in handwriting that has been getting worse for forty years."
    "I look. I don't touch. Nothing on these racks leaves without a grade and a reason."
    $ gain("insight", 1)
    return


################################################################################
## Missions
################################################################################

## Retired (3.6.1): the place view no longer offers it; Yaga's missions start
## from the mission buttons. Kept for saves made inside it.
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


## Retired: repeatable low-grade work from before Utahime's board. ###########

label sb_patrol:

    yaga "Grade four. Residual curse in a stairwell two stations out. Take someone."
    $ _p = closest_first_year()
    $ _pn = CAST[_p]["short"]

    scene bg city with fade_hard
    "[_pn] and I spend four hours in a stairwell that smells of wet concrete, and kill something the size of a dog, and fill in a form about it."

    $ add_bond(_p, 3)
    $ gain(tech()["scales"], 3)
    $ spend_stamina(25)
    $ advance_period(2)

    scene bg office with fade_hard
    yaga "Filed. Go eat something."
    return
