# Placeholder art generators

Pure-Python (no dependencies, not even Pillow) PNG renderers used to make every
image in `game/images/`. They exist so the project has *something* on screen
while you source or draw real art.

```bash
python3 tools/genbg.py       # -> game/images/bg/*.png    (1920x1080)
python3 tools/gensprite.py   # -> game/images/char/*.png  (760x1400, RGBA)
```

- `raster.py` — a tiny software rasteriser (gradients, polys, ellipses,
  rounded rects, glows, vignette, grain) plus a minimal PNG encoder.
- `genbg.py` — one function per location. Add a scene by writing a function and
  calling it from `__main__`.
- `gensprite.py` — one `CAST` table drives every character: skin, hair colour,
  hair style, uniform, accent, aura. Add a row to add a character.

To replace the placeholders with real art, just drop files with the same names
into `game/images/bg/` and `game/images/char/` — nothing in the script needs to
change. Sprites are drawn at `zoom 0.60`–`0.64` (see the `pos_*` transforms in
`game/jjk_defs.rpy`), so a real sprite around 1100–1400 px tall will drop in
without retuning.
