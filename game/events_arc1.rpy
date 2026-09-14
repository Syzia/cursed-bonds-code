################################################################################
## Cursed Bonds — Arc 1 events.
##
## Registration first, then the scenes themselves. `ev()` arguments decide when
## a scene becomes available; the scene never checks conditions itself.
################################################################################

init 1 python:

    ## --- first time you really talk to someone ---------------------------------
    ev("ev_yuji_1",   who="yuji",   thread=("yuji_countdown", 1))
    ev("ev_megumi_1", who="megumi", thread=("megumi_tsumiki", 0))
    ev("ev_nobara_1", who="nobara", thread=("nobara_saori", 0))
    ev("ev_maki_1",   who="maki",   thread=("maki_zenin", 0))
    ev("ev_panda_1",  who="panda",  thread=("panda_made", 0))
    ev("ev_toge_1",   who="toge",   thread=("toge_voice", 0))
    ev("ev_shoko_1",  who="shoko",  thread=("shoko_remembers", 0))

    ## --- once they actually trust you -----------------------------------------
    ev("ev_yuji_2",   who="yuji",   min_bond=35, thread=("yuji_countdown", 2))
    ev("ev_megumi_2", who="megumi", min_bond=35, thread=("megumi_tsumiki", 2))
    ev("ev_nobara_2", who="nobara", min_bond=35, thread=("nobara_saori", 1))
    ev("ev_maki_2",   who="maki",   min_bond=35, thread=("maki_zenin", 2))
    ev("ev_shoko_2",  who="shoko",  min_bond=35, thread=("shoko_remembers", 1))

    ## --- romance: gated behind affection, which is itself gated behind bond ---
    ev("ev_nobara_r1", who="nobara", min_bond=50, min_aff=20)
    ev("ev_maki_r1",   who="maki",   min_bond=50, min_aff=20)
    ev("ev_shoko_r1",  who="shoko",  min_bond=50, min_aff=20)

    ## --- bond 60: the threads pay off -----------------------------------------
    ev("ev_yuji_3",   who="yuji",   min_bond=60, thread=("yuji_countdown", 3))
    ev("ev_megumi_3", who="megumi", min_bond=60, thread=("megumi_tsumiki", 3))
    ev("ev_nobara_3", who="nobara", min_bond=60, thread=("nobara_saori", 3))
    ev("ev_shoko_3",  who="shoko",  min_bond=60, thread=("shoko_remembers", 2))
    ev("ev_panda_2",  who="panda",  min_bond=35, thread=("panda_made", 2))
    ev("ev_toge_2",   who="toge",   min_bond=35, thread=("toge_voice", 2))

    ## --- the two who had nothing ----------------------------------------------
    ev("ev_gojo_1",   who="gojo",   min_bond=20, thread=("gojo_measure", 1))
    ev("ev_yaga_1",   who="yaga",   min_bond=20)
    ev("ev_gojo_2",   who="gojo",   min_bond=40)
    ev("ev_yaga_2",   who="yaga",   min_bond=40)

    ## --- the arc's story mission ----------------------------------------------
    ev("ev_mission_sunmall", kind="mission", loc="office", min_day=8,
       requires=("settled_in", "roll_call"), priority=100)
    ev("ev_patrol", kind="mission", loc="office", once=False,
       requires=("mission_board_open",))

label ev_yuji_1:

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
            $ gain(tech()["scales"], 6)
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

label ev_megumi_1:

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
            $ gain(tech()["scales"], 7)
            $ flag("megumi_silence")
            "You stand there."
            "It is, for the first four minutes, unbearable. Your brain offers you eleven conversation topics and you decline all of them."
            "At minute six, something changes."
            if technique == "timestop":
                "You hold a second, out of curiosity, with nothing in it to escape."
                "The forest stops. The wind stops. Megumi stops, mid-breath, exactly as still as he was already trying to be."
                mcthink "He was almost there on his own."
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
            $ gain(tech()["scales"], 4)
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

label ev_nobara_1:

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

label ev_maki_1:

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
            $ gain(tech()["scales"], 5)
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
            $ gain(tech()["scales"], 9)
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

label ev_panda_1:

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


################################################################################
## New Arc 1 scenes
################################################################################

label ev_toge_1:

    scene bg rooftop with fade_slow
    show toge at pos_cr
    show mc at pos_l
    with dissolve

    "Inumaki is on the roof with his hood up and his phone out, and he lifts two fingers when he sees you, which you have learned means {i}sit down{/i}."

    toge "Salmon."

    "He turns the phone around. He has typed: {i}you look like you're deciding whether to ask me something.{/i}"

    mc "...Yeah."

    mc "How do you do it? A whole conversation, six words."

    "He types for a while."

    "{i}I don't. You do. I say salmon, you do the rest. Everyone thinks they're translating me. They're mostly just telling me what they already thought.{/i}"

    mc "That sounds lonely."

    toge "..."

    "{i}Sometimes. But when I say a real word it lands like a hammer, so I got careful, and careful turned out to be a whole personality.{/i}"

    menu:
        "He's watching you read it."

        "\"Say a real one. To me. On purpose.\"":
            $ add_bond("toge", 12)
            $ flag("toge_spoke")
            "He goes very still."
            "Then he pulls the collar down, and looks at you, and says — quietly, carefully, aiming it at nothing:"
            toge "Hello."
            "It hits you in the chest like a hand pushing you gently backwards. Not a command. Just a word with a whole person's cursed energy behind it."
            mc "...Hi."
            "He pulls the collar back up, and you can see the corners of his eyes go, and that's how you learn what Toge Inumaki laughing looks like."

        "\"Then I'll learn the six words properly.\"":
            $ add_bond("toge", 9)
            $ flag("toge_learning")
            mc "Salmon, tuna, tuna mayo, bonito flakes, mustard leaf, kelp. Right?"
            toge "Salmon!"
            mc "That one's yes."
            toge "Salmon salmon."
            mc "And doubling means you mean it."
            "He points at you and then at his own head, which even you can translate."
            "You spend an hour on the roof going through them, and by the end you are wrong about four times in ten, which he indicates is extremely good."

    return


