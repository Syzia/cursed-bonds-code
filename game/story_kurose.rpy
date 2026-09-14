################################################################################
## Arc 1 — the paperwork.
##
## The administrative horror thread, relocated from the old prologue. It works
## better here: Sana is dead, her parents have been given a story, and the
## player is the only person alive who knows what actually happened.
################################################################################

init 1 python:
    ev("st_kurose", kind="story", min_day=3, periods=["Afternoon", "Evening"],
       priority=98, requires=("roll_call",))
    ev("st_kurose_2", kind="story", min_day=12, periods=["Evening"],
       priority=88, requires=("kurose_met",))


################################################################################

label st_kurose:

    scene bg office with fade_slow
    show kurose at pos_c
    with dissolve

    "There is a man waiting outside the principal's office who is not a teacher and is not a sorcerer, and who stands up when you arrive and bows to you before he says anything."

    kurose "Kurose. Auxiliary management."

    kurose "I handle the civilian side. I have four forms and about nine minutes of your time, and then you will not see me again for a while."

    "He does not apologise for the intrusion. Ijichi would have apologised twice by now."

    kurose "The Torii family have been told there was a structural failure in the alley behind the arcade — a transformer housing. It is a real transformer housing and it did fail, six weeks ago, in Chiba."

    kurose "They have a coroner's report. It is accurate in every particular except one."

    mc "You lied to her parents."

    kurose "I gave them a version they can survive."

    kurose "The true one has a four-metre curse in it that nobody can see. There is nothing in that sentence a father can do anything with."

    menu:
        "He has the forms in a folder and has not opened it."

        "\"They'd want to know.\"":
            $ flag("kurose_argued")
            $ gain("output", 2)
            kurose "Almost everyone says that."
            kurose "In eleven years I have met two families who were better off knowing, and both of them had a sorcerer in the household already."
            kurose "The rest spend the remainder of their lives certain that something is in the room, and correct, and unable to prove it."
            kurose "I am not defending it. You asked what we do; that is what we do."

        "\"What did you tell my parents?\"":
            $ flag("kurose_asked_family")
            $ gain("insight", 3)
            kurose "That you were offered a place at a specialist school, at short notice, with a full bursary."
            kurose "Your mother asked which school. I told her. She will not be able to hold the name."
            mc "You did something to them."
            kurose "I filed something. There is a difference and it will stop mattering to you in about a month."

        "Say nothing. Read the forms.":
            $ flag("kurose_read")
            $ gain("insight", 4)
            "You take the folder and go through it properly while he waits, which he permits without any sign of impatience."
            "Three of the four are ordinary. The fourth is one sheet, no letterhead, no stamp, one signature line, and the sentences do not stay the same length when you look away and back."
            kurose "Most people don't read that one."
            kurose "That's fine too."

    "You sign. There is no version of the afternoon where you do not sign, and he has not once pretended otherwise."

    kurose "One more thing, and then I'll go."

    kurose "You are now the only living person who knows what happened in that alley."

    kurose "Her parents don't. Her school doesn't. In about four years, her friends will remember a girl who died in an accident, and the accident will be the shape of her."

    kurose "If that is going to be a problem for you, it is better that it becomes a problem now, in a corridor, than in eighteen months on a job."

    menu:
        "He says it without unkindness, which is what makes it land."

        "\"It's not a problem.\"":
            $ flag("kurose_cold")
            $ gain("control", 3)
            mc "I'll carry it. That's the whole job, isn't it."
            kurose "...Yes."
            kurose "You are going to be extremely good at this, and I am not certain that is a compliment."

        "\"It's going to be a problem.\"":
            $ flag("kurose_honest")
            $ add_bond("shoko", 4)
            $ gain("insight", 3)
            mc "Yes. Obviously yes. I'm not going to pretend it isn't."
            kurose "Good. Say that to Ieiri rather than to me — she is paid for it and I am not."
            "It is the single most useful sentence anybody says to you that week."

        "\"Does it get easier for you?\"":
            $ flag("kurose_asked_him")
            $ add_bond("yaga", 3)
            $ gain("insight", 2)
            "He stops with the folder half closed."
            kurose "No."
            kurose "I have done four hundred and six of these. I remember the names of all of them."
            kurose "That is not a boast. It is the only part of the job I am certain is correct."

    $ flag("kurose_met")
    $ flag("kurose_card")
    $ advance_period()

    scene expression graded_bg() with fade_slow
    return


################################################################################

label st_kurose_2:

    scene bg dorm with fade_slow

    "An envelope has been put under your door, squarely, by somebody who did not knock."

    "Inside is a photocopy of a single page: an assessment survey for the commercial street behind the arcade, dated in April, filed as clear."

    "There is a compliments slip clipped to it with one line on it in small, level handwriting."

    voice_ "You asked what we do. This is the part I am not certain is correct. — K"

    "The surveyor's signature is a name you do not know yet."

    if has_flag("wakuri_seeded"):
        mcthink "Gojo asked to see who filed that street."
        mcthink "Somebody has got there first, and posted it under my door instead of his."

    $ gain("insight", 4)
    $ flag("kurose_leak")
    $ flag("nade_prefigured")

    "You put it in the drawer with your father's watch, or your photograph, or the nothing you brought with you."

    "It sits there for some time."

    return
