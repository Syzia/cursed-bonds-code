"""
The campus record as a working sketch and as a page.

    python3 tools/campus_plan.py              # CAMPUS2.md, campus_plan.png and one crop for each area
    python3 tools/campus_plan.py --md         # only tools/bgs/CAMPUS2.md (plain Python, no Pillow)
    python3 tools/campus_plan.py --pins       # the pin targets the area-map prompts will ask for
    python3 tools/campus_plan.py --ref        # campus_plan_ref.png and its six pieces: colour blocks, no words
    python3 tools/campus_plan.py --check      # are the committed page and sketches what the record gives?
    options: --record <campus.json>   --out <folder>

docs/UI2_DESIGN.md 5.2, 4.8, 5.9. Everything here is drawn FROM
tools/bgs/campus.json, so the prose and the sketch can never disagree with
the record.

  tools/bgs/CAMPUS2.md          the record as a page: what every key means, the
                                chosen pictures, the ground plan, the paths,
                                what is seen from each yard, the windows, what
                                waits for a batch, the pin targets.
  tools/bgs/campus_plan.png     the ground plan, labelled; fixed facts solid,
                                proposals dashed. FOR REVIEWERS. It is never put
                                to the owner for approval: there is no drawing
                                to approve (the owner's ruling, O20).
  tools/bgs/campus_plan_<area>.png    the same, cut to one area, twice the size.
  tools/bgs/campus_plan_ref.png, campus_plan_ref_<area>.png
                                colour blocks, no words: the layout reference
                                handed to the editor with the map prompts
                                (5.9). --ref refuses until every building of
                                the record is fixed: the maps are made last.

--pins: each area's pins are the ground plan's points stretched onto the area
picture's pin frame, so west stays left and north stays higher; it checks
them with check_campus's own rule before printing. They are targets for the
map prompts, never kept by hand; the final points are measured on each chosen
map and written to game/layout/area_<key>.json.

The drawing needs Pillow: started with plain python3 it starts itself again
through tools/py_art.sh, and where ComfyUI's Python is absent that prints one
line and stops (--md and --pins never need it).
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_campus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGS = os.path.join(ROOT, "tools", "bgs")
PIN_INNER = (400, 300, 1500, 860)       # inside the map's pin frame (200, 200, 1700, 940)
PIN_BOX = (250, 110)                    # two pins closer than this in both directions would overlap


# ---- the pin targets -----------------------------------------------------------------------------------------
def pin_targets(record, area):
    """{place: (x, y)} on the area's picture, from the ground plan."""
    rec = check_campus.Rec(record)
    keys = [k for k, p in rec.places.items() if p["area"] == area and not p.get("pinless")]
    pts = dict((k, rec.at(k)) for k in keys)
    xs, ys = [p[0] for p in pts.values()], [p[1] for p in pts.values()]
    x0, y0, x1, y1 = PIN_INNER

    def stretch(v, lo, hi, a, b):
        return (a + b) / 2.0 if hi - lo < 1 else a + (v - lo) * (b - a) / float(hi - lo)

    out = dict((k, [stretch(p[0], min(xs), max(xs), x0, x1), stretch(p[1], min(ys), max(ys), y0, y1)])
               for k, p in pts.items())
    # two pins must not sit on top of each other: the lower of an overlapping pair moves down
    for _ in range(20):
        moved = False
        order = sorted(out, key=lambda k: (out[k][1], out[k][0]))
        for i, a in enumerate(order):
            for b in order[i + 1:]:
                if abs(out[a][0] - out[b][0]) < PIN_BOX[0] and abs(out[a][1] - out[b][1]) < PIN_BOX[1]:
                    out[b][1] = out[a][1] + PIN_BOX[1]
                    moved = True
        if not moved:
            break
    return dict((k, (int(round(v[0])), int(round(min(v[1], 940))))) for k, v in out.items())


