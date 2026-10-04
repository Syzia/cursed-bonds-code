# Phase 2 art: what is made, and how to make the rest

*Jujutsu Kaisen: Cursed Bonds · written by P8, 5 Oct 2026. This is section 5 of
`docs/PHASE2_DESIGN.md` as numbered steps, with the prices the tools print.
The sprite and background recipes of phase 1 are in `docs/ASSET_PIPELINE.md`.*

**Nothing in the game waits for any of this.** Every picture has a stand-in
the game draws by itself, and each real picture drops in by file name. Nothing
in the script changes.

## The hand-off habit

It is the same four steps every time, as with the sprites:

1. **Claude runs the tool.** It writes a drag-in workflow `.json` into
   `~/Desktop/JJK Game images/phase2/`, already loaded with the pictures and
   the prompt, and a short note (`art_batch_<n>.md`) with numbered steps and
   what to look for.
2. **You drag the file into the local ComfyUI (Comfy Desktop) and press
   Run.** You never need to save anything: the results land in
   `~/ComfyUI-Shared/output`.
3. **You say which version you prefer.** Pose versions are stacked in the
   workflow: **Version A is on top, Version B below it** (say "top" or
   "bottom"). Background versions are side by side (left, right).
4. **Claude installs it.** The install tool resizes and checks the picture,
   writes the game file, and shows you a preview in `shots/art/`. Then you
   look at it **in the game**, not only in ComfyUI.

Before you press Run you can check your credit balance: click your account
picture at the top right of ComfyUI, or open Settings (the gear, bottom left)
and choose Credits. If a run stops with a rate-limit or "high demand" error,
wait a minute and press Run again; a picture that already finished is not
paid for twice, as long as ComfyUI hasn't been restarted in between.

## What things cost

These are the prices the tools print. Nothing runs on this Mac's graphics
card.

| what | made with | price |
|---|---|---|
| a painted pose (two versions) | Nano Banana Pro, $0.16 a picture | about **$0.32** |
| blink and talk for one person (one picture each) | Nano Banana Pro | about **$0.32**; a redo of one is $0.16 |
| talk only (Gojo, Yaga) | Nano Banana Pro | about **$0.16** |
| an icon sheet (two versions) | Nano Banana Pro | about $0.32 |
| a background (two versions) | Krea 2, about $0.035 a picture | about **$0.07** |
| a foreground layer | cut from the background by `tools/make_fg.py` | free |

The plan guessed $0.64 for a person's blink and talk; it is $0.32, because
each is one picture, not two.

## What batches 1 to 3 delivered

About **$2.97** spent so far.

| batch | when | what | cost |
|---|---|---|---|
| 1 | after checkpoint A | the 88 icons (three sheets), the six area maps, the Tokyo map | $1.45 |
| 2 | after checkpoint B | the Library, Utahime's office, Gojo's office | $0.21 |
| 3 | after checkpoint C | the five yards (School Courtyard, Dormitory Garden, Staff Building Steps, Training Yard, Mountain Path); **the tests:** Yuji's blink and talk, Nobara on the sofa (evening), Utahime at her desk | $1.31 |

