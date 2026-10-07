# The campus record

**Written by `tools/campus_plan.py` from `tools/bgs/campus.json`. Do not edit this page: change the record and run the tool again.** It replaces `CAMPUS.md` for the second UI overhaul (`docs/UI2_DESIGN.md` 5.2).

There is no drawing of the campus to approve. The campus is kept one place a different way: every picture the owner chooses **fixes** facts, and every later picture is composed from words and the chosen pictures of its neighbours and must agree with the facts so far. The maps are made last, round the finished places.

- A **fixed** row is a fact a chosen picture shows. It names that picture and its revision, and it changes only when the owner chooses that picture again.
- A **proposed** row is the plan's words for something not painted yet. It goes into prompts, and it is rewritten without ceremony when a chosen picture says otherwise.
- A **waived** row names a fixed fact, the chosen picture that stands against it and the date the owner accepted that. Only `tools/install_redo.py --waive` writes one.

`tools/check_campus.py` checks all of it; `tools/campus_plan.png` is the same ground plan as a sketch (for reviewers, never for approval).

Today: **33 fixed rows, 123 proposed, 0 waived.**

## The pictures the owner has chosen

| picture | place | revision | kind | chosen | the render |
|---|---|---|---|---|---|
| `courtyard` | Courtyard | 2 | composed | 2026-10-06 | `look2_courtyard_gateway_00001_.png` |
| `library` | Library | 2 | composed | 2026-10-06 | `look2_library_bright_00001_.png` |
| `dorm_common` | Common Room | 2 | inplace | 2026-10-06 | `look3_dorm_common_keep_00001_.png` |
| `cafeteria` | Cafeteria | 2 | inplace | 2026-10-06 | `look3_cafeteria_keep_00001_.png` |

## The ground plan

Top-down on a 1920 x 1080 sheet, north and uphill at the top. Rows marked † are fixed. A building's look line is the same in every picture that shows it; its court side goes only into prompts whose camera sees that side.

