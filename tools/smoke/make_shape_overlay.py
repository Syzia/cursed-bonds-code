#!/usr/bin/env python3
"""tools/smoke/make_shape_overlay.py -- the test overlay that shapes every place
(docs/UI2_DESIGN.md 7.3, D60; "Acceptance (U0c2)"; written by U0c2).

No real place has a traced shape until its layout sitting. To prove that the
standing harnesses hold in a shaped place before any real shape exists, this
builds an asset overlay (tools/smoke.sh, 2b) in which EVERY place is shaped:

  game/layout/hot_<place>.json   the place's own sidecar (its spots, tips and
                                 the rest, kept), plus "shapes": an 80 px
                                 square round the applied point of every exit
                                 and every registered hotspot (two hotspots
                                 at one point, the storehouse's racks and
                                 armory, share one square), and "keep_tile":
                                 the ids that are planned for the place and
                                 not registered yet, which have no point
  game/layout/pictures.json      every place's picture at revision 2, and a
                                 row for everything made from a picture (its
                                 hour pictures, foreground cut-out, light row
                                 and poses) that says it was made for that
                                 revision, so that nothing else goes stale:
                                 the game then differs from the tree only in
                                 being shaped

It is generated, never committed:

  tools/smoke.sh u2_dump --out shots/art/game_layout.json
  python3 tools/smoke/make_shape_overlay.py --out shots/shape_overlay/all
  SMOKE_ASSETS=shots/shape_overlay/all tools/smoke.sh p2_paths

A harness that has an overlay of its own needs the two in one folder (2b:
SMOKE_ASSETS is used INSTEAD of tools/smoke/assets/<harness>/):

  python3 tools/smoke/make_shape_overlay.py --with tools/smoke/assets/p2_view \\
      --out shots/shape_overlay/p2_view
  SMOKE_ASSETS=shots/shape_overlay/p2_view tools/smoke.sh p2_view

  --dump <file>    the layout dump to read (default shots/art/game_layout.json;
                   the committed tools/art/game_layout.json only when asked)
  --out <dir>      the overlay folder to write (emptied first; it must be
                   under shots/ or outside the repository)
  --with <dir>     another overlay folder to lay under this one: its files are
                   copied, its sidecars and its manifest are merged
  --only a,b       shape only these places (default: all of them)
  --rev <n>        the revision every picture is put at (default 2; 1 builds
                   the "manifest at revision 1" state: nothing is shaped)
  --for-rev <n>    write "for_rev": n into every hot_ file it shapes (a value
                   that is not --rev builds the "stale sidecar" state)
  --size <px>      the side of each square (default 80)
  --selftest       check the counting functions of game/sb_hotspots.rpy (the
                   block between its two "hot_shape:" marker lines) in plain
                   Python against tools/smoke/hot_shape_cases.json, and stop
  --write-cases    rewrite the "expect" part of that file from the functions

Plain Python 3, standard library only. It writes nothing outside --out
(--write-cases: the cases file).
"""
import argparse
import json
import os
import shutil
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASES = os.path.join(ROOT, "tools", "smoke", "hot_shape_cases.json")
HOTSPOTS = os.path.join(ROOT, "game", "sb_hotspots.rpy")
BEGIN = "## >>> hot_shape:"
END = "## <<< hot_shape:"
HOURS = ("evening", "night")


def die(text):
    sys.stderr.write("make_shape_overlay.py: %s\n" % text)
    sys.exit(2)


