################################################################################
## Cursed Bonds — combat.
##
## The loop is: the curse telegraphs, I read it, I answer it. Answering
## correctly staggers it and is worth far more than raw damage, which is why
## Insight is a combat stat and not a flavour one.
##
## WP2 owns this file (PHASE1_DESIGN.md 3.5, 4.12). One technique, Last Light,
## so MOVES holds only "timestop". Enemy grades are GRADES keys. A fight with
## `rounds` ends after that many exchanges (the prologue's alley). An old
## save's fight state (`cb`) may still hold keys this file no longer writes
## (burn, ally_buff) or lack new ones (rounds): everything reads it with .get().
################################################################################

init -1 python:

    ## --- what a curse does ---------------------------------------------------
    ## kind -> the answer that beats it
    ANSWERS = {"heavy": "guard", "fast": "step", "grab": "strike", "ranged": "close"}

    ANSWER_LABEL = {"guard": "Brace", "step": "Step aside", "strike": "Break the grip",
                    "close": "Close the distance"}

    ENEMIES = {
        ## The prologue curse. Absurd numbers on purpose: the scene is written to
        ## be survived, not won. After four exchanges it stops playing, and
        ## combat returns "down" into the story.
        "alley_curse": dict(
            name="Something in the alley", grade="g1", hp=900, power=26, sprite="curse big", rounds=4,
            tells=[("It is suddenly much closer and I did not see it move.", "fast"),
                   ("It settles its weight and the walls creak.", "heavy"),
                   ("It takes hold of my forearm.", "grab"),
                   ("Something detaches and comes at me on its own.", "ranged")]),

        "nade_curse": dict(
            name="Nade's Shikigami", grade="g3", hp=92, power=18, sprite="curse small",
            tells=[("It plants itself and lowers its head.", "heavy"),
                   ("It circles fast, keeping the pillars between us.", "fast"),
                   ("It flings a fistful of paper talismans.", "ranged")]),
        "warehouse": dict(
            name="Registered Grade 4 (it is not)", grade="g2", hp=126, power=22,
            sprite="curse big",
            tells=[("It braces on four points and swells.", "heavy"),
                   ("It is behind me. It was not behind me.", "fast"),
                   ("It takes hold of my forearm and does not let go.", "grab"),
                   ("Something detaches and comes at me on its own.", "ranged")]),

        ## The Grade 3 promotion fight in the training hall, with Maki
        ## watching (D18). No ranged tell: it is a test of reading, up close.
        "promo_g3": dict(
            name="Grade 3 assessment curse", grade="g3", hp=100, power=16, sprite="curse small",
            tells=[("It sinks its weight into the floorboards and they complain.", "heavy"),
                   ("It is on my left. Then it is not.", "fast"),
                   ("It gets a hand around my wrist and pulls.", "grab")]),
    }

    ## --- what I can do back --------------------------------------------------
    ## Deliberately expensive. Stopping time answers any telegraph, so if it
    ## were affordable every round the fight would stop being a decision.
    MOVES = {
        "timestop": [
            dict(id="stutter", name="Stutter", tier=0, ce=14,
                 desc="Hold half a second. Whatever it was going to do, I am elsewhere.",
                 scale="control", mult=0.9, freedodge=True, reveal=True),
            dict(id="held", name="Held Second", tier=1, ce=26,
                 desc="A full second, spent hitting something that cannot move yet.",
                 scale="control", mult=1.9, stagger=True),
            dict(id="arrest", name="Arrest", tier=2, ce=40,
                 desc="Long enough to cross the room. It does not get a turn.",
                 scale="control", mult=2.8, stagger=True, freedodge=True),
        ],
    }

    def refresh_vitals():
        """WP2. hp_max from output and control; hp no higher than that."""
        store.hp_max = 50 + store.output + (store.control // 3)
        store.hp = min(store.hp, store.hp_max)

    def moves_available():
        """WP2. Last Light's moves up to the current tier."""
        t = tech_tier()[0]
        return [m for m in MOVES["timestop"] if m["tier"] <= t]

    def can_read():
        """WP2. Insight high enough to understand a telegraph without spending a turn."""
        return store.insight >= 45

    ## --- the fight ------------------------------------------------------------

    def combat_begin(key_or_dict, ally=None, flee_ok=True, bg=None):
        """WP2. Set up a fight against an ENEMIES key, or an enemy dict with
        the same fields (board fights, phase 3). HP is refreshed and floored
        at half, so no fight starts near zero."""
        if isinstance(key_or_dict, str):
            e = ENEMIES[key_or_dict]
            key = key_or_dict
        else:
            e = key_or_dict
            key = e.get("key", "custom")
        ## 2.1.6: the fight state is saved, so it keeps only plain values. A
        ## displayable background is dropped (it is lit at draw time from
        ## bg_loc/bg_per); a displayable sprite falls back to the stock curse.
        if bg is not None and not isinstance(bg, str):
            bg = None
        sprite = e["sprite"] if isinstance(e.get("sprite"), str) else "curse small"
        refresh_vitals()
        store.hp = max(store.hp, store.hp_max // 2)
        store.cb = dict(
            key=key, name=e["name"], grade=(grade_key(e.get("grade")) or e.get("grade")),
            ehp=e["hp"], ehp_max=e["hp"], power=e["power"], sprite=sprite,
            tells=list(e["tells"]), tell=None, kind=None,
            ally=ally, flee_ok=flee_ok, bg=bg,
            bg_loc=store.here, bg_per=store.period,
            read=can_read(), stagger=0, freedodge=False,
            answered=False, punish=False, rounds=e.get("rounds"),
            log=[], round=1, over=None,
        )
        combat_telegraph()

    def combat_telegraph():
        """WP2. The curse picks its next tell."""
        c = store.cb
        t = renpy.random.choice(c["tells"])
        c["tell"], c["kind"] = t[0], t[1]

    def clog(msg):
        """WP2. Add a line to the fight log (the newest four are kept)."""
        store.cb["log"] = ([msg] + store.cb.get("log", []))[:4]

    def _dmg(base, scale):
        stat = getattr(store, scale)
        return max(1, int(base * (0.6 + stat / 60.0)))

    def combat_player(action, move=None):
        """WP2. Resolve the player's action. Returns True if the fight has ended.

        Answering the telegraph defends and staggers but deals little. Using a
        technique deals real damage but leaves the telegraph unanswered, so it
        lands. That trade is the whole fight."""
        c = store.cb
        answer = ANSWERS.get(c.get("kind"))
        c["answered"] = False
        c["punish"] = False

        if action in ("guard", "step", "strike", "close"):
            if action == answer:
                c["answered"] = True
                c["stagger"] = 1
                d = _dmg(9, "output")
                c["ehp"] -= d
                clog("Read it. %s — it reels, %d." % (ANSWER_LABEL[action], d))
            else:
                c["punish"] = True
                clog("%s — wrong answer. It was not going to do that." % ANSWER_LABEL[action])

        elif action == "read":
            c["read"] = True
            gain("insight", 1, quiet=True)
            clog("I stop and listen. I can read it now — but it doesn't wait.")

        elif action == "move":
            if not spend_ce(move["ce"]):
                clog("Not enough reserve for %s." % move["name"])
                return False
            d = _dmg(int(11 * move.get("mult", 1.0)), move.get("scale", "control"))
            if c.get("stagger"):
                d = int(d * 1.5)
            c["ehp"] -= d
            clog("%s — %d." % (move["name"], d))
            if move.get("reveal"):
                c["read"] = True
            if move.get("freedodge"):
                c["freedodge"] = True
            if move.get("stagger"):
                c["stagger"] = 1

        elif action == "flee":
            c["over"] = "fled"
            return True

        if c["ehp"] <= 0:
            c["over"] = "win"
            return True
        return False

    def _combat_rounds(c):
        ## The round limit; an old save's fight state predates the field.
        if "rounds" in c:
            return c["rounds"]
        k = c.get("key")
        if isinstance(k, str) and k in ENEMIES:
            return ENEMIES[k].get("rounds")
        return None

    def combat_enemy():
        """WP2. The curse acts, then telegraphs its next move. With a round
        limit, the last exchange ends the fight as "down"."""
        c = store.cb

        if c.get("ally"):
            a = _dmg(7, "output")
            c["ehp"] -= a
            clog("%s goes in. %d." % (CAST[c["ally"]]["short"], a))
            if c["ehp"] <= 0:
                c["over"] = "win"
                return

        if c.get("stagger"):
            c["stagger"] -= 1
            clog("It is still recovering.")
        elif c.get("answered"):
            pass                                    # I was where it wasn't
        elif c.get("freedodge"):
            c["freedodge"] = False
            clog("I am already somewhere else when it arrives.")
        else:
            mult = 1.5 if c.get("punish") else 1.0
            d = max(1, int(c["power"] * mult * (1.0 - min(0.35, store.control / 260.0))))
            store.hp -= d
            clog("It connects. %d." % d)
            if store.hp <= 0:
                store.hp = 0
                c["over"] = "down"
                return

        rounds = _combat_rounds(c)
        if rounds and c.get("round", 1) >= rounds:
            clog("It stops playing with me.")
            c["over"] = "down"
            return

        c["round"] = c.get("round", 1) + 1
        combat_telegraph()


default hp = 60
default hp_max = 60
default cb = {}
default quick_menu_before_combat = True     # set on entry to every fight


################################################################################
## The fight loop
################################################################################

label combat(enemy, ally=None, flee_ok=True, bg=None):

    ## Hide the quick menu for the fight, then put back whatever the caller had:
    ## the sandbox runs with it off, story scenes with it on.
    $ quick_menu_before_combat = quick_menu
    $ quick_menu = False
    $ combat_begin(enemy, ally, flee_ok, bg)

    while True:

        call screen combat_screen
        $ _a = _return

        if _a[0] == "move":
            $ _done = combat_player("move", _a[1])
        else:
            $ _done = combat_player(_a[0])

        if not _done:
            $ combat_enemy()

        if cb["over"]:
            $ _outcome = cb["over"]
            $ quick_menu = quick_menu_before_combat
            return _outcome


################################################################################
## Screen
################################################################################

screen combat_screen():

    modal True
    tag sandbox

    $ _c = cb
    $ _ename = _c["name"]
    $ _grade = grade_label(_c["grade"]) if _c.get("grade") is not None else "Ungraded"
    $ _tell = _c["tell"]
    $ _meaning = ANSWER_LABEL[ANSWERS[_c["kind"]]] if _c["read"] else "?"
    $ _moves = moves_available()
    $ _log = _c["log"]
    $ _round = _c["round"]

    ## Test harness hook (8.1): answer every tell correctly.
    if smoke_autoplay:
        timer 0.05 action Return((ANSWERS[_c["kind"]],))

    ## The background is kept as a name (2.1.6); old saves may hold a displayable.
    add (_c.get("bg") or graded_bg(_c.get("bg_loc"), _c.get("bg_per")))
    add Solid(gui.ink) alpha 0.55

    add _c["sprite"]:
        xalign 0.5
        yalign 0.92
        zoom 0.8

    ## enemy
    vbox:
        xalign 0.5
        ypos 110
        spacing 6

        text "[_ename]":
            xalign 0.5
            color gui.seal
            size 34
        text "[_grade!u] · ROUND [_round]":
            xalign 0.5
            color gui.dim
            size 18
        use meter(_c["ehp"], _c["ehp_max"], width=620, height=14, fill=gui.seal)

    ## the telegraph — the whole game is here
    frame:
        xalign 0.5
        ypos 250
        background Frame(Solid(gui.panel), 6, 6)
        padding (30, 14)
        vbox:
            spacing 4
            text "[_tell]":
                xalign 0.5
                color gui.paper
                size 25
                text_align 0.5
                xsize 820
            text "Reading: [_meaning]":
                xalign 0.5
                color (gui.gold if _c["read"] else gui.mute)
                size 19

    ## recent events
    vbox:
        xpos 40
        ypos 430
        spacing 3
        for _l in _log:
            text "[_l]":
                color gui.dim
                size 19

    ## player state + actions
    frame:
        background Frame(Solid("#0b0913f0"), 6, 6)
        yalign 1.0
        xfill True
        ypadding 16
        xpadding 30

        vbox:
            spacing 12

            ## Row one: my state, then reading and withdrawing (kept off the
            ## move row so three Last Light moves still fit at 1920).
            fixed:
                xfill True
                ysize 50
                hbox:
                    spacing 40
                    yalign 0.5
                    vbox:
                        spacing 3
                        text "HP  [hp]/[hp_max]" style "jjk_label"
                        use meter(hp, hp_max, width=260, height=10, fill=gui.stamina)
                    vbox:
                        spacing 3
                        text "CURSED ENERGY  [ce]/[ce_max]" style "jjk_label"
                        use meter(ce, ce_max, width=260, height=10, fill=gui.violet)
                hbox:
                    spacing 10
                    xalign 1.0
                    yalign 0.5
                    if not _c["read"]:
                        button:
                            background Frame(Solid(gui.panel), 4, 4)
                            hover_background Frame(Solid(gui.panel2), 4, 4)
                            padding (18, 10)
                            action Return(("read",))
                            text _("Read it"):
                                color gui.gold
                                size 21

                    if _c["flee_ok"]:
                        button:
                            background Frame(Solid(gui.panel), 4, 4)
                            hover_background Frame(Solid(gui.panel2), 4, 4)
                            padding (18, 10)
                            action Return(("flee",))
                            text _("Withdraw"):
                                color gui.dim
                                size 21

            hbox:
                spacing 10

                for _k in ("guard", "step", "strike", "close"):
                    $ _lbl = ANSWER_LABEL[_k]
                    button:
                        background Frame(Solid(gui.panel), 4, 4)
                        hover_background Frame(Solid(gui.panel2), 4, 4)
                        padding (18, 10)
                        action Return((_k,))
                        text "[_lbl]":
                            color gui.paper
                            size 21

                null width 20

                for _m in _moves:
                    $ _mn = _m["name"]
                    $ _mc = _m["ce"]
                    $ _md = _m["desc"]
                    $ _afford = (ce >= _mc)
                    button:
                        background Frame(Solid(gui.violet_deep if _afford else gui.panel), 4, 4)
                        hover_background Frame(Solid(gui.violet), 4, 4)
                        padding (18, 10)
                        action Return(("move", _m))
                        sensitive _afford
                        vbox:
                            spacing 1
                            text "[_mn]  [_mc]":
                                color (gui.paper if _afford else gui.mute)
                                size 21
                            text "[_md]":
                                color gui.mute
                                size 16
                                xmaximum 330
