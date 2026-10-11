"""
The tests of the art tools. Run it through tools/test_art_tools.sh.

    tools/test_art_tools.sh                        # everything that can run here
    tools/test_art_tools.sh --layout-dump <file>   # in a worktree: the local dump (tools/smoke.sh u2_dump --out <file>)
    tools/test_art_tools.sh --only redo,pose       # some groups: fixtures reader layout redo stage compose pose face set status real yuji
    tools/test_art_tools.sh --strict               # an art sitting: a SKIPPED line is a failure
    tools/test_art_tools.sh --keep-work            # leave the scratch folder, and say where it is
    tools/test_art_tools.sh --write-measures       # rewrite tools/art/redo_measures.json from the real cases (U0d only)

docs/UI2_DESIGN.md 5.4, 6.5, 10.2 (U0d2's acceptance). Nothing here touches
the game: every install goes into a scratch copy of the tree (its .rpy files,
its layout files and its pictures; no .rpyc), and the last check is that no
file under game/ changed. The scratch copy is the tree as it was BEFORE the
overhaul installed anything: whatever a real install has written (a picture,
its foreground, its light row, a layout with for_rev, the manifest) is put
back from git (before_overhaul: each picture from the commit its own manifest
row names), so the fixtures stand at revision 1 and the suite reads the same
before and after batch 0, with the install committed or not. A manifest row
of a kind the suite does not know is a SKIPPED line. A tree whose pictures
of before git cannot give (no git, a clone without its history, a row that
names a commit which is not here) is one FAIL line, and nothing is run.

  SYNTHETIC cases run anywhere the repository is: pictures made from the
  game's own by hand (shifted 12 px, enlarged 2%, recoloured, a thing rubbed
  out, a thing drawn in), test layouts, test pose rows, a doctored layout dump.
  REAL cases run when their files are on the machine, and say so when they
  are not: the sixteen look-test renders in ~/ComfyUI-Shared/output, the
  renders the owner chose from early in ~/Desktop/JJK Game images/ui2/early
  (the seven corrections' own cases, and every chosen picture that was redone
  in place or relit: none may be REFUSED), Yuji's two old blink and talk
  renders, and Yuji's staged set in ~/Desktop/JJK Game images/redo_yuji.

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
GROUPS = ("fixtures", "reader", "layout", "redo", "stage", "compose", "pose", "face", "set", "status", "real", "yuji")

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


_BEFORE = {}
_COMMIT = re.compile(r"^[0-9a-f]{7,64}$")


class _NoCommit(Exception):
    """A commit the fixtures must be read from is not in this checkout: (the commit or None, what it is)."""


def before_overhaul(repo=None):
    """The suite's fixtures stand in the tree as it was BEFORE any picture of the overhaul was installed,
    whatever is installed today: a test that installs the Common Room at revision 2, or expects a relight to be
    refused because its day picture is not in the new look, must not change its answer on the day batch 0 goes
    in. This says what to put back in a scratch copy of `repo` (this tree):

        {"files": {path under the tree: its bytes then, or None for a file that was not there},
         "pictures": {stem: its `pictures` row of the campus record then, or None},
         "places": {place: the committed layout dump of then (tools/art/game_layout.json), whose rows for that
                    place stamp() lays into a test's dump: its points and slots as they were on the old picture},
         "problems": [a thing that could not be put back, in words: a SKIPPED line, and the rest is right],
         "fatal": [why the tree of before cannot be made at all, in words: nothing is put back, nothing is run]}

    Read from git, never from the working files, and never from where a commit "ought" to be:

      A PICTURE is the file its own manifest row names: `rev1_commit` (the commit that holds the place's picture
      of before the overhaul, which every later install carries on), and for a relight, whose row has none, the
      `from_commit` of the row as the manifest FIRST held it. A row that names no commit is a picture that was
      not there (a new place, a new hour). However the install was committed (in one commit, or the pictures
      in one and the manifest in a later one: review 3), the row says the same.
      WHAT GOES WITH IT (its foreground, its light rows, its row of the campus record, the place's rows of the
      layout dump) is read from the tree as it stood just before the picture was replaced: the parent of the
      commit in which the picture file stopped being what it was (or first appeared), found in that file's own
      history; HEAD while the install is not committed.
      A LAYOUT FILE that carries for_rev is its newest commit without for_rev.
      The manifest itself is taken away.

    A commit git does not hold is NOT a file that was not there: a checkout without its history (a shallow
    clone) or a row naming a commit of another clone is `fatal`, in one line (review 3: such a clone took the
    pictures away and the first test fell over with a traceback). With no manifest and no such file (the tree
    before batch 0) nothing is put back and git is not asked."""
    repo = os.path.abspath(repo or REPO)
    if repo in _BEFORE:
        return _BEFORE[repo]
    out = _BEFORE[repo] = {"files": {}, "pictures": {}, "places": {}, "problems": [], "fatal": []}
    lay_dir = os.path.join(repo, "game", "layout")
    man = check_campus.load_manifest(repo).get("pictures") or {}
    names = sorted(os.listdir(lay_dir)) if os.path.isdir(lay_dir) else []
    stamped = []
    for n in names:
        if re.match(r"(hot|view|area|map)_\w+\.json$", n):
            try:
                if "for_rev" in json.load(open(os.path.join(lay_dir, n), encoding="utf-8")):
                    stamped.append(n)
            except ValueError:
                pass
    lights = [n for n in names if re.match(r"light_\w+\.json$", n)]
    if not man and not stamped and not lights and not os.path.exists(os.path.join(lay_dir, "pictures.json")):
        return out

    def git(*args):
        p = subprocess.run(["git", "-C", repo] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout

    if git("rev-parse", "HEAD")[0] != 0:
        out["fatal"].append("pictures of the overhaul are installed in this tree and it is not a git checkout")
        return out
    shallow = git("rev-parse", "--is-shallow-repository")[1].decode().strip() == "true"
    held = {}

    def need(commit, what):
        if commit not in held:
            held[commit] = git("cat-file", "-e", commit + "^{commit}")[0] == 0
        if not held[commit]:
            raise _NoCommit(commit, what)

    def show(commit, rel, what):
        """The file at a commit, or None when that commit holds no such file. The commit must be here."""
        need(commit, what)
        code, blob = git("show", "%s:%s" % (commit, rel))
        return blob if code == 0 else None

    def blob_id(commit, rel):
        code, got = git("rev-parse", "--verify", "-q", "%s:%s" % (commit, rel))
        return got.decode().strip() if code == 0 else None

    def fatal(e):
        commit, what = e.args
        words = what if commit is None else "git does not hold %s (%s): %s" % (
            "the parent of commit %s" % commit[:-1][:12] if commit.endswith("^") else "commit %s" % commit[:12], what,
            "this checkout's history is shallow (git fetch --unshallow brings the rest)" if shallow
            else "it is not in this checkout (was the picture installed in another clone?)")
        if words not in out["fatal"]:
            out["fatal"].append(words)

    mrel = "game/layout/pictures.json"
    firsts = {}

    def first_row(key):
        """A row as the manifest first held it: the manifest's history, oldest first, then the file on disk."""
        if not firsts:
            code, log = git("log", "--reverse", "--format=%H", "--", mrel)
            for c in log.decode().split():
                try:
                    rows = json.loads(git("show", "%s:%s" % (c, mrel))[1] or b"{}").get("pictures") or {}
                except ValueError:
                    rows = {}
                for k, r in rows.items():
                    firsts.setdefault(k, r)
            for k, r in man.items():
                firsts.setdefault(k, r)
        return firsts.get(key)

    def base_of(rel, then_id, what):
        """The tree as it stood just before the overhaul reached this file: the parent of the commit in which
        the file stopped being what it was then (`then_id`: git's name for those bytes; None: it was not
        there), read from the file's own history; "HEAD" while that is not committed."""
        commits = git("log", "--format=%H", "--", rel)[1].decode().split()      # the newest first
        if then_id is None:
            if not commits:
                return "HEAD"
            replaced = commits[-1]
        else:
            ids = [blob_id(c, rel) for c in commits]
            if then_id not in ids:
                raise _NoCommit(None, "the history of %s in this checkout does not hold %s" % (rel, what))
            if ids.index(then_id) == 0:
                return "HEAD"
            replaced = commits[ids.index(then_id) - 1]
        need(replaced + "^", "the tree as it stood just before the overhaul reached %s" % rel)
        return replaced + "^"

    # the pictures, each from the commit its own row names
    bases = {}
    for k in sorted(man):
        row = man[k]
        if not (isinstance(row, dict) and "kind" in row):
            continue
        rel = "game/images/bg/%s.png" % k
        try:
            if row.get("kind") == "relight":
                first = first_row(k) or row
                if first.get("rev", 2) != 2:
                    raise _NoCommit(None, "the manifest's history in this checkout does not reach the first install of "
                                          "%s (the oldest row it holds is revision %s)" % (k, first.get("rev")))
                commit, field, named = first.get("from_commit"), "from_commit", "the from_commit of its first row"
            else:
                commit, field, named = row.get("rev1_commit"), "rev1_commit", "its rev1_commit"
            if commit is not None and not _COMMIT.match(str(commit)):
                raise _NoCommit(None, "the manifest's row for %s names no commit for its picture of before the overhaul "
                                      "(its %s is %r)" % (k, field, commit))
            what = "%s's picture of before the overhaul, which the manifest names: %s" % (k, named)
            blob = show(commit, rel, what) if commit else None
            if commit and blob is None:
                raise _NoCommit(None, "commit %s holds no %s, though the manifest names it (%s)" % (commit[:12], rel, named))
            bases[k] = base_of(rel, blob_id(commit, rel) if commit else None, what)
            out["files"][rel] = blob
        except _NoCommit as e:
            fatal(e)

    # what goes with each picture, from the tree as it stood just before the picture was replaced
    records, dumps = {}, {}
    try:
        for k in sorted(bases):
            base = bases[k]
            if base not in records:
                try:
                    records[base] = json.loads(show(base, "tools/bgs/campus.json", "the campus record of then") or b"{}").get("pictures") or {}
                except ValueError:
                    records[base] = {}
            out["pictures"][k] = records[base].get(k)
        for k in sorted(man):
            row = man[k]
            if isinstance(row, dict) and "kind" in row:
                continue
            if k.startswith("light_"):
                continue        # a place's light rows are one file, put back below
            if not k.startswith("fg_"):
                out["problems"].append("the manifest row %r is of a kind the suite's fixtures do not know how to put back "
                                       "(tools/test_art_tools.py, before_overhaul)" % k)
                continue
            of = row.get("of") if isinstance(row, dict) else None
            if of in man and of not in bases:
                continue        # its picture could not be found: said above
            rel = "game/images/fg/%s.png" % k
            out["files"][rel] = show(bases.get(of, "HEAD"), rel, "the foreground of then")
        out["files"][mrel] = None
        for n in lights:
            # light_<place>.json holds a row for each hour: it is as it was before the place's FIRST picture went in
            key = n[:-5]
            rows = [key] if key in man else [k for k in sorted(man) if k in (key + "_evening", key + "_night")]
            ofs = [man[k].get("of") for k in rows if isinstance(man[k], dict)]
            if ofs and all(o in man and o not in bases for o in ofs):
                continue
            base = next((bases[o] for o in ofs if o in bases), "HEAD")
            out["files"]["game/layout/" + n] = show(base, "game/layout/" + n, "the light rows of then")
        where = dict((k, bases[k]) for k in bases)
        for n in stamped:
            rel = "game/layout/" + n
            found, newer = None, None       # newer: the oldest commit seen in which the file carries for_rev
            for c in ["HEAD"] + git("log", "--format=%H", "--", rel)[1].decode().split():
                code, blob = git("show", "%s:%s" % (c, rel))
                try:
                    if code == 0 and "for_rev" not in json.loads(blob):
                        found = blob
                        break
                except ValueError:
                    continue
                if code == 0:
                    newer = c
            if found is None and shallow:
                raise _NoCommit(None, "this checkout's history is shallow (git fetch --unshallow brings the rest): it cannot "
                                      "say what %s was before the overhaul" % rel)
            out["files"][rel] = found
            m = re.match(r"(hot|view)_(\w+)\.json$", n)
            if m and m.group(2) not in where:
                base = "HEAD" if newer in (None, "HEAD") else newer + "^"
                if base != "HEAD":
                    need(base, "the tree as it was before %s was installed" % rel)
                where.setdefault(m.group(2), base)
        for key in sorted(where):
            base = where[key]
            if base not in dumps:
                try:
                    dumps[base] = json.loads(show(base, "tools/art/game_layout.json", "the layout dump of then") or b"null")
                except ValueError:
                    dumps[base] = None
            if not isinstance(dumps[base], dict):
                out["problems"].append("git has no layout dump at %s to give %s's points as they were" % (base[:10], key))
                continue
            # the dump's tables are keyed by the place, the manifest by its picture: My Room is `dorm`, your_room.png
            place = next((p.get("key") for p in dumps[base].get("places") or [] if isinstance(p, dict)
                          and p.get("file") == "images/bg/%s.png" % key), key)
            out["places"][place] = dumps[base]
    except _NoCommit as e:
        fatal(e)
    if out["fatal"]:
        for part in ("files", "pictures", "places"):
            out[part].clear()       # a tree that cannot be made is not made in part
    return out


def fixtures_line(then):
    """One plain line for a tree whose fixtures cannot be made (before_overhaul()'s `fatal`), or None."""
    fatal = then.get("fatal") or []
    if not fatal:
        return None
    return ("the tree as it was before the overhaul cannot be made here: %s%s. Nothing was run: run the tests in a git "
            "checkout that holds the project's whole history"
            % (fatal[0], "; and %d more of the kind" % (len(fatal) - 1) if len(fatal) > 1 else ""))


def mkroot(path):
    """A scratch copy of the tree: the .rpy files, the layout files, the pictures (cloned, not copied, where the
    disk can), the foreground outlines and the campus record. Never a .rpyc. What the overhaul has installed
    is put back to what it was before (before_overhaul): the fixtures stand at revision 1. Where that tree
    cannot be made (before_overhaul's `fatal`) no copy is made at all."""
    then = before_overhaul()
    if then["fatal"]:
        raise SystemExit("mkroot: " + fixtures_line(then))
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(os.path.join(path, "game"))
    os.makedirs(os.path.join(path, "tools", "bgs"))
    for n in sorted(os.listdir(os.path.join(REPO, "game"))):
        if n.endswith(".rpy"):
            shutil.copyfile(os.path.join(REPO, "game", n), os.path.join(path, "game", n))
    for sub in ("layout", "images"):
        # -L: a link is never copied as a link (an install into the copy would write through it)
        src, dst = os.path.realpath(os.path.join(REPO, "game", sub)), os.path.join(path, "game", sub)
        if subprocess.run(["cp", "-cRL", src, dst], stderr=subprocess.PIPE).returncode != 0:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    shutil.copytree(os.path.join(REPO, "tools", "fg"), os.path.join(path, "tools", "fg"))
    shutil.copyfile(os.path.join(REPO, "tools", "bgs", "campus.json"), os.path.join(path, "tools", "bgs", "campus.json"))
    for rel, blob in then["files"].items():
        dst = os.path.join(path, *rel.split("/"))
        if os.path.lexists(dst):
            os.remove(dst)              # never written through: a cloned file is replaced, not opened
        if blob is not None:
            with open(dst, "wb") as f:
                f.write(blob)
    if then["pictures"]:
        rp = os.path.join(path, "tools", "bgs", "campus.json")
        text = open(rp, encoding="utf-8").read()
        rec = json.loads(text)
        for stem, row in then["pictures"].items():
            if row is None:
                rec.get("pictures", {}).pop(stem, None)
            else:
                rec.setdefault("pictures", {})[stem] = row
        if rec != json.loads(text):     # a record that is the same is left byte for byte as it was
            with open(rp, "w", encoding="utf-8") as f:
                json.dump(rec, f, indent=1, ensure_ascii=False)
                f.write("\n")
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
    # the scratch tree stands before the overhaul (before_overhaul): so does its dump, place by place
    for place, then in before_overhaul()["places"].items():
        for key, val in d.items():
            if isinstance(val, dict) and isinstance(then.get(key), dict):
                if place in then[key]:
                    val[place] = then[key][place]
                else:
                    val.pop(place, None)
            elif isinstance(val, list) and isinstance(then.get(key), list) and all(isinstance(v, str) for v in val + then[key]):
                if place in val and place not in then[key]:
                    val.remove(place)
                elif place in then[key] and place not in val:
                    val.append(place)
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
box = [int(v) for v in args[0].split(",")] if args and "," in args[0] and ";" not in args[0] else None
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
elif cmd == "glass":   # a new view behind glass: each pane (x,y,w,h;x,y,w,h) shows another drawing altogether
    out = look(a)
    for part in args[0].split(";"):
        x, y, w, h = [int(v) for v in part.split(",")]
        d = ImageDraw.Draw(out); d.rectangle([x, y, x + w - 1, y + h - 1], fill=(222, 230, 240))
        for k in range(x + 20, x + w, 34):          # a timbered house outside: dark posts and rails on a pale wall
            d.rectangle([k, y, min(k + 6, x + w - 1), y + h - 1], fill=(44, 38, 46))
        for k in range(y + 14, y + h, 34):
            d.rectangle([x, k, x + w - 1, min(k + 6, y + h - 1)], fill=(44, 38, 46))
elif cmd == "refloor":  # a floor drawn again: its polygon (x,y;x,y;...) gets boards that run the other way, and sunlight
    out = look(a); poly = [tuple(int(v) for v in q.split(",")) for q in args[0].split(";")]
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    px = np.asarray(a)[np.asarray(m) > 0]
    base = tuple(int(v) for v in np.median(px, axis=0))
    fl = Image.new("RGB", (W, H), base); d = ImageDraw.Draw(fl)
    vx, vy = (min(xs) + max(xs)) // 2, min(ys) - 420            # the boards run toward the back wall
    for k in range(min(xs) - 900, max(xs) + 900, 46):
        d.line([vx + (k - vx) * 0.25, min(ys) - 4, k, H + 4], fill=tuple(max(0, v - 46) for v in base), width=3)
    sx = min(xs) + (max(xs) - min(xs)) // 3                     # a window's light across it, with its frame's shadow
    d.polygon([(sx, min(ys) + 12), (sx + 420, min(ys) + 12), (sx + 520, H - 14), (sx - 60, H - 14)],
              fill=tuple(min(255, v + 70) for v in base))
    for k in (0.33, 0.66):
        d.line([sx + 420 * k, min(ys) + 12, sx - 60 + 580 * k, H - 14], fill=tuple(max(0, v - 20) for v in base), width=9)
    d.line([sx - 30, (min(ys) + H) // 2, sx + 470, (min(ys) + H) // 2], fill=tuple(max(0, v - 20) for v in base), width=9)
    out.paste(fl, (0, 0), m)
    if len(args) > 1:                                           # and, with it, a thing of the room slid (x,y,w,h,d)
        x, y, w, h, dd = [int(v) for v in args[1].split(",")]
        src = out.copy() if len(args) > 2 and args[2] == "floor-too" else look(a)   # the new floor slid with it, or not
        out.paste(src.crop((x - 24 - dd, y - 24, x + w + 24 - dd, y + h + 24)), (x - 24, y - 24))
elif cmd == "inside":  # a thing drawn differently inside its outline: the box, 3 px in, lighter and turned over
    out = look(a); x, y, w, h = box
    part = out.crop((x + 3, y + 3, x + w - 3, y + h - 3)).transpose(Image.FLIP_TOP_BOTTOM)
    out.paste(Image.blend(part, Image.new("RGB", part.size, (236, 232, 222)), 0.45), (x + 3, y + 3))
elif cmd == "bag":     # a flat dark thing set down (a bag, a mat): an ellipse with no pattern and no rim
    out = look(a); x, y, w, h = box
    ImageDraw.Draw(out).ellipse([x, y, x + w, y + h], fill=(34, 30, 36))
elif cmd == "mat":     # a flat pale thing laid down (a mat, a sheet of card): one colour, no pattern and no rim
    out = look(a); x, y, w, h = box
    ImageDraw.Draw(out).rectangle([x, y, x + w, y + h], fill=(214, 204, 180))
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
def group_fixtures(lab):
    """before_overhaul() itself, on small git trees made here: what the suite's own fixtures are built from once
    a picture of the overhaul is installed. Plain Python and git; no picture is read."""
    if subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        skipped("the fixtures: before_overhaul() on small git trees", "no git")
        return

    def git(repo, *args):
        p = subprocess.run(["git", "-C", repo, "-c", "user.name=test_art_tools", "-c", "user.email=test@example.invalid",
                            "-c", "commit.gpgsign=false", "-c", "protocol.file.allow=always"] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.stdout.decode("utf-8", "replace").strip()

    def put(repo, rel, data):
        path = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data if isinstance(data, bytes) else (json.dumps(data, sort_keys=True) + "\n").encode())

    hot_then = {"spots": {"zz_door": [100, 200]}}
    record_then = {"chosen": None, "source": "the picture of before"}

    def tree(name):
        """A tree before the overhaul: a room (the place zzplace, the picture zzroom.png) with an evening picture,
        a foreground cut AGAIN in a later commit than the picture's own, a layout, a record and a dump."""
        repo = os.path.join(lab.work, "fx_" + name)
        os.makedirs(repo)
        git(repo, "init", "-q")
        put(repo, "game/images/bg/zzroom.png", b"the room, before the overhaul")
        put(repo, "game/images/bg/zzroom_evening.png", b"its evening, before the overhaul")
        put(repo, "game/images/fg/fg_zzplace.png", b"the foreground, first cut")
        put(repo, "game/layout/hot_zzplace.json", hot_then)
        put(repo, "tools/bgs/campus.json", {"pictures": {"zzroom": record_then}})
        put(repo, "tools/art/game_layout.json", {"hash": "then", "exits": {"zzplace": ["as it was"]},
                                                 "places": [{"key": "zzplace", "file": "images/bg/zzroom.png"}]})
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "the room")
        first = git(repo, "rev-parse", "HEAD")
        put(repo, "game/images/fg/fg_zzplace.png", b"the foreground, cut again before the overhaul")
        put(repo, "tools/art/game_layout.json", {"hash": "then, the last dump before the overhaul", "exits": {"zzplace": ["as it was"]},
                                                 "places": [{"key": "zzplace", "file": "images/bg/zzroom.png"}]})
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "the foreground cut again, and a new dump")
        return repo, first

    def install(repo, first, rev1="given"):
        """What an install writes (install_redo.py), by hand: the room composed again, its evening relit, and a
        place that had no picture."""
        put(repo, "game/images/bg/zzroom.png", b"the room, in the new look")
        put(repo, "game/images/bg/zzroom_evening.png", b"its evening, relit")
        put(repo, "game/images/bg/zznew.png", b"a place that had no picture")
        put(repo, "game/images/fg/fg_zzplace.png", b"the foreground, cut from the new picture")
        put(repo, "game/layout/hot_zzplace.json", dict(hot_then, for_rev=2))
        put(repo, "game/layout/view_zzplace.json", {"slots": {}, "for_rev": 2})
        put(repo, "game/layout/light_zzplace.json", {"": ["#ffffff", 0, 1, 0.5], "evening": ["#ffd0a0", 0, 1, 0.5]})
        put(repo, "game/layout/pictures.json", {"pictures": {
            "zzroom": {"rev": 2, "kind": "composed", "rev1_commit": first if rev1 == "given" else rev1, "from_commit": first},
            "zzroom_evening": {"rev": 2, "kind": "relight", "of": "zzroom", "of_rev": 2, "from_commit": first},
            "zznew": {"rev": 2, "kind": "composed"},
            "fg_zzplace": {"of": "zzroom", "of_rev": 2}, "light_zzplace": {"of": "zzroom", "of_rev": 2},
            "light_zzplace_evening": {"of": "zzroom_evening", "of_rev": 2}}})
        put(repo, "tools/bgs/campus.json", {"pictures": {"zzroom": {"chosen": "the new render"}, "zznew": {"chosen": "a render"}}})
        put(repo, "tools/art/game_layout.json", {"hash": "now", "exits": {"zzplace": ["as the new layout has it"]},
                                                 "places": [{"key": "zzplace", "file": "images/bg/zzroom.png"}]})

    want = {"game/images/bg/zzroom.png": b"the room, before the overhaul",
            "game/images/bg/zzroom_evening.png": b"its evening, before the overhaul",
            "game/images/bg/zznew.png": None,
            "game/images/fg/fg_zzplace.png": b"the foreground, cut again before the overhaul",
            "game/layout/hot_zzplace.json": (json.dumps(hot_then, sort_keys=True) + "\n").encode(),
            "game/layout/view_zzplace.json": None, "game/layout/light_zzplace.json": None, "game/layout/pictures.json": None}

    def wrong(then):
        """What is not as it was before the overhaul, in words; [] when all of it is."""
        bad = ["%s: %r" % (rel, (then["files"].get(rel, "not named") or b"")[:48]) for rel in sorted(want)
               if rel not in then["files"] or then["files"][rel] != want[rel]]
        bad += ["%s is named and should not be" % rel for rel in sorted(then["files"]) if rel not in want]
        if then["pictures"] != {"zzroom": record_then, "zzroom_evening": None, "zznew": None}:
            bad.append("the record's rows: %r" % then["pictures"])
        if (then["places"].get("zzplace") or {}).get("hash") != "then, the last dump before the overhaul":
            bad.append("the dump for zzplace: %r" % (then["places"].get("zzplace") or {}).get("hash"))
        return bad + ["problem: " + w for w in then["problems"]] + ["fatal: " + w for w in then["fatal"]]

    repo, first = tree("one")
    install(repo, first)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "the install, in one commit")
    got = wrong(before_overhaul(repo))
    ok("the fixtures, an install committed in ONE commit: each picture is the one its manifest row names (rev1_commit; "
       "a relight's first from_commit), a place that had no picture has none, and what goes with a picture (its "
       "foreground as last cut, its light rows, its layout without for_rev, its row of the record, the dump) is as it "
       "stood just before the picture was replaced", not got, "\n".join(got))

    repo2, first2 = tree("two")
    install(repo2, first2)
    git(repo2, "add", "game/images")
    git(repo2, "commit", "-q", "-m", "the install: the pictures")
    git(repo2, "add", "-A")
    git(repo2, "commit", "-q", "-m", "the install: the manifest and the rest")
    got = wrong(before_overhaul(repo2))
    ok("the fixtures, the same install committed as the PICTURES FIRST and the manifest after: the same tree of before "
       "(review 3: read from the parent of the manifest's first commit, these were the NEW pictures, and nothing said so)",
       not got and len(git(repo2, "log", "--format=%H").split()) == 4, "\n".join(got))

    repo3, first3 = tree("open")
    install(repo3, first3)
    got = wrong(before_overhaul(repo3))
    ok("the fixtures, the same install NOT committed yet: the same tree of before, read from HEAD", not got, "\n".join(got))

    shallow = os.path.join(lab.work, "fx_shallow")
    git(lab.work, "clone", "-q", "--depth", "1", "file://" + repo, shallow)
    then = before_overhaul(shallow)
    line = fixtures_line(then) or ""
    ok("the fixtures, in a clone WITHOUT ITS HISTORY (depth 1): a commit git does not hold is not a file that was not "
       "there. Nothing is put back or taken away, and one plain line names the commit and says the history is shallow",
       os.path.exists(os.path.join(shallow, "game", "layout", "pictures.json")) and bool(then["fatal"])
       and then["files"] == {} and then["pictures"] == {} and then["places"] == {}
       and any("git does not hold commit %s (zzroom's picture of before the overhaul" % first[:12] in w for w in then["fatal"])
       and "git does not hold" in line and "history is shallow" in line and "\n" not in line
       and line.startswith("the tree as it was before the overhaul cannot be made here"), line + "\n" + json.dumps(then["fatal"]))

    bare = os.path.join(lab.work, "fx_nogit")
    shutil.copytree(repo, bare, ignore=shutil.ignore_patterns(".git"))
    then = before_overhaul(bare)
    ok("the fixtures, in a copy that is no git checkout: one plain line, and nothing put back or taken away",
       then["files"] == {} and len(then["fatal"]) == 1 and "it is not a git checkout" in (fixtures_line(then) or ""), fixtures_line(then))

    repo4, first4 = tree("copyrow")
    install(repo4, first4, rev1="not committed (a copy)")
    git(repo4, "add", "-A")
    git(repo4, "commit", "-q", "-m", "an install whose row names no commit")
    then = before_overhaul(repo4)
    ok("the fixtures, a manifest row whose rev1_commit is no commit (\"not committed (a copy)\"): its picture of before "
       "cannot be taken from git, and the line says which row", then["files"] == {}
       and "the manifest's row for zzroom names no commit" in (fixtures_line(then) or ""), fixtures_line(then))

    repo5, first5 = tree("pose")
    install(repo5, first5)
    rows = json.load(open(os.path.join(repo5, "game", "layout", "pictures.json")))
    rows["pictures"]["pose_zz_megumi"] = {"of": "zzroom", "of_rev": 2}
    put(repo5, "game/layout/pictures.json", rows)
    then = before_overhaul(repo5)
    ok("the fixtures, a manifest row of a kind they do not know (a pose's): a SKIPPED line names it, and the rest is "
       "still put back", len(then["problems"]) == 1 and "pose_zz_megumi" in then["problems"][0] and not then["fatal"]
       and then["files"].get("game/images/bg/zzroom.png") == want["game/images/bg/zzroom.png"], json.dumps(then["problems"] + then["fatal"]))
    ok("the fixtures of this tree itself: %s" % ("nothing of the overhaul is installed here, and git is not asked"
                                                  if not before_overhaul()["files"] else
                                                  "%d files are put back or taken away, from git" % len(before_overhaul()["files"])),
       not before_overhaul()["fatal"], fixtures_line(before_overhaul()))


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

    def within(poly, x, y):
        hit = False
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / float(y1 - y0):
                hit = not hit
        return hit

    floor = [z for z in json.load(open(os.path.join(TOOLS, "bgs", "keep", "cafeteria.json"), encoding="utf-8"))["empty"]
             if z["name"] == "the floor"][0]["poly"]
    feet = sorted(set((x, y) for _n, x, y in lay.slot_feet("cafeteria")))
    out_of = [pt for pt in feet if not within(floor, pt[0], pt[1])]
    ok("the Cafeteria's keep list: its floor zone holds every place people stand (%d of %d; a thing set down where a "
       "row stands is refused only inside it)" % (len(feet) - len(out_of), len(feet)), len(feet) == 9 and not out_of, out_of)
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
    world = lay.d.get("world") or {}
    nohome = game_layout.Layout(dict(lay.d, world=dict(world, asleep={"weekday": ["gojo", "megumi"], "weekend": []})))
    ok("asleep() is the game's world_asleep: someone on the list who has no home (Gojo, were he on it) is asleep "
       "nowhere, and Megumi beside him on the same list still is",
       "gojo" not in (world.get("homes") or {}) and nohome.asleep("gojo", "Mon", "Night") is False
       and nohome.asleep("megumi", "Mon", "Night") is True,
       (nohome.asleep("gojo", "Mon", "Night"), nohome.asleep("megumi", "Mon", "Night")))
    # rooms lit at Night (U0n, 5.7a): the dump's two top-level keys and their readers
    late_cells = (lay.where("megumi", "Sun", "Night"), lay.asleep("megumi", "Sun", "Night"), lay.where("megumi", "Sat", "Night"),
                  lay.asleep("megumi", "Mon", "Night"),
                  lay.where("toge", "Wed", "Night"), lay.where("toge", "Thu", "Night"), lay.where("panda", "Wed", "Night"))
    ok("game_layout.py: where() knows the game's late table (the dump's `late`, WORLD_LATE): Megumi is in the Library "
       "on a Sunday Night, awake, and in his own room on a Saturday's (and asleep there on a Monday's, as before); Toge is there on a Wednesday Night and at home on "
       "a Thursday's, and Panda is at home on both",
       late_cells == ("library", False, "megumi_room", True, "library", "senpai_room", "senpai_room"), late_cells)
    lit_rooms = lay.lit_places()
    ok("lit_places() and lit_file() read the game's lit table (the dump's `lit_planned`, WORLD_LIT): the Library and "
       "My Room are in it (My Room's file is your_room_lit.png), every one is indoors, and a yard is not",
       lit_rooms is not None and "library" in lit_rooms and "dorm" in lit_rooms and lay.lit_file("dorm") == "images/bg/your_room_lit.png"
       and all(lay.indoor(p) for p in lit_rooms) and "courtyard" not in lit_rooms and lay.lit_file("courtyard") is None
       and all(lay.lit_file(p) == "images/bg/%s_lit.png" % lay.bg_stem(p) for p in lit_rooms), lit_rooms)
    import make_redo_workflow
    ok("the workflow maker's own list of lit rooms (make_redo_workflow.LIT_ROOMS, which art_batch.py shares) is the game's "
       "table as the dump holds it: a room added to WORLD_LIT, or taken out, is seen here",
       lit_rooms is not None and sorted(make_redo_workflow.LIT_ROOMS) == sorted(lit_rooms),
       [make_redo_workflow.LIT_ROOMS, lit_rooms])
    not_lit = [p["key"] for p in lay.d["places"] if p["key"] not in (lit_rooms or [])][0]
    ok("periods_showing(place, \"lit\") is Night and nothing else for a room of the lit table, and no hour at all for a "
       "place that is not in it (%s); a room's night and evening pictures show when they did" % not_lit,
       lay.periods_showing("library", "lit") == {"Night"} and lay.periods_showing(not_lit, "lit") == set()
       and "Night" in lay.periods_showing("library", "night") and lay.periods_showing("library", "evening") == {"Evening"}
       and "lit" in game_layout.HOURS, (lay.periods_showing("library", "lit"), lay.periods_showing(not_lit, "lit")))
    before_n = game_layout.Layout(dict((k, v) for k, v in lay.d.items() if k not in ("lit_planned", "late")))
    ok("a dump written before U0n (neither key) answers None (\"not known\") from lit_places() and late(); where() then "
       "answers from the routine alone (Megumi at home on a Sunday Night) and a lit picture is counted for Night in any room",
       (before_n.lit_places(), before_n.late(), before_n.where("megumi", "Sun", "Night"), before_n.lit_file("library"),
        before_n.periods_showing(not_lit, "lit")) == (None, None, "megumi_room", None, {"Night"}))
    swapped = game_layout.Layout(dict(lay.d, late={"megumi": {"place": "library", "days": ["Sat"]}}))
    ok("where() follows the dump's table, not a list of its own: with Megumi's late Night moved to Saturday he is in the "
       "Library then and at home on Sunday; and the away table still wins over a late stay",
       (swapped.where("megumi", "Sat", "Night"), swapped.where("megumi", "Sun", "Night")) == ("library", "megumi_room")
       and game_layout.Layout(dict(lay.d, late={"nobara": {"place": "library", "days": ["Sun"]}},
                                   world=dict(world, away={"nobara": {"Sun Night": "harajuku"}}))).where("nobara", "Sun", "Night") == "harajuku")
    rc, out = run([tool("game_layout.py"), "--layout-dump", lab.dump])
    ok("python3 tools/game_layout.py says how many rows of each of the two tables the dump holds",
       rc == 0 and re.search(r"lit picture \(lit_planned\): %d rows" % len(lit_rooms or []), out) is not None
       and re.search(r"\(late\): %d rows" % len(lay.late() or {}), out) is not None, out)
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

    # check_layout.py: the game's own counting, the numbers it types, and its negative tests (10.2, U0d3)
    import check_layout
    for what, good in check_layout.shape_cases():
        ok("check_layout.py counts with the game's own text (the block between the two hot_shape: marker lines of "
           "game/sb_hotspots.rpy), on the three shapes of tools/smoke/hot_shape_cases.json: %s" % what, good)
    block = check_layout.shape_block()
    ns = {}
    exec(compile(block.replace("return total", "return total + 1.0", 1), "a changed block", "exec"), ns)
    cases_file = json.load(open(os.path.join(TOOLS, "smoke", "hot_shape_cases.json"), encoding="utf-8"))
    ok("and the day that text differs the answers differ: with one line of the block changed (an area one px2 larger) "
       "the three shapes no longer give the answers the cases file holds",
       "return total" in block and
       dict((k, dict(v)) for k, v in ns["hot_shape_count"](cases_file["shapes"], dict((k, tuple(v)) for k, v in cases_file["points"].items()),
                                                           tuple(cases_file["size"]), cases_file["grid"]).items()) != cases_file["expect"])
    bad = [what for what, good in check_layout.pinned() if not good]
    ok("every number check_layout.py types itself (the two-line banner, a yard's exit heights, the caption's ring, the "
       "hover label's size) still stands in the line of the game or harness it is from (%d lines)" % len(check_layout.PINNED),
       not bad, "\n".join(bad))
    folder = os.path.join(lab.work, "layout_cases")
    cl = [tool("check_layout.py")]
    for k, (name, files, rule, words, also) in enumerate(check_layout.cases()):
        paths = check_layout.write_case(files, os.path.join(folder, "c%02d" % k))
        rc, out = run(cl + [os.path.dirname(paths[0]), "--layout-dump", lab.dump])
        refused = [l for l in out.splitlines() if l.startswith("REFUSED")]
        tags = set(re.findall(r"\[([a-z-]+)\]", " ".join(l.split(":")[0] for l in refused)))
        last = out.strip().splitlines()[-1] if out.strip() else ""
        if rule is None:
            ok("check_layout.py: %s (exit 0, nothing refused)" % name, rc == 0 and not refused and ": PASS (" in last, out)
        else:
            ok("check_layout.py refuses, by name [%s], %s" % (rule, name),
               rc == 1 and any("[%s]" % rule in l.split(":")[0] and words in l for l in refused)
               and tags <= set((rule,) + tuple(also)) and "REFUSED (" in last, out)
    # the two rules that read what the dump gained with U0d3 (lock_labels, frames.tag_*): each case lays its own
    # test numbers over the dump, so the lines read the same on a dump written before and after
    os.makedirs(os.path.join(lab.work, "layout_dumps"))
    for k, (name, files, patch, want, words) in enumerate(check_layout.dump_cases()):
        paths = check_layout.write_case(files, os.path.join(folder, "d%02d" % k))
        dp = os.path.join(lab.work, "layout_dumps", "d%02d.json" % k)
        json.dump(check_layout.patched(json.load(open(lab.dump, encoding="utf-8")), patch), open(dp, "w"))
        rc, out = run(cl + [os.path.dirname(paths[0]), "--layout-dump", dp])
        what = ("refuses, by name [%s], %s" % (want, name) if want and not want.startswith("REPORT")
                else "%s (exit 0, nothing refused%s)" % (name, ", [%s] reported" % want[7:] if want else ""))
        ok("check_layout.py %s" % what, check_layout.dump_case_ok(want, words, out.splitlines(), rc), out)
    one = check_layout.write_case(check_layout.base_courtyard(), os.path.join(folder, "files"))
    rc, out = run(cl + sorted(one) + ["--layout-dump", lab.dump, "--quiet"])
    ok("it reads a layout as files named one by one, as well as a folder; it REPORTS, and does not refuse, the part "
       "of a shape inside the toast lane; and --quiet leaves the NOTE lines out",
       rc == 0 and "[in-lane]: shape 'go_courtyard__training_yard'" in out and "NOTE" not in out and "REFUSED" not in out, out)
    high = check_layout.base_courtyard()
    high["hot_courtyard"]["shapes"]["gateway"] = [[[600, 300], [690, 60], [780, 300], [790, 560], [590, 560]]]
    high["hot_courtyard"]["shapes"].pop("straw_posts")
    high["hot_courtyard"]["keep_tile"] = {"straw_posts": "a test: the posts are not painted on this picture"}
    rc, out = run(cl + [os.path.dirname(check_layout.write_case(high, os.path.join(folder, "high"))[0]), "--layout-dump", lab.dump])
    ok("it REPORTS, and does not refuse, the part of a shape above y 92 (no shape takes the pointer there), and prints "
       "how many hotspots keep a button in the place, and why",
       rc == 0 and "[above-hud]: shape 'gateway'" in out and "above y 92" in out
       and "[keep-tile]: 1 hotspot keeps a button in Courtyard: straw_posts (a test: the posts are not painted on this picture)" in out, out)
    front = check_layout.base_courtyard()
    front["check_courtyard"] = {"front": ["straw_posts"], "objects": {"spot_vend": [1556, 616, 88, 148]}}
    rc, out = run(cl + [os.path.dirname(check_layout.write_case(front, os.path.join(folder, "front"))[0]), "--layout-dump", lab.dump])
    rc2, out2 = run(cl + [os.path.dirname(check_layout.write_case(check_layout.base_courtyard(), os.path.join(folder, "front2"))[0]),
                          "--layout-dump", lab.dump, "--front", "straw_posts"])
    ok("a PLANNED foreground object is read as front from check_<place>.json's \"front\" list, or from --front: the "
       "planned straw posts, named front, are then asked for their object's box like any front shape",
       rc == 1 and rc2 == 1 and all("[front-shape]: shape 'straw_posts'" in o for o in (out, out2)), out + out2)
    beside = [f for f in check_layout.write_case(front, os.path.join(folder, "front3")) if not os.path.basename(f).startswith("check_")]
    rc, out = run(cl + ["--layout"] + sorted(beside) + ["--layout-dump", lab.dump])
    ok("and when only the hot_ and view_ files are named (as tools/install_redo.py --compose names them), the "
       "check_<place>.json lying beside them is still read: the same front id is asked for its box",
       rc == 1 and len(beside) == 2 and "[front-shape]: shape 'straw_posts'" in out, out)
    # batch 0, as staged (tools/art/staged/): the first two shaped places, and the four pictures by their renders
    import copy, struct as _struct
    staged = os.path.join(TOOLS, "art", "staged")
    record = check_campus.load_record(os.path.join(REPO, "tools", "bgs", "campus.json"))
    for place, ids in (("courtyard", 7), ("library", 4)):
        there = os.path.join(staged, place)
        hot_path = os.path.join(there, "hot_%s.json" % place)
        hot = json.load(open(hot_path, encoding="utf-8"))
        view = json.load(open(os.path.join(there, "view_%s.json" % place), encoding="utf-8"))
        gone_in = os.path.join(REPO, "game", "layout", "view_%s.json" % place)
        if os.path.exists(gone_in) and "for_rev" in json.load(open(gone_in, encoding="utf-8")):
            # installed: the staged copy is history, and what is checked is that it IS what went in
            def bare(path):
                data = json.load(open(path, encoding="utf-8"))
                data.pop("for_rev", None)
                return data
            inst_hot = os.path.join(REPO, "game", "layout", "hot_%s.json" % place)
            same = os.path.exists(inst_hot) and bare(inst_hot) == bare(hot_path) and bare(gone_in) == bare(os.path.join(there, "view_%s.json" % place))
            ok("batch 0's %s layout is installed, and game/layout/hot_%s.json and view_%s.json are the staged files "
               "(tools/art/staged/%s/) apart from for_rev: the staged copy is the record of what was traced"
               % (place, place, place, place), same)
            continue
        rc, out = run(cl + [there, "--layout-dump", lab.dump])
        ok("the staged %s (tools/art/staged/%s/) passes check_layout.py with nothing refused: %d shapes, one for every "
           "exit and every hotspot registered or planned, each with its point and the side its name opens, none keeping "
           "a button; one to four people, a floor and a scale" % (place, place, ids),
           rc == 0 and "REFUSED" not in out and ": PASS (" in out.strip().splitlines()[-1]
           and len(hot["shapes"]) == ids and set(hot["shapes"]) == set(hot["spots"]) == set(hot["tips"])
           and "keep_tile" not in hot and hot.get("for_rev") == view.get("for_rev") == 2
           and sorted(view["slots"]) == ["1", "2", "3", "4"] and view["floor"]["on"] and len(view["scale"]) == 3, out)
        rc, out = run([tool("check_campus.py"), "--layout-dump", lab.dump, "--layout", hot_path])
        ok("and agrees with the campus record's fixed facts for the place (check_campus.py --layout: nothing failed, "
           "nothing reported)", rc == 0 and "FAIL" not in out and "check_campus: PASS (0 reported" in out, out)
        trial = copy.deepcopy(record)
        before = dict((r["id"], (r.get("side"), r.get("order"))) for r in check_campus.Rec(trial).rows("exit", place=place))
        _kind, _key, spots = check_campus.read_layout_file(hot_path)
        done = check_campus.fix_from_layout(trial, place, spots, 2, date="2026-10-06")
        after = check_campus.Out()
        check_campus.check_record(check_campus.Rec(trial), lay.d, after)
        ok("and with its facts written into the record, as a real install writes them, the record still passes and no "
           "exit's side or order has changed (the Courtyard's exits are numbered among the things seen between them)",
           after.count("FAIL") == 0 and not done["rewritten"]
           and before == dict((r["id"], (r.get("side"), r.get("order"))) for r in check_campus.Rec(trial).rows("exit", place=place)),
           [repr(done)] + after.texts("FAIL"))
    art0 = json.load(open(os.path.join(staged, "batch_0", "art_0.json"), encoding="utf-8"))["pictures"]
    ok("batch 0's four pictures are staged by their 2752 x 1536 renders, the ones the campus record names, never by a "
       "1920 px file (tools/art/staged/batch_0/art_0.json)",
       sorted(art0) == ["cafeteria", "courtyard", "dorm_common", "library"]
       and all(row["size"] == [2752, 1536] and row["render"] == record["pictures"][k]["render"]
               and "1920" not in row["render"] and len(row["sha256"]) == 64 for k, row in art0.items()), art0)
    for k, row in sorted(art0.items()):
        path = os.path.join(OUTPUT, row["render"])
        if not os.path.exists(path):
            skipped("REAL: batch 0's render for %s is the file its record names" % k, "%s is not on this machine" % path)
            continue
        data = open(path, "rb").read()
        ok("REAL: batch 0's render for %s is the file its record names: %s, 2752 x 1536, the same sha256" % (k, row["render"]),
           data[:8] == b"\x89PNG\r\n\x1a\n" and list(_struct.unpack(">II", data[16:24])) == row["size"]
           and hashlib.sha256(data).hexdigest() == row["sha256"])
    rc, out = run([tool("check_campus.py"), "--selftest", "--layout-dump", lab.dump])
    ok("python3 tools/check_campus.py --selftest passes (it failed unseen from U0c1 to U0d3's review: no standing "
       "test ran it)", rc == 0 and "check_campus selftest: PASS" in out and "FAIL" not in out, out)
    rc, out = run(cl + ["--selftest", "--layout-dump", lab.dump])
    ok("python3 tools/check_layout.py --selftest passes (the same cases, run inside the tool)",
       rc == 0 and "check_layout selftest: PASS" in out, out)
    stale = os.path.join(lab.work, "layout_stale.json")
    d = json.load(open(lab.dump)); d["hash"] = "0" * 64; json.dump(d, open(stale, "w"))
    rc, out = run(cl + [folder + "/files", "--layout-dump", stale])
    ok("check_layout.py refuses, in one line, a dump that is out of date", rc == 2 and out.strip() == STALE, out)

    # layout_sheet.py: the new keys, its numbers from the dump, a shaped place, a layout that is only staged
    import struct
    import layout_sheet

    def png_size(path):
        with open(path, "rb") as f:
            head = f.read(24)
        return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else None

    layout_sheet.use_dump(lay)
    lanes = lay.frame("hot_lanes")
    moved = game_layout.Layout(dict(lay.d, frames=dict(lay.d["frames"], hot_lanes=[[1000, 100, 200, 300], [400, 96, 900, 74]])))
    was = (layout_sheet.TOAST_LANE, layout_sheet.BANNER_LANE, layout_sheet.HOT_FRAME, layout_sheet.PIN_FRAME)
    layout_sheet.use_dump(moved)
    ok("layout_sheet.py draws the toast lane, the banner lane and the two frames from the layout dump (the toast lane "
       "runs to y %d, as the game's does; its own copy stopped at 350), and a dump with another lane moves the sheet's"
       % (lanes[0][1] + lanes[0][3]),
       was == ((lanes[0][0], lanes[0][1], lanes[0][0] + lanes[0][2], lanes[0][1] + lanes[0][3]),
               (lanes[1][0], lanes[1][1], lanes[1][0] + lanes[1][2], lanes[1][1] + lanes[1][3]),
               tuple(lay.frame("hot_bounds")), tuple(lay.frame("map_pin_frame")))
       and was[0][3] == 422 and layout_sheet.TOAST_LANE == (1000, 100, 1200, 400), was)
    layout_sheet.use_dump(lay)
    staged = os.path.join(folder, "staged")
    files = check_layout.base_courtyard()
    files["view_courtyard"].update({"scale": [1750, 340, 1030], "talk": False, "cast": {"evening": [1, 0.5, 0.3]}})
    check_layout.write_case(files, staged)
    picture = os.path.join(REPO, "game", "images", "bg", "courtyard.png")
    ls = [tool("layout_sheet.py")]
    sheet = os.path.join(folder, "hot_courtyard.png")
    rc, out = run(ls + ["hot_courtyard", "--staged", staged, "--bg", picture, "--out", sheet, "--layout-dump", lab.dump])
    ok("layout_sheet.py draws a layout that is still only staged (its files in a folder, its picture given by path), and "
       "for a shaped place two frames: the outlines over the picture, and every shape lit and named (1920 x 2212)",
       rc == 0 and png_size(sheet) == (1920, 2212) and "picture courtyard.png (--bg)" in out and "staged" in out, out)
    if rc == 0:
        from pngread import load as png_load
        im = png_load(sheet)

        def px(x, y):
            i = (y * im.w + x) * im.ch
            return tuple(im.buf[i:i + 3])
        top, low = px(1200, 44 + 1000), px(1200, 44 + 1080 + 8 + 1000)     # inside the gate's band of flagstones
        out_top, out_low = px(1000, 44 + 880), px(1000, 44 + 1080 + 8 + 880)     # flagstones outside every shape
        ok("in the second frame a shape is lit against a dimmed picture: inside the gate's band the pixel is lighter than "
           "the same flagstones outside it, and outside every shape the second frame is darker than the first",
           sum(low) > sum(out_low) + 40 and sum(out_low) < sum(out_top), (top, low, out_top, out_low))
    plain = dict(files["hot_courtyard"]); plain.pop("shapes")
    check_layout.write_case({"hot_courtyard": plain}, os.path.join(folder, "plain"))
    sheet2 = os.path.join(folder, "hot_plain.png")
    rc, out = run(ls + ["hot_courtyard", "--staged", os.path.join(folder, "plain"), "--out", sheet2, "--layout-dump", lab.dump])
    ok("a place with no shapes is one frame, as before (1920 x 1124), with the keys tips and spots read",
       rc == 0 and png_size(sheet2) == (1920, 1124), out)
    sheet3 = os.path.join(folder, "view_courtyard.png")
    rc, out = run(ls + ["view_courtyard", "--staged", staged, "--out", sheet3, "--layout-dump", lab.dump])
    ok("a view sheet takes the new keys (floor, scale, cast, talk) and draws the floor and the scale on a full-size "
       "panel (1920 x 2212)", rc == 0 and png_size(sheet3) == (1920, 2212), out)
    check_layout.write_case({"hot_boys_dorm": {"spare": [[640, 620], [1030, 640], [1320, 760]], "for_rev": 2,
                                               "keep_tile": {}, "tips": {"go_boys_dorm__dorm": "right"}}}, os.path.join(folder, "house"))
    rc, out = run(ls + ["hot_boys_dorm", "--staged", os.path.join(folder, "house"), "--out", os.path.join(folder, "house.png"),
                        "--layout-dump", lab.dump])
    ok("a hotspot sheet takes spare, tips, keep_tile and for_rev (a house's spare doors are drawn)", rc == 0, out)
    check_layout.write_case({"hot_boys_dorm": {"spots": {}, "doors": []}}, os.path.join(folder, "wrong"))
    rc, out = run(ls + ["hot_boys_dorm", "--staged", os.path.join(folder, "wrong"), "--out", os.path.join(folder, "wrong.png"),
                        "--layout-dump", lab.dump])
    ok("and still stops, in one plain line, at a key no sidecar holds",
       rc != 0 and "unknown key 'doors'" in out and len(out.strip().splitlines()) == 1, out)


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

    # ---- U0d3: the band along a traced shape's outline (5.4 step 2, D60), and the corrections the check was owed
    # A shape traced round the back window, in a dump that says so (the dump's `shapes`, as the game's sidecar
    # would give it). The window and the wall round it are slid 9 px.
    frame = [[612, 222], [1045, 222], [1045, 535], [612, 535]]
    shaped = stamp(lab.dump, root, out=os.path.join(root, "dump_shaped.json"), extra={"shapes": {"dorm_common": {"tv": [frame]}}})
    win9 = lab.syn("slide", room, "syn_win9_a_00001_.png", "600,210,460,340", "9")
    rc, out, v = one(win9)
    ok("with no shape traced there, a wall slid 9 px under no registered point is only shown (LOOK)",
       v[0] == "LOOK" and rc == 0 and "sits 9 px right" in v[1], out)
    rc, out = run(redo + [win9, "--dry", "--root", root, "--layout-dump", shaped], py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("with a shape traced there, the same render is REFUSED: the wall under the shape's outline moved 9 px, and the "
       "shape is named (once, though its outline is held at many points)",
       v[0] == "REFUSED" and rc == 1 and v[1].count("the outline of the shape traced for the hotspot tv moved 9 px right") == 1
       and v[1].count("the outline of the shape traced for the hotspot tv") == 1, out)
    rc, out = run(redo + [good, "--dry", "--root", root, "--layout-dump", shaped], py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    m = re.search(r"(\d+) points checked", out)
    m0 = re.search(r"(\d+) points checked", one(good)[1])
    ok("and a good render of a shaped room still passes, with the outline's points among those checked (%s, against %s)"
       % (m.group(1) if m else "?", m0.group(1) if m0 else "?"),
       v[0] == "PASS" and m is not None and m0 is not None and int(m.group(1)) > int(m0.group(1)), out)

    # 1. glass. The way to the garden sits on the sliding door's glass; the keep list's `windows` rows are its panes.
    kl = json.load(open(os.path.join(TOOLS, "bgs", "keep", "dorm_common.json")))
    panes = ";".join(",".join(str(n) for n in w["box"]) for w in kl["windows"])
    view = lab.syn("glass", room, "syn_view_a_00001_.png", panes)
    rc, out, v = one(view)
    ok("a new view behind the glass of the door an exit sits on is not a moved door: with the panes in the keep "
       "list's `windows` it is not refused, and the changed view is shown",
       v[0] == "LOOK" and rc == 0 and "drawn differently" in v[1] and "Dormitory Garden" not in v[1] and "gone" not in v[1], out)
    noglass = os.path.join(lab.work, "keep_noglass")
    os.makedirs(noglass, exist_ok=True)
    json.dump(dict((k, r) for k, r in kl.items() if k != "windows"), open(os.path.join(noglass, "dorm_common.json"), "w"))
    rc, out, v = one(view, ["--keep", noglass])
    ok("without the `windows` rows the same render is REFUSED for the door, which is the false alarm the rows are for",
       v[0] == "REFUSED" and "%s no longer lines up" % spot in v[1], out)
    # (the door itself slid 12 px, slid 30 px and painted out are refused above, with the `windows` rows in place)

    # 2. a floor drawn again: other boards, a window's light across it
    floor = ";".join("%d,%d" % tuple(q) for q in [z for z in kl["empty"] if z["name"] == "the floor"][0]["poly"])
    rc, out, v = one(lab.syn("refloor", room, "syn_refloor_a_00001_.png", floor))
    ok("a floor drawn again (its boards run the other way, sunlight lies on it) is not a moved floor and not a new "
       "thing: it is shown (\"the floor is drawn again\"), not refused",
       v[0] == "LOOK" and rc == 0 and "the floor is drawn again" in v[1] and "something new" not in v[1]
       and "no longer lines up" not in v[1], out)
    rc, out, v = one(lab.syn("refloor", room, "syn_refloortv_a_00001_.png", floor, "1497,380,190,322,12"))
    ok("with the floor drawn again AND the television slid 12 px, the picture is still REFUSED for the television",
       v[0] == "REFUSED" and rc == 1 and re.search(r"the television moved 1[0-4] px right", v[1]) is not None, out)
    # (a cushion, a kettle, a bag and a striped bag set down on the floor that is still the same drawing are refused above)
    # A floor that MOVED is still refused (review 1). With no keep list at all, so that nothing but the standing
    # points can say so: the sofa's foot, the rug and the boards under two standing rows slid 12 px.
    bare = os.path.join(lab.work, "keep_none")
    os.makedirs(bare, exist_ok=True)
    rc, out, v = one(lab.syn("slide", room, "syn_floor12_a_00001_.png", "324,884,472,167", "12"), ["--keep", bare])
    ok("the floor under two standing rows slid 12 px, in a room with no keep list, is REFUSED by the standing points "
       "alone, and the tool says by how much (a window that locks on an offset has moved, feet or not)",
       v[0] == "REFUSED" and rc == 1 and "the floor where people stand (a row of 1, at x 560) moved 12 px right" in v[1]
       and "the floor where people stand (a row of 4, at x 590) moved 12 px right" in v[1]
       and "drawn differently where people stand" not in v[1], out)
    rc, out, v = one(lab.syn("slide", room, "syn_floor12w_a_00001_.png", "174,724,852,327", "12"), ["--keep", bare])
    ok("a wider part of the room slid 12 px: every standing row on it is named as moved 12 px",
       v[0] == "REFUSED" and rc == 1 and len(re.findall(r"the floor where people stand \(a row of \d, at x \d+\) moved 12 px right", v[1])) >= 4, out)
    cls = os.path.join(root, "game", "images", "bg", "classroom.png")
    rc, out = run([tool("install_redo.py"), "classroom", lab.syn("slide", cls, "syn_class9_a_00001_.png", "124,674,952,377", "9"),
                   "--dry", "--keep", bare] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("the classroom's floor slid 9 px is REFUSED the same way (\"a row of 2, at x 720\" moved 9 px right)",
       v[0] == "REFUSED" and rc == 1 and "the floor where people stand (a row of 2, at x 720) moved 9 px right" in v[1], out)
    # and the refusal that is left for a floor drawn again: its boards are new (so its own window agrees with
    # nothing), but the sofa and the table that stand on it slid 12 px. Only the wider, coarse window can say so.
    rc, out, v = one(lab.syn("refloor", room, "syn_refloorslid_a_00001_.png", floor, "174,724,852,204,12"), ["--keep", bare])
    ok("a floor drawn again whose furniture slid 12 px is REFUSED by the floor's edge and what stands on it "
       "(the wider window on the coarse drawing), where the same floor with nothing moved is only shown",
       v[0] == "REFUSED" and rc == 1
       and re.search(r"the floor where people stand \(a row of \d, at x \d+\) moved 12 px right \(the floor's edge and what stands round it\)", v[1]) is not None, out)

    # and a floor that is NOT drawn again (review 2): a flat dark bag set down where the rows of three and four
    # stand in the Cafeteria. It has too little fine edge for "something new is on the floor"; the standing
    # points say it, because the keep list's floor zone still agrees with the game's everywhere else.
    caf = os.path.join(root, "game", "images", "bg", "cafeteria.png")
    credo = [tool("install_redo.py"), "cafeteria"]
    rc, out = run(credo + [lab.syn("bag", caf, "syn_cafbag_a_00001_.png", "700,900,90,60"), "--dry"] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("a flat dark bag set down where people stand, on a floor that is otherwise the same drawing, is REFUSED by "
       "the standing points (\"something stands there\"), not shown as a floor drawn differently",
       v[0] == "REFUSED" and rc == 1
       and "the floor where people stand (a row of 3, at x 760) no longer lines up with the picture in the game, on a "
           "floor that is otherwise the same drawing: something stands there" in v[1]
       and "drawn differently where people stand" not in v[1] and "moved" not in v[1], out)
    rc, out = run(credo + [lab.syn("look", caf, "syn_caflook_a_00001_.png"), "--dry"] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("and the same Cafeteria with nothing set down passes", v[0] == "PASS" and rc == 0, out)
    rc, out = run(credo + [os.path.join(lab.work, "syn_cafbag_a_00001_.png"), "--dry", "--keep", bare] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("with no keep list (no floor zone to say the floor is the same drawing) the bag is only shown: nothing is "
       "known of that floor",
       v[0] == "LOOK" and rc == 0 and "drawn differently where people stand" in v[1], out)
    # review 3. The same bag, named: where the room's named addition (`allow`) lies inside a standing point's
    # window, what stands there is what was asked for. Step 4 leaves that floor unjudged; so do the points.
    asked = os.path.join(lab.work, "keep_asked")
    os.makedirs(asked, exist_ok=True)
    ckl = json.load(open(os.path.join(TOOLS, "bgs", "keep", "cafeteria.json"), encoding="utf-8"))
    json.dump(dict(ckl, allow=[{"name": "a bag left by the tables", "box": [690, 890, 110, 80]}]),
              open(os.path.join(asked, "cafeteria.json"), "w"))
    rc, out = run(credo + [os.path.join(lab.work, "syn_cafbag_a_00001_.png"), "--dry", "--keep", asked] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("named in `allow`, the same bag is what was asked for: the standing points whose windows it lies in are shown, "
       "not refused (\"something stands there\" is not said of the room's own named addition)",
       v[0] == "LOOK" and rc == 0 and "something stands there" not in v[1] and "something new" not in v[1]
       and "drawn differently where people stand" in v[1] and "it has what was asked for: a bag left by the tables" in v[1], out)
    # review 3. The Cafeteria's floor zone holds all nine places people stand: the rows by the wall (x 250, x 330)
    # and by the near table (x 1380) lay outside it, and a thing set down there was only shown.
    rc, out = run(credo + [lab.syn("mat", caf, "syn_cafmat_a_00001_.png", "1300,985,160,70"), "--dry"] + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    ok("a flat pale mat laid where the row of two stands by the near table (x 1380), which lay outside the keep "
       "list's floor zone until review 3, is REFUSED by the standing point and by the floor",
       v[0] == "REFUSED" and rc == 1
       and "the floor where people stand (a row of 2, at x 1380) no longer lines up with the picture in the game, on a "
           "floor that is otherwise the same drawing: something stands there" in v[1]
       and "something new is on the floor (at its right end" in v[1] and "moved" not in v[1] and "gone" not in v[1], out)
    # review 3. A flat dark thing where the standing point's OWN window still lines up (the Common Room's holds
    # the foot of the wall and the cabinet as well as the boards, so a bag in it changes too little): the floor
    # says it. It is the same drawing everywhere else, and the part the bag lies on no longer agrees.
    rc, out, v = one(lab.syn("bag", room, "syn_combag_a_00001_.png", "1335,945,130,78"))
    ok("a flat dark bag set down on the Common Room's boards where the row of three stands (x 1400) is REFUSED by "
       "the floor (\"that part of it no longer agrees with the picture in the game\"), though the standing point's own "
       "window still lines up and the bag has too little fine edge for \"something new\" (unseen until review 3)",
       v[0] == "REFUSED" and rc == 1 and "something new is on the floor (at its right end" in v[1]
       and "that part of it no longer agrees with the picture in the game" in v[1] and "and the rest of it does" in v[1]
       and "something stands there" not in v[1] and "moved" not in v[1] and "gone" not in v[1], out)

    # 3. the named addition on a hotspot's own object: the allow box wins over the automatic keep box, and over
    # nothing else
    card = "1350,826,100,100"
    board = lab.syn("sign", room, "syn_cards_a_00001_.png", card)
    rc, out, v = one(board)
    ok("a new thing drawn over the card table's hotspot is REFUSED three ways: its spot, the thing at it, and the "
       "cushions it covers",
       v[0] == "REFUSED" and "the spot the hotspot card_table sits on no longer lines up" in v[1]
       and "the thing at the hotspot card_table is gone" in v[1] and "the floor cushions by the low table are gone" in v[1], out)
    allowed = os.path.join(lab.work, "keep_allowed")
    os.makedirs(allowed, exist_ok=True)
    json.dump(dict(kl, allow=[{"name": "a game board on the card table", "box": [int(n) for n in card.split(",")]}]),
              open(os.path.join(allowed, "dorm_common.json"), "w"))
    rc, out, v = one(board, ["--keep", allowed])
    ok("named in `allow`, it no longer makes the hotspot's own object \"gone\" (the allow box wins over the automatic "
       "box round the same point); the hand-written row it covers is still refused",
       v[0] == "REFUSED" and "card_table" not in v[1].split("(also")[0] and "the floor cushions by the low table are gone" in v[1]
       and "it has what was asked for: a game board on the card table" in v[1], out)

    # 4. the rescue for a pale thing on a lighter wall needs the thing's outline: a thing washed out and turned
    # over inside its box, outline and all, is still gone
    rc, out, v = one(lab.syn("inside", room, "syn_inside_a_00001_.png", "1285,483,65,72"))
    ok("a kept thing washed out and turned over inside its own box is still REFUSED as gone (\"fainter\" is said "
       "only of a thing whose outline still agrees)",
       v[0] == "REFUSED" and "the kettle on the counter is gone" in v[1] and "fainter" not in v[1], out)

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
    ok("and its report says, where \"added\" stands for a day picture, that a relight is read by eye for added things",
       len(re.findall(r"(?m)^\s+added\s+not judged in a relight", out)) == 2 and "by eye" in out, out)
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

    # a room lit at Night (U0n, 5.7a): `lit` is a third hour, for a room of the game's lit table only
    lamp = lab.syn("night", os.path.join(root, "game", "images", "bg", "dorm_common.png"), "syn_lit_a_00001_.png")
    plain = stamp(lab.dump, root)
    before = tree_hash(root)
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "lit", lamp, "--choose", "a", "--root", root,
                   "--layout-dump", plain], py=True)
    ok("--relight <place> lit is refused in one line for a room the game's lit table (WORLD_LIT) does not name, and "
       "nothing is written", rc != 0 and "has no lit picture" in out and "WORLD_LIT" in out and len(out.strip().splitlines()) == 1
       and tree_hash(root) == before, out)
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "dusk", lamp, "--dry", "--root", root,
                   "--layout-dump", plain], py=True)
    ok("an hour that is not evening, night or lit is refused in one line", rc != 0 and "evening|night" in out and "lit" in out
       and len(out.strip().splitlines()) <= 2, out)
    lit_table = {"lit_planned": [["dorm_common", "images/bg/dorm_common_lit.png"]]}        # TEST ONLY: the Common Room has none
    ltail = ["--root", root, "--layout-dump", stamp(lab.dump, root, out=os.path.join(root, "dump_lit.json"), extra=lit_table)]
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "lit", lamp, moved, "--dry"] + ltail, py=True)
    v = verdicts(out)
    ok("a lit picture is proved as any relight is: the same drawing with the lamps on is not refused, the one shifted "
       "9 px is, and --dry writes nothing but the previews (redo_dorm_common_lit_a.jpg)",
       v.get("a", ("",))[0] in ("PASS", "LOOK") and v.get("b", ("",))[0] == "REFUSED" and "(dorm_common_lit.png), a relight" in out
       and tree_hash(root) == before and os.path.exists(os.path.join(root, "shots", "art", "redo_dorm_common_lit_a.jpg")), out)
    night_bytes = open(os.path.join(root, "game", "images", "bg", "dorm_common_night.png"), "rb").read()
    night_row = dict(check_campus.load_manifest(root)["pictures"]["dorm_common_night"])
    fg_before = sorted(os.listdir(os.path.join(root, "game", "images", "fg")))
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "lit", lamp, moved, "--choose", "a", "--batch", "47"] + ltail, py=True)
    man = check_campus.load_manifest(root)["pictures"]
    row = man.get("dorm_common_lit", {})
    ok("the chosen lit picture is installed as <picture>_lit.png with its manifest row: kind relight, of its day picture, "
       "at that picture's revision",
       rc == 0 and os.path.exists(os.path.join(root, "game", "images", "bg", "dorm_common_lit.png"))
       and row.get("kind") == "relight" and row.get("of") == "dorm_common" and row.get("of_rev") == man["dorm_common"]["rev"] == 2
       and row.get("rev") == 2 and row.get("batch") == 47 and row.get("render") == os.path.basename(lamp)
       and "rev1_commit" not in row, out + json.dumps(row))
    ldata = json.load(open(light))
    ok("its light row is written under the key \"lit\" of light_<place>.json (six numbers, measured), with the manifest row "
       "light_<place>_lit; the day's and the night's rows are still there",
       len(ldata.get("lit", [])) == 6 and "night" in ldata and "" in ldata
       and man.get("light_dorm_common_lit") == {"of": "dorm_common_lit", "of_rev": 2}, json.dumps(ldata))
    fg_lit = os.path.join(root, "game", "images", "fg", "fg_dorm_common_lit.png")
    ok("its foreground is cut from the lit picture as fg_<place>_lit.png, by the day outline copied to the key \"lit\" of "
       "tools/fg/<place>.json, with the manifest row fg_<place>_lit; no foreground file was deleted",
       os.path.exists(fg_lit) and man.get("fg_dorm_common_lit") == {"of": "dorm_common_lit", "of_rev": 2}
       and json.load(open(polys)).get("lit") == json.load(open(polys)).get("")
       and sorted(os.listdir(os.path.join(root, "game", "images", "fg"))) == sorted(fg_before + ["fg_dorm_common_lit.png"]), out)
    ok("the room's dark night is not touched by it: the picture, its row, and the campus record's chosen picture are "
       "what they were",
       open(os.path.join(root, "game", "images", "bg", "dorm_common_night.png"), "rb").read() == night_bytes
       and man.get("dorm_common_night") == night_row and man.get("fg_dorm_common_night") == {"of": "dorm_common_night", "of_rev": 2}
       and json.load(open(os.path.join(root, "tools", "bgs", "campus.json")))["pictures"]["dorm_common"]["rev"] == 2)
    import check_content
    found = check_content.layout_file_findings(os.path.join(root, "game", "layout"), {}, {"dorm_common"})
    found_real = check_content.layout_file_findings(os.path.join(root, "game", "layout"), {})
    ok("what it wrote passes check_content.py --layout-files for a room that has a lit picture, and the same file is a "
       "finding for the Common Room by the game's own table, which does not name it",
       not found and any("not a place of WORLD_LIT" in t for _p, t in found_real), found + found_real)
    ltail = ["--root", root, "--layout-dump", stamp(lab.dump, root, out=os.path.join(root, "dump_lit.json"), extra=lit_table)]
    rc, out = run([tool("sample_light.py"), "--check"] + ltail, py=True)
    rc2, out2 = run([tool("sample_light.py"), "dorm_common", "lit"] + ltail, py=True)
    ok("sample_light.py knows the hour: --check reads the lit row against the lit picture and finds it right (the "
       "day row, edited by hand above, is still its one failure), and `sample_light.py <place> lit` prints the row "
       "from <picture>_lit.png",
       "ok    light_dorm_common.json, lit: " in out and out.count("FAIL  light_dorm_common.json") == 1
       and "FAIL  light_dorm_common.json, day" in out and rc2 == 0 and "dorm_common lit: [" in out2
       and "dorm_common_lit.png" in out2, out + out2)
    rc, out = run([tool("art_status.py"), "--root", root])
    ok("art_status.py lists the lit picture in the new look, and nothing of it as stale or half made",
       re.search(r"dorm_common_lit\s+revision 2\s+relight", out) is not None
       and not re.search(r"(?m)^   (fg_|light_)?dorm_common_lit\s+(is still|made for)", out), out)
    rc, out = run([tool("install_redo.py"), "--relight", "dorm_common", "lit", lamp, "--choose", "a", "--root", root2,
                   "--layout-dump", stamp(lab.dump, root2, extra=lit_table)], py=True)
    ok("a lit picture is not installed before its day picture is in the new look either (K8)",
       rc != 0 and "not installed in the new look" in out and "lit" in out
       and not os.path.exists(os.path.join(root2, "game", "images", "bg", "dorm_common_lit.png")), out)

    # review 3. A copy of the tree may stand at an OLDER revision than HEAD holds: these fixtures do, once a
    # picture of the overhaul is committed (the copy is the tree as it was before). The row must still name the
    # commit that holds the picture the install replaced, or its proof cannot be rerun. Made here with a small
    # git history of its own: the copy's picture is committed, then another over it, then the first put back.
    rh = mkroot(os.path.join(lab.work, "r_hist"))
    rel = "game/images/bg/dorm_common.png"
    pic = os.path.join(rh, *rel.split("/"))

    def g(*args):
        p = subprocess.run(["git", "-C", rh, "-c", "user.name=test_art_tools", "-c", "user.email=test@example.invalid",
                            "-c", "commit.gpgsign=false"] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.stdout.decode("utf-8", "replace").strip()

    older = lab.syn("plainrecolour", pic, "syn_hist_older_a_00001_.png")        # the same drawing, other bytes
    g("init", "-q")
    shutil.copyfile(older, pic)
    g("add", "-f", rel)
    g("commit", "-q", "-m", "the picture this copy stands at")
    held = g("rev-parse", "HEAD")
    shutil.copyfile(made["recolour"], pic)
    g("add", "-f", rel)
    g("commit", "-q", "-m", "a later picture: the one HEAD holds")
    head = g("rev-parse", "HEAD")
    shutil.copyfile(older, pic)
    rc, out = run(redo + [good, "--choose", "a", "--batch", "3", "--root", rh, "--layout-dump", stamp(lab.dump, rh)], py=True)
    row = check_campus.load_manifest(rh)["pictures"].get("dorm_common", {})
    ok("a copy that stands at an older picture than its HEAD holds: the row's from_commit and rev1_commit are the commit "
       "of the file's history that holds the picture on disk, not \"not committed (a copy)\" (review 3: so the suite's "
       "own rows read once batch 0 was committed)",
       rc == 0 and re.match(r"^[0-9a-f]{40}$", held) is not None and held != head
       and row.get("from_commit") == held and row.get("rev1_commit") == held, out + json.dumps(row))
    rc, out = run(redo + [good, "--dry", "--against-rev1", "--root", rh, "--layout-dump", stamp(lab.dump, rh)], py=True)
    ok("and its proof can be rerun from git: --against-rev1 measures against that commit's picture",
       rc == 0 and "before the overhaul (git, commit %s)" % held[:10] in out, out)
    return root


PIXELS = r'''
import sys, json, numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
out = {"size": [a.shape[1], a.shape[0]]}
if len(sys.argv) > 2:
    b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(int)
    if a.shape == b.shape:
        d = np.abs(a - b).max(axis=2) > 24
        d[:30] = False                      # the line of words over a frame
        ys, xs = np.where(d)
        out["changed"] = int(d.sum())
        out["box"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(ys) else None
        for k, v in enumerate(sys.argv[3:]):
            x0, y0, x1, y1 = [int(n) for n in v.split(",")]
            out["in%d" % k] = int(d[y0:y1, x0:x1].sum())
            out["lighter%d" % k] = float((a[y0:y1, x0:x1].mean() - b[y0:y1, x0:x1].mean()))
print(json.dumps(out))
'''


def group_stage(lab):
    """stage_preview.py: a place drawn as the game would, with the people standing in it (6.5, D60)."""
    if not lab.art:
        skipped("stage_preview.py", "no ComfyUI python")
        return
    root = mkroot(os.path.join(lab.work, "r_stage"))
    dump = stamp(lab.dump, root)
    pix = os.path.join(lab.work, "pixels.py")
    open(pix, "w").write(PIXELS)
    out = os.path.join(lab.work, "stage")
    os.makedirs(out, exist_ok=True)

    def draw(args, name, d=None):
        path = os.path.join(out, name)
        rc, text = run([tool("stage_preview.py")] + args + ["--root", root, "--layout-dump", d or dump, "--out", path], py=True)
        return rc, text, path

    def pixels(*args):
        rc, text = run([pix] + list(args), py=True)
        return json.loads(text.strip().splitlines()[-1]) if rc == 0 else {"error": text}

    rc, text, empty = draw(["dorm_common", "evening", "--who", "none", "--plain"], "empty.png")
    rc2, text2, three = draw(["dorm_common", "evening", "--who", "megumi,yuji,maki", "--plain"], "three.png")
    got = pixels(three, empty)
    ok("the Common Room at evening is drawn with three people, on the room's own evening picture and under its light",
       rc == 0 and rc2 == 0 and got.get("size") == [1920, 1110] and "dorm_common_evening.png; as painted" in text2
       and "the game's own row for the place" in text2, text + text2 + json.dumps(got))
    # where the game stands three people there (view_stage.rpy: VIEW_SLOTS), and the tags' line; 30 px is the title
    slots = json.load(open(dump))["slots"]["dorm_common"]["3"]
    box = got.get("box") or [0, 0, 0, 0]
    x0 = min(s[0] - 760 * s[2] / 2 for s in slots)
    x1 = max(s[0] + 760 * s[2] / 2 for s in slots)
    top = min(1080 + s[1] - 1400 * s[2] for s in slots) + 30
    ok("the people are where the game stands them: nothing is drawn outside the three slots' rectangles and the "
       "name-tag line (changed pixels lie in x %d to %d, y %d to %d)" % (box[0], box[2], box[1], box[3]),
       got.get("changed", 0) > 60000 and box[0] >= x0 - 4 and box[2] <= x1 + 4 and box[1] >= top - 4 and box[3] <= 1080 + 30, json.dumps(got))
    far = [s for s in slots if s[3]][0]
    # the far person stands behind the low table: where the foreground is solid, at the table, nothing changes
    fg = os.path.join(root, "game", "images", "fg", "fg_dorm_common_evening.png")
    code = ("import sys, json, numpy as np; from PIL import Image; a = np.asarray(Image.open(sys.argv[1]).convert('RGBA'))[..., 3]; "
            "ys, xs = np.where(a > 250); x = int(%d); col = ys[xs == x]; print(json.dumps([x, int(col.min()), int(col.max())]))" % far[0])
    rc, text = run(["-c", code, fg], py=True)
    col = json.loads(text.strip().splitlines()[-1]) if rc == 0 else [0, 0, 0]
    got = pixels(three, empty, "%d,%d,%d,%d" % (col[0] - 3, col[1] + 30 + 4, col[0] + 3, col[2] + 30 - 4))
    ok("the foreground is laid over the far person: in the low table's own column under them (x %d, y %d to %d) "
       "not a pixel changed" % (col[0], col[1], col[2]), rc == 0 and col[2] - col[1] > 40 and got.get("in0") == 0, text + json.dumps(got))
    rc, text, marked = draw(["dorm_common", "evening", "--who", "megumi,yuji,maki"], "marked.png")
    got = pixels(marked, three)
    ok("without --plain the exit's tile and each thing to do are drawn at their points", rc == 0 and got.get("changed", 0) > 3000, json.dumps(got))

    # a shaped place (D60): the outlines, and a frame with every shape lit and named
    frame = [[612, 222], [1045, 222], [1045, 535], [612, 535]]
    shaped = stamp(lab.dump, root, out=os.path.join(root, "dump_shaped.json"), extra={"shapes": {"dorm_common": {"tv": [frame]}}})
    rc, text, plain_sheet = draw(["dorm_common"], "sheet.jpg")
    rc2, text2, shape_sheet = draw(["dorm_common"], "sheet_shaped.jpg", shaped)
    a, b = pixels(plain_sheet), pixels(shape_sheet)
    ok("the sheet of a place: one to four people by day and a frame for each hour, at half size (%s)" % a.get("size"),
       rc == 0 and a.get("size") == [1928, 3 * 570 + 16] and "shaped" not in text, text)
    ok("the sheet of a SHAPED place has two frames more, at full size: every shape's outline, and every shape lit "
       "and named (%s)" % b.get("size"),
       rc2 == 0 and b.get("size") == [1928, 3 * 570 + 16 + 2 * (1110 + 8)]
       and "shaped: 1 shapes; two frames more, their outlines and every shape lit and named" in text2, text2)
    rc, text, lit = draw(["dorm_common", "day", "--who", "none"], "shape_frame.png", shaped)
    rc2, text2, unlit = draw(["dorm_common", "day", "--who", "none", "--plain"], "shape_plain.png", shaped)
    got = pixels(lit, unlit, "612,%d,1045,%d" % (222 + 30 - 3, 222 + 30 + 3))
    ok("and one frame of it draws the shape's outline on the picture", rc == 0 and rc2 == 0 and got.get("in0", 0) > 800, text + json.dumps(got))

    # a picture and a layout that are only staged
    staged = os.path.join(lab.work, "staged_room")
    os.makedirs(staged, exist_ok=True)
    json.dump({"spots": {"tv": [1500, 500]}, "shapes": {"tv": [[[1420, 380], [1690, 380], [1690, 700], [1420, 700]]]}},
              open(os.path.join(staged, "hot_dorm_common.json"), "w"))
    json.dump({"slots": {"1": [[900, -40, 0.52, 0]]}}, open(os.path.join(staged, "view_dorm_common.json"), "w"))
    render = lab.syn("look", os.path.join(root, "game", "images", "bg", "dorm_common.png"), "syn_stage_bg.png")
    rc, text, one = draw(["dorm_common", "day", "--who", "megumi", "--plain", "--bg", render, "--staged", staged], "staged_one.png")
    rc2, text2, none = draw(["dorm_common", "day", "--who", "none", "--plain", "--bg", render, "--staged", staged], "staged_none.png")
    got = pixels(one, none)
    box = got.get("box") or [0, 0, 0, 0]
    ok("a picture given by --bg and a layout that is only staged are drawn: the person stands at the staged slot "
       "(x 900; drawn from x %d to %d), under a light measured on that picture" % (box[0], box[2]),
       rc == 0 and rc2 == 0 and "view_dorm_common.json from the staged folder" in text and "taken as the day picture" in text
       and "measured on this picture, as the installer would write it" in text and 700 <= box[0] and box[2] <= 1100
       and "shaped: 1 shapes" in text, text + json.dumps(got))
    rc, text, _p = draw(["dorm_common", "evening", "--who", "megumi,yuji,maki", "--dialogue"], "scene.png")
    got = pixels(_p, three)
    ok("--dialogue draws the scene case: the people larger, their feet on the bottom edge", rc == 0 and got.get("changed", 0) > 100000, text)
    rc, text, _p = draw(["nowhere"], "x.png")
    ok("a name that is no place is refused in one line", rc != 0 and "is not a place of the game" in text and len(text.strip().splitlines()) == 1, text)
    stale = os.path.join(lab.work, "stale_dump.json")
    with open(stale, "w") as f:
        json.dump(dict(json.load(open(dump)), hash="0" * 64), f)
    rc, text = run([tool("stage_preview.py"), "dorm_common", "day", "--root", root, "--layout-dump", stale], py=True)
    ok("an out-of-date dump is refused (status 2), as every art tool refuses it", rc == 2 and text.strip() == STALE, text)


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
    # rooms lit at Night (U0n, 5.7a): a pose on a lit picture carries the variant `lit`
    {"who": "megumi", "place": "library", "variant": "lit", "batch": 97, "doing": "t", "spot": "sitting at a reading table"},
    {"who": "toge", "place": "library", "variant": "lit", "batch": 97, "doing": "t", "spot": "sitting at a reading table"},
    {"who": "toge", "place": "senpai_room", "variant": "lit", "batch": 98, "doing": "t", "spot": "sitting at the board"},
    {"who": "panda", "place": "senpai_room", "variant": "lit", "batch": 98, "state": "asleep", "doing": "asleep"},
]
# The asleep, home and away tables of a test, in the shape the dump writes them (tools/smoke/u2_dump.rpy: `world`).
TEST_TABLES = {"world": {"asleep": {"weekday": ["megumi", "panda"], "weekend": ["yuji", "toge"]},
                         "homes": {"megumi": "megumi_room", "panda": "senpai_room", "toge": "senpai_room", "yuji": "yuji_room"},
                         "away": {"nobara": {"Sun Afternoon": "harajuku"}, "maki": {"Sun Afternoon": "harajuku"},
                                  "yuji": {"Sun Afternoon": "shibuya"}}},
               # the lit and late tables (U0n), at the dump's top level, in its shape
               "lit_planned": [["library", "images/bg/library_lit.png"], ["megumi_room", "images/bg/megumi_room_lit.png"],
                               ["senpai_room", "images/bg/senpai_room_lit.png"]],
               "late": {"megumi": {"place": "library", "days": ["Sun"]}, "toge": {"place": "library", "days": ["Wed"]}}}
