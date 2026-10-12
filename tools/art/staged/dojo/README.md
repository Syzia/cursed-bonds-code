# The Dojo's layout, staged

Laid out on 12 Oct 2026 on the Dojo the owner chose (O46),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_dojo2_a_00001_.png`, traced
on its fitted copy `~/Desktop/JJK Game images/ui2/early/chosen/dojo_1920.png`.
Every number is in the game's 1920 x 1080 frame. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_dojo.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_dojo.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_dojo.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line and the box of the painted door | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_dojo__training_yard` | the open sliding doorway at the left, from its lintel down to the sill: the yard, its striking posts and the big hall are seen through it | (215, 600), in the left half of the opening | above |
| `wall_shrine` (planned, a look) | the shrine shelf high on the end wall: its top board, the rope, the little shrine with its two green sprigs, and the shelf | (1288, 372), on the left sprig | left |
| `weapon_rack` (planned, an act) | both racks under the shrine, one polygon each: the sword rack with its five swords and its feet, and the stand of staffs, wooden swords, the naginata and the spear, round each tip | (1522, 636), low on the stand | below |

No hotspot keeps a button. Nothing is in front of the people.

## Where people stand

The eye line is at y 567: the door's lintel and sill, and the side wall's
sill and skirting, meet there. The scale is the doorway's right post, sill
to lintel (y 248 to 886, 638 px, taken as 200 cm). By it the camera is about
a metre up, and a person at the game's usual size (zoom 0.52) has their feet
at y 912, a step inside the door; the two a step back are at 0.47, feet at
y 878. All of them stand on the open boards between the door and the racks.

One, two and three people hide nothing. With four, the fourth (x 1150)
stands under the shrine and covers its point, so the shrine waits until they
move (a look has no tile in the column); the door and the racks stay clear
in every row.

## What the checks say

- `check_layout.py` REFUSES the two files on one thing only: they carry
  `for_rev`, and the record's `place.dojo` row still says `how: inplace`
  (the first plan). The picture was composed again (O45, O46; the early
  record's `pictures.dojo.kind` is `composed`, and its `about` says the real
  record takes `how: composed` when the room is installed). With a copy of
  the record in which that one word is `composed`, the layout PASSES with
  nothing else refused. Whoever installs it sets the row first; the files
  need no change.
- REPORT, in-lane: 47% of the shrine's shape is inside the toast lane. The
  shrine is painted there; its point is left of the lane (x 1288), so the
  point's square is clear. A toast may cover the shrine's right half while
  it shows. Left as it is.

## Unsure of

- The door is taken as 200 cm. If a dojo's door is taller the people should
  be a little smaller; by the staffs in the stand (about 185 cm by this
  scale) it holds.
- The right post of the door frame (x 366 to 400) is left out of the exit's
  shape: the shape is the opening itself.
- `wall_shrine` opens its name to the left, over the wall and the edge of
  one hanging lamp.
- The Dojo has hour pictures (evening, night, lit) relit from this one, so
  the layout holds for them; none was looked at here.
