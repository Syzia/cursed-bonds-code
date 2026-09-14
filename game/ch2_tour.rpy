################################################################################
## Chapter Two — The Strongest of Today
##
## The tour, the corpse, the principal, and three first-years. No second-years.
################################################################################

label chapter_two:

    scene bg black with None
    show screen chapter_card("CHAPTER TWO", "The Strongest of Today", "Tokyo Metropolitan Curse Technical College.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    scene bg car with fade_slow

    "The count reaches eleven before the driver speaks."

    ijichi "Kiyotaka Ijichi. Assistant manager. Transport, paperwork, veils and damage reports — mostly damage reports."

    ijichi "I'm very sorry about your friend."

    "He says it to the windscreen, at the correct moment, having clearly decided in advance to say it, and it lands better than most of what the adults will say to you this week."

    scene bg gate with fade_slow
    show gojo at pos_cr
    show mc at pos_l
    with dissolve

    "The gate is a torii older than the idea of Japan having a capital. Past it the ground opens out and keeps going for a hundred kilometres."

    gojo "Right! Tour."

    gojo "I do this for everyone and I do it badly, so ask questions or you'll get nothing useful."

    scene bg courtyard with fade_slow

    "He walks you through it at a pace that suggests he has somewhere else to be and no intention of going there."

    gojo "Classrooms. Nobody teaches in them. Training hall — bigger inside than the building, don't think about it."

    gojo "Dorms. Cafeteria. Infirmary, which you will get to know embarrassingly well."

    gojo "Storehouse is sealed, ridge is for running up, and the riverside is freezing and everyone swims in it anyway."

    menu:
        "He has not stopped moving since the gate."

        "\"How many sorcerers are there? Like, in total.\"":
            $ gain("insight", 2)
            $ flag("asked_numbers")
            gojo "Properly trained, active, in Japan? Low hundreds."
            gojo "Special grades? Four."
            mc "Four."
            gojo "Four. And one of them's me, and one of them doesn't work for anybody, and I'd rather not talk about the other two before lunch."

        "\"Why was it in an alley?\"":
            $ gain("insight", 3)
            $ flag("asked_why_alley")
            gojo "Mm. Yeah. That's the right question and I don't have a good answer."
            gojo "Something that size wants a place with a lot of feeling in it. A hospital, a school, somewhere a lot of people were frightened for a long time."
            gojo "Not a cut-through behind an arcade with a vending machine in it."
            gojo "Somebody filed that street as clear this year. I've asked to see who."
            $ flag("wakuri_seeded")

        "\"Are you the strongest?\"":
            $ gain("control", 2)
            $ flag("asked_strongest")
            "He does not answer immediately, which is the first time that has happened."
            gojo "Yes."
            gojo "Not in a fun way. In a load-bearing way. If I'm somewhere, that place is fine; if I'm not, it might not be."
            gojo "It's the least interesting true thing about me and it's the only one anyone remembers."

    "Then, near the far end of the grounds, he stops walking."

    "There is a building here that he did not name on the way past. It is low, and old, and the ground in front of it is wrong — nothing grows in a rough circle about twenty metres across."

    if not has_flag("asked_strongest"):
        mc "Are you the strongest?"
        mc "Everyone keeps saying it like it's a fact."
        gojo "It is a fact."

    gojo "I'm the strongest of today."

    mc "...Of today."

    gojo "Of today."

    "He looks at the low building for a while."

    gojo "Come here. You're going to find out about this at some point and I'd rather it was from me and not from a rumour in the dorms."

    scene bg storehouse with fade_curse

    "Inside it is one room, and the room is mostly floor, and in the middle of the floor there is a sealed casket the size of a person, bound in paper that has been replaced so many times the newest layer is glossy and the oldest is the colour of tea."

    "You can feel it from the door. It is like standing near an open freezer, except the cold is interested in you."

    gojo "That's the strongest in history."

    mc "...What is?"

    gojo "Him. In there."

    gojo "Titles aren't a compliment in this job, they're a filing category. There's one for the strongest currently alive and there's one for the strongest there has ever been, and those have never been the same person."

    gojo "I've got the first one. He has the second."

    mcthink "Has. Present tense."

    menu:
        "The paper on the casket is moving very slightly, and there is no wind in here."

        "\"He's dead, though.\"":
            $ flag("asked_dead")
            $ gain("insight", 2)
            gojo "He's a corpse. That's not the same thing, and the difference is the entire reason this building has a budget."
            gojo "Nine people re-seal that every year. It's the single most expensive ongoing task in Japanese jujutsu and nobody outside this fence knows it exists."

        "\"Why is it here? Why not somewhere safer?\"":
            $ flag("asked_why_here")
            $ gain("control", 2)
            gojo "Because I'm here."
            gojo "That's the whole security arrangement. There isn't a second layer. There's a box, and a lot of paper, and me."
            gojo "Which is fine right up until I'm in Sendai."

        "Say nothing.":
            $ gain("insight", 3)
            $ flag("watched_the_box")
            "You look at it and it is, unmistakably, looking back — not with eyes, and not in a way you could describe, but with the flat patient attention of something taking your measurement."
            gojo "...Yeah. It does that."
            gojo "Don't take it personally. It does it to everyone. It's just that most people can't feel it."

    gojo "Right! That's the tour."

    gojo "Do not come back in here on your own. That's not a rule, the rules are Yaga's. That's me asking."

    $ flag("saw_the_casket")

    scene bg office with fade_slow
    show yaga at pos_c
    with dissolve

    "Masamichi Yaga does not stand up when you come in."

    yaga "Sit."

    yaga "I have read what Gojo wrote about Thursday night. It was two sentences long and one of them was about a vending machine."

    yaga "So I'll ask you directly. Why do you want to be here?"

    menu:
        "It is not conversation. The assessment started before you sat down."

        "\"So it doesn't happen to anyone else.\"":
            $ flag("yaga_duty")
            $ add_bond("yaga", 5)
            yaga "Hm."
            yaga "That is an honest answer and a dangerous one. 'So it doesn't happen again' is how sorcerers talk themselves into things they don't come back from."
            yaga "Keep the honest part. We will work on the rest."

        "\"Because I couldn't do anything.\"":
            $ flag("yaga_anger")
            $ add_bond("yaga", 6)
            $ gain("output", 2)
            mc "I stood in an alley and something took her apart four feet away and I couldn't even see it."
            mc "I'm not here to be noble. I'm here because I was useless and I'd like to stop."
            yaga "...Good."
            yaga "Anger is fuel. Fuel is fine. Fuel that doesn't know where it's going burns the house down."
            yaga "Remember that you told me this. I will hold you to it."

        "\"I don't know that I do want to be here.\"":
            $ flag("yaga_honest")
            $ add_bond("yaga", 8)
            $ gain("insight", 3)
            mc "I said yes in an alley eight hours after watching my friend die. That's not a decision, that's a reflex."
            mc "I don't know what I want. I know I can't unsee it."
            "Yaga looks at you for a long moment."
            yaga "That is the best answer anyone has given me in four years."
            yaga "The ones who are certain on day one are the ones I have to watch."

    yaga "You may leave. I mean that — there is a form, Ijichi has it, and you can be home by this evening."

    mc "And the seeing?"

    yaga "Permanent."

    mc "And the things that can smell me?"

    yaga "Also permanent."

    "He lets that sit."

    yaga "So the form exists and I will sign it if you ask. You would simply be an untrained sorcerer living in a town instead of a trained one living here."

    mc "That's not a choice."

    yaga "No. It is a door, and I am obliged to show it to you, and I am not obliged to pretend it leads anywhere."

    yaga "Welcome to Tokyo Jujutsu High."

    $ flag("enrolled")

    scene bg training with fade_slow
    show gojo at pos_fl
    show yuji at pos_l
    show nobara at pos_cr
    show megumi at pos_r
    with dissolve

    gojo "Right — first-years. There are three of them and now there are four of you."

    "One of them is upside down."

    yuji "— no but {i}listen{/i}, if you got strong enough, at some point you could definitely punch a whale—"

    nobara "Why would you punch a whale."

    yuji "I'm not saying I {i}would{/i}, I'm saying the {b}capability{/b}—"

    megumi "Please stop talking."

    "The pink-haired one drops out of his handstand, sees you, and lights up like a vending machine."

    yuji "Oh! You're the new one! Yuji Itadori, first year, hi—"

    megumi "Fushiguro. Megumi Fushiguro."

    nobara "Nobara Kugisaki. Don't touch my nails and don't tell me to be careful."

    "They already know. You can tell in about four seconds: nobody asks how your week was."

    gojo "Okay. I'm leaving. You four do something."

    megumi "Do what?"

    gojo "{i}Something.{/i} I'm not doing it for you, that defeats the object."

    "He is gone between one step and the next."

    menu:
        "Three people you met ninety seconds ago, and an afternoon."

        "Ask them to show you what they can do.":
            $ flag("first_day_training")
            $ add_bond("yuji", 6)
            $ add_bond("megumi", 6)
            $ add_bond("nobara", 4)
            $ gain("output", 3)
            "So they show you."
            "Megumi puts two white dogs out of his own shadow and they are perfectly, ordinarily real, and one of them sniffs your knee."
            "Nobara drives a nail through a straw doll on the far wall and something in the rafters that you had not known was there comes apart."
            "Yuji punches the training post so hard that the sound arrives twice."
            yuji "Okay — your go!"
            mc "I stopped a second once. For one second. Badly."
            nobara "...That's a lot, actually."
            megumi "That's a great deal, actually."

        "Ask what happened to them.":
            $ flag("first_day_asking")
            $ add_bond("yuji", 4)
            $ add_bond("megumi", 8)
            $ add_bond("nobara", 7)
            $ gain("insight", 4)
            mc "How did you three end up here?"
            "It is the wrong question and the right one. Nobara answers first, at volume, about a village with one bus a day."
            "Megumi answers second, in about eleven words, and you understand from the shape of them that there is a great deal underneath."
            "Yuji answers last, and much more slowly."
            yuji "Mine's a long one. Ask me again in a couple of weeks — I'll tell you properly. Promise."

        "Say you'd rather just sit down for a bit.":
            $ flag("first_day_quiet")
            $ add_bond("yuji", 8)
            $ add_bond("nobara", 5)
            $ gain("control", 3)
            mc "Honestly? I got here four hours ago and I've been awake since Thursday."
            "There is a pause."
            yuji "Oh. Yeah. Okay."
            "He sits down on the floor of the training hall. Then Nobara does. Then, after a moment of visible internal argument, so does Megumi."
            "Nobody makes you talk. Somebody produces snacks from somewhere. You sit on the floor of an enormous room with three strangers for about an hour and it is the first hour since the alley that has not been unbearable."
            nobara "...Right. That's enough of that."
            nobara "Tomorrow you're doing something, though. I'm not running a hospice."

    scene bg dorm with fade_slow

    "Your room has a bed, a desk, and a window facing a mountain that is also Tokyo."

    "Your bag is on the floor, unpacked."

    if has_flag("took_photo"):
        "You put the photograph on the desk, face up, where you will have to look at it."
    elif has_flag("took_hachimaki"):
        "You put the hachimaki in the drawer, and then take it out, and then put it on the desk."
    elif has_flag("took_watch"):
        "You put your father's watch on the desk. It is four minutes fast and you decide not to fix it."
    else:
        "There is nothing to put out. You had thought that would feel cleaner than it does."

    mcthink "Thursday I was at dinner."

    mcthink "It's Sunday."

    "Somewhere below, a door goes, and somebody laughs at something, and the building settles."

    "You sleep for eleven hours."

    scene bg black with fade_slow
    return
