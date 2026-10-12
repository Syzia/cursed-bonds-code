# The Main Gate's layout, staged

Laid out on 12 Oct 2026 on the Main Gate the owner chose (the third go's
version B), `~/Desktop/JJK Game images/ui2/early/chosen/gate_1920.png`, the
fitted copy of `ui2_gate3_b_00001_.png`. Every number is in the game's
1920 x 1080 frame. Nothing here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_gate.json` | the exit's and the planned look's point, the side its name opens, and its shape | yes |
| `view_gate.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_gate.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_gate__courtyard` | two polygons: the gatehouse, whole (roof, railed upper floor, the lower storey with its open doors, the stone platform and its steps), and the plank bridge that leads to it | (962, 690), in the open doorway, on the flagstones seen through it | above |
| `gate_pond` (planned, a look) | the water, three polygons: left of the bridge; right of the bridge as far as the near stone lantern; and the strip that shows again right of that lantern | (330, 905), on the left water | left |

The stepping stones and the raked gravel between the bridge and the steps are
left out (they are ground people walk on, and tracing them would join the two
polygons into one large shape over where people stand). The rocks round the
water, the lanterns, the maples and the pines are not traced: nothing is
planned for them. No hotspot keeps a button and the place has no foreground
outline. The gatehouse's roof ridge runs through the banner lane and its
right eave tip touches the toast lane; `check_layout.py` reports both and
refuses neither.

## Where people stand

The picture is seen in the first person, standing: the record says so, and
the bridge's two sides and the flagstones seen through the gate all run to
about y 635, which is the eye line. A standing person's eye is about 160 cm
up, so anything on the ground is 160 cm tall where it reaches y 635. `scale`
is that measure written as 200 cm at the foot of the gatehouse's right post,
[1245, 594, 800]. By it the two lanterns beside the gate are about 1.5 m,
the garden wall about 2.6 m and the gate's doors a little over 2 m.

A person on the near gravel therefore measures much less than the game's
usual size: the gate draws people at zoom 0.40 (0.37 a step back) instead of
0.50, about 7% over what the scale gives. On the stage sheet they read as
people standing in the garden with the gatehouse towering over them, which is
what the picture was composed for.

One person stands left of the stepping stones. Two stand either side of
them, and the open gate shows between them. With three or four, someone a
step back stands in front of the doorway and the way to the Courtyard is in
the icon column. The pond's point, on the left water, is left of every row,
so the look is never hidden. Nobody stands in the bush at the bottom left or
behind the near lantern on the right: every row keeps between about x 430 and
x 1500, on the gravel.

## What I was unsure of

- **The size of people.** There is no plain door of a known height beside
  where people stand; the scale rests on the eye line and on the picture
  being seen from a standing eye. If the gate's doors are meant to be 3 m
  tall, people should be smaller still (about zoom 0.30); if the owner finds
  them small as they are, 0.42 is the most the rule allows on this scale.
- **The eye line**, read to about 10 px from the bridge and the flagstones,
  which do not agree exactly (636 and about 626).
- **Whether the bridge should take the click.** The record says the
  Courtyard "is reached over the plank bridge, up the steps and through the
  open gate", so the bridge is the exit's second polygon and lights with the
  gatehouse. People often stand in front of it.
- **The water right of the near lantern** is a small strip between the
  lantern and the bush; it is traced so that the pond does not stop dead at
  the lantern, and can be dropped without changing anything else.

## For whoever installs it, and for wave 1

- U4 registers `gate_pond` as a look, not front. Run `check_layout.py` again
  then, so that its name plate is measured and no longer guessed.
- `check_layout.py` reads `tools/bgs/campus.json`, where the gate is still a
  proposal; `check_campus.py --layout ... --record
  tools/art/staged/early/campus_for_batch3.json` passes.
- The record's two proposed "seen" rows for the gate hold on this picture:
  the schoolhouse shows above the wall on the left (with the pagoda behind
  it) and a large tiled roof on the right.
- Words that describe the picture (hand-off, never edited here): there is no
  torii and no paved road; the way is a plank bridge over a pond, stepping
  stones in raked gravel, and three stone steps.

## Review 1 (12 Oct 2026, a second reading)

Every shape was drawn again over the picture with a separate script and read
enlarged. One thing was mended: the pond's polygon right of the bridge lay
over the near lantern's cap and shaft (as far as x 1688); it now stops at the
lantern's own edge (x 1634 to 1668) and runs 12 px further down beside it,
to the water's edge at y 984. The gatehouse, the bridge and the other two
polygons of the pond were left as they were; both checks pass as before.
