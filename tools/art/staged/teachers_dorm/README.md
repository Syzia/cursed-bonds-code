# The Teachers' Dormitory's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose (O69),
`~/Desktop/JJK Game images/ui2/early/chosen/teachers_dorm_1920.png` (render
`ui2_teachers_dorm3_a_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid
4 px down). Every number is in the game's 1920 x 1080 frame; edges were read
from gridded crops of the full-size render. Nothing here is in the game. The
evening and night pictures were made from this one, so the layout holds for
them.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_teachers_dorm.json` | the exit's and the two looks' points, the side each name opens, the shapes, and the spare door | yes |
| `view_teachers_dorm.json` | where one to four people stand, the floor (and the hearth nobody stands on), the scale | yes |
| `check_teachers_dorm.json` | the eye line and the four bedroom doors' boxes, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_teachers_dorm__teachers_lounge` | a band of floor along the bottom edge: the stairs down are behind the camera and not in the picture | (960, 995) | above |
| `workbench` (planned, a look) | the sewing bench under the end window, whole: its top with the folded cloth, the spools, the pincushion, the bear on its cloth and the work lamp, both legs, and the two boxes under its left end. The hearth's hook hangs in front of it and is left out | (1105, 600), on the bear | above |
| `name_plates` (planned, a look) | three of the four blank wooden plates, one polygon each: the near one on the left wall, and the far and the near one on the right wall | (474, 397), on the near left plate | right |

`spare` holds one point, (618, 520), on the far door of the left wall: the
record gives the room one spare door, and a shape holds at most three
polygons, so the plate left untraced (the smallest, 13 by 70 px) is taken as
the spare door's. No hotspot keeps a button; no shape overlaps another; the
room has no foreground outline.

## Where people stand

The eye line is at y 530 (the two side walls' foot lines and the doors'
handles meet there): a low camera, about a metre up. `scale` is the right
edge of the near door on the right, [1553, 210, 866], 656 px taken as
200 cm. The floor at the bottom of the picture is close to the camera, so
people at the game's usual size (zoom 0.52) stand further in, feet at y 886,
in front of the hearth's near cushion; a step back is zoom 0.49 with feet at
y 873 (3% under what the door gives). Their name tags stay at the bottom
edge, about 150 px below their feet. The hearth with its four cushions, and
the strip under the bench with the blue cushion, are no-stand polygons.

One person (x 760) and two (720, 1345) hide nothing: the bear shows between
the two. With three or four the leftmost stands over the name plates' point
(a look, which waits); the workbench's point and the way out are never
hidden.

## What check_layout.py says

- Run as `python3 tools/check_layout.py tools/art/staged/teachers_dorm
  --record tools/art/staged/early/campus_for_batch3.json` it PASSES with one
  REPORT: 62% of `name_plates` is inside the toast lane. That is where the two
  right-hand plates hang; the point is on the left plate, clear of both lanes.
- Run without `--record` it reads the game's own record
  (`tools/bgs/campus.json`), whose row for this room is still the proposal
  with THREE spare doors, and prints one REFUSED line (`spare`: 3 wanted, 1
  given). The early record, which binds, says one (O69: four doors, three
  named). The line goes when the installer writes the chosen picture's facts
  into the game's record.
- `check_campus.py --layout ... --record .../campus_for_batch3.json`: PASS.

## Unsure of

- **Which door is the spare one.** All four plates are blank in the picture.
  The far left one was taken because its plate is too small to trace; if the
  story wants another, move the `spare` point to that door and swap the
  polygon.
- **The way out.** The stairs are not in the picture (the sitting asked for
  that). At the right edge a plain recess reads as the landing; it lies
  under the icon column (x over 1700, where no point may sit), so the exit is
  the floor band at the bottom, as in the Library and the boys' corridor.
- **The plates are small things to click** (27 to 45 px wide). They are
  traced tight; while names are shown their outlines are what one sees.
- The two planned name plates' sizes are guesses (150 by 29 px) until U4
  registers the hotspots.
- The scale takes the sliding door as 200 cm; at 180 cm people would be
  drawn a tenth smaller.

## For whoever installs it, and for wave 1

- U4 registers `workbench` and `name_plates` as looks, neither in front; run
  `check_layout.py` again then.
- The record's words say "cushions round a sunken hearth, a workbench under
  the end window, and four sliding bedroom doors, each with a small blank
  wooden plate": all of it is in the picture.
