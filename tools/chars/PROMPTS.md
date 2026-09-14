# Sprite prompts

Written for a general-purpose model (Krea-2 / SDXL-class) that does **not** know
Jujutsu Kaisen by name — every character is described, never named. On a
Danbooru-tag anime checkpoint (Illustrious, NoobAI, Pony) you can replace the
description block with the character tag and get closer likeness for less work.

## House style block — append to every character

```
clean cel shaded anime illustration, crisp dark line art, flat colours with one
shadow tone, visual novel character art, solid flat chroma green background,
even lighting, no shadows on the background
```

## Framing block — append to every character

```
full body anime character sprite, standing facing the viewer, arms relaxed at
their sides, entire figure visible from head to feet with space around them
```

Aspect ratio **9:16**. LoRAs off. Keep the seed when you find one that works —
reuse it across expressions so the body stays stable.

---

## yuji
short salmon-pink hair in an undercut, dark shaved sides, pink top swept up and back
in soft spikes, brown eyes, two small dark marks under each eye, strong eyebrows,
warm open face, athletic build, dark navy high-collared school uniform jacket open
over a red hoodie with the hood bunched behind the collar, dark trousers, white sneakers

## megumi
black hair in heavy upward spikes sweeping back with strands falling over the brow,
narrow sea-green eyes, permanent slight frown, pale, slim and tall, dark navy
high-collared school uniform buttoned to the throat, hands in pockets

## nobara
orange-ginger hair in a chin-length bob with a long side-swept fringe over one eye,
brown eyes, sharp confident expression, chin slightly raised, dark navy school jacket
open at the collar, pleated skirt, knee socks, sneakers

## maki
very dark green hair in a high ponytail with a straight fringe, round red-brown
glasses, gold eyes, hard level stare, athletic and tall, dark navy school jacket
with the sleeves pushed up

## panda
an anthropomorphic panda standing upright, two metres tall and stocky, black eye
patches ears arms and legs, white face belly and crown, big soft expressive eyes,
kind face, wearing a fitted dark navy school uniform jacket

## toge
pale ash-white hair, short and messy with a fringe over the brow, calm violet eyes,
a dark high uniform collar zipped up over his mouth and nose so only the eyes show,
small dark fang-like seal marks on the cheeks above the collar

## shoko
shoulder-length loose brown hair slightly untidy, brown eyes with tired shadows
beneath them, pale, deadpan expression, white doctor's lab coat over a dark shirt

## gojo
very tall and lean young man, spiky white hair swept up and back, a wide black
blindfold cloth covering the eyes completely, confident grin, long dark
high-collared coat, dark trousers, dark boots, hands in pockets

## yaga
large broad heavily built man, tan skin, black hair in a short spiky flat-top, goatee,
dark rectangular sunglasses, stern, dark uniform jacket tight across the shoulders

## ijichi
neat black side-parted hair, rectangular glasses, pale, anxious expression, black
business suit with a white shirt and dark tie, slight stoop, hands clasped

## mc
violet-tinted dark hair of medium length swept to one side with a lock falling
between the eyes, grey-violet eyes, slim, average height, watchful expression,
dark navy high-collared school uniform jacket

## sana
sixteen year old girl, short dark hair with a grown-out fringe pinned back, dark eyes,
small round face, bright cheerful expression, grey school blazer with a red ribbon tie
and grey pleated skirt

---

## Expressions

Generate the body once, then change only the face. On a full-inpainting setup,
mask the head and re-run with the expression swapped. Without inpainting, keep
the same seed and change only this clause:

| | |
|---|---|
| neutral | `neutral expression, mouth closed, relaxed brows` |
| happy | `smiling warmly, eyes slightly narrowed, raised brows` |
| serious | `level stare, mouth a flat line, lowered brows` |
| angry | `angry glare, furrowed brows, teeth showing slightly` |
| surprised | `wide eyes, raised brows, mouth open slightly` |
| sad | `downcast eyes, brows angled up at the inner ends, small frown` |

## Target output

760 x 1400 RGBA, figure centred, feet ~40px from the bottom, head ~40px from the
top. Name files `<key>_<expression>.png` in `game/images/char/`, then run
`python3 tools/gen_sprite_defs.py` — the declarations, expression attributes and
textbox side portraits all wire themselves up.
