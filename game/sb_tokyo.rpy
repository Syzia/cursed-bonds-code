################################################################################
## Cursed Bonds — the Tokyo layer: districts and trips in Ijichi's car.
##
## WP1 (PHASE1_DESIGN.md 3.3). After Ijichi's ride-along (flag ijichi_rides)
## he drives me into the city from the gate, mornings to afternoons. A trip is
## half a day: a short arrival in the district, then back at the gate. The
## districts' own scenes (label district_<key>) come in phase 3; sb_trip calls
## one when it exists.
##
## To add a district: an entry in DISTRICTS, its key in DISTRICT_ORDER, a
## background (bg_placeholders.rpy + a BG_LIGHT row in lighting.rpy), and a
## card position in DISTRICT_POS (ui_map.rpy).
################################################################################

init -1 python:

    ## key -> dict(name, kanji, desc, places, bg, min_grade, needs_flag,
    ## locked_hint, lines). desc is the card's one line; places is "what's
    ## there"; min_grade / needs_flag gate it beyond ijichi_rides, and
    ## locked_hint names that gate in the player's words; lines are the
    ## first-person arrival (2-3 lines).
    DISTRICT_ORDER = ["shibuya", "harajuku", "shinjuku", "kawasaki", "yotsuka"]

    DISTRICTS = {
        "shibuya": dict(
            name="Shibuya", kanji="渋谷",
            desc="The busiest crossing in the world. A thousand people, and nobody touches anybody.",
            places="The scramble crossing, the station, an arcade, a café",
            bg="bg shibuya", min_grade=None, needs_flag=None,
            locked_hint="After Ijichi's ride-along",
            lines=[
                "Ijichi lets me out two streets from the scramble, because he says nobody should have to park in Shibuya.",
                "The lights go green and a thousand people walk straight at each other without touching. I stand at the kerb and watch it happen twice before I try.",
                "Under all of it there's a hum I couldn't hear before the alley. I decide it's the trains.",
            ]),
        "harajuku": dict(
            name="Harajuku", kanji="原宿",
            desc="Loud, sweet, and very pink. Nobara's idea of a day out.",
            places="Takeshita Street, crêpe stands, a talisman shop down a side street",
            bg="bg harajuku", min_grade=None, needs_flag=None,
            locked_hint="After Ijichi's ride-along",
            lines=[
                "Takeshita Street is a tunnel of crêpes, lace and people filming each other.",
                "Nobara would know which shop is the good one. I don't, so I walk the whole length of it and back again.",
                "A stall by the station sells lucky charms. None of them are real. I can tell now, which is a strange thing to be able to tell.",
            ]),
        "shinjuku": dict(
            name="Shinjuku", kanji="新宿",
            desc="Neon, towers, and the jobs that need a Grade 2.",
            places="Neon streets, the station, the rooftops",
            bg="bg shinjuku", min_grade="g2", needs_flag=None,
            locked_hint="Grade 2",
            lines=[
                "Even at noon Shinjuku keeps its signs lit, like it's trying to keep something out.",
                "The station swallows people on one side and lets them out on the other, a little more tired.",
                "Up on the roofs the signs are taller than the buildings under them. Anything could be sitting behind one.",
            ]),
        "kawasaki": dict(
            name="Kawasaki", kanji="川崎",
            desc="Across the river. Quieter than Tokyo, and not as quiet as it looks.",
            places="The river, a cinema, streets I don't know yet",
            bg="bg kawasaki", min_grade=None, needs_flag="kawasaki_open",
            locked_hint="Act III",
            lines=[
                "Kawasaki is quieter than I expected: low roofs, the river, a cinema with its posters bleached pale by the sun.",
                "Nothing here is looking for me. I remind myself that this is what it's like for most people, all the time.",
            ]),
        "yotsuka": dict(
            name="Home — Yotsuka", kanji="四塚",
            desc="Where I grew up. It hasn't moved.",
            places="My parents' house, the diner, the alley",
            bg="bg yotsuka", min_grade=None, needs_flag=None,
            locked_hint="After Ijichi's ride-along",
            lines=[
                "Yotsuka hasn't changed. It feels like something it should have asked me about first.",
                "I walk past the diner without looking in. Then I walk back and look in. Two kids in school uniform have our stools at the counter, and one of them is pushing a half-finished bowl at the other.",
                "There's a new light over the fire door in the alley behind the arcade. I don't go down it.",
            ]),
    }

    def tokyo_open():
        """WP1. The Tokyo tab is open: after Ijichi's ride-along (flag ijichi_rides)."""
        return has_flag("ijichi_rides")

    def district_state(key):
        """WP1. (open, reason) for a district; the reason is in the player's
        words ("After Ijichi's ride-along", "Grade 2", "Act III") and "" when
        open."""
        d = DISTRICTS.get(key)
        if d is None:
            return (False, "Later")
        if not tokyo_open():
            return (False, "After Ijichi's ride-along")
        if d["needs_flag"] and not has_flag(d["needs_flag"]):
            return (False, d["locked_hint"])
        if d["min_grade"] and grade_rank(player_grade()) < grade_rank(d["min_grade"]):
            return (False, d["locked_hint"])
        return (True, "")

    ## Ijichi drives in these periods (his schedule has him at the gate then).
    TRIP_PERIODS = ("Morning", "Noon", "Afternoon")

    def trip_ok_now():
        """WP1. A trip can start now: Ijichi is at the gate this period, and
        it is Morning, Noon or Afternoon."""
        return store.period in TRIP_PERIODS and char_location("ijichi") == "gate"

    def car_action_ok():
        """WP1. "Ask Ijichi for a ride" is offered: a trip can start now,
        Tokyo is open, and I'm at the gate."""
        return trip_ok_now() and tokyo_open() and store.here == "gate"

    register_place_action("car", "Ask Ijichi for a ride", "Into the city. Half a day.",
                          cost=2, locs=("gate",), when="car_action_ok")


