################################################################################
## Cursed Bonds — the night.
##
## Phase 2 (PHASE2_DESIGN.md 4.15, D20 to D24, 6.1). P4b.
##
## Night is the last hour. I can still walk, talk, eat and look at things, but
## anything that takes time is closed, and Wait becomes "Go to bed". The
## exceptions each have a price:
##   - a night of training with Gojo on the ridge (rare; tomorrow is a rest
##     day: no missions, no board jobs, no training);
##   - a night in Tokyo (the club, or the Black Market once it is found;
##     tomorrow starts with half my stamina and less cursed energy);
##   - the story's own night scenes (NIGHT_OK).
## Whenever the day turns while I'm away from my room, the loop walks me home
## first (night_carry_home).
##
## None of it applies in explore mode, before the game has settled in, or in
## a replay. Every number is one entry in the tables below.
##
## Saves (2.3): the three `menu:` statements below, with their captions, and
## both `call market_open` statements, each with the line after it, stay
## textually identical.
################################################################################

init -1 python:

    ## Tables (3.2) ---------------------------------------------------------------

    ## True: at Night nothing that takes time can be started, except NIGHT_OK.
    ## False (the loose reading): those rows stay, marked "ends the night".
    NIGHT_STRICT = True

    ## Action and activity ids the strict Night still allows.
    NIGHT_OK = {"night_gojo", "stargaze", "rom_close", "int_night"}

    ## Action and activity ids closed on a rest day (the day after a Gojo
    ## night). `train` is Train, Practice and "Train together".
    NIGHT_REST_BLOCKS = {"train", "lesson", "hold", "swim"}

    ## The Gojo night (D23). day_step and day_hold mirror sb_do_train on the
    ## ridge and sb_do_hold; day_lesson and day_lesson_reserve mirror
    ## act_lesson (tools/smoke/p2_night.rpy proves they still match). `over`
    ## and `reserve_over` are what the night gives beyond the best day.
    ## past_cap is how far the night may leave Control above my grade's
    ## ceiling (the owner's ruling, 3 Oct 2026); with it above 0 the reserve
    ## may end reserve_over above its own ceiling. gap is the days between
    ## two nights.
    NIGHT_GOJO = dict(over=6, reserve_over=3, day_step=4, day_hold=2, day_lesson=5,
                      day_lesson_reserve=5, past_cap=6, gap=10, place="ridge")

    ## The night in Tokyo (D24): the club's door charge, a companion's Bond,
    ## the share of stamina and cursed energy I wake with, and the district
    ## the Black Market is in.
    NIGHT_OUT = dict(cover=1500, bond=4, stamina=0.5, ce=0.7, market="shibuya")

    ## The districts a night out can be spent in, and the periods it can
    ## start in.
    NIGHT_DISTRICTS = ("shibuya", "shinjuku")
    NIGHT_OUT_PERIODS = ("Evening", "Night")

    ## What I say when the loop walks me home, by where the day turned: a
    ## place's own line first, then its area's ("" is anywhere else: a story
    ## scene off the campus).
    NIGHT_CARRY_LINES = {
        "heart":    "The gate lamps are still lit when I cross the courtyard. I'm in my room before the first bell.",
        "school":   "The school building is dark, and my footsteps are the loudest thing in it. I walk back to my room.",
        "dorms":    "The dormitory is a row of closed doors and one that isn't. Mine. I'm through it before anyone is up.",
        "girls_dorm": "I let myself out before the corridor wakes.",
        "staff":    "The staff building's lamps are still on from last night, and nobody is left to turn them off. I walk back to my room as it gets light.",
        "grounds":  "The dew is already down on the training grounds. I get to my room as it turns light.",
        "mountain": "The path down the mountain is easier to find than it has any right to be. I'm in my room before the sun is.",
        "":         "It's morning before I notice. I walk back to my room.",
    }

    ## The words of the two next-day costs: the status chip (night_tag), the
    ## morning toast, and why the board and the training say no.
    NIGHT_TAGS = {
        "gojo": "Worn out — no missions or training today",
        "out":  "Rough morning",
    }
    NIGHT_REST_REASON = "Not today. I can barely stand."

    ## The rule --------------------------------------------------------------------

    def night_exists():
        """P4b (sb_night.rpy). bool: the night rule is built."""
        return True

    def night_on():
        """P4b. bool: the night rule applies: the game has settled in, and
        this is neither explore mode nor a replay."""
        if store.explore_mode or getattr(store, "_in_replay", None):
            return False
        return has_flag("settled_in")

    def night_is_night():
        """P4b. bool: it is the last period of the day."""
        return store.period == PERIODS[-1]

    def night_pending():
        """P4b. bool: the day turned while I was away from my room, and the
        loop should walk me home (night_carry_home). The loop asks on every
        pass, so a mark left behind by a scene that already took me to my
        room is dropped here."""
        if not store.night_carried:
            return False
        if store.here == "dorm":
            store.night_carried = ""
            return False
        return night_on()

    def night_carry_line():
        """P4b. str: what I say on the walk home, for where the day turned."""
        place = store.night_carried or store.here
        return (NIGHT_CARRY_LINES.get(place) or NIGHT_CARRY_LINES.get(area_of(place) or "")
                or NIGHT_CARRY_LINES[""])

    def night_can_work():
        """P4b. bool: missions, board jobs and training can be started today
        (False the day after a Gojo night)."""
        return not (store.night_cost_kind == "gojo" and store.night_cost_day == store.day)

    def night_block_reason():
        """P4b. str: why I can't work today, "" when clear."""
        return "" if night_can_work() else NIGHT_REST_REASON

    def night_tag():
        """P4b. str: the status chip's words ("Worn out ...", "Rough
        morning"), "" when clear."""
        if store.night_cost_kind and store.night_cost_day == store.day:
            return NIGHT_TAGS.get(store.night_cost_kind, "")
        return ""

    def night_blocks(id):
        """P4b. bool: this action or activity is closed today because of a
        rest day (NIGHT_REST_BLOCKS)."""
        return (id in NIGHT_REST_BLOCKS) and not night_can_work()

    def night_allows(id, cost):
        """P4b. bool: the night lets this start now. id is an action or
        activity id, or "mission:" + mid; cost is its periods. Always True
        before Night, in explore mode and before the game has settled in. At
        a strict Night: True when it costs nothing or its id is in NIGHT_OK;
        a mission, when its periods include Night or it costs nothing."""
        if not night_on() or not night_is_night() or not NIGHT_STRICT:
            return True
        if not cost:
            return True
        if isinstance(id, str) and id.startswith("mission:"):
            m = (getattr(store, "MISSION_BY_ID", None) or {}).get(id[len("mission:"):]) or {}
            return PERIODS[-1] in (m.get("periods") or ())
        return id in NIGHT_OK

    def night_filter_actions(loc, acts):
        """P4b. A list of (id, label, hint, cost): the place's actions as the
        night rule leaves them. Explore mode and an unsettled game: acts,
        unchanged. Otherwise, first, at any period, the rows a rest day
        closes are dropped (night_blocks). Then, only at Night: Wait goes;
        "Go to bed" is added everywhere but my room (which has Sleep); and
        with NIGHT_STRICT every row that costs time and isn't in NIGHT_OK
        goes (without it those rows stay, marked "ends the night")."""
        if not night_on():
            return acts
        out = [a for a in acts if not night_blocks(a[0])]
        if not night_is_night():
            return out if len(out) != len(acts) else acts
        out = [a for a in out if a[0] != "wait"]
        if NIGHT_STRICT:
            out = [a for a in out if not a[3] or a[0] in NIGHT_OK]
        else:
            out = [((a[0], a[1], a[2] + " · ends the night", a[3]) if (a[3] and a[0] not in NIGHT_OK) else a)
                   for a in out]
        if loc != "dorm":
            out.append(("night_bed", "Go to bed", "Walk back to my room and sleep. The day ends.", 0))
        return out

    ## Next-day costs ----------------------------------------------------------------

    def night_set_cost(kind):
        """P4b. Returns None. Sets tomorrow's cost: "gojo" (a rest day) or
        "out" (a rough morning). Called before the day rolls."""
        if kind not in NIGHT_TAGS:
            return None
        store.night_cost_kind = kind
        store.night_cost_day = store.day + 1
        return None

    def night_new_day_early():
        """P4b, new-day hook (order 5). Notes where the day turned when I
        wasn't in my room, for the walk home."""
        if not night_on():
            return
        store.night_carried = store.here if store.here != "dorm" else ""

    def night_new_day_late():
        """P4b, new-day hook (order 80, after the refill). Applies a night
        out's stamina and cursed energy, says what today costs, and clears a
        cost whose day has passed."""
        if not store.night_cost_kind:
            return
        if store.night_cost_day < store.day:
            store.night_cost_kind = ""
            store.night_cost_day = 0
            return
        if store.night_cost_day != store.day:
            return
        if store.night_cost_kind == "out":
            store.stamina = int(store.stamina_max * NIGHT_OUT["stamina"])
            store.ce = int(store.ce_max * NIGHT_OUT["ce"])
        toast(NIGHT_TAGS[store.night_cost_kind], "info")

    ## The Gojo night (D23) ---------------------------------------------------------

    def night_step(cur, amount):
        """P4b. int: what gain() would add to a stat standing at `cur`,
        ceiling aside, without changing anything. Both cuts apply in turn,
        exactly as in gain (sb_energy.rpy): from 60, then from 85."""
        if amount > 0:
            if cur >= 60:
                amount = max(1, int(amount * 0.6))
            if cur >= 85:
                amount = max(1, int(amount * 0.5))
        return amount

    def night_day_walk(cur, steps):
        """P4b. int: what a run of gains adds, in order, from `cur`."""
        total = 0
        for s in steps:
            a = night_step(cur, s)
            cur += a
            total += a
        return total

    def night_day_best():
        """P4b. int: the Control the best day of training would add from my
        Control now, my grade's ceiling aside. A day is one step for each
        period and one free Hold the hour. Two days are walked: Gojo's
        lesson with a train on the ridge in every other period, and a train
        in every period; each with the hold and the lesson in every position
        (order matters near 60 and 85). The best of them all."""
        g = NIGHT_GOJO
        n = len(PERIODS)
        days = [[g["day_step"]] * n]
        for i in range(n):
            d = [g["day_step"]] * n
            d[i] = g["day_lesson"]
            days.append(d)
        best = 0
        for d in days:
            for h in range(n + 1):
                best = max(best, night_day_walk(store.control, d[:h] + [g["day_hold"]] + d[h:]))
        return best

    def night_gojo_gain():
        """P4b. (int, int): the Control and the reserve a Gojo night gives:
        the best day's Control and `over` more; the better day's reserve (a
        train gives 1, the lesson day_lesson_reserve, the hold none) and
        reserve_over more. What a grade's ceiling leaves of it is
        night_gojo_apply's business."""
        g = NIGHT_GOJO
        n = len(PERIODS)
        return (night_day_best() + g["over"],
                max(n, g["day_lesson_reserve"] + n - 1) + g["reserve_over"])

    def night_gojo_beats():
        """P4b. bool: from where I stand, the night would leave me with more
        Control than a real day of training could (D23). The night never
        takes Control past 100, so at a ceiling of 100 it is due only while
        there is more than a day's room left."""
        g = NIGHT_GOJO
        ceiling = grade_cap("stat") or 100
        best = night_day_best()
        night = min(best + g["over"], min(100, ceiling + g["past_cap"]) - store.control)
        real = min(best, max(0, ceiling - store.control))
        if not night > real:
            return False
        if g["past_cap"] <= 0:
            cap = grade_cap("reserve")
            if cap is not None and store.ce_max + night_gojo_gain()[1] > cap:
                return False
        return True

    def night_gojo_due():
        """P4b. bool: a Gojo night is due this morning: after his first
        lesson, on a day he is in, at least NIGHT_GOJO["gap"] days after the
        last one, and only if it would beat a day of training."""
        if not night_on():
            return False
        if not has_flag("intensive_done") or not gojo_in_today() or "gojo" not in store.roster:
            return False
        if store.day - store.night_gojo_last < NIGHT_GOJO["gap"]:
            return False
        return night_gojo_beats()

    def night_gojo_ok():
        """P4b. bool: "Train until morning" is offered here, now: tonight is
        the night he asked for, it is Night, and I'm on the ridge."""
        return bool(night_on() and store.night_gojo_day == store.day and night_is_night()
                    and store.here == NIGHT_GOJO["place"])

    def night_gojo_apply():
        """P4b. (control gained, reserve gained). Gives the night's gains:
        Control one point at a time through gain() (which never gives less
        than one), then the reserve, then one toast with the totals. gain()
        stops at my grade's ceiling; with NIGHT_GOJO["past_cap"] above 0 the
        points it refused go on directly, while Control is below the ceiling
        + past_cap. The reserve the same way: what raise_reserve clipped, at
        most reserve_over of it, and never past its ceiling + reserve_over."""
        g = NIGHT_GOJO
        want_c, want_r = night_gojo_gain()
        c0, r0 = store.control, store.ce_max
        ceiling = grade_cap("stat") or 100
        top = min(100, ceiling + g["past_cap"])
        tier0 = tech_tier()[0]
        for i in range(want_c):
            before = store.control
            gain("control", 1, quiet=True)
            if store.control != before:
                continue
            if g["past_cap"] > 0 and store.control < top:
                store.control = min(100, store.control + 1)
            else:
                break
        if tech_tier()[0] > tier0 and store.control > ceiling:
            ## gain() announces a tier it crosses itself; this is one crossed
            ## by the points above the ceiling.
            toast("Technique advanced — %s" % tech_tier()[1], "stat")
        left = want_r - raise_reserve(want_r)
        cap = grade_cap("reserve")
        if left > 0 and g["past_cap"] > 0 and cap is not None:
            store.ce_max += max(0, min(left, g["reserve_over"], cap + g["reserve_over"] - store.ce_max))
        got = (store.control - c0, store.ce_max - r0)
        if got[0] or got[1]:
            toast("A night on the ridge — Control %+d, reserve %+d" % got, "stat")
        return got

    def night_gojo_invite():
        """P4b. Tonight is a Gojo night: he is pinned to the ridge at Night
        and the morning toast is queued, once a day."""
        store.night_gojo_day = store.day
        pin("gojo", NIGHT_GOJO["place"], store.day, PERIODS[-1])
        if "night_toast" not in store.actions_today:
            store.actions_today.add("night_toast")
            toast("Gojo: the ridge, tonight", "info", "gojo")

    def night_gojo_morning():
        """P4b, new-day hook (order 55). On a morning a Gojo night is due:
        the invitation is for today, he is on the ridge at Night, and one
        toast says so."""
        if night_gojo_due():
            night_gojo_invite()

    def night_marks():
        """P4b. dict {area key: "moon"}: the map's night badges. The
        Mountain, on a day Gojo has asked for the night."""
        if not night_on() or store.night_gojo_day != store.day:
            return {}
        area = area_of(NIGHT_GOJO["place"])
        return {area: "moon"} if area else {}

    ## The night in Tokyo (D24) -----------------------------------------------------

    def night_out_ok(key):
        """P4b. (bool, str): a night in this district can start now, and the
        reason when it can't. (False, "") hides the map's night button: the
        wrong district, the wrong hour, explore mode."""
        if not night_on() or key not in NIGHT_DISTRICTS or key not in DISTRICTS:
            return (False, "")
        if store.period not in NIGHT_OUT_PERIODS:
            return (False, "")
        ok, why = district_state(key)
        if not ok:
            return (False, why or "Later")
        if store.day - store.night_out_last < 2:
            return (False, "Not two nights running")
        return (True, "")

    def night_market_here(key):
        """P4b. bool: the Black Market can be visited from this district:
        it is built, it is here, and I've found it."""
        return bool(market_exists() and key == NIGHT_OUT["market"] and has_flag("market_found"))

    def night_out_auto():
        """P4b. str: what the test harness's autoplay takes at the arrival
        menu: the club when I can cover it, else home."""
        return "club" if store.yen >= NIGHT_OUT["cover"] else "home"

    def night_bg(key):
        """P4b. str: the picture a night in a district plays over: its night
        picture ("bg shibuya night") once one is painted, else the district's
        own (today's stand-ins for Shibuya and Shinjuku are already lit by
        neon)."""
        name = DISTRICTS[key]["bg"]
        if renpy.has_image(name + " night", exact=True):
            return name + " night"
        return name

    ## The review tools (4.16) ------------------------------------------------------

    def night_dev(kind):
        """P4b. Returns None. The review tools' switches: "gojo" (he asks for
        tonight), "rest" (tomorrow is a rest day), "market" (the Black Market
        is found)."""
        if kind == "gojo":
            store.actions_today.discard("night_toast")
            night_gojo_invite()
        elif kind == "rest":
            night_set_cost("gojo")
            toast("Tomorrow is a rest day.", "info")
        elif kind == "market":
            flag("market_found")
            toast("The Black Market is found. Shibuya, after dark.", "info")
        return None

    ## Registration -----------------------------------------------------------------

    register_new_day(night_new_day_early, order=5)
    register_new_day(night_gojo_morning, order=55)
    register_new_day(night_new_day_late, order=80)

    register_place_action("night_gojo", "Train until morning",
                          "More than a day's worth. Tomorrow I'm no use to anyone.",
                          cost=1, locs=(NIGHT_GOJO["place"],), when="night_gojo_ok", order=5)

    def night_validate():
        """P4b, a registered validator. The night's tables against the
        game's own: every id and place they name exists."""
        out = []
        acts = set(a["id"] for a in ACTIVITIES) | set(a["id"] for a in PLACE_ACTIONS) | {
            "train", "swim", "hold", "study", "think", "eat", "rest", "sleep", "wait"}
        for name, table in (("NIGHT_OK", NIGHT_OK), ("NIGHT_REST_BLOCKS", NIGHT_REST_BLOCKS)):
            for i in sorted(table):
                if i not in acts:
                    out.append("%s: %r is not an action or activity id" % (name, i))
        if NIGHT_GOJO["place"] not in LOCATIONS:
            out.append("NIGHT_GOJO: place %r is not a place" % (NIGHT_GOJO["place"],))
        for k in NIGHT_DISTRICTS + (NIGHT_OUT["market"],):
            if k not in DISTRICTS:
                out.append("the night in Tokyo: %r is not a district" % (k,))
        if NIGHT_OUT["market"] not in NIGHT_DISTRICTS:
            out.append("NIGHT_OUT: the market's district %r has no night out" % (NIGHT_OUT["market"],))
        for a in sorted(NIGHT_CARRY_LINES):
            if a and a not in AREA_BY_KEY and a not in LOCATIONS:
                out.append("NIGHT_CARRY_LINES: %r is not an area or a place" % (a,))
        for a in AREAS:
            if a["key"] not in NIGHT_CARRY_LINES:
                out.append("NIGHT_CARRY_LINES: no line for the area %r" % (a["key"],))
        if "" not in NIGHT_CARRY_LINES:
            out.append("NIGHT_CARRY_LINES: no fallback line (key \"\")")
        return out

    register_validator(night_validate)


