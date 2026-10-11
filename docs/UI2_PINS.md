# The second UI overhaul: the ledger of harness lines

Written by U0a (wave 0), before the overhaul changed a game file
(`docs/UI2_DESIGN.md` K3, K13, 10.3; D43, D44).

**How to use it.** A harness line in Part 2 or Part 3 that fails *for the
reason written beside it* is a hand-off, not a failure: log it with the exact
edit, prove the edit in a scratch copy, and pass it to the package named under
"whose". Anything that fails and is **not** here is a real finding. Line
numbers are today's (commit of this file); U0a's own edits moved the numbers
in `p2_paths`, `p2_map`, `p2_rooms`, `p2_view` and `p2_contracts` a little from
the plan's, so find a line by the words of its check.

---

## Part 1. Lines U0a turned into rules (K3), once

Each gives the verdict it gave before on the untouched tree (`p2_contracts` 129,
`p2_map` 97, `p2_view` 130, `p2_rooms` 126, `p2_paths` 110, `p2_hud` 129: all
passing, the same counts before and after), and each
rule was made to fail on purpose, as the last column says.

| harness | was | is now | made to fail by |
|---|---|---|---|
| `p2_paths` "no exit is within PATH_CLEAR ..." and "what each place keeps clear ..." | a hand copy of `PATH_KEEP_CLEAR` (eleven places' points) compared with the table | the points an exit keeps clear are the room's live hotspot points (`path_keep_clear(loc)` once U0c2 defines it; `zz_keep_clear` in the harness until then). The code's table is only noted | a sidecar putting the Courtyard's Training Yard exit 70 px from the vending machine: FAIL, naming the exit |
| `p2_paths` "the courtyard's exits are clear of the vending machine and inside the frame ..." | the exit equals (1640, 850); my door's y is 120 below the laptop's | every Courtyard exit is `PATH_CLEAR` from the machine's applied point and inside `HOT_BOUNDS`; my door is `PATH_CLEAR` from the laptop | the same sidecar: FAIL |
| `p2_paths` the garden's exits (three lines: the save in a yard, the Night, the worst case) | exactly 7 | every exit of `path_exits("dorm_yard")` is offered, and there are at most 7 | a count read from the table cannot be broken by a sidecar; the "offered in the room or the column, never neither" sweep beside it still catches a lost exit |
| `p2_paths` "every place has at least one exit" | 24 places | `len(LOC_ORDER)`, equal to `len(LOCATIONS)`, no key twice | (a count) |
| `p2_paths` "in the six hubs every exit's hover label ..." | 30 labels | the sum of the six yards' exits | (a count) |
| `p2_paths` "the Mountain marker's centre lies on the mountain" | the box equals (1160, 119, 1420, 285) | the box is `map_campus.json`'s `mountain_box` when the map has one, else the code's; it is a box on the picture and the marker's centre, which is the area's anchor, is inside it | a `map_campus.json` whose box is elsewhere: FAIL |
| `p2_map` "pressing an open pin returns ('go', loc)" | every one of the 24 places | every **pinned** place (`world_pinned`, once U0c defines it; every place until then), and the number of places is `LOC_ORDER`'s | (a count; the overlap and frame rules beside it are unchanged) |
| `p2_map` the two budgets of level 2 | 16 words, 10 buttons | 18 words, 11 buttons (K11, raised once, here) | – |
| `p2_map` "five areas as shipped: no hovered pin's label meets another pin" | `2 * (len(LOCATIONS) - 5)` hovers | twice the pinned places outside the School Building (which this harness lays its own sidecar over) | a sidecar standing my room's pin on the garden's: FAIL here (a label meets another pin) and on "no pin overlaps another pin" |
| `p2_view` "a sidecar row of the wrong length or shape is ignored"; "other rooms keep their rows"; "with the file back the room's own slots return"; "a layout with a clear set is used as it is" | compared with `VIEW_SLOTS[...]` by name | compared with what `view_slots` itself reads (`zzv_plain_slots`, or the value read before the test took the file away) | these compare the function with itself across a change of state; the rule on a sidecar's numbers is `view_validate`'s and `check_layout.py`'s (U0d3), not this line's |
| `p2_view` "the pose plan ..." | 14 rows; the hour's picture through `bg_variant` | every row; the hour's picture from `TIME_VARIANT` (U0c2 gates `bg_variant`: it is None for a stale hour picture) | (U0c2 proves the stale half: 10.2) |
| `p2_view` "every polygon in tools/fg/ has its foreground file" | a list of five file names | every polygon's cut loads, for every fresh picture of its room (`art_fresh`, once U0c2 defines it) | (the file list is outside `game/`; U0c2's stale test covers it) |
| `p2_view` fixture | – | its overlay gains `layout/pictures.json` (`{"pictures": {}}`) and `layout/pose_dorm_common.json` (its two test boxes), so its test poses and cuts cannot go stale when the real Common Room is revised. Today's game reads neither file | – |
| `p2_contracts` "ICONS holds exactly the names the icon sheets hold" | 88 | the names in `tools/icons/sheet_<n>.txt`, each once, equal to `ICONS` | a sheet with one name taken out: FAIL, naming it |
| `p2_rooms` "the first set of 4.10 is registered" | the registry equals the fifteen | the fifteen are present with their place, kind and action; more are allowed | (a table; U4 adds to it) |
| `p2_rooms` "SPOT_LINES holds the look hotspots' lines" | `len(SPOT_LINES) == 3` | every row of `SPOT_LINES` is a registered look and holds its lines; at least three | (a count) |
| `p2_rooms` "every point in game/layout/hot_<place>.json ..." | every sidecar point equals the code's default, and there are 15 | every id a sidecar names is registered for its place, or planned for it (`SPOT_PLANNED`), and its point passes `hot_point_findings`; no count, no equality with the code | a sidecar naming an unknown id, putting the cafeteria's counter in the toast lane, and standing the machine where people stand: FAIL, naming all three |
| `p2_hud` section 3b, the eight named tiles ("the label of 'Practice' hides nothing where it opens") | the label opens on a named side, and opened on the other it "used to" cover a named exit | the label hides no exit, hotspot or corner button where it opens, and reads its title; the side and what it would have covered are a note | not breakable by a sidecar: with an exit put where a label opens the game moves the label clear, and the rule passes (129 of 129). It fails only if the placing of a tile's label regresses. (The first moved-points overlay failed the OLD line, which also pinned the side.) |
| `p2_rooms` "the machine's point is clear of where one to four people stand" | the code row of `HOT_SPOTS` | the machine's applied point (the sidecar's) | the same sidecar: FAIL |

