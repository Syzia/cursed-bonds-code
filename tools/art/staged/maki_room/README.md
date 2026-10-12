# Maki's Room's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/maki_room_1920.png` (render
`ui2_maki_room2_a_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and laid 4 px
down; the fitted file and the render fitted that way are the same picture,
pixel for pixel). Every number is in the game's 1920 x 1080 frame; edges were
read from enlarged crops of the full-size render. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_maki_room.json` | the exit's and the two looks' points, the side each name opens, and the shapes | yes |
| `view_maki_room.json` | where one to four people stand, the floor (and the three parts of it nobody stands on), the scale | yes |
| `check_maki_room.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_maki_room__girls_dorm` | the door in the left wall, whole: the leaf, its two posts, the board over it and the sill, with the pull-up bar that is fixed across it | (262, 600), on the leaf beside the handle | above |
| `bed_maki` (planned, a look) | the bed: the cover down to its hem, the pillow, the two legs that show, and the folded uniform lying on it | (500, 780), on the cover's near side | above |
| `weapon_case` (planned, a look) | the leather case leaning on the far wall, with its handle; not the rack of wooden weapons above it and not the desk | (1052, 500), near its top | above, on the bare wall over the case |

No hotspot keeps a button; the room has no foreground outline. The rack, the
desk, the mat and the dumbbells are not clickable. The pull-up bar is part of
the door's shape, not a thing of its own (the dump plans none for it).

Review 1 (12 Oct 2026) added the bar's right-hand end cap to the door's
shape: it stands about 23 px past the door's far post (x 372 to 395, y 231
to 257) and had been left outside the outline. Nothing else was moved.

`check_layout.py` reports one thing and refuses nothing: 3% of the door's
shape is above y 92, where no shape takes the pointer. It is the board over
the door, which reaches the top of the picture; it is left as it is, because
the door without its head would be a worse outline.

## Where people stand

Eye line y 509: the two rails that run along the side walls at the same
height meet at (964, 509), and the foot of the right wall runs to the same
point. The scale is the door's far edge, [328, 165, 928], 763 px taken as
200 cm; by it the camera is about 110 cm up (someone sitting).

The floor at the bottom of the picture is very close to the camera, so, as in
the Library and the Principal's Office, people stand further in: feet at
y 916, drawn at zoom 0.54 (the scale gives 0.56 there), and a step back at
y 868 and zoom 0.49. That is a little larger than the game's usual 0.52,
because the open floor of this small room begins only in front of the bed's
foot: at 0.52 the feet would belong at y 887, inside the bed. Their heads
come level with the top of the door, which is right for a room this size.

- One person stands on the training mat, in front of the desk, and hides
  nothing.
- Two: the second stands at the foot of the bed (feet on the boards in front
  of its corner). The bed's point and the case's stay clear; the person's
  legs cover the bed's near corner.
- Three and four: someone a step back stands in front of the case, and its
  point is hidden (a look has no tile in the column, so it waits until they
  move). The bed and the door are never hidden.

Nobody stands in front of the door. The bed, the strip along the far wall
under the case and the desk, and the rolled mat with the dumbbells are
no-stand polygons; the flat mat is floor.

## Unsure of

- the size of people. A room this small, seen from this low, makes anyone in
  it large: 0.54 is what the door gives, and it is 4% over the game's usual
  size. If the owner finds them too big, 0.52 at the same feet is within the
  rule (7% under the scale).
- two people. The other choice was both by the window, clear of the bed
  altogether; drawn, they stood shoulder to shoulder with one foot on the
  rolled mat, so the foot of the bed was taken.
- the two planned name plates are guesses (150 by 29 px) until U4 registers
  the hotspots.
- the room has a lit picture and an evening and a night one, made from this
  day picture: the layout should hold for them, but they were not opened here.
- Maki's own painted poses for this room (at the bar, on the mat) are not
  part of this layout.
