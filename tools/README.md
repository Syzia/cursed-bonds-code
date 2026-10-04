# Tools

Python scripts for making the game's art and checking it. The full recipe, with
what each step fixes and what it costs, is in
[docs/ASSET_PIPELINE.md](../docs/ASSET_PIPELINE.md). Each script's docstring
has its exact usage. Everything is pure Python with no dependencies, except
`gen_gui.py --all`, which needs Pillow.

The ComfyUI steps write a workflow `.json` into `~/Desktop/JJK Game images`
(phase 2's into its `phase2/` folder): drag it into ComfyUI and press Run. The
results land in `~/ComfyUI-Shared/output`. Phase 2's art, with numbered steps
and prices, is in [docs/ART_PHASE2.md](../docs/ART_PHASE2.md).

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
- `make_bg_workflow.py <name> [<name> ...]` — the local ComfyUI workflow
  (Krea 2, two candidates a place, about $0.035 a picture). It refuses a name
  with no prompt file. `--out phase2/areas.json` writes the workflow under
  that name instead of `backgrounds.json`. Phase 2 added prompts for the six
  bird's-eye area maps (`area_<key>`, which use `bgs/style_aerial.txt`: no
  horizon, no eye-level camera), `map_tokyo`, `library`, `utahime_office`,
  `gojo_office`, and the five yards: `school_yard`, `dorm_yard`, `staff_yard`,
  `training_yard`, `trailhead`.
- `make_relight_workflow.py <name> night` — evening and night versions of an
  approved picture.
- `install_bg.py <render.png> [name]` — enlarges a render to 1920x1080 and
  writes `game/images/bg/<name>.png`.

## Phase 2: icons, poses, faces, foregrounds, layouts

Each has a stand-in the game draws by itself; the file drops in by name.

- **Icons.** `make_icon_workflow.py [n]` writes one workflow a sheet
  (`icons_sheet_<n>.json`, three sheets of 6 x 5 white line icons, two
  candidates each, about $0.32 a sheet). `--names` rewrites
  `icons/sheet_<n>.txt` from `ICONS` in `game/ui_icons.rpy`; every run checks
  the three files hold exactly the 88 names, and that its own `DRAW` table
  (what each icon looks like) agrees with `ICONS`.
  `cut_icons.py <sheet.png> icons/sheet_<n>.txt` cuts a render into
  `game/images/icons/ic_<name>.png` (96x96) and always writes a preview,
  `shots/art/icons_<names file>__<render>.png`. `--dry` writes the preview
  only; `--only a,b` installs just those names; `--out <dir>` installs
  elsewhere; `--any-sheet` cuts even when the render's sheet number differs
  from the names file's (it stops otherwise). A line `-` in a names file
  leaves a cell out.