**The moved-points test** (the acceptance of U0a): with an overlay that moves
every exit, the hotspot, every slot of the Courtyard and every pin of the
Dormitories' map at least 50 px to other legal points, `p2_paths`, `p2_rooms`,
`p2_view`, `p2_hud`, `p2_map`, `p2_contracts` and `wp1_world` pass. The first
overlay tried was not legal, and two rules that are still rules said so: the
gate's exit was hidden by the Courtyard's commonest pair (`p2_paths`, "with two
people the gate exit is in the picture ..."), and the Training Yard's exit sat
where the label of "Practice" opens (`p2_hud`, section 3b, as it then was: the
line also pinned the side the label opens on, and that is what failed). The
first is what a layout sitting must respect. The second overlay showed that
`p2_hud`'s eight named tiles still pinned a side and a covered exit of the old
pictures; that line became the rule in the table above, which an exit under a
label does not break, because the game moves the label clear of it.

**Every harness, before and after.** All 27 harness runs of `tools/README.md`
(the 26 files, `p2_oldsave` on slot 1-1 among them) pass on the untouched game
with the same number of checks before U0a's edits and after: 3,299 in all.

---

## Part 2. The plan's ledger (10.3), found line by line

| harness line (today) | pins | changed by | fixed by |
|---|---|---|---|
| `p2_paths.rpy:305-323` (the loop walk) and `:462-466` | "the exit in my room walks to the Dormitory Garden"; the button returns `('act', 'path_dorm_yard')`, its label reads "To the Dormitory Garden" | U0b | U0b |
| `p2_saves.rpy:452-457` | presses `hot_go_dorm__dorm_yard`, asserts `here == "dorm_yard"` | U0b | U0b |
| `p2_paths.rpy:468` | the garden's exit `hot_go_dorm_yard__dorm` reads "To My Room" | U0b (the exit is to the Boys' Dormitory) | U0b |
| `p2_paths.rpy:1040-1052` | at Night `char_location("panda") == "dorm_yard"`, and what can be started with him there | U0b | U0b (against `senpai_room`; "what can be started" on a weekend Night, when he is awake) |
| `p2_saves.rpy:467-476` | `area_dorms`, then `row_dorm` | nobody: my room keeps its pin. Listed so nobody "fixes" it | – |
| `wp1_world.rpy:246-248` | `places_in("dorms")`, `places_in("staff")` | U0b, U0c | U0b, U0c |
| `wp1_world.rpy:296-333` | who is in the garden at Night | U0b | U0b (nobody, on any of the seven Nights) |
| `wp1_world.rpy:329-334` | the Common Room is empty at Night | unchanged; listed so nobody breaks it | – |
| `wp1_world.rpy:335-338` | "only the cafeteria and the riverside hold five" | U0b (the weekend cafeteria drops to four), U0c1 (the pool) | each in its own commit; checked on a Saturday |
| `wp1_world.rpy:352-378` | the lock sentences | U0c, U1 | U0c, U1 |
| `wp1_world.rpy:22-75, 262-272` | the frozen copy of the schedule and the regression line that compares days 1 to 14 against it | U0b, U0c1 | each in its own commit: the copy's cells and its "on purpose" comment |
| `p2_paths.rpy:1033-1039` | the list of people who moved, and "nobody who moved lost an activity" | U0b, U0c; U4 (`swim_pool`) | U0b, U0c; in wave 1 U4 proves its edit in scratch and hands it to U2 |
| `game/sb_activities.rpy:205` (`TRAIN_TOGETHER`) and the choice order above it | name `swim` | U4 | U4 |
| `p2_paths.rpy:1056-1066` | the Courtyard on a weekday afternoon is Yuji and Nobara | unchanged | – |
| `p2_night.rpy` (its literals `"dorm"`) | every night ends in `dorm` | unchanged; rerun | – |
| `p2_map` hover and overlap sweeps; `p2_hud` section 3b; `p2_paths` sections 3 and 5 | pins, exits and labels on the pictures | every composed picture | rerun at each layout sitting; they check rules, so no line is edited |
| `p2_rooms.rpy:83-93` | the fifteen hotspots, room by room | U4 (the looks, the moved actions) | U4 (the check allows more since U0a; a moved action changes its row) |
| `wp4_board.rpy:309-313` | "the sweep met students off campus" | U0b (no student is off campus at Night any more) | U0b (a fixture pins one student off campus) |
| `p2_map.rpy:540-556` | at Night the girls' corridor is locked with people in it; Yuji and Panda are in the garden | U0b, U0c1 | U0b, U0c1 |
| `p2_map.rpy:792-800` | `person_now("nobara")` at Night; Megumi "Off campus" | U0b, U0c1; U1 (the name) | U0b, U0c1; then U1 proves the edit and hands it to U2 |
| `p2_paths.rpy:1126-1127` | `who_is_here("dorm_yard") == ["yuji", "panda"]` on a weekday Night | U0b | U0b (the garden is empty at Night) |
| `p2_night.rpy:1732`, `wp4_board.rpy:434` | a "later build" or "combat update" note is on its screen | U8 (the notes are hidden) | U8 |
| `wp0_stubs.rpy:341-353` | `place_actions("dorm")`, `("courtyard")` shapes | unchanged | – |
| `wp8_journal.rpy:516-519, 969-974, 1133-1136` and `p2_contracts.rpy:1520` | the Preferences rows' words (MOTION, On, Off) | U6 (a row added, none renamed) | U6 |
| `tools/make_icon_workflow.py`'s own check | the sheets equal `ICONS` | U0b | U0b |
| `wp0_stubs.rpy:574`, and the trips in `phase1_all` and `phase2_all` | `call sb_trip(...)` runs to the end without a click | unchanged; listed so nobody removes the autoplay line | – |
| `p2_map.rpy:603-618` | the Tokyo layer's ids | unchanged | – |
| `p2_journal.rpy:593-637`, `:1149`, `:1270` | patches `person_now` with the old "Somewhere I can't go right now" | unchanged (a patch of its own) | – |
| `p2_paths.rpy:604-623` | the girls' corridor's lock in the Evening with the flag discarded | unchanged while Bond is below the door's level; U0c1 confirms | U0c1 |

