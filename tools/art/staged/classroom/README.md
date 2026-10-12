# The Classroom's layout, staged

Traced on 12 Oct 2026 on the installed picture, `game/images/bg/classroom.png`
(render `ui2_classroom_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and
laid 4 px down: measured, the two agree pixel for pixel). Every number is in
the game's 1920 x 1080 frame; edges were read from enlarged crops of the
full-size render. The room was redone in place, so neither file carries
`for_rev`. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_classroom.json` | the exit's and the three hotspots' points, the side each name opens, and the shapes | yes |
| `view_classroom.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_classroom.json` | the eye line and the sliding door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_classroom__school_yard` | the sliding door in the right wall (from its jamb at x 1797 and the beam over it to the picture's right edge), with the floor at its foot: the aisle between the near desk and the wall down to the bottom edge, and the patch of floor seen under the near desk's right corner (one polygon) | (1692, 940), on that patch of floor, in the bottom band | left |
| `blackboard` (the registered look) | the dark board in the middle of the far wall, frame and chalk ledge, cut round the back of the teacher's chair | (1450, 500), where it is today | left |
| `notices` (planned, a look) | the notices by the door: the green pin board right of the blackboard with its two sheets, and the two plaster bays of the door wall that carry a sheet each (two polygons; the corner post between them left out) | (1615, 478), on the pin board's sheets | below |
| `front_desk` (planned, an act) | the teacher's desk: its top, what shows of its front above the pupils' desks, and its chair's back | (1195, 628), on the desk's front at the left | right |

No hotspot keeps a button; the room has no foreground outline (the plan gives
the Classroom none). The pin board LEFT of the blackboard, the clock and the
pupils' desks are not clickable.

`check_layout.py` reports two things and refuses nothing: 2% of the
blackboard and 8% of the notices lie inside the toast lane (their top edges,
where the picture has them); every point is below the lane.

## The way out

The room's only door is the sliding door in the right wall, and all of it is
right of x 1797, under the icon column's side of the picture, where no point
may sit (points stay left of x 1700). So the shape is the door itself, lit
and clicked wherever no tile lies over it, run on down the floor at its foot,
and the point is on the nearest floor a point may be: under the right corner
of the near desk, in the bottom band (y 900 or lower), which is how the check
passes it. The door's box is in `check_classroom.json`.

## Where people stand

Eye line y 480 (the door's glazing bars and the window wall's rails do not
agree to better than about 40 px; 480 is what the door and the desks give
together). The scale is the door's jamb, `[1800, 336, 900]`, 564 px taken as
200 cm; by it the near desks measure 66 to 70 cm, which is what a school desk
is.

The only open floor is in front of the first desks, along the bottom of the
picture, left of the middle. People stand there where the code stands them
today (feet at y 1022), nearer the camera than every desk, so they are drawn
over the desks behind them and that is right. By the scale a person there is
a little larger than the game's usual size: zoom 0.55, not 0.52 (the scale
gives 0.555). With four, the leftmost moved from x 240 to 250 so that the
larger picture stays on the stage.

No row for one to four people hides anything: the blackboard, the notices,
the front desk and the way out are all right of the people. Panda at the
right end of four (x 900) reaches x 1142; the front desk's name was opened to
the right of its point so that it is clear of him.

## What was changed and what was kept

- `game/layout/hot_classroom.json` held one point, `blackboard` at
  (1450, 500): kept as it is.
- The exit moved from the code's (1670, 620), a point on the wainscot, to
  (1692, 940).
- The room had no `view_classroom.json`; the slots are the code's own, with
  the zoom and the one x named above.

## Unsure of

- **The exit's point is not on the door.** It cannot be (x over 1700). If the
  owner would rather have a plain band of floor along the bottom, as the
  Library has, the under-desk patch is the part to redraw.
- **Which notices.** The plan's words are "the notices by the door". The pin
  board right of the blackboard and the sheets on the door wall were taken;
  the pin board left of the blackboard, which also carries sheets, was not.
- **The eye line,** as said above. The scale rule passes with room to spare
  from 440 to 520.
- **The front desk is small** (about 9,250 px, mostly hidden by the pupils'
  desks); its chair's back is traced with it.
- The planned name plates' sizes are guesses until U4 registers the hotspots.

## For the relight proof

Laid over the evening and the night picture: nothing has moved, every outline
sits on its thing in both. Corners and edges a relight may change:

- the exit's right edge runs down the picture's edge over the door's glass
  (dark blue at night), and its corners (1857, 285) and (1920, 238) are on the
  beam just over that glass;
- the exit's corners (1664, 882), (1741, 882) and (1664, 1080) are on shaded
  floor under and beside the near desk (no window light reaches it in any of
  the three pictures);
- the blackboard's left corners (1082, 414) and (1082, 590) are at the edge
  of the painted bars of window light that cross the left pin board and the
  board's left third: the bars are in the same place in all three pictures,
  warm by day and evening, blue at night.

## The second reading (12 Oct 2026)

Nothing was changed. Every outline was drawn again over the picture, enlarged,
and over the evening and night pictures; the relight proof, computed in memory
on these outlines, passes both hours with no outline a pixel off.
