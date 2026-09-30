################################################################################
## Cursed Bonds — Arc 1 story spine.
##
## Nothing here runs on a date. These beats find you wherever you are, in the
## order the main story sets (the mission chain in sb_missions.rpy), and they
## wait for you until you get there.
################################################################################

init 1 python:

    ## The order and the gaps between beats come from the mission chain;
    ## these keep only their periods, priorities and requirements.
    ## st_board_open is retired (Utahime's board replaced Ijichi's note): its
    ## label stays below for old saves, but it is no longer registered.
    ev("st_roll_call",   kind="story", periods=["Morning"],        priority=100)
    ev("st_noise",       kind="story", periods=["Evening"],        priority=90,
       requires=("roll_call",))
    ev("st_second_years", kind="story", periods=["Afternoon"],     priority=95,
       requires=("roll_call",))
    ev("st_aftermath",   kind="story", periods=["Morning"],        priority=95,
       requires=("sunmall_done",))
    ev("st_intensive",   kind="story", periods=["Afternoon"],      priority=90,
       requires=("sunmall_done",))
    ev("st_roster",      kind="story", periods=["Noon"],           priority=90)
    ev("st_night_before", kind="story", periods=["Evening", "Night"], priority=120)


################################################################################

label st_roll_call:

    scene bg classroom with fade_slow
    show yaga at pos_c
    show yuji at pos_fl
    show megumi at pos_l
    show nobara at pos_cr
    with dissolve

    "Ijichi finds me before breakfast and says the word 'mandatory' twice, which for Ijichi is shouting."

    yaga serious "Sit."

    yaga "Every sorcerer in this country has a grade. It decides what you are sent to, and who is sent with you."

    yaga "Every year Kyoto sends their students here for the Goodwill Event. It is billed as an exchange. It is a fight."

    yaga "Two schools, one field, and a scoreboard that the higher-ups read very carefully."

    nobara @ happy "So it's a job interview with sticks."

    yaga "That is the most accurate description of it I have ever heard and I would appreciate you never repeating it."

    yaga "Four first-years. Kyoto has six students and two of them have been doing this since they were eleven."

    yaga "When it comes, you will not be ready. The question is how much not-ready."

    "He looks along the row and stops on me."

    yaga "[mc_surname]. Last week you didn't know cursed energy existed. Today you get a number."

    $ promote("mc", "g4", "Assessed at roll call", quiet=True)
    call show_grade_card("g4", "ASSESSED")

    yaga neutral "Grade 4. Everyone starts somewhere. Most people start here."

    yaga "Fushiguro is Grade 2. Kugisaki, Grade 3. Itadori is Grade 4 on paper, for reasons above both of us."

    yuji @ happy "On paper. I'm taking that as a compliment."

    megumi serious "Don't."

    menu:
        "Everyone is looking at me."

        "\"Then I'd better start now.\"":
            $ add_bond("yaga", 6)
            $ gain("output", 2)
            $ flag("rollcall_defiant")
            yaga "You had better."
            yaga "Most people your age hear 'Grade 4' and hear the bottom rung. You heard it as a starting line."
            yaga "That's the correct reading. Don't let it make you stupid."

        "\"What happens if I'm not ready?\"":
            $ add_bond("yaga", 4)
            $ gain("insight", 3)
            $ flag("rollcall_honest")
            yaga "Then you get hurt, and Ieiri puts you back together, and I write a report explaining why I sent you."
            yaga "I have written that report. Twice."
            yaga "I would prefer a third time not to have your name on it."

        "\"Who am I fighting?\"":
            $ gain("insight", 2)
            $ flag("rollcall_tactical")
            yaga "Good question. Wrong day for it, but good question."
            yaga "Zenin will tell you about Kyoto. She knows more about them than she has ever wanted to."

    yaga serious "Two things, then get out."

    yaga "One: the storehouse is open to you from today. Look, don't take. Nothing on those racks leaves without a grade and a reason."

    yaga "Two: Kyoto's teacher arrives tomorrow to prepare the Goodwill Event, and she has agreed to run the board while she is here. Low grade. Real."

    $ flag("roll_call")
    ## A save made before this chapter and resumed at the menu above skips
    ## the promote: migration 20 has already turned its old int into None.
    if not isinstance(grade, str):
        $ promote("mc", "g4", "Assessed at roll call", quiet=True)
    $ flag("storehouse_access")
    $ advance_period()

    scene expression graded_bg() with fade_slow
    return


