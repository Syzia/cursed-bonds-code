################################################################################
## Chapter Two — The Strongest of Today
##
## The tour, the veil on the ridge, the principal, and three first-years.
## No second-years.
##
## WP9 (phase 1): first person, split into called steps (PHASE1_DESIGN.md
## 5.2, D39). Nothing is sealed in the storehouse any more: Sukuna's body sits
## inside the veil on the mountain ridge.
##   ch2_arrival      the car, the gate, the tour
##   ch2_the_veil     the strongest of today, and the veil on the ridge
##   ch2_yaga         why are you here?
##   ch2_first_years  three first-years, and the first night
################################################################################

label chapter_two:

    call prologue_catch_up("ch2_arrival")

    scene bg black with None
    show screen chapter_card("CHAPTER TWO", "The Strongest of Today", "Tokyo Metropolitan Curse Technical College.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    call ch2_arrival

    call ch2_the_veil

    call ch2_yaga

    call ch2_first_years

    return


################################################################################
## The car, the gate, the tour
################################################################################

label ch2_arrival:

    $ story_point = "ch2_arrival"

    scene bg car with fade_slow
    show ijichi neutral at pos_c
    with dissolve

    "The count reaches eleven red lights before the driver speaks again."

    ijichi surprised "Oh — sorry. I should have said. Kiyotaka Ijichi. Assistant manager. Transport, paperwork, veils and damage reports — mostly damage reports."

    ijichi neutral "Gojo-san will meet you at the gate. He's — well. He's the strongest. That isn't me being dramatic. It's on the paperwork."

    ijichi sad "I'm very sorry about your friend."

    "He says it to the windscreen first and then, at the correct moment, to me, having clearly decided in advance to say it, and it lands better than most of what the adults will say to me this week."

    scene bg gate with fade_slow
    show gojo happy at pos_c
    with dissolve

    "The gate is a torii older than the idea of Japan having a capital. Past it the ground opens out and keeps going for a hundred kilometres."

    gojo "Right! Tour."

    gojo neutral "I do this for everyone and I do it badly, so ask questions or you'll get nothing useful."

    scene bg courtyard with fade_slow
    show gojo neutral at pos_c
    with dissolve

    "He walks me through it at a pace that suggests he has somewhere else to be and no intention of going there."

    gojo "Classrooms. Nobody teaches in them. Training hall — bigger inside than the building, don't think about it."

    gojo @ happy "Dorms. Cafeteria. Infirmary, which you will get to know embarrassingly well."

    gojo "Storehouse is Yaga's, the ridge is for running up — the lower half — and the riverside is freezing and everyone swims in it anyway."

    menu:
        "He has not stopped moving since the gate."

        "\"How many sorcerers are there? Like, in total.\"":
            $ gain("insight", 2)
            $ flag("asked_numbers")
            gojo neutral "Properly trained, active, in Japan? Low hundreds."
            gojo "Special grades? Four."
            mc @ surprised "Four."
            gojo happy "Four. And one of them's me, and one of them doesn't work for anybody, and I'd rather not talk about the other two before lunch."

        "\"Why was it in an alley?\"":
            $ gain("insight", 3)
            $ flag("asked_why_alley")
            gojo serious "Mm. Yeah. That's the right question and I don't have a good answer."
            gojo "Something that size wants a place with a lot of feeling in it. A hospital, a school, somewhere a lot of people were frightened for a long time."
            gojo "Not a cut-through behind an arcade with a vending machine in it."
            gojo @ angry "Somebody filed that street as clear this year. I've asked to see who."
            $ flag("wakuri_seeded")

        "\"Are you the strongest?\"":
            $ gain("control", 2)
            $ flag("asked_strongest")
            "He does not answer immediately, which is the first time that has happened."
            gojo serious "Yes."
            gojo "Not in a fun way. In a load-bearing way. If I'm somewhere, that place is fine; if I'm not, it might not be."
            gojo @ happy "It's the least interesting true thing about me and it's the only one anyone remembers."

    $ story_point = "ch2_the_veil"
    return


################################################################################
## The veil on the ridge
################################################################################

label ch2_the_veil:

    $ story_point = "ch2_the_veil"

    scene bg courtyard
    show gojo neutral at pos_c

    "Then, near the top of the grounds, he stops walking and looks up."

    if not has_flag("asked_strongest"):
        mc "Are you the strongest?"
        mc "Ijichi-san said it in the car like it was a fact."
        gojo @ happy "It is a fact."

    gojo serious "I'm the strongest of today."

    mc @ surprised "...Of today."

    gojo "Of today."

    "He is still looking up, past the dorms and the trees, to where the mountain goes grey."

    gojo neutral "Come here. You're going to find out about this at some point and I'd rather it was from me and not from a rumour in the dorms."

    "He takes me up the running path as far as a rope strung between two posts, and stops there, and points."

    scene bg ridge_veil with fade_curse
    show gojo serious at pos_c
    with dissolve

    "Above us, where the ridge flattens out, the air is wrong."

    "It is a dome, dark and faintly violet, the size of a house, and the light that goes into it does not come back out."

    "Inside it, if I let my eyes do the new thing they do, there is a figure sitting cross-legged, like someone meditating."

    "It is dry, and brown, and very still, and the hands folded in its lap are missing their fingers."

    "I can feel it from here. It is like standing near an open freezer, except the cold is interested in me."

    gojo "That's the strongest in history."

    mc @ serious "...What is?"

    gojo "Him. Up there."

    gojo neutral "Titles aren't a compliment in this job, they're a filing category. There's one for the strongest currently alive and there's one for the strongest there has ever been, and those have never been the same person."

    gojo @ happy "I've got the first one. He has the second."

    mcthink "Has. Present tense."

    gojo serious "Ryomen Sukuna. King of Curses. Twenty fingers, and not one of them is up there with him."

    menu:
        "The veil ripples very slightly. There is no wind up there."

        "\"He's dead, though.\"":
            $ flag("asked_dead")
            $ gain("insight", 2)
            gojo serious "He's a corpse. That's not the same thing, and the difference is the entire reason this school keeps a veil up there day and night."
            gojo "Nine people take turns holding it, all year, in shifts. It's the single most expensive ongoing task in Japanese jujutsu and nobody outside this fence knows it exists."

        "\"Why is it here? Why not somewhere safer?\"":
            $ flag("asked_why_here")
            $ gain("control", 2)
            gojo neutral "Because I'm here."
            gojo "That's the whole security arrangement. There isn't a second layer. There's a veil, nine very tired people, and me."
            gojo @ happy "Which is fine right up until I'm in Sendai."

        "Say nothing.":
            $ gain("insight", 3)
            $ flag("watched_the_box")
            "I look at it for a long time. It has no eyes that I can find, and it does not move, and after a while I understand what is wrong with the shape of it."
            "…It is facing the school."
            gojo sad "...Yeah. It does that."
            gojo neutral "Don't take it personally. It's faced this way for as long as anyone's kept records. Most people just can't feel it."

    ## Already on screen in a new game. A save made at the old storehouse menu
    ## lands on this menu with the storehouse still up, so set the ridge again.
    scene bg ridge_veil
    show gojo neutral at pos_c

    gojo happy "Right! That's the tour."

    gojo serious "Don't go near it. Not the ridge path past the rope markers. Not on a dare, not on your own. That's not a rule, the rules are Yaga's. That's me asking."

    $ flag("saw_the_ridge_veil")

    $ story_point = "ch2_yaga"
    return


################################################################################
## Why are you here?
################################################################################

label ch2_yaga:

    $ story_point = "ch2_yaga"

    scene bg office with fade_slow
    show yaga serious at pos_c
    with dissolve

    "Masamichi Yaga does not stand up when I come in."

    yaga "Sit."

    yaga neutral "I have read what Gojo wrote about Thursday night. It was two sentences long and one of them was about a vending machine."

    yaga serious "So I'll ask you directly. Why do you want to be here?"

    menu:
        "It is not conversation. The assessment started before I sat down."

        "\"So it doesn't happen to anyone else.\"":
            $ flag("yaga_duty")
            $ add_bond("yaga", 5)
            yaga neutral "Hm."
            yaga serious "That is an honest answer and a dangerous one. 'So it doesn't happen again' is how sorcerers talk themselves into things they don't come back from."
            yaga neutral "Keep the honest part. We will work on the rest."

        "\"Because I couldn't do anything.\"":
            $ flag("yaga_anger")
            $ add_bond("yaga", 6)
            $ gain("output", 2)
            mc angry "She could see them. She'd been seeing them for weeks. I stood next to her in an alley and something took her apart three metres from me and I couldn't even see it."
            mc "I'm not here to be noble. I'm here because I was useless and I'd like to stop."
            yaga @ surprised "...Good."
            yaga serious "Anger is fuel. Fuel is fine. Fuel that doesn't know where it's going burns the house down."
            yaga "Remember that you told me this. I will hold you to it."

        "\"I don't know that I do want to be here.\"":
            $ flag("yaga_honest")
            $ add_bond("yaga", 8)
            $ gain("insight", 3)
            mc sad "I said yes in an alley minutes after watching my friend die. That's not a decision, that's a reflex."
            mc "I don't know what I want. I know I can't unsee it."
            show yaga surprised
            "Yaga looks at me for a long moment."
            yaga neutral "That is the best answer anyone has given me in four years."
            yaga serious "The ones who are certain on day one are the ones I have to watch."

    yaga neutral "You may leave. I mean that — there is a form, Ijichi has it, and you can be home by this evening."

    mc serious "And the seeing?"

    yaga serious "Permanent."

    mc "And the things that can smell me?"

    yaga "Also permanent."

    "He lets that sit."

    yaga neutral "So the form exists and I will sign it if you ask. You would simply be an untrained sorcerer living in a town instead of a trained one living here."

    mc @ sad "That's not a choice."

    yaga sad "No. It is a door, and I am obliged to show it to you, and I am not obliged to pretend it leads anywhere."

    yaga serious "Welcome to Tokyo Jujutsu High."

    $ flag("enrolled")

    $ story_point = "ch2_first_years"
    return


################################################################################
## Three first-years, and the first night
################################################################################

label ch2_first_years:

    $ story_point = "ch2_first_years"

    scene bg training with fade_slow
    show gojo happy at pos_fl
    show yuji happy at pos_l
    show nobara neutral at pos_c
    show megumi neutral at pos_r
    with dissolve

    gojo "Right — first-years. There are three of them and now there are four of you."

    "One of them is upside down."

    yuji "— no but {i}listen{/i}, if you got strong enough, at some point you could definitely punch a whale—"

    nobara angry "Why would you punch a whale."

    yuji @ surprised "I'm not saying I {i}would{/i}, I'm saying the {b}capability{/b}—"

    megumi serious "Please stop talking."

    "The pink-haired one drops out of his handstand, sees me, and lights up like a vending machine."

    yuji happy "Oh! You're the new one! Yuji Itadori, first year, hi—"

    megumi neutral "Fushiguro. Megumi Fushiguro."

    nobara happy "Nobara Kugisaki. Don't touch my nails and don't tell me to be careful."

    "They already know. I can tell in about four seconds: nobody asks how my week was."

    gojo neutral "Okay. I'm leaving. You four do something."

    megumi @ surprised "Do what?"

    gojo @ happy "{i}Something.{/i} I'm not doing it for you, that defeats the object."

    hide gojo with dissolve

    "He is gone between one step and the next."

    menu:
        "Three people I met ninety seconds ago, and an afternoon."

        "Ask them to show me what they can do.":
            $ flag("first_day_training")
            $ add_bond("yuji", 6)
            $ add_bond("megumi", 6)
            $ add_bond("nobara", 4)
            $ gain("output", 3)
            "So they show me."
            "Megumi puts two white dogs out of his own shadow and they are perfectly, ordinarily real, and one of them sniffs my knee."
            "Nobara drives a nail through a straw doll on the far wall and something in the rafters that I had not known was there comes apart."
            "Yuji punches the training post so hard that the sound arrives twice."
            yuji happy "Okay — your go!"
            mc @ serious "I stopped a second once. For one second. Badly."
            nobara surprised "...That's a lot, actually."
            megumi serious "That's a great deal, actually."

        "Ask what happened to them.":
            $ flag("first_day_asking")
            $ add_bond("yuji", 4)
            $ add_bond("megumi", 8)
            $ add_bond("nobara", 7)
            $ gain("insight", 4)
            mc @ serious "How did you three end up here?"
            show nobara happy
            "It is the wrong question and the right one. Nobara answers first, at volume, about a village with one bus a day."
            show megumi serious
            "Megumi answers second, in about eleven words, and I understand from the shape of them that there is a great deal underneath."
            show yuji sad
            "Yuji answers last, and much more slowly."
            yuji @ happy "Mine's a long one. Ask me again in a couple of weeks — I'll tell you properly. Promise."

        "Say I'd rather just sit down for a bit.":
            $ flag("first_day_quiet")
            $ add_bond("yuji", 8)
            $ add_bond("nobara", 5)
            $ gain("control", 3)
            mc @ sad "Honestly? I got here four hours ago and I haven't really slept since Thursday."
            "There is a pause."
            yuji sad "Oh. Yeah. Okay."
            "He sits down on the floor of the training hall. Then Nobara does. Then, after a moment of visible internal argument, so does Megumi."
            "Nobody makes me talk. Somebody produces snacks from somewhere. I sit on the floor of an enormous room with three strangers for about an hour and it is the first hour since the alley that has not been unbearable."
            nobara neutral "...Right. That's enough of that."
            nobara @ angry "Tomorrow you're doing something, though. I'm not running a hospice."

    scene bg your_room night with fade_slow

    "The room they give me is at the end of the first-year corridor, and by the time I see it properly it is dark."

    "My bag is on the floor, still packed."

    if has_flag("took_photo"):
        "I put the photograph on the desk, face up, where I will have to look at it."
    elif has_flag("took_hachimaki"):
        "I put the hachimaki in the drawer, and then take it out, and then put it on the desk."
    elif has_flag("took_watch"):
        "I put my father's watch on the desk. It is four minutes fast and I decide not to fix it."
    else:
        "There is nothing to put out. I had thought that would feel cleaner than it does."

    mcthink "Thursday I was at dinner."

    mcthink "It's Sunday."

    "Somewhere below, a door goes, and somebody laughs at something, and the building settles."

    "I sleep for eleven hours."

    scene bg black with fade_slow

    $ story_point = "arc_one_open"
    return