| building or ground | what a prompt calls it | holds | at (x, y) | its look | court side (seen from) |
|---|---|---|---|---|---|
| † Courtyard | the central courtyard | `courtyard` | (960, 800) | a wide flagstone court |  |
| † Gateway | the roofed gateway | a landmark, not a place | (960, 690) | a roofed timber gate with a grey tiled roof, a stone lantern either side; behind it a flight of stone steps uphill |  |
| † Gate Lodge (west) | the gate lodge left of the gateway | a landmark, not a place | (890, 690) | one of a matching pair of gate lodges, either side of the gateway steps behind the low stone wall: brown timber, a railed veranda, a grey tiled roof |  |
| † Gate Lodge (east) | the gate lodge right of the gateway | a landmark, not a place | (1040, 690) | one of a matching pair of gate lodges, either side of the gateway steps behind the low stone wall: brown timber, a railed veranda, a grey tiled roof |  |
| † Pagoda | the pagoda | a landmark, not a place | (840, 640) | a pagoda of five storeys, dark timber and grey tiled roofs, behind the schoolhouse's north end |  |
| † School Building | the schoolhouse | `classroom` | (720, 760), long, north to south | a two-storey schoolhouse of warm brown timber boarding, two rows of large white-framed windows | a covered entrance porch with shoe lockers (`courtyard`) |
| † Library | the library | `library` | (430, 640) | white plaster and timber, tall gridded windows |  |
| † Archive Wing | the low wing behind the library | a landmark, not a place | (430, 560) | a low grey-tiled roof behind the library, among treetops |  |
| † Training Hall | the training hall | `training` | (1200, 760), long, north to south | a broad brown-timber hall with a deep roofed veranda and paper-screened sliding doors | a weapon rack on the veranda and straw posts by the steps; the vending machine at the court end of the veranda (`courtyard`) |
| Main Gate | the main gate | `gate` | (960, 985) | a stone torii across a flagstone footpath between cedars and stone lanterns, with no road; beyond the torii a flight of stone steps climbs to an open flagstone court, and nothing is built at the top of the steps |  |
| School Courtyard | the school courtyard | `school_yard` | (470, 770) | packed earth, one pine with a bench under it |  |
| Infirmary | the infirmary | `infirmary` | (250, 760) | a small white annex with a pale green door and a ramp, at the forest edge |  |
| Cafeteria | the dining hall | `cafeteria` | (430, 890) | a low wide hall with a grey tiled roof, a wall of glass sliding doors, a metal kitchen chimney, benches outside |  |
| Training Yard | the training yard | `training_yard` | (1470, 780) | bare earth, a row of striking posts |  |
| Storehouse | the storehouse | `storehouse` | (1480, 640) | a white kura with a black tiled roof and one heavy door |  |
| Dojo | the dojo | `dojo` | (1720, 760) | a long low hall with one unbroken band of windows |  |
| Swimming Pool | the swimming pool | `pool` | (1740, 900) | an open-air pool set into a stone terrace behind the dojo, edged in the yards' grey stone, a timber deck and a low wooden fence, a small changing hut under the school's grey tiled roof |  |
| Dormitory Garden | the dormitory garden | `dorm_yard` | (960, 540) | a stone path through a kept garden, a pond with two stone lanterns |  |
| Boys' Dormitory | the boys' dormitory | `boys_dorm`, `dorm`, `yuji_room`, `megumi_room`, `senpai_room` | (720, 480) | two storeys of dark timber, an upstairs gallery, an outside stair, a plain blue door curtain |  |
| Common Room | the common room | `dorm_common` | (960, 470) | one storey, glass doors the whole width, a deck over the pond |  |
| Tower | the tower | `rooftop` | (960, 380) | the tall wooden tower with an open top veranda |  |
| Girls' Dormitory | the girls' dormitory | `girls_dorm`, `nobara_room`, `maki_room` | (1200, 480) | two storeys of white plaster and timber, latticed windows, a plain red door curtain, flower boxes |  |
| Staff Building Steps | the staff building steps | `staff_yard` | (1560, 520) | wide stone steps, gravel either side |  |
| Principal's Hall | the principal's hall | `office` | (1560, 400) | the largest roof, on a stone platform, heavy closed doors, no windows |  |
| Gojo's Office | the small detached office | `gojo_office` | (1400, 470) | a small detached house with one very large window |  |
| Utahime's Office | the small office pavilion | `utahime_office` | (1690, 480) | a neat small pavilion, a round window, paper screens |  |
| Teachers' House | the teachers' house | `teachers_lounge`, `teachers_dorm` | (1790, 400) | a two-storey house with a veranda all round, warm windows, a bamboo fence |  |
| Mountain Path | the mountain path | `trailhead` | (900, 300) | where the stone gives out: a standing stone and a low gate |  |
| Bathhouse (shown as Onsen) | the hot-spring house | `bathhouse`, `sauna` | (1160, 240) | a tall tiled roof with a steam vent, a stone basin by the door, steam above the fence |  |
| Forest Trail | the forest trail | `forest` | (330, 230) | tall cedars, nothing built |  |
| Riverside | the riverside | `riverside` | (1380, 170) | a clear river, a pebble bank, a deep pool |  |
| Mountain Ridge | the mountain ridge | `ridge` | (950, 110) | grass and rock above the trees; a faint dark curtain standing in the sky beyond the far mountains |  |

