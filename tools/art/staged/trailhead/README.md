# The Mountain Path's layout, staged

Laid out on 12 Oct 2026 on the Mountain Path the owner chose on 7 Oct (O36),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_trailhead_sa_b_00001_.png`,
as fitted in `~/Desktop/JJK Game images/ui2/early/chosen/trailhead_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_trailhead.json` | every exit's and the planned hotspot's point, the side its name opens, and its shape | yes |
| `view_trailhead.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_trailhead.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_trailhead__forest` | the level dirt path on the left, from where it joins the open ground back to where it goes in between the cedars, with the gap of woods between the two near trunks that it leads into (one polygon) | (165, 628), on the far end of the path | above |
| `go_trailhead__ridge` | the stone stairs, whole: the lower flight with its two stone kerbs, the upper flight, and the thin far flight up to the top; and the black dome on the hilltop they lead to (two polygons, 4 px apart at the hilltop). The outline goes round the standing stone's top, so the stone is not inside it | (858, 365), on the upper flight, above every head | above |
| `go_trailhead__bathhouse` | the bathhouse, whole: roof and chimney, the walls, the porch and door, the water basin, and the two board fences in front of it down to their stone footing | (1570, 560), on the right-hand fence | above |
| `go_trailhead__riverside` | the dirt path on the right that runs down beside the river, from the foot of the stone wall to where it leaves the picture at the bottom right | (1680, 890), on the path | left |
| `go_trailhead__dorm_yard` | the stone slabs at the bottom of the picture (the garden is behind the camera, and the slabs are the way back to it) | (900, 995), on the slabs | above |
| `standing_stone` (planned, a look) | the mossy standing stone behind the low gate, down to the gate's top rail | (912, 610), on the stone | left |

No hotspot keeps a button. Every exit's thing is in the picture: nothing was
placed on a guess.

`check_layout.py` reports two things and refuses none: 14% of the bathhouse
(the right half of its roof) lies in the toast lane, and 11% of the stairs'
shape (the top of the dome) lies in the banner lane. Both are the picture's:
the building and the dome are where they are, both points are well outside
the lanes, and the Courtyard's hall roof is reported the same way.

## Where people stand

The picture is seen from standing height. Its eye line is at about y 517:
the bathhouse door (taken as 200 cm: 100 px, y 503 to 603) and the low gate
in front (posts 244 px tall at y 900, which is then about 108 cm, a
waist-high gate) agree on it, and by it the standing stone is about 160 cm.
`scale` is the bathhouse door, [1350, 503, 603].

By that measure a person on the near ground is smaller than the game's
usual size, as in the Courtyard: 0.43 with the feet at y 1003, and 0.395 a
step back with the feet at y 965 (both within 1% of what the scale gives).
On the stage sheet they stand a head and a half above the gate, which reads
right.

- One person stands left of the gate (x 600).
- Two stand either side of the gate (x 400 and 1290).
- Three: two on the left, one on the right.
- Four: two on the left, two on the right. Nobody ever stands in front of
  the gate, because the standing stone is the only thing to look at here
  and a row may not hide it.

No row hides any point: with four people nothing drops into the icon column
(2 tiles of 8). That is why the bathhouse's point is on its right-hand fence
and not on its door (the person on the right would cover the door), why the
forest's is at the far end of its path, and why the slabs' point is left of
centre.

## What I was unsure of

- **The eye line** is read to about 25 px: the picture has no long straight
  lines running away from the camera, so it comes from two things of
  guessed height (a door, a low gate). A door 190 cm tall would put people
  5% smaller, inside the rule's 12%.
- **The forest's shape** is closed at the top by an arch (y 468 at its
  highest, down to y 500 to 512 at the two trunks): the woods the path leads
  into have no edge of their own, so where the top lies is a choice. (The
  second reading, 12 Oct 2026, rounded it; it was a straight line at y 470
  and read as a box.)
- **The dome is part of the way to the ridge.** It is where the ridge is,
  and it lights with the stairs. If the owner would rather only the stairs
  light, the first polygon is removed and nothing else changes.
- **The slabs' polygon** follows the group of slabs as one outline, not
  each slab, and runs to the bottom edge of the picture (y 1076).

## For whoever installs it, and for wave 1

- The record (`tools/art/staged/early/campus_for_batch3.json`) fixed the
  five ways from a first guess read by eye; this layout keeps every side
  (`check_campus.py --layout ... --record` passes) and moves each point
  onto its traced thing. The real rows are written by
  `install_redo.py --compose` at the install.
- U4 registers `standing_stone` as a look, not front. Until then its shape
  is in the file and the game does not draw it; run `check_layout.py`
  again then, so that its name plate is measured and not guessed.
- The riverside path's shape reaches the right edge, under the icon
  column; its point is at x 1680, clear of it.
- The low gate is not a hotspot and has no shape: nothing in the game's
  list is the gate.