def pins_report(record):
    rec = check_campus.Rec(record)
    lines, bad = [], 0
    for area, a in record["areas"].items():
        pins = pin_targets(record, area)
        out = check_campus.Out()
        check_campus.check_pins(rec, "the %s map" % check_campus.map_name(a), pins, out, True, a.get("batch", "?"), a["stem"])
        bad += out.count("FAIL") + out.count("REPORT")
        lines.append("%s (%d): %s" % (a["name"], len(pins), ", ".join(
            "%s (%d, %d)" % (k, pins[k][0], pins[k][1]) for k in sorted(pins, key=lambda k: (pins[k][1], pins[k][0])))))
        for level in ("FAIL", "REPORT"):
            lines += ["   %s %s" % (level, t) for t in out.texts(level)]
    return lines, bad


# ---- the page ------------------------------------------------------------------------------------------------
def by_words(rec, row):
    if not rec.is_fixed(row):
        return "proposed"
    by = row.get("by", {})
    return "**fixed** by `%s` (revision %s)" % (by.get("picture"), by.get("rev"))


def markdown(record):
    rec = check_campus.Rec(record)
    r = record
    L = []
    add = L.append
    add("# The campus record")
    add("")
    add("**Written by `tools/campus_plan.py` from `tools/bgs/campus.json`. Do not edit this page: change the "
        "record and run the tool again.** It replaces `CAMPUS.md` for the second UI overhaul "
        "(`docs/UI2_DESIGN.md` 5.2).")
    add("")
    add("There is no drawing of the campus to approve. The campus is kept one place a different way: every "
        "picture the owner chooses **fixes** facts, and every later picture is composed from words and the chosen "
        "pictures of its neighbours and must agree with the facts so far. The maps are made last, round the "
        "finished places.")
    add("")
    add("- A **fixed** row is a fact a chosen picture shows. It names that picture and its revision, and it "
        "changes only when the owner chooses that picture again.")
    add("- A **proposed** row is the plan's words for something not painted yet. It goes into prompts, and it is "
        "rewritten without ceremony when a chosen picture says otherwise.")
    add("- A **waived** row names a fixed fact, the chosen picture that stands against it and the date the owner "
        "accepted that. Only `tools/install_redo.py --waive` writes one.")
    add("")
    add("`tools/check_campus.py` checks all of it; `tools/campus_plan.png` is the same ground plan as a sketch "
        "(for reviewers, never for approval).")
    add("")
    nf, np_ = len(r["fixed"]), len(r["proposed"])
    add("Today: **%d fixed rows, %d proposed, %d waived.**" % (nf, np_, len(r.get("waived", []))))
    add("")
    add("## The pictures the owner has chosen")
    add("")
    add("| picture | place | revision | kind | chosen | the render |")
    add("|---|---|---|---|---|---|")
    for stem, p in r["pictures"].items():
        add("| `%s` | %s | %s | %s | %s | `%s` |" % (stem, rec.name(p["place"]), p.get("rev"), p.get("kind"),
                                                 p.get("chosen", ""), p.get("render", "")))
    add("")
    add("## The ground plan")
    add("")
    add("Top-down on a %d x %d sheet, north and uphill at the top. Rows marked \u2020 are fixed. A building's look "
        "line is the same in every picture that shows it; its court side goes only into prompts whose camera sees "
        "that side." % tuple(r["sheet"]))
    add("")
    add("| building or ground | what a prompt calls it | holds | at (x, y) | its look | court side (seen from) |")
    add("|---|---|---|---|---|---|")
    for b in rec.rows("building"):
        cs = "%s (%s)" % (b["court_side"], ", ".join("`%s`" % s for s in b.get("court_seen_from", []))) \
            if b.get("court_side") else ""
        add("| %s%s | %s | %s | (%d, %d)%s | %s | %s |" % (
            "\u2020 " if rec.is_fixed(b) else "", b["name"], b["as"],
            ", ".join("`%s`" % h for h in b.get("holds", [])) or "a landmark, not a place",
            b["at"][0], b["at"][1], ", " + b["shape"] if b.get("shape") else "", b["look"], cs))
    notes = [b for b in rec.rows("building") if b.get("note")]
    if notes:
        add("")
        for b in notes:
            add("- **%s:** %s" % (b["name"], b["note"]))
    add("")
    add("No prompt names the series or a character, so in a prompt a building is called what the second column "
        "says, never by a person's name.")
    add("")
    add("## Paths")
    add("")
    for row in rec.rows("path"):
        add("- %s to %s: %s (%s)" % (rec.name(row["a"]), rec.name(row["b"]), row["words"], by_words(rec, row)))
    add("")
    add("## What I see from each place, and what each exit sits on")
    add("")
    for place in sorted(set(row["place"] for row in rec.rows("exit") + rec.rows("seen")),
                        key=lambda k: list(rec.places).index(k)):
        p = rec.places[place]
        cam = "I stand at (%d, %d), facing %s." % (p["camera"][0], p["camera"][1], p["facing"]) if p.get("camera") \
            else "The camera stands in the room%s." % (", facing %s" % p["facing"] if p.get("facing") else "")
        add("### %s" % p["name"])
        add("")
        add("%s The place itself is %s%s." % (cam, by_words(rec, p),
                                             "; at least %d of its exits must stay clear of a four-person row"
                                             % p["clear"] if p.get("clear") else ""))
        add("")
        add("| where | what | leads to | |")
        add("|---|---|---|---|")
        rows = sorted(check_campus.view_rows(rec, place),
                      key=lambda row: (check_campus.SIDES.index(row["side"]), row.get("order") or 0,
                                       row.get("half") or ""))
        for row in rows:
            where = row["side"] + (" " + row["half"] if row.get("half") else "")
            what = (rec.buildings[row["thing"]]["name"] + ": " if row.get("thing") else "") + row["words"]
            add("| %s | %s | %s | %s |" % (where, what, rec.name(row["to"]) if row["kind"] == "exit" else "",
                                           by_words(rec, row)))
        add("")
    add("**Behind the camera means the bottom of the picture.** A place the camera has its back to has its exit "
        "in the bottom band (y %d or lower down)." % rec.rules.get("bottom_band", 900))
    add("")
    add("## What the windows show")
    add("")
    add("A line names a neighbour only once that neighbour's picture is chosen; until then the prompt leaves the "
        "line out.")
    add("")
    add("| room | wall | faces | the wall is | the line a prompt carries | waits for | the line is |")
    add("|---|---|---|---|---|---|---|")
    walls = dict(((w["room"], w["wall"]), w) for w in rec.rows("window"))
    for ln in rec.rows("line"):
        w = walls[(ln["room"], ln["wall"])]
        add("| %s | %s | %s | %s | %s | %s | %s |" % (
            rec.name(ln["room"]), ln["wall"], w.get("faces") or "", by_words(rec, w), ln["shows"],
            ", ".join(rec.name(n) for n in ln.get("needs", []) if rec.chosen(n) is None), by_words(rec, ln)))
    add("")
    add("The Principal's office, the storehouse and the sauna have no windows. The Rooftop's far view is redone "
        "in place and stays a loose cluster of roofs.")
    add("")
    add("## The rooms already chosen, as their pictures show them")
    add("")
    for row in rec.rows("interior"):
        add("- **%s** (%s): %s." % (rec.name(row["room"]), by_words(rec, row), row["words"]))
    add("")
    add("## What waits for a batch")
    add("")
    add("`tools/check_campus.py` lists these, with every side and pin of today's pictures that disagrees with "
        "the record, as \"waits for batch N\". They are not failures while the picture is at revision 1.")
    add("")
    for w in r.get("waits", []):
        add("- batch %s, `%s`: %s." % (w["batch"], w["picture"], w["what"]))
    add("")
    add("## Waived")
    add("")
    if r.get("waived"):
        for w in r["waived"]:
            add("- `%s`, against `%s` (revision %s), accepted %s: %s" % (w["fact"], w["picture"], w.get("rev"),
                                                                     w["date"], w.get("words", "")))
    else:
        add("Nothing. (A waiver is the last rung of the ladder in 5.2: the owner is shown the contradiction in "
            "plain words and accepts it.)")
    add("")
    add("## The order of making")
    add("")
    add("A place is not made before the chosen picture of each place in its `after` (K8).")
    add("")
    add("| place | picture | how | batch | made after | chosen |")
    add("|---|---|---|---|---|---|")
    for key, p in rec.places.items():
        add("| %s | `%s.png` | %s | %s | %s | %s |" % (
            p["name"], p["stem"], {"composed": "composed again", "inplace": "redone in place"}[p["how"]],
            p["batch"], ", ".join(rec.name(a) for a in p.get("after", [])) or "\u2013",
            "yes" if rec.chosen(key) else ""))
    add("")
    add("## The pin targets for the maps")
    add("")
    add("What the area-map prompts will ask for (`tools/campus_plan.py --pins`): the ground plan stretched onto "
        "each area picture's pin frame. The final points are measured on each chosen map.")
    add("")
    lines, _ = pins_report(record)
    for line in lines:
        add("- " + line)
    add("")
    add("## The shape of `campus.json`")
    add("")
    add("| key | what it holds |")
    add("|---|---|")
    for key, what in SHAPE:
        add("| %s | %s |" % (key, what))
    add("")
    return "\n".join(L)