- **Gateway:** the way to the dormitories; a landmark, not a place
- **Gate Lodge (west):** Fixed as a lodge: it stands at the foot of the steps and is not a dormitory. The dormitories stand further up, round the garden, and keep their own two looks.
- **Gate Lodge (east):** Fixed as a lodge: it stands at the foot of the steps and is not a dormitory. The dormitories stand further up, round the garden, and keep their own two looks.
- **Pagoda:** a landmark, not a place
- **Archive Wing:** a landmark, not a place: it is what the chosen Library's two far windows show
- **Swimming Pool:** built with the school, not added to it (the owner's ruling, O17)
- **Mountain Ridge:** straight up the stone stairs from the Mountain Path

No prompt names the series or a character, so in a prompt a building is called what the second column says, never by a person's name.

## Paths

- Courtyard to School Courtyard: through the passage by the schoolhouse's porch (**fixed** by `courtyard` (revision 2))
- Courtyard to Dormitory Garden: up the gateway steps (**fixed** by `courtyard` (revision 2))
- Courtyard to Training Yard: by the training hall's veranda steps (**fixed** by `courtyard` (revision 2))
- Dormitory Garden to Staff Building Steps: east along stepping stones (proposed)
- Dormitory Garden to Mountain Path: north, behind the boys' dormitory (proposed)
- Staff Building Steps to Training Yard: south, down a walled path (proposed)

## What I see from each place, and what each exit sits on

### Courtyard

I stand at (960, 870), facing north. The place itself is **fixed** by `courtyard` (revision 2).

| where | what | leads to | |
|---|---|---|---|
| left | School Building: on the schoolhouse's covered entrance porch | School Courtyard | **fixed** by `courtyard` (revision 2) |
| ahead | Pagoda: behind the schoolhouse's north end, left of the gateway |  | **fixed** by `courtyard` (revision 2) |
| ahead | Gate Lodge (west): behind the low stone wall, left of the gateway steps |  | **fixed** by `courtyard` (revision 2) |
| ahead | Gateway: on the gateway's steps, which climb to the dormitories | Dormitory Garden | **fixed** by `courtyard` (revision 2) |
| ahead | Gate Lodge (east): behind the low stone wall, right of the gateway steps |  | **fixed** by `courtyard` (revision 2) |
| right | Training Hall: on the training hall's veranda steps | Training Yard | **fixed** by `courtyard` (revision 2) |
| bottom | the flagstones at the bottom of the frame, leading back to the gate | Main Gate | **fixed** by `courtyard` (revision 2) |

### Library

The camera stands in the room, facing north. The place itself is **fixed** by `library` (revision 2).

| where | what | leads to | |
|---|---|---|---|
| bottom | the way out is behind the camera (the chosen picture shows no door), so it sits at the bottom of the picture | School Courtyard | **fixed** by `library` (revision 2) |

### Main Gate

I stand at (960, 1040), facing north. The place itself is proposed.

| where | what | leads to | |
|---|---|---|---|
| left | School Building: the schoolhouse's timber shows at the top of the steps, on the left |  | proposed |
| ahead | Courtyard: it is reached through the torii, up the steps | Courtyard | proposed |
| right | Training Hall: the training hall's veranda shows at the top of the steps, on the right |  | proposed |

### School Courtyard

I stand at (470, 840), facing north. The place itself is proposed.

| where | what | leads to | |
|---|---|---|---|
| left | Infirmary: its door is the way in | Infirmary | proposed |
| ahead | Library: its door, with the pine and its bench in front of it | Library | proposed |
| right | School Building: a side porch in its west wall, facing this yard | Classroom | proposed |
| bottom left | Cafeteria: the path to the dining hall's glass doors; the dining hall is behind the camera | Cafeteria | proposed |
| bottom right | the passage by the schoolhouse, back to the central courtyard | Courtyard | proposed |

### Dormitory Garden

I stand at (960, 610), facing north. The place itself is proposed; at least 1 of its exits must stay clear of a four-person row.

| where | what | leads to | |
|---|---|---|---|
| left | Boys' Dormitory: its door, under the blue door curtain | Boys' Dormitory | proposed |
| left | the dirt path that goes up behind the boys' dormitory | Mountain Path | proposed |
| ahead | Common Room: its glass doors open onto the deck | Common Room | proposed |
| ahead | Tower: it rises behind and above the common room | Rooftop | proposed |
| right | Girls' Dormitory: its door, under the red door curtain, beyond the pond | Girls' Dormitory | proposed |
| bottom left | the steps down to the central courtyard | Courtyard | proposed |
| bottom right | the stepping stones east, to the staff building steps | Staff Building Steps | proposed |

### Staff Building Steps

I stand at (1560, 610), facing north. The place itself is proposed.

| where | what | leads to | |
|---|---|---|---|
| left | Gojo's Office: its door faces the steps | Gojo's Office | proposed |
| ahead | Principal's Hall: it stands at the top of the steps | Principal's Office | proposed |
| right | Utahime's Office: its door faces the steps | Utahime's Office | proposed |
| right | Teachers' House: it stands beyond the office pavilion, at the edge | Teachers' Lounge | proposed |
| bottom left | the path back to the dormitory garden | Dormitory Garden | proposed |
| bottom right | the walled path down to the training yard | Training Yard | proposed |

### Training Yard

I stand at (1470, 890), facing north. The place itself is proposed; at least 1 of its exits must stay clear of a four-person row.

| where | what | leads to | |
|---|---|---|---|
| left | Training Hall: its doors onto this yard | Training Hall | **fixed** by `courtyard` (revision 2) |
| left | the passage at the bottom left, back to the central courtyard | Courtyard | proposed |
| ahead | Storehouse: it stands beyond the striking posts | Storehouse | proposed |
| ahead | the walled path and its steps, right of the storehouse | Staff Building Steps | proposed |
| right | Dojo: its door faces the yard | Dojo | proposed |
| right | a roofed timber gate at the edge, beside the dojo: the way to the swimming pool | Swimming Pool | proposed |

### Mountain Path

I stand at (900, 340), facing north. The place itself is proposed.

| where | what | leads to | |
|---|---|---|---|
| left | Forest Trail: a level path leads into the cedars | Forest Trail | proposed |
| ahead | Mountain Ridge: stone stairs climb straight up the mountain toward it | Mountain Ridge | proposed |
| right | Bathhouse (shown as Onsen): it stands in the middle distance, among the trees | Onsen | proposed |
| right | the path that goes down at the edge, toward the river | Riverside | proposed |
| bottom | the stone slabs back down to the dormitory garden | Dormitory Garden | proposed |

**Behind the camera means the bottom of the picture.** A place the camera has its back to has its exit in the bottom band (y 900 or lower down).

## What the windows show

A line names a neighbour only once that neighbour's picture is chosen; until then the prompt leaves the line out.

| room | wall | faces | the wall is | the line a prompt carries | waits for | the line is |
|---|---|---|---|---|---|---|
| Library | far | north | **fixed** by `library` (revision 2) | the low grey tiled roof of the wing behind the building, among treetops |  | **fixed** by `library` (revision 2) |
| Common Room | far | north | **fixed** by `dorm_common` (revision 2) | at the back, the foot of a tall wooden tower and cedars | Dormitory Garden | proposed |
| Common Room | left | west | **fixed** by `dorm_common` (revision 2) | on the left, the dark timber and upstairs gallery of the boys' dormitory | Dormitory Garden | proposed |
| Cafeteria | left | north | **fixed** by `cafeteria` (revision 2) | the school courtyard and its pine | School Courtyard | proposed |
| Classroom | side | west | proposed | the school courtyard below, the library's roof beyond it, and cedars | School Courtyard | proposed |
| Infirmary | side | west | proposed | cedar trunks at the forest edge |  | proposed |
| My Room | side | north | proposed | the forested mountain slope and the ridge above it, with nothing built in view |  | proposed |
| Yuji's Room | side | east | proposed | the dormitory garden and its pond | Dormitory Garden | proposed |
| Megumi's Room | side | west | proposed | the cedar forest |  | proposed |
| Panda and Toge's Room | side | east | proposed | the tall wooden tower | Dormitory Garden | proposed |
| Girls' Dormitory | end | west | proposed | the dormitory garden and the common room's roof | Dormitory Garden | proposed |
| Nobara's Room | side | west | proposed | the dormitory garden and the common room's roof | Dormitory Garden | proposed |
| Maki's Room | side | west | proposed | the dormitory garden and the common room's roof | Dormitory Garden | proposed |
| Teachers' Lounge | side | west | proposed | the staff building steps | Staff Building Steps | proposed |
| Teachers' Dormitory | end |  | proposed | a small inner garden |  | proposed |
| Training Hall | high |  | proposed | sky and cedar tops |  | proposed |
| Dojo | side | west | proposed | the training yard's striking posts | Training Yard | proposed |
| Onsen | open screens |  | proposed | the hot spring and the cedar slope behind it |  | proposed |
| Utahime's Office | round |  | proposed | a small raked gravel garden |  | proposed |
| Gojo's Office | large |  | proposed | cedars |  | proposed |

The Principal's office, the storehouse and the sauna have no windows. The Rooftop's far view is redone in place and stays a loose cluster of roofs.

## The rooms already chosen, as their pictures show them

- **Library** (**fixed** by `library` (revision 2)): tall bookshelves with a rolling ladder along the left wall; two tall windows in the far wall; a long reading table with green-shaded lamps in the middle distance and a second table at the right; two low armchairs between the windows; a glass-fronted cabinet with a small brass padlock against the right wall, holding scrolls; a wide clear wooden floor in the foreground; no door in view.
- **Common Room** (**fixed** by `dorm_common` (revision 2)): seen from the sliding glass doors: a sofa along the left wall under a large window; a bookshelf with board games on top in the far left corner; a window in the far wall; a low table on a rug in the middle with two floor cushions; a small fridge, a kettle and a microwave at the far right; a television on a low cabinet on the right; an air conditioner high on the far wall.
- **Cafeteria** (**fixed** by `cafeteria` (revision 2)): a wall of tall windows with tied-back curtains along the left; a water cooler and potted plants at the far left; the serving counter with a food warmer and stacked trays along the far wall; rows of long wooden tables and chairs on the right; round paper lamps hanging from the ceiling; a clear wooden floor on the left.

## What waits for a batch

`tools/check_campus.py` lists these, with every side and pin of today's pictures that disagrees with the record, as "waits for batch N". They are not failures while the picture is at revision 1.

- batch 2, `gate`: today's gate picture shows a large hall with a hipped tiled roof at the top of the steps behind the torii; the Courtyard the owner chose has no hall there.
- batch 3a, `dorm_common`: the Common Room's windows show a town-style house; they are redone to show the tower and the boys' dormitory once the garden is chosen.
- batch 4a, `cafeteria`: the Cafeteria's windows show roofs that are not the campus; they are redone to show the School Courtyard once it is chosen.

## Waived

Nothing. (A waiver is the last rung of the ladder in 5.2: the owner is shown the contradiction in plain words and accepts it.)

## The order of making

A place is not made before the chosen picture of each place in its `after` (K8).

| place | picture | how | batch | made after | chosen |
|---|---|---|---|---|---|
| Courtyard | `courtyard.png` | composed again | 0 | – | yes |
| Cafeteria | `cafeteria.png` | redone in place | 0 | School Courtyard | yes |
| Library | `library.png` | composed again | 0 | School Courtyard | yes |
| Common Room | `dorm_common.png` | redone in place | 0 | Dormitory Garden | yes |
| Main Gate | `gate.png` | composed again | 2 | Courtyard |  |
| School Courtyard | `school_yard.png` | composed again | 1 | Courtyard |  |
| Classroom | `classroom.png` | redone in place | 6 | School Courtyard |  |
| Infirmary | `infirmary.png` | redone in place | 6 | School Courtyard |  |
| Dormitory Garden | `dorm_yard.png` | composed again | 1 | Courtyard |  |
| Boys' Dormitory | `boys_dorm.png` | composed again | 9 | Dormitory Garden |  |
| My Room | `your_room.png` | redone in place | 3 | Dormitory Garden |  |
| Yuji's Room | `yuji_room.png` | composed again | 9 | Dormitory Garden |  |
| Megumi's Room | `megumi_room.png` | composed again | 10 | Dormitory Garden |  |
| Panda and Toge's Room | `senpai_room.png` | composed again | 10 | Dormitory Garden |  |
| Rooftop | `rooftop.png` | redone in place | 8 | Dormitory Garden |  |
| Girls' Dormitory | `girls_dorm.png` | redone in place | 4 | Dormitory Garden |  |
| Nobara's Room | `nobara_room.png` | composed again | 11 | Dormitory Garden |  |
| Maki's Room | `maki_room.png` | composed again | 11 | Dormitory Garden |  |
| Staff Building Steps | `staff_yard.png` | composed again | 2 | Dormitory Garden, Training Yard |  |
| Principal's Office | `office.png` | redone in place | 12 | Staff Building Steps |  |
| Gojo's Office | `gojo_office.png` | redone in place | 12 | Staff Building Steps |  |
| Utahime's Office | `utahime_office.png` | redone in place | 12 | Staff Building Steps |  |
| Teachers' Lounge | `teachers_lounge.png` | composed again | 13 | Staff Building Steps |  |
| Teachers' Dormitory | `teachers_dorm.png` | composed again | 13 | Staff Building Steps |  |
| Training Yard | `training_yard.png` | composed again | 1 | Courtyard |  |
| Training Hall | `training.png` | redone in place | 15 | Training Yard |  |
| Storehouse | `storehouse.png` | redone in place | 16 | Training Yard |  |
| Dojo | `dojo.png` | redone in place | 15 | Training Yard |  |
| Swimming Pool | `pool.png` | composed again | 16 | Training Yard |  |
| Mountain Path | `trailhead.png` | composed again | 2 | Dormitory Garden |  |
| Forest Trail | `forest.png` | redone in place | 17 | Mountain Path |  |
| Mountain Ridge | `ridge.png` | redone in place | 18 | Mountain Path |  |
| Onsen | `bathhouse.png` | composed again | 19 | Mountain Path |  |
| Sauna | `sauna.png` | composed again | 19 | Mountain Path |  |
| Riverside | `riverside.png` | redone in place | 17 | Mountain Path |  |

## The pin targets for the maps

What the area-map prompts will ask for (`tools/campus_plan.py --pins`): the ground plan stretched onto each area picture's pin frame. The final points are measured on each chosen map.

- Courtyard & Gate (2): courtyard (950, 300), gate (950, 860)
- School Building (5): library (821, 300), infirmary (400, 569), classroom (1500, 569), school_yard (915, 591), cafeteria (821, 860)
- Dormitories (6): rooftop (972, 300), dorm (400, 475), dorm_common (972, 615), boys_dorm (444, 650), girls_dorm (1500, 650), dorm_yard (972, 860)
- Staff Building (5): office (851, 300), teachers_lounge (1500, 300), gojo_office (400, 627), utahime_office (1218, 673), staff_yard (851, 860)
- Training Grounds (5): storehouse (970, 300), training (400, 558), dojo (1459, 558), training_yard (950, 602), pool (1500, 860)
- The Mountain (5): ridge (1050, 300), riverside (1500, 477), forest (400, 654), bathhouse (1270, 683), trailhead (997, 860)

## The shape of `campus.json`

| key | what it holds |
|---|---|
| `format` | `1` |
| `sheet` | the ground plan's size, `[1920, 1080]`; north is up |
| `rules` | `thirds` (the two x where the screen's thirds meet), `bottom_band` (an exit behind the camera has y at or below this), `apart` (px on a picture inside which two exits or pins are not ordered), `plan_apart` (the same on the ground plan), and the four angles that say what "left", "ahead", "right" and "behind" mean from a camera |
| `areas` | `{area key: {name, hub, stem, batch}}`: the six area maps |
| `campus_map` | `{stem, batch, mountain_only_north}` |
| `pictures` | `{picture stem: {place, rev, kind, batch, chosen, render, source, source_2k}}`: the pictures the owner has chosen. `source` is where the chosen file is kept until it is installed in the game. The installer adds a row with each picture |
| `fixed`, `proposed` | lists of rows; every row has a unique `id` and a `kind`. A fixed row also has `by: {picture, rev}`. A proposal that a chosen picture fixes moves, with its id, from one list to the other |
| row `building` | `key`, `name`, `as` (what a prompt calls it; never a person's name), `holds` (place keys), `at` `[x, y]`, `shape`, `ground` (true for a yard or open ground), `look`, and apart from it `court_side` with `court_seen_from` (the places whose camera sees that side), `note` |
| row `place` | `key`, `name`, `stem` (its picture's file name), `area`, `indoor`, `building`, `how` (`composed` or `inplace`), `batch`, `after` (the places whose chosen pictures it waits for, K8), `refs_also` (more reference pictures, used once chosen), `words` (what a new composition is built from), `camera` `[x, y]` and `facing`, `camera_in` (`doorway`) with `entered_from`, `old_picture` (`camera`: keep its camera and sides; `school`: only to know the school and the camera height), `clear` (4.6), `at` (its own point, where the building's will not do), `pinless`, `spare_doors`, `facts` (sentences a fixed fact adds to its prompt), `check` (extra yes/no lines), `note` |
| row `path` | `a`, `b`, `words`: the game's `PATH_LINKS` |
| row `exit` | `place`, `to`, `side` (`left`, `ahead`, `right`, `bottom`), `order` (from left to right; equal numbers are not ordered), `half` (`left` or `right`, for a bottom exit), `on` (`building` or `path`), `thing` (the building it sits on), `words`, `alias` (an older key for the same exit), `against` (what the owner is told when a version contradicts it) |
| row `seen` | a building seen from a place that no exit sits on: `place`, `thing`, `side`, `order`, `words` |
| row `window` | `room`, `wall`, `faces` (`north`, `east`, `south`, `west`, or null where it does not matter) |
| row `line` | `room`, `wall`, `shows` (the words after "Through the windows:"), `names` (the buildings it names, each of which must lie on the side the wall faces), `needs` (places whose pictures must be chosen before the line is used) |
| row `interior` | `room`, `words`: a chosen room's layout, read off its picture (not used in prompts) |
| `waived` | `{fact, picture, rev, date, words}` |
| `waits` | `{id, picture, batch, until_rev, what}`: something a new picture must put right that no tool can see |