## The safety net (D21, D22): the day turned while I was away from my room.
## Called at the top of the loop when night_pending().
label night_carry_home:
    $ renpy.say(None, night_carry_line())
    $ here = "dorm"
    scene expression graded_bg()
    with Dissolve(0.4)
    $ night_carried = ""
    return


## "Go to bed": the walk back to my room, then Sleep.
label sb_do_night_bed:
    if here != "dorm":
        "I walk back while I can still feel my feet."
        $ here = "dorm"
    call sb_do_sleep
    return


## "Train until morning" (D23). Under the test harness's autoplay the menu is
## taken as "Stay.".
label sb_do_night_gojo:
    ## PLACEHOLDER — rewrite in phase 4
    if not night_gojo_ok():
        return

    ## the ridge as it is tonight, behind the menu
    scene expression graded_bg()

    if not smoke_autoplay:
        menu:
            "A whole night with Gojo. Tomorrow I won't be fit for missions or training."
            "Stay.":
                pass
            "Not tonight.":
                return

    scene expression graded_bg()
    show gojo happy at pos_c
    with dissolve
    gojo happy "You came. Good. Without you this is just a man sitting on a rock."
    gojo serious "One rule. You don't stop when you're tired. You stop when I say."
    "He has me hold a second, let it go, and take the next one before the first has finished leaving. Then again. The veil hums behind him the whole time."
    "Somewhere past midnight I lose count. My hands shake, and then they stop, and what's left is steadier than anything I've held before."
    gojo happy "There. Remember where that sits. You'll want it back."
    "The sky goes grey behind the ridge. I don't remember the walk down."

    $ _night_got = night_gojo_apply()
    if _night_got[0] or _night_got[1]:
        $ night_set_cost("gojo")
    $ night_gojo_last = day
    $ here = "dorm"
    $ new_day()
    scene expression graded_bg()
    with Dissolve(0.6)
    "Day [day]. Morning."
    return


