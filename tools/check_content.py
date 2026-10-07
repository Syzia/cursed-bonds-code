#!/usr/bin/env python3
"""Static content checks (docs/PHASE1_DESIGN.md 8.4; docs/PHASE2_DESIGN.md 2.2).

    python3 tools/check_content.py [--all | RULE FLAGS ...] [FILES ...]

Prints one line per finding, `file:line: rule: text`, and exits 1 if there
are any (0 when clean, 2 on a usage error). A count per rule goes to stderr.

Rules (flags):
  --no-mc-on-screen   `show mc` / `hide mc` lines. Allowed on a line tagged
                      `## first-person exception`.
  --one-technique     Filament, Emberfall, Aftersound or Stillness, in any
                      case, anywhere on the line. Allowed on a line tagged
                      `# legacy-technique`.
  --no-deadline       KYOTO_DAY, days_left(, "days until Kyoto", "TO KYOTO",
                      "Three weeks from today", "In three weeks", `arc = 2`,
                      "END OF ARC ONE".
  --narration-person  Narrator lines (a line inside a label that is just a
                      string, not a menu choice ending in `:`) that say you,
                      your, yours or yourself outside {i}...{/i}. Allowed on a
                      line tagged `## you-ok`.
                      Exempt: the later chapters that section 5.4 keeps in
                      "you" until phase 4 converts them (the PHASE4_YOU table
                      below: files, and the labels in them). Their findings
                      are counted, not listed, and one note line on stderr
                      gives the count. This rule only; every other rule still
                      checks those files.
  --include-phase4    List the PHASE4_YOU findings as well (they then count
                      as findings and make the exit code 1).
  --no-literal-name   "Kaito" or "Amagiri" inside a string literal (D29).
                      Allowed: `default` lines in jjk_defs.rpy, `label start`
                      in script.rpy, and the renpy.input defaults (a line that
                      calls renpy.input, or assigns mc_name / mc_surname, like
                      the fallback `mc_name = _n if _n else "Kaito"`).
  --dup-labels        A label defined twice. Every .rpy under game/ is read;
                      each definition in FILES is reported when game/ defines
                      the same label elsewhere. (Files outside game/, such as
                      smoke harnesses, are compared with game/ only, not with
                      each other: they are installed one at a time.)
  --dup-globals       A top-level name defined twice (phase 2, R2). Read from
                      every .rpy under game/: `NAME =`, `def` and `class`
                      at the top level of an `init ... python:` block (under
                      its own `if`, `for`, `try` ... too; a header may span
                      several lines; every target of `a = b = 1` and
                      `(a, b) = ...`, `store.NAME =`, `import x as NAME`,
                      `from x import y as NAME` and `with ... as NAME:`
                      count, in every statement of `a = 1; b = 2`; a
                      plain `import x` does not, nor does `except ... as
                      NAME:`, which Python unbinds again), and every
                      `define`, `default`, `screen`, `style`, `transform`,
                      `image` and `label`. Store names (python names, define,
                      default, transform), screens, styles, images and labels
                      are five separate namespaces. A style is a finding only
                      when two files define it (`style x is y`, then
                      `style x:`, in one file is the usual way to write one).
                      A harness (a file outside
                      game/) is compared with game/, with tools/smoke/_lib.rpy
                      and with itself, never with another harness.
  --prefixes          A game name that is not in the baseline of today's names
                      (tools/smoke/baseline_globals.txt) must start with one
                      of its file's prefixes in tools/prefixes.json, or be on
                      that file's exception list (R1). A file with no row may
                      gain no new name. `$ x = ...` temporaries in labels are
                      checked too, unless x is a store variable some file
                      defines.
  --harness-names     Every top-level name in tools/smoke/*.rpy starts with
                      zz / ZZ (the names phase 1 left are in the baseline).
                      When no harness is among FILES, tools/smoke/ is read.
  --art-names         Two files under game/images/ with one base name (Ren'Py
                      names an image after it, whatever the folder).
  --action-returns    Every `Function(` inside a `screen` block or a `def`
                      body in a game file must be `Function(ui_do, ...)` or
                      name a function listed in tools/none_ok.txt (R4): a
                      button's function that returns anything but None ends
                      the interaction. A name on the line after `Function(`
                      is read as well, and so are `store.Function(` and
                      `renpy.store.Function(`. `Function` handed on without
                      a call (`F = Function`) is a finding anywhere in a
                      game file: what F( ... ) runs could not be read.
  --icon-names        The literal first argument of `icon("...")` and
                      `icon_btn("...")` (as `use icon_btn(` too, and written
                      `name="..."`) in a game file must be a key of ICONS in
                      game/ui_icons.rpy. Lint cannot see this: an unknown
                      name draws a question mark in the game. An argument
                      that is not one plain string (`icon(_s["icon"])`,
                      `icon("area_" + _k)`) is not read; icon_validate()
                      checks the data tables at start-up.
  --layout-files      (UI overhaul 2, 3.2) Every game/layout/*.json: a known
                      file name (hot_<place>, view_<place>, pose_<place>,
                      light_<place>, area_<key>, light, map_campus, faces,
                      pictures), only that kind's keys, and each key's shape.
                      `for_rev` in a hot_ or view_ file is a finding unless
                      pictures.json calls that place's picture "composed".
                      --layout-dir <dir> reads another folder.
  --decency           (K16) A word list (towel, naked, undress, strip,
                      swimsuit, bikini, skin, bare, changing) over the text of
                      room_bath.rpy, room_pool.rpy and room_tokyo.rpy, and over
                      every AMBIENT, SPOT_LINES and POSES row whose place is
                      the Bathhouse, the Sauna, the Pool or a friend's room.
  --baths-optional    (K17) `"bath"`, bath_soak, bath_sauna, bath_ok or
                      pool_swim in a game file other than room_bath.rpy and
                      room_pool.rpy. Allowed only: a row of ICONS or ICON_FOR
                      in ui_icons.rpy, a row of SPOT_PLANNED in
                      sb_hotspots.rpy, a register_hotspot row, and the tuple
                      NIGHT_REST_BLOCKS in sb_night.rpy.
  --later-notes       (8.3) "later build" and "combat update" in text a player
                      can read (string literals; not comments or docstrings),
                      less the rows of tools/later_ok.txt. NOT part of --all:
                      it is a report (exit 0) until integration; with
                      --strict its lines are findings.
  --all               Every rule but --later-notes. This is also the default
                      when no rule flag is given.
  --no-baseline       List the findings tools/smoke/baseline_check_content.txt
                      already records as well. By default a finding whose
                      file, rule and text are in that file is counted on
                      stderr, not listed (line numbers are not compared).
  --write-baseline    Write tools/smoke/baseline_globals.txt and
                      tools/smoke/baseline_check_content.txt from the tree as
                      it stands (game/ and tools/smoke/). P0a ran this once,
                      before phase 2 changed a game file; the two files are
                      frozen after that, so the flag alone writes nothing: it
                      lists the rows the names baseline would gain and lose
                      and exits 2. Only with --i-am-p0a-or-p8 as well are the
                      two files replaced (P8, at the end of the phase).

FILES are .rpy files or folders (searched for .rpy). With none, every .rpy
under game/ is checked.

Examples:
    python3 tools/check_content.py --all game/*.rpy
    python3 tools/check_content.py --narration-person --include-phase4 game/story_arc1.rpy
    python3 tools/check_content.py --no-literal-name game/sb_board.rpy
    python3 tools/check_content.py --all game/*.rpy tools/smoke/*.rpy
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")
SMOKE = os.path.join(ROOT, "tools", "smoke")
BASELINE_FINDINGS = os.path.join(SMOKE, "baseline_check_content.txt")
BASELINE_GLOBALS = os.path.join(SMOKE, "baseline_globals.txt")
PREFIXES = os.path.join(ROOT, "tools", "prefixes.json")
NONE_OK = os.path.join(ROOT, "tools", "none_ok.txt")

RULES = [
    "no-mc-on-screen",
    "one-technique",
    "no-deadline",
    "narration-person",
    "no-literal-name",
    "dup-labels",
    "dup-globals",
    "prefixes",
    "harness-names",
    "art-names",
    "action-returns",
    "icon-names",
    "layout-files",
    "decency",
    "baths-optional",
]
# Asked for by name only (UI overhaul 2, 8.3): a report until integration.
REPORT_RULES = ["later-notes"]
LATER_OK = os.path.join(ROOT, "tools", "later_ok.txt")
LAYOUT = os.path.join(GAME, "layout")

MC_ON_SCREEN = re.compile(r"^\s*(show|hide)\s+mc\b")
TECHNIQUE = re.compile(r"filament|emberfall|aftersound|stillness", re.IGNORECASE)
DEADLINE = re.compile(
    r"KYOTO_DAY|days_left\(|days until Kyoto|TO KYOTO|Three weeks from today"
    r"|In three weeks|\barc\s*=\s*2\b|END OF ARC ONE"
)
YOU = re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE)
ITALIC = re.compile(r"\{i\}.*?(\{/i\}|$)")
LITERAL_NAME = re.compile(r"Kaito|Amagiri")
NAME_ASSIGN = re.compile(r"\bmc_(sur)?name\s*=(?!=)")
LABEL_DEF = re.compile(r"^\s*label\s+([A-Za-z_.][\w.]*)")
PYTHON_HEADER = re.compile(r"^(init(\s+[-+]?\d+)?\s+)?python\b(.*)$")
ICON_CALL = re.compile(r"(?<![\w.])icon(?:_btn)?\(")
# One whole string and then the end of the argument: `"area_" + k` is not read.
ICON_LITERAL = re.compile(r"""\s*(?:name\s*=\s*)?(["'])([^"'\\]*)\1\s*(?=[,)])""")
ICONS_OPEN = re.compile(r"^\s*ICONS\s*=\s*\{\s*$")
ICONS_ROW = re.compile(r"""^\s*["'](\w+)["']\s*:\s*\(""")
# The narrator's string may be followed by say arguments or a transition.
SAY_TAIL = re.compile(r"^(with\b|\(|id\b|nointeract\b)")

# Section 5.4 of docs/PHASE1_DESIGN.md: "Narration stays you" in the later
# chapters, except st_roll_call (D9). Phase 4 converts them in D9's order and
# removes each entry here as its chapter turns into "I". Keyed by file name;
# the value holds the exempt labels, "*" for every label in the file, and
# "-<label>" for a label that is NOT exempt (already first person).
# Only --narration-person reads this table.
PHASE4_YOU = {
    "events_arc1.rpy":       {"*"},
    "ch4_mission.rpy":       {"*"},
    "story_arc1.rpy":        {"*", "-st_roll_call"},
    "events_intimate.rpy":   {"*"},
    "events_romance.rpy":    {"*"},
    "story_oda.rpy":         {"*"},
    "missions_arc1.rpy":     {"*"},
    "events_stand.rpy":      {"*"},
    "story_kurose.rpy":      {"*"},
    "ch5_debrief.rpy":       {"*"},
    # WP7 converted the other activity scenes; confiding is a phase 4 scene.
    "events_activities.rpy": {"act_confide"},
}


def phase4_exempt(path, label):
    """True when a narration-person finding in `label` of `path` is one that
    section 5.4 keeps in "you" for now."""
    rules = PHASE4_YOU.get(os.path.basename(path))
    if not rules or label is None:
        return False
    top = label.split(".")[0]
    if "-" + top in rules:
        return False
    return "*" in rules or top in rules


# Blocks whose bare strings are not narration.
NON_SCRIPT_BLOCKS = {"python", "screen", "transform", "image", "style",
                     "layeredimage", "init", "define", "default", "testcase"}


class Line(object):
    """One physical line, as the scanner saw it."""

    __slots__ = ("n", "raw", "code", "strings", "first_string", "rest",
                 "continuation", "blocks", "bare")

    def __init__(self, n, raw):
        self.n = n
        self.raw = raw
        self.code = raw          # the line up to a comment
        self.strings = []        # string literal contents (fragments too)
        self.first_string = None  # (start, end) of a string opening the line
        self.rest = ""           # code after that first string
        self.continuation = False  # inside brackets or a string from above
        self.blocks = ()         # enclosing blocks, outermost first: (kind, name)
        self.bare = raw          # the code with every string literal blanked


def scan(text):
    """Split a .rpy file into Line records: comments stripped, string literals
    collected, bracket and string continuations flagged, and each line's
    enclosing blocks (label, menu, python, screen, ...) worked out from
    indentation."""
    lines = []
    open_quote = None   # '"', "'", '\"\"\"' or "'''" carried from the line above
    depth = 0
    stack = []          # [(indent, kind, name)]
    pending = None      # (indent, code) of a statement still open in brackets
    for n, raw in enumerate(text.splitlines(), 1):
        ln = Line(n, raw)
        ln.continuation = bool(open_quote) or depth > 0
        i = 0
        L = len(raw)
        comment_at = None
        spans = []          # (start, end) of the string literals on this line
        if open_quote:
            end = raw.find(open_quote)
            while end > 0 and raw[end - 1] == "\\" and len(open_quote) == 1:
                end = raw.find(open_quote, end + 1)
            if end < 0:
                ln.strings.append(raw)
                spans.append((0, L))
                i = L
            else:
                ln.strings.append(raw[:end])
                i = end + len(open_quote)
                spans.append((0, i))
                open_quote = None
        while i < L:
            c = raw[i]
            if c == "#":
                comment_at = i
                break
            if c in "\"'":
                q = raw[i:i + 3] if raw[i:i + 3] in ('"""', "'''") else c
                j = i + len(q)
                while j < L:
                    if raw[j] == "\\":
                        j += 2
                        continue
                    if raw.startswith(q, j):
                        break
                    j += 1
                if j >= L:
                    ln.strings.append(raw[i + len(q):])
                    spans.append((i, L))
                    open_quote = q
                    i = L
                    break
                ln.strings.append(raw[i + len(q):j])
                spans.append((i, j + len(q)))
                if ln.first_string is None and not raw[:i].strip():
                    ln.first_string = (i, j + len(q))
                i = j + len(q)
                continue
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth = max(0, depth - 1)
            i += 1
        if comment_at is not None:
            ln.code = raw[:comment_at]
        bare = list(ln.code)
        for a, b in spans:
            for k in range(a, min(b, len(bare))):
                bare[k] = " "
        ln.bare = "".join(bare)
        if ln.first_string is not None:
            ln.rest = ln.code[ln.first_string[1]:].strip()

        stripped = ln.code.strip()
        if stripped and not ln.continuation:
            indent = len(raw) - len(raw.lstrip())
            while stack and stack[-1][0] >= indent:
                stack.pop()
            ln.blocks = tuple((k, nm) for _, k, nm in stack)
            if stripped.endswith(":") and depth == 0 and not open_quote:
                stack.append((indent,) + block_kind(stripped))
            # A header spread over several lines (`def f(a,` / `b):`) opens
            # its block on the line that closes the brackets.
            pending = (indent, stripped) if (depth > 0 or open_quote) else None
        else:
            ln.blocks = tuple((k, nm) for _, k, nm in stack)
            if pending is not None and depth == 0 and not open_quote:
                if stripped.endswith(":"):
                    stack.append((pending[0],) + block_kind(pending[1]))
                pending = None
        lines.append(ln)
    return lines


def block_kind(stripped):
    """(kind, name) of a block header such as `label start:` or `menu:`."""
    m = PYTHON_HEADER.match(stripped)
    if m:
        # The name says which store the block fills: "" for the default one,
        # the name after `in`, or "-" for `hide` (its names are thrown away).
        tail = m.group(3)
        if re.search(r"\bhide\b", tail):
            return ("python", "-")
        st = re.search(r"\bin\s+([A-Za-z_][\w.]*)", tail)
        return ("python", st.group(1) if st else "")
    if stripped.startswith(('"', "'")):
        return ("choice", "")
    m = re.match(r"([A-Za-z_]\w*)\s*([A-Za-z_.][\w.]*)?", stripped)
    if not m:
        return ("other", "")
    return (m.group(1), m.group(2) or "")


def in_kind(ln, kinds):
    return any(k in kinds for k, _ in ln.blocks)


def label_of(ln):
    """The innermost label enclosing a line, or None."""
    for k, nm in reversed(ln.blocks):
        if k == "label":
            return nm
    return None


# --- rules ---------------------------------------------------------------------

def rule_mc(path, lines):
    for ln in lines:
        if ln.continuation:
            continue
        if MC_ON_SCREEN.match(ln.raw) and "## first-person exception" not in ln.raw:
            yield ln


def rule_technique(path, lines):
    for ln in lines:
        if TECHNIQUE.search(ln.raw) and "# legacy-technique" not in ln.raw:
            yield ln


def rule_deadline(path, lines):
    for ln in lines:
        if DEADLINE.search(ln.raw):
            yield ln


def rule_narration(path, lines):
    for ln in lines:
        if ln.continuation or ln.first_string is None or "## you-ok" in ln.raw:
            continue
        if label_of(ln) is None or in_kind(ln, NON_SCRIPT_BLOCKS):
            continue
        rest = ln.rest
        if rest.endswith(":") or (rest and not SAY_TAIL.match(rest)):
            continue
        text = ln.strings[0]
        if YOU.search(ITALIC.sub("", text)):
            yield ln


def rule_literal_name(path, lines):
    base = os.path.basename(path)
    for ln in lines:
        if not any(LITERAL_NAME.search(s) for s in ln.strings):
            continue
        code = ln.code.strip()
        if base == "jjk_defs.rpy" and code.startswith("default "):
            continue
        if base == "script.rpy" and label_of(ln) == "start":
            continue
        if "renpy.input(" in ln.code or NAME_ASSIGN.search(ln.code):
            continue
        yield ln


def label_defs(path, lines):
    """[(name, line)] for every label a file defines; local labels qualified."""
    out = []
    current = None
    for ln in lines:
        # A screen's `label "Text"` is a widget, not a script label.
        if ln.continuation or in_kind(ln, NON_SCRIPT_BLOCKS):
            continue
        m = LABEL_DEF.match(ln.code)
        if not m or not ln.code.rstrip().endswith(":"):
            continue
        name = m.group(1)
        if name.startswith("."):
            name = (current or "") + name
        elif "." not in name:
            current = name
        out.append((name, ln))
    return out


# --- phase 2: names (R1, R2) ----------------------------------------------------

DEFINE_DEF = re.compile(r"^(define|default)\s+(?:[-+]?\d+\s+)?([A-Za-z_][\w.]*)\s*=(?!=)")
SCREEN_DEF = re.compile(r"^screen\s+([A-Za-z_]\w*)")
STYLE_DEF = re.compile(r"^style\s+([A-Za-z_]\w*)")
TRANSFORM_DEF = re.compile(r"^transform\s+([A-Za-z_]\w*)")
IMAGE_DEF = re.compile(r"^(?:image|layeredimage)\s+([^=:]+?)\s*[=:]")
PY_DEF = re.compile(r"^(?:def|class)\s+([A-Za-z_]\w*)")
PY_ASSIGN = re.compile(r"^([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*(?::[^=]+)?=(?!=)")
PY_FOR = re.compile(r"^for\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s+in\b")
DOLLAR_ASSIGN = re.compile(r"^\$\s*([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*=(?!=)")
# Python blocks that do not make a new scope.
PY_TRANSPARENT = {"if", "elif", "else", "try", "except", "finally", "with", "for", "while"}
PY_NAME = re.compile(r"^[A-Za-z_]\w*$")
PY_STORE_ATTR = re.compile(r"^(?:renpy\.)?store\.([A-Za-z_]\w*)$")
PY_AS = re.compile(r"\bas\s+([A-Za-z_]\w*)")
# `Function(` (or `Function (`), also written `store.Function(` or
# `renpy.store.Function(`;
# never another object's method (`x.Function(`).
FUNCTION_CALL = re.compile(r"(?<![\w.])(?:renpy\.store\.|store\.)?Function\s*\(")
# `Function` with no call after it: handed on under another name.
FUNCTION_ALIAS = re.compile(r"(?<![\w.])(?:renpy\.store\.|store\.)?Function\b(?!\s*\()")

# Variables Ren'Py itself owns; a label may set them without owning the name.
RENPY_VARS = {
    "_return", "_window", "_skipping", "_rollback", "_dismiss_pause", "_game_menu_screen",
    "_confirm_quit", "_autosave", "_history", "_window_auto", "_side_image", "_quit_slot",
    "quick_menu", "save_name", "mouse_visible", "suppress_overlay", "main_menu",
}


def file_key(path):
    """A file's name as the baselines and tools/prefixes.json write it:
    `game/x.rpy`, `tools/smoke/x.rpy`. A copy outside the repository (a
    scratch project, a worktree with its own tools/) keeps the same key."""
    real = os.path.realpath(path)
    root = os.path.realpath(ROOT)
    if real.startswith(root + os.sep):
        return os.path.relpath(real, root).replace(os.sep, "/")
    parent = os.path.basename(os.path.dirname(real))
    if parent == "game":
        return "game/" + os.path.basename(real)
    if parent == "smoke":
        return "tools/smoke/" + os.path.basename(real)
    return real.replace(os.sep, "/")


def is_game(path):
    return file_key(path).startswith("game/")


def py_statements(bare):
    """One line of python cut at every `;` outside brackets (`a = 1; b = 2`).
    `bare` has its string literals blanked, so a `;` in a string is no cut."""
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(bare):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            parts.append(bare[start:i])
            start = i + 1
    parts.append(bare[start:])
    return [p for p in parts if p.strip()]


def py_bound_names(bare):
    """The names a line of python binds at its own level, read from its
    first line with the string literals blanked out; every statement of
    `a = 1; b = 2` is read."""
    out = []
    for part in py_statements(bare):
        out.extend(py_bound_names_one(part))
    return out


def py_bound_names_one(bare):
    """The names one python statement binds at its own level: `import x as
    NAME`, `from x import y as NAME`, `with ... as NAME:`, `for NAME in`, and
    every target of an assignment (`a = b = 1`, `(a, b) = ...`, `a: int = 1`,
    `store.a = 1`). A plain `import x` binds a module's own name and is left
    alone; so is an augmented assignment, which defines nothing new; so is
    `except ... as NAME:`, because Python unbinds that name when the block
    ends, so it never stays in the store."""
    code = bare.strip()
    if re.match(r"^import\s", code) or re.match(r"^from\s+[\w.]+\s+import\b", code):
        return PY_AS.findall(code)
    if re.match(r"^with\b", code):
        return PY_AS.findall(code)
    m = PY_FOR.match(code)
    if m:
        return [n.strip() for n in m.group(1).split(",")]
    if re.match(r"^(?:if|elif|else|while|try|except|finally|def|class|return|yield|assert|del|raise|"
                r"global|nonlocal|pass|lambda|print)\b", code):
        return []
    # Cut the line at every `=` outside brackets that is an assignment.
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(code):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "=" and depth == 0:
            before = code[i - 1] if i else ""
            after = code[i + 1] if i + 1 < len(code) else ""
            if after == "=" or before == "=":
                continue            # ==
            if before in "<>!":
                continue            # <=, >=, !=
            if before in "+-*/%&|^@:~":
                return []           # augmented, or a walrus
            parts.append(code[start:i])
            start = i + 1
    out = []
    for target in parts:
        target = target.strip()
        # An annotation: `name: type`.
        d = 0
        for i, ch in enumerate(target):
            if ch in "([{":
                d += 1
            elif ch in ")]}":
                d -= 1
            elif ch == ":" and d == 0:
                target = target[:i].strip()
                break
        if len(target) > 1 and target[0] + target[-1] in ("()", "[]"):
            target = target[1:-1]
        for name in target.split(","):
            name = name.strip().lstrip("*").strip()
            if PY_NAME.match(name):
                out.append(name)
            else:
                m = PY_STORE_ATTR.match(name)
                if m:
                    out.append(m.group(1))
    return out


def top_level(ln):
    """True for a statement at the top of a file or directly inside `init:`."""
    return all(k == "init" for k, _ in ln.blocks)


def definitions(path, lines):
    """[(namespace, name, Line)] for every top-level name a file defines.
    Namespaces: store (python names, define, default, transform), screen,
    style, image, label."""
    out = []
    for ln in lines:
        if ln.continuation:
            continue
        code = ln.code.strip()
        if not code:
            continue
        if top_level(ln):
            m = DEFINE_DEF.match(code)
            if m:
                out.append(("store", m.group(2), ln))
                continue
            for ns, rx in (("screen", SCREEN_DEF), ("style", STYLE_DEF),
                           ("store", TRANSFORM_DEF), ("image", IMAGE_DEF)):
                m = rx.match(code)
                if m:
                    out.append((ns, " ".join(m.group(1).split()), ln))
                    break
            continue
        # Python's own `if`, `try`, `for` ... at the top of an init python
        # block define top-level names too; a def or a class does not.
        blocks = list(ln.blocks)
        while blocks and blocks[-1][0] in PY_TRANSPARENT:
            blocks.pop()
        if not blocks:
            continue
        kind, store = blocks[-1]
        if kind == "python" and store != "-" and all(k == "init" for k, _ in blocks[:-1]):
            # At the top level of an init python block (not in a def or class).
            pre = (store + ".") if store else ""
            m = PY_DEF.match(code)
            if m:
                out.append(("store", pre + m.group(1), ln))
                continue
            for name in py_bound_names(ln.bare):
                out.append(("store", pre + name, ln))
    for name, ln in label_defs(path, lines):
        out.append(("label", name, ln))
    out.sort(key=lambda d: d[2].n)
    return out


def label_temporaries(path, lines):
    """[(name, Line)] for every plain `$ name = ...` (and `name = ...` in a
    python block) inside a label."""
    out = []
    for ln in lines:
        if ln.continuation or label_of(ln) is None:
            continue
        kinds = [k for k, _ in ln.blocks]
        code = ln.code.strip()
        if any(k in NON_SCRIPT_BLOCKS and k != "python" for k in kinds):
            continue
        if "python" in kinds:
            if kinds[-1] != "python":
                continue
            m = PY_ASSIGN.match(code)
        else:
            m = DOLLAR_ASSIGN.match(code)
        if m:
            for name in m.group(1).split(","):
                out.append((name.strip(), ln))
    return out


class Baseline(object):
    """tools/smoke/baseline_globals.txt: the names the tree had when the
    baseline was last written (before phase 2 at P0a; again at the end of it).
    Tab-separated rows, `kind  namespace  name  file`:
      def  a top-level name (--prefixes and --harness-names leave it alone)
      dup  one definition site of a name that was already defined twice
      tmp  a label temporary (namespace is `-`)"""

    def __init__(self, path=BASELINE_GLOBALS):
        self.defs = set()       # (ns, name, file)
        self.dups = {}          # (ns, name, file) -> count
        self.tmps = set()       # (name, file)
        self.found = os.path.isfile(path)
        if not self.found:
            return
        with open(path, encoding="utf-8") as f:
            for raw in f:
                raw = raw.rstrip("\n")
                if not raw or raw.startswith("#"):
                    continue
                parts = raw.split("\t")
                if len(parts) != 4:
                    continue
                kind, ns, name, fk = parts
                if kind == "def":
                    self.defs.add((ns, name, fk))
                elif kind == "dup":
                    self.dups[(ns, name, fk)] = self.dups.get((ns, name, fk), 0) + 1
                elif kind == "tmp":
                    self.tmps.add((name, fk))


def load_prefixes(path=PREFIXES):
    if not os.path.isfile(path):
        return {"files": {}, "exceptions": [], "harness": ["zz", "ZZ"]}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_none_ok(path=NONE_OK):
    """The first column of tools/none_ok.txt: what `Function(` may name."""
    out = set()
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for raw in f:
                if raw.strip() and not raw.startswith("#"):
                    out.add(raw.rstrip("\n").split("\t")[0].strip())
    return out


def has_prefix(name, prefixes):
    """A name carries a prefix when it starts with it, leading underscores
    aside, or with its capitals (`toast_` also allows `TOAST_`). For
    `gui.x` and `persistent.x` the part after the dot may carry it."""
    cands = [name.lstrip("_")]
    if " " in name:
        cands.append(name.replace(" ", "_"))    # an image: `night sky` carries `night_`
    head, dot, tail = name.partition(".")
    if dot and head in ("gui", "persistent"):
        cands.append(tail.lstrip("_"))
    for c in cands:
        for p in prefixes:
            if c.startswith(p) or c.startswith(p.upper()):
                return True
    return False


def prefix_problem(ns, name, fk, cfg):
    """Why a new name in file fk breaks R1, or None."""
    for e in cfg.get("exceptions", []):
        if e.get("name") == name and e.get("file") == fk and e.get("namespace", ns) == ns:
            return None
    prefixes = cfg.get("files", {}).get(fk)
    if prefixes is None:
        return "%s has no row in tools/prefixes.json, so it may gain no new name" % fk
    if has_prefix(name, prefixes):
        return None
    if ns == "label":
        bare = name.lstrip("_")
        # sb_do_<action id>, where the action id carries the file's prefix,
        # and mg_<game id> for a minigame's label.
        if bare.startswith("sb_do_") and has_prefix(bare[len("sb_do_"):], prefixes):
            return None
        if bare.startswith("mg_"):
            return None
    return "does not start with one of %s's prefixes (%s)" % (fk, ", ".join(prefixes))


def rule_action_returns(path, lines, allowed):
    """[(Line, the function named)] for each `Function(` in a screen or a def
    that names neither ui_do nor a tools/none_ok.txt function."""
    for at, ln in enumerate(lines):
        # `F = Function`, anywhere in the file: calls made through the other
        # name could not be read, so the alias itself is the finding.
        if FUNCTION_ALIAS.search(ln.bare) and not re.match(r"\s*(?:from|import)\b", ln.bare):
            yield ln, None
        if not any(k in ("screen", "def") for k, _ in ln.blocks):
            continue
        for m in FUNCTION_CALL.finditer(ln.bare):
            rest = ln.bare[m.end():]
            if not rest.strip():
                # `Function(` and then a line break: the name is on the next
                # line that holds any code.
                for nxt in lines[at + 1:at + 6]:
                    if nxt.bare.strip():
                        rest = nxt.bare
                        break
            depth = 0
            arg = ""
            for ch in rest:
                if ch in "([{":
                    depth += 1
                elif ch in ")]}":
                    if depth == 0:
                        break
                    depth -= 1
                elif ch == "," and depth == 0:
                    break
                arg += ch
            arg = arg.strip()
            if arg != "ui_do" and arg not in allowed:
                yield ln, arg


def icon_names(lines):
    """The keys of ICONS, read from game/ui_icons.rpy's own text: the
    `"name": (` rows between `ICONS = {` and the line that closes it."""
    names = set()
    inside = False
    for ln in lines:
        if not inside:
            inside = bool(ICONS_OPEN.match(ln.code))
            continue
        if ln.code.strip().startswith("}"):
            break
        m = ICONS_ROW.match(ln.code)
        if m:
            names.add(m.group(1))
    return names


def rule_icon_names(path, lines, names):
    """[(Line, name)] for each icon("...") / icon_btn("...") whose literal
    first argument is not an icon name."""
    for ln in lines:
        # Found in the code with strings blanked (so "icon(" inside a string
        # is not a call), then read from the code itself.
        for m in ICON_CALL.finditer(ln.bare):
            lit = ICON_LITERAL.match(ln.code[m.end():])
            if lit and lit.group(2) not in names:
                yield ln, lit.group(2)


def art_names(images):
    """{base name: [paths]} for the names two or more files under images share."""
    seen = {}
    for d, _dirs, files in os.walk(images):
        for f in sorted(files):
            if f.startswith(".") or "." not in f:
                continue
            stem = f.rsplit(".", 1)[0].lower()
            seen.setdefault(stem, []).append(os.path.join(d, f))
    return {k: v for k, v in seen.items() if len(v) > 1}


def finding_key(path, rule, text):
    if len(text) > 200:
        text = text[:197] + "..."
    return (file_key(path), rule, text)


def load_known(path=BASELINE_FINDINGS):
    """{(file, rule, text): count} from tools/smoke/baseline_check_content.txt
    (the output format, `file:line: rule: text`; the line is not compared)."""
    known = {}
    if not os.path.isfile(path):
        return known
    rx = re.compile(r"^(.*?):(\d+): ([a-z0-9-]+): (.*)$")
    with open(path, encoding="utf-8") as f:
        for raw in f:
            m = rx.match(raw.rstrip("\n"))
            if m and m.group(3) in RULES:
                k = (m.group(1), m.group(3), m.group(4))
                known[k] = known.get(k, 0) + 1
    return known



# --- UI overhaul 2: layout files, decency, the baths, the "later" notes --------

def table_lines(lines, names):
    """The line numbers inside each top-level assignment `NAME = ( / [ / {`
    whose NAME is in `names`, from its first line to the one that closes it:
    {NAME: set of line numbers}."""
    out = {}
    cur, depth = None, 0
    rx = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*[\(\[\{]")
    for ln in lines:
        if cur is None:
            m = rx.match(ln.bare)
            if not m or m.group(1) not in names:
                continue
            cur, depth = m.group(1), 0
        out.setdefault(cur, set()).add(ln.n)
        for ch in ln.bare:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
        if depth <= 0:
            cur = None
    return out


def call_lines(lines, fn):
    """The line numbers of every `fn( ... )` call, continuation lines included."""
    out = set()
    depth, inside = 0, False
    rx = re.compile(r"(?<![\w.])" + re.escape(fn) + r"\s*\(")
    for ln in lines:
        if not inside:
            m = rx.search(ln.bare)
            if not m:
                continue
            inside, depth = True, 0
            text = ln.bare[m.start():]
        else:
            text = ln.bare
        out.add(ln.n)
        for ch in text:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
        if depth <= 0:
            inside = False
    return out


TRIPLE = ('"' * 3, "'" * 3)


def docstring_lines(lines):
    """The line numbers that are (part of) a triple-quoted string."""
    out = set()
    inside = None
    for ln in lines:
        raw = ln.raw
        i = 0
        hit = inside is not None
        while True:
            if inside is None:
                found = [c for c in (raw.find(q, i) for q in TRIPLE) if c >= 0]
                if not found:
                    break
                c = min(found)
                inside = raw[c:c + 3]
                hit = True
                i = c + 3
            else:
                c = raw.find(inside, i)
                if c < 0:
                    break
                inside = None
                i = c + 3
        if hit:
            out.add(ln.n)
    return out


def world_keys(cache):
    """(place keys, area keys) read from game/sb_world.rpy's own text."""
    src = os.path.join(GAME, "sb_world.rpy")
    places, areas = set(), set()
    if not os.path.isfile(src):
        return places, areas
    lines = read_lines(src, cache)
    inside = table_lines(lines, {"LOCATIONS", "AREAS"})
    for ln in lines:
        if ln.n in inside.get("LOCATIONS", ()):
            m = re.match(r"""\s*["'](\w+)["']\s*:\s*dict\(""", ln.code)
            if m:
                places.add(m.group(1))
        if ln.n in inside.get("AREAS", ()):
            m = re.search(r"""dict\(\s*key\s*=\s*["'](\w+)["']""", ln.code)
            if m:
                areas.add(m.group(1))
    return places, areas


def lf_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def lf_point(v):
    return isinstance(v, list) and len(v) == 2 and all(lf_num(q) for q in v)


def lf_poly(v):
    return isinstance(v, list) and len(v) >= 3 and all(lf_point(q) for q in v)


def lf_box(v):
    return isinstance(v, list) and len(v) == 4 and all(lf_num(q) for q in v) and v[2] > 0 and v[3] > 0


def lf_rev(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def lf_light_row(v):
    return (isinstance(v, list) and len(v) in (4, 6) and isinstance(v[0], str)
            and bool(re.match(r"^#[0-9a-fA-F]{6}$", v[0])) and all(lf_num(q) for q in v[1:]))


LF_SIDES = ("top", "bottom", "left", "right")
LF_FACES = ("neutral", "happy", "serious", "angry", "surprised", "sad")
LF_HOURS = ("", "evening", "night")
LF_PERIODS = ("Morning", "Noon", "Afternoon", "Evening", "Night")
# The houses painted with spare doors (D50): their hot_ file may hold `spare`.
LF_SPARE_HOUSES = ("boys_dorm", "girls_dorm", "teachers_dorm", "teachers_lounge")
LF_PICTURE_KEYS = {"rev", "kind", "batch", "render", "record", "rev1_commit", "from_commit",
                   "shift", "sharp", "of", "of_rev", "waiver"}
LF_PICTURE_KINDS = ("composed", "inplace", "relight")
LF_LIGHT_ROW = ("[\"#rrggbb\", brightness, saturation, shadow opacity], or the same with "
                "[shadow lean, shadow stretch] after it")


def lf_floor(v):
    """A list of polygons, or {"on": [polygons], "off": [polygons]}."""
    if isinstance(v, dict):
        return (set(v) <= {"on", "off"} and "on" in v
                and all(isinstance(v[k], list) and all(lf_poly(p) for p in v[k]) for k in v))
    return isinstance(v, list) and bool(v) and all(lf_poly(p) for p in v)


def lf_slots(v):
    if not isinstance(v, dict):
        return "slots must be {\"1\" to \"4\": [[x centre, y offset, zoom, far], ...]}"
    for k, rows in v.items():
        if k not in ("1", "2", "3", "4"):
            return "slot key %r is not \"1\" to \"4\"" % k
        if not isinstance(rows, list) or len(rows) != int(k):
            return "slots[%r] must hold %s row%s" % (k, k, "" if k == "1" else "s")
        for r in rows:
            if not (isinstance(r, list) and len(r) in (3, 4) and all(lf_num(q) for q in r) and r[2] > 0):
                return "slots[%r]: a row is three or four numbers with a zoom above 0" % k
    return None


def lf_hour_dict(v, test):
    """{hour or period: value}, each value passing `test`."""
    return isinstance(v, dict) and all(k in LF_HOURS + LF_PERIODS and test(x) for k, x in v.items())


def layout_file_findings(folder, cache):
    """--layout-files: [(path, text)] for every file under game/layout/."""
    out = []
    if not os.path.isdir(folder):
        return out
    places, areas = world_keys(cache)
    data = {}
    for f in sorted(os.listdir(folder)):
        path = os.path.join(folder, f)
        if f.startswith(".") or os.path.isdir(path):
            continue
        if not f.endswith(".json"):
            out.append((path, "only .json files belong in game/layout/"))
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                got = json.load(fh)
        except Exception as e:
            out.append((path, "it is not JSON (%s)" % " ".join(str(e).split())[:80]))
            continue
        if not isinstance(got, dict):
            out.append((path, "it must hold one JSON object"))
            continue
        data[f[:-5]] = (path, got)

    composed = set()
    pics = data.get("pictures", (None, {}))[1].get("pictures")
    if isinstance(pics, dict):
        composed = set(k for k, r in pics.items() if isinstance(r, dict) and r.get("kind") == "composed")

    def bad(path, text):
        out.append((path, text))

    def keys(path, got, allowed):
        extra = sorted(set(got) - set(allowed))
        if extra:
            bad(path, "unknown key%s %s (allowed: %s)" % (
                "" if len(extra) == 1 else "s", ", ".join(repr(k) for k in extra),
                ", ".join(repr(k) for k in allowed)))

    def place_of(path, stem, head):
        key = stem[len(head):]
        if places and key not in places:
            bad(path, "%r is not a place (a key of LOCATIONS in game/sb_world.rpy)" % key)
        return key

    def for_rev(path, got, place, need_composed=True):
        if "for_rev" not in got:
            return
        if not lf_rev(got["for_rev"]):
            bad(path, "for_rev must be a whole number, 1 or more")
        if need_composed and place not in composed:
            bad(path, "for_rev is only for a composed picture or a new place: pictures.json does not "
                      "call %r \"composed\" (a room redone in place carries none, 3.2)" % place)

    for stem in sorted(data):
        path, got = data[stem]
        if stem.startswith("hot_"):
            place = place_of(path, stem, "hot_")
            keys(path, got, ("spots", "tips", "spare", "for_rev"))
            v = got.get("spots", {})
            if not (isinstance(v, dict) and all(isinstance(k, str) and lf_point(p) for k, p in v.items())):
                bad(path, "spots must be {\"<hotspot or exit id>\": [x, y]}")
            v = got.get("tips", {})
            if not (isinstance(v, dict) and all(isinstance(k, str) and s in LF_SIDES for k, s in v.items())):
                bad(path, "tips must be {\"<id>\": \"top\", \"bottom\", \"left\" or \"right\"}")
            if "spare" in got:
                if not (isinstance(got["spare"], list) and all(lf_point(p) for p in got["spare"])):
                    bad(path, "spare must be a list of [x, y] points")
                if place not in LF_SPARE_HOUSES:
                    bad(path, "spare is for the houses with spare doors only (%s)" % ", ".join(LF_SPARE_HOUSES))
            for_rev(path, got, place)
        elif stem.startswith("view_"):
            place = place_of(path, stem, "view_")
            keys(path, got, ("slots", "poses", "floor", "scale", "slot_light", "cast", "talk", "for_rev"))
            if "slots" in got:
                why = lf_slots(got["slots"])
                if why:
                    bad(path, why)
            v = got.get("poses", {})
            if not (isinstance(v, dict) and all(isinstance(k, str) and lf_box(b) for k, b in v.items())):
                bad(path, "poses must be {\"<who>\" or \"<who>__<variant>\": [x, y, w, h]}")
            if "floor" in got and not lf_floor(got["floor"]):
                bad(path, "floor must be a list of polygons, or {\"on\": [polygons], \"off\": [polygons]}; "
                          "a polygon is three or more [x, y] points")
            if "scale" in got and not (isinstance(got["scale"], list) and len(got["scale"]) == 3
                                       and all(lf_num(q) for q in got["scale"]) and got["scale"][1] < got["scale"][2]):
                bad(path, "scale must be [x, y top, y bottom] of one door or post")
            if "slot_light" in got and not lf_hour_dict(got["slot_light"], lambda x: isinstance(x, (dict, list))):
                bad(path, "slot_light must be keyed by hour (\"\", \"evening\", \"night\") or period")
            if "cast" in got and not lf_hour_dict(got["cast"], lambda x: isinstance(x, list) and len(x) == 3
                                                  and all(lf_num(q) for q in x)):
                bad(path, "cast must be {hour or period: [direction, length, darkness]}")
            if "talk" in got and not isinstance(got["talk"], bool):
                bad(path, "talk must be true or false")
            for_rev(path, got, place)
        elif stem.startswith("pose_"):
            place_of(path, stem, "pose_")
            keys(path, got, ("poses",))
            v = got.get("poses")
            if not (isinstance(v, dict) and all(isinstance(k, str) and lf_box(b) for k, b in v.items())):
                bad(path, "it must hold {\"poses\": {\"<who>\" or \"<who>__<variant>\": [x, y, w, h]}}")
        elif stem.startswith("light_"):
            place_of(path, stem, "light_")
            keys(path, got, LF_HOURS)
            for k in sorted(got):
                if k in LF_HOURS and not lf_light_row(got[k]):
                    bad(path, "the row %r must be %s" % (k, LF_LIGHT_ROW))
        elif stem == "light":
            for k in sorted(got):
                if not lf_light_row(got[k]):
                    bad(path, "the row %r must be %s" % (k, LF_LIGHT_ROW))
        elif stem.startswith("area_"):
            key = stem[len("area_"):]
            if areas and key not in areas:
                bad(path, "%r is not an area (a key of AREAS in game/sb_world.rpy)" % key)
            keys(path, got, ("spots", "for_rev"))
            v = got.get("spots", {})
            if not (isinstance(v, dict) and all(isinstance(k, str) and lf_point(p) for k, p in v.items())):
                bad(path, "spots must be {\"<place>\": [x, y]}")
            elif places:
                for k in sorted(v):
                    if k not in places:
                        bad(path, "spots: %r is not a place" % k)
            for_rev(path, got, None, need_composed=False)
        elif stem == "map_campus":
            keys(path, got, ("anchors", "mountain_box"))
            v = got.get("anchors", {})
            if not (isinstance(v, dict) and all((not areas or k in areas) and lf_point(p) for k, p in v.items())):
                bad(path, "anchors must be {\"<area key>\": [x, y]}")
            if "mountain_box" in got:
                b = got["mountain_box"]
                if not (isinstance(b, list) and len(b) == 4 and all(lf_num(q) for q in b) and b[0] < b[2] and b[1] < b[3]):
                    bad(path, "mountain_box must be [x0, y0, x1, y1]")
        elif stem == "faces":
            keys(path, got, ("blink_also",))
            v = got.get("blink_also", {})
            if not (isinstance(v, dict) and all(isinstance(k, str) and isinstance(fs, list)
                                                and all(f in LF_FACES for f in fs) for k, fs in v.items())):
                bad(path, "blink_also must be {\"<who>\": [faces]}, the faces among %s" % ", ".join(LF_FACES))
        elif stem == "pictures":
            keys(path, got, ("pictures",))
            v = got.get("pictures")
            if not isinstance(v, dict):
                bad(path, "it must hold {\"pictures\": {\"<file stem>\": {...}}}")
                continue
            for k in sorted(v):
                r = v[k]
                if not isinstance(r, dict):
                    bad(path, "pictures[%r] must be an object" % k)
                    continue
                extra = sorted(set(r) - LF_PICTURE_KEYS)
                if extra:
                    bad(path, "pictures[%r]: unknown key%s %s" % (k, "" if len(extra) == 1 else "s", ", ".join(extra)))
                if "rev" in r and not lf_rev(r["rev"]):
                    bad(path, "pictures[%r]: rev must be a whole number, 1 or more" % k)
                if "kind" in r and r["kind"] not in LF_PICTURE_KINDS:
                    bad(path, "pictures[%r]: kind must be one of %s" % (k, ", ".join(LF_PICTURE_KINDS)))
                if ("of" in r) != ("of_rev" in r) or ("of" in r and not (isinstance(r["of"], str) and lf_rev(r["of_rev"]))):
                    bad(path, "pictures[%r]: `of` (a file stem) and `of_rev` (its revision) go together" % k)
                if "rev" not in r and "of" not in r:
                    bad(path, "pictures[%r]: a row holds `rev`, or `of` and `of_rev`" % k)
                for pair in ("shift", "sharp"):
                    if pair in r and not lf_point(r[pair]):
                        bad(path, "pictures[%r]: %s must be two numbers" % (k, pair))
        else:
            bad(path, "not a layout file name (hot_<place>, view_<place>, pose_<place>, light_<place>, "
                      "area_<key>, light, map_campus, faces, pictures)")
    return out


DECENCY = re.compile(r"\b(towels?|naked|undress(?:ed|es|ing)?|strip(?:s|ped|ping)?|swimsuits?|bikinis?"
                     r"|skin|bare|changing)\b", re.IGNORECASE)
DECENCY_FILES = ("room_bath.rpy", "room_pool.rpy", "room_tokyo.rpy")
DECENCY_PLACES = ("bathhouse", "sauna", "pool",
                  "yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room")
DECENCY_PAIR = re.compile(r"""\(\s*["'](\w+)["']\s*,\s*["'](\w+)["']""")
DECENCY_KEY = re.compile(r"""^\s*["'](\w+)["']\s*:""")
POSES_TOOL = os.path.join(ROOT, "tools", "make_pose_workflow.py")


def decency_findings(files, cache):
    """--decency: [(path, line number, text)]."""
    out = []

    def hits(path, ln, where):
        for s in ln.strings:
            m = DECENCY.search(s)
            if m:
                out.append((path, ln.n, "%r %s: %s" % (m.group(1).lower(), where, ln.raw.strip())))
                return

    game = [p for p in files if is_game(p)]
    # hotspot id -> place, for the rows of SPOT_LINES: every ("id", "place"
    # pair in a game file whose second name is one of the places.
    spot_place = {}
    for path in collect([GAME]):
        for ln in read_lines(path, cache):
            for m in DECENCY_PAIR.finditer(ln.code):
                if m.group(2) in DECENCY_PLACES:
                    spot_place[m.group(1)] = m.group(2)
    for path in game:
        lines = read_lines(path, cache)
        docs = docstring_lines(lines)
        if os.path.basename(path) in DECENCY_FILES:
            for ln in lines:
                if ln.n not in docs:
                    hits(path, ln, "in %s" % os.path.basename(path))
            continue
        inside = table_lines(lines, {"AMBIENT", "SPOT_LINES"})
        key = None
        for ln in lines:
            if ln.n in inside.get("AMBIENT", ()):
                m = DECENCY_PAIR.search(ln.code)
                if m and m.group(2) in DECENCY_PLACES:
                    hits(path, ln, "in the AMBIENT row for %s" % m.group(2))
            elif ln.n in inside.get("SPOT_LINES", ()):
                m = DECENCY_KEY.match(ln.code)
                if m:
                    key = m.group(1)
                if key in spot_place:
                    hits(path, ln, "in the SPOT_LINES row %r (%s)" % (key, spot_place[key]))
            else:
                key = None
    # The pose plan is a tool's table; it is read whenever the rule runs.
    if os.path.isfile(POSES_TOOL):
        lines = read_lines(POSES_TOOL, cache)
        inside = table_lines(lines, {"POSES"}).get("POSES", set())
        row, depth, place = [], 0, None
        for ln in lines:
            if ln.n not in inside:
                continue
            was = depth
            for ch in ln.bare:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
            if was == 0 and "{" not in ln.bare:
                depth = 0
                continue
            row.append(ln)
            m = re.search(r"""["']place["']\s*:\s*["'](\w+)["']""", ln.code)
            if m:
                place = m.group(1)
            if depth <= 0:
                if place in DECENCY_PLACES:
                    for r in row:
                        hits(POSES_TOOL, r, "in the POSES row for %s" % place)
                row, depth, place = [], 0, None
    return out


BATHS = re.compile(r"bath_soak|bath_sauna|bath_ok|pool_swim")
BATHS_OWN = ("room_bath.rpy", "room_pool.rpy")
BATHS_TABLES = {"ui_icons.rpy": {"ICONS", "ICON_FOR"}, "sb_hotspots.rpy": {"SPOT_PLANNED"},
                "sb_night.rpy": {"NIGHT_REST_BLOCKS"}}
BATHS_ICON_FOR = re.compile(r"^\s*ICON_FOR\s*\[")


def baths_findings(files, cache):
    """--baths-optional: [(path, Line, what)]."""
    out = []
    for path in files:
        base = os.path.basename(path)
        if not is_game(path) or base in BATHS_OWN:
            continue
        lines = read_lines(path, cache)
        ok = set(call_lines(lines, "register_hotspot"))
        for nums in table_lines(lines, BATHS_TABLES.get(base, set())).values():
            ok |= nums
        for ln in lines:
            what = None
            if "bath" in ln.strings:
                what = '"bath"'
            else:
                m = BATHS.search(ln.code)
                if m:
                    what = m.group(0)
            if what is None or ln.n in ok:
                continue
            if base == "ui_icons.rpy" and BATHS_ICON_FOR.match(ln.code):
                continue
            out.append((path, ln, what))
    return out


LATER = re.compile(r"later build|combat update", re.IGNORECASE)


def load_later_ok(path=LATER_OK):
    """[(file, text fragment)]: the rows of tools/later_ok.txt, one line of
    the game each."""
    rows = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for raw in f:
                if raw.strip() and not raw.startswith("#"):
                    parts = raw.rstrip("\n").split("\t")
                    if len(parts) >= 2:
                        rows.append((parts[0].strip(), parts[1].strip()))
    return rows


def later_findings(files, cache):
    """--later-notes: ([(path, Line)] not allowed, how many were allowed,
    [rows of later_ok.txt that matched no line])."""
    spare = load_later_ok()
    out, allowed = [], 0
    for path in files:
        if not is_game(path):
            continue
        lines = read_lines(path, cache)
        docs = docstring_lines(lines)
        fk = file_key(path)
        for ln in lines:
            if ln.n in docs or not any(LATER.search(s) for s in ln.strings):
                continue
            for i, (f, frag) in enumerate(spare):
                if f == fk and frag in ln.raw:
                    del spare[i]
                    allowed += 1
                    break
            else:
                out.append((path, ln))
    checked = set(file_key(p) for p in files)
    return out, allowed, [r for r in spare if r[0] in checked]


# --- driver --------------------------------------------------------------------

def read_lines(path, cache):
    key = os.path.realpath(path)
    if key not in cache:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if text.startswith("﻿"):
            text = text[1:]
        cache[key] = scan(text)
    return cache[key]


def collect(paths):
    """Expand folders into their .rpy files, keeping the order given."""
    out = []
    for p in paths:
        if os.path.isdir(p):
            for d, _dirs, files in os.walk(p):
                for f in sorted(files):
                    if f.endswith(".rpy"):
                        out.append(os.path.join(d, f))
        else:
            out.append(p)
    seen = set()
    uniq = []
    for p in out:
        k = os.path.realpath(p)
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def shown(path):
    """A path as it reads best: relative to the current folder when inside it."""
    rel = os.path.relpath(path)
    return path if rel.startswith("..") else rel


def global_findings(files, chosen, cache):
    """The findings of --dup-globals, --prefixes, --harness-names, --art-names,
    --action-returns and --icon-names, as (path, line, rule, text)."""
    out = []
    base = Baseline()
    cfg = load_prefixes()
    game_files = collect([GAME])
    lib = os.path.join(SMOKE, "_lib.rpy")

    def defs_of(path):
        return definitions(path, read_lines(path, cache))

    game_defs = {}      # (ns, name) -> [(path, Line)]
    for path in game_files:
        for ns, name, ln in defs_of(path):
            game_defs.setdefault((ns, name), []).append((path, ln))
    lib_defs = {}
    if os.path.isfile(lib):
        for ns, name, ln in defs_of(lib):
            lib_defs.setdefault((ns, name), []).append((lib, ln))

    harnesses = [p for p in files if not is_game(p)]
    if "harness-names" in chosen and not harnesses and os.path.isdir(SMOKE):
        harnesses = collect([SMOKE])

    if "dup-globals" in chosen:
        for path in files:
            real = os.path.realpath(path)
            fk = file_key(path)
            own = {}
            for ns, name, ln in defs_of(path):
                own.setdefault((ns, name), []).append(ln)
            for (ns, name), lns in sorted(own.items(), key=lambda kv: kv[1][0].n):
                if ns == "label" and "dup-labels" in chosen:
                    continue    # that rule reports it; once is enough
                others = [(p, l) for p, l in game_defs.get((ns, name), [])
                          if os.path.realpath(p) != real]
                if not is_game(path) and real != os.path.realpath(lib):
                    others += lib_defs.get((ns, name), [])
                if ns == "style":
                    # `style x is y` and then `style x:` in one file is how
                    # Ren'Py styles are written; a style is a finding only
                    # when two files define it.
                    lns = lns[:1]
                if len(lns) < 2 and not others:
                    continue
                # Every site of a name defined twice is a finding, less the
                # sites the baseline already holds for this file.
                spare = base.dups.get((ns, name, fk), 0)
                for ln in lns[spare:]:
                    where = ["%s:%d" % (shown(p), l.n) for p, l in others]
                    where += ["%s:%d" % (shown(path), l.n) for l in lns if l is not ln]
                    out.append((path, ln.n, "dup-globals", "%s %s is also defined at %s" % (
                        ns, name, ", ".join(where))))

    if "prefixes" in chosen:
        store_names = set(name for (ns, name) in game_defs if ns == "store")
        store_names |= set(name for (ns, name, _f) in base.defs if ns == "store")
        for path in files:
            if not is_game(path):
                continue
            fk = file_key(path)
            lines = read_lines(path, cache)
            for ns, name, ln in defs_of(path):
                if (ns, name, fk) in base.defs:
                    continue
                if ns == "store" and name.startswith("config."):
                    continue    # an engine setting, not a name of ours
                why = prefix_problem(ns, name, fk, cfg)
                if why:
                    out.append((path, ln.n, "prefixes", "%s %s %s" % (ns, name, why)))
            seen = set()
            for name, ln in label_temporaries(path, lines):
                if name in seen or name in store_names or name in RENPY_VARS or (name, fk) in base.tmps:
                    continue
                seen.add(name)
                why = prefix_problem("tmp", name, fk, cfg)
                if why:
                    out.append((path, ln.n, "prefixes", "label temporary %s %s" % (name, why)))

    if "harness-names" in chosen:
        marks = tuple(cfg.get("harness", ["zz", "ZZ"]))
        for path in harnesses:
            fk = file_key(path)
            for ns, name, ln in defs_of(path):
                if (ns, name, fk) in base.defs or name.lstrip("_").startswith(marks):
                    continue
                out.append((path, ln.n, "harness-names", "%s %s does not start with %s" % (
                    ns, name, " / ".join(marks))))

    if "art-names" in chosen:
        images = os.path.join(GAME, "images")
        for stem, paths in sorted(art_names(images).items()):
            for p in paths[1:]:
                out.append((p, 1, "art-names", "the image name %s is also %s" % (
                    stem, ", ".join(file_key(q) for q in paths if q != p))))

    if "action-returns" in chosen:
        allowed = load_none_ok()
        for path in files:
            if not is_game(path):
                continue
            for ln, arg in rule_action_returns(path, read_lines(path, cache), allowed):
                if arg is None:
                    out.append((path, ln.n, "action-returns",
                                "Function is passed on without being called (an alias hides what it "
                                "runs from this rule): %s" % ln.raw.strip()))
                    continue
                out.append((path, ln.n, "action-returns",
                            "Function(%s ...) is not ui_do or in tools/none_ok.txt: %s" % (arg, ln.raw.strip())))

    if "icon-names" in chosen:
        src = os.path.join(GAME, "ui_icons.rpy")
        names = icon_names(read_lines(src, cache)) if os.path.isfile(src) else set()
        checked = [p for p in files if is_game(p)]
        if not names and checked:
            # Never pass because the list could not be read.
            out.append((src, 1, "icon-names", "no ICONS = { ... } table of \"name\": (kanji, word) rows "
                        "could be read from game/ui_icons.rpy"))
        elif names:
            for path in checked:
                for ln, name in rule_icon_names(path, read_lines(path, cache), names):
                    out.append((path, ln.n, "icon-names", "%r is not an icon name (a key of ICONS in "
                                "game/ui_icons.rpy): %s" % (name, ln.raw.strip())))
    return out


def write_baselines(cache, really=True):
    """--write-baseline: the names and the findings of the tree as it stands.
    With really=False nothing is written: the rows the names baseline would
    gain and lose are printed instead."""
    files = collect([GAME, SMOKE])
    game_files = [p for p in files if is_game(p)]
    all_defs = {p: definitions(p, read_lines(p, cache)) for p in files}
    game_defs = {}
    for p in game_files:
        for ns, name, ln in all_defs[p]:
            game_defs.setdefault((ns, name), []).append(p)
    lib = os.path.realpath(os.path.join(SMOKE, "_lib.rpy"))
    lib_names = set((ns, name) for p in files if os.path.realpath(p) == lib
                    for ns, name, ln in all_defs[p])
    store_names = set(name for (ns, name) in game_defs if ns == "store")
    rows = []
    for p in files:
        fk = file_key(p)
        counts = {}
        for ns, name, ln in all_defs[p]:
            counts[(ns, name)] = counts.get((ns, name), 0) + 1
        for (ns, name), n in sorted(counts.items()):
            rows.append(("def", ns, name, fk))
            elsewhere = [q for q in game_defs.get((ns, name), []) if os.path.realpath(q) != os.path.realpath(p)]
            if not is_game(p) and os.path.realpath(p) != lib and (ns, name) in lib_names:
                elsewhere.append(lib)
            if ns == "style":
                n = 1
            if n > 1 or elsewhere:
                rows.extend([("dup", ns, name, fk)] * n)
        if is_game(p):
            for name in sorted(set(nm for nm, ln in label_temporaries(p, read_lines(p, cache)))):
                if name not in store_names and name not in RENPY_VARS:
                    rows.append(("tmp", "-", name, fk))
    if not really:
        old = set()
        if os.path.isfile(BASELINE_GLOBALS):
            with open(BASELINE_GLOBALS, encoding="utf-8") as f:
                old = set(tuple(r.rstrip("\n").split("\t")) for r in f
                          if r.strip() and not r.startswith("#"))
        new = set(rows)
        for mark, group in (("+", sorted(new - old)), ("-", sorted(old - new))):
            for r in group:
                print("  %s %s" % (mark, "  ".join(r)), file=sys.stderr)
        print("check_content: %d row%s would be added to %s and %d removed" % (
            len(new - old), "" if len(new - old) == 1 else "s", shown(BASELINE_GLOBALS),
            len(old - new)), file=sys.stderr)
        return len(rows)
    with open(BASELINE_GLOBALS, "w", encoding="utf-8") as f:
        f.write("# tools/smoke/baseline_globals.txt -- the names the tree had when this file\n"
                "# was last written (by `tools/check_content.py --write-baseline`: at P0a,\n"
                "# before phase 2 changed a game file, and again by P8 at the end of the\n"
                "# phase; frozen in between). Tab-separated: kind, namespace, name, file.\n"
                "#   def  a top-level name: --prefixes and --harness-names leave it alone\n"
                "#   dup  one definition site of a name that was already defined twice:\n"
                "#        --dup-globals leaves that many sites in that file alone\n"
                "#   tmp  a `$ name = ...` temporary in a label: --prefixes leaves it alone\n")
        for r in sorted(set(r for r in rows if r[0] != "dup")) + sorted(r for r in rows if r[0] == "dup"):
            f.write("\t".join(r) + "\n")
    return len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_content.py",
        description="Static content checks (PHASE1_DESIGN.md 8.4, PHASE2_DESIGN.md 2.2).",
        epilog="Prints file:line: rule: text; exits 1 on findings.")
    ap.add_argument("--all", action="store_true", help="every rule (the default)")
    for r in RULES + REPORT_RULES:
        ap.add_argument("--" + r, dest=r.replace("-", "_"), action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="--later-notes: its lines are findings (integration)")
    ap.add_argument("--layout-dir", default=LAYOUT,
                    help="--layout-files: the folder to read (default game/layout)")
    ap.add_argument("--include-phase4", action="store_true",
                    help="also list the narration-person findings that section 5.4 "
                         "exempts (the PHASE4_YOU table)")
    ap.add_argument("--no-baseline", action="store_true",
                    help="also list the findings tools/smoke/baseline_check_content.txt records")
    ap.add_argument("--write-baseline", action="store_true",
                    help="write baseline_globals.txt and baseline_check_content.txt "
                         "from the tree as it stands (P0a and P8 only)")
    ap.add_argument("--i-am-p0a-or-p8", dest="really_write", action="store_true",
                    help="the second flag --write-baseline needs before it replaces "
                         "the two frozen baselines")
    ap.add_argument("files", nargs="*", help=".rpy files or folders (default: game/)")
    args = ap.parse_args(argv)

    chosen = [r for r in RULES if getattr(args, r.replace("-", "_"))]
    reports = [r for r in REPORT_RULES if getattr(args, r.replace("-", "_"))]
    if args.all or not (chosen or reports):
        chosen = list(RULES)

    cache = {}
    if args.write_baseline and not args.really_write:
        # The baselines are frozen: a package that rewrote them would bless
        # its own findings. Show what would change and stop.
        print("check_content.py: --write-baseline would replace the two frozen baselines:\n"
              "  %s\n  %s\nNothing was written. Only P0a and P8 do this; they add "
              "--i-am-p0a-or-p8." % (shown(BASELINE_GLOBALS), shown(BASELINE_FINDINGS)),
              file=sys.stderr)
        write_baselines(cache, really=False)
        return 2
    if args.write_baseline:
        n_rows = write_baselines(cache)
        chosen = list(RULES)
        args.files = [GAME, SMOKE]
        args.no_baseline = True

    files = collect(args.files or [GAME])
    missing = [p for p in files if not os.path.isfile(p)]
    if missing:
        for p in missing:
            print("check_content.py: no such file: " + p, file=sys.stderr)
        return 2

    findings = []   # (path, line, rule, text)
    exempt = {}     # file -> narration-person lines exempted by PHASE4_YOU
    per_line_rules = [
        ("no-mc-on-screen", rule_mc),
        ("one-technique", rule_technique),
        ("no-deadline", rule_deadline),
        ("narration-person", rule_narration),
        ("no-literal-name", rule_literal_name),
    ]
    for path in files:
        lines = read_lines(path, cache)
        for name, fn in per_line_rules:
            if name in chosen:
                for ln in fn(path, lines):
                    if (name == "narration-person" and not args.include_phase4
                            and phase4_exempt(path, label_of(ln))):
                        exempt[path] = exempt.get(path, 0) + 1
                        continue
                    findings.append((path, ln.n, name, ln.raw.strip()))

    if "dup-labels" in chosen:
        # Game files clash with each other. A file outside game/ (a smoke
        # harness, installed alone into a scratch copy) clashes only with
        # game files, never with another harness.
        game_defs = {}
        for path in collect([GAME]):
            for name, ln in label_defs(path, read_lines(path, cache)):
                game_defs.setdefault(name, []).append((path, ln))
        for path in files:
            for name, ln in label_defs(path, read_lines(path, cache)):
                others = [(p, l) for p, l in game_defs.get(name, [])
                          if os.path.realpath(p) != os.path.realpath(path) or l.n != ln.n]
                if others:
                    findings.append((path, ln.n, "dup-labels", "label %s is also defined at %s" % (
                        name, ", ".join("%s:%d" % (shown(p), l.n) for p, l in others))))

    findings.extend(global_findings(files, chosen, cache))

    if "layout-files" in chosen:
        for path, text in layout_file_findings(args.layout_dir, cache):
            findings.append((path, 1, "layout-files", text))
    if "decency" in chosen:
        for path, n, text in decency_findings(files, cache):
            findings.append((path, n, "decency", text))
    if "baths-optional" in chosen:
        for path, ln, what in baths_findings(files, cache):
            findings.append((path, ln.n, "baths-optional",
                             "%s is read outside room_bath.rpy and room_pool.rpy (K17: nothing may need a "
                             "bath): %s" % (what, ln.raw.strip())))
    report_lines = []
    if "later-notes" in reports:
        later, later_ok_n, later_unused = later_findings(files, cache)
        rows = [(path, ln.n, "later-notes", ln.raw.strip()) for path, ln in later]
        rows += [(os.path.join(ROOT, f), 1, "later-notes",
                  "tools/later_ok.txt allows a line holding %r, and no such line is left" % frag)
                 for f, frag in later_unused]
        (findings if args.strict else report_lines).extend(rows)
        print("check_content: note: later-notes: %d line%s on tools/later_ok.txt; %d other%s%s" % (
            later_ok_n, "" if later_ok_n == 1 else "s", len(rows), "" if len(rows) == 1 else "s",
            "" if args.strict else " (a report: --strict makes them findings)"), file=sys.stderr)

    order = {os.path.realpath(p): i for i, p in enumerate(files)}
    findings.sort(key=lambda f: (order.get(os.path.realpath(f[0]), len(order)), f[1], (RULES + REPORT_RULES).index(f[2])))

    def out_line(path, n, rule, text):
        if len(text) > 200:
            text = text[:197] + "..."
        return "%s:%d: %s: %s" % (file_key(path) if args.write_baseline else shown(path), n, rule, text)

    if args.write_baseline:
        with open(BASELINE_FINDINGS, "w", encoding="utf-8") as f:
            f.write("# tools/smoke/baseline_check_content.txt -- the findings of\n"
                    "# `tools/check_content.py --all game/ tools/smoke/` that the tree had when this\n"
                    "# file was last written (by --write-baseline: at P0a, before phase 2 changed a\n"
                    "# game file, and again by P8 at the end of the phase; frozen in between).\n"
                    "# A finding with the same file, rule and text is counted, not listed; line\n"
                    "# numbers are not compared. --no-baseline lists them. (Names have their own\n"
                    "# baseline, baseline_globals.txt.)\n")
            for path, n, rule, text in findings:
                f.write(out_line(path, n, rule, text) + "\n")
        print("check_content: wrote %s (%d rows) and %s (%d findings)" % (
            shown(BASELINE_GLOBALS), n_rows, shown(BASELINE_FINDINGS), len(findings)), file=sys.stderr)
        return 0

    known_n = 0
    if not args.no_baseline:
        known = load_known()
        kept = []
        for f in findings:
            k = finding_key(f[0], f[2], f[3])
            if known.get(k, 0) > 0:
                known[k] -= 1
                known_n += 1
            else:
                kept.append(f)
        findings = kept

    for path, n, rule, text in report_lines + findings:
        print(out_line(path, n, rule, text))

    if exempt:
        n_ex = sum(exempt.values())
        print("check_content: note: narration-person: %d line%s exempt in %d file%s "
              "(section 5.4 keeps the later chapters in \"you\" until phase 4; "
              "--include-phase4 lists them)" % (
                  n_ex, "" if n_ex == 1 else "s",
                  len(exempt), "" if len(exempt) == 1 else "s"), file=sys.stderr)
    if known_n:
        print("check_content: note: %d finding%s already in %s (--no-baseline lists them)" % (
            known_n, "" if known_n == 1 else "s", shown(BASELINE_FINDINGS)), file=sys.stderr)

    counts = {}
    for f in findings:
        counts[f[2]] = counts.get(f[2], 0) + 1
    if findings:
        summary = ", ".join("%s %d" % (r, counts[r]) for r in RULES + REPORT_RULES if r in counts)
        print("check_content: %d finding%s in %d file%s (%s)" % (
            len(findings), "" if len(findings) == 1 else "s",
            len(files), "" if len(files) == 1 else "s", summary), file=sys.stderr)
        return 1
    print("check_content: clean (%s; %d file%s)" % (
        ", ".join(chosen + reports), len(files), "" if len(files) == 1 else "s"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