label ev_shoko_1:

    scene bg infirmary with fade_slow
    show shoko at pos_cr
    show mc at pos_l
    with dissolve

    "You come in for a wrist you're fairly sure is fine. Shoko Ieiri looks at it for four seconds and tells you it is not fine."

    shoko "Hairline. Two days of nothing, or ninety seconds of me. Pick."

    mc "...Ninety seconds."

    shoko "Everyone picks ninety seconds."

    "She puts two fingers on your wrist and something green and unbearably warm goes through it, and the pain leaves in a way that feels like it's being politely escorted out."

    mc "That's Reverse Cursed Technique."

    shoko "That's Reverse Cursed Technique."

    mc "I thought almost nobody could do it."

    shoko "Almost nobody can."

    "She lights a cigarette off nothing in particular and does not offer any further information, which is, you are learning, a thing she does."

    menu:
        "She's waiting to see whether you'll push."

        "\"That must be a lot of weight.\"":
            $ add_bond("shoko", 12)
            $ flag("shoko_weight")
            shoko "..."
            shoko "There are four people in the country who can heal other people. I'm one. That's not a brag, it's a duty roster."
            shoko "So when somebody comes back from a mission in pieces, it's me. Every time. There's no rota."
            shoko "And when they come back and it's too late — that's me too. I'm the one who has to say it out loud, because I'm the one who'd know."
            mc "Who does that for you?"
            shoko "..."
            shoko "Huh."
            shoko "You're the first person to ask me that in about eleven years."
            "She doesn't answer it. But she doesn't leave, either, and you sit in the infirmary for another twenty minutes not talking, and it seems to be what she wants."

        "\"Can you teach me?\"":
            $ add_bond("shoko", 8)
            $ gain("insight", 3)
            $ flag("shoko_lessons")
            shoko "No."
            shoko "Not because I'm precious about it. Because RCT is running your cursed energy backwards, and to do that you have to be able to feel the direction it's already going."
            shoko "Most sorcerers can't. You currently cannot."
            shoko "Come back when your control is somewhere respectable and I'll tell you if you're wasting your time."
            "It's not a no. From Shoko Ieiri, apparently, it's practically a syllabus."

    return


label ev_yuji_2:

    scene bg cafeteria with fade_slow
    show yuji at pos_cr
    show mc at pos_l
    with dissolve

    "Itadori has cooked. It is nine in the evening and there is enough food on the table for eleven people and there are two of you."

    yuji "I got carried away. I do that. Eat something."

    "You eat something. It is, annoyingly, excellent."

    yuji "My grandpa taught me. He was in a hospital bed for about two years at the end and he'd talk me through it over the phone."

    yuji "Last thing he ever said to me was — you're strong, so help people. Save as many as you can. Don't die alone like me. Be surrounded."

    "He pushes food around his plate."

    yuji "I say that a lot. 'A proper death, surrounded by people.' I say it like it's a mission statement."

    yuji "Thing is, I've never actually said the other half out loud."

    menu:
        "He's stopped eating."

        "\"Say it.\"":
            $ add_bond("yuji", 14)
            $ flag("yuji_afraid")
            yuji "...I'm going to die before you all."
            yuji "Not maybe. There's a countdown on me and everybody in this school knows the number and nobody says it at dinner."
            yuji "So when I say 'surrounded' — I'm not being noble. I'm asking. I'm asking people to be there, because I already know I'm going first, and I am so scared of doing it in a room by myself."
            "You do not say it's going to be fine, because he would know."
            mc "Then I'll be there."
            yuji "You can't promise that."
            mc "No. I'm doing it anyway."
            "He laughs, wetly, and puts more food on your plate, because that is the only thing he knows how to do with a feeling."

        "\"You don't have to.\"":
            $ add_bond("yuji", 9)
            "He looks up, surprised."
            mc "You've said the noble half about six times since I got here. Every time, to somebody who needed cheering up."
            mc "You're allowed to have a version that isn't for other people's benefit."
            yuji "...Huh."
            yuji "Nobody's ever told me that."
            yuji "I'm going to need, like, a week to think about it. Eat more, I'm not carrying this back."

    return


label ev_megumi_2:

    scene bg forest with fade_slow
    show megumi at pos_cr
    show mc at pos_l
    with dissolve

    "Megumi is sitting on a root instead of standing, which for him is practically lying down."

    megumi "I have a sister. Step-sister. Tsumiki."

    "He says it out of nowhere, forty minutes into a silence, which is how you learn he has been building up to it for forty minutes."

    megumi "She's been asleep for a year. Not a coma — a curse. Nobody can wake her up and nobody can tell me why."

    mc "I'm sorry."

    megumi "Don't. It's not a tragedy yet, it's an unsolved problem. Those are different."

    megumi "She's the reason I said what I said. About good people getting more of an outcome than bad people."

    megumi "Tsumiki is genuinely good. Not nice — good. She'd apologise to furniture. And the world put her to sleep anyway, and it did not put a single one of the people who deserved it to sleep."

    megumi "So I decided I'd be the correction. Manually. Case by case."

    menu:
        "It is the most he has ever said at once."

        "\"That's not a job. That's a sentence.\"":
            $ add_bond("megumi", 14)
            $ flag("megumi_sentence")
            megumi "..."
            megumi "Say that again."
            mc "You've made yourself personally responsible for whether the universe is fair. You're fifteen."
            mc "You're going to fail at that constantly. Not because you're bad at it — because it's not a solvable problem."
            megumi "I know."
            mc "Then what happens the first time you decide wrong?"
            megumi "..."
            megumi "That's the question, isn't it."
            "He's quiet for a long time."
            megumi "Nobody's asked me that. Everyone just says it's admirable."
            megumi "Keep asking me. When it happens, I'd rather it was you."

        "\"Then let me help with Tsumiki.\"":
            $ add_bond("megumi", 11)
            $ flag("tsumiki_promise")
            megumi "You can't. I've had Gojo-sensei look. I've had Ieiri-san look."
            mc "I didn't say I could fix it. I said let me help."
            mc "You've been carrying an unsolved problem alone for a year. That's a different thing from it being unsolvable."
            megumi "..."
            "He doesn't say yes. But three days later a folder appears under your door with everything he has on it, in handwriting so small it's almost a code, and that is Megumi Fushiguro saying yes."

    return


