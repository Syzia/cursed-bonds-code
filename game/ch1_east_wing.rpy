################################################################################
## Chapter One — The East Wing
################################################################################

label chapter_one:

    scene bg black
    with None

    show screen chapter_card("CHAPTER ONE", "The East Wing", "October. The night before the festival.")
    with fade_slow
    $ renpy.pause(2.8)
    hide screen chapter_card
    with fade_slow

    scene bg ruin
    with fade_slow

    "Everyone knows the smell of a building that has been closed too long. Dust, old varnish, rain that got in somewhere and never left."

    "This is not that."

    "This is sweet. Sweet the way meat goes sweet on the third day."

    mcthink "Breathe through your mouth. Don't think about it."

    "The East Wing of Yotsuka High School was condemned in March. It comes down in November. Until then, it is a corridor of taped-off doors and a smell nobody will put in writing."

    "You are here because Sana Torii went in forty minutes ago on a dare, and has not come out."

    "You are here because you were the only one who said {i}we should go get her{/i} instead of laughing."

    menu:
        "Everyone else is still out on the field, arguing about whether it's a prank."

        "Go in. Now, before you talk yourself out of it.":
            $ flag("brave_entry")
            "You duck under the tape before your legs can file a complaint."
            "The corridor swallows the sound of the festival behind you like a hand over a mouth."

        "Shout for her from the doorway first.":
            $ flag("careful_entry")
            mc "Sana! Sana, it's not funny anymore!"
            "Your voice goes down the corridor and does not come back. Not an echo. Not even the shape of one."
            mcthink "That's — corridors echo. Corridors always echo."
            "You go in anyway."

        "Take a photo of the corridor first. Proof, in case.":
            $ flag("evidence_entry")
            "You lift your phone. The screen shows the corridor, empty, ordinary, grainy in the dark."
            "Then it shows something standing halfway down it that your eyes insist is not there."
            "You lower the phone. The corridor is empty again."
            mcthink "Okay. Okay. That's a smudge on the lens. That is definitely a smudge on the lens."
            "You go in anyway."

    "Twenty paces in, the temperature drops. Not gradually. Like walking through a doorway into a different month."

    "Forty paces in, you find Sana's shoe."

    "Sixty paces in, you find Sana."

    show curse small at pos_loom_r, pulse_in
    with fade_curse

    "She is against the far wall, and she is breathing, and something has its hand on her chest the way you'd hold a book open."

    "It is the colour of pond scum. It has too many joints in each arm and a mouth that goes around the side of its head, and it is looking at you with an expression you recognise, which is the worst part."

    "It looks {i}delighted{/i}."

    curse "Ooh. Two."

    curse "Two is a good night. Two is a very good night."

    mcthink "It talks. Why does it talk. Nothing about this needs to talk."

    "Your legs have made a decision without consulting you. They are not running."

    menu:
        "It hasn't moved yet. It's enjoying this."

        "Get between it and Sana.":
            $ flag("shield_first")
            $ add_ce(3)
            "You move before you can price the decision."
            "Three steps, and you are standing in the space between a thing that should not exist and a girl who sat behind you in maths for two years."
            curse "Braaave. Brave ones taste like copper."

        "Grab the fire extinguisher off the wall.":
            $ flag("weapon_first")
            "You rip it off its bracket. It's heavier than it looks and it is the only object in this corridor that makes sense."
            curse "Oh, a {i}tool.{/i} Use the tool. I love it when they use the tool."

        "Keep it talking. Buy Sana time.":
            $ flag("talk_first")
            $ add_ce(2)
            mc "What are you?"
            curse "What are {i}you?{/i} You can see me. They mostly can't see me."
            curse "Do you know how {b}lonely{/b} that is?"

    "It moves."

    show curse small at pos_loom_r, shake
    with hpunch

    "There is no wind-up. One instant it is at the far wall and the next it is close enough that you can see the dust it has displaced hanging in the air where it used to be."

    "Its hand closes on your shoulder and something inside you — something you have carried your whole life without ever once being asked to name it — {b}wakes up{/b}."

    scene bg black
    with flash_white

    "It is the feeling of a word arriving right before you say it."

    "It is under your sternum and behind your eyes and it has been there since you were born, and it has never had anywhere to go."

    "Now it has somewhere to go."

    mcthink "{b}What is this—{/b}"

    "It pours out of you the only way it knows how. Your way. The shape it was always going to take."

    menu:
        "Choose how your cursed energy manifests. This is your innate technique, and it is permanent."

        "Threads. Thin, invisible, everywhere at once. — {b}Filament{/b}":
            $ technique = "filament"
            scene bg ruin
            with flash_purple
            "The air fills with lines."
            "Hundreds of them, finer than spider silk, running from your fingertips to every surface in the corridor — and every one of them is {i}reporting back.{/i}"
            "You know where the walls are. You know where Sana's heartbeat is. You know, with sick precision, exactly where the thing's joints bend."
            "You close your fist and the threads go taut, and the curse's arm comes off at the third elbow like a thread cutting cheese."

        "Heat. Slow, patient, refusing to go out. — {b}Emberfall{/b}":
            $ technique = "emberfall"
            scene bg ruin
            with flash_purple
            "Your hand is not on fire. That would be simpler."
            "Instead everything you touch begins, quietly, to {i}keep burning.{/i} Not flame — a heat that has decided to stay."
            "You hit the curse in the ribs, badly, an ugly amateur's punch."
            "It laughs. Then it stops laughing, because the place you hit it is still getting hotter, and it will still be getting hotter in a minute, and in five."

        "Sound. Every second this room has already lived. — {b}Aftersound{/b}":
            $ technique = "aftersound"
            scene bg ruin
            with flash_purple
            "The corridor plays itself back to you."
            "Sana running. Sana stopping. The thing unfolding out of a locker that has been welded shut since March. Forty minutes, all at once, laid over the present like tracing paper."
            "And in all of it, one repeated shape: every time it strikes, it turns its head a fraction to the left first."
            "You have never fought anything in your life. But you have watched this thing fight thirty times in the last four seconds."
            "You step left. It hits the wall."

    $ add_ce(8)

    show curse small at pos_loom_r
    with dissolve

    curse "{b}No—{/b}"

    curse "no no no you're not — you weren't — you were {i}empty{/i} when you came in—"

    mcthink "I have no idea what I'm doing."

    mcthink "I have never been more certain of anything."

    "You put everything you have into one more push. It's clumsy. It's wasteful. It works for exactly as long as it needs to."

    "The curse recoils, screaming out of a mouth on the wrong side of its face, and gathers itself, and you understand with total clarity that you have spent everything and it has spent nothing."

    mcthink "That's it. That's all of it. I don't have any more."

    "It comes at you."

    "And then it doesn't."

    hide curse small
    with flash_white

    show gojo at pos_c, pulse_in
    with dissolve

    "There is a man standing in the corridor who was not standing in the corridor."

    "He is very tall, and he is wearing a blindfold, and he has his hands in his pockets, and the curse is — "

    "The curse is a smear of dissipating grey at his feet, and you did not see him move, and you are not sure he did."

    gojo "Hm."

    gojo "Grade three. Sloppy little thing. It shouldn't have been here."

    gojo "Neither should you, honestly, but you're much more interesting."

    "He crouches, unhurried, and looks at Sana. Something invisible passes over her and her breathing evens out."

    gojo "She'll be fine. Won't remember a thing. That's usually kinder."

    "He straightens up and turns that blindfold toward you, and even through the cloth you have the distinct sensation of being read cover to cover."

    gojo "You, though. You did something."

    gojo "You did something with no training, no teacher, and no idea it was there until about ninety seconds ago."

    gojo "That's rare. That's {i}genuinely{/i} rare, and I don't say that a lot, because I'm usually the rare one in the room."

    gojo "So. Question."

    gojo "What's your name?"

    python:
        _n = renpy.input("Given name:", default="Kaito", length=16).strip()
        mc_name = _n if _n else "Kaito"
        _s = renpy.input("Family name:", default="Amagiri", length=16).strip()
        mc_surname = _s if _s else "Amagiri"

    mc "[mc_surname]. [mc_surname] [mc_name]."

    gojo "[mc_name]! Great. I'm Satoru Gojo. I teach."

    mc "You teach."

    gojo "I teach {i}this.{/i}"

    "He gestures at the corridor, the smear on the floor, the girl breathing quietly against the wall, the impossible thing that just happened inside your own chest."

    gojo "There's a school. It's in Tokyo, it's in a mountain, and both of those are true at once, which I'll explain later or possibly never."

    gojo "You'd be a first-year. You'd be behind. You'd also be alive next year, which — statistically — you will not be otherwise."

    gojo "Because here's the thing about what just woke up in you, [mc_name]."

    gojo "Curses eat people with cursed energy first. You've been invisible your whole life. As of about four minutes ago, you're a beacon."

    menu:
        "He waits. He is in absolutely no hurry."

        "\"Is that a threat?\"":
            $ add_bond("gojo", 6)
            $ flag("gojo_challenged")
            gojo "Ha!"
            gojo "No. Threats are for people I want something from."
            gojo "That was a weather report. You're standing in it either way. I'm just the guy offering the umbrella."
            gojo "I like that you asked, though. Most people just say yes to the tall man in the blindfold."

        "\"What happens if I say no?\"":
            $ add_bond("gojo", 3)
            $ flag("gojo_hesitant")
            gojo "Then someone comes and softens the last hour for you, and you go home, and you have a strange dream about a corridor."
            gojo "And in about six weeks something finds you at a bus stop."
            gojo "I'd rather that didn't happen. But I've stopped pretending that's a reason for other people."

        "\"Yes.\" — no hesitation.":
            $ add_bond("gojo", 5)
            $ add_ce(4)
            $ flag("gojo_immediate")
            gojo "...Huh."
            gojo "That was fast."
            mc "Something was going to kill Sana and I couldn't do anything about it. Now I can."
            mc "Why would I want the version of me that couldn't?"
            gojo "{i}Huh.{/i}"
            gojo "Okay. Yeah. You'll do."

    scene bg black
    with fade_slow

    return
