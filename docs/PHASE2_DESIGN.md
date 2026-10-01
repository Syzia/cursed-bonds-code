# Phase 2 design: the UI overhaul

*Jujutsu Kaisen: Cursed Bonds · build plan · written 1 Oct 2026 against branch `phase2` (65b98f6). Scope and the owner's answers: `docs/PHASE2_UI_OVERHAUL.md` ("SCOPE"; its section 5 wins over everything here). Phase 1's rules: `docs/PHASE1_DESIGN.md` ("PHASE1") sections 2, 6, 7, 8, 10. Paths are relative to `/Users/hunterjolly/Desktop/JJKgame.md/`. Line numbers are today's.*

This plan starts from the winning design ("evolve in place": screens keep their names and return values, the loop keeps its shape, no save migration) and folds in what the three judges asked for from the other two. Every graft, flaw and gap they raised is a numbered decision in section 1. It was then put through an adversarial review (coverage, feasibility, packages); what that changed is listed in 12.5. A verification pass then checked the revision against the code and against itself; what it changed is listed in 12.6.

"Decision D20" and the like are the numbered rows of section 1.

---

## 0. What phase 2 changes, in plain words

**What you will notice when you play**

- **The map is calm.** It opens on "Jujutsu High", written once at the top, with six big area markers and nothing else. Each marker shows up to three faces of the people there (then "+2") and a gold mark if a mission is waiting. Click an area and the view moves in to that area's own picture, with its rooms on it as icons. Clicking an area only looks at it; I move when I pick a room (two clicks to anywhere). Tokyo works the same way: districts first, then the district. Walking is still free.
- **The row of faces is gone from the map.** Each person's journal page says where they are right now and what they're doing, with a "Go there" button. The People tab shows everyone's place at a glance.
- **Words become icons.** Map, Journal and Menu stay in their corner, as icons. What you can do in a room is a column of icons down the right edge. Rest the pointer on any icon and its name, and what it costs, appears beside it. Until the real icon pictures exist, each icon keeps its word underneath so nothing is a mystery.
- **The journal has five tabs.** Memories moved into People. A person's page has three parts: right now, their story (for Nobara, *Somebody Remembered* and her missions as one list of chapters, with the next step spelled out), and every scene you've shared, replayable. A scene with three people in it shows on all three pages. A "Me" card comes first: the main story by act, and the scenes nobody else is in.
- **Clicking a person shows less:** their grade and three or four choices, each with an icon. No name, no diamonds, no bars, no "Closer" line.
- **Grades have colours everywhere:** Grade 4 green, Grade 3 blue, Grade 2 purple, Grade 1 and Semi-Grade 1 red, Special Grade a slow oil-slick sheen. Gojo's chip shimmers. Tools and talismans too.
- **The armory shows a checklist** under each tool: what it asks of me, ticked or not. The Inverted Spear of Heaven shows four boxes, all empty. Talismans get the same checklist, in the journal's Equipment and Inventory tabs and at the Black Market.
- **Night has a rule.** Night is the last hour. I can still walk, talk, eat, use my computer and look at things, but anything that takes time is closed (the card table too), and Wait becomes "Go to bed": I walk to my room, sleep, and wake there. Exceptions, each with a price:
  - a rare night of training with Gojo on the ridge, announced that morning. It always gives more Control and more reserve than training every hour of that day would have, Gojo's own lesson included (the game works the number out from its own training rules). The next day I can't start missions, board jobs or any training, alone or with someone;
  - a night in Tokyo (Shibuya from the first ride; Shinjuku once I'm Grade 2). Once there I choose: the club (¥1,500 at the door), the Black Market (once I've found it), or head home. Staying out, at either, means I wake with half my stamina and less cursed energy;
  - the Black Market, found on the first Shibuya club night (or from a rumour on my computer). It sells four talismans of its own, sealing talismans and first aid, for a lot of yen;
  - story scenes that happen at night (stargazing, the late scenes with someone close) still happen.
- **Rooms have things in them.** Small glowing icons on objects:
  - the computer in my room is a small fake internet: a folklore wiki, a rumour blog, the school intranet, a genealogy site and an urban-legends board, with pages on Sukuna, Gojo, cursed techniques and the Gojo, Kamo and Zen'in clans. It can also cross-check this week's board jobs and flag one that "doesn't add up". When the story gives me something to look up, it shows in the journal's Missions tab as a lead ("Look up what was on the ridge — my computer"); one lead ships;
  - the card table in the common room: blackjack and poker for yen against whoever is there. Each person plays in character, and their face is the tell;
  - fishing at the riverside: three casts, a timing bar, a record book, one legendary fish in the evening, and now and then something cursed on the line;
  - the Library, a new room in the School Building, the best place to study;
  - a vending machine, the common-room TV, the blackboard.
- **People stop looking pasted on.** They cast a shadow you can see, take the room's light, stand at slightly different depths, breathe, and stand behind table edges. Click someone and the view eases in while they turn to you; it eases back when you leave. As you make the pictures, each person is painted into their place doing what the caption says.
- **The SKIPPING tag** no longer sits on the map and journal headers, and reward pop-ups no longer cover the journal, the board, the armory or the map.

**What isn't there yet**

- **After the first package the game looks almost the same.** That is expected: it lays the wiring. The only things to see at checkpoint A are the SKIPPING fix, the style sample, an empty Library on the old map, and the character scenes waiting for roll call.
- **Pictures arrive as you make them.** Until then: area maps are enlarged pieces of the campus map (blurry), icons are kanji seals with their word underneath, the Library borrows the classroom, people use their standing sprites. Every picture drops in by filename; nothing in the script changes.
- **Tools and talismans still don't do anything in a fight.** That is phase 3. "More depth" in this phase means requirements; what a tool *does* arrives with combat. None of the Inverted Spear's four boxes can be ticked before Arc Two.
- **No mission is locked behind the computer yet.** Locking an existing mission would trap progress in your old saves, so today's lead is optional. Story missions that *require* research arrive with the story (phase 4); the hook for them is built.
- **No Special Grade talisman is for sale.** The three unsealed ones stay what phase 1 made them: rewards at the end of Gojo's story, Todo's story and Act V.
- **Tokyo's daytime places** are pins that say "later build". The night in Tokyo and the Gojo night are short placeholder scenes.
- **Outfits** at the Black Market are an empty shelf until there is sprite art.
- **The early character scenes still narrate in "you".** They now wait until after roll call. Converting them is phase 4.
- **Chess, memory and tic-tac-toe** are not built; adding one later is one new file.
- **Sana and Kaito don't blink.** Kaito is never on screen; Sana is only in the prologue. Adding her later is two pictures ($0.64) and no script change.
- **If credits run short,** the first things to wait are poker, then the Black Market. You'll be asked before either is dropped; nothing you decided is cut without your say.

**Five things for you to decide at checkpoint A** (each has a default that is built unless you say otherwise):

1. **The night rule's strictness** (decision D20 in section 1). Default: at Night nothing that takes time is allowed except the listed exceptions. The alternative: Night stays usable and Kaito just wakes in his room afterwards.
2. **When the character scenes start** (D25). Default: after roll call (day 2). The alternative: after the Sun Mall (about day 4 or later), which keeps "you" narration further from the prologue but leaves the first days with no bond scenes.
3. **Two-hour activities** (D26). Default: if a story scene is waiting, a trip into town with someone, a day off together or the Tokyo trip ends an hour early so the scene isn't pushed to tomorrow, and the hour isn't lost. (A spar is one hour and is never cut short.) The alternative: leave it as it is (the scene comes a day late).
4. **The look of the icons and grade chips,** from a sample screen in the review tools (D7, D15). The Special Grade sheen is already on that sample.
5. **The Gojo night and my grade's ceiling** (D23). Default: the night never pushes Control past my grade's ceiling, and it is only offered when there is room under the ceiling for it to beat a full day. **That makes it rarer than it sounds.** A promotion lifts the ceiling by 15, and a full day of training is worth up to 23, so a player who keeps Control close to the ceiling gets no Gojo night at Grade 4, Grade 3 or Grade 2, promotion or not; it only comes back at Semi-Grade 1. (In numbers: it is offered at Grade 4 while Control is 16 or less, at Grade 3 up to 31, at Grade 2 up to 52, at Semi-Grade 1 up to 72.) The alternative: let that one night push Control up to 6 past the ceiling, so it is offered at every grade whenever it is due. It is one number (`past_cap`).

