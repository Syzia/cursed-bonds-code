#!/bin/bash
# tools/smoke.sh v2 -- run one Ren'Py test harness in a throwaway copy of the
# project (docs/PHASE1_DESIGN.md, section 8.1).
#
#   tools/smoke.sh <harness.rpy>
#
# Environment:
#   SMOKE_TIMEOUT=180  seconds before the watchdog kills the run
#   SMOKE_SAVES=1      copy the owner's saves (game/saves and the user save
#                      folder) into the scratch copy, as read-only copies
#   SMOKE_SLOT=<slot>  the slot tools/smoke/load_slot.rpy loads
#   SMOKE_SHOTS=<dir>  where result.txt, screenshots and logs go
#                      (default: shots/<harness name>/ in the repo)
#   HEADLESS=1         use SDL's dummy video driver. Off by default: on
#                      macOS 27 it stalls at "Initializing sw renderer".
#   RENPY_SDK=<dir>    the SDK (default ~/Desktop/renpy-8.5.3-sdk)
#
# How it works:
#   1. A scratch project is made under $TMPDIR/jjk_smoke.XXXX/. game/*.rpy and
#      game/*.rpyc are copied (so compiling touches only the copies), the asset
#      folders (images, gui, fonts, audio, ...) are symlinked, and
#      tools/smoke/_lib.rpy and the harness are installed as
#      game/zz_smoke_lib.rpy and game/zz_smoke.rpy.
#   2. Ren'Py runs the scratch project with --savedir <scratch>/savedir, so the
#      owner's saves, persistent data and .rpyc are never touched. Logs,
#      tracebacks and tracesaves land in the scratch copy too. Ren'Py's script
#      backups (normally ~/Library/RenPy/backups/<project>/) are switched off
#      with RENPY_DISABLE_BACKUPS. The only thing read outside the project is
#      the save-token key file Ren'Py always reads (~/Library/RenPy/tokens).
#   3. A watchdog stops the run after SMOKE_TIMEOUT, or shortly after the
#      harness has written its result, or after an error screen has sat
#      there with no result (an init or parse error the harness can't catch).
#   4. The result is $SMOKE_SHOTS/result.txt. It is printed, and the exit
#      status is 0 only when its last line is "RESULT PASS". The scratch copy
#      is deleted either way. Ren'Py's console output, log.txt and any
#      traceback.txt / errors.txt are kept next to the result.
#
# Nothing is ever written into the real game/ folder, so several harnesses can
# run at once, even from one checkout.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${RENPY_SDK:-$HOME/Desktop/renpy-8.5.3-sdk}"
LIB="$ROOT/tools/smoke/_lib.rpy"

die() { echo "smoke.sh: $*" >&2; exit 2; }

HARNESS="${1:-}"
[ -n "$HARNESS" ] && [ -f "$HARNESS" ] || die "no harness at ${HARNESS:-<none>} (usage: tools/smoke.sh <harness.rpy>)"
case "$HARNESS" in *.rpy) ;; *) die "the harness must be a .rpy file: $HARNESS" ;; esac
HARNESS="$(cd "$(dirname "$HARNESS")" && pwd)/$(basename "$HARNESS")"
NAME="$(basename "$HARNESS" .rpy)"
[ -x "$SDK/renpy.sh" ] || die "no Ren'Py SDK at $SDK (set RENPY_SDK)"
[ -f "$LIB" ] || die "missing $LIB"

TIMEOUT="${SMOKE_TIMEOUT:-180}"
case "$TIMEOUT" in ''|*[!0-9]*) die "SMOKE_TIMEOUT must be a whole number of seconds" ;; esac