label st_board_open:

    "A folded notice appears on your door sometime before dawn, in Ijichi's handwriting, apologising for the folded notice."

    "{i}Mission board is live in the principal's office. Grade four only. Take somebody with you. — Ijichi{/i}"

    "{i}(P.S. Sorry about the hour. And the paper.){/i}"

    $ flag("mission_board_open")
    return


label st_noise:

    scene bg courtyard with fade_curse

    $ _here_folk = [c for c in who_is_here() if c in ("yuji", "megumi", "nobara", "maki", "panda", "toge")]
    $ _ally = _here_folk[0] if _here_folk else closest_first_year()
    $ _an = CAST[_ally]["short"]

    "The veil over the campus is not a wall. It is a filter, and filters clog."

    "At twenty past seven in the evening, something the size of a large dog comes through the drainage cut below the training hall and starts eating the lights."

    show curse small at pos_loom_r, pulse_in
    with fade_curse

    "[_an] gets there the same moment you do."

    if _ally == "yuji":
        yuji "Oh, you're joking—"
    elif _ally == "megumi":
        megumi "Don't shout. It hunts by sound."
    elif _ally == "nobara":
        nobara "It ate the {i}lights?{/i} What is wrong with it?"
    elif _ally == "maki":
        maki "Grade four. Don't embarrass yourself."
    elif _ally == "panda":
        panda "Okay! Team-building!"
    else:
        toge "Salmon!"

    menu:
        "It's small, it's fast, and it is between you and the dormitories."

        "Take the front. Let [_an] flank.":
            $ gain("output", 3)
            $ add_bond(_ally, 6)
            $ flag("noise_front")
            "You go straight at it and make yourself the loudest thing in the courtyard, and it commits to you completely, which is exactly the plan and feels nothing like a plan while it happens."
            "[_an] takes it from the side about a second and a half later."

        "Let [_an] lead. Read it first.":
            $ gain("insight", 4)
            $ add_bond(_ally, 5)
            $ flag("noise_read")
            "You hang back for four seconds and watch it move, and in those four seconds you learn that it always breaks left after it lunges."
            mc "Left! It always goes left!"
            "[_an] adjusts mid-swing. It goes left. It does not go anywhere after that."

        "Both of you at once. No plan.":
            $ gain("output", 2)
            $ gain("control", 2)
            $ add_bond(_ally, 8)
            $ spend_stamina(15)
            $ flag("noise_reckless")
            "There is no plan. There is barely a decision."
            "It takes nine seconds and both of you come out of it bleeding slightly and laughing in a way that is mostly adrenaline."

    hide curse small with fade_curse

    "It comes apart into grey and the courtyard lights come back on one at a time, which is somehow the eeriest part of the whole evening."

    $ add_bond(_ally, 2)
    $ advance_period()

    scene expression graded_bg() with fade_slow

    if _ally == "yuji":
        yuji "Hey. That was good. {i}We{/i} were good."
        $ open_thread("yuji_countdown")
    elif _ally == "maki":
        maki "You didn't reach for your technique first. Twice now."
        maki "Dojo. Dawn."
        $ open_thread("maki_zenin")

    "Ijichi arrives four minutes later with a clipboard and an expression of profound weariness."

    ijichi "Was anything structural damaged."

    mc "The lights."

    ijichi "...The lights are structural."

    return


