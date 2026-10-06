#!/bin/bash
# tools/test_keying.sh -- the tests of the cut-out's edge (docs/UI2_DESIGN.md
# D58 and 10.2 "U0k"; docs/ASSET_PIPELINE.md "The cut-out's edge").
#
#   tools/test_keying.sh            every test below but the last
#   tools/test_keying.sh --model    also run the anime-trained model once (step 8)
#
# No Ren'Py, no window, no pointer: it may run beside anything. Nothing under
# game/ is read except the four sprites the test pictures are made from, and
# nothing under game/ is written: every tool that installs a sprite is run
# from a scratch copy of tools/, so its "game" folder is in the scratch too.
# About two minutes; most of it is step 4, which is plain Python on a
# 1536x2752 render.
#
#   1  the sixteen exact pictures are built from the game's sprites
#      (tools/make_key_tests.py: flat pink and green, crisp and soft, the true
#      cut-out known)
#   2  both edges are scored on them. Taken four at a time (one backdrop, one
#      kind of outline) the new edge may leave no more than 800 visibly wrong
#      pixels on a crisp four and 9,000 on a soft four, and it must beat the
#      old on every four. Yuji's pink hair and red hood on pink must come
#      through whole.
#   3  the tests test: with a rule of the new edge broken on purpose (in
#      memory) the hood, then the hair, must be reported eaten
#   4  --edge old, and no option, give byte for byte what keysprite gave
#      before the option existed, on two kept renders (Maki on pink, Yuji on
#      green): the sprite and the side portrait, against sums recorded from
#      commit d2eb9db. The text of the old keying's functions is held to a
#      recorded sum too, so this still says something where the renders are
#      absent.
#   5  --edge new reaches tools/keyedge.py through keysprite and writes a
#      760x1400 sprite that is not the old one; composite_face.py hands the
#      option on
#   6  on the two real renders the new edge leaves no strongly tinted pixel
#      and no pocket of backdrop solid (keyedge.py --check)
#   7  cutcheck.py, where the model is absent, says so plainly and exits 0
#   8  (--model) cutcheck.py runs the model on Yuji's render and changes
#      neither the render nor the cut-out
#
# The two renders are outside the repository:
#   ~/Desktop/JJK Game images/maki_base_00001_.png
#   ~/Desktop/JJK Game images/redo_yuji/yuji_base.png
# A step that needs one says SKIP and why when it is absent; a skip is not a
# pass, and the last line then reads RESULT PASS (with skips).
#
# Environment: KEY_TESTS_DIR to keep the scratch (the pictures, the sprites)
# in a folder of yours; otherwise a temporary folder, removed at the end.
# KEY_TEST_MAKI and KEY_TEST_YUJI name the two renders if they are kept
# somewhere else (the recorded sums of step 4 are of these two pictures).
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools"
MAKI="${KEY_TEST_MAKI:-$HOME/Desktop/JJK Game images/maki_base_00001_.png}"
YUJI="${KEY_TEST_YUJI:-$HOME/Desktop/JJK Game images/redo_yuji/yuji_base.png}"
WITH_MODEL=0
[ "${1:-}" = "--model" ] && WITH_MODEL=1

if [ -n "${KEY_TESTS_DIR:-}" ]; then
    WORK="$KEY_TESTS_DIR"; mkdir -p "$WORK"; KEEP=1
else
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/key_tests.XXXXXX")"; KEEP=0
fi

# What keysprite wrote for the two renders at commit d2eb9db, before --edge.
SUM_MAKI_CHAR=cc11d62a9abcc2b9913e8c7a2c2a757b3026c6cf64a159d8c6b1300ea8ddb743
SUM_MAKI_SIDE=48a0ac1bf6086c0d3de74afcf85377508475055d0065aa87773dd17f638833a5
SUM_YUJI_CHAR=82fa05a34debe6908f8e37afc14d8c0855ec5631eaf038c53588b1a1eae100ba
SUM_YUJI_SIDE=b355370a5f707a3810dc1ab906b030b1ae242306eac174233427399a1285af56
# The text of the old keying (sample_bg, _hue_lean, screen_key, _dist,
# backdrop_regions, key_out, _grow) at that commit.
SUM_OLD_SOURCE=d77f9c7b204a7cec4b56ac68ae9c26012eb828c02b590ef612dbd7a758fb9355

PASSES=0; FAILS=0; SKIPS=0
pass() { PASSES=$((PASSES + 1)); echo "PASS  $1"; }
fail() { FAILS=$((FAILS + 1)); echo "FAIL  $1"; }
skip() { SKIPS=$((SKIPS + 1)); echo "SKIP  $1"; }
sum() { shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1; }
# a scratch project root holding a copy of the tools an install needs: what
# keysprite calls "the game" is then <scratch>/game
scratch_root() {
    mkdir -p "$WORK/$1/tools"
    cp "$TOOLS/keysprite.py" "$TOOLS/raster.py" "$TOOLS/pngread.py" "$TOOLS/keyedge.py" "$WORK/$1/tools/"
}

