# The School Courtyard's layout, staged

Laid out on 12 Oct 2026 on the School Courtyard the owner chose (version B),
`~/Desktop/JJK Game images/ui2/early/chosen/school_yard_1920.png`, the fitted
copy of `ui2_school_yard_b_fit.png` (the render with its black strip cut off).
Every number is in the game's 1920 x 1080 frame. Nothing here is in the game
yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_school_yard.json` | every exit's and the planned look's point, the side its name opens, and its shape | yes |
| `view_school_yard.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_school_yard.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_school_yard__infirmary` | the small white annex on the left, whole: its roof, both walls, the side steps and the timber ramp up to the pale green door | (395, 730), on the green door | above |
| `go_school_yard__library` | the long hall ahead with the grey tiled roof, whole, as far as the schoolhouse's porch hides it, with the two stone steps under its double door | (1148, 722), on the double door | above |
| `go_school_yard__classroom` | the schoolhouse on the right, whole: from the roof's edge to the stone footing, with the side porch, its shoe lockers and its stone slab | (1500, 740), inside the porch | above |
| `go_school_yard__cafeteria` | the kerbed paved path at the bottom left, from the foot of the infirmary's ramp to where it leaves the picture (the dining hall is behind the camera) | (110, 990), on the path | above |
| `go_school_yard__courtyard` | the paving slabs at the bottom right, which run off the right edge by the schoolhouse's corner | (1695, 930), on the slabs' near tip | left |
| `pine_bench` (planned, a look) | the pine, crown and trunk, with the bench under it and the two small benches beside it (one polygon) | (832, 290), in the top of the crown | left |

The pine stands in front of the Library, so its shape lies over part of the
Library's: the pine's is the smaller and is on top, and the Library's door,
where its point is, is clear of it. No hotspot keeps a button and the yard
has no foreground outline. The schoolhouse reaches above the top bar and
through the toast lane; `check_layout.py` reports both and refuses neither
(the Courtyard's schoolhouse and hall do the same).

## Where people stand

The picture is seen from low down: its eye line is at about y 745 (the
schoolhouse's window sill runs level there; its boards above lean one way and
its footing the other). The Library's double door is the scale: 127 px tall,
taken as 200 cm; it stands on two steps, so `scale` is that door set down on
the ground at the steps' foot, [1148, 671, 800]. By it the bench's back is
about 87 cm and the porch's posts about 215 cm, which agree; a person on the
near ground measures a little under the game's usual size, so the yard draws
people at zoom 0.50 (0.46 a step back) instead of 0.52.

One person stands left of the pine; two stand either side of its trunk; both
rows leave every door's point clear. With three, the one on the right stands
over the Library's door (that exit is then in the icon column). With four,
the Infirmary's and the Library's are hidden: 2 of 5 things in the column,
4 tiles of 8. The pine's point is above every head, so the look is never
hidden; the porch, the path and the slabs are clear of every row.

## What I was unsure of

- **The eye line**, read to about 10 px. The scale's door is only 55 px
  below it, so 10 px either way moves the size a person "should" be by a
  sixth. The bench and the porch were used to cross-check it; the people were
  then judged by eye on the stage sheet.
- **The infirmary is painted small**: by the same measure its green door is
  about 1.4 m tall. People stand well in front of it, so it reads as a small
  annex further off; a person is never drawn beside its door.
- **The way back to the Courtyard.** The record says "the passage by the
  schoolhouse". The passage itself is not in the picture: what is there is
  the paving at the bottom right that leads off the right edge towards it.
  The exit is traced on that paving. Its point is on the slabs' near tip,
  because points may not lie right of x 1700; the shape runs on to the edge.
- **The cafeteria** is not in the picture either (the record puts it behind
  the camera); its exit is the path that leaves at the bottom left.
- **The porch** shows shoe lockers and a dark wall with a window band behind
  them, not a plainly painted door leaf. The whole schoolhouse is the shape,
  and the point is in the porch's opening.

## For whoever installs it, and for wave 1

- U4 registers `pine_bench` as a look, not front. Run `check_layout.py`
  again then, so that its name plate is measured and no longer guessed.
- `check_layout.py` reads `tools/bgs/campus.json`, where this yard is still
  a proposal; `check_campus.py --layout ... --record
  tools/art/staged/early/campus_for_batch3.json` passes.
- Words that describe the picture (hand-off, never edited here): the pine
  has one long bench and two small ones; the infirmary has a ramp; the
  Library's door has two steps.

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged. One thing was mended: the Library's shape ran 28 px over the end of
the schoolhouse's eave (its top right corner was square, [1296, 463] to
[1296, 506]); it now follows the eave's underside ([1272, 463], [1268, 469],
[1276, 484], [1298, 504]), so the eave end lights with the schoolhouse and
not with the Library. Nothing else was moved; both checks pass as before.
