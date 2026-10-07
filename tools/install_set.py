"""
Put a redrawn person's whole set into the game in one step, or not at all.

    python3 tools/install_set.py yuji <staged folder>                 # the fourteen pictures and the faces.json rows
    python3 tools/install_set.py yuji <staged folder> --dry           # every check; writes nothing
    python3 tools/install_set.py yuji <staged folder> --root <a copy of the project>
    python3 tools/install_set.py --stage yuji <render folder> [--out <staged folder>]
                                                                      # key and fit the six renders first
    options: --no-cloth (do not run the uniform's cloth match)

docs/UI2_DESIGN.md D57, D58, D59. A person who is redrawn changes all at
once: there must be no day on which their clothes differ between two faces,
or their eyes blink where the old drawing had them. So this installs,
together and only together:

  - six sprites        <staged>/char/<who>_<expression>.png   (neutral, happy, serious, angry, surprised, sad)
  - six side portraits <staged>/side/<who>_<expression>.png
  - two overlay pictures <staged>/fx/fx_<who>_blink.png and fx_<who>_talk.png
  - their rows in      <staged>/faces.json: "eyes" and "mouth" for the person (their boxes on the new
                       drawing, measured by tools/install_face.py --sprite ... --stage), and "blink_also"

and then regenerates game/jjk_sprites.rpy (the feet and the contact shadow
are measured again), on the same file names and the same canvas, so no script
and no save changes.

IT REFUSES, and writes nothing, when
  - any of the fourteen pictures is missing, or the person's eye or mouth box
    is not in the staged faces.json (every missing thing is listed);
  - a sprite is not on the person's canvas (760x1400; Panda's is 880 wide);
  - the six sprites do not share one body: outside a box round the face
    (the eye and mouth boxes together, with room for the brows and the
    chin), every face's sprite must be the calm sprite pixel for pixel;
  - an overlay picture differs from the calm sprite outside its own box, or
    is the calm sprite itself (a blink that never closes);
  - the eye box and the mouth box overlap, or the mouth is not below the eyes;
  - a side portrait is not the one made from the sprite staged beside it;
  - afterwards one of the person's image names would no longer resolve.
If a later step fails, everything it had written is put back as it was.

THE UNIFORM'S CLOTH (D59). For someone who wears the school uniform, the
cloth is put on the one ramp in the same step: tools/cloth_match.py --apply
<who> (with --redrawn for Yuji), and its check must then pass. That needs
ComfyUI's Python; without it the install is refused (or pass --no-cloth and
match it afterwards). The overlay pictures are made again from the matched
calm sprite, so they still differ from it only inside their boxes.

--stage is the step before: it keys <render folder>/<who>_base.png (the calm
picture) and <render folder>/composited/<who>_<expression>.png with the new
edge (tools/keysprite.py --edge new, D58), fits them to the canvas at the
person's height and makes the side portraits, into <render folder>/staged/.
A new sprite is never keyed with the old edge. The two overlay pictures are
made after that, from the staged calm sprite (tools/install_face.py --prepare
<who> --sprite ..., the owner runs the edit, then install_face.py ... --stage).

AFTERWARDS, in the owner's folder (docs/UI2_CONTRACTS.md A2): the sprite's
feet numbers are in tools/smoke/baseline_sprite_tree.txt, which is written
again once the tree line of tools/smoke.sh u2_baseline has passed; then
tools/load_all_saves.sh and every harness that shows the person.

Pure Python, apart from the keying and the cloth match, which start
themselves with ComfyUI's Python.
"""
import sys, os, re, json, shutil, subprocess, tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
from pngread import load

ROOT = os.path.dirname(TOOLS)
EXPRESSIONS = ("neutral", "happy", "serious", "angry", "surprised", "sad")
KINDS = (("blink", "eyes"), ("talk", "mouth"))
CANVAS_H = 1400
HEAD_SHARE = 0.30           # the faces differ only in the top of the figure, this share of its height
# "One body" is judged on a box round the face: the eye and mouth boxes together, grown by these shares of
# their joint height (above: the brows; below: the chin) and width. On the thirteen people in the game the
# faces differ from the calm one by at most 0.45 above (Shoko), 0.45 below (Utahime) and 0.26 beside (Panda).
FACE_UP, FACE_DOWN, FACE_SIDE = 0.6, 0.6, 0.35
REDRAWN = ("yuji",)         # cloth_match.py matches these with --redrawn


