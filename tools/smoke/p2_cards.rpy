## tools/smoke/p2_cards.rpy -- P7's harness: the card table, blackjack and
## five-card draw (docs/PHASE2_DESIGN.md, 7 · P7; 4.12; D32).
##
##   tools/smoke.sh tools/smoke/p2_cards.rpy
##
## Every acceptance bullet of P7 is a named check below, in the plan's order:
##   A  cards_ok(): an empty common room, less than ¥100, the place action
##   B  blackjack: the hand-total function; 2,000 hands through the game's own
##      functions; never staking more than I hold; a sitting stops at five
##      hands and at ¥3,000 down; cards_state and mg_result after leaving
##   C  the day's winnings never pass BOARD_YEN["g4"][1]
##   D  poker: the ranker on 20 fixed hands; full hands under autoplay; the
##      eleven styles; the read
##   E  Bond +1 once a day; one period only if a hand was played;
##      cards_records()
##   F  rollback is blocked after every deal, draw, read and settlement: the
##      real labels are played with cards_block() wrapped, the blocks are
##      matched to the moves made, and a rollback is asked for from inside
##      the next screen after each one (nothing may change)
##   G  at Night the table is closed
##   H  zz_worst of the three screens: no toast drawn; the names
##   I  the saved state pickles; the stand-in pictures
## A line that waits for another package is a NOTE that says so (7.3).
##
## State is built through cards_new() and the game's own functions (R5), and
## cleared through them too (zz_c_reset: cards_sit_down, cards_get_up); the
## harness never assigns cards_state or cards_sit.
## Where a hand must come out a given way, cards_draw() (the one function a
## card comes from) is wrapped to hand out scripted cards; nothing else of
## the game is replaced. The labels are driven through cards_auto(), the
## game's own autoplay answer, wrapped with a policy that is a pure function
## of the state (a screen may evaluate it more than once).
##
## Screenshots: worst_cards_table.png, worst_cards_blackjack.png,
## worst_cards_poker.png (R6), cards_blackjack_done.png, cards_poker_draw.png,
## cards_poker_read.png, cards_poker_showdown.png, cards_poker_one.png,
## cards_standin.png, cards_table_poor.png, cards_poker_hover_card.png (a
## card hovered in the draw: no label), cards_blackjack_long.png (nine cards).
##
## A run takes about 35 seconds.

init 999 python:
    import builtins
    import pickle

    class ZZCardsState(builtins.object):
        """Harness state, outside the store."""

        def __init__(self):
            self.cards = builtins.list()        # scripted cards, handed out before the deck's
            self.blocks = builtins.list()       # what cards_block() saw, each call
            self.policy = None                  # (where, state) -> a screen's answer
            self.said = builtins.list()
            self.shows = builtins.list()        # the state after every poker showdown
            self.patched = builtins.dict()
            self.rb_on = False                  # ask for a rollback at the screen after each block
            self.rb_arm = builtins.list()       # what the next screen's rollback follows
            self.rb_wait = None                 # (what, the state when the rollback was asked for)
            self.rb_log = builtins.list()       # (what, the state came back the same)
            self.rb_read = False                # the read's own rollback has been asked for
            self.reads = builtins.list()        # what cards_pk_read returned, each call
            self.picks = builtins.list()        # the stake the table opened on, each visit

    zz_c = ZZCardsState()

    zz_c_real_say = renpy.exports.say

    def zz_c_say(who, what, *args, **kwargs):
        zz_c.said.append(what)
        return zz_c_real_say(who, what, *args, **kwargs)

    renpy.exports.say = zz_c_say

    def zz_c_patch(name, fn):
        if name not in zz_c.patched:
            zz_c.patched[name] = getattr(store, name)
        setattr(store, name, fn)

    def zz_c_unpatch(*names):
        for n in (names or builtins.list(zz_c.patched)):
            if n in zz_c.patched:
                setattr(store, n, zz_c.patched.pop(n))

    ZZ_C_RANKS = "23456789TJQKA"
    ZZ_C_SUITS = "SHDC"

    def zz_cd(text):
        """Cards from "AS KH 2D": the game's ints (rank = c % 13, suit = c // 13)."""
        return [ZZ_C_SUITS.index(t[1]) * 13 + ZZ_C_RANKS.index(t[0]) for t in text.split()]

    def zz_c_draw(st):
        """cards_draw, handing out the scripted cards first."""
        if zz_c.cards:
            c = zz_c.cards.pop(0)
            if c in st["deck"]:
                st["deck"].remove(c)
            return c
        return zz_c.patched["cards_draw"](st)

    def zz_c_block():
        """cards_block, noting what the rollback log says right after it."""
        zz_c.patched["cards_block"]()
        st = store.cards_state or {}
        zz_c.blocks.append(builtins.dict(game=st.get("game"), stage=st.get("stage"), hands=st.get("hands"),
                                         result=st.get("result"), read=bool(st.get("read_used")),
                                         can=bool(renpy.can_rollback())))
        if zz_c.rb_on:
            zz_c.rb_arm.append("%s %s" % (st.get("stage"), st.get("hands")))
        return None

    def zz_c_read(who):
        """cards_pk_read, noted; the first one arms a rollback at the next
        screen whether or not the label blocks after it."""
        r = zz_c.patched["cards_pk_read"](who)
        zz_c.reads.append(r)
        if zz_c.rb_on and not zz_c.rb_read:
            zz_c.rb_read = True
            zz_c.rb_arm.append("read")
        return r

    def zz_c_snap():
        return pickle.dumps((store.cards_state, store.cards_sit, store.yen, store.cards_won, store.period), 2)

    def zz_c_rollback():
        """Called while a cards screen is being drawn (from cards_auto). After
        a block or a read: note the state and ask for a rollback, as the mouse
        wheel would. The next time round: has anything changed? The notes are
        kept outside the store, so the rollback can't take them back."""
        if not zz_c.rb_on or renpy.predicting():
            return
        if zz_c.rb_wait is not None:
            what, snap = zz_c.rb_wait
            zz_c.rb_wait = None
            zz_c.rb_log.append((what, snap == zz_c_snap()))
        if zz_c.rb_arm and len(zz_c.rb_log) < 60:
            what = " + ".join(zz_c.rb_arm)
            del zz_c.rb_arm[:]
            zz_c.rb_wait = (what, zz_c_snap())
            if renpy.can_rollback():
                ## It will go: this screen is half built, so clear the ui
                ## stack the rollback's exception would leave behind.
                renpy.ui.reset()
            renpy.rollback()
            ## Still here: there was nothing to roll back to.
            zz_c.rb_wait = None
            zz_c.rb_log.append((what, True))

    def zz_c_auto(where):
        zz_c_rollback()
        if zz_c.policy is not None:
            r = zz_c.policy(where, store.cards_state or {})
            if r is not None:
                return r
        return zz_c.patched["cards_auto"](where)

    def zz_c_showdown():
        r = zz_c.patched["cards_pk_showdown"]()
        st = store.cards_state
        zz_c.shows.append(builtins.dict(pot=st["pot"], paid=builtins.dict(st["paid"]), last=st["last"],
                                        result=st["result"], me_in=st["me_in"], live=builtins.list(st["live"])))
        return r

    def zz_c_wrap():
        """Wrap the game's seams for the label-driven sections."""
        zz_c_patch("cards_pk_read", zz_c_read)
        zz_c_patch("cards_draw", zz_c_draw)
        zz_c_patch("cards_block", zz_c_block)
        zz_c_patch("cards_auto", zz_c_auto)
        zz_c_patch("cards_pk_showdown", zz_c_showdown)

    def zz_c_btn(screen, wid):
        """The Button with `id wid` on a shown screen. For a textbutton
        renpy.get_widget gives the Text inside it; this gives the button
        around it, which is what carries the action and the tooltip."""
        w = renpy.get_widget(screen, wid)
        if w is None or isinstance(w, renpy.display.behavior.Button):
            return w
        found = []
        def visit(d):
            if isinstance(d, renpy.display.behavior.Button) and w in d.visit():
                found.append(d)
        renpy.get_screen(screen).visit_all(visit)
        return found[0] if found else None

    def zz_c_reset():
        """Empties cards_state and cards_sit the game's own way: a sitting
        with no hand played, got up from (no period, no Bond)."""
        cards_sit_down([])
        cards_get_up()

    def zz_c_base(yen=5000, who=("yuji",), period="Afternoon", day=3):
        """A day at the table: these people in the common room, nobody else."""
        zz_c_reset()
        store.actions_today = builtins.set()
        fixture(day=day, period=period, here="dorm_common", yen=yen, cards_won=0, cards_won_day=0,
                companion=None, explore_mode=False, insight=30)
        for w in ROSTER_ORDER:
            recruit(w)
        for w in builtins.list(who_is_here("dorm_common")):
            pin(w, "courtyard")
        for w in who:
            pin(w, "dorm_common")
        toast_clear()
        del zz_c.cards[:]
        del zz_c.blocks[:]
        del zz_c.said[:]
        del zz_c.shows[:]
        del zz_c.rb_arm[:]
        del zz_c.rb_log[:]
        del zz_c.reads[:]
        del zz_c.picks[:]
        zz_c.rb_on = False
        zz_c.rb_wait = None
        zz_c.rb_read = False
        zz_c.policy = None

    def zz_c_tell(who, s, plan, n=400):
        """How often, in n tries, someone's face shows their tell."""
        return builtins.sum(1 for i in range(n) if cards_pk_face(who, s, plan) == CARDS_STYLE[who]["tell"]) / float(n)

    def zz_c_plain(v):
        """True when v holds only the types a save may hold."""
        if v is None or isinstance(v, (bool, int, float, str)):
            return True
        if isinstance(v, (builtins.list, builtins.tuple, builtins.set, builtins.frozenset)):
            return all(zz_c_plain(x) for x in v)
        if isinstance(v, builtins.dict):
            return all(zz_c_plain(k) and zz_c_plain(x) for k, x in v.items())
        return False

    ## Policies: pure functions of (where, state).

    def zz_c_keep_dealing(where, st):
        """One game at the smallest stake; stand or check; deal while a hand can be dealt."""
        if where == "table":
            return None
        if st.get("stage") == "done":
            return ("leave",) if cards_can_deal(st["game"], st["stake"]) else ("deal",)
        return None

    def zz_c_thousand(where, st):
        """As above, at ¥1,000 a hand."""
        if where == "table":
            return ("close",) if cards_tally()[0] else ("play", "blackjack", 1000)
        return zz_c_keep_dealing(where, st)

    def zz_c_five_hundred(where, st):
        """One blackjack hand at ¥500 (stand), back to the table, then away;
        notes the stake the table opens on at each visit."""
        if where == "table":
            if not renpy.predicting():
                zz_c.picks.append(cards_default_stake())
            return ("close",) if cards_tally()[0] else ("play", "blackjack", 500)
        return ("stand",) if st.get("stage") == "play" else ("leave",)

    def zz_c_close(where, st):
        return ("close",) if where == "table" else None

    def zz_c_every_move(where, st):
        """Blackjack: a hit, a stand, a double. Hand 1: hit, then stand;
        hand 2: double; then away."""
        if where == "table":
            return None
        if st.get("stage") == "play":
            if st["hands"] == 1:
                return ("hit",) if len(st["mine"]) == 2 else ("stand",)
            return ("double",)
        if st.get("stage") == "done":
            return ("deal",) if st["hands"] < 2 else ("leave",)
        return None

    def zz_c_poker_moves(where, st):
        """Poker: hand 1 a read, a check (and a call if someone bets), a draw
        of two, a bet; hand 2 a bet, a stand-pat draw, a fold; then away."""
        if where == "table":
            return ("close",) if cards_tally()[0] else ("play", "poker", 100)
        stage = st.get("stage")
        if stage == "bet1":
            if st["hands"] == 1 and cards_pk_can_read():
                return ("read", st["live"][0])
            return ("check",) if st["hands"] == 1 else ("bet",)
        if stage in ("call1", "call2"):
            return ("bet",)
        if stage == "draw":
            return ("draw", (0, 1)) if st["hands"] == 1 else ("draw", ())
        if stage == "bet2":
            return ("bet",) if st["hands"] == 1 else ("fold",)
        if stage == "done":
            return ("deal",) if st["hands"] < 2 else ("leave",)
        return None

    ## The harness's own hotspot on the card table (P6's is not in this
    ## worktree): an action hotspot for cards_play.
    register_hotspot("zz_c_table", "dorm_common", 900, 800, "cards_play", act="cards_play")

    ## Twenty hands, weakest first (D).
    ZZ_C_LADDER = [
        "7H 5D 4C 3S 2H", "KS JH 9D 5C 3S", "AS JH 9D 5C 3S", "AS KH 9D 5C 3S",
        "2S 2H AD KC QS", "9S 9H 4D 3C 2S", "9D 9C AH 3H 2C", "AS AH 4D 3C 2S",
        "3S 3H 2D 2C AS", "KS KH 2D 2C 3S", "KS KH QD QC 2S",
        "2S 2H 2D AC KS", "AS AH AD 3C 2S",
        "AS 2H 3D 4C 5S", "2S 3H 4D 5C 6S", "TS JH QD KC AS",
        "2H 4H 6H 8H TH", "2S 2H 2D 3C 3S", "3S 3H 3D 3C 2S", "AS 2S 3S 4S 5S",
    ]
    ZZ_C_LADDER_CATS = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 6, 7, 8]


