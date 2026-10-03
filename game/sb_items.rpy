################################################################################
## Cursed Bonds — items, equipment and the armory.
##
## WP6 owns this file (PHASE1_DESIGN.md 3.8, 4.9, D4, D10, D11, D24).
##
##   ITEMS[id]            the catalogue: keepsakes, mission items, sealing
##                        talismans, supplies, cursed tools and worn talismans
##   give_item / take_item / has_item / item_count / items_in / add_yen
##   can_wear / equip_talisman / unequip_talisman / equip_tool (+ can_hold)
##   armory_open_now / armory_tools, label sb_do_armory, screen armory
##   sync_keepsakes()     the one path that hands out keepsakes and mission
##                        items from story flags (D24): a new-day hook, an
##                        event-done hook and migration 70
##
## Tool and talisman effects are stored in `fx` now and switched on by the
## combat update (phase 3). Nothing here changes a fight yet.
##
## Phase 2 (P4a; PHASE2_DESIGN.md D27, D28, 4.8, 4.9):
##   ITEM_REQS            what a tool or talisman asks of me, a side table
##   item_requirements / item_requirements_met / item_first_unmet
##   can_hold / can_wear  also ask the checklist, for a tool not already in my
##                        hand and a talisman not already worn (D28: nothing
##                        I already hold or wear is taken away)
##   armory_checklist     the lines the armory draws under a tool
################################################################################

