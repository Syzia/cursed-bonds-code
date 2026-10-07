#!/bin/bash
# tools/load_all_saves.sh -- load every one of the owner's saves in a scratch
# copy and report where each lands (docs/PHASE1_DESIGN.md, 8.3).
#
#   tools/load_all_saves.sh            every save
#   tools/load_all_saves.sh 1-1 auto-3 just these slots
#   tools/load_all_saves.sh --from <folder> [--from <folder> ...] [slot ...]
#                                      the saves of these folders instead of
#                                      the owner's: a snapshot (the owner keeps
#                                      playing and autosaves rotate), or the
#                                      made saves in tools/smoke/assets/ui2_saves
#
# The second UI overhaul's save set (docs/UI2_DESIGN.md D42; standard acceptance
# (e)) is the snapshot of the owner's eleven and the nineteen made saves:
#   tools/load_all_saves.sh --from ~/Desktop/JJK_backup_ui2_20261007/snapshot \
#                           --from tools/smoke/assets/ui2_saves
# docs/load_report_ui2_wave0.txt is what it gave before anything changed.
#
# Without --from the saves are the *.save files in game/saves and in the user
# save folder (~/Library/RenPy/<config.save_directory>). Names with spaces (Finder
# duplicates such as "auto-8-LT1 2.save") are skipped. A slot present in both
# folders is loaded once: Ren'Py picks the newer copy, as the game would.
#
# Each slot runs tools/smoke/load_slot.rpy through tools/smoke.sh with
# SMOKE_SAVES=1, so only read-only copies of the saves are used, in a scratch
# project. Per-slot results go to shots/load_slot/<slot>/ (result.txt and
# landed.png); the combined report is shots/load_report.txt: the status
# table, then a summary per slot (version, technique, grade, arc, day, roster
# size, merit, story step, objective, keepsakes, where it landed), then each
# slot's full result.
#
# Status per slot: SAME (landed where it was saved), EARLIER (its statement is
# gone; rolled back to an older one), MOVED, RECOVER load_recover /
# return_recover, UNKNOWN, or RAISED (an exception, a timeout or no result).
# Exits 1 if any slot RAISED. Slots whose call stack holds a return site the
# script no longer has are listed under "Dead return sites", with where
# return_recover will send them once play returns that far; the table's last
# column gives each slot's dead return sites ("none" is what is wanted: a slot
# is SAME when it lands on its statement even if a return site below it is
# gone, so SAME alone does not prove a save whole).
#
# Environment: SMOKE_TIMEOUT per slot (default 120); LOAD_SHOTS to write the
# results somewhere other than shots/ (e.g. a scratch folder).
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SAVE_DIRNAME="$(sed -n 's/^define config.save_directory *= *"\(.*\)".*/\1/p' "$ROOT/game/options.rpy" | head -n 1)"
SAVE_DIRNAME="${SAVE_DIRNAME:-JJKgamemd-1788928056}"
USER_SAVES="$HOME/Library/RenPy/$SAVE_DIRNAME"
GAME_SAVES="$ROOT/game/saves"
SHOTS_DIR="${LOAD_SHOTS:-$ROOT/shots}"
OUT="$SHOTS_DIR/load_slot"
REPORT="$SHOTS_DIR/load_report.txt"
SUFFIX="-LT1.save"

# --from <folder>, any number of times, before the slot names.
FROM=""
FROM_LIST=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --from)
            [ "$#" -ge 2 ] || { echo "load_all_saves.sh: --from needs a folder" >&2; exit 2; }
            [ -d "$2" ] || { echo "load_all_saves.sh: --from: no folder $2" >&2; exit 2; }
            d="$(cd "$2" && pwd -P)"
            FROM="${FROM:+$FROM:}$d"
            FROM_LIST="$FROM_LIST
$d"
            shift 2 ;;
        --) shift; break ;;
        -*) echo "load_all_saves.sh: unknown option $1" >&2; exit 2 ;;
        *) break ;;
    esac
