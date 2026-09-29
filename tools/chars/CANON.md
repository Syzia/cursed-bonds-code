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
From the anime stills and official art in `references/characters/maki/` (2026-09-28).
- **Age:** 19 in this game, a year above the first-years.
- **Hair:** very dark teal-green, a muted blue-green (the references measure
  hue 171-184 degrees) that reads almost black in shadow. A high ponytail tied
  with a dark band, straight bangs across the forehead, and long straight
  locks framing her face down to the jaw.
- **Face:** sharp amber-gold eyes with heavy upper lids, thin straight brows.
  Thin **silver wire-framed** glasses with narrow oval lenses, not round
  red-brown ones: she needs them to see curses.
- **Arc 1 outfit, from the full-body references:** the navy uniform jacket
  with a high standing collar, the white shirt collar showing, fastened at the
  side with one gold button; a fitted navy skirt just above the knee; loose,
  slouchy white socks; brown lace-up ankle boots. Omit the weapon. Tall and
  athletic.
- **Expressions:** she rarely smiles; "happy" is a smirk.
- **Backdrop: magenta, not green.** Her hair would key away on Krea's muted
  green: a stress test lost 82% of dark green hair. fix_edges.start() moves a
  magenta render onto pure green for the rest of the pipeline.
- **Later look (Shibuya onward):** burn scars, short hair, and later no
  glasses. Add it as a second sprite set the game switches to from a story
  flag, so scripts keep saying `show maki angry`.

## panda — Panda (2nd year)
From the official art and stills in `references/characters/panda/` (2026-09-28).
- **What he is:** an actual giant panda, about 2 m tall with his ears, stocky,
  standing upright like a person.
- **Clothes: none.** The old note that he wears the uniform jacket was wrong.
  The references show only his fur. In fights he wears red or blue wrist cuffs
  with panda faces; in one still, an "I ♥" armband.
- **Markings:** a white head with small round black ears, black oval eye
  patches slanting toward the nose, small dark eyes inside them, and a few fur
  lines above the eyes for brows. A black nose, a short muzzle. A black band
  over the shoulders and across the upper chest, black arms with claws, a huge
  round white belly, and short black legs.
- **Sprite pose:** arms hanging at his sides. The official pose raises a paw,
  but that makes him too wide for the 760 px canvas at full height.
- **Height:** 200 cm drawn, ears included: the tallest of the cast, the height
  the game is scaled to. He has no chin, so he isn't measured chin to soles.
- **No skin:** his face is white fur, so face masks find it by fur, not skin.
- **Expressions:** kind and expressive. Happy is a broad smile; angry shows
  small fangs.

## toge — Toge Inumaki (2nd year)
From the official art and stills in `references/characters/toge/` (2026-09-28).
- **Age:** 19 in this game, like Maki.
- **Hair:** pale silvery ash-blond, almost white. In season 1 it is a neat
  short cut with a straight fringe; the game uses his spikier look (see below).
- **Face:** calm, sleepy violet-grey eyes with heavy lids, thin light brows,
  pale skin.
- **Uniform:** the navy jacket with a very tall, loose funnel collar zipped up
  and folded over his mouth and nose, fastened at the side with one gold
  button, with white shirt cuffs. Baggy navy trousers cropped above the ankle,
  black socks, white high-top sneakers with a folded cuff.
- **Seal marks:** the "snake-and-fangs" crest is a small ring at each **corner
  of the mouth**, joined to it by a short line like a fang, plus a mark on his
  tongue. With the collar up they are hidden. The old note that they show on
  his cheeks was wrong.
- **The game's look (the user's choice, 2026-09-28): spiky hair and visible
  seal marks.** The collar sits under his chin so the marks at the corners of
  his mouth show. Krea drew the body (with the collar under the chin, whatever
  the prompt said); Nano Banana redrew the head with spiky hair, the marks, a
  slimmer face and sleepy eyes (HEAD_FIX in tools/fix_edges.py).
- **Expressions:** eyes, brows and mouth; the marks stay at the mouth's corners.

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
- **What the base model got wrong (2026-09-28):** named, Krea drew his body,
  jacket and hair right, but his skin pale peach, his goatee as a faint chin
  tuft, and his sunglasses tall, with thin silver frames and glossy pink
  lenses. His skin is graded to the sheet's tan (SKIN_TARGET, so face and fists
  match), and Nano Banana redraws the goatee and the slit-like black-framed
  glasses (HEAD_FIX).

## ijichi — Kiyotaka Ijichi (assistant manager)
From the anime close-ups and the manga colour art in `references/characters/ijichi/` (2026-09-29).
- **Age:** late twenties.
- **Hair:** neat, straight, black with a faint blue sheen. Short at the back,
  with a straight fringe to the eyebrows parted slightly off-centre, and the
  sides over the tops of the ears. It isn't combed back, as the old note said.
- **Face:** from the anime close-ups: narrow rectangular glasses with thin
  black frames, a long, narrow, sharp face, calm, slightly tired eyes, thin
  brows, pale skin. Tall, slim and long-legged.
- **Outfit, the game's look (the user's choice, 2026-09-29): "a little bit of
  style".** From the manga colour art the user picked: a sharp, sleek,
  slim-fitting **black** suit with narrow lapels closed with one button, a
  crisp white shirt, a slim black tie, a silver wristwatch, slim trousers
  tapered to the ankle, and polished pointed black shoes. Not the anime's
  frumpy charcoal suit and maroon tie, whose renders the user rejected.
- **Pose:** tall and relaxed, adjusting the watch on his left wrist at chest
  height, as in that art, but facing the viewer. Cool and composed, not
  hunched.
