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
