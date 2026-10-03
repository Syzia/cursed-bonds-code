################################################################################
## Cursed Bonds — grades, merit and per-character stats.
##
## WP2 owns this file (PHASE1_DESIGN.md 3.4, 4.10, 3.12 orders 10/20/30).
##
##   The ladder      GRADES / GRADE_ORDER, grade_key / grade_rank / grade_label,
##                   the player's caps and slots (Grade 4's while unassessed, D16)
##   Merit           add_merit, merit_progress, next_grade_text
##   Promotion       promote (never lowers; logged; toasted; NPC remarks, D12)
##   Everyone else   NPC_BASE + npc_state: stats are base + a growth bonus, so
##                   they never drop; xp is cumulative (D21). grow_everyone runs
##                   each new day; train_together adds xp when you work together.
##   The grade card  screen grade_card / label show_grade_card
##
## Balance numbers live in the tables at the top, so tuning never touches code.
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

    ## How the next grade is reached, after the merit (next_grade_text).
    GRADE_HOW = {
        "g3": "then a promotion mission — Maki will watch.",
        "g2": "then a Grade 1's word.",
        "s1": "then a recommendation.",
        "g1": "Two Grade 1 recommendations. Arc Two.",
    }

    ## A legacy enemy grade is a literal number.
    _LEGACY_INT_GRADE = {4: "g4", 3: "g3", 2: "g2", 1: "g1", 0: "sp"}

    ## NPC base stats (3.4): grade, reserve, control, output, xp a day, the
    ## highest grade they reach in Arc One. student=True: a Tokyo student
    ## (pick_team). hidden=True: registered, shown once met.
    NPC_BASE = {
        "yuji":    dict(grade="g4", reserve=110, control=28, output=62, rate=3, max_grade="g2", student=True),
        "megumi":  dict(grade="g2", reserve=150, control=58, output=44, rate=2, max_grade="s1", student=True),
        "nobara":  dict(grade="g3", reserve=120, control=46, output=50, rate=2, max_grade="g2", student=True),
        "maki":    dict(grade="g4", reserve=0,   control=30, output=88, rate=2, max_grade="g4", student=True,
                        restricted=True, note="Heavenly Restriction — and the Zenin keep her grade low"),
        "panda":   dict(grade="g2", reserve=160, control=42, output=70, rate=1, max_grade="s1", student=True),
        "toge":    dict(grade="s1", reserve=170, control=62, output=56, rate=1, max_grade="s1", student=True),
        "gojo":    dict(grade="sp", reserve=None, control=None, output=None, rate=0, max_grade="sp", off_scale=True),
        "yaga":    dict(grade="g1", reserve=220, control=80, output=78, rate=0, max_grade="g1", role="Principal"),
        "utahime": dict(grade="s1", reserve=200, control=72, output=50, rate=0, max_grade="s1", role="Kyoto teacher"),
        "shoko":   dict(grade=None, reserve=180, control=90, output=10, rate=0, max_grade=None, role="Doctor"),
        "ijichi":  dict(grade=None, reserve=60,  control=30, output=8,  rate=0, max_grade=None, role="Assistant manager"),
        "nanami":  dict(grade="g1", reserve=None, control=None, output=None, rate=0, max_grade="g1", hidden=True),
        "todo":    dict(grade="g1", reserve=None, control=None, output=None, rate=0, max_grade="g1", hidden=True),
        "mei_mei": dict(grade="g1", reserve=None, control=None, output=None, rate=0, max_grade="g1", hidden=True),
        "miwa":    dict(grade="g3", reserve=None, control=None, output=None, rate=0, max_grade="g3", hidden=True),
        "yuta":    dict(grade="sp", reserve=None, control=None, output=None, rate=0, max_grade="sp", hidden=True,
                        off_scale=True),
    }

    ## NPC growth (D21). Cumulative xp to reach each grade; the growth bonus on
    ## every stat is min(NPC_BONUS_MAX, xp // NPC_XP_PER_POINT).
    PROMO_XP = {"g3": 40, "g2": 130, "s1": 290}
    NPC_XP_PER_POINT = 6
    NPC_BONUS_MAX = 30

    ## The highest grade a student can be promoted to, by how many acts are
    ## complete (acts_done()). None: no promotions yet.
    ACT_STUDENT_CAP = {0: None, 1: "g3", 2: "g2", 3: "g2", 4: "s1", 5: "s1"}

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
        """WP2. The player's "stat" or "reserve" cap (Grade 4's while None).
        None at Special Grade, which is off the scale."""
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
        """WP2. (merit, merit needed, next grade key). The need is None when
        the next grade isn't reached by merit, and the key None at the top."""
        nxt = _next_key()
        return (store.merit, merit_needed(nxt) if nxt else None, nxt)

    def next_grade_text():
        """WP2. The Stats tab's promotion line, e.g. "Merit 34/60, then a
        promotion mission — Maki will watch." Empty at the top of the scale."""
        if store.grade is None:
            return "Not yet assessed. Roll call comes first."
        m, need, nxt = merit_progress()
        if not nxt:
            return ""
        how = GRADE_HOW.get(nxt, "")
        if need is None:
            return "%s: %s" % (GRADES[nxt]["name"], how)
        if m >= need:
            ## The merit is there: only the last step is left.
            if how.startswith("then "):
                how = how[len("then "):]
            return ("Merit %d/%d. Ready: %s" % (m, need, how)).strip()
        return ("Merit %d/%d, %s" % (m, need, how)).strip()

    def grade_opens_text(key):
        """WP2. What a grade opens, for the grade card: "Board: Grade 3 jobs ·
        Reserve up to 140 · 2 talisman slots"."""
        g = GRADES[grade_key(key) or "g4"]
        reserve = ("Reserve up to %d" % g["reserve"]) if g["reserve"] is not None else "Reserve off the scale"
        slots = "%d talisman slot%s" % (g["slots"], "" if g["slots"] == 1 else "s")
        return "Board: %s jobs · %s · %s" % (g["name"], reserve, slots)

    ## Merit --------------------------------------------------------------------

    def add_merit(n, why=""):
        """WP2. Add merit, with a toast (kind grade): "Merit +30 — The Sun Mall"."""
        if not n:
            return
        store.merit += n
        text = "Merit %+d" % n
        if why:
            text += " — " + why
        toast(text, "grade", None, n)

    def raise_reserve(n):
        """WP2. Raise ce_max by n, up to the grade's reserve cap; never lowers
        (a reserve already above the cap stays). Replaces every hard-coded
        ce_max = min(...). Returns how much it rose."""
        if n <= 0:
            return 0
        cap = grade_cap("reserve")
        before = store.ce_max
        if cap is None:
            store.ce_max = before + n
        elif before < cap:
            store.ce_max = min(cap, before + n)
        return store.ce_max - before

    ## Promotion ----------------------------------------------------------------

    def _npc(who):
        ## who's growth record, made on first use (npc_state is saved state).
        st = store.npc_state.get(who)
        if st is None:
            st = store.npc_state[who] = dict(grade=NPC_BASE.get(who, {}).get("grade"), xp=0, promoted_day=None)
        else:
            ## A record from the WP0 stub held only "grade".
            if "grade" not in st:
                st["grade"] = NPC_BASE.get(who, {}).get("grade")
            if "xp" not in st:
                st["xp"] = 0
            if "promoted_day" not in st:
                st["promoted_day"] = None
        return st

    def _npc_grade(who):
        st = store.npc_state.get(who)
        if st is not None and "grade" in st:
            return st["grade"]
        return NPC_BASE.get(who, {}).get("grade")

    def _who_name(who):
        c = CAST.get(who)
        if c:
            return c["short"]
        return who.replace("_", " ").title()

    def promote(who, key, why="", quiet=False):
        """WP2. Promote the player ("mc") or an NPC to the grade key. It never
        lowers a grade. A promotion is logged in promotions_log and toasted
        (kind grade) unless quiet; an NPC's also leaves a remark for the next
        Talk (pending_remarks, D12). Returns True if the grade rose."""
        k = grade_key(key)
        if k is None:
            return False
        if who == "mc":
            cur = store.grade
            if grade_rank(cur) >= GRADES[k]["rank"]:
                ## Already there or above. A legacy int becomes its key.
                if grade_key(cur) == k and cur != k:
                    store.grade = k
                return False
            store.grade = k
        else:
            st = _npc(who)
            if grade_rank(st["grade"]) >= GRADES[k]["rank"]:
                return False
            st["grade"] = k
            st["promoted_day"] = store.day
            store.pending_remarks[who] = True
        store.promotions_log.append(dict(day=store.day, who=who, grade=k, why=why))
        if not quiet:
            if who == "mc":
                toast("Promoted to %s" % GRADES[k]["name"], "grade")
            else:
                toast("%s — promoted to %s" % (_who_name(who), GRADES[k]["name"]), "grade", who)
        return True

    def recent_promotion(who, days=3):
        """WP2. True if who ("mc" or an NPC) was promoted within the last
        `days` days: today counts, and so do the days-1 days before it."""
        for e in store.promotions_log:
            if e.get("who") == who and 0 <= store.day - e.get("day", -999) < days:
                return True
        return False

    def pop_remark(who):
        """WP2. True once after who's promotion (the next Talk remarks on it);
        clears the pending remark."""
        return bool(store.pending_remarks.pop(who, False))

    ## Everyone else's numbers --------------------------------------------------

    def npc_stats(who):
        """WP2. dict(grade, ce_max, control, output, off_scale, restricted,
        role, note, xp, max_grade, hidden) for an NPC. Each number is its base
        plus min(30, xp // 6), so it never drops; None where the base is None
        (off the scale, or not yet known). Maki's Heavenly Restriction keeps
        her reserve at its base. Reading never changes saved state."""
        b = NPC_BASE.get(who, {})
        st = store.npc_state.get(who, {})
        xp = st.get("xp", 0)
        bonus = min(NPC_BONUS_MAX, xp // NPC_XP_PER_POINT)
        restricted = b.get("restricted", False)

        def grown(base, grows=True):
            if base is None:
                return None
            return base + (bonus if grows else 0)

        return dict(grade=_npc_grade(who),
                    ce_max=grown(b.get("reserve"), not restricted),
                    control=grown(b.get("control")),
                    output=grown(b.get("output")),
                    off_scale=b.get("off_scale", False),
                    restricted=restricted,
                    role=b.get("role", ""),
                    note=b.get("note", ""),
                    xp=xp,
                    max_grade=b.get("max_grade"),
                    hidden=b.get("hidden", False))

    def _grows(who):
        return NPC_BASE.get(who, {}).get("rate", 0) > 0

    def train_together(who, n=3, stat=None):
        """WP2. Working with someone grows them: a student gains 2*n xp (their
        promotion, if due, comes overnight). With stat, the player also gets
        gain(stat, 1). Callers: sparring and act_train (3, "output"),
        act_study (2, "insight"), act_swim / act_walk (1), board jobs (6)."""
        if who and _grows(who):
            _npc(who)["xp"] += 2 * n
        if stat:
            gain(stat, 1)

    def _student_cap():
        try:
            done = int(acts_done())
        except Exception:
            done = 0
        done = max(0, min(done, max(ACT_STUDENT_CAP)))
        return ACT_STUDENT_CAP.get(done)

    def grow_everyone():
        """WP2. New-day hook: every rostered NPC with rate > 0 gains rate xp
        plus a 0-or-1 jitter seeded by day and name. One grade a night at
        most, when their xp reaches PROMO_XP, within their max grade and
        within ACT_STUDENT_CAP[acts_done()] (D21)."""
        import random
        import zlib
        cap = _student_cap()
        order = [w for w in ROSTER_ORDER if w in NPC_BASE] + sorted(w for w in NPC_BASE if w not in ROSTER_ORDER)
        for who in order:
            if who not in store.roster or not _grows(who):
                continue
            b = NPC_BASE[who]
            st = _npc(who)
            jitter = random.Random(store.day * 1009 + zlib.crc32(who.encode("utf-8"))).randint(0, 1)
            st["xp"] += b["rate"] + jitter
            nxt = _next_key(st["grade"]) if st["grade"] else None
            if (nxt and cap and nxt in PROMO_XP and st["xp"] >= PROMO_XP[nxt]
                    and GRADES[nxt]["rank"] <= grade_rank(b.get("max_grade"))
                    and GRADES[nxt]["rank"] <= grade_rank(cap)):
                promote(who, nxt, "Promoted on their own record")

    register_new_day(grow_everyone, order=20)

    def sorcerer_power(who):
        """WP2. A rough strength number. The player ("mc"):
        (control+output)/2 + insight/4 + 6 * Last Light's tier. An NPC:
        (control+output)/2, or their grade's stat cap where their numbers
        aren't known yet. Off the scale (Gojo): 999."""
        if who == "mc":
            return (store.control + store.output) / 2.0 + store.insight / 4.0 + 6 * tech_tier()[0]
        s = npc_stats(who)
        if s["off_scale"]:
            return 999
        if s["control"] is None or s["output"] is None:
            k = grade_key(s["grade"])
            return float(GRADES[k]["stat"] or 0) if k else 0.0
        return (s["control"] + s["output"]) / 2.0

    def pick_team(n, min_key=None):
        """WP2. The n rostered Tokyo students with the highest grade, then the
        highest bond (D12: grade is who gets picked). min_key drops anyone
        below that grade. The player is not in the list."""
        floor = grade_rank(min_key) if min_key else -1
        pool = []
        for who in NPC_BASE:
            if not NPC_BASE[who].get("student") or who not in store.roster:
                continue
            r = grade_rank(_npc_grade(who))
            if r < floor:
                continue
            order = ROSTER_ORDER.index(who) if who in ROSTER_ORDER else 99
            pool.append((-r, -store.bonds.get(who, 0), order, who))
        pool.sort()
        return [p[3] for p in pool[:max(0, n)]]

    ## Migrations (3.12) --------------------------------------------------------

    def _migrate_10():
        """WP2, migration 10. Every technique becomes Last Light ("timestop")
        and the old one is remembered as flag technique_was_<old>. A save that
        had the old output technique also gets control = max(control, output),
        so Last Light's tier (which scales off control) doesn't drop.
        Idempotent."""
        old = store.technique
        if old == "timestop":
            return
        if old == "emberfall":  # legacy-technique
            store.control = max(store.control, store.output)
        if isinstance(old, str) and old:
            flag("technique_was_" + old)
        store.technique = "timestop"

    def _migrate_20():
        """WP2, migration 20. The player's grade becomes a key: int 3 -> "g3";
        any other int (the old default 4) -> "g4" if roll call happened, else
        None (D16). None after roll call -> "g4" too (roll call always
        assesses). A key stays. Idempotent. A finished st_roll_call counts as
        roll call: migration 40 backfills the flag later, so a save that left
        roll call through a recovery would otherwise wait a load for it.
        play_event marks st_roll_call done before the scene plays, so a save
        made inside roll call, before its assessment line, reaches g4 here;
        the scene's promote() then does nothing. So whenever this moves the
        player to "g4" it also logs the assessment, once."""
        rc = has_flag("roll_call") or "st_roll_call" in store.done_events
        g = store.grade
        if g is None:
            if rc:
                store.grade = "g4"
                _migrate_20_log()
            return
        if isinstance(g, str) and g in GRADES:
            return
        if isinstance(g, int) and not isinstance(g, bool) and g == 3:
            store.grade = "g3"
        else:
            store.grade = "g4" if rc else None
            if rc:
                _migrate_20_log()

    def _migrate_20_log():
        """Migration 20's roll-call row: added only if the player has none."""
        if not any(p.get("who") == "mc" for p in store.promotions_log):
            store.promotions_log.append(dict(day=store.day, who="mc", grade="g4",
                                             why="Assessed at roll call"))

    def _migrate_30():
        """WP2, migration 30. hp_max from today's stats; a save left at 0 HP
        gets it back. Idempotent."""
        refresh_vitals()
        if store.hp <= 0:
            store.hp = store.hp_max

    register_migration(10, _migrate_10, "technique -> timestop (Last Light)")
    register_migration(20, _migrate_20, "grade int -> key")
    register_migration(30, _migrate_30, "refresh vitals, restore 0 HP")

    ## Validator ------------------------------------------------------------------

    def _validate_grades():
        out = []
        if sorted(GRADE_ORDER) != sorted(GRADES):
            out.append("GRADE_ORDER and GRADES disagree")
        for i, k in enumerate(GRADE_ORDER):
            if GRADES.get(k, {}).get("rank") != i:
                out.append("GRADES[%r] rank is not its place in GRADE_ORDER" % k)
        for who, b in NPC_BASE.items():
            for f in ("grade", "max_grade"):
                v = b.get(f)
                if v is not None and v not in GRADES:
                    out.append("NPC_BASE[%r] %s %r is not a grade key" % (who, f, v))
            if grade_rank(b.get("max_grade")) < grade_rank(b.get("grade")):
                out.append("NPC_BASE[%r] max_grade is below its grade" % who)
        for k in list(PROMO_XP) + [v for v in ACT_STUDENT_CAP.values() if v]:
            if k not in GRADES:
                out.append("%r in PROMO_XP / ACT_STUDENT_CAP is not a grade key" % k)
        for key, e in ENEMIES.items():
            if e.get("grade") not in GRADES:
                out.append("ENEMIES[%r] grade %r is not a grade key" % (key, e.get("grade")))
            for tell in e.get("tells", ()):
                if tell[1] not in ANSWERS:
                    out.append("ENEMIES[%r] tell kind %r has no answer" % (key, tell[1]))
        if list(MOVES) != ["timestop"]:
            out.append("MOVES should hold only 'timestop', has %r" % list(MOVES))
        if list(TECHNIQUES) != ["timestop"]:
            out.append("TECHNIQUES should hold only 'timestop', has %r" % list(TECHNIQUES))
        ntiers = len(TECHNIQUES["timestop"]["tiers"])
        ids = set()
        for m in MOVES.get("timestop", ()):
            if not (0 <= m.get("tier", -1) < ntiers):
                out.append("move %r tier %r is not a Last Light tier" % (m.get("id"), m.get("tier")))
            if m.get("id") in ids:
                out.append("move id %r twice" % m.get("id"))
            ids.add(m.get("id"))
        n10 = len([m for m in MIGRATIONS if m[0] == 10])
        if n10 != 1:
            out.append("%d migrations registered at order 10 (want 1)" % n10)
        return out

    register_validator(_validate_grades)


## Grade colours (phase 2: PHASE2_DESIGN.md D15, D16, 4.8) #####################
##
## P0 wrote these, final; the sites that use them belong to their owners (4.8).
## One colour a tier: Semi-Grade 1 shares Grade 1's red. Special Grade is a
## slow oil-slick sheen (gui/grade_sheen.png, panned by the wall clock) on a
## dark base; until that strip exists the fill is a flat gui.grade_sp.

init -1 python:
    import time as _grade_time

    GRADE_TIER = {"g4": "g4", "g3": "g3", "g2": "g2", "s1": "g1", "g1": "g1", "sp": "sp"}

    GRADE_SHEEN = "gui/grade_sheen.png"     # 1024x64, tileable
    GRADE_SHEEN_LOOP = 14.0                 # seconds for one pass

    def grade_tier(v):
        """P0 (sb_grades.rpy), final. The colour tier of a grade: "g4", "g3",
        "g2", "g1" (Grade 1 and Semi-Grade 1) or "sp"; None when ungraded.
        v is a grade key, a legacy enemy int (0 is Special Grade) or None."""
        return GRADE_TIER.get(grade_key(v))

    def grade_color(v):
        """P0 (sb_grades.rpy), final. The grade's colour as a hex str;
        gui.dim when ungraded. Special Grade gives gui.grade_sp, for the
        places where only a string fits."""
        t = grade_tier(v)
        if t is None:
            return gui.dim
        return getattr(gui, "grade_" + t)

    def grade_is_special(v):
        """P0 (sb_grades.rpy), final. bool: True for Special Grade."""
        return grade_tier(v) == "sp"

    def grade_has_sheen():
        """P0 (sb_grades.rpy). bool: the Special Grade strip is on disk."""
        return bool(renpy.loadable(GRADE_SHEEN))

    def grade_sheen_fn(trans, st, at):
        """P0 (sb_grades.rpy). The transform function that pans the sheen: a
        512-wide window slides along the strip once every GRADE_SHEEN_LOOP
        seconds, by the wall clock. Returns VIEW_TICK as the redraw delay,
        or None (and a still strip) when view_motion() is False. Top-level,
        so nothing that carries it is a closure (R10)."""
        if not view_motion():
            trans.crop = (0, 0, 512, 64)
            return None
        f = (_grade_time.time() % GRADE_SHEEN_LOOP) / GRADE_SHEEN_LOOP
        trans.crop = (int(1024 * f), 0, 512, 64)
        return VIEW_TICK

    def grade_fill(v):
        """P0 (sb_grades.rpy), final. A displayable that fills a grade chip:
        the tier's flat colour; the sheen on its dark base for Special Grade
        (flat gui.grade_sp until gui/grade_sheen.png exists); the ghost
        panel when ungraded. Build it in the line that uses it and never
        store it: screen scope is saved (R10)."""
        t = grade_tier(v)
        if t is None:
            return Frame("gui/panel_ghost.png", 4, 4)
        if t != "sp":
            return Solid(getattr(gui, "grade_" + t))
        if not grade_has_sheen():
            return Solid(gui.grade_sp)
        ## Two copies side by side, so the sliding window never runs off the end.
        strip = Tile(GRADE_SHEEN, xysize=(2048, 64))
        return Fixed(Solid(gui.grade_sp_base),
                     Frame(Transform(strip, function=grade_sheen_fn, crop=(0, 0, 512, 64), alpha=0.85)))

    def grade_text_color(v):
        """P0 (sb_grades.rpy). The colour of a chip's text: dark on a flat
        fill, light on the Special Grade sheen, dim when ungraded."""
        t = grade_tier(v)
        if t is None:
            return gui.dim
        if t == "sp" and grade_has_sheen():
            return gui.paper
        return gui.ink


## P0 (sb_grades.rpy), final. A filled chip with the grade's name: "GRADE 2".
## v is a grade key, a legacy int or None; text replaces the name ("Off the
## scale", a role for someone with no grade); dim=True draws it at alpha 0.45.
screen grade_chip(v, size=13, text=None, dim=False):
    $ _grade_txt = (text or grade_label(v)).upper()
    frame at Transform(alpha=(0.45 if dim else 1.0)):
        background grade_fill(v)
        padding (10, 3)
        text _grade_txt:
            substitute False
            font gui.body_bold_font
            color grade_text_color(v)
            size size
            kerning 1


## Grade card (4.10) ############################################################

## WP2. The ASSESSED / PROMOTED card, centred, 900x420.
screen grade_card(key, kicker):

    zorder 90

    ## D16: an unset grade shows Grade 4's card, never "ASSESSED / Not yet assessed".
    $ _gl = grade_label(key or "g4")
    $ _opens = grade_opens_text(key or "g4")

    add Solid(gui.ink) alpha 0.5

    frame:
        style "jjk_panel"
        xalign 0.5
        yalign 0.5
        xysize (900, 420)

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 18

            hbox:
                xalign 0.5
                spacing 16
                use seal("級", 44)
                text "[kicker]":
                    yalign 0.5
                    font gui.body_medium_font
                    color gui.gold
                    size 22
                    kerning 6

            text "[mc_surname] [mc_name]":
                xalign 0.5
                color gui.dim
                size 26

            ## Phase 2 (4.8): the grade in its own colour; Special Grade sits
            ## on a rule of the sheen.
            text "[_gl]":
                xalign 0.5
                font gui.display_font
                color grade_color(key or "g4")
                size 64

            if grade_is_special(key):
                frame:
                    xalign 0.5
                    xysize (560, 6)
                    padding (0, 0)
                    background grade_fill(key)
            else:
                use rule(560)

            text "[_opens]":
                xalign 0.5
                text_align 0.5
                color gui.dim
                size 21

## WP2. Shows the card for three seconds (a click ends it early), then
## dissolves it away. The quick menu is hidden while it shows (same save and
## restore as a fight), so nothing is clickable under the backdrop.
label show_grade_card(key, kicker="PROMOTED"):
    $ key = key or "g4"
    $ quick_menu_before_card = quick_menu
    $ quick_menu = False
    show screen grade_card(key, kicker)
    with dissolve
    $ renpy.pause(3.0)
    hide screen grade_card
    with dissolve
    $ quick_menu = quick_menu_before_card
    return


default merit = 0
default merit_granted = set()     # keys paid once: "mission:m_sunmall", "ch5_recommendation"…
default npc_state = {}            # who -> dict(grade, xp, promoted_day), made on first use
default promotions_log = []       # dict(day, who, grade, why), the player's and everyone's
default quick_menu_before_card = True   # set while the grade card shows
default pending_remarks = {}      # who -> True until the next Talk remarks on their promotion
