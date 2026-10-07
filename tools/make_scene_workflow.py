"""
Build the ComfyUI workflow for a picture that is COMPOSED AGAIN: a yard, the
gate, a new place, an area map or the campus map. Every word of its prompt
comes from the campus record.

    python3 tools/make_scene_workflow.py training_yard            # a yard, a new place, the gate
    python3 tools/make_scene_workflow.py area_heart               # an area map; map_campus is the campus map
    python3 tools/make_scene_workflow.py school_yard --print      # the prompt and its pictures; writes nothing
    python3 tools/make_scene_workflow.py dorm_yard --again 1      # one more pair, from two other seeds
    python3 tools/make_scene_workflow.py --list                   # every picture it can make, and what each waits for
    options: --out <folder>   --manifest <pictures.json>   --record <campus.json>   --layout-dump <file>

docs/UI2_DESIGN.md 5.2, 5.6, K4, K8. No outdoor prompt is written by hand.
The prompt is, in this order:

  1. one opening sentence, and one sentence for each reference picture;
  2. the place's own words from the record (tools/bgs/campus.json), then what
     stands on the left, ahead, on the right and at the bottom of the frame:
     each building by the look line it has in EVERY picture that shows it,
     and each exit by the thing it sits on. A fact a chosen picture has fixed
     is said in words ("the same building that stands on the right of
     picture 1");
  3. tools/bgs/stage.txt for a place people stand in (what the screen needs
     of the picture), or tools/bgs/map.txt for a map; never both;
  4. tools/bgs/look.txt.

The reference pictures (the editor takes up to fourteen): the chosen picture
of each neighbour; the crop of each building the two share, when the
installer has cut one to tools/bgs/refs/<building>.png; and, for a yard that
is laid out again, the picture it replaces, either to keep its camera or only
"to know the school and the camera height". There is no plan drawing among
them, except for a map (its piece of campus_plan_ref.png, when that exists).

THE ORDER IS ENFORCED (K8): a place is not made before the chosen picture of
the yard it stands off (the record's `after`), working outwards from the
Courtyard, and a map not before every place on it has its picture. A room
inside a house waits for the yard its house stands on, not for its corridor.
"Chosen" is the record's `pictures`: the installer writes a row there with
the picture. Refusals are one plain line saying what is missing.

Two versions of every picture, from two fixed seeds, saved as
`ui2_<stem>_a_0000N_.png` and `ui2_<stem>_b_...`: pressing Run again after an
error pays only for the boxes that did not finish. It writes the workflow
(`scene_<stem>.json`) into ~/Desktop/JJK Game images/ui2/ and copies the
reference pictures beside it and into ComfyUI's input folder. It queues
nothing: the owner presses Run (K14). Nano Banana Pro at 2K, 2752x1536,
about $0.16 a render.

tools/art_batch.py <n> calls this for a whole sitting and writes the page of
numbered steps; run this by hand only for one picture.

Plain Python.
"""
import sys, os, json, copy, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_prompts
import check_campus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.expanduser("~/Desktop/JJK Game images")
OUT = os.path.join(IMAGES, "ui2")
COMFY_INPUT = os.path.expanduser("~/ComfyUI-Shared/input")
REFS = os.path.join(ROOT, "tools", "bgs", "refs")
PLAN_REF = os.path.join(ROOT, "tools", "bgs", "campus_plan_ref_%s.png")
COST = 0.16
RESOLUTION = "2K"
VERSIONS = "ab"
MAX_REFS = 14
S = check_prompts.sentence


class Refused(Exception):
    """Why a picture cannot be made yet, in one plain line."""


# ---- which pictures exist ---------------------------------------------------------------------------------
def chosen_file(rec, manifest, place, root=None):
    """The chosen picture of a place: the game's file once it is installed in
    the new look, before that the file the record's row names."""
    p = rec.places[place]
    pic = rec.chosen(place)
    if pic is None:
        return None
    game = os.path.join(root or ROOT, "game", "images", "bg", p["stem"] + ".png")
    if check_campus.rev_of(manifest, p["stem"]) >= 2 and os.path.exists(game):
        return game
    src = os.path.expanduser(pic.get("source") or "")
    return src if src and os.path.exists(src) else None


