"""
Build the ComfyUI workflows that draw the game's icons, thirty to a sheet.

    python3 tools/make_icon_workflow.py            # all three sheets
    python3 tools/make_icon_workflow.py 1          # just sheet 1
    python3 tools/make_icon_workflow.py --names    # rewrite tools/icons/sheet_<n>.txt from ICONS

The game has 88 icon names (`ICONS` in game/ui_icons.rpy). Until an icon has a
picture, the game draws its kanji on a seal with the word underneath; a
picture at `game/images/icons/ic_<name>.png` (96x96, white lines on clear)
replaces it with no script change.

Each sheet is one picture of 6 x 5 white line icons on black. A sheet's
workflow loads a blank grid (`icon_grid.png`, so the cells come back where
tools/cut_icons.py expects them) and asks Nano Banana Pro for the sheet twice
(two candidates, fixed seeds). It writes, into `~/Desktop/JJK Game images/phase2/`:

    icons_sheet_<n>.json     drag it into the LOCAL ComfyUI and press Run
    icon_grid.png            the blank grid (also copied to ComfyUI's input folder)

The results land in ~/ComfyUI-Shared/output as `icons_sheet<n>_a_0000N_.png`
and `icons_sheet<n>_b_0000N_.png`: the letter is the box, whatever order they
finished in. Then:

    python3 tools/cut_icons.py <that picture> tools/icons/sheet_<n>.txt

Which icons are on which sheet, and in what order, is `tools/icons/sheet_<n>.txt`
(one name a line, left to right, top row first). Those files are generated
from `ICONS` by --names, and every run checks that the three files together
hold exactly the names of `ICONS`, each once, so the sheets and the table
cannot disagree. What each icon should look like is `DRAW` below; the model is
never told a name from the game.

Cost: Nano Banana Pro is a paid partner node, about $0.16 a picture at 1K or
2K (ComfyUI's own price list), and each candidate box is one picture: about
$0.32 a sheet, $0.96 for the three. Nothing runs on this Mac's GPU.
"""
import sys, os, re, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from raster import Img

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
OUT = os.path.join(IMAGES, "phase2")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
NAMES_DIR = os.path.join(ROOT, "tools", "icons")

COLS, ROWS = 6, 5
PER_SHEET = COLS * ROWS
SHEETS = 3
GRID = "icon_grid.png"
GRID_SIZE = (1500, 1200)             # 5:4, the nearest shape the model offers to 6 x 5 cells
GRID_LINE = (48, 48, 48)             # dark enough that cut_icons.py reads it as background
CANDIDATES = 2
COST = 0.16                          # Nano Banana Pro, a picture, at 1K or 2K

