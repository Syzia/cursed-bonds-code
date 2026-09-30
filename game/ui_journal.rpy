################################################################################
## Cursed Bonds — the journal.
##
## WP8 (phase 1, PHASE1_DESIGN.md 4.7). One full-screen journal with six tabs:
## People, Missions, Memories, Stats, Equipment and Inventory.
##
##   screen journal(tab="people")   tag menu, its own chrome (not game_menu)
##   screen jjk_status()            use journal("stats")   (kept: old callers)
##   screen jjk_journal()           use journal("people")  (kept: old callers)
##
## How it is opened (D4):
##   - on campus, through the loop: Return(("journal", tab)) from the place
##     view, then `call screen journal(tab)` in the main context. Only there
##     is it `editable`: equipment can change and Arc Two can begin
##     (Return(("arc_two",))).
##   - from the quick menu or the game menu during a scene: ShowMenu("journal"),
##     a menu context. The Equipment tab is read-only there.
##
## The journal only reads other packages' state, through the frozen section 6
## API (grades WP2, missions WP3, board WP4, memories WP5, items WP6, world
## WP1). The helpers below are tolerant of the shapes those return (a record
## may be a dict or an object; a mission list may hold ids or records), so the
## journal keeps drawing whatever order the packages merge in.
##
## The journal's view state (tab, selection, filters) is one dict held in the
## screen, `js`, rather than separate screen variables. The tab bodies are
## screens of their own, and the wrappers `use` the journal, so a plain
## SetScreenVariable would land in the wrong screen's scope; a shared dict
## changed through SetDict works from every one of them.
################################################################################

