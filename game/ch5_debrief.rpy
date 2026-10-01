################################################################################
## Debrief — the evening of the Sun Mall, straight after the mission.
################################################################################

label chapter_five:

    scene bg black
    with None

    show screen chapter_card("DEBRIEF", "What Should Have Happened", "That evening.")
    with fade_slow
    $ renpy.pause(2.4)
    hide screen chapter_card
    with fade_slow

    scene expression graded_bg("classroom", "Evening")
    with fade_slow

    show yaga at pos_c
    with dissolve

    yaga "It was a grade two."

    yaga "It was registered as a grade three because the sorcerer who registered it did a forty-minute survey of a four-storey building, and I have his name, and he will be hearing from me."

    yaga "Four first-years went into a grade two encounter. Four first-years came out. One civilian recovered."

    yaga "That outcome is not a credit to your training. There is a version of that day where I am writing four letters."

    yaga "Do you understand the difference between what happened and what should have happened?"

    mc "Yes, sir."

    yaga "Good. Most people your age say yes and mean 'we won'."

    "He looks at the file in his hands for a moment longer than he needs to."

    yaga "[mc_surname]. Not long ago you did not know cursed energy existed."

    if has_flag("saved_civilian"):
        yaga "You put yourself between a grade two and a civilian on a four-second decision."
        yaga "I want to be extremely clear that I am not praising that."
        yaga "I am {i}recording{/i} it, because it is going to happen again, and next time I want you to have done it once already with somebody watching."
    else:
        yaga "You made a tactical call to neutralise the threat before extraction."
        yaga "It was correct. It was also the call that puts a civilian in a gap for another ninety seconds, and you will be carrying that around for a while, and you should."
        yaga "Not forever. But you should."

    ## A recommendation, not a promotion: Grade 3 is earned on the board and
    ## in the promotion fight with Maki watching (D18). Old saves promoted
    ## here by the old chapter keep their grade (migration 20).
    if "maki" in roster:
        yaga "Your cursed energy has come along faster than your file predicted. Zenin's doing, I assume."
    else:
        yaga "Your cursed energy has come along faster than your file predicted."
    yaga "I am putting your name forward for Grade 3."
    yaga "That is not a promotion. It is a recommendation, and it is worth exactly what you do with it. Earn it on Iori's board, and then in front of a witness."

    ## Paid once: the "ch5_recommendation" key is the one migration 60 checks
    ## before paying the same 20 to old saves.
    python:
        if "ch5_recommendation" not in getattr(store, "merit_granted", ()):
            add_merit(20, "The Sun Mall")
            if hasattr(store, "merit_granted"):
                store.merit_granted.add("ch5_recommendation")
    $ flag("recommended_g3")

    if total_bond() >= 90:
        $ flag("strong_class")
        yaga "One more thing."
        yaga "Gojo left the four of you in a training hall and told you to do something. He tells everyone that. Almost nobody does it."
        yaga "Itadori requested you as a partner. Fushiguro corroborated the request, in writing, which he has never done for anyone."
        if "maki" in roster and bonds.get("maki", 0) >= 20:
            yaga "Zenin has you in her training log most days."
        yaga "That is worth more to me than your grade. Do not tell Gojo I said that, he will be unbearable."

    hide yaga
    with dissolve

    scene bg rooftop evening
    with fade_slow

    show gojo at pos_c
    with dissolve

    gojo "So! Yaga did the whole 'this is not a promotion' thing, right? He loves that one."

    mc "You were listening."

    gojo "I was {i}on the roof.{/i} Which is where we are now, so that's just efficient."

    "He is sitting on the railing with his back to a hundred-kilometre drop, eating something from a convenience store bag, and it is impossible to tell whether he is looking at you."

    gojo "Okay. Real question, and then I'll go away and be annoying somewhere else."

    gojo "The other week you were in an alley behind an arcade. Something was standing over your friend."

    gojo "If you could go back and not have any of it — the technique, the school, all of us — would you?"

    menu:
        "He asks it lightly. He is not asking it lightly."

        "\"No. Not for anything.\"":
            $ add_bond("gojo", 10)
            $ flag("end_committed")
            mc "I spent eighteen years not being able to do anything about anything."
            mc "I'd rather be tired."
            gojo "Ha! Okay. Good answer."
            gojo "Wrong answer, probably. But good."
            gojo "Ask me again in a year and I'll tell you which."

        "\"Ask me when I've stopped shaking.\"":
            $ add_bond("gojo", 8)
            $ flag("end_honest")
            mc "It's been a few hours and my hands still aren't right."
            mc "I don't know. That's the honest version. I don't know yet."
            gojo "..."
            gojo "You know, out of everyone I've ever asked that, about four people said 'I don't know'."
            gojo "They're all still alive."
            gojo "Congratulations, that's the best answer in the set and you got it by being tired."

        "\"Would you?\"":
            $ add_bond("gojo", 12)
            $ flag("end_turned_it_around")
            "For the first time since you met him, Satoru Gojo stops moving."
            gojo "..."
            gojo "That's rude."
            mc "You asked first."
            gojo "I did. Yeah."
            gojo "..."
            gojo "There was a guy. Best friend. Strongest person I knew apart from me, which — at the time, honestly, felt like the same category."
            gojo "And there was a version of the world where I noticed what was happening to him in time."
            gojo "So, yes. There's an alley I'd go back to."
            "He hops off the railing and the grin snaps back into place like a door closing."
            gojo "{i}Anyway!{/i} That's why I keep leaving you lot in a room together and telling you to do something. So you'll notice."
            gojo "Very heavy-handed teaching. I'm aware. It's the only kind I've got."

    gojo "Right. Homework."

    gojo "There's an exchange event with Kyoto coming up. They'll try to hurt you, it's traditional, don't take it personally except from Todo, who means it."

    gojo "Before then: keep doing whatever it is you four do. All of it. Especially the parts that felt like a waste of an afternoon."

    gojo "Because in about six months something is going to be standing in front of one of your friends, and the only thing that'll matter is whether you already knew where they were."

    "He walks off toward the stairs, waves without turning round, and is gone in a way that does not look like walking."

    scene bg rooftop evening
    with slowdissolve

    "You stay on the roof for a while."

    "The other week you were frightened of an alley. You are still frightened of the alley. You have simply added several other things."

    if has_flag("strong_class"):
        "Below you, in the courtyard, three first-years are arguing about whether a person could punch a whale."
        "One of them looks up, sees you, and shouts your name loud enough to carry four floors."
        mcthink "Ah."
        mcthink "So that's what he meant."
    else:
        "Below you, in the courtyard, three first-years are arguing about something you can't hear."
        "You watch them for a while, from up here, and then you go down."
        mcthink "They're not going anywhere. Neither am I."

    ## This is a mid-arc debrief now, not a finale — the arc closes on the
    ## roof the night before Kyoto. Hand the player back to the campus.

    mcthink "Nobody has given me a date for anything."

    mcthink "So I get to choose what the days are for."

    scene bg black
    with fade_slow

    return
