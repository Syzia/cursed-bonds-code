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

- `genworld.py` — draws the campus map, `map_campus.png`. Its `NODES` are the
  map art's pins; the map screen no longer draws them (it draws the `AREAS`
  cards from `game/sb_world.rpy`, and the two offices have no node). They
  matter only when the map is redrawn. It skips the map if it already exists
  unless given `--force`.
- `gensprite.py` — the few placeholder sprites still in use: the bare
  shoko/ijichi/utahime/yaga files that stand in for Mom, Dad, Oda, Kurose and
  Nade, and the two curses. It skips files that already exist unless given
  `--force`.
- `gen_gui.py` — the GUI images, from the same palette as `gui.rpy`.
- `fitcheck.py <background.png> yuji megumi ...` — characters standing in a
  background as the game shows them, without launching Ren'Py.
- Helpers: `raster.py` (drawing and PNG writing), `pngread.py` (PNG reading),
  `make_workflow.py` (the `Graph` and `recipe` helpers `make_base_workflow.py`
  builds on; its own inpainting workflow for expressions is superseded by
  step 5), `comfy_nodes/` (node definitions copied from ComfyUI).

## Testing and review (the harness kit)

Phase 1's checks, from `docs/PHASE1_DESIGN.md` section 8. None of them touches
the real `game/` folder, the owner's saves, persistent data or `.rpyc` files.
Run them from the project root.

### Lint

```bash
RENPY_DISABLE_BACKUPS="I take responsibility for this." \
  ~/Desktop/renpy-8.5.3-sdk/renpy.sh <project> --savedir <scratch folder> lint
```

Clean means no report lines before `Statistics:` and no `VALIDATE:` lines.
The `VALIDATE:` lines come from each system's validator (registered with
`register_validator` in `game/sb_hooks.rpy`): a mission label that doesn't
exist, a memory with an unknown person, an item with a bad grade, a board
partner without lines, a schedule naming a place that doesn't exist, and so on.

### `smoke.sh <harness.rpy>` — one test harness

