################################################################################
## Chapter One (b) — The Offer
##
## Gojo names what I did, then lays out two futures. One of them ends the game.
##
## WP9 (phase 1): first person (PHASE1_DESIGN.md 5.2). chapter_one_b is one
## prologue step; it jumps to ch1b_goodbye or ch1b_the_other_road, and each of
## those also stands on its own as a memory (they set the scene themselves).
################################################################################

label chapter_one_b:

    call prologue_catch_up("chapter_one_b")

    $ story_point = "chapter_one_b"

    scene bg alley with fade_slow
    show gojo serious at pos_c
    with dissolve

    "There is an ambulance somewhere behind me that will not be needed, and a woman from the flats above who has come down and been sent back up again without appearing to notice she was sent."

    gojo serious "Before anything else. The thing you did in there."

    gojo "You held the second the lights went out. Stopped it, and stood in it."

    gojo @ happy "Zank{font=DejaVuSans.ttf}ō{/font}. Last Light. Somebody has to put something on the form."

    $ flag("named_last_light")

    "He says it as if he is reading it off me. Maybe he is."

    gojo neutral "Two things are true as of about six minutes ago."

    gojo "One: you can see curses. That doesn't switch off. You will see them on trains and in supermarkets and outside your own front door for the rest of your life."

    gojo serious "Two: they can see {i}you.{/i} Cursed energy is food and you just started giving off a lot of it."

    mc serious "So what happens now."

    gojo @ happy "That's actually up to you, which is rarer than you'd think."

    gojo neutral "Option one. There's a school. Tokyo Metropolitan Curse Technical College — it's in Tokyo and it's in a mountain and both of those are true, and I'll explain that badly at some point."

    gojo "You'd learn to use what opened tonight. You'd be with people who can do it too. And you'd be a sorcerer, which is a job where the retirement plan is mostly theoretical."

    gojo serious "Option two. I make tonight go away."

    mc @ surprised "...Make it go away."

    gojo sad "You'd remember a power cut and an accident. You'd grieve properly, which matters. And you would never know any of this was real."

    menu:
        "He is not selling either one. He is standing in an alley at ten at night with his hands in his pockets, waiting."

        "\"Why is it my choice? You could just do it.\"":
            $ add_bond("gojo", 6)
            $ flag("gojo_asked_why")
            gojo neutral "I could, yes."
            gojo serious "I've done it. Dozens of times. It's the kindest thing we do and I hate it, and I've stopped being willing to do it to someone who saw it happen with their eyes open."
            gojo "You looked at the thing that killed your friend. Somebody who does that gets asked."

        "\"If I forget — does she still count?\"":
            $ add_bond("gojo", 8)
            $ flag("gojo_asked_sana")
            show gojo surprised
            "It is the first thing I have said that makes him stop moving."
            gojo "..."
            gojo sad "She counts either way. She counted before I got here."
            gojo "But you'd be the only person alive who knew what actually happened to her, and then you wouldn't be."
            gojo serious "I'm not going to pretend that's nothing. It isn't nothing."

        "\"What would you do?\"":
            $ add_bond("gojo", 5)
            $ flag("gojo_asked_advice")
            gojo happy "Oh, I'd go. Obviously I'd go, look at me."
            gojo neutral "But I was born into it and I've never once had to decide, so my answer's worth approximately nothing and you should weigh it accordingly."

    gojo @ happy "Take your time. I'm extremely patient about exactly one thing and this is it."

    "I take my time."

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

    ## Already on screen when chapter_one_b jumps here; set again so the scene
    ## also stands on its own as a memory.
    scene bg alley
    show gojo neutral at pos_c

    mc serious "I'll go."

    gojo serious "Okay."

    gojo neutral "Then go home first. Say it properly. Take the weekend. A car will be outside at seven on Sunday morning, and the paperwork is my problem, not yours."

    mc @ sad "What do I tell them?"

    gojo serious "The truth, if you want. They won't be able to hold onto the parts that matter — that's not me being cruel, it's just what happens near this."

    gojo sad "But you'll have said it. That's for you, not for them. Do it anyway."

    scene bg home_living with fade_slow
    show mother at pos_cl
    show father at pos_r
    with dissolve

    "I get home at eleven. My mother is still up, because the school rang, because somebody has already made a call I did not hear about."

    "She has been crying. She hugs me for a very long time and does not ask a single question about the alley."

    mother "They said it was the power cut. That she fell."

    "I could correct her. I watch myself not correct her, and file the feeling for later."

    menu:
        "My father is standing in the kitchen doorway with a tea he has not drunk."

        "Tell them the truth.":
            $ flag("told_parents_truth")
            $ gain("insight", 2)
            "I tell them all of it. The dark, the thing in the alley, the man in the blindfold, the school in a mountain."
            "They listen. They believe me — I can see them believing me."
            "And then, somewhere around the third sentence, it goes out of them like water out of a cupped hand, and my mother says {i}well, a scholarship, that's wonderful{/i} in a voice with nothing wrong in it at all."
            mcthink "He told me. He told me and I did it anyway."
            mcthink "Good. I'd rather have said it."

        "Tell them it's a scholarship.":
            $ flag("told_parents_lie")
            $ gain("control", 2)
            mc "There's a school. They came to me tonight — they'd been watching, apparently."
            "My father is so proud of me that I have to look at the floor."
            "It is a clean lie and it fits them perfectly and I understand, putting it on them, that I have just done to my parents exactly what Gojo offered to do to me."

        "Say almost nothing.":
            $ flag("told_parents_nothing")
            $ gain("control", 3)
            "I say I'm going away to school, and that it's a good one, and that it happened fast."
            "My mother makes me eat something. My father says {i}well{/i} four times over an hour."
            "Nobody in the house sleeps, and nobody says so."

    scene bg home_living with fade_slow
    show mother at pos_c
    with dissolve

    "On Friday morning my mother makes breakfast for four."

    "She lays the fourth place without thinking about it — a bowl, chopsticks, the small dish Sana always got because she liked it and said so once, three years ago, and was given it every time after."

    "Then she stops, with her hand still on the dish."

    mother "...Why did I—"

    "It lasts about a second and a half. I watch her look at the fourth place and not be able to get to the end of the thought, and then go smoothly, terribly around it."

    mother "Well. That's silly of me."

    "She clears it away. She is entirely cheerful about it."

    mcthink "It's not gone. It's underneath."

    mcthink "She just can't get at it."

    hide mother with dissolve

    scene bg home_bedroom_night with fade_slow

    "On Sunday I pack at two in the morning, in the dark, without turning the light on."

    menu:
        "There is room in the bag for one thing that isn't clothes."

        "The photo from the summer festival.":
            $ flag("took_photo")
            $ gain("insight", 1)
            "Three years old. Sana has her arm around my neck and is pulling me sideways out of frame, and I am laughing, and it is not a good photograph."

        "Her hachimaki.":
            $ flag("took_hachimaki")
            "She left it at mine after sports day, three weeks ago, and never asked for it back. Her name is inside the band in marker, in her handwriting."

        "My father's watch.":
            $ flag("took_watch")
            $ gain("control", 1)
            "It has been in the drawer since before I was born. He puts it in my hand at the door in the morning and says {i}for the exams,{/i} and he thinks there are going to be exams."

        "Nothing.":
            $ flag("took_nothing")
            $ gain("control", 2)
            "I take clothes. I have decided, without being able to explain it, that I do not want anything from this house touching the next one."

    scene bg street_morning with fade_slow

    "The car is black and completely unremarkable and there is a man in a suit beside it who apologises to my father for the hour."

    "My mother hugs me the correct amount. My father shakes my hand, which he has never done."

    "As the door closes my mother puts her hand flat against the window."

    "And for exactly one second it is the same face she had over the fourth place setting — something underneath, pushing, almost getting there."

    "Then it is gone, and she smiles, and waves."

    mcthink "There. Twice now."

    mcthink "She's still in there. They just filed over the top of her."

    scene bg car with fade_slow

    voice_ "Sorry — it's about ninety minutes."

    "For something to do, I decide to count the red lights we stop at."

    scene bg black with fade_slow

    $ story_point = "ch2_arrival"
    return


