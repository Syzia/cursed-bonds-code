"""
The prompt check: no background, map or pose prompt may ask for the old look.

    python3 tools/check_prompts.py <file> [<file> ...]   # a text file, or a workflow .json
    python3 tools/check_prompts.py --text "Through the windows: old tiled roofs."
    python3 tools/check_prompts.py --selftest

docs/UI2_DESIGN.md 5.1 and K5. Every maker of the second UI overhaul runs
this on a prompt before it writes a workflow (`refuse_if_bad`), and writes
nothing if it finds something.

WHAT IT READS, EXACTLY. Only the per-picture lines: the hour sentence of a
relight, the window line, an `allow` or `change` line, a pose's `spot`, and
the place lines a new composition is built from (the campus record's `as`,
`look`, `court_side`, `words`, `shows` and `facts`). Taken out first, and never read:

  - the six frozen texts in tools/bgs/ (look.txt, keep.txt, keep_outdoor.txt,
    keep_light.txt, stage.txt, map.txt). They are reviewed once, as wholes;
    the look itself has to say "no haze" and "fallen leaves on the floor".
  - the makers' own fixed sentences, TOOL_SENTENCES below. Where one has a
    slot ({thing}), what fills the slot is still read.

WHAT FAILS A PROMPT. In the lines it reads:

  - a banned word or phrase, matched as whole words (so "gold" and "managed"
    pass): worn, old, weathered, aged, moss, mossy, lived-in, dusty,
    scattered, "nothing on", "leaves on", jacket, umbrella, haze, bloom,
    painterly, brushwork, "soft painted", "water mark", watermark;
  - the series' name or a character's (the editor is a closed service and
    refuses them);
  - a count of movable objects ("four desks"). A building's storeys, its rows
    of windows, its doors and single named features are not movable things
    ("five storeys", "two stone lanterns", "one heavy door" pass);
  - "lantern", unless the campus record puts one there (the words are then
    the record's own line, word for word).

Sprite base prompts (tools/chars/prompts/), which must name the house style,
are outside it.

Plain Python; nothing is written anywhere.
"""
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGS = os.path.join(ROOT, "tools", "bgs")
FROZEN = ("look.txt", "keep.txt", "keep_outdoor.txt", "keep_light.txt", "stage.txt", "map.txt")

# Whole words. A trailing "s" is the same word.
BANNED = ["worn", "old", "weathered", "aged", "moss", "mossy", "lived-in", "dusty", "scattered", "nothing on",
          "leaves on", "jacket", "umbrella", "haze", "bloom", "painterly", "brushwork", "soft painted", "water mark",
          "watermark"]

# The series and its people, and this game's own cast. Whole words, any case.
NAMES = ["jujutsu", "kaisen", "jjk", "cursed bonds", "gojo", "satoru", "yuji", "itadori", "megumi", "fushiguro",
         "nobara", "kugisaki", "maki", "zenin", "zen'in", "toge", "inumaki", "panda", "yaga", "masamichi", "shoko",
         "ieiri", "utahime", "iori", "ijichi", "kiyotaka", "sukuna", "ryomen", "nanami", "mei mei", "miwa", "todo",
         "kamo", "geto", "mahito", "kaito", "sana", "kurose", "nade", "oda"]

# Things that can be carried or pushed about: a count of these tells the
# editor to add or take away until the number is right.
MOVABLE = ["desk", "chair", "table", "bench", "benche", "stool", "sofa", "armchair", "cushion", "pillow", "bed",
           "futon", "book", "box", "boxe", "crate", "bag", "plant", "cup", "bottle", "bowl", "tray", "poster",
           "lamp", "mat", "rug", "basket", "bucket", "barrel", "shoe", "locker", "towel", "umbrella", "shelf",
           "shelve", "bookshelf", "bookshelve", "cabinet", "television"]
NUMBERS = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "dozen",
           "couple", "several"]

