#!/bin/bash
# tools/review_pack.sh -- everything a reviewer of one package of the second UI
# overhaul looks at, made again from the repository (docs/UI2_DESIGN.md K13:
# "nothing lives only in a scratch folder"; 10.2, U0a step 9).
#
#   tools/review_pack.sh <package>          U0a U0b U0c1 U0c2 U0d U1 ... U10, L
#   tools/review_pack.sh <package> --list   say what it would run, run nothing
#   tools/review_pack.sh <package> --no-harness   the sheets only
#
# It writes shots/review/<package>/ (shots/ is ignored by git):
#   <harness>/        each harness of the package's row in the plan's 10.1: its
#                     result.txt and every screenshot it takes
#   layout/           a layout sheet for every game/layout/hot_*, view_* and
#                     area_* file the package's places have (tools/layout_sheet.py)
#   stage/            stage sheets, once tools/stage_preview.py exists (U0d3)
#   content.txt       tools/check_content.py --all, and --later-notes
#   INDEX.txt         what was made, each harness's last line, what was skipped
#
# The harnesses run one after another through tools/smoke.sh, which takes the
# pointer lock for the ones that need it, so this can be started from any
# worktree at any time. A harness that does not exist yet (a later package's)
# is listed as "not written yet", not failed. Exit status 0 when every harness
# that ran ended RESULT PASS; 1 when one failed; 3 when none failed but one was
# REFUSED (a game was open, or the wait for the pointer ran out): run it again.
# u2_dump's file goes to <pack>/u2_dump/game_layout.json, never to the
# committed tools/art/game_layout.json.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="${1:-}"
[ -n "$PKG" ] || { echo "usage: tools/review_pack.sh <package> [--list] [--no-harness]" >&2; exit 2; }
shift
LIST=0; NOH=0
for a in "$@"; do
    case "$a" in
        --list) LIST=1 ;;
        --no-harness) NOH=1 ;;
        *) echo "review_pack.sh: unknown argument $a" >&2; exit 2 ;;
    esac
done

# The standing set of every package (the plan's standard acceptance (c), (d)).
STANDING="u2_contracts p2_contracts core_flow phase1_all phase2_all"
# package -> its own harnesses (the plan's 10.1), then the places whose layout
# sheets it is judged on ("all" for every file under game/layout/).
case "$PKG" in
    U0a)  OWN="u2_dump u2_baseline p2_paths p2_view p2_map p2_hud p2_rooms wp1_world"; SHEETS="" ;;
    U0b)  OWN="u2_home wp1_world p2_map p2_paths p2_saves p2_night wp4_board"; SHEETS="dorm dorm_yard boys_dorm dorms" ;;
    U0c1) OWN="u2_home wp1_world p2_map p2_paths p2_saves p2_night"; SHEETS="all" ;;
    U0c2|U0c) OWN="u2_home u2_baseline p2_view p2_rooms p2_hud p2_night"; SHEETS="all" ;;
    U0d|U0d1|U0d2|U0d3|U0k) OWN="u2_dump"; SHEETS="all" ;;
    U1)   OWN="wp1_world u2_world"; SHEETS="" ;;
    U2)   OWN="p2_map p2_paths u2_map"; SHEETS="all" ;;
    U3)   OWN="p2_view u2_blend"; SHEETS="all" ;;
    U4)   OWN="p2_rooms p2_hud wp7_ui u2_things"; SHEETS="all" ;;
    U5)   OWN="p2_cards u2_rooms"; SHEETS="bathhouse sauna pool dorm_common" ;;
    U6)   OWN="wp8_journal u2_screens"; SHEETS="" ;;
    U7)   OWN="wp9_prologue u2_offcampus"; SHEETS="" ;;
    U8)   OWN="u2_older p2_gear wp4_board p2_cards p2_night"; SHEETS="" ;;
    U9)   OWN="u2_names wp10_chapters wp9_prologue wp5_memories p2_saves p2_night"; SHEETS="" ;;
    U10)  OWN="ui2_all u2_saves"; SHEETS="all" ;;
    L)    OWN="u2_dump p2_map p2_hud p2_paths p2_view p2_rooms"; SHEETS="all" ;;
    *) echo "review_pack.sh: no package $PKG (U0a U0b U0c1 U0c2 U0d U1 to U10, L)" >&2; exit 2 ;;
esac

OUT="$ROOT/shots/review/$PKG"
HARNESSES=""
for h in $OWN $STANDING; do
    case " $HARNESSES " in *" $h "*) ;; *) HARNESSES="$HARNESSES $h" ;; esac
done

# The layout files the package's sheets are drawn from.
STEMS=""
if [ -n "$SHEETS" ]; then
    for f in "$ROOT"/game/layout/hot_*.json "$ROOT"/game/layout/view_*.json "$ROOT"/game/layout/area_*.json; do
        [ -f "$f" ] || continue
        stem="$(basename "$f" .json)"
        key="${stem#*_}"
        if [ "$SHEETS" = "all" ]; then
            STEMS="$STEMS $stem"
        else
            case " $SHEETS " in *" $key "*) STEMS="$STEMS $stem" ;; esac
        fi
    done
fi

