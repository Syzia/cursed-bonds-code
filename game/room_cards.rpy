################################################################################
## Cursed Bonds — the card table.
##
## Phase 2, P7 (PHASE2_DESIGN.md 4.12, D32, 6.1). Blackjack and five-card draw,
## for yen, against whoever is in the common room (three at most).
##
##   cards_ok()                 the table can be sat at now (the place action's
##                              `when`)
##   cards_new(game, opponents, stake)   builds cards_state for a game
##   cards_records()            dict(today=<yen won today>), for the Me page
##   label sb_do_cards_play     the place action: the table, then a game
##   label mg_blackjack(opponents, stake=0), label mg_poker(opponents, stake=0)
##                              the two games (the interface is sb_hotspots.rpy's:
##                              register_minigame, mg_games, mg_result)
##   screens cards_table, cards_blackjack, cards_poker
##
## The rules, in one place:
##   - a sitting is five hands at most (CARDS_LIMIT), over both games, and ends
##     when I'm ¥3,000 down or when I leave. It costs one period if a hand was
##     played, and gives Bond +1 with each opponent once a day;
##   - a stake is taken from my yen when the hand is dealt (and each bet when
##     it is made), so I can never stake more than I hold;
##   - the day's winnings never pass BOARD_YEN["g4"][1]: blackjack isn't dealt
##     at a stake that could pass it, and a poker pot is paid only up to it;
##   - every deal, draw and settlement is followed by cards_block(), which
##     blocks rollback: a lost hand can't be replayed with the next card known.
##     The next card is also picked when it is drawn, not when the deck is
##     shuffled, so a reloaded save doesn't know it either.
##
## State is plain data: cards_state (the game in progress; cards are ints 0 to
## 51: rank = c % 13 with 0 the two and 12 the ace, suit = c // 13) and
## cards_sit (the sitting's tally). Nothing here draws a toast: the screens are
## tagged `sandbox`, so toasts wait until I get up (R6).
##
## The hotspot on the table itself is room_spots.rpy's (P6); this file
## registers the place action it stands for.
################################################################################

define gui.cards_red = "#d8263f"        # hearts and diamonds
define gui.cards_black = "#16121f"      # spades and clubs
define gui.cards_paper = "#f1ecdf"      # a card's face
define gui.cards_felt = "#12301f"       # the table top

