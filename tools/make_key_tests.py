"""
The sixteen exact test pictures for the cut-out's edge, and their score.

    python3 tools/make_key_tests.py <folder>                 # build the pictures and their true cut-outs
    python3 tools/make_key_tests.py --score <folder>         # score both edges; exit 1 if a bound is passed
    python3 tools/make_key_tests.py --score <folder> --edge new
    python3 tools/make_key_tests.py --prove <folder>         # break three rules on purpose: the tests must notice
    (tools/test_keying.sh does both, and the rest of the keying tests)

A cut-out can only be scored against a picture whose true cut-out is known,
and no render comes with one. So the pictures are made backwards, from the
game's own sprites: Maki, Yuji, Shoko and Nobara (calm face) are each set on a
flat pink and a flat green backdrop, with a crisp and with a soft outline, as
a fresh render would hold them. Four people x two backdrops x two edges is
sixteen pictures, and for each the true cut-out is the sprite it was made of.

How a picture is made (all of it matters to the score):
  - The soft edge pixels of a sprite in the game carry colours left over from
    the keying that made it. An anti-aliased drawing on a flat backdrop does
    not: its edge pixels are the outline's own colour, part covered. So every
    pixel first takes the colour of the nearest fully solid pixel.
  - crisp: the sprite's own alpha. soft: that alpha blurred by 0.8 px, the
    width a real render's edge fades over (about two pixels).
  - The backdrop is flat, with noise of 3 a channel over the whole picture,
    as a render has. The noise is seeded, so the pictures are the same every
    time they are built from the same sprites.

The score ("visibly wrong", the measure the plan's bounds are in): the
finished cut-out and the true one are each laid on four grounds (white, black,
a sky blue, a wood brown); a pixel is visibly wrong if on any of the four the
two differ by more than 24 in a channel. One number catches every fault: an
edge too solid or too thin, backdrop colour left on, colour taken off.

The bounds, for each four pictures of one backdrop and one kind of edge
(docs/UI2_DESIGN.md 10.2, U0k): the new edge leaves no more than 800 visibly
wrong pixels on a crisp four and 9,000 on a soft four. On 7 Oct it measured
560 to 620 and 6,400 to 7,600; keysprite's own keying 15,600 and 35,700.

A second test, on the two pink pictures of Yuji: a rule that eats a figure's
own colour. He has pink hair and a red hood, the two colours nearest a pink
backdrop, and each was eaten by a rule of the new edge while it was being
written. Deep inside the figure (four pixels in), where the hair and the hood
are solid, none of either may come out thinned or with its colour changed.

`--prove` shows the tests test. It takes the new edge's source, breaks one
rule in a copy held in memory (the file is not touched), and scores the four
pink pictures again: with the hue test switched off (every colour counts as
the backdrop's hue) the red hood must come out eaten, and with the tint rule
made to forget the figure's own lean the pink hair must. A third break lets
rule 4 take any nearby colour that fits as the figure's colour (not only a
solid one deeper in and far from the backdrop): that eats nothing deep inside,
it only roughens crisp outlines, so it is judged by the bound instead, and the
crisp pink four must pass 800 (it measured 879 on 7 Oct, against 622 as
built). That margin is thin. If a redrawn sprite moves the numbers and this
break slips under the bound, --prove fails and says so: the bound, or the
test, then needs looking at, not a refreshed number. If a break goes
unnoticed, the tests have gone soft and this fails.

The pictures are rebuilt from the sprites in the game as they are on the day,
so the numbers move a little when a sprite is redrawn. The bounds have room
for that; they are not a baseline to refresh.

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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

WHO = ("maki", "yuji", "shoko", "nobara")
EDGES = ("crisp", "soft")
KEYS = {"mag": (211, 51, 158), "grn": (40, 190, 70)}      # the pink and the green a render comes back on
KEY_WORD = {"mag": "pink", "grn": "green"}
MARGIN = 0.06                                              # empty frame above and below the figure, as in a render
NOISE = 3.0
GROUNDS = {"white": (255, 255, 255), "black": (0, 0, 0), "sky": (135, 180, 230), "wood": (140, 100, 70)}
VISIBLE = 24.0
BOUND = {"crisp": 800, "soft": 9000}
DEEP = 4                                                   # px inside the figure: past any edge either keying softens


def build(folder, root):
    char = os.path.join(root, "game", "images", "char")
    os.makedirs(folder, exist_ok=True)
    rng = np.random.default_rng(11)           # one stream, drawn in this loop's order: keep the order
    for who in WHO:
        im = Image.open(os.path.join(char, who + "_neutral.png")).convert("RGBA")
        fig = np.asarray(im.crop(im.split()[-1].getbbox())).astype(np.float64)
        fh, fw = fig.shape[:2]
        h = int(round(fh / (1 - 2 * MARGIN))); w = int(round(h * 9 / 16.0))      # a 9:16 frame, as the renders are
        x0, y0 = (w - fw) // 2, (h - fh) // 2
        t = np.zeros((h, w, 4)); t[y0:y0 + fh, x0:x0 + fw] = fig
        solid = t[..., 3] >= 250
        _, (iy, ix) = ndi.distance_transform_edt(~solid, return_distances=True, return_indices=True)
        rgb = t[..., :3][iy, ix]                                   # every pixel takes its nearest solid colour
        for edge in EDGES:
            a = t[..., 3] / 255.0
            if edge == "soft":
                a = ndi.gaussian_filter(a, 0.8)
                a = np.where(a < 0.01, 0, a)
            truth = np.dstack([rgb * (a[..., None] > 0), a * 255])
            Image.fromarray(np.clip(truth + 0.5, 0, 255).astype(np.uint8)).save(
                os.path.join(folder, "truth_%s_%s.png" % (edge, who)))
            for tag, K in KEYS.items():
                c = rgb * a[..., None] + np.array(K) * (1 - a[..., None])
                c += rng.normal(0, NOISE, c.shape)
                Image.fromarray(np.clip(c + 0.5, 0, 255).astype(np.uint8)).save(
                    os.path.join(folder, "test_%s_%s_%s.png" % (edge, tag, who)))
        print("  %-7s %dx%d" % (who, w, h))


def wrong(F, a, truth):
    """Per pixel, how far the finished cut-out is from the true one at worst
    when both are laid on the four grounds."""
    t = truth.astype(float)
    ta, tF = t[..., 3:4] / 255.0, t[..., :3]
    e = np.zeros(a.shape)
    for B in GROUNDS.values():
        B = np.array(B, float)
        e = np.maximum(e, np.abs((a[..., None] * F + (1 - a[..., None]) * B) - (ta * tF + (1 - ta) * B)).max(axis=2))
    return e


def cut_new(path):
    import keyedge
    px, _ = keyedge.cut_file(path)            # the 8-bit cut-out, exactly as the tool writes it
    return px[..., :3].astype(float), px[..., 3] / 255.0


def cut_old(path):
    from pngread import load
    from keysprite import key_out
    im = load(path)
    out = key_out(im)
    px = np.frombuffer(bytes(out.buf), np.uint8).reshape(im.h, im.w, 4).astype(float)
    return px[..., :3], px[..., 3] / 255.0


def own_colours(truth, K):
    """Yuji's pink hair and red hood on the true cut-out, four pixels in: the
    two colours of his that lean to a pink backdrop. The hood is a saturated
    red, (180, 60, 60); the hair a salmon pink, (204, 132, 132), which skin
    comes close to, so the hair is read from the top twentieth of the figure,
    above the forehead."""
    t = truth.astype(float)
    r, g, b = t[..., 0], t[..., 1], t[..., 2]
    solid = t[..., 3] >= 250
    deep = ndi.binary_erosion(solid, iterations=DEEP)
    rows = np.nonzero(solid.any(axis=1))[0]
    crown = np.zeros_like(solid)
    crown[rows[0]:rows[0] + (rows[-1] - rows[0]) // 20] = True
    hood = deep & (r - g > 90) & (r - b > 70)
    hair = deep & crown & ~hood & (r - g > 45)
    return {"pink hair": hair, "red hood": hood}


def score_one(job):
    folder, edge, tag, who, which = job
    path = os.path.join(folder, "test_%s_%s_%s.png" % (edge, tag, who))
    truth = np.asarray(Image.open(os.path.join(folder, "truth_%s_%s.png" % (edge, who))))
    F, a = (cut_new if which == "new" else cut_old)(path)
    e = wrong(F, a, truth)
    eaten = {}
    if who == "yuji" and tag == "mag":
        for name, m in own_colours(truth, KEYS[tag]).items():
            eaten[name] = (int(m.sum()), int((m & ((e > VISIBLE) | (a < 0.98))).sum()))
    return edge, tag, who, which, int((e > VISIBLE).sum()), eaten


def score(folder, which):
    from multiprocessing import Pool
    jobs = [(folder, edge, tag, who, w) for w in which for edge in EDGES for tag in KEYS for who in WHO]
    missing = [j for j in jobs if not os.path.exists(os.path.join(folder, "test_%s_%s_%s.png" % j[1:4]))]
    if missing:
        raise SystemExit("no test pictures in %s: build them first (make_key_tests.py <folder>)" % folder)
    with Pool(min(8, os.cpu_count() or 2)) as pool:
        rows = pool.map(score_one, jobs, chunksize=1)
    total, eaten = {}, {}
    for edge, tag, who, w, n, eat in rows:
        total.setdefault((w, edge, tag), {})[who] = n
        for name, v in eat.items():
            eaten[(w, edge, name)] = v
    fails = []
    print("visibly wrong pixels (off by more than %d on a white, black, blue or brown ground)" % VISIBLE)
    print("  %-22s %-6s %-6s %7s %7s %7s %7s %8s   %s" % (("edge", "outline", "on") + WHO + ("the four", "bound")))
    for w in which:
        for edge in EDGES:
            for tag in KEYS:
                per = total[(w, edge, tag)]
                s = sum(per.values())
                name = "new (keyedge)" if w == "new" else "old (keysprite key_out)"
                verdict = ""
                if w == "new":
                    ok = s <= BOUND[edge]
                    verdict = "%d  %s" % (BOUND[edge], "ok" if ok else "PASSED THE BOUND")
                    if not ok:
                        fails.append("new edge, %s outlines on %s: %d visibly wrong pixels, the bound is %d"
                                     % (edge, KEY_WORD[tag], s, BOUND[edge]))
                print("  %-22s %-6s %-6s %7d %7d %7d %7d %8d   %s"
                      % ((name, edge, KEY_WORD[tag]) + tuple(per[x] for x in WHO) + (s, verdict)))
    if len(which) == 2:
        for edge in EDGES:
            for tag in KEYS:
                n, o = sum(total[("new", edge, tag)].values()), sum(total[("old", edge, tag)].values())
                if n >= o:
                    fails.append("new edge is no better than the old on %s outlines on %s (%d against %d)"
                                 % (edge, KEY_WORD[tag], n, o))
    print("a figure's own colour, deep inside Yuji on pink (pixels of it; pixels thinned or changed)")
    for (w, edge, name), (n, bad) in sorted(eaten.items()):
        line = "  %-4s %-6s %-10s %7d %6d" % (w, edge, name, n, bad)
        if w == "new":
            if n < 500:
                fails.append("the %s was not found on Yuji's sprite (%d px): the test is not testing" % (name, n))
            if bad:
                fails.append("new edge ate %d px of the %s on pink (%s outlines)" % (bad, name, edge))
            line += "   ok" if (n >= 500 and not bad) else "   FAIL"
        print(line)
    for f in fails:
        print("FAIL: " + f)
    print("KEY TESTS %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


# (what is broken, the source text replaced, what replaces it, how it must be
# noticed: the name of a colour that must come out eaten on both kinds of
# outline, or PAST_BOUND for a break that must push the crisp pink four past
# its bound)
PAST_BOUND = "past the crisp bound"
BREAKS = (
    ("the hue test switched off",
     "    kc = k0 - k0.mean()\n    ch = c - c.mean(axis=2, keepdims=True)\n    return (ch * kc)",
     "    return np.ones(c.shape[:2])\n    kc = k0 - k0.mean()\n    ch = c - c.mean(axis=2, keepdims=True)\n    return (ch * kc)",
     "red hood"),
    ("the tint rule forgetting the figure's own lean",
     "np.maximum(expected, 0.0) + 0.02", "0.0 + 0.02", "pink hair"),
    ("any nearby colour that fits taken as the figure's",
     "(depth[qy, qx] > pd + 0.3) & (den > far * far) & (res < fit_max)", "(res < fit_max)", PAST_BOUND),
)


def prove(folder):
    import types
    src = open(os.path.join(HERE, "keyedge.py")).read()
    fails = []
    for label, old, new, colour in (("as built", None, None, None),) + BREAKS:
        text = src
        if old is not None:
            if text.count(old) != 1:
                fails.append("cannot break the edge (%s): the line it replaces is no longer in keyedge.py; "
                             "bring BREAKS in make_key_tests.py up to date" % label)
                continue
            text = text.replace(old, new)
        mod = types.ModuleType("keyedge_broken")
        mod.__file__ = os.path.join(HERE, "keyedge.py")
        exec(compile(text, mod.__file__, "exec"), mod.__dict__)
        for edge in EDGES:
            total, eaten = 0, {}
            for who in WHO:
                truth = np.asarray(Image.open(os.path.join(folder, "truth_%s_%s.png" % (edge, who))))
                c = np.asarray(Image.open(os.path.join(folder, "test_%s_mag_%s.png" % (edge, who))).convert("RGB")).astype(float)
                px = mod.to_rgba(*mod.keycut(c)[:2])
                F, a = px[..., :3].astype(float), px[..., 3] / 255.0
                e = wrong(F, a, truth)
                total += int((e > VISIBLE).sum())
                if who == "yuji":
                    for name, m in own_colours(truth, KEYS["mag"]).items():
                        eaten[name] = int((m & ((e > VISIBLE) | (a < 0.98))).sum())
            print("  %-48s %-5s pink four %6d (bound %d)   hair eaten %4d   hood eaten %4d"
                  % (label, edge, total, BOUND[edge], eaten["pink hair"], eaten["red hood"]))
            if colour is None and (eaten["pink hair"] or eaten["red hood"] or total > BOUND[edge]):
                fails.append("the edge as built fails on %s outlines" % edge)
            if colour == PAST_BOUND:
                if edge == "crisp" and total <= BOUND[edge]:
                    fails.append("with %s, the crisp pink four stayed inside its bound (%d, the bound is %d): "
                                 "the test has gone soft" % (label, total, BOUND[edge]))
            elif colour is not None and not eaten[colour]:
                fails.append("with %s, the %s was not reported eaten (%s outlines): the test has gone soft"
                             % (label, colour, edge))
    for f in fails:
        print("FAIL: " + f)
    print("KEY TESTS PROOF %s" % ("FAIL" if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    root = os.path.dirname(HERE)
    which = ["old", "new"]
    if "--root" in argv:
        i = argv.index("--root"); root = os.path.expanduser(argv[i + 1]); del argv[i:i + 2]
    if "--edge" in argv:
        i = argv.index("--edge")
        which = {"new": ["new"], "old": ["old"], "both": ["old", "new"]}[argv[i + 1]]; del argv[i:i + 2]
    do_score = "--score" in argv
    do_prove = "--prove" in argv
    args = [v for v in argv if not v.startswith("--")]
    if len(args) != 1:
        print(__doc__); raise SystemExit(1)
    folder = os.path.expanduser(args[0])
    if do_prove:
        raise SystemExit(prove(folder))
    if do_score:
        raise SystemExit(score(folder, which))
    print("building the sixteen pictures from %s" % os.path.join(root, "game", "images", "char"))
    build(folder, root)
    print("-> %s" % folder)
