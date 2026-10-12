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

**Changed by U0n (its first sitting, 12 Oct): the two lines above, old and new.**

| harness line | old | new |
|---|---|---|
| `u2_home.rpy`, section D's first check (the loop over days 8 to 14 and its `check`) | the test `char_location(w) != home or world_home(w) != home`; the name "D: on each of the seven Nights everyone who lives on campus is in their own home (the four boys, the two girls, Shoko, the three teachers), and the garden, the Common Room, the girls' corridor and the lounge are empty" | the test `char_location(w) != (world_late_cell(w) or home) or world_home(w) != home`; the name "D: on each of the seven Nights everyone who lives on campus is in their own home, or where WORLD_LATE puts them that Night (the four boys, ...), and the garden, the Common Room, the girls' corridor and the lounge are empty". The four empty places are tested as before |
| `wp1_world.rpy`, the copy of the old schedule (`zz_old_location`) | after the away table: nothing | a copy of the late table, `ZZ_OLD_LATE = {("megumi", "Sun", "Night"): "library", ("toge", "Wed", "Night"): "library"}`, read after `ZZ_OLD_AWAY` (`loc = ZZ_OLD_LATE.get((who, wd, per), loc)`). The check's name and test are unchanged ("regression: days 1-14 x 5 periods, the original 9 match the pre-phase-1 schedule and Gojo's roll") |

Each was seen to fail, in two scratch copies. (1) With the table wrong (Megumi's row moved to the Cafeteria on Mondays in `sb_world.rpy`): `wp1_world`'s regression line fails on days 1, 7, 8 and 14, and `u2_home` fails beside the ledger line, on its asleep lists (Megumi is no longer asleep at home on a Monday) and on lint; its ledger line follows the table, as its new wording says, and so holds. (2) With the table right and `char_location` no longer reading it: `u2_home`'s ledger line fails (`('Wed', 'toge', 'senpai_room'), ('Sun', 'megumi', 'megumi_room')`) and `wp1_world`'s on days 3, 7, 10 and 14. The third row above (`p2_view.rpy`, the pose plan's check) is still owed, to U3, with the first pose painted on a `lit` picture.

## Part 2d. Found at Yuji's install (12 Oct 2026; D57)

Yuji's redrawn set went in on 12 Oct (`tools/install_set.py yuji`): six sprites, six side portraits, his blink and his talking mouth, his rows in `game/layout/faces.json` and `game/jjk_sprites.rpy` regenerated. His eyes and mouth sit elsewhere on the new drawing, and his blink sits on his calm face only (the old drawing's blink also sat on happy, sad, serious and surprised). Three kinds of line pinned the old drawing; none was in the plan's ledger. Each is changed in the commit before the install's, and each holds on the tree before the install and after it.

| line | pinned | now |
|---|---|---|
| `p2_view.rpy`, section 8, "lit_sprite adds the two layers on a compatible expression (neutral), only the blink on Yuji's happy face (VIEW_BLINK_ALSO: integration)", and the two lines after it ("the happy layer is the eye box", "the layers are the eye box and the mouth box") | that the faces Yuji blinks on, and the boxes of his eyes and mouth, are the code's tables (`VIEW_BLINK_ALSO`, `VIEW_FACE`). With his `faces.json` rows installed the first failed and the second raised an IndexError, which stopped the harness at 66 of its 130 lines | the three build their sprites as with no `faces.json` (`zzv_no_faces`), so they test the mechanism on the code's tables, as before; and one line is added, the rule on the tree as it is: the blink sits on exactly the faces `VIEW_BLINK_OK` and `view_blink_also` name, the mouth on `VIEW_TALK_OK`'s, and the two layers are the boxes `view_face_box` answers. 131 lines. Seen to pass with an empty `faces.json` laid by overlay (the tree before the install), and the new line seen to fail when the layers read `VIEW_FACE` in place of `view_face_box` |
| `u2_baseline`: "K9: lit_sprite builds the tree it built" and "picture: map_campus.png is pixel for pixel the baseline's" | his sprite's arguments (the tree's first line holds his feet numbers, (389, 1365, 313), now (382, 1365, 315)); and the map's first level, which shows his face on the Training marker | `tools/smoke/baseline_sprite_tree.txt` written again from `U2_BASELINE_WRITE=1` once the tree was seen to differ in that first line and the two pickle sums only (A2 of the contracts foresaw the sums, not the first line); `baseline_shots/ui2/map_campus.png` and its sum in `shots.json` written again from the same run, the difference being 272 pixels in a 20 px square, his face. The other four pictures are byte for byte the baseline's. `u2_baseline` reads 47 lines and its six differences by design, as before the install |
| `tools/test_art_tools.py`, group face: two lines "... the tree is unchanged (D57)", and three lines "REAL: Yuji's first blink render ..." | that the tree has no `game/layout/faces.json` at all; and that the tree's Yuji is the drawing his first blink render (4 Oct) was cut from | the two ask that the file holds no row for the person the test installs (the tree hash beside them already says nothing in it changed); the three lay his six sprites of before the redraw under their scratch root, from git at `f966a99` (`YUJI_BEFORE`), and are SKIPPED with the reason where git does not hold that commit |

