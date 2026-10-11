## tools/smoke/assets/u2_contracts: a test overlay file, never part of the game.
## It stands for the line tools/gen_sprite_defs.py writes into jjk_sprites.rpy
## once a person's set has landed (docs/UI2_DESIGN.md 8.2): with it, `nade` is a
## lit_sprite and the guarded stand-in block of jjk_defs.rpy leaves the name
## alone. `mother` has a test picture in this overlay and no such line.
image nade = lit_sprite("images/char/nade_neutral.png", (760, 1400), (380, 1362, 300))

## The tree's own manifest, laid under this overlay's three test rows.
## tools/smoke.sh lays this overlay's layout/pictures.json OVER the tree's own
## (its step 2b copies a file, it does not merge), so without this block a
## tree that holds a real manifest would be read here with every picture back
## at revision 1, and each real sidecar that carries for_rev would be "stale".
## The tree's own rows are read from the repository (SMOKE_ROOT) and laid
## under the three test rows, which win where both name a picture, before
## anything asks for a revision (art_manifest.rpy is init -6 and sorts before
## this file).
init -6 python:
    def zz_u2c_tree_rows():
        import builtins, json, os
        rows = art_rows()
        path = os.path.join(os.environ.get("SMOKE_ROOT", ""), "game", "layout", "pictures.json")
        if os.path.isfile(path):
            with builtins.open(path, encoding="utf-8") as f:
                got = json.load(f)
            got = got.get("pictures") if isinstance(got, builtins.dict) else None
            for k, r in (got or builtins.dict()).items():
                if isinstance(r, builtins.dict):
                    rows.setdefault(builtins.str(k), r)
    zz_u2c_tree_rows()