init python:

    ## The Stats tab's full picture ---------------------------------------------

    def kaito_card_image():
        """WP8. The unlit full picture on the Stats tab: the Yotsuka outfit
        until the campus opens, the uniform after."""
        if has_flag("settled_in"):
            return "images/char/mc_neutral.png"
        return "images/char/mcyotsuka_neutral.png"

    ## Tabs and state -----------------------------------------------------------

    JOURNAL_TABS = [
        ("people",    "人", "People"),
        ("missions",  "任", "Missions"),
        ("memories",  "憶", "Memories"),
        ("stats",     "力", "Stats"),
        ("equipment", "装", "Equipment"),
        ("inventory", "品", "Inventory"),
    ]

    JR_MISSION_FILTERS = [("available", "Available"), ("active", "Active"),
                          ("done", "Done"), ("all", "All")]
    JR_MISSION_SUBS = [("story", "Story"), ("character", "Character"), ("board", "Board")]

    JR_INV_CATS = [("all", "All"), ("keepsake", "Keepsakes"), ("sealing", "Sealing talismans"),
                   ("supply", "Supplies"), ("mission", "Mission items"),
                   ("talisman", "Talismans"), ("tool", "Cursed tools")]

    ## Symbols the interface fonts don't carry (✓, ◌, ∞) come from Ren'Py's own
    ## DejaVu Sans, which ships with every build.
    JR_SYMBOL_FONT = "DejaVuSans.ttf"

    ## The interface fonts with ō and its kin drawn in DejaVu Sans (screens.rpy,
    ## macron_font): the Last Light's "残光 · Zankō", and any title that
    ## carries a macron.
    JR_DISPLAY_FONT = macron_font(gui.display_font)
    JR_BODY_FONT = macron_font(gui.body_font)
    JR_MEDIUM_FONT = macron_font(gui.body_medium_font)
    JR_BOLD_FONT = macron_font(gui.body_bold_font)

    JR_FX_NOTE = "Takes effect in combat from the combat update."

    JR_PERIOD_WORDS = {"Morning": "mornings", "Noon": "noon", "Afternoon": "afternoons",
                       "Evening": "evenings", "Night": "nights"}

    def journal_editable():
        """WP8 (D4). True when the journal was opened from campus, in the
        main context (`call screen journal`); False in a menu context (the
        quick menu or the game menu during a scene), where equipment is
        read-only and Arc Two can't begin."""
        return not renpy.context()._menu

    def journal_state(tab="people"):
        """WP8. A fresh view state for the journal screen."""
        if tab not in [t[0] for t in JOURNAL_TABS]:
            tab = "people"
        return dict(tab=tab, sel=None, mfilter="available", msub="story",
                    mem_mode="person", mem_who=None, inv_cat="all", inv_sel=None,
                    pick=None, collapsed={})

    def jr_toggle(js, key, item):
        """Flip js[key][item] (the collapsed act headers)."""
        d = js.setdefault(key, {})
        d[item] = not d.get(item, False)

    def jr_go(js, **kw):
        """Change several view-state keys at once (a tab jump from a link)."""
        js.update(kw)
        if "tab" in kw:
            js["pick"] = None

    ## Reading other packages' records ------------------------------------------

    def jr_get(rec, key, default=None):
        """A field of a record that may be a dict or an object."""
        if rec is None:
            return default
        if isinstance(rec, dict):
            return rec.get(key, default)
        return getattr(rec, key, default)

    def jr_clip(s, n):
        """Cut a string to n characters with an ellipsis."""
        s = "" if s is None else str(s)
        return s if len(s) <= n else s[:max(0, n - 1)].rstrip() + "…"

    def jr_place_name(loc):
        """A place key as its name; anything else as it is."""
        if isinstance(loc, (tuple, list)):
            return " / ".join(jr_place_name(l) for l in loc)
        if loc in LOCATIONS:
            return LOCATIONS[loc]["name"]
        if isinstance(loc, str) and "_" in loc:
            return loc.replace("_", " ").title()
        return "" if loc is None else str(loc)

    def jr_periods_text(periods):
        """("Morning", "Noon") -> "mornings and noon"."""
        if not periods:
            return ""
        if isinstance(periods, str):
            periods = (periods,)
        words = [JR_PERIOD_WORDS.get(p, str(p).lower()) for p in periods]
        if len(words) == 1:
            return words[0]
        return ", ".join(words[:-1]) + " and " + words[-1]

    ## Short names for people who have a JOURNAL_CAST entry but no CAST entry
    ## (the way the others call them), used when the entry has no "short".
    JR_SHORT = {"nanami": "Nanami", "todo": "Todo", "miwa": "Miwa",
                "mei_mei": "Mei Mei", "yuta": "Yuta"}

    def jr_cast_entry(who):
        """This person's JOURNAL_CAST entry, or None."""
        for e in JOURNAL_CAST:
            if jr_get(e, "who") == who:
                return e
        return None

    def jr_short(who):
        """A person's short name: CAST's, the JOURNAL_CAST entry's "short",
        JR_SHORT, then the last word of the entry's full name."""
        c = CAST.get(who)
        if c:
            return c.get("short", who)
        e = jr_cast_entry(who)
        if jr_get(e, "short"):
            return jr_get(e, "short")
        if who in JR_SHORT:
            return JR_SHORT[who]
        if jr_get(e, "name"):
            return jr_get(e, "name").split()[-1]
        return str(who).replace("_", " ").title()

    def jr_color(who):
        c = CAST.get(who)
        if c:
            return c.get("color", gui.dim)
        for e in JOURNAL_CAST:
            if jr_get(e, "who") == who and jr_get(e, "color"):
                return jr_get(e, "color")
        return gui.dim

    ## People -------------------------------------------------------------------

    def journal_met(entry):
        """WP8. Whether a JOURNAL_CAST entry has been met: its rule is
        ("roster",), ("flag", name) or ("always",) (a callable or a bool
        also work). Unknown rules fall back to "in the roster"."""
        who = jr_get(entry, "who")
        rule = jr_get(entry, "met", ("roster",))
        if callable(rule):
            return bool(rule())
        if isinstance(rule, bool):
            return rule
        if isinstance(rule, str):
            rule = (rule,)
        kind = rule[0] if rule else "roster"
        if kind == "always":
            return True
        if kind == "flag" and len(rule) > 1:
            return has_flag(rule[1])
        ## The default roster already holds the first-years, Gojo, Yaga,
        ## Ijichi and Shoko, so before the campus opens a roster rule only
        ## counts once the prologue has reached the step that introduces them.
        if not jr_on_campus():
            step = JR_PROLOGUE_MEET.get(who)
            return bool(step) and jr_prologue_index() >= jr_step_index(step)
        return who in store.roster

    ## The prologue step that introduces each person the default roster
    ## already holds (anyone else waits for the campus).
    JR_PROLOGUE_MEET = {"gojo": "ch1_gojo", "ijichi": "ch2_arrival", "yaga": "ch2_yaga",
                        "yuji": "ch2_first_years", "megumi": "ch2_first_years",
                        "nobara": "ch2_first_years"}

    def jr_step_index(step):
        steps = [s for s, c in PROLOGUE_STEPS]
        return steps.index(step) if step in steps else len(steps)

    def jr_prologue_index():
        """WP8. Where this save is in the prologue, as an index into
        PROLOGUE_STEPS: len(PROLOGUE_STEPS) once the campus is open. Reads
        story_point, or legacy_story_point() for a save without one; a
        chapter label counts as its first step, anything unknown as the start."""
        steps = [s for s, c in PROLOGUE_STEPS]
        if has_flag("settled_in"):
            return len(steps)
        sp = getattr(store, "story_point", None)
        try:
            sp = sp or legacy_story_point()
        except Exception:
            sp = None
        if sp == "sandbox":
            return len(steps)
        if sp in steps:
            return steps.index(sp)
        chapters = [c for s, c in PROLOGUE_STEPS]
        if sp in chapters:
            return chapters.index(sp)
        return 0

    def jr_on_campus():
        """WP8. True from arc_one_open on (settled_in, or a save the recovery
        sends to arc_one_open)."""
        return jr_prologue_index() >= jr_step_index("arc_one_open")

    def jr_has_art(who):
        return renpy.loadable("images/side/%s_neutral.png" % who)

    def jr_portrait(who, black=False):
        """The side portrait at zoom 0.9, cropped to one height (324x162).
        black=True gives the unmet silhouette."""
        path = "images/side/%s_neutral.png" % who
        if black:
            return Transform(path, crop=(0, 0, 360, 180), zoom=0.9,
                             matrixcolor=TintMatrix("#000000"), alpha=0.85)
        return Transform(path, crop=(0, 0, 360, 180), zoom=0.9)

    def journal_cast():
        """WP8. The People tab's cards, in JOURNAL_CAST order: dicts of who,
        name, color, role, hint, met, art."""
        out = []
        for e in JOURNAL_CAST:
            who = jr_get(e, "who")
            c = CAST.get(who, {})
            name = jr_get(e, "name") or c.get("name") or str(who).replace("_", " ").title()
            out.append(dict(
                who=who, name=name,
                color=jr_get(e, "color") or c.get("color") or gui.dim,
                role=jr_get(e, "role") or c.get("year", ""),
                hint=jr_get(e, "hint", "") or "",
                met=journal_met(e),
                art=jr_has_art(who)))
        return out

    def jr_grade_line(who, role=""):
        """"Grade 2", "Off the scale", or the role for the ungraded."""
        try:
            st = npc_stats(who) or {}
        except Exception:
            st = {}
        if st.get("off_scale"):
            return "Off the scale"
        if st.get("grade"):
            return grade_label(st.get("grade"))
        return st.get("role") or role or CAST.get(who, {}).get("year", "")

    def jr_next(who):
        """"Next: <text> — <where>" from next_for, or ""."""
        try:
            nf = next_for(who)
        except Exception:
            nf = None
        if not nf:
            return ""
        if isinstance(nf, (tuple, list)):
            text = nf[0] if nf else ""
            where = nf[1] if len(nf) > 1 else None
        else:
            text, where = str(nf), None
        where = jr_place_name(where)
        if where:
            return "Next: %s — %s" % (text, where)
        return "Next: %s" % text

    def jr_promotions(who):
        """[(day, grade key, why)] from promotions_log, oldest first."""
        out = []
        for p in (getattr(store, "promotions_log", None) or []):
            if jr_get(p, "who") == who:
                out.append((jr_get(p, "day"), jr_get(p, "grade"), jr_get(p, "why", "")))
        return out

    def jr_recently_promoted(who):
        try:
            return bool(recent_promotion(who))
        except Exception:
            return False

    def jr_thread(who):
        """(title, [stages learned]) of this person's open thread, or None."""
        for tid in THREAD_ORDER:
            T = THREADS[tid]
            if T["who"] == who:
                st = thread_stage(tid)
                if st >= 0:
                    return (T["title"], T["stages"][:st + 1], thread_done(tid))
        return None

    def jr_aff_note(who):
        """The affection-cap note under the heart meter."""
        if is_together(who):
            return "Together"
        cap = aff_cap(who)
        if cap >= AFF_BASE_MAX:
            return ""
        need = None
        for need_bond, allowed in AFF_CAP_BY_BOND:
            if allowed > cap:
                need = need_bond
                break
        if need is None:
            return ""
        if cap <= 0:
            return "Affection opens at Bond %d" % need
        return "Affection can't pass %d until Bond %d" % (cap, need)

    def jr_person(who):
        """WP8. Everything the People detail pane shows about someone. Name
        and role come from the card (journal_cast), so the pane matches it
        for people who only have a JOURNAL_CAST entry."""
        c = CAST.get(who, {})
        card = dict((e["who"], e) for e in journal_cast()).get(who, {})
        try:
            st = npc_stats(who) or {}
        except Exception:
            st = {}
        d = dict(who=who, name=card.get("name") or c.get("name") or jr_short(who), color=jr_color(who),
                 blurb=c.get("blurb", ""), grade=jr_grade_line(who, card.get("role", "")),
                 year=c.get("year", ""),
                 off_scale=bool(st.get("off_scale")), restricted=bool(st.get("restricted")),
                 note=st.get("note", "") or "",
                 reserve=st.get("ce_max"), control=st.get("control"), output=st.get("output"))
        d["has_stats"] = d["off_scale"] or any(d[k] is not None for k in ("reserve", "control", "output"))
        d["bond"] = store.bonds.get(who, 0)
        d["bond_rank"] = bond_rank(d["bond"])[1]
        d["romance"] = is_romanceable(who)
        d["aff"] = store.affection.get(who, 0)
        d["aff_rank"] = aff_rank(d["aff"])[1]
        d["aff_cap"] = aff_cap(who) if d["romance"] else None
        d["aff_note"] = jr_aff_note(who) if d["romance"] else ""
        d["promotions"] = ["Promoted to %s on Day %s" % (grade_label(g), dy)
                           for dy, g, why in jr_promotions(who)]
        d["thread"] = jr_thread(who)
        d["missions"] = [jr_mission_row(m, character=True) for m in jr_missions(kind="character", who=who)]
        try:
            d["usual"] = usual_places(who) or ""
        except Exception:
            d["usual"] = ""
        d["office_today"] = (who == "gojo" and gojo_in_today())
        mems = jr_memories_with(who)
        d["mem_seen"] = len([m for m in mems if jr_mem_state(m) == "seen"])
        d["mem_total"] = len(mems)
        d["sprite"] = "images/char/%s_neutral.png" % who
        return d

    ## Missions -----------------------------------------------------------------

    def jr_mrec(m):
        """A mission record from a record or an id."""
        if isinstance(m, str):
            by = getattr(store, "MISSION_BY_ID", None) or {}
            return by.get(m) or dict(id=m, title=m)
        return m

    def jr_missions(kind=None, who=None):
        """Mission records, in registry order. kind "story" also takes the
        promotion rows, which sit in the story chain."""
        try:
            if kind == "story":
                ms = [jr_mrec(m) for m in (missions_list() or [])]
                return [m for m in ms if jr_get(m, "kind", "story") in ("story", "promotion")]
            return [jr_mrec(m) for m in (missions_list(kind=kind, who=who) or [])]
        except Exception:
            return []

    def jr_filter_ok(status, f):
        if f == "all":
            return True
        if f == "available":
            return status in ("available", "waiting")
        if f == "active":
            return status == "active"
        if f == "done":
            return status in ("done", "skipped")
        return True

    ## status -> (symbol, colour key, uses the symbol font)
    JR_STATUS_ICON = {
        "done":      ("✓", "stamina", True),
        "skipped":   ("✓", "mute", True),
        "available": ("◆", "gold", False),
        "active":    ("●", "violet2", False),
        "waiting":   ("◌", "dim", True),
        "locked":    ("—", "mute", False),
        "unwritten": ("·", "mute", False),
        "closed":    ("—", "mute", False),
    }

    def jr_where_when(m):
        """Where and when a mission happens, in the player's words."""
        trig = jr_get(m, "trigger", "auto")
        where = jr_get(m, "where")
        giver = jr_get(m, "with_who") or jr_get(m, "who")
        periods = jr_periods_text(jr_get(m, "periods"))
        if trig == "auto":
            return (periods + ", wherever I am") if periods else "wherever I am"
        if where is None:
            place = ("wherever %s is" % jr_short(giver)) if giver else ""
        else:
            place = jr_place_name(where)
        when = ""
        if giver and isinstance(where, str):
            try:
                when = when_at(giver, where) or ""
            except Exception:
                when = ""
        when = when or periods
        return ", ".join([p for p in (place, when) if p])

    def jr_group_text(m):
        """"The Surveyor 2/3" for a row in a group, else ""."""
        g = jr_get(m, "group")
        if not g:
            return ""
        members = [x for x in jr_missions(kind="story") if jr_get(x, "group") == g]
        done = len([x for x in members if mission_status(jr_get(x, "id")) in ("done", "skipped")])
        return "%s %d/%d" % (g, done, len(members))

    def jr_mission_row(m, character=False):
        """WP8. One row of the Missions tab (and the People detail)."""
        mid = jr_get(m, "id")
        try:
            status = mission_status(mid)
        except Exception:
            status = "locked"
        title = jr_get(m, "title", mid) or mid
        line = ""
        if status in ("available", "active"):
            obj = jr_get(m, "objective", "") or ""
            ww = jr_where_when(m)
            line = " — ".join([p for p in (obj, ww) if p])
        elif status == "waiting":
            ## 3.6's waiting form: "<objective> — <where and when>, tomorrow".
            obj = jr_get(m, "objective", "") or ""
            why = mission_reason(mid) or ""
            ww = ", ".join([q for q in (jr_where_when(m), why) if q])
            line = " — ".join([p for p in (obj, ww) if p])
        elif status == "locked":
            line = mission_reason(mid) or "Not yet"
        elif status == "unwritten":
            line = "Written in a later build" if character else "Coming in a later build"
        elif status == "closed":
            line = "Closed when Arc Two began"
        elif status == "skipped":
            line = "Passed by"
        rewards = jr_get(m, "rewards", {}) or {}
        merit = jr_get(rewards, "merit", 0) or 0
        icon, colkey, symfont = JR_STATUS_ICON.get(status, ("—", "mute", False))
        return dict(id=mid, status=status, title=title, line=line, merit=merit,
                    group=jr_group_text(m), icon=icon, color=getattr(gui, colkey),
                    symfont=symfont, dim=(status in ("unwritten", "closed", "skipped")))

    def jr_acts():
        """ACTS as dicts of id, title, kanji and band."""
        out = []
        for a in (ACTS or []):
            if isinstance(a, dict):
                out.append(dict(id=a.get("id"), title=a.get("title", ""), kanji=a.get("kanji", ""),
                                band=a.get("band", a.get("grade_band", "")) or ""))
            elif isinstance(a, (tuple, list)):
                a = list(a) + ["", "", "", ""]
                out.append(dict(id=a[0], title=a[1] or "", kanji=a[2] or "", band=a[3] or ""))
            else:
                out.append(dict(id=getattr(a, "id", None), title=getattr(a, "title", ""),
                                kanji=getattr(a, "kanji", ""), band=getattr(a, "band", "")))
        return out

    def jr_act_title(a):
        t, aid = a["title"], a["id"]
        if aid in ("P", "Prologue") or str(t).lower().startswith(("act", "prologue")):
            return t or "Prologue"
        return "Act %s · %s" % (aid, t) if t else "Act %s" % aid

    def jr_story_groups(f):
        """[(act dict, header note, [rows])] for the Story sub-tab, filtered."""
        rows_by_act = {}
        order = []
        for m in jr_missions(kind="story"):
            aid = jr_get(m, "act")
            if aid not in rows_by_act:
                rows_by_act[aid] = []
                order.append(aid)
            r = jr_mission_row(m)
            if jr_filter_ok(r["status"], f):
                rows_by_act[aid].append(r)
        acts = jr_acts()
        known = [a["id"] for a in acts]
        for aid in order:
            if aid not in known:
                acts.append(dict(id=aid, title="", kanji="", band=""))
        out = []
        for a in acts:
            rows = rows_by_act.get(a["id"], [])
            try:
                done, written, total = act_progress(a["id"])
            except Exception:
                done, written, total = (0, 0, 0)
            note = ""
            if written:
                note = "%d of %d" % (done, written)
            if total > written:
                note += (" · " if note else "") + "%d in a later build" % (total - written)
            if rows or (f == "all" and a["id"] in rows_by_act):
                out.append((a, note, rows))
        return out

    def jr_character_groups(f):
        """[(person card dict, [rows])] for the Character sub-tab."""
        out = []
        for e in journal_cast():
            if not e["met"] or e["who"] == "sana":
                continue
            rows = [jr_mission_row(m, character=True) for m in jr_missions(kind="character", who=e["who"])]
            rows = [r for r in rows if jr_filter_ok(r["status"], f)]
            if rows:
                out.append((e, rows))
        return out

    def jr_mission_counts():
        """How many missions are available now (the tab badge)."""
        n = 0
        for m in jr_missions(kind="story") + jr_missions(kind="character"):
            if mission_status(jr_get(m, "id")) in ("available", "active"):
                n += 1
        return n

    def jr_promotion():
        """(merit, need, next label, line) for the promotion box."""
        try:
            m, need, nxt = merit_progress()
        except Exception:
            m, need, nxt = (store.merit, None, None)
        line = next_grade_text() or ""
        return (m, need, grade_label(nxt) if nxt else "", line)

    def jr_merit_label(m, need, line):
        """The promotion bar's own "Merit m / need" label, or "" when the
        next_grade_text() line under it already starts with the merit."""
        if str(line).lstrip().lower().startswith("merit"):
            return ""
        return ("Merit %s / %s" % (m, need)) if need else ("Merit %s" % m)

    ## The board ----------------------------------------------------------------

    def jr_board():
        """What the Board sub-tab shows, from board_summary()."""
        try:
            s = board_summary() or {}
        except Exception:
            s = {}
        host = board_host()
        where = "At Utahime's office" if host[0] == "utahime" else "At Principal Yaga's office, with Ijichi"
        offers = list(jr_get(s, "offers", []) or [])
        taken = list(jr_get(s, "taken", []) or [])
        log = list(jr_get(s, "log", None) or jr_get(s, "recent", None) or jr_get(s, "runs", None) or [])[-10:]
        try:
            mis = jr_get(s, "misgrades", None)
            if mis is None:
                mis = misgrade_count()
        except Exception:
            mis = 0
        return dict(where=where, offers=offers, taken=taken, log=list(reversed(log)),
                    misgrades=mis or 0, empty=not (offers or taken or log))

    def jr_offer_line(o):
        parts = [jr_get(o, "case"), jr_get(o, "place")]
        return " · ".join([str(p) for p in parts if p])

    def jr_yen(v):
        if isinstance(v, (tuple, list)) and len(v) == 2:
            return "¥%s–%s" % ("{:,}".format(v[0]), "{:,}".format(v[1]))
        if isinstance(v, int):
            return "¥{:,}".format(v)
        return str(v) if v else ""

    def jr_log_row(r):
        """(day, grade, partner, outcome, merit) text of a board log row."""
        if isinstance(r, (tuple, list)):
            r = dict(zip(("day", "grade", "partner", "outcome", "merit"), r))
        partner = jr_get(r, "partner") or jr_get(r, "who") or ""
        return ("Day %s" % jr_get(r, "day", "?"), grade_label(jr_get(r, "grade")),
                jr_short(partner) if partner else "", str(jr_get(r, "outcome", "") or "").capitalize(),
                "Merit +%d" % (jr_get(r, "merit", 0) or 0), jr_get(r, "title", "") or "")

    ## Memories -----------------------------------------------------------------

    def _jr_rule(rule):
        """A memory's seen or unlock rule (3.9) against the save's own state."""
        if not rule:
            return False
        if isinstance(rule, list):
            return any(_jr_rule(r) for r in rule)
        if not isinstance(rule, tuple) or len(rule) < 2:
            return False
        kind, arg = rule[0], rule[1]
        if kind == "label":
            return arg in (getattr(store, "memories_seen", None) or {})
        if kind == "event":
            return arg in store.done_events
        if kind == "flag":
            return has_flag(arg)
        if kind == "act":
            return arg in (getattr(store, "seen_acts", None) or set())
        if kind == "together":
            return arg in store.together
        if kind == "district":
            return arg in (getattr(store, "districts_visited", None) or set())
        if kind == "item":
            return has_item(arg)
        return False

    def jr_mem_state(m):
        """WP8. "seen" (replayable), "later" (triggered, written in a later
        build) or "locked". Uses WP5's memory_state(m) when it exists, or a
        state/seen field on the record, else the record's rules."""
        fn = getattr(store, "memory_state", None)
        if callable(fn):
            try:
                s = fn(m)
                if isinstance(s, bool):
                    return "seen" if s else "locked"
                if s in ("seen", "later", "locked"):
                    return s
            except Exception:
                pass
        s = jr_get(m, "state")
        if s in ("seen", "later", "locked"):
            return s
        seen = jr_get(m, "seen")
        if isinstance(seen, bool):
            ok = seen
        else:
            ok = _jr_rule(seen)
        if ok:
            return "seen"
        unlock = jr_get(m, "unlock")
        if unlock and _jr_rule(unlock):
            label = jr_get(m, "label")
            if not (label and renpy.has_label(label)):
                return "later"
        return "locked"

    def jr_mem_who(m):
        w = jr_get(m, "who", ()) or ()
        if isinstance(w, str):
            w = (w,)
        return tuple(w)

    def jr_all_memories():
        """Every catalogued memory once, in catalogue order."""
        out, seen = [], set()
        src = list(MEMORIES or [])
        if not src:
            for title, mems in (memory_groups("act") or []):
                src.extend(mems)
        for m in src:
            key = jr_get(m, "id") or jr_get(m, "label") or id(m)
            if key not in seen:
                seen.add(key)
                out.append(m)
        return out

    def jr_memories_with(who):
        return [m for m in jr_all_memories() if who in jr_mem_who(m)]

    def jr_memory_groups(mode, who=None):
        """[(title, [memory])] for the Memories tab. With `who`, one group:
        every memory with that person."""
        if who:
            return [(CAST.get(who, {}).get("name", jr_short(who)), jr_memories_with(who))]
        try:
            groups = memory_groups(mode) or []
        except Exception:
            groups = []
        return [(t, list(ms)) for t, ms in groups if ms]

    def jr_memory_counts():
        try:
            seen, total = memory_counts()
        except Exception:
            seen, total = (0, 0)
        if not total:
            mems = jr_all_memories()
            total = len(mems)
            seen = len([m for m in mems if jr_mem_state(m) == "seen"])
        return seen, total

    def jr_mem_thumb(m):
        """The tile's thumbnail: the memory's background, 280x158."""
        bg = jr_get(m, "bg")
        d = None
        if bg:
            if renpy.has_image(bg):
                d = bg
            elif renpy.loadable(bg):
                d = bg
        if d is None:
            return Solid(gui.panel2, xysize=(280, 158))
        return Transform(d, xysize=(280, 158), fit="cover")

    def journal_replay_action(m):
        """WP8. What a seen memory tile does: WP5's memory_replay(m)."""
        return memory_replay(m)

    ## Stats --------------------------------------------------------------------

    def jr_grade_for_stat(req):
        """The lowest grade whose stat cap reaches req, or None."""
        for k in GRADE_ORDER:
            g = GRADES[k]
            if g["stat"] is not None and g["stat"] >= req and not g.get("off_scale"):
                return k
        return None

    def jr_tech():
        """What the Last Light panel shows."""
        t = tech()
        ti, tname, tdesc = tech_tier()
        nx = next_tier()
        cap = grade_cap("stat")
        nxline = ""
        if nx:
            nxline = "%s — at %s %d" % (nx[0], t.get("tag", "Control"), nx[1])
            if cap is not None and nx[1] > cap:
                g = jr_grade_for_stat(nx[1])
                if g:
                    nxline += " — needs %s" % grade_label(g)
        moves = []
        for mv in (MOVES.get("timestop") or MOVES.get(store.technique) or []):
            tier = mv.get("tier", 0)
            ok = tier <= ti
            req = t["tiers"][tier][2] if tier < len(t["tiers"]) else 0
            moves.append(dict(name=mv.get("name", ""), ce=mv.get("ce", 0), desc=mv.get("desc", ""),
                              ok=ok, needs=("Unlocks at %s %d" % (t.get("tag", "Control"), req)) if not ok else ""))
        vd = (t.get("verb_desc", "") or "").strip()
        ## 4.7: the verb's line says it is once a day. WP2's verb_desc (3.4)
        ## already does; add it only to one that doesn't.
        if vd and "once a day" not in vd.lower():
            vd += " Once a day."
        return dict(name=t.get("name", ""), jp=t.get("jp", ""), tier=tname, tier_desc=tdesc,
                    next=nxline, verb=t.get("verb", ""), verb_desc=vd,
                    moves=moves)

    def jr_bars():
        """[(label, value, max, cap marker, colour, value text)] for Stats."""
        scap = grade_cap("stat")
        rcap = grade_cap("reserve")
        rscale = max(store.ce_max, rcap or 0, 1)
        return [
            ("Health", store.hp, max(1, store.hp_max), None, gui.seal, "%d / %d" % (store.hp, store.hp_max)),
            ("Cursed energy", store.ce, rscale, rcap, gui.violet,
             "%d / %d" % (store.ce, store.ce_max) + ("  · cap %d" % rcap if rcap else "")),
            ("Control", store.control, 100, scap, gui.violet2,
             "%d" % store.control + ("  · cap %d" % scap if scap else "")),
            ("Output", store.output, 100, scap, gui.gold,
             "%d" % store.output + ("  · cap %d" % scap if scap else "")),
            ("Insight", store.insight, 100, None, gui.paper, "%d" % store.insight),
            ("Stamina", store.stamina, max(1, store.stamina_max), None, gui.stamina,
             "%d / %d" % (store.stamina, store.stamina_max)),
        ]

    def jr_year():
        """The "Your year" strip: [(name, colour, reserve or None, off_scale)]."""
        out = [(store.mc_name, CAST.get("mc", {}).get("color", gui.violet2), store.ce_max, False)]
        for who in ("yuji", "megumi", "nobara", "gojo"):
            try:
                st = npc_stats(who) or {}
            except Exception:
                st = {}
            out.append((jr_short(who), jr_color(who), st.get("ce_max"), bool(st.get("off_scale"))))
        return out

    def jr_meter_px(value, maximum, width):
        try:
            return max(0, min(width, int(width * (float(value) / float(max(1, maximum))))))
        except Exception:
            return 0

    ## Equipment and inventory --------------------------------------------------

    def jr_item(iid):
        """An ITEMS entry with fallbacks for every field the journal reads."""
        it = ITEMS.get(iid, {}) or {}
        return dict(id=iid, name=it.get("name") or str(iid).replace("_", " ").capitalize(),
                    kind=it.get("kind", ""), grade=it.get("grade"), desc=it.get("desc", "") or "",
                    effect=it.get("effect", "") or "", source=it.get("source", "") or "",
                    special=bool(it.get("special")), sealed=it.get("sealed"))

    def jr_worn():
        return list(getattr(store, "equipped_talismans", None) or [])

    def jr_tool():
        return getattr(store, "equipped_tool", None)

    def jr_slot_opens(i):
        """"Opens at Grade 3" for talisman slot i (0-based)."""
        for k in GRADE_ORDER:
            g = GRADES[k]
            if g["slots"] > i and not g.get("off_scale"):
                return "Opens at %s" % g["name"]
        return "Sealed"

    def jr_pick_options(kind, slot=0):
        """[(item id, selectable, reason)] for the picker."""
        out = []
        if kind == "tool":
            cur = jr_tool()
            for iid in items_in("tool"):
                out.append((iid, iid != cur, "In my hand" if iid == cur else ""))
            return out
        worn = jr_worn()
        cur = worn[slot] if slot < len(worn) else None
        for iid in items_in("talisman"):
            if iid == cur:
                out.append((iid, False, "In this slot"))
                continue
            if iid in worn:
                out.append((iid, False, "Worn in another slot"))
                continue
            try:
                ok, why = can_wear(iid)
            except Exception:
                ok, why = (False, "")
            ## Replacing: the slot this goes into is about to be free.
            if not ok and cur and str(why).startswith("No free slot"):
                ok, why = True, ""
            out.append((iid, ok, why or ""))
        return out

    def jr_wear(slot, iid):
        """WP8. Put a talisman in a slot, through WP6's API only, keeping
        the others where they are: take off what was in the slot and every
        talisman after it, wear the new one, then put the later ones back in
        their order. If WP6 refuses the new one, put everything back as it
        was. (WP6 appends, so an empty slot is always the next one.)"""
        worn = jr_worn()
        cur = worn[slot] if slot < len(worn) else None
        later = worn[slot + 1:] if cur else []
        for x in ([cur] if cur else []) + later:
            unequip_talisman(x)
        equip_talisman(iid)
        ok = iid in jr_worn()
        for x in ([] if ok else ([cur] if cur else [])) + later:
            if x not in jr_worn():
                equip_talisman(x)

    def jr_inventory(cat):
        """Owned item ids in a category, by kind order then name."""
        order = [c[0] for c in JR_INV_CATS]
        ids = [i for i, n in store.inventory.items() if n > 0]
        if cat != "all":
            ids = [i for i in ids if jr_item(i)["kind"] == cat]
        def key(i):
            k = jr_item(i)["kind"]
            return (order.index(k) if k in order else 99, jr_item(i)["name"])
        return sorted(ids, key=key)

    def jr_inv_count(cat):
        return len(jr_inventory(cat))


