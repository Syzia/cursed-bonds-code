# The second UI overhaul: contracts

**Final for wave 0.** Started by U0a (the safety net); made final by U0c2, the
scaffold: its first sitting for everything but shapes, its second for D60
("the picture is what is clicked", B15).
`tools/smoke/u2_contracts.rpy` asserts it and is in every package's standard
set; it is not edited after wave 0. The plan is `docs/UI2_DESIGN.md`; its
section 9 says what is frozen and in what order of cost. This file is where
the exact shapes live.

- Part A: what U0a built (the saves, the baselines, the dump, the sidecars'
  shapes, the checks), with A3 and A4 brought up to date by U0c2.
- Part B: the symbols, stubs, hooks and names the scaffold froze, each with
  its example call and return shape.
- **B15: clicking the picture itself** (D60: `hot_shapes_for`,
  `hot_tip_rect`, `HOT_SHAPE`, the `shapes` and `keep_tile` keys of a `hot_`
  file, `hot_look.json`, the `hotshape_<id>` widgets), added by U0c2's second
  sitting with section I of `u2_contracts.rpy`. Nothing in Part A or in B1 to
  B14 changed shape when it landed; A3, A4, B9 and B13 gained rows.
- **B16: rooms lit at Night** (D61, plan 5.7a: the attribute `lit`,
  `WORLD_LIT`, `WORLD_LATE`, `WORLD_SHUT_NIGHT`, `world_night_up`,
  `world_lit_bg`), added by U0n, the last package of wave 0, with section J
  of `u2_contracts.rpy` (lines gained, none edited). Nothing in Part A or in
  B1 to B15 changed shape when it landed; A3, A4, B2, B3 and B6 gained rows
  in its first sitting (the game), and B13 gained the tools' `lit` in its
  second (the art tools), with A4's two refusals in `check_content.py`.

---

## Part A. Frozen by U0a (A3 and A4 as U0c2 left them)

### A1. The save set

Thirty saves. Every package's acceptance loads all of them and wants each row
as in `docs/load_report_ui2_wave0.txt`: 27 SAME, 3 MOVED for the reasons that
file gives, every "dead return sites" entry `none`, nothing RAISED.

| what | where |
|---|---|
| the owner's eleven, as they stood on 7 Oct 2026 | `~/Desktop/JJK_backup_ui2_20261007/snapshot/` (checksums in the load report) |
| the nineteen made on purpose (`u2-*.save`) | `tools/smoke/assets/ui2_saves/` (and copies in the snapshot) |
| how they were made | `tools/smoke/u2_mksaves.rpy` (not run again: a save made by a later tree proves nothing about the old one) |

```
tools/load_all_saves.sh --from ~/Desktop/JJK_backup_ui2_20261007/snapshot     # all thirty
tools/load_all_saves.sh --from tools/smoke/assets/ui2_saves                   # the nineteen, from the repository alone
```

A test names a save by what it holds (`u2-garden-night`), never by a slot of
the owner's: autosaves rotate.

### A2. The baselines (what the game answered before the overhaul)

All in `tools/smoke/`, written from commit `d2eb9db` by
`U2_BASELINE_WRITE=1 tools/smoke.sh u2_baseline`. `tools/smoke.sh u2_baseline`
compares a tree with them, one check for each part, so a package can read the
part it promised to keep. It is a tool, not part of any standard set: from U0b
on, parts of it differ on purpose.

| file | holds | who compares |
|---|---|---|
| `baseline_u2.json` | `where` and `here` (who is where, a whole week, every hour), `actions` (`place_actions` for every place and hour, a Tuesday and a Saturday), `rail`, `exits`, `links`, `hubs`, and the fixture they were read in | U0c2 ("place_actions for the 24 old places equals the baseline apart from exits"); U1's `u2_world` (the new week against the old) |
| `baseline_story_names.json` | `{file: {statement name: [kind, line, hash of diff_info()]}}` for every node of the frozen files and of U9's files, **except `sb_night.rpy`** | U9's `u2_names`; U7 |
| `baseline_night_names_u0a.json` | the same for `sb_night.rpy` before U0c2 | U0c2 (every node outside its edited init blocks keeps its name); **U0c2 then adds `game/sb_night.rpy` to `baseline_story_names.json` as its last step** |
| `baseline_sprite_tree.txt` | what `lit_sprite` builds for Yuji, with and without the blink and talk pictures, and the sha256 of its pickle (K9). Built from his real arguments, read from the `image yuji = lit_sprite(...)` line of `game/jjk_sprites.rpy` | U3's `u2_blend`; **L rewrites it** (see below) |
| `baseline_shots/ui2/` | `place.png`, `person.png`, `map_campus.png`, `map_area.png`, `main_menu.png`, and `shots.json` (the pictures' size, the fixture, each file's sha256) | U0c2 ("pixel-identical to U0a's") |

A statement's name is `json.dumps(node.name)`: a label's name, or
`["game/<file>.rpy", <version>, <serial>]`. Its hash is the first 16 hex digits
of `sha1(repr((class name,) + diff_info()[1:]))`. Two nodes with one name and
one hash are the same statement to a save.

