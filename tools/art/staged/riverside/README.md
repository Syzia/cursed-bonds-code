# The Riverside's layout, staged

Laid out on 12 Oct 2026 on the Riverside the owner chose on 11 Oct (sitting
17a, drawn again, version A),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_riverside2_a_00001_.png`,
as fitted in `~/Desktop/JJK Game images/ui2/early/chosen/riverside_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet. The evening and night pictures were made
from this same day picture, so the layout is meant to hold for them; that
proof is the installer's (see "Corners on ground that changes with the hour").

| file | what it is | goes into the game? |
|---|---|---|
| `hot_riverside.json` | the exit's, the registered hotspot's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_riverside.json` | where one to four people stand, the ground they stand on (and the slab's front face, where nobody does), the scale | yes |
| `check_riverside.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_riverside__trailhead` | the sandy footpath on the left, from where it meets the pebbles (y 762) up between the ferns and the grass to the crest where it goes out of sight behind the big boulder (y 386): the sand only, one polygon | (125, 452), high on the path, left of everybody | above |
| `waterfall` (planned, a look) | the white fall, from its lip (y 399) to the foam at its foot (y 656), between the big boulder on its left, the lower boulder in front of its left foot, and the boulders on its right. The small dark rock that splits the lip (x 505 to 552) is inside the outline; the spray right of x 830 is not | (625, 470), on the fall, between the first and second standing places | above |
| `bank` (registered: fishing) | the flat grey rock at the lower right, whole: its level top and its mossy near face, down to its waterline | (1580, 905), where the game has it today (not moved) | left |
| `deep_pool` (planned: the swim) | the water, all of it: from the foot of the fall and the far bank's boulders (their waterlines) to the edge of the pebble bank, the right edge and the bottom edge of the picture. The flat rock lies inside it and is its own, smaller shape, so a click on the rock is the rock's | (1088, 720), on the dark deep water in the middle | above |

No hotspot keeps a button. Every thing is in the picture: nothing was placed
on a guess. No shape reaches the top bar or either lane.

**The fishing spot is called the bank and is a rock in the water.** The
game's `bank` is "cast from the bank" at (1580, 905); in this picture that
point is on the flat rock, which stands in shallow water a step from the
pebbles (sitting 17a kept the point for that reason: "the fishing spot on the
same flat rock as today"). The shape is the rock. Nobody is stood on it.

**The pool is traced as the whole water, not the dark middle only.** The deep
part has no edge of its own: it fades into the turquoise shallows across open
water, and that fade moves with the light. An outline there would hang on
nothing (the installer's relight proof) and would give the player an
invisible line in mid-water. So the shape's edges are things that stay: the
pebbles' edge, the rocks' waterlines, the fall's foot, the picture's edges.
The point and the name are on the deep water. One small rock that stands in
the water at the left (x 550 to 635, y 738 to 768) is inside the shape.

## Where people stand

On the dry pebble bank, and one on the level top of the broad slab that lies
on it at the lower left. Nobody stands in the water, on the flat rock in the
water, on the boulders or on the path. The game draws nothing in front of
people here (the Riverside is not in `fg_rooms`), so every standing place is
in front of what is near it.

The eye line is at about y 410, the waterfall's lip: the picture shows no
water above the lip, the far bank's trunks and ferns come out at believable
sizes with it (trunks about 40 cm thick, fronds about a metre), and the
pebbles about 9 cm. Nothing has a known height (no door, no post), so the
scale is reasoned, as the Forest Trail's is: with the camera 165 cm up,
`scale` is what a 200 cm post would measure standing on the pebbles at
y 990, `[1250, 287, 990]` (703 px).

By it the game's usual size is right: zoom 0.5 with the feet at y 998 and
1018 (3% and about 7% under the scale; 1008 before review 1), and 0.47 a step back with the feet at
y 950 (within 1%). On the stage sheet a person is a little taller than the
fall is high, which the eye line says is so (the fall is about eye height,
ten metres off).

- One person stands on the pebbles right of the fall (x 858).
- Two: x 858 and x 1318, both on the pebbles.
- Three: one more on the slab's top at the left (x 400, a step back).
- Four: a fourth between the two on the pebbles, a step back (x 1090), near
  the water's edge. He covers the pool's point, so the swim is in the icon
  column while four are here; the other three points stay clear.

Rows of one, two and three hide no point. The points sit in the gaps between
the rows on purpose: the path's left of everybody, the fall's between x 579
and 668, the pool's between x 1048 and 1128, the rock's right of x 1508. The
gaps are a few pixels wider than the 72 px square each, so a standing place
moved by 10 px will hide something: run the check after any change.

Panda (880 px wide) was drawn at the left and at the right of the three row
and at the right of the four row: no name's end is under him ("deep pool"
ends 6 px left of his arm). His right paw comes to within about 30 px of the
water at x 1460.

`floor.off` is the slab's dark near face (y 950 to 1045, x 0 to 668), which
is upright stone and not ground.

## Corners on ground that changes with the hour

Asked of every layout of this run, for the installer's relight proof (192 px
windows round each corner of each shape, on the evening and night pictures):

- `deep_pool` (1920, 1076): open shallow water at the picture's corner.
- `deep_pool` (1800, 1076), (1760, 1064), (1700, 1054), (1650, 1042),
  (1600, 1028): the pebbles' edge where the pebbles go under clear water;
  the edge is soft there and the stones show through.
- `deep_pool` (700, 812), (800, 842), (600, 796): on the narrow band of wet
  sand between the pebbles and the water.
- `deep_pool` (576, 662), (700, 662), (832, 654) and `waterfall` (576, 656),
  (700, 658), (830, 648): the fall's foot, white foam on water. Both shapes
  share that line, 4 to 6 px apart.
- `deep_pool` (1920, 756): the far boulder's waterline at the right edge
  (stone, but its dark reflection lies under it).
- `go_riverside__trailhead` (158, 625), (150, 600), (140, 660), (133, 700),
  (258, 625), (270, 665): the sand's edge where the ferns' shadows fall
  across the path by day; at evening the shadows will lie elsewhere.
- `go_riverside__trailhead` (150, 765), (335, 762): where the sand meets the
  pebbles, a soft edge.

Every other corner is on a rock's outline, the grass's edge against the sand,
or the pebbles' dry edge. The standing places: three on pebbles, one on the
slab's top, which is half in leaf shadow by day.

## What I was unsure of

- **The eye line and so the size of people.** Read from the lip of the fall
  and the sizes of far things, to perhaps 40 px; no straight lines run away
  from the camera. If the owner reads people as too large beside the fall,
  the zoom is the number to change (a camera at 150 cm would ask for people
  8% larger, one at 180 cm for 8% smaller; both inside the rule's 12%).
- **A person on the slab.** It is dry, level and on the bank, and the
  story has people climb out "onto the warm stones"; but it is a rock. If
  the owner wants pebbles only, the three row and the four row lose their
  left place and the row has to close up between x 700 and x 1320, which
  hides the fall's or the pool's point.
- **The whole water as the pool**, as said above. If the owner would rather
  only the deep middle lit, its lower edge is a line across open water at
  about y 795 and the relight proof may refuse it.
- **The top of the path.** It ends at the crest (y 386), where the sand is
  lost between the leaves on the left and the grass on the right; leaves
  overhang its left edge between y 400 and 470 and the outline runs under
  them.
- **Maki's and Toge's painted poses** (rows 52, 53 and 65: sitting on the
  bank at the left, crouched at the water's edge on the right) are not laid
  out here; their boxes are the pose installer's. The slab's top and the
  pebbles right of x 1320 are where they would go, and the standing place at
  x 400 would then have to be looked at again.

## A refusal that is the record's, not the layout's

`python3 tools/check_layout.py tools/art/staged/riverside` says REFUSED
twice, the same sentence for each file: "for_rev is only for a composed
picture or a new place: pictures.json does not call 'riverside'
\"composed\"". The Riverside was composed again (`pictures.riverside.kind`
in the early record is "composed"), but `place.riverside` in both records
still reads `"how": "inplace"`. Proved against a scratch copy of
`tools/art/staged/early/campus_for_batch3.json` with that one word set to
"composed" (`--record <copy>`), the same files read `PASS (0 reported)`.
Both real records were left alone: the word is the orchestrator's to change
at the install. `check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json` reads `PASS (0 reported, 18
waiting for a batch)`.

## For whoever installs it, and for wave 1

- The record has no row for which side this exit lies on; its first guess
  was (192, 576), on the same path. The point was moved up the path to
  (125, 452) so that the person on the slab does not stand on it and so that
  its name ("Mountain Path", opening above it) is clear of the widest figure.
  The name opens at y 380 to 420, below the arrival caption (y 110 to 270).
- U4 registers `waterfall` (a look) and `deep_pool` (an act), neither front.
  Run `check_layout.py` again then, so that their name plates are measured
  and no longer guessed.
- `bank`'s point did not move, so `keep_clear` and the fishing float
  (1100, 700, on the deep water) stand as they are.
- The pool's shape reaches the right edge, under the icon column; its point
  is at x 1088, clear of it.

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged (the path and the fall at 3.5 times, the flat rock and the near
edge of the water at 3), and laid over the chosen evening and night pictures
(`chosen/riverside_evening_1920.png`, `riverside_night_1920.png`): the path,
the fall, the rock and the water's edge are in the same place at every hour.
No shape and no point was changed. The pool's near edge runs along the tops
of the outermost pebbles to within about 10 px.

One number of `view_riverside.json` was changed: **the right-hand standing
place, (1318, -54) became (1318, -44)** in the rows of two, three and four,
so the feet are at y 1018, not 1008. At 1008 the right shoe of a wide stance
(Maki's, and Panda's foot) touched the line where the pebbles go under the
water; 10 px nearer the camera there is a clear row of dry pebbles beyond
the soles. It cannot move left instead: its rectangle begins 4 px right of
the pool's square.

Looked at and left: fishing is "from the flat rock at the lower right" in
the sitting's own record (`art_17a_early.json`), so `bank` on the rock is
what was asked for. Panda was drawn first of four (on the slab) and last of
three: no name is touched.

`check_layout.py ... --record <scratch copy with "how": "composed">`: PASS
(0 reported). `check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS (0 reported).
