# Sprite prompts

**The prompts actually used live in `tools/chars/prompts/<character>.txt`** —
one file each, in the four-paragraph structure that produced the reference Yuji
(framing and expression / face and hair / clothing / art style, the last word
for word the same for everyone). `tools/make_base_workflow.py <character>`
turns one into a drag-in Comfy Cloud workflow. The blocks below are the
starting descriptions those files were written from.

**Name them, on Krea-2 Turbo (2026-09-23).** Yuji and Megumi came out in MAPPA's
Jujutsu Kaisen style because their descriptions were distinctive enough for the
model to recognise them. Nobara, described as an orange bob in a uniform, came
out generic. One Run compared the two approaches for her, two pictures each:
her description plus a written-out version of the style gave the right
proportions but a flat, generic face. "Nobara Kugisaki from the anime Jujutsu
Kaisen, drawn exactly as she appears in MAPPA's Jujutsu Kaisen anime" gave her
real face, hair and colouring. So for the rest of the cast: **name the character
and MAPPA's style, then describe**. This model runs open on Comfy Cloud, so a
name can't be refused. Still never name them to closed services such as
Nano Banana or Seedream. The winning prompt is prompts/nobara.txt; the losing one
is kept as prompts/nobara_described.txt.

**When the name isn't enough (Shoko, 2026-09-23).** A minor character gets a
generic face even when named: Krea draws her from the description, and small
facial features such as tired eyes and a mole are exactly where it stops
listening. Keep the base for its body and outfit, and redraw the face and the
top of the hair with Nano Banana on the head close-up: add the character to
HEAD_FIX in tools/fix_edges.py, and the head goes into the same Run as the edge
repairs.

The notes below were first written for a general-purpose model assumed not to
know Jujutsu Kaisen by name. On a
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
light orange-brown chin-length bob with pointed tips, fringe sweeping across one eye, other
side tucked behind the ear, reddish-brown eyes with separate lower-lash strokes, cropped
navy jacket with mandarin collar and gold buttons over a white blouse, high-waisted flared
navy skirt to the knee with a wide buttoned waistband, brown sheer tights, brown loafers,
one hand on her hip (full prompt: prompts/nobara.txt)

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
original character, a Sung Jin-Woo type (Sung Jinwoo's face and hairstyle, named to Krea):
strikingly handsome, dark chocolate brown hair, messy, with a fringe of pointed locks and one
falling between the eyes, sharp narrow grey-violet eyes, lean and athletic, cool and watchful,
Jujutsu High uniform, rendered on magenta (full prompt: prompts/mc.txt; the Yotsuka High
outfit is the same picture with the clothes swapped)

## sana
original character with Reze's (Chainsaw Man) face and purple bob, a white daisy hair clip,
green eyes, the Yotsuka High uniform (grey blazer, red ribbon, grey pleated skirt), no choker,
rendered on magenta (full prompt: prompts/sana.txt)

---

## Expressions

Expressions are not prompted any more. The base picture is the neutral, and
the other five come from an edit model: `tools/make_edit_workflow.py` sends
the head close-up (from `composite_face.py --prepare`) to Nano Banana Pro with
one instruction per expression, from `EXPRESSIONS` (the shared wording) or
`CHAR_EXPRESSIONS` (a character's own, such as Gojo's, whose eyes are under
the blindfold), and `composite_face.py` pastes each face back. Describe only
what changes, and never name the character to it. The full steps are in
docs/ASSET_PIPELINE.md (recipe step 6).

## Target output

760 x 1400 RGBA, figure centred, feet ~40px from the bottom, head ~40px from the
top. Name files `<key>_<expression>.png` in `game/images/char/`, then run
`python3 tools/gen_sprite_defs.py` — the declarations and expression attributes
wire themselves up. Side portraits are generated too, but they only appear once
the Characters get image= tags, which none has yet (a phase 1 UI decision).
