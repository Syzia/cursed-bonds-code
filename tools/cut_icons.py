"""
Cut an icon sheet into the game's icons.

    python3 tools/cut_icons.py <sheet.png> tools/icons/sheet_1.txt
    python3 tools/cut_icons.py <sheet.png> tools/icons/sheet_1.txt --dry
    python3 tools/cut_icons.py <sheet.png> tools/icons/sheet_1.txt --only map,journal

The sheet is a render from tools/make_icon_workflow.py: 6 x 5 cells of white
line icons on black (`~/ComfyUI-Shared/output/icons_sheet<n>_a_0000N_.png`).
The names file says which icon is in which cell, left to right, top row first;
a line `-` leaves that cell out.

For each cell it finds the drawing (the bright pixels, ignoring the grid lines
at the cell's edge), squares it up with a margin, shrinks it to 96x96 and
writes `game/images/icons/ic_<name>.png`: pure white, with the drawing's
brightness as its alpha, so the black sheet becomes clear. The game picks an
icon up by its file name (`icon()` in game/ui_icons.rpy); nothing in the
script changes.

It always writes a preview, `shots/art/icons_<names file>__<render>.png`
(`icons_sheet_1__icons_sheet1_a_00001_.png`), one per render: every icon as
cut, on the game's dark panel, with its name under it. Look at it before
keeping the icons: the model can draw the wrong thing in a cell, or two cells
swapped. Then:

  --dry          write the preview only, and install nothing
  --only a,b     install just these names (to take most icons from one version
                 of a sheet and a few from the other)
  --out <dir>    install into another folder (tests)
  --any-sheet    cut even when the render's file name says another sheet than
                 the names file (a render that was renamed)

The render's name carries its sheet number (`icons_sheet1_a_...`), and so does
the names file (`sheet_1.txt`). When both do and they differ it stops before
cutting anything: sheet 1's picture cut by sheet 3's names would install every
icon under the wrong name.

It stops, installing nothing, if a named cell is empty. A drawing that touches
its cell's edge is reported (it may have been cut off), but still installed.
Pure Python: raster.py and pngread.py.
"""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pngread import load
from raster import Img, crop, resample
from layout_sheet import text, text_size, fill
from make_icon_workflow import COLS, ROWS, read_sheet, icon_names

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "game", "images", "icons")
SIZE = 96                   # the installed icon
DRAWN = 80                  # the drawing's longer side inside it
INSET = 0.05                # of a cell, ignored at each edge: the grid lines live there
INK = 110                   # a pixel this bright is part of a drawing
LOW, HIGH = 56, 208         # brightness -> alpha: the grid's grey is clear, a line is solid
PANEL, PAPER, GOLD, SEAL = (20, 17, 29), (236, 231, 245), (255, 209, 102), (232, 51, 79)


def brightness(im):
    """One byte a pixel: the brightest of red, green and blue."""
    ch = im.ch
    b = im.buf
    return bytearray(max(b[i], b[i + 1], b[i + 2]) for i in range(0, im.w * im.h * ch, ch))


