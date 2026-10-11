"""
The tests of the art tools. Run it through tools/test_art_tools.sh.

    tools/test_art_tools.sh                        # everything that can run here
    tools/test_art_tools.sh --layout-dump <file>   # in a worktree: the local dump (tools/smoke.sh u2_dump --out <file>)
    tools/test_art_tools.sh --only redo,pose       # some groups: reader layout redo compose pose face set status real yuji
    tools/test_art_tools.sh --strict               # an art sitting: a SKIPPED line is a failure
    tools/test_art_tools.sh --keep-work            # leave the scratch folder, and say where it is
    tools/test_art_tools.sh --write-measures       # rewrite tools/art/redo_measures.json from the real cases (U0d only)

docs/UI2_DESIGN.md 5.4, 6.5, 10.2 (U0d2's acceptance). Nothing here touches
the game: every install goes into a scratch copy of the tree (its .rpy files,
its layout files and its pictures; no .rpyc), and the last check is that no
file under game/ changed.

  SYNTHETIC cases run anywhere the repository is: pictures made from the
  game's own by hand (shifted 12 px, enlarged 2%, recoloured, a thing rubbed
  out, a thing drawn in), test layouts, test pose rows, a doctored layout dump.
  REAL cases run when their files are on the machine, and say so when they
  are not: the sixteen look-test renders in ~/ComfyUI-Shared/output, Yuji's
  two old blink and talk renders, and Yuji's staged set in
  ~/Desktop/JJK Game images/redo_yuji.

A line is PASS, FAIL or SKIPPED. Without ComfyUI's Python (numpy, scipy,
Pillow) the picture tests print "SKIPPED (no ComfyUI python)": a pass for a
code package, a failure for an art sitting (--strict). Exit status 0 when
nothing failed, 1 otherwise, 2 when the layout dump is out of date.
"""
import sys, os, json, subprocess, tempfile, shutil, hashlib, re, time

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import check_campus

OUTPUT = os.path.expanduser("~/ComfyUI-Shared/output")
YUJI = os.path.expanduser("~/Desktop/JJK Game images/redo_yuji")
MEASURES = os.path.join(TOOLS, "art", "redo_measures.json")
STALE = check_campus.STALE
GROUPS = ("reader", "layout", "redo", "compose", "pose", "face", "set", "status", "real", "yuji")

counts = {"PASS": 0, "FAIL": 0, "SKIPPED": 0}
failed = []


def ok(name, cond, detail=None):
    word = "PASS" if cond else "FAIL"
    counts[word] += 1
    print("%s  %s" % (word, name))
    if not cond:
        failed.append(name)
        for line in str(detail or "").strip().splitlines()[-14:]:
            print("        | %s" % line[:240])
    sys.stdout.flush()
    return cond


def skipped(name, why):
    counts["SKIPPED"] += 1
    print("SKIPPED  %s (%s)" % (name, why))
    sys.stdout.flush()


def run(args, py=False, cwd=None):
    """(exit status, output) of a tool. py: start it through tools/py_art.sh."""
    cmd = (["/bin/bash", os.path.join(TOOLS, "py_art.sh")] if py else ["python3"]) + [str(a) for a in args]
    env = dict((k, v) for k, v in os.environ.items() if not k.startswith("PYTHON") and k != "JJK_PY_ART")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd=cwd)
    return p.returncode, p.stdout.decode("utf-8", "replace")


def tool(name):
    return os.path.join(TOOLS, name)


def have_art_python():
    return subprocess.run(["/bin/bash", tool("py_art.sh"), "--where"], stdout=subprocess.PIPE).returncode == 0


def tree_hash(root):
    """One hash over every file under root/game (names and bytes), and tools/fg and tools/bgs."""
    h = hashlib.sha256()
    for base in ("game", os.path.join("tools", "fg"), os.path.join("tools", "bgs")):
        for d, _dirs, names in sorted(os.walk(os.path.join(root, base))):
            for n in sorted(names):
                if n.endswith(".rpyc") or n == ".DS_Store":
                    continue
                p = os.path.join(d, n)
                h.update(os.path.relpath(p, root).encode() + b"\0")
                with open(p, "rb") as f:
                    h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def game_status():
    p = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "game"], stdout=subprocess.PIPE)
    return p.stdout.decode().strip()


def mkroot(path):
    """A scratch copy of the tree: the .rpy files, the layout files, the pictures (cloned, not copied, where the
    disk can), the foreground outlines and the campus record. Never a .rpyc."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(os.path.join(path, "game"))
    os.makedirs(os.path.join(path, "tools", "bgs"))
    for n in sorted(os.listdir(os.path.join(REPO, "game"))):
        if n.endswith(".rpy"):
            shutil.copyfile(os.path.join(REPO, "game", n), os.path.join(path, "game", n))
    for sub in ("layout", "images"):
        src, dst = os.path.join(REPO, "game", sub), os.path.join(path, "game", sub)
        if subprocess.run(["cp", "-cR", src, dst], stderr=subprocess.PIPE).returncode != 0:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    shutil.copytree(os.path.join(REPO, "tools", "fg"), os.path.join(path, "tools", "fg"))
    shutil.copyfile(os.path.join(REPO, "tools", "bgs", "campus.json"), os.path.join(path, "tools", "bgs", "campus.json"))
    return path


def stamp(dump_path, root, out=None, extra=None):
    """TEST ONLY: a copy of the dump whose hash is taken again over `root`, with test keys laid in. In the
    tests the points have not changed (an install wrote a light row or the manifest); in real use the dump is
    written again by the game (tools/smoke.sh u2_dump), never restamped."""
    d = json.load(open(dump_path, encoding="utf-8"))
    extra = dict(extra or {})
    if isinstance(extra.get("world"), dict):
        # a test's world tables are laid over the dump's own, table by table; the rest of `world` stays
        extra["world"] = dict(d.get("world") or {}, **extra["world"])
    drop = extra.pop("__drop__", ())
    d.update(extra)
    for key in drop:
        d.pop(key, None)
    d["files"] = check_campus.dump_files(root)
    d["hash"] = check_campus.dump_hash(d["files"], root)
    out = out or os.path.join(root, "dump.json")
    json.dump(d, open(out, "w"))
    return out


# ---- pictures made by hand (ComfyUI's Python) --------------------------------------------------------------
SYN = r'''
import sys, numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
cmd, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
args = sys.argv[4:]
a = Image.open(src).convert("RGB"); W, H = a.size
box = [int(v) for v in args[0].split(",")] if args and "," in args[0] else None
def look(im):          # a stand-in for the new look: the same drawing, much sharper
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=260, threshold=0))
if cmd == "look":
    out = look(a)
elif cmd == "shift12":
    out = Image.new("RGB", (W, H)); out.paste(look(a), (12, 0)); out.paste(look(a).crop((0, 0, 12, H)), (0, 0))
elif cmd == "zoom2":
    z = look(a).resize((int(W * 1.02), int(H * 1.02)), Image.LANCZOS)
    out = z.crop(((z.width - W) // 2, (z.height - H) // 2, (z.width - W) // 2 + W, (z.height - H) // 2 + H))
elif cmd == "recolour":
    out = Image.eval(ImageEnhance.Color(look(a)).enhance(1.35), lambda v: min(255, int(v * 0.92 + 14)))
elif cmd == "plainrecolour":
    out = Image.eval(ImageEnhance.Color(a).enhance(1.35), lambda v: min(255, int(v * 0.92 + 14)))
elif cmd == "erase":   # a thing rubbed out: its box smeared flat
    out = look(a); x, y, w, h = box
    out.paste(a.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(28)), (x, y))
elif cmd == "add":     # a thing drawn in: a striped cloth with a dark outline, as a jacket is
    out = look(a); x, y, w, h = box; d = ImageDraw.Draw(out)
    d.rectangle([x + 6, y + 4, x + w - 6, y + h - 4], fill=(46, 54, 52), outline=(8, 8, 10), width=3)
    for k in range(x + 12, x + w - 12, 9):
        d.line([k, y + 7, k + 9, y + h - 7], fill=(168, 176, 160), width=2)
elif cmd == "bars":
    out = look(a); d = ImageDraw.Draw(out); d.rectangle([0, 0, W, 60], fill=(0, 0, 0)); d.rectangle([0, H - 60, W, H], fill=(0, 0, 0))
elif cmd == "static":
    out = Image.fromarray(np.random.RandomState(7).randint(0, 255, (H, W, 3)).astype("uint8"), "RGB")
elif cmd == "night":   # a relight by hand: the same drawing, dark and blue
    n = np.asarray(a).astype(float) * np.array([0.42, 0.50, 0.78]) + np.array([4, 8, 26])
    out = Image.fromarray(np.clip(n, 0, 255).astype("uint8"), "RGB")
elif cmd == "nightshift":
    n = np.asarray(a).astype(float) * np.array([0.42, 0.50, 0.78]) + np.array([4, 8, 26])
    n = Image.fromarray(np.clip(n, 0, 255).astype("uint8"), "RGB")
    out = Image.new("RGB", (W, H)); out.paste(n, (9, 0)); out.paste(n.crop((0, 0, 9, H)), (0, 0))
elif cmd == "slide":   # a box and what is round it, moved 10 px right (or by the number given)
    out = look(a); x, y, w, h = box
    d = int(args[1]) if len(args) > 1 else 10
    out.paste(look(a).crop((x - 24 - d, y - 24, x + w + 24 - d, y + h + 24)), (x - 24, y - 24))
elif cmd == "patch":   # a pose render: a flat person-sized patch on the room
    out = a.copy(); x, y, w, h = box
    col = tuple(int(v) for v in args[1].split(",")) if len(args) > 1 else (230, 40, 60)
    ImageDraw.Draw(out).rectangle([x, y, x + w - 1, y + h - 1], fill=col)
elif cmd in ("paste", "pasteplain"):   # a thing of the picture's own, set down somewhere else (1920-wide numbers)
    out = look(a) if cmd == "paste" else a.copy(); k = W / 1920.0
    x, y, w, h = [int(v * k) for v in box]; px, py = [int(int(v) * k) for v in args[1].split(",")]
    out.paste(out.crop((x, y, x + w, y + h)), (px, py))
elif cmd == "sign":    # a thing drawn on a wall or a window: a yellow board with a black rim
    out = look(a); x, y, w, h = box; d = ImageDraw.Draw(out)
    d.rectangle([x, y, x + w, y + h], fill=(240, 205, 40), outline=(10, 10, 10), width=5)
    d.line([x + 12, y + h // 2, x + w - 12, y + h // 2], fill=(10, 10, 10), width=5)
elif cmd in ("cup", "plaincup"):   # a red-and-white cup with a dark rim, set down (its box in 1920-wide numbers)
    out = look(a) if cmd == "cup" else a.copy(); k = W / 1920.0
    x, y, w, h = [int(v * k) for v in box]; d = ImageDraw.Draw(out); t = max(2, int(3 * k))
    d.rectangle([x, y, x + w, y + h], fill=(236, 232, 226), outline=(30, 24, 24), width=t)
    d.rectangle([x + t, y + h // 3, x + w - t, y + 2 * h // 3], fill=(200, 40, 44))
    d.ellipse([x + t, y - 2 * t, x + w - t, y + 3 * t], fill=(60, 40, 36), outline=(30, 24, 24))
elif cmd == "copy":
    out = a
out.save(dst)
'''


class Lab(object):
    def __init__(self, work, dump, art):
        self.work, self.dump, self.art = work, dump, art
        self.syn_py = os.path.join(work, "syn.py")
        open(self.syn_py, "w").write(SYN)

    def syn(self, cmd, src, name, *args):
        dst = os.path.join(self.work, name)
        rc, out = run([self.syn_py, cmd, src, dst] + list(args), py=True)
        if rc != 0:
            raise SystemExit("could not make the test picture %s:\n%s" % (name, out))
        return dst


# ---- the groups ---------------------------------------------------------------------------------------------
def group_reader(lab):
    """Every tool refuses, in one line, a dump whose hash is out of date, and reads --layout-dump."""
    root = mkroot(os.path.join(lab.work, "r_reader"))
    good = stamp(lab.dump, root)
    rc, out = run([tool("make_pose_workflow.py"), "--batch", "5", "--print", "--root", root, "--layout-dump", good])
    ok("the reader: a dump that matches the tree is read (make_pose_workflow.py --layout-dump)", STALE not in out, out)
    cases = (("a changed .rpy file", os.path.join(root, "game", "sb_world.rpy")),
             ("a changed game/layout/*.json", os.path.join(root, "game", "layout", "hot_dorm.json")))
    tools = [("make_pose_workflow.py", ["--batch", "5", "--print", "--root", root, "--layout-dump", good], False),
             ("install_pose.py", [os.path.join(root, "nothing.png"), "--name", "pose_dorm_common__yuji", "--root", root,
                                  "--layout-dump", good], False),
             ("art tools' reader (game_layout.load)", None, False),
             ("install_redo.py", ["dorm_common", os.path.join(root, "game", "images", "bg", "dorm_common.png"), "--dry",
                                  "--root", root, "--layout-dump", good], True),
             ("sample_light.py", ["dorm_common", "--root", root, "--layout-dump", good], True)]
    open(os.path.join(root, "nothing.png"), "wb").write(open(os.path.join(root, "game", "images", "bg", "black.png"), "rb").read())
    for what, path in cases:
        before = open(path, "rb").read()
        open(path, "ab").write(b"\n")
        for name, args, py in tools:
            if py and not lab.art:
                skipped("%s refuses the dump after %s" % (name, what), "no ComfyUI python")
                continue
            if args is None:
                rc, out = run(["-c", "import sys; sys.path.insert(0, %r); import game_layout; game_layout.load(%r, %r)"
                               % (TOOLS, good, root)])
            else:
                rc, out = run([tool(name)] + args, py=py)
            ok("%s refuses, in one line, a dump that is out of date (%s)" % (name, what),
               rc == 2 and out.strip() == STALE, "exit %s\n%s" % (rc, out))
        open(path, "wb").write(before)
    # make_fg.py reads the tree it lives in: its refusal is proved on a dump whose hash is wrong for this tree
    bad = os.path.join(lab.work, "bad_dump.json")
    d = json.load(open(lab.dump)); d["hash"] = "0" * 64; json.dump(d, open(bad, "w"))
    rc, out = run([tool("make_fg.py"), "dorm_common", "--dry", "--layout-dump", bad], cwd=lab.work)
    ok("make_fg.py refuses, in one line, a dump that is out of date", rc == 2 and out.strip() == STALE, out)
    rc, out = run([tool("make_fg.py"), "dorm_common", "--layout-dump", bad[:-5] + "_missing.json"], cwd=lab.work)
    ok("and says so when the file --layout-dump names is not there", rc != 0 and "no layout dump at" in out, out)


def group_layout(lab):
    """The layout tools (docs/UI2_DESIGN.md 10.2, U0d3): game_layout.py's readers, check_layout.py's negative
    tests, layout_sheet.py. Plain Python: nothing here needs ComfyUI's."""
    import game_layout
    lay = game_layout.load(lab.dump)
    committed = os.path.abspath(lab.dump) == os.path.abspath(check_campus.DUMP)
    cells = (lay.where("megumi", "Mon", "Night"), lay.asleep("megumi", "Mon", "Night"), lay.asleep("megumi", "Sat", "Night"),
             lay.asleep("megumi", "Mon", "Evening"), lay.away("nobara", "Sun", "Afternoon"), lay.away("nobara", "Sat", "Afternoon"),
             lay.where("yuji", "Sun", "Afternoon"), lay.districts(), lay.homes().get("panda"))
    ok("game_layout.py: where(), asleep() and away() each answer a known cell from the %s dump (world.homes, "
       "world.asleep, world.away): Megumi is in his room and asleep on a Monday Night and not on a Saturday's; Nobara "
       "is in Harajuku on Sunday afternoon and nowhere on Saturday's; Yuji's Sunday afternoon is Shibuya"
       % ("committed" if committed else "local"),
       cells == ("megumi_room", True, False, False, "harajuku", "", "shibuya", ["harajuku", "shibuya"], "senpai_room"), cells)
    rc, out = run([tool("game_layout.py"), "--layout-dump", lab.dump])
    ok("python3 tools/game_layout.py finds all three tables in the dump (no \"NOT in the dump\" line)",
       rc == 0 and "NOT in the dump" not in out and out.count("in the dump,") == 3, out)
    old = game_layout.Layout(dict(lay.d, world_asleep={"weekday": ["megumi"]}, world_away={}, world=None))
    ok("a dump with no `world` answers None (\"not known\") from asleep(), away() and districts(), whatever "
       "top-level keys of the old names it holds",
       (old.asleep("megumi", "Mon", "Night"), old.away("nobara", "Sun", "Afternoon"), old.districts()) == (None, None, None))
    test = game_layout.Layout(dict(lay.d, shapes={"courtyard": {"spot_vend": [[[1560, 640], [1640, 640], [1640, 740], [1560, 740]]]}},
                                   keep_tile={"courtyard": {"gateway": "a test"}}, shaped=["courtyard"]))
    got = test.shapes("courtyard")
    got["spot_vend"][0][0][0] = -1
    ok("game_layout.py: shapes(place) gives a place's shapes as its sidecar holds them, a fresh copy each call, and "
       "{} for a place with none; keep_tile(), shaped() and front_ids() beside it (the vending machine is the "
       "Courtyard's one front id today)",
       test.shapes("courtyard") == {"spot_vend": [[[1560, 640], [1640, 640], [1640, 740], [1560, 740]]]}
       and test.shapes("library") == {} and lay.shapes("courtyard") == dict(lay.d.get("shapes", {}).get("courtyard", {}))
       and test.keep_tile("courtyard") == {"gateway": "a test"} and test.shaped("courtyard") and not test.shaped("gate")
       and lay.front_ids("courtyard") == set(["spot_vend"]) and lay.front_ids("library") == set(),
       (test.shapes("courtyard"), lay.front_ids("courtyard")))