---

## Part 2b. Found after the scratch run, while wave 0 was built (7 Oct)

| harness line | pins | changed by | fixed by |
|---|---|---|---|
| `phase2_all`'s driver: on even days it goes by map to wherever a person stands and presses `row_<place>` | every place a person stands in has a map row | U0b's `WORLD_PINLESS` (a friend's room has no pin), first met when U0c1's cells shifted the thirty-day route | fixed in ae56832: the driver walks, or presses the house's pin (`zzq_pin`); 35 of 35 |
| `p2_map`, "a person in a locked room is on no marker and no pin" (`map_pin_people("girls_dorm") == []`) | a house's pin shows nobody from its rooms | U2, when a house's pin carries the people in its rooms (4.2) | U2 |
| `p2_paths.rpy:1087-1102`, "nobody who moved lost an activity" | everyone who moved can still be asked to walk somewhere | U0c1: Utahime's weekend Evening moved from the Courtyard to the Onsen (the plan's own cell), and the Courtyard was her only walk place, so by routine "Walk with them" is offered with her nowhere | **open: the owner's ruling.** Either accept it (the harness's NOTE stays) or give her one cell at a walk place |
| `p2_view.rpy:647-710` (section 5, the pose installer) | `install_pose.py` writes `view_<place>.json` and needs no flag for a test room | U0d2: the installer writes `pose_<place>.json`, reads the layout dump, and takes `--no-game` for a test room | fixed in b2cf9d3 (U0d2's third review round), the hand-off that should have gone in with U0d2's merge |
| `p2_paths.rpy:591-596` | a locked exit is drawn as the lock icon at alpha 0.45, an open one as its place's icon at 1.0 | D60: a shaped place draws no icon; there the lock is its `path_exits()` row's reason, its label and the square's alpha wrapper. It would first fail at batch 1, when the Training Yard is shaped | U0c2 turns the line into that rule, read from the icon only where the place draws buttons |
| `p2_view.rpy:798`, "and nobody stands up on the table ... (other rooms keep their rows)" | old wording: `view_slots("library", 3) == zzv_plain_slots("library", 3)`: the Library's row of three IS the plain row (a coordinate, once the Library has slots of its own) | batch 0: the Library's own `view_library.json` (U0d3's staged layout; its people stand further in). With that file live the line read 129 PASS, 1 FAIL | fixed in U0d3's review round 1. New wording: `_zz_lib3 = view_slots("library", 3)` is read before the foreground file is taken away, and the line asks `view_slots("library", 3) == _zz_lib3 and len(_zz_lib3) == 3`: a room with no foreground keeps the row it had. It fails if taking a foreground file away changes a room that has none (tried: with `VIEW_FG_ROOMS` given the Library in a scratch copy the line fails) |
| `p2_hud.rpy:611-624` | every hover label's key is unique on the place view | D60 would break it with one key on a hotspot's two focus areas; the shape's key is `hotshape_<id>`, so the line passes unedited | – (listed so that nobody gives the two one key) |
| `p2_contracts.rpy:1118, 1131, 1239, 1324`, `p2_paths.rpy:412`, `p2_rooms.rpy:477, 499`, `u2_home.rpy:1048` | `hot_validate() == []` while the harnesses' own hotspots are registered in real places | D60's "a place is shaped all at once" would report them in a shaped place; the rule leaves out ids that begin `zz`, and a hotspot with no shape is drawn as its button | – (they pass unedited; U0c2's overlay over all 35 places proves it) |
| any other harness line that looks at what a hotspot draws and not at its id, rectangle, action or label | a shaped place draws no ring and no icon (D60) | every shaped place, from batch 0 | found by U0c2's run of the standing set over the overlay that shapes all 35 places, and turned into its rule there |

**Turned by U0c2's first sitting (7 Oct):**

| harness line | was | is now | why |
|---|---|---|---|
| `p2_view`, "with no box and others on stage there is no pose" and the line after it | `RULE_LAYOUT["view_dorm_common"] = {}` stood for "no box in the sidecar" | it empties `RULE_LAYOUT["pose_dorm_common"]` as well (and puts both back) | `view_pose` reads `pose_<place>.json` before the `view_` file's `poses` key (3.2, K15), and the overlay U0a gave this harness holds its two test boxes in both files. Proven: `p2_view` 130 of 130 with the edit, 128 without. Nothing else in a harness older than this sitting was edited |

The four D60 rows above (the lock icon's line in `p2_paths`, the unique keys of
`p2_hud`, the `zz` hotspots, "any other line that looks at what a hotspot
draws") are **the second sitting's**: the first built no shapes, and with no
shaped place every one of those lines passes as it is.

**Turned by U0c2's second sitting (D60; 10 Oct).** The ten harnesses the
acceptance names (`p2_paths`, `p2_rooms`, `p2_hud`, `p2_view`, `p2_saves`,
`p2_contracts`, `p2_cards`, `p2_night`, `u2_home`, `phase2_all`) were run over
the generated overlay that shapes every one of the 35 places with every
picture at revision 2 (`tools/smoke/make_shape_overlay.py`; a harness with an
overlay of its own gets the two merged with `--with`). Seven passed unedited.
Three lines failed, one in each of three harnesses, and each was turned into a
rule that holds in a place with buttons and in a shaped one. Each can still
fail where the place draws buttons: the old condition is still the one read
there.

| harness line | was | is now | why |
|---|---|---|---|
| `p2_paths`, "it is drawn as the lock icon (an open exit keeps its place's icon)" (the plan's `p2_paths.rpy:591-593`) | the locked exit's button draws the `lock` icon and not `place_storehouse`; the open exit's draws `place_dojo` | the same, **where the two exits have no traced shape** (`hot_shapes_for("training_yard")`). Where they have: neither square draws an icon, the shape says the lock's reason under `hotshape_<id>`, the locked exit's square and shape both do nothing, and the open exit's two both return `("act", "path_dojo")` | D60: a shaped hotspot draws no icon. It would have failed at batch 1, when the Training Yard is shaped, at an art sitting. The line after it (the alpha wrapper at 0.45 and 1.0) holds in both kinds of place and is not edited |
| `p2_rooms`, "E: the test sidecar hot_dorm.json is the one read (the asset overlay)" | `rule_layout("hot_dorm") == {"spots": {...}}`, the whole file | `set(rule_layout("hot_dorm")) <= {"spots", "shapes", "keep_tile"}` and `rule_layout("hot_dorm").get("spots") == {...}`: the test file's points are what is read, and beside them the file holds nothing but the two keys D60 may add (review round 1 tightened it from `.get("spots")` alone, to match `p2_contracts`' sister line) | the generated overlay adds `shapes` and `keep_tile` to the harness's own test sidecar. It is the overlay's doing and not a real place's: a real `hot_dorm.json` is replaced whole by the harness's file. The rule still fails when the test file is not the one read |
| `p2_contracts`, "rule_layout('hot_dorm_common') reads the hotspot sidecar, and only it" | `set(_zz_hot) == {"spots"}` and the points | the points, and no key that is not a `hot_` file's (`spots`, `shapes`, `keep_tile`) | the same: the overlay adds the two D60 keys to the harness's own test sidecar. "Only it" still means nothing of the `view_` file |

What passed unedited, and why it could: the lines that read `hot_validate() ==
[]` with the harnesses' own `zz` hotspots registered in real places (the rule
leaves out ids that begin `zz`, and each is drawn as its button above the
shapes); `p2_hud`'s "every hover label's key is unique" (the shape's key is
`hotshape_<id>`); every line that finds a hotspot by `hot_<id>` and reads its
rectangle, action, label or alpha wrapper (the square keeps all four); every
line that counts the place view's buttons before and after something (the
count is larger in a shaped place by one for each shaped hotspot, the same
before and after). `p2_hud` failed its "hovered, no corner button's label
meets a neighbour" line once in the first run of the ten (the hover label read
None, the known "needs the pointer" kind) and passed 129 of 129 when run again
alone over the same overlay.

