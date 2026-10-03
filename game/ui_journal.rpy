################################################################################
## Cursed Bonds — the journal.
##
## WP8 (phase 1, PHASE1_DESIGN.md 4.7), rebuilt by P3 in phase 2
## (PHASE2_DESIGN.md 4.7). One full-screen journal with five tabs: People,
## Missions, Stats, Equipment and Inventory. Memories live in People: each
## person's page holds where they are right now, their story, and every scene
## shared with them; the Me page holds the main story's scenes and my records.
##
##   screen journal(tab="people")   tag menu, its own chrome (not game_menu)
##   screen jjk_status()            use journal("stats")   (kept: old callers)
##   screen jjk_journal()           use journal("people")  (kept: old callers)
##
## How it is opened (D4):
##   - on campus, through the loop: Return(("journal", tab)) from the place
##     view, then `call screen journal(tab)` in the main context. Only there
##     is it `editable`: equipment can change, Arc Two can begin
##     (Return(("arc_two",))) and a person's page offers "Go there"
##     (Return(("go", loc)), which the loop hands to rule_walk_to).
##   - from the quick menu or the game menu during a scene: ShowMenu("journal"),
##     a menu context. The Equipment tab is read-only there.
##
## The journal only reads other packages' state, through the frozen section 6
## API (grades WP2, missions WP3, board WP4, memories WP5, items WP6, world
## WP1). The helpers below are tolerant of the shapes those return (a record
## may be a dict or an object; a mission list may hold ids or records), so the
## journal keeps drawing whatever order the packages merge in. Phase 2's
## packages are read only through their contract functions (6.1, 6.2):
## person_now, grade_chip, item_requirements, and the leads and records
## functions of the computer, the river and the card table. Never their
## tables or their saved variables.
##
## The journal's view state (tab, selection, filters) is one dict held in the
## screen, `js`, rather than separate screen variables. The tab bodies are
## screens of their own, and the wrappers `use` the journal, so a plain
## SetScreenVariable would land in the wrong screen's scope; a shared dict
## changed through SetDict works from every one of them.
################################################################################

