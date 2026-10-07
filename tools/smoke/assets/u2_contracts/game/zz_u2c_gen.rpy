## tools/smoke/assets/u2_contracts: a test overlay file, never part of the game.
## It stands for the line tools/gen_sprite_defs.py writes into jjk_sprites.rpy
## once a person's set has landed (docs/UI2_DESIGN.md 8.2): with it, `nade` is a
## lit_sprite and the guarded stand-in block of jjk_defs.rpy leaves the name
## alone. `mother` has a test picture in this overlay and no such line.
image nade = lit_sprite("images/char/nade_neutral.png", (760, 1400), (380, 1362, 300))