label st_aftermath:

    scene bg infirmary with fade_slow
    show shoko at pos_c
    with dissolve

    "The morning after Saitama, Shoko Ieiri goes through all four of you in order and does not say anything at all until she's finished."

    shoko "Kugisaki, wrist. Itadori, everything, as usual. Fushiguro, you're fine and you're pretending you're not, which is new."

    shoko "You. Sit."

    "She turns your hands over."

    shoko "Cursed energy debt. You spent past your reserve and kept going."

    mc "It worked."

    shoko "It always works. That's the problem with it."

    shoko "There's no alarm. You don't pass out at a threshold. You just get quieter and slower and one day you're a bit too slow, in a stairwell, and that's the whole story."

    menu:
        "She hasn't let go of your hands."

        "\"Then teach me where the line is.\"":
            $ add_bond("shoko", 8)
            $ gain("insight", 4)
            $ flag("shoko_taught_limits")
            shoko "...Right. Yes. That's the correct question."
            shoko "Here."
            "She presses two fingers just under your sternum."
            shoko "That's your reserve. Not a metaphor — feel for it."
            "You feel for it. There is, astonishingly, something there."
            shoko "When it goes cold and thin, you're done. Not tired. {i}Done.{/i}"
            shoko "Most sorcerers learn that at about twenty-five. You get it in week two, because I am tired of the alternative."
            $ open_thread("shoko_remembers")

        "\"It was a grade two. Somebody had to.\"":
            $ add_bond("shoko", 3)
            $ flag("shoko_worried")
            shoko "Mm."
            shoko "I've heard that sentence from about forty people."
            shoko "I want you to notice that I said {i}heard{/i}, and not {i}hear.{/i}"
            "She lets go of your hands."
            shoko "Go and eat something."

    $ restore_ce(ce_max)
    $ stamina = stamina_max
    $ flag("aftermath_done")
    $ advance_period()

    scene expression graded_bg() with fade_slow
    return


label st_intensive:

    scene bg ridge with fade_slow
    show gojo at pos_c
    with dissolve

    "Gojo is waiting on the ridge, which he has never once done, sitting on a rock with no sweets and no phone."

    gojo "Sit down. I'm going to be serious for about eleven minutes and then I'm going to stop, so use them."

    "He is not smiling. Without the smile his face is very hard to look at, blindfold and all."

    gojo "You've got a technique you didn't ask for and a body that hasn't caught up to it."

    gojo "And one of these days you're going to stand on a field opposite people who have had this their whole lives."

    gojo "So here's the only thing I actually teach."

    $ _t = tech()
    $ _tn = _t["name"]

    gojo "Everyone thinks cursed energy is a tank you empty. It isn't. It's a {i}shape{/i} you hold."

    gojo "Holding a shape is tiring. Making one is not. That's why you're exhausted after four minutes and Zenin isn't after four hours."

    gojo "[_tn] is a shape. Stop making it over and over. Make it once and {b}hold{/b} it."

    menu:
        "Eleven minutes. He meant it literally; you can feel them going."

        "Try it now, in front of him.":
            $ gain(tech()["scales"], 8)
            $ gain("control", 3)
            $ raise_reserve(20)
            $ flag("intensive_tried")
            "You do it wrong four times."
            "On the fifth you feel the difference in your chest — not a thing you are pushing out, a thing you are simply {i}being{/i} — and you hold it for nine entire seconds before it collapses."
            gojo "There."
            gojo "Nine seconds. In a week, ninety. In a year you'll forget you're doing it."
            gojo "That's the whole lesson. Everything else is reps."

        "\"Why are you telling me and not all four of us?\"":
            $ add_bond("gojo", 12)
            $ gain("insight", 5)
            $ raise_reserve(12)
            $ flag("intensive_asked")
            gojo "..."
            gojo "Because Itadori has Sukuna doing his arithmetic for him and Fushiguro was raised in a clan that taught him this at nine."
            gojo "And Kugisaki works it out herself, in her own time, by being annoyed about it."
            gojo "You're the one who came in from outside. Off the street, off one bad Thursday."
            gojo "Everyone else here got a running start. I'm evening it up. Quietly, because if I do it loudly you'll all decide it means something."
            mc "Doesn't it?"
            gojo "...Yeah."
            gojo "Eleven minutes are up."

    $ advance_thread("gojo_measure", 2)
    $ flag("intensive_done")
    $ advance_period()

    "He's gone before you've stood up. He does not appear on campus again for two days."

    scene expression graded_bg() with fade_slow
    return