- **Poses** (a person painted into their room).
  `make_pose_workflow.py <place> <who> [variant]` (the two names in either
  order), `--batch <n>` for every pose of an art batch, `--list` for the plan
  and its cost. Two candidates, stacked: A on top, B below; about $0.32 a
  pose. The plan is the table `POSES` in the tool; `smoke/p2_view.rpy` checks
  each row against the schedule.
  `install_pose.py <render.png>` brings the render to 1920x1080 (scaled to
  the full width, then padded or cropped in height: the editor lays the room
  across the render's whole width), refuses it if more than 35% of the room
  changed, measures the box around the person,
  and writes the box to `game/layout/view_<place>.json` (the only file it
  writes there), the picture to `game/images/place/` and a preview to
  `shots/art/`. `--name pose_<place>__<who>` when the file name doesn't say;
  `--bg <picture>` to compare against another room picture; `--box x,y,w,h`
  sets the box by hand; `--dry` writes nothing but the preview; `--root <dir>`
  writes under another folder (the harness uses it).
- **Blink and talk.** `install_face.py --prepare <who>` cuts the close-up an
  editor is given (`<who>_fx_in.png`) from the game's own neutral sprite;
  `make_edit_workflow.py <who> --only blink,talk` (Gojo and Yaga: `--only
  talk`) writes `<who>_fx.json` and prints the cost ($0.16 a picture);
  `install_face.py <render.png> <who> blink|talk` lines the answer up and
  writes `game/images/char/fx/fx_<who>_<kind>.png`. `--sheet` draws every eye
  and mouth box (`VIEW_FACE` in `game/view_stage.rpy`) on its sprite.
- **Foregrounds.** `make_fg.py <place> [variant]` (`--all`, `--dry`) cuts
  `game/images/fg/fg_<place>[_<variant>].png` out of the room's own picture,
  by the polygon in `fg/<place>.json` (tool input; the game never reads it).
  Free.
- **Layout sheets.** `layout_sheet.py <name>` draws a layout on its picture
  for approval, into `shots/layout/<name>.png`. The name is the layout's full
  stem: `view_<place>` (where people stand, pose boxes, the foreground
  polygon), `hot_<place>` (the room's hotspots and exits, the frame they must
  stay in, the two lanes they must stay out of, where people stand) or
  `area_<key>` (an area's map pins). It draws the code's numbers with the
  sidecar `game/layout/<name>.json` laid over them. `--sidecar <file>` and
  `--fg <file>` use another file; `--no-sidecar` draws the code's numbers
  alone; `--defaults <file>` and `--out <file>` name the input and the output.
  It stops with one line on a malformed sidecar (unknown keys, a slot key
  outside "1" to "4", a slot list of the wrong length). **In a new worktree,
  run `tools/smoke.sh tools/smoke/p2_contracts.rpy` first:** the code's
  numbers come from `shots/layout/defaults.json`, which that harness writes
  and git ignores.

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
- `gen_gui.py` — the GUI images, from the same palette as `gui.rpy`. A plain
  run draws only phase 2's four pictures (`gui/grade_sheen.png`,
  `hot_ring.png`, `soft_box.png`, `card_back.png`) in pure Python. `--all`
  also redraws the phase-1 set; it needs Pillow, which is not installed on
  this Mac, so **`--all` has never been run here and is unverified**. Nothing
  in the game depends on it.
- `fitcheck.py <background.png> yuji megumi ...` — characters standing in a
  background as the game shows them, without launching Ren'Py.
- Helpers: `raster.py` (drawing and PNG writing), `pngread.py` (PNG reading),
  `make_workflow.py` (the `Graph` and `recipe` helpers `make_base_workflow.py`
  builds on; its own inpainting workflow for expressions is superseded by
  step 5), `comfy_nodes/` (node definitions copied from ComfyUI).

## Testing and review (the harness kit)

The checks of `docs/PHASE1_DESIGN.md` section 8 and `docs/PHASE2_DESIGN.md`
sections 2.2 and 8. None of them touches the real `game/` folder, the owner's
saves, persistent data or `.rpyc` files. Run them from the project root.

**The standing set** for any change: lint; `check_content.py --all`;
`p2_contracts.rpy`, `core_flow.rpy` and `phase1_all.rpy`; then the harness of
the system you touched. Before a merge, every harness in the tables below.

### Lint

```bash
RENPY_DISABLE_BACKUPS="I take responsibility for this." \
  ~/Desktop/renpy-8.5.3-sdk/renpy.sh <project> --savedir <scratch folder> lint
```

The command ends at `lint`. With a trailing `.` this SDK tries to write its
report to `.` and raises IsADirectoryError.

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
`RENPY_SDK`. Several harnesses can run at once, except the ones that need the
pointer (below).

Phase 2 added:
- **`## smoke-with: <file>.rpy`**, a line in a harness: `tools/smoke/<file>.rpy`
  is installed beside it under its own name. This is how `p2_contracts.rpy`
  runs with `aa_zz_order.rpy`, which must sort before every game file.
- **The asset overlay.** When `tools/smoke/assets/<harness name>/` exists,
  every file under its `game/` folder is copied to the same path in the
  scratch copy (`assets/p2_view/game/images/place/x.png`), so a test picture
  never lands in the real `game/images/`. Anything outside `game/` is refused.
  `SMOKE_ASSETS=<dir>` uses another overlay folder.
- **`SMOKE_ROOT`**, set for the harness: the repository the run started from,
  so it can read (never write) `tools/smoke/baseline_p0.json` or
  `tools/none_ok.txt`.
- **It refuses a linked cache.** Never set up a worktree or a scratch root
  with `game/cache` linked to another tree's; the script stops if the scratch
  `game/cache` ends up a link.

A harness is one `.rpy` file (it can live anywhere) that defines
`label zz_smoke`. `smoke/_lib.rpy` is installed beside it; its header is the
reference. It gives `check(cond, name, detail)`, `note`, `shot(name)`,
`finish()`, `abort`, `autoplay()` (plays script through: menus pick
themselves, text fast-skips, the name input and combat answer themselves),
`fixture(**vars)`, `settle(**vars)` (a post-prologue state) and `smoke_env`.
An uncaught exception fails the run with its traceback. A harness never waits
for input: it calls the loop's functions directly, or drives the loop's own
screens from an overlay timer.

`fixture()` fails on a name the store doesn't have, and refuses the shaped
variables (`board_offers`, `inventory`, `npc_state`, `cards_state` and the
rest): build those with their owner's functions (`board_generate()`,
`give_item()`, `promote()`, `cards_new()`, `fish_land()`, `pc_request()`).
The measuring helpers: `zz_rect(screen, id)`, `zz_buttons(screen)`,
`zz_words(screen)` (Latin-letter tokens only; icon glyphs are skipped),
`zz_texts(screen)`, `zz_calls(fn, seconds)`, `zz_layer_tags(layer)`,
`zz_render()` and `zz_worst(screen, hover=, name=)` (four toasts queued, the
banner up, skipping on, one button hovered, then a screenshot). They work over
a modal screen; a harness's own `renpy.pause` over one needs `modal=False`.

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