init python:

    import re
    import unicodedata

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

    ## The clutter budget (4.0): a person's page holds at most this many
    ## words at rest. A learned story line that doesn't fit prints its short
    ## name from THREADS ("The roof"), or, when it has none, its first
    ## JR_LEAD_WORDS words (never fewer than JR_LEAD_MIN); the whole line is
    ## its hover label.
    JR_PAGE_WORDS = 70
    JR_LEAD_WORDS = 4
    JR_LEAD_MIN = 2
    JR_FOLD_WORDS = 2                   # "3 earlier lines"
    JR_TAG_RE = re.compile(r"\{[^{}]*\}")

    JR_FX_NOTE = "Takes effect in combat from the combat update."

    JR_PERIOD_WORDS = {"Morning": "mornings", "Noon": "noon", "Afternoon": "afternoons",
                       "Evening": "evenings", "Night": "nights"}

    def journal_editable():
        """WP8 (D4). True when the journal was opened from campus, in the
        main context (`call screen journal`); False in a menu context (the
        quick menu or the game menu during a scene), where equipment is
        read-only and Arc Two can't begin. Never during a replay."""
        return not renpy.context()._menu and not _in_replay

    ## The sub-panes: a person's page, the Stats tab, the Me page.
    JR_PERSON_SUBS = [("story", "Their story"), ("memories", "Memories")]
    JR_STATS_SUBS = [("overview", "Overview"), ("light", "Last Light"), ("year", "My year")]
    JR_ME_SUBS = [("story", "My story"), ("records", "Records")]

    def journal_state(tab="people"):
        """WP8. A fresh view state for the journal screen. Phase 2 (4.7):
        the Memories tab is gone, so "memories" opens People (a save whose
        loop is about to open ("journal", "memories") lands there). `sel`
        is None, a person, or "me"; psub, ssub and msub2 are the chips of a
        person's page, the Stats tab and the Me page. mem_mode and mem_who
        stay in the dict, unused."""
        if tab == "memories":
            tab = "people"
        if tab not in [t[0] for t in JOURNAL_TABS]:
            tab = "people"
        return dict(tab=tab, sel=None, mfilter="available", msub="story",
                    mem_mode="person", mem_who=None, inv_cat="all", inv_sel=None,
                    pick=None, collapsed={}, psub="story", ssub="overview", msub2="story")

    def jr_fix(js):
        """P3. A guard for a view state that lacks the phase 2 keys or names
        a tab that is gone (one handed in by a harness, say): it is brought
        up to date in place. A load does not need it: it runs `call screen
        journal(tab)` again, so `js` is a fresh journal_state(tab), which is
        what sends "memories" to People. Returns the tab to draw."""
        if js.get("tab") not in [t[0] for t in JOURNAL_TABS]:
            js["tab"] = "people"
        for k, v in (("psub", "story"), ("ssub", "overview"), ("msub2", "story"),
                     ("sel", None), ("pick", None), ("collapsed", None)):
            if k not in js:
                js[k] = {} if k == "collapsed" else v
        return js["tab"]

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

    def jr_next(who, limit=None):
        """"Next: <text> — <where>" from next_for, or "". With limit, the
        whole line is kept to that many characters (the card has room for
        two lines). The where may be WP1's full weekly schedule ("Classroom
        Building (mornings) · Cafeteria (noon) · ..."), so it is shortened
        first by keeping its leading " · " parts (with " …" after them), then
        the where itself is clipped (never below 20 characters), and only
        last the text ("Eat together at Bond 10" keeps its number)."""
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
        text = "" if text is None else str(text)
        ## Wave 0's hand-off: while the roll-call gate holds this person's
        ## next scene, next_for skips it and offers the next unlock ("Eat
        ## together at Bond 10") or "Talk". Say what is really next.
        if text in jr_next_fallbacks(who):
            held = jr_next_hangout(who)
            if held and held[1] == "held":
                return "Next: Spend time together — %s" % (held[2][:1].lower() + held[2][1:])
        if where:
            if limit:
                room = limit - 9                     # "Next: " and " — "
                parts = where.split(" · ")

                def _where(k):
                    return " · ".join(parts[:k]) + (" …" if k < len(parts) else "")

                keep = len(parts)
                while keep > 1 and len(text) + len(_where(keep)) > room:
                    keep -= 1
                where = _where(keep)
                if len(text) + len(where) > room:
                    where = jr_clip(where, max(20, room - len(text)))
                if len(text) + len(where) > room:
                    text = jr_clip(text, max(16, room - len(where)))
                if len(text) + len(where) > room:
                    where = jr_clip(where, max(8, room - len(text)))
            return "Next: %s — %s" % (text, where)
        if limit:
            text = jr_clip(text, max(12, limit - 6))
        return "Next: %s" % text

    ## What the roll-call gate is waiting for, in words (RULE_HANGOUT_AFTER).
    JR_GATE_WORDS = {"roll_call": "After roll call", "sunmall_done": "After the Sun Mall"}

    def jr_next_fallbacks(who):
        """P3. The two lines next_for gives when it found neither a mission
        nor a scene: the next unlock, and "Talk"."""
        out = ["Talk"]
        try:
            nu = next_unlock(who)
        except Exception:
            nu = None
        if nu:
            out.append("%s at %s" % (nu[1], nu[2]))
        return out

    def jr_next_hangout(who):
        """P3. The next scene behind "Spend time together" with someone, as
        (event, state, words), or None when every one has played. state is
        "open" (it plays the next time I spend time with them), "held" (the
        roll-call gate is holding it; words says until when), "need" (words
        is what it needs: "Bond 35", "Bond 50 and ♡ 20") or "later" (it
        waits for the story). A scene I can have now comes first, then the
        one that asks the least."""
        if who not in CAST:
            return None
        b = store.bonds.get(who, 0)
        a = store.affection.get(who, 0)
        found = []
        for e in EVENTS:
            if e["kind"] != "hangout" or e["who"] != who or not e["once"]:
                continue
            if e["label"] in store.done_events or e["arc"] > store.arc or b >= e["max_bond"]:
                continue
            needs = []
            if b < e["min_bond"]:
                needs.append("Bond %d" % e["min_bond"])
            if a < e["min_aff"]:
                needs.append("♡ %d" % e["min_aff"])
            if any(not has_flag(f) for f in e["requires"]) or any(has_flag(f) for f in e["forbids"]):
                state, words = "later", "Later in the story"
            elif needs:
                state, words = "need", " and ".join(needs)
            elif not rule_hangout_gate(e):
                state, words = "held", JR_GATE_WORDS.get(RULE_HANGOUT_AFTER, "Soon")
            else:
                state, words = "open", ""
            rank = {"open": 0, "held": 0, "need": 1, "later": 2}[state]
            found.append(((rank, 1 if e["min_aff"] else 0, e["min_bond"], e["min_aff"]), (e, state, words)))
        if not found:
            return None
        found.sort(key=lambda r: r[0])
        return found[0][1]

    def jr_closer(who):
        """P3. The page's "Closer: ..." line. It is unlock_line(who), except
        while the roll-call gate holds this person's next scene: then
        nothing with them gets closer before roll call, and the line says
        so, as the story's NEXT row does ("Closer: after roll call")."""
        if who not in CAST:
            return ""
        nh = jr_next_hangout(who)
        if nh and nh[1] == "held":
            return "Closer: %s%s" % (nh[2][:1].lower(), nh[2][1:])
        try:
            return unlock_line(who) or ""
        except Exception:
            return ""

    def jr_thread_id(who):
        """P3. The id of this person's thread, or None."""
        for tid in THREAD_ORDER:
            if THREADS[tid]["who"] == who:
                return tid
        return None

    def jr_now(who):
        """P3. person_now(who) (P1's contract), with every key present
        whatever it returned."""
        d = dict(place=None, name="Off campus", doing="", reachable=False, hidden=False, with_me=False)
        try:
            d.update(person_now(who) or {})
        except Exception:
            pass
        return d

    def jr_now_line(pn):
        """P3. The "Right now" line: the place's name and what they're doing
        ("Cafeteria — halfway through an enormous bowl"), or the name alone."""
        name = str(pn.get("name") or "")
        doing = str(pn.get("doing") or "")
        return ("%s — %s" % (name, doing)) if (name and doing) else (name or doing)

    def jr_can_go(pn):
        """P3. Whether the page offers "Go there": only in the campus
        journal, only for a place I can reach, and not for where I already
        stand."""
        return bool(journal_editable() and pn.get("reachable") and pn.get("place")
                    and not pn.get("with_me") and pn.get("place") != store.here)

    def jr_card_place(who):
        """P3. The one dim line on a People card: where they are right now
        ("Cafeteria", "With me", "Off campus"); "Elsewhere" for a room I
        can't enter. "" for Sana, and mid-scene, where "right now" means
        nothing."""
        if who == "sana" or not journal_editable():
            return ""
        pn = jr_now(who)
        if pn.get("hidden"):
            return "Elsewhere"
        return jr_clip(pn.get("name") or "", 26)

    def jr_card_tip(who):
        """P3. A People card's hover label: jr_next(who) on two lines, what
        is next and then where ("Next: Spend time together" / "Cafeteria
        (noon) · ..."). "" when there is nothing next."""
        return jr_next(who).replace(" — ", "\n", 1)

    def jr_card_new(who):
        """P3. The gold dot on a People card: a mission with them can be
        started, or a new scene with them is ready."""
        if store.explore_mode or who not in CAST or not journal_editable():
            return False
        try:
            for m in jr_missions(kind="character", who=who):
                if mission_status(jr_get(m, "id")) in ("available", "active"):
                    return True
            return bool(has_event("hangout", who))
        except Exception:
            return False

    def jr_story_where(who):
        """P3. Where the next step of someone's story happens, in words:
        where they are now when I can walk there, else where they usually
        are. Never empty."""
        pn = jr_now(who)
        if journal_editable() and pn.get("with_me"):
            return "with me now"
        if journal_editable() and pn.get("place") and not pn.get("hidden"):
            return "%s, right now" % pn.get("name")
        try:
            usual = usual_places(who) or ""
        except Exception:
            usual = ""
        first = usual.split(" · ")[0].strip()
        if not first:
            return "around campus"
        return ("usually " + first) if "(" in first else first

    def jr_mission_where(m, who):
        """P3. Where a mission that can be started happens, for the NEXT
        row: its own place and time; for one that starts wherever its giver
        is, where that person is (jr_story_where), not "wherever Maki is"."""
        if jr_get(m, "where") is None and jr_get(m, "trigger", "auto") != "auto":
            return jr_story_where(who)
        return jr_where_when(m) or jr_story_where(who)

    def jr_stage_short(tid, i):
        """P3. The short name of a thread's stage ("The roof"), or ""."""
        names = THREADS.get(tid, {}).get("short") or []
        return names[i] if 0 <= i < len(names) else ""

    def jr_story_row(kind, title="", line="", state="", where="", next=False, **more):
        d = dict(kind=kind, title=title, line=line, state=state, where=where, next=next)
        d.update(more)
        return d

    def jr_story_rows(who):
        """P3 (ui_journal.rpy). A person's story as a list of
        dict(kind, title, line, state, where, next), for their page (4.7).

        kind "heading": the thread's title (state "done" once resolved).
        kind "stage":   a thread line I have learned (state "done"); it
                        carries "short", its name in a word or two.
        kind "mission": one of their missions; state is "done", "next",
                        "available", "waiting", "locked" or "closed".
        kind "step":    the next thing to do when it isn't a mission
                        ("Spend time together", line "Bond 35").
        kind "later":   every unwritten mission, as one row.

        Order: the heading; what is done (stages in order, each followed by
        the mission it unlocks, then the other missions in act order); the
        one row with next=True, which says where; what is still closed; the
        "later build" row. A stage not learned yet is not listed."""
        rows = []
        if who == "sana":
            return rows
        tid = jr_thread_id(who)
        cur = thread_stage(tid) if tid else -1
        ms = [jr_mrec(m) for m in jr_missions(kind="character", who=who)]
        if tid:
            T = THREADS[tid]
            rows.append(jr_story_row("heading", title=T["title"],
                                     state=("done" if thread_done(tid) else ("open" if cur >= 0 else "locked"))))
        slotted, free = {}, []
        for m in ms:
            g = jr_get(jr_get(m, "gate", None) or {}, "thread")
            if tid and g and g[0] == tid:
                slotted.setdefault(g[1], []).append(m)
            else:
                free.append(m)
        order = []
        if tid:
            for i, line in enumerate(THREADS[tid]["stages"]):
                if i <= cur:
                    order.append(("stage", (i, line)))
                for m in slotted.get(i, []):
                    order.append(("mission", m))
        for m in free:
            order.append(("mission", m))

        done, ready, closed, later = [], [], [], 0
        for kind, x in order:
            if kind == "stage":
                done.append(jr_story_row("stage", line=x[1], state="done",
                                         short=jr_stage_short(tid, x[0])))
                continue
            mid = jr_get(x, "id")
            try:
                status = mission_status(mid)
            except Exception:
                status = "locked"
            title = jr_get(x, "title", mid) or mid
            if status == "unwritten":
                later += 1
            elif status in ("done", "skipped"):
                done.append(jr_story_row("mission", title=title, state="done", id=mid,
                                         line=("Passed by" if status == "skipped" else "")))
            elif status in ("available", "active"):
                ready.append(jr_story_row("mission", title=title, state="available", id=mid,
                                          line=jr_get(x, "objective", "") or "",
                                          where=jr_mission_where(x, who)))
            elif status == "closed":
                closed.append(jr_story_row("mission", title=title, state="closed", id=mid,
                                           line="Closed when Arc Two began"))
            else:
                try:
                    why = mission_reason(mid) or ""
                except Exception:
                    why = ""
                closed.append(jr_story_row("mission", title=title, state=status, id=mid,
                                           line=why or "Not yet"))

        nxt = None
        if ready:
            nxt = ready.pop(0)
        else:
            h = jr_next_hangout(who)
            if h:
                ## Once their thread is resolved the next scene is not
                ## another chapter of it.
                nxt = jr_story_row("step", line=h[2], where=jr_story_where(who),
                                   title=("More time together" if (tid and thread_done(tid))
                                          else "Spend time together"))
            else:
                try:
                    nu = next_unlock(who) if who in CAST else None
                except Exception:
                    nu = None
                if nu:
                    nxt = jr_story_row("step", title=nu[1], line=nu[2], where=jr_story_where(who))
        if nxt is None:
            ## Nothing to do but wait: the first mission still locked is
            ## the NEXT row (4.7: the first row not done), with what it
            ## waits for and where it will be.
            for r in closed:
                if r["state"] != "closed":
                    closed.remove(r)
                    r["where"] = jr_story_where(who)
                    nxt = r
                    break
        if nxt:
            nxt["next"] = True
            nxt["state"] = "next"
        rows.extend(done)
        if nxt:
            rows.append(nxt)
        rows.extend(ready)
        rows.extend(closed)
        if later:
            rows.append(jr_story_row("later", state="later",
                                     line=("1 more chapter in a later build" if later == 1
                                           else "%d more chapters in a later build" % later)))
        return rows

    ## The page's word budget (4.0) ---------------------------------------------

    def jr_is_word(tok):
        """P3. A token that holds a Latin letter: "+2" and "◆ 1" are not
        words (4.0's rule for the clutter budget)."""
        for ch in tok:
            if ch.isalpha() and unicodedata.name(ch, "").startswith("LATIN"):
                return True
        return False

    def jr_word_count(*texts):
        """P3. How many words the given strings put on the screen, text tags
        left out."""
        n = 0
        for t in texts:
            if not t:
                continue
            plain = JR_TAG_RE.sub(" ", str(t).replace("{{", " "))
            n += len([k for k in plain.split() if jr_is_word(k)])
        return n

    def jr_lead(line, n):
        """P3. The first n words of a line and an ellipsis ("He is the
        loudest…"). Never fewer than JR_LEAD_MIN words: a row is never a
        bare ellipsis."""
        n = max(JR_LEAD_MIN, n)
        out, words = [], 0
        for tok in str(line or "").split():
            if words >= n:
                break
            out.append(tok)
            if jr_is_word(tok):
                words += 1
        return (" ".join(out).rstrip(",.;:") + "…") if out else "…"

    def jr_usual_first(us):
        """P3. The first of someone's usual places ("Dojo (mornings and
        noon) …"), with an ellipsis when there are more."""
        parts = str(us or "").split(" · ")
        return parts[0] + (" …" if len(parts) > 1 else "")

    def jr_text_width(s, font, size):
        """P3. How wide a string draws, in pixels (0 if it can't be
        measured)."""
        try:
            return Text(s, font=font, size=size, substitute=False, layout="nobreak").size()[0]
        except Exception:
            return 0

    def jr_fit_name(s, font, size, floor, width):
        """P3. A name that must fit `width` pixels, as (text, size): drawn
        smaller, down to `floor`, and then clipped a letter at a time."""
        s = str(s or "")
        while size > floor and jr_text_width(s, font, size) > width:
            size -= 2
        n = len(s)
        out = s
        while n > 4 and jr_text_width(out, font, size) > width:
            n -= 1
            out = jr_clip(s, n)
        return out, size

    def jr_story_sub(r):
        """P3. The small line under a story row's title: its line and where."""
        return jr_clip(" · ".join([p for p in (r["line"], r["where"]) if p]), 110)

    def jr_story_brief(r):
        """P3. A learned line in a word or two, for when the whole of it
        doesn't fit: its short name, else its first JR_LEAD_MIN words."""
        return r.get("short") or jr_lead(r["line"], JR_LEAD_MIN)

    def jr_story_fit(rows, room):
        """P3. jr_story_rows' rows as the page draws them at rest, inside a
        budget of `room` words (4.0: a person's page holds 70). Each copy
        gains:
          "show"  what a learned stage line prints at rest: the whole line
                  while there is room, the newest first; else its short
                  name ("The roof"), or its first words and an ellipsis
                  when it has none. Whole lines are always the newest
                  run: nothing older than a cut line prints whole;
          "tip"   the whole text for the hover label when the row is cut
                  short ("" when it is not);
          "sub"   the small line of a mission or step row ("" when folded
                  into the hover label).
        Every row stays a row, with one exception: when even the short
        names don't fit, the oldest learned lines become one row, "3 earlier
        lines" ("fold": 3), whose hover label lists them whole. A row is
        never a bare ellipsis. The NEXT row is never cut. The frozen rows
        are not changed."""
        out = [dict(r, show=r.get("line", ""), tip="", sub="") for r in rows]
        title = ""
        used = 0
        for r in out:
            if r["kind"] == "heading":
                title = r["title"]
                used += jr_word_count(r["title"]) + (1 if r["state"] == "done" else 0)
            elif r["kind"] == "later":
                used += jr_word_count(r["line"])
            elif r["kind"] != "stage":
                r["sub"] = jr_story_sub(r)
                used += jr_word_count(jr_clip(r["title"], 60), r["sub"]) + (1 if r["next"] else 0)
        if not out:
            return out
        ## Too much even before the story's own lines: the other chapters
        ## keep their titles and move their small lines to the hover label,
        ## from the bottom up.
        for r in reversed(out):
            if used <= room:
                break
            if r["kind"] in ("mission", "step") and not r["next"] and r["sub"]:
                used -= jr_word_count(r["sub"])
                r["tip"] = "%s\n%s" % (r["title"], r["sub"])
                r["sub"] = ""
        left = max(0, room - used)
        head = title or "Their story"
        stages = [r for r in out if r["kind"] == "stage"]
        costs = [jr_word_count(jr_story_brief(r)) for r in stages]
        ## Not even the short names fit: fold the oldest lines into one row.
        fold = 0
        while fold < len(stages) and sum(costs[fold:]) + (JR_FOLD_WORDS if fold else 0) > left:
            fold += 1
        if fold:
            gone = stages[:fold]
            row = dict(gone[0], line="", short="", fold=fold,
                       show=("1 earlier line" if fold == 1 else "%d earlier lines" % fold),
                       tip="\n".join([head] + [g["line"] for g in gone]))
            out[out.index(gone[0])] = row
            out = [r for r in out if not any(r is g for g in gone)]
            stages, costs = stages[fold:], costs[fold:]
            left = max(0, left - JR_FOLD_WORDS)
        ## The newest line is served first; an older one keeps at least its
        ## short name. Once a line has had to take its short name, every
        ## older one does too, so the whole lines are always the newest run
        ## and the list never reads name, sentence, name.
        cut = False
        for j in range(len(stages) - 1, -1, -1):
            r = stages[j]
            spare = left - sum(costs[:j])
            w = jr_word_count(r["line"])
            if w <= spare and not cut:
                left -= w
                continue
            cut = True
            r["show"] = r.get("short") or jr_lead(r["line"], min(JR_LEAD_WORDS, spare))
            r["tip"] = "%s\n%s" % (head, r["line"])
            left = max(0, left - jr_word_count(r["show"]))
        return out

    ## The People grid ------------------------------------------------------------

    def jr_people_cards():
        """P3. The cards of the People grid, in order: Me, everyone met in
        JOURNAL_CAST order, then Sana. Each is a journal_cast() dict; the Me
        card is dict(who="me", ...). A card may carry "key", its button's id
        (jr_card_<key>), when two cards show one person."""
        cast = journal_cast()
        me = dict(who="me", name=(store.mc_name if jr_name_known() else "Me"),
                  color=CAST.get("mc", {}).get("color", gui.violet2), role="", hint="",
                  met=True, art=True)
        return ([me] + [e for e in cast if e["met"] and e["who"] != "sana"]
                + [e for e in cast if e["who"] == "sana"])

    def jr_people_unmet():
        """P3. The JOURNAL_CAST people not met yet, for the bottom row."""
        return [e for e in journal_cast() if not e["met"] and e["who"] != "sana"]

    def jr_face(who, size=72):
        """P3. A square face, size x size: WP1's face_chip for a person; for
        "me", the same crop of my own side portrait (the Yotsuka outfit until
        the campus opens)."""
        if who != "me":
            return face_chip(who, size)
        path = "images/side/mc_neutral.png" if has_flag("settled_in") else "images/side/mcyotsuka_neutral.png"
        if not renpy.loadable(path):
            return Text("？", font=gui.display_font, size=int(size * 0.6), color=gui.mute)
        return Transform(path, crop=(124, 0, 112, 112), xysize=(size, size))

    def jr_grade_chip(who, role=""):
        """P3. What a person's grade chip shows, as (grade key or None, text
        or None): Gojo's is ("sp", "Off the scale") on the Special fill; the
        ungraded get (None, their role); nobody with neither gets (None, None)."""
        try:
            st = npc_stats(who) or {}
        except Exception:
            st = {}
        if st.get("off_scale"):
            return ("sp", "Off the scale")
        if st.get("grade"):
            return (st.get("grade"), None)
        text = st.get("role") or role or CAST.get(who, {}).get("year", "")
        return (None, text or None)

    ## A person's page, the Me page ---------------------------------------------------

    def jr_page_memories(who):
        """P3. The tiles on someone's page: WP5's memories_with(who), each a
        memory_entry() (so an unseen tile has its `text`, which never names
        someone not met)."""
        try:
            return [m for m in (memories_with(who) or []) if m]
        except Exception:
            return jr_memories_with(who)

    def jr_me_groups():
        """P3. [(act title, [entry])] for the Me page's "My story": WP5's
        memory_groups("act") without the Bonds group (those are on the
        people's own pages). It holds the scenes nobody else is in."""
        out = []
        for title, mems in jr_memory_groups("act"):
            mems = [m for m in mems if jr_get(m, "act") != "Bonds"]
            if mems:
                out.append((title, mems))
        return out

    def jr_records():
        """P3. The Me page's Records, read through three contract functions
        only: [(heading, [line])], a section with nothing in it left out."""
        out = []
        try:
            pages = [str(t) for t in (pc_records() or [])]
        except Exception:
            pages = []
        if pages:
            out.append(("PAGES I'VE READ", pages))
        try:
            fish = list(fish_records() or [])
        except Exception:
            fish = []
        lines = []
        for r in fish:
            if isinstance(r, (tuple, list)) and len(r) >= 2:
                lines.append("%s — %s" % (r[0], ("%s cm" % r[1]) if r[1] else "not caught yet"))
        if lines:
            out.append(("THE RECORD BOOK", lines))
        try:
            won = int((cards_records() or {}).get("today", 0) or 0)
        except Exception:
            won = 0
        if won:
            out.append(("AT THE CARD TABLE", ["%s today: ¥%s" % ("Won" if won > 0 else "Lost", "{:,}".format(abs(won)))]))
        return out

    def jr_leads():
        """P3. The Missions tab's leads, from pc_leads() (P6's contract):
        one line each, "Look up what was on the ridge — my computer"."""
        out = []
        try:
            leads = list(pc_leads() or [])
        except Exception:
            leads = []
        for l in leads:
            note = ""
            if isinstance(l, (tuple, list)):
                note = str(l[1]) if len(l) > 1 and l[1] else ""
            elif l:
                note = str(l)
            note = note.strip() or "Something to look up"
            if "computer" not in note.lower():
                note += " — my computer"
            out.append(note)
        return out

    def jr_reqs(iid):
        """P3. item_requirements(iid) (P4a's contract) as a list of
        (line, met): the checklist under a tool or a talisman. [] when the
        item asks for nothing."""
        try:
            return [(str(r[0]), bool(r[1])) for r in (item_requirements(iid) or [])]
        except Exception:
            return []

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

    def jr_aff_scale(who):
        """The heart meter's full scale: 100, or 200 once the confession has
        lifted the cap (AFF_TRUE_MAX), so the meter keeps showing progress."""
        try:
            return max(AFF_BASE_MAX, aff_cap(who))
        except Exception:
            return AFF_BASE_MAX

    def jr_aff_marker(who):
        """Where the heart meter's cap marker goes: the bond's cap, or None
        once together (the cap is then the meter's own end)."""
        if is_together(who):
            return None
        return aff_cap(who)

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
        d["aff_max"] = jr_aff_scale(who)
        d["aff_marker"] = jr_aff_marker(who) if d["romance"] else None
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
        ## WP4 gives the log newest first (board_summary: "the last 10
        ## runs, newest first"), which is the order the tab shows.
        log = list(jr_get(s, "log", None) or jr_get(s, "recent", None) or jr_get(s, "runs", None) or [])[:10]
        try:
            mis = jr_get(s, "misgrades", None)
            if mis is None:
                mis = misgrade_count()
        except Exception:
            mis = 0
        return dict(where=where, offers=offers, taken=taken, log=log,
                    misgrades=mis or 0, empty=not (offers or taken or log))

    def jr_board_place(key):
        """A board place as the player reads it. WP4's offers carry a
        BOARD_PLACES key ("kita"); show its phrase ("an apartment stairwell
        in Kita"). Anything that isn't a known key is shown as it is."""
        if not key:
            return ""
        by_key = getattr(store, "BOARD_PLACE_BY_KEY", None) or {}
        p = by_key.get(key) if isinstance(by_key, dict) else None
        if p:
            return p.get("phrase") or p.get("short") or str(key)
        return str(key)

    def jr_offer_line(o):
        parts = [jr_get(o, "case"), jr_board_place(jr_get(o, "place"))]
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
        """The tile's thumbnail: the memory's background, 280x158. Cropped:
        a 16:9 picture made to cover the tile comes out a pixel too wide."""
        bg = jr_get(m, "bg")
        d = None
        if bg:
            if renpy.has_image(bg):
                d = bg
            elif renpy.loadable(bg):
                d = bg
        if d is None:
            return Solid(gui.panel2, xysize=(280, 158))
        return Crop((0, 0, 280, 158), Transform(d, xysize=(280, 158), fit="cover"))

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

    def jr_name_known():
        """WP8. Whether the player's name may be shown: not on the main menu,
        and only once the save is past the ch1_gojo step, where Gojo asks
        for it (2.3: nobody uses the name before he asks)."""
        if main_menu:
            return False
        return jr_prologue_index() > jr_step_index("ch1_gojo")

    def jr_is_met(who):
        """Whether the People tab counts this person as met (their
        JOURNAL_CAST entry's rule); someone with no entry counts as met."""
        e = jr_cast_entry(who)
        return True if e is None else journal_met(e)

    def jr_stats_title():
        """The Stats tab's header: "<surname> <name>", or "My journal" before
        Gojo asks the name."""
        if not jr_name_known():
            return _("My journal")
        return "%s %s" % (store.mc_surname, store.mc_name)

    def jr_year():
        """The "Your year" strip: [(name, colour, reserve or None, off_scale)].
        The player's row reads "Me" until the name is asked; the others show
        only once the People tab counts them as met."""
        me = store.mc_name if jr_name_known() else _("Me")
        out = [(me, CAST.get("mc", {}).get("color", gui.violet2), store.ce_max, False)]
        for who in ("yuji", "megumi", "nobara", "gojo"):
            if not jr_is_met(who):
                continue
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
                if iid == cur:
                    out.append((iid, False, "In my hand"))
                    continue
                ## 4.7: the picker says why WP6 won't let me hold one.
                try:
                    ok, why = can_hold(iid)
                except Exception:
                    ok, why = (True, "")
                out.append((iid, bool(ok), why or ""))
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

    def jr_hold(iid):
        """WP8. Take a cursed tool in hand (None: bare hands) through WP6's
        equip_tool. Returns None on purpose: WP6 returns True/False, and a
        button action that returns anything but None ends the interaction,
        which would close the journal (and hand the value to the caller)."""
        equip_tool(iid)

    def jr_takeoff(iid):
        """WP8. Take a talisman off through WP6's unequip_talisman. Returns
        None for the same reason as jr_hold."""
        unequip_talisman(iid)

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

