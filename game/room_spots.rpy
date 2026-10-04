################################################################################
## Cursed Bonds — what is in the rooms: hotspots and their lines.
##
## Phase 2, P6 (PHASE2_DESIGN.md 4.10, D30, 6.1). The first set of hotspots:
## things in a room's picture that can be clicked. The machinery (the
## registry, what is visible, the layer that draws them, the validator) is
## sb_hotspots.rpy's; this file only says which room has what.
##
##   SPOT_SET         the action hotspots: an object that stands for a row of
##                    place_actions(), which leaves the icon column while the
##                    object can be seen
##   SPOT_LOOKS       where each look hotspot is, and its name
##   SPOT_LINES       {hotspot id: [first-person lines]} for the look hotspots
##   spot_vend_ok()   the courtyard's vending machine can be used now
##   label sb_do_spot_vend
##
## The points here are the code's own. The final ones, measured on each
## picture with tools/layout_sheet.py, are in game/layout/hot_<place>.json
## (D5) and win. The card table's hotspot is registered here with the rest of
## the set; its action (cards_play) and everything behind it is
## room_cards.rpy's.
################################################################################

init -1 python:

    ## What the machine costs and gives (4.10).
    SPOT_VEND = dict(yen=150, stamina=10)

    def spot_vend_ok():
        """P6 (room_spots.rpy). bool: the courtyard's vending machine can be
        used now: once a day."""
        return "spot_vend" not in store.actions_today

    ## (hotspot id, place, x, y, icon, the place action it stands for).
    ## Existing actions only move from the column into the room: their ids,
    ## labels and rules are untouched (4.10). The storehouse has two rows at
    ## one point; the room never offers both actions at once.
    SPOT_SET = [
        ("computer",   "dorm",           440, 590,  "pc_open",    "pc_open"),
        ("bed",        "dorm",           1330, 720, "sleep",      "sleep"),
        ("card_table", "dorm_common",    1400, 876, "cards_play", "cards_play"),
        ("bank",       "riverside",      1580, 905, "fish_cast",  "fish_cast"),
        ("stacks",     "library",        300, 520,  "lib_study",  "lib_study"),
        ("counter",    "cafeteria",      1500, 600, "eat",        "eat"),
        ("cot",        "infirmary",      1420, 700, "rest",       "rest"),
        ("racks",      "storehouse",     1600, 600, "tools",      "tools"),
        ("armory",     "storehouse",     1600, 600, "armory",     "armory"),
        ("board",      "utahime_office", 1500, 470, "board",      "board"),
        ("veil",       "ridge",          960, 250,  "veil",       "veil"),
    ]

    ## (hotspot id, place, x, y, its name on hover).
    SPOT_LOOKS = [
        ("tv",           "dorm_common", 1590, 560, "The television"),
        ("locked_shelf", "library",     1630, 480, "A locked cabinet"),
        ("blackboard",   "classroom",   1450, 500, "The blackboard"),
    ]

    ## One line a day each (hot_use says lines[day % len(lines)]).
    SPOT_LINES = {
        "tv": [
            "The television is off. Somebody has left a controller on the table with its battery cover taped on.",
            "I turn the television on. A cooking programme, a quiz, the weather. Out there it is an ordinary day.",
            "There's a rental case on the shelf under the television with Yuji's handwriting on the spine: DO NOT RETURN YET.",
            "A late film with the sound low. I watch four minutes of it standing up and never learn who did it.",
        ],
        "locked_shelf": [
            "A cabinet with a lattice door and a paper seal across the lock. The spines behind it have no titles.",
            "I try the cabinet door, gently. It doesn't move, and the seal on it warms under my thumb. I take my thumb away.",
            "Someone has dusted every shelf in this room except the ones behind that door.",
            "Through the lattice I can count eleven books and a gap where a twelfth was.",
        ],
        "blackboard": [
            "The blackboard still has the last lesson on it: a barrier in cross-section, half rubbed out, and the word AGAIN underlined twice.",
            "Somebody has drawn Gojo in the corner of the blackboard. It is four lines and a blindfold, and it is unmistakable.",
            "The duty roster is on the blackboard in new chalk. I'm on windows.",
            "One line left over from the last lesson: cursed energy is born from the negative. I read it until it stops being words.",
        ],
    }


## Registered at init 0: every room_*.rpy sorts before sb_hotspots.rpy, whose
## registry is made at init -5 (6.1, "Init order, frozen").
init python:

    for _spot_row in SPOT_SET + SPOT_LOOKS:
        if _spot_row[0] in SPOT_LINES:
            register_hotspot(_spot_row[0], _spot_row[1], _spot_row[2], _spot_row[3], "look",
                             lines=SPOT_LINES[_spot_row[0]], label=_spot_row[4])
        else:
            register_hotspot(_spot_row[0], _spot_row[1], _spot_row[2], _spot_row[3], _spot_row[4], act=_spot_row[5])

    del _spot_row

    ## The one hotspot that is in no place_actions list: it is always drawn in
    ## front, and a person never hides it (4.10).
    register_hotspot("spot_vend", "courtyard", 1600, 690, "spot_vend",
                     label="Vending machine",
                     hint="Something cold. ¥%d. Once a day." % SPOT_VEND["yen"],
                     cost=0, when="spot_vend_ok", standalone=True)


## The vending machine under the eaves (4.10): ¥150, stamina +10, once a day.
## A refusal costs nothing and uses nothing up.
label sb_do_spot_vend:
    if not spot_vend_ok():
        "The machine is sold out of the only thing I like. Tomorrow."
        return
    if yen < SPOT_VEND["yen"]:
        "I count my coins twice. It comes to less than the machine wants, both times."
        return
    if stamina >= stamina_max:
        "I'm not thirsty."
        return
    $ actions_today.add("spot_vend")
    $ add_yen(-SPOT_VEND["yen"])
    "The machine under the eaves takes my coins, thinks about it, and drops a can so cold it hurts to hold."
    $ stamina = min(stamina_max, stamina + SPOT_VEND["stamina"])
    "I drink it standing in the shade, and the day gets a little easier."
    return
