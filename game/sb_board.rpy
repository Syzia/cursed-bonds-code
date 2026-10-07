################################################################################
## Cursed Bonds — Utahime's board of graded jobs.
##
## WP4 owns this file (PHASE1_DESIGN.md 3.7, 4.8, D12, D13).
##
## The board is a place action ("board") at Utahime's office. Each week it
## posts three jobs built from parts (a case, a place, a curse, a twist): two
## at or below my grade and one a grade up that needs a senior partner. I take
## one with a partner; phase 1 narrates it and resolves it automatically
## (phase 3 turns it into a fight), then pays merit, yen, bond and sometimes a
## drop, exactly once. About one job in six at Grade 4 or 3 is misgraded: the
## curse inside is a grade heavier than the card. That is Wakuri's hand.
##
## Flow:  label sb_do_board -> screen board_screen -> screen board_partner(offer)
##        -> label run_board_mission(offer_id, who)
##
## Saved state is plain data only: board_offers (offers, and the cards I took
## until their replacement goes up), board_week, board_log (the last 30 runs)
## and board_misgrades.
################################################################################

init -1 python:
    import random as _board_random
    import zlib as _board_zlib

    ## The parts (3.7) ---------------------------------------------------------

    BOARD_GRADES = ["g4", "g3", "g2", "s1"]

    BOARD_CASES = ["Missing persons", "A haunting", "Residual clean-up",
                   "A school after hours", "Unexplained injuries", "Livestock deaths"]

    ## phrase: how the narration says it; short: the card's title; bg: the
    ## picture the job plays over. The second overhaul (U0c2; docs/UI2_DESIGN.md
    ## 5.8, 3.1): five kinds of job site, each an image name of its own that
    ## always exists (bg_placeholders.rpy defines it with a stand-in until
    ## images/bg/site_<kind>.png is painted), so a job no longer plays over
    ## a picture that belongs to another scene.
    BOARD_PLACES = [
        dict(key="nerima",    phrase="a drainage tunnel in Nerima",                  short="The Nerima Tunnel",      bg="bg site_tunnel"),
        dict(key="adachi",    phrase="a closed maternity ward in Adachi",            short="The Adachi Ward",        bg="bg site_ward"),
        dict(key="ikebukuro", phrase="a dead platform under Ikebukuro",              short="The Dead Platform",      bg="bg site_platform"),
        dict(key="setagaya",  phrase="an after-hours school pool in Setagaya",       short="The Setagaya Pool",      bg="bg site_pool"),
        dict(key="kita",      phrase="an apartment stairwell in Kita",               short="The Kita Stairwell",     bg="bg site_ward"),
        dict(key="shinagawa", phrase="a train depot in Shinagawa",                   short="The Shinagawa Depot",    bg="bg site_platform"),
        dict(key="edogawa",   phrase="a riverbank underpass in Edogawa",             short="The Edogawa Underpass",  bg="bg site_tunnel"),
        dict(key="koenji",    phrase="a karaoke box in Koenji that closed mid-song", short="The Koenji Karaoke Box", bg="bg site_karaoke"),
    ]
    BOARD_PLACE_BY_KEY = dict((p["key"], p) for p in BOARD_PLACES)

    BOARD_CURSES = {
        "g4": ["a residual that eats light bulbs", "a stairwell crawler", "a grudge the size of a dog"],
        "g3": ["a mimic that uses the missing person's voice", "a nest of finger-length curses", "a pool drowner"],
        "g2": ["a curse that only moves in the dark", "a platform pusher", "a thing wearing the building"],
        "s1": ["a named curse with a domain it can't close yet", "a crowd that is one curse"],
    }

    ## Which parts fit together, so a card doesn't put a school at a train
    ## depot or a stairwell crawler in a karaoke box. A part that isn't listed
    ## fits everywhere. Offers pick the place first, then a case and a curse
    ## that fit it (falling back to any, if nothing fits).
    BOARD_CASE_FITS = {                      # case -> places
        "A school after hours": ("setagaya",),
        "Livestock deaths": ("edogawa", "nerima"),
    }
    BOARD_CURSE_FITS = {                     # curse -> places
        "a stairwell crawler": ("kita", "adachi"),
        "a pool drowner": ("setagaya", "edogawa"),
        "a platform pusher": ("ikebukuro", "shinagawa"),
        "a thing wearing the building": ("adachi", "kita", "koenji", "shinagawa"),
    }
    BOARD_CURSE_CASE = {                     # curse -> cases
        "a mimic that uses the missing person's voice": ("Missing persons",),
    }

    ## key -> (difficulty modifier, card line, weight when posting)
    BOARD_TWISTS = {
        "dark":     (4,  "It only moves in the dark", 1),
        "civilian": (6,  "Someone is still inside", 1),
        "split":    (5,  "There are two of them", 1),
        "decoy":    (3,  "The reported curse is a decoy", 1),
        "daylight": (-3, "It sleeps in daylight", 1),     # the -3 counts in the Morning only
        "none":     (0,  "", 3),
    }
    BOARD_TWIST_ORDER = ["dark", "civilian", "split", "decoy", "daylight", "none"]

    ## Numbers (3.7). Tuning lives here, never in the code below.
    BOARD_DIFFICULTY = {"g4": 30, "g3": 55, "g2": 80, "s1": 110}      # by the TRUE grade
    BOARD_MERIT = {"g4": 10, "g3": 18, "g2": 28, "s1": 40}             # by the posted grade
    BOARD_YEN = {"g4": (3000, 6000), "g3": (6000, 10000), "g2": (10000, 15000), "s1": (15000, 20000)}
    BOARD_OUTCOME_MERIT = {"clean": 1.0, "costly": 0.6, "withdrew": 0.0}
    BOARD_BOND = {"clean": 5, "costly": 6, "withdrew": 2}
    BOARD_MISGRADE_RATE = 1.0 / 6.0     # g4 and g3 postings only
    BOARD_STAMINA = 25
    BOARD_PERIODS = 2
    BOARD_TRAIN_XP = 6                  # train_together(partner, 6)
    BOARD_LOG_MAX = 30

    ## Drops: 30% a sealing talisman; 10% a not-yet-owned talisman of the
    ## posted grade; 5% a not-yet-owned cursed tool of the posted grade (the
    ## storyboard's "sometimes a cursed tool"), but only once Maki has opened
    ## the armory (armory_open, D10) and only a tool at or below my grade.
    ## Only when the job got done: a withdrawn job pays no yen and no drops.
    BOARD_SEALING = ("sealing_talisman", 0.30)
    BOARD_TALISMAN_CHANCE = 0.10
    BOARD_TALISMAN_DROPS = {"g4": ("paper_ward", "steady_hand"), "g3": ("deep_well", "iron_seal")}
    BOARD_TOOL_CHANCE = 0.05
    BOARD_TOOL_DROPS = {"g4": ("slaughter_demon",), "g3": ("nunchaku",)}

    ## Every item the board can drop, with the card's name for it while ITEMS
    ## (WP6) doesn't know the id.
    BOARD_ITEM_NAMES = {
        "sealing_talisman": "Sealing talisman", "paper_ward": "Paper Ward",
        "steady_hand": "Steady Hand", "deep_well": "Deep Well", "iron_seal": "Iron Seal",
        "slaughter_demon": "Slaughter Demon", "nunchaku": "Nunchaku",
    }

    ## Phase 2 (4.8): the board's grades in the game's grade colours (the
    ## gui.grade_* tokens; Semi-Grade 1 shares Grade 1's red). The chips are
    ## drawn by grade_chip (sb_grades.rpy); this table stays for readers.
    BOARD_GRADE_COLOR = {"g4": gui.grade_g4, "g3": gui.grade_g3, "g2": gui.grade_g2, "s1": gui.grade_g1}

    ## Never partners (teachers, the doctor, the driver, the dead), whatever
    ## their grade. Anyone else rostered with a grade can come, if on campus.
    BOARD_NOT_PARTNERS = ("gojo", "yaga", "utahime", "shoko", "ijichi", "sana")

    ## Partner lines (3.7): (narration around it, expression, their line).
    ## First person; each partner as they are in Season 1.
    BOARD_PARTNER_KEYS = ["yuji", "megumi", "nobara", "maki", "panda", "toge"]

    PARTNER_LINES = {
        "yuji": dict(
            arrive=("Yuji is already stretching by the time the veil finishes coming down, bouncing on his toes like this is a school trip.",
                    "happy", "Okay! Where is it? I'll hit it, you do the clock thing."),
            win=("Yuji puts the last of it through the floor and turns round grinning, knuckles steaming.",
                 "happy", "That was so cool. The second where everything stopped? Do that again next time."),
            hurt=("Yuji sits down hard against the wall with his arm held wrong, and laughs anyway.",
                  "sad", "I'm fine. I'm fine! ...Don't tell Ieiri-san I said I'm fine."),
        ),
        "megumi": dict(
            arrive=("Megumi reads the file once, hands it back, and brings a Divine Dog up out of his shadow without looking at it.",
                    "serious", "Stay where I can see you."),
            win=("Megumi lets the dog sink back into his shadow and checks the corners anyway. From him, the next two words are a speech.",
                 "neutral", "Clean. Good."),
            hurt=("Megumi's breathing is wrong, and he is pretending it isn't.",
                  "angry", "We should have let it move first. My call. My mistake."),
        ),
        "nobara": dict(
            arrive=("Nobara looks the place up and down like it owes her money.",
                    "neutral", "What a dump. Let's make this quick. I have plans, and they don't involve smelling like this."),
            win=("Nobara taps the last nail home with her hammer and blows the hair out of her face.",
                 "happy", "Admit it. I was the best part of that."),
            hurt=("Nobara is bleeding from the hairline and far angrier about her jacket.",
                  "angry", "This was new. Do you know what this cost? That thing is going to pay for it. Maybe not today, but it's going to pay."),
        ),
        "maki": dict(
            arrive=("Maki checks the veil, then her staff, then me, in that order.",
                    "serious", "Stay behind me until I say otherwise. Then don't hesitate."),
            win=("Maki spins the staff once and rests it across her shoulders.",
                 "happy", "Not bad. You didn't flinch. Keep that."),
            hurt=("Maki wipes her mouth with the back of her hand and looks at the blood as if it has insulted her.",
                  "serious", "That's what happens when you let it pick the ground. Remember it."),
        ),
        "panda": dict(
            arrive=("Panda rolls his shoulders, looks up at the black dome over us and sniffs the air.",
                    "happy", "Smells like a curse. Also like old gym socks. Could be the same thing."),
            win=("Panda dusts off his paws and holds one up for a high five I can't possibly refuse.",
                 "happy", "Nice work, partner. You're getting less stiff. In the head, I mean."),
            hurt=("Panda's shoulder is torn open, and there is stuffing, or something like stuffing, where there shouldn't be.",
                  "sad", "Don't look at it like that. Yaga'll stitch it. He'll lecture me the whole time, but he'll stitch it."),
        ),
        "toge": dict(
            arrive=("Toge pulls his collar down just far enough to show the seal at the corner of his mouth, and raises a thumb. I think it means he's ready.",
                    "neutral", "Salmon."),
            win=("Toge gives me two thumbs up and a very smug pair of eyes over the collar.",
                 "happy", "Tuna mayo!"),
            hurt=("Toge coughs into his sleeve, and it comes away speckled. He spent his voice on it for me, and he waves me off before I can thank him.",
                  "sad", "...Kelp."),
        ),
    }

    ## The job, in first person, from the parts ---------------------------------

    BOARD_TWIST_LINES = {
        "dark": "The file was right about one thing: it only moves in the dark, and somebody has broken every bulb in here.",
        "civilian": "Someone is still inside: a man in a work jacket, pressed into a corner, too frightened to answer when we call. We have to work around him.",
        "split": "There are two of them, just as the card warned. The report inside only ever describes one; the other has been careful to stay out of it.",
        "decoy": "The reported curse is a decoy, a husk left where it would be seen. The real one is further in, and it has been waiting.",
        "daylight": "It sleeps in daylight, and we've come in the morning. It is slow and half-formed when we find it.",
        "daylight_late": "It sleeps in daylight, but the day is getting on, and it is already awake when we find it.",
    }

    BOARD_OUTCOME_LINES = {
        "clean": "I hold the second. The colour drains out of everything but one warm light, the curse hangs mid-lunge, and when the world starts again %s is already there to finish it.",
        "costly": "I hold the second a beat too late. We finish it, but it takes the long way round, and it takes a piece out of both of us on the way.",
        "withdrew": "It is more than we can take. I hold the second just long enough to get %s clear, and we back out through the veil with it still screaming behind us.",
        ## A withdrawal with someone still inside doesn't leave them there.
        "withdrew_civilian": "It is more than we can take. I hold the second just long enough to get %s and the man clear, and we back out through the veil with it still screaming behind us.",
    }

    ## The host's word when we come back: (expression, line). "misgraded"
    ## takes the posted grade's name.
    BOARD_HOST_LINES = {
        "utahime": dict(
            clean=("serious", "Clean work. Write the report properly. Not the way Gojo writes reports."),
            costly=("angry", "You finished it, and now you're bleeding on my floor. Infirmary first. Then the report."),
            withdrew=("serious", "You came back. Good. A first-year who comes back is worth more to me than a closed file."),
            misgraded=("surprised", "That was filed as %s? ...Leave the report with me. I want to know who signed it."),
        ),
        "ijichi": dict(
            clean=("neutral", "Filed. Thank you both. Please let Ieiri-san look at you anyway."),
            costly=("surprised", "Oh. Oh no. The infirmary first, please. I'll do the paperwork."),
            withdrew=("serious", "You withdrew. That was the right call. I'll... I'll explain it upstairs."),
            misgraded=("serious", "Filed as %s? That's... I'll send this to the Grading Office. Quietly."),
        ),
    }

    ## Where the board is (D13) --------------------------------------------------

    def board_host():
        """WP4. (who, place) running the board: Utahime at her office, or
        Ijichi at Yaga's once the flag utahime_leads_kyoto is set (D13)."""
        if has_flag("utahime_leads_kyoto"):
            return ("ijichi", "office")
        return ("utahime", "utahime_office")

    ## D13: said on the board itself while it is Ijichi's.
    BOARD_MOVED_LINE = "Utahime-sensei has gone to lead Kyoto. Her board is with Ijichi in Yaga's office now, and he apologises for it."

    def board_host_note():
        """WP4. The line saying the board has moved (D13), or "" while it is
        still Utahime's."""
        return BOARD_MOVED_LINE if board_host()[0] != "utahime" else ""

    def board_open():
        """WP4. True when the board can be used here and now: the flag
        mission_board_open, I'm at the host's place, and the host is there
        this period. An old save's mission_board_open (from the retired
        st_board_open) opens nothing until Utahime is rostered, because an
        unrostered character has no location."""
        if store.explore_mode or not has_flag("mission_board_open"):
            return False
        who, place = board_host()
        return store.here == place and char_location(who) == place

    def _board_host_name():
        return CAST.get(board_host()[0], {}).get("short", "Utahime")

    ## Grades --------------------------------------------------------------------

    def _board_player_rank():
        ## Grade 4 while unassessed (D16).
        return max(0, grade_rank(player_grade() or "g4"))

    def _board_player_key():
        ## The board's grade for me; above Semi-Grade 1 the board has nothing
        ## higher to post, so it posts Semi-Grade 1.
        k = grade_key(player_grade()) or "g4"
        if k in BOARD_GRADES:
            return k
        return "s1"

    def _board_next(key):
        i = BOARD_GRADES.index(key) + 1
        return BOARD_GRADES[i] if i < len(BOARD_GRADES) else None

    def _board_prev(key):
        i = BOARD_GRADES.index(key) - 1
        return BOARD_GRADES[i] if i >= 0 else None

    def _board_npc_grade(who):
        try:
            return npc_stats(who).get("grade")
        except Exception:
            return None

    def _board_tool_ok(tool_grade):
        ## Tools drop only once the armory is open, and only up to my grade (D10).
        return has_flag("armory_open") and grade_rank(tool_grade) <= _board_player_rank()

    def board_drops_now(offer):
        """WP4. What this offer can still drop for me now: the sealing
        talisman, the grade's talismans I don't own, and (armory open, at or
        below my grade) its tools I don't own."""
        out = []
        for iid in offer.get("drop", ()):
            if iid == BOARD_SEALING[0]:
                out.append(iid)
            elif _board_owned(iid):
                continue
            elif iid in BOARD_TOOL_DROPS.get(offer.get("grade"), ()):
                if _board_tool_ok(offer.get("grade")):
                    out.append(iid)
            else:
                out.append(iid)
        return out

    def board_needs_senior(offer):
        """WP4. True when a job is above my grade, so it needs a senior partner."""
        return grade_rank(offer.get("grade")) > _board_player_rank()

    ## Offers ----------------------------------------------------------------------

    def board_week_now():
        """WP4. The board's week. Day 1 is a Monday, so weeks start on Mondays."""
        return (store.day - 1) // 7

    def _board_rng(*parts):
        seed = _board_zlib.crc32("|".join(str(p) for p in parts).encode("utf-8")) & 0xffffffff
        return _board_random.Random(seed)

    def _board_item_name(iid):
        return ITEMS.get(iid, {}).get("name") or BOARD_ITEM_NAMES.get(iid, iid)

    def _board_owned(iid):
        return (has_item(iid) or getattr(store, "equipped_tool", None) == iid
                or iid in (getattr(store, "equipped_talismans", None) or ()))

    def _board_fits(part, table, value):
        ## A part fits unless its table lists it for other values only.
        return part not in table or value in table[part]

    def _board_pick(rng, parts, fit, avoid):
        ## Fitting and not yet on the board; else fitting; else not on the
        ## board; else anything.
        for pool in ([p for p in parts if fit(p) and p not in avoid],
                     [p for p in parts if fit(p)],
                     [p for p in parts if p not in avoid]):
            if pool:
                return rng.choice(pool)
        return rng.choice(parts)

    def board_curses_for(grade, place, case):
        """WP4. The grade's curses that fit this place and case (all of them
        if none fit)."""
        c = [k for k in BOARD_CURSES[grade] if _board_fits(k, BOARD_CURSE_FITS, place)
             and _board_fits(k, BOARD_CURSE_CASE, case)]
        return c or list(BOARD_CURSES[grade])

    def _board_make_offer(rng, grade, senior, oid, avoid=()):
        """One posting at `grade`, built from the parts with rng: the place
        first, then a case and a curse that fit it. `avoid` holds the places,
        cases and curses already on the board, so a week's cards don't repeat
        one another where the parts allow."""
        places = [p for p in BOARD_PLACES if p["key"] not in avoid] or BOARD_PLACES
        place = rng.choice(places)
        pk = place["key"]
        case = _board_pick(rng, BOARD_CASES, lambda c: _board_fits(c, BOARD_CASE_FITS, pk), avoid)
        curse = _board_pick(rng, BOARD_CURSES[grade],
                            lambda k: _board_fits(k, BOARD_CURSE_FITS, pk) and _board_fits(k, BOARD_CURSE_CASE, case),
                            avoid)
        weights = [BOARD_TWISTS[t][2] for t in BOARD_TWIST_ORDER]
        pick = rng.random() * sum(weights)
        twist = BOARD_TWIST_ORDER[-1]
        for t, w in zip(BOARD_TWIST_ORDER, weights):
            if pick < w:
                twist = t
                break
            pick -= w
        true_grade = grade
        if rng.random() < BOARD_MISGRADE_RATE and grade in ("g4", "g3"):
            true_grade = _board_next(grade)       # Wakuri's hand
        drop = ([BOARD_SEALING[0]] + list(BOARD_TALISMAN_DROPS.get(grade, ()))
                + list(BOARD_TOOL_DROPS.get(grade, ())))
        where = place["phrase"][0].upper() + place["phrase"][1:]
        blurb = "%s. %s. The report says %s." % (case, where, curse)
        return dict(id=oid, grade=grade, true_grade=true_grade, case=case, place=place["key"],
                    curse=curse, twist=twist, title=place["short"], blurb=blurb,
                    merit=BOARD_MERIT[grade], yen=BOARD_YEN[grade], drop=drop,
                    senior_only=bool(senior))

    def _board_slot_grade(rng, slot, mine):
        """Slot 0 is at my grade, slot 1 at my grade or one below, slot 2 one
        grade up (senior_only), or at my grade when the board has nothing higher."""
        if slot == 2:
            up = _board_next(mine)
            return (up, True) if up else (mine, False)
        if slot == 1:
            below = _board_prev(mine)
            roll = rng.random()
            if below and roll < 0.4:
                return (below, False)
        return (mine, False)

    def board_generate(week=None):
        """WP4. A week's three offers, seeded with Random(week*7919 + 11): the
        same week always posts the same board (at the same grade of mine)."""
        if week is None:
            week = board_week_now()
        rng = _board_random.Random(week * 7919 + 11)
        mine = _board_player_key()
        out, used = [], []
        for slot in range(3):
            g, senior = _board_slot_grade(rng, slot, mine)
            o = _board_make_offer(rng, g, senior, "b%d.%d" % (week, slot), avoid=used)
            used += [o["place"], o["case"], o["curse"]]
            out.append(o)
        return out

    def _board_replacement(old, slot):
        """The card that goes up the day after one is taken, in the same slot."""
        week = board_week_now()
        rng = _board_random.Random(week * 7919 + 11 + store.day * 104729 + slot)
        mine = _board_player_key()
        g, senior = _board_slot_grade(rng, 2 if old.get("senior_only") else min(slot, 1), mine)
        avoid = [o.get(k) for o in store.board_offers if not o.get("taken_by") for k in ("place", "case", "curse")]
        return _board_make_offer(rng, g, senior, "b%d.%d.d%d" % (week, slot, store.day), avoid=avoid)

    def board_refresh():
        """WP4. Post this week's board if it isn't up yet (a new week, or a
        board that opened mid-week), and put up the replacement for any card
        I took on an earlier day. Idempotent within a day."""
        w = board_week_now()
        if store.board_week != w or not store.board_offers:
            store.board_offers = board_generate(w)
            store.board_week = w
            _board_npc_keep()
            return
        for i, o in enumerate(list(store.board_offers)):
            if o.get("taken_by") and o.get("day", store.day) < store.day:
                store.board_offers[i] = _board_replacement(o, i)
        _board_npc_keep()

    def _board_new_day():
        ## New-day hook: Mondays repost; yesterday's taken cards are replaced.
        if has_flag("mission_board_open"):
            board_refresh()

    def board_offers_open():
        """WP4. The offers I can still take, in slot order."""
        return [o for o in store.board_offers if not o.get("taken_by")]

    def board_find(offer_id):
        """WP4. The open offer with this id, or None."""
        for o in store.board_offers:
            if o.get("id") == offer_id and not o.get("taken_by"):
                return o
        return None

    ## Taken cards (D12) ---------------------------------------------------------

    def _board_students():
        return [w for w in ROSTER_ORDER if w in store.roster and w not in BOARD_NOT_PARTNERS
                and grade_rank(_board_npc_grade(w)) >= 0]

    def board_introduced():
        """WP4. True once the player has met the board: mission_board_open and
        its host rostered. An old save's mission_board_open (from the retired
        st_board_open) shows no board anywhere until Utahime's scene."""
        return has_flag("mission_board_open") and board_host()[0] in store.roster

    def _board_npc_above():
        mine = _board_player_rank()
        return [w for w in _board_students() if grade_rank(_board_npc_grade(w)) > mine]

    def _board_npc_keep():
        """WP11. Fix this week's senior card once it is picked (board_npc), so
        its taker, grade and place don't change when students join mid-week.
        Picked again only for a new week or when the taker no longer outranks
        me. Called from board_refresh, never from a screen."""
        kept = store.board_npc
        week = board_week_now()
        if isinstance(kept, dict) and kept.get("week") == week and kept.get("taken_by") in _board_npc_above():
            return
        card = _board_npc_pick()
        store.board_npc = dict(card, week=week) if card else None

    def board_npc_card():
        """WP4. While any rostered student outranks me, one read-only card,
        dict(taken_by=who, grade, title): "Grade 2 · taken by Megumi" (D12).
        Who took it rotates by week among the students above me; once the
        board has posted it for the week (board_npc) it stays. None until
        the board has been introduced."""
        if not board_introduced():
            return None
        kept = store.board_npc
        if (isinstance(kept, dict) and kept.get("week") == board_week_now()
                and kept.get("taken_by") in _board_npc_above()):
            return dict(taken_by=kept["taken_by"], grade=kept["grade"], title=kept["title"])
        return _board_npc_pick()

    def _board_npc_pick():
        """The senior card as it would be picked now, or None."""
        if not board_introduced():
            return None
        above = _board_npc_above()
        if not above:
            return None
        week = board_week_now()
        who = _board_rng("npc", week).choice(above)
        g = grade_key(_board_npc_grade(who))
        if g not in BOARD_GRADES:
            g = "s1"
        posted = [o.get("place") for o in store.board_offers]
        place = _board_rng("npcplace", week, who).choice([p for p in BOARD_PLACES if p["key"] not in posted] or BOARD_PLACES)
        return dict(taken_by=who, grade=g, title=place["short"])

    def board_taken_cards():
        """WP4. The read-only cards: jobs I took (until the replacement goes up
        the next day), then the one a senior student took."""
        out = [dict(o) for o in store.board_offers if o.get("taken_by")]
        npc = board_npc_card()
        if npc:
            out.append(npc)
        return out

    def board_card_line(card):
        """WP4. "Grade 2 · taken by Megumi", or "Grade 4 · taken by me and Yuji"."""
        who = card.get("taken_by")
        if who == "mc":
            mate = CAST.get(card.get("partner"), {}).get("short")
            name = ("me and " + mate) if mate else "me"
        else:
            name = CAST.get(who, {}).get("short", str(who))
        return "%s · taken by %s" % (grade_label(card.get("grade")), name)

    ## Partners --------------------------------------------------------------------

    def board_partner_rows(offer=None):
        """WP4. [(who, ok, reason, senior)] for every rostered student with a
        grade (never a teacher, the doctor or the driver)."""
        mine = _board_player_rank()
        need = bool(offer) and board_needs_senior(offer)
        rows = []
        for w in _board_students():
            senior = grade_rank(_board_npc_grade(w)) > mine
            if char_location(w) is None:
                rows.append((w, False, "Off campus right now", senior))
            elif need and not senior:
                rows.append((w, False, "This job needs someone senior to me", senior))
            else:
                rows.append((w, True, "", senior))
        return rows

    def board_partners(offer=None):
        """WP4. Who can come on a job: rostered, graded, not a teacher, the
        doctor or the driver, on campus now, and senior to me when the job is
        above my grade. Nobody goes alone ("Always take someone")."""
        return [w for w, ok, why, senior in board_partner_rows(offer) if ok]

    ## Rules -------------------------------------------------------------------------

    def board_take_reason(offer):
        """WP4. Why a card can't be taken right now, in the player's words, or ""."""
        if not night_can_work():        ## phase 2: a rest day (sb_night.rpy)
            return night_block_reason() or "Not today"
        if store.period in ("Evening", "Night"):
            return "Evenings: %s doesn't send anyone out after dark" % _board_host_name()
        if store.stamina < BOARD_STAMINA:
            return "Too tired — %d stamina" % BOARD_STAMINA
        if grade_rank(offer.get("grade")) > _board_player_rank() + 1:
            return "Above my grade"
        if not board_partners(offer):
            if board_needs_senior(offer):
                return "Needs a senior partner — none on campus"
            return "Nobody on campus to take along"
        return ""

    def board_refusal(offer, who):
        """WP4. The narration line that stops a run, or "" when it can go."""
        if not night_can_work():        ## phase 2: a rest day (sb_night.rpy)
            return night_block_reason() or "Not today."
        if not offer:
            return "That card is already off the board."
        if store.period in ("Evening", "Night"):
            return "%s doesn't send anyone out after dark." % _board_host_name()
        if store.stamina < BOARD_STAMINA:
            return "I'm too tired for a job. I need to eat, or sleep, first."
        if grade_rank(offer.get("grade")) > _board_player_rank() + 1:
            return "That job is above my grade."
        if who not in board_partners(offer):
            return "%s can't come on this one." % CAST.get(who, {}).get("short", "They")
        return ""

    ## Resolve (phase 1: automatic) ------------------------------------------------

    def board_resolve(offer, who, day=None, period=None):
        """WP4. A run's result, as a plain dict. power = (my power + 0.6 x the
        partner's) x a factor from 0.9 to 1.1 (seeded by offer id and day),
        against the TRUE grade's difficulty plus the twist. Yen and drops are
        rolled here too, so one run pays one fixed result."""
        day = store.day if day is None else day
        period = store.period if period is None else period
        rng = _board_rng(offer["id"], day)
        factor = 0.9 + 0.2 * rng.random()
        power = (float(sorcerer_power("mc")) + 0.6 * float(sorcerer_power(who))) * factor
        mod = BOARD_TWISTS.get(offer["twist"], (0,))[0]
        if offer["twist"] == "daylight" and period != "Morning":
            mod = 0
        difficulty = BOARD_DIFFICULTY[offer["true_grade"]] + mod
        if power >= difficulty:
            outcome = "clean"
        elif power >= 0.7 * difficulty:
            outcome = "costly"
        else:
            outcome = "withdrew"
        merit = int(round(offer["merit"] * BOARD_OUTCOME_MERIT[outcome]))
        lo, hi = offer["yen"]
        yen = int(round(rng.uniform(lo, hi) / 100.0)) * 100
        s_roll, t_roll, k_roll = rng.random(), rng.random(), rng.random()
        drops = []
        if outcome == "withdrew":
            yen = 0
        else:
            if s_roll < BOARD_SEALING[1]:
                drops.append(BOARD_SEALING[0])
            if t_roll < BOARD_TALISMAN_CHANCE:
                c = [t for t in BOARD_TALISMAN_DROPS.get(offer["grade"], ()) if not _board_owned(t)]
                if c:
                    drops.append(rng.choice(c))
            if k_roll < BOARD_TOOL_CHANCE and _board_tool_ok(offer["grade"]):
                c = [t for t in BOARD_TOOL_DROPS.get(offer["grade"], ()) if not _board_owned(t)]
                if c:
                    drops.append(rng.choice(c))
        misgraded = offer["true_grade"] != offer["grade"]
        true_curse = offer["curse"]
        if misgraded:
            true_curse = _board_rng("true", offer["id"]).choice(
                board_curses_for(offer["true_grade"], offer["place"], offer["case"]))
        place = BOARD_PLACE_BY_KEY.get(offer["place"], BOARD_PLACES[0])
        return dict(id=offer["id"], grade=offer["grade"], true_grade=offer["true_grade"],
                    title=offer["title"], case=offer["case"], place=offer["place"],
                    place_phrase=place["phrase"], bg=place["bg"], curse=offer["curse"],
                    true_curse=true_curse, twist=offer["twist"], partner=who,
                    outcome=outcome, merit=merit, yen=yen, drops=drops,
                    bond=BOARD_BOND[outcome], misgraded=misgraded, day=day, period=period,
                    power=round(power, 1), difficulty=difficulty, host=board_host()[0])

    def board_take(offer_id, who):
        """WP4. Take a card: resolve the run and leave a taken card in its slot
        (replaced the next day). None if the card is already gone."""
        for i, o in enumerate(store.board_offers):
            if o.get("id") == offer_id and not o.get("taken_by"):
                res = board_resolve(o, who)
                store.board_offers[i] = dict(taken_by="mc", partner=who, grade=o["grade"],
                                             title=o["title"], id=o["id"], place=o["place"],
                                             senior_only=o.get("senior_only", False), day=store.day)
                return res
        return None

    def board_pay(res):
        """WP4. Pay a run exactly once (keyed by its offer id in board_log):
        merit, yen, bond, train_together, drops and the misgrade clue. The
        cost (25 stamina, 2 periods) is board_clock's, after the debrief, so
        the host speaks during her hours. False if it was already paid."""
        if not res or any(r.get("id") == res["id"] for r in store.board_log):
            return False
        who = res["partner"]
        store.board_log.append(dict(id=res["id"], day=res["day"], grade=res["grade"],
                                    true_grade=res["true_grade"], title=res["title"], partner=who,
                                    outcome=res["outcome"], merit=res["merit"], yen=res["yen"],
                                    drops=list(res["drops"]), misgraded=res["misgraded"]))
        del store.board_log[:-BOARD_LOG_MAX]
        if res["misgraded"]:
            store.board_misgrades += 1
            flag("wakuri_clue")
            toast("Filed as %s. It wasn't." % grade_label(res["grade"]), "mission")
        if res["merit"] > 0:
            add_merit(res["merit"], res["title"])
        if res["yen"] > 0:
            add_yen(res["yen"])
            toast("¥{:,} — {}".format(res["yen"], res["title"]), "item")
        add_bond(who, res["bond"])
        train_together(who, BOARD_TRAIN_XP)
        for iid in res["drops"]:
            give_item(iid)
        return True

    def board_clock(res):
        """WP4. A paid run's cost, exactly once (the `clocked` mark on its
        board_log row): 25 stamina and 2 periods. Runs after the host's
        debrief, so an Afternoon job's debrief isn't played at Night.
        The clock stops after one period when a story beat is waiting there
        (board_beat_waiting), so a Noon- or Afternoon-only beat isn't skipped.
        False if there is no paid row or it was already charged."""
        for r in reversed(store.board_log):
            if res and r.get("id") == res["id"]:
                if r.get("clocked"):
                    return False
                r["clocked"] = True
                spend_stamina(BOARD_STAMINA)
                for _i in range(BOARD_PERIODS):
                    if advance_period(1):
                        break
                    if _i + 1 < BOARD_PERIODS and board_beat_waiting():
                        break   ## stop the clock where a story beat is waiting
                return True
        return False

    def board_beat_waiting():
        """WP11. True when the sandbox loop would play a story beat here, now
        (the same test as sb_loop's pick_event("story", loc=here), without
        its random pick). board_clock stops a job's clock there."""
        if store.explore_mode:
            return False
        return has_event("story", loc=store.here)

    ## Narration -----------------------------------------------------------------------

    def board_script(res):
        """WP4. A run as steps for board_play: ("scene", bg), ("show", who,
        expr), ("hide", who), ("say", None | "mcthink" | who, text), ("pay",),
        ("clock",). Seven to ten spoken lines, first person, built from the
        parts; the clock moves only after the host's debrief."""
        who = res["partner"]
        name = CAST.get(who, {}).get("short", who)
        lines = PARTNER_LINES.get(who) or PARTNER_LINES["yuji"]
        s = [("scene", res["bg"])]
        s.append(("say", None, "Ijichi drops %s and me at %s and brings the veil down behind us. The file is marked “%s”. The report inside says %s." % (
            name, res["place_phrase"], res["case"], res["curse"])))
        pre, expr, spoken = lines["arrive"]
        s.append(("show", who, expr))
        s.append(("say", None, pre))
        s.append(("say", who, spoken))
        if res["twist"] != "none":
            key = res["twist"]
            if key == "daylight" and res["period"] != "Morning":
                key = "daylight_late"
            s.append(("say", None, BOARD_TWIST_LINES[key]))
        if res["misgraded"]:
            s.append(("show", who, "surprised"))
            s.append(("say", None, "Whoever wrote the report never came this far in. It's %s, not %s, and the weight of it in the air is a whole grade past anything the card promised." % (
                res["true_curse"], res["curse"])))
            s.append(("say", "mcthink", "Filed as %s. It isn't." % grade_label(res["grade"])))
        okey = res["outcome"]
        if okey == "withdrew" and res["twist"] == "civilian":
            okey = "withdrew_civilian"
        out = BOARD_OUTCOME_LINES[okey]
        if res["outcome"] != "clean":
            s.append(("show", who, "serious"))
        s.append(("say", None, (out % name) if "%s" in out else out))
        pre, expr, spoken = lines["win" if res["outcome"] == "clean" else "hurt"]
        s.append(("show", who, expr))
        s.append(("say", None, pre))
        s.append(("say", who, spoken))
        s.append(("pay",))
        host = res.get("host", "utahime")
        hl = BOARD_HOST_LINES.get(host, BOARD_HOST_LINES["utahime"])
        hexpr, hline = hl["misgraded" if res["misgraded"] else res["outcome"]]
        if "%s" in hline:
            hline = hline % grade_label(res["grade"])
        s.append(("hide", who))
        s.append(("scene", "@host"))
        s.append(("show", host, hexpr))
        s.append(("say", host, hline))
        s.append(("hide", host))
        s.append(("clock",))
        return s

    def board_place_bg(place):
        """WP4. A campus place's background, lit for the period, or the
        placeholder `bg <place>` while the place isn't in LOCATIONS yet."""
        if place in LOCATIONS:
            return graded_bg(place)
        return "bg " + place

    def board_play(step, res):
        """WP4. Play one step of board_script: at most one interaction."""
        kind = step[0]
        if kind == "scene":
            renpy.scene()
            if step[1] == "@host":
                place = board_host()[1]
                if place in LOCATIONS:
                    renpy.show("bg", what=graded_bg(place))
                    store.scene_light = light_for_place(place, store.period)
                else:
                    renpy.show("bg " + place)
                    store.scene_light = light_for_bg("bg " + place)
            else:
                renpy.show(step[1])
                store.scene_light = light_for_bg(step[1])
            renpy.with_statement(fade_hard)
        elif kind == "show":
            renpy.show("%s %s" % (step[1], step[2]), at_list=[pos_c])
        elif kind == "hide":
            renpy.hide(step[1])
        elif kind == "say":
            who = step[1]
            if who is None:
                renpy.say(None, step[2])
            elif who == "mcthink":
                renpy.say(store.mcthink, step[2])
            else:
                renpy.say(CHARS.get(who), step[2])
        elif kind == "pay":
            board_pay(res)
        elif kind == "clock":
            board_clock(res)

    ## The journal (and anyone else) --------------------------------------------------

    def misgrade_count():
        """WP4. How many misgraded jobs I have found."""
        return store.board_misgrades

    def board_summary():
        """WP4. What the journal's Board tab needs:
            offers     this week's open offers (plain dicts, 3.7)
            taken      read-only taken cards, dict(taken_by, grade, title)
            log        the last 10 runs, newest first: dict(id, day, grade,
                       true_grade, title, partner, outcome, merit, yen,
                       drops, misgraded)
            misgrades  misgrade_count()
            host       board_host();  open  board_open();  week  board_week
            note       board_host_note(): the line saying the board moved (D13)
        Offers' `drop` lists only what can still drop for me now, and
        `senior_only` whether the job needs a senior partner at my grade now.
        Before the board is introduced (board_introduced()) there are no
        offers and no taken cards."""
        offers = board_offers_open()
        if not board_introduced():
            offers = []
        elif not store.board_offers or store.board_week != board_week_now():
            ## The board opened today, or a new week hasn't been posted yet:
            ## show what goes up, without changing anything.
            offers = board_generate(board_week_now())
        offers = [dict(o) for o in offers]
        for o in offers:
            o["drop"] = board_drops_now(o)
            o["senior_only"] = board_needs_senior(o)
        return dict(offers=offers,
                    taken=board_taken_cards() if board_introduced() else [],
                    log=[dict(r) for r in reversed(store.board_log[-10:])],
                    misgrades=misgrade_count(), host=board_host(),
                    open=board_open(), week=store.board_week, note=board_host_note())

    ## Migration 80 (3.12) ------------------------------------------------------------

    def _migrate_80():
        """WP4, migration 80. A save with the board open (the old flag from
        st_board_open, or Utahime's scene) and no offers gets this week's.
        Idempotent: once there are offers it does nothing."""
        if has_flag("mission_board_open") and not store.board_offers:
            store.board_offers = board_generate(board_week_now())
            store.board_week = board_week_now()

    ## Validator ----------------------------------------------------------------------

    _BOARD_EXPRS = ("neutral", "happy", "serious", "angry", "surprised", "sad")

    def _validate_board():
        out = []
        for g in BOARD_GRADES:
            if len(BOARD_CURSES.get(g, ())) < 2:
                out.append("board: grade %s has no curses" % g)
            for name, table in (("BOARD_DIFFICULTY", BOARD_DIFFICULTY), ("BOARD_MERIT", BOARD_MERIT),
                                ("BOARD_YEN", BOARD_YEN)):
                if g not in table:
                    out.append("board: %s has no %s" % (name, g))
        _partners = list(BOARD_PARTNER_KEYS) + [w for w in ROSTER_ORDER
                                                if w not in BOARD_NOT_PARTNERS and w not in BOARD_PARTNER_KEYS]
        for w in _partners:
            lines = PARTNER_LINES.get(w)
            if not lines:
                out.append("board: partner %s has no PARTNER_LINES" % w)
                continue
            for k in ("arrive", "win", "hurt"):
                v = lines.get(k)
                if not v or len(v) != 3 or not v[0] or not v[2] or v[1] not in _BOARD_EXPRS:
                    out.append("board: PARTNER_LINES[%r][%r] is incomplete" % (w, k))
        for host, hl in BOARD_HOST_LINES.items():
            for k in ("clean", "costly", "withdrew", "misgraded"):
                if k not in hl or hl[k][0] not in _BOARD_EXPRS:
                    out.append("board: BOARD_HOST_LINES[%r] has no valid %r" % (host, k))
        for t in BOARD_TWIST_ORDER:
            if t not in BOARD_TWISTS:
                out.append("board: twist %r is missing" % t)
            elif t != "none" and t not in BOARD_TWIST_LINES:
                out.append("board: twist %r has no narration" % t)
        _all_curses = [c for g in BOARD_GRADES for c in BOARD_CURSES.get(g, ())]
        for table, parts, vals, name in ((BOARD_CASE_FITS, BOARD_CASES, BOARD_PLACE_BY_KEY, "BOARD_CASE_FITS"),
                                         (BOARD_CURSE_FITS, _all_curses, BOARD_PLACE_BY_KEY, "BOARD_CURSE_FITS"),
                                         (BOARD_CURSE_CASE, _all_curses, BOARD_CASES, "BOARD_CURSE_CASE")):
            for k, v in table.items():
                if k not in parts or not v or any(x not in vals for x in v):
                    out.append("board: %s[%r] names a part that doesn't exist" % (name, k))
        for p in BOARD_PLACES:
            if not renpy.has_image(p["bg"], exact=True):
                out.append("board: place %s uses a missing image %r" % (p["key"], p["bg"]))
        if ITEMS:
            for iid in BOARD_ITEM_NAMES:
                if iid not in ITEMS:
                    out.append("board: drop %r is not in ITEMS" % iid)
        if not renpy.has_label("run_board_mission"):
            out.append("board: label run_board_mission is missing")
        return out

    register_new_day(_board_new_day, order=60)
    register_migration(80, _migrate_80, "board offers for a save with the board open")
    register_validator(_validate_board)
    register_place_action("board", "Mission board", "Graded jobs. Bring someone.",
                          locs=("utahime_office", "office"), when="board_open")


