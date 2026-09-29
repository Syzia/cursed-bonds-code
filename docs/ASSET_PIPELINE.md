# Asset pipeline — how the sprites get made

Started 2026-09-14, after the first Comfy Cloud render came back usable. The
research report from that day is archived (see the end of this file).

One question the research raised and this repo can answer: the cast is eleven
canon Jujutsu Kaisen characters plus two originals (the player and Sana), and
the under-eye marks that Krea-2 dropped are canon. So the Danbooru-tag argument
for a local anime checkpoint is real, not hypothetical — see tools/chars/CANON.md.

## Making a character: the recipe (2026-09-28, after all nine campus regulars)

Yuji, Megumi, Nobara, Maki, Toge, Shoko, Yaga, Gojo and Panda are done, six
expressions each, and since then Utahime, Ijichi, Sana (the first original)
and the player, Kaito (two outfits sharing one face, see step 8), too. The
same steps, and the fixes that turned out to be needed, cover every one of
them.

1. **References.** Put 2–5 in `references/characters/<name>/`. A full-body
   shot and a face close-up are the two that matter; an official design sheet
   beats everything else.
2. **Base picture:** `tools/chars/prompts/<name>.txt`, then
   `make_base_workflow.py <name>`. This runs on Comfy Cloud, because Krea-2
   Turbo needs a big NVIDIA card; it's about 36 GB unpacked on a Mac.
   - **Name** the character and MAPPA's style, then describe them. Named
     prompts get the anime's look; pure descriptions come out generic. Never
     name them to Nano Banana or Seedream.
   - Say nothing about height. A full-frame "shorter" becomes child
     proportions; `HEIGHT_CM` sets height instead.
   - If anything on them is **green** (Maki's hair), render on magenta.
     Krea's magenta comes back rose, and purple hair leans toward it (Sana),
     so the magenta key also measures lean along the screen's own hue. Check
     a move onto green by comparing pixels whose colour is far from the
     backdrop, not with the key's own measure: nothing inside the outline
     should change.
   - The move onto green mixes each soft edge pixel so the green key reads
     back the same alpha, and strips the screen's colour from the 2 px just
     inside the outline. Before that (fixed 2026-09-29) both magenta
     characters, Maki and Sana, had a green and maroon fringe. Check an
     outline at 4x zoom on a dark and a light ground.
3. **Repair the base** (`fix_edges.py --prepare <name>`, one `edges.json` Run
   in the local ComfyUI). Add the character to `BASES` first. Every option is
   per character:
   - **Cut edges, any side:** Krea overflows the frame on almost every render.
   - **`HEAD_FIX`:** the model draws the outfit right but the face generic
     (Shoko), or misses details (Yaga's goatee and glasses), or you want a
     different look (Toge's spiky hair and seal marks). `HEAD_MARGIN` and
     `HEAD_ROOM_ABOVE` give hair that changes shape room to grow.
   - **`HAIR_FIX`** restyles hair along its whole length, and `HAIR_TARGET`
     grades its colour to the references. Nano Banana overshoots colour.
   - **`BODY_FIX`** reshapes a build (Yaga came out fat) and keeps the head.
   - **`SKIN_TARGET`** grades skin to the official art (Yaga's tan).
   - **Combining two head-fix versions** (Utahime: box 3's face with box 1's
     scar): `tools/transplant_scar.py` moves a detail pixel by pixel, because
     both close-ups are lined-up crops of the same base. Don't ask Nano Banana
     to combine two pictures: given both, it returned the reference whole.
   - **Which version is which:** output file numbers follow completion order,
     not the order of the boxes. Map them through ComfyUI's /history before
     acting on "the first one".
4. **Measure the drawn height** chin to soles, then set `HEIGHT_CM`. Include
   heels, ponytails and spikes. A very wide build gets `CANVAS_W` (Panda: 880),
   so the fit doesn't squeeze it. Then run `fix_edges.py <name> --install` and
   retire the placeholder `image <name>` line in `jjk_defs.rpy`.
5. **Face mask** (`facemask.py`), generated rather than hand-drawn:
   `python3 tools/facemask.py "~/Desktop/JJK Game images/<render>.png" <name>`
   writes `masks/<name>_face.png` beside the render.
   - default: follows the skin. Skin is found by colour: where green sits
     between blue and red separates facial skin (0.39-0.46 on the first
     render) from salmon-pink hair (0.08-0.11) and a red hoodie (0.01-0.04),
     and a paleness test keeps ginger hair out. The top is raised by the
     feather's width so the eyebrows move at full strength, and the edge is
     pulled in so the jaw line, which the key cuts along, is never redrawn.
   - `--below-hairline`: glasses or a blindfold split the face
   - `--fur`: Panda
   Overlay the mask and look at it before spending anything.
6. **Expressions:** `composite_face.py --prepare`, then `make_edit_workflow.py
   <name> --only happy,serious,sad,angry,surprised` (about $0.80), then
   `composite_face.py` on each result, then `gen_sprite_defs.py`.
   - `CHAR_EXPRESSIONS` holds per-character wording: Gojo and Yaga have hidden
     eyes, Maki's happy is a smirk, Shoko is deadpan, Panda has fur brows.
   - `CHAR_KEEP` protects glasses, blindfolds and marks.
7. **Check every time:** zero body pixels differ from the neutral below the
   face, lint is clean, and the cast line-up still reads as one show.
8. **A second outfit** (Kaito, 2026-09-29): `OUTFIT_FIX` in fix_edges.py
   redraws the clothes on the finished working base and pastes everything
   but the head, so the face is pixel-identical and the five expressions
   are made once, then copied onto the other outfit's base. The outfit is a
   character of its own for the tools (`mcyotsuka`); in the game,
   `OUTFITS` in gen_sprite_defs.py makes the owner's images a
   ConditionSwitch on a story flag, so scenes just `show mc`.
   - Anything pasted from an edit model sits on its vivid green,
     (10, 249, 10). keysprite gives solid pixels near the outline of a vivid
     screen their own ramp and despill, and treats a sealed sliver of that
     green as backdrop. Look for green on the outline and in gaps between
     a hand and a leg.

Typical cost per character, besides the base run on the Comfy Cloud plan:
$0.50–1.50 of repairs and $0.80 of expressions, at Nano Banana Pro's
$0.16 a picture.

## The character pass: grounding and light (done 2026-09-23)

Spotted by standing Yuji and Megumi in the first real background
(tools/fitcheck.py), and fixed once the campus backgrounds were done:

1. **Clipped soles: fixed.** Yuji's and Megumi's left shoes (on the right of the
   picture) ended in a straight cut with a green fringe. Both base renders had
   the feet touching the bottom edge. keysprite's QA flagged it at the time, and
   it was dismissed as "under 1% of height". At game size it is plainly visible,
   so a QA flag for a clipped figure should be treated as blocking.
   - `tools/fix_feet.py` pads the base with backdrop green and sends a 16:9
     close-up of the feet to Nano Banana, which finishes the sole.
   - It then lines the result up on the trousers (scale 1.0025, shift 0) and
     pastes only the clipped foot into all six expressions, whose feet are
     pixel-identical.
   - About $0.64 for both characters, two versions each.
   - Future bases: re-roll any candidate the QA flags.
2. **Floating: fixed.** Every generated sprite now has a soft contact shadow
   under its feet (`lit_sprite()` in `game/lighting.rpy`).
   - The feet are measured from the neutral pose by `gen_sprite_defs.py`, which
     also draws `images/fx/contact_shadow.png`.
   - The shadow is subtle, because the feet stand only about 20px above the
     bottom of the screen.
3. **Lighting: fixed.** Every character image is wrapped in a lit transform.
   - The light is set whenever a background goes up on the master layer, through
     a `config.show` hook: from the place and hour for `scene expression graded_bg()`,
     or from the background's name for `scene bg ...`.
   - At night in the courtyard the characters are moonlit blue, at sunset on the
     rooftop they're warm, and in Yaga's office they're candlelit.
   - The tables are `OUTDOOR_LIGHT`, `INDOOR_LIGHT`, `PLACE_LIGHT` and `BG_LIGHT`.
     Add a row when a new painted evening or night picture, or a new story
     background, lands.

---

## What actually works (updated 2026-09-22, after Yuji and Megumi)

**Base picture:** Krea-2 Turbo on Comfy Cloud, from `tools/chars/prompts/<character>.txt`
via `make_base_workflow.py`. If the body is right but the head isn't, redraw only
the head: `facemask.py --head` + `make_workflow.py --head` (Megumi's took one Run).

**Expressions: an edit model, not inpainting.** Masked inpainting with Krea-2
worked for Yuji and failed completely for Megumi. Four rounds, denoise up to 0.78,
a wider mask, shorter prompts: his face was repainted at full strength every time
(the raw pixel change matched Yuji's) and came back bored every time. What worked
first try was **Nano Banana Pro** (Gemini 3 Pro Image, a paid partner node, about
$0.16 an edit), given a **head close-up** rather than the full sprite:

1. `python3 tools/composite_face.py --prepare <base.png> <character>`: head close-up, 1024 square
2. `python3 tools/make_edit_workflow.py <character>`: drag-in workflow, one row per expression
3. Run it in ComfyUI. Results land in `~/ComfyUI-Shared/output`.
4. `python3 tools/composite_face.py <base.png> <edit.png> <character> <expression>`
   lines the edit up with the sprite and pastes only the face through the face mask

On Megumi, Nano Banana Pro kept the geometry exactly (scale 1.000, shift 0) and
changed the colour by about 2 levels. None of the body pixels changed.

**Seedream refuses these characters.** Its output filter rejected Megumi with "the
output image may be related to copyright restrictions". Firing eight partner
requests at once also hits rate limits: they queue and retry, which is slow but
still works.

---

The 2026-09-14 research report and the superseded inpainting procedure
("Running step 1") are in
[archive/2026-09-14-asset-research.md](archive/2026-09-14-asset-research.md).