style jr_unmet_button is button:
    background Frame("gui/panel_ghost.png", 4, 4)
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (0, 0)

style jr_strength_button is button:
    background Solid("#07060cb0")
    padding (14, 10)

## A button that is only there to carry a hover label.
style jr_plain_button is button:
    background None
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
    ## jr_fix: a guard for a `js` without the phase 2 keys (a load builds a
    ## fresh one from journal_state(tab)).
    $ _cur = jr_fix(js)
    ## Explore mode never fires the story, so it shows no story goal.
    $ _obj = "" if explore_mode else (objective_text() or "")
    $ _idle = _("Explore mode: no story here.") if explore_mode else (_("Nothing pressing. Go and see who's around.") if jr_on_campus() else _("Nothing pressing."))

    add gui.game_menu_background
    add Solid(gui.ink) alpha 0.86

    ## Esc and right-click: close the picker or the detail pane, else leave.
    if js.get("pick") is not None:
        key "game_menu" action SetDict(js, "pick", None)
    elif js.get("sel") is not None and _cur == "people":
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
                ## 44 high, so the first tab sits at y 148 (4.7).
                fixed:
                    xysize (260, 44)
                    hbox:
                        yalign 0.5
                        spacing 16
                        add icon("journal", 44) yalign 0.5
                        text _("Journal"):
                            font JR_DISPLAY_FONT
                            color gui.paper
                            size 40
                            yalign 0.5
                use rule(260)
                null height 10

                ## Five tabs (4.7): the first at y 148, then every 86 px. The
                ## rail is a table of contents, so each icon keeps its word.
                for _k, _kan, _lab in JOURNAL_TABS:
                    $ _badge = ""
                    if _in_replay:
                        pass
                    elif _k == "missions":
                        $ _n = 0 if explore_mode else jr_mission_counts()
                        $ _badge = str(_n) if _n else ""
                    elif _k == "inventory":
                        $ _n = jr_inv_count("all")
                        $ _badge = str(_n) if _n else ""
                    button:
                        id "jr_tab_" + _k
                        style "jr_tab_button"
                        selected (_cur == _k)
                        sensitive (not _in_replay)
                        action [SetDict(js, "sel", None), SetDict(js, "pick", None), SetDict(js, "tab", _k)]
                        fixed:
                            hbox:
                                spacing 14
                                yalign 0.5
                                add icon(icon_for("tab", _k), 44) yalign 0.5
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
                id "jr_return"
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

        ## A replay runs in a clean store (3.9), so the journal would show a
        ## wiped save: say so instead.
        if _in_replay:
            use jr_replay_note()
        else:

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
                        ## One line only: a long objective drops to 18 px.
                        text (jr_clip(_obj, 120) if _obj else _idle):
                            font JR_DISPLAY_FONT
                            color (gui.paper if _obj else gui.dim)
                            size (22 if len(_obj) <= 104 else 18)
                            yalign 0.5

            fixed:
                ypos 72
                xysize (1520, 928)

                if _cur == "people":
                    use jr_people(js)
                elif _cur == "missions":
                    use jr_missions_tab(js, editable)
                elif _cur == "stats":
                    use jr_stats_tab(js)
                elif _cur == "equipment":
                    use jr_equipment_tab(js, editable)
                elif _cur == "inventory":
                    use jr_inventory_tab(js)

    if js["pick"] is not None and _cur == "equipment" and editable:
        use jr_picker(js)


