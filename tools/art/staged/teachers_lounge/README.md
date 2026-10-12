# The Teachers' Lounge's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/teachers_lounge_1920.png` (render
`ui2_teachers_lounge2_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and
laid 4 px down; the fitted file and the render fitted that way are the same
picture, pixel for pixel). Every number is in the game's 1920 x 1080 frame;
edges were read from enlarged crops of the full-size render. Nothing here is
in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_teachers_lounge.json` | the two exits' and the two looks' points, the side each name opens, and the shapes | yes |
| `view_teachers_lounge.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_teachers_lounge.json` | the eye line and the boxes of the entrance and the stairs, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_teachers_lounge__staff_yard` | the open entrance in the left wall: the opening from the curtain rod down to the door track, with the door curtain, the fence and the paving seen through it, and the door's edge on the right | (300, 600), in the opening | above |
| `go_teachers_lounge__teachers_dorm` | the staircase at the right end of the far wall: both strings, the treads from the foot to the landing, and the opening at the top; cut round the sofa's back where the sofa stands in front | (1378, 620), on the lower treads at the right | above |
| `rota` (planned, a look) | the duty board on the right wall, frame and all; not the cord it hangs by | (1624, 480), on the board's bare lower right | below |
| `kettle` (planned, a look) | the kettle with the stove it stands on and the cupboard under the stove (the kettle alone is 37 by 35 px, smaller than a button); cut round the armchair's back | (895, 541), on the stove's front, below the kettle | below, on the cupboard doors |

No hotspot keeps a button; the room has no foreground outline. The
television, the sofas, the bar and the fridge are not clickable.

`check_layout.py` reports two things and refuses nothing: 39% of the board
and 2% of the staircase lie inside the toast lane, which a toast may cover
for a moment. Both are where the picture has them; their points are below
the lane.

## Where people stand

Eye line y 480: the top of the left wall's rail and the board's top and
bottom edges meet at (1136, 480). The scale is the entrance's right jamb,
[476, 280, 838], 558 px taken as 200 cm; the kitchen counter measured the
same way comes to 85 cm, which is what a counter is.

The open floor is on the right and along the bottom, as the sitting asked.
People stand on it in front of the sofa and the bar, feet at y 940, at zoom
0.53 (the scale gives 0.54 there); a step back, between the sofa and the bar,
feet at y 880 and zoom 0.47.

- One person stands in front of the sofa and hides nothing: the stairs'
  point was put on the right of the staircase and the kettle's on the stove
  so that this one place is clear of both.
- Two: the second stands in front of the stool and the bar; the stairs'
  point is hidden, so that way out is in the icon column. The board and the
  kettle are clear.
- Three and four: the board's point is hidden too (a look has no tile; it
  waits). The kettle and the entrance are never hidden. Four stand close
  together: the room leaves 363 px for them between the kettle and the
  stage's right limit.

Nobody stands on the stone entry floor, among the slippers or between the
chairs: the floor polygon is the boards right of the near armchair and the
strip along the bottom.

## Unsure of

- the right-hand crowd. Everyone stands in the right third, because a
  person's rectangle is 400 px wide and the kettle must stay clear for one
  and two people. If the kettle may be hidden, people could spread left
  towards the armchair; the rule as written says no.
- the kettle's shape. The kettle itself is too small to be a shape (5 184
  px at least), so the stove and its cupboard are lit with it. The other
  choice is `keep_tile` (a button on the kettle); the Principal's Office's
  photograph was done this way, so it was followed.
- the scale. The entrance is taken as 200 cm to the rod; the counter agrees,
  so this is less unsure than most.
- the planned name plates are guesses (150 by 29 px) until U4 registers the
  hotspots; the board's opens below and runs 40 px past the board onto the
  wall post.
- the evening and the night picture were made from this day picture; they
  were not opened here.
- the record's note on this picture (`art_13a_early.json`: "not fitted yet:
  the doll is changed first") is older than the picture chosen: the chosen
  one has no doll and has the bar.
