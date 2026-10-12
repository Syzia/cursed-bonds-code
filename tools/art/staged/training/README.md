# The Training Hall's layout, staged

Laid out on 12 Oct 2026 on the Training Hall the owner chose on 11 Oct (O46),
`~/Desktop/JJK Game images/ui2/early/renders/ui2_training2a_view_a_00001_.png`,
as fitted in `~/Desktop/JJK Game images/ui2/early/chosen/training_1920.png`
(2752 x 1536 becomes 1920 x 1072, laid 4 px down). Every number is in the
game's 1920 x 1080 frame, read off gridded crops of the full-size render.
Nothing here is in the game yet.

| file | what it is | goes into the game? |
|---|---|---|
| `hot_training.json` | the exit's and the two planned hotspots' points, the side each name opens, and each shape | yes |
| `view_training.json` | where one to four people stand, the floor they stand on, the scale | yes |
| `check_training.json` | what `tools/check_layout.py` needs and the game does not read: the picture's eye line, and the two open screens as the room's doors | never |

## What is traced (D60)

| id | the thing on the picture | point | name opens |
|---|---|---|---|
| `go_training__training_yard` | the two open screens in the left wall, each as the opening itself, post to post and lintel to sill: the wide one with the yard and its striking posts seen through it, and the narrow one further along (two polygons) | (380, 640), in the wide opening | above |
| `mats` (planned, a look) | the pile of six rolled mats against the back wall, with 4 to 6 px of room round it: traced tight it is about a button's area, the least a shape may be | (1035, 700), on the pile | above |
| `straw_bundles` (planned, Practice) | the four straw bundles leaning along the right wall, as one outline round all four (each overlaps the next, so they are one polygon and not four); their wooden stands are left out | (1650, 740), on the nearest bundle | left |

No hotspot keeps a button, and the exit's thing is in the picture. Nothing
is in front of the people: the room has no foreground outline.

## Where people stand

The picture is seen from low down, about a metre off the floor. The lintel
and the sill of the wide opening run to one point, (1265, 653), so the eye
line is at y 653. `scale` is that opening's far post, lintel to sill, taken
as 200 cm: [582, 497, 810]. By it a person at the game's usual size (0.52)
stands with the feet at y 988, and a step back (0.46) at y 949: 3% and 2%
over what the scale gives. The nearest straw bundle measures about 125 cm
by the same numbers, which is what such a bundle is.

- One person stands on the open floor left of centre (x 700), in the light
  from the wide opening.
- Two stand at x 690 and x 1300: clear of the exit's point, the mats and
  the bundles.
- With three or four, someone a step back stands in front of the mats and
  their point is hidden (a look has no tile in the column, so it waits
  until they move). The way out and the straw bundles are never hidden.

Panda's picture is wider than the others' (880 px, not 760). At x 1300 its
left edge just reaches the mats' square and its right edge is well short of
the bundles' point. `check_layout.py` measures every row at 760 px, so this
was looked at on the stage sheet instead: he stands in front of the weapon
racks, beside the bundles, and the mats are still seen.

## What `check_layout.py` says

**REFUSED, twice, for one reason that is not this layout's:**
`for_rev is only for a composed picture or a new place: pictures.json does
not call 'training' "composed"`. The hall WAS composed again and chosen
(O46; the early record's `pictures` row says `kind: composed`), but its
`place` row still says `how: inplace`, in the game's record and in the early
one, whose own note says "the real record takes how: composed ... when they
are installed". The files carry `"for_rev": 2` as a composed picture's must.
With a scratch copy of the early record in which that one word is changed,
the check reads `PASS (0 reported)`. So: whoever installs the hall writes
`how: composed` first (it is `install_redo.py --compose`'s row), and the
refusal goes with it. The dojo and the storehouse stand the same way.

`check_campus.py --layout ... --record tools/art/staged/early/campus_for_batch3.json`
passes.

## What I was unsure of

- **The exit is both openings.** The record's first guess (380, 640) is in
  the wide one, and the point stays there. The narrow one further along
  opens on the same yard, so it lights too; if the owner finds that odd,
  the second polygon is removed and nothing else changes.
- **The mats' shape has room round it** and is not tight, for the area
  rule (6,471 px² against the least allowed, 5,184).
- **The door's height.** If the opening is 190 cm and not 200, people are
  8% over the scale, still inside the rule's 12%.
- **The two racks on the back wall** (the staves and the wooden swords) are
  not in the game's list and have no shape. They would be the natural next
  thing to click in this room.

## For whoever installs it, and for wave 1

- U4 registers `mats` as a look and `straw_bundles` as Practice; neither is
  front. Until then their shapes are in the file and the game does not draw
  them. Run `check_layout.py` again then, so that their name plates are
  measured and not guessed.
- The code's own slots for the hall (`slots_code`) are replaced by this
  file's, which stand people 34 px further in and move the second, third
  and fourth of each row.
