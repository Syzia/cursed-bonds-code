## tools/smoke/aa_zz_order.rpy -- the init-order check (docs/PHASE2_DESIGN.md
## 2.2 R2 "Init order", 6.1 "Init order, frozen").
##
## Ren'Py runs files of equal init priority in filename order. This file is
## named to sort before every game file, and at init 0 it registers one
## hotspot and one minigame. The registries (HOT_SPOTS, MG_GAMES,
## register_hotspot, register_minigame) live in game/sb_hotspots.rpy at
## `init -5 python`; every room_*.rpy sorts before sb_hotspots.rpy and
## registers at init 0 or later. If a registry is ever defined too late (a
## plain `init python:` in sb_hotspots.rpy would be), this file raises a
## NameError at start-up and the run fails before the harness can report.
##
## It is not a harness. tools/smoke.sh installs it into the scratch game/
## for a harness that carries the line
##
##     ## smoke-with: aa_zz_order.rpy
##
## P0a wrote the file; P0b switches it on by putting that line in
## tools/smoke/p2_contracts.rpy once sb_hotspots.rpy exists, and asserts there
## that ZZ_ORDER_HOTSPOT is in the hotspot registry and ZZ_ORDER_GAME in the
## minigame registry.
##
## The two rows are inert: the hotspot is a look hotspot whose `when` is
## never true, so it is never visible, and nothing offers the game.

init python:

    ZZ_ORDER_HOTSPOT = "zz_order_spot"
    ZZ_ORDER_GAME = "zz_order"

    def zz_order_never():
        """The dummy hotspot's `when`: never."""
        return False

    register_hotspot(ZZ_ORDER_HOTSPOT, "dorm", 960, 600, "look",
                     lines=["Nothing here. The init-order check put this line in."],
                     label="Init-order check", when="zz_order_never")
    register_minigame(ZZ_ORDER_GAME, "Init-order check", "act", min_people=1)


## The dummy game's label: a game is `label mg_<id>(opponents, stake=0)`, and
## sets mg_result before it returns (4.12).
label mg_zz_order(opponents, stake=0):
    $ mg_result = dict(game="zz_order", outcome="quit", yen=0)
    return
