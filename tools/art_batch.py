"""
One art sitting: the workflows the owner drags into ComfyUI, and the page of
numbered steps that goes with them.

    python3 tools/art_batch.py --list             # every batch: what, how many renders, what it waits for
    python3 tools/art_batch.py 1                  # write batch 1's files
    python3 tools/art_batch.py 3b                 # one file of a batch that has a pause in it
    python3 tools/art_batch.py 1 --preview --out <folder>     # write it early, somewhere else, to read
    python3 tools/art_batch.py 1 --again 1        # one more pair of every picture, from two other seeds
    python3 tools/art_batch.py --done 3a          # the art-install role: 3a's pictures are installed
    python3 tools/art_batch.py --selftest
    options: --out <folder>   --manifest <pictures.json>   --record <campus.json>   --keep <folder>

docs/UI2_DESIGN.md 5.13, D25, D52, D53, K8. The batch table is data:
tools/art/batches.json. For each file of a sitting this writes
`art_<n>[a|b|_1|_2].json` (drag it into the LOCAL ComfyUI, press Run) and one
page, `art_<n>.md`, into ~/Desktop/JJK Game images/ui2/.

  - Every picture is made in two versions, from two fixed seeds: the owner
    chooses. Results are saved as `ui2_<picture>_a_...` and `..._b_...`.
  - No sitting is over twelve renders and no file over ten (a rate-limit
    failure aborts a run), so a sitting of twelve is always two files.
  - "a then b" is two files with a pause: b is made from a's installed
    pictures, so b's file is written only when a is marked done.
  - It queues nothing. The owner presses Run (K14).

THE ORDER IS ENFORCED, twice (K8). The table's "needs first" is held here: a
batch is not written until the batches it needs are marked done in
batches.json (`--done`, the art-install role's word, when their pictures are
installed or their wording is judged). And each maker holds its own rule
whatever the table says: a place after the yard it stands off, an hour
picture after its day picture, a map after every place on it. A refusal is
one plain line, and nothing at all is written when any picture of a file is
refused. --preview skips only the table's rule, never a maker's, and must be
given a folder of its own: it is for reading a batch's prompts early.

WHAT IT WRITES ITSELF: pictures composed again (a yard, the gate, a new
place), rooms redone in place, evenings and nights, the maps
(tools/make_scene_workflow.py, tools/make_redo_workflow.py). A pose, the icon
sheet, a face, a person and the pictures off campus are made by other tools or
do not have their words yet; for those it says which, and writes nothing.

Plain Python.
"""
import sys, os, json, copy, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_prompts
import check_campus
import make_scene_workflow as scene
import make_redo_workflow as redo
from make_scene_workflow import Refused

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCHES = os.path.join(ROOT, "tools", "art", "batches.json")
OWN_KINDS = ("composed", "inplace", "relight", "map")
OTHER = {
    "pose": "a painted pose is written by tools/make_pose_workflow.py (its tooling is U0d2's, its rows are picked "
            "by U3); art_batch.py does not write it",
    "icons": "the icon sheet is written by tools/make_icon_workflow.py",
    "face": "the file for this run already exists (docs/UI2_DESIGN.md D57)",
    "blink": "blink and talk are written person by person, by phase 2's steps (docs/ART_PHASE2.md, batch 5)",
    "person": "a new person is a sitting of its own (docs/ASSET_PIPELINE.md): a base on Comfy Cloud, then repairs",
    "scene": "the words for the pictures off campus are not in the batch table yet (docs/UI2_DESIGN.md 5.8)",
    "veil": "the strong veil picture is made from the new ridge once it is installed; its words are not written yet",
    "menu": "the main menu's picture waits for the mock-up the owner chooses at checkpoint C",
    "curse": "the curses are painted from words on flat green; their words are not written yet (5.11)",
    "tokyo_map": "the Tokyo map is not a place of the campus record; its redo is written with batch 32's pictures",
    "installed": "nothing to run: these pictures are already made and are installed by tools/install_redo.py",
}


def load(path=None):
    return json.load(open(path or BATCHES, encoding="utf-8"))