################################################################################
## Labels
################################################################################

## WP4. The place action: the board, then who comes, then the job. Cancelling
## the partner screen goes back to the board; a job ends the visit.
label sb_do_board:
    if not board_open():
        return
    $ board_refresh()
    $ _bdone = False
    while not _bdone:
        call screen board_screen
        $ _bs = _return
        if _bs[0] == "take":
            call screen board_partner(board_find(_bs[1]))
            $ _bp = _return
            if _bp[0] == "partner":
                call run_board_mission(_bs[1], _bp[1])
                $ _bdone = True
        else:
            $ _bdone = True
    ## Drop the screens' answers so later saves don't carry them.
    $ _bs = _bp = None
    return

## PLACEHOLDER — rewrite in phase 3
## WP4. One job with one partner: narrated, resolved and paid once (3.7).
## Phase 1 plays it out on its own; the board says fights come in a later build.
## The spec calls the second parameter `partner`; that name is an old store
## variable (read by migration 5 and legacy_story_point), so it is `who` here.
label run_board_mission(offer_id, who):
    $ _bwhy = board_refusal(board_find(offer_id), who)
    if _bwhy:
        "[_bwhy]"
        return
    $ _bres = board_take(offer_id, who)
    $ _bl = board_script(_bres)
    $ _bi = 0
    while _bi < len(_bl):
        $ board_play(_bl[_bi], _bres)
        $ _bi += 1
    $ board_pay(_bres)
    $ board_clock(_bres)
    scene expression graded_bg()
    ## The job is paid and logged; drop its script and result so later saves
    ## don't carry them.
    $ _bl = _bres = None
    return


