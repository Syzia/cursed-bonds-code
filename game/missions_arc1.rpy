################################################################################
## Arc 1 — the Surveyor.
##
## Yaga said he had the name of the man who filed the Sun Mall as a grade 3.
## This is what happens when he uses it.
################################################################################

init 1 python:
    ev("ms_nade_1", kind="mission", loc="office", min_day=10, priority=80,
       requires=("sunmall_done",))
    ev("ms_nade_2", kind="mission", loc="office", min_day=14, priority=80,
       requires=("nade_named",))
    ev("ms_nade_3", kind="mission", loc="office", min_day=18, priority=90,
       requires=("nade_traced",))


################################################################################

label ms_nade_1:

    yaga "Ryōsuke Nade."

    yaga "Grade 2. Fourteen years in the field, six of them in assessment. He is the man who walked around the Kawagoe Sun Mall for forty minutes and wrote {i}three{/i} on a form."

    yaga "I have pulled every survey he has filed since April. There are sixty-one."

    yaga "Eleven of them are wrong."

    mc "Wrong how?"

    yaga "Low. All eleven. Never high."

    "He does not raise his voice. He has not raised his voice once since you arrived, and it is beginning to occur to you that this is not calm."

    yaga "You are going to look at one of them. A disused freight warehouse in Kawaguchi, filed grade 4 in June, no follow-up."

    yaga "Take someone. If it is a grade 4, you will be home by six."

    $ _p = closest_first_year()
    $ _pn = CAST[_p]["short"]

    scene bg city with fade_hard
    show expression _p at pos_cr
    show mc at pos_l
    with dissolve

    "The warehouse has been empty for nine years. The door is chained from the inside, which is the first thing that is wrong, because somebody chained it and then did not leave."

    if technique == "aftersound":
        "You let it play. Six weeks ago a man in a suit walked the length of this floor with a clipboard, stopped in the middle, stood still for eleven minutes, and left without writing anything."
        $ gain("insight", 2)
        $ flag("heard_nade_survey")

    "[_pn] gets a hand on your sleeve before you are four metres in."

    if _p == "megumi":
        megumi "That's not a four."
    elif _p == "nobara":
        nobara "That is absolutely not a four."
    else:
        yuji "Uh — that's not a four, right? Tell me that's not a four."

    show expression _p at pos_fr
    with move

    "It comes down off the roof beams in a way that a grade 4 does not have the mass to do."

    call combat("warehouse", _p, True, "bg city")
    $ _r = _return

    if _r == "win":
        "It comes apart across the loading bay floor and the chain on the door is still hanging there, holding nothing shut."
        $ add_bond(_p, 6)
        $ gain("output", 3)
        $ flag("warehouse_cleared")
    elif _r == "down":
        "You go down on the concrete and the last thing you see is [_pn] putting themselves between you and it."
        "You wake in the infirmary with Shoko already halfway through the paperwork, and a headache, and both of you alive."
        $ add_bond(_p, 8)
        $ stamina = stamina_max
        $ flag("warehouse_costly")
    else:
        "You get out. Both of you, through the fire door, into an afternoon that has no idea."
        "It is the correct call and it feels like nothing of the sort."
        $ flag("warehouse_withdrew")

    scene bg office with fade_slow
    show yaga at pos_c
    with dissolve

    yaga "Grade two."

    yaga "Filed as a four, in June, by a man who has been doing this for fourteen years."

    "He writes something down. It takes a while."

    yaga "Nade is not clever. I have met him. He is not clever and he is not cruel."

    yaga "Which means somebody is telling him what to write."

    $ flag("nade_named")
    $ advance_period(2)
    return