def verdicts(out):
    """{version letter: (verdict, the lines under it)} from install_redo.py's report."""
    got, letter = {}, None
    for line in out.splitlines():
        m = re.match(r"^version ([ab])\b", line)
        if m:
            letter = m.group(1)
            got[letter] = ["?", []]
        m = re.match(r"^\s+VERDICT\s+(PASS|LOOK|REFUSED)", line)
        if m and letter:
            got[letter][0] = m.group(1)
        elif letter and line.startswith("            "):
            got[letter][1].append(line.strip())
    return dict((k, (v[0], " | ".join(v[1]))) for k, v in got.items())


def group_redo(lab):
    """install_redo.py in place, on pictures whose answers are known because they were made by hand."""
    if not lab.art:
        skipped("install_redo.py, the synthetic cases", "no ComfyUI python")
        return
    root = mkroot(os.path.join(lab.work, "r_redo"))
    dump = stamp(lab.dump, root)
    room = os.path.join(root, "game", "images", "bg", "dorm_common.png")
    redo = [tool("install_redo.py"), "dorm_common"]
    tail = ["--root", root, "--layout-dump", dump]
    good = lab.syn("look", room, "syn_look_a_00001_.png")
    made = {}
    for name, cmd, arg in (("shift12", "shift12", None), ("zoom2", "zoom2", None), ("recolour", "recolour", None),
                           ("plainrecolour", "plainrecolour", None), ("bars", "bars", None), ("static", "static", None),
                           ("erased", "erase", "1140,815,320,105"), ("added", "add", "570,718,160,52")):
        made[name] = lab.syn(cmd, room, "syn_%s_b_00001_.png" % name, *([arg] if arg else []))

    def one(path, extra=()):
        rc, out = run(redo + [path, "--dry"] + tail + list(extra), py=True)
        v = verdicts(out)
        return rc, out, list(v.values())[0] if v else ("?", "")

    rc, out, v = one(good)
    ok("in place: the same drawing, sharper, is a PASS", v[0] == "PASS" and rc == 0, out)
    rc, out, v = one(made["shift12"])
    ok("a picture shifted 12 px by hand is REFUSED as moved, and the tool says by how much",
       v[0] == "REFUSED" and "the whole picture moved 12 px right" in v[1], out)
    rc, out, v = one(made["zoom2"])
    ok("a picture enlarged 2% by hand is REFUSED as moved", v[0] == "REFUSED" and "moved" in v[1] and rc == 1, out)
    rc, out, v = one(made["recolour"])
    ok("a picture that is only recoloured (and sharper) is not refused", v[0] in ("PASS", "LOOK"), out)
    rc, out, v = one(made["plainrecolour"])
    ok("recoloured and no sharper: nothing moved, vanished or appeared; refused only for not being sharper",
       v[0] == "REFUSED" and "moved" not in v[1] and "gone" not in v[1] and "something new" not in v[1]
       and "not sharper" in v[1], out)
    rc, out, v = one(made["bars"])
    ok("letterbox bars are refused at the fit", v[0] == "REFUSED" and "bars" in v[1], out)
    rc, out, v = one(made["static"])
    ok("static is refused at the fit", v[0] == "REFUSED" and "static" in v[1], out)
    rc, out, v = one(made["erased"])
    ok("a thing rubbed out is REFUSED and named: \"the floor cushions by the low table are gone\"",
       v[0] == "REFUSED" and "the floor cushions by the low table are gone" in v[1], out)
    rc, out, v = one(made["added"])
    ok("a thing drawn in is REFUSED and its place named: \"something new is on the sofa seat\"",
       v[0] == "REFUSED" and "something new is on the sofa seat" in v[1], out)

    # one thing set down on the wide floor (5.4 step 4: "across the whole floor polygon ... a cup, a jacket").
    # The floor is 1590 px wide: judged whole, one cushion is lost in its mean, so it is judged in parts too.
    for what, cmd, a1, a2 in (("the sofa's cushion", "paste", "497,618,145,104", "700,966"),
                              ("the kettle", "paste", "1285,483,65,72", "1010,998"),
                              ("the green bag", "paste", "1125,640,100,165", "1380,960"),
                              ("a striped bag drawn in", "add", "1300,975,120,80", None)):
        path = lab.syn(cmd, room, "syn_floor_%s_a_00001_.png" % re.sub(r"\W+", "_", what), a1, *([a2] if a2 else []))
        rc, out, v = one(path)
        ok("%s set down on the bare floor is REFUSED: \"something new is on the floor\", and the part of the floor is named" % what,
           v[0] == "REFUSED" and rc == 1 and re.search(r"something new is on the floor \((at its left end|in its middle|at its right end), from x \d+ to \d+\)", v[1]) is not None
           and "gone" not in v[1], out)
    # the rug in front of the low table is no part of the floor polygon: it has an empty row of its own
    rc, out, v = one(lab.syn("cup", room, "syn_rugcup_a_00001_.png", "932,865,56,70"))
    ok("a cup set down on the rug in front of the low table is REFUSED: \"something new is on the rug in front of the low table\"",
       v[0] == "REFUSED" and rc == 1 and "something new is on the rug in front of the low table" in v[1] and "gone" not in v[1], out)
    # two renders whose names carry the same letter (the same seed file run twice) keep a verdict each
    rc, out = run(redo + [good, lab.syn("slide", room, "syn_twice_a_00002_.png", "60,200,130,700", "30"), "--dry"] + tail, py=True)
    v2 = verdicts(out)
    ok("two renders named with the same letter are versions a and b, each with its own verdict; the good one can still be chosen",
       rc == 0 and v2.get("a", ("",))[0] == "PASS" and v2.get("b", ("",))[0] == "REFUSED"
       and len(re.findall(r"(?m)^version ", out)) == 2, out)
    # step 6: what else changed is shown, not refused
    rc, out, v = one(lab.syn("sign", room, "syn_sign_a_00001_.png", "900,330,140,140"))
    ok("a board painted over the window (outside every keep box and empty place) is a LOOK, and its place is told",
       v[0] == "LOOK" and rc == 0 and re.search(r"the part of the picture at \(\d+, \d+\) is drawn differently", v[1]) is not None, out)

    # the door an exit sits on (5.4 step 2: "the door my room's exit sits on moved"). The Common Room's way to
    # the garden is at (84, 540), on the sliding door at the left.
    spot = "the spot the way to Dormitory Garden sits on"
    door = "the sliding glass door on the left"
    rc, out, v = one(lab.syn("slide", room, "syn_door12_a_00001_.png", "60,200,130,700", "12"))
    ok("the door an exit sits on, slid 12 px, is REFUSED and the tool says by how much",
       v[0] == "REFUSED" and rc == 1 and re.search(r"%s moved 1[0-4] px right" % spot, v[1]) is not None, out)
    rc, out, v = one(lab.syn("slide", room, "syn_door30_a_00001_.png", "60,200,130,700", "30"))
    ok("slid 30 px, further than a shift is looked for, it is still REFUSED: the spot no longer lines up",
       v[0] == "REFUSED" and rc == 1 and "%s no longer lines up with the picture in the game" % spot in v[1], out)
    rc, out, v = one(lab.syn("erase", room, "syn_doorgone_a_00001_.png", "10,150,170,800"))
    ok("and painted out, it is REFUSED: the spot no longer lines up, and the door is named as gone",
       v[0] == "REFUSED" and rc == 1 and "%s no longer lines up" % spot in v[1] and re.search(r"%s[^|]* is gone" % door, v[1]) is not None, out)
    nodoors = os.path.join(lab.work, "keep_nodoors")
    os.makedirs(nodoors, exist_ok=True)
    kl = json.load(open(os.path.join(TOOLS, "bgs", "keep", "dorm_common.json")))
    kl.pop("doors")
    json.dump(kl, open(os.path.join(nodoors, "dorm_common.json"), "w"))
    rc, out, v = one(os.path.join(lab.work, "syn_doorgone_a_00001_.png"), ["--keep", nodoors])
    ok("with no `doors` row in the keep list the painted-out door is still REFUSED, by the spot alone",
       v[0] == "REFUSED" and "%s no longer lines up" % spot in v[1] and "is gone" not in v[1], out)
    rc, out, v = one(lab.syn("slide", room, "syn_tv12_a_00001_.png", "1497,380,190,322", "12"))
    ok("a kept thing slid 12 px inside its box is reported as moved, not as gone",
       v[0] == "REFUSED" and re.search(r"the television moved 1[0-4] px right", v[1]) is not None
       and "the television is gone" not in v[1], out)

    # a `change` box: left out of steps 3 and 4; its outline must not move
    keep = os.path.join(lab.work, "keep_change")
    os.makedirs(keep, exist_ok=True)
    kl = json.load(open(os.path.join(TOOLS, "bgs", "keep", "dorm_common.json")))
    shelf = "520,450,215,215"
    flat = lab.syn("erase", room, "syn_shelfgone_a_00001_.png", shelf)
    slid = lab.syn("slide", room, "syn_slid_b_00001_.png", shelf)
    rc, out, v = one(flat)
    ok("without a `change` row, a bookshelf rubbed out is REFUSED (\"the manga on the bookshelf is gone\")",
       v[0] == "REFUSED" and "the manga on the bookshelf is gone" in v[1], out)
    kl["change"] = [{"name": "the bookshelf", "box": [int(x) for x in shelf.split(",")]}]
    json.dump(kl, open(os.path.join(keep, "dorm_common.json"), "w"))
    rc, out, v = one(flat, ["--keep", keep])
    ok("with the bookshelf in a `change` box, the same picture is not refused: the box is left out of "
       "\"nothing vanished\" and \"nothing was added\", and its outline has not moved",
       v[0] in ("PASS", "LOOK") and "gone" not in v[1] and "its outline is" in out, out)
    rc, out, v = one(slid, ["--keep", keep])
    ok("and a bookshelf that has MOVED inside its `change` box is REFUSED: its outline is held",
       v[0] == "REFUSED" and re.search(r"the outline of the bookshelf moved \d+ px right", v[1]) is not None, out)

    # two versions: a verdict for each; only the one the owner names goes in
    before = tree_hash(root)
    rc, out = run(redo + [good, made["erased"], "--dry"] + tail, py=True)
    v = verdicts(out)
    ok("given two versions it reports a verdict for each (a: PASS, b: REFUSED)",
       v.get("a", ("",))[0] == "PASS" and v.get("b", ("",))[0] == "REFUSED", out)
    ok("--dry writes nothing but the previews", tree_hash(root) == before
       and os.path.exists(os.path.join(root, "shots", "art", "redo_dorm_common_a.jpg")), out)
    rc, out = run(redo + [good, made["erased"]] + tail, py=True)
    ok("with no --choose nothing is installed, and it says how to choose", tree_hash(root) == before and "--choose a" in out, out)
    rc, out = run(redo + [good, made["erased"], "--choose", "b"] + tail, py=True)
    ok("the refused version cannot be chosen, and nothing is written", rc != 0 and "cannot be chosen" in out
       and tree_hash(root) == before, out)
    rc, out = run(redo + [good, "--choose", "a", "--batch", "three"] + tail, py=True)
    ok("--batch three is refused in one line and nothing is written", rc != 0 and out.strip().startswith("--batch three: a batch is")
       and len(out.strip().splitlines()) == 1 and tree_hash(root) == before, out)
    rc, out = run(redo + [good, made["erased"], "--choose", "a", "--batch", "3", "--date", "2026-10-07"] + tail, py=True)
    man = check_campus.load_manifest(root)["pictures"]
    row = man.get("dorm_common", {})
    ok("the version the owner names is installed: the picture, and a manifest row at revision 2 whose batch is the "
       "number 3, as the plan's manifest has it (not the text \"3\")",
       rc == 0 and row.get("rev") == 2 and row.get("batch") == 3 and isinstance(row.get("batch"), int) and row.get("kind") == "inplace" and row.get("render") == os.path.basename(good)
       and tree_hash(root) != before, out + json.dumps(row))
    ok("the row records rev1_commit and from_commit (the commit that holds the picture it replaced), the shift and "
       "the sharpness against revision 1",
       re.match(r"^[0-9a-f]{40}$", row.get("rev1_commit", "")) is not None and row.get("from_commit") == row.get("rev1_commit")
       and row.get("shift") == [0, 0] and len(row.get("sharp", [])) == 2 and row["sharp"][1] >= 2 * row["sharp"][0], json.dumps(row))
    light = os.path.join(root, "game", "layout", "light_dorm_common.json")
    ok("it writes light_<place>.json, a measured row, and the foreground cut again with its row",
       os.path.exists(light) and len(json.load(open(light))[""]) == 6 and man.get("fg_dorm_common") == {"of": "dorm_common", "of_rev": 2}
       and man.get("light_dorm_common") == {"of": "dorm_common", "of_rev": 2}, out)
    ok("no foreground file was deleted, and the room's hot_ and view_ files are byte for byte what they were",
       sorted(os.listdir(os.path.join(root, "game", "images", "fg"))) == sorted(os.listdir(os.path.join(REPO, "game", "images", "fg")))
       and all(open(os.path.join(root, "game", "layout", n), "rb").read() == open(os.path.join(REPO, "game", "layout", n), "rb").read()
               for n in ("hot_dorm_common.json", "view_dorm_common.json")))
    ok("the approved render is kept (in a scratch copy: beside it)", os.path.exists(os.path.join(root, "approved", os.path.basename(good))))
    rec = json.load(open(os.path.join(root, "tools", "bgs", "campus.json")))
    ok("the campus record has the picture as chosen at that revision", rec["pictures"]["dorm_common"]["rev"] == 2
       and rec["pictures"]["dorm_common"]["render"] == os.path.basename(good))
    rc, out = run([tool("check_content.py"), "--layout-files", "--layout-dir", os.path.join(root, "game", "layout")])
    ok("what it wrote passes check_content.py --layout-files", rc == 0, out)
    rc, out = run(redo + [good, "--dry"] + tail, py=True)
    ok("after the install the old dump is refused (the hash covers game/layout/)", rc == 2 and out.strip() == STALE, out)
    dump = stamp(lab.dump, root)
    tail = ["--root", root, "--layout-dump", dump]

    # sharpness is against revision 1: the installed render offered again
    rc, out = run(redo + [good, "--dry"] + tail, py=True)
    m = re.search(r"sharper\s+([\d.]+) times", out)
    ok("sharpness is against revision 1: with a render installed and the same render offered again, step 5 "
       "passes (it reads %s times, not 1.0)" % (m.group(1) if m else "?"),
       verdicts(out).get("a", ("",))[0] == "PASS" and m is not None and float(m.group(1)) >= 2.0 and "git, commit" not in out.split("version")[0], out)
    before = tree_hash(root)
    rc, out = run(redo + [good, "--dry", "--against-rev1"] + tail, py=True)
    ok("--dry --against-rev1 measures against the place's picture from git, prints its figures and installs nothing",
       rc == 0 and "before the overhaul (git, commit" in out and '"sharp"' in out and tree_hash(root) == before, out)
    rc, out = run([tool("sample_light.py"), "--check"] + tail, py=True)
    ok("sample_light.py --check passes on the row the installer wrote", rc == 0 and "PASS" in out, out)
    data = json.load(open(light)); data[""][1] = -0.14; data[""][0] = "#8090ff"; json.dump(data, open(light, "w"))
    dump = stamp(lab.dump, root)
    tail = ["--root", root, "--layout-dump", dump]
    rc, out = run([tool("sample_light.py"), "--check"] + tail, py=True)
    ok("and fails a hand-edited row that has drifted from the picture", rc == 1 and "FAIL" in out, out)

    # a relight
    night = lab.syn("night", os.path.join(root, "game", "images", "bg", "dorm_common.png"), "syn_night_a_00001_.png")
    moved = lab.syn("nightshift", os.path.join(root, "game", "images", "bg", "dorm_common.png"), "syn_nightshift_b_00001_.png")
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "night", night, moved, "--dry"] + tail, py=True)
    v = verdicts(out)
    ok("a relight: the same drawing made dark and blue is not refused, though it is no sharper; the one shifted 9 px is",
       v.get("a", ("",))[0] in ("PASS", "LOOK") and v.get("b", ("",))[0] == "REFUSED" and "moved" in v["b"][1]
       and "sharper" not in out, out)
    polys = os.path.join(root, "tools", "fg", "dorm_common.json")
    data = json.load(open(polys)); data.pop("night"); json.dump(data, open(polys, "w"))
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "night", night, moved, "--choose", "a"] + tail, py=True)
    man = check_campus.load_manifest(root)["pictures"]
    row = man.get("dorm_common_night", {})
    ok("the chosen relight is installed with its row (of the day picture, at its revision), its light row, and its "
       "foreground cut from the day outline copied to that hour",
       rc == 0 and row.get("kind") == "relight" and row.get("of") == "dorm_common" and row.get("of_rev") == 2 and row.get("rev") == 2
       and "night" in json.load(open(polys)) and man.get("fg_dorm_common_night") == {"of": "dorm_common_night", "of_rev": 2}
       and "night" in json.load(open(light)), out + json.dumps(row))
    root2 = mkroot(os.path.join(lab.work, "r_redo2"))
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "night", night, "--choose", "a", "--root", root2,
                   "--layout-dump", stamp(lab.dump, root2)], py=True)
    ok("a relight is not installed before its day picture is in the new look (K8)", rc != 0 and "not installed in the new look" in out, out)
    return root