def canvas_of(who):
    from keysprite import CANVAS_W, OUT_W
    return CANVAS_W.get(who, OUT_W), CANVAS_H


def uniform_people():
    """Who wears the school uniform: the keys of cloth_match.UNIFORM, read without importing numpy."""
    src = open(os.path.join(TOOLS, "cloth_match.py"), encoding="utf-8").read()
    m = re.search(r"^UNIFORM = \{(.*?)^\}", src, re.S | re.M)
    return re.findall(r'^\s*"(\w+)":', m.group(1), re.M) if m else []


def staged_files(who, folder):
    """[(what it is, staged path, path in the game)] for the fourteen pictures."""
    out = []
    for e in EXPRESSIONS:
        out.append(("the %s sprite" % ("calm" if e == "neutral" else e), os.path.join(folder, "char", "%s_%s.png" % (who, e)),
                    os.path.join("game", "images", "char", "%s_%s.png" % (who, e))))
    for e in EXPRESSIONS:
        out.append(("the %s side portrait" % ("calm" if e == "neutral" else e), os.path.join(folder, "side", "%s_%s.png" % (who, e)),
                    os.path.join("game", "images", "side", "%s_%s.png" % (who, e))))
    for kind, _key in KINDS:
        out.append(("the %s picture" % kind, os.path.join(folder, "fx", "fx_%s_%s.png" % (who, kind)),
                    os.path.join("game", "images", "char", "fx", "fx_%s_%s.png" % (who, kind))))
    return out


def differing_rows(a, b, box=None):
    """(first row, last row, count) of the pixels where two RGBA pictures differ, outside `box`; None if none."""
    if a.buf == b.buf:
        return None
    w, h = a.w, a.h
    first = last = None
    n = 0
    for y in range(h):
        ra, rb = a.buf[y * w * 4:(y + 1) * w * 4], b.buf[y * w * 4:(y + 1) * w * 4]
        if ra == rb:
            continue
        if box is not None and box[1] <= y < box[1] + box[3]:
            x0, x1 = box[0] * 4, (box[0] + box[2]) * 4
            if ra[:x0] == rb[:x0] and ra[x1:] == rb[x1:]:
                continue
        n += 1
        first = y if first is None else first
        last = y
    return (first, last, n) if n else None


def differing_box(a, b):
    """(x0, y0, x1, y1) round every pixel where two RGBA pictures of one size differ; None if none."""
    if a.buf == b.buf:
        return None
    w, h = a.w, a.h
    x0, y0, x1, y1 = w, h, 0, 0
    for y in range(h):
        ra, rb = a.buf[y * w * 4:(y + 1) * w * 4], b.buf[y * w * 4:(y + 1) * w * 4]
        if ra == rb:
            continue
        first = next(i for i in range(w * 4) if ra[i] != rb[i]) // 4
        last = next(i for i in range(w * 4 - 1, -1, -1) if ra[i] != rb[i]) // 4
        x0, x1 = min(x0, first), max(x1, last + 1)
        y0, y1 = min(y0, y), max(y1, y + 1)
    return (x0, y0, x1, y1)


def face_box(eyes, mouth):
    """(x0, y0, x1, y1): where a person's faces may differ from the calm one."""
    x0, y0 = min(eyes[0], mouth[0]), min(eyes[1], mouth[1])
    x1, y1 = max(eyes[0] + eyes[2], mouth[0] + mouth[2]), max(eyes[1] + eyes[3], mouth[1] + mouth[3])
    w, h = x1 - x0, y1 - y0
    return (int(x0 - w * FACE_SIDE), int(y0 - h * FACE_UP), int(x1 + w * FACE_SIDE + 0.5), int(y1 + h * FACE_DOWN + 0.5))


