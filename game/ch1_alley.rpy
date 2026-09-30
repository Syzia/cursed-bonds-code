################################################################################
## Chapter One — The Lights
##
## Dinner, an alleyway, the thing Sana finally told me, and the second I held.
##
## WP9 (phase 1): told in first person, and split into called steps
## (PHASE1_DESIGN.md 5.2, D39). Each step is a memory and a resume point:
##   ch1_diner      the diner and the walk home
##   ch1_the_thing  the alley: the dark, what Sana tells me, Last Light, the fight
##   ch1_gojo       the man in the blindfold, and my name
## Each step sets story_point to its own name as it starts and to the next
## step's as it ends (see prologue_catch_up in script.rpy).
################################################################################

## Last Light: the instant the lights went out, held still. Everything on the
## master layer loses its colour; the lamp over the fire door (a screen, so the
## grey-out doesn't reach it) stays warm.
transform last_light_still:
    matrixcolor SaturationMatrix(1.0)
    linear 0.5 matrixcolor SaturationMatrix(0.08)

## Where the lamp over the fire door is on the alley picture (centre, in
## pixels at 1920x1080). The placeholder alley borrows the konbini picture,
## whose only lamp is the streetlight at the top right; move this when the
## real alley art lands.
define LAST_LIGHT_LAMP = (1718, 108)

transform last_light_lamp_in:
    alpha 0.0
    linear 0.6 alpha 1.0

screen last_light_lamp():
    zorder 5
    fixed at last_light_lamp_in:
        ## A wide warm spill, then the bulb.
        add Transform("images/fx/contact_shadow.png", xysize=(620, 620),
                      matrixcolor=ColorizeMatrix("#ff9a3c", "#ff9a3c"), blend="add", alpha=0.55):
            xcenter LAST_LIGHT_LAMP[0] ycenter LAST_LIGHT_LAMP[1]
        add Transform("images/fx/contact_shadow.png", xysize=(150, 150),
                      matrixcolor=ColorizeMatrix("#ffe2b0", "#ffe2b0"), blend="add", alpha=0.95):
            xcenter LAST_LIGHT_LAMP[0] ycenter LAST_LIGHT_LAMP[1]


label chapter_one:

    scene bg black with None

    show screen chapter_card("CHAPTER ONE", "The Lights", "Thursday. Nine-forty at night.")
    with fade_slow
    $ renpy.pause(2.8)
    hide screen chapter_card
    with fade_slow

    call ch1_diner

    call ch1_the_thing

    call ch1_gojo

    return


################################################################################
## The diner, and the walk home
################################################################################

label ch1_diner:

    $ story_point = "ch1_diner"

    scene bg diner with fade_slow
    show sana happy at pos_c
    with dissolve

    "Thursday. The counter place two streets from the station, which is not good, and which I have been coming to since I was fourteen because it is nine hundred yen and it is ours."

    sana "Okay. Okay. Ranking."

    mc "We did rankings last week."

    sana @ angry "We did {i}food{/i} rankings last week. This is different. This is teachers."

    "Sana Torii has been assembling this ranking, visibly, for several days. She has a system. The system has a flaw and she knows it and she is going to present it anyway."

    sana neutral "Bottom is Hasegawa, obviously—"

    mc @ happy "Obviously."

    sana @ angry "—because of the thing with the projector, which I'm still not over. Top is Oda-sensei, because she caught me eating in her lesson and instead of telling me off she just said {i}finish it properly, you'll get indigestion.{/i}"

    sana happy "That's leadership. I'd follow that woman into a war."

    menu:
        "She is entirely serious about this."

        "\"You've got Hasegawa too low.\"":
            $ flag("dinner_argued")
            mc "The projector thing wasn't his fault."
            sana surprised "It was {b}entirely{/b} his fault—"
            mc "The cable was already broken."
            sana angry "Then he should have {i}known{/i} the cable was broken. That's the job. That's literally the job."
            "We argue about a projector for eleven minutes. It is the best eleven minutes of the week and neither of us notices that at the time."

        "\"Where am I on the list?\"":
            $ flag("dinner_joked")
            sana neutral "You're not a teacher."
            mc "Put me on it anyway."
            sana "...Mid. Solid mid."
            mc @ surprised "{i}Mid.{/i}"
            sana sad "You'd be higher but you do the thing where you go quiet and I have to work out what's wrong. Teachers don't do that. Teachers just tell you."
            "She says it lightly, and it is not light, and we both let it go past."

        "Let her run.":
            $ flag("dinner_listened")
            $ gain("insight", 1)
            "I let her run, because she is good at this and because she has been having a long month and this is what she does instead of talking about it."
            "She gets through eleven teachers. Four of them she has clearly never been taught by."

    show sana happy
    "She orders a second bowl she does not finish and pushes it at me halfway through, which she has done every time for two years, and has never once acknowledged doing."

    sana @ surprised "Oh — hey. I've got a thing to tell you."

    mc "What thing?"

    sana neutral "A thing thing. A proper one."

    mc "So tell me."

    sana serious "Not in here, it's got a bad ceiling for it."

    "She points at the ceiling, and for a second she isn't joking. She looks at one corner of it the way people look at a wasp."

    "I look where she is pointing. It is a ceiling: a water stain, a strip light, a fan that has never worked."

    sana happy "I'll tell you on the way. Or — no. When we get to yours. It needs a doorstep."

    mc "It needs a doorstep."

    sana @ angry "Some things need a doorstep!"

    "She is delighted with herself. I pay, badly, in coins. She says she'll get it next time."

    scene bg town_street with fade_slow
    show sana neutral at pos_c
    with dissolve

    "Outside it is cold in the way October gets at about nine, and she walks with her hands pulled up into her sleeves and keeps not telling me the thing."

    sana happy "— and I'm not saying I'd {i}win{/i} a fight with a swan. I'm saying it wouldn't be as one-sided as everyone claims."

    mc @ serious "Tell me the thing."

    sana @ serious "Doorstep."

    mc "We're eleven minutes from the doorstep."

    sana happy "Then you've got eleven minutes to be patient, which, frankly, is a growth area for you."

    "She glances back over her shoulder, once, at nothing. Then she links her arm through mine as if that was all she turned round for."

    "I cut through the alley behind the arcade because it saves four minutes and because I always do."

    $ story_point = "ch1_the_thing"
    return


