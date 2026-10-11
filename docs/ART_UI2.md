# The pictures of the second UI overhaul: how a sitting goes

*Jujutsu Kaisen: Cursed Bonds · written by U0d3, 11 Oct 2026. This is the
owner's page for sections 5.4, 5.6, 5.11 and 5.13 of `docs/UI2_DESIGN.md`.
Phase 2's page, `docs/ART_PHASE2.md`, still holds for what it describes; this
one is about the new backgrounds, their evenings and nights, and the four new
people. Where this page and your own words in `docs/UI_OVERHAUL_2.md`
differ, your words win.*

**Nothing in the game waits for a picture.** Until a picture is installed
the game shows what it shows today, or a clearly marked stand-in for a new
place.

## A sitting, step by step

A sitting is one small batch of pictures: twelve or fewer, about $0.16 each.

1. **Claude writes the file.** A drag-in workflow, `art_<n>.json`, in
   `~/Desktop/JJK Game images/ui2/` (the ones run so far are in its `early`
   folder). The reference pictures and the prompts are already in it. Claude
   tells you its name, how many pictures it paints and what they cost.
2. **You drag it into the local ComfyUI and press Run, once.** You save
   nothing and move nothing: the results land in ComfyUI's output folder. If
   it stops with a rate-limit or "high demand" error, wait a minute and press
   Run again straight away: a picture that already finished is not paid for
   twice. (That holds only until another file is run. ComfyUI remembers the
   last file's results and no others, so a file run again later is painted
   and paid for again.)
3. **You say the renders are in.** Claude looks at every one, runs the check
   on it (below), and shows you a sheet for each picture: version A beside
   version B, with what the check said and which one it would pick, and why.
4. **You choose.** "A", "B", one letter per picture in order, or "go with
   your picks". If you want something different ("turn the main light off",
   "there are doors that lead to nothing"), say it in your own words: that
   picture is written again and run once more, and what you said becomes a
   rule for the pictures after it.
5. **Claude installs what you chose,** and you look at it **in the game**,
   after relaunching, not only in ComfyUI.
   - A room painted again where it stands (the same camera, the same things):
     about ten minutes.
   - A yard, the gate, a map or a new place: its layout is done first (where
     each door and thing to click is, where people stand), about fifty
     minutes a picture, so it may show in the game a day later.

## What has really happened so far

Many sittings were run early, while the tools were still being built: one
file at a time, you pressing Run and then saying the renders were in, and
choosing from the sheets. That is how the yards, the dormitory rooms, the
school's rooms, the training rooms, the offices, and most evenings and nights
were chosen. Your choices are written down as you made them (the plan's
section 1.1), and the pictures you chose are kept in
`~/Desktop/JJK Game images/ui2/early/chosen/`.

**None of them is in the game yet.** They go in after you have played
checkpoint A, starting with **batch 0**, which has nothing to run: the four
pictures from the look test (the Courtyard, the Library, the Common Room, the
Cafeteria). The Courtyard and the Library are then the first two places
where **the picture itself is what you click**: hover the training hall and
it lights. You judge that, and how strong the light is, on those two before
the other places are traced.

## Every picture comes as two versions

Each background, evening, night, map and pose is painted twice, **version A
and version B**, and you choose. If neither is right, the pair is run once
more. (The exceptions are a person's extra faces, blink and talking mouth:
one picture each, because they are laid over a sprite that is already
chosen.)

## The three words the check uses

Before you are asked to choose, a tool measures each render against the
picture in the game. You are never asked to check by eye that nothing moved.

| word | what it means | what you do |
|---|---|---|
| **PASS** | It can go in. | Choose it or the other version. |
| **LOOK** | It can go in, and here is what changed, in plain words ("the view through the window is drawn differently", "the floor is drawn again"). A picture with a new window view, or with something added on purpose, always comes back as a LOOK. | Look at what is named, then choose it or not. |
| **REFUSED** | Something moved, vanished or appeared, and it says what ("the floor cushions by the low table are gone"). It cannot be chosen. | Nothing, unless both versions are refused: then the pair is run once more. |

Two things the check cannot do, so Claude does them by eye and says so on
the sheet: an evening or night picture is looked at beside its day picture
for anything added (a lamp, a blanket), and a brand-new view (a yard, a new
room) is read for whether it agrees with the pictures already chosen.

## Which sittings have more than one file

By the plan there are forty-seven sittings. Eleven are one file. The others:

- **Two files with a pause (eighteen sittings: 3, 4, 6 to 13, 15 to 19, 21,
  24, 28).** Run the first file and choose. The second is made *from* what
  you chose (a room's evening and night from its new day picture), so it can
  only be written afterwards. For a new place the second file can wait for
  another day.
- **Two files, no pause (twelve sittings: 14, 23, 25, 27, 32, 33, 41, 42,
  43, 45, 46, 47).** Up to twelve renders, split in two only so that no
  single run is over ten. Run one, then the other.
- **Five short files (sittings 35 and 36).** Blink and talking mouth, one
  file per person.
- **The four people (sittings 37 to 40):** see below.

The early sittings did not always follow these numbers: some were split
further or run in another order, and each file was simply named when it was
ready (`art_15r.json`, `art_14p.json`). Going by the file Claude names is
always right.

## The four people: Dad, Mom, Kurose, Nade

These four sittings are a different kind, the way Sana was made:

1. A **base picture** of the person, made on **Comfy Cloud** (your plan needs
   to be active then). You choose between versions.
2. **Two or three short repair runs** in your own local ComfyUI (small
   fixes to the figure), choosing between versions after each.
3. Claude cuts the figure out and sets its height, and you look at the
   person in the game.

About $1.00 to $1.50 a person. Dad is first, as the test of the route: allow
an evening for him, less for the other three. Each has one face for now.

## What it costs

$0.16 a render (Nano Banana Pro at 2K), so a pair is $0.32 and a full sitting
of twelve is $1.92. Nothing runs on this Mac's graphics card. You can check
your credit balance before pressing Run: your account picture at the top
right of ComfyUI, or Settings, then Credits.

## Where things are

| what | where |
|---|---|
| the files you drag in | `~/Desktop/JJK Game images/ui2/` (so far: its `early` folder) |
| what ComfyUI paints | `~/ComfyUI-Shared/output/` |
| the sheets you choose from | `~/Desktop/JJK Game images/ui2/early/compare_*.jpg`, and shown in chat |
| the pictures you chose | `~/Desktop/JJK Game images/ui2/early/chosen/`; once installed, a copy of each render in `ui2/approved/` |
| what you said and what was chosen | `docs/UI2_DESIGN.md`, section 1.1 |