init -1 python:

    CARDS_STAKES = (100, 500, 1000)
    CARDS_LIMIT = dict(hands=5, down=3000)

    CARDS_RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
    CARDS_SUITS = (u"♠", u"♥", u"♦", u"♣")
    CARDS_SUIT_FONT = "DejaVuSans.ttf"
    CARDS_BACK = "gui/card_back.png"    # drawn by tools/gen_gui.py; a flat panel until it exists
    CARDS_HANDS = ("High card", "A pair", "Two pair", "Three of a kind", "Straight",
                   "Flush", "Full house", "Four of a kind", "Straight flush")
    CARDS_LIVE = ("play", "bet1", "call1", "draw", "bet2", "call2")     # a hand is being played
    CARDS_READ_AT = 20                  # the Insight a read takes
    CARDS_GAMES = ("blackjack", "poker")    # the games this file plays
    CARDS_BLURB = {
        "blackjack": "Against the dealer. Twenty-one, or as near as I dare.",
        "poker": "The cards matter less than the faces. Watch them.",
    }

    ## How each of the eleven plays (D32). tight: how good a hand they want
    ## before they put money in (0 loose, 1 tight). bluff: how often they bet
    ## on nothing. tell: the expression their face slips into; shows: what
    ## that gives away ("bluff", "bet": about to bet, "strong", "weak", or
    ## None: nothing). rest: the face they wear otherwise; sore: when they
    ## lose a hand. blind: plays without looking (the cards don't steer them).
    ## win / lose: what they say when they win or lose a hand; stop: when
    ## they've lost all they mean to today.
    CARDS_STYLE = {
        "yuji": dict(tight=0.3, bluff=0.45, tell="serious", shows="bluff", rest="happy", sore="surprised",
                     win="Ha! Sorry. Not that sorry.",
                     lose="No way. One more, one more.",
                     stop="I'm out. That was my ramen money."),
        "megumi": dict(tight=0.7, bluff=0.1, tell="neutral", shows=None, rest="neutral", sore="serious",
                       win="You hesitated.",
                       lose="Hm. Take it.",
                       stop="That's enough of my money."),
        "nobara": dict(tight=0.45, bluff=0.3, tell="angry", shows="bet", rest="neutral", sore="angry",
                       win="Pay up. I've got my eye on a jacket.",
                       lose="Tch. You got lucky.",
                       stop="I'm done. You're buying lunch."),
        "maki": dict(tight=0.6, bluff=0.2, tell="angry", shows="weak", rest="serious", sore="angry",
                     win="Too slow. Hand it over.",
                     lose="Not bad. Don't get used to it.",
                     stop="That's all you're getting out of me today."),
        "panda": dict(tight=0.5, bluff=0.1, tell="happy", shows="strong", rest="neutral", sore="sad",
                      win="Panda wins! Don't look at me like that.",
                      lose="Aw. I really thought I had that one.",
                      stop="I'm cleaned out. Pandas don't even get an allowance."),
        "toge": dict(tight=0.5, bluff=0.35, tell="neutral", shows=None, rest="neutral", sore="neutral",
                     win="Salmon.",
                     lose="Bonito flakes.",
                     stop="Mustard leaf."),
        "shoko": dict(tight=0.5, bluff=0.25, tell="happy", shows="bluff", rest="neutral", sore="neutral",
                      win="Mm. That covers tonight.",
                      lose="Fine. I wasn't using it.",
                      stop="That's my limit. I have rounds."),
        "gojo": dict(tight=0.0, bluff=0.5, tell="happy", shows=None, rest="happy", sore="surprised", blind=True,
                     win="I wasn't even looking. Isn't that great?",
                     lose="Oh no. Whatever will I do.",
                     stop="Okay, okay. Even my wallet has feelings."),
        "yaga": dict(tight=0.8, bluff=0.05, tell="angry", shows="weak", rest="serious", sore="serious",
                     win="Discipline. That's all it is.",
                     lose="Hmph. Well played.",
                     stop="Enough. Go and do something useful."),
        "utahime": dict(tight=0.55, bluff=0.15, tell="sad", shows="weak", rest="serious", sore="angry",
                        win="See? Patience.",
                        lose="Not a word about this to anyone.",
                        stop="No more. I'm not paying for your weekend."),
        "ijichi": dict(tight=0.75, bluff=0.05, tell="surprised", shows="strong", rest="neutral", sore="sad",
                       win="Oh. I'm sorry. I think I won.",
                       lose="I should have folded. I always should have folded.",
                       stop="Please. I have rent."),
    }
    CARDS_STYLE_ANY = dict(tight=0.5, bluff=0.2, tell="neutral", shows=None, rest="neutral", sore="neutral",
                           win="Mine.", lose="Yours.", stop="That's enough for today.")

    ## Small things ---------------------------------------------------------------

    def cards_yen(n):
        """P7. "¥1,500"."""
        return u"¥{:,}".format(int(n))

    def cards_signed(n):
        """P7. "+¥500", "−¥500" or "±¥0"."""
        n = int(n)
        return (u"+" if n > 0 else (u"−" if n < 0 else u"±")) + cards_yen(abs(n))

    def cards_style(who):
        """P7. Someone's CARDS_STYLE row (a plain one for a stranger)."""
        return CARDS_STYLE.get(who) or CARDS_STYLE_ANY

    def cards_short(who):
        """P7. Someone's short name."""
        return (CAST.get(who) or {}).get("short") or str(who).title()

    def cards_rank(c):
        """P7. A card's rank, 2 to 14 (the ace)."""
        return int(c) % 13 + 2

    def cards_suit(c):
        """P7. A card's suit, 0 to 3 (spades, hearts, diamonds, clubs)."""
        return int(c) // 13

    def cards_color(c):
        """P7. The colour a card's rank and suit are drawn in."""
        return gui.cards_red if cards_suit(c) in (1, 2) else gui.cards_black

    def cards_deck():
        """P7. A fresh deck: the ints 0 to 51, shuffled (renpy.random)."""
        d = list(range(52))
        renpy.random.shuffle(d)
        return d

    def cards_draw(st):
        """P7. Takes one card from the state's deck. The deck is shuffled
        again first, so the card is chosen now: neither a rollback nor a
        reloaded save knows what comes next."""
        renpy.random.shuffle(st["deck"])
        return st["deck"].pop()

    def cards_block():
        """P7. Blocks rollback. The labels call it after every deal, every
        draw and every settlement (4.12). Returns None."""
        renpy.block_rollback()
        return None

    ## The day's winnings and the sitting -----------------------------------------

    def cards_today():
        """P7. The yen won at cards today (negative when I'm down)."""
        return int(store.cards_won) if store.cards_won_day == store.day else 0

    def cards_cap():
        """P7. The most a day at the table may win: a Grade 4 job's best pay."""
        return int(BOARD_YEN["g4"][1])

    def cards_cap_left():
        """P7. How much more I may win today."""
        return max(0, cards_cap() - cards_today())

    def cards_bank(n):
        """P7. Adds a hand's net result to the day's winnings."""
        if store.cards_won_day != store.day:
            store.cards_won_day = store.day
            store.cards_won = 0
        store.cards_won += int(n)

    def cards_records():
        """P7 (room_cards.rpy). dict(today=int): the yen won at cards today
        (negative when I lost), for the journal's Me page."""
        return dict(today=cards_today())

    def cards_opponents():
        """P7. Who sits down with me: the people in the common room, three
        at most."""
        return list(who_is_here("dorm_common"))[:3]

    def cards_ok():
        """P7 (room_cards.rpy). bool: the card table can be sat at now:
        someone is in the common room, I have the smallest stake, and I
        haven't already sat today with everyone who is here."""
        if store.explore_mode:
            return False
        opp = cards_opponents()
        if not opp:
            return False
        if store.yen < CARDS_STAKES[0]:
            return False
        if all(("cards:" + w) in store.actions_today for w in opp):
            return False
        return True

    def cards_tally():
        """P7. (hands, net) of the sitting: from the game in progress, else
        from the sitting's own tally."""
        st = store.cards_state
        if st:
            return int(st.get("hands", 0)), int(st.get("net", 0))
        sit = store.cards_sit or {}
        return int(sit.get("hands", 0)), int(sit.get("net", 0))

    def cards_tally_line():
        """P7. "Hand 2 of 5 · ¥300 up": the hand on the table (or the next
        one, between games) and the sitting's yen so far."""
        hands, net = cards_tally()
        if not (store.cards_state or {}).get("stage") in CARDS_LIVE + ("done",):
            hands += 1
        if hands > CARDS_LIMIT["hands"]:
            head = "%d hands played" % CARDS_LIMIT["hands"]
        else:
            head = "Hand %d of %d" % (hands, CARDS_LIMIT["hands"])
        tail = "even" if not net else ("%s %s" % (cards_yen(abs(net)), "up" if net > 0 else "down"))
        return u"%s · %s" % (head, tail)

    def cards_need(game, stake):
        """P7. The yen I must hold to be dealt a hand: the stake at
        blackjack; the ante and both bets at poker, so I can always see a
        hand through."""
        return int(stake) * (3 if game == "poker" else 1)

    def cards_can_deal(game, stake):
        """P7. Why a hand can't be dealt now, as a first-person line; ""
        when it can. The sitting's five hands and ¥3,000; my yen; the
        day's winnings (blackjack needs room for a doubled win)."""
        hands, net = cards_tally()
        stake = int(stake)
        if hands >= CARDS_LIMIT["hands"]:
            return "Five hands. That's the sitting."
        if net <= -CARDS_LIMIT["down"]:
            return "I'm %s down. Enough." % cards_yen(CARDS_LIMIT["down"])
        if store.yen < cards_need(game, stake):
            return "I'd need %s for that." % cards_yen(cards_need(game, stake))
        room = stake * (2 if game == "blackjack" else 1)
        if stake and cards_cap_left() < room:
            return "They've lost enough to me today."
        return ""

    def cards_sit_down(opponents):
        """P7. Starts a sitting's tally. Returns None."""
        store.cards_sit = dict(day=store.day, hands=0, net=0, opponents=list(opponents)[:3])
        return None

    def cards_sit_note(game):
        """P7. After a game's label returns: a game that isn't this file's
        (chess, later) is counted from mg_result. Returns None."""
        sit = store.cards_sit
        res = store.mg_result or {}
        if sit and game not in CARDS_GAMES and res.get("game") == game and res.get("outcome") != "quit":
            sit["hands"] = int(sit.get("hands", 0)) + 1
            sit["net"] = int(sit.get("net", 0)) + int(res.get("yen", 0))
        return None

    def cards_sit_over():
        """P7. The line that ends the sitting, or "" while it goes on."""
        sit = store.cards_sit or {}
        opp = sit.get("opponents") or cards_opponents()
        first = opp[0] if opp else None
        if int(sit.get("hands", 0)) >= CARDS_LIMIT["hands"]:
            return "Five hands. %s gathers the cards up." % (cards_short(first) if first else "Somebody")
        if int(sit.get("net", 0)) <= -CARDS_LIMIT["down"]:
            return "I'm %s down. I push my chair back before it gets worse." % cards_yen(CARDS_LIMIT["down"])
        if cards_cap_left() < 2 * CARDS_STAKES[0]:
            if first:
                return "%s pushes the deck away. \"%s\"" % (cards_short(first), cards_style(first)["stop"])
            return "Nobody will play me again today."
        if store.yen < CARDS_STAKES[0]:
            return "My pockets are empty. That's the game."
        return ""

    def cards_get_up():
        """P7. Ends the sitting. If a hand was played: Bond +1 with each
        opponent, once a day each, and one period. Returns None."""
        sit = store.cards_sit or {}
        played = int(sit.get("hands", 0)) > 0
        opp = list(sit.get("opponents") or [])
        store.cards_sit = {}
        store.cards_state = {}
        if not played:
            return None
        for w in opp:
            key = "cards:" + w
            if key not in store.actions_today:
                store.actions_today.add(key)
                add_bond(w, 1)
        advance_period_soft(1)
        return None

    ## The game in progress -------------------------------------------------------

    def cards_new(game, opponents, stake):
        """P7 (room_cards.rpy). Builds the state of a game about to be
        played, puts it in cards_state and returns it: a plain dict. The
        hands and the yen of the sitting so far carry in from cards_sit."""
        sit = store.cards_sit or {}
        st = dict(game=str(game), opponents=list(opponents)[:3], stake=max(0, int(stake)),
                  deck=[], stage="idle",
                  hands=int(sit.get("hands", 0)), net=int(sit.get("net", 0)),
                  played=0, won=0, put=0, last=0, result="", line="", says="", speaker="",
                  face={}, capped=False)
        if game == "blackjack":
            st.update(dealer=[], mine=[], bet=0, hide=True)
        elif game == "poker":
            st.update(theirs={}, mine=[], pot=0, live=[], me_in=False, plan={}, owed=0, bettor="",
                      marks=dict((i, False) for i in range(5)), read="", read_used=False,
                      drew={}, paid={}, shown=[])
        store.cards_state = st
        return st

    def cards_finish_hand(pay, result):
        """P7. Settles a hand: `pay` yen come back to me (my own stake
        included), the net goes on the day's winnings and the sitting's
        tally. Returns the net."""
        st = store.cards_state
        pay = max(0, int(pay))
        add_yen(pay)
        net = pay - int(st.get("put", 0))
        cards_bank(net)
        st["net"] = int(st.get("net", 0)) + net
        st["won"] = int(st.get("won", 0)) + net
        st["last"] = net
        st["put"] = 0
        st["result"] = result
        st["stage"] = "done"
        return net

    def cards_forfeit():
        """P7. Leaving in the middle of a hand gives it up. Returns None."""
        st = store.cards_state
        if not st:
            return None
        if st.get("game") == "blackjack" and st.get("stage") == "play":
            st["hide"] = False
            cards_bj_react("left")
            cards_finish_hand(0, "left")
        elif st.get("game") == "poker" and st.get("stage") in CARDS_LIVE:
            st["me_in"] = False
            cards_pk_showdown()
        return None

    def cards_end():
        """P7. Leaves the game: sets mg_result = dict(game, outcome, yen),
        carries the tally to the sitting and clears cards_state. outcome is
        "quit" when no hand was played. Returns None."""
        st = store.cards_state or {}
        won = int(st.get("won", 0))
        if not st.get("played"):
            outcome = "quit"
        else:
            outcome = "win" if won > 0 else ("lose" if won < 0 else "even")
        store.mg_result = dict(game=st.get("game", ""), outcome=outcome, yen=won)
        if store.cards_sit:
            store.cards_sit["hands"] = int(st.get("hands", 0))
            store.cards_sit["net"] = int(st.get("net", 0))
        store.cards_state = {}
        return None

    def cards_result_line():
        """P7. What the last hand came to, in my words."""
        st = store.cards_state or {}
        res = st.get("result")
        if not res:
            return ""
        if st.get("game") == "blackjack":
            text = {"natural": "Twenty-one off the deal.", "win": "My hand.", "push": "A push. My stake comes back.",
                    "bust": "Over. I'm bust.", "lose": "The dealer's hand.", "left": "I leave my stake on the table."}.get(res, "")
        else:
            text = {"win": "The pot's mine.", "split": "A split pot.", "lose": "Not my pot.",
                    "fold": "I fold."}.get(res, "")
        if st.get("capped"):
            text += " They won't pay past that today."
        return u"%s  %s" % (text, cards_signed(st.get("last", 0)))

    def cards_auto(where):
        """P7. What the test harness's autoplay answers a cards screen with:
        one hand of the first game at the smallest stake, standing or
        checking, then away."""
        st = store.cards_state or {}
        if where == "table":
            if cards_tally()[0]:
                return ("close",)
            for g in mg_games():
                if renpy.has_label("mg_" + g["id"]) and not cards_can_deal(g["id"], CARDS_STAKES[0]):
                    return ("play", g["id"], CARDS_STAKES[0])
            return ("close",)
        stage = st.get("stage")
        if where == "blackjack":
            return ("stand",) if stage == "play" else ("leave",)
        if stage in ("bet1", "bet2"):
            return ("check",)
        if stage in ("call1", "call2"):
            return ("bet",) if store.yen >= int(st.get("owed", 0)) else ("fold",)
        if stage == "draw":
            return ("draw", ())
        return ("leave",)

    ## Blackjack ------------------------------------------------------------------

    def cards_total(hand):
        """P7. A blackjack hand's total: an ace counts eleven while that
        doesn't bust the hand, else one."""
        total = 0
        aces = 0
        for c in hand:
            r = cards_rank(c)
            if r == 14:
                aces += 1
                total += 11
            elif r >= 10:
                total += 10
            else:
                total += r
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def cards_natural(hand):
        """P7. bool: twenty-one in two cards."""
        return len(hand) == 2 and cards_total(hand) == 21

    def cards_dealer():
        """P7. Who deals at blackjack: the first opponent (None at an empty
        table)."""
        opp = (store.cards_state or {}).get("opponents") or []
        return opp[0] if opp else None

    def cards_bj_react(result):
        """P7. The dealer's line and face after a hand."""
        st = store.cards_state
        who = cards_dealer()
        if who is None:
            return
        sty = cards_style(who)
        st["speaker"] = who
        if result in ("win", "natural"):
            st["says"], st["face"] = sty["lose"], {who: sty["sore"]}
        elif result == "push":
            st["says"], st["face"] = "", {who: sty["rest"]}
        else:
            st["says"], st["face"] = sty["win"], {who: "happy"}

    def cards_bj_deal():
        """P7. Deals a hand of blackjack: my stake leaves my yen, two cards
        each. A natural on either side settles at once. Returns True if a
        hand was dealt."""
        st = store.cards_state
        if not st or st.get("game") != "blackjack" or st["stage"] not in ("idle", "done"):
            return False
        if cards_can_deal("blackjack", st["stake"]):
            return False
        st["deck"] = cards_deck()
        st["mine"] = [cards_draw(st), cards_draw(st)]
        st["dealer"] = [cards_draw(st), cards_draw(st)]
        st["bet"] = st["stake"]
        add_yen(-st["bet"])
        st["put"] = st["bet"]
        st["hide"] = True
        st["result"] = ""
        st["capped"] = False
        st["says"] = ""
        st["line"] = ""
        who = cards_dealer()
        st["face"] = {who: cards_style(who)["rest"]} if who else {}
        st["hands"] += 1
        st["played"] += 1
        st["stage"] = "play"
        if cards_natural(st["mine"]) or cards_natural(st["dealer"]):
            cards_bj_settle()
        return True

    def cards_bj_hit():
        """P7. One more card for me; over 21 settles the hand."""
        st = store.cards_state
        if not st or st.get("game") != "blackjack" or st["stage"] != "play":
            return False
        st["mine"].append(cards_draw(st))
        if cards_total(st["mine"]) > 21:
            cards_bj_settle()
        return True

    def cards_bj_stand():
        """P7. I stand: the dealer draws to 17 and the hand settles."""
        st = store.cards_state
        if not st or st.get("game") != "blackjack" or st["stage"] != "play":
            return False
        while cards_total(st["dealer"]) < 17:
            st["dealer"].append(cards_draw(st))
        cards_bj_settle()
        return True

    def cards_bj_can_double():
        """P7. bool: Double is open: my first two cards, a second stake in
        my pocket, and room under the day's winnings for a doubled win."""
        st = store.cards_state or {}
        return bool(st.get("game") == "blackjack" and st.get("stage") == "play" and len(st["mine"]) == 2
                    and st["bet"] == st["stake"] and store.yen >= st["stake"]
                    and cards_cap_left() >= 2 * st["stake"])

    def cards_bj_double():
        """P7. Double: a second stake, one card, then I stand."""
        st = store.cards_state
        if not cards_bj_can_double():
            return False
        add_yen(-st["stake"])
        st["put"] += st["stake"]
        st["bet"] += st["stake"]
        st["mine"].append(cards_draw(st))
        if cards_total(st["mine"]) > 21:
            cards_bj_settle()
        else:
            cards_bj_stand()
        return True

    def cards_bj_settle():
        """P7. Settles blackjack: a win pays 1:1, a natural 3:2, a push
        returns the stake."""
        st = store.cards_state
        st["hide"] = False
        me, dl = cards_total(st["mine"]), cards_total(st["dealer"])
        mine_nat, deal_nat = cards_natural(st["mine"]), cards_natural(st["dealer"])
        bet = st["bet"]
        if me > 21:
            res, pay = "bust", 0
        elif mine_nat and not deal_nat:
            res, pay = "natural", bet + bet * 3 // 2
        elif deal_nat and not mine_nat:
            res, pay = "lose", 0
        elif dl > 21 or me > dl:
            res, pay = "win", 2 * bet
        elif me == dl:
            res, pay = "push", bet
        else:
            res, pay = "lose", 0
        cards_bj_react(res)
        return cards_finish_hand(pay, res)

    ## Poker: five-card draw ------------------------------------------------------

    def cards_pk_rank(hand):
        """P7. A five-card hand's rank as a tuple that sorts by strength:
        (category 0 to 8, then the ranks that break a tie). The wheel
        (A-2-3-4-5) is a straight to the five."""
        ranks = sorted((cards_rank(c) for c in hand), reverse=True)
        counts = {}
        for r in ranks:
            counts[r] = counts.get(r, 0) + 1
        groups = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        order = tuple(r for r, n in groups)
        shape = tuple(n for r, n in groups)
        flush = len(set(cards_suit(c) for c in hand)) == 1
        straight = len(counts) == 5 and ranks[0] - ranks[4] == 4
        if ranks == [14, 5, 4, 3, 2]:
            straight = True
            order = (5, 4, 3, 2, 1)
        if straight and flush:
            cat = 8
        elif shape[0] == 4:
            cat = 7
        elif shape == (3, 2):
            cat = 6
        elif flush:
            cat = 5
        elif straight:
            cat = 4
        elif shape[0] == 3:
            cat = 3
        elif shape == (2, 2, 1):
            cat = 2
        elif shape[0] == 2:
            cat = 1
        else:
            cat = 0
        return (cat,) + order

    def cards_pk_name(hand):
        """P7. "Two pair"."""
        return CARDS_HANDS[cards_pk_rank(hand)[0]] if len(hand) == 5 else ""

    def cards_pk_strength(hand):
        """P7. How good a five-card hand is, 0.0 to 1.0: roughly the share
        of dealt hands it beats."""
        rk = cards_pk_rank(hand)
        cat, top = rk[0], rk[1]
        if cat == 0:
            return max(0.0, min(0.5, (top - 7) / 14.0))
        if cat == 1:
            return 0.5 + (top - 2) / 12.0 * 0.42
        if cat == 2:
            return 0.93
        if cat == 3:
            return 0.96
        return 0.98 + 0.004 * (cat - 4)

    def cards_pk_steps(hand):
        """P7. A hand's strength as the read shows it: 1 to 5."""
        return 1 + min(4, int(cards_pk_strength(hand) * 5))

    def cards_pk_face(who, strength, plan):
        """P7. The expression someone wears for the betting round ahead:
        their tell most of the time when what it gives away is true, now
        and then when it isn't, else their resting face."""
        sty = cards_style(who)
        shows = sty.get("shows")
        if not shows:
            return sty["rest"]
        on = {"bluff": plan["bluff"], "bet": plan["bet"], "strong": strength >= 0.7, "weak": strength < 0.45}.get(shows, False)
        return sty["tell"] if renpy.random.random() < (0.85 if on else 0.08) else sty["rest"]

    def cards_pk_plan():
        """P7. Decides, for the betting round ahead, what each opponent
        still in will do (bet when checked to; call when bet into) and
        what their face gives away. Kept in the state, so a face doesn't
        change while I look at it."""
        st = store.cards_state
        plan = {}
        face = dict(st.get("face") or {})
        for w in st["live"]:
            sty = cards_style(w)
            s = cards_pk_strength(st["theirs"][w])
            if sty.get("blind"):
                bluff = False
                bet = renpy.random.random() < 0.5
                call = bet or renpy.random.random() < 0.6
            else:
                strong = s >= 0.5 + 0.35 * sty["tight"]
                bluff = (not strong) and renpy.random.random() < sty["bluff"] * 0.6
                bet = strong or bluff
                call = bet or s >= 0.3 + 0.35 * sty["tight"] or renpy.random.random() < sty["bluff"] * 0.4
            plan[w] = dict(bet=bool(bet), call=bool(call), bluff=bool(bluff))
            face[w] = cards_pk_face(w, s, plan[w])
        st["plan"] = plan
        st["face"] = face

    def cards_pk_deal():
        """P7. Deals a hand of five-card draw: an ante of one stake from
        everyone, five cards each. Returns True if a hand was dealt."""
        st = store.cards_state
        if not st or st.get("game") != "poker" or st["stage"] not in ("idle", "done"):
            return False
        if cards_can_deal("poker", st["stake"]):
            return False
        opp = list(st["opponents"])
        st["deck"] = cards_deck()
        st["mine"] = [cards_draw(st) for i in range(5)]
        st["theirs"] = dict((w, [cards_draw(st) for i in range(5)]) for w in opp)
        st["live"] = opp
        st["me_in"] = True
        add_yen(-st["stake"])
        st["put"] = st["stake"]
        st["pot"] = st["stake"] * (len(opp) + 1)
        st["marks"] = dict((i, False) for i in range(5))
        st["read"] = ""
        st["read_used"] = False
        st["owed"] = 0
        st["bettor"] = ""
        st["drew"] = {}
        st["paid"] = {}
        st["shown"] = []
        st["result"] = ""
        st["capped"] = False
        st["line"] = "Everyone antes %s." % cards_yen(st["stake"])
        st["says"] = ""
        st["speaker"] = ""
        st["face"] = {}
        st["hands"] += 1
        st["played"] += 1
        st["stage"] = "bet1"
        cards_pk_plan()
        return True

    def cards_pk_names(folk):
        """P7. "Megumi and Yuji"."""
        names = [cards_short(w) for w in folk]
        if len(names) <= 1:
            return "".join(names)
        return ", ".join(names[:-1]) + " and " + names[-1]

    def cards_pk_answer(skip=None):
        """P7. Everyone still in, but `skip`, answers a bet: a stake into
        the pot, or out. Returns the sentence that says who did what."""
        st = store.cards_state
        called, folded = [], []
        for w in list(st["live"]):
            if w == skip:
                continue
            if (st["plan"].get(w) or {}).get("call"):
                st["pot"] += st["stake"]
                called.append(w)
            else:
                st["live"].remove(w)
                folded.append(w)
        parts = []
        if called:
            parts.append("%s call%s." % (cards_pk_names(called), "s" if len(called) == 1 else ""))
        if folded:
            parts.append("%s fold%s." % (cards_pk_names(folded), "s" if len(folded) == 1 else ""))
        return " ".join(parts)

    def cards_pk_advance():
        """P7. After a betting round: the draw, or the showdown."""
        st = store.cards_state
        st["owed"] = 0
        st["bettor"] = ""
        if not st["live"] or st["stage"] in ("bet2", "call2"):
            cards_pk_showdown()
        else:
            st["stage"] = "draw"

    def cards_pk_bet():
        """P7. On my turn: I bet one stake and everyone answers. Facing a
        bet: I call it. Refused when I don't hold the yen."""
        st = store.cards_state
        if not st or st.get("game") != "poker":
            return False
        stake = st["stake"]
        if st["stage"] in ("bet1", "bet2"):
            if store.yen < stake:
                return False
            add_yen(-stake)
            st["put"] += stake
            st["pot"] += stake
            st["line"] = ("I bet %s. " % cards_yen(stake)) + cards_pk_answer()
            cards_pk_advance()
            return True
        if st["stage"] in ("call1", "call2"):
            owed = st["owed"]
            if store.yen < owed:
                return False
            add_yen(-owed)
            st["put"] += owed
            st["pot"] += owed
            st["line"] = ("I call. " + cards_pk_answer(skip=st["bettor"])).strip()
            cards_pk_advance()
            return True
        return False

    def cards_pk_check():
        """P7. I check. The first opponent who means to bet does, and then
        it is on me to call or fold; otherwise the round is over."""
        st = store.cards_state
        if not st or st.get("game") != "poker" or st["stage"] not in ("bet1", "bet2"):
            return False
        bettor = None
        for w in st["live"]:
            if (st["plan"].get(w) or {}).get("bet"):
                bettor = w
                break
        if bettor is None:
            st["line"] = "Checks all round."
            cards_pk_advance()
            return True
        st["pot"] += st["stake"]
        st["owed"] = st["stake"]
        st["bettor"] = bettor
        st["line"] = "I check. %s bets %s." % (cards_short(bettor), cards_yen(st["stake"]))
        st["stage"] = "call1" if st["stage"] == "bet1" else "call2"
        return True

    def cards_pk_fold():
        """P7. I fold: what I put in stays in the pot, and the others
        settle it between them."""
        st = store.cards_state
        if not st or st.get("game") != "poker" or st["stage"] not in ("bet1", "call1", "bet2", "call2"):
            return False
        st["me_in"] = False
        cards_pk_showdown()
        return True

    def cards_pk_discards(hand, blind=False):
        """P7. The cards an opponent throws away at the draw, as indexes:
        nothing from a made hand, everything outside a pair, two pair or
        three of a kind, and the three lowest of nothing at all. Someone
        playing blind throws away any three or fewer."""
        if blind:
            return sorted(renpy.random.sample(list(range(5)), renpy.random.randint(0, 3)))
        cat = cards_pk_rank(hand)[0]
        if cat >= 4:
            return []
        ranks = [cards_rank(c) for c in hand]
        if cat == 0:
            keep = sorted(range(5), key=lambda i: ranks[i], reverse=True)[:2]
            return sorted(i for i in range(5) if i not in keep)
        return sorted(i for i in range(5) if ranks.count(ranks[i]) == 1)[:3]

    def cards_pk_draw(idx=()):
        """P7. The draw: I throw away the cards at these indexes (three at
        most) and take new ones; then everyone still in draws."""
        st = store.cards_state
        if not st or st.get("game") != "poker" or st["stage"] != "draw":
            return False
        mine = sorted(set(int(i) for i in (idx or ()) if 0 <= int(i) < 5))[:3]
        for i in mine:
            st["mine"][i] = cards_draw(st)
        took = []
        for w in st["live"]:
            out = cards_pk_discards(st["theirs"][w], bool(cards_style(w).get("blind")))
            for i in out:
                st["theirs"][w][i] = cards_draw(st)
            st["drew"][w] = len(out)
            took.append("%s takes %d." % (cards_short(w), len(out)))
        st["marks"] = dict((i, False) for i in range(5))
        st["line"] = ("I take %d. " % len(mine)) + " ".join(took)
        st["stage"] = "bet2"
        cards_pk_plan()
        return True

    def cards_pk_can_read():
        """P7. bool: the read is on offer: Insight 20, once a hand, while
        the hand is live and someone is still in."""
        st = store.cards_state or {}
        return bool(st.get("game") == "poker" and st.get("stage") in CARDS_LIVE
                    and not st.get("read_used") and store.insight >= CARDS_READ_AT and st.get("live"))

    def cards_pk_read(who):
        """P7. I read one opponent: their hand's strength shows as a
        five-step bar for the rest of the hand. Once a hand."""
        st = store.cards_state
        if not cards_pk_can_read() or who not in st["live"]:
            return False
        st["read"] = who
        st["read_used"] = True
        return True

    def cards_pk_showdown():
        """P7. Settles poker: the best hand still in takes the pot; equal
        hands split it. What I win is paid only up to the day's limit."""
        st = store.cards_state
        players = (["me"] if st["me_in"] else []) + list(st["live"])
        if not players:
            players = list(st["opponents"][:1])
        ranks = dict((p, cards_pk_rank(st["mine"] if p == "me" else st["theirs"][p])) for p in players)
        best = max(ranks.values())
        winners = [p for p in players if ranks[p] == best]
        share, rem = divmod(int(st["pot"]), len(winners))
        st["paid"] = dict((p, share + (1 if i < rem else 0)) for i, p in enumerate(winners))
        st["shown"] = [p for p in players if p != "me"] if (len(players) > 1 and st["me_in"]) else []
        pay = st["paid"].get("me", 0)
        st["capped"] = False
        if pay - st["put"] > cards_cap_left():
            pay = st["put"] + cards_cap_left()
            st["capped"] = True
        if not st["me_in"]:
            res = "fold"
        elif winners == ["me"]:
            res = "win"
        elif "me" in winners:
            res = "split"
        else:
            res = "lose"
        theirs = [p for p in winners if p != "me"]
        face = dict(st.get("face") or {})
        if theirs:
            st["says"] = cards_style(theirs[0])["win"]
            st["speaker"] = theirs[0]
            for w in theirs:
                face[w] = "happy"
        elif st["opponents"]:
            w = (st["shown"] or st["opponents"])[0]
            st["says"] = cards_style(w)["lose"]
            st["speaker"] = w
            for x in st["opponents"]:
                face[x] = cards_style(x)["sore"]
        st["face"] = face
        if res == "fold":
            st["line"] = "%s take%s the pot." % (cards_pk_names(theirs), "s" if len(theirs) == 1 else "")
        elif len(players) == 1:
            st["line"] = "Everyone else is out."
        elif res in ("win", "split"):
            st["line"] = "%s." % cards_pk_name(st["mine"])
        else:
            st["line"] = "%s: %s." % (cards_pk_names(theirs), cards_pk_name(st["theirs"][theirs[0]]).lower())
        return cards_finish_hand(pay, res)

    ## What the screens draw ------------------------------------------------------

    def cards_side(who, expr=None):
        """P7. The path of someone's side portrait in that expression (their
        neutral one when it has no picture), or None when there is none."""
        for e in (expr, "neutral"):
            if e:
                path = "images/side/%s_%s.png" % (who, e)
                if renpy.loadable(path):
                    return path
        return None

    def cards_portrait(who, expr=None, zoom=1.0):
        """P7. Someone's side portrait as a displayable (a face chip when
        they have none). Build it in the line that uses it (R10)."""
        path = cards_side(who, expr)
        if path is None:
            return face_chip(who, int(160 * zoom))
        return Transform(path, zoom=zoom)

    def cards_back(w=120):
        """P7. A face-down card, w wide: gui/card_back.png, or a flat panel
        until that file exists."""
        h = int(w * 1.4)
        if renpy.loadable(CARDS_BACK):
            return Transform(CARDS_BACK, xysize=(w, h))
        return Fixed(Frame("gui/panel_solid.png", 4, 4),
                     Solid(gui.violet_deep, xysize=(max(2, w - 12), max(2, h - 12)), xalign=0.5, yalign=0.5),
                     xysize=(w, h))

    def cards_face_of(who):
        """P7. The expression someone at the table wears now."""
        st = store.cards_state or {}
        return (st.get("face") or {}).get(who) or cards_style(who)["rest"]

    def cards_default_stake():
        """P7. The stake the table opens on: the smallest."""
        return CARDS_STAKES[0]

    def cards_game_note(g, stake, n_people):
        """P7. The line under a game's button: why it can't be played, or
        what it is."""
        if n_people < int(g.get("min_people", 1)):
            return "Needs %d at the table." % int(g.get("min_people", 1))
        why = cards_can_deal(g["id"], stake)
        return why or CARDS_BLURB.get(g["id"], "")

    def cards_game_open(g, stake, n_people):
        """P7. bool: the game's button can be pressed at this stake."""
        return bool(n_people >= int(g.get("min_people", 1)) and renpy.has_label("mg_" + g["id"])
                    and not cards_can_deal(g["id"], stake))

    def cards_seat_x(n):
        """P7. The x centres of n opponents' seats at the poker table."""
        return {1: (960,), 2: (640, 1280), 3: (340, 960, 1580)}.get(n, (960,))

    def cards_marked():
        """P7. The indexes of my cards marked to throw away."""
        marks = (store.cards_state or {}).get("marks") or {}
        return tuple(i for i in range(5) if marks.get(i))

    def cards_validate():
        """P7, a registered validator. Every roster person has a complete
        CARDS_STYLE row with real expressions; the stakes rise; each of
        this file's games has its label."""
        out = []
        for w in ROSTER_ORDER:
            row = CARDS_STYLE.get(w)
            if not row:
                out.append("CARDS_STYLE has no row for %r" % w)
                continue
            for k in ("tight", "bluff", "tell", "win", "lose", "stop", "rest", "sore"):
                if k not in row:
                    out.append("CARDS_STYLE[%r] has no %r" % (w, k))
            for k in ("tell", "rest", "sore"):
                if k in row and row[k] not in ("neutral", "happy", "serious", "angry", "surprised", "sad"):
                    out.append("CARDS_STYLE[%r][%r] = %r is not an expression" % (w, k, row[k]))
            if row.get("shows") not in (None, "bluff", "bet", "strong", "weak"):
                out.append("CARDS_STYLE[%r]: shows=%r" % (w, row.get("shows")))
        for w in CARDS_STYLE:
            if w not in CAST:
                out.append("CARDS_STYLE: %r is not in CAST" % w)
        if list(CARDS_STAKES) != sorted(set(CARDS_STAKES)) or CARDS_STAKES[0] <= 0:
            out.append("CARDS_STAKES must rise from above zero")
        for g in CARDS_GAMES:
            if not renpy.has_label("mg_" + g):
                out.append("the card table has no label mg_%s" % g)
        return out


