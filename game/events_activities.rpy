################################################################################
## Cursed Bonds — activity scenes.
##
## One label per activity. Each pulls character-specific lines from a table so
## eating with Maki is not eating with Panda, without writing 9 x 12 scenes.
################################################################################

init -1 python:

    ## who -> line. "_" is the fallback for anyone without an entry.
    LINES = {
        "eat": {
            "_":      "They eat like someone who has been told to and is complying.",
            "yuji":   "Itadori eats three helpings and talks through all of them, and somehow I follow every word.",
            "megumi": "Fushiguro eats in complete silence and then, at the end, says the food was good, as though filing a report.",
            "nobara": "Kugisaki rates every dish out of ten, aloud, with reasons. The rice gets a four and she will not be moved.",
            "maki":   "Zenin eats an enormous amount very fast, notices me noticing, and does not slow down.",
            "panda":  "Panda has brought his own crisps to a canteen. He offers me some. They are somehow the best thing on the table.",
            "toge":   "Inumaki eats with his collar pulled down and his back to the room, and pushes the pickles onto my tray without comment.",
            "shoko":  "Ieiri has coffee and half a bread roll and calls it lunch, and dares me with her eyes to say something.",
            "gojo":   "Gojo has ordered four desserts and no food. He is not embarrassed. He offers me the worst one.",
            "yaga":   "Yaga eats a set meal in eleven minutes and asks me two questions about my training, both of which I get wrong.",
        },
        "study": {
            "_":      "We get through about nine pages between us.",
            "yuji":   "Itadori reads a paragraph aloud four times and then explains it back to me, wrong, in a way that makes it clearer.",
            "megumi": "Fushiguro has already read it. He waits for me to catch up without any sign of impatience, which is worse.",
            "nobara": "Kugisaki highlights things aggressively and calls the author an idiot twice.",
            "maki":   "Zenin studies the way she trains — repetition, no complaining, and a small noise of contempt at anything decorative.",
            "panda":  "Panda cannot hold a pen properly and has developed an elaborate workaround involving his mouth. It works.",
            "toge":   "Inumaki writes his questions on my page in the margin. His handwriting is very small and very neat.",
            "shoko":  "Ieiri explains cursed energy pathways on the back of a form and it makes more sense in four minutes than the book has in a month.",
            "gojo":   "Gojo reads over my shoulder, corrects the textbook, and refuses to explain why it's wrong.",
            "yaga":   "Yaga does not study with me. He sets me a problem, leaves, and comes back exactly when I have finished it.",
        },
        "swim": {
            "_":      "They swim out further than I do and come back slower.",
            "yuji":   "Itadori does a bomb from the rocks and the wave reaches the far bank. He does it eleven more times.",
            "megumi": "Fushiguro swims properly, in a line, like a man completing an exercise, and then floats on his back for a long time saying nothing.",
            "nobara": "Kugisaki declares the water freezing, gets in anyway, and is furious about it for a full minute before she starts enjoying herself.",
            "maki":   "Zenin swims to the far bank and back twice before I've got my shoes off, and is not remotely out of breath.",
            "panda":  "Panda floats. Panda is extremely good at floating. He calls it his best technique and I can't argue.",
            "toge":   "Inumaki won't put his face in — the collar — so he swims with his chin up, and I match him without mentioning it.",
            "shoko":  "Ieiri sits on the rocks with her feet in and her sleeves rolled, and says this is the most exercise she has taken since March.",
        },
        "walk": {
            "_":      "We walk for a while without deciding where.",
            "yuji":   "Itadori talks the whole way and then, somewhere near the treeline, stops talking, and the quiet is comfortable.",
            "megumi": "Fushiguro walks slightly ahead the entire time, and every so often slows until I'm level, and then does it again.",
            "nobara": "Kugisaki walks fast and points at things she has opinions about, which is all things.",
            "maki":   "Zenin names three exits from every place we pass without being asked. It's a game now. I'm getting better at it.",
            "panda":  "Panda walks like a person and it is still, weeks in, briefly astonishing every time.",
            "toge":   "Inumaki walks with me for forty minutes and says two words and it is a real conversation.",
            "shoko":  "Ieiri smokes half of one and puts it out, and walks with her hands in her coat, and does not once mention work.",
            "gojo":   "Gojo walks me the long way round and pretends it's an accident. We pass the same vending machine twice.",
            "yaga":   "Yaga walks the perimeter every evening and lets me come. He points out where the veil is thin, and where it isn't, and why.",
        },
        "stargaze": {
            "_":      "We sit out under it and neither of us fills the silence.",
            "yuji":   "Itadori knows one constellation and it is wrong, and he defends it for twenty minutes.",
            "megumi": "Fushiguro says nothing for an hour and then, at the end, 'this was good,' and goes to bed.",
            "nobara": "Kugisaki says the sky's better here than at home and sounds annoyed to be admitting it.",
            "maki":   "Zenin lies flat on the concrete with her hands behind her head and her glasses folded on her chest.",
            "panda":  "Panda has brought two coffees and a blanket, because Panda always knows.",
            "toge":   "Inumaki points at things and I guess, and I am right about half the time, and that is somehow enough.",
            "shoko":  "Ieiri points out where Tokyo is, over the ridge, by the colour of the sky above it.",
            "gojo":   "Gojo takes the blindfold off for about four seconds. I do not look. He notices that I did not look.",
        },
    }

    def line_for(kind, who):
        return LINES.get(kind, {}).get(who, LINES.get(kind, {}).get("_", ""))


