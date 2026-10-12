# The Training Yard's layout, staged

Traced on 12 Oct 2026 on the Training Yard the owner chose (version B),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_training_yard_b_00001_.png`,
as fitted to the game's frame in `chosen/training_yard_1920.png` (2752 x 1536
becomes 1920 x 1072, laid 4 px down). Every number is in the 1920 x 1080
frame; edges were read on enlarged crops of the full-size render. Nothing
here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_training_yard.json` | every exit's and the planned hotspot's point, the side its name opens, and its shape | yes |
| `view_training_yard.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_training_yard.json` | the picture's eye line, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_training_yard__courtyard` | the roofed passage at the bottom left: its low tiled roof, the open bay under it and the stone slab at its foot | (60, 700), in the open bay | right |
| `go_training_yard__training` | the training hall, whole: roof, gable, the wall with its paper screens, the veranda and its stone step (the passage's bay left out) | (485, 640), on the paper screen beside the open doorway | above |
| `striking_posts` (planned, Practice) | the row of five striking posts, one polygon round the row | (763, 760), on the nearest post | left |
| `go_training_yard__storehouse` | the white storehouse, whole: roof (with the ridge ornament, added by review 1), wall, door canopy and its steps | (945, 690), on its double door | above |
| `go_training_yard__staff_yard` | the flight of stone steps between the two stone walls, right of the storehouse, with the strip of ground at its foot | (1150, 690), on the steps | above |
| `go_training_yard__dojo` | the dojo, whole: the long low hall with the band of windows, from its roof down to its footing, as far as the pool gate hides it | (1560, 700), on the wall under the windows' right end | above |
| `go_training_yard__pool` | the roofed timber gate at the right edge: its roof, both posts, its side panels, the opening with the pool seen through it, and the stone threshold | (1690, 740), on the gate's left post | below |

The posts stand in front of the storehouse's corner; the smaller shape is on
top, so the posts answer there. No hotspot keeps a button. No shape is in
front of the people.

## Where people stand

The eye line is at y 700: the dojo's window sill is level there, and the
hall's eave and veranda lines meet it from the other side (both read on
crops; good to about 5 px). The scale is the pool gate's opening, the left
post from its foot (y 857) to the underside of the lintel (y 598), taken as
200 cm. By it the camera is about 120 cm up, the striking posts are about
150 cm, the dojo's sill about 120 cm and the storehouse door about 185 cm,
which agree with one another. A person on the near earth is therefore
smaller than the game's usual size: zoom 0.44, and 0.40 a step back, the
same as the Courtyard next door.

A person's rectangle at that size is 334 px wide and reaches up to y 430, so
it hides any point within about 200 px to either side. The seven points were
set so that two gaps are wide enough to stand in: between the passage and
the hall's doorway (x 272) and between the steps and the dojo's point
(x 1355). One person stands at 1355, two at 272 and 1355, and they hide
nothing. With three, one a step back stands in front of the storehouse
(its exit is then in the icon column). With four, the hall's doorway and the
storehouse are hidden: 2 of 7 things in the column, 4 tiles of 8. The
striking posts are clear of every row.

## What the checks said

`check_layout.py`: PASS. Three REPORT lines, none mended: 6% of the dojo's
shape is inside the toast lane (its roof runs up to the right edge of the
picture); 6% of the training hall's shape is above y 92 and 2% of it is in
the banner lane (its roof fills the top left corner). A building is traced
whole, and the Courtyard's two buildings report the same. `check_campus.py
--layout ... --record tools/art/staged/early/campus_for_batch3.json`: PASS.

The way to the pool can be locked and its reason is a wide label: opened
above the gate it would have covered the way to the dojo (`check_layout.py`
refused that), so the pool's name opens below its point.

## What I was unsure of

- The dojo's door. The record says "its door faces the yard", and the
  picture shows no door on the dojo: only boarding and the band of windows.
  The building is traced whole and its point is on the wall.
- The passage back to the Courtyard is read as the roofed bay at the bottom
  left with the stone slab leading into it; the picture does not show where
  it goes.
- Two people stand far apart (1,083 px), one by the hall and one by the
  dojo, so that neither covers a way out. Standing them together in the
  middle would hide the storehouse and the steps.
- The scale rests on the gate's opening being about 2 m. If the owner finds
  people small here, the eye line and this one measure are what to look at.
- The right part of the pool gate lies under the icon column; its point is
  on the left post, clear of it.

## For whoever installs it, and for wave 1

- Wave 1 registers `striking_posts` (Practice, not front). Run
  `check_layout.py` again then, so that its name plate is measured.
- The evening and night pictures of the yard must keep these buildings where
  they are: the shapes are traced on the day picture.