Phase 2's harnesses (the PASS counts are the merged tree's at the end of P8,
for comparison):

| harness | what it checks |
|---|---|
| `p2_contracts.rpy` (130) | The frozen contracts of design section 6: every shared function's signature, owning file and return shape; every `tools/none_ok.txt` example returns `None`; icon coverage; the registries' duplicate checks; init order (with `aa_zz_order.rpy`, which adds two inert hotspots, `zz_order_spot` and `zz_tv`). It also **writes `shots/layout/defaults.json`**, the code's own layout numbers, for `layout_sheet.py`. Run it **without `SMOKE_P0_STRICT`**: its notes that a wave-0 comparison "no longer holds" are expected. |
| `p2_map.rpy` (96) | The two-level map: six markers, pins, the zoom-in, tooltips, Tokyo's districts and the night button. |
| `p2_hud.rpy` (117) | The corner icons and chips, the icon column for every room and period, the person view, toast lanes, the banner. Its last section saves and loads inside the real loop and must stay last. About 95 s. |
| `p2_journal.rpy` (188) | The five tabs, person pages, the Me page, the 70-word budget over 214 pages, checklists, Leads. **Run it with `SMOKE_TIMEOUT=300`**: it takes about 150 s of the default 180. |
| `p2_gear.rpy` (78) | Grade chips on the board, the armory and the fight header; tool and talisman checklists; nothing held is taken away. |
| `p2_night.rpy` (170) | The night rule, the Gojo night against real training days, the night in Tokyo, the Black Market and its price rule. |
| `p2_view.rpy` (130) | People blended into rooms: slots, poses, foregrounds, name tags, blink and talk, the save test in dialogue, the pose plan against the schedule. It runs the system `python3` for `install_pose.py`. About 110 s. |
| `p2_rooms.rpy` (126) | Hotspots (every action is in the room or in the column, never neither, never both), the computer, the Library, fishing, the vending machine. |
| `p2_cards.rpy` (145) | Blackjack and poker: thousands of simulated hands, the limits, rollback blocked after every deal. About 45 s. |
| `p2_paths.rpy` (109) | Exits and the five yards: the graph is connected, an exit costs no time, locked exits, the map's smaller markers. |
| `phase2_all.rpy` (35) | The whole of phase 2 end to end: `SMOKE_TIMEOUT=300 tools/smoke.sh tools/smoke/phase2_all.rpy` (about 90 s for the default 30 days; `PHASE2_DAYS` sets the days, `PHASE2_MAX_SECONDS` when the driver stops itself). A fresh game through the prologue, then the real loop played by a driver that presses what the screens offer: the map's two levels and the exits on alternate days, the journal's five tabs and a person's page, a board job a day, a page read and the cross-check, a cast, a blackjack and a poker hand, a ride with Ijichi, a night in Shibuya with a market purchase, a Gojo night, bed and one carried-home night. It writes `days.txt` (one block a day) and `driver_log.txt`. |
| `p2_saves.rpy` (170) | Saves are tested by saving: `tools/smoke.sh tools/smoke/p2_saves.rpy` (about 35 s). In one run inside the real loop it makes and reloads 21 saves (the armory, the board, a yard, the map, the computer, the journal, the person view, dialogue, blackjack, fishing at the bite, the night's menus, the market, the Gojo night, the rest day) and checks each comes back on its own statement with the same state, without `load_recover`. Not covered: a save inside a fight or on the grade card (the owner's phase-1 saves cover those). `p8_patterns/` holds the two patterns it was built from, with a README on the two load pitfalls. |

