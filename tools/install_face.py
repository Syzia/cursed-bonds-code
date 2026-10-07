"""
Blink and talk: prepare the close-up an editor is given, and put its answer
into the game.

    python3 tools/install_face.py --prepare yuji
    python3 tools/make_edit_workflow.py yuji --only blink,talk
    python3 tools/install_face.py "~/ComfyUI-Shared/output/yuji_blink_nanobanana_00001_.png" yuji blink
    python3 tools/install_face.py "~/ComfyUI-Shared/output/yuji_talk_nanobanana_00001_.png" yuji talk
    python3 tools/install_face.py --sheet        # every eye and mouth box, to look at

  A REDRAWN PERSON, whose set is staged and not in the game yet (docs/UI2_DESIGN.md D57):
    python3 tools/install_face.py --prepare yuji --sprite <staged>/char/yuji_neutral.png --images <folder>
    python3 tools/install_face.py <blink render> yuji blink --sprite <staged>/char/yuji_neutral.png \
            --images <folder> --stage <staged>

The game makes someone blink and talk by laying two small boxes over their
sprite: the eyes from `images/char/fx/fx_<who>_blink.png` and the mouth from
`fx_<who>_talk.png` (PHASE2_DESIGN.md D39, 4.5). Both are the neutral sprite
with only that box changed, on the same canvas.

WHERE THE BOXES COME FROM. For the sprites in the game: a person's row in
game/layout/faces.json when there is one, else VIEW_FACE in
game/view_stage.rpy (today's numbers). For a sprite given with --sprite the
boxes are MEASURED on that sprite: the edit is lined up with it, and the box
is where the two differ (the eyes for a blink, the mouth for a talk). A new
drawing puts the eyes and the mouth somewhere else, and the art-install role
may not edit a `.rpy` file.

--prepare cuts a square around the head from the neutral sprite (the game's
own, game/images/char/<who>_neutral.png, or the one --sprite names), puts it
on flat green, enlarges it to 1024 and writes `<who>_fx_in.png` into
~/Desktop/JJK Game images (and ComfyUI's input folder), with the square
recorded in masks/<who>_fx_crop.txt. Because the close-up comes from the
sprite itself, the answer maps straight back onto it. With --sprite the
square is found from the sprite's own outline (the top of the figure, a
little over a quarter of its height), not from the old boxes.

Installing takes the editor's picture, shrinks it back to the square, lines it
up with the sprite (editors nudge and zoom a picture by a pixel or two: scale
0.97 to 1.03 and 8 px either way are searched, scored on the skin and hair
around the box), matches any colour cast, and copies ONLY the eye box (blink)
or the mouth box (talk) onto a copy of the neutral sprite. For a MEASURED box
the line-up is refined to a quarter pixel and a quarter of a percent, the two
pictures are compared to within one pixel (a line half a pixel off is not a
change), and a box that cannot be right is REFUSED with nothing written: eyes
taller than a fifth of the close-up's square, a mouth taller than about 60 px,
or a mouth box that overlaps the eye box or lies above it. A staged sprite's
blink and mouth go in only with the whole set: --sprite naming any sprite but
the game's own needs --stage (D57). It prints how well
the box's rim meets the sprite, and writes a preview, shots/art/fx_<who>_<kind>.png
(the neutral head, the new one, and the two alternating boxes marked).

WHAT IT WRITES INTO game/layout/faces.json (the only tool that writes it;
3.2, D57), keeping every other person's rows:
  "blink_also": {who: [faces]}   on installing a blink: which of the person's
        other faces the blink also sits on, measured: the rim of the eye box
        on that face's sprite matches the neutral sprite's (a mean difference
        under 5 of 255, with no stroke crossing it). Without the row a blink
        shows on the calm face only.
  "eyes": {who: [x, y, w, h]}, "mouth": {who: [x, y, w, h]}   only when the
        box was measured (--sprite): on the 760x1400 canvas, like VIEW_FACE.
With --stage <folder> the picture goes to <folder>/fx/ and the rows to
<folder>/faces.json: tools/install_set.py puts a person's whole set in at once.

Gojo's eyes are under his blindfold and Yaga's behind his glasses: they have
no eye box, so no blink.

--root <dir> writes under another folder than the project (and reads the
sprites and faces.json there when it has them: a copy of the project).
--images <dir> uses another folder than ~/Desktop/JJK Game images. Pure Python.
"""
import sys, os, re, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, crop, resample

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
EDIT_SIZE = 1024
GREEN = (0, 177, 64)
KINDS = {"blink": "eyes", "talk": "mouth"}
SCALES = [0.97 + 0.01 * i for i in range(7)]
SHIFT = 8
SEAM_WARN = 14.0
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")
BLOCK = 4                   # the measured box: the edit and the sprite are compared in blocks this size
CHANGED = 22                # a block changed when it differs by more than this on average
BOX_PAD = 8                 # the measured box is the changed region grown by this
BOX_GROW = 1                # ... after its sides have each moved out by at most this many blocks (see measure_box)
# (Set on Yuji's first blink render, 7 Oct 2026: with these two the box is (332, 297) 92x44, the hand-set one
# within 4 px, and the blink sits on the four faces the hand-set table lists; the same render enlarged or
# shrunk 2% and slid 6 px gives the same box. A box 4 px lower already crosses the other faces' lashes.)
# The measured path lines the edit up finely (an editor's nudge is rarely a whole pixel): after the coarse
# search the shift is refined to a quarter pixel and the scale to a quarter of a percent.
FINE = ((1.0, 0.01), (0.5, 0.005), (0.25, 0.0025))
# A measured box that cannot be right is refused, not written. The limits are shares of the close-up's square
# (309 px for Yuji), set against the hand-set boxes of VIEW_FACE measured the same way: the tallest eye box
# is Nobara's (0.15 of her square), the widest Megumi's and Panda's (0.35); the tallest mouth box is Panda's
# and Yaga's (0.16), the widest Panda's muzzle (0.45; everyone else's is under 0.20, about 60 px).
EYES_MAX_H = 0.20           # the eye box is at most this tall (about 60 px on the 760 canvas) ...
EYES_MAX_W = 0.48           # ... and this wide
MOUTH_MAX_H = 0.195         # the mouth box: about 60 px tall ...
MOUTH_MAX_W = 0.48          # ... and no wider than the eyes may be
# blink_also: the eye box's rim on another face differs by less than RIM_MEAN on average, and no more than
# RIM_STROKE of it differs strongly (an eyebrow crossing it). Set on Yuji's first set, whose answer was known
# by eye (VIEW_BLINK_ALSO): happy, serious, sad and surprised read 3.9 to 4.3 with 0.5 to 1.3% crossed and
# take the blink; angry reads 5.7 with 3.2% crossed and keeps its own eyes.
RIM_MEAN = 5.0
RIM_STROKE = 0.025


