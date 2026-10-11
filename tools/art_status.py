"""
Where the art stands: which pictures are in the new look, which room sets are
half made, what has gone stale, and what a change to the campus record
touches.

    python3 tools/art_status.py                 # the table
    python3 tools/art_status.py --check         # also fails on anything that must not happen
    options: --root <a copy of the project>   --record <campus.json>

docs/UI2_DESIGN.md 5.5, K7, K9. It reads game/layout/pictures.json (the
manifest the install tools write), the picture files, and the campus record.
It is the first thing in every checkpoint note.

  IN THE NEW LOOK        every picture at revision 2 or later, with how it was
                         made and from which render.
  HALF-MADE ROOM SETS    a room whose day picture is in the new look while an
                         evening, night or lit picture of it is still the old
                         one. The game tints the new day picture at that hour
                         (K7); but a scene or a memory that names the old
                         hour picture itself still shows it. The five that
                         are named so are marked. A LIT picture (5.7a: the
                         room at Night with someone up in it) that was made
                         for the old room is not shown either: until it is
                         remade the room is dark at Night whoever is up.
  STALE                  a foreground, a pose, an hour picture or a light row
                         made for an older revision of its room. The game
                         does not use it; it is remade in its batch.
  THE RECORD             the unmade pictures whose prompt changed because a
                         chosen picture rewrote a proposal.

--check exits 1 when
  - a foreground file that was ever installed is missing: every
    game/images/fg/fg_*.png the game had when this overhaul began, every one
    added since, and every one the manifest names. A save made on a line of dialogue in that room holds the file's
    path, so it is never deleted; a room that loses its foreground gets a
    fully transparent file of the same name (K9);
  - a manifest row names a picture whose file is missing;
  - a manifest row depends on a picture the manifest and the game do not have.

Plain Python.
"""
import sys, os, json, subprocess

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import check_campus

ROOT = os.path.dirname(TOOLS)
HOURS = ("evening", "night", "lit")       # lit: a room's second Night picture, someone up in it (5.7a)
HALF_WORDS = {"lit": "until it is remade the room shows its dark Night picture even with someone up in it"}
BASE = "d2eb9db"            # the commit the second UI overhaul's baselines were written from (docs/UI2_CONTRACTS.md A2)
# K7: the hour pictures a written scene or a memory row shows by name, whatever the gates say.
NAMED = {"your_room_night": "scenes show `bg your_room night` five times",
         "rooftop_evening": "two scenes and a memory show `bg rooftop evening`",
         "rooftop_night": "a memory shows `bg rooftop night`",
         "infirmary_night": "a memory shows `bg infirmary night`",
         "dorm_common_night": "the memory \"Eleven Tuesdays\" shows `bg dorm_common night`"}


def file_of(root, stem):
    """Where a manifest stem's file is, or None for a row that has no file of its own."""
    if stem.startswith("fg_"):
        return os.path.join(root, "game", "images", "fg", stem + ".png")
    if stem.startswith("pose_"):
        return os.path.join(root, "game", "images", "place", stem + ".png")
    if stem.startswith("light_"):
        return None
    return os.path.join(root, "game", "images", "bg", stem + ".png")