# The makers' own fixed sentences. They are not per-picture lines, so they are
# taken out before the check; what fills a {slot} is put back and read.
# make_scene_workflow.py and make_redo_workflow.py take their sentences from
# here, so the two cannot drift apart. `--selftest` reads each of these once.
TOOL_SENTENCES = {
    "open_yard": "This is a background picture for a visual novel: a new picture of one part of a traditional "
                 "Japanese mountain school, with timber halls, grey tiled roofs, cedar forest and green mountains "
                 "behind.",
    "open_room": "This is a background picture for a visual novel: a new picture of one room of a traditional "
                 "Japanese mountain school, built of timber and white plaster.",
    "open_map": "This is a background picture for a visual novel: a painted map of one part of a traditional "
                "Japanese mountain school, with timber halls, grey tiled roofs and cedar forest.",
    "ref_neighbour": "Picture {n} is {thing}, already painted: the new picture shows the same school, and every "
                     "building the two pictures share must look the same in both.",
    "ref_building": "Picture {n} is {thing}, cut from a picture already painted: paint it the same wherever it "
                    "shows.",
    "ref_old_camera": "Picture {n} is this place as it was painted before: keep its camera position and the side "
                      "each thing stands on, and design the rest again.",
    "ref_old_school": "Picture {n} is this place as it was painted before: use it only to know the school and the "
                      "camera height; its layout is not kept.",
    "ref_plan": "Picture {n} is a plan of this part of the school in flat colours, north at the top: lay the "
                "buildings out as it does.",
    "the_place": "THE PLACE: {thing}.",
    "the_ground": "The ground: {thing}.",
    "left": "On the left: {thing}.",
    "ahead": "Straight ahead: {thing}.",
    "right": "On the right: {thing}.",
    "bottom": "At the bottom of the picture: {thing}.",
    "bottom_left": "At the bottom of the picture, on the left: {thing}.",
    "bottom_right": "At the bottom of the picture, on the right: {thing}.",
    "same_as": "the same building that stands {where} of picture {n}",
    "clear": "Put at least {count} of these doors or paths either high in the picture, above head height, or at "
             "its far left or right end, clear of the open ground where people stand.",
    "map_at": "On the map, {where}: {thing}.",
    "windows": "Through the windows: {thing}.",
    "add": "Do not remove or tidy away anything, and add nothing except this: {thing}.",
    "change": "Change only this, and keep its outline exactly: {thing}.",
}
SLOT_FREE = ("n", "count", "where")      # slots a tool fills with its own words, never with a line from data


def frozen_texts(bgs=None):
    """{file name: text} of the six frozen texts, each on one line."""
    out = {}
    for name in FROZEN:
        path = os.path.join(bgs or BGS, name)
        if os.path.exists(path):
            out[name] = " ".join(open(path, encoding="utf-8").read().split())
    return out


def text_of(name, bgs=None):
    t = frozen_texts(bgs).get(name)
    if t is None:
        raise SystemExit("tools/bgs/%s is missing: every maker reads it" % name)
    return t


def sentence(key, **slots):
    return TOOL_SENTENCES[key].format(**slots)


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def _tool_regex(template):
    """A tool sentence as a pattern; a slot matches anything, lazily."""
    parts = re.split(r"(\{\w+\})", template)
    rx, read = "", []
    for p in parts:
        if p.startswith("{") and p.endswith("}"):
            rx += "(.+?)"
            read.append(p[1:-1] not in SLOT_FREE)
        else:
            rx += re.escape(p)
    return re.compile(rx), read


def strip_frozen(prompt, bgs=None):
    """The per-picture lines of a prompt: the frozen texts and the tools' own
    sentences taken out, what filled a slot left in."""
    text = " ".join(prompt.split())
    frozen = frozen_texts(bgs)
    for name in sorted(frozen, key=lambda n: -len(frozen[n])):
        text = text.replace(frozen[name], " ")
    # A named addition drops the keep text's last sentence, so the keep texts
    # are also taken out sentence by sentence.
    for name in ("keep.txt", "keep_outdoor.txt", "keep_light.txt"):
        for s in _sentences(frozen.get(name, "")):
            text = text.replace(s, " ")
    for key in sorted(TOOL_SENTENCES, key=lambda k: -len(TOOL_SENTENCES[k])):
        rx, read = _tool_regex(TOOL_SENTENCES[key])
        text = rx.sub(lambda m: " " + " ".join(g for g, r in zip(m.groups(), read) if r) + " ", text)
    return " ".join(text.split())


def _word_rx(word):
    return re.compile(r"(?<![A-Za-z])%s(?:s)?(?![A-Za-z])" % re.escape(word).replace(r"\ ", r"\s+"), re.I)