def cut(lum, w, h, col, row):
    """(icon as a 96x96 RGBA Img or None when the cell is empty, touches edge)."""
    cw, chh = w / float(COLS), h / float(ROWS)
    x0, y0 = int(col * cw + cw * INSET), int(row * chh + chh * INSET)
    x1, y1 = int((col + 1) * cw - cw * INSET), int((row + 1) * chh - chh * INSET)
    left, top, right, bottom = x1, y1, x0 - 1, y0 - 1
    for y in range(y0, y1):
        line = lum[y * w + x0:y * w + x1]
        if max(line) < INK:
            continue
        xs = [k for k, v in enumerate(line) if v >= INK]
        left, right = min(left, x0 + xs[0]), max(right, x0 + xs[-1])
        top, bottom = min(top, y), max(bottom, y)
    if right < left:
        return None, False
    touches = left <= x0 or top <= y0 or right >= x1 - 1 or bottom >= y1 - 1
    # A square around the drawing, with the margin that makes it DRAWN of SIZE.
    side = max(right - left + 1, bottom - top + 1) * SIZE / float(DRAWN)
    cx, cy = (left + right + 1) / 2.0, (top + bottom + 1) / 2.0
    sx0, sy0 = int(round(cx - side / 2.0)), int(round(cy - side / 2.0))
    side = int(round(side))
    # The square may run past the cell's inset (never past its drawing): take
    # only what is inside the inset cell, so a neighbour or a grid line stays out.
    big = Img(side, side, alpha=True)
    for y in range(max(sy0, y0), min(sy0 + side, y1)):
        for x in range(max(sx0, x0), min(sx0 + side, x1)):
            v = lum[y * w + x]
            if v > LOW:
                a = min(255, (v - LOW) * 255 // (HIGH - LOW))
                i = ((y - sy0) * side + (x - sx0)) * 4
                big.buf[i:i + 4] = bytes((255, 255, 255, a))
    icon = resample(big, SIZE, SIZE)
    for p in range(SIZE * SIZE):                    # pure white whatever the averaging did
        if icon.buf[p * 4 + 3]:
            icon.buf[p * 4:p * 4 + 3] = b"\xff\xff\xff"
    return icon, touches


def preview(cells, path, title):
    """Every cell as cut, on the game's dark panel, named."""
    tile_w, tile_h = 200, 150
    sheet = Img(COLS * tile_w, 40 + ROWS * tile_h, fill=(7, 6, 12))
    text(sheet, 12, 12, title, GOLD, 2, back=None)
    for k, (name, icon, state) in enumerate(cells):
        ox, oy = (k % COLS) * tile_w, 40 + (k // COLS) * tile_h
        fill(sheet, ox + 4, oy + 4, ox + tile_w - 4, oy + tile_h - 4, PANEL)
        if icon is not None:
            for y in range(SIZE):
                for x in range(SIZE):
                    a = icon.buf[(y * SIZE + x) * 4 + 3]
                    if a:
                        sheet.blend(ox + (tile_w - SIZE) // 2 + x, oy + 12 + y, PAPER, a / 255.0)
            # and at the size the game most often shows it
            small = resample(icon, 40, 40)
            for y in range(40):
                for x in range(40):
                    a = small.buf[(y * 40 + x) * 4 + 3]
                    if a:
                        sheet.blend(ox + tile_w - 52 + x, oy + 12 + y, PAPER, a / 255.0)
        label = name if name != "-" else "(left out)"
        scale = 2 if text_size(label, 2)[0] <= tile_w - 16 else 1
        colour = SEAL if state in ("empty", "edge") else PAPER
        text(sheet, ox + (tile_w - text_size(label, scale)[0]) // 2, oy + 114, label, colour, scale, back=None)
        if state != "ok" and name != "-":
            text(sheet, ox + 10, oy + 134, {"empty": "empty cell", "edge": "touches the edge",
                                            "skipped": "not installed"}[state], colour, 1, back=None)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)


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

    only, dest = opt("--only"), opt("--out")
    dry = "--dry" in argv
    any_sheet = "--any-sheet" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2 or [a for a in argv if a.startswith("--") and a not in ("--dry", "--any-sheet")]:
        print(__doc__); raise SystemExit(1)
    sheet_png, names_file = os.path.expanduser(args[0]), args[1]
    said = re.search(r"sheet_?(\d+)", os.path.basename(sheet_png))
    want = re.search(r"sheet_?(\d+)", os.path.basename(names_file))
    if said and want and int(said.group(1)) != int(want.group(1)) and not any_sheet:
        raise SystemExit("%s looks like sheet %s, but %s is sheet %s -- nothing cut "
                         "(--any-sheet if the render was renamed)" % (
                             os.path.basename(sheet_png), said.group(1),
                             os.path.basename(names_file), want.group(1)))
    names = read_sheet(names_file)
    known = set(icon_names())
    if len(names) > COLS * ROWS:
        raise SystemExit("%s has %d names; a sheet has %d cells" % (names_file, len(names), COLS * ROWS))
    unknown = [n for n in names if n != "-" and n not in known]
    if unknown:
        raise SystemExit("not in ICONS (game/ui_icons.rpy): %s" % ", ".join(unknown))
    wanted = set(only.split(",")) if only else None
    if wanted and wanted - set(names):
        raise SystemExit("--only names icons this sheet doesn't have: %s" % ", ".join(sorted(wanted - set(names))))

    im = load(sheet_png)
    lum = brightness(im)
    cells, empty, edge = [], [], []
    for k, name in enumerate(names):
        if name == "-":
            cells.append((name, None, "ok"))
            continue
        icon, touches = cut(lum, im.w, im.h, k % COLS, k // COLS)
        state = "empty" if icon is None else "edge" if touches else "ok"
        if wanted is not None and name not in wanted and state != "empty":
            state = "skipped"
        if icon is None and (wanted is None or name in wanted):
            empty.append(name)
        if touches and (wanted is None or name in wanted):
            edge.append(name)
        cells.append((name, icon, state))

    stem = os.path.splitext(os.path.basename(names_file))[0]
    # Named after the render too, so version A's preview is still there after
    # version B is cut (the two are compared, and a few icons taken from B).
    render = os.path.splitext(os.path.basename(sheet_png))[0]
    shot = os.path.join(ROOT, "shots", "art", "icons_%s__%s.png" % (stem, render))
    preview(cells, shot, "%s  cut by %s  (large, and at 40 px)" % (os.path.basename(sheet_png), stem))
    print("sheet     %s  %dx%d" % (os.path.basename(sheet_png), im.w, im.h))
    print("preview -> %s" % shot)
    if edge:
        print("touching their cell's edge (look at them): %s" % ", ".join(edge))
    if empty:
        raise SystemExit("nothing drawn in the cell of: %s -- nothing installed" % ", ".join(empty))
    if dry:
        print("--dry: nothing installed")
        return
    dest = dest or DEST
    os.makedirs(dest, exist_ok=True)
    done = 0
    for name, icon, state in cells:
        if icon is None or state == "skipped":
            continue
        icon.save(os.path.join(dest, "ic_%s.png" % name))
        done += 1
    print("installed %d icons -> %s" % (done, dest))


if __name__ == "__main__":
    main(sys.argv[1:])
