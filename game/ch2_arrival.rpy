################################################################################
## Chapter Two — Everyone Here Is Insane
################################################################################

label chapter_two:

    scene bg black
    with None

    show screen chapter_card("CHAPTER TWO", "Everyone Here Is Insane", "Tokyo Metropolitan Curse Technical College.")
    with fade_slow
    $ renpy.pause(2.6)
    hide screen chapter_card
    with fade_slow

    scene bg gate
    with fade_slow

    show ijichi at pos_r
    with dissolve

    "The car climbs for ninety minutes into mountains that, according to every map you have ever seen, are about forty kilometres outside Tokyo and also nowhere."

    "The man driving it has apologised eleven times. You have counted."

    ijichi "Sorry about the road. And the hour. And — sorry, are you carsick? I have bags."

    mc "I'm okay."

    ijichi "Kiyotaka Ijichi. Assistant manager. I do transport, paperwork, veils, and damage reports. Mostly damage reports."

    ijichi "Gojo-sensei said he briefed you."

    mc "He said the school is in a mountain and in Tokyo and both are true."

    ijichi "...That was the whole briefing?"

    mc "That was the whole briefing."

    ijichi "{i}(He does this.){/i}"

    ijichi "Right. Okay. Short version: this is the only place in Japan that teaches jujutsu sorcery. There are four first-years including you. There were three."

    ijichi "Try not to die in your first term. It generates an enormous amount of paperwork and I am the one who does it."

    hide ijichi
    with dissolve

    scene bg courtyard
    with fade_slow

    "The gate is a torii older than the concept of Japan having a capital, and past it the school opens out into a courtyard with a view that goes on for a hundred kilometres."

    "It is, and you resent this slightly, beautiful."

    show yaga at pos_c
    with dissolve

    yaga "[mc_surname]."

    yaga "Masamichi Yaga. Principal."

    yaga "I've read what Gojo wrote about the East Wing. It was two sentences long and one of them was about a convenience store."

    yaga "So I'll ask you directly. Why did you go in?"

    menu:
        "He is not making conversation. This is an assessment and it started before you sat down."

        "\"Someone had to.\"":
            $ flag("yaga_duty")
            mc "Nobody else was going to. That's it. That's the whole reason."
            yaga "Hm."
            yaga "That's an honest answer and a dangerous one. 'Someone had to' is how sorcerers talk themselves into things they can't come back from."
            yaga "Hold onto the honest part. We'll work on the rest."

        "\"I didn't think. I just went.\"":
            $ flag("yaga_instinct")
            mc "There wasn't a decision. I was outside, and then I was inside."
            yaga "Then your instincts are better than your training, which is not a compliment — you have no training."
            yaga "Instinct keeps you alive for about six months. After that it kills you. We have six months."

        "\"Because I was angry.\"":
            $ flag("yaga_anger")
            $ add_ce(3)
            mc "Everyone was standing around laughing. She'd been gone forty minutes."
            mc "I wasn't brave. I was furious that nobody else cared enough to move."
            yaga "...Good."
            yaga "Anger is fuel. Fuel is fine. Fuel that doesn't know where it's going burns the house down."
            yaga "Remember that you told me this. I'm going to hold you to it."

    yaga "Your classmates are in the training hall. Gojo is supposed to be supervising them."

    yaga "He is not supervising them."

    hide yaga
    with dissolve

    scene bg training
    with fade_slow

    "The training hall is bigger inside than the building it is in, which you decide to simply accept, because the alternative is sitting down on the floor for a while."

    show yuji at pos_l
    show nobara at pos_c
    show megumi at pos_r
    with dissolve

    "Three people. One of them is upside down."

    yuji "— no, but {i}listen{/i}, if you get strong enough, at some point you could definitely punch a whale —"

    nobara "Why would you punch a whale."

    yuji "I wouldn't! I'm saying the {i}capability{/i} —"

    megumi "Please stop talking."

    "The pink-haired one drops out of his handstand, sees you, and lights up like a vending machine."

    show yuji at pos_l, shake
    with None

    yuji "Oh! {b}Oh!{/b} You're the new one!"

    yuji "Yuji Itadori! First-year! Sorry, we've been arguing about whales for like twenty minutes, that's not — we're not normally—"

    megumi "We are exactly normally like this."

    yuji "Megumi, {i}come on{/i}."

    megumi "Fushiguro. Megumi Fushiguro."

    nobara "Nobara Kugisaki. Don't touch my nails, don't tell me to be careful, and if you snore we're going to have a problem."

    mc "[mc_surname] [mc_name]."

    nobara "Technique?"

    $ tname = TECHNIQUES[technique]["name"]
    mc "...Apparently it's called [tname]."

    nobara "Apparently?"

    mc "I found out about it five days ago in a condemned school building."

    "There is a pause. All three of them look at each other."

    yuji "Okay, so, honestly? That's kind of the standard onboarding process here."

    megumi "It is not."

    yuji "It's {i}kind of{/i} the standard—"

    megumi "Itadori, it is not."

    menu:
        "Three people, thirty seconds, and you already have to decide who you are here."

        "Ask Yuji what his technique is.":
            $ add_bond("yuji", 8)
            $ flag("asked_yuji")
            mc "What about you? What do you do?"
            yuji "Uh — that's kind of a long one."
            "Something happens in his face. It's fast, and he puts it away fast, but you saw it."
            yuji "Short version, I hit things really hard and I'm... carrying something. It's fine! It's under control."
            megumi "It is not under control."
            yuji "It's {i}mostly{/i} under control!"
            "He grins at you, and the grin is completely genuine, and you understand that both of those things are true at once."
            yuji "Ask me again in a couple weeks. I'll tell you properly. Promise."

        "Ask Megumi what he actually thinks of you being here.":
            $ add_bond("megumi", 8)
            $ flag("asked_megumi")
            mc "You've been sizing me up since I walked in. What's the verdict?"
            "Megumi doesn't pretend he wasn't."
            megumi "You came out of a grade three encounter with no training and no injuries. That means one of two things."
            megumi "Either your technique is extremely good, or you got extremely lucky."
            mc "Which do you think?"
            megumi "I think it doesn't matter, because in three weeks you'll be in a building with me and I'll find out."
            megumi "...That wasn't a threat. That was scheduling."
            nobara "Fushiguro, that was so a threat."

        "Ask Nobara how she stands any of this.":
            $ add_bond("nobara", 8)
            $ flag("asked_nobara")
            mc "Is it always like this?"
            nobara "God, no. Sometimes it's worse."
            nobara "I came here from a village with one bus a day and a grandmother who thought Tokyo was a moral failing."
            nobara "So yes, I fight monsters now. But I fight monsters {i}in Tokyo{/i}, and I get paid, and last week I bought a coat."
            nobara "You'll figure out your reason. Everyone here has one. The ones without a reason don't last."
            "She says it lightly. It doesn't land lightly."

        "Say nothing. Watch them.":
            $ add_ce(5)
            $ flag("watched_first")
            "You don't fill the silence."
            "Yuji fills it instead, immediately, with a story about a cat. Nobara talks over him. Megumi lets them, and his eyes stay on the door."
            mcthink "Itadori is loud because quiet costs him something. Kugisaki decides what she thinks and then defends it. Fushiguro is watching the exits."
            mcthink "And all three of them checked where the other two were standing when I walked in. Without looking."
            mcthink "They've already fought together. A lot."
            "It's a small thing to notice. It's the first useful thing you have done since the East Wing."

    show maki at pos_fr
    with dissolve

    maki "Are we doing introductions or are we training?"

    "The woman in the doorway is carrying a naginata over one shoulder like it's a shopping bag."

    maki "Maki Zenin. Second-year. Congratulations on the technique, nobody cares."

    yuji "Maki-san, that's—"

    maki "Nobody cares, Itadori, because a technique doesn't stop a knife."

    "She points the naginata at you without any particular ceremony."
    maki "You. Come here. I want to see something."

    "You come here. It does not occur to you until much later that you could have refused."

    maki "Rule one. Everything in this school will try to convince you that cursed energy is the whole game."

    maki "Then you'll meet something that moves faster than you can think, and the only thing between you and the floor will be whether your feet were already in the right place."

    maki "So. Feet."

    "She swings. Not fast. Not gently either — at exactly the speed of someone establishing a baseline."

    menu:
        "The naginata comes in at hip height. You have about a second."

        "Use [tname]. It's what you have.":
            $ add_ce(6)
            $ flag("spar_technique")
            if technique == "filament":
                "You throw threads at the floor and pull, and it works — you yank yourself sideways by half a metre and the shaft goes past your stomach."
                "You also land badly, because you have never once practised landing."
                maki "Not bad. You moved your whole body with something that isn't your legs."
                maki "Now do it forty times in a row without breaking your ankle."
            elif technique == "emberfall":
                "You catch the shaft. It's a stupid decision and you make it confidently."
                "Your palms scream. But the wood where you gripped it is now warm, and getting warmer, and Maki feels it through the haft."
                maki "Huh."
                maki "You just gave me a reason not to keep my hands on my own weapon. That's actually annoying."
                maki "It's also going to cost you both palms if you do it to anything that bleeds."
            else:
                "The last ten seconds of the room are still playing in your head. You have watched her shoulders drop like that before — twice, while she was warming up."
                "You are already stepping back when the naginata arrives."
                maki "...Okay."
                maki "You read the wind-up. Fine. Do it when I'm not telegraphing on purpose."
                mc "You were telegraphing on purpose?"
                maki "Obviously."

        "Just move. Don't think.":
            $ add_ce(3)
            $ add_bond("maki", 6)
            $ flag("spar_instinct")
            "You drop. Badly, gracelessly, entirely on instinct, and the naginata passes through the space your ribs were renting."
            "You land on your back and the ceiling is very high and very far away."
            maki "Good."
            mc "I fell over."
            maki "You fell over {i}early{/i}. That's ninety percent of it."
            maki "Everyone's first reflex here is to reach for their technique. Yours was to get out of the way. Keep that. Everything else is teachable."

        "Take the hit. Learn what it costs.":
            $ add_ce(2)
            $ add_bond("maki", 10)
            $ add_bond("yuji", 4)
            $ flag("spar_took_it")
            "You don't move."
            "The shaft hits you across the hip and you go down like laundry, and the floor is a lot harder than it looks, and for a second the room has no air in it."
            nobara "{i}What is wrong with you—{/i}"
            "Maki crouches down. She isn't smiling, but something in her face has changed."
            maki "Why?"
            mc "Because I've never been hit before. Not really."
            mc "If I meet something that hits me, I want to already know what it's like. I don't want to find out then."
            maki "..."
            maki "Get up."
            "You get up."
            maki "Same time tomorrow. And every day after that. Don't be late, I don't wait."
            "Behind you, very quietly, Yuji says {i}oh, they're going to be a problem{/i}, and he sounds genuinely delighted about it."

    show panda at pos_fl
    show toge at pos_cl
    with dissolve

    panda "Oh good, we're doing hazing already."

    "There is a panda. It is two metres tall, it is wearing a school uniform, and it is holding a can of coffee."

    panda "Panda. Second-year. Yes, I'm a panda, no, I'm not a panda, we can do that conversation later when you've eaten something."

    toge "Salmon."

    panda "Inumaki says welcome."

    mc "That was 'welcome'?"

    panda "That was 'welcome'. He speaks in rice ball ingredients. Cursed Speech — anything he actually says, you have to do."

    panda "Last month he said 'don't move' to a grade two and its legs stopped working. So we keep it to tuna mayo."

    toge "Tuna mayo."

    show gojo at pos_c, pulse_in
    with dissolve

    gojo "{b}Wonderful!{/b} You've all met, nobody's crying, and I only missed the good part."

    megumi "You were supposed to be supervising."

    gojo "I was! From a bakery! Emotionally!"

    gojo "Okay, everybody, listen up, this is the actual reason I came."

    "He drops a folder on the floor because there is no table and he does not appear to consider that a problem."

    gojo "Sometime in the next fortnight, the four of you are going to a shopping centre in Saitama that closed in 2019."

    gojo "Something in there has eaten two urban explorers and a security guard. Registered grade three. Probably a grade three."

    nobara "'Probably.'"

    gojo "Probably! That's why it's fun."

    gojo "Between now and then — train, rest, get to know each other, whatever you want. I genuinely don't care how you spend it."

    gojo "Campus is open. Everyone's somewhere. Go find out where."

    gojo "But I'll tell you the thing nobody told me when I was fifteen, so listen."

    show gojo at pos_c
    with None

    gojo "One of these weeks, one of you is going to be standing somewhere very dark, and the only thing that will get you out is knowing — without checking — exactly where the others are."

    gojo "You don't get that from training."

    gojo "You get that from the boring afternoons. So go have some."

    ## ------------------------------------------------------------------
    ## Closing beat: the infirmary. Shoko is a major character and a
    ## romance option; she shouldn't first appear as a stranger on a map.
    ## ------------------------------------------------------------------

    scene bg infirmary with fade_slow
    show shoko at pos_cr
    show mc at pos_l
    with dissolve

    "Ijichi walks you to the infirmary afterwards, apologising twice, and hands you to a woman in a lab coat who looks at you the way a mechanic looks at a car that has been driven into a wall."

    shoko "Shoko Ieiri. I'm the doctor. I'm the only doctor."

    shoko "Sit."

    "She turns your hands over, then your jaw, then — without asking — the hip Maki put a stick through."

    shoko "Zenin's work."

    mc "How can you tell?"

    shoko "Because it's exactly where it should be, and it's the right amount."

    shoko "She does not hurt people by accident. Remember that when you're deciding how you feel about her."

    "Something green and unreasonably warm goes through your hip and the ache leaves the way a guest leaves when the host stands up."

    mc "That's—"

    shoko "Reverse Cursed Technique. Yes. Don't be impressed, it's the only interesting thing about me."

    menu:
        "She has already turned back to her paperwork, which you are fairly sure is a test."

        "\"Everyone here does that. The self-deprecating thing.\"":
            $ add_bond("shoko", 8)
            $ flag("shoko_noticed")
            "She stops writing."
            shoko "Say more."
            mc "Gojo makes a joke. Fushiguro says four words. You say you're not interesting."
            mc "It's the same move at three different volumes."
            shoko "..."
            shoko "You've been here one day."
            mc "It's been a long day."
            shoko "Mm."
            "She goes back to the paperwork. Then, without looking up:"
            shoko "Door's open. It generally is. I'm here more than I'm anywhere."

        "\"Thank you.\"":
            $ add_bond("shoko", 5)
            shoko "You're welcome."
            shoko "You'll be back. Everyone's back. Itadori's been in four times this month and twice it was a door."
            "You laugh. She doesn't, but something happens in the region of her mouth."

        "Say nothing and let her work.":
            $ add_bond("shoko", 3)
            $ gain("insight", 3)
            "You sit quietly while she finishes."
            "There is a photograph face-down on the desk that she straightens twice without turning over. An ashtray that has been emptied but not hidden. And a second chair on this side of the desk, which is not where you put a chair for patients."
            mcthink "She spends a lot of hours in here on her own."
            "She catches you looking, does not comment, and does not move the chair."

    ## Prologue choices seed the journal, so the first real conversation you
    ## had with someone is already on the board when the campus opens.
    python:
        if has_flag("asked_yuji"):
            open_thread("yuji_countdown")
        if has_flag("asked_megumi"):
            open_thread("megumi_tsumiki")
        if has_flag("asked_nobara"):
            open_thread("nobara_saori")
        if has_flag("spar_took_it") or has_flag("spar_instinct"):
            open_thread("maki_zenin")
        if has_flag("shoko_noticed"):
            open_thread("shoko_remembers")
        open_thread("gojo_measure")

    scene bg black
    with fade_slow

    return