Runs a Ren'Py harness in a scratch copy of the project (the game's `.rpy` and
`.rpyc` are copied, the art is linked, saves go to a scratch folder) and prints
its PASS/FAIL lines and a last line `RESULT PASS` or `RESULT FAIL`; the exit
code is 0 only on a pass. A Ren'Py window opens briefly. Results, screenshots
and logs go to `shots/<harness name>/` (or `SMOKE_SHOTS=<dir>`). Other
settings: `SMOKE_TIMEOUT` (seconds, default 180), `SMOKE_SAVES=1` (read-only
copies of the owner's saves), `SMOKE_SLOT` (for `load_slot.rpy`), `HEADLESS=1`,
`RENPY_SDK`. Several harnesses can run at once.

A harness is one `.rpy` file (it can live anywhere) that defines
`label zz_smoke`. `smoke/_lib.rpy` is installed beside it; its header is the
reference. It gives `check(cond, name, detail)`, `note`, `shot(name)`,
`finish()`, `abort`, `autoplay()` (plays script through: menus pick
themselves, text fast-skips, the name input and combat answer themselves),
`fixture(**vars)`, `settle(**vars)` (a post-prologue state) and `smoke_env`.
An uncaught exception fails the run with its traceback. A harness never waits
for input: it calls the loop's functions directly.

### The harnesses in `smoke/`

| harness | what it checks |
|---|---|
| `core_flow.rpy` | The standing check every package passes: a settled game, a day of the loop (story event, three actions, three new days) and the three main screens. |
| `wp0_stubs.rpy` | The contracts (design section 6): every shared function and screen exists with its frozen signature. `tools/smoke.sh tools/smoke/wp0_stubs.rpy` checks signatures, hooks and screen renders only by default; set `SMOKE_STUBS_VALUES=1` to also run the WP0 stub-value checks (these fail on the merged tree, since every stub has been replaced). `SMOKE_STUBS_ONLY_SIGS=1` is still accepted and forces signatures only. |
| `wp1_world.rpy` | Places, areas, schedules (with a frozen copy of the old ones), the offices' locks, Gojo's in-days, Tokyo trips, the ridge veil, the map (screenshots). |
| `wp2_grades.rpy` | Grades, caps, merit, NPC growth and promotions, Last Light, the alley fight's four rounds, the Grade 3 fight, migrations 10/20/30. |
| `wp3_missions.rpy` | The mission registry and story chain on a fresh and an old-save fixture; the objective at every step goes to `objectives.txt` for a read-through. |
| `wp4_board.rpy` | The board: offers, partners, outcomes over many trials, misgrades, rewards paid once, time and refusals (screenshots). |
| `wp5_memories.rpy` | The memories catalogue, the recorder, replays leaving the save untouched, Sana's flashbacks. |
| `wp6_items.rpy` | Keepsakes from flags, talisman slots and rules, the armory's states. |
| `wp7_ui.rpy` | The HUD, toasts (order, merging), the place view with four people, `person_choices` over every person, place and period. |
| `wp8_journal.rpy` | Every journal tab on a fresh and a rich save (screenshots), equipment surviving save and load, replays returning to the journal. |
| `wp9_prologue.rpy` | The whole prologue under autoplay, its flags, Kaito never on screen, the replay guards. |
| `wp10_chapters.rpy` | The later chapters' edits, then their scenes under autoplay. |
| `wp11_dev.rpy` | The review tools (`dev_panel`): every button, explore mode never firing the story, the two story buttons through the loop, and Arc Two's exact warning (screenshots). |
| `phase1_all.rpy` | The whole of phase 1 end to end: label `start` as New Game plays it (the prologue under autoplay, always "Go with him.", the real `combat`), then 30 days of the real sandbox loop, played by an overlay driver that answers the loop's own screens: start missions, the objective's place, the journal and the map each day, one board job, one person, then Sleep. It fails on any exception, a stuck day or story rows finishing out of order, and writes `objectives.txt` (one line per day: grade, merit, story step, objective, the scenes played) and `driver_log.txt`. `PHASE1_DAYS` sets the number of days. |
| `load_slot.rpy` | Used by `load_all_saves.sh`: loads one save (`SMOKE_SAVES=1 SMOKE_SLOT=1-1`) and reports where it lands. |

### `load_all_saves.sh [slot ...]` — the save regression

Loads every save (or just the slots named) in `game/saves` and
`~/Library/RenPy/JJKgamemd-1788928056`, each through `load_slot.rpy` with
read-only copies, and writes `shots/load_report.txt` (`LOAD_SHOTS=<dir>` puts
it elsewhere). Names with spaces are skipped. The report's header counts the
slots by status, then a table gives each slot's status, where it was saved and
where it landed, then each slot's summary (version, technique, grade, arc, day,
roster size, merit, the story step, the objective, keepsakes and where it
landed), then any call-stack return sites the script no longer has:

- **SAME** — landed where it was saved;
- **EARLIER** — its statement is gone, so it rolled back to an older one;
- **MOVED** — its statement exists but it landed elsewhere;
- **RECOVER** — `load_recover` or `return_recover` ran (it picks up on campus or
  at the right prologue step);
- **UNKNOWN** — the save's log couldn't be read first;
- **RAISED** — an exception, a timeout or no result. Any RAISED slot makes the
  script exit 1.

"Dead return sites" lists saves whose call stack returns to a statement the
script no longer has, with where `return_recover` will send them.

### `check_content.py [--all | --<rule> ...] [--include-phase4] [files]` — the text rules

Static checks on the story text; `--help` lists them. It prints
`file:line: rule: text` per finding and exits 1 if there are any.

- `--no-mc-on-screen` — `show mc` / `hide mc` (Kaito is never on screen),
  unless tagged `## first-person exception`;
- `--one-technique` — Filament, Emberfall, Aftersound or Stillness, unless
  tagged `# legacy-technique`;
- `--no-deadline` — the Kyoto countdown and its phrases;
- `--narration-person` — narrator lines that say "you", unless tagged
  `## you-ok`. The later chapters that design section 5.4 keeps in "you"
  until phase 4 are exempt (the `PHASE4_YOU` table: files, and labels within
  them): their count is printed as one note line, and `--include-phase4`
  lists them. Phase 4 removes entries as it converts chapters;
- `--no-literal-name` — "Kaito" or "Amagiri" written out instead of
  `[mc_name]` / `[mc_surname]`;
- `--dup-labels` — a label defined twice.

`python3 tools/check_content.py --all game/*.rpy` passes on the finished
phase 1. `smoke/baseline_check_content.txt` is the baseline WP0 recorded
before phase 1 began, kept for comparison.
