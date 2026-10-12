# Megumi's Room's layout, staged

Laid out on 12 Oct 2026 on the room the owner chose on 11 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_megumi_room_a_00001_.png`,
as it is fitted in `ui2/early/chosen/megumi_room_1920.png` (1920 x 1072,
laid 4 px down). Every number is in the game's 1920 x 1080 frame, read from
gridded crops of the full-size render and checked by drawing the outlines
back onto it. Nothing here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_megumi_room.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_megumi_room.json` | where one to four people stand, the floor, the scale | yes |
| `check_megumi_room.json` | the eye line and the painted door's box, for `tools/check_layout.py` only | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_megumi_room__boys_dorm` | the pair of sliding door leaves in the left wall, with the head rail and the sill | (310, 560), where the two leaves meet | above |
| `bed_megumi` (planned, a look) | the bed, whole: pillow, blanket, the strip of sheet at its head, the base and its two near legs | (525, 700), on the blanket's near corner | above |
| `bookshelf` (planned, a look) | the bookshelf as far as it is seen: the whole case down to the desk top, and below that its left third down to the floor; the chair, the desk and the lamp's shade in front of it are left out | (1110, 410), on the second shelf | above |

No hotspot keeps a button; no two shapes overlap. The desk, the lamp, the
chair, the shoes and the window are not things to click: the game has no
hotspot for them.

## Where people stand

The eye line is taken at y 465: the door's head and sill lines meet there,
and so do the two walls' foot lines (the window's lines meet higher, at
425). `scale` is the door's right-hand edge, [436, 260, 812], taken as
200 cm; by it the desk measures 74 cm and the bookshelf about 2 m, which is
right for both. A person at the game's usual size (zoom 0.52) has their feet
at y 899, and a step back (0.47) at y 857: open boards in the middle of the
room. The row of shoes and the footprint of the desk and chair are parts of
the floor nobody stands on.

One person (x 830) stands in front of the bed's foot end; two (830, 1390):
the second in front of the desk, by the window, as near the right wall as a
person can stand without their shoulder in it. Neither row hides a point.
Three: the one a step back stands over the bookshelf's point (a look, which
waits). Four (760, 965, 1175, 1390): the same; a close row, 205 px apart,
because the right wall leaves no room further right. The bed's point and
the door stay clear in every row, which is why the bed's point is on its
near corner.

## What check_layout.py says

PASS, nothing reported. `check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS.

## What I was unsure of

- **The door is painted as a PAIR of sliding leaves, with a pull at the
  outer edge of each,** which is how a cupboard is drawn as often as a door.
  It is the only door in the picture and stands where the record and the
  sitting's words put the room's door (the left wall, near the camera), so
  the way out is traced on both leaves. If the owner reads it as a cupboard,
  the picture shows no way out and the exit belongs in a band along the
  bottom edge.
- **The eye line** (425 to 484 by different lines); 465 is where two of the
  three pairs agree.
- **The bookshelf's lower right part**, seen between the chair's and the
  desk's legs, is not in the shape: a click there does nothing.
- **Four people** cover the bookshelf and most of the desk.

## For whoever installs it, and for wave 1

- U4 registers `bookshelf` and `bed_megumi` as looks; neither is front (the
  desk and chair stand in front of the shelf, but people stand in front of
  both). Run `check_layout.py` again then: their name plates are measured,
  not guessed (150 x 29 px today).
- The room's evening, night and lit pictures were made from this picture, so
  the layout holds for them; look at the boxes a relight added on the shelf
  (Method note 39) before installing those.
