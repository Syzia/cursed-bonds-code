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

## Clean, not old

"Old", "worn" and "bare" make the model paint neglect: stained plaster,
specked ceilings, grimy floors, water damage. The first classroom and
bedroom got all of it. Jujutsu High is traditional but looked after, so
describe buildings as traditional and well kept. The interior style asks for
smooth freshly painted walls and clean polished floors. Moss between
flagstones and weathered wood outdoors are fine: that's age, not dirt.

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

## Round 2: the rest of the campus (2026-09-23)

The 13 remaining places. Where each one is and what it looks out on is in
`CAMPUS.md`. Not every place uses the shared exterior set any more:

- **Forest, riverside, ridge:** a nature set, so no temple roofs creep in:
  - `style_ref_10_mossy_stream`: the mossy stream beside the garden path,
    cropped clear of Gojo, Yuji and the subtitle. It's the softest, most
    painterly shot in the folder.
  - `style_ref_9_gate_approach`
  - the bridge
  - `style_ref_11_mountain_sky`: the mountain above the cemetery shot,
    cropped clear of the graves, the browser banner and a lens flare.
- **Gate:** the torii approach, the mossy stream, the hall front and the bridge.
- **Rooftop:** the view down from the veranda (`style_ref_1`), the aerial, the
  pagodas and the mountain sky. It is painted as the veranda at the top of the
  tall tower, since the campus has no flat roof.
- **Office:** Yaga's candlelit hall (`style_ref_8`), in place of the daylight room.

For these places, copying a reference's framing is the point. The sets are
kept to four so the reference that matters isn't diluted.

Left out, and why:

- the curved path, because its metal guard rail would turn up in the forest
- the courtyard from above, because Gojo and Yuji stand in the middle of it
- the walled estate with the pond (`OL-STokyo`), because it's a different place
  (save it for a clan estate scene)
- the cemetery's graves

The office and storehouse use `style_dim.txt`, which is lit by lamps and
candles, because the interior paragraph brings daylight through windows.

**First run (2026-09-23): 11 of 26 finished** before Krea turned requests away
("429 after all retry attempts"). ComfyUI sends every partner request at once,
so a big batch floods Krea, and one failed node stops the whole run. The
workflows now use fixed seeds: press Run again and the finished pictures come
from ComfyUI's cache instead of being made and paid for again.

- Rooftop, forest, riverside, training hall and storehouse came out excellent.
  The infirmary and cafeteria are good.
- The nature set worked: no roofs crept into the forest or the river.
- **Letterboxing:** both office pictures came back with black film bars at the
  top and bottom, although `style_ref_8` has none. The model took the dark,
  moody frame for a film still. The better one is trimmed to the picture
  between the bars. If the office is redone, watch for this.

**Second and third runs (2026-09-23):**

- The other five places came through. The gate, ridge, dojo and common room
  are excellent.
- The girls' dorm came back with stained, blotchy walls in both versions, and
  the common room and cafeteria were mildly dingy. The Nano Banana clean-up
  fixed all three with the layout kept. The clean wording in the style
  paragraph helps, but doesn't guarantee a clean room, so budget a clean-up
  pass for corridors and plain-walled rooms.
- **Google's filter** blocked the first clean-up because the wording said
  "remove every stain, water mark...", which it read as removing a watermark.
  The clean-up now describes the finished room instead.
- The relights (rooftop at evening and night, riverside at evening, infirmary
  at night) all held the layout exactly, first time.

## The style paragraph

Lives in `tools/bgs/style.txt` and is appended to every scene description in
`tools/bgs/prompts/`. Change it there, once, for every location.
