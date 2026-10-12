# Yuji's Room's layout, staged

Laid out on 12 Oct 2026 on the room the owner chose on 11 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_yuji_room_b_placed_00001_.png`
(room B with the posters placed on it), as it is fitted in
`ui2/early/chosen/yuji_room_1920.png` (1920 x 1072, laid 4 px down). Every
number is in the game's 1920 x 1080 frame, read from gridded crops of the
full-size render and checked by drawing the outlines back onto it. Nothing
here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_yuji_room.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_yuji_room.json` | where one to four people stand, the floor, the scale | yes |
| `check_yuji_room.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_yuji_room__boys_dorm` | the sliding door in the left wall, with its recess, from the head rail to the sill | (285, 560), on the leaf | above |
| `bed_yuji` (planned, a look) | the bed, whole: pillow, blanket and the timber base | (445, 718), on the pillow | above |
| `film_shelf` (planned, a look) | the shelf of films with the stack of tapes on its top; its lower left corner, which the blanket covers, belongs to the bed | (985, 665), on the middle shelf | above |

No hotspot keeps a button; no two shapes overlap (2 to 4 px lie between the
bed and the shelf where the blanket hangs in front of it). The posters, the
television, the cushion and the window are not things to click: the game
has no hotspot for them.

## Where people stand

The eye line is taken at y 500: the door's head and sill lines meet at
y 483, the window's top and sill at 505, the two walls' foot lines at 523.
`scale` is the door's right-hand edge, [348, 262, 862], taken as 200 cm; the
film cases on the shelf (19 cm, about 45 px) agree with it to within 7%. By
it a person at the game's usual size (zoom 0.52) has their feet at y 916, and
a step back (0.47) at y 876: open boards, in front of the bed and of the
cushion. The cushion's footprint is a part of the floor nobody stands on.

One person (x 732) stands in front of the bed's foot end; two (732, 1300):
the second in front of the television, by the window. Neither row hides a
point. Three: the one a step back stands over the film shelf's point (a
look, which waits until they move). Four (690, 925, 1160, 1395): the same;
the bed's point on the pillow and the door stay clear in every row, which is
why the bed's point is on the pillow and not in the middle of the blanket.

## What check_layout.py says

PASS, nothing reported. `check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS.

## What I was unsure of

- **The eye line.** The picture's lines do not meet at one height (483 to
  523); 500 is the middle. At 483 or 523 the people are still within 5% of
  what the door gives.
- **Four people are a close row** (235 px apart) and cover most of the
  posters; the room is small.
- **The door's shape takes the whole recess**, 6 to 10 px more than the leaf
  at the top, so that the dark gap above the leaf lights with it.

## For whoever installs it, and for wave 1

- U4 registers `film_shelf` and `bed_yuji` as looks; neither is front. Run
  `check_layout.py` again then: their name plates are measured, not guessed
  (150 x 29 px today).
- The room's evening, night and lit pictures were made from this picture, so
  the layout holds for them; look at the pot plants a relight added on the
  sill (Method note 39) before installing those.