# The same, with both of them out late on the same Night: then their two poses in the lit Library can show together.
SAME_NIGHT = dict(TEST_TABLES, late={"megumi": {"place": "library", "days": ["Sun"]}, "toge": {"place": "library", "days": ["Sun"]}})


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
    lit_man = os.path.join(lab.work, "pose_manifest_lit.json")
    json.dump({"pictures": {"library": {"rev": 2, "kind": "inplace"},
                            "library_lit": {"rev": 2, "kind": "relight", "of": "library", "of_rev": 2}}}, open(lit_man, "w"))
    shutil.copyfile(os.path.join(bg, "your_room_night.png"), os.path.join(bg, "library_lit.png"))
    shutil.copyfile(os.path.join(bg, "your_room_night.png"), os.path.join(bg, "senpai_room_lit.png"))
    on_lit = ["--root", root, "--layout-dump", dump, "--manifest", lit_man, "--print", "--plan", plan]
    rc, out = run(mk + ["library", "megumi", "lit"] + on_lit)
    ok("a row on a lit picture (variant lit, U0n) is written as pose_<place>__<who>__lit and painted on <picture>_lit.png",
       rc == 0 and "pose_library__megumi__lit" in out and re.search(r"picture 1:.*library_lit\.png", out) is not None, out)
    json.dump({"pictures": {"library": {"rev": 2, "kind": "inplace"}}}, open(lit_man, "w"))
    rc, out = run(mk + ["library", "megumi", "lit"] + on_lit)
    ok("K8: and it is refused in one line while the room's lit picture is not installed in the new look",
       rc != 0 and len(out.strip().splitlines()) == 1 and "library_lit" in out and "not installed in the new look" in out, out)
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

        # rooms lit at Night (U0n, 5.7a): poses on a lit picture, and the late table in "can show together"
        lib = os.path.join(bg, "library_lit.png")

        def restamp(tables=TEST_TABLES):
            return ["--root", root, "--layout-dump", stamp(lab.dump, root, extra=tables), "--plan", plan]

        rc, out = run(ip + [render("pose_library__megumi__lit_a_00001_.png", "1000,520,300,360", lib)] + restamp())
        lman = check_campus.load_manifest(root)["pictures"]
        ok("install_pose.py installs a pose on a lit picture: its box under <who>__lit in pose_<place>.json, and its "
           "manifest row names <picture>_lit",
           rc == 0 and "megumi__lit" in json.load(open(os.path.join(root, "game", "layout", "pose_library.json")))["poses"]
           and lman.get("pose_library__megumi__lit") == {"of": "library_lit", "of_rev": 1}
           and os.path.exists(os.path.join(root, "game", "images", "place", "pose_library__megumi__lit.png")), out)
        clash = render("pose_library__toge__lit_a_00001_.png", "1100,540,300,360", lib)
        rc, out = run(ip + [clash, "--dry"] + restamp(SAME_NIGHT))
        ok("two overlapping poses in the lit Library are refused when the late table has both there on the same Night, "
           "and the Night is named (Sun, Night)",
           rc != 0 and "overlaps the box of pose_library__megumi__lit" in out and "can show together (Sun, Night)" in out, out)
        rc, out = run(ip + [clash] + restamp())
        ok("and accepted by the game's own table, where Megumi stays late on Sundays and Toge on Wednesdays: the two "
           "never show together",
           rc == 0 and "never show together" in out
           and sorted(json.load(open(os.path.join(root, "game", "layout", "pose_library.json")))["poses"]) == ["megumi__lit", "toge__lit"], out)
        room3 = os.path.join(bg, "senpai_room_lit.png")
        rc, out = run(ip + [render("pose_senpai_room__panda__lit__asleep_a_00001_.png", "900,600,500,240", room3, "90,80,120")] + restamp())
        rc2, out2 = run(ip + [render("pose_senpai_room__toge__lit_a_00001_.png", "1000,500,300,360", room3)] + restamp())
        ok("on the shared room's lit picture Toge awake and Panda asleep can show together (a weekday Night) and may not "
           "overlap; the Night Toge is out late is not the one named",
           rc == 0 and rc2 != 0 and "overlaps the box of pose_senpai_room__panda__lit__asleep" in out2
           and "can show together" in out2 and "(Wed, Night)" not in out2, out + out2)
        no_wed = dict(TEST_TABLES, world=dict(TEST_TABLES["world"], asleep={"weekday": ["megumi"], "weekend": ["yuji", "toge", "panda"]}))
        rc3, out3 = run(ip + [render("pose_senpai_room__toge__lit_a_00002_.png", "1000,500,300,360", room3), "--dry"] + restamp(no_wed))
        ok("and with Panda asleep there on no Night Toge is at home awake, the same two boxes never show together",
           rc3 == 0 and "never show together" in out3, out3)

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
    bgdir = os.path.join(root, "game", "images", "bg")
    shutil.copyfile(os.path.join(bgdir, "dorm_common_night.png"), os.path.join(bgdir, "dorm_common_lit.png"))
    shutil.copyfile(os.path.join(root, "game", "images", "fg", "fg_dorm_common_night.png"),
                    os.path.join(root, "game", "images", "fg", "fg_dorm_common_lit.png"))
    rc, out = run([tool("art_status.py"), "--root", root])
    ok("a lit picture (5.7a) made for the old room is listed as half made in its own words (the room stays dark at "
       "Night whoever is up), and its foreground as stale against the day picture",
       re.search(r"dorm_common_lit\s+is still the picture made for the old dorm_common; until it is remade the room "
                 r"shows its dark Night picture even with someone up in it", out) is not None
       and re.search(r"fg_dorm_common_lit\s+made for revision 1 of dorm_common, which is now at revision 2", out) is not None
       and re.search(r"dorm_common_night\s+is still the picture made for the old dorm_common; until it is remade that hour "
                     r"shows the new day picture tinted", out) is not None, out)


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
    # (until U0d3 its second sentence was "no longer lines up with the picture in the game", said of the floor
    # where people stand; a floor that is drawn differently is shown now, and the shelf alone refuses it)
    ("library", "look2_library_bright", "REFUSED", ["the thing at the hotspot locked_shelf moved 1", "the spot the hotspot locked_shelf sits on moved 1",
                                                    "the floor is drawn differently where people stand"]),
    ("library", "look2_library_gallery", "REFUSED", ["this is a different picture"]),
]
PAIRS = [("dorm_common", "dorm_common", "evening"), ("dorm_common", "dorm_common", "night"), ("rooftop", "rooftop", "evening"),
         ("rooftop", "rooftop", "night"), ("riverside", "riverside", "evening"), ("infirmary", "infirmary", "night"),
         ("girls_dorm", "girls_dorm", "night"), ("dorm", "your_room", "night")]


