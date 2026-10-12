# The Principal's Office's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/office_1920.png` (render
`ui2_office2_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid 4 px
down). Every number is in the game's 1920 x 1080 frame; edges were read from
enlarged crops of the full-size render. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_office.json` | the exit's and the two looks' points, the side each name opens, and the shapes | yes |
| `view_office.json` | where one to four people stand, the floor (and the desk and cushion nobody stands on), the scale | yes |
| `check_office.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

**`for_rev: 2` is in both files (review 1 put it in, as the Storehouse, the
Dojo and the Training Hall carry it), and `check_layout.py` refuses it as the
record stands.** This picture was composed again (O53, `art_12c`) and the
record's `pictures` row calls it "composed", but its `place.office` row still
says `"how": "inplace"`, which is what the check reads: it prints two REFUSED
lines (`file`: "for_rev is only for a composed picture"), and nothing else.
With that one word of the record changed to "composed" (a scratch copy) the
check passes with nothing reported, under the stricter rules a composed
layout is held to (floor and scale required). The record is not this
folder's to edit; `install_redo.py --compose` stamps `for_rev` itself.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_office__staff_yard` | the open double doors in the left wall: both leaves and the opening between them, with the balustrade at the top of the steps seen through it | (452, 600), in the opening | above |
| `dolls` (planned, a look) | the three shelf units of cloth dolls along the far wall, from the heads of the top row down to the cupboards' feet | (1330, 560) | above |
| `photograph` (planned, a look) | the framed photograph with the low desk it stands on (the frame alone is smaller than a button) | (1275, 738), on the desk top beside the frame | right |

No hotspot keeps a button; the room has no foreground outline. The two
latticed vents either side of the doors and the candle stands are not
clickable.

## Where people stand

Eye line y 595 (the door's head and sill lines meet there, and every candle
dish sits on it). The scale is the far leaf of the open doors,
[553, 443, 768], 325 px taken as 200 cm; by it the desk is about 39 cm high
and the candle stands about 108 cm. At the bottom of the picture the floor is
close to the camera, so people at the game's usual size (zoom 0.52, 0.47 a
step back) stand further in, feet at y 962 and y 927, as in the Library.
Their name tags stay at the bottom edge, about 75 px below their feet.

Everyone stands on the open floor left of the desk. One and two people hide
nothing. With three or four the leftmost stands in front of the doors and the
way out is in the icon column; the dolls and the photograph are never hidden
(the photograph's point is on the desk top, only 2 px clear of the fourth
person's picture). The desk and the cushion are a no-stand polygon.

## Unsure of

- the scale. The hall's doors are called heavy and are taken as 200 cm; if
  they are meant taller, people here are drawn too large (at 240 cm they
  would be a sixth smaller). On the stage sheet they read as right beside the
  desk and a little large against the far shelves.
- `for_rev`, above: the record's place row is the orchestrator's to settle.
- the two planned name plates are guesses (150 by 29 px) until U4 registers
  the hotspots; they are 150 px apart.
- Yaga sits at this desk in the story; a painted pose for him is not part of
  this layout, and the cushion is behind the desk, right of it in the picture.
