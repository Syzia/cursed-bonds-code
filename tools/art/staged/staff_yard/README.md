# The Staff Building Steps' layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/staff_yard_1920.png` (render
`ui2_staff_yard_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid
4 px down). Every number is in the game's 1920 x 1080 frame; edges were read
from enlarged crops of the full-size render. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_staff_yard.json` | every exit's and hotspot's point, the side its name opens, and its shape | yes |
| `view_staff_yard.json` | where one to four people stand, the ground, the scale | yes |
| `check_staff_yard.json` | the picture's eye line, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_staff_yard__office` | the principal's hall, whole (both roofs, the porch, what shows above the white wall) and the stone steps up to it, between their two stone side rails: one polygon | (960, 440), on the top of the hall's doors, above everyone's head | above |
| `go_staff_yard__gojo_office` | the small detached office on the left, whole: roof, front, side wall and its door step | (480, 448), on the white gable, above everyone's head | below |
| `go_staff_yard__utahime_office` | the pavilion with the round window, whole: gable, skirt roof, walls, the bench-deck and its step | (1350, 618), on its paper door | below |
| `go_staff_yard__teachers_lounge` | the two-storey teachers' house, as much as shows: from the roof's edge to the veranda, cut along the bamboo fence that stands in front of it | (1680, 610), on the red door curtain | above |
| `go_staff_yard__dorm_yard` | the paved path at the bottom left, whole: from the picture's edge up to the foot of Gojo's door step (review 1 redrew it: the first outline stopped at the kerb joint and its upper edge ran about 20 px inside the paving) | (110, 985) | above |
| `go_staff_yard__training_yard` | the walled way down at the bottom right: the tile-capped wall, the strip of paving that leads to it and the flight of steps, to the picture's edge | (1650, 905), on the steps | left |
| `stone_lanterns` (planned, a look) | **the picture shows no stone lantern.** Placed on the nearest stone things where lanterns would stand: the two square stone posts at the foot of the steps, each with the sloping stone rail above it (two polygons) | (1146, 728), on the right post | right |

No hotspot keeps a button; the place has no foreground outline. No two
shapes overlap: the hall's shape runs between the rails, and the pavilion's
is cut round the head of the walled way's cap.

Not clickable, on purpose: the dirt track
that goes off behind the buildings at the far left; the unnamed timber
building at the left edge; the middle paved path (the ground people stand on).

## Where people stand

Eye line y 610 (the middle path's two kerbs meet at y 620, the teachers'
house's eave and balcony rail at y 600). The scale is the door of Gojo's
office, [612, 580, 745], 165 px taken as 200 cm. By it a person on the near
gravel (feet at y 1036) is about 450 px tall, so people are drawn at zoom
0.40, and 0.36 a step back (2% and 3% over the scale; 12% is allowed). They
are smaller than the game's usual 0.52, as in the Courtyard.

Everyone stands on the left gravel and the middle path, x 300 to 950, because
the right half holds four of the things to click and the only look's point is
on the right post. No row of one to four people hides anything: the two
points on the left are above the heads (Gojo's on the gable, the hall's on
the top of its doors), the path's point is left of the rows, and 0 of 6 exits
drop into the icon column with four people.

## What check_layout.py reports, and why nothing is mended

- the hall's shape: under 1% in the toast lane and under 1% in the banner
  lane (its ridge and right eave tip): it is the building's real outline;
- the teachers' house: 20% in the toast lane (its upper storey and roof): the
  same. Its point and its door are below the lane.

## Unsure of

- `stone_lanterns`: the owner or U4 decides whether the look is rewritten for
  the stone posts, lanterns are painted in, or the hotspot is dropped.
- the path to the garden is lit whole, so its top end touches Gojo's door
  step (the step itself is his office's). If the owner would sooner have only
  the near stretch lit, cut the polygon at the kerb joint, (442, 803) to
  (463, 859).
- Gojo's name opens under a point on his gable, not on his door, so that
  nobody standing in front of the office hides it. With the point on the door
  (612, 655) a row would have to leave x 424 to 800 empty.
- his lock reason is 503 px wide; opened below the gable point it lies over
  his own front wall and covers no other exit (above or right it would cover
  the hall's square, which the check refuses).
- the planned name plate of `stone_lanterns` is a guess (150 by 29 px) until
  U4 registers it; it clears Utahime's plate by 9 px.