label st_roster:

    scene bg courtyard with fade_slow
    show maki at pos_c
    with dissolve

    "The Kyoto roster goes up on the board outside the classroom building at noon one day, and Maki reads it standing very still."

    maki "Mai's on it."

    mc "Your sister."

    maki "My twin. There's a difference and she'd want me to make it."

    "She doesn't move for a while."

    maki "She's going to say things. On the field, where everyone can hear, because that's the only place she's got left to say them."

    maki "And I'm going to have to not react, because if I react she wins something she doesn't actually want."

    menu:
        "Not long now."

        "\"You don't have to not react.\"":
            $ add_bond("maki", 10)
            $ add_aff("maki", 4)
            $ advance_thread("maki_zenin", 3)
            $ flag("maki_roster_open")
            mc "Everyone's going to be watching a fight. Nobody's going to be watching whether you flinched."
            mc "Except her. And she's not looking for a flinch — she's looking for whether you're still there."
            maki "..."
            maki "That's a horrible thing to say to someone this close to it."
            maki "...Come with me. After. When I go back to that house."
            maki "Not to fight anyone. Just so there's somebody in the room who isn't a Zenin."
            mc "Yes."
            maki "You didn't think about it."
            mc "No."

        "\"What do you want to happen?\"":
            $ add_bond("maki", 7)
            $ add_aff("maki", 2)
            $ advance_thread("maki_zenin", 2)
            maki "I want to win."
            maki "..."
            maki "I want her to see me win and be glad about it, in private, where nobody can hold it against her."
            maki "That's not a plan. You can't build a training week around 'and then my sister feels something'."
            mc "You could build the rest of the time around it."
            maki "...Dojo. Dawn. Bring something to hit."

    $ advance_period()
    scene expression graded_bg() with fade_slow
    return


label st_night_before:

    scene bg rooftop with fade_slow
    show yuji at pos_fl
    show nobara at pos_l
    show megumi at pos_cr
    show maki at pos_fr
    with dissolve

    "Nobody organises it. That's the part you remember afterwards — nobody sends a message, nobody suggests it."

    "You go up to the roof the night before Kyoto because you can't sleep, and everyone else is already there, because none of them could either."

    nobara "If you tell anyone I was nervous I will end you."

    yuji "You said that out loud though."

    nobara "To {i}you.{/i} You don't count, you're barely a person, you're a golden retriever with a curse in it."

    yuji "That's the nicest thing you've ever said to me."

    megumi "Both of you should sleep."

    nobara "Are {i}you{/i} going to sleep, Fushiguro?"

    megumi "...No."

    "Maki is sitting on the railing with her back to the drop, cleaning something that does not need cleaning."

    $ _closest = closest_partner()
    $ _cn = CAST[_closest]["short"]
    $ _cb = bonds.get(_closest, 0)

    if _cb >= 60:
        "[_cn] shifts over without being asked, and you end up sitting close enough that your shoulders touch, and neither of you says anything about it."
    else:
        "You find a space at the edge and sit in it."

    "Not so long ago you were on the ground in the alley behind the arcade with your hands full of something you couldn't name."

    $ _open = len(threads_open())
    $ _done = len(threads_complete())

    if _open >= 5:
        mcthink "I know all of these people now."
        mcthink "Not their techniques. {i}Them.{/i} What they're carrying and roughly how heavy it is."
        mcthink "When I got here I'd have said that was the soft part of the job."
    elif _open >= 2:
        mcthink "I know some of them. Properly, I mean — past the introductions."
        mcthink "Not enough of them. I spent my days on other things."
    else:
        mcthink "I've spent almost all of my time here alone, on a ridge, getting stronger."
        mcthink "Tomorrow I find out whether that was the right trade."

    if _done >= 3:
        $ add_bond("yuji", 3)
        $ add_bond("megumi", 3)
        $ add_bond("nobara", 3)
        $ add_bond("maki", 3)
        "Somebody starts an argument about whether Panda counts as a first-year for scoring purposes. It goes on for forty minutes. It is the best forty minutes you have had since you arrived."

    yuji "Hey."

    yuji "Whatever happens tomorrow — this was good. This bit. Right now."

    megumi "You're being sentimental."

    yuji "I'm being {i}accurate.{/i}"

    nobara "He's being sentimental."

    "The light comes up over the mountains at about four and none of you have moved."

    ## Not the end of Arc One any more: the Goodwill Event is main story now
    ## (Act IV), so this only marks the night as done.
    $ flag("night_before_done")

    scene bg black with fade_slow

    show screen chapter_card("THE NIGHT BEFORE", "Goodwill", "The Kyoto Goodwill Event — coming in a later build.")
    $ renpy.pause(4.5)
    hide screen chapter_card
    with fade_slow

    scene expression graded_bg() with fade_slow
    return


