"""
Build the ComfyUI workflow for a picture REDONE IN PLACE: the same camera,
the same walls and things, in the settled look. Also a place's evening and
night, relit from its new day picture, and a room's second Night picture,
`lit`: the room with someone up in it (D61, docs/UI2_DESIGN.md 5.7a).

    python3 tools/make_redo_workflow.py classroom                    # a room, by day
    python3 tools/make_redo_workflow.py dorm --add                   # with its one named addition (the laptop)
    python3 tools/make_redo_workflow.py dorm_common --from-rev1      # from the picture it had before the overhaul
    python3 tools/make_redo_workflow.py --relight dorm_common evening      # an hour picture: evening, night or lit
    python3 tools/make_redo_workflow.py --relight library lit              # the room at Night with someone up in it
    python3 tools/make_redo_workflow.py forest --print               # the prompt and its input; writes nothing
    python3 tools/make_redo_workflow.py classroom --again 1          # one more pair, from two other seeds
    options: --out <folder>   --manifest <pictures.json>   --record <campus.json>   --keep <folder of keep lists>

A place is named by its key (dorm) or by its picture (your_room).

docs/UI2_DESIGN.md 5.1, 5.4, 5.7, K5, K8. The prompt is, in this order:

  1. the keep text: tools/bgs/keep.txt indoors, keep_outdoor.txt outdoors.
     It is KEEP of tools/make_look_workflow.py, the wording the third look
     test proved: every object stays, however small. It never says "nothing
     on the floor": that wording emptied the Common Room.
  2. by day, tools/bgs/keep_light.txt ("Keep the time of day and the
     direction of the light."). A relight leaves it out and says its hour
     instead: one sentence from HOURS below, or the batch's own for a room
     that needs one (a windowless room by lamplight). AT NIGHT A ROOM IS DARK
     UNLESS IT IS `lit` (5.7a): the general indoor `night` sentence is the
     room with every light off, by moonlight (the words the owner chose for
     the Common Room and My Room, O38), and the general `lit` sentence is the
     room with its own lamps on, which was the night sentence before D61. In
     the batch table every indoor night row has words of its own (lights
     off; for the infirmary and the Teachers' Dormitory, their lamps), so
     the general night sentence is only for a relight made by hand. A yard
     has one Night picture and no `lit`, and neither has a room the game's
     table WORLD_LIT does not name (LIT_ROOMS below): `lit` is refused for
     both, as the installer would refuse the render.
  3. by day, where the campus record has one for the room, the window line:
     "Through the windows: ...". It is written by the tool from the record,
     never by hand, and a line that names a neighbour is left out until that
     neighbour's picture is chosen.
  4. tools/bgs/look.txt.

A NAMED ADDITION (--add) replaces the keep text's last sentence with "Do not
remove or tidy away anything, and add nothing except this:" and the `allow`
line of the room's keep list (tools/bgs/keep/<picture>.json, written by the
art-install role before the room's batch). A NAMED CHANGE (--change, used only
by the fallback of 5.2) adds "Change only this, and keep its outline exactly:"
and the keep list's `change` line.

THE INPUT is the game's own file, game/images/bg/<picture>.png, never the
stale backgrounds_chosen folder. --from-rev1 (the Common Room and the
Cafeteria in batches 3a and 4a) takes the picture the place had before this
overhaul, from git, by the manifest's `rev1_commit`: those two are already
redos, and a redo of a redo has never been tried.

THE ORDER IS ENFORCED (K8): a room is not made before the chosen picture of
the yard it stands off, and an hour picture not before its day picture is
installed in the new look (revision 2 or later in game/layout/pictures.json).

Two versions of every picture, from two fixed seeds, saved as
`ui2_<picture>[_<hour>]_a_0000N_.png` and `..._b_...`. The workflow
(`redo_<picture>[_<hour>].json`) goes to ~/Desktop/JJK Game images/ui2/. It
queues nothing: the owner presses Run (K14). Then tools/install_redo.py proves
that nothing moved, vanished or appeared before either version can go in.

tools/art_batch.py <n> calls this for a whole sitting; run it by hand only for
one picture.

Plain Python.
"""
import sys, os, json, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_prompts
import check_campus
import make_scene_workflow as kit
from make_scene_workflow import Refused

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEEP_DIR = os.path.join(ROOT, "tools", "bgs", "keep")
S = check_prompts.sentence
LAST = "Do not remove, tidy away or add anything."

