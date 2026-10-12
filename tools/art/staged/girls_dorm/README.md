# The Girls' Dormitory corridor's layout, staged

Laid out on 12 Oct 2026 on the corridor the owner chose,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_girls_dorm5x_b_00001_.png`,
as it is fitted in `ui2/early/chosen/girls_dorm_1920.png` (1920 x 1080).
Every number is in the game's 1920 x 1080 frame, read from gridded crops of
the fitted picture enlarged two to six times. Nothing here is in the game
yet. The chosen evening (`ui2_girls_dorm_evening_a_00001_.png`) and night
(`ui2_girls_dorm_night_off_a_00001_.png`) were laid under the same outlines
and read: every door, the rack, the plant, the window and the three lights
sit where the day picture has them.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_girls_dorm.json` | every exit's and hotspot's point, the side its name opens, its shape, and the four spare doors | yes |
| `view_girls_dorm.json` | where one to four people stand, the floor, the scale | yes |
| `check_girls_dorm.json` | the eye line and the six painted doors' boxes, for `tools/check_layout.py` only | never |
| (moved at the merge, 12 Oct 2026) | the keep list written here for the new corridor is now `tools/bgs/keep/girls_dorm.json`, in place of the one that described the OLD corridor (eight doors, a card reader). It was staged here as `keep_girls_dorm.json` | it is the keep list |

## The six doors

The picture is a corridor seen straight down its middle: three doors on
each side, each facing the one opposite, a window at the far end. Which
room is behind which door is the sitting's record
(`tools/art/staged/early/art_4u_early.json`).

| door | room | id |
|---|---|---|
| left, near | Nobara's Room | `go_girls_dorm__nobara_room` |
| left, middle | spare (664, 480) | – |
| left, far | spare (765, 560) | – |
| right, far | spare (1155, 560) | – |
| right, middle | spare (1256, 480) | – |
| right, near | Maki's Room | `go_girls_dorm__maki_room` |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_girls_dorm__nobara_room` | the near door on the left with its frame: the wall post on its left, the leaf, the jamb on its right, from the sloping head down to the sill track | (356, 580), on the leaf's middle rail | above |
| `go_girls_dorm__maki_room` | the near door on the right with its frame, the mirror of the other | (1564, 580) | above |
| `go_girls_dorm__dorm_yard` | a band of floor along the bottom edge, between the two near doors' sills: the picture shows NO door to the garden; the way out is behind the camera, as in the Boys' Dormitory | (960, 1000) | above |
| `plant` (planned, a look) | the potted plant beside the far window: its leaves and its pot, one polygon of twenty points | (1036, 566), on its left-hand leaves | left (over the window's glass) |

No hotspot keeps a button; no two shapes overlap. The four spare doors have
a point each and no shape: nothing lights on them, and nothing makes a
bedroom door a thing to look through (K16). The shoe rack is not a hotspot
of this corridor (the dump plans none): it is a part of the floor nobody
stands on, and a `keep` row.

## Where people stand

The eye line is at y 552 (the walls' foot lines and the door heads meet at
about y 535 to 561). `scale` is the inner edge of the right-hand jamb of
Nobara's door, [407, 118, 968], head to sill, taken as 200 cm. As in the
Boys' Dormitory the floor at the bottom is very close to the camera, so
people stand further in: feet at y 861 at zoom 0.48, a step back y 822 at
0.42; the door gives those sizes to within 1%.

- One (x 746) and two (746, 1265) hide nothing.
- The plant is the corridor's only thing to do, and the check refuses a row
  of three or four that hides it. So three stand as two on the left and one
  on the right (710, 838 a step back, 1265), and four as two pairs either
  side of the plant (710 and 838; 1233 and 1330), the first of three and
  the two near ones of the four a little nearer the camera (feet y 900, zoom 0.50: 6% under the
  door's measure, inside the 12% allowed) because the corridor is wider
  there. The plant's point stays clear in every row; its leaves are partly
  behind a wide person (Panda) in the second place, its point is not.
- Nobody stands behind anything: the corridor is not in `fg_rooms`. The
  first person of four stands in front of the shoe rack's far end (his feet
  are nearer the camera than its front edge at that x).
- Panda was drawn in the second place of four and in the first of three:
  the two rooms' names (x 290 to 430 and 1505 to 1625) are clear of him and
  of the arrival caption (they open at y 515, below it).

## What check_layout.py says

`python3 tools/check_layout.py hot_girls_dorm.json view_girls_dorm.json
--record <scratch copy>`: PASS (4 reported). The scratch copy is the early
record with `place.girls_dorm`'s `"how"` set to `"composed"` (it still says
`"inplace"`; that word is the orchestrator's to change at the install, and
both real records were left alone). Against the game's own record the same
run prints the two expected `for_rev is only for a composed picture` lines
and nothing else new.

