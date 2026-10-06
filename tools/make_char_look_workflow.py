"""
Build the ComfyUI workflow that tries two redos of the characters that feel off.

    python3 tools/make_char_look_workflow.py
    python3 tools/make_char_look_workflow.py --who yuji,maki
    python3 tools/make_char_look_workflow.py --list      # every prompt, and what a Run costs
    python3 tools/make_char_look_workflow.py --set 2     # the second round (below)
    python3 tools/make_char_look_workflow.py --set 3     # the picks on a flat colour, for cutting out

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

The second round (`--set 2`, 7 Oct): the first round put Yuji right in both
columns and left Nobara as she was, but missed twice. Maki's jacket and skirt
came back drawn as tight as before in A and in B, and Shoko's A lost her tired
half-closed eyes (the prompt asked for "larger" eyes) while her B kept the
long half-real face. Each box of the second round takes one first-round
RESULT and asks for one change only, which is what the editor follows best:

    Maki C    B's pose, the uniform drawn hanging loose
    Maki D    A's pose, the same change
    Shoko C   A's clean face, the eyes made tired again
    Shoko D   B's tired face, drawn as simply as the rest of her

It writes `look_chars_2.json` and `look_chars_2.md`, copies the four
first-round pictures it starts from as `look_char2_in_<who>_<A|B>.png`, and
its results land as `look_char2_<who>_<C|D>_0000N_.png`. Four boxes at 2K:
about $0.64 a Run.

The picks on a flat colour (`--set 3`, 7 Oct): the second round's two changes
both worked. Claude's picks are Maki C and Shoko C, with Nobara kept as she
is, and for Yuji the redraw B. Then the owner asked: "Should we not put yuji
in his school uniform like megumi with his red collar?" Today's sprite has
him in an open jacket over a red hoodie, so both redos do too. This set
dresses B in the school uniform: the editor is given B and, as a guide to the
cloth and the cut, the unchanged sprite of Megumi, and is asked for one
change, the clothes, with a red hood sewn to the collar. Two tries: E keeps
his white trainers, F gives him red ones.

A sprite cannot be cut cleanly off grey: on test pictures whose true outline
is known, the cut from a grey backdrop left about twelve times as many wrong
edge pixels as the cut from a flat saturated colour (grey lies on the line
between the backdrop and the dark uniforms, so shading reads as
transparency). So every pick is drawn once more with only the background
changed, to a colour the character does not wear: green for Yuji and Shoko,
magenta pink for Maki (her hair is green). Yuji's two tries are each chained
straight into that step. Two small corrections ride along: Maki's eyes
drifted from amber to red-brown, and the shadows under Shoko's eyes came out
heavy. It writes `look_chars_final.json` and `look_chars_final.md`; results
land as `look_char_yuji_<E|F>_0000N_.png` (the uniform on grey),
`look_char_final_yuji_<E|F>_0000N_.png` and `look_char_final_<who>_0000N_.png`.
Six boxes at 2K: about $0.96 a Run. Nothing is installed by it.

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


# ---------------------------------------------------------------- the second round
COMFY_OUTPUT = os.path.expanduser("~/ComfyUI-Shared/output")
SEED2 = 2921

HEAD2 = ("This is a full-body standing character sprite for a visual novel, in cel-shaded anime style, on a "
         "plain grey background. Redraw this exact picture and change one thing only, described below. "
         "Everything else stays exactly as it is: the same person at the same age, the same pose, the same "
         "hair, the same clothes and colours, the same outlines and shading style, the same size and place "
         "in the frame. The character stays fully and ordinarily dressed: do not remove, shorten, open or "
         "add any piece of clothing. Background: one flat, even mid-grey, with no floor, no cast shadow, no "
         "gradient and no text. Output a 9:16 picture.")

MAKI_CLOTH = ("THE ONE CHANGE: how the cloth of the school uniform is drawn. At present the jacket and the "
              "skirt are drawn tight against the body. Draw them as a sturdy, boxy school uniform of thick "
              "cloth that hangs loose and straight, the way a blazer does. The jacket falls straight down "
              "from the shoulders to its hem and does not follow the shape of the body underneath: its "
              "front is one plain, nearly flat surface with the same simple two-tone shading as the "
              "sleeves, with no curved shadow shapes on the chest and no creases pulling across it. The "
              "skirt is a plain straight uniform skirt of the same length as now, hanging straight from "
              "the waist to its hem, with a flat plain front: no dark V-shaped shadow on it. The face, the "
              "glasses, the hair, the arms and hands, the legs, the socks and the shoes stay exactly as "
              "they are.")
MAKI_SPECK = (" One shoe has a small stray bright green speck on it: paint over it in the shoe's own "
              "brown.")                       # B carried it over from today's sprite; A did not
SHOKO_EYES = ("THE ONE CHANGE: the eyes. She is a tired, unhurried adult doctor who has not slept enough. "
              "Redraw the eyes smaller and half-closed: heavy upper eyelids resting low over the irises, so "
              "that only the lower half of each iris shows; the brows relaxed and level; one flat "
              "grey-brown shadow under each eye. Calm and a little bored, not sad and not surprised. Keep "
              "the small mole under the eye, on the same side as now. The shape of the face, the nose and "
              "the mouth stay exactly as they are.")
SHOKO_FACE = ("THE ONE CHANGE: the drawing of the face, which is in a more realistic style than the rest of "
              "the picture. Redraw the face as a simple anime face in the same clean style as the body: a "
              "slightly shorter face with a softer jaw, a small simple nose drawn with one short line, a "
              "simple mouth line with no drawn lips, clean simple eyes. Keep what makes her herself: the "
              "eyes stay half-closed and tired under heavy upper eyelids, with one flat grey-brown shadow "
              "under each eye in place of the many fine lines there now, and the small mole stays under the "
              "eye on the same side as now. She stays an adult woman of the same age.")

# who, this box's letter, the first-round result it starts from, the label, the one change
SET2 = [
    ("maki", "C", "B", "B's pose, uniform hanging loose", MAKI_CLOTH + MAKI_SPECK),
    ("maki", "D", "A", "A's pose, uniform hanging loose", MAKI_CLOTH),
    ("shoko", "C", "A", "A's clean face, tired eyes", SHOKO_EYES),
    ("shoko", "D", "B", "B's tired face, drawn simpler", SHOKO_FACE),
]


def stem2(who, letter):
    return "look_char2_%s_%s" % (who, letter)


def in_name2(who, src):
    return "look_char2_in_%s_%s.png" % (who, src)


def first_round(who, src):
    return os.path.join(COMFY_OUTPUT, "%s_00001_.png" % stem(who, src))


def build2():
    shell, nodes, links, ids, add, wire = kit()
    count = len(SET2)
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [0, -560], "size": [CELL_W * 2 - 40, 460],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## The character look test, second round: Maki and Shoko\n\n"
        "Run this in the **local ComfyUI**. Press **Run** once.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, about $%.2f a picture, charged to your "
        "Comfy account).\n\n"
        "Each pair of boxes is one try: on the left a picture **from the first round**, on the right the "
        "same picture with **one thing changed**. If a left box shows an error, click **choose file to "
        "upload** and pick its `look_char2_in_...png` from `JJK Game images/look_test`.\n\n"
        "- **Maki C and D:** the uniform drawn hanging loose, like a school uniform. C keeps B's pose "
        "(hand on hip), D keeps A's.\n"
        "- **Shoko C:** A's clean face with her tired, half-closed eyes back.\n"
        "- **Shoko D:** B's tired face, drawn as simply as the rest of her.\n\n"
        "Nothing in the game changes from this test. The results go to ComfyUI's output folder and Claude "
        "picks them up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (count, count * COST, COST)]})
    groups = []
    rows = []
    for box in SET2:
        if box[0] not in rows: rows.append(box[0])
    for i, (who, letter, src, label, change) in enumerate(SET2):
        r = rows.index(who)
        c = sum(1 for b in SET2[:i] if b[0] == who)
        x, y = c * 2 * CELL_W, r * ROW_H
        load = add("LoadImage", (x, y), (CELL_W - 40, GEM_H + 20 + SAVE_H),
                   title="Load Image: %s, %s from the first round" % (NAMES[who], src))
        load["widgets_values"] = [in_name2(who, src), "image"]
        g = add("GeminiImage2Node", (x + CELL_W, y), (CELL_W - 40, GEM_H),
                title="Nano Banana Pro: %s %s, %s" % (NAMES[who], letter, label))
        w = g["widgets_values"]
        w[0], w[2], w[3], w[4], w[5], w[6] = "%s %s" % (HEAD2, change), SEED2 + i, "fixed", ASPECT, RESOLUTION, "IMAGE"
        wire(load, 0, g, "images")
        s = add("SaveImage", (x + CELL_W, y + GEM_H + 60), (CELL_W - 40, SAVE_H),
                title="%s %s: %s" % (NAMES[who], letter, label))
        s["widgets_values"] = [stem2(who, letter)]
        wire(g, 0, s, "images")
    for r, who in enumerate(rows):
        mine = [b for b in SET2 if b[0] == who]
        groups.append({"id": r + 1,
                       "title": "%s:  %s" % (NAMES[who].upper(), "   |   ".join(
                           "%s from the first round  >  %s, %s" % (b[2], b[1], b[3]) for b in mine)),
                       "bounding": [-20, r * ROW_H - 50, len(mine) * 2 * CELL_W, CELL_H + 70],
                       "color": "#3f4f5a", "font_size": 24, "flags": {}})
    wf = finish(shell, nodes, links, ids, groups)
    wf["extra"]["ds"] = {"scale": 0.4, "offset": [80, 600]}
    return wf


NOTES2 = """# The character look test, second round: Maki and Shoko