def save(data, path=None):
    with open(path or BATCHES, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def find(data, n):
    for b in data["batches"]:
        if b["id"] == str(n):
            return b
    return None


def versions(pic):
    return int(pic.get("versions", 2))


def file_renders(f):
    return sum(versions(p) for p in f["pictures"])


def batch_renders(b):
    return b["renders"] if "renders" in b else sum(file_renders(f) for f in b["files"])


def markers(b):
    """The markers that stand for this batch's files, in order: ["3a", "3b"], or ["14"]."""
    parts = [b["id"] + f["part"] for f in b["files"] if f.get("part")]
    return parts or [b["id"]]


def is_done(data, marker):
    done = set(data.get("done", []))
    if marker in done:
        return True
    b = find(data, marker)
    if b is not None:           # a whole batch: done when each of its files is
        return len(markers(b)) > 1 and all(x in done for x in markers(b))
    m = re.match(r"^(\d+)([a-z])$", marker)
    return bool(m) and m.group(1) in done


def missing_needs(data, b, f):
    need = list(b.get("needs", [])) + list(f.get("needs", []))
    return [n for n in need if not is_done(data, n)]


def target(data, arg):
    """(batch, [files]) for "3", "3b", "0b"."""
    b = find(data, arg)
    if b is not None:
        return b, list(b["files"])
    m = re.match(r"^(\d+)([a-z])$", arg)
    if m:
        b = find(data, m.group(1))
        if b is not None:
            files = [f for f in b["files"] if f.get("part") == m.group(2)]
            if files:
                return b, files
    raise SystemExit("no batch %s in tools/art/batches.json (see --list)" % arg)


def picture_job(pic, record, manifest, again=0, root=None, work_dir=None, keep_dir=None, dump=None):
    kind = pic["kind"]
    if kind == "composed":
        return scene.scene_job(record, manifest, pic["place"], again, root)
    if kind == "map":
        return scene.scene_job(record, manifest, pic["stem"], again, root, dump)
    if kind == "inplace":
        return redo.redo_job(record, manifest, pic["place"], None, pic.get("from_rev1", False), pic.get("add", False),
                             pic.get("change", False), None, again, root, work_dir, keep_dir)
    if kind == "relight":
        return redo.redo_job(record, manifest, pic["place"], pic["hour"], hour_words=pic.get("hour_words"),
                             again=again, root=root, work_dir=work_dir, keep_dir=keep_dir)
    raise Refused(OTHER.get(kind, "art_batch.py does not know how a %r is made" % kind))


def what_of(pic, rec=None):
    name = (rec.name(pic["place"]) if rec and pic.get("place") else None) or pic.get("stem") or pic.get("what") or ""
    kind = pic["kind"]
    if kind == "relight":
        return "%s, %s" % (name, pic["hour"])
    if kind == "pose":
        return "pose, row %s%s" % (pic["row"], ": " + pic["what"] if pic.get("what") else "")
    if kind == "inplace":
        return "%s%s%s" % (name, ", with its named addition" if pic.get("add") else "",
                           ", from its picture of before the overhaul" if pic.get("from_rev1") else "")
    return name + (" (%s)" % pic["what"] if pic.get("what") and kind not in OWN_KINDS else "")


def file_jobs(f, record, manifest, again=0, root=None, work_dir=None, keep_dir=None, dump=None):
    """(jobs, refusals) for one file. Nothing is written if there is a refusal."""
    jobs, refused = [], []
    rec = check_campus.Rec(record)
    for pic in f["pictures"]:
        try:
            j = picture_job(pic, record, manifest, again, root, work_dir, keep_dir, dump)
            bad = check_prompts.check(j["prompt"], record, place=j.get("place"))
            if bad:
                raise Refused("its prompt fails tools/check_prompts.py: " + "; ".join(bad))
            jobs.append(j)
        except Refused as e:
            refused.append("%s: %s" % (what_of(pic, rec), e))
    return jobs, refused


# ---- the page of numbered steps -------------------------------------------------------------------------------
def page(b, written, waiting, record, cost):
    """art_<n>.md: for the owner first, then for the session that installs."""
    rec = check_campus.Rec(record)
    L = ["# Art sitting %s: %s" % (b["id"], b["title"]), ""]
    total = sum(len(j["seeds"]) for _, jobs in written for j in jobs)
    L.append("**%d picture%s to run, about $%.2f.** Each picture is painted twice, so you choose between a "
             "version A and a version B." % (total, "" if total == 1 else "s", total * cost))
    L.append("")
    L += ["## What to do", ""]
    n = 1
    for i, (f, jobs) in enumerate(written):
        r = sum(len(j["seeds"]) for j in jobs)
        L.append("%d. Open the **local ComfyUI**. Drag `%s.json` from `JJK Game images/ui2` onto the canvas." % (n, f["name"])); n += 1
        L.append("%d. Press **Run** once. It paints %d pictures (about $%.2f): %s." % (
            n, r, r * cost, ", ".join(j["label"] for j in jobs))); n += 1
        L.append("%d. If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** "
                 "again. A finished picture is not paid for twice." % n); n += 1
        if f.get("part") and i == len(written) - 1 and waiting:
            L.append("%d. Tell Claude it has finished, and which version of each picture you like better. Claude "
                     "checks both versions of each and installs the ones you choose." % n); n += 1
    if not (written and written[-1][0].get("part") and waiting):
        L.append("%d. Tell Claude it has finished, and which version of each picture you like better. You don't "
                 "need to save or move anything: Claude picks the results up from ComfyUI's output folder." % n); n += 1
    for f, why in waiting:
        L.append("%d. **Later:** `%s.json` is not written yet. %s Claude writes it when that is done; then it is "
                 "the same three steps again." % (n, f["name"], why)); n += 1
    L += ["", "## What you will be shown", ""]
    L.append("For each picture, version A beside version B, each with one word:")
    L.append("")
    L.append("- **PASS**: it can go in.")
    L.append("- **LOOK**: here is what changed; choose it or not.")
    L.append("- **REFUSED**: something moved, vanished or appeared (it says what). It cannot be chosen. If both "
             "versions are refused, the answer is \"run it once more\".")
    L += ["", "## For the session that installs (not the owner)", ""]
    if b.get("note"):
        L += [b["note"], ""]
    if b.get("needs_words"):
        L += ["Needs first: %s." % b["needs_words"], ""]
    for f, jobs in written:
        for j in jobs:
            L.append("### %s (`%s`)" % (j["label"], j["stem"]))
            L.append("")
            L.append("Results: `%s_0000N_.png`, `%s_0000N_.png` in ComfyUI's output folder." % tuple(j["save"]))
            for k, (title, src) in enumerate(j["inputs"], 1):
                L.append("Picture %d given to the editor: %s (`%s`)." % (k, title, os.path.basename(src)))
            L.append("")
            for line in j["checklist"]:
                L.append("- %s" % line)
            L.append("")
            L.append("Prompt:")
            L.append("")
            L.append("> " + j["prompt"])
            L.append("")
    if b.get("unlocks"):
        L += ["## What it unlocks in the game", "", b["unlocks"] + ".", ""]
    return "\n".join(L)


def write_batch(data, arg, record, manifest, out_dir=None, preview=False, again=0, root=None, keep_dir=None,
                dump=None, quiet=False):
    """Write what can be written of a batch. Returns (written [(file, jobs, path)], waiting [(file, why)])."""
    b, files = target(data, arg)
    out_dir = out_dir or scene.OUT
    cost = data.get("cost_per_render", scene.COST)
    limits = data.get("limits", {"batch": 12, "file": 10})
    if batch_renders(b) > limits["batch"]:
        raise SystemExit("batch %s is %d renders; no sitting is over %d" % (b["id"], batch_renders(b), limits["batch"]))
    ready, waiting, refusals = [], [], []
    for f in files:
        marker = b["id"] + (f.get("part") or "")
        if file_renders(f) > limits["file"]:
            raise SystemExit("%s is %d renders; no single run is over %d" % (f["name"], file_renders(f), limits["file"]))
        if not f.get("name"):
            refusals.append("batch %s: %s" % (b["id"], OTHER.get(f["pictures"][0]["kind"], "there is nothing to run")))
            continue
        need = [] if preview else missing_needs(data, b, f)
        if need:
            waiting.append((f, "It waits for %s." % scene._and(["batch " + x for x in need])))
            continue
        if is_done(data, marker) and not again and not preview:
            waiting.append((f, "It is already marked done (say --again 1 for one more pair)."))
            continue
        jobs, refused = file_jobs(f, record, manifest, again, root, out_dir, keep_dir, dump)
        if refused:
            refusals += ["%s: %s" % (f["name"], r) for r in refused]
        else:
            ready.append((f, jobs))
    if refusals or not ready:
        lines = refusals + ["%s: %s" % (f["name"], why) for f, why in waiting]
        raise Refused("batch %s is not written:\n  - %s" % (arg, "\n  - ".join(lines)))
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for f, jobs in ready:
        path = os.path.join(out_dir, f["name"] + ".json")
        scene.write_workflow(path, "Art sitting %s: %s" % (b["id"] + (f.get("part") or ""), b["title"]),
                             "%d picture%s, each painted twice." % (len(jobs), "" if len(jobs) == 1 else "s"),
                             jobs, out_dir, record)
        written.append((f, jobs, path))
        if not quiet:
            r = sum(len(j["seeds"]) for j in jobs)
            print("%-10s %d renders, about $%.2f: %s" % (f["name"], r, r * cost, ", ".join(j["label"] for j in jobs)))
            print("   workflow -> %s" % path)
    note = os.path.join(out_dir, "art_%s.md" % b["id"])
    open(note, "w", encoding="utf-8").write(page(b, [(f, jobs) for f, jobs, _ in written], waiting, record, cost))
    if not quiet:
        print("   the steps -> %s" % note)
        for f, why in waiting:
            print("%-10s not written yet. %s" % (f["name"], why))
    return written, waiting


def listing(data):
    rec = check_campus.Rec(check_campus.load_record())
    total = 0
    for b in data["batches"]:
        if b.get("heading"):
            print("\n  %s" % b["heading"])
        r = batch_renders(b)
        total += r if b["id"].isdigit() else 0
        state = "done" if is_done(data, b["id"]) else ""
        need = [n for n in b.get("needs", []) if not is_done(data, n)]
        print("%3s  %-62s %2s renders  %s%s" % (
            b["id"], b["title"][:62], r if r else "-", state,
            ("waits for " + ", ".join(need)) if need and not state else ""))
        for f in b["files"]:
            if len(b["files"]) > 1 and f.get("name"):
                print("       %-10s %2d  %s" % (f["name"], file_renders(f), "; ".join(what_of(p, rec) for p in f["pictures"])[:150]))
    print("\n%d renders in batches 1 to 46 (the four people are extra), about $%.2f"
          % (total, total * data.get("cost_per_render", 0.16)))


# ---- the tests ---------------------------------------------------------------------------------------------
def selftest():
    import tempfile, shutil
    fails, skips = [], []

    def ok(what, cond, detail=None):
        print("  %s  %s" % ("ok  " if cond else "FAIL", what))
        if not cond:
            fails.append(what)
            for d in (detail or [])[:8]:
                print("          %s" % str(d)[:400])

    def refused(fn):
        try:
            fn()
            return None
        except Refused as e:
            return str(e)

    def two_each(path):
        """Every picture of a workflow is rendered exactly twice, as _a and _b, from two different fixed seeds."""
        wf = json.load(open(path))
        saves = {}
        ids = dict((n["id"], n) for n in wf["nodes"])
        for l in wf["links"]:
            a, b = ids[l[1]], ids[l[3]]
            if a["type"] == "GeminiImage2Node" and b["type"] == "SaveImage":
                stem, letter = b["widgets_values"][0].rsplit("_", 1)
                saves.setdefault(stem, []).append((letter, a["widgets_values"][2], a["widgets_values"][3]))
        return bool(saves) and all(sorted(x[0] for x in v) == ["a", "b"] and v[0][1] != v[1][1]
                                   and all(x[2] == "fixed" for x in v) for v in saves.values())

    data = load()
    record = check_campus.load_record()
    rec = check_campus.Rec(record)
    nothing = {"pictures": {}}
    stage = check_prompts.text_of("stage.txt")
    tmp = tempfile.mkdtemp(prefix="art_batch_test_")
    try:
        # the table is the plan's
        def renders(lo, hi):
            return sum(batch_renders(b) for b in data["batches"] if b["id"].isdigit() and lo <= int(b["id"]) <= hi)

        curses = sum(versions(p) for b in data["batches"] for f in b["files"] for p in f["pictures"] if p["kind"] == "curse")
        ok("the table's counts are the plan's: 40, 178, 140 and six curse renders, 70",
           (renders(1, 5), renders(6, 22), renders(23, 36) - curses, curses, renders(41, 46)) == (40, 178, 140, 6, 70),
           [(renders(1, 5), renders(6, 22), renders(23, 36) - curses, curses, renders(41, 46))])
        pics = [(b, f, p) for b in data["batches"] for f in b["files"] for p in f["pictures"]]
        ok("64 hour pictures and 67 poses", (sum(1 for _, _, p in pics if p["kind"] == "relight"),
                                             sum(1 for _, _, p in pics if p["kind"] == "pose")) == (64, 67))
        ok("no sitting is over twelve renders and no file over ten",
           all(batch_renders(b) <= 12 for b in data["batches"]) and all(file_renders(f) <= 10 for _, f, _ in pics))
        ok("every picture the table composes, redoes or relights is a place of the record, made the way the record says",
           all(p["place"] in rec.places and (p["kind"] == "relight" or rec.places[p["place"]]["how"] == p["kind"])
               for _, _, p in pics if p["kind"] in ("composed", "inplace", "relight")),
           [p for _, _, p in pics if p["kind"] in ("composed", "inplace") and rec.places.get(p.get("place"), {}).get("how") != p["kind"]])
        made = set(p["place"] for _, _, p in pics if p["kind"] in ("composed", "inplace", "installed"))
        ok("all 35 places are in the table", made == set(rec.places), sorted(set(rec.places) - made))
        ok("each place's batch in the record is the table's",
           all(rec.places[p["place"]]["batch"] == b["id"] or (b["id"] in ("3", "4") and p.get("from_rev1"))
               for b, _, p in pics if p["kind"] in ("composed", "inplace", "installed")),
           [(b["id"], p["place"], rec.places[p["place"]]["batch"]) for b, _, p in pics
            if p["kind"] in ("composed", "inplace", "installed") and rec.places[p["place"]]["batch"] != b["id"]])

        # the order: the table's, then the makers'
        msg = refused(lambda: write_batch(data, "1", record, nothing, os.path.join(tmp, "x"), quiet=True))
        ok("batch 1 is not written before batch 0 is done", msg is not None and "waits for batch 0" in msg, [msg])
        msg = refused(lambda: write_batch(data, "2", record, nothing, os.path.join(tmp, "x"), preview=True, quiet=True))
        ok("the staff steps are refused before the garden is chosen (even in a preview)",
           msg is not None and "Staff Building Steps cannot be made yet: Dormitory Garden has no chosen picture" in msg, [msg])
        msg = refused(lambda: redo.redo_job(record, nothing, "classroom"))
        ok("a room is refused before its yard", msg is not None and "School Courtyard has no chosen picture" in msg, [msg])
        msg = refused(lambda: scene.scene_job(record, nothing, "area_heart"))
        ok("an area map is refused before every place on it has its picture",
           msg is not None and "Main Gate has no chosen picture" in msg, [msg])
        msg = refused(lambda: redo.redo_job(record, nothing, "dorm_common", "evening"))
        ok("an hour picture is refused before its day picture is installed in the new look",
           msg is not None and "day picture is not installed in the new look" in msg, [msg])
        msg = refused(lambda: write_batch(data, "5", record, nothing, os.path.join(tmp, "x"), preview=True, quiet=True))
        ok("a batch another tool makes says which, and writes nothing", msg is not None and "make_pose_workflow.py" in msg
           and not os.path.exists(os.path.join(tmp, "x")), [msg])

        # batch 1, as it will be written: three yards from words and the chosen Courtyard
        court = os.path.expanduser(record["pictures"]["courtyard"]["source"])
        if not os.path.exists(court):
            skips.append("batch 1's files (the chosen Courtyard is not on this machine: %s)" % court)
            print("  SKIP  batch 1's files: the chosen Courtyard is not at %s" % court)
        else:
            out1 = os.path.join(tmp, "batch1")
            written, _ = write_batch(data, "1", record, nothing, out1, preview=True, quiet=True)
            jobs = written[0][1]
            ok("batch 1 is one file of three yards", [j["stem"] for j in jobs] == ["school_yard", "dorm_yard", "training_yard"])
            ok("each carries the chosen Courtyard as its first reference",
               all(j["inputs"] and j["inputs"][0][1] == court and j["inputs_named"][0][1].startswith("ui2_in_")
                   for j in jobs)
               and all(open(os.path.join(out1, j["inputs_named"][0][1]), "rb").read() == open(court, "rb").read() for j in jobs))
            said = {"school_yard": "the same building that stands on the left of picture 1",
                    "training_yard": "the same building that stands on the right of picture 1",
                    "dorm_yard": "are gate lodges, not the dormitories"}
            ok("each says the fixed facts in words", all(said[j["stem"]] in j["prompt"] for j in jobs))
            ok("each passes the prompt check", all(not check_prompts.check(j["prompt"], record) for j in jobs))
            ty = [j for j in jobs if j["stem"] == "training_yard"][0]["prompt"].lower()
            ok("the Training Yard's prompt asks for no vending machine and no shoe lockers",
               "vending" not in ty and "shoe locker" not in ty and "weapon rack" not in ty)
            ok("each has the stage text and none has the map text",
               all(stage in j["prompt"] and check_prompts.text_of("map.txt") not in j["prompt"] for j in jobs))
            wf = json.load(open(written[0][2]))
            boxes = scene.renders_in(wf)
            saves = sorted(n["widgets_values"][0] for n in wf["nodes"] if n["type"] == "SaveImage")
            ok("the workflow renders two versions of each, at 2K, from fixed seeds, saved with a letter",
               len(boxes) == 6 and all(n["widgets_values"][3] == "fixed" and n["widgets_values"][5] == "2K"
                                       and n["widgets_values"][4] == "16:9" for n in boxes)
               and len(set(n["widgets_values"][2] for n in boxes)) == 6
               and saves == sorted("ui2_%s_%s" % (s, v) for s in said for v in "ab"), saves)
            ok("every picture in it is rendered twice", two_each(written[0][2]))
            ok("and passes check_prompts.py as a file",
               all(not check_prompts.check(p, record) for _, p in check_prompts.prompts_in(written[0][2])))
            note = open(os.path.join(out1, "art_1.md"), encoding="utf-8").read()
            ok("the page of steps is written, with a checklist for each yard",
               "Press **Run** once" in note and "no vending machine and no shoe lockers in this yard: yes / no" in note
               and "Training Hall is on the left: yes / no" in note)

        # a later state, made up for the test: the first two rings chosen, batch 0 installed
        later = copy.deepcopy(record)
        man = {"pictures": {}}
        game = os.path.join(ROOT, "game", "images", "bg")
        for place in ("school_yard", "dorm_yard", "training_yard", "staff_yard", "trailhead", "gate", "dorm"):
            p = rec.places[place]
            later["pictures"][p["stem"]] = {"place": place, "rev": 2, "kind": p["how"], "source": os.path.join(game, p["stem"] + ".png")}
        for stem in ("courtyard", "library", "dorm_common", "cafeteria", "your_room"):
            man["pictures"][stem] = {"rev": 2, "kind": "inplace", "rev1_commit": "HEAD", "from_commit": "HEAD"}
        keep = os.path.join(tmp, "keep")
        os.makedirs(keep)
        json.dump({"keep": [], "empty": [], "allow": [{"name": "a closed laptop on the desk", "box": [400, 540, 120, 70]}]},
                  open(os.path.join(keep, "your_room.json"), "w"))
        state = copy.deepcopy(data)
        state["done"] = ["0", "1", "2"]
        need_files = [os.path.join(game, s + ".png") for s in ("dorm_yard", "your_room", "dorm_common", "school_yard")]
        have_git = os.path.exists(os.path.join(ROOT, ".git"))
        if not all(os.path.exists(x) for x in need_files) or not have_git:
            skips.append("batches 3a and 9a (the game's pictures or git are not here)")
            print("  SKIP  batches 3a and 9a: the game's pictures or git are not here")
        else:
            out3 = os.path.join(tmp, "batch3")
            written, waiting = write_batch(state, "3", later, man, out3, keep_dir=keep, quiet=True)
            jobs = written[0][1]
            ok("batch 3a is written without refusing: the Common Room once more, and My Room before its corridor exists",
               [j["stem"] for j in jobs] == ["dorm_common", "your_room"] and [f["name"] for f, _ in waiting] == ["art_3b"],
               [j["stem"] for j in jobs])
            cr, mr = jobs[0]["prompt"], jobs[1]["prompt"]
            ok("the Common Room's prompt is the keep text, the light sentence, its window line from the record, the look",
               cr.startswith(check_prompts.text_of("keep.txt") + " " + check_prompts.text_of("keep_light.txt")
                             + " Through the windows: at the back, the foot of a tall wooden tower and cedars; on the "
                             "left, the dark timber and upstairs gallery of the boys' dormitory. ")
               and cr.endswith(check_prompts.text_of("look.txt")), [cr])
            ok("its input is the picture it had before the overhaul, from git",
               os.path.basename(jobs[0]["inputs"][0][1]) == "ui2_rev1_dorm_common.png"
               and os.path.getsize(jobs[0]["inputs"][0][1]) > 100000)
            ok("My Room's prompt names its one addition and nothing else to add",
               "Do not remove or tidy away anything, and add nothing except this: a closed laptop on the desk." in mr
               and redo.LAST not in mr and "Through the windows: the forested mountain slope" in mr, [mr])
            ok("neither says 'nothing on the floor'", "nothing on" not in cr and "nothing on" not in mr)
            out9 = os.path.join(tmp, "batch9")
            state["done"] = ["0", "1", "2", "3"]
            written, _ = write_batch(state, "9a", later, man, out9, keep_dir=keep, quiet=True)
            jobs = written[0][1]
            ok("batch 9a is written without refusing: a house and a room inside it, in one file",
               [j["stem"] for j in jobs] == ["boys_dorm", "yuji_room"] and two_each(written[0][2])
               and len(scene.renders_in(json.load(open(written[0][2])))) == 4,
               [j["stem"] for j in jobs])
            ok("the room carries the garden and My Room as references, and its window line",
               len(jobs[1]["inputs"]) == 2 and "Through the windows: the dormitory garden and its pond." in jobs[1]["prompt"],
               [jobs[1]["inputs"], jobs[1]["prompt"]])
            state["done"] = ["0", "1", "2", "3a"]
            written, _ = write_batch(state, "3b", later, man, os.path.join(tmp, "batch3b"), keep_dir=keep, quiet=True)
            ok("batch 3b is four hour pictures, each from the installed day picture",
               [j["stem"] for j in written[0][1]] == ["dorm_common_evening", "dorm_common_night", "your_room_evening", "your_room_night"]
               and all(os.path.basename(j["inputs"][0][1]) in ("dorm_common.png", "your_room.png") for j in written[0][1])
               and two_each(written[0][2]) and two_each(os.path.join(out3, "art_3a.json")))
            ring1 = copy.deepcopy(later)
            del ring1["pictures"]["staff_yard"]
            j2 = scene.scene_job(ring1, man, "staff_yard")
            ok("with the garden and the Training Yard chosen the staff steps are made, from both",
               len([i for i in j2["inputs"] if "as chosen" in i[0]]) == 2)
            jm = scene.scene_job(later, man, "area_heart")
            ok("with the gate chosen the Courtyard & Gate map is made: the map text, none of the stage text, and it passes",
               check_prompts.text_of("map.txt") in jm["prompt"] and stage not in jm["prompt"]
               and not any(s in jm["prompt"] for s in check_prompts._sentences(stage))
               and not check_prompts.check(jm["prompt"], later), [jm["prompt"]])

        # every prompt the table's campus pictures can produce, whatever is chosen
        everything = copy.deepcopy(record)
        for key, p in rec.places.items():
            everything["pictures"].setdefault(p["stem"], {"place": key, "rev": 2, "kind": p["how"]})
        bad, relit, redone, composed = [], 0, 0, 0
        k16_places = set()
        for b, f, p in pics:
            try:
                if p["kind"] == "relight":
                    text = redo.prompt_for(record, p["place"], hour=p["hour"], hour_words=p.get("hour_words"))
                    relit += 1
                    if "Keep the time of day" in text:
                        bad.append("%s %s says 'Keep the time of day'" % (p["place"], p["hour"]))
                    if "Through the windows" in text:
                        bad.append("%s %s carries a window line" % (p["place"], p["hour"]))
                elif p["kind"] == "inplace":
                    text = redo.prompt_for(everything, p["place"], add="a thing asked for" if p.get("add") else None)
                    redone += 1
                    if "Keep the time of day and the direction of the light." not in text:
                        bad.append("%s by day does not keep its light" % p["place"])
                elif p["kind"] == "composed":
                    refs = [("neighbour", a) for a in rec.places[p["place"]].get("after", [])]
                    text = scene.prompt_for(everything, p["place"], refs)
                    composed += 1
                    if stage not in text:
                        bad.append("%s has no stage text" % p["place"])
                elif p["kind"] == "map":
                    text = scene.map_prompt_for(everything, p["stem"], [])
                    if any(s in text for s in check_prompts._sentences(stage)):
                        bad.append("%s carries the stage text" % p["stem"])
                else:
                    continue
            except (Refused, SystemExit) as e:
                bad.append("%s: %s" % (p.get("place") or p.get("stem"), e)); continue
            for x in check_prompts.check(text, everything, place=p.get("place")):
                bad.append("%s: %s" % (p.get("place") or p.get("stem"), x))
            if not text.endswith(check_prompts.text_of("look.txt")):
                bad.append("%s does not end with the look" % (p.get("place") or p.get("stem")))
            if check_prompts.k16_place(p.get("place")):       # the words are check_prompts' K16 rule, above
                k16_places.add(p["place"])
                if "No people" not in text:
                    bad.append("%s: the prompt does not say 'No people'" % p["place"])
        ok("all %d relight, %d in-place, %d composed and 7 map prompts pass the prompt check; no relight says 'Keep "
           "the time of day'; no map carries the stage text; nobody is in the baths, the pool or a bedroom"
           % (relit, redone, composed), not bad and (relit, redone, composed) == (64, 16, 17)
           and k16_places == set(["bathhouse", "sauna", "pool", "yuji_room", "megumi_room", "senpai_room",
                                  "nobara_room", "maki_room"]), bad + sorted(k16_places))

        # a yard with no view in the record is refused, not written with no building, door or path in it
        blind = copy.deepcopy(record)
        for st in ("fixed", "proposed"):
            blind[st] = [row for row in blind[st] if not (row.get("kind") == "exit" and row.get("place") == "school_yard")]
        ok("a yard whose view has gone from the record is refused",
           "has no view in the record" in refused(lambda: scene.prompt_for(blind, "school_yard", [])))
        # K16 reaches a maker's prompt through the place it is a picture of
        peopled = copy.deepcopy(record)
        check_campus.Rec(peopled).by_id["place.sauna"]["words"] += ", and a figure on the bench"
        try:
            check_prompts.refuse_if_bad(scene.prompt_for(peopled, "sauna", []), "the Sauna", peopled, "sauna")
            said = ""
        except SystemExit as e:
            said = str(e)
        ok("a prompt that puts somebody in the sauna is refused before a workflow is written", "K16" in said, [said])

        # the marks
        d2 = copy.deepcopy(data)
        d2["done"] = ["3a", "3b", "7a"]
        ok("'3' is done when 3a and 3b are, and '7' is not when only 7a is",
           is_done(d2, "3") and not is_done(d2, "7") and is_done(d2, "7a") and not is_done(d2, "1"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("art_batch selftest: %s%s" % ("PASS" if not fails else "FAIL (%d)" % len(fails),
                                        " (with %d skipped: %s)" % (len(skips), "; ".join(skips)) if skips else ""))
    return 1 if fails else 0


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

    if "--selftest" in argv:
        raise SystemExit(selftest())
    table = opt("--batches")
    data = load(table)
    done, undo = opt("--done"), opt("--undo")
    if done or undo:
        marker = done or undo
        b, files = target(data, marker)
        if marker not in markers(b) and marker != b["id"]:
            raise SystemExit("%s is not a file of batch %s (its files are %s)" % (marker, b["id"], ", ".join(markers(b))))
        if done and marker not in data["done"]:
            data["done"].append(marker)
        if undo and marker in data["done"]:
            data["done"].remove(marker)
        save(data, table)
        print("batches.json: done is now %s" % (", ".join(data["done"]) or "empty"))
        return
    if "--list" in argv:
        listing(data)
        return
    out_dir, again, keep_dir = opt("--out"), int(opt("--again") or 0), opt("--keep")
    record = check_campus.load_record(opt("--record"))
    manifest = check_campus.load_manifest(path=opt("--manifest"))
    dump_path = opt("--layout-dump")
    preview = "--preview" in argv
    if preview:
        argv.remove("--preview")
        if not out_dir or os.path.abspath(out_dir) == os.path.abspath(scene.OUT):
            raise SystemExit("--preview needs --out <a folder of its own>: it never writes into the owner's ui2 folder")
    if len(argv) != 1 or argv[0].startswith("--"):
        print(__doc__); raise SystemExit(1)
    b, files = target(data, argv[0])
    dump = None
    if any(p["kind"] == "map" and p["stem"] == record.get("campus_map", {}).get("stem") for f in files for p in f["pictures"]):
        dump = check_campus.load_dump(dump_path)
    try:
        write_batch(data, argv[0], record, manifest, out_dir, preview, again, keep_dir=keep_dir, dump=dump)
    except Refused as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main(sys.argv[1:])