## During a replay: one panel in place of the tabs.
screen jr_replay_note():
    frame:
        xalign 0.5
        ypos 260
        xsize 900
        background Frame("gui/panel_dark.png", 4, 4)
        padding (48, 40)
        vbox:
            spacing 16
            text _("The journal isn't kept during a replay."):
                font JR_DISPLAY_FONT
                color gui.paper
                size 34
            text _("End the replay to see it again."):
                font JR_BODY_FONT
                color gui.dim
                size 22


## People #######################################################################

## The grid (4.7): cards 288x196, five across (5 x 288 + 4 x 20 = 1520), in a
## viewport. Thirteen cards are three rows; all seventeen people and Me are
## four (844 px), inside the 928 px body. The bar sits in the margin right of
## the body and shows only when the cards are taller than it.
screen jr_people(js):

    $ _sel = js.get("sel")

    if _sel == "me":
        use jr_me_detail(js)

    elif _sel is not None:
        use jr_person_detail(js, _sel)

    else:
        $ _unmet = jr_people_unmet()
        viewport:
            id "jr_people_vp"
            xysize (1520, 928)
            mousewheel True
            draggable True
            pagekeys True
            vbox:
                spacing 20
                hbox:
                    box_wrap True
                    box_wrap_spacing 20
                    spacing 20
                    for _e in jr_people_cards():
                        use jr_person_card(js, _e)
                if _unmet:
                    vbox:
                        spacing 8
                        text _("NOT MET YET") style "jr_kicker" size 14
                        hbox:
                            spacing 12
                            for _e in _unmet:
                                use jr_unmet_chip(_e)
        vbar:
            value YScrollValue("jr_people_vp")
            xpos 1528
            xsize 10
            ysize 928
            unscrollable "hide"


