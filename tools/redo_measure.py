"""
The measurements behind tools/install_redo.py: has a picture redone in place
moved, lost something, gained something, and is it sharper.

    tools/py_art.sh tools/redo_measure.py <old.png> <new.png>      # the raw figures of one pair, to read

docs/UI2_DESIGN.md 5.4 (steps 1 to 6) and 5.7. Everything is measured on the
1920x1080 picture the game shows. The method is the one the look tests were
measured with on 6 Oct 2026 (24 tiles of every first-test and third-test
render lined up with the game's picture to 0 px; a picture shifted 12 px or
enlarged 2% by hand read as moved everywhere):

  EDGE MAP    the picture in grey, blurred by 2 px, then the size of its
              gradient. The new look changes texture and colour and keeps
              where things are, and the edge map is what stays.
  A SHIFT     the two edge maps of a window are slid over each other (up to
              24 px any way) and the offset where they agree best is the
              shift. "Agreement" is their correlation, 1.0 for the same
              drawing and about 0 for unrelated ones.
  A POINT     a registered point (an exit, a hotspot, feet, a foreground's
              outline, a traced shape's outline) is held twice: its window
              may not have shifted, and when no shift is found the window
              must still be the same drawing: it agrees at some offset at
              all, and within 3 px of where it was it agrees at least
              GONE_REL of what the picture's 24 tiles do. A door slid
              further than the search, or painted out, fails the second.
  GLASS       the keep list's `windows` rows are left out of every point's
              window and every keep box (filled with the mean of the rest):
              a door is held by its post and its handle, and the view
              through it may change. A window that is nearly all glass has
              nothing to line up on and is said so.
  A FLOOR     a point where people stand that fails either test is held
              again in a wider window on a coarse edge map (the floor's
              outline, a table's legs; not the lines between boards). Moved
              there, it is refused; otherwise it is shown (LOOK).
  VANISHED    inside a keep box: the agreement of the two edge maps (the
              best within 3 px) against the agreement of the picture's 24
              tiles (a heavy redraw lowers both; an object taken away lowers
              only its own box), and how much of the old edge is still
              there. An object taken away leaves the wall behind it. One
              that agrees well a little way off is named as moved instead;
              one whose box, a little wider, agrees as well as the picture
              does is still there, fainter (LOOK). The automatic box round
              a hotspot is left out where an `allow` box lies on it.
  ADDED       inside an empty zone: the amount of fine edge (1 px blur),
              against how much the picture as a whole gained. A jacket, a
              cup or a scatter of leaves is fine edge where there was none.
              A zone wider or taller than 250 px (a floor) is judged whole
              AND in overlapping 160 px cells: one bag on a wide floor is
              lost in the floor's mean and plain in its own cell. A floor
              whose cells no longer agree with the game's (drawn again) is
              shown, not refused. A relight is not judged; its small empty
              zones are read against the ring round each, for a LOOK only.
  LOOK        whatever else changed is shown, not refused: a 320 px tile,
              or a 120 px cell, whose edge map no longer agrees with the
              game's picture (a new view through a window, a thing drawn
              on a wall). Not for a relight, whose windows change by design.
  SHARPER     the variance of the Laplacian over the picture.

Every number that decides a verdict is a constant below, set against renders
whose answers are known (tools/test_art_tools.sh runs them; the figures are
recorded in tools/art/redo_measures.json).

numpy, scipy and Pillow: start it through tools/py_art.sh.
"""
import sys, os

try:
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import ndimage as ndi
except ImportError:
    raise SystemExit("numpy, scipy and Pillow are needed: start this with tools/py_art.sh")

W, H = 1920, 1080
EDGE_ROWS = 8               # rows left out at the top and the bottom: a 2K render is padded there

# ---- the thresholds (5.4: "set in U0d against renders whose answers are known") --------------------------
SHIFT_WHOLE = 1             # the whole picture may be off by this many px
SHIFT_POINT = 3             # a window round a registered point, and a change box's outline, by this many
SEARCH = 24                 # how far a shift is looked for
WINDOW = 192                # the window round a registered point
FLAT = 1.2                  # an edge map with less spread than this has nothing to line up on
LOCK = 0.30                 # an offset is believed when the agreement there is at least this ...
LOCK_GAIN = 0.08            # ... and beats the agreement at no offset by this ...
LOCK_ZERO = 0.70            # ... while the agreement at no offset is under this share of it (a drawing that really
                            # moved agrees poorly where it was; one redrawn in place still agrees there), and the
                            # offset is not at the very edge of the search
DIFFERENT = 0.20            # a tile whose best agreement is under this is a different drawing (LOOK)
MOVED_TILES = 0.25          # this share of the 24 tiles moved: the picture is moved or enlarged everywhere
GONE_REL = 0.54             # a keep box that agrees less than this share of what the picture's tiles do ...
GONE_EDGE = 0.40            # ... or keeps less than this share of its edge, is gone
REL_FLOOR = 0.50            # (the tiles' middle agreement is never taken as less than this)
ADDED_RISE = 1.16           # an empty zone whose fine edge rose this many times more than the picture's did ...
ADDED_MIN = 1.2             # ... and by at least this much, in levels a pixel
CELL_FROM = 250             # an empty zone wider or taller than this is judged in cells as well as whole:
CELL = 160                  # ... cells this wide and at most this tall ...
CELL_STEP = 80              # ... every this many px (so they overlap by half) ...
CELL_MIN = 3000             # ... leaving out a cell that holds fewer px of the zone than this
CELL_RISE = 1.22            # a cell is "something new" from this rise and this many levels. A cell is noisier than a
CELL_ADD = 1.5              # whole zone: on the Common Room's floor the good renders read at most 1.06 and the emptied
                            # second-test room 1.14 / 1.0; two cups set on the bare boards read 1.26 / 1.7, a cushion
                            # 1.42 / 3.4, a kettle 1.48 / 3.1, a bag 1.31 / 2.5 (each at its weakest of five places)
