# The Common Room's layout, staged

Traced on 12 Oct 2026 on the installed picture, `game/images/bg/dorm_common.png`
(render `ui2_dorm_common_a_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and
laid 4 px down: the two were compared and are the same picture, pixel for
pixel). Every number is in the game's 1920 x 1080 frame; edges were read from
gridded crops of the full-size render, and every outline was then laid over
the day, the evening and the night picture. The room was redone in place, so
neither file carries `for_rev`. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_dorm_common.json` | the exit's and the five things' points, the side each name opens, and the shapes | yes |
| `view_dorm_common.json` | where one to four people stand, the floor, the scale; the painted pose's box, kept as it was | yes |
| `check_dorm_common.json` | the eye line, and that the card table is the room's foreground object, for `tools/check_layout.py` only | never |

## What was kept, and what changed

- `view_dorm_common.json`: the `poses` key (`nobara__evening`, [248, 408, 632, 536]) is kept exactly as the game holds it. `slots`, `floor` and `scale` are new.
- `hot_dorm_common.json`: the exit's point (84, 540) and the television's (1590, 560) are the ones the game applies today; both still sit on their thing. The card table's point moved from the floor cushion (1400, 876) onto the low table (797, 742), as the plan asks (7.3, R13). The three planned looks are placed for the first time. `tips` and `shapes` are new.
- `tools/fg/dorm_common.json` is not touched: its outline fits the installed table on all three hours (the view sheet shows it).
- `tools/bgs/keep/dorm_common.json` is not touched: every row of it still fits the installed picture. Its two `doors` rows are what the exit-on-door rule reads, so the check file names no door of its own.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_dorm_common__dorm_yard` | the sliding glass door at the left edge: its glass from the top rail down, its post with the handle, to the foot of the leaf at y 1010. The small pane above the top rail (y 0 to 62) is left out, so that no corner sits on sky | (84, 540), on the third pane, where it is today | above |
| `card_table` (act; the room's foreground object) | the low table with the bowl and the controller on it: the same 23 points as the foreground outline, so the light lies exactly on what is drawn over the people | (797, 742), the table top's left end | above |
| `tv` (look) | the television: its screen and frame, and the stand's feet | (1590, 560), the middle of the screen, as today | above |
| `fridge` (planned, a look) | the small two-door fridge under the counter, front and left side, cut round the green bag | (1300, 690), on the lower door | above |
| `game_boxes` (planned, a look) | the board-game boxes on the bookshelf, one polygon for each pile | (702, 418), on the right pile | above |
| `manga_shelf` (planned, a look) | the bookshelf from its top board down to the sofa's back, cut round the sofa cushion | (702, 565), on the right of the middle shelf | above |

No hotspot keeps a button; no two shapes overlap; no two name plates meet.
The kettle, the microwave, the cushions, the sofa, the bags, the plant and
the window are not clickable. Every exit and thing the game registers or
plans for the room is in the picture: nothing had to be placed by the record
alone.

`card_table` is written under `front` in the check file. The game registers
it `front=False` today; the plan has wave 1 (U4) register it `front=True`
(7.3, "Layers"). Until then its light is drawn under the table's cut-out and
does not show on the table itself. This is for U4, not for this folder.

## Where people stand

**The eye line is y 600**, lower than the middle: the television's top and
bottom edges meet at y 597, the low table's top and its feet give 590 to 612,
the television cabinet's edges 615. **The scale** is the post left of the far
window, from the floor (y 800) to the top of the beam it carries (y 248),
552 px taken as 200 cm. By it the fridge and the counter come to 85 cm, the
low table to 38 cm high and 93 cm wide, the ceiling to 256 cm: all what such
things are.

The camera is low and close, so the floor at the front of the picture is very
near: a person standing there is far larger than the game's usual size. The
room's open floor is two pieces (the `floor` polygons), and people are drawn
at what the scale gives in each:

- **the strip between the low table and the far wall** (feet at y 838, zoom
  0.49, a step back): behind the table, which is drawn over their legs;
- **the boards along the front** (feet at y 962 to 965, zoom 0.67 and 0.68;
  the scale gives 0.75 there, so these are 10% under it, inside the 12%
  allowed, to keep the near people from filling the frame).

Nobody stands on the rug in front of the table (the table would be drawn over
their legs), on the cushions, or in the 35 cm between the sofa and the table.

| people | where | hidden |
|---|---|---|
| 1 | in front of the sofa's near arm (x 392) | nothing |
| 2 | the same, and one behind the table's right half, in front of the window (x 1040) | nothing |
| 3 | the same two, and one on the boards in front of the cushions (x 1290) | the fridge's point (a look: it waits until they move) |
| 4 | the same three, and a second behind the table's left half (x 860) | the fridge, the game boxes, the manga shelf, and the card table (an act: it is then in the icon column, 3 tiles of 8) |

**The audit's fault F5 is mended**: with three people the card table and the
television are both clear, where the code's row stood someone in front of
each. The way out and the television are never hidden. To get there the
points were put where the rows leave them clear: the card table's on the
table's left end (the person behind the table stands at its right half), the
shelf's and the boxes' on their right ends (the person by the sofa ends at
x 651), the fridge's on its lower door.

## What check_layout.py reports, and why it stands

- the door: 6% of its shape is above y 92, where no shape takes the pointer. The post really runs to the top of the picture; the point is far below.
- `tv`: 4% of it is inside the toast lane (the screen's top right corner). The television stands there; its point is below the lane.

`check_layout.py`: PASS (2 reported). `check_campus.py --layout`: PASS (0 reported, 18 waiting for a batch, none of them this room's layout).

## Corners a relight could move (laid over the evening and the night picture, and read)

Every outline follows an edge that stays in all three pictures. Named, as the
sitting asked:

- **on glass**: the door's left edge runs down the glass at x 0 (the picture's own edge), and its corner (0, 64) and (108, 64) sit on the top rail with the small sky pane just above. The keep list's four `windows` rows cover the panes below the rail, not the pane above it.
- **changed by the hour, inside a shape, not on its outline**: the television's screen (a reflection of the window in the evening, blue at night), the fridge's door (a sun patch in the evening).
- **the board-game boxes**: the evening and night pictures drew the boxes' printing a little differently (the boxes themselves did not move). The outlines sit on the boxes' edges, which agree in all three.
- **no corner of any shape lies on open floor.** Two standing points do: (1290, 962), on the boards at the rug's front edge, is crossed by the evening's sun streaks; (392, 965) is in shade at every hour.

## Unsure of

- **The near people are large** (zoom 0.67 and 0.68 against the game's 0.52; the tallest reaches from y 186 to y 965). It is what the picture's own furniture gives, and on the stage sheet they read as people standing just inside the door. If the owner finds them too large, the only floor where a person at 0.52 fits is behind the table, which holds two.
- **Panda in the place by the sofa** (drawn on `shots/stage/dorm_common_night_3panda.jpg`): his arm covers the right end of the way out's name (the plate runs from x 48 to 242 at y 475 to 504, his arm from about x 125). The door's glass gives the point nowhere higher that is clear of the arrival caption, and lower his legs cover the same end. He is not in this room by the timetable. With anyone else the name is clear.
- **The painted pose** (`nobara__evening`) was made on the room's old picture and at the old, smaller size. Its box covers the sofa, the manga shelf and the table's left end, and the person by the sofa stands in front of where she sits. The pose is a later sitting's; this layout does not move its box.
- **The eye line** is read to about 15 px from furniture edges (the room's wall beams do not agree with each other). At 585 every slot still passes the scale rule; at 615 the near people, already drawn 10% under the scale, come out 14% under it and are refused. So if the eye line is really lower in the picture than read, the near people want to be larger still, not smaller.
- **The exit is the door I stand in**: the picture is framed by the two leaves of the open glass door, and the garden is behind the camera. The left leaf was traced, as the keep list names it.
- The three planned name plates are guesses (150 by 29 px) until U4 registers the hotspots.

## For whoever installs it, and for wave 1

- U4 registers `fridge`, `game_boxes` and `manga_shelf` as looks, not front, and `card_table` `front=True`; run `check_layout.py` again then.
- The keep list's `scale` for pose prompts, [447, 235, 830], gives about 3 px a centimetre by the sofa, where this layout's scale gives 4.5: a pose written from it comes out two thirds the size of the people standing beside it. This layout's `scale` and eye line are the ones to copy.

## Second reading (the reviewer's pass)

Every shape was drawn again over the installed picture with a script of the
reviewer's own, enlarged, and over the evening and night pictures. Nothing
was changed: the door leaf, the low table (the same outline as
tools/fg/dorm_common.json), the television, the fridge, the game boxes and
the bookshelf each sit tight on their thing at all three hours; the two
people a step back have their feet (y 838) behind the table's far legs
(y 857) and inside the foreground's box; the near people stand left and
right of the table's outline (x 761 to 1150), never across it, so the cut-out
table is drawn over nobody it should not be. The `poses` key is as the game's
file holds it.