def record_strings(record):
    """Every string of the campus record a prompt may carry word for word."""
    out = []
    if not record:
        return out
    for row in list(record.get("fixed", [])) + list(record.get("proposed", [])):
        if row.get("kind") == "interior":
            continue
        for key in ("as", "look", "court_side", "words", "shows"):
            if isinstance(row.get(key), str):
                out.append(row[key])
        out += [f for f in row.get("facts", []) if isinstance(f, str)]
    return out


def prompt_lines(row):
    """(key, text) for every string of a record row that a prompt may carry."""
    out = [(key, row[key]) for key in ("as", "look", "court_side", "words", "shows") if isinstance(row.get(key), str)]
    return out + [("facts", f) for f in row.get("facts", []) if isinstance(f, str)]


def findings(text, record=None):
    """What is wrong with these per-picture lines: a list of plain sentences."""
    out = []
    for word in BANNED:
        m = _word_rx(word).search(text)
        if m:
            out.append('"%s" is a banned word (in "...%s...")' % (word, text[max(0, m.start() - 30):m.end() + 30]))
    for name in NAMES:
        m = _word_rx(name).search(text)
        if m:
            out.append('"%s" names the series or a character: a closed editor refuses it' % m.group(0))
    numbers = "|".join(NUMBERS) + r"|\d+"
    nouns = "|".join(sorted(MOVABLE, key=len, reverse=True))
    rx = re.compile(r"(?<![A-Za-z])(%s)\s+(?:[A-Za-z-]+\s+){0,2}?(%s)(?:s)?(?![A-Za-z])" % (numbers, nouns), re.I)
    for m in rx.finditer(text):
        if re.search(r"(?<![A-Za-z])street\s+lamps?$", m.group(0), re.I):
            continue
        out.append('"%s" counts movable things: say what is there, not how many' % m.group(0))
    lantern = text
    for s in sorted((s for s in record_strings(record) if "lantern" in s.lower()), key=len, reverse=True):
        lantern = lantern.replace(s, " ")
    if _word_rx("lantern").search(lantern):
        out.append('"lantern" is asked for where the campus record puts none (tools/bgs/campus.json)')
    return out


def check(prompt, record=None, bgs=None):
    """Findings for a whole prompt, its frozen parts taken out first."""
    return findings(strip_frozen(prompt, bgs), record)


def refuse_if_bad(prompt, what, record=None):
    """For a maker: stop, in plain words, before a workflow is written."""
    bad = check(prompt, record)
    if bad:
        raise SystemExit("the prompt for %s is refused (tools/check_prompts.py):\n  - %s" % (what, "\n  - ".join(bad)))


def prompts_in(path):
    """The prompts a file holds: a workflow's Nano Banana Pro boxes, or the text itself."""
    raw = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        wf = json.loads(raw)
        return [(n.get("title") or "box %s" % n.get("id"), n["widgets_values"][0])
                for n in wf.get("nodes", []) if n.get("type") == "GeminiImage2Node"]
    return [(os.path.basename(path), raw)]