label ev_nobara_2:

    scene bg courtyard with fade_slow
    show nobara at pos_cr
    show mc at pos_l
    with dissolve

    "Kugisaki is sitting on the steps with her shoes off, and she does not look up when you sit down."

    nobara "There was a girl in my village called Saori."

    nobara "City girl. Moved in for about a year. Wore clothes nobody there had the imagination for and did not care even slightly what two hundred people thought about it."

    nobara "She was the only interesting thing that ever happened to that place. So obviously they ran her out."

    mc "What happened?"

    nobara "Nothing happened. That's how it works. Nobody does anything, everybody just... {i}decides{/i} about you, out loud, in shops, for a year, until you go."

    nobara "And I stood there and watched it and I was eleven and I didn't say anything."

    "She turns a nail over and looks at it."

    nobara "So I said — fine. I'm going to Tokyo, and I'm going to like my life so loudly that nobody can decide anything about me."

    menu:
        "She still hasn't looked up."

        "\"Did you ever find her?\"":
            $ add_bond("nobara", 14)
            $ add_aff("nobara", 4)
            $ flag("nobara_saori")
            nobara "No."
            nobara "I look. Every time we're in the city I look at faces like an idiot."
            nobara "I'm going to. That's not hope, that's a plan. Tokyo's big but it's not infinite."
            mc "And when you find her?"
            nobara "Then I tell her that somebody remembered. That's it. That's the whole speech."
            nobara "One person remembering out loud would have changed that entire year for me. So."
            "She finally looks up, and her eyes are dry and absolutely furious, which you now understand is what Nobara Kugisaki looks like when she's sad."

        "\"You were eleven. That wasn't yours to stop.\"":
            $ add_bond("nobara", 10)
            $ add_aff("nobara", 3)
            nobara "Don't."
            nobara "Don't do the reasonable thing. I know it wasn't. I've been told it wasn't by four adults."
            nobara "Knowing that has never once helped, so I've stopped collecting it."
            "She's quiet."
            nobara "What actually helps is doing something about the next one. That's why I'm here. That's the entire reason I'm here."
            nobara "So next time somebody's getting decided about in front of me — I'm the loudest thing in the room."
            mc "You are already the loudest thing in every room."
            nobara "{b}Good.{/b}"

    return


label ev_maki_2:

    scene bg dojo with fade_slow
    show maki at pos_cr
    show mc at pos_l
    with dissolve

    "Two hours of drills and then, without any change in tone, while wiping down a blade:"

    maki "I have a twin. Mai. She's at Kyoto."

    maki "We were born to the Zenin clan, which is a family in the way a company is a family."

    maki "Heavenly Restriction — I got a body that does impossible things and almost no cursed energy. Mai got a little cursed energy and a normal body."

    maki "So they decided we were both failures, and they were only slightly wrong twice."

    mc "What did they do?"

    maki "Nothing dramatic. That's what people never get."

    maki "They just... assigned us. To serve tea. To fetch things for men who'd never won a fight in their lives but had a technique, so they outranked us permanently, by birth, forever."

    maki "Sixteen years of being furniture in your own house."

    "She sets the blade down."

    maki "I left. Mai didn't. She could have. I asked her to."

    maki "She said I was abandoning her by leaving, and I said she was choosing the cage, and we were both right, which is the worst possible way for an argument to go."

    menu:
        "She has never once talked this long."

        "\"You still want her to come.\"":
            $ add_bond("maki", 14)
            $ add_aff("maki", 4)
            $ flag("maki_mai")
            maki "..."
            maki "Every day."
            maki "She hates me. Properly hates me, in public, at the Goodwill Event, where everyone can hear."
            maki "And I'd still take her back in about a second and a half."
            mc "Have you told her that?"
            maki "How would I possibly say that."
            mc "Out loud. Badly. Like you just did to me."
            maki "..."
            maki "That's an annoying answer."
            maki "Pick up the stick."
            "But she doesn't put the blade away for a long while."

        "\"So what happens when you're strong enough?\"":
            $ add_bond("maki", 11)
            $ add_aff("maki", 2)
            maki "I go back."
            maki "Not to burn it down. Everyone assumes I mean burn it down."
            maki "I go back and I stand in the middle of that house and I make every single one of them look at me. That's all. That's the whole revenge."
            maki "Then I take Mai and I leave again, and this time she comes."
            mc "That's not a bad plan."
            maki "It's a terrible plan. It has one step and it's 'become the strongest person alive'."
            maki "But it's mine, and I've never had anything that was."

    return


label ev_shoko_2:

    scene bg rooftop with fade_slow
    show shoko at pos_cr
    show mc at pos_l
    with dissolve

    "Shoko is on the roof at dusk with a cigarette, which she does not hide and does not explain."

    shoko "You know Gojo and I were students here? Same year."

    mc "I did not know that."

    shoko "There were three of us. Me, Satoru, and a boy called Suguru Geto."

    "She says the third name the way you'd set down something heavy."

    shoko "Best in the country. All three of us, at sixteen, absolutely insufferable about it."

    mc "What happened to him?"

    shoko "He decided non-sorcerers weren't people, and he killed a hundred and twelve of them in an afternoon, and now he's the most wanted man alive."

    "She taps ash off the roof edge."

    shoko "Satoru has never once talked about it. Not to me. Not in eleven years."

    shoko "He does the grin, and the sweets, and the — you've seen it. The whole show."

    shoko "And I'm the only person left who was actually there, so I'm the only person who knows the show is a show."

    menu:
        "The cigarette has burned most of the way down and she hasn't drawn on it in a while."

        "\"That's why you're still here.\"":
            $ add_bond("shoko", 14)
            $ add_aff("shoko", 4)
            $ flag("shoko_geto")
            shoko "..."
            shoko "Yeah."
            shoko "I could work anywhere. Do you understand how in-demand a functioning reverse curse user is? I could name a number."
            shoko "I stay because if I go, there's nobody in the building who remembers Satoru as a person instead of as a weather system."
            shoko "Somebody has to be the one who knew him before. Otherwise he just... becomes the myth. All the way through."
            mc "And who remembers you as a person?"
            shoko "..."
            shoko "That is the second time you've done that."
            "She puts the cigarette out."
            shoko "Don't make a habit of it. I'm not built for it."
            "She says it, and then she doesn't leave, and the two of you watch the light go off the mountains."

        "\"He was your friend too.\"":
            $ add_bond("shoko", 11)
            $ add_aff("shoko", 3)
            shoko "He was."
            shoko "Everyone frames it as Satoru's loss. Satoru's tragedy. Satoru's best friend."
            shoko "Suguru used to bring me coffee at four in the morning when I was learning to heal and getting it wrong."
            shoko "Nobody has ever once asked me how I'm doing about it. Eleven years."
            "She lights another one off the first."
            shoko "So. Thanks. That's the most I've said about him since it happened."

    return


