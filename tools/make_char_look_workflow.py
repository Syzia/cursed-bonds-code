"""
Build the ComfyUI workflow that tries two redos of the characters that feel off.

    python3 tools/make_char_look_workflow.py
    python3 tools/make_char_look_workflow.py --who yuji,maki
    python3 tools/make_char_look_workflow.py --list      # every prompt, and what a Run costs

The owner (7 Oct 2026): "redoing the characters aswell. Some of them feel
off", and, asked which: "Yuji, maki, shoko, maybe nobara". This is the look
test for those four and nobody else, built the way the background look tests
were (tools/make_look_workflow.py: the same node copying, the same grid).

Each box gives Nano Banana Pro one picture and one instruction: the neutral
sprite the game has today (game/images/char/<who>_neutral.png), laid on flat
mid-grey, and one of two treatments.

    A  corrected   the same pose and design, with what looks off put right
    B  redrawn     the same person and outfit drawn afresh, relaxed standing pose

No prompt names a character or the series: closed editors refuse them. Each
describes the person only by what is in the picture, lists what must not
change (hair, eyes, outfit and its colours, marks and accessories), and keeps
them fully and ordinarily dressed as they are.

It writes, into ~/Desktop/JJK Game images/look_test/:

    look_chars.json           drag it into the LOCAL ComfyUI, press Run
    look_char_in_<who>.png    the sprite as it is today on grey (also copied
                              to ComfyUI's input folder)

The input picture is the sprite's own pixels, not resized: the figure is cut
to its outline and set on a 9:16 grey canvas with an even margin, so all four
fill the frame alike (Nobara sits small and low on the game's canvas).

The workflow is a grid: one row for each character, the sprite as it is now on
the left, then A and B with the result under each. Results land in
~/ComfyUI-Shared/output as `look_char_<who>_<A|B>_0000N_.png`. Nothing is
installed from this test. A character that is redone afterwards needs its six
faces made again (docs/ASSET_PIPELINE.md).

Shape and size: the node offers 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9
and 21:9. The game's sprite canvas is 760x1400 (0.54 wide for 1 high) and
9:16 is 0.5625, the nearest by far (2:3 is 0.67). At 9:16 the sizes are
768x1376 (1K), 1536x2752 (2K) and 3072x5504 (4K). The sprite is 1400 high, so
2K is the smallest that is not smaller than the game's own.

Cost: Nano Banana Pro is a paid partner node. Its own price data
(/object_info/GeminiImage2Node, price_badge) gives 1K and 2K as $0.1608 a
picture and 4K as $0.288. Eight boxes at 2K: about $1.29 a Run. Nothing runs
on this Mac's GPU.

Pillow: the system python3 has none. If it is missing, this script starts
itself again with ComfyUI's own Python.
"""
import sys, os, json, shutil

COMFY_PY = os.path.expanduser("~/ComfyUI-Installs/ComfyUI/standalone-env/bin/python")
try:
    from PIL import Image
except ImportError:
    if os.path.exists(COMFY_PY) and os.path.realpath(sys.executable) != os.path.realpath(COMFY_PY):
        os.execv(COMFY_PY, [COMFY_PY, os.path.abspath(__file__)] + sys.argv[1:])
    raise SystemExit("Pillow is needed: run this with %s" % COMFY_PY)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_look_workflow import ROOT, OUT, COMFY_INPUT, COST, RESOLUTION, kit, finish, CELL_W, GEM_H

WHO = ["yuji", "maki", "shoko", "nobara"]
NAMES = {"yuji": "Yuji", "maki": "Maki", "shoko": "Shoko", "nobara": "Nobara"}
LETTERS = ["A", "B"]
SHORT = {"A": "corrected", "B": "redrawn"}
ASPECT = "9:16"            # 1536x2752 at 2K; the sprite canvas is 760x1400
GREY = (128, 128, 128)     # flat mid-grey: none of the four has grey on them
MARGIN = 0.06              # of the picture's height, above the hair and below the soles
SEED = 2901                # then 2902, 2903...: fixed, all different

# The same in all eight prompts. {keep} is that character's own list.
HEAD = ("This is a full-body standing character sprite for a visual novel, in cel-shaded anime style, on a "
        "plain grey background. Draw this same character again. It must stay recognisably the same person, "
        "at the same age. Do not change: {keep} Keep the expression on the face as it is now. The "
        "character stays fully and ordinarily dressed exactly as now: do not remove, shorten, open or add "
        "any piece of clothing. Show the whole figure from the top of the hair to the soles of the shoes, "
        "centred, with a small even margin all round and nothing cut off. Background: one flat, even "
        "mid-grey, with no floor, no cast shadow, no gradient, no text and nothing else in the picture. "
        "Output a 9:16 picture.")