echo "== 1  the sixteen exact pictures"
if python3 "$TOOLS/make_key_tests.py" "$WORK/pics" --root "$ROOT" && [ "$(ls "$WORK/pics" | grep -c '^test_')" = 16 ]; then
    pass "sixteen pictures built from the game's sprites"
else
    fail "the test pictures could not be built"
fi

echo "== 2  both edges scored against the true cut-outs"
if python3 "$TOOLS/make_key_tests.py" --score "$WORK/pics"; then
    pass "the new edge is inside its bounds, beats the old on every four, and eats none of Yuji's own colours"
else
    fail "the score (see the FAIL lines above)"
fi

echo "== 3  the tests test"
if python3 "$TOOLS/make_key_tests.py" --prove "$WORK/pics"; then
    pass "a broken rule is noticed: the hood, then the hair, reported eaten"
else
    fail "a broken rule went unnoticed, or the edge as built fails"
fi

echo "== 4  --edge old, and no option, are byte for byte what the tool gave before"
GOT_SOURCE="$(python3 - "$TOOLS" <<'EOF'
import sys, inspect, hashlib
sys.path.insert(0, sys.argv[1])
import keysprite as k
names = ("sample_bg", "_hue_lean", "screen_key", "_dist", "backdrop_regions", "key_out", "_grow")
print(hashlib.sha256("".join(inspect.getsource(getattr(k, n)) for n in names).encode()).hexdigest())
EOF
)"
if [ "$GOT_SOURCE" = "$SUM_OLD_SOURCE" ]; then
    pass "the old keying's own functions are textually what they were at d2eb9db"
else
    fail "the text of the old keying (key_out and what it calls) has changed"
fi
scratch_root none; scratch_root old; scratch_root new
if [ -f "$MAKI" ] && [ -f "$YUJI" ]; then
    ( python3 "$WORK/none/tools/keysprite.py" "$MAKI" maki_neutral > "$WORK/none/maki.log" 2>&1 ) &
    ( python3 "$WORK/none/tools/keysprite.py" "$YUJI" yuji_neutral > "$WORK/none/yuji.log" 2>&1 ) &
    ( python3 "$WORK/old/tools/keysprite.py" --edge old "$MAKI" maki_neutral > "$WORK/old/maki.log" 2>&1 ) &
    ( python3 "$WORK/old/tools/keysprite.py" "$YUJI" yuji_neutral --edge=old > "$WORK/old/yuji.log" 2>&1 ) &
    wait
    for way in none old; do
        bad=""
        [ "$(sum "$WORK/$way/game/images/char/maki_neutral.png")" = "$SUM_MAKI_CHAR" ] || bad="$bad maki-sprite"
        [ "$(sum "$WORK/$way/game/images/side/maki_neutral.png")" = "$SUM_MAKI_SIDE" ] || bad="$bad maki-side"
        [ "$(sum "$WORK/$way/game/images/char/yuji_neutral.png")" = "$SUM_YUJI_CHAR" ] || bad="$bad yuji-sprite"
        [ "$(sum "$WORK/$way/game/images/side/yuji_neutral.png")" = "$SUM_YUJI_SIDE" ] || bad="$bad yuji-side"
        label="--edge old"; [ "$way" = none ] && label="no option"
        if [ -z "$bad" ]; then
            pass "$label: Maki's and Yuji's sprite and side portrait are byte for byte as at d2eb9db"
        else
            fail "$label: not what the tool gave before:$bad (logs in $WORK/$way)"
        fi
    done
else
    skip "the byte-for-byte test needs both kept renders and one is absent: $MAKI ; $YUJI"
fi

echo "== 5  --edge new reaches keyedge.py; composite_face.py hands the option on"
python3 - "$TOOLS" "$WORK" > "$WORK/step5.log" 2>&1 <<'EOF'
import sys, os
sys.path.insert(0, sys.argv[1])
import keysprite, composite_face
from raster import Img
p = keysprite.pop_edge
assert p(["a", "b"]) == ("old", ["a", "b"])
assert p(["--edge", "new", "a", "b"]) == ("new", ["a", "b"])
assert p(["a", "--edge=new", "b"]) == ("new", ["a", "b"])
assert p(["a", "b", "--edge", "old"]) == ("old", ["a", "b"])
assert p(["--batch", "f", "--edge", "new"]) == ("new", ["--batch", "f"])
for bad in (["--edge", "blue"], ["--edge"], ["--edge=newer"]):
    try:
        p(bad)
    except SystemExit:
        continue
    raise AssertionError("pop_edge took %r" % bad)