################################################################################
## Friendship activities
################################################################################

label act_eat(who):
    ## Staged by stage_person before this runs: they stay on screen.
    $ _n = CAST[who]["short"]
    $ _l = line_for("eat", who)
    "I get food and sit with [_n]."
    "[_l]"
    $ stamina = min(stamina_max, stamina + 25)
    $ add_bond(who, 3)
    if is_romanceable(who):
        $ add_aff(who, 1)
    return


label act_study(who):
    $ _n = CAST[who]["short"]
    $ _l = line_for("study", who)
    "[_l]"
    $ gain("insight", 3)
    $ add_bond(who, 3)
    $ spend_stamina(8)
    return


label act_swim(who):
    scene bg riverside with Dissolve(0.5)
    show expression who at pos_c
    with dissolve
    $ _n = CAST[who]["short"]
    $ _l = line_for("swim", who)
    "[_l]"
    "Afterwards I lie on the warm stones and let the cold come out of my hands."
    $ gain("output", 2)
    $ restore_ce(12)
    $ spend_stamina(10)
    $ add_bond(who, 5)
    if is_romanceable(who):
        $ add_aff(who, 3)
    return


label act_walk(who):
    $ _n = CAST[who]["short"]
    $ _l = line_for("walk", who)
    "[_l]"
    $ gain("insight", 2)
    $ add_bond(who, 4)
    if is_romanceable(who):
        $ add_aff(who, 2)
    return


label act_stargaze(who):
    $ _n = CAST[who]["short"]
    $ _l = line_for("stargaze", who)
    "[_l]"
    $ restore_ce(15)
    $ add_bond(who, 5)
    if is_romanceable(who):
        $ add_aff(who, 4)
    return


label act_train(who):
    call sb_spar(who)
    return


label act_invite(who):
    $ _n = CAST[who]["short"]
    if companion == who:
        $ companion = None
        "[_n] peels off at the next junction with a half-wave."
        return
    $ companion = who
    if who == "megumi":
        megumi "...Fine. I wasn't doing anything."
    elif who == "nobara":
        nobara "Only because I'm bored. Don't read anything into it."
    elif who == "maki":
        maki "You'll slow me down. Keep up anyway."
    elif who == "yuji":
        yuji "{b}Yes.{/b} Where are we going? Doesn't matter. Yes."
    elif who == "panda":
        panda "Ah, the buddy system. Love the buddy system."
    elif who == "toge":
        toge "Salmon."
    elif who == "shoko":
        shoko "I have three hours before anyone bleeds on me. Fine."
    else:
        "[_n] falls into step beside me."
    "[_n] will stay with me until the day ends."
    $ add_bond(who, 1, quiet=True)
    return


