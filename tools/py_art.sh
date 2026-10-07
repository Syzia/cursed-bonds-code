#!/bin/bash
# tools/py_art.sh -- start an art tool with the Python that has numpy, scipy
# and Pillow (docs/UI2_DESIGN.md K14).
#
#   tools/py_art.sh tools/campus_plan.py            run a tool
#   tools/py_art.sh --where                         print which Python it would use
#
# The system python3 has none of the three. ComfyUI's own Python has all of
# them, so every tool of the second UI overhaul that needs one starts through
# this file (campus_plan.py when it draws, install_redo.py, sample_light.py);
# a tool started with plain python3 starts itself again through it.
#
# When that Python is not on the machine it prints ONE line and exits with
# status 69, and nothing else happens. A harness that needed the tool then
# prints "SKIPPED (no ComfyUI python)": a pass for a code package, a failure
# for an art sitting.
#
# JJK_ART_PYTHON names another Python, if ComfyUI is installed somewhere else.
PY="${JJK_ART_PYTHON:-$HOME/ComfyUI-Installs/ComfyUI/standalone-env/bin/python}"
if [ ! -x "$PY" ]; then
    echo "py_art.sh: no ComfyUI python at $PY (the art tools that need numpy or Pillow cannot run here)"
    exit 69
fi
if [ "${1:-}" = "--where" ]; then
    echo "$PY"
    exit 0
fi
if [ $# -eq 0 ]; then
    echo "py_art.sh: name the tool to run: tools/py_art.sh tools/<tool>.py [its options]"
    exit 2
fi
JJK_PY_ART=1 exec "$PY" "$@"