(While the keep list was staged in this folder the check was run on the two
files by name: on the folder it refused `keep_girls_dorm.json` as "not a
layout file name". The keep list has moved to `tools/bgs/keep/`, and the
check runs on the folder again.)

The four REPORT lines, which stand:
- each near door is 3% above y 92: its head, under the top bar.
- Maki's door is 34% inside the toast lane and Nobara's 1% inside the
  banner lane: that is where the doors are painted; both points are clear.

`check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS (0 reported, 18
waiting for a batch).

## The keep list (staged)

`doors`: the six doors' boxes. `windows`: the far window's two panes, just
inside the frame (the view changes with the hour). `empty`: the floor under
the standing places, clear of the rack and of the far end. `keep`: the shoe
rack, the plant, the three ceiling lights, one row each. `scale`: the same
as the view file's.

## What I was unsure of

- **The eye line** is read to about 15 px (535 to 561 by different lines);
  552 is used. The sizes hold within the rule for any value in that range.
- **Four people** stand as two close pairs (138 px and 107 px between the
  people of a pair, the far one a step back). It is the only row that
  leaves the plant's point clear in a corridor this narrow. If the owner
  would rather have an even row of four, the plant must then wait behind
  someone, and the check's rule would have to allow it.
- **The evening's sun** lies as a bright patch on the floor inside the
  keep list's `empty` polygon, and the plant throws a shadow on the right
  wall and floor (outside it). The proof against the evening and the night
  is the orchestrator's: if the floor row refuses the evening, the patch is
  light, not a thing set down.
- **Corners on open floor.** Only the way out's band has any: (430, 970)
  and (1490, 970), each 7 px inside the foot of its near door's sill, and
  (308, 1066), (1612, 1066), (308, 1080), (1612, 1080) at the bottom edge.
  The floor is glossy boards whose reflections change with the hour.
- The plant's name opens to the left, over the window's glass; opened to
  the right it would lie under the second person.
- The record's line for the end window says it shows "the dormitory garden
  and the common room's roof"; the picture shows trees and sky. Nothing is
  traced on the window.

## For whoever installs it, and for wave 1

- U4 registers `plant` as a look, not in front; run `check_layout.py`
  again then, so that its name plate is measured.
- (Done at the merge: the keep list is `tools/bgs/keep/girls_dorm.json`,
  in time for the evening and the night to be proved against it.)
- The sheets: `shots/layout/hot_girls_dorm__staged.png`,
  `shots/layout/view_girls_dorm__staged.png`, `shots/stage/girls_dorm.jpg`.

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged (the two doors at 1.8 times, the plant at 6): each follows its door
frame, its leaves and its pot to within a few pixels, and no shape was
changed. The outlines and the keep list were also laid over the chosen
evening and night pictures (`chosen/girls_dorm_evening_1920.png`,
`girls_dorm_night_1920.png`): every door, the rack, the plant, the window and
the three lights are where the day picture has them.

Three numbers of `view_girls_dorm.json` and one row of the keep list were
changed:

- **The first of three: (700, -200, 0.48) became (710, -160, 0.50).** At
  x 700 with the feet at y 861 a person's left boot stood inside the far end
  of the shoe rack (the rack's footprint reaches x 664 at that depth, the
  boot began at about x 620): drawn in front of it, he read as standing in
  the rack. With the feet at y 900 the rack ends at x 623 and the boot begins
  at about x 627.
- **The first of four: x 700 became 710,** for the same boot.
- **The last of four: x 1340 became 1330.** The right wall's foot is at
  x 1407 where her feet are (y 900); at 1340 the widest stance (Maki's)
  reached x 1437, onto the skirting of Maki's door.
- **The keep list's `empty` floor polygon** now starts at y 808, not 780:
  the evening picture's patch of sun from the end window ends at about
  y 790, and its edge lay inside the polygon. Every standing place (feet
  y 822 to 900) is still inside it.

Looked for and left as they are: the pairs of the rows of three and four
cannot be opened out. The game's rectangle for a person is the whole canvas
(760 px times the zoom), the plant's square is x 1000 to 1072, and the row
may not hide the corridor's only hotspot: the person a step back on the left
can stand no further right than x 838, the one on the right no further left
than x 1233, and the wall's foot is 70 px beyond his feet. The plant's name
opens to the left and is guessed at 146 px wide until wave 1 registers it
(the measured plate of a five-letter name is about 50 px): at that width its
left end would be under the person at x 838, at the real width it is clear.
With Panda first of four the rack and most of the person behind him are
hidden; no name is.

`check_layout.py hot_girls_dorm.json view_girls_dorm.json --record <scratch
copy with "how": "composed">`: PASS (4 reported, the four lines above).
`check_campus.py --layout ... --record tools/art/staged/early/campus_for_batch3.json`:
PASS (0 reported).