## One card. At rest: the face, the name, the grade chip, the bond bar and one
## dim line with where they are right now. Hover: "Next: ...".
screen jr_person_card(js, e):

    $ _who = e["who"]
    $ _key = "jr_card_" + str(e.get("key") or _who)
    $ _col = e["color"]

    if _who == "me":
        $ _g = player_grade()
        button:
            id _key
            style "jr_card_button"
            xysize (288, 196)
            action [SetDict(js, "msub2", "story"), SetDict(js, "sel", "me")]
            tooltip (_("Me\nThe story so far, and what I've kept a record of."), _key)
            fixed:
                hbox:
                    xpos 20
                    ypos 22
                    spacing 14
                    fixed:
                        xysize (72, 72)
                        add Solid(gui.panel2)
                        add jr_face("me", 72)
                    vbox:
                        yalign 0.5
                        spacing 8
                        ## substitute False: the player typed this name.
                        text jr_clip(e["name"], 11) substitute False font JR_DISPLAY_FONT color _col size 24
                        if _g:
                            use grade_chip(_g, 13)
                        else:
                            use grade_chip(None, 13, text=_("Not yet assessed"))
                add Solid(gui.line) xpos 20 ypos 119 xysize (248, 1)
                text _("My story") style "jr_dim" size 15 xpos 20 ypos 144

    elif _who == "sana":
        button:
            id _key
            style "jr_card_button"
            xysize (288, 196)
            action [SetDict(js, "psub", "memories"), SetDict(js, "sel", "sana")]
            fixed:
                hbox:
                    xpos 20
                    ypos 22
                    spacing 14
                    fixed:
                        xysize (72, 72)
                        add Solid(gui.panel2)
                        add jr_face(_who, 72)
                    vbox:
                        yalign 0.5
                        spacing 8
                        text CAST.get("sana", {}).get("short", "Sana") font JR_DISPLAY_FONT color _col size 24
                        use jr_chip(_("In memory"), gui.gold)
                add Solid(gui.line) xpos 20 ypos 119 xysize (248, 1)

    else:
        $ _gk, _gt = jr_grade_chip(_who, e["role"])
        $ _promo = jr_recently_promoted(_who)
        $ _gtxt = ((_gt or grade_label(_gk)) + " ↑") if (_promo and _gk) else _gt
        $ _b = bonds.get(_who, 0)
        $ _nx = jr_card_tip(_who)
        $ _pl = jr_card_place(_who)
        $ _nm = jr_short(_who)
        button:
            id _key
            style "jr_card_button"
            xysize (288, 196)
            action [SetDict(js, "psub", "story"), SetDict(js, "sel", _who)]
            tooltip ((_nx, _key) if _nx else None)
            fixed:
                hbox:
                    xpos 20
                    ypos 22
                    spacing 14
                    fixed:
                        xysize (72, 72)
                        add Solid(gui.panel2)
                        add jr_face(_who, 72) xalign 0.5 yalign 0.5
                    vbox:
                        yalign 0.5
                        spacing 8
                        text jr_clip(_nm, 11) font JR_DISPLAY_FONT color _col size 24
                        if _gk or _gtxt:
                            use grade_chip(_gk, (13 if len(_gtxt or "") <= 14 else 11), text=_gtxt)
                fixed:
                    xpos 20
                    ypos 116
                    xysize (248, 14)
                    use jr_meter(_b, 100, width=248, height=6, fill=_col)
                if _pl:
                    text _pl style "jr_dim" size 15 xpos 20 ypos 144
                ## Something new with them: a mission, or a scene that is ready.
                if jr_card_new(_who):
                    text "●" color gui.gold size 14 xpos 256 ypos 10


## Someone not met yet: a 72x72 silhouette; the hint is the hover label.
screen jr_unmet_chip(e):
    $ _key = "jr_unmet_" + str(e["who"])
    button:
        id _key
        style "jr_unmet_button"
        xysize (72, 72)
        action NullAction()
        tooltip ((_("Not met yet") + "\n" + (e["hint"] or "")), _key)
        if e["art"]:
            add face_chip(e["who"], 72) at Transform(matrixcolor=TintMatrix("#000000"), alpha=0.85)
        else:
            text "？" font gui.display_font size 40 color gui.mute xalign 0.5 yalign 0.5