## A night in a Tokyo district (D24), from the Tokyo map in the Evening or at
## Night. The club, the Black Market once it is found, or home. Heading home
## costs nothing and no time passes. After the club or the market I was out
## all night. Under the test harness's autoplay the club is taken when I can
## cover it, else home, and Home at the second menu.
label night_out(key):
    ## PLACEHOLDER — rewrite in phase 4
    if not night_out_ok(key)[0]:
        return

    ## where I am, as it is tonight, behind the first line
    scene expression graded_bg()

    $ _night_name = DISTRICTS[key]["name"].split(" — ")[-1]
    $ _night_cover = "{:,}".format(NIGHT_OUT["cover"])
    $ _night_who = companion

    "The last train into the city leaves from the foot of the mountain in twenty minutes. I could be on it."

    ## the district, behind the menu (config.show sets the sprite light from it)
    scene expression night_bg(key)
    with Dissolve(0.4)

    $ _night_pick = night_out_auto() if smoke_autoplay else ""
    while not _night_pick:
        menu:
            "[_night_name], after dark."
            "The club · ¥[_night_cover]" if yen >= NIGHT_OUT["cover"]:
                $ _night_pick = "club"
            "The club · ¥[_night_cover] · Not enough yen" if yen < NIGHT_OUT["cover"]:
                "I count what's in my wallet twice. It comes to the same both times."
            "The Black Market" if night_market_here(key):
                $ _night_pick = "market"
            "Head home":
                $ _night_pick = "home"

    if _night_pick == "home":
        ## back where I was
        scene expression graded_bg()
        with Dissolve(0.4)
        return

    ## The district again. A new night already shows it; a save made on the
    ## menu above by an older tree still holds the campus room.
    scene expression night_bg(key)

    if _night_pick == "market":
        "Past the club's door, one flight further down. Nobody at this one asks for money."
        call market_open
        $ _night_pick = "market_done"

    else:
        $ add_yen(-NIGHT_OUT["cover"])
        "[_night_name] at night is a different city wearing the same streets. The club is down a flight of stairs, behind a door with no sign on it."
        "The bass comes up through the floor and into my teeth. For a few hours nobody in the room knows what I am, and nothing in it needs exorcising."
        if _night_who and _night_who in CAST:
            $ _night_who_name = CAST[_night_who]["short"]
            if _night_who in ("yuji", "nobara"):
                "[_night_who_name] pulls me onto the floor twice and laughs at me both times. Neither of us has looked this well all week."
            else:
                "[_night_who_name] finds a wall to stand against and I stand against it too. Somewhere in the second hour we both stop watching the door."
            $ add_bond(_night_who, NIGHT_OUT["bond"])
        if key == NIGHT_OUT["market"] and market_exists() and not has_flag("market_found"):
            "On the way out I take the wrong stairs. One floor further down a man sits at a folding table under a paper lantern, with talismans laid out in front of him like playing cards."
            "He looks at me, and then at my hands, and nods. I make sure I'll know the door again."
            $ flag("market_found")
        if night_market_here(key) and not smoke_autoplay:
            menu:
                "The night isn't over yet."
                "The Black Market":
                    call market_open
                    $ _night_pick = "club_market"
                "Home":
                    pass

    ## Out all night.
    $ night_set_cost("out")
    $ night_out_last = day
    $ here = "dorm"
    $ new_day()
    scene expression graded_bg()
    with Dissolve(0.6)
    "Day [day]. Morning. The first train back is full of people going the other way, and I'm in my room before roll call."
    return


## Night state (3.3).
default night_carried = ""       # the place where the day turned while I wasn't in my room; "" when none
default night_cost_day = 0       # the day a next-day cost applies to
default night_cost_kind = ""     # "gojo" or "out"
default night_gojo_last = -99    # day of the last Gojo night
default night_gojo_day = 0       # the day tonight's invitation is for
default night_out_last = -99     # day of the last night out