################################################################################
## The road not taken — this one ends
################################################################################

label ch1b_the_other_road:

    ## Already on screen when chapter_one_b jumps here; set again so the scene
    ## also stands on its own as a memory.
    scene bg alley
    show gojo neutral at pos_c

    mc sad "Take it away."

    gojo sad "...Okay."

    gojo neutral "For what it's worth, I think that's a reasonable thing to want and I'd have said yes to it at your age."

    "He puts two fingers against my forehead, almost gently."

    gojo @ sad "You won't remember this bit either. Sorry."

    scene bg black with fade_slow

    "There was a power cut on a Thursday in October, and my friend Sana Torii had an accident in the alley behind the arcade."

    "It was very sad. Everyone said so."

    scene bg town_street with fade_slow

    "Winter comes. I go back to school in January because that is what there is to do."

    "I am fine. Everyone tells me how well I am doing and I agree with them."

    "Occasionally, in a shop or on a platform, I look at a place where there is nothing, for slightly too long, and then I stop."

    scene bg home_living with fade_slow
    show mother at pos_c
    with dissolve

    "In March my mother is in the kitchen at about six in the evening, and I am upstairs, and the lights go out."

    "All of them. At once."

    scene bg black with Dissolve(0.5)

    "I come down in the dark, because that is what a person does."

    "I call out. She does not answer."

    "I cannot see anything. I have never been able to see anything. That is the arrangement I agreed to in an alley in October and then forgot agreeing to."

    "I find her at the bottom of the stairs."

    "Something opens in me, five months late, for the second time in my life — and this time there is nobody in the doorway with his hands in his pockets."

    scene bg black with flash_white

    "I can see it."

    "I can see it, and I have no idea what to do, and the thing in my chest goes off like a dropped glass — all of it, at once, in every direction, with no shape on it at all."

    "It takes about nine seconds."

    "They will say it was the gas."

    scene bg black with fade_slow
    $ renpy.pause(1.6)

    show screen chapter_card("AN ENDING", "The Quiet Option", "I was asked once, in an alley, and I said no.")
    with fade_slow
    $ renpy.pause(5.0)
    hide screen chapter_card
    with fade_slow

    "Some choices get made before anyone knows what they are choosing."

    "This was one, and it was offered fairly, and it was mine."

    $ renpy.pause(2.0)
    if _in_replay:
        $ renpy.end_replay()
    $ renpy.full_restart()

    return