## A person's page (4.7): the sprite left; the header, "Right now", and two
## chips over one pane (their story, or the memories shared with them).
##
## The page holds at most JR_PAGE_WORDS words at rest (4.0). What it prints
## outside the story list is counted first, and jr_story_fit fits the list
## into the rest. Three things wait on hover so the story keeps its room:
## "Usually: ..." while I can see where they are (the Right now block), what
## holds the heart bar back, and the whole of a story line cut short.
screen jr_person_detail(js, who):

    $ _d = jr_person(who)
    $ _col = _d["color"]
    $ _sana = (who == "sana")
    $ _live = journal_editable()
    $ _pn = jr_now(who)
    $ _mems = jr_page_memories(who)
    $ _seen = len([m for m in _mems if jr_mem_state(m) == "seen"])
    $ _sub = "memories" if _sana else js.get("psub", "story")
    $ _gk, _gt = jr_grade_chip(who, _d["grade"])
    $ _hover = "\n".join([t for t in (_d["blurb"], _d["note"]) if t])

    ## What the page prints outside the story list, worked out here so the
    ## list can be fitted into what is left of the 70 words (4.0).
    $ _year = _d["year"] if (_d["year"] and _d["year"] != _d["grade"]) else ""
    $ _pl = jr_promotions(who)
    $ _prom = (_("Promoted Day %s") % _pl[-1][0]) if _pl else ""
    $ _heart = ("♡ " + _d["aff_rank"]) if _d["romance"] else ""
    ## I can see where they are: the place has a name I'm allowed to know.
    $ _seen_now = bool(_live and (_pn.get("with_me") or (_pn.get("place") and not _pn.get("hidden"))))
    ## 72 characters is one line of the 900 px block at size 22.
    $ _now = jr_clip(jr_now_line(_pn), 72) if _live else ""
    $ _us = jr_clip(_d["usual"] or _("Around campus."), 104)
    ## "In his office today." needs a place to stand on: beside "Off campus"
    ## (no place at all) it would contradict the line above it.
    $ _today = _("In his office today.") if (_d["office_today"] and (not _live or _pn.get("place"))) else ""
    ## When I can't see where they are, the first of their usual places is
    ## printed (the rest on hover); mid-scene, all of them.
    $ _line2 = "" if _seen_now else (_today or (_us if not _live else (_("Usually: ") + jr_usual_first(_us))))
    $ _ul = jr_closer(who)
    $ _chip_mem = "Memories %d/%d" % (_seen, len(_mems))
    $ _words = jr_word_count(_d["name"], (_gt or (grade_label(_gk) if _gk else "")), _year, _d["bond_rank"], _prom, _heart,
                             (_("RIGHT NOW") if _live else _("USUALLY")), _now, _line2, _ul, _("Their story"), _chip_mem, _("← Back"))
    if _d["has_stats"]:
        $ _words += 4 + (2 if _d["restricted"] else 0)

    frame:
        style "jr_panel_dark"
        xysize (1520, 928)
        padding (0, 0)
        fixed:

            ## Left, x 0 to 420: the raw sprite, unlit, at zoom 0.5.
            fixed:
                xpos 0
                xysize (420, 928)
                if renpy.loadable(_d["sprite"]):
                    add _d["sprite"] zoom 0.5 xalign 0.5 yalign 1.0 yoffset -10
                else:
                    text "「？」" size 120 color gui.mute xalign 0.5 yalign 0.5

                ## Strength, kept from phase 1 in a small block over the
                ## sprite's head room. Their blurb and note are its hover label.
                if _d["has_stats"]:
                    button:
                        id "jr_strength"
                        style "jr_strength_button"
                        xpos 20
                        ypos 20
                        xsize 380
                        action NullAction()
                        tooltip ((_hover, "jr_strength") if _hover else None)
                        vbox:
                            spacing 5
                            text _("STRENGTH") style "jr_kicker" size 13
                            hbox:
                                spacing 10
                                text _("Reserve") style "jr_dim" size 15 min_width 70 yalign 0.5
                                if _d["restricted"]:
                                    text _("Heavenly Restriction") color gui.gold size 15 yalign 0.5
                                elif _d["off_scale"]:
                                    use jr_meter(300, 300, width=180, height=6, fill=_col, off_scale=True)
                                elif _d["reserve"] is not None:
                                    use jr_meter(_d["reserve"], 300, width=220, height=6, fill=_col)
                                    text "[_d['reserve']]" style "jr_dim" size 14 yalign 0.5
                            for _lab, _k in ((_("Control"), "control"), (_("Output"), "output")):
                                hbox:
                                    spacing 10
                                    text _lab style "jr_dim" size 15 min_width 70 yalign 0.5
                                    if _d["off_scale"]:
                                        use jr_meter(100, 100, width=180, height=6, fill=_col, off_scale=True)
                                    elif _d[_k] is not None:
                                        use jr_meter(_d[_k], 100, width=220, height=6, fill=_col)
                                        text str(_d[_k]) style "jr_dim" size 14 yalign 0.5

            ## Header, x 450, y 24: name, grade chip, year.
            hbox:
                xpos 450
                ypos 24
                spacing 16
                text _d["name"] font JR_DISPLAY_FONT color _col size 40 yalign 0.5
                vbox:
                    yalign 0.5
                    if _sana:
                        use jr_chip(_("In memory"), gui.gold)
                    elif _gk or _gt:
                        use grade_chip(_gk, 15, text=_gt)
                if _year:
                    text _year style "jr_dim" size 17 yalign 0.5

            ## y 84: the bond bar, 620x10, with the rank and number under it;
            ## the heart bar at x 1100 when it applies; then the promotions.
            if not _sana:
                fixed:
                    xpos 450
                    ypos 84
                    xysize (1040, 44)
                    use jr_meter(_d["bond"], 100, width=620, height=10, fill=_col)
                    hbox:
                        ypos 20
                        spacing 24
                        text "[_d['bond_rank']] · [_d['bond']]" style "jr_dim" size 16
                        ## The latest promotion; the chip by the name says
                        ## which grade.
                        if _prom:
                            text _prom style "jr_dim" size 16
                    if _d["romance"]:
                        ## The heart bar. What holds it back ("Affection
                        ## can't pass 40 until Bond 50") is its hover label.
                        button:
                            id "jr_heart"
                            style "jr_plain_button"
                            xpos 650
                            xysize (390, 44)
                            action NullAction()
                            tooltip (((_heart + "\n" + _d["aff_note"]), "jr_heart") if _d["aff_note"] else None)
                            fixed:
                                use jr_meter(_d["aff"], _d["aff_max"], width=380, height=6, fill=gui.romance, marker=_d["aff_marker"])
                                text _heart color gui.romance size 16 ypos 20

                ## Right now, (450, 140), 1040x112.
                frame:
                    xpos 450
                    ypos 140
                    xysize (1040, 112)
                    background Frame("gui/panel.png", 4, 4)
                    padding (20, 4, 16, 5)
                    fixed:
                        ## While I can see where they are, "Usually: ..." is
                        ## this block's hover label. When I can't (off
                        ## campus, a room I can't enter) the first of their
                        ## usual places is printed, because it is then the
                        ## way to find them, and the rest stay on hover.
                        ## On a day Gojo is in, "In his office today."
                        ## takes that line. Mid-scene the list is whole.
                        button:
                            id "jr_now"
                            style "jr_plain_button"
                            xsize 900
                            action NullAction()
                            tooltip (((_("Usually") + "\n" + _us), "jr_now") if (_live and (_seen_now or _line2 != _("Usually: ") + _us)) else None)
                            vbox:
                                spacing 0
                                xsize 900
                                text (_("RIGHT NOW") if _live else _("USUALLY")) style "jr_kicker" size 13
                                ## Mid-scene the first line is left out: "right
                                ## now" means nothing inside a scene.
                                if _live:
                                    ## Three lines: the first gives a little so
                                    ## the last clears the panel's border.
                                    text _now color gui.paper size (20 if (_line2 and _ul) else 22)
                                if not _live:
                                    text _line2 color gui.paper size 18
                                elif _line2:
                                    text _line2 style "jr_dim" size 16
                                if _ul:
                                    text _ul color gui.gold size 16
                        if jr_can_go(_pn):
                            fixed:
                                xalign 1.0
                                yalign 0.5
                                xysize (76, 70)
                                use icon_btn("go", Return(("go", _pn["place"])), tip=(_("Go there") + "\n" + jr_place_name(_pn["place"])), size=52, wid="jr_go_btn")

            ## Two chips at (450, 270).
            hbox:
                xpos 450
                ypos (270 if not _sana else 96)
                spacing 10
                if not _sana:
                    textbutton _("Their story"):
                        id "jr_psub_story"
                        style "jr_chip_button"
                        selected (_sub == "story")
                        action SetDict(js, "psub", "story")
                textbutton _chip_mem:
                    id "jr_psub_memories"
                    style "jr_chip_button"
                    selected (_sub == "memories")
                    action SetDict(js, "psub", "memories")

            ## One pane, 1040x584, at (450, 320).
            fixed:
                xpos 450
                ypos (320 if not _sana else 150)
                xysize (1040, (584 if not _sana else 754))
                if _sub == "memories":
                    use jr_scroll(1040, (584 if not _sana else 754)):
                        if not _mems:
                            text (_("Nothing yet. What I remember of her ends up here.") if _sana else _("Nothing shared yet. Scenes I live through with them end up here.")) style "jr_dim"
                        hbox:
                            box_wrap True
                            box_wrap_spacing 16
                            spacing 16
                            for _m in _mems:
                                use jr_memory_tile(_m)
                else:
                    use jr_scroll(1040, 584, spacing=10):
                        use jr_story_list(jr_story_fit(jr_story_rows(who), JR_PAGE_WORDS - _words), 1000)

            textbutton _("← Back"):
                id "jr_back"
                style "jr_chip_button"
                xalign 1.0
                xoffset -24
                ypos 20
                action SetDict(js, "sel", None)


## A person's story as a list of chapters (jr_story_rows, fitted to the
## page's word budget by jr_story_fit): what is done, the NEXT row on a gold
## rail, what is still closed, and one "later build" row. A row cut short to
## keep the page calm shows the rest as its hover label.
screen jr_story_list(rows, w=1000):

    if not rows:
        text _("Nothing written for them yet.") style "jr_dim"

    for _r in rows:

        if _r["kind"] == "heading":
            hbox:
                spacing 12
                text _r["title"] font JR_DISPLAY_FONT color gui.gold size 26
                if _r["state"] == "done":
                    vbox:
                        yalign 0.5
                        use jr_chip(_("Resolved"), fill=gui.stamina)

        elif _r["next"]:
            frame:
                xsize w
                background Frame("gui/panel.png", 4, 4)
                padding (0, 0)
                hbox:
                    add Solid(gui.gold) xsize 4 ysize 74
                    vbox:
                        xpos 18
                        yalign 0.5
                        xsize (w - 60)
                        spacing 2
                        hbox:
                            spacing 14
                            text "NEXT":
                                font JR_BOLD_FONT
                                color gui.gold
                                size 13
                                kerning 2
                                yalign 0.6
                            text jr_clip(_r["title"], 60) font JR_DISPLAY_FONT color gui.paper size 22
                        text _r["sub"] style "jr_dim" size 16

        elif _r["kind"] == "stage" and _r["tip"]:
            ## An earlier line, cut short: the whole of it on hover.
            button:
                id "jr_stage_%d" % rows.index(_r)
                style "jr_plain_button"
                action NullAction()
                tooltip (_r["tip"], "jr_stage_%d" % rows.index(_r))
                hbox:
                    spacing 12
                    text "✓" font JR_SYMBOL_FONT color gui.stamina size 17 min_width 22 ypos 3
                    text _r["show"] style "jr_dim" size 18

        elif _r["kind"] == "stage":
            hbox:
                spacing 12
                text "✓" font JR_SYMBOL_FONT color gui.stamina size 17 min_width 22 ypos 3
                text _r["show"] style "jr_text" size 18 xsize (w - 50)

        elif _r["kind"] == "later":
            hbox:
                spacing 12
                text "·" color gui.mute size 20 min_width 22
                text _r["line"] color gui.mute size 16 yalign 0.5

        else:
            if _r["tip"]:
                ## Its small line folded away: the whole of it on hover.
                button:
                    id "jr_chapter_%d" % rows.index(_r)
                    style "jr_plain_button"
                    action NullAction()
                    tooltip (_r["tip"], "jr_chapter_%d" % rows.index(_r))
                    use jr_story_chapter(_r)
            else:
                use jr_story_chapter(_r)