def faces_path(root=None, stage=None):
    return os.path.join(stage, "faces.json") if stage else os.path.join(root or ROOT, "game", "layout", "faces.json")


def read_faces_file(path):
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(open(path, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("%s is not JSON: %s" % (path, e))
    if not isinstance(data, dict):
        raise SystemExit("%s must be a JSON object" % path)
    return data


def write_faces(path, who, blink_also=None, eyes=None, mouth=None):
    """Set one person's rows in faces.json, keeping everybody else's."""
    data = read_faces_file(path)
    for key, val in (("blink_also", blink_also), ("eyes", eyes), ("mouth", mouth)):
        if val is None:
            continue
        table = data.get(key)
        if not isinstance(table, dict):
            table = {}
        table[who] = [int(v) for v in val] if key != "blink_also" else list(val)
        data[key] = table
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(path + ".tmp", path)


def faces(root=None):
    """{who: {"eyes": box, "mouth": box}}: a person's row in game/layout/faces.json where there is one,
    else VIEW_FACE."""
    out = view_face()
    data = read_faces_file(faces_path(root))
    for key in ("eyes", "mouth"):
        for who, box in (data.get(key) or {}).items():
            if isinstance(box, list) and len(box) == 4:
                out.setdefault(who, {})[key] = tuple(int(v) for v in box)
    return out


def view_face():
    """VIEW_FACE, read from game/view_stage.rpy: {who: {"eyes": box, "mouth": box}}."""
    src = open(os.path.join(ROOT, "game", "view_stage.rpy"), encoding="utf-8").read()
    m = re.search(r"VIEW_FACE = \{(.*?)\n    \}", src, re.S)
    if not m:
        raise SystemExit("can't find VIEW_FACE in game/view_stage.rpy")
    out = {}
    for row in re.finditer(r'"(\w+)":\s*dict\((.*?)\)\s*,?\s*$', m.group(1), re.M):
        boxes = {}
        for b in re.finditer(r"(eyes|mouth)=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", row.group(2)):
            boxes[b.group(1)] = tuple(int(b.group(k)) for k in (2, 3, 4, 5))
        out[row.group(1)] = boxes
    if not out:
        raise SystemExit("VIEW_FACE in game/view_stage.rpy has no rows this tool can read")
    return out


def sprite_path(who, root=None):
    """The neutral sprite: the one under --root when that folder has it (a copy of the project), else the game's."""
    for base in dict.fromkeys([root or ROOT, ROOT]):
        p = os.path.join(base, "game", "images", "char", who + "_neutral.png")
        if os.path.exists(p):
            return p
    raise SystemExit("no sprite at %s" % p)


def head_square_alpha(sprite):
    """(X, Y, side) for a sprite whose boxes are not known yet: from the figure's own outline. The square
    starts just above the top of the hair and is a little over a quarter of the figure tall, centred on the
    head."""
    if sprite.ch != 4:
        raise SystemExit("the sprite has no alpha channel")
    w, h, b = sprite.w, sprite.h, sprite.buf
    rows = [y for y in range(h) if sum(1 for x in range(0, w, 2) if b[(y * w + x) * 4 + 3] > 24) >= 3]
    if not rows:
        raise SystemExit("the sprite is empty")
    y0, y1 = rows[0], rows[-1] + 1
    fh = y1 - y0
    side = min(max(260, int(fh * 0.27)), w, h)
    xs = [x for y in range(y0, min(h, y0 + int(fh * 0.12)), 2) for x in range(0, w, 2) if b[(y * w + x) * 4 + 3] > 128]
    cx = sorted(xs)[len(xs) // 2] if xs else w // 2
    X = max(0, min(w - side, cx - side // 2))
    Y = max(0, min(h - side, y0 - int(side * 0.04)))
    return X, Y, side


def head_square(who, face, sprite):
    """(X, Y, side): the square around the head the editor is given."""
    boxes = list(face.values())
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    side = int(max(260, 3 * max(x1 - x0, y1 - y0)))
    side = min(side, sprite.w, sprite.h)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    X = max(0, min(sprite.w - side, cx - side // 2))
    Y = max(0, min(sprite.h - side, cy - side // 2))
    return X, Y, side


def on_green(im):
    """An RGBA picture flattened onto the flat green the edit prompts name."""
    out = Img(im.w, im.h, fill=GREEN)
    if im.ch == 3:
        out.buf[:] = im.buf
        return out
    b, o = im.buf, out.buf
    for p in range(im.w * im.h):
        a = b[p * 4 + 3]
        if a:
            for k in range(3):
                o[p * 3 + k] = (b[p * 4 + k] * a + GREEN[k] * (255 - a)) // 255
    return out


def rgb(im):
    if im.ch == 3:
        return im
    out = Img(im.w, im.h)
    b, o = im.buf, out.buf
    o[0::3], o[1::3], o[2::3] = b[0::4], b[1::4], b[2::4]
    return out


def crop_record(images, who):
    return os.path.join(images, "masks", "%s_fx_crop.txt" % who)


def prepare(who, images=None, sprite_file=None, root=None):
    images = images or IMAGES
    face = faces(root).get(who)
    if sprite_file:
        # a staged sprite: a new drawing, so the old boxes say nothing about where its head is
        sprite_file = os.path.expanduser(sprite_file)
        if not os.path.exists(sprite_file):
            raise SystemExit("no sprite at %s" % sprite_file)
        sprite = load(sprite_file)
        X, Y, side = head_square_alpha(sprite)
        face = face or {"eyes": None, "mouth": None}
    else:
        if not face:
            raise SystemExit("%s has no row in VIEW_FACE (game/view_stage.rpy) or in faces.json" % who)
        sprite = load(sprite_path(who, root))
        X, Y, side = head_square(who, face, sprite)
    cut = on_green(crop(sprite, X, Y, X + side, Y + side))
    big = resample(cut, EDIT_SIZE, EDIT_SIZE)
    os.makedirs(os.path.join(images, "masks"), exist_ok=True)
    path = os.path.join(images, "%s_fx_in.png" % who)
    big.save(path)
    with open(crop_record(images, who), "w") as f:
        f.write("%d %d %d\n" % (X, Y, side))
    if images == IMAGES and os.path.isdir(COMFY_INPUT):
        import shutil
        shutil.copy(path, os.path.join(COMFY_INPUT, os.path.basename(path)))
    print("close-up  %dx%d of %s at (%d, %d) -> %dx%d" % (side, side, "the staged sprite" if sprite_file else "the sprite",
                                                        X, Y, EDIT_SIZE, EDIT_SIZE))
    print("edit in -> %s" % path)
    kinds = [k for k, key in sorted(KINDS.items()) if key in face]
    print("next: python3 tools/make_edit_workflow.py %s --only %s" % (who, ",".join(kinds)))
    return path


def sample(ed, fx, fy):
    """Bilinear sample of an RGB picture at a float position."""
    x0 = int(fx); y0 = int(fy)
    if x0 < 0: x0, fx = 0, 0.0
    if y0 < 0: y0, fy = 0, 0.0
    if x0 >= ed.w - 1: x0, fx = ed.w - 2, float(ed.w - 1)
    if y0 >= ed.h - 1: y0, fy = ed.h - 2, float(ed.h - 1)
    tx, ty = fx - x0, fy - y0
    a = (y0 * ed.w + x0) * 3
    b = a + 3
    c = a + ed.w * 3
    d = c + 3
    buf = ed.buf
    out = []
    for k in range(3):
        top = buf[a + k] + (buf[b + k] - buf[a + k]) * tx
        bot = buf[c + k] + (buf[d + k] - buf[c + k]) * tx
        out.append(top + (bot - top) * ty)
    return out


def _regions(grid, gw, gh):
    """[(blocks, x0, y0, x1, y1)] of the connected changed blocks (8-connected), the largest first."""
    seen = [bytearray(gw) for _y in range(gh)]
    out = []
    for sy in range(gh):
        for sx in range(gw):
            if not grid[sy][sx] or seen[sy][sx]:
                continue
            stack, n = [(sx, sy)], 0
            seen[sy][sx] = 1
            x0, y0, x1, y1 = sx, sy, sx, sy
            while stack:
                x, y = stack.pop()
                n += 1
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if 0 <= nx < gw and 0 <= ny < gh and grid[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = 1
                            stack.append((nx, ny))
            out.append((n, x0, y0, x1, y1))
    out.sort(key=lambda r: -r[0])
    return out


def measure_box(sprite, ref, ed, X, Y, side, s, dx, dy, cast, kind):
    """Where the lined-up edit differs from the sprite: the eye box (blink) or the mouth box (talk), on the
    sprite's canvas. None when nothing changed.

    The two are compared to within one pixel, both ways: a sample has changed by how far the edit there lies
    outside the range of the sprite's nine pixels round that place, or by how far the sprite's pixel lies
    outside the range of the edit one pixel round it, whichever is more. A picture that came back half a
    pixel off puts every ink line half a pixel off; a value part way across a line lies between its
    neighbours, so it is no change (counted as one, every line of the hair and the collar would join the
    box). A line that was taken away or drawn in lies outside the range on one of the two sides.

    That finds the heart of the change and misses its faint rim (a lid that only shifted a shade). So each
    side of the box then moves out, by at most BOX_GROW blocks, while the blocks just outside it differ
    plainly, pixel against pixel: enough to take the rim in, too little for a line that is merely half a
    pixel off to carry the box away along the hair."""
    c = side / 2.0
    gw = gh = side // BLOCK
    grid = [bytearray(gw) for _y in range(gh)]
    plain = [bytearray(gw) for _y in range(gh)]
    rb, eb = ref.buf, ed.buf
    for gy in range(gh):
        for gx in range(gw):
            tot, n, ptot = 0.0, 0, 0.0
            for yy in (gy * BLOCK + 1, gy * BLOCK + 3):
                for xx in (gx * BLOCK + 1, gx * BLOCK + 3):
                    j = ((Y + yy) * sprite.w + X + xx) * 4
                    if sprite.buf[j + 3] < 255 or not (0 < xx < side - 1 and 0 < yy < side - 1):
                        continue
                    ex, ey = c + (xx - c) / s - dx, c + (yy - c) / s - dy
                    v = sample(ed, ex, ey)
                    i0 = (yy * side + xx) * 3
                    ptot += max(abs(v[k] + cast[k] - rb[i0 + k]) for k in range(3))
                    worst = 0.0
                    for k in range(3):
                        lo = hi = rb[i0 + k]
                        for ny in (yy - 1, yy, yy + 1):
                            i = (ny * side + xx - 1) * 3 + k
                            a, b, d = rb[i], rb[i + 3], rb[i + 6]
                            if a < lo: lo = a
                            if b < lo: lo = b
                            if d < lo: lo = d
                            if a > hi: hi = a
                            if b > hi: hi = b
                            if d > hi: hi = d
                        e = v[k] + cast[k]
                        off = lo - e if e < lo else (e - hi if e > hi else 0.0)
                        if off > worst:
                            worst = off
                    if worst <= CHANGED:
                        # the other way: the sprite's pixel against the edit's own pixels one pixel round the
                        # place (its pixels, not samples between them, which are all blurred alike)
                        qx, qy = min(max(int(ex) - 1, 0), ed.w - 4), min(max(int(ey) - 1, 0), ed.h - 4)
                        for k in range(3):
                            lo, hi = 255, 0
                            for ny in range(qy, qy + 4):
                                i = (ny * ed.w + qx) * 3 + k
                                for a in eb[i:i + 12:3]:
                                    if a < lo: lo = a
                                    if a > hi: hi = a
                            e = rb[i0 + k] - cast[k]
                            off = lo - e if e < lo else (e - hi if e > hi else 0.0)
                            if off > worst:
                                worst = off
                    tot += worst
                    n += 1
            if n >= 3 and tot / n > CHANGED:
                grid[gy][gx] = 1
            if n >= 3 and ptot / n > CHANGED:
                plain[gy][gx] = 1
    found = [r for r in _regions(grid, gw, gh) if r[0] >= 3]
    if not found:
        return None
    n, x0, y0, x1, y1 = found[0]
    grew = True
    rest = found[1:]
    while grew:
        grew = False
        for r in list(rest):
            _n, a0, b0, a1, b1 = r
            gap_x = max(0, a0 - x1 - 1, x0 - a1 - 1)
            gap_y = max(0, b0 - y1 - 1, y0 - b1 - 1)
            # the other eye is on the same row, some way across; a piece of the mouth is right beside it
            near = (gap_y <= 2 and gap_x <= gw // 3) if kind == "blink" else (gap_x <= 3 and gap_y <= 3)
            if near:
                rest.remove(r)
                x0, y0, x1, y1 = min(x0, a0), min(y0, b0), max(x1, a1), max(y1, b1)
                grew = True
    for _step in range(BOX_GROW):
        cols, rows_ = range(max(0, x0), min(gw, x1 + 1)), range(max(0, y0), min(gh, y1 + 1))
        up = y0 > 0 and any(plain[y0 - 1][x] for x in cols)
        down = y1 < gh - 1 and any(plain[y1 + 1][x] for x in cols)
        left = x0 > 0 and any(plain[y][x0 - 1] for y in rows_)
        right = x1 < gw - 1 and any(plain[y][x1 + 1] for y in rows_)
        x0, y0, x1, y1 = x0 - left, y0 - up, x1 + right, y1 + down
    bx0 = max(0, X + x0 * BLOCK - BOX_PAD)
    by0 = max(0, Y + y0 * BLOCK - BOX_PAD)
    bx1 = min(sprite.w, X + (x1 + 1) * BLOCK + BOX_PAD)
    by1 = min(sprite.h, Y + (y1 + 1) * BLOCK + BOX_PAD)
    return (bx0, by0, bx1 - bx0, by1 - by0)


def boxes_overlap(a, b):
    return min(a[0] + a[2], b[0] + b[2]) > max(a[0], b[0]) and min(a[1] + a[3], b[1] + b[3]) > max(a[1], b[1])


def box_wrong(kind, box, side, rows, who):
    """Why a measured box cannot be the eyes (blink) or the mouth (talk), or None. `rows` is the faces.json
    the box would be written to: the person's other box, when it is there, must lie clear of this one, the
    eyes above the mouth."""
    x, y, w, h = box
    if kind == "blink":
        if h > side * EYES_MAX_H or w > side * EYES_MAX_W:
            return ("eyes are not %dx%d px on a head this size (at most %dx%d): the edit changed more than the "
                    "eyes, or came back moved further than it can be lined up"
                    % (w, h, int(side * EYES_MAX_W), int(side * EYES_MAX_H)))
    else:
        if w > side * MOUTH_MAX_W or h > side * MOUTH_MAX_H:
            return ("a mouth is not %dx%d px on a head this size (at most %dx%d): the edit changed more than the "
                    "mouth, or came back moved further than it can be lined up"
                    % (w, h, int(side * MOUTH_MAX_W), int(side * MOUTH_MAX_H)))
    other_key = "mouth" if kind == "blink" else "eyes"
    other = (rows.get(other_key) or {}).get(who)
    if isinstance(other, list) and len(other) == 4:
        eyes, mouth = (box, other) if kind == "blink" else (other, box)
        if boxes_overlap(eyes, mouth):
            return "it overlaps the %s box already measured, (%d, %d) %dx%d" % ((other_key,) + tuple(other))
        if mouth[1] < eyes[1] + eyes[3]:
            return "it puts the mouth beside or above the eyes (the %s box already measured is (%d, %d) %dx%d)" % (
                (other_key,) + tuple(other))
    return None


def rim_matches(neutral, other, box):
    """Does the rim of the eye box look the same on another face's sprite? (mean difference, share crossed)."""
    x, y, w, h = box
    tot, n, strong = 0.0, 0, 0
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if not (xx - x < 3 or x + w - xx <= 3 or yy - y < 3 or y + h - yy <= 3):
                continue
            j = (yy * neutral.w + xx) * 4
            if neutral.buf[j + 3] < 255 or other.buf[j + 3] < 255:
                continue
            d = sum(abs(neutral.buf[j + k] - other.buf[j + k]) for k in range(3)) / 3.0
            tot += d; n += 1
            if d > 48:
                strong += 1
    if not n:
        return 999.0, 1.0
    return tot / n, strong / float(n)


def blink_also(who, neutral_file, box):
    """The other faces a person's blink also sits on, measured on the sprites beside the neutral one."""
    neutral = load(neutral_file)
    folder = os.path.dirname(neutral_file)
    out = []
    for expr in EXPRESSIONS:
        if expr == "neutral":
            continue
        p = os.path.join(folder, "%s_%s.png" % (who, expr))
        if not os.path.exists(p):
            continue
        other = load(p)
        if (other.w, other.h, other.ch) != (neutral.w, neutral.h, 4):
            continue
        mean, crossed = rim_matches(neutral, other, box)
        ok = mean < RIM_MEAN and crossed <= RIM_STROKE
        print("   %-10s the eye box's rim differs by %.1f on average, %.1f%% of it strongly: %s"
              % (expr, mean, 100 * crossed, "the blink sits on it" if ok else "it keeps its own eyes"))
        if ok:
            out.append(expr)
    return out


def install(src, who, kind, images=None, root=None, sprite_file=None, stage=None):
    images = images or IMAGES
    root = root or ROOT
    if kind not in KINDS:
        raise SystemExit("the kind is blink or talk, not %r" % kind)
    measured = bool(sprite_file)
    if measured and not stage:
        # D57: a redrawn person's blink and mouth go in with the six sprites or not at all. Without --stage
        # this would lay the new drawing's eyes over the old sprites in the game.
        own = os.path.join(root, "game", "images", "char", who + "_neutral.png")
        if not os.path.exists(own):
            own = os.path.join(ROOT, "game", "images", "char", who + "_neutral.png")
        if os.path.realpath(os.path.expanduser(sprite_file)) != os.path.realpath(own):
            raise SystemExit("a staged sprite's blink and mouth go in only with the whole set: add --stage <staged "
                             "folder>, then tools/install_set.py")
    face = faces(root).get(who) or {}
    if not measured and KINDS[kind] not in face:
        raise SystemExit("%s has no %s box in VIEW_FACE (game/view_stage.rpy) or in faces.json: no %s for them"
                         % (who, KINDS[kind], kind))
    box = None if measured else face[KINDS[kind]]
    rec = crop_record(images, who)
    if not os.path.exists(rec):
        raise SystemExit("no %s: run `python3 tools/install_face.py --prepare %s` first, and edit the "
                         "close-up it writes" % (rec, who))
    X, Y, side = [int(v) for v in open(rec).read().split()]
    src = os.path.expanduser(src)
    if not os.path.exists(src):
        raise SystemExit("no picture at %s" % src)
    raw = rgb(load(src))
    if abs(raw.w - raw.h) > max(raw.w, raw.h) * 0.05:
        raise SystemExit("%s is %dx%d: the edit of a %s_fx_in.png close-up is square" % (src, raw.w, raw.h, who))
    ed = resample(raw, side, side)
    neutral_file = os.path.expanduser(sprite_file) if sprite_file else sprite_path(who, root)
    if not os.path.exists(neutral_file):
        raise SystemExit("no sprite at %s" % neutral_file)
    sprite = load(neutral_file)
    if sprite.ch != 4:
        raise SystemExit("%s has no alpha channel" % neutral_file)
    if X + side > sprite.w or Y + side > sprite.h:
        raise SystemExit("the close-up's square (%d, %d, %d) does not fit this sprite: run --prepare again with "
                         "the same --sprite" % (X, Y, side))
    ref = on_green(crop(sprite, X, Y, X + side, Y + side))
    c = side / 2.0

    def points_round(b):
        """Points to line the two up on: around the box (not in it: that is what changed), where the
        sprite is solid, every third pixel. With no box yet, the whole head."""
        pts = []
        if b is None:
            for y in range(SHIFT + 2, side - SHIFT - 2, 4):
                for x in range(SHIFT + 2, side - SHIFT - 2, 4):
                    if sprite.buf[((Y + y) * sprite.w + X + x) * 4 + 3] == 255:
                        pts.append((x, y))
            return pts
        bx, by, bw, bh = b[0] - X, b[1] - Y, b[2], b[3]
        pad = max(30, bw // 2)
        for y in range(max(SHIFT + 2, by - pad), min(side - SHIFT - 2, by + bh + pad), 3):
            for x in range(max(SHIFT + 2, bx - pad), min(side - SHIFT - 2, bx + bw + pad), 3):
                if bx - 2 <= x < bx + bw + 2 and by - 2 <= y < by + bh + 2:
                    continue
                if sprite.buf[((Y + y) * sprite.w + X + x) * 4 + 3] < 255:
                    continue
                pts.append((x, y))
        return pts

    def line_up(pts, fine=False, start=None):
        """(the mismatch before, (the mismatch, scale, dx, dy) at the best fit). fine: after the coarse search
        the best few are refined to a quarter pixel and a quarter of a percent (FINE). start: refine from
        there, with no coarse search."""
        def score(s, dx, dy):
            tot = 0.0
            for x, y in pts:
                v = sample(ed, c + (x - c) / s - dx, c + (y - c) / s - dy)
                i = (y * side + x) * 3
                tot += abs(v[0] - ref.buf[i]) + abs(v[1] - ref.buf[i + 1]) + abs(v[2] - ref.buf[i + 2])
            return tot / (3.0 * len(pts))

        before = score(1.0, 0, 0)
        best = (before, 1.0, 0, 0)
        per_scale = []
        for s in ([] if start else SCALES):
            here = None
            for dy in range(-SHIFT, SHIFT + 1, 2):
                for dx in range(-SHIFT, SHIFT + 1, 2):
                    e = score(s, dx, dy)
                    if e < best[0]:
                        best = (e, s, dx, dy)
                    if here is None or e < here[0]:
                        here = (e, s, dx, dy)
            per_scale.append(here)
        if not fine:
            _e, s, dx0, dy0 = best
            for dy in (dy0 - 1, dy0, dy0 + 1):
                for dx in (dx0 - 1, dx0, dx0 + 1):
                    e = score(s, dx, dy)
                    if e < best[0]:
                        best = (e, s, dx, dy)
            return before, best
        # A shift between two steps of the coarse search is answered there by a wrong scale, so the climb
        # starts from the best fit at each of the three best scales (and from no change at all), not from one.
        starts = [(score(*start),) + tuple(start)] if start else sorted(per_scale)[:3] + [(before, 1.0, 0, 0)]
        seen = {}

        def at(s, dx, dy):
            key = (round(s, 4), round(dx, 2), round(dy, 2))
            if key not in seen:
                seen[key] = score(*key)
            return seen[key]

        best = None
        for _e, s, dx, dy in starts:
            cur = (at(s, dx, dy), s, float(dx), float(dy))
            for step, sstep in FINE:
                for _round in range(24):
                    e, s0, x0, y0 = cur
                    near = [(s0, x0 + step, y0), (s0, x0 - step, y0), (s0, x0, y0 + step), (s0, x0, y0 - step)]
                    near += [(s0 + sstep, x0, y0), (s0 - sstep, x0, y0)]
                    near = [n for n in near if SCALES[0] - 0.01 <= n[0] <= SCALES[-1] + 0.01
                            and abs(n[1]) <= SHIFT + 1 and abs(n[2]) <= SHIFT + 1]
                    got = min((at(*n),) + n for n in near)
                    if got[0] >= e - 1e-9:
                        break
                    cur = got
            if best is None or cur[0] < best[0]:
                best = cur
        return before, best

    def cast_of(pts, s, dx, dy):
        cast = [0.0, 0.0, 0.0]
        for x, y in pts:
            v = sample(ed, c + (x - c) / s - dx, c + (y - c) / s - dy)
            i = (y * side + x) * 3
            for k in range(3):
                cast[k] += ref.buf[i + k] - v[k]
        return [v / len(pts) for v in cast]

    fpath = faces_path(root, os.path.expanduser(stage) if stage else None)
    whole = None
    if measured:
        pts = points_round(None)
        if len(pts) < 40:
            raise SystemExit("too little of the sprite in the close-up to line the edit up on")
        _b, whole = line_up(pts, fine=True)
        _e, s, dx, dy = whole
        box = measure_box(sprite, ref, ed, X, Y, side, s, dx, dy, cast_of(pts, s, dx, dy), kind)
        if box is None:
            raise SystemExit("REFUSED: the edit does not differ from the sprite anywhere: there is no %s to measure "
                             "(was the close-up edited?)" % KINDS[kind])
        if box[2] * box[3] > side * side * 0.25:
            raise SystemExit("REFUSED: the edit differs from the sprite over a quarter of the head (%dx%d px): it "
                             "changed more than the %s, so its box cannot be measured. Run the edit again."
                             % (box[2], box[3], KINDS[kind]))
        why = box_wrong(kind, box, side, read_faces_file(fpath), who)
        if why:
            raise SystemExit("REFUSED: the %s box measured on this sprite, (%d, %d) %dx%d, cannot be right: %s. "
                             "Nothing was written. Run the edit again."
                             % ((KINDS[kind],) + tuple(box) + (why,)))
        print("measured  the %s box on this sprite: (%d, %d) %dx%d" % ((KINDS[kind],) + tuple(box)))
    bx, by, bw, bh = box[0] - X, box[1] - Y, box[2], box[3]
    pts = points_round(box)
    if len(pts) < 40:
        raise SystemExit("too little of the sprite around the %s box to line the edit up on" % KINDS[kind])
    if measured:
        before, (err, s, dx, dy) = line_up(pts, fine=True, start=whole[1:])
    else:
        before, (err, s, dx, dy) = line_up(pts)

    # The colour cast, measured on the same points.
    cast = cast_of(pts, s, dx, dy)

    out = Img(sprite.w, sprite.h, alpha=True)
    out.buf[:] = sprite.buf
    seam, n_seam = 0.0, 0
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            j = ((Y + y) * sprite.w + X + x) * 4
            if not sprite.buf[j + 3]:
                continue
            v = sample(ed, c + (x - c) / s - dx, c + (y - c) / s - dy)
            new = [max(0, min(255, int(v[k] + cast[k] + 0.5))) for k in range(3)]
            if x in (bx, bx + bw - 1) or y in (by, by + bh - 1):
                seam += sum(abs(new[k] - sprite.buf[j + k]) for k in range(3)) / 3.0
                n_seam += 1
            out.buf[j:j + 3] = bytes(new)
    seam = seam / max(1, n_seam)

    if stage:
        dest = os.path.join(os.path.expanduser(stage), "fx", "fx_%s_%s.png" % (who, kind))
    else:
        dest = os.path.join(root, "game", "images", "char", "fx", "fx_%s_%s.png" % (who, kind))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    out.save(dest)
    if measured:
        print("lined up  scale %.4f, shift (%+.2f, %+.2f); mismatch around the box %.1f -> %.1f" % (s, dx, dy, before, err))
    else:
        print("lined up  scale %.2f, shift (%+d, %+d); mismatch around the box %.1f -> %.1f" % (s, dx, dy, before, err))
    print("colour    shifted by (%+.1f, %+.1f, %+.1f) to meet the sprite" % tuple(cast))
    print("rim       the box's edge differs from the sprite by %.1f on average" % seam)
    if seam > SEAM_WARN:
        print("!! the edge of the %s box will show: the edit changed more than the %s (or the box is too "
              "small for it). Look at the preview before trusting it." % (KINDS[kind], KINDS[kind]))
    if err > 18:
        print("!! the face around the box still differs a lot after lining up: the edit may have moved "
              "the head. Look at the preview.")
    prev = os.path.join(root, "shots", "art", "fx_%s_%s.png" % (who, kind))
    preview(sprite, out, X, Y, side, box, prev)
    print("preview -> %s" % prev)
    print("%s -> %s" % ("staged" if stage else "installed", dest))
    # faces.json: what the game reads in place of the tables in view_stage.rpy
    also = None
    if kind == "blink":
        print("which other faces the blink sits on:")
        also = blink_also(who, neutral_file, box)
    write_faces(fpath, who, blink_also=also,
                eyes=box if measured and kind == "blink" else None,
                mouth=box if measured and kind == "talk" else None)
    said = []
    if also is not None:
        said.append("blink_also %s" % json.dumps(also))
    if measured:
        said.append("%s %s" % (KINDS[kind], json.dumps([int(v) for v in box])))
    if said:
        print("faces.json -> %s (%s: %s)" % (fpath, who, "; ".join(said)))
    return dest


def big(im, s):
    out = Img(im.w * s, im.h * s)
    for y in range(im.h):
        row = im.buf[y * im.w * 3:(y + 1) * im.w * 3]
        line = bytearray()
        for x in range(im.w):
            line += row[x * 3:x * 3 + 3] * s
        for k in range(s):
            o = ((y * s + k) * out.w) * 3
            out.buf[o:o + len(line)] = line
    return out


def frame(im, x, y, w, h, c, t=2):
    for k in range(t):
        im.row_fill(y + k, x, x + w, c)
        im.row_fill(y + h - 1 - k, x, x + w, c)
    for yy in range(y, y + h):
        im.row_fill(yy, x, x + t, c)
        im.row_fill(yy, x + w - t, x + w, c)


def preview(sprite, fx, X, Y, side, box, path, s=2):
    a = big(on_green(crop(sprite, X, Y, X + side, Y + side)), s)
    b = big(on_green(crop(fx, X, Y, X + side, Y + side)), s)
    sheet = Img(a.w * 2 + 8, a.h, fill=(20, 18, 28))
    for y in range(a.h):
        o = y * sheet.w * 3
        sheet.buf[o:o + a.w * 3] = a.buf[y * a.w * 3:(y + 1) * a.w * 3]
        o += (a.w + 8) * 3
        sheet.buf[o:o + b.w * 3] = b.buf[y * b.w * 3:(y + 1) * b.w * 3]
    for ox in (0, a.w + 8):
        frame(sheet, ox + (box[0] - X) * s - 2, (box[1] - Y) * s - 2, box[2] * s + 4, box[3] * s + 4, (255, 209, 102))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)


def sheet(root=None, s=3):
    """Every person's eye and mouth box on their neutral sprite."""
    root = root or ROOT
    table = dict((who, f) for who, f in faces(root).items() if f)
    names = sorted(table)
    cw, chh = 240, 220
    cols = 4
    rows = (len(names) + cols - 1) // cols
    out = Img(cw * s * cols, chh * s * rows, fill=(40, 38, 50))
    for k, who in enumerate(names):
        face = table[who]
        sprite = load(sprite_path(who, root))
        boxes = list(face.values())
        cx = (min(b[0] for b in boxes) + max(b[0] + b[2] for b in boxes)) // 2
        cy = (min(b[1] for b in boxes) + max(b[1] + b[3] for b in boxes)) // 2
        x0 = max(0, min(sprite.w - cw, cx - cw // 2))
        y0 = max(0, min(sprite.h - chh, cy - chh // 2 - 10))
        cell = big(on_green(crop(sprite, x0, y0, x0 + cw, y0 + chh)), s)
        ox, oy = (k % cols) * cw * s, (k // cols) * chh * s
        for y in range(cell.h):
            o = ((oy + y) * out.w + ox) * 3
            out.buf[o:o + cell.w * 3] = cell.buf[y * cell.w * 3:(y + 1) * cell.w * 3]
        for key, col in (("eyes", (90, 220, 230)), ("mouth", (255, 209, 102))):
            if key in face:
                b = face[key]
                frame(out, ox + (b[0] - x0) * s, oy + (b[1] - y0) * s, b[2] * s, b[3] * s, col)
        frame(out, ox, oy, cw * s, chh * s, (7, 6, 12), 3)
    path = os.path.join(root, "shots", "layout", "view_faces.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    print("%d people, in name order: %s" % (len(names), ", ".join(names)))
    print("blue: the eye box (blink)   gold: the mouth box (talk)")
    print("sheet -> %s" % path)
    return path


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

    root, images, sprite_file, stage = opt("--root"), opt("--images"), opt("--sprite"), opt("--stage")
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if flags == ["--sheet"] and not args:
        sheet(root)
    elif flags == ["--prepare"] and len(args) == 1:
        prepare(args[0], images, sprite_file, root)
    elif not flags and len(args) == 3:
        install(args[0], args[1], args[2], images, root, sprite_file, stage)
    else:
        print(__doc__); raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
