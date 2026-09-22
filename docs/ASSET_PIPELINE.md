# Asset pipeline — how the sprites get made

Researched 2026-09-14, after the first Comfy Cloud render came back usable.
Every load-bearing claim below was independently fact-checked; where a figure
could not be verified it says so rather than guessing. Two file sizes were
re-verified directly against the HuggingFace API from this machine:
`krea2_turbo_nvfp4` is 7.67 GB and NVIDIA-Blackwell-only, and
`Illustrious-XL-v2.0` is 6.94 GB and ungated.

One question the research raised and this repo can answer: the cast is eleven
canon Jujutsu Kaisen characters plus two originals (the player and Sana), and
the under-eye marks that Krea-2 dropped are canon. So the Danbooru-tag argument
for a local anime checkpoint is real, not hypothetical — see tools/chars/CANON.md.

## Queued for the character pass (after backgrounds)

Spotted by standing Yuji and Megumi in the first real background (tools/fitcheck.py):

1. **Clipped soles.** Yuji's right shoe and Megumi's right boot end in a straight
   cut. Both base renders had the feet touching the bottom edge. keysprite's QA
   flagged it at the time, and it was dismissed as "under 1% of height". At game
   size it is plainly visible, so a QA flag for a clipped figure should be
   treated as blocking. Fix: pad the base render with green below the feet, have
   the edit model complete the shoes, and composite only a feet mask back, in
   the same way composite_face.py does for faces. Future bases: re-roll any
   candidate the QA flags.
2. **Floating.** There is no shadow where they stand. Fix in the engine: a soft
   ellipse under each sprite, scaled with it, drawn under the character layer.
3. **Lighting by time of day.** The game tints backgrounds for evening and night
   but not sprites, so at night the characters glow. Fix in the engine: a matching
   per-period tint on sprites.

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

## Running step 1

The face mask is generated, not hand-drawn:

```bash
python3 tools/facemask.py "~/Desktop/JJK Game images/<render>.png" <character>
```

It finds the face by colour — green being at least a quarter of the way from
blue to red, which separates facial skin (0.39-0.46 on the first render) from
salmon-pink hair (0.08-0.11) and the red hoodie (0.01-0.04) with a wide margin
either side — insets from there, and draws a superellipse rather than a plain
ellipse so the eyebrows are inside the mask. It prints the exact ImageCrop
x/y/width/height to reuse in ImageCompositeMasked.

Then build the workflow itself:

```bash
python3 tools/make_workflow.py "~/Desktop/JJK Game images/<render>.png" <character>
```

It reads the model, sampler settings and prompt out of the render's own PNG
metadata (ComfyUI embeds the full workflow in every image it saves) and writes
`<character>_expressions.json`: one row per expression, each swapping only the
expression words, each composited back over the untouched original. Drag it
onto the Comfy Cloud canvas, upload the render and mask into the two Load Image
boxes, press Run once.

Then `python3 tools/keysprite.py --batch <folder>` ingests whatever comes back.

---

# RECOMMENDATION: Do not install local ComfyUI now. Stay on Comfy Cloud.

**No — don't spend today on the local install.** The thing standing between you and 78 sprites is not model access, it's a workflow you haven't built yet: masked face-oval inpainting with lossless composite-back. That workflow is the entire answer to "can the same face survive 6 expressions," it is buildable from **pure core ComfyUI nodes**, it runs unmodified on Comfy Cloud today, and it iterates in ~20–30 seconds per attempt there versus an estimated **8–15+ minutes** per attempt on this M2. You need 200–400 generations to converge. That is roughly one afternoon of cloud time against **50–100 hours** of a fan-limited 13" laptop pinned at 100%. Build the workflow on Cloud, prove it on one character, and only then decide whether local is worth anything.

Also: your 7 GB file is not the whole download and may be the wrong file entirely. Details in §6.

---

## 1. What actually solves expression consistency (this is the whole report)

**Inpaint only a face oval, then composite the untouched original pixels back over the full sprite.** This is categorically different from every other technique because it is a *pixel-preservation guarantee*, not a quality hope.

