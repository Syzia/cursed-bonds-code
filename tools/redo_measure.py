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
  VANISHED    inside a keep box: the agreement of the two edge maps (the
              best within 3 px) against the agreement of the picture's 24
              tiles (a heavy redraw lowers both; an object taken away lowers
              only its own box), and how much of the old edge is still
              there. An object taken away leaves the wall behind it.
  ADDED       inside an empty zone: the amount of fine edge (1 px blur),
              against how much the picture as a whole gained. A jacket, a
              cup or a scatter of leaves is fine edge where there was none.
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
SHARP_PASS = 2.0            # times the revision-1 picture's figure
SHARP_LOOK = 1.3
# A relight (5.7): a night picture loses edge in its dark corners, so "vanished" has thresholds of its own
# and "added" and "sharper" are not judged.
RELIGHT_GONE_REL = 0.30      # a relight: gone only when BOTH are under. Of the eight pairs the game has, the weakest
RELIGHT_GONE_EDGE = 0.50     # kept thing is a window lit at night: 0.39 of its agreement, 43% of its edge.


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


def window(pt, size=WINDOW):
    """(x0, y0, x1, y1) of the window round a point, kept inside the picture."""
    x0 = int(min(max(pt[0] - size // 2, 0), W - size))
    y0 = int(min(max(pt[1] - size // 2, EDGE_ROWS), H - EDGE_ROWS - size))
    return x0, y0, x0 + size, y0 + size


def moved(eo, en, box, limit=SHIFT_POINT, gain=None, zero_share=None):
    """One window: {"state": "flat" / "same" / "moved" / "different", dx, dy, agree}."""
    x0, y0, x1, y1 = box
    a, b = eo[y0:y1, x0:x1], en[y0:y1, x0:x1]
    if a.std() < FLAT:
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


def kept(eo, en, box, gain):
    """One keep box: (agreement, the share of its old edge still there, corrected for the picture's own gain)."""
    x0, y0, x1, y1 = box
    a, b = eo[y0:y1, x0:x1], en[y0:y1, x0:x1]
    if a.size == 0 or a.std() < FLAT * 0.5:
        return None
    _dx, _dy, peak, _zero = shift(a, b, search=3)
    # the old edge that is strong, and how strong the new picture is at the same pixels
    strong = a >= np.percentile(a, 70)
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


def lapvar(a):
    g = grey(a)[EDGE_ROWS:H - EDGE_ROWS]
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


# ---- the whole judgement ----------------------------------------------------------------------------------
def judge(old, new, points=(), keep=(), empty=(), allow=(), change=(), rev1=None, relight=False):
    """Steps 2 to 6 for one version.

    old, new: fitted pictures. points: [{"name", "at"}] (exits, hotspots, feet, outline samples).
    keep / empty / allow / change: keep-list rows. rev1: the revision-1 picture (step 5); None skips it.
    Returns {"verdict": PASS / LOOK / REFUSED, "refused": [words], "look": [words], "lines": [report lines],
             "figures": {...}, "marks": what the preview draws}."""
    eo, en = edges(old), edges(new)
    refused, look, lines, marks = [], [], [], {"moved": [], "gone": [], "added": [], "different": []}
    fig = {}
    allow_boxes = [box_of(z) if z.get("box") else zone_mask(z)[1] for z in allow]
    change_boxes = [box_of(z) for z in change if z.get("box")]

    # step 2: nothing moved
    sl = slice(EDGE_ROWS, H - EDGE_ROWS)
    dx, dy, peak, zero = shift(eo[sl], en[sl])
    fig["shift"] = [dx, dy]; fig["agree"] = round(zero, 3)
    if peak < DIFFERENT * 0.75:
        refused.append("this is a different picture: nothing in it lines up with the one in the game")
    elif max(abs(dx), abs(dy)) > SHIFT_WHOLE and peak - zero >= 0.02:
        refused.append("the whole picture moved %s" % _way(dx, dy))
    worst = (0, None)
    n_checked = 0
    for p in points:
        box = window(p["at"])
        if any(c[0] <= p["at"][0] < c[2] and c[1] <= p["at"][1] < c[3] for c in change_boxes):
            continue        # what is inside a change box is meant to change; its outline is held below
        got = moved(eo, en, box)
        if got["state"] == "flat":
            continue
        n_checked += 1
        d = max(abs(got["dx"]), abs(got["dy"]))
        if got["state"] == "moved":
            refused.append("%s moved %s" % (p["name"], _way(got["dx"], got["dy"])))
            marks["moved"].append(box)
        elif got["state"] == "same" and d > worst[0] and d <= SHIFT_POINT:
            worst = (d, p["name"])
    lines.append(("moved", "the whole picture %d, %d px; %d point%s checked%s"
                  % (dx, dy, n_checked, "" if n_checked == 1 else "s",
                     ", the furthest off %d px (%s)" % worst if worst[1] else ", none off by a pixel")))
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
    fig["tiles_moved"] = len(tile_moved); fig["tiles_different"] = len(tile_diff)
    middle = max(float(np.median(tile_agree)) if tile_agree else 1.0, REL_FLOOR)
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
    g_rel, g_edge = (RELIGHT_GONE_REL, RELIGHT_GONE_EDGE) if relight else (GONE_REL, GONE_EDGE)
    for z in keep:
        box = box_of(z)
        if any(overlaps(box, c) for c in change_boxes) or box[2] - box[0] < 8 or box[3] - box[1] < 8:
            continue
        got = kept(eo, en, box, gain)
        if got is None:
            continue
        n_keep += 1
        a, s = got
        rel = a / middle
        if (rel < g_rel and s < g_edge) if relight else (rel < g_rel or s < g_edge):
            refused.append("%s %s gone" % (z["name"], "are" if not z.get("auto") and _plural(z["name"]) else "is"))
            marks["gone"].append(box)
        if weakest is None or rel < weakest[0]:
            weakest = (round(rel, 3), s, z["name"])
    fig["keep_weakest"] = list(weakest[:2]) if weakest else None
    lines.append(("vanished", "%d thing%s checked%s" % (n_keep, "" if n_keep == 1 else "s",
                  "; the weakest is %s (it agrees %.2f as well as the picture does, with %d%% of its edge; gone "
                  "under %.2f %s %d%%)" % (weakest[2], weakest[0], round(100 * weakest[1]), g_rel,
                                          "and" if relight else "or", round(100 * g_edge))
                  if weakest else "")))

    if not relight:
        # step 4: nothing was added
        fo, fn = edges(old, 1.0), edges(new, 1.0)
        fgain = gain_of(fo, fn)
        most = None
        for z in empty:
            mask, box = zone_mask(z)
            if box is None or any(overlaps(box, a) for a in allow_boxes) or any(overlaps(box, c) for c in change_boxes):
                continue
            r, by = rise(fo, fn, mask, fgain)
            if r >= ADDED_RISE and by >= ADDED_MIN:
                refused.append("something new is on %s" % z["name"])
                marks["added"].append(box)
            if most is None or r > most[0]:
                most = (r, by, z["name"])
        fig["empty_most"] = list(most[:2]) if most else None
        lines.append(("added", "%d place%s checked%s" % (len(empty), "" if len(empty) == 1 else "s",
                      "; the largest rise is %.2f times, on %s (new from %.2f times)" % (most[0], most[2], ADDED_RISE)
                      if most else "")))
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
    if allow:
        look.append("it has what was asked for: %s" % "; ".join(z["name"] for z in allow))
    verdict = "REFUSED" if refused else ("LOOK" if look else "PASS")
    return {"verdict": verdict, "refused": refused, "look": look, "lines": lines, "figures": fig, "marks": marks}


def _way(dx, dy):
    parts = []
    if dx:
        parts.append("%d px %s" % (abs(dx), "right" if dx > 0 else "left"))
    if dy:
        parts.append("%d px %s" % (abs(dy), "down" if dy > 0 else "up"))
    return " and ".join(parts) or "0 px"


def _plural(name):
    if " and " in name.split(",")[0]:
        return True
    first = name.split(",")[0].split(" on ")[0].split(" by ")[0].split(" in ")[0].split(" at ")[0].strip()
    return first.endswith("s") and not first.endswith("ss")


# ---- step 7: the preview ----------------------------------------------------------------------------------
def preview(old, new, path, points=(), keep=(), empty=(), allow=(), change=(), marks=None, title=None):
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
                          (change, (230, 90, 230, 255))):
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
           "gold: allowed  red: what the verdict names  amber: drawn differently", fill=(240, 236, 220))
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
