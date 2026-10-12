# The Boys' Dormitory corridor's layout, staged

Laid out on 12 Oct 2026 on the corridor the owner chose on 11 Oct,
`~/Desktop/JJK Game images/ui2/early/renders/ui2_boys_dorm_a_00001_.png`, as
it is fitted in `ui2/early/chosen/boys_dorm_1920.png` (1920 x 1072, laid
4 px down). Every number is in the game's 1920 x 1080 frame, read from
gridded crops of the full-size render. Nothing here is in the game yet. Its
evening and night pictures were made from this one, so the layout holds for
them.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_boys_dorm.json` | every exit's and hotspot's point, the side its name opens, its shape, and the three spare doors | yes |
| `view_boys_dorm.json` | where one to four people stand, the floor, the scale | yes |
| `check_boys_dorm.json` | the eye line and the seven painted doors' boxes, for `tools/check_layout.py` only | never |

## The seven doors

Which room is behind which door follows the early record's first guess, and
agrees with the windows the record plans (Megumi's faces west, Yuji's and
the second-years' face east, the camera looking north).

| door | room | id |
|---|---|---|
| left, near | Megumi's Room | `go_boys_dorm__megumi_room` |
| left, middle | spare (664, 480) | – |
| left, far | spare (765, 560) | – |
| far end | My Room | `go_boys_dorm__dorm` |
| right, far | spare (1154, 520) | – |
| right, middle | Panda and Toge's Room | `go_boys_dorm__senpai_room` |
| right, near | Yuji's Room | `go_boys_dorm__yuji_room` |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_boys_dorm__megumi_room` | the near door on the left, with its frame | (352, 580) | above |
| `go_boys_dorm__yuji_room` | the near door on the right, with its frame | (1570, 580) | above |
| `go_boys_dorm__senpai_room` | the middle door on the right, with its frame | (1262, 600) | below |
| `go_boys_dorm__dorm` | the door at the far end, with its frame | (966, 600), on its right-hand edge | below |
| `go_boys_dorm__dorm_yard` | a band of floor along the bottom edge: the stairs down are behind the camera | (960, 1000) | above |
| `shoe_rack` (planned, a look) | the shoe rack, whole | (526, 800), on its end panel | left |
| `notice_board` (planned, a look) | the notice board | (1044, 484) | above |

No hotspot keeps a button; no two shapes overlap. The three spare doors
have a point each and no shape: nothing lights on them.

## Where people stand

The eye line is at y 548 (the walls' rails and foot lines meet there).
`scale` is the leaf of the near door on the right, [1522, 115, 966], taken
as 200 cm. The floor at the bottom of the picture is very close to the
camera, so, as in the Library, people stand further in: feet at about
y 861 at zoom 0.48 (a step back: y 822 at 0.42), which is what the door
gives to within 1%. Their name tags stay at the bottom edge, about 170 px
below their feet. The shoe rack's footprint is a part of the floor nobody
may stand on.

One person (x 746) hides nothing. Two (746, 1265): the second stands over
the point of Panda and Toge's door, which is then in the column. Three and
four: also My Room's door, and the notice board (a look, which waits). The
near doors, the shoe rack and the way out are never hidden. Four people are
a close row in a corridor this wide (173 px between them).

## What check_layout.py reports, and why it stands

- the two near doors reach above y 92 (2% each): their heads.
- Megumi's door is 1% inside the banner lane and Yuji's 34% inside the
  toast lane: that is where the doors are painted; both points are clear.

## What I was unsure of

- **My Room's point is on the door's right-hand edge** (x 966 of a door that
  ends at x 974), so that one person can stand in the corridor without
  hiding it; 30 px left it would be hidden by the first person.
- **Panda and Toge's Room is the middle door on the right,** as the first
  guess has it. The record calls it "the big corner bedroom"; no door in
  this picture is at a corner except the far ones, which are spare.
- **The doors came back panelled, with handles,** not sliding doors of
  boards (the sitting's own note says so). The shapes are the doors as
  painted.
- The record's words name "a window seat"; the picture has none and nothing
  is traced for one.

## For whoever installs it, and for wave 1

- U4 registers `shoe_rack` and `notice_board` as looks, neither in front;
  run `check_layout.py` again then, so that their name plates are measured.
- The reasons on the three doors that can be locked open above Megumi's and
  Yuji's and below Panda and Toge's: opened above that one it would cover
  Yuji's door (the check refused it).

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged: each sits on its door, board or rack to within a few pixels, and
nothing was changed. The row for two people was tried elsewhere: no place on
this floor clears both the notice board's point and Panda and Toge's door, so
that door's exit stays in the column when two people are here.
