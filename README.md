# Jujutsu Kaisen: Cursed Bonds

An unofficial, non-commercial fan game built in **Ren'Py**. A linear prologue
hands off to an **open campus sandbox**: a clock, a map, characters who are
somewhere specific at every hour, and relationships you build by choosing where
to spend your time.

Jujutsu Kaisen is created by Gege Akutami. This is a fan work.

```bash
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md      # run
~/Desktop/renpy-8.5.3-sdk/renpy.sh ~/Desktop/JJKgame.md lint # check
```

---

## Shape of the game

**Prologue** (linear, ~30 min) — the East Wing, your technique waking up, Gojo,
arrival at Jujutsu High. Then the campus opens and never closes again.

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
Gojo is rerolled daily from `GOJO_SPOTS` and is *usually absent* — finding him is
meant to feel like luck.

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

### Lighting — `sb_world.rpy`
One authored image per place, tinted at runtime so a room reads as the hour
you're standing in it. `graded_bg()` picks a tint + brightness from
`OUTDOOR_GRADE` / `INDOOR_GRADE` (interiors get a gentler curve — a lit corridor
at midnight is not a blue field) and caches one displayable per
`(place, period)` outside the store, so screens don't churn and saves stay small.

Places in `NIGHT_VARIANT` have a genuinely different night image rather than a
tint (your room's window shows a mountain by day and a moon by night); those are
served ungraded at Night so they aren't crushed twice.

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

### Affection, and the ceiling — `sb_relations.rpy`
Bond gates affection up to **100**. At 100 there is nowhere left for it to go,
and one activity appears: **Say it**. That scene is written per character, and
playing it calls `begin_together()`, which lifts the ceiling to **200** and
opens four tiers of quieter, more intimate activities above it — staying the
night, waking up together, a whole day off, and talking about after. Ranks
past 100 are Certain / Devoted / Inseparable / Unconditional.

Everything above the confession is *hidden* until it happens, rather than shown
as a lock, so the ceiling is a surprise rather than a checklist.

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

Kinds: `hangout` (from a character), `place` (location), `story` (auto-fires on
arrival), `mission` (the office board). A `!` on a character means they have
something new.

---

## Adding content

**A scene:** write `label ev_thing:` in `events_arc1.rpy`, add one `ev(...)` line
to the init block at the top. That's the whole wiring.

**A location:** add to `LOCATIONS` in `sb_world.rpy` (including `indoor=`), add
matching `x`/`y` to `NODES` in `tools/genworld.py`, add an `image bg …` line in
`jjk_defs.rpy`.

**A character:** add to `CAST` and `ROSTER_ORDER` in `sb_relations.rpy`, a row to
`SCHEDULE`, a `Character` + `image` in `jjk_defs.rpy`, an entry in `CHARS`, and a
sprite row in `tools/gensprite.py`.

**An action:** add to `place_actions()` in `sb_screens.rpy` and write a matching
`label sb_do_<id>:` in `sb_loop.rpy`.

---

## Files

| File | What |
|---|---|
| `script.rpy` | Entry point, prologue → sandbox handoff |
| `ch1_east_wing.rpy` `ch2_arrival.rpy` | Prologue |
| `ch4_mission.rpy` `ch5_debrief.rpy` | Arc 1 story mission (fired from the office) |
| `sb_world.rpy` | Clock, locations, schedules, access rules |
| `sb_energy.rpy` | Reserve/Control/Output/Insight, techniques, tiers |
| `sb_relations.rpy` | Cast, bonds, affection, roster |
| `sb_events.rpy` | Event registry, dispatcher, small talk |
| `sb_screens.rpy` | HUD, campus map, location view, character panel, status |
| `sb_loop.rpy` | Main loop and every action |
| `sb_threads.rpy` | Per-character storylines and the journal data |
| `story_arc1.rpy` | The seven calendar beats |
| `events_arc1.rpy` | All Arc 1 character scenes |

---

## Art

Everything in `game/images/` is procedurally generated placeholder art from
`tools/` (no dependencies, not even Pillow). Drop real files in with the same
names — nothing in the script changes. See `tools/README.md`.

## Known gaps

- **Arc 2 (Kyoto) is not written.** The Night Before sets `arc = 2` and stops there.

- No audio. `game/audio/` is empty by design so nothing errors.
- Sprites have one pose and no expressions.
- The fonts are DejaVu, which has **no CJK glyphs** — avoid kanji in UI strings
  or ship a font that covers them.
- Only `dorm` has a real night image. Other interiors are tinted, which is
  convincing but means lit windows stay "lit" at 3am.