label ms_nade_2:

    yaga "Nade has stopped answering the Grading Office. Three weeks."

    yaga "His filings still arrive. Same hand, same phrasing, from an address in Saitama that is a records annexe nobody has staffed since 2019."

    yaga "Go and look at the annexe. Do not engage him. Look."

    scene bg ruin with fade_curse
    show mc at pos_l
    with dissolve

    "The annexe is two floors of shelving and a smell of wet paper."

    "Somebody has been here recently. There is a kettle, and a cup, and a cushion on an office chair that has been sat in for a very long time by somebody who did not want to go home."

    "And on the desk, in neat stacks: survey forms. Blank ones. Pre-signed."

    mcthink "He signs them empty."

    mcthink "Somebody else fills in the grade."

    if technique == "filament":
        "Your threads find the drawer under the desk before your hands do. There is a phone in it, switched off, and a second one that is not."
        $ gain("control", 2)
        $ flag("found_the_phone")
    elif technique == "aftersound":
        "The room replays: a man on the phone, saying {i}I can't keep doing eleven, someone's going to count them{/i}, and then not saying anything for a long time while somebody on the other end talks."
        $ gain("insight", 3)
        $ flag("heard_the_call")

    "The shikigami is in the stairwell, and it has been left here, which means Nade knew somebody would come."

    call combat("nade_curse", None, True, "bg ruin")
    $ _r = _return

    if _r == "win":
        "It goes down hard and does not get up, and the paper in the stairwell settles for a long time afterwards."
        $ gain(tech()["scales"], 4)
        $ flag("annexe_cleared")
    elif _r == "down":
        "You wake up on the annexe floor with your cheek on a survey form and no idea how long you were out."
        "Nothing has taken anything. It was never here to kill you. It was here to make you slow."
        $ stamina = stamina_max
    else:
        "You get out with a fistful of the pre-signed forms and a shikigami still standing between you and the stairs."

    "You take a form with you. Blank, signed, waiting for a number."

    $ flag("nade_traced")
    $ advance_period(2)

    scene bg office with fade_slow
    return


label ms_nade_3:

    yaga "We have him."

    yaga "A flat in Toda. He has been there eleven days and has not left it."

    yaga "You are going because he will not run from a first-year, and because I want somebody in that room who has actually stood in one of his grade fours."

    yaga "Gojo will be four streets away eating something. That is as much supervision as this warrants."

    scene bg town_street with fade_slow
    show nade at pos_cr
    show mc at pos_l
    with dissolve

    "Ryōsuke Nade is forty-six and has not slept properly in some time. He opens the door before you knock."

    nade "You're one of Yaga's."

    nade "...You're a first-year."

    nade "He sent a {i}first-year.{/i}"

    "He laughs, and it goes on slightly too long, and stops."

    menu:
        "He has not invited you in and he has not closed the door."

        "\"I was in the Kawaguchi warehouse.\"":
            $ gain("insight", 2)
            $ flag("nade_confronted_hard")
            nade "...The freight one. June."
            nade "Was anyone with you?"
            mc "A first-year."
            nade "..."
            nade "I'm sorry."
            "He means it, which is somehow much worse than if he had not."

        "\"Who fills in the numbers?\"":
            $ gain("insight", 3)
            $ flag("nade_asked_direct")
            nade "You've seen the forms, then."
            nade "Good. Somebody should have seen them in 2021."

        "Say nothing.":
            $ gain("control", 2)
            "You let the silence sit on the doorstep with him."
            "It takes about forty seconds."
            nade "I'm going to tell you, because I've been waiting three weeks for someone to make me."

    nade "I sign them blank. I have signed them blank since 2020."

    nade "He said it was for speed. Assessment backlog, six weeks behind, sign the sheets and he'd fill in what the survey found."

    nade "And the first year the numbers were right. That's the part nobody believes. {i}The first year the numbers were right.{/i}"

    mc "And then?"

    nade "And then there was a three that should have been a two, near a school with a promising second-year in it."

    nade "And she lived. And she got very good, very fast."

    nade "And I understood what I was signing, and by then I had signed four hundred of them."

    "He goes inside and comes back with an A3 sheet folded into eighths, and holds it out, and does not let go of it immediately."

    nade "Don't tell me his name. I've spent six years not knowing it on purpose and I'd like to keep that."

    "It is a map of the Kantō region. There are eleven circles on it in red, and a twelfth in a different hand."

    "The twelfth is around a town you know extremely well, because you grew up in it, and the date beside it is four years before the East Wing."

    mcthink "Four years."

    mcthink "It was in the diary before I ever went into that corridor."

    $ flag("nade_map")
    $ flag("cartographer_seeded")
    $ gain("insight", 4)
    $ advance_thread("gojo_measure", 1)

    scene bg office with fade_slow
    show yaga at pos_c
    with dissolve

    yaga "..."

    yaga "Say the last part again."

    mc "My town. Circled. Four years before I awakened."

    "Yaga Masamichi sits down, which you have never seen him do in his own office."

    yaga "Then you were not found."

    yaga "You were {b}scheduled.{/b}"

    yaga "Say nothing about this to your year. Not yet. That is not me protecting them, it is me not knowing who else signs blank forms."

    $ flag("arc1_villain_revealed")
    $ advance_period(2)
    return
