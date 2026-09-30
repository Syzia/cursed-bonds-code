################################################################################
## Cursed Bonds — the new mission scenes of phase 1 (PHASE1_DESIGN.md 5.3).
##
## WP3 owns this file. Every scene here is a placeholder, first person, and is
## played through the mission registry (sb_missions.rpy):
##   st_utahime_office  story step m_utahime (an ev(), below)
##   st_promotion_g3    promotion m_promo_g3 (start: Maki, training hall/dojo)
##   cm_ijichi_1        character mission "Ride-Along" (start: Ijichi, gate)
##   cm_maki_1          character mission "The Armory" (start: Maki)
## Rewards (merit, items, bond) are paid by the mission when it completes,
## not in the scene.
################################################################################

init python:

    ## Utahime's arrival finds you wherever you are, mornings to afternoons,
    ## the day after roll call at the earliest (m_utahime gates it).
    ev("st_utahime_office", kind="story", periods=["Morning", "Noon", "Afternoon"], priority=96)


################################################################################
## m_utahime · The Room Next Door
################################################################################

## The text is timeless: an old save may meet her weeks after roll call.
label st_utahime_office:
    ## PLACEHOLDER — rewrite in phase 3

    "Ijichi catches me between one thing and the next. Someone in the staff building has asked for \"the new first-year\", and he says it like an apology."

    scene bg utahime_office with fade_slow

    "There is a new nameplate beside Yaga's door, the ink on it barely dry. {i}Iori.{/i}"

    "The door is open. Inside, a woman in a white and red hakama is pinning job sheets to a board in rows so straight they look ruled."

    show utahime serious at pos_c
    with dissolve

    utahime "You're one of Tokyo's first-years. Come in. Don't touch the board."

    utahime "Utahime Iori. I teach at the Kyoto school."

    utahime "The Goodwill Event is ours to prepare this year, so I came ahead of my students. Someone has to see that it's done properly."

    mcthink "Nobody on this campus has said the word \"properly\" since I arrived."

    utahime "While I'm here, I've agreed to run Tokyo's board. Graded jobs. Real ones, with real curses at the end of them."

    utahime "There are three rules. I'll say them once."

    utahime "One. You take jobs at your own grade."

    utahime "Two. One grade up, only with a senior partner beside you."

    utahime "Three. You always take someone. I don't care how easy the file looks."

    mc "Ijichi said you're helping Gojo-sensei with something, too."

    utahime angry "Do not say that man's name in my office."

    utahime "...I am assisting with a matter that does not concern first-years. That is all it is."

    mcthink "She says it the way people say they're fine."

    utahime neutral "Here."

    "She writes on a strip of paper without looking at it, folds it once, and takes two more from a drawer."

    utahime "A ward I wrote myself. Wear it and your reserve holds a little more. The other two are sealing talismans, for when you're losing."

    utahime @ serious "Come back from a job without your partner, and don't come back to this office."

    utahime "Go on. The board is open whenever I'm in."

    $ recruit("utahime")
    $ flag("utahime_arrived")
    $ flag("mission_board_open")

    scene expression graded_bg() with fade_slow
    return


################################################################################
## m_promo_g3 · Promotion: Grade 3
################################################################################

label st_promotion_g3:
    ## PLACEHOLDER — rewrite in phase 3

    scene bg training with fade_slow
    show maki serious at pos_c
    with dissolve

    "Maki is standing in the middle of the training hall holding a clipboard, and she looks personally offended by it."

    maki "Iori sent the paperwork. Promotion assessment, Grade 3. I'm the witness."

    maki "There's a curse in the sealed box behind me. Registered Grade 3, caught last week, very annoyed about it."

    maki "Beat it and you're Grade 3. Don't, and you come back tomorrow. Nobody writes anything bad down either way."

    maki @ angry "Don't look at me. I'm not allowed to help, and I wouldn't."

    "She kicks the seal off the lid."

    call combat("promo_g3", None, True, "bg training")

    if _return == "win":

        scene bg training with fade_hard
        show maki happy at pos_c
        with dissolve

        maki "...Fine. That was fine."

        maki "You read it before you hit it. Most people who pass this just hit it harder."

        $ promote("mc", "g3", "Promotion assessment")
        call show_grade_card("g3")

        maki serious "Grade 3. It means they send you somewhere worse. Congratulations."

    else:

        scene bg training with fade_hard
        show maki serious at pos_c
        with dissolve

        maki "Again. Tomorrow."

        maki "Eat something first. You fought like you were hungry."

        $ mission_fail("m_promo_g3")

    scene expression graded_bg() with fade_slow
    return


################################################################################
## cm_ijichi_1 · Ride-Along
################################################################################

label cm_ijichi_1:
    ## PLACEHOLDER — rewrite in phase 3

    scene bg gate with fade_slow
    show ijichi surprised at pos_c
    with dissolve

    ijichi "Oh — you came. That's, um. That's good. Thank you."

    ijichi neutral "Principal Yaga thought you should see the job from the passenger seat. Three sites today. Nothing that should need you."

    ijichi @ sad "Should. I'm sorry. I always say should."

    scene bg car with fade_hard

    "Ijichi drives exactly at the speed limit and apologises to other cars when they overtake him."

    "The first site is a primary school whose caretaker keeps finding the same classroom door open. Ijichi walks the corridor with a clipboard, finds nothing, and bows to the caretaker for a full three seconds."

    "The second is a car park where something has been sitting on level four for a month. It is a Grade 4 residual, fading on its own. He files it, and we leave it to finish."

    scene bg town_street with fade_hard
    show ijichi serious at pos_c
    with dissolve

    "The third is a street corner in Nerima, where an assessment team is going in after dark and needs the block kept clear."

    ijichi "Please stand behind me. It isn't dangerous. It's just rude to stand in front."

    "He raises two fingers and murmurs something under his breath, and the sky above the corner darkens like ink dropped into water."

    "Nobody on the street notices. That is the point of it, he tells me: people walk around the corner without ever deciding to."

    mcthink "Somebody raises one of these every time a sorcerer goes to work. I had never once thought about who."

    scene bg car with fade_hard
    show ijichi neutral at pos_c
    with dissolve

    ijichi "On days you're free, I could drive you into the city. If you like. Mornings to afternoons, from the gate."

    ijichi happy "It's nicer with someone in the passenger seat. Gojo-san sits in the back and kicks my chair."

    $ flag("ijichi_rides")
    $ here = "gate"

    scene expression graded_bg() with fade_slow
    return


################################################################################
## cm_maki_1 · The Armory
################################################################################

label cm_maki_1:
    ## PLACEHOLDER — rewrite in phase 3

    scene bg storehouse with fade_slow
    show maki serious at pos_c
    with dissolve

    "Maki walks me to the storehouse without saying why, takes a key off a nail I never noticed, and opens the inner door."

    maki "Yaga's rule is look, don't take. Yaga's rule has an exception, and it's me."

    maki "These racks are graded the way you are. Grade 4 tools come out for Grade 4 sorcerers. Anything above that stays sealed until your paperwork catches up."

    maki @ angry "Don't sulk. It's the only rule in this place that's ever kept anyone alive."

    "She takes a short knife off the lowest rack. The black sheath has a paper seal across the guard."

    maki "Slaughter Demon. It cuts curses, and whatever it cuts keeps bleeding."

    maki happy "It was my first one too. Try not to lose it inside something."

    mcthink "It is lighter than it should be, and warm, as if somebody had just put it down."

    maki serious "The armory knows your face now. Come back when your grade does."

    $ flag("armory_open")
    $ here = "storehouse"

    scene expression graded_bg() with fade_slow
    return