## Half a day in a district, then back at the gate (3.3). A trip that starts
## in the Morning ends in the Afternoon. It returns at once when the district
## is closed or Ijichi isn't driving now. Under the test harness's autoplay
## (smoke_autoplay) the "Go." / "Not today." menu is taken as "Go.". The map's
## Tokyo tab can start a trip from anywhere on campus; I walk down to the gate
## first (walking is free). Only plain values stay in the store: the district
## is read from DISTRICTS[key] each time.
label sb_trip(key):
    ## PLACEHOLDER — rewrite in phase 3
    ## (the arrival lines stand in for the district scenes, label district_<key>)
    if key not in DISTRICTS or not district_state(key)[0] or not trip_ok_now():
        return
    $ _trip_name = DISTRICTS[key]["name"].split(" — ")[-1]      # "Yotsuka", not "Home — Yotsuka"

    if not smoke_autoplay:
        menu:
            "Half a day in [_trip_name]."
            "Go.":
                pass
            "Not today.":
                return

    if here != "gate":
        "I walk down to the gate. Ijichi is already holding the car door."
    ## Nobody else comes along: the car has one spare seat, and it's taken.
    if companion:
        $ _trip_who = CAST[companion]["short"]
        "[_trip_who] waves me off at the gate. Ijichi only has the one spare seat, and it's full of paperwork."
        $ companion = None

    ## After the first trip his line rotates by day and period, so two trips
    ## on one day never repeat it.
    $ _car_line = (day * 5 + period_index()) % 3
    scene bg car
    with Dissolve(0.4)
    if not districts_visited:
        show ijichi serious at pos_c
        with dissolve
        ijichi "Seatbelt, please. And if you see anything, anything at all, you call me first. Before you do something about it. Please."
    elif _car_line == 0:
        show ijichi neutral at pos_c
        with dissolve
        ijichi "Back at the gate by the usual time, please. I've already filed the mileage."
    elif _car_line == 1:
        show ijichi sad at pos_c
        with dissolve
        ijichi "Please don't tell Gojo-san I let you out alone. He'll want to come next time."
    else:
        show ijichi serious at pos_c
        with dissolve
        ijichi "If anything feels wrong, walk away from it first and call me second. In that order, please."

    ## (renpy.show skips config.show, so the sprite light is set here.)
    $ renpy.scene()
    $ scene_light = light_for_bg(DISTRICTS[key]["bg"])
    $ renpy.show(DISTRICTS[key]["bg"])
    with Dissolve(0.6)
    $ _trip_i = 0
    while _trip_i < len(DISTRICTS[key]["lines"]):
        $ renpy.say(None, DISTRICTS[key]["lines"][_trip_i])
        $ _trip_i += 1

    $ districts_visited.add(key)
    if renpy.has_label("district_" + key):
        call expression "district_" + key

    "Ijichi is waiting where he said he'd be. The drive back up the mountain is quiet."
    $ advance_period(2)
    $ here = "gate"
    scene expression graded_bg()
    with Dissolve(0.6)
    return


## The car action (3.3): the Tokyo layer of the map. A district starts a
## trip; the Campus tab still walks me somewhere, as sb_travel does.
label sb_do_car:
    if not car_action_ok():
        return
    call screen sb_map(layer="tokyo")
    $ _car = _return
    if _car[0] == "district":
        call sb_trip(_car[1])
    elif _car[0] == "go":
        $ _ok, _why = can_enter(_car[1])
        if not _ok:
            "[_why]"
        else:
            $ here = _car[1]
            scene expression graded_bg()
            with Dissolve(0.4)
    return


default districts_visited = set()   # WP1: the districts Ijichi has driven me to