# The benchmark, in words: what the sprites the owner did not name look like.
FINISH = ("THE FINISH: a clean character design sheet from a modern high-budget TV anime. Confident, even, "
          "dark outlines of medium weight. Flat clean colour with two-tone cel shading: one crisp-edged "
          "shadow tone, and on dark cloth a few crisp lighter streaks along the folds. No gradients, no soft "
          "airbrushing, no glossy or satin shine, no painterly texture, no realistic rendering. A simple "
          "anime face: clean eyes, a small simple nose, a simple mouth line.")

A_OPEN = ("TREATMENT: correct this drawing, do not redesign it. Keep the pose as it is (the same stance, the "
          "same angle of the head and body, the arms, legs and feet where they are), except where a "
          "correction below asks for a small change. Correct only the following, and change nothing else.")
B_OPEN = ("TREATMENT: draw this character afresh, as a new drawing and not a tracing of this one. A natural, "
          "relaxed standing pose facing the viewer, the weight settled comfortably, the shoulders loose, "
          "both feet flat on the ground, the head level.")

# who: (his/her, what must not change, what A corrects, B's pose and proportion,
#       one plain line for the owner on what looks off). Plain literals only.
# CHARS-BEGIN
CHARS = {
    "yuji": ("his",
        "the short spiky pink hair with the darker close-cut sides; the brown eyes; the small line mark "
        "under each eye; the red hoodie with its drawstrings; the dark open jacket with gold buttons worn "
        "over it; the dark trousers; the white lace-up trainers; all of their colours.",
        "The arms hang like a mannequin's, held stiffly away from the body with the hands half open: let "
        "them hang naturally, with relaxed hands resting close to the thighs. The eyes are too round and "
        "wide, like a doll's: make them a little smaller and sharper, with a firmer jaw and chin, so that "
        "he reads as a sturdy, athletic high-school boy and not a small child. The shoulders are narrow for "
        "the head: make them a little broader. The jacket and the trousers are drawn as flat dark shapes "
        "with thin lines: keep their colour, and give them the crisp fold lines and the few crisp lighter "
        "streaks of the finish described below.",
        "One hand in his trouser pocket and the other relaxed at his side, the weight on one leg, an easy "
        "and friendly stance. The proportions of a sturdy, athletic high-school boy: the shoulders clearly "
        "wider than the head, about seven heads tall, the hands and feet in proportion.",
        "stands like a mannequin, arms held stiffly out from his sides; round doll-like eyes and narrow "
        "shoulders make him look younger and softer than the others; his jacket and trousers are flat "
        "black with a thin line, where theirs have a firm line, crisp folds and lighter streaks."),
    "maki": ("her",
        "the dark green hair in a high ponytail, with the straight fringe and the locks at the sides; the "
        "amber eyes; the thin metal-framed glasses; the navy high-collared uniform jacket with its white "
        "collar edge, white cuffs and single gold button; the navy straight skirt, no shorter than it "
        "is now; the white loose socks; the brown lace-up shoes; all of their colours.",
        "The arms hang dead straight and symmetrical at the sides: let them hang naturally, the elbows "
        "slightly bent and the hands relaxed. The head is small for the body and the legs are over-long, "
        "so she reads as a tall adult: make the head a little larger and the legs a natural length, the "
        "proportions of an athletic high-school girl about seven heads tall. The jacket and the skirt are drawn "
        "clinging to the body: draw them as sturdy uniform cloth that hangs straight and a little loose, "
        "the jacket from the shoulders to its hem and the skirt from the waist to its hem, with a few "
        "plain straight folds and no dark shadow shapes on the front of either. Remove the small stray green speck on one shoe.",
        "The weight on one leg, one hand resting lightly on her hip and the other arm relaxed at her side, "
        "the shoulders square: a confident, athletic stance. The proportions of an athletic high-school "
        "girl, about seven heads tall. The uniform is sturdy cloth that hangs straight and a little loose, "
        "the jacket from the shoulders to its hem and the skirt from the waist to its hem, with a few "
        "plain straight folds.",
        "stands to attention, arms dead straight at her sides; a small head on long legs makes her read as "
        "a tall adult, not a student; her jacket and skirt are drawn clinging to her instead of hanging "
        "like uniform cloth; one shoe has a stray green speck left from cutting her out."),
    "shoko": ("her",
        "the long straight brown hair with its centre parting; the brown eyes; the tired shadow under the "
        "eyes; the small mole beneath one eye, on the same side as now; the blue turtleneck sweater; the "
        "long white lab coat worn open; the dark slim trousers; the beige heeled shoes; all of their "
        "colours.",
        "The face is drawn in a different, half-realistic style from the rest of the cast: a long face "
        "with a realistic nose and lips and heavily lined bags under the eyes. Redraw the face as a simple "
        "anime face in the finish described below: a slightly shorter face, larger and simpler eyes, a "
        "small simple nose, a simple mouth line, and the tiredness shown by one small flat shadow under "
        "each eye. The outline is thin and scratchy: make it the confident medium line of the finish, and "
        "keep the white coat's shading to one clean pale blue-grey shadow tone along the folds. "
        "The legs are over-long: make them a natural length, the proportions of an adult woman about seven "
        "and a half heads tall.",
        "Both hands in the pockets of the lab coat, the weight on one leg, unhurried and at ease. The "
        "proportions of an adult woman, about seven and a half heads tall, with legs of a natural length. "
        "A simple anime face in the finish described below, the tiredness shown by one small flat shadow "
        "under each eye.",
        "looks as if she came from a different show: a long, half-realistic face with a real nose, lips "
        "and heavily lined eye bags, a thin scratchy outline, and very long legs."),
    "nobara": ("her",
        "the chin-length orange-brown bob with its side parting; the brown eyes; the navy high-collared "
        "cropped uniform jacket with gold buttons; the white shirt hem showing beneath it; the "
        "high-waisted navy pleated skirt with its gold buttons, at its present length; the dark brown "
        "tights; the brown loafers; the hand resting on the hip; all of their colours.",
        "The feet are planted wide and turned "
        "outward: bring them to a natural shoulder width, pointing more nearly forward. Draw the hand on "
        "the hip with clean, clearly separated fingers. The front of the jacket is shaded with heavy dark "
        "shapes: draw it as sturdy uniform cloth that hangs straight from the shoulders to its hem in a "
        "few plain folds.",
        "Keep the spirit of the present pose: one hand resting on her hip, the other arm relaxed at her "
        "side, the weight on one leg, the chin up, self-assured. The feet a natural shoulder width apart. "
        "The proportions of a high-school girl, about six and a half heads tall. The uniform is sturdy "
        "cloth that hangs straight in a few plain folds.",
        "looks right: she is drawn in the same finish as the three used as the benchmark, and the pose "
        "and the face work. The only things to pick at are the wide turned-out feet, the heavy shading "
        "on the jacket front, and that she sits smaller and lower on the canvas than everyone else."),
}
# CHARS-END

