"""
Blink and talk: prepare the close-up an editor is given, and put its answer
into the game.

    python3 tools/install_face.py --prepare yuji
    python3 tools/make_edit_workflow.py yuji --only blink,talk
    python3 tools/install_face.py "~/ComfyUI-Shared/output/yuji_blink_nanobanana_00001_.png" yuji blink
    python3 tools/install_face.py "~/ComfyUI-Shared/output/yuji_talk_nanobanana_00001_.png" yuji talk
    python3 tools/install_face.py --sheet        # every eye and mouth box, to look at

The game makes someone blink and talk by laying two small boxes over their
sprite: the eyes from `images/char/fx/fx_<who>_blink.png` and the mouth from
`fx_<who>_talk.png` (PHASE2_DESIGN.md D39, 4.5). Both are the neutral sprite
with only that box changed, on the same canvas. The boxes are VIEW_FACE in
game/view_stage.rpy; this tool reads them from there.

--prepare cuts a square around the head from the GAME's own neutral sprite
(game/images/char/<who>_neutral.png), puts it on flat green, enlarges it to
1024 and writes `<who>_fx_in.png` into ~/Desktop/JJK Game images (and
ComfyUI's input folder), with the square recorded in
masks/<who>_fx_crop.txt. Because the close-up comes from the sprite itself,
the answer maps straight back onto it.

Installing takes the editor's picture, shrinks it back to the square, lines it
up with the sprite (editors nudge and zoom a picture by a pixel or two: scale
0.97 to 1.03 and 8 px either way are searched, scored on the skin and hair
around the box), matches any colour cast, and copies ONLY the eye box (blink)
or the mouth box (talk) onto a copy of the neutral sprite. It prints how well
the box's rim meets the sprite, and writes a preview, shots/art/fx_<who>_<kind>.png
(the neutral head, the new one, and the two alternating boxes marked).

Gojo's eyes are under his blindfold and Yaga's behind his glasses: they have
no eye box, so no blink.

--root <dir> writes under another folder than the project. --images <dir>
uses another folder than ~/Desktop/JJK Game images. Pure Python.
"""
import sys, os, re

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


def faces():
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


def sprite_path(who):
    p = os.path.join(ROOT, "game", "images", "char", who + "_neutral.png")
    if not os.path.exists(p):
        raise SystemExit("no sprite at %s" % p)
    return p


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


def prepare(who, images=None):
    images = images or IMAGES
    face = faces().get(who)
    if not face:
        raise SystemExit("%s has no row in VIEW_FACE (game/view_stage.rpy)" % who)
    sprite = load(sprite_path(who))
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
    print("close-up  %dx%d of the sprite at (%d, %d) -> %dx%d" % (side, side, X, Y, EDIT_SIZE, EDIT_SIZE))
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


def install(src, who, kind, images=None, root=None):
    images = images or IMAGES
    root = root or ROOT
    if kind not in KINDS:
        raise SystemExit("the kind is blink or talk, not %r" % kind)
    face = faces().get(who)
    if not face or KINDS[kind] not in face:
        raise SystemExit("%s has no %s box in VIEW_FACE (game/view_stage.rpy): no %s for them"
                         % (who, KINDS[kind], kind))
    box = face[KINDS[kind]]
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
    sprite = load(sprite_path(who))
    if sprite.ch != 4:
        raise SystemExit("%s has no alpha channel" % sprite_path(who))
    ref = on_green(crop(sprite, X, Y, X + side, Y + side))

    # Points to line the two up on: around the box (not in it: that is what
    # changed), where the sprite is solid, every third pixel.
    bx, by, bw, bh = box[0] - X, box[1] - Y, box[2], box[3]
    other = [b for k, b in face.items() if k != KINDS[kind]]
    pad = max(30, bw // 2)
    pts = []
    for y in range(max(SHIFT + 2, by - pad), min(side - SHIFT - 2, by + bh + pad), 3):
        for x in range(max(SHIFT + 2, bx - pad), min(side - SHIFT - 2, bx + bw + pad), 3):
            if bx - 2 <= x < bx + bw + 2 and by - 2 <= y < by + bh + 2:
                continue
            if sprite.buf[((Y + y) * sprite.w + X + x) * 4 + 3] < 255:
                continue
            pts.append((x, y))
    if len(pts) < 40:
        raise SystemExit("too little of the sprite around the %s box to line the edit up on" % KINDS[kind])
    c = side / 2.0

    def score(s, dx, dy):
        tot = 0.0
        for x, y in pts:
            v = sample(ed, c + (x - c) / s - dx, c + (y - c) / s - dy)
            i = (y * side + x) * 3
            tot += abs(v[0] - ref.buf[i]) + abs(v[1] - ref.buf[i + 1]) + abs(v[2] - ref.buf[i + 2])
        return tot / (3.0 * len(pts))

    before = score(1.0, 0, 0)
    best = (before, 1.0, 0, 0)
    for s in SCALES:
        for dy in range(-SHIFT, SHIFT + 1, 2):
            for dx in range(-SHIFT, SHIFT + 1, 2):
                e = score(s, dx, dy)
                if e < best[0]:
                    best = (e, s, dx, dy)
    _e, s, dx0, dy0 = best
    for dy in (dy0 - 1, dy0, dy0 + 1):
        for dx in (dx0 - 1, dx0, dx0 + 1):
            e = score(s, dx, dy)
            if e < best[0]:
                best = (e, s, dx, dy)
    err, s, dx, dy = best

    # The colour cast, measured on the same points.
    cast = [0.0, 0.0, 0.0]
    for x, y in pts:
        v = sample(ed, c + (x - c) / s - dx, c + (y - c) / s - dy)
        i = (y * side + x) * 3
        for k in range(3):
            cast[k] += ref.buf[i + k] - v[k]
    cast = [v / len(pts) for v in cast]

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

    dest = os.path.join(root, "game", "images", "char", "fx", "fx_%s_%s.png" % (who, kind))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    out.save(dest)
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
    print("installed -> %s" % dest)
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
    table = faces()
    names = sorted(table)
    cw, chh = 240, 220
    cols = 4
    rows = (len(names) + cols - 1) // cols
    out = Img(cw * s * cols, chh * s * rows, fill=(40, 38, 50))
    for k, who in enumerate(names):
        face = table[who]
        sprite = load(sprite_path(who))
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

    root, images = opt("--root"), opt("--images")
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if flags == ["--sheet"] and not args:
        sheet(root)
    elif flags == ["--prepare"] and len(args) == 1:
        prepare(args[0], images)
    elif not flags and len(args) == 3:
        install(args[0], args[1], args[2], images, root)
    else:
        print(__doc__); raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