LOOK_CELL = 120             # step 6: a cell this size ...
LOOK_DIFF = 0.30            # ... whose best agreement within 3 px is under this is drawn differently (LOOK)
LOOK_MANY = 6               # more cells than this are told in one line
SHARP_PASS = 2.0            # times the revision-1 picture's figure
SHARP_LOOK = 1.3
# A relight (5.7): a night picture loses edge in its dark corners, so "vanished" has thresholds of its own
# and "added" and "sharper" are not judged.
RELIGHT_GONE_REL = 0.30      # a relight: gone only when BOTH are under. Of the eight pairs the game has, the weakest
RELIGHT_GONE_EDGE = 0.50     # kept thing is a window lit at night: 0.39 of its agreement, 43% of its edge.
# The corrections of 11 Oct 2026 (U0d3; tools/art/staged/early/art_3a_early.json, art_4b_early.json). Each was a
# false alarm on a picture the owner chose; each is set against that picture AND against the faults that must
# still be refused (the emptied Common Room, a door slid 30 px, a thing set down on a floor).
AUTO_BOX = 110              # the box kept round every hotspot's point without being written down
GLASS_MIN = 0.12            # a guard window with less than this share of itself off the glass has nothing to line
                            # up on: it is left out, and the report says so
FLOOR_WIDE = (384, 256)     # a standing point whose own window no longer agrees is held by this wider window on a
FLOOR_BLUR = 5.0            # coarse edge map: the floor's outline and what stands on it, not the boards' lines
REDRAWN = 0.55              # a wide empty zone (a floor) whose 160 px cells agree, in the middle, less than this
REDRAWN_CELLS = 8           # with the game's picture (and has at least this many cells) is DRAWN AGAIN: other
                            # boards, light across it. Measured: My Room's chosen render 0.32, the first test's
                            # Common Room B 0.22; every floor that is the same drawing 0.84 or more, with a
                            # cushion, a kettle, a bag or two cups set down on it as well
RELIGHT_ADD_RISE = 1.40     # a relight is never refused for an added thing (5.7), but a SMALL empty place of the
RELIGHT_ADD_MIN = 1.5       # keep list (not a floor: light falls across floors) whose fine edge rose this many
RELIGHT_RING = 60           # times more than the ring this wide round it did, and by this many levels, is shown.
                            # Measured on the sixteen relit Common Room, My Room and Cafeteria renders: the blanket
                            # a lamplit night laid over the sofa's arm reads 1.53 / 2.0; the most on any place of
                            # the eight pictures the owner chose is 1.24 (a table top under moonlight)
FAINT_PAD = 16              # a kept thing that reads as gone inside its own box, but whose box widened by this
FAINT_REL = 0.85            # much agrees at least this share of what the picture does, is still there: fainter,
                            # or drawn differently inside its outline. Measured: the calendar on My Room's wall,
                            # which became lighter, 1.06; of the emptied Common Room's twelve things the best 0.64


class Refused(Exception):
    """Why a picture cannot go in, in the owner's words."""


# ---- step 1: the fit --------------------------------------------------------------------------------------
def _bars(a):
    """How many rows or columns at each edge are one flat near-black or near-white colour."""
    g = a.mean(axis=2)

    def run(lines):
        n = 0
        for line in lines:
            if line.std() < 2.0 and (line.mean() < 10 or line.mean() > 246):
                n += 1
            else:
                break
        return n

    return (run(g), run(g[::-1]), run(g.T), run(g.T[::-1]))


def fit(im):
    """(the picture as a 1080x1920x3 float array, a line saying what was done). Refuses static and bars.

    A 2752x1536 render is the room at 1920x1072: it is scaled to the full width, laid 4 px down, and the
    4 px above and below are filled with the render's own first and last rows (cropping its sides to 16:9
    instead would put everything 6 to 7 px off at the edges)."""
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.float32)
    top, bottom, left, right = _bars(a)
    if max(top, bottom) > a.shape[0] * 0.012 or max(left, right) > a.shape[1] * 0.012:
        raise Refused("the render has bars along its edges (%d px above, %d below, %d left, %d right): it is not a "
                      "whole picture" % (top, bottom, left, right))
    g = a.mean(axis=2)
    gx = g[:, 1:] - g[:, :-1]
    if g.std() < 2.0:
        raise Refused("the render is one flat colour")
    if np.corrcoef(g[:, :-1].ravel()[::7], g[:, 1:].ravel()[::7])[0, 1] < 0.5 and gx.std() > 20:
        raise Refused("the render is static: neighbouring pixels have nothing to do with each other")
    if im.size == (W, H):
        return a, "%dx%d, as it is" % (W, H)
    nh = int(im.height * W / float(im.width) + 0.5)
    b = np.asarray(im.resize((W, nh), Image.LANCZOS)).astype(np.float32)
    if nh == H:
        return b, "%dx%d -> %dx%d" % (im.width, im.height, W, H)
    if nh > H:
        y0 = (nh - H) // 2
        return b[y0:y0 + H], "%dx%d -> %dx%d, %d rows cropped above and below" % (im.width, im.height, W, nh, y0)
    y0 = (H - nh) // 2
    out = np.empty((H, W, 3), np.float32)
    out[:y0] = b[0]
    out[y0:y0 + nh] = b
    out[y0 + nh:] = b[-1]
    return out, "%dx%d -> %dx%d, %d px down" % (im.width, im.height, W, nh, y0)