# ---- the pictures the owner chose early (U0d3) ----------------------------------------------------------------
EARLY = os.path.expanduser("~/Desktop/JJK Game images/ui2/early")
EARLY_RECORD = os.path.join(TOOLS, "art", "staged", "early", "campus_for_batch3.json")
# The seven corrections' own cases (tools/art/staged/early/art_3a_early.json, art_3b_early.json, art_4b_early.json,
# art_6b_early.json, art_7b_early.json, art_17a_early.json): (what it shows, place, hour, render, its day picture,
# the verdicts it may have, words its report must hold, words it must not hold). A day picture is "" for the
# game's own (redone in place), "chosen" for the fitted copy of the chosen day picture, or a file of OUTPUT.
EARLY_CASES = [
    ("1. a view changed on purpose behind the glass door: the chosen Common Room is not refused for the garden door",
     "dorm_common", "", "ui2_dorm_common_a", "", ("LOOK",), ["drawn differently"], ["Dormitory Garden", "gone", "moved"]),
    ("2 to 4. the chosen My Room: the floor drawn again, the laptop at the computer and the calendar on a lighter "
     "wall are each shown, and nothing is refused",
     "your_room", "", "ui2_your_room_b", "", ("LOOK",),
     ["the floor is drawn again", "the floor is drawn differently where people stand",
      "the calendar by the door is fainter, or something else is drawn inside its outline",
      "it has what was asked for: a closed laptop on the desk"], ["is gone", "something new", "no longer lines up"]),
    ("2. the Riverside redone in place, version A: still a PASS", "riverside", "", "ui2_riverside_a", "", ("PASS",), [], []),
    ("2. the Riverside redone in place, version B: a slab of rock repainted lighter is shown, not refused",
     "riverside", "", "ui2_riverside_b", "", ("LOOK",), ["the floor is drawn differently where people stand"], ["no longer lines up"]),
    ("5. a relit Common Room with a blanket laid over the sofa's arm (not chosen): shown, never refused",
     "dorm_common", "night", "ui2_dorm_common_night_a", "chosen", ("LOOK",), ["something new may be on the sofa's near arm"], []),
    ("5. the other version of that night, which added nothing: a PASS",
     "dorm_common", "night", "ui2_dorm_common_night_b", "chosen", ("PASS",), [], []),
    ("7. the Cafeteria's evening, version A: the window's grid of sunlight across the floor is shown, not refused",
     "cafeteria", "evening", "ui2_cafeteria_evening_a", "chosen", ("LOOK",), ["the floor is drawn differently where people stand"], ["no longer lines up"]),
    ("7. the Cafeteria's evening, version B: still a PASS", "cafeteria", "evening", "ui2_cafeteria_evening_b", "chosen", ("PASS",), [], []),
    ("7. the Cafeteria's night, version A: moonlight across the floor is shown, not refused",
     "cafeteria", "night", "ui2_cafeteria_night_a", "chosen", ("LOOK",), ["the floor is drawn differently where people stand"], ["no longer lines up"]),
    ("7. the Cafeteria's night, version B: the same", "cafeteria", "night", "ui2_cafeteria_night_b", "chosen", ("LOOK",),
     ["the floor is drawn differently where people stand"], ["no longer lines up"]),
    ("7. the infirmary's lights-off night, version B: the same false alarm, met again, is shown",
     "infirmary", "night", "ui2_infirmary_night_off_b", "chosen", ("LOOK",), ["the floor is drawn differently where people stand"], ["no longer lines up"]),
    ("7. the Library's night, version B: the same", "library", "night", "ui2_library_night_b", "look2_library_bright_00001_.png",
     ("LOOK",), ["the floor is drawn differently where people stand"], ["no longer lines up"]),
]
# THE WIDER PROOF: every picture redone in place or relit that the owner has chosen (the `chosen` rows of
# tools/art/staged/early/art_*_early.json), each run as its record says it was. None may be REFUSED.
# (the sitting's file, place, hour, the chosen render, its day picture)
EARLY_CHOSEN = [
    ("3a", "dorm_common", "", "ui2_dorm_common_a", ""), ("3a", "your_room", "", "ui2_your_room_b", ""),
    ("4a", "cafeteria", "", "ui2_cafeteria_a", ""), ("6a7a", "classroom", "", "ui2_classroom_b", ""),
    ("6a7a", "infirmary", "", "ui2_infirmary_a", ""), ("8a", "rooftop", "", "ui2_rooftop_a", ""),
    ("3b", "dorm_common", "evening", "ui2_dorm_common_evening_a", "chosen"), ("3c", "dorm_common", "night", "ui2_dorm_common_night_off_a", "chosen"),
    ("3b", "your_room", "evening", "ui2_your_room_evening_b", "chosen"), ("3c", "your_room", "night", "ui2_your_room_night_off_a", "chosen"),
    # My Room lit (5.7a): the lamp-on night of sitting 3b, version A, which the owner passed over as the room's night (O38)
    ("3b", "your_room", "lit", "ui2_your_room_night_a", "chosen"),
    ("4b", "cafeteria", "evening", "ui2_cafeteria_evening_a", "chosen"), ("4b", "cafeteria", "night", "ui2_cafeteria_night_a", "chosen"),
    ("4b", "girls_dorm", "evening", "ui2_girls_dorm_evening_a", "chosen"), ("4b", "girls_dorm", "night", "ui2_girls_dorm_night_off_a", "chosen"),
    ("6a7a", "courtyard", "evening", "ui2_courtyard_evening_a", "chosen"), ("6a7a", "courtyard", "night", "ui2_courtyard_night_a", "chosen"),
    ("6b", "classroom", "evening", "ui2_classroom_evening_b", "chosen"), ("6b", "classroom", "night", "ui2_classroom_night_a", "chosen"),
    ("6b", "infirmary", "evening", "ui2_infirmary_evening_b", "chosen"), ("6b", "infirmary", "night", "ui2_infirmary_night_a", "chosen"),
    ("7b", "school_yard", "evening", "ui2_school_yard_evening_a", "chosen"), ("7b", "school_yard", "night", "ui2_school_yard_night_a", "chosen"),
    ("7b", "library", "evening", "ui2_library_evening_b", "look2_library_bright_00001_.png"),
    ("7b", "library", "night", "ui2_library_night_a", "look2_library_bright_00001_.png"),
    ("7b", "library", "lit", "ui2_library_night_lamps_a", "look2_library_bright_00001_.png"),
    ("8a", "dorm_yard", "evening", "ui2_dorm_yard_evening_b", "chosen"), ("8b", "dorm_yard", "night", "ui2_dorm_yard_night_moon_a", "chosen"),
    ("8b", "rooftop", "evening", "ui2_rooftop_evening_a", "chosen"), ("8b", "rooftop", "night", "ui2_rooftop_night_b", "chosen"),
    ("12d", "gojo_office", "evening", "ui2_gojo_office_evening_a", "chosen"), ("12d", "office", "evening", "ui2_office_evening_b", "chosen"),
    ("12d", "utahime_office", "evening", "ui2_utahime_office_evening_a", "chosen"),
    ("14p", "pool", "evening", "ui2_pool_evening_a", "chosen"), ("14p", "staff_yard", "evening", "ui2_staff_yard_evening_b", "chosen"),
    ("14p", "trailhead", "evening", "ui2_trailhead_evening_b", "chosen"), ("14p", "trailhead", "night", "ui2_trailhead_night_b", "chosen"),
    ("15b", "training", "evening", "ui2_training_evening_a", "chosen"), ("15b", "training", "night", "ui2_training_night_a", "chosen"),
    ("15b", "dojo", "evening", "ui2_dojo_evening_a", "chosen"), ("15b", "dojo", "night", "ui2_dojo_night_a", "chosen"),
    ("15c", "dojo", "lit", "ui2_dojo_lit2_a", "chosen"),
    ("15b", "storehouse", "evening", "ui2_storehouse_evening_a", "chosen"), ("15b", "storehouse", "night", "ui2_storehouse_night_a", "chosen"),
    ("16p", "training_yard", "evening", "ui2_training_yard_evening_a", "chosen"), ("16p", "training_yard", "night", "ui2_training_yard_night_b", "chosen"),
    ("18g", "gate", "evening", "ui2_gate_evening_a", "chosen"), ("18g", "gate", "night", "ui2_gate_night_b", "chosen"),
    ("17b", "ridge", "evening", "ui2_ridge_evening_b", "chosen"), ("17b", "ridge", "night", "ui2_ridge_night_a", "chosen"),
    ("17b", "riverside", "evening", "ui2_riverside_evening_a", "chosen"), ("17b", "riverside", "night", "ui2_riverside_night_a", "chosen"),
    ("17c", "forest", "evening", "ui2_forest_evening_a", "chosen"), ("17c", "forest", "night", "ui2_forest_night_a", "chosen"),
    ("19b", "bathhouse", "evening", "ui2_bathhouse_evening_a", "chosen"), ("19b", "bathhouse", "night", "ui2_bathhouse_night_a", "chosen"),
    # chosen on 11 Oct, after the list above was written (review 1). A `lit` picture (a room with its lamp on at
    # Night, 5.7a) is run under its own hour, `lit`, since U0n taught the installer that hour; all eight of the
    # game's lit rooms are in this list (the Library's, My Room's and the dojo's above, the five friends' below).
    ("9b", "boys_dorm", "evening", "ui2_boys_dorm_evening_b", "chosen"), ("9b", "boys_dorm", "night", "ui2_boys_dorm_night_b", "chosen"),
    ("9c", "yuji_room", "evening", "ui2_yuji_room_evening_b", "chosen"), ("9c", "yuji_room", "night", "ui2_yuji_room_night_b", "chosen"),
    ("9c", "yuji_room", "lit", "ui2_yuji_room_lit_a", "chosen"),
    ("10b", "megumi_room", "evening", "ui2_megumi_room_evening_b", "chosen"), ("10b", "megumi_room", "night", "ui2_megumi_room_night_b", "chosen"),
    ("10b", "megumi_room", "lit", "ui2_megumi_room_lit_b", "chosen"),
    ("10b", "senpai_room", "evening", "ui2_senpai_room_evening_b", "chosen"), ("10b", "senpai_room", "night", "ui2_senpai_room_night_a", "chosen"),
    ("10b", "senpai_room", "lit", "ui2_senpai_room_lit_a", "chosen"),
    ("11b", "nobara_room", "evening", "ui2_nobara_room_evening_b_00002_.png", "chosen"),
    ("11b", "nobara_room", "night", "ui2_nobara_room_night_b_00002_.png", "chosen"),
    ("11b", "nobara_room", "lit", "ui2_nobara_room_lit_b_00002_.png", "chosen"),
    ("11b", "maki_room", "evening", "ui2_maki_room_evening_b", "chosen"), ("11b", "maki_room", "night", "ui2_maki_room_night_a", "chosen"),
    ("11b", "maki_room", "lit", "ui2_maki_room_lit_a", "chosen"),
    ("13d", "teachers_lounge", "evening", "ui2_teachers_lounge_evening_a", "chosen"),
    ("13d", "teachers_lounge", "night", "ui2_teachers_lounge_night_b", "chosen"),
    ("13d", "teachers_dorm", "evening", "ui2_teachers_dorm_evening_a", "chosen"),
    ("13d", "teachers_dorm", "night", "ui2_teachers_dorm_night_b", "chosen"),
]
# Each later early sitting that chooses a picture redone in place or relit adds its row here (the records are
# tools/art/staged/early/art_<n>_early.json; this list ends with the records of 11 Oct 2026).


