# The second UI overhaul: scope and the owner's word

*Started 6 Oct 2026, after phase 2 was merged. This file holds what the owner
asked for, in their words, and how each thing was read. It wins over any plan
written from it. Nothing here is designed yet; the audit of what the game
still lacks is `docs/UI_AUDIT.md` (written when the audit run finishes).*

## 1. What was asked

**6 Oct, in chat:** "Lets plan a UI overhaul adding the new locations, all the
missing backgrounds. Missing players interacting with the environment, and
anything else. [...] everything related to UI that is".

**5 Oct, after checkpoint D** (also in `docs/PHASE2_UI_OVERHAUL.md`, section 5):
"we do need to add dorms, instead of just girls dorms and my dorm. Also where
do the teachers stay. We're going to need a teachers lounge/dorms. If they
stay on campus. Gojo wont, but the other will." and "We can add an invite
feature. Like invite toge or panda etc to come play."

## 2. The owner's review (6 Oct, "Untitled document (3).pdf", 19 pages)

Eighteen pages of screenshots from a playthrough, then these notes, verbatim:

> This one isnt as important, but we need a good title card.

> We need to put in all the backgrounds that we missed.
>
> We need to redo locations; they just don't feel very alive. The grainy
> texture and vague view from the windows.
> I think we should redo every location. They can't look like artworks but
> instead actual scenearies.
>
> Then we need to blend the characters into the background.
>
> New locations to add: (We can redo the jujutsu high map)
>
> Campus:
> - Teachers' lounge
> - Osen/sauna recovery rooms
> - teachers' dorms
> - Swimming pool
>
> You can add some locations if you feel theyre needed.

**What the screenshots show**, in order:
- The title screen (the Main Gate picture with the title over it).
- The prologue on flat stand-in pictures: the diner counter, the street, the
  city at night, the alley (a black screen), the curse (a blob), the fight
  screen, the parents' living room (the parents are block figures), the
  bedroom at night, the house from the street, the car window.
- The ridge and my room (painted).
- The courtyard, with the vending machine's icon on a porch that has no
  machine painted on it.
- The dormitory garden, the girls' dormitory corridor, the first level of the
  campus map (a flat drawing), the school courtyard, the training yard, the
  staff building steps, the mountain path, the ridge.
- Tokyo: Home (Yotsuka), Shibuya and Harajuku, all flat stand-ins with
  "Later build" pins.
- The library, the common room, the infirmary and the cafeteria.

## 3. Answers so far

| Asked | The owner's answer (6 Oct) | Read as |
|---|---|---|
| Sprites for the people who are still block figures (the parents, Kurose, Nade) and the curses, or backgrounds only? | "Yes plan sprites too" | The plan includes sprites for them. |
| The dormitories: a corridor of doors like the girls' one, or rooms I can walk into? | "rooms you can walk into" | The boys' dormitory has rooms that are places. |
| | "But make the boys dorm you the place where the mc stays." | My room is in the boys' dormitory: it is reached through it, not straight from the garden. |

## 4. How the review was read

- **Every campus location is redone.** The audit had counted the 24 campus
  pictures as finished (painted, one style). The owner's eye says otherwise,
  and that decides it.
- **"Actual sceneries", not "artworks":** read as a sharp, clean frame of a
  real place, like a background from the anime, with a clear view through the
  windows, and not a soft, grainy painting. A look test on three places
  (`~/Desktop/JJK Game images/look_test/`) settles this before anything else
  is redone.
- **Redone in place:** each picture is redone from the current one, same
  camera and layout, so the icons, exits and standing spots that sit on it
  stay where they are.
- **"Blend the characters into the background":** read as people who look
  like they stand in the room: a shadow under them, their colours matched to
  the room's light, a believable size and floor line, furniture in front of
  them where it should be; and, after the rooms are redone, painted poses of
  people doing things.
- **New places:** the four the owner named, more dormitories (asked on 5 Oct),
  and any others the plan proposes (the owner: "You can add some locations if
  you feel theyre needed").
- **The campus map is redone** with the new places on it.
