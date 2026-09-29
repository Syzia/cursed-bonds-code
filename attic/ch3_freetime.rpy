################################################################################
## Chapter Three — Three Boring Afternoons
################################################################################

label chapter_three:

    scene bg black
    with None

    show screen chapter_card("CHAPTER THREE", "Three Boring Afternoons", "Gojo's homework.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    $ ft_slots = 3
    $ ft_used = set()
    $ ft_day = 1

    scene bg courtyard
    with fade_slow

    "Three days. No lessons, no schedule, and a principal who made it very clear that 'unsupervised' is not the same as 'unobserved'."

    mcthink "Three afternoons to work out who these people are before one of us has to trust the others in the dark."

    mcthink "No pressure."

label ft_loop:

    python:
        _labels = {
            "yuji":   ("Yuji Itadori",   "Loud. Constant. Hiding something."),
            "megumi": ("Megumi Fushiguro", "Says four words. Means eleven."),
            "nobara": ("Nobara Kugisaki",  "Will not be pitied. Will pity you."),
            "maki":   ("Maki Zenin",       "Offered you a standing appointment."),
            "panda":  ("Panda & Toge",     "The second-years who actually check on people."),
        }
        _opts = []
        for _k in ["yuji", "megumi", "nobara", "maki", "panda"]:
            _t, _s = _labels[_k]
            _opts.append(dict(
                id=_k,
                title=_t,
                sub=(_s if _k not in ft_used else "Already spent an afternoon here."),
                color=CAST[_k]["color"],
                image=_k,
                meter=bonds[_k],
                enabled=(_k not in ft_used),
            ))
        _opts.append(dict(
            id="train",
            title="Train alone",
            sub="Cursed energy control. Nobody to talk to.",
            color="#a259ff",
            image="mc",
            meter=ce,
            enabled=True,
        ))
        _day_label = "Day %d of 3" % ft_day

    $ quick_menu = False
    call screen free_time(_opts, ft_slots, _day_label)
    $ quick_menu = True

    $ _pick = _return
    $ ft_used.add(_pick)
    $ ft_slots -= 1
    $ ft_day += 1

    call expression "ft_" + _pick

    if ft_slots > 0:
        jump ft_loop

    scene bg dorm
    with fade_slow

    "Three afternoons, spent."

    "You lie on a bed in a dormitory in a mountain that is also Tokyo, and you do the arithmetic on what you have learned about four people in seventy-two hours, and it comes out to almost nothing."

    mcthink "Almost."

    mcthink "But not nothing."

    "In the morning, a car comes."

    scene bg black
    with fade_slow

    return


################################################################################
## Hangouts
################################################################################

label ft_yuji:

    scene bg rooftop
    with fade_slow

    show yuji at pos_cr
    show mc at pos_l
    with dissolve

    "You find Itadori on the roof of the dormitory block, doing push-ups, badly, while eating."

    yuji "You want one? They're the strawberry ones. They're objectively the best ones and Megumi is objectively wrong."

    mc "It's four in the afternoon."

    yuji "Yeah, that's when they're best."

    "He rolls onto his back and squints up at you, and for a second the constant motion of him stops."

    yuji "You did really good yesterday. With Maki-san. I meant to say."

    mc "I got hit with a stick."

    yuji "You got hit with a stick {i}on purpose{/i}, which is completely insane, and also I'd have done the same thing."

    yuji "That's how I know you're going to be okay here."

    menu:
        "He's smiling. He's been smiling since you walked up here."

        "\"You asked me to ask again in a couple of weeks. It's been three days.\"":
            $ add_bond("yuji", 12)
            $ flag("yuji_told_truth")
            "The smile doesn't go anywhere. It just... stops being in front of anything."
            yuji "Yeah. I did say that."
            "He sits up properly. He looks out at the mountains instead of at you."
            yuji "There's a curse. A really old one. Sukuna. He's — he was a person, a long time ago, and then he was something else, and there were twenty fingers of him left in the world."
            yuji "I ate one."
            mc "You {i}ate{/i} one."
            yuji "To save somebody. It was that or watch it happen. So, yeah, I ate a mummified finger, and now he lives in here."
            "He taps his own chest, twice, the way you'd knock on a door you didn't want opened."
            yuji "He talks to me. He's very funny and he wants everyone I love to die."
            yuji "They were going to execute me. Gojo-sensei got it postponed. Not cancelled — {i}postponed{/i}, until I've eaten all twenty."
            "The wind goes across the roof."
            mc "...Why are you telling me this on day three?"
            yuji "Because on day thirty it'd be a betrayal that I hadn't."
            yuji "And because you're going into a building with me next week and you deserve to know what's in there with us."
            "He looks over. The grin comes back on, and this time you can see exactly how much it costs him to put it on."
            yuji "Also because you didn't laugh when I said the whale thing. That was huge for me, honestly."

        "\"Why do you keep checking on people?\"":
            $ add_bond("yuji", 8)
            $ add_bond("megumi", 3)
            $ flag("yuji_kindness")
            yuji "Huh?"
            mc "You've asked Kugisaki if she ate today. Twice. You asked Fushiguro if his shoulder was okay and he said it was fine and you got him ice anyway."
            mc "You've known me for seventy-two hours and you brought me candy."
            yuji "...Is that weird? That's weird, isn't it."
            mc "It's not weird. I'm asking why."
            "He thinks about it. It takes him longer than you expected."
            yuji "My grandpa died last year. Last thing he ever said to me was to help people. Save as many as I can. So that when I go, I'm surrounded."
            yuji "And I said okay, because you say okay."
            yuji "But then I actually started {i}doing{/i} it and it turns out most of it isn't dramatic? Most of it's, like — did you eat. Is your shoulder okay. Here's a strawberry one."
            yuji "The dramatic part's easy. Anyone can do the dramatic part once."

        "\"Teach me to throw a punch.\"":
            $ add_bond("yuji", 9)
            $ add_ce(6)
            $ flag("yuji_trained")
            yuji "Oh, {b}yes.{/b} Yes. Finally."
            yuji "Okay, stand up. No — stand up {i}properly{/i} —"
            "For ninety minutes, Yuji Itadori teaches you to hit things, and he is a startlingly good teacher, because he explains every single thing twice, in two different ways, without ever once making you feel stupid."
            yuji "It's not your arm. Everyone thinks it's the arm. It's the back foot."
            yuji "The back foot decides how much of you is in it."
            "Somewhere around the sixtieth repetition you stop thinking about your hands."
            yuji "There! That one! Did you feel that one?"
            mc "That one felt different."
            yuji "That one {i}was{/i} different. Do it four thousand more times and it'll be yours."

    "By the time the sun goes down, the strawberry ones are gone and your knuckles hurt and you have learned exactly one thing about Yuji Itadori."

    mcthink "He is the least complicated person I have ever met, and there is something enormous underneath him, and he carries it around at full sprint so nobody has to see it."

    return


label ft_megumi:

    scene bg forest
    with fade_slow

    show megumi at pos_cr
    show mc at pos_l
    with dissolve

    "Fushiguro is forty minutes into the treeline behind the school, alone, doing nothing at all."

    "That is not a figure of speech. He is standing still with his eyes closed, and has been for some time."

    megumi "You followed me."

    mc "You walked past me very slowly and made eye contact. That's an invitation."

    megumi "...Fine. It was."

    "He doesn't open his eyes."

    megumi "Shadow work. My technique uses my own shadow as a container. If I'm sloppy about the boundary, things come out that I didn't ask for."

    megumi "So I stand still and I find the edge of myself. It's boring. Do it anyway."

    menu:
        "Ten minutes of silence. He hasn't told you to leave."

        "Stand there with him. Don't talk.":
            $ add_bond("megumi", 12)
            $ add_ce(7)
            $ flag("megumi_silence")
            "You stand there."
            "It is, for the first four minutes, unbearable. Your brain offers you eleven conversation topics and you decline all of them."
            "At minute six, something changes."
            if technique == "aftersound":
                "The forest starts playing itself back to you — an hour of wind, a deer, a boy standing very still for a very long time, over and over, every day this week."
                mcthink "He comes here every day."
            elif technique == "filament":
                "Your threads drift out on their own and find the trees, the roots, the cold seam of water under the hill."
                mcthink "It's the first time I've used it without being terrified."
            else:
                "The heat under your sternum stops straining outward and just... sits there, banked, patient."
                mcthink "Oh. It doesn't have to be a fire. It can be a stove."
            "At minute twenty Megumi opens his eyes."
            megumi "You didn't talk."
            mc "You were working."
            megumi "Everyone talks. Itadori talks {i}more{/i} when I'm doing this, I think as a joke, I've stopped being sure."
            "He picks his bag up off the ground."
            megumi "Same time tomorrow, if you want. I'm not going to invite you again, so just come or don't."
            "From Megumi Fushiguro, you are beginning to understand, that is roughly a declaration of eternal friendship."

        "\"What do you actually want out of all this?\"":
            $ add_bond("megumi", 9)
            $ flag("megumi_philosophy")
            "His eyes open."
            megumi "That's a big question for day three."
            mc "I've had a strange week."
            megumi "..."
            megumi "I don't think I want to save everyone. I've never said that out loud."
            megumi "Itadori wants to save everyone. Gojo-sensei wants to build a generation that can. Kugisaki wants to live somewhere with a decent department store, which is honestly the healthiest answer."
            megumi "I want good people to have more of an outcome than bad people. That's it. That's the whole thing."
            mc "Who decides who's good?"
            megumi "I do. Badly. Constantly."
            megumi "That's the part that keeps me up."
            "He says it flatly, like a weather report about himself."
            megumi "If you ever see me deciding somebody isn't worth it, and you think I'm wrong — say so. Out loud. Immediately."
            megumi "Don't be polite about it. Politeness is how people like me get away with things."

        "\"Show me the shadow thing.\"":
            $ add_bond("megumi", 6)
            $ add_ce(4)
            $ flag("megumi_demo")
            megumi "It's not a party trick."
            mc "I've been a sorcerer for eight days. Everything is a party trick to me."
            "That, unexpectedly, gets something out of him that is almost a laugh."
            megumi "...Fine."
            "He makes a shape with his hands. His shadow on the leaf-litter goes deep in a way shadows should not, and two white dogs come out of it like they're stepping over a threshold."
            "They are perfectly, ordinarily real. One of them sniffs your knee."
            mc "That's the most beautiful thing I've ever seen."
            megumi "It's a search-and-flush pair. They're for hunting."
            mc "Fushiguro, it's the most beautiful thing I've ever seen."
            megumi "...Thank you."
            "He scratches the white one behind the ear when he thinks you aren't looking."

    "You walk back down the mountain in a silence that is somehow companionable."

    mcthink "He talks like he's rationing it. Every sentence he spends, he's decided you were worth the cost."

    return


label ft_nobara:

    scene bg city
    with fade_slow

    show nobara at pos_cr
    show mc at pos_l
    with dissolve

    "You do not choose to spend the afternoon with Kugisaki. Kugisaki informs you that you are spending the afternoon with her, and then a train happens."

    nobara "Rule one: if you say the word 'budget' I'm leaving you in Harajuku."

    nobara "Rule two: you're carrying the bags on the way back, because I carried Itadori's the last time and he thanked me for it, which was somehow worse."

    "By the fourth shop you have stopped protesting. It is, and you would not admit this under interrogation, the first time in nine days that nothing has been trying to kill you."

    nobara "So. You've got the face."

    mc "What face?"

    nobara "The 'is this allowed' face. Everybody gets it in the first fortnight."

    menu:
        "She's not wrong. You've been carrying something around all week."

        "\"How do you go shopping three days before a mission?\"":
            $ add_bond("nobara", 12)
            $ flag("nobara_philosophy")
            nobara "Oh, we're doing this one already? Fine, sit down, I'll do the speech."
            "She sits on a step outside a shop and pats the concrete next to her, and you sit."
            nobara "I grew up in a village of two hundred people that decided what I was when I was six and never revised it."
            nobara "I got out. And the deal I made with myself when I got out was: I'm going to like my life. Out loud. On purpose. Where people can see it."
            nobara "So I buy the coat. I get the nails done. I eat the expensive one."
            nobara "Because in four days something is going to try very hard to make me stop existing, and I refuse — {i}refuse{/i} — to have spent the week before that being sensible."
            mc "That's not what I expected."
            nobara "What did you expect?"
            mc "Something about not thinking about it."
            nobara "God, no. I think about it constantly. That's the whole point."
            nobara "You don't buy a coat you love because you forgot you might die. You buy it because you remembered."

        "\"Does it get easier? Seeing them?\"":
            $ add_bond("nobara", 9)
            $ add_bond("yuji", 3)
            $ flag("nobara_honest")
            "She stops walking."
            nobara "No."
            nobara "It gets {i}familiar.{/i} That's different, and don't let anyone tell you it isn't."
            nobara "First one I saw properly, I was eleven. It was standing over somebody I liked and it had her by the hair."
            nobara "And I remember thinking — very clearly, like reading a sign — {i}oh, so this is what the adults have been not-telling us about.{/i}"
            nobara "I didn't get scared. I got {b}furious{/b}. Still am. That's the engine."
            nobara "You'll find out what yours is. Everybody's got a different one and they all work fine, right up until they don't."

        "\"...Why me? You could have taken any of them.\"":
            $ add_bond("nobara", 10)
            $ flag("nobara_chose_you")
            nobara "Because Itadori would've enjoyed it too much and Fushiguro would've stood in the corner like a coat rack."
            nobara "And because when Maki-san knocked you over, you got up and you didn't apologise for it."
            nobara "People here apologise constantly. For being new, for being scared, for taking up space."
            nobara "You didn't. I decided on the spot that I liked you and now you're stuck."
            mc "That's it? That's the whole assessment?"
            nobara "That's the whole assessment. I'm extremely decisive, it's one of my best qualities."
            "She hands you two of the bags without breaking stride."
            nobara "Also you're tall enough to reach the top shelf, which frankly did most of the work."

    scene bg city
    with slowdissolve

    "You get back to the school after dark, loaded like a pack animal, and Kugisaki is still talking, and you realise with mild horror that you have been laughing for about an hour."

    mcthink "She decided I was worth the effort in under a week, and she'll never bring it up again, and she'd be furious if I thanked her."

    return


label ft_maki:

    scene bg training
    with fade_slow

    show maki at pos_cr
    show mc at pos_l
    with dissolve

    "Maki does not do conversation. Maki does repetitions, and if you happen to be in the room, conversation occasionally falls out."

    maki "Again."

    maki "Again."

    maki "You're dropping your left shoulder when you get tired. Which is fine. Everyone does."

    maki "It's just that everything that's ever going to kill you will also notice."

    "Two hours. You have hit a post four hundred times and you have stopped being able to feel your forearms."

    menu:
        "There's a break. She's drinking water and looking at nothing."

        "\"You don't have cursed energy at all, do you.\"":
            $ add_bond("maki", 12)
            $ flag("maki_truth")
            "The bottle stops halfway down."
            maki "Who told you."
            mc "Nobody. You've never once used it, and you talk about technique like it's someone else's hobby."
            maki "...Heavenly Restriction. I was born with almost none. In exchange I got a body that does things bodies aren't supposed to."
            maki "In the Zenin clan, that makes you furniture. They had me serving tea to men who'd never won a fight in their lives, because they had a technique and I didn't."
            maki "So I left, and I came here, and I decided I'd get strong enough that they'd have to look at me."
            mc "And when they do?"
            maki "Then they look at me. That's it. That's the whole plan. It's a bad plan."
            maki "It's kept me upright for four years, so I've stopped auditing it."
            "She screws the cap back on the bottle."
            maki "You're the first person to work it out without being told. Everyone else here got told."
            maki "That's a compliment, so don't make me say another one."

        "\"Why did you agree to train me?\"":
            $ add_bond("maki", 9)
            $ add_ce(5)
            $ flag("maki_reason")
            maki "You took the hit."
            mc "That was stupid."
            maki "Extremely. But stupid I can work with. Stupid means you'll do the boring part."
            maki "Everyone in this school has a technique that makes them feel special, and the second they feel special they stop doing the boring part."
            maki "Then they meet something that doesn't care how special they are."
            maki "I've buried people who were more talented than you'll ever be. All of them could do something amazing once."
            maki "None of them could do something adequate four hundred times."
            maki "Pick up the stick."

        "\"Teach me something that isn't hitting.\"":
            $ add_bond("maki", 7)
            $ add_ce(9)
            $ flag("maki_positioning")
            maki "Finally. Yes."
            "She takes you into the middle of the hall and puts you in the centre of it and then goes and stands somewhere else."
            maki "Where's the door?"
            mc "Behind me."
            maki "Don't look."
            maki "Where's Itadori standing?"
            mc "He's not — he's not in the room."
            maki "He was ten minutes ago. Where was he."
            "You have to think about it. That is, apparently, the point."
            maki "Every fight you'll ever be in, you'll have about a second and a half of actual thinking. You spend it on {i}what do I do{/i}, you're dead."
            maki "You spend it on what to do, because you already knew where everyone was — that's the whole job."
            maki "Walk into every room from now on and name three exits before you sit down."
            maki "Do it for a year. Then it's free."

    "You limp back to the dormitory at nine, and you have never been this tired, and you are already planning tomorrow."

    return


label ft_panda:

    scene bg dorm
    with fade_slow

    show panda at pos_cl
    show toge at pos_cr
    with dissolve

    "There is a knock on your door at eight in the evening, and it is a panda holding two cans of coffee and a bag of crisps, and behind him is Toge Inumaki holding nothing and looking mildly apologetic about it."

    panda "Welfare check. Sit down, you look like a rumour."

    mc "I'm fine."

    panda "Right, sure. How many nights have you actually slept since the corridor?"

    "You open your mouth. You close it."

    panda "Yeah. That's what I thought. Inumaki, I told you."

    toge "Bonito flakes."

    panda "He says he told me first, which is a lie."

    menu:
        "The panda has sat down on your floor and is opening the crisps like this is his room."

        "\"Does it stop? The being scared?\"":
            $ add_bond("panda", 11)
            $ add_bond("toge", 8)
            $ flag("panda_fear")
            panda "Nope."
            panda "Sorry. I could dress that up but you'd notice."
            panda "What happens is you get better at doing things {i}while{/i} scared, and after a while that looks so much like courage that even you start believing it."
            toge "Salmon."
            panda "Inumaki says the first year is the worst, and he's right, and he'd know."
            panda "He couldn't talk for two months when he got here. Not couldn't — {i}wouldn't{/i}. His technique means every word he says lands on somebody."
            panda "Imagine being fifteen and finding out you can hurt people by getting frustrated."
            toge "Tuna."
            panda "He says he's fine now. He is, mostly. But that's what I mean — nobody here stopped being scared. We just built stuff around it."

        "\"What are you? Actually?\"":
            $ add_bond("panda", 9)
            $ flag("panda_origin")
            panda "Straight in! I like that. Everyone dances around it for a month."
            panda "I'm a cursed corpse. Principal Yaga made me. He makes them — cursed objects with a soul bolted in, basically."
            panda "Difference is most cursed corpses get an order and follow it. I got a personality and a school uniform."
            mc "So you're... his?"
            panda "I'm {i}mine.{/i} That's actually the interesting part."
            panda "He built something that could tell him no. On purpose. Then he had to sit there and find out whether it would."
            panda "That's parenting, near as I can tell. Never having done it. Being it."
            toge "Mustard leaf."
            panda "He says I get sentimental after nine PM. He's not wrong and I don't appreciate it."

        "\"Thank you for coming.\"":
            $ add_bond("panda", 8)
            $ add_bond("toge", 10)
            $ flag("panda_thanks")
            "Panda pauses with a crisp halfway to his mouth."
            panda "...Huh."
            panda "Nobody says that. Everyone says 'I'm fine' and then eats all my crisps."
            "Inumaki says something you don't catch, and Panda looks at him for a long moment."
            panda "He says — okay, I'm translating loosely — he says that when he got here, the second-years did this for him. Came round at eight with food and no questions."
            panda "And he decided that when it was his turn he'd do it right, because the version where nobody comes is really, really long."
            toge "Salmon salmon."
            panda "That one means it, by the way. He doubles them when he means it."
            "You will remember that. Later, in the dark, it will matter."

    "They stay until midnight. Nobody asks you a single thing about the East Wing."

    mcthink "That was the point. That was the entire point."

    "You sleep, that night, for six unbroken hours. It's the most anyone has given you all week."

    return


label ft_train:

    scene bg forest
    with fade_slow

    show mc at pos_c
    with dissolve

    "You take the afternoon alone, up the ridge behind the school, where nobody will see you be bad at this."

    "Cursed energy, according to the one textbook Ijichi gave you, is generated by negative emotion and refined by control. The book is four hundred pages long and says almost nothing else."

    mcthink "Fine. Do it the stupid way. Do it until it's not stupid."

    if technique == "filament":
        "You throw threads. Hundreds of them, thousands, at trees and stones and the empty air, and you get almost all of them wrong."
        "Then, around the third hour, one goes exactly where you meant it to go, and you understand — physically, in your hands — the difference between {i}reaching{/i} and {i}aiming{/i}."
        "You do it eleven more times. Nine of them work."
    elif technique == "emberfall":
        "You put your hand flat on a stone and hold heat in it until the stone is too hot to touch."
        "Then you do it again while running. Then again while off balance. Then again while thinking about something else, which turns out to be the hardest one by an enormous margin."
        "By evening the ridge is dotted with warm stones, and you can hold a burn in something for a full four minutes without watching it."
    else:
        "You sit and let the ridge replay itself."
        "Deer. Wind. A hiker, two days ago. A second-year running this path every morning at 5:40, over and over, layered a hundred deep."
        "The trick, you learn, is not hearing more. The trick is hearing {i}less{/i} — choosing one layer out of the hundred and letting the rest go quiet."
        "By evening you can pick a single minute out of a week."

    $ add_ce(14)

    "You come down the mountain in the dark, shaking, empty, and better than you were."

    mcthink "Nobody saw that. Nobody's going to know."

    mcthink "Which is fine. That wasn't for them."

    return
