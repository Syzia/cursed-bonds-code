# Panda and Toge's Room's layout, staged

Laid out on 12 Oct 2026 on the room the owner chose on 11 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_senpai_room_a_00001_.png`, as
it is fitted in `ui2/early/chosen/senpai_room_1920.png` (1920 x 1072, laid
4 px down). Every number is in the game's 1920 x 1080 frame, read from
gridded crops of the full-size render. Nothing here is in the game yet. The
evening, night and lit pictures were made from this one; the shapes were
drawn over all three and sit on the same things.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_senpai_room.json` | the exit's and the three planned hotspots' points, the side each name opens, and the shapes | yes |
| `view_senpai_room.json` | where one to four people stand, the floor, the scale | yes |
| `check_senpai_room.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_senpai_room__boys_dorm` | the sliding door of dark boards in the left wall, with its lintel and sill, as far as the picture's left edge shows it | (92, 520), beside its handle | above |
| `bed_panda` (planned, a look) | the very large futon at the far left, with the two pillows at its head | (882, 705), at its right-hand end | above |
| `shogi_board` (planned, a look) | the shogi board on its four legs, and the two cushions beside it (three polygons that do not touch) | (985, 850), on the board's front face | below |
| `bed_toge` (planned, a look) | the small futon on the right, with its pillow | (1500, 850), on its near half | above |

No hotspot keeps a button; no two shapes overlap; nothing is in front of the
people. The window, the chest and the paper lamp are not clickable (the
game plans nothing for them).

## Where people stand

The picture is seen from low down: its eye line is at y 518 (the window's
head and sill, the gallery rail, and the ceiling's and the floor's corner
lines meet between y 505 and y 545). `scale` is the door's leaf at its
right-hand edge, [134, 118, 912], taken as 200 cm.

The open floor is the mats on the left, between the left wall, the large
futon and the left cushion, and people stand there: feet at about y 838 at
zoom 0.50 (the door gives a person 2% smaller). A third person stands a step
back on the strip of mat between the large futon and the cushions (x 805,
feet at y 798, zoom 0.44), and a fourth further in, in front of the chest
(x 1090, feet at y 745, zoom 0.36): the room is deep and each is the size
the door gives at that depth, to within 4%. The floor in front of the board
is too close to the camera for people of the game's usual size.

One person (x 490) and two (360, 615) hide nothing. The third hides the
large futon's point, and so does nobody else: a look has no tile in the
column, so it waits until they move. The door, the board and the small
futon are never hidden.

## What check_layout.py reports, and why it stands

- the door's shape is 1% above y 92: the top of its lintel at the picture's
  left edge. Its point is far below.

`check_campus.py --layout ... --record tools/art/staged/early/campus_for_batch3.json`
reads PASS: the door is in the left third, where the early record's first
guess has it.

## What I was unsure of

- **How tall the door is.** Taken as 200 cm it makes the camera 100 cm up,
  the cushions 54 cm wide and the ceiling 2.8 m. If it is an old house's
  180 cm door, everyone should be about a tenth larger; zoom 0.50 at this
  depth lies between the two readings and inside the rule for either.
- **The fourth person is small** (zoom 0.36) because the only free floor
  left is at the far wall. It reads as depth on the stage sheet; if the
  owner dislikes it, the fourth can only stand in the left group.
- **Panda is wider than the others** (880 px canvas): at x 490 alone he
  covers most of his own futon, not its point.
- **The cushions light with the board.** If only the board should light,
  drop the second and third polygons.

## For whoever installs it, and for wave 1

- U4 registers `shogi_board`, `bed_panda` and `bed_toge` as looks, none of
  them front. Run `check_layout.py` again then: their name plates are
  guessed at 150 x 29 px until the game measures them.
- The record's words say "a shogi board on the floor between them": it is,
  with a cushion each side.

## Second reading (12 Oct 2026)

Drawn again over the picture, enlarged, by a second reader. Three shapes
were tightened; no point, slot or floor line moved.

- `shogi_board`, the board's polygon: its right side stood 10 px off the
  board (x 1092, now 1082), and its foot line cut through the three legs
  that show (the near-left leg's left third, the far-left leg and the
  right leg's left edge lay outside). It now follows the top face, the two
  side faces and each leg.
- `shogi_board`, the right cushion's polygon: it began at x 1096 and left
  out the strip of cushion beside the board (x 1083 to 1096); its right
  corner stood 11 px off. It now starts at the board's edge and ends on
  the cushion's corner (1262, 866).
- `bed_toge`: the far edge and the foot end stood 6 to 9 px outside the
  futon, on the wall's skirting; pulled in onto the futon.
- `bed_panda`: the right shoulder pulled in 4 to 5 px.
