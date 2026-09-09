################################################################################
## Chapter One (b) — Nothing Happened
## Day 1. The morning after the East Wing; festival day; that evening.
################################################################################

label chapter_one_b:

    scene bg black with None
    show screen chapter_card("CHAPTER ONE", "Nothing Happened", "Festival day.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    scene bg home_bedroom with fade_slow

    "Six forty in the morning. Thirty-one messages in the class chat, none of them about Sana."

    "The East Wing is closed for structural reasons. Somebody has posted a photo of the new tape. Fourteen people have reacted to it with the laughing face."

    "Your hands are fine. Your shoulder, where it put its hand, is fine. There is no bruise, no ache, no mark of any kind."

    mcthink "Nothing is wrong with me."

    mcthink "That's the wrong part."

    if has_flag("evidence_entry"):
        "You open last night's photo."
        "The corridor is empty in it. Not cleaned up — {i}empty{/i}, the way a thing is empty when it was never recorded in the first place."
        $ gain("insight", 2)

    scene bg home_living with fade_slow
    show mother at pos_cl
    show father at pos_r
    with dissolve

    "Your mother is making three breakfasts and humming something from a drama she has never admitted to watching."

    mother "You came in late."

    "You wait for the rest of it."

    "It doesn't come."

    father "Oh — a man from the school rang at seven. About a scholarship interview, this evening."

    father "Sounded very pleasant."

    "You have never applied for anything."

    menu:
        "Your mother is buttering toast and waiting for an answer that she has not, in fact, asked for."

        "\"Nothing happened.\"":
            $ flag("mother_lied")
            $ gain("insight", 2)
            mother "Mm."
            "She accepts it about half a second too fast. Not suspiciously fast — {i}comfortably{/i} fast, like a woman being handed a coat she was already reaching for."

        "\"Sana got hurt. I helped.\"":
            $ flag("mother_told_partial")
            "Your mother looks at your hands, which is an odd place to look."
            mother "Well. She's fine now."
            "She says it the way you confirm a thing, not the way you hope one."

        "\"What scholarship?\"":
            $ flag("asked_scholarship")
            $ gain("insight", 3)
            mother "He said you'd been selected."
            mother "He had a very nice voice."
            mc "What was his name?"
            "She thinks about it while she pours the tea, and then she pours the tea, and the question goes somewhere and does not come back."

    scene bg festival with fade_slow

    "The festival happens."

    "That is the thing you will remember about the day, later, when you are somewhere else entirely: it happens, completely, on schedule, forty metres from a taped-off corridor."

    "Two men in coveralls are working at the tape. Their van has no logo on it."

    "There is a crow on every fence post between the gate and the East Wing. Not many crows. One per post, the whole way, all of them facing the same direction, which is the direction you are walking."

    "The takoyaki stall's dog starts whining when you pass and does not stop until you are well down the row."

    if technique == "aftersound":
        "You don't mean to listen. The corridor by the tape gives you five in the morning anyway: two people at the door, and one of them saying {i}the girl's clean, the boy isn't — don't touch the boy.{/i}"
        $ gain("insight", 2)

    scene bg yotsuka_class with fade_slow
    show oda at pos_cr
    with dissolve

    "Oda-sensei catches you between the stall shifts, in an empty classroom, holding a form."

    oda "Extended leave. Filled in. Dated today. Stamped by the vice-principal."

    oda "Your parents rang this morning and said scholarship."

    oda "I have done this job for nineteen years."

    oda "Scholarships do not telephone the school before the family knows the name of the school."

    "She is entirely on your side and she can do absolutely nothing, and she knows both of those things, and she is telling you anyway."

    menu:
        "She has not put the form down."

        "\"It's real. I'm going.\"":
            $ flag("oda_reassured")
            $ gain("control", 2)
            "You lie to protect her, which is a new kind of lie and you find you are good at it."
            "She signs. She doesn't believe you. She signs anyway, because the alternative is a conversation she isn't allowed to win."

        "\"I don't know what it is either.\"":
            $ flag("oda_confided")
            $ flag("oda_number")
            oda "...Right."
            "She takes the carbon copy, turns it over, and writes a mobile number on the back in small, fast handwriting."
            oda "That's mine. Not the school's."
            oda "If it turns out not to be a scholarship, you call that."

        "Say nothing. Let her fill it.":
            $ gain("insight", 3)
            "You don't answer, and the silence does the work."
            oda "...The vice-principal told me to sign it before first period."
            "It is now the middle of the afternoon. She has been stalling for six hours, on her own, over a boy she teaches maths to."

    hide oda with dissolve
    scene bg festival with fade_slow
    show sana at pos_cr
    with dissolve

    "Sana Torii is running the class stall in a hachimaki, at volume, wearing one borrowed sneaker."

    sana "Have you seen my other shoe? I've lost a {i}shoe{/i}. Who loses one shoe?"

    "You know precisely where it is. It is forty paces into a corridor that is closed for structural reasons."

    sana "I went home sick. Seven-ish? Felt rotten, went home, slept like the dead."

    sana "Everyone's being weird with me today and nobody will say why, which is honestly worse than whatever it is."

    "She pulls her collar aside without warning, the way she has done since you were both eleven."

    sana "Oh — look at this. Woke up with it."

    "There is a bruise on her sternum. It is not the shape of furniture."

    sana "Shaped like a {i}hand.{/i} I'm haunted. I'm going to charge admission."

    menu:
        "She is laughing. She is genuinely laughing."

        "\"Show me. Properly.\"":
            $ flag("sana_marked_seen")
            "She holds still, amused, while you look at it like it matters."
            if technique == "filament":
                "There is a thread on it. Not yours. Thin, and old, and it runs off her and away over the rooftops toward the East Wing, and it is still attached."
                $ gain("control", 3)
            elif technique == "emberfall":
                "The skin over it is cold. Not cool. Cold, in the specific way that means something took heat out and did not give it back."
                $ gain("output", 3)
            else:
                "Under the stall noise the yard is still playing last night, and in it Sana is saying {i}it's not funny anymore{/i} in a voice you have never heard her use."
                $ gain("insight", 3)
            sana "Well? Am I cursed?"
            mc "...You're fine."

        "\"Put ice on it.\"":
            $ flag("sana_marked_ignored")
            $ gain("control", 1)
            "You do not look at it properly, and you are aware, while not looking, that you are choosing not to know."
            sana "Ice. Great. Very medical."

        "\"What did you dream?\"":
            $ sana_trust += 1
            $ flag("sana_dream")
            sana "Huh. A corridor."
            sana "Someone shouting my name. Really shouting. That's it, that's the whole dream."
            sana "Why?"
            mc "No reason."
            "She squeezes your arm on her way back to the griddle and does not think about it again."

    "The fireworks are cancelled. Structural."

    "A teacher plays a video of fireworks on the gym projector instead, and four hundred people stand in the dark and watch a recording of a sky."

    "Everyone claps."

    "You clap."

    hide sana with dissolve
    scene bg home_living with fade_slow
    show kurose at pos_c
    show mother at pos_fl
    show father at pos_fr
    with dissolve

    "There is a man at your kitchen table."

    "Black suit, black tie, glasses that do not catch the light. He has been given tea and has not touched it. When you come in he stands, and bows to you — {i}to you{/i}, before your parents — and your father notices this and likes it enormously."

    kurose "Kurose. I'm from the school."

    kurose "Congratulations."

    "There is one sheet of paper on the table. No letterhead. No stamp. One signature line."

    "Your mother's hanko is already sitting beside it."

    menu:
        "Nobody has explained anything, and nobody in the room but you seems to have noticed."

        "Pick it up and read it.":
            $ flag("read_the_paper")
            $ gain("insight", 3)
            "You read the first sentence. You reach the end of it and it is a different sentence."
            "You go back. It is a different sentence again. Two words hold still long enough to be read: {i}custodial{/i}, and {i}disclosure{/i}."
            kurose "Most people don't read it."
            kurose "That's fine too."

        "\"What happens if they don't sign?\"":
            $ flag("challenged_kurose")
            $ gain("output", 2)
            "Your father laughs, embarrassed, and starts to apologise for you."
            "Kurose raises one finger, and your father stops, and does not appear to mind stopping."
            kurose "Then we ask again on Thursday."
            kurose "We're very patient. It's the one thing we're reliably good at."

        "Say nothing. Watch your mother's hand.":
            $ gain("insight", 3)
            "Your mother picks up the hanko the way she picks up anything — without ceremony, mid-sentence, already talking about the cake."
            "There is no hesitation in it at all."
            "You had been hoping for hesitation."

    father "It's a good opportunity."

    "Your mother stamps. Your father signs. It takes nine seconds."

    kurose "They'll be very comfortable with this."

    kurose "That's part of the service."

    "At the door, while your parents are in the kitchen being pleased, he stops and speaks to you alone, at a volume they will not hear."

    kurose "The Torii girl isn't our concern."

    kurose "Unless she becomes one."

    "He gives you a card. It has a phone number on it and nothing else — no name, no logo, no organisation."

    $ flag("kurose_card")

    hide kurose
    hide mother
    hide father
    with dissolve

    scene bg home_bedroom_night with fade_slow

    "The house creaks in all the places the house creaks."

    "At two-fourteen in the morning the light in the hall comes on."

    "You lie still and listen to nobody walking, and after a while it goes off again."

    "You do not get up."

    scene bg black with fade_slow
    return