I read core ComfyUI's `comfy_extras/nodes_mask.py`. `ImageCompositeMasked` clones the destination and computes `mask*source + (1-mask)*destination`. **Where the mask is 0, the destination pixel is returned byte-for-byte.** Pixels outside the composited rectangle are never touched at all. So:

- Body, clothing, hair silhouette, and the flat chroma green are **bit-identical across all 6 variants**.
- You chroma-key **once**, on the base sprite. The other five inherit an identical alpha matte by construction.
- No edge crawl, no sub-pixel registration jitter when Ren'Py cross-fades expressions in place.

**One caveat the survey got wrong:** the guarantee only holds with a hard (0/1) mask boundary. `composite()` bilinearly interpolates the mask, so a feathered edge produces fractional values in a transition band, and those pixels *do* get blended. Fix: shrink the oval so it sits ~15 px inside the hairline, then feather inward. The entire feather gradient then lies on skin, and the mask is exactly 0 over all hair, body, and green.

**What this beats, and why:**

| Technique | Verdict |
|---|---|
| Fixed seed + expression clause swap | **Fails.** Seed fixes the initial noise tensor, not the denoising trajectory — conditioning changes the cross-attention maps from step 1 and compounds. You get correlated layout with a different face. Worse here because the face is only ~100–130 px tall in a 760×1400 frame, which is the exact regime FaceDetailer exists to fix. |
| img2img at low denoise, whole image | Whole frame round-trips VAE encode/decode. Green shifts by a few non-uniform RGB values per variant → different matte per expression → shimmering edges. |
| IPAdapter / FaceID / InstantID | Built on ArcFace photo embeddings; weak on stylised anime faces. Still regenerates everything. |
| ControlNet openpose/lineart | Locks pose, not identity, not pixels. Lineart actively drags the old mouth back in. |
| Character LoRA | Solves "draw this character in a new pose," not composite-matching. Your base sprite's own pixels are a *stronger* identity anchor than any LoRA — exact rather than statistical. |
| Qwen-Image-Edit-2509/2511 (on Cloud) | Excellent expression semantics but has documented, unfixed **pixel drift** — output shifts/zooms a few px. Usable only *inside* the mask with composite-back. |

**Correction to one claim in the survey:** ComfyUI-Inpaint-CropAndStitch is genuinely **not** on Comfy Cloud (I trust the fact-check: 36 supported packs, verified by parsing the page, and custom-node install is disabled). But **ComfyUI-Impact-Pack *is* supported**, and its `FaceDetailer` / `DetailerForEach` do the same crop→inpaint-at-higher-res→paste-back cycle with the same preservation property. So you have two routes on Cloud, not one. `ComfyUI-RMBG` and `comfyui_face_parsing` are also supported and can auto-generate the face mask.

**Your dropped under-eye marks: stop trying to generate them.** The model dropped them once and will drop them inconsistently again. Make them a **static PNG overlay** composited at fixed coordinates — either in your Python tool or as an `always` layer in Ren'Py's `layeredimage`. Fixed facial markings are static assets, not generated details. This is free and permanent.

---

## 2. The graph, concretely (core nodes only — identical on Cloud and local)

```
LoadImage  "gojo_base.png"        (760x1400, approved, flat green)
LoadImage  "gojo_facemask.png"    (760x1400, white oval on black, authored once per character)
      |
      +-- ImageToMask (channel: red) --------------------------+
      |                                                         |
ImageCrop(base)     x=188 y=96 width=384 height=384             |
      |             <-- record x,y EXACTLY, reuse below         |
ImageScale 384 -> 1024 (lanczos)                                |
      |                                            MaskToImage --+
VAEEncode                                          ImageCrop  (same x,y,w,h)
      |                                            ImageScale 384 -> 1024
      +----> SetLatentNoiseMask <-----------------  ImageToMask
                    |                                  |
                    |                             GrowMask (expand 4)
                    |                             FeatherMask (8)
                 KSampler
                    |
                VAEDecode
                    |
            ImageScale 1024 -> 384 (lanczos)
                    |
            ImageCompositeMasked
              destination   = LoadImage "gojo_base.png"   (full 760x1400, untouched)
              source        = the 384 result
              x, y          = SAME x,y as ImageCrop
              resize_source = false
              mask          = the ORIGINAL unscaled 384 face-oval mask
                    |
                SaveImage
```

