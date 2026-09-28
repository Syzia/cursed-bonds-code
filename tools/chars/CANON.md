# Character canon — how each person must read on screen

Every sprite is 760x1400 RGBA, full body, feet ~40px from the bottom, head ~40px from the top,
figure centred. Tokyo Jujutsu High uniform unless noted: very dark navy (near-black, #1c1f2e-ish) jacket
with a standing collar, matching trousers/skirt, white sneakers unless the entry says otherwise (Megumi wears brown
ankle boots). Line art dark navy, not pure black.
Six expressions each: neutral, happy, serious, angry, surprised, sad. Also a side portrait
(head + shoulders crop, ~360x360) for the textbox.

## Ages (this game, not canon)
The first-year class is **18**: Yuji, Megumi, Nobara and the player. Sana, the
player's age, is 18 too. The dialogue that states ages matches this. Older
characters keep their own history, such as Shoko, Gojo and Geto at sixteen.
Describe the first-years to image models as young adults of eighteen, drawn
in the same mature style as each other.

## yuji — Yuji Itadori (1st year)
Salmon-pink hair, short undercut: dark shaved sides, pink top pushed up/back in soft spikes. Brown eyes,
small dark marks under each eye (signature). Strong brows, open friendly face, athletic shoulders.
Uniform jacket worn over a RED HOODIE — hood bunched at the neck behind the collar. Default expression
warm; angry is fierce, not mean.

## megumi — Megumi Fushiguro (1st year)
Checked against official full-body art (2026-09-21). Black hair, a dense crown of sharp spiky tufts
flaring up and out like black flames, several pointed locks falling over the forehead to eye level,
short at the sides with ears showing. Dark blue-grey eyes with HEAVY HALF-LIDDED UPPER LIDS — the
drowsy, bored look is his face; wide round eyes read as someone else. Pale, long narrow face, pointed
chin. Tall and slim with long legs. Uniform jacket in navy (not purple), hip length, with a very tall
loose funnel collar up to the jaw and an ASYMMETRIC closure: the front flap crosses diagonally from the
collar to one side, two gold swirl buttons off-centre on that side (one on the collar, one on the chest).
Trousers TAPERED and CROPPED above the ankle, pleated at the waist, loose at the thigh — not wide-leg.
Black socks showing. TAN-BROWN LEATHER ANKLE BOOTS, not the cast's white sneakers. Hands often in
pockets. Default expression flat/bored; happy is barely a smile; anger is cold, not shouted.

## nobara — Nobara Kugisaki (1st year)
From the official anime art and screenshots in `references/characters/nobara/`
(2026-09-23).
- **Hair:** light orange-brown, a muted ginger-brown rather than bright orange.
  A straight chin-length bob with fine pointed tips, parted on one side. The
  long side of the fringe sweeps across the forehead past one eye; the other
  side is tucked behind the ear.
- **Face:** an oval face with a soft jaw and small pointed chin. Reddish-brown
  eyes with a thick upper lash line and short separate strokes for lower
  lashes, which is her signature look. Thin neat brows, pale pink lips.
- **Uniform:** a cropped navy jacket ending above the waist, with a small
  mandarin collar, gold buttons and white cuffs. A band of white blouse shows
  below it. A high-waisted flared navy skirt to the knee, with a wide dark
  waistband and gold buttons. Brown sheer tights and brown penny loafers.
- **Build:** slim, with narrow shoulders, shorter than the boys (drawn 160 cm).
- **Stance:** one hand on her hip. Carries herself like she's decided
  something. Angry is her best expression.

She is 18 in this game, like Yuji and Megumi (see "Ages" at the top). Draw her
as a young woman the same age as them, in the same mature style: a long oval face, narrow heavy-lidded eyes and about 7.5 heads tall. The
first render came out childlike because the prompt said "shorter and more
delicate than the boys", "soft rounded jaw" and "blush". Never put height in a
prompt: the frame is always full height, so the model shows "short" with child
proportions. keysprite's HEIGHT_CM sets her height in the game.

## maki — Maki Zenin (2nd year)
Very dark green (reads black-green) hair in a high ponytail with a straight fringe. GLASSES with round
red-brown frames (she needs them to see curses). Gold/amber eyes, hard stare. Athletic build, taller than
the first-years. Uniform jacket, sleeves sometimes pushed up. Often a naginata or training blade — omit
weapon in the sprite. Rarely smiles; "happy" is a smirk.

## panda — Panda (2nd year)
An actual panda, ~2m tall, stocky, standing upright. Black eye patches, ears, arms, legs; white face,
belly, top of head. Wears the uniform JACKET (fitted for him) — no trousers needed. Expressive, kind
face; big soft eyes inside the patches. Happy is a broad smile; angry shows small fangs.

## toge — Toge Inumaki (2nd year)
Pale ash-white hair, short and messy with fringe over the brow. Violet/purple eyes, calm and a bit sleepy.
The uniform collar is ZIPPED UP HIGH over his mouth and nose — you never see his mouth. Visible on his
cheeks above the collar: small dark "snake-and-fangs" seal marks (short curved lines at the corners of the
mouth area, like stylised fangs). Expressions live entirely in the eyes and brows.

## shoko — Shoko Ieiri (doctor)
From her official character design sheet in `references/characters/shoko/` (2026-09-23).
- **Age:** 28.
- **Hair:** long and straight, a warm dark cocoa brown (the sheet measures
  hue +11°), past the shoulders to mid-chest. It is parted in the centre and
  falls straight down both sides of her face, so her whole forehead shows,
  with a few thin strands at the temples. Don't write "reddish" or "bangs":
  the first four renders came back burgundy (hue −4°) with a side fringe
  across the forehead.
- **Face:** a soft oval face with a gentle jaw. Sleepy, heavy-lidded brown
  eyes with lilac-grey tired shadows under them, and a small dark mole just
  below her right eye (on the left of the picture). Thin arched brows,
  rose-pink lips, pale skin.
- **Outfit:** a knee-length white lab coat worn open over a fitted teal-blue
  turtleneck, slim dark navy trousers cropped at the ankle, beige high-heeled
  pumps. Often a cigarette; omit it in the sprite.
- **Expression:** deadpan. Happy is a small wry smile; sad reads as exhausted.
- **The model doesn't know her face.** Named or not, two Krea runs drew the
  outfit right but a generic face: big wide-open eyes with violet irises
  ("lilac" leaked into the irises), a smile, a fringe across the forehead.
  Her base keeps Krea's body; her face and the top of her hair are redrawn by
  Nano Banana on the head close-up (HEAD_FIX in tools/fix_edges.py), and her
  hair is shifted +9 degrees toward the anime's brown (HAIR_SHIFT).

## gojo — Satoru Gojo (teacher)
Very tall, lean. White hair, spiky, swept up and back. BLACK BLINDFOLD over the eyes (a wide cloth band),
so expression is mouth + brow-line + head tilt only. Big confident grin as default. Long dark high-collared
jacket (uniform-like, longer than the students'), dark trousers, dark boots. Hands in pockets.

## yaga — Masamichi Yaga (principal)
From his official design sheet and anime stills in `references/characters/yaga/` (2026-09-28).
- **Age:** 47. He collects sunglasses and likes cute things (his dolls).
- **Build:** very large, broad and heavily muscled, with a thick neck and tan skin.
- **Hair:** dark brown, the sides shaved short and grey, the top a short spiky
  flat-top standing up.
- **Face:** narrow rectangular sunglasses with thin dark frames and dark red
  lenses, always on. A goatee: the moustache's ends curve down around the
  mouth to a short pointed chin beard. Heavy square jaw, deep lines.
- **Outfit:** a black zip-up jacket with a high stand collar zipped to the
  throat and a thin silver zip down the middle, loose black trousers and black
  shoes. There is also a training look (grey T-shirt, taped wrists), which
  could be an alternate outfit.
- **Expressions:** stern; happy is the beard moving. His eyes are behind the
  sunglasses, so his expressions live in his brows, mouth and beard, like Gojo's.

## ijichi — Kiyotaka Ijichi (assistant manager)
Neat black hair combed back/side-parted, rectangular glasses, pale, permanently anxious. Black business
suit, white shirt, dark tie. Slight stoop, hands clasped. Surprised and sad are his home expressions.

## utahime — Utahime Iori (Kyoto teacher; used later)
Long dark purple-black hair with a ribbon, straight fringe. A SCAR across the bridge of her nose (a short
diagonal line). Brown eyes. Red-and-white miko-style outfit: white top with red hakama. Prim, irritable.

## sana — Sana Torii (the friend from the East Wing; original)
Same age as the player. Black hair in a low ponytail, straight fringe, dark eyes, small round face.
Ordinary high-school uniform of a DIFFERENT school: grey blazer, white shirt, red ribbon/tie, grey pleated
skirt. Bright, a little reckless; after the wipe, oddly serene. Happy is her default.

## mc — the player (original)
Violet-tinted dark hair, medium length, swept to one side, a lock falling between the eyes. Grey-violet
eyes. Slim, average height. Starts in the Yotsuka High uniform (dark blazer, white shirt, dark tie) —
this is the pre-campus look; a second variant "mc_jjk" in the Jujutsu High uniform is used on campus.
Expression default: watchful. Make them look like someone who notices things.

## Curses (keep abstract — do not humanise)
curse_small: pond-scum green, too many joints, a mouth that goes round the side of the head, two eyes.
curse_big: four metres of accumulated mass with faces in it, pink-red eyes. Existing amorphous style is fine.
