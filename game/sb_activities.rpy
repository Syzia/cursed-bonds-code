################################################################################
## Cursed Bonds — activities.
##
## What you can do with a person, and what it takes to unlock it.
##
## WP7 (PHASE1_DESIGN.md 4.5, 5.1, section 6): the person view offers at most
## four of these at a time, ranked by person_choices(); stage_person puts the
## person on screen before Talk and every act_* so they stay there while we
## talk; Gojo's lesson (activity `lesson`, label act_lesson) is new.
################################################################################

init -1 python:

    ## kind:  "friend" — available to everyone
    ##        "romance" — only for romanceable characters, gated on affection
    ## who:   None = anyone, or a tuple of keys
    ## loc:   None = anywhere, or a tuple of location keys
    ## per:   None = any period, or a tuple of period names
    ## cost:  periods it takes (0 = free). Required on every entry.
    ## when:  None, or the NAME of a store function; the activity is hidden
    ##        while it returns False

    ACTIVITIES = [
        dict(id="talk",     label="Talk",              hint="A few minutes. Costs nothing.",
             kind="friend", min_bond=0,  cost=0),

        dict(id="hang",     label="Spend time together", hint="Whatever they're doing, do it with them.",
             kind="friend", min_bond=0,  cost=1, needs_event=True),

        dict(id="eat",      label="Eat together",      hint="Everyone's here at noon anyway.",
             kind="friend", min_bond=10, cost=1, loc=("cafeteria",)),

        dict(id="train",    label="Train together",    hint="They hit harder than they need to.",
             kind="friend", min_bond=20, cost=1,
             loc=("dojo", "training", "ridge", "forest"),
             who=("yuji", "megumi", "maki", "panda", "toge", "nobara")),

        dict(id="study",    label="Study together",    hint="Four hundred pages, two people.",
             kind="friend", min_bond=25, cost=1, loc=("classroom", "dorm_common", "dorm")),

        dict(id="swim",     label="Swim together",     hint="The water is snowmelt cold.",
             kind="friend", min_bond=35, cost=1, loc=("riverside",),
             per=("Noon", "Afternoon")),

        dict(id="walk",     label="Walk with them",    hint="No destination. That's the point.",
             kind="friend", min_bond=40, cost=1,
             loc=("courtyard", "gate", "forest", "riverside", "ridge")),

        dict(id="invite",   label="Ask them along",    hint="They'll stick with me for the rest of the day.",
             kind="friend", min_bond=45, cost=0),

        dict(id="stargaze", label="Sit out with them", hint="The roof, and a hundred kilometres of dark.",
             kind="friend", min_bond=50, cost=1, loc=("rooftop", "ridge", "riverside"),
             per=("Evening", "Night")),

        ## Gojo's lesson, on the odd day he's in his office (5.3, D17).
        dict(id="lesson",   label="Take the lesson",   hint="He's in. He says eleven minutes. It was, once.",
             kind="friend", min_bond=0,  cost=1, who=("gojo",), loc=("gojo_office",),
             when="lesson_ok"),

        dict(id="confide",  label="Tell them something true", hint="Something I haven't said to anyone here.",
             kind="friend", min_bond=65, cost=1, once=True),

        ## The top of the friendship track. You have spent the whole game being
        ## the one who needs things; here it goes the other way.
        dict(id="stand",    label="They asked me for something",
             hint="It took them a while to work up to it.",
             kind="friend", min_bond=80, cost=2, once=True,
             requires_flag="confided_"),

        ## ---- romance ------------------------------------------------------
        dict(id="rom_town", label="Ask them into town", hint="A whole afternoon, off the mountain.",
             kind="romance", min_bond=50, min_aff=30, cost=2,
             loc=("gate", "courtyard")),

        dict(id="rom_close", label="Stay a while longer", hint="Neither of us moves to go.",
             kind="romance", min_bond=60, min_aff=45, cost=1,
             per=("Evening", "Night")),

        ## The ceiling scene: appears only when affection has nowhere left to go,
        ## and lifts the lid so it can keep going.
        dict(id="rom_say",  label="Say it",             hint="Out loud. Badly, probably.",
             kind="confession", min_bond=85, min_aff=100, cost=2, once=True),

        ## ---- after the confession ----------------------------------------
        dict(id="int_night", label="Stay the night",    hint="Neither of us suggests I go.",
             kind="intimate", min_aff=110, cost=1, per=("Evening", "Night")),

        dict(id="int_morning", label="Wake up with them", hint="The first hour, before anyone needs anything.",
             kind="intimate", min_aff=130, cost=1, per=("Morning",)),

        dict(id="int_day",  label="A day off. Just the two of us.", hint="No training, no missions, no map.",
             kind="intimate", min_aff=150, cost=3),

        dict(id="int_after", label="Talk about after",  hint="What happens when all this is over.",
             kind="intimate", min_aff=175, cost=1),
    ]

    ACT_BY_ID = {a["id"]: a for a in ACTIVITIES}

    def _act_place_ok(a, loc):
        return (not a.get("loc")) or loc in a["loc"]

    def _act_period_ok(a):
        return (not a.get("per")) or store.period in a["per"]

    def activity_state(a, who, loc=None):
        """(available, reason) — reason explains the lock, in the player's words."""
        loc = loc or store.here

        if a["kind"] in ("romance", "confession", "intimate") and not is_romanceable(who):
            return False, None                      # hidden entirely

        ## The confession only exists at the ceiling, and only once.
        if a["kind"] == "confession":
            if not confession_ready(who):
                return False, None
            return (store.stamina >= 10), (None if store.stamina >= 10 else "Too tired")

        ## Everything above the confession is hidden until it has happened.
        if a["kind"] == "intimate" and not is_together(who):
            return False, None

        if a.get("who") and who not in a["who"]:
            return False, None                      # hidden entirely

        if a.get("when"):
            fn = getattr(store, a["when"], None)
            if fn is None or not fn():
                return False, None                  # hidden entirely

        b = store.bonds.get(who, 0)
        af = store.affection.get(who, 0)
        short = CAST[who]["short"]

        if b < a.get("min_bond", 0):
            return False, "Bond %d" % a["min_bond"]
        if af < a.get("min_aff", 0):
            return False, "♡ %d" % a["min_aff"]
        if a.get("once") and has_flag("did_%s_%s" % (a["id"], who)):
            return False, "Done"
        if a.get("requires_flag") and not has_flag(a["requires_flag"] + who):
            return False, "Not yet"
        if not _act_place_ok(a, loc):
            names = ", ".join(LOCATIONS.get(l, {}).get("name", l) for l in a["loc"][:2])
            return False, names
        if not _act_period_ok(a):
            return False, "/".join(a["per"])
        if a.get("needs_event") and not has_event("hangout", who, loc):
            return False, "Nothing new"
        if a["id"] != "talk" and who in store.spent_today:
            return False, "Later"
        if a["cost"] and store.stamina < 10:
            return False, "Too tired"
        return True, None

    def activities_for(who, loc=None):
        """[(activity, available, reason)] — hidden ones already filtered out."""
        out = []
        for a in ACTIVITIES:
            ok, why = activity_state(a, who, loc)
            if not ok and why is None:
                continue                            # not applicable to this person
            out.append((a, ok, why))
        return out

    def next_unlock(who):
        """The cheapest thing still out of reach, for the 'coming up' line."""
        best = None
        for a, ok, why in activities_for(who):
            if ok or not why or why in ("Later", "Done", "Nothing new", "Too tired"):
                continue
            if why.startswith(("Bond", "♡")):
                n = int(why.split()[-1])
                if best is None or n < best[0]:
                    best = (n, a["label"], why)
        return best

    def lesson_ok():
        """WP7. Gojo's lesson is on: he is in today (gojo_in_today) and I
        haven't had one yet today."""
        return bool(gojo_in_today()) and "lesson" not in store.actions_today

    ## Training with someone grows them too (3.4): activity -> (n, my stat).
    ## Train goes through sb_spar, which calls train_together itself.
    TRAIN_TOGETHER = {"study": (2, "insight"), "swim": (1, None), "walk": (1, None)}

    ## Person view ranking (section 6).
    _MILESTONES = ("rom_say", "stand", "confide")
    _ROMANCE_PICKS = ("int_night", "int_morning", "int_day", "int_after", "rom_close", "rom_town")

    def _choice_ok(aid, who, loc):
        a = ACT_BY_ID.get(aid)
        return bool(a) and activity_state(a, who, loc)[0]

    def _choice_do(aid):
        a = ACT_BY_ID[aid]
        return dict(kind="do", id=aid, label=a["label"], hint=a["hint"], cost=a["cost"],
                    gold=False, romance=(a["kind"] in ("romance", "confession", "intimate")))

    def _choice_special(who, loc):
        """The person-specific action: Utahime's board, Gojo's lesson,
        Ijichi's car."""
        if who == "utahime" and loc == "utahime_office" and board_open():
            return dict(kind="act", id="board", label="Mission board", hint="Graded jobs. Bring someone.",
                        cost=0, gold=False, romance=False)
        if who == "gojo" and loc == "gojo_office" and _choice_ok("lesson", who, loc):
            return _choice_do("lesson")
        if who == "ijichi" and loc == "gate" and car_action_ok():
            return dict(kind="act", id="car", label="Ask Ijichi for a ride", hint="Into the city. Half a day.",
                        cost=2, gold=False, romance=False)
        return None

    def person_choices(who, loc=None):
        """WP7. Up to four ranked choices for the person view (section 6):
        [dict(kind="do"|"mission"|"act", id, label, hint, cost, gold=False,
        romance=False)], always ending with Talk. Up to three of: their first
        mission (gold); their own action (board, lesson, car); a milestone
        (Say it > They asked me > Tell them something true); Spend time
        together when there's a scene; one romance or intimate activity; the
        one activity that suits the place. Only available activities."""
        loc = loc or store.here
        out = []

        ## 1. A mission they can give.
        ms = [] if store.explore_mode else missions_with(who, loc)
        if ms:
            mid, title, hint = mission_view(ms[0])
            out.append(dict(kind="mission", id=mid, label=title, hint=hint, cost=0,
                            gold=True, romance=False))

        ## 2. Their own action.
        sp = _choice_special(who, loc)
        if sp and len(out) < 3:
            out.append(sp)

        ## 3. A milestone.
        for aid in _MILESTONES:
            if len(out) < 3 and _choice_ok(aid, who, loc):
                out.append(_choice_do(aid))
                break

        ## 4. A bond scene.
        if len(out) < 3 and _choice_ok("hang", who, loc):
            out.append(_choice_do("hang"))

        ## 5. One romance or intimate activity.
        for aid in _ROMANCE_PICKS:
            if len(out) < 3 and _choice_ok(aid, who, loc):
                out.append(_choice_do(aid))
                break

        ## 6. The one activity that suits the place, in section 6's order.
        for aid in ("eat", "train", "swim", "stargaze", "study", "walk"):
            if len(out) < 3 and _choice_ok(aid, who, loc):
                out.append(_choice_do(aid))
                break

        ## 7. Talk, always, last.
        out.append(_choice_do("talk"))
        return out