def test_layout(place, swap=None):
    """The record's own test layout for a place (tools/bgs/tests/good/, which tools/check_campus.py checks on
    every run), with two exits swapped when asked: {"spots": {go_<place>__<to>: [x, y]}}."""
    data = json.load(open(os.path.join(TOOLS, "bgs", "tests", "good", "hot_%s.json" % place), encoding="utf-8"))
    spots = dict(data["spots"])
    if swap:
        a, b = ["go_%s__%s" % (place, to) for to in swap]
        spots[a], spots[b] = spots[b], spots[a]
    return {"spots": spots}


def group_compose(lab):
    """install_redo.py --compose: the facts a layout fixes, the record's hash, a contradiction, a waiver."""
    if not lab.art:
        skipped("install_redo.py --compose", "no ComfyUI python")
        return
    root = mkroot(os.path.join(lab.work, "r_compose"))
    dump = stamp(lab.dump, root)
    place = "training_yard"
    rpath = os.path.join(root, "tools", "bgs", "campus.json")
    record = json.load(open(rpath))
    rec = check_campus.Rec(record)
    ok("fixture: the Training Yard is a proposal with exits to compose, one of them a fact the Courtyard fixed",
       rec.chosen(place) is None and rec.is_fixed(rec.by_id["exit.training_yard.training"])
       and any(not rec.is_fixed(r) for r in rec.rows("exit", place=place)))
    render = lab.syn("look", os.path.join(root, "game", "images", "bg", "training_yard.png"), "ui2_training_yard_a_00001_.png")
    lay_dir = os.path.join(lab.work, "lay1"); os.makedirs(lay_dir, exist_ok=True)
    hot = os.path.join(lay_dir, "hot_training_yard.json")
    json.dump(test_layout(place), open(hot, "w"))
    comp = [tool("install_redo.py"), "--compose", place, render, "--root", root, "--layout-dump", dump, "--date", "2026-10-07"]
    before = tree_hash(root)
    rc, out = run(comp + ["--dry"], py=True)
    ok("--compose --dry with no layout draws the OLD layout on the new picture and writes nothing else",
       rc == 0 and "OLD layout" in out and os.path.exists(os.path.join(root, "shots", "art", "redo_training_yard.jpg"))
       and tree_hash(root) == before, out)
    rc, out = run(comp, py=True)
    ok("a composed picture is not installed without its layout", rc != 0 and "only together with its layout" in out
       and tree_hash(root) == before, out)
    refs = os.path.join(lay_dir, "refs.json")
    json.dump({"storehouse": [800, 300, 300, 300]}, open(refs, "w"))
    rc, out = run(comp + ["--layout", hot, "--refs", refs, "--batch", "1"], py=True)
    after = json.load(open(rpath))
    arec = check_campus.Rec(after)
    newly = [r["id"] for r in arec.rows("exit", place=place) if arec.is_fixed(r) and not rec.is_fixed(rec.by_id[r["id"]])]
    man = check_campus.load_manifest(root)["pictures"].get("training_yard", {})
    ok("with a test picture and layout, --compose adds its fixed rows to a copy of the record (%d exits, the place "
       "and its ground)" % len(newly), rc == 0 and len(newly) >= 3 and arec.is_fixed(arec.places[place])
       and after["pictures"]["training_yard"]["rev"] == 2
       and all(arec.by_id[i]["by"] == {"picture": "training_yard", "rev": 2} for i in newly), out)
    ok("and stamps the manifest row with the record's hash, as the record stands after the install",
       man.get("kind") == "composed" and man.get("rev") == 2 and man.get("record") == hashlib.sha256(open(rpath, "rb").read()).hexdigest(),
       json.dumps(man))
    side = json.load(open(os.path.join(root, "game", "layout", "hot_training_yard.json")))
    ok("the layout file is installed with for_rev set, and a reference crop of the building it shows is cut",
       side.get("for_rev") == 2 and side["spots"] == json.load(open(hot))["spots"]
       and os.path.exists(os.path.join(root, "tools", "bgs", "refs", "storehouse.png")), json.dumps(side)[:300])
    ok("a building the picture shows becomes a fixed fact of the record", arec.is_fixed(arec.buildings["storehouse"]))

    def redump(hot_file):
        """TEST ONLY: the dump as the game would write it again after the install (the yard's exits at the
        layout's points)."""
        d = json.load(open(lab.dump))
        spots = json.load(open(hot_file))["spots"]
        for e in d["exits"][place]:
            if e["id"] in spots:
                e["applied"] = spots[e["id"]]
        return stamp(lab.dump, root, extra={"exits": d["exits"]})

    rc, out = run([tool("check_campus.py"), "--record", rpath, "--layout-dump", redump(hot), "--no-hash", "--manifest",
                   os.path.join(root, "game", "layout", "pictures.json"), "--quiet"])
    ok("the record still passes tools/check_campus.py in full afterwards", rc == 0 and "check_campus: PASS" in out,
       "\n".join(l for l in out.splitlines() if not l.startswith("WAIT")))
    rc, out = run([tool("check_content.py"), "--layout-files", "--layout-dir", os.path.join(root, "game", "layout")])
    ok("what --compose wrote passes check_content.py --layout-files", rc == 0, out)
    rc, out = run([tool("art_status.py"), "--root", root])
    ok("art_status.py lists the picture as in the new look", "training_yard" in out.split("HALF-MADE")[0], out)

    # a second layout that contradicts a fact the first one fixed
    dump = redump(hot)
    comp = [tool("install_redo.py"), "--compose", place, render, "--root", root, "--layout-dump", dump, "--date", "2026-10-08"]
    fixed_exits = [r for r in arec.rows("exit", place=place) if r["side"] in ("left", "right") and r["id"] in newly]
    left = [r for r in arec.rows("exit", place=place) if r["side"] == "left"][0]
    right = [r for r in fixed_exits if r["side"] == "right"][0]
    lay2 = os.path.join(lab.work, "lay2"); os.makedirs(lay2, exist_ok=True)
    hot2 = os.path.join(lay2, "hot_training_yard.json")
    json.dump(test_layout(place, swap=(left["to"], right["to"])), open(hot2, "w"))
    before = tree_hash(root)
    rc, out = run(comp + ["--layout", hot2], py=True)
    ok("a second test layout that contradicts one of them is REFUSED with the fact named (%s), in plain words, and "
       "nothing is written" % right["id"],
       rc == 1 and "REFUSED" in out and "against the fixed fact %s" % right["id"] in out and tree_hash(root) == before
       and "--waive" in out, out)
    rc, out = run(comp + ["--layout", hot2, "--waive", right["id"]], py=True)
    ok("--waive is refused without the owner's own word", rc != 0 and "without the owner's own word" in out
       and tree_hash(root) == before, out)
    rc, out = run(comp + ["--layout", hot2, "--waive", right["id"], "--owner-said", "test: I accept it"], py=True)
    ok("--waive that names only ONE of the facts it stands against is still refused, and the other is named",
       rc == 1 and "against the fixed fact %s" % left["id"] in out and tree_hash(root) == before, out)
    rc, out = run(comp + ["--layout", hot2, "--waive", right["id"], "--waive", left["id"], "--owner-said",
                          "test: I accept it"], py=True)
    final = json.load(open(rpath))
    frec = check_campus.Rec(final)
    waived = sorted(w["fact"] for w in final.get("waived", []))
    ok("and it is installed, with a `waived` row for each, only when --waive names every such fact",
       rc == 0 and waived == sorted([left["id"], right["id"]])
       and all(w["picture"] == "training_yard" and w["date"] == "2026-10-08" and w["words"] for w in final["waived"])
       and check_campus.load_manifest(root)["pictures"]["training_yard"].get("rev") == 3, out)
    ok("a fact that was fixed is not rewritten or moved back to a proposal by the picture that stands against it",
       frec.is_fixed(frec.by_id[right["id"]]) and frec.by_id[right["id"]]["side"] == "right"
       and frec.is_fixed(frec.by_id["exit.training_yard.training"]) and frec.by_id["exit.training_yard.training"]["side"] == "left")
    rc, out = run([tool("check_campus.py"), "--record", rpath, "--layout-dump", redump(hot2), "--no-hash", "--manifest",
                   os.path.join(root, "game", "layout", "pictures.json"), "--quiet"])
    ok("check_campus.py then reports the waived facts on every run and does not fail on them",
       rc == 0 and out.count("waived (the owner accepted it") >= 2, "\n".join(l for l in out.splitlines() if not l.startswith("WAIT")))