SHAPE = [
    ("`format`", "`1`"),
    ("`sheet`", "the ground plan's size, `[1920, 1080]`; north is up"),
    ("`rules`", "`thirds` (the two x where the screen's thirds meet), `bottom_band` (an exit behind the camera "
                "has y at or below this), `apart` (px on a picture inside which two exits or pins are not "
                "ordered), `plan_apart` (the same on the ground plan), and the four angles that say what "
                "\"left\", \"ahead\", \"right\" and \"behind\" mean from a camera"),
    ("`areas`", "`{area key: {name, hub, stem, batch}}`: the six area maps"),
    ("`campus_map`", "`{stem, batch, mountain_only_north}`"),
    ("`pictures`", "`{picture stem: {place, rev, kind, batch, chosen, render, source, source_2k}}`: the "
                   "pictures the owner has chosen. `source` is where the chosen file is kept until it is "
                   "installed in the game. The installer adds a row with each picture"),
    ("`fixed`, `proposed`", "lists of rows; every row has a unique `id` and a `kind`. A fixed row also has "
                            "`by: {picture, rev}`. A proposal that a chosen picture fixes moves, with its id, "
                            "from one list to the other"),
    ("row `building`", "`key`, `name`, `as` (what a prompt calls it; never a person's name), `holds` (place "
                       "keys), `at` `[x, y]`, `shape`, `ground` (true for a yard or open ground), `look`, and "
                       "apart from it `court_side` with `court_seen_from` (the places whose camera sees that "
                       "side), `note`"),
    ("row `place`", "`key`, `name`, `stem` (its picture's file name), `area`, `indoor`, `building`, `how` "
                    "(`composed` or `inplace`), `batch`, `after` (the places whose chosen pictures it waits for, "
                    "K8), `refs_also` (more reference pictures, used once chosen), `words` (what a new "
                    "composition is built from), `camera` `[x, y]` and `facing`, `camera_in` (`doorway`) with "
                    "`entered_from`, `old_picture` (`camera`: keep its camera and sides; `school`: only to know "
                    "the school and the camera height), `clear` (4.6), `at` (its own point, where the building's "
                    "will not do), `pinless`, `spare_doors`, `facts` (sentences a fixed fact adds to its prompt), `check` (extra yes/no lines), `note`"),
    ("row `path`", "`a`, `b`, `words`: the game's `PATH_LINKS`"),
    ("row `exit`", "`place`, `to`, `side` (`left`, `ahead`, `right`, `bottom`), `order` (from left to right; "
                   "equal numbers are not ordered), `half` (`left` or `right`, for a bottom exit), `on` "
                   "(`building` or `path`), `thing` (the building it sits on), `words`, `alias` (an older key "
                   "for the same exit), `against` (what the owner is told when a version contradicts it)"),
    ("row `seen`", "a building seen from a place that no exit sits on: `place`, `thing`, `side`, `order`, "
                   "`words`"),
    ("row `window`", "`room`, `wall`, `faces` (`north`, `east`, `south`, `west`, or null where it does not "
                     "matter)"),
    ("row `line`", "`room`, `wall`, `shows` (the words after \"Through the windows:\"), `names` (the buildings "
                   "it names, each of which must lie on the side the wall faces), `needs` (places whose pictures "
                   "must be chosen before the line is used)"),
    ("row `interior`", "`room`, `words`: a chosen room's layout, read off its picture (not used in prompts)"),
    ("`waived`", "`{fact, picture, rev, date, words}`"),
    ("`waits`", "`{id, picture, batch, until_rev, what}`: something a new picture must put right that no tool "
                "can see"),
]