# What to draw for each icon name. Plain objects, no words, nothing from the
# series: the model is given these lines and nothing else about the game.
DRAW = {
    # HUD
    "map": "a folded paper map with a location pin standing on it",
    "journal": "a closed notebook with a ribbon bookmark hanging out of it",
    "menu": "three short horizontal bars stacked one above the other",
    "back": "an arrow curving round to point left",
    "close": "a bold X made of two crossed strokes",
    "stay": "a location pin with a tick mark inside it",
    "stamina_low": "a battery that is almost empty, with one small bar left",
    "moon": "a crescent moon with two small stars",
    "skip": "two triangles side by side pointing right, like a fast-forward button",
    # journal
    "people": "the head and shoulders of two people side by side",
    "missions": "a rolled paper scroll with a round wax seal",
    "stats": "three upright bars rising in height from left to right",
    "equipment": "a tall paper charm strip hanging from a knotted cord",
    "inventory": "a drawstring pouch tied at the neck",
    "story": "an open book lying flat",
    "memories": "a framed photograph of a hill and a sun",
    "now": "a round wall clock with two hands",
    "go": "a thick arrow pointing right inside a circle",
    # map
    "area_heart": "a Japanese torii gate with a round tree beside it",
    "area_school": "a school building with a round clock on its front gable",
    "area_dorms": "a two-storey house with four square windows and a door",
    "area_staff": "a hall with four pillars under a wide tiled roof",
    "area_grounds": "two wooden practice swords crossed",
    "area_mountain": "a mountain range of three peaks with a small sun above",
    "campus": "a five-storey pagoda",
    "tokyo": "a city skyline with one tall lattice tower",
    "district": "a street post with two arrow signs pointing opposite ways",
    "lock": "a closed padlock",
    "news": "a large four-pointed sparkle with a small sparkle beside it",
    # places
    "place_gate": "a plain Japanese torii gate, seen from the front",
    "place_courtyard": "a stone garden lantern",
    "place_classroom": "a school desk and chair seen from the side",
    "place_cafeteria": "a meal tray holding a bowl and a cup",
    "place_training": "a wooden training dummy post with two arms",
    "place_dojo": "a martial-arts jacket tied with a belt",
    "place_dorm_common": "a sofa with two cushions",
    "place_dorm": "a single bed with a pillow, seen from the side",
    "place_girls_dorm": "a door with a ribbon bow tied on its handle",
    "place_rooftop": "a tiled temple roof with upturned eaves and a small cloud above",
    "place_infirmary": "a medical cross inside a rounded square",
    "place_office": "a stuffed toy bear with stitched seams, sitting",
    "place_utahime_office": "a neat stack of papers with a writing brush lying beside it",
    "place_gojo_office": "three round dumplings on a skewer",
    "place_storehouse": "a wooden chest with a strip of paper sealed across its lid",
    "place_forest": "three tall cedar trees",
    "place_riverside": "a river winding between two banks with a few reeds",
    "place_ridge": "one sharp mountain peak with a small pennant on its top",
    "place_library": "a bookshelf with two rows of books",
    "place_later": "a traffic cone",
    # actions
    "sleep": "a pillow with a crescent moon above it",
    "night_bed": "a bed seen from the side with a crescent moon above it",
    "wait": "an hourglass",
    "study": "a pencil writing in an open notebook",
    "train": "a clenched fist with three short motion lines behind it",
    "swim": "a swimmer's head and one raised arm above two wavy lines",
    "eat": "a steaming bowl with a pair of chopsticks resting on it",
    "rest": "two adhesive bandages crossed",
    "think": "a person sitting cross-legged with hands on knees",
    "hold": "two cupped hands around a small flame",
    "tools": "a rack holding a staff, a spear and a sword upright",
    "armory": "a shield with a sword behind it",
    "veil": "a large dome drawn with a dashed line over a small hill",
    "car": "a car seen from the side",
    "board": "a noticeboard with three pinned notes",
    "release": "an open hand with a small bird flying up from it",
    "mission": "a pennant flag on a pole with a star on the flag",
    "act": "a hand with its index finger pointing, about to tap",
    # person choices
    "talk": "a speech bubble with three dots in it",
    "hang": "two paper cups touching in a toast",
    "lesson": "a blackboard on a stand with a triangle drawn on it and a pointer stick",
    "walk": "two simple figures walking side by side",
    "stargaze": "a telescope on a tripod aimed at a star",
    "confide": "a speech bubble with a keyhole in it",
    "stand": "two hands clasped in a handshake",
    "heart": "a heart",
    "invite": "the head and shoulders of one person with a plus sign beside them",
    # rooms and night
    "pc_open": "an open laptop computer",
    "cards_play": "two playing cards fanned out, one with a spade and one with a diamond",
    "fish_cast": "a fishing rod with its line and a fish on the hook",
    "lib_study": "a stack of three books with a pair of reading glasses on top",
    "look": "an open eye",
    "spot_vend": "a drinks vending machine",
    "night_gojo": "a crescent moon with a small flame beneath it",
    "night_out": "a cocktail glass with a small star above it",
    "market": "a market stall with a striped awning",
    "buy": "a coin dropping into an open hand",
    "take": "a hand reaching down to pick up a small box",
    "record": "a book with a medal and ribbon on its cover",
}

STYLE = ("Every icon is a flat white line drawing on the pure black background: one even, medium line "
         "weight with rounded ends, the same on every icon, drawn simply enough to read at a very small "
         "size. White lines only: no colour, no grey shading, no gradients, no shadows, no glow, no solid "
         "white shapes larger than a small dot. No words, letters, numbers or captions anywhere in the "
         "picture. Each icon sits in the middle of its own cell, fills about two thirds of the cell, and "
         "stays well clear of the cell's edges; no icon touches or crosses a grid line. All of them match "
         "as one clean set of user-interface icons.")


def icon_names():
    """The names of ICONS, in the table's order, read from game/ui_icons.rpy."""
    src = open(os.path.join(ROOT, "game", "ui_icons.rpy"), encoding="utf-8").read()
    m = re.search(r"^    ICONS = \{\n(.*?)^    \}", src, re.S | re.M)
    if not m:
        raise SystemExit("can't find ICONS in game/ui_icons.rpy")
    names = re.findall(r'^\s+"(\w+)":\s+\(u"', m.group(1), re.M)
    if len(names) != len(set(names)):
        raise SystemExit("ICONS names an icon twice")
    return names


