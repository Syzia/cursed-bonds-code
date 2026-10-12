# Gojo's Office's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/gojo_office_1920.png` (render
`ui2_gojo_office2_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid
4 px down). Every number is in the game's 1920 x 1080 frame; edges were read
from enlarged crops of the full-size render, and the finished shapes were laid
back over those crops. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_gojo_office.json` | the exit's and the two looks' points, the side each name opens, and the shapes | yes |
| `view_gojo_office.json` | where one to four people stand, the floor, the scale | yes |
| `check_gojo_office.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

**`for_rev: 2` is in both files, and `check_layout.py` refuses it as the
record stands** (the same case as the Principal's Office before its record row
was put right). This picture was composed again (`art_12c`), and the early
record's `pictures` row calls it "composed", but the `place.gojo_office` row
still says `"how": "inplace"` in `tools/bgs/campus.json` and in
`campus_for_batch3.json`, which is what the check reads: it prints two REFUSED
lines (`file`: "for_rev is only for a composed picture"), and nothing else is
refused. With that one word changed to "composed" in a scratch copy of the
record (`--record`), the check PASSES under the stricter rules a composed
layout is held to (floor and scale required). The record is not this folder's
to edit; `install_redo.py --compose` stamps `for_rev` itself.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_gojo_office__staff_yard` | the open sliding door in the left wall: the opening from the lintel down to the sill, with the yard's paving seen through it, and the timber leaf slid aside beside it | (200, 560), in the opening | above |
| `gojo_tv` (planned, a look) | the television with its foot, not the cabinet under it | (1342, 480), on the screen's right side | left |
| `sweets` (planned, a look) | the low table whole: the four open boxes of sweets on it, the table and its legs, and the three shopping bags standing against it | (1040, 640), among the boxes | left |

Everything the game registers or plans here is in the picture. No hotspot
keeps a button; the room has no foreground outline. The sofa, the windows,
the lamp and the television's cabinet are not clickable.

## Where people stand

Eye line y 420. The picture's own lines do not agree on one (the left wall's
meet at about y 365, the right wall's at about y 420, the television's edges
at about y 450); 420 is the one by which the far wall (floor at y 660, lintel
at y 290) and the door measure the same height. The scale is the near stile
of the door leaf, [345, 126, 912], 786 px taken as 200 cm; by it the
television stands about 107 cm tall on a 42 cm cabinet and the sofa's back is
about 66 cm, which is right for all three.

That door is close to the camera, so the open floor in front of the sofa is
too: people are drawn a little larger than the game's usual size, zoom 0.54
(0.50 a step back), feet at y 880 and y 850. That is 3% and 4% under what the
scale gives there. At 0.52 they pass as well (6% under); 0.54 was kept because
on the stage sheet they read right beside the door leaf, which stands about a
head taller than they do.

Everyone stands on the boards between the door and the low table. One person
stands in front of the sofa; two stand inside the door and in front of the
sofa: both rows hide nothing. With three or four, the rightmost stands in
front of the low table and the sweets wait until they move (a look has no
tile in the column); the television and the door are never hidden, so the
column gains nothing from this room. The floor polygon leaves out the sofa,
the table with its bags, and the cabinet.

## What the check reports

- `above-hud` and `in-lane` (banner) on the door: under 1% each. The lintel's
  near corner is at y 62; the door is traced as it is.
- `in-lane` on the television: 7% of it (its top right corner) is under the
  toast lane. The point is below the lane (its square starts at y 444).
- `check_campus.py --layout ... --record campus_for_batch3.json`: PASS (the
  18 WAIT lines are the area maps of batch 21b, none of them this layout's).

## Unsure of

- `for_rev`, above: the record's place row is the orchestrator's to settle.
- the eye line, for the reason given; the scale is beside the people, so a
  line 30 px higher or lower moves the answer by under 2%.
- the door is traced with its leaf. The leaf is slid in front of the wall, so
  the lit shape is wider than the way through; without it the shape is the
  opening alone, [115, 62] to [345, 914]. The first person in a row of two,
  three or four stands in front of the leaf, never in the opening.
- the two planned name plates are guesses (150 by 29 px) until U4 registers
  the hotspots; on the stage sheet they are clear of each other and of the
  door's.
- the evening picture (`gojo_office_evening`, `art_12d`) was made from this
  day picture, so the layout should hold for it; it was not laid over it here.
