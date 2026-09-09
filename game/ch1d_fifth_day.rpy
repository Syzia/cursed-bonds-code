################################################################################
## Chapter One (d) — On the Fifth Day
## Day 4 evening through Day 5 morning. Ends as the car reaches the expressway.
################################################################################

label chapter_one_d:

    scene bg black with None
    show screen chapter_card("CHAPTER ONE", "On the Fifth Day", "A car comes.")
    with fade_slow
    $ renpy.pause(2.4)
    hide screen chapter_card
    with fade_slow

    scene bg home_bedroom with fade_slow
    show mother at pos_cr
    with dissolve

    "Your mother packs your room on Monday evening."

    "She packs things you would not have packed: a photograph of the three of you at a beach in a year you barely remember, the winter coat, a jumper you have not worn since you were fourteen."

    "She does not pack the festival photograph."

    "She is cheerful throughout. There is no sadness anywhere in the room, and the absence of it has a shape, like a missing tooth your tongue keeps going back to."

    if has_flag("held_it_burning"):
        "Your palms are blistered. She has put ointment on them and taped them and not once asked how."

    "Your father comes home early with a cake that says {i}Congratulations{/i} in pink icing."

    "Nobody can remember ordering it."

    hide mother with dissolve
    scene bg konbini with fade_slow
    show gojo at pos_cr
    show mc at pos_l
    with dissolve

    "You go out for air at nine, and there is a very tall man sitting on the kerb outside the convenience store with a plastic bag of sweet buns."

    "He has clearly been there some time."

    gojo "I felt something go out on Saturday night. Three streets that way."

    gojo "Very tidy. Or very messy — from Shinjuku those feel about the same."

    "He has not come to help. He came four days late, on purpose, to see what you did without him."

    gojo "I'm putting the convenience store in the report, by the way. Yaga reads them. He'll hate it."

    if has_flag("reported_curse"):
        gojo "You told Kurose. Good. Boring, but good."
    elif has_flag("called_oda"):
        gojo "You rang your {i}homeroom teacher.{/i}"
        gojo "I have genuinely never seen anyone do that. I'm going to be thinking about it all week."
    else:
        gojo "You told nobody. Interesting."
        gojo "Stupid. But interesting. Do it again and I'll be annoyed."

    "He offers you the bag. You take one because it is easier than not."

    gojo "The paper on your table. You want to know what it does."

    gojo "It's not mind control. Mind control's rude, and it doesn't hold."

    gojo "It's a veil. For people. It finds the part of them that would worry, and it gives that part something else to do."

    gojo "They'll be happy. Accurately happy — it's not a lie, they really will be."

    gojo "It's the kindest thing we do and I hate it."

    menu:
        "He is eating a sweet bun on a kerb and has just described your family."

        "\"Will they miss me?\"":
            $ add_bond("gojo", 4)
            $ flag("asked_gojo_parents")
            "There is a pause with actual weight in it, which you have not seen from him before."
            gojo "...Yes."
            gojo "Just not at the volume you deserve."
            "He does not make a joke afterwards, and the not-joking is the worst part."

        "\"What did Kurose mean — unless she becomes one?\"":
            $ add_bond("gojo", 6)
            $ flag("asked_gojo_sana")
            $ flag("sana_visit_warned")
            gojo "It means Saturday moved her out of one column and into another."
            gojo "And then you moved her back. Nicely, actually."
            gojo "She's in the safe column now. You keep her there by not going to see her."
            "You had not, until this moment, understood that you were going to have to be careful with her from a distance, permanently."

        "\"Why weren't you there?\"":
            if has_flag("gojo_challenged"):
                $ add_bond("gojo", 8)
            else:
                $ add_bond("gojo", 3)
            $ flag("asked_gojo_absent")
            gojo "Because you didn't need me."
            gojo "If you had, I'd have been there. I {i}was{/i} there — Shinjuku, eating a crepe, listening."
            gojo "That's how it works with me. It's very annoying for everyone."
            gojo "Also I wanted to see whether you'd tell anybody."

    gojo "Right. One thing before I go, since I'm here and you're standing there."

    menu:
        "He has not stood up."

        "Take the lesson.":
            $ flag("gojo_lesson")
            $ add_bond("gojo", 3)
            if technique == "filament":
                gojo "Thread the shop door. Hold it shut. Three seconds, against an actual person."
                "A salaryman walks into a door that will not open, apologises to it, and tries again."
                gojo "Good. Now notice you did that without looking at your hands."
                $ gain("control", 3)
            elif technique == "emberfall":
                gojo "Warm this."
                "You warm his coffee can."
                gojo "Now {i}stop.{/i}"
                "You stop, and that turns out to be the entire lesson, and much harder than starting."
                $ gain("output", 2)
                $ gain("control", 2)
            else:
                gojo "Play the kerb back. Find the bit that's me."
                "You listen. There is a bus, a shutter, a bicycle, an argument two streets over."
                "There is no version of the last hour with him in it."
                gojo "I don't leave any. That should worry you considerably more than the thing in the bedroom did."
                $ gain("insight", 3)

        "\"Not tonight.\"":
            $ flag("refused_gojo_lesson")
            $ add_bond("gojo", 2)
            gojo "Okay."
            gojo "You'll ask later. They always ask later."
            "He is not remotely offended, which is somehow worse than if he had been."

    if has_flag("held_it_burning"):
        gojo "Next time, use something that isn't your hands."
        gojo "Or don't. It's a style."

    "He stands, and shoulders the bag, and looks down the street at nothing."

    gojo "Things will keep coming to your road for a while after you've gone. Not for them — they're empty, there's nothing there to eat."

    gojo "For the smell of you."

    gojo "Someone will come and put a veil on the street. He's very good at it. He'll apologise the entire time."

    gojo "Tomorrow, the car. Bring one thing you're not supposed to."

    gojo "Everyone does. It's the ones who bring nothing that I worry about."

    "He is gone between one streetlight and the next. You did not see him go and you are not entirely certain that he did."

    hide gojo
    hide mc
    with dissolve

    scene bg home_bedroom with fade_slow

    "Tuesday. The suitcase is closed. Your mother's list is taped to the lid, itemised, in her own handwriting, in her own pen."

    menu:
        "One thing that isn't on the list."

        "The festival photograph.":
            $ flag("took_photo")
            $ gain("insight", 2)
            "The one with the East Wing in the background, and the fourth shape in the upstairs window."
            "Somebody at this school is going to want to see that."

        "Your father's old watch.":
            $ flag("took_watch")
            $ gain("control", 2)
            "It has been in the drawer since before you were born."
            "He puts it in your hand himself, in the hall, and says {i}for the exams.{/i}"
            "He thinks there are going to be exams."

        "Sana's hachimaki." if sana_trust >= 2:
            $ flag("took_hachimaki")
            $ sana_trust += 1
            "She left it at yours after the festival, and she has not asked for it, and she is not going to."
            "It has her name inside the band in marker, in her handwriting, from a year she can still account for."

        "Oda-sensei's number." if has_flag("oda_number"):
            $ flag("took_oda_number")
            $ gain("insight", 1)
            "You fold the carbon copy down to the size of a stamp and put it behind your student card."

        "Nothing. Exactly the list.":
            $ flag("took_nothing")
            $ gain("control", 3)
            "You take exactly what is written down, and nothing else, and close the case."
            mcthink "{i}It's the ones who bring nothing that I worry about.{/i}"

    menu:
        "And one thing you leave."

        "A letter for Sana.":
            $ flag("left_letter")
            $ sana_trust += 2
            $ gain("control", 2)
            "You write the whole truth, four pages, and push it under her door on the way to the corner."
            "You already know it will slide off her when she reads it."
            "You write it anyway. The writing was the point; the reading was never going to be."
            "On the last page you tell her to open it again if she ever has the corridor dream twice in one week."

        "Your number on the calendar.":
            $ flag("left_number_home")
            $ gain("output", 2)
            "Underneath {i}[mc_name] — school{/i}, in the expensive pen that is not your mother's, you write your own telephone number in your own biro."
            "It is a small act of vandalism against a document, and it makes you feel better than it should."

        "Nothing. A clean exit.":
            $ flag("clean_exit")
            $ gain("control", 3)
            "You leave nothing at all, because it is kinder, and it is."
            "You learned that from a man in a black suit four days ago, and you are aware of where you learned it."

    scene bg street_morning with fade_slow

    "The car is black and completely unremarkable."

    "A man in a black suit gets out. He bows to your mother twice. He apologises to your father for the hour."

    "Then he apologises to you for the road, before you have said anything at all."

    if technique == "aftersound":
        "The street plays back five days without being asked: your mother going in and out with the pen. And once, on Sunday night, standing alone in the hall at two in the morning, doing nothing whatsoever."
        $ flag("heard_mother_awake")

    menu:
        "He reaches for your bag."

        "Let him take it.":
            $ add_bond("ijichi", 3, quiet=True)
            $ flag("driver_let_carry")
            "He looks so relieved that you feel briefly guilty for having considered saying no."

        "Carry it yourself. Thank him.":
            $ add_bond("ijichi", 2, quiet=True)
            $ flag("driver_thanked")
            "He apologises for having offered."

    "Your mother hugs you for the correct length of time. Your father shakes your hand, which he has never done."

    "Neither of them cries, and you had not realised until this second how much you had been counting on one of them to."

    "You get in."

    "As the door closes your mother puts her hand flat against the window."

    "For exactly one second there is something underneath her face, pushing, trying to get out — the way a fish moves under ice."

    "Then it is gone, and she smiles, and waves."

    mcthink "There. That was her."

    mcthink "One second of her, in five days."

    if has_flag("sana_half") or (has_flag("sana_told") and sana_trust >= 3):
        "Sana is standing at the corner in her school uniform, which is wrong, because school is in the other direction."
        "She does not wave. She looks at the car the way you look at something you are trying to memorise while it is already leaving."
    elif has_flag("sana_spared"):
        "The corner is empty."
        "You look for her the whole way down the road, which is your own doing, and you know it."

    if has_flag("reported_curse"):
        "There is a white van with no logo parked outside the Torii house."
        mc "What's that?"
        voice_ "Assessment."
        voice_ "...Sorry."

    scene bg car with fade_slow

    "The car turns onto the expressway."

    voice_ "Sorry — it's about ninety minutes."

    "That is twice he has apologised."

    "For something to do, you decide to count."

    scene bg black with fade_slow
    return
