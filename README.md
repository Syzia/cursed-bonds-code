# Jujutsu Kaisen: Cursed Bonds

An unofficial, non-commercial fan game built in **Ren'Py**. A linear prologue
hands off to an **open campus sandbox**: a clock, a map, characters who are
somewhere specific at every hour, and relationships you build by choosing where
to spend your time.

Jujutsu Kaisen is created by Gege Akutami. This is a fan work.

> **Phase 1 is under way:** the arc structure, UI, grades and techniques are
> being reworked (storyboard: https://claude.ai/artifact/V6qPxrGmSUQDUn5twNWsbr),
> so the parts of this README that describe them will change.

```bash
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md      # run
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md lint # check
```

---

## Shape of the game

**Prologue** (linear, ~30 min) — the alley behind the arcade, your sight
opening, Gojo's offer, arrival at Jujutsu High. Then the campus opens and never
closes again.

**Arc 1: Tokyo Jujutsu High** (sandbox) — **21 days** until the Kyoto exchange.
Sixteen locations, nine characters on real schedules, and a story spine that
runs on the calendar whether or not you go looking for it.

### The Arc 1 calendar — `story_arc1.rpy`

| Day | Beat | |
|---|---|---|
| 2 | **Roll Call** | Yaga sets the deadline. Unlocks storehouse + mission board. |
| 4 | **The Board** | Grade-4 patrols become available. |
| 6 | **The Noise Downstairs** | Something gets through the veil. Whoever's nearest fights it with you. |
| 8+ | **Kawagoe Sun Mall** | The arc's real mission. Needs roll call done. |
| +1 | **Aftermath** | Shoko, cursed-energy debt, consequences. |
| 14 | **Gojo's Intensive** | The one thing he actually teaches. Big technique gain. |
| 18 | **The Roster** | Kyoto team announced. Mai. |
| 21 | **The Night Before** | Everyone on the roof. Arc closes; reads back what you built. |

Beats fire wherever you are, gated on day + period + flags, so the three weeks
have shape even if you spend them on a ridge alone.

### Threads — `sb_threads.rpy`

Eight storylines, one per character, each 3–4 stages, shown in the **Journal**
with what you've learned so far. Events declare the stage they represent and the
engine advances it — scenes carry no bookkeeping:

```python
ev("ev_yuji_2", who="yuji", min_bond=35, thread=("yuji_countdown", 2))
```

Prologue choices seed the journal, so who you talked to on day one is already on
the board when the campus opens.

---

## Systems

### The clock — `sb_world.rpy`
Day counter, weekday, and five periods: **Morning / Noon / Afternoon / Evening /
Night**. Most actions cost one period. Sleeping rolls the day, restores stamina
and reserve, and clears the once-a-day interactions.

### Schedules
`SCHEDULE` gives every character a location per period; `WEEKEND` overrides it on
Sat/Sun. Maki opens the dojo at dawn and swims on weekends. Shoko is in the
infirmary all day and on the roof at dusk. Megumi and Toge leave campus at night.
Gojo is rerolled daily from `GOJO_SPOTS`: he's off campus about a third of the
time and rarely where you are — finding him is meant to feel like luck.

`pin(who, loc)` forces someone somewhere for a story beat.

### Cursed energy — `sb_energy.rpy`
Four numbers, not one:

| | |
|---|---|
| **Reserve** (`ce`/`ce_max`) | Spendable. Technique verbs cost it. Training raises the cap. |
| **Control** | Precision. Scales Filament. |
| **Output** | Raw force. Scales Emberfall. |
| **Insight** | Reading energy, rooms and people. Scales Aftersound. |

Gains have diminishing returns past 60 and again past 85.

### Techniques
Three, and each has a **sandbox verb** — something it does while you walk around,
not just in a fight. That's the point of choosing:

- **Filament** *(Control)* — **Sense**: see where every character is, from the
  map, without walking there. Turns the schedule system into information.
- **Emberfall** *(Output)* — **Temper**: work the storehouse forge for large
  Output gains and (later) arm the people you like.
- **Aftersound** *(Insight)* — **Replay**: hear the last hour of any room. Tells
  you who was here and raises their bond, because you understand them better.

Each has four tiers unlocked by its scaling stat (0 / 30 / 60 / 90), ending in a
Domain Expansion.

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

Enemies live in `ENEMIES`, moves in `MOVES` (three per technique, unlocked by
tier). `call combat("key", ally, flee_ok, bg)` returns "win" / "down" / "fled".

### The road home — `story_oda.rpy`
Every sandbox location is on the mountain, Sana is dead and the parents are
edited, so after Chapter 2 the outside world is closed. Oda-sensei is the one
line still running off it: not family, so the veil never took — it is filed on
households. She writes to a school whose name the player's own mother cannot
hold in her head, having worked out on her own that something is wrong.

Two beats. Day 9: the letter, and whether to answer it honestly, carefully, or
at all. Day 15 (only if answered): she has counted nine short-notice transfers
in four years, three of them dead inside eighteen months, and the countersigned
notice she encloses carries the signature Kurose leaked. She is the counterweight
to him — he files, she notices — and answering her turns a civilian into an
asset nine days after being told what that costs.

### Antagonists
See `docs/ANTAGONISTS.md`. One through-line villain — **Sadao Wakuri, "the
Cartographer"**, a Grading Office assessor who files curses one grade low near
students he has chosen, because sorcerers who nearly die young get stronger —
with an arc-level antagonist in front of him each time. Arc 1 is **Ryōsuke
Nade**, the man who signed the Sun Mall as a grade 3; he is not a mastermind,
he is complicit, which is worse. `missions_arc1.rpy` runs that thread across
three office missions ending on a map with the player's home town circled,
dated four years before the alley.

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

Kinds: `story` (auto-fires on arrival), `hangout` (from a character), `mission`
(the office board). A `!` on a character means they have something new.

---

## Adding content

**A scene:** write `label ev_thing:` in `events_arc1.rpy`, add one `ev(...)` line
to the init block at the top. That's the whole wiring.

**A location:** add to `LOCATIONS` in `sb_world.rpy` (including `indoor=`), add
matching `x`/`y` to `NODES` in `tools/genworld.py` (then redraw the map with
`--force`), add an `image bg …` line in `jjk_defs.rpy`. For the picture, write
`tools/bgs/prompts/<name>.txt`, build the workflow with
`tools/make_bg_workflow.py <name>`, run it in ComfyUI and put the pick in with
`tools/install_bg.py`. An evening or night version comes from
`tools/make_relight_workflow.py`, plus a `TIME_VARIANT` entry and a light row.

**A character:** add to `CAST` and `ROSTER_ORDER` in `sb_relations.rpy`, a row to
`SCHEDULE`, a `Character` in `jjk_defs.rpy` and an entry in `CHARS`. Sprites
follow `docs/ASSET_PIPELINE.md`: the base render is repaired and keyed with
`tools/fix_edges.py` and `tools/keysprite.py`, the expressions are added, and
`tools/gen_sprite_defs.py` writes the images into `jjk_sprites.rpy`.

**An action:** add to `place_actions()` in `sb_screens.rpy` and write a matching
`label sb_do_<id>:` in `sb_loop.rpy`.

---

## Files

| File | What |
|---|---|
| `script.rpy` | Entry point, prologue → sandbox handoff |
| `ch1_alley.rpy` `ch1b_the_offer.rpy` `ch2_tour.rpy` | Prologue |
| `ch4_mission.rpy` `ch5_debrief.rpy` | Arc 1 story mission (fired from the office) |
| `jjk_defs.rpy` | Characters, backgrounds, placeholder images, transforms, `CHARS` |
| `jjk_sprites.rpy` | Sprite and side-portrait images, generated by `tools/gen_sprite_defs.py` (don't hand-edit) |
| `jjk_screens.rpy` | Shared screen pieces: panel, section head, meter, chapter card |
| `lighting.rpy` | Scene light, `lit_sprite()`, contact shadows |
| `explore.rpy` | Explore mode (main menu, developer builds only): free roam, no story, every door open |
| `sb_world.rpy` | Clock, locations, schedules, access rules |
| `sb_energy.rpy` | Reserve/Control/Output/Insight, techniques, tiers |
| `sb_relations.rpy` | Cast, bonds, affection, roster |
| `sb_activities.rpy` | Activities per person and what unlocks them |
| `sb_combat.rpy` | Turn-based combat, `ENEMIES`, `MOVES` |
| `sb_events.rpy` | Event registry, dispatcher, small talk |
| `sb_screens.rpy` | HUD, campus map, location view, character panel, status |
| `sb_loop.rpy` | Main loop and every action |
| `sb_threads.rpy` | Per-character storylines and the journal data |
| `story_arc1.rpy` | The seven calendar beats |
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
generators were retired; they are in git history if needed). The campus map
(`tools/genworld.py`), the curses and the tinted stand-ins for Mom, Dad, Oda,
Kurose and Nade (`tools/gensprite.py`) are placeholder art drawn by `tools/`.
Drop real files in with the same names — nothing in the script changes.

## Known gaps

- **Arc 2 (Kyoto) is not written.** The Night Before sets `arc = 2` and stops there.

- No audio. `game/audio/` is empty by design so nothing errors.
- Sprites have one pose each (with six expressions).
- Side portraits are generated but don't show yet: no `Character` has an
  `image=` tag (a phase 1 UI decision).
- Six places have painted evening or night images (`TIME_VARIANT`). The rest
  are tinted, which is convincing but means lit windows stay "lit" at 3am.