init -1 python:

    import re as _items_re

    ## The catalogue (3.8) ----------------------------------------------------------
    ##
    ## id -> dict(name, kind, grade, special, sealed, stack, desc, effect, fx,
    ##            source, from_flag, hidden)
    ##   kind       keepsake | sealing | supply | mission | tool | talisman
    ##   grade      a grade key (WP2's ladder) or None
    ##   special    a special-grade talisman: bound by story, one worn at a time
    ##   sealed     None, or what unseals it ("Arc Two")
    ##   stack      more than one can be carried; otherwise the count stays at 1
    ##   desc       what it is, in my words; effect: what it does, in a line
    ##   fx         the phase-3 numbers (stored, not applied yet)
    ##   source     where it comes from, for the inventory panel
    ##   from_flag  the story flag that grants it (sync_keepsakes), or None
    ##   hidden     not listed in any catalogue until it is owned (daisy_clip)

    ITEM_KINDS = ("keepsake", "sealing", "supply", "mission", "tool", "talisman")

    ITEMS = {}

    def _item(id, name, kind, grade=None, desc="", effect="", fx=None, source="",
              from_flag=None, special=False, sealed=None, stack=False, hidden=False):
        ITEMS[id] = dict(name=name, kind=kind, grade=grade, special=special, sealed=sealed,
                         stack=stack, desc=desc, effect=effect, fx=dict(fx or {}),
                         source=source, from_flag=from_flag, hidden=hidden)

    ## Keepsakes: the one thing I packed, and what came after.
    _item("photo", "The festival photo", "keepsake",
          desc="Three years old. Sana has her arm around my neck and is pulling me out of frame. It is not a good photograph.",
          source="Packed on my last night at home.", from_flag="took_photo")
    _item("hachimaki", "Sana's hachimaki", "keepsake",
          desc="She left it at mine in October and never asked for it back. Her name is inside the band, in marker.",
          source="Packed on my last night at home.", from_flag="took_hachimaki")
    _item("watch", "My father's watch", "keepsake",
          desc="It runs four minutes fast. I have decided not to fix it.",
          source="My father, at the door. \"For the exams.\"", from_flag="took_watch")
    _item("oda_letter", "Oda-sensei's letter", "keepsake",
          desc="Small, fast handwriting I know from two years of corrected homework, and a telephone number at the bottom.",
          source="The post, from home.", from_flag="oda_letter_read")
    _item("daisy_clip", "Sana's daisy clip", "keepsake",
          desc="A plastic daisy on a hair clip. Hers.",
          source="Somewhere I didn't expect to find it.", hidden=True)

    ## Mission items: what the Nade business has put in my drawer.
    _item("kurose_card", "Kurose's card", "mission",
          desc="Auxiliary management. A name, a number, and nothing that says what the department actually does.",
          source="Kurose, outside Yaga's office.", from_flag="kurose_card")
    _item("kurose_photocopy", "The photocopied survey", "mission",
          desc="A survey of the street behind the arcade, dated April, filed as clear. A slip clipped to it, signed K.",
          source="Under my door.", from_flag="kurose_leak")
    _item("presigned_form", "A pre-signed survey form", "mission",
          desc="Blank, signed, waiting for a number.",
          source="The annexe.", from_flag="nade_traced")
    _item("nade_map", "Nade's map", "mission",
          desc="The Kanto region, eleven circles in red and a twelfth in a different hand. The twelfth is my home town.",
          source="Nade, at his door.", from_flag="nade_map")

    ## Sealing talismans and supplies: used up.
    _item("sealing_talisman", "Sealing talisman", "sealing", grade="g4", stack=True,
          desc="Paper, ink and somebody else's cursed energy. Burned in a fight, it pins a curse where it stands.",
          effect="Binds a curse in place for a turn. Used up.", fx={"bind_turns": 1},
          source="Utahime writes them. Board jobs turn them up.")
    _item("first_aid", "First-aid kit", "supply", stack=True,
          desc="Gauze, tape, and the infirmary's extension on a card in Shoko's handwriting.",
          effect="Patches me up between exchanges.", fx={"heal": 30},
          source="The infirmary (a later build).")

    ## Cursed tools: one in my hand at a time.
    _item("slaughter_demon", "Slaughter Demon", "tool", grade="g4",
          desc="A short cursed knife. It wants to be used, which is the first thing Maki warns me about.",
          effect="Strikes leave a bleed.", fx={"bleed": 3},
          source="The armory.")
    _item("nunchaku", "Nunchaku", "tool", grade="g3",
          desc="Maki's training weapon: two short staves on a chain, worn smooth where her hands go.",
          effect="Fast strikes that chain.", fx={"chain": 1},
          source="The armory.")
    _item("playful_cloud", "Playful Cloud", "tool", grade="g2",
          desc="A special-grade three-section staff, and Maki won't lend it to me before Grade 2. No technique of its own: it hits as hard as whoever swings it.",
          effect="Damage scales with raw strength.", fx={"output_scale": 1.5},
          source="Lent by Maki, at the end of her story.")
    _item("split_soul", "Split Soul Katana", "tool", grade="s1",
          desc="It cuts the soul, not the body. A curse's hide means nothing to it.",
          effect="Cuts straight through a curse's defence.", fx={"ignore_guard": 1.0},
          source="The end of Arc One (Act V).")
    _item("inverted_spear", "Inverted Spear of Heaven", "tool", grade="sp", sealed="Arc Two",
          desc="Behind glass, and behind a seal that is not in Yaga's handwriting.",
          effect="Cancels any technique it touches.", fx={"cancel_technique": 1},
          source="Sealed until Arc Two.")

    ## Worn talismans: slots grow with my grade; I can wear up to my own grade.
    _item("paper_ward", "Paper Ward", "talisman", grade="g4",
          desc="Utahime writes these herself. Tucked into a uniform, it quietly adds to what I can hold.",
          effect="+10 cursed energy reserve.", fx={"reserve": 10},
          source="Utahime.")
    _item("steady_hand", "Steady Hand", "talisman", grade="g4",
          desc="A narrow strip in Utahime's hand. It smooths the edge off every technique.",
          effect="Techniques cost a little less.", fx={"tech_cost": -0.1},
          source="Utahime.")
    _item("deep_well", "Deep Well", "talisman", grade="g3",
          desc="Heavier paper, heavier ink. It lets me hold more and give it back more slowly.",
          effect="+20 reserve; I recover a little less between fights.", fx={"reserve": 20, "recover": -0.1},
          source="Utahime.")
    _item("iron_seal", "Iron Seal", "talisman", grade="g3",
          desc="Stamped rather than written. Everything I throw lands heavier, and I stop bothering to cover.",
          effect="Strikes hit harder; guarding blocks less.", fx={"strike": 0.15, "guard": -0.15},
          source="A mission reward.")
    _item("spark", "Spark", "talisman", grade="g2",
          desc="Warm to the touch, always.",
          effect="The Black Flash timing window is a little wider.", fx={"bf_window": 0.1},
          source="Utahime, after Act III.")
    _item("held_breath", "Held Breath", "talisman", grade="g2",
          desc="Gojo drew this one. It is mostly a doodle, and it works anyway.",
          effect="Last Light costs less, and the held moment lasts one beat longer.",
          fx={"hold_cost": -0.15, "hold_beats": 1},
          source="Gojo's training.")
    ## Effect text is the storyboard's, word for word. 3.8's fx has no key yet
    ## for "the widened window lasts longer": phase 3 adds one when it applies fx.
    _item("afterglow", "Afterglow", "talisman", grade="g1",
          desc="Priced like a car. Mei Mei calls it a bargain.",
          effect="A Black Flash refills more cursed energy, and the widened window lasts longer.",
          fx={"bf_refill": 0.5},
          source="Mei Mei.")
    _item("black_sun", "Black Sun", "talisman", grade="g1",
          desc="Ink so dark it looks like a hole in the paper.",
          effect="Black Flash hits for 3x instead of 2.5x, but the window is narrower.",
          fx={"bf_mult": 3.0, "bf_window": -0.1},
          source="Mei Mei, rarely.")

    ## Special-grade talismans: legendary, one of a kind, bound by story. One worn.
    _item("unending_moment", "Unending Moment", "talisman", grade="sp", special=True,
          desc="Last Light, written down by someone who has stood outside time for longer than I have.",
          effect="Once a fight, Last Light holds for a whole round: the enemy loses two turns. Then it is gone for that fight.",
          fx={"hold_round": 1, "hold_lockout": 1},
          source="The end of Gojo's story.")
    _item("the_zone", "The Zone", "talisman", grade="sp", special=True,
          desc="Todo swears it is the only way he has ever felt about anything.",
          effect="After my first Black Flash in a fight, the window stays wide. Until then, my strikes are weaker.",
          fx={"zone": 1, "pre_zone_strike": -0.15},
          source="Todo, at the end of his story.")
    _item("finger_wrap", "Finger Wrap", "talisman", grade="sp", special=True,
          desc="The paper that once sealed one of Sukuna's fingers. It is still warm where the finger was.",
          effect="Output far beyond my grade, but Sukuna notices every fight I win with it.",
          fx={"output_mult": 2.0, "sukuna_notice": 1},
          source="Found in Act V.")
    _item("tengens_seal", "Tengen's Seal", "talisman", grade="sp", special=True, sealed="Arc Two",
          desc="A barrier folded small enough to carry.",
          effect="The first hit against me each fight is cancelled by a barrier.",
          fx={"first_hit_barrier": 1},
          source="Sealed until Arc Two.")

    ## The armory's racks (4.9), in display order: (id, "armory" | "story").
    ## "armory" tools are released up to my grade once armory_open is set;
    ## "story" tools hang there as goals and come from the story.
    ARMORY_RACK = [
        ("slaughter_demon", "armory"),
        ("nunchaku", "armory"),
        ("playful_cloud", "story"),
        ("split_soul", "story"),
        ("inverted_spear", "armory"),
    ]
    _ARMORY_KIND = dict(ARMORY_RACK)

    ## What Utahime's board can drop (3.7). WP4 keeps its own drop tables in
    ## sb_board.rpy (BOARD_SEALING, BOARD_TALISMAN_DROPS, BOARD_TOOL_DROPS, all
    ## named in BOARD_ITEM_NAMES); the validator below ties them to this tuple
    ## and this tuple to ITEMS, so a board drop the catalogue doesn't know is
    ## caught. give_item still counts an id that isn't in ITEMS (WP0's contract)
    ## without toasting it, so such a drop would reach the saved inventory;
    ## readers use ITEMS.get(id).
    BOARD_DROP_ITEMS = ("sealing_talisman", "paper_ward", "steady_hand", "deep_well", "iron_seal",
                        "slaughter_demon", "nunchaku")

    ## Lookups ----------------------------------------------------------------------

    def item_name(id):
        """WP6. The item's display name (the id itself for an unknown id)."""
        return ITEMS.get(id, {}).get("name", id)

    def all_item_ids(include_hidden=False):
        """WP6. Every catalogued id, in catalogue order. A hidden item is left
        out unless asked for or owned. For the review tools' "one of every item"."""
        return [i for i, it in ITEMS.items()
                if include_hidden or not it["hidden"] or has_item(i)]

    def _my_rank():
        ## Grade 4's rules while I'm unassessed (D16).
        return max(0, grade_rank(player_grade() or "g4"))

    ## Inventory --------------------------------------------------------------------

    def give_item(id, n=1, quiet=False):
        """WP6. Add n of an item, with a toast (kind item) unless quiet. An item
        that doesn't stack stays at one. A cursed tool goes straight into an
        empty hand. An id that isn't in ITEMS is still counted (WP0's contract
        check gives one), but never toasted, and in developer mode it is logged:
        readers of the inventory use ITEMS.get(id). Returns how many were added."""
        if n <= 0:
            return 0
        it = ITEMS.get(id)
        have = store.inventory.get(id, 0)
        if it is None:
            if config.developer:
                print("WP6 give_item: %r is not in ITEMS" % (id,))
            store.inventory[id] = have + n
            return n
        if not it["stack"]:
            n = min(n, 1 - have)
            if n <= 0:
                return 0
        store.inventory[id] = have + n
        if not quiet:
            text = item_name(id) if n == 1 else "%s ×%d" % (item_name(id), n)
            toast(text, "item", None, n)
        if it["kind"] == "tool" and store.equipped_tool is None and can_hold(id)[0]:
            equip_tool(id)
        return n

    def take_item(id, n=1):
        """WP6. Remove n of an item. False (and nothing removed) if there aren't
        enough. Taking the last one also takes it out of my hand or slot.
        n == 0 removes nothing and is True; a negative n is refused (False)."""
        if n <= 0:
            return n == 0
        have = store.inventory.get(id, 0)
        if have < n:
            return False
        if have == n:
            store.inventory.pop(id, None)
            if store.equipped_tool == id:
                equip_tool(None)
            if id in store.equipped_talismans:
                unequip_talisman(id)
        else:
            store.inventory[id] = have - n
        return True

    def has_item(id):
        """WP6. True if at least one is in the inventory."""
        return store.inventory.get(id, 0) > 0

    def item_count(id):
        """WP6. How many are in the inventory."""
        return store.inventory.get(id, 0)

    def items_in(kind):
        """WP6. The ids of owned items of a kind, in catalogue order."""
        return [i for i in ITEMS if ITEMS[i]["kind"] == kind and store.inventory.get(i, 0) > 0]

    def add_yen(n):
        """WP6. Add yen (a negative n spends it; never below zero). No toast:
        the caller says where the money came from."""
        store.yen = max(0, store.yen + int(n))

    def sync_keepsakes():
        """WP6. The one path that hands out keepsakes and mission items from
        story flags (D24). Idempotent: each grant is recorded in items_granted
        as "flag:<f>", so a later sync never grants it again, even if the item
        has been used or returned since. Runs as a new-day hook, after every
        event, and as migration 70."""
        for id, it in ITEMS.items():
            f = it["from_flag"]
            if not f or not has_flag(f):
                continue
            key = "flag:" + f
            if key in store.items_granted:
                continue
            store.items_granted.add(key)
            give_item(id)

    ## Equipment (D4) ---------------------------------------------------------------

    def _slot_reason():
        slots = talisman_slots()
        mine = GRADE_ORDER.index(grade_key(player_grade()) or "g4")
        for k in GRADE_ORDER[mine + 1:]:
            if GRADES[k].get("off_scale"):
                break
            if talisman_slots(k) > slots:
                return "No free slot — opens at " + grade_label(k)
        return "No free slot"

    def can_wear(id):
        """WP6. (ok, reason) for putting on a talisman now. The reasons, in the
        order they are checked: "Not a talisman", "Already worn",
        "Sealed — Arc Two", "Special: bound by story", "Needs Grade 2",
        "A special is already worn", "Not in my inventory",
        "No free slot — opens at Grade 3", and last (phase 2) the first line
        of its checklist that I don't meet, e.g. "Control 80 · I have 62".
        A talisman I already wear answers "Already worn" before any of that,
        so the checklist never takes one off (D28). To swap, take one off
        first."""
        it = ITEMS.get(id)
        if it is None or it["kind"] != "talisman":
            return (False, "Not a talisman")
        if id in store.equipped_talismans:
            return (False, "Already worn")
        if it["sealed"]:
            return (False, "Sealed — " + it["sealed"])
        if it["special"]:
            if id not in store.bound_specials:
                return (False, "Special: bound by story")
        elif grade_rank(it["grade"]) > _my_rank():
            return (False, "Needs " + grade_label(it["grade"]))
        if it["special"] and any(ITEMS.get(t, {}).get("special") for t in store.equipped_talismans):
            return (False, "A special is already worn")
        if not has_item(id):
            return (False, "Not in my inventory")
        if len(store.equipped_talismans) >= talisman_slots():
            return (False, _slot_reason())
        why = item_unmet_reason(id)
        if why:
            return (False, why)
        return (True, "")

    def equip_talisman(id):
        """WP6. Wear a talisman in the next free slot. True if it went on;
        False (nothing changed) when can_wear(id) refuses."""
        if not can_wear(id)[0]:
            return False
        store.equipped_talismans.append(id)
        renpy.retain_after_load()
        return True

    def unequip_talisman(id):
        """WP6. Take a talisman off; the slots after it move up. True if it was worn."""
        if id not in store.equipped_talismans:
            return False
        store.equipped_talismans.remove(id)
        renpy.retain_after_load()
        return True

    def can_hold(id):
        """WP6. (ok, reason) for taking a cursed tool in hand: "Not a cursed
        tool", "Sealed — Arc Two", "Not in my inventory", then (phase 2) the
        first line of its checklist that I don't meet ("Needs Grade 2",
        "Output 50 · I have 32"). The tool already in my hand is never asked
        (D28). None (bare hands) is always fine."""
        if id is None:
            return (True, "")
        it = ITEMS.get(id)
        if it is None or it["kind"] != "tool":
            return (False, "Not a cursed tool")
        if it["sealed"]:
            return (False, "Sealed — " + it["sealed"])
        if not has_item(id):
            return (False, "Not in my inventory")
        if store.equipped_tool != id:
            why = item_unmet_reason(id)
            if why:
                return (False, why)
        return (True, "")

    def equip_tool(id):
        """WP6. Hold a cursed tool, or None for bare hands. One tool in hand.
        True if my hand now holds it; False when can_hold(id) refuses."""
        if not can_hold(id)[0]:
            return False
        store.equipped_tool = id
        renpy.retain_after_load()
        return True

    ## The armory (D10, 4.9) --------------------------------------------------------

    def armory_open_now():
        """WP6. The armory action is offered: in the storehouse, with armory_open
        (set by Maki's The Armory, WP3)."""
        return store.here == "storehouse" and has_flag("armory_open")

    def armory_tools():
        """WP6. [(id, state, reason)] for every tool on the racks, in rack order.
        state: take | owned | sealed ("Sealed until Grade 3") | story ("Story
        reward") | arcii ("Sealed — Arc Two"). A tool sealed until Arc Two reads
        arcii even if I own it (review tools can grant it); any other owned
        tool is "owned", and its reason says whether it is in my hand.
        Phase 2 (4.9): a rack tool my grade could carry is still "sealed"
        while its checklist has an unmet line, and that line is the reason
        (an unmet grade still reads "Sealed until Grade 3")."""
        out = []
        mine = _my_rank()
        for id, rack in ARMORY_RACK:
            it = ITEMS[id]
            if it["sealed"]:
                out.append((id, "arcii", "Sealed — " + it["sealed"]))
            elif has_item(id):
                out.append((id, "owned", "In my hand" if store.equipped_tool == id else "Owned"))
            elif rack == "story":
                out.append((id, "story", "Story reward"))
            elif grade_rank(it["grade"]) > mine:
                out.append((id, "sealed", "Sealed until " + grade_label(it["grade"])))
            else:
                unmet = item_first_unmet(id)
                if unmet is None:
                    out.append((id, "take", ""))
                elif unmet[0][0] == "grade":
                    out.append((id, "sealed", "Sealed until " + unmet[1]))
                else:
                    out.append((id, "sealed", unmet[1]))
        return out

    def armory_state(id):
        """WP6. The (state, reason) that armory_tools() gives one tool."""
        for i, s, r in armory_tools():
            if i == id:
                return (s, r)
        return (None, "")

    def armory_take(id):
        """WP6. Take a released tool off the rack and into my hand: choosing it
        from the rack is choosing to carry it (the tool it replaces stays in my
        inventory). True if taken."""
        if armory_state(id)[0] != "take":
            return False
        if give_item(id, quiet=True) <= 0:
            return False
        equip_tool(id)
        toast("%s — in my hand" % item_name(id), "item", None, 1)
        return True

    def armory_return(id):
        """WP6. Hang an armory tool back on its rack. Story tools stay mine.
        If it was in my hand, the next tool I own (in rack order) takes its
        place, so my hand is only empty when I own no other tool. True if
        returned."""
        if _ARMORY_KIND.get(id) != "armory" or not has_item(id):
            return False
        was_held = store.equipped_tool == id
        take_item(id, item_count(id))
        nxt = None
        if was_held:
            for other, rack in ARMORY_RACK:
                if other != id and can_hold(other)[0]:
                    nxt = other
                    break
            if nxt:
                equip_tool(nxt)
        if nxt:
            toast("%s — back on the rack; %s in my hand" % (item_name(id), item_name(nxt)), "item")
        else:
            toast("%s — back on the rack" % item_name(id), "item")
        return True

    ## Registration -----------------------------------------------------------------

    register_place_action("armory", "Armory", "Cursed tools, released up to my grade.",
                          locs=("storehouse",), when="armory_open_now")

    register_new_day(sync_keepsakes, order=70)
    register_event_done(lambda e: sync_keepsakes())
    register_migration(70, sync_keepsakes, "keepsakes and mission items from flags (WP6)")

    ## Requirements (phase 2: PHASE2_DESIGN.md D27, D28, 4.9) -----------------------
    ##
    ## A side table, so ITEMS records keep their twelve fields.
    ## id -> [requirement], each one of
    ##   ("grade", key)          my grade is at least this
    ##   ("arc", n)              the story has reached arc n
    ##   ("flag", name, words)   a story flag; words is how the checklist says it
    ##   ("stat", name, n)       control, output or insight is at least n
    ## P0 wrote the validator; P4a the rows (the three tools and the two Grade 1
    ## talismans) and the functions that read them; sb_market.rpy adds its
    ## four with ITEM_REQS.update(...).

    ITEM_REQS = {
        ## Cursed tools (D27).
        "inverted_spear": [("arc", 2), ("grade", "sp"),
                           ("flag", "spear_unsealed", "The seal broken"),
                           ("flag", "yaga_signature", "Yaga's signature")],
        "playful_cloud": [("grade", "g2"), ("stat", "output", 50)],
        "split_soul": [("grade", "s1"), ("stat", "insight", 60)],
        ## The two Grade 1 talismans (D27). The market's four are added by
        ## sb_market.rpy.
        "afterglow": [("grade", "g1"), ("stat", "control", 80)],
        "black_sun": [("grade", "g1"), ("stat", "output", 80)],
    }

    ITEM_REQ_STATS = ("control", "output", "insight")

    ## How a checklist names an arc.
    ITEM_ARC_NAMES = {1: "Arc One", 2: "Arc Two", 3: "Arc Three"}

    def item_req_line(r):
        """P4a (sb_items.rpy). One requirement as (line, met): "Grade 2",
        "Arc Two", a flag's words, "Output 50", and for a stat I'm short of
        "Output 50 · I have 32". A row that is none of the four kinds reads
        as unmet (the validator reports it)."""
        try:
            kind = r[0]
            if kind == "grade":
                return (grade_label(r[1]), _my_rank() >= grade_rank(r[1]) >= 0)
            if kind == "arc":
                return (ITEM_ARC_NAMES.get(r[1], "Arc %s" % (r[1],)), store.arc >= r[1])
            if kind == "flag":
                return (str(r[2]), has_flag(r[1]))
            if kind == "stat":
                have = getattr(store, r[1])
                line = "%s %d" % (r[1].capitalize(), r[2])
                if have >= r[2]:
                    return (line, True)
                return ("%s · I have %d" % (line, have), False)
        except Exception:
            pass
        return ("?", False)

    def item_requirements(id):
        """P4a (sb_items.rpy). A list of (str, bool): each requirement of an
        item as a line and whether I meet it, in the order of its ITEM_REQS
        row. [] for an item with no row."""
        return [item_req_line(r) for r in ITEM_REQS.get(id, ())]

    def item_requirements_met(id):
        """P4a (sb_items.rpy). bool: I meet every requirement of the item
        (True for an item with no row)."""
        return all(ok for line, ok in item_requirements(id))

    def item_first_unmet(id):
        """P4a (sb_items.rpy). The first requirement I don't meet, as
        (requirement, line), or None when I meet them all."""
        for r in ITEM_REQS.get(id, ()):
            line, ok = item_req_line(r)
            if not ok:
                return (r, line)
        return None

    def item_unmet_reason(id):
        """P4a (sb_items.rpy). Why can_hold / can_wear refuse on the
        checklist: the first unmet line, or "" when there is none. An unmet
        grade reads "Needs Grade 2", as can_wear's own grade test does."""
        unmet = item_first_unmet(id)
        if unmet is None:
            return ""
        if unmet[0] and unmet[0][0] == "grade":
            return "Needs " + unmet[1]
        return unmet[1]

    def armory_checklist(id):
        """P4a (sb_items.rpy). The (line, met) pairs the armory draws under a
        tool: item_requirements(id), or, for a tool with no row, the one
        thing the racks ask: its grade."""
        rows = item_requirements(id)
        if rows:
            return rows
        g = ITEMS.get(id, {}).get("grade")
        if g is None:
            return []
        return [(grade_label(g), _my_rank() >= grade_rank(g))]

    def item_validate_reqs():
        """P0 (sb_items.rpy), final (D27). A list of str findings over every
        row of ITEM_REQS, whichever file added it: the item exists; each
        requirement is one of the four kinds; a Control or Output threshold
        is reachable under the item's own grade cap (GRADES[grade]["stat"]);
        an Insight threshold is at most 100; a flag has words. [] while the
        table is empty. A registered validator: lint prints each finding."""
        out = []
        for id in sorted(ITEM_REQS):
            it = ITEMS.get(id)
            if it is None:
                out.append("ITEM_REQS: %r is not an item" % (id,))
                continue
            reqs = ITEM_REQS[id]
            if not isinstance(reqs, (list, tuple)):
                out.append("ITEM_REQS[%r] must be a list of requirements" % (id,))
                continue
            g = grade_key(it.get("grade"))
            cap = GRADES[g]["stat"] if g else None
            for r in reqs:
                if not isinstance(r, (list, tuple)) or not r:
                    out.append("ITEM_REQS[%r]: %r is not a requirement" % (id, r))
                    continue
                kind = r[0]
                if kind == "grade":
                    if len(r) != 2 or r[1] not in GRADES:
                        out.append("ITEM_REQS[%r]: %r is not a grade requirement" % (id, r))
                elif kind == "arc":
                    if len(r) != 2 or not isinstance(r[1], int) or isinstance(r[1], bool) or r[1] < 1:
                        out.append("ITEM_REQS[%r]: %r is not an arc requirement" % (id, r))
                elif kind == "flag":
                    if len(r) != 3 or not (isinstance(r[1], str) and r[1]):
                        out.append("ITEM_REQS[%r]: %r is not a flag requirement" % (id, r))
                    elif not (isinstance(r[2], str) and r[2].strip()):
                        out.append("ITEM_REQS[%r]: the flag %r has no words" % (id, r[1]))
                elif kind == "stat":
                    if (len(r) != 3 or r[1] not in ITEM_REQ_STATS
                            or not isinstance(r[2], int) or isinstance(r[2], bool)):
                        out.append("ITEM_REQS[%r]: %r is not a stat requirement" % (id, r))
                    elif r[1] == "insight":
                        if r[2] > 100:
                            out.append("ITEM_REQS[%r]: Insight %d is above 100" % (id, r[2]))
                    elif cap is not None and r[2] > cap:
                        out.append("ITEM_REQS[%r]: %s %d is above %s's cap of %d"
                                   % (id, r[1].capitalize(), r[2], grade_label(g), cap))
                    elif r[2] > 100:
                        out.append("ITEM_REQS[%r]: %s %d is above 100" % (id, r[1].capitalize(), r[2]))
                else:
                    out.append("ITEM_REQS[%r]: unknown requirement kind %r" % (id, kind))
        return out

    register_validator(item_validate_reqs)

    ## The validator (lint) ---------------------------------------------------------

    _ITEM_FIELDS = ("name", "kind", "grade", "special", "sealed", "stack", "desc",
                    "effect", "fx", "source", "from_flag", "hidden")

    ## A literal item id passed to one of the item functions in a script.
    _ITEM_CALL_RE = _items_re.compile(
        r"\b(?:give_item|take_item|has_item|item_count|equip_tool|equip_talisman|"
        r"unequip_talisman|can_wear|can_hold|armory_take|armory_return)\(\s*[\"']([A-Za-z0-9_]+)[\"']")

    def _mission_item_ids():
        out = []
        for m in getattr(store, "MISSIONS", None) or ():
            rw = m.get("rewards") if isinstance(m, dict) else getattr(m, "rewards", None)
            its = rw.get("items") if isinstance(rw, dict) else None
            mid = m.get("id") if isinstance(m, dict) else getattr(m, "id", "?")
            for i in (its or ()):
                out.append((mid, i))
        return out

    def _validate_items():
        out = []
        for id, it in ITEMS.items():
            missing = [f for f in _ITEM_FIELDS if f not in it]
            if missing:
                out.append("item %r is missing %s" % (id, ", ".join(missing)))
                continue
            if it["kind"] not in ITEM_KINDS:
                out.append("item %r has an unknown kind %r" % (id, it["kind"]))
            if it["grade"] is not None and grade_key(it["grade"]) != it["grade"]:
                out.append("item %r has an unknown grade %r" % (id, it["grade"]))
            if it["kind"] in ("tool", "talisman", "sealing") and it["grade"] is None:
                out.append("item %r (%s) needs a grade" % (id, it["kind"]))
            if it["special"] and (it["kind"] != "talisman" or it["grade"] != "sp"):
                out.append("item %r: only special-grade talismans are special" % id)
            if it["from_flag"] and it["kind"] not in ("keepsake", "mission"):
                out.append("item %r: only keepsakes and mission items come from a flag" % id)
            if it["stack"] and it["kind"] not in ("sealing", "supply"):
                out.append("item %r: only sealing talismans and supplies stack" % id)
            if not isinstance(it["fx"], dict):
                out.append("item %r: fx must be a dict" % id)
        for id, rack in ARMORY_RACK:
            if ITEMS.get(id, {}).get("kind") != "tool":
                out.append("armory rack: %r is not a cursed tool" % id)
            if rack not in ("armory", "story"):
                out.append("armory rack: %r has an unknown rack kind %r" % (id, rack))
        for id, it in ITEMS.items():
            if it.get("kind") == "tool" and id not in _ARMORY_KIND:
                out.append("cursed tool %r is not on the armory rack" % id)
        for id in BOARD_DROP_ITEMS:
            if id not in ITEMS:
                out.append("board drop %r is not in ITEMS" % id)
        for id in getattr(store, "BOARD_ITEM_NAMES", {}):
            if id not in BOARD_DROP_ITEMS:
                out.append("board can drop %r but BOARD_DROP_ITEMS doesn't list it" % id)
        for mid, id in _mission_item_ids():
            if id not in ITEMS:
                out.append("mission %s rewards an unknown item %r" % (mid, id))
        try:
            files = [f for f in renpy.list_files() if f.endswith(".rpy")]
        except Exception:
            files = []
        for fn in files:
            try:
                with renpy.open_file(fn, encoding="utf-8") as f:
                    src = f.read()
            except Exception:
                continue
            for lineno, line in enumerate(src.splitlines(), 1):
                for id in _ITEM_CALL_RE.findall(line):
                    if id not in ITEMS:
                        out.append("%s:%d uses an unknown item %r" % (fn, lineno, id))
        return out

    register_validator(_validate_items)