################################################################################
## The alley
################################################################################

label ch1_the_thing:

    $ story_point = "ch1_the_thing"

    scene bg alley
    show sana neutral at pos_c
    with Dissolve(1.0)

    "Then the lights go out."

    $ hide_side_images = True
    scene bg black with Dissolve(0.6)

    "Not one light. Every light — the vending machine, the lamp over the fire door, the windows of the flats above, the phone in Sana's hand."

    "All of them, at once, in the same instant."

    sana surprised "...Okay, that's a power cut. That's a power cut, right?"

    "Her voice is too high. She laughs, and it doesn't take."

    sana neutral "Hey — I'm going to tell you the thing now, actually. This feels like a doorstep."

    sana serious "Okay. The thing."

    sana "I've been seeing things. Not people. {i}Things.{/i} For about six weeks."

    sana "The one on the ceiling in there tonight. I pointed right at it, and you looked right at it, and you didn't see anything."

    sana sad "There's one on the platform every morning. By the third pillar. Everyone walks straight through where it is, and it just... lets them."

    sana "I've been drawing them in the back of my maths book. So I'd know I'm not making it up."

    sana "Because if I was making it up, I'd draw them different every time. And I don't."

    "I cannot see her face. I can hear that she has practised this, and that the practising did not help."

    mc @ happy "Is this a bit? This feels like a bit."

    sana "..."

    sana serious "There's one at the end of this alley."

    sana "It's been standing there since we turned in. I didn't say, in case saying it made it—"

    $ flag("sana_told_the_thing")
    $ flag("sana_sketchbook")

    "She stops."

    "There is no sound. That is the part my body notices before my mind does: a town makes a noise all the time, and this one has stopped."

    menu:
        "I cannot see my own hands."

        "\"Sana. Take my arm.\"":
            $ flag("reached_for_her")
            "I find her sleeve. She grips back, hard, and laughs the way people laugh when they want something to be funny."
            sana "This is so stupid. Why is my heart going like—"

        "\"Get behind me.\"":
            $ flag("stood_in_front")
            "I put myself between her and the far end of the alley, the end she said, because it is the only direction I have."
            sana "It's dark. I can't see it any more. I could see it a second ago and now I can't—"

        "Say nothing. Listen.":
            $ flag("listened_first")
            $ gain("insight", 2)
            "I listen, and I hear one thing: a soft, wet, unhurried sound, about nine metres away, that has not moved and is not breathing."

    "Something hits us both."

    "I do not see it arrive and I never see it leave. There is simply a moment where I am standing and a moment where I am twelve feet down the alley with the whole left side of my body ringing, and the two moments are not connected by anything."

    scene bg black with hpunch

    "Sana is screaming my name."

    "Then she is not."

    mcthink "She told me. Thirty seconds ago she told me, and I asked if it was a bit."

    "I get up because getting up is the only instruction my body has left. I cannot see her. I cannot see anything. I go toward where the sound stopped, with both hands out, and my hands find her."

    "They find most of her."

    mc sad "Sana—"

    mc "{b}Sana—{/b}"

    "She is warm and she is not moving and there is something else in the alley, standing over her, and I know it is there because I can feel the air it is displacing on my face."

    "I cannot see it."

    "I have never been able to see it. She could. For weeks she could, on her own, drawing them in the back of a maths book so she'd know she wasn't mad, and I asked if it was a bit. That, {i}that{/i}, is the thing my chest does not survive."

    scene bg black with flash_white

    "Something opens."

    "It is not a decision and it is not brave. It is the sound a rope makes when the last strand goes."

    "And the world — the whole world, the alley, the fire door, the shape standing over my friend — {b}arrives.{/b}"

    $ hide_side_images = False
    scene bg alley dark with flash_purple
    show curse big at pos_loom, pulse_in
    with dissolve

    "I can see it."

    "Four metres of it, filling the alley wall to wall, with too many joints and a mouth running around the side of a head that is not a head."

    "It has been standing there the entire time."

    mcthink "It was always there."

    mcthink "It was there while she was telling me about it."

    curse2 "Oh."

    curse2 "{b}Oh,{/b} you can {i}see{/i} me."

    curse2 "She could see me too. She kept looking right at me."

    curse2 "Two in one alley. That's new. That's {i}very{/i} new. Do that again."

    "And underneath the seeing — underneath the sick, total clarity of it — there is a second thing, newer, pressing outward from behind my sternum, and it has been there my whole life waiting to be given a direction."

    "It is going to take me in about a second and a half. I can feel the shape of what is inside me, and I know exactly what I want it to be."

    "I do not want to be faster. I do not want to be stronger. I want the second to {b}stop{/b}: the one where she was talking, the one where the lights went, the one that is arriving now."

    "And it does."

    show layer master at last_light_still
    show screen last_light_lamp

    "The alley holds. The colour goes out of it the way heat goes out of a cup."

    "Dust hangs in the air as if it has been pinned there. The thing above me is exactly, perfectly still, mid-reach, four feet away."

    "One light stays on: the lamp over the fire door, caught in the instant before it went out. Warm. The only warm thing left."

    "I have one second. I am standing inside it."

    "Nothing in me knows what to do with it yet. I spend it looking at Sana, because I cannot help it, and then the world starts again and I am still holding nothing."

    hide screen last_light_lamp
    show layer master
    with dissolve

    $ technique = "timestop"
    $ flag("last_light_woke")

    "It comes at me."

    call combat("alley_curse", None, False, "bg alley dark")

    hide curse big with dissolve

    "I do not win."

    "Nobody could have told me that in advance in a way I would have heard, so I find it out the long way: I put everything I have into it, again and again, and it is not a fight, it is a thing happening to me."

    "I am on the ground somewhere near the fire door with one arm not working when the alley fills with light."

    $ story_point = "ch1_gojo"
    return