## Staging someone for an activity (5.1) ########################################
##
## Puts the person on screen, with the face they look up with (or `expr`), at
## pos_c over the place, before Talk and every act_*, so they stay there while
## we talk. Hangouts stage themselves.

label stage_person(who, expr=None):
    scene expression graded_bg()
    $ renpy.show(person_image(who, expr), at_list=[pos_c])
    with Dissolve(0.3)
    return


## Gojo's lesson (5.3) ##########################################################

label act_lesson(who):
    ## PLACEHOLDER — rewrite in phase 3
    $ actions_today.add("lesson")
    $ _v = day % 3

    if _v == 0:
        gojo happy "Oh, good, a student. Sit, sit. Not that one, that's the mochi chair."
        "He turns the television off with his foot. The blindfold stays on."
        gojo "Question. When you hold a second, where does the rest of the world go?"
        mc "Nowhere. It waits."
        gojo serious "Wrong. It doesn't know it's waiting. That's the part you should find scary."
        "He puts a sweet on the table between us and tells me to stop him picking it up. I stop the second. I can't hold it long enough to do anything with it, and when it starts again he picks the sweet up as if I hadn't."
        gojo happy "See? You're good. I'm just better. Eat that, it's a reward."
        "Walking out, my control feels tighter, like something in me has been tuned half a turn."

    elif _v == 1:
        gojo happy "[mc_name]! Perfect timing. I was about to be bored."
        gojo "Today's lesson is breathing. Don't make that face. Everyone breathes wrong."
        "He has me hold a thread of cursed energy in one fingertip for as long as I can, and talks about sweets the whole time, on purpose."
        gojo serious "There. You dropped it when I said 'daifuku'. A curse won't say daifuku. It'll do something much worse."
        "We go again, and again. By the ninth try I can hold it through a whole story about a cake shop in Kyoto."
        gojo happy "Good! Your reserve's a little deeper. Don't tell Yaga I taught you something. He'll expect it every week."

    else:
        gojo "Come in. Close the door. No, leave it open. It's funnier."
        gojo serious "Hold a second for me. Right now. Go."
        "I reach for the instant the lights went out and put my weight on it. The room stops."
        "Everything stops except him. Inside my second, he tilts his head and waves."
        gojo happy "Hi."
        "I let go so fast the television flickers."
        gojo "Don't panic. Almost nobody can move in there. I'm not almost nobody."
        gojo "Still. If I can walk in, your second has a door in it. Let's find out where."
        "We spend most of an hour finding out where. I leave with a headache and the feeling that I've been measured."

    $ gain("control", 5)
    $ raise_reserve(5)
    return


## Who is currently tagging along ###############################################

default companion = None

## People you have already spent a period with today (talking is free). Cleared
## by new_day() in sb_world.rpy.
default spent_today = set()
