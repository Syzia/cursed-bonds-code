"""
One cloth for the school uniform.

    python3 tools/cloth_match.py --check                  # how far each uniform is from the ramp
    python3 tools/cloth_match.py --apply all              # match the sprites and side portraits in the game
    python3 tools/cloth_match.py --apply maki,nobara
    python3 tools/cloth_match.py --apply yuji --redrawn   # only once his school-uniform set is in the game
    python3 tools/cloth_match.py --apply all --root <copy of the project>     # a dry run on a copy

The owner (7 Oct 2026), looking at the redrawn Yuji beside the others: "the
characters clothing isnt consistent. The textures are all different", and,
shown the before and after: "Yes that's what I meant, apply it to all six".

Six people wear the school uniform: Megumi, Yuji, Nobara, Maki, Toge and the
player. Each sprite was drawn on its own, so the same cloth came out six ways:
Megumi's and Toge's agree (a deep navy with thin crisp streaks), Yuji's redraw
is lighter and purplish, Nobara's darker with broad soft highlights, Maki's
bluer with soft-edged shading, the player's with almost no highlights.

This does not redraw anything. Every pixel of uniform cloth is moved onto one
colour ramp (Megumi's and Toge's) by its own brightness, after that person's
dark, main and streak tones are lined up with the ramp's; where a drawing
shades softly (Nobara, Maki) the step between the main tone and the streak
tone is made crisp, as it is on the others. Nothing else changes: the face,
hair, hands, legs, shoes, buttons, a red hood, the shapes of the folds, and
the cut-out's edge (the alpha channel is not touched).

A person's six sprites share one body, pixel for pixel, so the cloth and its
tones are read once, off the calm sprite, and the same change is made to all
six. The side portraits are then made again from the sprites by
keysprite.side_portrait, which reproduces today's thirty exactly.

`--apply` checks its own work and stops before writing if a check fails: the
alpha channel is unchanged, no pixel outside the cloth has changed, and the
cloth is on the ramp afterwards. A person whose cloth is already on the ramp
is left alone, so running it twice does nothing the second time.

It does not add streaks where a drawing has none (the player's jacket stays
flatter than Megumi's), and it leaves every other outfit alone: Gojo's darker
uniform, the adults' clothes, the grey uniform of Sana and of the player's
old school (`mcyotsuka_*`).

Yuji is not in `all`: the sprite the game has today shows him in an open
jacket over a hoodie, and his school-uniform set goes in as one step
(docs/UI2_DESIGN.md D57). It is matched then, with `--apply yuji --redrawn`.

numpy, scipy and Pillow: the system python3 has none. If they are missing,
this script starts itself again with ComfyUI's own Python.
"""
import sys, os

COMFY_PY = os.path.expanduser("~/ComfyUI-Installs/ComfyUI/standalone-env/bin/python")
try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
except ImportError:
    if os.path.exists(COMFY_PY) and os.path.realpath(sys.executable) != os.path.realpath(COMFY_PY):
        os.execv(COMFY_PY, [COMFY_PY, os.path.abspath(__file__)] + sys.argv[1:])
    raise SystemExit("numpy, scipy and Pillow are needed: run this with %s" % COMFY_PY)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")

# The ramp: the uniform's colour at each brightness, read off Megumi and Toge
# (their cloth agrees to within two levels). Brightness is the mean of R, G, B.
RAMP_L = np.array([6.0, 20.0, 36.7, 40.3, 46.3, 84.0, 110.0])
RAMP_C = np.array([[7, 6, 9], [19, 17, 24], [34, 31, 45], [37, 34, 50], [41, 39, 59], [64, 68, 120], [84, 90, 156]], float)
REF = {"dark": 20.0, "base": 40.3, "high": 84.0}

# Who wears it. rows: where the cloth starts and stops, as fractions of the
# figure's height on the calm sprite (below the hair, above the socks or
# shoes). crisp: how hard a soft step up to the streak tone is sharpened.
# neutral_below: from that height down, colourless darks are not cloth (the
# player's black boots start where his trousers end, on a slant).
UNIFORM = {
    "megumi": {"rows": (0.14, 0.862)},
    "toge":   {"rows": (0.13, 0.848)},
    "nobara": {"rows": (0.155, 0.70), "crisp": 0.6},
    "maki":   {"rows": (0.15, 0.64), "crisp": 0.6},
    "mc":     {"rows": (0.13, 0.93), "neutral_below": 0.86},     # black boots under the hems
    "yuji":   {"rows": (0.165, 0.925), "not_red": True, "redrawn_only": True},
}
ALL = ["megumi", "toge", "nobara", "maki", "mc"]
ON_RAMP = 1.5        # mean distance from the ramp, in levels, at which a uniform counts as matched
# A cloth that is on the ramp (within 0.6) with its three tones this close to the ramp's has been matched
# already. The streak tone is a percentile of few pixels and lands within three or four levels, not on it.
MATCHED_WITHIN = {"dark": 2.0, "base": 2.5, "high": 4.0}


