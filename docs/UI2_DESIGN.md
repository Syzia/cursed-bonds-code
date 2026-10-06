# The second UI overhaul: build plan

*Jujutsu Kaisen: Cursed Bonds · written 6 Oct 2026 against branch `ui2` at c7a7728 (the game tree of main at 5f9da45, plus docs and the look-test tool). The owner's word is `docs/UI_OVERHAUL_2.md` ("SCOPE"; it wins over everything here). The audit is `docs/UI_AUDIT.md` ("AUDIT", 134 items, 54 questions). Phase 1 and 2's rules: `docs/PHASE1_DESIGN.md` 2.1 to 2.4 and `docs/PHASE2_DESIGN.md` ("PHASE2") sections 2, 6. What phase 2 really built and the lessons: `docs/PHASE2_HANDOFFS.md` ("HANDOFFS"). Paths are relative to `/Users/hunterjolly/Desktop/JJKgame.md/`. Line numbers are today's.*

This plan was built from three competing designs and three judges' verdicts. It takes the places, the schedule and the owner's latest rulings from the "living campus" design, the save safety and the smallest-risk mechanisms from the "smallest safe steps" design, and the separation of art from code and the proof for every picture from the "pictures first" design. Every factual error the judges found is fixed here; where they disagreed the code was read again and the choice is recorded in the Method note at the end. It was then put through an adversarial review (coverage, feasibility, art); each finding was checked against the code and the pictures, and what changed is item 15 of the Method note. Nothing was run in Ren'Py to write this.

"D12" and the like are the numbered decisions of section 1. "K7" and the like are the ground rules of section 2. "U3" is a work package, "batch 9" an art sitting.

---

## 0. What this overhaul changes, in plain words

**What you will notice when you play**

- **Every place on campus is redone in the look you chose:** a real place, kept clean. Seventeen rooms are redone exactly where they stand, so everything you click stays put; three of those gain one thing each (a laptop on my desk, a desk and photograph for Yaga, the veil on the ridge). The Courtyard is the gateway picture you chose, the Library the bright room you chose; the five yards and all seven maps are designed again.
- **The campus becomes one place.** Before any outdoor picture is made there is one drawing of the whole school from above, every building named and placed once. The yards and the maps are all made from it, so the building on my left in a yard is the building on the left of the map, and every exit sits on the door or path it leads to (indoors, when the door is behind me, the way out sits at the bottom of the picture).
- **My room is inside the Boys' Dormitory.** From the garden I walk into the dormitory's corridor; my door is the one at the end. "Go to bed" works exactly as before, and your old saves load where they were.
- **Eleven new places:** the Boys' Dormitory corridor with Yuji's room, Megumi's room and the room Panda and Toge share; Nobara's and Maki's rooms off the girls' corridor; the Teachers' Lounge with the Teachers' Dormitory behind it; the Bathhouse with its Sauna, up by the mountain path; the Swimming Pool behind the dojo.
- **Night has people in it.** Everybody but Gojo now sleeps on campus. At Night friends are in their rooms, awake, and I can walk in when they are home; the teachers are in their sitting room. Someone behind a door I can't open yet shows on the map and in the journal as being at home.
- **People stand in the room, not on it.** Each place gets its own floor line and size for people, light measured from the picture, a shadow that leans the way the room's light falls, and furniture in front of people where there is furniture. When I look at one person the others stay in the room behind, dimmed.
- **People do things.** Every person has a real line for every place they go, and 22 painted poses: each person in their main place, and the students, Shoko and Gojo at Night. The teachers at home, and people at the baths and the pool, stand as sprites for now. A painted person stays painted while I look at them.
- **Things to click everywhere.** Every place has at least one thing in the picture besides its exits. I can soak at the bathhouse, sit out the sauna and swim at the pool. At the card table I can ask someone over.
- **All the missing backgrounds:** the prologue (alley, diner, home, street, car, city), the Sun Mall, the warehouse and the annexe, the board's job sites, the five Tokyo districts, the club and the Black Market, and a painted campus map.
- **Real people where there are block figures:** Mom, Dad, Kurose and Nade, and painted curses.
- **Screens:** a title picture of its own and a Continue button; saves that say "Day 9 · Tue · Evening · Cafeteria"; a "How to play" page and six small one-time hints; a "Show names" setting (or hold N); choices moved to the side so they stop covering faces.
- **Faces move again** in the character scenes (no new art).

**What isn't in it**

Combat and its screen. New story scenes, the "you" to "I" rewrite, the storyboard's new cast (Sukuna first, with his act). Outfits, music and sound, video, Tokyo places you can walk into, chess and the other table games, item and fish pictures. Section 11 lists each with its phase.

**The order you will see it in**

| step | what you play or do | what you will have made by then |
|---|---|---|
| **Checkpoint A** (about 15 minutes) | The game looks almost the same; that is expected, this step lays the wiring. My room is down a corridor in the Boys' Dormitory. All eleven new places can be walked into on borrowed, tinted pictures. Everyone who lives on campus has somewhere to be at Night. Your old saves load where they were. You look at **one drawing of the campus from above** and say yes, or move something. | nothing |
| **Batch 0, the same day (free)** | The four pictures you have already made go into the game: the gateway Courtyard, the bright Library, the Common Room and the Cafeteria. | nothing to run |
| **Batches 1 to 6** | The rooms where every evening is spent, with their evenings and nights; the first painted person back (Nobara on the sofa); the five yards; the icons; the six area maps and the painted campus map. | 40 renders, about $6.40 |
| **Checkpoint B** (about 30 minutes) | A day and a night on the new campus: walk it by exits alone, soak, swim, ask Toge to cards, click five dead things that now answer, visit a friend at Night, find the teachers at home. People standing properly in the rooms. | |
| **Batches 7 to 13** | Every other room; the campus after dark; the dormitories, the teachers' house, the baths and the pool as themselves; then two painted people (Utahime at her desk, Megumi at the Library's table) as a test. | 53 renders, about $8.50 |
| **Checkpoint C** (about 30 minutes) | The whole campus, all 35 places, by day and after dark. Faces in two character scenes. The title, a save, choices at the side. The two painted people beside the standing ones. | |
| **Batches 14 to 24** | The other painted poses; the prologue; the Sun Mall and the board; Tokyo; the title; blink and talk; Mom, Dad, Kurose, Nade and the curses. | about 99 renders and the four people, about $21 |
| **Checkpoint D** | Everything together from New Game, your old saves, and the list of titles, captions and numbers to review. | |

**What you have to do**

- Answer three of the four questions below now, with this plan (they need no drawing), and at checkpoint A approve the one drawing of the campus.
- Twenty-four small art sittings: drag one file into ComfyUI, press Run, say which version you like. Twelve pictures or fewer each time, each with a page of numbered steps. For a room redone where it stands, the tools install the result at once and you see it in the game after relaunching. For a yard, a map or a new place, after you choose a version you say so in a session and its layout is done for you (about forty minutes) before it shows in the game. The tools, not you, check that nothing moved, vanished or was added, and say in plain words if a picture has to be run again ("the floor cushions by the low table are gone").
- Four checkpoints played from the Ren'Py launcher.

**What it costs**

About **190 renders for about 150 installed pictures, about $36**; allow **$43** for pictures run twice. The campus itself (through checkpoint C, the pose test included) is about **$15** of that. Nothing in the game waits for any of it: until a picture exists the game shows what it shows today, or for a new place a clearly marked stand-in.

**If credits run short,** these wait first, in this order, and you are asked before each: blink and talk for the other ten people ($2.88); the second set of home-at-Night poses ($1.28); the club, the Black Market and the board's job sites ($1.12); the night pictures of the School Courtyard, the staff steps and the Training Yard ($0.48); Nobara's and Maki's rooms ($1.28 with their poses; their doors then stay shut). Nothing you asked for by name is cut without asking, and cutting any of these blocks no other picture.

**Four rulings.** Numbers 2, 3 and 4 are asked **now, with this plan**, because the first step of building rests on them and none needs a drawing. Number 1 is asked at checkpoint A, because it needs the drawing.

1. **The campus from above** (at checkpoint A). You will be shown one drawing. Four things on it are the plan's guesses, not yours: the Bathhouse is up by the mountain path; the Pool is behind the dojo; the teachers' house stands to the right of the staff steps; the Boys' Dormitory is the house on the left of the garden and the Girls' on the right. Yes, or move something? Every outdoor picture depends on this.
2. **Whose rooms.** Five rooms to walk into: Yuji's, Megumi's, the one Panda and Toge share, Nobara's and Maki's. Each is two pictures and a pose (about $0.65). All five, fewer, or someone else? (Asked now so that only the rooms you want are ever built. A room dropped later stays as a shut door; a room added later is a small job of its own.)
3. **The budget and the cut order** above: about $36, allow $43, in twenty-four sittings.
4. **Is your Comfy Cloud plan still active?** The four new people (Mom, Dad, Kurose, Nade) start from a base picture made there. If not, one small test of the local route on Dad comes first.

**You will also be asked, later:** at checkpoint B whether Yuji's talking mouth looks right before ten more are made, and to read the list of new captions; at checkpoint C whether a painted person sits right beside the standing ones (three are bought before nineteen more); at checkpoint D the review of titles, captions and numbers.

**Chosen for you; say the word and any of these changes** (each is one table entry or one prompt line; all 54 of the audit's questions are answered one by one in section 12.2)

- *Living on campus.* Panda and Toge share a room; Maki is in the Girls' Dormitory. Yaga, Utahime and Ijichi live in the teachers' house; Shoko spends her nights in the infirmary on purpose; Gojo is never on campus at Night except on his own night. The Common Room is its own hall and stays empty at Night, as you ruled.
- *Doors.* A friend's room is open whenever they are in it. The girls' corridor after dark opens once Nobara or Maki knows me well enough (Bond 30; today nothing ever opens it). The teachers' sitting room is open at any hour; their bedrooms are doors. The pool's gate is chained at Night. I can always walk out of a room I am in.
- *Weekends.* The river crowd splits: Yuji, Nobara and Panda swim at the pool. Nobara and Utahime spend weekend Evenings at the baths. The teachers use their lounge off duty, and Yaga stays on campus at weekends.
- *The baths.* Nobody is ever drawn in the bath: people stand in the rest hall in uniform, and my soak is a few lines over the picture. One bath a day: a soak brings stamina back, the sauna cursed energy; each takes an hour, so both are closed at Night.
- *The card invite.* From the table: any student I have met who is on campus this hour, no Bond level, up to the three seats, free, not at Night. They walk over and sit down for that hour.
- *Pictures.* The veil shows high on the slope every time I stand on the ridge; Sukuna's body is not shown. Yaga's office keeps its doll hall and gains a low desk with the photograph. No car at the gate (it has a footpath, no road): Ijichi is "on the phone by the torii". Painted evenings and nights wherever people stand after dark, and a real night sky for the six yards and the ridge; everywhere else keeps the tint, which now also darkens the people standing in it (so evening windows in the dojo, the classroom, the training hall and the offices still show daylight under the tint). The dead "Later build" pins in Tokyo are hidden.
- *People.* Poses are single figures, never groups. Faces go onto the campus character scenes now; the "you" lines are not touched. Lines are proposed for every "what they're doing" caption and you approve them at checkpoint B.
- *Screens.* The title is the torii and the steps at blue hour with the campus roofs above; the name stays as text. A small card when the day turns; the hour and yen stay off the HUD. The red seal stays as the game's mark; buttons become icons; one Close everywhere. Notes about later builds are hidden where they are only notes (the journal's extra rows, the "combat update" lines, the dead Tokyo pins); the cards that mark where the story really stops for now stay.
- *Not now:* chess, memory and tic-tac-toe; outfits; music; video; item pictures; a paper or phone view; one-off moment pictures; the storyboard's cast; the lake, the basement, Yaga's workshop.

---

## 1. Decisions

"From" says where the idea came from: C, S, P are the three designs (living campus, smallest safe steps, pictures first); J-owner, J-code, J-art are the judges; "code" means it was settled by reading the game. "Pkg" is the package or batch that builds it.

### 1.1 The owner's (quoted; these bind the plan)

| # | The owner's word | What the plan does |
|---|---|---|
| O1 | "We should go with B, but we need to make it feel clean as-well ... The walls are also sure dirty, we still want to the clean anime look." | One look paragraph, the same in every prompt (5.1). |
| O2 | "I think we should just redo the whole library." / "Library - I also think we go with the Bright room, the two level is just overcomplicating it." | The Library is the chosen bright room, already rendered; installed in batch 0. |
| O3 | "I also think we should redo the courtyard, All 3 buildings look the same. But all 3 lead to different locations." / "Courtyard - I think we go with the gate in the middle aswell." | The Courtyard is the chosen gateway picture, already rendered: schoolhouse left, gateway to the dormitories ahead, training hall right. Installed in batch 0. |
| O4 | "We want the map to flow. But also feel accurate." | The campus bible first (5.2); the yards, area maps and campus map are made from it; a tool checks exits and pins against it. |
| O5 | "I think we should redo every location. They can't look like artworks but instead actual scenearies." | All 24 places (5.3). |
| O6 | "Then we need to blend the characters into the background." | Section 6; poses after the rooms (section 7). |
| O7 | "New locations to add: (We can redo the jujutsu high map) Campus: Teachers' lounge; Osen/sauna recovery rooms; teachers' dorms; Swimming pool. You can add some locations if you feel theyre needed." | Section 4: the four, with the sauna as its own room; the dormitory places below. |
| O8 | "we do need to add dorms, instead of just girls dorms and my dorm. Also where do the teachers stay ... Gojo wont, but the other will." | The Boys' Dormitory, five friends' rooms, the teachers' house. Yaga, Utahime and Ijichi live on campus. Gojo has no room. |
| O9 | "rooms you can walk into" / "But make the boys dorm you the place where the mc stays." | Friends' rooms are places. My Room hangs off the Boys' Dormitory corridor (4.4). |
| O10 | "We can add an invite feature. Like invite toge or panda etc to come play." | 7.4. |
| O11 | "Yes plan sprites too" | Mom, Dad, Kurose, Nade, three curses (5.11). |
| O12 | "We need to put in all the backgrounds that we missed." | Every stand-in background is replaced (5.8). |
| O13 | "This one isnt as important, but we need a good title card." | Its own picture and a Continue button, late in the art order (5.10, 8.3). |
| O14 | Standing words from phase 2: the Common Room in the Evening holds the first years only; the Common Room is empty at Night; Panda in the garden at Night was "for now"; the night is strict; pictures without words. | All kept. Panda moves indoors now that there is a room. |

### 1.2 Places and the map

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D1 | **A building with rooms inside is not a new map area.** One table, `WORLD_INSIDE` (room → the room it opens off), and a few lines of rule in `path_validate`. Level 1 keeps six markers at today's anchors. | A seventh marker costs an area picture, an icon and four whole-list checks (S), and the owner's map stays calm. `path_hub` takes an area key and `path_register`, `path_exits`, `path_neighbours` only walk `PATH_EXITS` (`room_paths.rpy:178, 214-238, 296-333`), so only the validator changes (`:349-364`). (P, C; J-code confirmed the cost.) | U0b |
| D2 | **Home is the key `dorm`, for ever** (K1). Moving my room changes which place its door opens onto, nothing else. | About 180 literals in the game and the harnesses agree on `"dorm"`; every night path teleports there by name. (S) | U0b |
| D3 | **My room keeps its own pin** on the Dormitories map, so "home" is still two clicks and the button `row_dorm` survives. The Dormitories view shows six pins. | C dropped the pin and replaced it a wave later, which crashes `map_area` (`ui_map.rpy:811-812` reads a spot for every place) and breaks the level-1 "no `row_*` button" check (`p2_map.rpy:273`). (P; J-code) | U0b |
| D4 | **Moving my room is its own small package, alone,** proved on stand-ins before anything is built on it. | It is the one change every old save meets. (S; J-code, J-owner graft 9) | U0b |
| D5 | **Eleven new places** (4.1). Five friends' rooms, including Nobara's and Maki's. The sauna is its own room inside the Bathhouse. | "rooms you can walk into"; "Osen/sauna recovery rooms". (C for the five rooms; P for the sauna; J-owner grafts) | U0b, U0c |
| D6 | **The Bathhouse is on the Mountain Path, the Pool on the Training Yard.** No yard goes above seven exits; the garden stays at seven. | The icon column is the real ceiling on exits (`p2_paths.rpy:739-740`). P put both on the Training Yard and took three yards to seven exits on wrong arithmetic. (C, S; J-code) | U0c |
| D7 | **The teachers' house is one building:** the lounge downstairs, the Teachers' Dormitory (a sitting room with bedroom doors) reached through it. Both are open at any hour. | One more exit on the staff steps, not two; and the teachers can be found at Night. (C for the house; S for the door rule; J-owner graft 10) | U0c, U1 |
| D8 | **`person_now` keeps its exact six keys.** For someone at home behind a door I can't open, only `name` changes ("In the Girls' Dormitory"). | `p2_contracts.rpy:431-436` asserts exactly six keys; C and P each added one. `jr_now_line` prints `name — doing` and needs no change. (S; J-code) | U1 |
| D9 | **Gojo's Night is decided in `char_location`,** before story pins, so his own night still wins. `roll_gojo` and `GOJO_SPOTS` are not touched. | No saved value changes and no other day's draw moves. (S, P) | U1 |
| D10 | **The girls' corridor after dark opens at Bond 30 with Nobara or Maki** (one more clause in `place_access`; the old flag still works), with one toast when it first does. | The flag `invited_girls_dorm` has no setter in `game/`. Bond 30 sits between "Study together" (25) and "Swim together" (35). (P's number; S's clause) | U1 |
| D11 | **The Common Room stays empty at Night by routine.** Nobara's weekend Night is her room. | `wp1_world.rpy:329-334` asserts it, and it is the owner's standing word; C put Nobara there. (J-code) | U0c |
| D12 | **Budgets are raised once, on purpose** (K11): 35 places; six pins on an area view (Dormitories only); 18 words on an area view; 114 icons. | The word budget counts the title, Back and the date chip as well as the plates (`_lib.rpy:392-403`): Dormitories and Staff both come to 17. All three designs miscounted it. (J-code) | U0a, U0b |

