#!/bin/bash
# tools/smoke.sh v4 -- run one Ren'Py test harness in a throwaway copy of the
# project (docs/PHASE1_DESIGN.md, section 8.1; docs/PHASE2_DESIGN.md, D49;
# docs/UI2_DESIGN.md, K13 and 5.4).
#
#   tools/smoke.sh <harness.rpy>
#   tools/smoke.sh <name>                the same as tools/smoke/<name>.rpy
#   tools/smoke.sh --open-games          the games a pointer harness would refuse
#                                        for, one "<pid> <project>" a line
#   tools/smoke.sh --lock-selftest       checks that list against made-up
#                                        process lines (see open_games below)
#   tools/smoke.sh <name> --out <file>   a harness that writes a file for the
#                                        repository (see 5) writes it to <file>
#                                        instead: tools/smoke.sh u2_dump --out
#                                        shots/art/game_layout.json
#
# Environment:
#   SMOKE_TIMEOUT=180  seconds before the watchdog kills the run
#   SMOKE_SAVES=1      copy the owner's saves (game/saves and the user save
#                      folder) into the scratch copy, as read-only copies
#   SMOKE_SAVES_FROM=<dir>[:<dir>...]  with SMOKE_SAVES=1: copy the *.save
#                      files of these folders instead of the owner's (a
#                      snapshot, or tools/smoke/assets/ui2_saves)
#   SMOKE_SLOT=<slot>  the slot tools/smoke/load_slot.rpy loads
#   SMOKE_SHOTS=<dir>  where result.txt, screenshots and logs go
#                      (default: shots/<harness name>/ in the repo)
#   SMOKE_ASSETS=<dir> an overlay folder to use instead of
#                      tools/smoke/assets/<harness name>/ (see 2b)
#   HEADLESS=1         use SDL's dummy video driver. Off by default: on
#                      macOS 27 it stalls at "Initializing sw renderer".
#   RENPY_SDK=<dir>    the SDK (default ~/Desktop/renpy-8.5.3-sdk)
#   SMOKE_POINTER=1|0  treat this harness as one that needs the pointer, or as
#                      one that does not, whatever the list says (see 6)
#   SMOKE_LOCK_WAIT=14400 seconds to wait for the pointer before giving up
#                      (four hours: six worktrees' pointer harnesses, one after
#                      another, are about ninety minutes). A run that gives up
#                      says REFUSED and exits with status 3: run it again; it
#                      is not a failed harness.
#   SMOKE_PS_FIXTURE=<file>  read in place of the process list (--lock-selftest)
#   SMOKE_LOCK_DIR=<dir>  the lock folder (default ~/Library/Caches/jjk_smoke;
#                      another folder only to test the lock itself)
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
#      The harness also sees SMOKE_ROOT, the repository it was started from,
#      so it can read (never write) files such as tools/smoke/baseline_p0.json.
#   2a. Extra scripts. A harness line `## smoke-with: <file>.rpy` installs
#      tools/smoke/<file>.rpy into the scratch game/ under its own name (this
#      is how p2_contracts.rpy runs with aa_zz_order.rpy, which must sort
#      before every game file).
#   2b. The asset overlay (D49). When tools/smoke/assets/<harness name>/ exists,
#      every file under its game/ folder is copied to the same path under the
#      scratch game/ (tools/smoke/assets/p2_contracts/game/layout/x.json lands
#      at <scratch>/game/layout/x.json). The asset folders of the scratch copy
#      are links into the real game/, so each folder on the way is first made
#      a real folder holding links to the original's children, and a link the
#      file would replace is removed first: nothing is ever written through a
#      link, and a test picture never lands in the real game/images/.
#   3. A watchdog stops the run after SMOKE_TIMEOUT, or shortly after the
#      harness has written its result, or after an error screen has sat
#      there with no result (an init or parse error the harness can't catch).
#   4. The result is $SMOKE_SHOTS/result.txt. It is printed, and the exit
#      status is 0 only when its last line is "RESULT PASS". The scratch copy
#      is deleted either way. Ren'Py's console output, log.txt and any
#      traceback.txt / errors.txt are kept next to the result.
#   5. A file for the repository. A harness line
#        ## smoke-out: <file> -> <path in the repository>
#      says the harness writes <file> into $SMOKE_SHOTS and where it belongs
#      (tools/smoke/u2_dump.rpy: game_layout.json -> tools/art/game_layout.json).
#      After a RESULT PASS this script copies it there, or to the file --out
#      names. Nothing is copied after a failure, and never into game/.
#   6. The pointer lock (docs/UI2_DESIGN.md, K13). Some harnesses rest the
#      pointer on a button (or use renpy.set_focus) and fail, for no real
#      reason, while any other Ren'Py window is open. They are the names in
#      SMOKE_POINTER_LIST below and any harness with a line `## smoke-pointer`.
#      Such a run
#        - refuses, with one line and exit status 3, while a Ren'Py game that
#          is not a smoke run is open (the owner playing, started from the
#          launcher or any other way; a second copy of the game; the
#          launcher's own window does not count);
#        - takes the machine-wide lock, the folder
#          ~/Library/Caches/jjk_smoke/pointer.lock, waiting for whoever holds
#          it (another pointer harness, from this checkout or any worktree);
#        - then waits for every other smoke run on this machine to finish.
#      A harness that does not need the pointer waits while the lock is held,
#      so it never opens a window under a pointer harness. A lock whose holder
#      has died is taken over. Nobody has to arrange any of this by hand.
#
# Nothing is ever written into the real game/ folder, so several harnesses can
# run at once, even from one checkout (the pointer harnesses take their turn,
# 6). That holds when game/cache (or a folder
# of scripts) is a symbolic link as well: such a link is followed and its
# contents are copied. Still, never set up a worktree or a scratch root with
# game/cache linked to another tree's.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${RENPY_SDK:-$HOME/Desktop/renpy-8.5.3-sdk}"
LIB="$ROOT/tools/smoke/_lib.rpy"

