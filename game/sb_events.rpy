################################################################################
## Cursed Bonds — the event engine.
##
## Content files register events at init; the sandbox loop asks this module
## which one to fire. Nothing here knows what any individual scene contains.
################################################################################

init -1 python:

    EVENTS = []

    def ev(label, kind="hangout", who=None, loc=None, periods=None, weekend=None,
           min_bond=0, min_aff=0, max_bond=101, requires=(), forbids=(),
           once=True, arc=1, priority=0,
           min_day=0, max_day=9999, thread=None):
        """Register an event. `label` is the Ren'Py label that plays it."""
        EVENTS.append(dict(
            label=label, kind=kind, who=who, loc=loc, periods=periods,
            weekend=weekend, min_bond=min_bond, min_aff=min_aff, max_bond=max_bond,
            requires=tuple(requires), forbids=tuple(forbids), once=once, arc=arc,
            priority=priority,
            min_day=min_day, max_day=max_day, thread=thread,
        ))

    def _loc_ok(e, loc):
        want = e.get("loc")
        if not want:
            return True
        if isinstance(want, str):
            return loc == want
        return loc in want

    def find_events(kind, who=None, loc=None):
        loc = loc or store.here
        out = []
        for e in EVENTS:
            if e["kind"] != kind:
                continue
            if e["who"] and e["who"] != who:
                continue
            if not _loc_ok(e, loc):
                continue
            if e["periods"] and store.period not in e["periods"]:
                continue
            if e["weekend"] is not None and is_weekend() != e["weekend"]:
                continue
            if e["arc"] > store.arc:
                continue
            ## min_day / max_day are no longer read here (D40): the story waits
            ## for you. Pacing comes from the registered gates below.
            if e["once"] and e["label"] in store.done_events:
                continue
            w = e["who"]
            if w:
                b = store.bonds.get(w, 0)
                if b < e["min_bond"] or b >= e["max_bond"]:
                    continue
                if store.affection.get(w, 0) < e["min_aff"]:
                    continue
            if any(not has_flag(f) for f in e["requires"]):
                continue
            if any(has_flag(f) for f in e["forbids"]):
                continue
            if not event_allowed(e):
                continue
            out.append(e)
        return out

    def pick_event(kind, who=None, loc=None):
        """The most advanced event you've unlocked, ties broken at random."""
        cands = find_events(kind, who, loc)
        if not cands:
            return None
        def tier(e):
            ## Explicit priority first, so a story beat always beats filler.
            return (e["priority"], e["min_bond"] + e["min_aff"] * 2)
        best = max(tier(e) for e in cands)
        return renpy.random.choice([e for e in cands if tier(e) == best])

    def has_event(kind, who=None, loc=None):
        return bool(find_events(kind, who, loc))

    def mark_done(label):
        store.done_events.add(label)


default done_events = set()


################################################################################
## Playing an event
################################################################################

label play_event(e):
    $ mark_done(e["label"])
    call expression e["label"]
    ## An event can declare the thread stage it represents; the engine moves it,
    ## so individual scenes stay free of bookkeeping.
    if e["thread"]:
        $ advance_thread(e["thread"][0], e["thread"][1])
    $ run_event_done(e)
    return


## Generic filler so "Talk" always has something to say. ########################

label sb_smalltalk(who):

    $ _c = CAST[who]
    $ _n = _c["short"]

    if who in talked_today:
        "[_n] is busy with something. I leave it."
        return

    $ talked_today.add(who)
    $ add_bond(who, 1)

    ## Someone promoted since we last talked says so first (D12), instead of
    ## the small talk.
    $ _line = promo_line(who)
    if _line is None:
        $ _lines = SMALLTALK.get(who, SMALLTALK["_default"])
        $ _line = renpy.random.choice(_lines)

    $ renpy.say(CHARS[who], _line)

    return