## The armory (4.9) #############################################################
##
## Reached from the storehouse once Maki has opened the racks (armory_open).
## Taking and returning cost no time.

label sb_do_armory:
    if not armory_open_now():
        return
    while True:
        call screen armory
        if not isinstance(_return, tuple) or not _return or _return[0] == "close":
            return
        elif _return[0] == "take":
            $ armory_take(_return[1])
        elif _return[0] == "return":
            $ armory_return(_return[1])
    return


style armory_row is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (26, 7)
    xfill True

style armory_name is text:
    font gui.display_font
    color gui.paper
    size 27

style armory_desc is text:
    color gui.dim
    size 19

style armory_effect is text:
    font gui.body_medium_font
    color gui.violet2
    size 18

style armory_state is text:
    font gui.body_medium_font
    size 20
    xalign 1.0
    yalign 0.5
    text_align 1.0


style armory_req_frame is frame:
    background Frame("gui/panel_ghost.png", 4, 4)
    padding (10, 2)

style armory_req_text is text:
    font gui.body_medium_font
    size 16

## P4a. One line of a checklist as a chip: a tick and the line in paper when
## I meet it, a cross and the line in seal red when I don't. The marks need
## the symbol font (JR_SYMBOL_FONT, ui_journal.rpy).
screen armory_req(line, met):
    frame:
        style "armory_req_frame"
        hbox:
            spacing 6
            text ("✓" if met else "✗"):
                font JR_SYMBOL_FONT
                size 15
                yalign 0.5
                color (gui.paper if met else gui.seal)
            text line:
                style "armory_req_text"
                substitute False
                yalign 0.5
                color (gui.paper if met else gui.seal)


