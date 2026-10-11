# The Courtyard's layout, staged for batch 0

Laid out on 11 Oct 2026 (U0d3, sitting 3) on the gateway Courtyard the owner
chose, `~/ComfyUI-Shared/output/look2_courtyard_gateway_00001_.png`, as the
installer fits it (2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every
number is in the game's 1920 x 1080 frame. Nothing here is in the game yet:
`tools/art/staged/batch_0/art_0.json` has the command that installs it.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_courtyard.json` | every exit's and hotspot's point, the side its name opens, and its shape | yes |
| `view_courtyard.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_courtyard.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line and the vending machine's box | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_courtyard__school_yard` | the schoolhouse, whole: its wall, its roof edge, the entrance porch and the porch's stone step | (330, 700), inside the porch | above |
| `go_courtyard__dorm_yard` | the way through the gateway: its two posts, the opening with the steps seen through it, and the stone sill | (1078, 720), on the right post | above |
| `go_courtyard__training_yard` | the training hall, whole: from the roof's edge down to the veranda, with the veranda steps | (1530, 865), on the steps | above |
| `go_courtyard__gate` | the flagstones along the bottom edge (the gate is behind the camera) | (1300, 985) | above |
| `spot_vend` | the vending machine (in front of the people: it is never hidden) | (1368, 760) | left |
| `gateway` (planned, a look) | the gateway's tiled roof and the beams under it | (1100, 548), the roof's right end | left |
| `straw_posts` (planned, Practice) | the two straw posts, one polygon each | (1695, 925), on the nearer post | left |

The gateway carries two things, so it is two shapes that do not overlap: the
roof is the look, the way through is the exit. No hotspot keeps a button.
The hall's roof runs through the toast lane and the schoolhouse reaches above
the top bar; `check_layout.py` reports both and refuses neither.

## Where people stand

The picture is seen from low down: its eye line is at y 748 (the schoolhouse's
and the hall's roof and ground lines meet there), and the vending machine, a
thing of known height (183 cm, 158 px tall at y 838), gives the scale. By
that measure a person on the near flagstones is smaller than the game's usual
size, so the Courtyard draws people at zoom 0.455 (0.415 a step back) instead
of 0.52. Looked at on the stage sheet and in the game: they sit right beside
the porch and the machine.

One and two people stand left of the gateway and hide nothing. Three hide
the schoolhouse's point (that exit is then in the icon column). Four hide
the schoolhouse's, the gateway's and the way through it: 2 of 5 things in the
column, 4 tiles of 8 (the gateway is a look, and a look has no tile there).
The vending machine is clear of every row.

## The old layout on the new picture

`install_redo.py --compose courtyard <render> --dry` drew it first. Only the
way back to the gate still sat on its thing (the flagstones) and was kept at
(1300, 985); the three buildings are new, so their exits, the machine and the
two planned hotspots were placed afresh.

## For whoever installs it, and for wave 1

- U4 registers `gateway` as a look and `straw_posts` as Practice; neither is
  front. Until then their shapes are in the file and the game does not draw
  them. When they are registered, run `check_layout.py` again: their name
  plates are then measured and no longer guessed.
- The straw posts stand at the right edge, and the icon column is drawn over
  the right 25 px of the farther post. The point is on the nearer post.
- The installer measures the light row. On this picture the sampler answers
  a tint of `#f5ffff` (a little of the sky's blue): look at the people on
  the installed picture before keeping it.
- `tools/bgs/keep/courtyard.json` holds a `scale` of its own for pose
  prompts, [1365, 666, 830]; this layout's is [1362, 665, 838], traced on a
  crop of the full-size render. They agree within 6%.
- Words that describe the picture (hand-off, never edited here): the place's
  description says nothing of buildings and still fits. A look line for the
  gateway and a line for Practice at the posts are U4's and U5's.