def figure_rows(im):
    rows = [y for y in range(im.h) if any(im.buf[(y * im.w + x) * 4 + 3] > 24 for x in range(0, im.w, 3))]
    return (rows[0], rows[-1] + 1) if rows else (0, im.h)


def image_names(path, who):
    """{image name: [files it shows]} for one person, read from a jjk_sprites.rpy."""
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^image ((?:side )?%s(?: \w+)?) = (.*)$" % re.escape(who), line.rstrip("\n"))
        if m:
            out[m.group(1)] = re.findall(r'"(images/[^"]+)"', m.group(2))
    return out


def check_set(who, folder, root):
    """Everything that must hold before a file is written. Returns (files, faces rows) or exits with every fault."""
    faults = []
    files = staged_files(who, folder)
    missing = [(what, src) for what, src, _dest in files if not os.path.exists(src)]
    for what, src in missing:
        faults.append("%s is missing (%s)" % (what, src))
    fpath = os.path.join(folder, "faces.json")
    rows = {}
    if not os.path.exists(fpath):
        faults.append("the staged faces.json is missing (%s): the person's eye and mouth boxes on the new drawing" % fpath)
    else:
        data = json.load(open(fpath, encoding="utf-8"))
        cw, ch = canvas_of(who)
        for _kind, key in KINDS:
            box = (data.get(key) or {}).get(who)
            ok = (isinstance(box, list) and len(box) == 4 and all(isinstance(v, int) and not isinstance(v, bool) for v in box)
                  and box[2] > 0 and box[3] > 0 and box[0] >= 0 and box[1] >= 0 and box[0] + box[2] <= cw and box[1] + box[3] <= ch)
            if not ok:
                faults.append("the staged faces.json has no %s box for %s (\"%s\": {\"%s\": [x, y, w, h]})" % (key, who, key, who))
            else:
                rows[key] = box
        also = (data.get("blink_also") or {}).get(who, [])
        if not isinstance(also, list) or any(e not in EXPRESSIONS or e == "neutral" for e in also):
            faults.append("the staged faces.json: blink_also for %s must be a list of faces" % who)
        rows["blink_also"] = also
        if "eyes" in rows and "mouth" in rows:
            import install_face
            e, m = rows["eyes"], rows["mouth"]
            if install_face.boxes_overlap(e, m):
                faults.append("the staged faces.json: the eyes box (%d, %d) %dx%d and the mouth box (%d, %d) %dx%d overlap: "
                              "one of them was measured wrongly (run that edit again)" % (tuple(e) + tuple(m)))
            elif m[1] < e[1] + e[3]:
                faults.append("the staged faces.json: the mouth box (%d, %d) %dx%d is not below the eyes box (%d, %d) %dx%d"
                              % (tuple(m) + tuple(e)))
    if missing:
        fail(who, faults, len(missing))
    cw, ch = canvas_of(who)
    loaded = {}
    for what, src, dest in files:
        im = load(src)
        loaded[dest] = im
        if im.ch != 4:
            faults.append("%s has no alpha channel (%s)" % (what, os.path.basename(src)))
        elif "side" not in dest.split(os.sep) and (im.w, im.h) != (cw, ch):
            faults.append("%s is %dx%d, not the %dx%d canvas (%s)" % (what, im.w, im.h, cw, ch, os.path.basename(src)))
    if faults:
        fail(who, faults, 0)
    calm = loaded[os.path.join("game", "images", "char", "%s_neutral.png" % who)]
    top, bottom = figure_rows(calm)
    head_end = top + int((bottom - top) * HEAD_SHARE)
    face = face_box(rows["eyes"], rows["mouth"]) if "eyes" in rows and "mouth" in rows else None
    for e in EXPRESSIONS[1:]:
        d = differing_box(calm, loaded[os.path.join("game", "images", "char", "%s_%s.png" % (who, e))])
        if d is None:
            continue
        if face is None:
            if d[3] > head_end:
                faults.append("the six do not share one body: the %s sprite differs from the calm one down to row %d (the "
                              "head ends near row %d)" % (e, d[3] - 1, head_end))
        elif d[0] < face[0] or d[1] < face[1] or d[2] > face[2] or d[3] > face[3]:
            faults.append("the six do not share one body: the %s sprite differs from the calm one outside the face (it "
                          "differs in columns %d to %d, rows %d to %d; the face is columns %d to %d, rows %d to %d)"
                          % (e, d[0], d[2] - 1, d[1], d[3] - 1, face[0], face[2] - 1, face[1], face[3] - 1))
    for kind, key in KINDS:
        if key not in rows:
            continue
        fx = loaded[os.path.join("game", "images", "char", "fx", "fx_%s_%s.png" % (who, kind))]
        if fx.buf == calm.buf:
            faults.append("the %s picture is the calm sprite itself: nothing changes inside the %s box (%s)"
                          % (kind, key, "a blink that never closes" if kind == "blink" else "a mouth that never moves"))
            continue
        diff = differing_rows(calm, fx, rows[key])
        if diff:
            faults.append("the %s picture differs from the calm sprite outside the %s box (%d rows, from row %d): the "
                          "box in faces.json is not the one this picture was made with" % (kind, key, diff[2], diff[0]))
    # each side portrait is the one made from the sprite staged beside it
    from keysprite import side_portrait
    for e in EXPRESSIONS:
        made = side_portrait(loaded[os.path.join("game", "images", "char", "%s_%s.png" % (who, e))])
        got = loaded[os.path.join("game", "images", "side", "%s_%s.png" % (who, e))]
        if (got.w, got.h) != (made.w, made.h) or got.buf != made.buf:
            faults.append("the %s side portrait was not made from the %s sprite staged beside it (tools/install_set.py "
                          "--stage makes the two together)" % (("calm" if e == "neutral" else e,) * 2))
    if faults:
        fail(who, faults, 0)
    return files, rows