# The results folder. Absolute, because Ren'Py runs from somewhere else.
SHOTS="${SMOKE_SHOTS:-$ROOT/shots/$NAME}"
mkdir -p "$SHOTS" || die "cannot create $SHOTS"
SHOTS="$(cd "$SHOTS" && pwd -P)"
REALGAME="$(cd "$ROOT/game" && pwd -P)"
case "$SHOTS/" in "$REALGAME"/*) die "SMOKE_SHOTS may not be inside the real game/ folder" ;; esac
RESULT="$SHOTS/result.txt"
# Stale files from an earlier run would be mistaken for this one's.
rm -f "$RESULT" "$RESULT.tmp" "$SHOTS/console.txt" "$SHOTS/log.txt" \
      "$SHOTS/traceback.txt" "$SHOTS/errors.txt"

# --- the scratch copy ----------------------------------------------------------
TMPBASE="${TMPDIR:-/tmp}"
TMPBASE="${TMPBASE%/}"
SCRATCH="$(mktemp -d "$TMPBASE/jjk_smoke.XXXX")" || die "mktemp failed in $TMPBASE"
PID=""

cleanup() {
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        kill -TERM "$PID" 2>/dev/null
        sleep 1
        kill -9 "$PID" 2>/dev/null
    fi
    case "$SCRATCH" in
        "$TMPBASE"/jjk_smoke.*) [ -d "$SCRATCH" ] && rm -rf "$SCRATCH" ;;
    esac
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP

G="$SCRATCH/game"
mkdir -p "$G/saves" "$SCRATCH/savedir" || die "cannot populate $SCRATCH"

# Scripts are copied, with their timestamps, so the scratch compile keeps the
# owner's statement names and never writes a .rpyc into the real tree. Stray
# zz_* harness files from older tooling are left behind.
for f in "$ROOT"/game/*; do
    b="$(basename "$f")"
    case "$b" in zz_*|saves|cache|*.bak|*.new|*.old) continue ;; esac
    if [ -d "$f" ]; then
        # Asset folders are symlinked. A folder holding scripts is copied
        # instead, or Ren'Py would compile into the real tree through the link.
        if [ -n "$(find -H "$f" \( -name '*.rpy' -o -name '*.rpym' -o -name '*.rpyc' -o -name '*.rpymc' \) -print -quit)" ]; then
            cp -Rp "$f" "$G/$b"
        else
            ln -s "$f" "$G/$b"
        fi
    else
        case "$b" in
            *.rpy|*.rpyc|*.rpym|*.rpymc) cp -p "$f" "$G/$b" ;;
            *) ln -s "$f" "$G/$b" ;;
        esac
    fi
done
# The bytecode cache only saves start-up time; the copy is private to this run.
[ -d "$ROOT/game/cache" ] && cp -Rp "$ROOT/game/cache" "$G/cache"

cp "$LIB" "$G/zz_smoke_lib.rpy"
cp "$HARNESS" "$G/zz_smoke.rpy"

# The owner's saves, as read-only copies (SMOKE_SAVES=1).
if [ "${SMOKE_SAVES:-0}" = "1" ]; then
    SAVE_DIRNAME="$(sed -n 's/^define config.save_directory *= *"\(.*\)".*/\1/p' "$ROOT/game/options.rpy" | head -n 1)"
    USER_SAVES="$HOME/Library/RenPy/${SAVE_DIRNAME:-JJKgamemd-1788928056}"
    for f in "$ROOT"/game/saves/*.save; do
        [ -f "$f" ] && cp -p "$f" "$G/saves/"
    done
    for f in "$USER_SAVES"/*.save; do
        [ -f "$f" ] && cp -p "$f" "$SCRATCH/savedir/"
    done
    chmod a-w "$G"/saves/*.save "$SCRATCH"/savedir/*.save 2>/dev/null
fi

# Ren'Py opens traceback.txt in an editor when a run fails at start-up. A
# do-nothing editor keeps that from popping up during tests.
cat > "$SCRATCH/noop_editor.py" <<'EOF'
class Editor(object):
    def begin(self, new_window=False, **kwargs):
        pass
    def end(self, **kwargs):
        pass
    def open(self, filename, line=None, **kwargs):
        pass
EOF

export SMOKE_SHOTS="$SHOTS"
# Ren'Py's own switch; without it every compile copies the scripts into
# ~/Library/RenPy/backups/jjk_smoke.XXXX/.
export RENPY_DISABLE_BACKUPS="I take responsibility for this."
export SMOKE_HARNESS="$NAME"
export RENPY_EDIT_PY="$SCRATCH/noop_editor.py"
if [ "${HEADLESS:-0}" = "1" ]; then
    export SDL_VIDEODRIVER=dummy
    export SDL_AUDIODRIVER=dummy
fi

# --- the run -------------------------------------------------------------------
last_line() { [ -f "$RESULT" ] && tail -n 1 "$RESULT" | tr -d '\r'; }

"$SDK/renpy.sh" "$SCRATCH" run --savedir "$SCRATCH/savedir" > "$SHOTS/console.txt" 2>&1 &
PID=$!

REASON=""
started=$SECONDS
done_at=""
error_at=""
while kill -0 "$PID" 2>/dev/null; do
    now=$SECONDS
    case "$(last_line)" in
        "RESULT PASS"|"RESULT FAIL")
            # Finished: give Ren'Py a moment to quit on its own.
            [ -z "$done_at" ] && done_at=$now
            if [ $((now - done_at)) -ge 15 ]; then REASON="quit"; break; fi
            ;;
        *)
            if [ -f "$SCRATCH/traceback.txt" ] || [ -f "$SCRATCH/errors.txt" ]; then
                # An error the harness may still be reporting. If no result
                # follows, it is sitting on Ren'Py's error screen.
                [ -z "$error_at" ] && error_at=$now
                if [ $((now - error_at)) -ge 10 ]; then REASON="error screen"; break; fi
            fi
            ;;
    esac
    if [ $((now - started)) -ge "$TIMEOUT" ]; then REASON="timeout"; break; fi
    sleep 1
done
if kill -0 "$PID" 2>/dev/null; then
    kill -TERM "$PID" 2>/dev/null
    sleep 2
    kill -9 "$PID" 2>/dev/null
fi
wait "$PID" 2>/dev/null
PID=""

for f in log.txt traceback.txt errors.txt; do
    [ -f "$SCRATCH/$f" ] && cp "$SCRATCH/$f" "$SHOTS/$f"
done

# No verdict from the harness: write one.
case "$(last_line)" in
    "RESULT PASS"|"RESULT FAIL") ;;
    *)
        {
            [ -f "$RESULT" ] && cat "$RESULT"
            if [ "$REASON" = "timeout" ] && { [ -f "$SCRATCH/traceback.txt" ] || [ -f "$SCRATCH/errors.txt" ]; }; then
                REASON="error screen"
            fi
            case "$REASON" in
                timeout)        echo "FAIL smoke: no result after ${TIMEOUT}s (watchdog)" ;;
                "error screen") echo "FAIL smoke: Ren'Py stopped on an error screen before the harness could report" ;;
                *)              echo "FAIL smoke: Ren'Py exited without a result" ;;
            esac
            for f in errors.txt traceback.txt; do
                if [ -f "$SCRATCH/$f" ]; then
                    echo "--- $f"
                    LC_ALL=C sed "1s/^$(printf '\357\273\277')//" "$SCRATCH/$f" | sed -n '1,60p'
                fi
            done
            echo "RESULT FAIL"
        } > "$RESULT.tmp"
        mv "$RESULT.tmp" "$RESULT"
        ;;
esac

cat "$RESULT"
if [ "$(last_line)" = "RESULT PASS" ]; then exit 0; else exit 1; fi
