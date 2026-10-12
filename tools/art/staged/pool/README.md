# The Swimming Pool's layout, staged

Laid out on 12 Oct 2026 on the pool the owner chose (O50),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_pool_b_00001_.png`, traced
on its fitted copy `~/Desktop/JJK Game images/ui2/early/chosen/pool_1920.png`.
Every number is in the game's 1920 x 1080 frame. Nothing here is in the game.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_pool.json` | the exit's and the two planned hotspots' points, the side each name opens, and their shapes | yes |
| `view_pool.json` | where one to four people stand, the deck they stand on, the scale | yes |
| `check_pool.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_pool__training_yard` | the roofed timber gate on the left, whole: its tiled roof, the two posts, the opening with the yard's earth seen through it, the two side panels with their small roofs, down to the sill | (400, 620), in the opening, on the earth of the yard | above |
| `lane_board` (planned, a look) | the blank board on the fence at the right, with its two legs | (1625, 548), on the board | above |
| `pool_swim` (planned, an act) | the water, edge to edge inside the stone coping, to where it leaves the picture on the right | (1560, 770), in the right of the water | above |

No hotspot keeps a button. Nothing is in front of the people. The changing
hut and the dojo's gable are not things to click and are not traced.

## Where people stand

On the timber deck across the bottom, never in or over the water's edge
(K16: nobody is drawn in the water). The eye line is at y 540 (the pool's
two long edges and the fence's top and foot meet there). The scale is the
gate's opening at its left post, ground to lintel (y 440 to 722, 282 px,
taken as 200 cm); the changing hut's door measures 207 cm by the same rule,
which agrees. By it a person at zoom 0.52 has their feet at y 984, and the
two a step back (0.47) at y 942; the deck starts at y 885.

Every row stands between the gate and the right of the pool, so the gate's
point, the board and the point in the water are clear with one, two, three
and four people: nothing goes to the icon column.

## What the checks say

`check_layout.py`: PASS, nothing reported. `check_campus.py --layout`: PASS.

## Unsure of

- The gate's opening is taken as 200 cm. By the pool's own width the camera
  would be higher and people a little larger; the gate and the hut's door
  agree with each other, so they were followed.
- The gate's shape runs along the edge of the white wall at its left
  (x 253), where the wall's own roof covers the gate roof's lower corner.
- The right edge of the water is traced on the inner edge of the coping; the
  wet wall under it is inside the shape.
- The pool's evening picture was relit from this one, so the layout holds
  for it; it was not looked at here. The pool has no Night.

## Second reading (12 Oct 2026)

Every shape was drawn over the 2752 px render by a second reader. One change:
the gate's outline now takes in the stone doorstep slab in front of the
opening (bottom edge through (538, 685) and (412, 722); it used to cut the
slab off at (500, 676) to (345, 712)). The water, the board, the slots, the
floor and the scale are as first traced.