# (hour, indoors): the hour sentence of a relight. Light is only ever switched
# on where the picture already has it.
HOURS = {
    ("evening", True): "Change the time of day to early evening: low warm orange sunlight slants in through the "
                       "windows, long soft shadows cross the floor, and the sky outside is orange and pink.",
    ("evening", False): "Change the time of day to early evening: a warm orange and pink sunset sky, and low "
                        "golden sunlight with long soft shadows. Windows already in the picture catch the light or "
                        "begin to glow warm; add no new light.",
    # the room with nobody up in it (5.7a): the words chosen for the Common Room and My Room (art_3c, O38)
    ("night", True): "Change the time of day to night, with every light in the room switched off: the ceiling "
                     "light and every lamp are dark. Outside the windows it is night, under a deep blue sky with "
                     "stars. The room is lit only by cool blue moonlight coming in through the windows, which lies "
                     "in pale patches on the floor and the furniture. The room is dim, but everything in it can "
                     "still be seen clearly.",
    # the room with someone up in it (5.7a): until D61 this was the indoor night sentence
    ("lit", True): "Change the time of day to night: outside the windows it is dark, under a deep blue night "
                   "sky. The room's own lamps and ceiling lights are switched on and fill it with warm light and "
                   "soft shadows.",
    ("night", False): "Change the time of day to night: a deep blue night sky with a few stars and a faint moon, "
                      "and cool blue moonlight on everything, with soft shadows. Windows and lamps already in the "
                      "picture glow warm yellow; add no new light.",
}
HOUR_NAMES = ("evening", "night", "lit")
LIT = "lit"
# The rooms that have a lit picture: the game's table WORLD_LIT (sb_world.rpy; 5.7a), by place key. The installer reads
# the same list from the layout dump (game_layout.lit_places()); tools/test_art_tools.py holds the two together.
LIT_ROOMS = ("library", "yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room", "dorm", "dojo")


def place_of(rec, name):
    """A place by its key or by its picture's name."""
    if name in rec.places:
        return name
    for key, p in rec.places.items():
        if p["stem"] == name:
            return key
    raise Refused("%s is not a place of the campus record" % name)


def keep_list(rec, place, keep_dir=None):
    p = rec.places[place]
    for name in (p["stem"], place):
        path = os.path.join(keep_dir or KEEP_DIR, name + ".json")
        if os.path.exists(path):
            return json.load(open(path, encoding="utf-8"))
    return None


def named(rec, place, key, keep_dir=None):
    """The `allow` or `change` line of a room's keep list, in words."""
    p = rec.places[place]
    kl = keep_list(rec, place, keep_dir)
    rows = [row.get("name", "").strip() for row in (kl or {}).get(key, []) if row.get("name", "").strip()]
    if not rows:
        raise Refused("%s has no `%s` row in its keep list (tools/bgs/keep/%s.json): the art-install role writes "
                      "it before the room's batch, and the prompt says exactly what it names" % (p["name"], key, p["stem"]))
    return "; ".join(rows)


def lit_asked(p, place, hour):
    """Refused when the hour is lit and the place has no lit picture: a yard, or a room the game's table does not
    name. The installer would refuse the render (install_redo.py), so nothing is written for it."""
    if hour != LIT:
        return
    if not p["indoor"]:
        raise Refused("%s is outdoors: a yard has one Night picture and no lit one (5.7a)" % p["name"])
    if place not in LIT_ROOMS:
        raise Refused("%s has no lit picture: only a room of the game's WORLD_LIT has one (5.7a). Its Night picture "
                      "is --relight %s night" % (p["name"], place))


def prompt_for(record, place, hour=None, add=None, change=None, window=True, ignore_needs=False, hour_words=None):
    """The prompt of a redo in place (hour None) or of a relight ("evening", "night", "lit").
    add / change: the words of the keep list's `allow` / `change` line."""
    rec = check_campus.Rec(record)
    p = rec.places[place]
    keep = check_prompts.text_of("keep.txt" if p["indoor"] else "keep_outdoor.txt")
    out = []
    if add:
        if not keep.endswith(LAST):
            raise SystemExit("the keep text no longer ends %r: a named addition replaces that sentence" % LAST)
        out.append(keep[:-len(LAST)].strip())
        out.append(S("add", thing=add.rstrip(".")))
    else:
        out.append(keep)
    if change:
        out.append(S("change", thing=change.rstrip(".")))
    if hour is None:
        out.append(check_prompts.text_of("keep_light.txt"))
        if window and p["indoor"]:
            line = kit.window_line(rec, place, ignore_needs)
            if line:
                out.append(line)
    else:
        if hour not in HOUR_NAMES:
            raise Refused("the hour is evening, night or lit, not %r" % hour)
        lit_asked(p, place, hour)
        out.append(hour_words or HOURS[(hour, bool(p["indoor"]))])
    out.append(check_prompts.text_of("look.txt"))
    return " ".join(out)


