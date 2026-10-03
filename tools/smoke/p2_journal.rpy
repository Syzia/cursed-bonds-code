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
##  12. worst      zz_worst screenshots of every full view. No toast over the
##                 journal: the journal is tagged `menu`, which is what 4.2's
##                 toast_room() tests, and with 4.2's value for that row no
##                 toast is drawn and none is lost. With this tree's own
##                 toast_room() the line is a check once it returns (0, 0, 0)
##                 and a NOTE while it is still wave 0's stub (P2's file).
##  13. budget     4.0: a person's page holds at most 70 words at rest, for
##                 every person, at every stage of their story, whether I can
##                 see where they are, can't, or am mid-scene; and, for
##                 the eight with a story, with the stub's "Off campus" and
##                 with them beside me. Every learned line is still a row
##                 (printed whole, or by its short name with the whole line
##                 on hover, or folded with the oldest into "n earlier
##                 lines"); no row is a bare ellipsis.
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

    def zz_now_longest(who):
        """person_now as P1 will answer it for someone I can walk to: the
        longest place name on campus and that person's longest caption."""
        doing = builtins.max([row[0] for (w, loc), row in AMBIENT.items() if w == who] or [AMBIENT_FALLBACK[0]], key=len)
        return builtins.dict(place="dorm_common", name=LOCATIONS["dorm_common"]["name"], doing=doing,
                             reachable=True, hidden=False, with_me=False)

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
        ## A mission that starts wherever its giver is names where that is
        ## (cm_maki_1 has no place of its own).
        _zz_keep4 = (bonds.get("maki", 0), bonds.get("ijichi", 0), set(flags))
        flag("met_second_years")
        bonds["maki"] = 12
        note("cm_maki_1", mission_status("cm_maki_1"))
        _zz_next = [r for r in jr_story_rows("maki") if r["next"]]
        check(mission_status("cm_maki_1") in ("available", "active") and len(_zz_next) == 1 and _zz_next[0]["kind"] == "mission"
              and _zz_next[0].get("id") == "cm_maki_1" and _zz_next[0]["where"] == jr_story_where("maki")
              and "wherever" not in _zz_next[0]["where"],
              "a mission Maki can give now is the NEXT row, and its where is a place, not \"wherever Maki is\"", _zz_next)
        zz_patch("person_now", zz_now("dojo", "Dojo"))
        check([r for r in jr_story_rows("maki") if r["next"]][0]["where"] == "Dojo, right now", "(and where she is now, when I can see it)",
              [r for r in jr_story_rows("maki") if r["next"]])
        zz_patch("person_now", zz_now("courtyard", "With me", with_me=True))
        check([r for r in jr_story_rows("maki") if r["next"]][0]["where"] == "with me now", "(or with me now)")
        zz_unpatch("person_now")
        ## A mission with its own place keeps it.
        check(jr_mission_where(MISSION_BY_ID["cm_ijichi_1"], "ijichi") == jr_where_when(MISSION_BY_ID["cm_ijichi_1"])
              and jr_mission_where(MISSION_BY_ID["cm_ijichi_1"], "ijichi").startswith(LOCATIONS["gate"]["name"]),
              "a mission with a place of its own keeps it", jr_mission_where(MISSION_BY_ID["cm_ijichi_1"], "ijichi"))
        ## Nothing to do but wait: the first locked mission is the NEXT row.
        zz_patch("jr_next_hangout", lambda who: None)
        zz_patch("next_unlock", lambda who: None)
        _zz_st0 = mission_status("cm_ijichi_1")
        zz_patch("mission_status", lambda mid, _o=mission_status: ("locked" if mid == "cm_ijichi_1" else _o(mid)))
        _zz_rows = jr_story_rows("ijichi")
        _zz_next = [r for r in _zz_rows if r["next"]]
        check(len(_zz_next) == 1 and _zz_next[0]["kind"] == "mission" and _zz_next[0].get("id") == "cm_ijichi_1"
              and _zz_next[0]["state"] == "next" and _zz_next[0]["where"] and _zz_next[0]["line"],
              "when all that is left is a locked mission, it is the NEXT row, with what it waits for and where", _zz_rows)
        zz_patch("mission_status", lambda mid, _o=zz_st.patched["mission_status"]: ("closed" if mid == "cm_ijichi_1" else _o(mid)))
        check(not [r for r in jr_story_rows("ijichi") if r["next"]], "a mission closed by Arc Two is never the NEXT row",
              jr_story_rows("ijichi"))
        zz_unpatch("jr_next_hangout", "next_unlock", "mission_status")
        bonds["maki"], bonds["ijichi"] = _zz_keep4[0], _zz_keep4[1]
        flags.clear(); flags.update(_zz_keep4[2])
        ## A resolved thread: the next scene is not another chapter of it.
        _zz_keep4 = (threads.get("nobara_saori"), bonds["nobara"])
        threads["nobara_saori"] = len(THREADS["nobara_saori"]["stages"]) - 1
        _zz_rows = jr_story_rows("nobara")
        _zz_steps = [r for r in _zz_rows if r["kind"] == "step"]
        check(_zz_rows[0]["state"] == "done" and (not _zz_steps or _zz_steps[0]["title"] != "Spend time together"),
              "once a thread is resolved the step is not titled Spend time together", _zz_steps)
        if jr_next_hangout("nobara"):
            check(_zz_steps and _zz_steps[0]["title"] == "More time together" and _zz_steps[0]["next"], "it reads More time together", _zz_steps)
        threads["nobara_saori"], bonds["nobara"] = _zz_keep4
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
        ## The page's Closer line agrees with it (it used to read "Closer:
        ## Eat together — at Bond 10" over a NEXT row saying After roll call).
        check(jr_closer("megumi") == "Closer: after roll call", "before roll call the Closer line says after roll call too", jr_closer("megumi"))
        zz_open("people", sel="megumi", psub="story")
        shot("page_megumi_before_roll_call")
        check(zz_has("Closer: after roll call") and [t for t in zz_texts("journal") if t.startswith("After roll call")]
              and not [t for t in zz_texts("journal") if t.startswith("Closer: ") and " at Bond" in t],
              "and the page prints it: Right now and the NEXT row say one thing", [t for t in zz_texts("journal") if "loser" in t or "roll call" in t])
        flags.clear(); flags.update(_zz_keep[0])
        done_events.clear(); done_events.update(_zz_keep[1])
        check(jr_next("megumi").startswith("Next: Spend time together — ") and "roll call" not in jr_next("megumi"),
              "after roll call the Next line is the scene and where", jr_next("megumi"))
        check(jr_closer("megumi") == unlock_line("megumi") and "roll call" not in jr_closer("megumi"),
              "after roll call the Closer line is unlock_line again", (jr_closer("megumi"), unlock_line("megumi")))

    ## =====================================================================
    ## 5. Right now, and the go button
    ## =====================================================================
    python:
        ## The stub (or P1's real function): the page prints what it says.
        _zz_pn = person_now("yuji")
        zz_open("people", sel="yuji", psub="story")
        check(zz_has(jr_clip(jr_now_line(jr_now("yuji")), 72)), "Right now prints person_now(who) as it is today", (_zz_pn, [t for t in zz_texts("journal")][:12]))
        zz_patch("person_now", zz_now("cafeteria", "Cafeteria", "halfway through an enormous bowl"))
        zz_open("people", sel="yuji", psub="story")
        shot("page_yuji_story")
        check(zz_has("Cafeteria — halfway through an enormous bowl"), "Right now equals person_now(who)'s name and doing")
        ## While I can see where they are, "Usually: ..." is the panel's hover
        ## label (the page's word budget, 4.0); when I can't, it is printed.
        _zz_tip = getattr(zz_widget("jr_now"), "_tooltip", None)
        check(isinstance(_zz_tip, builtins.tuple) and _zz_tip[0] == "Usually\n" + jr_clip(usual_places("yuji"), 104) and _zz_tip[1] == "jr_now"
              and not any(t.startswith("Usually: ") for t in zz_texts("journal")),
              "while I can see where they are, Usually is the Right now panel's hover label", _zz_tip)
        renpy.set_focus("journal", "jr_now")
        shot("page_yuji_usually_hover")
        check(zz_has(jr_closer("yuji")) if jr_closer("yuji") else True, "the third line is the Closer hint", jr_closer("yuji"))
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
            _zz_printed = [t for t in zz_texts("journal") if t.startswith("Usually: ")]
            _zz_tip = getattr(zz_widget("jr_now"), "_tooltip", None)
            _zz_us = jr_clip(usual_places("yuji"), 104)
            check(isinstance(_zz_tip, builtins.tuple) and _zz_tip[0] == "Usually\n" + _zz_us
                  and (not _zz_printed if _zz_case == "with me" else
                       (_zz_printed == ["Usually: " + _zz_us.split(" · ")[0] + " …"] and " · " in _zz_us)),
                  "when " + _zz_case + ", Usually is " + ("on hover only" if _zz_case == "with me" else "printed as the first usual place, with the whole list on hover"),
                  (_zz_printed, _zz_tip))
        ## A long caption stays on one line: the Closer line keeps its place.
        zz_patch("person_now", zz_now("dorm_common", LOCATIONS["dorm_common"]["name"], "halfway through explaining a film nobody else here has seen or ever will see, at length"))
        zz_open("people", sel="nobara", psub="story")
        _zz_nd = zz_node(jr_clip(jr_now_line(jr_now("nobara")), 72))
        shot("page_now_long")
        check(_zz_nd is not None and len(jr_clip(jr_now_line(jr_now("nobara")), 72)) == 72
              and renpy.render(_zz_nd, 900, 200, 0, 0).height < 40,
              "a long Right now line is clipped to one line (72 characters)", _zz_nd and renpy.render(_zz_nd, 900, 200, 0, 0).height)
        ## A day Gojo is in: "In his office today." stands alone, and his
        ## usual places are the hover label.
        zz_patch("gojo_in_today", lambda: True)
        zz_patch("person_now", zz_now("gojo_office", "Somewhere I can't go right now", reachable=False, hidden=True))
        zz_open("people", sel="gojo", psub="story")
        _zz_tip = getattr(zz_widget("jr_now"), "_tooltip", None)
        check(zz_has("In his office today.") and not zz_any("Usually: ") and isinstance(_zz_tip, builtins.tuple)
              and _zz_tip[0] == "Usually\n" + jr_clip(usual_places("gojo"), 104),
              "on a day Gojo is in, the line reads In his office today. (no Usually:), and his usual places are on hover", _zz_tip)
        ## ... but never beside "Off campus" (no place at all, which is also
        ## wave 0's person_now stub): the two would contradict each other.
        zz_patch("person_now", zz_now(None, "Off campus", reachable=False))
        zz_open("people", sel="gojo", psub="story")
        check(zz_has("Off campus") and not zz_has("In his office today.") and zz_any("Usually: "),
              "on a day Gojo is in but has no place (Off campus), In his office today. is not printed; the first usual place is", zz_texts("journal"))
        shot("page_gojo_today_offcampus")
        zz_unpatch("gojo_in_today")
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
        _zz_bad = [(t, l) for t in THREAD_ORDER for l in [THREADS[t]["title"]] + THREADS[t]["short"] if _zz_you.search(l)]
        check(not _zz_bad, "nor does a thread's title or a stage's short name", _zz_bad)
        check(all(len(THREADS[t]["short"]) == len(THREADS[t]["stages"]) and all(1 <= jr_word_count(n) <= 2 for n in THREADS[t]["short"])
                  and len(set(THREADS[t]["short"])) == len(THREADS[t]["short"]) for t in THREAD_ORDER),
              "every stage has a short name of one or two words", [(t, THREADS[t]["short"]) for t in THREAD_ORDER])
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
        ## (what the card draws: the key it hands grade_fill; the card
        ## alone, so the grid behind it doesn't answer for it)
        renpy.hide_screen("journal")
        zz_render()
        _zz_fills = builtins.list()
        zz_patch("grade_fill", lambda v, _o=grade_fill: (_zz_fills.append(v), _o(v))[1])
        renpy.show_screen("jr_person_card", journal_state(), [e for e in _zz_cards if e["who"] == "gojo"][0])
        _zz_tx = zz_texts("jr_person_card")
        renpy.hide_screen("jr_person_card")
        zz_unpatch("grade_fill")
        zz_open("people")
        check("OFF THE SCALE" in _zz_tx and jr_grade_chip("gojo") == ("sp", "Off the scale") and grade_is_special("sp")
              and _zz_fills and all(grade_tier(v) == "sp" for v in _zz_fills),
              "Gojo's chip reads OFF THE SCALE on the Special fill (the card asks grade_fill for the Special tier)", (_zz_tx, _zz_fills))
        check(jr_grade_line("gojo") == "Off the scale", "jr_grade_line(\"gojo\") is still \"Off the scale\"", jr_grade_line("gojo"))
        ## Hover: the Next line is the card's tooltip, as a (text, key) tuple.
        _zz_tip = getattr(zz_widget("jr_card_megumi"), "_tooltip", None)
        check(isinstance(_zz_tip, builtins.tuple) and len(_zz_tip) == 2 and _zz_tip[0] == jr_card_tip("megumi")
              and _zz_tip[0].replace("\n", " — ", 1) == jr_next("megumi") and _zz_tip[0].startswith("Next: ")
              and _zz_tip[1] == "jr_card_megumi", "a card's hover label is its Next line, as a (text, key) tooltip", _zz_tip)
        check("Next: " not in " ".join(zz_texts("journal")), "at rest no card prints its Next line")
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
        ## R6: toasts wait while the journal is up. The lanes are P2's
        ## (toast_room() in ui_hud.rpy, 4.2); the journal's half is to be
        ## what that function tests for: a screen tagged `menu`.
        zz_open("people")
        check(renpy.get_screen("menu") is renpy.get_screen("journal") and renpy.get_screen("journal") is not None,
              "the journal is the screen tagged menu while it is up (what 4.2's toast_room() tests)")
        renpy.hide_screen("journal")
        ## With 4.2's value for that row, (0, 0, 0), nothing is drawn over
        ## the journal and nothing is lost.
        zz_patch("toast_room", lambda: (0, 0, 0))
        zz_patch("toast_limit", lambda: 0)
        _zz_ok = zz_worst("journal", "people", name="worst_journal_lanes")
        toast("A reward", "item")
        zz_render(0.5)
        check(_zz_ok and toast_visible() == [] and len(TOASTQ.items) == 1 and TOASTQ.items[0]["t_shown"] is None,
              "with toast_room() at 4.2's (0, 0, 0) for a menu screen, no toast is drawn over the journal and the queued one waits",
              (toast_visible(), len(TOASTQ.items)))
        zz_unpatch("toast_room", "toast_limit")
        ## With this tree's own toast_room().
        toast_clear()
        toast("A reward", "item")
        zz_open("people")
        _zz_room = toast_room()
        if _zz_room == (0, 0, 0):
            check(not toast_visible(), "zz_worst(\"journal\"): no toast is drawn over the journal")
        else:
            note("zz_worst(\"journal\"): no toast drawn, with this tree's toast_room()",
                 "NOT YET: toast_room() is still wave 0's stub %r in ui_hud.rpy (P2's file, frozen for P3), so toasts draw over the journal here; this line is a check on the merged tree" % (_zz_room,))
        toast_clear()
        zz_unpatch()
        renpy.hide_screen("journal")

    ## =====================================================================
    ## 13. The page's word budget (last: it walks every story to its end)
    ## =====================================================================
    python:
        ## 13. The page's budget (4.0): at most 70 words at rest. Everyone,
        ## at every stage of their story (-1: not opened), with the bond,
        ## the heart bar and a promotion that go with it, in three views.
        gui.icon_words = "never"
        _zz_over, _zz_most, _zz_lost, _zz_n = builtins.list(), (0, ""), builtins.list(), 0
        _zz_bare, _zz_folds, _zz_shorts = builtins.list(), builtins.list(), 0
        _zz_mixed = builtins.list()
        _zz_fold_re = re.compile(r"^(\d+) earlier lines?$")
        _zz_stub_now = person_now
        _zz_extra = [THREADS[t]["who"] for t in THREAD_ORDER] + ["ijichi", "nanami"]
        for _zz_stage in (-1, 0, 1, 2, 3):
            for _zz_tid in THREAD_ORDER:
                if _zz_stage < 0:
                    threads.pop(_zz_tid, None)
                else:
                    threads[_zz_tid] = min(_zz_stage, len(THREADS[_zz_tid]["stages"]) - 1)
            for _zz_e in JOURNAL_CAST:
                bonds[_zz_e["who"]] = 15 + 20 * (_zz_stage + 1)
                if is_romanceable(_zz_e["who"]):
                    affection[_zz_e["who"]] = 60
            if _zz_stage == 1:
                for _zz_w in ("yuji", "megumi", "nobara"):
                    promote(_zz_w, "g2", quiet=True)
            ## Before roll call the gate words the NEXT row "After roll call".
            _zz_rc = (set(flags), set(done_events))
            if _zz_stage == -1:
                flags.discard("roll_call")
                done_events.discard("st_roll_call")
            for _zz_mode, _zz_fn, _zz_live in (("seen", zz_now_longest, True),
                                               ("hidden", zz_now("gojo_office", "Somewhere I can't go right now", reachable=False, hidden=True), True),
                                               ("mid-scene", zz_now_longest, False),
                                               ("stub", _zz_stub_now, True),
                                               ("with me", zz_now("courtyard", "With me", with_me=True), True)):
                zz_patch("person_now", _zz_fn)
                if not _zz_live:
                    zz_patch("journal_editable", lambda: False)
                for _zz_e in JOURNAL_CAST:
                    _zz_who = _zz_e["who"]
                    ## Someone with no thread has no stages: first and last only.
                    if not jr_thread_id(_zz_who) and _zz_stage not in (-1, 3):
                        continue
                    ## The two extra views: the eight with a story and two others.
                    ## (at the first and last stage only, to keep the run
                    ## well inside the default timeout).
                    if _zz_mode in ("stub", "with me") and (_zz_who not in _zz_extra or _zz_stage not in (-1, 3)):
                        continue
                    renpy.show_screen("jr_person_detail", journal_state(), _zz_who)
                    _zz_w = zz_words("jr_person_detail")
                    _zz_n += 1
                    _zz_most = max(_zz_most, (len(_zz_w), "%s, stage %d, %s" % (_zz_who, _zz_stage, _zz_mode)))
                    if len(_zz_w) > 70:
                        _zz_over.append((_zz_who, _zz_stage, _zz_mode, len(_zz_w)))
                    ## Every learned line is still a row: printed whole, or
                    ## cut short with the whole line as its hover label.
                    _zz_tid = jr_thread_id(_zz_who)
                    if _zz_tid and _zz_stage >= 0:
                        ## (the tree zz_words has just rendered)
                        _zz_tx = [zz_text_string(d) for d in zz_text_nodes("jr_person_detail")]
                        _zz_tips = [b._tooltip[0] for b in zz_btns("jr_person_detail")
                                    if isinstance(getattr(b, "_tooltip", None), builtins.tuple)]
                        for _zz_line in THREADS[_zz_tid]["stages"][:thread_stage(_zz_tid) + 1]:
                            if not (_zz_line in _zz_tx or any(("\n" + _zz_line) in t for t in _zz_tips)):
                                _zz_lost.append((_zz_who, _zz_stage, _zz_mode, _zz_line))
                        ## A row each, but for the oldest folded into one.
                        _zz_f = [int(_zz_fold_re.match(t).group(1)) for t in _zz_tx if _zz_fold_re.match(t)]
                        if _zz_f:
                            _zz_folds.append((_zz_who, _zz_stage, _zz_mode, _zz_f[0]))
                        if len(_zz_f) > 1 or len([t for t in _zz_tx if t == "✓"]) + sum(_zz_f) - len(_zz_f) < thread_stage(_zz_tid) + 1:
                            _zz_lost.append((_zz_who, _zz_stage, _zz_mode, "rows"))
                        _zz_shorts += len([t for t in _zz_tx if t in THREADS[_zz_tid]["short"]])
                        ## Whole lines are the newest run: nothing older than
                        ## a line shown by its short name prints whole.
                        _zz_wh = [(l in _zz_tx) for l in THREADS[_zz_tid]["stages"][:thread_stage(_zz_tid) + 1]]
                        if _zz_wh != sorted(_zz_wh):
                            _zz_mixed.append((_zz_who, _zz_stage, _zz_mode, _zz_wh))
                        if [t for t in _zz_tx if t.strip() in ("…", "...", "✓ …") or (t.endswith("…") and not jr_word_count(t))]:
                            _zz_bare.append((_zz_who, _zz_stage, _zz_mode))
                    renpy.hide_screen("jr_person_detail")
                zz_unpatch("person_now", "journal_editable")
            flags.clear(); flags.update(_zz_rc[0])
            done_events.clear(); done_events.update(_zz_rc[1])
        note("the wordiest person page of %d measured" % _zz_n, _zz_most)
        check(_zz_n == 3 * (5 * len(THREAD_ORDER) + 2 * (len(JOURNAL_CAST) - len(THREAD_ORDER))) + 2 * 2 * (len(THREAD_ORDER) + 2) and not _zz_over,
              "a person's page holds at most 70 words at rest: everyone, every story stage, seen / hidden / mid-scene; the eight with a story and two others also with the stub's person_now and with me, at the first and last stage (4.0)", _zz_over)
        check(not _zz_lost, "on every one of those pages each learned stage line is there: whole, or by its short name with the whole line on hover, or folded with the oldest", _zz_lost[:6])
        check(not _zz_bare, "no row on any of those pages is a bare ellipsis", _zz_bare[:6])
        check(not _zz_mixed, "on every one of those pages the whole lines are the newest run: no line printed whole sits above one shown by its short name", _zz_mixed[:6])
        note("pages where the oldest lines are folded into one row", (len(_zz_folds), _zz_folds[:8]))
        note("short names printed across those pages", _zz_shorts)
        ## The fitting itself.
        threads["yuji_countdown"] = 3
        _zz_rows = jr_story_rows("yuji")
        _zz_wide, _zz_tight = jr_story_fit(_zz_rows, 500), jr_story_fit(_zz_rows, 0)
        _zz_fixed = sum(jr_word_count(jr_clip(r["title"], 60), jr_story_sub(r)) + 1 for r in _zz_rows if r["next"]) \
            + sum(jr_word_count(r["title"]) + 1 for r in _zz_rows if r["kind"] == "heading") \
            + sum(jr_word_count(r["line"]) for r in _zz_rows if r["kind"] == "later")
        _zz_names = jr_story_fit(_zz_rows, _zz_fixed + 8)
        _zz_all = THREADS["yuji_countdown"]["stages"]
        check(len(_zz_wide) == len(_zz_names) == len(_zz_rows)
              and all(r["show"] == r["line"] and not r["tip"] for r in _zz_wide if r["kind"] == "stage")
              and [r["show"] for r in _zz_names if r["kind"] == "stage"] == THREADS["yuji_countdown"]["short"]
              and all(r["tip"] == "The Countdown\n" + r["line"] for r in _zz_names if r["kind"] == "stage")
              and [r for r in _zz_tight if r["next"]][0]["sub"] == [r for r in _zz_wide if r["next"]][0]["sub"] != ""
              and all("show" not in r for r in _zz_rows),
              "jr_story_fit keeps every row: whole lines with room; short names with the whole line on hover without; the NEXT row is never cut",
              [(r["show"], r["tip"]) for r in _zz_names])
        _zz_fd = [r for r in _zz_tight if r["kind"] == "stage"]
        check(len(_zz_fd) == 1 and _zz_fd[0]["show"] == "4 earlier lines" and _zz_fd[0]["fold"] == 4
              and _zz_fd[0]["tip"] == "\n".join(["The Countdown"] + _zz_all) and len(_zz_tight) == len(_zz_rows) - 3,
              "with no room at all the learned lines fold into one row, \"4 earlier lines\", whose hover label lists them whole", _zz_fd)
        _zz_fd = [r for r in jr_story_fit(_zz_rows, _zz_fixed + 6) if r["kind"] == "stage"]
        check([r["show"] for r in _zz_fd] == ["2 earlier lines"] + THREADS["yuji_countdown"]["short"][2:]
              and _zz_fd[0]["tip"] == "\n".join(["The Countdown"] + _zz_all[:2]),
              "with room for some, only the oldest fold", [(r["show"], r["tip"]) for r in _zz_fd])
        check(not any(r["show"].strip() in ("", "…") for n in range(0, 80) for r in jr_story_fit(_zz_rows, n) if r["kind"] == "stage"),
              "at no budget is a row empty or a bare ellipsis")
        _zz_mid = jr_story_fit(_zz_rows, _zz_fixed + 22)
        _zz_st = [r for r in _zz_mid if r["kind"] == "stage"]
        check(_zz_st[-1]["show"] == _zz_st[-1]["line"] and _zz_st[0]["tip"] and _zz_st[0]["show"] == "Something quiet",
              "when room is short the newest learned line is the one printed whole", [(r["show"], bool(r["tip"])) for r in _zz_st])
        check(jr_word_count("{b}+2{/b} ◆ 1 Bond 35 · the Cafeteria") == 3 and jr_lead("He is the loudest person here", 3) == "He is the…"
              and jr_lead("He is the loudest person here", 0) == "He is…" and jr_usual_first("Dojo (mornings) · Riverside (evenings)") == "Dojo (mornings) …"
              and jr_usual_first("Around campus.") == "Around campus.",
              "jr_word_count counts as 4.0 does; jr_lead cuts at a word and never below two; jr_usual_first keeps the first place")
        ## A stage with no short name falls back to its first words.
        _zz_nos = jr_story_fit([dict(r, short="") for r in _zz_rows], _zz_fixed + 8)
        check([r["show"] for r in _zz_nos if r["kind"] == "stage"] == [jr_lead(l, 2) for l in _zz_all],
              "a line with no short name is cut to its first two words", [r["show"] for r in _zz_nos if r["kind"] == "stage"])
        ## A cut line's hover label, and the heart bar's.
        zz_patch("person_now", zz_now_longest)
        bonds["nobara"] = 95
        affection["nobara"] = 60
        threads["nobara_saori"] = 3
        zz_open("people", sel="nobara", psub="story")
        _zz_cut = [b for b in zz_btns() if str(getattr(b, "id", "")).startswith("jr_stage_")]
        check(_zz_cut and all(isinstance(b._tooltip, builtins.tuple) and b._tooltip[0].startswith("Somebody Remembered\n") and b._tooltip[1] == b.id for b in _zz_cut),
              "a cut line is a row whose hover label is the thread's title and the whole line", [getattr(b, "_tooltip", None) for b in _zz_cut])
        check(not any(t.endswith("…") for t in zz_texts("journal")) and any(t in THREADS["nobara_saori"]["short"] for t in zz_texts("journal")),
              "her cut lines print their short names, with no ellipsis", [t for t in zz_texts("journal") if t.endswith("…")])
        check(zz_has("More time together") or not jr_next_hangout("nobara"), "her resolved story's NEXT row reads More time together")
        if _zz_cut:
            renpy.set_focus("journal", _zz_cut[0].id)
        shot("page_nobara_story_cut_hover")
        _zz_tip = getattr(zz_widget("jr_heart"), "_tooltip", None)
        check(zz_has("♡ " + aff_rank(60)[1]) and (jr_aff_note("nobara") == "" or (isinstance(_zz_tip, builtins.tuple) and _zz_tip[0].endswith(jr_aff_note("nobara"))))
              and not zz_has(jr_aff_note("nobara") or "zz none"),
              "the heart bar prints its rank; what holds it back is its hover label", (_zz_tip, jr_aff_note("nobara")))
        check(zz_has("Promoted Day %s" % jr_promotions("nobara")[-1][0]), "the promotions line is the latest promotion's day", jr_promotions("nobara"))
        ## The tightest page: Maki, her story finished, in a room I can't
        ## enter (her nights, once P1's person_now is in).
        zz_patch("person_now", zz_now("girls_dorm", "Somewhere I can't go right now", reachable=False, hidden=True))
        threads["maki_zenin"] = 3
        zz_open("people", sel="maki", psub="story")
        shot("page_maki_hidden")
        _zz_tx = zz_texts("journal")
        check(not any(t.strip() == "…" for t in _zz_tx) and all((n in _zz_tx) != (l in _zz_tx) for n, l in zip(THREADS["maki_zenin"]["short"], THREADS["maki_zenin"]["stages"]) if n != "Heavenly Restriction")
              and any(t.startswith("Usually: ") and t.endswith(" …") for t in _zz_tx),
              "Maki in a room I can't enter, story finished: four named rows, no bare ellipsis, the first usual place printed", _zz_tx)
        renpy.hide_screen("journal")
        zz_unpatch("person_now")
        ## The Me page: "1st year" as on everyone's page; a name as long as
        ## the prompt allows stays left of the Back chip, with the chip and
        ## the year.
        _zz_nm = (mc_name, mc_surname)
        zz_open("people", sel="me")
        check(zz_has("1st year") and not zz_has("First-year"), "the Me page says 1st year, as every other page does")
        mc_name, mc_surname = "W" * 16, "M" * 16
        zz_open("people", sel="me")
        shot("me_long_name")
        _zz_back = zz_rect("journal", "jr_back")
        _zz_yr = zz_node("1st year")
        _zz_fit = jr_fit_name(jr_stats_title(), JR_DISPLAY_FONT, 40, 28, 600)
        check(_zz_fit[1] == 28 and _zz_fit[0].endswith("…") and jr_text_width(_zz_fit[0], JR_DISPLAY_FONT, 28) <= 600
              and zz_has(_zz_fit[0]) and _zz_yr is not None,
              "a name as long as the prompt allows is drawn smaller and clipped to 600 px, and the year is still drawn", _zz_fit)
        mc_name, mc_surname = "Bo", "Li"
        check(jr_fit_name(jr_stats_title(), JR_DISPLAY_FONT, 40, 28, 600) == (jr_stats_title(), 40), "a short name is left alone")
        mc_name, mc_surname = _zz_nm
        ## Sana's page with nothing on it speaks of her, not of "them".
        zz_patch("jr_page_memories", lambda who: [])
        zz_open("people", sel="sana")
        check(zz_has("Nothing yet. What I remember of her ends up here.") and not zz_any("with them"),
              "Sana's empty page says what I remember of her")
        zz_open("people", sel="yuji", psub="memories")
        check(zz_has("Nothing shared yet. Scenes I live through with them end up here."), "anyone else's empty Memories pane keeps its line")
        zz_unpatch("jr_page_memories")
        renpy.hide_screen("journal")
        gui.icon_words = "auto"

    $ finish()
