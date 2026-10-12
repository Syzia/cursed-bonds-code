# The Rooftop's layout, staged

Traced on 12 Oct 2026 on the Rooftop as it is installed, `game/images/bg/rooftop.png`
(redone in place; render `ui2_rooftop_a_00001_.png`, 2752 x 1536, used for the
zoomed crops). Every number is in the game's 1920 x 1080 frame. The room had no
`hot_rooftop.json` and no `view_rooftop.json` before: nothing was replaced, and
neither file carries `for_rev` (a room redone in place). It has no keep list and
no foreground: nobody stands behind anything.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_rooftop.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_rooftop.json` | where one to four people stand, the deck they stand on, the scale | yes |
| `check_rooftop.json` | the picture's eye line, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `rooftop_view` (planned, a look) | the school seen below, two polygons: the cluster of grey roofs round the paved court, from the hall on the left to the roof at the right, cut where the trees cover it and along the top of the railing's top rail; and the five-storey pagoda, spire to the trees at its foot | (1322, 505), on the pagoda, right of every row of people | right |
| `railing` (planned, an act: "Sit a while") | the railing, two polygons: from the left post's edge (x 124) to where its rails end against the right post (x 1742), from the top of the round top rail down to the foot of the deck-edge beam, the gaps between the rails included; and the short piece right of the right post, to the picture's edge | (1560, 745), on the middle rail, right of every row | above |
| `go_rooftop__dorm_yard` | a band of the deck's planks along the bottom edge, from the left post's edge to the right edge: the way down is behind the camera | (1560, 995) | above |

No hotspot keeps a button. The view's and the railing's shapes do not overlap:
the view stops at the top rail's upper edge.

Left out of the view on purpose: the far hills, the valley town and the sky
(the whole vista is more than two fifths of the frame, which the shape rules
refuse), and the roof seen through the railing's gaps at about (930 to 1010, 730
to 760), which is inside the railing's shape.

## The exit: its stair is not in the picture

The picture shows no stair, hatch or door. The game's point today, (1680, 640),
sits on the trees beside the right post, on nothing that leads anywhere. The
campus record has no row for this exit (only `exit.dorm_yard.rooftop`, the
other way, and `place.rooftop`), so nothing says which side the stair is on.
The roof's beams overhead and the two posts say the camera stands under the
tower's roof looking out, so the way down is behind it: the exit is the band
of deck along the bottom, as the Courtyard's and the Library's are. Its point
is at the right, where it was, under the railing's point and clear of every
row of people.

## Where people stand

On the deck, this side of the railing: the floor polygon starts at the foot of
the deck-edge beam and nobody's feet are near it (near feet at y 1040, a step
back at y 1030; the beam's foot is at y 947 on the left and 824 at the right
post). Nobody stands on or beyond the railing.

The eye line is at y 500: the railing's top rail and the foot of the deck-edge
beam, both straight, meet at about (5900, 490 to 505). The camera is taken to
be at a standing person's eye height (the heads of the people at the game's
usual size come just above that line, as they should). By that the railing at
x 1000 (top rail's top y 704, beam's foot y 885, 181 px) is about 75 cm high,
a low temple railing, and `scale` is that railing carried up to 200 cm:
[1000, 405, 885]. People are drawn at the code's own sizes, zoom 0.5 (0.48 a
step back), which is within 2% of the scale. On the stage sheet the top rail
comes to the upper thigh of a person standing a good step this side of it.

The rows are the code's own (one at x 700; two at 470 and 930; three at 330,
700, 1070), except the four-person row, drawn in (320, 570, 820, 1066
where the code has 240, 540, 860, 1160): at the left so that a wide figure
(Panda) does not stand over the near post, which is in front of everybody, and
at the right so that the pagoda's point stays clear even of his 880 px canvas
(it ends at x 1286, where the point's square begins).
All three points are right of every row: nothing goes to the icon column with
one to four people. No name opens under the arrival caption.

People stand in front of the school's roofs (never of the pagoda): the view's
point is on the pagoda for that reason.

## What the checks say

`check_layout.py`: PASS, nothing reported (one NOTE: no hotspot keeps a
button). `check_campus.py --layout`: PASS, nothing reported.

## The evening and the night

Every outline was laid over `rooftop_evening.png` and `rooftop_night.png` and
read: the roofs, the pagoda, the railing and the planks are where they are by
day. Corners a relight proof may look at twice:

- the exit's band: its top edge (y 968, x 124 to 1920) and its two right
  corners lie on open planks crossed by the railing's shadow and by sunlight
  (by day and evening) and by moonlight at night. The planks' seams are in
  every window; the band's left end is on the left post's edge;
- the view, at night: the corners (524, 575) and (528, 588) are beside the lit
  lantern at about (530, 563), and the school's lit windows are inside the
  shape, some within a window of its corners (the hall's at (455, 590), the
  small tower's at (625, 580), the right building's at (1000 to 1030, 600 to
  620));
- the view's corners along the trees ((433, 611) to (600, 671), (749, 696) to
  (940, 707), (1042, 690) to (1148, 643)) and the pagoda's foot ((1296, 620)
  to (1396, 582)) follow the edge of tree crowns, not a wall;
- the railing's top edge and the second piece's corners have trees, far hills
  and (at the left) sky behind them.

## Unsure of

- Which side the stair is on. If the owner wants the way down on a thing, the
  picture needs a stair head or a hatch painted in; until then the band is all
  there is.
- The railing's height. Taken as 75 cm so that the camera is at eye height;
  taken as 90 cm, people would be about 15% smaller (zoom 0.42). The post
  (115 px wide at its foot, about 57 cm by this scale and 68 cm by the other)
  and the stage sheet both speak for the larger people.
- What `rooftop_view` should light. The school and its pagoda were taken as
  "the view"; the hills cannot be lit with them (too large a shape).
- The pagoda's lowest roof on the right, (1355 to 1396, 581), is half in the
  trees; the outline follows the dark roof that shows.

## For wave 1

U4 registers `rooftop_view` (a look) and `railing` (an act). Their name plates
are a guess (150 x 29) until then: run `check_layout.py` again when they are
registered.

## Second reading (the reviewer's pass)

Every shape was drawn again over the installed picture with a script of the
reviewer's own, enlarged, and over the evening and night pictures: the
railing, the school's roofs and the pagoda sit on their things at all three
hours. Two things were changed:

- `rooftop_view` has a third polygon, the small roof alone among the trees
  between the school and the pagoda ([1096, 552] to [1187, 574] along its
  ridge, down to y 587): a player takes it for one of the school's roofs, and
  hovering it lit nothing. It is unlit at night, like the trees round it.
- The row of four moved from (240, 520, 800, 1080) to (320, 570, 820, 1066):
  see "where people stand" above. Drawn with Panda leftmost
  (shots/stage/rooftop_day_4panda.jpg) his arm is clear of the near post.

Left as traced: the way down as a band of planks along the bottom (no stair
is painted; the record has no row saying which side it is on), the railing,
the floor, the scale and the eye line.
