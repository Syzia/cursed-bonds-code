#!/bin/bash
# Run a throwaway Ren'Py test harness, then remove every trace of it.
#
#   tools/smoke.sh path/to/harness.rpy
#
# The harness is copied to game/zz_smoke.rpy and run headless. Ren'Py compiles
# it to zz_smoke.rpyc -- and will keep running a stray .rpyc even after the
# .rpy is gone, which is how a finished test once hijacked the real game's
# splash screen. So the trap below removes the source, the compiled file and
# its backup however the run ends.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${RENPY_SDK:-$HOME/Desktop/renpy-8.5.3-sdk}"
cleanup() { rm -f "$ROOT"/game/zz_smoke.rpy "$ROOT"/game/zz_smoke.rpyc "$ROOT"/game/zz_smoke.rpyc.bak; }
trap cleanup EXIT INT TERM
# Without a harness Ren'Py would just start the real game and sit there until
# the watchdog kills it.
[ -f "${1:-}" ] || { echo "no harness at ${1:-<none>}" >&2; exit 2; }
cp "$1" "$ROOT/game/zz_smoke.rpy"
# A real window by default: on macOS 27 the dummy SDL driver stalls at
# "Initializing sw renderer" and never runs the script. HEADLESS=1 opts back in.
if [ "${HEADLESS:-0}" = "1" ]; then export SDL_VIDEODRIVER=dummy; fi
"$SDK/renpy.sh" "$ROOT" > "${SMOKE_LOG:-/dev/null}" 2>&1 &
pid=$!
# macOS has no `timeout`; a harness that hits an error screen waits forever.
( sleep "${SMOKE_TIMEOUT:-180}"; kill -9 $pid 2>/dev/null ) &
watchdog=$!
wait $pid
status=$?
kill $watchdog 2>/dev/null
cleanup
ls "$ROOT"/game/zz_smoke* >/dev/null 2>&1 && { echo "!! harness files survived cleanup"; exit 1; }
exit $status