label st_second_years:

    scene bg training with fade_slow
    show maki at pos_l
    show panda at pos_c
    show toge at pos_r
    with dissolve

    "There have been three other people on this campus since you arrived. You have seen them at a distance, at meals, crossing the courtyard, and nobody has introduced anybody, because nobody here does that."

    "Today one of them walks into the training hall while you are in it, carrying a naginata over one shoulder like a shopping bag."

    maki "You're the new first-year."

    maki "Maki Zenin. Second-year. Congratulations on the technique, nobody cares."

    yuji "Maki-san, that's—"

    maki "Nobody cares, Itadori, because a technique doesn't stop a knife."

    "The panda behind her is two metres tall, wearing a school uniform, and holding a can of coffee."

    panda "Panda. Second-year. Yes I'm a panda, no I'm not a panda, we can do that conversation when you've eaten something."

    toge "Salmon."

    panda "Inumaki says welcome. He speaks in rice ball ingredients — Cursed Speech. Anything he actually says, you have to do."

    panda "Last month he told a grade two 'don't move' and its legs stopped working. So we keep it to tuna mayo."

    toge "Tuna mayo."

    menu:
        "Maki has not put the naginata down."

        "\"Why now? You've been here the whole time.\"":
            $ add_bond("maki", 6)
            $ gain("insight", 2)
            maki "Because for the first few days you were a first-year who'd had a bad Thursday."
            maki "Today you were in here at six in the morning on your own. That's different."
            maki "I'm not interested in people who've had something happen to them. I'm interested in people who get up early about it."

        "\"What does a second-year know that I don't?\"":
            $ add_bond("maki", 8)
            $ gain("output", 2)
            maki "Everything, and none of it is the interesting kind."
            maki "Here's the only one that matters today."
            "She swings — not fast, not gently, at exactly the speed of someone establishing a baseline — and you get out of the way badly and entirely on instinct."
            maki "Good. You moved your feet before you reached for your technique."
            maki "Everyone here reaches for the technique. Dojo. Dawn. Don't be late, I don't wait."
            $ open_thread("maki_zenin")

        "\"Hi. I'm not going to be interesting for about a month.\"":
            $ add_bond("panda", 8)
            $ add_bond("toge", 6)
            $ gain("control", 2)
            panda "Ha! Okay, I like that. That's honest."
            panda "For the record, the second-years look out for the first-years. That's the whole system, it isn't written down anywhere, and it's the only reason any of us got through our first year."
            toge "Salmon salmon."
            panda "He doubles them when he means it. You'll want to learn that one."

    python:
        for _c in ("maki", "panda", "toge"):
            recruit(_c)

    $ flag("met_second_years")
    $ advance_period()

    scene expression graded_bg() with fade_slow
    return
