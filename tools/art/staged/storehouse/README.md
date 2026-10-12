# The Storehouse's layout, staged

Traced on 12 Oct 2026 on the Storehouse the owner chose (version B with the
view through its door put right),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_storehouse2b_doorview_00001_.png`,
as fitted to the game's frame in `chosen/storehouse_1920.png` (2752 x 1536
becomes 1920 x 1072, laid 4 px down). Every number is in the 1920 x 1080
frame; edges were read on enlarged crops of the full-size render. Nothing
here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_storehouse.json` | the exit's and every hotspot's point, the side its name opens, and its shape | yes |
| `view_storehouse.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_storehouse.json` | the picture's eye line and the box of the painted door, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_storehouse__training_yard` | the open double door in the front wall: the opening with both leaves and the sill, the yard and its striking posts seen through it | (960, 640), in the opening | above |
| `racks` and `armory` (one point, one shape: the room never offers both) | the weapon racks, two polygons: the stand of six swords, and the stand of spears beside it down to where the chest hides it | (1222, 690), on the sword stand | above |
| `big_chest` (planned, a look) | the iron-bound chest, with its far end that shows under the workbench | (1385, 750), on its hasp | below |

No hotspot keeps a button and nothing is in front of the people. The racks'
point moves from the code's (1600, 600), which is bare wall in this picture.

## Where people stand

The eye line is at y 626: the shelf boards of the left wall slope down above
it and up below it, and the yard's far edge seen through the door lies on
it. The scale is the door: its opening is 283 px tall (y 482 to the sill at
y 765) and is taken as about 240 cm, which is what the same door measures
from outside in the Training Yard's picture, so `scale` is the door post
from the sill up to 200 cm, [813, 529, 765]. By it the workbench is about
80 cm and the chest about 60 cm. People are the game's usual size (zoom
0.52, and 0.47 a step back), feet on the near boards.

One person stands left of the door, in front of the loft stair; two stand
at the left, in front of the shelves, and hide nothing. With three, one a
step back stands in the doorway; with four, the nearest on the right stands
in it: the way out is then in the icon column. The racks and the chest are
clear of every row.

## What the checks said

`check_layout.py`: nothing reported, and PASS when the record calls the room
composed. **With the record as it stands in the tree it prints two REFUSED
lines, one for each file: "for_rev is only for a composed picture or a new
place".** The room was composed again on the owner's word (O45) and the
record's `pictures` row says `kind: composed`, but its `place.storehouse`
row still says `how: inplace`, and that row is the one the check reads. The
files carry `for_rev: 2` as a composed picture's must; the place row is the
record's to put right (not mine to edit), or the refusal ends by itself when
the installer writes the manifest row. The PASS was read with a scratch copy
of `campus_for_batch3.json` in which that one word is changed.
`check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS.

## What I was unsure of

- How tall the door is. Taken as 240 cm; at 200 cm people would be drawn a
  sixth smaller. The bench, the chest and the yard's picture agree with 240.
- Whether the tool board and the workbench belong to "Look through the
  racks". They are left out: the shape is the two weapon stands.
- The person at the far left stands in front of the shelves' lower boxes;
  the floor there is narrow.

## For whoever installs it, and for wave 1

- Wave 1 registers `big_chest` as a look, not front. Run `check_layout.py`
  again then, so that its name plate is measured.
- The code's `keep_clear` point for this room is the racks' old point
  (1600, 600); it follows the sidecar once this file is installed.
- A keep list for this picture (`tools/bgs/keep/storehouse.json`) should
  name the door's box, [813, 482, 295, 283], as `check_storehouse.json` does.
