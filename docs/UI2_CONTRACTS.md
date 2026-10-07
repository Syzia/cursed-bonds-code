# The second UI overhaul: contracts

**First draft, by U0a (wave 0, the safety net).** U0c2 makes it final and writes
`tools/smoke/u2_contracts.rpy`, which asserts all of it. The plan is
`docs/UI2_DESIGN.md`; its section 9 says what is frozen and in what order of
cost. This file is where the exact shapes live.

- Part A is frozen **now**: U0a built it, the tools enforce it, and the six
  parallel packages of wave 1 rely on it.
- Part B is the list U0c2 fills in (symbols, stubs, hooks). It is copied from the
  plan so that nothing is forgotten; the plan's wording wins until U0c2 has
  replaced each row with its example call and return shape.

---

## Part A. Frozen by U0a

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
| `baseline_sprite_tree.txt` | what `lit_sprite` builds for Yuji, with and without the blink and talk pictures, and the sha256 of its pickle (K9) | U3's `u2_blend` |
| `baseline_shots/ui2/` | `place.png`, `person.png`, `map_campus.png`, `map_area.png`, `main_menu.png`, and `shots.json` (the pictures' size, the fixture, each file's sha256) | U0c2 ("pixel-identical to U0a's") |

A statement's name is `json.dumps(node.name)`: a label's name, or
`["game/<file>.rpy", <version>, <serial>]`. Its hash is the first 16 hex digits
of `sha1(repr((class name,) + diff_info()[1:]))`. Two nodes with one name and
one hash are the same statement to a save.

The pictures were taken at 2666 x 1499 (this Mac's window). They compare byte
for byte on this Mac; on a screen of another size `u2_baseline` says so in a
note and the pictures are looked at instead.

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
New keys may be added by U0c (the door, asleep and away tables are not in it
yet); none of the keys above changes shape.

### A4. Sidecars (`game/layout/`), as `check_content.py --layout-files` enforces them

Every file is one JSON object; every key is optional unless it says otherwise;
lists, not tuples. An unknown file name or an unknown key is a finding.

| file | keys |
|---|---|
| `hot_<place>.json` | `spots {id: [x, y]}` (a hotspot's id, or an exit's `go_<from>__<to>`); `tips {id: "top" / "bottom" / "left" / "right"}`; `spare [[x, y], ...]` (the houses with spare doors only: `boys_dorm`, `girls_dorm`, `teachers_dorm`, `teachers_lounge`); `for_rev` |
| `view_<place>.json` | `slots {"1".."4": [[x centre, y offset, zoom(, far)], ...]}` (key `n` holds `n` rows); `poses {key: [x, y, w, h]}`; `floor` (a list of polygons, or `{"on": [polygons], "off": [polygons]}`; a polygon is three or more `[x, y]`); `scale [x, y top, y bottom]`; `slot_light {hour: ...}`; `cast {hour: [direction, length, darkness]}`; `talk` (true or false); `for_rev` |
| `pose_<place>.json` | `poses {key: [x, y, w, h]}` (required) |
| `light_<place>.json` | `""`, `"evening"`, `"night"`: each a row `["#rrggbb", brightness, saturation, shadow opacity]`, or the same with `[shadow lean, shadow stretch]` after it |
| `light.json` | `{image name: row}` |
| `area_<key>.json` | `spots {place: [x, y]}`; `for_rev` |
| `map_campus.json` | `anchors {area key: [x, y]}`; `mountain_box [x0, y0, x1, y1]` |
| `faces.json` | `blink_also {who: [faces]}` |
| `pictures.json` | `pictures {file stem: {rev, kind ("composed" / "inplace" / "relight"), batch, render, record, rev1_commit, from_commit, shift [dx, dy], sharp [a, b], of, of_rev, waiver}}`; a row holds `rev`, or `of` with `of_rev` |

An hour is `""` (the day picture), `"evening"` or `"night"`; a period name is
accepted as well. `for_rev` is a whole number from 1; in a `hot_` or `view_`
file it is a finding unless `pictures.json` calls that place's picture
`composed` (a room redone in place carries none, plan 3.2).

**For U0c2 to settle and then tighten here and in the rule:** the exact inner
shape of `floor` (both forms are accepted today), of `slot_light`, and which
of the two teachers' keys carries `spare`.

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
  `room_pool.rpy`, `room_tokyo.rpy`, and in any `AMBIENT`, `SPOT_LINES` or
  `POSES` row whose place is `bathhouse`, `sauna`, `pool`, `yuji_room`,
  `megumi_room`, `senpai_room`, `nobara_room` or `maki_room`.
- `--baths-optional`: `"bath"`, `bath_soak`, `bath_sauna`, `bath_ok`,
  `pool_swim` anywhere under `game/` outside `room_bath.rpy` and
  `room_pool.rpy`, except in `ICONS` / `ICON_FOR` (`ui_icons.rpy`),
  `SPOT_PLANNED` (`sb_hotspots.rpy`), a `register_hotspot(...)` call, and
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
  REFUSED) while a Ren'Py game that is not a smoke run is open. Every other
  harness waits while the lock is held. **A new harness that hovers or calls
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

## Part B. For U0c2 to make final (from the plan's section 9)

1. **Home** (K1): the key `dorm`, `bg your_room`, `default here = "dorm"`,
   `sb_do_path_dorm`.
2. **The eleven place keys** and their image and file names: `boys_dorm`,
   `yuji_room`, `megumi_room`, `senpai_room`, `nobara_room`, `maki_room`,
   `teachers_lounge`, `teachers_dorm`, `bathhouse`, `sauna`, `pool`.
3. **Action ids and labels**: `path_<key>` for the eleven, `bath_soak`,
   `bath_sauna`, `pool_swim`, `cards_invite`; the activity `swim_pool` and
   `act_swim_pool`; the ids of `SPOT_PLANNED`; `district_harajuku`,
   `district_shibuya`, `tky_people`; the screen `tky_meet` and its three
   return tuples.
4. **The saved sprite** (K9): A2's `baseline_sprite_tree.txt`.
5. **The light row**: four values, or six.
6. **Sidecar shapes**: A4 (tightened), the manifest's fields, the keep list's
   keys, and A3.
7. **The 26 icon names** and their cells on sheet 4; the new image names of
   the plan's 5.8.
8. **The frozen texts** under `tools/bgs/` and the shape of `campus.json`.
9. **`hint_seen`**, the six hint ids, `persistent.show_names`, the key held to
   show names.
10. **The budgets** (A9) and **the ledger** (A8).
11. **The door, asleep and away tables** and the three hooks;
    `--baths-optional` (A6).
12. **The tools' command lines.**

The symbols of the plan's 9.2 and the hooks of 9.3 are asserted by
`u2_contracts.rpy`, each with an example call and its return shape and each
function's owning file; every one exists, at least as a stub, when wave 0
ends.
