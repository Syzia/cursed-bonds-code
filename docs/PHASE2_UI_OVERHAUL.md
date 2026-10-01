# Phase 2: the UI overhaul

*Jujutsu Kaisen: Cursed Bonds · scope written 30 Sep 2026 from the owner's playtest notes on checkpoints 2 and 3 ("JJK notes", with screenshots).*

This is the scope of a new phase that the owner asked for after playing the phase 1 build. It is **not yet a build plan**. Once the open questions at the end are answered and phase 1 (WP0–WP11) has passed the owner's checkpoint 4, it gets a full design in the style of `PHASE1_DESIGN.md`: work packages, contracts and acceptance.

## The new phase order

| # | Phase | What it is |
|---|---|---|
| 1 | Foundation | Built. WP0–WP11 are merged on `phase1`, pending the owner's checkpoint 4. |
| **2** | **UI overhaul** (new) | This document. |
| 3 | Combat | Formerly phase 2: Black Flash, partner moves, tool and talisman effects, real board fights, enemy phases. |
| 4+ | Story acts | Formerly phase 3+: the unwritten missions, districts, Sana's flashbacks, converting the chapters to "I". |

The UI comes before combat for three reasons:
- the combat screen, board fights and every new act will sit inside the new map, journal, icons and grade colours;
- building those first means combat and story are built once, not built and then reskinned;
- the phase needs almost no art spend until its last part.

This order replaces the storyboard's build order (Foundation → Combat → Act I …). The storyboard scheduled "people in their places" and "blinking and talking" for the Act I phase; they move here, because the owner's notes treat them as part of how every screen feels.

---

## 1. The owner's notes, and whether each was already planned

| Note | Was it planned? | Where it goes |
|---|---|---|
| The campus map is too cluttered. Show only the main areas, then the places inside an area once you go there (e.g. "School Building", then Classroom, Cafeteria, Infirmary, Library) | **New** | 2.A |
| The map header "TOKYO JUJUTSU HIGH · Campus · Tokyo" is too crowded for the middle. Call it "Jujutsu High" and put it at the top. The day is in a good spot | **New** | 2.A |
| Clicking an area zooms into its own bird's-eye picture with its sub-places | **New** (the storyboard only had a campus layer and a Tokyo layer) | 2.A |
| "Find someone" belongs in the journal, on each character's profile: where they are now and what they're doing, updated as the story moves | **New** | 2.C |
| The strip of faces on the map gets more crowded with every new character | **New** (same fix as above) | 2.C |
| Send Kaito back to his room at night to sleep, with some exceptions | **New** | 2.H |
| Journal and Menu buttons are in good places; the Map button needs a better one | **New** | 2.B |
| Small icons for every feature instead of words, with the word popping up on hover | **New** | 2.B |
| More to do in some rooms, e.g. a computer in the bedroom that affects other things | **New** | 2.G |
| A board game in the common room when people are there | **New** | 2.G |
| Fishing | **New** | 2.G |
| Little interactive things all over the map | **New** | 2.G |
| Characters should blend into backgrounds and foregrounds, with a smoother change from idle to talking | **In the storyboard** ("People in their places", "Blinking and talking", "Motion in the engine"), scheduled for the Act I phase; not in phase 1 or WP11 | 2.F |
| People say they're doing something ("on her phone") but just stand there, waiting for the player. Utahime's office is the prime example | **In the storyboard**, same as above | 2.F |
| The person view is cluttered: no need for the name; keep the grade and the choices | **New** | 2.D |
| "Somebody Remembered": is that a quest? | Answered below | 2.D |
| Put Memories into the People tab, each memory under its person | **New** (phase 1 built six tabs, as the storyboard had them) | 2.C |
| The Stats tab is good, a little cluttered | Polish | 2.C |
| Utahime's board looks good | Kept | — |
| The armory is good, but tools need more depth and requirements, especially the Inverted Spear of Heaven | **Partly**: tool and talisman effects are in the combat phase; requirements beyond grade are new | 2.I |
| Colour by grade: Grade 4 green, Grade 3 blue, Grade 2 purple, Grade 1 red, Special Grade oil slick; the same for talismans | **New** | 2.E |