################################################################################
## Romance
################################################################################

label ev_nobara_r1:

    scene bg riverside with fade_slow
    show nobara at pos_cr
    show mc at pos_l
    with dissolve

    "She drags you down to the water on a Sunday with a bag she will not let you look in."

    nobara "Sit. Don't talk yet."

    "She produces, in order: two drinks, something wrapped in paper that turns out to be genuinely good, and a scarf, which she throws at your head."

    mc "What's this?"

    nobara "It's a scarf. You've been wearing the same grey thing for a month and it's making me physically unwell."

    "It is, you notice, exactly the colour you would have picked. She has never asked you what colour you would have picked."

    mc "Kugisaki—"

    nobara "Don't make it a whole thing."

    mc "I'm going to make it a small thing."

    nobara "...Fine. One small thing. Go."

    menu:
        "She is looking very hard at the river."

        "\"Thank you. I mean it.\"":
            $ add_aff("nobara", 12)
            $ flag("nobara_scarf")
            "She goes red from the ears inward, which is a process you have never seen before and will be thinking about later."
            nobara "It was on sale."
            mc "It wasn't."
            nobara "It was {b}on sale.{/b}"
            "She hits you with the bag. It's empty. It doesn't hurt at all."
            "Then she sits back down a little closer than she was before, and neither of you mentions that, and the river goes on doing what rivers do."
            nobara "...You're welcome."

        "\"You picked the colour on purpose.\"":
            $ add_aff("nobara", 14)
            $ flag("nobara_noticed")
            "There is a silence with a lot going on inside it."
            nobara "Obviously I picked the colour on purpose. I'm not an animal."
            mc "You've never asked me what colours I like."
            nobara "I didn't need to {i}ask{/i}."
            "She realises what she's said about half a second after she's said it."
            nobara "That's — I notice things. That's a professional skill. That's a {i}sorcery{/i} skill."
            mc "Right."
            nobara "Shut up."
            "She does not, however, move away, and after a while her shoulder ends up against yours and stays there."

    return


label ev_maki_r1:

    scene bg dojo with fade_slow
    show maki at pos_cr
    show mc at pos_l
    with dissolve

    "It's past eleven and the dojo lamps are down to one, and Maki is still working, and so are you, because that is apparently what the two of you are now."

    maki "Enough. Your form's gone."

    "She takes the training blade out of your hands and then, instead of putting it on the rack, turns your wrist over and looks at it."

    maki "You've split these open again."

    mc "It's fine."

    maki "It's the third time. Ieiri's going to start charging you."

    "She wraps them. She does it properly, tightly, without looking up, and it takes much longer than it needs to."

    menu:
        "She hasn't let go of your hand."

        "\"You could have just told me to see Shoko.\"":
            $ add_aff("maki", 13)
            $ flag("maki_hands")
            maki "..."
            maki "Yeah."
            "She still doesn't look up."
            maki "I've had exactly one person in my life who noticed when I was hurt and did something about it without me asking, and she stopped talking to me when I was sixteen."
            maki "So I'm not good at it. The doing-it-for-someone-else part."
            maki "But you keep showing up at dawn and getting knocked over and coming back, and at some point I started — "
            "She stops."
            maki "I started looking for you in the doorway. That's all. That's the whole thing."
            mc "That's not a small thing."
            maki "No."
            maki "It isn't."
            "She finishes the wrapping. She lets go about four seconds after she needs to."

        "\"Maki.\"":
            $ add_aff("maki", 11)
            "She looks up."
            "Neither of you says anything for a while, and the one lamp does what one lamp does, and somewhere outside a bird is having a bad night."
            maki "Don't."
            mc "I wasn't going to."
            maki "You were going to."
            mc "...I was going to."
            maki "..."
            maki "Ask me again when I've won something."
            "It is not a no. It is a date, set at an unspecified point in the future, by the least sentimental person you have ever met, and you decide to treat it as binding."

    return


label ev_shoko_r1:

    scene bg infirmary with fade_slow
    show shoko at pos_cr
    show mc at pos_l
    with dissolve

    "You come in at two in the morning because you cannot sleep, and the light is on, because it always is."

    shoko "You're not injured."

    mc "No."

    shoko "Then you're the good kind of visitor. Sit down."

    "She's doing paperwork. There is an enormous amount of paperwork involved in putting people back together."

    shoko "Can't sleep, or won't?"

    mc "Every time I close my eyes I'm in that corridor."

    shoko "Mm. That doesn't go. I can tell you that honestly or I can be encouraging, and you strike me as someone who'd rather have the first one."

    mc "The first one."

    shoko "Then: it doesn't go. It gets further away. There's a difference and the difference is the whole job."

    "She puts the pen down."

    menu:
        "It's two in the morning and neither of you is going anywhere."

        "\"How do you sleep?\"":
            $ add_aff("shoko", 13)
            $ flag("shoko_night")
            shoko "Badly. Rarely. Usually here."
            shoko "I've got a flat in the city I've been in maybe nine times."
            mc "That's not sustainable."
            shoko "No. It's been unsustainable for eleven years. At some point unsustainable just becomes what you do."
            "She looks at you for a while."
            shoko "You keep asking me questions about me. Do you know how rare that is, in a building full of people who need something from me?"
            shoko "You come in at two in the morning and you don't want to be healed. You just want to sit."
            shoko "...Stay, if you want. I've got about four hours of this left."
            "You stay. She works. Neither of you says much."
            "You fall asleep in the chair around four, and when you wake up there's a blanket on you and she is pretending very hard to have not done it."

        "\"Tell me something that isn't about the job.\"":
            $ add_aff("shoko", 11)
            shoko "...Huh."
            shoko "Give me a second, I might not have one."
            "She thinks about it for genuinely a whole minute."
            shoko "I can't cook. At all. Catastrophically. Satoru once watched me ruin rice and had to sit down."
            mc "Rice."
            shoko "{i}Rice.{/i}"
            "You laugh, and she looks briefly, genuinely delighted with herself, and then puts it away."
            shoko "Right. That's my one. Don't spend it all at once."

    return


