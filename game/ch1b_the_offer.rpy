################################################################################
## Chapter One (b) — The Offer
##
## Gojo lays out two futures. One of them ends the game.
################################################################################

label chapter_one_b:

    scene bg konbini with fade_slow
    show gojo at pos_cr
    show mc at pos_l
    with dissolve

    "There is an ambulance somewhere behind you that will not be needed and a woman from the flats above who has come down and been sent back up again without appearing to notice she was sent."

    gojo "Two things are true as of about six minutes ago."

    gojo "One: you can see curses. That doesn't switch off. You will see them on trains and in supermarkets and outside your own front door for the rest of your life."

    gojo "Two: they can see {i}you.{/i} Cursed energy is food and you just started giving off a lot of it."

    mc "So what happens now."

    gojo "That's actually up to you, which is rarer than you'd think."

    gojo "Option one. There's a school. Tokyo Metropolitan Curse Technical College — it's in Tokyo and it's in a mountain and both of those are true, and I'll explain that badly at some point."

    gojo "You'd learn to use what opened tonight. You'd be with people who can do it too. And you'd be a sorcerer, which is a job where the retirement plan is mostly theoretical."

    gojo "Option two. I make tonight go away."

    mc "...Make it go away."

    gojo "You'd remember a power cut and an accident. You'd grieve properly, which matters. And you would never know any of this was real."

    menu:
        "He is not selling either one. He is standing in an alley at ten at night with his hands in his pockets, waiting."

        "\"Why is it my choice? You could just do it.\"":
            $ add_bond("gojo", 6)
            $ flag("gojo_asked_why")
            gojo "I could, yes."
            gojo "I've done it. Dozens of times. It's the kindest thing we do and I hate it, and I've stopped being willing to do it to someone who saw it happen with their eyes open."
            gojo "You looked at the thing that killed your friend. Somebody who does that gets asked."

        "\"If I forget — does she still count?\"":
            $ add_bond("gojo", 8)
            $ flag("gojo_asked_sana")
            "It is the first thing you have said that makes him stop moving."
            gojo "..."
            gojo "She counts either way. She counted before I got here."
            gojo "But you'd be the only person alive who knew what actually happened to her, and then you wouldn't be."
            gojo "I'm not going to pretend that's nothing. It isn't nothing."

        "\"What would you do?\"":
            $ add_bond("gojo", 5)
            $ flag("gojo_asked_advice")
            gojo "Oh, I'd go. Obviously I'd go, look at me."
            gojo "But I was born into it and I've never once had to decide, so my answer's worth approximately nothing and you should weigh it accordingly."

    gojo "Take your time. I'm extremely patient about exactly one thing and this is it."

    "You take your time."

    "It is four minutes, and it is not enough, and it is all there is."

    menu:
        "Two futures, both of them bad in different ways."

        "Go with him.":
            $ flag("chose_jujutsu")
            jump ch1b_goodbye

        "Let him take it away.":
            $ flag("chose_forget")
            jump ch1b_the_other_road


################################################################################
## The road taken
################################################################################