init -1 python:

    SMALLTALK = {
        "_default": [
            "Hey. You settling in okay?",
            "Long day. They're all long days.",
            "Gojo-sensei's off doing something. Nobody knows what.",
        ],
        "yuji": [
            "Oh hey! You eaten? You look like you haven't eaten.",
            "I did four hundred push-ups. I don't feel great about it.",
            "Do you think Megumi's dogs like me? Be honest.",
            "Okay so hypothetically — could a person outrun a train. Hypothetically.",
        ],
        "megumi": [
            "...Hm.",
            "If you're going to the ridge, take water. People forget.",
            "Itadori's looking for you. He didn't say why. He never says why.",
            "You've been training. It shows in how you stand.",
        ],
        "nobara": [
            "Do NOT tell me you're wearing that on a mission.",
            "I found a place in town that does nails for half what Tokyo charges.",
            "Fushiguro said eleven words today. I counted. New record.",
            "You look tired. Sleep. That's not concern, that's logistics.",
        ],
        "maki": [
            "Dojo. Dawn. Don't be late, I don't wait.",
            "Your left shoulder still drops. Fix it before something notices.",
            "Cursed energy is a crutch. Have a second leg.",
            "You've got about nine hundred repetitions left before that's yours.",
        ],
        "panda": [
            "Welfare check. You look like a rumour. Eat something.",
            "Inumaki says hello. That was 'hello'. Trust me.",
            "You ever think about how weird it is that I'm a panda? I do. Constantly.",
            "The second-years look out for the first-years. That's the whole system.",
        ],
        "toge": [
            "Salmon.",
            "Tuna mayo.",
            "Bonito flakes!",
            "Mustard leaf...",
        ],
        "shoko": [
            "You're not bleeding. That makes you my favourite person today.",
            "If you feel dizzy after training, that's cursed energy debt. Eat. Sleep.",
            "I've stitched every single person in this school back together. Including the panda.",
            "Don't tell Yaga about the cigarettes.",
        ],
        "gojo": [
            "Oh! You found me. Nobody finds me. That's actually impressive.",
            "I'm technically supposed to be teaching right now. Don't tell Yaga.",
            "Sweets? I've got sweets. I've always got sweets.",
            "You're getting stronger. I can see it from here. Literally, I can see it.",
        ],
        "yaga": [
            "If you're not here about a mission, be brief.",
            "Your file says your control is improving. Files are optimistic.",
            "The storehouse is not a museum. Don't touch what you can't name.",
        ],
        "utahime": [
            "If you're here for a job, the board is on the wall. If you're here to chat, I'm working.",
            "Take someone with you. Every time. I don't care what the file says.",
            "If Gojo sent you, the answer is no. If he didn't, sit up straight.",
            "Read the whole report before you go. Tokyo's files have a habit of being one grade kind.",
        ],
        "ijichi": [
            "Ah — good morning. Or afternoon. Sorry, I've been in the car since five.",
            "If Gojo-san asks where I am, you haven't seen me. Please. You haven't.",
            "Gojo-san asked me to buy forty mochi. I'm told it's for a meeting.",
            "I have three reports due, and one of them is about the other two.",
        ],
    }

    ## What a student says the first time you talk after they're promoted
    ## (D12), in place of small talk. %(grade)s is their new grade.
    ## maki and toge can't be promoted with today's NPC_BASE caps (Maki is
    ## held at Grade 4, Toge is already semi-grade 1): their lines are
    ## unreachable for now and kept so every student has one.
    PROMO_LINES = {
        "yuji":   "Guess who's %(grade)s now! Me! I don't really know what it means, but Megumi said \"fine\", and I think that's his version of a party.",
        "megumi": "%(grade)s. It's paperwork. It means they send me further away, that's all.",
        "nobara": "%(grade)s. Don't make a face, you'll catch up. Probably.",
        "maki":   "%(grade)s. Somebody in Kyoto is going to choke on that. Good.",
        "panda":  "%(grade)s! Yaga says he isn't proud. He said it twice, which means he is.",
        "toge":   "Salmon! ...Tuna mayo.",
    }

    def promo_line(who):
        """WP3. The promotion remark someone makes instead of small talk, or
        None. Uses up the pending remark (pop_remark) only for someone who
        has a line."""
        if who not in PROMO_LINES or not pop_remark(who):
            return None
        grade = npc_stats(who).get("grade")
        return PROMO_LINES[who] % dict(grade=grade_label(grade))