def need_chosen(rec, manifest, place, why, root=None):
    """The file of a chosen neighbour, or a refusal that says what is missing."""
    p = rec.places[place]
    if rec.chosen(place) is None:
        raise Refused("%s has no chosen picture yet (batch %s). %s" % (p["name"], p.get("batch", "?"), why))
    path = chosen_file(rec, manifest, place, root)
    if path is None:
        raise Refused("the chosen picture of %s is not on this machine (it is not installed in the game, and %s "
                      "is absent)" % (p["name"], rec.chosen(place).get("source") or "the record names no file"))
    return path


def k8_place(rec, place):
    """K8 for a place: every yard it stands off is chosen."""
    p = rec.places[place]
    for a in p.get("after", []):
        if rec.chosen(a) is None:
            raise Refused("%s cannot be made yet: %s has no chosen picture (batch %s). A place is made after the "
                          "yard it stands off, working outwards from the Courtyard."
                          % (p["name"], rec.places[a]["name"], rec.places[a].get("batch", "?")))


def k8_map(rec, stem):
    """K4: a map waits for every place on it."""
    r = rec.r
    if stem == r.get("campus_map", {}).get("stem", "map_campus"):
        missing = [a["name"] for a in r["areas"].values() if a["stem"] not in r.get("pictures", {})]
        if missing:
            raise Refused("the campus map cannot be made yet: it is composed from the six area maps, and %s %s no "
                          "chosen picture" % (_and(missing), "has" if len(missing) == 1 else "have"))
        return None
    for key, a in r["areas"].items():
        if a["stem"] == stem:
            missing = [p["name"] for p in rec.places.values()
                       if p["area"] == key and not p.get("pinless") and rec.chosen(p["key"]) is None]
            if missing:
                raise Refused("the %s map cannot be made yet: a map is made last, from finished places, and %s %s "
                              "no chosen picture" % (check_campus.map_name(a), _and(sorted(missing)),
                                                     "has" if len(missing) == 1 else "have"))
            return key
    raise Refused("%s is not a map of the record" % stem)


