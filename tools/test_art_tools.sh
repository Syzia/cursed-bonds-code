#!/bin/bash
# tools/test_art_tools.sh -- the tests of the art tools (docs/UI2_DESIGN.md 5.4, 6.5).
#
#   tools/test_art_tools.sh                        everything that can run on this machine
#   tools/test_art_tools.sh --layout-dump <file>   in a worktree: the local dump
#                                                  (tools/smoke.sh u2_dump --out <file>)
#   tools/test_art_tools.sh --only redo,pose       some groups: reader layout redo stage compose pose face set
#                                                  status real yuji
#   tools/test_art_tools.sh --strict               an art sitting: a SKIPPED line is a failure
#   tools/test_art_tools.sh --keep-work            keep the scratch folder
#
# It runs the SYNTHETIC cases anywhere the repository is, and the REAL ones
# (the sixteen look-test renders, Yuji's staged set) when their files are on
# the machine; it prints which it skipped. Each line is PASS, FAIL or SKIPPED,
# and the last line is RESULT PASS or RESULT FAIL. Nothing touches the game:
# every install goes into a scratch copy, and the last check is that no file
# under game/ changed. No Ren'Py is started. About ten minutes in full.
# The scratch copy is the tree as it was before the overhaul installed any
# picture (what an install wrote is put back from git), so the suite reads
# the same before and after batch 0; it needs a git checkout once a picture
# is installed, and will not run where game/images is a symbolic link.
#
# Exit status 0 when nothing failed, 1 otherwise, 2 when the layout dump is
# out of date ("run tools/smoke.sh u2_dump").
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/test_art_tools.py" "$@"
