# Sprite prompts

**The prompts actually used live in `tools/chars/prompts/<character>.txt`** —
one file each, in the four-paragraph structure that produced the reference Yuji
(framing and expression / face and hair / clothing / art style, the last word
for word the same for everyone). `tools/make_base_workflow.py <character>`
turns one into a drag-in Comfy Cloud workflow. The blocks below are the
starting descriptions those files were written from.

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
their sides, zoomed out wide shot, the whole figure from the top of the head to
the soles of the shoes sits inside the frame with clear empty green space above
the head and below the feet, nothing touching any edge of the image
```

The first render came out with the right shoe clipped by the bottom edge and
seven pixels of clearance over the hair — the model fills the frame unless it is
pushed not to, and a clipped foot means the figure's real height is unknown, so
it cannot be scaled correctly against the rest of the cast. The keyer now
refuses to pass a render silently when this happens; `--batch` prints
`figure runs off the bottom of the frame` and you re-roll that one.

Aspect ratio **9:16**. LoRAs off. Keep the seed when you find one that works —
reuse it across expressions so the body stays stable.

### What Krea-2 Turbo actually honours (measured on yuji, 2026-09-14)

Landed correctly: hair colour and the undercut, brown eyes, the red hoodie with
its drawstrings sitting behind the jacket collar, dark navy jacket, white
sneakers, the flat green backdrop, and the full-body framing. The line art came
out near-black rather than dark navy, which is fine.

Dropped: the small under-eye marks. Small facial details are where this model
stops reading the prompt, so anything of that kind — Toge's cheek seals, Gojo's
eyes, Yuji's marks — needs it spelled out as a physical object ("a short dark
tattooed line on the cheekbone") rather than named as a feature, and may still
need a touch-up pass. The blocks below use that wording where it matters.

---

## yuji
short salmon-pink hair in an undercut, dark shaved sides, pink top swept up and back
in soft spikes, brown eyes, **a short dark tattooed line on the cheekbone directly
under each eye**, strong eyebrows, warm open face, athletic build, dark navy
high-collared school uniform jacket open over a red hoodie with the hood bunched
behind the collar, dark trousers, white sneakers

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
