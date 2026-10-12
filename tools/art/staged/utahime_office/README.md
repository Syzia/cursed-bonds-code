# Utahime's Office's layout, staged

Traced on 12 Oct 2026 on the picture the owner chose,
`~/Desktop/JJK Game images/ui2/early/chosen/utahime_office_1920.png` (render
`ui2_utahime_office2_b_00001_.png`, 2752 x 1536, fitted to 1920 x 1072 and
laid 4 px down). Every number is in the game's 1920 x 1080 frame; edges were
read from gridded crops of the full-size render. Nothing here is in the game.
The evening picture was made from this one, so the layout holds for it.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_utahime_office.json` | the exit's, the board's and the binders' points, the side each name opens, and the shapes | yes |
| `view_utahime_office.json` | where one to four people stand, the floor (and the desk's and the chair's footprints), the scale | yes |
| `check_utahime_office.json` | the eye line, the painted door's box, and the desk's outline (`fg`) on the new picture, for the tools only | never |

**`for_rev: 2` is in both files, and `check_layout.py` refuses it as the
record stands**, exactly as it did for the Principal's Office: the picture
was composed again (the record's `pictures` row says "composed") but the
`place.utahime_office` row still says `"how": "inplace"`. It prints two
REFUSED lines (`file`: "for_rev is only for a composed picture"), and nothing
else is refused. With that one word changed to "composed" in a scratch copy
of the early record the check PASSES with three REPORT lines. The record is
not this folder's to edit.

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_utahime_office__staff_yard` | the open sliding door in the left wall: the whole opening, from the slid-back leaf to the jamb and from the lintel to the sill, with the yard's gravel and paving seen through it | (275, 600), in the opening (the record's first guess) | above |
| `board` (registered, the mission board) | the cork board of pinned notices on the right wall, by its frame's four corners (the flowers stand in front of its lower left corner) | (1405, 462), on its lower right part, below the toast lane | left |
| `binders` (planned, a look) | the files on the shelves behind the desk, two polygons: the four ring binders with the three books leaning on them (middle shelf), and the row of files above them | (1040, 420), on the ring binders | above |

No hotspot keeps a button; no shape overlaps another. The round window, the
desk, the vase and the cabinet are not clickable.

## The desk is the room's foreground

*Done at the install, 12 Oct 2026: the outline below is the day outline of
`tools/fg/utahime_office.json`, and the foreground was cut again from the
installed picture (5.4% of the frame).*

The game draws this room's desk over the people (`VIEW_FG_ROOMS`), and
`tools/fg/utahime_office.json` still holds the OLD picture's desk. The new
desk's outline (the desk, with the brush stand, the pen cup and the lamp on
it) is in `check_utahime_office.json` under `fg`; the sheets were drawn with
it. **Whoever installs the picture must write that outline to
`tools/fg/utahime_office.json`**, or the foreground is cut from the wrong
part of the picture.

## Where people stand

The eye line is at y 350 (the door's head and sill lines, and the board's
top and bottom edges, meet there): a standing camera. `scale` is the door's
jamb, [406, 144, 834], 690 px taken as 200 cm. By it a person at the game's
usual size (zoom 0.52) stands level with the desk's front legs, feet at about
y 840, not at the bottom of the picture, where the floor is very close to the
camera; name tags stay at the bottom edge, about 195 px below the feet.
Because the desk is drawn over everyone, nobody stands in front of it:

- one person stands left of the desk, in front of the round window (x 590);
- the second stands behind the desk, a step back (x 860, zoom 0.37, feet at
  y 681: by the scale a person there is 408 px tall, and is seen from the
  hips up over the desk top);
- the third stands right of the desk, in front of the chair and the cabinet
  (x 1280);
- with four, the first two near people stand in the doorway's light (x 440,
  zoom 0.55 because that spot is nearer) and left of the desk (x 650).

One and two people hide nothing. Three hide the board's point (the third
person stands in front of it: the mission board is then in the icon column);
four hide the board's and the way out. The binders' point is never hidden.
The desk's footprint and the chair with the paper tubs are no-stand polygons.

## What check_layout.py reports, and why it stands

- `board`: 50% of it is inside the toast lane. The board hangs there; its
  point is below the lane.
- the door: under 1% of it is above y 92 and under 1% inside the banner
  lane: the top left corner of the opening.

`check_campus.py --layout ... --record .../campus_for_batch3.json`: PASS.

## Unsure of

- **`for_rev`**, above: the record's place row is the orchestrator's.
- **The person behind the desk is small** (zoom 0.37, softened and dimmed as
  a step back is). It is what the door's scale gives at that depth, and on
  the sheet it reads as someone standing behind the desk; if it reads too
  small in the game, the other choice is to stand nobody there and let a
  second person stand right of the desk, which hides the board with two.
- The code's pose box for Utahime ([400, 376, 236, 300]) belongs to the old
  picture's desk and is not this layout's to move; a painted pose at the new
  desk is a later sitting's.
- The binders' name plate is a guess (150 by 29 px) until U4 registers it;
  it opens between the two polygons.
- The scale takes the door as 200 cm.

## For whoever installs it, and for wave 1

- Write the `fg` outline to `tools/fg/utahime_office.json` (above), and let
  the installer recut the foreground for the day and the evening.
- U4 registers `binders` as a look, not in front; run `check_layout.py`
  again then.
- The board's point moved from (1500, 470) to (1405, 462): the new board
  hangs further left, clear of the icon column.
