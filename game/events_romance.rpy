################################################################################
## Cursed Bonds — romance activities.
##
## Three tiers, unlocked by affection, which is itself capped by bond. Each is
## written per character; PG-13 throughout — the weight is in what gets said.
################################################################################

label act_rom_town(who):

    scene bg city with fade_slow
    show expression who at pos_c
    with dissolve

    $ _n = CAST[who]["short"]

    "You get the bus down the mountain together, which takes ninety minutes and costs a whole afternoon, and neither of you calls it anything."

    if who == "nobara":
        nobara "Right. Ground rules. You carry the bags, you don't say 'do you need that', and if I ask which one you pick one."
        mc "What if I pick wrong?"
        nobara "Then I'll know something about you."
        "She takes you through four shops with the focus of a woman running a mission. You pick, twice. She buys the one you picked, twice, and says nothing about it."
        "On the bus back she falls asleep somewhere around the third tunnel and does not lean on your shoulder, but ends up quite close to it."
        nobara "...If you tell Itadori about the sleeping I'll deny it and he'll believe me."

    elif who == "maki":
        maki "I need a whetstone and a coat that isn't school issue. That's the whole list."
        "It takes eleven minutes. You have four hours left."
        maki "...Right. I hadn't thought past the list."
        "So you walk. She is bad at this in a way you find unreasonably reassuring — she keeps naming exits, and then catching herself doing it, and stopping."
        maki "This is the first afternoon in about two years where nobody's expecting anything off me."
        maki "I don't know what to do with it."
        mc "You don't have to do anything with it."
        maki "See, that's—"
        "She stops."
        maki "Yeah. Okay."

    else:
        shoko "I haven't been off that mountain in five weeks. Do you know how that sounds when I say it out loud?"
        "She takes you to a coffee place she used to go to at eighteen, which is now a different coffee place, and she is quietly, genuinely upset about it for about four seconds."
        shoko "That's the thing nobody tells you about staying in one job. The city keeps going without asking."
        "She buys you the expensive one. She does not let you pay. She is very firm about it in a way that closes the subject."
        shoko "Don't make this a habit. ...Make it a bit of a habit."

    $ add_bond(who, 5)
    $ add_aff(who, 10)
    $ flag("town_date_" + who)
    scene bg gate with fade_slow
    show expression who at pos_c
    return


label act_rom_close(who):

    $ _n = CAST[who]["short"]

    "Whatever you were doing has finished, and neither of you has stood up."

    if who == "nobara":
        nobara "It's late."
        mc "It is."
        nobara "I'm not going anywhere though."
        "She says it to the middle distance, like a weather report, and then glances over to see whether you heard it as one."
        mc "Neither am I."
        nobara "Good. Fine. Great."
        "She shifts about four centimetres closer and spends the next hour talking about absolutely nothing, and you have never listened to anything so carefully."

    elif who == "maki":
        "Zenin doesn't do endings. She does the last repetition and then the next one. So when she stops, and stays stopped, you notice."
        maki "I keep finding reasons for you to be in the dojo at six in the morning."
        maki "There aren't that many reasons. I've used most of them."
        mc "You could just ask."
        maki "..."
        maki "Come to the dojo at six in the morning."
        mc "Why?"
        maki "Because I want you there."
        "It costs her something visible to say, and she says it looking straight at you, because Maki Zenin does not flinch on purpose."

    else:
        "The infirmary at this hour is just a lit room with two people in it."
        shoko "You should go to bed."
        mc "So should you."
        shoko "I live here. That's not a joke, that's a lease violation."
        "She turns the desk lamp down instead of off, which is not the same as asking you to stay, and is not different from it either."
        shoko "I'm not good at this. I want to be clear about that in advance, so it's not a surprise later."
        mc "Noted."
        shoko "...You didn't ask what 'this' was."
        mc "No."
        shoko "Right."

    $ add_bond(who, 4)
    $ add_aff(who, 12)
    $ flag("close_" + who)
    return


label act_rom_say(who):

    $ _n = CAST[who]["short"]

    "You have been carrying the sentence around for about a week and it has not got any lighter."

    if who == "nobara":
        mc "Kugisaki. Nobara."
        nobara "Oh, we're doing full names. This is going to be a whole thing, isn't it."
        mc "I'm in love with you."
        "There is a silence with an enormous amount happening inside it."
        nobara "...Okay, see, I had a whole plan for this, and the plan was that {i}I{/i} would say it, in about three weeks, somewhere better than a corridor."
        mc "Sorry."
        nobara "Don't be sorry, you've ruined it, it's fine, I'm furious—"
        "She takes your collar in both hands and does not appear to know what she intends to do with it."
        nobara "I love you too. Obviously. God, {i}obviously.{/i}"
        nobara "If you tell Itadori before I do I will end you."

    elif who == "maki":
        "You say it badly. You have rehearsed it and it comes out in the wrong order and you say it anyway."
        maki "..."
        maki "You know what I am, right? No cursed energy. A family that'd rather I didn't exist. A twin who says things about me in public."
        mc "Yes."
        maki "And you're saying it anyway."
        mc "I'm saying it because of it."
        "She looks at the floor for a long moment. When she looks up her eyes are wet and her jaw is set, which is the most Maki Zenin arrangement of a face there has ever been."
        maki "I told you to ask me again when I'd won something."
        mc "You have."
        maki "I haven't won anything."
        mc "You got out. You're still standing. That's the whole fight."
        maki "..."
        maki "Then ask me."
        mc "Maki—"
        maki "{b}Yes.{/b} Sorry. Yes. I've been holding that for a couple of weeks, I wasn't going to make you finish."

    else:
        mc "Shoko."
        shoko "Don't."
        mc "I'm going to."
        shoko "I know. That's why I said don't."
        "She puts the pen down, which from Shoko Ieiri is the same as standing up."
        shoko "I have watched eleven years of people in this building fall in love and then get filed. I'm the one who files them."
        shoko "So when you say it I'm going to hear the form. That's not your fault, it's just wiring."
        mc "I'm saying it anyway."
        shoko "...Yeah."
        shoko "Go on, then."
        mc "I love you."
        "She is quiet for a long time."
        shoko "Right. Okay."
        shoko "I'm going to say it back and then I'm going to be extremely normal about it, because if I stop to feel it properly I'll cry, and I have not cried since two thousand and fifteen and I'd like to keep the record."
        shoko "I love you. Pass me that form."
        "You pass her the form. Her hand is not entirely steady."

    $ add_bond(who, 10)
    $ begin_together(who)
    $ add_aff(who, 10)

    "Something that had been at its limit for weeks has quietly stopped having one."

    return