################################################################################
## Missions
################################################################################

label ev_mission_sunmall:

    yaga "Sit down."

    yaga "Four storeys of dead escalators in Saitama. Two urban explorers and a security guard have gone in and not come out."

    yaga "Registered grade three."

    yaga "Itadori, Fushiguro and Kugisaki are going. You're going with them."

    menu:
        "This is not a request, but he is watching your face."

        "\"Understood.\"":
            $ flag("accepted_sunmall")
        "\"Three people for a grade three is a lot.\"":
            $ gain("insight", 3)
            $ flag("accepted_sunmall")
            $ flag("suspected_grade")
            yaga "...Yes. It is."
            yaga "Say that again in front of Ijichi and he'll write it down, which is the highest honour available in this organisation."
            yaga "Go in careful. If the grading is wrong, you leave. All four of you."

    call chapter_four

    call chapter_five

    $ flag("sunmall_done")

    scene expression graded_bg() with fade_slow
    return


label ev_patrol:
    call sb_patrol
    return

################################################################################
## Bond 60 — the threads resolve
################################################################################

label ev_yuji_3:

    scene bg rooftop with fade_slow
    show yuji at pos_cr
    show mc at pos_l
    with dissolve

    "He asks you up to the roof, which he has never done. Itadori doesn't ask; he arrives."

    yuji "So I've been thinking about the thing you said. About the noble half."

    yuji "And I worked out what I actually want, and it's really embarrassing, and I'm going to say it fast."

    mc "Go."

    yuji "I want somebody to know the number."

    "You wait."

    yuji "The execution. It's postponed, not cancelled. Everybody knows that in the way you know a fact."

    yuji "But nobody's — nobody sits with it. Gojo-sensei jokes. Megumi goes quiet. Kugisaki changes the subject so fast it's basically a martial art."

    yuji "And I get it! I'd do the same! But it means I'm the only person in this building actually carrying it and I have to be cheerful about it all day."

    menu:
        "He's looking at the mountains, not at you."

        "\"Tell me the number.\"":
            $ add_bond("yuji", 12)
            $ flag("yuji_number")
            "He does."
            "He tells you how many fingers are left, and roughly how long the higher-ups will tolerate the delay, and what the two most likely versions of the end look like."
            "It takes about four minutes. You don't interrupt once."
            "When he's finished he lets out a breath that sounds like it's been in there since June."
            yuji "...Huh."
            yuji "That's better. That's a lot better and I don't know why."
            mc "Because now it's in two people."
            yuji "Yeah."
            yuji "Yeah, that's it."
            "You sit up there until it's properly dark. He doesn't make a single joke, which from Yuji Itadori is the loudest thing he has ever done."

        "\"I'm not going to be cheerful about it.\"":
            $ add_bond("yuji", 10)
            $ flag("yuji_serious")
            mc "I'll come and find you and I'll be completely normal about the fact that you might die."
            mc "I won't cheer you up. I won't change the subject. I'll just be a person who knows."
            yuji "...That's the weirdest offer anyone's ever made me."
            mc "Do you want it?"
            yuji "{b}Yeah.{/b}"
            yuji "Yeah, I really, really do."

    "Later, going down the stairs, he catches your sleeve."

    yuji "Hey. When it happens — the surrounded thing. You're on the list."

    mc "I know."

    yuji "I'm just saying it out loud. That's the whole point, right? Saying it out loud."

    return


label ev_megumi_3:

    scene bg dorm_common with fade_slow
    show megumi at pos_cr
    show mc at pos_l
    with dissolve

    "The folder has been on your desk for two weeks. You have read it eleven times."

    "Tonight you put it on the table in front of him and open it to a page he has annotated four separate times in four different years of handwriting."

    mc "This one. The dates."

    megumi "I've been through the dates."

    mc "You've been through them as her brother."

    "That stops him."

    mc "Every entry where she got worse is a Tuesday. Not most. All of them. Eleven Tuesdays over fourteen months."

    megumi "..."

    megumi "That's not — "

    "He takes the folder. He goes down the column with his finger, and his finger slows down, and then it stops."

    megumi "That's not possible."

    mc "It's in your own handwriting. You've read this a hundred times."

    megumi "I've read it a {i}thousand{/i} times."

    "He sits back."

    megumi "I couldn't see it. I physically could not see it, because every time I open this I'm not reading, I'm — "

    mc "Checking she's still there."

    megumi "...Yeah."

    menu:
        "It is the closest to undone you have ever seen him."

        "\"That's why you gave it to me.\"":
            $ add_bond("megumi", 14)
            $ flag("tsumiki_lead")
            megumi "..."
            megumi "Yes."
            megumi "I've known for about six months that I'd stopped being useful to her. I just didn't have anyone to hand it to."
            mc "You had Gojo. You had Ieiri."
            megumi "They'd have solved it. Or told me it couldn't be solved. Both of those end with me not doing anything."
            megumi "I needed somebody who'd sit with it as long as I have."
            "He closes the folder and pushes it back across the table to you."
            megumi "Keep it. Bring me Tuesdays."

        "\"Then let's go through it properly. Both of us. Tonight.\"":
            $ add_bond("megumi", 11)
            $ gain("insight", 6)
            $ flag("tsumiki_lead")
            "You go through it properly. It takes until four in the morning and most of a pot of terrible coffee."
            "You find two more things. Neither is an answer. Both are the first new information in this folder for a year."
            megumi "...Okay."
            megumi "Okay. Same time tomorrow."
            "He says it like a man who has just been handed back something he had privately given up on."

    return


