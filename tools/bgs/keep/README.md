# Keep lists

One file a picture, `<picture>.json` (the picture's file name: `your_room`,
not `dorm`). `docs/UI2_DESIGN.md` 5.4 has the rules. They are data for
`tools/install_redo.py`; they add no words to any prompt, except that the
`allow` and `change` rows are the words of a named addition or change
(`tools/make_redo_workflow.py --add`, `--change`).

| key | what it is | what the installer does with it |
|---|---|---|
| `keep` | things that must still be there: `{"name", "box": [x, y, w, h]}` | "nothing vanished": below the threshold the picture is REFUSED and the thing is named |
| `empty` | places that must not gain anything: a `box`, or a `poly` of `[x, y]` points | "nothing was added": above the threshold the picture is REFUSED and the place is named; a place wider or taller than 250 px (a floor) is also judged in overlapping 160 px parts, so one thing set down on it is found. A floor polygon does not cover a rug, a table top or a bed cover: each open surface a thing could be set down on needs a row of its own (the Common Room's rug has one) |
| `allow` | the room's one named addition, or a window that is meant to change | an `empty` zone or tile inside it is not judged |
| `change` | a box meant to change inside a fixed outline (5.2's fallback only) | left out of "vanished" and "added"; its outline must still agree within 3 px |
| `doors` | the room's painted doors: `{"name", "box"}` | kept like a `keep` row ("nothing vanished": a door painted out is REFUSED and named); also read by `tools/check_layout.py` (an indoor exit sits on a door or in the bottom band) |
| `windows` | the room's glass, pane by pane: `{"name", "box"}` or a `poly`, drawn just INSIDE the frame, so that the frame's own edge stays outside it | left out of every guard window and keep box. A point that lies on glass (an exit on a glass door) is held by the post, the handle and the frame round it, and a view changed on purpose behind it is a LOOK, not a moved door. Only where a registered point's 192 px window reaches glass does a room need them |
| `ground` | open ground or open water whose light and shadow change with the hour (the earth of a path under trees, a lawn, a river's surface): `{"name", "box"}` or a `poly`, drawn just INSIDE the ground's edges, so that the banks, the stones and the verge stay outside it | in a RELIGHT only, and only in "nothing moved": left out of every registered point's window as glass is, so a point that lies on it is held by what stands round it. A point whose window is nearly all ground cannot be held, and the report says so. It does nothing in a picture redone in place, nothing to "vanished" or "added", and it is not `change` (a named re-skin, whose words go into a prompt) |
| `scale` | `[x, y top, y bottom]` of one door or post, taken as 200 cm | the height in a pose's prompt, until the room's `view_` file has its own |

All numbers are on the 1920x1080 picture. Besides these rows the installer
keeps, by itself, a 110 px box round every exit and hotspot of the room and
the bounding box of every foreground polygon.

The six files here were written in wave 0 (U0d2) for the pictures of batches
0, 3 and 4, read off the game's pictures and the two chosen ones with a 100 px
grid. The art-install role corrects them at each room's sitting (about ten
minutes a room, with `tools/layout_sheet.py`), and writes the others before
their batches.

- `dorm_common`, `cafeteria`: redone in place (batch 0's third-test renders;
  run again in 3a and 4a). The Common Room's `windows` are the four panes of
  the sliding door on the left: the way to the garden sits on its glass, and
  the chosen render of 3a shows the boys' dormitory through it (U0d3). The Common Room's `scale` is the post in the left
  wall beside the sofa, floor to lintel: it is there so that batch 5's pose
  prompt can say how tall Nobara stands before the room's layout sitting.
- `your_room` (My Room), `girls_dorm`: batches 3a and 4a. My Room's `allow` is
  its one addition, a closed laptop on the desk.
- `courtyard`, `library`: composed again, already chosen; nothing is kept,
  emptied or allowed in a composed picture. They hold the `scale` their poses
  need (the vending machine; the far wall's post) and no door: the Courtyard
  is outdoors, and the chosen Library shows none, because I stand in it.
- `trailhead` (the Mountain Path), written on 12 Oct 2026 for its evening: one
  `ground` row, the earth of the way to the river where leaf shadow lies by
  day and low sun in the evening. A corner of that way's traced outline lies
  on it, and the evening the owner chose was refused there.
