## tools/smoke/p2_journal.rpy -- P3's harness: the journal's five tabs, the
## person page and the Me page (docs/PHASE2_DESIGN.md 4.7, section 7 "P3").
##
##   tools/smoke.sh tools/smoke/p2_journal.rpy        (shots/p2_journal/)
##
## Every acceptance bullet of P3 is a named check, in the plan's order:
##   1. tabs       five rows; journal("memories") opens People; an older
##                 journal's view state is brought up to date; the wrappers.
##   2. pages      every met person's page has its three sections; its tiles
##                 are memories_with(who); a shared scene is on every
##                 participant's page; the scenes nobody else is in are on the
##                 Me page only; every catalogued memory can be reached.
##   3. replay     a seen tile replays and the journal is still up; an unseen
##                 tile is not a button and names nobody unmet.
##   4. story      jr_story_rows("nobara"): heading, one NEXT row with a place,
##                 at most one "later build" row; the roll-call gate's words.
##   5. right now  the page prints person_now(who); the go button only in the
##                 campus journal and only when reachable, returning
##                 ("go", loc); every other button leaves the journal up; the
##                 journal in a menu context returns only True.
##   6. wording    no thread stage line says "you" or "your".
##   7. grid       18 cards in four rows without scrolling; 26 cards scroll,
##                 and the last can be pressed; six words a card; Gojo's chip.
##   8. records    no section with the three stubs; two titles when patched;
##                 the source reads no other package's table or variable.
##   9. checklist  item_requirements chips in the talisman picker, the tool
##                 picker, the Equipment panels and the Inventory panel.
##  10. leads      first on the Missions tab when there is one; absent otherwise.
##  11. stats      one pane at a time under three chips.
##  12. worst      zz_worst screenshots of every full view; no toast over the
##                 journal (a NOTE until P2's toast_room() is in, 7.3).
##
## Memories are built with their owner's constructors (_mem / memory_entry,
## R5); items with give_item; grades with promote. Other packages' contract
## functions (person_now, item_requirements, pc_leads, pc_records,
## fish_records, cards_records) are patched under their store names for the
## span of one check and put back.

init 999 python:
    import builtins
    import os
    import re

    class ZZJ2State(builtins.object):
        """Harness state outside the store: not saved, not rolled back."""
        def __init__(self):
            self.script = builtins.list()
            self.menu_driver = False
            self.replays = 0
            self.replay_flags = None
            self.menu = builtins.dict()
            self.patched = builtins.dict()

    zz_st = ZZJ2State()

    ## One harness memory, shared by two people, built with WP5's constructor.
    _mem("zz_mem_scene", "A Harness Scene", "Bonds", "zz_mem_scene", who=("yuji", "megumi"),
         bg="bg courtyard", hint="A scene the harness plays.", seen=[("flag", "zz_mem_seen")])
    MEMORY_BY_ID["zz_mem_scene"] = MEMORIES[-1]

    def zz_patch(name, fn):
        """Rebind a store function for a check; zz_unpatch puts it back."""
        if name not in zz_st.patched:
            zz_st.patched[name] = getattr(store, name)
        setattr(store, name, fn)

    def zz_unpatch(*names):
        for n in (names or builtins.list(zz_st.patched)):
            if n in zz_st.patched:
                setattr(store, n, zz_st.patched.pop(n))

    def zz_js():
        s = renpy.get_screen("journal")
        return s.scope.get("js") if s is not None else None

    def zz_open(tab="people", **kw):
        """Show the journal on a tab, set view-state keys, and render."""
        renpy.hide_screen("journal")
        renpy.show_screen("journal", tab)
        zz_render()
        js = zz_js()
        js.update(kw)
        zz_render(0.2)
        return js

    def zz_btns(screen="journal"):
        s = renpy.get_screen(screen)
        out = builtins.list()
        if s is None:
            return out
        def cb(d):
            if isinstance(d, renpy.display.behavior.Button):
                out.append(d)
        s.visit_all(cb)
        return out

    def zz_flat(a):
        if isinstance(a, (builtins.list, builtins.tuple)):
            r = builtins.list()
            for x in a:
                r.extend(zz_flat(x))
            return r
        return [a]

    def zz_actions(screen="journal"):
        out = builtins.list()
        for b in zz_btns(screen):
            out.extend(zz_flat(b.action))
        return out

    def zz_return_values(screen="journal"):
        return [a.value for a in zz_actions(screen) if type(a).__name__ == "Return"]

    def zz_widget(wid, screen="journal"):
        if renpy.get_screen(screen) is None:
            return None
        ## base=True: for a textbutton the plain lookup gives its Text.
        return renpy.get_displayable(screen, wid, base=True)

    def zz_has(text, screen="journal"):
        return text in zz_texts(screen)

    def zz_any(part, screen="journal"):
        return any(part in t for t in zz_texts(screen))

    def zz_node(text, screen="journal"):
        for d in zz_text_nodes(screen):
            if zz_text_string(d) == text:
                return d
        return None

    def zz_replay_ids(screen="journal"):
        """The memory ids of the tiles that replay, in tree order."""
        return [a.mem_id for a in zz_actions(screen) if isinstance(a, MemoryReplay)]

    ## What a button's action may be if the journal is to stay up (R4): it
    ## changes the view state, calls a none_ok function, replays a memory or
    ## does nothing. Only a Return ends the journal.
    ZZ_STAY_TYPES = ("SetDict", "NullAction", "MemoryReplay", "Function")
    ZZ_NONE_OK = ("jr_go", "jr_toggle", "jr_wear", "jr_hold", "jr_takeoff", "ui_do")

    def zz_leaving(screen="journal"):
        """Every action in the screen that is not known to leave it up, and
        every Return's value."""
        odd, rets = builtins.list(), builtins.list()
        for a in zz_actions(screen):
            n = type(a).__name__
            if n == "Return":
                rets.append(a.value)
            elif n == "Function":
                if getattr(a.callable, "__name__", "") not in ZZ_NONE_OK:
                    odd.append(repr(a.callable))
            elif n not in ZZ_STAY_TYPES and a is not None:
                odd.append(n)
        return odd, rets

    def zz_now(place, name, doing="", reachable=True, hidden=False, with_me=False):
        def f(who):
            return builtins.dict(place=place, name=name, doing=doing, reachable=reachable,
                                 hidden=hidden, with_me=with_me)
        return f

    def zz_tick():
        if not zz_st.script:
            return None
        fn = zz_st.script.pop(0)
        try:
            return fn()
        except Exception:
            import traceback
            check(False, "driver step raised", traceback.format_exc())
            zz_st.script[:] = []
            return "zz_error"

    def zz_nil(*values):
        return None

    def zz_done():
        return "zz_done"

    def zz_set(**kw):
        zz_js().update(kw)
        renpy.restart_interaction()
        return None

    def zz_press(pred, name):
        """Run the first journal button whose action list satisfies pred."""
        for b in zz_btns():
            if any(pred(a) for a in zz_flat(b.action)):
                return renpy.run(b.action)
        check(False, "journal has a button: " + name)
        return None

    def zz_replay_press(mem_id):
        autoplay(True)
        try:
            zz_press(lambda a: isinstance(a, MemoryReplay) and a.mem_id == mem_id, "the tile of " + mem_id)
        finally:
            autoplay(False)
        return None

    def zz_start_interact():
        if zz_st.menu_driver and renpy.context()._menu and not renpy.get_screen("zz_driver"):
            renpy.show_screen("zz_driver")

    config.start_interact_callbacks.append(zz_start_interact)

    def zz_source():
        root = os.environ.get("SMOKE_ROOT")
        if not root:
            return None
        with open(os.path.join(root, "game", "ui_journal.rpy"), encoding="utf-8") as f:
            return f.read()

    def zz_body(r):
        """A rectangle lies wholly inside the journal's body (1520x928 at
        x 360, y 112)."""
        return bool(r) and r[0] >= 360 and r[1] >= 112 and r[0] + r[2] <= 1880 and r[1] + r[3] <= 1040

    def zz_meet_everyone():
        for w in ("maki", "panda", "toge", "utahime"):
            if w not in store.roster:
                store.roster.append(w)
        for e in JOURNAL_CAST:
            rule = e.get("met")
            if rule and rule[0] == "flag":
                flag(rule[1])