Also made, free: five foreground layers (the common room by day, evening and
night; the cafeteria; Utahime's office), and the four small GUI pictures
(the Special Grade sheen, the hotspot glow, the soft box for poses, the card
back).

You judged the three tests in play at checkpoint C and asked for no change,
so batches 4 and 5 can go ahead whenever you like.

## What is still to make

About **$6.72** in all, in two batches, plus free foreground layers.

| batch | what | pictures | cost |
|---|---|---|---|
| 4 | the other twelve poses | 24 (two versions each) | about $3.84 |
| 5 | blink and talk for the other ten people | 18 | about $2.88 |
| – | foreground layers, when a room needs one | – | free |

---

## Batch 4: the other twelve poses

A pose is one whole picture of a room with one person painted in, doing what
their caption says. The game cuts a soft-edged box around the person and lays
it over the room it already has. So the rest of the room must come back
untouched.

| # | who | where | doing | notes |
|---|---|---|---|---|
| 3 | Yuji | Cafeteria | halfway through an enormous bowl | |
| 4 | Megumi | Classroom | reading at a desk by the window | |
| 5 | Shoko | Infirmary | at the counter with coffee | a day picture: see "Shoko at night" below |
| 6 | Maki | Training Hall | drilling with a staff | |
| 7 | Yaga | Principal's Office | sewing a cursed doll | |
| 8 | Ijichi | Main Gate | on the phone beside the car | |
| 9 | Toge | Cafeteria | with onigiri, at the far table | |
| 10 | Panda | Courtyard | stretching, waiting for a sparring partner | |
| 11 | Yuji | Courtyard | beside the vending machine, a can in his hand | the courtyard picture has no machine painted in; the prompt keeps him to one side of where its icon sits |
| 12 | Megumi | Library | three books deep | |
| 13 | Gojo | Gojo's Office | on the sofa, eating mochi in front of the TV | |
| 14 | Gojo | Mountain Ridge | sitting just outside the veil | seen only on a Gojo night |

### Steps

1. **Claude** checks the list still matches the schedule: `python3
   tools/make_pose_workflow.py --list` prints the fourteen rows and the total,
   and `tools/smoke.sh tools/smoke/p2_view.rpy` fails if a row names a place
   that person's routine never puts them. A row that fails is dropped or
   moved before anything is paid for.
2. **Claude** runs `python3 tools/make_pose_workflow.py --batch 4`. It writes
   twelve files, `pose_<place>__<who>.json`, into `~/Desktop/JJK Game
   images/phase2/`, with each room's picture and each person on plain grey
   beside them, and copies those pictures into ComfyUI's input folder.
   (One pose alone: `python3 tools/make_pose_workflow.py cafeteria yuji`; the
   two names can go in either order.)
3. **You** drag one file onto the ComfyUI window. The two Load Image boxes on
   the left should show the room and the person on grey. If one shows an
   error, click "choose file to upload" in that box and pick the file from
   the `phase2` folder.
4. **You** press **Run**. Two boxes each paint the whole room once: **Version
   A on top, Version B below it.** About $0.32.
5. **You** look for three things: the person is where the caption says and
   the right size for the furniture; they are still clearly themselves; and
   **everything else in the room looks untouched**.
6. **You** tell Claude "Yuji's cafeteria pose is done", and "top" or "bottom"
   if you have a favourite. You can do several files before saying so.
7. **Claude** runs `python3 tools/install_pose.py <the picture>` (first with
   `--dry` to look). The tool:
   - brings the picture to 1920×1080 and compares it with the room;
   - **refuses it if more than 35% of the room changed** (the room was
     repainted, so the box would show a seam): then the other version is
     tried;
   - measures the box around the person and writes it to
     `game/layout/view_<place>.json`;
   - writes a side-by-side preview to `shots/art/` and the picture to
     `game/images/place/`.
8. **Claude** checks the two things batch 3 taught:
   - **the fit.** The editor lays the room across the render's whole width,
     so a 2752×1536 render is the room at 1920×1072, 4 px down. A good pose
     reads a few percent changed (batch 3's two read 4.0% and 1.7%). The tool
     does this fit itself (scaled to 1920 wide, the height centred). If a
     picture that looks right still reads over 10%, with changed blocks all
     along the edges, the editor repainted the room: try the other version;
   - **the box.** On a seated pose the automatic box can miss the feet or the
     floor shadow. Look at the preview; set it by hand with `--box x,y,w,h`
     when it is short.
9. **Claude** draws the room's sheet, `python3 tools/layout_sheet.py
   view_<place>` (after `tools/smoke.sh tools/smoke/p2_contracts.rpy` has
   refreshed the numbers), and looks at the people who still stand beside the
   pose. If two of them overlap, the room gets its own slots row in the
   sidecar.
10. **You** see it in the game at the hour that person is there, and say
    whether it looks right.

### Rules a pose has to keep

- **It is painted on the picture you actually see at that hour.** Nobara's is
  on the evening common room, and is named for it
  (`pose_dorm_common__nobara__evening.png`). A day pose is never laid on a
  night room: where the room has its own evening or night picture and there
  is no pose for it, the person is their standing sprite.
- **The editor is never told a name.** It gets the room and the person on
  grey, and the words "change nothing else".
- **A pose shows whenever its file exists for the hour,** whatever the caption
  says that day. If a story caption later says the person is doing something
  else in that room, that needs a second pose.
- **Someone walking with me never takes their pose.**

### Shoko at night (optional, one more picture)

Shoko's planned pose is a day picture, and the infirmary has its own night
picture. So at Night she will stand as her sprite. If you want her seated at
Night too, that is one more pose on `infirmary_night.png` (about $0.32).
Claude first adds a row for it to the list in `tools/make_pose_workflow.py`
(`POSES`: where in the room, doing what), then runs `python3
tools/make_pose_workflow.py infirmary shoko night`.

---

## Batch 5: blink and talk for the other ten

Yuji's pair is installed and was the test. The other ten on campus: Megumi,
Nobara, Maki, Panda, Toge, Shoko, Ijichi and Utahime get both; **Gojo and
Yaga get talk only** (his eyes are under the blindfold, Yaga's behind
glasses). That is 18 pictures, about $2.88.

Sana and Kaito have none: Kaito is never on screen and Sana is only in the
prologue. Adding her later is two pictures ($0.32) and no script change.

### Steps, once per person

1. **Claude** runs `python3 tools/install_face.py --prepare <who>`. It cuts a
   square around the head from the game's own neutral sprite, puts it on flat
   green and writes `<who>_fx_in.png` into `~/Desktop/JJK Game images` (and
   ComfyUI's input folder).
2. **Claude** runs `python3 tools/make_edit_workflow.py <who> --only
   blink,talk` (for Gojo and Yaga: `--only talk`). It prints the cost and
   writes `<who>_fx.json`.
3. **You** drag the file onto the ComfyUI window. The box called "Load Image:
   the close-up" should show `<who>_fx_in.png`, the head on bright green. If
   it shows an error, pick that file by hand.
4. **You** press **Run**. Two rows, one picture each: **BLINK** on top,
   **TALK** under it. About $0.32. There is no second version of these.
5. **You** look for: both eyes closed, each a soft curved line (blink); the
   mouth a little open, as if halfway through a word (talk); and in both, the
   head in the same place and the same size as in the close-up. A head that
   has moved or been redrawn is the thing to reject. A slightly different
   collar doesn't matter: the game uses only a small box around the eyes and
   one around the mouth.
6. **You** tell Claude "<who>'s blink and talk are done". If one looks wrong,
   say which; a redo of one is $0.16.
7. **Claude** runs `python3 tools/install_face.py <the picture> <who> blink`
   and `... <who> talk`. The tool lines the answer up with the sprite, copies
   only the eye box or the mouth box onto a copy of the neutral sprite, prints
   how well the box's rim meets the sprite, and writes
   `game/images/char/fx/fx_<who>_blink.png` / `fx_<who>_talk.png` and a
   preview in `shots/art/`.
8. **Claude** checks which of that person's other faces the blink also sits
   on without a seam (Yuji's does on four of his five others) and adds the
   row; the mouth stays on the neutral face only.
9. **You** talk to that person in the game and watch.

`python3 tools/install_face.py --sheet` draws every eye and mouth box on its
sprite, to look at before anything is paid for.

---

## Foreground layers (free)

A foreground is a piece of the room's own picture (a table edge, a desk) that
people stand behind. It is cut from the background by a polygon, so it costs
nothing and can never drift from the picture.

Five exist, in three rooms: `fg_dorm_common.png`, `fg_dorm_common_evening.png`,
`fg_dorm_common_night.png`, `fg_cafeteria.png`, `fg_utahime_office.png`. The
classroom has none; people there stand in the front aisle.

**The one rule to remember:** every new painted time version of the common
room, the cafeteria or Utahime's office (an evening cafeteria, say) **needs
its own foreground file**, `fg_<place>_<variant>.png`. Until it exists, that
room at that hour falls back to plain standing places and draws no
foreground, so people stand in front of the table.

### Steps (all Claude's; you only look at the result)

1. Add the polygon to `tools/fg/<place>.json`, one per picture: `""` for the
   day picture, `"evening"` or `"night"` for the others. Trace the object a
   pixel or two inside its outline.
2. Look at it first: `python3 tools/layout_sheet.py view_<place>`.
3. Cut it: `python3 tools/make_fg.py <place>` (or `<place> evening`; `--dry`
   for the preview only). It writes `game/images/fg/fg_<place>[_<variant>].png`
   and a preview in `shots/art/`.
4. For a room that has no foreground yet (the classroom, if you want someone
   back behind a desk): also a far standing place in `VIEW_SLOTS` and the
   room's name in `VIEW_FG_ROOMS` (`game/view_stage.rpy`). An object's icon
   that sits on a foreground object must be registered "in front".
5. You see it in the game.

---

## Other pictures that could be made one day

None of these is planned or priced into the figures above.

- **Tokyo's districts** (Shibuya, Harajuku, Shinjuku, Kawasaki, Yotsuka) are
  still tinted stand-ins. A night picture for a district, defined under the
  name `bg <district> night` (`bg shibuya night`), would show behind the
  night out by itself. They belong with the districts' own scenes (phase 4).
- **The alley and the ridge veil** are tinted stand-ins from phase 1.
- **A vending machine in the courtyard picture.** Its icon sits on the
  right-hand porch today.
- **More evening and night versions of rooms.** Each is a relight of the
  approved picture (`tools/make_relight_workflow.py`). Remember the
  foreground rule above, and that a pose painted on the day picture is not
  shown on the new version.

## Where things live

| what | file in `game/` | tool |
|---|---|---|
| icons | `images/icons/ic_<name>.png` (96×96) | `tools/make_icon_workflow.py`, `tools/cut_icons.py` |
| area maps, rooms, yards | `images/bg/<name>.png` | `tools/make_bg_workflow.py`, `tools/install_bg.py` |
| poses | `images/place/pose_<place>__<who>[__<variant>].png` and its box in `layout/view_<place>.json` | `tools/make_pose_workflow.py`, `tools/install_pose.py` |
| blink and talk | `images/char/fx/fx_<who>_blink.png`, `fx_<who>_talk.png` | `tools/install_face.py`, `tools/make_edit_workflow.py` |
| foregrounds | `images/fg/fg_<place>[_<variant>].png` (polygons in `tools/fg/<place>.json`) | `tools/make_fg.py` |
| the four GUI pictures | `gui/grade_sheen.png`, `hot_ring.png`, `soft_box.png`, `card_back.png` | `tools/gen_gui.py` |
| where things sit on a picture | `layout/area_<key>.json`, `view_<place>.json`, `hot_<place>.json` | `tools/layout_sheet.py` draws them for approval |

Each tool's own first lines give its exact usage; `tools/README.md` lists them
all.