One workflow file is in this folder: `look_chars_2.json`. Drag it into the
**local ComfyUI** (Comfy Desktop) and press **Run**, like the first round.

Only run this if you agree with Claude's read of the first round:

- **Maki:** in A and in B the jacket and skirt are still drawn tight against
  her, where Nobara's uniform hangs like cloth.
- **Shoko:** A has a clean face in the others' style but lost her tired,
  half-closed eyes, so she reads as someone younger. B kept her tired eyes but
  also the long, half-real face.

If something else is what feels off about either of them, say so instead and
Claude will aim a round at that.

**Nothing in the game changes from this test.**

**Total: %d pictures, about $%.2f** (Nano Banana Pro, about $%.2f a picture).

## Steps

1. Open Comfy Desktop.
2. Drag `look_chars_2.json` from this folder onto the ComfyUI window.
3. Each left-hand box should show a picture from the first round. If one shows
   an error, click **choose file to upload** in that box and pick its
   `look_char2_in_...png` from this folder.
4. Press **Run** once. Four pictures, about $%.2f.
5. Wait until all four show a picture, then tell Claude.

## The four tries

Each one takes a first-round picture and changes one thing.

- **Maki C:** B (hand on hip), with the uniform drawn hanging loose.
- **Maki D:** A (standing), with the same change.
- **Shoko C:** A's clean face, with her tired, half-closed eyes back.
- **Shoko D:** B's tired face, drawn as simply as the rest of her.
"""


def make2(out_dir=None):
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    dirs = [out_dir] + ([COMFY_INPUT] if out_dir == OUT and os.path.isdir(COMFY_INPUT) else [])
    for who, letter, src, label, _ in SET2:
        if not os.path.exists(first_round(who, src)):
            raise SystemExit("no first-round picture at %s" % first_round(who, src))
    for who, src in sorted({(b[0], b[2]) for b in SET2}):
        for d in dirs:
            shutil.copyfile(first_round(who, src), os.path.join(d, in_name2(who, src)))
    for who, letter, src, label, _ in SET2:
        print("%-6s %s  from %-28s -> %s   (%s)" % (who, letter, in_name2(who, src), stem2(who, letter), label))
    out = os.path.join(out_dir, "look_chars_2.json")
    json.dump(build2(), open(out, "w"), indent=1)
    cost = len(SET2) * COST
    open(os.path.join(out_dir, "look_chars_2.md"), "w").write(NOTES2 % (len(SET2), cost, COST, cost))
    print("%d pictures at %s %s, about $%.2f" % (len(SET2), ASPECT, RESOLUTION, cost))
    print("   workflow -> %s" % out)
    return out


# ---------------------------------------------------------------- the picks, on a flat colour
SEED3 = 2931

HEAD3 = ("This is a full-body standing character sprite for a visual novel, in cel-shaded anime style, on a "
         "plain grey background. Redraw this exact picture. The figure stays exactly as it is, line for "
         "line: the same person at the same age, the same pose, the same face and expression, the same "
         "hair, the same clothes and colours, the same outlines and shading, at the same size and in the "
         "same place in the frame, the whole figure from the top of the hair to the soles of the shoes. "
         "The character stays fully and ordinarily dressed: do not remove, shorten, open or add any piece "
         "of clothing.")
BACKDROP3 = ("THE BACKGROUND: replace the grey with one flat, even, fully saturated %s, the same colour from "
             "corner to corner like a studio chroma-key screen: no floor, no cast shadow under the feet, no "
             "gradient, no vignette, no texture and no text. That colour must not tint the figure: the "
             "figure's outlines stay dark and its colours stay as they are right up to its edge.")
GREEN3 = "pure green (about RGB 0, 200, 60)"
PINK3 = "magenta pink (about RGB 220, 40, 160)"

# Yuji's school uniform. The owner, 7 Oct: "Should we not put yuji in his school uniform like megumi
# with his red collar?" Today's sprite, and so both redos of it, has him in an open jacket over a red
# hoodie. Two pictures go to the editor: his redraw (B), and the unchanged sprite of the student whose
# uniform it is, as a guide to the cloth and the cut. The red hood sewn to the collar is his own.
UNIFORM_GUIDE = "megumi"
YUJI_FROM = (1, "B")
YUJI_UNIFORM = (
    "Two pictures are given. The FIRST is the character to redraw: a full-body standing character sprite "
    "for a visual novel, in cel-shaded anime style, on a plain grey background. The SECOND shows another "
    "student and is a guide to one thing only, the school uniform. Redraw the FIRST picture and change one "
    "thing only: his clothes. Everything else stays exactly as in the first picture: the same person at "
    "the same age, the same head, face and expression, the same hair, the same pose with one hand in his "
    "trouser pocket, the same hands, the same size and place in the frame, the same outlines and shading "
    "style, the same flat grey background. Copy nothing else from the second picture: not that student's "
    "face, hair, pose, trousers or boots. "
    "THE ONE CHANGE: he wears the school's uniform in place of the open jacket and the red hoodie. The "
    "jacket is the one in the second picture: the same dark navy cloth with the same lighter streaks along "
    "the folds, a high stand-up collar, a closed front and one gold button with a swirl on it. It is a "
    "short jacket that ends at his waist. Sewn to its collar is a bright red hood, which is his alone: the "
    "hood is down, lying behind his neck and across the back of his shoulders, and its red cloth shows all "
    "the way round the collar at the front. Below the jacket, straight full-length trousers of the same "
    "dark navy cloth. There is no hoodie under the jacket: no drawstrings, no red hem below the jacket and "
    "no red cuffs at the wrists. %s "
    "The character stays fully and ordinarily dressed. Output a 9:16 picture showing the whole figure from "
    "the top of the hair to the soles of the shoes.")
YUJI_TRIES = [   # letter, the shoes, the label
    ("E", "His white lace-up trainers stay exactly as they are.", "school uniform, red hood, white trainers"),
    ("F", "His trainers become red, with white soles and white laces, in the same shape as now.",
     "school uniform, red hood, red trainers"),
]

# who, the picture it starts from (round, letter), the backdrop, a correction or None, the label
SET3 = [
    ("maki", 2, "C", PINK3,
     "ONE CORRECTION: the irises of the eyes are amber, a warm golden brown, and not red-brown. Nothing "
     "else about the face changes.", "C on magenta pink, amber eyes"),
    ("shoko", 2, "C", GREEN3,
     "ONE CORRECTION: the shadows under the eyes are a little too heavy. Keep them, but make each one "
     "smaller and paler, a soft pale grey-brown that reads as tiredness. Nothing else about the face "
     "changes.", "C on green, lighter shadows under the eyes"),
]


def source3(who, rnd, letter):
    return os.path.join(COMFY_OUTPUT, "%s_00001_.png" % (stem(who, letter) if rnd == 1 else stem2(who, letter)))


def in_name3(who):
    return "look_char3_in_%s.png" % who


def guide_name3():
    return "look_char3_guide_%s.png" % UNIFORM_GUIDE


def stem3(who, letter=None):
    return "look_char_final_%s" % who + ("_%s" % letter if letter else "")


def prompt3(colour, fix):
    return " ".join(x for x in (HEAD3, BACKDROP3 % colour, fix, "Output a 9:16 picture.") if x)


def count3():
    return 2 * len(YUJI_TRIES) + len(SET3)


def build3():
    shell, nodes, links, ids, add, wire = kit()
    count = count3()
    ids["n"] += 1
    nodes.append({"id": ids["n"], "type": "MarkdownNote", "pos": [0, -600], "size": [CELL_W * 2 - 40, 500],
                  "flags": {}, "order": 0, "mode": 0, "inputs": [], "outputs": [], "properties": {},
                  "title": "Start here", "color": "#222", "bgcolor": "#000", "widgets_values": [
        "## Yuji in his school uniform, and the picks on a flat colour\n\n"
        "Run this in the **local ComfyUI**. Press **Run** once.\n\n"
        "**Cost:** %d pictures, about **$%.2f** (Nano Banana Pro, about $%.2f a picture, charged to your "
        "Comfy account).\n\n"
        "- **Yuji** (the top block): his redraw is dressed in the school uniform, like Megumi's, with a red "
        "hood sewn to the collar. Two tries: **E** keeps his white trainers, **F** gives him red ones. Each "
        "is then drawn once more on flat green.\n"
        "- **Maki** and **Shoko:** the picked picture drawn once more on flat pink or green.\n\n"
        "The green and pink are only there so the figures can be cut out cleanly; they never show in the "
        "game. If a left-hand box shows an error, click **choose file to upload** and pick its "
        "`look_char3_...png` from `JJK Game images/look_test`.\n\n"
        "Nothing in the game changes from this. The results go to ComfyUI's output folder and Claude picks "
        "them up from there.\n\n"
        "If it stops with a rate-limit or \"high demand\" error, wait a minute and press **Run** again: a "
        "finished picture is reused, not paid for twice (as long as ComfyUI hasn't been restarted)."
        % (count, count * COST, COST)]})
    groups = []
    # Yuji: his redraw and the guide go in together; each try is then put on green
    who = "yuji"
    load = add("LoadImage", (0, 0), (CELL_W - 40, 760), title="Load Image: Yuji %s, as picked" % YUJI_FROM[1])
    load["widgets_values"] = [in_name3(who), "image"]
    guide = add("LoadImage", (0, 800), (CELL_W - 40, 760),
                title="Load Image: %s, for the uniform" % UNIFORM_GUIDE.capitalize())
    guide["widgets_values"] = [guide_name3(), "image"]
    both = add("BatchImagesNode", (0, 1600), (CELL_W - 40, 120), title="Both pictures: Yuji first")
    wire(load, 0, both, "images.image0")
    wire(guide, 0, both, "images.image1")
    for k, (letter, shoes, label) in enumerate(YUJI_TRIES):
        y = k * ROW_H
        g = add("GeminiImage2Node", (CELL_W, y), (CELL_W - 40, GEM_H),
                title="Nano Banana Pro: Yuji %s, %s" % (letter, label))
        w = g["widgets_values"]
        w[0], w[2], w[3], w[4], w[5], w[6] = YUJI_UNIFORM % shoes, 2941 + 2 * k, "fixed", ASPECT, RESOLUTION, "IMAGE"
        wire(both, 0, g, "images")
        sv = add("SaveImage", (CELL_W, y + GEM_H + 60), (CELL_W - 40, SAVE_H), title="Yuji %s: %s" % (letter, label))
        sv["widgets_values"] = [stem(who, letter)]
        wire(g, 0, sv, "images")
        g2 = add("GeminiImage2Node", (2 * CELL_W, y), (CELL_W - 40, GEM_H),
                 title="Nano Banana Pro: Yuji %s on green" % letter)
        w = g2["widgets_values"]
        w[0], w[2], w[3], w[4], w[5], w[6] = prompt3(GREEN3, None), 2942 + 2 * k, "fixed", ASPECT, RESOLUTION, "IMAGE"
        wire(g, 0, g2, "images")
        sv2 = add("SaveImage", (2 * CELL_W, y + GEM_H + 60), (CELL_W - 40, SAVE_H), title="Yuji %s on green" % letter)
        sv2["widgets_values"] = [stem3(who, letter)]
        wire(g2, 0, sv2, "images")
    groups.append({"id": 1, "title": "YUJI:  %s as picked + the uniform  >  %s  >  each on green" % (
                       YUJI_FROM[1], "  |  ".join("%s %s" % (t[0], t[2]) for t in YUJI_TRIES)),
                   "bounding": [-20, -50, 3 * CELL_W, len(YUJI_TRIES) * ROW_H - 50],
                   "color": "#3f4f5a", "font_size": 24, "flags": {}})
    for i, (who, rnd, letter, colour, fix, label) in enumerate(SET3):
        y = (len(YUJI_TRIES) + i) * ROW_H
        load = add("LoadImage", (0, y), (CELL_W - 40, GEM_H + 20 + SAVE_H),
                   title="Load Image: %s %s, as picked" % (NAMES[who], letter))
        load["widgets_values"] = [in_name3(who), "image"]
        g = add("GeminiImage2Node", (CELL_W, y), (CELL_W - 40, GEM_H),
                title="Nano Banana Pro: %s, %s" % (NAMES[who], label))
        w = g["widgets_values"]
        w[0], w[2], w[3], w[4], w[5], w[6] = prompt3(colour, fix), SEED3 + 1 + i, "fixed", ASPECT, RESOLUTION, "IMAGE"
        wire(load, 0, g, "images")
        sv = add("SaveImage", (CELL_W, y + GEM_H + 60), (CELL_W - 40, SAVE_H), title="%s: %s" % (NAMES[who], label))
        sv["widgets_values"] = [stem3(who)]
        wire(g, 0, sv, "images")
        groups.append({"id": i + 2, "title": "%s:  %s as picked  >  %s" % (NAMES[who].upper(), letter, label),
                       "bounding": [-20, y - 50, 2 * CELL_W, CELL_H + 70],
                       "color": "#3f4f5a", "font_size": 24, "flags": {}})
    wf = finish(shell, nodes, links, ids, groups)
    wf["extra"]["ds"] = {"scale": 0.3, "offset": [80, 700]}
    return wf


NOTES3 = """# Yuji in his school uniform, and the picks on a flat colour