### 1.3 Pictures

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D13 | **The look is `LOOK3`, and a redo in place puts `KEEP` in front** (`tools/make_look_workflow.py`), word for word for an indoor room by day, which is all the tests have tried. Outdoor redos, relights and named additions use stated variants of `KEEP`, each tested in its first batch (5.1). Never "nothing on the floor". | SCOPE 3c: the second test's wording emptied the Common Room; the third test's kept everything. (C; all three judges) | U0d |
| D14 | **The campus bible is built on the chosen gateway Courtyard and the chosen Library,** and is approved by the owner before any outdoor picture is made. | SCOPE 3c. P's bible was built on the main hall. (C) | U0d |
| D15 | **Batch 0 installs the four pictures already made, free.** | The first thing the owner sees after checkpoint A is the look, in the game. (C; J-owner, J-art) | batch 0 |
| D16 | **The Common Room and the Cafeteria are run once more with their window line from the bible,** in the very next sitting, with their evening and night pictures straight after. | The third-test renders show a town-style house outside (the look text's generic "tiled roofs"). The Library's roofs are made true by the bible instead: its windows face the Cafeteria. (J-art errors 2 and 13) | batch 1 |
| D17 | **A picture carries its numbers** (K2): every number measured on a picture lives in a sidecar beside it, exits included; installing a picture changes no `.rpy` file and no harness. | Phase 2 paid twice for the yards (111 + 190 lines). The reader for exits in a sidecar already exists (`room_paths.rpy:226-231`). (P; J-code graft 3 over S's "exits never in a sidecar") | U0a, U0c |
| D18 | **A picture is installed only by the tool that proves it** (K6): in place, nothing moved, nothing vanished, nothing was added; composed, its layout passes the screen's rules. Refusals are in plain words. | (P's guard zones and keep lists; C's floor measure; S's "refused twice becomes a new composition"; J-art) | U0d |
| D19 | **The sharpness check passes at twice the figure of the picture the place had before this overhaul** (revision 1, from git), never the installed one, **and warns below it.** A second redo of a room already in the look would otherwise be refused. | "Three times" would refuse or nearly refuse the look the owner approved: the third-test Common Room measures 3.0 times, the Cafeteria 7.5. (J-art error 1) | U0d |
| D20 | **Nothing stale is shown** (K7): a record of which picture is at which revision; an evening, night, foreground, pose or light row made for the old picture steps aside until it is remade. An hour picture is not used until its foreground exists. | The owner plays between batches. (P's manifest; C's foreground clause; J-code graft 4, J-art graft 4) | U0c |
| D21 | **All missing backgrounds are in,** including the Sun Mall's three, the warehouse, the annexe, five kinds of job site, five districts and two nights, the club and the market. They are first on the cut order, not left out. | "all the backgrounds that we missed". (P; J-owner graft 1) | U0c (the names); batches 18 to 21 |
| D22 | **Nothing lends any more.** The scaffold copies each flat file that other stand-ins are tinted from into `game/images/bg/standin/`, and every stand-in borrows from the copy (what D24 does for the menus). A picture can then be painted in any order and cut without blocking another. | "Lenders last" (S) deadlocked with the cut order: with the job sites cut, the prologue's street and city could never be installed (review). | U0c |
| D23 | **The alley is fitted to the lamp's number,** not the number to the alley. `ch1_alley.rpy` is not opened. | Eight of the owner's saves rest in the prologue. Reward lines over the lamp (AUDIT L2) wait for the story phase. (S; J-code) | batch 18 |
| D24 | **The menus stop borrowing `veil.png` in the scaffold** (a copy of today's file becomes `game/gui/menu_ground.png`); later the menu ground is made free from the title picture. The title stops borrowing the gate's file the same way. | So the veil and the gate can be repainted at any time. P's rule blocked the veil for seven batches. (S; J-art graft 6) | U0c, batch 21 |
| D25 | **No batch is over twelve renders; counts are of renders, not pictures.** Poses and blink-and-talk are split. | The owner presses Run for renders. (S's splits; J-art errors 7, 10, 11) | 5.13 |
| D26 | **Two small tests before big buys:** the plan as a reference (two yards and one area map, batch 3) before the other yards and maps; three poses (batches 2 and 13) before nineteen. | Whether the editor follows a plan drawing, and whether a painted person matches the sprites in the new look, have never been tried. (all three; J-art error 12) | batches 2, 3, 13 |
| D27 | **Sprites are budgeted at $1.00 to $1.50 a person,** one face each now; the local route is tried on Dad first if the cloud plan has lapsed. | (S's figure; C's fallback; J-art graft 9) | batch 24 |

### 1.4 People, blending, things to do

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D28 | **Nothing is added to the saved sprite** (K9). The shadow's lean and stretch ride as two more values at the end of a light row; `_shadow_light` keeps its name and signature and sets two more properties. | `scene_light` is set from the picture shown at five points, one in a frozen file (`lighting.rpy:108-121`, `view_stage.rpy:552`, `sb_board.rpy:762-768`, `sb_tokyo.rpy:171`); all go through `light_for_place` / `light_for_bg`, so all five follow with no edit. P read the shape by `store.here`, which is wrong in every story scene; C added a saved value nobody set at four of the five points. (S; J-code graft 5) | U0c, U3 |
| D29 | **Light is measured from the picture** and written beside it by the installer; a person may tune it within a set distance. Where an hour is only a tint, people take 60% of the room's tint. | "Panda glows in the night garden" (AUDIT T1). (S, C) | U0d, U3 |
| D30 | **The others stay in the room, dimmed, while I look at one person.** In the conversation itself they still step out. | `sb_char` is its own screen and can draw them without touching the loop (`sb_screens.rpy:782-793`). (C; J-code corrected S's reason) | U0c hook, U3 |
| D31 | **A painted person stays painted while their card is open** and stands up only when a scene starts, if the scaffold proves it is screen-only; otherwise as now. | It removes the pop the audit's P4 describes. (P; J-owner graft 6) | U3 |
| D32 | **22 poses in three steps;** a pose steps aside when a story caption says something else. | (C; S's caption rule) | U3; batches 2, 13 to 17 |
| D33 | **New actions, the whole list:** Soak, Sauna (one bath a day between them), Swim at the pool (the river's numbers), "Swim together" at the pool (a new activity, `swim_pool`, with the river's numbers and its own pool scene, because `act_swim` shows the river by name in a frozen file), "Ask someone to the table". Existing actions gain places: Train at the yard's posts, "Walk with them" in the yards, "Sit out with them" in the garden, "Study together" in three friends' rooms. No number that exists today changes. | Scope allows "a recovery action at the baths, swimming at the pool". (C, P, S) | U4, U5 |
| D34 | **`pool_swim` and `swim_pool` join `NIGHT_REST_BLOCKS` in the scaffold,** in `sb_night.rpy` itself, and the scaffold's stubs register the three new actions (closed) so the night validator knows the ids. | S forgot it; C's "add it from `room_pool.rpy` at init" fails because that file sorts before `sb_night.rpy`. `night_validate` (`sb_night.rpy:424-433`) refuses an id that is not a registered action. (J-code; review) | U0c |
| D35 | **The invite is from the table, students only, no Bond level,** by the existing story-pin function. | Closest to the owner's sentence. (S; J-owner) | U5 |
| D36 | **"Show names" and a held key (N) are wired in the scaffold** (the three files that draw names are then left alone); the Preferences row arrives with the screens package. Not Tab: Tab is Ren'Py's skip toggle (`00keymap.rpy`: `toggle_skip = ['K_TAB']`) and the game does not rebind it. | C and S gave the work to packages that did not own the files. (J-code; review) | U0c, U3, U6 |

### 1.5 Scenes, screens, method

| # | Decision | Why / from | Pkg |
|---|---|---|---|
| D37 | **Story files are opened by one package, alone, after everything else has merged,** in two commits: seven listed `scene` lines, then faces as say attributes on the campus character scenes. A names check proves no statement moved. | Seven of the owner's saves rest on menus inside story files. P spread story edits over two packages and eleven files. (S's isolation; P's swap list; C's scope for faces; J-code) | U9 |
| D38 | **`show mother sad` is not added.** Mom's one face is painted for the scene she is in. **The Black Market's ground is drawn by its own screen.** The club needs one new `scene expression` line, in the placeholder night-out label. | Fewer statements added where saves rest (`ch1b_the_offer.rpy`; the protected `call market_open` pairs in `sb_night.rpy`). (J-code; code) | U7, U8, U9 |
| D39 | **Faces are on by default and first on the cut list.** | The owner asked for "anything else ... everything related to UI"; S's "only on a yes" asked too much. (C, P; J-owner) | U9 |
| D40 | **The engine screens are restyled, never rewritten;** names, parameters, ids and the Preferences words the harnesses read stay. | They are phase 1's work with checks that read them. (all three) | U6 |
| D41 | **No migration. `SAVE_VERSION` stays 1.** New saved state: one variable, `hint_seen`. | (all three) | all |
| D42 | **The safety net is built first:** the owner's eleven saves are snapshotted (they keep playing, and autosaves are overwritten), six more are made on purpose in the places this overhaul changes, and every package loads all seventeen. | (S; J-owner graft 9, J-code) | U0a |
| D43 | **A ledger of harness lines this overhaul is known to change** is written before anything changes; a ledger line failing for its listed reason is a hand-off, not a failure. | HANDOFFS' first lesson. It includes `p2_saves.rpy:452-457`, which all three designs missed. (S; J-code) | U0a |
| D44 | **Harnesses pin rules, not coordinates** (K3), each rewritten check proved by one negative test. | A recomposed Courtyard would otherwise fail a dozen lines for reasons that are not faults. (P, C; J-code graft 3) | U0a |
| D45 | **A standing art-install role** owns pictures and their sidecars and never a `.rpy` file, so it can run beside any wave. | (P) | L |

---

## 2. Ground rules

### 2.1 Carried over, unchanged

PHASE1 2.1 to 2.4 and PHASE2 2.1 to 2.4 stand as written:

- Protected statements stay textually identical (PHASE2 2.3's list, with `room_paths.rpy`'s `label path_walk` and all 24 `label sb_do_path_<to>`). New branches are new lines; new labels are **appended** to the end of their file.
- No label is deleted. No store variable is renamed. New state is `default` and holds only plain values. Nothing un-picklable is saved or shown (R10).
- The owner's `game/*.rpyc` are never deleted, moved or force-recompiled. Worktrees get `cp -p` copies and never copy back.
- Screens keep their names, parameters and return tuples. An action id is never renamed (the loop calls `"sb_do_" + id`).
- First person; no literal protagonist name; Kaito never on screen. New text passes `check_content.py --narration-person`.
- R1 prefixes, R2 checks, R3 frozen return values, R4 screen actions, R5 fixtures from constructors, R6 lanes, R8 drop-in art, R9 the motion budget, R10 picklability. PHASE2's D43 (never edit a `call` and the statement after it in one phase) and D51 (a failed package gets one retry with its log, then the owner is asked; a cut of something the owner decided is the owner's call).
- **Frozen for the whole overhaul** (only integration, U10, may touch them, and it expects to change none): `sb_loop.rpy`, `sb_tokyo.rpy`, `sb_missions.rpy`, `sb_events.rpy`, `sb_hooks.rpy`, `explore.rpy`, `script.rpy`, `sb_combat.rpy`, `jjk_screens.rpy`, `sb_threads.rpy`, and every `ch*`, `story_*`, `missions_*` and `events_*` file except the lines U9 lists (8.1).

### 2.2 New rules, each designing out a known way to fail

Lettered K so they are not mistaken for packages (U) or phase 2's rules (R).

**K1. Home is the key `dorm`, for ever.** The place key `dorm`, its image name `bg your_room`, its files `your_room*.png`, its label `sb_do_path_dorm` and `default here = "dorm"` never change. No HOME constant is introduced.

**K2. A picture carries its numbers.** Every number measured on a picture or judged from one (exit points, hotspot points, hover-label sides, standing slots, the floor, a door for scale, pose boxes, foreground outlines, light rows, map pins, the Mountain marker's box) lives in `game/layout/` or `tools/fg/`, in a file named for the picture. Tables in `.rpy` files hold only schematic defaults that lint clean. **Installing a picture changes files under `game/images/`, `game/gui/`, `game/layout/`, `tools/fg/`, `tools/bgs/` and nothing else:** no `.rpy` file, no harness. (The one exception is as old as the pipeline: installing a new person's sprite regenerates `game/jjk_sprites.rpy`.)

**K3. Harnesses pin rules, not coordinates.** A check on an exit, slot, pin or polygon asks "inside the frame, clear of the lanes, on the floor, apart from its neighbours", never "equals (1640, 850)". A count of art-dependent rows is read from its table, never written as a literal. U0a makes this change once, on the untouched tree: each rewritten check must give the verdict it gave before, **and must fail when its sidecar is deliberately broken** (one negative test per rule). A literal coordinate added to a harness later is a review finding.

**K4. The bible first.** No outdoor prompt is written by hand; every one is built by a tool from `tools/bgs/campus.json`. The tool refuses to make an outdoor picture until the owner has approved the plan (checkpoint A, question 1). A later change to a building's look or position marks every picture that shows it "check this one" in the status list.

**K5. One look.** `tools/bgs/look.txt` is the only place the look is written; every maker reads it. A redo in place puts the keep text in front (`keep.txt` indoors, `keep_outdoor.txt` outdoors; `keep_light.txt` after it for a day redo only; 5.1). `tools/check_prompts.py` fails any assembled prompt that contains a banned word or phrase (5.1). The look text and `keep.txt` are frozen after batch 1, `keep_outdoor.txt` after batch 8.

**K6. A picture is installed only by the tool that proves it.** `tools/install_redo.py`: for a redo in place, nothing moved, nothing vanished, nothing was added, sharper than before; for a new composition, a layout that passes the screen's rules. A picture refused twice in place is made as a new composition and laid out again, and the checkpoint note says so. `install_bg.py` is never used for a redo (its fit drifts 7 px at the edges), nor `install_pose.py`'s colour rule (it reads 44 to 56% "changed" on a good redo).

**K7. Nothing stale is shown.** A foreground, an evening or night picture, a pose or a light row made for a room's old picture is not used once that room's picture is replaced; the game falls back to what it does when the file is missing (the day picture tinted, the standing sprite, the general light). Foregrounds are recut by the installer in the same run. An hour picture in a room with a foreground is not used until its foreground exists. Written scenes and memory rows that name an hour picture themselves bypass this (`scene bg your_room night`, five times; `scene bg rooftop evening`, twice; and `sb_memories.rpy:182-253`, which stage memories on `bg your_room night`, `bg rooftop evening`, `bg rooftop night`, `bg infirmary night` and `bg dorm_common night`), so **a day picture and its hour pictures are always made in one sitting.** The one known gap is the Common Room between batch 0 and batch 1 (its day picture is already made): for that one sitting the memory "Eleven Tuesdays" shows the old night picture; the checkpoint A note says so and `art_status.py` lists it under "half-made room sets".

**K8. Order is enforced by the tools.** An hour picture cannot be made before its day picture is installed in the new look; a pose cannot be made before the picture it is painted on; an outdoor picture cannot be made before the plan is approved. The maker refuses and says what is missing. (There is no rule about lenders: nothing lends any more, D22.)

**K9. Nothing new in a saved sprite.** `lit_sprite`'s displayable tree, `_sprite_light`, `_shadow_light`, `view_blink_fn`, `view_talk_fn`, `view_breathe_fn`, `hot_pulse_fn`, `view_enter_ease`, `char_focus` and every `pos_*` transform keep their names, signatures and shapes. Blending is done by data those functions already read, or in `view_sprite` and the stage screens, which never reach a save. Files that sit inside saves keep their paths: every `images/char/...` file, `images/fx/contact_shadow.png`, `images/fg/fg_cafeteria.png`.

**K10. Story files: one package, alone.** Only U9 opens a story file. It may change the image name on the seven listed `scene` lines, add the one listed `scene` line, and add say attributes; no quoted text changes, no statement is removed or moved, no menu, call, flag or reward line is touched. Each of its two commits is right the first time (a line reworded, compiled and put back has lost its name for good), and is proved by the names check (8.1) in a tree whose `.rpyc` are copies of the owner's.

**K11. Budgets are raised once, on purpose, in the contracts file:**

| budget | today | this overhaul | pinned at |
|---|---|---|---|
| places | 24 | **35** | `p2_map.rpy:350`, `p2_paths.rpy:393` (both become `len(LOC_ORDER)`) |
| markers on level 1 | 6 | 6 | unchanged (`p2_map.rpy:272, 282`; `wp1_world.rpy:241-243`) |
| pins on an area view | 5 | **6** (Dormitories only) | `p2_map.rpy:352` (buttons ≤ 10 becomes ≤ 11) |
| words on an area view | ≤ 16 | **≤ 18** (Dormitories and Staff are 17: the plates, the title, Back's "Jujutsu High" and the date chip all count) | `p2_map.rpy:351` |
| exits from a yard | 7 (the garden) | 7 (the garden); the staff steps and the Training Yard 6, the Mountain Path 5 | `p2_paths.rpy:316, 483, 1089` become "at most 7 and equal to its table" |
| tiles in the icon column with people in the place | ≤ 8 | ≤ 8, **not loosened** (`p2_paths.rpy:739-740`) | 4.6 says how each yard is laid out to keep it |
| icons | 88 | **114** | `p2_contracts.rpy:1052` becomes "the count the sheets hold" |
| faces on the map | 3 a pin, 18 in all | unchanged | `p2_map.rpy:299-301` |

**K12. A new place is walkable on a stand-in before its picture exists,** and its stand-in is a borrowed, mirrored, tinted picture that cannot be mistaken for the real room. Until a yard is repainted, an exit to a new building sits at a clear point on the old yard picture, on the planned side where the old picture has that side and otherwise wherever it is clear; the old exits stay on today's sides. The checkpoint note says so, and `check_campus.py` reports such a yard as waiting for its batch, not as wrong (5.2).

**K13. Phase 2's four lessons, as rules.**
- *A failing check that is a hand-off is not a failure.* U0a writes `docs/UI2_PINS.md`, the ledger of every harness line this overhaul is known to change (10.3), each with the package that changes the behaviour and the package that owns the harness that wave. A ledger line that fails for its listed reason is logged with the exact edit, proven in a scratch copy, and passed to its owner.
- *Pointer harnesses run alone:* `p2_contracts`, `p2_hud`, `p2_map`, `p2_paths`, `p2_view` and the new `u2_map`, one at a time, no game window open, never from two worktrees at once. This is enforced, not asked: `tools/smoke.sh` takes a machine-wide lock (a directory under `~/Library/Caches/`) before a harness on the pointer list, waits for it, and refuses with one line while a window of this game is open. A hover failure is rerun alone before it is believed.
- *Review rounds are capped.* A package gets at most two review rounds; a third happens only for a finding about a save, a crash, a contract or the owner's word. Wording goes on the owner's reading list.
- *Everything a reviewer needs is in the repository:* the plan, the look, the manifest, the baselines, the keep lists; the old pictures come from git (`git show <commit>:game/images/bg/<file>`); the six made saves are committed under `tools/smoke/assets/ui2_saves/`, and the snapshot of the owner's eleven is named, with a checksum for each, in `docs/load_report_ui2_wave0.txt`. `tools/review_pack.sh <package>` regenerates that package's layout sheets, stage sheets and screenshots. Nothing lives only in a scratch folder.

**K14. Two Pythons; paid runs are the owner's.** A tool that needs numpy or Pillow starts through `tools/py_art.sh`, which finds ComfyUI's Python (`~/ComfyUI-Installs/ComfyUI/standalone-env/bin/python`) or prints one clear line and exits. A harness that needs such a tool prints `SKIPPED (no ComfyUI python)`: a pass for a code package, a failure for an art sitting. A tool writes the workflow and the note; the owner presses Run. No tool queues a paid node.

**K15. An art sitting never writes a file an open worktree owns.** Light rows are in their own file (`light_<place>.json`) and pose boxes in theirs (`pose_<place>.json`), so that installing a room or a pose during a wave touches nothing a package is editing. The `hot_` and `view_` files of rooms redone in place belong to U4 and U3 and carry no `for_rev` (3.2), so an install never has to rewrite them.

### 2.3 Statements that become protected in this overhaul

From the commit each lands in, these stay textually identical, each with the line after it.

| file | statements |
|---|---|
| `room_paths.rpy` | the eleven appended labels `sb_do_path_boys_dorm`, `_yuji_room`, `_megumi_room`, `_senpai_room`, `_nobara_room`, `_maki_room`, `_teachers_lounge`, `_teachers_dorm`, `_bathhouse`, `_sauna`, `_pool`, each with its line `call path_walk("<to>")` |
| `room_cards.rpy` | `call screen cards_invite_pick` / `$ _cards_i = _return` |
| `room_bath.rpy` | `label sb_do_bath_soak`, `label sb_do_bath_sauna` (their names; no menu and no called screen inside) |
| `room_pool.rpy` | `label sb_do_pool_swim`, `label act_swim_pool(who)` (their names) |
| `sb_night.rpy` | the one new line `scene expression night_club_bg(key)` (U9), once it lands |

Action ids that never change once shipped: `path_<key>` for the eleven keys, `bath_soak`, `bath_sauna`, `pool_swim`, `cards_invite`; and the activity id `swim_pool` (the loop calls `"act_" + id`).

---

## 3. Data model

### 3.1 Tables changed (init data, never saved)

| table | file | change |
|---|---|---|
| `LOCATIONS`, `LOC_ORDER` | `sb_world.rpy` | +11 rows, appended, each written `"<key>": dict(indoor=..., name="...", bg="bg <key>", ...)` in exactly that order (three tools find a place's picture by that pattern). The Library's `desc` is rewritten for a bright room. |
| `AREAS[…]["places"]`, `["spots"]`, `["blurb"]` | `sb_world.rpy` | new keys appended to `dorms`, `staff`, `grounds`, `mountain`; `spots` holds only places that are not in `WORLD_PINLESS`; the `dorms` blurb loses "where everyone ends up by evening". The six `anchor`s do not change. |
| `SCHEDULE`, `WEEKEND` | `sb_world.rpy` | 4.3; `WEEKEND` gains Night cells |
| `TIME_VARIANT` | `sb_world.rpy` | the eight static rows stay; new cells are filled at init from `WORLD_VARIANTS` for files that exist |
| `place_access`, `char_location`, `person_now` | `sb_world.rpy` | 4.2 (return shapes unchanged) |
| `PATH_EXITS`, `PATH_TO_WORDS` | `room_paths.rpy` | 4.5; code holds defaults, the picture's sidecar wins. `PATH_LINKS` and `PATH_HUBS` do not change. |
| `PATH_KEEP_CLEAR` | `room_paths.rpy` | kept as the fallback only; `path_keep_clear(loc)` reads the place's live hotspot points, which ends the three hand copies |
| `path_validate` | `room_paths.rpy` | the house rule (4.4); the spacing rules read each exit's applied point (sidecar first), not the code row |
| `path_icon` | `room_paths.rpy` | a yard is drawn as `place_<yard>` when `icon_has_art("place_" + yard)` is true at the moment it is drawn (the sheet has been cut), else its area's icon as today. So from checkpoint A to batch 5 nothing changes on any exit and no column drops to six tiles. `path_validate` keeps its test on the fallback name. |
| `NIGHT_REST_BLOCKS` | `sb_night.rpy` | + `pool_swim`, `swim_pool` |
| `night_club_bg(key)` | `sb_night.rpy` | new helper: `"bg club"` when that image exists, else `night_bg(key)` (the club in Shinjuku must not show a Shibuya stand-in) |
| `ICONS`, `ICON_FOR` | `ui_icons.rpy` | 88 → 114 names, final in the scaffold (4.8); `ICON_TIP_SIDES` stops being the only source: a `hot_` sidecar's `tips` wins, and with neither the side is worked out from where the tile is |
| `AMBIENT`, `AMBIENT_NEEDS` | `sb_screens.rpy` | every routine cell gets its own caption (7.1) |
| `place_actions` | `sb_screens.rpy` | `train` is offered at `training_yard` |
| `ACTIVITIES` | `sb_activities.rpy` | one new row, `swim_pool` ("Swim together", `loc=("pool",)`, with `swim`'s kind, Bond 35, cost and periods; it takes `swim`'s place in the choice order and in `TRAIN_TOGETHER`); `swim` stays at the riverside only. `loc` gains: `study` + `yuji_room`, `megumi_room`, `nobara_room`; `stargaze` + `dorm_yard`; `walk` + the five yards |
| `SPOT_SET`, `SPOT_LOOKS`, `SPOT_LINES` | `room_spots.rpy` | 7.3; the ids are the ones frozen in `SPOT_PLANNED` (3.2) |
| `VIEW_SLOTS`, `VIEW_FG_ROOMS`, `VIEW_FG_TALK` | `view_stage.rpy` | defaults only; the room's sidecar wins; a foreground room is "a room with a fresh cut for the hour" |
| `PLACE_LIGHT`, `BG_LIGHT`, `OUTDOOR_LIGHT`, `INDOOR_LIGHT` | `lighting.rpy` | kept as the fallback; a measured row from a sidecar wins; a row may hold four or six values (6.2) |
| `BOARD_PLACES[*]["bg"]` | `sb_board.rpy` | the five `bg site_*` names (5.8), set in the scaffold together with the names themselves, so the board's own validator (`sb_board.rpy:875-876`) never meets a missing image |
| every new off-campus image name of 5.8 | `bg_placeholders.rpy` | defined in the scaffold with its stand-in (5.8) |
| the stand-in people, `image curse big` | `jjk_defs.rpy` | 8.2 |
| `gui.main_menu_background`, `gui.game_menu_background` | `gui.rpy` | 8.3 |
| one memory row | `sb_memories.rpy` | "Breakfast for Four" is staged on the alley, not the konbini; "The Boy in the Car" is set where Panda now is |
| `POSES` | `tools/make_pose_workflow.py` | 22 rows (7.2) |

### 3.2 New tables, functions and files

| name | where | what |
|---|---|---|
| `WORLD_INSIDE` | `sb_world.rpy` | `{room: the room it opens off}`, one level deep: `dorm`, `yuji_room`, `megumi_room`, `senpai_room` → `boys_dorm`; `nobara_room`, `maki_room` → `girls_dorm`; `teachers_dorm` → `teachers_lounge`; `sauna` → `bathhouse`. `world_inside(loc)` returns the house's key or None. |
| `WORLD_PINLESS` | `sb_world.rpy` | `("yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room", "teachers_dorm", "sauna")`: reached on foot or by "Go there"; no pin. `dorm` is **not** in it. `world_pinned(loc)` → bool. |
| `WORLD_HOMES` | `sb_world.rpy` | `{who: place}`: Yuji, Megumi, Nobara, Maki to their rooms; Panda and Toge to `senpai_room`; Yaga, Utahime, Ijichi to `teachers_dorm`; Shoko to `infirmary`. Gojo has no row. `world_home(who)`. |
| `WORLD_VARIANTS` | `sb_world.rpy` | every planned new hour picture as `(place, period, attribute, file)`. At init a row whose file is loadable registers its image with `renpy.image` and its `TIME_VARIANT` cell; a row whose file is missing does nothing. A new check reports any `TIME_VARIANT` cell with no image. |
| `SPOT_PLANNED` | `sb_hotspots.rpy` | every hotspot this overhaul will register, as `(id, place, kind)`, for all 35 places (7.3's looks and moved actions, the new places' actions). Frozen in the contracts file. `hot_validate` and `check_layout.py` accept a sidecar point for a planned id that is not registered yet, so a layout sitting before wave 1 places every point once. `u2_things` checks that wave 1 registered exactly these. |
| `WORLD_WELCOME_BOND = 30`, `world_welcome_check()` | `sb_world.rpy` | the girls' corridor (4.2); the check runs from the new-day hook and sets the existing flag once, with its toast |
| `art_rev(stem)`, `art_fresh(stem)`, `art_validate()` | `game/art_manifest.rpy` (new; prefix `art_`) | the manifest reader (5.5) |
| `path_keep_clear(loc)` | `room_paths.rpy` | list of (x, y) |
| `light_row(loc, variant)`, `light_follow(row, grade)`, `light_validate()` | `lighting.rpy` | 6.2 |
| `view_floor(loc)`, `screen view_others(loc, who)` | `view_stage.rpy` | 6.2 |
| `bath_*` | `game/room_bath.rpy` (new) | Soak and Sauna, their labels and lines |
| `pool_*` | `game/room_pool.rpy` (new) | Swim, its label and lines; `label act_swim_pool(who)`, the shared swim's own scene on `bg pool` (a `prefixes.json` exception for the one `act_` label) |
| `hint_*` | `game/ui_hints.rpy` (new) | the six hints, `screen hint_layer`, `default hint_seen` |
| `cards_invitable()`, `screen cards_invite_pick` | `room_cards.rpy` | 7.4 |
| `standin_*` | `jjk_defs.rpy` (gains a `prefixes.json` row for this prefix only) | the guarded stand-in block (8.2) |
| `sys_*`, `gui.sys_*` | `screens.rpy`, `gui.rpy` | new helper screens and tokens for 8.3 |

**Sidecars** (`game/layout/`, all read through `rule_layout`; shapes frozen in the contracts file and checked by a new rule, `check_content.py --layout-files`):

| file | written by | keys |
|---|---|---|
| `hot_<place>.json` | a layout sitting (L), or U4 for a room redone in place | `spots` (hotspots by id; exits by `go_<from>__<to>`, the reader exists today), `tips` (hover-label sides), `for_rev` (composed pictures and new places only) |
| `view_<place>.json` | a layout sitting, or U3 for a room redone in place | `slots`, `poses` (today's two keys; still read, for the two poses that exist), `floor`, `scale`, `slot_light`, `cast`, `talk`, `for_rev` (composed pictures and new places only) (6.1) |
| `pose_<place>.json` | `install_pose.py` only | `poses`: the pose boxes, read by `view_pose` before the `view_` file's own `poses` key |
| `light_<place>.json` | the installer, from the picture | `{"": row, "evening": row, "night": row}`, each row four or six values |
| `light.json` | the installer | rows for story pictures, keyed by image name (`"bg alley"`) |
| `area_<key>.json` | a layout sitting | `spots` (as today), `for_rev` |
| `map_campus.json` | a layout sitting | `anchors` (optional nudges), `mountain_box` |
| `pictures.json` | the installer only | the manifest (5.5) |

A sidecar that carries `for_rev` is ignored, with a lint line, when the installed picture is at another revision. **Only a layout written by `install_redo.py --compose` carries `for_rev`.** The sidecars of the seventeen rooms redone in place carry none: the "nothing moved" proof is what keeps them valid from revision to revision, and with a `for_rev` every later in-place install of the room (its window rerun, an "again") would silently drop its slots, floor and points back to the code's defaults. `check_content.py --layout-files` rejects `for_rev` in a `hot_` or `view_` file whose place is not `composed` in the manifest.

### 3.3 What is saved, and what a save can hold

| new store variable | default | holds |
|---|---|---|
| `hint_seen` | `set()` | hint ids already shown (strings) |
| `persistent.show_names` | `False` | the "Show names" setting (persistent, not saved; a `prefixes.json` exception, as `persistent.motion` is) |

Nothing else. Written into existing saved variables in their existing shapes: `actions_today` gains the strings `"bath"` and `"cards_inv:<who>"` (reset each day); `schedule_overrides` gains invite pins (the shape story pins already use); `scene_light` may hold six values where it held four (the code accepts either, so an old save's four-value tuple still works); the flag `invited_girls_dorm` gets a setter. A new save's slot line is written into the save's own header by a `config.save_json_callbacks` entry, not into the store.

- **No migration. `SAVE_VERSION` stays 1.**
- A save may now hold `here` equal to a new key. A key that reaches a save is never removed (if one ever were, `_migrate_15` already sends such a save to the Courtyard, and its `sb_do_path_` label must stay).
- Nothing is added to what `lit_sprite` builds (K9).
- A sprite on screen in an old save is saved by image name, so Mom shows as the new sprite after loading once her files exist.

---

## 4. The places and the map

### 4.1 The new places (eleven; 24 becomes 35)

The owner's four (the lounge, the teachers' dormitory, the recovery rooms as a Bathhouse with a Sauna, the pool) and the dormitory the owner asked for as seven places (a corridor, my room re-hung, five friends' rooms). Considered and not added: a main hall interior, a lake, a kitchen, the basement, Yaga's workshop, an armory room, a staff corridor (section 11).

| key | name | area · opens off | indoor | what it is | what there is to do | door (`place_access`) |
|---|---|---|---|---|---|---|
| `boys_dorm` | Boys' Dormitory | dorms · the garden | yes | the first-year corridor upstairs in the house on the west side of the garden: a shoe rack at the head of the stairs, sliding doors on both sides, a window seat, and one door at the far end (mine) | exits; looks: the shoe rack, the notice board | always open |
| `yuji_room` | Yuji's Room | dorms · `boys_dorm` | yes | film posters, a floor cushion, a small television; the window faces the garden | talk; "Study together"; look: the film shelf | open while Yuji is in it, or walking with me; else "Nobody's in.", tag "Out" |
| `megumi_room` | Megumi's Room | dorms · `boys_dorm` | yes | spare and tidy, a full bookshelf, shoes in a line | talk; "Study together"; look: the bookshelf | the same, for Megumi |
| `senpai_room` | Panda and Toge's Room | dorms · `boys_dorm` | yes | the big corner room: one very large futon, one neat one, a shogi board between them | talk; look: the shogi board | open while Panda or Toge is in it |
| `nobara_room` | Nobara's Room | dorms · `girls_dorm` | yes | a dressing mirror, shopping bags in a row, a tool roll on the desk | talk; "Study together"; look: the mirror | open while Nobara is in it; the corridor's own after-dark rule comes first |
| `maki_room` | Maki's Room | dorms · `girls_dorm` | yes | bare, a weapon case, a pull-up bar in the door frame | talk; look: the weapon case | open while Maki is in it; the corridor's rule first |
| `teachers_lounge` | Teachers' Lounge | staff · the steps | yes | the ground floor of the teachers' house: sofas round a low table, a kitchenette, a television, the staff rota on the wall, stairs up | talk to teachers off duty; look: **the rota** (it says where each teacher is this hour and whether Gojo is in today); look: the kettle | always open |
| `teachers_dorm` | Teachers' Dormitory | staff · `teachers_lounge` | yes | upstairs: a sitting room round a sunken hearth, Yaga's workbench under the end window, four sliding doors with name plates | talk; looks: the workbench, the name plates (a line each, by who is home) | always open; the bedrooms are doors, never places |
| `bathhouse` | Bathhouse | mountain · the Mountain Path | yes | the rest hall of a timber bathhouse at the edge of the trees: benches, a fan, a fridge of cold milk, a cedar door to the sauna, and through open screens the stone hot spring, steaming and empty, with the forest behind it | **Soak** (4.7); look: the milk fridge; talk | always open (the soak itself is closed at Night) |
| `sauna` | Sauna | mountain · `bathhouse` | yes | a cedar box, a stove, a bucket and a bench; no window | **Sit it out** (4.7) | always open |
| `pool` | Swimming Pool | grounds · the Training Yard | no | an open-air 25 m pool on a timber deck behind the dojo, a changing hut, the mountains beyond | **Swim** (4.7); "Swim together" (`swim_pool`, 4.7); look: the lane board | closed at Night: "The gate's chained after dark.", tag "Night" |

**Nobody is ever drawn in the bath.** The Bathhouse's picture is its rest hall. A soak or a sauna is told in the first person over the room's own picture with no sprite shown; people who are there stand in the rest hall in uniform.

**What each needs painted** (5.13 has the batches). Until a picture exists the place shows its stand-in (K12), defined with `bg_placeholder` so the real file replaces it at the next launch with no script change; while `config.developer` is on, a small "stand-in" tag sits in the corner.

| place | day | after dark | foreground | stand-in until then |
|---|---|---|---|---|
| `boys_dorm` | yes (two versions) | night (also shown, warmed, in the Evening) | – | the girls' corridor, mirrored, cool grey |
| `yuji_room`, `megumi_room`, `senpai_room` | yes | night each | – | My Room mirrored, in three tints (warm, blue, green) |
| `nobara_room`, `maki_room` | yes | night each | – | My Room, rose and slate |
| `teachers_lounge` | yes (two versions) | night | the sofa's back | the Common Room, violet-grey |
| `teachers_dorm` | yes | night | – | the Principal's Office cropped, warm |
| `bathhouse` | yes (two versions) | night | – | the infirmary, pale teal |
| `sauna` | yes (no window: one picture and a light row for every hour) | – | – | the storehouse, amber |
| `pool` | yes (two versions) | evening (Night is closed) | – | the riverside cropped to the water, cyan |

Eleven day pictures and ten hour pictures.

**Which friends' rooms are built is the owner's ruling 2, asked before U0b starts,** so a room the owner does not want never gets a key. After wave 0 a key has reached saves and can never be removed (3.3), so:

- **A room dropped later** (by the owner, or by the art cut line of 10.6) becomes a shut door, not a missing place. Its `LOCATIONS` row, its `sb_do_path_` label and its exit row stay (so `path_validate` still finds it and a save standing in it still loads and can walk out); `place_access` returns a fixed line for it ("Her door's shut.", tag "Closed"); its owner's schedule cells go back to the corridor (the girls') or to where they were before; its `WORLD_HOMES` row points at the corridor; no picture is bought and its stand-in stays. One small commit in `sb_world.rpy`, with `u2_world`'s Night column updated in the same commit.
- **A room added later** ("someone else") is a new appended key, label and exit: a change to the frozen contracts, done as its own small package after the wave that is running, never inside one.

### 4.2 Doors, homes and "at home"

- A friend's room is refused by `place_access` unless one of its owners is in it now (`char_location`, which does not call `place_access`, so there is no loop) or is the companion walking with me. The door says who is out and where they are ("Nobody's in. Megumi's in the forest about now."). **Once inside I am never locked in.** The protected `label path_walk` refuses a locked destination (`room_paths.rpy:420-424`), and a room's only exit is its house, so `place_access` starts with one clause: **a house is always enterable from one of its own rooms** (`if world_inside(store.here) == loc: return True, "", ""`, before the girls' corridor's after-dark clause). Without it, walking into Nobara's room on a weekend Morning and waiting until Evening would leave the only exit locked. "Go to bed" teleports as before.
- **A room inside a house asks its house first.** `place_access("nobara_room")` applies the girls' corridor's rule before its own, because the journal's "Go there" walks straight to a place after `can_enter` (`sb_rules.rpy:68-78`) and must not step round the corridor.
- **The girls' corridor after dark:** `place_access` lets me in with the flag `invited_girls_dorm` **or** Bond 30 with Nobara or Maki. `world_welcome_check()` sets the flag the first morning that is true, with one toast: "Nobara: 'You can come up, you know. Knock first.'" The lock's own sentence does not change, and the harness line that sets the flag still passes.
- **Someone at home is no longer "nowhere".** `person_now` keeps its six keys. When the person is in a place I cannot enter and that place is their `WORLD_HOMES` place or the house it is inside, `name` reads "In the Girls' Dormitory" (the house's name) where today it reads "Somewhere I can't go right now"; `hidden` stays True and `place` stays None, so no caller can walk there. `map_pin_people` and `map_area_people` return such people, and the pin draws their faces at half strength with a small door mark (`at_home`), where today it shows a lock and nobody.
- **A house's pin and its exit carry everyone inside it.** `map_pin_people("boys_dorm")` includes the people in the rooms `WORLD_INSIDE` hangs off it (my room keeps its own pin and its own count), and the exit tile to a house shows up to three faces of who is home, so "who is in" is visible from the garden.
- **Gojo** is off campus at Night whatever his daily draw says: one rule in `char_location`, read before story pins, so the Gojo night's pin to the ridge still wins.

### 4.3 Who is where, and when

Cells that change; everything else in `SCHEDULE` and `WEEKEND` stays.

| who | weekday | weekend |
|---|---|---|
| Yuji | Night: garden → `yuji_room` | Afternoon: riverside → `pool`; Night (new cell): `dorm_yard`, by the pond |
| Megumi | Night: off campus → `megumi_room` | – |
| Nobara | Night: `girls_dorm` → `nobara_room` | Morning: `girls_dorm` → `nobara_room`; Afternoon: riverside → `pool`; Evening: courtyard → `bathhouse` |
| Maki | Night: `girls_dorm` → `maki_room` | Night (new cell): `bathhouse` |
| Panda | Night: garden → `senpai_room` | Afternoon: riverside → `pool` |
| Toge | Night: off campus → `senpai_room` | – |
| Shoko | – | – |
| Yaga | Night: off campus → `teachers_dorm` | Morning: `teachers_dorm` (at the workbench); Noon and Evening: `teachers_lounge`; Afternoon stays off campus |
| Utahime | Night: off campus → `teachers_dorm` | Afternoon: off campus → `teachers_lounge`; Evening: courtyard → `bathhouse` |
| Ijichi | Evening: off campus → `teachers_lounge`; Night: → `teachers_dorm` | the same |
| Gojo | never on campus at Night (D9) | the same |

**The whole Night column**

| who | weekday Night | weekend Night | can I reach them? |
|---|---|---|---|
| Yuji | his room | the garden, by the pond | yes |
| Megumi | his room | his room | yes |
| Nobara | her room | her room | once welcome (Bond 30 with her or Maki); until then the map and journal say she is at home |
| Maki | her room | the Bathhouse, on the bench | weekdays once welcome; weekends always |
| Panda, Toge | the shared room | the shared room | yes |
| Shoko | the infirmary | the infirmary | yes |
| Yaga, Utahime, Ijichi | the Teachers' Dormitory | the Teachers' Dormitory | yes |
| Gojo | off campus | off campus (the ridge on his own night) | only on his night |

On a weekday Night eight people can be talked to before any welcome (three today: Yuji, Panda, Shoko), ten after it.

Consequences, each checked against the code:

- The Common Room is still empty at Night by routine on all seven days (`wp1_world.rpy:329-334`, unedited).
- The weekend river holds two (Maki, Toge) and the pool three, so only the cafeteria at noon still holds five; the line in `wp1_world.rpy:335` that names the riverside is updated in the same commit by the package that owns the schedule.
- "Nobody who moved lost an activity" (`p2_paths.rpy:996-1002`) asks whether the activity is still offered anywhere in the person's week. Yuji, Nobara and Panda still stand in the Courtyard, a walk place; and for the three who left the weekend river, "Swim together" is still offered, as `swim_pool` at the pool. The check is told that `swim_pool` continues `swim` (one mapping, a ledger line, 10.3); no list of exceptions is written. The new people are added to its `_zz_moved` list: in wave 0 everyone but the three who left the river, and those three in wave 1, in the commit that brings `swim_pool` (until then the pool, like every new place, offers nothing to do).
- No written scene is tied to a person and a place (`p2_paths.rpy:987`), so no scene breaks. The four "stay the night" scenes still play wherever I stand; setting them in the new rooms is the story phase's.
- Utahime and Yaga keep their office hours, so the board's host and the missions' `where="office"` are untouched. Ijichi keeps the gate from Morning to Afternoon (`trip_ok_now`).
- The Courtyard on a weekday afternoon is still Yuji and Nobara (`p2_paths.rpy:1028`).
- The Daytime and Evening moves in the table (the pool on weekend Afternoons, the baths on weekend Evenings, the lounge off duty, Yaga on campus at weekends, Nobara's weekend Morning in her room) were not asked for by the owner; they are what gives the new places people. They are listed in section 0 under "Chosen for you" and each is one table cell.
- At Night every timed activity is closed by the night rule, so a Night move removes nothing; "Sit out with them" is in `NIGHT_OK` and gains the garden, so Yuji by the pond on a weekend Night offers it.

### 4.4 My room moves into the Boys' Dormitory, case by case

The house rule, added to `path_validate` (`room_paths.rpy:349-364`): a place in `WORLD_INSIDE` must have its house as its **first** exit and is left out of its yard's "must lead to every room" list; a house must be a room of the same area whose own first exit is the yard; a house may lead to the places inside it. `path_hub`, `path_exits`, `path_neighbours` and `path_register` do not change. Every place still belongs to exactly one area, so `area_of("dorm")` is still `"dorms"`.

| step | what | file |
|---|---|---|
| 1 | `WORLD_INSIDE["dorm"] = "boys_dorm"`; `dorm` stays in `AREAS["dorms"]["places"]` and keeps its pin | `sb_world.rpy` |
| 2 | `PATH_EXITS["dorm"] = [("boys_dorm", 150, 760)]` (the same point: it is my door, and my room is redone in place); in `PATH_EXITS["dorm_yard"]` the row `("dorm", 248, 728)` becomes `("boys_dorm", 248, 728)` (the same point: the left house's veranda steps) | `room_paths.rpy` |
| 3 | `label sb_do_path_boys_dorm` and the three rooms' labels appended. **`label sb_do_path_dorm` (now used from the corridor) and `label sb_do_path_dorm_yard` are not touched.** | `room_paths.rpy` |
| 4 | `screen map_area` skips places in `WORLD_PINLESS`; `_validate_world` and `map_validate` accept a missing spot for those keys only | `ui_map.rpy`, `sb_world.rpy` |
| 5 | The walk-home line for the area already reads "The dormitory is a row of closed doors and one that isn't. Mine." No new line is needed. | – |

Nothing else changes, because everything that means "home" says `"dorm"` by name and **teleports**: `night_carry_home`, `sb_do_night_bed`, the Gojo night, the night out, the Sun Mall's end (`events_arc1.rpy:1056`), `default here = "dorm"`, Sleep and Study in `place_actions`, the computer and the bed. The walk home never walks exits, so a lock or a moved door cannot strand me.

| a save made… | after the move |
|---|---|
| standing in my room (`sb_loop.rpy:37`, `here == "dorm"`) | loads on the same statement; the room shows one exit, "To the Boys' Dormitory", at the same point. Nothing a save holds names an exit. |
| on the map with `here == "dorm"` (the owner's auto-1, `sb_loop.rpy:72`) | loads on level 1 (the open area is a screen variable); "I'M HERE" is on Dormitories, as before; `row_dorm` is still there |
| in the garden | loads the same; the garden's exits are rebuilt from the table; the left house's exit reads "To the Boys' Dormitory" |
| with a rollback log that walked my room → garden by the old exit | rollback restores `here`; the return sites are in `sb_do_path_dorm_yard` and `path_walk`, which still exist, textually identical |
| parked on `sb_do_path_dorm`'s return (walked into my room a moment before the save) | the label and its `call path_walk("dorm")` are untouched; loads the same |
| on a night menu (the owner's auto-3), or anywhere a night ends | unaffected: those paths set `here = "dorm"` by name |
| in the prologue (eight of the owner's saves; default `here == "dorm"`) | unaffected. `arc_one_open` then says "I go out into the courtyard", a narrated walk, still true |
| a new game | wakes in `dorm` as before |

Three ways home, each tested by name in `u2_home.rpy`: "Go to bed" from anywhere (a teleport, unchanged); the map (Dormitories, then my room's pin: two clicks, as before); on foot (garden, corridor, the door at the end: one click more than today, which is what the owner asked for).

### 4.5 Exits

Every row has its way back. Points on a picture that is composed again, and on every new place, are schematic in code and live in `hot_<place>.json` once the picture exists (K2).

| from | exits, in order |
|---|---|
| `dorm_yard` | `boys_dorm` (replaces `dorm`), `dorm_common`, `girls_dorm`, `rooftop`, `courtyard`, `staff_yard`, `trailhead`: **still 7** |
| `boys_dorm` | `dorm_yard` (the stairs), `dorm` (the door at the end), `yuji_room`, `megumi_room`, `senpai_room` |
| `dorm` | `boys_dorm`, at (150, 760): my door |
| `yuji_room`, `megumi_room`, `senpai_room` | `boys_dorm` |
| `girls_dorm` | `dorm_yard`, `nobara_room` (the near left door, about (470, 600)), `maki_room` (the near right door, about (1475, 600)); both doors are already painted and the corridor is redone in place, so these two points are measured once, on today's picture |
| `nobara_room`, `maki_room` | `girls_dorm` |
| `staff_yard` | `office`, `utahime_office`, `gojo_office`, `teachers_lounge`, `dorm_yard`, `training_yard`: 6 |
| `teachers_lounge` | `staff_yard`, `teachers_dorm` (the stairs) |
| `teachers_dorm` | `teachers_lounge` |
| `training_yard` | `training`, `dojo`, `storehouse`, `pool`, `courtyard`, `staff_yard`: 6 |
| `pool` | `training_yard` |
| `trailhead` | `forest`, `ridge`, `riverside`, `bathhouse`, `dorm_yard`: 5 |
| `bathhouse` | `trailhead`, `sauna` |
| `sauna` | `bathhouse` |

70 exits in all (48 today), 33 of them from the six yards (30 today). Eleven labels are appended; all 24 old ones stay. `PATH_LINKS` keeps today's six: there is still no path from the Courtyard to the staff steps (the plan has none; AUDIT M5 stays as it is, now for a reason the plan shows).

### 4.6 The icon column: how each yard keeps to one column

`p2_paths.rpy:739-740` wants at most eight tiles in the column with four people in the place. An exit, or an action on an object, drops into the column whenever a person's rectangle covers its square, and that rectangle is the whole sprite canvas (about 395 by 728 px), so four people can cover most of the lower picture. Hold the hour and Wait are always two tiles. So:

| yard | things that can drop into the column | at least this many must stay clear of a four-person row |
|---|---|---|
| Dormitory Garden | 7 exits | 1 |
| Training Yard | 6 exits and Train at the posts | 1 |
| Staff Building Steps | 6 exits | 0 |
| School Courtyard, Mountain Path | 5 exits | 0 |
| Courtyard | 4 exits, Practice; the vending machine is never hidden | 0 |

The rule for a layout sitting: in each yard the four-person row stands on the near ground and at least the number above of exits sit where no person's rectangle reaches (above the heads, as the garden's tower exit does today, or outside the row's left and right ends). `tools/check_layout.py` counts it from the sidecars before a yard is installed; the unedited harness line counts it again in the game. With a companion a second column is allowed, as today. **If the Training Yard cannot pass, "Train at the posts" becomes a look and training stays in the hall;** nothing else depends on it.

### 4.7 Small actions and lines this adds (the full list)

| id | where | cost | what it does | words |
|---|---|---|---|---|
| `bath_soak` | Bathhouse (the open screens to the spring) | 1 period; one bath a day (the key `"bath"` in `actions_today`, shared with the sauna) | stamina to full; three or four first-person lines; if someone is in the rest hall, a line with them | "Soak" |
| `bath_sauna` | Sauna (the bench) | 1 period; the same one bath a day | cursed energy to full; lines | "Sit it out" |
| `pool_swim` | Swimming Pool (the water) | 1 period | exactly `sb_do_swim`'s numbers (Output +2, stamina −12, cursed energy +12, its Bond with one person who is there) over the pool's picture; its own label because `sb_do_swim` shows the river by name | "Swim" |
| `swim_pool` (an activity, with a person) | Swimming Pool | as `swim`: 1 period, Bond 35, Noon and Afternoon | exactly `act_swim`'s Bond and numbers, in its own scene `label act_swim_pool(who)` on `bg pool` with its own four or five lines (the deck, the lanes, the changing hut; no rocks, no far bank). Its own activity because `act_swim` runs `scene bg riverside` and speaks of the river's stones (`events_activities.rpy:102-103`), in a frozen file. `swim` itself stays at the riverside and is not edited | "Swim together" |
| `train` (existing) | Training Yard (the striking posts) | 1 period | the existing `sb_do_train`, its general branch | "Train" |
| `cards_invite` | Common Room (beside the card table) | free | 7.4 | "Ask someone to the table" |
| existing activities | new places | – | 3.1's `ACTIVITIES` row | – |
| looks | 7.3 | free | three or four first-person lines each, turning by day | – |
| captions | every (who, place) cell | – | 7.1 | – |
| lock lines, the welcome toast, six hints | – | – | 4.1, 4.2, 7.5 | – |

Under the night rule the baths and both pool swims cost time and are not in `NIGHT_OK`, so they are closed at Night as everything else that takes an hour is. On a rest day (the day after a Gojo night) `pool_swim` and `swim_pool` are closed as `swim` is; the baths are allowed (they are rest, not training). The infirmary's free "Get patched up" is unchanged. No stat, price or reward that exists today changes.

### 4.8 The map, laid out again

- **Level 1: six markers at today's anchors.** The picture becomes a painted bird's-eye view composed *to* those anchors (5.9), so `wp1_world.rpy:241-243` (order, seals, anchors) is untouched. `game/layout/map_campus.json` may nudge an anchor and holds the Mountain marker's box, measured on the painted peak; `map_validate` reads the box from it and falls back to today's constant.
- **Level 2.** A place in `WORLD_PINLESS` has no pin; its house's pin shows its people. Target points the area-map prompts ask for (the final points are measured on each approved picture and written to `area_<key>.json`). The table is printed by `campus_plan.py --pins` from `campus.json`, not kept by hand, so it cannot disagree with the plan of 5.2; `check_campus.py` is run on these targets before the drawing goes to the owner:

| area | pins |
|---|---|
| Courtyard & Gate (2) | `courtyard` (960, 470), `gate` (960, 830) |
| School Building (5) | `school_yard` (900, 600), `classroom` (1380, 520), `library` (820, 300), `infirmary` (400, 560), `cafeteria` (800, 860) |
| Dormitories (6) | `dorm_yard` (960, 700), `boys_dorm` (480, 560), `dorm` (430, 330; my window at the end of the boys' house), `dorm_common` (960, 480), `rooftop` (1010, 250), `girls_dorm` (1440, 520) |
| Staff Building (5) | `staff_yard` (900, 760), `office` (900, 380), `gojo_office` (420, 600), `utahime_office` (1300, 620), `teachers_lounge` (1560, 340) |
| Training Grounds (5) | `training_yard` (900, 640), `training` (420, 520), `storehouse` (1000, 300), `dojo` (1400, 560), `pool` (1480, 850) |
| The Mountain (5) | `trailhead` (700, 860), `forest` (360, 640), `ridge` (960, 250), `bathhouse` (1080, 640), `riverside` (1500, 560) |

- **Getting to a friend's room:** two clicks to the house on the map and one on the door; or one click on "Go there" on their journal page.
- **Icons: 88 become 114,** final in the scaffold; until the sheet is cut each shows its kanji stand-in and its word, as in phase 2. The 26: eleven places (`place_<key>`); five yards (`place_school_yard`, `place_dorm_yard`, `place_staff_yard`, `place_training_yard`, `place_trailhead`), so an exit to a yard and the area's marker stop looking the same (AUDIT M6); four actions (`bath_soak`, `bath_sauna`, `pool_swim`, `cards_invite`); the three the quick menu lacks (History, Auto, Save by today's table; U0b confirms which); `help`, `continue`, `at_home`. All 26 go on a new sheet 4 (30 cells, four left empty); sheet 3 and its 28 finished icons are not rendered again (`make_icon_workflow.py`: `SHEETS = 4`).
- **The maps follow the hour:** the grade the outdoor places take, at half strength (AUDIT T10). Free.
- **Tokyo:** the fifteen dead "Later build" pins are hidden from players (shown while `config.developer` is on); the district markers take the campus markers' size and the unused district icon (AUDIT M1, M3).
- **An area marker with nobody in it** is drawn at half height (AUDIT M6).
- `tools/genworld.py` and `LOCATIONS[*]["x"/"y"]` become dead data and are left alone.

---

## 5. The pictures

### 5.1 The settled look: one paragraph, in every prompt

`tools/bgs/look.txt`, read by every maker (redo, new composition, relight, pose room, map). It is `LOOK3` from `tools/make_look_workflow.py`, the wording the third test proved, with these small changes: "the room" becomes "the place" and "the floor" becomes "the floor or the ground"; "daylight" becomes "light" (the hour comes from its own sentence); its last window clause ("of trees, tiled roofs and sky") is dropped, because what a window shows now comes from the campus bible, room by room; and "water marks" becomes "damp patches" (the project's record: the service once blocked a room clean-up as watermark removal when "remove" met "water mark", and one blocked box aborts the whole run; `KEEP` says "Do not remove" in every in-place prompt). Batch 1 is the test of these words before they are frozen.

> THE LOOK: a real place you could walk into, drawn as a clean modern anime background. Believable materials (wood grain, glass with soft reflections, stone, plaster, fabric), physically believable light with soft shadows and bounced light, real depth. Clean and well kept: walls are fresh and even, with no stains, cracks, peeling, damp patches or dirt, and there is no dust, litter or fallen leaves on the floor or the ground; everything that belongs to the place is still there. Crisp precise edges, clean clear colour, no film grain, no noise, no canvas texture, no visible brush strokes, no haze or glow washing out detail. Through every window a clear, in-focus view. No people, no animals, no text, no logos. Output a 16:9 picture.

Rules round it:

- **A redo in place puts the keep text in front.** It is `KEEP` from the same file, split into data files the maker reads, because `KEEP` as tested is wording for an indoor room by day and ends "Keep the time of day and the direction of the light", which a relight must not say:
  - `keep.txt`: `KEEP` word for word, less its last sentence (keep the camera, every wall and object, "every object that is in the picture now, however small, each in its place: the books and boxes on the shelves ... Do not remove, tidy away or add anything."). Indoor places.
  - `keep_outdoor.txt`: the same sentences with outdoor nouns ("every building, roof, wall, path, step, rock and tree exactly where it is"; "the lanterns, the benches, the posts, the signs") in place of the furniture and the shelf list. The gate, the forest, the riverside, the ridge, the rooftop and every outdoor relight. **Untried; batch 8a is its test.**
  - `keep_light.txt`: "Keep the time of day and the direction of the light." Added after the keep text for a **day** redo only; a relight leaves it out and says its hour instead.
  - **A named addition** (the laptop, Yaga's desk and photograph, the veil) replaces the keep text's last sentence with "Do not remove or tidy away anything, and add nothing except this:" followed by the room's `allow` line. **Untried; batch 1a (the laptop) is its test.**
  - The keep lists of 5.4 are installer data for the "nothing vanished" check; they add no words to the prompt.
  - A variant refused twice at its test is not bought again: the old picture (or the old hour picture, or the room without its addition) stays, and the owner is told what and why.
- **Never "nothing on the floor", "empty", "tidy away the", or a list of things to take off a seat or a table.** The second test's "nothing scattered on them" emptied the Common Room.
- **What a window shows is one more sentence, written by the tool from the bible** ("Through the windows: the garden pond and the tower's foot"), never invented per prompt.
- **A new composition** puts `tools/bgs/stage.txt` in front instead (5.6): what the screen needs from the picture, in a painter's words.
- `tools/check_prompts.py` fails any assembled prompt that contains: worn, old, weathered, aged, moss, mossy, lived-in, dusty, scattered, "nothing on", "leaves on", jacket, umbrella, haze (outside the look's own "no haze"), bloom, painterly, brushwork, "soft painted", "water mark", watermark, a character's or the series' name (the editor is a closed service), a count of objects ("four desks"), or "lantern" unless the bible puts one there. It runs on every prompt before a workflow is written.
- The four phase-1 style files (`style.txt`, `style_interior.txt`, `style_dim.txt`, `style_aerial.txt`), `STYLE.md` and `make_relight_workflow.py` ask for the old look. They get a first line saying which file replaced them, and no maker of this overhaul reads them.
- Every render is 2K (2752×1536, Nano Banana Pro, $0.16). Nothing is enlarged from 1K again. Result files carry a letter for the candidate (`_a_`, `_b_`), never a finish-order number.

### 5.2 The campus bible

Made by U0d before any outdoor picture, approved by the owner at checkpoint A (K4):

- `tools/bgs/campus.json`: the table below, the paths, each yard's camera and what stands on each side of it, and what each room's windows look onto. **It is the only place an outdoor fact is written.**
- `tools/campus_plan.py` draws it: `tools/bgs/campus_plan.png` (labelled, for the owner and reviewers), `campus_plan_ref.png` (colour blocks, no words, with a camera arrow per yard; handed to the editor as a layout reference) and one crop per area. It also writes `tools/bgs/CAMPUS2.md` from the same data, so the prose can never disagree with the table; `CAMPUS.md` gets a first line pointing at it.
- `tools/make_scene_workflow.py` builds every outdoor and map prompt from the table. No outdoor prompt is written by hand.
- `tools/check_campus.py` (plain Python, part of every package's acceptance once it lands) is the automatic test of "the map flows": every place has a building and every building a look line; every `PATH_LINKS` pair is a path on the plan, and nothing else is; for each yard, each exit's point (code default or sidecar) lies in the third of the screen its side of the table names, and exits to two buildings keep the table's left-to-right order (two exits within 60 px of each other across are not ordered); a place the table puts **behind the camera** has its exit in the bottom band of the picture; on each area picture the pins keep the plan's relations (if building A is west of B on the plan, A's pin is left of B's, and north is higher; a tolerance of 60 px), and the same for the six markers on the campus map; and every building a room's window line names lies in the half of the plan that wall faces.

  **What counts as a failure, and when.** Today's pictures disagree with the plan on purpose (the Training Yard's hall and dojo are on the other sides, `room_paths.rpy:128-130`; the two offices are swapped on the Staff map, `sb_world.rpy:139-140`), and U0c leaves the old yards' code points on today's sides. So: the plan itself, 4.8's target pins and every test sidecar are checked in full, always; a yard or map whose picture is still at **revision 1** is reported as "waits for batch N" and is not a failure; from **revision 2** every side, order and pin relation is a hard failure. The tool has one negative test: a composed test sidecar with two exits swapped must fail.

**The plan** (top-down, north and uphill at the top, on a 1920×1080 sheet, drawn so that each quarter sits where its map marker already is). The look line is repeated word for word in every prompt that shows the building.

| building or ground | holds | at (x, y) | its look, the same in every picture that shows it |
|---|---|---|---|
| Main Gate | `gate` | (960, 985) | a stone torii across a flagstone footpath between cedars and stone lanterns (there is no road) |
| Courtyard | `courtyard` | (960, 800) | a wide flagstone court |
| Gateway | the way to the dormitories | (960, 690) | a roofed timber gate with a grey tiled roof, a stone lantern either side; behind it a flight of stone steps uphill |
| Pagoda | landmark | (840, 640) | five storeys, behind the schoolhouse's north end |
| School Building | `classroom` | (720, 760), long, north to south | a two-storey schoolhouse of warm brown timber boarding, two rows of large white-framed windows, a covered entrance porch with shoe lockers (read off the chosen Courtyard) |
| School Courtyard | `school_yard` | (470, 770) | packed earth, one pine with a bench under it |
| Library | `library` | (430, 640) | white plaster and timber, tall gridded windows |
| Infirmary | `infirmary` | (250, 760) | a small white annex with a pale green door and a ramp, at the forest edge |
| Cafeteria | `cafeteria` | (430, 890) | a low wide hall with a grey tiled roof, a wall of glass sliding doors, a metal kitchen chimney, benches outside |
| Training Hall | `training` | (1200, 760), long, north to south | a broad brown-timber hall with a deep roofed veranda and paper-screened sliding doors; a weapon rack on the veranda and straw posts by the steps; the vending machine at the court end of the veranda (read off the chosen Courtyard) |
| Training Yard | `training_yard` | (1470, 780) | bare earth, a row of striking posts |
| Storehouse | `storehouse` | (1480, 640) | a white *kura* with a black tiled roof and one heavy door |
| Dojo | `dojo` | (1720, 760) | a long low hall with one unbroken band of windows |
| Swimming Pool | `pool` | (1740, 900) | an open-air pool on a timber deck behind a low wooden fence, a small changing hut |
| Dormitory Garden | `dorm_yard` | (960, 540) | a stone path through a kept garden, a pond with two stone lanterns |
| Boys' Dormitory | `boys_dorm`, `dorm`, `yuji_room`, `megumi_room`, `senpai_room` | (720, 480) | two storeys of dark timber, an upstairs gallery, an outside stair, a plain blue door curtain |
| Common Room | `dorm_common` | (960, 470) | one storey, glass doors the whole width, a deck over the pond |
| Tower | `rooftop` | (960, 380) | the tall wooden tower with an open top veranda |
| Girls' Dormitory | `girls_dorm`, `nobara_room`, `maki_room` | (1200, 480) | two storeys of white plaster and timber, latticed windows, a plain red door curtain, flower boxes |
| Staff Building Steps | `staff_yard` | (1560, 520) | wide stone steps, gravel either side |
| Principal's Hall | `office` | (1560, 400) | the largest roof, on a stone platform, heavy closed doors, no windows |
| Gojo's Office | `gojo_office` | (1400, 470) | a small detached house with one very large window |
| Utahime's Office | `utahime_office` | (1690, 480) | a neat small pavilion, a round window, paper screens |
| Teachers' House | `teachers_lounge`, `teachers_dorm` | (1790, 400) | a two-storey house with a veranda all round, warm windows, a bamboo fence |
| Mountain Path | `trailhead` | (900, 300) | where the stone gives out: a standing stone and a low gate |
| Bathhouse | `bathhouse`, `sauna` | (1160, 240) | a tall tiled roof with a steam vent, a stone basin by the door, steam above the fence |
| Forest Trail | `forest` | (330, 230) | old cedars, nothing built |
| Riverside | `riverside` | (1380, 170) | a clear river, a pebble bank, a deep pool |
| Mountain Ridge | `ridge` | (950, 110), straight up the stone stairs from the Mountain Path | grass and rock above the trees; the veil high on the slope beyond |

Paths (`PATH_LINKS`, unchanged): Courtyard to the School Courtyard through the passage by the schoolhouse's porch; to the garden up the gateway steps; to the Training Yard by the training hall's veranda steps; garden to the staff steps east along stepping stones; garden to the Mountain Path north, behind the Boys' Dormitory; staff steps to the Training Yard south, down a walled path.

**What I see in each yard** (the camera, and what each exit sits on; this also settles AUDIT N14, where the map and the steps disagreed about the two offices: Gojo's is on the left and Utahime's on the right, on the steps and on the Staff map alike):

| yard | I stand at, facing | left | ahead | right | bottom of the frame |
|---|---|---|---|---|---|
| Courtyard (as chosen) | (960, 870), north | the School Building; exit on its porch → School Courtyard | the gateway and its steps → Dormitory Garden; pagoda behind | the Training Hall; exit on its veranda steps → Training Yard; the vending machine | the flagstones → Main Gate |
| School Courtyard | (470, 840), north | the Infirmary at the forest edge | the Library, the pine and its bench in front | the schoolhouse's west wall and its side porch → Classroom | bottom left the path to the Cafeteria's glass doors → Cafeteria (it is behind me); bottom right the passage by the schoolhouse → Courtyard |
| Dormitory Garden | (960, 610), north | the Boys' Dormitory; behind it the dirt path → Mountain Path | the Common Room, the tower above it → Rooftop | the pond, then the Girls' Dormitory | the steps → Courtyard (left); stepping stones → Staff Building Steps (right) |
| Staff Building Steps | (1560, 610), north | Gojo's Office; bottom left the path → Dormitory Garden | the Principal's Hall on its steps | Utahime's Office; behind it the Teachers' House → Teachers' Lounge | the walled path down → Training Yard |
| Training Yard | (1470, 890), north | the Training Hall's yard doors; bottom left the passage → Courtyard | the posts, the *kura*; right of it the walled path and its steps → Staff Building Steps | the Dojo; at the edge the pool's gate → Swimming Pool | – |
| Mountain Path | (900, 340), north | the path → Forest Trail | the stone stairs → Mountain Ridge | the Bathhouse in the middle distance; at the edge the path down → Riverside | the slabs → Dormitory Garden |

The garden, the staff steps and the Mountain Path keep today's camera and today's sides; the Training Yard's sides swap (the hall must be on the Courtyard's side) and the School Courtyard is laid out afresh. On the Mountain Path the order from left to right is the Forest Trail, the Ridge's stairs, the Bathhouse, the Riverside, on the plan, in the picture (today's exits already are: 180, 862, 1640 across) and on the Mountain map alike.

**Behind the camera means the bottom of the picture.** A place the camera has its back to (the Cafeteria from the School Courtyard; the door I came in by, in a room that shows no door) has its exit in the bottom band, the lowest row the lanes allow, as the yards' ways back already are. It is a stated rule of the plan, `check_layout.py` and `check_campus.py` know it, and it is what "an exit sits on the thing it leads to" means when the thing cannot be in the picture.

**What the windows show** is a line per window wall in the plan, each with the way that wall faces, so the tool can check it (a building named in a line must lie on that side of the room on the plan). Common Room (I stand in the glass doors on the deck, the pond behind me, looking north; read off the installed picture): the back window shows the tower's foot and cedars, the left window the Boys' Dormitory's dark timber and gallery; the pond is not in this view. Cafeteria: the School Courtyard and the pine. Library: the Cafeteria's grey tiled roof and treetops (which is what the chosen picture already shows). Classroom: the School Courtyard below, the Library's roof, cedars. Infirmary: cedar trunks at the forest edge. My Room: the mountain slope and the ridge, no building. Yuji's Room: the garden and the pond. Megumi's Room: the forest. Panda and Toge's Room: the tower. Girls' corridor (the end window) and both girls' rooms: the garden and the Common Room's roof. Lounge: the staff steps. Teachers' Dormitory: a small inner garden. Training Hall (high windows): sky and cedar tops. Dojo: the Training Yard's posts. Bathhouse: the spring and the cedar slope. Utahime's office: her gravel garden. Gojo's office: cedars. The Principal's office, the storehouse and the sauna have no windows. The Rooftop's far view is a redo in place and stays a loose cluster of roofs.

**How a building keeps its look from picture to picture,** in order of trust: (1) the look line above, identical in every prompt; (2) each later picture is given the earlier approved picture of that building as a reference (the editor takes up to fourteen; the installer cuts `tools/bgs/refs/<building>.png` from the first approved picture that shows each); (3) a person looks, with a five-line checklist per picture ("the schoolhouse is on the left: yes / no"). The order of making follows from it: the Courtyard (done) fixes the schoolhouse, the gateway and the training hall; then the five yards; then the six area maps, each given the plan crop and its yard; last the campus map, given the plan and the six area maps. **Whether the editor holds a layout drawing this well is untested; batch 3 is that test,** two yards and one area map, before the other three yards and twelve map renders are bought. The owner is told the result at checkpoint B. What happens if the drawing is not followed is decided here, not on the day:

| step | what | cost |
|---|---|---|
| the pass rule for batch 3 | for each of its three pictures, at least one candidate on which a first-guess layout passes `check_campus.py`'s sides and order, and the five-line checklist is all yes | – |
| if a picture fails | one more pair for it, with words and the approved neighbours' crops only, no plan drawing | $0.32 a picture, at most $0.96 |
| if it fails again: the three yards that keep today's camera (garden, staff steps, Mountain Path) | redone in place with a named addition (the two dormitories told apart; the teachers' house; the Bathhouse), by 5.4's procedure. The laptop in batch 1a will already have shown whether a named addition holds | one render each |
| if it fails again: the School Courtyard and the Training Yard, which cannot be redone in place to match the plan | today's picture is redone in place, and **the bible, the exits and the area map are changed to match the picture** instead (the map then agrees with what is seen, which is what "accurate" asks). For the Training Yard that leaves the hall on the far side from the Courtyard; the owner is shown it at checkpoint B and may ask for the swap to be tried again later. The pool's gate is then a named addition | one render each; the bible is reopened with the owner |
| if the editor will not paint a map from the plan | all six area maps and the campus map fall back to drawn maps in the new palette from `campus_plan.py` | free |

**The editor may change under us.** It is a preview model (`gemini-3-pro-image-preview`) used across twenty-four sittings. At the start of any sitting more than a week after the last, the art-install role runs `test_art_tools.sh`'s real cases and one fixed "canary": a redo of the Common Room from its revision-1 picture with the frozen words ($0.16). If the canary's shift, vanished-object and sharpness figures fall outside the range recorded at batch 1, the sitting stops and the owner is told, before a batch is bought in a look that no longer matches the rooms already made.

### 5.3 The 24 places, picture by picture

| place (file) | how | what sits on it and must still fit | batch |
|---|---|---|---|
| `courtyard` | **composed again: the chosen gateway picture, already made** | 4 exits, the vending machine, "Practice" on the straw posts, a standing row, Yuji's pose, a night picture | 0 |
| `library` | **composed again: the chosen bright room, already made** | 1 exit (the chosen picture shows no door: I stand in it, so the way out sits at the bottom of the picture, by 5.2's rule), 3 hotspots, standing rows, three poses, an evening picture | 0 |
| `dorm_common` | in place, **already made** (third test); run once more for its window line | 1 exit, 2 hotspots and the new looks, standing rows, one polygon in three hours, Nobara's pose | 0, 1 |
| `cafeteria` | in place, **already made** (third test); run once more for its window line | 1 exit, the counter, standing rows, a polygon, Yuji's pose | 0, 1 |
| `school_yard` | composed again (laid out afresh) | 5 exits | 3 |
| `dorm_yard` | composed again (same camera and sides; the two dormitories told apart) | 7 exits | 3 |
| `staff_yard` | composed again (same camera and sides; the teachers' house added) | 6 exits | 4 |
| `training_yard` | composed again (sides swap; the pool's gate added) | 6 exits, the posts | 4 |
| `trailhead` | composed again (same camera; the Bathhouse added). Fallback: in place with one named addition | 5 exits | 4 |
| `dorm` (`your_room.png`) | in place **plus one object**: a closed laptop on the desk, under the computer's icon. If it does not hold after two tries, my room is installed without it and the icon stays where it is | 1 exit, 2 hotspots | 1 |
| `girls_dorm`, `rooftop` | in place | 1 exit each (the corridor gains two, on doors already painted) | 1 |
| `office` | in place **plus two objects**: a low writing desk and a framed photograph on it. If they do not hold after two tries, the office stays as it is and Yaga sews at the low table the picture already has | 1 exit; a polygon for the desk; Yaga's pose | 7 |
| `classroom`, `infirmary`, `training`, `dojo`, `storehouse`, `utahime_office`, `gojo_office` | in place | 1 exit each; 5 hotspots among them; Utahime's polygon and pose | 7 |
| `gate`, `forest`, `riverside` | in place | 1 exit each, 1 hotspot | 8 |
| `ridge` | in place **plus one thing**: the veil, faint, high on the slope above the rope markers, under the look-up icon at (960, 250). If it does not hold after two tries, the ridge is installed without it and `bg ridge_veil` keeps today's picture | 1 exit, 1 hotspot; `bg ridge_veil` is then made from the new ridge by the same edit, stronger, replacing the flat smudge | 8 |

**Seventeen in place** (three of them with a named addition), **seven composed again.** With the six area maps and the campus map, fourteen pictures are composed again, as the brief expected.

`gate.png` is today also the title picture; the title gets its own lookup in the scaffold (D24), so redoing the gate changes only the gate.

### 5.4 Redone in place: the procedure, and the proof that nothing moved

**What the tests proved** (measured on the nine first-test renders and the two third-test renders): fitted the right way, every one of 24 tiles of every picture lines up with the game's picture to 0 px; a picture shifted 12 px or zoomed 2% by hand reads as moved everywhere; and with `KEEP` every object stays.

**The maker: `tools/make_redo_workflow.py`.** Input: the game's own file `game/images/bg/<stem>.png` (never the stale `backgrounds_chosen/` folder). Prompt: the keep text for the place (5.1: indoor or outdoor; `keep_light.txt` for a day redo; the addition sentence where the room has one), then at most two lines from data (the hour, for a relight; "Through the windows: …" from the bible), then `look.txt`. Every workflow uses fixed seeds, so pressing Run again after an error in the same session pays only for the boxes that did not finish. One candidate ($0.16); a second is bought only when the first is refused or the owner says "again". It writes the workflow and a page of numbered steps (`art_<n>.md`) into `~/Desktop/JJK Game images/ui2/`, and refuses a picture whose order is wrong (K8).

**The keep list: `tools/bgs/keep/<stem>.json`,** one per room, written once before the room's batch by the art-install role (about ten minutes a room, looking at the picture with `layout_sheet.py`):

```
{"keep":  [{"name": "the floor cushions by the low table", "box": [1330, 820, 240, 110]}, ...],
 "empty": [{"name": "the sofa seat", "box": [150, 300, 230, 60]}, {"name": "the floor", "poly": [[...]]}],
 "allow": [{"name": "a closed laptop on the desk", "box": [400, 540, 120, 70]}]}
```

Every hotspot's object, every object a caption or a pose names and every foreground object is in `keep` automatically (a 110 px box round each registered point, the bounding box of each foreground polygon); the hand-written rows add what the eye would miss. `empty` is what must not gain anything; `allow` is the named addition or the window.

**The installer: `tools/install_redo.py`** (ComfyUI's Python, through `tools/py_art.sh`).

1. **Fit:** refuse static and letterbox bars; scale the 2752×1536 render to 1920×1072, lay it 4 px down, fill the 4 px above and below with the render's own first and last rows.
2. **Nothing moved.** Edge maps of old and new. The whole-picture shift must be 0 or 1 px. Round every registered point of the place (each exit, each hotspot, the feet of every slot for one to four people, each pose box, a 12 px band along each foreground outline) a 192 px window is checked alone and must agree within 3 px. A moved window refuses the picture and names it: "the door my room's exit sits on moved 9 px left".
3. **Nothing vanished.** For each `keep` box, the edge agreement inside it; below the "gone" threshold the picture is refused: "the floor cushions by the low table are gone".
4. **Nothing was added.** For each `empty` zone, and across the whole floor polygon, the amount of fine edge has not risen above the threshold (this is the number that catches leaves, a cup, a jacket): "something new is on the sofa seat", unless the zone is in `allow`.
5. **Sharper.** Variance of the Laplacian at least **twice** that of **the place's revision-1 picture** passes; between 1.3 and 2 the verdict is LOOK (shown to the owner, not refused); below 1.3 it is refused. (The approved third-test rooms read 3.0 and 7.5 times; the first test's 13 to 19.) The revision-1 picture is taken from git by the manifest's `from_commit`, never from the installed file: batch 1a redoes the Common Room and the Cafeteria from pictures that are already in the look, and against those a good second redo reads about 1.0 times and would be refused. Steps 2 to 4 are measured against the installed picture, which is what must not move.
6. Everything else that changed (a window's view, a tile that is simply different) is shown, not refused: verdict LOOK, with the tiles tinted on the preview.
7. **Preview:** `shots/art/redo_<stem>.jpg`, old beside new with every point and zone drawn on both.
8. **On PASS, or a LOOK the owner accepts:** write `game/images/bg/<stem>.png`, its manifest row, `light_<place>.json` (6.2), recut the room's foregrounds with `make_fg.py` (free), cut the reference crops of 5.2, and copy the approved render to `~/Desktop/JJK Game images/ui2/approved/` (a seed does not reproduce a picture on another day). Nothing else.
9. The old picture is not copied anywhere: it is in git, and the manifest row records the commit, so the proof can be rerun from the repository alone.

The thresholds of steps 3 to 5 are set in U0d against renders whose answers are known: the tool must pass both third-test renders and the first test's A pictures; flag the first test's Common Room B for the jacket and the cup; report the cushions, the manga shelf, the kettle and the bag as gone on the second test's emptied Common Room; and refuse a picture shifted 12 px or enlarged 2% by hand while passing one that is only recoloured. `tools/test_art_tools.sh` runs the synthetic cases anywhere and the real ones when the files are present, and prints which it skipped.

**Verdicts, in the owner's words:** PASS (it is in the game), LOOK (here is what changed; yes or again), REFUSED (what moved, vanished or appeared, and "run it once more").

**What a redo in place costs besides the picture:** no code, no harness line, and no layout number changes at the install (the room's `hot_` and `view_` files carry no `for_rev`, 3.2, so they stay in force). The few exits that sit on no door today are moved once, on today's picture, by U4 (7.3). Its hour pictures, foregrounds and poses follow in order; until each is remade the game shows the fallback of K7. A room refused twice is made as a new composition (5.6) and laid out again.

### 5.5 The record: which picture is at which revision

`game/layout/pictures.json`, written only by the install tools, read at init by `game/art_manifest.rpy`. Not saved. A picture with no row is today's picture (revision 1), and with no rows at all the game behaves exactly as it does today, so the scaffold changes nothing on screen.

```
{"pictures": {
  "courtyard":           {"rev": 2, "kind": "composed", "batch": 0, "render": "look2_courtyard_gateway_00001_.png", "bible": "9f3a…"},
  "dorm_common":         {"rev": 3, "kind": "inplace",  "batch": 1, "from_commit": "…", "shift": [0, 0], "sharp": [91, 180]},
  "dorm_common_evening": {"rev": 2, "kind": "relight",  "of": "dorm_common", "of_rev": 3},
  "fg_dorm_common":      {"of": "dorm_common", "of_rev": 3},
  "pose_dorm_common__nobara__evening": {"of": "dorm_common_evening", "of_rev": 2}
}}
```

- `art_rev(stem)`: the picture's revision (1 when there is no row).
- `art_fresh(stem)`: False when the row names a parent (`of`) whose revision is no longer `of_rev`. A dependant with no row is fresh only while its parent is at revision 1.

K7 in code, four small gates laid by the scaffold: `bg_variant` (a stale hour picture is not used: the day picture is tinted; and in a foreground room an hour picture is not used until its foreground exists); `view_fg_path` (a stale foreground is not used); `view_pose` (a stale pose is not used: the standing sprite); `light_for_place` (a stale light row is not used: the general row). `tools/art_status.py` prints the manifest as a table (what is in the new look, which room sets are half made, which dependant is stale, which pictures a bible change touches); it is the first thing in every checkpoint note.

### 5.6 Composed again: the procedure, and what the re-layout costs

1. **The prompt** comes from the bible, plus `look.txt`, plus `tools/bgs/stage.txt`, the rules every picture people stand in must obey, in a painter's words:

   > The picture is seen from a standing person's eye height, the horizon a little above the middle. Level open ground runs across the whole bottom of the picture, with nothing tall standing on it. Leave the right ninth of the picture and the top-left corner free of doors, steps, signs and machines: put nothing there that a visitor would walk to or use. Every door, flight of steps and path named above is clearly visible, and no two of them are close together.

   The tool also places each exit's "thing to sit on" in words ("the steps are two thirds of the way across") and, for a yard, asks for the clear places 4.6 needs.
2. **Two candidates** (2K, $0.32) for a picture with more than one exit, with a foreground, or outdoors; **one** for a room with one exit and no foreground (a friend's room, the Teachers' Dormitory, the Sauna), with a rerun if its layout cannot pass. References: the plan crop, the picture being replaced "to know the school and the camera height", and the approved crop of each building it shares.
3. **The layout sitting** (the art-install role, not the owner; no `.rpy` file is touched; the owner starts it by saying which version they chose). It places every hotspot in `SPOT_PLANNED` for the place (3.2), whether or not wave 1 has registered it yet, so each picture is laid out once. It starts from `install_redo.py --compose --dry`, which draws the *old* layout on the new picture: what still sits on its thing is kept, the rest is moved. Per picture:

| laid out again | where it is written |
|---|---|
| every exit and hotspot point; which side a hover label opens | `hot_<place>.json` (`spots`, with exits under `go_<from>__<to>`; `tips`) |
| standing slots for one to four people; the floor polygon; a door for scale | `view_<place>.json` (`slots`, `floor`, `scale`) |
| a foreground outline, where the design has one | `tools/fg/<place>.json`, then `make_fg.py` |
| the light rows | `light_<place>.json`, measured by the installer, tuned by eye |
| map pins (area pictures); the Mountain box and any anchor nudge (campus map) | `area_<key>.json`, `map_campus.json` |
| words that describe the picture (`LOCATIONS[…]["desc"]`, a caption, a hotspot line) | collected as a hand-off list for the package that owns the file, never edited by the sitting |

4. **`install_redo.py --compose <stem> <render> --layout <files>`** installs a composed picture only together with its layout, and only if `tools/check_layout.py` (plain Python: the same numbers as `hot_validate`, `path_validate`, `view_validate` and `map_validate`) passes on it: every exit and hotspot inside (40, 180, 1700, 1000) and out of the toast and banner lanes and the arrival caption's box; exits 110 px apart and 120 px from a hotspot; the top-row rule; every slot's rectangle inside x 40 to 1700 and its feet inside the floor polygon; a lockable exit with room for its label; the icon-column count of 4.6; the sides of 5.2 (`check_campus.py`). A picture that cannot pass is not installable, and the reason goes to the owner in plain words. On success one step writes the picture, its layout files (`for_rev` set), the manifest row and the reference crops.

**The budget for the fourteen composed pictures and the eleven new places:**

| pictures | exits | hotspots | slot rows | pins | to follow |
|---|---|---|---|---|---|
| `courtyard` | 4 | 3 | 4 | – | a pose; a night picture |
| `library` | 1 | 3 | 4 | – | three poses; an evening picture |
| `school_yard`, `dorm_yard`, `staff_yard`, `training_yard`, `trailhead` | 29 | 7 | 20 | – | a pose; five night pictures |
| six area maps | – | – | – | 28 | – |
| the campus map | – | – | – | the Mountain box | – |
| eleven new places | 17 | about 14 | 44 | – | ten hour pictures; six poses; one polygon |

51 exits, about 27 hotspots, 72 slot rows, 28 pins: about nine layout sittings of forty minutes, one per batch that carries composed pictures. **No `.rpy` file and no harness line is edited for any of it,** because U0a turned every coordinate a harness pins into the rule it stands for (K3). First estimates for the two pictures already chosen, read off a 200 px grid and agreeing with the judges' measurements (to be set properly at the sitting): Courtyard, School Courtyard exit on the porch about (450, 720); garden exit on the gateway steps about (975, 720); Training Yard exit on the veranda steps about (1515, 860); the gate exit stays (1300, 985); the vending machine about (1365, 750); "Practice" on the straw posts about (1690, 880), at the edge of the frame the screen allows. Library: the stacks about (330, 520) and the locked cabinet's padlock about (1610, 527) (both within 40 px of today's points); the way out at the bottom of the picture, about (1480, 950): the chosen room shows no door, because I stand in it (5.2's rule).

### 5.7 Times of day

A painted hour is used when its file exists and is fresh (5.5); otherwise the day picture is tinted, as today. Each is relit **from the new day picture**, never redone from the old night picture (two separate redos would disagree in every detail the editor invents): `make_redo_workflow.py --relight <stem> evening|night`, the installed game file as input, 2K, the keep text **without** `keep_light.txt` (5.1), the hour sentence, `look.txt`, one candidate. `install_redo.py --against <day picture>` runs the fit and "nothing moved" (5.4 steps 1 and 2) and "nothing vanished" with a threshold of its own; it skips "sharper" and "nothing was added", because a night picture loses edges in its dark corners, gains pools of light on the floor and is less sharp than its day picture, and none of that is a fault. Colour is free to change. The relight thresholds are set in U0d on the eight day and hour pairs the game has today (a pair that was not made as a relight of its day picture is listed and left out). **A relight has never been run with these words; batch 1b is its test,** and batch 9 the first outdoor one. A relight refused twice is not bought again: that hour keeps the tint and the owner is told.

| place | Evening | Night | why |
|---|---|---|---|
| `dorm` (My Room) | **painted (new)** | painted (remade) | today the Evening shows the night picture warmed (AUDIT T9) |
| `dorm_common` | painted (remade) | painted (remade) | the first years every Evening |
| `girls_dorm` | tint | painted (remade) | the corridor I cross to their rooms |
| `infirmary` | tint | painted (remade) | Shoko, every Night |
| `rooftop` | painted (remade) | painted (remade) | Shoko every Evening; "Sit out with them" |
| `riverside` | painted (remade) | tint | Maki, weekday Evenings |
| `library` | **painted (new)** | tint | Panda and Toge, every Evening |
| `cafeteria` | **painted (new)**, with its own foreground cut | tint | Utahime on weekday Evenings, Yuji at weekends |
| `courtyard`, `school_yard`, `dorm_yard`, `staff_yard`, `training_yard`, `trailhead` | tint | **painted (new)** | the yards are what I walk through at Night, and a daytime sky under a blue wash is what gives the tint away |
| `ridge` | tint | **painted (new)** | the Gojo night |
| `boys_dorm`, the five rooms, `teachers_lounge`, `teachers_dorm`, `bathhouse` | the night picture, warmed (the rule `graded_bg` already has for My Room) | **painted (new)** | lamp-lit interiors read the same at both hours |
| `pool` | **painted (new)** | closed | weekend afternoons run into the Evening |
| everything else (`gate`, `classroom`, `training`, `dojo`, `storehouse`, the three offices, `forest`, `sauna`) | tint | tint | nobody is sent there after dark often enough, or it has no window; first on the "later" list |

28 relit pictures: the 8 that exist, remade; 10 new on old places; 10 on new places. And `ridge_veil`, the story's picture, made from the new ridge.

A *new* hour picture needs an image name and a `TIME_VARIANT` cell; both appear when the file does (`WORLD_VARIANTS`, 3.2), so nothing is defined for a picture that does not exist and a missing file can never break a place at that hour.

### 5.8 The missing backgrounds (every stand-in)

No layout sits on any of these except the alley's lamp, so none needs a sitting. Each is a new picture made from words and the look; two candidates for the six that carry a scene alone, one for the rest.

**Nothing lends any more (D22).** Today flat files are borrowed by other pictures through tinted crops: the city at night lends to the alley, Shibuya, Shinjuku, the mall's front and the warehouse; the morning street to Kawasaki and Yotsuka; the town street to Harajuku; the ruined hall to the mall's inside and the annexe; `veil.png` to the mall's atrium and the ridge's veil; and the board's eight jobs play straight over `bg ruin`, `bg city`, `bg veil`, `bg alley dark` and `bg town_street` (`sb_board.rpy:35-44`). Painting a lender would change several stand-ins at once, and a rule that the lender waits for its borrowers deadlocks with the cut order (cut the job sites and the prologue's street and city could never go in). So the scaffold (U0c) copies each of the five flat files as it is today to `game/images/bg/standin/<name>.png`, points every tinted stand-in in `bg_placeholders.rpy` at the copy, **defines every new image name of this table with its stand-in**, and sets the board's job-to-picture column to the five `site_*` names. From then on each picture below replaces only itself, in any order, and cutting one blocks nothing. (Two jobs change stand-in that day, because they share a kind with another: the Edogawa underpass and the Kita stairwell show the tinted hall; the checkpoint A note says so.)

| group | pictures | how each reaches the game |
|---|---|---|
| **Prologue** (9) | `alley` (lit; two versions), `alley_dark` (relit from it), `diner` (two), `home_living` (two), `home_bedroom_night`, `car` (seen from the back seat, the gap between the front seats in the middle, the driver's seat empty), and `street_morning`, `town_street`, `city_night` | `alley` and `alley_dark` drop in by name (`bg_placeholders.rpy`); the others replace a flat file of the same name. No scene line changes. |
| **The Sun Mall and the Nade sites** (5) | `mall_front`, `mall_hall`, `mall_atrium` (two versions), `warehouse`, `annexe` | new image names (U0c) with today's borrow as the stand-in; the `scene` lines that should show them are swapped by U9 (8.1). **If U9's swaps are cut, these six renders are not made** |
| **General curse sites** (2) | `ruin_hall`, `veil` (the inside of a veil) | replace the flat files |
| **Board job sites** (5 shared kinds) | `site_tunnel` (the Nerima tunnel, the Edogawa underpass), `site_ward` (the Adachi ward, the Kita stairwell), `site_platform` (the Ikebukuro platform, the Shinagawa depot), `site_pool` (the Setagaya school pool after hours), `site_karaoke` (the Koenji karaoke box) | new names (U0c); the board's job-to-picture column (`sb_board.rpy:33-44`) is data, set in the scaffold |
| **Tokyo** (9) | `shibuya` (two versions), `harajuku`, `shinjuku`, `kawasaki`, `yotsuka`; `shibuya_night`, `shinjuku_night` (relit); `club`, `market` | the five districts drop in by name; the two nights and `bg club` are defined (U0c) only when their file exists, which is what `night_bg` and `night_club_bg` look for; the market's ground is drawn by `screen market_screen` itself when its file exists (no statement added; U8); the club is one new `scene expression` line (8.1; U9) |
| **Dropped** | the konbini | no scene shows it; the one memory that opens on it for an instant is pointed at the alley (a data row); its file stays |
| **Later, with the story** | the storyboard's nine story places; Nade's doorstep; the fifteen district spots; one-off moment pictures | each needs a scene that does not exist yet or is marked for rewrite |

30 pictures, 35 renders.

**The alley and the lamp.** `LAST_LIGHT_LAMP = (1718, 108)` is a `define` inside `ch1_alley.rpy`, and this plan does not open that file. The alley's prompt asks for "one lit street lamp high in the top right corner", and `install_redo.py --anchor 1718,108 --at <x,y>` shifts the approved render (padding by repeating its edge) so the bulb lands on the point; `wp9_prologue`'s screenshot of the Last Light moment checks the glow sits within 12 px of the painted lamp.

**Light.** Each new dark picture gets a measured row in `game/layout/light.json`, read by `light_for_bg` before `BG_LIGHT`, so people stop standing daylit in a dark alley (AUDIT B19); the rows that exist were tuned to the flat stand-ins.

### 5.9 The campus map and the area maps

- **Six area maps,** composed again as bird's-eye pictures from the south (north stays up, so left on the map is left in a north-facing yard), each from the plan crop and its approved yard, with the buildings at the pin targets of 4.8 and clear ground where the pins will sit. Two candidates each; the Courtyard & Gate map is made first, alone, in batch 3's test.
- **The campus map,** a painted bird's-eye picture of the whole plan with the six area maps as references, mountains at the top, the gate at the bottom, each quarter where its marker already is. Two candidates. Installed with `map_campus.json`. Until it exists the flat drawing shows.

### 5.10 The title picture and the menu ground

- The scaffold breaks two borrowings: `gui.main_menu_background = bg_placeholder("gui/title.png", "images/bg/gate.png")` and `gui.game_menu_background = bg_placeholder("gui/menu_ground.png", "images/bg/veil.png")` (`bg_placeholder` is defined at init −3, before `gui.rpy`'s −2), and it copies today's `veil.png` to `game/gui/menu_ground.png`. Until the title exists the game shows exactly what it shows today, and the gate and the veil can be repainted at any time.
- **The title** is composed late (the owner's "less important"), two candidates: the torii and the steps at blue hour from below, lanterns lit, the campus roofs and the tower above, the left third of the frame quiet and dark enough to carry the name and the menu. The name stays as text.
- **The menu ground** is then made from the title by `tools/gen_gui.py` (blurred, darkened to the ink colour): free.

### 5.11 New people, the curses, blink and talk

| who | what is made | cost (about) |
|---|---|---|
| Mom (`mother`), Dad (`father`), Kurose (`kurose`), Nade (`nade`) | a standing sprite each, one face, by Sana's route (`docs/ASSET_PIPELINE.md`): a prompt in `tools/chars/prompts/` describing an original character and naming the house style, a base on Comfy Cloud, repairs, keying; rows in `fix_edges.py` `BASES` and `keysprite.py` `HEIGHT_CM` (a key with no row is drawn two metres tall): mother 158, father 174, kurose 178, nade 165. Mom's one face is painted for the scene she is in: warm, holding herself together. | $1.00 to $1.50 each |
| the alley's curse, the Sun Mall's curse, the small curse | painted from words at 9:16, 2K (the editor offers fixed shapes only; 1536×2752), on flat **green** (the curses here are violet, and the project's record is that purple leans toward a magenta screen and is keyed out; magenta only for a curse with green on it), two candidates each, then keyed and fitted to the 760×1400 canvas by `keysprite.py` with a `HEIGHT_CM` row per curse (the alley's and the mall's over 200 so they loom; the small one about 90); kept strange, never human (`tools/chars/CANON.md`). The alley's and the small one go over `curse_big.png` and `curse_small.png`, the same file names, so every scene and the fight screen pick them up; the mall's is a third file (8.2) | $0.96 |
| Oda | nothing: never shown | – |
| blink and talk for the other ten | phase 2's plan unchanged: 18 pictures in two sittings of nine; the rooms do not affect it. It waits only for the owner's verdict on Yuji's mouth at checkpoint B | $2.88 |

If the Comfy Cloud plan has lapsed (question 4), the base step is tried on the local paid Krea node, on Dad first (about $0.03 a candidate; never yet used for a sprite), before the other three. The second faces for Kurose and Nade wait for the story phase that will use them.

### 5.12 Poses

22, in three steps (7.2 has the list). A pose is painted on the picture the player sees at that hour, so each waits for its room and its hour picture (`make_pose_workflow.py` reads the installed game file and refuses otherwise). The two that exist are painted on pictures being replaced, so both stop showing the day their room is installed (K7) and are remade. The pose prompt gains the person's standing height in pixels at that spot (from the room's `scale`), so a seated person is no longer drawn large, and asks for "the same clean flat anime cel shading as the reference figure, a soft contact shadow only". **These changes, the order check of K8, and the manifest row and `pose_<place>.json` box that `install_pose.py` writes are U0d's, in wave 0,** so the first pose test (batch 2) is made with the tooling it is testing and shows the day it is installed: without a manifest row a pose on a revised picture counts as stale (5.5) and would not show. U3 only re-picks `POSES`. **Two people at one piece of furniture** (7.2 rows 12 and 13, 16 and 17) are each given a named, separate seat in `POSES`; the second is made after the first is installed, and `install_pose.py` refuses a box that overlaps another installed pose box of the same room and hour picture, naming both (a pose reaches the game as an opaque box cut from a whole-room render, so an overlap would paint empty room over the other person). Utahime's carries her sprite and, in plain words, "long dark hair, a ribbon, a scar across the face" (AUDIT P12).

### 5.13 Every batch

One drag-in file and one page of numbered steps each (`~/Desktop/JJK Game images/ui2/art_<n>.md`), twelve renders or fewer. "a then b" is two short runs in one sitting: the day pictures, a look, then their hour pictures (K7). `tools/art/batches.json` holds this table; `tools/art_batch.py <n>` writes the workflow and the note. All prices are Nano Banana Pro at 2K, $0.16 a render.

| # | what | renders | cost | needs first | what it unlocks in the game |
|---|---|---|---|---|---|
| **0** | **nothing to run.** Install the four pictures already made: the gateway Courtyard and the bright Library (each with its layout sitting), the Common Room and the Cafeteria (third test) | 0 | $0 | checkpoint A; U0d | the look, in the game, on four places; the Courtyard's exits on its three buildings. (Until batch 1 the Common Room's evening and night are its new day picture tinted, K7) |
| **1** | **the rooms where every evening is spent.** a: the Common Room and the Cafeteria once more for their window lines; My Room (with the laptop), the girls' corridor, the rooftop. b: Common Room evening and night; My Room evening and night; the corridor's night; the rooftop's evening and night | 5 + 7 = 12 | $1.92 | the plan approved (the window lines come from it) | five rooms whole, by day and after dark, foregrounds recut. Also the first test of three wordings: the frozen look, a named addition (the laptop, in a) and a relight (b) |
| **2** | **the first pose back:** Nobara on the sofa, on the new evening Common Room (two versions) | 2 | $0.32 | 1 (the pose tooling is U0d's and the pose box has its own file, so she shows the day she is installed, beside wave 1) | a painted person in the new look, the first read on whether she matches the sprites |
| **3** | **the test of the plan:** the School Courtyard and the Dormitory Garden (two versions each); the Courtyard & Gate area map (two versions) | 6 | $0.96 | the plan approved; 0 | proves or changes 5.2's mechanism before the other three yards and twelve map renders depend on it (5.2 has the pass rule and what follows a failure). Good results are installed |
| **4** | **the other yards:** the staff steps, the Training Yard, the Mountain Path (two versions each) | 6 | $0.96 | 3 judged | the whole campus walked by exits on final pictures; the doors of the four new buildings |
| **5** | **the icon sheet** (sheet 4: the 26 new icons, two versions; sheet 3 is not run again) | 2 | $0.32 | U0c | icons for everything new (until then they show their word) |
| **6** | **the maps.** a: the School, Dormitories, Staff, Grounds and Mountain area maps (two versions each). b: the campus map (two) | 10 + 2 = 12 | $1.92 | 3, 4 | the painted campus map; pins on the right roofs → **checkpoint B** |
| **7** | **the school, staff and training rooms.** a: classroom, infirmary, Yaga's office (with the desk), Utahime's office, Gojo's office, training hall, dojo, storehouse. b: infirmary night; Library evening; Cafeteria evening | 8 + 3 = 11 | $1.76 | 1 (the Cafeteria's final day picture) | most of the campus in the look; the evening as the second years spend it |
| **8** | **the gate and the mountain.** a: gate, forest, riverside, ridge (with the veil). b: riverside evening; ridge night; the strong veil picture | 4 + 3 = 7 | $1.12 | U0c (the title no longer borrows the gate) | every old place in the new look. a is the first test of the outdoor keep wording and of the veil as an addition |
| **9** | **the yards at night:** Courtyard, garden, Mountain Path; then the School Courtyard, the staff steps, the Training Yard | 6 | $0.96 | 0, 3, 4 | the campus at Night: lit windows, a real sky |
| **10** | **the Boys' Dormitory.** a: the corridor (two versions), Yuji's room, Megumi's room, Panda and Toge's room. b: their four nights | 5 + 4 = 9 | $1.44 | 1 (My Room, as the building's reference), 3 | the dormitory as itself; visiting at Night |
| **11** | **the teachers' house and the girls' rooms.** a: the lounge (two versions), the Teachers' Dormitory, Nobara's room, Maki's room. b: their four nights | 5 + 4 = 9 | $1.44 | 1, 4 | where the teachers stay; the girls' rooms |
| **12** | **the baths and the pool.** a: the Bathhouse (two versions), the Sauna, the pool (two). b: the Bathhouse's night; the pool's evening | 5 + 2 = 7 | $1.12 | 4 | the owner's recovery rooms and pool |
| **13** | **the pose test:** Utahime at her desk, Megumi at the Library's reading table (two versions each) | 4 | $0.64 | 7 (Utahime's office); 0 (the Library) | the owner's ruling on painted people in the new look, before nineteen more are bought → **checkpoint C** |
| **14** | **poses, main places, first five** (7.2 rows 4 to 8) | 10 | $1.60 | the owner's yes at checkpoint C; 7 | people doing things |
| **15** | **poses, main places, second five.** a: rows 9 to 12. b: row 13 (Toge, after Panda is installed at the same table) | 8 + 2 = 10 | $1.60 | 7, 8 | |
| **16** | **poses, at home at Night, first five.** a: rows 14, 15, 16, 18. b: row 17 (Toge, after Panda is installed at the same board) | 8 + 2 = 10 | $1.60 | 10, 11 | people at home at Night |
| **17** | **poses, at home at Night, last four** (rows 19 to 22) | 8 | $1.28 | 7, 8, 9, 11 | |
| **18** | **the whole prologue.** a: the alley, the diner, the living room (two versions each), the city at night. b: the dark alley (from the installed alley), the bedroom at night, the car, the morning street, the town street | 7 + 5 = 12 | $1.92 | – (nothing lends any more, D22) | the first twenty minutes of the game on real pictures, street, city and all |
| **19** | **the Sun Mall, the Nade sites, the board.** a: mall front, hall, atrium (two versions), warehouse, annexe. b: the five job sites | 6 + 5 = 11 | $1.76 | a: U9's first commit, to be seen (**if U9's swaps are cut, a is not made**). b: – | the arc's main mission and the board's jobs on their own pictures |
| **20** | **Tokyo:** Shibuya (two versions), Harajuku, Shinjuku, Kawasaki, Yotsuka; then Shibuya and Shinjuku at night, the club, the market | 6 + 4 = 10 | $1.60 | – for the districts and their nights; the market's ground shows once U8 has merged, the club once U9 has | day trips and the night out |
| **21** | **the two general curse sites and the title:** the ruined hall, the inside of a veil; the title (two versions) | 4 | $0.64 | 8 (the new gate, as the torii's reference), for the title only | the last flat pictures gone; a title screen of its own; the menus' ground made from it |
| **22, 23** | **blink and talk** for ten people, nine pictures and nine | 9 + 9 | $2.88 | the owner's yes on Yuji's mouth (checkpoint B) | everyone blinks and speaks |
| **24** | **the people and the curses:** Mom, Dad, Kurose, Nade; three curses (two versions each) | 6 and the four people | about $6 | ruling 4; U7 (the guarded stand-in block, the height and base rows, the curse switch) | no block figures left → **checkpoint D** |

**Totals:** 186 background, pose, icon and face renders ($29.76), six curse renders ($0.96) and the four people (about $5): **about 190 renders, about $36.** Installed: 35 place pictures, 28 hour pictures and `ridge_veil`, 7 maps, 30 stand-in replacements, the title, 22 poses, 18 blink-and-talk pictures, 7 sprite and curse files, 26 icons, plus free foreground cuts and the free menu ground: about 150 pictures. Allow one render in five run a second time: **$43.** The three look tests already spent about $2.57 (sixteen renders). The fallbacks of 5.2 and the canary of 5.2 come out of the allowance. No single run is over ten paid boxes (the record: a rate-limit failure aborts a run), which is why 18 and 19 are two runs each.

Batches 1 to 6 can be run in any order the owner likes except where the table says "needs first"; batches 14 to 24 likewise. Everything after batch 13 can stop at any point with the game whole.

---

## 6. Blending: people who stand in the room

The owner's sentence was read as: a shadow under them, colours matched to the room's light, a believable size and floor line, furniture in front of them where it belongs; and, after the rooms are redone, painted poses (section 7). Today the game has a simple form of each: one soft shadow blob, the same shape everywhere; one hand-set tint per room or per hour; one sole line for every room; three rooms with a foreground; eight rooms with fitted standing rows; and nothing that measures any of it.

**The one constraint everything here is built round (K9).** A sprite on screen during a save is saved as the displayable `lit_sprite` built. Anything added to that tree is in every save made mid-scene, for good. So nothing is added to it. Blending is done in three places that are safe: **data** the existing `_sprite_light` and `_shadow_light` already read; **`view_sprite` and the stage screens**, which build their displayables in the screen's `add` line on every draw and never reach a save; and **sidecars and polygons**.

### 6.1 The room's data

`game/layout/view_<place>.json`, hand-authored at the place's sitting; every key is optional and has today's behaviour as its default.

| key | holds | how it is got | read by |
|---|---|---|---|
| `slots` | where 1, 2, 3, 4 people stand: `[x centre, y offset, zoom, far]` | proposed by `tools/stage_preview.py --propose` from `floor` and `scale`, corrected by eye on the preview | `view_slots` (exists; the sidecar already wins over code) |
| `poses` | pose boxes; from this overhaul they are written to their own file, `game/layout/pose_<place>.json`, so an install never touches a `view_` file a package has open (K15) | `install_pose.py` (exists) | `view_pose` (the `pose_` file first, then this key) |
| `floor` | one or two polygons of floor or ground a person may stand on, and optional polygons they may not (the pond, the railing, a table top) | traced on the picture | the preview and `check_layout.py` only (never the game, except `view_floor` for the review tools) |
| `scale` | `[x, y top, y bottom]` of one door or post beside where people stand, taken as 200 cm | read off the picture | the preview and `check_layout.py` only |
| `slot_light` | per hour and per slot, a small `[tint, brightness]` on top of the room's row, for a slot in a sun patch or in shade | the sampler, at each slot's own rectangle; left out where the difference is small | `view_sprite` |
| `cast` | outdoors, per hour: `[direction, length, darkness]` of a long shadow on the ground | judged from the picture's own shadows | `view_stage` |
| `talk` | the foreground stays up in dialogue | by eye, on the dialogue preview | `view_enter` |

`game/layout/light_<place>.json`, written by the installer: `{"": row, "evening": row, "night": row}`, a row being `[tint, brightness, saturation, shadow opacity]` or the same with `[..., shadow lean in px, shadow stretch]`.

All 35 places get a `floor`, a `scale` and `slots` (today 16 of 24 stand people on default spots: the pond, the railing and the sweets table are among them). Rooms redone in place have theirs written on today's picture, because nothing moves; composed pictures and new places get theirs at their layout sitting.

### 6.2 What is drawn, and where

| # | effect | drawn by | data | reaches | in a save? |
|---|---|---|---|---|---|
| 1 | **Light matched to the picture, by measurement,** for every place and every hour picture | the existing `_sprite_light`; `light_for_place` reads the sidecar row first, then `PLACE_LIGHT`, then the default | `light_<place>.json` | everyone lit, wherever they are drawn: the stage, the person view, dialogue, story scenes, the board | `scene_light`, the tuple that is saved today |
| 2 | **Light tied to the tint where the hour is only a tint.** At Night in a yard the picture is washed `#6f86d8`, −0.34 and people only `#a8b6e8`, −0.10, so they glow. The sprite's light for a tinted hour becomes the day row moved 60% of the way to the background's own grade, so the two tables can no longer drift apart | `light_for_place` | one constant, `LIGHT_FOLLOW = 0.6`, and the grade tables that exist | everyone lit, in every place without a painted hour | no |
| 3 | **A shadow that follows the room's light.** The blob under the feet leans away from the light and stretches when the light is low; it is fainter in flat light and stronger under a lamp | the existing `_shadow_light` (same name, same signature): besides `alpha` it sets `xoffset` and `xzoom` on the shadow's own Transform | two more values at the end of a light row; a four-value row means (0, 1.0). `light_matrix` reads the first three values of a row of either length | everyone lit by `lit_sprite`. In dialogue it is behind the text box, so it pays off on the stage and the person view | old saves hold four values and the code accepts four or six |
| 4 | **Size and floor line per room** | `view_slots` | `slots` | the stage, and where the person view's ease starts | no |
| 5 | **A different light per standing spot** | `view_sprite`: the per-slot `matrixcolor` it already sets for hover and distance also takes the slot's `[tint, brightness]` | `slot_light` | the stage only | no |
| 6 | **Furniture in front of people,** in more rooms (the table below), and **kept in front while talking** where the room's sidecar says `talk` | `view_fg` and `view_enter`, as today | polygons in `tools/fg/`; `talk` | the stage; dialogue in rooms marked `talk` | the foreground's file path, as the cafeteria's is today: those files are never renamed |
| 7 | **The others stay in the room** while I look at one person, dimmed and one blur step back, not clickable. In the conversation itself they step out, as now | `screen view_others(loc, who)` in `view_stage.rpy`, used from `sb_char` by one line the scaffold places | – | the person view | no |
| 8 | **A painted person stays painted** while their card is open (D31) | `view_focus` keeps the pose patch in place; the sprite eases in only when a scene starts | – | the person view | no (screen only; if the scaffold's test shows otherwise, this row is dropped and today's fade stays) |
| 9 | **A long cast shadow outdoors,** by day and evening | `view_stage`: one more `add` under each standing person, the shadow picture squashed, skewed and dimmed; a fixed transform, no function | `cast` | the stage only | no |
| 10 | **Panda fits:** slot choice and the foreground test use each person's own canvas width (880 for Panda), so he is no longer sliced by the cafeteria table's layer | `view_pick_slots` | – | the stage | no |
| 11 | **The stand-in people stop being flat:** Mom, Dad, Kurose and Nade become `lit_sprite` sprites (8.2) and get the shadow and the room's light with them | – | – | story scenes | by image name |

**Foregrounds after this overhaul** (free, cut from the room's own pixels by `tools/make_fg.py`, recut by the installer on every install of the room or one of its hours):

| room | object | hours |
|---|---|---|
| `dorm_common` | the low table | day, evening, night (recut) |
| `cafeteria` | the near table | day (recut), evening (new) |
| `utahime_office` | the desk | day (recut) |
| `office` | the new desk, Yaga behind it (only if the desk holds, 5.3) | day (new) |
| `gojo_office` | the sweets table (his feet are in it today) | day (new) |
| `teachers_lounge` | the sofa's back | day, night (new) |

Not given one: the Library and the infirmary (their tables and desks are filled by poses), the classroom (the desks are too thin to hide anyone behind; Megumi is painted at one instead), the yards, the friends' rooms.

**Not done, and why:** a gradient or rim light with direction over each sprite (a new layer inside `lit_sprite`, in every dialogue save for good, for an effect the text box mostly hides); a second foreground plane; a per-room size in dialogue and story scenes (it means redefining `pos_c` or `view_enter_ease`, and what an old save holding them does afterwards has never been tested); the others staying on screen during the conversation itself. All are on the "later" list (section 11).

**Motion budget (R9):** no new function transform anywhere. The eight a place view may hold stay eight; `p2_view`'s call-count check passes unchanged.

### 6.3 Rules for where people stand

Written into every layout sitting and checked by `check_layout.py` and the preview:

- every near slot's feet are inside a floor polygon and outside every no-stand polygon; a far slot's feet are inside the floor and behind the foreground polygon;
- a person's drawn height at a slot (the near line draws a 173 cm person 596 px tall, about 3.45 px a centimetre) is within 12% of what the room's `scale` says a person that tall measures at that depth;
- name tags stay inside x 179 to 1700, people inside x 40 to 1700 (the existing validator);
- **no slot row for one or two people hides any hotspot of the room,** and no row for one to four people hides the room's only things to click (Megumi no longer stands in front of the television and the card table: AUDIT F5, R12);
- in a yard, the four-person row leaves clear the number of exits 4.6 asks for;
- the Courtyard's vending machine, which is never hidden, stays clear of every slot row.

### 6.4 What it costs when drawn

Per standing person: one sprite, one shadow quad, outdoors at most one cast-shadow quad; two 0.25 s light functions (as today), two 0.05 s face functions where blink and talk exist (as today), one breathing function (as today). Per room: one background, at most one foreground layer. On the person view: up to three dimmed sprites more, with static blur. The shadow's lean and stretch are set inside a function every sprite already carries, on its existing tick. Nothing is added per frame.

### 6.5 How it is measured and tested

**Outside the game, on the pictures** (ComfyUI's Python; `tools/test_art_tools.sh` runs all of it and prints PASS, FAIL or one SKIPPED line):

- **`tools/sample_light.py <place> [variant]`** reads the standing rows, takes the band of floor under the soles and the band of wall behind the heads, and proposes the row: tint (the band's mean colour, pulled halfway to white: people are lit by the room, not painted with it), brightness (the floor's luminance against a mid-lit floor, clamped), saturation, shadow opacity (higher under a lamp), lean and stretch (from which side is brighter at head height and how low the light is). The installer writes it; a person may tune it. `--check` fails a hand-edited row that has drifted more than 0.12 in brightness or 0.15 in any tint channel from the sample unless the file says why (`"note"`), so "matched to the room" stays a measured claim and a redone room cannot keep the old room's light.
- **`tools/stage_preview.py <place> [hour] [--who a,b,c] [--bg <render>] [--dialogue]`** draws the stage as the game draws it: the picture under its hour's tint and the ink wash, each person's sprite at their slot's zoom and floor line, the light matrix, the shaped shadow and the cast shadow, the far steps, the foreground on top, every hotspot and exit ring, the name-tag line. One sheet per place (`shots/stage/<place>.jpg`: one to four people by day, and a frame for each hour picture). It is what a room is judged on **before** its picture is installed (`--bg` takes a render straight from ComfyUI's output folder), what goes in each art note ("here is the room with the people who use it"), and what a reviewer looks at. `--dialogue` draws the scene case (people 23% larger, feet on the bottom edge), because a room that looks right on the stage can look wrong in a scene.
- `check_layout.py` on every `view_` file: 6.3's rules by number.

**In the game** (`tools/smoke/u2_blend.rpy`, with test sidecars under `tools/smoke/assets/u2_blend/`; not pointer-dependent):

- a sidecar's light row, `slot_light` and `cast` are read, win over the tables, and fall back key by key; a stale row is not used;
- with a four-value `scene_light` set by hand (an old save's), `_shadow_light` and `_sprite_light` run without error and leave the lean at 0 and the stretch at 1;
- after Wait, after walking, in a story scene, on a board job and on a Tokyo trip, `scene_light` equals what the picture shown gives (the five set points);
- at Night in a yard with no painted hour the sprite's brightness is within 0.10 of the background's;
- **the saved sprite is unchanged (K9):** a text dump of `lit_sprite(...)` for Yuji (each node's class, its function's name, its curried argument names, its file path) equals `tools/smoke/baseline_sprite_tree.txt`, written by U0a from the untouched tree, and the pickle of what `lit_sprite` returns is byte for byte what it was;
- R10's save test (`p2_view`: save and load on the first line after `stage_person`, in a room with a foreground kept in dialogue, after a rollback, with blink and talk) passes unedited, and again with a pre-overhaul save in which a sprite is showing;
- the count of function transforms on the place view is unchanged; with Motion off, zero;
- the person view with four people on stage: three dimmed, none focusable;
- every place returns slots for one to four people from its sidecar or its code row, never the bare defaults.

---

## 7. People doing things, and things to do

### 7.1 Captions: every cell says something

Every (person, place) pair the routine can produce gets its own caption in `AMBIENT` (today 21 of 43 show a filler). A caption never claims a prop or clothing the standing sprite contradicts ("in a yukata" is out; "fanning herself on the bench" is in). New cells, as proposed:

| who, where | caption |
|---|---|
| Yuji, his room | on the floor in front of a paused film |
| Megumi, his room | reading on the bed, shoes lined up by the door |
| Panda, the shared room | filling half the floor, a shogi board in front of him (alone: "setting up the shogi board") |
| Toge, the shared room | cross-legged at the shogi board, one move ahead |
| Nobara, her room | at the desk, laying her nails out in a row |
| Maki, her room | cleaning her glasses, a weapon case against the wall |
| Maki, the Bathhouse | on the bench, a cold milk in her hand |
| Nobara, the Bathhouse | fanning herself, arguing with Utahime about the fan |
| Utahime, the Bathhouse | losing an argument about the fan |
| Yuji / Nobara / Panda, the pool | at the edge, daring someone to race / feet in the water, sunglasses on / floating. Just floating. |
| Ijichi, the lounge / the Teachers' Dormitory | reading yesterday's paper / asleep sitting up, tie still on |
| Yaga, the lounge / the Teachers' Dormitory | the baseball on with the sound off / at the workbench, stitching an ear on |
| Utahime, the lounge / the Teachers' Dormitory | marking reports in red / by the hearth with tea and tomorrow's lists |
| Yuji, the garden at Night | by the pond, counting stars out loud (tied to Night; a day line for when I walk him through) |
| Ijichi, the gate | on the phone by the torii |

The 21 fillers are written the same way by the package that owns the table (U4) and shown to the owner at checkpoint B as one list. Captions that can never show are fixed or removed: Megumi's riverside line and Nobara's rooftop line go (their routines never go there); Panda's "sparring with Toge" becomes "stretching, slowly, like a building settling"; Utahime stops being "buried in paperwork" in the cafeteria. A person I asked to the card table reads "here because I asked".

**Seeing them without hovering.** The owner's ruling "pictures without words" stands as the default. Added: a "Show names" row in Preferences (`persistent.show_names`) and a held key (N; not Tab, which is Ren'Py's skip toggle) that, while down, labels every person with their caption, every exit with where it goes and every icon with its name.

### 7.2 Poses: the policy and the list

- One person, one picture. No group pictures (they are fixed to who is there, and the schedule moves). People who share a table are painted at the same table, **each in a named seat of their own** (5.12): Panda at the left end of the Library table and Toge at the right end; Panda on the near side of the shogi board and Toge on the far side. The second of a pair is made after the first is installed, and the tool refuses overlapping boxes. If the board is too small for two separate boxes beside Panda's 880 px canvas, Panda is painted there and Toge stands.
- A pose is made for a (person, place, hour picture) the routine really produces; the harness checks every row against the schedule and counts the rows from the tool's table, never from a literal (`p2_view.rpy:712`'s "exactly 14" becomes that rule).
- A pose is made only after its room **and** the hour picture it is seen on are installed (K8), and shows only with the picture it was painted on (K7).
- **A pose steps aside when its caption is not the one showing:** when an `AMBIENT_STORY` row has taken over (after the Sun Mall Nobara is "re-taping the grip of her hammer" while her pose holds a phone), the standing sprite shows, unless the pose's row lists that condition (AUDIT P11).
- A painted person stays painted while I look at them (6.2 row 8). A companion never takes a pose.

| # | who, where, hour | doing | batch |
|---|---|---|---|
| | **The test (3):** does a person painted into a "real place" still match the sprites beside them? | | |
| 1 | Nobara, Common Room, evening | on the sofa with her phone (remade) | 2 |
| 2 | Utahime, her office | writing at her desk (remade, matched to her sprite) | 13 |
| 3 | Megumi, Library | reading at the table by the window | 13 |
| | **Main places (10)** | | |
| 4 | Yuji, cafeteria | eating at the near table | 14 |
| 5 | Megumi, classroom | reading at a desk by the window (the answer to "someone at a desk") | 14 |
| 6 | Shoko, infirmary, day | at her desk with coffee | 14 |
| 7 | Maki, dojo | drilling with a staff (her main place; it was the training hall) | 14 |
| 8 | Yaga, his office | sewing at the new desk (or at the low table, 5.3) | 14 |
| 9 | Gojo, his office | on the sofa | 15 |
| 10 | Yuji, Courtyard | at the vending machine | 15 |
| 11 | Ijichi, Main Gate | on the phone by the torii | 15 |
| 12 | Panda, Library, evening | at the table, turning pages very carefully | 15 |
| 13 | Toge, Library, evening | at the other end of the table, a book open, hands in his sleeves | 15 (after row 12) |
| | **At home at Night (9)** | | |
| 14 | Megumi, his room | reading on the bed | 16 |
| 15 | Yuji, his room | on the floor in front of a paused film | 16 |
| 16 | Panda, the shared room | at the shogi board | 16 |
| 17 | Toge, the shared room | on the far side of the shogi board | 16 (after row 16) |
| 18 | Nobara, her room | at the desk | 16 |
| 19 | Maki, her room | cleaning her glasses | 17 |
| 20 | Shoko, infirmary, night | at the desk, lamp on | 17 |
| 21 | Yuji, the garden, night (weekends) | by the pond, looking up | 17 |
| 22 | Gojo, the ridge, night (his night) | on the rock, looking up at the veil | 17 |

Not painted now (section 0 says so): the teachers at home (Yaga, Utahime and Ijichi stand as sprites in the lounge and the Teachers' Dormitory) and anyone at the baths or the pool. Each is a row and two renders ($0.32) whenever wanted.

Of the twelve phase 2 planned, nine are kept and three are re-pointed at where those people now spend their time (Maki from the training hall to the dojo; Toge and Panda from the cafeteria and the Courtyard to the Library). If the test fails, poses stop at three and captions plus "Show names" carry "people doing things".

### 7.3 Dead things come alive

**Every place has at least one thing in the picture besides its exits** (a rule in `u2_things`). Looks are free and work at Night. Each is a row in `room_spots.rpy` and a point in the place's `hot_` sidecar; points for a room redone in place are measured now, on today's picture, and points for a composed picture at its layout sitting. **The ids are frozen first** (`SPOT_PLANNED`, 3.2, in the scaffold), so a layout sitting that happens before wave 1 (batches 0, 3 and 4 do) places every look and moved action once, and lint accepts a point whose hotspot is planned but not yet registered.

**Exits sit on doors, indoors too** (AUDIT M4; U4, who owns the `hot_` files of the rooms redone in place). Each in-place room's exit is put on its painted door, on today's picture; where the room shows no door, it goes to the bottom of the picture as the way back (5.2's rule). Known today: the infirmary's (at (84, 500), on a window), the ridge's, and the girls' corridor's (at the far end; the stairs are behind me). `check_layout.py` holds the rule: an indoor exit is inside a door box named in the room's keep list, or in the bottom band.

**Actions that move onto the object they belong to** (no new action id; the column tile disappears while the object is visible, as `hot_covers` already does, and comes back when a person stands in front of it): Study on the classroom's front desk and on my own desk; "Sit a while" on the rooftop railing; Train on the training hall's straw bundles, the dojo's weapon rack and the Training Yard's posts (a new place for it); Practice on the Courtyard's straw posts; Swim on the river's deep pool. The card table's icon moves from the floor cushion onto the low table, and stays, dimmed, once the day's limit is reached (AUDIT R13, L3). The dimming is drawn by `hot_layer`, which is final in the scaffold: U0c gives it a generic "spent" state (a registered hotspot may name a `dim` function; today it dims only for the night rule or a lock, `sb_hotspots.rpy:312`), and U5 supplies the function.

**Looks** (about 40; three or four first-person lines each, turning by day as the three existing looks do):

| place | look | place | look |
|---|---|---|---|
| Main Gate | the torii | Boys' Dormitory | the shoe rack; the notice board |
| Courtyard | the gateway and its steps | Yuji's Room | the film shelf |
| School Courtyard | the pine and the bench | Megumi's Room | the bookshelf |
| Classroom | the notices by the door | Panda and Toge's Room | the shogi board |
| Cafeteria | the water cooler | Nobara's Room | the mirror |
| Infirmary | Shoko's desk | Maki's Room | the weapon case |
| Library | the reading table | Teachers' Lounge | the rota (useful: who is where this hour); the kettle |
| Dormitory Garden | the pond; at Night the lit windows | Teachers' Dormitory | the workbench; the name plates |
| My Room | the wardrobe; the window (what the ridge looks like tonight) | Bathhouse | the milk fridge |
| Common Room | the fridge; the board-game boxes; the manga shelf; the television now names who is watching | Sauna | the bucket |
| Girls' Dormitory | the plant at the end | Swimming Pool | the lane board |
| Rooftop | the view | Staff Building Steps | the stone lanterns |
| Principal's Office | the dolls; the photograph | Utahime's Office | the binders |
| Gojo's Office | the television; the sweets ("I don't. He counts them.") | Storehouse | the big chest |
| Training Hall, Dojo | the mats; the wall shrine | Mountain Path, Forest Trail, Riverside | the standing stone; the stone markers; the waterfall |

With the moved actions and the new places' own actions that is about 65 things to click in the pictures against 15 today. The lines are caption text, not story; they are proposed by U4 and read by the owner at checkpoint B. Not built (each is a feature, not a look; section 11): watching the television with someone, the console, opening the locked cabinet or the chest, the wardrobe as outfits.

### 7.4 The card-table invite

"Like invite toge or panda etc to come play."

- **Where.** A second tile beside the card table's, **"Ask someone to the table"** (`cards_invite`, its own icon: the existing invite icon already means "Ask them along"). Shown whenever the table could be sat at this hour (so never at Night) and a seat is free.
- **Who.** A small picker, `screen cards_invite_pick`, shows the faces of every student I have met who is on campus this hour (their routine puts them somewhere, at home included), is not already in the room, is not pinned somewhere by the story, and whom I have not already asked today. No Bond level. Each tile says where they are now ("in the Library").
- **What happens.** One line as they come in ("Toge looks at his phone, then at the door. He comes."; one per person) and they are **in the Common Room for the rest of this hour**: standing on the stage, on the map, in the journal, and at the table when I sit down, because `cards_opponents()` already takes whoever is in the room. I can ask again while a seat is free (the table seats three with me). Next hour they are back in their routine.
- **How, with no new saved state.** The game already has a way to put a person somewhere for one hour: `pin(who, loc)`, which writes `schedule_overrides[(who, day, period)]` (`sb_world.rpy`; story scenes use it). The invite calls `pin(who, "dorm_common")` for the current hour and adds `"cards_inv:<who>"` to `actions_today`.
- **Cost.** Free: it takes no hour. The game at the table costs what it costs today. Nothing in `sb_do_cards_play` changes, and none of its protected statements. The picker is one new `call screen` pair, protected from the commit it lands in.
- **What it does not do:** invite by phone or from a dormitory door; invite teachers; carry over to the next hour. Each is a word away.

### 7.5 What teaches a new player

- **Six one-time hints** (`game/ui_hints.rpy`): a single line in the objective banner's lane the first time its situation happens, gone on the first click, never again (`hint_seen`). (1) the first place view: "Things in the picture can be clicked: people, glowing objects, and the doors and paths that lead somewhere else."; (2) after it: "Rest the pointer on anything to see its name. Hold N to see them all."; (3) the first time the map opens: "Pick an area, then a place. Walking is free."; (4) the first time a person stands in a place: "Click someone to talk or to do something together."; (5) the first time an hour is spent: "Each thing with a pip takes an hour. Wait lets an hour pass."; (6) the first Night: "At Night nothing that takes an hour can be started. I can still walk, talk, look and visit. Go to bed ends the day." The first five show only before day 3, so an old save is not lectured and no migration is needed; the sixth can show once to anyone. Never shown in a replay, in explore mode or while skipping.
- **"How to play"** in the pause and title menus: the orphaned `screen help`, rewritten as one page in the game's words (the place view, the map, the journal, the hours and the night, walking, the keys M, J, N, Esc and Space, and Tab to skip, as in any Ren'Py game).
- **A small card when the day turns** ("Day 9 · Tuesday", two seconds), shown from the new-day hook the way the objective banner is; it takes no required argument, so a save holding it loads.
- No scripted walkthrough: that would be a new story scene.

---

## 8. Scenes and screens

### 8.1 Story files: seven scene lines, then faces (U9, alone)

**Why it is safe.** A save resumes at a statement name. When a changed `.rpy` is compiled beside the old `.rpyc`, names are carried over by matching each statement's identity (Ren'Py 8.5.3, `script.py:556-572`). A say statement's identity is its speaker and its words, not its attributes; a menu's has no text at all, and it keeps its name while a neighbour keeps its own; a `scene` whose image changes gets a new name, and no save rests on a `scene`. Seven of the owner's eleven saves rest on menus inside story files, so the rules are narrow.

**Commit 1: the scene lines that change picture.** Each new image name is defined in `bg_placeholders.rpy` by the scaffold (U0c) with today's picture as its stand-in, so the swap can merge before the pictures exist and shows what it shows today.

| file | today | becomes |
|---|---|---|
| `ch4_mission.rpy:22` | `scene bg city` | `scene bg mall_front` |
| `ch4_mission.rpy:79`, `:337` | `scene bg ruin` | `scene bg mall_hall` |
| `ch4_mission.rpy:291` | `scene bg veil` | `scene bg mall_atrium` |
| `missions_arc1.rpy:43` | `scene bg city with fade_hard` | `scene bg warehouse with fade_hard` |
| `missions_arc1.rpy:113` | `scene bg ruin with fade_curse` | `scene bg annexe with fade_curse` |
| `story_arc1.rpy:335` | `scene bg courtyard with fade_slow` (Maki's roster, "the board outside the classroom building") | `scene bg school_yard with fade_slow` (AUDIT G9) |
| `sb_night.rpy`, the club branch of `label night_out` | no picture of its own: it plays on over `scene expression night_bg(key)`, the district's night | one new line, `scene expression night_club_bg(key)`, after `$ add_yen(-NIGHT_OUT["cover"])` and before the first say line; away from the three protected menus and both `call market_open` pairs, in a label marked for the story rewrite. Not `scene bg club`: a fixed stand-in is one picture, and the club in Shinjuku would show a Shibuya street until the art exists. `night_club_bg` (U0c) returns `"bg club"` once that file exists and the district's own night until then, so the line shows exactly today's picture the day it lands |

None of the seven is the statement after a `call`; none sits directly before a menu whose first inner line also changes; only the image name changes on each. (Read at today's lines.)

**Commit 2: faces.** Scope: the 26 `ev_*` character scenes in `events_arc1.rpy` and the `act_*` scenes in `events_activities.rpy`, `events_intimate.rpy`, `events_romance.rpy` and `events_stand.rpy`: about 1,150 lines of script in which no face changes today. Chapters 4 and 5, the Nade missions, Kurose, Oda and `story_arc1.rpy` wait for the story phase, which rewrites them.

- A face is added **only as a say attribute** on a line that person already speaks: `yuji serious "…"`, or `yuji @ surprised "…"` for one line. The words between the quotes stay byte-identical.
- **No `show` line is added, no line is reworded, no "you" becomes "I",** no menu, call, flag or reward line is touched. A face that would need a narration line to change on is left for the story phase.
- Each scene's first spoken line carries an explicit face, so the greeting face no longer runs through a grave scene (Yuji grinning through his third scene). Then about one change every four or five spoken lines, on the line where the mood turns.
- Only the eleven campus people and Kaito's portrait, only the six faces.

**Proof.** `tools/smoke/u2_names.rpy` compares, in a tree whose `.rpyc` are copies of the owner's, every say, menu, call, `call screen`, label and user statement of the edited files against `tools/smoke/baseline_story_names.json` (written by U0a before any story file is touched): every old name must still exist with the same kind, speaker and words, and the number of statements in each file may differ only by the one listed new line. Then `tools/load_all_saves.sh` must show the same seventeen rows SAME. Then lint (it rejects an attribute with no picture), `wp9_prologue`, `wp10_chapters`, `wp5_memories`, `phase1_all`, `phase2_all`, `p2_saves`, `p2_night`.

**Known cost:** the mouth moves on the calm face only, so more faces means the mouth shows less often. Accepted for now; a talking mouth per used face is on the "later" list.

**Why it is last, alone, and first on the cut list.** It is the only step that edits files the owner's saves rest in, it needs no art, and nothing depends on it. If the owner would rather faces wait for the story rewrite, commit 2 is skipped; if commit 1 is skipped too, the mall, the warehouse and the annexe keep playing on the painted general pictures.

### 8.2 The stand-in people and the curses (U7)

- **The five stand-in lines** at `jjk_defs.rpy:96-100` become one guarded block, at `init 1 python` (after `jjk_sprites.rpy`'s init-0 `image` statements), that defines `mother`, `father`, `oda`, `kurose`, `nade` as today's tinted figures **for each key where `not renpy.has_image(key, exact=True)`** (an `image` statement cannot be conditional, so the block calls `renpy.image`). The guard is on the image, not on the file: when `mother_neutral.png` has landed but `tools/gen_sprite_defs.py` has not been run yet, nothing else defines `mother`, and a guard on the file would leave `show mother` (`ch1b_the_offer.rpy:121`) with no image. When the generator is run, its `image <key> = lit_sprite(...)` takes over. No scene line changes: `show mother at pos_cl` shows the new sprite, with a contact shadow and the room's light, in old saves too. The four old flat files stay until all four people have landed, and `oda` keeps using one.
- No Character gains an `image=` tag in this overhaul and no attribute is given to Mom, Dad, Kurose or Nade (an attribute on a speaker with no pictures is a lint error and a crash). That, and their second faces, arrive with the story phase.
- **The curses** drop in by file name (5.11). The Sun Mall's curse is a third file: `image curse big` becomes a switch on `has_flag("settled_in")` (the alley's before the campus opens, the mall's after), as `image mc` already switches outfits; with no third file both show the first. The fight screen itself is the combat phase's.
- *Harness (`u2_offcampus.rpy`):* all three states: with no files the five names resolve to today's figures; with a test picture overlaid but the generator not run, still today's figures and no error; with the generator's lines overlaid as well, `lit_sprite` sprites with a shadow; `--dup-globals` is clean both ways; a save made with `mother` on screen loads and shows whichever is installed.

### 8.3 The title, the menus, the engine screens (U6; restyled, never rewritten)

Screen names, parameters, ids and what buttons do stay exactly as they are.

| screen | change |
|---|---|
| `main_menu` | its own picture (5.10); a **Continue** button above Start when a save exists (it loads the newest slot); "How to play" |
| `navigation` | "How to play" |
| `game_menu` | the menu ground (5.10) |
| `file_slots` | each slot reads "Day 9 · Tue · Evening · Cafeteria" from `FileJson`, written by one `config.save_json_callbacks` entry; an old save, which has no such keys, shows its clock time as today. A small delete button on each slot. Still six slots a page. |
| `preferences` | a "Show names" row beside Motion. The words "MOTION", "On", "Off" and "…PORTRAIT" stay, because three harnesses read them. |
| `help` | rewritten as "How to play" (7.5) |
| `choice` | the list moves to the right-hand third of the screen (a style change only), so the face at centre stays visible. Captions that would wrap past three lines at the new width are listed by the harness. |
| `quick_menu` | seven icons with hover labels in place of seven grey words; a small mark while auto-play is on; hidden over `sandbox` and `menu` screens as now |
| `say` | a small "click to go on" mark at the end of a finished line |
| "later build" notes | Hidden from players, shown while `config.developer` is on, **each by the package that owns its file:** U6, in `ui_journal.rpy`: the "n more chapters in a later build" rows (`:661-662`, `:1192`) and `JR_FX_NOTE` (`:95`, "Takes effect in combat from the combat update"). U2, in `ui_map.rpy`: the fifteen Tokyo pins. U8, in its screen blocks (wave 2): `sb_items.rpy:930`, `sb_market.rpy:354`, `sb_board.rpy:1091`. **These stay, on purpose,** because they mark where the build really stops and saying nothing there would be worse: "Written in a later build" on a memory tile or a journal row for a scene that is not written (`sb_memories.rpy:87`, `sb_missions.rpy:525`, `ui_journal.rpy:1131, 2907`), the objective line "The story continues in a later build" (`sb_missions.rpy:868`), the two closing chapter cards (`sb_missions.rpy:1161`, `story_arc1.rpy:466`) and one item's source line (`sb_items.rpy:96`); three of those files are frozen (2.1). `tools/later_ok.txt` (U0a) lists exactly the lines that stay, and `check_content.py --later-notes` greps player-visible text for "later build" and "combat update" against it: a report during waves 1 and 2, a failure at integration. `gui.about` and the version string say this build |
| the window icon | redrawn by `tools/gen_gui.py` (it is a plain red square) |

A new harness, `u2_screens.rpy`, takes the first screenshots that exist of the title, save, load, preferences, help and choice screens.

### 8.4 The phase-1 screens (U8: board, armory, market, card tables, grade card, toasts)

One rule: **the red seal stays as the header's mark; every word button becomes an icon tile with a hover label (Take, Buy, Deal, Hit, Stand); one Close, top right, the same everywhere** (it appears three ways today), on the computer, fishing and the invite picker too. The card games get a one-line legend under the table (what Hit, Stand, Bet and Fold do). The Black Market's screen draws its own painted ground when the file exists. The three "later build" and "combat update" lines in these screens (`sb_items.rpy:930`, `sb_market.rpy:354`, `sb_board.rpy:1091`) are hidden from players (8.3). Screen names, tags, return tuples and every `call screen` / `$ _x = _return` pair are protected and untouched; `chapter_card` and `grade_card` can be inside a save and keep their parameters exactly. This is the first package to wait if a wave runs long: the screens work today.

### 8.5 What does not change in scenes (and waits for the story phase)

Where people stand and how big in a written scene; the hour picture a scene shows; a scene offered away from where it is set; people who speak without being drawn; a motion kit; one-off painted moments; the paper and phone views; the "you" narration; reward lines over the Last Light lamp. Each needs scene lines reworded or re-staged, and the story phase is about to rewrite those same lines. The rooms those scenes name are redone, so every one of them improves without a line changing.

---

## 9. Contracts (what is frozen first)

`docs/UI2_CONTRACTS.md`, started by U0a and final after U0c, with `tools/smoke/u2_contracts.rpy` asserting all of it (each symbol with an example call and its return shape; each function's owning file by `__code__.co_filename`). `u2_contracts.rpy` is not edited after wave 0, and it is in every package's standard set, so **every symbol it asserts exists, at least as a stub, when wave 0 ends** (9.3 lists the stubs).

### 9.1 In the order of what it would cost to get wrong

1. **Home:** `dorm`, `bg your_room`, `default here = "dorm"`, `sb_do_path_dorm` (K1).
2. **The eleven place keys** (fewer if the owner's ruling 2 says so, settled before U0b) **and their image and file names:** `bg <key>`, `bg <key> night|evening`, `images/bg/<key>[_<variant>].png`. A key that reaches a save can never be removed; a room dropped later is a shut door (4.1).
3. **Action ids and labels:** `path_<key>` ×11, `bath_soak`, `bath_sauna`, `pool_swim`, `cards_invite`; the loop calls `"sb_do_" + id`. The activity id `swim_pool` and its label `act_swim_pool`. **The hotspot ids of `SPOT_PLANNED`** (id, place, kind), so layouts can be made before wave 1.
4. **The saved sprite** (K9): the text dump of `lit_sprite`'s tree for one person, recorded.
5. **The light row:** four values, or six with `(shadow lean, shadow stretch)` last; `light_for_place(loc, per)` and `light_for_bg(name)` keep their signatures.
6. **Sidecar shapes** (3.2), `pose_<place>.json`, who may carry `for_rev` (composed pictures and new places only), and the manifest's fields.
7. **The 26 icon names** and which cell of sheet 4 each is in. **The new image names of 5.8** (`bg mall_front`, `mall_hall`, `mall_atrium`, `warehouse`, `annexe`, `site_tunnel`, `site_ward`, `site_platform`, `site_pool`, `site_karaoke`, `club`, `market`, `shibuya night`, `shinjuku night`) and the stand-in copies under `images/bg/standin/`.
8. **`tools/bgs/look.txt`, `keep.txt`, `keep_light.txt`, `stage.txt`** (frozen after batch 1), **`keep_outdoor.txt`** (after batch 8) and **`tools/bgs/campus.json`** (frozen when the owner approves the plan).
9. **`hint_seen`**, the six hint ids, `persistent.show_names`, and the key held to show names (N; `u2_contracts` asserts it is in no `config.keymap` list, and if N turns out to be taken the scaffold picks the next free letter and the help page names it).
10. **The raised budgets** (K11) and **the ledger** (10.3).
11. **The tools' command lines:** `make_redo_workflow.py`, `make_scene_workflow.py`, `install_redo.py`, `check_layout.py`, `check_campus.py`, `art_status.py`, `art_batch.py`, `stage_preview.py`, `sample_light.py`, `campus_plan.py`.

### 9.2 Symbols

| symbol | file | returns |
|---|---|---|
| `world_inside(loc)` | `sb_world.rpy` | the house's key or None |
| `world_pinned(loc)` | | bool |
| `world_home(who)` | | a place key or None |
| `person_now(who)` | (unchanged) | the same dict, **exactly the six keys it has today** |
| `place_access(loc)` | (unchanged signature) | `(bool, reason, short tag)`; a house is always open from one of its own rooms; a room inside a house asks its house first |
| `night_club_bg(key)` | `sb_night.rpy` | an image name (str) |
| `bg_variant(loc, per)` | (unchanged signature) | the attribute or None; None for a stale hour picture |
| `art_rev(stem)`, `art_fresh(stem)` | `art_manifest.rpy` | int (1 when unknown); bool |
| `rule_layout(name)` | `sb_rules.rpy` (unchanged signature) | dict; `{}` for a file whose `for_rev` does not match (a file with no `for_rev` is always read) |
| `path_keep_clear(loc)` | `room_paths.rpy` | list of (x, y) |
| `path_hub`, `path_exits`, `path_neighbours`, `view_slots`, `view_slot_rects`, `view_person_rects`, `view_pose`, `view_motion`, `stage_person`, `char_focus`, `register_hotspot`, `register_place_action` | | unchanged |
| `light_row(loc, variant)` | `lighting.rpy` | a 4- or 6-tuple or None (the measured row when fresh) |
| `view_floor(loc)` | `view_stage.rpy` | list of polygons or None |
| `bath_ok()`, `pool_ok()` | room files | bool |
| `cards_invitable()` | `room_cards.rpy` (a stub from U0c: an empty list) | list of person keys |
| `hint_show(id)` | `ui_hints.rpy` | None (on `tools/none_ok.txt`) |
| screens | | `cards_invite_pick()` returns `("ask", who)` or `("close",)`; `view_others(loc, who)`; `hint_layer()`; `hud_day_card(n=None, weekday=None)` (`cards_invite_pick` and `hud_day_card` are stubs from U0c, appended to `room_cards.rpy` and `ui_hud.rpy`); `main_menu`, `choice`, `say`, `file_slots`, `preferences`, `quick_menu`, `journal`, `sb_map`, `sb_place`, `sb_char` keep name and parameters |

### 9.3 Hooks the scaffold places in files other packages will own

So that no wave package has to touch a file it does not own. Each is behaviour-neutral until its package fills it.

| in | the hook | filled by |
|---|---|---|
| `sb_screens.rpy` | `use hint_layer` in `sb_place`; `use view_others(here, who)` in `sb_char` | U4 (hints), U3 (the others) |
| `ui_map.rpy` | `use hint_layer` in `sb_map` | U4 |
| `ui_icons.rpy` | `icon_words_shown` also reads `persistent.show_names` and the held N key | final in U0c |
| `sb_hotspots.rpy` | while names are shown, an exit wears where it leads and a hotspot its name; an exit tile draws the faces `path_faces(to)` returns (a stub in `room_paths.rpy`: none); `hot_validate` refuses a sidecar point for a hotspot or exit that is neither registered nor in `SPOT_PLANNED`; `SPOT_PLANNED` itself; a registered hotspot may name a `dim` function and `hot_layer` draws it at the dimmed strength while that returns True | final in U0c; U2 fills `path_faces`; U4 registers the planned ids; U5 supplies the card table's `dim` |
| `view_stage.rpy` | the sidecar keys of 6.1 read with today's behaviour as default; `view_pose` reads `pose_<place>.json` first; the gates of 5.5 in `view_fg_path` and `view_pose` | U3 builds on them |
| `lighting.rpy` | four- or six-value rows; `light_row`; the `light.json` lookup in `light_for_bg` | U3 |
| `sb_world.rpy` | the gate in `bg_variant`; `WORLD_VARIANTS` and its registration | U1 |
| `sb_night.rpy` | `pool_swim` and `swim_pool` in `NIGHT_REST_BLOCKS`; `night_club_bg` | final in U0c (U9 adds the one line that calls it) |
| `room_bath.rpy`, `room_pool.rpy` | the three actions registered with `when="bath_ok"` / `"pool_ok"`, both returning False, and their labels (`sb_do_bath_soak`, `sb_do_bath_sauna`, `sb_do_pool_swim`, `act_swim_pool`) as `return`: the ids exist for `night_validate` and the activity's label exists for U4's row | U5 |
| `room_cards.rpy`, `ui_hud.rpy` | appended at the end of each: `cards_invitable()` returning `[]`, an empty `screen cards_invite_pick`, an empty `screen hud_day_card(n=None, weekday=None)` | U5; U4 |
| `bg_placeholders.rpy`, `sb_board.rpy` | the new image names of 5.8 with their stand-ins, the stand-in copies, the board's job-to-picture column | final in U0c |
| `gui.rpy` | the two picture lookups (5.10); the `gui.sys_` tokens | U6 |
| `jjk_defs.rpy` | the guarded stand-in block | U7 |
| the new-day hook registry | nothing is placed: `world_welcome_check` and the day card register themselves from their own files | U1, U4 |

No hook is needed in a frozen file: every new action is a registered place action reached through the loop's existing `call expression "sb_do_" + _r[1]`.

---

## 10. Work packages

```
Before wave 0: the owner's rulings 2, 3 and 4 (whose rooms; the budget; the cloud plan)
Wave 0  (in turn, in the owner's folder on ui2; U0d may run beside U0b and U0c, it touches no game file)
        U0a the safety net  →  U0b my room moves  →  U0c the scaffold        U0d art tools and the bible
                                                                              → checkpoint A
        art: batch 0 (free), then batches 1 to 6, beside wave 1
Wave 1  (six parallel worktrees, ~/Desktop/JJK_worktrees/u2_<n>, branched from ui2 after checkpoint A)
        U1 world and people · U2 the map and the doors · U3 stage and blending
        U4 things to do · U5 baths, pool, invite · U6 menus and system screens
                                                                              → trial merge → checkpoint B
        art: batches 7 to 13, beside wave 2
Wave 2  (two parallel, then one alone)
        U7 the people as drawn · U8 the older screens
        then U9 story files (alone)                                           → checkpoint C
        art: batches 14 to 24
Wave 3  U10 integration                                                       → checkpoint D
```

Eleven code packages and one standing art-install role (L). The split is by risk, not by size: U0b is small and alone because it moves the bedroom; U9 is alone because it edits story files.

**Standard acceptance for every package** (PHASE2 2.4, with this overhaul's additions): (a) lint clean, no `VALIDATE:` line; (b) `check_content.py --all` shows no new finding; (c) its own harness passes through `tools/smoke.sh`; (d) `u2_contracts`, `p2_contracts`, `core_flow`, `phase1_all` and `phase2_all` pass, and every harness in its row of 10.1, apart from ledger lines handed off by name (K13); (e) **the save set loads the same:** the owner's eleven saves and the six made saves, by `tools/load_all_saves.sh --from <snapshot>`, each row SAME; (f) `tools/check_campus.py` and `tools/check_layout.py` pass once U0d has landed, by the rule of 5.2: the plan, 4.8's targets and every test sidecar in full; a yard or map still at revision 1 is listed as waiting for its batch, not failed; (g) a `zz_worst` screenshot of each full screen it owns; (h) a five-line "what changed, what to look at" note for the owner. Worktrees get copies of the owner's `.rpyc` and never copy back.

### 10.1 File ownership (within a wave every file under `game/` and `tools/` has one owner)

| owner (wave) | game files | tools, harnesses, docs |
|---|---|---|
| **U0a** (0) | none | `tools/check_content.py`, `tools/prefixes.json`, `tools/smoke/_lib.rpy`, `tools/smoke.sh` (the pointer lock, K13), `tools/later_ok.txt`, `tools/smoke/assets/ui2_saves/` (the six made saves), `tools/load_all_saves.sh` (a `--from <folder>` option), `tools/review_pack.sh`; the baselines (`baseline_u2.json`, `baseline_story_names.json`, `baseline_sprite_tree.txt`, `baseline_shots/ui2/`); `docs/UI2_PINS.md`, `docs/UI2_CONTRACTS.md` (first draft), `docs/load_report_ui2_wave0.txt`; for this sitting only, the picture-pinned and count-pinned lines of `p2_paths`, `p2_view`, `p2_map`, `p2_hud`, `p2_rooms`, `p2_contracts`, `wp1_world` |
| **U0b** (0) | `sb_world.rpy`, `room_paths.rpy`, `ui_map.rpy`, `bg_placeholders.rpy`, `ui_icons.rpy` (the 26 icon rows) | `tools/icons/sheet_4.txt` (new; `sheet_3.txt` is not touched), `tools/make_icon_workflow.py`; `wp1_world.rpy`, `p2_map.rpy`, `p2_paths.rpy`, `p2_saves.rpy`, `p2_night.rpy`, `u2_home.rpy` (new) |
| **U0c** (0) | `sb_world.rpy`, `room_paths.rpy`, `ui_map.rpy`, `bg_placeholders.rpy`, `art_manifest.rpy` (new), `sb_rules.rpy`, `sb_hotspots.rpy`, `ui_icons.rpy` (`icon_words_shown` only), `view_stage.rpy`, `lighting.rpy`, `sb_night.rpy` (one set), `gui.rpy`, `game/gui/menu_ground.png`, `jjk_defs.rpy`, `sb_screens.rpy` (two hook lines), `sb_board.rpy` (the job-to-picture column only), `game/images/bg/standin/` (five copies), stubs `room_bath.rpy`, `room_pool.rpy`, `ui_hints.rpy`, and stubs appended to `room_cards.rpy` and `ui_hud.rpy` (9.3) | `u2_contracts.rpy` (new), the harnesses of U0b's row for the other seven places, `u2_home.rpy`; `docs/UI2_CONTRACTS.md` (final) |
| **U0d** (0) | none | `tools/bgs/` (`look.txt`, `keep.txt`, `keep_outdoor.txt`, `keep_light.txt`, `stage.txt`, `campus.json`, `CAMPUS2.md`, `campus_plan*.png`, `keep/` for batches 0 and 1, first lines of the old style files), `tools/art/batches.json`, `tools/py_art.sh`, `campus_plan.py`, `check_campus.py`, `make_scene_workflow.py`, `make_redo_workflow.py`, `install_redo.py`, `check_layout.py`, `check_prompts.py`, `stage_preview.py`, `sample_light.py`, `art_status.py`, `art_batch.py`, `test_art_tools.sh`, `layout_sheet.py` (the new keys; its lanes read from the dump `p2_contracts` writes, since its own copy is out of step); one shared reader of that dump in place of the regular expressions in `make_fg.py`, `install_pose.py`, `make_pose_workflow.py`; and in those two pose tools the whole of 5.12's tooling (the height hint and wording, the order check, the manifest row, the `pose_<place>.json` box, the overlap refusal); `docs/ART_UI2.md` |
| **U1** (1) | `sb_world.rpy` | `wp1_world.rpy`, `u2_world.rpy` (new) |
| **U2** (1) | `ui_map.rpy`, `room_paths.rpy` | `p2_map.rpy`, `p2_paths.rpy`, `u2_map.rpy` (new) |
| **U3** (1) | `view_stage.rpy`, `lighting.rpy`; `game/layout/view_*.json` and `tools/fg/*.json` for the rooms redone in place | `tools/make_pose_workflow.py` (the `POSES` table only; the tooling is U0d's and is done), `make_fg.py`; `p2_view.rpy`, `u2_blend.rpy` (new) |
| **U4** (1) | `sb_screens.rpy`, `room_spots.rpy`, `sb_activities.rpy`, `room_library.rpy` (words only; never the shelf menu), `ui_hints.rpy`, `ui_hud.rpy`; `game/layout/hot_*.json` for the rooms redone in place (their hotspot points and their exits, 7.3), with their door boxes in `tools/bgs/keep/` by hand-off to L | `p2_rooms.rpy`, `p2_hud.rpy`, `wp7_ui.rpy`, `u2_things.rpy` (new) |
| **U5** (1) | `room_bath.rpy`, `room_pool.rpy`, `room_cards.rpy` | `p2_cards.rpy`, `u2_rooms.rpy` (new) |
| **U6** (1) | `screens.rpy`, `gui.rpy`, `options.rpy`, `ui_journal.rpy` (its own hidden notes only: 8.3 lists whose are whose), `game/gui/*` except the title and the menu ground | `tools/gen_gui.py`; `wp8_journal.rpy`, `u2_screens.rpy` (new) |
| **U7** (2) | `jjk_defs.rpy`, `sb_memories.rpy` (two data rows) | `tools/keysprite.py` (height rows for the four people and the three curses), `fix_edges.py`, `gen_sprite_defs.py`, `tools/chars/prompts/`; `wp9_prologue.rpy`, `u2_offcampus.rpy` (new) |
| **U8** (2) | the screen blocks of `sb_board.rpy`, `sb_items.rpy`, `sb_market.rpy`, `room_cards.rpy`, `sb_grades.rpy`, `room_computer.rpy` and `room_fishing.rpy` (Close only), with the three hidden notes of 8.3; the toast styles in `ui_hud.rpy` | `u2_older.rpy` (new) and the screenshot lines of `p2_gear`, `wp4_board`, `p2_cards` |
| **U9** (2, alone) | `ch4_mission.rpy`, `missions_arc1.rpy`, `story_arc1.rpy`, `sb_night.rpy` (one line), `events_arc1.rpy`, `events_activities.rpy`, `events_intimate.rpy`, `events_romance.rpy`, `events_stand.rpy` | `u2_names.rpy` (new), `wp10_chapters.rpy` |
| **U10** (3) | everything, the frozen files included | `ui2_all.rpy`, `u2_saves.rpy` (new); `docs/PLAYTEST.md`, `docs/ART_UI2.md`, `tools/README.md`, this design ("As built"), `docs/UI_OVERHAUL_2.md` (the rulings), `docs/load_report_ui2.txt` |
| **L, the art-install role** (any) | `game/images/**`, `game/gui/title.png` and `menu_ground.png`, `game/jjk_sprites.rpy` (generated), `game/layout/pictures.json`, `light*.json`, `pose_*.json`, `area_*.json`, `map_campus.json`, and the `hot_`, `view_` and `tools/fg/` files of composed pictures and new places | `tools/bgs/keep/**`, `tools/bgs/refs/**`, the status in `tools/art/batches.json` |

L never touches a `.rpy` file by hand or a harness (K2, K3), so it runs beside any wave; K15 leaves no overlap (pose boxes have their own file, and an in-place install rewrites no `hot_` or `view_` file).

### 10.2 The packages

#### U0a · The safety net (no game file changes)

1. Back up `game/*.rpyc`, `game/saves/` and `~/Library/RenPy/JJKgamemd-1788928056/` to `~/Desktop/JJK_backup_ui2_<date>/`. **Copy the owner's eleven saves into a snapshot folder there:** the owner keeps playing, and their autosaves are the only saves that rest on story menus.
2. Run `load_all_saves.sh` on the untouched tree; commit the report.
3. **Make six more saves from the untouched tree,** in a scratch copy, by harness: standing in my room; in the garden one step after walking out of my room; on the map with the Dormitories area open; on the first line of dialogue in the Common Room with the foreground and a sprite up; in the prologue with `mother` on screen; on a chapter card. They join the snapshot and are committed under `tools/smoke/assets/ui2_saves/` (they hold no personal play), so every package's acceptance (e) can be rerun from the repository; the snapshot folder's path and a checksum for each of the owner's eleven go into `docs/load_report_ui2_wave0.txt`. They are the saves this overhaul is most likely to hurt, and the owner does not happen to have them.
4. The baselines, from today's tree: place actions for every place and period; who is where for every place, period, weekday and weekend; the exit graph; every statement name of the story files; the text dump of `lit_sprite`'s tree; screenshots of the place view, the person view, the map's two levels and the title.
5. `tools/prefixes.json`: rows for `art_manifest.rpy` (`art_`), `room_bath.rpy` (`bath_`), `room_pool.rpy` (`pool_`), `ui_hints.rpy` (`hint_`), and new prefixes for `jjk_defs.rpy` (`standin_`), `screens.rpy` (`sys_`), `gui.rpy` (`gui.sys_`); one exception for the label `act_swim_pool` in `room_pool.rpy` (the loop calls an activity by `"act_" + id`). Then frozen again.
6. **K3, once:** `p2_paths.rpy:631` (the copy of `PATH_KEEP_CLEAR`: equals the live hotspot points), `:642` (the Courtyard's exit point: clear of the machine and inside the frame), `:316, :483, :1089` (the garden's "exactly 7": at most 7 and equal to its table), `:393` and `p2_map.rpy:350` (24: `len(LOC_ORDER)`), `:717` (30 yard exit labels: counted from the table), `:866-888` (the Mountain box: from the file); `p2_map.rpy:336-341` (press `row_<loc>` for every place: for every pinned place), `:351-352` (the budgets of K11); `p2_view.rpy:510, 587, 769, 775` (slots compared with whatever `view_slots` reads), `:712` (14 pose rows: every row passes the schedule check), `:726-740` (the foreground file lists: "every polygon file has its cut for every fresh hour picture of its room"); `p2_contracts.rpy:1052` (88: the count the sheets hold); `p2_rooms.rpy:83` (the fifteen are present; more are allowed).
7. `check_content.py --layout-files` (allowed keys and shapes of every `game/layout/*.json`).
8. `docs/UI2_PINS.md`, the ledger (10.3): each line found by grep, then confirmed by running its harness in a scratch tree with a stub of the change.
9. `tools/review_pack.sh <package>`.
10. **The pointer lock** in `tools/smoke.sh` (K13): a harness on the pointer list waits for a machine-wide lock, and refuses with one line while a window of this game is open. With six worktrees in wave 1 and `p2_contracts` in every package's standard set, collisions are otherwise certain and each looks like a real hover failure.
11. `tools/later_ok.txt` and `check_content.py --later-notes` (8.3).

*Acceptance:* the tree is byte-identical under `game/`; every harness in `tools/README.md` gives the verdict it gave before; each rewritten check fails when its sidecar is deliberately broken; the seventeen saves load the same.

#### U0b · My room moves (alone)

It starts only after the owner's ruling 2 (whose rooms): a room the owner does not want is not built here or in U0c, and the tables, counts and budgets of this plan shrink by it. Tasks: 4.4, steps 1 to 5; `boys_dorm`, `yuji_room`, `megumi_room` and `senpai_room` as places on stand-ins (the checklist of `map_places.md` 3.3, row by row); `WORLD_INSIDE`, `WORLD_PINLESS`; the Night cells for Yuji (weekdays), Megumi, Panda and Toge, and Yuji's weekend Night in the garden; the Dormitories view with six pins (on today's area picture the new pin is placed clear of my room's; 4.8's points arrive with the new map); the whole icon table (26 rows with kanji stand-ins and their words) and sheet 4; the ledger's lines for `p2_paths.rpy:307, 439-441` and `p2_saves.rpy:452-457` ("the exit in my room walks to the Dormitory Garden" becomes the corridor), `p2_paths.rpy:448` (the garden's exit label "To My Room" becomes "To the Boys' Dormitory") and `p2_paths.rpy:1003-1014` (Panda's Night: "in the garden" becomes "in the shared room").

*Acceptance:* the standard set; and `u2_home.rpy`:
- from every place at Night, "Go to bed" ends in `dorm` with the right carry line; a Gojo night, a night out and the Sun Mall's end do too;
- on foot: garden → corridor → my room, and back, no time spent; from my room every place is reached by exits alone;
- by map: Dormitories → `row_dorm` walks to my room (`p2_saves.rpy:467-476` passes unedited);
- the garden has exactly seven exits;
- save and load, and roll back through, a walk from the garden into the corridor into my room (three saves, each loads on its statement);
- `label path_walk` and all 24 existing `sb_do_path_*` labels are textually what they were (that block of `room_paths.rpy` is compared with the baseline);
- the seventeen saves load the same; for the "one step after walking out of my room" save, rolling back lands in my room; the owner's auto-1 (on the map, in my room) and 1-1 play on to the next morning (`p2_oldsave`, run, not read).

#### U0c · The scaffold (the game looks and plays the same in every old place)

Tasks: the other seven places on stand-ins, with exits both ways, labels, pins placed clear of their neighbours on today's area pictures, doors (4.1, 4.2 as far as "open while its owner is in", "the house first", the pool at Night) and the rest of 4.3's cells; `WORLD_HOMES`, `WORLD_VARIANTS` and its registration; the manifest reader and the four gates (5.5); `rule_layout`'s `for_rev`; `path_validate`'s spacing on applied points; `path_keep_clear`; hover-label sides from `tips` or from position; four- or six-value light rows and the `light_` and `light.json` readers; the sidecar keys of 6.1 read with today's behaviour as default; "Show names" and the held N key in `ui_icons.rpy` and `sb_hotspots.rpy`; `SPOT_PLANNED` and the generic `dim` state in `sb_hotspots.rpy`; `pool_swim` and `swim_pool` in `NIGHT_REST_BLOCKS`; `night_club_bg`; "a house is always open from one of its own rooms" in `place_access`; the title and menu-ground lookups and the copied menu ground; the five stand-in copies, every new image name of 5.8 with its stand-in, and the board's job-to-picture column; the guarded stand-in people (8.2); `view_pose` reading `pose_<place>.json`; the hooks and stubs of 9.3 (the baths', the pool's and the hints' frozen shapes; the three new actions registered but closed, with labels that only `return`; the card invite's and the day card's stubs); the old yards' code points left on today's sides (K12); a test that settles D31 (is a pose kept on the person view screen-only). Until wave 1 the new rooms are open and offer nothing to do.

*Acceptance:* the standard set; from `dorm` every one of 35 places is reached by exits; `place_actions` for the 24 old places equals the baseline apart from exits; with no manifest and no new sidecar, screenshots of an untouched room (place view and person view), the map's first level and the title are pixel-identical to U0a's; with an overlaid manifest and files, each gate falls back as K7 says and a mismatched `for_rev` is ignored and reported; a save made in each new place reloads there; the `mother` save shows `mother`; `p2_paths.rpy:739-740` passes unedited on the schematic exits; lint reports a `TIME_VARIANT` cell with no image and a stale sidecar point, and accepts a point for a planned hotspot; lint is clean with `pool_swim` in `NIGHT_REST_BLOCKS` (the stub registers it); a board job shows its site's stand-in and the board's validator is clean; each new name of 5.8 resolves to its stand-in without the file and to the file with a test overlay; the stand-in people in all three states of 8.2; a pose installed by test overlay on a revised picture shows; with no icon art, every exit to a yard draws its area's icon exactly as today and no column's cap changes; **walk into Nobara's room on a weekend Morning, Wait to Evening, walk out: the exit works**; the names key is in no `config.keymap` list; `make_icon_workflow.py --names` agrees with `ICONS`. *Harness:* `u2_contracts.rpy`.

#### U0d · Art tools and the campus bible (no `.rpy` change)

Tasks: everything in its row of 10.1; `campus.json` filled from 5.2; the plan drawn; 4.8's pin targets printed from it; the look lines of the schoolhouse, the gateway and the training hall read off the chosen Courtyard; the window walls of the four installed rooms read off their pictures; the pose tooling of 5.12; keep lists and layout for batch 0's four pictures; the workflows and notes for batches 1 to 4; `docs/ART_UI2.md` (the owner's page: the hand-off habit of `ART_PHASE2.md`, the verdict words PASS, LOOK, REFUSED and what each means).

*Acceptance:* `tools/test_art_tools.sh` passes its synthetic cases and gives the right answers on the sixteen test renders (5.4); `install_redo.py --dry` passes both third-test renders and names what is gone on the second test's emptied Common Room; **a second redo of `look3_dorm_common_keep` run through `install_redo.py` passes step 5** (sharpness is against revision 1); the eight day and hour pairs the game has today are run through `--against` and the relight thresholds recorded; `check_campus.py` **passes in full on the plan, on 4.8's target pins and on the window lines before the drawing goes to the owner**, fails its negative test (two exits swapped in a composed test sidecar), and lists as "waits for batch N" the facts the new pictures must fix (today's Training Yard sides, the two offices on the Staff map); every prompt batches 1 to 4 need is generated and passes `check_prompts.py`, and no relight prompt contains "Keep the time of day"; `install_pose.py` refuses two overlapping test boxes and writes a manifest row; `stage_preview.py` draws the Common Room at evening with three people and matches a game screenshot of the same state closely enough to judge by eye; `check_layout.py` passes on the layouts written for the chosen Courtyard and Library; no file under `game/` changed.

#### Wave 1

| package | tasks | harness and its key checks |
|---|---|---|
| **U1 · World and people** | the girls' welcome (4.2); "at home" in `person_now`'s name; Gojo's Night; a room inside a house asks its house first; the door lines that say where someone is; the Library's and the Dormitories' words; `wp1_world`'s lock sentences in the same commit | `u2_world.rpy`: the Night column, person by person, weekday and weekend; nobody is in two places; a friend's room opens exactly when its owner is in or with me, and never locks me in (the exact case: into Nobara's room on a weekend Morning before any welcome, Wait to Evening, walk out to the corridor and on to the garden; and the same after entering with her as companion); the corridor's rule comes first, by "Go there" too; the flag is set once at Bond 30 and never before; `person_now` for someone at home names the house, offers no walk, and has exactly six keys; Gojo is on no place at Night on any of 60 days, and on the ridge on his night; the Common Room is empty at Night |
| **U2 · The map and the doors** | a house's pin and its exit tile carry the people inside; dim faces with the door mark for people at home; the Mountain box and anchor nudges from `map_campus.json`; the tint by hour; Tokyo's dead pins hidden (its share of 8.3's notes) and its markers restyled; an empty marker at half height; the new budgets | `u2_map.rpy` (pointer-dependent: run alone): six markers; at most six pins and eighteen words in every area with the real names; pressing every pinned place returns `("go", loc)`; `row_dorm` from a save made on the map; no pin overlaps and no hover label covers a pin, for the code defaults and for test sidecars at 4.8's targets; a painted test map with its sidecar moves the box and a missing one leaves today's; a person in a pinless room shows on the house's pin and on the area marker |
| **U3 · Stage and blending** | section 6: rows 2, 3, 5 to 10 of 6.2; floor, scale and slots for the 17 rooms redone in place (authored on today's pictures); the new polygons on in-place rooms (Gojo's office; Yaga's waits for its desk); the pose's caption rule; `POSES` re-picked, with a named seat for each of a pair (the pose tooling itself is U0d's); captions under name tags while names are shown; the cast shadow last. Its `view_` files carry no `for_rev` | 6.5; and a pose installed on a revised picture shows, from its `pose_` file |
| **U4 · Things to do** | captions for every cell (7.1); the looks and the moved actions of 7.3, registered under exactly the ids of `SPOT_PLANNED` (points for rooms redone in place measured now; lines for every look); **each in-place room's exit put on its painted door, or at the bottom of the picture where the room shows none** (7.3); the activity places of 3.1 and the `swim_pool` row; the six hints; the day card. Its `hot_` files carry no `for_rev` | `u2_things.rpy`: every routine cell has its own caption; every one of the 35 places has at least one thing to click that is not an exit; every action is in the picture or in the column, never both, never neither; every id in `SPOT_PLANNED` is registered and nothing else is; every indoor exit of an in-place room is on a door box or in the bottom band; "Swim together" is offered at the pool with the three who go there and at the river with the two who stay; a look works at Night and costs nothing; each hint shows once, survives save and load, and never shows in a replay or to a save past day 2 (the sixth excepted); the column still fits in every place and hour (`p2_hud` section 3b, alone); all new text is first person |
| **U5 · Baths, pool, invite** | 4.7 and 7.4, filling U0c's stubs (the labels keep their names); `label act_swim_pool(who)` with its own pool lines; the card table's `dim` function (the drawing is U0c's hook) | `u2_rooms.rpy`: one bath a day across both rooms, an hour spent, closed at Night, allowed on a rest day, the numbers of 4.7; the pool's numbers equal the river's and it is closed on a rest day and at Night; "Swim together" at the pool shows the pool, never the river, and gives `act_swim`'s Bond; an invited person is in the Common Room this hour and back in their routine the next, on the map and in the journal too; three at the table at most; no teacher is offered; nothing is offered at Night; a save on the picker reloads on it; rollback through an invite restores the pin; a save made in the sauna loads |
| **U6 · Menus and system screens** | 8.3 (of the hidden notes, only the journal's) | `u2_screens.rpy`: Continue loads the newest save and is absent with none; a new save's slot reads its day, hour and place and an old one its time; the Preferences words the harnesses read are still there; every text style is still on a font group; the choice list leaves the rectangle of a centre face clear with three choices; first screenshots of title, save, load, preferences, help, choices |

Hand-offs expected in wave 1, by ledger: slots moved by U3 change results in `p2_rooms`, `p2_hud` and `p2_paths` (their numbers assumed today's stage); captions changed by U4 are read by `wp7_ui`.

#### Wave 2

| package | tasks | harness |
|---|---|---|
| **U7 · The people as drawn** | 8.2 (the guard is already in the scaffold; here the curse switch and the rest); the two memory rows; prompts, height rows and `BASES` rows for the four people; `HEIGHT_CM` rows for the three curses and their green-screen prompts (5.11) | `u2_offcampus.rpy`: 8.2's checks in all three states; the Last Light lamp's glow sits within 12 px of a test alley's lamp; `wp9_prologue` passes; no story file changed (`u2_names` reports zero differences) |
| **U8 · The older screens** | 8.4; the three hidden notes in its screens (8.3) | `u2_older.rpy`: none of the three notes shows to a player and all three show with `config.developer` on; every return tuple each screen gave before, it still gives (driven through the existing harnesses); one Close per screen; the market draws its ground with a test file and today's picture without; a board job shows its site's stand-in; `zz_worst` of each |
| **U9 · Story files (alone, after U7 and U8 have merged)** | 8.1, as two commits | `u2_names.rpy`; the seventeen saves SAME; lint; each swapped scene shows its stand-in today and its picture with a test overlay; the first spoken line of each `ev_*` scene carries a face |

#### Wave 3 · U10 integration

Anything in the ledger still open; `ui2_all.rpy` (a fresh game through the prologue, then thirty days on the new campus by a driver that walks into every one of the 35 places by exits and by the map, sleeps in my room, spends a night in each kind of Night place, soaks, sits out the sauna, swims, invites, and loads a save in each new place; then the owner's 1-1 played on for three days); `u2_saves.rpy` (save and reload in the corridor, in a friend's room at Night, on the invite picker, in the sauna, with a kept foreground in dialogue); `docs/PLAYTEST.md` rewritten for this overhaul with a stand-ins list that is complete this time (AUDIT B19); `docs/ART_UI2.md` final; `tools/README.md`; the final load report; "As built" notes in this design.

#### The art sittings (L)

One sitting per batch of 5.13, in the owner's folder, never while a wave is merging. A sitting more than a week after the last starts with the canary of 5.2. For a room redone in place: `install_redo.py`, which recuts foregrounds, measures the light rows and updates the manifest; one commit per room set (the day picture with its hour pictures). For a composed picture or a new place: the layout sitting of 5.6, started when the owner says which version they chose, picture and numbers in one commit, every planned hotspot placed. Each sitting ends with lint, `test_art_tools.sh`, `check_layout.py`, `check_campus.py`, `art_status.py --check`, the place's layout sheet and stage sheet for the owner, and `p2_view`, `p2_rooms`, `p2_paths` (the last three alone). A code package never writes a real sidecar for a composed picture or a new place: it tests with its own under `tools/smoke/assets/<harness>/`.

### 10.3 The ledger: harness lines this overhaul is known to change

Written out in full in `docs/UI2_PINS.md` by U0a. The known rows (lines U0a turns into rules, 10.2, are not repeated here):

| harness line | pins | changed by | fixed by |
|---|---|---|---|
| `p2_paths.rpy:305-307, 439-441` | "the exit in my room walks to the Dormitory Garden" | U0b | U0b |
| `p2_saves.rpy:452-457` | presses `hot_go_dorm__dorm_yard`, asserts `here == "dorm_yard"` | U0b | U0b |
| `p2_paths.rpy:448` | the garden's exit `hot_go_dorm_yard__dorm` reads "To My Room" | U0b (the exit is now to the Boys' Dormitory) | U0b |
| `p2_paths.rpy:1003-1014` | at Night `char_location("panda") == "dorm_yard"`, and what can be started with him there | U0b (his Night is the shared room) | U0b (the same comparison, against `senpai_room`) |
| `p2_saves.rpy:467-476` | `area_dorms`, then `row_dorm` | nobody: it keeps passing because my room keeps its pin; listed so nobody "fixes" it | – |
| `wp1_world.rpy:244-246` | `places_in("dorms")`, `places_in("staff")` | U0b, U0c | U0b, U0c |
| `wp1_world.rpy:296-333` | who is in the garden at Night (Yuji and Panda, every day) | U0b | U0b |
| `wp1_world.rpy:329-334` | the Common Room is empty at Night | unchanged; listed so nobody breaks it | – |
| `wp1_world.rpy:335` | "only the cafeteria and the riverside hold five" | U0c (the pool) | U0c |
| `wp1_world.rpy:352-378` | the lock sentences | U0c, U1 | U0c, U1 |
| `p2_paths.rpy:996-1002` | the list of people who moved | U0b, U0c; U4 (`swim_pool`) | U0b, U0c (people added, except the three who left the river; no exception list); in wave 1 the three are added and the check counts `swim_pool` as `swim` continued, an edit U4 proves in scratch and hands to the owner of `p2_paths` that wave (U2) |
| `sb_activities.rpy:278` and `TRAIN_TOGETHER` | the choice order and the shared-training table name `swim` | U4 | U4 (`swim_pool` beside `swim` in both) |
| `p2_paths.rpy:1028` | the Courtyard on a weekday afternoon is Yuji and Nobara | unchanged | – |
| `p2_night` (29 literals) | every night ends in `dorm` | unchanged; rerun | – |
| `p2_map` hover and overlap sweeps; `p2_hud` section 3b; `p2_paths` sections 3 and 5 | pins, exits and labels on the pictures | every composed picture | rerun alone at each layout sitting; they check rules after U0a, so no line is edited |
| `p2_rooms.rpy:83-93` | the fifteen hotspots, room by room | U4 (the looks, the moved actions) | U4 |
| `wp0_stubs.rpy:341-353` | `place_actions("dorm")`, `("courtyard")` shapes | unchanged (new actions are registered ones) | – |
| `wp8_journal.rpy:516-519, 969-974`; `p2_contracts.rpy:1499-1508` | the Preferences rows' words | U6 (a row added, none renamed) | U6 |
| `make_icon_workflow.py`'s own check | the sheets equal `ICONS` | U0b | U0b |

### 10.4 What the owner sees after each step, and where it can stop

| step | the owner sees | if it stopped here |
|---|---|---|
| U0a | nothing (by design) | the game is today's game, with a safety net |
| U0b | my room is down a corridor; three friends' rooms on borrowed pictures, with their owners in them at Night | a complete small change |
| U0c, U0d | seven more places to walk into; the teachers on campus at Night; one drawing of the campus | the same, on stand-ins; four doors float on the old yard pictures |
| batch 0 | the look, in the game, on four places | four places new, twenty old: uneven, nothing broken |
| batches 1, 2 | five rooms whole by day and after dark; Nobara painted on the sofa | |
| batches 3 to 6 | the yards and the maps: the campus as one place | interiors are still mostly the old look |
| wave 1 | people behind a shut door still show on the map; standing spots, shadows and light everywhere; looks, the invite, the soak, the swim; hints, Continue, save slots | each package is whole without the others |
| batches 7 to 13 | every place new, by day and after dark; the new places as themselves; two painted people as a test | the campus is done |
| wave 2 | one Close; the last notes hidden; faces in the character scenes; the mall and the Nade sites on their own names | U8 and U9 can each be skipped with no effect on anything else |
| batches 14 to 24 | the other poses; the prologue, the mall, the board, Tokyo; the title; mouths; the four people and the curses | any of these can be bought in any order, or not at all |
| U10 | the record brought up to date; everything played end to end | |

### 10.5 The checkpoints

| | played from the launcher | the owner is asked |
|---|---|---|
| **A** (after wave 0; about 15 minutes) | Load an old save: it is where it was. Walk garden → Boys' Dormitory → my room; sleep; wake. Walk into each new place on its stand-in. At Night visit Yuji, Megumi, the second years and the Teachers' Dormitory. A new game to the Courtyard. | Ruling 1 of section 0, looking at the drawing of the campus (rulings 2 to 4 were given before building began). Is one more click to my door on foot fine? |
| **B** (after wave 1 and batches 0 to 6; about 30 minutes) | Walk the six yards without the map: does each door lead where it looks like it leads? Open the map: find someone at Night. A day and a night: soak, swim, ask Toge to cards, click one look in each area, visit a friend at Night, go to bed from a friend's room. A new game's first morning with the hints. Watch Yuji talk. | Does the campus feel like one place? Are people standing *in* the rooms? Yuji's mouth: make ten more the same way? The caption and look lines (one reading list). Does Nobara on the sofa sit right beside the others? |
| **C** (after wave 2 and batches 7 to 13; about 30 minutes) | Every place, day and after dark (a list of 35 with a tick box). Six rooms with four people in them. Utahime painted at her desk and Megumi at the Library's table, each beside standing people. Two character scenes with faces. The title, a save, the choices at the side; the board and the armory. | The pose test is in front of you: buy the other nineteen? Any picture to run again? |
| **D** (after U10 and whichever of batches 14 to 24 are made) | The prologue from New Game. The Sun Mall. One board job. A day trip and a night out. The poses beside sprites. Mom, Dad, Kurose and Nade. | The review of titles, captions and numbers (one list). |

### 10.6 Cut lines

**If a package fails its acceptance twice** (PHASE2's D51), it is cut at its line and the rest ships; the owner is asked before anything they decided is cut:

- U8, the older screens: all of it. They work as they are.
- U9: the faces (commit 2), then the scene swaps (commit 1).
- U3: the cast shadow; then the per-slot light; then the shadow's lean (opacity and stretch stay); then the others staying on the person view. Never cut: floor, size and measured light.
- U4: looks cut to two lines each; then to one look a place.
- U6: the quick menu's icons; then the choice list's move.
- U2: the tint by hour; the half-height marker.
- U5: nothing (the four places the owner named and the invite are the owner's).

**If the art budget is cut,** section 0's order: blink and talk; poses 19 to 22; the club, the market and the job sites; the night pictures of three yards; Nobara's and Maki's rooms (each becomes a shut door by 4.1's procedure: the key, the label and the exit stay, the door says "Her door's shut.", and their Night cells go back to `girls_dorm`; no picture is bought). None of these cuts blocks another picture (D22). Then a second candidate for every composed picture (halves their cost; the owner takes what comes or reruns one).

**Never cut without the owner:** the four places they named, the Boys' Dormitory and my room in it, the invite, the campus bible, the redo of every existing place, the missing backgrounds, the title.

### 10.7 Risks

| # | risk | what is done about it |
|---|---|---|
| 1 | An old save no longer loads where it was saved | No label deleted, no variable renamed, no migration; every package loads seventeen saves (eleven the owner's, snapshotted first; six made on purpose where this overhaul changes things); new labels are appended; the loop is not edited at all |
| 2 | Moving my room strands a save, a night or the walk home | The key never changes (K1); every "home" is a teleport by name; the move is one small package, alone, proved on stand-ins before anything depends on it; 4.4's table is its test list |
| 3 | The house rule in the exit validator breaks walking somewhere | It is in U0b, alone, with the reachability check from `dorm`, the full hover sweep and `phase1_all`'s thirty days before any wave starts; the frozen contract functions keep their signatures |
| 4 | The editor does not follow a layout drawing, so the yards and maps disagree with the plan | Batch 3 is two yards and one map, judged by a stated pass rule before the other three yards and twelve map renders are bought; 5.2's table says what follows each failure, down to changing the bible to match the picture for the two yards that cannot be redone in place, and drawn maps; the look lines and `check_campus.py`'s side and order rules hold either way |
| 5 | A redo in place quietly moves something by a few pixels | `install_redo.py` refuses on windows round every registered point; `install_bg.py` is never used for a redo; the proof can be rerun from git at any time |
| 6 | "Clean" empties a room, or "real" dirties one | `KEEP` + `LOOK3`, proven on two indoor rooms by day; the three variants that are not proven (outdoors, a relight, a named addition) each have a named first test and a fallback (5.1); the banned-word check; the keep lists, the vanished-object refusal and the floor measure |
| 7 | Between batches a room shows old-look dependants | K7's four gates, tested with overlays; foregrounds recut by the installer; a day picture and its hour pictures in one sitting, because scenes and memory rows that name an hour picture bypass the gates (the one known gap, the Common Room for one sitting, is in K7) |
| 8 | A composed picture puts something where the screen cannot use it | `stage.txt` in every compose prompt; a picture is installable only with a layout that passes `check_layout.py`; two candidates wherever there is more than one exit or a foreground, and a rerun from the allowance for a one-exit room that cannot pass |
| 9 | Turning harness pins into rules hides a real regression | U0a must show identical verdicts on the untouched tree and one negative test per rule; the hover sweeps run alone at every layout sitting |
| 10 | A yard's icons overflow the column when people stand in front of its doors | No yard goes above seven exits; 4.6's rule is counted by the tool before a yard is installed and by the unedited harness line after; "Train at the posts" falls back to a look |
| 11 | The six-pin, eighteen-word Dormitories view crowds the map | One more pin than today, on a picture composed for six buildings; the overlap and hover sweeps on the planned points in wave 0 and on the measured ones at the sitting; the owner sees it at checkpoint A on the old map |
| 12 | Blending puts something new into every save made mid-scene | K9: nothing is added to the saved sprite; the tree dump and the pickle are compared with the baseline; R10's save test runs unedited |
| 13 | A measured light row makes people look wrong in a room nobody checked | The sampler proposes, a person tunes on the stage sheet, the check bounds the drift; one sheet per place per hour picture is in the review pack; `define sprite_lighting` remains the off switch |
| 14 | A story edit moves a save parked on a menu | Only U9 edits story files: seven image names, one new line, attributes; the names check against a baseline taken with the owner's `.rpyc`; the seven menu-parked saves; two commits, each right the first time; last; skippable |
| 15 | A sprite for Mom arrives and the image is defined twice, or the block figure vanishes before the sprite exists | The stand-ins sit behind an "image not defined" guard that runs after the generated sprites' definitions, from wave 0; the generator's definition takes over when the generator is run, and a file that has landed without it changes nothing; a harness checks all three states |
| 16 | A painted person does not match the sprites beside them in the new look | Three are bought before nineteen (batches 2 and 13) and looked at in the game. If it fails, poses stop there and about $6 is not spent |
| 17 | The in-place desk and photograph in Yaga's office do not hold | Two tries; then the office stays as it is and Yaga sews at the low table the picture already has |
| 18 | Twenty-four sittings is a lot of pressing Run for a beginner | Twelve renders or fewer; one candidate where the tool can judge; the tool, not the owner, finds faults and says so in plain words; every batch is useful alone; the order front-loads what changes the feel; everything after batch 13 can stop at any point |
| 19 | The art costs more than said | $0.16 a render is the node's own price; the total allows a fifth again for reruns; the campus is complete at about $14 |
| 20 | New places are empty boxes | Each has a person at some hour, a look, and (the baths and the pool) its own action; the Night column gives the dormitories their reason to exist; the schedule is one table the owner can change with a word at checkpoint B |
| 21 | A locked friend's room reads as a dead end in the first days | The door says who is out and where they are, and the journal's "Go there" walks to them |
| 22 | ComfyUI's Python is missing or changes; the sprite base route is not available | K14: one clear line, code packages are not blocked, an art sitting cannot install without the proof; question 4, and the test on Dad first |
| 23 | Fixed seeds do not reproduce a picture; the look or the bible changes after pictures are made | Every approved render is kept as a file; the look and the plan are frozen (9.1), and the manifest stamps each picture with the bible's hash, so the status list names the pictures a change touches |
| 24 | A reviewer cannot see what an agent saw | `tools/review_pack.sh`; tools and measurements live in `tools/`; the plan drawing, the sheets and the manifest are regenerated, never kept in scratch |
| 25 | The editor (a preview model) changes during the twenty-four sittings, so later rooms differ from earlier ones | The canary at the start of any sitting more than a week after the last (5.2); every approved render is kept |
| 26 | Holding a key to see names collides with a key the engine uses | N, not Tab (Tab toggles skipping, which would also switch the hints and the stage's eases off); `u2_contracts` asserts the key is in no `config.keymap` list |
| 27 | A check that is in every package's standard set cannot pass in a worktree because another package owns the thing it needs | Every contract symbol has a wave-0 stub; every new image name, the board's column and the pose tooling are in wave 0; hotspot ids are frozen as `SPOT_PLANNED`; `check_campus.py` has a stated rule for pictures not yet made |
| 28 | Two painted people at one table paint over each other | Named seats, made in order, and the tool refuses overlapping boxes (5.12) |
| 29 | A paid run aborts part-way (a blocked prompt, a rate limit) | "water mark" is out of the look and on the banned list; no run is over ten paid boxes; fixed seeds, so a second Run in the same session pays only for what did not finish |

---

## 11. What is left to later phases

**Combat (next):** the fight screen; tools and talismans that do something; curses by grade; cut-ins; more talismans.

**Story:** scenes staged on each room's floor plan and at their own hour; a closer view in one-to-one talks; the others staying in the room during the conversation itself; a motion kit and the Last Light grey-out everywhere it is used; painted moments (the storyboard's and the scene list's); the paper and phone views; the storyboard's nine places and its cast, Sukuna in Yuji's body first, with the cheek-mouth; the Divine Dog and Yaga's doll; "you" to "I"; faces in chapters 4 and 5, the Nade missions, Kurose and Oda, and second faces and speaker tags for Mom, Kurose and Nade; the four "stay the night" scenes set in the new rooms; Tokyo places to walk into; the club, the day trips and the Gojo night as real scenes; the driver painted into the car; Nade's doorstep; the seller and the friend at the market; reward lines over the Last Light lamp; the town scenes moved onto the Shibuya and Harajuku pictures; the lake, the basement, Yaga's workshop, an armory room, a main-hall interior.

**Whenever wanted, each small:** chess, memory, tic-tac-toe; watching the television with someone, the console, fishing with a friend; outfits; reusable cut-outs; activity pictures; a talking mouth per face; Sana's blink; item, fish and computer-page pictures; a painted card table; a bigger grade card; the hour and yen on the HUD; text size; night pictures for the gate, the forest, the river and the windowed rooms; a second foreground plane; an open map area kept across a save; a test of the cheaper editor.

**Its own pass:** music and sound, credits, a gallery, accessibility. **Not planned:** video (one $1 test whenever the owner likes); group pictures.

---

## 12. Coverage

### 12.1 Every item of the audit

**In** names the package (U) or batch (b). **Later** names the phase (section 11). **Dropped** gives the reason.

| item | answer |
|---|---|
| **N1** boys' dormitory | In: U0b; b10 |
| **N2** teachers' lounge and quarters | In: U0c, U1; b11 |
| **N3** the Night schedule | In: U0b, U0c (4.3); captions U4 |
| **N4** the girls' invitation | In: U1 (Bond 30) |
| **N5** second years | In: the shared room (U0b); Maki in the girls' dormitory |
| **N6** a friend's own room | In: five rooms, or the owner's choice at ruling 2 (U0b, U0c; b10, b11). Later (story): the four night scenes set in them |
| **N7** limits a new dormitory hits | In: `WORLD_INSIDE` (U0b); budgets raised on purpose (K11); the yards composed again (b3, b4) |
| **N8** the card-table invite | In: U5 |
| **N9** what a new place needs | In: 4.1; U0b, U0c; b5, b10 to b12 |
| **N10** where Utahime, Shoko, Ijichi sleep | In: 4.3 (U0c) |
| **N11** Gojo after dark | In: U1 |
| **N12** people at home on the map and journal | In: U1 (the name), U2 (dim faces) |
| **N13** other places | In: the baths. Later (story): the lake, the basement, the workshop, the armory room, the staff corridor, the main hall |
| **N14** which office is which | In: the bible; b4, b6 |
| **N15** one dormitory building or two; stale lines | In: the bible (the Common Room is its own hall); the blurb (U1). Later (story): Yuji's "roof of the dormitory block" line |
| **B1** the alley | In: b18 (fitted to the lamp's number) |
| **B2** the Sun Mall | In: b19; U0c (the names), U9 (the swaps) |
| **B3** the board's job sites | In: five shared kinds, b19; U0c (the names and the board's column) |
| **B4** home | In: b18 |
| **B5** the veil on the ridge | In: b8. Later (story): Sukuna's body |
| **B6** the city | In: b18. Later (story): town scenes moved to the district pictures |
| **B7** the districts | In: all five and two nights, b20 |
| **B8** the town street | In: b18. Later: Nade's doorstep |
| **B9** warehouse and annexe | In: b19; U0c, U9 |
| **B10** the campus map | In: b6 |
| **B11** the club and the market | In: b20; U0c (`night_club_bg`), U8 (the market's ground), U9 (the club's line). Later: the seller and the friend drawn |
| **B12** the diner | In: b18 |
| **B13** the car | In: b18. Later: the driver painted in |
| **B14** general curse-site pictures | In: b21 |
| **B15** the storyboard's nine places | Later (story) |
| **B16** the vending machine and the laptop | In: b0 (the machine is in the chosen Courtyard), b1 (the laptop) |
| **B17** Yaga's office | In: b7 (a desk and the photograph; fallback 5.3) |
| **B18** the konbini | Dropped: no scene shows it; the memory that opened on it is pointed at the alley (U7) |
| **B19** prompts, light rows, the record | In: U0d (prompts from data), the installer (measured rows), U10 (the stand-ins list) |
| **B20** two looks | In: one look for everything (5.1) |
| **T1** the garden at Night | In: b9; the tint on people (U3) |
| **T2** the Library's evening | In: b7 |
| **T3** scenes at a named hour | Later (story) |
| **T4** the Courtyard after dark | In: night, b9. The evening keeps the tint (its weekend pair moves to the baths) |
| **T5** the cafeteria's evening | In: b7, with its foreground |
| **T6** the ridge at Night | In: b8 |
| **T7** windowed rooms after dark | In part: the people in them are darkened with the tint now (U3). Later: the windows themselves. The classroom, the training hall, the dojo and the offices keep the tint at every hour, and the infirmary and the girls' corridor in the Evening (5.7), so their windows still show daylight under it; section 0 says so under "Chosen for you". A painted evening for the dojo, where Maki is on weekend Evenings, is one render ($0.16) whenever wanted |
| **T8** other outdoor nights | In: the six yards and the ridge. Later: gate, forest, river |
| **T9** my room's evening | In: b1 |
| **T10** the maps by hour | In: U2 |
| **F1** five in one place | In: the pool thins the river (U0c); the chip stays at lunch |
| **F2** the classroom | In: the front aisle stays; Megumi painted at a desk (b14) |
| **F3** places with no standing positions | In: U3 (in-place rooms), L (composed pictures, new places) |
| **F4** rooms that could have a foreground | In: Yaga's office, Gojo's office, the lounge (6.2); the Library and the infirmary by poses |
| **F5** the Common Room's last spot | In: 6.3's rule (U3) |
| **F6** behind the table in a conversation | In: per room, the `talk` key (U3) |
| **F7** Panda and the near table | In: U3 |
| **F8** foregrounds for new hour pictures | In: the installer recuts; the gate of K7 |
| **P1** captions | In: U4; approved at checkpoint B |
| **P20** nobody with anybody | In: captions that pair people; shared tables. Dropped: group pictures (fixed to who is there) |
| **P2** the twelve planned poses | In: re-picked into 22 (b2, b13 to b17) |
| **P19** four poses' missing objects | In: the machine (b0), the desk (b7), the veil (b8). The car: caption changed (the gate has no road) |
| **P3** ten captioned pairs | In: Maki in the dojo, Panda and Toge in the Library, Yuji by the pond. Later: the rest |
| **P4** clicking a painted person | In: U3 (stays painted), if screen-only; else as now |
| **P5** activities | Later; the bath and the pool are told in words |
| **P6** one body per person | Later |
| **P7** outfits | Later |
| **P8** the stand-in people | In: U7; b24. Oda is never shown |
| **P9** the curses | In: U7; b24 |
| **P10** the dog and props | Later (story) |
| **P11** pose against story caption | In: U3; Shoko's night pose (b17) |
| **P12** Utahime's pose | In: b13 |
| **P13** a painted person beside sprites | In: tested, b2 and b13, both before checkpoint C |
| **P14** the caption on hover only | In: "Show names" and a held key, N (U0c, U3, U6) |
| **P15** a companion | Kept as now |
| **P16** empty places | In part: fewer empty hours. An empty place is fine; each now has a look |
| **P17** captions that never show | In: U4 |
| **P21** the storyboard's cast | Later (each act) |
| **P18** the journal's future cast | Later (story) |
| **E1** faces | In: U9, the campus character scenes. Later (story): the rest |
| **E2** blink and talk for ten | In: b22, b23 |
| **E3** the mouth on other faces | Later |
| **E4** Yuji's mouth | The owner's verdict at checkpoint B, before b22 |
| **E5** the cheek-mouth | Later (with Sukuna) |
| **R1** thirteen places with nothing | In: U4 (a rule: every place has a thing) |
| **R2** the Common Room's dead things | In: looks (U4). Later: the console, watching together |
| **R3** chess, memory, tic-tac-toe | Later |
| **R4** the yards | In: Train at the posts, "Walk with them", the pond (U4); "Swim together" at the pool as its own activity (U4, U5) |
| **R5** Night | In: looks are free; visiting |
| **R6** actions on objects | In: U4 |
| **R7** the two offices | In: looks (U4) |
| **R8** my room | In: looks; Study on the desk. Later: outfits |
| **R9** fishing's pictures | Later; Swim moves onto the water |
| **R10** one-thing rooms | In: one more look each |
| **R11** dojo, hall, roof, gate, paths | In: looks; no car |
| **R12** a person in front of an object | In: 6.3's rule |
| **R13** the card spot and the look icons | In: the icon moves onto the low table (U4); looks keep the eye |
| **M1** Tokyo's dead pins | In: hidden (U2). Later (story): real places |
| **M2** the day trip | Later (story) |
| **M3** Tokyo's markers | In: U2 |
| **M4** exits on no door | In: every composed picture's layout sitting (L); the in-place rooms' stray exits (the infirmary, the ridge, the corridor's end) moved onto their doors by U4, on today's pictures (7.3). Where a room shows no door (the chosen Library) the way out sits at the bottom of the picture, a stated rule (5.2) that `check_layout.py` holds |
| **M5** Courtyard to the staff steps | Dropped: the plan has no such path |
| **M6** yard icons, empty markers, saves on the map | In: yard icons (U0b, b5; an exit keeps its area's icon until the sheet is cut), the half-height marker (U2). Later: an open area kept across a save |
| **S1** choice lists | In: U6 (position). Later: icons and costs on them |
| **S2** sound and the rest | Later (its own pass) |
| **S17** nothing teaches the place view | In: U4 (hints), U6 (How to play) |
| **S3** title and menu ground | In: U0c, U6; b21 |
| **S4** item pictures | Later |
| **S5** the older look | In: U8 |
| **S6** menus, saves, help | In: U6 |
| **S19** names on hover only | In: U0c, U3, U6 |
| **S7** letters and phone | Later (story) |
| **S8** time passing | In: the day card (U4). Later: an hour mark, yen on the HUD |
| **S9** the quick menu | In: U6; b5 |
| **S18** the computer's pages | Later |
| **S10** developer notes | In: hidden by the owner of each file (U6 the journal's, U2 the Tokyo pins, U8 the armory's, the market's and the board's). Kept on purpose: the lines and cards that mark where the story really stops (8.3 lists them; three are in frozen files) |
| **S11** memory tiles | Fixes itself as pictures land; Panda's memory place corrected (U7). The 70-word page stays |
| **S12** the grade card | In: its Close only (U8). Later: a bigger one |
| **S13** video | Not planned |
| **S14** redrawing the interface's pictures | In: unblocked (ComfyUI's Python); used by U6 |
| **S15** small leftovers | In: the window icon (U6). Later: the rest |
| **S16** the fight screen | Combat |
| **G1** the others while talking | In: they stay on the person view (U3). Later (story): in dialogue |
| **G2**, **G3**, **G4**, **G5**, **G6**, **G7**, **G10**, **G11** | Later (story), with the scenes it rewrites (8.5) |
| **G8** poses in scenes | In part: a pose stays on click. Later (story): scenes |
| **G9** scenes that borrow the wrong room | In: Maki's roster scene (U9). Later (story): the debrief |
| **L1** hover labels | In: sides from the picture's file or from position (U0c); swept at each sitting |
| **L2** toasts over the lamp | Later (story) |
| **L3** card and night-out small rules | In: the table's icon stays, dim (U0c's hook, U5's rule). Later: the club choice (a protected menu) |
| **L4** the after-phase review | In: checkpoint D |
| **L5** talismans | Later (combat) |
| **L6** narration voice | Later (story) |

All 134 are placed: N 15, B 20, T 10, F 8, P 21, E 5, R 13, M 6, S 19, G 11, L 6.

### 12.2 Every one of the audit's 54 questions

| Q | status | the answer the plan builds |
|---|---|---|
| 1 | **the owner answered** ("rooms you can walk into"); for whom is **for the owner** (question 2) | default: Yuji, Megumi, Panda and Toge (shared), Nobara, Maki |
| 2 | chosen for you | the second years share the boys' and girls' dormitories; Panda rooms with Toge, not with Yaga |
| 3 | **the owner answered** in part ("Gojo wont, but the other will"); the rest chosen | both a lounge and a dormitory, in one house; Yaga, Utahime and Ijichi live there; a student may walk in at any hour; bedrooms are doors |
| 4 | chosen | awake and visible in their rooms |
| 5 | chosen | Bond 30 with Nobara or Maki opens the girls' corridor after dark; friends' rooms open while their owner is in; the teachers' house always |
| 6 | chosen | rooms open off a corridor (the garden keeps seven exits); the Dormitories map shows six pins; no new area |
| 7 | chosen | the districts, the club and the market are painted now; the dead pins are hidden; places to walk into wait for the story |
| 8 | **the owner answered** ("all the backgrounds that we missed"; "Yes plan sprites too") | all of them; Oda is never shown |
| 9 | chosen | the storyboard's cast waits for each act; Sukuna-in-Yuji first, with the cheek-mouth |
| 10 | chosen | 22 poses in three steps |
| 11 | chosen | paint the object: the machine, the desk and photograph, the veil, a laptop. The car: change the caption |
| 12 | chosen | single figures |
| 13 | chosen | a painted person stays painted while I look at them |
| 14 | chosen | the others stay, dimmed, on the person view; they step out in the conversation |
| 15 | chosen | faces now on the campus character scenes; the "you" lines are not touched |
| 16 | chosen | every place gets at least one thing; first the pond, the posts, the railing, the wardrobe, Gojo's television |
| 17 | **the owner asked for it**; the details chosen | from the table; any student met and on campus; up to three seats; no Bond level; free; not at Night |
| 18 | chosen | none now; chess first when wanted |
| 19 | chosen | one-time hints and a "How to play" page |
| 20 | chosen | a "Show names" setting and hold N (Tab is the engine's skip key) |
| 21 | chosen | yes: looks are free at Night, and visiting |
| 22 | chosen | wherever people stand after dark, plus a real night for the six yards and the ridge (5.7); evening windows in the dojo, the classroom, the hall and the offices keep the tint |
| 23 | **the owner answered** | one look everywhere |
| 24 | chosen | shared activities keep the standing sprite; the bath and the pool are told in words |
| 25 | chosen | no reusable cut-outs |
| 26 | chosen | no outfits |
| 27 | chosen | no sound, gallery or credits in this overhaul |
| 28 | chosen | no video test |
| 29 | **the owner answered** ("We can redo the jujutsu high map") | a painted bird's-eye campus with the new buildings on it |
| 30 | **the owner answered** (a title card); what it shows chosen | the torii and steps at blue hour; the name as text; the menu ground made from it |
| 31 | chosen | choices move to the right third; icons and costs on them not now |
| 32 | chosen | the red seal stays; buttons become icons; one Close |
| 33 | chosen | "Day 9 · Tue · Evening · Cafeteria"; settings added: Show names |
| 34 | chosen | no item, fish or computer-page pictures now |
| 35 | chosen | no motion kit now |
| 36 | chosen | scenes keep their pictures and positions |
| 37 | chosen | scenes are offered where they are today |
| 38 | chosen | no one-off moment pictures now |
| 39 | chosen | the veil shows every time on the ridge; Sukuna's body is not shown |
| 40 | chosen | the doll hall stays and gains a low desk with the photograph |
| 41 | **the owner answered** (the baths and the pool); the rest chosen | none of the lake, basement, workshop, armory room, staff corridor or main hall |
| 42 | **the owner answered** for Ijichi and Gojo ("Gojo wont, but the other will"); the rest chosen | Utahime has the guest room in the Teachers' Dormitory; Shoko's nights in the infirmary are on purpose |
| 43 | chosen | the Common Room is its own hall, shared by everyone |
| 44 | chosen | lines are proposed; the owner approves them at checkpoint B; hover-only unless names are shown |
| 45 | chosen | thin the river (the pool, where "Swim together" has its own pool scene); keep the chip at lunch |
| 46 | chosen | the front aisle, with Megumi painted at a desk; people stay behind the desk or table where the picture allows |
| 47 | chosen | redo Utahime's pose; a painted person beside sprites is accepted after the test |
| 48 | chosen, with the owner's eye at checkpoint B | the calm face only; Yuji judged before ten more; Sana does not blink |
| 49 | chosen | a day card; no hour mark; the hour and yen stay off the HUD |
| 50 | chosen | no paper or phone view |
| 51 | chosen | exits on doors and paths, indoors too; where the door is behind me, at the bottom of the picture; the Courtyard not joined to the staff steps; the yards get icons |
| 52 | chosen | "later build" notes hidden from players where they are only notes; the cards and lines that mark where the story stops for now stay |
| 53 | chosen | not needed: ComfyUI's own Python has Pillow |
| 54 | chosen | the review is one list at checkpoint D |

Kept for the owner: the four rulings of section 0. Three are asked now, with the plan (whose rooms; the budget and cut order; the cloud plan); one at checkpoint A (the campus from above).

---

## Method: where the judges disagreed, and what was decided

The three judges each named a different design as the best (the owner's words: the living campus; the code and the saves: the smallest safe steps; the art and its proof: pictures first). They agree on more than that suggests: each asked for the other two's strongest part as a graft. This plan is those grafts, taken together. Where they pulled apart, the code was read again:

1. **The dormitory's shape.** A seventh map area (steps), a house table with my room pinless and a Home chip (campus), or a house table with my room keeping its pin (pictures). Read: `room_paths.rpy:178, 214-238, 296-333, 349-364`; `ui_map.rpy:811-812`; `p2_map.rpy:273, 336-352`; `p2_saves.rpy:467-476`. Decided: the house table with the pin kept. It needs only validator lines (the code judge confirmed the steps design overstated its cost), keeps six markers (the owner's judge), and avoids both the crash and the level-1 check the campus version ran into.
2. **Where exits live.** In code with layout sittings that edit `.rpy` (steps) or in sidecars (pictures, campus). Read: the sidecar reader exists (`room_paths.rpy:226-231`); `path_validate`'s spacing rules read code rows only (`:381-390`). Decided: sidecars, with the validator's spacing moved onto applied points and `check_layout.py` before install, as the code judge's graft 3 asks.
3. **The shadow's shape.** Read `lighting.rpy:108-143` and the five set points: the six-value light row (steps) is the only one right by construction.
4. **`person_now`.** Read `p2_contracts.rpy:431-436`: exactly six keys. The shape stays (steps).
5. **The area view's word budget.** Counted from `sb_world.rpy`'s names with `_lib.rpy:392-403`'s rule: Dormitories 17, Staff 17. Raised on purpose to 18; all three designs had it wrong.
6. **The Common Room at Night.** Read `wp1_world.rpy:329-334`: it must stay empty by routine. The campus design's Nobara cell was moved to her room.
7. **How far "all the backgrounds" goes, against how many story lines are touched.** The owner's judge wanted every stand-in replaced with the scene swaps; the code judge wanted the fewest edits where saves rest. Read: the seven `scene` lines (none follows a call or fronts a menu); `sb_night.rpy:520-595`; `sb_market.rpy`'s screen. Decided: all the pictures; the swaps in one package, alone, with the names check; the market's ground drawn by its screen (no statement); one new line for the club; no `show mother sad`; the alley fitted to the lamp so `ch1_alley.rpy` is never opened.
8. **Faces.** On by default (the owner's judge), but alone, last and first on the cut list (the code judge).
9. **The baths and the pool.** On the Training Yard (pictures) the column check fails by arithmetic (seven exits and two fixed tiles are nine); on the Mountain Path and the Training Yard separately (campus, steps) no yard passes seven. The sauna as its own room and "nobody is drawn in the bath" are the owner's judge's grafts.
10. **The teachers' door.** The steps design's open sitting room, as the owner's judge proposed, inside the campus design's one house, which costs the staff steps one exit instead of two.
11. **The proof for a redo.** Pictures' guard windows and keep lists, with the campus design's floor measure and the steps design's escalation; the sharpness threshold set from the third test (the art judge re-measured: 3.0 and 7.5 times), since all three designs' "three times" would have refused the approved look.
12. **The window views.** The art judge found the two third-test rooms show a generic town roof. I looked at the pictures: the Common Room's left window shows a house that is not on the campus, so it and the Cafeteria are run once more in batch 1; the chosen Library's grey roofs are kept and the plan puts the Cafeteria's roof there.
13. **Batches.** The art judge's count of renders, not pictures, and no sitting over twelve; the free batch 0 first; the Common Room's evenings and Nobara's pose in the very next sitting.
14. **Small corrections taken from the verdicts:** the konbini does stage one memory (`sb_memories.rpy:156`), so its row is re-pointed; `pool_swim` joins `NIGHT_REST_BLOCKS` in `sb_night.rpy` itself; `p2_saves.rpy:452-457` is in the ledger; no "intended losses" list is written for "Walk with them"; Ijichi lives on campus; there is no car at the gate because the gate has no road; rule names are K, never U.

15. **The adversarial review (three lenses, 45 findings, several of them the same fault seen from two sides).** Each was checked against the code and the pictures; all but the details noted here were right and are fixed. *The map:* the Ridge sat east of the Riverside on the plan and west of it on the Mountain map; it is now straight up the stairs from the Mountain Path (today's exit is at x 862 and today's pin at x 960), and 4.8's pins are printed from the plan by tool. The Training Yard's staff path is on the kura's right. The School Courtyard's camera faces north (it had its back to the schoolhouse it put on its right). The Common Room's window line was read off the installed picture (the pond is behind the camera). *Feasibility:* "Swim together" at the pool is its own activity (`act_swim` shows the river, `events_activities.rpy:102-103`); a house is always open from its own rooms (`path_walk` refuses a locked destination); the held key is N (Tab is `toggle_skip`); sidecars of in-place rooms carry no `for_rev`; the pose tooling, every new image name, the board's column and every contract stub move into wave 0; hotspot ids are frozen as `SPOT_PLANNED`; `check_campus.py` has a rule for pictures not yet made; the stand-in guard is on the image, after the generated sprites; the stubs register the new actions for `night_validate`; a yard keeps its area's icon until the sheet is cut; the club's line is `scene expression night_club_bg(key)`; the pointer lock; two more ledger lines; the six made saves in the repository. *Art:* sharpness is measured against revision 1; `KEEP` is split so a relight is not told to keep the time of day, and the three untried wordings each have a named test and a fallback; nothing lends any more, so "lenders last" and its deadlock with the cut order are gone and the whole prologue is one sitting; pairs at a table have seats and an overlap refusal; the fallback for batch 3 is a table; a canary guards against the editor changing; the curses are painted on green at 9:16; "water marks" left the look. *The owner's page:* three rulings are asked before building, the pose test comes before the checkpoint that judges it, and section 0 is corrected where it claimed more than the plan does. **Taken differently from the finding:** the three proposals for the Ridge's new position disagreed, and two of them kept a pin that would then have been reversed against the Bathhouse; (950, 110) with the pin at (960, 250) satisfies every relation. For the lenders, the stand-in copies were taken over the "warning the owner can accept", because they also remove the ordering. Not every "later build" line is hidden: the ones that tell the player where the story stops are kept and listed. No teacher poses were added; section 0 was corrected instead.

Not taken, from any design: the Home chip, a seventh marker, a saved `light_shadow`, a new key on `person_now`, the cold-milk action, a test of the cheaper editor, a sidecar for the lamp's point, the second test's emptied Common Room, and the main-hall Courtyard.

**Still open, and where each is settled:** whether the editor follows a plan drawing (batch 3); whether a painted person matches the sprites in the new look (batches 2 and 13); whether a pose kept on the person view is screen-only (U0c's test); whether each yard, as painted, leaves the column at eight tiles (each layout sitting); whether the desk holds in Yaga's office (batch 7); whether a named addition, a relight and an outdoor redo hold with their keep wording (batches 1a, 1b, 8a); whether N is free on the owner's keyboard layout (U0c's check); whether the Comfy Cloud plan is active (ruling 4, asked now). Line numbers were read, not run.