def load(path):
    return fit(Image.open(path))


def save(a, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGB").save(path)


# ---- the edge map and a shift -----------------------------------------------------------------------------
def grey(a):
    return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114


def edges(a, sigma=2.0):
    g = ndi.gaussian_filter(grey(a), sigma)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    return np.hypot(gx, gy)


def agree(a, b):
    """The correlation of two edge windows at no offset."""
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 1e-6 else 0.0


def shift(old, new, search=SEARCH):
    """How far `new` has moved against `old`: (dx, dy, the agreement there, the agreement at no offset).
    dx is positive when the new drawing sits further right."""
    a = old - old.mean(); b = new - new.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    if d < 1e-6:
        return 0, 0, 0.0, 0.0
    r = np.fft.irfft2(np.fft.rfft2(b) * np.conj(np.fft.rfft2(a)), s=a.shape) / d
    h, w = a.shape
    sy, sx = min(search, h // 2 - 1), min(search, w // 2 - 1)
    best = (-2.0, 0, 0)
    ys = list(range(0, sy + 1)) + list(range(h - sy, h))
    xs = list(range(0, sx + 1)) + list(range(w - sx, w))
    sub = r[np.ix_(ys, xs)]
    k = int(np.argmax(sub))
    py, px = ys[k // len(xs)], xs[k % len(xs)]
    dy = py - h if py > h // 2 else py
    dx = px - w if px > w // 2 else px
    return int(dx), int(dy), float(sub.max()), float(r[0, 0])


def window(pt, size=WINDOW, high=None):
    """(x0, y0, x1, y1) of the window round a point, kept inside the picture (`size` wide, `high` or `size` tall)."""
    high = high or size
    x0 = int(min(max(pt[0] - size // 2, 0), W - size))
    y0 = int(min(max(pt[1] - high // 2, EDGE_ROWS), H - EDGE_ROWS - high))
    return x0, y0, x0 + size, y0 + high


def glass_mask(windows):
    """The glass of a room (the keep list's `windows` rows) as one mask over the picture; None when it has none."""
    out = None
    for z in windows or ():
        m = zone_mask(z)[0]
        out = m if out is None else (out | m)
    return out


def pair(eo, en, box, glass=None):
    """The two edge windows of a box, with the glass left out: (old, new, the share of the window that is glass).
    Glass is filled with the mean of the rest, so that it adds nothing to an agreement. (None, None, share) when
    too little of the window is off the glass to line anything up."""
    x0, y0, x1, y1 = box
    a, b = eo[y0:y1, x0:x1], en[y0:y1, x0:x1]
    if glass is None:
        return a, b, 0.0
    m = glass[y0:y1, x0:x1]
    if not m.any():
        return a, b, 0.0
    share = float(m.mean())
    if 1.0 - share < GLASS_MIN:
        return None, None, share
    a, b = a.copy(), b.copy()
    a[m] = a[~m].mean()
    b[m] = b[~m].mean()
    return a, b, share


def moved(eo, en, box, limit=SHIFT_POINT, gain=None, zero_share=None, glass=None):
    """One window: {"state": "flat" / "same" / "moved" / "different", dx, dy, agree}. With `glass`, the glass
    inside the window is left out; a window that is all glass is "flat"."""
    a, b, _share = pair(eo, en, box, glass)
    if a is None or a.std() < FLAT:
        return {"state": "flat", "dx": 0, "dy": 0, "agree": 0.0}
    dx, dy, peak, zero = shift(a, b)
    out = {"dx": dx, "dy": dy, "agree": round(peak, 3), "zero": round(zero, 3)}
    if peak < DIFFERENT:
        out["state"] = "different"
    elif (limit < max(abs(dx), abs(dy)) < SEARCH and peak >= LOCK
          and peak - zero >= (LOCK_GAIN if gain is None else gain)
          and zero <= (LOCK_ZERO if zero_share is None else zero_share) * peak):
        out["state"] = "moved"
    else:
        out["state"] = "same"
    return out


def tiles():
    """The 24 tiles (6 across, 4 down) as (name, box)."""
    th, tw = (H - 2 * EDGE_ROWS) // 4, W // 6
    return [("row %d, column %d" % (ty + 1, tx + 1), (tx * tw, EDGE_ROWS + ty * th, (tx + 1) * tw, EDGE_ROWS + (ty + 1) * th))
            for ty in range(4) for tx in range(6)]


# ---- zones ------------------------------------------------------------------------------------------------
def zone_mask(zone):
    """A keep-list row as (mask over the picture, its bounding box)."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    if zone.get("poly"):
        d.polygon([tuple(p) for p in zone["poly"]], fill=255)
    else:
        x, y, w, h = zone["box"]
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=255)
    mask = np.asarray(m) > 0
    ys, xs = np.where(mask)
    if not len(ys):
        return mask, None
    return mask, (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def box_of(zone, pad=0):
    x, y, w, h = zone["box"]
    return (max(0, x - pad), max(EDGE_ROWS, y - pad), min(W, x + w + pad), min(H - EDGE_ROWS, y + h + pad))


def inside(inner, outer):
    return inner[0] >= outer[0] and inner[1] >= outer[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def overlaps(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def kept(eo, en, box, gain, glass=None):
    """One keep box: (agreement, the share of its old edge still there, corrected for the picture's own gain).
    With `glass`, the glass inside the box is left out (a door is kept by its frame, not by the view through it)."""
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        return None
    a, b, share = pair(eo, en, box, glass)
    if a is None or a.size == 0 or a.std() < FLAT * 0.5:
        return None
    _dx, _dy, peak, _zero = shift(a, b, search=3)
    # the old edge that is strong, and how strong the new picture is at the same pixels
    off = ~glass[y0:y1, x0:x1] if share else np.ones(a.shape, bool)
    strong = (a >= np.percentile(a[off], 70)) & off
    share = float(b[strong].mean() / max(a[strong].mean() * gain, 1e-6))
    return round(peak, 3), round(share, 3)


def gain_of(eo, en):
    """How much edge the picture as a whole gained: the middle of the 24 tiles' ratios."""
    ratios = []
    for _name, (x0, y0, x1, y1) in tiles():
        a, b = eo[y0:y1, x0:x1].mean(), en[y0:y1, x0:x1].mean()
        if a > 0.3:
            ratios.append(b / a)
    return float(np.median(ratios)) if ratios else 1.0


def rise(fo, fn, mask, gain):
    """One empty zone: (how many times more its fine edge rose than the picture's did, by how many levels)."""
    a, b = float(fo[mask].mean()), float(fn[mask].mean())
    return round((b + 1.0) / (a * gain + 1.0), 3), round(b - a * gain, 2)


def _starts(lo, hi, size, step):
    """Where windows of `size` start so that they cover lo..hi in steps of `step` (one window when it fits)."""
    if hi - lo <= size:
        return [lo]
    out = list(range(lo, hi - size, step))
    return out + [hi - size]


def cells(mask, box):
    """The overlapping cells a large empty zone is judged in: [(mask of the zone inside the cell, the cell's box)].
    None for a zone that is small enough to be judged whole only."""
    x0, y0, x1, y1 = box
    if x1 - x0 <= CELL_FROM and y1 - y0 <= CELL_FROM:
        return []
    out = []
    for cy in _starts(y0, y1, CELL, CELL_STEP):
        for cx in _starts(x0, x1, CELL, CELL_STEP):
            m = np.zeros_like(mask)
            m[cy:min(cy + CELL, y1), cx:min(cx + CELL, x1)] = mask[cy:min(cy + CELL, y1), cx:min(cx + CELL, x1)]
            if int(m.sum()) >= CELL_MIN:
                out.append((m, (cx, cy, min(cx + CELL, x1), min(cy + CELL, y1))))
    return out


def look_cells():
    """The 120 px cells step 6 looks at: 16 across, 9 down (the last row laid over the one above it)."""
    ys = list(range(EDGE_ROWS, H - EDGE_ROWS - LOOK_CELL + 1, LOOK_CELL))
    if ys[-1] + LOOK_CELL < H - EDGE_ROWS:
        ys.append(H - EDGE_ROWS - LOOK_CELL)
    return [(x, y, x + LOOK_CELL, y + LOOK_CELL) for y in ys for x in range(0, W, LOOK_CELL)]


def lapvar(a):
    g = grey(a)[EDGE_ROWS:H - EDGE_ROWS]
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


# ---- the whole judgement ----------------------------------------------------------------------------------
def judge(old, new, points=(), keep=(), empty=(), allow=(), change=(), rev1=None, relight=False, windows=()):
    """Steps 2 to 6 for one version.

    old, new: fitted pictures. points: [{"name", "at", "kind"}] (exits, hotspots, feet, outline samples;
    kind "feet" is a point where people stand, "hotspot" a hotspot's own point).
    keep / empty / allow / change / windows: keep-list rows. rev1: the revision-1 picture (step 5); None skips it.
    Returns {"verdict": PASS / LOOK / REFUSED, "refused": [words], "look": [words], "lines": [report lines],
             "figures": {...}, "marks": what the preview draws}."""
    eo, en = edges(old), edges(new)
    refused, look, lines, marks = [], [], [], {"moved": [], "gone": [], "added": [], "different": []}
    fig = {}
    allow_boxes = [box_of(z) if z.get("box") else zone_mask(z)[1] for z in allow]
    change_boxes = [box_of(z) for z in change if z.get("box")]
    glass = glass_mask(windows)
    coarse = []                 # the coarse edge maps, made when first needed

    def coarse_maps():
        if not coarse:
            coarse.extend([edges(old, FLOOR_BLUR), edges(new, FLOOR_BLUR)])
        return coarse

    # step 2: nothing moved
    sl = slice(EDGE_ROWS, H - EDGE_ROWS)
    dx, dy, peak, zero = shift(eo[sl], en[sl])
    fig["shift"] = [dx, dy]; fig["agree"] = round(zero, 3)
    if peak < DIFFERENT * 0.75:
        refused.append("this is a different picture: nothing in it lines up with the one in the game")
    elif max(abs(dx), abs(dy)) > SHIFT_WHOLE and peak - zero >= 0.02:
        refused.append("the whole picture moved %s" % _way(dx, dy))
    # the 24 tiles are measured first: their middle agreement is what a registered point is held against
    tile_moved, tile_diff, tile_agree = [], [], []
    for name, box in tiles():
        if any(inside(box, c) for c in change_boxes):
            continue
        got = moved(eo, en, box)
        if got["state"] != "flat":
            tile_agree.append(got["agree"])
        if got["state"] == "moved":
            tile_moved.append((name, box, got))
        elif got["state"] == "different":
            tile_diff.append((name, box))
    middle = max(float(np.median(tile_agree)) if tile_agree else 1.0, REL_FLOOR)
    g_rel, g_edge = (RELIGHT_GONE_REL, RELIGHT_GONE_EDGE) if relight else (GONE_REL, GONE_EDGE)
    worst = (0, None)
    n_checked = 0
    lost, on_glass, floor = [], [], []
    for p in points:
        box = window(p["at"])
        kind = p.get("kind")
        if any(c[0] <= p["at"][0] < c[2] and c[1] <= p["at"][1] < c[3] for c in change_boxes):
            continue        # what is inside a change box is meant to change; its outline is held below
        # A point that lies on glass is held by what is round the glass (the door's post, its handle, the
        # window's frame): the view through it may be changed on purpose (5.2's window line).
        a, b, _share = pair(eo, en, box, glass)
        if a is None:
            on_glass.append(p["name"])
            continue
        got = moved(eo, en, box, glass=glass)
        if got["state"] == "flat":
            continue
        n_checked += 1
        d = max(abs(got["dx"]), abs(got["dy"]))
        if got["state"] == "moved":
            # The lines of a floor's boards are no proof that the floor moved: a floor drawn again has other
            # boards. A point where people stand has moved only if the coarse drawing round it (the floor's
            # outline, what stands on it) reads as moved too.
            if kind == "feet" and _floor_moved(coarse_maps(), p["at"], glass) is None:
                floor.append(p["name"])
                marks["different"].append(box)
                continue
            refused.append("%s moved %s" % (p["name"], _way(got["dx"], got["dy"])))
            marks["moved"].append(box)
            continue
        # Not found moved within the search: is the drawing under the point still the one in the game? A door
        # slid further than the search, or painted out, agrees with nothing ("different"), or agrees where it
        # was far less than the picture's own tiles do (the measure "nothing vanished" uses).
        here = shift(a, b, search=SHIFT_POINT)[2]
        allowed = any(q and q[0] <= p["at"][0] < q[2] and q[1] <= p["at"][1] < q[3] for q in allow_boxes)
        if kind == "hotspot" and not allowed:
            # the named addition set on a hotspot's own object (a laptop at the computer): the allow box wins
            near = _auto_box(p["at"])
            allowed = any(q and overlaps(near, q) for q in allow_boxes)
        if not allowed and (got["state"] == "different" or here / middle < g_rel):
            if kind == "feet":
                # A floor drawn again (other boards, sunlight on it), or a relight whose window throws a grid
                # of light across it: the floor cannot move on its own. It is refused only when the floor's
                # outline and what stands on it moved; otherwise it is shown.
                far = _floor_moved(coarse_maps(), p["at"], glass)
                if far is not None:
                    refused.append("%s moved %s (the floor's edge and what stands round it)" % (p["name"], _way(*far)))
                    marks["moved"].append(box)
                else:
                    floor.append(p["name"])
                    marks["different"].append(box)
            else:
                lost.append(p["name"])
                marks["gone"].append(box)
        elif d > worst[0] and d <= SHIFT_POINT:
            worst = (d, p["name"])
    lost = list(dict.fromkeys(lost))
    floor = list(dict.fromkeys(floor))
    if floor:
        look.append("the floor is drawn differently where people stand (other boards, or light lying across it), at "
                    "%s: nothing round %s moved; look that nothing new stands there"
                    % ("; ".join(_short(n) for n in floor[:4]) + (", and %d more" % (len(floor) - 4) if len(floor) > 4 else ""),
                       "it" if len(floor) == 1 else "them"))
    if lost:
        tail = "no longer lines up with the picture in the game (moved further than %d px, or gone)" % SEARCH
        if len(lost) <= 3:
            refused += ["%s %s" % (name, tail) for name in lost]
        else:
            refused.append("%d of the registered spots no longer line up with the picture in the game (moved further "
                           "than %d px, or gone): %s, and %d more" % (len(lost), SEARCH, "; ".join(lost[:3]), len(lost) - 3))
    lines.append(("moved", "the whole picture %d, %d px; %d point%s checked%s%s"
                  % (dx, dy, n_checked, "" if n_checked == 1 else "s",
                     ", the furthest off %d px (%s)" % worst if worst[1] else ", none off by a pixel",
                     "; %d lie%s wholly on glass and cannot be held (%s)" % (len(on_glass), "s" if len(on_glass) == 1 else "",
                                                                          "; ".join(on_glass[:3])) if on_glass else "")))
    fig["floor_points"] = len(floor)
    fig["tiles_moved"] = len(tile_moved); fig["tiles_different"] = len(tile_diff)
    fig["tiles_agree"] = round(middle, 3)
    if len(tile_diff) >= MOVED_TILES * 24 and not any("different picture" in r for r in refused):
        refused.append("this is not the same picture: %d of its 24 parts are drawn differently" % len(tile_diff))
        marks["different"] += [b for _n, b in tile_diff]
        tile_diff = []
    if len(tile_moved) >= MOVED_TILES * 24:
        refused.append("the picture is moved or enlarged everywhere (%d of 24 tiles are off, by up to %d px)"
                       % (len(tile_moved), max(max(abs(g["dx"]), abs(g["dy"])) for _n, _b, g in tile_moved)))
        marks["moved"] += [b for _n, b, _g in tile_moved]
    else:
        for name, box, got in tile_moved:
            if not any(overlaps(box, a) for a in allow_boxes):
                look.append("the part of the picture at %s sits %s" % (name, _way(got["dx"], got["dy"])))
            marks["different"].append(box)
    for name, box in tile_diff:
        if not any(overlaps(box, a) for a in allow_boxes):
            look.append("the part of the picture at %s is drawn differently" % name)
        marks["different"].append(box)

    # a change box: only its outline is held (5.1's named change)
    for z in [z for z in change if z.get("box")]:
        box = box_of(z, pad=24)
        # the outline is read on a coarse edge map (a 5 px blur: the roof line, the foot of the wall), whose
        # wide edges still agree a good deal where they were; so the offset is believed on a smaller gain
        co, cn = edges(old, 5.0), edges(new, 5.0)
        got = moved(co, cn, box, gain=0.03, zero_share=0.97)
        if got["state"] == "moved":
            refused.append("the outline of %s moved %s; a named change keeps its outline exactly"
                           % (z["name"], _way(got["dx"], got["dy"])))
            marks["moved"].append(box)
        lines.append(("change", "%s: its outline is %s" % (z["name"], "off by %d, %d px" % (got["dx"], got["dy"])
                                                           if got["state"] != "flat" else "too faint to measure")))

    # step 3: nothing vanished
    gain = gain_of(eo, en)
    fig["gain"] = round(gain, 3)
    weakest = None
    n_keep = 0
    for z in keep:
        box = box_of(z)
        if any(overlaps(box, c) for c in change_boxes) or box[2] - box[0] < 8 or box[3] - box[1] < 8:
            continue
        if z.get("auto") and any(a and overlaps(box, a) for a in allow_boxes):
            continue        # the named addition stands on this hotspot's own object: the allow box wins
        got = kept(eo, en, box, gain, glass)
        if got is None:
            continue
        n_keep += 1
        a, s = got
        rel = a / middle
        if (rel < g_rel and s < g_edge) if relight else (rel < g_rel or s < g_edge):
            # a thing slid inside its box agrees badly where it was and well a little way off: say "moved"
            far = moved(eo, en, box_of(z, pad=SEARCH), glass=glass)
            wide = kept(eo, en, box_of(z, pad=FAINT_PAD), gain, glass)
            if far["state"] == "moved":
                refused.append("%s moved %s" % (z["name"], _way(far["dx"], far["dy"])))
                marks["moved"].append(box)
            elif wide is not None and wide[0] / middle >= FAINT_REL and s >= g_edge:
                # a pale thing on a wall that became lighter: its outline is where it was, and it has its edge
                look.append("%s %s fainter, or drawn differently inside %s outline, which is where it was: look "
                            "that %s still there" % ((z["name"],) + (("are", "their", "they are") if _are(z)
                                                                     else ("is", "its", "it is"))))
                marks["different"].append(box)
            else:
                refused.append("%s %s gone" % (z["name"], "are" if _are(z) else "is"))
                marks["gone"].append(box)
        if weakest is None or rel < weakest[0]:
            weakest = (round(rel, 3), s, z["name"])
    fig["keep_weakest"] = list(weakest[:2]) if weakest else None
    lines.append(("vanished", "%d thing%s checked%s" % (n_keep, "" if n_keep == 1 else "s",
                  "; the weakest is %s (it agrees %.2f as well as the picture does, with %d%% of its edge; gone "
                  "under %.2f %s %d%%)" % (weakest[2], weakest[0], round(100 * weakest[1]), g_rel,
                                          "and" if relight else "or", round(100 * g_edge))
                  if weakest else "")))

    if relight:
        # 5.7: a relight is not judged for added things (a night gains pools of light). One thing can be read
        # without a false alarm: a small empty place of the keep list that gained fine edge against what is
        # round it. It is shown, never refused; everything else in a relight is read by eye against the day.
        fo, fn = edges(old, 1.0), edges(new, 1.0)
        most = None
        for z in empty:
            mask, box = zone_mask(z)
            if (box is None or cells(mask, box) or any(a and overlaps(box, a) for a in allow_boxes)
                    or any(overlaps(box, c) for c in change_boxes)):
                continue
            ring = np.zeros_like(mask)
            ring[max(EDGE_ROWS, box[1] - RELIGHT_RING):min(H - EDGE_ROWS, box[3] + RELIGHT_RING),
                 max(0, box[0] - RELIGHT_RING):min(W, box[2] + RELIGHT_RING)] = True
            ring &= ~mask
            a = float(fo[ring].mean())
            if a < 0.3:
                continue
            r, by = rise(fo, fn, mask, float(fn[ring].mean()) / a)
            if most is None or r > most[0]:
                most = (r, by, z["name"])
            if r >= RELIGHT_ADD_RISE and by >= RELIGHT_ADD_MIN:
                look.append("something new may be on %s (its fine edge rose %.2f times against what is round it; shown "
                            "from %.2f): a relight is not refused for it, so look at it beside the day picture"
                            % (z["name"], r, RELIGHT_ADD_RISE))
                marks["different"].append(box)
        fig["relight_empty_most"] = list(most[:2]) if most else None
        if most:
            lines.append(("added", "not judged in a relight; of the keep list's small empty places the largest rise is "
                          "%.2f times, on %s (shown from %.2f). Read the picture by eye beside its day picture for "
                          "anything else that was added" % (most[0], most[2], RELIGHT_ADD_RISE)))
        else:
            lines.append(("added", "not judged in a relight: read the picture by eye beside its day picture for "
                          "anything that was added (a lamp, a blanket, a bench)"))
    else:
        # step 4: nothing was added
        fo, fn = edges(old, 1.0), edges(new, 1.0)
        fgain = gain_of(fo, fn)
        most, cell_most, n_empty = None, None, 0
        redrawn = []
        for z in empty:
            mask, box = zone_mask(z)
            if box is None or any(overlaps(box, a) for a in allow_boxes) or any(overlaps(box, c) for c in change_boxes):
                continue
            r, by = rise(fo, fn, mask, fgain)
            # one thing on a wide floor is lost in the floor's mean: a wide zone is judged cell by cell as well
            hit, same = [], []
            for cmask, cbox in cells(mask, box):
                cr, cby = rise(fo, fn, cmask, fgain)
                if cr >= CELL_RISE and cby >= CELL_ADD:
                    hit.append(cbox)
                if cell_most is None or cr > cell_most[0]:
                    cell_most = (cr, cby, z["name"])
                ca, cb = eo[cbox[1]:cbox[3], cbox[0]:cbox[2]], en[cbox[1]:cbox[3], cbox[0]:cbox[2]]
                if ca.std() >= FLAT * 0.5:
                    same.append(shift(ca, cb, search=SHIFT_POINT)[2])
            # A floor DRAWN AGAIN (its boards run another way, sunlight lies on it) gains and loses fine edge
            # everywhere: "something new" cannot be read from its lines. It is shown, not refused; a thing set
            # down on a floor that is still the same drawing leaves the rest of it agreeing, and is refused.
            if len(same) >= REDRAWN_CELLS and float(np.median(same)) < REDRAWN:
                redrawn.append(z["name"])
                look.append("%s is drawn again (other boards, or light lying across it; its parts agree %.2f with the "
                            "game's, the same drawing reads 0.84 or more): look that nothing new stands on it%s"
                            % (z["name"], float(np.median(same)),
                               "; its lines are most changed %s" % _where(min(b[0] for b in hit), max(b[2] for b in hit), box)
                               if hit else ""))
                marks["different"] += hit
            elif hit:
                refused.append("something new is on %s (%s)" % (z["name"], _where(min(b[0] for b in hit), max(b[2] for b in hit), box)))
                marks["added"] += hit
            elif r >= ADDED_RISE and by >= ADDED_MIN:
                refused.append("something new is on %s" % z["name"])
                marks["added"].append(box)
            n_empty += 1
            if most is None or r > most[0]:
                most = (r, by, z["name"])
        fig["empty_most"] = list(most[:2]) if most else None
        fig["empty_cell_most"] = list(cell_most[:2]) if cell_most else None
        if redrawn:
            fig["redrawn"] = redrawn
        lines.append(("added", "%d place%s checked%s%s" % (n_empty, "" if n_empty == 1 else "s",
                      "; the largest rise is %.2f times, on %s (new from %.2f times)" % (most[0], most[2], ADDED_RISE)
                      if most else "",
                      "; the largest in any %d px part of a wide one is %.2f times, on %s (new from %.2f)"
                      % (CELL, cell_most[0], cell_most[2], CELL_RISE)
                      if cell_most else "")))
        # step 5: sharper than revision 1
        if rev1 is not None:
            base, now = lapvar(rev1), lapvar(new)
            ratio = now / max(base, 1e-6)
            fig["sharp"] = [round(base, 1), round(now, 1)]
            lines.append(("sharper", "%.1f times the picture the place had before the overhaul (%.0f against %.0f; "
                          "passes at %.1f, shown to you from %.1f)" % (ratio, now, base, SHARP_PASS, SHARP_LOOK)))
            if ratio < SHARP_LOOK:
                refused.append("it is not sharper than the old picture (%.1f times; it has to reach %.1f)"
                               % (ratio, SHARP_LOOK))
            elif ratio < SHARP_PASS:
                look.append("it is only %.1f times as sharp as the old picture (%.1f is a clear pass)" % (ratio, SHARP_PASS))
        # step 6: everything else that changed is shown. The 320 px tiles miss a thing the size of a window
        # pane or a poster, so the picture is read again in 120 px cells (for LOOK only, never a refusal).
        whole = ("different picture", "not the same picture", "whole picture moved", "moved or enlarged everywhere")
        if not any(w in r for r in refused for w in whole):
            told = [b for b in marks["different"]]
            named = marks["added"] + marks["gone"] + marks["moved"]     # what a refusal has already named
            fine = []
            for box in look_cells():
                cpt = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
                if (any(b[0] <= cpt[0] < b[2] and b[1] <= cpt[1] < b[3] for b in told)
                        or any(overlaps(box, c) for c in change_boxes) or any(a and overlaps(box, a) for a in allow_boxes)
                        or any(overlaps(box, n) for n in named)):
                    continue
                a, b = eo[box[1]:box[3], box[0]:box[2]], en[box[1]:box[3], box[0]:box[2]]
                if a.std() < FLAT:
                    continue
                if shift(a, b, search=SHIFT_POINT)[2] < LOOK_DIFF:
                    fine.append(box)
            fig["cells_different"] = len(fine)
            marks["different"] += fine
            if len(fine) > LOOK_MANY:
                look.append("%d parts of the picture are drawn differently (tinted on the preview), among them at %s"
                            % (len(fine), ", ".join("(%d, %d)" % (b[0], b[1]) for b in fine[:3])))
            else:
                look += ["the part of the picture at (%d, %d) is drawn differently (a window's view, or a thing on a wall: "
                         "tinted on the preview)" % (b[0], b[1]) for b in fine]
    if allow:
        look.append("it has what was asked for: %s" % "; ".join(z["name"] for z in allow))
    refused = list(dict.fromkeys(refused))      # one outline sampled at several points says a thing once
    verdict = "REFUSED" if refused else ("LOOK" if look else "PASS")
    return {"verdict": verdict, "refused": refused, "look": look, "lines": lines, "figures": fig, "marks": marks}


def _auto_box(pt):
    """The box kept round a hotspot's point without being written down, as (x0, y0, x1, y1)."""
    h = AUTO_BOX // 2
    return (pt[0] - h, pt[1] - h, pt[0] - h + AUTO_BOX, pt[1] - h + AUTO_BOX)


def _floor_moved(maps, pt, glass=None):
    """Has the floor's outline, and what stands on the floor round a standing point, moved? (dx, dy), or None.
    Read on the coarse edge maps, where the lines between boards are gone, in a window wide enough to hold a
    wall's foot or a table's leg."""
    co, cn = maps
    got = moved(co, cn, window(pt, FLOOR_WIDE[0], FLOOR_WIDE[1]), glass=glass)
    return (got["dx"], got["dy"]) if got["state"] == "moved" else None


def _short(name):
    """"a row of 3, at x 760" from "the floor where people stand (a row of 3, at x 760)"."""
    return name[name.index("(") + 1:name.rindex(")")] if "(" in name and name.endswith(")") else name


def _are(zone):
    return not zone.get("auto") and _plural(zone["name"])


def _way(dx, dy):
    parts = []
    if dx:
        parts.append("%d px %s" % (abs(dx), "right" if dx > 0 else "left"))
    if dy:
        parts.append("%d px %s" % (abs(dy), "down" if dy > 0 else "up"))
    return " and ".join(parts) or "0 px"


def _where(x0, x1, box):
    """Where along a wide zone a thing was found, in a person's words."""
    w = float(box[2] - box[0])
    if x1 - x0 > 0.6 * w:
        return "all along it"
    mid = (x0 + x1) / 2.0 - box[0]
    side = "at its left end" if mid < w / 3 else ("at its right end" if mid > 2 * w / 3 else "in its middle")
    return "%s, from x %d to %d" % (side, x0, x1)


def _plural(name):
    if " and " in name.split(",")[0]:
        return True
    first = name.split(",")[0].split(" on ")[0].split(" by ")[0].split(" in ")[0].split(" at ")[0].strip()
    return first.endswith("s") and not first.endswith("ss")


# ---- step 7: the preview ----------------------------------------------------------------------------------
def preview(old, new, path, points=(), keep=(), empty=(), allow=(), change=(), marks=None, title=None, windows=()):
    """Old beside new at half size, every point and zone drawn on both; what a verdict names is tinted on the new."""
    def half(a):
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").resize((W // 2, H // 2), Image.LANCZOS)

    sheet = Image.new("RGB", (W + 8, H // 2 + 28), (20, 18, 28))
    for k, a in enumerate((old, new)):
        im = half(a).convert("RGBA")
        over = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        if k == 1 and marks:
            for key, col in (("different", (255, 200, 60, 70)), ("moved", (232, 51, 79, 110)), ("gone", (232, 51, 79, 110)),
                             ("added", (232, 51, 79, 110))):
                for b in marks.get(key, []):
                    d.rectangle([b[0] // 2, b[1] // 2, b[2] // 2, b[3] // 2], fill=col)
        for rows, col in ((keep, (90, 220, 120, 255)), (empty, (90, 180, 255, 255)), (allow, (255, 209, 102, 255)),
                          (change, (230, 90, 230, 255)), (windows, (150, 240, 255, 255))):
            for z in rows:
                if z.get("poly"):
                    pts = [(p[0] // 2, p[1] // 2) for p in z["poly"]]
                    d.line(pts + [pts[0]], fill=col, width=2)
                else:
                    x, y, w, h = z["box"]
                    d.rectangle([x // 2, y // 2, (x + w) // 2, (y + h) // 2], outline=col, width=2)
        for p in points:
            x, y = p["at"][0] // 2, p["at"][1] // 2
            d.line([x - 7, y, x + 7, y], fill=(255, 255, 255, 255), width=2)
            d.line([x, y - 7, x, y + 7], fill=(255, 255, 255, 255), width=2)
        sheet.paste(Image.alpha_composite(im, over).convert("RGB"), (k * (W // 2 + 8), 28))
    d = ImageDraw.Draw(sheet)
    d.text((8, 8), (title or "") + "   left: in the game   right: the render   green: kept  blue: must stay empty  "
           "gold: allowed  pale blue: glass  red: what the verdict names  amber: drawn differently", fill=(240, 236, 220))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    sheet.save(path, quality=88)
    return path


def main(argv):
    if len(argv) != 2:
        print(__doc__); raise SystemExit(1)
    old, _ = load(argv[0])
    new, note = load(argv[1])
    got = judge(old, new, rev1=old)
    print("fit       %s" % note)
    for key, text in got["lines"]:
        print("%-9s %s" % (key, text))
    print("figures   %s" % got["figures"])
    print("verdict   %s %s" % (got["verdict"], "; ".join(got["refused"] or got["look"])))


if __name__ == "__main__":
    main(sys.argv[1:])