One workflow file is in this folder: `look_chars_final.json`. Drag it into the
**local ComfyUI** (Comfy Desktop) and press **Run**.

## What it makes

- **Yuji in his school uniform.** You asked: "Should we not put yuji in his
  school uniform like megumi with his red collar?" Yes. His redraw (B, hand in
  his pocket) is dressed in the same uniform as Megumi's, with a red hood sewn
  to the collar. Two tries: **E** keeps his white trainers, **F** gives him
  red ones. Each is then drawn once more on flat green.
- **Maki C** and **Shoko C**, each drawn once more with only the background
  changed, to flat pink (Maki) and flat green (Shoko). Two small corrections
  ride along: Maki's eyes back to amber (they drifted to red-brown), and the
  shadows under Shoko's eyes a little lighter.

The green and pink are there so the figures can be cut out cleanly. They
never show in the game.

If you would rather have Maki D, Shoko D, or something else for either of
them, say so instead of running this and Claude will rebuild the file.
Nobara is kept as she is: nothing is made for her.

**Nothing in the game changes from this.**

**Total: %d pictures, about $%.2f** (Nano Banana Pro, about $%.2f a picture).

## Steps

1. Open Comfy Desktop.
2. Drag `look_chars_final.json` from this folder onto the ComfyUI window.
3. The left-hand boxes should show Yuji, Megumi, Maki and Shoko. If one shows
   an error, click **choose file to upload** in that box and pick its
   `look_char3_...png` from this folder.
