"""
The cut-out's edge, for a NEW sprite rendered on a flat saturated backdrop.

    python3 tools/keyedge.py <render.png> <cutout.png>      # the render's own size, RGBA
    python3 tools/keyedge.py --check <render.png> [<cutout.png>]   # what a cut-out still carries of the backdrop
    python3 tools/keysprite.py --edge new <render.png> <character>_<expression>

keysprite's own keying (`key_out`) decides each pixel from how far it leans to
the screen's hue. That is clean, but the edge it leaves is hard, and on the
sixteen test pictures whose true cut-out is known (tools/make_key_tests.py) it
left 15,600 visibly wrong pixels on crisp outlines and 35,700 on soft ones.
This step left 560 to 620 and 6,400 to 7,600 (docs/UI2_DESIGN.md D58,
docs/UI_OVERHAUL_2.md 3d). tools/test_keying.sh holds it to that.

It is for new sprites only. The sprites already in the game were keyed by
`key_out` and are not keyed again (D58): `--edge old`, and no option at all,
are that code, untouched.

A flat backdrop of a known colour K gives every pixel one hard fact:

    C = a*F + (1 - a)*K        C is what the render holds; a (how much of the
                               pixel is figure) and F (the figure's own colour)
                               are what a cut-out needs.

The rules, in the order they run; the reason for each is beside it in the code:

  1. the backdrop colour is read at every pixel, not once for the picture;
  2. a pixel that is pure backdrop is clear, wherever it is;
  3. the figure is solid from three pixels in;
  4. between the two, a is read off the mix of the backdrop and the figure
     colour just inside, and F then follows exactly;
  5. an outline the backdrop has tinted is brought back to the colouring of
     the figure beside it, and never past neutral;
  6. a small patch enclosed by the figure that leans to the backdrop's hue is
     a pocket of backdrop and is cleared;
  7. the faintest edge pixels take the colour of the solid pixel beside them.

It will not cut a figure off grey or white: a backdrop with no hue gives it
nothing to go by, and measured about twelve times worse (D58). Render on a
colour the character does not wear.

No model takes part. tools/cutcheck.py runs the anime-trained model beside a
finished cut-out as a second pair of eyes; it never changes a pixel.

numpy, scipy and Pillow: the system python3 has none. If they are missing,
this script starts itself again with ComfyUI's own Python, as
tools/cloth_match.py does.
"""
import sys, os

COMFY_PY = os.path.expanduser("~/ComfyUI-Installs/ComfyUI/standalone-env/bin/python")
try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
except ImportError:
    if (__name__ == "__main__" and os.path.exists(COMFY_PY)
            and os.path.realpath(sys.executable) != os.path.realpath(COMFY_PY)):
        os.execv(COMFY_PY, [COMFY_PY, os.path.abspath(__file__)] + sys.argv[1:])
    raise SystemExit("numpy, scipy and Pillow are needed: run this with %s" % COMFY_PY)

# A pixel within this of the backdrop colour (largest channel difference) is
# pure backdrop. Why 8: a render's flat colour is not exact; the test pictures
# carry noise of about 3 a channel, and 8 clears that without reaching the
# faintest real edge pixel, which rule 4 then reads.
TOL = 8.0
# A pixel this far from the backdrop certainly holds some figure. Why 24 and
# not TOL: the silhouette is grown outward from these sure pixels into the
# faint ones touching them, so a lone noisy backdrop pixel between 8 and 24
# off, touching nothing, never becomes a speck of figure.
SEED = 24.0
# Below this much colour (the length of the backdrop's colour once its grey is
# taken out) the backdrop has no hue to go by.
NEUTRAL = 25.0


class NoHue(ValueError):
    """The backdrop is grey or white: this step cannot cut a figure off it."""


def key_colour(c):
    """The backdrop colour of the whole picture: the median of the outer eight
    rows and columns. The median, because a figure that touches one side of
    the frame, or a dark border line, is then outvoted by the other sides."""
    strip = np.concatenate([c[:8].reshape(-1, 3), c[-8:].reshape(-1, 3),
                            c[:, :8].reshape(-1, 3), c[:, -8:].reshape(-1, 3)])
    return np.median(strip, axis=0)


