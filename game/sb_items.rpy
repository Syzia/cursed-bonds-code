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
## combat update (phase 2). Nothing here changes a fight yet.
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
    ##   fx         the phase-2 numbers (stored, not applied yet)
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
          desc="A three-section staff of special grade. No technique of its own: it hits as hard as whoever swings it.",
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

    ## What Utahime's board can drop (3.7), checked by the validator.
    BOARD_DROP_ITEMS = ("sealing_talisman", "paper_ward", "steady_hand", "deep_well", "iron_seal")

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
        empty hand. Returns how many were added."""
        if n <= 0:
            return 0
        it = ITEMS.get(id)
        have = store.inventory.get(id, 0)
        if it is not None and not it["stack"]:
            n = min(n, 1 - have)
            if n <= 0:
                return 0
        store.inventory[id] = have + n
        if not quiet:
            text = item_name(id) if n == 1 else "%s ×%d" % (item_name(id), n)
            toast(text, "item", None, n)
        if it is not None and it["kind"] == "tool" and store.equipped_tool is None and can_hold(id)[0]:
            equip_tool(id)
        return n

    def take_item(id, n=1):
        """WP6. Remove n of an item. False (and nothing removed) if there aren't
        enough. Taking the last one also takes it out of my hand or slot."""
        have = store.inventory.get(id, 0)
        if have < n:
            return False
        if have == n:
            del store.inventory[id]
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
        "No free slot — opens at Grade 3". To swap, take one off first."""
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
        tool", "Sealed — Arc Two", "Not in my inventory". None (bare hands)
        is always fine."""
        if id is None:
            return (True, "")
        it = ITEMS.get(id)
        if it is None or it["kind"] != "tool":
            return (False, "Not a cursed tool")
        if it["sealed"]:
            return (False, "Sealed — " + it["sealed"])
        if not has_item(id):
            return (False, "Not in my inventory")
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
        reward") | arcii ("Sealed — Arc Two"). An owned tool is "owned" whatever
        else is true of it; its reason says whether it is in my hand."""
        out = []
        mine = _my_rank()
        for id, rack in ARMORY_RACK:
            it = ITEMS[id]
            if has_item(id):
                out.append((id, "owned", "In my hand" if store.equipped_tool == id else "Owned"))
            elif it["sealed"]:
                out.append((id, "arcii", "Sealed — " + it["sealed"]))
            elif rack == "story":
                out.append((id, "story", "Story reward"))
            elif grade_rank(it["grade"]) > mine:
                out.append((id, "sealed", "Sealed until " + grade_label(it["grade"])))
            else:
                out.append((id, "take", ""))
        return out

    def armory_state(id):
        """WP6. The (state, reason) that armory_tools() gives one tool."""
        for i, s, r in armory_tools():
            if i == id:
                return (s, r)
        return (None, "")

    def armory_take(id):
        """WP6. Take a released tool off the rack (it goes into an empty hand).
        True if taken."""
        if armory_state(id)[0] != "take":
            return False
        return give_item(id) > 0

    def armory_return(id):
        """WP6. Hang an armory tool back on its rack. Story tools stay mine.
        True if returned."""
        if _ARMORY_KIND.get(id) != "armory" or not has_item(id):
            return False
        take_item(id, item_count(id))
        toast("%s — back on the rack" % item_name(id), "item")
        return True

    ## Registration -----------------------------------------------------------------

    register_place_action("armory", "Armory", "Cursed tools released at your grade.",
                          locs=("storehouse",), when="armory_open_now")

    register_new_day(sync_keepsakes, order=70)
    register_event_done(lambda e: sync_keepsakes())
    register_migration(70, sync_keepsakes, "keepsakes and mission items from flags (WP6)")

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
        $ _armory_r = _return
        if not isinstance(_armory_r, tuple) or not _armory_r or _armory_r[0] == "close":
            return
        elif _armory_r[0] == "take":
            $ armory_take(_armory_r[1])
        elif _armory_r[0] == "return":
            $ armory_return(_armory_r[1])
    return


style armory_row is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (26, 12)
    xfill True

style armory_name is text:
    font gui.display_font
    color gui.paper
    size 30

style armory_desc is text:
    color gui.dim
    size 20

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


## The racks: one row per tool, with Take / Return or why not. Returns
## ("take", id), ("return", id) or ("close",).
screen armory():

    tag sandbox

    $ _rows = armory_tools()
    $ _hand = item_name(equipped_tool) if equipped_tool else "Bare hands"
    $ _mine = grade_label(player_grade() or "g4").upper()

    add graded_bg("storehouse")
    add Solid(gui.ink) alpha 0.62

    key "game_menu" action Return(("close",))

    frame:
        style "jjk_panel"
        xpos 110
        ypos 36
        xsize 1700

        vbox:
            spacing 10

            fixed:
                ysize 84
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
                    text "MY GRADE  ·  " + _mine style "jjk_label" xalign 1.0 color gui.gold
                    text "In my hand: " + _hand style "jjk_value" size 22 xalign 1.0

            use rule()

            for _id, _st, _why in _rows:
                $ _it = ITEMS[_id]
                $ _open = _st in ("take", "owned")
                $ _rack = _ARMORY_KIND.get(_id)

                frame:
                    style "armory_row"
                    background Frame(("gui/panel_gold.png" if _st == "take" else "gui/panel_dark.png"), 4, 4)

                    hbox:
                        spacing 28
                        yalign 0.5

                        frame:
                            background Frame("gui/panel_ghost.png", 4, 4)
                            xsize 190
                            yalign 0.5
                            padding (10, 10)
                            text grade_label(_it["grade"]).upper():
                                style "jjk_label"
                                size 16
                                xalign 0.5
                                text_align 0.5
                                color (gui.gold if _open else gui.mute)

                        vbox:
                            xsize 990
                            yalign 0.5
                            spacing 4
                            text _it["name"] style "armory_name" color (gui.paper if (_open or _st == "story") else gui.dim)
                            text _it["desc"] style "armory_desc"
                            text _it["effect"] style "armory_effect"

                        fixed:
                            xsize 290
                            ysize 92
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