## The racks: one row per tool, with Take / Return or why not. Returns
## ("take", id), ("return", id) or ("close",).
screen armory():

    tag sandbox

    $ _rows = armory_tools()
    $ _hand = item_name(equipped_tool) if equipped_tool else "Bare hands"
    $ _mine = grade_label(player_grade() or "g4").upper()
    $ _mykey = grade_key(player_grade()) or "g4"

    add graded_bg("storehouse")
    add Solid(gui.ink) alpha 0.62

    key "game_menu" action Return(("close",))

    frame:
        style "jjk_panel"
        xpos 110
        ypos 30
        xsize 1700

        vbox:
            spacing 5

            fixed:
                ysize 76
                hbox:
                    spacing 18
                    yalign 0.5
                    use seal("具", 44)
                    vbox:
                        spacing 2
                        text "The Armory" font gui.display_font size 44 color gui.paper
                        text "The racks release what my grade can carry. The rest stays sealed." style "jjk_small"
                vbox:
                    xalign 1.0
                    yalign 0.5
                    spacing 4
                    hbox:
                        xalign 1.0
                        spacing 12
                        text "MY GRADE" style "jjk_label" yalign 0.5 color gui.gold
                        use grade_chip(_mykey, 14)
                    text "In my hand: " + _hand style "jjk_value" size 22 xalign 1.0

            use rule()

            for _id, _st, _why in _rows:
                $ _it = ITEMS[_id]
                $ _open = _st in ("take", "owned")
                $ _rack = _ARMORY_KIND.get(_id)
                $ _reqs = armory_checklist(_id)

                frame:
                    style "armory_row"
                    background Frame(("gui/panel_gold.png" if _st == "take" else "gui/panel_dark.png"), 4, 4)

                    hbox:
                        spacing 28
                        yalign 0.5

                        ## The tool's grade, in its colour; dim while sealed (4.8).
                        frame:
                            background None
                            xsize 190
                            yalign 0.5
                            padding (0, 0)
                            hbox:
                                xalign 0.5
                                use grade_chip(_it["grade"], 15, dim=(_st in ("sealed", "arcii")))

                        vbox:
                            xsize 990
                            yalign 0.5
                            spacing 2
                            text _it["name"] style "armory_name" color (gui.paper if (_open or _st == "story") else gui.dim)
                            text _it["desc"] style "armory_desc"
                            text _it["effect"] style "armory_effect"
                            ## The checklist (4.9): what it asks of me, ticked or not.
                            if _reqs:
                                hbox:
                                    box_wrap True
                                    box_wrap_spacing 4
                                    spacing 8
                                    for _line, _met in _reqs:
                                        use armory_req(_line, _met)

                        fixed:
                            xsize 290
                            ysize 86
                            yalign 0.5
                            if _st == "take":
                                textbutton "Take":
                                    style "jjk_button"
                                    xsize 220
                                    xalign 1.0
                                    yalign 0.5
                                    text_color gui.gold
                                    text_hover_color gui.paper
                                    text_xalign 0.5
                                    action Return(("take", _id))
                            elif _st == "owned" and _rack == "armory":
                                vbox:
                                    xalign 1.0
                                    yalign 0.5
                                    spacing 6
                                    textbutton "Return":
                                        style "jjk_button"
                                        xsize 220
                                        xalign 1.0
                                        text_xalign 0.5
                                        action Return(("return", _id))
                                    text _why style "armory_state" size 16 color gui.dim
                            elif _st == "owned":
                                text _why style "armory_state" color gui.gold
                            elif _st == "story":
                                text _why style "armory_state" color gui.dim
                            else:
                                text _why style "armory_state" color gui.seal

    text "Tools take effect in combat from the combat update. I change what I hold in the journal, under Equipment.":
        style "jjk_small"
        xpos 110
        ypos 1000
        yanchor 0.5

    textbutton "Close":
        style "jjk_button"
        xsize 220
        xanchor 1.0
        xpos 1810
        ypos 1000
        yanchor 0.5
        text_xalign 0.5
        action Return(("close",))


default inventory = {}
default items_granted = set()
default yen = 0
default equipped_tool = None
default equipped_talismans = []
default bound_specials = set()
