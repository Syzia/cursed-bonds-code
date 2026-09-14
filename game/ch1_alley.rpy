################################################################################
## Chapter One — The Lights
##
## Dinner, an alleyway, and the thing you could not see until it was too late.
################################################################################

label chapter_one:

    scene bg black with None

    show screen chapter_card("CHAPTER ONE", "The Lights", "Thursday. Nine-forty at night.")
    with fade_slow
    $ renpy.pause(2.8)
    hide screen chapter_card
    with fade_slow

    scene bg diner with fade_slow
    show sana at pos_cr
    show mc at pos_l
    with dissolve

    "Thursday. The counter place two streets from the station, which is not good, and which you have been coming to since you were fourteen because it is nine hundred yen and it is yours."

    sana "Okay. Okay. Ranking."

    mc "We did rankings last week."

    sana "We did {i}food{/i} rankings last week. This is different. This is teachers."

    "Sana Torii has been assembling this ranking, visibly, for several days. She has a system. The system has a flaw and she knows it and she is going to present it anyway."

    sana "Bottom is Hasegawa, obviously—"

    mc "Obviously."

    sana "—because of the thing with the projector, which I'm still not over. Top is Oda-sensei, because she caught me eating in her lesson and instead of telling me off she just said {i}finish it properly, you'll get indigestion.{/i}"

    sana "That's leadership. I'd follow that woman into a war."

    menu:
        "She is entirely serious about this."

        "\"You've got Hasegawa too low.\"":
            $ flag("dinner_argued")
            mc "The projector thing wasn't his fault."
            sana "It was {b}entirely{/b} his fault—"
            mc "The cable was already broken."
            sana "Then he should have {i}known{/i} the cable was broken. That's the job. That's literally the job."
            "You argue about a projector for eleven minutes. It is the best eleven minutes of the week and neither of you notices that at the time."

        "\"Where am I on the list?\"":
            $ flag("dinner_joked")
            sana "You're not a teacher."
            mc "Put me on it anyway."
            sana "...Mid. Solid mid."
            mc "{i}Mid?{/i}"
            sana "You'd be higher but you do the thing where you go quiet and I have to work out what's wrong. Teachers don't do that. Teachers just tell you."
            "She says it lightly, and it is not light, and you both let it go past."

        "Let her run.":
            $ flag("dinner_listened")
            $ gain("insight", 1)
            "You let her run, because she is good at this and because she has been having a long month and this is what she does instead of talking about it."
            "She gets through eleven teachers. Four of them she has clearly never been taught by."

    "She orders a second bowl she does not finish and pushes it at you halfway through, which she has done every time for two years, and has never once acknowledged doing."

    sana "Oh — hey. I've got a thing to tell you."

    mc "What thing?"

    sana "A thing thing. A proper one."

    mc "So tell me."

    sana "Not in here, it's got a bad ceiling for it."

    "She points at the ceiling. The ceiling is a ceiling."

    sana "I'll tell you on the way. Or — no. When we get to yours. It needs a doorstep."

    mc "It needs a {i}doorstep.{/i}"

    sana "Some things need a doorstep!"

    "She is delighted with herself. You pay, badly, in coins. She says she'll get it next time."

    scene bg town_street with fade_slow

    "Outside it is cold in the way October gets at about nine, and she walks with her hands pulled up into her sleeves and keeps not telling you the thing."

    sana "— and I'm not saying I'd {i}win{/i} a fight with a swan. I'm saying it wouldn't be as one-sided as everyone claims."

    mc "Tell me the thing."

    sana "Doorstep."

    mc "We're eleven minutes from the doorstep."

    sana "Then you've got eleven minutes to be patient, which, frankly, is a growth area for you."

    "You cut through the alley behind the arcade because it saves four minutes and because you always do."

    scene bg konbini with Dissolve(1.0)

    "Then the lights go out."

    scene bg black with Dissolve(0.6)

    "Not one light. Every light — the vending machine, the security lamp over the fire door, the windows of the flats above, the phone in Sana's hand."

    "All of them, at once, in the same instant."

    sana "...Okay, that's a power cut. That's a power cut, right?"

    sana "Hey — I'm going to tell you the thing now, actually. This feels like a doorstep."

    "There is no sound. That is the part your body notices before your mind does: a town makes a noise all the time, and this one has stopped."

    menu:
        "You cannot see your own hands."

        "\"Sana. Take my arm.\"":
            $ flag("reached_for_her")
            "You find her sleeve. She grips back, hard, and laughs the way people laugh when they want something to be funny."
            sana "This is so stupid. Why is my heart going like—"

        "\"Get behind me.\"":
            $ flag("stood_in_front")
            "You put yourself between her and the dark end of the alley, which is a guess, because there is no reason to think the dark end is the one that matters."
            sana "Behind you from {i}what?{/i}"

        "Say nothing. Listen.":
            $ flag("listened_first")
            $ gain("insight", 2)
            "You listen, and you hear one thing: a soft, wet, unhurried sound, about nine metres away, that has not moved and is not breathing."

    "Something hits you both."

    "You do not see it arrive and you never see it leave. There is simply a moment where you are standing and a moment where you are twelve feet down the alley with the whole left side of your body ringing, and the two moments are not connected by anything."

    scene bg black with hpunch

    "Sana is screaming your name."

    "Then she is not."

    mcthink "She never told me the thing."

    "You get up because getting up is the only instruction your body has left. You cannot see her. You cannot see anything. You go toward where the sound stopped, with both hands out, and your hands find her."

    "They find most of her."

    mc "Sana—"

    mc "{b}Sana—{/b}"

    "She is warm and she is not moving and there is something else in the alley, standing over her, and you know it is there because you can feel the air it is displacing on your face."

    "You cannot see it."

    "You have never been able to see it, and neither could she, and neither could anyone, and that — {i}that{/i} — is the thing your chest does not survive."

    scene bg black with flash_white

    "Something opens."

    "It is not a decision and it is not brave. It is the sound a rope makes when the last strand goes."

    "And the world — the whole world, the alley, the fire door, the shape standing over your friend — {b}arrives.{/b}"

    scene bg konbini with flash_purple
    show curse big at pos_loom, pulse_in
    with dissolve

    "You can see it."

    "Four metres of it, filling the alley wall to wall, with too many joints and a mouth running around the side of a head that is not a head."

    "It has been standing there the entire time."

    mcthink "It was always there."

    mcthink "It was there while she was talking about the man at the next table."

    curse2 "Oh."

    curse2 "{b}Oh,{/b} you can {i}see{/i} me."

    curse2 "That's new. That's very new. Do that again."

    "And underneath the seeing — underneath the sick, total clarity of it — there is a second thing, newer, pressing outward from behind your sternum, and it has been there your whole life waiting to be given a direction."

    menu:
        "It is going to take you in about a second and a half. You can feel the shape of what is inside you. You get to decide what it becomes, and you get exactly this long."

        "{b}Make the second stop.{/b} — Stillness":
            $ technique = "timestop"
            "You do not want to be faster. You do not want to be stronger. You want the second to {b}stop{/b} — the one where she was talking, the one where the lights went, the one that is arriving now."
            "And it does."
            scene bg konbini with flash_white
            "The alley holds. Dust hangs in the air like it has been pinned there. The thing above you is exactly, perfectly still, mid-reach, four feet away."
            "You have one second. You are standing inside it."
            "Nothing in you knows what to do with it yet. You spend it looking at Sana, because you cannot help it, and then the world starts again and you are still holding nothing."

        "Threads. Everywhere at once. — Filament":
            $ technique = "filament"
            "It goes out of you as lines — hundreds, finer than hair, filling the alley and reporting back."
            "You know where the walls are. You know where its joints bend. You know, with sick precision, exactly how still Sana is."
            "You close your fist and something comes off it at the third elbow, and it does not appear to notice."

        "Heat. Slow, and staying. — Emberfall":
            $ technique = "emberfall"
            "Your hands are not on fire. Everything you touch simply begins, quietly, to keep burning."
            "You get one palm on it and it recoils — and the place you touched is still getting hotter, and will be in a minute, and in five."
            "It looks at the mark. Then it looks at you, with more interest than you wanted."

    $ tname = TECHNIQUES[technique]["name"]

    "It comes at you."

    call combat("alley_curse", None, False, "bg konbini")

    hide curse big with dissolve

    "You do not win."

    "Nobody could have told you that in advance in a way you would have heard, so you find it out the long way: you put everything you have into it, twice, and it is not a fight, it is a thing happening to you."

    "You are on the ground somewhere near the fire door with one arm not working when the alley fills with light."

    scene bg konbini with flash_white
    show gojo at pos_c, pulse_in
    with dissolve

    "There is a very tall man standing in the mouth of the alley with his hands in his pockets."

    "He is wearing a blindfold. He does not appear to be in a hurry."

    gojo "Hm."

    "The curse does not get to finish turning around."

    "There is no noise and no flash and no gesture you could describe afterwards. It is there, and then there is a grey smear settling out of the air where it used to be, and the smear is already thinning."

    gojo "Special grade adjacent. In an {i}alley.{/i} Behind an arcade."

    gojo "That's not where those live. That's not where those go."

    "He crouches by Sana for a while. He is careful with her in a way that makes your throat close."

    "Then he sits back on his heels and does not say anything for long enough that you know."

    mc "Can you—"

    gojo "No."

    gojo "I'm sorry. I could have, forty seconds ago. Not now."

    "He says it plainly, without softening it, and you will be grateful for that later and not for a long time."

    gojo "You saw it."

    gojo "Not at the end — at the start. You were looking at it before I got here, which means it opened while it was standing over her."

    gojo "That's the worst possible way for that to happen and it's also the reason you're alive."

    "He stands up. The blindfold turns toward you, and even through cloth you have the distinct sensation of being read cover to cover."

    gojo "What's your name?"

    python:
        _n = renpy.input("Given name:", default="Kaito", length=16).strip()
        mc_name = _n if _n else "Kaito"
        _s = renpy.input("Family name:", default="Amagiri", length=16).strip()
        mc_surname = _s if _s else "Amagiri"

    mc "[mc_surname]. [mc_surname] [mc_name]."

    gojo "Satoru Gojo."

    gojo "[mc_name] — I need you to hear the next part while you're still numb, because it'll be harder in an hour."

    scene bg black with fade_slow
    return