die() { echo "smoke.sh: $*" >&2; exit 2; }

# "<pid> <project>" for every Ren'Py game open on this machine that is neither
# the launcher, nor a smoke run, nor a lint or compile (which open no window).
# A game is started in three shapes, and all three count:
#   <sdk>/renpy.sh <project>            seen as <sdk>/lib/py3-.../renpy <project>
#   <sdk>/renpy.app/Contents/MacOS/pythonw <sdk>/renpy.py <project> --json-dump ...
#                                       the launcher's "Launch Project" (python
#                                       in place of pythonw with the console on)
#   python renpy.py <project>           by hand
# The launcher's own window is renpy.app/Contents/MacOS/renpy with no project.
# SMOKE_PS_FIXTURE=<file> is read in place of the process list (the self-test).
open_games() {
    if [ -n "${SMOKE_PS_FIXTURE:-}" ]; then cat "$SMOKE_PS_FIXTURE"; else ps -axo pid=,command= 2>/dev/null; fi | awk '
        {
            pid = $1; exe = $2
            ok = 0
            if (exe ~ /(^|\/)renpy(\.sh|\.py|\.exe)?$/) ok = 1
            else if (exe ~ /(^|\/)pythonw?[0-9.]*(\.exe)?$/) {
                if (exe ~ /\/(lib\/py[^\/]*|renpy\.app\/Contents\/MacOS)\/[^\/]*$/) ok = 1
                else if ($0 ~ /(^|[ \/])renpy\.py( |$)/) ok = 1
            }
            if (!ok) next
            if ($0 !~ /[Rr]en.?[Pp]y/) next
            if ($0 ~ /jjk_smoke\./) next
            proj = ""; quiet = 0
            for (i = 3; i <= NF; i++) {
                if ($i ~ /^-/) continue
                if ($i ~ /renpy\.py$/) continue
                if (proj == "") { proj = $i; continue }
                if ($i == "lint" || $i == "compile" || $i == "translate" || $i == "dialogue" || $i == "distribute") quiet = 1
            }
            if (proj == "" || proj ~ /\/launcher\/?$/ || quiet) next
            print pid " " proj
        }'
}

# tools/smoke.sh --open-games     prints what a pointer harness would refuse for
# tools/smoke.sh --lock-selftest  feeds open_games the shapes above and says
#                                 whether each is seen (exit status 0 when all are)
case "${1:-}" in
    --open-games) open_games; exit 0 ;;
    --lock-selftest)
        T="$(mktemp "${TMPDIR:-/tmp}/jjk_lock_selftest.XXXX")" || die "mktemp failed"
        cat > "$T" <<'EOF_PS'
