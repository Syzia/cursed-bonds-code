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
   A sprite that is not yet in the game is keyed with `--edge new`
   (`keyedge.py`, below); the sprites already in the game are never keyed again.

- `keyedge.py <render.png> <cutout.png>` — the cut-out's edge for a NEW sprite on
  a flat saturated backdrop (docs/UI2_DESIGN.md D58): how much of each edge
  pixel is figure is read off the backdrop's own colour. Needs numpy and scipy,
  so it starts itself again with ComfyUI's Python. `--check` reports what a
  cut-out still carries of the backdrop.
- `make_key_tests.py <folder>` and `test_keying.sh` — the sixteen exact test
  pictures (the game's sprites on flat pink and green, the true cut-out known)
  and the tests of the edge. No Ren'Py; about two minutes. Run after any
  change to `keyedge.py` or `keysprite.py`.
- `cutcheck.py <render.png> [<cutout.png>]` — a second look at a cut-out by the
  anime-trained model, run directly. It reports a gap left filled, a piece cut
  off or a stray mark and never changes a pixel; it says so and exits 0 where
  the model file is absent.
- `cloth_match.py --check | --apply <who,...|all>` — one cloth for the school
  uniform (D59): moves each pixel of uniform cloth onto one colour ramp and
  remakes the side portraits. It redraws nothing and refuses to write if a
  pixel outside the cloth, or the alpha channel, would change. Yuji's
  redrawn set is matched with `--apply yuji --redrawn` at its install.
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
  writes `game/images/char/fx/fx_<who>_<kind>.png`; a blink also writes
  `shots/art/fx_<who>_blink_faces.png`, every other face with the blink laid
  on it (blue frame: takes the blink; red: keeps its own eyes), to be looked
  at before `install_set.py`. `--sheet` draws every eye
  and mouth box (`VIEW_FACE` in `game/view_stage.rpy`) on its sprite.
- **Foregrounds.** `make_fg.py <place> [variant]` (`--all`, `--dry`) cuts
  `game/images/fg/fg_<place>[_<variant>].png` out of the room's own picture,
  by the polygon in `fg/<place>.json` (tool input; the game never reads it).
  Free.
- **Layout sheets.** `layout_sheet.py <name>` draws a layout on its picture
  for approval, into `shots/layout/<name>.png`. The name is the layout's full
  stem: `view_<place>` (where people stand, the floor and the scale, pose
  boxes, the foreground polygon), `hot_<place>` (the room's hotspots and
  exits, the side each name opens on, the frame they must stay in, the two
  lanes they must stay out of, the spare doors, where people stand) or
  `area_<key>` (an area's map pins). **For a shaped place** (the sidecar
  holds `shapes`, D60) a hotspot sheet is two frames: every shape's outline
  over the picture, then every shape lit and named, as while names are shown.
  It draws the code's numbers with the sidecar `game/layout/<name>.json` laid
  over them, and takes every key of UI2_DESIGN.md 3.2. `--sidecar <file>` and
  `--fg <file>` use another file; `--no-sidecar` draws the code's numbers
  alone; `--out <file>` names the output. **A layout that is still only
  staged:** `--staged <folder>` reads `<name>.json` (and `check_<place>.json`)
  from a folder such as `tools/art/staged/<stem>/`, and `--bg <picture>`
  draws on a picture given by path (a 2752 px render is fitted). All its
  numbers (the frame, the lanes, the stage, the points, the code's slots, the
  pins) come from the layout dump, `tools/art/game_layout.json`; in a
  worktree, `--layout-dump <file>`. It no longer reads
  `shots/layout/defaults.json`.
- **The layout check.** `check_layout.py <folder or files>` is the check a
  layout must pass before its picture may be installed (UI2_DESIGN.md 5.6
  step 4, 7.3, 6.3, 4.6). It reads a candidate as files (`hot_<place>.json`,
  `view_<place>.json`, `area_<key>.json`, `map_campus.json`) before they are
  in `game/layout/`, prints one plain line for each thing REFUSED and each
  thing only REPORTed, and exits 0 only when nothing is refused (1 refused, 2
  a dump out of date). Every limit comes from the layout dump; the shape
  rules are the game's own text, run from `game/sb_hotspots.rpy`; the fixed
  facts are `check_campus.py`'s, called. Beside the layout's files a folder
  may hold `check_<place>.json`, read by this tool and the sheet only and
  never installed: `front` (the PLANNED hotspots that are their room's
  foreground object; `--front id,id` adds to it), `objects` (the box of the
  thing a front shape is traced round), `fg` (a foreground outline not yet in
  `tools/fg/`), `doors`, `horizon`. `--selftest` runs its negative tests (one
  whole layout that passes, and small ones that must each be refused by
  name); `tools/test_art_tools.sh --only layout` runs each through the
  command line, and runs `check_campus.py --selftest` beside them (that
  selftest failed unseen from U0c1 to U0d3's review, because nothing ran
  it). `--layout-dump <file>` in a worktree; `--no-campus` for a
  test layout on a picture the campus record does not speak of.
  Two rules read numbers the dump gained with U0d3 (`lock_labels`, and
  `tag_edges`, `tag_gap`, `tag_w` under `frames`): a door that can be locked
  must have room for its reason (`lock-label`), and a row's name tags must
  fit between their edges (`tag-x`). With a dump written before those keys,
  `lock-label` is only reported, on a label at its largest, and `tag-x` is
  not checked: both begin to refuse once `tools/smoke.sh u2_dump` has
  rewritten the committed dump in the owner's folder.
  When the files are named one by one (as `install_redo.py --compose
  ... --layout hot_x.json view_x.json` names them) the `check_<place>.json`
  lying beside them is read all the same.
- **Batch 0, staged (U0d3).** `tools/art/staged/courtyard/` and
  `tools/art/staged/library/` hold the first two layouts traced as shapes
  (D60): `hot_<place>.json`, `view_<place>.json`, the tool-only
  `check_<place>.json`, and a `README.md` saying what each shape is and why
  people stand where they do. `tools/art/staged/batch_0/art_0.json` names
  the four pictures of batch 0 by their 2752 px renders (name, size,
  sha256), what the installer said of each when run dry, and the four
  commands that install them. **A staged picture is kept as the render
  itself, where ComfyUI wrote it; the repository holds its name and sum,
  never a fitted copy,** because the installer fits the render itself. To
  look at a staged layout: `python3 tools/layout_sheet.py hot_courtyard
  --staged tools/art/staged/courtyard --bg <render>` and `tools/py_art.sh
  tools/stage_preview.py courtyard --bg <render> --staged
  tools/art/staged/courtyard`. Two faults a real install of the Courtyard
  met were put right with it: `check_campus.fix_from_layout` no longer
  renumbers the exits of a place whose exits were already fixed facts (the
  Courtyard's are numbered among the things seen between them), and
  `u2_dump`'s check of a test `tips` row lays its two rows over the place's
  own.
- **The installer's check, corrected (U0d3).** `install_redo.py` (its own
  header has the whole proof) holds, besides every exit, hotspot, standing
  row, pose box and foreground outline, **the wall under each traced shape's
  outline** (D60): a render in which it moved is REFUSED and the shape is
  named. Seven false alarms and blind spots met on the pictures run early are
  corrected, each against the render that showed it
  (`tools/art/staged/early/art_3a_early.json`, `art_3b_early.json`,
  `art_4b_early.json`): a point on glass is held by the door's post and frame
  and not by the view (the keep list's `windows` rows,
  `tools/bgs/keep/README.md`); a floor drawn again (other boards, sunlight) or
  crossed by a window's grid of light is a LOOK, both where people stand and
  as "something new on the floor" (but a standing point whose own window
  LOCKS on an offset has moved and is refused like any other point, and so
  is one whose floor is drawn again while what stands on it slid, and one
  that no longer lines up on a floor the keep list's floor zone shows to be
  the same drawing: "something stands there", a flat bag or a mat that has
  too little fine edge for "something new is on the floor"; not where the
  room's named addition, `allow`, lies in the point's window); the named addition on a hotspot's own
  object does not make that object "gone"; a pale thing on a wall that became
  lighter is a LOOK ("fainter"). **A flat thing set down on a floor**
  (review 3, 12 Oct): the standing points find it only where a point's own
  window holds little but bare boards, so a wide floor that is still the
  same drawing (its 160 px parts agree with the game's 0.75 or better in
  the middle) is refused when ONE part agrees under 0.55: "something new
  is on the floor (...): that part of it no longer agrees with the picture
  in the game". On the chosen Cafeteria and Common Room, with a flat thing
  set down at each of the nine places people stand, 51 of 72 are refused
  now (22 before). What it still cannot find: a dark thing against dark
  wood (a dark bag on the Cafeteria's wall panels, or beside the Common
  Room's backpack), anything at the Common Room's three rows on the rug
  (that zone is too small to be read in parts), and a thing that covers
  so much of a floor's zone that the zone no longer reads as the same
  drawing: its middle under 0.55 is "the floor is drawn again", a LOOK,
  and between 0.55 and 0.75 nothing is said (a mat 400 px wide across the
  Common Room's boards reads 0.74, and is not seen). The Cafeteria's floor zone (`tools/bgs/keep/cafeteria.json`)
  now runs under all nine places people stand there: the rows by the wall
  (x 250, x 330) and by the near table (x 1380) lay outside it. **A relight is read by eye beside its day
  picture for anything added** (a lamp, a blanket, a bench): it is never
  refused for one, and the one case that can be measured without a false
  alarm is shown as a LOOK (a small `empty` row of the keep list that gained
  edge: the blanket over the sofa's arm is caught, the lamp on the desk is
  not). Two later relights were tried against that rule on 11 Oct (review
  1) and it is left as it is: three pot plants a relight set on Yuji's
  windowsill read 1.43 once the sill is an `empty` row (a LOOK, by 0.03),
  and three boxes set on top of Megumi's bookshelf read 1.15, under the
  1.24 that a bare table top reads under moonlight in a relight the owner
  chose, so no threshold tells them apart. Neither room has a keep list, so today both
  pass unseen: **look at every relight beside its day picture.**
  `tools/test_art_tools.sh` runs every picture the owner chose early that
  was redone in place or relit (76, to the records of 11 Oct): none may be
  REFUSED. **The suite's fixtures are the tree as it was before the
  overhaul installed anything**: whatever an install has written (a picture,
  its foreground, its light row, a layout with `for_rev`, the manifest, the
  place's rows of the dump) is put back from git in the scratch copy
  (`before_overhaul()` in `tools/test_art_tools.py`), so the suite reads the
  same before and after batch 0: every line the same, but that the six
  lines on the two staged layouts become two saying the installed files
  are the staged ones. Each picture is taken from the commit its own
  manifest row names (`rev1_commit`; a relight's first `from_commit`), and
  what goes with it from the tree as it stood just before the picture was
  replaced, so it does not matter how the install was committed. Proved on
  12 Oct (review 3) in clones holding batch 0 committed in one commit,
  committed as the pictures first and the manifest after, and not
  committed; their dump was the committed one with its hash taken again,
  not one the game wrote. (The proof of 11 Oct was made with the install
  not committed. Committed, five lines failed: the copy stands at the
  picture of before, HEAD holds the new one, and the installer found no
  commit for the picture it replaced. For a copy, `--root`, it now reads
  the file's history as well.) A manifest row of a kind it does not
  know how to put back (the first pose, say) is a SKIPPED line, which
  `--strict` fails: teach `before_overhaul()` that kind then. A tree whose
  pictures of before git cannot give (a copy with no git, a clone without
  its history, a row that names a commit which is not there) is ONE line
  saying which commit is missing, nothing is run, and the suite ends
  RESULT FAIL: a commit git does not hold is never read as a picture that
  was not there. `tools/test_art_tools.sh --only fixtures` tests all of
  this on small git trees of its own. It will not
  run where `game/images`, `game/layout` or `tools/fg` is a symbolic link
  (a copy would write through it). To try an install in a scratch copy of the tree, run THIS tree's
  tool with `--root <the copy>`; a copy that is not a git checkout keeps its
  approved render beside itself whichever tool is run.
- **The stage preview.** `tools/py_art.sh tools/stage_preview.py <place>
  [hour] [--who a,b,c]` draws a place as the game would, with the people
  standing in it: the hour's picture or the day picture under the hour's
  tint, the ink wash, each sprite at its slot with its contact shadow under
  the room's light, the foreground over the far people, the name tags. With
  no hour it writes the sheet `shots/stage/<place>.jpg` (one to four people
  by day and a frame for each hour, at half size); with an hour, one frame at
  full size. `--bg <render>` draws on a picture that is not installed (a
  2752 px render is fitted) and `--staged <folder>` reads `hot_`, `view_`,
  `light_` and `check_<place>.json` from a folder such as
  `tools/art/staged/<stem>/`: it is what a room is judged on BEFORE it goes
  in. **For a shaped place** each shape's outline is drawn (a front one
  dashed), and the sheet gains two frames at full size: the outlines with the
  people, and every shape lit and named, each name where the game draws its plate
  (so names that would meet are seen meeting). `--dialogue` is the scene case;
  `--plain` leaves out everything the game does not draw, and `--beside
  <screenshot>` lays the drawing beside a game screenshot. Measured against a
  screenshot of the Common Room at evening with three people, the sprites,
  the wall and the foreground agree to one level in 255. Not drawn, because
  the game does not draw them yet: a slot's own light, a cast shadow, the
  shadow's lean, a painted pose, the HUD. `--layout-dump <file>` in a
  worktree.
- **The dump's reader.** `python3 tools/game_layout.py` says whether the dump
  is fresh and what it holds. `where()`, `asleep()` and `away()` read the
  dump's `world.homes`, `world.asleep` and `world.away`; `shapes(place)`,
  `keep_tile`, `front_ids`, `name_rects`, `tips`, `hot_shape` and `frame`
  read what D60 added.

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
- `mods/roadmap/` — not a game tool: a Claude Code mod (a panel in the Claude
  desktop app) that draws `docs/roadmap.json`, the road to the finished game:
  the main goal, its phases, each phase's steps and roughly how far along
  each is. `/roadmap` opens its panel. Claude keeps `docs/roadmap.json`
  current as steps finish; the mod only reads it. The copy that runs is in
  `~/.claude/dev-mods/<session>/roadmap/`; this folder is its source, kept
  with the data it draws. Check it with the app's own engine:
  `claude plugin validate tools/mods/roadmap` and
  `claude plugin test tools/mods/roadmap` (20 tests).
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
`RENPY_SDK`. Several harnesses can run at once; the ones that need the pointer
take their turn by themselves (the pointer lock, below).

The second UI overhaul (U0a) added:
- **A bare name.** `tools/smoke.sh p2_map` is `tools/smoke/p2_map.rpy`.
- **The pointer lock.** A harness on the pointer list, or with a line
  `## smoke-pointer`, takes a machine-wide lock
  (`~/Library/Caches/jjk_smoke/pointer.lock`), waits for the other smoke runs
  to finish, and refuses with one line (exit status 3, a `result.txt` that
  says REFUSED) while a Ren'Py game that is not a smoke run is open, however
  it was started: from the launcher's "Launch Project" (`renpy.app/Contents/
  MacOS/pythonw renpy.py <project>`), with `renpy.sh`, or by hand. The
  launcher's own window does not count. Every other harness waits while the
  lock is held. It works across worktrees. `SMOKE_LOCK_WAIT` (seconds, default
  14400, four hours) is how long a run waits; `SMOKE_POINTER=1` or `0`
  overrides the list. **Exit status 3 means "run it again", never "the
  harness failed"**: a game was open, or the wait ran out. A package's
  acceptance closes the game or waits, and reruns. `tools/smoke.sh
  --open-games` prints the games a pointer harness would refuse for;
  `tools/smoke.sh --lock-selftest` checks that list against made-up process
  lines (the six ways a game is started are seen; the launcher, a smoke run,
  a lint, a compile and the tools are not).
- **A file for the repository.** A harness line `## smoke-out: <file> ->
  <path>` names a file the harness writes into its results folder and where
  it belongs; after a pass the script copies it there, or to `--out <file>`.
  `tools/smoke.sh u2_dump` rewrites `tools/art/game_layout.json`;
  `tools/smoke.sh u2_dump --out shots/art/game_layout.json` writes a local
  copy (what a worktree does: the committed file is only ever written in the
  owner's folder).
- **`SMOKE_SAVES_FROM=<dir>[:<dir>]`** with `SMOKE_SAVES=1`: the saves of
  those folders instead of the owner's.

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
for comparison; after checkpoint D `core_flow` is 26, `wp1_world` 156 and
`wp7_ui` 146):

| harness | what it checks |
|---|---|
| `p2_contracts.rpy` (129) | The frozen contracts of design section 6: every shared function's signature, owning file and return shape; every `tools/none_ok.txt` example returns `None`; icon coverage; the registries' duplicate checks; init order (with `aa_zz_order.rpy`, which adds two inert hotspots, `zz_order_spot` and `zz_tv`). It also **writes `shots/layout/defaults.json`**, the code's own layout numbers, for `layout_sheet.py`. Run it **without `SMOKE_P0_STRICT`**: its notes that a wave-0 comparison "no longer holds" are expected. |
| `p2_map.rpy` (97) | The two-level map: six markers, pins, the zoom-in, tooltips, Tokyo's districts and the night button. |
| `p2_hud.rpy` (129 after checkpoint D; 118 at the end of P8) | The corner icons and chips, the icon column for every room and period, the person view, toast lanes, the banner. Section 3b (after checkpoint D) rests the pointer on every tile of the column in every place at every period and fails if its label hides an exit, a hotspot, a corner button or the toast lane. Its last section saves and loads inside the real loop and must stay last. About 115 s. |
| `p2_journal.rpy` (188) | The five tabs, person pages, the Me page, the 70-word budget over 214 pages, checklists, Leads. **Run it with `SMOKE_TIMEOUT=300`**: it takes about 150 s of the default 180. |
| `p2_gear.rpy` (78) | Grade chips on the board, the armory and the fight header; tool and talisman checklists; nothing held is taken away. |
| `p2_night.rpy` (170) | The night rule, the Gojo night against real training days, the night in Tokyo, the Black Market and its price rule. |
| `p2_view.rpy` (130) | People blended into rooms: slots, poses, foregrounds, name tags, blink and talk, the save test in dialogue, the pose plan against the schedule. It runs the system `python3` for `install_pose.py`. About 110 s. |
| `p2_rooms.rpy` (126) | Hotspots (every action is in the room or in the column, never neither, never both), the computer, the Library, fishing, the vending machine. |
| `p2_cards.rpy` (145) | Blackjack and poker: thousands of simulated hands, the limits, rollback blocked after every deal. About 45 s. |
| `p2_paths.rpy` (110) | Exits and the five yards: the graph is connected, an exit costs no time, locked exits, the map's smaller markers. |
| `phase2_all.rpy` (35) | The whole of phase 2 end to end: `SMOKE_TIMEOUT=300 tools/smoke.sh tools/smoke/phase2_all.rpy` (about 90 s for the default 30 days; `PHASE2_DAYS` sets the days, `PHASE2_MAX_SECONDS` when the driver stops itself). A fresh game through the prologue, then the real loop played by a driver that presses what the screens offer: the map's two levels and the exits on alternate days, the journal's five tabs and a person's page, a board job a day, a page read and the cross-check, a cast, a blackjack and a poker hand, a ride with Ijichi, a night in Shibuya with a market purchase, a Gojo night, bed and one carried-home night. It writes `days.txt` (one block a day) and `driver_log.txt`. |
| `p2_saves.rpy` (188) | Saves are tested by saving: `tools/smoke.sh tools/smoke/p2_saves.rpy` (about 50 s). In one run inside the real loop it makes and reloads 22 saves (the armory, the board, a yard, the map, the computer, the journal, the person view, dialogue, blackjack, fishing at the bite, the night's menus, the market, the Gojo night, the rest day, the walk home's line) and checks each comes back on its own statement with the same state, without `load_recover`. It also rolls back through `stage_person`, through a market purchase, through the Gojo night's `new_day()` and onto the walk home's line. Not covered: a save inside a fight or on the grade card (the owner's phase-1 saves cover those). `p8_patterns/` holds the two patterns it was built from, with a README on the two load pitfalls. |
| `p2_oldsave.rpy` (21 on slot 1-1, 14 on the others) | One of the owner's saves, played on: `SMOKE_SAVES=1 SMOKE_SLOT=1-1 tools/smoke.sh tools/smoke/p2_oldsave.rpy` (about 10 s). It loads the slot (1-1 was made before phase 2), checks it lands on its statement with phase 2's variables at their defaults, plays through the real loop to the next morning, then saves and loads on the place view, the map, the person view and the journal. |

The second UI overhaul's harnesses (wave 0; each later package adds its own):

| harness | what it checks |
|---|---|
| `u2_dump.rpy` (14) | Writes `tools/art/game_layout.json`, the one file the art tools read the game's numbers from: exits and hotspots with their default and applied points, slots, frames and lanes, areas and pins, each person's canvas, the light and grade tables, the schedule, the size of each locked exit's hover label and the name tags' edges (U0d3, for `check_layout.py`), and a hash of the `.rpy` files and `game/layout/*.json` it was read from. Not pointer-dependent. `--out <file>` writes a local copy. Its header lists every key. U0n added two keys at the top level, `lit_planned` (`WORLD_LIT`) and `late` (`WORLD_LATE`), and the line that proves them; none under `world`. |
| `u2_baseline.rpy` (52 on the untouched tree) | Compares a tree with the overhaul's baselines (`baseline_u2.json`, `baseline_story_names.json`, `baseline_night_names_u0a.json`, `baseline_sprite_tree.txt`, `baseline_shots/ui2/`), one check for each part. A tool, not a member of the standing set: from U0b on, parts differ on purpose. `U2_BASELINE_WRITE=1` writes them afresh into the results folder (U0a did, once). It parks the pointer, so it takes the pointer lock. **The five pictures do not depend on the display:** before they are taken the window is set to 1280x720 pixels (half as many points on a display that draws two pixels to the point), whatever size it opened at. Should a display be unable to hold that window, ONE check fails ("pictures: the window could be made the baseline's size") and the five are not compared; that failure is about the screen, not the game. |
| `u2_home.rpy` (220) | U0b, my room in the Boys' Dormitory: bed from every place at Night, the walk garden to corridor to my room and back with no time spent, the garden's seven exits, the door and Bond rules of the three friends' rooms, who is asleep and what that hides, three saves made and loaded across the walk; and U0c1's seven places: a save in each (M), Nobara's room as her companion and out after dark (N), the Teachers' Dormitory at Night (O). Not a pointer harness. It copies three made saves from `tools/smoke/assets/ui2_saves`. Until the baselines are retaken, `u2_baseline` shows five lines that differ by U0b's planned changes (`docs/UI2_PINS.md`). |
| `u2_lit.rpy` (99) | U0n, rooms lit at Night and the two late stays (plan 5.7a, D61): `lit` as an hour's attribute in `ART_HOURS` and in every gate that builds a file name or a key from it (the cut, the pose, the light row, a `view_` file's hour tables); `WORLD_LIT` and its registration beside the untouched 56 rows of `WORLD_VARIANTS`; with no lit picture registered `bg_variant` and `bg_name` answer the same for all 35 places at every hour of the week whoever is where; with a test lit picture of the Library: lit with Megumi there or walking with me in it, dark with nobody, with a companion whose table has them elsewhere, with someone asleep, with a stale file, a missing or stale cut, and nothing different at Evening; two cache rows and `_light_key` unchanged; a replay lit by the memory's cast; no hour in the store; `world_lit_bg`; `WORLD_LATE` in `char_location` (exactly the cells the table names, against the table emptied), awake and "out", a story pin and a flag schedule win, what is offered, the stayer's own door, `person_now`; `WORLD_SHUT_NIGHT` against `place_access`; each lint refusal made to fire. Its overlay (`assets/u2_lit/`) is one plain test card, `library_lit.png`, and no manifest: rows are laid in place over an empty manifest, and the few other files a gate asks for (a cut, a pose) are answered through `renpy.loadable` for the length of a check. While the manifest is emptied, the two rooms the tests light (the Library, Megumi's room) are answered as having no foreground cut unless a check says so, so the harness reads the same with the Library's day picture and its cut installed and no lit picture yet, and with all of them installed (both states were run from test overlays in scratch). It registers the test picture itself where the tree's manifest would call it stale, so it reads the same after an art sitting. No pointer. |
| `u2_contracts.rpy` (245 with its overlay, 242 bare) | U0c2, the scaffold's contracts (`docs/UI2_CONTRACTS.md`): the manifest and the four gates that keep a stale picture, cut, pose or light row off the screen; `WORLD_VARIANTS`; `rule_layout`'s `for_rev`; the sidecar readers (the room's data, `faces.json`, pose files, hover-label sides); `path_keep_clear`; "Show names" and the held N key; `SPOT_PLANNED`; the dim state; the night, activity and Tokyo hooks with K16's test; every stub and hook of the plan's 9.3; the off-campus picture names, the board's job sites and the stand-in people; the test that settles D31; and D60, "the picture is what is clicked" (section I: the frozen names, the counting functions against `hot_shape_cases.json`, the shape rules in lint, the gates, and the shaped Courtyard: the square and the shape, the light, the layers, hidden behind a person, dimmed, names shown, faces, `hot_look.json`, pickling). **In every package's standard set, and not edited after wave 0.** It runs in two states and the acceptance is both: `tools/smoke.sh u2_contracts` (its overlay under `assets/u2_contracts/` lays test pictures and a test manifest) and `SMOKE_ASSETS=/var/empty tools/smoke.sh u2_contracts` (the tree as it ships). It sets the focus and rests the pointer on a shape, so it takes the pointer lock. The real pointer is read only when the game window is the frontmost one; otherwise the harness focuses the widget the engine picks at that point, and its NOTE "the pointer on a shape" says which of the two it did. It depends on nothing the wave is planned to add (its header lists how: the Courtyard's test sidecar and trimmed registry, the empty manifest for the gates, the stub marks). A tree that has a `game/layout/pictures.json` of its own is read with its own rows in both states: `smoke.sh` copies the overlay's test manifest over the tree's (it does not merge), so the overlay's `zz_u2c_gen.rpy` reads the tree's manifest from `SMOKE_ROOT` and lays its rows under the three test rows. It was run before the merge over a wave-1 stand-in and over a batch-0 stand-in laid in the tree's real `game/layout` (its own manifest, the Courtyard's and the Library's `hot_` and `view_` files with `for_rev` 2): both pass in both states. |
| `make_shape_overlay.py` (a tool, not a harness) | U0c2, D60. Builds the test overlay that shapes every one of the 35 places from a local dump: an 80 px square round each exit's and hotspot's applied point in `hot_<place>.json`, and a `pictures.json` that puts every picture at revision 2 with everything made from it still fresh. `python3 tools/smoke/make_shape_overlay.py --out shots/shape_overlay/all`, then `SMOKE_ASSETS=shots/shape_overlay/all tools/smoke.sh <harness>`; `--with tools/smoke/assets/<harness>` merges a harness's own overlay under it; `--rev 1` and `--for-rev <n>` build the two states in which nothing is shaped. Never committed (it refuses an `--out` inside the repository that is not under `shots/`). `--selftest` runs the counting functions of `game/sb_hotspots.rpy` (the block between its `hot_shape:` marker lines) as plain Python against `hot_shape_cases.json`, the three test shapes `tools/check_layout.py` is given too (their counts, their order, their findings, and what the layers' rule `hot_shape_layers` says of them with the hall in front). |
| `u2_mksaves.rpy` | How the nineteen made saves in `assets/ui2_saves/` were made (`U2_SAVES=campus`, `sunmall`, `warehouse`, `roster`, `prologue`). Kept as the record; the saves are not made again. |

**Hover checks need the pointer.** `p2_contracts`, `p2_hud`, `p2_map`,
`p2_journal`, `p2_view`, `p2_rooms`, `p2_paths`, `p2_cards`, `p2_saves` and
`phase2_all` hold the pointer over a button, use `renpy.set_focus`, or drive
the loop's screens. They fail while another Ren'Py window is open. Since the
second UI overhaul `tools/smoke.sh` arranges this itself (the pointer lock,
above): start them whenever you like, from any worktree, and each waits its
turn. What the lock cannot do is close the owner's game: with a game open a
pointer harness refuses, in one line. When one still fails on a hover or
tooltip check, run it again by itself before treating it as real.

**Since U0a these harnesses pin rules, not coordinates** (`docs/UI2_DESIGN.md`
K3; the lines are listed in `docs/UI2_PINS.md`): a check on an exit, a slot, a
pin or a polygon asks "inside the frame, clear of the lanes, apart from its
neighbours", and a count of art-dependent rows is read from its table. A
literal coordinate added to a harness now is a review finding.

**The strict wave-0 evidence** (the place view and person view pixel-identical
to the tree before phase 2) is `SMOKE_P0_STRICT=1` with
`SMOKE_P0_SHOTS=<repo>/tools/smoke/baseline_shots/1818x1022`. It is only
meaningful against the pre-phase-2 tree, so it is history now. The two
screenshots directly in `baseline_shots/` are 2666x1499, from before this
Mac's window size changed; the per-size folder is kept rather than retaking
them.

### `load_all_saves.sh [--from <folder> ...] [slot ...]` — the save regression

Loads every save (or just the slots named) in `game/saves` and
`~/Library/RenPy/JJKgamemd-1788928056`, each through `load_slot.rpy` with
read-only copies, and writes `shots/load_report.txt` (`LOAD_SHOTS=<dir>` puts
it elsewhere). **`--from <folder>`** (any number of times) loads the saves of
those folders instead. The second UI overhaul's save set is thirty saves:
`--from ~/Desktop/JJK_backup_ui2_20261007/snapshot` (the owner's eleven as
they stood on 7 Oct 2026, and the nineteen made on purpose), or, from the
repository alone, `--from tools/smoke/assets/ui2_saves` (the nineteen). The
table's last column gives each slot's dead return sites; `none` is wanted.
`docs/load_report_ui2_wave0.txt` is the reference for the overhaul. Names with spaces are skipped. The report's header counts the
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

`--harness-names` lets a test overlay carry a real name only through an
exception in `tools/prefixes.json` that gives both the name and its file (the
one today: `image nade` in `tools/smoke/assets/u2_contracts/game/zz_u2c_gen.rpy`,
which stands for the line `gen_sprite_defs.py` writes). `--selftest` proves
that such an exception lets through that one name in that one file and
nothing else; the rule runs the same test each time it is used.

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

The second UI overhaul's rules (`docs/UI2_DESIGN.md`; `docs/UI2_CONTRACTS.md`
A4 and A6). The first three are part of `--all`:

- `--layout-files` — every `game/layout/*.json`: a known file name, only that
  kind's keys, each key's shape; `for_rev` only where `pictures.json` calls
  the place's picture composed. `--layout-dir <dir>` reads another folder.
  Since U0c2: `faces.json` may hold `eyes` and `mouth` (a person's boxes, the
  mouth below the eyes); `pose_<district>.json` is accepted for a district of
  `WORLD_AWAY`; `light_<place>.json` may hold a `note`; `floor` is
  `{"on": [...], "off": [...]}`, `slot_light` is by hour and by slot, and
  `spare` is for the three houses with spare doors;
- `--decency` (K16) — a word list over the text of `room_bath.rpy`,
  `room_pool.rpy` and `room_tokyo.rpy`, and over every `AMBIENT`,
  `AMBIENT_STORY`, `SPOT_LINES` and `POSES` row for the Bathhouse, the Sauna,
  the Pool or a friend's room. A row wrapped onto several lines is read to
  its end, and an `AMBIENT_STORY` row for no place in particular (`None`) is
  read as one for every place. A row put into one of the three caption
  tables from outside its literal (`AMBIENT[...] = ...`, `.update(...)`,
  `.append(...)`, `.extend`, `.insert`, `.setdefault`) is read too;
- `--baths-optional` (K17) — `"bath"`, `bath_soak`, `bath_sauna`, `bath_ok`
  or `pool_swim` outside `room_bath.rpy` and `room_pool.rpy`, apart from the
  four places the plan itself puts them. In a `register_hotspot(...)` call
  only the ids are allowed: `"bath"` there (a `cond=` that reads whether I
  bathed) is a finding like anywhere else;
- `--later-notes` (not in `--all`) — "later build" and "combat update" in
  text a player can read, less the lines `tools/later_ok.txt` allows. A
  report (exit 0) until integration; `--strict` makes its lines findings.

`smoke/baseline_check_content.txt` holds the known findings of the tree as it
stood before phase 2; they are subtracted by file, rule and text (not line
number), and `--no-baseline` lists them. `--write-baseline` rewrites both
baselines and **does nothing without the second flag `--i-am-p0a-or-p8`**:
never run it in a package.

What the name rules do not read: a plain `import x`, `except ... as NAME`, a
one-line `if x: a = 1`, and names set through `setattr` or `globals()`.

### `review_pack.sh <package>` — what a reviewer looks at

`tools/review_pack.sh U3` runs the harnesses of that package's row in the
plan (and the standing set), draws a layout sheet for each of its places'
layout files, and runs the content checks, all into `shots/review/U3/` with
an `INDEX.txt`. `--list` says what it would do; `--no-harness` makes the
sheets only. A harness a later package has yet to write is listed as "not
written yet". `u2_dump`'s file goes into the pack
(`shots/review/<package>/u2_dump/game_layout.json`), never over the committed
`tools/art/game_layout.json`. Exit status: 0 when every harness that ran
passed, 1 when one failed, 3 when none failed but one was REFUSED (a game was
open, or the wait for the pointer ran out; `INDEX.txt` says which): run it
again.
