################################################################################
## Cursed Bonds — activities.
##
## What you can do with a person, and what it takes to unlock it. Locked
## activities stay visible with their requirement showing, because seeing what
## is still out of reach is most of what makes a relationship system feel deep.
################################################################################

init -1 python:

    ## kind:  "friend" — available to everyone
    ##        "romance" — only for romanceable characters, gated on affection
    ## who:   None = anyone, or a tuple of keys
    ## loc:   None = anywhere, or a tuple of location keys
    ## per:   None = any period, or a tuple of period names
    ## cost:  periods it takes (0 = free). Required on every entry.

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

        dict(id="invite",   label="Ask them along",    hint="They'll follow you for the rest of the day.",
             kind="friend", min_bond=45, cost=0),

        dict(id="stargaze", label="Sit out with them", hint="The roof, and a hundred kilometres of dark.",
             kind="friend", min_bond=50, cost=1, loc=("rooftop", "ridge", "riverside"),
             per=("Evening", "Night")),

        dict(id="confide",  label="Tell them something true", hint="Something you haven't said to anyone here.",
             kind="friend", min_bond=65, cost=1, once=True),

        ## The top of the friendship track. You have spent the whole game being
        ## the one who needs things; here it goes the other way.
        dict(id="stand",    label="They asked you for something",
             hint="It took them a while to work up to it.",
             kind="friend", min_bond=80, cost=2, once=True,
             requires_flag="confided_"),

        ## ---- romance ------------------------------------------------------
        dict(id="rom_town", label="Ask them into town", hint="A whole afternoon, off the mountain.",
             kind="romance", min_bond=50, min_aff=30, cost=2,
             loc=("gate", "courtyard")),

        dict(id="rom_close", label="Stay a while longer", hint="Neither of you moves to go.",
             kind="romance", min_bond=60, min_aff=45, cost=1,
             per=("Evening", "Night")),

        ## The ceiling scene: appears only when affection has nowhere left to go,
        ## and lifts the lid so it can keep going.
        dict(id="rom_say",  label="Say it",             hint="Out loud. Badly, probably.",
             kind="confession", min_bond=85, min_aff=100, cost=2, once=True),

        ## ---- after the confession ----------------------------------------
        dict(id="int_night", label="Stay the night",    hint="Neither of you suggests you go.",
             kind="intimate", min_aff=110, cost=1, per=("Evening", "Night")),

        dict(id="int_morning", label="Wake up with them", hint="The first hour, before anyone needs anything.",
             kind="intimate", min_aff=130, cost=1, per=("Morning",)),

        dict(id="int_day",  label="A day off. Just you two.", hint="No training, no missions, no map.",
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
            names = ", ".join(LOCATIONS[l]["name"] for l in a["loc"][:2])
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

    def person_choices(who, loc=None):
        """WP7. Up to four ranked choices for the person view (section 6):
        [dict(kind="do"|"mission"|"act", id, label, hint, cost, gold=False,
        romance=False)], always ending with Talk. (WP0 stub: [].)"""
        return []


## Staging someone for an activity (5.1) ########################################
##
## WP7: puts the person on screen (their greeting face, at pos_c, over the
## place) before Talk and every act_*, so they stay there while you talk.
## (WP0 stub: returns.)

label stage_person(who, expr=None):
    return


## Who is currently tagging along ###############################################

default companion = None

## People you have already spent a period with today (talking is free). Cleared
## by new_day() in sb_world.rpy.
default spent_today = set()