def early_run(place, hour, render, day, tail):
    """One early render through install_redo.py --dry, as its record says it was run: (rc, out, verdict, words),
    or None with the file that is not on this machine."""
    path = os.path.join(EARLY, "renders", render if render.endswith(".png") else render + "_00001_.png")
    base = "" if not day else (os.path.join(EARLY, "chosen", "%s_1920.png" % place) if day == "chosen" else os.path.join(OUTPUT, day))
    for f in (path, base):
        if f and not os.path.exists(f):
            return None, f
    if hour:
        args = [tool("install_redo.py"), "--relight", place, hour, path, "--against", base, "--record", EARLY_RECORD]
    else:
        args = [tool("install_redo.py"), place, path]
    rc, out = run(args + tail, py=True)
    v = list(verdicts(out).values())[0] if verdicts(out) else ("?", "")
    return (rc, out, v[0], v[1]), None


def real_early(tail):
    """The seven corrections on the renders that showed them, and the wider proof."""
    for what, place, hour, render, day, want, words, never in EARLY_CASES:
        got, absent = early_run(place, hour, render, day, tail)
        if got is None:
            skipped("REAL, early: %s" % what, "%s is not on this machine" % absent)
            continue
        rc, out, verdict, said = got
        ok("REAL, early: %s (%s: %s)" % (what, render, verdict),
           verdict in want and rc == 0 and all(w in said for w in words) and not any(w in said for w in never), out)
    table = []
    for sitting, place, hour, render, day in EARLY_CHOSEN:
        got, absent = early_run(place, hour, render, day, tail)
        name = "REAL, chosen in sitting %s: %s%s (%s)" % (sitting, place, " at %s" % hour if hour else ", redone in place", render)
        if got is None:
            skipped(name, "%s is not on this machine" % absent)
            continue
        rc, out, verdict, said = got
        table.append((sitting, render, verdict))
        ok("%s is %s, not REFUSED" % (name, verdict), verdict in ("PASS", "LOOK") and rc == 0, out)
    return table


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
        # batch 0's two composed pictures with their staged layouts, as the installer will be asked (10.2, U0d3)
        for stem, render in (("courtyard", "look2_courtyard_gateway"), ("library", "look2_library_bright")):
            staged = os.path.join(TOOLS, "art", "staged", stem)
            name = ("REAL: install_redo.py --compose %s <its 2752 px render> --layout <the staged hot_ and view_ files> --dry"
                    % stem)
            gone_in = os.path.join(REPO, "game", "layout", "view_%s.json" % stem)
            if os.path.exists(gone_in) and "for_rev" in json.load(open(gone_in, encoding="utf-8")):
                row = check_campus.load_manifest(REPO)["pictures"].get(stem, {})
                ok("%s: the picture is installed, so the staged layout is no longer asked; the manifest's row says it is "
                   "that render, composed, at revision 2" % name,
                   row.get("render") == render + "_00001_.png" and row.get("kind") == "composed" and row.get("rev") == 2, row)
                continue
            if not os.path.exists(os.path.join(OUTPUT, render + "_00001_.png")):
                skipped(name, "%s_00001_.png is not in %s" % (render, OUTPUT))
                continue
            rc, out = run([tool("install_redo.py"), "--compose", stem, os.path.join(OUTPUT, render + "_00001_.png"), "--layout",
                           os.path.join(staged, "hot_%s.json" % stem), os.path.join(staged, "view_%s.json" % stem)] + tail, py=True)
            ok("%s is a PASS: the render is fitted from 2752 px, the layout passes the screen's rules with the "
               "check_%s.json beside it read, and the campus record agrees" % (name, stem),
               rc == 0 and "2752x1536 -> 1920x1072, 4 px down" in out and "VERDICT   PASS" in out
               and "check_%s, hot_%s, view_%s: PASS" % (stem, stem, stem) in out and "REFUSED" not in out, out)
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
    real_early(tail)
    for place, stem, hour in PAIRS:
        # the pairs the game had before the overhaul: read from the scratch copy, which stands there (mkroot)
        day = os.path.join(root, "game", "images", "bg", stem + ".png")
        pic = os.path.join(root, "game", "images", "bg", "%s_%s.png" % (stem, hour))
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
            "(docs/UI2_DESIGN.md 5.4, 5.7), written by tools/test_art_tools.sh --write-measures: first on 7 Oct 2026, and "
            "again on 11 Oct 2026 (U0d3's review) for the constants and the two figure keys the seven corrections added "
            "(floor_points: how many standing points read as a floor drawn differently; relight_empty_most: [rise, levels] of "
            "the small empty place of a relight that gained most against the ring round it). No verdict changed. And on "
            "12 Oct 2026 (review 3) for SAME_FLOOR and SAME_CELL (a flat thing set down on a floor that is the same "
            "drawing) and the figure key empty_cell_least, with the Cafeteria's floor zone widened to hold all nine "
            "places people stand. No verdict changed.",
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
            "(a floor) that gained most; cells_different is how many 120 px cells step 6 shows; empty_cell_least is [the "
            "agreement with the game's picture of the 160 px part of a wide empty place that agrees least, the middle "
            "agreement of that place's parts]: a thing set down reads under SAME_CELL where the middle is SAME_FLOOR or more."]
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
    for rel in ("game/images", "game/images/bg", "game/images/fg", "game/layout", "tools/fg", "tools/bgs"):
        if os.path.islink(os.path.join(REPO, *rel.split("/"))):
            raise SystemExit("%s is a symbolic link in this tree: the tests copy the tree and install into the copy, "
                             "and will not run where a copy could write through a link" % rel)
    art = have_art_python()
    game_before = game_status()
    hash_before = tree_hash(REPO)
    work = work or tempfile.mkdtemp(prefix="test_art_tools_")
    os.makedirs(work, exist_ok=True)
    lab = Lab(work, dump, art)
    t0 = time.time()
    print("# test_art_tools: %s; ComfyUI's Python %s; scratch %s" % (", ".join(groups), "found" if art else "NOT found", work))
    then = before_overhaul()
    for why in then["problems"]:
        skipped("the fixtures stand in the tree as it was before the overhaul", why)
    if then["fatal"]:
        # one plain line, and nothing is run: all but one of the groups install into a copy of that tree
        ok("the fixtures: %s" % fixtures_line(then), False)
        groups = []
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