POSE_PLAN = [
    {"who": "megumi", "place": "dorm_common", "variant": "evening", "batch": 91, "doing": "t", "spot": "standing by the wall"},
    {"who": "yuji", "place": "dorm_common", "variant": "evening", "batch": 91, "doing": "t", "spot": "sitting on the floor cushions"},
    {"who": "nobara", "place": "dorm_common", "variant": "evening", "batch": 91, "doing": "t", "spot": "standing by the television", "at": "tv"},
    {"who": "megumi", "place": "megumi_room", "variant": "night", "batch": 92, "doing": "t", "spot": "sitting on the bed"},
    {"who": "megumi", "place": "megumi_room", "variant": "night", "batch": 92, "state": "asleep", "doing": "asleep"},
    {"who": "panda", "place": "senpai_room", "variant": "night", "batch": 92, "state": "asleep", "doing": "asleep"},
    {"who": "toge", "place": "senpai_room", "variant": "night", "batch": 92, "doing": "t", "spot": "sitting at the board"},
    {"who": "nobara", "place": "harajuku", "variant": "", "batch": 93, "doing": "t", "spot": "on the pavement left of the middle"},
    {"who": "maki", "place": "harajuku", "variant": "", "batch": 93, "doing": "t", "spot": "on the pavement right of the middle"},
    {"who": "megumi", "place": "harajuku", "variant": "", "batch": 94, "doing": "t", "spot": "on the pavement"},
    {"who": "yuji", "place": "pool", "variant": "", "batch": 95, "doing": "t", "spot": "at the deck's edge"},
    {"who": "maki", "place": "dorm_common", "variant": "evening", "batch": 96, "doing": "t", "spot": "sitting on the old dusty sofa"},
]
# The asleep, home and away tables of a test, in the shape the dump writes them (tools/smoke/u2_dump.rpy: `world`).
TEST_TABLES = {"world": {"asleep": {"weekday": ["megumi", "panda"], "weekend": ["yuji", "toge"]},
                         "homes": {"megumi": "megumi_room", "panda": "senpai_room", "toge": "senpai_room", "yuji": "yuji_room"},
                         "away": {"nobara": {"Sun Afternoon": "harajuku"}, "maki": {"Sun Afternoon": "harajuku"},
                                  "yuji": {"Sun Afternoon": "shibuya"}}}}