label ev_nobara_3:

    scene bg city with fade_slow
    show nobara at pos_cr
    show mc at pos_l
    with dissolve

    "Shibuya on a Saturday is four hundred thousand faces an hour, and Nobara Kugisaki is standing in the middle of the crossing looking at every single one of them."

    nobara "This is stupid."

    mc "It's not stupid."

    nobara "It's statistically stupid. I've run the numbers. I ran them on the train, out loud, to nobody."

    "She keeps looking anyway."

    nobara "Eight years. She'd be twenty-three. She might not even be in Tokyo, she just said Tokyo because that's what you say."

    "You don't tell her the odds. You stand next to her and you look too."

    "After an hour she says, without any warning at all:"

    nobara "Do you know what I'm actually scared of?"

    nobara "Not that I won't find her. That I'll find her and she'll be {i}fine.{/i}"

    nobara "That the worst year of my life was a Tuesday to her."

    menu:
        "The crossing empties and fills and empties again."

        "\"Then you'd tell her anyway.\"":
            $ add_bond("nobara", 12)
            $ add_aff("nobara", 8)
            $ flag("saori_resolved")
            mc "You said it once. One person remembering out loud."
            mc "You didn't say 'one person remembering out loud, provided it turns out to have been important to her as well.'"
            nobara "..."
            nobara "That's a horrible thing to be right about."
            "She's quiet for a long time."
            nobara "Okay. Yes. I'd tell her anyway."
            nobara "And if she's fine — good. {b}Good.{/b} That's the outcome I wanted. I'd just have to have my feelings about it somewhere else, like an adult."
            "She turns away from the crossing for the first time in an hour."
            nobara "Thanks for standing here. You didn't say the odds."
            mc "I know the odds."
            nobara "Yeah. You didn't say them. That's the thing I'm thanking you for."

        "\"It wasn't a Tuesday to you. That's enough.\"":
            $ add_bond("nobara", 10)
            $ add_aff("nobara", 6)
            $ flag("saori_resolved")
            nobara "That's not how it works. It's supposed to be mutual, that's the whole — "
            mc "Says who?"
            nobara "..."
            mc "You've built eight years on remembering somebody. That's yours. She doesn't have to co-sign it."
            nobara "..."
            nobara "God, you're annoying."
            "She takes your arm on the way to the station, briskly, like it's a logistical decision, and does not let go until they announce the train."

    return


label ev_shoko_3:

    scene bg infirmary with fade_slow
    show shoko at pos_cr
    show mc at pos_l
    with dissolve

    "You bring her coffee at four in the morning."

    "You do it three nights running before she says anything about it."

    shoko "Suguru used to do this."

    mc "I know. You told me."

    shoko "..."

    shoko "I told you that once, six weeks ago, in passing."

    mc "You told me once. That's usually how telling works."

    "She holds the cup with both hands and doesn't drink it."

    shoko "I want to be honest with you, because you keep being honest with me and it's making me feel like a fraud."

    shoko "I have been managing you. A bit. Since the first week."

    shoko "It's what I do. Somebody comes in raw, I give them a piece of myself so they feel seen, and then they go away feeling better and I go back to the paperwork."

    shoko "It's not a lie. Every bit of it was true. It's just — a technique."

    menu:
        "She is looking at the cup, not at you."

        "\"And?\"":
            $ add_bond("shoko", 14)
            $ add_aff("shoko", 8)
            $ flag("shoko_open")
            shoko "And it stopped working about a month ago."
            shoko "You kept coming back. That's not in the technique. The technique assumes people get what they need and leave."
            shoko "So at some point I stopped giving you managed pieces and started just — talking. And I genuinely did not notice it happening."
            "She finally drinks the coffee."
            shoko "I haven't done that with anyone since I was seventeen."
            mc "How does it feel?"
            shoko "Terrifying. Obviously."
            shoko "...Bring the coffee tomorrow as well."

        "\"You gave me real things.\"":
            $ add_bond("shoko", 11)
            $ add_aff("shoko", 6)
            $ flag("shoko_open")
            mc "You told me about Geto. Nobody manages anyone with that."
            shoko "..."
            shoko "No. You're right. That one got away from me."
            shoko "I've thought about that a lot, actually. Why I said it."
            shoko "I think I wanted one person in this building to know that Satoru Gojo used to have a best friend, in case I stop being here to remember it."
            mc "You're not going anywhere."
            shoko "Everyone here says that to everyone here. Have you noticed? It's practically the school motto."

    return


################################################################################
## The second-years, further in
################################################################################

label ev_panda_2:

    scene bg dorm_common with fade_slow
    show panda at pos_cr
    show mc at pos_l
    with dissolve

    "Panda is watching television with the sound off, which he does when he is thinking, which he does more than anyone gives him credit for."

    panda "Can I tell you a thing I don't tell people?"

    mc "Yes."

    panda "I've got two sisters. Sort of. Inside me."

    "You wait, because there is clearly more, and because there is no reasonable follow-up to that sentence."

    panda "Cursed corpses have cores. Yaga built me with three."

    panda "There's me. There's a Gorilla — that one's for fighting, don't ask, it's a whole thing. And there's a third."

    panda "The third one's my older sister. She never woke up."

    "The television flickers silently."

    panda "So I'm carrying a person who never got to be one. And I'm the only one who knows what she'd have been like, and I don't, because she never was."

    menu:
        "He hasn't looked away from the screen."

        "\"Does Yaga know you think of her as your sister?\"":
            $ add_bond("panda", 13)
            $ flag("panda_sisters")
            panda "..."
            panda "Yeah. He named her."
            panda "He built three cores and only one of them took, and he could have quietly not mentioned the other two, and instead he sat me down when I was about four years old — in panda years, whatever that means — and told me exactly what I was carrying."
            panda "Because he decided I had a right to know what was in me."
            panda "That's the thing about him nobody sees. He shouts. He fails people on purpose. And then he does that."
            mc "That's why you stayed."
            panda "That's why I stayed."

        "\"What would you have called her?\"":
            $ add_bond("panda", 11)
            $ flag("panda_named")
            panda "...Huh."
            panda "Nobody's asked me that. Ever. Not once, in my whole entire life."
            "He's quiet for long enough that you wonder if you've done something wrong."
            panda "I don't have an answer. I want to think about it properly."
            panda "But — hey. Come back and ask me again in a few months. I'll have one."
            panda "That's a good thing to have to think about. That's a really good thing to have to think about."

    return