def lean_of(c, k0):
    """How far a colour leans toward the backdrop's hue: 1 is as much as the
    backdrop itself, 0 not at all. Brightness is taken out first, so a dark
    pixel of the backdrop's hue still leans."""
    kc = k0 - k0.mean()
    return ((c - c.mean(axis=2, keepdims=True)) * kc).sum(axis=2) / max((kc * kc).sum(), 1.0)


def hue_match(c, k0):
    """1 is exactly the backdrop's hue, whatever its strength. This is what
    tells the backdrop from a colour that is merely near it: on a pink
    backdrop Yuji's red hood and his salmon-pink hair both score about 0.75,
    while leaning to it by 0.4 to 0.6. A rule that asks only for a strong lean
    eats them (the two faults met on 7 Oct), so every rule below that clears
    or thins a pixel asks for the hue as well."""
    kc = k0 - k0.mean()
    ch = c - c.mean(axis=2, keepdims=True)
    return (ch * kc).sum(axis=2) / np.maximum(np.sqrt((ch * ch).sum(axis=2)) * np.sqrt((kc * kc).sum()), 1.0)


def backdrop(c, k0=None, sigma=40.0, win=7):
    """Rule 1. The backdrop colour at every pixel, and each pixel's lean and
    hue match.

    Why not one colour for the picture: a "flat" render drifts a little from
    side to side, and one colour would leave a faint wash of backdrop on one
    side or thin the edge on the other. So the picture's own pure-backdrop
    pixels (within 10 of the picture's colour) are averaged over a wide
    neighbourhood, and that is the backdrop there.

    Why pockets are read apart: the backdrop a figure encloses (between
    fingers, inside a lace loop) comes out a shade of its own, too far from
    the picture's colour to pass as pure backdrop, so it stayed in as a
    coloured patch. Where the purest backdrop-hued pixels in a 7 px window are
    a shade of their own, that shade is the backdrop there, and the pocket is
    judged against it."""
    k0 = key_colour(c) if k0 is None else np.asarray(k0, float)
    strict = (np.abs(c - k0).max(axis=2) <= 10).astype(float)
    w = ndi.gaussian_filter(strict, sigma)
    wide = np.dstack([ndi.gaussian_filter(c[..., i] * strict, sigma) for i in range(3)]) / np.maximum(w, 1e-6)[..., None]
    wide = np.where(w[..., None] > 0.02, wide, k0)        # deep inside the figure there is none to average
    lean = lean_of(c, k0)
    cos = hue_match(c, k0)
    fam = (lean >= 0.8) & (cos >= 0.97)
    top = fam & (lean >= ndi.maximum_filter(np.where(fam, lean, -1.0), size=win) - 0.06)
    n = ndi.uniform_filter(top.astype(float), size=win)
    local = np.dstack([ndi.uniform_filter(c[..., i] * top, size=win) for i in range(3)]) / np.maximum(n, 1e-6)[..., None]
    # only where at least three such pixels agree and the shade really differs:
    # elsewhere the wide average is the steadier number
    off = (n * win * win >= 3) & (np.abs(local - wide).max(axis=2) > 6)
    return np.where(off[..., None], local, wide), k0, lean, cos