def group_pose(lab):
    """make_pose_workflow.py and install_pose.py: 5.12's tooling."""
    root = mkroot(os.path.join(lab.work, "r_pose"))
    bg = os.path.join(root, "game", "images", "bg")
    shutil.copyfile(os.path.join(bg, "town_street.png"), os.path.join(bg, "harajuku.png"))        # a test street
    plan = os.path.join(lab.work, "pose_plan.json")
    json.dump(POSE_PLAN, open(plan, "w"))
    manifest = os.path.join(lab.work, "pose_manifest.json")
    json.dump({"pictures": {"dorm_common": {"rev": 3, "kind": "inplace"},
                            "dorm_common_evening": {"rev": 2, "kind": "relight", "of": "dorm_common", "of_rev": 3},
                            "harajuku": {"rev": 2, "kind": "composed"}}}, open(manifest, "w"))
    keep = os.path.join(lab.work, "pose_keep"); os.makedirs(keep, exist_ok=True)
    json.dump({"scale": [400, 300, 700]}, open(os.path.join(keep, "harajuku.json"), "w"))
    dump = stamp(lab.dump, root, extra=TEST_TABLES)
    bare = stamp(lab.dump, root, out=os.path.join(root, "dump_bare.json"))
    mk = [tool("make_pose_workflow.py")]
    common = ["--root", root, "--layout-dump", dump, "--manifest", manifest, "--print"]

    rc, out = run(mk + ["--batch", "5"] + common)
    kl = json.load(open(os.path.join(TOOLS, "bgs", "keep", "dorm_common.json")))
    want = int(round(160 * (kl["scale"][2] - kl["scale"][1]) / 200.0))
    ok("the batch 5 prompt for Nobara contains her height in pixels, from the Common Room keep list's `scale` "
       "(%d px)" % want, rc == 0 and "pose_dorm_common__nobara__evening" in out and "about %d pixels tall" % want in out, out)
    ok("it keeps the frozen clothes sentence and asks for the reference figure's flat shading and a contact shadow only",
       "Keep her face, hair, clothes and colours exactly as in the second picture" in out
       and "the same clean flat anime cel shading as the reference figure" in out and "a soft contact shadow only" in out, out)
    ok("no prompt names the series or a character", not re.search(r"(?i)\b(nobara|jujutsu|kaisen|megumi|yuji)\b", out.split("\n", 1)[1].split("picture 1:")[0]), out)
    rc, out = run(mk + ["--batch", "5", "--root", root, "--layout-dump", dump, "--print"])
    ok("K8: with the Common Room's evening not installed in the new look, the row is refused in one line",
       rc != 0 and len(out.strip().splitlines()) == 1 and "not installed in the new look" in out, out)
    stale = os.path.join(lab.work, "pose_manifest_stale.json")
    json.dump({"pictures": {"dorm_common": {"rev": 4, "kind": "inplace"},
                            "dorm_common_evening": {"rev": 2, "kind": "relight", "of": "dorm_common", "of_rev": 3}}}, open(stale, "w"))
    rc, out = run(mk + ["--batch", "5", "--root", root, "--layout-dump", dump, "--manifest", stale, "--print"])
    ok("K8: and when that evening picture has gone stale", rc != 0 and "remade first" in out, out)
    empty = os.path.join(lab.work, "pose_keep_empty"); os.makedirs(empty, exist_ok=True)
    rc, out = run(mk + ["--batch", "5"] + common + ["--keep", empty])
    ok("with no `scale` in the room's view_ file or its keep list, it refuses in one line",
       rc != 0 and len(out.strip().splitlines()) == 1 and "no `scale`" in out, out)
    view = os.path.join(root, "game", "layout", "view_dorm_common.json")
    data = json.load(open(view)); data["scale"] = [100, 100, 500]; json.dump(data, open(view, "w"))
    rc, out = run(mk + ["--batch", "5", "--root", root, "--layout-dump", stamp(lab.dump, root, out=os.path.join(root, "d2.json"), extra=TEST_TABLES),
                        "--manifest", manifest, "--print"])
    ok("the room's own view_ file wins over the keep list (a 400 px door: 320 px)", rc == 0 and "about 320 pixels tall" in out, out)
    data.pop("scale"); json.dump(data, open(view, "w"))
    dump = stamp(lab.dump, root, extra=TEST_TABLES)
    common = ["--root", root, "--layout-dump", dump, "--manifest", manifest, "--print"]
    planned = common + ["--plan", plan, "--keep", keep]

    rc, out = run(mk + ["--batch", "95"] + planned)
    ok("make_pose_workflow.py refuses a test row at the pool (K16)", rc != 0 and "Bathhouse, the Sauna or the Pool" in out, out)
    night = os.path.join(lab.work, "pose_manifest_night.json")
    json.dump({"pictures": {"megumi_room": {"rev": 2, "kind": "composed"},
                            "megumi_room_night": {"rev": 2, "kind": "relight", "of": "megumi_room", "of_rev": 2},
                            "senpai_room": {"rev": 2, "kind": "composed"},
                            "senpai_room_night": {"rev": 2, "kind": "relight", "of": "senpai_room", "of_rev": 2}}}, open(night, "w"))
    for stem in ("megumi_room_night", "senpai_room_night"):
        shutil.copyfile(os.path.join(bg, "your_room_night.png"), os.path.join(bg, stem + ".png"))
    asleep = ["--root", root, "--layout-dump", dump, "--manifest", night, "--print", "--plan", plan, "--keep", keep]
    rc, out = run(mk + ["megumi_room", "megumi", "night", "--asleep"] + asleep)
    ok("for a row whose `state` is asleep it writes the frozen blanket sentence and no figure",
       rc == 0 and "in the bed, a sleeper under a blanket, turned to the wall; only the top of the hair shows; no face, "
       "no arm, no shoulder" in out and "Paint that same character" not in out and "pixels tall" not in out
       and "pose_megumi_room__megumi__night__asleep" in out, out)
    rc, out = run(mk + ["senpai_room", "panda", "night", "--asleep"] + asleep)
    ok("and for Panda, \"a very large mound under a blanket\"", rc == 0 and "a very large mound under a blanket" in out
       and "sleeper" not in out, out)
    rc, out = run(mk + ["harajuku", "nobara"] + planned)
    ok("it accepts a test row whose place is a district WORLD_AWAY sends that person to (the height from the "
       "district picture's keep list: 320 px)", rc == 0 and "about 320 pixels tall" in out, out)
    rc, out = run(mk + ["harajuku", "megumi"] + planned)
    ok("and refuses one for a district it does not send them to", rc != 0 and "never sends megumi to harajuku" in out, out)
    bare = stamp(lab.dump, root, out=os.path.join(root, "dump_bare.json"))
    rc, out = run(mk + ["harajuku", "nobara", "--root", root, "--layout-dump", bare, "--manifest", manifest, "--print",
                        "--plan", plan, "--keep", keep])
    ok("with the dump as it is (the game's own away table, world.away, sends her there on Sunday afternoon), the "
       "same district row is accepted", rc == 0 and "about 320 pixels tall" in out, out)
    rc, out = run(mk + ["harajuku", "megumi", "--root", root, "--layout-dump", bare, "--manifest", manifest, "--print",
                        "--plan", plan, "--keep", keep])
    ok("and by the game's own table a row for someone it never sends there is refused",
       rc != 0 and "never sends megumi to harajuku" in out, out)
    none = stamp(lab.dump, root, out=os.path.join(root, "dump_no_world.json"), extra={"__drop__": ("world",)})
    rc, out = run(mk + ["harajuku", "nobara", "--root", root, "--layout-dump", none, "--manifest", manifest, "--print",
                        "--plan", plan, "--keep", keep])
    ok("with a dump that has no away table (its `world` taken out), a district row is refused, and it says why",
       rc != 0 and "no away table" in out, out)
    rc, out = run(mk + ["--batch", "96"] + planned)
    ok("a `spot` with a banned word is refused by the prompt check", rc != 0 and "check_prompts" in out and "old" in out, out)

    # install_pose.py
    if not lab.art:
        skipped("install_pose.py's room rules (the test renders are drawn with Pillow)", "no ComfyUI python")
    else:
        evening = os.path.join(bg, "dorm_common_evening.png")
        ip = [tool("install_pose.py")]
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        view_before = open(view, "rb").read()

        def render(name, box, src=evening, colour="230,40,60"):
            return lab.syn("patch", src, name, box, colour)

        before = tree_hash(root)
        rc, out = run(ip + [render("pose_dorm_common__megumi__evening_a_00001_.png", "60,420,160,300")] + tail)
        ok("install_pose.py refuses a test box that covers an exit point of its room, and names the point",
           rc != 0 and "REFUSED" in out and "the way to Dormitory Garden at (84, 540)" in out
           and not os.path.exists(os.path.join(root, "game", "layout", "pose_dorm_common.json")), out)
        rc, out = run(ip + [render("pose_dorm_common__megumi__evening_b_00001_.png", "1500,480,180,300")] + tail)
        ok("it refuses one that covers a hotspot point its row does not name in `at`",
           rc != 0 and "the hotspot tv at (1590, 560)" in out and "does not name in `at`" in out, out)
        rc, out = run(ip + [render("pose_dorm_common__nobara__evening_b_00001_.png", "1500,480,180,300")] + tail)
        ok("it accepts one that covers the hotspot its row names in `at`", rc == 0 and "installed ->" in out, out)
        pose_file = os.path.join(root, "game", "layout", "pose_dorm_common.json")
        man = check_campus.load_manifest(root)["pictures"]
        ok("the box goes to pose_<place>.json; the room's view_ file is byte for byte what it was (K15)",
           json.load(open(pose_file))["poses"].get("nobara__evening") == [1476, 456, 228, 348] and open(view, "rb").read() == view_before,
           open(pose_file).read())
        ok("and it writes a manifest row: the picture the pose was painted on, at its revision",
           man.get("pose_dorm_common__nobara__evening") == {"of": "dorm_common_evening", "of_rev": 1}, json.dumps(man))
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc, out = run(ip + [render("pose_dorm_common__megumi__evening_a_00002_.png", "700,500,260,360")] + tail)
        ok("fixture: a first pose (Megumi, the Common Room's evening) is installed", rc == 0, out)
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        before = tree_hash(root)
        rc, out = run(ip + [render("pose_dorm_common__yuji__evening_a_00001_.png", "860,560,260,300")] + tail)
        ok("install_pose.py refuses two overlapping test boxes that can show together, and names both",
           rc != 0 and "overlaps the box of pose_dorm_common__megumi__evening" in out and "can show together" in out
           and not os.path.exists(os.path.join(root, "game", "images", "place", "pose_dorm_common__yuji__evening.png")), out)
        rc, out = run(ip + [render("pose_dorm_common__yuji__evening_a_00002_.png", "1150,600,200,300")] + tail)
        ok("and accepts the same person where the boxes do not overlap", rc == 0, out)

        room = os.path.join(bg, "megumi_room_night.png")
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc, out = run(ip + [render("pose_megumi_room__megumi__night_a_00001_.png", "1100,560,400,300", room)] + tail)
        ok("fixture: Megumi awake on his bed at Night is installed", rc == 0, out)
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc, out = run(ip + [render("pose_megumi_room__megumi__night__asleep_a_00001_.png", "1150,600,420,240", room, "90,80,120")] + tail)
        poses = json.load(open(os.path.join(root, "game", "layout", "pose_megumi_room.json")))["poses"]
        ok("it accepts two overlapping boxes that cannot show together: one awake, one asleep, the same person",
           rc == 0 and "never show together" in out and sorted(poses) == ["megumi__night", "megumi__night__asleep"], out)
        room2 = os.path.join(bg, "senpai_room_night.png")
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc, out = run(ip + [render("pose_senpai_room__panda__night__asleep_a_00001_.png", "900,600,500,240", room2, "90,80,120")] + tail)
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc2, out2 = run(ip + [render("pose_senpai_room__toge__night_a_00001_.png", "1000,500,300,360", room2)] + tail)
        ok("but Toge awake at the board and Panda asleep beside it do show together (weekday Nights) and may not overlap",
           rc == 0 and rc2 != 0 and "can show together" in out2, out + out2)

        rc, out = run([tool("check_content.py"), "--layout-files", "--layout-dir", os.path.join(root, "game", "layout")])
        ok("what install_pose.py wrote for the campus rooms passes check_content.py --layout-files", rc == 0, out)
        # (a district's pose file, written next, is not known to that rule yet: handed to U0c2)
        street = os.path.join(bg, "harajuku.png")
        rc, out = run(ip + [render("pose_harajuku__nobara_a_00001_.png", "500,500,300,480", street)] + tail)
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc2, out2 = run(ip + [render("pose_harajuku__maki_a_00001_.png", "700,520,300,460", street)] + tail)
        ok("it refuses two overlapping test boxes in one district for two people WORLD_AWAY sends there the same hour",
           rc == 0 and rc2 != 0 and "overlaps the box of pose_harajuku__nobara" in out2 and "Sun, Afternoon" in out2, out + out2)
        rc, out = run(ip + [render("pose_harajuku__megumi_a_00001_.png", "1200,520,300,460", street)] + tail)
        ok("and a pose in a district the game never sends that person to", rc != 0 and "never sends megumi to harajuku" in out, out)
        rc, out = run(ip + [render("pose_pool__yuji_a_00001_.png", "900,500,300,400", evening)] + tail)
        ok("install_pose.py refuses a pose at the pool (K16)", rc != 0 and "Bathhouse, the Sauna or the Pool" in out, out)
        # D59: the uniform's cloth on a painted pose
        dump = stamp(lab.dump, root, extra=TEST_TABLES)
        tail = ["--root", root, "--layout-dump", dump, "--plan", plan]
        rc, out = run(ip + [render("pose_dorm_common__maki__evening_a_00001_.png", "300,560,220,330", evening, "58,50,92"), "--dry"] + tail)
        ok("D59: for someone in the school uniform the cloth in the box is measured against the ramp and reported "
           "(a flat purplish cloth reads OFF the ramp)", rc == 0 and "the uniform's cloth in the box" in out and "OFF the ramp" in out, out)
        rc, out = run(ip + [render("pose_dorm_common__maki__evening_a_00002_.png", "300,560,220,330", evening, "37,34,50"), "--dry"] + tail)
        ok("and cloth of the ramp's own colour reads on the ramp", rc == 0 and "on the ramp" in out and "OFF the ramp" not in out, out)

    # the harness's own test room: p2_view.rpy section 5, with the two changes handed to its owner
    # (--no-game, and the box now in pose_<place>.json)
    fix = os.path.join(lab.work, "p2view"); out_root = os.path.join(fix, "root")
    os.makedirs(os.path.join(out_root, "game", "layout"))
    hot = os.path.join(out_root, "game", "layout", "hot_zzroom.json")
    open(hot, "w").write('{"spots": {"zz_thing": [640, 480]}}\n')
    src = open(os.path.join(TOOLS, "smoke", "p2_view.rpy"), encoding="utf-8").read()
    m = re.search(r"ZZV_POSE_PY = r'''(.*?)'''", src, re.S)
    rc, out = run(["-c", m.group(1), TOOLS, fix])
    side = os.path.join(out_root, "game", "layout", "pose_zzroom.json")
    base = [tool("install_pose.py"), "--no-game", "--bg", os.path.join(fix, "room.png"), "--root", out_root]
    r1 = run(base + [os.path.join(fix, "pose_zzroom__nobara_a_00001_.png")])
    refused = r1[0] != 0 and "REFUSED" in r1[1] and "40.0%" in r1[1] and not os.path.exists(side)
    r2 = run(base + [os.path.join(fix, "pose_zzroom__yuji_b_00002_.png")])
    r3 = run(base + [os.path.join(fix, "pose_zzroom__megumi__evening_a_00001_.png")])
    r4 = run(base + [os.path.join(fix, "pose_zzroom__yuji_b_00002_.png"), "--box", "400,300,500,700"])
    r5 = run([tool("install_pose.py"), "--no-game", "--bg", os.path.join(fix, "room2.png"), "--root", out_root,
              os.path.join(fix, "pose_zzroom__maki_a_00001_.png")])
    r6 = run(base + [os.path.join(fix, "pose_zzroom__panda_a_00001_.png")])
    poses = json.load(open(side)).get("poses", {}) if os.path.exists(side) else {}
    ok("--no-game: p2_view.rpy's own six calls give the answers that harness pins (40% refused; boxes 576,276,528,480; "
       "--box; the 1376x768 render; the feet), the box now in pose_zzroom.json",
       refused and all(r[0] == 0 for r in (r2, r3, r4, r5, r6)) and poses.get("megumi__evening") == [576, 276, 528, 480]
       and poses.get("yuji") == [400, 300, 500, 700] and poses.get("maki") == [576, 280, 528, 484]
       and poses.get("panda") == [576, 276, 528, 528] and "10.1%" in r5[1]
       and sorted(os.listdir(os.path.join(out_root, "game", "layout"))) == ["hot_zzroom.json", "pose_zzroom.json"]
       and set(json.load(open(side))) == {"poses"}, json.dumps(poses) + r1[1] + r5[1])
    rc, out = run([tool("install_pose.py"), "--no-game", "--bg", os.path.join(fix, "room.png"),
                   os.path.join(fix, "pose_zzroom__yuji_b_00002_.png")])
    ok("--no-game cannot write into the game itself: it needs --root", rc != 0 and "needs --root" in out, out)
    rc, out = run([tool("install_pose.py"), "--no-game", "--root", REPO + os.sep, "--bg", os.path.join(fix, "room.png"),
                   os.path.join(fix, "pose_zzroom__yuji_b_00002_.png")])
    ok("nor when --root names the game's own folder another way (a trailing slash): the folders are compared, not their names",
       rc != 0 and "needs --root" in out and not os.path.exists(os.path.join(REPO, "game", "layout", "pose_zzroom.json")), out)


# an editor's nudge, by hand: the picture enlarged about its middle and slid (pure Python, as install_face.py is)
NUDGE = r'''
import sys
sys.path.insert(0, sys.argv[1])
from pngread import load
from raster import Img
from install_face import sample, rgb
im = rgb(load(sys.argv[2])); zoom, dx, dy = [float(v) for v in sys.argv[4:7]]
c = im.w / 2.0
out = Img(im.w, im.h); o = out.buf
for y in range(im.h):
    fy = c + (y - c - dy) / zoom
    for x in range(im.w):
        v = sample(im, c + (x - c - dx) / zoom, fy)
        i = (y * im.w + x) * 3
        o[i] = int(v[0] + 0.5); o[i + 1] = int(v[1] + 0.5); o[i + 2] = int(v[2] + 0.5)
out.save(sys.argv[3])
'''