**Mask authoring rules (highest-leverage decision in the project):**
- The white oval must sit **strictly inside the hairline**. It must never touch the hair silhouette or the green. Everything outside it is then provably never sampled.
- Inset the oval ~15 px from the hairline, *then* feather 8 px — so the feather band is entirely on skin.
- Cost: you cannot change hair or push the jaw past the chin line. That's fine — VN expression sheets change eyes, brows, mouth and blush, all of which live inside the oval.

**Sampler settings:**

| | Krea 2 Turbo | SDXL / Illustrious |
|---|---|---|
| steps | 8 | 26–30 |
| cfg | **1.0** | 5.0–7.0 |
| sampler / scheduler | euler / simple | dpmpp_2m / karras |
| negative prompt | **does nothing** — CFG 1.0 means there is no negative lever. Real limitation; plan around it. | works normally |

**Denoise ladder (the single dial):**
- **0.35–0.45** — neutral → smile, worried, annoyed, sad. Identity unmistakably preserved; existing under-eye marks survive from source pixels.
- **0.50–0.60** — open-mouth shout, eyes squeezed shut. Identity starts to wobble; inspect every output.
- **>0.70** — different person. Don't.

**Seed:** vary it per expression. Fixing it buys nothing; the source latent is doing the identity work.

**Prompt:** keep the full character description **byte-identical** across all six; change only the expression clause, and describe the end state rather than a delta.

**If you end up on SDXL/Illustrious**, use high-count Danbooru tags (counts verified live against the Danbooru API today): `smile` 4.17M · `blush` 4.10M · `open_mouth` 3.52M · `closed_eyes` 1.06M · `parted_lips` 745K · `grin` 358K · `tears` 296K · `expressionless` 181K · `frown` 154K · `half-closed_eyes` 145K · `clenched_teeth` 106K · `surprised` 74K · `angry` 62K · `wide-eyed` 53K. Prefer `expressionless`/`half-closed_eyes` over `serious` (39.8K) and `frown`+`tears` over `sad` (17.9K) — the low-count tags are noticeably weaker levers.

---

## 3. The Ren'Py optimization — take it, it's free

You probably should not ship 78 full 760×1400 RGBAs. Since the face oval is the only region that differs, export **13 body PNGs + 78 small face plates (~384×384)**:

```renpy
layeredimage gojo:
    always "gojo_body"            # 760x1400, chroma-keyed ONCE
    always "gojo_marks"           # static under-eye marks overlay, fixed offset
    group expression:
        attribute neutral default "gojo_face_neutral"   # ~384x384 at fixed offset
        attribute smile   "gojo_face_smile"
        attribute angry   "gojo_face_angry"
        ...
```

Three wins: the body is *literally the same file*, so composite-matching is tautological rather than merely guaranteed; disk and texture memory drop ~10x; and redrawing a body updates all 6 expressions for free. This falls out of the face-oval mask strategy at zero extra cost.

---

## 4. Iteration economics

78 finals = 13 base generations + 65 inpaints. At a realistic 3–5x retry factor, **234–390 runs**.

**Comfy Cloud.** Billing rate is genuinely disputed across Comfy's own sources — the pricing page says 736.39 credits/hr (0.2045/sec), the docs say 0.266/sec, and a docs PR raises it to 0.2732/sec. **Plan at 0.273/sec.** No measured Krea 2 Turbo wall-clock on Cloud exists anywhere I can verify; the nearest real datapoint is ~13 s sampling / ~20 s wall for one 1024² 8-step image on an RTX 3090, and Cloud runs a Blackwell RTX PRO 6000 (96 GB VRAM), which is much faster — but cold model load is billed too. Budget **20–45 s billed per run**.

- 400 runs × 30 s × 0.273 ≈ **3,280 credits**
- 400 runs × 45 s × 0.273 ≈ **4,910 credits**

Standard is $20/mo for 4,200 credits, Creator $35/mo for 7,400. **So: $20 probably covers it; $35 certainly does.** Top-up credits roll over up to a year. The free tier (400 credits/month, recurring, no card) is ~1,465 GPU-seconds ≈ **50–70 generations/month** — enough to prototype one character's full 6-expression loop, not the whole set. Note the earlier "$0.96 for the whole project" estimate was built on the lowest of three disputed rates plus an unmeasured 6 s/image; ignore it.