# ---- the sketch ------------------------------------------------------------------------------------------------
def need_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
    except ImportError:
        runner = os.path.join(ROOT, "tools", "py_art.sh")
        if not os.environ.get("JJK_PY_ART") and os.path.exists(runner):
            os.execv("/bin/bash", ["/bin/bash", runner, os.path.abspath(__file__)] + sys.argv[1:])
        raise SystemExit("campus_plan.py: Pillow is needed to draw: run it through tools/py_art.sh")


INK, PAPER, FIXED, LOOSE = (40, 44, 52), (246, 243, 236), (58, 92, 140), (150, 120, 70)
AREA_TINT = {"heart": (232, 224, 204), "school": (214, 226, 236), "dorms": (220, 234, 214),
             "staff": (236, 222, 226), "grounds": (236, 228, 208), "mountain": (214, 230, 222)}
AREA_BLOCK = {"heart": (196, 170, 120), "school": (110, 150, 196), "dorms": (120, 176, 120),
              "staff": (190, 120, 140), "grounds": (200, 150, 90), "mountain": (90, 150, 130)}


def box_of(b):
    x, y = b["at"]
    if b.get("ground"):
        w, h = 210, 120
    elif "north to south" in (b.get("shape") or ""):
        w, h = 64, 150
    elif not b.get("holds"):
        w, h = 44, 44
    else:
        w, h = 104, 60
    return [x - w // 2, y - h // 2, x + w // 2, y + h // 2]


def area_of_building(rec, b):
    for p in b.get("holds", []):
        if p in rec.places:
            return rec.places[p]["area"]
    near = min(rec.places.values(), key=lambda p: (rec.at(p["key"])[0] - b["at"][0]) ** 2
               + (rec.at(p["key"])[1] - b["at"][1]) ** 2)
    return near["area"]


def dashed(draw, pts, fill, width=2, dash=10):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / dash))
        for i in range(0, n, 2):
            a, b = i / float(n), min(1.0, (i + 1) / float(n))
            draw.line([x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b],
                      fill=fill, width=width)