# The grid: taller cells than the background tests, the pictures are upright.
SAVE_H = 660
CELL_H = GEM_H + 60 + SAVE_H
ROW_H = CELL_H + 120


def stem(who, letter):
    return "look_char_%s_%s" % (who, letter)


def in_name(who):
    return "look_char_in_%s.png" % who


def sprite_file(who):
    return os.path.join(ROOT, "game", "images", "char", who + "_neutral.png")


def prompt_for(who, letter):
    _, keep, fix, fresh, _ = CHARS[who]
    head = HEAD.replace("{keep}", keep)
    if letter == "A":
        return "%s %s %s %s" % (head, A_OPEN, fix, FINISH)
    return "%s %s %s %s" % (head, B_OPEN, fresh, FINISH)


def prepare(who, out_dirs):
    """The sprite's own pixels, cut to the figure, on a 9:16 flat grey canvas."""
    im = Image.open(sprite_file(who)).convert("RGBA")
    box = im.split()[-1].getbbox()
    fig = im.crop(box)
    h = int(round(fig.height / (1 - 2 * MARGIN)))
    w = int(round(h * 9 / 16.0))
    if fig.width > w * (1 - 2 * MARGIN):                 # a very wide figure: fit the width instead
        w = int(round(fig.width / (1 - 2 * MARGIN)))
        h = int(round(w * 16 / 9.0))
    canvas = Image.new("RGBA", (w, h), GREY + (255,))
    canvas.alpha_composite(fig, ((w - fig.width) // 2, (h - fig.height) // 2))
    for d in out_dirs:
        canvas.convert("RGB").save(os.path.join(d, in_name(who)))
    return (w, h), fig.size


def build(who_list):
    shell, nodes, links, ids, add, wire = kit()
    count = len(who_list) * len(LETTERS)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [0, -660], "size": [CELL_W * 2 - 40, 560],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## The character look test: %d characters, two redos each\n\n"
        "Run this in the **local ComfyUI**. Press **Run** once.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, about $%.2f a picture, charged to your "
        "Comfy account).\n\n"
        "**Rows** are characters: %s. The first box in each row is the character **as they are now**, on "
        "grey. If it shows an error, click **choose file to upload** and pick that character's "
        "`look_char_in_...png` from `JJK Game images/look_test`.\n\n"
        "**Columns** are the two redos, the same two for everyone:\n\n"
        "- **A, corrected:** the same pose and the same design, with what looks off put right.\n"
        "- **B, redrawn:** the same person in the same outfit, drawn afresh in a relaxed standing pose.\n\n"
        "In both, the hair, the eyes, the outfit and its colours should be the ones they have now.\n\n"
        "Nothing in the game changes from this test. You don't need to save anything: the results go to "
        "ComfyUI's output folder and Claude picks them up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (len(who_list), count, count * COST, COST, ", ".join("**%s**" % NAMES[w] for w in who_list))]})

    groups = []
    for r, who in enumerate(who_list):
        y = r * ROW_H
        src = add("LoadImage", (0, y), (CELL_W - 40, GEM_H + 20 + SAVE_H),
                  title="Load Image: %s as they are now" % NAMES[who])
        src["widgets_values"] = [in_name(who), "image"]
        for c, letter in enumerate(LETTERS):
            x = (c + 1) * CELL_W
            g = add("GeminiImage2Node", (x, y), (CELL_W - 40, GEM_H),
                    title="Nano Banana Pro: %s, %s %s" % (NAMES[who], letter, SHORT[letter]))
            w = g["widgets_values"]
            # A fixed seed for each box, numbered by the character's place in WHO
            # so that --who never changes anyone's seed. 9:16 is the nearest the
            # node has to the sprite canvas; 2K costs the same as 1K.
            seed = SEED + WHO.index(who) * len(LETTERS) + c
            w[0], w[2], w[3], w[4], w[5], w[6] = prompt_for(who, letter), seed, "fixed", ASPECT, RESOLUTION, "IMAGE"
            wire(src, 0, g, "images")
            s = add("SaveImage", (x, y + GEM_H + 60), (CELL_W - 40, SAVE_H),
                    title="%s: %s, %s" % (NAMES[who], letter, SHORT[letter]))
            s["widgets_values"] = [stem(who, letter)]
            wire(g, 0, s, "images")
        groups.append({"id": r + 1,
                       "title": "%s:  now  |  %s" % (NAMES[who].upper(), "  |  ".join(
                           "%s %s" % (l, SHORT[l]) for l in LETTERS)),
                       "bounding": [-20, y - 50, (len(LETTERS) + 1) * CELL_W, CELL_H + 70],
                       "color": "#3f4f5a", "font_size": 24, "flags": {}})
    wf = finish(shell, nodes, links, ids, groups)
    wf["extra"]["ds"] = {"scale": 0.4, "offset": [80, 700]}
    return wf


def make(who_list, out_dir=None):
    out_dir = out_dir or OUT
    for who in who_list:
        if not os.path.exists(sprite_file(who)):
            raise SystemExit("no sprite at %s" % sprite_file(who))
    os.makedirs(out_dir, exist_ok=True)
    dirs = [out_dir] + ([COMFY_INPUT] if out_dir == OUT and os.path.isdir(COMFY_INPUT) else [])
    for who in who_list:
        size, fig = prepare(who, dirs)
        print("%-8s %-22s %dx%d (figure %dx%d)   %s" % (who, in_name(who), size[0], size[1], fig[0], fig[1],
                                                       "  ".join(stem(who, l) for l in LETTERS)))
    out = os.path.join(out_dir, "look_chars.json")
    json.dump(build(who_list), open(out, "w"), indent=1)
    count = len(who_list) * len(LETTERS)
    print("%d pictures at %s %s, about $%.2f" % (count, ASPECT, RESOLUTION, count * COST))
    print("   workflow -> %s" % out)
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

    out_dir, who = opt("--out"), opt("--who")
    who_list = [w.lower() for w in who.split(",") if w] if who else list(WHO)
    for w in who_list:
        if w not in CHARS:
            raise SystemExit("no character %r: choose from %s" % (w, ",".join(WHO)))
    if len(set(who_list)) != len(who_list):
        raise SystemExit("a character is named twice")
    if "--list" in argv:
        for w in who_list:
            print("%s: %s\n" % (NAMES[w], CHARS[w][4]))
            for l in LETTERS:
                print("  %s  (%s)\n   %s\n" % (stem(w, l), SHORT[l], prompt_for(w, l)))
        print("%d pictures, about $%.2f a Run" % (len(who_list) * len(LETTERS),
                                                  len(who_list) * len(LETTERS) * COST))
        return
    if argv or not who_list:
        print(__doc__); raise SystemExit(1)
    make(who_list, out_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