def shape_block(path=HOTSPOTS):
    """The text between the two marker lines of game/sb_hotspots.rpy, with
    the init block's four leading spaces taken off: plain Python."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    a = [n for n, l in enumerate(lines) if l.strip().startswith(BEGIN)]
    b = [n for n, l in enumerate(lines) if l.strip().startswith(END)]
    if len(a) != 1 or len(b) != 1 or b[0] <= a[0]:
        die("%s: the two 'hot_shape:' marker lines are not there once each" % path)
    return textwrap.dedent("\n".join(lines[a[0] + 1:b[0]])) + "\n"


def shape_functions():
    """The functions of that block, run as plain Python: {name: function}."""
    ns = {}
    exec(compile(shape_block(), "sb_hotspots.rpy (hot_shape block)", "exec"), ns)
    return ns


def cases_expect(ns, cases):
    got = ns["hot_shape_count"](cases["shapes"], dict((k, tuple(v)) for k, v in cases["points"].items()),
                                tuple(cases["size"]), cases["grid"])
    return dict((k, dict(v)) for k, v in got.items()), list(ns["hot_shape_order"](cases["shapes"]))


def selftest(write=False):
    ns = shape_functions()
    with open(CASES, encoding="utf-8") as f:
        cases = json.load(f)
    expect, order = cases_expect(ns, cases)
    if write:
        cases["expect"] = expect
        cases["order"] = order
        with open(CASES, "w", encoding="utf-8") as f:
            json.dump(cases, f, indent=1, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        print("wrote %s" % os.path.relpath(CASES, ROOT))
        return 0
    bad = []
    if order != cases.get("order"):
        bad.append("order: %r, expected %r" % (order, cases.get("order")))
    for hid in sorted(cases["shapes"]):
        if expect.get(hid) != cases["expect"].get(hid):
            bad.append("%s: %r, expected %r" % (hid, expect.get(hid), cases["expect"].get(hid)))
    limits = dict(cases["limits"], polys=tuple(cases["limits"]["polys"]), points=tuple(cases["limits"]["points"]))
    found = ns["hot_shape_findings"]("zz_cases", cases["shapes"], None,
                                     dict((k, tuple(v)) for k, v in cases["points"].items()),
                                     set(cases["shapes"]), set(cases["shapes"]), limits, tuple(cases["size"]))
    if found != cases.get("findings"):
        bad.append("findings: %r, expected %r" % (found, cases.get("findings")))
    for line in bad:
        print("FAIL " + line)
    print("selftest %s: the block of game/sb_hotspots.rpy runs as plain Python and counts the %d test shapes of %s %s"
          % ("FAIL" if bad else "PASS", len(cases["shapes"]), os.path.relpath(CASES, ROOT),
             "differently" if bad else "as recorded"))
    return 1 if bad else 0


def square(x, y, side):
    h = side // 2
    return [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dump", default=os.path.join(ROOT, "shots", "art", "game_layout.json"))
    ap.add_argument("--out")
    ap.add_argument("--with", dest="also", action="append", default=[])
    ap.add_argument("--only", default="")
    ap.add_argument("--rev", type=int, default=2)
    ap.add_argument("--for-rev", dest="for_rev", type=int, default=None)
    ap.add_argument("--size", type=int, default=80)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-cases", action="store_true")
    args = ap.parse_args()

    if args.selftest or args.write_cases:
        return selftest(write=args.write_cases)
    if not args.out:
        die("--out <dir> is needed (see --help)")
    out = os.path.abspath(args.out)
    game = os.path.join(ROOT, "game")
    if out == ROOT or (out + os.sep).startswith(game + os.sep) or (
            (out + os.sep).startswith(ROOT + os.sep) and not (out + os.sep).startswith(os.path.join(ROOT, "shots") + os.sep)):
        die("--out must be under shots/ or outside the repository (the overlay is never committed)")
    if not os.path.isfile(args.dump):
        die("no dump at %s: run tools/smoke.sh u2_dump --out shots/art/game_layout.json" % args.dump)
    dump = read_json(args.dump)

    if os.path.isdir(out):
        shutil.rmtree(out)
    lay = os.path.join(out, "game", "layout")
    os.makedirs(lay)

    # The other overlays first: their files as they are.
    for also in args.also:
        src = os.path.join(os.path.abspath(also), "game")
        if not os.path.isdir(src):
            die("--with %s: it has no game/ folder" % also)
        for base, _dirs, files in os.walk(src):
            for f in files:
                if f == ".DS_Store":
                    continue
                dest = os.path.join(out, "game", os.path.relpath(os.path.join(base, f), src))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(os.path.join(base, f), dest)

    def effective(name):
        """A layout file as the scratch game would hold it: the overlay's
        (a --with folder's), else the tree's; {} when neither has it."""
        for path in (os.path.join(lay, name), os.path.join(game, "layout", name)):
            if os.path.isfile(path):
                got = read_json(path)
                return got if isinstance(got, dict) else {}
        return {}

    places = [p["key"] for p in dump["places"]]
    only = [k for k in args.only.split(",") if k]
    for k in only:
        if k not in places:
            die("--only: %r is not a place" % k)
    stems = dict((p["key"], os.path.splitext(os.path.basename(p["file"]))[0]) for p in dump["places"])
    registered = dict((loc, [r["id"] for r in dump["exits"].get(loc, [])] + [r["id"] for r in dump["hotspots"].get(loc, [])])
                      for loc in places)
    shaped = 0
    squares = 0
    for loc in places:
        if only and loc not in only:
            continue
        side = effective("hot_%s.json" % loc)
        spots = side.get("spots") if isinstance(side.get("spots"), dict) else {}
        side["spots"] = spots
        shapes = {}
        for r in dump["exits"].get(loc, []) + dump["hotspots"].get(loc, []):
            x, y = r["applied"]
            p = spots.get(r["id"])          # a --with overlay may have moved it
            if isinstance(p, list) and len(p) == 2:
                x, y = p
            shapes[r["id"]] = [square(int(x), int(y), args.size)]
        keep = {}
        for hid, place, _kind in dump.get("spot_planned", []):
            if place == loc and hid not in registered[loc]:
                keep[hid] = "planned, not registered yet: it has no point on this picture"
        side["shapes"] = shapes
        if keep:
            side["keep_tile"] = keep
        if args.for_rev is not None:
            side["for_rev"] = args.for_rev
        with open(os.path.join(lay, "hot_%s.json" % loc), "w", encoding="utf-8") as f:
            json.dump(side, f, indent=1, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        shaped += 1
        squares += len(shapes)

    # The manifest: every picture at --rev, and what was made from each still fresh.
    manifest = effective("pictures.json")
    rows = manifest.get("pictures") if isinstance(manifest.get("pictures"), dict) else {}
    if args.rev != 1:
        folders = [game] + [os.path.join(out, "game")]

        def there(rel):
            return any(os.path.isfile(os.path.join(g, rel)) for g in folders)

        def listed(rel):
            names = set()
            for g in folders:
                d = os.path.join(g, rel)
                if os.path.isdir(d):
                    names.update(os.listdir(d))
            return sorted(names)

        for loc in places:
            stem = stems[loc]
            rows.setdefault(stem, {})["rev"] = args.rev
            rows[stem].setdefault("kind", "inplace")
            for hour in HOURS:
                if there("images/bg/%s_%s.png" % (stem, hour)):
                    rows.setdefault("%s_%s" % (stem, hour), {"rev": 1, "kind": "relight", "of": stem, "of_rev": args.rev})
            rows.setdefault("fg_" + loc, {"of": stem, "of_rev": args.rev})
            rows.setdefault("light_" + loc, {"of": stem, "of_rev": args.rev})
        for f in listed("images/place"):
            if not (f.startswith("pose_") and f.endswith(".png")):
                continue
            name = f[:-4]
            parts = name[len("pose_"):].split("__")
            if len(parts) < 2 or parts[0] not in stems or any(p in HOURS for p in parts[2:]):
                continue        # a pose on an hour picture hangs off that picture, which is at revision 1
            rows.setdefault(name, {"of": stems[parts[0]], "of_rev": args.rev})
    manifest["pictures"] = rows
    with open(os.path.join(lay, "pictures.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")

    print("%s: %d places shaped (%d squares of %d px), every picture at revision %d%s%s"
          % (os.path.relpath(out, ROOT) if (out + os.sep).startswith(ROOT + os.sep) else out, shaped, squares, args.size, args.rev,
             ", for_rev %d" % args.for_rev if args.for_rev is not None else "",
             "; laid over %s" % ", ".join(args.also) if args.also else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