**Hover checks need the pointer.** `p2_contracts.rpy`, `p2_paths.rpy` and
`p2_view.rpy` have checks that hold the pointer over a button (or use
`renpy.set_focus`). They fail while another Ren'Py window is open: run these
three one at a time, with no other harness and no game running, and never in
parallel from several worktrees on one desktop. When one fails on a hover or
tooltip check, run it again alone a few minutes later before treating it as
real.

**The strict wave-0 evidence** (the place view and person view pixel-identical
to the tree before phase 2) is `SMOKE_P0_STRICT=1` with
`SMOKE_P0_SHOTS=<repo>/tools/smoke/baseline_shots/1818x1022`. It is only
meaningful against the pre-phase-2 tree, so it is history now. The two
screenshots directly in `baseline_shots/` are 2666x1499, from before this
Mac's window size changed; the per-size folder is kept rather than retaking
them.

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

The reference is `docs/load_report_phase2.txt`: the owner's eleven slots (1-1
and auto-1 to auto-10, which are also the checkpoint saves), all SAME. Compare
a new run with it by status, not by line number. `docs/load_report_phase1.txt`
and the three `load_report_phase2_wave<n>.txt` files are history.

### `check_content.py [--all | --<rule> ...] [--include-phase4] [files]` — the text and name rules

Static checks on the story text and, since phase 2, on names; `--help` lists
them. It prints `file:line: rule: text` per finding and exits 1 if there are
any. It can be called by absolute path from any folder.

```bash
python3 tools/check_content.py --all game/*.rpy tools/smoke/*.rpy
```

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

Phase 2's rules (design 2.2, R1, R2 and R4):

- `--dup-globals` — a top-level name defined in two files, or twice in one:
  every `NAME =`, `def` and `class` in an init block, and every `define`,
  `default`, `screen`, `style`, `transform`, `image`. Store names, screens,
  styles and images are separate namespaces. A style counts only when two
  files define it; labels are left to `--dup-labels` when both run;
- `--prefixes` — a new name (one not in `smoke/baseline_globals.txt`) must
  carry its file's prefix from `prefixes.json`, or be on that file's
  exception list. A lower-case prefix also allows its capitals. A file with
  no row may gain no new top-level name. `define config.*` is ignored;
- `--harness-names` — every top-level name in `tools/smoke/*.rpy` starts with
  `zz` / `ZZ`;
- `--art-names` — two files under `game/images/` with the same basename
  (Ren'Py names an image from its basename);
- `--action-returns` — every `Function(` in a game file, in screens and in
  `def` bodies, must be `Function(ui_do, fn, ...)` or call a function listed
  in `none_ok.txt` (one per line: name, a tab, an example call that
  `p2_contracts.rpy` runs and asserts returns `None`). `Function` handed on
  without a call (an alias) is a finding too;
- `--icon-names` (added by P8) — the literal first argument of `icon("...")`
  and `icon_btn("...")` in a game file must be one of the 88 names of `ICONS`
  in `game/ui_icons.rpy`. Lint cannot see this: an unknown name draws a
  question mark in the game. An argument that is not one plain string is not
  read.

`smoke/baseline_check_content.txt` holds the known findings of the tree as it
stood before phase 2; they are subtracted by file, rule and text (not line
number), and `--no-baseline` lists them. `--write-baseline` rewrites both
baselines and **does nothing without the second flag `--i-am-p0a-or-p8`**:
never run it in a package.

What the name rules do not read: a plain `import x`, `except ... as NAME`, a
one-line `if x: a = 1`, and names set through `setattr` or `globals()`.