def sprite_path(root, who, expr):
    return os.path.join(root, "game", "images", "char", "%s_%s.png" % (who, expr))


def side_path(root, who, expr):
    return os.path.join(root, "game", "images", "side", "%s_%s.png" % (who, expr))


def read(path):
    im = Image.open(path)
    if im.mode != "RGBA":
        raise SystemExit("%s is %s, not RGBA" % (path, im.mode))
    return np.asarray(im).astype(float)


def cloth_mask(a, who):
    """The uniform's cloth on the calm sprite: dark, cool-coloured, in the body's rows, in big pieces."""
    spec = UNIFORM[who]
    al = a[..., 3]
    ys = np.where(al.max(axis=1) > 24)[0]
    y0, y1 = ys[0], ys[-1] + 1
    top, bot = spec["rows"]
    rows = np.zeros(al.shape, bool)
    rows[y0 + int((y1 - y0) * top):y0 + int((y1 - y0) * bot)] = True
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    luma = (r + g + b) / 3
    cool = (b >= r - 6) & (b >= g - 6)          # navy, indigo, plum or neutral dark: not skin, brown tights or green hair
    ok = (al > 0) & (luma < 135) & cool & rows
    if spec.get("not_red"):
        ok &= ~((r > 110) & (r - b > 40))       # a red hood, red cuffs
    if spec.get("neutral_below"):
        low = np.zeros(al.shape, bool)
        low[y0 + int((y1 - y0) * spec["neutral_below"]):] = True
        ok &= ~(low & (b - r < 6))
    m = ndi.binary_opening(ok, iterations=1)
    lab, n = ndi.label(m)
    if n:                                       # the jacket, the trousers, the skirt: not specks
        sizes = ndi.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.where(sizes > 400)[0])
    m = ndi.binary_dilation(m, iterations=1) & ok
    if not m.any():
        return m
    # Nothing brighter than the cloth's own streaks, and nothing bright that is not blue: the blend where
    # a white cuff or a hand meets the cloth is grey, and moved onto the ramp it would turn blue.
    hist, edges = np.histogram(luma[m], bins=64, range=(0, 128))
    main = (edges[hist.argmax()] + edges[hist.argmax() + 1]) / 2
    return m & (luma <= np.percentile(luma[m], 97.5) + 12) & ~((luma > main + 18) & (b - r < 14))


def tones(a, m):
    """This drawing's own dark, main and streak brightness."""
    luma = a[..., :3].mean(axis=2)[m]
    lo, hi = np.percentile(luma, 3), np.percentile(luma, 97.5)
    hist, edges = np.histogram(luma, bins=64, range=(0, 128))
    base = (edges[hist.argmax()] + edges[hist.argmax() + 1]) / 2
    return {"dark": float(lo), "base": float(base), "high": float(max(hi, base + 12))}


def match(a, m, t, crisp=0.0):
    """Move the cloth pixels of one sprite onto the ramp. m and t come from the calm sprite."""
    luma = a[..., :3].mean(axis=2)
    L = np.interp(luma, [0, t["dark"], t["base"], t["high"], 255],
                  [0, REF["dark"], REF["base"], REF["high"], 255 * REF["high"] / max(t["high"], 1)])
    if crisp > 0:
        # pull a soft gradient between the main tone and the streak tone apart...
        lo = REF["base"] + 4
        u = np.clip((L - lo) / (REF["high"] - lo), 0, 1)
        v = np.clip((u - 0.5) * (1 + 6 * crisp) + 0.5, 0, 1)
        v = v * v * (3 - 2 * v)
        L = np.where(L > lo, lo + v * (REF["high"] - lo), L)
        # ...and soften the stair-steps that leaves, inside the cloth only
        Ls = ndi.gaussian_filter(np.where(m, L, 0.0), 0.7) / np.maximum(ndi.gaussian_filter(m.astype(float), 0.7), 1e-6)
        L = np.where(m & (L > REF["base"] - 2), Ls, L)
    out = a.copy()
    new = np.dstack([np.interp(L, RAMP_L, RAMP_C[:, i]) for i in range(3)])
    out[..., :3] = np.where(m[..., None], np.round(new), a[..., :3])
    return out