def fail(who, faults, n_missing):
    print("REFUSED: %s's set is not installed, and nothing was written." % who.capitalize())
    for f in faults:
        print("  - %s" % f)
    if n_missing:
        print("A set goes in whole: all fourteen pictures and the face rows, or none (docs/UI2_DESIGN.md D57).")
    raise SystemExit(1)


def regenerate(root):
    """tools/gen_sprite_defs.py, run on `root` (it finds its project from its own path)."""
    gen = os.path.join(TOOLS, "gen_sprite_defs.py")
    code = compile(open(gen, encoding="utf-8").read(), gen, "exec")
    fake = os.path.join(root, "tools", "gen_sprite_defs.py")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(code, {"__file__": fake, "__name__": "__main__"})
    return buf.getvalue()


def remake_fx(root, who, rows, staged):
    """The overlay pictures again: the calm sprite as installed, with only the box taken from the staged picture."""
    from raster import Img
    calm = load(os.path.join(root, "game", "images", "char", "%s_neutral.png" % who))
    for kind, key in KINDS:
        src = load(staged[kind])
        x, y, w, h = rows[key]
        out = Img(calm.w, calm.h, alpha=True)
        out.buf[:] = calm.buf
        for yy in range(y, y + h):
            a, b = (yy * calm.w + x) * 4, (yy * calm.w + x + w) * 4
            out.buf[a:b] = src.buf[a:b]
        out.save(os.path.join(root, "game", "images", "char", "fx", "fx_%s_%s.png" % (who, kind)))