## One chapter of a story that isn't a learned line or the NEXT row: a
## mission, done, open or still closed.
screen jr_story_chapter(r):

    $ _ic, _ck, _sf = JR_STATUS_ICON.get(r["state"], ("—", "mute", False))
    $ _dimmed = r["state"] not in ("done", "available")
    hbox:
        spacing 12
        text _ic:
            font (JR_SYMBOL_FONT if _sf else JR_BODY_FONT)
            color getattr(gui, _ck)
            size 17
            min_width 22
            ypos 3
        vbox:
            spacing 0
            text jr_clip(r["title"], 60) font JR_DISPLAY_FONT color (gui.mute if _dimmed else gui.paper) size 20
            if r["sub"]:
                text r["sub"] style "jr_dim" size 15 color (gui.mute if _dimmed else gui.dim)


## The Me page (4.7): the journal portrait left; My story (the main story's
## scenes by act, with the ones nobody else is in) and Records.
screen jr_me_detail(js):

    $ _sub = js.get("msub2", "story")
    $ _g = player_grade()
    $ _groups = jr_me_groups()
    $ _all = [m for t, ms in _groups for m in ms]
    $ _seen = len([m for m in _all if jr_mem_state(m) == "seen"])
    $ _name, _nsize = jr_fit_name(jr_stats_title(), JR_DISPLAY_FONT, 40, 28, 600)

    frame:
        style "jr_panel_dark"
        xysize (1520, 928)
        padding (0, 0)
        fixed:

            fixed:
                xpos 0
                xysize (420, 928)
                add kaito_card_image() zoom 0.5 xalign 0.5 yalign 1.0 yoffset -10

            hbox:
                xpos 450
                ypos 24
                spacing 16
                ## substitute False: the player typed the name. A long one
                ## is drawn smaller, then clipped, so the chip and the year
                ## stay left of the Back chip.
                text _name substitute False font JR_DISPLAY_FONT color gui.paper size _nsize yalign 0.5 layout "nobreak"
                vbox:
                    yalign 0.5
                    if _g:
                        use grade_chip(_g, 15)
                    else:
                        use grade_chip(None, 15, text=_("Not yet assessed"))
                text _("1st year") style "jr_dim" size 17 yalign 0.5

            hbox:
                xpos 450
                ypos 96
                spacing 10
                for _k, _lab in JR_ME_SUBS:
                    textbutton (_lab + ("  %d/%d" % (_seen, len(_all)) if _k == "story" else "")):
                        id "jr_msub2_" + _k
                        style "jr_chip_button"
                        selected (_sub == _k)
                        action SetDict(js, "msub2", _k)
                null width 20
                textbutton _("Stats →"):
                    id "jr_me_stats"
                    style "jr_link_button"
                    yalign 0.5
                    action Function(jr_go, js, tab="stats", sel=None)

            fixed:
                xpos 450
                ypos 150
                xysize (1040, 754)
                use jr_scroll(1040, 754):
                    if _sub == "records":
                        use jr_records_pane()
                    else:
                        if not _groups:
                            text _("Nothing yet. Scenes I live through end up here, and I can go back to any of them.") style "jr_dim"
                        for _title, _ms in _groups:
                            text _title font JR_DISPLAY_FONT color gui.paper size 24
                            hbox:
                                box_wrap True
                                box_wrap_spacing 16
                                spacing 16
                                for _m in _ms:
                                    use jr_memory_tile(_m)

            textbutton _("← Back"):
                id "jr_back"
                style "jr_chip_button"
                xalign 1.0
                xoffset -24
                ypos 20
                action SetDict(js, "sel", None)


## Records (4.7): what I've read on the computer, the record book, today's
## card winnings. A section with nothing in it is not drawn.
screen jr_records_pane():
    $ _recs = jr_records()
    if not _recs:
        text _("Nothing on record yet.") style "jr_dim"
    for _head, _lines in _recs:
        vbox:
            spacing 6
            text _head style "jr_kicker"
            for _l in _lines:
                hbox:
                    spacing 12
                    add "gui/pip_small.png" ypos 8
                    text jr_clip(_l, 90) substitute False style "jr_text" size 19


## The requirement checklist of a tool or a talisman (item_requirements): one
## chip a line, ticked or crossed. Nothing when the item asks for nothing.
screen jr_req_chips(iid, w=510):
    $ _reqs = jr_reqs(iid)
    if _reqs:
        ## xmaximum, not xsize: a wrapping box that must fill its width
        ## spreads its children across it.
        hbox:
            xmaximum w
            box_wrap True
            box_wrap_spacing 6
            spacing 8
            for _line, _ok in _reqs:
                frame:
                    background Frame("gui/panel_ghost.png", 4, 4)
                    padding (9, 3)
                    hbox:
                        spacing 6
                        text ("✓" if _ok else "✗") font JR_SYMBOL_FONT color (gui.stamina if _ok else gui.seal) size 13 yalign 0.5
                        text _line substitute False color (gui.dim if _ok else gui.seal) size 13 yalign 0.5


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
    ## Leads (4.7, D31): what the story has asked me to look up, first on the
    ## tab, only while there is one. The lists under it give up its height.
    $ _leads = jr_leads()
    $ _lshow = _leads[:3]
    $ _lh = (48 + 30 * len(_lshow) + (24 if len(_leads) > 3 else 0)) if _leads else 0
    $ _h = 856 - ((_lh + 14) if _leads else 0)

    vbox:
        spacing 14

        if _leads:
            frame:
                xysize (1520, _lh)
                background Frame("gui/panel_dark.png", 4, 4)
                padding (20, 10)
                vbox:
                    spacing 4
                    text _("LEADS") style "jr_kicker" size 14
                    for _l in _lshow:
                        hbox:
                            spacing 12
                            add icon("pc_open", 26) yalign 0.5
                            text jr_clip(_l, 120) substitute False style "jr_dim" size 18 yalign 0.5
                    if len(_leads) > 3:
                        text ("and %d more" % (len(_leads) - 3)) color gui.mute size 15

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
            use jr_story(js, editable, _h)
        elif _sub == "character":
            use jr_character(js, _h)
        else:
            use jr_board_view(_h)


screen jr_story(js, editable, h=856):

    ## Explore mode plays no story, so it lists none.
    $ _groups = [] if explore_mode else jr_story_groups(js["mfilter"])
    $ _m, _need, _nxl, _pline = jr_promotion()
    $ _mlab = jr_merit_label(_m, _need, _pline)
    $ _begun = has_flag("arc2_started")
    $ _complete = main_story_complete() and not _begun

    use jr_scroll(1520, h, spacing=10):

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
        elif _begun:
            frame:
                style "jr_panel"
                xsize 1480
                text _("Arc One is finished. Arc Two has begun.") style "jr_dim"

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
                text (_("Explore mode: no story here.") if explore_mode else _("Nothing to show under this filter. The NEXT line above says what comes next.") if js["mfilter"] != "all" else _("The story's missions appear here as they open.")) style "jr_dim"

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


screen jr_character(js, h=856):

    $ _groups = jr_character_groups(js["mfilter"])

    use jr_scroll(1520, h, spacing=10):

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