def draw_plan(record, words=True, scale=1):
    Image, ImageDraw, ImageFont = need_pillow()
    rec = check_campus.Rec(record)
    W, H = record["sheet"]
    im = Image.new("RGB", (W * scale, H * scale), PAPER if words else (238, 238, 232))
    d = ImageDraw.Draw(im)

    def font(size):
        for path in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size * scale)
                except Exception:
                    pass
        return ImageFont.load_default()

    def sc(v):
        return [c * scale for c in v]

    small, mid, big = font(15), font(19), font(30)
    buildings = rec.rows("building")
    # grounds first, then paths, then buildings
    for b in buildings:
        if b.get("ground"):
            area = area_of_building(rec, b)
            box = sc(box_of(b))
            if words:
                d.rounded_rectangle(box, radius=26 * scale, fill=AREA_TINT[area])
                if rec.is_fixed(b):
                    d.rounded_rectangle(box, radius=26 * scale, outline=FIXED, width=3 * scale)
                else:
                    x0, y0, x1, y1 = box
                    dashed(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], LOOSE, 2 * scale, 12 * scale)
            else:
                d.rounded_rectangle(box, radius=26 * scale, fill=tuple(min(255, c + 40) for c in AREA_BLOCK[area]))
    for row in rec.rows("path"):
        a, b = sc(rec.at(row["a"])), sc(rec.at(row["b"]))
        if not words:
            d.line(a + b, fill=(150, 150, 150), width=8 * scale)
        elif rec.is_fixed(row):
            d.line(a + b, fill=FIXED, width=4 * scale)
        else:
            dashed(d, [tuple(a), tuple(b)], LOOSE, 3 * scale, 14 * scale)
    for b in buildings:
        if b.get("ground"):
            continue
        area = area_of_building(rec, b)
        box = sc(box_of(b))
        if not words:
            d.rectangle(box, fill=AREA_BLOCK[area])
            continue
        if rec.is_fixed(b):
            d.rectangle(box, fill=(196, 208, 226), outline=FIXED, width=3 * scale)
        else:
            d.rectangle(box, fill=(250, 248, 242))
            x0, y0, x1, y1 = box
            dashed(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], LOOSE, 2 * scale, 8 * scale)
    if not words:
        return im
    # cameras: where I stand in each yard, and which way I look
    for p in rec.places.values():
        if p.get("camera"):
            x, y = sc(p["camera"])
            fx, fy = check_campus.FACING[p["facing"]]
            r = 9 * scale
            d.polygon([(x + fx * r * 2, y + fy * r * 2), (x - fy * r - fx * r, y + fx * r - fy * r),
                       (x + fy * r - fx * r, y - fx * r - fy * r)], fill=(200, 60, 50))
    def label(text, cx, top, fill):
        tw = d.textlength(text, font=small)
        d.rectangle([cx - tw / 2 - 3 * scale, top - 1 * scale, cx + tw / 2 + 3 * scale, top + 18 * scale], fill=PAPER)
        d.text((cx - tw / 2, top), text, fill=fill, font=small)

    for b in buildings:
        x0, y0, x1, y1 = sc(box_of(b))
        name = b["name"].replace(" (shown as Onsen)", "").replace("Gate Lodge (west)", "Lodge").replace(
            "Gate Lodge (east)", "Lodge")
        if b.get("ground"):
            label(name, (x0 + x1) / 2, y0 + 6 * scale, INK)
        elif name == "Lodge":
            label(name, (x0 + x1) / 2, y1 + 3 * scale, FIXED if rec.is_fixed(b) else INK)
        else:
            label(name, (x0 + x1) / 2, y0 - 21 * scale, FIXED if rec.is_fixed(b) else INK)
    d.text((24 * scale, 20 * scale), "The campus record: a working sketch", fill=INK, font=big)
    d.text((24 * scale, 58 * scale), "For reviewers. Never for approval: there is no drawing to approve, the map "
           "is made last (O20).", fill=INK, font=mid)
    d.text((24 * scale, 84 * scale), "North and uphill at the top. Written from tools/bgs/campus.json by "
           "tools/campus_plan.py.", fill=INK, font=mid)
    lx, ly = 24 * scale, (H - 150) * scale
    d.rectangle([lx, ly, lx + 46 * scale, ly + 26 * scale], fill=(196, 208, 226), outline=FIXED, width=3 * scale)
    d.text((lx + 58 * scale, ly + 2 * scale), "fixed by a picture the owner chose", fill=INK, font=mid)
    ly += 38 * scale
    d.rectangle([lx, ly, lx + 46 * scale, ly + 26 * scale], fill=(250, 248, 242))
    dashed(d, [(lx, ly), (lx + 46 * scale, ly), (lx + 46 * scale, ly + 26 * scale), (lx, ly + 26 * scale), (lx, ly)],
           LOOSE, 2 * scale, 8 * scale)
    d.text((lx + 58 * scale, ly + 2 * scale), "proposed: the plan's words, until a chosen picture says otherwise",
           fill=INK, font=mid)
    ly += 38 * scale
    d.polygon([(lx + 23 * scale, ly), (lx + 10 * scale, ly + 24 * scale), (lx + 36 * scale, ly + 24 * scale)],
              fill=(200, 60, 50))
    d.text((lx + 58 * scale, ly + 2 * scale), "where I stand in a yard, and which way I look", fill=INK, font=mid)
    return im


