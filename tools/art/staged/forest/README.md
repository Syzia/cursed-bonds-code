# The Forest Trail's layout, staged

Laid out on 12 Oct 2026 on the Forest Trail the owner chose on 11 Oct
(sitting 17a, version A, with the root seat of 17b),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_forest2a_root_00001_.png`,
as fitted in `~/Desktop/JJK Game images/ui2/early/chosen/forest_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet. The evening and night pictures were made
from this same day picture, so the layout holds for them.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_forest.json` | the exit's and the planned hotspot's points, the side each name opens, and their shapes | yes |
| `view_forest.json` | where one to four people stand, the ground they stand on (and the patch round the markers where nobody does), the scale | yes |
| `check_forest.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_forest__trailhead` | the trail's earth along the bottom edge of the picture, between the ferns on the left and the ferns on the right: the way back is behind the camera (one polygon) | (1320, 992), on the earth, right of where people stand | above |
| `stone_markers` (planned, a look) | the two square stone markers on the right, one polygon each, traced on the stone from the top face to the foot | (1492, 672), on the farther marker | left |

No hotspot keeps a button. No shape reaches the top bar or either lane.

**The way back is not painted as a thing.** The picture looks along the
trail, deeper into the forest; the Mountain Path lies behind the camera.
So the exit is the trail under the player's feet, at the bottom of the
picture, as the art sitting planned it (17a: "the trail under my feet as the
way back") and as the Library's and the Courtyard's ways back are. The record
has no row for which side this exit lies on; its first guess was (960, 985),
and the point was moved right along the same band, to x 1320, so that rows of
one to three people do not stand on it.

**The trail that runs on ahead leads nowhere in the game.** It is the
plainest path in the picture and nothing happens when it is clicked: the
Forest Trail has one exit. It is left unlit, because nothing may be clickable
that goes nowhere; the owner may want to know that the eye is drawn to it.

## Where people stand

The picture is seen from standing height on level ground. Its eye line is
at about y 468, where the trail is lost among the trunks. Nothing in the
picture has a known height (no door, no post), so the scale is reasoned, not
measured: with the camera 150 cm up, the root seat comes out 46 cm high, the
trail 2.3 m wide where it leaves the clearing ("wide enough for two"), and
the nearer marker 88 cm tall. Those three agree, so `scale` is what a 200 cm
post would measure standing at the nearer marker's foot, `[1594, 358, 797]`
(439 px).

By it the game's usual size is right: zoom 0.5 with the feet at y 972, and
0.46 a step back with the feet at y 929 (both within 2% of the scale). On the
stage sheet the markers come to a person's waist.

- One person stands in the middle of the clearing (x 800).
- Two at x 620 and x 1000; three at 540, 800 (a step back) and 1060.
- Four at 500, 760 and 1010 (a step back) and 1260. The person on the right
  then covers the way back's point: it is in the icon column (3 tiles of 8).
- Nobody stands right of x 1260, so the markers are never hidden; nobody
  stands left of x 500, where the ferns begin; and a patch of ground round
  the markers' feet is marked as not for standing.

The root seat is not a standing place; a seated pose is the pose sittings'.

## What I was unsure of

- **The scale**, as said: reasoned from an eye height of 150 cm. If the
  owner reads people as too large or too small beside the markers, the zoom
  is the number to change (the markers would be 100 cm with the camera at
  170 cm, and people then 12% smaller).
- **How far up the earth the way back should reach.** It is a band 112 px
  deep, from y 968 down; the ground has no edge there to trace.
- **Megumi's painted pose** (crouched on the trail with the white dog, pose
  row 40) is not laid out here; its box is the pose installer's.

## A refusal that is the record's, not the layout's

`python3 tools/check_layout.py tools/art/staged/forest` says REFUSED twice,
the same sentence for each file: "for_rev is only for a composed picture or
a new place: pictures.json does not call 'forest' \"composed\"". The Forest
Trail was composed again (plan 5.3; `pictures.forest.kind` in the early
record is "composed"), but the game's manifest has no row for it yet and
`place.forest` in both records still reads `"how": "inplace"`, which is what
the check looks at. With a manifest that calls the forest composed (a
scratch root, or the installer's own run) the same files read
`PASS (0 reported)`. `for_rev: 2` is kept, as 3.2 asks of a composed picture;
whoever installs the picture changes `place.forest`'s `how` to `composed`
first, or installs with `--compose`, which writes the manifest row.

## For whoever installs it, and for wave 1

- U4 registers `stone_markers` as a look, not front. Run `check_layout.py`
  again then, so that its name plate is measured and no longer guessed.
- The look line for the markers (sb_hotspots.rpy) should fit two plain
  square-cut stones with nothing carved on them.