screen zz_driver():
    zorder 500
    timer 0.3 repeat True action Function(zz_tick)


## The harness memory's scene. It changes state, which a replay must not keep.
label zz_mem_scene:
    $ zz_st.replays += 1
    $ zz_st.replay_flags = bool(_in_replay)
    $ day = 999
    $ flag("zz_replay_changed_this")
    "(A replayed memory.)"
    return


label zz_smoke:

    $ fixture(mc_name="Tester", mc_surname="Harness")
    $ settle(day=6, period="Noon", here="courtyard")
    python:
        for _zz_f in ("roll_call", "storehouse_access", "zz_mem_seen", "kurose_met", "oda_letter_read", "kurose_leak"):
            flag(_zz_f)
        done_events.add("st_roll_call")
        done_events.add("ev_yuji_1")
        done_events.add("ev_nobara_1")
        bonds.update(dict(yuji=38, megumi=22, nobara=24, gojo=12, shoko=8, yaga=5, ijichi=14))
        threads.update(dict(yuji_countdown=1, nobara_saori=0))
        promote("mc", "g4", quiet=True)
        gui.icon_words = "never"

    ## =====================================================================
    ## 1. Five tabs; "memories" opens People; the wrappers
    ## =====================================================================
    python:
        check(len(JOURNAL_TABS) == 5 and [t[0] for t in JOURNAL_TABS] == ["people", "missions", "stats", "equipment", "inventory"],
              "JOURNAL_TABS has five rows, and no Memories row", [t[0] for t in JOURNAL_TABS])
        check(journal_state("memories")["tab"] == "people", "journal_state maps \"memories\" to \"people\"")
        _zz_js = zz_open("memories")
        check(_zz_js["tab"] == "people", "journal(\"memories\") opens with js[\"tab\"] == \"people\"", _zz_js["tab"])
        check(all(zz_widget("jr_tab_" + k) is not None for k, kan, lab in JOURNAL_TABS)
              and zz_widget("jr_tab_memories") is None, "the rail has five tab buttons and no Memories button")
        _zz_r = [zz_rect("journal", "jr_tab_" + k) for k, kan, lab in JOURNAL_TABS]
        check(all(_zz_r) and _zz_r[0][1] == 148 and [r[1] - _zz_r[0][1] for r in _zz_r] == [0, 86, 172, 258, 344],
              "the tab buttons start at y 148 and step 86 px", _zz_r)
        shot("people_grid")
        ## A view state made by the six-tab journal (a save taken inside it).
        _zz_old = dict(tab="memories", sel=None, mfilter="available", msub="story", mem_mode="person",
                       mem_who="nobara", inv_cat="all", inv_sel=None, pick=None, collapsed={})
        check(jr_fix(_zz_old) == "people" and _zz_old["psub"] == "story" and _zz_old["ssub"] == "overview"
              and _zz_old["msub2"] == "story" and _zz_old["mem_who"] == "nobara",
              "an older journal's view state lands on People with the new keys", _zz_old)
        _zz_new = journal_state("stats")
        check(_zz_new["psub"] == "story" and _zz_new["ssub"] == "overview" and _zz_new["msub2"] == "story"
              and "mem_mode" in _zz_new and "mem_who" in _zz_new, "journal_state has psub, ssub, msub2 and keeps mem_mode, mem_who")
        renpy.hide_screen("journal")
        for _zz_w in ("jjk_status", "jjk_journal"):
            renpy.show_screen(_zz_w)
            zz_render(0.2)
            check(renpy.get_screen(_zz_w) is not None and zz_any("Journal", _zz_w), _zz_w + " renders")
            renpy.hide_screen(_zz_w)
        ## Every icon name this file draws is in the table (wave 0's hand-off).
        _zz_src = zz_source()
        if _zz_src is None:
            note("icon names", "SMOKE_ROOT is not set; the source checks are skipped")
        else:
            _zz_names = set(re.findall(r'icon(?:_btn)?\(\s*"([a-z_]+)"', _zz_src))
            check(_zz_names and all(n in ICONS for n in _zz_names), "every literal icon name in ui_journal.rpy is in ICONS",
                  sorted(n for n in _zz_names if n not in ICONS))
        check(all(icon_for("tab", k) in ICONS and icon_for("tab", k) != "act" for k, kan, lab in JOURNAL_TABS),
              "every tab has its own icon")
        ## The stand-in path: with no picture on disk the rail still draws.
        zz_patch("icon_has_art", lambda name: False)
        gui.icon_words = "auto"
        zz_open("people")
        shot("rail_standin_icons")
        check(len([d for d in zz_text_nodes("journal") if zz_is_glyph(d)]) >= 6
              and not any(zz_text_string(d) == u"？" for d in zz_text_nodes("journal") if zz_is_glyph(d)),
              "with no icon pictures the rail draws its kanji stand-ins, none a question mark")
        zz_unpatch("icon_has_art")
        gui.icon_words = "never"
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 2. Every met person's page: three sections; the tiles; who is where
    ## =====================================================================
    python:
        zz_meet_everyone()
        _zz_cast = [e for e in journal_cast() if e["met"]]
        check(len(_zz_cast) == 17, "all 17 of JOURNAL_CAST are met through their own rules", [e["who"] for e in journal_cast() if not e["met"]])
        _zz_bad = builtins.list()
        _zz_onpages = set()
        _zz_unseen_texts = builtins.list()
        for _zz_e in _zz_cast:
            _zz_who = _zz_e["who"]
            _zz_want = memories_with(_zz_who)
            _zz_onpages.update(m["id"] for m in _zz_want)
            if [m["id"] for m in jr_page_memories(_zz_who)] != [m["id"] for m in _zz_want]:
                _zz_bad.append((_zz_who, "page list differs"))
            zz_open("people", sel=_zz_who, psub="story")
            _zz_tx = zz_texts("journal")
            if _zz_who == "sana":
                if not (zz_has("IN MEMORY") and not zz_has("RIGHT NOW") and zz_widget("jr_psub_memories") is not None
                        and zz_widget("jr_psub_story") is None):
                    _zz_bad.append((_zz_who, "Sana's page: In memory, no Right now, Memories open"))
            else:
                if not (zz_has("RIGHT NOW") and zz_widget("jr_psub_story") is not None and zz_widget("jr_psub_memories") is not None):
                    _zz_bad.append((_zz_who, "sections missing"))
                if zz_replay_ids():
                    _zz_bad.append((_zz_who, "tiles on the story pane"))
            zz_js().update(psub="memories")
            zz_render(0.2)
            _zz_seen = [m["id"] for m in _zz_want if m["state"] == "seen"]
            if zz_replay_ids() != _zz_seen:
                _zz_bad.append((_zz_who, "seen tiles %r, want %r" % (zz_replay_ids(), _zz_seen)))
            _zz_tx = zz_texts("journal")
            ## (Someone with no sprite has one 「？」 in its place.)
            _zz_dark = len([t for t in _zz_tx if t == u"「？」"]) - (0 if renpy.loadable("images/char/%s_neutral.png" % _zz_who) else 1)
            _zz_later = len([t for t in _zz_tx if t == MEMORY_LATER])
            if _zz_dark != len([m for m in _zz_want if m["state"] == "unseen"]) or _zz_later != len([m for m in _zz_want if m["state"] == "later"]):
                _zz_bad.append((_zz_who, "unseen %d, later %d" % (_zz_dark, _zz_later)))
            for _zz_m in _zz_want:
                if _zz_m["state"] == "unseen":
                    if jr_clip(_zz_m["text"], 70) not in _zz_tx:
                        _zz_bad.append((_zz_who, "unseen tile text missing: " + _zz_m["id"]))
                    _zz_unseen_texts.append((_zz_who, _zz_m["id"], _zz_m["text"]))
            if not zz_has("Memories %d/%d" % (len(_zz_seen), len(_zz_want))):
                _zz_bad.append((_zz_who, "chip count"))
        check(not _zz_bad, "every met person's page shows its three sections, and its tiles equal memories_with(who)", _zz_bad)
        shot("page_last_memories")
        check(all("ch2_first_years" in [m["id"] for m in jr_page_memories(w)] for w in ("yuji", "megumi", "nobara")),
              "ch2_first_years is on Yuji's, Megumi's and Nobara's pages")
        check(all("zz_mem_scene" in [m["id"] for m in jr_page_memories(w)] for w in ("yuji", "megumi"))
              and "zz_mem_scene" not in [m["id"] for m in jr_page_memories("nobara")],
              "a scene two people share is on both their pages and nobody else's")

        ## The Me page.
        _zz_alone = [m["id"] for m in MEMORIES if not m["who"]]
        check(len(_zz_alone) == 3, "three catalogued scenes have nobody else in them", _zz_alone)
        zz_open("people", sel="me", msub2="story")
        shot("me_story")
        _zz_me_ids = [jr_get(m, "id") for t, ms in jr_me_groups() for m in ms]
        check(all(i in _zz_me_ids for i in _zz_alone) and all(i in zz_replay_ids() for i in _zz_alone),
              "the three who=() memories are on the Me page, as tiles that replay", (_zz_alone, zz_replay_ids()))
        check(not any(i in _zz_onpages for i in _zz_alone), "the three who=() memories are on no person's page")
        check(not any(jr_get(m, "act") == "Bonds" for t, ms in jr_me_groups() for m in ms)
              and zz_widget("jr_msub2_story") is not None and zz_widget("jr_msub2_records") is not None
              and zz_widget("jr_me_stats") is not None,
              "the Me page: My story without Bonds, the Records chip, the Stats link")
        _zz_all = set(m["id"] for m in MEMORIES)
        check(_zz_all <= (_zz_onpages | set(_zz_me_ids)), "every memory in the catalogue is reachable from a page or the Me page",
              sorted(_zz_all - _zz_onpages - set(_zz_me_ids)))
        renpy.run(zz_widget("jr_me_stats").action)
        zz_render(0.2)
        check(zz_js()["tab"] == "stats" and zz_js()["sel"] is None, "Stats → on the Me page opens the Stats tab")
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 3. An unseen tile; then a replay from a page, and the journal stays
    ## =====================================================================
    python:
        ## Panda is met, Toge is not: their shared scene must not name him.
        roster.remove("toge")
        _zz_e = memory_entry("ev_panda_1")
        check(_zz_e["state"] == "unseen" and _zz_e["text"] == MEMORY_UNMET_HINT and MEMORY_UNMET_HINT == "Someone I haven't met yet.",
              "the unmet hint is in the first person", (_zz_e["text"], MEMORY_UNMET_HINT))
        zz_open("people", sel="panda", psub="memories")
        shot("page_panda_unseen")
        _zz_tx = zz_texts("journal")
        _zz_unmet = [e for e in journal_cast() if not e["met"]]
        _zz_names = [n for e in _zz_unmet for n in (e["name"], jr_short(e["who"]))]
        _zz_tile_tx = [jr_clip(m["text"], 70) for m in jr_page_memories("panda") if m["state"] == "unseen"]
        check(MEMORY_UNMET_HINT in _zz_tx and "ev_panda_1" not in zz_replay_ids()
              and not any(n in t for n in _zz_names for t in _zz_tile_tx),
              "an unseen tile is not clickable and names nobody unmet", (_zz_names, _zz_tile_tx))
        check(not any(isinstance(a, MemoryReplay) and memory_state(a.mem_id) != "seen" for a in zz_actions()),
              "no tile that replays is for an unseen memory")
        roster.append("toge")
        ## Across every page (everyone met again): the unseen tiles' words.
        _zz_unmet_names = [n for e in journal_cast() if not e["met"] for n in (e["name"], jr_short(e["who"]))]
        check(not any(n in t for n in _zz_unmet_names for w, i, t in _zz_unseen_texts), "no unseen tile on any page names someone unmet")
        renpy.hide_screen("journal")
        zz_st.replays = 0
        _zz_day, _zz_flags, _zz_bonds = day, set(flags), dict(bonds)
        zz_st.script[:] = [
            lambda: zz_set(sel="yuji", psub="memories"),
            lambda: zz_nil(shot("page_yuji_memories", wait=0)),
            lambda: zz_nil(check("zz_mem_scene" in zz_replay_ids(), "a seen tile is a button that replays", zz_replay_ids())),
            lambda: zz_replay_press("zz_mem_scene"),
            lambda: zz_nil(check(renpy.get_screen("journal") is not None and zz_js()["sel"] == "yuji" and zz_js()["psub"] == "memories",
                                 "after the replay the journal is still up, on Yuji's memories")),
            lambda: zz_nil(shot("page_after_replay", wait=0)),
            zz_done,
        ]
    show screen zz_driver
    call screen journal("people")
    hide screen zz_driver
    python:
        check(_return == "zz_done", "the journal's own interaction carried on after the replay", _return)
        check(zz_st.replays == 1 and zz_st.replay_flags is True, "the memory played once, as a replay", (zz_st.replays, zz_st.replay_flags))
        check(day == _zz_day and flags == _zz_flags and bonds == _zz_bonds, "the replay left the save's state alone")

    ## =====================================================================
    ## 4. Their story
    ## =====================================================================
    python:
        _zz_rows = jr_story_rows("nobara")
        note("jr_story_rows(nobara)", [(r["kind"], r["state"], r["title"] or r["line"][:30], r["where"]) for r in _zz_rows])
        check(_zz_rows and _zz_rows[0]["kind"] == "heading" and _zz_rows[0]["title"] == "Somebody Remembered",
              "jr_story_rows(\"nobara\") starts with \"Somebody Remembered\"")
        _zz_next = [r for r in _zz_rows if r["next"]]
        check(len(_zz_next) == 1 and _zz_next[0]["where"], "exactly one row has next=True, and it says where", _zz_next)
        check(len([r for r in _zz_rows if r["kind"] == "later"]) <= 1, "at most one collapsed \"later build\" row")
        check(all(set(r) >= {"kind", "title", "line", "state", "where", "next"} for r in _zz_rows), "every row has the six frozen keys")
        check([r["line"] for r in _zz_rows if r["kind"] == "stage"] == THREADS["nobara_saori"]["stages"][:1],
              "the learned stage lines are done rows, and nothing not yet learned is listed")
        _zz_i = _zz_rows.index(_zz_next[0])
        check(all(r["state"] == "done" for r in _zz_rows[1:_zz_i]) and not any(r["state"] == "done" for r in _zz_rows[_zz_i:]),
              "the NEXT row is the first row not done")
        ## The step and where: her second scene asks for Bond 35.
        check(_zz_next[0]["kind"] == "step" and _zz_next[0]["title"] == "Spend time together" and _zz_next[0]["line"] == "Bond 35",
              "below Bond 35 the next step reads Spend time together — Bond 35", _zz_next)
        ## A mission she can give comes first; one her thread unlocks sits after its stage.
        bonds["nobara"] = 61
        flag("ijichi_rides")
        threads["nobara_saori"] = 1
        _zz_rows = jr_story_rows("nobara")
        _zz_next = [r for r in _zz_rows if r["next"]]
        _zz_m = MISSION_BY_ID["cm_nobara_1"]
        note("cm_nobara_1", mission_status("cm_nobara_1"))
        if mission_status("cm_nobara_1") in ("available", "active"):
            check(len(_zz_next) == 1 and _zz_next[0]["kind"] == "mission" and _zz_next[0]["title"] == _zz_m["title"] and _zz_next[0]["where"],
                  "a mission she can give now is the NEXT row", _zz_next)
        else:
            check(len(_zz_next) == 1 and _zz_next[0]["where"], "one NEXT row with a place (her first mission is %s)" % mission_status("cm_nobara_1"), _zz_next)
        zz_open("people", sel="nobara", psub="story")
        shot("page_nobara_story")
        check(zz_has("Somebody Remembered") and zz_has("NEXT") and len([t for t in zz_texts("journal") if t == "NEXT"]) == 1,
              "her page draws the heading and one NEXT row")
        check(len([t for t in zz_texts("journal") if "in a later build" in t]) <= 1, "her page draws at most one later-build row")
        renpy.hide_screen("journal")
        bonds["nobara"] = 24
        threads["nobara_saori"] = 0
        ## Someone with no thread and nothing written still gets a page.
        check(isinstance(jr_story_rows("nanami"), builtins.list) and len([r for r in jr_story_rows("nanami") if r["kind"] == "later"]) <= 1
              and jr_story_rows("sana") == [], "a JOURNAL_CAST-only person's story is a list; Sana's is empty", jr_story_rows("nanami"))
        ## Wave 0's hand-off: the roll-call gate.
        _zz_keep = (set(flags), set(done_events))
        flags.discard("roll_call")
        done_events.discard("st_roll_call")
        done_events.discard("ev_yuji_1")
        check(not rule_hangout_gate(dict(kind="hangout")), "(fixture) before roll call the gate holds the character scenes")
        check(jr_next("megumi") == "Next: Spend time together — after roll call", "before roll call a card's Next says after roll call", jr_next("megumi"))
        _zz_h = [r for r in jr_story_rows("megumi") if r["next"]]
        check(len(_zz_h) == 1 and _zz_h[0]["line"] == "After roll call", "and so does the story's NEXT row", _zz_h)
        flags.clear(); flags.update(_zz_keep[0])
        done_events.clear(); done_events.update(_zz_keep[1])
        check(jr_next("megumi").startswith("Next: Spend time together — ") and "roll call" not in jr_next("megumi"),
              "after roll call the Next line is the scene and where", jr_next("megumi"))

    ## =====================================================================
    ## 5. Right now, and the go button
    ## =====================================================================
    python:
        ## The stub (or P1's real function): the page prints what it says.
        _zz_pn = person_now("yuji")
        zz_open("people", sel="yuji", psub="story")
        check(zz_has(jr_clip(jr_now_line(jr_now("yuji")), 84)), "Right now prints person_now(who) as it is today", (_zz_pn, [t for t in zz_texts("journal")][:12]))
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        zz_open("people", sel="yuji", psub="story")
        shot("page_yuji_story")
        check(zz_has("Cafeteria — halfway through an enormous bowl"), "Right now equals person_now(who)'s name and doing")
        check(any(t.startswith("Usually: ") for t in zz_texts("journal")), "the second line is Usually: ...")
        check(zz_has(unlock_line("yuji")) if unlock_line("yuji") else True, "the third line is the Closer hint", unlock_line("yuji"))
        _zz_go = zz_widget("jr_go_btn")
        check(_zz_go is not None and journal_editable() and ("go", "cafeteria") in zz_return_values(),
              "the go button is there in the campus journal when reachable, returning (\"go\", loc)", zz_return_values())
        for _zz_case, _zz_fn in (("not reachable", zz_now("gojo_office", "Somewhere I can't go right now", reachable=False, hidden=True)),
                                 ("off campus", zz_now(None, "Off campus", reachable=False)),
                                 ("with me", zz_now("courtyard", "With me", reachable=True, with_me=True))):
            zz_patch("person_now", _zz_fn)
            zz_open("people", sel="yuji", psub="story")
            check(zz_widget("jr_go_btn") is None and not [v for v in zz_return_values() if v is not None]
                  and zz_has(_zz_fn("yuji")["name"]),
                  "no go button when " + _zz_case + ", and the line is person_now's", zz_return_values())
        ## The grid's one line.
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        check(jr_card_place("yuji") == "Cafeteria", "a card's place line is person_now's name")
        zz_patch("person_now", zz_now("gojo_office", "Somewhere I can't go right now", reachable=False, hidden=True))
        check(jr_card_place("gojo") == "Elsewhere", "a card says Elsewhere for a room I can't enter")
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        renpy.hide_screen("journal")

    ## Every other button leaves the journal up: walk every view.
    python:
        store.inventory = {}
        for _zz_id in ("paper_ward", "steady_hand", "slaughter_demon", "nunchaku", "first_aid"):
            give_item(_zz_id, 1, quiet=True)
        fixture(equipped_tool="slaughter_demon", equipped_talismans=["paper_ward"])
        _zz_views = [("people grid", "people", {}), ("a person's story", "people", dict(sel="megumi", psub="story")),
                     ("a person's memories", "people", dict(sel="megumi", psub="memories")),
                     ("Sana", "people", dict(sel="sana")),
                     ("Me: story", "people", dict(sel="me", msub2="story")), ("Me: records", "people", dict(sel="me", msub2="records")),
                     ("missions: story", "missions", dict(msub="story", mfilter="all")),
                     ("missions: character", "missions", dict(msub="character", mfilter="all")),
                     ("missions: board", "missions", dict(msub="board")),
                     ("stats: overview", "stats", dict(ssub="overview")), ("stats: light", "stats", dict(ssub="light")),
                     ("stats: year", "stats", dict(ssub="year")),
                     ("equipment", "equipment", {}), ("picker: talisman", "equipment", dict(pick=("talisman", 0))),
                     ("picker: tool", "equipment", dict(pick=("tool", 0))),
                     ("inventory", "inventory", dict(inv_sel="paper_ward"))]
        _zz_bad = builtins.list()
        for _zz_name, _zz_tab, _zz_kw in _zz_views:
            zz_open(_zz_tab, **_zz_kw)
            _zz_odd, _zz_rets = zz_leaving()
            _zz_page = bool(_zz_kw.get("sel")) and _zz_kw.get("sel") not in ("me", "sana")
            _zz_want = [None, ("go", "cafeteria")] if _zz_page else [None]
            if _zz_odd or _zz_rets != _zz_want:
                _zz_bad.append((_zz_name, _zz_odd, _zz_rets))
        check(not _zz_bad, "on every view, every button but Return and go leaves the journal up", _zz_bad)
        ## And a few, really pressed.
        zz_open("people")
        for _zz_wid in ("jr_card_megumi", "jr_psub_memories", "jr_psub_story", "jr_back", "jr_card_me", "jr_msub2_records",
                        "jr_back", "jr_tab_stats", "jr_ssub_year", "jr_tab_inventory", "jr_tab_people"):
            _zz_b = zz_widget(_zz_wid)
            _zz_v = renpy.run(_zz_b.action) if _zz_b is not None else "missing"
            zz_render(0.15)
            check(_zz_v is None and renpy.get_screen("journal") is not None, "pressing %s leaves the journal up" % _zz_wid, _zz_v)
        renpy.hide_screen("journal")

    ## The go button, pressed in the campus journal: the loop's branch.
    python:
        zz_st.script[:] = [
            lambda: zz_set(sel="yuji", psub="story"),
            lambda: zz_nil(check(zz_widget("jr_go_btn") is not None and journal_editable(), "campus journal: the go button is offered")),
            lambda: renpy.run(zz_widget("jr_go_btn").action),
        ]
    show screen zz_driver
    call screen journal("people")
    hide screen zz_driver
    $ _zz_j = _return
    $ check(_zz_j == ("go", "cafeteria"), "pressing go returns (\"go\", loc) to the loop", _zz_j)
    $ autoplay(True)
    if isinstance(_zz_j, tuple) and _zz_j and _zz_j[0] == "go":
        call rule_walk_to(_zz_j[1])
    $ autoplay(False)
    $ check(here == "cafeteria", "and the loop's rule_walk_to walks me there", here)
    $ here = "courtyard"

    ## From the game menu (a menu context) the journal returns only True.
    python:
        zz_patch("main_story_complete", lambda: True)
        zz_open("missions", msub="story", mfilter="all")
        check(("arc_two",) in zz_return_values(), "(campus) Begin Arc Two returns (\"arc_two\",)", zz_return_values())
        renpy.hide_screen("journal")
        zz_st.menu = builtins.dict()
        zz_st.menu_driver = True
        zz_st.script[:] = [
            lambda: zz_nil(zz_st.menu.update(menu=bool(renpy.context()._menu), editable=journal_editable())),
            lambda: zz_set(sel="yuji", psub="story"),
            lambda: zz_nil(zz_st.menu.update(go=zz_widget("jr_go_btn") is not None, rets=zz_return_values(),
                                             heads=[t for t in zz_texts("journal") if t in ("RIGHT NOW", "USUALLY")],
                                             line=zz_has("Cafeteria — halfway through an enormous bowl"))),
            lambda: zz_nil(shot("menu_page_yuji", wait=0)),
            lambda: zz_set(sel=None, tab="missions", msub="story", mfilter="all"),
            lambda: zz_nil(zz_st.menu.update(rets2=zz_return_values())),
            lambda: zz_set(tab="equipment"),
            lambda: zz_nil(zz_st.menu.update(rets3=zz_return_values())),
            lambda: zz_press(lambda a: type(a).__name__ == "Return" and a.value is None, "Return"),
        ]
        ShowMenu("journal", "people")()
        zz_st.menu_driver = False
        renpy.hide_screen("zz_driver")
        _zz_mn = zz_st.menu
        check(_zz_mn.get("menu") and not _zz_mn.get("editable"), "the game menu's journal runs in a menu context, read-only", _zz_mn)
        check(_zz_mn.get("go") is False, "no go button in the game menu's journal", _zz_mn)
        check(_zz_mn.get("heads") == ["USUALLY"] and _zz_mn.get("line") is False,
              "opened mid-scene the panel is headed Usually and the first line is left out", _zz_mn)
        check(all(v is None for v in _zz_mn.get("rets", [1]) + _zz_mn.get("rets2", [1]) + _zz_mn.get("rets3", [1])),
              "from the game menu the journal returns only True (every Return is the plain one)", _zz_mn)
        zz_unpatch("main_story_complete")
        zz_unpatch("person_now")

    ## The loop's old tuple: ("journal", "memories") opens People.
    python:
        zz_st.script[:] = [
            lambda: zz_nil(check(zz_js()["tab"] == "people", "call screen journal(\"memories\") opens People", zz_js()["tab"])),
            zz_done,
        ]
    show screen zz_driver
    $ _zz_jr = ("journal", "memories")
    call screen journal(_zz_jr[1])
    hide screen zz_driver

    ## =====================================================================
    ## 6. No thread stage line says "you" or "your"
    ## =====================================================================
    python:
        _zz_you = re.compile(r"\b(you|your|yours|yourself|you're|you've|you'd|you'll)\b", re.I)
        _zz_bad = [(t, l) for t in THREAD_ORDER for l in THREADS[t]["stages"] if _zz_you.search(l)]
        check(not _zz_bad, "no thread stage line contains \"you\" or \"your\"", _zz_bad)
        check(sum(len(THREADS[t]["stages"]) for t in THREAD_ORDER) == 28 and all(len(THREADS[t]["stages"]) in (3, 4) for t in THREAD_ORDER),
              "the threads keep their stage counts (only the index is saved)")

    ## =====================================================================
    ## 7. The grid: 18 cards without scrolling; 26 scroll; six words a card
    ## =====================================================================
    python:
        _zz_cards = jr_people_cards()
        check(len(_zz_cards) == 18 and _zz_cards[0]["who"] == "me" and _zz_cards[-1]["who"] == "sana"
              and [e["who"] for e in _zz_cards[1:-1]] == [e["who"] for e in JOURNAL_CAST if e["who"] != "sana"],
              "18 cards: Me, the cast in order, Sana", [e["who"] for e in _zz_cards])
        zz_open("people")
        shot("people_grid_18")
        _zz_r = [zz_rect("journal", "jr_card_" + e["who"]) for e in _zz_cards]
        check(all(_zz_r) and all(r[2:] == (288, 196) for r in _zz_r), "every card is 288x196", _zz_r)
        _zz_ys = sorted(set(r[1] for r in _zz_r if r))
        _zz_xs = sorted(set(r[0] for r in _zz_r if r))
        check(len(_zz_ys) == 4 and len(_zz_xs) == 5 and _zz_xs[-1] + 288 - _zz_xs[0] == 1520,
              "five across (5 x 288 + 4 x 20 = 1520), four rows", (_zz_xs, _zz_ys))
        check(all(_zz_r) and max(r[1] + r[3] for r in _zz_r) - min(r[1] for r in _zz_r) == 844 and all(zz_body(r) for r in _zz_r),
              "all 18 cards fit without scrolling: 844 px in the 928 px body", (_zz_ys, _zz_r[-1]))
        _zz_vp = zz_widget("jr_people_vp")
        check(_zz_vp is not None and _zz_vp.yadjustment.range == 0, "with 18 cards there is nothing to scroll", getattr(_zz_vp, "yadjustment", None) and _zz_vp.yadjustment.range)
        ## Words: each card alone, icon words off.
        _zz_over = builtins.list()
        _zz_most = (0, None)
        for _zz_e in _zz_cards:
            renpy.show_screen("jr_person_card", journal_state(), _zz_e)
            _zz_w = zz_words("jr_person_card")
            renpy.hide_screen("jr_person_card")
            _zz_most = max(_zz_most, (len(_zz_w), _zz_e["who"]))
            if len(_zz_w) > 6:
                _zz_over.append((_zz_e["who"], _zz_w))
        note("the wordiest card", _zz_most)
        check(not _zz_over, "zz_words on one card is at most 6, for every card", _zz_over)
        check(len(zz_btns("journal")) >= 18 and len([b for b in zz_btns("journal") if getattr(b, "id", "") and str(b.id).startswith("jr_card_")]) == 18,
              "one button a card")
        ## Gojo's chip.
        renpy.show_screen("jr_person_card", journal_state(), [e for e in _zz_cards if e["who"] == "gojo"][0])
        _zz_tx = zz_texts("jr_person_card")
        renpy.hide_screen("jr_person_card")
        check("OFF THE SCALE" in _zz_tx and jr_grade_chip("gojo") == ("sp", "Off the scale") and grade_is_special("sp"),
              "Gojo's chip reads OFF THE SCALE on the Special fill", _zz_tx)
        check(jr_grade_line("gojo") == "Off the scale", "jr_grade_line(\"gojo\") is still \"Off the scale\"", jr_grade_line("gojo"))
        ## Hover: the Next line is the card's tooltip, as a (text, key) tuple.
        _zz_tip = getattr(zz_widget("jr_card_megumi"), "_tooltip", None)
        check(isinstance(_zz_tip, builtins.tuple) and len(_zz_tip) == 2 and _zz_tip[0] == jr_card_tip("megumi")
              and _zz_tip[0].replace("\n", " — ", 1) == jr_next("megumi") and _zz_tip[0].startswith("Next: ")
              and _zz_tip[1] == "jr_card_megumi", "a card's hover label is its Next line, as a (text, key) tooltip", _zz_tip)
        check("Next: " not in " ".join(zz_texts("journal")), "at rest no card prints its Next line")
        ## A person's page, measured the same way (the 4.0 budget is 70).
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        for _zz_who in ("megumi", "yuji", "gojo"):
            renpy.show_screen("jr_person_detail", journal_state(), _zz_who)
            note("words on %s's page (budget 70)" % _zz_who, "%d: %s" % (len(zz_words("jr_person_detail")), " ".join(zz_words("jr_person_detail"))))
            renpy.hide_screen("jr_person_detail")
        zz_unpatch("person_now")
        renpy.hide_screen("journal")

        ## 26 cards: the list jr_people reads, patched.
        _zz_base = jr_people_cards()
        _zz_26 = _zz_base + [dict(_zz_base[1], key="zz%d" % i) for i in range(8)]
        zz_patch("jr_people_cards", lambda: _zz_26)
        zz_open("people")
        _zz_vp = zz_widget("jr_people_vp")
        check(_zz_vp.yadjustment.range > 0, "with 26 cards the grid scrolls", _zz_vp.yadjustment.range)
        check(not zz_body(zz_rect("journal", "jr_card_zz7")), "(before scrolling the last card is out of view)", zz_rect("journal", "jr_card_zz7"))
        _zz_vp.yadjustment.change(_zz_vp.yadjustment.range)
        zz_render(0.3)
        shot("people_grid_26_end")
        _zz_last = zz_rect("journal", "jr_card_zz7")
        check(zz_body(_zz_last) and _zz_last[2:] == (288, 196), "the last of 26 cards can be scrolled to, whole", _zz_last)
        _zz_row = [zz_rect("journal", "jr_card_zz%d" % i) for i in range(3, 8)]
        check(all(zz_body(r) and r[2:] == (288, 196) for r in _zz_row), "no card in view is clipped at the end of the scroll", _zz_row)
        _zz_v = renpy.run(zz_widget("jr_card_zz7").action)
        zz_render(0.2)
        check(_zz_v is None and zz_js()["sel"] == _zz_base[1]["who"], "and it can be pressed: its page opens", zz_js()["sel"])
        zz_unpatch("jr_people_cards")
        renpy.hide_screen("journal")

        ## Not met yet: one row of silhouettes under the cards.
        _zz_keep = (builtins.list(roster), set(flags))
        for _zz_w in ("maki", "panda", "toge", "utahime"):
            roster.remove(_zz_w)
        for _zz_e in JOURNAL_CAST:
            if _zz_e["met"][0] == "flag":
                flags.discard(_zz_e["met"][1])
        zz_open("people")
        shot("people_grid_unmet")
        _zz_un = jr_people_unmet()
        _zz_r = [zz_rect("journal", "jr_unmet_" + e["who"]) for e in _zz_un]
        check(len(_zz_un) == 9 and zz_has("NOT MET YET") and all(r and r[2:] == (72, 72) and zz_body(r) for r in _zz_r)
              and len(set(r[1] for r in _zz_r)) == 1,
              "NOT MET YET: one row of 72x72 silhouettes at the bottom, inside the body", _zz_r)
        check(not any(e["hint"] in zz_texts("journal") for e in _zz_un) and not any(jr_short(e["who"]) in zz_texts("journal") for e in _zz_un),
              "an unmet person's hint is the hover label, not on the page; no unmet name is drawn")
        roster[:] = _zz_keep[0]
        flags.clear(); flags.update(_zz_keep[1])
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 8. Records
    ## =====================================================================
    python:
        zz_patch("pc_records", lambda: [])
        zz_patch("fish_records", lambda: [])
        zz_patch("cards_records", lambda: dict(today=0))
        check(jr_records() == [], "with the three stubs Records has no section")
        zz_open("people", sel="me", msub2="records")
        shot("me_records_empty")
        check(zz_js()["sel"] == "me" and zz_has("Nothing on record yet.")
              and not any(t in ("PAGES I'VE READ", "THE RECORD BOOK", "AT THE CARD TABLE") for t in zz_texts("journal")),
              "Records renders with the three stubs and shows no section")
        zz_patch("pc_records", lambda: ["Ryomen Sukuna", "The Three Great Clans"])
        zz_open("people", sel="me", msub2="records")
        check(zz_has("PAGES I'VE READ") and zz_has("Ryomen Sukuna") and zz_has("The Three Great Clans")
              and jr_records() == [("PAGES I'VE READ", ["Ryomen Sukuna", "The Three Great Clans"])],
              "with pc_records patched to two titles it lists two", jr_records())
        zz_patch("fish_records", lambda: [("Carp", 42), ("River Lord", None)])
        zz_patch("cards_records", lambda: dict(today=1200))
        zz_open("people", sel="me", msub2="records")
        shot("me_records_full")
        check(zz_has("Carp — 42 cm") and zz_has("River Lord — not caught yet") and zz_has("Won today: ¥1,200"),
              "the record book and today's card winnings each get a section", jr_records())
        zz_unpatch("pc_records", "fish_records", "cards_records")
        renpy.hide_screen("journal")
        _zz_src = zz_source()
        if _zz_src is not None:
            _zz_hit = [n for n in ("PC_PAGES", "pc_read", "FISH_KINDS", "fish_log", "cards_won") if n in _zz_src]
            check(not _zz_hit, "ui_journal.rpy reads none of PC_PAGES, pc_read, FISH_KINDS, fish_log, cards_won", _zz_hit)

    ## =====================================================================
    ## 9. The requirement checklist
    ## =====================================================================
    python:
        _zz_seen_marks = builtins.list()
        zz_patch("item_requirements", lambda id: [])
        for _zz_name, _zz_tab, _zz_kw in (("equipment", "equipment", {}), ("the talisman picker", "equipment", dict(pick=("talisman", 0))),
                                          ("the tool picker", "equipment", dict(pick=("tool", 0))),
                                          ("inventory", "inventory", dict(inv_sel="paper_ward"))):
            zz_open(_zz_tab, **_zz_kw)
            if "✓" in zz_texts("journal") or "✗" in zz_texts("journal"):
                _zz_seen_marks.append(_zz_name)
        check(not _zz_seen_marks, "with the stub ([]) nothing is added to the pickers or the item panels", _zz_seen_marks)
        zz_patch("item_requirements", lambda id: [("Grade 2", True), ("Control 50 · I have 31", False)])
        _zz_seal = renpy.easy.color(gui.seal)
        for _zz_name, _zz_tab, _zz_kw, _zz_n in (("the Equipment panels", "equipment", {}, 2),
                                                 ("the talisman picker", "equipment", dict(pick=("talisman", 0)), 2),
                                                 ("the tool picker", "equipment", dict(pick=("tool", 0)), 2),
                                                 ("the Inventory panel", "inventory", dict(inv_sel="paper_ward"), 1)):
            zz_open(_zz_tab, **_zz_kw)
            shot("reqs_" + _zz_tab + ("_" + _zz_kw["pick"][0] if "pick" in _zz_kw else ""))
            _zz_tx = zz_texts("journal")
            _zz_bad_node = zz_node("Control 50 · I have 31")
            check(_zz_tx.count("Grade 2") >= _zz_n and _zz_tx.count("Control 50 · I have 31") >= _zz_n
                  and _zz_tx.count("✓") >= _zz_n and _zz_tx.count("✗") >= _zz_n
                  and _zz_bad_node is not None and renpy.easy.color(_zz_bad_node.style.color) == _zz_seal,
                  "%s: both requirement chips render, the unmet one in seal red" % _zz_name,
                  (_zz_tx.count("Grade 2"), _zz_tx.count("Control 50 · I have 31"), _zz_bad_node and _zz_bad_node.style.color))
        zz_unpatch("item_requirements")
        ## The tool picker says why a tool can't be held.
        zz_patch("can_hold", lambda id: (False, "Needs Grade 2") if id == "nunchaku" else (True, ""))
        zz_open("equipment", pick=("tool", 0))
        _zz_b = zz_widget("jr_pick_nunchaku")
        check(zz_has("Needs Grade 2") and _zz_b is not None and not _zz_b.is_sensitive()
              and ("slaughter_demon", False, "In my hand") in jr_pick_options("tool"),
              "the tool picker shows can_hold's reason, and the row can't be pressed", jr_pick_options("tool"))
        zz_unpatch("can_hold")
        ## Grade chips: the journal's own gold chip is gone from the gear.
        zz_open("inventory", inv_sel="paper_ward")
        check(zz_has("GRADE 4"), "an item's grade is a grade chip")
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 10. Leads
    ## =====================================================================
    python:
        zz_patch("pc_leads", lambda: [])
        zz_open("missions")
        check(not zz_has("LEADS"), "with the stub the Leads section is absent")
        zz_patch("pc_leads", lambda: [("sukuna", "Look up what was on the ridge")])
        zz_open("missions")
        shot("missions_leads")
        _zz_tx = zz_texts("journal")
        _zz_lead = "Look up what was on the ridge — my computer"
        check("LEADS" in _zz_tx and _zz_lead in _zz_tx and _zz_tx.index("LEADS") < _zz_tx.index("Story")
              and _zz_tx.index(_zz_lead) < _zz_tx.index("Story"),
              "with pc_leads patched to one row the Missions tab shows it first", [t for t in _zz_tx if t in ("LEADS", _zz_lead, "Story")])
        for _zz_s in ("character", "board"):
            zz_js().update(msub=_zz_s)
            zz_render(0.2)
            check(zz_has("LEADS"), "the lead stays first on the %s sub-tab" % _zz_s)
        zz_unpatch("pc_leads")
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 11. Stats: one pane at a time
    ## =====================================================================
    python:
        _zz_tech = jr_tech()["verb_desc"]
        _zz_marks = dict(overview=lambda tx: "Health" in tx and any(t.startswith("PROMOTION") for t in tx) and any(t.startswith("First-year") for t in tx),
                         light=lambda tx: _zz_tech in tx,
                         year=lambda tx: any(t.startswith("MY YEAR") for t in tx))
        for _zz_s in ("overview", "light", "year"):
            zz_open("stats", ssub=_zz_s)
            shot("stats_" + _zz_s)
            _zz_tx = zz_texts("journal")
            _zz_on = [k for k in ("overview", "light", "year") if _zz_marks[k](_zz_tx)]
            check(_zz_on == [_zz_s], "Stats, ssub=%s: only that pane's texts are drawn" % _zz_s, _zz_on)
            check(all(zz_widget("jr_ssub_" + k) is not None for k in ("overview", "light", "year"))
                  and all(l in _zz_tx for l in ("Overview", "Last Light", "My year")), "Stats, ssub=%s: the three chips are there" % _zz_s)
        check(len(jr_bars()) == 6, "Overview has six bars")
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 12. The worst case of every full view; nothing un-picklable on screen
    ## =====================================================================
    python:
        gui.icon_words = "auto"
        ## R10: what a save keeps of a screen is its scope. On every view it
        ## must pickle, and hold plain values only (no displayable, no
        ## function). (A whole renpy.save here would also pickle this
        ## harness's own lambdas, which are not the game's state.)
        import pickle as zz_pickle
        _zz_bad = builtins.list()
        for _zz_name, _zz_tab, _zz_kw in _zz_views:
            zz_open(_zz_tab, **_zz_kw)
            _zz_scope = renpy.get_screen("journal").scope
            for _zz_k, _zz_v in _zz_scope.items():
                if isinstance(_zz_v, renpy.display.displayable.Displayable) or callable(_zz_v):
                    _zz_bad.append((_zz_name, _zz_k, type(_zz_v).__name__))
            try:
                zz_pickle.dumps(builtins.dict(_zz_scope), zz_pickle.HIGHEST_PROTOCOL)
            except Exception as _zz_err:
                _zz_bad.append((_zz_name, repr(_zz_err)[:160]))
        check(not _zz_bad, "on every view the journal's screen scope pickles and holds no displayable or function (R10)", _zz_bad)
        renpy.hide_screen("journal")
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        zz_patch("pc_leads", lambda: [("sukuna", "Look up what was on the ridge")])
        zz_patch("item_requirements", lambda id: [("Grade 2", True), ("Control 50 · I have 31", False)])
        bonds["nobara"] = 61
        affection["nobara"] = 35
        _zz_orig_state = journal_state
        for _zz_name, _zz_tab, _zz_kw, _zz_hover in (
                ("worst_journal", "people", {}, "jr_card_megumi"),
                ("worst_journal_person", "people", dict(sel="nobara", psub="story"), "jr_go_btn"),
                ("worst_journal_person_memories", "people", dict(sel="yuji", psub="memories"), None),
                ("worst_journal_me", "people", dict(sel="me"), None),
                ("worst_journal_missions", "missions", dict(mfilter="all"), None),
                ("worst_journal_stats", "stats", {}, None),
                ("worst_journal_equipment", "equipment", {}, None),
                ("worst_journal_picker", "equipment", dict(pick=("talisman", 0)), None),
                ("worst_journal_inventory", "inventory", dict(inv_sel="slaughter_demon"), None)):
            renpy.hide_screen("journal")
            zz_patch("journal_state", lambda tab="people", kw=_zz_kw: builtins.dict(_zz_orig_state(tab), **kw))
            _zz_ok = zz_worst("journal", _zz_tab, hover=_zz_hover, name=_zz_name)
            zz_unpatch("journal_state")
            check(_zz_ok and zz_js()["tab"] == _zz_tab, "zz_worst screenshot: " + _zz_name)
        ## R6: toasts wait while the journal is up. toast_room() is P2's.
        toast_clear()
        toast("A reward", "item")
        zz_open("people")
        _zz_room = toast_room()
        if _zz_room == (0, 0, 0):
            check(toast_visible() == [] or not toast_visible(), "zz_worst(\"journal\"): no toast is drawn over the journal")
        else:
            note("zz_worst(\"journal\"): no toast drawn",
                 "DEFERRED to P8 (7.3): toast_room() is still wave 0's stub %r here, so toasts draw over the journal until P2's lanes are merged" % (_zz_room,))
        toast_clear()
        zz_unpatch()
        renpy.hide_screen("journal")

    $ finish()