################################################################################
## Screens (4.8)
################################################################################

style board_card_title is text:
    font gui.display_font
    color gui.paper
    size 30

style board_card_line is text:
    color gui.paper
    size 19

style board_card_dim is text:
    color gui.dim
    size 18

style board_chip_text is text:
    font gui.display_heavy_font
    color gui.ink
    size 26
    kerning 2

## A grade chip in the grade's colour. Phase 2 (4.8): the name stays, the
## chip is the game's one grade chip (sb_grades.rpy).
screen board_grade_chip(g, size=26):
    use grade_chip(g, size)


## One job card, 400 x 620.
screen board_card(o):
    $ _why = board_take_reason(o)
    $ _tw = BOARD_TWISTS.get(o["twist"], (0, "", 0))[1]
    $ _lo, _hi = o["yen"]
    $ _money = "Merit %d  ·  ¥%s–%s" % (o["merit"], "{:,}".format(_lo), "{:,}".format(_hi))
    $ _drops = "May drop: " + " · ".join(_board_item_name(i) for i in board_drops_now(o))
    $ _where = BOARD_PLACE_BY_KEY.get(o["place"], BOARD_PLACES[0])["phrase"]
    $ _where = _where[0].upper() + _where[1:]
    $ _senior = board_needs_senior(o)

    frame:
        xysize (400, 620)
        background Frame("gui/panel_dark.png", 4, 4)
        padding (26, 24)

        vbox:
            spacing 10
            use board_grade_chip(o["grade"], 26)
            null height 2
            text o["title"] style "board_card_title"
            text o["case"].upper() style "jjk_label" color gui.violet2
            text _where style "board_card_dim"
            text "Reported: " + o["curse"] style "board_card_line"
            if _tw:
                hbox:
                    spacing 8
                    text "◆" color gui.gold size 16 yalign 0.5
                    text (_tw + (" — best in the morning" if o["twist"] == "daylight" else "")) color gui.gold size 18
            null height 4
            use rule(348)
            text _money style "board_card_line"
            text _drops style "board_card_dim" size 16
            if _senior:
                frame:
                    background Frame("gui/panel_gold.png", 4, 4)
                    padding (12, 4)
                    text _("Needs a senior partner") color gui.gold size 16

        if _why:
            text _why:
                yalign 1.0
                color gui.seal
                size 18
                xmaximum 348
        else:
            textbutton _("Take"):
                style "jjk_button"
                yalign 1.0
                action Return(("take", o["id"]))