**Also spotted in the screenshots:** Ren'Py's "SKIPPING" tag sits on top of the map and journal headers. It moves in 2.B.

**"Somebody Remembered" is not a quest.** It is the name of Nobara's personal story (her friend Saori). It belongs to the older *story threads* system (`sb_threads.rpy`): Yuji, Megumi, Nobara, Maki, Panda, Toge, Shoko and Gojo each have one, with four stages that their hangout scenes advance. The diamonds next to it (◆◇◇◇) are her progress. Phase 1's character missions sit on top of these threads, which is why it looks like a quest but isn't listed as one. In this phase it moves off the person view and into the journal, as the "story" section of each character's page, with the next step spelled out.

---

## 2. Scope

### 2.A The map, in two levels

- **The campus map shows only the main areas.** Each area is a large marker on the bird's-eye picture, showing the people there and any mission waiting. Proposed areas:
  - School Building (was "Classrooms");
  - Dormitories;
  - Staff Building;
  - Training Grounds;
  - Courtyard & Gate;
  - The Mountain.
- **Choosing an area takes you there** and opens that area's own view: a closer bird's-eye picture with its sub-places, for example School Building → Classroom, Cafeteria, Infirmary, **Library** (new). New places slot into their area without touching the main map.
- **The header:** "Jujutsu High" at the top. The day stays top left. The Campus / Tokyo switch leaves the middle and becomes a small toggle.
- **Tokyo works the same way:** districts first, then each district's own places (the storyboard already calls each district "a small hub with its own places").
- **Time:** walking stays free, within an area and between areas.
- **Art:** a bird's-eye picture per area (6 on campus, plus Tokyo), placeholders first, the way phase 1's backgrounds work.

### 2.B The HUD, icons and labels

- **Map button:** it moves (see question 1). Journal and Menu stay where they are.
- **Icons everywhere:** every button, place action, person choice, journal tab and map marker gets a small icon. Its name appears when the pointer rests on it. This takes most of the words off the screen.
- **The skip tag:** it moves out from under the map and journal headers.

### 2.C The journal: five tabs, with the person at the centre

- **Tabs:** People · Missions · Stats · Equipment · Inventory. Memories fold into People.
- **Each person's page** holds:
  - **Right now:** where they are and what they're doing ("Cafeteria, halfway through an enormous bowl"). This replaces the map's Find someone strip, which goes.
  - **Their story:** the story thread (e.g. *Somebody Remembered*) and their character missions as one list of chapters, with the next step and where.
  - **Memories:** every scene you've shared with them, replayable.
  - Grade, bond and strength, as now.
- **Scenes that aren't about one person** (story missions, the prologue) replay from Missions › Story (see question 6).
- **Stats and People:** a lighter layout, less on screen at once.

### 2.D The person view

- **Removed:** the name (the nameplate in the scene already says who it is) and the story-thread diamonds, which move to the journal.
- **Kept:** the grade and the three or four choices, with icons.
- The "Closer: … at Bond 20" hint moves to the journal page.

### 2.E Grade colours, everywhere

| Grade | Colour |
|---|---|
| Grade 4 | Green |
| Grade 3 | Blue |
| Grade 2 | Purple |
| Grade 1 | Red |
| Special Grade | Oil slick: a slow shifting rainbow sheen |