init python:

    register_minigame("blackjack", "Blackjack", "cards_play")
    register_minigame("poker", "Five-card draw", "cards_play")

    register_place_action("cards_play", "Play cards", "Blackjack or poker, for yen. Five hands a sitting.",
                          cost=1, locs=("dorm_common",), when="cards_ok", order=40)

    register_validator(cards_validate)


style cards_face is frame:
    background Solid(gui.cards_paper)
    padding (0, 0)

style cards_rank is text:
    font gui.display_heavy_font
    size 44

style cards_suit is text:
    font CARDS_SUIT_FONT
    size 56

style cards_title is text:
    font gui.display_font
    color gui.paper
    size 34

style cards_money is text:
    font gui.body_medium_font
    color gui.gold
    size 28

style cards_total is text:
    font gui.display_font
    color gui.paper
    size 40

style cards_says is text:
    color gui.paper
    size 26

style cards_line is text:
    color gui.dim
    size 22

style cards_result is text:
    font gui.body_medium_font
    color gui.gold
    size 26

style cards_btn is jjk_button:
    xfill False
    xsize 220
    padding (20, 14)

style cards_btn_text is jjk_button_text:
    xalign 0.5
    text_align 0.5

style cards_chip is cards_btn:
    xsize 170
    selected_background Frame("gui/panel_gold.png", 4, 4)