label ev_toge_2:

    scene bg ridge with fade_slow
    show toge at pos_cr
    show mc at pos_l
    with dissolve

    "Inumaki goes up to the ridge at 5:40 every single morning. You have known this for weeks — it's in the schedule of the place, if you pay attention."

    "Today you go with him."

    "He doesn't seem surprised. He points at a spot about ten metres off and taps his own throat, which you have learned means {i}stand back, I'm going to talk properly.{/i}"

    "Then he faces the empty valley and he uses his voice."

    toge "{b}Don't move.{/b}"

    "The wind stops. Not metaphorically — a bird thirty metres out drops four feet before it remembers how to fly."

    toge "{b}Get away.{/b}"

    "Something in the treeline goes crashing off downhill at a speed no animal that size should manage."

    "He does it for twenty minutes, aimed at nothing, out where the only casualties are weather."

    "Then he pulls the collar back up and sits down, and his throat is visibly raw, and he is entirely calm about it."

    menu:
        "He's got the phone out, waiting to see what you make of it."

        "\"You come out here so it doesn't land on anyone.\"":
            $ add_bond("toge", 13)
            $ gain("insight", 4)
            $ flag("toge_ridge")
            "He types: {i}every word I say is a hand on someone. Even hello. Especially hello.{/i}"
            "{i}Out here I get to just talk. For twenty minutes. Then I go back down and I'm careful again.{/i}"
            mc "That's every day."
            toge "Salmon."
            "{i}It's the only place I'm not dangerous. I'd rather be lonely at 5:40 than careless at noon.{/i}"
            mc "Can I come tomorrow?"
            "He looks at you for a second."
            toge "Salmon salmon."
            "He doubles them when he means it. You are starting to be able to hear it."

        "\"Doesn't it hurt?\"":
            $ add_bond("toge", 10)
            $ flag("toge_cost")
            "{i}Yes. Cursed Speech costs the throat. Big words cost more. Nobody warns you about that bit, they just tell you it's rare and powerful.{/i}"
            "{i}Ieiri patches it. She's never once asked why it's always Thursday.{/i}"
            mc "It's every day. Not Thursday."
            toge "..."
            "{i}...She's never once asked why it's always.{/i}"

    return


################################################################################
## The two who never had scenes
################################################################################

label ev_gojo_1:

    show gojo at pos_cr
    show mc at pos_l
    with dissolve

    "Finding Gojo is mostly luck. Keeping him is harder."

    gojo "Oh! It's you. Hi. Walk with me, I'm avoiding a phone call."

    "You walk with him. He does not go anywhere in particular."

    gojo "Question. Serious one, don't let the face fool you."

    gojo "If I dropped you into that shopping centre again — same curse, same day — but on your own. No Itadori, no Fushiguro. What do you do?"

    menu:
        "It is very hard to tell whether he is joking. It usually is."

        "\"Get the civilian out and run.\"":
            $ add_bond("gojo", 10)
            $ gain("insight", 4)
            $ flag("gojo_test_retreat")
            gojo "Correct."
            gojo "Genuinely, completely correct, and about one first-year in five says it."
            gojo "The other four say something brave. Brave is how you end up on Ieiri's table with your ribs on the outside."
            gojo "You're allowed to lose. Nobody ever tells students that, so I'm telling you: you are allowed to lose and come back."

        "\"Fight it. I'd have to.\"":
            $ add_bond("gojo", 6)
            $ gain("output", 4)
            $ flag("gojo_test_fight")
            gojo "Mm. That's the honest answer, isn't it. Not the right one — the honest one."
            gojo "You'd fight it because leaving somebody is a thing you can't currently do."
            gojo "That's not courage, by the way. That's a limitation. A really useful one that will eventually kill you."
            gojo "We'll work on it. Slowly. I don't actually want to take it off you, I just want you to be able to choose."

        "\"Depends what my reserve's at.\"":
            $ add_bond("gojo", 12)
            $ gain("control", 4)
            $ flag("gojo_test_measured")
            gojo "..."
            "He stops walking, which you have never seen him do mid-sentence."
            gojo "Say more."
            mc "Full reserve, I can hold it long enough to get her out. Under half, I can't, and trying just means two bodies instead of one."
            mc "So the answer's a number, not a feeling."
            gojo "..."
            gojo "Okay, that's — yeah. That's a second-year answer."
            gojo "Who taught you to think about it as a budget?"
            mc "Ieiri-san. And Zenin, sort of. Mostly Ieiri-san."
            gojo "{i}Huh.{/i} Shoko's teaching again."
            "Something passes across his face that the blindfold does not entirely cover."
            gojo "Good. That's good."

    "His phone rings. He looks at it with open loathing."

    gojo "That's my call. Go and be somewhere else, I'm about to be extremely unprofessional."

    return