def sheet_path(n):
    return os.path.join(NAMES_DIR, "sheet_%d.txt" % n)


def read_sheet(path):
    """A names file: one icon name a line, in cell order; `-` leaves a cell
    out; `#` starts a comment."""
    out = []
    for raw in open(path, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def write_names():
    names = icon_names()
    if len(names) > PER_SHEET * SHEETS:
        raise SystemExit("%d icons do not fit on %d sheets of %d" % (len(names), SHEETS, PER_SHEET))
    os.makedirs(NAMES_DIR, exist_ok=True)
    for n in range(1, SHEETS + 1):
        part = names[(n - 1) * PER_SHEET:n * PER_SHEET]
        with open(sheet_path(n), "w", encoding="utf-8") as f:
            f.write("# Icon sheet %d of %d: the names on it, left to right, top row first (%d x %d cells).\n"
                    % (n, SHEETS, COLS, ROWS))
            f.write("# Generated from ICONS (game/ui_icons.rpy) by: python3 tools/make_icon_workflow.py --names\n")
            f.write("# Read by tools/make_icon_workflow.py (what to ask for) and tools/cut_icons.py (what to cut).\n")
            f.write("\n".join(part) + "\n")
        print("sheet_%d.txt  %d names" % (n, len(part)))


def check_names():
    """The three files hold exactly the names of ICONS, each once, and every
    one has a line in DRAW. Returns the sheets as lists."""
    names = icon_names()
    sheets, seen = [], []
    for n in range(1, SHEETS + 1):
        if not os.path.exists(sheet_path(n)):
            raise SystemExit("no %s -- write the names files with --names" % sheet_path(n))
        part = read_sheet(sheet_path(n))
        if len(part) > PER_SHEET:
            raise SystemExit("sheet_%d.txt has %d names; a sheet holds %d" % (n, len(part), PER_SHEET))
        sheets.append(part)
        seen += [p for p in part if p != "-"]
    problems = []
    for name in sorted(set(seen)):
        if seen.count(name) > 1:
            problems.append("%r is on the sheets %d times" % (name, seen.count(name)))
    problems += ["%r is in ICONS but on no sheet" % x for x in names if x not in seen]
    problems += ["%r is on a sheet but not in ICONS" % x for x in sorted(set(seen)) if x not in names]
    problems += ["%r has no line in DRAW" % x for x in names if x not in DRAW]
    problems += ["DRAW has %r, which ICONS does not" % x for x in sorted(DRAW) if x not in names]
    if problems:
        raise SystemExit("the icon sheets and ICONS disagree (re-run with --names?):\n  " + "\n  ".join(problems))
    return sheets


def sheet_prompt(names):
    rows = []
    for r in range(ROWS):
        cells = names[r * COLS:(r + 1) * COLS]
        if not cells:
            break
        parts = []
        for c in range(COLS):
            if c < len(cells) and cells[c] != "-":
                parts.append("(%d) %s" % (c + 1, DRAW[cells[c]]))
            else:
                parts.append("(%d) leave this cell empty and black" % (c + 1))
        rows.append("Row %d, left to right: %s." % (r + 1, "; ".join(parts)))
    for r in range(len(rows), ROWS):
        rows.append("Row %d: leave all six cells empty and black." % (r + 1))
    return ("The attached picture is a black sheet divided by thin dark grey lines into a grid of %d columns "
            "and %d rows: %d equal cells. Keep the sheet and its grid exactly as they are and draw one "
            "small icon in each cell, in exactly this order.\n\n%s\n\n%s"
            % (COLS, ROWS, COLS * ROWS, "\n".join(rows), STYLE))


def write_grid(path):
    w, h = GRID_SIZE
    im = Img(w, h)
    for c in range(COLS + 1):
        x = min(w - 3, max(0, c * w // COLS - 1))
        im.rect(x, 0, x + 3, h, GRID_LINE)
    for r in range(ROWS + 1):
        y = min(h - 3, max(0, r * h // ROWS - 1))
        im.rect(0, y, w, y + 3, GRID_LINE)
    im.save(path)


def build(n, names):
    proto = json.load(open(os.path.join(ROOT, "tools", "comfy_nodes", "edit_nodes.json")))
    P, shell = proto["nodes"], proto["shell"]
    nodes, links = [], []
    ids = {"n": 0, "l": 0}

    def add(kind, pos, size=None, title=None):
        ids["n"] += 1
        node = copy.deepcopy(P[kind])
        node["id"], node["pos"], node["order"] = ids["n"], list(pos), ids["n"]
        if size: node["size"] = list(size)
        for i in node.get("inputs", []): i["link"] = None
        for o in node.get("outputs", []): o["links"] = [] if o.get("links") is not None else None
        if title: node["title"] = title
        node["widgets_values"] = list(node.get("widgets_values") or [])
        nodes.append(node)
        return node

    def wire(a, a_slot, b, b_input):
        ids["l"] += 1
        slot = next(i for i, x in enumerate(b["inputs"]) if x["name"] == b_input)
        kind = a["outputs"][a_slot]["type"]
        assert kind == b["inputs"][slot]["type"], (a["type"], b["type"], b_input)
        links.append([ids["l"], a["id"], a_slot, b["id"], slot, kind])
        if a["outputs"][a_slot]["links"] is None:
            a["outputs"][a_slot]["links"] = []
        a["outputs"][a_slot]["links"].append(ids["l"])
        b["inputs"][slot]["link"] = ids["l"]

    count = len([x for x in names if x != "-"])
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-520, -40], "size": [440, 440],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Icon sheet %d of %d: %d icons\n\n"
        "Run this in the **local ComfyUI**.\n\n"
        "1. The **Load Image** box should already show `%s` (a black sheet with a faint grid). If it "
        "shows an error, click **choose file to upload** and pick it from `JJK Game images/phase2`.\n"
        "2. Press **Run**.\n\n"
        "The two coloured boxes each draw the whole sheet once, so there are two versions to choose "
        "from: **A** on the top row, **B** under it.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, charged to your Comfy account).\n\n"
        "You don't need to save anything. The results go to ComfyUI's output folder and Claude picks "
        "them up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: "
        "a finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (n, SHEETS, count, GRID, CANDIDATES, CANDIDATES * COST)]})

    load = add("LoadImage", (-520, 440), (440, 420), title="Load Image: the blank grid")
    load["widgets_values"] = [GRID, "image"]

    prompt = sheet_prompt(names)
    groups = []
    for k in range(CANDIDATES):
        letter = "ab"[k]
        y = k * 620
        g = add("GeminiImage2Node", (0, y), (420, 540), title="Nano Banana Pro: sheet %d, version %s" % (n, letter.upper()))
        w = g["widgets_values"]
        # A fixed seed for each box, so a Run that stops on a rate limit can be
        # pressed again and reuse what finished. 5:4 is the grid's own shape;
        # 2K costs the same as 1K and gives each cell twice the pixels.
        w[0], w[2], w[3], w[4], w[5], w[6] = prompt, 900 + n * 10 + k, "fixed", "5:4", "2K", "IMAGE"
        wire(load, 0, g, "images")
        s = add("SaveImage", (440, y), (520, 540), title="Version %s" % letter.upper())
        s["widgets_values"] = ["icons_sheet%d_%s" % (n, letter)]
        wire(g, 0, s, "images")
        groups.append({"id": k + 1, "title": "SHEET %d, VERSION %s" % (n, letter.upper()),
                       "bounding": [-20, y - 50, 1000, 600], "color": "#3f4f5a", "font_size": 24, "flags": {}})

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links, "groups": groups})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.55, "offset": [620, 120]}
    return wf


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--names" in argv:
        if len(argv) != 1:
            print(__doc__); raise SystemExit(1)
        write_names()
        check_names()
        raise SystemExit(0)
    if [a for a in argv if a.startswith("--")] or [a for a in argv if a not in [str(n) for n in range(1, SHEETS + 1)]]:
        print(__doc__); raise SystemExit(1)
    which = sorted(set(int(a) for a in argv)) or list(range(1, SHEETS + 1))
    sheets = check_names()

    os.makedirs(OUT, exist_ok=True)
    grid = os.path.join(OUT, GRID)
    write_grid(grid)
    if os.path.isdir(COMFY_INPUT):
        shutil.copy(grid, os.path.join(COMFY_INPUT, GRID))
    print("grid      %s (%dx%d, %d x %d cells)" % (GRID, GRID_SIZE[0], GRID_SIZE[1], COLS, ROWS))
    for n in which:
        names = sheets[n - 1]
        out = os.path.join(OUT, "icons_sheet_%d.json" % n)
        json.dump(build(n, names), open(out, "w"), indent=1)
        print("sheet %d   %d icons, %d versions, about $%.2f" % (n, len([x for x in names if x != "-"]),
                                                                CANDIDATES, CANDIDATES * COST))
        print("workflow -> %s" % out)
