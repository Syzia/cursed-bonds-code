#!/usr/bin/env python3
"""Static content checks for phase 1 (docs/PHASE1_DESIGN.md, section 8.4).

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
  --all               Every rule. This is also the default when no rule flag
                      is given.

FILES are .rpy files or folders (searched for .rpy). With none, every .rpy
under game/ is checked.

Examples:
    python3 tools/check_content.py --all game/*.rpy
    python3 tools/check_content.py --narration-person --include-phase4 game/story_arc1.rpy
    python3 tools/check_content.py --no-literal-name game/sb_board.rpy
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "game")

RULES = [
    "no-mc-on-screen",
    "one-technique",
    "no-deadline",
    "narration-person",
    "no-literal-name",
    "dup-labels",
]

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
PYTHON_HEADER = re.compile(r"^(init(\s+[-+]?\d+)?\s+)?python\b")
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
                 "continuation", "blocks")

    def __init__(self, n, raw):
        self.n = n
        self.raw = raw
        self.code = raw          # the line up to a comment
        self.strings = []        # string literal contents (fragments too)
        self.first_string = None  # (start, end) of a string opening the line
        self.rest = ""           # code after that first string
        self.continuation = False  # inside brackets or a string from above
        self.blocks = ()         # enclosing blocks, outermost first: (kind, name)


def scan(text):
    """Split a .rpy file into Line records: comments stripped, string literals
    collected, bracket and string continuations flagged, and each line's
    enclosing blocks (label, menu, python, screen, ...) worked out from
    indentation."""
    lines = []
    open_quote = None   # '"', "'", '\"\"\"' or "'''" carried from the line above
    depth = 0
    stack = []          # [(indent, kind, name)]
    for n, raw in enumerate(text.splitlines(), 1):
        ln = Line(n, raw)
        ln.continuation = bool(open_quote) or depth > 0
        i = 0
        L = len(raw)
        comment_at = None
        if open_quote:
            end = raw.find(open_quote)
            while end > 0 and raw[end - 1] == "\\" and len(open_quote) == 1:
                end = raw.find(open_quote, end + 1)
            if end < 0:
                ln.strings.append(raw)
                i = L
            else:
                ln.strings.append(raw[:end])
                i = end + len(open_quote)
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
                    open_quote = q
                    i = L
                    break
                ln.strings.append(raw[i + len(q):j])
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
        else:
            ln.blocks = tuple((k, nm) for _, k, nm in stack)
        lines.append(ln)
    return lines


def block_kind(stripped):
    """(kind, name) of a block header such as `label start:` or `menu:`."""
    if PYTHON_HEADER.match(stripped):
        return ("python", "")
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


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check_content.py",
        description="Static content checks (PHASE1_DESIGN.md 8.4).",
        epilog="Prints file:line: rule: text; exits 1 on findings.")
    ap.add_argument("--all", action="store_true", help="every rule (the default)")
    for r in RULES:
        ap.add_argument("--" + r, dest=r.replace("-", "_"), action="store_true")
    ap.add_argument("--include-phase4", action="store_true",
                    help="also list the narration-person findings that section 5.4 "
                         "exempts (the PHASE4_YOU table)")
    ap.add_argument("files", nargs="*", help=".rpy files or folders (default: game/)")
    args = ap.parse_args(argv)

    chosen = [r for r in RULES if getattr(args, r.replace("-", "_"))]
    if args.all or not chosen:
        chosen = list(RULES)

    files = collect(args.files or [GAME])
    missing = [p for p in files if not os.path.isfile(p)]
    if missing:
        for p in missing:
            print("check_content.py: no such file: " + p, file=sys.stderr)
        return 2

    cache = {}
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

    order = {os.path.realpath(p): i for i, p in enumerate(files)}
    findings.sort(key=lambda f: (order.get(os.path.realpath(f[0]), 0), f[1], RULES.index(f[2])))
    for path, n, rule, text in findings:
        if len(text) > 200:
            text = text[:197] + "..."
        print("%s:%d: %s: %s" % (shown(path), n, rule, text))

    if exempt:
        n_ex = sum(exempt.values())
        print("check_content: note: narration-person: %d line%s exempt in %d file%s "
              "(section 5.4 keeps the later chapters in \"you\" until phase 4; "
              "--include-phase4 lists them)" % (
                  n_ex, "" if n_ex == 1 else "s",
                  len(exempt), "" if len(exempt) == 1 else "s"), file=sys.stderr)

    counts = {}
    for f in findings:
        counts[f[2]] = counts.get(f[2], 0) + 1
    if findings:
        summary = ", ".join("%s %d" % (r, counts[r]) for r in RULES if r in counts)
        print("check_content: %d finding%s in %d file%s (%s)" % (
            len(findings), "" if len(findings) == 1 else "s",
            len(files), "" if len(files) == 1 else "s", summary), file=sys.stderr)
        return 1
    print("check_content: clean (%s; %d file%s)" % (
        ", ".join(chosen), len(files), "" if len(files) == 1 else "s"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
