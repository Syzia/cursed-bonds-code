################################################################################
## Cursed Bonds — the Black Market.
##
## Phase 2 (PHASE2_DESIGN.md 4.16, D24, D27, D29, 6.1). P4b.
##
## A folding table under a paper lantern, one floor below a club in Shibuya.
## Found on the first club night there (or from a rumour on my computer), and
## visited on a night in Tokyo (sb_night.rpy). It sells four talismans of its
## own, sealing talismans and first aid, for a lot of yen.
##
## It sells no Special Grade talisman (the owner's answer, 1 Oct 2026), and
## it never touches bound_specials. Effects are stored in `fx` and switched
## on by the combat update (phase 3), like every other talisman's.
##
## Saves (2.3): `call screen market_screen` and the `$ _market_r = _return`
## after it stay textually identical.
##
## This file sorts after sb_items.rpy at init -1, which _item() and
## ITEM_REQS.update() need.
################################################################################

init -1 python:

    ## The market's own talismans (3.1): twelve fields each, through _item().
    _item("borrowed_luck", "Borrowed Luck", "talisman", grade="g3",
          desc="A pawn ticket folded into a talisman. Whatever luck it draws on belongs to somebody else.",
          effect="Once a fight, the hit that would put me down leaves me standing.",
          fx={"last_stand": 1},
          source="The Black Market")
    _item("night_eyes", "Night Eyes", "talisman", grade="g3",
          desc="The ink was mixed with something that used to see in the dark. It still tries to.",
          effect="I read a curse's next move a beat early.",
          fx={"read_ahead": 1},
          source="The Black Market")
    _item("debt_marker", "Debt Marker", "talisman", grade="g2",
          desc="An IOU with no name on it. The interest is paid in cursed energy.",
          effect="Techniques hit harder, and each one costs a little more.",
          fx={"tech_power": 0.2, "tech_cost": 0.1},
          source="The Black Market")
    _item("second_wind", "Second Wind", "talisman", grade="s1",
          desc="Folded so many times the creases have gone soft. Somebody leaned on this one for years.",
          effect="Once a fight, at half health, my reserve comes back.",
          fx={"second_wind": 1},
          source="The Black Market")

    ## What each of them asks of me (D27), in sb_items.rpy's ITEM_REQS.
    ITEM_REQS.update({
        "borrowed_luck": [("grade", "g3"), ("stat", "insight", 30)],
        "night_eyes":    [("grade", "g3"), ("stat", "insight", 35)],
        "debt_marker":   [("grade", "g2"), ("stat", "control", 50)],
        "second_wind":   [("grade", "s1"), ("stat", "output", 60)],
    })

    ## What is on the table (4.16), in display order. once: one only.
    MARKET_STOCK = [
        dict(item="borrowed_luck",    price=9000,  once=True),
        dict(item="night_eyes",       price=12000, once=True),
        dict(item="debt_marker",      price=24000, once=True),
        dict(item="second_wind",      price=45000, once=True),
        dict(item="sealing_talisman", price=800,   once=False),
        dict(item="first_aid",        price=500,   once=False),
    ]

    ## Outfits: dict(name, files). A row shows only once every one of its
    ## sprite files exists; none is drawn yet, so the shelf is empty.
    MARKET_OUTFITS = []

    ## The highest grade the market sells: the highest Arc One reaches (D29).
    MARKET_TOP_GRADE = "s1"

    def market_exists():
        """P4b (sb_market.rpy). bool: the market is built."""
        return True

    def market_price_cap(id):
        """P4b. int: the most the market may ask for an item (D29): three top
        board jobs at its grade; Grade 1 uses the Semi-Grade 1 row (the board
        has no Grade 1 jobs); Special Grade is six of those; an ungraded
        supply is one low Grade 4 job."""
        g = grade_key((ITEMS.get(id) or {}).get("grade"))
        if g is None:
            return BOARD_YEN["g4"][0]
        if g == "sp":
            return 6 * BOARD_YEN["s1"][1]
        if g not in BOARD_YEN:
            g = "s1"
        return 3 * BOARD_YEN[g][1]

    def market_row(id):
        """P4b. The MARKET_STOCK row of an item, or None."""
        for r in MARKET_STOCK:
            if r["item"] == id:
                return r
        return None

    def market_state(r):
        """P4b. (state, reason) of a stock row: ("buy", ""),
        ("sold", "Sold") or ("poor", "Can't afford it"). Sold means bought
        here (market_bought), not merely owned: the review tools' "Grant one
        of every item" leaves the table as it was."""
        if r["once"] and r["item"] in store.market_bought:
            return ("sold", "Sold")
        if store.yen < r["price"]:
            return ("poor", "Can't afford it")
        return ("buy", "")

    def market_rows():
        """P4b. A list of (id, price, state, reason), one per stock row, in
        display order; state is "buy", "sold" or "poor"."""
        out = []
        for r in MARKET_STOCK:
            if r["item"] not in ITEMS:
                continue
            state, reason = market_state(r)
            out.append((r["item"], r["price"], state, reason))
        return out

    def market_buy(id):
        """P4b. bool: the item was bought (yen spent, item given). False,
        with nothing changed, when it isn't stock, is sold, or costs more
        than I have. It never touches bound_specials."""
        r = market_row(id)
        if r is None or r["item"] not in ITEMS:
            return False
        if market_state(r)[0] != "buy" or store.yen < r["price"]:
            return False
        add_yen(-r["price"])
        give_item(id)
        if r["once"]:
            store.market_bought.add(id)
        return True

    def market_outfits():
        """P4b. The MARKET_OUTFITS rows whose sprite files all exist."""
        return [o for o in MARKET_OUTFITS
                if o.get("files") and all(renpy.loadable(f) for f in o["files"])]

    def market_yen(n):
        """P4b. "¥12,000"."""
        return "¥{:,}".format(int(n))

    def market_validate():
        """P4b, a registered validator (D29). Every stock row names an item
        once, with a price above zero and at most market_price_cap(); nothing
        special, sealed or graded above MARKET_TOP_GRADE is sold; every
        talisman on the table has its checklist in ITEM_REQS."""
        out = []
        seen = set()
        for r in MARKET_STOCK:
            id = r.get("item")
            it = ITEMS.get(id)
            if it is None:
                out.append("MARKET_STOCK: %r is not an item" % (id,))
                continue
            if id in seen:
                out.append("MARKET_STOCK: %r is listed twice" % (id,))
            seen.add(id)
            p = r.get("price")
            if not isinstance(p, int) or isinstance(p, bool) or p <= 0:
                out.append("MARKET_STOCK: %r needs a price above zero" % (id,))
            elif p > market_price_cap(id):
                out.append("MARKET_STOCK: %r costs %d, above its ceiling of %d" % (id, p, market_price_cap(id)))
            if not isinstance(r.get("once"), bool):
                out.append("MARKET_STOCK: %r needs once=True or False" % (id,))
            elif not r["once"] and not it["stack"]:
                out.append("MARKET_STOCK: %r doesn't stack, so it can only be sold once" % (id,))
            if it["special"] or grade_key(it["grade"]) == "sp":
                out.append("MARKET_STOCK: %r is Special Grade; the market sells none" % (id,))
            elif it["sealed"]:
                out.append("MARKET_STOCK: %r is sealed" % (id,))
            elif grade_rank(it["grade"]) > grade_rank(MARKET_TOP_GRADE):
                out.append("MARKET_STOCK: %r is %s, above %s" % (id, grade_label(it["grade"]), grade_label(MARKET_TOP_GRADE)))
            if it["kind"] == "talisman" and not ITEM_REQS.get(id):
                out.append("MARKET_STOCK: the talisman %r has no ITEM_REQS row" % (id,))
        for o in MARKET_OUTFITS:
            if not isinstance(o, dict) or not o.get("name") or not o.get("files"):
                out.append("MARKET_OUTFITS: %r needs a name and its sprite files" % (o,))
        return out

    register_validator(market_validate)


