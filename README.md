# Jujutsu Kaisen: Cursed Bonds

An unofficial, non-commercial fan game built in **Ren'Py**. A linear prologue
hands off to an **open campus sandbox**: a clock, a map, characters who are
somewhere specific at every hour, and relationships you build by choosing where
to spend your time.

Jujutsu Kaisen is created by Gege Akutami. This is a fan work.

> **Version 0.3, Arc One, phase 1.** Phase 1 laid the Arc One foundation:
> first-person narration, grades, missions, Utahime's board, items, memories,
> Tokyo trips and a new HUD, map and journal. The plan and every decision are in
> `docs/PHASE1_DESIGN.md` (storyboard: https://claude.ai/artifact/V6qPxrGmSUQDUn5twNWsbr);
> the owner's review checklist is `docs/PLAYTEST.md`. Phase 2 is the UI
> overhaul (`docs/PHASE2_UI_OVERHAUL.md`), phase 3 combat, phase 4+ the story.

```bash
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md      # run
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md lint # check
```

The test and review tools (harnesses, the save regression, content checks) are
described in `tools/README.md`.

---

## Shape of the game

**Prologue** (linear, ~30 min) — the diner, the alley behind the arcade, Sana,
the lights going out, Last Light waking, Gojo's offer, and the tour of Jujutsu
High that ends at the veil on the ridge. It is told in the first person: Kaito
narrates as "I" and never appears on screen. Then the campus opens and never
closes again.

**Arc One: Tokyo Jujutsu High** (sandbox) — five acts, and **no deadline**.
Story beats come in order and wait for you; the NEXT banner and the journal
say what comes next and where. Eighteen places in six areas, eleven people on
real schedules, a board of graded jobs, and Tokyo by car once Ijichi trusts you.

| Act | Title | Grade band | Written in phase 1 |
|---|---|---|---|
| I | Grade Four | Grade 4 | roll call, Utahime's arrival, the Sun Mall, the morning after, Kurose |
| II | The Ones Who Stay | Grade 4 → 3 | the second-years, the courtyard curse, Oda's letter, Gojo's first lesson, the Grade 3 promotion fight |
| III | Overtime | Grade 3 → 2 | the Nade missions, Kurose's leak, Oda's reply |
| IV | Goodwill | Grade 2 | the roster, the night before Kyoto |
| V | Cursed Womb | Grade 2 → Grade 1 candidate | (later) |

Every storyboard beat not yet written has a row that reads "Coming in a later
build"; unwritten rows never block written ones. The storyboard's order lives
in `sb_missions.rpy`, not in the chapter files.

### Threads — `sb_threads.rpy`

Eight storylines, one per character, each 3–4 stages, shown in the **Journal**
with what you've learned so far. Events declare the stage they represent and the
engine advances it — scenes carry no bookkeeping:

```python
ev("ev_yuji_2", who="yuji", min_bond=35, thread=("yuji_countdown", 2))
```

Prologue choices seed the journal, so who you talked to on day one is already on
the board when the campus opens. Character missions are gated on threads.

---

## Systems

### Writing rules
New or edited text is first person: Kaito narrates in "I", present tense;
everyone else says "you", `[mc_name]` or `[mc_surname]`, never a literal
"Kaito" or "Amagiri". Kaito is never shown on screen; everyone faces the
camera. Expressions (neutral / happy / serious / angry / surprised / sad) work
only on the 13 characters with an image tag: mc, yuji, megumi, nobara, maki,
panda, toge, gojo, yaga, ijichi, shoko, utahime, sana. The Sun Mall and the
chapters after it, and the character scenes (hangouts, which can come up from
day 1), still say "you" until phase 4 converts them (design 5.4, D9).
`tools/check_content.py` checks all of this.

### Hooks, migrations and saves — `sb_hooks.rpy`
The shared plumbing. `register_new_day`, `register_event_gate`,
`register_event_done`, `register_place_action`, `register_migration` and
`register_validator` let each system plug in without editing the loop.
Migrations run on every load (they are idempotent), so old saves keep loading:
they convert old values (the old techniques become Last Light, an old grade
number becomes a grade key), backfill merit and memories, and hand out
keepsakes. A save whose statement no longer exists lands in `load_recover`,
which picks up on campus or at the right prologue step. `toast()` is the one
way to show a notification. The rules that keep saves loading are in design
section 2.1: never delete a label, never rename a store variable, new state is
`default`, and a few statements must stay textually identical.

### The clock — `sb_world.rpy`
Day counter, weekday, and five periods: **Morning / Noon / Afternoon / Evening /
Night**. Most actions cost one period. Sleeping rolls the day, restores stamina,
reserve and health, and clears the once-a-day actions (`actions_today`: Hold the
hour, Get patched up, Look through the racks, the veil, Gojo's lesson). New-day
hooks then run: NPC growth, Gojo's in-day, the board's weekly offers, keepsakes.

### Places, areas and schedules — `sb_world.rpy`, `ui_map.rpy`
`LOCATIONS` holds eighteen places, including Utahime's office (open once she
arrives) and Gojo's office (locked, "SOON!", until his first lesson). The map
draws them grouped into six `AREAS` (Courtyard & Gate, Classrooms,
Dormitories, Staff Building, Training Grounds, The Mountain), each row showing
who is there now and which missions wait there, plus a Find someone strip.

`SCHEDULE` gives every character a place per period; `WEEKEND` overrides it on
Sat/Sun. Gojo roams (`GOJO_SPOTS`), and after his first lesson he keeps office
hours about one day in six (never two days running, never more than eight days
without). `FLAG_SCHEDULES` lets a story flag replace someone's whole routine.
`pin(who, loc)` forces someone somewhere for a story beat, and wins over
everything. `usual_places(who)` and `when_at(who, loc)` put a schedule in words.

On the ridge, once the tour has shown it, *Look up at the veil* is a free,
once-a-day action with three rotating passages.

### Tokyo — `sb_tokyo.rpy`
After Ijichi's ride-along (flag `ijichi_rides`) the map gets a Tokyo tab.
Ijichi drives from the gate, mornings to afternoons. A trip to Shibuya,
Harajuku, Shinjuku (Grade 2), Kawasaki (Act III) or home to Yotsuka takes half
a day: a short first-person arrival, then back at the gate. The districts' own
scenes (`label district_<key>`) come in phase 4; a trip plays one when it exists.

### Grades and merit — `sb_grades.rpy`
The ladder is Grade 4, Grade 3, Grade 2, Semi-Grade 1, Grade 1 and Special
Grade (keys `g4`…`sp`). You have no grade until roll call assesses you as
Grade 4. Your grade caps Control, Output and your reserve, sets how many
talismans you can wear, which board jobs you can take and what the armory
releases. Merit (from the story, missions and the board) opens each
promotion: Grade 3 at 60 merit and a fight in the training hall with Maki
watching. Everyone else has a grade too (`NPC_BASE`), grows every day, grows
faster when you train together (`train_together`), and is promoted on their
own, with a toast and a remark next time you talk.

### Cursed energy and Last Light — `sb_energy.rpy`
Four numbers: **Reserve** (`ce`/`ce_max`, spent by the technique), **Control**
(Last Light scales with it), **Output** (raw force) and **Insight** (reading
energy, rooms and people). Gains have diminishing returns past 60 and 85, and
stop at your grade's cap (a promotion lifts it; nothing is ever lowered).

There is one technique, **Last Light (残光, Zankō)**: holding the instant the
lights went out. Its sandbox verb is *Hold the hour* (once a day, costs
reserve: the hour doesn't pass). Four tiers by Control (0 / 30 / 60 / 90):
Stutter, Held Second, Arrest, and The Second That Did Not Happen, a Domain
Expansion reachable only at Grade 1. The internal key stays `"timestop"`.

### Missions and the objective — `sb_missions.rpy`, `missions_stubs.rpy`
One registry holds every beat: the main story (acts I–V), promotions and
character missions (up to three per person, `cm_<who>_<n>`). A mission's
status is worked out from the save each time (done, waiting, available,
locked, "Written in a later build"…). *Auto* missions are story events that
find you wherever you are; *start* missions are gold buttons on a person or a
place. Rewards (merit, bond, yen, items, flags) are paid once, when the
mission completes. `objective_text()` is the one-line NEXT goal the banner and
the journal show. Two character missions are playable in phase 1: Ijichi's
*Ride-Along* and Maki's *The Armory*. Arc Two can be begun from the journal
once the whole main story is done (not reachable in normal play yet).

### Utahime's board — `sb_board.rpy`
From Utahime's arrival, her office has a board of graded jobs, three a week
(new ones on Mondays): two at or below your grade and one a grade up that
needs a senior partner. You always take someone. A job costs 2 periods and 25
stamina (only 1 when a story beat is waiting at the office, so it is never
skipped) and isn't offered after dark. In phase 1 it plays out on its own from
its parts (a case, a place, a curse, a twist and your partner's lines) and pays
merit, yen, bond and sometimes a talisman or a tool. About one Grade 4 or 3 job
in six is misgraded: the curse inside is heavier than the card said.

### Items, equipment and the armory — `sb_items.rpy`
`ITEMS` holds keepsakes (the thing you packed), mission items (what the Nade
business leaves in your drawer), sealing talismans, supplies, cursed tools and
worn talismans. `sync_keepsakes()` hands out anything a story flag has earned.
You hold one tool and wear talismans in the slots your grade allows. Maki's
*The Armory* opens the storehouse racks, which release tools up to your grade.
Tool and talisman effects (`fx`) are stored now and switch on in phase 3.

### Memories — `sb_memories.rpy`
The journal's Memories tab replays any scene this save has seen: the prologue
steps, the story, every hangout and activity scene, and Sana's flashbacks
(written in phase 4, unlocked by a trip home, her daisy clip, and Oda's
letter). Whether a memory is seen is read from the save, never from the
machine. A replay runs in its own copy of the store, so nothing in it reaches
the save.

### The HUD, toasts, place view and person view — `ui_hud.rpy`, `sb_screens.rpy`, `sb_activities.rpy`
Walking around shows only the date and three buttons (MAP, JOURNAL, MENU).
Rewards stack as toasts at the top right, merging repeated bond gains
("Yuji bond +4"). A NEXT banner slides in when the objective changes, and a
caption names the place and hour on arrival. Each place shows up to four people
with what they are doing (`AMBIENT`); clicking one brings them closer with two
to four sensible choices (`person_choices`), and they stay on screen while you
talk. When run from the SDK a small *Review tools* button sits at the bottom
left.

### The journal — `ui_journal.rpy`
Six tabs: People, Missions (Story / Character / Board), Memories, Stats (your
grade, merit, stats and Last Light), Equipment and Inventory. Equipment can only
be changed when the journal is opened on campus (from the place view).

### Review tools — `explore.rpy`
A developer-only panel (only when run from the SDK), reached from the place
view: add merit, promote you or a first-year, finish the next story step, raise
every bond, open Tokyo, make Gojo in, recruit Utahime, grant every item, open
the armory, mark the main story complete, jump a week, and look at the ridge
veil again today. Explore mode (on the
main menu, also developer-only) is a free roam with every door open and no
story.

### Lighting — `sb_world.rpy`, `lighting.rpy`
One authored image per place, tinted at runtime so a room reads as the hour
you're standing in it. `graded_bg()` picks a tint + brightness from
`OUTDOOR_GRADE` / `INDOOR_GRADE` (interiors get a gentler curve — a lit corridor
at midnight is not a blue field) and caches one displayable per
`(place, period)` outside the store, so screens don't churn and saves stay small.

Places in `TIME_VARIANT` have a genuinely different evening or night image
rather than a tint, relit from the day picture so it is recognisably the same
place (your room's window shows a mountain by day and a moon by night; the
rooftop gets a sunset). Those are served ungraded so they aren't crushed twice.

The characters are lit to match, in `game/lighting.rpy`. Whenever a background
goes up, the scene's light is set from the place and hour (or, for story
scenes, from the background's name), and every sprite is wrapped in
`lit_sprite()`, which tints it by that light and puts a soft contact shadow
under its feet. The tables are `OUTDOOR_LIGHT`, `INDOOR_LIGHT`, `PLACE_LIGHT`
and `BG_LIGHT`.

### Bonds and romance — `sb_relations.rpy`
Two tracks. **Bond** for everyone. **Affection** for the romanceable cast
(Nobara, Maki, Shoko), and affection is *hard-capped by bond*:

```
bond  0 → affection cap   0        bond 50 → cap  40
bond 30 → affection cap  20        bond 70 → cap  70
                                   bond 85 → cap 100
```

So romance can't be ground out ahead of friendship — the UI tells you plainly
when you've hit the ceiling. Romance content is written PG-13.

### The friendship track — `sb_activities.rpy`
Tops out at **bond 80** with *"They asked you for something"*, gated behind
having already told them something true at 65. Every other scene in the game
has the player needing something; this one reverses it, once per character.
Yuji asks you to be the one who tells the others. Megumi asks you to come and
sit with Tsumiki. Shoko asks you to be her emergency contact, a line that has
been blank for eleven years. Nine unique scenes, several with choices.

### Affection, and the ceiling — `sb_relations.rpy`
Bond gates affection up to **100**. At 100 there is nowhere left for it to go,
and one activity appears: **Say it**. That scene is written per character, and
playing it calls `begin_together()`, which lifts the ceiling to **200** and
opens four tiers of quieter, more intimate activities above it — staying the
night, waking up together, a whole day off, and talking about after. Ranks
past 100 are Certain / Devoted / Inseparable / Unconditional.

Everything above the confession is *hidden* until it happens, rather than shown
as a lock, so the ceiling is a surprise rather than a checklist.

### Combat — `sb_combat.rpy`
Turn-based, and the loop is **read the enemy, then answer it**. Each round the
curse telegraphs ("It is behind you. It was not behind you."); each telegraph has
one correct answer (Brace / Step aside / Break the grip / Close the distance).

Answering correctly defends *and* staggers, but deals little damage. Using a
technique deals real damage but leaves the telegraph unanswered, so it lands.
That trade is the whole fight. A wrong answer is punished at 1.5x.

`Insight >= 45` reads telegraphs for free; below that you spend a turn on
"Read it", or fight blind. Simulated at 200 trials per matchup: reading tells
takes a fight from **47% to 100%**, and a grade 2 kills an under-levelled
first-year **~97%** of the time.

Enemies live in `ENEMIES` (with grade keys), moves in `MOVES` (Last Light's
three, unlocked by tier). `call combat("key", ally, flee_ok, bg)` returns
"win" / "down" / "fled". The alley fight ends after four exchanges. Combat is
reworked in phase 3.

### The road home — `story_oda.rpy`
Every sandbox location is on the mountain, Sana is dead and the parents are
edited, so after Chapter 2 the outside world is closed. Oda-sensei is the one
line still running off it: not family, so the veil never took — it is filed on
households. She writes to a school whose name the player's own mother cannot
hold in her head, having worked out on her own that something is wrong.

Two beats. The letter, and whether to answer it honestly, carefully, or at
all. Then (only if answered): she has counted nine short-notice transfers in
four years, three of them dead inside eighteen months, and the countersigned
notice she encloses carries the signature Kurose leaked. She is the
counterweight to him — he files, she notices — and answering her turns a
civilian into an asset days after being told what that costs.

### Antagonists
See `docs/ANTAGONISTS.md`. One through-line villain — **Sadao Wakuri, "the
Cartographer"**, a Grading Office assessor who files curses one grade low near
students he has chosen, because sorcerers who nearly die young get stronger —
with an arc-level antagonist in front of him each time. Arc 1 is **Ryōsuke
Nade**, the man who signed the Sun Mall as a grade 3; he is not a mastermind,
he is complicit, which is worse. `missions_arc1.rpy` runs that thread across
three office missions ending on a map with the player's home town circled,
dated four years before the alley. The board's misgraded jobs are his hand.

### Planned: binding vows
Not built yet. The canon mechanic — trade a restriction for power — is a good
fit for the *combat* progression rather than the relationship one, e.g. a vow
with Maki that raises Output as long as you train with her every week, and
lapses if you don't. Deliberately kept separate from affection so romance stays
a side system with no stat pressure attached to it.

### Events — `sb_events.rpy`
Content is data. `ev()` registers a label with conditions; the engine picks the
most advanced unlocked event and fires it. Scenes never test conditions themselves.

```python
ev("ev_maki_2",   who="maki", min_bond=35)
ev("ev_maki_r1",  who="maki", min_bond=50, min_aff=20)
ev("ev_night_x",  who="nobara", loc="rooftop", periods=["Night"], weekend=True)
```

Kinds: `story` (auto-fires wherever you are, but only while its mission is
available: the mission registry decides the order, not the day) and `hangout`
(a bond scene behind "Spend time together"). A gold 「!」 or NEW chip on a
person means they have a mission or a new scene.

---

## Adding content

After any change: run lint (the validators print `VALIDATE:` lines for broken
references), `python3 tools/check_content.py <your files>`, and the harness of
the system you touched (`tools/README.md`). Registries are init-time data and
are never saved, so adding to one never breaks an old save; never rename or
delete an id, a label or a store variable that already exists.

**A scene (hangout):** write `label ev_thing:` in `events_arc1.rpy`, add one
`ev(...)` line to the init block at the top. That's the whole wiring. Give it a
memory tile too (below).

**A mission** (`sb_missions.rpy`): add one `mission(...)` call in its act's
section of the main-story table, before the lookups at the end of the init
block (they are built once, there):

```python
mission("m_cinema", "story", "III", 340, "The Cinema",
        "Kawasaki, a film, and a boy called Junpei.",   # summary (journal)
        "Something is wrong at a cinema in Kawasaki",   # objective (NEXT line)
        label="st_cinema", periods=("Afternoon",), gate=dict(gap_days=1),
        done_if=("event:st_cinema", "flag:cinema_done"), rewards=dict(merit=10))
```

- The id and `order` must be unique (orders are spaced by 10, so insert
  between). An unwritten beat already has a row with a reserved id: give it a
  `label=` instead of adding a new row.
- `trigger="auto"` (the default) is a story event that finds you: also register
  it with `ev("st_cinema", kind="story", periods=[...])` in the chapter file's
  init block, or it never fires (the validator requires every story `ev()` to
  be bound to a mission). `trigger="start"` is a gold button: set `where` and
  `with_who` (the giver who must be present) instead, and no `ev()`.
- `gate` keys: `after`, `gap_days`, `flags`, `not_flags`, `min_bond`,
  `min_grade`, `merit`, `thread`, `gojo_in`, `act_done`. `done_if` / `skip_if`
  clauses: `event:<label>`, `flag:<f>`, `grade:<key>`, `mission:<id>`. Old saves
  count as done through `done_if`, so list the flags the scene sets.
- Rewards are paid by the mission when it completes, never in the scene. A
  start mission's scene can call `mission_fail(mid)` to be retried tomorrow.
- A character mission's row already exists (`_CM_TABLE`, ids `cm_<who>_<n>`):
  writing `label cm_<who>_<n>:` is enough to make it playable. Per-mission
  extras (place, cost, rewards) go in `_CM_EXTRA`.
- Mark new scenes `## PLACEHOLDER — rewrite in phase 4` until they are final.

**A memory** (`sb_memories.rpy`): one line in the catalogue. A story scene:

```python
_mem_story("st_cinema", "The Cinema", "III", ("yuji",), "bg city",
           "Something is wrong at a cinema in Kawasaki.", flags=("cinema_done",))
```

`_mem(id, title, act, label, who=(), args=(), seen=[rules], hint, unlock,
bg, place, stage)` is the general form. `seen` rules: `("label", l)`,
`("event", l)`, `("flag", f)`, `("act", "aid:who")`, `("together", who)`; any
one will do. A scene played for a person (`act_*`, hangouts) takes
`args=(who,)`. `place=(loc, period)` makes a replay stand somewhere first, for
scenes that draw the place they are played in. The tile's `hint` is shown
while unseen. The validator checks the label, the people, the act, the rules
and the picture.

**An item** (`sb_items.rpy`): one `_item(...)` line.

```python
_item("iron_seal", "Iron Seal", "talisman", grade="g3",
      desc="...", effect="Hits harder, guards worse.",
      fx={"strike": 0.15, "guard": -0.15}, source="Utahime's board.")
```

Kinds: `keepsake`, `sealing`, `supply`, `mission`, `tool`, `talisman`. A
keepsake or mission item earned by a story flag takes `from_flag="<flag>"`, and
`sync_keepsakes()` hands it out once. Otherwise give it with a mission's
`rewards=dict(items={"id": 1})` or `give_item("id")`. Tools on the storehouse
racks are listed in `ARMORY_RACK`. Board drops are `BOARD_TALISMAN_DROPS` /
`BOARD_TOOL_DROPS` (`sb_board.rpy`); add a new drop to `BOARD_DROP_ITEMS` too,
which the validator checks against `ITEMS`. `fx` numbers are stored only, until
phase 3.

**A district** (`sb_tokyo.rpy`): an entry in `DISTRICTS` (name, kanji, desc,
places, bg, `min_grade` / `needs_flag` and the `locked_hint` that names them,
and 2–3 first-person arrival `lines`), its key in `DISTRICT_ORDER`, a
background (`bg_placeholders.rpy`, with a `BG_LIGHT` row in `lighting.rpy`), and
a card position in `DISTRICT_POS` (`ui_map.rpy`). A scene of its own is
`label district_<key>:`; the trip plays it after the arrival lines.

**A board part** (`sb_board.rpy`): edit `BOARD_CASES`, `BOARD_PLACES` (each with
a narration phrase, a short card title and a `bg`), `BOARD_CURSES` (per grade;
the validator wants at least 2 each), `BOARD_TWISTS` plus its line in
`BOARD_TWIST_LINES`, and `PARTNER_LINES` (arrive / win / hurt, each a
narration line, an expression and their spoken line). When a part fits only
some places or cases, add fit entries: `BOARD_CASE_FITS` (case → places),
`BOARD_CURSE_FITS` (curse → places), `BOARD_CURSE_CASE` (curse → cases). A part
not listed there fits everywhere. The validator flags any rostered non-staff
student without `PARTNER_LINES`. Numbers (difficulty, merit, yen, drops) are
tables at the top of the file.

**An ambient line** (`sb_screens.rpy`): what someone is doing in a place, shown
under their nameplate, and the face they wear there.

```python
("maki", "dojo"):  ("drilling with a staff", "serious"),   # in AMBIENT
("maki", None):    ("a staff over one shoulder", "serious"),  # anywhere else
```

A caption that names someone else goes in `AMBIENT_NEEDS` too, with the
caption to use while that person isn't there. The expression is one of the six,
and the person must be one of the 13 tagged characters. The validator checks
the people and places.

**A schedule by flag** (`sb_world.rpy`, `FLAG_SCHEDULES`): while a flag is set,
a table replaces someone's whole routine.

```python
init python:
    FLAG_SCHEDULES.append(("yuji_presumed_dead", "yuji", None))    # off campus
    FLAG_SCHEDULES.append(("maki_hurt", "maki",                     # (a made-up flag)
                           {"Morning": "infirmary", "Noon": "infirmary",
                            "Afternoon": "infirmary", "Evening": "girls_dorm",
                            "Night": "girls_dorm"}))
```

Each entry is `(flag, who, table_or_None)`. The table (`{period: place}`)
replaces the weekend schedule too, and any period it leaves out is off campus;
`None` means off campus all day. The last matching entry wins. Story pins
(`pin`) still win over it. The map, the People tab and `usual_places` follow
it (runs of three periods read "X to Y": "mornings to afternoons"). The entries
can live in any file's `init python` block (sb_world's own block runs at
init -2, before it); the validator checks the places.

**A location:** add to `LOCATIONS` and `LOC_ORDER` in `sb_world.rpy`
(including `indoor=`), and put its key in one `AREAS` entry's `places`: the map
draws from `AREAS`. Add its access rule to `can_enter` if it needs one, an
`image bg …` line in `jjk_defs.rpy`, and a light row. The `x`/`y` in
`LOCATIONS` and `NODES` in `tools/genworld.py` matter only if you redraw
`map_campus.png` (`--force`). For the picture, write
`tools/bgs/prompts/<name>.txt`, build the workflow with
`tools/make_bg_workflow.py <name>`, run it in ComfyUI and put the pick in with
`tools/install_bg.py`. An evening or night version comes from
`tools/make_relight_workflow.py`, plus a `TIME_VARIANT` entry and a light row.

**A character:** add to `CAST` and `ROSTER_ORDER` in `sb_relations.rpy`, a row to
`SCHEDULE`, a `Character` (with `image="<tag>"` for side portraits and
expressions) in `jjk_defs.rpy` and an entry in `CHARS`; then `NPC_BASE`
(`sb_grades.rpy`), `JOURNAL_CAST` (`sb_missions.rpy`), `AMBIENT` and
`PERSON_GREET_EXPR` (`sb_screens.rpy`). Sprites follow
`docs/ASSET_PIPELINE.md`: the base render is repaired and keyed with
`tools/fix_edges.py` and `tools/keysprite.py`, the expressions are added, and
`tools/gen_sprite_defs.py` writes the images into `jjk_sprites.rpy`.

**An action:** `register_place_action(id, label, hint, cost=0, locs=(...),
when="<name of a store function returning bool>")` in an init block, and a
matching `label sb_do_<id>:` that does the work and charges the time. The
built-in actions are in `place_actions()` (`sb_screens.rpy`) and `sb_loop.rpy`.

---

## Files

| File | What |
|---|---|
| `script.rpy` | Entry point, prologue → sandbox handoff (`arc_one_open`) |
| `ch1_alley.rpy` `ch1b_the_offer.rpy` `ch2_tour.rpy` | Prologue, in first person, split into steps (`ch1_diner` … `ch2_first_years`) |
| `ch4_mission.rpy` `ch5_debrief.rpy` | The Sun Mall (started from Yaga's office) and its debrief |
| `jjk_defs.rpy` | Characters (with image tags), backgrounds, placeholder images, transforms, `CHARS` |
| `jjk_sprites.rpy` | Sprite and side-portrait images, generated by `tools/gen_sprite_defs.py` (don't hand-edit) |
| `jjk_screens.rpy` | Shared screen pieces: panel, section head, meter, chapter card |
| `bg_placeholders.rpy` | Stand-in backgrounds for the alley, the ridge veil, the offices and Tokyo; real files drop in by name |
| `lighting.rpy` | Scene light, `lit_sprite()`, contact shadows |
| `explore.rpy` | Explore mode and the review tools (developer builds only) |
| `sb_hooks.rpy` | Hooks, migrations, load recovery, `toast()`, validators |
| `sb_world.rpy` | Clock, places, areas, schedules, flag schedules, Gojo's in-days, access rules, the ridge veil |
| `sb_tokyo.rpy` | Tokyo districts and trips in Ijichi's car |
| `sb_energy.rpy` | Reserve/Control/Output/Insight, Last Light and its tiers |
| `sb_grades.rpy` | Grades, merit, caps, NPC stats and growth, promotions, the grade card |
| `sb_relations.rpy` | Cast, bonds, affection, roster |
| `sb_activities.rpy` | Activities per person, what unlocks them, `person_choices`, Gojo's lesson |
| `sb_combat.rpy` | Turn-based combat, `ENEMIES`, `MOVES` |
| `sb_events.rpy` | Event registry, dispatcher, small talk |
| `sb_missions.rpy` | Mission registry: story chain, promotions, character missions, the objective, Arc Two |
| `missions_stubs.rpy` | The new placeholder scenes: Utahime's arrival, the Grade 3 fight, Ride-Along, The Armory |
| `sb_board.rpy` | Utahime's board of graded jobs |
| `sb_items.rpy` | Items, equipment, keepsakes, the armory |
| `sb_memories.rpy` | Memories catalogue and replay |
| `ui_hud.rpy` | HUD, toasts, the NEXT banner |
| `ui_map.rpy` | The campus and Tokyo map |
| `ui_journal.rpy` | The six-tab journal |
| `sb_screens.rpy` | Place view, person view, `AMBIENT`, staging |
| `sb_loop.rpy` | Main loop and every built-in action |
| `sb_threads.rpy` | Per-character storylines and the journal data |
| `screens.rpy` | Ren'Py's engine screens: say (with side portraits), quick menu, preferences |
| `story_arc1.rpy` | Arc One story beats (roll call to the night before) |
| `story_kurose.rpy` | The paperwork thread (Kurose) |
| `story_oda.rpy` | The road home (Oda-sensei) |
| `missions_arc1.rpy` | The Surveyor: Nade's three office missions |
| `events_arc1.rpy` | All Arc 1 character scenes |
| `events_activities.rpy` | Activity scenes, with each character's lines from a table |
| `events_stand.rpy` | The top of the friendship track ("They asked you for something") |
| `events_romance.rpy` | Romance activities, three tiers |
| `events_intimate.rpy` | After the confession |

---

## Art

The 13 character sprite sets (six expressions each; the player has two
outfits) and the 24 campus backgrounds (16 places plus 8 evening and night
versions) are ComfyUI renders, made as `docs/ASSET_PIPELINE.md` describes.
The prologue and story backgrounds are still procedural placeholders (their
generators were retired; they are in git history if needed). The alley, the
ridge veil, the two offices, the Tokyo map and the districts are tinted crops
of existing pictures (`bg_placeholders.rpy`). The campus map
(`tools/genworld.py`), the curses and the tinted stand-ins for Mom, Dad, Oda,
Kurose and Nade (`tools/gensprite.py`) are placeholder art drawn by `tools/`.
Drop real files in with the same names — nothing in the script changes.

## Known gaps

- **Arc Two is not written.** Beginning it from the journal shows a card and
  returns to campus.
- Board jobs play out on their own; they become fights in phase 3. Item
  effects switch on then too.
- Most character missions, the unwritten story beats, the district scenes and
  Sana's flashbacks read "Written in a later build" / "Coming in a later build".
- The Sun Mall and the chapters after it, and the character scenes (hangouts,
  which can come up from day 1), still say "you" until phase 4 converts them
  (design 5.4, D9).
- No audio. `game/audio/` is empty by design so nothing errors.
- Sprites have one pose each (with six expressions).
- Six places have painted evening or night images (`TIME_VARIANT`). The rest
  are tinted, which is convincing but means lit windows stay "lit" at 3am.