################################################################################
## The man in the blindfold
################################################################################

label ch1_gojo:

    $ story_point = "ch1_gojo"
    $ hide_side_images = False

    scene bg alley with flash_white
    show gojo serious at pos_c, pulse_in
    with dissolve

    "There is a very tall man standing in the mouth of the alley with his hands in his pockets."

    "He is wearing a blindfold. He does not appear to be in a hurry."

    gojo neutral "Hm."

    "The curse does not get to finish turning around."

    "There is no noise and no flash and no gesture I could describe afterwards. It is there, and then there is a grey smear settling out of the air where it used to be, and the smear is already thinning."

    gojo serious "Special grade adjacent. In an {i}alley.{/i} Behind an arcade."

    gojo "That's not where those live. That's not where those go."

    show gojo sad
    "He crouches by Sana for a while. He is careful with her in a way that makes my throat close."

    "Then he sits back on his heels and does not say anything for long enough that I know."

    mc sad "Can you—"

    gojo "No."

    gojo "I'm sorry. I could have, forty seconds ago. Not now."

    "He says it plainly, without softening it, and I will be grateful for that later, and not for a long time."

    gojo serious "You saw it."

    gojo "Not at the end — at the start. You were looking at it before I got here, which means it opened while it was standing over her."

    gojo @ sad "That's the worst possible way for that to happen and it's also the reason you're alive."

    "He stands up. The blindfold turns toward me, and even through cloth I have the distinct sensation of being read cover to cover."

    gojo neutral "What's your name?"

    if not (_in_replay or smoke_autoplay):
        python:
            _n = renpy.input("Given name:", default="Kaito", length=16).strip()
            mc_name = _n if _n else "Kaito"
            _s = renpy.input("Family name:", default="Amagiri", length=16).strip()
            mc_surname = _s if _s else "Amagiri"

    mc serious "[mc_surname]. [mc_surname] [mc_name]."

    gojo @ happy "Satoru Gojo."

    gojo serious "[mc_name] — I need you to hear the next part while you're still numb, because it'll be harder in an hour."

    scene bg black with fade_slow

    $ story_point = "chapter_one_b"
    return
