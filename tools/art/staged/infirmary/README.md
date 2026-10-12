# The Infirmary's layout, staged

Traced on 12 Oct 2026 on the installed picture, `game/images/bg/infirmary.png`
(redone in place, revision 2, render `ui2_infirmary_a_00001_.png`), and laid
over `infirmary_evening.png` and `infirmary_night.png`. Every number is in the
game's 1920 x 1080 frame, read from gridded, enlarged crops of the installed
picture and checked by drawing the outlines back onto it. Nothing here is in
the game. The room is redone in place, so neither file carries `for_rev`.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_infirmary.json` | the exit's, the cot's and the desk's points, the side each name opens, and the shapes | yes |
| `view_infirmary.json` | where one to four people stand, the floor, the scale | yes |
| `check_infirmary.json` | the eye line, for `tools/check_layout.py` only | never |

## What the room's files held, and what changed

- `game/layout/hot_infirmary.json` held one key, `spots.cot` = (1420, 700).
  **Kept as it is**: that point is on the far cot's mattress.
- The way out had no point in a file: the code's own was (84, 500), which is
  on the left wall's window. **Moved** to the bottom band, (880, 1000).
- `shoko_desk` (planned) had no point: placed.
- There was no `view_infirmary.json`: the room stood people on the code's
  slots (zoom 0.54 and 0.50, x 260 to 1150), which put the outer people of a
  row of three or four inside the desk and on the beds. All four rows are new.
- `light_infirmary.json` is the installer's and is not touched. The room has
  no keep list and no foreground outline (the plan gives it none).

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_infirmary__school_yard` | a band of open boards along the bottom edge, from the desk's side to the near cot's leg: the picture shows no door (the door is behind the camera) | (880, 1000) | above |
| `cot` (the registered act, resting) | the two cots as one outline: the far cot's foot end with its two castors, its mattress and pillow as far as the curtain that hangs in front of its head, and the near cot whole, from its foot end to the right edge of the picture | (1420, 700), on the far cot's mattress, where it was | right, onto the far mattress |
| `shoko_desk` (planned, a look) | the desk with what stands on it (the file box, the binders, the monitor, the mug) and its chair, which stands against its side | (330, 735), on the desk top | above |

One polygon each. The two cots are one polygon because the near cot's foot
end stands in front of the far cot's mattress: two outlines would cross. The
curtain between the cots, the bedside cabinets, the trolley, the couch, the
cupboards and the filing cabinets are not things to click. No hotspot keeps a
button.

## Where people stand

The eye line is taken at y 515: the top and bottom edges of the near cot's
foot board, the desk's right edge and the right wall's beam meet between
y 500 and y 531 near x 730. That is a camera about 1 m up. The scale is read
at the back wall: with that eye line the filing cabinets (top y 437, foot
y 765) come to 131 cm, which is what a four-drawer cabinet is, the couch to
66 cm and the trolley to about 85 cm. `scale` is the filing cabinets' left
edge carried up to 200 cm, [1024, 265, 765].

The camera is low and close, so a person at the bottom of the picture would
be far larger than the game's usual size. People stand further in, on the
boards between the desk's chair and the cots: feet at y 900 at zoom 0.56,
and a step back at y 872 (just in front of the trolley, zoom 0.52) or y 850
(left of the trolley, in front of the couch, zoom 0.50). The scale asks 4%,
3% and 1% more.

The open floor is narrow: about 345 px between the chair and the far cot's
castor. One person stands at x 770; two at 700 and 992; three and four stand
close, alternately near and a step back (the row of four as the second
reading, below, left it). No row hides the cot's or the desk's
point, and the way out, in the band below everyone's feet, is never hidden,
so nothing drops into the icon column. Nobody stands on or between the cots,
behind the desk or on the couch. The floor polygon leaves out the trolley's
footprint and the far cot's castor.

## What check_layout.py says

`python3 tools/check_layout.py tools/art/staged/infirmary`: PASS, nothing
refused, nothing reported. `python3 tools/check_campus.py --layout ...`:
PASS (0 reported; its 18 "waits for a batch" lines are other places').

## The evening and the night picture

The outlines were laid over both: nothing has moved and every outline still
follows its thing. Corners a relight proof may find hard:

- the desk: (46, 622), (95, 620), (97, 606), (258, 603), (272, 603),
  (263, 513) are corners of the binders and the monitor **against the window
  glass**; (263, 513), (396, 510), (414, 648) are the monitor's corners, and
  the monitor is **lit at night** and throws a glow on the wall beside it.
- the way out: (566, 955) and (1190, 955) are on open boards (each a few
  pixels from the desk's side and the cot's leg); the band's top edge crosses
  the window's streak on the floor, and in the evening a patch of sunlight
  lies over its right end.
- the cots: the outline follows the frames and the mattresses' edges; in the
  evening sunlight lies in bars across both mattresses and the near foot
  board, inside the outline.

## Unsure of

- **The exit has no door in the picture.** The record says only that the
  infirmary's door is the way in from the School Courtyard; the room shows
  the left wall's windows, the back wall and the cots. The point is in the
  bottom band, as the Library's is.
- **The eye line** (500 to 531 by different lines). At 500 or 531 people are
  still within 8% of what the scale gives.
- **The close rows.** Three and four people overlap one another, and Panda
  (880 px canvas) in the leftmost place overlaps the chair's back, in the
  rightmost the foot ends of both cots by about 35 px; he hides neither point
  nor the end of a name. The room leaves no wider row.
- **One outline for two cots.** If only one cot should light, it is the far
  one (the point is on it), cut at the near foot board.
- **The chair is traced with the desk.** Without it the desk's outline would
  be cut round the chair's back and seat.
- The desk's name plate is a guess (150 x 29 px) until U4 registers it.
- The exit's name opens above its point, at about y 931 to 960; the feet of
  the near row end at about y 921 (Panda's at 930), and a name is drawn under
  the people. The name tags' row is below the point.

## For whoever installs it, and for wave 1

- U4 registers `shoko_desk` as a look, not front. Run `check_layout.py`
  again then.
- The installer's relight proof is run on these outlines when the layout is
  staged; see the corners named above.

## The second reading (12 Oct 2026)

- **The row of four was spread.** It was x 690 (back), 800, 912 (back),
  1018, and the two at the back were mostly hidden behind the two in front.
  It is now x 660 (back, feet y 850, zoom 0.50), 800 (feet y 900, 0.56),
  935 (back, feet y 872, 0.52) and 1100 (feet y 942, zoom 0.60): the fourth
  stands nearer, on the boards in front of the far cot's castor and beside
  the near cot's foot board, 7% under what the scale gives there.
- The way out's point moved from (880, 998) to (880, 1000), so that the
  nearer fourth person's rectangle does not reach its square.
- The cot's name opens to the RIGHT of its point now (onto the far
  mattress), not the left: at the left its plate began at x 1259, where the
  arm of a wide figure in the rightmost place reaches.
- The relight proof, computed in memory on these outlines against the
  installed evening and night pictures: PASS both, the furthest outline 2 px
  off (the desk, at night).