101 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/pythonw /S/renpy-8.5.3-sdk/renpy.py /Users/x/Desktop/JJKgame.md --json-dump /tmp/a/dump.json
102 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/python /S/renpy-8.5.3-sdk/renpy.py /Users/x/Desktop/JJKgame.md
103 /S/renpy-8.5.3-sdk/lib/py3-mac-universal/pythonw /S/renpy-8.5.3-sdk/renpy.py /Users/x/wt/U1
104 /S/renpy-8.5.3-sdk/lib/py3-mac-universal/renpy /Users/x/wt/U2
105 /usr/bin/python3 /S/renpy-8.5.3-sdk/renpy.py /Users/x/wt/U3 run
106 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/renpy /Users/x/wt/U4
201 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/renpy
202 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/pythonw /S/renpy-8.5.3-sdk/renpy.py /S/renpy-8.5.3-sdk/launcher
203 /S/renpy-8.5.3-sdk/lib/py3-mac-universal/renpy /private/tmp/jjk_smoke.Ab12 run --savedir /private/tmp/jjk_smoke.Ab12/savedir
204 /S/renpy-8.5.3-sdk/lib/py3-mac-universal/renpy /Users/x/scratch/lintcopy lint
205 /S/renpy-8.5.3-sdk/renpy.app/Contents/MacOS/pythonw /S/renpy-8.5.3-sdk/renpy.py /Users/x/scratch/lintcopy compile
206 /usr/bin/python3 /Users/x/Desktop/JJKgame.md/tools/check_content.py --all
207 /bin/bash /Users/x/Desktop/JJKgame.md/tools/smoke.sh p2_cards
208 /usr/bin/python3 -m http.server
EOF_PS
        GOT="$(SMOKE_PS_FIXTURE="$T" open_games | awk '{print $1}' | tr '\n' ' ')"
        rm -f "${T:?}"
        WANT="101 102 103 104 105 106 "
        if [ "$GOT" = "$WANT" ]; then
            echo "smoke.sh: lock self-test PASS (the six ways a game is started are seen; the launcher, a smoke run, a lint, a compile and the tools are not)"
            exit 0
        fi
        echo "smoke.sh: lock self-test FAIL: saw [$GOT] and wanted [$WANT]" >&2
        exit 1 ;;
esac

