# Background style: Tokyo Jujutsu High

Written from 16 anime reference screenshots in
`~/Desktop/JJK Game images/references/backgrounds/` (2026-09-22). Every background
prompt ends with the same **style paragraph** word for word, so the whole campus
reads as one place and one art style.

## The look

- **Architecture:** traditional Japanese Buddhist temple buildings. Heavy dark-grey
  ceramic tiled roofs with upturned eaves; dark brown wooden pillars and beams;
  white plaster walls; lattice windows; raised wooden verandas with railings;
  stone steps up to every hall.
- **Setting:** a steep forested mountainside. Dense saturated emerald forest, tall
  cedars, mist in the valleys, dappled sunlight and visible sun rays.
- **Stone and water:** mossy fitted-stone retaining walls, pale grey flagstone paths
  and courtyards, stone lanterns, a stone torii on the forest approach, ponds,
  mossy streams, an arched wooden bridge.
- **Landmarks** (put one in the distance where it fits): a tiered pagoda, and the
  tall multi-storey wooden main building.
- **Interiors:** dark polished wood, pale plaster, big windows onto forest. The
  principal's office is a dim wooden hall lit by candles. The dorm rooms are plain
  and modern-simple (metal bed frame, wall air conditioner) inside the old wooden
  shell.

## Rules for a visual novel background

Characters are drawn standing, at eye level, feet on the ground, filling most of
the frame height. So every background needs:

1. **The horizon at their eye line**, about a third of the way down the frame.
   The first courtyard put it through their hips: the camera was at waist
   height, so the characters looked like they towered over the scene.
2. **Open, walkable ground across the lower half**, where a character can stand.
   Nothing big in the middle foreground.
3. **No people and no text.** The references are full of both, so ask explicitly.
4. **Softer than the sprites.** Anime backgrounds are painted, with diffused light
   and haze, while the characters have crisp line art. That difference is what
   makes the characters stand out. The first round was the opposite, with hard
   sun, sharp detail everywhere and high saturation, and it competed with them.

## Round 1 (2026-09-22): what went wrong

- Crisp, contrasty, oversaturated: it read as AI wallpaper, not soft anime paint.
- Low wide-angle camera: a huge tilted floor and the horizon at waist height.
- World logic: the classroom had far more than four desks, and one had grass
  growing indoors. Models ignore numbers, so describe a small room instead.
- The night room came back as static in all four candidates, a failed run.
  install_bg.py now refuses static.
- Scale was fine: the characters stood at a believable size against the halls.

## Locked settings (2026-09-22, after the style and blend tests)

- **Model:** Krea 2 Medium, the paid partner node, at 16:9 and 1K (1376x768),
  creativity "medium". It is enlarged to 1920x1080 by install_bg.py. It costs
  about $0.035 a picture.
- **Words:** each scene description in `tools/bgs/prompts/` plus `tools/bgs/style.txt`.
- **Style references:** four crops of the anime in `references/style_refs/`
  (bridge, pagodas, hall front, campus aerial), each at **0.50**.
  - At 0.9 the model copies the references' contents: framing, lens flare, stray props.
  - At 0.65 a copied roof edge crept back in.
  - At 0.35 it is lovely but a shade too soft.
  - The veranda and wooden-hall frames are left out because they leak.
- **What was tried:** Krea 2 on words alone was soft but washed-out and grey.
  Nano Banana Pro with the references was clean but muted, slipped a figure onto
  some steps, and costs about 5x as much. Keep it for scenes Krea 2 can't manage.
- **Characters fit:** stood in the 0.50 courtyard, Yuji and Megumi sit naturally.
  The vivid anime colour suits the cel-shaded sprites far better than round 1's
  crisp wallpaper look did.

## The style paragraph

Lives in `tools/bgs/style.txt` and is appended to every scene description in
`tools/bgs/prompts/`. Change it there, once, for every location.