## The journal ##################################################################

style jr_text is text:
    color gui.paper
    size 20

style jr_dim is jr_text:
    color gui.dim
    size 18

style jr_kicker is text:
    font JR_MEDIUM_FONT
    color gui.dim
    size 16
    kerning gui.track

style jr_title is text:
    font JR_DISPLAY_FONT
    color gui.paper
    size 30

style jr_tab_button is button:
    xysize (260, 72)
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    selected_background Frame("gui/panel_active.png", 4, 4)
    selected_hover_background Frame("gui/panel_active.png", 4, 4)
    padding (14, 0, 16, 0)

style jr_tab_text is text:
    font JR_DISPLAY_FONT
    color gui.dim
    hover_color gui.paper
    selected_color gui.paper
    size 26

style jr_card_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (0, 0)

style jr_card_frame is frame:
    background Frame("gui/panel_ghost.png", 4, 4)
    padding (0, 0)

style jr_panel is frame:
    background Frame("gui/panel.png", 4, 4)
    padding (28, 22)

style jr_panel_dark is frame:
    background Frame("gui/panel_dark.png", 4, 4)
    padding (28, 22)

style jr_chip_button is button:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    selected_background Frame("gui/panel_active.png", 4, 4)
    selected_hover_background Frame("gui/panel_active.png", 4, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (18, 8)

style jr_chip_button_text is text:
    font JR_MEDIUM_FONT
    color gui.dim
    hover_color gui.paper
    selected_color gui.paper
    insensitive_color gui.mute
    size 18

style jr_link_button is button:
    background None
    padding (0, 4)

style jr_link_button_text is text:
    font JR_MEDIUM_FONT
    color gui.gold
    hover_color gui.paper
    insensitive_color gui.mute
    size 19

style jr_row_button is button:
    background Frame("gui/panel.png", 4, 4)
    hover_background Frame("gui/rail_violet.png", 10, 4)
    insensitive_background Frame("gui/panel_ghost.png", 4, 4)
    padding (22, 12)

## A small uppercase chip ("GRADE 2", "SENIOR").
screen jr_chip(text, color=gui.dim, fill=None):
    frame:
        background (Solid(fill) if fill else Frame("gui/panel_ghost.png", 4, 4))
        padding (10, 3)
        yalign 0.5
        text "[text!u]":
            font JR_BOLD_FONT
            color (gui.ink if fill else color)
            size 13
            kerning 2


## A meter with an optional cap marker, and an off-scale overflow (task 5):
## an off_scale bar runs past the end of its track and ends in "∞".
screen jr_meter(value, maximum=100, width=620, height=10, fill=gui.violet, marker=None, off_scale=False):

    $ _w = jr_meter_px(value, maximum, width)

    fixed:
        xysize (width + (56 if off_scale else 0), max(height + 8, 26 if off_scale else 0))
        add Solid(gui.line) xysize (width, height) yalign 0.5
        if off_scale:
            add Solid(fill) xysize (width + 22, height) yalign 0.5
            text "∞":
                font JR_SYMBOL_FONT
                color fill
                size 26
                xpos width + 28
                yalign 0.5
        elif _w:
            add Solid(fill) xysize (_w, height) yalign 0.5
        if marker is not None and not off_scale:
            $ _mx = max(0, min(width - 2, jr_meter_px(marker, maximum, width) - 1))
            add Solid(gui.paper) xpos _mx xysize (2, height + 8) yalign 0.5


## A vertical scroller that fills the content area below the NEXT strip.
screen jr_scroll(w=1520, h=900, spacing=18):
    ## With scrollbars, the size goes to the whole (viewport + bar): the
    ## viewport itself is w - 20 wide.
    viewport:
        xysize (w, h)
        scrollbars "vertical"
        side_spacing 10
        vscrollbar_xsize 10
        vscrollbar_unscrollable "hide"
        mousewheel True
        draggable True
        pagekeys True
        has vbox
        spacing spacing
        transclude


screen journal(tab="people"):

    tag menu

    default js = journal_state(tab)

    ## D4: editable only when opened from campus, in the main context.
    $ editable = journal_editable()
    $ _cur = js["tab"]
    $ _obj = objective_text() or ""
    $ _idle = _("Nothing pressing. Go and see who's around.") if jr_on_campus() else _("Nothing pressing.")

    add gui.game_menu_background
    add Solid(gui.ink) alpha 0.86

    ## Esc and right-click: close the picker or the detail pane, else leave.
    if js["pick"] is not None:
        key "game_menu" action SetDict(js, "pick", None)
    elif js["sel"] is not None and _cur == "people":
        key "game_menu" action SetDict(js, "sel", None)
    else:
        key "game_menu" action Return()

    ## The rail -------------------------------------------------------------
    frame:
        xpos 0
        ypos 0
        xysize (320, 1080)
        background Solid(gui.panel)
        padding (30, 40, 30, 40)

        fixed:
            vbox:
                spacing 14
                hbox:
                    spacing 16
                    use seal("記", 44)
                    text _("Journal"):
                        font JR_DISPLAY_FONT
                        color gui.paper
                        size 40
                        yalign 0.5
                use rule(260)
                null height 10

                for _k, _kan, _lab in JOURNAL_TABS:
                    $ _badge = ""
                    if _k == "missions":
                        $ _n = jr_mission_counts()
                        $ _badge = str(_n) if _n else ""
                    elif _k == "memories":
                        $ _ms = jr_memory_counts()
                        $ _badge = ("%d" % _ms[0]) if _ms[1] else ""
                    elif _k == "inventory":
                        $ _n = jr_inv_count("all")
                        $ _badge = str(_n) if _n else ""
                    button:
                        style "jr_tab_button"
                        selected (_cur == _k)
                        action [SetDict(js, "sel", None), SetDict(js, "pick", None), SetDict(js, "tab", _k)]
                        fixed:
                            hbox:
                                spacing 14
                                yalign 0.5
                                use seal(_kan, 44)
                                text _lab style "jr_tab_text" yalign 0.5
                            if _badge:
                                frame:
                                    xalign 1.0
                                    yalign 0.5
                                    background Solid(gui.gold if _k == "missions" else gui.line2)
                                    padding (9, 2)
                                    text _badge:
                                        font JR_BOLD_FONT
                                        color (gui.ink if _k == "missions" else gui.paper)
                                        size 15

            textbutton _("Return"):
                style "return_button"
                xpos 0
                yalign 1.0
                yoffset 0
                action Return()

    ## The content area -----------------------------------------------------
    fixed:
        xpos 360
        ypos 40
        xysize (1520, 1000)

        ## ◆ NEXT
        frame:
            xysize (1520, 52)
            background Frame("gui/panel_dark.png", 4, 4)
            padding (22, 0)
            fixed:
                add Solid(gui.gold) xysize (1520 - 44, 2) ypos 0
                hbox:
                    spacing 18
                    yalign 0.5
                    text "◆ NEXT":
                        font JR_BOLD_FONT
                        color gui.gold
                        size 17
                        kerning 3
                        yalign 0.5
                    text (jr_clip(_obj, 120) if _obj else _idle):
                        font JR_DISPLAY_FONT
                        color (gui.paper if _obj else gui.dim)
                        size 22
                        yalign 0.5

        fixed:
            ypos 72
            xysize (1520, 928)

            if _cur == "people":
                use jr_people(js)
            elif _cur == "missions":
                use jr_missions_tab(js, editable)
            elif _cur == "memories":
                use jr_memories_tab(js)
            elif _cur == "stats":
                use jr_stats_tab()
            elif _cur == "equipment":
                use jr_equipment_tab(js, editable)
            elif _cur == "inventory":
                use jr_inventory_tab(js)

    if js["pick"] is not None and _cur == "equipment" and editable:
        use jr_picker(js)


## People #######################################################################

screen jr_people(js):

    if js["sel"] is not None:
        use jr_person_detail(js, js["sel"])

    else:
        use jr_scroll(1520, 928):
            ## 4 columns of 362: the box wraps at the viewport's width.
            hbox:
                box_wrap True
                box_wrap_spacing 16
                spacing 16
                for _e in journal_cast():
                    use jr_person_card(js, _e)


screen jr_person_card(js, e):

    $ _who = e["who"]
    $ _col = e["color"]
    $ _nm = e["name"]

    if _who == "sana":
        $ _mems = jr_memories_with("sana")
        $ _ms = len([m for m in _mems if jr_mem_state(m) == "seen"])
        $ _mt = len(_mems)
        button:
            style "jr_card_button"
            xysize (362, 330)
            action Function(jr_go, js, tab="memories", mem_mode="person", mem_who="sana", sel=None)
            vbox:
                xpos 19
                ypos 14
                spacing 6
                if e["art"]:
                    add jr_portrait(_who)
                text _nm font JR_DISPLAY_FONT color _col size 26
                use jr_chip(_("In memory"), gui.gold)
                text _("Memories: [_ms] of [_mt]") style "jr_dim"
                text _("See her memories →") style "jr_dim" color gui.gold size 17

    elif e["met"]:
        $ _gl = jr_grade_line(_who, e["role"])
        $ _b = bonds.get(_who, 0)
        $ _br = bond_rank(_b)[1]
        $ _rom = is_romanceable(_who)
        $ _a = affection.get(_who, 0)
        $ _nx = jr_clip(jr_next(_who), 74)
        $ _promo = jr_recently_promoted(_who)
        button:
            style "jr_card_button"
            xysize (362, 330)
            action SetDict(js, "sel", _who)
            vbox:
                xpos 19
                ypos 12
                spacing 3
                if e["art"]:
                    add jr_portrait(_who)
                else:
                    fixed:
                        xysize (324, 162)
                        add Solid(gui.panel2)
                        text "「？」" size 64 color gui.mute xalign 0.5 yalign 0.5
                text jr_clip(_nm, 24) font JR_DISPLAY_FONT color _col size 24
                ## The chip and the bond rank; the heart rank sits on its own
                ## meter's line, so long ranks can't push past the card.
                hbox:
                    spacing 10
                    ## D12: a recent promotion shows as a gold chip.
                    if _gl:
                        if _promo:
                            use jr_chip(_gl + " ↑", fill=gui.gold)
                        else:
                            use jr_chip(_gl, gui.dim)
                    text jr_clip(_br, 18) style "jr_dim" size 15 yalign 0.5
                vbox:
                    spacing 0
                    use jr_meter(_b, 100, width=324, height=6, fill=_col)
                    if _rom:
                        $ _ar = jr_clip(aff_rank(_a)[1], 16)
                        hbox:
                            spacing 10
                            use jr_meter(_a, 100, width=170, height=4, fill=gui.romance, marker=aff_cap(_who))
                            text "♡ [_ar]" color gui.romance size 15 yalign 0.5
                if _nx:
                    text _nx color gui.gold size 16 xsize 324 line_spacing 0

    else:
        frame:
            style "jr_card_frame"
            xysize (362, 330)
            vbox:
                xpos 19
                ypos 14
                spacing 10
                fixed:
                    xysize (324, 162)
                    add Solid(gui.panel2)
                    if e["art"]:
                        add jr_portrait(_who, black=True)
                    else:
                        text "「？」" size 72 color gui.mute xalign 0.5 yalign 0.5
                text _("Not yet met") style "jr_kicker"
                text e["hint"] style "jr_dim" xsize 324 size 18


screen jr_person_detail(js, who):

    $ _d = jr_person(who)
    $ _col = _d["color"]

    frame:
        style "jr_panel_dark"
        xysize (1520, 928)
        padding (0, 0)
        fixed:

            ## The raw sprite, unlit.
            fixed:
                xpos 10
                xysize (440, 928)
                if renpy.loadable(_d["sprite"]):
                    add _d["sprite"] zoom 0.5 xalign 0.5 yalign 1.0 yoffset -10
                else:
                    text "「？」" size 120 color gui.mute xalign 0.5 yalign 0.5

            fixed:
                xpos 470
                ypos 24
                xysize (1030, 890)

                use jr_scroll(1030, 890):

                    ## Name, grade, blurb.
                    vbox:
                        spacing 6
                        text _d["name"] font JR_DISPLAY_FONT color _col size 46
                        hbox:
                            spacing 12
                            if _d["grade"]:
                                use jr_chip(_d["grade"], gui.paper)
                            if _d["year"] and _d["year"] != _d["grade"]:
                                text _d["year"] style "jr_dim" yalign 0.5
                        if _d["blurb"]:
                            text _d["blurb"] style "jr_text" xsize 960 italic True
                        for _p in _d["promotions"]:
                            text _p color gui.gold size 18

                    ## Strength.
                    if _d["has_stats"]:
                        vbox:
                            spacing 8
                            text _("STRENGTH") style "jr_kicker"
                            hbox:
                                spacing 16
                                text _("Reserve") style "jr_dim" min_width 120 yalign 0.5
                                if _d["restricted"]:
                                    text _("Heavenly Restriction") color gui.gold size 18 yalign 0.5
                                elif _d["off_scale"]:
                                    use jr_meter(300, 300, width=620, fill=_col, off_scale=True)
                                elif _d["reserve"] is not None:
                                    use jr_meter(_d["reserve"], 300, width=620, fill=_col)
                                    text "[_d['reserve']]" style "jr_dim" yalign 0.5
                            for _lab, _k in ((_("Control"), "control"), (_("Output"), "output")):
                                hbox:
                                    spacing 16
                                    text _lab style "jr_dim" min_width 120 yalign 0.5
                                    if _d["off_scale"]:
                                        use jr_meter(100, 100, width=620, fill=_col, off_scale=True)
                                    elif _d[_k] is not None:
                                        use jr_meter(_d[_k], 100, width=620, fill=_col)
                                        text str(_d[_k]) style "jr_dim" yalign 0.5
                            if _d["note"]:
                                text _d["note"] style "jr_dim" size 16 italic True

                    ## Bond and affection.
                    vbox:
                        spacing 8
                        text _("BOND") style "jr_kicker"
                        hbox:
                            spacing 16
                            use jr_meter(_d["bond"], 100, width=620, fill=_col)
                            text "[_d['bond_rank']] · [_d['bond']]" style "jr_dim" yalign 0.5
                        if _d["romance"]:
                            hbox:
                                spacing 16
                                use jr_meter(_d["aff"], 100, width=620, height=6, fill=gui.romance, marker=_d["aff_cap"])
                                text "♡ [_d['aff_rank']]" color gui.romance size 18 yalign 0.5
                            if _d["aff_note"]:
                                text _d["aff_note"] style "jr_dim" size 16

                    ## Their thread.
                    if _d["thread"]:
                        vbox:
                            spacing 6
                            hbox:
                                spacing 12
                                text _d["thread"][0] font JR_DISPLAY_FONT color gui.gold size 26
                                if _d["thread"][2]:
                                    use jr_chip(_("Resolved"), fill=gui.stamina)
                            for _line in _d["thread"][1]:
                                hbox:
                                    spacing 12
                                    add "gui/pip_small.png" ypos 8
                                    text _line style "jr_text" size 19 xsize 940

                    ## Their missions.
                    if _d["missions"]:
                        vbox:
                            spacing 6
                            text _("THEIR STORY") style "jr_kicker"
                            for _r in _d["missions"]:
                                use jr_mission_line(_r, 960)

                    ## Where they are.
                    vbox:
                        spacing 4
                        text _("USUALLY") style "jr_kicker"
                        if _d["office_today"]:
                            text _("In his office today.") color gui.gold size 19
                        text (_d["usual"] or _("Around campus.")) style "jr_text" size 19 xsize 960

                    ## Memories.
                    if _d["mem_total"]:
                        textbutton _("Memories with them ([_d['mem_seen']]) →"):
                            style "jr_link_button"
                            action Function(jr_go, js, tab="memories", mem_mode="person", mem_who=who, sel=None)

            textbutton _("← Back"):
                style "jr_chip_button"
                xalign 1.0
                xoffset -24
                ypos 20
                action SetDict(js, "sel", None)


## Missions #####################################################################

## One mission row, compact (the People detail).
screen jr_mission_line(r, w=960):
    hbox:
        spacing 12
        text r["icon"]:
            font (JR_SYMBOL_FONT if r["symfont"] else JR_BODY_FONT)
            color r["color"]
            size 20
            min_width 22
        vbox:
            spacing 0
            text r["title"] color (gui.mute if r["dim"] else gui.paper) size 20
            if r["line"]:
                text r["line"] style "jr_dim" size 16 xsize (w - 40)


## A full mission row, 1480x72.
screen jr_mission_row(r):
    frame:
        background Frame("gui/panel_ghost.png" if r["dim"] else "gui/panel.png", 4, 4)
        xysize (1480, 72)
        padding (20, 0)
        hbox:
            yalign 0.5
            spacing 18
            text r["icon"]:
                font (JR_SYMBOL_FONT if r["symfont"] else JR_BODY_FONT)
                color r["color"]
                size 24
                min_width 28
                text_align 0.5
                yalign 0.5
            vbox:
                yalign 0.5
                xsize 1180
                spacing 2
                hbox:
                    spacing 14
                    text jr_clip(r["title"], 70):
                        font JR_DISPLAY_FONT
                        color (gui.mute if r["dim"] else gui.paper)
                        size 22
                    if r["group"]:
                        text r["group"] style "jr_dim" size 16 yalign 1.0
                if r["line"]:
                    text jr_clip(r["line"], 130) style "jr_dim" size 16 color (gui.mute if r["dim"] else gui.dim)
            if r["merit"]:
                text "Merit +[r['merit']]" color gui.gold size 17 yalign 0.5


screen jr_missions_tab(js, editable):

    $ _sub = js["msub"]
    $ _f = js["mfilter"]

    vbox:
        spacing 14

        hbox:
            spacing 10
            for _k, _lab in JR_MISSION_SUBS:
                textbutton _lab:
                    style "jr_chip_button"
                    selected (_sub == _k)
                    action SetDict(js, "msub", _k)
            if _sub != "board":
                null width 40
                for _k, _lab in JR_MISSION_FILTERS:
                    textbutton _lab:
                        style "jr_chip_button"
                        selected (_f == _k)
                        action SetDict(js, "mfilter", _k)

        if _sub == "story":
            use jr_story(js, editable)
        elif _sub == "character":
            use jr_character(js)
        else:
            use jr_board_view()


screen jr_story(js, editable):

    $ _groups = jr_story_groups(js["mfilter"])
    $ _m, _need, _nxl, _pline = jr_promotion()
    $ _mlab = jr_merit_label(_m, _need, _pline)
    $ _complete = main_story_complete()

    use jr_scroll(1520, 856, spacing=10):

        ## Arc Two (D38): only from campus.
        if _complete:
            frame:
                style "jr_panel"
                background Frame("gui/panel_gold.png", 4, 4)
                xsize 1480
                hbox:
                    spacing 24
                    vbox:
                        xsize 1100
                        spacing 4
                        text _("Arc One is finished.") font JR_DISPLAY_FONT color gui.gold size 30
                        if editable:
                            text _("Arc Two can begin whenever I'm ready.") style "jr_text"
                        else:
                            text _("Begin Arc Two from the campus journal — open it from the place view.") style "jr_dim"
                    if editable:
                        textbutton _("Begin Arc Two"):
                            style "jr_chip_button"
                            yalign 0.5
                            text_color gui.gold
                            text_size 22
                            action Return(("arc_two",))

        ## Promotion.
        frame:
            style "jr_panel"
            xsize 1480
            hbox:
                spacing 30
                vbox:
                    spacing 6
                    text _("PROMOTION") style "jr_kicker"
                    text (_nxl or grade_label(player_grade())) font JR_DISPLAY_FONT color gui.paper size 28
                vbox:
                    yalign 0.5
                    spacing 8
                    if _need:
                        hbox:
                            spacing 16
                            use jr_meter(_m, _need, width=620, fill=gui.gold)
                            if _mlab:
                                text _mlab color gui.gold size 18 yalign 0.5
                    elif _mlab:
                        text _mlab color gui.gold size 18
                    if _pline:
                        text _pline style "jr_dim" xsize 1000

        if not _groups:
            frame:
                style "jr_card_frame"
                xsize 1480
                padding (28, 22)
                text (_("Nothing to show under this filter. The NEXT line above says what comes next.") if js["mfilter"] != "all" else _("The story's missions appear here as they open.")) style "jr_dim"

        for _a, _note, _rows in _groups:
            $ _aid = _a["id"]
            $ _closed = js["collapsed"].get(_aid, False)
            button:
                style "jr_link_button"
                action Function(jr_toggle, js, "collapsed", _aid)
                hbox:
                    spacing 14
                    text ("+" if _closed else "−") color gui.dim size 22 yalign 0.5 min_width 16
                    if _a["kanji"]:
                        use seal(_a["kanji"], 44)
                    text jr_act_title(_a) font JR_DISPLAY_FONT color gui.paper size 28 yalign 0.5
                    if _note:
                        text "— [_note]" style "jr_dim" yalign 0.5
                    if _a["band"]:
                        use jr_chip(_a["band"], gui.violet2)
            if not _closed:
                for _r in _rows:
                    use jr_mission_row(_r)


screen jr_character(js):

    $ _groups = jr_character_groups(js["mfilter"])

    use jr_scroll(1520, 856, spacing=10):

        if not _groups:
            frame:
                style "jr_card_frame"
                xsize 1480
                padding (28, 22)
                text _("No character stories under this filter yet. Bonds open them: the People tab shows what's next with everyone.") style "jr_dim" xsize 1420

        for _e, _rows in _groups:
            hbox:
                spacing 14
                text _e["name"] font JR_DISPLAY_FONT color _e["color"] size 28
                text jr_grade_line(_e["who"], _e["role"]) style "jr_dim" yalign 0.5
            for _r in _rows:
                use jr_mission_row(_r)


screen jr_board_view():

    $ _b = jr_board()

    use jr_scroll(1520, 856):

        hbox:
            spacing 16
            use seal("任", 44)
            text _b["where"] font JR_DISPLAY_FONT color gui.paper size 30 yalign 0.5
            if _b["misgrades"] >= 1:
                text "· Misgraded jobs found: [_b['misgrades']]" color gui.seal size 19 yalign 0.5

        if _b["empty"]:
            frame:
                style "jr_card_frame"
                xsize 1480
                padding (28, 22)
                text _("No jobs posted yet. Utahime's board opens once she has settled in.") style "jr_dim"

        if _b["offers"]:
            text _("THIS WEEK'S OFFERS · take them at the board") style "jr_kicker"
            hbox:
                spacing 20
                for _o in _b["offers"]:
                    frame:
                        style "jr_panel"
                        xysize (470, 210)
                        vbox:
                            spacing 6
                            hbox:
                                spacing 10
                                use jr_chip(grade_label(jr_get(_o, "grade")), gui.gold)
                                if jr_get(_o, "senior_only"):
                                    use jr_chip(_("Needs a senior partner"), gui.seal)
                            text jr_clip(jr_get(_o, "title", ""), 60) font JR_DISPLAY_FONT color gui.paper size 22 xsize 414
                            text jr_clip(jr_offer_line(_o), 80) style "jr_dim" size 16 xsize 414
                            if jr_get(_o, "blurb"):
                                text jr_clip(jr_get(_o, "blurb"), 90) style "jr_dim" size 15 xsize 414 italic True
                            hbox:
                                spacing 16
                                $ _om = jr_get(_o, "merit", 0) or 0
                                text "Merit +[_om]" color gui.gold size 16
                                text jr_yen(jr_get(_o, "yen")) style "jr_dim" size 16

        if _b["taken"]:
            text _("TAKEN") style "jr_kicker"
            hbox:
                spacing 16
                for _t in _b["taken"]:
                    frame:
                        style "jr_card_frame"
                        padding (20, 12)
                        hbox:
                            spacing 12
                            use jr_chip(grade_label(jr_get(_t, "grade")), gui.mute)
                            text jr_clip(jr_get(_t, "title", ""), 40) color gui.mute size 18 yalign 0.5
                            $ _tb = jr_short(jr_get(_t, "taken_by", "")) if jr_get(_t, "taken_by") else "someone"
                            text "· taken by [_tb]" color gui.mute size 16 yalign 0.5

        if _b["log"]:
            text _("LAST JOBS") style "jr_kicker"
            vbox:
                spacing 4
                for _r in _b["log"]:
                    $ _l = jr_log_row(_r)
                    hbox:
                        spacing 0
                        text _l[0] style "jr_dim" min_width 110
                        text _l[1] style "jr_text" size 18 min_width 150
                        text jr_clip(_l[5], 36) style "jr_text" size 18 min_width 400
                        text _l[2] style "jr_text" size 18 min_width 140
                        text _l[3] style "jr_dim" min_width 140
                        text _l[4] color gui.gold size 18


## Memories #####################################################################

screen jr_memories_tab(js):

    $ _mode = js["mem_mode"]
    $ _who = js["mem_who"]
    $ _groups = jr_memory_groups(_mode, _who)
    $ _seen, _total = jr_memory_counts()

    vbox:
        spacing 14

        hbox:
            spacing 10
            textbutton _("By person"):
                style "jr_chip_button"
                selected (_mode == "person" and not _who)
                action [SetDict(js, "mem_who", None), SetDict(js, "mem_mode", "person")]
            textbutton _("By act"):
                style "jr_chip_button"
                selected (_mode == "act" and not _who)
                action [SetDict(js, "mem_who", None), SetDict(js, "mem_mode", "act")]
            if _who:
                $ _wn = jr_short(_who)
                textbutton "[_wn]  ×":
                    style "jr_chip_button"
                    selected True
                    action SetDict(js, "mem_who", None)
            null width 30
            text "[_seen] of [_total] found" color gui.gold size 20 yalign 0.5

        use jr_scroll(1520, 856):

            if not _groups:
                frame:
                    style "jr_card_frame"
                    xsize 1480
                    padding (28, 22)
                    text _("No memories yet. Scenes I live through end up here, and I can go back to any of them.") style "jr_dim"

            for _title, _mems in _groups:
                text _title font JR_DISPLAY_FONT color gui.paper size 26
                hbox:
                    box_wrap True
                    box_wrap_spacing 16
                    spacing 16
                    for _m in _mems:
                        use jr_memory_tile(_m)


screen jr_memory_tile(m):

    $ _st = jr_mem_state(m)
    $ _title = jr_get(m, "title", "") or ""

    if _st == "seen":
        ## No replay inside a replay (the journal opened from the quick menu
        ## while one is playing).
        button:
            style "jr_card_button"
            xysize (280, 158)
            sensitive (not _in_replay)
            action journal_replay_action(m)
            fixed:
                add jr_mem_thumb(m)
                add Solid(gui.ink) alpha 0.35
                frame:
                    yalign 1.0
                    xfill True
                    background Solid(gui.ink)
                    padding (12, 6)
                    text jr_clip(_title, 30) font JR_DISPLAY_FONT color gui.paper size 18
    else:
        frame:
            style "jr_card_frame"
            xysize (280, 158)
            fixed:
                add Solid(gui.ink) alpha 0.8
                if _st == "later":
                    vbox:
                        xpos 14
                        ypos 14
                        spacing 6
                        text jr_clip(_title, 30) font JR_DISPLAY_FONT color gui.dim size 18 xsize 252
                        text _("Written in a later build") color gui.gold size 15
                else:
                    text "「？」" size 40 color gui.mute xalign 0.5 ypos 14
                    text jr_clip(jr_get(m, "hint", "") or "", 70):
                        style "jr_dim"
                        size 15
                        xpos 14
                        ypos 82
                        xsize 252
                        text_align 0.5


## Stats ########################################################################

screen jr_stats_tab():

    $ _gradeline = ("First-year · %s" % grade_label(player_grade())) if player_grade() else _("First-year · Not yet assessed")
    $ _m, _need, _nxl, _pline = jr_promotion()
    $ _mlab = jr_merit_label(_m, _need, _pline)
    $ _t = jr_tech()
    $ _year = jr_year()

    ## Left: the full picture, unlit.
    fixed:
        xpos 0
        xysize (500, 928)
        add kaito_card_image() zoom 0.62 xalign 0.5 yalign 1.0

    ## Right.
    fixed:
        xpos 540
        xysize (980, 928)

        use jr_scroll(980, 928, spacing=12):

            vbox:
                spacing 4
                text "[mc_surname] [mc_name]" font JR_DISPLAY_FONT color gui.paper size 40
                text _gradeline style "jr_kicker" size 18

            frame:
                style "jr_panel"
                xsize 940
                padding (24, 12)
                vbox:
                    spacing 8
                    text (_("PROMOTION — ") + _nxl.upper() if _nxl else _("PROMOTION")) style "jr_kicker"
                    if _need:
                        hbox:
                            spacing 16
                            use jr_meter(_m, _need, width=620, fill=gui.gold)
                            if _mlab:
                                text _mlab color gui.gold size 18 yalign 0.5
                    elif _mlab:
                        text _mlab color gui.gold size 18
                    if _pline:
                        text _pline style "jr_dim" xsize 880

            vbox:
                spacing 4
                for _lab, _v, _mx, _cap, _fill, _vt in jr_bars():
                    hbox:
                        spacing 16
                        text _lab style "jr_dim" min_width 150 yalign 0.5
                        use jr_meter(_v, _mx, width=620, fill=_fill, marker=_cap)
                        text _vt style "jr_dim" size 16 yalign 0.5

            frame:
                style "jr_panel"
                xsize 940
                padding (24, 12)
                vbox:
                    spacing 4
                    hbox:
                        spacing 14
                        text _t["name"] font JR_DISPLAY_FONT color gui.violet2 size 30
                        text _t["jp"] style "jr_dim" yalign 0.5 font JR_BODY_FONT
                    hbox:
                        spacing 12
                        text _t["tier"] color gui.paper size 21
                        text "— [_t['tier_desc']]" style "jr_dim" size 17 yalign 0.5 xsize 640
                    if _t["next"]:
                        text _("Next: [_t['next']]") style "jr_dim" size 17
                    hbox:
                        spacing 12
                        text _t["verb"].upper() style "jr_kicker" color gui.violet2 yalign 0.5
                        text _t["verb_desc"] style "jr_dim" size 17 xsize 780
                    for _mv in _t["moves"]:
                        hbox:
                            spacing 12
                            text _mv["name"] color (gui.paper if _mv["ok"] else gui.mute) size 18 min_width 150
                            text "[_mv['ce']] CE" color (gui.violet if _mv["ok"] else gui.mute) size 16 min_width 64 yalign 0.5
                            text (_mv["desc"] if _mv["ok"] else _mv["needs"]) color (gui.dim if _mv["ok"] else gui.mute) size 16 xsize 640 yalign 0.5

            frame:
                style "jr_panel"
                xsize 940
                padding (24, 12)
                vbox:
                    spacing 2
                    text _("MY YEAR · CURSED ENERGY RESERVE, 0–300") style "jr_kicker"
                    for _nm, _col, _res, _off in _year:
                        hbox:
                            spacing 16
                            text jr_clip(_nm, 14) color _col size 18 min_width 160 yalign 0.5
                            if _off:
                                use jr_meter(300, 300, width=620, height=8, fill=_col, off_scale=True)
                            elif _res is not None:
                                use jr_meter(_res, 300, width=620, height=8, fill=_col)
                                text str(_res) style "jr_dim" size 16 yalign 0.5


## Equipment ####################################################################

screen jr_equipment_tab(js, editable):

    $ _tool = jr_tool()
    $ _ti = jr_item(_tool) if _tool else None
    $ _worn = jr_worn()
    $ _slots = talisman_slots()

    use jr_scroll(1520, 928):

        if not editable:
            frame:
                style "jr_card_frame"
                xsize 1480
                padding (24, 12)
                text _("Change equipment on campus — open the journal from the place view.") color gui.gold size 19

        ## The tool in hand.
        frame:
            style "jr_panel"
            xsize 1480
            hbox:
                spacing 24
                vbox:
                    xsize 1180
                    spacing 6
                    text _("CURSED TOOL") style "jr_kicker"
                    if _ti:
                        hbox:
                            spacing 12
                            text _("In my hand: [_ti['name']]") font JR_DISPLAY_FONT color gui.paper size 28
                            if _ti["grade"]:
                                use jr_chip(grade_label(_ti["grade"]), gui.gold)
                        if _ti["desc"]:
                            text _ti["desc"] style "jr_dim" xsize 1160
                        if _ti["effect"]:
                            text "[_ti['effect']] · [JR_FX_NOTE]" color gui.violet2 size 17 xsize 1160
                    else:
                        text _("In my hand: Bare hands") font JR_DISPLAY_FONT color gui.paper size 28
                        text _("No cursed tool yet. The armory releases them by grade.") style "jr_dim"
                if editable:
                    textbutton _("Change"):
                        style "jr_chip_button"
                        yalign 0.5
                        action SetDict(js, "pick", ("tool", 0))

        text _("TALISMANS · [_slots] slot(s) at my grade") style "jr_kicker"

        hbox:
            spacing 24
            for _i in range(4):
                if _i < _slots:
                    $ _id = _worn[_i] if _i < len(_worn) else None
                    $ _it = jr_item(_id) if _id else None
                    ## Talismans fill from slot 1 (WP6 appends), so only the
                    ## first empty slot takes a new one.
                    button:
                        style "jr_card_button"
                        xysize (352, 260)
                        sensitive (editable and _i <= len(_worn))
                        action SetDict(js, "pick", ("talisman", _i))
                        vbox:
                            xpos 20
                            ypos 18
                            xsize 312
                            spacing 6
                            text ("SLOT %d" % (_i + 1)) style "jr_kicker"
                            if _it:
                                text _it["name"] font JR_DISPLAY_FONT color gui.paper size 24 xsize 312
                                if _it["grade"]:
                                    use jr_chip(grade_label(_it["grade"]), gui.gold)
                                if _it["effect"]:
                                    text _it["effect"] color gui.violet2 size 16 xsize 312
                                text JR_FX_NOTE style "jr_dim" size 14 xsize 312
                            else:
                                text _("Empty") font JR_DISPLAY_FONT color gui.dim size 24
                                if editable and _i == len(_worn):
                                    text _("Click to wear a talisman.") style "jr_dim" size 16
                                elif editable:
                                    $ _first = len(_worn) + 1
                                    text _("Fill slot [_first] first.") style "jr_dim" size 16
                else:
                    frame:
                        style "jr_card_frame"
                        xysize (352, 260)
                        vbox:
                            xpos 20
                            ypos 18
                            spacing 8
                            text ("SLOT %d" % (_i + 1)) style "jr_kicker" color gui.mute
                            text jr_slot_opens(_i) font JR_DISPLAY_FONT color gui.mute size 24


## The modal picker for a slot or the tool (editable journal only).
screen jr_picker(js):

    $ _kind, _slot = js["pick"]
    $ _opts = jr_pick_options(_kind, _slot)
    $ _worn = jr_worn()
    $ _cur = (jr_tool() if _kind == "tool" else (_worn[_slot] if _slot < len(_worn) else None))

    button:
        style "empty"
        xysize (1920, 1080)
        action SetDict(js, "pick", None)
        add Solid(gui.ink) alpha 0.75

    frame:
        style "jr_panel"
        background Frame("gui/panel_solid.png", 4, 4)
        xalign 0.5
        yalign 0.5
        xsize 980
        padding (36, 30)

        vbox:
            spacing 14
            hbox:
                spacing 16
                use seal("装", 44)
                text (_("Choose a cursed tool") if _kind == "tool" else ("Choose a talisman for slot %d" % (_slot + 1))):
                    font JR_DISPLAY_FONT
                    color gui.paper
                    size 32
                    yalign 0.5

            if not _opts:
                text (_("I don't own a cursed tool yet.") if _kind == "tool" else _("I don't own a talisman yet.")) style "jr_dim"

            ## Five rows or fewer sit in the panel at their own height; more
            ## scroll in a 560px list with a scrollbar.
            if len(_opts) > 5:
                viewport:
                    xsize 920
                    ysize 560
                    scrollbars "vertical"
                    side_spacing 10
                    vscrollbar_xsize 10
                    vscrollbar_unscrollable "hide"
                    mousewheel True
                    draggable True
                    has vbox
                    spacing 8
                    use jr_picker_rows(js, _kind, _slot, _opts)
            elif _opts:
                vbox:
                    spacing 8
                    use jr_picker_rows(js, _kind, _slot, _opts)

            hbox:
                spacing 14
                if _cur:
                    textbutton (_("Bare hands") if _kind == "tool" else _("Unequip")):
                        style "jr_chip_button"
                        action ([Function(equip_tool, None)] if _kind == "tool" else [Function(unequip_talisman, _cur)]) + [SetDict(js, "pick", None)]
                textbutton _("Close"):
                    style "jr_chip_button"
                    action SetDict(js, "pick", None)


## The picker's rows: one button per option (a sensitive one wears it).
screen jr_picker_rows(js, _kind, _slot, _opts):
    for _id, _ok, _why in _opts:
        $ _it = jr_item(_id)
        button:
            style "jr_row_button"
            xsize 900
            sensitive _ok
            action ([Function(equip_tool, _id)] if _kind == "tool" else [Function(jr_wear, _slot, _id)]) + [SetDict(js, "pick", None)]
            vbox:
                spacing 2
                hbox:
                    spacing 12
                    text _it["name"] font JR_DISPLAY_FONT color (gui.paper if _ok else gui.mute) size 22
                    if _it["grade"]:
                        use jr_chip(grade_label(_it["grade"]), (gui.gold if _ok else gui.mute))
                    if _why:
                        text _why color (gui.dim if _ok else gui.seal) size 16 yalign 0.5
                if _it["effect"]:
                    text "[_it['effect']] · [JR_FX_NOTE]" color (gui.violet2 if _ok else gui.mute) size 15 xsize 850


## Inventory ####################################################################

screen jr_inventory_tab(js):

    $ _cat = js["inv_cat"]
    $ _ids = jr_inventory(_cat)
    $ _sel = js["inv_sel"] if js["inv_sel"] in inventory and inventory.get(js["inv_sel"], 0) > 0 else None
    $ _yen = "¥ {:,}".format(yen)

    vbox:
        spacing 14

        fixed:
            xysize (1520, 44)
            hbox:
                spacing 8
                yalign 0.5
                for _k, _lab in JR_INV_CATS:
                    $ _n = jr_inv_count(_k)
                    textbutton "[_lab] [_n]":
                        style "jr_chip_button"
                        text_size 16
                        padding (12, 7)
                        selected (_cat == _k)
                        action [SetDict(js, "inv_cat", _k), SetDict(js, "inv_sel", None)]
            text _yen font JR_DISPLAY_FONT color gui.gold size 30 xalign 1.0 yalign 0.5

        hbox:
            spacing 30

            fixed:
                xysize (920, 856)
                use jr_scroll(920, 856):
                    if not _ids:
                        frame:
                            style "jr_card_frame"
                            xsize 880
                            padding (28, 22)
                            text _("Nothing here yet. Things I pick up along the way end up in here.") style "jr_dim" xsize 820
                    hbox:
                        box_wrap True
                        box_wrap_spacing 16
                        spacing 16
                        for _id in _ids:
                            $ _it = jr_item(_id)
                            $ _c = inventory.get(_id, 0)
                            button:
                                style "jr_card_button"
                                xysize (280, 160)
                                selected (_sel == _id)
                                selected_background Frame("gui/panel_active.png", 4, 4)
                                action SetDict(js, "inv_sel", _id)
                                vbox:
                                    xpos 18
                                    ypos 16
                                    xsize 244
                                    spacing 6
                                    text jr_clip(_it["name"], 40) font JR_DISPLAY_FONT color gui.paper size 21 xsize 244
                                    hbox:
                                        spacing 10
                                        if _c > 1:
                                            text "× [_c]" color gui.paper size 18 yalign 0.5
                                        if _it["grade"]:
                                            use jr_chip(grade_label(_it["grade"]), gui.gold)
                                    text dict(JR_INV_CATS).get(_it["kind"], "") style "jr_dim" size 15

            frame:
                style "jr_panel"
                xysize (570, 856)
                if _sel:
                    $ _it = jr_item(_sel)
                    vbox:
                        spacing 10
                        text _it["name"] font JR_DISPLAY_FONT color gui.paper size 32 xsize 510
                        hbox:
                            spacing 10
                            if _it["grade"]:
                                use jr_chip(grade_label(_it["grade"]), gui.gold)
                            text dict(JR_INV_CATS).get(_it["kind"], "") style "jr_dim" size 16 yalign 0.5
                            if inventory.get(_sel, 0) > 1:
                                $ _selc = inventory.get(_sel, 0)
                                text "× [_selc]" color gui.paper size 18 yalign 0.5
                        if _it["desc"]:
                            text _it["desc"] style "jr_text" xsize 510
                        if _it["source"]:
                            text _("From: [_it['source']]") style "jr_dim" size 17 xsize 510
                        if _it["effect"]:
                            text "[_it['effect']]" color gui.violet2 size 17 xsize 510
                            text JR_FX_NOTE style "jr_dim" size 15 xsize 510
                else:
                    text _("Choose something to look at it.") style "jr_dim" xalign 0.5 yalign 0.5


## Wrappers (kept: the old Status and Journal entry points) ######################

screen jjk_status():
    tag menu
    use journal("stats")

screen jjk_journal():
    tag menu
    use journal("people")
