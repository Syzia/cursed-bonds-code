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
| `p2_hud` section 3b, the eight named tiles ("the label of 'Practice' hides nothing where it opens") | the label opens on a named side, and opened on the other it "used to" cover a named exit | the label hides no exit, hotspot or corner button where it opens, and reads its title; the side and what it would have covered are a note | an exit placed where the label opens (the first moved-points overlay did exactly that): FAIL |
| `p2_rooms` "the machine's point is clear of where one to four people stand" | the code row of `HOT_SPOTS` | the machine's applied point (the sidecar's) | the same sidecar: FAIL |

**The moved-points test** (the acceptance of U0a): with an overlay that moves
every exit, the hotspot, every slot of the Courtyard and every pin of the
Dormitories' map at least 50 px to other legal points, `p2_paths`, `p2_rooms`,
`p2_view`, `p2_hud`, `p2_map`, `p2_contracts` and `wp1_world` pass. The first
overlay tried was not legal, and two rules that are still rules said so: the
gate's exit was hidden by the Courtyard's commonest pair (`p2_paths`, "with two
people the gate exit is in the picture ..."), and the Training Yard's exit sat
where the label of "Practice" opens (`p2_hud`, section 3b). Both are what a
layout sitting must respect. The second showed that `p2_hud`'s eight named
tiles still pinned a side and a covered exit of the old pictures; that line
became the rule in the table above.

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
| `wp8_journal.rpy` and `p2_contracts.rpy:1520` | the Preferences rows' words (MOTION, On, Off) | U6 (a row added, none renamed) | U6 |
| `tools/make_icon_workflow.py`'s own check | the sheets equal `ICONS` | U0b | U0b |
| `wp0_stubs.rpy:574`, and the trips in `phase1_all` and `phase2_all` | `call sb_trip(...)` runs to the end without a click | unchanged; listed so nobody removes the autoplay line | – |
| `p2_map.rpy:603-618` | the Tokyo layer's ids | unchanged | – |
| `p2_journal.rpy:593-637` | patches `person_now` with the old "Somewhere I can't go right now" | unchanged (a patch of its own) | – |
| `p2_paths.rpy:604-623` | the girls' corridor's lock in the Evening with the flag discarded | unchanged while Bond is below the door's level; U0c1 confirms | U0c1 |

---

## Part 3. The scratch-tree confirmation: what a stub of wave 0 breaks

A scratch copy of the tree was given a crude stub of what wave 0 changes in who
is where: the eleven places (borrowed pictures, legal exit points, a pin
each), my room behind the Boys' Dormitory, **the whole Night column of 4.3,
the five starred weekend cells, the two weekend Evening cells, the lounge and
bath cells, the Sunday afternoons in Tokyo, and sleepers left off the stage**.
It linted clean. Then every harness in `tools/README.md` was run against it.

**Passed unchanged (22):** `core_flow`, `wp0_stubs`, `wp2_grades`,
`wp3_missions`, `wp4_board`, `wp5_memories`, `wp6_items`, `wp7_ui`,
`wp8_journal`, `wp9_prologue`, `wp10_chapters`, `wp11_dev`, `phase1_all`,
`phase2_all`, `p2_hud`, `p2_journal`, `p2_view`, `p2_rooms`, `p2_cards`,
`p2_gear`, `p2_night`, `p2_oldsave`. (`wp4_board` passes in the full stub
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