def ever_installed_fg(root):
    """Every game/images/fg/fg_*.png a save can hold the path of: the ones in the tree this overhaul began
    from (commit BASE, which the baselines were written from; phase 2 shipped exactly those), every one added
    since on this branch, and the ones in the tree now."""
    out = set()

    def names(text):
        for line in text.decode("utf-8", "replace").splitlines():
            name = os.path.basename(line.strip())
            if name.startswith("fg_") and name.endswith(".png"):
                out.add(name)

    for repo in dict.fromkeys([root, ROOT]):
        git = lambda *a: subprocess.run(["git", "-C", repo] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        head = git("ls-tree", "-r", "--name-only", "HEAD", "--", "game/images/fg")
        if head.returncode != 0:
            continue
        names(head.stdout)
        base = git("ls-tree", "-r", "--name-only", BASE, "--", "game/images/fg")
        if base.returncode == 0:
            names(base.stdout)
            since = git("log", "%s..HEAD" % BASE, "--pretty=format:", "--name-only", "--diff-filter=A", "--", "game/images/fg")
            if since.returncode == 0:
                names(since.stdout)
        break
    return out


def status(root, record_path=None):
    manifest = check_campus.load_manifest(root)
    pics = manifest.get("pictures") or {}
    rev = lambda stem: check_campus.rev_of(manifest, stem)
    lines, faults = [], []

    new = sorted((k, r) for k, r in pics.items() if "rev" in r and int(r["rev"]) >= 2)
    lines.append("IN THE NEW LOOK (%d picture%s)" % (len(new), "" if len(new) == 1 else "s"))
    if not new:
        lines.append("   none yet: with no manifest every picture is today's (revision 1)")
    for stem, r in new:
        extra = []
        if r.get("batch") is not None:
            extra.append("batch %s" % r["batch"])
        if r.get("sharp"):
            extra.append("%.1f times as sharp as before" % (r["sharp"][1] / max(r["sharp"][0], 1e-6)))
        if r.get("waiver"):
            extra.append("stands against a waived fact: %s" % r["waiver"])
        lines.append("   %-26s revision %-2d %-9s %s%s" % (stem, int(r["rev"]), r.get("kind", "?"), r.get("render", ""),
                                                         "   (" + "; ".join(extra) + ")" if extra else ""))
        path = file_of(root, stem)
        if path and not os.path.exists(path):
            faults.append("the manifest has %s at revision %s and its file is missing (%s)" % (stem, r["rev"], os.path.relpath(path, root)))

    half = []
    for stem, r in sorted(pics.items()):
        if r.get("kind") not in ("inplace", "composed") or int(r.get("rev", 1)) < 2:
            continue
        for hour in HOURS:
            h = "%s_%s" % (stem, hour)
            path = file_of(root, h)
            if not os.path.exists(path):
                continue
            row = pics.get(h)
            if row is None or row.get("of_rev") != rev(stem):
                half.append((h, stem, NAMED.get(h)))
    lines.append("")
    lines.append("HALF-MADE ROOM SETS (%d)" % len(half))
    for h, stem, named in half:
        hour = h[len(stem) + 1:]
        lines.append("   %-26s is still the picture made for the old %s; %s%s" % (
            h, stem, HALF_WORDS.get(hour, "until it is remade that hour shows the new day picture tinted"),
            "" if not named else ". BUT %s: those still show the old picture" % named))

    stale = []
    for stem, r in sorted(pics.items()):
        if "of" not in r:
            continue
        parent = r["of"]
        if parent not in pics and not os.path.exists(file_of(root, parent) or ""):
            faults.append("%s depends on %s, which the manifest and the game do not have" % (stem, parent))
        if r.get("of_rev") != rev(parent):
            stale.append((stem, parent, r.get("of_rev"), rev(parent)))
        path = file_of(root, stem)
        if path and not os.path.exists(path):
            faults.append("the manifest names %s and its file is missing (%s)" % (stem, os.path.relpath(path, root)))
    # a dependant with no row is fresh only while its parent is at revision 1 (5.5)
    for folder, prefix in (("fg", "fg_"), ("place", "pose_")):
        d = os.path.join(root, "game", "images", folder)
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            stem = name[:-4]
            if not name.endswith(".png") or not stem.startswith(prefix) or stem in pics:
                continue
            body = stem[len(prefix):]
            if prefix == "pose_":
                place, _, rest = body.partition("__")
                bits = [b for b in rest.split("__")[1:] if b != "asleep"]
                parent = _stem_of(root, place) + ("_" + bits[0] if bits else "")
            else:
                parent = None
                for hour in HOURS:
                    if body.endswith("_" + hour):
                        parent = _stem_of(root, body[:-len(hour) - 1]) + "_" + hour
                parent = parent or _stem_of(root, body)
            day = parent
            for hour in HOURS:
                if parent.endswith("_" + hour):
                    day = parent[:-len(hour) - 1]
            # name the picture whose revision moved: the hour picture itself, or the day picture it belongs to
            if rev(parent) > 1:
                stale.append((stem, parent, 1, rev(parent)))
            elif rev(day) > 1:
                stale.append((stem, day, 1, rev(day)))
    lines.append("")
    lines.append("STALE (%d): made for an older picture, so the game does not use it" % len(stale))
    for stem, parent, was, now in stale:
        lines.append("   %-44s made for revision %s of %s, which is now at revision %s" % (stem, was, parent, now))

    rpath = record_path or os.path.join(root, "tools", "bgs", "campus.json")
    lines.append("")
    if os.path.exists(rpath):
        record = check_campus.load_record(rpath)
        rec = check_campus.Rec(record)
        rows = [(stem, [t for t in pic.get("touches", []) if t in rec.places and rec.chosen(t) is None
                        or t not in rec.places and t not in record.get("pictures", {})])
                for stem, pic in sorted(record.get("pictures", {}).items())]
        rows = [(stem, t) for stem, t in rows if t]
        lines.append("THE RECORD: %d chosen picture%s; %d of them changed a proposal that an unmade picture's prompt carries"
                     % (len(record.get("pictures", {})), "" if len(record.get("pictures", {})) == 1 else "s", len(rows)))
        for stem, touches in rows:
            lines.append("   choosing %-18s changed the prompt of: %s" % (stem, ", ".join(touches)))
        for w in record.get("waived", []):
            lines.append("   WAIVED: %s stands against the fixed fact %s (the owner, %s)" % (w.get("picture"), w.get("fact"), w.get("date")))
    else:
        lines.append("THE RECORD: no campus record at %s" % rpath)

    # K9
    need = ever_installed_fg(root) | set(k + ".png" for k in pics if k.startswith("fg_"))
    fg_dir = os.path.join(root, "game", "images", "fg")
    missing = sorted(n for n in need if not os.path.exists(os.path.join(fg_dir, n)))
    for n in missing:
        faults.append("the foreground file game/images/fg/%s was installed once and is missing: a save made in dialogue "
                      "in that room holds its path. Put it back (a fully transparent picture of the same name if the "
                      "room no longer has a foreground)" % n)
    lines.append("")
    lines.append("FOREGROUND FILES: %d ever installed, %d missing" % (len(need), len(missing)))
    return lines, faults


def _stem_of(root, place):
    """A place's picture name. `dorm` is the one place whose picture is not named for it (K1)."""
    return {"dorm": "your_room"}.get(place, place)


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

    root, record = opt("--root") or ROOT, opt("--record")
    check = "--check" in argv
    if [a for a in argv if a != "--check"]:
        print(__doc__); raise SystemExit(1)
    lines, faults = status(root, record)
    print("\n".join(lines))
    if check:
        print("")
        for f in faults:
            print("FAIL  %s" % f)
        print("art_status --check: %s" % ("FAIL (%d)" % len(faults) if faults else "PASS"))
        raise SystemExit(1 if faults else 0)
    if faults:
        print("\n%d thing%s --check would fail on" % (len(faults), "" if len(faults) == 1 else "s"))


if __name__ == "__main__":
    main(sys.argv[1:])