- **Expressions:** permanently anxious. Surprised and sad are his home
  expressions; happy is relief. His glasses may split the face mask the way
  Yaga's did, in which case use `facemask.py --below-hairline`.
- **Placeholder:** the prologue's father and Kurose borrow
  `images/char/ijichi.png`, so keep that file.

## utahime — Utahime Iori (Kyoto teacher; used later)
From her official design sheet and stills in `references/characters/utahime/` (2026-09-28).
- **Age:** 31, per the sheet's profile. Gojo is her junior, and she is often
  harsh with him.
- **Hair:** long, straight, very dark purple-black with an indigo sheen, past
  the shoulders to mid-back. A long, choppy, wispy fringe to the eyes and long
  locks framing the face. The upper part is tied at the back of the head with
  a large cream-white ribbon bow, whose loops show above her head from the front.
- **The scar:** a **wide band** across the middle of her face, from cheek to
  cheek over the bridge of the nose just below the eyes. Rough pinkish-brown
  skin with faint scratch lines. The old note ("a short diagonal line") was
  wrong.
- **Face:** a mature long oval face, sharp brown eyes with heavy lids.
- **Outfit:** a shrine maiden's white kimono top with a crossed collar and
  wide hanging sleeves, and red pleated hakama to the ankles, tied high with
  a big front bow. Brown heeled ankle boots. A casual look also exists (cap,
  black off-shoulder top), unused.
- **Pose:** hands clasped in front of her waist, as on the sheet.
- **Figure and face (the user's direction, 2026-09-28):** she's 31, so draw
  her as a mature, feminine woman: a full bust, a slim defined waist and
  rounded hips under the kimono top; a soft oval face, long lashes, full lips.
  The first render drew her flat and plain, with no scar and a huge bow on top
  of her head. The face gets a Nano Banana head redraw after the base (HEAD_FIX),
  which also adds the scar if the base drops it.
- **Expressions:** prim and composed. Warm with her students, so happy is a
  real smile; angry is fuming irritation, her reaction to Gojo.

## sana — Sana Torii (the friend from the East Wing; original)
Designed with the user (2026-09-29), from the Reze references in `references/characters/sana/`.
- **Who she is:** the player's best friend since they were three. Funny,
  opinionated, a little reckless, teasing. She has "a thing to tell you" and
  dies in the alley in chapter one. Reze (Chainsaw Man, also MAPPA) dies in an
  alley on the way to meet the boy, which makes her a deliberate homage.
- **Age:** 18, the player's classmate at Yotsuka High.
- **Face and hair, from Reze:** a short dark purple (indigo-violet) bob with
  loose strands across her face and a small bun at the nape, large bright
  green eyes, a gentle, teasing smile, a faint blush. The user kept the
  purple; the player's hair will change colour instead.
- **Her own:** a small **white daisy hair clip** above her left temple, a
  nod to Reze's flower and a memento the story can reuse after the alley.
  No choker: Reze's grenade-pin choker stays Reze's.
- **Outfit:** the Yotsuka High uniform: a grey blazer worn open, a white
  shirt, a red ribbon bow, a grey pleated skirt just above the knee, black
  knee socks and brown loafers. The player's prologue uniform matches (the
  boys' version with a tie).
- **Backdrop: magenta.** Her darker green eyes measured only 49 from Krea's
  muted green, against a cutoff of 45. Krea's magenta came back rose,
  (231, 59, 140), and her lavender hair highlights lean toward it almost as
  far as the key's cut, so the first move onto green keyed them half out.
  keysprite's magenta key now also measures lean along the screen's own hue
  (her hair leans blue, the screen red). Moved onto pure green, nothing more
  than 3 px inside her outline changed.
- **Expressions:** happy is her default. After the wipe, oddly serene.

## mc — the player (original)
Kaito Amagiri by default (the player can rename him): 18, Sana's classmate
at Yotsuka High, then a first-year at Jujutsu High.
- **A Sung Jin-Woo type** (the user, after the first renders): "the MC
  always has to be good looking". Named to Krea for the face, hairstyle,
  build and bearing, as Reze was for Sana: strikingly handsome, sharp
  narrow eyes, a defined jaw, lean and athletic, cool and composed.
- **Hair: dark brown** (the user chose dark ash brown), not Jin-Woo's
  black, which would make him a Megumi double in shared scenes, and not
  purple like Sana's. Say "dark chocolate brown": "ash" and "grey
  highlights" came back charcoal grey, (75, 84, 85). Grey-violet eyes.
- **Two outfits, one face.** The base is rendered in the Jujutsu High
  uniform (dark navy, stand-up collar, gold swirl buttons): most of the
  game is on campus, and the model draws it best by name. The Yotsuka High
  version (grey blazer with Sana's dark green piping, white shirt, red tie
  to match her ribbon, grey trousers, brown loafers) is the same picture
  with the clothes swapped, so the face, and every expression, is shared.
- **Backdrop: magenta**, for the Yotsuka blazer's dark green piping.
- **Expression default:** watchful. Someone who notices things. His happy
  is a warm, confident smile, his anger cold.
- **Done 2026-09-29:** render #1 with a head redraw (a neat side-swept dark
  brown cut, (71, 53, 44), eyebrows showing), drawn 179 cm (standing 172).
  Yotsuka outfit: box 1, the blazer buttoned. He wears it until the flag
  `settled_in` (Arc One's opening), then the Jujutsu High uniform.

## Curses (keep abstract — do not humanise)
curse_small: pond-scum green, too many joints, a mouth that goes round the side of the head, two eyes.
curse_big: four metres of accumulated mass with faces in it, pink-red eyes. Existing amorphous style is fine.