The pictures are 1280 x 720. `u2_baseline` sets the window to that many pixels
before it takes them (half as many points on a display that draws two pixels
to the point), so they do not depend on the size the window opens at, which
follows the display in use. They compare byte for byte. When a display cannot
hold that window, one check fails, "pictures: the window could be made the
baseline's size", and the five are not compared: that is about the screen and
is not a change in the game. The baseline was taken on a display of scale 1.0
(`shots.json`, `scale`); on a display of another scale a run that fails all
five pictures and nothing else is first suspected of the display, and the
check says so. **For U0c2** ("pixel-identical to U0a's"): the evidence is the
five `picture:` lines of `tools/smoke.sh u2_baseline` reading PASS, with the
`pictures:` line above them. **The picture evidence is taken with the external
monitor as the main display** (scale 1.0), as the baseline was. On the
laptop's own panel (two pixels to the point) the five have never been
compared: nobody knows yet whether a 640 x 360 point window there gives the
baseline's bytes. It is tried once at checkpoint A, or whenever the monitor is
unplugged; if the five differ there, U0a's harness is changed so that a
display of another scale gets the one `pictures:` line ("taken at scale 2.0,
baseline at 1.0: not compared") and not five failures.

**The sprite tree and Yuji's new set (D57).** The pickle holds Yuji's feet
numbers, today `(389, 1365, 313)`. L replaces his whole set during wave 1 and
measures his feet and contact shadow again, so from that install the line
"K9: and its pickle is byte for byte what it was" differs by design, and so
does any comparison U3's `u2_blend` makes with the pickle's hash. That is not
a change to `lit_sprite`. The line "K9: lit_sprite builds the tree it built"
stays meaningful and must still pass. **L**, in the commit that installs the
set: first see that tree line pass, then rewrite the file with
`U2_BASELINE_WRITE=1 tools/smoke.sh u2_baseline` and commit only
`tools/smoke/baseline_sprite_tree.txt` from what that run wrote (the other
baselines are not rewritten). **U3**: a pickle difference before L's install
is a finding; after it, compare with the rewritten file.

### A3. `tools/art/game_layout.json` (the one file the art tools read the game through)

Written by `tools/smoke.sh u2_dump` (D47, 5.4). Committed only from the owner's
folder; a worktree writes a local copy with
`tools/smoke.sh u2_dump --out shots/art/game_layout.json` and passes it to the
tools with `--layout-dump`. Two runs on one tree give the same bytes.

| key | shape |
|---|---|
| `format` | `1` |
| `hash` | sha256, hex. Over every `game/*.rpy` (names starting `zz_` or `aa_zz_` left out) and every `game/layout/*.json`, in name order of their paths from `game/`; for each file `path + "\0" + sha256(bytes).hexdigest() + "\n"`. |
| `files` | the paths the hash covers |
| `screen` | `[1920, 1080]` |
| `places` | list, in `LOC_ORDER`: `{key, name, indoor, bg, file, variants: {period: attribute}, area, hub, zoom, y}` |
| `exits` | `{place: [{to, id, default: [x, y], applied: [x, y]}]}`, in `path_exits` order; `id` is `go_<from>__<to>` |
| `hotspots` | `{place: [{id, kind, act, icon, default, applied, front, standalone, when}]}` (exits are not repeated here) |
| `spot_planned` | `[[id, place, kind]]`; `[]` until U0c defines `SPOT_PLANNED` |
| `slots` | `{place: {"1".."4": [[x centre, y offset, zoom, far]]}}`, what `view_slots` answers at Noon |
| `slots_code` | `VIEW_SLOTS`, the code's own rows |
| `poses` | `{place: {"<who>" or "<who>__<variant>": [x, y, w, h]}}` (the `pose_` file over the `view_` file's key) |
| `areas` | list, in `AREAS` order: `{key, name, places, hub, anchor, bg, spots: {place: {default, applied}}}` |
| `frames` | `hot_bounds [x0, y0, x1, y1]`, `hot_size`, `hot_lanes [[x, y, w, h], ...]`, `caption_box`, `path_apart`, `path_clear`, `keep_clear`, `map_pin_frame`, `map_mountain_box`, `map_pin`, `map_area [w, h]`, `stage_x [40, 1700]`, `sprite [760, 1400]`, `tag_y`, `rail {tile, gap, bottom, top, top_inner, max, columns}` |
| `people` | `{who: {file, canvas: [w, h], feet: [x centre, sole row, width]}}` |
| `grade` | `{outdoor, indoor}`, each `{period: [tint, brightness]}` |
| `light` | `{neutral, outdoor, indoor, place, bg}`; a `place` key is `"<place>"` or `"<place> <variant>"` |
| `schedule`, `weekend` | `SCHEDULE`, `WEEKEND` |
| `periods`, `weekdays`, `fg_rooms`, `fg_talk` | lists |

A tool that finds the hash out of date refuses with exactly: `the game's
layout has changed since the dump was written: run tools/smoke.sh u2_dump`.
**Added by U0c2** (new keys; none of the keys above changed shape):

| key | shape |
|---|---|
| `spot_planned` | now filled: the 59 rows of `SPOT_PLANNED`, `[[id, place, kind]]` |
| `variants_planned` | `WORLD_VARIANTS`: `[[place, period, attribute, file]]`, 56 rows |
| `keep_clear` | `{place: [[x, y]]}`, what `path_keep_clear(place)` answers (`frames.keep_clear` is the old table, kept) |
| `tips` | `{place: {id: side}}`, the hover-label sides a `hot_` sidecar gives |
| `faces` | `{who: {eyes, mouth, blink_also}}` as the game reads them (`faces.json` first, then the tables) |
| `world` | `inside`, `pinless`, `homes`, `asleep`, `away` (`{who: {"<weekday> <period>": district}}`), `door_bond` and `door_owners` by place |
| `standins` | `copies {lender: file}`, `names {image key: lender}`, `if_file {image name: file}`, `people` |
| `names_key` | `"K_n"` |

**Added by U0c2's second sitting (D60)**, new keys again:

| key | shape |
|---|---|
| `hot_shape` | `HOT_SHAPE`: the limits `polys [1, 3]`, `points [3, 60]`, `area_min 5184`, `area_max 0.4`, `buried_max 0.5`, `grid 4`, the HUD's row `top 92` (above that y no shape takes the pointer), and the light's default look `color`, `wash`, `edge`, `dim`, `names`, `blur`, `line` |
| `hot_look`, `look_keys` | the look in force (`HOT_SHAPE`'s with what `hot_look.json` replaces), and the keys that file may hold |
| `shapes` | `{place: {id: [polygon, ...]}}`: what each `hot_` sidecar holds under `shapes`, as written, whatever the picture's revision; a place with none is left out |
| `keep_tile` | `{place: {id: reason}}` |
| `shaped` | the places that are shaped now (`hot_shapes_for` answers), in `LOC_ORDER` |
| `name_rects` | `{place: {id: [x, y, w, h]}}`: for every registered hotspot and exit, where its name plate is drawn in a shaped place while names are shown (`hot_name_rect` at its applied point). **Measured standing in each place in turn** (`here` is set to the place while its rectangles are computed), so the place's own `tips` rows decide the side each plate lies on, as in the game. `check_layout.py` refuses a place where two meet |

**Added by U0d3 (the layout check)**, four keys more, written by
`tools/smoke/u2_dump.rpy` from that package on:

| key | shape |
|---|---|
| `lock_labels` | `{place: {exit id: [w, h]}}`: for every exit the game can lock, the size of the hover label that says why it is locked, as `icon_tip_size` measures it at its largest over the five periods (no flag, no Bond); a place with no such exit is left out. `check_layout.py` refuses a layout in which that label would leave the screen or cover another exit or the arrival caption (`lock-label`) |
| `frames.tag_edges` | `[x left, x right]`: the edges a row's name tags are kept between (179 and 1700) |
| `frames.tag_gap` | the gap `view_tag_xs` keeps between two name tags, in px |
| `frames.tag_w` | the widest name tag of the cast, in px. With the two above, `check_layout.py` lays out each row's tags and refuses a row that does not fit (`tag-x`) |

**Added by U0n (rooms lit at Night, B16)**, two keys at the top level and
none under `world`, whose seven keys a line pins:

| key | shape |
|---|---|
| `lit_planned` | `WORLD_LIT`: `[[place, file]]`, 8 rows: every room that has a second Night picture, the room lit (`images/bg/<stem>_lit.png`) |
| `late` | `WORLD_LATE`: `{who: {"place": place, "days": [weekday, ...]}}`: who is out late, in which room, on which Nights |

**The committed file is regenerated in the owner's folder after U0c2 merges**
(`tools/smoke.sh u2_dump`), never from a worktree.

### A4. Sidecars (`game/layout/`), as `check_content.py --layout-files` enforces them

Every file is one JSON object; every key is optional unless it says otherwise;
lists, not tuples. An unknown file name or an unknown key is a finding.

| file | keys |
|---|---|
| `hot_<place>.json` | `spots {id: [x, y]}` (a hotspot's id, registered or planned in `SPOT_PLANNED`, or an exit's `go_<from>__<to>`); `tips {id: "top" / "bottom" / "left" / "right"}` (the same ids; read by `icon_tip_side`); `shapes {id: [polygon, ...]}` (D60: one to three polygons, each a list of 3 to 60 `[x, y]`; the same ids); `keep_tile {id: "<why it keeps its button>"}` (D60: a non-empty string; an id is under one or the other; it means nothing without `shapes`); `spare [[x, y], ...]` (the three houses painted with spare doors only: `boys_dorm`, `girls_dorm`, `teachers_dorm`; read by the tools, never by the game); `for_rev` |
| `hot_look.json` | D60, the light of a shaped hotspot: `color` (`"#rrggbb"`), `wash`, `edge`, `dim`, `names` (each a number from 0 to 1); every key optional, `HOT_SHAPE`'s value otherwise. Written by L on the owner's word. (It is not a place's file: there is no place `look`.) |
| `view_<place>.json` | `slots {"1".."4": [[x centre, y offset, zoom(, far)], ...]}` (key `n` holds `n` rows); `poses {key: [x, y, w, h]}` (the older home of pose boxes: still read, after `pose_<place>.json`); `floor {"on": [polygons], "off": [polygons]}` (`on`: one or more polygons people may stand on, required when the key is there; `off`: optional; a polygon is three or more `[x, y]`); `scale [x, y top, y bottom]`; `slot_light {hour: {"1".."4": [one entry a slot: null or ["#rrggbb", brightness]]}}` (key `n` holds `n` entries, in the slots' order); `cast {hour: [direction, length, darkness]}`; `talk` (true or false); `for_rev` |
| `pose_<place>.json` | `poses {key: [x, y, w, h]}` (required). `<place>` is a place key or a Tokyo district of `WORLD_AWAY` (`harajuku`, `shibuya`). A key is `<who>`, `<who>__<variant>` or `<who>__<variant>__asleep` |
| `light_<place>.json` | `""`, `"evening"`, `"night"`, and `"lit"` for a room with a lit picture (U0n, B16): each a row `["#rrggbb", brightness, saturation, shadow opacity]`, or the same with `[shadow lean in px, shadow stretch]` after it (the installer writes six); `note` (a string, the installer's own words; not read by the game) |
| `light.json` | `{image name: row}` (`"bg alley"`); read by `light_for_bg` before `BG_LIGHT` |
| `area_<key>.json` | `spots {place: [x, y]}`; `for_rev` |
| `map_campus.json` | `anchors {area key: [x, y]}`; `mountain_box [x0, y0, x1, y1]` |
| `faces.json` | `blink_also {who: [faces]}`; `eyes {who: [x, y, w, h]}`; `mouth {who: [x, y, w, h]}` (D57). Boxes are on the sprite canvas (inside 880 x 1400); for one person the mouth box starts at or below the foot of the eye box. Read by `view_blink_also` and `view_face_box` before `VIEW_BLINK_ALSO` and `VIEW_FACE` |
| `pictures.json` | `pictures {key: {rev, kind ("composed" / "inplace" / "relight"), batch, render, record, rev1_commit, from_commit, shift [dx, dy], sharp [a, b], of, of_rev, waiver}}`; a row holds `rev`, or `of` with `of_rev`. `batch` is a number for a whole batch (`0`, `3`) and a string for one file of a batch (`"3a"`) |

An hour is `""` (the day picture), `"evening"` or `"night"`; a period name is
accepted as well, and where both fit the period's own row is read first.
**U0n (B16):** `"lit"` is an hour too, the room at Night with someone up in
it: the game reads a `view_` file's `slot_light` and `cast` and a `light_`
file under `"lit"` while the lit picture shows. A `Night` key in a `view_`
file would serve both of a room's Night pictures, so
`check_content.py --layout-files` knows `"lit"` and refuses a `Night` key in
the `slot_light` or `cast` of a place of `WORLD_LIT` (write `"night"` and
`"lit"`); `"lit"` in a `light_` or `view_` file of any other place is a
finding too. The checker reads the eight places from `world_lit_rows()` in
`sb_world.rpy`'s own text and says so if it can no longer read them
(`check_content.py --selftest` holds each of these).
`for_rev` is a whole number from 1; in a `hot_` or `view_` file it is a
finding unless `pictures.json` calls that place's picture `composed` (a room
redone in place carries none, plan 3.2). The game ignores a file whose
`for_rev` is not its picture's revision and lint says so (`rule_validate`).

**The manifest's keys** (plan 5.5). A picture's key is its file stem
(`courtyard`, `your_room` for My Room, `dorm_common_evening`). What is made
from a picture is keyed by the PLACE key and names its parent picture:

| key | row | made from |
|---|---|---|
| `<stem>_evening`, `<stem>_night` | `{rev, kind: "relight", of, of_rev}` | the day picture `<stem>` |
| `<stem>_lit` (U0n; `library_lit`, `your_room_lit`) | `{rev, kind: "relight", of, of_rev}` | the day picture `<stem>` |
| `fg_<place>[_<hour>]` | `{of, of_rev}` | the place's picture for that hour |
| `light_<place>[_<hour>]` | `{of, of_rev}` | the same |
| `pose_<place>__<who>[__<variant>][__asleep]` | `{of, of_rev}` | the place's picture for the variant |

In the three rows below it `<hour>` and `<variant>` may be `lit` as well
(`fg_library_lit`, `light_library_lit`, `pose_library__megumi__lit`), made
from `<stem>_lit` (`ART_HOURS` is `("evening", "night", "lit")`).

Something with a row is fresh while its parent is at the row's `of_rev`;
something with no row is fresh while its parent is at revision 1; and what was
made from a stale picture is stale too (`art_fresh`).

**The keep list** (`tools/bgs/keep/<stem>.json`, U0d2's): `keep`, `empty`,
`allow`, `change`, `doors`.

### A5. Names (`tools/prefixes.json`)

Opened once by U0a and frozen again. New rows: `art_manifest.rpy` (`art_`),
`room_bath.rpy` (`bath_`), `room_pool.rpy` (`pool_`), `room_tokyo.rpy`
(`tky_`), `ui_hints.rpy` (`hint_`), `jjk_defs.rpy` (`standin_`). Added to
existing rows: `screens.rpy` + `sys_`; `gui.rpy` + `gui.sys_`;
`bg_placeholders.rpy` + `standin_` and + `bg ` (any image named `bg ...`: the
stand-in pictures of the new places and of the off-campus names are defined
there). Exceptions: the labels `district_harajuku` and `district_shibuya` in
`room_tokyo.rpy`; the label `act_swim_pool` in `room_pool.rpy`; `SPOT_PLANNED`
in `sb_hotspots.rpy`; `persistent.show_names` in `ui_icons.rpy` or in
`screens.rpy`, whichever holds its `default`.

### A6. The checks (`tools/check_content.py`)

`--all` now also runs `--layout-files` (A4), `--decency` (K16) and
`--baths-optional` (K17). All three are clean today and a finding is a failure
for the package that wrote the line.

- `--decency`: the words towel, naked, undress, strip, swimsuit, bikini, skin,
  bare, changing (and their plain endings), in the strings of `room_bath.rpy`,
  `room_pool.rpy`, `room_tokyo.rpy`, and in any `AMBIENT`, `AMBIENT_STORY`,
  `SPOT_LINES` or `POSES` row whose place is `bathhouse`, `sauna`, `pool`,
  `yuji_room`, `megumi_room`, `senpai_room`, `nobara_room` or `maki_room`. A
  row may be wrapped onto several lines: every line of it is read. An
  `AMBIENT_STORY` row whose place is `None` shows everywhere, so it is read
  too. (A new caption table would not be read: captions go in these two.)
  A caption belongs inside the table's own literal. A row put in from
  outside it (`AMBIENT[(who, place)] = ...`, `AMBIENT.update({...})`,
  `AMBIENT_STORY.append(...)`, `SPOT_LINES[id] = ...`, also `.extend`,
  `.insert`, `.setdefault`) is read as well when the statement names one of
  those places or a hotspot of one, or, for `AMBIENT_STORY`, `None`; a row
  added any other way (through another name, `setattr`, a loop over a second
  table) is not read and is a review finding.
- `--baths-optional`: `"bath"`, `bath_soak`, `bath_sauna`, `bath_ok`,
  `pool_swim` anywhere under `game/` outside `room_bath.rpy` and
  `room_pool.rpy`, except in `ICONS` / `ICON_FOR` (`ui_icons.rpy`),
  `SPOT_PLANNED` (`sb_hotspots.rpy`), the ids (never `"bath"`) in a
  `register_hotspot(...)` call, and
  `NIGHT_REST_BLOCKS` (`sb_night.rpy`).
- `--later-notes` (asked for by name; not in `--all`): "later build" and
  "combat update" in player-visible strings, less the rows of
  `tools/later_ok.txt` (file, a tab, a piece of the line, a tab, why). A
  report until integration; U10 runs it with `--strict`.

### A7. `tools/smoke.sh`

- `tools/smoke.sh <name>` is `tools/smoke/<name>.rpy`.
- **The pointer lock (K13).** A harness on the pointer list (`p2_contracts`,
  `p2_hud`, `p2_map`, `p2_journal`, `p2_view`, `p2_rooms`, `p2_paths`,
  `p2_cards`, `p2_saves`, `phase2_all`, `u2_map`), or one with a line
  `## smoke-pointer`, takes the machine-wide lock
  `~/Library/Caches/jjk_smoke/pointer.lock`, waits for the other smoke runs to
  finish, and refuses (one line, exit status 3, `RESULT FAIL` with the word
  REFUSED) while a Ren'Py game that is not a smoke run is open, whether it was
  started from the launcher, with `renpy.sh` or by hand. Every other
  harness waits while the lock is held. A run waits up to four hours
  (`SMOKE_LOCK_WAIT`). **Exit status 3 is "run it again" (close the game, or
  wait), never a failed harness.** **A new harness that hovers or calls
  `renpy.set_focus` or `renpy.set_mouse_pos` carries `## smoke-pointer`.**
- `## smoke-out: <file> -> <path>`: the harness writes `<file>` into
  `$SMOKE_SHOTS`; after a pass the script copies it to `<path>` in the
  repository, or to the file `--out` names.
- `SMOKE_SAVES_FROM=<dir>[:<dir>]` with `SMOKE_SAVES=1`: a snapshot's saves
  instead of the owner's.

### A8. Harness lines turned into rules (K3), and the ledger

`docs/UI2_PINS.md`. A literal coordinate or an art-dependent count added to a
harness after this is a review finding.

### A9. Budgets (K11), as the harnesses now hold them

Places: `len(LOC_ORDER)` (24 today, 35 after wave 0). Words on an area view:
at most 18. Buttons on an area view: at most 11 (six pins and five buttons).
Exits from a yard: at most 7 and equal to its table. Icons: the count the
sheets in `tools/icons/` hold (88 today, 114 after U0b's sheet 4). Tiles in
the icon column: at most 8, not loosened.

---

## Part B. Frozen by the scaffold (U0b, U0c1, U0c2)

`tools/smoke/u2_contracts.rpy` asserts this part: each function's owning file
(`fn.__code__.co_filename`), its signature and its return shape. A wave
package that fills a stub keeps all three. The harness runs in two states,
with its overlay and without (`SMOKE_ASSETS=/var/empty`); both pass.

### B1. Home (K1)

The place key `dorm`; its image `bg your_room` and files `your_room*.png`;
`default here = "dorm"`; `label sb_do_path_dorm`. None of them ever changes
and there is no HOME constant. `art_stem("dorm") == "your_room"`.

### B2. The eleven place keys

`boys_dorm`, `yuji_room`, `megumi_room`, `senpai_room`, `nobara_room`,
`maki_room`, `teachers_lounge`, `teachers_dorm`, `bathhouse`, `sauna`, `pool`.
Each has the image `bg <key>`, the file `images/bg/<key>.png` (a stand-in
until it is painted: `standin_bg(key, src, matrix, **kw)` in
`bg_placeholders.rpy`), the label `sb_do_path_<key>` and the action
`path_<key>`. An hour picture is `bg <key> evening` / `night`, from
`images/bg/<key>_evening.png` / `_night.png` (B6). A key that reaches a save is
never removed. **U0n (B16):** the five friends' rooms (`yuji_room`,
`megumi_room`, `senpai_room`, `nobara_room`, `maki_room`) also have
`bg <key> lit`, from `images/bg/<key>_lit.png`: the room with its lamp on,
shown at Night while its owner is up in it; `bg <key> night` is the room dark.

### B3. The world's tables (`sb_world.rpy`; U0b, U0c1; final)

| name | shape |
|---|---|
| `WORLD_INSIDE` | `{room: house}`, one level deep. `world_inside(loc)` → the house's key or None |
| `WORLD_PINLESS` | a tuple of place keys with no map pin. `world_pinned(loc)` → bool |
| `WORLD_HOMES` | `{who: place}`. `world_home(who)` → a place key or None |
| `WORLD_DOOR_OWNERS` | `{place: (who, ...)}`. `world_door_owners(loc)` → a list of person keys |
| `WORLD_DOOR_BOND` | `{None: 15}`; a row `{"maki_room": 25}` would set one door apart. `world_door_bond(loc)` → an int, or None for a place with no Bond door |
| `WORLD_ASLEEP` | `{"weekday": (who, ...), "weekend": (who, ...)}`. `world_asleep(who, per=None)` → bool, the only reader |
| `WORLD_AWAY` | `{who: {(weekday, period): district}}`. `world_away(who, per=None)` → a district key or None |
| `world_home_state(who, per=None)` | `"awake"`, `"asleep"` or `"out"` |
| `world_room_state(loc)` | `{owner: one of those}`; `{}` for a place that is nobody's home |
| `WORLD_VARIANTS` | a tuple of `(place, period, attribute, file)`: the 56 planned new hour pictures (B6) |
| `WORLD_LIT` (U0n, B16) | a tuple of `(place, file)`: the rooms with a second Night picture, lit. `WORLD_LIT_ON` → `{place: file}` for the rows that registered; `WORLD_LIT_ATTR` → `"lit"` |
| `WORLD_LATE` (U0n) | `{who: (place, (weekday, ...))}`. `world_late_cell(who, per=None)` → the room the table has them in tonight, or None |
| `WORLD_SHUT_NIGHT` (U0n) | a tuple of the places `place_access` shuts at Night |
| `world_night_up(loc, per=None)` (U0n) | bool: at Night somebody is up in this place |

`place_access(loc)` keeps its signature and returns `(bool, reason, short
tag)`. The flag `door_<place>` opens any place; a house is always open from
one of its own rooms; a room inside a house asks its house first; **the Bond
clause applies only to a place that has a house** (`world_inside`): the girls'
corridor has owners too, and its own rule (after dark). The flags
`welcome_<room>` and `invited_girls_dorm` are U1's to set. `person_now(who)`
keeps exactly its six keys. A hotspot's `when` is how a later quest shows one
(D49); no new contract.

Also laid in wave 0 and final: `PATH_HOUSE_EXITS = 7`, `PATH_YARD_ICONS`
(`room_paths.rpy`); `map_pins(key)`, `map_marks()`, `map_mission_asleep`
(`ui_map.rpy`); `rail_asleep_line(loc)` and its line in `screen sb_place`
(`sb_screens.rpy`; U4 keeps it or replaces it with the bed tags). The
`ICON_TIP_SIDES` row for `hot_go_dorm_yard__boys_dorm` goes when the garden's
sidecar brings `tips`.

### B4. Action ids, labels and hotspot ids

- Actions (the loop calls `"sb_do_" + id`): `path_<key>` for the eleven keys;
  `bath_soak`, `bath_sauna`, `pool_swim` (registered, closed, by the stubs);
  `cards_invite` (registered by U5).
- The activity `swim_pool` and its label `act_swim_pool(who)` (the loop calls
  `"act_" + id`). Its row is last in `ACTIVITIES`: `swim`'s kind, Bond 35,
  cost and hours, `loc=("pool",)`, `when="pool_ok"`.
- Labels: `district_harajuku`, `district_shibuya` (the frozen `sb_trip` calls
  `"district_" + key`), `tky_people(key)`.
- **`SPOT_PLANNED`** (`sb_hotspots.rpy`): 59 rows of `(id, place, kind)`, kind
  `"look"` or `"act"`. Wave 1 registers exactly these ids in these places as
  these kinds, and nothing else. A hotspot's widget id and tooltip key are
  `hot_<id>`.

| place | looks | actions (the action each stands for) |
|---|---|---|
| `gate` | `gate_pond` | |
| `courtyard` | `gateway` | `straw_posts` (`train`, "Practice") |
| `school_yard` | `pine_bench` | |
| `classroom` | `notices` | `front_desk` (`study`) |
| `cafeteria` | `water_cooler` | |
| `infirmary` | `shoko_desk` | |
| `library` | `reading_table` | |
| `dorm_yard` | `pond`, `lit_windows` | |
| `dorm` | `wardrobe`, `window` | `desk` (`study`) |
| `dorm_common` | `fridge`, `game_boxes`, `manga_shelf` | (`card_table` keeps its id) |
| `girls_dorm` | `plant` | |
| `rooftop` | `rooftop_view` | `railing` (`think`, "Sit a while") |
| `boys_dorm` | `shoe_rack`, `notice_board` | |
| `yuji_room` | `film_shelf`, `bed_yuji` | |
| `megumi_room` | `bookshelf`, `bed_megumi` | |
| `senpai_room` | `shogi_board`, `bed_panda`, `bed_toge` | |
| `nobara_room` | `mirror`, `bed_nobara` | |
| `maki_room` | `weapon_case`, `bed_maki` | |
| `staff_yard` | `stone_lanterns` | |
| `office` | `dolls`, `photograph` | |
| `utahime_office` | `binders` | |
| `gojo_office` | `gojo_tv`, `sweets` | |
| `teachers_lounge` | `rota`, `kettle` | |
| `teachers_dorm` | `workbench`, `name_plates` | |
| `training_yard` | | `striking_posts` (`train`) |
| `training` | `mats` | `straw_bundles` (`train`) |
| `dojo` | `wall_shrine` | `weapon_rack` (`train`) |
| `storehouse` | `big_chest` | |
| `pool` | `lane_board` | `pool_swim` |
| `trailhead` | `standing_stone` | |
| `forest` | `stone_markers` | |
| `riverside` | `waterfall` | `deep_pool` (`swim`) |
| `bathhouse` | `milk_fridge` | `bath_soak` |
| `sauna` | `bucket` | `bath_sauna` |

(`ridge` keeps `veil`, which exists.) The six bed tags are looks registered
with a `when` that is true only while that person is asleep in the room.
`cards_invite` is a tile of the icon column, not a hotspot.

### B5. The saved sprite (K9)

`tools/smoke/baseline_sprite_tree.txt` (A2). `lit_sprite`, `_sprite_light`,
`_shadow_light`, `view_blink_fn`, `view_talk_fn`, `view_breathe_fn`,
`hot_pulse_fn`, `view_enter_ease`, `char_focus` and every `pos_*` transform
keep their names, signatures and shapes. `view_face_layers(path)` builds the
same two layers; only which faces and which boxes come from data.

**D31 is settled** (`u2_contracts`, section G): a painted pose kept in place
by the person view's screen is screen-only. What a save made on that screen
pickles holds no displayable of the pose picture (the same picture *shown* as
an image is held). U3 may build 6.2 row 8, as long as the patch is added by
the screen and never by a `show`.

### B6. Pictures, revisions and the gates (`art_manifest.rpy`, new)

| symbol | example | returns |
|---|---|---|
| `art_rev(stem)` | `art_rev("courtyard")` | int; 1 when the manifest has no row |
| `art_fresh(stem, of=None, depth=0)` | `art_fresh("dorm_common_evening")`, `art_fresh("fg_dorm")`, `art_fresh("pose_dorm_common__nobara__evening")` | bool (A4, "The manifest's keys"). `of` names the parent of a thing with no row; without it the parent is read from the name |
| `art_stem(loc)` | `art_stem("dorm")` → `"your_room"` | a place's picture stem |
| `art_validate()` | | lint findings for the rows' shapes. A stale row is not a finding (`tools/art_status.py` lists those) |

With no `pictures.json` every picture is revision 1 and the game is as it was.
`ART_PICTURES` is init data, never saved.

The four gates (K7), each falling back to what the game does when the file is
missing:

| gate | file | a stale thing is not used, and then |
|---|---|---|
| `bg_variant(loc, per)` (unchanged signature) | `sb_world.rpy` | the attribute or None. None for an hour picture made for a day picture that has been replaced, and, in a room with a foreground (`images/fg/fg_<loc>.png` exists), for an hour picture whose own cut is missing or stale: the day picture, tinted |
| `view_fg_path(loc, per=None)` | `view_stage.rpy` | None: no cut is laid, and a room of `VIEW_FG_ROOMS` stands people on the plain slots |
| `view_pose(who, loc, per=None)` | `view_stage.rpy` | None: the standing sprite |
| `light_for_place(loc, per)` (unchanged signature) | `lighting.rpy` | the general row (`PLACE_LIGHT`, then the indoor or outdoor row) |

`WORLD_VARIANTS`: a row whose file is loadable and fresh defines
`bg <picture> <attribute>` and sets `TIME_VARIANT[place][period]` at init,
over a static cell too (My Room's Evening is `night` today and becomes
`evening` when `your_room_evening.png` lands). A row whose file is missing
does nothing. Lint reports a `TIME_VARIANT` cell with no image.

**U0n (B16):** `bg_variant` also answers `"lit"`, at Night only, for a place
of `WORLD_LIT_ON` whose lit picture is ready (`world_lit_ready(loc)`:
loadable, fresh against the day picture, and with its own cut
`images/fg/fg_<loc>_lit.png` where the room has a foreground) while
`world_night_up(loc)` is true; otherwise exactly the answer above. The other
three gates take the attribute from it and build `fg_<loc>_lit.png`,
`pose_<loc>__<who>__lit.png` and the light row under `"lit"` as they build an
hour's. `WORLD_LIT`: a row whose file is loadable and fresh defines
`bg <picture> lit` at init and is noted in `WORLD_LIT_ON`; it sets no
`TIME_VARIANT` cell, and a row whose file is missing does nothing.

`rule_layout(name)` (`sb_rules.rpy`, unchanged signature): the sidecar as a
dict, a fresh copy each call; `{}` for a file that does not exist and for one
whose `for_rev` is not its picture's revision (`hot_`/`view_` + place: the
place's picture; `area_<key>`: the area's map). A file with no `for_rev` is
always read. The mismatch is reported by `rule_validate` (lint) and by no
other validator.

### B7. The light row

Four values `(tint "#rrggbb", brightness, saturation, shadow opacity)`, or six
with `(shadow lean in px, shadow stretch)` last; four means `(0, 1.0)`.
`scene_light` (saved) may hold either. `light_matrix` reads the first three,
`_shadow_light` the fourth. **Drawing the lean and the stretch is U3's**
(6.2 row 3): today the two values are carried and not drawn.

| symbol | returns |
|---|---|
| `light_row(loc, variant=None)` | the measured row of `light_<loc>.json` as a tuple of four or six, when well formed and fresh; else None |
| `light_for_place(loc, per)` | the measured row for the picture showing (its hour picture's row; the day row in the Morning, at Noon and in the Afternoon), else the tables as before. **In an Evening or a Night that is only a tint the general row stays** until U3's `light_follow` |
| `light_follow(row, grade)` | not there in wave 0; U3 adds it to `lighting.rpy` (plan 3.2, 6.2 row 2). **Its presence in the store is what marks U3's light**: while there is no such function `u2_contracts` asserts the general row at a tinted hour; once there is, it notes so and asserts only that `light_for_place` answers a well-formed row there that is neither the night picture's measured row nor the day row unchanged. So U3 changes the tinted hour's light in the same commit that adds `light_follow`, under that name |
| `light_for_bg(name)` | `light.json`'s row, then `BG_LIGHT`, then a campus picture's measured row or `PLACE_LIGHT`; a story picture's variant with no row keeps its base's |

### B8. The room's data (`view_stage.rpy`)

Every key of `view_<place>.json` is optional and without it the room is as it
was.

| symbol | returns |
|---|---|
| `view_floor(loc, off=False)` | a list of polygons (lists of `(x, y)`) or None; for the review tools |
| `view_slot_light(loc, n, i, per=None)` | `(tint, brightness)` or None. **Applying it is U3's** (6.2 row 5) |
| `view_cast(loc, per=None)` | `(direction, length, darkness)` or None. **Drawing it is U3's** (row 9) |
| `view_talk(loc)` | bool: the sidecar's `talk`, else `loc in VIEW_FG_TALK`; `view_enter` reads it |
| `view_pose_box(loc, key)` | the box from `pose_<loc>.json`, then from `view_<loc>.json`'s `poses` |
| `view_blink_also(who)` | a tuple of faces: `faces.json`, then `VIEW_BLINK_ALSO` |
| `view_face_box(who, key)` | `(x, y, w, h)` or None, key `"eyes"` or `"mouth"`: `faces.json`, then `VIEW_FACE` |
| `view_slots`, `view_slot_rects`, `view_person_rects`, `view_motion`, `char_focus` | unchanged |
| `label stage_person(who, expr=None)` (`sb_activities.rpy`, not this file) | unchanged |

### B9. Exits and hotspots

| symbol | file | returns |
|---|---|---|
| `path_keep_clear(loc)` | `room_paths.rpy` | a list of `(x, y)`: the place's own registered hotspots where they sit now (the sidecar applied), each point once; ids that begin `zz` (a harness's) are left out |
| `path_faces(to)` | `room_paths.rpy` (a stub: `[]`; U2) | a list of person keys, three at most (`hot_faces` cuts a longer list to its first three, and `u2_contracts` asserts that) |
| `path_hub`, `path_exits`, `path_neighbours` | | unchanged. `path_validate`'s spacing rules read each exit's applied point |
| `register_hotspot`, `hot_spots_for` (the same eleven keys), `hot_covers`, `screen hot_layer(loc, front=False)` | `sb_hotspots.rpy` | unchanged |
| `hot_set_dim(hot_id, fn)` | | None. `fn` is the NAME of a store function that returns a reason (a str) or `""`. While it gives a reason `hot_layer` draws the hotspot at `HOT_DIM_ALPHA` (0.45), its hover label says the reason and pressing it does nothing. (Separate from `register_hotspot`, whose signature is frozen.) **Only a hotspot `hot_spots_for` returns is drawn**: for an action hotspot U5 keeps the place action offered while it is dim (`hot_spots_for` drops an action hotspot whose place action is not offered), and the action's own label must refuse too, since the tile for the same action in the icon column is not dimmed by `hot_layer`. U5 names the card table's. `HOT_DIM` is `{hotspot id: function name}`: `u2_contracts` keeps the table as it finds it and puts it back, and asserts nothing about which hotspots are in it besides the vending machine's absence |
| `hot_dim_reason(h)`, `hot_planned(place=None)`, `hot_name(h)`, `hot_faces(h)` | | a str; `{id: row}`; a str; a list of person keys |
| `hot_validate()` | | accepts a sidecar point for an id planned for that place; refuses one that is neither registered nor planned; reads the shape rules of B15 |
| `hot_shapes_for(loc)`, `hot_tip_rect(key)`, `HOT_SHAPE` | | D60: B15 |

**Names.** `persistent.show_names` (default False; its Preferences row is
U6's). The key held to show names is **N** (`ICON_NAMES_KEY = "K_n"`), in no
`config.keymap` list; `hot_layer` listens for it, so it is live on the place
view. `icon_names_shown()` → bool is the one reader, and
`icon_words_shown(name, words=None)` follows it. While names are shown an exit
wears where it leads (`path_words`, locked or not) and a hotspot its name, on a
plate under its tile; an exit's tile draws the faces `hot_faces` returns.

**Hover-label sides** (`icon_tip_side(tip)`, `ui_icons.rpy`): the `tips` of
`hot_<here>.json`; then `ICON_TIP_SIDES`; and a hotspot or exit with no row of
its own there is placed from where its tile is (above an exit, left of anything
else, the opposite side when the label would leave the screen).

### B10. The stubs (9.3). Each is behaviour-neutral until its package fills it

| symbol | file | the stub returns | filled by |
|---|---|---|---|
| `bath_ok()` | `room_bath.rpy` | `False` | U5 |
| `pool_ok()` | `room_pool.rpy` | `False` | U5 |
| labels `sb_do_bath_soak`, `sb_do_bath_sauna`, `sb_do_pool_swim`, `act_swim_pool(who)` | the two files above | `return` | U5 |
| `tky_here(key)` | `room_tokyo.rpy` | `[]` (a list of person keys) | U5 |
| `tky_caption(who, key)` | | `""` (a str) | U5 |
| `TKY_LINES`, `TKY_BOND` | | `{}`, `4` | U5 |
| labels `district_harajuku`, `district_shibuya`, `tky_people(key)` | | `return` | U5 |
| `screen tky_meet(key)` | | `("back",)` at once; when filled: `("talk", who)`, `("with", who)` or `("back",)` | U5 |
| `cards_invitable()` | `room_cards.rpy` (appended) | `[]` | U5 |
| `screen cards_invite_pick()` | | `("close",)` at once; when filled: `("ask", who)` or `("close",)` | U5 |
| `screen hud_day_card(n=None, weekday=None)` | `ui_hud.rpy` (appended) | empty | U4 |
| `hint_show(id)` | `ui_hints.rpy` | None, always (it is on `tools/none_ok.txt`) | U4 |
| `HINT_IDS` | | `("place", "names", "map", "person", "hour", "night")`, frozen | |
| `hint_seen` | | `default hint_seen = set()`: the one new saved variable. Changed only by a function that then calls `renpy.retain_after_load()` | U4 |
| `screen hint_layer()` | | empty | U4 |
| `map_district_people(key)` | `ui_map.rpy` | `[]` (three at most) | U2 |
| `view_asleep(loc)` | `view_stage.rpy` | `[]`; when filled: a list of `(who, patch)`, `patch` a pose dict `dict(image, box)`. `screen view_stage` lays each on the room before the people, and a patch is no button (`u2_contracts` asserts both with a test function in its place) | U3 |
| `screen view_others(loc, who)` | `view_stage.rpy` | empty | U3 |
| `night_club_bg(key)` | `sb_night.rpy` (final) | an image name: `"bg club"` when that image exists, else `night_bg(key)` | U9 adds the one line that calls it |

**What marks the stubs.** `TKY_LINES` is `{}` only until U5 fills it, and U5
fills it together with `tky_meet` and `cards_invite_pick`. `u2_contracts`
calls those two screens (to see each answer at once) only while `TKY_LINES` is
empty and neither `bath_ok()` nor `pool_ok()` is true; once they are filled it
notes "the stub-only check is skipped" and calls neither, because a filled
screen waits for its own input. U5 therefore fills `TKY_LINES` in the same
commit as either screen.

**`label tky_people` returns at once while `smoke_autoplay` is true** (plan
7.6). `u2_contracts` rides to Harajuku at Sunday Noon under `autoplay()`, the
one hour a filled `tky_here` finds Nobara and Maki there; a `tky_meet` that
opened on that ride would hold every package's standard set until its
watchdog.

**What else `u2_contracts` does so that it goes on passing** (it is not edited
after wave 0, so it depends on nothing the wave is planned to add):

- the Courtyard is its test place. Wherever it stands there it lays a test
  sidecar of today's five points (the four exits and `spot_vend`) and nothing
  else, so the real `hot_courtyard.json` may come to hold moved points, `tips`,
  `shapes` and a `for_rev`; and where it counts the Courtyard's hotspots
  (section B's spacing test, section E's sleeper, all of section I) it takes
  every other row registered there out of `HOT_SPOTS` for the test and puts it
  back. **So `gateway` and `straw_posts`, or anything else U4 registers in the
  Courtyard, change nothing in it.** The ids `go_courtyard__<to>` and
  `spot_vend` must stay registered there;
- section A's four gates are read on test rows laid over an empty manifest,
  whatever rows `pictures.json` holds by then, and with `light_classroom.json`
  taken as absent;
- **a tree with a manifest of its own** is read with its own rows in both
  states. `tools/smoke.sh` copies an overlay file over the tree's, it does not
  merge, so the overlay's `zz_u2c_gen.rpy` reads the tree's
  `game/layout/pictures.json` from the repository and lays its rows under the
  overlay's three test rows (a test row wins where both name a picture): a
  real sidecar that carries `for_rev` is as fresh in the default run as in the
  bare one. Where the harness needs the Courtyard or the Library at a revision
  of its own it lays its test files over the real `hot_courtyard.json` and
  `view_courtyard.json`, counts as section A's one mismatch only files of the
  Courtyard, and leaves the Library's row alone once it is at revision 2 or
  later, so either place may be composed again;
- the stub-only checks stand aside, each with a NOTE, once the stub is filled:
  an empty `TKY_LINES` (the two screens), `bath_ok()` or `pool_ok()` (the
  baths, the pool, the seven labels), a store function `light_follow` (B7);
- `view_asleep`, `path_faces`, `path_locked`, `view_person_rects`,
  `view_stage_rows` and `view_fg_path` are replaced by test functions for one
  check each and put back: each must stay a plain store function that is looked
  up by name when it is called.

It was run, as it is at this merge, over a wave-1 stand-in (the 59 planned
ids registered, the baths, the pool and Tokyo filled, the card table's dim
function named, `light_follow` in, `path_faces` and `map_district_people`
filled) and over a batch-0 stand-in laid in the tree's REAL `game/layout`, as
batch 0 will lay it (its own `pictures.json` with the Courtyard and the
Library composed at revision 2, their light rows and the Common Room's day
picture at 2; `hot_courtyard.json` and `hot_library.json` with moved points,
`tips`, a shape for every exit, hotspot and planned id and `for_rev` 2; their
`view_` files with `for_rev` 2; their light files), and over the two
together: RESULT PASS in each, **in both states** (the default run and
`SMOKE_ASSETS=/var/empty`). The batch-0 stand-in with the Courtyard, or the
Library, composed a second time (revision 3, `for_rev` 3) passes bare as
well. (Before review round 3 the batch-0 run was one generated overlay folder
whose manifest already held the test rows, in the default state only; a real
batch-0 tree failed in both states.)

**Defaults that stay.** `hud_day_card`'s `n` and `weekday`, `hot_layer`'s
`front` and `sb_map`'s `layer` and `area` keep a default (`u2_contracts`
asserts it): `hud_day_card` must be showable with no argument, so that a save
that holds it loads.

Hook lines placed in screens other packages own: `use hint_layer` in
`sb_place` and in `sb_map`; `use view_others(here, who)` in `sb_char`.

Two tests in `activity_state` (`sb_activities.rpy`), final: the kinds
`romance`, `confession` and `intimate` are hidden while I stand in
`bathhouse`, `sauna` or `pool` (K16; `ACT_NO_ROMANCE`), and `invite` is hidden
with a friend in their `WORLD_AWAY` hour or the hour before it (7.6).
`NIGHT_REST_BLOCKS` holds `pool_swim` and `swim_pool`; `NIGHT_CARRY_LINES` has
rows for `nobara_room` and `maki_room`.

Screens that keep name and parameters: `main_menu`, `choice`, `say`,
`file_slots`, `preferences`, `quick_menu`, `journal`, `sb_map`, `sb_place`,
`sb_char`, `hot_layer`, `hover_label`.

### B11. Pictures and names

- **The menus.** `gui.main_menu_background = bg_placeholder("gui/title.png",
  "images/bg/gate.png")`; `gui.game_menu_background =
  bg_placeholder("gui/menu_ground.png", "images/bg/veil.png")`. The two files
  are copies of today's `gate.png` and `veil.png`.
- **The five lenders' copies:** `images/bg/standin/standin_<name>.png` for
  `city_night`, `street_morning`, `town_street`, `ruin_hall`, `veil`
  (`STANDIN_COPIES`, `standin_copy(name)`). Every stand-in is made from a
  copy. (The plan wrote `standin/<name>.png`; a second file with the same
  base name under `images/` would give Ren'Py one image name twice, which
  `check_content.py --art-names` refuses.)
- **Ten names that always exist** (`STANDIN_NAMES`), each `bg <key>` with
  `images/bg/<key>.png` when painted, else its lender's copy as it is:
  `mall_front` (city_night), `mall_hall` (ruin_hall), `mall_atrium` (veil),
  `warehouse` (city_night), `annexe` (ruin_hall), `site_tunnel` (ruin_hall),
  `site_ward` (ruin_hall), `site_platform` (city_night), `site_pool` (veil),
  `site_karaoke` (city_night).
- **Three that exist only when their file is loadable** (`STANDIN_IF_FILE`):
  `bg club` (`club.png`), `bg shibuya night` (`shibuya_night.png`),
  `bg shinjuku night` (`shinjuku_night.png`).
- **The market** is a file name, `images/bg/market.png`, not an image name.
- **The board:** `BOARD_PLACES[*]["bg"]` is one of the five `bg site_*` names
  (tunnel: Nerima, Edogawa; ward: Adachi, Kita; platform: Ikebukuro,
  Shinagawa; pool: Setagaya; karaoke: Koenji).
- **The stand-in people** (`jjk_defs.rpy`): `mother`, `father`, `oda`,
  `kurose`, `nade` are defined by one guarded block, `init 501 python`, each
  only when `not renpy.has_image(key, exact=True)`. (An `image` statement runs
  at init 500, so the plan's "init 1" would run before the generated lines.)
  `STANDIN_DEFINED` is the keys it defined.
- **The 26 icon names**, in the order of `tools/icons/sheet_4.txt` (6 x 5
  cells, left to right, top row first): `place_boys_dorm`, `place_yuji_room`,
  `place_megumi_room`, `place_senpai_room`, `place_nobara_room`,
  `place_maki_room`, `place_teachers_lounge`, `place_teachers_dorm`,
  `place_bathhouse`, `place_sauna`, `place_pool`, `place_school_yard`,
  `place_dorm_yard`, `place_staff_yard`, `place_training_yard`,
  `place_trailhead`, `bath_soak`, `bath_sauna`, `pool_swim`, `cards_invite`,
  `history`, `auto`, `save`, `help`, `continue`, `at_home`. 114 icons in all.
  `ICON_FOR[("do", "swim_pool")] = "swim"`; the four action rows
  (`("act", "bath_soak")` and the rest) are set by the stubs.

### B12. The frozen texts and the record (U0d1)

`tools/bgs/look.txt`, `keep.txt`, `keep_light.txt` (frozen after batch 3);
`stage.txt` (after batch 1); `map.txt` (after batch 21a); `keep_outdoor.txt`
(after batch 8); the pose prompt's two frozen sentences (a person's clothes as
their sprite's; the asleep shape, K16).

**The shape of `tools/bgs/campus.json`** (`tools/bgs/CAMPUS2.md` has it key by
key): `format` (1), `about`, `sheet`, `rules`, `areas`, `campus_map`,
`pictures` (`{stem: {place, rev, kind, batch, chosen, render, source,
source_2k}}`), `fixed` and `proposed` (lists of rows, each with a unique `id`
and a `kind`: `building`, `place`, `path`, `exit`, `seen`, `window`, `line`,
`interior`; a fixed row also has `by: {picture, rev}`), `waived`, `waits`. Its
rows are never frozen as a whole (O20).

### B13. The tools' command lines (as each tool's own header gives them)

```
python3 tools/make_redo_workflow.py <place> [--add] [--from-rev1] [--print] [--again <n>]
python3 tools/make_redo_workflow.py --relight <place> evening|night|lit
python3 tools/make_scene_workflow.py <place | area_<key> | map_campus> [--print] [--again <n>] | --list
tools/py_art.sh tools/install_redo.py <place> <render a> <render b> [--dry | --choose a|b]
tools/py_art.sh tools/install_redo.py --relight <place> evening|night|lit <a> <b> [--dry | --choose a|b]
tools/py_art.sh tools/install_redo.py --compose <place> <render> [--dry] [--layout hot_<place>.json view_<place>.json]
        options: --root <dir> --layout-dump <file> --keep <folder> --record <campus.json> --batch <n> --date <yyyy-mm-dd>
tools/py_art.sh tools/sample_light.py <place> [evening|night|lit] [--bg <render>] [--write] | --check
python3 tools/check_campus.py [--layout-dump <file>] [--layout <files>] [--sidecars <folder>] [--selftest]
python3 tools/check_prompts.py <file> ... | --text "..." [--place <place>] | --selftest
python3 tools/art_status.py [--check]
python3 tools/art_batch.py --list | <batch> [--preview --out <folder>] [--again <n>] | --done <batch> | --selftest
python3 tools/campus_plan.py [--md | --pins | --ref | --check]
python3 tools/install_set.py <who> <staged folder> [--dry] [--root <dir>] | --stage <who> <render folder>
python3 tools/install_face.py --prepare <who> | <render> <who> blink|talk | --sheet
python3 tools/install_pose.py <render> [--box x,y,w,h] [--name pose_<place>__<who>] [--dry]
python3 tools/check_content.py --all game/*.rpy tools/smoke/*.rpy      (also: --layout-files [--layout-dir <dir>])
tools/smoke.sh u2_dump [--out shots/art/game_layout.json]
python3 tools/smoke/make_shape_overlay.py --out shots/shape_overlay/<name> [--with tools/smoke/assets/<harness>]
        options: --dump <file> --only a,b --rev <n> --for-rev <n> --size <px> | --selftest | --write-cases
```

`check_layout.py`, `stage_preview.py` and the new `layout_sheet.py` are U0d3's
and join this list with that package.

**U0n (B16), the hour `lit`.** `lit` is a third hour in every tool that lists
the hours, for the eight rooms of `WORLD_LIT` only (any other place is refused
in one line):

- `install_redo.py --relight <place> lit <a> <b>` proves the pair as any
  relight and, for the version chosen, writes `images/bg/<stem>_lit.png` with
  the manifest row `<stem>_lit` (`kind: "relight"`, `of: <stem>`, `of_rev`),
  the light row under `"lit"` of `light_<place>.json` (row `light_<place>_lit`)
  and, where the room has a foreground outline, `images/fg/fg_<place>_lit.png`
  (row `fg_<place>_lit`): the names B16 lists. The place is named by its key or
  its picture (`dorm` or `your_room`). The room's `night` is not touched.
- `make_redo_workflow.py --relight <place> lit`: the general indoor sentence
  with the room's lamps on is the `lit` one; the general indoor `night`
  sentence is the room with every light off; a yard has no `lit`, and neither
  has a room outside `WORLD_LIT` (refused in one line). Renders are
  saved as `ui2_<stem>_lit_a` and `_b`.
- `game_layout.py`: `HOURS` holds `"lit"`; `lit_places()`, `lit_file(place)`
  and `late()` read the dump's `lit_planned` and `late` (None for a dump
  written before U0n); `where(who, day, period)` answers the late table's room
  on a late Night (after the away table); `periods_showing(place, "lit")` is
  `{"Night"}` for a room of the table and empty for any other place.
- `install_pose.py` and `make_pose_workflow.py` take the variant `lit` as any
  other (`pose_<place>__<who>__lit`, painted on `<stem>_lit.png`).
- `stage_preview.py <place> lit` draws the Night frame on the lit picture.
- `art_batch.py`: a relight row's `hour` may be `lit`; a row with
  `"versions": 0` and `"made"` is a picture that exists and is never written
  into a workflow. The table holds 72 hour pictures and a batch 47.

### B14. Budgets and the ledger

A9 (K11) and `docs/UI2_PINS.md`. The motion budget is unchanged: no function
transform was added to the place view (a shaped hotspot has no ring, so a
shaped place has fewer).

### B15. The picture is what is clicked (D60; `sb_hotspots.rpy`, final)

Plan 7.3. Asserted by section I of `u2_contracts.rpy`. **No real sidecar holds
shapes yet, so no place is shaped and the game plays as it did**; the first two
are the Courtyard and the Library at batch 0 (U0d3 stages them, L traces the
rest).

**When a place is shaped.** Its `hot_<place>.json` holds `shapes`, the file is
not stale (`for_rev`, if it carries one, is its picture's revision), and its
picture is at revision 2 or later: `art_rev(art_stem(loc))`, the stem being
`your_room` for `dorm`. Anything else draws its buttons exactly as before.

| symbol | returns |
|---|---|
| `hot_shapes_for(loc)` | `{hotspot id: [polygon, ...]}`, a polygon a list of `[x, y]`; `{}` for a place that is not shaped. A fresh copy each call. An exit's id is `go_<from>__<to>` |
| `hot_tip_rect(key)` | `(x, y, w, h)`: the 72 px square at a shaped hotspot's point, for either of its tooltip keys, `hot_<id>` and `hotshape_<id>`; `None` for any other key, for a hotspot with no shape and for one that is not showing |
| `HOT_SHAPE` | one dict: the limits (`polys (1, 3)`, `points (3, 60)`, `area_min 5184`, `area_max 0.4`, `buried_max 0.5`, `grid 4`), the HUD's row (`top 92`) and the light's default look (`color "#fff0cc"`, `wash 0.30`, `edge 0.85`, `dim 0.4`, `names 0.5`, `blur 9`, `line 2`). `HOT_LOOK_KEYS` are the five `hot_look.json` may replace |
| `hot_look()` | the look in force, a dict of those five keys |
| `hot_keep_tile(loc)` | `{id: reason}` |
| `hot_name_rect(h)` | `(x, y, w, h)` of a shaped hotspot's name plate while names are shown; `h` is a `hot_spots_for` row. The side is `icon_tip_side`'s, which reads the `tips` of `hot_<here>.json`: it answers for a hotspot of **the place I stand in** (a tool that asks about another place sets `here` first, as `u2_dump` does) |
| `hot_tip_faces(key)` | the people whose faces the hover label draws beside a shaped exit's name (`hot_faces`); `[]` for any other key |
| `hot_place_points(place)` | `{id: (x, y)}`: the applied point of every hotspot and exit registered there, and the sidecar's point of a planned one |
| `icon_tip_key(key)` (`ui_icons.rpy`) | `hot_<id>` for `hotshape_<id>`, any other key unchanged: the side lookups (`icon_tip_side`) answer alike for both |

**What `hot_layer` draws for a shaped hotspot** (its two parameters and
`hot_spots_for`'s eleven keys are unchanged):

- no ring and no icon;
- **the square**: a button with the id `hot_<id>`, 72 px at the point, inside
  today's alpha wrapper (1.0, or `HOT_DIM_ALPHA` 0.45), with today's action and
  today's tooltip `(text, "hot_<id>")`. It is empty and its focus mask
  (`hot_no_point`) refuses every point: the keyboard and `renpy.set_focus` reach
  it, the pointer never does. `zz_rect("sb_place", "hot_<id>")` is the same
  rectangle as with buttons;
- **the shape**: a second button, id `hotshape_<id>`, the size of the shape's
  bounding box, with the same action and the tooltip `(text, "hotshape_<id>")`.
  Its focus mask is `renpy.partial(hot_shape_hit, shape, box, fg)`: inside one
  of the polygons, and for a back shape not where the room's foreground cut-out
  is opaque; and never above `HOT_SHAPE["top"]` (y 92), the HUD's row.
  `keyboard_focus False`. So a shaped place holds one more focusable widget for
  each shaped hotspot;
- **the light**, drawn only while it is lit: three layers of the class
  `hot_ShapeLight` (a dark rim, a wash added to the picture, the outline), each
  drawn from the polygons at that moment. Lit at strength 1.0 while the tooltip
  in force is the hotspot's under either key (`hot_lit_id`; never the button's
  own hover state), at `names` while names are shown, and both times `dim` for
  one that is locked, shut by the night or spent;
- **while names are shown**, its name on a plate at `hot_name_rect`: against
  the square, on the side its hover label opens (`tips`, else the table), left
  edges together above or below and top edges together beside it, flipped when
  it would leave the screen; a house's faces after the name;
- **order** within a layer: the larger shape first, so the smaller is on top
  (`hot_shape_order`: by area, then the id that sorts first), then every
  visible hotspot with no shape as its button (a `keep_tile` row, a harness's
  `zz` hotspot). A back shape is under the people, under a painted pose's box
  and under the foreground cut-out; a front one (`front=True`, or a
  standalone) is over all three.

`hover_label` opens against `hot_tip_rect(key)` when that answers, else beside
the focused button as before, and draws `hot_tip_faces(key)` after the name.

**A shape under a panel.** A button is kept inside `HOT_BOUNDS` and out of
`HOT_LANES`; a traced shape (a roofline, a path to the picture's edge) is only
asked to stay inside the picture, so it may lie under what the HUD draws over
the place view. What was chosen:

- **built here:** no shape takes the pointer in the HUD's row, above y 92
  (`HOT_SHAPE["top"]`; the lanes begin there and no hotspot's point can be that
  high). Resting the pointer on the date or between the chips lights nothing
  and a click there walks nowhere;
- **handed on, not built:** a toast, the objective banner (`HOT_LANES`), the
  arrival caption and "Nobody here right now." are drawn over the picture for a
  few seconds and are not buttons, so a shape under one still takes the pointer
  there. `check_layout.py` (U0d3) REPORTS, and does not refuse, the cells of a
  shape that lie above `top` (they are dead) and inside `HOT_LANES` (a toast or
  the banner may cover them); U4, which owns `ui_hud.rpy`, decides whether a
  toast and the banner take the pointer (a `button` with `NullAction()`, or a
  `focus_mask True` frame). Where nothing is drawn over the picture (between
  the tiles of the icon column) the picture is clicked, as it looks.

**The rules** (`hot_validate`, in lint; the same text for `check_layout.py`).
A sidecar that holds `shapes` or `keep_tile` is read whatever its picture's
revision. Each finding names its id and ends `(hot_<place>.json)`:

| rule | finding |
|---|---|
| one to three polygons | `a shape is 1 to 3 polygons` |
| 3 to 60 points, each `[x, y]` | `polygon N has K points`, `polygon N is not a list of [x, y] points` |
| inside the picture (0 to 1920, 0 to 1080) | `polygon N leaves the picture` |
| a polygon does not cross or touch itself, repeat a point or fold back | `polygon N crosses itself` |
| a shape's polygons do not overlap (they may share a side) | `two of its polygons overlap` |
| area (the shoelace sum) at least 5,184 px² | `smaller than a button` |
| at most two fifths of the picture, by cells | `it covers N% of the picture` |
| its hotspot's point inside it | `is outside its own shape`; `its hotspot has no point` for a planned id with no point under `spots` |
| and under no smaller shape | `is under the smaller shape '<id>'` |
| at most half of it under smaller shapes, by cells | `N% of it is under smaller shapes` |
| **the two layers** (`hot_shape_layers`): a back hotspot's point is under no FRONT shape, whatever the two sizes | `is under the front shape '<id>'` (a front shape that is also the smaller one is the row above) |
| and at most half of a back shape is under front shapes and smaller back ones together | `N% of it is under front shapes and smaller ones` (said only when the smaller ones alone do not bury it) |
| its id is registered in the place or planned for it | `no hotspot or exit of that id` |
| shaped all at once: every exit and hotspot registered or planned there has a shape or a `keep_tile` reason; ids that begin `zz` are left out | `<place> is shaped, and '<id>' has no shape and is not under keep_tile` |
| `keep_tile`: a known id, a reason in words, no shape as well, and not without `shapes` | four sentences that begin `keep_tile` |

"Smaller" is by `hot_shape_order`. Two hotspots whose points are equal (the
storehouse's `racks` and `armory`) carry the same polygons, and nothing is read
between the two. Cells are 4 px squares counted by their centres.

"Front" is the game's front layer: a hotspot registered `front=True` or
`standalone=True` (the `front` flag of its row in the dump's `hotspots`; an
exit is never in front). The
game stacks by layer first and by size only within a layer, so the first ten
rows, which read "on top" by area alone, are right for the shapes of one layer
and `hot_shape_layers` adds what the layers change. It errs one way only, and
on the safe side: a front shape whose point lies under a smaller BACK shape is
still refused by the row above ("is under the smaller shape"), though the
game plays that layout correctly: the front shape takes the click at its own
point, and the back shape may lie up to half under front shapes and still be
reached on the rest of itself. Lint refuses nothing the game plays wrongly.
**The rule for the layout sittings: keep a front hotspot's point out of every
smaller back shape** (move the point, or trace the back shape round it).

**Two things the layers' rule does not read, handed on in writing.**

- **To U0d3: a hotspot that keeps its button.** The game's lint reads the
  layers only for ids under `shapes`. A back hotspot or an exit under
  `keep_tile` whose point lies inside a front shape gives no finding
  (`hot_validate() == []`): its button is still drawn, and the front shape
  takes the click at its point. `check_layout.py` refuses it: a `keep_tile`
  id that is not front whose point lies inside a front shape.
- **To the layout sittings and U4: a planned foreground object has no layer
  until it is registered.** `front` comes from `HOT_SPOTS` alone, and a
  `SPOT_PLANNED` row is (id, place, kind), so until U4 registers it lint reads
  every planned thing as back. The layout sittings trace a planned foreground
  object as front (`check_layout.py` takes those ids as front), and U4
  registers it `front=True`, so that the verdict on an installed sidecar does
  not change in wave 1 with no layout edit.

**The one text for both validators.** The functions between the lines
`## >>> hot_shape: ...` and `## <<< hot_shape: ...` of `game/sb_hotspots.rpy`
are plain Python that names nothing of Ren'Py and nothing else of the game
(`import builtins` is their one import): `hot_shape_num`, `hot_shape_poly`,
`hot_shape_area`, `hot_shape_box`, `hot_shape_inside`, `hot_shape_turn`,
`hot_shape_between`, `hot_shape_meet`, `hot_shape_crossed`, `hot_shape_cells`,
`hot_shape_order`, `hot_shape_count`, `hot_shape_findings(place, shapes,
keep, points, known, need, limits, size)`, which returns the first sentences
above, and `hot_shape_layers(place, shapes, points, front, limits, size)`,
which returns the two of the layers. Lint is the two lists, one after the
other (`hot_shape_validate`), and `check_layout.py` calls both the same way,
`front` being the ids whose dump row says `front`.
`tools/check_layout.py` (U0d3) carries that text with the block's four leading
spaces removed, or reads it from the file as
`tools/smoke/make_shape_overlay.py` does (`shape_block()`,
`shape_functions()`). **The three test shapes** are in
`tools/smoke/hot_shape_cases.json` with their answers (`expect`: area, cells,
twice, buried, point, under; `order`; `findings`; and `layers`: with the ids of
`layers.front` in the front layer, `hot_shape_layers` answers
`layers.findings`): `python3 tools/smoke/make_shape_overlay.py --selftest`
asserts all of them in plain Python, and `u2_contracts` asserts the first
three in the game and the layers' two rules on the Courtyard.

**The overlay that shapes every place** is generated, never committed:

```
tools/smoke.sh u2_dump --out shots/art/game_layout.json
python3 tools/smoke/make_shape_overlay.py --out shots/shape_overlay/all
SMOKE_ASSETS=shots/shape_overlay/all tools/smoke.sh p2_hud
python3 tools/smoke/make_shape_overlay.py --with tools/smoke/assets/p2_view --out shots/shape_overlay/p2_view
SMOKE_ASSETS=shots/shape_overlay/p2_view tools/smoke.sh p2_view
```

An 80 px square round each applied point, the planned ids under `keep_tile`,
every picture at revision 2 and a manifest row for everything made from one,
so that nothing but the shapes differs. `--rev 1` and `--for-rev 3` build the
two states in which nothing is shaped.

**A save on a shaped place view.** Section I of `u2_contracts` makes a save
on the place view of the shaped Courtyard and loads it in the same run: it
comes back at the same depth, day, hour and place with the place view up, the
shapes answer at their points, and neither `load_recover` nor `return_recover`
runs. The state the night shuts is asserted there on the Library's `stacks`
(shaped by a square round each of the Library's points, at Night).

**The real pointer.** `u2_contracts` rests the pointer on a shape with
`renpy.set_mouse_pos`. The window takes it only when it is the frontmost
window; otherwise the harness focuses the widget the engine itself picks at
that point and says so in its NOTE "the pointer on a shape". Every run since
the second sitting's bare one took the second path, so the real pointer over a
shape is the first thing the owner tries on the Courtyard at batch 0.

**Not built** (plan 7.3, asked at checkpoint B): a shimmer on walking in; a
thing staying clickable while someone stands on its point; a cut-out picture
for each light; shapes on the maps.

### B16. Rooms lit at Night (D61, plan 5.7a; `sb_world.rpy`, `art_manifest.rpy`; U0n, final)

At Night a room that is shown both ways has two pictures: `bg <place> night`,
the room with nobody up in it, and `bg <place> lit`, the room with its lamps
on. No lit picture is installed by U0n; until one is, the game shows what it
showed.

| symbol | example | returns |
|---|---|---|
| `WORLD_LIT` | `(("library", "images/bg/library_lit.png"), ...)` | the eight rooms: the Library, the five friends' rooms, My Room (`your_room_lit.png`), the dojo. A table of its own: `WORLD_VARIANTS` keeps its 56 rows |
| `WORLD_LIT_ON` | `{"library": "images/bg/library_lit.png"}` | the rows that registered at init (`world_lit_register()`, as `world_variants_register` registers). Init data, never saved |
| `world_lit_ready(loc)` | | bool: registered, loadable, fresh, and with its own fresh cut in a room with a foreground (K7) |
| `world_night_up(loc, per=None)` | `world_night_up("library")` | bool. False unless the hour asked (`per`, else the hour it is) is Night, and False while the store holds no hour (init: the memory tiles). In a replay: whether the memory being replayed (`_mem_label`, `_mem_args`) names a person; False when it is not found. Otherwise: whether anyone on the roster has `char_location(who, "Night") == loc` and is not asleep. It never reads `who_is_here`: I do not count, and whoever walks with me counts only in the room their own table has them in |
| `bg_variant(loc, per)` (unchanged signature) | `bg_variant("library", "Night")` | `"lit"` at Night when `loc in WORLD_LIT_ON and world_lit_ready(loc) and world_night_up(loc, per)`; otherwise what it answered before (the hour's attribute, or None) |
| `world_lit_bg(place)` | `scene expression world_lit_bg("dorm")` | for a written scene that needs the room lit: the image name `"bg <picture> lit"` when `world_lit_ready(place)`, else `graded_bg(place, "Night")`. It does not ask who is there. U0n re-points no scene line; U9 points My Room's five at it (plan 5.7a) |
| `graded_bg(loc=None, per=None)` | | as before. Its cache key is `(place, hour, "lit" or None)`, so a room's two Night pictures are two rows; **`_light_key` stays `(place, hour)`**, on a tinted picture only (a painted one is lit by its own name) |
| `WORLD_LATE` | `{"megumi": ("library", ("Sun",)), "toge": ("library", ("Wed",))}` | who is out late, where, on which Nights (the owner's yes of 11 Oct, O47). Read in `char_location`'s routine branch after `WORLD_AWAY`: a story pin and a flag schedule still win. `routine_location`, `usual_places` and `when_at` do not read it |
| `world_late_cell(who, per=None)` | `world_late_cell("megumi")` | the room, on a Night the row names; None at any other hour or day |
| `WORLD_SHUT_NIGHT` | `("office", "utahime_office", "gojo_office", "pool")` | the places `place_access` shuts at Night (tag `"Night"`); a harness line holds the two equal |
| `world_lit_validate(lit=None, shut=None, on=None)`, `world_late_validate(late=None, lit=None, shut=None)` | | lint findings (both run from `_validate_world`); each takes a table to test in place of the game's |

Someone out late is where `char_location` says: counted there by
`who_is_here`, on the stage, awake (`world_asleep` is true only at home), and
`"out"` for `world_home_state`. Their own room opens as on any other Night.
With them: Talk and "Ask them along", by the night rule as it stands.

Lint refuses a `WORLD_LATE` row whose person has no routine in `SCHEDULE` (or
is Gojo) or is on that Night's `WORLD_ASLEEP` list, and whose place is
outdoors, is somebody's home, has a Bond door (`WORLD_DOOR_OWNERS`), is in
`WORLD_SHUT_NIGHT`, or has no `WORLD_LIT` row; and a `WORLD_LIT` row that is
not `(place, images/bg/<stem>_lit.png)`, is outdoors, shut at Night, or listed
twice.

The names an art sitting writes for a lit room: the picture
`images/bg/<stem>_lit.png` with the manifest row `<stem>_lit`
`{rev, kind: "relight", of: <stem>, of_rev}`; the cut
`images/fg/fg_<place>_lit.png` (row `fg_<place>_lit`, `of: <stem>_lit`); a
pose `images/place/pose_<place>__<who>__lit.png` with its box under
`<who>__lit` in `pose_<place>.json`; the light row under `"lit"` in
`light_<place>.json` (row `light_<place>_lit`).