4. Press **Run** once. Six pictures, about $%.2f.
5. Wait until all six show a picture, then tell Claude.
"""


def make3(out_dir=None):
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    dirs = [out_dir] + ([COMFY_INPUT] if out_dir == OUT and os.path.isdir(COMFY_INPUT) else [])
    picks = [("yuji",) + YUJI_FROM] + [(b[0], b[1], b[2]) for b in SET3]
    for who, rnd, letter in picks:
        if not os.path.exists(source3(who, rnd, letter)):
            raise SystemExit("no picked picture at %s" % source3(who, rnd, letter))
    for who, rnd, letter in picks:
        for d in dirs:
            shutil.copyfile(source3(who, rnd, letter), os.path.join(d, in_name3(who)))
    # the guide: the unchanged sprite on grey, at the size of the picture it travels with
    size = Image.open(source3("yuji", *YUJI_FROM)).size
    tmp = out_dir
    prepare(UNIFORM_GUIDE, [tmp])
    ref = Image.open(os.path.join(tmp, in_name(UNIFORM_GUIDE))).convert("RGB").resize(size, Image.LANCZOS)
    os.remove(os.path.join(tmp, in_name(UNIFORM_GUIDE)))
    for d in dirs:
        ref.save(os.path.join(d, guide_name3()))
    for letter, shoes, label in YUJI_TRIES:
        print("yuji   %s  from %s + %s -> %s, then %s   (%s)" % (
            letter, in_name3("yuji"), guide_name3(), stem("yuji", letter), stem3("yuji", letter), label))
    for who, rnd, letter, colour, fix, label in SET3:
        print("%-6s from %-24s -> %s   (%s)" % (who, in_name3(who), stem3(who), label))
    out = os.path.join(out_dir, "look_chars_final.json")
    json.dump(build3(), open(out, "w"), indent=1)
    cost = count3() * COST
    open(os.path.join(out_dir, "look_chars_final.md"), "w").write(NOTES3 % (count3(), cost, COST, cost))
    print("%d pictures at %s %s, about $%.2f" % (count3(), ASPECT, RESOLUTION, cost))
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

    out_dir, who, which = opt("--out"), opt("--who"), opt("--set")
    if which == "2":
        if "--list" in argv:
            for who2, letter, src, label, change in SET2:
                print("%s  (%s %s: %s; from the first round's %s)\n   %s %s\n" % (
                    stem2(who2, letter), NAMES[who2], letter, label, src, HEAD2, change))
            print("%d pictures, about $%.2f a Run" % (len(SET2), len(SET2) * COST))
            return
        if argv or who:
            print(__doc__); raise SystemExit(1)
        make2(out_dir)
        return
    if which == "3":
        if "--list" in argv:
            for letter, shoes, label in YUJI_TRIES:
                print("%s  (Yuji %s: %s; from round %d's %s and %s's sprite)\n   %s\n" % (
                    stem("yuji", letter), letter, label, YUJI_FROM[0], YUJI_FROM[1], UNIFORM_GUIDE,
                    YUJI_UNIFORM % shoes))
                print("%s  (Yuji %s on green)\n   %s\n" % (stem3("yuji", letter), letter, prompt3(GREEN3, None)))
            for who3, rnd, letter, colour, fix, label in SET3:
                print("%s  (%s: %s; from round %d's %s)\n   %s\n" % (
                    stem3(who3), NAMES[who3], label, rnd, letter, prompt3(colour, fix)))
            print("%d pictures, about $%.2f a Run" % (count3(), count3() * COST))
            return
        if argv or who:
            print(__doc__); raise SystemExit(1)
        make3(out_dir)
        return
    if which not in (None, "1"):
        raise SystemExit("--set is 1, 2 or 3")
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