## Part 2e. Found at the installs of 12 Oct (twenty-four pictures, then the six yards; K3)

Commit `25a3e3e` installed twenty-four pictures with `tools/install_redo.py`: the evenings and nights of the Courtyard, the Library, the Common Room, My Room, the Cafeteria, the Classroom, the Infirmary and the Rooftop, the Library's and My Room's `lit`, and six day pictures (the Common Room and the Cafeteria at revision 3). Seven harness lines had taken the Cafeteria or the Classroom as their example of "a room with one picture", "an hour that is only a tint" or "a room with no night picture", and two of the baseline's pictures are taken in the Classroom. Later the same day the six main yards went in with their traced layouts (`7ddaadf`, `e0559b3`), and two lines of `u2_home` that pinned where the yards' exits stood on their old pictures failed in turn. None was a fault of the game; none was in the plan's ledger. More pictures go in daily until every place has its day, its evening and its night, so no real room can stand for "a room without one" any longer: each line is now a rule that reads the same whatever is installed.

**How each became a rule.** Where a line needs a room without an hour picture, that room's hour cells are taken out of `TIME_VARIANT` for the length of the reading and put back (`_zz_cells = TIME_VARIANT.pop("<room>", None)` ... `if _zz_cells is not None: TIME_VARIANT["<room>"] = _zz_cells`). The room is then what any room with no cell is to `bg_variant`: its day picture, tinted. It is the harnesses' own way (`u2_contracts`' header: it changes `TIME_VARIANT` in place to test a gate and puts it back; `u2_lit`'s `zzl_night` sets the Library's Night cell for a test). Where a line needs "no such picture" it names one the game does not have (the room `zz_no_such_room`, the attribute `zz_no_picture`). Every check keeps its name, and every harness its count.

**`u2_contracts.rpy`** (frozen: these five checks and nothing else in the file; each carries a comment naming this part):

| check | old | new | why it failed on 12 Oct |
|---|---|---|---|
| "A: gate 2, today: view_fg_path answers the cut for the hour's picture" | `view_fg_path("cafeteria", "Night") == "images/fg/fg_cafeteria.png" and view_fg_path("dorm", "Noon") is None` (after the two Common Room clauses) | `_zz_fg_one = view_fg_path("cafeteria", "Night")` is read with the Cafeteria's cells taken out, and the check asks `_zz_fg_one == "images/fg/fg_cafeteria.png" and (world_fg_room("dorm") or view_fg_path("dorm", "Noon") is None) and view_fg_path("zz_no_such_room", "Noon") is None`. The two Common Room clauses are as they were | the Cafeteria has a night picture with a cut of its own, so at Night `view_fg_path` rightly answers `fg_cafeteria_night.png`. (My Room is asked only while it has no cut, and a name the game does not have always: "a room with no cut" no longer leans on a real room either) |
| "A: gate 4: at an hour that is only a tint the general row stays (the night row waits for the night picture)" | `_zz_tint = (light_for_place("classroom", "Night"), light_for_place("classroom", "Evening"))`, read as the Classroom stands | the same reading, with the Classroom's cells taken out before it and put back after it. The check is unchanged | the Classroom has a night picture, so at Night `light_for_place` rightly reads the test's `night` row, `("#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3)` |
| "A: lint reports a TIME_VARIANT cell with no image" | the test cell `TIME_VARIANT["classroom"]["Night"] = "night"`, and `"bg classroom night" in _zz_f[0]` | the test cell is `"zz_no_picture"`, and the finding is asked for `"bg classroom zz_no_picture"` | `bg classroom night` exists now, so lint rightly reports nothing |
| "B: view_slot_light reads the hour's row for that many people: the day row by day, a period's own row first, and no night row while the room has no night picture" | read as the Classroom stands (`view_slot_light("classroom", 1, 0, "Night") is None`) | the check is unchanged; it and the next are read with the Classroom's cells taken out, put back after the second | with a night picture `view_hour_row` rightly reads the test's `night` row: `("#000000", 0.5)` |
| "B: view_cast and view_talk read their keys (an hour with no row of its own takes the row of the picture that shows)" | read as the Classroom stands (`view_cast("classroom", "Night") == (35, 1.4, 0.3)`, the day row) | unchanged, inside the same pair of lines as the check above | the test's `cast` has no `night` row, so with a night picture showing the answer is rightly None |

**`p2_view.rpy`** (two checks; its overlay lays an empty manifest, so both are read with every picture fresh):

| check | old | new | why it failed on 12 Oct |
|---|---|---|---|
| "view_fg picks the variant's file for the hour, the day file where the room has one picture, none elsewhere" | `view_fg_path("cafeteria", "Night") == "images/fg/fg_cafeteria.png" and view_fg_path("dorm", "Night") is None and view_fg_path("riverside", "Noon") is None` (after the three Common Room clauses) | `_zz_fg_one`, read with the Cafeteria's cells taken out, `== "images/fg/fg_cafeteria.png"`; `(world_fg_room("dorm") or view_fg_path("dorm", "Night") is None) and (world_fg_room("riverside") or view_fg_path("riverside", "Noon") is None) and view_fg_path("zz_no_such_room", "Noon") is None` | as gate 2 above |
| "the foreground view_enter shows pickles, tinted (the cafeteria in the Evening) or not" | `_zz_img = view_fg_image(view_fg_path("cafeteria", "Evening"), "cafeteria")`, read as the Cafeteria stands, and `isinstance(_zz_img, Transform)` | the same, built with the Cafeteria's cells taken out; what `graded_bg` holds for the Cafeteria's Evening is dropped from `_BG_CACHE` before and after, so the room is built once as a tinted room and once more as it is. The check is unchanged | the Cafeteria's Evening is a painted picture now and is shown untinted, so its foreground is rightly a plain picture and not a `Transform` |

**Proved for the seven**, on 12 Oct. (a) On today's tree: `u2_contracts` 245 with its overlay and 242 bare, `p2_view` 131, as before the installs. (b) On the tree before these installs (a scratch copy of the tree with the 45 files of `25a3e3e` put back from `e26c67b`, run with its own `tools/smoke.sh`): 245, 242 and 131 again; and on the tree with the six yards installed as well (a scratch copy laid at `e0559b3`): 245, 242 and 131. (c) No line reads a real room as lacking a picture. (d) Each still fails when the game code it stands for is weakened, tried once in an overlay that lays the edited `.rpy` files over the scratch copy: with `view_fg_path` picking the cut by the hour's name and not by `bg_variant`, both foreground lines fail; with `light_for_place` reading a measured row at every hour by the hour's name, gate 4's line; with lint no longer asking whether a cell's image exists, lint's line; with `view_hour_row` picking the row by the hour's name, the slot light's and the cast's lines; with `view_fg_image` returning the picture untinted, the pickle line. `u2_contracts` then read 239 and 6 (the five, and "gate 2: recut for the new picture ...", which reads `view_fg_path` too), `p2_view` 129 and exactly its two.

**`u2_baseline`: `place.png` and `person.png` written again.** Both are taken in the Classroom on a Tuesday Morning, and the Classroom has its new day picture and a light row measured on it. Seen before rewriting:

- with the Classroom's old picture laid back over today's tree (an overlay of `classroom.png` from `e26c67b`, an empty `light_classroom.json`, and the manifest without the Classroom's six rows), both pictures come out **byte for byte the old baseline's** (`3981d3c5...`, `31305a83...`), and the harness reads 47 lines and its six by design. So nothing but the Classroom's picture and its light row changed them: the HUD, the people, the card and the texts are drawn where they were;
- with the new picture and only the light row emptied, 31,572 pixels of `place.png` and 50,544 of `person.png` differ from the new pictures, all inside Megumi's box (x 245 to 421, y 265 to 692; and x 234 to 458, y 163 to 706), by at most 10 in a channel: that is the measured light on him. Of those pixels, 86% are the same in the old baseline and in the new picture's shot under the old light: he stands where he stood (the rest is his soft edge over another background). Outside his box the pixels that did not change are the things drawn solid over the room: the two hotspot buttons, his name tag, the corner buttons and the day's label in `place.png`; the card (71,359 pixels in one piece) and the same corners in `person.png`.

Then `U2_BASELINE_WRITE=1 tools/smoke.sh u2_baseline`, and from what it wrote only `place.png`, `person.png` and their two sums in `shots.json` (the file it wrote differs from the old one in those two sums alone; the other three pictures are byte for byte the baseline's). `u2_baseline` reads 47 lines PASS and six FAIL by design, as before: the five of Part 3 below (`where`, `here`, `exits`, `rail`, `place_actions`) and "names: every statement of game/sb_night.rpy keeps its name and its identity", which compares with the file as it was before U0c2 (`baseline_night_names_u0a.json`; `docs/UI2_CONTRACTS.md` A2) and names the five init statements that package's edits replaced.

**`u2_home.rpy`** (two checks; found when the six main yards went in with their traced layouts, commits `7ddaadf` and `e0559b3`: the School Courtyard, the Dormitory Garden, the Training Yard, the Staff Building Steps, the Mountain Path and the gate, each a `hot_<place>.json` and a `view_<place>.json` with `for_rev` 2). Both pinned where the yards' exits stood on yesterday's pictures, by reading `path_exits()`, which is the point on screen: the code's point (`PATH_EXITS`) with the place's `hot_` file applied. K12 is about the first of those: "on the old pictures the old exits stay where they were". A layout traced on a new picture moves the point on screen, and is meant to.

| check | old | new | why it failed |
|---|---|---|---|
| "B: both exits keep the points they had before the overhaul (U0a's baseline): the left house's steps in the garden, my door in my room; the garden's other six are as they were" | `path_exits("dorm_yard")` and `path_exits("dorm")` against the baseline's points | the same comparisons made on `zzh_code_points(place)`: the place's exits read with its `hot_` file taken as absent (the file is put back before it returns), which is where the code has them and so where they stood on the picture of before the overhaul. And for a place whose `hot_` file carries no `for_rev` (`not zzh_traced(place)`: no layout traced on a new picture is installed), the points on screen (`zzh_exit_points`) must be those same points: `_zz_drawn` lists a place where they are not, and must be empty | the garden's traced layout puts the Boys' Dormitory's steps at (345, 575), not (248, 728), and its other six where the new picture has them |
| "B: in the three yards that gained an exit, and in the girls' corridor, every old exit keeps its point and its order (K12)" | every baseline row of the four places is among `path_exits(place)`'s points | every baseline row is among `zzh_code_points(place)`, and, where the place is not traced, among the points on screen too. The order is read as before: it is `PATH_EXITS`' own, and a layout moves points, never the order | the Staff Building Steps, the Training Yard and the Mountain Path have their traced layouts: fourteen old exits stand elsewhere on screen |

Proved on 12 Oct: 220 on today's tree; 220 with the six yards laid over it (an overlay of the 25 game files `e0559b3` holds beyond this tree: their pictures, `hot_`, `view_` and `light_` files and the manifest), where the two lines read 218 and 2 before the edit; 220 on the tree before the day's installs (`e26c67b`). Each still fails: with one old exit of the garden and one of the staff steps moved 20 px in `PATH_EXITS` (an overlay with the edited `room_paths.rpy`) both lines fail and nothing else does, on today's tree and with the six yards laid as well (218 and 2 each time). So the rule holds for a place still on its old picture, says nothing false of a place with its new picture and layout, and still catches a point moved in the code under either.

**`tools/test_art_tools.py`**, the art tools' suite (465 lines; 462 before). Its scratch copies are the tree as it was before the overhaul installed anything (`before_overhaul()`, `mkroot()`). Run after the twenty-four installs it failed four lines and stopped at a traceback in its compose group (a fifth, in `status`, lay behind the traceback); on the tree with the six yards, with those mended, five more failed. What upset it was never a tool's rule: the fixtures put back less than an install writes, and a few lines compared a scratch copy, or a test layout, with the real tree of today.

| what | why it failed | now |
|---|---|---|
| the copies' campus record | `before_overhaul()` put back a picture's own row of the record and left the facts the picture fixes. An install moves the place's row (and a composed picture's exits and ground) from `proposed` to `fixed` and stamps each `by` the picture at its revision; a second install stamps them again. So the copy's record held facts fixed by a picture it had at another revision (the Common Room and the Cafeteria, at revision 3) or did not have at all (My Room, the Classroom, the Infirmary, the Rooftop): ten findings of `check_campus.py`. `--compose` refuses to install into such a record: two lines failed, and the next line fell over on the layout file that was never written | `before_overhaul()` also answers `facts` (every row today's record has as fixed by an installed picture, as the record of then held it) and `waived`, and `record_before()` lays them in: a proposal again where it was one, in its old place in the list; the old revision where it was stamped again; a fact written since follows its picture's row of then. On the tree of `25a3e3e` what comes out is, row for row, the record git holds from before batch 0 |
| the copies' foreground outlines (`tools/fg/<place>.json`) | an hour picture's install copies the day outline to that hour; the copy kept the Cafeteria's `evening` and `night` outlines with no such pictures | put back as the file stood before the place's first picture went in |
| `layout`: "batch 0's four pictures are staged by their 2752 x 1536 renders, the ones the campus record names, never by a 1920 px file" | read against today's record, where the two rooms redone since name their revision-3 renders | read against the record's row as it stood before the room's first install: "... the ones the campus record named when they were chosen (its row of before the first install, whatever revision the room is at since) ..." |
| `redo`: "no foreground file was deleted, and the room's hot_ and view_ files are byte for byte what they were" | compared the copy's foreground folder with the real tree's, which holds the Cafeteria's evening and night cuts the copy has no picture for | compared with the copy itself as it stood just before the install |
| `status`: "art_status.py --check passes on a copy of the tree, and with no manifest says every picture is today's" | `art_status.py` asks git which foreground files a save may hold the path of; for a copy with no history of its own it asks this repository's HEAD, which holds two files the copy, the tree of before, never had | the copy is given the history a tree of its own has (its foreground folder, committed once, as `r_hist` is in the redo group), and the line also asks for "N ever installed, 0 missing" with N the copy's own count |
| `layout`: three cases of `check_layout.py` ("[column] a yard whose seven exits all drop into the icon column with four people", and two of "[lock-label] a door that can be locked ..."), and "python3 tools/check_campus.py --selftest passes" and "python3 tools/check_layout.py --selftest passes" | these cases lay test layouts for real yards (the Dormitory Garden, the Training Yard) and expect one rule to speak. With those yards installed their exits are fixed facts, so [campus] refuses the test layout too; their people stand where the traced layout has them, so five of the seven exits drop into the column and not seven; and `check_campus.py --selftest` reads the record with an empty manifest, as before any install | the cases and both selftests are read against the record of before (`record_before`) and a dump whose rows for the installed places are those of before (`stamp`, its hash taken over the tree). For that, `--selftest` of `check_campus.py` and of `check_layout.py` takes `--record`: the argument is handed on, and no rule of either tool changes. Run bare on a tree with yards installed the two selftests fail, as they did; they are run through `tools/test_art_tools.sh --only layout` |

Three lines are new, in `fixtures`: the record's facts on small git trees (an install committed in one commit, in two, and not yet); the outline; and "the fixtures of this tree itself: the campus record as every scratch copy holds it ... passes check_campus.py's rules for a record", which says in one line, with the findings, what this morning took a traceback to say. Seen to fail: with the facts not put back, that line and the one on the small trees fail, the first with the ten findings above. The suite reads 465 passed, 0 failed, 0 skipped on the tree of `25a3e3e`, and the same on a scratch copy of the tree with the six yards installed (`e0559b3`), where it read 460 and 5 before the `layout` lines were mended: 465 passed. The fixtures do not depend on which places are installed: each picture and what goes with it is put back by its own manifest row.

**Lines that pass today and will not, later.** Named so nobody reads them as a fault of the game when they turn:

| line | leans on | turns when |
|---|---|---|
| `wp1_world.rpy`, "gojo_office lit by PLACE_LIGHT (Evening)" and the same for Utahime's office (`config.show("graded", what=graded_bg(_loc, _p))`, then `scene_light == light_for_place(_loc, _p)`) | the office having one light row for every hour, or its Evening being the day picture under a tint. The harness shows the room under the name `graded`, and only a tinted picture carries the `_light_key` that sets the light from that; a painted evening is a plain image name, so the light stays the Morning's from the turn before. The game is right: `scene expression graded_bg()` shows a painted picture under its own name, and `_show_lit` reads the light from that | an office's evening picture goes in with its measured light rows (sitting 12). Tried on 12 Oct with test files laid by overlay for Gojo's office: with a test `gojo_office_evening.png` alone the line still holds, 156 of 156 (`PLACE_LIGHT` has one row for the office at every hour, so the stale light is the right one by chance); with that picture and a `light_gojo_office.json` holding a day row and an evening row, as `install_redo.py` writes them, it fails, 155 and 1 (the light read is the day row). The rule to turn it into: show the room as the game does, `renpy.show(d)` for a name and `config.show("graded", what=d)` for a tinted picture |
| `u2_contracts.rpy`, "A: a row whose file exists (N) has its image and its cell; a row whose file is missing (M) has neither" (and, read the same way but not tried, "A (overlay): a My Room evening file turns the Evening cell from night to evening, and it is shown as painted") | every hour picture on disk being fresh against its day picture | a tree is committed with a day picture redone and its evening or night still the old one (a sitting "a" without its "b"): the stale file is there and rightly registers no cell. Tried on 12 Oct with a manifest laid in which the Classroom is at revision 3 and its evening and night are still made for revision 2: the first line fails and nothing else does (241 and 1, bare). An ordinary install leaves nothing stale, so it holds from one install to the next |
| `u2_baseline`: the five pictures | today's art: the Classroom's day picture and its light row (`place.png`, `person.png`), the campus map and the school's map (`map_campus.png`, `map_area.png`), the main menu (`main_menu.png`) | the Classroom is redone or its light measured again; the maps' pictures go in (sittings 21 and 22); the menu's picture goes in. Each time: see that it differs by that picture alone, as here, and write that picture and its sum again |
| `p2_view.rpy`, the pose plan's check | Part 2c's third row, still owed to U3 | the first pose painted on a `lit` picture |
| `tools/test_art_tools.py`, `layout`: "batch 0's courtyard layout is installed, and game/layout/hot_courtyard.json and view_courtyard.json are the staged files (tools/art/staged/courtyard/) apart from for_rev", and the Library's | the Courtyard and the Library being installed with the layouts staged for batch 0 | either is composed again, or a point of its installed layout is moved by hand: the staged copy is then the record of batch 0 alone, and the line has to say so |

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