def area_box(record, area, margin=130):
    rec = check_campus.Rec(record)
    pts = []
    for b in rec.rows("building"):
        if area_of_building(rec, b) == area:
            pts.append(box_of(b))
    x0, y0 = min(p[0] for p in pts) - margin, min(p[1] for p in pts) - margin
    x1, y1 = max(p[2] for p in pts) + margin, max(p[3] for p in pts) + margin
    W, H = record["sheet"]
    return [max(0, x0), max(0, y0), min(W, x1), min(H, y1)]


def write_sketches(record, out_dir, ref=False):
    rec = check_campus.Rec(record)
    made = []
    if ref:
        loose = [b["name"] for b in rec.rows("building") if not rec.is_fixed(b)]
        if loose:
            raise SystemExit("campus_plan_ref.png is drawn at the end, when every place is fixed: %d building%s "
                             "of the record %s still a proposal (%s%s)"
                             % (len(loose), "" if len(loose) == 1 else "s", "is" if len(loose) == 1 else "are",
                                ", ".join(loose[:4]), ", ..." if len(loose) > 4 else ""))
        big = draw_plan(record, words=False, scale=2)
        full = big.resize(tuple(record["sheet"]))
        full.save(os.path.join(out_dir, "campus_plan_ref.png"), optimize=True); made.append("campus_plan_ref.png")
        for area in record["areas"]:
            name = "campus_plan_ref_%s.png" % area
            big.crop([c * 2 for c in area_box(record, area)]).save(os.path.join(out_dir, name), optimize=True)
            made.append(name)
        return made
    full = draw_plan(record)
    full.save(os.path.join(out_dir, "campus_plan.png"), optimize=True); made.append("campus_plan.png")
    big = draw_plan(record, scale=2)
    for area in record["areas"]:
        name = "campus_plan_%s.png" % area
        big.crop([c * 2 for c in area_box(record, area)]).save(os.path.join(out_dir, name), optimize=True)
        made.append(name)
    return made


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

    record = check_campus.load_record(opt("--record"))
    out_dir = opt("--out") or BGS
    known = ("--md", "--pins", "--ref", "--check")
    if [a for a in argv if a not in known]:
        print(__doc__); raise SystemExit(1)
    if "--pins" in argv:
        lines, bad = pins_report(record)
        print("\n".join(lines))
        print("campus_plan --pins: %s" % ("every target keeps the ground plan's relations" if not bad
                                          else "%d of them break the ground plan's relations" % bad))
        raise SystemExit(1 if bad else 0)
    if "--check" in argv:
        page = os.path.join(BGS, "CAMPUS2.md")
        same = os.path.exists(page) and open(page, encoding="utf-8").read() == markdown(record)
        print("CAMPUS2.md %s" % ("is what the record gives" if same else
                                 "is NOT what the record gives: run tools/campus_plan.py"))
        missing = [n for n in ["campus_plan.png"] + ["campus_plan_%s.png" % a for a in record["areas"]]
                   if not os.path.exists(os.path.join(BGS, n))]
        if missing:
            print("missing: %s" % ", ".join(missing))
        raise SystemExit(0 if same and not missing else 1)
    if "--ref" in argv:
        os.makedirs(out_dir, exist_ok=True)
        for name in write_sketches(record, out_dir, ref=True):
            print("   wrote %s" % os.path.join(out_dir, name))
        return
    os.makedirs(out_dir, exist_ok=True)
    if "--md" not in argv:
        need_pillow()
    path = os.path.join(out_dir, "CAMPUS2.md")
    open(path, "w", encoding="utf-8").write(markdown(record))
    print("   wrote %s" % path)
    if "--md" in argv:
        return
    for name in write_sketches(record, out_dir):
        print("   wrote %s" % os.path.join(out_dir, name))


if __name__ == "__main__":
    main(sys.argv[1:])