- **Where it shows:** grade chips in the journal, board cards, the grade card, the combat header, cursed tools and talismans (and later, curses).
- **Semi-grades** (Utahime's "Semi-Grade 1") and Gojo's "Off the scale": see question 7.

### 2.F The place view comes alive

Already promised by the storyboard, now moved here.

- **People in their places.** For each character and place they go to, one picture painted into that background, doing what the caption says: Nobara on her phone in the common room, Utahime buried in paperwork at her desk, Yuji halfway through a bowl. Nano Banana, about $0.32 a picture; the storyboard's list has about 15.
- **Until the pictures exist,** the engine blends the standing sprites in better:
  - a soft contact shadow;
  - colour and light matched to the background and the time of day (lighting.rpy already grades backgrounds);
  - scale and a touch of blur by depth;
  - a foreground layer (a table edge, a doorframe) in front of people where the place has one;
  - slow idle breathing.
- **From idle to talking.** When you choose someone, the camera eases in and the idle picture dissolves into their talking sprite, which turns to face you. It dissolves back when you leave. Blinking and talking mouths: two edits per character, about $0.32 each.
- The owner makes the pictures in ComfyUI from workflow files handed over with numbered steps, as with the sprites.

### 2.G Things to do in rooms

- **Hotspots:** clickable objects in the background of a place, each with an icon and a hover label. This is the framework the next three ideas sit on, and it takes "little interactive things" anywhere on the map.
- **The bedroom computer** (see question 3). Some ideas:
  - read the jujutsu network's rumour board, which feeds leads to Utahime's board;
  - message friends, for a small bond gain;
  - order supplies, which spends yen;
  - research a curse before a job, for insight.
- **A board game in the common room** when people are there (see question 4). A short game against whoever is present, for bond. It uses their personality: Megumi plays careful, Yuji plays chaos.
- **Fishing at the riverside** (see question 5). A timing game; the catch goes to the cafeteria, becomes gifts, or sells for yen.
- In this phase: build the hotspot framework plus a simple version of each idea the owner picks. Deeper versions can come later.

### 2.H The night rule

- At Night, Kaito heads back to his room: other places are closed and the map says why.
- **Exceptions** (see question 2) could include:
  - story beats that happen at night;
  - a companion who asks you to stay out (the rooftop);
  - a night mission or patrol;
  - Gojo on one of his days.

### 2.I Cursed tools and talismans with more depth

- **Requirements beyond grade,** shown as a checklist on the armory card. For example:
  - Inverted Spear of Heaven: Arc Two, Special Grade, a story unlock, and Yaga's signature;
  - Playful Cloud: a raw-strength threshold;
  - Split Soul Katana: an Insight threshold, because you have to see the soul to cut it.
- **Grade colours** on every tool and talisman (2.E).
- **The effects themselves** switch on in phase 3 (combat), as already planned.

---

## 3. Order inside the phase

1. **Structure, no art cost:**
   - the two-level map;
   - the header;
   - the HUD;
   - icons and hover labels;
   - the journal's five tabs and person pages;
   - the person view;
   - grade colours;
   - the night rule;
   - tool requirements.
2. **Presentation:**
   - the engine-side blending, the foreground layers and the idle-to-talking transition;
   - then the people-in-places pictures and blink/talk edits as the owner makes them.
3. **Rooms:** the hotspot framework and the first simple activities.

## 4. Art this phase needs

- A bird's-eye picture for each campus area (6), plus Tokyo. Placeholders until then.
- About 15 people-in-places pictures to start (about $0.32 each; the storyboard's list).
- Blink and talk edits for the 13 cast members (about $0.32 each).
- Foreground layers for the busiest places.
- A Library background.
- Icons: a small matched set, made or drawn once.

## 5. Questions for the owner

1. **Map button:** where should it go?
   - (a) bottom left, as a small compass icon;
   - (b) top left under the day;
   - (c) replaced by clicking the day/place name.
2. **The night rule:** which exceptions do you want? The list in 2.H is a starting point.
3. **The bedroom computer:** which of the ideas in 2.G, or something else?
4. **The board game:** which game? Shogi, go, hanafuda, or a made-up jujutsu card game.
5. **Fishing:** in or out, and what should a catch give?
6. **Story scenes that aren't about one person:** replay from Missions › Story (proposed), or under the main person in them?
7. **Colours:** does a semi-grade take its grade's colour, a lighter shade of it, or something else? Should Gojo's "Off the scale" use the Special oil slick?
8. **The Library:** add it as a new place in the School Building?
