# The Library's layout, staged for batch 0

Laid out on 11 Oct 2026 (U0d3, sitting 3) on the bright Library the owner
chose, `~/ComfyUI-Shared/output/look2_library_bright_00001_.png`, as the
installer fits it (2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every
number is in the game's 1920 x 1080 frame. Nothing here is in the game yet:
`tools/art/staged/batch_0/art_0.json` has the command that installs it.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_library.json` | every exit's and hotspot's point, the side its name opens, and its shape | yes |
| `view_library.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_library.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `stacks` (Study) | the shelves: the wall of shelves on the left with its rolling ladder, and the two bookcases beyond it (two polygons, the strip of wall between them left out) | (300, 520), where it is today | right |
| `reading_table` (planned, a look) | the two reading tables, each with its chairs and its lamps: the middle one, and the one on the right as far as the cabinet's edge (two polygons; review 1 added the second, so that the twin lights too) | (1000, 690), on the middle one | left |
| `locked_shelf` (a look) | the glass-fronted cabinet on the right, whole | (1610, 527), on its padlock | left |
| `go_library__school_yard` | a band of floor along the bottom edge, from the ladder's foot to the right wall: the door is behind the camera | (1480, 985) | above |

No hotspot keeps a button. The room has no foreground outline (the plan
gives the Library none: its tables are filled by painted poses). The stacks
and the cabinet reach above the top bar and into the two lanes;
`check_layout.py` reports that and refuses nothing.

## Where people stand

The picture is seen from about a seated person's eye height: its eye line is
at y 554. The reading table (72 cm, 174 px tall at its front legs) gives the
scale; by it the cabinet's near edge measures about 213 cm, and `scale` is
that edge up to 200 cm, [1553, 213, 848]. At the bottom of the picture the
floor is very close to the camera, so people at the game's usual size (zoom
0.52) stand further in: their feet at about y 900, level with the cabinet's
foot, not at y 1022. Both were drawn and looked at; at y 1022 they read as
small people in a big room.

One person stands in front of the bookcases; two stand either side of the
reading table and hide nothing. With three or four, someone a step back
stands in front of the table and its point is hidden (a look has no tile in
the column, so it waits until they move). The way out is below every row and
is never hidden.

## The old layout on the new picture

`install_redo.py --compose library <render> --dry` drew it first. The stacks'
point still sat on the shelves and is kept. The cabinet's point still sat on
the cabinet and was moved 50 px onto its padlock. The way out sat on the
cabinet's foot and was moved to the bottom of the picture, as the campus
record asks (the room shows no door).

## For whoever installs it, and for wave 1

- U4 registers `reading_table` as a look, not front. Until then its shape
  is in the file and the game does not draw it. Run `check_layout.py` again
  then, so that its name plate is measured.
- `tools/bgs/keep/library.json` holds a `scale` for pose prompts,
  [1140, 205, 695]: the wall post up to the beam over the windows, taken as
  200 cm. By the table and the chairs that beam is about 320 cm up, so a
  pose prompt built from it would ask for people about half as large again
  as they should be. Put it right before the Library's poses are written;
  this layout's `scale` is the one to copy.
- The Library's hour pictures (evening, night, and its lamps-on night) were
  chosen early and were made from this same day picture, so the layout
  holds for them.
- Words that describe the picture (hand-off, never edited here): "Shelves
  to the ceiling and a smell of dust and ink" still fits the chosen room.