def group_face(lab):
    """install_face.py: the close-up from a staged sprite, the measured boxes, faces.json."""
    work = os.path.join(lab.work, "face")
    stage, images = os.path.join(work, "stage"), os.path.join(work, "images")
    os.makedirs(os.path.join(stage, "char"))
    for e in ("neutral", "happy", "serious", "angry", "surprised", "sad"):
        shutil.copyfile(os.path.join(REPO, "game", "images", "char", "megumi_%s.png" % e), os.path.join(stage, "char", "megumi_%s.png" % e))
    sprite = os.path.join(stage, "char", "megumi_neutral.png")
    rc, out = run([tool("install_face.py"), "--prepare", "megumi", "--sprite", sprite, "--images", images])
    crop = os.path.join(images, "masks", "megumi_fx_crop.txt")
    ok("install_face.py --prepare <who> --sprite <file> cuts the close-up from the staged sprite, not the game's",
       rc == 0 and "the staged sprite" in out and os.path.exists(os.path.join(images, "megumi_fx_in.png")) and os.path.exists(crop), out)
    X, Y, side = [int(v) for v in open(crop).read().split()[:3]] if os.path.exists(crop) else (0, 0, 1)
    ok("the square is found from the sprite's own outline and holds the head (it covers today's eye and mouth boxes)",
       X <= 308 and Y <= 283 and X + side >= 308 + 114 and Y + side >= 338 + 28, (X, Y, side))
    # an "edit": the close-up with a flat patch where the eyes are (then one where the mouth is)
    edits = {}
    code = ("import sys; sys.path.insert(0, %r)\nfrom pngread import load\nim = load(sys.argv[1]); s = im.w / float(%d)\n"
            "x, y, w, h = [int(v) for v in sys.argv[3].split(',')]\n"
            "for yy in range(int((y - %d) * s), int((y + h - %d) * s)):\n"
            "    for xx in range(int((x - %d) * s), int((x + w - %d) * s)):\n"
            "        j = (yy * im.w + xx) * im.ch; im.buf[j:j + 3] = bytes((238, 200, 176))\n"
            "im.save(sys.argv[2])\n" % (TOOLS, side, Y, Y, X, X))
    for kind, box in (("blink", "316,290,98,30"), ("talk", "350,342,40,20")):
        edits[kind] = os.path.join(work, "megumi_%s_edit.png" % kind)
        run(["-c", code, os.path.join(images, "megumi_fx_in.png"), edits[kind], box])
    before = game_status()
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--sprite", sprite, "--images", images,
                   "--stage", stage, "--root", os.path.join(work, "root")])
    rc2, out2 = run([tool("install_face.py"), edits["talk"], "megumi", "talk", "--sprite", sprite, "--images", images,
                     "--stage", stage, "--root", os.path.join(work, "root")])
    rows = json.load(open(os.path.join(stage, "faces.json"))) if os.path.exists(os.path.join(stage, "faces.json")) else {}
    eyes, mouth = rows.get("eyes", {}).get("megumi"), rows.get("mouth", {}).get("megumi")

    def near(got, want, tol=10):
        return got is not None and all(abs(a - b) <= tol for a, b in zip(got, want))

    ok("install_face.py measures the eye box on the sprite it is given and writes it to faces.json beside the blink "
       "row (measured %s; the patch was 316,290 98x30)" % eyes,
       rc == 0 and near(eyes, [316 - 8, 290 - 8, 98 + 16, 30 + 16]) and isinstance(rows.get("blink_also", {}).get("megumi"), list), out)
    ok("and the mouth box (measured %s; the patch was 350,342 40x20)" % mouth,
       rc2 == 0 and near(mouth, [350 - 8, 342 - 8, 40 + 16, 20 + 16]), out2)
    faces_prev = os.path.join(work, "root", "shots", "art", "fx_megumi_blink_faces.png")
    ok("a blink also writes a preview of every other face with the blink laid on it, and says which take it and "
       "which keep their own eyes, so the row is looked at before install_set.py",
       rc == 0 and os.path.exists(faces_prev) and "faces preview -> " in out
       and len(re.findall(r"\((?:takes the blink|keeps its own eyes)\)", out)) == 5, out)
    ok("the two overlay pictures are staged, not installed: nothing under game/ changed",
       os.path.exists(os.path.join(stage, "fx", "fx_megumi_blink.png")) and os.path.exists(os.path.join(stage, "fx", "fx_megumi_talk.png"))
       and game_status() == before)
    # an editor's picture rarely comes back on the pixel: nudged inside the range the tool searches, the boxes
    # must be the ones measured without the nudge
    for label, zoom, dx, dy in (("enlarged 2%", 1.02, 0, 0), ("enlarged 1% and slid 3 px", 1.01, 3, -2),
                                ("slid 4 px (of the 1024 the editor works at)", 1.0, 4, 0)):
        got = {}
        said = ""
        for kind in ("blink", "talk"):
            nudged = os.path.join(work, "megumi_%s_nudged.png" % kind)
            st = os.path.join(work, "stage_n_%s" % re.sub(r"\W+", "_", label))
            run(["-c", NUDGE, TOOLS, edits[kind], nudged, zoom, dx, dy])
            rc, out = run([tool("install_face.py"), nudged, "megumi", kind, "--sprite", sprite, "--images", images,
                           "--stage", st, "--root", os.path.join(work, "root")])
            said += out
            rows_n = json.load(open(os.path.join(st, "faces.json"))) if os.path.exists(os.path.join(st, "faces.json")) else {}
            got[kind] = rows_n.get("eyes" if kind == "blink" else "mouth", {}).get("megumi")
        ok("the same two edits %s give the same boxes within 10 px (eyes %s, mouth %s)" % (label, got["blink"], got["talk"]),
           eyes is not None and mouth is not None and near(got["blink"], eyes) and near(got["talk"], mouth), said)
    # a measured box that cannot be right is refused, and nothing is written
    def staged_state():
        h = hashlib.sha256()
        for d, _dirs, names in sorted(os.walk(stage)):
            for n in sorted(names):
                h.update(n.encode() + open(os.path.join(d, n), "rb").read())
        return h.hexdigest()

    state = staged_state()
    tall = os.path.join(work, "megumi_tall_edit.png")
    run(["-c", code, os.path.join(images, "megumi_fx_in.png"), tall, "316,270,98,80"])
    rc, out = run([tool("install_face.py"), tall, "megumi", "blink", "--sprite", sprite, "--images", images,
                   "--stage", stage, "--root", os.path.join(work, "root")])
    ok("an edit that changed far more than the eyes is REFUSED (the eye box would be taller than a fifth of the "
       "close-up) and nothing is written", rc != 0 and "REFUSED" in out and "cannot be right" in out
       and "Run the edit again" in out and staged_state() == state, out)
    high = os.path.join(work, "megumi_high_edit.png")
    run(["-c", code, os.path.join(images, "megumi_fx_in.png"), high, "350,296,40,20"])
    rc, out = run([tool("install_face.py"), high, "megumi", "talk", "--sprite", sprite, "--images", images,
                   "--stage", stage, "--root", os.path.join(work, "root")])
    ok("a \"mouth\" measured on top of the eye box is REFUSED, and nothing is written",
       rc != 0 and "REFUSED" in out and "overlaps the eyes box" in out and staged_state() == state, out)
    wide = os.path.join(work, "megumi_wide_edit.png")
    run(["-c", code, os.path.join(images, "megumi_fx_in.png"), wide, "330,336,60,70"])
    rc, out = run([tool("install_face.py"), wide, "megumi", "talk", "--sprite", sprite, "--images", images,
                   "--stage", stage, "--root", os.path.join(work, "root")])
    ok("and a mouth box taller than a mouth (about 60 px)", rc != 0 and "a mouth is not" in out and staged_state() == state, out)
    # D57: a staged sprite's blink never goes into the game by itself
    root_game = mkroot(os.path.join(work, "root_game"))
    tb = tree_hash(root_game)
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--sprite", sprite, "--images", images,
                   "--root", root_game])
    ok("with --sprite naming a staged sprite and no --stage it stops in one line and the tree is unchanged (D57)",
       rc != 0 and out.strip() == "a staged sprite's blink and mouth go in only with the whole set: add --stage <staged "
       "folder>, then tools/install_set.py" and tree_hash(root_game) == tb
       and not os.path.exists(os.path.join(root_game, "game", "layout", "faces.json")), out)
    # ... and not after --prepare --sprite either: the close-up's record says which sprite it was cut from
    other = os.path.join(work, "stage_other", "char")
    os.makedirs(other)
    shutil.copyfile(os.path.join(REPO, "game", "images", "char", "megumi_serious.png"), os.path.join(other, "megumi_neutral.png"))
    images_o = os.path.join(work, "images_other")
    run([tool("install_face.py"), "--prepare", "megumi", "--sprite", os.path.join(other, "megumi_neutral.png"), "--images", images_o])
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--images", images_o, "--root", root_game])
    ok("after --prepare --sprite <another drawing>, the plain command (no --sprite, no --stage) stops in one line: the "
       "close-up was cut from another sprite; the tree is unchanged (D57)",
       rc != 0 and len(out.strip().splitlines()) == 1 and out.startswith("this close-up was cut from another sprite (")
       and os.path.join("stage_other", "char", "megumi_neutral.png") in out and "run --prepare again" in out
       and tree_hash(root_game) == tb and not os.path.exists(os.path.join(root_game, "game", "layout", "faces.json")), out)
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--sprite", sprite, "--images", images_o,
                   "--stage", os.path.join(work, "stage_o2"), "--root", os.path.join(work, "root")])
    ok("and so does the same close-up laid on a different staged sprite, with nothing staged",
       rc != 0 and out.startswith("this close-up was cut from another sprite (") and not os.path.exists(os.path.join(work, "stage_o2", "faces.json")), out)
    images_3 = os.path.join(work, "images_three")
    os.makedirs(os.path.join(images_3, "masks"))
    open(os.path.join(images_3, "masks", "megumi_fx_crop.txt"), "w").write("%d %d %d\n" % (X, Y, side))
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--sprite", os.path.join(other, "megumi_neutral.png"),
                   "--images", images_3, "--stage", os.path.join(work, "stage_o3"), "--root", os.path.join(work, "root")])
    ok("a record of three numbers (written before 7 Oct) is the game's own sprite: refused on a staged one",
       rc != 0 and out.startswith("this close-up was cut from another sprite (the game's own megumi_neutral.png"), out)
    root_old = os.path.join(work, "root_old")
    rc, out = run([tool("install_face.py"), edits["blink"], "megumi", "blink", "--images", images_3, "--root", root_old])
    ok("and accepted on the game's own, the old way (into a scratch folder)",
       rc == 0 and os.path.exists(os.path.join(root_old, "game", "images", "char", "fx", "fx_megumi_blink.png")), out)
    # the game's own sprites, the old way: the box from VIEW_FACE, and the measured blink row
    root = os.path.join(work, "root2")
    blink = os.path.join(OUTPUT, "yuji_blink_nanobanana_00001_.png")
    rec = os.path.expanduser("~/Desktop/JJK Game images/masks/yuji_fx_crop.txt")
    if os.path.exists(blink) and os.path.exists(rec):
        im2 = os.path.join(work, "images2"); os.makedirs(os.path.join(im2, "masks"))
        shutil.copyfile(rec, os.path.join(im2, "masks", "yuji_fx_crop.txt"))
        rc, out = run([tool("install_face.py"), blink, "yuji", "blink", "--images", im2, "--root", root])
        rows = json.load(open(os.path.join(root, "game", "layout", "faces.json"))) if rc == 0 else {}
        ok("REAL: Yuji's first blink render, installed the old way into a scratch folder, writes the measured "
           "blink row: the four faces the hand-set table lists (%s)" % rows.get("blink_also", {}).get("yuji"),
           rc == 0 and sorted(rows.get("blink_also", {}).get("yuji", [])) == ["happy", "sad", "serious", "surprised"]
           and "eyes" not in rows, out)
        st2 = os.path.join(work, "stage2")
        rc, out = run([tool("install_face.py"), blink, "yuji", "blink", "--sprite",
                       os.path.join(REPO, "game", "images", "char", "yuji_neutral.png"), "--images", im2, "--stage", st2, "--root", root])
        got = json.load(open(os.path.join(st2, "faces.json"))).get("eyes", {}).get("yuji") if rc == 0 else None
        ok("REAL: measured on his sprite, the eye box lands on the hand-set one (336,296 88x44) within 4 px: %s" % got,
           near(got, [336, 296, 88, 44], 4), out)
        nudged = os.path.join(work, "yuji_blink_nudged.png")
        run(["-c", NUDGE, TOOLS, blink, nudged, 1.01, 3, -2])
        st3 = os.path.join(work, "stage3")
        rc, out = run([tool("install_face.py"), nudged, "yuji", "blink", "--sprite",
                       os.path.join(REPO, "game", "images", "char", "yuji_neutral.png"), "--images", im2, "--stage", st3, "--root", root])
        rows3 = json.load(open(os.path.join(st3, "faces.json"))) if rc == 0 else {}
        got3 = rows3.get("eyes", {}).get("yuji")
        ok("REAL: the same render enlarged 1%% and slid 3 px gives the same eye box within 10 px (%s) and the same four faces" % got3,
           near(got3, got or [0, 0, 0, 0]) and sorted(rows3.get("blink_also", {}).get("yuji", [])) == ["happy", "sad", "serious", "surprised"], out)
    else:
        skipped("REAL: Yuji's first blink render through install_face.py", "%s or its crop record is absent" % blink)


def staged_from_game(lab, who, name):
    """A whole staged set made from the game's own sprites, with stand-in overlay pictures."""
    stage = os.path.join(lab.work, name)
    for sub in ("char", "side", "fx"):
        os.makedirs(os.path.join(stage, sub))
    for e in ("neutral", "happy", "serious", "angry", "surprised", "sad"):
        for sub in ("char", "side"):
            shutil.copyfile(os.path.join(REPO, "game", "images", sub, "%s_%s.png" % (who, e)), os.path.join(stage, sub, "%s_%s.png" % (who, e)))
    return stage


