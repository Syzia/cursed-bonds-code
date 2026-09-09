################################################################################
## Cursed Bonds — combat.
##
## The loop is: the curse telegraphs, you read it, you answer it. Answering
## correctly staggers it and is worth far more than raw damage, which is why
## Insight is a combat stat and not a flavour one.
################################################################################

init -1 python:

    ## --- what a curse does ---------------------------------------------------
    ## kind -> the answer that beats it
    ANSWERS = {"heavy": "guard", "fast": "step", "grab": "strike", "ranged": "close"}

    ANSWER_LABEL = {"guard": "Brace", "step": "Step aside", "strike": "Break the grip",
                    "close": "Close the distance"}

    ENEMIES = {
        "sitter": dict(
            name="The Sitter", grade=4, hp=40, power=11, sprite="curse sitter",
            tells=[("It folds its hands and goes still.", "heavy"),
                   ("It is suddenly a metre closer.", "fast"),
                   ("It reaches, slowly, for your wrist.", "grab")]),
        "stairwell": dict(
            name="Stairwell Residual", grade=4, hp=46, power=12, sprite="curse small",
            tells=[("It swells against the walls.", "heavy"),
                   ("It drops flat and skitters.", "fast"),
                   ("It spits something wet at the ceiling.", "ranged")]),
        "sunmall": dict(
            name="Kawagoe Accumulation", grade=2, hp=150, power=24, sprite="curse big",
            tells=[("Every face on it turns the same way.", "heavy"),
                   ("It comes apart and reassembles closer.", "fast"),
                   ("A limb unspools toward you across the atrium.", "grab"),
                   ("It draws breath in four-four time.", "ranged")]),
        "nade_curse": dict(
            name="Nade's Shikigami", grade=3, hp=92, power=18, sprite="curse small",
            tells=[("It plants itself and lowers its head.", "heavy"),
                   ("It circles fast, keeping the pillars between you.", "fast"),
                   ("It flings a fistful of paper talismans.", "ranged")]),
        "warehouse": dict(
            name="Registered Grade 4 (it is not)", grade=2, hp=126, power=22,
            sprite="curse big",
            tells=[("It braces on four points and swells.", "heavy"),
                   ("It is behind you. It was not behind you.", "fast"),
                   ("It takes hold of your forearm and does not let go.", "grab"),
                   ("Something detaches and comes at you on its own.", "ranged")]),
    }

    ## --- what you can do back ------------------------------------------------
    MOVES = {
        "filament": [
            dict(id="thread", name="Filament", tier=0, ce=6,
                 desc="Threads through the joints. Precise, cheap.", scale="control", mult=1.0),
            dict(id="suture", name="Suture", tier=1, ce=12,
                 desc="Stitch yourself back together.", scale="control", mult=0.0, heal=True),
            dict(id="marionette", name="Marionette", tier=2, ce=20,
                 desc="Move it instead of hitting it.", scale="control", mult=2.0, stagger=True),
        ],
        "emberfall": [
            dict(id="ember", name="Ember", tier=0, ce=6,
                 desc="A burn that keeps burning.", scale="output", mult=0.9, burn=3),
            dict(id="backdraft", name="Backdraft", tier=1, ce=14,
                 desc="Set it now. It goes off later.", scale="output", mult=1.4, burn=6),
            dict(id="kindling", name="Kindling", tier=2, ce=18,
                 desc="Lend the burn to whoever is beside you.", scale="output", mult=1.1, ally_buff=True),
        ],
        "aftersound": [
            dict(id="echo", name="Echo", tier=0, ce=5,
                 desc="Hear the half-second before it moves.", scale="insight", mult=0.8, reveal=True),
            dict(id="overlay", name="Overlay", tier=1, ce=12,
                 desc="Be where it is going to be.", scale="insight", mult=1.3, freedodge=True),
            dict(id="chorus", name="Chorus", tier=2, ce=20,
                 desc="Replay someone else's technique, badly.", scale="insight", mult=2.0, stagger=True),
        ],
    }

    def refresh_vitals():
        store.hp_max = 50 + store.output + (store.control // 3)
        store.hp = min(store.hp, store.hp_max)

    def moves_available():
        t = tech_tier()[0]
        return [m for m in MOVES[store.technique] if m["tier"] <= t]

    def can_read():
        """Insight high enough to understand a telegraph without spending a turn."""
        return store.insight >= 45

    ## --- the fight ------------------------------------------------------------

    def combat_begin(key, ally=None, flee_ok=True, bg=None):
        e = ENEMIES[key]
        refresh_vitals()
        store.cb = dict(
            key=key, name=e["name"], grade=e["grade"],
            ehp=e["hp"], ehp_max=e["hp"], power=e["power"], sprite=e["sprite"],
            tells=list(e["tells"]), tell=None, kind=None,
            ally=ally, flee_ok=flee_ok, bg=(bg or graded_bg()),
            read=can_read(), burn=0, stagger=0, freedodge=False, ally_buff=0,
            answered=False, punish=False,
            log=[], round=1, over=None,
        )
        combat_telegraph()

    def combat_telegraph():
        c = store.cb
        t = renpy.random.choice(c["tells"])
        c["tell"], c["kind"] = t[0], t[1]

    def clog(msg):
        store.cb["log"] = ([msg] + store.cb["log"])[:4]

    def _dmg(base, scale):
        stat = getattr(store, scale)
        return max(1, int(base * (0.6 + stat / 60.0)))

    def combat_player(action, move=None):
        """Resolve the player's action. Returns True if the fight has ended.

        Answering the telegraph defends and staggers but deals little. Using a
        technique deals real damage but leaves the telegraph unanswered, so it
        lands. That trade is the whole fight."""
        c = store.cb
        answer = ANSWERS[c["kind"]]
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
            clog("You stop and listen. You can read it now — but it doesn't wait.")

        elif action == "move":
            if not spend_ce(move["ce"]):
                clog("Not enough reserve for %s." % move["name"])
                return False
            if move.get("heal"):
                h = _dmg(13, "control")
                store.hp = min(store.hp_max, store.hp + h)
                clog("%s — you close what's open. +%d." % (move["name"], h))
            else:
                d = _dmg(int(11 * move["mult"]), move["scale"])
                if c["stagger"]:
                    d = int(d * 1.5)
                c["ehp"] -= d
                clog("%s — %d." % (move["name"], d))
            if move.get("burn"):
                c["burn"] = min(10, c["burn"] + move["burn"])
            if move.get("reveal"):
                c["read"] = True
            if move.get("freedodge"):
                c["freedodge"] = True
            if move.get("stagger"):
                c["stagger"] = 1
            if move.get("ally_buff"):
                c["ally_buff"] = 2

        elif action == "flee":
            c["over"] = "fled"
            return True

        if c["ehp"] <= 0:
            c["over"] = "win"
            return True
        return False

    def combat_enemy():
        """The curse acts, then telegraphs its next move."""
        c = store.cb

        if c["burn"]:
            c["ehp"] -= c["burn"]
            clog("It is still burning. %d." % c["burn"])
            c["burn"] = c["burn"] // 2
            if c["ehp"] <= 0:
                c["over"] = "win"
                return

        if c["ally"]:
            a = _dmg(7 + c["ally_buff"] * 3, "output")
            c["ehp"] -= a
            clog("%s goes in. %d." % (CAST[c["ally"]]["short"], a))
            c["ally_buff"] = max(0, c["ally_buff"] - 1)
            if c["ehp"] <= 0:
                c["over"] = "win"
                return

        if c["stagger"]:
            c["stagger"] -= 1
            clog("It is still recovering.")
        elif c["answered"]:
            pass                                    # you were where it wasn't
        elif c["freedodge"]:
            c["freedodge"] = False
            clog("You are already somewhere else when it arrives.")
        else:
            mult = 1.5 if c["punish"] else 1.0
            d = max(1, int(c["power"] * mult * (1.0 - min(0.35, store.control / 260.0))))
            store.hp -= d
            clog("It connects. %d." % d)
            if store.hp <= 0:
                store.hp = 0
                c["over"] = "down"
                return

        c["round"] += 1
        combat_telegraph()


default hp = 60
default hp_max = 60
default cb = {}


################################################################################
## The fight loop
################################################################################

label combat(enemy, ally=None, flee_ok=True, bg=None):

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
            $ quick_menu = True
            return _outcome


################################################################################
## Screen
################################################################################

screen combat_screen():

    modal True
    tag sandbox

    $ _c = cb
    $ _ename = _c["name"]
    $ _grade = _c["grade"]
    $ _tell = _c["tell"]
    $ _meaning = ANSWER_LABEL[ANSWERS[_c["kind"]]] if _c["read"] else "?"
    $ _moves = moves_available()
    $ _log = _c["log"]
    $ _round = _c["round"]

    add _c["bg"]
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
        text "GRADE [_grade] · ROUND [_round]":
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

            hbox:
                spacing 40
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

                null width 20

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