def rev1_picture(manifest, stem, work_dir, root=None):
    """The picture a place had before this overhaul, as a file."""
    root = root or ROOT
    row = (manifest.get("pictures") or {}).get(stem)
    game = os.path.join(root, "game", "images", "bg", stem + ".png")
    if row is None:
        return game          # nothing installed yet: the game's file IS revision 1
    commit = row.get("rev1_commit")
    if not commit:
        raise Refused("%s.png: the manifest has no rev1_commit for it, so its picture from before the overhaul "
                      "cannot be taken from git" % stem)
    os.makedirs(work_dir, exist_ok=True)
    out = os.path.join(work_dir, "ui2_rev1_%s.png" % stem)
    p = subprocess.run(["git", "-C", root, "show", "%s:game/images/bg/%s.png" % (commit, stem)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0 or not p.stdout:
        raise Refused("%s.png: git has no such picture at commit %s" % (stem, commit))
    open(out, "wb").write(p.stdout)
    return out


def redo_job(record, manifest, name, hour=None, from_rev1=False, add=False, change=False, hour_words=None,
             again=0, root=None, work_dir=None, keep_dir=None):
    """The job for one picture redone in place or relit, or Refused."""
    root = root or ROOT
    rec = check_campus.Rec(record)
    place = place_of(rec, name)
    p = rec.places[place]
    stem = p["stem"]
    game = os.path.join(root, "game", "images", "bg", stem + ".png")
    if hour is None:
        if p["how"] != "inplace":
            raise Refused("%s is composed again, not redone in place: use tools/make_scene_workflow.py" % p["name"])
        kit.k8_place(rec, place)
        src = rev1_picture(manifest, stem, work_dir or kit.OUT, root) if from_rev1 else game
        if not os.path.exists(src):
            raise Refused("no picture at %s" % src)
        prompt = prompt_for(record, place, add=named(rec, place, "allow", keep_dir) if add else None,
                            change=named(rec, place, "change", keep_dir) if change else None)
        label = p["name"]
        title = "%s, %s" % (p["name"], "as it was before the overhaul" if from_rev1 else "as it is in the game")
        checklist = ["nothing has moved: yes / no", "everything that was in the picture is still there: yes / no",
                     "nothing new has appeared%s: yes / no" % (" except what was asked for" if add else ""),
                     "the walls are clean and the floor is free of leaves and dust: yes / no"]
        if "Through the windows:" in prompt:
            checklist.append("the windows show what the record says: yes / no")
        return kit.job(stem, label, prompt, [(title, src)], again, checklist, kind="inplace", place=place)
    lit_asked(p, place, hour)          # before "its day picture is not installed": that would promise a picture
    if check_campus.rev_of(manifest, stem) < 2:
        raise Refused("%s's %s cannot be made yet: its day picture is not installed in the new look (batch %s). An "
                      "hour picture is relit from the day picture the owner chose." % (p["name"], hour, p.get("batch", "?")))
    if not os.path.exists(game):
        raise Refused("no picture at %s" % game)
    prompt = prompt_for(record, place, hour=hour, hour_words=hour_words)
    checklist = ["nothing has moved: yes / no", "everything that was in the day picture is still there: yes / no",
                 "it is plainly %s, in the windows and the sky too: yes / no" % ("night" if hour == LIT else hour)]
    if hour == LIT:
        checklist.append("the room's own light is on, as its sentence says, and no lamp has been added: yes / no")
    elif hour == "night" and p["indoor"] and not hour_words:
        checklist.append("every light in the room is off: yes / no")
    label = "%s, %s" % (p["name"], "lit at night" if hour == LIT else hour)
    return kit.job("%s_%s" % (stem, hour), label, prompt,
                   [("%s by day, as installed" % p["name"], game)], again, checklist, kind="relight", place=place)


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

    def flag(name):
        if name in argv:
            argv.remove(name)
            return True
        return False

    out_dir, again, keep_dir = opt("--out"), int(opt("--again") or 0), opt("--keep")
    record = check_campus.load_record(opt("--record"))
    manifest = check_campus.load_manifest(path=opt("--manifest"))
    hour = None
    if "--relight" in argv:
        i = argv.index("--relight")
        rest = argv[i + 1:i + 3]
        if len(rest) != 2 or rest[1] not in HOUR_NAMES:
            raise SystemExit("--relight needs a place and an hour: --relight dorm_common evening|night|lit")
        name, hour = rest
        del argv[i:i + 3]
        argv.append(name)
    from_rev1, add, change, show = flag("--from-rev1"), flag("--add"), flag("--change"), flag("--print")
    if len(argv) != 1 or argv[0].startswith("--"):
        print(__doc__); raise SystemExit(1)
    out_dir = out_dir or kit.OUT
    try:
        j = redo_job(record, manifest, argv[0], hour, from_rev1, add, change, None, again, work_dir=out_dir,
                     keep_dir=keep_dir)
    except Refused as e:
        raise SystemExit(str(e))
    check_prompts.refuse_if_bad(j["prompt"], j["label"], record, j.get("place"))
    if show:
        print(j["prompt"])
        for n, (title, f) in enumerate(j["inputs"], 1):
            print("picture %d: %s  <- %s" % (n, title, f))
        return
    path = os.path.join(out_dir, "redo_%s.json" % j["stem"])
    intro = ("One picture, relit from its day picture: only the hour changes." if hour else
             "One picture, redone in place: the same camera and the same things, in the new look.")
    wf = kit.write_workflow(path, j["label"], intro, [j], out_dir, record)
    print("%-22s %d versions, about $%.2f" % (j["stem"], len(kit.renders_in(wf)), len(kit.renders_in(wf)) * kit.COST))
    print("   workflow -> %s" % path)


if __name__ == "__main__":
    main(sys.argv[1:])