USAGE="usage: tools/smoke.sh <harness.rpy | name> [--out <file>]"
HARNESS="${1:-}"
[ "$#" -gt 0 ] && shift
# A bare name is tools/smoke/<name>.rpy.
if [ -n "$HARNESS" ] && [ ! -f "$HARNESS" ]; then
    case "$HARNESS" in
        */*|*.rpy) ;;
        *) [ -f "$ROOT/tools/smoke/$HARNESS.rpy" ] && HARNESS="$ROOT/tools/smoke/$HARNESS.rpy" ;;
    esac
fi
[ -n "$HARNESS" ] && [ -f "$HARNESS" ] || die "no harness at ${HARNESS:-<none>} ($USAGE)"
case "$HARNESS" in *.rpy) ;; *) die "the harness must be a .rpy file: $HARNESS" ;; esac
OUT_FILE=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --out) [ "$#" -ge 2 ] || die "--out needs a file name"; OUT_FILE="$2"; shift 2 ;;
        --out=*) OUT_FILE="${1#--out=}"; shift ;;
        *) die "unknown argument: $1 ($USAGE)" ;;
    esac
done
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

# A file the harness writes for the repository (5): `## smoke-out: a -> b`.
OUT_RX='^## smoke-out: *\([A-Za-z0-9_.-][A-Za-z0-9_.-]*\) *-> *\([A-Za-z0-9_./-][A-Za-z0-9_./-]*\) *$'
OUT_NAME="$(sed -n "s|$OUT_RX|\\1|p" "$HARNESS" | head -n 1)"
OUT_DEFAULT="$(sed -n "s|$OUT_RX|\\2|p" "$HARNESS" | head -n 1)"
OUT_DEST=""
if [ -n "$OUT_FILE" ]; then
    [ -n "$OUT_NAME" ] || die "--out: $NAME writes no file for the repository (it has no '## smoke-out:' line)"
    case "$OUT_FILE" in /*) OUT_DEST="$OUT_FILE" ;; *) OUT_DEST="$PWD/$OUT_FILE" ;; esac
elif [ -n "$OUT_NAME" ]; then
    case "/$OUT_DEFAULT/" in */../*) die "smoke-out: bad path $OUT_DEFAULT" ;; esac
    OUT_DEST="$ROOT/$OUT_DEFAULT"
fi
if [ -n "$OUT_DEST" ]; then
    mkdir -p "$(dirname "$OUT_DEST")" || die "cannot create the folder of $OUT_DEST"
    OUT_DEST="$(cd "$(dirname "$OUT_DEST")" && pwd -P)/$(basename "$OUT_DEST")"
    case "$OUT_DEST" in "$REALGAME"/*) die "a harness's file may not be written inside the real game/ folder: $OUT_DEST" ;; esac
    rm -f "${SHOTS:?}/${OUT_NAME:?}"
fi

# --- the pointer lock (6) ------------------------------------------------------
# The harnesses that rest the pointer on a button or use renpy.set_focus. A
# new one names itself with a line `## smoke-pointer`.
SMOKE_POINTER_LIST="p2_contracts p2_hud p2_map p2_journal p2_view p2_rooms p2_paths p2_cards p2_saves phase2_all u2_map"
LOCK_BASE="${SMOKE_LOCK_DIR:-$HOME/Library/Caches/jjk_smoke}"
LOCK="$LOCK_BASE/pointer.lock"
RUNNING="$LOCK_BASE/running"
LOCK_WAIT="${SMOKE_LOCK_WAIT:-14400}"
case "$LOCK_WAIT" in ''|*[!0-9]*) die "SMOKE_LOCK_WAIT must be a whole number of seconds" ;; esac
HAVE_LOCK=0
MARKER=""
SCRATCH_MARK="jjk_smoke.none"

POINTER=0
case " $SMOKE_POINTER_LIST " in *" $NAME "*) POINTER=1 ;; esac
grep -q '^## smoke-pointer *$' "$HARNESS" && POINTER=1
case "${SMOKE_POINTER:-}" in 1) POINTER=1 ;; 0) POINTER=0 ;; esac

games_line() { open_games | tr '\n' ';' | sed 's/;$//'; }

lock_holder() { cat "$LOCK/pid" 2>/dev/null; }
lock_what() { cat "$LOCK/what" 2>/dev/null; }

# How many other smoke runs are alive: their markers, and any Ren'Py started
# from a scratch copy by a smoke.sh older than the lock.
others_running() {
    local f p n=0
    for f in "$RUNNING"/*; do
        [ -f "$f" ] || continue
        p="$(basename "$f")"
        [ "$p" = "$$" ] && continue
        if kill -0 "$p" 2>/dev/null; then n=$((n + 1)); else rm -f "${f:?}"; fi
    done
    p="$(ps -axo pid=,command= 2>/dev/null | grep 'jjk_smoke\.' | grep -v grep | grep -v "$SCRATCH_MARK" | grep -c .)"
    echo $((n + ${p:-0}))
}

lock_release() {
    [ -n "$MARKER" ] && rm -f "${MARKER:?}"
    if [ "$HAVE_LOCK" = "1" ] && [ "$(lock_holder)" = "$$" ]; then
        rm -f "${LOCK:?}/pid" "${LOCK:?}/what"
        rmdir "${LOCK:?}" 2>/dev/null
    fi
    HAVE_LOCK=0
}

lock_refuse() {
    # One line, a result file that says so, and exit status 3.
    echo "smoke.sh: REFUSED: $*" >&2
    { echo "FAIL smoke: REFUSED: $*"; echo "RESULT FAIL"; } > "$RESULT"
    lock_release
    exit 3
}

# Take over a lock whose holder has died. Only one waiter wins the rename.
lock_clear_stale() {
    local dead stale="$LOCK.stale.$$"
    [ -d "$LOCK" ] || return 0
    dead="$(lock_holder)"
    if [ -n "$dead" ] && kill -0 "$dead" 2>/dev/null; then return 0; fi
    # A lock just made has no pid file for a moment: leave it be.
    if [ -z "$dead" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mtime -5s 2>/dev/null)" ]; then return 0; fi
    mv "$LOCK" "$stale" 2>/dev/null || return 0
    if [ "$(cat "$stale/pid" 2>/dev/null)" != "$dead" ]; then
        mv "$stale" "$LOCK" 2>/dev/null     # someone's new lock: put it back
    else
        rm -f "${stale:?}/pid" "${stale:?}/what"
        rmdir "${stale:?}" 2>/dev/null
    fi
}

lock_wait_start=$SECONDS
lock_timed_out() { [ $((SECONDS - lock_wait_start)) -ge "$LOCK_WAIT" ]; }

mkdir -p "$RUNNING" || die "cannot create $RUNNING"
trap lock_release EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP
if [ "$POINTER" = "1" ]; then
    [ -n "$(open_games)" ] && lock_refuse "$NAME needs the pointer and a Ren'Py game is open ($(games_line)). Close it and run this again."
    said=0
    while ! mkdir "$LOCK" 2>/dev/null; do
        lock_clear_stale
        if [ "$said" = "0" ] && [ -d "$LOCK" ]; then
            echo "smoke.sh: $NAME waits for the pointer (held by pid $(lock_holder): $(lock_what))" >&2
            said=1
        fi
        lock_timed_out && lock_refuse "$NAME waited ${LOCK_WAIT}s for the pointer lock $LOCK (held by pid $(lock_holder): $(lock_what))"
        sleep 2
    done
    echo "$$" > "$LOCK/pid"
    echo "$NAME from $ROOT" > "$LOCK/what"
    HAVE_LOCK=1
    said=0
    while [ "$(others_running)" != "0" ]; do
        if [ "$said" = "0" ]; then
            echo "smoke.sh: $NAME has the pointer and waits for the other smoke runs to finish" >&2
            said=1
        fi
        lock_timed_out && lock_refuse "$NAME waited ${LOCK_WAIT}s for the other smoke runs to finish"
        sleep 2
    done
    [ -n "$(open_games)" ] && lock_refuse "$NAME needs the pointer and a Ren'Py game is open ($(games_line)). Close it and run this again."
else
    MARKER="$RUNNING/$$"
    said=0
    while :; do
        echo "$NAME from $ROOT" > "$MARKER"
        lock_clear_stale
        [ -d "$LOCK" ] || break
        rm -f "${MARKER:?}"
        if [ "$said" = "0" ]; then
            echo "smoke.sh: $NAME waits: a pointer harness is running (pid $(lock_holder): $(lock_what))" >&2
            said=1
        fi
        lock_timed_out && lock_refuse "$NAME waited ${LOCK_WAIT}s for the pointer harness to finish (pid $(lock_holder): $(lock_what))"
        sleep 2
    done
fi

# --- the scratch copy ----------------------------------------------------------
TMPBASE="${TMPDIR:-/tmp}"
TMPBASE="${TMPBASE%/}"
SCRATCH="$(mktemp -d "$TMPBASE/jjk_smoke.XXXX")" || die "mktemp failed in $TMPBASE"
SCRATCH_MARK="$(basename "$SCRATCH")"
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
    lock_release
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
            # -L: a link (the folder itself, or one inside it) is followed and
            # its contents copied, never the link.
            cp -RpL "$f" "$G/$b"
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
# -L: when game/cache is a link (a worktree or a scratch root that borrows
# another tree's cache), its contents are copied. Copying the link itself
# would let Ren'Py write its caches through it into that other tree.
[ -d "$ROOT/game/cache" ] && cp -RpL "$ROOT/game/cache" "$G/cache"
[ -L "$G/cache" ] && die "the scratch game/cache is a link; refusing to run"

cp "$LIB" "$G/zz_smoke_lib.rpy"
cp "$HARNESS" "$G/zz_smoke.rpy"

# Extra scripts the harness asks for: `## smoke-with: <file>.rpy` installs
# tools/smoke/<file>.rpy under its own name.
sed -n 's/^## smoke-with: *\([A-Za-z0-9_][A-Za-z0-9_.-]*\.rpy\) *$/\1/p' "$HARNESS" | while IFS= read -r extra; do
    [ -f "$ROOT/tools/smoke/$extra" ] || { echo "smoke.sh: smoke-with: no tools/smoke/$extra" >&2; exit 2; }
    cp "$ROOT/tools/smoke/$extra" "$G/$extra"
done || exit 2

# --- the asset overlay (D49) ---------------------------------------------------
SCRATCH_REAL="$(cd "$SCRATCH" && pwd -P)"

# Make every folder on the way to game/<$1> a real folder inside the scratch
# copy. A folder that is a link into the real tree is replaced by a real one
# holding links to the original's children.
real_dirs() {
    local rest="$1" cur="$G" part target child
    while [ -n "$rest" ]; do
        part="${rest%%/*}"
        if [ "$part" = "$rest" ]; then rest=""; else rest="${rest#*/}"; fi
        [ -n "$part" ] || continue
        cur="$cur/$part"
        if [ -L "$cur" ]; then
            target="$(cd "$cur" 2>/dev/null && pwd -P)" || die "overlay: $cur is a link to something that is not a folder"
            rm "$cur" && mkdir "$cur" || die "overlay: cannot make $cur a real folder"
            for child in "$target"/* "$target"/.[!.]*; do
                [ -e "$child" ] || [ -L "$child" ] || continue
                ln -s "$child" "$cur/$(basename "$child")"
            done
        elif [ -d "$cur" ]; then
            :
        elif [ -e "$cur" ]; then
            die "overlay: $cur is a file, not a folder"
        else
            mkdir "$cur" || die "overlay: cannot create $cur"
        fi
    done
}

ASSETS="${SMOKE_ASSETS:-$ROOT/tools/smoke/assets/$NAME}"
if [ -d "$ASSETS" ]; then
    find "$ASSETS" -type f ! -name '.DS_Store' -print | LC_ALL=C sort > "$SCRATCH/overlay.txt"
    while IFS= read -r src; do
        rel="${src#"$ASSETS"/}"
        case "$rel" in
            game/*) rel="${rel#game/}" ;;
            *) die "overlay: $src is not under $ASSETS/game/ (only game/ is overlaid)" ;;
        esac
        case "/$rel/" in */../*) die "overlay: bad path $rel" ;; esac
        dir="$(dirname "$rel")"
        [ "$dir" = "." ] || real_dirs "$dir"
        dest="$G/$rel"
        # The folder the file goes into must now be real and inside the scratch copy.
        destdir="$(cd "$(dirname "$dest")" && pwd -P)"
        case "$destdir/" in "$SCRATCH_REAL"/*) ;; *) die "overlay: $dest would be written outside the scratch copy" ;; esac
        # A link (to the owner's file) is removed, never written through.
        if [ -L "$dest" ]; then rm "$dest" || die "overlay: cannot remove the link $dest"; fi
        [ -d "$dest" ] && die "overlay: $dest is a folder"
        cp -p "$src" "$dest" || die "overlay: cannot copy $src"
    done < "$SCRATCH/overlay.txt"
fi

# The owner's saves, as read-only copies (SMOKE_SAVES=1).
if [ "${SMOKE_SAVES:-0}" = "1" ]; then
    SAVE_DIRNAME="$(sed -n 's/^define config.save_directory *= *"\(.*\)".*/\1/p' "$ROOT/game/options.rpy" | head -n 1)"
    USER_SAVES="$HOME/Library/RenPy/${SAVE_DIRNAME:-JJKgamemd-1788928056}"
    if [ -n "${SMOKE_SAVES_FROM:-}" ]; then
        # A snapshot instead of the owner's folders (docs/UI2_DESIGN.md, D42).
        OLDIFS="$IFS"; IFS=":"
        for d in $SMOKE_SAVES_FROM; do
            [ -d "$d" ] || die "SMOKE_SAVES_FROM: no folder $d"
            for f in "$d"/*.save; do
                [ -f "$f" ] && cp -p "$f" "$SCRATCH/savedir/"
            done
        done
        IFS="$OLDIFS"
    else
        for f in "$ROOT"/game/saves/*.save; do
            [ -f "$f" ] && cp -p "$f" "$G/saves/"
        done
        for f in "$USER_SAVES"/*.save; do
            [ -f "$f" ] && cp -p "$f" "$SCRATCH/savedir/"
        done
    fi
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
export SMOKE_ROOT="$ROOT"
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
if [ "$(last_line)" != "RESULT PASS" ]; then exit 1; fi
if [ -n "$OUT_DEST" ]; then
    if [ ! -f "$SHOTS/$OUT_NAME" ]; then
        echo "smoke.sh: $NAME passed but wrote no $OUT_NAME" >&2
        exit 1
    fi
    cp "$SHOTS/$OUT_NAME" "$OUT_DEST.tmp" && mv "$OUT_DEST.tmp" "$OUT_DEST" || die "cannot write $OUT_DEST"
    echo "smoke.sh: wrote $OUT_DEST"
fi
exit 0