# composite_face.run hands its edge to keysprite's install: the slow parts
# (reading, lining up, compositing) are stood in for, the hand-over is real
seen = []
keysprite.install = lambda path, name, quiet=False, edge="old": seen.append((name, edge)) or []
composite_face.load = lambda path: Img(4, 4)
composite_face.read_crop = lambda *a: None
composite_face.align = lambda base, ed, mask: ((0.0, 1.0, 0, 0), 0.0, (2, 2))
composite_face.composite = lambda *a: (Img(4, 4), [0.0, 0.0, 0.0])
folder = os.path.join(sys.argv[2], "face")
os.makedirs(folder, exist_ok=True)
for edge in ("new", "old"):
    composite_face.run(os.path.join(folder, "base.png"), os.path.join(folder, "ed.png"), "yuji", "happy",
                       mask_path="m", edge=edge)
composite_face.run(os.path.join(folder, "base.png"), os.path.join(folder, "ed.png"), "yuji", "happy", mask_path="m")
assert seen == [("yuji_happy", "new"), ("yuji_happy", "old"), ("yuji_happy", "old")], seen
EOF
if [ $? = 0 ]; then
    pass "--edge is read in every form, a wrong value is refused, and composite_face hands it to the install"
else
    cat "$WORK/step5.log"
    fail "the --edge option (see the error above)"
fi
if [ -f "$MAKI" ]; then
    python3 "$WORK/new/tools/keysprite.py" --edge new "$MAKI" maki_neutral > "$WORK/new/maki.log" 2>&1
    NEW="$WORK/new/game/images/char/maki_neutral.png"
    SIZE="$(python3 -c "
import sys; sys.path.insert(0, '$TOOLS')
from pngread import load
im = load('$NEW'); print(im.w, im.h, im.ch)" 2>/dev/null)"
    if grep -q '^keyedge ' "$WORK/new/maki.log" && [ "$SIZE" = "760 1400 4" ] && [ "$(sum "$NEW")" != "$SUM_MAKI_CHAR" ]; then
        pass "keysprite --edge new cut Maki's render with keyedge.py: a 760x1400 sprite, not the old one"
    else
        fail "keysprite --edge new did not write a new-edge sprite (log: $WORK/new/maki.log)"
    fi
else
    skip "keysprite --edge new on a real render: Maki's render is absent ($MAKI)"
fi

echo "== 6  the two real renders: no strongly tinted pixel, no pocket left solid"
for pair in "Maki on pink|$MAKI" "Yuji on green|$YUJI"; do
    name="${pair%%|*}"; file="${pair#*|}"
    if [ -f "$file" ]; then
        if python3 "$TOOLS/keyedge.py" --check "$file"; then
            pass "$name"
        else
            fail "$name: the new edge left a strongly tinted pixel or a pocket solid"
        fi
    else
        skip "$name: the render is absent ($file)"
    fi
done

echo "== 7  cutcheck.py where the model is absent"
mkdir -p "$WORK/no_model"
OUT="$(CUTCHECK_MODEL_DIR="$WORK/no_model" python3 "$TOOLS/cutcheck.py" "$WORK/pics/test_crisp_grn_yuji.png" 2>&1)"; CODE=$?
echo "$OUT"
if [ $CODE = 0 ] && echo "$OUT" | grep -q '^cutcheck: skipped' && echo "$OUT" | grep -q 'not on this machine'; then
    pass "it says the model is not here and exits 0"
else
    fail "cutcheck.py without the model: exit $CODE"
fi

if [ $WITH_MODEL = 1 ]; then
    echo "== 8  cutcheck.py with the model"
    if [ -f "$YUJI" ]; then
        python3 "$TOOLS/keyedge.py" "$YUJI" "$WORK/yuji_cut.png" > /dev/null
        B1="$(sum "$YUJI")"; B2="$(sum "$WORK/yuji_cut.png")"
        OUT="$(python3 "$TOOLS/cutcheck.py" "$YUJI" "$WORK/yuji_cut.png" 2>&1)"; CODE=$?
        echo "$OUT"
        if echo "$OUT" | grep -q '^cutcheck: skipped'; then
            skip "the model is not on this machine"
        elif [ $CODE = 0 ] && echo "$OUT" | grep -q 'a piece cut off' && [ "$(sum "$YUJI")" = "$B1" ] && [ "$(sum "$WORK/yuji_cut.png")" = "$B2" ]; then
            pass "the model ran, reported, and changed neither the render nor the cut-out"
        else
            fail "cutcheck.py with the model: exit $CODE"
        fi
    else
        skip "cutcheck.py with the model: Yuji's render is absent ($YUJI)"
    fi
fi

[ $KEEP = 0 ] && rm -rf "$WORK"
echo
echo "$PASSES passed, $FAILS failed, $SKIPS skipped"
if [ $FAILS -gt 0 ]; then echo "RESULT FAIL"; exit 1; fi
if [ $SKIPS -gt 0 ]; then echo "RESULT PASS (with skips)"; exit 0; fi
echo "RESULT PASS"
