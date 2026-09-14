################################################################################
## Chapter One (c) — The Edit
## Day 2 (Saturday) morning through Day 3, 3 a.m.
################################################################################

label chapter_one_c:

    scene bg black with None
    show screen chapter_card("CHAPTER ONE", "The Edit", "Saturday.")
    with fade_slow
    $ renpy.pause(2.4)
    hide screen chapter_card
    with fade_slow

    scene bg home_living with fade_slow
    show mother at pos_cl
    show father at pos_r
    with dissolve

    "There is a suitcase in the hall. You do not own a suitcase."

    "Your winter coat has been moved to the front of the closet. It is October and it is not cold."

    "On the family calendar, on the fifth day, in your mother's handwriting: {i}[mc_name] — school.{/i}"

    "The pen is black, and fine, and expensive. It is lying on the table."

    "Your mother does not own that pen."

    father "It's a good opportunity."

    "He says it warmly, over the paper, and means it entirely."

    menu:
        "Your mother is humming and moving a plant six inches to the left."

        "\"Where is the school, exactly?\"":
            $ flag("parents_tested")
            $ gain("insight", 3)
            mother "Tokyo."
            "A pause of no particular weight."
            mother "In the mountains."
            "She does not notice that she has given two answers. She asks whether you want the last egg."

        "\"I don't want to go.\"":
            $ flag("parents_pushed")
            $ flag("anger_seeded")
            $ gain("output", 2)
            mother "Of course you do, sweetheart."
            "She says it without looking up, with a pen in her hand that is not hers, and moves on to whether you have enough socks."
            mcthink "The paper was never about their permission."
            mcthink "It was about their peace."

        "Let it go. Eat breakfast.":
            $ flag("parents_let_it")
            $ gain("control", 3)
            "You eat breakfast in a kitchen with a woman who is happy, and a man who is proud, and a calendar with your leaving written on it in somebody else's pen."
            "Holding still turns out to be a discipline of its own."

    hide mother
    hide father
    with dissolve
    scene bg town_street with fade_slow

    "You walk into town along the route Sana takes to the station, for no reason you would be able to give if asked."

    "A chained dog in a yard stands up as you pass, and stays standing, and watches you the whole length of the fence."

    "A shrine cat crosses the road to walk beside you for exactly one block, and then stops dead at a drain cover as though it has walked into a wall."

    "A man at the bus stop looks at you, and keeps looking, and is only a man."

    mcthink "{i}In about six weeks something finds you at a bus stop.{/i}"

    mcthink "He said six weeks."

    "You have not used it since the corridor. You have been carrying it around like a full cup."

    if technique == "filament":
        "You put a thread into the coin return of a vending machine and pull, and a hundred-yen coin comes out into your hand."
        "You spend a while learning how thin a thread can get before it stops being a thread. The answer is: thinner than you can see, and it still holds."
        $ gain("control", 3)
    elif technique == "emberfall":
        "You warm a can of coffee in your palm until it is too hot to hold, and set it on the bench at the station."
        "An hour later, on the way back, it is still warm. Somebody will pick it up today and never know that it was you."
        $ gain("output", 3)
    else:
        "You sit at the bus stop and let it play: the last bus at 23:50, a couple having a small vicious argument about a wedding."
        "And underneath, at about three in the morning, something walking past with no footsteps in it at all. Slowly. In the direction of Sana's street."
        $ gain("insight", 3)
        $ flag("heard_it_walking")

    menu:
        "You could push it further. You can feel where the edge is, roughly, the way you can feel the edge of a step in the dark."

        "Push.":
            $ flag("overreached_early")
            $ add_ce(2)
            "You push, and it goes further than you expected, and then your nose is bleeding onto the pavement."
            "A woman stops to ask if you're all right. You tell her it's hay fever."
            "It is the middle of October."

        "That's enough.":
            $ flag("held_back_early")
            $ gain("control", 1)
            "You put it down carefully, the way you'd put down something that might turn out to be hot."

    scene bg sana_room with fade_slow
    show sana tired at pos_cr
    with dissolve

    "Sana calls at two and asks you to come over, and does not make a joke while asking, which is how you know."

    "Her mother has the television on downstairs. Festival photographs are spread across the floor of her room in no order at all."

    "You are in three of them. In one, the East Wing is in the background, and there is a fourth shape in an upstairs window."

    "Sana has not noticed it. You do not point it out."

    sana "I keep not sleeping."

    sana "I wake up at the same time every night. Two-fourteen. Chest feels heavy — like a cat's sitting on it."

    sana "We don't have a cat."

    if has_flag("sana_marked_seen"):
        mcthink "I know what this is."
        mcthink "Knowing is worse. I had assumed knowing would be better."

    sana "Did something happen? At the festival?"

    sana "Everyone looks at me like I'm made of glass and nobody will say why, and I'm starting to think I did something."

    menu:
        "She is sitting on the floor among photographs of herself being fine."

        "Tell her everything.":
            $ flag("sana_told")
            $ sana_trust += 3
            $ gain("insight", 3)
            "You tell her all of it. The corridor, the thing, the hand on her chest, the man who ended it, the paper on your kitchen table."
            "She believes you completely."
            "It lasts about forty seconds."
            sana "I {i}knew{/i} — I knew there was something, I've been going mad, I knew—"
            "She is crying and gripping your sleeve and then something passes over her face like a hand smoothing a sheet."
            sana "...Sorry. What were we talking about?"
            sana "God, I'm so tired."
            "You told the truth to somebody who is not permitted to keep it, and you had to sit there and watch it be taken out of her."

        "Lie. Well.":
            $ flag("sana_spared")
            $ sana_trust += 1
            $ gain("control", 3)
            mc "Everyone's rattled about the wing closing. That's all it is. You're fine."
            "It fits her like a coat. She relaxes into it in real time."
            sana "...Okay."
            "She says it, and then she looks at you for a moment too long."
            sana "Okay."
            "It is the worst okay you have ever heard, and she has already moved on from it."
            mcthink "That is precisely the trade Kurose made for my parents."
            mcthink "I have just made it for her. I did it faster than he did."

        "Half of it.":
            $ flag("sana_half")
            $ sana_trust += 2
            $ gain("output", 1)
            mc "Something happened. I'm not allowed to tell you."
            mc "And I leave on Wednesday."
            sana "Not allowed by {i}who?{/i}"
            "She is furious. It is real and it is entirely hers, and you find yourself thinking that she will probably keep the anger long after they have taken the reason for it."

    scene bg sana_room_night with fade_slow

    "She falls asleep mid-sentence at nine, on the floor, with a photograph still in her hand."

    "It is the first time she has slept properly in three days, and it is because you are in the room, and the thing under the bed is waiting to find out what you are."

    "Her mother says stay, it's late, she'll telephone your mother."

    "Your mother, on the phone, is delighted."

    "You lie on the floor by the door and do not sleep."

    scene bg sana_room_night with Dissolve(1.2)

    "Two-fourteen."

    show curse sitter at pos_loom_r, pulse_in
    with fade_curse

    "It comes out from under the bed the way a folded thing unfolds."

    "It is the size of a small child put together wrong. Its hands are much too large for it. It has no face — only a seam where a face has been left out."

    "It climbs onto Sana's chest with the unhurried competence of something that has done this every night for three nights, and settles."

    "It does not look at you."

    "Then it does."

    curse2 "Warm."

    "It goes very still, and you understand that it has been waiting for you as well. It simply wanted the easy meal first."

    "Her mother is down the hall. The walls are paper. There is a lamp, a low bed, and six mats of floor."

    "You cannot wreck this room. You have never done this on purpose. You do not yet know what {i}enough{/i} costs."

    menu:
        "It is sitting on your friend's chest, and it is looking at you, and it is in no hurry at all."

        "Get it off her.":
            $ flag("pulled_it_off")
            $ gain("output", 2)
            "You take it by the arm and it is so cold that your hand goes numb, and it comes away with some of your skin."
            "It makes a sound. The stairs creak. You have about twenty seconds."

        "Don't move. Let it come.":
            $ flag("baited_it")
            $ gain("control", 2)
            "You stay exactly where you are, and let it decide."
            "It leaves her and comes across the ceiling toward you, and behind it Sana takes her first full breath in three nights."

        "Wake her.":
            $ flag("woke_sana")
            $ sana_trust += 2
            $ gain("insight", 2)
            "You say her name and she opens her eyes, and for one second — proximity, terror, whatever it is — she sees it."
            "She screams. It is a sound you will hear again."
            "Her mother is coming, faster now."

    if technique == "filament":
        "Threads: one to each wrist, one to the light fitting, one to the desk leg for an anchor."
        "You close your fist."
        "It comes apart without a single sound, and you feel the exact moment it stops being a thing that wants something."
        $ gain("control", 4)
        $ flag("kill_clean")
    elif technique == "emberfall":
        "You cannot set anything alight in a paper-walled bedroom, so you hold it instead. Both palms flat against the seam where its face isn't."
        "It takes a long time. It screams the entire time, in a register that only you and it can hear."
        "You do not let go."
        $ gain("output", 4)
        $ flag("held_it_burning")
    else:
        "You let the room play back, and watch it do this three nights running — including the night Sana woke and looked directly at it and did not see it."
        "Every time it moves, it goes left first. Exactly like the thing in the corridor."
        "You put the desk lamp where its head is going to be, and it does the rest itself."
        $ gain("insight", 4)
        $ flag("kill_read")

    hide curse sitter with fade_curse

    "The door opens. The lamp is on the floor. Nothing else in the room is wrong."

    voice_ "[mc_name]-kun? Is everything—"

    "Sana is asleep on the floor, breathing like a person."

    mc "Sorry. I knocked the lamp over."

    "Her mother looks at you for a long moment."

    voice_ "...Thank you for coming over. She's been better since you got here."

    "She does not know what she is thanking you for. She will never know. That is the arrangement, apparently."

    $ flag("solo_kill")
    $ add_ce(4)

    scene bg sana_room_night with fade_slow

    "Three in the morning. Your hands will not stop shaking and the room smells faintly, sweetly wrong."

    mcthink "He said six weeks."

    mcthink "It was three days. And it wasn't hunting me — it was already here. It came home with her."

    mcthink "{i}Unless she becomes one.{/i}"

    menu:
        "Your phone is on the floor by your knee."

        "Text the number on the card.":
            $ flag("reported_curse")
            "You type four lines and delete three of them and send the fourth."
            "The reply comes in forty seconds."
            voice_ "Noted. Do not re-enter the East Wing."
            mcthink "Somewhere, her name has just gone into a column."

        "Nobody. Handle it.":
            $ flag("kept_it_quiet")
            $ gain("control", 2)
            "You put the phone face down on the mat."
            "It is the first decision you have made since the corridor that nobody made for you."

        "Call Oda-sensei." if has_flag("oda_number"):
            $ flag("called_oda")
            $ gain("insight", 2)
            "She picks up on the second ring. At three in the morning. Without sounding surprised."
            oda "...You're all right?"
            mc "Yeah."
            oda "Right."
            "She stays on the line for eleven minutes and says almost nothing, and it is the most useful thing anybody does for you all week."

    scene bg black with fade_slow
    return