## WP4. The host, three job cards and the taken cards. Returns
## ("take", offer_id) or ("close",).
screen board_screen():
    tag sandbox

    $ _host, _place = board_host()
    $ _hname = CAST.get(_host, {}).get("short", "Utahime")
    $ _slots = list(store.board_offers)
    $ _taken = board_taken_cards()
    $ _note = board_host_note()

    add board_place_bg(_place)
    add Solid(gui.ink) alpha 0.5

    add "%s serious" % _host:
        xcenter 300
        yalign 1.0
        zoom 0.62

    hbox:
        xpos 620
        ypos 26
        spacing 16
        use seal("任", 44)
        vbox:
            yalign 0.5
            text "[_hname]'s board" font gui.display_font color gui.paper size 40
            if _note:
                text _note style "jjk_small" size 18 color gui.gold xmaximum 1220
            else:
                text _("Jobs at my grade or under it. One grade up with a senior partner. Always take someone.") style "jjk_small" size 18

    ## Cards stay in their slots: a taken card leaves a gap where it was.
    for _i, _x in enumerate((620, 1060, 1500)):
        if _i < len(_slots) and not _slots[_i].get("taken_by"):
            fixed:
                xpos _x
                ypos 140
                xysize (400, 620)
                use board_card(_slots[_i])
        else:
            frame:
                xpos _x
                ypos 140
                xysize (400, 620)
                background Frame("gui/panel_ghost.png", 4, 4)
                text _("A new card goes up tomorrow."):
                    xalign 0.5
                    yalign 0.5
                    color gui.mute
                    size 20

    if _taken:
        hbox:
            xpos 620
            ypos 790
            spacing 20
            for _t in _taken[:3]:
                frame:
                    xsize 400
                    background Frame("gui/panel_ghost.png", 4, 4)
                    padding (20, 12)
                    vbox:
                        spacing 4
                        text board_card_line(_t) color gui.mute size 18
                        text _t["title"] color gui.mute size 16

    text _("Offers change on Mondays. For now a job plays out on its own; the fights come in a later build."):
        xpos 620
        ypos 1000
        xmaximum 1040
        style "jjk_small"

    textbutton _("Close"):
        style "jjk_button"
        xsize 220
        xpos 1680
        ypos 980
        action Return(("close",))

    key "game_menu" action Return(("close",))