**Things chosen for you; say the word and any of them changes** (every number is one table entry; you'll be asked about these at checkpoints B and C):

- **Fishing** (D33) is the proposal you asked for: three casts an hour, a timing bar, six species with a record book, one legendary fish in the evening, a cursed catch about once a week.
- **The computer** (D31): five sites, twelve pages, and the weekly board cross-check.
- **Cards** (D32): stakes of ¥100 / ¥500 / ¥1,000; a sitting is five hands at most; at most ¥6,000 won in a day; closed at Night.
- **The Gojo night** (D23): whatever a full day of training would have given (the lesson, four sessions on the ridge and Hold the hour), plus 6 Control and 3 reserve; at most once every 10 days. From Control 30 that is +29 Control and +12 reserve, against a best day's +23 and +9. Whether it may pass my grade's ceiling is ruling 5 above.
- **The day after a Gojo night:** Train, Practice, "Train together", Gojo's lesson, Hold the hour and swimming are all closed. Studying, eating, talking, cards, fishing and the computer stay, but nothing raises Control or Output that day: the Library's barrier-craft shelf gives only its Insight, and the first fish of the day gives no Control.
- **The night in Tokyo** (D24): ¥1,500 for the club; half stamina and 70% cursed energy the next morning; not two nights running. Visiting only the market still costs the morning, not the ¥1,500.
- **Market prices:** ¥9,000 to ¥45,000 for its four talismans. **No Special Grade talisman is sold there** (the owner's answer, 1 Oct 2026: none for now; more talismans will be added later).
- **The map moves me on the second click,** not the first (your note said "once you go to that area"; a click on an area only opens it).
- **Small things:** Library study gives Insight +4 (a desk gives +3); the vending machine is ¥150 for 10 stamina, once a day.

**Art you'll make:** about 47 pictures, about $12.50 in all (the ten backgrounds use the cheaper background tool), in five small batches, each a drag-in file with numbered steps. The first batch is about $1.45. Nothing waits for any of it.

---

## 1. Decisions

"From" says where the idea came from: E, S, D are the three designs; J-owner, J-tech, J-build are the judges. "Pkg" is the package that builds it.

### The map

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D1 | The map always opens on the six areas, with "YOU ARE HERE" on mine. Clicking an area opens that area's view inside the same screen (a screen variable); I move only when a room is picked, which returns the existing `("go", loc)`. Esc: area → areas → close. This differs from SCOPE 2.A's wording ("choosing an area takes you there"); section 0 flags it for the owner. | SCOPE 2.A. `here` must stay a room; `call screen sb_map` is protected text. Two clicks to anywhere. (E, D; J-owner graft over S's area-first opening.) | P1 |
| D2 | The six areas keep their keys. `school` is renamed "School Building" and gains `library`. | Keys are in saves, schedules and missions. | P1 |
| D3 | Rooms on the area view are icon pins (a 72 px disc with the room's icon, the name on a plate under it, up to three faces), not text rows. Area markers on level 1 also stop at three faces and "+n" (18 faces at most on the map; the owner's page 5 note is about faces crowding). | J-owner: text rows broke SCOPE 2.B. (S) | P1 |
| D4 | Tokyo's second level: a district opens its own view with display-only pins ("Later build") and one "Ride with Ijichi" button returning the existing `("district", key)`. At Evening and Night it also offers "A night in [district]" (new return `("night", key)`). **Cuttable.** | Same shape as campus. | P1 |
| D5 | Pin positions, hotspot points, stage slots and pose boxes have code defaults that a **sidecar file** overrides. There is one file per owner, so no two packages write the same file: `game/layout/area_<key>.json` (P1: pins), `game/layout/view_<place>.json` (P5: slots and pose boxes; the only file `install_pose.py` writes) and `game/layout/hot_<place>.json` (P6: hotspot points). Their schemas are frozen in 6.1. `rule_layout(name)` takes the full stem. Foreground polygons are not a sidecar: the game never reads them; they are tool input in `tools/fg/<place>.json` (P5, D38). `tools/layout_sheet.py` draws all of them on the background for approval. | J-tech gap: points measured on stand-in art are wrong when the real picture lands. A JSON file is a drop-in, not a script change. (D's sidecar idea, widened.) | P0 |
| D6 | "Find someone" becomes "Right now" on each person's page plus one place line on each People card. The page has a "Go there" button (new journal return `("go", loc)`, campus journal only). A person in a room I can't enter reads "Somewhere I can't go right now". **The button is cuttable.** | SCOPE 2.C; PHASE1 section 10 note 1. | P1, P3 |

### HUD, icons, hover labels

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D7 | Map, Journal, Menu: same corner, same order, 64×52 icon buttons. | Owner's answer 1. | P2 |
| D8 | `icon(name)` uses `images/icons/ic_<name>.png` when it exists, else the kanji seal the game already uses. **While an icon has no picture, its word shows under it** (`gui.icon_words = "auto"`; `"never"` and `"always"` are the other values). | J-owner gap: kanji are unreadable without hovering. One value answers "too hidden" at checkpoint B. | P0 |
| D9 | The whole icon table (88 names, glyph and word) is final in the scaffold. A wave package never adds an icon name. | J-build: E's table sat in a wave file with a dangling reference. (S) | P0 |
| D10 | Hover labels use Ren'Py's own `tooltip` and `nearrect focus "tooltip"` in **one** screen, `hover_label`, listed in `config.always_shown_screens` at zorder 190. It draws only tuple tooltips (D11); a plain-string tooltip is left to the screen that owns it, so phase 1's map tooltips never show twice. | The engine captures the hovered button's rectangle by itself (`renpy/display/focus.py:226-228`; `NearRect`, `renpy/display/layout.py:2392`; `renpy/config.py:703`). Being its own top screen, the label is never under a toast or a sprite (J-tech's flaw in S; J-build's "label and toasts together" gap). | P0 |
| D11 | A tooltip is the tuple `(text, key)` with a key unique on its screen. | The engine only re-captures the rectangle when the tooltip *value* changes (`focus.py:226`); two neighbours with the same words would leave the label on the old button (J-tech's flaw in D). | P0 |
| D12 | Toasts draw only over scenes, the place view, the person view and a fight (as today). On every other full screen they wait with their clocks stopped. In the place view the stack sits left of the icon column and the objective banner moves left to x 400 to 1300, so the two never meet. The objective banner draws only over the place view. | Lesson 4; PHASE1 section 10 notes 3 and 4. One function, `toast_room()`. | P2 |
| D13 | The SKIPPING tag is hidden while any `sandbox` or `menu` screen is up (the quick menu's own test). Done in the scaffold so checkpoint A shows a fix. A small "skipping" chip sits by the date instead. | J-owner graft (E). | P0, P2 |
| D14 | Skipped rewards do not go to a log. | PHASE1's open question. New UI nobody asked for; rewards are visible in Stats, Inventory and the person's page. First thing to add back on request. | – |

### Grades

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D15 | Tokens: g4 `#4fbf7a`, g3 `#4a90e2`, g2 `#9b5de5`, g1 and s1 `#e5383b`, sp oil slick. Always a **filled chip with dark text**; the Special chip is a dark base (`#16121f`) with the sheen and light text. | Filled chips don't fight name colours (Maki green, Megumi blue). Answer 7. | P0 |
| D16 | The oil slick is a tileable strip, `gui/grade_sheen.png`, drawn by `tools/gen_gui.py`, **panned** behind the chip by a wall-clock function transform (a top-level function, R10). A painted strip of the same name replaces it. | J-tech: a hue-cycled flat colour reads as a glitch and an ATL loop restarts on every tooltip change. (D's strip, S's wall-clock rule.) | P0 |
| D17 | **Loops** (sheen, breathing, hotspot pulse, blink, talk) are wall-clock function transforms that ask for a redraw every 0.05 s (`VIEW_TICK`), never every frame. **One-shots** (the map's zoom-in, the eased entrance into dialogue, the focus on a person) are ATL `transform` statements. Every transform function is a **top-level store function** with its parameters passed through `renpy.curry`, never a closure or a lambda (R10): a sprite shown with `renpy.show` is saved, and a closure cannot be. Depth blur is a fixed property under the animation, not animated. `persistent.motion` (a "Motion" row in Preferences, default on) turns the loops off through one function, `view_motion()`. | J-tech's frame-budget gap. `toast_fx` in `ui_hud.rpy` proves the redraw pattern inside a screen (`renpy/display/transform.py:1063-1067`), but it is a closure, which is only safe because a screen does not save its transforms (`renpy/display/screen.py:329-345`); `Transform` keeps `self.function` (`transform.py:744`). (Review: blocker.) | P0 (switch, `VIEW_TICK`, `view_motion`), P5 |

### Journal and person view

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D18 | Five tabs. `journal("memories")` opens People. A shared scene shows on every participant's page (`memories_with(who)`, already written). A **"Me" card** comes first in People: the story by act, including the three scenes nobody else is in. | Answer 6, both halves; SCOPE 2.C's "Kaito's own page". (D; J-owner graft over E's Stats → My story.) | P3 |
| D19 | The person view shows a grade chip and the choices, then "Ask them along" and Back. The name, caption, bond bar, affection, thread diamonds and "Closer" hint are all on the journal page. | SCOPE 2.D. J-owner: E's bond bar was not asked for. A bond toast already answers "did that work?". | P2 |
| D19b | "Right now" captions follow the story: a new table `AMBIENT_STORY` of `(who, place, condition, caption, expression)` rows is read before `AMBIENT`; the last row whose condition holds wins. Twelve rows ship on existing flags and thread stages; phase 4 adds rows per act. | J-owner gap: the note says "updated as the story progresses". `ambient_of` keeps its 2-tuple. | P2 |

### The night

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D20 | **Night is the last hour, and it is strict.** At Night: walking and anything free stays; every action that costs time is closed ("Too late. Bed.") unless its id is in `NIGHT_OK`; Wait becomes **Go to bed** (walk to my room, sleep, wake there). `NIGHT_OK` at ship: `night_gojo`, `stargaze`, `rom_close`, `int_night`. A mission is asked about as `night_allows("mission:" + mid, cost)`: allowed when its periods include Night or it costs nothing. The card table is closed at Night (the owner's list of exceptions does not include it). One constant, `NIGHT_STRICT`, switches to the loose reading. | Answer 2: "must return to his bedroom to sleep at the latest hour before morning", with "until then the night is his" (Evening is untouched). J-owner: E's loose reading was weak and the three designs disagreed; the owner rules at checkpoint A. | P4b |
| D21 | **A safety net.** Whenever a day starts and I'm not in my room (a mission ran late, an allowed night scene ended), the loop walks me home with one line before anything else. The check sits after `$ ensure_state()` and **before** the story pick, so a waiting beat is picked for my room. Skipped in explore mode. | Covers every caller of the clock in one place. J-tech: S and D put it after the story pick. | P0b hook, P4b |
| D22 | The line the safety net says depends on where the day turned (`NIGHT_CARRY_LINES` by area; "I let myself out before the corridor wakes" from someone's room). | J-tech gap: the Nade missions (`missions_arc1.rpy:101, 149, 254`), "Stay the night" and a story beat that ends in `advance_period()` at Night (`story_arc1.rpy:109`) each roll the day themselves. Board jobs do not: the board refuses every job in the Evening and at Night (`sb_board.rpy:538-539, 554-555`). | P4b |
| D23 | **A night with Gojo.** After `intensive_done`, on a day he is in, at least 10 days after the last one, and only if the night would beat a day from where I stand (below): a morning toast "Gojo: the ridge, tonight", a moon on the Mountain marker, and he is on the ridge at Night ("sitting just outside the veil"). A gold icon there: "Train until morning". **The gain is derived, not a literal:** Control rises by `night_day_best()` + 6, where `night_day_best()` is what the best possible day of training would give from my Control now: **Gojo's lesson** (Control +5, one period; it is always on offer on a day a night is offered, because both need him in), a train on the ridge for each of the other four periods, and Hold the hour, in whichever order gives the most, through the same diminishing returns as `gain` (and never less than five trains and the hold with no lesson). Reserve rises by what that day would give plus 3: the lesson's 5 and one for each of the other four periods is 9, so 12 today. From Control 30 that is +29 Control against a day's +23, and +12 reserve against +9. The points are applied one at a time through `gain`, so its floor of one point a call makes the total exact. **The cap:** `gain` still stops at my grade's ceiling, so the night is only offered when the room under the ceiling (plus `NIGHT_GOJO["past_cap"]`, 0 by default) is larger than `night_day_best()` (then even a clipped night beats a day) and there is room for the whole reserve gain. **This is rarer than "it waits for a promotion":** ceilings rise 15 at a time (`sb_grades.rpy:25-29`) and a best day is worth 23 up to Control 40 and 16 at 55, so at the ceiling just after a promotion to Grade 3 or Grade 2 no invitation comes; it comes at Semi-Grade 1 (a best day from 70 is 12) and Grade 1. It is offered at Grade 4 while Control ≤ 16, Grade 3 ≤ 31, Grade 2 ≤ 52, Semi-Grade 1 ≤ 72, Grade 1 ≤ 93. Section 0 tells the owner so and puts the alternative as ruling 5 at checkpoint A: `past_cap = 6` lets that one night end up to 6 above the ceiling (4.15 says how, since `gain` clips), so it is offered at every grade. I wake in my room. **Next day: no missions or board jobs can be started, and nothing in `NIGHT_REST_BLOCKS` (Train, Practice, "Train together", the lesson, Hold the hour, swimming); nothing else raises Control or Output that day either (4.15); story beats that just happen still play.** A "Worn out" chip sits by the date. | Answer 2: "more control and cursed-energy reserve than training every hour of the day would". The first draft's +18 lost to five periods on the ridge (+20, `sb_loop.rpy:232-234`) and tied above Control 60 (review: major, twice); the revision's mirror left out the lesson (`act_lesson`, `sb_activities.rpy:321-322`: Control +5, reserve +5), so its reserve +8 lost to a lesson day's +9 (verification: blocker). The ridge uses the pose phase 1 never showed (D; PHASE1 section 10). No night is spent for nothing (J-owner's cap gap). Story beats are not held (J-owner flaw in E). | P4b |
| D24 | **A night in Tokyo.** From the Tokyo map at Evening or Night once Tokyo is open: Shibuya, and Shinjuku once it is open (Grade 2). On arriving I choose: **the club** (¥1,500; a companion gains Bond +4), **the Black Market** (Shibuya, once found), or **head home** (nothing happens, nothing is charged). The club and the market each mean I was out all night: next morning stamina at half, cursed energy at 70%, a "Rough morning" chip; missions and training stay allowed. Not two nights running. **The Black Market is in Shibuya,** found on the first club night or by reading the rumour thread. It sells four new talismans of its own, sealing talismans and first aid. **It does not sell `unending_moment`, `the_zone` or `finger_wrap`:** those are story rewards with their own sources (`sb_items.rpy:150-165`), "bound by story", and only one special may ever be bound (PHASE1 3.8). A market-only Special is one row, offered to the owner in section 0 and not built by default. Outfits: a shelf that appears only when an outfit row's sprite files exist. | Answer 2: "with the option to party at nightclubs" (the club is a choice, not the only thing to do). J-owner: Shinjuku is locked until Grade 2 (`sb_tokyo.rpy:51`), so the market must not live there. (S, D; review: majors.) | P4b |
| D25 | **Character scenes wait for roll call.** An event gate holds `hangout` events until `has_flag("roll_call")`, or `"st_roll_call"` is in `done_events`, or `has_flag("sunmall_done")` (so an old save that is already past it is never held). The flag it waits for is one constant, `RULE_HANGOUT_AFTER`. | Open call 2. Roll call costs the first day only; the Sun Mall would cost three or more (J-owner flaw in D). J-tech gap: old saves without the flag. | P0 |
| D26 | **Two-slot activities stop for a waiting beat** (the owner rules at checkpoint A; section 0, ruling 3). `advance_period_soft(n=1, loc=None)` steps one period at a time, stops early when a story beat is waiting at `loc` (default: where I stand; the Tokyo trip passes `"gate"`, where it is about to put me), and stops on arriving at Night with steps left. It tests `has_event("story", loc=…)` exactly as `board_beat_waiting` does (`sb_board.rpy:679-685`), never `pick_event` (which draws from `renpy.random`), and is skipped in explore mode. The lost time is forgiven, silently. Called at Night it rolls the day exactly as `advance_period` does. Used by the activity charge (`sb_loop.rpy:134`), the Tokyo trip (`sb_tokyo.rpy:184`), `start_mission`'s cost (`sb_missions.rpy:1138`) and the new rooms. | Open call 1; the board already does this (`board_clock`). J-build gap: the "stopped early" case is frozen as "silent, forgiven". Stopping at Night means a two-period activity started in the Evening can't carry me past bedtime. (A spar is not a case: "Train together" costs one period and `sb_spar` charges it itself; line 134 skips it. What costs two or more: `stand`, `rom_town`, `rom_say` (2), `int_day` (3), the Tokyo trip, a mission with a cost.) | P0 |

### Gear

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D27 | Requirements are a side table, `ITEM_REQS`; `ITEMS` records keep their 12 fields. **Tools:** Inverted Spear: Arc Two, Special Grade, flag `spear_unsealed`, flag `yaga_signature`. Playful Cloud: Grade 2, Output 50. Split Soul Katana: Semi-Grade 1, Insight 60. **Talismans, the same system:** Afterglow: Grade 1, Control 80. Black Sun: Grade 1, Output 80. Borrowed Luck: Grade 3, Insight 30. Night Eyes: Grade 3, Insight 35. Debt Marker: Grade 2, Control 50. Second Wind: Semi-Grade 1, Output 60. (The four market rows are added to `ITEM_REQS` by `sb_market.rpy`.) A validator (`item_validate_reqs`, written in `sb_items.rpy` by P0b so that P4a and P4b both run it; it has nothing to check while `ITEM_REQS` is `{}`) checks each Control or Output threshold is reachable under that item's own grade cap (`GRADES[grade]["stat"]`), each Insight threshold is at most 100, and every flag has words. | SCOPE 2.I ("Cursed tools and talismans with more depth"); the owner's page 5 note: "Same sort of system for the talismans as well". `wp6_items.rpy` pins the 12 fields. J-build: assert against the game's own tables. | P0b (the validator), P4a (P4b: the market rows) |
| D28 | Nothing already held is taken away: a tool in my hand or a talisman I'm wearing stays, whatever its new checklist says. The check gates *taking* and *putting on anew*. No migration is needed for this. | J-owner graft (D's intent) without D's migration. | P4a |
| D29 | Prices and winnings are tied to what the board pays. A validator checks every market price is at most three top jobs at the item's grade: `3 × BOARD_YEN[grade][1]` for `g4`, `g3`, `g2`, `s1`; `g1` uses the `s1` row (3 × 20,000 = ¥60,000) because `BOARD_YEN` has no `g1` key (`sb_board.rpy:86`); `sp` is six `s1` jobs (¥120,000); an ungraded supply is capped at `BOARD_YEN["g4"][0]` (¥3,000). Nothing is sold that can't be worn in Arc One: Second Wind is Semi-Grade 1, not Grade 1. Card winnings stop at one top Grade 4 job a day (`BOARD_YEN["g4"][1]`). A harness checks fishing earns less per period than the cheapest board job does. | J-owner and J-build gaps on unplayed balance. | P4b, P6, P7 |

### Rooms

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D30 | A hotspot is a row: a point and an icon. An **action** hotspot returns the existing `("act", id)`, so the loop runs `sb_do_<id>` as a button would; **it exists only while `place_actions(loc)` offers that id right now, and takes its label, hint and cost from that row** (so a once-a-day action, a closed board or explore mode hide it exactly as they hide the button). A **look** hotspot carries its lines and returns the new `("hot", id)`. A hotspot is *visible* only when its 72 px square is clear of every person standing in the room now; otherwise it is not drawn and its action stays in the column. **`place_actions()` is not changed.** The icon column leaves out an action a visible hotspot already offers (`rail_actions()`). | J-tech and J-build: E filtered inside `place_actions`, which `core_flow.rpy`, `wp11_dev.rpy` and `phase1_all.rpy` read. (D) | P0, P6 |
| D31 | **The computer is a fake internet.** Five sites with different voices, twelve pages. Reading is free; the first read gives Insight +1 (or the page's own `gives` in its place: `techniques` gives +2, not +3) and sets `researched_<page>`. It changes other things now: "Cross-check the board" (one period, once a week) marks a misgraded job, and the urban-legends thread reveals the Black Market. Missions use it through `pc_request(page, note)` and `gate.flags=("researched_<page>",)`; one request ships (Sukuna, after the ridge veil) and shows as a **lead** in the journal's Missions tab (`pc_leads()`), so the mission link is visible at checkpoint C. No existing mission gains a gate (it would lock progress in old saves). | Answer 3. (D's sites, E's cross-check, S's first prompt; J-owner grafts and gap.) | P6 |
| D32 | **Cards: blackjack, then poker (five-card draw),** at one table, for yen, against whoever is in the common room (up to three). Each person has a style (how tight, how often they bluff, what their face gives away); with Insight 20 I get one "read" per poker hand. Stakes ¥100 / ¥500 / ¥1,000; a sitting ends at five hands or ¥3,000 down. Closed at Night. Every deal, draw and settlement blocks rollback, so a lost hand can't be replayed with the next card known. If credits run short poker is the first thing to wait, **and only with the owner's say** (7.3). | Answer 4. (S's tells; D's interface so chess later is one file.) | P7 |
| D33 | **Fishing:** three casts for one period; a bite, then stop a marker in a zone. A catch has a species and a length; it sells itself (¥100 to ¥600), the first of a day gives Control +1 (not on a rest day, 4.15), the record book keeps my longest of each of six species. The River Lord bites only in the Evening on a near-perfect cast. Once a week in the Evening something cursed comes up and leaves a sealing talisman. A companion gains Bond +2 once a day. Each settled cast blocks rollback. This is the proposal the owner asked for; section 0 says so. | Answer 5: "a gimmick, or the biggest fish": both. (E; D's cursed catch; S's companion.) | P6 |
| D34 | **The Library:** place `library` in the School Building, open at every hour. "Study in the stacks" gives Insight +4 on its theory shelf (a desk gives +3). Megumi reads there on weekend afternoons. The room itself (its `LOCATIONS` row, its place in the School Building, its stand-in picture) is laid by the scaffold, so the wave-1 and wave-2 packages that mention it all lint against a real place. | Answer 8. (J-owner graft; review: P2 could not lint without it.) | P0 (the room), P1 (pins, schedule), P2 (caption, study), P6 (actions) |

### The place view

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D35 | The stage (the people, their name tags, the focus transform) moves into its own file, `game/view_stage.rpy`, in the scaffold (`sb_screens.rpy:405-453`: the stage buttons and the name plates, verbatim; the background at 402-403 and the overflow chip from 455 stay in `sb_place`). Because a `use`d screen that takes parameters gets a fresh scope holding only those parameters (`renpy/sl2/slast.py`, `SLUse.execute`), `view_stage(loc)` starts with its own copies of the five `$` lines the loop reads (`sb_screens.rpy:388-392`), with `here` replaced by `loc` (4.5). `sb_place` and `sb_char` `use` it. | J-tech and J-build: E handed `sb_screens.rpy` from one package to another. (S) | P0 |
| D36 | A pose is one whole 1920×1080 picture of the room with the person painted in. The engine overlays only a soft-edged box around the person, so several people in a room each use their own picture. **It is painted on the picture the player actually sees at that hour** (Nobara's on the evening common room) and named for it; a missing variant falls back to the standing sprite, never to a day pose on a night room. | E's box survives the pixel noise an AI repaint spreads (J-tech). D's variant rule (both judges' graft). | P5 |
| D37 | `tools/install_pose.py` refuses a picture where more than 35% of the room changed, writes a side-by-side preview, and writes the box to the sidecar `view_<place>.json`. "Changed" means: after a 4 px blur of both pictures, a pixel differs by more than 24 in any channel; the box is the largest connected changed region grown by 24 px. `--box x,y,w,h` sets the box by hand. | Graft (D). | P5 |
| D38 | Foreground layers are cut from the backgrounds themselves by `tools/make_fg.py` (a polygon per place, per time variant, kept in `tools/fg/<place>.json`: tool input, not a game sidecar). Free. | Graft (E). | P5 |
| D39 | Blink and talk: two edits of each neutral sprite; the engine uses only the eye box and mouth box, on the expressions listed as compatible. **Yuji's pair is made and judged first** ($0.64). Gojo and Yaga get talk only. **Cuttable.** | Graft (S). | P5 |
| D40 | Drop-in files start with their kind: `area_`, `pose_`, `fg_`, `ic_`, `fx_`. A validator rejects two files under `images/` with one basename. | Ren'Py names an auto-image from the basename; `images/fg/dorm_common.png` would collide with `images/bg/dorm_common.png`. (D) | P0 |

### Method

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D41 | **No migration, `SAVE_VERSION` stays 1.** All new state is a plain `default`, safe at its default. | E; J-tech showed S's and D's migrations were not needed. | all |
| D42 | Files that hold protected statements are edited **once**, by the scaffold, through a written hooks table (6.3). `sb_loop.rpy`, `sb_tokyo.rpy`, `sb_missions.rpy`, `sb_events.rpy`, `sb_hooks.rpy` and `explore.rpy` are then frozen until integration. (`sb_hooks.rpy` is not edited at all in phase 2: the duplicate place-action check the review asked for already exists there, `_validate_place_actions`, `sb_hooks.rpy:262-275`.) | E's strongest point (all three judges). | P0 |
| D43 | **Never edit a `call` and the statement after it in the same phase.** Ren'Py returns to the statement after the call by name (`renpy/ast.py:1629`), then falls back to the call's own next statement (`renpy/execution.py:795-796`), then to `return_recover`. `sb_loop.rpy:107` (`$ advance_period()` after `call play_event(_e)`) is such a line and is **not** edited. Lines 134, `sb_tokyo.rpy:184` and `sb_missions.rpy:1138` are not return sites (6.3). | J-tech gap. | P0 |
| D44 | Every new `call screen`, `menu` and `call` a save can rest on, with the line after it, joins the protected list from the commit it lands in (2.3). The owner's checkpoint saves join `load_all_saves.sh`. | J-tech gap. | all, P8 |
| D45 | Lesson 1: one prefix per new file, checked against a baseline of today's names; a duplicate-global check; each contract function's owning file asserted at run time; duplicate ids rejected in the hotspot, minigame and place-action registries. A file with no prefix row may gain no new top-level name. | S's baseline, D's `co_filename`, J-build's registry gap. | P0 |
| D46 | Lesson 2: contracts freeze return **values**; screens reach other packages only through `Return(tuple)`, `Function(ui_do, fn, …)` or a named Action class listed in section 4; a source check in `check_content.py` enforces it for every `Function(` in the game, in screens and in Python helpers alike. | S; J-tech: E's init-time walk can't be built. | P0 |
| D47 | Lesson 3: `fixture()` fails on an unknown name and refuses shaped variables; harnesses build records with the owner's constructors. | D. | P0 |
| D48 | A clutter budget per screen (4.0), counted by `zz_words()` and `zz_buttons()` with icon words off. `zz_words` counts tokens that contain a letter and skips the kanji of a stand-in icon (its `Text` carries the style `icon_glyph`), so the budget means the same thing before and after the icon art lands. Faces on the map have their own column. | J-owner: only S measured clutter. Our labels live in a separate screen, so S's "transparent text" problem doesn't arise. | P0, each |
| D49 | `tools/smoke.sh` gets a per-harness asset overlay, so a test picture never lands in the owner's `game/images/` (the script symlinks asset folders today, `tools/smoke.sh:99-106`). | J-build gap. | P0 |
| D50 | Review-tool buttons for the rare states (Night, a Gojo night, a rest day, yen, the market, a style sample) are added by the scaffold against stubs, so checkpoints B and C can reach them. A button whose feature is not built (`market_exists()` or `night_exists()` False) is hidden. | J-build gap. | P0 |
| D51 | If a package fails its harness: one retry with the failure log. If it fails again, stop and ask the owner. The wave merges without it (its stubs keep the game playable, and 7.3 lists what each missing package leaves hidden). **A cut that removes something the owner decided in SCOPE section 5 (poker, the night out, the market, the Library's actions) is never the agent's call:** the orchestrator asks the owner. Only the integration package may touch a frozen file. | J-build gap; limited credits. | all |
| D52 | The serif macron font (PHASE1 section 10) is not in phase 2. | A new font asset, no owner note. | – |

---

## 2. Ground rules

### 2.1 Phase 1's rules, still in force (PHASE1 2.1 to 2.4)

- The protected statements stay textually identical (PHASE1 2.1 rule 1). New branches are new `elif` lines; new statements go before or after.
- Never delete a label. Never rename a store variable. New state is `default`. Saved state holds only `str`, `int`, `bool`, `None`, `list`, `dict`, `set`, `tuple`.
- Never delete, move or force-recompile `game/*.rpyc` in the owner's folder. Worktrees get copies (`cp -p`); never copy back.
- Screens keep their names, parameters and return tuples. In phase 2 a screen may gain an optional parameter with a default, and an extra return tuple handled by a new `elif`. The additions are listed in 4.0 and nowhere else.
- First person; no literal protagonist name (`[mc_name]` / `[mc_surname]`); Kaito never on screen; placeholder scenes start with `## PLACEHOLDER — rewrite in phase 4`. Web pages and item text are in-world documents and never address the player.
- Colours, fonts and sizes are tokens. P0 adds its tokens to `gui.rpy`, which is then frozen. A wave package that needs a new one defines it in its own file as `define gui.<prefix>_<name>` (the browser's site colours are `gui.pc_*` in `room_computer.rpy`, the suit colours `gui.cards_*` in `room_cards.rpy`); `--dup-globals` and `--prefixes` cover `define gui.*`. New styles likewise live in the package's own file.
- `config.check_conflicting_properties` is on: never set both `xpos` and `xalign`, or `xsize` and `xysize`, on one thing.

### 2.2 Rules that design out phase 1's lessons

**R1. Prefixes (lesson 1).** Every new top-level name (function, table, screen, style, transform, image, label, `default`, and every `$ _x` temporary in a label) starts with its file's prefix.

| file | prefix | file | prefix |
|---|---|---|---|
| `game/ui_icons.rpy` (new) | `icon`, `ICON` (so `ICONS`, `ICON_FOR`, `ICON_GOLD`), `hover_`, `ui_do` | `game/room_spots.rpy` (new) | `spot_`, `SPOT_` |
| `game/sb_hotspots.rpy` (new) | `hot_`, `HOT_`, `mg_`, `MG_` | `game/room_computer.rpy` (new) | `pc_`, `PC_` |
| `game/sb_rules.rpy` (new) | `rule_`, `RULE_` | `game/room_fishing.rpy` (new) | `fish_`, `FISH_` |
| `game/view_stage.rpy` (new) | `view_`, `VIEW_` | `game/room_library.rpy` (new) | `lib_`, `LIB_` |
| `game/sb_night.rpy` (new) | `night_`, `NIGHT_` | `game/room_cards.rpy` (new) | `cards_`, `CARDS_` |
| `game/sb_market.rpy` (new) | `market_`, `MARKET_` | harnesses `tools/smoke/*.rpy` | `zz`, `ZZ` |

New names in an existing file use that file's prefix: `ui_map.rpy` `map_` / `MAP_`; `ui_journal.rpy` `jr_` / `JR_`; `ui_hud.rpy` `toast_` / `hud_`; `sb_screens.rpy` `rail_` / `AMBIENT_`; `sb_items.rpy` `item_` / `ITEM_` / `armory_`; `sb_grades.rpy` `grade_` / `GRADE_`; `sb_board.rpy` `board_`; `sb_combat.rpy` `combat_`; `sb_world.rpy` `world_`; `sb_activities.rpy` `act_`; `lighting.rpy` `light_`; `screens.rpy` `pref_`; `gui.rpy` `gui.grade_` / `gui.icon_` (P0b's tokens of 3.2); `explore.rpy` `dev_` / `DEV_`; `bg_placeholders.rpy` images `bg area_*` and `bg library` only. **A file with no row here (`sb_threads.rpy`, `sb_memories.rpy`, `sb_tokyo.rpy`, `sb_hooks.rpy`, and the rest) may gain no new top-level name.** Label temporaries are `_night_x`, `_pc_x`, never `_a`, `_r`, `_p`, `_ok`.

The only exceptions, by name: the contract symbols of section 6 that have no prefix (`advance_period_soft`, `register_hotspot`, `register_minigame`, `person_now`, in files whose prefix they don't carry); labels `sb_do_<action id>` where the action id carries the prefix (`sb_do_pc_open`, `sb_do_night_bed`); labels `mg_<game id>`; the moved transform `char_focus` (`stage_person` is a label in `sb_activities.rpy:278` and stays there; it is in the baseline). Everything else was renamed to fit: `hot_spots_for`, `mg_games`, screens `map_area`, `map_district` and `market_screen`. `tools/prefixes.json` holds the table and the exception list.

**R2. Checks (lesson 1).** `tools/check_content.py` gains, all inside `--all`:
- `--dup-globals`: across `game/*.rpy`, every top-level `NAME =`, `def`, `class` in `init … python:` blocks and every `define`, `default`, `screen`, `style`, `transform`, `image`, `label`; a name defined in two files, or twice in one, is a finding. Store names, screens, styles, images and labels are separate namespaces (today's `jr_mission_row` function and screen pass).
- `--prefixes`: a name that is not in `tools/smoke/baseline_globals.txt` (today's names, written by P0) must carry its file's prefix from `tools/prefixes.json`, or be on R1's exception list.
- `--harness-names`: every top-level name in `tools/smoke/*.rpy` starts with `zz` / `ZZ` (today's exceptions are recorded in the baseline).
- `--art-names`: two files under `game/images/` with the same basename.
- Run time: `tools/smoke/p2_contracts.rpy` asserts `fn.__code__.co_filename` ends with the owning file for every contract function. A silent replacement fails in every worktree.
- Registries: `register_hotspot` and `register_minigame` report a duplicate id as a `VALIDATE:` line. Place actions already have this check (`_validate_place_actions`, `sb_hooks.rpy:262-275`: "place action %r is registered twice"), so nothing is added and `sb_hooks.rpy` is not touched. Migrations are not checked: phase 2 adds none (D41), and order 65 is already used twice today (`sb_memories.rpy:623`, `sb_missions.rpy:1028`), so an order check would fail the untouched tree.
- Init order: `p2_contracts` is run with `tools/smoke/aa_zz_order.rpy`, a file named to sort before every game file, which makes one dummy `register_hotspot` and one `register_minigame` call at init 0. It fails with a NameError if a registry is ever defined too late (6.1).

**R3. Frozen return values (lesson 2).** Section 6 gives every contract's return value. A stub returns a value of the same type and shape. `p2_contracts.rpy` holds one table, `ZZ_RETURNS` (symbol, example call, expected type or shape), and runs against the stubs at P0 and, unchanged, against every worktree and the merged tree. (The three symbols that arrive with a later package are asserted in that package's own harness, 6.1, so `p2_contracts.rpy` is never edited after wave 0.)

**R4. Screens never call another package directly (lesson 2).** A button's action is one of:
- `Return(tuple)` to a label loop;
- `SetScreenVariable` / `SetDict` / `ToggleDict`; `NullAction()`; `ShowMenu(…)`; `Hide(…)`; `If(cond, a, b)` and lists of allowed actions; the existing replay action (`MemoryReplay`, `sb_memories.rpy:571`);
- `Function(ui_do, fn, …)` (`ui_do` calls `fn` and returns `None`);
- `Function(f, …)` where `f` is on `tools/none_ok.txt`;
- **a named Action class whose `__call__` returns the screen's documented tuple,** allowed only when section 4 lists it. One ships: `fish_Hook` (4.13), because the value it returns must be read at the moment of the click.

`check_content.py --action-returns` flags every other `Function(` in `game/*.rpy`, **inside `screen` blocks and inside `def` bodies** (today `explore.rpy:259-260` builds `Function(DEV_FUNCS[key])` in a `def`; `map_row_action` and `icon_btn`'s callers do the same). It flags nothing but `Function(`. `tools/none_ok.txt` is one line per function, `name<TAB>example call` (`jr_wear<TAB>jr_wear(0, "paper_ward")`: the slot is an integer, `ui_journal.rpy:948`); `p2_contracts.rpy` runs each example inside a `settle()` fixture and asserts `is None`. The `dev_*` functions change state (a week passes, a grade rises), so they are checked through `dev_action(key)` for every key in `DEV_FUNCS`, each in a fresh fixture. `none_ok.txt` at P0: `toast_tick`, `check_objective`, `jr_go`, `jr_toggle`, `jr_wear`, `jr_hold`, `jr_takeoff`, and the `dev_*` functions.

**R5. Fixtures from constructors (lesson 3).** `fixture()` fails on an unknown variable name, and refuses to set a shaped variable at all: `board_offers`, `board_log`, `npc_state`, `inventory`, `mission_state`, `cb`, `cards_state`, `fish_state`, `fish_log`, `pc_requests`. Harnesses build those with the owner's functions: `board_generate()`, `board_take()`, `give_item()`, `promote()`, `_mem()` / `memory_entry()`, `night_set_cost()`, `market_buy()`, `cards_new()`, `fish_land()`, `pc_request()`. Each package's acceptance names its builders.

**R6. Lanes (lesson 4).**

| overlay | may draw over | where (1920×1080) |
|---|---|---|
| toasts | a scene | right edge 1880, top 92, four at most (as now) |
| toasts | the place view | x 1330 to 1790, y 92 to 350 (left of the icon column) |
| toasts | the person view | right edge 1722, top 26, two at most (as now) |
| toasts | a fight (`combat_screen`, which is tagged `sandbox`) | right edge 1880, top 92, four at most (as now; a fight's rewards must not be held back) |
| toasts | the map, journal, board, the board's partner picker, the grade card, armory, market, computer, card table, fishing, the style sample, the game menu | **not drawn**; they wait, clocks stopped |
| toasts | the review panel (`dev_panel`) | right edge 1880, top 92, four at most (as now: the review buttons report through toasts, and the panel sits left of centre to leave the stack clear, `explore.rpy:362`) |
| objective banner | the place view only | x 400 to 1300, y 96 to 170 (`xpos 400`, `xsize 900`; today it is centred at x 510 to 1410, which would run under the toast lane) |
| arrival caption | the place view only | from (40, 100), up to 744 wide, fades |
| SKIPPING tag | scenes only | (48, 108) |
| hover label | everything | beside the hovered button; zorder 190; may cover a toast while I hover |

No hotspot, pin, marker or button may sit inside a lane on its own screen; the hotspot and pin validators reject one that does. The icon column never rises above y 360. Every package takes a `zz_worst(screen)` screenshot (four toasts queued, the banner up, skipping on, one button hovered) of each full screen it owns. `p2_hud` asserts the toast lane and the banner lane rectangles do not intersect.

**R7. Protected files are touched once (D42, D43).** After P0, the six frozen files change only through P8.

**R8. Drop-in art.** Every picture is looked up with `renpy.loadable(path)` and has an engine stand-in. No package makes a picture a requirement. Positions measured on a picture live in its sidecar (D5).

**R9. Motion budget (D17).** A function transform returns `VIEW_TICK` (0.05) as its redraw delay, or `None` when `view_motion()` is False. The place view holds at most eight **new** ones (four people, four hotspots); the two light transforms each sprite already carries (`lighting.rpy:133-143`, redrawing every 0.25 s) are not counted. Measurements are taken after any transition has ended (a `Dissolve` renders every frame). Blur is never inside one.

**R10. Nothing un-picklable reaches a save (D17; PHASE1 2.1).**
- Anything shown with `renpy.show` or a `show` statement (the eased entrance of `view_enter`, the `view_fg` layer, every sprite `lit_sprite` builds, with its blink and talk layers) uses only an ATL `transform` statement or a **top-level store function**, with parameters passed through `renpy.curry`. Never a closure, a local `def`, or a lambda. A sprite's ease uses `st`, not the wall clock, so it replays correctly after a load.
- Screen scope is saved too: never assign a displayable or a function transform with `$` or `default` inside a screen. Build it in the `add … at …` line.
- The phase-1 closures inside screens (`toast_fx`, the arrival caption's `arrival_fx` at `sb_screens.rpy:220-236`) stay as they are; new code does not copy them. (The stage itself has no function transform: `char_focus` is ATL.)
- Tested by saving: P5's harness and `p2_saves` save and reload on the first line of dialogue after `stage_person`, with the foreground up, and again after rolling back through it.

### 2.3 Statements that become protected in phase 2

From the commit each lands in, these stay textually identical, each with the line after it (D44). Later packages and phases 3 and 4 treat them as PHASE1 2.1 rule 1 treats the loop.

| file | statements |
|---|---|
| `sb_loop.rpy` | `call night_carry_home`; `call hot_use(_r[1])`; `call rule_walk_to(_j[1])`; `call night_out(_m[1])` |
| `sb_tokyo.rpy` | `call night_out(_car[1])` (a defensive branch, unreachable today: the car runs only until Afternoon and the night button shows only from Evening, 6.3) |
| `explore.rpy` | `call screen icon_sample` |
| `sb_night.rpy` | the three `menu:` statements (the Gojo night; the night in Tokyo's three-way arrival choice; the after-club Black Market / Home choice) with their captions; both `call market_open` statements (after the club; the direct market choice), each with the line after it |
| `sb_market.rpy` | `call screen market_screen` / `$ _market_r = _return` |
| `room_computer.rpy` | `call screen pc_screen(_pc_page)` / `$ _pc_r = _return` |
| `room_fishing.rpy` | `call screen fish_screen` / `$ _fish_r = _return` |
| `room_cards.rpy` | `call screen cards_table` / `$ _cards_r = _return`; `call screen cards_blackjack` / `$ _cards_b = _return`; `call screen cards_poker` / `$ _cards_p = _return`; `call expression "mg_" + _cards_r[1] pass (_cards_opp, _cards_r[2])` (opponents, then the stake: the frozen interface is `label mg_<id>(opponents, stake=0)`, 4.12) |
| `room_library.rpy` | the shelf `menu:` |

### 2.4 Working method

- **Backup first** (P0 task 0): `game/*.rpyc`, `game/saves/`, `~/Library/RenPy/JJKgamemd-1788928056/` → `~/Desktop/JJK_backup_phase2_<date>/`.
- P0a, P0b and P0c commit to `phase2` in the owner's folder, in that order (P0c changes no `.rpy` file). Each later package works in `~/Desktop/JJK_worktrees/p2_<n>`, **branched from `phase2` after the wave before has merged,** with the owner's `.rpyc` copied in. Files are disjoint within a wave, so merges are clean, and every package codes against P0's stubs, so the tree is playable after any merge in any order (7.3 lists the few acceptance lines that only run once another package is in).
- File ownership is **per wave** (7.2): in wave 0, P0 owns every file it touches; in wave 2, a file P2 owned in wave 1 can belong to P5.
- Lint is `~/Desktop/renpy-8.5.3-sdk/renpy.sh <tree> lint`, in a worktree or scratch copy only.
- **Standard acceptance for every package:** (a) lint clean, no `VALIDATE:` lines; (b) `python3 tools/check_content.py --all game/*.rpy tools/smoke/*.rpy` shows no new finding; (c) the package's harness passes through `tools/smoke.sh`; (d) `p2_contracts.rpy`, `core_flow.rpy` and `phase1_all.rpy` pass in the worktree, and so does every phase-1 `wp*` harness in the package's own row of 7.2; (e) a `zz_worst` screenshot of each full screen it owns; (f) a five-line "what changed / what to look at" note for the owner.

---

## 3. Data model

### 3.1 Changed tables (init data, never saved)

| table | file (owner) | change |
|---|---|---|
| `LOCATIONS` | `sb_world.rpy` (**P0**) | new row `"library": dict(indoor=True, name="Library", bg="bg library", x=250, y=640, desc="Shelves to the ceiling and a smell of dust and ink. Nobody talks above a murmur.")`; key appended to `LOC_ORDER`; the `school` row of `AREAS` (a list of dicts; `AREA_BY_KEY["school"]["places"]`) gains `"library"`; `bg library` in `bg_placeholders.rpy`. Laid in wave 0 so that P2's `AMBIENT` row and P6's hotspots lint against a real place (`_validate_wp7_tables`, `sb_screens.rpy:278-282`, rejects an unknown one). At checkpoint A the old map shows one more row, an empty Library |
| `AREAS` | `sb_world.rpy` (P1) | `school`: `name="School Building"`. Every row gains `bg="bg area_<key>"`, `blurb` (one first-person line) and `spots={loc: (x, y)}` (4.1). Keys, seals, order and anchors unchanged |
| `WEEKEND` | `sb_world.rpy` (P1) | Megumi, Saturday and Sunday Afternoon → `library`; the frozen copy in `tools/smoke/wp1_world.rpy` is updated in the same commit. **Cuttable** |
| `JOURNAL_TABS` | `ui_journal.rpy` (P3) | the `memories` row goes (five rows) |
| `THREADS` stage lines | `sb_threads.rpy` (P3) | the 11 lines that say "you" are reworded to "I/me". Only the stage index is saved |
| `MEMORY_UNMET_HINT` | `sb_memories.rpy` (P3) | "Someone I haven't met yet." |
| `ITEMS` | `sb_market.rpy` (P4b), through `_item()` | four talismans: `borrowed_luck` (g3), `night_eyes` (g3), `debt_marker` (g2), `second_wind` (s1); `source="The Black Market"`; `fx` stored only. Twelve fields each. (`sb_market.rpy` sorts after `sb_items.rpy` at init -1, which `_item()` and `ITEM_REQS.update(…)` need.) The three story Specials are not touched |
| `BOARD_GRADE_COLOR` | `sb_board.rpy` (P4a) | stays defined, re-pointed at the `gui.grade_*` tokens |
| `AMBIENT` | `sb_screens.rpy` (P2) | new row `("megumi", "library"): ("three books deep", "serious")` |
| `ACTIVITIES` | `sb_activities.rpy` (P2) | the `study` row's `loc` gains `"library"` |
| `DEV_BUTTONS`, `DEV_FUNCS`, `DEV_SCENES` | `explore.rpy` (P0) | six rows (4.16); the grid becomes 3×7 |

### 3.2 New tables (init data, never saved)

| table | file (owner) | shape |
|---|---|---|
| `gui.grade_g4`, `_g3`, `_g2`, `_g1`, `_sp`, `_sp_base`; `gui.icon_words` | `gui.rpy` (P0) | `"#4fbf7a"`, `"#4a90e2"`, `"#9b5de5"`, `"#e5383b"`, `"#9fe8d8"` (where only a string fits), `"#16121f"`; `"auto"` |
| `GRADE_TIER` | `sb_grades.rpy` (P0) | `{"g4":"g4","g3":"g3","g2":"g2","s1":"g1","g1":"g1","sp":"sp"}` |
| `ICONS` | `ui_icons.rpy` (P0, final) | `{name: (kanji, word)}`, the 88 names of 4.3. `ICON_FOR = {(kind, id): name}` maps action, activity, tab, place and area ids to icon names. `ICON_GOLD = {"mission", "night_gojo"}` |
| `HOT_SPOTS`, `MG_GAMES` | `sb_hotspots.rpy` (P0, final; `init -5 python`) | lists of dicts built by `register_hotspot` and `register_minigame` |
| `RULE_HANGOUT_AFTER`, `RULE_LAYOUT` | `sb_rules.rpy` (P0, final) | `"roll_call"`; a `builtins.dict()` cache of sidecar files |
| `AMBIENT_STORY` | `sb_screens.rpy` (P2) | `[(who, place or None, condition, caption, expr)]`; a condition is a flag name, `"thread:<who>:<n>"` or `"grade:<who>:<key>"` |
| `MAP_DISTRICT_SPOTS` | `ui_map.rpy` (P1) | `{district: [dict(id, name, icon, x, y, note)]}`, display only; `MAP_NIGHT_DISTRICTS = ("shibuya", "shinjuku")` |
| `ITEM_REQS` | `sb_items.rpy` (P0 writes `{}`; P4a fills the tool rows and the two Grade 1 talismans; P4b's `sb_market.rpy` adds its four with `ITEM_REQS.update`) | `{id: [(kind, …)]}`; kinds `("grade", key)`, `("arc", n)`, `("flag", name, words)`, `("stat", name, n)` |
| `MARKET_STOCK`, `MARKET_OUTFITS` | `sb_market.rpy` (P4b) | `[dict(item, price, once)]`; `[]` |
| `NIGHT_STRICT`, `NIGHT_OK`, `NIGHT_REST_BLOCKS`, `NIGHT_GOJO`, `NIGHT_OUT`, `NIGHT_CARRY_LINES` | `sb_night.rpy` (P4b) | `True`; `{"night_gojo", "stargaze", "rom_close", "int_night"}`; `{"train", "lesson", "hold", "swim"}` (action and activity ids closed on a rest day: `train` covers Train, Practice and "Train together"); `dict(over=6, reserve_over=3, day_step=4, day_hold=2, day_lesson=5, day_lesson_reserve=5, past_cap=0, gap=10, place="ridge")` (`day_step` and `day_hold` mirror `sb_do_train` on the ridge and `sb_do_hold`; `day_lesson` and `day_lesson_reserve` mirror `act_lesson`, `sb_activities.rpy:321-322`; a harness proves they still match; `past_cap` is how far the night may end above the grade ceiling: 0, or 6 if the owner chooses ruling 5's alternative); `dict(cover=1500, bond=4, stamina=0.5, ce=0.7, market="shibuya")`; `{area key or "": str}` |
| `VIEW_TICK` | `view_stage.rpy` (P0, final) | `0.05` |
| `VIEW_SLOTS`, `VIEW_FACE`, `VIEW_BLINK_OK`, `VIEW_TALK_OK` | `view_stage.rpy` (P5) | `{place: {n: [(xcenter, yoffset, zoom, far)]}}`; `{who: dict(eyes=(x,y,w,h), mouth=(x,y,w,h))}` on the sprite canvas; tuples of expressions |
| `SPOT_LINES` | `room_spots.rpy` (P6) | `{hotspot id: [first-person lines]}` |
| `PC_SITES`, `PC_PAGES` | `room_computer.rpy` (P6) | `{site: dict(name, url, tone)}`; `{page: dict(site, title, body=[str], links=[page], needs=None or flag, gives=None or ("insight", n) or ("flag", name))}` |
| `FISH_KINDS` | `room_fishing.rpy` (P6) | `[dict(id, name, min_cm, max_cm, weight, zone, yen_per_cm, periods)]`: six species, `river_lord`, `pale_thing` |
| `CARDS_STYLE`, `CARDS_STAKES`, `CARDS_LIMIT` | `room_cards.rpy` (P7) | `{who: dict(tight=0..1, bluff=0..1, tell=expr, win=str, lose=str)}` for the 11; `(100, 500, 1000)`; `dict(hands=5, down=3000)` |

### 3.3 New store variables (all `default`, plain, safe at default in a replay)

**P0 writes every `default` below into its owner's stub file,** so a package that reads another's state through a contract never meets a missing name, and a postponed package leaves its variables defined. "Owner" is who gives the variable its meaning.

| variable | default | owner | meaning |
|---|---|---|---|
| `night_carried` | `""` | P4b | the place key where the day turned while I wasn't in my room; `""` when none |
| `night_cost_day` | `0` | P4b | the day a next-day cost applies to |
| `night_cost_kind` | `""` | P4b | `"gojo"` or `"out"` |
| `night_gojo_last` | `-99` | P4b | day of the last Gojo night |
| `night_gojo_day` | `0` | P4b | the day tonight's invitation is for |
| `night_out_last` | `-99` | P4b | day of the last night out |
| `market_bought` | `set()` | P4b | once-only stock already bought |
| `mg_result` | `{}` | P0 | the last game's `dict(game, outcome, yen)` |
| `pc_read` | `set()` | P6 | page ids read |
| `pc_requests` | `[]` | P6 | `[(page, note)]` |
| `pc_checked_week` | `-1` | P6 | the `board_week` already cross-checked |
| `fish_log` | `{}` | P6 | species id → longest cm (int) |
| `fish_state` | `{}` | P6 | the sitting in progress; `{}` otherwise |
| `fish_cursed_week` | `-1` | P6 | the week the cursed catch last came up |
| `cards_state` | `{}` | P7 | the sitting in progress (deck as a list of ints); `{}` otherwise |
| `cards_won_day` | `0` | P7 | the day `cards_won` counts for |
| `cards_won` | `0` | P7 | yen won at cards that day |

Flags (in the existing `flags` set): `market_found`, `researched_<page>`, `caught_river_lord`; reserved for Arc Two: `spear_unsealed`, `yaga_signature`. `actions_today` (a set) gains `cards:<who>`, `fish_bond`, `fish_first`, `spot_vend`, `night_toast`, `hot:<id>` (a look hotspot used today). `default persistent.motion = True` (P0) is not in saves. `bound_specials` is not written by phase 2.

### 3.4 Migrations

**None** (D41). `SAVE_VERSION` stays 1; `_validate_grades`' "exactly one migration at order 10" is untouched. Orders 90, 92, 94 and 96 are reserved (nothing checks migration orders, R2); a package that finds it needs one says so in its hand-over note, and P8 (the only package that may edit `sb_hooks.rpy`) raises the version.

What replaces a migration:
- a tool already in my hand stays (D28);
- a save whose `_r` is `("journal", "memories")` opens People;
- the two owner saves parked on `call screen sb_map` (auto-1, auto-2) reopen on the six areas; the one on `call screen sb_place` (1-1) reopens in the new place view;
- a save parked at Night away from the dorm shows "Go to bed"; the next rollover walks it home. `docs/PLAYTEST.md` says so.

---

## 4. Screens

All positions are for 1920×1080. "At rest" is what shows with the pointer elsewhere.

### 4.0 What stays frozen, the only additions, and the clutter budget

| screen | parameters | returns (unchanged) | additions |
|---|---|---|---|
| `sb_map` | `(layer="campus", area=None)` | `("go", loc)`, `("district", key)`, `("cancel",)` | parameter `area`; return `("night", key)` |
| `sb_hud` | `(on_map=False, person=False)` | through its parent | none |
| `sb_place` | `()` | `("map",)`, `("journal","people")`, `("char", who)`, `("act", id)`, `("mission", mid)`, `("dev",)` | return `("hot", id)` |
| `sb_char` | `(who)` | `("do", aid, who)`, `("mission", mid)`, `("act", id)`, `("cancel",)` | none |
| `journal` | `(tab="people")` | `True`, `("arc_two",)` | `("go", loc)`, campus journal only; `"memories"` opens People |
| `armory`, `board_screen`, `board_partner(offer)`, `combat_screen`, `grade_card(key, kicker)`, `jjk_status`, `jjk_journal`, `toasts`, `objective_toast(text)`, `dev_panel` | unchanged | unchanged | `dev_panel` may return `"sample"`; over `sb_place`, `objective_toast` is drawn at `xpos 400` instead of centred (R6) |

Both protected map calls (`call screen sb_map`, `call screen sb_map(layer="tokyo")`) stay byte-identical. `tools/smoke/wp0_stubs.rpy:157` pins the parameter list and is updated by P0.

**Clutter budget** (counted at rest by `zz_words(screen)` and `zz_buttons(screen)` with `gui.icon_words = "never"`; the date chip and the three corner icons are not counted). A **word** is a token that contains a letter: "+2" and "◆ 1" are not words, and the kanji of a stand-in icon is skipped (its `Text` has the style `icon_glyph`), so the count is the same with and without icon art.

| screen | words at most | buttons at most | faces at most | today |
|---|---|---|---|---|
| map, six areas | 20 (six area names: 12; the title: 2; "YOU ARE HERE": 3) | 6 markers + 4 | 18 (three a marker) | about 45 words, 18 rows, 11 faces in a strip |
| map, one area | 16 (the area's name: 2; Back: 2; room plates: up to 10) | 5 pins + 4 | 15 (three a pin) | – |
| place view (after P5) | 2 per person on stage | 8 in the column, 4 hotspots | – | about 60 words and a card |
| place view (after P2, old name plates) | the column itself: 0 | the same | – | – |
| person view | 16 | 4 choices + 2 | – | about 40 words |
| journal, a People card | 6 | 1 | 1 | 6 lines a card |
| journal, a person's page | 70 | – | – | about 150 |

### 4.1 The map: `screen sb_map(layer="campus", area=None)` (`ui_map.rpy`, P1)

Screen variables: `default view = layer` (as now), `default zone = area` (`None` = level 1; an area or district key = level 2).

**Top row (y 26 to 78), both levels:**
- date chip at (40, 26): `use sb_hud(on_map=True)`, unchanged;
- title, `xalign 0.5`, `ypos 28`, display font 36, `gui.paper`: "Jujutsu High" on campus level 1; the area's name at level 2; "Tokyo" or the district's name on the Tokyo layer. No seal, no subline;
- Campus / Tokyo switch: a frame at `xpos 1560`, `ypos 26`, 124×52, with two 56×44 `icon_btn`s (`campus`, `tokyo`); each sets `view` and clears `zone`. Tokyo is a sensitive button with `NullAction()` until `tokyo_open()`, so its label ("Tokyo — after Ijichi's ride-along") still shows;
- Menu icon at x 1816 to 1880 (the HUD);
- nothing else above y 90. The old header block at y 108, the "Find someone" strip (`ui_map.rpy:440-457`), the bottom-right tooltip frame and the "Walking is free" line are removed. `face_chip`, `FACE_BOX`, `map_who_where`, `map_cards`, `map_people` and the `MAP_*` tables stay defined.

The removed tooltip frame includes the `$ _tip` lines P0 adjusted (6.3); every tooltip on the new map is a `(text, key)` tuple drawn by `hover_label`.

**Level 1, campus** (`screen sb_map_campus`, kept by name, rewritten). Ground: `bg map_campus` + ink 0.35.
- Six markers, `button id "area_<key>"`, 300×132, centred on the existing anchors: heart (960, 900), school (420, 740), dorms (900, 560), staff (1560, 440), grounds (1560, 760), mountain (740, 290).
  - Row 1: `icon("area_<key>", 44)` and the name (display 26). Row 2: up to **three** 36×36 `face_chip`s of the people in the area's rooms I can enter, then "+n" (as the pins do). Row 3, only when it applies: gold "◆ n" (`map_waiting`), a `moon` icon when `night_marks().get(key)`, and "YOU ARE HERE" in violet on my area (which uses `panel_active`).
  - Hover: the rooms' names ("Classroom · Cafeteria · Infirmary · Library") and the area's `blurb`.
  - Action: `SetScreenVariable("zone", key)`. Nothing is returned.
- "Stay here": `icon_btn("stay", Return(("cancel",)), wid="map_stay")` at `xalign 1.0`, `xoffset -40`, `yalign 1.0`, `yoffset -30`. Hover: "Stay here\nWalking is free. Doing something takes time."

**Level 2, an area** (`screen map_area(key)`, new). Ground: `AREAS` row `bg` at `map_zoom_in`, then ink 0.30. `map_zoom_in` is an ATL `transform` (zoom 1.12 → 1.0, alpha 0 → 1 over 0.3 s, `easeout`): a displayable that newly appears in a screen starts its ATL from zero, which a function transform's `st` would not (it counts from when the screen was shown, not from when `zone` changed). `p2_map` proves it (alpha is 1.0 half a second after the press); if it does not hold, the fallback is a start time written **at the click**: the marker's action becomes `[SetScreenVariable("zone", key), Function(ui_do, map_zoom_mark)]`, where `map_zoom_mark()` puts the wall clock into `MAP_ZOOM_T0[0]`, a one-element list outside the store (as `ARRIVAL` is in `sb_screens.rpy`; never saved). A literal float inside `SetScreenVariable` would be built when the screen was last drawn, not at the click: the fault 4.13 describes for `Return(("hook", q))`. With `view_motion()` False the picture is simply shown.
- Back: `icon_btn("back", SetScreenVariable("zone", None), w=220, words="always", wid="map_back")` at (40, 96), reading "Jujutsu High".
- One pin per room, `button id "row_<loc>"` (the id the phase-1 harness presses), centred on `map_spots(key)[loc]`: a 72 px disc with `icon("place_<loc>")`; under it a plate with `map_place_name(loc)` (22 px; "Empty Office" still works); beside the disc up to three 36 px faces and "+n"; a gold `news` badge when `map_has_news` or a mission marker; a violet ring on the room I'm in; a `lock` badge when `place_access` refuses, with people hidden.
  - Hover: the room's `desc`, the mission markers' text, or the lock's full reason.
  - Action: `map_row_action(loc)`, unchanged (`Return(("go", loc))`, or `NullAction()` when locked or already here).
- The stand-in picture (until `area_<key>.png` exists) is a 720×405 piece of `map_campus.png` around the anchor, **clamped to the 1920×1080 picture** (heart's anchor at y 900 would otherwise run off the bottom), enlarged and darkened.
- Default spots (overridden by `game/layout/area_<key>.json`):

| area | pins (x, y) |
|---|---|
| heart | courtyard (960, 460) · gate (960, 820) |
| school | classroom (520, 380) · cafeteria (1300, 420) · infirmary (620, 760) · library (1340, 780) |
| dorms | rooftop (960, 260) · dorm (480, 440) · girls_dorm (1440, 440) · dorm_common (960, 640) |
| staff | office (960, 340) · utahime_office (520, 660) · gojo_office (1400, 660) |
| grounds | training (620, 420) · dojo (1320, 420) · storehouse (960, 780) |
| mountain | ridge (960, 280) · forest (480, 700) · riverside (1380, 640) |

  The pin validator rejects a spot outside x 200 to 1700, y 200 to 940.
- Esc: level 2 → level 1; level 1 → `Return(("cancel",))`.

**Tokyo, level 1** (`screen sb_map_tokyo`, kept by name): five district markers at today's `DISTRICT_POS`, `button id "district_<key>"`, 300×132: kanji, name, one chip (the lock reason, or "VISITED"), a `moon` icon when `night_out_ok(key)[0]`. Action: `SetScreenVariable("zone", key)` when the district is open, else `NullAction()` with the reason on hover. The car card and footnote go; "Half a day by car" is the hover hint. **A district marker no longer returns:** `tools/smoke/wp1_world.rpy:619-622` and `654-661` press `district_yotsuka` and `district_harajuku` and expect `("district", key)` back, so P1 turns each into two presses (`district_<key>`, then `district_go`); the locked-Shinjuku check stays a `NullAction` on `district_shinjuku`.

**Tokyo, level 2** (`screen map_district(key)`, new): the district's own `bg` + ink 0.45; Back ("Tokyo") at (40, 96); the pins of `MAP_DISTRICT_SPOTS[key]` as dim icon discs with "Later build" on hover; and at (1180, 760), 560 wide:
- `button id "district_go"`: car icon, "Ride with Ijichi · half a day" → `map_district_action(key)`, unchanged;
- `button id "district_night"`, shown when `key in MAP_NIGHT_DISTRICTS`, the period is Evening or Night, **and `night_out_ok(key)` has something to say** (`ok or reason`; the stub returns `(False, "")`, so with the night out unbuilt or postponed there is no dead button): moon icon, "A night in [district]" → `Return(("night", key))` when `night_out_ok(key)[0]`, else `NullAction()` with the reason on hover. No price on the button: the ¥1,500 is the club's, chosen on arrival (D24).

No toasts over the map (R6).

### 4.2 The HUD: `screen sb_hud(on_map=False, person=False)` (`ui_hud.rpy`, P2)

- Date chip and **status chips** share one `hbox` at (40, 26), `spacing 10`: the date chip first, unchanged in look and position ("Day 12 · Wednesday" is 310 to 350 px wide, so a fixed x for the chips would overlap it), then the chips, each a 36 px icon with a hover label: `moon` when `night_tag()` is non-empty ("Worn out — no missions or training today" / "Rough morning"); `stamina_low` when stamina < 25 ("Running on empty. Eat or sleep.", moved here from above the action card); `skip` while `renpy.is_skipping()`.
- Navigation: the same right-anchored `hbox` (`xalign 1.0`, `xoffset -40`, `ypos 26`, `spacing 10`), three `icon_btn`s 64×52: Map (x 1668 to 1732), Journal (1742 to 1806), Menu (1816 to 1880). Same actions, same `m` / `j` keys, same `on_map` / `person` rules. Hover: "Map (M)", "Journal (J)", "Menu".
- "Review tools" at (40, 1040): unchanged.

**Toasts** (`screen toasts`): position and count from `toast_room()` → `(xpos, ypos, limit)`:

| what is up | returns |
|---|---|
| a scene (no `sandbox` or `menu` screen) | `(1880, 92, 4)` |
| `sb_place` | `(1790, 92, 4)` |
| `sb_char` | `(1722, 26, 2)` |
| `combat_screen` | `(1880, 92, 4)` (as now) |
| `grade_card` showing, **tested by name** (`renpy.get_screen("grade_card")`: it has no tag, `sb_grades.rpy:481-483`, and is called while no `sandbox` screen is up) | `(0, 0, 0)`: they wait |
| anything else tagged `sandbox` or `menu` (the map, journal, board, `board_partner`, armory, market, computer, cards, fishing, `icon_sample`, the game menu) | `(0, 0, 0)`: they wait |
| `dev_panel` (no tag either, `explore.rpy:348-351`; it falls through to the scene row on purpose: the review buttons report through toasts) | `(1880, 92, 4)` (as now) |
| the prologue blackout | `(0, 0, 0)` (as now) |

The tests run in the table's order, except that the `grade_card` test comes first. `toast_limit()` returns `toast_room()[2]`. `toast_tick` leaves every clock stopped while the limit is 0. `objective_toast` is hidden unless `sb_place` is the `sandbox` screen showing, and there it is drawn at `xpos 400`, `xsize 900` (x 400 to 1300), clear of the toast lane that starts at x 1330.

**Preferences** (`screens.rpy`): the "Motion" row for `persistent.motion` is added by P0 (6.3), not here.

### 4.3 Icons and hover labels (`ui_icons.rpy`, P0, final)

- `icon(name, size=40, gold=False)` → a displayable, never stored: `images/icons/ic_<name>.png` scaled to `size` when loadable; else a `Fixed` of `gui/seal_44.png` scaled to `size` with the name's kanji as a `Text` of style `icon_glyph` (`gui.display_heavy_font` at 0.55 × size, `gui.paper`, or `gui.gold` when `gold`); `zz_words` skips that style. An unknown name gives "？" and a `VALIDATE:` line at lint.
- `icon_label(name)` → `str`; `icon_has_art(name)` → `bool`; `icon_for(kind, id)` → an icon name, never `None` (`"act"` when unmapped). The kinds it accepts: `act` (a place action id), `do` (an activity id), `mission` (any mission id: always the `mission` icon), `tab`, `place`, `area`.
- `screen icon_btn(name, action, tip=None, size=52, w=None, gold=False, selected=False, pips=0, wid=None, words=None)`: a button `w or size + 12` wide; the icon centred; `pips` cost diamonds under it; the word under the icon (13 px) when `words == "always"`, or when `words` is `None` and `gui.icon_words` is `"always"`, or `"auto"` and `not icon_has_art(name)`; `tooltip ((tip or icon_label(name)), wid or name)`; `id wid` when given.
- `screen hover_label()`: `zorder 190`; in `config.always_shown_screens`. `$ _hover_t = GetTooltip()`; when it is set: `nearrect: focus "tooltip"  preferred_side "left"` holding a `panel_dark` frame (padding 14, 8; `xmaximum 520`). **It draws only when the tooltip is a 2-tuple;** the text is `_hover_t[0]`. A plain-string tooltip (phase 1's map rows, `ui_map.rpy:400, 455, 506`) is left to the screen that owns it. `"Title\nhint"` draws the first line at 22 in the display font and the rest at 18 dim. Callers that want the label on another side put the button where `nearrect` has no room on the left; it then uses the opposite side by itself.
- `screen icon_sample()` (for checkpoint A): a `sandbox` screen with a row of twelve `icon_btn`s in each of the three `icon_words` modes, the five grade chips at sizes 13 and 18, and one person-view choice button. Returns `("close",)`.

`ICONS`, `ICON_FOR` and `ICON_GOLD` are defined at `init -3 python`, before any file registers a hotspot (6.1).

**The 88 icon names** (kanji in the table; words as shown on hover):

| group | names |
|---|---|
| HUD (9) | `map`, `journal`, `menu`, `back`, `close`, `stay`, `stamina_low`, `moon`, `skip` |
| journal (9) | `people`, `missions`, `stats`, `equipment`, `inventory`, `story`, `memories`, `now`, `go` |
| map (11) | `area_heart`, `area_school`, `area_dorms`, `area_staff`, `area_grounds`, `area_mountain`, `campus`, `tokyo`, `district`, `lock`, `news` |
| places (20) | `place_<loc>` for the 19 rooms and `place_later` |
| actions (18) | `sleep`, `night_bed`, `wait`, `study`, `train`, `swim`, `eat`, `rest`, `think`, `hold`, `tools`, `armory`, `veil`, `car`, `board`, `release`, `mission`, `act` |
| person choices (9) | `talk`, `hang`, `lesson`, `walk`, `stargaze`, `confide`, `stand`, `heart`, `invite` |
| rooms and night (12) | `pc_open`, `cards_play`, `fish_cast`, `lib_study`, `look`, `spot_vend`, `night_gojo`, `night_out`, `market`, `buy`, `take`, `record` |

P0 writes the exact list into `ICONS`; `p2_contracts.rpy` asserts every id in `ACTIVITIES`, every `place_actions` id for every room and period, every registered place action, every tab, area and room maps to a name in it. A wave package that needs a picture for something new uses an existing name.

### 4.4 The place view: `screen sb_place()` (`sb_screens.rpy`, P2) with `view_stage` (P5) and `hot_layer` (P0)

Draw order, bottom to top:

1. `add graded_bg()`, ink 0.10.
2. `use hot_layer(here, front=False)`.
3. `use view_stage(here)`: the people and their name tags (4.5).
4. `use view_fg(here)`.
5. `use hot_layer(here, front=True)`.
6. The overflow chip at (1300, 900): unchanged.
7. "Nobody here right now." at (700, 640): the second sentence about the map is dropped; `tools/smoke/wp7_ui.rpy:445` is updated.
8. The arrival caption at (40, 100): unchanged.
9. **The icon column** (replaces the 440-wide card): a `vbox`, `xalign 1.0`, `xoffset -40`, `yalign 1.0`, `yoffset -40`, `spacing 10`, of 72×72 `icon_btn`s built from `rail_actions(here)`: gold mission icons first, then the actions in order, then Wait (or Go to bed), then `release` last when someone is tagging along (`rail_actions` appends that row itself, 6.1; today's separate "Let them go" link at `sb_screens.rpy:571` goes). Cost shows as pips. More than eight (six when words show): a second column at x 1726 to 1798. Never above y 360.
   - Hover: "Train\nPush my cursed energy. Costs stamina. · 1 period".
   - Returns unchanged: `("act", id)`, `("mission", mid)`.
10. `use sb_hud`.

`_missions` is also empty when `not night_can_work()`, and at Night holds only missions for which `night_allows("mission:" + mid, cost)`. The stage keeps x 40 to 1700.

**Between P0 and P2** the phase-1 action card is still there, but P0 has re-pointed it at `rail_actions` (6.3), so the night rule and the hotspots reach the screen whichever of P2, P4b and P6 lands first.

### 4.5 The stage: `screen view_stage(loc)`, `screen view_focus(who)`, `screen view_fg(loc)` (`view_stage.rpy`; P0 moves today's code in, P5 makes it live)

**P0's version is today's loop, verbatim** (`sb_screens.rpy:405-453`: the stage imagebuttons at 406-416 and the name plates at 418-453): sprites at `STAGE_CENTRES`, the name plates with caption, the same `Return(("char", who))`. **It cannot read `sb_place`'s variables:** a `use`d screen that declares parameters gets a fresh scope holding only its parameters (`renpy/sl2/slast.py`, `SLUse.execute`), so the loop's `_stage`, `_xs`, `_zoom` and `_yoff` would raise NameError. `view_stage(loc)` therefore begins with its own copies of `sb_screens.rpy:388-392` (`$ _stage, _extra = stage_people(loc)`; `$ _xs = STAGE_CENTRES.get(len(_stage), [])`; `$ _st = PLACE_STAGING.get(loc, {})`; `$ _zoom = …`; `$ _yoff = …`), with `here` replaced by `loc`, and then lines 405-453. `sb_place` keeps its own line 388 for the overflow chip and the "Nobody here" test. Lines 402-403 (`add graded_bg()` and the ink) and the overflow chip from line 455 stay in `sb_place`. P0 also writes `VIEW_TICK`, `view_motion()` and `view_person_rects(loc)` here, final. `view_focus(who)` is today's `add person_image(who) at char_focus(_x0)`, and for the same reason computes `$ _x0 = stage_x(who, here)` itself; `char_focus` moves here. Nothing looks different after P0.

**P5's version:**

- **Where people stand, as rectangles.** `view_person_rects(loc)` → one `(x, y, w, h)` for each person on stage now (P0: from `STAGE_CENTRES` and the sprite size at the room's zoom, about 395×728; P5: from `view_slots`, or the pose box when a pose is drawn). Hotspots use it to stay out from behind people (4.10).
- **Slots.** `view_slots(loc, n)` → n tuples `(xcenter, yoffset, zoom, far)`. Default: today's centres and `PLACE_STAGING` zoom, with the middle people 4% smaller, 10 px higher and `far=1`. `VIEW_SLOTS` (and a sidecar's `"slots"`) override per place; rows ship for `dorm_common`, `cafeteria`, `classroom`, `courtyard`, `training`, `infirmary`, `library`, `utahime_office`. `far` 1 or 2 adds `blur 0.8 × far` and dims 2% per step, as a fixed property on the sprite. `stage_x(who, loc)` (in `sb_screens.rpy`) keeps working: P0 re-points it at `view_slots`.
- **Light.** `view_sync_light()` runs before the place view opens (P0's hook) and sets `scene_light = light_for_place(here, period)`, fixing the stale tint after Wait, Study and the others.
- **Breathing.** A wall-clock function transform (`view_breathe_fn`, top-level, curried with the phase; R10): `yzoom` 1.0 ↔ 1.006 over 4.2 s about the feet, each person offset by a phase from their name; returns `VIEW_TICK`. Off for a pose picture and when `view_motion()` is False.
- **Name tags.** A 36-high tag with the short name (20 px, the person's colour) and the gold 「!」 / NEW badge (NEW is hidden while `night_allows("hang", 1)` is False: no badge for a scene the night won't let me start), at `ypos 1036` under the feet, so the contact shadow shows. The caption moves to the hover label (over the person or the tag).
- **Poses.** `view_pose(who, loc, per=None)` → `dict(image, box)` or `None`. `image` is the file's path as a `str`, never a displayable (a screen may hold the dict in a `$` variable, and screen scope is pickled, R10); the displayable is built in the `add` line. It looks for `images/place/pose_<loc>__<who>__<variant>.png` when `bg_variant(loc, per)` names a painted variant, else `images/place/pose_<loc>__<who>.png`. With a painted variant and only the day file: `None` (the sprite). `box` is `(x, y, w, h)` from the sidecar `game/layout/view_<loc>.json` key `"poses"`; with no box, the whole picture, and only when that person is alone on the stage. The box is cropped, given a 24 px feathered edge (`AlphaMask` with `gui/soft_box.png`, generated by `tools/gen_gui.py` in P0c; a hard edge until that file exists), tinted like the background when `graded_bg` tints it, and drawn at its own position as a `button` (hover: brightness +0.08) returning `("char", who)`.
- **Foreground.** `view_fg(loc)` adds `images/fg/fg_<loc>_<variant>.png` or `fg_<loc>.png` when loadable, tinted like the background. Files ship for `dorm_common` (three variants), `cafeteria`, `classroom`, `utahime_office`.
- **Idle to talking:**

| join | today | phase 2 |
|---|---|---|
| place → person view | hard cut | `view_before_person(who)` queues `renpy.transition(Dissolve(0.25))` |
| person view | `char_focus(x0)` from a fixed zoom 0.52 | `char_focus(x0, y0=-40, z0=0.52)` starts from the person's own slot; a pose fades out over 0.3 s as the talking sprite fades in |
| person view → dialogue | pops from x 520 / 0.66 to x 960 / 0.64 | `view_enter(who, expr)` shows the sprite `at` the ATL transform `view_enter_ease` (from (520, 0.66) to `pos_c`'s place over 0.35 s, timed by `st`), and the foreground layer above it (`zorder 5`, tag `view_fg`, a plain image) |
| dialogue → place | hard cut | `view_after_scene()` queues `renpy.transition(Dissolve(0.25))` for the next interaction (the `call screen sb_place`), as `view_before_person` does. Not `renpy.with_statement`: that would dissolve to the empty room and then cut to the people |

  In a replay (`_in_replay`) `view_enter` does exactly what it does today: no ease, no foreground. A `scene` statement clears the foreground.

  **These two are shown on the master layer, so they are saved and rolled back (R10).** `view_enter_ease` is an ATL `transform` statement; nothing `view_enter` shows carries a function defined inside another function. With `view_motion()` False the sprite is shown at `pos_c` as today.
- **Blink and talk** (cuttable). `lit_sprite(path, size, feet)` (`lighting.rpy`) derives `<who>` and the expression from the path; when `images/char/fx/fx_<who>_blink.png` or `fx_<who>_talk.png` is loadable and `VIEW_FACE[who]` has a box, it adds two small layers to the sprite's `Fixed`: the eye box cropped from the blink picture (shown 0.12 s every 3 to 6 s, on `VIEW_BLINK_OK` expressions) and the mouth box cropped from the talk picture (alternating 0.12 s while `VIEW_SPEAKING[0] == who`, on `VIEW_TALK_OK` expressions). Both layers are function transforms on a sprite that dialogue shows with `show`, so their functions are top-level (`view_blink_fn`, `view_talk_fn`), curried with `who` (R10). `VIEW_SPEAKING` is a `builtins.list([None])`, set by a `config.all_character_callbacks` entry. Without the files the sprite's structure is exactly today's. `jjk_sprites.rpy` and `jjk_defs.rpy` are not edited; `tools/gen_sprite_defs.py` only reads `images/char/*.png`, so the `fx/` folder is invisible to it.

### 4.6 The person view: `screen sb_char(who)` (`sb_screens.rpy`, P2)

- Background as now; the person through `use view_focus(who)` (ends at xcenter 520, zoom 0.66).
- Card: `jjk_panel`, `xpos 1180`, `ypos 190`, `xsize 640`, `ymaximum 850`, padding (20, 20):
  1. `use grade_chip(<the person's grade key>, size=18)`: "GRADE 2"; "OFF THE SCALE" on the sheen for Gojo; the role ("DOCTOR") in a plain chip for people with no grade;
  2. the choices from `person_choices(who, here)`, each a 600-wide button: `icon(choice["icon"], 40)` at the left, the label (display 24; gold for a mission, rose for romance), cost pips at the right; the hint is the hover label. Returns unchanged;
  3. footer: an `invite` icon button ("Ask them along" / "Let them go") and Back (`id "sb_char_back"` kept).
- Removed: the name, the role line, the caption, the bond and affection rows, the thread title and pips, the "Closer" hint. `person_thread`, `unlock_line` and `role_line` stay defined.
- `person_choices` dicts carry `icon` (`icon_for(choice["kind"], choice["id"])`, added by P0b, 6.3; a mission choice gets the `mission` icon); nothing unpacks them by position.
- Toasts at (1722, 26), two at most; the card starts at y 190 to stay clear.

### 4.7 The journal: `screen journal(tab="people")` (`ui_journal.rpy`, P3)

Chrome, rail and body keep their geometry (rail 0 to 320; body 1520×928 at x 360, y 112).

- **Rail:** five tab buttons (first at y 148, then every 86 px), each `icon(<tab>)` with the word beside it (the rail is a table of contents and has room). `journal_state(tab)` maps `"memories"` to `"people"` explicitly.
- **People grid** (`jr_people`): cards 288×196, five across (5 × 288 + 4 × 20 = 1520), **inside a viewport** (mousewheel; the bar shows only when the content is taller than the body). Order: Me, the met cast in roster order, Sana. Thirteen cards fit in three rows without scrolling, which is everyone Arc One can meet. `JOURNAL_CAST` has 17 people (`sb_missions.rpy:41-63`); with all of them met and the Me card that is 18 cards in four rows (844 px), which still fits the 928 px body without scrolling. The viewport is for phase 4's larger cast (a fifth row is 1,060 px).
  - At rest: a 72×72 face chip, the name (display 24, their colour), `grade_chip`, a 248×6 bond bar, one dim line with their place right now ("Cafeteria", "With me", "Off campus"). A gold dot when something is new with them.
  - Hover: "Next: …" (`jr_next`).
  - Not met yet: one row at the bottom, "NOT MET YET", of 72×72 silhouettes with the hint on hover.
  - Me: the journal portrait and my grade chip → `jr_go(js, sel="me")`.
- **A person's page** (`jr_person_detail(js, who)`, rebuilt). Panel 1520×928:
  - left, x 0 to 420: the neutral sprite at zoom 0.5;
  - header at x 450, y 24: name (display 40), `grade_chip`, year; "← Back" chip top right. y 84: bond bar 620×10 with rank and number; affection bar at x 1100 when it applies; the promotions line (dim 16);
  - **Right now** at (450, 140), 1040×112, `panel_dark`: line 1 (22): `person_now(who)`'s name and doing ("Cafeteria — halfway through an enormous bowl"; "With me"; "Somewhere I can't go right now"; "Off campus"); line 2 (dim 16): "Usually: …" (`usual_places`); line 3 (gold 16): the "Closer: …" hint (`unlock_line`); at the right edge a `go` icon button, only in the campus journal and only when `reachable` → `Return(("go", loc))`. Opened mid-scene (not `journal_editable()`), line 1 is omitted and the panel is headed "Usually";
  - two chips at (450, 270): **Their story** · **Memories n/m** (`js["psub"]`, default `"story"`);
  - a 1040×584 viewport at (450, 320):
    - *Their story:* `jr_story_rows(who)`: the thread's title as a heading; each learned stage line as a done row; character missions slotted in after the stage that unlocks them, else in act order. The first row not done is the **NEXT** row (gold rail): the step and where ("Spend time together — Bond 35 · usually the Cafeteria at noon"). Unwritten missions collapse into one dim row ("2 more chapters in a later build");
    - *Memories:* `jr_memory_tile` tiles 280×158, three across, from `memories_with(who)`. An unseen tile shows the entry's `text`, so an unmet partner is never named.
  - Sana's page: an "In memory" chip, no Right now panel, Memories open.
- **The Me page** (`jr_me_detail(js)`, new): the journal portrait left; right, two chips: **My story** (`memory_groups("act")` without Bonds, as tiles under act headings; it holds the three `who=()` scenes) and **Records** (pages read on the computer by title, the fishing record book, today's card winnings; see below). A "Stats →" link to the Stats tab.
- **Stats** (`jr_stats_tab`), lighter: portrait left; right, three chips, one pane at a time (`js["ssub"]`): **Overview** (grade line, promotion bar, six bars), **Last Light**, **My year**.
- **Missions:** unchanged, plus one section at the top, **Leads**, shown only when `pc_leads()` is non-empty: one row per lead, "Look up what was on the ridge — my computer" (dim, with the `pc_open` icon; display only).
- **Equipment, Inventory:** unchanged, except every grade chip becomes `use grade_chip(key, …)`; the tool picker shows `can_hold`'s reason and the checklist; **the talisman picker and the item panels of both tabs show `item_requirements(id)` as the same ✓ / ✗ chips the armory uses** (nothing when the list is empty).
- **Records** on the Me page reads only three contract functions, `pc_records()`, `fish_records()` and `cards_records()` (6.1), never another package's tables, and hides a section whose list is empty.
- New `js` keys: `psub`, `ssub`, `msub2` (the Me page's chip); `sel` accepts `"me"`. `mem_mode` and `mem_who` stay in the dict, unused.
- No toasts over the journal (R6).

### 4.8 Grade colours (`sb_grades.rpy`: functions P0, sites by their owners)

`screen grade_chip(v, size=13, text=None, dim=False)`: a frame with background `grade_fill(v)`, padding (10, 3), the text `(text or grade_label(v))` upper-cased and bold, in `gui.ink` (in `gui.paper` on the Special chip); `dim=True` draws at alpha 0.45. No grade: `panel_ghost` and dim text.

`grade_fill("sp")` is a clipped `Fixed`: `Solid(gui.grade_sp_base)` and `gui/grade_sheen.png` (1024×64, tileable) at alpha 0.85, panned by a wall-clock function transform (`grade_sheen_fn`, top-level; still when `view_motion()` is False), 14 s a loop. Never stored. Until `grade_sheen.png` exists the fill is a flat `gui.grade_sp`; P0c draws the strip **before checkpoint A** (7.3), so the owner judges the real Special chip on the style sample.

| site | file (owner) | change |
|---|---|---|
| journal chips (people card, person page, board view, equipment, picker, inventory) | `ui_journal.rpy` (P3) | `use grade_chip(key, …)`; Gojo passes `text="Off the scale"` |
| board card and partner chips | `sb_board.rpy` (P4a) | `board_grade_chip(g, size)` becomes `use grade_chip(g, size)` (name kept) |
| grade card | `sb_grades.rpy` (P4a) | the 64 px label takes `grade_color(key)`; for `sp` it sits on a 560×6 sheen rule |
| combat header | `sb_combat.rpy` (P4a) | `grade_chip(cb.get("grade"), 16)` left of "ROUND n"; the enemy's name stays red |
| armory rows and "MY GRADE" | `sb_items.rpy` (P4a) | `grade_chip`, `dim=True` when sealed |
| market rows | `sb_market.rpy` (P4b) | `grade_chip` |
| person view | `sb_screens.rpy` (P2) | 4.6 |

Sentences that name a grade (toasts, lock reasons) stay uncoloured.

### 4.9 The armory: `screen armory()` (`sb_items.rpy`, P4a)

- Each row gains one wrapped line under the effect text, inside the 990-wide column: `item_requirements(id)` as chips, spacing 8: "✓ Grade 2" (paper) or "✗ Output 50 · I have 32" (seal red). The marks use `JR_SYMBOL_FONT`. Height +28 px a row; five rows end near y 900, clear of the footer at y 1000.
- `armory_tools()` keeps its five state names and today's reason strings for today's cases (`wp6_items.rpy` pins them): `sealed` set → `arcii`; owned → `owned`; rack kind `story` → `story`; then any unmet requirement → `("sealed", <first unmet line>)`, where an unmet grade still reads "Sealed until Grade 3"; else `take`.
- `can_hold(id)` adds the same test for a tool not already in my hand; `can_wear(id)` adds it after its existing checks, for a talisman not already worn (D28). The talisman rows of `ITEM_REQS` (D27) are shown in the journal (4.7) and at the market (4.16); the armory lists tools only, as today.
- Returns unchanged.

### 4.10 Hotspots (`sb_hotspots.rpy`, P0 final; content in `room_spots.rpy`, P6)

- `register_hotspot(id, place, x, y, icon, act=None, lines=None, label="", hint="", cost=0, when=None, standalone=False, front=False)` → `None`. Three kinds:
  - **an action hotspot** (`act` set; default kind when `lines` is None, with `act = id`): it stands for a row of `place_actions(place)`. It has no label, hint or cost of its own (the validator rejects one that sets them): those come from the action's row, so they cannot drift;
  - **a look hotspot** (`lines` set): its own `label`, optional `when` (the name of a store function);
  - **a standalone hotspot** (`standalone=True`): an action that exists only as a hotspot and is in no `place_actions` list (`spot_vend` is the one that ships). It carries its own `label`, `hint`, `cost` and must carry `when`. Hidden in explore mode. **It is always drawn on the front layer (`front` is forced True) and is exempt from the person-rectangle rule below,** because no column row would offer it while it was hidden (pose 11 paints Yuji beside the vending machine every afternoon, and his pose box would otherwise remove the machine).
- **Visible** means all of: registered for this place; for an action hotspot, **its `act` is in `{a[0] for a in place_actions(loc)}` right now and `night_blocks(act)` is False** (so a used-up "Get patched up", a closed board, `veil` after one look, and explore mode, where only `explore_time` is offered, all remove the hotspot as they remove the button); for the other kinds, `when` is true; and, **for an action or a look hotspot, its 72 px square is clear of every rectangle in `view_person_rects(loc)`** (a standalone skips this test). A hotspot that is not visible is not drawn, and an action hotspot's action then stays in the column. Nothing is ever both hidden behind a person and missing from the column.
- `hot_spots_for(loc)` → the visible rows as dict copies, with the sidecar's point (`game/layout/hot_<loc>.json`) applied and, for an action hotspot, `label`, `hint` and `cost` filled from the action's row. `hot_covers(loc)` → the `set` of action ids a visible action hotspot offers.
- `screen hot_layer(loc, front=False)`: each row is a 72×72 `icon_btn` centred at (x, y) on a soft ring (`gui/hot_ring.png`, drawn by `tools/gen_gui.py`; a plain circle until it exists) that pulses between alpha 0.45 and 0.8 over 2.4 s (a wall-clock function transform, top-level, still when `view_motion()` is False). Action: `Return(("hot", id))` for a look; `Return(("act", act))` when `night_allows(act, cost)`; else `NullAction()`, dim, with "Too late. Bed." on hover.
- `label hot_use(id)`: says `lines[day % len(lines)]`, adds `"hot:" + id` to `actions_today` (a set: it records that the spot was used today, not how often), returns. Reached by P0's new `elif _r[0] == "hot"`.
- Validator: the place is in `LOCATIONS`; `sb_do_<act>` exists (unless `lines`); `when` is a store function; a standalone has `when`; an action hotspot sets no label, hint or cost; the icon is in `ICONS`; the point is inside x 40 to 1700, y 180 to 1000 and outside both lanes; a standalone's point is clear of the default stage rectangles for one to four people (it has no column to fall back to); no duplicate id.
- `sb_hotspots.rpy` defines its registries and `register_*` at **`init -5 python`** (as `sb_hooks.rpy:20` does), because `room_*.rpy` sort before `sb_hotspots.rpy` and Ren'Py runs equal priorities in filename order. Every `room_*.rpy` registers at init 0 or later.
- The first set (points are P6's to fix on each background with `tools/layout_sheet.py`):

| place | hotspot → action | start (x, y) |
|---|---|---|
| dorm | computer → `pc_open` · bed → `sleep` | (1240, 600) · (420, 760) |
| dorm_common | card table → `cards_play` (offered by `place_actions` only while `cards_ok()`) · TV → look | (900, 800) · (1420, 520) |
| riverside | the bank → `fish_cast` | (1180, 820) |
| library | the stacks → `lib_study` · a locked shelf → look | (520, 520) · (1480, 460) |
| courtyard | vending machine → `spot_vend` (standalone; ¥150, stamina +10, once a day; `when="spot_vend_ok"`) | (1500, 640) |
| classroom | blackboard → look | (760, 360) |
| cafeteria | the counter → `eat` | (1200, 560) |
| infirmary | the cot → `rest` | (640, 700) |
| storehouse | the racks: **two rows at one point,** `armory` and `tools` (the room never offers both: `tools` only before `armory_open`) | (960, 560) |
| utahime_office | the board → `board` | (1320, 420) |
| ridge | the veil → `veil` | (960, 420) |

Existing actions only move from the column to the room; their ids, labels and `when` rules are untouched. Train, Practice, Hold the hour, Wait and missions stay in the column.

Several start points sit where people stand (the card table at (900, 800), which only matters when someone is in the room; the cot at (640, 700) beside Shoko at x 700; the counter at (1200, 560) with four people in the cafeteria; the bank at (1180, 820)). The visibility rule handles that at run time: with someone in the way the icon goes and the action is in the column. P6 still moves each point, on the layout sheet, to where it is clear in the room's usual crowd.

### 4.11 The computer: `screen pc_screen(page="home")` (`room_computer.rpy`, P6)

- Entry: place action `pc_open` at `dorm` ("My computer", free), with a hotspot. `label sb_do_pc_open` loops `call screen pc_screen(_pc_page)` like `sb_do_armory`.
- `tag sandbox`, `modal True`. A browser window at (210, 110), 1500×860: a title bar (40 high) with the `close` icon → `Return(("close",))`; an address bar (48 high) with the page's made-up address; a left column 300 wide of bookmarks grouped by site, a gold dot on unread pages → `Return(("page", id))`; a 1140×700 viewport: the site's name in its own colour, the title (display 34), paragraphs (20), links as gold text buttons → `Return(("page", id))`, and a gold strip "Noted." when a first read gave something.
- **Sites and pages** (about 100 words a page, each in its site's voice, consistent with `docs/ANTAGONISTS.md`; no page addresses the reader):

| site (voice) | pages |
|---|---|
| a folklore wiki (dry, cited) | `sukuna_folk`; `sukuna` (needs `saw_the_ridge_veil`) |
| a rumour blog (breathless) | `gojo` ("the man in the blindfold") |
| the school intranet, Ijichi's login (careful, bureaucratic) | `home`; `techniques` (gives Insight +2, in place of the usual +1); `board_reports` |
| a genealogy site (stiff, proud) | `clans`; `clan_gojo`; `clan_kamo`; `clan_zenin` (each ends on a "restricted" line: the seeds for the later arc) |
| an urban-legends board (anonymous posts) | `legends`; `legends_market` (gives flag `market_found`; **listed, linked and counted only when `market_exists()`,** so a postponed market leaves no page pointing at nothing) |

- Home: "Requested reading" from `pc_requests` at the top, then the sites as cards. One request ships: once `saw_the_ridge_veil` is set and `sukuna` is unread, "What was that on the ridge?" → `sukuna`. `pc_leads()` → the open requests as `(page, note)`; the journal's Missions tab shows them as leads (4.7). `pc_records()` → the titles of the pages read, for the Me page.
- Site colours are tokens in this file (`define gui.pc_wiki`, `gui.pc_blog`, …; 2.1).
- `board_reports`: this week's offers by title and posted grade; a button "Cross-check the reports · 1 period" → `Return(("check",))`. The label refuses at Night ("Too late. Bed."), else sets `pc_checked_week`, calls `advance_period_soft(1)` and reopens; a checked week shows "This one doesn't add up." in gold on every offer whose `true_grade != grade` (read-only on `board_offers`, checking `taken_by` first).
- Under `smoke_autoplay` a 0.05 s timer returns `("close",)`.

### 4.12 Cards (`room_cards.rpy`, P7; the interface in `sb_hotspots.rpy`, P0)

- **The interface:** `register_minigame(id, name, icon, min_people=1)` → `None`; `mg_games()` → list of dict copies; a game is `label mg_<id>(opponents, stake=0)` (the list of people at the table, then the yen staked a hand; a game with no stake ignores it), which plays until I leave, keeps its state in its own plain dict, and before `return` sets `mg_result = dict(game=id, outcome="win"|"lose"|"even"|"quit", yen=n)`. Chess later is one file and one register call.
- Entry: place action `cards_play` at `dorm_common`, `when="cards_ok"` (someone is there, I have ¥100, and I haven't sat today with everyone present), cost 1, with a hotspot. It costs a period and is not in `NIGHT_OK`, so at Night the table is closed (D20). Opponents: `who_is_here("dorm_common")`, at most three.
- `screen cards_table()`: the common room + ink 0.6; a 900×520 panel at (510, 280): the opponents' face chips and names; one large button per `mg_games()` row; stake chips from `CARDS_STAKES` (dim when I can't cover one); my yen top right; Leave. Returns `("play", game, stake)`, `("close",)`. `label sb_do_cards_play` keeps the opponents in `_cards_opp` and starts the game with the protected `call expression "mg_" + _cards_r[1] pass (_cards_opp, _cards_r[2])` (2.3); the game's label builds its state with `cards_new(game, opponents, stake)`.
- `screen cards_blackjack()`: the dealer (the first opponent) as a side portrait at xcenter 480; a table panel x 760 to 1840, y 140 to 940: the dealer's hand at y 200, mine at y 520 (cards 120×168, drawn by the engine: a `panel_solid` rectangle, the rank at 44, the suit glyph from DejaVu Sans in `gui.cards_red` / `gui.cards_black`, tokens of this file; a face-down card is `gui/card_back.png` from `tools/gen_gui.py`, or a flat panel until it exists); totals beside each hand; the dealer's one-line reaction at y 420 with their face changing; buttons at y 840: Hit, Stand, Double, Leave. Returns `("hit",)`, `("stand",)`, `("double",)`, `("leave",)`. The dealer stands on 17; a win pays 1:1, a natural 3:2; a push returns the stake.
- `screen cards_poker()`: five-card draw. Opponents' card backs and side portraits along y 180, **each portrait wearing the expression their style gives away** (Yuji bluffs and it shows; Megumi shows nothing; Nobara raises when annoyed; Panda can't hide a good hand; Toge is unreadable; Gojo plays blind); the pot at y 400; my five cards at y 560 (click to mark a discard, three at most: `ToggleDict`); a `look` icon button at (1700, 560), once a hand, when Insight ≥ 20: shows one opponent's hand strength as a five-step bar; buttons at y 840 by stage: Check / Bet / Fold → Draw → Check / Bet / Fold → showdown. Returns `("bet",)`, `("check",)`, `("fold",)`, `("draw", (i, …))`, `("read", who)`, `("leave",)`.
- A sitting ends after five hands, when I'm ¥3,000 down, or when I leave; it costs one period if a hand was played (`advance_period_soft(1)`). Bond +1 with each opponent once a day. I can never stake more than I hold (the label checks `yen` first; `add_yen` clamps and returns `None`). Winnings past `BOARD_YEN["g4"][1]` in a day are refused with a line ("Megumi folds his cards. \"That's enough of my money.\"").
- State lives in `cards_state` (plain values; `renpy.random` shuffles), built by `cards_new(game, opponents, stake)` and cleared on exit. **The label calls `renpy.block_rollback()` after every deal, every draw and every settlement,** so I can't roll back past a lost hand and play it again knowing the next card. `cards_records()` → `dict(today=<yen won today>)` for the Me page. No toasts over the table.
- Under `smoke_autoplay` a timer plays "stand" / "check" and leaves after one hand.

### 4.13 Fishing: `screen fish_screen()` (`room_fishing.rpy`, P6)

- Entry: place action `fish_cast` at `riverside` ("Fish", cost 1), with a hotspot.
- `tag sandbox`, `modal True`: the riverside background; a float at (1100, 700) that dips after 1 to 3 s; then a 600×28 bar at (660, 860) with a marker sweeping across twice and a green zone whose width is the species' `zone`; a "Hook!" button (also Space or a click) whose action is **`fish_Hook()`**, a named Action class (R4): its `__call__` reads the wall clock against the sweep's start time (a float kept in `fish_state` when the bite begins), works out where the marker is, and returns `("hook", q)`. A plain `Return(("hook", q))` would carry the `q` of the last redraw, not of the click. Top left: three hook icons, "Cast 2 of 3". A `record` icon opens a 700×600 panel: each species, my best, "???" for ones not caught. Returns `("hook", q)` with `q` 0.0 to 1.0, `("miss",)`, `("leave",)`.
- After each cast `fish_land(kind, cm)` → `dict(id, cm, yen, record)` pays `cm × yen_per_cm`, updates `fish_log` (it only rises), gives the day's first catch its Control +1 (skipped when `not night_can_work()`: nothing raises Control on a rest day), and a result line shows ("Ayu, 21 cm. A new best."). **`renpy.block_rollback()` follows every settled cast** (a catch or a miss), so a cast can't be taken again. `fish_records()` → `[(name, cm or None)]` for the record panel and the Me page.
- The River Lord: Evening only, weight 0.03, needs `q ≥ 0.9`; ¥5,000 once; sets `caught_river_lord`. The pale thing: Evening only, at most once a board week; gives one `sealing_talisman` and a line.
- After three casts: `advance_period_soft(1)`. Under `smoke_autoplay` a timer returns `("hook", 0.5)`.

### 4.14 The Library (`sb_world.rpy` and `bg_placeholders.rpy`: the place, P0; pins and schedule, P1; `room_library.rpy` P6 for what to do)

- `bg library` = `bg_placeholder("images/bg/library.png", <classroom.png cropped and tinted warm>)`, one word after `bg` (`light_for_bg` matches on two).
- `lib_study` "Study in the stacks" (cost 1, stamina 8): a `menu` of three shelves with first-person captions (theory: Insight +4; barrier craft: Control +2, Insight +2; history: Insight +4). On a rest day (`not night_can_work()`) the barrier-craft shelf gives its Insight +2 only: nothing raises Control or Output that day (4.15). "Study together" works there (P2). The locked shelf is a look hotspot.

### 4.15 The night (`sb_night.rpy`, P4b)

No new full screen; the rule shows through the existing ones.

- **`night_filter_actions(loc, acts)`** (called by `rail_actions`, never by `place_actions`): in explore mode, or before `settled_in` is set, `acts` comes back unchanged. Otherwise, in this order: (1) **at any period,** every row whose id `night_blocks()` is dropped (a rest day; nothing is dropped on an ordinary day); (2) **then, only at Night:** `wait` is dropped; `("night_bed", "Go to bed", "Walk back to my room and sleep. The day ends.", 0)` is appended everywhere but `dorm` (where `sleep` already is); with `NIGHT_STRICT`, every row with cost > 0 whose id is not in `NIGHT_OK` is dropped. With `NIGHT_STRICT` off those rows stay and their hint gains " · ends the night".
- **`night_allows(id, cost)`** → `bool`: what hotspots, the column's missions, `person_choices` (for a person's mission, step 1) and `activity_state` (for every activity, the confession included) ask; 6.3 gives the exact lines. Not Night, or not settled, or explore mode: True. At Night with `NIGHT_STRICT`: True when `cost == 0` or `id in NIGHT_OK`. A mission is asked as `"mission:" + mid`: True when the mission's `periods` include Night or its cost is 0. `night_allows("hang", 1)` is False at Night, which also hides the NEW badge (4.5).
- **`night_blocks(id)`** → `bool`: True on a no-work day when `id in NIGHT_REST_BLOCKS`. **One table, read in every place:** `night_filter_actions` drops those rows from the column (and so from the hotspots, which follow the column); `activity_state` refuses those activity ids with `night_block_reason()`.
- **On a no-work day** (`not night_can_work()`): nothing in `NIGHT_REST_BLOCKS` is offered: Train, Practice and "Train together" (`train`), Gojo's lesson (`lesson`), Hold the hour (`hold`, Control +2, `sb_loop.rpy:304-328`) and swimming (`swim`, Output +2, `sb_loop.rpy:200-221`). Missions are not offered in the column or on people; the board refuses ("Not today. I can barely stand."). Study, eating, talking, cards, fishing and the computer stay, **but nothing raises Control or Output that day:** the two other sources this phase adds test `night_can_work()` themselves and skip the gain (the Library's barrier-craft shelf, 4.14; the first catch of the day, 4.13). `night_exists()` → `bool` is True once this file is real (the stub says False); the review panel asks it (4.16).
- **`label sb_do_night_bed`:** one line when I'm not in my room ("I walk back while I can still feel my feet."), `here = "dorm"`, `scene expression graded_bg()`, the existing sleep text, `new_day()`.
- **`label night_carry_home`** (called at the top of the loop when `night_pending()`): the line from `NIGHT_CARRY_LINES` for where the day turned, `here = "dorm"`, `scene expression graded_bg()`, `night_carried = ""`.
- **A Gojo night:** a new-day hook (order 55) sets `night_gojo_day = day`, pins him (`pin("gojo", "ridge", day, "Night")`) and toasts when `night_gojo_due()`. `register_place_action("night_gojo", "Train until morning", "More than a day's worth. Tomorrow I'm no use to anyone.", cost=1, locs=("ridge",), when="night_gojo_ok", order=5)`. `label sb_do_night_gojo`: a `menu` ("A whole night with Gojo. Tomorrow I won't be fit for missions or training." → Stay / Not tonight; taken as Stay under `smoke_autoplay`), a short placeholder scene in "I", `night_gojo_apply()`, `night_set_cost("gojo")`, `here = "dorm"`, `new_day()`, `scene expression graded_bg()`, "Day [day]. Morning." If the gains came to nothing, no cost is set.
  - `night_step(cur, amount)` → `int`: what `gain` would add at `cur`, without changing anything. It applies **both cuts in sequence, exactly as `gain` does** (`sb_energy.rpy:110-114`): `if cur >= 60: amount = max(1, int(amount * 0.6))`, then `if cur >= 85: amount = max(1, int(amount * 0.5))` (so 4 becomes 2, then 1, at 85 and above; the two are not alternatives).
  - `night_day_best()` → `int`: the Control the best day of training would add from my Control now. A day is `len(PERIODS)` one-period steps and one free step of `NIGHT_GOJO["day_hold"]`. Two days are walked through `night_step`: **the lesson day** (one step of `NIGHT_GOJO["day_lesson"]` and `len(PERIODS) - 1` steps of `NIGHT_GOJO["day_step"]`) and **the all-train day** (`len(PERIODS)` steps of `day_step`), each with the hold. Order matters near 60 and 85 (a day that holds first can gain one more), so the result is **the maximum over every position of the hold and of the lesson** among the steps (at most 6 × 5 orderings). From Control 30 it is 23; from 55, 16; from 70, 12.
  - `night_gojo_gain()` → `(control, reserve)`: `(night_day_best() + NIGHT_GOJO["over"], max(len(PERIODS), NIGHT_GOJO["day_lesson_reserve"] + len(PERIODS) - 1) + NIGHT_GOJO["reserve_over"])`: the reserve of the better of the two days (a train gives 1, `sb_loop.rpy:245`; the lesson gives 5; the hold gives none) plus 3, which is 12 today against a lesson day's 9.
  - `night_gojo_apply()` → `(control_gained, reserve_gained)`: calls `gain("control", 1, quiet=True)` once per point (every call gives exactly one point at any Control, because `gain` never gives less than 1), then `raise_reserve`, then one toast with the totals. With `NIGHT_GOJO["past_cap"]` above 0, once `gain` stops at the ceiling the remaining points, at most `past_cap` of them, are added by `store.control = min(100, store.control + 1)` (`gain` lives in frozen `sb_energy.rpy` and clips; it never lowers a value already above the cap, so the extra points stay).
  - `night_gojo_due()` also needs `room + NIGHT_GOJO["past_cap"] > night_day_best()`, where `room = (grade_cap("stat") or 100) - control` (`grade_cap` returns `None` at Special Grade, `sb_grades.rpy:109-112`; `gain` treats that as 100), and room under the reserve cap for the whole reserve gain (`grade_cap("reserve")` of `None` means no cap, as `raise_reserve` reads it). With less room a night could not beat a day, so none is offered. With `past_cap = 0` that means no night at the ceiling below Semi-Grade 1 (D23; section 0, ruling 5).
  - The mirror can't drift unseen: `p2_night` runs the real thing (five `sb_do_train` at every place whose `place_actions` offers `train`: `training`, `dojo`, `ridge`, `forest`, `courtyard`, `riverside`; the lesson day on the ridge, `act_lesson` through its label on a day Gojo is in plus four `sb_do_train`; each with one `sb_do_hold`, run hold-first and hold-last; and "Train together" with each partner) and fails if any real day beats `night_day_best()` on Control or the night's reserve on `ce_max`.
- **A night in Tokyo:** `("night", key)` → `label night_out(key)`: returns at once unless `night_out_ok(key)[0]`; a line for the last train in; then one `menu` ("[district], after dark."):
  - **"The club · ¥1,500"** (shown dim with "Not enough yen" when I can't cover it): `add_yen(-1500)`; a placeholder scene (the club, whoever came along, Bond +4 for a companion); in Shibuya, the first time, **and only when `market_exists()`**: I find the stairs (`flag("market_found")`; with the market unbuilt the line is not said and the flag is not set); then, when `market_found` and `market_exists()`, a second `menu` "The Black Market" (`call market_open`) / "Home";
  - **"The Black Market"** (only in `NIGHT_OUT["market"]`, with `market_found` and `market_exists()`): `call market_open`. No door charge;
  - **"Head home"**: `return`. Nothing is charged, no time passes, no cost is set.

  After the club or the market I was out all night: `night_set_cost("out")`, `here = "dorm"`, `new_day()`. Under `smoke_autoplay` the club is taken when affordable, else home; at the second menu autoplay takes Home.
- **The next day:** a new-day hook (order 80, after the refill) applies a night out's stamina and cursed energy and clears a cost whose day has passed. A hook at order 5 sets `night_carried = here` when the day turns, I'm not in `dorm`, and explore mode and replays are off.
- Explore mode: none of it applies.

### 4.16 The Black Market and the review tools

**`screen market_screen()`** (`sb_market.rpy`, P4b), modelled on `armory`: `tag sandbox`; a `jjk_panel` at (110, 36), 1700 wide; header "The Black Market" with my yen in gold at the right; one row per `market_rows()` entry: `grade_chip`, name, description, effect text, the requirement chips, the price, and Buy (or the reason: "Can't afford it", "Sold"); footer "Effects wake up with the combat update."; Close at (1590, 1000). Returns `("buy", id)`, `("close",)`. `label market_open` loops like `sb_do_armory`; `market_buy(id)` checks `yen >= price` before `add_yen(-price)` and `give_item(id)`. It never touches `bound_specials`. `market_exists()` → `bool` (True once P4b is in; the stub says False), which the computer's rumour page, the night menu and the review button ask before they mention the market.

| stock | grade | price | price ceiling (D29) |
|---|---|---|---|
| `borrowed_luck`, `night_eyes` | Grade 3 | ¥9,000, ¥12,000 | 3 × 10,000 |
| `debt_marker` | Grade 2 | ¥24,000 | 3 × 15,000 |
| `second_wind` | Semi-Grade 1 | ¥45,000 | 3 × 20,000 |
| `sealing_talisman`, `first_aid` | Grade 4 / ungraded | ¥800, ¥500 (not once-only) | 3 × 6,000 / ¥3,000 |

Each talisman row shows its requirement chips (D27). The three story Specials (`unending_moment`, `the_zone`, `finger_wrap`) are not stock. If the owner asks for a Special Grade talisman here (section 0), it is a new item made with `_item(…, grade="sp", special=True, source="The Black Market")`, priced under 6 × 20,000, and the question of what binding it means for the later story Specials (PHASE1 3.8: one bound special) goes back to the owner with it.

**Review tools** (`explore.rpy`, P0): six more `DEV_BUTTONS`, each a `dev_*` function that returns `None` and calls a contract function: "Jump to Night", "Gojo night tonight" (`night_dev("gojo")`), "Tomorrow is a rest day" (`night_dev("rest")`), "+¥20,000", "Find the Black Market" (`night_dev("market")`), and "Style sample" (in `DEV_SCENES`; `dev_tools` gains `elif _return == "sample":` / `call screen icon_sample`). A `DEV_BUTTONS` row may carry `when` (the name of a store function); the grid skips a row whose `when` is False. "Find the Black Market" has `when="market_exists"`; "Gojo night tonight" and "Tomorrow is a rest day" have `when="night_exists"` (`night_dev` is a no-op stub until P4b, so without the test they would be buttons that do nothing at checkpoint A, and for good if P4b were postponed). "Jump to Night", "+¥20,000" and "Style sample" work from P0b.

---

## 5. Art and ComfyUI

**The rule:** nothing waits for art. Every row has a stand-in the engine draws, and the file drops in by name. Costs: the edits and paintings (rows 1, 6, 7) use Nano Banana at about $0.32 a picture; the backgrounds (rows 2 to 5) use `tools/make_bg_workflow.py`, which is Krea 2 at about $0.035 a picture and renders two candidates a place (its docstring), so about $0.07 a background. The Nano Banana rows are costed at one $0.32 run a picture; **whether that workflow bills one run or each of its two candidates is not known from the tools** and is settled on the first icon sheet (P0c's hand-over note says what the sheet cost). If each candidate is billed, rows 1, 6 and 7 double.

**A hand-off is the same four steps every time:** 1. Claude runs the row's tool, which writes a drag-in workflow `.json` into `~/Desktop/JJK Game images/phase2/`, already loaded with the pictures and the prompt. 2. You drag it into ComfyUI and press Run (two candidates). 3. You say which candidate. 4. Claude runs the install command; it resizes, checks and writes the game file, and shows you a preview in `shots/art/`. Nothing in the script changes.

| # | picture | drop-in file (under `game/`) | stand-in | made with | count | cost |
|---|---|---|---|---|---|---|
| 1 | Icon sheets (three sheets of 30 white line icons, 6×5) | `images/icons/ic_<name>.png` ×88, 96×96 | the kanji seal with its word | `tools/make_icon_workflow.py`; `tools/cut_icons.py <sheet> tools/icons/sheet_<n>.txt` (the names on that sheet, in order) | 3 | $0.96 |
| 2 | Six area bird's-eye pictures | `images/bg/area_heart.png`, `area_school.png`, `area_dorms.png`, `area_staff.png`, `area_grounds.png`, `area_mountain.png` | a 720×405 piece of `map_campus.png` around the area's anchor (clamped to the picture), enlarged and darkened | `tools/make_bg_workflow.py` with `tools/bgs/prompts/area_<key>.txt`; `tools/install_bg.py` | 6 | $0.42 |
| 3 | Tokyo overview (owed since phase 1) | `images/bg/map_tokyo.png` | the night skyline, dimmed | the same, with `tools/bgs/prompts/map_tokyo.txt` | 1 | $0.07 |
| 4 | The Library | `images/bg/library.png` | the classroom, cropped and warmed | the same, with `library.txt` | 1 | $0.07 |
| 5 | Utahime's office, Gojo's office (owed since phase 1; needed before their poses) | `images/bg/utahime_office.png`, `gojo_office.png` | phase 1's tinted stand-ins | the same, with `utahime_office.txt` and `gojo_office.txt` | 2 | $0.14 |
| 6 | People in their places | `images/place/pose_<place>__<who>[__<variant>].png`, 1920×1080 | the standing sprite, blended | `tools/make_pose_workflow.py <place> <who> [variant]`; `tools/install_pose.py <render>` | 14 | $4.48 |
| 7 | Blink and talk | `images/char/fx/fx_<who>_blink.png`, `fx_<who>_talk.png` (edits of `<who>_neutral.png`, same canvas) | no blinking, no mouth | `tools/make_edit_workflow.py` with two new prompts; `tools/install_face.py` | 20 | $6.40 |
| 8 | Foreground layers | `images/fg/fg_<place>[_<variant>].png` | none | `tools/make_fg.py <place>`: cut from the background itself | 6 | free |
| 9 | Special Grade sheen, the hotspot ring, the soft box for poses, the card back | `gui/grade_sheen.png`, `gui/hot_ring.png`, `gui/soft_box.png`, `gui/card_back.png` | drawn by `tools/gen_gui.py` (P0c); before that, a flat colour, a plain circle, a hard edge, a flat panel | a painted file of the same name may replace any of them | 4 | free |

**47 paid pictures, about $12.54 in all (37 at $0.32, ten backgrounds at $0.07); $6.14 without blink and talk.** `make_bg_workflow.py` exits with "no prompt for …" unless `tools/bgs/prompts/<name>.txt` exists (`make_bg_workflow.py:195-196`), and today that folder has none of the ten: P0c writes all ten prompt files (the six areas, `library`, `map_tokyo`, `utahime_office`, `gojo_office`). Sana's blink and talk would be two more ($0.64); she is left out because she is only in the prologue (section 0). Playing cards and the browser are drawn by the engine.

**The 14 poses** (each on the picture shown at the hour that person is there; P5 checks every row against `when_at(who, place)` and drops one the schedule never produces before you pay for it):

| # | who · place · variant | doing | painted on |
|---|---|---|---|
| 1 | nobara · dorm_common · evening | on the sofa, on her phone | `dorm_common_evening.png` |
| 2 | utahime · utahime_office | at her desk, buried in paperwork | `utahime_office.png` (row 5 first) |
| 3 | yuji · cafeteria | halfway through an enormous bowl | `cafeteria.png` |
| 4 | megumi · classroom | reading at a desk by the window | `classroom.png` |
| 5 | shoko · infirmary | at the counter with coffee | `infirmary.png` |
| 6 | maki · training | drilling with a staff | `training.png` |
| 7 | yaga · office | sewing a cursed doll | `office.png` |
| 8 | ijichi · gate | on the phone beside the car | `gate.png` |
| 9 | toge · cafeteria | with onigiri, at the far table | `cafeteria.png` |
| 10 | panda · courtyard | stretching, waiting for a sparring partner | `courtyard.png` |
| 11 | yuji · courtyard | beside the vending machine, a can in his hand (the prompt keeps him to one side of it; the machine's hotspot is drawn in front of every pose box anyway, 4.10) | `courtyard.png` |
| 12 | megumi · library | three books deep | `library.png` (row 4 first) |
| 13 | gojo · gojo_office | on the sofa, eating mochi in front of the TV | `gojo_office.png` (row 5 first) |
| 14 | gojo · ridge | sitting just outside the veil (seen on a Gojo night) | `ridge.png` |

The storyboard's "Nobara on the rooftop" and "Megumi at the riverside" are added (two more, $0.64) only if P5's schedule check finds them there.

**What protects a pose.** The workflow gives Nano Banana the exact background and the neutral sprite, never the character's name, and asks for the person in a named spot doing the thing, "change nothing else". `install_pose.py` compares the result with the background: if more than 35% of the picture changed it refuses and says so (run the other candidate); otherwise it measures the box (the largest connected changed region grown by 24 px; D37 says what counts as changed, and `--box` overrides it), writes it to `game/layout/view_<place>.json` (the file P5 owns; hotspot points live in `hot_<place>.json` and are never touched), writes a side-by-side preview, and installs the file.

**The order, tied to checkpoints:**

| batch | when | what | cost |
|---|---|---|---|
| 1 | after checkpoint A, while wave 1 builds | the icon sheets, the six areas, the Tokyo overview: the first things you see at checkpoint B | $1.45 |
| 2 | after checkpoint B | the Library, the two offices | $0.21 |
| 3 | after checkpoint C | **the tests:** Yuji's blink and talk; poses 1 and 2 (your two examples). Judge them in play before anything else is paid for | $1.28 |
| 4 | if batch 3 looked right | poses 3 to 14 | $3.84 |
| 5 | if Yuji's blink looked right | blink and talk for the other ten on campus (Gojo and Yaga: talk only) | $5.76 |

---

## 6. Contracts (frozen by P0)

### 6.1 Symbols

P0 writes every symbol in its owner's file with its final signature, a docstring naming the owner and the return value, and the stub shown. **The return value is part of the contract** (R3), and **every function row has a stub** (`ZZ_RETURNS` and the owning-file check run on every function row at P0). The three rows marked "arrives with" (two map screens, the `fish_Hook` class) are used only inside their owner's own screens and are asserted in that package's own harness (`p2_map.rpy`, `p2_rooms.rpy`), not in `ZZ_RETURNS`: `p2_contracts.rpy` is frozen after wave 0 and no wave package edits it. "Final" means P0 writes the real thing.

**Init order, frozen.** Ren'Py runs files of equal init priority in filename order, and every `room_*.rpy` sorts before `sb_hotspots.rpy` and `ui_icons.rpy`. So: `sb_hotspots.rpy` (registries, `register_hotspot`, `register_minigame`) and `sb_rules.rpy` at `init -5 python`; `ICONS`, `ICON_FOR`, `ICON_GOLD` at `init -3 python`; `ITEM_REQS = {}` in `sb_items.rpy` at its existing init -1; every `room_*.rpy`, `sb_night.rpy` registration and `sb_market.rpy` stock at init -1 or later as stated in 3.1, with all `register_hotspot` / `register_minigame` calls at init 0 or later. `p2_contracts` proves it with `aa_zz_order.rpy` (R2).

| symbol | file (owner) | returns | P0 stub |
|---|---|---|---|
| `ui_do(fn, *args, **kwargs)` | `ui_icons.rpy` (P0) | `None`, always | final |
| `icon(name, size=40, gold=False)` | P0 | a displayable; never stored | final |
| `icon_label(name)`, `icon_for(kind, id)` | P0 | `str` | final |
| `icon_has_art(name)` | P0 | `bool` | final |
| screens `icon_btn(name, action, tip=None, size=52, w=None, gold=False, selected=False, pips=0, wid=None, words=None)`, `hover_label()`, `icon_sample()` | P0 | –; `icon_sample` returns `("close",)` | final |
| `grade_tier(v)` | `sb_grades.rpy` (P0) | `"g4"`, `"g3"`, `"g2"`, `"g1"`, `"sp"` or `None` | final |
| `grade_color(v)` | P0 | hex `str` (`gui.dim` when ungraded) | final |
| `grade_fill(v)` | P0 | a displayable; never stored | final |
| `grade_is_special(v)` | P0 | `bool` | final |
| screen `grade_chip(v, size=13, text=None, dim=False)` | P0 | – | final |
| `advance_period_soft(n=1, loc=None)` | `sb_world.rpy` (P0) | `bool`: True if the day rolled, as `advance_period`. `loc` is where a waiting beat is looked for (default `here`) | final |
| `rule_hangout_gate(e)` | `sb_rules.rpy` (P0) | `bool` | final |
| label `rule_walk_to(loc)` | P0 | `return`; moves only if `can_enter(loc)[0]`, else says why | final |
| `rule_layout(name)` | P0 | `dict` (`{}` when there is no sidecar) | final |
| **sidecar schemas** (JSON; lists, not tuples; every key optional) | written by P1 / P5 / P6, read by `rule_layout` (P0b) and `tools/layout_sheet.py` (P0c) | `area_<key>.json`: `{"spots": {"<loc>": [x, y]}}`. `view_<place>.json`: `{"slots": {"<n>": [[xcenter, yoffset, zoom, far], …]}, "poses": {"<who>" or "<who>__<variant>": [x, y, w, h]}}` (`<n>` is the number of people, `"1"` to `"4"`, as a string). `hot_<place>.json`: `{"spots": {"<hotspot id>": [x, y]}}`. Not a sidecar, tool input only: `tools/fg/<place>.json`: `{"<variant, or \"\" for the day picture>": [[x, y], …]}` (one polygon each; read by `make_fg.py` and `layout_sheet.py`, never by the game) | frozen; no file exists at P0 |
| `register_hotspot(id, place, x, y, icon, act=None, lines=None, label="", hint="", cost=0, when=None, standalone=False, front=False)` | `sb_hotspots.rpy` (P0) | `None` | final |
| `hot_spots_for(loc)` | P0 | `list` of dicts `(id, x, y, icon, label, hint, cost, act, lines, standalone, front)`: only the visible ones (4.10) | final |
| `hot_covers(loc)` | P0 | `set` of action ids | final |
| screen `hot_layer(loc, front=False)`; label `hot_use(id)` | P0 | `("act", id)` or `("hot", id)` through its parent; `return` | final |
| `register_minigame(id, name, icon, min_people=1)`; `mg_games()`; a game is `label mg_<id>(opponents, stake=0)` | P0 | `None`; `list` of dicts; `return`, having set `mg_result` | final (no game registered) |
| `rail_actions(loc)` | `sb_screens.rpy` (P0) | `list` of `(id, label, hint, cost, icon, gold)`: `night_filter_actions(loc, place_actions(loc))` without the ids in `hot_covers(loc)`, then, when `companion` is set, the row `("release", "Let them go", <hint>, 0, "release", False)` **last** | final |
| `VIEW_TICK`; `view_motion()` | `view_stage.rpy` (P0) | `0.05`; `bool` (`persistent.motion`) | final |
| `view_person_rects(loc)` | `view_stage.rpy` (P0 from `STAGE_CENTRES`; P5 from slots and pose boxes) | `list` of `(x, y, w, h)`, one per person on stage now | today's centres and sprite size |
| `place_actions(loc)` | `sb_screens.rpy` | `list` of `(id, label, hint, cost)`, **exactly as today** | untouched |
| `toast_room()` | `ui_hud.rpy` (P2) | `(int, int, int)`: xpos, ypos, limit | today's behaviour |
| `person_now(who)` | `sb_world.rpy` (P1) | `dict(place=key or None, name=str, doing=str, reachable=bool, hidden=bool, with_me=bool)`; never `None` | `dict(place=None, name="Off campus", doing="", reachable=False, hidden=False, with_me=False)` |
| `map_spots(key)` | `ui_map.rpy` (P1) | `dict` `{loc: (x, y)}` | `{}` |
| `AREAS` rows have `bg`, `blurb`, `spots` | `sb_world.rpy` (P1) | – | keys present, `spots={}` |
| screen `sb_map(layer="campus", area=None)`; screens `map_area(key)`, `map_district(key)` | `ui_map.rpy` (P1) | 4.0 | parameter added, today's body; the two new screens arrive with P1 |
| `ambient_of(who, loc)` | `sb_screens.rpy` (P2) | `(caption, expression)`, as today | untouched |
| `person_choices(who, loc=None)` | `sb_activities.rpy` (P2) | as today, each dict with `icon` (`icon_for(choice["kind"], choice["id"])`) | today's plus `icon`, added by P0b (6.3); P2 does not add it again |
| `journal(tab)` accepts `"memories"`; may return `("go", loc)` | `ui_journal.rpy` (P3) | 4.0 | the alias only |
| `jr_story_rows(who)` | P3 | `list` of `dict(kind, title, line, state, where, next)` | `[]` |
| `ITEM_REQS` | `sb_items.rpy` (P4a; `sb_market.rpy` adds rows) | `dict` | `{}` |
| `item_requirements(id)` | `sb_items.rpy` (P4a) | `list` of `(str, bool)` | `[]` |
| `item_requirements_met(id)` | P4a | `bool` | `True` |
| `item_validate_reqs()` (a registered validator) | `sb_items.rpy` (P0b) | `list` of `str` findings: D27's cap, Insight and flag-words checks over every row of `ITEM_REQS`, whichever file added it | final (nothing to check while `ITEM_REQS` is `{}`) |
| `market_exists()` | `sb_market.rpy` (P4b) | `bool` | `False` |
| `market_rows()` | P4b | `list` of `(id, price, state, reason)`, state in `buy`, `sold`, `poor` | `[]` |
| `market_buy(id)` | P4b | `bool` | `False` |
| label `market_open`; screen `market_screen()` | P4b | `return`; `("buy", id)` / `("close",)` | `return`; an empty screen that returns `("close",)` |
| `night_pending()` | `sb_night.rpy` (P4b) | `bool` | `False` |
| `night_can_work()` | P4b | `bool` | `True` |
| `night_exists()` | P4b | `bool`: the night rule is built | `False` (hides the two review buttons that need it, 4.16) |
| `night_block_reason()`, `night_tag()` | P4b | `str` (`""` when clear) | `""` |
| `night_filter_actions(loc, acts)` | P4b | `list` of `(id, label, hint, cost)` | `acts` unchanged |
| `night_allows(id, cost)` | P4b | `bool`; `id` is an action or activity id, or `"mission:" + mid` | `True` |
| `night_blocks(id)` | P4b | `bool`: closed today because of a rest day | `False` |
| `night_marks()` | P4b | `dict` `{area key: "moon"}` | `{}` |
| `night_out_ok(key)` | P4b | `(bool, str)` | `(False, "")`, which hides the map's night button (4.1) |
| `night_gojo_ok()`, `night_gojo_due()` | P4b | `bool` | `False` |
| `night_day_best()`; `night_gojo_gain()` | P4b | `int`; `(int, int)` | `0`; `(0, 0)` |
| `night_set_cost(kind)`, `night_dev(kind)` | P4b | `None` | no-op |
| labels `night_carry_home`, `night_out(key)`, `sb_do_night_bed`, `sb_do_night_gojo` | P4b | `return` | `return` (`sb_do_night_bed` calls `sb_do_sleep`) |
| screens `view_stage(loc)`, `view_focus(who)`, `view_fg(loc)` | `view_stage.rpy` (P5) | `("char", who)` through the parent; –; – | today's stage loop and `char_focus`, moved; empty |
| `view_slots(loc, n)` | P5 | `list` of n `(xcenter, yoffset, zoom, far)` | today's centres, zoom and y, `far` 0 |
| `view_pose(who, loc, per=None)` | P5 | `dict(image, box)` or `None`; `image` is a path `str`, `box` a 4-tuple of `int` | `None` |
| `view_sync_light()`, `view_before_person(who)`, `view_after_scene()` | P5 | `None` | no-ops |
| `view_enter(who, expr=None)` | P5 | `None` | today's `renpy.show(person_image(who, expr), at_list=[pos_c])` |
| `pc_has_read(page)` | `room_computer.rpy` (P6) | `bool` | `False` |
| `pc_request(page, note="")` | P6 | `None` | no-op |
| `pc_leads()` | P6 | `list` of `(page, note)`: open requests, for the Missions tab | `[]` |
| `pc_records()` | P6 | `list` of `str`: titles of pages read, for the Me page | `[]` |
| `fish_land(kind, cm)` | `room_fishing.rpy` (P6) | `dict(id, cm, yen, record)` | `dict(id=kind, cm=cm, yen=0, record=False)`, changing nothing |
| `fish_records()` | P6 | `list` of `(name, cm or None)` | `[]` |
| class `fish_Hook` (an Action) | P6 | `__call__` returns `("hook", q)`, `q` a float 0.0 to 1.0 | arrives with P6 (used only by P6's own screen) |
| `cards_ok()`; `cards_new(game, opponents, stake)` | `room_cards.rpy` (P7) | `bool`; the fresh `cards_state` `dict` | `False`; `{}` |
| `cards_records()` | P7 | `dict(today=int)` | `dict(today=0)` |
| `spot_vend_ok()` | `room_spots.rpy` (P6) | `bool` | `False` |
| labels `sb_do_pc_open`, `sb_do_fish_cast`, `sb_do_lib_study`, `sb_do_spot_vend`, `sb_do_cards_play` | P6, P6, P6, P6, P7 | `return` | `return` |

### 6.2 Who calls whom across packages

| caller (owner) | calls | how |
|---|---|---|
| `rail_actions` (P0, in P2's file) | `place_actions`, `night_filter_actions` (P4b), `hot_covers` (P0), `icon_for` (P0) | run time |
| `sb_place`, `sb_char` (P2) | `view_stage`, `view_focus`, `view_fg` (P5), `hot_layer` (P0), `grade_chip` (P0), `night_can_work` (P4b) | `use`; a screen-level test |
| `sb_hud` (P2) | `night_tag` (P4b) | text |
| `activity_state`, `person_choices` (P2) | `night_can_work`, `night_block_reason`, `night_allows`, `night_blocks` (P4b); `icon_for` (P0) | P0's hook lines |
| `sb_map` (P1) | `night_marks`, `night_out_ok` (P4b) | badges, the night button |
| `sb_loop.rpy`, `sb_tokyo.rpy` (frozen) | `night_pending`, `night_carry_home`, `night_out` (P4b); `view_sync_light`, `view_before_person`, `view_after_scene` (P5); `rule_walk_to`, `hot_use`, `advance_period_soft` (P0) | P0's hooks |
| `stage_person` (P2's file, P0's edit) | `view_enter` (P5) | a `$` line |
| `hot_layer` (P0) | `night_allows` (P4b), `view_motion` (P0) | run time |
| journal (P3) | `person_now` (P1), `grade_chip` (P0), `item_requirements` (P4a), `pc_leads`, `pc_records`, `fish_records` (P6), `cards_records` (P7), `ambient_of` (P2) | run time; never another package's tables or variables |
| `hot_spots_for` (P0) | `place_actions`, `view_person_rects` (P0, then P5), `night_blocks` (P4b), `rule_layout` (P0) | run time |
| `room_computer.rpy` (P6), `sb_night.rpy` (P4b), `explore.rpy` (P0) | `market_exists` (P4b); `explore.rpy` also `night_exists`, `night_dev` (P4b) | run time |
| `room_library.rpy`, `room_fishing.rpy` (P6) | `night_can_work` (P4b) | run time: no Control on a rest day (4.13, 4.14) |
| board (P4a's file) | `night_can_work`, `night_block_reason` (P4b) | P0's hook lines |
| night (P4b) | `market_open` (P4b), `gain`, `raise_reserve`, `pin`, `new_day`, `add_yen`, `add_bond` | labels |
| rooms (P6), cards (P7) | `advance_period_soft`, `add_yen`, `add_bond`, `gain`, `give_item`, `night_allows`, `register_hotspot`, `register_minigame` | labels, init |

No screen calls `market_buy`, `advance_period_soft`, `night_set_cost`, `give_item`, `add_yen` or `fish_land`; each is reached by a `Return(tuple)` to a label (R4). `fish_Hook` only reads the clock and returns a tuple.

### 6.3 Hooks P0 places in other files

Each is a new line calling a contract above. No existing statement's text changes except the three marked **edited** in the protected files, none of which is a return site (D43), the `renpy.show` line of `stage_person` (in `sb_activities.rpy`, not a protected file; the label, its name and its signature stay), and the screen lines marked **screen** (screens are not protected statements; their names and returns are, and those do not change).

| file | where | new line(s) |
|---|---|---|
| `sb_loop.rpy` `sandbox` | after `$ ensure_state()` | `if night_pending():` / `call night_carry_home` |
| | before `$ check_objective()` | `$ view_sync_light()` |
| | after the `"act"` branch | `elif _r[0] == "hot":` / `call hot_use(_r[1])` |
| | after the `arc_two` `if`, inside the journal branch | `elif isinstance(_j, tuple) and _j and _j[0] == "go":` / `call rule_walk_to(_j[1])` |
| `sb_loop.rpy` `sb_travel` | after the `district` branch | `elif _m[0] == "night":` / `call night_out(_m[1])` |
| `sb_loop.rpy` `sb_person` | before `call screen sb_char(who)` | `$ view_before_person(who)` |
| `sb_loop.rpy` `sb_activity` | after each of the four `scene expression graded_bg()` | `$ view_after_scene()` |
| | line 134 (**edited**; it follows an `if`, and the return site of the `call expression` above is line 128) | `advance_period(_a["cost"])` → `advance_period_soft(_a["cost"])` |
| | line 107 | **not touched** (it is the return site of `call play_event(_e)`; a hangout costs one period, so the soft clock would change nothing) |
| `sb_tokyo.rpy` `sb_do_car` | after its `district` branch | `elif _car[0] == "night":` / `call night_out(_car[1])`. **Defensive, unreachable today:** `sb_do_car` returns at once unless `car_action_ok()`, which needs Morning, Noon or Afternoon (`sb_tokyo.rpy:101-111, 194-195`), and the map shows `district_night` only in the Evening or at Night. The night out is reached through `sb_travel`. The branch is kept so that a later change to the car's hours cannot make the map return a tuple this label drops |
| `sb_tokyo.rpy` `sb_trip` | line 184 (**edited**; it follows a Say, which is the return site of the `call expression` above it) | `advance_period(2)` → `advance_period_soft(2, loc="gate")`: the clock is charged one line before `$ here = "gate"`, so the waiting beat must be looked for at the gate, not at the place I left |
| `sb_missions.rpy` `start_mission` | line 1138 (**edited**; inside an `if`, after `$ _sm_event = None`, which is the return site) | the cost charge uses `advance_period_soft` |
| `sb_events.rpy` | init | `register_event_gate(rule_hangout_gate)` is called from `sb_rules.rpy`; no line here changes |
| `sb_screens.rpy` | new function | `rail_actions(loc)` (final); `stage_x` re-pointed at `view_slots` |
| `sb_screens.rpy` `sb_place` | the stage loop and name plates (lines 405-453; **screen**) | replaced by `use hot_layer(here)`, `use view_stage(here)`, `use view_fg(here)`, `use hot_layer(here, front=True)`. `view_stage(loc)` opens with its own copies of lines 388-392 with `here` → `loc` (a `use`d screen with parameters cannot see the caller's variables, 4.5); `sb_place` keeps line 388 for the overflow chip and "Nobody here"; `_missions` also empty when `not night_can_work()`, and filtered by `night_allows("mission:" + mid, cost)` |
| `sb_screens.rpy` `sb_place` | the action card's `$ _acts = place_actions(here)` (**screen**) | `$ _acts = [a[:4] for a in rail_actions(here) if a[0] != "release"]`: identical output with the stubs, and from then on the night rule and the hotspots reach the phase-1 card too, so nothing depends on P2 landing |
| `ui_map.rpy` `sb_map` | after `$ _tip = GetTooltip()` (line 276; **screen**) | `$ _tip = _tip if isinstance(_tip, str) else None`, so the old tooltip frame never prints a tuple; P1 removes the frame |
| `sb_world.rpy`, `bg_placeholders.rpy` | data | the `library` place (3.1) |
| `sb_items.rpy` | data | `ITEM_REQS = {}`, the two stub functions, and the validator `item_validate_reqs` (final, registered with `register_validator`; D27) |
| `sb_screens.rpy` `sb_char` | the sprite line | `use view_focus(who)` (which computes `_x0 = stage_x(who, here)` itself) |
| `sb_activities.rpy` `stage_person` | the `renpy.show` line | `$ view_enter(who, expr)` |
| `sb_activities.rpy` `person_choices` | step 1 (`sb_activities.rpy:233-237`) | `ms` is also empty when `not night_can_work()`, and is filtered to the missions for which `night_allows("mission:" + mid, MISSION_BY_ID[mid]["cost"])` (step 1 builds its choice with `cost=0` and never passes through `activity_state`, so without this line a costed mission such as `cm_ijichi_1` is still offered on a person at Night) |
| `sb_activities.rpy` `person_choices` | where each choice dict is built | each dict gains `icon = icon_for(choice["kind"], choice["id"])` |
| `sb_activities.rpy` `activity_state` | **two places:** inside the confession block, after the `confession_ready` test and before its `return` (line 122), and before the last `return True, None` | `(False, night_block_reason())` when `night_blocks(a["id"])`; `(False, "Too late")` when `a["cost"]` and `not night_allows(a["id"], a["cost"])`. The confession (`rom_say`, cost 2, not in `NIGHT_OK`) returns early at lines 118-122, before the last return, so it needs its own copy of the two tests |
| `sb_board.rpy` `board_take_reason`, `board_refusal` | first test | `night_block_reason()` when `not night_can_work()` |
| `screens.rpy` `skip_indicator` | around the frame | `if not renpy.get_screen(("sandbox", "menu")):` |
| `screens.rpy` `preferences` | one new row | "Motion": on / off for `persistent.motion` (`default persistent.motion = True` sits in `view_stage.rpy`) |
| `explore.rpy` | `DEV_BUTTONS`, `DEV_FUNCS`, `DEV_SCENES`, the grid (skips a row whose `when` is False), `dev_tools` | 4.16; one new `elif` |

---

## 7. Work packages

```
Wave 0 (sequential)  P0a tooling, checks, baseline  →  P0b the game scaffold
                     →  P0c art and layout tooling (small)                     → checkpoint A
Wave 1 (parallel)    P1 map and world · P2 HUD, icon column, person view, toasts
                     P3 journal · P4a grades on cards, gear · P4b night, market → checkpoint B
Wave 2 (parallel)    P5 the place view alive · P6 rooms · P7 cards             → checkpoint C
Wave 3 (sequential)  P8 integration                                             → checkpoint D
```

Nine packages. Two of them are too big for one agent and are split for good: P0 into three sittings, P4 into two. That makes twelve sittings: three in wave 0, five agents in wave 1, three in wave 2, one in wave 3. Elsewhere in this document "P0" means its three sittings together and "P4" both halves; where it matters the sitting is named.

### 7.1 Size, and what happens when one fails

| package | new or changed lines (about) | harness | agent sittings |
|---|---|---|---|
| P0a | 600 tools, 150 harness | `p2_contracts.rpy` (the tooling half) | 1 |
| P0b | 900 game | `p2_contracts.rpy` (the contracts half) | 1 |
| P0c | 350 tools, 10 prompt files | none (its outputs are files; acceptance below) | 1, small |
| P1 | 550 | `p2_map.rpy` | 1 |
| P2 | 600 | `p2_hud.rpy` | 1 |
| P3 | 700 | `p2_journal.rpy` | 1 |
| P4a | 400 | `p2_gear.rpy` | 1 |
| P4b | 450 | `p2_night.rpy` | 1 |
| P5 | 600 game, 350 tools | `p2_view.rpy` | 1 |
| P6 | 750 (half of it page text) | `p2_rooms.rpy` | 1 |
| P7 | 550 | `p2_cards.rpy` | 1 |
| P8 | 400 | `phase2_all.rpy`, `p2_saves.rpy` | 1 |

The splits are not optional. P0 as one sitting was 13 tasks across about 30 files and the only package that edits protected statements; a failed sitting there is the costliest. P0a touches no game file, so "today's tree is clean under every new check" is proved before a line of the game changes.

**Failure rule (D51).** A package whose harness fails gets one retry, given the failure log. If it fails again, the orchestrator stops and asks the owner whether to spend more or postpone it. A wave merges without a failed or postponed package: its stubs stay, the game stays playable, and section 7.3 says what the owner then doesn't see. A wave package never edits a frozen file; if it needs a change there it writes the request in its hand-over note for P8. **Dropping something the owner decided (SCOPE section 5) is the owner's call, never an agent's** (7.3).

### 7.2 File ownership (per wave; within a wave every file under `game/` and `tools/` has one owner)

| owner (wave) | files |
|---|---|
| P0a (0) | `tools/check_content.py`, `tools/smoke.sh`, `tools/smoke/_lib.rpy`, `tools/smoke/p2_contracts.rpy`, `tools/smoke/aa_zz_order.rpy`, `tools/smoke/baseline_globals.txt`, `tools/smoke/baseline_check_content.txt`, `tools/smoke/baseline_p0.json`, `tools/smoke/baseline_shots/` (the two pre-P0 screenshots), `tools/prefixes.json`, `tools/none_ok.txt`, `tools/load_all_saves.sh`; any phase-1 `wp*` harness that fails under the new `_lib.rpy` |
| P0b (0) | every `game/` file named in 6.1, 6.3 and tasks 7 to 13: `gui.rpy`, `ui_icons.rpy`, `sb_hotspots.rpy`, `sb_rules.rpy`, `view_stage.rpy`, the seven stub files, `sb_grades.rpy`, `sb_world.rpy`, `bg_placeholders.rpy`, `sb_items.rpy` (stubs), `sb_screens.rpy`, `sb_activities.rpy`, `sb_board.rpy` (two hook lines), `ui_map.rpy` (the parameter, one line), `ui_hud.rpy` (the `toast_room` stub), `ui_journal.rpy` (stubs, the alias), `screens.rpy`, `explore.rpy`, `sb_loop.rpy`, `sb_tokyo.rpy`, `sb_missions.rpy`; `tools/smoke/p2_contracts.rpy` (the contracts half), `tools/smoke/assets/p2_contracts/` (its two test sidecars), `tools/smoke/wp0_stubs.rpy`, and any `wp*` harness its changes break (`wp11_dev.rpy` among them, if it pins the review panel's buttons or size). `sb_hooks.rpy` is not edited |
| P0c (0) | `tools/layout_sheet.py`, `tools/gen_gui.py`, `game/gui/grade_sheen.png`, `game/gui/hot_ring.png`, `game/gui/soft_box.png`, `game/gui/card_back.png`, `tools/make_icon_workflow.py`, `tools/cut_icons.py`, `tools/icons/sheet_1.txt`, `sheet_2.txt`, `sheet_3.txt`, `tools/bgs/prompts/area_*.txt`, `tools/bgs/prompts/library.txt`, `map_tokyo.txt`, `utahime_office.txt`, `gojo_office.txt` |
| P1 (1) | `game/sb_world.rpy`, `game/ui_map.rpy`, `game/bg_placeholders.rpy`, `game/layout/area_*.json`, `tools/smoke/wp1_world.rpy`, `tools/smoke/p2_map.rpy`, `tools/smoke/assets/p2_map/` |
| P2 (1) | `game/ui_hud.rpy`, `game/sb_screens.rpy`, `game/sb_activities.rpy`, `tools/smoke/wp7_ui.rpy`, `tools/smoke/p2_hud.rpy` |
| P3 (1) | `game/ui_journal.rpy`, `game/sb_threads.rpy`, `game/sb_memories.rpy`, `tools/smoke/wp8_journal.rpy`, `tools/smoke/wp5_memories.rpy`, `tools/smoke/p2_journal.rpy` |
| P4a (1) | `game/sb_grades.rpy`, `game/sb_items.rpy`, `game/sb_board.rpy`, `game/sb_combat.rpy`, `tools/smoke/wp2_grades.rpy`, `wp4_board.rpy`, `wp6_items.rpy`, `p2_gear.rpy` |
| P4b (1) | `game/sb_night.rpy`, `game/sb_market.rpy`, `tools/smoke/p2_night.rpy`, and, only if the night rule needs it, `tools/smoke/phase1_all.rpy` and `tools/smoke/core_flow.rpy` (the 30-day driver must still finish; no other wave-1 package edits them) |
| P5 (2) | `game/view_stage.rpy`, `game/lighting.rpy`, `game/images/fg/`, `game/images/place/`, `game/images/char/fx/`, `game/layout/view_*.json`, `tools/make_fg.py`, `tools/make_pose_workflow.py`, `tools/install_pose.py`, `tools/install_face.py`, `tools/make_edit_workflow.py` (two prompts added), `tools/fg/`, `tools/smoke/p2_view.rpy`, `tools/smoke/assets/p2_view/`, and in this wave `tools/smoke/wp7_ui.rpy` and `tools/smoke/p2_hud.rpy` (the name plates they pin change here) |
| P6 (2) | `game/room_spots.rpy`, `game/room_computer.rpy`, `game/room_fishing.rpy`, `game/room_library.rpy`, `game/layout/hot_*.json`, `tools/smoke/p2_rooms.rpy`, `tools/smoke/assets/p2_rooms/` |
| P7 (2) | `game/room_cards.rpy`, `tools/smoke/p2_cards.rpy` |
| P8 (3) | everything, including the frozen files; `tools/smoke/phase2_all.rpy`, `tools/smoke/p2_saves.rpy`, `tools/smoke/wp11_dev.rpy`, `tools/smoke/phase1_all.rpy`, `tools/smoke/core_flow.rpy`, `docs/PLAYTEST.md`, `docs/ART_PHASE2.md`, `docs/PHASE2_DESIGN.md`, `docs/load_report_phase2.txt`, `tools/README.md` |
| Frozen after wave 0 (change only through P8) | `game/sb_loop.rpy`, `game/sb_tokyo.rpy`, `game/sb_missions.rpy`, `game/sb_events.rpy`, `game/sb_hooks.rpy` (not edited by P0 either), `game/explore.rpy`, `game/ui_icons.rpy`, `game/sb_hotspots.rpy`, `game/sb_rules.rpy`, `game/gui.rpy`, `game/screens.rpy` (P0b's two edits are the only ones), `game/jjk_defs.rpy`, `game/sb_relations.rpy`, `game/sb_energy.rpy`, `game/options.rpy`, and everything in the P0a and P0c rows, `tools/smoke/p2_contracts.rpy` and its assets folder included (`tools/smoke/wp0_stubs.rpy` and `tools/smoke/load_slot.rpy` too) |
| Untouched in phase 2 | `game/jjk_sprites.rpy` (not regenerated), `game/jjk_screens.rpy`, `game/script.rpy`, `game/missions_stubs.rpy`, every story and event file (`ch*`, `events_*`, `story_*`, `missions_arc1.rpy`), every existing picture, font and sound, `tools/smoke/wp3_missions.rpy`, `wp9_prologue.rpy`, `wp10_chapters.rpy` (unless P0b's hangout gate or soft clock breaks one, in which case P0b fixes it in its own commit), and every other existing tool (`install_bg.py`, `make_bg_workflow.py`, `keysprite.py`, `raster.py`, `pngread.py`, `gen_sprite_defs.py`, the sprite tools, `comfy_nodes/`, `chars/`, `bgs/` apart from the new prompts) |

**Overlap check (after the review).** The three layout sidecars are three file patterns with three owners (`area_*`, `view_*`, `hot_*`). `sb_world.rpy`, `bg_placeholders.rpy`, `ui_map.rpy`, `sb_items.rpy`, `sb_grades.rpy`, `sb_board.rpy`, `ui_hud.rpy`, `ui_journal.rpy`, `sb_screens.rpy`, `sb_activities.rpy` and `view_stage.rpy` each appear in P0b's row and one later row: different waves. `wp7_ui.rpy` and `p2_hud.rpy` are P2's in wave 1 and P5's in wave 2. `phase1_all.rpy` and `core_flow.rpy` are P4b's in wave 1 (only if needed) and P8's in wave 3. `p2_contracts.rpy` is written by P0a and extended by P0b, in sequence, and by nobody after that (the "arrives with" symbols are asserted in `p2_map.rpy` and `p2_rooms.rpy`). `screens.rpy` is P0b's only. No file has two owners in one wave.

A phase-1 harness that fails in a wave because of a change is fixed by the owner of the file that changed the behaviour, if the harness is in that owner's row for that wave; otherwise it goes to P8 in the hand-over note.

### P0a · Tooling, checks and the baseline (wave 0, first; in the owner's folder on `phase2`; no game file changes)

**Tasks:**
0. Backup (2.4). Then, before anything changes: write `tools/smoke/baseline_p0.json` from a scratch run (`place_actions(loc)` for every room × period, `armory_tools()` for a Grade 4 fixture, the return tuples of `sb_char` for every person, `person_choices` for every person × room × period) and the two pre-P0 screenshots (place view, person view) into `tools/smoke/baseline_shots/`. Later packages compare against these files, not against memory.
1. `tools/check_content.py`: `--dup-globals`, `--prefixes`, `--harness-names`, `--art-names`, `--action-returns` (R2, R4; the last scans `Function(` in screens and in `def` bodies); write `tools/smoke/baseline_globals.txt`, `tools/prefixes.json`, `tools/none_ok.txt` (name, tab, example call). Today's tree must come out clean or the exceptions are in the baseline.
2. `tools/smoke.sh`: the asset overlay (D49). When `tools/smoke/assets/<harness name>/` exists, each of its files is copied to the same path under the scratch `game/`; every folder on that path is first made a real folder holding links to the original's children, so nothing is ever written through a link.
3. `tools/smoke/_lib.rpy`: `fixture()` fails on an unknown name and refuses the shaped variables (R5); `zz_rect(screen, wid)` → `(x, y, w, h)` of a button with that `id`, read from `renpy.display.focus.focus_list` after a render (buttons only); `zz_buttons(screen)` → the count of focusable widgets belonging to that screen; `zz_words(screen)` → the letter-bearing tokens of every `Text` displayable in `renpy.get_screen(screen)` (`visit_all`) **whose style is not `icon_glyph`**; it counts what is in the tree whether or not it is see-through, and hover labels (their own screen) are not counted; `zz_texts(screen)` → the list of every `Text`'s string in that screen (to assert a removed line is gone); `zz_calls(fn_name, seconds)` → wraps a store function, runs the interaction for that wall-clock span, and returns how many times it was called; `zz_layer_tags(layer)` → the set of tags showing on a layer; `zz_worst(screen, *args)` → queues four toasts, shows the objective banner, turns skipping on, renders, takes the screenshot.
4. `tools/smoke/p2_contracts.rpy`, the tooling half: every `none_ok.txt` example returns `None` inside a `settle()` fixture; every `DEV_FUNCS` key through `dev_action(key)`; the baseline file loads. `tools/smoke/aa_zz_order.rpy` is written here and switched on by P0b.

**Acceptance:** `check_content.py --all` on **today's tree** shows no finding; all twelve `wp*` harnesses, `core_flow` and `phase1_all` pass with the new `_lib.rpy` (a harness that relied on a lax `fixture()` is fixed in this commit); an overlay run leaves `git status` clean and nothing new under `game/images/`; `git diff --stat game/` is empty.

### P0b · The game scaffold: hooks, contracts, stubs (wave 0, second; in the owner's folder on `phase2`)

**Tasks:**
7. `gui.rpy`: the grade tokens, `gui.icon_words`. `sb_grades.rpy`: `GRADE_TIER`, `grade_tier`, `grade_color`, `grade_fill` (a flat fill until `grade_sheen.png` exists), `grade_is_special`, `screen grade_chip`.
8. `ui_icons.rpy` (4.3) in full, with `ICONS`, `ICON_FOR`, `ICON_GOLD` at init -3; the style `icon_glyph`; `config.always_shown_screens.append("hover_label")`; `hover_label` draws tuples only. `view_stage.rpy`: `default persistent.motion = True`, `VIEW_TICK`, `view_motion()`, `view_person_rects(loc)`. `screens.rpy`: the SKIPPING test and the Preferences "Motion" row, in one edit.
9. `sb_hotspots.rpy` (4.10, 4.12's interface) in full, at `init -5 python`; no hotspot or game registered. `default mg_result = {}`.
10. `sb_rules.rpy`: `rule_hangout_gate` (registered), `label rule_walk_to`, `rule_layout(name)` (the full stem: `area_school`, `view_dorm_common`, `hot_dorm_common`). `sb_world.rpy`: `advance_period_soft(n=1, loc=None)`; **the `library` place** (its `LOCATIONS` row, `LOC_ORDER`, the `school` row of `AREAS`: `AREA_BY_KEY["school"]["places"]`) and `bg library` in `bg_placeholders.rpy` (3.1, 4.14). `sb_hooks.rpy` is not edited (its `_validate_place_actions` already rejects a duplicate place-action id).
11. `view_stage.rpy`: today's stage loop and name plates (`sb_screens.rpy:405-453`) and `char_focus` moved in verbatim (D35), **preceded in `view_stage(loc)` by its own copies of lines 388-392 with `here` → `loc`** (4.5: the moved loop cannot see `sb_place`'s `_stage`, `_xs`, `_zoom`, `_yoff`); `view_focus(who)` computes `_x0` itself; plus the `view_*` stubs. New stub files `sb_night.rpy`, `sb_market.rpy`, `room_spots.rpy`, `room_computer.rpy`, `room_fishing.rpy`, `room_library.rpy`, `room_cards.rpy` with **every stub function and label of 6.1 and every `default` of 3.3**; the stub functions that live in existing files (`person_now`, `map_spots`, `toast_room`, `jr_story_rows`, `item_requirements`, `item_requirements_met`, `ITEM_REQS = {}`), and the final validator `item_validate_reqs` in `sb_items.rpy` (D27).
12. The hooks table (6.3), line by line, including the action card's `rail_actions` line and the map's tooltip line. `sb_map` gains `area=None` (unused yet). `person_choices` dicts gain `icon`. `explore.rpy`: the six review buttons, with `when` (`market_exists`, `night_exists`).
13. `p2_contracts.rpy`, the contracts half: `ZZ_RETURNS` for every function row of 6.1 (signature, owning file, return type or shape); `grade_color("s1") == grade_color("g1")`; `grade_tier(0) == "sp"`; the icon coverage check of 4.3; the registries' duplicate checks; `aa_zz_order.rpy` switched on; `rail_actions` with a companion ends in the `release` row; `rule_layout("view_dorm_common")` and `rule_layout("hot_dorm_common")` are read independently (two overlay files in `tools/smoke/assets/p2_contracts/game/layout/`, each in 6.1's schema and each changing only its own data); `here = "library"` renders `sb_place`; **the harness dumps the code defaults, through the contract functions only, to `shots/layout/defaults.json`** (`view_slots(loc, n)` for every room and n from 1 to 4, `map_spots(key)` for every area, the point of every registered hotspot; at P0b the last two are empty, and P1 and P6 refresh the file by running the harness in their worktrees); `rule_walk_to("library")` sets `here`, and for a locked room it says why and leaves `here` alone; `item_validate_reqs()` returns `[]` on the empty table and one finding for a test row whose Control threshold is above its grade's cap. `tools/smoke/wp0_stubs.rpy:157` learns `["layer", "area"]`. Run everything: lint, `p2_contracts`, `core_flow`, `phase1_all`, all twelve `wp*`, `tools/load_all_saves.sh`. Prove the hover label: a harness screenshot of `icon_sample` with one button hovered, held across 20 toast-timer ticks, with four toasts up.

**Acceptance:** standard; **all twelve `wp*` harnesses pass, or each one that fails is fixed in this commit** (the clock, the hangout gate, the stage move and the new room all land here); `load_all_saves.sh` reports all 11 saves SAME as `docs/load_report_phase1.txt`; `git diff` on `sb_loop.rpy`, `sb_tokyo.rpy` and `sb_missions.rpy` shows only added lines plus the three edited ones, and `sb_hooks.rpy` is unchanged; `advance_period_soft(2)` from Morning with `st_roster` waiting at Noon stops at Noon and returns False, with nothing waiting reaches Afternoon, from Evening stops at Night, `advance_period_soft(1)` at Night returns True, and `advance_period_soft(2, loc="gate")` stops for a beat waiting at the gate while I stand elsewhere and makes no `renpy.random` call; `rule_hangout_gate` is False for all eight on a fresh settled fixture, True once `roll_call` is set, and True for a fixture that lacks the flag but has `"st_roll_call"` in `done_events`; `place_actions` for every room × period equals `baseline_p0.json` apart from the Library's own rows; the phase-1 action card shows the same rows as before for every baseline room × period (it now reads `rail_actions`); the place view and person view screenshots are pixel-identical to `baseline_shots/` (the moved stage changed nothing); hovering a row on the old map shows **one** label, not two; with `persistent.motion` False the sheen and pulse functions return `None`; a save made on the place view reloads (nothing un-picklable was added, R10).

**Owner check (checkpoint A, about 10 minutes; played once P0c is in, so the style sample has the real sheen):** the game plays and looks as before; that is expected. The SKIPPING tag is gone from the map and the journal. An old save loads. Character scenes don't appear until after roll call. The old map lists one new room, the Library, with nothing in it yet. Open Review tools → Style sample: say which icon mode and whether the chips look right. Answer the four other rulings (the night, the character scenes, two-hour activities, the Gojo night and the ceiling).

### P0c · Art and layout tooling (wave 0, third; a small sitting in the owner's folder on `phase2`, after P0b and **before checkpoint A**; no `.rpy` file changes)

**Tasks (the old tasks 5 and 6):** `tools/layout_sheet.py <name>`: draws a sidecar's points, boxes and polygons (6.1's schemas; or the code defaults that P0b's `p2_contracts` dumps to `shots/layout/defaults.json`, task 13) on the background and writes `shots/layout/<name>.png`; pure `raster.py` / `pngread.py`. `tools/gen_gui.py`: `gui/grade_sheen.png`, `gui/hot_ring.png`, `gui/soft_box.png`, `gui/card_back.png`. `tools/make_icon_workflow.py`, `tools/cut_icons.py`, and the three names files `tools/icons/sheet_<n>.txt` (generated from `ICONS`, so the sheets and the table cannot disagree). `tools/bgs/prompts/area_<key>.txt` ×6 (each asks for the buildings at 4.1's pin positions), `library.txt`, `map_tokyo.txt`, `utahime_office.txt` and `gojo_office.txt`: ten prompt files, one for every background of section 5 rows 2 to 5 (`make_bg_workflow.py` refuses a name with no prompt). The hand-over note records what the first icon sheet cost (one run or two candidates, section 5).

**Acceptance:** `layout_sheet.py view_dorm_common` writes a sheet from the dumped stage slots in `defaults.json`, and a second from P0b's test sidecar (`tools/smoke/assets/p2_contracts/game/layout/view_dorm_common.json`), which differs; a test `tools/fg/` polygon is drawn (area sheets wait for P1, whose task re-runs the dump once `map_spots` has data); `make_bg_workflow.py` accepts all ten new names; the four `gui/` files exist at their sizes and the Special chip shows the strip; the three names files together hold exactly the 88 names of `ICONS`, each once; the icon workflow `.json` opens in ComfyUI (the owner's first step of art batch 1); no `.rpy` file changed.

### P1 · The two-level map, the Library's pins and schedule, Tokyo's second level (wave 1)

**Tasks:** 4.1 in full (screens `map_area`, `map_district`; the old tooltip frame removed); `AREAS` data, `map_spots` with the sidecar override; six `bg area_<key>` placeholders (clamped crops); the Library's pin and the School Building's new name (the room itself is P0b's); `MAP_DISTRICT_SPOTS`; `person_now(who)`; the Megumi weekend row with the harness's frozen copy; update `wp1_world.rpy` to open an area (`sb_map(area=…)`) before pressing `row_<loc>`, and to press `district_<key>` then `district_go` where it pressed a district card (lines 619-622, 654-661; the locked-Shinjuku check stays a `NullAction` on `district_shinjuku`); run `p2_contracts` to refresh `defaults.json`, then `tools/layout_sheet.py` for the six areas.

**Acceptance (`p2_map.rpy`):**
- level 1 has exactly six `area_<key>` buttons and no `row_*` button; `zz_texts("sb_map")` holds none of "Find someone", "Walking is free" or the old header's subline; `zz_words("sb_map") <= 20`; no marker shows more than three face chips, with five people in an area the fourth chip is "+2";
- `sb_map(area="school")` shows `row_classroom`, `row_cafeteria`, `row_infirmary`, `row_library`; pressing an open one returns `("go", loc)`, for every one of the 19 rooms; a locked one returns nothing and has a tooltip; `zz_words <= 16`;
- every tooltip on the screen is a 2-tuple with a key unique on the screen; no plain-string tooltip is left;
- half a second after pressing a marker the area picture's alpha is 1.0 (the zoom-in started at the press, not at the screen's start); with `persistent.motion` False it is 1.0 at once; the placeholder crop for every area lies inside 0 to 1920, 0 to 1080;
- every room is in exactly one area's spots, inside x 200 to 1700, y 200 to 940; a test sidecar (`tools/smoke/assets/p2_map/game/layout/area_school.json`) moves a pin;
- a person in a locked room is on no marker and no pin;
- screens `map_area(key)` and `map_district(key)` exist with exactly those parameters (the two "arrives with" rows of 6.1, asserted here because `p2_contracts.rpy` is frozen);
- with `night_marks` patched to `{"mountain": "moon"}` the Mountain marker shows the `moon` icon and no other marker does;
- `sb_map(layer="tokyo")` shows five `district_<key>`; pressing an open one returns nothing and opens its view (`zone` is set); an open district's view has `district_go`, which returns `("district", key)` exactly when `trip_ok_now()`; **with the stub (`(False, "")`) no `district_night` button exists anywhere;** with `night_out_ok` patched to `(True, "")` it exists only in Shibuya and Shinjuku at Evening or Night and returns `("night", key)`; patched to `(False, "Not two nights running")` it exists, returns nothing and shows the reason;
- the screen's parameters are `["layer", "area"]`; both protected call statements compile unchanged; `load_all_saves.sh`: auto-1 and auto-2 SAME;
- `_validate_world` passes; `person_now` returns its six keys for all 17 journal people, `hidden=True` for someone in a locked room, `with_me=True` for the companion;
- `zz_worst("sb_map")`: no toast drawn; the hover label is on top.

**Owner check:** open the map: six areas under "Jujutsu High". Click School Building, walk to the Library. Switch to Tokyo and back.
**Cut if short** (none of these is an owner decision): the Megumi row; Tokyo's second level (D4; districts then start the trip directly, and the night in Tokyo moves to a button on the Tokyo layer).

### P2 · HUD, the icon column, the lighter person view, toast lanes (wave 1)

**Tasks:** 4.2 (the date and status chips in one row; the banner's new x over the place view); 4.4 (the column, the "Nobody here" line, `release` from `rail_actions`); 4.6; `toast_room()` and the stopped clocks; the objective banner's rule; `AMBIENT_STORY` with twelve rows, read by `ambient_of`; the `AMBIENT` row and the `study` activity's `loc`; update `wp7_ui.rpy`. (`icon` on `person_choices` is already there from P0b. Quick-menu icons are not in phase 2: section 11.)

**Acceptance (`p2_hud.rpy`):**
- the three HUD buttons sit at x 1668 / 1742 / 1816, y 26 (`zz_rect`), return `("map",)`, `("journal","people")` and open the menu; with all three status chips showing and the longest date ("Day 100 · Wednesday"), no chip's rectangle meets the date chip's;
- every button on `sb_place`, `sb_char` and the HUD has a tooltip whose key is unique on its screen;
- for every room × period, the column offers exactly the `("act", id)` returns of `rail_actions(here)` and the `("mission", mid)` returns of `missions_here(here)` (as sets), with and without a companion (the `release` row is last); **every row of `baseline_p0.json`'s `place_actions` is still present in `place_actions(loc)`, in the same order; any extra row is a registered place action** (so this bullet still passes after P4b, P6 and P7 register theirs);
- with icon words off, the column holds no `Text` other than icon glyphs (`zz_words` is 0); with nine actions and four toasts up, no column button's rectangle meets the toast lane and none rises above y 360;
- `sb_char` for every person returns the tuples recorded in `baseline_p0.json` for each choice; the screen holds no `Text` equal to the person's name, no pip image, no "Closer", no bar; `zz_words("sb_char") <= 16`;
- `person_choices` still returns at most four, ending with `talk`, for every person × room × period, each with an `icon` in `ICONS`, and a mission choice's icon is `mission`;
- `toast_room()` is `(0, 0, 0)` with `journal`, `sb_map`, `board_screen`, `board_partner`, `armory`, `icon_sample` and the game menu up, and with `grade_card` shown by `call screen` over a scene (it has no tag; the test is by name); `(1880, 92, 4)` over `dev_panel`, and a review button's toast is drawn while the panel is up; `(1790, 92, 4)` over `sb_place`, `(1722, 26, 2)` over `sb_char`, `(1880, 92, 4)` over `combat_screen`; a toast queued under limit 0 is still queued and unexpired 10 s later;
- the toast lane (x 1330 to 1790, y 92 to 350) and the banner's rectangle over `sb_place` (x 400 to 1300) do not intersect; in the `zz_worst("sb_place")` screenshot the objective line is readable to its end;
- `ambient_of` returns a 2-tuple for every person × room; with `sunmall_done` set at least one caption differs from the fresh-game one.

**Owner check:** the corner icons; hover over everything; click Nobara: grade and choices only.

### P3 · The journal: five tabs, the person page, the Me page (wave 1)

**Tasks:** 4.7; `jr_story_rows`; reword the 11 "you" stage lines and `MEMORY_UNMET_HINT`; grade chips; the checklist chips on talismans; the Leads section; the `("go", loc)` return; update `wp8_journal.rpy` (the lines that expect a Memories tab) and `wp5_memories.rpy` (the hint text).

**Acceptance (`p2_journal.rpy`; memories built with `_mem()` / `memory_entry()`):**
- `JOURNAL_TABS` has five rows; `journal("memories")` opens with `js["tab"] == "people"`; `jjk_status` and `jjk_journal` render;
- for every met person the page shows the three sections; the tiles on a page equal `memories_with(who)`; `ch2_first_years` is on Yuji's, Megumi's and Nobara's pages; the three `who=()` memories are on the Me page and on no person's page; every memory in the catalogue is reachable from a page or from the Me page;
- a seen tile replays and the journal is still up afterwards; an unseen tile is not clickable and names nobody unmet;
- `jr_story_rows("nobara")` starts with "Somebody Remembered", has exactly one row with `next=True`, and that row has a non-empty `where`; at most one collapsed "later build" row;
- "Right now" equals `person_now(who)`'s text; the `go` button exists only when `journal_editable()` and `reachable`, and returns `("go", loc)`; every other journal button leaves the journal up; from the game menu the journal returns only `True`;
- no thread stage line contains "you" or "your" (a harness regex);
- **with all 17 of `JOURNAL_CAST` marked met through their own flags, all 18 cards fit without scrolling (`zz_rect`: four rows, 844 px in a 928 px body); with 26 test cards (the harness patches the list `jr_people` reads) the last card can be scrolled to and pressed, and none is clipped when it is in view;** `zz_words` on one card ≤ 6; Gojo's chip reads "OFF THE SCALE" on the Special fill; `jr_grade_line("gojo")` is still "Off the scale";
- **Records renders with the three stubs (`[]`, `[]`, `dict(today=0)`) and shows no section;** with `pc_records` patched to two titles it lists two; the journal reads none of `PC_PAGES`, `pc_read`, `FISH_KINDS`, `fish_log`, `cards_won` (a source check);
- **the talisman picker and the Equipment and Inventory item panels show `item_requirements(id)`:** with the function patched to `[("Grade 2", True), ("Control 50 · I have 31", False)]` both chips render, the second in seal red; with the stub (`[]`) nothing is added;
- Leads: with `pc_leads` patched to one row the Missions tab shows it first; with the stub the section is absent;
- Stats shows one pane at a time: for each value of `js["ssub"]` (Overview, Last Light, My year) only that pane's texts are in `zz_texts("journal")`, and the three chips are always there;
- `zz_worst("journal")`: no toast drawn.

**Owner check:** five tabs; open Nobara: where she is, her story with the next step, her memories; open Me: the story so far.
**Cut if short** (none of these is an owner decision): the Records chip on the Me page; the `go` button. **The Leads section is not on this list:** it is the journal's half of the owner's answer 3 ("as a part of missions", 12.2), so it is cut only with the owner's say (7.3).

### P4a · Grades on cards, gear requirements (wave 1)

**Tasks, in this order:** 4.8's four sites in its files; 4.9 with `ITEM_REQS` (the three tools and the two Grade 1 talismans), `item_requirements`, `item_requirements_met`, the `can_hold` / `can_wear` changes; update `wp2`, `wp4`, `wp6`. (The cap validator, `item_validate_reqs`, is already there from P0b and covers rows any file adds; P4a's rows must pass it.)

**Acceptance (`p2_gear.rpy`; items through `give_item`, grades through `promote`):**
- `armory_tools()` gives the five `(state, reason)` pairs recorded in `baseline_p0.json` for a Grade 4 fixture;
- `item_requirements("inverted_spear")` has four lines, all unmet on a fresh game; Playful Cloud's Output line flips when `output` crosses 50 (set through `gain`); every Control or Output `("stat", s, n)` has `n <= GRADES[<the item's grade>]["stat"]`;
- **a talisman has a checklist:** `item_requirements("afterglow")` has two lines (Grade 1, Control 80); `can_wear("afterglow")` refuses with the first unmet line after its existing checks; a talisman already worn stays worn after `ensure_state()` whatever its checklist says (D28);
- a tool equipped before an unmet requirement is still `equipped_tool` after `ensure_state()`; `can_hold` refuses a tool that is owned but not in hand, with the unmet line as its reason;
- every `ITEMS` record still has exactly 12 fields; `_validate_items` passes; `bound_specials` is never written;
- screenshots: the board (g4 green, g3 blue), the armory with checklists, the grade card for `sp`, the combat header; `zz_worst("armory")`.

**Owner check:** the armory's checklists; the board's coloured chips; a talisman's checklist in the journal.

### P4b · The night rule, the Gojo night, the night in Tokyo, the Black Market (wave 1)

**Tasks, in this order:** the night rule (4.15, D20 to D22) with `NIGHT_REST_BLOCKS` and its new-day hooks; the Gojo night with `night_day_best` and its mirror test (D23); the night in Tokyo (D24); the market (4.16) with its four talismans, their `ITEM_REQS` rows and the price validator (D29).

**Acceptance (`p2_night.rpy`; costs through `night_set_cost`, purchases through `market_buy`):**
- at Night, `night_filter_actions(loc, place_actions(loc))` has no `wait` anywhere, has `night_bed` everywhere but `dorm`, still has `sleep` in `dorm`, and has no costed id outside `NIGHT_OK` (so no `cards_play`); `rail_actions(loc)` is that list minus the ids in `hot_covers(loc)` (so the test still passes once P6's bed hotspot takes `sleep` out of the dorm's column), plus the `release` row when someone is along; at every other period on an ordinary day `night_filter_actions` returns `acts` unchanged; `place_actions` is unchanged at every period; with `NIGHT_STRICT = False` the costed rows return; **the same holds on the phase-1 action card** (rendered without P2: no Wait button at Night);
- `night_allows("mission:" + mid, cost)` is True at Night exactly for missions whose periods include Night or that cost nothing; `night_allows("hang", 1)` is False at Night and True at Evening; **at Night `person_choices(who)`, for every person, holds no mission for which `night_allows` is False (a fixture offers `cm_ijichi_1`, cost 2, at the gate: it is not there) and no costed activity outside `NIGHT_OK`; `activity_state` refuses `rom_say` at Night for a fixture that is `confession_ready`;**
- explore mode and an unsettled game: no filter, no pending;
- `advance_period()` from Night on the ridge sets `night_pending()`; one turn of the loop leaves `here == "dorm"`, `night_pending()` False and exactly one carry line said; the same from `dorm` never sets it; seven `new_day()` calls in a row leave one pending walk; a two-period action started in the Evening ends at Night with nothing pending;
- the net after scenes that roll the day themselves: a Nade mission started in the Evening, `int_night`, and a story beat that ends in `advance_period()` at Night each end with `here == "dorm"` and one carry line. (Board jobs are not a case: the board refuses in the Evening and at Night.)
- `night_gojo_due()` is False without `intensive_done`, on a day Gojo is out, within 10 days of the last, when the room under the ceiling plus `past_cap` is not more than `night_day_best()`, and without room for the reserve gain; True otherwise; at Special Grade (`grade_cap` is `None`) it does not raise; on an invitation day `night_marks()` is `{"mountain": "moon"}` and the morning toast is queued once; **the two cases section 0 tells the owner about hold:** with `past_cap = 0`, Control 55 just promoted to Grade 2 is not offered a night and Control 70 just promoted to Semi-Grade 1 is; with `past_cap = 6` both are, and the first ends above 70 and at most at 76; `wp1_world.rpy`'s schedule regression passes unchanged;
- **the owner's sentence:** from `settle()` fixtures at Control 30, 58, 60 and 80, each promoted (through `promote`) until `night_gojo_due()` can be True, and with `NIGHT_STRICT` both True and False: the harness measures five runs of `sb_do_train` at every place that offers `train` (`training`, `dojo`, `ridge`, `forest`, `courtyard`, `riverside`) plus one `sb_do_hold`, **the lesson day (on a day Gojo is in: `act_lesson` through its label, then four `sb_do_train` on the ridge, plus `sb_do_hold`)**, each of them hold-first and hold-last (stamina refilled between runs), and five "Train together" with each partner, takes the largest Control gain and the largest `ce_max` gain, and asserts (1) `night_day_best()` is at least that Control gain (the mirror has not drifted), (2) the night's measured Control gain and `ce_max` gain are **each strictly greater** than the best day's from the same fixture, (3) the night's Control gain equals `night_gojo_gain()[0]` and its `ce_max` gain equals `night_gojo_gain()[1]` (12 today, against the lesson day's 9); (4) `night_step` equals what `gain` really adds for every Control from 0 to 99 and amounts 2, 4 and 5 (both cuts compound at 85);
- with exactly `night_day_best() + 1` of room under the cap the night is offered, gains that one point more than the clipped day, and sets its cost; with `night_day_best()` of room it is not offered;
- the day after: `night_can_work()` False, `night_tag()` non-empty, **no id in `NIGHT_REST_BLOCKS` is offered in any column, hotspot or person view** (`rail_actions` for every room, `hot_spots_for`, `activity_state` for every person: `train`, `lesson`, `hold`, `swim`), `board_take_reason` gives the night's reason, no mission button anywhere; `study`, `eat` and `talk` are still offered; `pick_event("story")` still returns a waiting beat; the set of `available` missions two days later equals the set before the night (nothing was missed); the day after that, all clear;
- `night_out("shibuya")` under autoplay with ¥2,000: yen down 1,500, `here == "dorm"`, day +1, stamina at half, cursed energy at 70%, `market_found` set, `night_can_work()` True; autoplay takes Home at the second (after-club) menu; refused the next night; `night_out_ok("shinjuku")[0]` is False below Grade 2 and its reason is non-empty; with `market_exists` patched to False the club night neither sets `market_found` nor says the stairs line, and no second menu appears; `night_exists()` is True. With ¥0 autoplay heads home: yen, day and `here` unchanged, no cost set. Choosing the market alone: no yen taken at the door, the day rolls, the cost is set;
- the market: `market_exists()` is True; `market_buy` returns False and changes nothing when `yen < price`; True moves the yen and the item; a once-only row then reads "Sold"; **`MARKET_STOCK` holds no item with `special=True`**, and `bound_specials` is unchanged by any purchase; every price obeys D29's rule for its tier (the validator runs without a KeyError for `s1`, `g4` and an ungraded supply); each of the four talismans has an `ITEM_REQS` row that passes the cap validator (`item_validate_reqs`, in the tree since P0b) and none is graded above Semi-Grade 1, the highest grade Arc One reaches (actually putting one on through P4a's checklist in `can_wear` needs P4a's code: that one line is deferred to P8, 7.3); every `ITEMS` record still has exactly 12 fields; `zz_worst("market_screen")`;
- `phase1_all.rpy` completes its 30 days with the rule on;
- the six `night_*` variables and `market_bought` pickle and are harmless at default in a replay (`memory_scope` run for one memory).

**Owner check:** stay up until Night on the mountain: the column offers bed. Review tools: a Gojo night; try to train, hold the hour or take a mission the next day. A night in Tokyo: the club, then the market.
**Cut if short, in this order:** the market's outfits shelf (not an owner decision as built: it is an empty shelf). Then, **only with the owner's say (7.3):** the market itself (`market_exists()` stays False: the night menu, the rumour page and the review button all hide it); the night in Tokyo (the stub hides its map button).

### P5 · The place view alive (wave 2)

**Tasks:** 4.5's P5 version in full (every transform function top-level and curried, the entrance an ATL transform: R10); `view_person_rects` from the slots and pose boxes; `VIEW_SLOTS` for eight rooms; `tools/make_fg.py` with polygon files in `tools/fg/<place>.json` (6.1's schema; not in the `view_` sidecar), and the six foreground files; `tools/make_pose_workflow.py`, `tools/install_pose.py`, `tools/install_face.py`; `VIEW_FACE` boxes for the eleven on campus; the schedule check of the pose list; `tools/layout_sheet.py` runs for every room with slots, a foreground or face boxes (the sheets go to the owner at checkpoint C); test pictures in `tools/smoke/assets/p2_view/`.

**Acceptance (`p2_view.rpy`):**
- after `sb_do_wait` (no `scene` statement), `scene_light == light_for_place(here, period)` when the place view opens;
- `view_slots(loc, n)` returns n 4-tuples for every room and n from 1 to 4; `stage_x` agrees;
- with no pose file `view_pose` is `None` and the stage draws the sprite; with the overlay's `pose_dorm_common__nobara__evening.png` and its sidecar box, at Evening the stage draws a patch at the box and pressing it returns `("char", "nobara")`; at Noon (no day file) it draws the sprite; a day file alone is not used at Evening;
- `install_pose.py` refuses a test picture with 40% changed and accepts one with 10%, writing the box to `view_<place>.json` and the preview; a test picture with faint noise over the whole frame (every pixel off by 6) and one real 10% patch is accepted with the box around the patch only; `--box 400,300,500,700` writes that box; an existing `hot_<place>.json` beside it is byte-identical afterwards;
- `view_person_rects(loc)` returns one rectangle per person on stage, and a pose's box when a pose is drawn; `view_pose`'s `image` is a `str` and its dict pickles; `view_stage("cafeteria")` used from a test screen that defines none of `_stage`, `_xs`, `_zoom`, `_yoff` renders (it computes its own);
- the foreground files load; `view_fg` draws above the stage and below the name tags; after `stage_person` the foreground is on the master layer (`"view_fg" in zz_layer_tags("master")`) and a `scene` statement clears it; rolling back through `stage_person` (`renpy.rollback(checkpoints=1, force=True)` from a harness label) leaves no foreground behind (if forcing a rollback from a harness proves unreliable, this one line moves to the owner check at C and `p2_saves` covers the save);
- **the save test (R10):** `renpy.save` on the first line of dialogue after `stage_person`, with the eased sprite and the foreground up, succeeds and `renpy.load` comes back on that statement; the same after a rollback through it; the same with a blink and talk overlay on the sprite. `pickle.dumps` of every displayable `view_enter` and `lit_sprite` return succeeds; under skipping no transition runs and nothing is left; inside a replay (`memory_scope`) `view_enter` shows the sprite at `pos_c` with no foreground; a scene that then shows a second character still clears on `scene`;
- with the overlay's `fx_yuji_blink.png` / `fx_yuji_talk.png`, `lit_sprite` returns a displayable with the two extra layers on a compatible expression and none on `happy`; without the files the structure is today's;
- motion: once any transition has ended, `zz_calls("view_breathe_fn", 3)` on the common room with four people and two hotspots is at most 4 × 22 × 3, and 0 with `persistent.motion` off (the two light transforms each sprite already has are not counted, R9); no function transform has `blur` set by its function;
- `stage_person`'s signature is unchanged; `char_focus(x0)` with one argument still works; `zz_words("sb_place")` ≤ 2 per person on stage (this line runs only when P2's icon column is merged; with the phase-1 card still up it is deferred to P8); `wp7_ui.rpy`'s name-plate lines (386-388) are updated here;
- screenshots: the common room with three people (depth, shadows, the table edge in front), the same with a pose patch, the person view mid-ease.

**Owner check (checkpoint C):** the common room: people stand in the room, not on it. Click Nobara: the view eases in; leave: it eases back. Look at the layout sheets. Then art batch 3: drop in the two poses and Yuji's blink and judge them.
**Cut if short, in this order** (the same order as 7.3): blink and talk; the depth blur; the eased entrance.

### P6 · Rooms: hotspots, the computer, the Library's actions, fishing (wave 2)

**Tasks, in this order:** the hotspot set (4.10) with its look lines and the vending machine, points checked with `tools/layout_sheet.py`; the computer (4.11) with its twelve pages; the Library actions (4.14); fishing (4.13).

**Acceptance (`p2_rooms.rpy`; offers through `board_generate()`, catches through `fish_land()`, requests through `pc_request()`):**
- the hotspot validator passes; every *visible* hotspot's action is absent from that room's column (`rail_actions`) and present as a return of `hot_layer`; a look hotspot returns `("hot", id)` and its line changes with the day; at Night a costed hotspot is dim and returns nothing;
- **reachability:** for every room, every period and a stage of one to four people (placed through the schedule or `pin`), each id in `night_filter_actions(loc, place_actions(loc))` is offered by the column or by a visible hotspot whose rectangle (`zz_rect`) meets no rectangle of `view_person_rects(loc)`; never neither, never both; an id that `night_filter_actions` drops (at Night: `wait` and the costed ids outside `NIGHT_OK`; on a rest day: the ids in `NIGHT_REST_BLOCKS`) is offered by neither the column nor an enabled hotspot (against P4b's stub nothing is dropped and the bullet reads as before);
- **a hotspot follows its action:** after `sb_do_rest` the cot is gone; with the board closed its hotspot is gone; after one look the veil hotspot is gone; in explore mode `hot_spots_for` returns no action or standalone hotspot; the storehouse shows `tools` before `armory_open` and `armory` after, never both; on a rest day no hotspot offers an id in `NIGHT_REST_BLOCKS`; **the standalone is never hidden by a person:** with `view_person_rects("courtyard")` patched to a box covering (1500, 640) (pose 11's case), `spot_vend` is still in `hot_spots_for("courtyard")`, with `front` True;
- the vending machine: `sb_do_spot_vend` takes ¥150 and gives stamina +10; `spot_vend_ok()` is then False for the rest of the day and True the next; with ¥100 it is refused and nothing changes; a look hotspot's use adds `hot:<id>` to `actions_today`;
- a test sidecar (`tools/smoke/assets/p2_rooms/game/layout/hot_dorm.json`) moves a hotspot, and `view_dorm.json` beside it is not read for it;
- registration happens at init 0 or later (the file would not load otherwise; `aa_zz_order.rpy` guards the other direction);
- `sb_do_pc_open` under autoplay returns; reading a page adds it to `pc_read`, sets `researched_<page>`, gives its Insight once only; `pc_has_read` agrees; all twelve pages render; `sukuna` is hidden until `saw_the_ridge_veil`; `legends_market` sets `market_found` and is listed only while `market_exists()` (patched both ways; with it False no page links to it and eleven pages are counted); `pc_request("clan_zenin", "…")` shows on Home and in `pc_leads()`; `pc_records()` returns the titles read; no page text contains "you " addressed to the reader, "Kaito" or "Amagiri";
- cross-check: with offers regenerated through the board's own generator until one is misgraded, the checked view marks exactly the offers whose `true_grade != grade`; a second check the same week costs nothing; at Night it is refused;
- fishing: 1,000 simulated casts through the game's functions give lengths inside each species' range; the River Lord never appears outside Evening or below `q` 0.9; the pale thing at most once a week; `fish_log` only ever rises; the mean yen of a three-cast sitting is below `BOARD_YEN["g4"][0] // BOARD_PERIODS`; the day's first catch gives Control +1 once (`fish_first`), a second gives none, and on a rest day (`night_can_work` patched to False) the first gives none; a companion gains Bond +2 once a day (`fish_bond`); `fish_Hook()()` returns `("hook", q)` with `q` following the clock (two calls 0.2 s apart differ) and is the only non-`Function` action class the package adds; after a settled cast `renpy.can_rollback()` is False; `fish_records()` has one row per species;
- `lib_study` on the theory shelf gives Insight +4 and costs one period; the barrier-craft shelf gives Control +2 and Insight +2, and on a rest day (`night_can_work` patched to False) Insight +2 only; `sb_do_study` in the classroom is unchanged;
- every new screen has an autoplay timer and answers `key "game_menu"`; every new variable pickles; `zz_worst` of `pc_screen` and `fish_screen`: no toast drawn.

**Owner check (checkpoint C):** the computer in your room: read three pages, cross-check the board; three casts at the river; study in the Library; the vending machine.
**Cut if short, in this order** (none of these is an owner decision): the look hotspots; fishing's record panel (the Me page still lists records); the genealogy site's three clan sub-pages (the overview stays, and it names all three clans the owner listed). The Library's actions and fishing itself are owner decisions: postponing either is the owner's call (7.3).

### P7 · Cards: blackjack, then poker (wave 2)

**Tasks:** 4.12: the table picker, blackjack, `register_minigame("blackjack", …)`; then poker and its styles; the daily cap.

**Acceptance (`p2_cards.rpy`; state through `cards_new()`):**
- `cards_ok()` is False in an empty common room and with less than ¥100;
- blackjack: 2,000 simulated hands through the game's own functions settle with yen changing only by ±stake, +1.5 stake or 0; the hand-total function is right for every ace case; I can't stake more than I hold; a sitting stops at five hands and at ¥3,000 down; `cards_state == {}` after leaving and `mg_result` has its three keys;
- the day's winnings never pass `BOARD_YEN["g4"][1]`;
- poker (if built): the ranker orders a fixed set of 20 hands correctly; a full hand under autoplay ends with the pot paid to exactly one player or split; each of the eleven has a `CARDS_STYLE` row; the read is offered only at Insight ≥ 20 and once a hand;
- Bond +1 with each opponent once a day; one period is charged only if a hand was played; `cards_records()["today"]` equals the day's winnings;
- after every deal, draw and settlement `renpy.can_rollback()` is False;
- at Night the table is closed: `night_allows("cards_play", 1)` is False and the hotspot is dim (this line runs only when P4b's `sb_night.rpy` is merged; against the stub it is deferred to P8);
- `zz_worst` of the three screens: no toast drawn; `--prefixes` passes with the `mg_blackjack` / `mg_poker` labels on the exception list.

**Owner check (checkpoint C):** a few hands of blackjack with whoever is in the common room; a hand of poker; watch their faces.
**Cut if short:** nothing without asking. Poker is the owner's decision ("blackjack and poker first"); if the sitting runs out, blackjack alone still registers and plays, and the orchestrator asks the owner whether to spend another sitting on poker or let it wait (7.3).

### P8 · Integration (wave 3)

**Tasks:** merge; any cross-package fix from the hand-over notes; `tools/smoke/phase2_all.rpy` (phase 1's end-to-end driver, extended: the map's two levels by pressing buttons, one night at each of bed / carried home / Gojo / out, one market purchase, one page read, one cross-check, one cast, one blackjack hand); `tools/smoke/p2_saves.rpy` (D44: in one scratch run it makes and reloads five saves: at `call screen sb_place` at Night on the ridge, on a rest day, inside `call screen cards_blackjack`, **on the first line of dialogue after `stage_person` with the eased sprite and the foreground up, and at the same place after a rollback through it** (R10); a `builtins` stage counter survives the load; each must come back on its statement with no `load_recover`); add the owner's checkpoint saves to `tools/load_all_saves.sh`'s list; `wp11_dev.rpy` only for what integration changes (the six new buttons and the 3×7 panel are P0b's, whose acceptance already needs every `wp*` to pass); the deferred acceptance lines (wave 1: P4b's market talisman put on through P4a's `can_wear`; wave 2: P5's word budget, P7's Night line); `p2_saves` also saves and reloads at the after-club menu of `night_out`; `docs/PLAYTEST.md` (every stand-in named, the five rulings as built, the "chosen for you" list of section 0 with what the owner said), `docs/ART_PHASE2.md` (section 5 as numbered steps), `docs/PHASE2_DESIGN.md` as built, `docs/load_report_phase2.txt`, `tools/README.md`.

**Acceptance:** standard (a) to (d) on the merged tree; **every one of the twelve `wp*` harnesses and every one of the eight `p2_*` package harnesses passes on the merged tree** (not only the three standing ones); `phase2_all` passes for 30 days; `load_all_saves.sh`: the 11 phase-1 saves SAME and each checkpoint save loads; `p2_saves` passes; every check of R2 clean; `p2_contracts` passes, byte-identical to P0b's.

**Owner check (checkpoint D):** a full playthrough with `docs/PLAYTEST.md`.

### 7.3 Order and cut lines

- **Order:** P0a, then P0b, then P0c, then checkpoint A (P0c is small and changes no `.rpy`; it comes before A so that the style sample the owner rules on has the Special Grade sheen). Then P1, P2, P3, P4a, P4b in parallel (they share no file). **Wave 2 branches from `phase2` after wave 1 has merged.**
- **What each wave-2 package really needs:**

| package | needs | lines that wait for another package |
|---|---|---|
| P5 | P0 | the 2-words-a-person budget needs P2's icon column (deferred to P8 if P2 slipped) |
| P6 | P0 (the `library` place is P0b's, so P1 is not needed) | the rumour page shows only with P4b's market; Records and Leads show only with P3 |
| P7 | P0 | "closed at Night" needs P4b's real `sb_night.rpy` (deferred to P8 if P4b slipped) |
| P4b (wave 1) | P0 | putting a market talisman on through P4a's checklist needs P4a's `can_wear` (always deferred to P8: the two are parallel). The cap validator is P0b's, so it runs in P4b's own worktree |
| P6 | P0 | the reachability bullet's Night and rest-day half, and the two "no Control on a rest day" lines, test against P4b's real rule (with P4b slipped they run with `night_can_work` patched, as written, and the Night half is deferred to P8) |

  A wave-2 package may start before wave 1 is reviewed only with those lines deferred, and only if credits make waiting worse; they look best after P2.
- **A missing wave-1 package never strands another's work,** because P0b pointed the phase-1 action card at `rail_actions`: without P2, the night rule and the hotspots still reach the screen through the old card; without P4b, `night_out_ok` hides the map's night button and `market_exists()` hides the rumour page and the review button; without P1, `hover_label` ignores the old map's string tooltips and the old map still works.
- **Whole packages that can be postponed** (their stubs stay; nothing built breaks): P7 (no card table: `cards_ok()` is False, so `place_actions` never offers it and its hotspot never shows), then P6 (no hotspots: every action stays in the icon column; the Library is a room with nothing of its own to do yet, apart from "Study together"), then P5 (people stand as they do today; no foreground, no poses, no blink). **P6 and P7 hold owner decisions (the computer, fishing, the Library's actions, blackjack and poker), so postponing either is put to the owner, not decided by the orchestrator.**
- **The structure the owner asked for first** (SCOPE section 3, part 1) is P0 to P4.
- **Cuts inside packages, in the order they are taken.** First, things the owner never asked for by name, which an agent may cut and report: the look hotspots; the Megumi schedule row; Tokyo's second level; blink and talk; the depth blur; the eased entrance; the journal's `go` button; the Records chip; the outfits shelf; fishing's record panel; the three clan sub-pages. **Then, only after the orchestrator has asked the owner (as in D51): the journal's Leads section (it is how answer 3's "as a part of missions" shows in the journal); poker; the Black Market; the night in Tokyo; the Library's actions.** Section 0 tells the owner the first two may have to wait.

---

## 8. Testing

- **`tools/smoke.sh`** as PHASE1 8.1, plus the asset overlay (P0a task 2).
- **Standing checks in every worktree:** lint; `check_content.py --all`; `p2_contracts.rpy` (with `aa_zz_order.rpy`); `core_flow.rpy`; `phase1_all.rpy`; the `wp*` harnesses in the package's own row.
- **Everything, three times:** all twelve `wp*` harnesses run at P0a (new `_lib.rpy`), at P0b (the hooks) and at P8 (the merged tree, with all eight `p2_*`).
- **Baselines, not memory:** "unchanged" always means "equal to `tools/smoke/baseline_p0.json` or `baseline_shots/`", written by P0a before anything changed; where later packages legitimately add rows (`place_actions`), the test is "every baseline row still present, in order".
- **Per-package harnesses:** `p2_map`, `p2_hud`, `p2_journal`, `p2_gear`, `p2_night`, `p2_view`, `p2_rooms`, `p2_cards`; integration: `phase2_all`, `p2_saves`.
- **Save regression:** `tools/load_all_saves.sh` at P0, P1 (the map saves), P4b (Night away from the dorm) and P8; the baseline is `docs/load_report_phase1.txt`.
- **What the measuring helpers can and can't do.** `zz_rect` reads rectangles of buttons with an `id`, after one render; it can't see a plain frame, so toast and banner positions are checked through `toast_room()` and the lane constants, and by the `zz_worst` screenshot. `zz_words` counts letter-bearing tokens in one screen's tree, including see-through text and excluding icon glyphs; it can't tell what is hidden behind another screen. `zz_texts` lists the strings, for "this line is gone" checks that `zz_rect` cannot make. `zz_calls` counts calls to a top-level function over a wall-clock span; `zz_layer_tags` lists what a layer shows.
- **Balance assertions use the game's own tables and labels** (`GRADES`, `BOARD_YEN`, `BOARD_PERIODS`, `sb_do_train`, `sb_do_hold` and `act_lesson` themselves, at every training place), never literals (D27, D29, P4b's "owner's sentence").
- **Saves are tested by saving** (R10): on the place view at P0b, in dialogue with the eased sprite up at P5, and five states at P8.
- **Phase-1 harnesses this phase changes,** each updated by the owner of the changed behaviour in the same commit: `wp0_stubs` (P0: the map's parameters), `wp1_world` (P0b: the nineteenth room; P1: row presses, the two-press district cards, the Megumi row), `wp7_ui` (P0b: the stage move, if anything; P2: person view, toast counts, the "Nobody here" text; P5: the name plates), `wp8_journal` and `wp5_memories` (P3), `wp2_grades`, `wp4_board`, `wp6_items` (P4a), `wp11_dev` (P0b: the six new buttons and the panel's size, if it pins them; P8: only what integration changes).

---

## 9. Owner checkpoints

Each is played from the Ren'Py launcher in the owner's folder on branch `phase2`. Save in a new slot at the end of each; that save joins the regression.

| checkpoint | after | what to play | about | art to make next |
|---|---|---|---|---|
| A | P0a, P0b, P0c | The old game; it looks the same, and that is expected. SKIPPING no longer covers the map or journal. An old save loads. An empty Library is on the old map. Review tools → Style sample (with the Special Grade sheen). **Five rulings:** the night rule, when character scenes start, two-hour activities, the icon and chip style, and whether a Gojo night may pass the grade ceiling (without that it is not offered at the ceiling below Semi-Grade 1). | 10 min | batch 1: icons, the six areas, Tokyo (about $1.45) |
| B | P1 to P4 | The map (areas, then rooms; Tokyo). The corner icons, the icon column, hover labels. The person view. The journal's five tabs, a person's page, the Me page. Grade colours and the armory checklist. A normal night; a Gojo night and the day after; a night in Tokyo: the club, then the Black Market (Review tools get you there). **Questions:** is anything still cluttered? Are the faces on the map too many? Is anything now too hidden, including "where is everyone" without the row of faces? Is two clicks to walk somewhere right? **And the things chosen for you (section 0):** the Gojo night's size and how often (its ceiling rule was ruled at A; say if it now feels too rare); what is closed the day after; the night in Tokyo's price and hangover; market prices; one market-only Special Grade talisman, yes or no. | 30 min | batch 2: the Library, the two offices (about $0.21) |
| C | P5 to P7 | The common room with people blended in; idle to talking. The layout sheets. The computer (and its lead in the Missions tab), fishing, the Library, blackjack and poker. **Chosen for you, to confirm or change:** fishing as proposed; the computer's five sites and the cross-check; card stakes, five hands a sitting, ¥6,000 a day; Library +4; the vending machine. Then batch 3 dropped in: two poses and Yuji's blink. | 30 min | batch 3 ($1.28), then 4 and 5 if they look right |
| D | P8 | Everything, with `docs/PLAYTEST.md`. | a session | the rest, at your pace |

If credits run short after B, stop there: the structure is complete, and C's three packages each stand alone. What waits is then your choice (7.3): nothing you decided is dropped without asking.

---

## 10. Risks

1. **The scaffold is the one package that edits protected files, and it is the biggest.** *Mitigation:* it is three sittings; the tooling sitting (P0a) changes no game file and proves today's tree clean first; additions only; the hooks table is the whole list; the save regression, every phase-1 harness and a pixel comparison of the place view run before any other package starts.
2. **Icons hide words.** *Mitigation:* words stay under an icon until its picture exists (D8); labels on hover everywhere; the icon sheets are the first art batch; one value switches words back on for good.
3. **Painted poses may not match the room.** *Mitigation:* the feathered box hides small shifts; `install_pose.py` refuses a redrawn room; two poses are a $0.64 test before the other twelve.
4. **Blink and mouth boxes over other expressions** can look wrong. *Mitigation:* compatibility lists per expression; Yuji first; cuttable.
5. **The night rule may feel too strict, or surprise an old save** parked at Night away from the dorm. *Mitigation:* one constant; the owner rules at A and judges at B; `PLAYTEST.md` says what an old save will see.
6. **A Gojo night costs a day.** Missions can't be started, but nothing is missed: there are no deadlines (`check_content.py --no-deadline`), story beats still play, and the harness checks the available set afterwards.
7. **Placeholder area pictures are blurry crops.** *Mitigation:* they are in art batch 1, before checkpoint B; `PLAYTEST.md` names them.
8. **Positions measured on stand-in art** (the Library, the two offices) are wrong when the real picture lands. *Mitigation:* sidecars and `tools/layout_sheet.py` (D5); re-measuring is a file drop.
9. **Balance guesses:** night gains, market prices, stakes, fish prices, thresholds. All in tables; the three validators tie them to the board's pay and the grade caps.
10. **P4 carried four jobs.** It is now two packages with disjoint files (P4a, P4b); the market and the night in Tokyo sit behind stubs that hide their buttons, and dropping either is the owner's call.
11. **Motion cost on the owner's Mac.** *Mitigation:* 20 redraws a second at most for each new transform, blur never animated, a Preferences switch built in P0b, and a harness that counts.
12. **A transform that cannot be pickled breaks every save made while it is on screen.** *Mitigation:* R10 (ATL or top-level curried functions for anything shown outside a screen), `pickle.dumps` on what `view_enter` and `lit_sprite` build, and real save-and-load tests in dialogue at P5 and P8.
13. **The Gojo night can be rare to the point of invisible.** With the default (`past_cap = 0`) it is only offered when it can beat a day under the ceiling, which never happens at the ceiling below Semi-Grade 1 (D23). *Mitigation:* section 0 says so in plain words and the owner rules on it at checkpoint A (ruling 5; one constant, `NIGHT_GOJO["past_cap"]`, 3.2); the review button forces one for checkpoint B.
14. **A hotspot hides when someone stands in front of it,** so an action can move between the room and the column from hour to hour. *Mitigation:* P6 places points clear of the room's usual crowd on the layout sheets; the reachability test guarantees the action is always in exactly one place; the one hotspot with no column row (the vending machine) is never hidden.
15. **Harness drift.** Nine phase-1 harnesses pin behaviour this phase changes; each has a named owner (section 8).
16. **Ren'Py behaviours this plan relies on,** checked in the 8.5.3 source: a displayable with a tooltip captures the `"tooltip"` focus rectangle when it gains focus, and the interaction restarts (`renpy/display/focus.py:226-229`); `nearrect` takes `focus` and `preferred_side` (`renpy/display/layout.py:2392-2440`); `config.always_shown_screens` (`renpy/config.py:703`, `renpy/display/screen.py:1654`); a `call` pushes the name of the next statement and `lookup_return` falls back to the call site's `.next` (`renpy/ast.py:1629`, `renpy/execution.py:784-797`); an `if` keeps its name when an `elif` is added, because its `diff_info` is `(If,)` (`renpy/ast.py:2061`); a transform function's return value is the redraw delay (`renpy/display/transform.py:1063-1067`); a `use`d screen with parameters gets a fresh scope and one without copies the caller's (`renpy/sl2/slast.py`, `SLUse.execute`); a new ATL transform in a screen starts from zero (`renpy/atl.py:404-410, 713-719`); `renpy.get_displayable(screen, id)` (`renpy/display/screen.py:1540`) and `focus_list` entries carry `x, y, w, h` (`renpy/display/focus.py:88-96`). Still to prove in P0's harness: the hover label holds across the 0.1 s toast timer.

---

## 11. What is left for later

### Phase 3 (combat)

- Tool and talisman effects, including the four market talismans' `fx`; whether a requirement also gates an effect; depth for tools beyond the checklist.
- Curses coloured by grade in fights beyond the header chip; the combat layout recheck.
- The Nade missions' in-scene `advance_period(2)` and the rest of the time economy (the safety net catches them today).
- A research bonus in board fights (the cross-check only *shows* a misgrade today).
- Tuning: night gains, prices, stakes.

### Phase 4 (story)

- District scenes and making district pins visitable (a pin gains a label); real night-out and Gojo-night scenes; who can be invited.
- Missions that require research (`pc_request`, `gate.flags=("researched_…",)`); the clan arc the genealogy pages seed; the Library's locked shelf.
- The flags `spear_unsealed` and `yaga_signature`.
- Converting the character scenes to "I"; then `rule_hangout_gate` can go.
- `AMBIENT_STORY` rows for each new act.
- Outfits (`MARKET_OUTFITS`) once sprites exist.
- Chess, memory, tic-tac-toe (one file each behind `register_minigame`).
- Blink and talk for Sana (she is staged four times in the prologue, `ch1_alley.rpy`; two pictures, $0.64, no script change) and for Kaito if he is ever staged.
- A market-only Special Grade talisman, if the owner asks for one at checkpoint B.

### Not planned

- A log of skipped rewards (D14); the serif macron font (D52).
- Quick-menu words as icons (History, Auto, Save and the rest): no icon names were frozen for them, no part of section 4 specified them, and the owner did not ask. If wanted later it is six names in `ICONS` and one edit of `screens.rpy`, through P8 or a later phase.

---

## 12. Coverage

### 12.1 The owner's notes (SCOPE section 1)

| note | decision | section | package |
|---|---|---|---|
| Map too cluttered: main areas, then the places inside | D1, D2, D3 | 4.1 | P1 |
| Header too crowded: "Jujutsu High", at the top; the day stays | D1 | 4.1 top row | P1 |
| Clicking an area zooms into its own bird's-eye picture | D1, D5 | 4.1 level 2; art row 2 | P1 |
| "Find someone" belongs in the journal, per character, updated as the story moves | D6, D19b | 4.7 Right now | P1, P2, P3 |
| The strip of faces gets crowded | D6, D3 (three faces a marker, a faces column in the budget) | 4.1 (strip removed), 4.0 | P1 |
| Back to his room at night, with exceptions | D20 to D24 | 4.15 | P4b (hooks P0b) |
| Journal and Menu buttons good; the Map button | D7 (answer 1: it stays) | 4.2 | P2 |
| Small icons, the word on hover | D8 to D11 | 4.3, 4.4, 4.6 | P0, P2 |
| More to do in rooms, e.g. a computer that affects other things | D31 | 4.11 | P6 |
| A board game in the common room | D32 | 4.12 | P7 |
| Fishing | D33 | 4.13 | P6 |
| Little interactive things all over the map | D30 | 4.10 | P0, P6 |
| Blend characters into backgrounds and foregrounds; smoother idle to talking | D35, D38, D17 | 4.5 | P5 |
| People say they're doing something but just stand there | D36, D37 | 4.5 poses; art row 6 | P5, the owner's art |
| Person view cluttered: no name; keep grade and choices | D19 | 4.6 | P2 |
| "Somebody Remembered": is that a quest? | answered in SCOPE; moved to the page | 4.7 Their story | P3 |
| Memories into People, under each person | D18 | 4.7 | P3 |
| Stats a little cluttered | – | 4.7 Stats (three views) | P3 |
| Utahime's board looks good | kept; chips recoloured only | 4.8 | P4a |
| Armory: more depth and requirements, especially the Inverted Spear | D27, D28 | 4.9 | P4a |
| "Same sort of system for the talismans as well" (page 5) | D27's talisman rows | 4.7 Equipment and Inventory, 4.16 | P4a, P4b, P3 |
| Colour by grade, talismans too | D15, D16 | 4.8 | P0b, then P2, P3, P4a, P4b |
| (Also spotted) SKIPPING over headers | D13 | 4.2, 6.3 | P0 |

### 12.2 The owner's answers (SCOPE section 5)

| answer | decision | section | package |
|---|---|---|---|
| 1. Map button stays | D7 | 4.2 | P2 |
| 2. Bed by the last hour | D20, D21, D22 | 4.15 | P4b (hooks P0b) |
| 2. Night with Gojo: rare, beats training every hour of the day, no missions or training next day | D23 (the gain is derived from a day's training, Gojo's lesson included; `NIGHT_REST_BLOCKS`, and no other Control or Output that day; "rare" at the ceiling is ruling 5) | 4.15; P4b's "owner's sentence" test at every training place and on the lesson day | P4b (P6: the two rest-day lines) |
| 2. Tokyo, with the option of nightclubs, a worse next day | D24 (club / market / home on arrival) | 4.1 district view, 4.15 | P1, P4b |
| 2. Black Market there: special talismans, maybe outfits | D24, D29 (its own four; the story Specials are not sold; a market-only Special is offered to the owner) | 4.16 | P4b |
| 3. Bedroom computer: fake internet; Sukuna, Gojo, techniques, the three clans; part of missions; clans seed a later arc | D31 (one lead ships and shows in the Missions tab, and on the computer's own "Requested reading"; the Leads section is cut only with the owner's say; no old mission is gated) | 4.11, 4.7 Leads | P6, P3 |
| 4. Blackjack and poker first, for yen, against whoever is there | D32 (poker is cut only with the owner's say) | 4.12 | P7 |
| 5. Fishing: a proposal | D33 (named as a proposal in section 0; confirmed at C) | 4.13 | P6 |
| 6. Multi-person scenes in each person's memories; a story section is fine too | D18 | 4.7 | P3 |
| 7. Semi-grade takes its grade's colour; all Special Grade gets the oil slick | D15, D16 | 4.8 | P0 |
| 8. The Library, a place to study | D34 | 4.14 | P0b, P1, P2, P6 |
| Open: two-slot activities skipping a noon beat | D26; put to the owner as ruling 3 in section 0 and at checkpoint A | 6.1, 6.3 | P0b |
| Open: first hangouts in "you" on day 1 | D25 | `sb_rules.rpy` | P0 |

### 12.3 What phase 1 deferred to phase 2 (PHASE1 section 10)

| note | decision | section | package |
|---|---|---|---|
| The map hides people inside a locked place | kept, on markers, pins and "Right now" (D6) | 4.1, 4.7 | P1, P3 |
| The `PLACE_STAGING` zooms are guesses | `VIEW_SLOTS` per room, with sidecars | 4.5 | P5 |
| Toasts can show over the game menu | D12 | 4.2 `toast_room` | P2 |
| Toasts are drawn over the journal | D12 | 4.2 | P2 |
| Should skipped rewards go to a log? | D14: no | – | – |
| The People grid and long Missions lists need scrolling | all 18 cards (everyone met, plus Me) fit in four rows without scrolling; the grid is a viewport so phase 4's larger cast scrolls (tested with 26); Missions already scrolls | 4.7 | P3 |
| Serif macron letters | D52: left as is | – | – |
| People in their places; blinking and talking (moved from the storyboard) | D36, D39 | 4.5; art rows 6, 7 | P5, the owner's art |
| Gojo's ridge pose is never seen | D23 pins him there on a Gojo night; pose 14 | 4.15; art | P4b, P5 |
| Art placeholders from phase 1 (`map_tokyo`, the offices, districts) | `map_tokyo` in batch 1, the offices in batch 2; districts stay owed | section 5 | the owner's art |

### 12.4 The judges' flaws and gaps

| raised by | point | closed by |
|---|---|---|
| J-owner | the market behind Grade 2; the loose night; "the Archive" not an internet; beats held after a Gojo night; a bond bar on the person view; text pins; no clutter measure | D24; D20; D31; D23; D19; D3; D48 |
| J-owner gaps | the night ruling; unreadable kanji; no style preview; fixed captions; no mission needs the computer; gains near the cap; unplayed yen; no at-a-glance "where is everyone"; the two hangout holds; tool depth; blurry areas first | section 0 rulings; D8; `icon_sample` at A; D19b; section 0 and D31; D23; D29; People cards and checkpoint B's question; D25; section 0; art batch 1 |
| J-tech | `hot_strip` inside `place_actions`; the hue cycle; the init-time validator; the file hand-over; `VIEW_SPEAKING` in the rollback log; no motion switch | D30; D16; D46; D35; 4.5 (`builtins`); D17 |
| J-tech gaps | return sites; the protected list; saves for new states; stand-in measurements; a frame budget; the foreground under rollback, skipping, replay; boxes with no preview; the net after self-rolling scenes; a mission window missed on a rest day; old saves and the hangout gate | D43; D44, 2.3; `p2_saves`; D5; R9; P5 acceptance; `layout_sheet.py`; D22 and P4 acceptance; P4 acceptance; D25 |
| J-build | P7 too big; the dangling icon list; `sb_do_` labels against the prefix rule; unowned harnesses; no who-calls-whom | P6 / P7 split; D9; R1's exceptions; 7.2; 6.2 |
| J-build gaps | test pictures through symlinks; how rectangles and words are measured; size and failure rule; every file owned once; the night's stub state per checkpoint; the soft clock's stopped case; duplicate ids in registries and harness names; review buttons too late; the hover label with toasts; balance against real tables | D49; P0a task 3 and section 8; 7.1; 7.2; A is today's night, B has the rule (stubs in 6.1); D26; R2; D50; D10 and R6; D27, D29 |

### 12.5 The adversarial review (coverage, feasibility, packages)

| finding | severity | what changed | where |
|---|---|---|---|
| A closure in a transform shown with `renpy.show` breaks every save made in dialogue | blocker | ATL for one-shots; top-level curried functions for loops; a screen-scope rule; save-and-load tests in dialogue | D17, R10, 4.5, P5, P8 |
| The Gojo night lost to a day on the ridge and tied above Control 60 | major ×2 | the gain is derived: a best day plus 6, applied a point at a time; offered only when it can beat a day; tested at every training place | D23, 3.2, 4.15, P4b |
| The market sold three story Specials | major ×2 | removed; `bound_specials` untouched; a market-only Special is offered to the owner | D24, 4.16, section 0 |
| Only one of the two open calls was put to the owner | major | ruling 3 (two-hour activities) at checkpoint A | section 0, D26, section 9 |
| Choices presented as settled facts | major | "Things chosen for you" in section 0; asked at B and C | section 0, section 9 |
| Talismans had colours but no requirements | major | six talisman rows in `ITEM_REQS`; chips in the journal and the market | D27, 4.7, 4.16, P3, P4a, P4b |
| Owner decisions on agents' cut lists | major | cuts are ordered; anything from SCOPE section 5 needs the owner's say | D51, 7.1, 7.3, section 0 |
| Hold the hour and swimming still raised stats on a rest day; the list was hard-coded three times | major | one table, `NIGHT_REST_BLOCKS`, read through `night_blocks` | 3.2, 4.15, 6.3, P4b |
| The People grid did not scroll past 13 | major | a viewport; tested with all 17 met | 4.7, P3, 12.3 |
| Registries defined after the files that register | major | init priorities frozen; `aa_zz_order.rpy` | 6.1, R2, 4.10 |
| Hotspots hidden behind people, actions gone from the column | major | a hotspot is visible only when clear of `view_person_rects`; a reachability test | D30, 4.10, P6 |
| A hotspot could run an action the room was not offering | major ×2 | it exists only while `place_actions` offers its action, and takes label, hint and cost from that row; `standalone` for the vending machine; the storehouse is two rows | D30, 4.10, 6.1, P6 |
| P5 and P6 both owned `layout/<place>.json` | major ×2 | `view_<place>.json` (P5), `hot_<place>.json` (P6), `area_<key>.json` (P1) | D5, 4.5, 4.10, section 5, 7.2 |
| A duplicate-order check on migrations would fail today's tree; `sb_hooks.rpy` had no hooks row | major | migration check dropped; one new validator for place-action ids, listed in 6.3 | R2, 6.3 |
| The price rule could not be evaluated (`g1`, ungraded); a Grade 1 talisman can't be worn in Arc One | major + minor | the rule is stated per tier; Second Wind is Semi-Grade 1 | D29, 4.16 |
| "A board job taken at Night" cannot happen | major | removed; a story beat ending at Night is the third case | D22, P4b |
| Icon glyphs counted as words; the map budget left things out | major | `icon_glyph` style skipped; a word is a token with a letter; budgets itemised | D48, 4.0, P0a, P2 |
| `("hook", q)` needs a value read at click time; R4 omitted actions already in use | major | named Action classes allowed when listed (`fish_Hook`); the allowed list completed | R4, 4.13, 6.1 |
| Wrong line reference for the stage move | major | 405-453; 402-403 and 455 on stay | D35, 4.5, 6.3 |
| The Me page's Records read tables of packages not yet built | major ×2 | `pc_records`, `fish_records`, `cards_records`; every 3.3 `default` written by P0b; stubs for `fish_land`, `cards_new` | 6.1, 3.3, 4.7, P3 |
| Old map tooltips shown twice after P0 | major + minor | `hover_label` draws tuples only; the old frame ignores tuples | D10, 4.3, 6.3, P0b |
| P2 could not lint its Library row | major | the `library` place is laid by P0b | D34, 3.1, 4.14, P0b |
| Dependency and cut claims were false; the night rule never reached the screen without P2 | major | the phase-1 card reads `rail_actions` from P0b; a dependency table; wave 2 branches after wave 1 | 6.3, 4.4, 7.3, P4b |
| The motion switch had no builder | major + minor | P0b: `persistent.motion`, `VIEW_TICK`, `view_motion()`, the Preferences row | D17, 6.1, 6.3, P0b |
| No point where every harness must pass; "unchanged" bullets with no stored baseline | major | `baseline_p0.json` and screenshots (P0a); all `wp*` at P0a, P0b, P8; all `p2_*` at P8; ownership per wave | 2.4, 7.2, section 8, P0a, P2, P8 |
| Toast lane and objective banner overlapped; a fight was silently put on "toasts wait" | major | the banner sits at x 400 to 1300 over the place view; `combat_screen` keeps its toasts; every full screen has a row | D12, R6, 4.2, P2 |
| A cut package left dead buttons (night out, market page, review button) | major | `district_night` hidden on an empty reason; `market_exists()` | 4.1, 4.11, 4.16, 6.1, P1 |
| P0 and P4 too big for one sitting | major | P0a / P0b / P0c and P4a / P4b, mandatory | 7.1, 7.2, risks 1 and 10 |
| Minors | minor | `cards_play` out of `NIGHT_OK`; club / market / home menu; markers show three faces; D1 flagged; a lead in the Missions tab; section 0's voice, art cost, "looks the same"; `advance_period_soft(loc=)`; `renpy.transition` after a scene; names renamed to their prefixes and prefix rows added; generated `gui/` pictures and tokens in package files; status chips in one row; ATL zoom-in and a clamped crop; `night_allows("mission:…")` and the NEW badge; `block_rollback` in cards and fishing; R9 counts new transforms only; `install_pose.py` tolerance and `--box`; `release` in `rail_actions`; `--action-returns` scans `def` bodies and `none_ok.txt` carries example calls; orphan files owned; `zz_texts`, `zz_calls`, `zz_layer_tags` | sections 0 to 8 |

Three findings were answered differently from the fix proposed, each for a reason:
- **Sana's blink and talk** is not added to the art list: she is only in the prologue, and section 0 now says so with the price of adding her ($0.64). The false reason ("if ever staged") is corrected in section 11.
- **"About 43 pictures"** in the proposed wording is a miscount: rows 1 to 7 of section 5 are 3 + 6 + 1 + 1 + 2 + 14 + 20 = 47 paid pictures (47 × $0.32 = $15.04). Section 0 says 47.
- **The night's Control gain** is not raised to a literal +26: a literal would tie or lose again whenever `sb_do_train` changes or Control crosses 60. It is derived from the day it must beat.

### 12.6 The verification pass (the revision checked against the code and against itself)

Three checkers (fixes, consistency, code) read the revised plan. Every blocker and major was applied; every minor was applied. Findings raised by two checkers are one row.

| finding | severity | what changed | where |
|---|---|---|---|
| The "best day" left out Gojo's lesson (Control +5, reserve +5): the night's reserve +8 lost to a lesson day's +9 | blocker, major | `day_lesson`, `day_lesson_reserve` in `NIGHT_GOJO`; `night_day_best()` is the best of the lesson day and the all-train day, over every order; reserve is 12; the harness runs the real lesson day | section 0, D23, 3.2, 4.15, P4b, section 8, 12.2 |
| "Pressed against the ceiling it waits for a promotion" was false below Semi-Grade 1 | major | the default is kept and said plainly, with the numbers; the alternative is ruling 5 at checkpoint A; the missing constant `past_cap` and its cap-bypass are specified | section 0, D23, 3.2, 4.15, P4b, section 9, risk 13 |
| The owner would rule on a flat Special chip at A (the sheen was drawn in P0c, during A) | major ×2 | P0c runs before checkpoint A, in the owner's folder | section 7 diagram, 7.3, P0c, P0b owner check, 4.8, 2.4, section 9 |
| `defaults.json` had no writer; P0c's acceptance could not be met; sidecar schemas were not written down; foreground polygons had two homes | major ×2 | P0b's harness dumps the defaults; P0c's acceptance uses the stage slots and a test sidecar; schemas frozen in 6.1; polygons live in `tools/fg/` | D5, D38, 6.1, P0b task 13, P0c, P1, P5, 7.2 |
| P6's reachability bullet could not pass at Night or on a rest day; P4b's first bullet failed once P6's bed hotspot landed | major ×3 | both are stated over `night_filter_actions(loc, place_actions(loc))` and `hot_covers` | P4b, P6 |
| A person's costed mission and the confession were still offered at Night | major ×4 | two more hook lines in `person_choices` step 1 and inside the confession block of `activity_state`; tests | 4.15, 6.2, 6.3, P4b |
| The protected cards call passed the stake where the label expects opponents | major | `label mg_<id>(opponents, stake=0)`; the call passes `(_cards_opp, _cards_r[2])` | 2.3, 4.12, 6.1 |
| A third `menu` and a second `call market_open` in `sb_night.rpy` were not on the protected list | major, minor | added; `p2_saves` saves at the after-club menu | 2.3, 4.15, P4b, P8 |
| P1 and P6 were told to edit the frozen `p2_contracts.rpy` | major | the three "arrives with" symbols are asserted in `p2_map` and `p2_rooms` | R3, 6.1, 7.2, P1, P8 |
| Three backgrounds had no prompt file and no owner | major | P0c writes ten prompt files | section 5, 7.1, 7.2, P0c |
| "Quick-menu words as icons" had no spec and no icon names | major | removed from P2 and the cut list; `screens.rpy` is P0b's only; listed in section 11 | P2, 7.2, 7.3, section 11, R1 |
| P4b had to pass a validator that only existed in P4a's worktree | major | the validator (`item_validate_reqs`) is written by P0b; the one line that needs P4a's `can_wear` is deferred to P8 | D27, 6.1, 6.3, P0b, P4a, P4b, 7.3 |
| Pose 11 (Yuji at the vending machine) would hide the one hotspot with no column row | major | a standalone hotspot is exempt from the person rule and drawn in front; a test | 4.10, section 5, P6, risk 14 |
| `grade_card` and `dev_panel` have no tag, so a tag test could not hold toasts over them; holding them over `dev_panel` would hide the review buttons' feedback | major | `grade_card` is tested by name; `dev_panel` keeps today's toasts | R6, 4.2, P2 |
| `hook_validate_place_ids` duplicated an existing check | major | removed; `sb_hooks.rpy` is not edited in phase 2 | D42, R1, R2, 6.3, 7.2, P0b |
| The moved stage loop could not see `sb_place`'s variables | major | `view_stage(loc)` computes its own; `view_focus` computes `_x0` | D35, 4.5, 6.3, P0b task 11, P5 |
| `night_filter_actions`' first bullet contradicted the rest-day rule | major, minor | rewritten: rest-day drops at any period, then the Night rules | 4.15 |
| Minors | minor | prefix rows (`gui.rpy`, `ICON`), `stage_person` off the exception list; no Control on a rest day from the barrier shelf or the first fish; `night_exists()` for two review buttons, and the stairs line only when the market exists; R10's line reference; costs ($12.54, backgrounds at the Krea rate) and the candidate question; 18 People cards fit, scrolling tested with 26; Leads cut only with the owner's say; a spar is not a two-hour activity; `AREA_BY_KEY`; `wp11_dev` is P0b's; one cut order for P5; seven missing acceptance lines; `hot:<id>` in `actions_today`; the Inverted Spear's four boxes; `icon` on `person_choices` is P0b's, by the choice's kind; D31's "+1 or `gives`", the Library's shelves; 2.4, risks renumbered, 6.2 and 6.3's wording; `night_step` compounds and the order is maximised; `jr_wear(0, …)`; three line numbers; the two-press district cards in `wp1_world`; the car's night branch marked unreachable; the zoom fallback's clock read at the click; `grade_cap` of `None`; `view_pose`'s `image` is a `str` | sections 0 to 10 |

Nothing was disputed. Two things were answered with the checker's second option rather than its first:
- **The Gojo night at the ceiling:** the default stays "never past the ceiling" (changing it would be reopening a settled decision without the owner); the truth about how rare that makes it is now in section 0, and the choice is the owner's at checkpoint A.
- **Quick-menu icons:** dropped rather than given six new icon names, because nothing in SCOPE asks for them and the icon table is frozen at 88.

One thing this pass could not settle from the files: whether the Nano Banana workflow bills one run or both candidates (section 5). The figures assume one.