def off_ramp(a, m):
    """How far the cloth is from the ramp: the mean distance of a pixel from the ramp's colour at its brightness."""
    px = a[..., :3][m]
    luma = px.mean(axis=1)
    ramp = np.stack([np.interp(luma, RAMP_L, RAMP_C[:, i]) for i in range(3)], axis=1)
    return float(np.abs(px - ramp).max(axis=1).mean())


def report(root, people):
    worst = 0.0
    print("%-8s %8s  %-26s %s" % ("who", "cloth px", "dark / main / streak", "off the ramp (levels)"))
    for who in people:
        a = read(sprite_path(root, who, "neutral"))
        m = cloth_mask(a, who)
        t = tones(a, m)
        d = off_ramp(a, m)
        tone_gap = max(abs(t[k] - REF[k]) for k in ("dark", "base", "high"))
        verdict = "matched" if d <= ON_RAMP and tone_gap <= 6 else "NOT matched"
        worst = max(worst, d if tone_gap <= 6 else 99.0)
        print("%-8s %8d  %5.1f / %5.1f / %5.1f       %5.2f   %s" % (who, int(m.sum()), t["dark"], t["base"], t["high"], d, verdict))
    print("the ramp:                 %5.1f / %5.1f / %5.1f" % (REF["dark"], REF["base"], REF["high"]))
    return worst <= ON_RAMP


def apply(root, people):
    from pngread import load
    from keysprite import side_portrait
    for who in people:
        calm = read(sprite_path(root, who, "neutral"))
        m = cloth_mask(calm, who)
        t = tones(calm, m)
        crisp = UNIFORM[who].get("crisp", 0.0)
        if off_ramp(calm, m) <= 0.6 and all(abs(t[k] - REF[k]) <= gap for k, gap in MATCHED_WITHIN.items()):
            print("%-8s already matched: nothing done" % who)      # a second pass would not be nothing
            continue
        results, changed, biggest = {}, 0, 0.0
        for expr in EXPRESSIONS:
            p = sprite_path(root, who, expr)
            if not os.path.exists(p):
                raise SystemExit("no sprite at %s" % p)
            a = read(p)
            if a.shape != calm.shape:
                raise SystemExit("%s is not the size of the calm sprite" % p)
            out = match(a, m, t, crisp)
            if not np.array_equal(out[..., 3], a[..., 3]):
                raise SystemExit("%s: the cut-out's edge would change; nothing written" % p)
            diff = np.abs(out[..., :3] - a[..., :3]).max(axis=2)
            if (diff[~m] > 0).any():
                raise SystemExit("%s: a pixel outside the cloth would change; nothing written" % p)
            changed += int((diff > 0).sum()); biggest = max(biggest, float(diff.max()))
            results[expr] = out
        after = off_ramp(results["neutral"], m)
        if after > ON_RAMP:
            raise SystemExit("%s: the cloth would still be %.2f levels off the ramp; nothing written" % (who, after))
        for expr, out in results.items():
            Image.fromarray(out.astype(np.uint8), "RGBA").save(sprite_path(root, who, expr))
            side_portrait(load(sprite_path(root, who, expr))).save(side_path(root, who, expr))
        print("%-8s cloth %6d px on each sprite; %7d pixel changes over six sprites, the largest %3.0f levels; "
              "off the ramp %.2f -> %.2f; six side portraits made again"
              % (who, int(m.sum()), changed, biggest, off_ramp(calm, m), after))


def main(argv):
    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv):
                raise SystemExit("%s needs a value" % flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    root = opt("--root") or ROOT
    who = opt("--apply")
    redrawn = "--redrawn" in argv
    if redrawn: argv.remove("--redrawn")
    if "--check" in argv and not who:
        argv.remove("--check")
        if argv:
            print(__doc__); raise SystemExit(1)
        people = ALL + (["yuji"] if redrawn else [])
        raise SystemExit(0 if report(root, people) else 1)
    if not who or argv:
        print(__doc__); raise SystemExit(1)
    people = list(ALL) if who == "all" else [w for w in who.split(",") if w]
    for w in people:
        if w not in UNIFORM:
            raise SystemExit("no uniform row for %r: choose from %s" % (w, ", ".join(sorted(UNIFORM))))
        if UNIFORM[w].get("redrawn_only") and not redrawn:
            raise SystemExit("%s: today's sprite is not in the school uniform. Once the redrawn set is in the "
                             "game (docs/UI2_DESIGN.md D57), run --apply %s --redrawn" % (w, w))
    apply(root, people)
    report(root, people)


if __name__ == "__main__":
    main(sys.argv[1:])
