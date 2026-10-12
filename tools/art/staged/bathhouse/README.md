# The Onsen's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/bathhouse_1920.png` (render
`ui2_bathhouse_a_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid
4 px down). Every number is in the game's 1920 x 1080 frame; edges were read
from enlarged crops of the full-size render, and the finished shapes were laid
back over those crops. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_bathhouse.json` | the two exits', the look's and the action's points, the side each name opens, and the shapes | yes |
| `view_bathhouse.json` | where one to four people stand, the floor, the scale | yes |
| `check_bathhouse.json` | the eye line and the two painted doors' boxes, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_bathhouse__trailhead` | the entrance in the right wall: the opening under the dark-blue door curtain, with the stone basin and the path seen through it, and the latticed leaf slid aside beside it | (1545, 600), in the opening | above |
| `go_bathhouse__sauna` | the shut cedar door in the left wall, as much of it as shows beside and above the fridge | (352, 440), on the door | above |
| `milk_fridge` (planned, a look) | the glass-fronted fridge, down to its feet, less the corner the near bench covers; the fan standing on it is left out | (130, 700), on the bottles | right |
| `bath_soak` (planned, Soak) | the hot spring seen through the open screens: the water and its ring of stones, from the stones' tops down to the grass at their foot | (920, 635), on the water | above |

Everything the game registers or plans here is in the picture, and each way
out is on its own door: the entrance has the path behind it, the cedar door
is the only other door of the hall. The early record's first guesses
(trailhead at (1480, 520), sauna at (330, 470)) lie on the same two doors. No hotspot keeps a
button; the hall has no foreground outline. The fan, the benches, the paper
screens and the basin are not clickable.

## Where people stand

Eye line y 495 (the left wall's lintel and floor lines meet at y 499, the
right wall's at y 485). The scale is the entrance's jamb where the leaf
stops, [1432, 265, 792], 527 px taken as 200 cm; the cedar door measures
211 cm by it and the far opening onto the spring 200 cm.

People are at the game's usual size, zoom 0.52 (0.48 a step back), and stand
further in than the bottom edge, feet at y 883 and y 853: by the scale that
is exactly a 173 cm person at both depths. Their name tags stay at the bottom
edge.

One person stands in front of the left paper screen. Two stand either side
of the view of the spring and hide nothing. Three hide nothing either: one
on the left (x 640), two on the right (x 1145 a step back, x 1310), the view
of the spring open between them. The game schedules three people here at once
(Maki, Nobara and Utahime on weekend evenings), so this row is a real one, and
Soak is the hall's reason. Four stand two and two (x 470 and 660, x 1145 and
1310): the person at x 470 is then over the cedar door's point by the game's
rule (its box for a person is 395 px wide, wider than the body), so the way to
the Sauna is in the icon column (1 thing of 3 that can go there); the spring,
the fridge and the entrance stay clear.

(Review, 12 Oct: the first tracing stood the middle person of three, and two
of four, in front of the spring: rows 590/900/1210 and 590/820/1055/1290.
Both rows were moved; rows of one and two are as traced. The price: the two on
the right stand shoulder to shoulder, 165 px apart, and the nearer one stands
in front of the entrance's latticed leaf, not of the opening.)

The floor polygon leaves out the two near benches, the
fridge and the bench along the left wall.

## What the check reports

- `in-lane` on the entrance: 32% of it (the curtain and the top of the
  opening) is under the toast lane. The entrance is where the picture has
  it; its point is below the lane (its square starts at y 564).
- `check_campus.py --layout ... --record campus_for_batch3.json`: PASS (the
  18 WAIT lines are the area maps of batch 21b, none of them this layout's).

## Unsure of

- the rows of three and four, as said above: closer together than the rows
  of one and two, so that the spring stays open. Look at three in the game.
- how much of the view is Soak. Only the spring itself lights (336 by 158
  px); the fence and the slope above it do not. If the owner would rather
  click anywhere in the opening, the shape is the opening, [752, 340] to
  [1088, 702].
- the entrance is traced with its latticed leaf, as the office's doors are;
  without it the shape is the opening alone, from x 1432.
- the fridge's name opens to the right, over the fridge's own door; to the
  left it would leave the screen.
- the two planned name plates are guesses (150 by 29 px) until U4 registers
  the hotspots.
- nobody is ever drawn in the water (K16): the people on the stage sheet are
  the game's dressed sprites on the boards.
- the evening and night pictures (`art_19b`) were made from this day
  picture, so the layout should hold for them; it was not laid over them here.