if [ "$LIST" = "1" ]; then
    echo "package $PKG -> $OUT"
    for h in $HARNESSES; do
        if [ -f "$ROOT/tools/smoke/$h.rpy" ]; then echo "  harness $h"; else echo "  harness $h (not written yet)"; fi
    done
    for s in $STEMS; do echo "  layout sheet $s"; done
    [ -f "$ROOT/tools/stage_preview.py" ] && echo "  stage sheets (tools/stage_preview.py)" || echo "  stage sheets: tools/stage_preview.py is not written yet (U0d3)"
    echo "  content checks"
    exit 0
fi

mkdir -p "$OUT" || exit 2
INDEX="$OUT/INDEX.txt"
HEAD="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo '?')"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
DIRTY="$( [ -n "$(git -C "$ROOT" status --porcelain 2>/dev/null)" ] && echo ' + uncommitted changes')"
{
    echo "Review pack · $PKG · $(date '+%Y-%m-%d %H:%M') · $BRANCH @ $HEAD$DIRTY"
    echo
} > "$INDEX"

FAILED=0
REFUSED=0
export RENPY_DISABLE_BACKUPS="I take responsibility for this."
if [ "$NOH" = "0" ]; then
    echo "Harnesses" >> "$INDEX"
    for h in $HARNESSES; do
        if [ ! -f "$ROOT/tools/smoke/$h.rpy" ]; then
            printf '  %-16s not written yet\n' "$h" >> "$INDEX"
            continue
        fi
        echo "review_pack: $h"
        # u2_dump writes tools/art/game_layout.json, which is committed only
        # from the owner's folder (the plan's 5.4): a pack gets its own copy.
        if [ "$h" = "u2_dump" ]; then
            SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-420}" SMOKE_SHOTS="$OUT/$h" "$ROOT/tools/smoke.sh" "$ROOT/tools/smoke/$h.rpy" --out "$OUT/u2_dump/game_layout.json" > "$OUT/$h.out" 2>&1
        else
            SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-420}" SMOKE_SHOTS="$OUT/$h" "$ROOT/tools/smoke.sh" "$ROOT/tools/smoke/$h.rpy" > "$OUT/$h.out" 2>&1
        fi
        rc=$?
        if [ "$rc" = "3" ]; then
            # Not a verdict on the harness: a game was open, or the wait for
            # the pointer ran out (tools/smoke.sh, exit status 3).
            printf '  %-16s REFUSED (a game was open or the wait ran out: run it again)\n' "$h" >> "$INDEX"
            REFUSED=1
            continue
        fi
        last="$(tail -n 1 "$OUT/$h/result.txt" 2>/dev/null)"
        n_pass="$(grep -c '^PASS' "$OUT/$h/result.txt" 2>/dev/null)"
        n_fail="$(grep -c '^FAIL' "$OUT/$h/result.txt" 2>/dev/null)"
        n_png="$(ls "$OUT/$h"/*.png 2>/dev/null | wc -l | tr -d ' ')"
        printf '  %-16s %-12s %s passed, %s failed, %s pictures\n' "$h" "${last:-no result}" "${n_pass:-0}" "${n_fail:-0}" "$n_png" >> "$INDEX"
        [ "$last" = "RESULT PASS" ] || FAILED=1
    done
    echo >> "$INDEX"
fi

echo "Layout sheets" >> "$INDEX"
if [ -z "$STEMS" ]; then
    echo "  none for this package" >> "$INDEX"
else
    mkdir -p "$OUT/layout"
    for s in $STEMS; do
        if python3 "$ROOT/tools/layout_sheet.py" "$s" --out "$OUT/layout/$s.png" > "$OUT/layout/$s.txt" 2>&1; then
            echo "  layout/$s.png" >> "$INDEX"
        else
            echo "  $s: no sheet ($(tail -n 1 "$OUT/layout/$s.txt" | cut -c 1-120))" >> "$INDEX"
        fi
    done
fi
echo >> "$INDEX"

echo "Stage sheets" >> "$INDEX"
if [ -f "$ROOT/tools/stage_preview.py" ] && [ -n "$SHEETS" ]; then
    mkdir -p "$OUT/stage"
    for s in $STEMS; do
        case "$s" in view_*) ;; *) continue ;; esac
        place="${s#view_}"
        if "$ROOT/tools/py_art.sh" "$ROOT/tools/stage_preview.py" "$place" --out "$OUT/stage/$place.jpg" > "$OUT/stage/$place.txt" 2>&1; then
            echo "  stage/$place.jpg" >> "$INDEX"
        else
            echo "  $place: no stage sheet ($(tail -n 1 "$OUT/stage/$place.txt" | cut -c 1-120))" >> "$INDEX"
        fi
    done
else
    echo "  none (tools/stage_preview.py arrives with U0d3, or the package has no rooms)" >> "$INDEX"
fi
echo >> "$INDEX"

{
    echo "== check_content.py --all"
    python3 "$ROOT/tools/check_content.py" --all "$ROOT"/game/*.rpy "$ROOT"/tools/smoke/*.rpy 2>&1
    echo
    echo "== check_content.py --later-notes (a report until integration)"
    python3 "$ROOT/tools/check_content.py" --later-notes "$ROOT"/game/*.rpy 2>&1
} > "$OUT/content.txt"
echo "Content checks" >> "$INDEX"
echo "  content.txt: $(grep -m 1 '^check_content: \(clean\|[0-9]* finding\)' "$OUT/content.txt" | cut -c 1-100)" >> "$INDEX"

cat "$INDEX"
echo
echo "review_pack: $OUT"
[ "$FAILED" = "1" ] && exit 1
[ "$REFUSED" = "1" ] && exit 3
exit 0
