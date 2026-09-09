################################################################################
## Cursed Bonds — after the confession.
##
## These only exist once affection has broken its ceiling. Kept warm rather
## than explicit: the intimacy is in ordinary time together, which is the thing
## none of these people have ever had much of.
################################################################################

label act_int_night(who):

    scene expression graded_bg() with Dissolve(0.5)
    $ _n = CAST[who]["short"]

    "It gets late in the way it does when neither person is watching for it."

    if who == "nobara":
        nobara "You're not walking back across campus at this hour."
        mc "It's four minutes."
        nobara "You're not walking back across campus at this hour."
        "She fetches a spare futon with enormous busyness, so that at no point does anyone have to say anything, and puts it a very specific distance from her own."
        "You lie in the dark and she talks about her grandmother for about an hour, and then stops mid-sentence, asleep."
        "In the morning the futon has moved. Neither of you mentions it. She makes very aggressive eye contact over breakfast, daring you to."

    elif who == "maki":
        "Zenin does not offer. Zenin states."
        maki "Stay."
        mc "That's not a question."
        maki "No."
        "She gives you the good blanket and takes the thin one and refuses to discuss it. She sleeps like someone who has decided to, immediately and completely, the way she does everything."
        "At some point in the night she says your name, asleep, in a tone you have never heard her use awake — unguarded, and slightly worried, and checking."
        "You say {i}I'm here{/i} into the dark and she goes quiet again."

    else:
        shoko "There's a second bed. It's for patients. You're a patient, technically. You have a bruise."
        mc "That's a stretch."
        shoko "I'm the doctor. I decide what's a stretch."
        "She works until two and you fall asleep to the sound of a pen. At some point it stops."
        "When you wake at five she is asleep at the desk with her head on her arms, and there is a blanket over you that you did not put there, and the lamp has been turned down rather than off."

    $ add_aff(who, 8)
    $ stamina = stamina_max
    $ restore_ce(ce_max)
    return


label act_int_morning(who):

    scene expression graded_bg() with Dissolve(0.5)
    $ _n = CAST[who]["short"]

    "The first hour of the day, before anybody needs either of you for anything."

    if who == "nobara":
        "Kugisaki is catastrophic in the mornings and absolutely refuses to be perceived for the first twenty minutes."
        nobara "Don't talk to me. Don't look at me. Hand me that."
        "You hand her that. Twenty minutes later she is entirely herself again and pretending the previous twenty did not occur."
        nobara "...Thanks for the tea."
        mc "You didn't say anything about tea."
        nobara "I {i}thought{/i} about tea very loudly."

    elif who == "maki":
        "She is already awake. She has been awake for an hour, and has not got up, which for Maki Zenin is roughly unprecedented."
        maki "I've been lying here doing nothing since five."
        maki "I keep waiting to feel like I'm wasting the morning."
        mc "And?"
        maki "It hasn't turned up."
        "She looks genuinely unsettled by this, and stays exactly where she is for another forty minutes."

    else:
        "Shoko Ieiri, at six in the morning, without a cigarette, drinking tea instead of coffee because you left the tea out."
        shoko "This is the longest I've gone without going to the infirmary in about nine years."
        mc "It's been forty minutes."
        shoko "Yes."
        shoko "Do you understand what I'm telling you."
        mc "...Yeah."
        shoko "Good. Don't make a thing of it."
        "She makes a thing of it herself about four minutes later by putting her head on your shoulder and not explaining."

    $ add_aff(who, 8)
    $ stamina = min(stamina_max, stamina + 20)
    return


label act_int_day(who):

    scene bg riverside with fade_slow
    $ _n = CAST[who]["short"]

    "You take an entire day. No training, no board, nobody told."

    if who == "nobara":
        "You swim, badly. She judges your form out of ten and gives you a three and then a four when you improve, and the four is delivered like a medal."
        "She has brought an amount of food that suggests she was worried you would be hungry at some point and could not admit to the worry."
        nobara "I've decided I'm keeping you."
        mc "That's not how it works."
        nobara "It's how {i}I{/i} work. You'll adjust."
        "Later, lying on the warm stones with her head on your stomach, she says something so quietly that you have to ask her to repeat it, and she refuses, and you are fairly sure it was your name."

    elif who == "maki":
        "She does not know how to have a day off. She has never had one. It takes until noon for her to stop finding jobs."
        maki "This is very hard."
        mc "It's a river."
        maki "I'm aware it's a river."
        "By the afternoon she has managed it. She lies in the sun with her glasses off and her eyes shut and her hand in yours, and does not say anything for two hours, and at the end of it:"
        maki "Okay. I understand the point of this now."
        maki "We're doing it again."

    else:
        "You get her off the mountain for a full day, which takes a written note to Yaga and a genuine argument."
        "She spends the first hour checking her phone. The second hour she checks it twice. After that she forgets it exists, and you watch eleven years come off her face in real time."
        shoko "I used to do this. Before."
        shoko "Not with anyone. Just — days, where the next thing wasn't already decided."
        shoko "I'd stopped noticing they'd gone."
        "She falls asleep on the train back with her forehead against the window and does not wake up when it stops."

    $ add_aff(who, 12)
    $ stamina = stamina_max
    $ restore_ce(ce_max)
    return


label act_int_after(who):

    $ _n = CAST[who]["short"]

    "Nobody in this profession talks about after. There is a superstition about it that nobody will admit to."

    "You talk about it anyway."

    if who == "nobara":
        nobara "A flat. In the city, properly in it, not the edge."
        nobara "Big window. Terrible rent. I'd complain about the rent constantly and love it."
        mc "And me?"
        nobara "Obviously you're there, what kind of question is that."
        nobara "You'd do the cooking, because I've eaten what you call cooking and it's better than what I call cooking."
        "She says the whole thing at speed, like a list she has had ready for some time and has been waiting to be asked for."

    elif who == "maki":
        maki "I don't have one."
        maki "That's not me being bleak. I genuinely never made one, because for sixteen years the plan was 'get out', and then it was 'get strong', and there was never a third one."
        mc "So make a third one."
        maki "..."
        maki "Somewhere with a garden. Which is a stupid thing to want."
        mc "It isn't."
        maki "It's the least Zenin thing I can think of. That's why I want it."
        maki "And you're in it, and neither of us is anyone's weapon, and we're extremely boring."

    else:
        shoko "I'll be here."
        shoko "That's not resignation, it's just true. There are four of us in the country. I don't get an after."
        "You wait."
        shoko "...But I could have an alongside."
        shoko "Somebody who comes back. Who I stop having to translate myself for."
        shoko "That's not nothing. That might actually be the whole thing."
        mc "Then that's the plan."
        shoko "That's a terrible plan."
        shoko "...Yeah. That's the plan."

    $ add_aff(who, 10)
    $ add_bond(who, 4)
    $ flag("talked_about_after_" + who)
    return
