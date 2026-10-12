# The Cafeteria's layout, staged

Traced on 12 Oct 2026 on the installed picture, `game/images/bg/cafeteria.png`
(render `ui2_cafeteria_a_00001_.png`, 2752 x 1536; the room was redone in
place, revision 3). Every number is in the game's 1920 x 1080 frame; edges
were read from gridded crops of the full-size render. Nothing here is in the
game. Neither file carries `for_rev` (a room redone in place).

| file | what it is | goes into the game? |
|---|---|---|
| `hot_cafeteria.json` | the way out's, the counter's and the water cooler's points, the side each name opens, and the shapes | yes |
| `view_cafeteria.json` | where one to four people stand, the floor, the scale | yes |
| `check_cafeteria.json` | the eye line (y 550) and an empty door list, for the tools only | never |

## What the room's files held, and what was kept

`game/layout/hot_cafeteria.json` held one point, `counter` at (1500, 600): it
is kept as it is. The room had no `view_` file: the people stood on the
code's own slots (zoom 0.52, feet at y 1022, a step-back person at x 760 or
530, which is not behind the near table). `tools/fg/cafeteria.json` and
`tools/bgs/keep/cafeteria.json` were read and not changed.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_cafeteria__school_yard` | a band of open floor along the bottom edge, from the foot of the window wall to the tables' legs: **the room shows no door** (the way out is behind the camera) | (796, 990) (was (230, 520), on the first window's glass) | above |
| `counter` (registered, eating) | the serving counter, whole: its steel top, the food warmer and the stacked trays on it, and its wooden front down to the back edge of the far tables, stepped round the three chair backs that stand in front of it; at the left end, the front down to its foot | (1500, 600), on the trays, where it is today | left (the game's own side today) |
| `water_cooler` (planned, a look) | the water cooler: the bottle and the body, down to its foot | (790, 600), on its taps | right, onto the bare wall |

No hotspot keeps a button; no shape overlaps another. The windows, the
plants, the lamps and the tables are not clickable.

## The near table is the room's foreground

The outline in `tools/fg/cafeteria.json` (the same six points for the day,
the evening and the night) was laid over all three installed pictures
(`shots/layout/view_cafeteria__staged.png`): it fits the near table in each.
Its slanted left edge follows the lower edge of the table's side rail, about
20 px left of the table top's own edge. Nothing to mend.

## Where people stand

The eye line is at y 550: the window wall's sill, its middle bar and its head
bar meet at about (1060, 550). The room has no door or post of known height
beside the open floor, so the scale is taken from the furniture: the counter's
left front corner (foot at y 812, top at y 632) as 100 cm, carried up to 200
cm, `[921, 452, 812]`. By it the tables come to 72 cm, which is what a table
is. (The water cooler comes to over two metres by the same measure: it is
painted large, and was not used.)

By that scale a person at the game's usual size would stand with the feet on
the picture's bottom edge. People are drawn a little smaller, zoom 0.48, with
their feet at y 1010, so that the floor shows under their shoes and the name
tags lie below them. They stand on the open boards on the left:

- one person at x 570, in front of the second window;
- two: the second at x 1020, in front of the counter's left end, clear of the
  table legs. Neither hides the cooler, the counter or the way out (the way
  out's point is between them, 3 px and 6 px clear);
- three: the third stands a step back at x 1350, **behind the near table**
  (zoom 0.52, feet at y 1055, hidden); the table is drawn over the legs from
  the thigh down. The person covers the chair that stands behind the table;
- four: all four on the boards (x 470, 660, 850, 1040), since the install
  (see "At the install", below). The cooler's point and the way out are
  then hidden (the way out is in the icon column; the look waits). The
  counter is never hidden.

The floor is two polygons: the open boards, from the wall's foot to the
counter's foot and the tables' legs, and the strip of the aisle behind the
near table's left end (hidden by the table; it is there so that the check
knows the step-back place is floor).

`check_layout.py`: PASS, nothing reported. `check_campus.py --layout`: PASS.

## Unsure of

- **The way out has no door in this picture.** The record says the dining
  hall's glass doors are behind the camera, so the exit is the band of floor
  at the bottom. The panes of the window wall have handles like sliding
  doors, but they stand on a sill over a wainscot: they are windows, and the
  check refuses an exit on a window.
- **Where the person behind the table really stands.** By the picture's own
  legs the middle table's far edge meets the floor at about y 1050 and the
  aisle between the middle and the near table is below the bottom edge, so
  the feet (hidden) are not on floor one can see; the person reads as
  standing between the two tables, about a sixth smaller than that depth
  would make them.
- **The person behind the table is not smaller than the others.** A step
  back in this room means "behind the near table", and the only floor behind
  it without a chair is level with the near row. The game draws that person
  a little softer and 2% darker. If it reads wrong, the other choice is to
  stand all four on the boards (x 480, 680, 880, 1060, none a step back).
- **Panda at the left of four** (x 510): his arm reaches about 50 px over
  the window wall's wainscot. He hides the end of no name.
- **The scale** rests on the counter being 100 cm; a 90 cm counter would ask
  for people about 10% larger (the check allows 12%).
- The way out's point clears the two-person row by a few pixels only.
- The cooler's name plate is a guess (150 by 29 px) until U4 registers it.
- **For the relight proof** (not run here; laid over the evening and night
  pictures by eye): the band's top edge (y 965, x 466 to 1072) crosses open
  floor in the window's patch of light (sun by day, the window's lattice in
  the evening at x 830 to 1080, moonlight at night at x 740 to 1000); its
  corners (1072, 965), (1072, 1052) and (1168, 1052) are on floor beside
  table legs. The counter's foot (919, 812) to (1026, 812) meets the same
  patch in the evening. The cooler's right side lies against its own cast
  shadow on the wall, which the evening lengthens. The trays' and the
  warmer's top edges lie against wall the paper lamps light in the evening.
- `tools/bgs/keep/cafeteria.json`: every row still fits the picture. Its
  `scale` [1015, 318, 800] (for pose prompts) is about a third larger than
  this layout's; its `doors` list is empty, as the picture is.

## For wave 1

- U4 registers `water_cooler` as a look, not in front; run `check_layout.py`
  again then, so that its name plate is measured.

## The second reading (12 Oct 2026)

- The step-back place moved from x 1215 to x 1350 (three people) and x 1262
  (four). At x 1215 the legs showed left of the table's slanted end and were
  drawn OVER the near table's far-left leg: the outline in
  `tools/fg/cafeteria.json` follows the table top's end and leaves that leg
  (x 1170 to 1196, y 905 to 1080) outside. The outline was not changed. At
  x 1262 a little of the left shin still shows there, under the name tag.
  The hidden strip of floor was widened to x 1450 to hold the new place.
- **The way out's band is refused by the relight proof as the keep list
  stands.** The proof of `tools/install_redo.py` was computed in memory
  (`redo_measure.judge`, relight) on these outlines against the installed
  evening and night pictures: every outline holds except the way out. Its
  point (796, 990) and the samples of its top edge from about x 740 to 960
  lie on open boards under the window's light (a lattice of sun in the
  evening, moonlight at night), with nothing that stays inside their
  windows. No point between x 740 and 960 holds at any height from y 910
  down, and that is the only stretch clear of the rows for one and two
  people. A `ground` row in `tools/bgs/keep/cafeteria.json` (not this
  folder's to write) makes both hours pass with these same outlines:
  `{"name": "the open boards the windows light", "poly": [[500, 960], [640, 872], [740, 860], [775, 790], [900, 775], [905, 825], [1010, 828], [1012, 965], [1060, 965], [1060, 1060], [1095, 1075], [400, 1075], [400, 1045]]}`
- The keep list's `empty` row "the floor" is loose on this picture: its
  lower part runs from x 170 (inside the window wall's wainscot) to x 1480
  (over the near table's legs and top). Every other row fits.


## At the install (12 Oct 2026)

- **The row of four is all on the boards: x 470, 660, 850, 1040** (it was
  510, 730, 950 and a fourth behind the near table at x 1262). The Cafeteria
  at Noon is the one place and hour where five people stand together, and
  the game lists the fifth in a small "+1" chip whose corner is at x 1400
  on the bottom line (`RAIL_MORE_POS`). The fourth person's rectangle
  reached x 1460 behind the table, so the chip stood on it, and
  `p2_hud`'s line "the +N chip's names stand on no sprite" failed. The row
  now ends at x 1222. (The layout check does not know that chip: a rule for
  it is owed, for the place where five can stand.)
- **The keep list names the boards the windows light as ground**
  (`tools/bgs/keep/cafeteria.json`, one polygon, the second reader's): with
  it the installed evening and night pass against these outlines. Measured
  with a damage sweep on both pictures (48 damaged pictures): the near
  table, the counter, the cooler and the ground's surroundings slid or
  painted out are all still refused; the one refusal lost is the way out's
  own band of floor painted out, at night.
