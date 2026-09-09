################################################################################
## Chapter Four — Kawagoe Sun Mall, Closed 2019
################################################################################

label chapter_four:

    scene bg black
    with None

    show screen chapter_card("CHAPTER FOUR", "Kawagoe Sun Mall", "Closed 2019. Three missing.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    $ partner = closest_first_year()
    $ partner_name = CAST[partner]["short"]
    $ tname = TECHNIQUES[technique]["name"]

    scene bg city
    with fade_slow

    show ijichi at pos_fr
    with dissolve

    "The Sun Mall is four storeys of dead escalators in a town that built a bigger one two stations down."

    "Ijichi parks across the road and does not turn the engine off."

    ijichi "Veil's up. Nobody wanders in, nobody wanders out, and anything that happens in there stays a local weather event."

    ijichi "Registered grade three. Assistant Manager Ijichi's personal opinion, which is worth nothing and which I am giving you anyway: three people is a lot for a grade three."

    ijichi "If it goes wrong, you {i}leave{/i}. All four of you. That is not cowardice, that is the actual protocol, and I will personally file the report saying you followed it."

    hide ijichi
    with dissolve

    show yuji at pos_l
    show megumi at pos_cl
    show nobara at pos_cr
    show mc at pos_fr
    with dissolve

    megumi "Split. Two teams, two floors, meet on three."

    nobara "I'll take Itadori, he's got no sense of direction and I've got no patience for shouting."

    yuji "That's — that's actually fair."

    megumi "Then [mc_surname] goes with—"

    if partner == "yuji":
        yuji "Me."
        "It isn't a suggestion, and it isn't a favour. He says it the way you'd state a fact that was already on the paperwork."
        yuji "Sorry, Kugisaki. I'll shout less, I promise."
        nobara "You will not."
        nobara "{i}Fine.{/i} Fushiguro, you're with me. Try to be interesting."
        megumi "No."
    elif partner == "megumi":
        megumi "—me."
        "He says it before the sentence is finished, which for Megumi Fushiguro is practically shouting."
        nobara "Oh, {i}now{/i} he has opinions."
        megumi "They've been standing in a forest with me for three days. I know how they move."
        megumi "That's worth more than liking each other."
        yuji "That is the most Megumi sentence ever constructed."
    else:
        nobara "Change of plan. New kid's with me."
        yuji "Wait, I thought I—"
        nobara "You're with Fushiguro. You two can be silent and loud at each other, it'll be very healthy."
        nobara "I want somebody who doesn't argue with me in a stairwell."
        mc "I might argue with you in a stairwell."
        nobara "You might. But you'd do it fast."

    scene bg ruin
    with fade_curse

    hide yuji
    hide megumi
    hide nobara
    hide mc
    with None

    "Inside, the mall smells the way the East Wing smelled, and your whole body reports for duty before your brain has finished the comparison."

    "Sixty shopfronts with the shutters down. A children's ride, still plugged into something, turning very slowly."

    "And running through all of it, everywhere, like damp: cursed energy."

    if partner == "yuji":
        show yuji at pos_cr
    elif partner == "megumi":
        show megumi at pos_cr
    else:
        show nobara at pos_cr
    show mc at pos_l
    with dissolve

    if partner == "yuji":
        yuji "Okay, so, this is where you tell me you have a really useful technique for exactly this situation."
        mc "I have a technique that I have had for eleven days."
        yuji "Perfect. Love that. Let's go."
    elif partner == "megumi":
        megumi "Don't use your technique yet."
        mc "Why not?"
        megumi "Because it's watching, and I want it to think there are two ordinary students in here for as long as possible."
    else:
        nobara "It's diffuse. That's bad."
        mc "Bad how?"
        nobara "Diffuse means big. Or it means clever."
        nobara "I'd genuinely rather it was big."

    "You work the second floor shop by shop."

    menu:
        "The residue thickens toward the west end. There's a service corridor, and there is something written on the wall beside it in something that is not paint."

        "Read the writing.":
            $ flag("read_wall")
            $ add_ce(2)
            "It says {b}I WAS ONLY HERE FOR THE PHOTOS{/b}, four times, in handwriting that gets smaller each time."
            "The fourth one is about the size of a fingernail."
            if partner == "yuji":
                yuji "..."
                yuji "One of the explorers. That's one of the explorers."
                yuji "They were writing it while it was happening."
            elif partner == "megumi":
                megumi "It kept them alive long enough to write it four times."
                megumi "That's not a grade three. Grade threes don't {i}keep{/i} things."
            else:
                nobara "It made them repeat it."
                nobara "It liked hearing it. Great. It's one of the ones with a personality."

        "Ignore it. Keep moving.":
            $ flag("ignored_wall")
            "You do not look at the wall. You have decided, very deliberately, that you will look at the wall on the way out, if there is a way out."
            "It is the first cold decision you have ever made and you file the feeling away for later examination."

        "Use [tname] on the corridor.":
            $ flag("scouted_corridor")
            $ add_ce(4)
            if technique == "filament":
                "You feed threads down the service corridor, a metre at a time, reading the air."
                "Forty metres in they stop coming back."
                mcthink "Not cut. {i}Absorbed.{/i}"
            elif technique == "emberfall":
                "You touch the corridor wall and leave a slow warm mark in it, a beacon you'll be able to find in the dark from anywhere in the building."
                "Ninety seconds later you feel the heat move, because something has torn that section of wall down and carried it somewhere else."
            else:
                "You let the corridor replay."
                "A man running. A woman behind him, slower, shouting a name. A security guard, three weeks earlier, walking the same route with a torch, whistling."
                "And under all of it, on every layer, going back further than the building should be able to remember: something breathing in four-four time."

    "The corridor lets out into the atrium, and the atrium is where it has been keeping them."

    show curse big at pos_loom, pulse_in
    with fade_curse

    "It is not a grade three."

    "It is four metres of accumulated something, hung in the dead escalator well like a wasp nest, and it has faces on it. Some of them are recent."

    curse2 "{i}Oh good.{/i}"

    curse2 "Small ones. Fresh ones."

    curse2 "The last three were so {b}tired{/b} by the end."

    if partner == "yuji":
        yuji "{b}Hey!{/b}"
        "Itadori steps forward — not back, forward, all the way into its attention on purpose."
        yuji "Yeah, look at me. Big ugly. Look at me instead."
        mcthink "He's taking the first hit so I don't have to. He decided that before we walked in."
    elif partner == "megumi":
        megumi "Don't run."
        megumi "It's built for chasing. Everything about it is built for chasing."
        "His shadow is already deepening under him."
        megumi "Call Kugisaki. Now. Then get behind me for eight seconds."
    else:
        nobara "{i}Nope.{/i}"
        "She has a hammer out and four nails between her fingers before you have finished being afraid."
        nobara "Grade two. Minimum. Gojo-sensei is going to hear about this from me personally."

    "Somewhere below you, one storey down, you hear the other two start running."

    "And then you see her."

    "Third floor railing, above and behind the thing: a woman, maybe twenty-five, wedged in the gap where the escalator meets the balcony, alive, and absolutely silent because she has learned that noise is what it comes for."

    mcthink "Three missing. Two explorers, one guard."

    mcthink "Three missing, and one of them is still here."

    menu:
        "It hasn't noticed her. It has noticed you. You have perhaps four seconds to choose what this fight is about."

        "Go for her. Let it come after me.":
            $ flag("saved_civilian")
            $ add_bond("yuji", 8)
            $ add_bond("nobara", 5)
            jump ch4_save_first

        "Kill it first. She's safest if it's dead.":
            $ flag("fought_first")
            $ add_bond("megumi", 8)
            $ add_bond("maki", 4)
            jump ch4_fight_first


label ch4_save_first:

    "You move for the stairs and you make absolutely no attempt to be quiet about it."

    "Its attention comes off the atrium and onto you like a spotlight, which is the entire point, and which is also the worst thing you have ever voluntarily arranged."

    if partner == "yuji":
        yuji "{b}GO!{/b} I've got it! I've — okay I don't have it, but I've got its {i}face{/i}—"
    elif partner == "megumi":
        megumi "Idiot—"
        "Two dogs come out of the floor at a dead sprint before he's finished the word."
        megumi "Fine. {i}Fine.{/i} Eight seconds. I said eight seconds."
    else:
        nobara "You absolute — {b}fine!{/b} Fine, we're doing it your way!"
        "Four nails go into its mass in a line and she is already reaching for more."

    "You reach the railing. The woman looks at you with an expression you will still be able to draw in ten years."

    voice_ "Is it — did you — is it gone?"

    mc "No. Can you walk?"

    voice_ "I don't know. I've been here since Thursday."

    "It is Sunday."

    $ add_ce(3)

    if technique == "filament":
        "You anchor a dozen threads to the balcony above and a dozen to the ground floor, and you make a line, and you put her on it."
        "It is not elegant. She goes down the atrium in a controlled fall with your cursed energy screaming through your forearms, and she lands, and she is nineteen metres from the thing and moving."
    elif technique == "emberfall":
        "You put your palm flat on the escalator housing and pour everything you have into it, and the metal goes from cold to searing in four seconds."
        "The curse puts a limb on it to climb and recoils, and while it is dealing with a staircase that is now hostile, you get her over the rail and down."
    else:
        "The last hour of this atrium is still playing. You know exactly which route the thing took to reach the escalator well, three times, because it took the same one every time."
        "You take the other one. You take the one it never uses, and you take her down it, and it does not think to look there."

    "You put her behind a shuttered pharmacy on the ground floor and you tell her not to move and she says {i}I wasn't planning to{/i} with something that is almost a laugh, and that almost-laugh is going to keep you upright for the next four minutes."

    jump ch4_climax


label ch4_fight_first:

    "You do not go for her. You go for it."

    mcthink "If it's dead, she's safe. If I'm halfway up a staircase carrying somebody when it turns around, we both die."

    mcthink "It's the right call. It's the right call and I hate it."

    $ add_ce(5)

    if partner == "yuji":
        yuji "{b}Together!{/b}"
        "You have never fought alongside anyone. It turns out that Yuji Itadori makes it very easy, because Yuji Itadori simply assumes you will be where he needs you and then behaves as though you already are."
    elif partner == "megumi":
        megumi "Left side. Don't improvise."
        "You take the left side. You do not improvise. It is the single most useful thing anyone has ever told you."
    else:
        nobara "Its weight's all in the top. Break the bottom, the top comes to us!"
        nobara "And when it does — {b}you owe me a coat.{/b}"

    "You hit it eleven times in ninety seconds and it barely notices nine of them."

    "The other two, it notices."

    if technique == "filament":
        "Threads find the seam where the accumulated mass is thinnest, and you pull, and something inside it comes apart with a sound like a rope bridge."
    elif technique == "emberfall":
        "You leave three burns in it, deep, and they do not go out, and it starts trying to tear its own mass off to get away from them."
    else:
        "You have watched it swing forty times in the last four seconds. You know which shoulder drops. You put everything you have into the space it is about to be."

    "It screams, and the whole building takes it personally, and on the third floor the woman wedged in the escalator gap makes a small sound."

    "And it hears her."

    curse2 "{i}Ohhh.{/i}"

    curse2 "I'd forgotten about {b}you.{/b}"

    mcthink "No—"

    jump ch4_climax


label ch4_climax:

    scene bg veil
    with flash_purple

    "It comes apart and reassembles closer, and the atrium goes dark in a way that has nothing to do with the light."

    "This is the part nobody can teach you. This is the second and a half."

    if tech_stat() >= 40:
        $ flag("climax_strong")
        "And you already know where everyone is."
        "Maki made you name three exits in every room for a week. You named them on the way in without noticing you were doing it."
        "You know where the woman is. You know where your partner is. You know where the stairwell is and how many strides, and you have four hundred repetitions of one bad punch in your arms, and eleven days ago you were a high school student who was frightened of a corridor."
        mcthink "I don't have to win."
        mcthink "I have to hold it for eight seconds."
    else:
        $ flag("climax_thin")
        "And you are running on almost nothing."
        "Your cursed energy is a coin at the bottom of a well. Your arms have stopped taking instructions. There is a very reasonable voice in your head suggesting that you have already done more than anyone asked."
        mcthink "Eight seconds."
        mcthink "I have got maybe four."

    if partner == "yuji":
        yuji "[mc_name]!"
        yuji "{b}I'm here! I'm right here!{/b}"
        "He is. He has been the whole time. He puts himself between the thing and the stairwell and takes a hit meant for you and gets up so fast it looks like a rewind."
    elif partner == "megumi":
        megumi "Nue."
        "Something enormous comes out of his shadow and hits the atrium ceiling and the air goes white."
        megumi "Now. While it's blind. {i}Now{/i}, [mc_surname]."
    else:
        nobara "{b}RESONANCE!{/b}"
        "She drives a nail through a scrap of the thing she took off it two minutes ago, and every single part of it, everywhere in the building, breaks at once."

    "You step in."

    if technique == "filament":
        "Every thread you have, all of them, into one place — the knot at the centre where all the faces are pointing."
        "You have spent eleven days learning the difference between reaching and aiming."
        "You aim."
    elif technique == "emberfall":
        "You get one hand on the centre of it and you stop holding anything back."
        "Everything you have, all at once, into a fire that will not go out and does not need you to stay and watch it."
    else:
        "The last four seconds of the atrium play, and play, and play, and you know exactly where it is going to be."
        "You are already there."

    scene bg black
    with flash_white

    "And then Yuji and Nobara and Megumi are all in the atrium at once, and it is over in a way that is much louder and much faster than anything you did, and the four of you are standing in a dead shopping centre covered in something that is already evaporating."

    scene bg ruin
    with fade_slow

    show yuji at pos_l
    show megumi at pos_cl
    show nobara at pos_cr
    show mc at pos_fr
    with dissolve

    if has_flag("saved_civilian"):
        nobara "The woman's alive. Behind the pharmacy. She's asking for her phone, which I'm choosing to read as a good sign."
        megumi "That was a stupid call."
        megumi "..."
        megumi "It was also the right one. Both of those are true. Get used to that."
        $ add_bond("megumi", 4)
    else:
        nobara "She's alive."
        "There is a pause with a shape to it."
        nobara "She was in the gap for four days and she's got a broken wrist and she is {i}alive{/i}, so before you start, don't."
        yuji "I wasn't going to say anything."
        nobara "You were {b}thinking{/b} at me. I could hear it."
        megumi "You made a call with four seconds and bad information."
        megumi "That's the job. That's actually the whole job. Anyone who tells you they'd have found a third option in four seconds is lying to make you feel worse."
        $ add_bond("megumi", 6)
        $ flag("hard_lesson")

    yuji "Hey. [mc_name]."

    yuji "You did good."

    mc "I nearly—"

    yuji "Yeah. Everyone nearly."

    yuji "You did good."

    scene bg black
    with fade_slow

    return
