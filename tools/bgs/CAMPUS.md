# The campus: where everything is

The backgrounds are painted one at a time, so this page keeps them agreeing
about one place. Read it before writing a scene in `prompts/`. The positions
follow the campus map (`LOCATIONS` in `game/sb_world.rpy`, drawn by
`tools/genworld.py`), where **up the map is uphill, to the north**.

## The place

Tokyo Jujutsu High sits on a steep forested mountainside on the far edge of
Tokyo, disguised as a private religious school. It looks like a large Buddhist
temple complex: grey tiled roofs, dark timber, white plaster, mossy stone walls,
flagstone yards, stone lanterns, ponds and a stream. It is traditional but
**looked after**, so describe it as well kept, never old or run down (see
STYLE.md, "Clean, not old").

**Season:** early summer, the whole of Arc 1, with lush saturated greens and
clear skies. Bring in rain, autumn or snow only for a story scene that asks
for it.

**Landmarks** (put one in the distance where it fits):

- the **five-storey pagoda**, just north of the courtyard
- the **tall multi-storey wooden tower** at the top of the campus, which is where
  the "rooftop" is
- a thirteen-storey stone pagoda
- the ponds

## The layout, from the bottom of the mountain up

| Place | Where | What it is |
|---|---|---|
| **Main Gate** (`gate`) | south, the foot of the campus | A stone torii across a flagstone approach lined with stone lanterns, climbing through tall cedars. The only road down the mountain starts below it. |
| **Courtyard** (`courtyard`) | the centre | A wide flagstone yard between halls, with the main hall ahead to the north and the pagoda behind it. |
| **Cafeteria** (`cafeteria`) | lower west, near the gate | A single-storey dining hall with long tables and a serving counter. |
| **Classroom Building** (`classroom`) | west of the courtyard | A two-storey wooden school building. The first-years' room looks west onto the forest. |
| **Infirmary** (`infirmary`) | upper west, at the forest edge | A quiet clinic room: beds, curtains, cabinets, and Shoko's desk with an ashtray. |
| **Training Hall** (`training`) | east of the courtyard | A big hall that is **much bigger inside than out**: a vast wooden floor and pillars fading into haze. |
| **Dojo** (`dojo`) | lower east | A long single-storey hall with a row of windows, a polished floor and a weapon rack. The long windowed building in style_ref_2 is its outside. |
| **Principal's Office** (`office`) | upper east | Yaga's dim hall with no windows, lit by candles and full of handmade dolls. |
| **Storehouse** (`storehouse`) | far east, at the back | A white plaster *kura*: racks of sealed boxes and cursed tools, lit by lamps. |
| **Dorm Common Room** (`dorm_common`) | north-west, the boys' dorm ground floor | Sofa, low table, TV, kitchenette. Modern furniture inside the old wooden building. |
| **Your Room** (`your_room`) | north-west, the boys' dorm upstairs | Done. The window faces the mountain. |
| **Girls' Dormitory** (`girls_dorm`) | north-east | A long corridor of identical doors. |
| **Rooftop** (`rooftop`) | top centre | The open wooden veranda at the top of the tall tower, looking south over every roof down the valley. There is no modern flat roof on this campus; this is the highest place a student can stand. |
| **Forest Trail** (`forest`) | north-west, off campus | A trail through old cedars, 40 minutes long. There are no buildings on it. |
| **Riverside** (`riverside`) | north, off campus | A clear mountain river with a pebble bank and a deep pool. It feeds the campus ponds. |
| **Mountain Ridge** (`ridge`) | north-east, off campus | Grass and rock above the treeline. The campus roofs are tiny, far below. |

## What each place sees

- **Gate:** looking north up the approach, through the torii, to the first hall.
- **Courtyard:** the main hall ahead, the pagoda rising behind the roofs.
- **Rooftop:** the whole campus far below, then range after range of mountains.
- **Ridge:** mountains in every direction, with a few grey roofs deep in the valley.
- **Riverside and forest:** wild; nothing built in sight.
- **Rooms:** forest through the windows. The windows are glass and kept shut, as
  in the anime.

## Times of day

Every picture is painted in daylight first. The game tints it for the hour, and
the places people use after dark get a proper evening or night version relit
from the day picture (`make_relight_workflow.py`), so they stay the same place.

These are the ones worth relighting, going by the schedules in
`game/sb_world.rpy`. The game picks them up through `TIME_VARIANT` there.

| Place | Used after dark by | Pictures |
|---|---|---|
| Your room | the player | night (done) |
| Infirmary | Shoko, at night | night (done) |
| Rooftop | Shoko in the evening, and Gojo at any hour | evening and night (done) |
| Riverside | Maki in the evening | evening (done) |
| Dorm common room | nearly everyone, evening and night | evening and night (queued) |
| Girls' dormitory | Nobara and Maki, at night | night (queued) |
| Courtyard, dojo, cafeteria | weekend evenings | the tint is enough for now |
| Principal's office | nobody after dark | none needed: it's candlelit at every hour |

Relight from the approved day picture in `backgrounds_chosen/`. For a room
that was cleaned up, that is the clean version, so night stays clean too.