style market_row is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (26, 6)
    xfill True

style market_name is text:
    font gui.display_font
    color gui.paper
    size 26

style market_desc is text:
    color gui.dim
    size 19

style market_effect is text:
    font gui.body_medium_font
    color gui.violet2
    size 18

style market_price is text:
    font gui.body_medium_font
    color gui.gold
    size 24

style market_reason is text:
    font gui.body_medium_font
    color gui.seal
    size 18

## (A style, not a font on the text itself: styles get the font group that
## carries the tick, screens.rpy.)
style market_chip is text:
    font gui.body_medium_font
    color gui.dim
    size 15


## One requirement of a talisman, as the armory and the journal draw it
## (D27, 4.16): a tick in paper when it is met, a cross in seal red when not.
## The mark is its own text in DejaVu Sans: the game's fonts and their font
## group have no cross.
screen market_req(line, met):
    frame:
        background Frame("gui/panel_ghost.png", 4, 4)
        padding (10, 3)
        yalign 0.5
        hbox:
            spacing 6
            text ("✓" if met else "✗"):
                font "DejaVuSans.ttf"
                size 15
                yalign 0.5
                color (gui.paper if met else gui.seal)
            text line:
                style "market_chip"
                substitute False
                yalign 0.5
                color (gui.paper if met else gui.seal)