def keycut(c, k0=None, band_depth=3.0, radius=3, fit_max=12.0, far=40.0, spread=0.08, edge_rows=8):
    """c: the render, HxWx3 floats 0..255. Returns (F, a, notes): the figure's
    own colour HxWx3, how much of each pixel is figure HxW 0..1, and counts of
    what each rule did."""
    c = np.array(c, float)
    k0 = key_colour(c) if k0 is None else np.asarray(k0, float)
    kc = k0 - k0.mean()
    if float(np.sqrt((kc * kc).sum())) < NEUTRAL:
        raise NoHue("the backdrop (%d, %d, %d) is grey or white: nothing to key on. "
                    "Render on a flat saturated colour the character does not wear." % tuple(k0.round()))
    notes = {"backdrop": [int(v) for v in k0.round()]}

    # The outermost rows of a render are often an off shade of the backdrop (a
    # darker line where the picture was padded). Left alone they are "not
    # backdrop" and frame the cut-out; so, where they have its hue, they are it.
    rim = np.zeros(c.shape[:2], bool)
    rim[:edge_rows] = rim[-edge_rows:] = True; rim[:, :edge_rows] = rim[:, -edge_rows:] = True
    fix = rim & (lean_of(c, k0) >= 0.6) & (hue_match(c, k0) >= 0.97)
    c[fix] = k0

    # Rule 1.
    K, k0, lean, cos = backdrop(c, k0)
    hued = cos >= 0.97                  # the backdrop's own hue, not merely a colour near it (see hue_match)
    v0 = c - K
    d = np.abs(v0).max(axis=2)
    de = np.sqrt((v0 * v0).sum(axis=2))
    luma = c.mean(axis=2)

    # Rule 2. The silhouette is read off colour alone: everything clearly not
    # backdrop, grown into the faint pixels touching it. No flood from the
    # frame's edge and no test of size, so a gap the figure seals off (arm and
    # body, a hand on a hip) opens like any other backdrop, and a model's
    # filled-in gap can never reach the cut-out.
    S = ndi.binary_propagation(d > SEED, mask=d > TOL)

    # Rule 3. Solid from three pixels in. A drawn outline and its anti-aliasing
    # are about two pixels wide; deeper than that a pixel is all figure, and
    # reading a there off its colour would only let a pink blouse or a green
    # eye go thin. So colour decides nothing below the band, except the two
    # narrow cases further down (a sliver, a pocket).
    depth = ndi.distance_transform_edt(S)
    band = S & (depth < band_depth)

    # Rule 4. In the band, a is read off the mix. For a band pixel and a
    # neighbour deeper in, if the pixel's colour lies on the line from the
    # backdrop to that neighbour's colour, the neighbour is "the figure colour
    # just inside" and the place along the line is a. A neighbour counts only
    # if it is deeper in (so it is less mixed than the pixel), far from the
    # backdrop (a near one gives a line too short to measure on), leaves a
    # small remainder (the pixel really is on its line), and is not itself
    # backdrop-coloured (that would explain a pocket's rim as solid).
    H, W = d.shape
    ys, xs = np.nonzero(band)
    p0, pK, pd = v0[ys, xs], K[ys, xs], depth[ys, xs]
    figure_like = ~(hued & (lean >= 0.4))
    cand = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            r = (dy * dy + dx * dx) ** 0.5
            if r == 0 or r > radius + 0.5: continue
            qy, qx = np.clip(ys + dy, 0, H - 1), np.clip(xs + dx, 0, W - 1)
            v = c[qy, qx] - pK                    # the neighbour's colour, measured from THIS pixel's backdrop
            den = (v * v).sum(axis=1)
            a = np.clip((p0 * v).sum(axis=1) / np.maximum(den, 1.0), 0, 1)
            res = np.sqrt(((p0 - a[:, None] * v) ** 2).sum(axis=1))
            ok = (S[qy, qx] & (depth[qy, qx] > pd + 0.3) & (den > far * far) & (res < fit_max)
                  & (a < 0.97) & figure_like[qy, qx])
            cand.append(np.where(ok, a, np.inf))
    best = np.full((H, W), np.inf)
    if len(ys):
        cand = np.stack(cand)
        # Of the neighbours that explain the pixel, the ones giving the LOWEST
        # a are the true figure colour: a neighbour that is itself part
        # backdrop sits nearer along the line and overstates a. The lowest few
        # (within 0.08) are averaged, so one noisy neighbour does not decide.
        low = cand.min(axis=0)
        near = cand <= (low + spread)[None]
        best[ys, xs] = np.where(np.isfinite(low), np.where(near, cand, 0).sum(axis=0) / np.maximum(near.sum(axis=0), 1), np.inf)
    found = band & np.isfinite(best)
    a = np.where(S, 1.0, 0.0)
    a = np.where(found, best, a)

    # The floor the backdrop proves. F has to be a real colour (0..255 in each
    # channel), which puts a least value on a whatever else is read: a pixel
    # much brighter than the backdrop cannot be mostly backdrop.
    dev = np.maximum(np.abs(v0) - TOL, 0)
    amin = np.clip(np.where(c > K, dev / (255 - K), dev / np.maximum(K, 1)).max(axis=2), 0, 1)

    # A band pixel that nothing inside explains (a one-pixel strand of hair, a
    # speck). If it has the backdrop's own hue and most of its lean it is the
    # faint glow a render leaves round a figure: clear. If it has the hue and
    # some lean, it is as solid as the less sure of two readings says. If its
    # colour is its own it is figure, as solid as it is far from the backdrop
    # (fully at 60), which is what keeps thin strands of hair whole.
    lone = band & ~found
    own = np.clip((de - 12.0) / 48.0, 0, 1)
    glow = lone & hued & (lean >= 0.6)
    leaning = np.maximum(amin, np.clip((0.85 - lean) / 0.35, 0, 1))
    a = np.where(lone, np.where(glow, 0.0, np.where(hued & (lean >= 0.4), np.minimum(own, leaning), own)), a)

    # Deeper in than the band, a thin ridge of the backdrop's hue is a sliver
    # of backdrop showing between two strands of hair, too mixed to pass as
    # pure backdrop: it is as clear as its lean says. A ridge only: it must be
    # of the backdrop's hue, lean far more than the figure round it does
    # (`ref`, the figure's own average lean nearby, so pink hair on pink is not
    # a sliver of itself), and stand above its own 5 px surroundings.
    inner = S & (depth >= band_depth + 2)
    n_in = ndi.uniform_filter(inner.astype(float), size=15)
    ref = ndi.uniform_filter(np.where(inner, lean, 0.0), size=15) / np.maximum(n_in, 1e-6)
    _, (iy, ix) = ndi.distance_transform_edt(~inner, return_indices=True)
    thin = n_in * 225 < 8                 # too little solid figure nearby to average: use the nearest solid pixel
    ref = np.where(thin, lean[iy, ix], ref)
    ridge = lean - ndi.grey_opening(lean, size=(5, 5))
    sliver = S & ~band & hued & (lean - ref > 0.3) & (ridge > 0.25)
    a = np.where(sliver, np.clip((1 - lean) / np.maximum(1 - ref, 0.2), 0, 1), a)

    # Rule 6. A small patch, enclosed by the figure on every side, that leans
    # to the backdrop's hue far more than the figure round it is a pocket of
    # backdrop of an odd shade: the inside of a lace loop comes out teal on a
    # green backdrop, and keysprite's keying left it solid on both renders
    # tried. Small (60 px, or a ten-thousandth of the picture) and enclosed,
    # because a large or open patch of that colour is clothing. The hue test
    # is looser here (0.85) on purpose: the pocket's shade is off the
    # backdrop's. It is cleared with a soft edge, by its lean.
    raw_lean, raw_cos = lean_of(c, k0), hue_match(c, k0)
    odd = S & (raw_cos >= 0.85) & (raw_lean - ref > 0.4)
    lab_o, n_o = ndi.label(odd, structure=np.ones((3, 3)))
    pocket = np.zeros_like(S)
    if n_o:
        idx = np.arange(1, n_o + 1)
        small = ndi.sum(odd, lab_o, index=idx) <= max(60.0, 1e-4 * H * W)
        open_air = ndi.maximum(ndi.binary_dilation(~S, iterations=2), lab_o, index=idx) > 0
        core = np.concatenate([[False], small & ~open_air])[lab_o]
        pocket = ndi.binary_dilation(core, iterations=2) & S & ~band & (raw_cos >= 0.85) & (raw_lean - ref > 0.15)
        a = np.where(pocket, np.minimum(a, np.clip((0.5 - raw_lean) / np.maximum(0.5 - ref, 0.1), 0, 1)), a)
    sliver = sliver | pocket
    # the floor holds everywhere in the silhouette except where a rule above
    # has judged the pixel to be backdrop of an odd shade
    a = np.where(S, np.maximum(a, np.where(lone | sliver, 0, amin)), 0.0)
    notes.update(band_px=int(band.sum()), explained_px=int(found.sum()), lone_px=int(lone.sum()),
                 glow_px=int(glow.sum()), sliver_px=int((sliver & ~pocket).sum()), pocket_px=int(pocket.sum()),
                 rim_px=int(fix.sum()))

    # Rule 4, second half. With a settled, the figure's own colour follows
    # exactly from C = a*F + (1-a)*K. Under 4% figure the division is all
    # noise, so the pixel keeps its colour until rule 7 gives it a better one.
    a3 = a[..., None]
    F = np.clip((c - (1 - a3) * K) / np.maximum(a3, 1e-3), 0, 255)
    F = np.where(a3 < 0.04, c, F)

    # Rule 5. A render also tints its own outlines with the backdrop's hue,
    # solid pixels included (a green line down a grey trouser leg). Near the
    # edge no pixel may lean further to that hue than the figure's own
    # colouring just inside does: `expected` is that colouring's lean at the
    # pixel's brightness, and only the excess is taken out, along the
    # backdrop's hue. Two limits: the figure's own lean
    # is kept (pink hair on a pink backdrop stays pink, a red hood stays red),
    # and where the figure leans away from the backdrop the target is neutral,
    # never the opposite colour: taking out more than the tint would paint the
    # outline with the backdrop's complement.
    zone = (S & (depth < band_depth + 5)) | sliver
    chroma = c - luma[..., None]
    den = ndi.uniform_filter(np.where(inner, luma, 0.0), size=15)
    tint = np.dstack([ndi.uniform_filter(np.where(inner, chroma[..., i], 0.0), size=15) for i in range(3)]) / np.maximum(den, 1e-6)[..., None]
    tint = np.where(thin[..., None], chroma[iy, ix] / np.maximum(luma[iy, ix], 20.0)[..., None], tint)
    expected = (tint * kc).sum(axis=2) / max((kc * kc).sum(), 1.0) * F.mean(axis=2)
    excess = np.where(zone, np.clip(lean_of(F, k0) - (np.maximum(expected, 0.0) + 0.02), 0, None), 0.0)
    F = np.clip(F - excess[..., None] * kc, 0, 255)
    notes["despilled_px"] = int((excess > 0.05).sum())

    # Rule 7. Where less than a quarter of a pixel is figure, the colour read
    # out of it is mostly rounding. Those take the colour of the nearest firm
    # pixel (a >= 0.9), blending in between a quarter and 0.6, so the faint
    # rim of an outline is the outline's colour and not a guess.
    firm = S & (a >= 0.9)
    if firm.any():
        _, (fy, fx) = ndi.distance_transform_edt(~firm, return_indices=True)
        w = np.clip((a - 0.25) / 0.35, 0, 1)[..., None]
        F = np.where((S & (a < 0.6))[..., None], w * F + (1 - w) * F[fy, fx], F)
    return F, a, notes


