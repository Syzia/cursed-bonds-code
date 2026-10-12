# The Dormitory Garden's layout, staged

Laid out on 12 Oct 2026 on the garden the owner chose on 7 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_dorm_yard_a_00001_.png`, as
it is fitted in `ui2/early/chosen/dorm_yard_1920.png` (2752 x 1536 becomes
1920 x 1072, laid 4 px down). Every number is in the game's 1920 x 1080
frame and was read from gridded crops of the full-size render. Nothing here
is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_dorm_yard.json` | every exit's and hotspot's point, the side its name opens, and its shape | yes |
| `view_dorm_yard.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_dorm_yard.json` | the picture's eye line, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_dorm_yard__boys_dorm` | the dark timber house on the left, whole: gable, roof, gallery, the outside stair, down to its foot stones. The small roofed building with the studded door in front of it (far left) is left out | (345, 575), on the door under the blue curtain | above |
| `go_dorm_yard__trailhead` | the flight of stone steps that climbs behind the boys' dormitory, and the dirt path from its foot along the house as far as the outside stair | (600, 638), on the dirt path | left |
| `go_dorm_yard__rooftop` | the tower, as much as shows above the common room's roof | (945, 300), on its lower storey | above |
| `go_dorm_yard__dorm_common` | the common room, whole: roof, front, and the deck over the pond | (1040, 535), on the left glass doors | above |
| `go_dorm_yard__girls_dorm` | the white plaster house on the right, whole, with the door slab under the red curtain | (1700, 640), on the wall just left of the door | left |
| `go_dorm_yard__courtyard` | the flight of stone steps at the bottom left, whole | (215, 925) | above |
| `go_dorm_yard__staff_yard` | the flight of stone steps at the bottom right, with the paving at its foot | (1640, 990), on the paving at the foot | above |
| `pond` (planned, a look) | the pond with its rim of stones and the nearer stone lantern | (540, 790), on the water at its left end | left |
| `lit_windows` (planned, a look, at Night) | three lattice windows of the girls' dormitory: the larger one downstairs and the two larger ones upstairs (three polygons) | (1622, 520), on the downstairs one | above |

No hotspot keeps a button. The windows lie on the girls' dormitory's shape;
the smaller shape is on top, as the rule gives. No other two shapes overlap.

## Where people stand

On the flagstones along the bottom edge, feet at about y 992 (a step back:
y 963). The eye line is at y 530 (the boys' dormitory's eaves and foot line
meet at y 540, the girls' at y 527, and the lower window rails of the girls'
house agree). `scale` is the girls' doorway, from the curtain rail to the
sill, [1790, 458, 680], taken as 200 cm. By it a person on the flagstones
measures about 590 px, and people are drawn at zoom 0.48 (0.44 a step back),
7 to 9% under that: the picture's near things (the nearer lantern, the steps
either side) are painted small against that door, and at 0.52 people stood
too tall beside them.

One person (x 818) and two (818, 1262) hide no point at all. Three: the one
a step back stands over the common room's point. Four: the common room's
and the mountain path's points and the pond's (a look, which has no tile):
2 of 7 exits in the column, 4 tiles of 8. The boys' and girls' doors, the
tower and both flights of steps are never hidden.

## What check_layout.py reports, and why it stands

- the boys' dormitory, the girls' dormitory and the tower reach above y 92
  (2 to 5%): their roofs; a traced building is traced whole.
- the tower is 30% inside the banner lane, the girls' dormitory 31% and the
  windows 45% inside the toast lane, the common room 1%: that is where they
  are painted. Every point is clear of both lanes.

## What I was unsure of

- **The way to the staff building.** The record's words are "the stepping
  stones east, to the staff building steps". In the picture the stepping
  stones run from the flagstones up to the girls' door, and what leads east
  and out of the picture is the flight of steps at the bottom right. The
  exit is traced on that flight; the stepping stones are not clickable.
- **The girls' door is right of x 1700,** where no point may be (the icon
  column). The point is on the wall beside the door; the shape is the house.
- **The mountain path's point** must lie left of x 640 (the record: left
  third), so it is on the dirt path, not on the stone steps themselves
  (x 710 to 832). The steps are inside the shape.
- **Which windows are "the lit windows".** No night picture of the garden is
  made yet. The girls' lattice windows are the plainest windows in view (the
  boys' house shows none; the common room's glass is its doors). If the
  night picture lights others, the three polygons are redrawn then.
- **The building at the far left** (tiled roof, studded door) is read as a
  separate building and is not clickable.
- The second pagoda (`pagoda_east`, O35) is a landmark and has no shape; its
  row in the campus record is the installer's, not written here.

## For whoever installs it, and for wave 1

- U4 registers `pond` and `lit_windows` as looks, neither in front; run
  `check_layout.py` again then, so that their name plates are measured.
- The reason shown on the girls' locked door (505 by 115 px) opens to the
  left of its point and covers no other exit.

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged. One thing was mended: the pond's near edge lay 15 to 25 px out on
the grass (y 880 from x 700 to 1258); it now follows the water's edge at
y 864 to 866, and still takes in the rim stones at the left and the nearer
lantern's base. Nothing else was moved; both checks pass as before. The
reading of the way to the staff building (the bottom-right flight, not the
stepping stones, which lead to the girls' door) was looked at again and kept:
it is the owner's to confirm.


**At the install (12 Oct):** the tower's point moved from (945, 300) to (1010, 300) and the Common Room's from (1040, 535) to (990, 535), each still on its own building. The campus record's ground plan does not let the tower stand left of the Common Room as seen from the garden, and the installer refused the first points for it.
The name of the way to the Mountain Path opens to the right, not the left: opened left it covered the Boys' Dormitory's square (found by p2_paths in the game).