## The table: one row per stock item, with Buy or why not. Returns
## ("buy", id) or ("close",). Under the test harness's autoplay it closes
## itself.
screen market_screen():

    tag sandbox

    $ _market_list = market_rows()
    $ _market_shelf = market_outfits()

    add night_bg(NIGHT_OUT["market"])
    add Solid(gui.ink) alpha 0.72

    key "game_menu" action Return(("close",))

    if smoke_autoplay:
        timer 0.05 action Return(("close",))

    frame:
        style "jjk_panel"
        xpos 110
        ypos 36
        xsize 1700
        ypadding 20

        vbox:
            spacing 6

            fixed:
                ysize 76
                hbox:
                    spacing 18
                    yalign 0.5
                    use seal("市", 44)
                    vbox:
                        spacing 2
                        text "The Black Market" font gui.display_font size 40 color gui.paper
                        text "A folding table under a paper lantern. Cash, and no questions either way." style "jjk_small"
                vbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 4
                    text "MY YEN" style "jjk_label" xalign 1.0 color gui.gold
                    text market_yen(yen) style "jjk_value" size 30 xalign 1.0 color gui.gold

            use rule()

            for _id, _price, _st, _why in _market_list:
                $ _it = ITEMS[_id]
                $ _reqs = item_requirements(_id)

                frame:
                    style "market_row"
                    background Frame(("gui/panel_gold.png" if _st == "buy" else "gui/panel_dark.png"), 4, 4)

                    hbox:
                        spacing 26
                        yalign 0.5

                        fixed:
                            xsize 170
                            ysize 30
                            yalign 0.5
                            if _it["grade"]:
                                use grade_chip(_it["grade"], 14, dim=(_st == "sold"))
                            else:
                                text "SUPPLY" style "jjk_label" size 14 color gui.mute yalign 0.5

                        vbox:
                            xsize 1040
                            yalign 0.5
                            spacing 1
                            hbox:
                                spacing 14
                                text _it["name"] style "market_name" color (gui.dim if _st == "sold" else gui.paper) yalign 0.5
                                for _line, _met in _reqs:
                                    use market_req(_line, _met)
                            text _it["desc"] style "market_desc"
                            text _it["effect"] style "market_effect"

                        fixed:
                            xsize 300
                            ysize 72
                            yalign 0.5
                            if _st == "buy":
                                hbox:
                                    xalign 1.0
                                    yalign 0.5
                                    spacing 18
                                    text market_yen(_price) style "market_price" yalign 0.5
                                    textbutton "Buy":
                                        id "market_buy_" + _id
                                        style "jjk_button"
                                        xsize 130
                                        yalign 0.5
                                        text_color gui.gold
                                        text_hover_color gui.paper
                                        text_xalign 0.5
                                        action Return(("buy", _id))
                            else:
                                vbox:
                                    xalign 1.0
                                    yalign 0.5
                                    spacing 2
                                    text market_yen(_price) style "market_price" xalign 1.0 color (gui.mute if _st == "sold" else gui.dim)
                                    text _why style "market_reason" xalign 1.0 color (gui.mute if _st == "sold" else gui.seal)

            if _market_shelf:
                text "On the shelf behind him: " + ", ".join(o["name"] for o in _market_shelf) + ".":
                    style "jjk_small"

    text "Effects wake up with the combat update.":
        style "jjk_small"
        xpos 110
        ypos 1000
        yanchor 0.5

    textbutton "Close":
        id "market_close"
        style "jjk_button"
        xsize 220
        xanchor 1.0
        xpos 1810
        ypos 1000
        yanchor 0.5
        text_xalign 0.5
        action Return(("close",))


## The market, open: buy until I close it. Costs no time of its own (the
## night it is visited on does, sb_night.rpy).
label market_open:
    if not market_exists():
        return
    while True:
        call screen market_screen
        $ _market_r = _return
        if not isinstance(_market_r, tuple) or not _market_r or _market_r[0] == "close":
            return
        elif _market_r[0] == "buy":
            $ market_buy(_market_r[1])
    return


## Market state (3.3).
default market_bought = set()    # once-only stock already bought
