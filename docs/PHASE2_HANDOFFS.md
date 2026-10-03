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
