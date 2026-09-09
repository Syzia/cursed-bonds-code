################################################################################
## Cursed Bonds — the top of the friendship track.
##
## Every other scene in the game has the player needing something: training,
## an explanation, somewhere to put a feeling. Here it goes the other way, once
## per character, and only after they've been told something true.
################################################################################

label act_stand(who):

    scene expression graded_bg() with Dissolve(0.4)
    $ _n = CAST[who]["short"]

    "[_n] has been circling something for about a week. Today they stop circling."

    ## ------------------------------------------------------------------ Yuji
    if who == "yuji":
        yuji "Okay so I've been trying to ask you this for ages and I keep chickening out, so I'm just going to say it in one go."
        yuji "When it happens. The execution thing, or Sukuna, or — whatever version it ends up being."
        yuji "I want you to be the one who tells them."
        mc "Tells who?"
        yuji "Megumi. Kugisaki. Panda, Inumaki, Maki-san. Gojo-sensei'll already know, he always already knows."
        yuji "If somebody official does it, it'll be a room and a form and Ieiri-san's handwriting."
        yuji "And Megumi will go and stand somewhere on his own for about four months."
        yuji "I want it to be someone who'll sit down with them. That's all. That's the whole ask."
        menu:
            "He has clearly rehearsed this and it has still come out sideways."
            "\"I'll do it.\"":
                mc "I'll do it. All of them, in person, sitting down."
                yuji "...Okay. Good. Great."
                "He is enormously relieved and covers it by talking about food for four minutes."
                $ add_bond("yuji", 10)
                $ flag("yuji_will_tell")
            "\"Ask me again when you're eighty.\"":
                mc "I'll do it. On the condition that you ask me again when you're eighty and it's a formality."
                yuji "That's not — you can't negotiate this."
                mc "I just did."
                yuji "..."
                yuji "Deal. Eighty."
                "He shakes your hand on it like a man closing a contract, and holds on about two seconds longer than the joke requires."
                $ add_bond("yuji", 12)
                $ flag("yuji_will_tell")

    ## ---------------------------------------------------------------- Megumi
    elif who == "megumi":
        megumi "I'm going to see Tsumiki on Sunday."
        megumi "I go every three weeks. I've never taken anyone."
        "He is not looking at you, which is how you know this is the ask."
        megumi "It's two hours each way and there's nothing to do when you get there. She doesn't wake up. You sit in a chair."
        mc "You want me to come."
        megumi "..."
        megumi "I want to know whether I still talk to her when there's somebody in the room."
        megumi "I've stopped, I think. At some point I started just sitting."
        megumi "That seems like the sort of thing you notice happening and don't do anything about, and then it's been a year."
        "You go on Sunday. It is two hours each way and there is nothing to do when you get there."
        "He talks to her for forty minutes about a boy called Itadori who eats too much, and about someone new who has been asking him difficult questions, and he does not once mention that you are in the room."
        "On the train back he says nothing at all until the last stop."
        megumi "Same time in three weeks."
        $ add_bond("megumi", 12)
        $ advance_thread("megumi_tsumiki", 3)
        $ flag("visited_tsumiki")

    ## ---------------------------------------------------------------- Nobara
    elif who == "nobara":
        nobara "Right. I need a favour and I'm going to be weird about asking, so bear with me."
        nobara "If I stop — "
        nobara "No. Start again."
        nobara "In this job people get filed. You've seen the forms, Ieiri-san's got a drawer of them."
        nobara "And the form says grade, and date, and cause, and it doesn't say one single thing about the person."
        mc "Nobara—"
        nobara "I'm not being morbid, I'm being {b}organised.{/b}"
        nobara "If I get filed, I want somebody who'll say it out loud. Not at a funeral. Just — normally, for years. In shops. To people who didn't know me."
        nobara "'I knew someone who'd have had an opinion about that.' That kind of thing."
        nobara "Because that's the whole thing I've been on about since I got here. Somebody remembering out loud."
        nobara "I've been doing it for Saori for eight years and nobody's ever going to do it for me unless I ask, and asking is {i}humiliating{/i}, so — "
        mc "Yes."
        nobara "I hadn't finished."
        mc "You had, though."
        "She looks at you for a second and then away, fast."
        nobara "...Yeah. Okay. Thanks."
        "She does not bring it up again. Two days later she buys you lunch and refuses to explain why."
        $ add_bond("nobara", 12)
        $ add_aff("nobara", 6)
        $ advance_thread("nobara_saori", 3)
        $ flag("will_remember_nobara")

    ## ------------------------------------------------------------------ Maki
    elif who == "maki":
        maki "You remember what I said about going back to that house."
        mc "Stand in the middle of it and make them look at you."
        maki "That's the plan, yes. It's still a bad plan."
        maki "I've been thinking about the part I never worked out, which is what happens after they look."
        maki "Because they'll look, and they'll say something clever, and then I'll be standing in a room in that house being a Zenin again."
        maki "That's the bit that frightens me. Not the fight. The four seconds after it."
        "She is cleaning a blade that does not need cleaning, which is what she does instead of pausing."
        maki "So I need somebody in the room who isn't one of them. Who'll be looking at me the whole time."
        maki "Not to help. If you help, they win. Just — to be the reason I'm still me when I walk out."
        menu:
            "It has cost her a great deal to arrange those words in that order."
            "\"I'll be there.\"":
                mc "I'll be there. I won't lift a finger and I won't take my eyes off you."
                maki "..."
                maki "Good."
                "She goes back to the blade. Four or five minutes later, without looking up:"
                maki "Thank you."
                "It is, as far as you can establish, the first time she has said it to anyone at this school."
                $ add_bond("maki", 12)
                $ add_aff("maki", 6)
            "\"Why me?\"":
                maki "Because Mai will be there, and Mai is the only other person alive who knows what that house did."
                maki "And she'll be on their side of the room."
                maki "So I need one person on mine who understands it and isn't obliged to."
                mc "Then I'll be there."
                maki "I know. I'd worked that out. I wanted to hear it."
                $ add_bond("maki", 14)
                $ add_aff("maki", 8)
        $ advance_thread("maki_zenin", 3)
        $ flag("will_stand_with_maki")

    ## ----------------------------------------------------------------- Panda
    elif who == "panda":
        panda "You asked me a question a while back and I said come back in a few months."
        panda "It's been a few months."
        "He has brought coffee, which is how Panda opens anything difficult."
        panda "I've got a name for her."
        panda "I'm not going to tell you what it is yet, because I've only just decided and if I say it out loud today it'll be a thing I decided today."
        panda "I want it to be a thing I've known for a while first. Does that make sense?"
        mc "Completely."
        panda "Right. Good. Here's the actual ask."
        panda "When I do say it — I want you to use it. Out loud, normally, like she's someone we both know."
        panda "Because right now she's a core in a corpse and a thing Yaga did once. And the second two people are calling her a name, she's a person who didn't get a go."
        panda "That's — yeah. That's the difference. Two people is the difference."
        "He drinks his coffee. You drink yours."
        panda "Anyway. Sorry. Very heavy for a Tuesday."
        $ add_bond("panda", 12)
        $ advance_thread("panda_made", 2)
        $ flag("panda_named_her")

    ## ------------------------------------------------------------------ Toge
    elif who == "toge":
        "He hands you the phone with a message already typed, which is how you know it is serious. He usually types in front of you."
        "{i}There's a hearing next month about whether Cursed Speech users should be registered separately. I'm allowed to attend. I'm not allowed to speak — obviously.{/i}"
        "{i}They'll have someone from the clan speak for me. He's never met me.{/i}"
        "{i}Come and speak instead.{/i}"
        mc "I've been here about a month, Toge. They'll ignore me."
        "He takes the phone back and types for a while."
        "{i}Yes. But they'll ignore someone who knows me, instead of listening to someone who doesn't.{/i}"
        "{i}That's the entire difference and it's the only one available to me.{/i}"
        "He pulls the collar down. He does this perhaps twice a month, and never carelessly."
        toge "Please."
        "The word goes through you the way his words do — not a command, this one, just a whole person's worth of asking, delivered at close range."
        mc "Yes."
        toge "Salmon."
        toge "Salmon salmon."
        $ add_bond("toge", 14)
        $ advance_thread("toge_voice", 2)
        $ flag("will_speak_for_toge")

    ## ----------------------------------------------------------------- Shoko
    elif who == "shoko":
        shoko "Administrative question. Extremely boring. Say no if you want."
        shoko "Every member of staff files an emergency contact. Mine has been blank for eleven years."
        shoko "Not because there's nobody. Because the honest answer was Satoru, and putting Satoru on a form felt like a joke I'd have to explain."
        mc "And now?"
        shoko "Now Yaga's doing an audit and the blank is going to become a conversation."
        "She turns the form round on the desk. There is one empty line on it."
        shoko "It's not a big thing. It means someone rings you if I'm on my own table."
        mc "That is a big thing."
        shoko "...Yes. All right. It's a big thing."
        "You write your name on the line. She looks at it for slightly too long and then files it without comment."
        shoko "Right. Get out, I've got actual work."
        "You are almost through the door when she says, to the paperwork rather than to you:"
        shoko "It's the first one that isn't a joke I'd have to explain. So. Thanks."
        $ add_bond("shoko", 12)
        $ add_aff("shoko", 6)
        $ advance_thread("shoko_remembers", 2)
        $ flag("shoko_emergency_contact")

    ## ------------------------------------------------------------------ Gojo
    elif who == "gojo":
        "Gojo asks you for something exactly once, and he does it so lightly that you almost miss that it was an ask."
        gojo "Say I'm wrong about something."
        mc "...What?"
        gojo "Anything. Pick a thing. Say 'Gojo-sensei, that's wrong,' and then tell me why."
        mc "Is this a test?"
        gojo "Everything's a test, that's not the interesting part."
        gojo "The interesting part is that nobody's done it in about six years."
        gojo "Not because I'm always right — I'm frequently not, I'm just always {i}louder{/i}. And at some point the loudness started doing the work, and people stopped checking."
        gojo "That's how Suguru happened, by the way. Not the whole of it. But a piece of it is that nobody in this building was in the habit of telling either of us we were wrong."
        "It is the first time he has said that name to you without decorating it."
        gojo "So. Get in the habit. Start now, while it's cheap and I'm in a good mood."
        menu:
            "He is eating something and pretending this is nothing."
            "\"You should have come sooner. In the corridor.\"":
                mc "Four minutes earlier and Sana wouldn't have a bruise she can't explain."
                gojo "..."
                gojo "Yes."
                gojo "That's correct, and I've thought about it, and I decided the version where I arrive on time is worse for you long-term."
                gojo "Which is a monstrous thing to decide about somebody else's friend, and I did it in about a second and a half, and I'd probably do it again."
                gojo "See — that's useful. Say more things like that."
                $ add_bond("gojo", 14)
                $ flag("told_gojo_wrong")
            "\"You're wrong that being the strongest is the problem.\"":
                mc "You keep saying you're never in a room where somebody needs you to be a person."
                mc "You're in one now. You've been in one for about a month. You just don't count it, because we're students."
                gojo "..."
                gojo "Huh."
                "He does not have an answer. It goes on long enough to become genuinely uncomfortable."
                gojo "Right. Yes. Noted. I'm going to go and be annoyed about that for a while."
                $ add_bond("gojo", 16)
                $ flag("told_gojo_wrong")
        $ advance_thread("gojo_measure", 2)

    ## ------------------------------------------------------------------ Yaga
    else:
        yaga "Sit down. This is not about your training."
        yaga "Itadori is going to be executed. You know this. Everyone in this school knows it and behaves as though it is weather."
        yaga "Gojo has a plan. Gojo always has a plan, and his plans require him to be present, and he is the single most frequently-absent man in this profession."
        "He puts down the thing he is working on, which he does not do."
        yaga "If I am not here, and Gojo is not here, there will be a day when somebody has to stand between that boy and a room full of people with a mandate."
        yaga "It will not be a fight. Fights are easy. It will be a room, and forms, and adults being reasonable at him."
        yaga "I am asking you to be in that room."
        mc "I'm a first-year."
        yaga "You will not always be a first-year."
        yaga "And I am not asking the sorcerer. I am asking the person who walked into a condemned building for a girl who was never going to remember it."
        yaga "That person is the correct one for the room. I have been doing this for a long time and I am rarely wrong about which person is correct for which room."
        mc "...All right."
        yaga "Good."
        yaga "Now get out. And do the ordinary thing with them this week — all of you, together, whatever it is. That is not sentiment, it is the load-bearing part."
        $ add_bond("yaga", 14)
        $ flag("yaga_asked_for_itadori")

    $ gain("insight", 3)
    return