def load_record():
    path = os.path.join(BGS, "campus.json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def selftest():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    record = load_record()
    fails = []

    def ok(what, cond):
        print("  %s  %s" % ("ok  " if cond else "FAIL", what))
        if not cond:
            fails.append(what)

    look = text_of("look.txt")
    ok("the look text alone leaves nothing to read (it says 'no haze' and is not read)", strip_frozen(look) == "")
    for name in FROZEN:
        ok("%s is taken out whole" % name, strip_frozen(text_of(name)) == "")
    # the texts are the wording the third look test proved, with only the changes 5.1 lists
    import make_look_workflow as proven
    want = proven.LOOK3
    for old_words, new_words in (("daylight", "light"),
                                 ("on the floor; everything that belongs to the room",
                                  "on the floor or the ground; everything that belongs to the place"),
                                 ("water marks", "damp patches"), (" of trees, tiled roofs and sky", "")):
        want = want.replace(old_words, new_words)
    ok("look.txt is LOOK3 with the small changes of 5.1 and no other", look == want)
    ok("keep.txt and keep_light.txt together are KEEP, word for word",
       text_of("keep.txt") + " " + text_of("keep_light.txt") == proven.KEEP)
    last = "Do not remove, tidy away or add anything."
    ok("keep_outdoor.txt is keep.txt with outdoor nouns: as many sentences, the same last one, no furniture",
       len(_sentences(text_of("keep_outdoor.txt"))) == len(_sentences(text_of("keep.txt")))
       and _sentences(text_of("keep_outdoor.txt"))[-1] == _sentences(text_of("keep.txt"))[-1] == last
       and "furniture" not in text_of("keep_outdoor.txt"))
    for name in ("keep.txt", "keep_outdoor.txt", "look.txt", "stage.txt", "map.txt"):
        low = text_of(name).lower()
        ok('%s never says "nothing on", "empty" or "tidy away the"' % name,
           "nothing on" not in low and "empty" not in low and "tidy away the" not in low)
    for key, s in sorted(TOOL_SENTENCES.items()):
        ok("the tools' own sentence %r has no banned word in it" % key, not findings(re.sub(r"\{\w+\}", "x", s)))
    ok("a tool sentence's slot is still read",
       "old shed" in strip_frozen(sentence("add", thing="an old shed")) and check(sentence("add", thing="an old shed")))

    # the three cases of 5.1
    import make_redo_workflow as redo
    import make_scene_workflow as scene
    plain = redo.prompt_for(record, "dorm_common", window=False)
    ok("the plain Common Room prompt passes", not check(plain, record))
    lined = redo.prompt_for(record, "dorm_common", window=True, ignore_needs=True)
    ok("the Common Room prompt with its window line passes", "Through the windows:" in lined and not check(lined, record))
    yard = scene.prompt_for(record, "school_yard", [("neighbour", "courtyard"), ("old_school", "school_yard")])
    ok("the School Courtyard prompt passes", not check(yard, record))
    bad = plain.replace(look, sentence("windows", thing="old tiled roofs") + " " + look)
    ok('a window line with "old tiled roofs" fails', any('"old"' in f for f in check(bad, record)))

    # it bites, and only where it should
    for word in BANNED:
        ok('"%s" fails' % word, bool(findings("a wall with %s by the door" % word)))
    for fine in ("a gold handle", "a well managed household", "a folded cloth", "a mossless stone", "bloomington",
                 "a threshold"):
        ok('"%s" passes' % fine, not findings(fine))
    ok('"four desks" fails', bool(findings("four desks under the window")))
    ok('"three low wooden benches" fails', bool(findings("three low wooden benches")))
    for fine in ("a pagoda of five storeys", "two rows of large white-framed windows", "one heavy door",
                 "six sliding bedroom doors", "one pine with a bench under it"):
        ok('"%s" passes' % fine, not findings(fine, record))
    ok('"two stone lanterns" passes where the record says it',
       not findings("a stone path through a kept garden, a pond with two stone lanterns", record))
    ok('"a paper lantern on the table" fails', bool(findings("a paper lantern on the table", record)))
    for name in ("Gojo's office", "the Jujutsu school", "a girl like Maki", "Panda"):
        ok('"%s" fails' % name, bool(findings(name)))
    ok('"a ribbon of todoroki" passes', not findings("a ribbon of todoroki"))
    if record:
        for row in record["fixed"] + record["proposed"]:
            if row.get("kind") == "interior":
                continue
            for key, text in prompt_lines(row):
                if findings(text, record):
                    ok("the record's %s.%s passes" % (row["id"], key), False)
        ok("every line of the campus record a prompt may carry passes", not fails)
    print("check_prompts selftest: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)))
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        raise SystemExit(selftest())
    record = load_record()
    jobs = []
    if "--text" in argv:
        i = argv.index("--text")
        if i + 1 >= len(argv):
            raise SystemExit("--text needs the words to check")
        jobs.append(("the text given", argv[i + 1]))
        del argv[i:i + 2]
    for path in argv:
        if path.startswith("--"):
            print(__doc__); raise SystemExit(2)
        if not os.path.exists(path):
            raise SystemExit("no file at %s" % path)
        jobs += prompts_in(path)
    if not jobs:
        print(__doc__); raise SystemExit(2)
    bad = 0
    for what, prompt in jobs:
        found = check(prompt, record)
        print("%-6s %s" % ("FAIL" if found else "ok", what))
        for f in found:
            print("       - %s" % f)
        bad += bool(found)
    print("check_prompts: %s" % ("PASS, %d prompt%s" % (len(jobs), "" if len(jobs) == 1 else "s") if not bad
                                 else "FAIL, %d of %d" % (bad, len(jobs))))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
