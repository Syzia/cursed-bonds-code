################################################################################
## Cursed Bonds — grades, merit and per-character stats.
##
## WP2 owns this file (PHASE1_DESIGN.md 3.4, 4.10). WP0 wrote the frozen
## signatures below as working simple versions, so other packages can code
## against them: the ladder and the lookups work; promotion, growth and the
## grade card are minimal.
################################################################################

init -1 python:

    ## The ladder (3.4). reserve / stat are the caps; merit is what it takes
    ## to reach the grade; slots are talisman slots.
    GRADE_ORDER = ["g4", "g3", "g2", "s1", "g1", "sp"]

    GRADES = {
        "g4": dict(name="Grade 4",       rank=0, reserve=100,  stat=40,   slots=1, merit=None, off_scale=False),
        "g3": dict(name="Grade 3",       rank=1, reserve=140,  stat=55,   slots=2, merit=60,   off_scale=False),
        "g2": dict(name="Grade 2",       rank=2, reserve=180,  stat=70,   slots=3, merit=150,  off_scale=False),
        "s1": dict(name="Semi-Grade 1",  rank=3, reserve=220,  stat=85,   slots=4, merit=260,  off_scale=False),
        "g1": dict(name="Grade 1",       rank=4, reserve=260,  stat=100,  slots=4, merit=None, off_scale=False),
        "sp": dict(name="Special Grade", rank=5, reserve=None, stat=None, slots=4, merit=None, off_scale=True),
    }

    ## A legacy enemy grade is a literal number.
    _LEGACY_INT_GRADE = {4: "g4", 3: "g3", 2: "g2", 1: "g1", 0: "sp"}

    ## NPC base stats (3.4): grade, reserve, control, output, xp/day, max grade.
    NPC_BASE = {
        "yuji":    dict(grade="g4", reserve=110, control=28, output=62, rate=3, max_grade="g2"),
        "megumi":  dict(grade="g2", reserve=150, control=58, output=44, rate=2, max_grade="s1"),
        "nobara":  dict(grade="g3", reserve=120, control=46, output=50, rate=2, max_grade="g2"),
        "maki":    dict(grade="g4", reserve=0,   control=30, output=88, rate=2, max_grade="g4", restricted=True,
                        note="Heavenly Restriction — and the Zenin keep her grade low"),
        "panda":   dict(grade="g2", reserve=160, control=42, output=70, rate=1, max_grade="s1"),
        "toge":    dict(grade="s1", reserve=170, control=62, output=56, rate=1, max_grade="s1"),
        "gojo":    dict(grade="sp", reserve=None, control=None, output=None, rate=0, max_grade="sp", off_scale=True),
        "yaga":    dict(grade="g1", reserve=220, control=80, output=78, rate=0, max_grade="g1", role="Principal"),
        "utahime": dict(grade="s1", reserve=200, control=72, output=50, rate=0, max_grade="s1", role="Kyoto teacher"),
        "shoko":   dict(grade=None, reserve=180, control=90, output=10, rate=0, max_grade=None, role="Doctor"),
        "ijichi":  dict(grade=None, reserve=60,  control=30, output=8,  rate=0, max_grade=None, role="Assistant manager"),
    }

    ## Lookups ------------------------------------------------------------------

    def grade_key(v):
        """WP2. A grade key from a key, a legacy enemy int (4 -> "g4" ...
        0 -> "sp") or None (-> None)."""
        if v is None:
            return None
        if isinstance(v, int) and not isinstance(v, bool):
            return _LEGACY_INT_GRADE.get(v)
        return v if v in GRADES else None

    def grade_rank(v):
        """WP2. 0 for Grade 4 up to 5 for Special Grade; -1 for None or ungraded."""
        k = grade_key(v)
        return GRADES[k]["rank"] if k else -1

    def grade_label(v):
        """WP2. "Grade 3" from a key, an int or None ("Not yet assessed")."""
        if v is None:
            return "Not yet assessed"
        k = grade_key(v)
        return GRADES[k]["name"] if k else str(v)

    def player_grade():
        """WP2. The player's grade: a key, or None before roll call."""
        return store.grade

    def _player_key():
        ## Grade 4's numbers apply while the player is unassessed (D16).
        return grade_key(store.grade) or "g4"

    def grade_cap(kind):
        """WP2. The player's "stat" or "reserve" cap (Grade 4's while None)."""
        return GRADES[_player_key()]["stat" if kind == "stat" else "reserve"]

    def talisman_slots(key=None):
        """WP2. Talisman slots at a grade (default: the player's)."""
        k = grade_key(key) if key is not None else _player_key()
        return GRADES[k or "g4"]["slots"]

    def _next_key(key=None):
        k = grade_key(key) if key is not None else _player_key()
        i = GRADE_ORDER.index(k or "g4") + 1
        if i >= len(GRADE_ORDER) or GRADES[GRADE_ORDER[i]]["off_scale"]:
            return None
        return GRADE_ORDER[i]

    def merit_needed(key=None):
        """WP2. Merit to reach a grade (default: the player's next), or None."""
        if key is None:
            key = _next_key()
        k = grade_key(key)
        return GRADES[k]["merit"] if k else None

    def merit_progress():
        """WP2. (merit, merit needed, next grade key)."""
        nxt = _next_key()
        return (store.merit, merit_needed(nxt) if nxt else None, nxt)

    def next_grade_text():
        """WP2. The Stats tab's promotion line, e.g. "Merit 34/60, then a
        promotion mission — Maki will watch." (WP0 stub: the merit part.)"""
        m, need, nxt = merit_progress()
        if not nxt or need is None:
            return ""
        return "Merit %d/%d" % (m, need)

    ## Merit and promotion --------------------------------------------------------

    def add_merit(n, why=""):
        """WP2. Add merit, with a toast (kind grade). (WP0 stub: adds only.)"""
        store.merit += n

    def promote(who, key, why="", quiet=False):
        """WP2. Promote the player ("mc") or an NPC; never lowers; logged and
        toasted. (WP0 stub: sets the grade.)"""
        if who == "mc":
            store.grade = key
        else:
            store.npc_state.setdefault(who, {})["grade"] = key

    def recent_promotion(who, days=3):
        """WP2. True if who was promoted in the last `days` days. (WP0 stub.)"""
        return False

    def pop_remark(who):
        """WP2. Returns and clears a pending promotion remark. (WP0 stub.)"""
        return False

    def npc_stats(who):
        """WP2. dict(grade, ce_max, control, output, off_scale, restricted,
        role, note) for an NPC. (WP0 stub: the base numbers, no growth.)"""
        b = NPC_BASE.get(who, {})
        grade = store.npc_state.get(who, {}).get("grade", b.get("grade"))
        return dict(grade=grade, ce_max=b.get("reserve"), control=b.get("control"),
                    output=b.get("output"), off_scale=b.get("off_scale", False),
                    restricted=b.get("restricted", False), role=b.get("role", ""),
                    note=b.get("note", ""))

    def train_together(who, n=3, stat=None):
        """WP2. Training with someone grows them (and you, with stat). (WP0 stub: no-op.)"""
        return

    def sorcerer_power(who):
        """WP2. A rough strength number for the player ("mc") or an NPC. (WP0 stub: 10.)"""
        return 10

    def pick_team(n, min_key=None):
        """WP2. The n strongest rostered students (grade rank, then bond). (WP0 stub: [].)"""
        return []

    def raise_reserve(n):
        """WP2. Raise ce_max by n, up to the grade's reserve cap; never lowers.
        Replaces every hard-coded ce_max = min(...). (WP0 stub: uncapped.)"""
        if n > 0:
            store.ce_max += n

    ## Migration 10, interim (WP0 stub) ------------------------------------------

    def _migrate_10_interim():
        """WP2 replaces this with the full migration 10 (3.12), which turns
        every technique into "timestop". Until Last Light exists, the WP0
        stub changes only a technique the game no longer has at all (one
        dropped by the prologue rewrite), so such a save can open the campus
        instead of raising in tech(). It sets flag technique_was_<old>, as
        migration 10 will, and steps aside once another order-10 migration
        is registered."""
        if any(o == 10 and fn is not _migrate_10_interim for o, n, fn in MIGRATIONS):
            return
        old = store.technique
        if old in TECHNIQUES:
            return
        if isinstance(old, str):
            flag("technique_was_" + old)
        store.technique = "timestop"

    register_migration(10, _migrate_10_interim, "unknown technique -> timestop (WP0 interim)")


## Grade card (4.10) ############################################################

## WP2. The ASSESSED / PROMOTED card. (WP0 stub: text only.)
screen grade_card(key, kicker):

    zorder 90

    $ _gl = grade_label(key)

    frame:
        style "jjk_panel"
        xalign 0.5
        yalign 0.5
        vbox:
            spacing 12
            text "[kicker]" style "jjk_label"
            text "[mc_surname] [mc_name]"
            text "[_gl]" style "jjk_head"

## WP2. Shows the card for three seconds. (WP0 stub: returns.)
label show_grade_card(key, kicker="PROMOTED"):
    return


default merit = 0
default npc_state = {}