################################################################################
## Confide — the friendship ceiling. One scene per person.
################################################################################

label act_confide(who):

    $ _n = CAST[who]["short"]

    "There is a version of this conversation you have been not having for weeks."

    if who == "yuji":
        mc "I keep waiting to feel like I belong here."
        yuji "Oh, that doesn't stop."
        yuji "I've been here longer than you and I still get it. Every time Gojo-sensei says something I don't understand, or Megumi does the thing where he already knows."
        yuji "You just — do the day anyway. And then there's a load of days behind you and you're in it."
        yuji "That's the whole trick. There isn't a better one, I've looked."
    elif who == "megumi":
        mc "I fought the thing that killed Sana. On my own, before Gojo got there. I lost. I haven't told anyone that."
        megumi "..."
        megumi "How long did it take you to stop replaying it?"
        mc "I haven't."
        megumi "No. You don't."
        megumi "You get a second one, and the first one moves back a place. That's not comfort, it's just what happens."
        megumi "For what it's worth — going at it alone, untrained, and not telling anyone afterwards is the most Fushiguro thing I have ever heard from someone who isn't me."
    elif who == "nobara":
        mc "My parents were made happy about me leaving. Professionally. There's a paper."
        nobara "...Yeah. There's a paper for everyone."
        nobara "Mine signed it too. I watched. Grandma didn't — she was already gone, so there was nobody to make comfortable."
        nobara "I used to think that made me worse off. It doesn't. It means I got to keep the real version of her."
        nobara "You've got a real version of them somewhere. Under the paper. Hold onto it."
    elif who == "maki":
        mc "I don't know if I'm any good at this."
        maki "You aren't."
        maki "Neither was I. Four years ago I couldn't do a single one of the things I did this morning."
        maki "Everyone here who is good at it was bad at it in a room where nobody was watching. That's the entire secret and people keep making it into a personality."
        maki "You're at the boring part. Stay at the boring part."
    elif who == "panda":
        mc "Sometimes I think the person who got into that car outside my house isn't me any more."
        panda "Oh, he isn't. That's not a metaphor, by the way, I'm the wrong person to ask for metaphors about identity."
        panda "But here's the thing nobody says: it's not a loss. You didn't lose him. You've got him. He's in there being the reason you're doing any of this."
        panda "I've got two people in me who never got to be anyone. You've got one who did. Use him."
    elif who == "toge":
        "You tell him. All of it — Kurose's forms, the alley, the girl nobody but you remembers properly now."
        "He listens the way he does everything, completely, and when you finish he takes out his phone and types for a long time."
        "{i}I couldn't say any of that back to you without putting it in your body. So I'm going to sit here instead.{/i}"
        "{i}That's not less. I've had years to decide whether it's less. It isn't.{/i}"
        toge "Salmon."
    elif who == "shoko":
        mc "I don't think I'm frightened of dying here. I think I'm frightened of it being ordinary when I do."
        shoko "It will be."
        shoko "Sorry. You asked for the honest one, I can tell."
        shoko "It'll be a Tuesday, and there'll be a form, and I'll be the one filling it in."
        shoko "And then I'll go and sit on the roof for a while, and that's the part nobody puts in the form. The sitting on the roof is the whole memorial and it's mine and it's not nothing."
    elif who == "gojo":
        mc "Do you actually think any of us are going to be enough?"
        gojo "No."
        gojo "Not individually. Not one of you, on your own, against the thing I'm worried about."
        gojo "Together, in about six years, with nobody dying in between? Maybe."
        gojo "That's the most honest sentence I've said out loud this year and I'd appreciate you not repeating it."
    else:
        mc "I'm not sure what I'm doing here."
        yaga "No. You aren't."
        yaga "Neither was Gojo at your age, and he was already the strongest person alive."
        yaga "Not knowing is not a problem to fix before you start. It is the condition. Work anyway."

    $ add_bond(who, 8)
    if is_romanceable(who):
        $ add_aff(who, 4)
    $ gain("insight", 2)
    $ flag("confided_" + who)
    return