**Local.** 234–390 runs × 8–15 min = **31–98 hours** of continuous compute. The only traceable Apple-Silicon Krea 2 GGUF measurement is a **Mac mini M4, 32 GB, Q4_K_M: 6 min 27 s first image, 8–10 min thereafter** (17+ min on bf16). Your base M2 has fewer GPU cores, 24 GB instead of 32, and a single small fan. Treat 8–15 min as a reasonable expectation, explicitly **unbenchmarked on this exact machine**.

**The asymmetry:** face consistency is an iteration-count problem, and iteration is ~25x cheaper in wall-clock on Cloud. $20 buys more Krea 2 Turbo throughput than this M2 delivers in a month of running.

---

## 5. Is downloading reversible? Yes — almost entirely. Here is the one thing it forecloses.

**Low-risk, reversible, parallel-safe:**
- Disk: 788 GB free. A 16 GB download is 2 % of it.
- No system mutation. `uv venv --python 3.12` downloads its own standalone CPython into uv's cache; it never touches `/usr/bin/python3` (SIP-protected anyway), never changes your PATH default. The entire install is one deletable directory.
- Your Cloud account and credits are untouched. You can run both.
- **Workflows are portable both directions.** Graph A above is pure core nodes precisely so the same JSON runs in both places. Nothing you build on Cloud is wasted if you go local later, and vice versa.
- The download can run in the background while you work on Cloud. It costs bandwidth, not attention — *if* you don't start debugging it today.

**What it does cost:** attention, which is the scarce resource. The real risk is spending two days on GGUF forks and MPS dtype errors instead of authoring 13 face-oval masks, which is the actual blocker.

**The one genuine foreclosure:** if you go local on **SDXL/Illustrious**, you change model family, and the approved Krea 2 Turbo sprite's look cannot be matched — the whole 78-sprite set restarts from a different base. Going local on **Krea 2 Turbo GGUF Q4** keeps the architecture, but quantization changes outputs, so a Q4 local sprite will be close to but not identical with the cloud one. Neither is fatal; both are worth knowing before you commit.

---

## 6. If you download anyway — get the right files

Byte-verified sizes from the HuggingFace API for `Comfy-Org/Krea-2`:

| File | Size | Runs on M2? |
|---|---|---|
| `krea2_turbo_nvfp4` | 7.15 GiB | **NO — NVIDIA Blackwell only.** If this is your 7 GB, cancel it. |
| `krea2_turbo_fp8_scaled` | 13.14 GB | **NO on stock torch** — MPS cannot hold `Float8_e4m3fn` tensors at all |
| `krea2_turbo_bf16` | 26.28 GB | **NO** — exceeds 24 GB, swaps hard (measured ~31 GB resident on an M1 Max) |
| `krea2_turbo` GGUF **Q4_K_M** | **7.22 GB** (realrebelai) / **7.49 GB** (vantagewithai) | **Yes** — this is almost certainly your "7 GB", and it does work |
| `qwen3vl_4b_fp8_scaled` (text encoder) | 5.24 GB | **Unverified on MPS.** fp8 dtype is unsupported; you may need the bf16 (8.88 GB) or a GGUF TE quant instead. |
| `qwen_image_vae.safetensors` | 254 MB | Yes — **required**. The Flux VAE produces scrambled noise. |

**So the real download is 13–16 GB, not 7 GB**, plus ~2–3 GB of torch/deps. The 7 GB file is only the diffusion model.

**Install (run in Terminal.app, not through an agent):**

```bash
brew install uv                          # uv 0.12.11 available; Homebrew 6.0.22 already at /opt/homebrew
mkdir -p ~/AI && cd ~/AI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ~/AI/ComfyUI
uv venv --python 3.12                    # 3.9.6 is years below ComfyUI's floor; 3.12 > 3.13 because
source .venv/bin/activate                # the custom nodes you'll want are flagged as 3.13-fragile
uv pip install torch torchvision torchaudio   # macOS arm64 PyPI stable already includes MPS.
uv pip install -r requirements.txt            # ~130MB, no CUDA blob. Ignore any doc telling you
                                              # to use conda pytorch-nightly — that channel is dead.
python main.py --use-pytorch-cross-attention  # no xformers on Mac; this gives ~15-25% on M1/M2
```

