################################################################################
## Arc 1 — the road home.
##
## Oda-sensei is not family, so the veil did not take: it is filed on
## households. She is the counterweight to Kurose — he files, she notices —
## and the only line still running off this mountain.
################################################################################

init 1 python:
    ## Priority 84: yields to the incident, to Kurose's follow-up and to every
    ## other story beat. A letter can wait for a quiet evening. Order and gaps
    ## come from the mission chain (m_oda_letter, m_oda_2).
    ev("st_oda_letter", kind="story", periods=["Evening"],
       priority=84, requires=("kurose_met",))
    ev("st_oda_2", kind="story", periods=["Evening"],
       priority=86, requires=("oda_answered",))


################################################################################

label st_oda_letter:

    scene bg your_room night with fade_slow

    "There is a letter on your desk."

    "Not an envelope under the door — a letter, stamped, addressed, that has come through an actual postal system to a school whose name your own mother cannot hold in her head."

    "The handwriting is small and fast and you know it from two years of corrected homework."

    oda "[mc_surname]-kun."

    oda "I am aware this may not reach you and I am sending it anyway."

    oda "You left on the Sunday after the accident. The school was told on the Friday — two days before, which I have thought about a great deal."

    oda "I asked the office for the name of the institution. They gave it to me. I wrote it down, and when I looked at the note an hour later I could read it perfectly well and could not hold it in my head for more than about four seconds."

    oda "I have been teaching for nineteen years. I know what a bereaved student looks like and I know what a transferred one looks like, and I have never before had to write to an address I cannot remember."

    oda "Two things, then I will stop."

    oda "One. Sana's mother asked me at the service whether you were all right. I said yes. I would like that to have been true."

    oda "Two. I am not asking what happened. I am telling you that I noticed, so that there is one person left who did."

    oda "— Oda"

    "There is a telephone number at the bottom. It is the same one she wrote on the back of a form once, in a classroom, in another life."

    mcthink "Kurose said I was the only living person who knows."

    mcthink "He was wrong by one."

    menu:
        "Nine days, and the first thing from outside the fence."

        "Write back. The truth.":
            $ flag("oda_answered")
            $ flag("oda_told_truth")
            $ gain("insight", 3)
            "You write four pages and send three of them."
            "You tell her that Sana did not fall, that there was something in the alley, that you can see them now and could not before, and that the school is real and is in a mountain."
            "You do not expect her to be able to keep it. You have watched your mother fail to keep considerably less."
            mcthink "She kept the note for an hour."
            mcthink "That's longer than anyone else has managed."

        "Write back. Carefully.":
            $ flag("oda_answered")
            $ flag("oda_careful")
            $ gain("control", 3)
            "You write half a page that says you are all right, that the school is real, and that she was right to notice and should now stop."
            "It is a kind letter and a closed door and you are aware of building it."
            mcthink "That's the second time this month I've handed somebody a version they can survive."
            mcthink "I'm getting quick at it."

        "Don't answer.":
            $ flag("oda_ignored")
            $ gain("control", 2)
            "You put the letter in the drawer."
            "You take it out twice over the following week and put it back both times, which is its own kind of answer."
            mcthink "Kurose was clear about what happens to civilians who get close."
            mcthink "The kindest thing I can do is be a dead line."

    $ flag("oda_letter_read")
    $ advance_period()
    scene expression graded_bg() with fade_slow
    return


################################################################################

label st_oda_2:

    scene bg your_room night with fade_slow

    "Oda-sensei writes again, and this one is not a letter about you."

    oda "I have been doing something I suspect I should not."

    oda "You will remember I am the year's records officer, which mostly means I chase people for forms. It also means I can see regional transfer notices."

    oda "In the last four years, nine students in this prefecture have transferred out at short notice, mid-term, to schools the paperwork does not name."

    oda "Two of them I taught. One of them was a boy called Sōma with terrible handwriting who was not remotely academic, and the notice describes a specialist bursary."

    oda "Three of the nine are recorded as having died within the following eighteen months. The causes are ordinary and the reports are thorough."

    oda "I am not able to say what I think this is. I want to be clear that I have not lost my grip on anything. I have simply counted, twice."

    "There is a photocopy folded inside: a transfer notice, four years old, with a surveyor's countersignature in a corner."

    if has_flag("kurose_leak") or has_flag("nade_prefigured"):
        "You have seen that signature before. It was on the compliments slip that came under your door."
        $ gain("insight", 4)
        $ flag("oda_corroborates")
    else:
        "You do not know the signature. You copy it out anyway and put it in the drawer."
        $ gain("insight", 2)

    "And at the bottom, in smaller writing, the part she has clearly thought hardest about:"

    oda "A man came to the school in February and asked, very politely, whether anyone had been enquiring about transfer records."

    oda "I told him no."

    oda "I would like you to know that I lied to him, deliberately, and that I am not frightened, and that both of those things are true."

    menu:
        "Nine students. Three dead. A polite man asking questions in February."

        "Tell her to stop. Now.":
            $ flag("oda_warned_off")
            $ gain("control", 3)
            "You write one page. You tell her exactly what she is close to, in plain terms, without softening it — and that the man in February was real, and that the next one will not ask politely."
            "She writes back four days later: {i}Understood. I have stopped. I am keeping the copies.{/i}"
            mcthink "She's stopped and she's kept them."
            mcthink "That's not stopping. That's waiting."

        "Ask her for the other six names.":
            $ flag("oda_recruited")
            $ add_bond("yaga", 4)
            $ gain("insight", 4)
            "You ask for the names, and the dates, and anything she can get without being seen getting it."
            "She sends them in a fortnight. It takes her four attempts to post the letter, because she keeps going back for something she has forgotten, which is what happens near this."
            mcthink "I have just made a civilian into an asset."
            mcthink "The other week I sat in an office being told what that costs."

        "Say nothing. Take it to Yaga.":
            $ flag("oda_escalated")
            $ add_bond("yaga", 6)
            $ gain("insight", 3)
            "You put the letter on Yaga's desk and say nothing while he reads it."
            "He reads it twice."
            yaga "A homeroom teacher in a prefecture with no jujutsu presence has found in three weeks something my office has not found in four years."
            yaga "I want you to sit with what that means about my office."
            yaga "I will handle her safety. You will not write to her again until I say. That is not a punishment — it is the only version of this where she is still teaching in a year."

    $ flag("oda_thread_open")
    $ advance_period()
    scene expression graded_bg() with fade_slow
    return