style cards_chip_text is cards_btn_text:
    selected_color gui.gold

style cards_game is button:
    background Frame("gui/panel_dark.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (18, 14)

style cards_plain is button:
    background None
    padding (0, 0)


## One card, w wide: its face (the rank, and the suit from DejaVu Sans, in the
## suit's colour), or its back.
screen cards_card(c, up=True, w=120):
    if up and c is not None:
        frame:
            style "cards_face"
            xysize (w, int(w * 1.4))
            text CARDS_RANKS[c % 13]:
                style "cards_rank"
                size int(44 * w / 120.0)
                color cards_color(c)
                xpos int(w * 0.09)
                ypos int(w * 0.02)
            text CARDS_SUITS[c // 13]:
                style "cards_suit"
                size int(56 * w / 120.0)
                color cards_color(c)
                xalign 0.5
                yalign 0.8
    else:
        add cards_back(w)


## The table (4.12): who is here, the games, the stakes. Returns
## ("play", game, stake) or ("close",).
screen cards_table():

    tag sandbox

    default cards_pick = cards_default_stake()

    $ _cards_opp = (cards_sit or {}).get("opponents") or cards_opponents()
    $ _cards_games = mg_games()
    $ _cards_gw = (832 - 20 * max(0, len(_cards_games) - 1)) // max(1, len(_cards_games))

    add graded_bg("dorm_common")
    add Solid(gui.ink) alpha 0.6

    key "game_menu" action Return(("close",))

    if smoke_autoplay:
        timer 0.05 action Return(cards_auto("table"))

    frame:
        style "jjk_panel"
        xpos 510
        ypos 280
        xysize (900, 520)

        fixed:
            hbox:
                spacing 16
                use seal("賭", 44)
                vbox:
                    spacing 0
                    text "The card table" style "cards_title"
                    text cards_tally_line() style "cards_line" substitute False
            vbox:
                xalign 1.0
                spacing 2
                text "MY YEN" style "jjk_label" xalign 1.0 color gui.gold
                text cards_yen(yen) style "cards_money" xalign 1.0 substitute False

            hbox:
                ypos 96
                spacing 22
                for _cards_w in _cards_opp:
                    hbox:
                        spacing 10
                        add face_chip(_cards_w, 56) yalign 0.5
                        text cards_short(_cards_w) style "jjk_value" size 22 yalign 0.5 substitute False

            hbox:
                ypos 172
                spacing 20
                for _cards_g in _cards_games:
                    button:
                        id "cards_game_" + _cards_g["id"]
                        style "cards_game"
                        xysize (_cards_gw, 132)
                        sensitive cards_game_open(_cards_g, cards_pick, len(_cards_opp))
                        action Return(("play", _cards_g["id"], cards_pick))
                        tooltip ("%s\n%s" % (_cards_g["name"], CARDS_BLURB.get(_cards_g["id"], "")), "cards_game_" + _cards_g["id"])
                        hbox:
                            spacing 16
                            yalign 0.5
                            add icon(_cards_g["icon"], 64) yalign 0.5
                            vbox:
                                spacing 4
                                yalign 0.5
                                text _cards_g["name"] font gui.display_font size 28 color gui.paper substitute False
                                text cards_game_note(_cards_g, cards_pick, len(_cards_opp)):
                                    style "cards_line"
                                    size 18
                                    substitute False
                                    xmaximum _cards_gw - 120

            hbox:
                ypos 336
                spacing 16
                text "STAKE" style "jjk_label" yalign 0.5 color gui.gold
                for _cards_s in CARDS_STAKES:
                    textbutton cards_yen(_cards_s):
                        id "cards_stake_%d" % _cards_s
                        style "cards_chip"
                        sensitive (yen >= _cards_s)
                        selected (cards_pick == _cards_s)
                        action SetScreenVariable("cards_pick", _cards_s)
                        tooltip ("%s a hand\n%s" % (cards_yen(_cards_s), ("I can cover it." if yen >= _cards_s else "More than I hold.")), "cards_stake_%d" % _cards_s)

            textbutton "Leave":
                id "cards_leave"
                style "cards_btn"
                xalign 1.0
                yalign 1.0
                action Return(("close",))
                tooltip ("Leave\nGet up from the table.", "cards_leave")


## Blackjack (4.12): the dealer at the left, the table at the right. Returns
## ("hit",), ("stand",), ("double",), ("deal",) or ("leave",).
screen cards_blackjack():

    tag sandbox

    $ _cards_st = cards_state or {}
    $ _cards_who = cards_dealer()
    $ _cards_stage = _cards_st.get("stage")
    $ _cards_dl = _cards_st.get("dealer") or []
    $ _cards_my = _cards_st.get("mine") or []
    $ _cards_why = cards_can_deal("blackjack", _cards_st.get("stake", 0))

    add graded_bg("dorm_common")
    add Solid(gui.ink) alpha 0.6

    if smoke_autoplay:
        timer 0.05 action Return(cards_auto("blackjack"))

    if _cards_who:
        add cards_portrait(_cards_who, cards_face_of(_cards_who), 1.8):
            xcenter 480
            ypos 300
        vbox:
            xcenter 480
            ypos 670
            spacing 2
            text "DEALING" style "jjk_label" xalign 0.5 color gui.gold
            text cards_short(_cards_who) style "cards_title" xalign 0.5 substitute False

    frame:
        background Frame("gui/panel.png", 4, 4)
        padding (0, 0)
        xpos 760
        ypos 140
        xysize (1080, 800)
        add Solid(gui.cards_felt) alpha 0.55

    text "BLACKJACK" style "jjk_label" color gui.gold xpos 760 ypos 62
    text (u"Stake %s · %s" % (cards_yen(_cards_st.get("stake", 0)), cards_tally_line())):
        style "cards_line"
        substitute False
        xpos 760
        ypos 90
    vbox:
        xanchor 1.0
        xpos 1840
        ypos 58
        spacing 2
        text "MY YEN" style "jjk_label" xalign 1.0 color gui.gold
        text cards_yen(yen) style "cards_money" xalign 1.0 substitute False

    ## The dealer's hand, y 200.
    hbox:
        xpos 800
        ypos 200
        spacing 16
        for _cards_i, _cards_c in enumerate(_cards_dl):
            use cards_card(_cards_c, up=(_cards_i == 0 or not _cards_st.get("hide")))
    if _cards_dl:
        vbox:
            xpos 1640
            ypos 232
            text "DEALER" style "jjk_label"
            text (str(cards_total(_cards_dl)) if not _cards_st.get("hide") else str(cards_total(_cards_dl[:1])) + " + ?") style "cards_total" substitute False

    ## The dealer's line, y 420.
    if _cards_st.get("says") and _cards_who:
        text (u"%s: “%s”" % (cards_short(_cards_who), _cards_st["says"])):
            style "cards_says"
            substitute False
            xpos 800
            ypos 420
            xmaximum 1000

    ## My hand, y 520.
    hbox:
        xpos 800
        ypos 520
        spacing 16
        for _cards_c in _cards_my:
            use cards_card(_cards_c)
    if _cards_my:
        vbox:
            xpos 1640
            ypos 552
            text "MINE" style "jjk_label"
            text str(cards_total(_cards_my)) style "cards_total" substitute False

    if _cards_stage == "done":
        vbox:
            xpos 800
            ypos 716
            spacing 4
            text cards_result_line() style "cards_result" substitute False
            if _cards_why:
                text _cards_why style "cards_line" substitute False

    hbox:
        xpos 800
        ypos 840
        spacing 18
        if _cards_stage == "play":
            textbutton "Hit":
                id "cards_hit"
                style "cards_btn"
                action Return(("hit",))
                tooltip ("Hit\nOne more card.", "cards_hit")
            textbutton "Stand":
                id "cards_stand"
                style "cards_btn"
                action Return(("stand",))
                tooltip ("Stand\nThe dealer draws to seventeen.", "cards_stand")
            textbutton "Double":
                id "cards_double"
                style "cards_btn"
                sensitive cards_bj_can_double()
                action Return(("double",))
                tooltip ("Double\nA second stake, one card, and I stand.", "cards_double")
        else:
            textbutton "Deal":
                id "cards_deal"
                style "cards_btn"
                sensitive (not _cards_why)
                action Return(("deal",))
                tooltip ("Deal\nAnother hand at %s." % cards_yen(_cards_st.get("stake", 0)), "cards_deal")
        textbutton "Leave":
            id "cards_leave"
            style "cards_btn"
            action Return(("leave",))
            tooltip (("Leave\nMy stake stays on the table." if _cards_stage == "play" else "Leave\nBack to the table."), "cards_leave")


## Five-card draw (4.12): the opponents along the top, each with the face
## their style gives away; the pot; my five cards. Returns ("bet",),
## ("check",), ("fold",), ("draw", (i, ...)), ("read", who), ("deal",) or
## ("leave",).
screen cards_poker():

    tag sandbox

    default cards_picking = False

    $ _cards_st = cards_state or {}
    $ _cards_stage = _cards_st.get("stage")
    $ _cards_opp = _cards_st.get("opponents") or []
    $ _cards_live = _cards_st.get("live") or []
    $ _cards_my = _cards_st.get("mine") or []
    $ _cards_marks = _cards_st.get("marks") or {}
    $ _cards_out = cards_marked()
    $ _cards_shown = _cards_st.get("shown") or []
    $ _cards_xs = cards_seat_x(len(_cards_opp))
    $ _cards_why = cards_can_deal("poker", _cards_st.get("stake", 0))
    $ _cards_can_read = cards_pk_can_read()

    add graded_bg("dorm_common")
    add Solid(gui.ink) alpha 0.6

    if smoke_autoplay:
        timer 0.05 action Return(cards_auto("poker"))

    frame:
        background Frame("gui/panel.png", 4, 4)
        padding (0, 0)
        xpos 40
        ypos 380
        xysize (1840, 560)
        add Solid(gui.cards_felt) alpha 0.55

    text "FIVE-CARD DRAW" style "jjk_label" color gui.gold xpos 60 ypos 36
    text (u"Stake %s · %s" % (cards_yen(_cards_st.get("stake", 0)), cards_tally_line())):
        style "cards_line"
        substitute False
        xpos 60
        ypos 64
    vbox:
        xanchor 1.0
        xpos 1860
        ypos 32
        spacing 2
        text "MY YEN" style "jjk_label" xalign 1.0 color gui.gold
        text cards_yen(yen) style "cards_money" xalign 1.0 substitute False

    ## The opponents, along y 180.
    for _cards_i, _cards_w in enumerate(_cards_opp):
        $ _cards_in = _cards_w in _cards_live
        fixed:
            xpos _cards_xs[_cards_i] - 290
            ypos 120
            xysize (580, 250)
            add cards_portrait(_cards_w, cards_face_of(_cards_w), 0.95):
                alpha (1.0 if (_cards_in or _cards_stage == "done") else 0.4)
            vbox:
                xpos 330
                ypos 20
                spacing 4
                text cards_short(_cards_w) font gui.display_font size 28 color gui.paper substitute False
                if _cards_stage == "done" and _cards_w in _cards_shown:
                    text cards_pk_name(_cards_st["theirs"][_cards_w]) style "cards_line" size 18 color gui.gold substitute False
                elif not _cards_in:
                    text "Folded" style "cards_line" size 18 color gui.seal
                elif _cards_w in (_cards_st.get("drew") or {}):
                    text ("Took %d" % _cards_st["drew"][_cards_w]) style "cards_line" size 18 substitute False
                else:
                    text "In" style "cards_line" size 18
                hbox:
                    spacing 4
                    for _cards_c in (_cards_st.get("theirs") or {}).get(_cards_w, []):
                        use cards_card(_cards_c, up=(_cards_stage == "done" and _cards_w in _cards_shown), w=44)
                if _cards_st.get("read") == _cards_w and _cards_stage != "done":
                    hbox:
                        spacing 4
                        for _cards_k in range(5):
                            add Solid((gui.gold if _cards_k < cards_pk_steps(_cards_st["theirs"][_cards_w]) else gui.mute), xysize=(40, 10))
                elif cards_picking and _cards_can_read and _cards_in:
                    textbutton "Read":
                        id "cards_read_" + _cards_w
                        style "cards_btn"
                        xsize 120
                        padding (10, 4)
                        text_size 18
                        action Return(("read", _cards_w))
                        tooltip ("Read %s\nHow good the hand is, in five steps." % cards_short(_cards_w), "cards_read_" + _cards_w)

    ## The pot, y 400.
    vbox:
        xalign 0.5
        ypos 400
        spacing 4
        text (u"POT  %s" % cards_yen(_cards_st.get("pot", 0))) style "cards_total" xalign 0.5 substitute False
        if _cards_stage == "done" and _cards_st.get("says") and _cards_st.get("speaker"):
            text (u"%s: “%s”" % (cards_short(_cards_st["speaker"]), _cards_st["says"])):
                style "cards_says"
                size 24
                substitute False
                xalign 0.5
        text (_cards_st.get("line") or "") style "cards_line" xalign 0.5 substitute False

    ## My five cards, y 560. In the draw a click marks one to throw away.
    for _cards_i, _cards_c in enumerate(_cards_my):
        button:
            id "cards_my_%d" % _cards_i
            style "cards_plain"
            xpos 612 + 144 * _cards_i
            ypos (536 if _cards_marks.get(_cards_i) else 560)
            xysize (120, 168)
            sensitive (_cards_stage == "draw")
            action If(_cards_marks.get(_cards_i) or len(_cards_out) < 3, ToggleDict(_cards_marks, _cards_i), NullAction())
            tooltip (("Keep it" if _cards_marks.get(_cards_i) else "Throw it away"), "cards_my_%d" % _cards_i)
            fixed:
                use cards_card(_cards_c)
                if _cards_marks.get(_cards_i):
                    add Solid(gui.ink) alpha 0.35
    if _cards_my:
        vbox:
            xalign 0.5
            ypos 742
            spacing 2
            text cards_pk_name(_cards_my) style "cards_says" size 24 xalign 0.5 substitute False
            if _cards_stage == "draw":
                text "Click up to three cards to throw away." style "cards_line" size 18 xalign 0.5
            elif _cards_stage == "done":
                text cards_result_line() style "cards_result" size 22 xalign 0.5 substitute False
                if _cards_why:
                    text _cards_why style "cards_line" size 18 xalign 0.5 substitute False

    ## The read: once a hand, at Insight 20.
    if _cards_can_read:
        fixed:
            xpos 1700
            ypos 560
            xysize (84, 84)
            use icon_btn("look", (Return(("read", _cards_live[0])) if len(_cards_live) == 1 else ToggleScreenVariable("cards_picking")),
                         tip="Read someone\nOnce a hand: how good their cards are.", size=60, w=84,
                         selected=cards_picking, wid="cards_look", words="never")

    hbox:
        xalign 0.5
        ypos 850
        spacing 18
        if _cards_stage in ("bet1", "bet2"):
            textbutton "Check":
                id "cards_check"
                style "cards_btn"
                action Return(("check",))
                tooltip ("Check\nPut nothing in and see what they do.", "cards_check")
            textbutton (u"Bet %s" % cards_yen(_cards_st.get("stake", 0))):
                id "cards_bet"
                style "cards_btn"
                sensitive (yen >= _cards_st.get("stake", 0))
                action Return(("bet",))
                tooltip ("Bet\nOne stake. They call or fold.", "cards_bet")
            textbutton "Fold":
                id "cards_fold"
                style "cards_btn"
                action Return(("fold",))
                tooltip ("Fold\nWhat I've put in stays in.", "cards_fold")
        elif _cards_stage in ("call1", "call2"):
            textbutton (u"Call %s" % cards_yen(_cards_st.get("owed", 0))):
                id "cards_bet"
                style "cards_btn"
                sensitive (yen >= _cards_st.get("owed", 0))
                action Return(("bet",))
                tooltip ("Call\nMatch the bet and stay in.", "cards_bet")
            textbutton "Fold":
                id "cards_fold"
                style "cards_btn"
                action Return(("fold",))
                tooltip ("Fold\nWhat I've put in stays in.", "cards_fold")
        elif _cards_stage == "draw":
            textbutton ("Stand pat" if not _cards_out else "Draw %d" % len(_cards_out)):
                id "cards_draw"
                style "cards_btn"
                action Return(("draw", _cards_out))
                tooltip ("Draw\nNew cards for the ones I marked.", "cards_draw")
        else:
            textbutton "Deal":
                id "cards_deal"
                style "cards_btn"
                sensitive (not _cards_why)
                action Return(("deal",))
                tooltip ("Deal\nAnother hand at %s." % cards_yen(_cards_st.get("stake", 0)), "cards_deal")
        textbutton "Leave":
            id "cards_leave"
            style "cards_btn"
            action Return(("leave",))
            tooltip (("Leave\nBack to the table." if _cards_stage in ("done", "idle") else "Leave\nI fold this hand."), "cards_leave")


## The place action (4.12): the table, then a game, until the sitting is over
## or I get up. One period if a hand was played.
label sb_do_cards_play:
    if not cards_ok():
        return
    if not night_allows("cards_play", 1):
        "Too late. Bed."
        return
    $ _cards_opp = cards_opponents()
    $ cards_sit_down(_cards_opp)
    $ _cards_go = True
    while _cards_go:
        call screen cards_table
        $ _cards_r = _return
        if not isinstance(_cards_r, tuple) or len(_cards_r) < 3 or _cards_r[0] != "play":
            $ _cards_go = False
        elif not renpy.has_label("mg_" + _cards_r[1]) or cards_can_deal(_cards_r[1], _cards_r[2]):
            $ renpy.say(None, cards_can_deal(_cards_r[1], _cards_r[2]) or "Nobody here knows that one.")
        else:
            call expression "mg_" + _cards_r[1] pass (_cards_opp, _cards_r[2])
            $ cards_sit_note(_cards_r[1])
            if cards_sit_over():
                $ renpy.say(None, cards_sit_over())
                $ _cards_go = False
    $ cards_get_up()
    return


## Blackjack (4.12). The game's own label: it plays until I leave, and sets
## mg_result before it returns (cards_end). Rollback is blocked after every
## deal, every draw and every settlement.
label mg_blackjack(opponents, stake=0):
    $ cards_new("blackjack", opponents, stake)
    if cards_can_deal("blackjack", stake):
        $ cards_end()
        return
    $ cards_bj_deal()
    $ cards_block()
    while cards_state:
        call screen cards_blackjack
        $ _cards_b = _return
        if not isinstance(_cards_b, tuple) or not _cards_b or _cards_b[0] == "leave":
            $ cards_forfeit()
            $ cards_block()
            $ cards_end()
        elif _cards_b[0] == "hit":
            $ cards_bj_hit()
            $ cards_block()
        elif _cards_b[0] == "stand":
            $ cards_bj_stand()
            $ cards_block()
        elif _cards_b[0] == "double":
            $ cards_bj_double()
            $ cards_block()
        elif _cards_b[0] == "deal":
            $ cards_bj_deal()
            $ cards_block()
    return


## Five-card draw (4.12), as above.
label mg_poker(opponents, stake=0):
    $ cards_new("poker", opponents, stake)
    if cards_can_deal("poker", stake):
        $ cards_end()
        return
    $ cards_pk_deal()
    $ cards_block()
    while cards_state:
        call screen cards_poker
        $ _cards_p = _return
        if not isinstance(_cards_p, tuple) or not _cards_p or _cards_p[0] == "leave":
            $ cards_forfeit()
            $ cards_block()
            $ cards_end()
        elif _cards_p[0] == "bet":
            $ cards_pk_bet()
            $ cards_block()
        elif _cards_p[0] == "check":
            $ cards_pk_check()
            $ cards_block()
        elif _cards_p[0] == "fold":
            $ cards_pk_fold()
            $ cards_block()
        elif _cards_p[0] == "draw":
            $ cards_pk_draw(_cards_p[1] if len(_cards_p) > 1 else ())
            $ cards_block()
        elif _cards_p[0] == "read":
            $ cards_pk_read(_cards_p[1] if len(_cards_p) > 1 else None)
        elif _cards_p[0] == "deal":
            $ cards_pk_deal()
            $ cards_block()
    return


## Card state (3.3).
default cards_state = {}         # the sitting in progress (deck as a list of ints); {} otherwise
default cards_won_day = 0        # the day cards_won counts for
default cards_won = 0            # yen won at cards that day
default cards_sit = {}           # the sitting's tally (hands, net, opponents) over both games; {} otherwise
