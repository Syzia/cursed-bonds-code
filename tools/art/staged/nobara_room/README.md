# Nobara's Room's layout, staged

Laid out on 12 Oct 2026 on the room the owner chose on 11 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_nobara_room2_b_00001_.png`,
as it is fitted in `ui2/early/chosen/nobara_room_1920.png` (1920 x 1072, laid
4 px down). Every number is in the game's 1920 x 1080 frame, read from
gridded crops of the full-size render. Nothing here is in the game yet. The
evening, night and lit pictures were made from this one; the shapes were
drawn over all three and sit on the same things.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_nobara_room.json` | the exit's and the two planned hotspots' points, the side each name opens, and the shapes | yes |
| `view_nobara_room.json` | where one to four people stand, the floor, the scale | yes |
| `check_nobara_room.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_nobara_room__girls_dorm` | the brown door in the left wall, with its frame, down to the bottom edge | (205, 560), beside its handle | above |
| `bed_nobara` (planned, a look) | the bed: its three pillows, the quilt, the mattress and the timber frame, from where the wall's edge cuts it to its foot (the bedside table and lamp left out) | (376, 715), at its left end | above |
| `mirror` (planned, a look) | the tall dressing mirror in its frame, with its two feet | (1108, 395), in its top right corner | above |

No hotspot keeps a button; no two shapes overlap; nothing is in front of the
people. The clothes rail, the bags, the hats, the desk with the tool roll
and the window are not clickable (the game plans nothing for them).

## Where people stand

The eye line is at y 440 (the door's head and foot and the window's head and
sill meet between y 410 and y 455). `scale` is the door's leaf at its
right-hand edge, [259, 116, 981], taken as 200 cm; by it the desk is 72 cm
high and the mirror 156 cm. People stand on the round rug: feet at about
y 855 at zoom 0.50, which is what the door gives to within 1% (a step back:
y 815 at 0.46, on the rug's far edge).

The points are at the bed's left end and the mirror's top right corner so
that two people fit between them: one (x 745), two (610, 880) and three
(with one a step back at 745) hide nothing. Four are a close row (610, 757,
903, 1050; 147 px between them): the fourth stands in front of the mirror,
whose point is then hidden (a look, which waits until they move); the row
cannot spread further left without hiding the bed too, which the rule
refuses, nor further right, where the desk is. The door is never hidden.

## What check_layout.py reports, and why it stands

- the door's shape is 3% above y 92: the head of its frame. Its point is
  far below.

`check_campus.py --layout ... --record tools/art/staged/early/campus_for_batch3.json`
reads PASS: the door is in the left third, where the early record's first
guess has it.

## What I was unsure of

- **Four people are crowded,** and their name tags (232 px apart at the
  least) spread wider than they stand. It is a small bedroom; one to three
  read well.
- **The plant's leaves cross the mirror's right edge.** The shape is the
  mirror's frame, straight through the leaves.
- **The shopping bags and the tool roll** are in the record's words for the
  room and have no hotspot planned; nothing lights on them.

## For whoever installs it, and for wave 1

- U4 registers `mirror` and `bed_nobara` as looks, neither front. Run
  `check_layout.py` again then: their name plates are guessed at
  150 x 29 px until the game measures them.
- The mirror shows the door and the quilt, nobody in it: a look line can
  say so.
