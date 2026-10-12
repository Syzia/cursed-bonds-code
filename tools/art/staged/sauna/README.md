# The Sauna's layout, staged

Laid out on 12 Oct 2026 on the Sauna the owner chose on 11 Oct (sitting 19a,
version B), `~/Desktop/JJK Game images/ui2/early/renders/ui2_sauna_b_00001_.png`,
as fitted in `~/Desktop/JJK Game images/ui2/early/chosen/sauna_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet. The Sauna has one picture for every hour.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_sauna.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_sauna.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_sauna.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line and the painted door's box | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_sauna__bathhouse` | the cedar door in the far wall, with its frame, down to the floor (one polygon) | (628, 450), beside the handle | above |
| `bucket` (planned, a look) | the wooden bucket with its ladle, from the ladle's tip down to where the near bench hides the bucket's foot (one polygon) | (1528, 890), on the bucket's side | left |
| `bath_sauna` (planned, "Sit it out") | the bench along the left wall: its seat, from the far end to the bottom of the picture, and the two boards of the upper step above it (two polygons; the strip of wall between them is left out) | (300, 850), on the seat | above |

No hotspot keeps a button. Every thing is in the picture: nothing was placed
on a guess. No shape reaches the top bar or either lane.

Not clickable, though they are the room's largest things: the stone
cold-plunge tub with its bamboo spout, and the stove. The dump gives the
Sauna no hotspot for either. The sitting that wrote the picture (19a) gave
the sitting-out to the bench, and that is followed here.

## Where people stand

The picture is seen from a little below standing height, from the back of
the room. Its eye line is at y 363: the bench's edges, the upper step's
boards and the two ceiling lines of the side walls meet there (read from
crops, good to about 15 px). The door leaf, taken as 200 cm (492 px, y 213
to 705), is the scale, `[700, 213, 705]`; by it the camera is about 139 cm up.

The room is small and the camera close, so people at the game's usual size
(zoom 0.52) stand well into the picture: feet at y 850, on the open boards
between the bench and the stove, just in front of the tub (within 2% of what
the scale gives). A step back is zoom 0.49 with the feet at y 815. Their name
tags stay at the bottom edge, about 190 px below their feet, as in the Library.

- One person stands in front of the tub (x 940).
- Two stand at x 860 and x 1100: clear of the door's point, the bucket and
  the bench.
- Three and four are a formality (the plan: nobody but the player is ever
  in the Sauna). They stand shoulder to shoulder on the same boards; the
  person on the left then covers the door's point, and the way out is in the
  icon column.
- Nobody stands right of x 1100: the stove's front corner is nearer the
  camera than the feet would be, and a person there would be drawn over it.

The near bench across the bottom of the picture is in front of nothing a
person reaches (every foot is above y 815 and the bench's edge is below
y 950 there), so the room has no foreground outline.

## What I was unsure of

- **What "Sit it out" should light.** The bench is what the art sitting
  named; the stove and the tub are what the action's words speak of ("The
  heat, then the cold"). If the owner would rather click the stove or the
  tub, it is one shape to retrace; the tub's and the stove's outlines were
  read off the same crops and are easy to add.
- **The near bench at the bottom** (from about (650, 1070) to (1920, 895))
  is not part of the `bath_sauna` shape: it reads as the bench the camera
  sits on, and lighting it would light a fifth of the picture.
- **The bucket's lower edge** (review, 12 Oct) was 5 to 9 px above the near
  bench's edge, which is where the bucket stops being seen; it now follows
  that edge ((1468, 963), (1500, 957), (1560, 947), (1611, 939)).
- **The eye line.** If it is 20 px higher than read, people at these slots
  are 4% small; still well inside the 12% allowed.

## For whoever installs it, and for wave 1

- U4 registers `bucket` (a look) and `bath_sauna` (an act); neither is
  front. Run `check_layout.py` again then: their name plates are a guess
  (150 x 29) until the dump measures them, and "Sit it out" is shorter than
  the id the sheet shows.
- `check_sauna.json` gives the door's box under `doors`
  (`[581, 200, 240, 514]`); a keep list for the Sauna, when one is written,
  should carry the same door.