label ev_yaga_1:

    scene bg storehouse with fade_slow
    show yaga at pos_cr
    show mc at pos_l
    with dissolve

    "Yaga is in the back of the storehouse with a half-finished cursed corpse on the bench, and he does not send you away, which from Yaga is an invitation."

    yaga "Hold that. There. Don't grip it, support it."

    "You hold it. It is heavier than it looks and it is warm, which you decide not to think about."

    yaga "Cursed corpse. Cursed energy given a shape and a set of instructions. Most of them do exactly what they're told forever."

    mc "Panda doesn't."

    yaga "No."

    yaga "Panda has a soul. I put one in on purpose, and it is the single most difficult thing anyone in this field has done in forty years, and I have never published how."

    mc "Why not?"

    yaga "Because the second somebody else can do it, somebody else will do it badly."

    menu:
        "He is threading something with enormous care for a man with hands that size."

        "\"Why do it at all?\"":
            $ add_bond("yaga", 12)
            $ gain("insight", 5)
            $ flag("yaga_why")
            yaga "..."
            yaga "Because everything else in this profession is a weapon."
            yaga "Cursed tools. Cursed techniques. Students — yes, students, don't look like that, that is what the higher-ups think you are and I am not going to pretend otherwise in my own storehouse."
            yaga "I wanted to make one thing that could refuse."
            yaga "I built something capable of telling me no, and then I had to sit in this room and find out whether it would."
            mc "Did he?"
            yaga "Constantly. Loudly. About television."
            "He does not smile. Something in the region of his eyebrows moves about two millimetres."
            yaga "It was the best day of my career."

        "\"You're teaching me because I'm a weapon too.\"":
            $ add_bond("yaga", 8)
            $ flag("yaga_blunt")
            yaga "..."
            yaga "You are eleven weeks from being useful and three weeks from being sent somewhere."
            yaga "Yes. To them, you are an asset with a grade on it."
            yaga "To me you are a sixteen-year-old who walked into a condemned building for somebody who wasn't going to remember it."
            yaga "I run a school inside an institution that would prefer a factory. Every hour you spend in here holding a bench for me is an hour you are not on a form."
            yaga "Now hold it {i}straight.{/i}"

    $ flag("storehouse_access")
    return


label ev_gojo_2:

    scene bg rooftop with fade_slow
    show gojo at pos_cr
    show mc at pos_l
    with dissolve

    "You find him on the roof at an hour when he has no business being anywhere, sitting on the railing, not eating anything."

    gojo "You've got that face. Go on."

    mc "People keep telling me you're the strongest."

    gojo "People are correct! It's one of my best features."

    mc "Nobody ever says what that's like."

    "The grin stays where it is. Everything behind it goes somewhere else."

    gojo "...Huh."

    gojo "Okay. Fine. You've earned one."

    gojo "It's like this. Every single problem in this profession has exactly one solution, and the solution is me getting on a train."

    gojo "Special grade in Sendai? Me. Kyoto's got something they can't handle? Me. Higher-ups need a threat neutralised quietly? Me, and then a form."

    gojo "So I'm never in a room where I'm not the answer. Which means I'm never in a room where anyone needs me to be a person."

    menu:
        "The blindfold is looking at nothing in particular."

        "\"That's why you're building us.\"":
            $ add_bond("gojo", 14)
            $ gain("insight", 5)
            $ flag("gojo_purpose")
            gojo "{i}Yes.{/i} Yes. Thank you."
            gojo "Everyone thinks I teach because I'm bored, or because Yaga made me."
            gojo "I teach because in fifteen years I want there to be twenty people who can each do a tenth of what I do, so that no single one of them ever has to be the only answer."
            gojo "Including you. Especially you, actually — you came in from outside, so you're the proof it isn't just bloodlines."
            mc "That's a long game."
            gojo "It's the only game. Everything else is me getting on a train."

        "\"You've got Shoko.\"":
            $ add_bond("gojo", 11)
            $ add_bond("shoko", 4)
            $ flag("gojo_shoko")
            gojo "..."
            gojo "Yeah."
            gojo "Shoko's the only person alive who knew me before I was a sentence people say."
            gojo "We don't talk about it. That's — genuinely, that's the arrangement, and it works, and I'm not going to be the one who breaks it."
            mc "Does she know that's the arrangement?"
            gojo "..."
            gojo "That is an extremely annoying question and I'm going to think about it for about three weeks."

        "\"Sounds lonely.\"":
            $ add_bond("gojo", 8)
            gojo "Ohhh, don't do that."
            gojo "Don't do the sad voice. I get the sad voice from about four people and it's exhausting."
            gojo "It's not lonely, it's {i}structural.{/i} There's a difference."
            "There is not, particularly, a difference. You both know it. Neither of you says so."
            gojo "Anyway. You should be training."

    return


label ev_yaga_2:

    scene bg office with fade_slow
    show yaga at pos_cr
    show mc at pos_l
    with dissolve

    "There is a photograph on the shelf behind Yaga's desk that you have looked at every time you've been in this room and never once asked about."

    "Today you ask about it."

    yaga "..."

    yaga "Three second-years. Sixteen years old. Nineteen ninety-nine."

    yaga "Satoru Gojo. Shoko Ieiri. Suguru Geto."

    "In the photograph they are laughing at something outside the frame, and one of them has his arm around another's shoulders, and none of the three faces looks anything like the two you know."

    yaga "I taught them. All three. The strongest class this school has produced and I have never once been able to describe it as a success."

    menu:
        "He has not put the photograph down."

        "\"What would you have done differently?\"":
            $ add_bond("yaga", 14)
            $ gain("insight", 6)
            $ flag("yaga_photo")
            yaga "I have had eleven years to answer that and I have three answers and none of them are any good."
            yaga "I'd have taught them that they were allowed to be wrong. All three were told from eleven that they were exceptional, and exceptional people do not learn how to be corrected."
            yaga "I'd have made them do something ordinary. Together. Every week. Something with no technique in it at all."
            yaga "And I would have noticed that Suguru had stopped sleeping. I had the information. It was in front of me. I was busy."
            "He puts the photograph face down, deliberately, and then turns it back up again."
            yaga "That's why I make first-years hold benches. It looks like nothing. It is not nothing."

        "\"Do you blame yourself?\"":
            $ add_bond("yaga", 9)
            $ flag("yaga_blame")
            yaga "That is a question people ask because they want to say 'it wasn't your fault' afterwards."
            yaga "Don't."
            yaga "It was partly my fault. It was also partly a rotten institution and partly a boy who made a choice, and adults are capable of holding all three of those at once."
            yaga "What I do with it is: I keep the photograph up. Where I have to look at it."
            yaga "And I have never once let a class of mine go a term without being made to do something ordinary together."
            mc "Is that what the Goodwill Event is?"
            yaga "The Goodwill Event is a scoreboard for the higher-ups."
            yaga "The four of you on a roof the night before it is what I'm actually after."

    return