**MPS sanity check — must be run by you in Terminal.app:**
```bash
python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"
```
Expect `2.14.0 True`. **If it prints `False`, do not conclude your Mac can't do MPS.** PyTorch maintainers have documented that coding-agent sandboxes produce a false negative here (pytorch/pytorch#177819; `CODEX_SANDBOX=seatbelt` flips it, and malfet explicitly names Claude-style sandboxes). Any MPS check I run for you via a tool call is unreliable. Separately, pytorch#167679 ("MPS unavailable on macOS 26") was closed 1h43m after filing — it was a macOS 26.0-only bug, fixed in 26.1; you're on 26.6.2. One follow-up comment claims it still reproduces for some users on 26.3.1, so verify rather than assume.

**Directory tree:**
```
ComfyUI/models/checkpoints/       SDXL/Illustrious .safetensors
ComfyUI/models/unet/              GGUF diffusion models
ComfyUI/models/text_encoders/     qwen3vl_4b_*
ComfyUI/models/vae/               qwen_image_vae.safetensors, sdxl_vae.safetensors
ComfyUI/models/loras/
ComfyUI/custom_nodes/
```

**GGUF loader — mainline will not work.** `city96/ComfyUI-GGUF` throws "Unexpected architecture type" on krea2 (issue #464, open since 2026-06-24). Use the fork:
```bash
git clone https://github.com/molbal/ComfyUI-GGUF ~/AI/ComfyUI/custom_nodes/ComfyUI-GGUF
```
(`RealRebelAI/ComfyUI-GGUF_KREA-2` also works.) Load via the **Unet Loader (GGUF)** node.

**If instead you take the SDXL route** (proven MPS path, 60–120 s/image, but a different art style from your cloud sprite): `Illustrious-XL-v2.0.safetensors` = 6,938,040,674 bytes (6.94 GB, HF `OnomaAIResearch/Illustrious-XL-v2.0`, ungated) or WAI-illustrious-SDXL v17.0 ≈ 6.46 GB (Civitai 827184) → `models/checkpoints/`. Add `sdxl_vae` fp16-fix (0.33 GB) → `models/vae/`. **Generate at 768×1408 and downscale to 760×1400** — 760×1400 is a 1:1.84 aspect that falls in the gap between SDXL's trained buckets (768×1344 and 640×1536), and off-bucket generation degrades anatomy, which is exactly wrong for full-body sprites. Note that Illustrious open weights stop at **v2.0** — v3.0/v3.5/v3.6 are platform-gated on Stardust/Shakker/TensorArt and cannot be downloaded. Don't wait for them.

---

## 7. Will not work on Apple Silicon — do not waste time on these

- **`krea2_turbo_nvfp4` (7.15 GiB) and any MXFP8 build** — NVIDIA Blackwell formats. Zero chance.
- **`krea2_turbo_fp8_scaled` (13.14 GB) on stock torch** — MPS has no `Float8_e4m3fn` support (ComfyUI issues #8785, #9263, #16107). Community shims exist (`ComfyUI-AppleSilicon-FP8`) and claim to need torch 2.11+, but that is **unproven on a base M2** — one community writeup says fp8 works, another says it fails outright. Treat as unsettled; don't build a plan on it.
- **`krea2_turbo_bf16` (26.28 GB) on 24 GB** — will not fit, swaps violently.
- **Krea 2 Raw** — 52 steps; on an M1 Max/64 GB it took 47 minutes and output a pure black image (NaN in VAE decode). Never use it on Apple Silicon.
- **Mainline `city96/ComfyUI-GGUF` for krea2** — architecture unrecognized. Fork required.
- **`batch_size` > 1 on MPS for Krea 2** — only one frame in the batch denoises correctly, the rest come out static. Queue N separate jobs at batch 1.
- **`LoraLoaderModelOnly` at strength 0.0 on MPS** — NaNs the model, renders pure black. **Bypass the node; never zero it.** This is nasty because zeroing is the obvious way to A/B a LoRA.
- **xformers** — doesn't exist on Mac. `--use-pytorch-cross-attention` instead.
- **Nunchaku acceleration** (appears in the VNCCS model catalog) — NVIDIA 4xxx/5xxx only.
- **`PYTORCH_ENABLE_MPS_FALLBACK=1` as a permanent setting** — it stops crashes by silently falling back to CPU, 10–50x slower with no error. Diagnostic only, to identify the offending node.
- **LoRA training on this machine.** Not for the memory reason often cited — kohya-ss's own SDXL docs say LoRA training fits in 8–10 GB, so the "30 GB at 1024px" figure is wrong by ~3x. The reason is throughput: Apple Silicon runs 3–6x slower than comparable NVIDIA, and MPS blocks both `bitsandbytes` 8-bit optimizers and xformers. If you ever need a character LoRA, rent CUDA (a 5,900-step run finishes in ~75 min on an RTX 4090) or use a trainer service — and note Comfy Cloud can *use* an imported LoRA (Creator tier, $35, CivitAI/HuggingFace URLs only, safetensors only) but cannot *train* one.
- **Custom nodes on Comfy Cloud** — installation is disabled entirely. 36 packs are preinstalled. `ComfyUI-Inpaint-CropAndStitch` is not among them, which is why Graph A uses only core nodes.

---

## 8. Do this, in this order

1. **Today, on Cloud (free tier is enough).** Take the one approved sprite. Author its face-oval mask PNG in any image editor — oval inset ~15 px inside the hairline, white on black, 760×1400. Build Graph A. Run all 6 expressions at denoise 0.40. **~15–25 runs ≈ 120–200 credits, inside the free 400/month.**
2. **Evaluate at sprite scale, not thumbnail scale.** Flip between the 6 outputs at 100 % in an image viewer. If the faces hold and the green is untouched, your entire 78-sprite question is answered and you never needed the local install. If an expression is too weak, raise denoise to 0.50–0.55 for that one only.
3. **Chroma-key just the base sprite** with your Python tool. Confirm the other five produce an identical matte (they must — mask is 0 there).
4. **Only then scale.** Generate the remaining 12 base bodies, approve each, author 12 masks, run 60 inpaints. Buy one month of Standard ($20) when you cross the free tier.
5. **Export as 13 bodies + 78 face plates** into a Ren'Py `layeredimage`, with the under-eye marks as a static `always` overlay.
6. **Revisit local only if** you exhaust cloud credits repeatedly, want privacy, or want unlimited overnight iteration. By then you'll have a proven workflow JSON that drops straight into a local ComfyUI.

---

## 9. Two things I could not resolve — flagging rather than asserting

- **Are your 13 characters canon Jujutsu Kaisen or original characters?** The sprite you described (undercut, two small under-eye marks) doesn't match an obvious canon JJK design. This matters: if they're canon, an Illustrious/NoobAI checkpoint plus the JJK LoRA pack (Civitai 1769023, 4 packs × 217.9 MB, 30 characters) gives you correct likenesses from short Danbooru tags. **If they're OCs, that advantage vanishes entirely** — and the face-oval inpaint method becomes even more clearly correct, because it is identity-agnostic: it works from an approved master sprite with no tag and no LoRA.
- **Whether the fp8 Qwen3-VL text encoder loads on MPS** is unverified, and it determines whether the local Krea 2 download is ~12.7 GB or ~16.3 GB. Check before you start the transfer.

One legal note, since it's cheap to state: Comfy's ToS has **no NSFW or nudity clause at all** (I trust the fact-check's grep of the live document — the only prohibited-content clause covers illegal material), so swimwear/beach scenes are not a problem. The clause that *does* nominally apply to a JJK fan project is the one on content infringing third-party IP. There's no evidence of an automated classifier or of enforcement against fan art, but it is a contractual exposure you do not have locally. Non-commercial, unofficial, clearly labelled is the standard posture. Note also the **Krea 2 Community License is not Apache/MIT** — non-commercial is fine, but commercialising later requires contacting opensource@krea.ai.