def install(who, folder, root=None, dry=False, cloth=True):
    root = root or ROOT
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        raise SystemExit("no staged folder at %s" % folder)
    files, rows = check_set(who, folder, root)
    sprites_rpy = os.path.join(root, "game", "jjk_sprites.rpy")
    before = image_names(sprites_rpy, who)
    wears = who in uniform_people()
    py_art = os.path.join(TOOLS, "py_art.sh")
    if wears and cloth and subprocess.run(["/bin/bash", py_art, "--where"], stdout=subprocess.PIPE).returncode != 0:
        print("REFUSED: %s wears the school uniform, and its cloth is matched in the same step (D59). That needs "
              "ComfyUI's Python, which is not on this machine. Nothing was written." % who.capitalize())
        raise SystemExit(1)
    print("%s: all fourteen pictures are here, on the %dx%d canvas; the six share one body; the two overlay pictures "
          "differ from the calm sprite only inside their boxes" % ((who.capitalize(),) + canvas_of(who)))
    print("   eyes %s   mouth %s   the blink also sits on: %s"
          % (rows["eyes"], rows["mouth"], ", ".join(rows["blink_also"]) or "no other face"))
    if dry:
        print("(--dry: nothing written)")
        return 0

    # every file this step may change is kept, so that a failure puts all of it back
    backup = tempfile.mkdtemp(prefix="install_set_")
    touched = [dest for _w, _s, dest in files] + [os.path.join("game", "layout", "faces.json"),
                                                  os.path.join("game", "jjk_sprites.rpy"),
                                                  os.path.join("game", "images", "fx", "contact_shadow.png")]
    had = {}
    for rel in touched:
        p = os.path.join(root, rel)
        had[rel] = os.path.exists(p)
        if had[rel]:
            os.makedirs(os.path.dirname(os.path.join(backup, rel)), exist_ok=True)
            shutil.copy2(p, os.path.join(backup, rel))

    def put_back(why):
        for rel in touched:
            p = os.path.join(root, rel)
            if had[rel]:
                shutil.copy2(os.path.join(backup, rel), p)
            elif os.path.exists(p):
                os.remove(p)
        shutil.rmtree(backup, ignore_errors=True)
        print("REFUSED: %s. Everything this step had written has been put back as it was." % why)
        raise SystemExit(1)

    try:
        for _what, src, dest in files:
            os.makedirs(os.path.dirname(os.path.join(root, dest)), exist_ok=True)
            shutil.copyfile(src, os.path.join(root, dest))
        import install_face
        install_face.write_faces(os.path.join(root, "game", "layout", "faces.json"), who,
                                 blink_also=rows["blink_also"], eyes=rows["eyes"], mouth=rows["mouth"])
        if wears and cloth:
            flags = ["--redrawn"] if who in REDRAWN else []
            p = subprocess.run([sys.executable, os.path.join(TOOLS, "cloth_match.py"), "--apply", who, "--root", root] + flags,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            text = p.stdout.decode("utf-8", "replace").strip()
            for line in text.splitlines():
                print("   cloth     %s" % line)
            if p.returncode != 0:
                put_back("the uniform's cloth could not be matched (tools/cloth_match.py; the lines above say why)")
            p = subprocess.run([sys.executable, os.path.join(TOOLS, "cloth_match.py"), "--check", "--root", root] + flags,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if p.returncode != 0:
                for line in p.stdout.decode("utf-8", "replace").strip().splitlines():
                    print("   cloth     %s" % line)
                put_back("tools/cloth_match.py --check does not pass with the new set in")
            print("   cloth     tools/cloth_match.py --check%s passes" % (" --redrawn" if flags else ""))
            staged = dict((kind, os.path.join(folder, "fx", "fx_%s_%s.png" % (who, kind))) for kind, _k in KINDS)
            remake_fx(root, who, rows, staged)
        elif wears:
            print("   cloth     NOT matched (--no-cloth): run tools/cloth_match.py --apply %s%s before anyone sees it"
                  % (who, " --redrawn" if who in REDRAWN else ""))
        said = regenerate(root)
        after = image_names(sprites_rpy, who)
        lost = sorted(n for n in before if n not in after)
        gone = sorted(set(f for fs in after.values() for f in fs if not os.path.exists(os.path.join(root, "game", f))))
        if lost or gone or len(after) < 2 * len(EXPRESSIONS) + 2:
            put_back("afterwards %s" % ("; ".join(
                (["the image name%s %s would no longer resolve" % ("" if len(lost) == 1 else "s", ", ".join(lost))] if lost else [])
                + (["%s would be named and missing" % ", ".join(gone)] if gone else [])
                + (["only %d of the person's %d image names would be defined" % (len(after), 2 * len(EXPRESSIONS) + 2)]
                   if not lost and not gone else []))))
    except SystemExit:
        raise
    except Exception as e:           # anything unforeseen: still leave the game as it was
        put_back("the install stopped on an error (%s: %s)" % (type(e).__name__, e))
    shutil.rmtree(backup, ignore_errors=True)
    for line in said.strip().splitlines()[:1]:
        print("   sprites   %s" % line.strip())
    line = [l for l in open(sprites_rpy, encoding="utf-8") if l.startswith("image %s = " % who)]
    print("   installed 6 sprites, 6 side portraits, 2 overlay pictures and the faces.json rows; every one of %s's %d "
          "image names still resolves" % (who.capitalize(), len(after)))
    if line:
        print("   %s" % line[0].strip())
    print("   next, in the owner's folder: tools/smoke.sh u2_dump; the sprite baseline (docs/UI2_CONTRACTS.md A2); "
          "tools/load_all_saves.sh; the harnesses that show %s" % who.capitalize())
    return 0


def stage(who, folder, out=None):
    """Key the six renders with the new edge, fit them, make the side portraits."""
    from keysprite import key_new, fit, side_portrait, qa, HEIGHT_CM, CANVAS_W, OUT_W
    folder = os.path.expanduser(folder)
    out = os.path.expanduser(out) if out else os.path.join(folder, "staged")
    if who not in HEIGHT_CM:
        raise SystemExit("%s has no height in tools/keysprite.py (HEIGHT_CM)" % who)
    srcs = [("neutral", os.path.join(folder, "%s_base.png" % who))]
    srcs += [(e, os.path.join(folder, "composited", "%s_%s.png" % (who, e))) for e in EXPRESSIONS[1:]]
    missing = [p for _e, p in srcs if not os.path.exists(p)]
    if missing:
        raise SystemExit("nothing staged: %s missing: %s" % ("this render is" if len(missing) == 1 else "these renders are",
                                                             ", ".join(missing)))
    for sub in ("char", "side", "fx"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    for e, src in srcs:
        im = load(src)
        keyed = key_new(src)                 # D58: a new sprite is cut with the new edge, never the old one
        for pr in qa(im, keyed, "%s_%s" % (who, e)):
            print("   !! %s_%s: %s" % (who, e, pr))
        sprite = fit(keyed, HEIGHT_CM.get(who), CANVAS_W.get(who, OUT_W))
        sprite.save(os.path.join(out, "char", "%s_%s.png" % (who, e)))
        side_portrait(sprite).save(os.path.join(out, "side", "%s_%s.png" % (who, e)))
        print("   %-10s %dx%d -> %s" % (e, im.w, im.h, os.path.join(out, "char", "%s_%s.png" % (who, e))))
    import shlex
    q = shlex.quote                     # the folders have spaces in their names: the lines below are pasted
    calm = q(os.path.join(out, "char", "%s_neutral.png" % who))
    print("staged 6 sprites and 6 side portraits in %s" % out)
    print("still to come before the set can go in: the two overlay pictures and the face rows")
    print("   python3 tools/install_face.py --prepare %s --sprite %s --images %s" % (who, calm, q(folder)))
    print("   (the owner runs the blink and talk edit), then for each:")
    print("   python3 tools/install_face.py <render> %s blink|talk --sprite %s --images %s --stage %s"
          % (who, calm, q(folder), q(out)))
    print("   python3 tools/install_set.py %s %s --dry" % (who, q(out)))
    return out


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

    root, out = opt("--root"), opt("--out")
    known = ("--dry", "--stage", "--no-cloth")
    dry, staging, no_cloth = [f in argv for f in known]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2 or [a for a in argv if a.startswith("--") and a not in known]:
        print(__doc__); raise SystemExit(1)
    if staging:
        stage(args[0], args[1], out)
        return
    raise SystemExit(install(args[0], args[1], root, dry, not no_cloth))


if __name__ == "__main__":
    main(sys.argv[1:])