done

mkdir -p "$OUT"

# The slot names, unique, with the space-named files set aside.
SKIPPED=""
ALL=""
if [ -n "$FROM" ]; then
    DIRS="$(printf '%s\n' "$FROM_LIST" | sed '/^$/d')"
else
    DIRS="$GAME_SAVES
$USER_SAVES"
fi
OLDIFS="$IFS"; IFS="
"
for dir in $DIRS; do
    [ -d "$dir" ] || continue
    for f in "$dir"/*.save; do
        [ -f "$f" ] || continue
        b="$(basename "$f")"
        case "$b" in
            *" "*) SKIPPED="$SKIPPED
  $dir/$b" ;;
            *) ALL="$ALL
${b%$SUFFIX}" ;;
        esac
    done
done
IFS="$OLDIFS"
if [ "$#" -gt 0 ]; then
    SLOTS="$(printf '%s\n' "$@" | sed "s/$SUFFIX\$//")"
else
    SLOTS="$(printf '%s\n' "$ALL" | sed '/^$/d' | sort -u)"
fi
[ -n "$SLOTS" ] || { echo "load_all_saves.sh: no saves found in $(printf '%s' "$DIRS" | tr '\n' ' ')" >&2; exit 2; }

where_from() {
    # Which folders hold this slot, and whether the copies match.
    local s="$1" a="$GAME_SAVES/$1$SUFFIX" b="$USER_SAVES/$1$SUFFIX" r="" d
    if [ -n "$FROM" ]; then
        OLDIFS="$IFS"; IFS=":"
        for d in $FROM; do
            [ -f "$d/$1$SUFFIX" ] && r="${r:+$r + }$d"
        done
        IFS="$OLDIFS"
        echo "${r:-not found}"
        return
    fi
    [ -f "$a" ] && r="game/saves"
    [ -f "$b" ] && r="${r:+$r + }~/Library/RenPy/$SAVE_DIRNAME"
    if [ -f "$a" ] && [ -f "$b" ]; then
        if cmp -s "$a" "$b"; then r="$r (identical)"; else r="$r (DIFFERENT copies; the newer loads)"; fi
    fi
    echo "${r:-not found}"
}

field() { sed -n "s/^NOTE $1: //p" "$2" | head -n 1; }

TABLE=""
SUMMARY=""
DETAILS=""
DEAD=""
N=0; N_SAME=0; N_EARLIER=0; N_MOVED=0; N_RECOVER=0; N_UNKNOWN=0; N_RAISED=0
for slot in $SLOTS; do
    N=$((N + 1))
    printf 'loading %-24s ' "$slot"
    SMOKE_SAVES=1 SMOKE_SAVES_FROM="$FROM" SMOKE_SLOT="$slot" SMOKE_SHOTS="$OUT/$slot" SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-120}" \
        "$ROOT/tools/smoke.sh" "$ROOT/tools/smoke/load_slot.rpy" > /dev/null 2>&1
    res="$OUT/$slot/result.txt"
    if [ -f "$res" ] && [ "$(tail -n 1 "$res")" = "RESULT PASS" ]; then
        status="$(field status "$res")"
        saved="$(field saved_at "$res")"
        landed="$(field landed "$res")"
    else
        status="RAISED"
        saved="$( [ -f "$res" ] && field saved_at "$res")"
        landed="$( [ -f "$res" ] && grep -m 1 '^FAIL' "$res" | cut -c 1-90)"
    fi
    case "$status" in
        SAME) N_SAME=$((N_SAME + 1)) ;;
        EARLIER) N_EARLIER=$((N_EARLIER + 1)) ;;
        MOVED) N_MOVED=$((N_MOVED + 1)) ;;
        UNKNOWN) N_UNKNOWN=$((N_UNKNOWN + 1)) ;;
        RECOVER*) N_RECOVER=$((N_RECOVER + 1)) ;;
        *) N_RAISED=$((N_RAISED + 1)) ;;
    esac
    echo "$status"
    dead="$( [ -f "$res" ] && field dead_return_sites "$res")"
    if [ -n "$dead" ] && [ "$dead" != "none" ]; then
        DEAD="$DEAD
  $slot: $dead
      $(field on_dead_return "$res")"
    fi
    TABLE="$TABLE$(printf '%-24s %-22s %-34s %-34s %s' "$slot" "$status" "${saved:--}" "${landed:--}" "${dead:--}")
"
    # The per-slot summary (WP11 task 5), from load_slot.rpy's report.* notes.
    if [ -f "$res" ] && grep -q '^NOTE report\.' "$res"; then
        SUMMARY="$SUMMARY
$slot
  version    $(field 'report\.version' "$res")
  technique  $(field 'report\.technique' "$res") · grade $(field 'report\.grade' "$res") · arc $(field 'report\.arc' "$res") · day $(field 'report\.day' "$res")
  roster     $(field 'report\.roster' "$res") · merit $(field 'report\.merit' "$res")
  story step $(field 'report\.story_step' "$res")
  objective  $(field 'report\.objective' "$res")
  keepsakes  $(field 'report\.keepsakes' "$res")
  landed     $(field 'report\.where' "$res")"
    else
        SUMMARY="$SUMMARY
$slot
  (no summary: $status${landed:+ · $landed})"
    fi
    DETAILS="$DETAILS
=== $slot · $(where_from "$slot")
$( [ -f "$res" ] && cat "$res" || echo "(no result file)")
"
done

HEAD="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo '?')"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
DIRTY="$( [ -n "$(git -C "$ROOT" status --porcelain 2>/dev/null)" ] && echo ' + uncommitted changes')"

{
    echo "Load report · $(date '+%Y-%m-%d %H:%M') · $BRANCH @ $HEAD$DIRTY"
    if [ -n "$FROM" ]; then
        echo "Saves from (--from): $(printf '%s' "$DIRS" | tr '\n' ' ')"
    else
        echo "Saves from: $GAME_SAVES"
        echo "            $USER_SAVES"
    fi
    echo "Slots: $N · SAME $N_SAME · EARLIER $N_EARLIER · MOVED $N_MOVED · RECOVER $N_RECOVER · UNKNOWN $N_UNKNOWN · RAISED $N_RAISED"
    [ -n "$SKIPPED" ] && echo "Skipped (names with spaces):$SKIPPED"
    [ -n "$DEAD" ] && echo "Dead return sites (a later \`return\` reaches return_recover):$DEAD"
    echo
    echo "SAME: landed where it was saved. EARLIER: its statement is gone, so it rolled back"
    echo "to an older one (rollback_target) and stopped at the next interaction (LANDED)."
    echo "MOVED: its statement exists but it landed elsewhere. RECOVER: load_recover /"
    echo "return_recover ran. UNKNOWN: the save's log couldn't be read before loading."
    echo "RAISED: an exception, a timeout or no result (see the slot's section below)."
    echo
    printf '%-24s %-22s %-34s %-34s %s\n' "SLOT" "STATUS" "SAVED AT" "LANDED" "DEAD RETURN SITES"
    printf '%s' "$TABLE"
    echo
    echo "Per slot: version, technique, grade, arc, day, roster size, merit, story step"
    echo "(story_point, or legacy_story_point() for a save without one, then the story row"
    echo "the objective points at), the objective, keepsakes, and where it landed."
    printf '%s\n' "$SUMMARY"
    printf '%s\n' "$DETAILS"
} > "$REPORT"

echo
echo "Slots: $N · SAME $N_SAME · EARLIER $N_EARLIER · MOVED $N_MOVED · RECOVER $N_RECOVER · UNKNOWN $N_UNKNOWN · RAISED $N_RAISED"
echo "Report: $REPORT"
[ "$N_RAISED" -eq 0 ]
