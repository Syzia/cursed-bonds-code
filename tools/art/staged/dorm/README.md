# My Room's layout, staged

Laid out on 12 Oct 2026 on the installed picture, `game/images/bg/your_room.png`
(the place key is `dorm`; redone in place, revision 2, render
`ui2_your_room_b_00001_.png`). Every number is in the game's 1920 x 1080
frame, read from gridded enlargements of the installed picture and checked by
drawing the outlines back onto it and onto its evening, night and lit
pictures, where they sit on the same things. Nothing here is in the game yet.
A room redone in place carries no `for_rev` key, so neither file has one.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_dorm.json` | the exit's and the five hotspots' points, the side each name opens, and their shapes | yes |
| `view_dorm.json` | where one to four people stand, the floor, the scale | yes |
| `check_dorm.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What the room's files held, and what changed

`game/layout/hot_dorm.json` held two points and nothing else: `computer`
(440, 590) and `bed` (1330, 720). Both are replaced. The computer's point lay
on the edge of the box beside the laptop and is now on the laptop's screen.
The bed's point lay in the middle of the blanket, where the second person of
two would stand over it, and is now on the pillow. The exit had no point in
the file (the code's own was (150, 760), on the wall left of the door).
There was no `view_dorm.json`: the slots were the code's own (zoom 0.56, feet
at the bottom edge), and this file replaces them.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_dorm__boys_dorm` | my sliding door in the left wall: both paper leaves with the left jamb, the slanting head rail and the sill, from the top edge to the bottom edge of the picture | (285, 520), on the leaves | above |
| `computer` | the open laptop on the desk, with a few pixels of room round it (the laptop alone is smaller than a button) | (456, 590), on its screen | left |
| `desk` (planned, an act) | the school desk with its drawer and legs, and the swivel chair pushed under it | (436, 676), on the drawer | below |
| `wardrobe` (planned, a look) | the wardrobe's front as far as it shows: down to the laptop, the desk top and the chair's back, and its right-hand strip down to the floor | (470, 420), on its left door | above |
| `window` (planned, a look) | both windows, one polygon each: the one in the far wall (cut round the bed's head rail) and the one in the right wall, to the picture's edge | (1690, 530), on the right window | above |
| `bed` | the iron bed, whole: head rail, pillow, blanket and the three legs that show | (1196, 684), on the pillow | above |

No hotspot keeps a button; no two shapes overlap (2 or 3 px lie between the
laptop, the desk top and the wardrobe); nothing is in front of the people.
The air conditioner, the folded blanket on the wardrobe, the calendar, the
cardboard boxes and the ceiling lamp are not things to click: the game plans
nothing for them. The dark band left of the door (x 100 to 200) is left out
of the door's shape: it is not the leaves or their frame.

## Where people stand

The picture is seen from low down: the desk top is nearly edge-on, and the
lines of the left and the right wall meet between y 598 and y 664. The eye
line is taken at y 615. `scale` is the door's right-hand jamb,
[352, 190, 932], taken as 200 cm. The desk (72 cm), the wardrobe and the bed's
length each give a person 5 to 12% larger than the door does, so the door is
probably nearer 185 cm, and people are drawn 5 to 6% over what the door says
at every depth: zoom 0.54 with feet at y 905, 0.49 a step back (y 879), and
0.45 for the one furthest in (y 855).

People stand on the open boards between the chair and the bed, in front of
the far window, and one in front of the bed's foot half. Nobody stands on
the bed, and no row puts a body in front of the pillow (x 1110 to 1258).

- One (x 860): in front of the far window. Hides nothing.
- Two (800, 1440): the second in front of the bed's foot half, feet on the
  boards in front of it. Hides nothing: this is why the bed's point is on the
  pillow and the window's on the right-hand window.
- Three (730, 950 a step back, 1440): hides nothing.
- Four (715, 846 furthest in, 972 a step back, 1440): three stand close
  together on the left. Hides nothing: the bed's point sits between the
  third person's picture (it ends at x 1158) and the fourth's (it starts at
  x 1235), so Sleep stays on the picture, and nobody stands at the head rail.

## What check_layout.py reports, and why it stands

PASS, two reported.

- `above-hud`: 6% of the door's shape is above y 92. It is the top of the
  door, which runs out of the picture's top edge; its point is far below.
- `in-lane`: 11% of the window's shape is inside the toast lane. It is the
  upper part of the right-hand window; the point is below the lane.

`check_campus.py --layout`: PASS (0 reported; the 18 lines that wait for
batch 21b are the maps', none of this room).

## Corners a relight may not hold

Drawn over the evening, night and lit pictures, every outline sits on its
thing. The corners that lie on something the hour changes:

- the desk's shape along the floor: (401, 903) and (555, 903) on the boards
  under the desk, and the chair's base at (627, 852), (628, 880), (618, 898),
  (592, 898), beside the patch of window light on the floor by day;
- the bed's near leg at the floor, (1268, 894) and (1286, 894), at the edge
  of that same patch, and the bed's lower edge from (1068, 772) to
  (1572, 806), which runs along the shadow under the bed;
- the right-hand window's two corners on the picture's right edge,
  (1920, 135) and (1920, 712), and the far window's cut round the bed's head
  rail, (1038, 602) and (1071, 602), which lie on glass and frame;
- the laptop's screen, inside the computer's shape, if a relight ever lights
  it (it is not lit in the three installed pictures).

## The keep list

`tools/bgs/keep/your_room.json` still fits the installed picture, row for
row. Two remarks, nothing to mend: its door box starts at x 100 and takes in
the dark band left of the door (the traced door starts at x 200), and its
desk box ends at y 902 while the desk's feet reach y 917.

## What I was unsure of

- **The eye line.** The walls' lines meet anywhere from y 598 to y 664; 615
  is where the left wall's do and where the desk top is edge-on. At 640
  people would be about 8% larger than drawn here, still inside the rule.
- **How tall the door is.** Taken as 200 cm it makes everything else in the
  room a little large; that is why people are 5 to 6% over it.
- **The window's point is on the right-hand window**, at the stage's right
  edge, because every row of two stands in front of the far window. The name
  opens above the point, on the glass, clear of the second person.
- **The chair is traced with the desk.** If only the desk should light, the
  chair's back and base come out of the polygon.
- **The second person stands in front of the bed's foot half.** Their feet
  are on the boards and they are clear of the pillow, but their legs are
  drawn over the blanket. The only other free floor is the left group.
- **Four people** are a close group; the room is small.

## For whoever installs it, and for wave 1

- U4 registers `wardrobe` and `window` as looks and `desk` as an act, none
  of them front. Run `check_layout.py` again then: their name plates are
  guessed at 150 x 29 px until the game measures them.
- The relights are proved against these corners when the layout is staged;
  the list above is where to look first if one is refused.

## Second reading (the reviewer's pass)

Every shape was drawn again over the installed picture with a script of the
reviewer's own, enlarged, and over the evening, night and lit pictures: each
outline sits on its thing in all four. Two things were changed:

- `bed`'s point moved from (1150, 684) to (1196, 684), still on the pillow.
- The row of four: the second person from x 860 to 846 and the third from
  1000 to 972. With the old numbers the third person's picture covered the
  bed's point (Sleep dropped into the icon column) and they stood at the head
  rail beside the pillow; now no row of one to four hides anything.

Left as traced: every shape, every other point, the rows of one to three, the
floor, the scale and the eye line. The drawn people (173 cm at 619 px by the
near line) are about 5% over what the door gives as a 200 cm door and about 5%
under what the wardrobe (taken as 180 cm) and the desk (72 cm) give: between
the two, so left alone.
