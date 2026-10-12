# The Mountain Ridge's layout, staged

Laid out on 12 Oct 2026 on the Mountain Ridge the owner chose on 11 Oct
(sitting 17a, version A, O55),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_ridge2_a_00001_.png`, as
fitted in `~/Desktop/JJK Game images/ui2/early/chosen/ridge_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_ridge.json` | the exit's and the hotspot's points, the side each name opens, and their shapes | yes |
| `view_ridge.json` | where one to four people stand, the ground they stand on, the scale | yes |
| `check_ridge.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `veil` (the registered act: the look up at the veil) | the black dome on the rise beyond the rope, and nothing else: its round edge against the sky and its foot along the grass (one polygon, 16 corners, about 107 px wide and 70 tall) | (748, 214), inside the dome near its right edge | right |
| `go_ridge__trailhead` | the head of the stone stairs at the bottom of the picture, whole: the two stone kerbs and the three treads between them, from the back edge of the top tread down to the picture's bottom edge (one polygon) | (735, 962), on the second tread | above |

No hotspot keeps a button. The place has no planned hotspot. Both things are
in the picture: nothing was placed on a guess. No shape reaches the top bar
or either lane (the dome's top is at y 174, the banner lane ends at y 170).

The rope, its two posts and the flat rock are not in the game's list for
this place and have no shape. The path that climbs on beyond the rope leads
nowhere in the game and is not lit.

**Why the veil's name opens to the right, from the dome's right side.** The
arrival caption covers x 40 to 784 and y 100 to 260, and the dome (x 652 to
759, y 174 to 244) lies inside it. Opened to the left, as a hotspot's name
is by default, the name would sit wholly under the caption. From (748, 214)
and opened to the right its plate begins at x 784, just clear of it, over
the sky.

## Where people stand

Everybody stands on this side of the rope, on the shoulder of grass and
earth between the rope and the head of the stairs. The floor polygon is
that shoulder, drawn a little inside its edges: from the rope's line (y 560)
down to y 866 (the top of the stairs' kerbs), on the left as far as the
grass goes before the rock face, on the right round the foot of the flat
rock and in along the grass before the drop. Nobody stands on the rock,
beyond the rope, on the stairs or on the rock faces below.

The eye line is at y 328 (`check_ridge.json`). The picture has no straight
lines running away from the camera, so it is reasoned: the two posts are
"head high" in the words the picture was painted from, their tops are at
y 326 and 327, and a camera at head height sees every head-high thing end
on its eye line; the far valley floor meets the hills near the same height.
The left post (x 520 to 538, top y 327, foot y 541: 214 px) is taken as
170 cm, so a 200 cm post there would be 251 px, and `scale` is
`[529, 290, 541]`. By it the stairs come out about 113 cm wide between
their kerbs, which is what the Mountain Path's stairs look like.

By that measure people are a little smaller than the game's usual size:
zoom 0.47 with the feet at y 858 and 0.43 a step back with the feet at
y 812 (both within 1% of what the scale gives). On the stage sheet every
head comes level with the posts' tops, as it should.

- One person stands right of the path (x 1000), so the rope, the path up
  and the dome are all open.
- Two stand either side of the path (x 440 and 1010).
- Three: 430 and 975 in front, one a step back at 1250, before the rock.
- Four: 300 and 985 in front, 545 and 1260 a step back.

No row hides either thing: heads end at about y 325 and the dome's foot is
at y 244, the stairs are below everybody's feet, and no row's rectangle
touches the dome's square, so with four people nothing drops into the icon
column (2 tiles of 8). The exit's name opens at y 897 to 926, below the feet
of every row, and the name tags are lower still.

None of this place is in the dump's `fg_rooms`: nobody stands behind
anything, and the person a step back on the right stands in front of the
rock (its foot is at y 715 there, the feet at y 812).

With Panda (880 px wide) at x 300 and somebody at x 545 a step back, his
arm covers about half of that person; the names are not touched. The grass
ends at about x 200 there, so the row cannot be spread further left.

## Corners on open ground, grass or water

None. Every corner of the dome's shape is on the dome's own edge (against
the sky, and along the grass at its foot), and every corner of the stairs'
shape is on stone: the kerbs' outer edges, the kerbs' top corners, and the
back edge of the top tread where the stone meets the earth, (564, 888) and
(910, 888). The two bottom corners are on the picture's bottom edge
(y 1076). The outlines were laid over the chosen evening render
(`ui2_ridge_evening_b_00001_.png`) and the chosen night render
(`ui2_ridge_night_a_00001_.png`) by eye and follow the dome and the stairs
in both; the installer's own proof has not been run (no game is run here).
At night the dome has a bright rim on its right side: it is inside the
outline.

## What I was unsure of

- **The scale** rests on "head high" meaning 170 cm. Posts of 180 cm would
  make people 6% smaller, of 160 cm 6% larger; both are inside the 12% the
  rule allows. The shoulder is taken as level; if it rises a little toward
  the rope, the people a step back are a few per cent large.
- **The veil's point** is 11 px inside the dome's right edge, for the
  caption's sake. If the owner would rather the name open over the dome's
  middle, the point is (705, 212) and the name is then under the arrival
  caption until it fades.
- **The stairs' top edge** is the back of the top tread (y 888). The strip
  of earth between the kerbs above it (y 866 to 888) is ground, not stairs,
  and is left out.

## A refusal that is the record's, not the layout's

`python3 tools/check_layout.py tools/art/staged/ridge` says REFUSED twice,
once for each file: "for_rev is only for a composed picture or a new place:
pictures.json does not call 'ridge' "composed"". The ridge was composed
again (sitting 17a; `pictures.ridge.kind` in the early record is
"composed"), but `place.ridge` in both records still reads
`"how": "inplace"`. Proved against a scratch copy of
`tools/art/staged/early/campus_for_batch3.json` with that one word set to
"composed" (`--record <copy>`): `PASS (0 reported)`. Both real records were
left alone; the word is the orchestrator's to change at the install.
`check_campus.py --layout ... --record tools/art/staged/early/campus_for_batch3.json`
passes (0 reported).

## For whoever installs it, and for wave 1

- The record has no row for which side this exit lies on; its first guess
  was (732, 960), on the stairs, and the point is kept there (735, 962).
- The game's own point for `veil` today is (960, 250), in the sky of the
  old picture, and `frames.keep_clear.ridge` still names it: that row wants
  moving to (748, 214) with the install.
- The look line (sb_world.rpy:1325, "I look up past the rope markers. The
  veil sits on the top of the ridge") fits the picture as it is.
- Toge's and Gojo's painted poses on the rock (pose rows 62 and 23) are not
  laid out here; their boxes are the pose installer's. The rock's flat top
  runs from about x 1200 to 1670 at y 580 to 640.

## Review 1 (12 Oct 2026, a second reading)

Both shapes were drawn again over the picture with a separate script and
read enlarged (the dome at 8 times, the stairs at 3): the dome's outline is
on its edge all the way round and along the grass at its foot, the stairs'
on the kerbs' outer edges and the back of the top tread. Nothing was
changed. A row of four with Panda first was drawn: at x 300 his left paw is
at the grass's edge above the drop (an ordinary person's feet are 20 px
inside it), and he covers the left half of the person a step back; no name
is touched, and that person cannot move right, because his rectangle ends
4 px left of the dome's square.

`check_layout.py ... --record <scratch copy with "how": "composed">`: PASS
(0 reported). `check_campus.py --layout ... --record
tools/art/staged/early/campus_for_batch3.json`: PASS (0 reported).