## WP4. Who can come along on a job. Returns ("partner", who) or ("cancel",).
screen board_partner(offer):
    tag sandbox

    $ _host, _place = board_host()
    $ _ok = bool(offer) and "id" in offer
    $ _rows = board_partner_rows(offer) if _ok else []
    $ _good = [r for r in _rows if r[1]]
    $ _bad = [r for r in _rows if not r[1]]
    $ _sub = ""
    if _ok:
        $ _sub = "%s · %s" % (offer["title"], grade_label(offer["grade"]))
        if board_needs_senior(offer):
            $ _sub += " · Needs a senior partner"

    add board_place_bg(_place)
    add Solid(gui.ink) alpha 0.72

    hbox:
        xpos 120
        ypos 48
        spacing 16
        use seal("伴", 44)
        vbox:
            yalign 0.5
            text _("Who comes with me?") font gui.display_font color gui.paper size 40
            if _ok:
                text _sub style "jjk_small"
            else:
                text _("No job chosen.") style "jjk_small"

    if _ok and not _good:
        text _("Nobody can come along right now."):
            xpos 120
            ypos 200
            color gui.dim
            size 24

    for _i, _r in enumerate(_good[:6]):
        $ _w, _k, _why, _sen = _r
        $ _c = CAST.get(_w, {})
        $ _g = grade_key(_board_npc_grade(_w))
        $ _b = bonds.get(_w, 0)
        $ _side = "images/side/%s_neutral.png" % _w
        button:
            xpos 120 + (_i % 3) * 570
            ypos 170 + (_i // 3) * 280
            xysize (540, 250)
            background Frame("gui/panel_dark.png", 4, 4)
            hover_background Frame("gui/rail_violet.png", 10, 4)
            padding (20, 18)
            action Return(("partner", _w))
            hbox:
                spacing 20
                if renpy.loadable(_side):
                    add _side zoom 0.6
                vbox:
                    spacing 8
                    text _c.get("short", _w) font gui.display_font color _c.get("color", gui.paper) size 32
                    if _g:
                        use board_grade_chip(_g, 18)
                    text "Bond %d · %s" % (_b, bond_rank(_b)[1]) color gui.dim size 18
                    if _sen:
                        frame:
                            background Frame("gui/panel_gold.png", 4, 4)
                            padding (10, 2)
                            text _("senior") color gui.gold size 16

    if _bad:
        vbox:
            xpos 120
            ypos 760
            spacing 6
            text _("CAN'T COME") style "jjk_label"
            for _w, _k, _why, _sen in _bad:
                text "%s — %s" % (CAST.get(_w, {}).get("short", _w), _why) color gui.mute size 18

    textbutton _("Cancel"):
        style "jjk_button"
        xsize 220
        xpos 1680
        ypos 980
        action Return(("cancel",))

    key "game_menu" action Return(("cancel",))


default board_offers = []       # this week's offers, and the cards I took until replaced (3.7)
default board_week = -1         # the week board_offers was posted for
default board_npc = None        # WP11: this week's senior card, dict(week, taken_by, grade, title)
default board_log = []          # the last 30 runs
default board_misgrades = 0     # misgraded jobs found (board_log keeps only 30 runs)
