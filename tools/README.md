# Tools

Python scripts for making the game's art and checking it. The full recipe, with
what each step fixes and what it costs, is in
[docs/ASSET_PIPELINE.md](../docs/ASSET_PIPELINE.md). Each script's docstring
has its exact usage. Everything is pure Python with no dependencies, except
`gen_gui.py`, which needs Pillow.

The ComfyUI steps write a workflow `.json` into `~/Desktop/JJK Game images`:
drag it into ComfyUI and press Run.

## Character sprites

1. `make_base_workflow.py <name>` — the base picture (Krea 2 on Comfy Cloud),
   from `chars/prompts/<name>.txt`. Canon and prompt notes: `chars/CANON.md`,
   `chars/PROMPTS.md`.
2. `fix_edges.py` — repairs the base: cut-off edges, head, hair and body
   redraws, a second outfit; `--install` keys it into the game.
   `fix_feet.py` is the older shoes-only version, and `transplant_scar.py`
   moved Utahime's scar between two head redraws.
3. `keysprite.py` — keys the green or magenta screen, crops, and places the
   figure on the 760x1400 canvas at its `HEIGHT_CM`.
4. `facemask.py` — the face mask the new faces are pasted through.
5. `composite_face.py --prepare`, then `make_edit_workflow.py <name>` (Nano
   Banana Pro; the wording is in `EXPRESSIONS` and `CHAR_EXPRESSIONS`), then
   `composite_face.py` on each result — the five other expressions.
6. `gen_sprite_defs.py` — writes `game/jjk_sprites.rpy` from
   `game/images/char` and `game/images/side`.

## Backgrounds

- `bgs/prompts/<name>.txt` + `bgs/style*.txt` — the scene and the shared style
  (see `bgs/STYLE.md`, and `bgs/CAMPUS.md` for the layout).
- `make_bg_workflow.py <name>` — the local ComfyUI workflow (Krea 2).
- `make_relight_workflow.py <name> night` — evening and night versions of an
  approved picture.
- `install_bg.py <render.png> [name]` — enlarges a render to 1920x1080 and
  writes `game/images/bg/<name>.png`.

## Placeholders and the rest

- `genworld.py` — draws the campus map, `map_campus.png`. Its `NODES` must
  match `LOCATIONS` in `game/sb_world.rpy`. It skips the map if it already
  exists unless given `--force`.
- `gensprite.py` — the few placeholder sprites still in use: the bare
  shoko/ijichi/utahime/yaga files that stand in for Mom, Dad, Oda, Kurose and
  Nade, and the two curses. It skips files that already exist unless given
  `--force`.
- `gen_gui.py` — the GUI images, from the same palette as `gui.rpy`.
- `fitcheck.py <background.png> yuji megumi ...` — characters standing in a
  background as the game shows them, without launching Ren'Py.
- `smoke.sh <harness.rpy>` — runs a throwaway Ren'Py test harness and removes
  every trace of it afterwards.
- Helpers: `raster.py` (drawing and PNG writing), `pngread.py` (PNG reading),
  `make_workflow.py` (the `Graph` and `recipe` helpers `make_base_workflow.py`
  builds on; its own inpainting workflow for expressions is superseded by
  step 5), `comfy_nodes/` (node definitions copied from ComfyUI).