screen jr_board_view(h=856):

    $ _b = jr_board()

    use jr_scroll(1520, h):

        hbox:
            spacing 16
            add icon("board", 44) yalign 0.5
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
                                use grade_chip(jr_get(_o, "grade"), 13)
                                if jr_get(_o, "senior_only"):
                                    use jr_chip(_("Needs a senior partner"), gui.seal)
                            text jr_clip(jr_get(_o, "title", ""), 60) font JR_DISPLAY_FONT color gui.paper size 22 xsize 414
                            text jr_clip(jr_offer_line(_o), 80) style "jr_dim" size 16 xsize 414
                            if jr_get(_o, "curse"):
                                text jr_clip("Reported: %s" % jr_get(_o, "curse"), 90) style "jr_dim" size 15 xsize 414 italic True
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
                            vbox:
                                yalign 0.5
                                use grade_chip(jr_get(_t, "grade"), 13, dim=True)
                            text jr_clip(jr_get(_t, "title", ""), 40) color gui.mute size 18 yalign 0.5
                            ## A job I took reads "me and Nobara" (board_card_line's words).
                            $ _tb = jr_get(_t, "taken_by")
                            $ _tb = ((("me and " + jr_short(jr_get(_t, "partner"))) if jr_get(_t, "partner") else "me") if _tb == "mc" else (jr_short(_tb) if _tb else "someone"))
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


## Memory tiles #################################################################

## One memory, 280x158 (a person's page and the Me page; the Memories tab is
## gone, 4.7). A seen one replays; an unseen one is a dark tile with the
## entry's own `text` (WP5's memory_entry), which never names someone not met.
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
                    text jr_clip(jr_get(m, "text", None) or jr_get(m, "hint", "") or "", 70):
                        style "jr_dim"
                        size 15
                        xpos 14
                        ypos 82
                        xsize 252
                        text_align 0.5


## Stats ########################################################################

## Lighter (4.7): the portrait left; right, the name, then three chips and one
## pane at a time: Overview (the grade line, the promotion bar, six bars),
## Last Light, My year.
screen jr_stats_tab(js=None):

    $ _sub = (js or {}).get("ssub", "overview")
    $ _gradeline = ("First-year · %s" % grade_label(player_grade())) if player_grade() else _("First-year · Not yet assessed")

    ## Left: the full picture, unlit.
    fixed:
        xpos 0
        xysize (500, 928)
        add kaito_card_image() zoom 0.62 xalign 0.5 yalign 1.0

    ## Right.
    fixed:
        xpos 540
        xysize (980, 928)

        vbox:
            spacing 18

            ## substitute False: the player typed the name (see the year strip).
            text jr_stats_title() substitute False font JR_DISPLAY_FONT color gui.paper size 40

            hbox:
                spacing 10
                for _k, _lab in JR_STATS_SUBS:
                    textbutton _lab:
                        id "jr_ssub_" + _k
                        style "jr_chip_button"
                        selected (_sub == _k)
                        action (SetDict(js, "ssub", _k) if js is not None else NullAction())

            if _sub == "light":
                use jr_stats_light()
            elif _sub == "year":
                use jr_stats_year()
            else:
                use jr_stats_overview(_gradeline)


screen jr_stats_overview(gradeline):

    $ _m, _need, _nxl, _pline = jr_promotion()
    $ _mlab = jr_merit_label(_m, _need, _pline)

    vbox:
        spacing 22

        text gradeline style "jr_kicker" size 18

        frame:
            style "jr_panel"
            xsize 940
            padding (24, 16)
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
            spacing 14
            for _lab, _v, _mx, _cap, _fill, _vt in jr_bars():
                hbox:
                    spacing 16
                    text _lab style "jr_dim" min_width 150 yalign 0.5
                    use jr_meter(_v, _mx, width=620, fill=_fill, marker=_cap)
                    text _vt style "jr_dim" size 16 yalign 0.5


screen jr_stats_light():

    $ _t = jr_tech()

    frame:
        style "jr_panel"
        xsize 940
        padding (24, 18)
        vbox:
            spacing 10
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
            null height 4
            for _mv in _t["moves"]:
                hbox:
                    spacing 12
                    text _mv["name"] color (gui.paper if _mv["ok"] else gui.mute) size 18 min_width 150
                    text "[_mv['ce']] CE" color (gui.violet if _mv["ok"] else gui.mute) size 16 min_width 64 yalign 0.5
                    text (_mv["desc"] if _mv["ok"] else _mv["needs"]) color (gui.dim if _mv["ok"] else gui.mute) size 16 xsize 640 yalign 0.5


screen jr_stats_year():

    $ _year = jr_year()

    frame:
        style "jr_panel"
        xsize 940
        padding (24, 18)
        vbox:
            spacing 10
            text _("MY YEAR · CURSED ENERGY RESERVE, 0–300") style "jr_kicker"
            for _nm, _col, _res, _off in _year:
                hbox:
                    spacing 16
                    ## substitute False: the player typed this name, and a
                    ## "[" in it must not be read as an interpolation.
                    text jr_clip(_nm, 14) substitute False color _col size 18 min_width 160 yalign 0.5
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
                                vbox:
                                    yalign 0.5
                                    use grade_chip(_ti["grade"], 13)
                        if _ti["desc"]:
                            text _ti["desc"] style "jr_dim" xsize 1160
                        if _ti["effect"]:
                            text "[_ti['effect']] · [JR_FX_NOTE]" color gui.violet2 size 17 xsize 1160
                        use jr_req_chips(_tool, 1160)
                    else:
                        text _("In my hand: Bare hands") font JR_DISPLAY_FONT color gui.paper size 28
                        text _("No cursed tool yet. The armory releases them by grade.") style "jr_dim"
                if editable:
                    textbutton _("Change"):
                        style "jr_chip_button"
                        yalign 0.5
                        action SetDict(js, "pick", ("tool", 0))

        $ _sl = _("1 slot") if _slots == 1 else (_("%d slots") % _slots)
        text _("TALISMANS · [_sl] at my grade") style "jr_kicker"

        hbox:
            spacing 24
            for _i in range(4):
                if _i < _slots:
                    $ _id = _worn[_i] if _i < len(_worn) else None
                    $ _it = jr_item(_id) if _id else None
                    ## Talismans fill from slot 1 (WP6 appends), so only the
                    ## first empty slot takes a new one.
                    button:
                        id "jr_slot_%d" % _i
                        style "jr_card_button"
                        xysize (352, 300)
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
                                    use grade_chip(_it["grade"], 13)
                                if _it["effect"]:
                                    text _it["effect"] color gui.violet2 size 16 xsize 312
                                text JR_FX_NOTE style "jr_dim" size 14 xsize 312
                                use jr_req_chips(_id, 312)
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
                        xysize (352, 300)
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
                add icon("equipment", 44) yalign 0.5
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
                        action ([Function(jr_hold, None)] if _kind == "tool" else [Function(jr_takeoff, _cur)]) + [SetDict(js, "pick", None)]
                textbutton _("Close"):
                    style "jr_chip_button"
                    action SetDict(js, "pick", None)


## The picker's rows: one button per option (a sensitive one wears it).
screen jr_picker_rows(js, _kind, _slot, _opts):
    for _id, _ok, _why in _opts:
        $ _it = jr_item(_id)
        button:
            id "jr_pick_" + str(_id)
            style "jr_row_button"
            xsize 900
            sensitive _ok
            action ([Function(jr_hold, _id)] if _kind == "tool" else [Function(jr_wear, _slot, _id)]) + [SetDict(js, "pick", None)]
            vbox:
                spacing 2
                hbox:
                    spacing 12
                    text _it["name"] font JR_DISPLAY_FONT color (gui.paper if _ok else gui.mute) size 22
                    if _it["grade"]:
                        vbox:
                            yalign 0.5
                            use grade_chip(_it["grade"], 13, dim=(not _ok))
                    if _why:
                        text _why color (gui.dim if _ok else gui.seal) size 16 yalign 0.5
                if _it["effect"]:
                    text "[_it['effect']] · [JR_FX_NOTE]" color (gui.violet2 if _ok else gui.mute) size 15 xsize 850
                ## The checklist (4.7): what the tool or talisman asks of me.
                use jr_req_chips(_id, 850)


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
                                    ## At most two lines, so the count and kind stay inside the tile.
                                    $ _inm = jr_clip(_it["name"], 34)
                                    text _inm font JR_DISPLAY_FONT color gui.paper size (21 if len(_inm) <= 20 else 19) xsize 244
                                    hbox:
                                        spacing 10
                                        if _c > 1:
                                            text "× [_c]" color gui.paper size 18 yalign 0.5
                                        if _it["grade"]:
                                            vbox:
                                                yalign 0.5
                                                use grade_chip(_it["grade"], 13)
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
                                vbox:
                                    yalign 0.5
                                    use grade_chip(_it["grade"], 13)
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
                        ## The checklist (4.7), for a tool or a talisman.
                        if _it["kind"] in ("tool", "talisman"):
                            use jr_req_chips(_sel, 510)
                else:
                    text _("Choose something to look at it.") style "jr_dim" xalign 0.5 yalign 0.5


## Wrappers (kept: the old Status and Journal entry points) ######################

screen jjk_status():
    tag menu
    use journal("stats")

screen jjk_journal():
    tag menu
    use journal("people")
