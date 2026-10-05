# Phase 2: hand-offs from wave 0

*Written 3 Oct 2026 from the wave 0 (P0a, P0b, P0c) reports and its three review rounds. The wave-1 and wave-2 packages and P8 read this before they start. The plan is `docs/PHASE2_DESIGN.md`; where this file and the plan disagree about what wave 0 actually built, this file is right and P8 corrects the plan.*

## Hand-offs

Each line names who it is for.
- ALL wave-1 packages: run tools/smoke.sh tools/smoke/p2_contracts.rpy WITHOUT SMOKE_P0_STRICT. The file is frozen; NOTE lines saying a wave-0 comparison 'no longer holds' are expected once P2, P4b or P5 is in.
- ALL: after writing a screen, grep your own file for icon("...") and icon_btn("...") names and confirm each is a key of ICONS. An unknown name draws a question mark and is NOT caught by lint or check_content.
- ALL: the measuring helpers, shot() and zz_worst work over a modal screen. A harness's own renpy.pause over a modal screen still needs modal=False.
- ALL: never set up a worktree or scratch root with game/cache linked to another tree's.
- ALL: check_content.py can be called by absolute path from any folder. Never run --write-baseline (only P8, with --i-am-p0a-or-p8).
- ALL: at the top of an init python block every bound name needs the file's prefix: aliased imports, every target of a chained or bracketed assignment, `with ... as NAME`, `store.NAME =`, names under a top-level if/for/try, and every statement of `a = 1; b = 2`. A plain `import x` and `except ... as NAME` are not checked.
- ALL: never alias Function; `Function(`, `Function (`, store.Function( and renpy.store.Function( are all checked against ui_do and tools/none_ok.txt.
- ALL: call the label positionally, `call hot_use(x)`; its parameter is hot_id, not id.
- ALL: a harness using `## smoke-with: aa_zz_order.rpy` gets two inert zz hotspots (zz_order_spot in dorm, zz_tv in dorm_common), never visible.
- P1, P5, P6: run tools/smoke.sh tools/smoke/p2_contracts.rpy in your worktree before the first tools/layout_sheet.py call; it writes shots/layout/defaults.json there (shots/ is gitignored, so a new worktree has none).
- P2: keep the styles sb_action_button, sb_action_title, sb_action_hint (sb_screens.rpy) and sb_hud_nav_button (ui_hud.rpy) defined under the same names; frozen ui_icons.rpy (icon_sample) and explore.rpy (dev_panel) use them.
- P2: toast_room() must return (0, 0, 0) over icon_sample and the other sandbox/menu screens; the harness then turns its 20-tick check into a NOTE.
- P2: sb_char must keep the same set of Return values per person as baseline_p0.json (hard check, any order), with Back's ('cancel',) last in tree order.
- P2: a long icon word wraps to two or three lines in a 90 to 120 px icon button; size the rail's buttons with that in mind. hover_label uses the top side only for tooltip keys starting sample_auto_, sample_always_ or sample_never_.
- P3: in the commit that removes the Memories row from JOURNAL_TABS, journal_state must map "memories" to "people".
- P3: before roll call the People card's Next line skips the gated first hangout and shows 'Eat together at Bond 10'. When rule_hangout_gate holds a person's next hangout, show 'After roll call' instead.
- P4b: once night_exists() is True the harness skips the Night rows of person_choices and reports how many differ. Non-Night rows must still equal the baseline.
- P5: keep view_slot_rects(loc, n) in view_stage.rpy with this signature, returning n int rectangles (x, y, w, h) built from view_slots(loc, n). Frozen sb_hotspots.rpy (hot_point_findings, line 219) calls it; dropping or renaming it raises NameError for every standalone hotspot.
- P5: view_person_rects(loc) must return one rectangle per person on stage (hard harness check), and a hotspot whose square overlaps one is hidden. The harness's hotspot checks do not depend on your slot positions.
- P5: view_sync_light() and view_before_person() can be missed once by a pre-phase-2 save parked just before them; the screens must work without them having run.
- P6: final hotspot positions go in game/layout/hot_<place>.json and are linted (two numbers, x 40 to 1700 / y 180 to 1000, clear of the lanes, id registered for that place; a standalone also clear of the default stage rectangles).
- P6 / P5 / P1: tools/layout_sheet.py stops with a one-line message on a malformed sidecar. A view sidecar may hold only slots and poses, slot keys "1" to "4", each list exactly that many slots; hot and area sidecars only spots.
- P8: tools/smoke/p8_patterns/ holds the save-test patterns and a README with the two load pitfalls; build p2_saves from them (they were not re-run by the fixer).
- P8: docs to update: `label hot_use(hot_id)` in 6.1 and 4.10; journal("memories") stub column; add view_slot_rects to 6.1; ICON_SAMPLE; SMOKE_P0_STRICT, SMOKE_P0_SHOTS and baseline_shots/1818x1022/; --i-am-p0a-or-p8; --any-sheet; make_bg_workflow's --out and style_aerial.txt (and move the tool off the untouched list); the hover label's top side on the sample; the review panel's new footer text.
- P8: either add a check_content rule that reads literal first arguments of icon( / icon_btn( against ICONS, or correct 4.3's sentence about a VALIDATE line.
- P8: run `gen_gui.py --all` into a scratch output once Pillow is available. Decide whether to retake baseline_shots at a stated window size or keep the per-size folders.
- Orchestrator: wave 0's strict evidence is SMOKE_P0_STRICT=1 with SMOKE_P0_SHOTS=/Users/hunterjolly/Desktop/JJKgame.md/tools/smoke/baseline_shots/1818x1022: 136 PASS today.
- Orchestrator: use today's load report as the reference (11 SAME; compare status, not line numbers) until P8 writes docs/load_report_phase2.txt. It is at <scratchpad>/p2_p0/fix3/load/load_report.txt and will not survive a restart.
- Orchestrator: art batch 1 is ready in ~/Desktop/JJK Game images/phase2/ (five workflow files, icon_grid.png, art_batch_1.md; $1.45).

## Where wave 0 departs from the plan

- **P0a:** Baseline committed separately (de37a14) from the tooling (bc97121), so the history shows it was written before any tool changed. The plan speaks of one commit; the harness fixes are in the second.
- **P0a:** --dup-globals treats a style as a finding only when two files define it. `style x is y` then `style x:` in one file is the normal Ren'Py idiom (screens.rpy does it about 75 times); the letter of R2 would have needed 150 baseline rows and flagged every new file that writes a style the usual way.
- **P0a:** --dup-globals skips labels when --dup-labels also runs, so a duplicate label is reported once.
- **P0a:** --prefixes: a lower-case prefix also allows its capitals (`toast_` allows `TOAST_`). R1 lists only one case for some existing files, and section 8 mentions lane constants in ui_hud.rpy; prefixes.json is frozen, so a wave package could not have fixed that itself.
- **P0a:** prefixes.json has one exception R1 does not name: `persistent.motion` in view_stage.rpy (6.3 puts its default there and it cannot carry `view_`). `define config.*` is ignored by --prefixes.
- **P0a:** none_ok.txt carries a row `DEV_FUNCS[key]` (example `dev_action(key)()`), because the source check cannot resolve the subscript at explore.rpy:260. The harness runs it for every key, so P0b's six new review functions need no line.
- **P0a:** tools/smoke/baseline_check_content.txt was rewritten: it was phase 1's pre-WP0 list (506 lines, still in git history); it is now the known findings of today's tree, which check_content subtracts by file, rule and text (not line number).
- **P0a:** Overlay paths mirror the repository: files must sit under tools/smoke/assets/<harness>/game/. This follows P0b's and P0c's explicit paths (assets/p2_contracts/game/layout/...) rather than task 2's shorter wording; anything outside game/ is refused.
- **P0a:** smoke.sh additions the plan does not name: `## smoke-with: <file>.rpy` (how aa_zz_order.rpy gets installed), SMOKE_ROOT (so a harness can read baseline_p0.json and none_ok.txt), SMOKE_ASSETS (an overlay folder override, used to test the overlay without putting test files in the repo).
- **P0a:** _lib.rpy: zz_render() added; zz_worst takes hover=<id> and name=; zz_words counts Latin-letter tokens only, so a kanji seal drawn in an ordinary style is not a word.
- **P0a:** The lint and harness plumbing put the 'fresh'/'rich' fixtures, the dump and the PNG comparison inside p2_contracts.rpy (functions zz_p0_*), so P0b compares by re-running the same harness.
- **P0a:** wp2_grades, wp7_ui and wp11_dev were edited although they did not fail on fixture(): each defined its own zz_texts, which the library's would silently replace (wp2's has a different signature). wp2's is renamed zz_toast_texts; the other two now use the library's.
- **P0a:** tools/load_all_saves.sh is in P0a's row but needed no change.
- **P0b:** DEV_BUTTONS rows stay 2-tuples; a button's `when` lives in a new table DEV_WHEN (key -> function name), read by dev_rows(). wp11_dev and P0a's half of p2_contracts unpack `for k, t in DEV_BUTTONS`, so a third element would have broken them.
- **P0b:** The review grid is 3 x 6 now (three buttons hidden by `when`) and 3 x 7 once the night and the market exist; at 3 x 7 the panel is drawn tighter so it fits 1080. The plan only said "3 x 7". Close gained id "dev_close" so the harness can measure it.
- **P0b:** label hot_use's parameter is named hot_id, not id: a label parameter becomes a store variable while the label runs, which would shadow the builtin id(). The protected call `call hot_use(_r[1])` is positional and unaffected.
- **P0b:** rule_hangout_gate also passes everything in explore mode. Explore mode has no roll call, and holding the scenes there would change the old look-around mode.
- **P0b:** journal("memories") was not aliased to People. The Memories tab still exists until P3 removes its row, so an alias now would make that tab unreachable from the loop; journal() already accepts "memories". P3 adds the mapping with the row's removal.
- **P0b:** toast_room() is defined with today's values but not wired into toast_limit() or the toasts screen; 6.1 says the stub is "today's behaviour" and 4.2 gives the wiring to P2.
- **P0b:** The stage loop moved into view_stage(loc) uses `loc` where the old lines said `here`. It is the same room at every call and the screenshots are pixel-identical.
- **P0b:** person_choices adds `icon` in one loop at the end of the function, not at each place a dict is built. Same result.
- **P0b:** The Special Grade chip uses dark text on a flat gui.grade_sp until gui/grade_sheen.png exists, and light text on the sheen once it does (light text on the flat stand-in was unreadable). Checked with a scratch strip: the sheen pans.
- **P0b:** The hot ring stand-in is the existing seal picture (gui/seal_44.png) scaled, until P0c draws gui/hot_ring.png.
- **P0b:** icon_sample is not modal and closes itself under smoke_autoplay, like dev_panel. "Style sample" stays usable in explore mode (DEV_EXPLORE_OK).
- **P0b:** The hotspot validator checks the two lanes of R6 (toasts, banner) only, as 4.10 says; the arrival caption's area is not treated as a lane.
- **P0b:** AREAS rows carry bg="bg area_<key>", blurb="" and spots={}; the six bg area_* images are not defined yet (P1's task). Nothing reads `bg` until P1.
- **P0b:** board_take_reason / board_refusal return night_block_reason() or a short fallback ("Not today") so a refusal is never an empty string.
- **P0b:** The hover-label proof queues eight toasts, not four: four stay up for the whole span, where four alone would expire before 20 ticks.
- **P0c:** gen_gui.py's default run changed. It used to redraw every GUI picture with Pillow; Pillow is not installed on this Mac, and a different Pillow version could rewrite the owner's existing pictures as different bytes. A plain run now draws only the four phase-2 pictures, in pure Python; the phase-1 set is redrawn only with --all. The phase-1 code is the same text moved into a function (diffed against the original: blank lines only), but --all itself was not run because Pillow is missing.
- **P0c:** Sizes the plan does not give: hot_ring.png 96x96 (the size hot_layer shows it at), soft_box.png 96x96 with a 24 px feather for Frame(..., 24, 24), card_back.png 120x168 (the card size in 4.12). hot_ring is a soft rounded-square glow rather than a ring, because the 72 px button covers the middle of it.
- **P0c:** The icon workflow is one file per sheet (three files), so the owner can run sheet 1 alone first. Each sheet loads a blank 6x5 grid picture (icon_grid.png) so the cells come back where cut_icons.py expects them, and saves its two candidates as icons_sheet<n>_a / _b so the file name says which box it came from.
- **P0c:** What each icon should look like is a table (DRAW) inside make_icon_workflow.py; the names files hold names only, as the plan says. The tool stops if DRAW and ICONS disagree.
- **P0c:** cut_icons.py and make_icon_workflow.py take a few options the plan does not list: --dry, --only, --out, --names, and '-' in a names file to leave a cell out. cut_icons.py writes its preview to shots/art/ and installs nothing if a named cell is empty.
- **P0c:** layout_sheet.py takes --sidecar, --fg, --no-sidecar, --defaults and --out, and writes <name>__sidecar.png when --sidecar is given, so the two acceptance sheets do not overwrite each other. It also draws hot_<place> and area_<key> sheets with the validators' frames and the two lanes.
- **P0c:** make_bg_workflow.py always writes backgrounds.json into ~/Desktop/JJK Game images; I ran it twice and moved each result into phase2/ as areas.json and map_tokyo.json. It also copied its four style references into ~/ComfyUI-Shared/input, as it always does.
- **P0c:** tools/README.md was not updated with the new tools: it belongs to P8.
- **Review round 1:** tools/make_bg_workflow.py was on the plan's 'untouched in phase 2' list (7.2). It was edited for the review's major finding, and tools/bgs/style_aerial.txt was added. tools/make_relight_workflow.py imports INTERIORS, so it now treats library, utahime_office and gojo_office as rooms too.
- **Review round 1:** ui_icons.rpy gains ICON_SAMPLE, a name 6.1 does not list. The style sample's rows now show map, journal, menu, train, study, eat, sleep, talk, wait, mission, look, fish_cast; hang and pc_open are gone from the rows. The frame is 1290 wide with 90 px buttons instead of 1700 and 120.
- **Review round 1:** p2_contracts.rpy: the plan says 'unchanged means equal to the baseline'. Four comparisons are now hard only under SMOKE_P0_STRICT=1. sb_char is compared order-free in the default run. person_choices skips Night rows once night_exists().
- **Review round 1:** aa_zz_order.rpy registers a second inert hotspot (zz_tv in dorm_common); its header and the plan speak of two rows.
- **Review round 1:** tools/smoke/baseline_globals.txt, frozen at P0a, gained eight rows for phase-1 names the improved scanner now sees, with a comment saying so.
- **Review round 1:** hot_validate() reports more than 4.10 lists: sidecar points, a sidecar id nobody registered, a malformed sidecar. hot_spots_for() ignores a sidecar point that is not two numbers.
- **Review round 1:** check_content.py has a new flag, --i-am-p0a-or-p8; --write-baseline alone now exits 2 without writing.
- **Review round 1:** cut_icons.py's preview file name changed to icons_<names file>__<render>.png.
- **Review round 1:** The strict pixel evidence was taken against same-size screenshots of a scratch rebuild of the pre-phase-2 tree, not against the committed baseline_shots, because the window size on this Mac changed.
- **Review round 1:** art_batch_1.md was rewritten from scratch (the original was lost with the scratchpad) and now lives in ~/Desktop/JJK Game images/phase2/.
- **Review round 2:** tools/smoke/_lib.rpy (a phase-1 file wave 0 owns) changed behaviour: its three waits pass modal=False.
- **Review round 2:** ui_icons.rpy: hover_label picks 'top' for the style sample's icon-row keys; D10 says left when there is room. Everywhere else it is still left.
- **Review round 2:** tools/smoke/baseline_globals.txt, frozen at P0a, gained 15 more rows (ten phase-1 names) for names the improved scanner now sees, with a comment.
- **Review round 2:** check_content.py reports a new kind of action-returns finding: `Function` handed on without a call, anywhere in a game file.
- **Review round 2:** New folders in tools/smoke/ that the plan does not list: baseline_shots/1818x1022/ (two screenshots, 3.5 MB) and p8_patterns/ (two .txt patterns and a README).
- **Review round 2:** cut_icons.py has a new flag, --any-sheet, and refuses a render whose sheet number differs from the names file's.
- **Review round 2:** layout_sheet.py rejects more than the plan's sidecar description states: unknown top-level keys, slot keys outside "1" to "4", and a slot list whose length is not its key.
- **Review round 2:** smoke.sh refuses to run if the scratch game/cache ends up a link.
- **Review round 2:** p2_contracts.rpy's header gained one comment paragraph after its default and strict runs; no code changed after them.
- **Review round 2:** Carried from round 1: make_bg_workflow.py edited although on the untouched list; ICON_SAMPLE; SMOKE_P0_STRICT and SMOKE_P0_SHOTS; aa_zz_order.rpy's second inert hotspot; hot_validate's sidecar findings; --i-am-p0a-or-p8; cut_icons preview naming; art_batch_1.md living in ~/Desktop/JJK Game images/phase2/.
- **Review round 3:** explore.rpy: the review panel's footer text changed (one screen text line); the 6.3 hooks table does not list it. No protected statement moved.
- **Review round 3:** check_content.py reads every `;`-separated statement on a line for names; `except ... as NAME` stays unread by design (the finding asked for it to be read or documented; it is documented).
- **Review round 3:** p2_contracts.rpy: one check's condition changed (the `or True` line); the harness no longer references view_slot_rects.
- **Review round 3:** Carried from rounds 1 and 2: make_bg_workflow.py edited although on the untouched list, plus tools/bgs/style_aerial.txt; ICON_SAMPLE in ui_icons.rpy and the narrower style sample; hover_label's 'top' side for the sample's icon rows; SMOKE_P0_STRICT and SMOKE_P0_SHOTS; sb_char compared order-free and Night rows skipped once night_exists(); aa_zz_order.rpy's second inert hotspot; hot_validate's sidecar findings; baseline_globals.txt gained rows for phase-1 names the improved scanner sees; --i-am-p0a-or-p8; `Function` alias finding; cut_icons preview naming and --any-sheet; layout_sheet's stricter sidecar checks; smoke.sh refusing a linked scratch cache; _lib.rpy waits pass modal=False; new folders tools/smoke/baseline_shots/1818x1022/ and tools/smoke/p8_patterns/; art_batch_1.md living in ~/Desktop/JJK Game images/phase2/.

## Open after wave 0

- An unknown literal icon name in a screen is caught by nothing automatic; it rests on each package's own grep until P8 adds a rule.
- The harness branches for night_exists() True and toast_room() == (0, 0, 0), and the slot-independent hotspot checks against a changed slot table, are still unrun; no package code exists yet to trigger them.
- The committed 2666x1499 baseline_shots cannot be compared in this Mac's 1818x1022 window; the strict run needs SMOKE_P0_SHOTS pointed at the 1818x1022 folder.
- check_content does not read a plain `import x`, `except ... as NAME`, a one-line `if x: a = 1`, or names set through setattr/globals().
- The icon and background workflows have not been opened in ComfyUI. map_tokyo.json has no style reference.
- The credit-balance location in art_batch_1.md is from memory of ComfyUI, not checked in the app.
- gen_gui.py --all is still unrun (no Pillow on this Mac).
- journal("memories") still opens the Memories tab until P3; the Library stand-in is still the classroom picture; before roll call the journal's Next line reads 'Eat together at Bond 10' until P3.
- docs/PHASE2_DESIGN.md does not yet reflect the deviations of rounds 1 to 3; P8 owns the docs.

## Findings the fixers left unfixed, with their reasons

- **Round 1, not fixed:** spec minor: journal("memories") alias was not written (ui_journal.rpy) — No code change, as the finding asks. It is a hand-off: P3 maps "memories" to "people" in the commit that removes the JOURNAL_TABS row; P8 corrects 6.1's stub column.
- **Round 1, not fixed:** spec minor: label is hot_use(hot_id), 6.1 says hot_use(id) — Kept hot_id so the builtin id is not shadowed. Hand-off: P8 updates 6.1 and 4.10; packages call it positionally.
- **Round 1, not fixed:** spec minor: gen_gui.py --all path unverified; icon workflow not opened in ComfyUI — No code change, as the finding asks. Both stay open issues; the first drag-in of icons_sheet_1.json is the proof for the workflow.
- **Round 1, not fixed:** saves minor: view_sync_light() and view_before_person() are skipped once by a save parked just before them — No change in wave 0, as the finding asks. Hand-off to P5 and P8.
- **Round 1, not fixed:** saves minor: the only wave-0 save test trims the rollback log and saves from a fixture — Left for P8's p2_saves, as the finding asks. The reviewer's scratch harnesses (review_saves_r1) are gone with the scratchpad, so P8 writes them from the description in the finding.
- **Round 1, not fixed:** saves minor: docs/load_report_phase1.txt no longer matches the owner's saves line for line — Orchestrator item. Today's report (11 SAME, phase2 @ 7f40189 + these fixes) is in the scratch folder; compare status, not line numbers, until P8 writes docs/load_report_phase2.txt.
- **Round 2, not fixed:** oldgame minor: before roll call the journal's Next line skips ahead to 'Eat together at Bond 10' — No wave-0 code change (sb_events.rpy and ui_journal.rpy's People page are not P0's). The checkpoint A note carries the line, and P3's hand-off says to show 'After roll call' when rule_hangout_gate holds a person's next hangout.
- **Round 3, not fixed:** spec minor: frozen icon_sample and dev_panel use P2-owned styles (sb_action_button, sb_action_title, sb_action_hint, sb_hud_nav_button) — No code change, as the finding asks. Hand-off to P2: those four styles stay defined under the same names.
- **Round 3, not fixed:** spec minor: an unknown literal icon name in a screen passes lint silently (4.3 promises a VALIDATE line) — No wave-0 code change, as the finding asks; lint never runs a screen. Hand-off to every package (grep own file's icon("...") / icon_btn("...") names against ICONS) and to P8 (add a check_content rule or correct 4.3).
- **Round 3, not fixed:** spec minor: shots/layout/defaults.json is gitignored, so a new worktree has none until p2_contracts has run there — No code change, as the finding asks. Hand-off to P1, P5 and P6: run p2_contracts in the worktree before the first layout_sheet.py call.

---

# Hand-offs from wave 1

*Written 4 Oct 2026 from the wave 1 reports (P1, P2, P3, P4a, P4b), their review rounds, the trial merge and its integration fixes. Wave 2 (P5, P6, P7) and P8 read this before they start.*

## P1

**Hand-offs**
- Owner: the first room of the School Building is still named 'Classroom Building', so the marker's hover reads 'Classroom Building · Cafeteria · Infirmary · Library' and the pin plate says the same. If you want 'Classroom' on the map only, the edit is one line in map_place_name (game/ui_map.rpy): `if loc == "classroom": return "Classroom"`. LOCATIONS stays as it is.
- Owner: if an open area should be kept across a save and load, that needs a new store `default` and a plan change; today a load returns to the six areas (one more click).
- P2: once toast_room() returns (0, 0, 0) over the map and objective_toast draws nothing off the place view, p2_map's toast NOTE becomes a measured PASS with no edit. Until then toasts cover the Staff Building marker and the banner covers the Mountain marker / Rooftop pin.
- P2: the map's top row leaves x 1560 to 1684 for the Campus/Tokyo switch. Your Map/Journal/Menu icons at x 1668 to 1880 would overlap it by 16 px if all three showed on the map; keep on_map hiding Map and Journal.
- P2: add the AMBIENT row ("megumi", "library"): ("three books deep", "serious") as planned; until then person_now('megumi') in the Library gives the fallback caption.
- P3: person_now(who) keys are place, name, doing, reachable, hidden, with_me. Show the go button only when reachable is True and return ("go", v["place"]). For hidden, place is None and name is "Somewhere I can't go right now"; for the companion name is "With me".
- P4b: the map calls night_marks().get(area key) for the level-1 moon and night_out_ok(key) for the district moon and the district_night button (Shibuya/Shinjuku, Evening or Night, district open, and ok or a reason given). Return ('night', key) goes to sb_travel's existing branch.
- P8: hover labels on the Tokyo layer cover a neighbour while hovered (Shibuya's over Kawasaki's name and lock; the closed-Tokyo label over the Campus button). Either let hover_label (frozen ui_icons.rpy) take the top or bottom side for keys starting district_, or move DISTRICT_POS["kawasaki"] in sb_tokyo.rpy about 200 px right, to roughly (1320, 820).
- P8: tools/smoke/phase1_all.rpy zzp_map() logs 'no sensitive Go button' on every map visit because level 1 has no pins. Exact edit: before `vals = ...` in zzp_map add `sc = renpy.get_screen("sb_map")` / `if zzp.map_target and sc is not None and sc.scope.get("zone") != area_of(zzp.map_target): sc.scope["zone"] = area_of(zzp.map_target); renpy.restart_interaction(); return None`.
- P8: p2_saves must park on the real `call screen sb_map` with an area opened by pressing area_<key> (rollback log untrimmed), and expect zone None / level 1 after the load. It should also still park an old-tree save on `call screen sb_map` (p8_patterns/zz_old_park), since the owner's current saves no longer rest there.
- P8: docs to update: 4.1 (Back is not an icon_btn; Stay here on every level; hover lists who is there; district pictures zoom in; faces go left of a pin with x under 700; a closed district by argument shows level 1; a load returns to level 1), 6.1 (person_now's hidden row has place None; helpers world_area_crop/standin/bg, map_validate, MAP_FACES_LEFT_X), 7.2 (game/layout/area_*.json exist for all six areas).
- P8: a harness that presses a SetScreenVariable button from a timer on another screen must push sb_map as the current screen first (see zz_run_on_map in wp1_world.rpy and zz_on_map in p2_map.rpy).

**Where it departs from the plan**
- Back button is my own button (id map_back) rather than icon_btn('back', words='always'), so it can read 'Jujutsu High' / 'Tokyo'.
- 'Stay here' is on every level, not only level 1.
- A pin's 'disc' is a 72 px square tile; there is no round asset.
- A pin's hover line also lists who is there and says 'I'm here.' on my own room.
- My own room's pin stays hoverable (NullAction) instead of insensitive.
- person_now returns place=None for someone behind a locked door; the companion's doing is 'tagging along'.
- The area stand-in helpers live in sb_world.rpy; bg_placeholders.rpy only defines the six images from them.
- Pin rules are a separate validator map_validate in ui_map.rpy; _validate_world gained three AREAS checks.
- The zoom-in is also used for a district's picture.
- Marker names shrink to fit when too wide; so do pin name plates now (round 1), instead of a flat size.
- Six real sidecars game/layout/area_<key>.json exist; the plan's table stays as the code defaults.
- District pins show no name plate at rest, all with the place_later icon.
- Phase-1 map styles no longer used are left defined.
- New in round 1: a pin left of x 700 draws its faces on the left of the tile (the plan puts faces on the right).
- New in round 1: a closed district passed as area= opens the Tokyo layer on level 1 rather than that district's view.
- A save made through the real `call screen sb_map` with an area or district open reloads on level 1 (Ren'Py re-runs the call with a fresh scope). p2_map's save check covers a shown map only.

**Open**
- Toasts and the objective banner draw over the map until P2 is merged (P2's lane work).
- Hover labels on the Tokyo layer cover a neighbouring marker while hovered; needs frozen ui_icons.rpy or sb_tokyo.rpy (P8 hand-off).
- The room name 'Classroom Building' under the area 'School Building' waits for the owner's word.
- A save made with an area open reloads on the six areas; harmless, one more click.
- Level-1 markers for empty areas show two blank rows.
- The Tokyo district views still use phase 1's tinted stand-in pictures, and their 'Later build' pins sit on arbitrary spots.
- Pin positions were placed by eye; the Rooftop pin sits on the tower's upper floors because the roof is above the allowed frame.
- With icon pictures missing, the Campus/Tokyo switch grows about 16 px taller (stand-in path only).

**Findings left unfixed, with reasons**
- (not fixed) spec: the room 'Classroom Building' under the area 'School Building' — Left as the reviewer advised: LOCATIONS is unchanged (wp1_world and the journal pin the name) and the plan renames only the area. Put to the owner in the hand-offs with the one-line edit in map_place_name.
- (not fixed) spec: on Tokyo, Shibuya's hover label covers the Kawasaki marker — Not P1's files: the side is chosen in frozen ui_icons.rpy and DISTRICT_POS is in sb_tokyo.rpy. Hand-off to P8 with both options.

## P2

**Hand-offs**
- P1: keep `use sb_hud(on_map=True)` in sb_map. The HUD's top row holds the date and up to three 48 px chips from x 40 to about x 560, y 26 to 80, plus Menu at x 1816 to 1880; keep markers and pins out of it.
- P1: toasts and the objective banner do not draw over sb_map (toast_room() is (0,0,0)), so a zz_worst('sb_map') screenshot shows neither; that is correct.
- P3: the person view no longer shows the name, role line, caption, bond and affection bars, thread title and pips, or the 'Closer' hint. role_line(who), unlock_line(who) and person_thread(who) stay defined in sb_screens.rpy for the journal page.
- P3: the two affection notes that were only on the person card are gone from the game: '([_a]/[_cap] · I'd have to know them better)' and '([_a]/[_cap] · the rest is up to me)'. Put them on the person's page if they should survive.
- P3: ambient_of(who, loc) follows the story through AMBIENT_STORY; still a 2-tuple. Toasts wait while the journal is up and show when it closes.
- P4a: toasts wait over the armory, board_screen, board_partner and grade_card. 'in my hand' and 'back on the rack' toasts show only after the armory closes; if a tool change needs feedback on the screen itself, draw it there.
- P4b: the moon chip shows whenever night_tag() is non-empty; its hover text is night_tag(), plus ' — no missions or training today' when night_can_work() is False. Return just 'Worn out' or 'Rough morning' from night_tag().
- P4b: the column draws rail_actions(here) in order, so the row night_filter_actions puts in Wait's place (id night_bed) is drawn where Wait was. Missions in the column and on a person are hidden by night_can_work() and night_allows('mission:' + mid, cost). The 'Too late' reason from activity_state is not shown on the person view.
- P4b: market_screen is tagged sandbox, so toasts wait over it. night_carry_home and the night labels are scenes, so toasts draw there.
- P5 (wave 2, owns wp7_ui.rpy and p2_hud.rpy then): give the stage's sprite buttons and name tags tuple tooltips with keys unique on sb_place, for example (caption, 'stage_' + who) and (caption, 'tag_' + who). Then in tools/smoke/p2_hud.rpy section 2 replace the check 'sb_place: the only buttons without a hover label are the stage's own' and its NOTE with `check(not _zz_bare, ...)`.
- P5: the icon column occupies x 1808 to 1880 (and x 1726 to 1798 with more than eight actions) from y 360 or 430 down to 1040; the stage must stay left of x 1700 (p2_hud asserts it). The person card is at x 1180 to 1820 from y 250 (RAIL_CARD_Y) to at most y 1040; view_focus should keep ending at xcenter 520. wp7_ui's name-plate checks are yours to change.
- P5: the '+N' chip is now at RAIL_MORE_POS = (1400, 1040), bottom-anchored (sb_screens.rpy, sb_place; vbox id rail_more). p2_hud section 2 checks its names meet no view_slot_rects(here, n) rectangle; if the stage slots move right of x 1358, move the chip or that check fails. A two-line name plate (Yuji's 'halfway through an enormous bowl') still runs over 'Review tools' at the bottom left; that is view_stage.rpy.
- P5: sb_char is given the person's AMBIENT_STORY expression only through view_stage (ambient_of); view_focus uses person_image(who) as before.
- P5 / P8: p2_hud.rpy's last section saves and loads inside the real loop (ZZ_HUD_LOAD, zz_hud_load_step, zz_hud_sweep); it must stay last, because it calls finish() from a timer. Any new section goes before it, and must not leave an open file in a store variable across statements (the save would fail to pickle the rollback log). The reviewer's wider driver (rollback, a save on the person view) is at scratchpad p2_w1/P2/review_saves_r2/zzr_delay.rpy if a separate harness is wanted.
- P6 / P7: a room may hold at most 15 column tiles at any period (missions + actions + Wait + 'Let them go'); p2_hud section 3 fails a room that needs a third column, with pictures or with words (12 with words). At run time, tiles whose words would need a third column are drawn without words (rail_layout). A registered place action with no ICON_FOR row draws the generic `act` icon; while words show, the tile's word is the action's label, so keep labels short (about nine letters a line). The column leaves out anything hot_covers(loc) returns. A tile's id is 'rail_' + action id.
- P6: 'Study together' is offered in the Library (the activity's loc gained 'library').
- P8: game/ui_icons.rpy, screen hover_label, after the existing block that sets `_hover_side = "top"` for the sample keys, add: `elif isinstance(_hover_tip, tuple) and len(_hover_tip) > 1 and str(_hover_tip[1]).startswith(("hud_map", "hud_journal", "hud_menu", "hud_chip_")):` then `$ _hover_side = "bottom"`. Today a corner icon's label covers its neighbour (Journal's covers Map, Menu's covers Journal, the moon chip's covers the stamina chip). Not run by me. An edge-column tile's label also covers the inner column's tile on the same row when there are two columns.
- P8: game/sb_hotspots.rpy line 46, HOT_LANES: change (1330, 92, 460, 258) to (1330, 92, 460, 330). Four two-line toasts over the place view end near y 416. Correct R6's 'y 92 to 350' in the plan to match. The '+N' chip now stands at x 1400 to about 1500, y 950 to 1040, inside HOT_BOUNDS (x to 1700, y to 1000): consider keeping hotspots out of that corner in rooms that can hold five people.
- P8: add a row to 7.3's table: 'P2 | P0 | the sb_place half of the every-button-has-a-tooltip bullet waits for P5's stage tooltips'.
- P8: docs to update in PHASE2_DESIGN.md: 4.6 (the card starts at y 250, not 190); 4.4 (the '+N' chip at (1400, 1040); item 9: the tiles are rail_btn; a second column stops at y 430 and holds seven; two columns at most, and the words are dropped rather than open a third; a tile's word is the action's name); 4.2's toast_room order (grade card, blackout, the menu context, a `menu` screen, then the sandbox names; journal is tagged menu); 4.3 (the banner's slide runs on show and appear; check_objective hides before it shows); 6.1 (new P2 names: toast_hold, hud_banner_ok, hud_chips, TOAST_LANE, HUD_BANNER_X, HUD_BANNER_W, rail_rows, rail_columns, rail_layout, rail_height, rail_word, rail_tip, rail_missions, rail_chip, rail_story_ok, rail_story_caption, RAIL_COLUMNS, RAIL_CARD_Y, RAIL_MORE_POS, screen rail_btn); D19b's rows as shipped.
- P8: tools/smoke/_lib.rpy, zz_worst: it shows objective_toast directly, and the banner waits for the arrival caption, so a zz_worst screenshot taken within about 3 s of arriving at a new (day, period, place) shows no banner. p2_hud ages the caption first (`arrival_caption(); ARRIVAL[1] -= 10`); consider doing that inside zz_worst.
- P8: p2_contracts.rpy reports 131 PASS, with the 20-tick check as a NOTE. tools/smoke/p2_hud.rpy now reports 108 PASS and takes about 85 s; wp7_ui reports 142.
- P8: the renpy.hide_screen("objective_toast") line in check_objective() (ui_hud.rpy) is not covered by any harness: p2_hud passes without it, because the `appear` handler on objective_slide already makes a reloaded banner wait. Keep it or drop it; it is harmless.
- P8 / phase 4: AMBIENT_STORY has no row keyed on saw_the_ridge_veil because that flag is set in the prologue tour; a 'Gojo at the ridge' story caption needs a later flag. A grade condition on Shoko or Ijichi is a validator finding.

**Where it departs from the plan**
- New this round: rail_layout() drops the column's words when the worded layout would need a third column. The plan has no such rule; it keeps the stage (x 40 to 1700) clear.
- New this round: the '+N' chip is at (1400, 1040), bottom-anchored (RAIL_MORE_POS), not (1300, 900). The reviewer suggested x 1560; 1400 keeps it clear of Wait's hover label as well.
- New this round: the load check is the last section of p2_hud.rpy, not a separate p2_hud_load.rpy, because a new harness file is outside P2's owned list. It removes the harness's own _zz_ scratch variables from the store before saving, and deletes the baseline file handle right after reading it, so the save can be written.
- The person card starts at y 250, not the plan's 190 (4.6), so that two three-line toasts end above it.
- A tile's word, while words show, is the action's own name rather than the icon's word; missions keep 'Mission'.
- 'Nobody here right now.' is not shown in the dorm.
- check_objective() hides the banner screen before showing it.
- The column's tiles are a new screen, rail_btn (sb_screens.rpy), not icon_btn: a fixed 72x72 tile with a 50 px icon and the diamonds under it.
- A second column stops at y 430, not 360, because four two-line toasts end near y 416; it holds seven tiles, the edge column eight. At most two columns (RAIL_COLUMNS).
- With two columns the last rows (Wait, 'Let them go') stay at the foot of the edge column and the first rows overflow to the left.
- toast_room() tests the grade card, the blackout, the game menu's context and a `menu` screen before the `sandbox` names; every row's value is as 4.2's table says.
- Added toast_hold(), a start-of-interaction callback that stops every toast clock where toasts wait.
- The objective banner is wrapped in `showif hud_banner_ok()`; its slide therefore runs on `show` and `appear`.
- The status chips never show their word under the icon; the stamina chip is hidden in explore mode.
- The moon chip's hover text is night_tag(), plus ' — no missions or training today' when night_can_work() is False.
- The romance '♡ ' prefix on a choice's label is gone; the heart icon and rose colour carry it.
- Review tools and the overflow chip's names gained tooltips and ids.
- AMBIENT_STORY has twelve rows; none is keyed on saw_the_ridge_veil. Its helpers are named rail_story_ok and rail_story_caption.
- The 'Day 100 · Wednesday' check uses day 101, the first Wednesday from day 100.
- wp7_ui: checks for the name, role line, Closer hint and affection meter on the person card assert they are absent.

**Open**
- A corner icon's hover label covers the button beside it (Journal's covers Map, Menu's covers Journal, the moon chip's covers the stamina chip). The fix is in frozen ui_icons.rpy and is handed to P8; the owner will see it at checkpoint B when hovering.
- The stage's sprites and name tags on the place view have no hover label until P5 adds them, so the 'every button has a tooltip' line is not fully met on sb_place.
- The load check in p2_hud does not cover the hide_screen line added to check_objective() in round 1: with that line removed the harness still passes. It does catch the banner drawing at once after a load if the `appear` handler is lost. It runs an in-process load only; a load from the main menu in a fresh process is covered only by load_all_saves landing SAME, which does not read the banner.
- More than fifteen tiles in one room would still open a third column on the stage; only p2_hud's sweep stops that. No shipped room has more than four.
- When the column drops its words (many long-named tiles with words on), tiles that share the generic icon can only be told apart by hovering.
- Four two-line toasts over the place view run to about y 416, past the plan's lane bottom of 350. P2's column allows for it, but the frozen hotspot validator (HOT_LANES) still uses 350 until P8 changes it.
- The '+N' chip's new corner (x 1400 to about 1500, y 950 to 1040) is inside the area the hotspot validator allows; a hotspot placed there in a five-person room would sit under it.
- A long caption on a name plate ('halfway through an enormous bowl') wraps to two lines and runs over 'Review tools'; that is view_stage.rpy, P5's.
- 'Review tools' has a hover label that repeats its own words.
- combat_screen, board_partner and market_screen are checked for toast_room() by tag only, not rendered with toasts up.
- The moon chip, 'Go to bed' and Night mission filtering are untested against a real night rule until P4b merges.

**Findings left unfixed, with reasons**
- (not fixed) play: a corner icon's hover label covers the icon beside it (carried over) — No P2 edit is possible: the side is chosen in frozen game/ui_icons.rpy, screen hover_label. The exact edit stays in the P8 hand-off, and it is in the open issues and the owner notes.

## P3

**Hand-offs**
- P2: toast_room() must return (0, 0, 0) while the journal is up, and objective_toast must hide there. The journal is the screen tagged menu (renpy.get_screen('menu') is the journal), which p2_journal.rpy hard-checks. Until P2 is merged, toasts and the banner draw over every journal view. No edit requested in P2's files.
- P2: keep unlock_line(who) defined; the person page's Closer line calls it and counts its words toward the page's 70.
- P2: keep AMBIENT_STORY captions to about six words. They feed person_now's 'doing'; the page clips the Right now line at 72 characters and counts its words. A reviewer's sweep showed a 15-word caption makes one page fold its oldest story lines into '2 earlier lines' (Maki, stage 2, low bond).
- P1: the journal prints person_now(who)['name'] and ['doing'] joined by ' — ' on the page, and 'name' alone on the card ('Elsewhere' when hidden). 'Go there' returns ('go', place) only when reachable is True, place is set, with_me is False and place != here. While place is set and hidden is False (or with_me is True), 'Usually' is on hover only; otherwise the first usual place is printed and the full list is on hover. On a day Gojo is in, 'In his office today.' is printed only when person_now gives him a place. Keep face_chip(who, size) in ui_map.rpy.
- P4a: item_requirements(id) rows (str, bool) are drawn as tick/cross chips by screen jr_req_chips in the picker rows, the Equipment panels and the Inventory panel. The tool picker asks can_hold(id): a refused row is insensitive and shows the reason.
- P4a and P8 (D28 risk): jr_wear (phase 1 code, ui_journal.rpy) takes off every talisman after the chosen slot and re-equips them through equip_talisman. Once can_wear refuses on an unmet checklist, a later talisman worn from an old save could silently come off when an earlier slot is changed. After the merge add a check: wear A in slot 1 and B in slot 2, patch item_requirements_met(B) to False, change slot 1 through jr_wear, assert B is still worn. If it fails, jr_wear must restore the later talismans through a path that bypasses the checklist.
- P6: pc_leads() rows (page, note) print as note + ' — my computer'; pc_records() titles are listed as given; fish_records() rows print as 'Name — 42 cm' or 'Name — not caught yet'.
- P7: cards_records()['today'] prints as 'Won today: ¥n' ('Lost today' when negative); 0 hides the section.
- P8: on the merged tree, p2_journal.rpy's line 'zz_worst("journal"): no toast is drawn over the journal' must come out as a PASS, not the NOTE. If it is still a NOTE, P2's lanes are not reaching the journal. The objective banner over the journal is not checked by this harness; check it by eye in worst_journal.png. Add P3's row to plan 7.3's table as waiting for P2.
- P8: run p2_journal.rpy with SMOKE_TIMEOUT=300 and write that into the standing-set instructions. It takes about 145 s of the default 180 s here even after the sweep was trimmed.
- P8: once P1's real person_now and P2's AMBIENT_STORY are in, re-run the budget sweep and read the NOTE 'pages where the oldest lines are folded into one row'. If it is not (0, []), shorten the caption concerned or ask the owner to raise JR_PAGE_WORDS. The wordiest page is exactly 70 today; a page whose fixed text alone passes 70 would fail the check.
- P8 (frozen tools/smoke/baseline_globals.txt, line 432): when the baseline is regenerated on the merged tree, drop the row 'def screen jr_memories_tab game/ui_journal.rpy'; P3 removed that screen.
- P8 (p2_saves): nothing in p2_journal.rpy calls renpy.save / renpy.load from inside the journal. Reuse the reviewer's harness in the scratch folder, p2_w1/P3/review_saves_r2/v2/zz_p3_saves.rpy (it adds the hidden-person, forced-fold and long-name views to round 1's pattern). The scratch folder is not permanent: copy the file into the tree when building p2_saves.
- P8 (hover labels, frozen game/ui_icons.rpy): hover_label's left-first rule puts a card's label over the card to its left, the Strength label over the name, the Usually label over the Strength block, a story row's label over the sprite, and the first not-met chip's label over the rail. Let hover_label take a side from the tooltip key, as it does for the sample_ keys: open 'jr_now', 'jr_stage_' and 'jr_chapter_' below their row, and 'jr_card_', 'jr_unmet_' and 'jr_strength' top or bottom.
- P8 (docs, PHASE2_DESIGN.md): 4.7 should record short names for story lines that don't fit, with the line on hover, whole lines always the newest run, and the fold as last resort; 'Usually' on hover while the person can be seen and first place only when not; 'In his office today.' alone, and only when he has a place; the heart note on hover; 'Promoted Day n'; the Strength block; the lighter Right now panel; a locked mission as the NEXT row; 'More time together' after a resolved thread; short names and 'Elsewhere' on cards; Leads above the sub-tab chips; 352x300 slot cards; jr_stats_tab(js=None). 4.0 should say the person-page budget is measured on the default pane (Their story). 3.1 says 11 stage lines, 15 were reworded, and THREADS gained 'short' and the title 'Taking My Measure' (record the owner's ruling on the title).
- P8: the lint command in the task text ends in 'lint .', which makes Ren'Py try to write its report to '.' and raise IsADirectoryError; drop the dot.
- Wave 2 (P5, P6, P7): new store names in ui_journal.rpy all carry jr_ / JR_. jr_people_cards() is the list the grid reads; journal_state() has psub, ssub, msub2, and sel accepts 'me'.

**Where it departs from the plan**
- New this round: once a learned story line takes its short name, every older line takes its short name too, even if it would have fitted. Whole lines are always the newest run.
- New this round: 'In his office today.' is printed only mid-scene or when person_now gives Gojo a place; beside 'Off campus' the page prints 'Usually: <first place> …' instead.
- New this round: when the Right now block holds three lines, the place line is size 20, not 22; the block's top padding is 4, not 7.
- New this round: the harness's budget sweep measures 214 pages; the stub and with-me views run at stages -1 and 3 only. The run still takes about 145 s of the default 180 s.
- Round 1: a learned story line that doesn't fit prints its short name from THREADS['short'] (one or two words, no ellipsis), with the thread title and the whole line as its hover label. 4.7 says each learned stage line is a done row; each still is.
- Round 1: if even the short names don't fit, the oldest learned lines fold into one row ('3 earlier lines') whose hover label lists them whole. It occurred on none of the pages measured here.
- Round 1: when I can't see where someone is, 'Usually:' prints only the first usual place and ' …'; the full list is the Right now block's hover label. Mid-scene the full list is printed.
- Round 1: the Right now line is clipped at 72 characters.
- Round 1: a start-trigger mission with no place of its own takes its where from jr_story_where(who).
- Round 1: a mission still locked or waiting becomes the NEXT row when nothing else is left; a mission closed by Arc Two never does.
- Round 1: a step row is titled 'More time together' once the person's thread is resolved.
- Round 1: the thread title is 'Taking My Measure' (was 'Taking Your Measure'), changed without the owner's say.
- Round 1: THREADS rows carry a new init-data key, short=[...]. Nothing saved changes.
- Round 1: the Me page's name is drawn at size 40 down to 28 and then clipped to fit 600 px; it reads '1st year'.
- Round 1: Sana's empty page reads 'Nothing yet. What I remember of her ends up here.'
- Round 1: new names in ui_journal.rpy: JR_FOLD_WORDS, jr_mission_where, jr_stage_short, jr_story_brief, jr_usual_first, jr_text_width, jr_fit_name. From the retry: JR_PAGE_WORDS, JR_LEAD_WORDS, JR_LEAD_MIN, JR_TAG_RE, jr_is_word, jr_word_count, jr_lead, jr_story_sub, jr_story_fit, screen jr_story_chapter, style jr_plain_button.
- From the retry: the heart bar's note is its hover label; the promotions line reads 'Promoted Day n'; a closed mission row may move its small line to hover when the page is over budget before story lines.
- From the retry: jr_mem_thumb returns a Crop around the Transform, so the thumbnail is exactly 280x158.
- Strength (reserve, control, output) is kept on the person page as a small block over the sprite, with the blurb and note as its hover label.
- The Right now panel uses the lighter panel background, not panel_dark, because the page itself is panel_dark.
- Bond rank and number sit under the 620 px bar, not beside it.
- Cards use short names ('Gojo'); a person in a room I can't enter reads 'Elsewhere' on the card; mid-scene the card has no place line.
- A card's hover label is jr_next on two lines, through jr_card_tip.
- The go button is also hidden when the person is with me or already where I stand.
- The rail header is a fixed 44 px box so the first tab sits at y 148.
- 15 stage lines said 'you', not the plan's 11; all 15 are reworded.
- jr_story_rows: the heading is always the first row; an unlearned stage is never listed; rows carry extra 'id' and 'short' keys; Sana's list is empty.
- Internal screens changed: jr_stats_tab gained an optional js parameter; jr_story, jr_character and jr_board_view gained an optional height; jr_memories_tab is removed. No screen listed in 4.0 changed.
- Leads sit above the sub-tab chips on every Missions sub-tab, show at most three with 'and n more', and ' — my computer' is appended unless the note already mentions the computer.
- Talisman slot cards are 352x300 so the checklist fits.
- The People viewport's scrollbar sits in the margin right of the body (x 1888).
- The journal calls face_chip (ui_map.rpy) and unlock_line (sb_screens.rpy), and reads EVENTS, rule_hangout_gate and RULE_HANGOUT_AFTER for the 'after roll call' wording.
- Records wording is mine: 'PAGES I'VE READ', 'THE RECORD BOOK', 'AT THE CARD TABLE', with 'Lost today' for a negative figure.
- Harness: the save check pickles the screen scope on every view instead of calling renpy.save.

**Open**
- Toasts and the objective banner draw over the journal until P2's toast_room() and banner rule are merged; the acceptance line cannot be a PASS in P3's worktree alone.
- The page budget has no headroom: the wordiest measured page is exactly 70 (Yuji, story finished, with me). On tight pages the story shows mostly as short names and reads in full only on hover; with the new ordering rule Maki's hidden page shows four short names on a half-empty page. Owner decision: keep 70, or raise JR_PAGE_WORDS (about 95 would print every line whole; the harness's literal 70 changes with it).
- The thread title was changed to 'Taking My Measure' without the owner's say; reverting is one word in game/sb_threads.rpy.
- A finished story still shows the green RESOLVED chip above a NEXT row and 'n more chapters in a later build'. Left for the owner.
- The Memories pane of a person's page (up to about 115 words) and the Me page are not held to 70; the budget is checked on the default story pane.
- Hover labels open to the left and can cover the neighbouring card, the name, the Strength block, the sprite or the rail; the placement rule is in a frozen file.
- jr_wear may take off a later talisman once P4a's checklist can refuse it (D28); untestable until the merge.
- A long person_now caption (about 15 words) can make a page fold its oldest story lines into one row; this depends on P2's captions.
- With P1's stub every card and page reads 'Off campus' and no go button shows; the go path and the Usually-on-hover path are tested with person_now patched.
- The package harness runs at about 145 s of its 180 s limit; the sweep trim barely helped.
- tools/smoke/baseline_globals.txt (frozen) still lists the removed screen jr_memories_tab; harmless until regenerated.

**Findings left unfixed, with reasons**
- (not fixed) spec: Gojo's thread title changed to 'Taking My Measure' without the owner's say (sb_threads.rpy 76) — No code change, as the reviewer asks. It stays in ownerNotes for checkpoint B. Reverting is title="Taking Your Measure" plus dropping the titles from the you/your check in p2_journal.rpy.
- (not fixed) spec: the 'n earlier lines' fold can occur with a 15-word person_now caption (Maki, stage 2, low bond) — No P3 code change, as the reviewer asks; the fold works as designed and stays within 70. The hand-offs to P2 (captions of about six words) and P8 (read the fold NOTE on the merged tree) are tightened. In this tree's sweep the fold still occurs on 0 of 214 pages.
- (not fixed) spec: the package harness takes about 149 s of the default 180 s — I applied the reviewer's trim (stub and with-me views at stages -1 and 3 only; 214 pages, was 262), but the run only dropped to about 145 s wall, so the sweep is not where most of the time goes. Handed to P8: run p2_journal.rpy with SMOKE_TIMEOUT=300.
- (not fixed) saves: baseline_globals.txt still lists the removed screen jr_memories_tab — The file is frozen for P3. Handed to P8: drop the row when the baseline is regenerated on the merged tree. check_content is clean and the 11 saves load SAME.
- (not fixed) saves: the committed harness never calls renpy.save / renpy.load from inside the journal — Carried over; handed to P8 for p2_saves, now pointing at the round 2 scratch harness (review_saves_r2/v2/zz_p3_saves.rpy).
- (not fixed) play: hover labels open to the left over the Strength block, the sprite and the rail — Placement is hover_label's rule in frozen game/ui_icons.rpy. Handed to P8 with the keys to open below their row (jr_now, jr_stage_, jr_chapter_, plus round 1's jr_card_, jr_unmet_, jr_strength).
- (not fixed) play: the harness took 148.7 s of 180 s — Same as the spec finding: the sweep was trimmed but the run is still about 145 s. P8 runs it with SMOKE_TIMEOUT=300.
- (not fixed) play: toasts and the objective banner still draw over the journal — No P3 edit is possible: toast_room() is in P2's game/ui_hud.rpy. The journal's half is hard-checked and passes. P8 must see the line as a PASS on the merged tree.
- (not fixed) story: a finished story shows RESOLVED, a NEXT row and 'more chapters in a later build' together — Left for the owner at checkpoint B, as the reviewer allows. The suggested 'So far' chip adds a word to a page that sits at exactly 70 and reads oddly beside a title; no rule is broken as it stands.
- (not fixed) story: thread title 'Taking My Measure' changed without the owner's say — No code change, as the reviewer asks; kept in ownerNotes for checkpoint B.

## P4a

**Hand-offs**
- P2: in my worktree the worst-case toasts and the objective banner still draw over the armory, board_screen, board_partner and combat_screen (the unwired toast_room() stub). After your merge, re-run tools/smoke/p2_gear.rpy and look at worst_armory.png and worst_board_screen.png: R6 says no toast and no banner there (toasts stay allowed over combat_screen, the banner does not).
- P3: item_requirements(id) returns [(line, met)]; met lines read 'Grade 1' / 'Output 50', unmet stat lines read 'Control 80 · I have 62'. Draw the tick or cross yourself (the armory uses ✓ / ✗ in JR_SYMBOL_FONT, paper when met, gui.seal when not). It returns [] for a talisman with no row, so draw no checklist row for those.
- P3 (required before the next checkpoint; otherwise P8 at integration), ui_journal.rpy jr_pick_options, the tool loop: replace `out.append((iid, iid != cur, "In my hand" if iid == cur else ""))` with `ok, why = (False, "In my hand") if iid == cur else can_hold(iid)` then `out.append((iid, ok, why or ""))`. Without it, a tool I own but cannot hold (Playful Cloud below Grade 2 / Output 50) shows as pickable and jr_hold silently does nothing.
- P3 / P8 (required), ui_journal.rpy jr_pick_options, the talisman loop: after `if not ok and cur and str(why).startswith("No free slot"): ok, why = True, ""` add `why2 = item_unmet_reason(iid)` and `if ok and why2: ok, why = False, why2`. can_wear tests the slots before the checklist, so when replacing a full slot a talisman with an unmet checklist would otherwise look pickable and jr_wear would silently do nothing.
- P3 / P8 (required, D28), ui_journal.rpy jr_wear, the put-back loop at the end: change `equip_talisman(x)` to `item_wear_again(x)`. item_wear_again(id) is in sb_items.rpy: it wears the talisman without asking its checklist (every other test of can_wear applies) and returns True if it is worn afterwards. Leave the first `equip_talisman(iid)` for the new talisman as it is. tools/smoke/wp8_journal.rpy swaps in its own equip_talisman shim, so it needs a matching `store.item_wear_again = zzj_equip_talisman` (and to restore it) or its jr_wear checks will call the real function.
- P4b: ITEM_REQS is a plain dict filled at init -1 in sb_items.rpy; `ITEM_REQS.update({...})` from sb_market.rpy works as planned and item_validate_reqs covers your rows. Market rows can show a checklist with item_requirements(id); can_wear already applies your rows once they are in the table. A stat name must be control, output or insight: any other name reads '?' and blocks the item.
- P8: write the deferred 7.3 line (put a market talisman on through the checklist) against can_wear: the reason for an unmet stat is the line itself, for an unmet grade it is 'Needs <grade name>' from can_wear's own earlier grade test.
- P8, p2_saves, the P4a part: build a driver screen that calls renpy.save / renpy.load / renpy.rollback from inside `call screen armory`, `board_screen`, `board_partner`, `combat_screen` and the grade card's pause, and compares the statement name, call depth, equipped_tool, equipped_talismans and inventory before and after. The reviewer's scratch version passed but its folder does not outlive the session.
- P8: docs to correct in PHASE2_DESIGN.md: 4.8's combat-header row is `grade_chip(cb.get("grade"), 16, text=<Ungraded when None>)`; 4.9 (the panel ends near y 950; all five tools show a checklist, two of them the grade alone, ticked once owned; an unmet grade reads 'Needs Grade 2' in can_hold / can_wear; a sixth rack tool needs the rows in a viewport, ysize about 780, mousewheel True, rather than tighter rows); 6.1 may list item_first_unmet, item_unmet_reason, item_wear_check, item_wear_again and armory_checklist; PLAYTEST.md should say Playful Cloud no longer jumps into an empty hand below Grade 2 / Output 50.
- P8: the review tools' 'one of every item' now grants tools and Grade 1 talismans the player cannot hold or wear until the checklist is met; that is the intended gate, but the checkpoint note for the owner should mention it. A tool held under D28 that is put down for another (Take at the racks, then Return) does not come back into the hand by itself.
- Phase 4 (Arc Two): the Inverted Spear's ITEMS `sealed` field is decided before its checklist, so with all four lines met the armory row still reads 'Sealed — Arc Two'. When Arc Two is built, clear the spear's `sealed` field or let armory_tools' arcii state and can_hold's sealed test yield when arc >= 2.

**Where it departs from the plan**
- can_hold / can_wear word an unmet GRADE line as 'Needs Grade 2', not the bare checklist line 'Grade 2'. Every other kind is the line verbatim. One function, item_unmet_reason, if the owner wants it changed.
- The armory draws a checklist under all five tools. Slaughter Demon and Nunchaku have no ITEM_REQS row, so the armory shows their grade as a one-line checklist through armory_checklist(id); that line is a tick once I own the tool (round 1). item_requirements() stays [] for an item with no row.
- Armory layout: the panel ends near y 950 (plan said near 900); panel ypos 36 to 30, header 84 to 76, row padding 12 to 7, row spacing 10 to 5, name 30 to 27 px, description 20 to 19 px.
- New names the plan does not list, all carrying their file's prefix: item_req_line, item_first_unmet, item_unmet_reason, ITEM_ARC_NAMES, armory_checklist, screen armory_req, styles armory_req_frame and armory_req_text; round 1 adds item_wear_check(id, checklist=True) and item_wear_again(id).
- Round 1: the reviewer's fix was `equip_talisman(id, again=False)`. I added item_wear_again(id) instead, because the frozen wp0_stubs.rpy pins equip_talisman's signature as '(id)'.
- The grade chip on the board is the common chip instead of the old display-heavy one; style board_chip_text stays defined but unused.
- The combat header passes the screen variable _grade as the chip's text, so an enemy with no grade reads UNGRADED on a ghost chip rather than 'NOT YET ASSESSED'.
- Behaviour change that follows from the plan: give_item no longer drops Playful Cloud into an empty hand below Grade 2 / Output 50, and armory_return no longer hands it over as the next tool then. wp6_items' four checks of the old behaviour are rewritten and two pin the new one.
- wp2_grades, wp4_board and wp6_items each gained 'phase 2:' checks; none of their existing checks was removed. Round 1 tightened one wp6 check (the unowned tool's reason).
- item_req_line catches only IndexError, TypeError and AttributeError now; any other error in a checklist row is raised rather than shown as '?'.

**Open**
- Until P3 or P8 applies the three ui_journal.rpy edits in the hand-offs, the journal can show a tool or talisman as pickable that then does nothing, and a rearrange can drop a talisman worn under D28. The first is reachable in normal play after the merge; the other two need the review tools or an old save.
- A tool held under D28 leaves my hand with no warning when I Take another at the racks and Return it. I did not add a toast for it (unverifiable toast width without P2; R6 will keep toasts off the armory). Review-tools only today.
- The armory panel ends about 18 px above the Close button. A longer description, a wrapping checklist or a sixth rack tool would not fit without a viewport.
- The armory's 'sealed on an unmet line' branch of armory_tools cannot be reached with today's data; it is tested with a temporary row in p2_gear.
- A malformed checklist row reads '?' and counts as unmet; item_validate_reqs reports it at lint and developer mode prints it. Any other error in a row now raises instead of being hidden.
- Not run: SMOKE_P0_STRICT (wave 0 only, as instructed).

**Findings left unfixed, with reasons**
- (not fixed) spec: can_hold / can_wear word an unmet grade line as "Needs Grade 2" instead of the bare line "Grade 2" — Kept on purpose; the reviewer said no code change is needed if the owner accepts the wording. It matches can_wear's own grade test, and a bare "Grade 2" reads like a label. It is one function (item_unmet_reason) if the owner wants it changed. P8 records the wording in PHASE2_DESIGN.md 4.9.
- (not fixed) spec: the combat header passes text=_grade, so an ungraded enemy reads UNGRADED instead of grade_chip's own "NOT YET ASSESSED" — Code kept, as the reviewer recommends (wp2_grades already pins "Ungraded"). Added to the P8 docs hand-off: correct 4.8's combat-header row.
- (not fixed) spec: the armory panel ends near y 950, not near 900; padding and two font sizes were tightened — No change now, as the reviewer recommends. I looked again at armory_checklists.png: clear of the footer and Close. P8 corrects 4.9's numbers; the hand-off says a sixth rack tool needs a viewport (ysize about 780, mousewheel True).
- (not fixed) saves: p2_gear has no save / load / rollback test of its own — The plan leaves this to P8's p2_saves, and the reviewer's scratch harness passed. Hand-off to P8 describes the driver-screen harness to build, since the scratch folder does not outlive the session.
- (not fixed) play: the journal's tool picker offers tools I cannot hold (jr_pick_options, P3's file) — Not in P4a's files. The exact edit stays in the hand-offs, now marked as required before the next checkpoint.
- (not fixed) play: the Inverted Spear row shows four ticks but stays "Sealed — Arc Two" when every requirement is met — No change now, as the reviewer recommends (not reachable in Arc One). Added a phase 4 hand-off: clear the spear's `sealed` field, or let the arcii state yield when arc >= 2.

## P4b

**Hand-offs**
- P2 (ui_hud.rpy): toast_room() must return (0, 0, 0) while renpy.get_screen("market_screen") is showing (R6). Until then the club's 'Bond +4' toast and each purchase toast cover MY YEN and the first rows' prices.
- P2 (ui_hud.rpy): night_tag() returns the full hover text: 'Worn out — no missions or training today' or 'Rough morning', '' when clear. Use it as the moon chip's label as it stands.
- P1 (ui_map.rpy): night_out_ok(key) returns (False, '') for any district other than shibuya and shinjuku, before the Evening, and in explore mode; (False, reason) with 'Grade 2', 'After Ijichi's ride-along' or 'Not two nights running'; (True, '') otherwise. night_marks() is {'mountain': 'moon'} all day on an invitation day, else {}.
- P1 (ui_map.rpy around line 100, the waiting mark) and P5 (view_stage.rpy line 130): both call missions_with() without the night rule. Exact edit for view_stage.rpy:130: `$ _job = (not explore_mode) and night_can_work() and any(night_allows("mission:" + mission_view(m)[0], (MISSION_BY_ID.get(mission_view(m)[0]) or {}).get("cost", 0)) for m in missions_with(_who, loc))`. The same test belongs in ui_map.rpy's function.
- P5 (view_stage.rpy line 131): the NEW badge still shows at Night. Edit: `$ _new = has_event("hangout", _who, loc) and night_allows("hang", 1)`.
- P4a (sb_items.rpy): sb_market.rpy calls ITEM_REQS.update(...) at init -1 after sb_items.rpy, so ITEM_REQS must stay one dict object defined there. The market draws item_requirements(id) as chips of (line, met) pairs; short lines fit best. The four market talismans are new ITEMS rows.
- P3 (ui_journal.rpy): the Equipment and Inventory tabs will list four more talismans (borrowed_luck, night_eyes, debt_marker, second_wind), source 'The Black Market'.
- P3/P8 (ui_journal.rpy lines 844-853): after a Gojo night at the ceiling the Stats page reads 'Control 46 · cap 40' and 'Cursed energy 103 / 103 · cap 100'. When the value is above the cap, write the suffix as '  · cap 40, +6 from the ridge' (or drop the cap suffix). P8 adds a PLAYTEST.md line: a value above the cap after a Gojo night is intended.
- P6 (room_computer.rpy, room_library.rpy, room_fishing.rpy): market_exists() is now True, so legends_market is listed. night_can_work() is False only on the day after a Gojo night. The night's morning toast uses 'night_toast' in actions_today.
- P7 (room_cards.rpy): at Night a costed cards_play row is dropped by night_filter_actions, and night_allows('cards_play', 1) is False. Nothing to add unless the action costs 0.
- P8 (sb_loop.rpy, frozen): after `call play_event(_story)` add the line pair `if night_pending():` / `call night_carry_home`, so a future Night beat that rolls the day is walked home before the place view opens. Then let p2_night's E case drive the beat through the loop (leave pick_event unpatched for that turn).
- P8 (p2_saves): save and reload, rollback log untrimmed and from inside the interaction, at sb_night.rpy's three menus; at `call screen market_screen` before and after a purchase and after a rollback through a purchase; on the night_carry_home line; and on 'Day [day]. Morning.' after sb_do_night_gojo with a rollback through its new_day(). Pitfall: a save made at the first interaction after a fixture label reloads from the start of that label's python block, so the driver's own state must not be reset there.
- P8: put a market talisman on through P4a's checklist (the one deferred acceptance line). Run p2_night on the merged tree: its notes for cards_play, the chips and the toast lane should become real checks.
- P8 (the dim club choice): either correct 4.15's wording to the two-choice form as built, or set config.menu_include_disabled, style the insensitive choice button in screens.rpy and collapse the two choices into one with `if yen >= NIGHT_OUT["cover"]`. Decide before checkpoint B: the menu becomes protected once saves exist.
- P8 (docs 4.15 and 6.1): night_pending() 'clears a stale mark; call it from script only, never from a screen'; NIGHT_CARRY_LINES takes place keys before area keys; the night never takes Control past 100, so at a ceiling of 100 it is due only while it beats a day; the new table names; night_bg and the 'bg <district> night' drop-in name; the two companion lines.
- P8 (PLAYTEST.md): a save parked at Night away from the dorm shows Go to bed; an invitation not taken is offered again on Gojo's next in-day (about weekly); the two night scenes and the companion lines are stand-ins for phase 4. If the owner wants the invitation rarer: in night_gojo_morning also require `store.day - store.night_gojo_day >= NIGHT_GOJO["gap"]`.

**Where it departs from the plan**
- The club choice the player can't afford is not drawn dim: it is a separate choice, 'The club · ¥1,500 · Not enough yen', that says one line and brings the menu back (the frozen choice screen has no dim state).
- The owner's-sentence fixtures are promoted until the whole night fits under the ceiling, not 'until night_gojo_due() can be True' (with past_cap 6 a night is due at every grade).
- night_pending() drops a stale mark as a side effect when I am already in my room. Call it from script only.
- NIGHT_CARRY_LINES is keyed by place as well as area (new this round): a place's own row wins, then its area's. One place row today, 'girls_dorm'.
- night_gojo_beats() clamps the night at Control 100 (new this round), so at a ceiling of 100 the night is due only while it can still beat a day. This departs from the plan's formula at Grade 1 and Special Grade only; 4.15 needs the sentence.
- The club's companion line has two versions (new this round): one for Yuji and Nobara, one for anyone else.
- New names the plan does not list, all prefixed: NIGHT_DISTRICTS, NIGHT_OUT_PERIODS, NIGHT_TAGS, NIGHT_REST_REASON, night_on, night_is_night, night_carry_line, night_step, night_day_walk, night_gojo_beats, night_gojo_apply, night_gojo_invite, night_gojo_morning, night_market_here, night_out_auto, night_bg, night_validate, night_new_day_early/late; MARKET_TOP_GRADE, market_price_cap, market_row, market_state, market_outfits, market_yen, market_validate, screen market_req, styles market_*.
- The night out plays over the district's own picture with no extra tint; a picture named 'bg <district> night' drops in by name.
- market_screen closes itself under smoke_autoplay, so the 30-day driver can never hang on it.
- The morning after says 'Worn out — no missions or training today' or 'Rough morning' as an info toast, besides the two cost toasts.
- The harness's 'missions available two days later' check is an equality; it holds in the fixture used.

**Open**
- The night in Tokyo has no entry point in this worktree: the button is P1's map.
- Toasts and the objective banner are drawn over the market screen until P2's toast_room() treats it as a wait screen.
- Requirement chips on the market rows are empty in this worktree (item_requirements is P4a's stub).
- A person's mission mark and NEW badge still show on a rest day and at Night (frozen or other packages' files; edits are in the hand-offs).
- The journal shows a value above its cap after a Gojo night ('Control 46 · cap 40'); P3's file.
- An ignored Gojo invitation is offered again on each of his in-days, roughly weekly. Needs the owner's say to change.
- The unaffordable club choice is pressable, not dim. Needs a decision before checkpoint B.
- A story beat picked by the loop at Night that rolls the day would be walked home one action late; no Arc One beat does this (sb_loop.rpy is frozen).
- The Gojo night and night-out scenes are short placeholders, marked for phase 4.

**Findings left unfixed, with reasons**
- (not fixed) spec: the harness's story-beat net case does not exercise the loop's own order (sb_loop.rpy picks a beat after night_pending()) — sb_loop.rpy is frozen and no Arc One beat rolls the day at Night. Added a NOTE in p2_night and a hand-off to P8 with the exact line pair.
- (not fixed) spec: the unaffordable club choice is not dim (4.15) — Accepted as built: the frozen choice screen has no dim state, and the fix lives in screens.rpy and config. Hand-off to P8 to correct 4.15 or make it dim before checkpoint B, since the menus become protected once saves exist.
- (not fixed) saves: no renpy.save/renpy.load round trips inside the new flows in the package harness — No P4b change asked for; plan 7 gives real save tests to P8's p2_saves. Hand-off added with the list of save points and the pitfall.
- (not fixed) saves: night_pending() writes to the store as a side effect — Code left as the reviewer asked. Hand-off to P8: 6.1's row says 'clears a stale mark; call from script only, never from a screen'.
- (not fixed) play: NEW badge at Night and mission mark on a rest day (view_stage.rpy 130-131) — Frozen file, not P4b's. The two exact edits stay in the hand-offs for P5/P8, and the same test for P1's map mark.
- (not fixed) play: the club's reward toasts land on the market (ui_hud.rpy toast_room) — P2's file. Hand-off stands: toast_room() returns (0, 0, 0) while market_screen shows; P8 turns the p2_night NOTE into a hard check.
- (not fixed) play: journal Stats reads 'Control 46 · cap 40' after a Gojo night — ui_journal.rpy is P3's. New hand-off to P3/P8 with the suffix wording and a PLAYTEST.md line.
- (not fixed) play: an ignored Gojo invitation comes back on every in-day — It is the plan's formula and the reviewer asks for no change without the owner's say. Raised in the owner's note and as a P8 hand-off, with the one-line change if the owner wants it rarer.
- (not fixed) play: the unaffordable club choice is not dim (same as the spec finding) — Accepted as built; see the spec finding.

## Integration fixes after the first trial merge

- **P1:** Both integration problems are fixed on branch p2_1 (commit 8a25c25), and the map harness now passes against the real merged code as well as against the stubs.

- **Banner check (major):** the check in `tools/smoke/p2_map.rpy` now asks P2's `hud_banner_ok()` instead of reading the banner's words from the screen tree. `hud_banner_ok` does not exist in wave 0's stub, so the check looks it up with `getattr` and falls back to the old empty-tree test when it is absent.
- **"YOU ARE HERE" (minor):** the current-area marker in `game/ui_map.rpy` now reads "I'M HERE". The harness check was updated to match, and a new check asserts the campus map shows no second-person words.

To prove the fix against real code, I copied the trial tree (without .rpyc or .git) into my scratch folder, overlaid my two files, and ran p2_map there: 92 PASS, 0 FAIL, including the banner check that was red.
  - hand-off: Orchestrator: re-merge p2_1 at 8a25c25. Only game/ui_map.rpy (one string, one comment) and tools/smoke/p2_map.rpy changed.
  - hand-off: Any other harness or doc that looks for the words 'YOU ARE HERE' on the map must now look for "I'M HERE". I found none in game/*.rpy or tools/smoke/*.rpy on my branch.
- **P2:** The doubled rest-day chip text is fixed on branch p2_2 (commit 6d2b5cc). hud_chips() in game/ui_hud.rpy now uses night_tag() as it comes; the two lines that appended "no missions or training today" are gone. tools/smoke/p2_hud.rpy now swaps in P4b's real rest-day sentence and checks the chip's text equals night_tag() with the clause appearing once. p2_hud, core_flow, wp7_ui, wp0_stubs, check_content and lint all pass. p2_contracts passed 3 of 7 runs; the other 4 failed on hover-focus checks, which I believe is other agents' harness windows taking focus, not this change.
  - hand-off: P4b: the moon chip now shows night_tag() verbatim, so NIGHT_TAGS must carry the full hover sentence (it does today: 'Worn out — no missions or training today', 'Rough morning').
  - hand-off: Orchestrator: run p2_contracts on the re-merged tree with no other Ren'Py window open. Its hover checks use renpy.set_focus and failed intermittently here while other smoke runs were open.
- **P4b:** All three P4b integration problems are fixed on branch p2_4b in one commit, with a new p2_night check for each. Everything I re-ran passes in my worktree (stubs for the other packages); I did not run against the merged tree, so the re-merge is the first test against the real P4a/P2 code.

- **Requirement chips:** `market_req` in /Users/hunterjolly/Desktop/JJK_worktrees/p2_4b/game/sb_market.rpy now draws a tick in paper when met and a cross in seal red when not, the same shape as `armory_req`. The mark is its own text in DejaVuSans.ttf, because the frozen font group in screens.rpy has no cross.
- **Sold after "Grant one of every item":** `market_state` now decides Sold from `market_bought` only. A talisman owned some other way still shows Buy and can be bought once.
- **Stale picture behind the night menus:** `scene expression graded_bg()` is a new statement after the `night_out_ok` test in `night_out` and after the `night_gojo_ok` test in `sb_do_night_gojo`, in /Users/hunterjolly/Desktop/JJK_worktrees/p2_4b/game/sb_night.rpy. The menus themselves are untouched.
  - hand-off: Orchestrator: the brief's lint command should end at `lint`, with no trailing '.'.
  - hand-off: P2 (unchanged from the checker's note): the rest-day moon chip doubles 'no missions or training today' because P2 appends a clause night_tag()'s text already carries; the fix is on P2's side.
- **P3:** The one P3 finding is fixed and committed on p2_3 (6660cbd). Before roll call a person's page now reads "Closer: after roll call" in the Right now panel, matching the NEXT row below it; after roll call it is the usual "Closer: ... — at Bond N" line again.

The change is in /Users/hunterjolly/Desktop/JJK_worktrees/p2_3/game/ui_journal.rpy: a new helper jr_closer(who) builds the line, and jr_person_detail uses it instead of calling unlock_line directly. It reuses jr_next_hangout's "held" state, which is what the NEXT row already follows, so the two cannot disagree. rule_hangout_gate is the same P0 code on the trial tree, so the fix holds against the real code and the stubs alike.

/Users/hunterjolly/Desktop/JJK_worktrees/p2_3/tools/smoke/p2_journal.rpy gained three checks (173 pass, 0 fail) and a screenshot, shots/p2_journal/page_megumi_before_roll_call.png, which I looked at: the panel and the NEXT row say the same thing.
  - hand-off: No edits are needed in files P3 does not own.
  - hand-off: Orchestrator: re-merge p2_3 at 6660cbd. Only game/ui_journal.rpy and tools/smoke/p2_journal.rpy changed.

## Left after the second trial pass (all minor; for P8 unless a wave-2 package owns the file)

- **frozen, game/ui_icons.rpy:316-322, screen hover_label (preferred side):** Unchanged from pass 1. 'Rough morning' is still drawn over the date chip (walkh_new_c/j11_rough_morning_hover_moon.png: 'Day 4' is half hidden) and 'Journal (J)' over the Map button (walkh_new_a/a04_hover_journal.png). Same cause elsewhere: on Tokyo, Shibuya's label covers the Kawasaki card (b11_tokyo_hover_shibuya.png); on the journal's People tab a card's label covers its own name and the next card's (walkh_save_a/d02_journal_hover_card.png). *Fix:* P8 or a wave-0 fix: in hover_label add `elif str(_hover_tip[1]).startswith("hud_"): $ _hover_side = "bottom"` beside the sample_ rule. For map cards and journal cards, place the label on the side with free room (below the card when the right or left neighbour is within the label's width).
- **frozen, game/ui_icons.rpy:205-206, icon():** Unchanged from pass 1: with the art installed icon() returns the picture and ignores `gold`, so 'Train until morning' is a white tile like the others (walkh_new_c/i06_hover_train_until_morning.png). D23 calls it a gold icon. *Fix:* In icon(), when gold and the picture exists, return `Transform(ICON_ART % name, xysize=(size, size), matrixcolor=TintMatrix(gui.gold))`. Or P2 gives rail_btn a gold frame when `gold or name in ICON_GOLD`.
- **frozen, tools/smoke/phase1_all.rpy:339-347, zzp_map():** Unchanged from pass 1: 73 notes 'map: no sensitive Go button for … ; going anyway'; the harness passes 14/0 but no longer walks through the map. *Fix:* P8: have zzp_map press area_<area_of(loc)> and then row_<loc>, as wp1_world.rpy does.
- **P4b, game/sb_night.rpy:525-526, label night_out (the new `scene expression graded_bg()`):** The fix removed the daylight room, but graded_bg() draws `here`, which is still the campus room I left from. 'Shibuya, after dark.' and the club / Head home menu play over my bedroom at night (walk_new_c/j04_night_menu.png). The club scene that follows has the right skyline (j05_club_scene.png). P4b listed this as an open issue. *Fix:* In night_out, replace the new line with the district's own picture, as sb_tokyo.rpy:171-172 does: `$ scene_light = light_for_bg(DISTRICTS[key]["bg"])` then `scene expression DISTRICTS[key]["bg"]` (or the same skyline the club scene uses). Leave sb_do_night_gojo's line as it is.
- **P2, game/sb_screens.rpy:282-289, rail_tip():** The Gojo night's hover label reads 'More than a day's worth. Tomorrow I'm no use to anyone. · 1 period' (walkh_new_c/i06_hover_train_until_morning.png). It takes the rest of the night and the next day's work, so '1 period' is wrong beside 'Go to bed … The day ends.', which shows no cost. *Fix:* In rail_tip, do not append the period cost at Night (`if cost and store.period != PERIODS[-1]:`), or have rail_rows pass cost 0 for actions in NIGHT_OK.
- **P2, game/ui_hud.rpy:83-84, toast_room() in a scene:** In a scene the toast stack sits at x 1880 and is about 460 wide, so its left 40 px lie over the right end of the choice buttons (1000 wide, centred). Seen with the review tools' toasts still up at the night out's menu (walk_new_c/j04_night_menu.png). No text is hidden. It may be phase 1's layout carried over; I did not compare. *Fix:* In toast_room(), when renpy.get_screen("choice") is up return (0, 0, 0) so toasts wait, or narrow the scene lane so the stack starts right of x 1460.
- **P3, game/ui_journal.rpy, jr_person_detail: the 'Usually' hover label on the Right now panel:** The label is drawn to the left of the panel and its right edge lies about 20 px over the panel's border and the first letter of 'RIGHT NOW' (walkh_save_a/d04_person_page_hover_now.png). *Fix:* Give that tooltip's label a small gap from the panel (shift it 24 px left), or show it below the panel's first line.

---

# Hand-offs from wave 2

*Written 5 Oct 2026 from the wave 2 reports (P5, P6, P7, P9), their review rounds, the two trial merges and the integration edits. P8 reads this before it starts. Wave 2 was merged into phase2 at 50998ce.*

## P5

**Hand-offs**
- Owner at checkpoint C: the classroom. It has no foreground; on the sheet (shots/layout/view_classroom.png) the front-aisle people stand over the nearest desks and chairs. Either keep it, or restore a person behind a desk: a polygon covering the whole desk with legs and chair in tools/fg/classroom.json, then tools/make_fg.py, a far slot in VIEW_SLOTS['classroom'] and "classroom" in VIEW_FG_ROOMS (game/view_stage.rpy).
- Owner at checkpoint C: VIEW_FG_TALK. In dialogue the foreground stays over the person only in the cafeteria. For the plan's behaviour in every foreground room, set VIEW_FG_TALK = ("cafeteria", "dorm_common", "utahime_office") in game/view_stage.rpy.
- P8 (frozen ui_icons.rpy): the hover label opens to the left of the button and can cover the neighbouring tag's NEW chip or the next person's head. Let a tooltip tuple carry a side as a third item, e.g. (text, key, 'above'), and open the label above the button when it is given. P5's three tooltips in game/view_stage.rpy (the sprite button, the pose button and the tag in view_tags) then pass 'above'.
- P8 / orchestrator (after batch 3's poses): if two standing people overlap beside a pose, raise the spacing test in view_pick_slots' mixed-layout pass (game/view_stage.rpy, about line 335) from 170 to 0.6 * 760 * max(pool[i][2], pool[j][2]), or give that room a sidecar slots row. Re-check the common room with four people afterwards: wider spacing may leave no clear set there.
- P6 / P8 (hotspots under a foreground): the foreground picture is drawn after hot_layer(here), so a hotspot on a foreground object is covered unless registered front=True. The card table's start point (900, 800) in dorm_common has its top third under the coffee table's apron: register it front=True or move it to about (955, 850). Polygons in tools/fg/<place>.json: dorm_common (x 761 to 1150, y 698 to 908), cafeteria (near table from x 1160, y 881 down), utahime_office (x 156 to 779, y 557 to 968). The classroom has none.
- P6 / P9 / P8 (points against the slots): the classroom's four-person rectangles are centred at x 250, 540, 820, 1100 (zoom 0.52); the blackboard spot (760, 360) is behind the third person when four are in. The TV look spot (1420, 520) is behind the third person in dorm_common. tools/layout_sheet.py hot_<place> draws them once p2_contracts has rewritten shots/layout/defaults.json.
- P8 / owner (art rule): every new painted time variant of a foreground room (dorm_common, cafeteria, utahime_office) needs its fg_<loc>_<variant>.png. Until it exists the room falls back to plain default slots and draws no foreground.
- P9 / P8: re-run the pose plan's schedule check (p2_view section 6) on the merged tree, since P9 moves schedule slots into the hubs. If a row fails, either the slot stays or the row moves in POSES (tools/make_pose_workflow.py).
- P9: no BG_LIGHT row was requested for the five hubs, so none was added to lighting.rpy; they get the default outdoor light. The tag check walks LOCATIONS with four people in each room, so it covers the hubs after the merge.
- P8 (frozen sb_screens.rpy): VIEW_INK = 0.10 and VIEW_INK_PERSON = 0.35 mirror `add Solid(gui.ink) alpha 0.10` in sb_place and `alpha 0.35` in sb_char. If either alpha changes, change the constant too.
- P8 (frozen sb_screens.rpy, optional): stage_x(who, loc) reads view_slots by index, which differs from where a person stands when someone else is a painted pose. Exact version: `row = [r for r in view_stage_rows(loc or store.here) if r['who'] == who]; return row[0]['x'] if row else 700`.
- P8 (frozen ui_hud.rpy): the tags' left limit, VIEW_TAG_EDGES[0] = 179, assumes the Review tools link ends at x 171. If that link moves or widens, change the constant.
- P8 (p2_saves): save in dialogue after stage_person with the rollback log untrimmed (p2_view purges it first). A working pattern is the reviewer's harness at scratchpad p2_w2/P5/review_saves_r1/zzr_saves.rpy (run with SMOKE_ASSETS=tools/smoke/assets/p2_view): jump sandbox, drive sb_place and sb_char from an overlay timer, guard the start flag against the load's greedy rollback.
- P8 (docs, PHASE2_DESIGN.md): in 4.5 and section 7 P5 record 'five foreground files (no classroom)'. Section 5 row 6 can stay as written. In 4.5 / 6.1 / 7 also record: the tags are in view_fg / view_tags; VIEW_FG_TALK; VIEW_FG_ROOMS and the default-slot fallback; the ink wash; view_pick_slots (mixed layouts, 170 px), view_pose_cost; view_tag_w, view_tag_est, view_tag_xs(rows, widths), VIEW_TAG_GAP, VIEW_TAG_EDGES, VIEW_TAG_W; VIEW_SPEAKING as [who, until]; the <who>_fx_in.png close-up and install_face.py's --prepare / --sheet; install_pose.py's --name, --bg, --root, --dry; and the names view_stage_rows, view_draw_order, view_sprite, view_pose_patch, view_fg_path, view_fg_image, view_room_matrix, view_tag_marks, view_face_layers, view_say_cb, view_validate, light_face_layers. tools/README.md needs the four new tools.
- P8 (standing set): p2_view reports 117 PASS in about 75 s; wp7_ui 143; p2_hud 109. p2_view runs the system python3 for install_pose.py, and its pointer check needs the harness window to hold the pointer (re-run alone if it fails while another Ren'Py window is open).
- P8 (frozen _lib.rpy, optional): zz_worst focuses only by id, which does not light a focus_mask sprite. To hover a sprite in the worst-case shot it would need a point option that calls renpy.display.focus.mouse_handler(None, x, y, default=False).
- Orchestrator (layout sheets for checkpoint C): the sheets in the p2_5 worktree's shots/layout/ are current as of this round, but shots/ is gitignored, so regenerate in the merged tree: tools/smoke.sh tools/smoke/p2_contracts.rpy; then python3 tools/layout_sheet.py view_<room> for dorm_common, cafeteria, classroom, courtyard, training, infirmary, library and utahime_office; then python3 tools/install_face.py --sheet.
- Orchestrator (art batch 3): python3 tools/make_pose_workflow.py --batch 3 writes the two pose workflows; python3 tools/install_face.py --prepare yuji, then python3 tools/make_edit_workflow.py yuji --only blink,talk writes yuji_fx.json. Install with tools/install_pose.py <render> and tools/install_face.py <render> yuji blink|talk.
- Orchestrator: during the first build two input pictures were copied into ~/ComfyUI-Shared/input (pose_ref_nobara.png, pose_room_dorm_common_evening.png); they are the same files batch 3 will put there. Nothing else outside the worktree and the scratch folder was written in any round.
- P8 / owner: a pose shows whenever its file exists for the hour, even when AMBIENT_STORY has changed the caption. If that matters, give view_pose a caption test or paint a second pose.

**Where it departs from the plan**
- Five foreground files ship, not the plan's six. The classroom's foreground was removed in round 1; everyone there stands in the front aisle (with three people the middle one is a slight step back, with nothing in front).
- A foreground room (VIEW_FG_ROOMS: dorm_common, cafeteria, utahime_office) uses the plain default slots while its foreground picture for the hour is missing.
- make_pose_workflow.py accepts both <place> <who> (the plan's order) and <who> <place>.
- The name tags' right limit is the tag's right edge at x 1700; the second icon column starts at 1726.
- The name tags are drawn by screen view_fg (through screen view_tags), not by view_stage, so they sit above the foreground picture.
- In dialogue the foreground is shown over the sprite only in the cafeteria (VIEW_FG_TALK), not in every room with a foreground file as 4.5 says. For the owner at checkpoint C.
- Foreground and pose pieces get the same ink wash the screens lay over the room (VIEW_INK 0.10, VIEW_INK_PERSON 0.35, mirroring sb_screens.rpy).
- When someone is a painted pose, the people still standing take the slots that cover the pose box least: one layout's slots when a clear set exists, else slots from all the room's layouts, 170 px apart. stage_x in sb_screens.rpy still reads plain slots, so it can differ in that case.
- Name tags are moved apart by their measured widths (8 px gap) and kept right of the Review tools link.
- A companion never takes their pose.
- The far slots in rooms with a foreground are stronger than the plan's default (zoom 0.43 and feet 190 px higher behind the coffee table). Rooms without a row keep the plan's default.
- VIEW_BLINK_OK and VIEW_TALK_OK are ('neutral',) only.
- The mouth moves for a time taken from the line's length (0.6 to 2.4 s), since text is shown at once; VIEW_SPEAKING is [who, until], not [None].
- Blink and talk are edited from a new close-up cut from the game's own sprite (install_face.py --prepare writes <who>_fx_in.png); make_edit_workflow.py loads that file for --only blink,talk.
- install_pose.py's 4 px blur is a 4x4 block average and its region is measured on those blocks; both tools are pure Python and take --root so the harness never writes into the repository.
- The save test purges the rollback log at its start.
- install_pose.py's test pictures are drawn when the harness runs rather than kept in the asset overlay.
- The harness slot check is 'left of x 1700 and not off-screen'; a NOTE lists the defaults left of x 40 (dorm with four people, x 27).
- No game/layout/view_*.json ships; install_pose.py creates the file when the first pose lands.
- Round 2 made no commit, although the task named one ('Phase 2 P5: review fixes, round 2'): no finding needed a change to a tracked file.

**Open**
- The harnesses, the standing set and the save loads were not re-run in round 2; their results are round 1's, at the same commit.
- The pose workflow and the blink/talk workflow have not been opened in ComfyUI; install_face.py's line-up was tried only on a simulated edit.
- view_pick_slots was tested with the one test pose (Nobara on the sofa, three and four people). Its 170 px spacing lets two standing people touch shoulders; overlap with other rooms' poses is unknown until batch 3.
- The hover label of a person or tag opens to the left (frozen ui_icons.rpy) and can cover the neighbouring tag or head while hovered.
- Classroom: the front-aisle people stand over the nearest desks and chairs on the sheet; the owner has not ruled on five foreground files instead of six.
- In the stand-in case (no foreground picture) a person on a default slot can stand in front of the coffee table with their legs over it.
- The far slots and the three remaining polygons were placed by eye; in the cafeteria the fourth person's leg can touch the near table's corner.
- VIEW_FACE boxes have not had a real blink or talk picture laid in them.
- People a step back are large for the furniture they stand behind; a matter of taste.
- A person shown by a later `show` in a cafeteria scene at pos_r stands behind the near table.
- Shoko's planned pose is a day picture and the infirmary has a night picture, so at Night she is her standing sprite unless a night pose is painted.
- The dorm with four people starts at x 27 (phase-1 default), left of the plan's x 40; one VIEW_SLOTS row or a sidecar fixes it if it matters.

**Findings left unfixed, with reasons**
- (not fixed) spec / five foreground files ship where plan 4.5 says six (the classroom's was removed in round 1) — No code change, as the finding asks. It is the owner's choice at checkpoint C on the classroom sheet (keep the front aisle, or restore a whole-desk polygon, a far slot and 'classroom' in VIEW_FG_ROOMS). The docs edit goes to P8. Both are in the hand-offs.
- (not fixed) play / view_pick_slots' mixed-layout pass keeps only 170 px between centres, so two standing people can touch — No change, as the finding says. The only pose that exists reads acceptably, and widening the spacing now could leave the common room with no clear set for four people, which would put someone back over the sofa. The reviewer's one-line change (line 335: 170 becomes 0.6 * 760 * max of the two zooms) is in the hand-offs for when a batch-3 pose shows a real overlap.
- (not fixed) play / the hover label opens to the left and can cover the neighbouring tag or head — Out of scope for P5: the label's side is set in the frozen ui_icons.rpy. Handed to P8 with the edit (a third tuple item 'above'); once that exists, P5's three tooltips in view_stage.rpy pass it.

## P6

**Hand-offs**
- P8 (frozen tools/smoke/wp0_stubs.rpy line 353): replace `check(registered_place_actions("dorm") == [("zzact", "Zed", "A test action.", 1)],` with `check([a for a in registered_place_actions("dorm") if a[0].startswith("zz")] == [("zzact", "Zed", "A test action.", 1)],`. Re-run this round: 323 PASS.
- P5 (owns tools/smoke/p2_hud.rpy this wave; else P8), line 581: before the `if any(v[0] in ("act", "mission") ...` line add `_zz_hot = [("act", h["act"]) for h in hot_spots_for(_zz_loc) if h["lines"] is None]` and add `and v not in _zz_hot` to the generator's condition. Re-run this round: 109 PASS.
- P8 (tools/smoke/p2_night.rpy lines 1266 and 1268): `_zz_dorm = zz_n_ids(rail_actions("dorm")) + builtins.sorted(hot_covers("dorm"))` and `_zz_caf = zz_n_ids(rail_actions("cafeteria")) + builtins.sorted(hot_covers("cafeteria"))`. Re-run this round: 165 PASS.
- Orchestrator: the three patched harness copies are in the scratch folder p2_w2/P6/retry/patched/ (wp0_stubs.rpy, p2_hud.rpy, p2_night.rpy); their diffs against the originals are exactly the edits above.
- P7: the card table's hotspot is already registered in room_spots.rpy (id card_table, dorm_common, act cards_play, point (1400, 876) in game/layout/hot_dorm_common.json). Do not register a second one.
- P9 / P8: P6's final points are in game/layout/hot_<place>.json (listed under deviations). Exits must clear those; the vending machine is at (1600, 690).
- P5: hotspot visibility was placed against today's view_slot_rects. If the stage slots move right of about x 1360 or people stand taller than y 312, re-run tools/smoke/p2_rooms.rpy and look at room_*.png.
- P8 (phase2_all): under autoplay sb_do_pc_open closes at once and sb_do_fish_cast hooks at q 0.5 three times. To drive the screens use returns as p2_rooms' zz_r_drive does: ("page", id), ("check",), ("hook", 1.0). zz_r_drive(..., own=fn) leaves a screen to its own timers. After sb_do_fish_cast has dealt its first cast renpy.can_rollback() is False; a harness that rolls back across a sitting will be refused. The text filter now sees fishing's opening line as "[_fish_line]", like the result lines.
- P8 (p2_saves): p2_rooms writes a real save inside pc_screen and fish_screen and checks can_load; it does not load them. Working state machines are in scratch p2_w2/P6/review_saves_r3/rv3_saves.rpy (passed against db1632a; not re-run against 548eb33, which changes fishing's opening line and the pack-up-at-the-bite line) and review_saves_r3/rv_owner.rpy (use it only on slots parked on sb_map or sb_place, such as 1-1 and auto-1); fix_r1/zzf_load.rpy also still works. Do not use review_saves_r2/rv2_saves.rpy: it expects round 1's behaviour. Expected for fishing: a save loaded during a cast lands on fish_screen with the same cast number, kind and centre, nothing settled, in the phase it was saved in; a save at the bite starts that cast's sweep again. A save made with the record book open loads with the book closed, same cast: do not assert the book is still open. Cautions: in the shelf menu the caption is item 0, so the choices are 1, 2, 3; with the rich fixture a Kurose beat plays in the Library after the study, so compare Insight and the period on the first line after lib_read; treat the say screen as up only when its 'what' text is non-empty; set stage counters with max(), because renpy.rollback(checkpoints=1) re-runs the harness's own set-up block; expect Insight +2 from the page 'techniques'.
- P8 (protected statements): `call screen pc_screen(_pc_page)` / `$ _pc_r = _return`, `call screen fish_screen` / `$ _fish_r = _return` and the shelf `menu:` are protected from commit a2201c9 and unchanged in 2b0d19d, db1632a and 548eb33. `$ renpy.block_rollback()` sits on the line above the fish_screen pair.
- P8 (docs, PHASE2_DESIGN.md): 3.1: PC_SITES rows are dict(name, url, tone, color), color being the name of the gui.pc_* token. 3.3: pc_noted; fish_state gains plan (list of [kind, spare, r, wait]). 4.10: the final points. 4.11: Home's order (requests, intranet lines, sites); the Night button is drawn shut. 4.13: q's definition and the zone rule; the result line is narration; rollback is blocked when a cast is dealt and again when it is settled; packing up while the float sits is free, packing up at the bite is a miss with its own line, leaving after a cast costs the period; the sitting is rolled when it starts, and a save loaded during a cast finds the same cast in the same phase; a save loaded at the bite starts that cast's sweep again (same fish, same zone); Esc / right-click closes the record book when it is open, and the float's wait restarts when the book closes; the opening line rotates by day; a species' first catch says 'The first in the book.'; the record book's button is above Pack up; the seven-row record book and its names. PLAYTEST.md: the courtyard machine has no picture behind it; the fishing float and bar are engine-drawn stand-ins.
- Owner's call, then P8 if yes: the shipped request note 'What was that on the ridge?' (the plan's 4.11 wording) could become 'Who was Ryomen Sukuna?'. Edits: game/room_computer.rpy PC_AUTO_REQUESTS (P6's file), tools/smoke/p2_rooms.rpy (the check that compares the note's text), PHASE2_DESIGN.md 4.11.
- Phase 4 / mission authors: to gate a mission on research, call pc_request("<page>", "<the question>") and put gate.flags=("researched_<page>",) on what it opens. The note may hold any characters; brackets and braces are drawn as written.
- Orchestrator: the lint command in the brief ends in 'lint .'; it was run without the dot, as P3 and P4b advised.

**Where it departs from the plan**
- Final hotspot points differ from 4.10's start points (measured on stand-in art): computer (440, 590), bed (1330, 720), card table (1400, 876), TV (1590, 560), bank (1580, 905), stacks (300, 520), locked cabinet (1630, 480), vending machine (1600, 690), blackboard (1450, 500), counter (1500, 600), cot (1420, 700), racks and armory (1600, 600), board (1500, 470), veil (960, 250). Code defaults and sidecars hold the same numbers.
- The courtyard picture has no vending machine in it; the icon sits on the right-hand building's porch.
- pc_open is registered with order=5 so it sorts before wp0_stubs' test action.
- One saved variable 3.3 does not list: default pc_noted = "".
- A page's first-read Insight is given quietly and shown on the page's gold 'Noted.' strip; no toast.
- Cross-check reads offers through board_summary()["offers"] and keys the week on board_week_now().
- The one shipped request is derived in pc_leads() from PC_AUTO_REQUESTS and the flag saw_the_ridge_veil; it is not stored in pc_requests.
- PC_SITES rows are dict(name, url, tone, color); 3.1 gives three keys.
- Home is ordered: requests, the intranet's two lines, then the sites as one-line cards.
- At Night the cross-check button is drawn shut with 'Too late. Bed.' under it; the label's refusal remains for a driven return.
- Fishing: q is closeness to the middle of the zone (1.0 centre, 0.2 less per tenth of the bar); a fish is landed when q >= 1 - zone. Under autoplay the 0.5 hook lands only the easiest species.
- The fishing marker redraws every frame and ignores the Motion switch.
- A cast's result is a line of narration after the screen closes, so fish_screen keeps exactly its three returns.
- Packing up while the float sits is free; packing up once it has dipped is a miss (the cast is spent, the period charged). Packing up after any settled cast costs the period.
- NEW: packing up at the bite says its own fixed line ('I lift the rod while it is still making up its mind...'), not a miss line; this also replaces the River Lord's and the pale thing's special miss lines in that case.
- Rollback is blocked when a cast is dealt (before fish_screen opens) and again when it is settled.
- The sitting's three casts are rolled in fish_begin() into fish_state["plan"]; fish_next() reads them. A save loaded during a cast lands on fish_screen in the same cast and phase; a save at the bite starts that cast's sweep again.
- The record book has seven rows (six species and the River Lord, ??? until caught); names are Pale chub, Dace, Ayu, Yamame trout, Char, Carp.
- The record book's button is at (1750, 900), above Pack up.
- NEW: with the record book open, Esc / right-click closes the book; otherwise it packs up. Closing the book by any of its three ways restarts the float's wait (fish_rewait).
- NEW: the cast row top left sits on a dark plate (frame at (48, 50), Solid #07060c99).
- NEW: the sitting's opening line rotates over three lines by day (FISH_OPEN_LINES, fish_open_line); two of the three differ from the reviewer's suggested wording so that none presumes an earlier sitting.
- NEW: the River Lord's catch line names the fish from two words cut into the rod's handle.
- A species' first catch says 'The first in the book.'; 'A new best.' only when an earlier best is beaten. fish_land's return is unchanged.
- With a companion, sb_do_fish_cast says one extra line naming them (_fish_who).
- The vending machine also refuses, at no cost, when stamina is full.
- The Library menu has exactly three choices and no way back; on a rest day the barrier shelf says its own single line.
- The legends thread hints at the alley and the Sun Mall (Kawagoe's shut mall); no line about the forty-minute survey.
- New names beyond the plan, all prefixed: SPOT_SET, SPOT_LOOKS, SPOT_VEND; pc_can_see, pc_pages, pc_links, pc_address, pc_color, pc_visit, pc_week, pc_checked, pc_offers, pc_check_ok, pc_check, pc_validate, PC_SITE_ORDER, PC_PAGE_ORDER, PC_AUTO_REQUESTS, _pc_bad_n; fish_roll, fish_hit, fish_length, fish_cast_once, fish_plan, fish_settle and the sitting helpers, fish_rewait, fish_open_line, FISH_OPEN_LINES, fish_validate, _fish_who; LIB_SHELVES, lib_gains, lib_line, lib_read, lib_validate.

**Open**
- wp0_stubs, p2_hud and p2_night each fail one check in P6's worktree until the hand-off edits are applied at the merge.
- Quitting the game at the bite and reloading starts that cast's sweep again (same fish, same zone), so the hook can be retried that way. Closing it needs a second protected call screen between the dip and the hook; left for the owner (checkpoint C).
- A save made with the record book open loads with the book closed, and the float then dips at once. Only a quit autosave can reach this.
- The record book's overlay click and Close button carry the same action list as the Esc key, but the harness presses only the key.
- The record book's hover label is checked by screenshot only; no check measures its rectangle.
- Because rollback is blocked from the first cast, a player who sits down to fish cannot roll back to before the sitting once the float is in the water. Packing up before the dip is still free.
- Opening the record book repeatedly puts the bite off each time (the wait restarts on close). Harmless, but it is a way to stall.
- Fishing was still not played by hand: the sweep (1.5 s a pass), the 1 to 3 s wait and the zone widths are untested for feel. The numbers are constants at the top of game/room_fishing.rpy.
- Home scrolls again with about six or more requests; the bookmarks on the left still reach every page.
- The card table's hotspot cannot be seen in this worktree (P7's stub); its point is only linted.
- With two or more people in a room some hotspots hide and their actions return to the column; that is the plan's rule, but it may read as icons coming and going.
- Only the first-set table was built; eight rooms have no hotspot.
- The pages' lore (the Nihon Shoki entry, the Keicho duel, Noritoshi Kamo, Michizane) is written from memory and was not checked against a reference.
- The made-up web addresses use realistic endings (.jp, .net); they are never clickable.

**Findings left unfixed, with reasons**
- (not fixed) spec/minor: a save loaded at the bite starts that cast's sweep again (same fish, same zone) — No code change, as the finding says: D33 is met in ordinary play, and closing this fully needs a second protected call screen, which is the owner's call. The line is added to the P8 docs hand-off for 4.13, to open issues and to the owner's note.
- (not fixed) saves/minor: a save made with the record book open loads with the book closed — No code change, as the finding says. The note is added to the P8 (p2_saves) hand-off. The bite-at-once side effect after such a load remains, because the load does not pass through the book's closers.

## P7

**Hand-offs**
- P6 (room_spots.rpy): register the card-table hotspot as an action hotspot for `cards_play` in dorm_common, e.g. `register_hotspot("cards_play", "dorm_common", 900, 800, "cards_play")`. It shows only while cards_ok() is True, which is also False once the day's ¥6,000 is won.
- P6 / P2 (column budget): dorm_common gains one column tile, 'Play cards' (id cards_play, cost 1, order 40), while someone is there, I hold ¥100, I haven't sat with everyone present today, and the day's limit is not reached.
- P3 (journal Me page): cards_records()['today'] is net yen for the day and can be negative; 0 on a new day. No edit needed.
- P8: re-run tools/smoke/p2_cards.rpy on the merged tree. Section G's hotspot check uses the harness's own hotspot (zz_c_table) plus any real one for cards_play.
- P8 (p2_saves): park on `call screen cards_blackjack` inside label mg_blackjack; state is cards_state plus cards_sit. A reload mid-hand keeps the dealt cards but the next card is drawn fresh, by design. A save made at the poker draw comes back with no cards marked: do not assert on marks. After a load the move buttons are deaf for 0.3 s (cards_guard starts True): a harness that clicks must wait that long; the autoplay timer is not affected.
- P8 (phase2_all): under smoke_autoplay, sb_do_cards_play plays one blackjack hand at ¥100 (stand) and gets up, costing one period. It needs someone in dorm_common, ¥100, and the day's card winnings under ¥5,800.
- P8 (docs, PHASE2_DESIGN.md): 2.3's protected list for room_cards.rpy is as written. Update 3.3 with cards_sit (keys day, hands, net, opponents, stake). Update 4.12 with: the ("deal",) return; no-raise betting; the three-stake rule for poker; how the cap is applied, including cards_ok() going False at the cap and the poker note 'They'll pay me ¥N more today, no further.'; the ¥3,000 limit being a stop rule; light card faces; the extra CARDS_STYLE keys (shows, rest, sore, stop, blind, glad, deal); rollback blocked after a read; no hover labels on worded buttons, only on the look icon; 'Give up the hand' / 'Fold and leave'; people not yet played seated first; the table remembering the stake; the 0.3 s click guard on the two game screens; nobody speaks on a split. 6.1 may list cards_can_deal, cards_today, cards_cap_left, cards_auto, cards_block, cards_row_gap, cards_default_stake, cards_act, cards_hands_word.
- P8 (docs/PLAYTEST.md, checkpoint C list): ask the owner whether the ¥3,000 stop should be a hard ceiling, and whether the table should disappear at the ¥6,000 cap. Hard-ceiling edit if wanted: in cards_can_deal refuse when net - cards_need(game, stake) * (2 if game == 'blackjack' else 1) < -CARDS_LIMIT['down'], and add the matching test on the sitting's net to cards_bj_can_double.
- P8 (tools/smoke/_lib.rpy, ZZ_SHAPED): add cards_sit to the shaped list. p2_cards builds it with cards_sit_down() and clears it with cards_get_up(); a few checks set cards_sit keys (stake, net, hands) on a sitting built that way.
- P8 (tools/smoke/_lib.rpy) and other packages' harnesses: renpy.get_widget(screen, id) on a textbutton returns the Text inside it, not the Button, so `._get_tooltip()` or `.action` read that way test nothing or raise. p2_cards has a helper zz_c_btn(screen, wid) that walks up to the Button; consider moving it into _lib.rpy and checking other harnesses' tooltip checks on textbuttons.
- P8 / orchestrator: p2_cards joins the standing set at 145 PASS, about 45 s. It has no pointer-dependent pass/fail check.
- Orchestrator: the lint command in the task text (`... lint .`) fails on this SDK with IsADirectoryError: '.'; drop the trailing dot.

**Where it departs from the plan**
- The two game screens return one value the plan does not list: ("deal",), for the Deal button shown after a hand is settled.
- Blackjack with Double settles at ±2 stakes as well as the plan's ±stake, +1.5 stake or 0.
- A fourth saved variable, `default cards_sit = {}`, holds the sitting's tally (day, hands, net, opponents, stake) so the five-hand and ¥3,000 limits span both games.
- The daily cap is enforced two ways: blackjack is not dealt at a stake whose doubled win could pass it; a poker pot is paid only up to it, with a line. New this round: the table's poker button says beforehand how much a win can still pay.
- cards_ok() is also False once less than ¥200 can still be won that day, so the place action disappears at the cap.
- Poker needs three stakes in hand to be dealt; blackjack needs one.
- Poker has no raises: Check, Bet or Fold, then Call or Fold. The Call button returns ("bet",).
- CARDS_STYLE rows carry more keys than the plan's five: shows, rest, sore, stop, blind, glad, deal.
- The next card is chosen when it is drawn, not fixed at the shuffle.
- Card faces are a light paper colour with red and black suits, not a dark panel.
- With two or three opponents the look button switches on a 'Read' button under each opponent still in.
- The poker buttons sit at y 850 rather than 840.
- The game screens do not bind the menu key and are not modal.
- Leaving in the middle of a hand forfeits what is on the table; the button says so ('Give up the hand', 'Fold and leave').
- No worded button on the three card screens has a hover label; only the icon-only look button keeps one.
- With more than three people in the room, the ones not yet played today are seated first.
- The table opens on the sitting's last stake, not always the smallest.
- A blackjack hand of seven or more cards overlaps its cards so the row stays left of the total.
- The card-table hotspot is not registered here; it belongs to P6's room_spots.rpy.
- The ¥3,000 limit is a stop rule checked before each deal, so a sitting can end further down than ¥3,000. New this round: the closing line says the real figure.
- New this round: the move buttons on the blackjack and poker screens take no click for the first 0.3 s after the screen opens (screen variable cards_guard, action built by cards_act). The table picker is not guarded: none of its buttons sits under a game screen's button.
- New this round: on a split pot the opponent says nothing and keeps their resting face.

**Open**
- Balance is untuned. One good poker hand at ¥500 against three opponents won ¥3,500 in the harness, so the ¥6,000 daily cap can be reached in one or two hands. Tells fire about 85% of the time when true. All of it is table values in CARDS_STYLE and CARDS_STAKES.
- Owner decision for checkpoint C: the ¥3,000 limit is checked between hands, so a sitting can end at ¥4,000 or ¥5,000 down. Making it a hard ceiling is a small change (see hand-offs).
- Owner decision for checkpoint C: the 'Play cards' icon goes away once the day's ¥6,000 is won, which the plan's cards_ok does not list.
- With three opponents at ¥1,000, the poker button on the table always reads "They'll pay me ¥6,000 more today, no further." instead of its usual blurb, because such a hand can win ¥9,000. It is true, but the owner may find it noisy; the alternative is to show it only once something has been won that day.
- The new near-limit note on the table picker was checked as text only; no screenshot of it was taken or viewed.
- The 0.3 s click guard has been tested with posted mouse clicks (the reviewer's harness), not by a person; if 0.3 s feels sluggish or too short, it is one number in each screen's timer.
- The real card-table hotspot does not exist until P6's branch merges; until then the table is reached from the icon column only.
- No renpy.save / renpy.load round trip inside the card screens is in this harness (P8's p2_saves).
- The poker blind player (Gojo) bets and calls at random; nobody has played against him by hand yet.
- With the hover labels gone, the one-line explanations of Hit, Stand, Double, Check, Bet and Fold are not shown anywhere.
- If the dialogue window is still up when a card screen opens, its gradient dims the bottom buttons. Seen only in the harness, not from the place view.
- The harness's rollback test calls renpy.ui.reset() before a rollback that will actually go through (failing case only); harness-only.

**Findings left unfixed, with reasons**
- (not fixed) spec minor (carried over): declared departures from plan 4.12 and 3.3 need P8's doc update and the owner's word — No code change wanted. All stay in deviations and the P8 hand-offs.
- (not fixed) saves minor (carried over): cards_sit (with stake) is not in plan 3.3 or ZZ_SHAPED — Not my files. Kept as a hand-off to P8. No new saved variable this round: cards_guard is a screen variable (a bool).
- (not fixed) saves minor (carried over): a save at the poker draw loads with no cards marked — Settled as no fix. The P8 hand-off (p2_saves must not assert on marks) is kept.
- (not fixed) play minor (carried over): the ¥3,000 stop rule and cards_ok() False at the cap are owner decisions — No change. Both stay in the checkpoint C list handed to P8.

## P9

**Hand-offs**
- P8 (frozen tools/smoke/wp0_stubs.rpy, 2 failing checks; proven 323/0 in a scratch copy). Line 349: `_ids = [a[0] for a in place_actions("courtyard") if not a[0].startswith("path_")]`. Line 353: compare `[r for r in registered_place_actions("dorm") if not r[0].startswith("path_")]` with the same right-hand side.
- P5 or P8 (tools/smoke/p2_hud.rpy line 581, 1 failing check; proven 109/0 in a scratch copy): replace the condition with `if any(v[0] in ("act", "mission") for v in _zz_all if isinstance(v, tuple) and v not in _zz_got and not (v[0] == "act" and v[1] in hot_covers(_zz_loc))):`. P6's action hotspots will trip the same check.
- P8 (frozen game/sb_hotspots.rpy, screen hot_layer), to dim a locked exit; proven 7/0 in retry/patched/p9_dim_proof.rpy. After `$ _hot_ok = hot_open(_hot_h)` add `$ _hot_lock = path_locked(_hot_h["act"][5:]) if str(_hot_h["act"]).startswith("path_") else ""`; use `alpha=(1.0 if (_hot_ok and not _hot_lock) else 0.45)`; pass `(NullAction() if _hot_lock else hot_action(_hot_h))` as the button's action. In the same commit, make the dim destination icon the default: in game/room_paths.rpy delete class path_SpotRow and the line `HOT_SPOTS[-1] = path_SpotRow(HOT_SPOTS[-1], to=to)` in path_register, so a locked exit is the room's own icon at alpha 0.45 with the reason on hover. Then in tools/smoke/p2_paths.rpy: replace the NOTE 'a locked exit is not drawn dim' with a check; change the check 'it is drawn as the lock icon' to expect place_storehouse; in zz_row_reads() and its two checks expect the icons to be place_storehouse both locked and open; drop path_SpotRow from the 'no saved store variable holds a registry row' check and from zz_loop_save_names. Also reword path_exits' docstring line for `icon` (drop the words about "lock").
- New this round. P8 (frozen game/ui_icons.rpy, screen hover_label), so an exit's label opens under its icon and not over the exit to its left. After the two lines `if isinstance(_hover_tip, tuple) and len(_hover_tip) > 1 and str(_hover_tip[1]).startswith(("sample_auto_", "sample_always_", "sample_never_")):` / `$ _hover_side = "top"` add: `elif isinstance(_hover_tip, tuple) and len(_hover_tip) > 1 and str(_hover_tip[1]).startswith("hot_go_"):` / `$ _hover_side = "bottom"`. The key is right: icon_btn's tooltip key is its wid, and hot_layer passes wid="hot_" + id with exit ids go_<from>__<to>. Not run. After it, p2_paths' two hover checks (the girls' dormitory label hides no other exit; the courtyard gate label lies between x 1040 and 1300) need re-measuring, and the gate exit at y 985 needs room below it (the label would run past y 1080, so NearRect may fall back to another side). Or instead, when re-placing the hub exits on the painted pictures, keep at least 360 px of empty picture left of each exit.
- P8: exit rows in PLACE_ACTIONS and HOT_SPOTS read their label and icon live through row[key], row.get, row.items, row.values and row.copy; a dict(row) copy holds the label and icon of the moment it was made, so do not keep such a copy across a change of flags or period.
- P8 (sb_screens.rpy, AMBIENT) caption requests for D57: ("nobara", "training_yard"): ("on her way to the training hall", "neutral"); ("toge", "school_yard"): ("on the steps, onigiri in hand", "happy"); ("yuji", "dorm_yard"): ("on the garden wall, counting stars out loud", "happy"); ("megumi", "trailhead"): ("with a Divine Dog, heading up", "neutral"); ("shoko", "staff_yard"): ("on the steps with coffee", "neutral"). Until then the fallbacks show.
- New this round. If the owner wants Yuji outside by day: in game/sb_world.rpy set WEEKEND["yuji"]["Morning"] = "dorm_yard" (he is in dorm_common then; no written scene uses that slot), and change his AMBIENT request to ("on the garden wall, doing nothing loudly", "happy").
- P8 (sb_activities.rpy): 'Walk with them' is offered only at courtyard, gate, forest, riverside and ridge. Add the five hubs to its loc tuple if a walk should start from a yard.
- P5 (lighting.rpy): the hubs need no BG_LIGHT row; they are outdoor LOCATIONS and take OUTDOOR_LIGHT. Add PLACE_LIGHT rows only if the painted pictures call for them.
- P5: with wave 0's stage, top-row exits (y 272, x 850 to 1270) and exits at x 84 or x 1640 and above stay visible with up to three people; the courtyard's gate exit (1300, 985) stays in the picture with one or two people and moves to the column with three or more. If your slots, pose boxes or name tags change, re-check p2_paths' check 'with two people the gate exit is in the picture and its hover label is right of both name tags' (it assumes the second tag ends by x 1040).
- P6: exits are action hotspots with ids go_<from>__<to>, drawn at PATH_EXITS in room_paths.rpy. Keep your final points 120 px from them (the courtyard's gate exit is now at (1300, 985)). game/layout/hot_<place>.json can move an exit by its id; path_exits() reports the moved point and path_validate checks it against the caption box. Exit tiles come first among registered actions in the column (order 5).
- P8: once P6's final points and the five hub pictures are in, re-place the hub exits on natural spots with tools/layout_sheet.py hot_<hub>. Keep them out of PATH_CAPTION_BOX (40, 100, 744, 160): lint reports any that are not. Keep a room that can be locked (girls_dorm, office, utahime_office, gojo_office, storehouse) leftmost in its row or with empty picture to its left, because its hover label is up to 520 px wide and opens to the left; on the staff steps spread the three office doors so each has that room. Keep the courtyard's gate exit right of the name tags. tools/layout_sheet.py's STAND_INS table needs the five hub stand-ins (WORLD_HUB_STANDINS in sb_world.rpy).
- Orchestrator (art batch 3): `python3 tools/make_bg_workflow.py school_yard dorm_yard staff_yard training_yard trailhead --out phase2/hubs.json` writes ten pictures, about $0.35. Not run for real: it writes into ~/Desktop/JJK Game images and ~/ComfyUI-Shared/input.
- P8 (docs/PHASE2_DESIGN.md). (1) Section 2.3, add a row: `room_paths.rpy | label path_walk(path_to) with its line call rule_walk_to(path_to); every label sb_do_path_<to> with its line call path_walk("<to>")`. Saves made after an exit walk hold return sites in these. (2) D55: the action is path_<to> and its label sb_do_path_<to>; never rename the labels to go_<to>. (3) D54: the link list as built (courtyard to school_yard, dorm_yard, training_yard; dorm_yard to staff_yard, trailhead; staff_yard to training_yard), or the owner's ruling from checkpoint C. (4) D56: add the arrival caption box as a keep-clear zone. (5) Section 4.0, place view row: 4 object hotspots plus the place's exits (1 in a room, up to 7 in a hub; the Dormitory Garden has 7). (6) 4.0's level-2 map budget is 5 pins plus 5 buttons. (7) Record: path_locked, path_label, path_icon, path_words, path_is_hub, path_reach, path_LiveRow, PATH_HUBS, PATH_LINKS, PATH_EXITS, PATH_KEEP_CLEAR, PATH_CAPTION_BOX, PATH_ACTION_ORDER, map_pin_icon, map_area_rect, MAP_AREA_W/H, MAP_MOUNTAIN_BOX, WORLD_HUB_STANDINS, world_hub_standin, world_hub_bg. (8) LOCATIONS has 24 rows; tools/bgs/CAMPUS.md still says 'Classroom Building'.
- P8 (p2_saves): p2_paths section 10 saves, loads and rolls back through exit walks inside the real loop. p2_saves may still want the same on the merged tree with P5's stage and P6's hotspots in.
- If the owner wants the courtyard joined to the staff steps: add ("courtyard", "staff_yard") to PATH_LINKS, a ("staff_yard", x, y) row to PATH_EXITS["courtyard"] and a ("courtyard", x, y) row to PATH_EXITS["staff_yard"]; the labels already exist.
- All wave-2 packages: code that walks every place must read LOCATIONS or LOC_ORDER (24 entries). icon_for('place', hub) returns area_<key>; 'place_' + hub is not an icon name. A harness that keeps a PLACE_ACTIONS or HOT_SPOTS row in a store variable across statements carries it into any later save through the rollback log; read the rows inside a function or delete the variable in the same statement.

**Where it departs from the plan**
- A locked exit is not dim (D55): frozen hot_layer dims a hotspot only when the night closes it. It shows the lock icon, gives the reason on hover, and does nothing when clicked. The P8 edit is in the hand-offs.
- Action ids are path_<to> with labels sb_do_path_<to>, not D55's go_<to>: the prefix rule rejects sb_do_go_<to> in room_paths.rpy. Hotspot ids are D55's go_<from>__<to>.
- Hub links follow map_campus.png, not D54's list: staff_yard joins training_yard and dorm_yard, not the courtyard.
- The exit rows in PLACE_ACTIONS and HOT_SPOTS are dict subclasses (path_LiveRow, path_ActionRow, path_SpotRow) that read their label and icon when asked. Nothing is written to a registry at run time and nothing new reaches a save.
- room_paths.rpy adds rows to ICON_FOR at init (each exit action, each new hub).
- Exits come first among the registered place actions (order 5).
- Hub top rows sit at x 850 to 1270, y 272, with a lockable room leftmost, so the row order on screen is not the list order in PATH_EXITS.
- Changed this round: the courtyard's gate exit is at (1300, 985), well right of the flagstones' centre. It stays in the picture with one or two people and moves to the column with three or more.
- PATH_CAPTION_BOX is a keep-clear zone that the plan's D56 does not list.
- The Mountain Path and Training Yard descriptions are the round 2 story reviewer's wordings; the Mountain Path line differs from round 1's suggested text.
- On the five stand-in pictures the exits follow one plan rather than natural spots; they need re-placing once the hub pictures are painted.
- D57: Yuji's hub slot is Night, not Evening; the Staff Building Steps and the Mountain Path have someone at weekends only.
- D61: the People card's hover keeps 'Next: Spend time together / after roll call', as the NEXT row does.
- The hub stand-in table and builder live in sb_world.rpy (prefix rule); area markers use a new style map_area_marker (240 x 96); the heart keeps ['gate', 'courtyard'].

**Open**
- wp0_stubs (2 checks) and p2_hud (1 check) failed in this worktree on round 1's run and will fail on the merged tree until the hand-off edits are applied. Neither was re-run this round, nor were wp2, wp4 to wp7, wp9 to wp11, p2_gear and p2_night.
- A locked exit is the lock icon, not dim, until P8 edits hot_layer. On the Staff Building Steps at Night that is three identical locks in a row.
- In every hub, hovering a top-row exit puts its label over the exit to its left (14 pairs at Noon by the reviewer's sweep). Nothing is lost; the fix is the hover_label hand-off or the re-placing on painted pictures.
- The courtyard has no direct exit to the Staff Building Steps (two walks away). The owner has not ruled; a checkpoint C question.
- Four hubs show more than 4.0's four hotspots from exits alone (Dormitory Garden 7; School Courtyard, Staff Steps and Training Yard 5). Whether the garden keeps seven is a checkpoint C question.
- The five hubs show stand-in pictures, so their exits sit in a schematic row at the top right until art batch 3.
- A few room exits sit where the picture shows no door (infirmary, library, ridge, the end of the girls' dormitory corridor), and the courtyard's gate exit is now on the right side of the flagstones, at x 1300.
- Yuji stands in the Dormitory Garden only on weekday nights, with a fallback caption until P8 adds the AMBIENT row. The Staff Building Steps and the Mountain Path have a person at weekends only.
- p2_contracts' hover checks failed (126/3) while another Ren'Py window was open and passed 129/0 alone; expect the same on any crowded run. p2_paths now has two hover checks that need the pointer (the girls' dormitory label, the courtyard gate label); both passed on both runs here.
- The new gate-label check assumes wave 0's stage (second name tag ends by x 1040); P5's slots or tags may need the number changed.

**Findings left unfixed, with reasons**
- (not fixed) spec: carried from round 1: D54's courtyard-to-staff_yard link is not built; four hubs show 5 to 7 exits against 4.0's budget — No code change, by the reviewer's own advice. Both stay as checkpoint C questions in the owner note, open issues and hand-offs.
- (not fixed) play: in every hub, a top-row exit's hover label opens over the exit to its left — As advised, PATH_EXITS is not changed: the row is a stand-in plan until the hub pictures are painted, and the fix is in frozen game/ui_icons.rpy. The exact edit is in the P8 hand-offs. I confirmed the tooltip key of an exit is its widget id "hot_go_<from>__<to>" (icon_btn line 291), so the suggested test matches. The edit itself was not run.
- (not fixed) story: Yuji is in the Dormitory Garden only at Night on weekdays, so the owner may not see the example they asked for — No code change, as advised. The owner note now says when and where to see Yuji and Nobara; the weekend-morning alternative is in the hand-offs.

## Left after the trial merges (all minor; for P8)

- **frozen, game/ui_icons.rpy screen hover_label (preferred side), with P5's name tags:** Unchanged from pass 1. pass2/shots/p2_view/worst_sb_place.png: Megumi's tag label opens left and covers Yuji's name tag. walk_new_a/a_4_hover_tag.png: Nobara's opens left over empty floor. *Fix:* P8: in hover_label treat tooltip keys starting 'tag_' (and 'hud_') like the sample_ keys and open the label above the button.
- **frozen, tools/smoke/wp10_chapters.rpy:129-148, zz_wp10_text():** 149/1 once, 150/0 twice on this tree. The needle fires on a predicted line, so ch4_curse_reveal is pictured one scene early. Harness race, not the game. *Fix:* P8: first line of zz_wp10_text: `if renpy.predicting(): return _zz_wp10_prev_filter(s) if _zz_wp10_prev_filter else s`.
- **frozen, game/ui_hud.rpy toast lane on the place view against P5's slots:** Unchanged from pass 1. worst_sb_place.png: four two-line toasts end near y 397 and touch the top of Maki's hair at the right-hand slot. Only with four wrapped toasts; they fade. *Fix:* P8: cap the place-view stack at three when any toast wraps, or accept it. No P5 change.
- **frozen, game/sb_loop.rpy (call screen hides the place view before view_before_person runs):** d_02_person_first_tick.png and d_05_back_first_tick.png: both dissolves run between the bare room and the full view, so the other people and the HUD fade out and in rather than staying put. Right hour now; P5 listed this as an open issue. *Fix:* P8, only if the owner minds it at checkpoint C: show the person view from inside sb_place (or keep sb_place shown under sb_char) so the stage never leaves the screen. Otherwise accept.
- **P6, tools/smoke/p2_rooms.rpy lines 355, 361, 717 (six checks: 495, 516, 697, 706, 721, 729):** p2_rooms 117/6 on the merged tree. Each failing check compares the whole hotspot list of a room with P6's own set and now also sees P9's go_<from>__<to> exits; line 721 forbids any action hotspot in explore mode, which D55 requires of exits. Test-only: the game behaves as planned. *Fix:* Line 355: `return [h for h in HOT_SPOTS if not h["id"].startswith(("zz", "go_"))]`. Line 361: `return [h["id"] for h in hot_spots_for(loc) if not h["id"].startswith(("zz", "go_"))]`. Line 717: append `and not _zz_h["id"].startswith("go_")` to the comprehension's condition. Proven 123/0 in pass1/full/patched/p2_rooms.rpy.
- **P9, tools/smoke/p2_paths.rpy line 528 (and the NOTE at line 481):** p2_paths 102/1: 'in the evening the girls' dormitory exit reads its lock's reason'. The check still expects the locked exit to return ('act', 'path_girls_dorm'); with P9's own hot_layer edit applied it is NullAction. *Fix:* Line 528: replace `zz_action_value("hot_go_dorm_yard__girls_dorm") == ("act", "path_girls_dorm")` with `zz_action_value("hot_go_dorm_yard__girls_dorm") is None`; turn the NOTE 'a locked exit is not drawn dim' at line 481 into a check. Proven 103/0 in pass1/full/patched/p2_paths.rpy.
- **P9, game/room_paths.rpy PATH_EXITS['courtyard'] and PATH_KEEP_CLEAR:** The Training Yard exit (1640, 780) is 98 px from P6's final vending machine point (1600, 690): the two rings overlap by 6 px and the icons sit almost touching (walk_new_e/e1_courtyard_hov_spot_vend.png). PATH_KEEP_CLEAR still holds 4.10's start points, so P9's validator cannot see it; p2_paths only notes it. *Fix:* Move the exit to ("training_yard", 1640, 850) (165 px from the machine, clear of the column and the gate exit). Replace PATH_KEEP_CLEAR with P6's final points (courtyard (1600, 690); dorm (440, 590), (1330, 720); dorm_common (1400, 876), (1590, 560); riverside (1580, 905); library (300, 520), (1630, 480); classroom (1450, 500); cafeteria (1500, 600); infirmary (1420, 700); storehouse (1600, 600); utahime_office (1500, 470); ridge (960, 250)).
- **P9, game/room_paths.rpy PATH_EXITS['dorm']:** In My Room the exit at (150, 560) and the computer at (440, 590) are on one row. The exit's label 'To the Dormitory Garden' covers the top of the laptop icon, and the computer's label 'My computer / Look something up...' covers the lower half of the exit icon (walk_new_e/e00_dorm_hov_go_dorm__dorm_yard.png, e00_dorm_hov_computer.png). Both stay clickable. *Fix:* Move the exit down the same door: ("dorm_yard", 150, 760). Its label then spans about y 724 to 772, below the computer's ring (542 to 638), and the computer's label no longer reaches it.
- **P9, game/room_paths.rpy, the leftmost top-row exit of each hub (850, 272):** For the first seconds in a hub the arrival caption is up; hovering the leftmost exit while it is locked opens a two-line reason to the left that covers the caption's last line (walk_new_e/e2_locked_storehouse.png: 'The storehouse is sealed...' over 'usually hear this place before I see it.'). Same geometry for the girls' dormitory and Utahime's office. *Fix:* Put the lockable exits at the right end of the top row (x 1270) so their label opens over empty picture, or lower the hubs' top row to y 300. Either is a PATH_EXITS edit only.
- **P9, game/sb_world.rpy schedule (D57), School Courtyard:** walk_new_h and walk_save_h: school_yard on a weekday Afternoon has nobody; 'roster has toge: False'. Toge is the hub's only resident, and he is not met in a new game or in the owner's campus save, so that hub is empty through the first week. *Fix:* Give the School Courtyard a first-year as well, at an hour that moves no scene (owner's choice of who), or accept it as is until the second-years are met. One schedule row.
- **P9, game/ui_journal.rpy jr_records (the Me page's Records):** Before I have ever fished, Records shows THE RECORD BOOK with seven 'not caught yet' lines (walk_new_f f00 jr_records). fish_records() always returns seven rows by contract, so jr_records' 'leave an empty section out' rule never fires for it. ui_journal.rpy is P9's this wave for D61 only; P8 may be the right hand. *Fix:* In jr_records, build the record-book section only when something is caught: `if lines and any(isinstance(r, (tuple, list)) and len(r) >= 2 and r[1] for r in fish):` before `out.append(("THE RECORD BOOK", lines))`.

## The checkpoint C note the trial checker wrote for the owner

Walk it: in My Room click the door icon on the left, then keep clicking icons in the picture: Dormitory Garden, Courtyard, Training Yard, Training Hall. No map, no time spent. At the gate, the icon above the torii leads up to the courtyard.
Common room in the evening: three people stand in the room with shadows and evening light, one behind the table. Click someone and watch the view ease in, then back.
My Room: click the laptop. Read a few pages, then "Posted assignments" and cross-check the board (your campus save has the board open; a brand-new game does not yet). The lead shows in the journal's Missions tab until you read the page.
Riverside: the fishing icon on the flat rock. Click the water when the white marker is in the green. Say if it feels too fast or slow; nobody has tuned it by hand.
Library: the shelves on the left (one hour, three shelves). Courtyard: the vending machine icon on the right porch (¥150, once a day).
Card table: with ¥100 and someone in the common room, play blackjack and a hand of poker; watch their faces. With three people in the room the table icon moves to the right-hand column.
People in the yards: Nobara in the Training Yard on weekday mornings, Yuji in the Dormitory Garden at night, Megumi on the Mountain Path and Shoko on the Staff Building Steps on Saturdays. The School Courtyard stays empty until you meet Toge.
Known placeholders: the five yards use tinted cut-outs of the courtyard and forest, with exits in a plain row along the top; the courtyard picture has no vending machine painted in; the fishing float and bar are plain shapes; poses and Yuji's blink wait for art batch 3.
Small things you may notice: in the courtyard the vending machine and the Training Yard exit sit almost touching; in My Room the door's and the laptop's hover labels cover each other a little. Both are one-line moves.
Locked doors are dimmed, say why when you hover, and do nothing when clicked.


## From art batch 3 (5 Oct 2026), for P8

- **`tools/install_pose.py`, `fit()`:** it centre-crops the 2752x1536 render, but the editor scales the room to the render's width, so everything lands 6 to 7 px off at the edges and the tool reports 11 to 12% "changed" with thousands of changed blocks outside the largest region. Both batch-3 poses were installed from width-fitted copies instead (1920x1072 placed at y=4), which align exactly (4.0% and 1.7% changed). Make `fit()` scale to width and pad or crop the height, and re-check against the two installed poses.
- **`tools/install_pose.py`, the auto box:** on Nobara's sofa pose it missed her feet; she was installed with `--box 248,408,632,536`, leaving out her painted floor shadow. Check the box rule against a seated pose.
- **`game/room_paths.rpy`, `PATH_EXITS`:** the five hubs now have real backgrounds (`school_yard`, `dorm_yard`, `staff_yard`, `training_yard`, `trailhead`), but their exits still sit in the stand-in's plain row along the top. Move each exit onto the door, steps or path it leads to, with `tools/layout_sheet.py`.
- **Utahime's pose:** her scar is faint in both candidates; the desk foreground hides her feet and the lower edge of her hands. For the owner to judge at checkpoint C.
- **Pose candidates in the workflow are stacked (A above B), not side by side;** the hand-off note for batch 4 should say "top" and "bottom".

---

# P8: where the record went (5 Oct 2026)

*Written by P8's docs group. Nothing below is new work for a wave: it says where each thing above ended up, for phases 3 and 4.*

- **The plan is now as built.** `docs/PHASE2_DESIGN.md` carries every departure listed in this file, in the section it belongs to, in a sentence or block marked **As built**. Where the two still disagree about what was built, the code is right.
- **What was put off** is in the plan's section 11, under its phase: phase 3 (a save test inside a fight; yen balance), phase 4 (the Inverted Spear's `sealed` field, a ridge caption for Gojo, the placeholder night scenes and district pins, a caption test for poses, cafeteria staging, the computer pages' lore, `pc_request` for mission authors, Night beats that roll the day), and a list for the owner's review after the phase.
- **The owner's checklist** for checkpoint D is `docs/PLAYTEST.md`: the play-through, every stand-in, the five rulings as built, what was chosen and what the owner said at A, B and C, and the questions still open.
- **The art still to make** (twelve poses, blink and talk for ten, foregrounds) is `docs/ART_PHASE2.md`, as numbered steps with the prices the tools print.
- **The tools and harnesses** of phase 2 are in `tools/README.md`; the systems in `README.md`.
- **The save reference** is `docs/load_report_phase2.txt` (the owner's eleven slots, which are also the checkpoint saves). The three per-wave reports are kept as history.
- **Not settled by P8, for the owner:** `gen_gui.py --all` is unverified (no Pillow on this Mac); `build.version` in `game/options.rpy` still reads "0.3" (only `config.version` was asked for; it names the build folder).

## P8: what the final merge closed (5 Oct 2026)

*Written by P8's integrator on the merged tree. Each line closes something listed above.*

- **Hover labels** (P5's hand-off and its "not fixed" line; trial-merge bullet on the leftmost hub exit): the side comes from the tooltip key (`ICON_TIP_SIDES`, `icon_tip_side`, `game/ui_icons.rpy`). Name tags and exits open above, so the line asking to keep a lockable exit leftmost "because the label opens to the left" no longer applies. Two rows depend on where things stand today: `hot_go_courtyard__training_yard` (left) and `hot_computer` (top); re-check them if those spots move.
- **Hub exits** (art batch 3; P9's hand-off): they sit on the painted yards. Two points differ from the triage's: `dorm_yard` → `girls_dorm` (1530, 600) and `training_yard` → `staff_yard` (620, 560, left of the kura). `PATH_KEEP_CLEAR` holds P6's final points. A locked exit stays a dim lock icon (the "dim room icon" proposal was not taken). An exit a person stands in front of moves to the icon column, like any hotspot.
- **The toast lane** (P2's hand-off, line "HOT_LANES"): `HOT_LANES` is `(1330, 92, 460, 330)` and `TOAST_LANE` is `(1330, 92, 1790, 422)`. Toasts wait while a choice menu is up; over the place view three show while one of them wraps (`toast_wraps`).
- **The five yard captions** (P9's hand-off) are in `AMBIENT`; Yuji's is "by the pond, counting stars out loud". A `NIGHT_OK` action at Night shows no diamond and no "1 period". `stage_x` answers with the row's own x.
- **A Night beat that rolls the day** (P4b's note): the loop asks `night_pending()` again right after `play_event`, so the walk home is not one action late; `p2_night.rpy` section E plays it.
- **The journal** (P4a open issue 1; P3's "jr_wear may take off a later talisman"; P4b's "Control 46 · cap 40"; trial-merge bullet 11): closed. The rows read "Control 46  · cap 40, +6 from the ridge" and "Cursed energy 103 / 103  · cap 100, +3 from the ridge". The record book is listed on the Me page from the first catch on.
- **The night out** (wave 1's "wrong picture behind the night-out menu"; P4b's "toasts land on the market" and "requirement chips"; 7.3's deferred line): closed; checked in `p2_night.rpy` section K, `p2_gear.rpy` and at the end of `phase2_all.rpy`.
- **The baselines** (`tools/smoke/baseline_globals.txt`, `baseline_check_content.txt`) were rewritten at the end of the phase: five stale rows went (screen `jr_memories_tab`, store `char_focus`, and `g`, `m`, `r` of `sb_missions.rpy`), 1,197 phase-2 names came in, and the findings stayed at 102.
- **Still open, for the owner or phase 3:** with seven or more people in the Common Room the "+N" chip's list would cover the card table (the schedule puts five there at most; `p2_rooms.rpy` notes the rectangles on every run). `p2_saves.rpy` does not save inside a fight or on the grade card, and loads no save made by the pre-phase-2 tree itself: the owner's eleven slots (`tools/load_all_saves.sh`) stand in for those.

## P8: after the review (5 Oct 2026)

*Written by P8's integrator after the review round. What was changed, and what stays open.*

- **`tools/smoke/p2_contracts.rpy` is the wave-0 file again,** byte for byte (plan section 7, P8's acceptance). The check that the banner does not wait for the arrival caption under `zz_worst` moved to `tools/smoke/p2_hud.rpy`; `fixture()` refusing `cards_sit` was already covered by the frozen check (`_zz_refused == list(ZZ_SHAPED)`).
- **`p2_saves.rpy`** gained the save on `night_carry_home`'s line and three rollbacks: through a market purchase, from "Day N. Morning." back through `new_day()`, and from the place view back onto the carry line. **`p2_oldsave.rpy`** is new: it loads one of the owner's slots (`SMOKE_SAVES=1 SMOKE_SLOT=1-1`), plays it on for a day and saves and loads on the place view, the map, the person view and the journal.
- **Not built, for the owner to accept or phase 3:** a save made by the tree as it was before phase 2 while parked on `call screen sb_map`, or just before `view_sync_light`. Nobody holds such a save: slot 1-1 is the one slot from before phase 2 and it is parked on the place view. `docs/PLAYTEST.md` asks the owner whether the eleven slots are enough. A save inside `combat_screen` or on the grade card stays with phase 3 (plan section 11).
- **`label night_out`** sets the district picture twice: before the arrival menu, and again after the "Head home" block. The second repairs a save made on that menu by a tree older than P8, which still holds the campus room.
- **Map pins:** a room pin's hover label is centred above its pin (`ICON_TIP_CENTRED`). Seven rows of `ICON_TIP_SIDES` name the pins that have another pin above them (the three yard pins left, the Mountain Path right, the Common Room, the Storehouse and the Library below). They depend on `game/layout/area_*.json` as it is today; `p2_map.rpy` hovers every pin of the five areas it does not overlay and fails if a label meets another pin. The School Building is measured under the harness's own test sidecar and only noted there.
- **The courtyard's Dormitory Garden exit** is at (960, 310), clear of a two-line banner.
- **`p2_view.rpy`'s label check** moves the pointer over each person (a sprite has no rectangle under `renpy.set_focus`) and fails on a label that is not beside its person.
- **Open, hover only, for the owner (asked in `docs/PLAYTEST.md`):**
  - A column tile's label opens to the left over whatever stands beside the column: in the Courtyard the Practice tile's label hides the Training Yard exit at (1640, 850); the same over the Library's exit and the Riverside's bank. No point on the right-hand porch is clear of both the vending machine and the column's labels, so `PATH_EXITS` is unchanged. The fix, if wanted, is in `hover_label`: open the first `rail_` tile's label above.
  - The "+N" chip: with five people in the Common Room in the evening Panda's name label is drawn over the "+1 / Toge" chip, and the chip sits on Panda's feet; with seven or more its list would cover the card table. One decision covers both: move `RAIL_MORE_POS` (today (1400, 1040), `game/sb_screens.rpy`) clear of the last stage slot and re-run `p2_hud`, `p2_view` and `p2_rooms`.
- **Hover checks** that need the pointer are now in five harnesses: `p2_contracts`, `p2_hud`, `p2_map`, `p2_paths`, `p2_view`.

## P8: round 3 (5 Oct 2026)

*Written by P8's integrator after the second review. No game file changed in this round.*

- **Docs only:** `docs/ART_PHASE2.md` (batch 4, step 8) no longer asks for a hand-made width fit, since `tools/install_pose.py` fits the render itself; `docs/PLAYTEST.md` part 3 names the hour each yard person stands there.
- **Exit labels, as built: above the icon.** Triage items w2-P5-01, w2-P9-02 and tm-09 said "under the icon"; the plan's 4.3 and the lines above record the departure, and `p2_paths.rpy` measures the labels as drawn.
- **`build.version`** stays "0.3" until the owner says otherwise (it names the build folder only; no save depends on it).
- **Save tests still open, for phase 3:** parks `combat` and `grade_card` in `p2_saves.rpy` on the `zzs_park` pattern, when the fight is rebuilt. A pre-phase-2 save parked on the map does not exist to test.
- **One run to watch:** `p2_oldsave.rpy` on slot auto-10 (a prologue save) once ended after 3 s with "the harness returned without calling finish()"; the same slot passed 14 of 14 on the two runs after it and on the earlier round. Nothing was raised and the slot loads SAME; treat a single such result as the harness's timing and run it again.

## After checkpoint D (5 Oct 2026)

*Written by the builder of the "D notes" package, after the owner played checkpoint D ("checkpoint D plays fine, open the PR"). Each line closes something listed above; the older lines stand as written. The owner's words and how they were read are in `docs/PHASE2_UI_OVERHAUL.md`, section 5.*

- **The Common Room in the evening is the first years'** (closes "the schedule puts five there at most" and the "+N chip ... five people in the Common Room in the evening" item). `SCHEDULE["panda"]["Evening"]` and `SCHEDULE["toge"]["Evening"]` are `"library"` (`game/sb_world.rpy`); `WEEKEND` has no Evening cell for either, so all seven days follow. By the routine the room now holds Yuji, Megumi and Nobara on a weekday evening and Megumi alone at the weekend. No teacher or staff member was ever scheduled there, `GOJO_SPOTS` does not hold it, `FLAG_SCHEDULES` is empty and no story pin places anyone there. A companion still enters with me (`who_is_here` adds whoever is tagging along): that is the game's rule, not the schedule.
- **Why the Library.** "Study together" is offered only in the classroom, the Common Room, my room and the Library, and the night rule closes it at Night, so the Common Room in the Evening was the only hour it could be asked of Panda or Toge without "Ask them along". The Library keeps it for both (`p2_paths.rpy`'s "nobody who moved lost an activity" check now lists the two). Nobody else is in the Library in the Evening; with the two of them no exit, hotspot or pose is covered. A yard was weighed (the owner's wish at B for people outside) and not taken, because each yard loses the study offer: it is put to the owner in `docs/PLAYTEST.md`.
- **Captions.** `AMBIENT` gained `("panda", "library")` "turning pages very carefully" and `("toge", "library")` "a book open, hands in his sleeves". `AMBIENT_STORY` gained a thirteenth row, `("panda", "library", "thread:panda:1", "a bag of crisps open under the table")`, so the crisps of his thread's first line still show in the evening; the Common Room row stays for his Night slot and for when he is brought along, and its caption was reworded from "sharing out a bag of crisps" to "a bag of crisps open beside him", because by the routine he is now alone whenever it shows (round 1 of the review). His "something true" memory, "The Boy in the Car", is still set in the Common Room in the Evening (`sb_memories.rpy`: the replay's backdrop and the tile's picture only); whether it moves to the Library is put to the owner. Nothing else needed a word changed: no `ev()` row has both a person and a place, the memory rows only set where a replay stands, and the journal's "Usually" and "Next" lines and the map's faces are computed from the schedule.
- **The card table** seats whoever is in the Common Room, so Panda and Toge sit only when brought along, as Maki, Shoko, Gojo and Yaga already do. It still opens with the first years (weekdays) or Megumi (weekends). What follows from the rules in `room_cards.rpy` (`cards_opponents`, `cards_ok`): a weekday evening now gives one sitting where five people gave two (three, then the two not yet played), the weekend table seats Megumi alone where it sat Megumi, Panda and Toge, and since cards are closed at Night, Panda's and Toge's card faces and lines are seen only through "Ask them along", one of them at a time. Put to the owner in `docs/PLAYTEST.md`.
- **Old saves.** A save on the place view in the Common Room in the Evening rebuilds from the schedule. A save in Panda's or Toge's person view there shows them once more, then the room without them. No say, menu, call or label was touched; the eleven slots load SAME.
- **Not changed: Panda's Night slot** (Common Room, alone) and **`RAIL_MORE_POS`** (1400, 1040). Both are with the owner (`docs/PLAYTEST.md`, "After D").
- **Where five still stand together, measured.** By the routine (Gojo not counted): the Cafeteria at Noon on weekdays and at weekends (Yuji, Megumi, Nobara, Panda on stage; Toge on the "+1" chip), and the Riverside on a weekend Afternoon (Yuji, Nobara, Maki, Panda; Toge on the chip). In all three, as drawn: the chip's name button is at x 1400 to 1480, y 1002 to 1040; the fourth person (Panda) ends at about x 1273 in the Cafeteria and x 1350 at the Riverside; the chip stands on nobody, and no name tag's hover label meets the chip (each opens above its own tag, x 1002 to 1158 in the Cafeteria and x 1087 to 1243 at the Riverside for Panda). The chip's own name label opens to its left at y 1002 while the pointer rests on it: x 1291 to 1400 in the Cafeteria, short of Panda's drawn foot, and x 1224 to 1400 at the Riverside, over Panda's right foot. Screenshots were read for all three. `wp1_world.rpy` now fails if the list of five-person hours changes. With seven or more in the Common Room the chip's list would still cover the card table; nothing in play puts seven there now (the routine gives three at most in the Evening and a companion adds one); it would take a later schedule change or a story pin.
- **The icon column's label** (closes "A column tile's label opens to the left ... The fix, if wanted, is in `hover_label`: open the first `rail_` tile's label above"). That fix alone was measured and is not enough: in the Courtyard it clears Practice, but in the Library the top tile's label opened above still lands on the exit, and at the Riverside the tiles that hide the bank are the second and third. A fourth everyday case was found on the way: in the School Courtyard at Night, "Go to bed" (the bottom tile) hid the Courtyard exit. The rule as built (`icon_tip_place`, `icon_tip_spot`, `icon_tip_blocks`, `icon_tip_size`, `icon_tip_column` in `game/ui_icons.rpy`): the top tile of a column opens its label above the tile, right edges together, when that rectangle is clear; otherwise, and for every other tile, the label stays beside the column and moves up or down to the nearest height where it is clear. "Clear" means off every exit and hotspot showing in the place (their 72 px buttons, `hot_spots_for`), off the screen's top right corner down to the foot of the toast lane (the toasts and the corner buttons), and on screen. `icon_tip_side` and `ICON_TIP_SIDES` are unchanged (a `rail_` key still answers "left"); the "+N" chip's names (`rail_more_`) are not tiles and open as before; the tooltip is still `(text, key)` (D11) and `hover_label` is still the one screen that draws labels. The label's measures became named values (`ICON_TIP_W`, `ICON_TIP_PAD`, `ICON_TIP_TEXT`, `ICON_TIP_GAP`), the same numbers as before, so the screen and the measuring agree.
- **How it is checked.** `p2_hud.rpy` section 3b: the rule over 3,840 states (every place and period, both fixtures, a weekday and a Saturday, a rest day, Hold used, a companion: 8,164 tiles, the furthest move 100 px); then, as drawn, every place at every period on a weekday and a Saturday with the pointer resting on each tile (a column drawn again over the very same exits and hotspots is hovered once); then the Courtyard's Practice (above), the Library's Hold the hour (30 px down), the Riverside's Train (13 px up) and Hold the hour (55 px down) and the School Courtyard's Go to bed, with screenshots `column_label_*.png`. The buttons are measured, not their 96 px glow: in the Courtyard the label above Practice sits between the vending machine and the Training Yard exit touching the vending machine's lower edge (0 px: the label's top and the button's foot are both y 726) and 10 px above the Training Yard exit, over the edge of both glows. Touching counts as clear (`hot_overlap` is a strict test).
- **`build.version` is "0.4"** (closes the two lines saying it still reads "0.3"). Only Ren'Py's build code reads it: the folder, archive and "-dists" folder names (`CursedBonds-0.4`), the version line a built copy writes at the top of its log, and the updater's label (not used). No save, persistent data, harness or tool reads it. A save stores `config.version` and lives under `config.save_directory`; `tools/smoke.sh` and `tools/load_all_saves.sh` read only `config.save_directory`; no harness, tool or screen reads `build.version`. `core_flow.rpy` pins it.
- **Old saves: left for now,** the owner's word (closes "`docs/PLAYTEST.md` asks the owner whether the eleven slots are enough"). A pre-phase-2 save parked on the map, and saves inside a fight or on the grade card, stay where the lines above put them (phase 3).
- **Harnesses changed:** `wp1_world.rpy` 151 → 155 (the frozen schedule copy follows the two cells; four new checks: seven days, the tables, the two new places, the five-person hours); `wp7_ui.rpy` 143 → 146 (the schedule gives three; Panda and Toge are pinned in as a fixture for the four-people and "+1" views); `core_flow.rpy` 25 → 26; `p2_hud.rpy` 118 → 129 (section 3b; thirteen `AMBIENT_STORY` rows; about 115 s); `p2_paths.rpy` 109 (its moved-people list gained the two). `p2_contracts.rpy` is untouched, byte for byte, and passes 129.
- **Open, small, outside the four notes:** (1) a column label can sit edge to edge with a button, nothing hidden: the Courtyard (Practice, opened above, under the vending machine), the Library (Hold the hour, under the exit), the Riverside (Train on top of the bank's icon, Hold the hour under it) and the Staff Building yard (Hold the hour, under the Training Yard exit, not moved at all). A margin is one line in `icon_tip_spot`, but it belongs only in the beside-the-column search: applied to the "above" test as well, even 1 px stops Practice opening above in the Courtyard, against the owner's word. (1b) The move beside the column has no limit, so a label moved more than about 70 px stands level with the next tile: School Courtyard at Night with a companion, "Go to bed" 100 px down, beside "Let them go"; at the Riverside on a weekend afternoon the Mountain Path tile's label straddles its tile and Wait. The hovered tile is lit and nothing is hidden. When missions are given in the yards (phase 3; none is today) a wide mission label could move much further: cap the move then, or let such a label open above and to the left. (2) In the Common Room in the evening the third first year (Megumi) stands in front of the card table and the television, so "Play cards" is in the column and the TV look is hidden. With exactly three on stage the third slot is at x 1400 (`VIEW_SLOTS`, `view_stage.rpy`), in front of both icons; with four the slots were further left and both showed. Before the change three stood there only on weekend evenings; now it is every weekday evening. No slot was moved (that would be a new number); it is put to the owner. (3) A column label can still lie over a person standing near the column, or over the "+N" chip; the owner's note named exits and things to click. (4) In the person view the choice buttons' labels open to the left, over the person in focus. (5) Panda's journal line says he does welfare checks at eight in the evening with crisps (`sb_threads.rpy`); in the Library at that hour he reads, with the crisps under the table. The yard option would show the rounds; the owner has that to weigh.