Also handed on: the Library's description is rewritten for a bright room by U1 ("the Library's and the Dormitories' words", plan 10.2); the Teachers' Dormitory stand-in was brightened in 56f0ea0 (it was nearly black at Night) and is still a borrowed picture.

## Part 2c. Owed to U0n, rooms lit at Night (written 11 Oct, before the package starts: D43, K13)

The plan's 5.7a (D61; the owner's yes of 11 Oct, O47) puts two people out late: Megumi in the Library on Sunday Nights and Toge on Wednesday Nights (`WORLD_LATE`). A second reader traced every harness line that crosses a Night: these are the only ones that change. Every line that fixes a Tuesday, a Friday or a Saturday Night holds as written, the frozen `u2_contracts.rpy` among them (its Nights are days 2 and 6).

| harness line | pins | changed by | fixed by |
|---|---|---|---|
| `u2_home.rpy:1163-1180`, "D: on each of the seven Nights everyone who lives on campus is in their own home ... and the garden, the Common Room, the girls' corridor and the lounge are empty" | where all ten are on each of the seven Nights | U0n: on day 10 (a Wednesday) Toge, and on day 14 (a Sunday) Megumi, are in the Library | U0n: "in their own home, or where `WORLD_LATE` puts them that Night"; the four empty places stay empty |
| `wp1_world.rpy`, the copy of the old schedule and the line that compares `char_location` with it (about `:282-299`; the copy is `:52-81` and `zz_old_location`, `:87-103`) | where each of the original nine is on days 1 to 14 at all five periods | U0n: days 3 and 10 (Toge), 7 and 14 (Megumi), at Night | U0n: the copy learns the late table, as it learned the away table (`ZZ_OLD_AWAY`) |
| `p2_view.rpy:714-740`, the pose plan's check | every `POSES` row's picture is in `TIME_VARIANT` at an hour the routine has the person there; exactly one row comes another way (the Gojo night's) | the first pose painted on a `lit` picture (7.2 rows 16 to 21, and the three of 5.7a): a lit picture is in `WORLD_LIT`, and the routine never has a late stayer in the Library. **With the poses, not before** | U3: a row's picture is read from `TIME_VARIANT` or `WORLD_LIT`, and a `lit` row's hours from the Night cells of the schedule and the late table |

Lines that cross a Sunday or a Wednesday Night and hold: `u2_home.rpy:1181-1184` (the asleep lists: each stayer is awake that Night), `wp1_world.rpy:317-334` with `:351` and `:361`, `wp4_board.rpy:307-321`, `wp3_missions.rpy:412-419` and `:454-466`; `p2_hud.rpy:810-816` and `p2_contracts.rpy:237-255` sweep day 3 and hold because their roster has no Toge that day. If a later package puts Toge on that roster, these two meet him in the Library at Night.

## Part 3. The scratch-tree confirmation: what a stub of wave 0 breaks

A scratch copy of the tree was given a crude stub of what wave 0 changes in who
is where: the eleven places (borrowed pictures, legal exit points, a pin
each), my room behind the Boys' Dormitory, **the whole Night column of 4.3,
the five starred weekend cells, the two weekend Evening cells, the lounge and
bath cells, the Sunday afternoons in Tokyo, and sleepers left off the stage**.
It linted clean. Then every harness in `tools/README.md` was run against it.

**Passed unchanged (21):** `core_flow`, `wp0_stubs`, `wp2_grades`,
`wp3_missions`, `wp4_board`, `wp5_memories`, `wp6_items`, `wp7_ui`,
`wp8_journal`, `wp9_prologue`, `wp10_chapters`, `wp11_dev`, `phase1_all`,
`p2_hud`, `p2_journal`, `p2_view`, `p2_rooms`, `p2_cards`,
`p2_gear`, `p2_night`, `p2_oldsave`. (`phase2_all` passed against the stub and
was listed here; it did not pass against the real places, see "Found after this
run" below.) (`wp4_board` passes in the full stub
because three students are off campus on Sunday afternoons; with U0b alone its
ledger row above applies.)

**Failed (5, and the baseline comparison), every failing check listed.**
"stub" means the crude stub caused it and the real package will not;
"**not in the plan's ledger**" marks the lines this run found that nobody had
listed, which is what the run was for. There are thirteen of them.

**`p2_contracts`** (1)

| the check | whose | what it means |
|---|---|---|
| icon coverage: every activity, place action (every room x period), tab, area and room maps to an icon | U0b, U0c1 | the new places need icons (sheet 4: `ICONS`, `ICON_FOR`); fixed by the 26 icon rows |

**`p2_map`** (11)

| the check | whose | what it means |
|---|---|---|
| level 2: zz_words <= 18 in every area (K11) | stub | the stub pins all eleven new places; the plan leaves seven rooms pinless (`WORLD_PINLESS`), which brings Dormitories and Staff to 17 |
| level 2: at most 6 pins (the hub's included) + 5 buttons in every area (K11) | stub | the same: with the pinless rooms off the map the Dormitories have six pins |
| no pin overlaps another pin of its area, or Back | stub | the stub's pins stand in a row; real points come from the layout |
| the shipped sidecars: every room of each area has a point inside the frame, and no two pins of an area are closer than 240 px across and 120 px down | U0b, U0c1 | **not in the plan's ledger.** `p2_map` wants every pin of an area 240 px across and 120 px down from its neighbours, in `area_<key>.json` or the code's default. Each new pin must be given such a point in the commit that adds it |
| at Night the girls' dormitory is locked with people in it | U0b, U0c1 | ledger: `p2_map`, the Night in the girls' corridor and the garden |
| the open places' pins still show who is there | U0b, U0c1 | the same ledger row: the garden is empty at Night |
| person_now: hidden=True for someone in a locked room, and the room isn't given away | U0b, U0c1, then U1 | ledger: `p2_map`, `person_now("nobara")` at Night |
| person_now: someone off campus | U0b | the same ledger row: Megumi is in his room at Night, no longer off campus |
| five areas as shipped: no hovered pin's label meets another pin, the Dormitories among them (hover check: needs the pointer) | stub | pins in a row (the count itself is now read from the pinned places) |
| stand-in: the word counts are the same without icon art (17, 29), and no icon is a question mark | U0b, U0c1 | **not in the plan's ledger.** `p2_map` holds the map's word counts without icon art as the literals (17, 29); every new pinned place adds words. Whoever owns `p2_map` that sitting updates the pair in the same commit |
| stand-in: the area view works on the stand-in picture | U0c1 | **not in the plan's ledger.** `p2_map` lists the Training Grounds' `row_` ids; the pool adds `row_pool` |

**`p2_paths`** (14)

| the check | whose | what it means |
|---|---|---|
| every room's first exit leads to its area's hub | U0b | **not in the plan's ledger.** `p2_paths` section 1: a room inside a house leads to its house first. The check must learn `world_inside` (the house rule, 4.4) |
| every hub has an exit to each of its rooms and to each neighbouring hub, and no other | U0b | **not in the plan's ledger.** The same rule from the yard's side: a yard has no exit to a room inside a house |
| icons are existing names: place_<room> for a room, area_<key> for a hub (in the room and in the column) | U0b, U0c1 | the new places' icons (sheet 4), and `path_icon` for a yard once its own icon is cut (3.1) |
| the exit in my room is a button in the picture that returns ('act', 'path_dorm_yard') | U0b | ledger: `p2_paths`, "the exit in my room walks to the Dormitory Garden" |
| its hover label reads To the Dormitory Garden | U0b | the same ledger row |
| hover labels read naturally: To My Room, To the Courtyard, To Utahime's Office | U0b | ledger: `p2_paths`, the garden's exit reads "To My Room" |
| at Night under the strict rule the exit is still offered and still walks | U0b | **not in the plan's ledger.** `p2_paths` section 2 walks `hot_go_dorm__dorm_yard` at Night; the id is `hot_go_dorm__boys_dorm` now |
| the Night's place view draws it as a live button (not 'Too late. Bed.') | U0b | the same lines |
| a hub at Night offers its exits beside Go to bed | U0b | **not in the plan's ledger.** The line asks for `path_dorm` among the garden's exits at Night; it is `path_boys_dorm` now |
| on arrival (the caption up) every exit button of each of the five hubs, as drawn, is clear of it | stub | the stub's exit points; real ones come from the layout sitting (the rule stands) |
| in the six hubs every exit's hover label (33 of them) is on screen and covers no other exit of its hub (hover check: needs the pointer) | stub | the stub's exit points (the count is read from the table: 33 in the stub) |
| every new hub has one or two people in its week (D57) | U0b, U0c1 | **not in the plan's ledger.** `p2_paths` (D57) wants one or two people in each yard's week. The garden loses its Night pair and gains Yuji on weekend Evenings, and the starred cells take people out of two yards. The owner of the schedule rereads the line and the sentence it prints |
| at Night whatever can be started with Panda in the common room can be started with him in the garden (Bond 100) | U0b | ledger: `p2_paths`, Panda at Night |
| abort: the walk's click 'hot_go_dorm__dorm_yard' returned 'zz_missing' | U0b | ledger: `p2_paths`, the loop walk out of my room. **Everything after it in the file did not run in the stub** (about a dozen checks, the save in a yard and the Night garden line among them), so `p2_paths` is rerun whole once this line is fixed |

**`p2_saves`** (2)

| the check | whose | what it means |
|---|---|---|
| stage 1: the button hot_go_dorm__dorm_yard is on sb_place | U0b | ledger: `p2_saves` presses `hot_go_dorm__dorm_yard` |
| every save was made, loaded and compared (22): missing | U0b | follows from the line above: the run stops there, so `p2_saves` is rerun whole after the fix |

**`wp1_world`** (10)

| the check | whose | what it means |
|---|---|---|
| places_in (P9, D53: each area's hub is first) | U0b, U0c | ledger: `wp1_world`, `places_in("dorms")`, `places_in("staff")` |
| regression: days 1-14 x 5 periods, the original 9 match the pre-phase-1 schedule and Gojo's roll | U0b, U0c1 | ledger: `wp1_world`, the frozen copy of the schedule |
| Panda and Toge spend the Evening in the library, weekends too; Panda's Night is the dormitory garden, beside Yuji, on all seven days | U0b | ledger: `wp1_world`, who is in the garden at Night |
| by the routine, five stand together only in the cafeteria at Noon and at the riverside on a weekend Afternoon | U0b, U0c1 | ledger: `wp1_world`, "only the cafeteria and the riverside hold five" |
| Utahime's weekday | U0c1 | **not in the plan's ledger.** `wp1_world` holds Utahime's five weekday cells; her Night is the Teachers' Dormitory now |
| Utahime's weekend | U0c1 | **not in the plan's ledger.** the same for her weekend (the lounge in the Afternoon, the baths in the Evening) |
| Ijichi at the gate, mornings to afternoons | U0c1 | **not in the plan's ledger.** `wp1_world` holds Ijichi's phrase; his Evening is the lounge and his Night the Teachers' Dormitory |
| Ijichi keeps his hours on weekends | U0c1 | **not in the plan's ledger.** the same, at weekends |
| when_at maki dojo: weekday mornings and noon; weekend noon | U0b, U0c1 | the ledger's row for weekend lines "not read line by line": Maki's weekend Morning and Evening leave the dojo |
| usual_places maki: Dojo (mornings and noon) · Training Hall (afternoons) · Riverside (evenings) · Maki's Room (nights) | U0c1 | **not in the plan's ledger.** `wp1_world` holds the whole sentence of `usual_places("maki")`; her Night adds her room |

**`u2_baseline`** (5)

| the check | whose | what it means |
|---|---|---|
| baseline: who is where, for the eleven, every hour of a week (where) | on purpose | `u2_baseline` is the comparison itself: these parts differ by design, and `u2_world` (U1) checks the new week against `baseline_u2.json` |
| baseline: who is in each place, every hour of a week (here) | on purpose | `u2_baseline` is the comparison itself: these parts differ by design, and `u2_world` (U1) checks the new week against `baseline_u2.json` |
| baseline: every place's exits and where they are drawn (exits) | on purpose | `u2_baseline` is the comparison itself: these parts differ by design, and `u2_world` (U1) checks the new week against `baseline_u2.json` |
| baseline: what the icon column offers, place by place (rail) | on purpose | `u2_baseline` is the comparison itself: these parts differ by design, and `u2_world` (U1) checks the new week against `baseline_u2.json` |
| baseline: place_actions for every place and period | on purpose | `u2_baseline` is the comparison itself: these parts differ by design, and `u2_world` (U1) checks the new week against `baseline_u2.json` |

**What this run could not see.** `p2_paths` and `p2_saves` stop at the first
press of `hot_go_dorm__dorm_yard`, so the checks after it did not run against
the stub; both are rerun whole by U0b once that line is fixed, and a line that
then fails and is not in Part 2 is a finding to bring back here. The stub had
no Bond doors, so no door line was exercised (`p2_paths`' lock lines passed
because the doors were open); `u2_home` is U0b's own harness for those.