label ch1b_goodbye:

    mc "I'll go."

    gojo "Okay."

    gojo "Then go home first. Say it properly. I'll be outside at seven and the paperwork is my problem, not yours."

    mc "What do I tell them?"

    gojo "The truth, if you want. They won't be able to hold onto the parts that matter — that's not me being cruel, it's just what happens near this."

    gojo "But you'll have said it. That's for you, not for them. Do it anyway."

    scene bg home_living with fade_slow
    show mother at pos_cl
    show father at pos_r
    with dissolve

    "You get home at eleven. Your mother is still up, because the school rang, because somebody has already made a call you did not hear about."

    "She has been crying. She hugs you for a very long time and does not ask a single question about the alley."

    mother "They said it was the power cut. That she fell."

    "You could correct her. You watch yourself not correct her, and file the feeling for later."

    menu:
        "Your father is standing in the kitchen doorway with a tea he has not drunk."

        "Tell them the truth.":
            $ flag("told_parents_truth")
            $ gain("insight", 2)
            "You tell them all of it. The dark, the thing in the alley, the man in the blindfold, the school in a mountain."
            "They listen. They believe you — you can see them believing you."
            "And then, somewhere around the third sentence, it goes out of them like water out of a cupped hand, and your mother says {i}well, a scholarship, that's wonderful{/i} in a voice with nothing wrong in it at all."
            mcthink "He told me. He told me and I did it anyway."
            mcthink "Good. I'd rather have said it."

        "Tell them it's a scholarship.":
            $ flag("told_parents_lie")
            $ gain("control", 2)
            mc "There's a school. They came to me tonight — they'd been watching, apparently."
            "Your father is so proud of you that you have to look at the floor."
            "It is a clean lie and it fits them perfectly and you understand, putting it on them, that you have just done to your parents exactly what Gojo offered to do to you."

        "Say almost nothing.":
            $ flag("told_parents_nothing")
            $ gain("control", 3)
            "You say you're going away to school, and that it's a good one, and that it happened fast."
            "Your mother makes you eat something. Your father says {i}well{/i} four times over an hour."
            "Nobody in the house sleeps, and nobody says so, and in the morning there is an enormous breakfast that nobody asked for."

    scene bg home_bedroom_night with fade_slow

    "You pack at two in the morning."

    menu:
        "There is room in the bag for one thing that isn't clothes."

        "The photo from the summer festival.":
            $ flag("took_photo")
            $ gain("insight", 1)
            "Three years old. Sana has her arm around your neck and is pulling you sideways out of frame, and you are laughing, and it is not a good photograph."

        "Her hachimaki.":
            $ flag("took_hachimaki")
            "She left it at yours in October and never asked for it back. Her name is inside the band in marker, in her handwriting."

        "Your father's watch.":
            $ flag("took_watch")
            $ gain("control", 1)
            "It has been in the drawer since before you were born. He puts it in your hand at the door in the morning and says {i}for the exams,{/i} and he thinks there are going to be exams."

        "Nothing.":
            $ flag("took_nothing")
            $ gain("control", 2)
            "You take clothes. You have decided, without being able to explain it, that you do not want anything from this house touching the next one."

    scene bg street_morning with fade_slow

    "The car is black and completely unremarkable and there is a man in a suit beside it who apologises to your father for the hour."

    "Your mother hugs you the correct amount. Your father shakes your hand, which he has never done."

    "As the door closes your mother puts her hand flat against the window, and for exactly one second there is something underneath her face trying to get out."

    "Then it is gone, and she smiles, and waves."

    mcthink "There. That was her."

    scene bg car with fade_slow

    voice_ "Sorry — it's about ninety minutes."

    "For something to do, you decide to count."

    scene bg black with fade_slow
    return


################################################################################
## The road not taken — this one ends
################################################################################

label ch1b_the_other_road:

    mc "Take it away."

    gojo "...Okay."

    gojo "For what it's worth, I think that's a reasonable thing to want and I'd have said yes to it at your age."

    "He puts two fingers against your forehead, almost gently."

    gojo "You won't remember this bit either. Sorry."

    scene bg black with fade_slow

    "There was a power cut on a Thursday in October and your friend Sana Torii had an accident in the alley behind the arcade."

    "It was very sad. Everyone said so."

    scene bg town_street with fade_slow

    "Winter comes. You go back to school in January because that is what there is to do."

    "You are fine. Everyone tells you how well you are doing and you agree with them."

    "Occasionally, in a shop or on a platform, you look at a place where there is nothing, for slightly too long, and then you stop."

    scene bg home_living with fade_slow
    show mother at pos_c
    with dissolve

    "In March your mother is in the kitchen at about six in the evening, and you are upstairs, and the lights go out."

    "All of them. At once."

    scene bg black with Dissolve(0.5)

    "You come down in the dark, because that is what a person does."

    "You call out. She does not answer."

    "You cannot see anything. You have never been able to see anything. That is the arrangement you agreed to in an alley in October and then forgot agreeing to."

    "You find her at the bottom of the stairs."

    "Something opens in you, four months late, for the second time in your life — and this time there is nobody in the doorway with his hands in his pockets."

    scene bg black with flash_white

    "You can see it."

    "You can see it, and you have no idea what to do, and the thing in your chest goes off like a dropped glass — all of it, at once, in every direction, with no shape on it at all."

    "It takes about nine seconds."

    "They will say it was the gas."

    scene bg black with fade_slow
    $ renpy.pause(1.6)

    show screen chapter_card("AN ENDING", "The Quiet Option", "You were asked once, in an alley, and you said no.")
    with fade_slow
    $ renpy.pause(5.0)
    hide screen chapter_card
    with fade_slow

    "Some choices are made before you know what you are choosing."

    "This was one, and it was offered fairly, and it was yours."

    $ renpy.pause(2.0)
    $ renpy.full_restart()

    return