def to_rgba(F, a):
    """The cut-out as 8-bit RGBA. A clear pixel carries no colour."""
    px = np.dstack([np.where(a[..., None] > 0, F, 0.0), a * 255.0])
    px = np.clip(px + 0.5, 0, 255).astype(np.uint8)
    px[px[..., 3] == 0] = 0
    return px


def cut_file(src, dst=None):
    """Cut one render. Returns (rgba, notes); writes dst when it is given."""
    c = np.asarray(Image.open(os.path.expanduser(src)).convert("RGB")).astype(float)
    F, a, notes = keycut(c)
    px = to_rgba(F, a)
    if dst:
        Image.fromarray(px, "RGBA").save(os.path.expanduser(dst))
    return px, notes


STRONG = 0.5       # of the backdrop's own lean, on keysprite's measure
FAINT = 18         # keysprite's own line for "fringe" (its qa), in 8-bit steps
POCKET_MIN = 6     # px


def check(c, px, k0=None):
    """What a finished cut-out (px, 8-bit RGBA) of the render c still carries
    of the backdrop. It reads the cut-out only, so it judges keysprite's own
    keying and this step alike. For a render on a colour the character does
    not wear: a figure's own pink on a pink backdrop would count as tint.

      strong   visible pixels (alpha 8 or more) that lean to the screen's hue
               more than half as much as the backdrop itself does. The measure
               is keysprite's own (`screen_key`), the one its QA reports fringe
               with, so the two tools speak of the same thing.
      faint    the same above keysprite's fringe line, 18. Reported, not failed
               on: a dark outline a shade off neutral is not seen in the game.
      pockets  patches of the render that have the backdrop's hue and half its
               lean or more (a pocket's shade is off the backdrop's, so the hue
               test is the looser 0.85), six pixels or more, that the cut-out
               left more solid than clear. The open backdrop is one such patch
               and is clear; a patch left solid is a pocket inside a lace loop
               or between fingers. Each is (x, y, pixels).
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from keysprite import screen_key
    c = np.asarray(c, float)
    k0 = key_colour(c) if k0 is None else np.asarray(k0, float)
    bg = tuple(int(v) for v in k0.round())
    screen = screen_key(bg)
    if screen is None:
        raise NoHue("the backdrop (%d, %d, %d) is grey or white: nothing to check against" % bg)
    lean = screen[1]
    top = float(lean(*bg))
    a = px[..., 3]
    F = px[..., :3].astype(float)
    ys, xs = np.nonzero((a >= 8) & (lean_of(F, k0) > 0.03))       # the few worth asking keysprite about
    strong = faint = 0
    for r, g, b in px[ys, xs, :3].tolist():
        v = lean(r, g, b)
        if v > FAINT:
            faint += 1
            if v > STRONG * top:
                strong += 1
    like = (hue_match(c, k0) >= 0.85) & (lean_of(c, k0) >= 0.5)
    lab, n = ndi.label(like)
    pockets = []
    if n:
        idx = np.arange(1, n + 1)
        size = ndi.sum(like, lab, index=idx)
        mean = ndi.mean(a / 255.0, lab, index=idx)
        where = ndi.find_objects(lab)
        for i in np.nonzero((size >= POCKET_MIN) & (mean > 0.5))[0]:
            pockets.append((int(where[i][1].start), int(where[i][0].start), int(size[i])))
    return {"strong": strong, "faint": faint - strong, "pockets": pockets, "backdrop": list(bg)}


def check_file(src, cut=None):
    c = np.asarray(Image.open(os.path.expanduser(src)).convert("RGB")).astype(float)
    if cut:
        px = np.asarray(Image.open(os.path.expanduser(cut)).convert("RGBA"))
        if px.shape[:2] != c.shape[:2]:
            raise SystemExit("keyedge: the cut-out is %dx%d and the render %dx%d: give the cut-out at the "
                             "render's own size" % (px.shape[1], px.shape[0], c.shape[1], c.shape[0]))
    else:
        F, a, _ = keycut(c)
        px = to_rgba(F, a)
    return check(c, px)


if __name__ == "__main__":
    args = [v for v in sys.argv[1:] if not v.startswith("--")]
    if "--check" in sys.argv[1:]:
        if len(args) not in (1, 2):
            print(__doc__); raise SystemExit(1)
        try:
            got = check_file(*args)
        except NoHue as e:
            raise SystemExit("keyedge: " + str(e))
        print("keyedge check   backdrop (%d, %d, %d): %d strongly tinted px, %d faintly, %d pocket(s) left solid%s"
              % (tuple(got["backdrop"]) + (got["strong"], got["faint"], len(got["pockets"]),
                 "".join("; %d px at (%d, %d)" % (n, x, y) for x, y, n in got["pockets"][:8]))))
        raise SystemExit(1 if got["strong"] or got["pockets"] else 0)
    if len(args) != 2:
        print(__doc__); raise SystemExit(1)
    try:
        _, notes = cut_file(args[0], args[1])
    except NoHue as e:
        raise SystemExit("keyedge: " + str(e))
    print("keyedge   backdrop (%d, %d, %d); edge band %d px, %d read off the mix, %d on their own; "
          "%d slivers, %d pocket px cleared; %d px brought back from the backdrop's tint"
          % (tuple(notes["backdrop"]) + (notes["band_px"], notes["explained_px"], notes["lone_px"],
                                         notes["sliver_px"], notes["pocket_px"], notes["despilled_px"])))