STANDIN_FX = r'''
import sys, os, json
sys.path.insert(0, sys.argv[1])
from pngread import load
folder, who = sys.argv[2], sys.argv[3]
boxes = {"blink": ("eyes", json.loads(sys.argv[4])), "talk": ("mouth", json.loads(sys.argv[5]))}
rows = {"blink_also": {who: ["happy"]}}
for kind, (key, (x, y, w, h)) in boxes.items():
    im = load(os.path.join(folder, "char", who + "_neutral.png"))
    for yy in range(y + 6, y + h - 6):
        for xx in range(x + 6, x + w - 6):
            j = (yy * im.w + xx) * 4
            if im.buf[j + 3] == 255:
                im.buf[j:j + 3] = bytes((236, 196, 170))
    im.save(os.path.join(folder, "fx", "fx_%s_%s.png" % (who, kind)))
    rows[key] = {who: [x, y, w, h]}
json.dump(rows, open(os.path.join(folder, "faces.json"), "w"), indent=2, sort_keys=True)
'''


def set_checks(lab, who, stage, root, label, cloth_flag):
    sprites = os.path.join(root, "game", "jjk_sprites.rpy")
    import install_set
    names_before = install_set.image_names(sprites, who)
    before = tree_hash(root)
    hidden = os.path.join(stage, "char", "%s_angry.png" % who)
    os.rename(hidden, hidden + ".away")
    rc, out = run([tool("install_set.py"), who, stage, "--root", root] + cloth_flag)
    ok("%s: a set with one face missing is refused, the missing picture is named, and nothing is written" % label,
       rc == 1 and "REFUSED" in out and "the angry sprite is missing" in out and tree_hash(root) == before, out)
    os.rename(hidden + ".away", hidden)
    faces = os.path.join(stage, "faces.json")
    kept = open(faces).read()
    data = json.loads(kept); data["eyes"].pop(who); json.dump(data, open(faces, "w"))
    rc, out = run([tool("install_set.py"), who, stage, "--root", root] + cloth_flag)
    ok("%s: and a set whose eye box is not in the staged faces.json" % label,
       rc == 1 and "no eyes box" in out and tree_hash(root) == before, out)
    open(faces, "w").write(kept)
    rc, out = run([tool("install_set.py"), who, stage, "--root", root, "--dry"] + cloth_flag)
    ok("%s: --dry checks the whole set and writes nothing" % label, rc == 0 and tree_hash(root) == before, out)
    rc, out = run([tool("install_set.py"), who, stage, "--root", root] + cloth_flag)
    names_after = install_set.image_names(sprites, who)
    resolves = all(os.path.exists(os.path.join(root, "game", f)) for fs in names_after.values() for f in fs)
    ok("%s: a full set is installed, and every one of the person's %d image names still resolves"
       % (label, len(names_before)), rc == 0 and len(names_before) == 14 and sorted(names_after) == sorted(names_before) and resolves, out)
    rows = json.load(open(os.path.join(root, "game", "layout", "faces.json")))
    want = json.loads(kept)
    ok("%s: the person's eye and mouth boxes and blink row are in game/layout/faces.json of the copy" % label,
       rows.get("eyes", {}).get(who) == want["eyes"][who] and rows.get("mouth", {}).get(who) == want["mouth"][who]
       and rows.get("blink_also", {}).get(who) == want["blink_also"][who], json.dumps(rows))
    return out


def group_set(lab):
    """install_set.py on a set made from the game's own sprites."""
    stage = staged_from_game(lab, "megumi", "set_megumi")
    rc, out = run(["-c", STANDIN_FX, TOOLS, stage, "megumi", "[308, 283, 114, 44]", "[345, 338, 48, 28]"])
    root = mkroot(os.path.join(lab.work, "r_set"))
    cloth = [] if lab.art else ["--no-cloth"]
    out = set_checks(lab, "megumi", stage, root, "install_set.py (a set made from the game's own Megumi)", cloth)
    if lab.art:
        ok("the uniform's cloth is matched in the same step and cloth_match.py --check passes (a set already on "
           "the ramp is left alone)", "cloth_match.py --check passes" in out, out)
    else:
        skipped("the uniform's cloth match inside install_set.py", "no ComfyUI python")
    ok("its sprites, unchanged, give the generated jjk_sprites.rpy it had (byte for byte)",
       open(os.path.join(root, "game", "jjk_sprites.rpy"), "rb").read() == open(os.path.join(REPO, "game", "jjk_sprites.rpy"), "rb").read())
    # a set that does not share one body
    stage2 = staged_from_game(lab, "megumi", "set_megumi_bad")
    run(["-c", STANDIN_FX, TOOLS, stage2, "megumi", "[308, 283, 114, 44]", "[345, 338, 48, 28]"])
    code = ("import sys; sys.path.insert(0, %r)\nfrom pngread import load\nim = load(sys.argv[1])\n"
            "for xx in range(300, 360):\n    j = (900 * im.w + xx) * 4; im.buf[j:j + 3] = bytes((200, 30, 30))\nim.save(sys.argv[1])\n" % TOOLS)
    run(["-c", code, os.path.join(stage2, "char", "megumi_sad.png")])
    before = tree_hash(root)
    rc, out = run([tool("install_set.py"), "megumi", stage2, "--root", root] + cloth)
    ok("a set whose six sprites do not share one body is refused, and nothing is written",
       rc == 1 and "do not share one body" in out and "the sad sprite" in out and tree_hash(root) == before, out)

    def bad_set(name, spoil):
        st = staged_from_game(lab, "megumi", name)
        run(["-c", STANDIN_FX, TOOLS, st, "megumi", "[308, 283, 114, 44]", "[345, 338, 48, 28]"])
        spoil(st)
        return run([tool("install_set.py"), "megumi", st, "--root", root] + cloth)

    def beside_the_head(st):     # at the height of the face, but out beside the hair
        run(["-c", "import sys; sys.path.insert(0, %r)\nfrom pngread import load\nim = load(sys.argv[1])\n"
             "for xx in range(200, 230):\n    j = (320 * im.w + xx) * 4; im.buf[j:j + 4] = bytes((200, 30, 30, 255))\nim.save(sys.argv[1])\n" % TOOLS,
             os.path.join(st, "char", "megumi_happy.png")])

    rc, out = bad_set("set_megumi_beside", beside_the_head)
    ok("\"one body\" is a box round the face: a sprite that differs at the height of the face but beside the head is refused",
       rc == 1 and "the happy sprite differs from the calm one outside the face" in out and tree_hash(root) == before, out)
    rc, out = bad_set("set_megumi_noblink", lambda st: shutil.copyfile(os.path.join(st, "char", "megumi_neutral.png"),
                                                                       os.path.join(st, "fx", "fx_megumi_blink.png")))
    ok("an overlay picture that is the calm sprite itself (a blink that never closes) is refused",
       rc == 1 and "the blink picture is the calm sprite itself" in out and tree_hash(root) == before, out)
    rc, out = bad_set("set_megumi_side", lambda st: shutil.copyfile(os.path.join(st, "side", "megumi_happy.png"),
                                                                    os.path.join(st, "side", "megumi_sad.png")))
    ok("a side portrait that was not made from the sprite staged beside it is refused, and named",
       rc == 1 and "the sad side portrait was not made from the sad sprite" in out and "the happy side" not in out
       and tree_hash(root) == before, out)

    def overlapping(st):
        f = os.path.join(st, "faces.json")
        data = json.load(open(f)); data["mouth"]["megumi"] = [345, 300, 48, 28]; json.dump(data, open(f, "w"))

    rc, out = bad_set("set_megumi_overlap", overlapping)
    ok("a set whose eye and mouth boxes overlap is refused",
       rc == 1 and "the eyes box (308, 283) 114x44 and the mouth box (345, 300) 48x28 overlap" in out and tree_hash(root) == before, out)


def group_status(lab):
    root = mkroot(os.path.join(lab.work, "r_status"))
    rc, out = run([tool("art_status.py"), "--root", root, "--check"])
    ok("art_status.py --check passes on a copy of the tree, and with no manifest says every picture is today's",
       rc == 0 and "none yet" in out and "art_status --check: PASS" in out, out)
    os.remove(os.path.join(root, "game", "images", "fg", "fg_cafeteria.png"))
    rc, out = run([tool("art_status.py"), "--root", root, "--check"])
    ok("art_status.py --check reports a deleted foreground file, by name", rc == 1 and "game/images/fg/fg_cafeteria.png" in out
       and "FAIL" in out, out)
    json.dump({"pictures": {"dorm_common": {"rev": 2, "kind": "inplace", "render": "x.png"},
                            "fg_dorm_common": {"of": "dorm_common", "of_rev": 1}}},
              open(os.path.join(root, "game", "layout", "pictures.json"), "w"))
    rc, out = run([tool("art_status.py"), "--root", root])
    ok("the table lists a half-made room set (the Common Room's old evening and night, and the memory that still "
       "shows the old night picture) and a stale foreground",
       "dorm_common_evening" in out and "Eleven Tuesdays" in out and re.search(r"fg_dorm_common\s+made for revision 1", out) is not None, out)
    ok("a stale foreground of an hour picture names the picture whose revision moved (the day picture, not the hour's)",
       re.search(r"fg_dorm_common_evening\s+made for revision 1 of dorm_common, which is now at revision 2", out) is not None
       and "dorm_common_evening, which is now at revision" not in out, out)


# the sixteen look-test renders: (picture, render, verdict, what its words must hold). Five that nothing moved,
# vanished or appeared in are a LOOK and not a PASS: each has a new view through a window (the Common Room's two
# panes show a roof where the trees were; the Library's windows; a doorway opened in the Courtyard's hall), which
# 5.4 step 6 shows the owner and does not refuse. A LOOK can be chosen like a PASS.
SIXTEEN = [
    ("dorm_common", "look3_dorm_common_keep", "LOOK", ["drawn differently"]),
    ("cafeteria", "look3_cafeteria_keep", "PASS", []),
    ("dorm_common", "look_dorm_common_A", "LOOK", ["drawn differently"]),
    ("courtyard", "look_courtyard_A", "LOOK", ["drawn differently"]),
    ("library", "look_library_A", "LOOK", ["drawn differently"]),
    ("dorm_common", "look_dorm_common_B", "REFUSED", ["something new is on the sofa's near arm", "something new is on the low table's top"]),
    ("dorm_common", "look2_dorm_common_clean", "REFUSED", ["the floor cushions by the low table are gone", "the manga on the bookshelf is gone",
                                                         "the kettle on the counter is gone", "the bag by the sofa is gone"]),
    ("dorm_common", "look_dorm_common_C", "PASS", []),
    ("courtyard", "look_courtyard_B", "PASS", []),
    ("courtyard", "look_courtyard_C", "PASS", []),
    ("library", "look_library_B", "LOOK", ["drawn differently"]),
    ("library", "look_library_C", "PASS", []),
    ("courtyard", "look2_courtyard_gateway", "REFUSED", ["this is not the same picture"]),
    ("courtyard", "look2_courtyard_mainhall", "REFUSED", ["this is not the same picture"]),
    ("library", "look2_library_bright", "REFUSED", ["the thing at the hotspot locked_shelf moved 1", "no longer lines up with the picture in the game"]),
    ("library", "look2_library_gallery", "REFUSED", ["this is a different picture"]),
]
PAIRS = [("dorm_common", "dorm_common", "evening"), ("dorm_common", "dorm_common", "night"), ("rooftop", "rooftop", "evening"),
         ("rooftop", "rooftop", "night"), ("riverside", "riverside", "evening"), ("infirmary", "infirmary", "night"),
         ("girls_dorm", "girls_dorm", "night"), ("dorm", "your_room", "night")]


def figures(out):
    return [json.loads(m) for m in re.findall(r"^\s+figures\s+(\{.*\})$", out, re.M)]