label zz_smoke:

    $ settle(day=3)
    $ autoplay(False)

    ## =====================================================================
    ## A. cards_ok(), and the place action
    python:
        zz_c_base(yen=1000, who=())
        check(who_is_here("dorm_common") == [] and cards_ok() is False,
              "A: cards_ok() is False in an empty common room", who_is_here("dorm_common"))
        check("cards_play" not in [a[0] for a in place_actions("dorm_common")],
              "A: an empty common room offers no card table")
        zz_c_base(yen=1000, who=("yuji",))
        check(cards_ok() is True, "A: with Yuji in the common room and ¥1,000, cards_ok() is True")
        fixture(yen=99)
        check(cards_ok() is False, "A: cards_ok() is False with less than ¥100 (¥99)")
        fixture(yen=100)
        check(cards_ok() is True, "A: ¥100 is enough to sit down")
        _zz_row = [a for a in place_actions("dorm_common") if a[0] == "cards_play"]
        check(len(_zz_row) == 1 and _zz_row[0][3] == 1 and "cards_play" not in [a[0] for a in place_actions("dorm")],
              "A: the place action cards_play is offered in the common room only, at one period", _zz_row)
        check(icon_for("act", "cards_play") == "cards_play" and "cards_play" in ICONS and "look" in ICONS,
              "A: the icons the table uses (cards_play, look) are in ICONS")
        store.actions_today.add("cards:yuji")
        check(cards_ok() is False, "A: after a sitting with everyone present, cards_ok() is False for the day")
        pin("megumi", "dorm_common")
        check(cards_ok() is True, "A: someone I haven't played today walks in: the table is open again")
        fixture(explore_mode=True)
        check(cards_ok() is False and "cards_play" not in [a[0] for a in place_actions("dorm_common")],
              "A: explore mode has no card table")
        fixture(explore_mode=False)
        zz_c_base(yen=1000, who=("yuji", "megumi", "nobara", "shoko"))
        check(cards_opponents() == who_is_here("dorm_common")[:3] and len(cards_opponents()) == 3,
              "A: at most three opponents sit down", cards_opponents())
        for _zz_w in cards_opponents():
            store.actions_today.add("cards:" + _zz_w)
        check(cards_ok() is True and cards_opponents()[0] == "shoko" and len(cards_opponents()) == 3,
              "A: four present, three played today: the fourth gets a seat and the table is open", cards_opponents())
        store.actions_today.add("cards:shoko")
        check(cards_ok() is False and cards_opponents() == who_is_here("dorm_common")[:3],
              "A: all four played: the table is closed, and the seats are in roster order again", cards_opponents())
        store.actions_today = builtins.set()
        check([g["id"] for g in mg_games() if not g["id"].startswith("zz")] == ["blackjack", "poker"]
              and renpy.has_label("mg_blackjack") and renpy.has_label("mg_poker"),
              "A: blackjack, then poker, are registered and each has its label", mg_games())
        check(cards_validate() == [], "A: the table's own validator is clean", cards_validate())

    ## =====================================================================
    ## B. Blackjack
    python:
        _zz_cases = [("AS KH", 21), ("AS AH", 12), ("AS AH 9D", 21), ("AS 5H KD", 16), ("AS AH AD 8C", 21),
                     ("AS 9H AD", 21), ("AS AH AD AC", 14), ("AS 6H", 17), ("AS 6H TD", 17), ("AS 6H TD 5C", 22),
                     ("TS JH QD", 30), ("2S 3H", 5), ("AS AH KD QC", 22), ("9S AH AD", 21), ("KS QH AD", 21)]
        _zz_bad = [(t, n, cards_total(zz_cd(t))) for t, n in _zz_cases if cards_total(zz_cd(t)) != n]
        check(not _zz_bad, "B: the hand-total function is right for every ace case (%d hands)" % len(_zz_cases), _zz_bad)
        check(cards_natural(zz_cd("AS KH")) and not cards_natural(zz_cd("AS 5H 5D")) and not cards_natural(zz_cd("KS QH")),
              "B: a natural is twenty-one in two cards only")

        ## 2,000 hands, hitting below 17 and never doubling.
        zz_c_base(yen=100000, who=("yuji",))
        _zz_seen = builtins.dict()
        _zz_odd = builtins.list()
        _zz_res = builtins.dict()
        for _zz_i in range(2000):
            fixture(yen=100000, cards_won=0, cards_won_day=0)
            cards_new("blackjack", ["yuji"], 500)
            _zz_dealt = cards_bj_deal()
            while cards_state["stage"] == "play":
                if cards_total(cards_state["mine"]) < 17:
                    cards_bj_hit()
                else:
                    cards_bj_stand()
            _zz_d = yen - 100000
            _zz_seen[_zz_d] = _zz_seen.get(_zz_d, 0) + 1
            _zz_res[cards_state["result"]] = _zz_res.get(cards_state["result"], 0) + 1
            _zz_want = {"win": 500, "natural": 750, "push": 0, "lose": -500, "bust": -500}.get(cards_state["result"])
            if not _zz_dealt or _zz_d != _zz_want or _zz_d != cards_state["last"] or cards_today() != _zz_d:
                _zz_odd.append((cards_state["result"], _zz_d))
            _zz_me, _zz_dl = cards_total(cards_state["mine"]), cards_total(cards_state["dealer"])
            if cards_state["result"] in ("win", "lose", "push") and not (cards_natural(cards_state["dealer"])):
                if not (_zz_dl >= 17 and ((_zz_dl > 21 or _zz_me > _zz_dl) == (cards_state["result"] == "win"))):
                    _zz_odd.append(("dealer", cards_state["result"], _zz_me, _zz_dl))
            if len(builtins.set(cards_state["mine"] + cards_state["dealer"] + cards_state["deck"])) != 52:
                _zz_odd.append(("deck", len(cards_state["deck"])))
            cards_end()
        check(not _zz_odd and builtins.set(_zz_seen) <= {-500, 0, 500, 750} and builtins.set(_zz_seen) == {-500, 0, 500, 750},
              "B: 2,000 hands through the game's own functions settle at -stake, 0, +stake or +1.5 stake only",
              (_zz_seen, _zz_odd[:4]))
        note("B: the 2,000 hands", "yen change -> hands: %r; results: %r" % (builtins.sorted(_zz_seen.items()), builtins.sorted(_zz_res.items())))
        check(_zz_res.get("natural", 0) > 20 and _zz_res.get("push", 0) > 20 and _zz_res.get("bust", 0) > 100,
              "B: naturals, pushes and busts all occur in the 2,000 hands", _zz_res)

        ## 600 more with Double (two stakes, win or lose).
        _zz_seen2 = builtins.dict()
        _zz_odd = builtins.list()
        for _zz_i in range(600):
            fixture(yen=100000, cards_won=0, cards_won_day=0)
            cards_new("blackjack", ["megumi"], 500)
            cards_bj_deal()
            while cards_state["stage"] == "play":
                _zz_t = cards_total(cards_state["mine"])
                if cards_bj_can_double() and _zz_t in (9, 10, 11):
                    cards_bj_double()
                elif _zz_t < 17:
                    cards_bj_hit()
                else:
                    cards_bj_stand()
            _zz_d = yen - 100000
            _zz_seen2[_zz_d] = _zz_seen2.get(_zz_d, 0) + 1
            cards_end()
        check(builtins.set(_zz_seen2) <= {-1000, -500, 0, 500, 750, 1000} and _zz_seen2.get(1000, 0) > 0 and _zz_seen2.get(-1000, 0) > 0,
              "B: with Double a hand also settles at two stakes up or down, and at nothing else", _zz_seen2)
        note("B: Double", "the plan's list (±stake, +1.5 stake, 0) is without Double; a doubled hand is ±2 stakes: %r"
             % (builtins.sorted(_zz_seen2.items()),))

        ## I can't stake more than I hold.
        zz_c_patch("cards_draw", zz_c_draw)
        zz_c_base(yen=400, who=("yuji",))
        cards_new("blackjack", ["yuji"], 500)
        check(cards_can_deal("blackjack", 500) != "" and cards_bj_deal() is False and yen == 400 and cards_state["stage"] == "idle",
              "B: with ¥400 a ¥500 hand is not dealt and nothing is taken", (cards_can_deal("blackjack", 500), yen))
        cards_end()
        check(mg_result == builtins.dict(game="blackjack", outcome="quit", yen=0) and cards_state == {},
              "B: leaving without a hand: mg_result says quit, cards_state is empty", mg_result)
        zz_c_base(yen=700, who=("yuji",))
        cards_new("blackjack", ["yuji"], 500)
        zz_c.cards[:] = zz_cd("5S 6H TD 7C")
        cards_bj_deal()
        check(yen == 200 and cards_state["stage"] == "play" and cards_state["put"] == 500,
              "B: the stake leaves my yen when the hand is dealt", (yen, cards_state["stage"]))
        check(cards_bj_can_double() is False and cards_bj_double() is False and yen == 200 and cards_state["bet"] == 500,
              "B: Double is refused when I don't hold a second stake", (yen, cards_state["bet"]))
        fixture(yen=500)
        check(cards_bj_can_double() is True, "B: with a second stake in my pocket Double is open")
        zz_c.cards[:] = zz_cd("TS")
        cards_bj_double()
        check(cards_state["stage"] == "done" and cards_state["result"] == "win" and yen == 2000 and cards_state["last"] == 1000,
              "B: a doubled 21 against 17 pays two stakes", (cards_state["result"], yen))
        cards_end()
        for _zz_y in (0, 99, 100, 250, 499, 500, 999, 1000, 2999):
            for _zz_s in CARDS_STAKES:
                for _zz_g in ("blackjack", "poker"):
                    zz_c_base(yen=_zz_y, who=("yuji", "megumi"))
                    cards_new(_zz_g, ["yuji", "megumi"], _zz_s)
                    _zz_ok = cards_bj_deal() if _zz_g == "blackjack" else cards_pk_deal()
                    if _zz_ok:
                        while cards_state["stage"] != "done":
                            if _zz_g == "blackjack":
                                if not cards_bj_double():
                                    cards_bj_stand()
                            elif cards_state["stage"] == "draw":
                                cards_pk_draw(())
                            elif not cards_pk_bet():
                                cards_pk_fold()
                    if yen < 0 or (_zz_ok and _zz_y < _zz_s) or (not _zz_ok and _zz_y >= _zz_s * 3):
                        _zz_odd.append((_zz_g, _zz_y, _zz_s, _zz_ok, yen))
                    cards_end()
        check(not _zz_odd, "B: at every purse and stake, in both games, a hand I can't cover is not dealt and yen never goes below zero", _zz_odd[:4])

        ## The sitting's limits, through the functions.
        zz_c_base(yen=20000, who=("yuji",))
        cards_sit_down(["yuji"])
        cards_new("blackjack", ["yuji"], 1000)
        for _zz_i in range(3):
            zz_c.cards[:] = zz_cd("TS 6H TD 9C")
            cards_bj_deal()
            cards_bj_stand()
        check(cards_state["net"] == -3000 and cards_can_deal("blackjack", 100) != "" and "down" in cards_can_deal("blackjack", 100)
              and cards_bj_deal() is False and cards_state["hands"] == 3,
              "B: at ¥3,000 down no further hand is dealt", (cards_state["net"], cards_can_deal("blackjack", 100)))
        cards_end()
        check("3,000 down" in cards_sit_over() and mg_result["outcome"] == "lose" and mg_result["yen"] == -3000,
              "B: the sitting ends at ¥3,000 down, with its line", (cards_sit_over(), mg_result))
        cards_sit["net"] = -4000
        check("4,000 down" in cards_sit_over() and "3,000" not in cards_sit_over(),
              "B: the line that ends a losing sitting says what I am really down, not the limit", cards_sit_over())
        _zz_lim = CARDS_LIMIT["hands"]
        CARDS_LIMIT["hands"] = 4
        cards_sit["net"] = 0
        cards_sit["hands"] = 4
        check(cards_sit_over().startswith("Four hands. ") and cards_can_deal("blackjack", 100) == "Four hands. That's the sitting.",
              "B: the hand-limit lines are built from CARDS_LIMIT, not written out", (cards_sit_over(), cards_can_deal("blackjack", 100)))
        CARDS_LIMIT["hands"] = _zz_lim
        cards_sit["hands"] = _zz_lim
        check(cards_sit_over().startswith("Five hands. ") or _zz_lim != 5, "B: at the real limit the line reads 'Five hands.'", cards_sit_over())
        cards_sit["hands"] = 3
        cards_get_up()
        zz_c_unpatch()

    ## The sitting through the real labels: five hands, then up.
    python:
        zz_c_base(yen=5000, who=("yuji", "megumi"))
        zz_c_wrap()
        zz_c.policy = zz_c_keep_dealing
        zz_c.cards[:] = zz_cd("TS 8H TD 7C") * 5       # 18 against 17, five times: no natural ends a hand early
        _zz_b0 = (bonds.get("yuji", 0), bonds.get("megumi", 0))
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        zz_c_unpatch()
        _zz_hands = builtins.max([b["hands"] or 0 for b in zz_c.blocks] or [0])
        check(_zz_hands == 5 and any("Five hands" in s for s in zz_c.said),
              "B: a sitting stops at five hands (played through label sb_do_cards_play)", (_zz_hands, zz_c.said))
        check(cards_state == {} and cards_sit == {}, "B: cards_state == {} after leaving (and the sitting's tally is cleared)", (cards_state, cards_sit))
        check(builtins.sorted(mg_result) == ["game", "outcome", "yen"] and mg_result["game"] == "blackjack"
              and mg_result["outcome"] == "win" and mg_result["yen"] == yen - 5000 == 500,
              "B: mg_result has its three keys, and its yen is what my purse changed by", (mg_result, yen))
        check(period == "Evening", "E: a sitting with a hand played costs one period", period)
        check((bonds.get("yuji", 0), bonds.get("megumi", 0)) == (_zz_b0[0] + 1, _zz_b0[1] + 1)
              and {"cards:yuji", "cards:megumi"} <= actions_today,
              "E: Bond +1 with each opponent after the sitting", (bonds.get("yuji"), bonds.get("megumi")))
        check(cards_records() == builtins.dict(today=yen - 5000), "E: cards_records()['today'] equals the day's winnings", (cards_records(), yen))
        check(len(zz_c.blocks) == 11 and not any(b["can"] for b in zz_c.blocks),
              "F: blackjack through the label: after each of 5 deals, 5 stands and the leave, renpy.can_rollback() is False",
              [(b["stage"], b["can"]) for b in zz_c.blocks])
        _zz_toasts = [t["text"] for t in TOASTQ.items]
        check(len(_zz_toasts) >= 1, "E: the Bond toasts are queued for the place view, after the table", _zz_toasts)

    ## ¥3,000 down, through the labels: three lost hands at ¥1,000.
    python:
        zz_c_base(yen=9000, who=("nobara",))
        zz_c_wrap()
        zz_c.policy = zz_c_thousand
        zz_c.cards[:] = zz_cd("TS 6H TD 9C") * 3
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        zz_c_unpatch()
        check(yen == 6000 and builtins.max(b["hands"] or 0 for b in zz_c.blocks) == 3 and any("3,000 down" in s for s in zz_c.said),
              "B: a sitting stops at ¥3,000 down (played through label sb_do_cards_play)", (yen, zz_c.said))
        check(cards_records()["today"] == -3000, "E: a losing day reads as a negative figure", cards_records())

    ## The table remembers the sitting's stake (played through the label).
    python:
        zz_c_base(yen=5000, who=("yuji",))
        zz_c_wrap()
        zz_c.policy = zz_c_five_hundred
        zz_c.cards[:] = zz_cd("TS 6H TD 9C")
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        zz_c_unpatch()
        check(zz_c.picks[:1] == [100] and zz_c.picks[-1] == 500 and yen == 4500,
              "B: back at the table after a ¥500 hand, the stake is still ¥500 (it opened on ¥100)", (zz_c.picks, yen))
        check(cards_default_stake() == 100, "B: a new sitting opens on the smallest stake again", cards_sit)
        cards_sit_down(cards_opponents())
        cards_sit["stake"] = 1000
        fixture(yen=1000)
        _zz_a = cards_default_stake()
        fixture(yen=999)
        check(_zz_a == 1000 and cards_default_stake() == 100,
              "B: the remembered stake is kept only while I can cover it", (_zz_a, cards_default_stake()))
        zz_c_reset()

    ## No hand played: no period, no Bond.
    python:
        zz_c_base(yen=5000, who=("yuji",))
        zz_c_wrap()
        zz_c.policy = zz_c_close
        _zz_b0 = bonds.get("yuji", 0)
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        zz_c_unpatch()
        check(period == "Afternoon" and bonds.get("yuji", 0) == _zz_b0 and "cards:yuji" not in actions_today and yen == 5000
              and cards_ok() is True,
              "E: sitting down and getting up without a hand costs no period and gives no Bond", (period, bonds.get("yuji")))

    ## =====================================================================
    ## C. The day's winnings never pass BOARD_YEN["g4"][1]
    python:
        zz_c_base(yen=50000, who=("megumi",))
        zz_c_patch("cards_draw", zz_c_draw)
        _zz_cap = BOARD_YEN["g4"][1]
        _zz_top = 0
        _zz_n = 0
        _zz_over = builtins.list()
        for _zz_round in range(40):
            cards_sit_down(["megumi"])
            _zz_any = False
            for _zz_s in builtins.reversed(CARDS_STAKES):
                cards_new("blackjack", ["megumi"], _zz_s)
                while not cards_can_deal("blackjack", _zz_s):
                    ## A natural on even hands, a doubled 21 on odd ones: the most a hand can win.
                    if _zz_n % 2 == 0:
                        zz_c.cards[:] = zz_cd("AS KH TD 7C")
                        cards_bj_deal()
                    else:
                        zz_c.cards[:] = zz_cd("5S 6H TD 7C TS")
                        cards_bj_deal()
                        if not cards_bj_double():
                            cards_bj_stand()
                    _zz_n += 1
                    _zz_any = True
                    _zz_top = builtins.max(_zz_top, cards_today())
                    if cards_today() > _zz_cap:
                        _zz_over.append(cards_today())
                cards_end()
            zz_c_reset()
            if not _zz_any:
                break
        check(not _zz_over and _zz_cap - 2 * CARDS_STAKES[0] < _zz_top <= _zz_cap and cards_records()["today"] == _zz_top,
              "C: winning every blackjack hand, sitting after sitting, the day's winnings stop under BOARD_YEN['g4'][1]",
              (_zz_top, _zz_cap, _zz_n, _zz_over[:3]))
        check(all(cards_can_deal("blackjack", s) != "" for s in CARDS_STAKES),
              "C: after that no stake is dealt: the refusal has its line", [cards_can_deal("blackjack", s) for s in CARDS_STAKES])
        cards_sit_down(["megumi"])
        check(CARDS_STYLE["megumi"]["stop"] in cards_sit_over() and "Megumi" in cards_sit_over(),
              "C: winnings past the limit are refused with a line", cards_sit_over())
        zz_c_reset()
        check(yen >= CARDS_STAKES[0] and cards_opponents() == ["megumi"] and "cards:megumi" not in actions_today
              and cards_ok() is False and "cards_play" not in [a[0] for a in place_actions("dorm_common")],
              "C: once the day's limit is won the table is no longer offered (no dead-end icon)", (cards_ok(), cards_cap_left()))
        fixture(day=4)
        pin("megumi", "dorm_common")
        check(cards_records()["today"] == 0 and cards_can_deal("blackjack", 1000) == "" and cards_ok() is True,
              "C: the next day the count starts again and the table is back", cards_records())
        fixture(cards_won=4500, cards_won_day=day)
        cards_sit_down(["megumi"])
        check(cards_can_deal("blackjack", 1000).startswith("Not at that stake") and cards_can_deal("blackjack", 500) == ""
              and cards_can_deal("poker", 1000) == "",
              "C: a stake too big for the room left says so, while a lower one still plays",
              [cards_can_deal("blackjack", s) for s in CARDS_STAKES])
        fixture(cards_won=5900, cards_won_day=day)
        check(all(cards_can_deal("blackjack", s) == "They've lost enough to me today." for s in CARDS_STAKES),
              "C: with no stake left to play, the line is the plain one", [cards_can_deal("blackjack", s) for s in CARDS_STAKES])
        zz_c_reset()

        ## Poker: a pot bigger than the room left is paid only up to the limit.
        zz_c_base(yen=20000, who=("megumi", "nobara", "yuji"))
        _zz_pk = [g for g in mg_games() if g["id"] == "poker"][0]
        check(cards_game_note(_zz_pk, 500, 3) == CARDS_BLURB["poker"] and cards_game_note(_zz_pk, 1000, 2) == CARDS_BLURB["poker"],
              "C: while the day's limit is further off than the most a hand can win, poker's note is its blurb", cards_game_note(_zz_pk, 500, 3))
        check(cards_game_note(_zz_pk, 1000, 3) == u"They'll pay me ¥6,000 more today, no further.",
              "C: three opponents at ¥1,000 could lose ¥9,000 in a hand: the note says the ¥6,000 they will pay", cards_game_note(_zz_pk, 1000, 3))
        fixture(cards_won=5000, cards_won_day=day)
        check(cards_game_note(_zz_pk, 1000, 3) == u"They'll pay me ¥1,000 more today, no further." and cards_game_open(_zz_pk, 1000, 3)
              and cards_game_note(_zz_pk, 100, 3) == CARDS_BLURB["poker"],
              "C: near the limit the table says, before the hand, how much a poker win can still pay",
              (cards_game_note(_zz_pk, 1000, 3), cards_game_note(_zz_pk, 100, 3)))
        cards_new("poker", ["megumi", "nobara", "yuji"], 1000)
        ## Mine, then Megumi's, Nobara's, Yuji's: a royal flush against three high pairs.
        zz_c.cards[:] = zz_cd("TS JS QS KS AS") + zz_cd("AH AD KC 8C JC") + zz_cd("KH KD QD JD 9C") + zz_cd("QH QC 9D 8D 7C")
        cards_pk_deal()
        _zz_y0 = yen
        cards_pk_bet()
        _zz_stage1 = cards_state["stage"]
        cards_pk_draw(())
        cards_pk_bet()
        check(_zz_stage1 == "draw" and cards_state["stage"] == "done" and cards_state["result"] == "win"
              and cards_state["pot"] == 12000 and cards_state["paid"] == {"me": 12000}
              and cards_state["capped"] and cards_today() == _zz_cap and cards_state["last"] == 1000
              and yen == 20000 + 1000,
              "C: a ¥12,000 pot won with ¥1,000 of room left pays my money back and ¥1,000, no more",
              (_zz_stage1, cards_state["stage"], cards_state["result"], cards_state["pot"], cards_today(), yen))
        check("part of it" in cards_result_line() and "past that" not in cards_result_line(),
              "C: the screen says the pot was cut short", cards_result_line())
        cards_end()
        zz_c_unpatch()

    ## =====================================================================
    ## D. Poker
    python:
        _zz_ranks = [cards_pk_rank(zz_cd(h)) for h in ZZ_C_LADDER]
        check(len(ZZ_C_LADDER) == 20 and all(_zz_ranks[i] < _zz_ranks[i + 1] for i in range(19))
              and [r[0] for r in _zz_ranks] == ZZ_C_LADDER_CATS,
              "D: the ranker orders a fixed set of 20 hands correctly",
              [(ZZ_C_LADDER[i], _zz_ranks[i]) for i in range(19) if not _zz_ranks[i] < _zz_ranks[i + 1]])
        _zz_mixed = builtins.list(ZZ_C_LADDER)
        renpy.random.shuffle(_zz_mixed)
        check(builtins.sorted(_zz_mixed, key=lambda h: cards_pk_rank(zz_cd(h))) == ZZ_C_LADDER,
              "D: sorting the 20 hands by rank from any order gives the same ladder")
        check(cards_pk_rank(zz_cd("AS KH 9D 5C 3S")) == cards_pk_rank(zz_cd("AD KC 9H 5S 3H"))
              and cards_pk_rank(zz_cd("5S 4H 3D 2C AS")) == cards_pk_rank(zz_cd("AS 2H 3D 4C 5S")),
              "D: suits never break a tie, and the order of the cards in the hand doesn't matter")
        check([cards_pk_name(zz_cd(h)) for h in (ZZ_C_LADDER[0], ZZ_C_LADDER[4], ZZ_C_LADDER[19])] == ["High card", "A pair", "Straight flush"]
              and [cards_pk_steps(zz_cd(h)) for h in (ZZ_C_LADDER[0], ZZ_C_LADDER[7], ZZ_C_LADDER[17])] == [1, 5, 5],
              "D: hand names and the read's five steps", [cards_pk_steps(zz_cd(h)) for h in ZZ_C_LADDER])

        _zz_missing = [w for w in ROSTER_ORDER if not (isinstance(CARDS_STYLE.get(w), builtins.dict)
                       and all(k in CARDS_STYLE[w] for k in ("tight", "bluff", "tell", "win", "lose")))]
        check(len(ROSTER_ORDER) == 11 and not _zz_missing and all(0 <= CARDS_STYLE[w]["tight"] <= 1 and 0 <= CARDS_STYLE[w]["bluff"] <= 1 for w in ROSTER_ORDER),
              "D: each of the eleven has a CARDS_STYLE row (tight, bluff, tell, win, lose)", _zz_missing)
        check(CARDS_STAKES == (100, 500, 1000) and CARDS_LIMIT == builtins.dict(hands=5, down=3000),
              "D: CARDS_STAKES and CARDS_LIMIT are the plan's", (CARDS_STAKES, CARDS_LIMIT))
        _zz_words = " ".join(" ".join((r["win"], r["lose"], r["stop"])) for r in CARDS_STYLE.values())
        check(not any(n in _zz_words for n in ("Kai" + "to", "Ama" + "giri")), "D: no table line names the protagonist")

        ## The faces: what each style gives away.
        _zz_plan_bluff = builtins.dict(bet=True, call=True, bluff=True)
        _zz_plan_quiet = builtins.dict(bet=False, call=False, bluff=False)
        check(zz_c_tell("yuji", 0.2, _zz_plan_bluff) > 0.7 and zz_c_tell("yuji", 0.2, _zz_plan_quiet) < 0.2,
              "D: Yuji bluffs and it shows", (zz_c_tell("yuji", 0.2, _zz_plan_bluff), zz_c_tell("yuji", 0.2, _zz_plan_quiet)))
        check(zz_c_tell("panda", 0.95, _zz_plan_quiet) > 0.7 and zz_c_tell("panda", 0.2, _zz_plan_quiet) < 0.2,
              "D: Panda can't hide a good hand")
        check(zz_c_tell("nobara", 0.6, _zz_plan_bluff) > 0.7 and zz_c_tell("nobara", 0.6, _zz_plan_quiet) < 0.2,
              "D: Nobara looks annoyed when she is about to bet")
        check(all(builtins.set(cards_pk_face(w, s, p) for i in range(60) for s in (0.1, 0.9) for p in (_zz_plan_bluff, _zz_plan_quiet))
                  == {CARDS_STYLE[w]["rest"]} for w in ("megumi", "toge", "gojo")),
              "D: Megumi shows nothing, Toge is unreadable, Gojo's face says nothing either")
        check(CARDS_STYLE["gojo"].get("blind") is True, "D: Gojo plays blind")

        ## 400 hands through the functions: the pot is always paid whole.
        _zz_odd = builtins.list()
        _zz_kinds = builtins.dict()
        zz_c_patch("cards_pk_showdown", zz_c_showdown)
        for _zz_i in range(400):
            zz_c_base(yen=50000, who=("yuji", "megumi", "gojo"))
            cards_new("poker", [("yuji", "megumi", "gojo"), ("nobara",), ("panda", "toge")][_zz_i % 3], 500)
            _zz_n = len(cards_state["opponents"])
            cards_pk_deal()
            _zz_step = 0
            while cards_state["stage"] != "done" and _zz_step < 12:
                _zz_step += 1
                _zz_stage = cards_state["stage"]
                if _zz_stage == "draw":
                    cards_pk_draw(cards_pk_discards(cards_state["mine"]))
                elif _zz_stage in ("call1", "call2"):
                    if renpy.random.random() < 0.7:
                        cards_pk_bet()
                    else:
                        cards_pk_fold()
                elif renpy.random.random() < 0.5:
                    cards_pk_bet()
                else:
                    cards_pk_check()
            _zz_sh = zz_c.shows[-1] if zz_c.shows else {}
            _zz_paid = _zz_sh.get("paid") or {}
            _zz_kinds[cards_state["result"]] = _zz_kinds.get(cards_state["result"], 0) + 1
            if (cards_state["stage"] != "done" or not _zz_paid or builtins.sum(_zz_paid.values()) != _zz_sh["pot"]
                    or builtins.max(_zz_paid.values()) - builtins.min(_zz_paid.values()) > 1
                    or yen - 50000 != cards_state["last"] or yen < 0
                    or (("me" in _zz_paid) != (cards_state["result"] in ("win", "split")))
                    or _zz_sh["pot"] % 500 or _zz_sh["pot"] < 500 * (_zz_n + 1)
                    or len(builtins.set(cards_state["mine"] + [c for h in cards_state["theirs"].values() for c in h] + cards_state["deck"])) != len(cards_state["mine"]) + 5 * _zz_n + len(cards_state["deck"])):
                _zz_odd.append((cards_state["stage"], _zz_paid, _zz_sh.get("pot"), yen - 50000, cards_state["last"]))
            cards_end()
        check(not _zz_odd and _zz_kinds.get("win", 0) > 20 and _zz_kinds.get("lose", 0) > 20 and _zz_kinds.get("fold", 0) > 5,
              "D: 400 hands through the game's functions: the pot is paid whole, to one player or split, and my yen moves by exactly my share less what I put in",
              (_zz_kinds, _zz_odd[:3]))
        note("D: 400 poker hands", "results: %r" % (builtins.sorted(_zz_kinds.items()),))

        ## A split pot.
        zz_c_base(yen=5000, who=("megumi",))
        zz_c_patch("cards_draw", zz_c_draw)
        cards_new("poker", ["megumi"], 100)
        zz_c.cards[:] = zz_cd("TS JH QD KC AS") + zz_cd("TH JD QC KS AH")      # two straights to the ace: nobody draws
        cards_pk_deal()
        cards_pk_bet()
        cards_pk_draw(())
        check(cards_state["line"] == "I stand pat. Megumi stands pat.", "D: the draw is told in words, and nobody 'takes 0'", cards_state["line"])
        cards_pk_bet()
        _zz_sh = zz_c.shows[-1]
        check(cards_state["line"] == "The same hand. We split it." and cards_face_of("megumi") == "neutral"
              and cards_face_of("megumi") == CARDS_STYLE["megumi"]["rest"]
              and cards_state["says"] == "" and cards_state["speaker"] == "",
              "D: a split says so, nobody speaks a winner's line, and Megumi's face stays at rest", (cards_state["line"], cards_state["face"]))
        check(cards_state["result"] == "split" and _zz_sh["pot"] == 600 and _zz_sh["paid"] == {"me": 300, "megumi": 300}
              and cards_state["last"] == 0 and yen == 5000,
              "D: equal hands split the pot", (_zz_sh, cards_state["result"], yen))
        cards_end()

        ## Everyone folds to my bet: nobody showed a hand, so nobody is sore about one.
        _zz_out = None
        for _zz_i in range(30):
            zz_c_base(yen=5000, who=("ijichi", "panda"))
            zz_c_patch("cards_draw", zz_c_draw)
            cards_new("poker", ["ijichi", "panda"], 100)
            zz_c.cards[:] = zz_cd("AS AH AD 4C 2S") + zz_cd("7H 5D 4D 3S 2H") + zz_cd("7C 5C 4H 3D 2C")
            cards_pk_deal()
            cards_pk_bet()
            if cards_state["stage"] == "done" and not cards_state["live"]:
                _zz_out = builtins.dict(cards_state)
                cards_end()
                break
            cards_end()
        check(_zz_out is not None and _zz_out["result"] == "win" and _zz_out["shown"] == [] and _zz_out["says"] == ""
              and _zz_out["speaker"] == "" and _zz_out["line"] == "Everyone else is out." and _zz_out["last"] == 200,
              "D: when everyone folds to my bet nobody speaks a losing line about a hand they threw away",
              _zz_out and (_zz_out["says"], _zz_out["line"], _zz_out["last"]))
        _zz_words = " ".join(r["lose"] for r in CARDS_STYLE.values())
        check("folded" not in _zz_words and "Panda wins" not in " ".join(r["win"] for r in CARDS_STYLE.values()),
              "D: no losing line talks about folding (it is the blackjack dealer's line too), and Panda says 'I'")
        check([cards_style(w).get("glad", "happy") for w in ("megumi", "toge", "yaga", "maki", "yuji", "panda")]
              == ["neutral", "neutral", "serious", "serious", "happy", "happy"],
              "D: the ones whose faces give nothing away don't grin when they win")
        for _zz_w, _zz_f in (("megumi", "neutral"), ("yuji", "happy")):
            zz_c_base(yen=5000, who=(_zz_w,))
            zz_c_patch("cards_draw", zz_c_draw)
            cards_new("blackjack", [_zz_w], 100)
            zz_c.cards[:] = zz_cd("TS 6H TD 9C")
            cards_bj_deal()
            cards_bj_stand()
            check(cards_state["result"] == "lose" and cards_face_of(_zz_w) == _zz_f
                  and cards_state["says"] == {"megumi": "Dealer's hand.", "yuji": CARDS_STYLE["yuji"]["win"]}[_zz_w],
                  "D: dealing a winning hand, %s's face is %s and the line is the dealer's" % (_zz_w.title(), _zz_f),
                  (cards_state["result"], cards_state["face"], cards_state["says"]))
            cards_end()

        ## The read.
        zz_c_base(yen=5000, who=("yuji", "megumi"))
        fixture(insight=19)
        cards_new("poker", ["yuji", "megumi"], 100)
        cards_pk_deal()
        renpy.show_screen("cards_poker")
        check(cards_pk_can_read() is False and cards_pk_read("yuji") is False and zz_rect("cards_poker", "cards_look") is None,
              "D: at Insight 19 the read is not offered (no button, and the function refuses)")
        fixture(insight=20)
        check(cards_pk_can_read() is True and zz_rect("cards_poker", "cards_look") is not None,
              "D: at Insight 20 the read is offered", zz_rect("cards_poker", "cards_look"))
        _zz_look = zz_rect("cards_poker", "cards_look")
        check(_zz_look is not None and abs(_zz_look[0] - 1700) <= 2 and abs(_zz_look[1] - 560) <= 2,
              "D: the look button is at (1700, 560)", _zz_look)
        check(cards_pk_read("megumi") is True and cards_state["read"] == "megumi", "D: reading Megumi marks him as read")
        check(cards_pk_can_read() is False and cards_pk_read("yuji") is False and cards_state["read"] == "megumi"
              and zz_rect("cards_poker", "cards_look") is None,
              "D: the read is once a hand: a second is refused and the button is gone")
        _zz_bar = cards_pk_steps(cards_state["theirs"]["megumi"])
        check(1 <= _zz_bar <= 5, "D: the read shows a strength of one to five steps", _zz_bar)
        shot("cards_poker_read")
        while cards_state["stage"] != "done":
            if cards_state["stage"] == "draw":
                cards_pk_draw(())
            else:
                cards_pk_fold()
        cards_pk_deal()
        check(cards_pk_can_read() is True and cards_state["read"] == "", "D: the next hand has its own read")
        renpy.hide_screen("cards_poker")
        cards_end()
        zz_c_unpatch()

    ## Full hands under the game's own autoplay (check, call, stand pat, leave).
    python:
        zz_c_base(yen=50000, who=("yuji", "megumi", "nobara"))
        zz_c_patch("cards_pk_showdown", zz_c_showdown)
        _zz_auto_n = 0
        _zz_odd = builtins.list()
        autoplay(True)
    while _zz_auto_n < 6:
        $ _zz_y0 = yen
        $ fixture(cards_won=0, cards_won_day=0)
        call mg_poker(["yuji", "megumi", "nobara"][:1 + _zz_auto_n % 3], 100)
        python:
            _zz_auto_n += 1
            _zz_sh = zz_c.shows[-1] if len(zz_c.shows) == _zz_auto_n else {}
            _zz_paid = _zz_sh.get("paid") or {}
            if (not _zz_paid or builtins.sum(_zz_paid.values()) != _zz_sh["pot"] or cards_state != {}
                    or builtins.sorted(mg_result) != ["game", "outcome", "yen"] or mg_result["game"] != "poker"
                    or mg_result["yen"] != yen - _zz_y0 or mg_result["outcome"] == "quit"):
                _zz_odd.append((_zz_sh, mg_result, yen - _zz_y0))
    python:
        autoplay(False)
        zz_c_unpatch()
        check(not _zz_odd and len(zz_c.shows) == 6,
              "D: a full hand under autoplay ends with the pot paid to exactly one player or split (6 hands, 1 to 3 opponents, label mg_poker)",
              _zz_odd[:2])
        check(cards_state == {} and mg_result["game"] == "poker", "D: poker leaves cards_state empty and sets mg_result", mg_result)

    ## =====================================================================
    ## E. Bond once a day (the period and the first Bond are checked in B)
    python:
        zz_c_base(yen=5000, who=("yuji",))
        _zz_b0 = bonds.get("yuji", 0)
        for _zz_i in range(2):
            cards_sit_down(["yuji"])
            cards_new("blackjack", ["yuji"], 100)
            cards_bj_deal()
            cards_bj_stand()
            cards_end()
            fixture(period="Afternoon")
            cards_get_up()
        check(bonds.get("yuji", 0) == _zz_b0 + 1, "E: Bond +1 with an opponent once a day, not once a sitting", (bonds.get("yuji"), _zz_b0))
        fixture(day=4, period="Afternoon")
        store.actions_today = builtins.set()
        pin("yuji", "dorm_common")
        cards_sit_down(["yuji"])
        cards_new("blackjack", ["yuji"], 100)
        cards_bj_deal()
        cards_bj_stand()
        cards_end()
        cards_get_up()
        check(bonds.get("yuji", 0) == _zz_b0 + 2, "E: and again the next day", bonds.get("yuji"))
        toast_clear()

    ## =====================================================================
    ## F. Rollback: every move, through the real labels
    python:
        zz_c_base(yen=5000, who=("megumi",))
        zz_c_wrap()
        zz_c.policy = zz_c_every_move
        zz_c.rb_on = True
        zz_c.cards[:] = zz_cd("9S 2H TD 7C 7S") + zz_cd("5S 6H TD 7C TS")
        autoplay(True)
    call mg_blackjack(["megumi"], 100)
    python:
        autoplay(False)
        zz_c_unpatch()
        _zz_log = [(b["stage"], b["hands"], b["can"]) for b in zz_c.blocks]
        check(len(zz_c.blocks) == 6 and not any(b["can"] for b in zz_c.blocks)
              and [b["stage"] for b in zz_c.blocks[:5]] == ["play", "play", "done", "play", "done"],
              "F: blackjack: after the deal, a hit, the stand's settlement, a second deal, a double and the leave, renpy.can_rollback() is False",
              _zz_log)
        check(mg_result == builtins.dict(game="blackjack", outcome="win", yen=300) and yen == 5300,
              "F: as scripted: 18 beats 17 (+¥100), then a doubled 21 beats 17 (+¥200)", (mg_result, yen))
        ## The leave's block has no cards screen after it here (the label was called bare).
        check([w for w, same in zz_c.rb_log] == ["play 1", "play 1", "done 1", "play 2", "done 2"] and all(same for w, same in zz_c.rb_log),
              "F: blackjack: a rollback asked for on the screen after the deal, the hit, each settlement and the second deal changes nothing",
              zz_c.rb_log)
    python:
        zz_c_base(yen=5000, who=("megumi", "panda"))
        zz_c_wrap()
        zz_c.policy = zz_c_poker_moves
        zz_c.rb_on = True
        ## Both opponents hold two pair each hand, so both always bet and call:
        ## the moves, and so the blocks, come out the same every run. Mine,
        ## theirs, theirs; then the draw (hand 1: my two, one each; hand 2: one each).
        _zz_deal = zz_cd("AS AH 7D 4C 2S") + zz_cd("KS KH QD QC 3S") + zz_cd("JS JH TD TC 3H")
        zz_c.cards[:] = _zz_deal + zz_cd("9C 8C 4D 5D") + _zz_deal + zz_cd("4D 5D")
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        zz_c_unpatch()
        _zz_log = [(b["stage"], b["hands"], b["read"]) for b in zz_c.blocks]
        ## Hand 1: deal, read, check (they bet), call, draw two, bet (showdown).
        ## Hand 2: deal, bet, stand pat, fold; then the leave.
        _zz_want = [("bet1", 1, False), ("bet1", 1, True), ("call1", 1, True), ("draw", 1, True), ("bet2", 1, True), ("done", 1, True),
                    ("bet1", 2, False), ("draw", 2, False), ("bet2", 2, False), ("done", 2, False), ("done", 2, False)]
        check(_zz_log == _zz_want and not any(b["can"] for b in zz_c.blocks),
              "F: poker through sb_do_cards_play: cards_block() follows the deal, the read, the check, the call, the draw, the bet, the fold and the leave, in that order, and renpy.can_rollback() is False after each",
              (_zz_log, [b["can"] for b in zz_c.blocks]))
        check(zz_c.reads == [True],
              "F: the read is spent once: no rollback gives it back to be used on someone else", zz_c.reads)
        check(len(zz_c.rb_log) == 11 and zz_c.rb_log[1][0].startswith("read") and zz_c.rb_log[-1][0] == "done 2"
              and all(same for w, same in zz_c.rb_log),
              "F: poker: a rollback asked for on the screen after every one of those (the read, the draw and the showdown among them, and at the table after leaving) changes nothing",
              zz_c.rb_log)
        check(len(zz_c.shows) == 2 and mg_result["game"] == "poker" and period == "Evening" and cards_state == {},
              "F: two poker hands were played out through the table, and the sitting cost its period", (mg_result, period))

    ## =====================================================================
    ## G. Night
    python:
        zz_c_base(yen=5000, who=("yuji",), period="Night")
        zz_c_patch("view_person_rects", lambda loc: [])
        if night_exists():
            check(night_allows("cards_play", 1) is False, "G: at Night night_allows('cards_play', 1) is False")
            check(cards_ok() is True and "cards_play" in [a[0] for a in place_actions("dorm_common")]
                  and "cards_play" not in [a[0] for a in rail_actions("dorm_common")],
                  "G: at Night the icon column has no card table", [a[0] for a in rail_actions("dorm_common")])
            _zz_hs = [h for h in hot_spots_for("dorm_common") if h["act"] == "cards_play"]
            check(len(_zz_hs) >= 1 and all(hot_open(h) is False and isinstance(hot_action(h), NullAction) for h in _zz_hs),
                  "G: at Night the table's hotspot is dim and does nothing", _zz_hs)
            note("G: the hotspot", "the row tested is the harness's own (zz_c_table) plus P6's if it is in this tree: %r. "
                 "P6 registers the real one in room_spots.rpy; P8 re-runs this section on the merged tree."
                 % ([h["id"] for h in _zz_hs],))
        else:
            note("G: at Night the table is closed", "NOT YET: sb_night.rpy is the wave-0 stub here; deferred to P8 (7.3)")
        fixture(period="Afternoon")
        _zz_hs = [h for h in hot_spots_for("dorm_common") if h["act"] == "cards_play"]
        check(len(_zz_hs) >= 1 and all(hot_open(h) and hot_action(h) == Return(("act", "cards_play")) for h in _zz_hs)
              and "cards_play" not in [a[0] for a in rail_actions("dorm_common")] and "cards_play" in hot_covers("dorm_common"),
              "G: by day the hotspot returns ('act', 'cards_play') and the column leaves the action to it")
        zz_c_unpatch()
        fixture(period="Night")
        _zz_n = len(zz_c.said)
        autoplay(True)
    call sb_do_cards_play
    python:
        autoplay(False)
        if night_exists():
            check(period == "Night" and yen == 5000 and cards_state == {} and cards_sit == {} and zz_c.said[_zz_n:] == ["Too late. Bed."],
                  "G: label sb_do_cards_play at Night says it is too late and deals nothing", (period, zz_c.said[_zz_n:]))

    ## =====================================================================
    ## H. The three screens: zz_worst, no toast, the lanes, the names
    ## (The dialogue window of section G's line is put away first, as the
    ## place view's loop would have it: its gradient would dim the buttons.)
    window hide
    python:
        note("H: screens up before the shots", builtins.sorted(zz_layer_tags("screens")))
        zz_c_base(yen=3200, who=("yuji", "megumi", "nobara"))
        cards_sit_down(cards_opponents())
        renpy.show_screen("cards_table")
        check(toast_room() == (0, 0, 0), "H: toast_room() is (0, 0, 0) over the card table", toast_room())
        check(zz_rect("cards_table", "cards_game_blackjack") is not None and zz_rect("cards_table", "cards_game_poker") is not None
              and all(zz_rect("cards_table", "cards_stake_%d" % s) is not None for s in CARDS_STAKES)
              and zz_rect("cards_table", "cards_leave") is not None,
              "H: the table shows a button per game, the three stakes and Leave")
        _zz_ok = zz_worst("cards_table", hover="cards_game_blackjack")
        toast("A reward", "item")
        zz_render(0.5)
        check(_zz_ok and toast_visible() == [] and len(TOASTQ.items) == 1 and TOASTQ.items[0]["t_shown"] is None,
              "H: zz_worst('cards_table'): no toast is drawn, and a queued one waits", (toast_visible(), len(TOASTQ.items)))
        toast_clear()
        _zz_tips = [(i, zz_c_btn("cards_table", i)._get_tooltip())
                    for i in ["cards_game_blackjack", "cards_game_poker", "cards_leave"] + ["cards_stake_%d" % s for s in CARDS_STAKES]]
        check(all(t is None for i, t in _zz_tips),
              "H: the table's buttons carry their names in words and no hover label (it would cover the button beside it)", _zz_tips)
        zz_worst("cards_table", hover="cards_game_poker", name="cards_table_hover_poker")
        check(GetTooltip() is None, "H: hovering Five-card draw draws no label", GetTooltip())
        _zz_tw = zz_words("cards_table")
        note("H: cards_table", "%d words, %d buttons" % (len(_zz_tw), zz_buttons("cards_table")))
        renpy.hide_screen("cards_table")
        ## A purse that covers ¥500 but not ¥1,000.
        fixture(yen=600)
        renpy.show_screen("cards_table")
        check(zz_rect("cards_table", "cards_stake_1000") is None and zz_rect("cards_table", "cards_stake_500") is not None,
              "H: a stake I can't cover is dim (not pressable)")
        shot("cards_table_poor")
        renpy.hide_screen("cards_table")
        zz_c_reset()

        ## Blackjack, mid-hand.
        zz_c_base(yen=3200, who=("nobara", "shoko"))
        zz_c_patch("cards_draw", zz_c_draw)
        cards_sit_down(cards_opponents())
        cards_new("blackjack", cards_opponents(), 500)
        zz_c.cards[:] = zz_cd("9S 2H KD 7C")
        cards_bj_deal()
        renpy.show_screen("cards_blackjack")
        zz_render(0.05)
        _zz_g0 = [type(zz_c_btn("cards_blackjack", i).action).__name__ for i in ("cards_hit", "cards_stand", "cards_double", "cards_leave")]
        zz_render(0.6)
        _zz_g1 = [zz_c_btn("cards_blackjack", i).action for i in ("cards_hit", "cards_stand", "cards_leave")]
        check(_zz_g0 == ["NullAction"] * 4 and all(isinstance(a, Return) for a in _zz_g1) and _zz_g1[0].value == ("hit",)
              and renpy.get_screen("cards_blackjack").scope["cards_guard"] is False,
              "H: blackjack's buttons take no click for a moment after the screen opens (a double click on Deal isn't a Hit), then work",
              (_zz_g0, _zz_g1))
        check(toast_room() == (0, 0, 0), "H: toast_room() is (0, 0, 0) over blackjack", toast_room())
        _zz_btn = [zz_rect("cards_blackjack", i) for i in ("cards_hit", "cards_stand", "cards_double", "cards_leave")]
        check(all(r is not None and abs(r[1] - 840) <= 2 and 760 <= r[0] and r[0] + r[2] <= 1840 for r in _zz_btn),
              "H: Hit, Stand, Double and Leave sit at y 840 inside the table panel", _zz_btn)
        _zz_ok = zz_worst("cards_blackjack", hover="cards_hit")
        toast("A reward", "item")
        zz_render(0.5)
        check(_zz_ok and toast_visible() == [] and len(TOASTQ.items) == 1,
              "H: zz_worst('cards_blackjack'): no toast is drawn", (toast_visible(), len(TOASTQ.items)))
        toast_clear()
        _zz_tips = [(i, zz_c_btn("cards_blackjack", i)._get_tooltip()) for i in ("cards_hit", "cards_stand", "cards_double", "cards_leave")]
        check(all(t is None for i, t in _zz_tips), "H: blackjack's buttons carry no hover label", _zz_tips)
        check(any("Give up the hand" in t for t in zz_texts("cards_blackjack")),
              "H: mid-hand the way out says what it costs: 'Give up the hand'", zz_texts("cards_blackjack"))
        zz_worst("cards_blackjack", hover="cards_double", name="cards_blackjack_hover_double")
        check(GetTooltip() is None, "H: hovering Double draws no label over Stand", GetTooltip())
        _zz_scope = builtins.dict((k, v) for k, v in renpy.get_screen("cards_blackjack").scope.items() if "cards" in k)
        check(zz_c_plain(_zz_scope) and pickle.loads(pickle.dumps(_zz_scope, pickle.HIGHEST_PROTOCOL)) == _zz_scope,
              "I: blackjack's screen variables are plain and pickle", builtins.sorted(_zz_scope))
        zz_c.cards[:] = zz_cd("TS")
        cards_bj_hit()
        cards_bj_stand()
        zz_render(0.2)
        check(zz_rect("cards_blackjack", "cards_deal") is not None and zz_rect("cards_blackjack", "cards_hit") is None,
              "H: once a hand is settled the buttons are Deal and Leave")
        check(zz_c_btn("cards_blackjack", "cards_deal")._get_tooltip() is None
              and not any("Give up the hand" in t for t in zz_texts("cards_blackjack")) and any(t == "Leave" for t in zz_texts("cards_blackjack")),
              "H: Deal has no hover label, and the way out reads 'Leave' again", zz_texts("cards_blackjack"))
        check(any(CARDS_STYLE["nobara"]["lose"] in t for t in zz_texts("cards_blackjack")) and cards_face_of("nobara") == CARDS_STYLE["nobara"]["sore"],
              "H: the dealer's line and face follow the hand (21 against 17: she loses)", (cards_state["says"], cards_state["face"]))
        shot("cards_blackjack_done")
        cards_end()

        ## A long hand closes up: it never runs under its total or off the table.
        _zz_gaps = [(n, cards_row_gap(n)) for n in range(1, 12)]
        check(all(g == 16 for n, g in _zz_gaps if n <= 6) and all(120 * n + g * (n - 1) <= 820 and 120 + g >= 60 for n, g in _zz_gaps if n >= 2),
              "H: a blackjack hand of up to eleven cards ends by x 1620, left of its total, with each card's rank still showing", _zz_gaps)
        cards_new("blackjack", cards_opponents(), 100)
        zz_c.cards[:] = zz_cd("2S 2H TD 7C") + zz_cd("2D 2C 3S 3H 3D AS AH")
        cards_bj_deal()
        while len(cards_state["mine"]) < 9 and cards_state["stage"] == "play":
            cards_bj_hit()
        zz_render(0.2)
        check(len(cards_state["mine"]) == 9 and cards_total(cards_state["mine"]) == 19 and cards_state["stage"] == "play",
              "H: nine cards to nineteen, still in play (the screenshot's hand)", (cards_state["mine"], cards_state["stage"]))
        shot("cards_blackjack_long")
        cards_bj_stand()
        renpy.hide_screen("cards_blackjack")
        cards_end()
        zz_c_reset()

        ## Poker: three opponents, a live hand.
        zz_c_base(yen=3200, who=("yuji", "megumi", "panda"))
        cards_sit_down(cards_opponents())
        cards_new("poker", cards_opponents(), 500)
        zz_c.cards[:] = zz_cd("AS AH 7D 4C 2S")
        cards_pk_deal()
        renpy.show_screen("cards_poker")
        zz_render(0.05)
        _zz_g0 = [type(zz_c_btn("cards_poker", i).action).__name__ for i in ("cards_check", "cards_bet", "cards_fold", "cards_leave")]
        zz_render(0.6)
        _zz_g1 = [zz_c_btn("cards_poker", i).action for i in ("cards_check", "cards_bet", "cards_fold", "cards_leave")]
        check(_zz_g0 == ["NullAction"] * 4 and all(isinstance(a, Return) for a in _zz_g1) and _zz_g1[1].value == ("bet",),
              "H: poker's buttons take no click for a moment after the screen opens (a double click on Deal isn't a Bet), then work",
              (_zz_g0, _zz_g1))
        check(toast_room() == (0, 0, 0), "H: toast_room() is (0, 0, 0) over poker", toast_room())
        _zz_ok = zz_worst("cards_poker", hover="cards_check")
        toast("A reward", "item")
        zz_render(0.5)
        check(_zz_ok and toast_visible() == [] and len(TOASTQ.items) == 1,
              "H: zz_worst('cards_poker'): no toast is drawn", (toast_visible(), len(TOASTQ.items)))
        toast_clear()
        _zz_btn = [zz_rect("cards_poker", i) for i in ("cards_check", "cards_bet", "cards_fold", "cards_leave")]
        check(all(r is not None and 838 <= r[1] <= 852 for r in _zz_btn), "H: Check, Bet, Fold and Leave sit at y 840 to 850", _zz_btn)
        _zz_tips = [(i, zz_c_btn("cards_poker", i)._get_tooltip()) for i in ("cards_check", "cards_bet", "cards_fold", "cards_leave")]
        check(all(t is None for i, t in _zz_tips) and any("Fold and leave" in t for t in zz_texts("cards_poker")),
              "H: poker's buttons carry no hover label, and mid-hand the way out reads 'Fold and leave'", _zz_tips)
        check(zz_c_btn("cards_poker", "cards_look")._get_tooltip() is not None,
              "H: the icon-only look button keeps its hover label", zz_c_btn("cards_poker", "cards_look")._get_tooltip())
        renpy.get_screen("cards_poker").scope["cards_picking"] = True
        zz_render(0.2)
        _zz_rd = [(w, zz_c_btn("cards_poker", "cards_read_" + w)) for w in cards_state["opponents"]]
        check(len(_zz_rd) == 3 and all(b is not None and b._get_tooltip() is None and isinstance(b.action, Return) for w, b in _zz_rd),
              "H: the Read buttons under each opponent carry no hover label",
              [(w, b and b._get_tooltip()) for w, b in _zz_rd])
        renpy.get_screen("cards_poker").scope["cards_picking"] = False
        zz_render(0.2)
        zz_worst("cards_poker", hover="cards_fold", name="cards_poker_hover_fold")
        check(GetTooltip() is None, "H: hovering Fold draws no label over Bet", GetTooltip())
        check(all(zz_rect("cards_poker", "cards_my_%d" % i) is None for i in range(5)),
              "H: before the draw my cards can't be marked")
        ## Get to the draw whatever the opponents do.
        cards_pk_check()
        if cards_state["stage"] == "call1":
            cards_pk_bet()
        if cards_state["stage"] == "draw":
            zz_render(0.2)
            _zz_mine = [zz_rect("cards_poker", "cards_my_%d" % i) for i in range(5)]
            check(all(r is not None and r[1] == 560 and r[0] == 612 + 144 * i for i, r in enumerate(_zz_mine)),
                  "H: in the draw my five cards are buttons at y 560", _zz_mine)
            cards_state["marks"][2] = True
            cards_state["marks"][3] = True
            cards_state["marks"][4] = True
            zz_render(0.2)
            check(cards_marked() == (2, 3, 4) and zz_rect("cards_poker", "cards_my_2")[1] == 536,
                  "H: a marked card lifts, and three is the most", cards_marked())
            shot("cards_poker_draw")
            _zz_tips = [zz_c_btn("cards_poker", "cards_my_%d" % i)._get_tooltip() for i in range(5)]
            check(zz_c_btn("cards_poker", "cards_draw")._get_tooltip() is None, "H: the Draw button carries no hover label")
            check(_zz_tips == [None] * 5,
                  "H: my cards carry no hover label in the draw (it would cover the rank of the card beside it)", _zz_tips)
            zz_worst("cards_poker", hover="cards_my_4", name="cards_poker_hover_card")
            note("H: hovering my fifth card", "GetTooltip() is %r (cards_poker_hover_card.png)" % (GetTooltip(),))
            _zz_scope = builtins.dict((k, v) for k, v in renpy.get_screen("cards_poker").scope.items() if "cards" in k)
            check(zz_c_plain(_zz_scope) and pickle.loads(pickle.dumps(_zz_scope, pickle.HIGHEST_PROTOCOL)) == _zz_scope,
                  "I: poker's screen variables are plain and pickle", builtins.sorted(_zz_scope))
            zz_c.cards[:] = zz_cd("AD 9C 9S")
            cards_pk_draw(cards_marked())
            check(cards_pk_name(cards_state["mine"]) == "Full house" and cards_marked() == (),
                  "H: the draw replaces the marked cards and clears the marks", cards_state["mine"])
            check(cards_state["line"].startswith("I take three. ") and not any(ch.isdigit() for ch in cards_state["line"]),
                  "H: the draw's line spells its numbers out", cards_state["line"])
            cards_pk_bet()
            if cards_state["stage"] == "call2":
                cards_pk_bet()
            zz_render(0.2)
            check(cards_state["stage"] == "done" and zz_rect("cards_poker", "cards_deal") is not None,
                  "H: after the showdown the buttons are Deal and Leave", cards_state["stage"])
            check(zz_c_btn("cards_poker", "cards_deal")._get_tooltip() is None and any(t == "Leave" for t in zz_texts("cards_poker")),
                  "H: Deal has no hover label, and the way out reads 'Leave' again")
            if cards_state["result"] == "win":
                check(cards_result_line().startswith("Mine.  +"), "H: the result line leaves the pot to the line above it", cards_result_line())
            if cards_state["result"] == "win" and cards_state["shown"]:
                check(cards_state["line"] == "My full house holds." and cards_state["line"] not in ("Full house.",),
                      "H: a won showdown says my hand held, not its name a second time", cards_state["line"])
            shot("cards_poker_showdown")
        else:
            note("H: the draw screenshots", "everyone folded to the first bet this run; no draw to photograph")
        renpy.hide_screen("cards_poker")
        cards_end()
        zz_c_reset()

        ## Poker against one, and the stand-in pictures (no card back, no portrait).
        zz_c_base(yen=3200, who=("gojo",))
        cards_new("poker", ["gojo"], 100)
        cards_pk_deal()
        renpy.show_screen("cards_poker")
        zz_render(0.2)
        shot("cards_poker_one")
        store.CARDS_BACK = "gui/zz_no_such_card_back.png"
        zz_c_patch("cards_side", lambda who, expr=None: None)
        zz_render(0.3)
        check(not renpy.loadable(CARDS_BACK) and cards_side("gojo", "happy") is None,
              "I: the stand-in path: with no card back and no side portrait the poker screen still draws")
        shot("cards_standin")
        store.CARDS_BACK = "gui/card_back.png"
        zz_c_unpatch()
        renpy.hide_screen("cards_poker")
        cards_end()
        check(renpy.loadable("gui/card_back.png") and all(cards_side(w, e) for w in ROSTER_ORDER for e in ("neutral", "happy", "serious", "angry", "surprised", "sad")),
              "I: the card back and every side portrait the table uses are on disk")

    ## =====================================================================
    ## I. Saved state
    python:
        zz_c_base(yen=3200, who=("yuji", "megumi"))
        cards_sit_down(cards_opponents())
        _zz_all = builtins.list()
        cards_new("blackjack", cards_opponents(), 100)
        cards_bj_deal()
        _zz_all.append(builtins.dict(cards_state))
        cards_end()
        cards_new("poker", cards_opponents(), 100)
        cards_pk_deal()
        _zz_all.append(builtins.dict(cards_state))
        while cards_state["stage"] != "done":
            if cards_state["stage"] == "draw":
                cards_pk_draw((0,))
            elif not cards_pk_bet():
                cards_pk_fold()
        _zz_all.append(builtins.dict(cards_state))
        _zz_all.append(builtins.dict(cards_sit))
        cards_end()
        cards_get_up()
        _zz_all.append((cards_state, cards_sit, cards_won, cards_won_day, mg_result))
        check(all(zz_c_plain(v) for v in _zz_all) and pickle.loads(pickle.dumps(_zz_all, pickle.HIGHEST_PROTOCOL)) == _zz_all,
              "I: cards_state (both games, live and settled), cards_sit, cards_won, cards_won_day and mg_result hold plain values and pickle")
        check(all(isinstance(c, int) and 0 <= c < 52 for c in _zz_all[0]["deck"]) and isinstance(_zz_all[0]["deck"], builtins.list),
              "I: the deck is a list of ints")
        note("H: --prefixes", "check_content.py --all is clean with label mg_blackjack and label mg_poker in room_cards.rpy "
             "(mg_<game id> is on tools/prefixes.json's exception list); it is run outside this harness")
        note("I: saves", "saving and reloading inside `call screen cards_blackjack` is P8's p2_saves (plan 7, P8)")

    $ finish()