def _and(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


# ---- the references ---------------------------------------------------------------------------------------
def shared_buildings(rec, place):
    """Buildings this place's picture shows that a chosen picture has already fixed."""
    out = []
    for row in check_campus.view_rows(rec, place):
        b = rec.buildings.get(row.get("thing"))
        if b is not None and rec.is_fixed(b) and b["key"] not in out and not b.get("ground"):
            out.append(b["key"])
    return out


def refs_for(rec, manifest, place, root=None):
    """[(kind, key, file)] in picture order: neighbours, shared buildings' crops, the old picture."""
    p = rec.places[place]
    refs = []
    for a in p.get("after", []):
        refs.append(("neighbour", a, need_chosen(rec, manifest, a, "It is a reference for %s." % p["name"], root)))
    for a in p.get("refs_also", []):
        if a not in p.get("after", []) and rec.chosen(a) is not None and chosen_file(rec, manifest, a, root):
            refs.append(("neighbour", a, chosen_file(rec, manifest, a, root)))
    for b in shared_buildings(rec, place):
        crop = os.path.join(REFS, b + ".png")
        if os.path.exists(crop):
            refs.append(("building", b, crop))
    if p.get("old_picture"):
        old = os.path.join(root or ROOT, "game", "images", "bg", p["stem"] + ".png")
        if os.path.exists(old):
            refs.append(("old_" + p["old_picture"], place, old))
    if len(refs) > MAX_REFS:
        raise Refused("%s would be given %d reference pictures; the editor takes %d" % (p["name"], len(refs), MAX_REFS))
    return refs


# ---- the prompt ---------------------------------------------------------------------------------------------
def _where_in(rec, building, ref_places):
    """("on the right", n) when a reference picture shows this building on a known side."""
    for n, place in ref_places:
        for row in check_campus.view_rows(rec, place):
            if row.get("thing") == building and rec.is_fixed(row) and row.get("side") in ("left", "ahead", "right"):
                return {"left": "on the left", "ahead": "in the middle", "right": "on the right"}[row["side"]], n
    return None


def _thing_words(rec, place, row, ref_places):
    """One row of a view as a painter's words: the building by its look line, then what the exit sits on."""
    b = rec.buildings.get(row.get("thing"))
    if b is None:
        return row["words"]
    parts = [b["as"], b["look"]]
    if b.get("court_side") and place in b.get("court_seen_from", []):
        parts.append("on this side " + b["court_side"])
    if rec.is_fixed(b):
        where = _where_in(rec, b["key"], [(n, pl) for n, pl in ref_places if pl != place])
        if where:
            parts.append(S("same_as", where=where[0], n=where[1]))
    return ", ".join(parts) + "; " + row["words"]


def prompt_for(record, place, refs=(), window=True):
    """The prompt for a composed place. refs: [(kind, key)] or [(kind, key, file)], in picture order."""
    rec = check_campus.Rec(record)
    p = rec.places[place]
    if not (p.get("words") or "").strip():
        raise Refused("%s has no words in the record to compose it from" % p["name"])
    rows = check_campus.view_rows(rec, place)
    if not p["indoor"] and p.get("camera") and not rec.rows("exit", place=place):
        raise Refused("%s has no view in the record: no row says which building, door or path is on which side of "
                      "it (tools/bgs/campus.json)" % p["name"])
    out = [S("open_room" if p["indoor"] else "open_yard")]
    ref_places = []
    for n, ref in enumerate(refs, 1):
        kind, key = ref[0], ref[1]
        if kind == "neighbour":
            b = rec.building_of(key)
            out.append(S("ref_neighbour", n=n, thing=b["as"] if b.get("ground") or len(b.get("holds", [])) == 1
                         else "a room of " + b["as"]))
            ref_places.append((n, key))
        elif kind == "building":
            out.append(S("ref_building", n=n, thing=rec.buildings[key]["as"]))
        elif kind == "old_camera":
            out.append(S("ref_old_camera", n=n))
        elif kind == "old_school":
            out.append(S("ref_old_school", n=n))
        elif kind == "plan":
            out.append(S("ref_plan", n=n))
    out.append(S("the_place", thing=p["words"]))
    ground = rec.building_of(place)
    if ground is not None and ground.get("ground"):
        out.append(S("the_ground", thing=ground["look"]))
    out += list(p.get("facts", []))
    for side in ("left", "ahead", "right"):
        here = sorted((r for r in rows if r["side"] == side), key=lambda r: (r.get("order") or 0))
        if here:
            out.append(S(side, thing="; ".join(_thing_words(rec, place, r, ref_places) for r in here)))
    for half, key in (("left", "bottom_left"), ("right", "bottom_right"), (None, "bottom")):
        here = [r for r in rows if r["side"] == "bottom" and r.get("half") == half]
        if here:
            out.append(S(key, thing="; ".join(r["words"] for r in here)))
    if p.get("clear"):
        out.append(S("clear", count={1: "one", 2: "two"}.get(p["clear"], str(p["clear"]))))
    if p["indoor"] and window:
        line = window_line(rec, place)
        if line:
            out.append(line)
    out.append(check_prompts.text_of("stage.txt"))
    out.append(check_prompts.text_of("look.txt"))
    return " ".join(out)


def window_line(rec, room, ignore_needs=False):
    """"Through the windows: ..." from the record, or None. A line that names a
    neighbour is left out until that neighbour's picture is chosen."""
    shows = []
    for ln in rec.rows("line", room=room):
        if ignore_needs or all(rec.chosen(n) is not None for n in ln.get("needs", [])):
            shows.append(ln["shows"])
    return S("windows", thing="; ".join(shows)) if shows else None


def pin_words(pt, frame=(200, 200, 1700, 940)):
    """Where on a map a point is, in a painter's words."""
    x0, y0, x1, y1 = frame
    col = min(2, max(0, int(3 * (pt[0] - x0) / float(x1 - x0))))
    row = min(2, max(0, int(3 * (pt[1] - y0) / float(y1 - y0))))
    return [["in the upper left", "at the top, in the middle", "in the upper right"],
            ["on the left, half way up", "in the middle", "on the right, half way up"],
            ["in the lower left", "at the bottom, in the middle", "in the lower right"]][row][col]


def map_prompt_for(record, stem, refs=(), anchors=None):
    """The prompt for an area map, or for the campus map (stem map_campus)."""
    import campus_plan
    rec = check_campus.Rec(record)
    r = rec.r
    out = [S("open_map")]
    for n, ref in enumerate(refs, 1):
        kind, key = ref[0], ref[1]
        if kind == "neighbour":
            if key in rec.places:
                out.append(S("ref_neighbour", n=n, thing=rec.building_of(key)["as"]))
            else:
                out.append(S("ref_neighbour", n=n, thing="the map of one part of the school"))
        elif kind == "building":
            out.append(S("ref_building", n=n, thing=rec.buildings[key]["as"]))
        elif kind == "plan":
            out.append(S("ref_plan", n=n))
    if stem == r.get("campus_map", {}).get("stem", "map_campus"):
        out.append(S("the_place", thing="the whole school on its mountainside: high ground and mountains across "
                     "the whole top of the picture, their main mass in the upper right, and the main gate at the "
                     "bottom"))
        for key, a in r["areas"].items():
            hub = rec.building_of(a["hub"])
            pt = (anchors or {}).get(key) or rec.at(a["hub"])
            out.append(S("map_at", where=pin_words(pt, (0, 0, 1920, 1080)).capitalize(),
                         thing="%s, %s" % (hub["as"], hub["look"])))
    else:
        area = [k for k, a in r["areas"].items() if a["stem"] == stem][0]
        hub = rec.building_of(r["areas"][area]["hub"])
        out.append(S("the_place", thing="the part of the school round %s" % hub["as"]))
        pins = campus_plan.pin_targets(record, area)
        seen = set()
        for place in sorted(pins, key=lambda k: (pins[k][1], pins[k][0])):
            b = rec.building_of(place)
            if b["key"] in seen:
                continue
            seen.add(b["key"])
            out.append(S("map_at", where=pin_words(pins[place]).capitalize(), thing="%s, %s" % (b["as"], b["look"])))
    out.append(check_prompts.text_of("map.txt"))
    out.append(check_prompts.text_of("look.txt"))
    return " ".join(out)


def map_refs(rec, manifest, stem, root=None):
    r = rec.r
    refs = []
    if stem == r.get("campus_map", {}).get("stem", "map_campus"):
        for key, a in r["areas"].items():
            game = os.path.join(root or ROOT, "game", "images", "bg", a["stem"] + ".png")
            if not os.path.exists(game):
                raise Refused("the %s map is chosen but its file is not in the game" % a["name"])
            refs.append(("neighbour", a["stem"], game))
        return refs
    area = [k for k, a in r["areas"].items() if a["stem"] == stem][0]
    hub = r["areas"][area]["hub"]
    refs.append(("neighbour", hub, need_chosen(rec, manifest, hub, "It is the map's first reference.", root)))
    for p in rec.places.values():
        b = rec.buildings[p["building"]]
        crop = os.path.join(REFS, b["key"] + ".png")
        if p["area"] == area and os.path.exists(crop) and ("building", b["key"], crop) not in refs:
            refs.append(("building", b["key"], crop))
    plan = PLAN_REF % area
    if os.path.exists(plan):
        refs.append(("plan", area, plan))
    return refs[:MAX_REFS]


# ---- the workflow kit (make_redo_workflow.py and art_batch.py use it too) ----------------------------------------
def seeds_for(stem, again=0):
    base = 3000 + (sum(ord(c) * (i + 1) for i, c in enumerate(stem)) % 4000) * 2 + again * 20
    return [base + k for k in range(len(VERSIONS))]


def job(stem, label, prompt, inputs, again=0, checklist=(), kind="composed", note=None, place=None):
    """One picture of a workflow: its prompt, its input pictures [(title, file)], two fixed seeds.
    place: the place it is a picture of, which the prompt check reads (K16 is stricter in some)."""
    return {"stem": stem, "place": place, "label": label, "prompt": prompt, "inputs": list(inputs), "seeds": seeds_for(stem, again),
            "save": ["ui2_%s_%s" % (stem, v) for v in VERSIONS], "checklist": list(checklist), "kind": kind,
            "note": note}


def input_name(stem, n, path):
    return "ui2_in_%s_%d%s" % (stem, n, os.path.splitext(path)[1].lower() or ".png")


def build(title, intro, jobs):
    """The workflow: one row a picture; its input pictures, then version A over version B."""
    proto = json.load(open(os.path.join(ROOT, "tools", "comfy_nodes", "edit_nodes.json")))
    P, shell = proto["nodes"], proto["shell"]
    nodes, links, groups = [], [], []
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
        node.pop("widgets_values_named", None)
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

    renders = sum(len(j["seeds"]) for j in jobs)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [-640, -560], "size": [600, 480],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## %s\n\n%s\n\n"
        "Run this in the **local ComfyUI**. Press **Run** once.\n\n"
        "Each row is one picture, painted twice: **version A** on top, **version B** under it. You choose "
        "between them afterwards.\n\n"
        "The **Load Image** boxes on the left should already show their pictures. If one shows an error, click "
        "**choose file to upload** and pick the file with the same name from `JJK Game images/ui2`.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, about $%.2f a picture, charged to your Comfy "
        "account).\n\n"
        "You don't need to save anything: the results go to ComfyUI's output folder and Claude picks them up "
        "from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (title, intro, renders, renders * COST, COST)]})

    row_h = 1260
    for r, j in enumerate(jobs):
        y = r * row_h
        n_in = len(j["inputs"])
        loads = []
        for k, (ititle, name) in enumerate(j["inputs"]):
            ld = add("LoadImage", (-1960 + (k % 4) * 330, y + (k // 4) * 380), (310, 340),
                     title="Load Image %d: %s" % (k + 1, ititle))
            ld["widgets_values"] = [name, "image"]
            loads.append(ld)
        # The editor is handed its pictures as one batch, in order. A batch box
        # takes three; a longer list is chained, the batch so far going in first.
        src = None
        if n_in == 1:
            src = loads[0]
        elif n_in > 1:
            rest = list(loads)
            src = rest.pop(0)
            k = 0
            while rest:
                b = add("BatchImagesNode", (-600 + k * 60, y + 40 + k * 150), (225, 120),
                        title="The pictures, in order" if not k else "and the next")
                wire(src, 0, b, "images.image0")
                wire(rest.pop(0), 0, b, "images.image1")
                if rest:
                    wire(rest.pop(0), 0, b, "images.image2")
                src = b
                k += 1
        for v, (seed, save) in enumerate(zip(j["seeds"], j["save"])):
            letter = VERSIONS[v].upper()
            gy = y + v * 600
            g = add("GeminiImage2Node", (0, gy), (420, 540), title="Nano Banana Pro: %s, version %s" % (j["label"], letter))
            w = g["widgets_values"]
            # A fixed seed for each box, so a Run that stops can be pressed again and
            # reuse what finished. 16:9 at 2K is 2752x1536: nothing is enlarged from 1K.
            w[0], w[2], w[3], w[4], w[5], w[6] = j["prompt"], seed, "fixed", "16:9", RESOLUTION, "IMAGE"
            if src is not None:
                wire(src, 0, g, "images")
            s = add("SaveImage", (440, gy), (620, 540), title="%s: version %s" % (j["label"], letter))
            s["widgets_values"] = [save]
            wire(g, 0, s, "images")
        groups.append({"id": r + 1, "title": "%s:  A over B" % j["label"].upper(),
                       "bounding": [-1980, y - 50, 3060, row_h - 60], "color": "#3f4f5a", "font_size": 24,
                       "flags": {}})

    wf = dict(shell)
    wf.update({"id": str(uuid.uuid4()), "revision": 0, "last_node_id": ids["n"], "last_link_id": ids["l"],
               "nodes": nodes, "links": links, "groups": groups})
    wf["extra"] = dict(wf.get("extra") or {})
    wf["extra"]["ds"] = {"scale": 0.35, "offset": [2040, 640]}
    return wf


def write_workflow(path, title, intro, jobs, out_dir=None, record=None):
    """Copy every input picture beside the workflow (and into ComfyUI's input
    folder when this is the owner's own folder), then write the workflow."""
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    staged = []
    for j in jobs:
        check_prompts.refuse_if_bad(j["prompt"], j["label"], record or check_prompts.load_record(), j.get("place"))
        named = []
        for n, (ititle, src) in enumerate(j["inputs"], 1):
            name = input_name(j["stem"], n, src)
            staged.append((src, name))
            named.append((ititle, name))
        j["inputs_named"] = named
    for src, name in staged:
        shutil.copy(src, os.path.join(out_dir, name))
        if os.path.abspath(out_dir) == os.path.abspath(OUT) and os.path.isdir(COMFY_INPUT):
            shutil.copy(src, os.path.join(COMFY_INPUT, name))
    wf = build(title, intro, [dict(j, inputs=j["inputs_named"]) for j in jobs])
    json.dump(wf, open(path, "w"), indent=1)
    return wf


def renders_in(workflow):
    return [n for n in workflow["nodes"] if n["type"] == "GeminiImage2Node"]


# ---- one picture ------------------------------------------------------------------------------------------
REF_TITLES = {"neighbour": "%s, as chosen", "building": "%s, cut from a chosen picture",
              "old_camera": "%s as it was painted before", "old_school": "%s as it was painted before",
              "plan": "the plan of %s"}


def checklist_for(rec, place):
    """Up to five yes/no lines a person reads off each version (5.2, the third rung of trust)."""
    p = rec.places[place]
    lines = list(p.get("check", []))
    rows = sorted(check_campus.view_rows(rec, place), key=lambda r: (not rec.is_fixed(r), r.get("order") or 9))
    for row in rows:
        if len(lines) >= 5:
            break
        what = rec.buildings[row["thing"]]["name"] if row.get("thing") and row["side"] != "bottom" \
            else "the way to %s" % rec.name(row.get("to"))
        where = {"left": "on the left", "ahead": "ahead", "right": "on the right",
                 "bottom": "at the bottom of the picture"}[row["side"]]
        lines.append("%s is %s" % (what, where))
    return ["%s: yes / no" % l for l in lines[:5]]


def scene_job(record, manifest, stem, again=0, root=None, dump=None):
    """The job for one composed picture, or Refused."""
    rec = check_campus.Rec(record)
    r = rec.r
    map_stems = [a["stem"] for a in r["areas"].values()] + [r.get("campus_map", {}).get("stem", "map_campus")]
    if stem in map_stems:
        k8_map(rec, stem)
        refs = map_refs(rec, manifest, stem, root)
        anchors = dict((a["key"], a["anchor"]) for a in dump["areas"]) if dump else None
        prompt = map_prompt_for(record, stem, refs, anchors)
        name = "The campus map" if stem == map_stems[-1] else "The %s map" % [
            check_campus.map_name(a) for a in r["areas"].values() if a["stem"] == stem][0]
        inputs = [(REF_TITLES[k] % (rec.name(key) if key in rec.places or key in rec.buildings else key), f)
                  for k, key, f in refs]
        return job(stem, name, prompt, inputs, again, ["every building is where the ground plan has it: yes / no",
                                                       "there is open ground beside each building: yes / no"],
                   kind="map")
    place = next((k for k, p in rec.places.items() if p["stem"] == stem or k == stem), None)
    if place is None:
        raise Refused("%s is not a place or a map of the record" % stem)
    p = rec.places[place]
    if p["how"] != "composed":
        raise Refused("%s is redone in place, not composed again: use tools/make_redo_workflow.py" % p["name"])
    if rec.chosen(place) is not None and not again:
        raise Refused("%s already has a chosen picture%s; say --again N to make another pair"
                      % (p["name"], " (%s)" % rec.chosen(place)["render"] if rec.chosen(place).get("render") else ""))
    k8_place(rec, place)
    refs = refs_for(rec, manifest, place, root)
    prompt = prompt_for(record, place, refs)
    inputs = [(REF_TITLES[k] % rec.name(key), f) for k, key, f in refs]
    return job(p["stem"], p["name"], prompt, inputs, again, checklist_for(rec, place), place=place)


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

    out_dir, again = opt("--out"), int(opt("--again") or 0)
    record = check_campus.load_record(opt("--record"))
    manifest = check_campus.load_manifest(path=opt("--manifest"))
    dump_path = opt("--layout-dump")
    rec = check_campus.Rec(record)
    if "--list" in argv:
        stems = [p["stem"] for p in rec.places.values() if p["how"] == "composed"]
        stems += [a["stem"] for a in record["areas"].values()] + [record["campus_map"]["stem"]]
        for stem in stems:
            try:
                j = scene_job(record, manifest, stem)
                print("%-16s ready: %d reference picture%s" % (stem, len(j["inputs"]), "" if len(j["inputs"]) == 1 else "s"))
            except Refused as e:
                print("%-16s %s" % (stem, e))
        return
    show = "--print" in argv
    if show: argv.remove("--print")
    if len(argv) != 1 or argv[0].startswith("--"):
        print(__doc__); raise SystemExit(1)
    stem = argv[0]
    dump = None
    if stem == record.get("campus_map", {}).get("stem"):
        dump = check_campus.load_dump(dump_path)
    try:
        j = scene_job(record, manifest, stem, again, dump=dump)
    except Refused as e:
        raise SystemExit(str(e))
    check_prompts.refuse_if_bad(j["prompt"], j["label"], record, j.get("place"))
    if show:
        print(j["prompt"])
        for n, (title, f) in enumerate(j["inputs"], 1):
            print("picture %d: %s  <- %s" % (n, title, f))
        return
    out_dir = out_dir or OUT
    path = os.path.join(out_dir, "scene_%s.json" % j["stem"])
    wf = write_workflow(path, j["label"], "One picture, composed again from the campus record.", [j], out_dir, record)
    print("%-16s %d versions, about $%.2f" % (j["stem"], len(renders_in(wf)), len(renders_in(wf)) * COST))
    print("   workflow -> %s" % path)


if __name__ == "__main__":
    main(sys.argv[1:])