def group_real(lab, write=False):
    """The sixteen look-test renders and the eight day and hour pairs the game has."""
    if not lab.art:
        skipped("the sixteen test renders and the eight day and hour pairs", "no ComfyUI python")
        return
    root = mkroot(os.path.join(lab.work, "r_real"))
    dump = stamp(lab.dump, root)
    tail = ["--root", root, "--layout-dump", dump, "--dry"]
    record = {"about": [], "thresholds": {}, "renders": [], "relight_pairs": []}
    missing = [r for _p, r, _v, _w in SIXTEEN if not os.path.exists(os.path.join(OUTPUT, r + "_00001_.png"))]
    if missing:
        skipped("REAL: the sixteen look-test renders", "%d of them are not in %s: %s" % (len(missing), OUTPUT, ", ".join(missing[:4])))
    else:
        for picture, render, want, words in SIXTEEN:
            rc, out = run([tool("install_redo.py"), picture, os.path.join(OUTPUT, render + "_00001_.png")] + tail, py=True)
            v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
            what = {"look3_dorm_common_keep": "the third test's Common Room can go in: nothing moved, vanished or appeared; "
                                              "it is a LOOK for the new view through its two window panes",
                    "look3_cafeteria_keep": "the third test's Cafeteria passes",
                    "look_dorm_common_B": "the first test's Common Room B is flagged for the jacket and the cup",
                    "look2_dorm_common_clean": "the second test's emptied Common Room: the cushions, the manga shelf, the "
                                               "kettle and the bag are named as gone"}.get(render, "%s on %s: %s" % (render, picture, want))
            ok("REAL: %s" % what, v[0] == want and all(w in v[1] for w in words) and rc == (1 if want == "REFUSED" else 0)
               and (want == "REFUSED" or not re.search(r"moved|gone|something new", v[1])), out)
            fig = (figures(out) or [{}])[0]
            record["renders"].append({"picture": picture, "render": render + "_00001_.png", "verdict": v[0], "figures": fig})
        # one thing on the wide floor of the approved render itself
        for what, a1, a2 in (("its own sofa cushion", "497,618,145,104", "700,966"), ("its own two cups", "1232,503,55,52", "1010,1018")):
            pasted = lab.syn("pasteplain", os.path.join(OUTPUT, "look3_dorm_common_keep_00001_.png"),
                             "real_floor_%s_a_00001_.png" % re.sub(r"\W+", "_", what), a1, a2)
            rc, out = run([tool("install_redo.py"), "dorm_common", pasted] + tail, py=True)
            v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
            ok("REAL: the third test's Common Room with %s set down on the bare floor is REFUSED: something new is on the floor" % what,
               v[0] == "REFUSED" and "something new is on the floor (" in v[1], out)
        cup = lab.syn("plaincup", os.path.join(OUTPUT, "look3_dorm_common_keep_00001_.png"), "real_rugcup_a_00001_.png", "932,865,56,70")
        rc, out = run([tool("install_redo.py"), "dorm_common", cup] + tail, py=True)
        v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
        ok("REAL: the third test's Common Room with a cup set down on the rug in front of the low table is REFUSED: "
           "something new is on the rug", v[0] == "REFUSED" and "something new is on the rug in front of the low table" in v[1], out)
        # the proof that sharpness is against revision 1, on the real render
        root3 = mkroot(os.path.join(lab.work, "r_real_rev1"))
        keep_r = os.path.join(OUTPUT, "look3_dorm_common_keep_00001_.png")
        rc, out = run([tool("install_redo.py"), "dorm_common", keep_r, "--choose", "a", "--batch", "0", "--root", root3,
                       "--layout-dump", stamp(lab.dump, root3)], py=True)
        rc2, out2 = run([tool("install_redo.py"), "dorm_common", keep_r, "--dry", "--root", root3, "--layout-dump", stamp(lab.dump, root3)], py=True)
        m = re.search(r"sharper\s+([\d.]+) times", out2)
        ok("REAL: with look3_dorm_common_keep installed and the same render offered as the candidate, step 5 passes: "
           "%s times revision 1 (against the installed picture it would read 1.0 and be refused)" % (m.group(1) if m else "?"),
           rc == 0 and verdicts(out2).get("a", ("",))[0] == "PASS" and m is not None and float(m.group(1)) >= 2.9, out + out2)
        rc, out = run([tool("install_redo.py"), "dorm_common", keep_r, "--dry", "--against-rev1", "--root", root3,
                       "--layout-dump", stamp(lab.dump, root3)], py=True)
        fig = (figures(out) or [{}])[0]
        ok("REAL: --dry --against-rev1 on that render: shift %s, sharpness %s, weakest kept thing %s; nothing installed"
           % (fig.get("shift"), fig.get("sharp"), fig.get("keep_weakest")),
           rc == 0 and fig.get("shift") == [0, 0] and "git, commit" in out, out)
        record["canary_shape"] = {"render": "look3_dorm_common_keep_00001_.png", "figures": fig}
    for place, stem, hour in PAIRS:
        day = os.path.join(REPO, "game", "images", "bg", stem + ".png")
        pic = os.path.join(REPO, "game", "images", "bg", "%s_%s.png" % (stem, hour))
        rc, out = run([tool("install_redo.py"), place, pic, "--against", day] + tail, py=True)
        v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
        fig = (figures(out) or [{}])[0]
        ok("the day and hour pair %s / %s through --against: nothing moved, nothing vanished (%s; the weakest kept "
           "thing %s)" % (stem, hour, v[0], fig.get("keep_weakest")), v[0] in ("PASS", "LOOK") and fig.get("shift") == [0, 0], out)
        record["relight_pairs"].append({"day": stem + ".png", "hour": "%s_%s.png" % (stem, hour), "verdict": v[0], "figures": fig})
    if write and not missing:
        sys.path.insert(0, TOOLS)
        code = ("import sys, json; sys.path.insert(0, %r); import redo_measure as m\n"
                "print(json.dumps(dict((k, getattr(m, k)) for k in dir(m) if k.isupper() and isinstance(getattr(m, k), (int, float, tuple)))))" % TOOLS)
        rc, out = run(["-c", code], py=True)
        record["thresholds"] = json.loads(out.strip().splitlines()[-1])
        record["about"] = [
            "tools/art/redo_measures.json -- what tools/install_redo.py measured on the renders whose answers are known "
            "(docs/UI2_DESIGN.md 5.4, 5.7), written by tools/test_art_tools.sh --write-measures on 7 Oct 2026.",
            "`thresholds` are the constants of tools/redo_measure.py as they stood (the file is a record: the tool reads its own constants).",
            "`renders` are the sixteen look-test renders, each judged in place against the game's picture of that place.",
            "Five of them are a LOOK, not a PASS, since review round 2 (7 Oct): nothing in them moved, vanished or appeared, "
            "and each has a new view through a window or a doorway, which step 6 shows in 120 px cells and does not refuse.",
            "`relight_pairs` are the eight day and hour pairs the game has; all eight line up with their day picture to 0 px, "
            "so all eight were made as relights and none is left out. The relight's own \"vanished\" rule (gone only when a "
            "thing agrees under RELIGHT_GONE_REL of what the picture does AND keeps under RELIGHT_GONE_EDGE of its edge) was "
            "set so that every one of them passes: the window at the end of the girls' corridor, lit at night, keeps 0.39 of "
            "its agreement and 43% of its edge, and is the weakest kept thing of the eight.",
            "In `figures`: shift is the whole picture's, in px; keep_weakest is [agreement against the picture's own, share "
            "of its edge] of the weakest kept thing; empty_most is [rise, levels] of the empty place that gained most; sharp "
            "is [revision 1, this render]; empty_cell_most is the same as empty_most for the 160 px part of a wide empty place "
            "(a floor) that gained most; cells_different is how many 120 px cells step 6 shows."]
        with open(MEASURES, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=1, sort_keys=True)
            f.write("\n")
        print("        wrote %s" % MEASURES)
    elif os.path.exists(MEASURES) and not missing:
        old = json.load(open(MEASURES, encoding="utf-8"))
        same = ([(r["render"], r["verdict"]) for r in old.get("renders", [])] == [(r["render"], r["verdict"]) for r in record["renders"]]
                and [(r["hour"], r["verdict"]) for r in old.get("relight_pairs", [])] == [(r["hour"], r["verdict"]) for r in record["relight_pairs"]])
        ok("the verdicts are the ones recorded in tools/art/redo_measures.json", same)


def group_yuji(lab):
    """Yuji's staged set (D57), when it is on the machine: keyed with the new edge, installed into a scratch copy."""
    need = [os.path.join(YUJI, "yuji_base.png")] + [os.path.join(YUJI, "composited", "yuji_%s.png" % e)
                                                    for e in ("happy", "serious", "sad", "angry", "surprised")]
    absent = [p for p in need if not os.path.exists(p)]
    if absent:
        skipped("REAL: Yuji's staged set through install_set.py", "absent: %s" % ", ".join(absent))
        return
    if not lab.art:
        skipped("REAL: Yuji's staged set through install_set.py", "no ComfyUI python")
        return
    stage = os.path.join(lab.work, "yuji_staged")
    rc, out = run([tool("install_set.py"), "--stage", "yuji", YUJI, "--out", stage])
    import install_set
    from pngread import load
    sizes = set()
    for e in install_set.EXPRESSIONS:
        p = os.path.join(stage, "char", "yuji_%s.png" % e)
        if os.path.exists(p):
            im = load(p)
            sizes.add((im.w, im.h, im.ch))
    ok("REAL: Yuji's six renders are keyed with the new edge and fitted to the 760x1400 canvas, with six side portraits",
       rc == 0 and sizes == {(760, 1400, 4)} and len(os.listdir(os.path.join(stage, "side"))) == 6 and out.count("keyedge") >= 6, out)
    import shlex
    ok("REAL: the commands --stage prints can be pasted: the folder with spaces in its name is quoted",
       "--images %s" % shlex.quote(YUJI) in out and " " in YUJI and "--images %s " % YUJI not in out, out)
    root = mkroot(os.path.join(lab.work, "r_yuji"))
    tb = tree_hash(root)
    rc, out = run([tool("install_set.py"), "yuji", stage, "--root", root])
    ok("REAL: as staged today the set has no overlay pictures (batch 0c is not run), so it is refused whole and "
       "nothing is written", rc == 1 and "the blink picture is missing" in out and "the talk picture is missing" in out
       and tree_hash(root) == tb, out)
    # STAND-IN overlay pictures and boxes, to prove the full install; the real ones come from batch 0c
    run(["-c", STANDIN_FX, TOOLS, stage, "yuji", "[326, 296, 86, 40]", "[348, 346, 46, 30]"])
    out = set_checks(lab, "yuji", stage, root, "REAL: Yuji's set, with STAND-IN overlay pictures", [])
    m = re.search(r"off the ramp ([\d.]+) -> ([\d.]+)", out)
    ok("REAL: his uniform's cloth is put on the ramp in the same step (%s -> %s levels off) and cloth_match.py --check "
       "--redrawn passes" % (m.group(1) if m else "?", m.group(2) if m else "?"),
       m is not None and float(m.group(2)) <= 1.5 and "cloth_match.py --check --redrawn passes" in out, out)
    calm = load(os.path.join(root, "game", "images", "char", "yuji_neutral.png"))
    same = True
    for e in install_set.EXPRESSIONS[1:]:
        d = install_set.differing_rows(calm, load(os.path.join(root, "game", "images", "char", "yuji_%s.png" % e)))
        top, bottom = install_set.figure_rows(calm)
        same = same and (d is None or d[1] < top + (bottom - top) * install_set.HEAD_SHARE)
    ok("REAL: as installed the six sprites share one body (below the head they are the calm sprite pixel for pixel)", same)
    for kind, key, box in (("blink", "eyes", [326, 296, 86, 40]), ("talk", "mouth", [348, 346, 46, 30])):
        d = install_set.differing_rows(calm, load(os.path.join(root, "game", "images", "char", "fx", "fx_yuji_%s.png" % kind)), box)
        same = same and d is None
    ok("REAL: and the two overlay pictures differ from the matched calm sprite only inside their boxes", same)
    line = [l for l in open(os.path.join(root, "game", "jjk_sprites.rpy")) if l.startswith("image yuji = ")]
    ok("REAL: jjk_sprites.rpy is regenerated with his feet measured again: %s" % (line[0].strip() if line else "?"),
       bool(line) and re.search(r"\(760, 1400\), \(\d+, 13\d\d, \d+\)", line[0]) is not None)


def main(argv):
    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    dump = opt("--layout-dump") or check_campus.DUMP
    only = opt("--only")
    work = opt("--work")
    strict, keep_work, write = ["--strict" in argv, "--keep-work" in argv, "--write-measures" in argv]
    if [a for a in argv if a not in ("--strict", "--keep-work", "--write-measures")]:
        print(__doc__); raise SystemExit(1)
    groups = [g for g in (only.split(",") if only else GROUPS)]
    for g in groups:
        if g not in GROUPS:
            raise SystemExit("--only takes: %s" % " ".join(GROUPS))
    if not os.path.exists(dump):
        print("no layout dump at %s: run tools/smoke.sh u2_dump --out <file>, then --layout-dump <file>" % dump)
        raise SystemExit(2)
    d = json.load(open(dump, encoding="utf-8"))
    if d.get("hash") != check_campus.dump_hash(check_campus.dump_files()):
        print(STALE)
        raise SystemExit(2)
    dump = os.path.abspath(dump)
    art = have_art_python()
    game_before = game_status()
    hash_before = tree_hash(REPO)
    work = work or tempfile.mkdtemp(prefix="test_art_tools_")
    os.makedirs(work, exist_ok=True)
    lab = Lab(work, dump, art)
    t0 = time.time()
    print("# test_art_tools: %s; ComfyUI's Python %s; scratch %s" % (", ".join(groups), "found" if art else "NOT found", work))
    try:
        for g in groups:
            print("## %s" % g)
            if g == "real":
                group_real(lab, write)
            else:
                globals()["group_" + g](lab)
    finally:
        ok("no file under game/, tools/fg/ or tools/bgs/ changed", tree_hash(REPO) == hash_before and game_status() == game_before,
           game_status())
        if keep_work:
            print("# the scratch folder is kept: %s" % work)
        else:
            shutil.rmtree(work, ignore_errors=True)
    bad = counts["FAIL"] + (counts["SKIPPED"] if strict else 0)
    print("# %d passed, %d failed, %d skipped%s; %.0f s" % (counts["PASS"], counts["FAIL"], counts["SKIPPED"],
                                                           " (--strict: a skip is a failure)" if strict and counts["SKIPPED"] else "",
                                                           time.time() - t0))
    for name in failed:
        print("#   FAIL  %s" % name[:150])
    print("RESULT %s" % ("FAIL" if bad else "PASS"))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
