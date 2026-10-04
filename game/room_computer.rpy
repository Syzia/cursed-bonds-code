################################################################################
## Cursed Bonds — the computer in my room.
##
## Phase 2, P6 (PHASE2_DESIGN.md 4.11, D31, 6.1). A fake internet: five sites
## with different voices, twelve pages. Reading is free; the first read of a
## page gives Insight +1 (or the page's own `gives` in its place) and sets
## the flag researched_<page>. Two things reach outside the screen: the
## weekly cross-check of the board (one period) and the rumour thread that
## finds the Black Market.
##
##   PC_SITES, PC_PAGES     the sites and their pages (in-world documents:
##                          none of them addresses the reader)
##   pc_pages()             the pages that exist for me now, in order
##   pc_visit(page)         reads a page; returns the "Noted." line or ""
##   pc_has_read(page)      bool
##   pc_request(page, note) asks me to look a page up (missions use it)
##   pc_leads()             the open requests, [(page, note)]: the journal's
##                          Missions tab and this screen's "Requested reading"
##   pc_records()           the titles of the pages read: the journal's Me page
##   screen pc_screen(page="home")   returns ("page", id), ("check",), ("close",)
##   label sb_do_pc_open
##
## A mission that needs research: pc_request("<page>", "<the question>") when
## it should appear, and gate.flags=("researched_<page>",) on what it opens.
################################################################################

## The sites' colours, and the browser's own (2.1: tokens of this file).
define gui.pc_wiki   = '#8fb8de'
define gui.pc_blog   = '#ff8fb0'
define gui.pc_intra  = '#77e0a0'
define gui.pc_gene   = '#d8b46a'
define gui.pc_board  = '#b9a3ff'
define gui.pc_chrome = '#221d30'
define gui.pc_bar    = '#1b1727'
define gui.pc_side   = '#110e19'
define gui.pc_page   = '#16131f'

init -1 python:

    ## What a page gives on its first read when it names nothing of its own.
    PC_GIVES = ("insight", 1)

    ## site -> name, made-up address, the voice it is written in, and the
    ## name of its colour token (gui.<color>): dict(name, url, tone, color).
    PC_SITES = {
        "intra": dict(name="Tokyo Jujutsu High · Staff Intranet", url="intra.jujutsu-high.local",
                      tone="The school's own pages. Somebody left Ijichi signed in.", color="pc_intra"),
        "wiki": dict(name="Kwaidan Index", url="kwaidan-index.jp/wiki",
                     tone="A folklore wiki. Dry, and cited.", color="pc_wiki"),
        "blog": dict(name="TOKYO AFTER MIDNIGHT", url="tokyo-after-midnight.blog.jp",
                     tone="A rumour blog. It has never once been calm.", color="pc_blog"),
        "gene": dict(name="The Houses of Japan: A Register", url="houses-register.or.jp",
                     tone="A genealogy site. Stiff, and proud of it.", color="pc_gene"),
        "board": dict(name="yoru-ita /occult/", url="yoru-ita.net/occult",
                      tone="An anonymous board. Nobody signs anything.", color="pc_board"),
    }
    PC_SITE_ORDER = ("intra", "wiki", "blog", "gene", "board")

    ## The one request that ships (D31): (page, note, the flag that raises it).
    PC_AUTO_REQUESTS = [("sukuna", "What was that on the ridge?", "saw_the_ridge_veil")]

    ## The page that only exists while the market does (4.11).
    PC_MARKET_PAGE = "legends_market"
    PC_HOME = "home"
    PC_BOARD_PAGE = "board_reports"

    PC_PAGES = {
        "home": dict(
            site="intra", title="Intranet home",
            body=[
                "Session: IJICHI K. · Device: student loan unit 14 · Signed in 41 days ago.",
                "Reminder to all auxiliary staff: sign out of a device before it is issued to a student. This is the fourth reminder this term.",
            ],
            links=["techniques", "board_reports"], needs=None, gives=None),

        "techniques": dict(
            site="intra", title="Note 4: Innate techniques",
            body=[
                "Prepared by the Auxiliary Office for first-year orientation. Not for circulation outside the school.",
                "Cursed energy is common to every sorcerer. An innate technique is not. It is inherited or it is absent, it is fixed by about the age of six, and it cannot be taught. Students are asked not to describe their techniques to persons outside their year without a supervisor's consent.",
                "Three measures are recorded for each student. Reserve: how much cursed energy is held. Control: how finely it is shaped. Output: how much can be released at once. A grade states what a sorcerer may be sent to face. It is not a measure of worth, and the Office asks that it not be treated as one.",
                "Awakenings after the age of fifteen are rare, and are to be reported to the Grading Office within the week.",
            ],
            links=["board_reports"], needs=None, gives=("insight", 2)),

        "board_reports": dict(
            site="intra", title="Posted assignments",
            body=[
                "Assignments are surveyed and graded by the Grading Office before they are posted. The posted grade is the Office's.",
                "Field staff with a concern about a survey may file form 7-C. Form 7-C is reviewed by the Grading Office.",
            ],
            links=["techniques"], needs=None, gives=None),

        "sukuna_folk": dict(
            site="wiki", title="Ryomen-sukuna (folklore)",
            body=[
                "Ryomen-sukuna is a figure of Hida Province, first recorded in the Nihon Shoki under the sixty-fifth year of the Emperor Nintoku: one body with two faces set back to back, four arms and four legs, who would not obey the court and was put down by a commander sent for the purpose. (1)",
                "Temple tradition in the same province disagrees with the chronicle. There he is a benefactor, and the founder of more than one mountain temple. (2)",
                "A third body of tales, not attested before the medieval period, gives the name to a sorcerer of the Heian era, spoken of as a calamity and not as a man. (3) These tales agree on little, except that he was not defeated in his lifetime and that, after it, twenty fingers were kept.",
                "Notes. (1) Nihon Shoki, scroll 11. (2) Oral; several versions. (3) Citation needed.",
            ],
            links=["sukuna"], needs=None, gives=None),

        "sukuna": dict(
            site="wiki", title="Ryomen Sukuna (sorcerer)",
            body=[
                "This article is about the sorcerer of the Heian era. For the figure of Hida Province, see Ryomen-sukuna (folklore).",
                "Later sources call him the King of Curses, and the strongest sorcerer in history. The second phrase recurs word for word in accounts that otherwise share nothing. (1)",
                "After his death the body could not be destroyed. Its twenty fingers were cut away and sealed separately, as cursed objects of the highest grade. (2) Their whereabouts are not public.",
                "The disposition of the body itself is unrecorded. One late source claims it was carried east and set on a mountain, under a curtain, where the strong might keep watch over it in turns. (3) The claim is uncited.",
                "This article has been nominated for deletion eleven times. Each nomination was withdrawn by the account that made it.",
            ],
            links=["sukuna_folk"], needs="saw_the_ridge_veil", gives=None),

        "gojo": dict(
            site="blog", title="The man in the blindfold",
            body=[
                "Third sighting this month, and this one comes with a PHOTO. It is blurry. They are always blurry. Why are they always blurry?",
                "Tall. White hair. A black blindfold, at night, in Shibuya, walking as if the street had been built for him. One reader swears he stepped off a roof and simply did not fall. Another says the rain went around him. AROUND.",
                "This blog has ruled out: a stunt, a street magician, a very committed fashion student. This blog has not ruled out: the government.",
                "The comments keep saying there is a school in the mountains. There is no school in the mountains. This blog checked. There is a temple, and a religious boarding academy with no website and no telephone number, which is EXACTLY what a school in the mountains would have.",
                "More as it comes. He was eating a crepe.",
            ],
            links=["legends"], needs=None, gives=None),

        "clans": dict(
            site="gene", title="The three great houses",
            body=[
                "Three houses stand above the rest of the jujutsu world, and have done since the Heian court. This Register lists them in alphabetical order, having learned not to list them in any other.",
                "Gojo. Kamo. Zen'in. Each holds an inherited technique that the others do not, each keeps its own records, and each has, at some point in the last thousand years, declined to recognise one of the other two.",
                "A sorcerer born outside the three houses is not thereby lesser. The Register is obliged to say so, and does.",
                "Entries for the individual houses follow. Portions of each are restricted at the request of the house concerned.",
            ],
            links=["clan_gojo", "clan_kamo", "clan_zenin"], needs=None, gives=None),

        "clan_gojo": dict(
            site="gene", title="The House of Gojo",
            body=[
                "The Gojo house traces its descent from Sugawara no Michizane, and has never been asked to prove it.",
                "Its inheritance is the Limitless, a technique that few of its bearers have been able to put to any use, and, perhaps once in several centuries, the Six Eyes, which make the Limitless usable. The two have appeared together in one person only a handful of times.",
                "The present head holds both. He is the first to do so in some four hundred years, and the house is, for most practical purposes, him. The Register records this without comment.",
                "The duel of the Keicho era, in which the heads of the Gojo and Zen'in houses killed one another before their lords, is treated under Zen'in.",
                "Entries after 1989 are restricted at the request of the family.",
            ],
            links=["clans", "clan_zenin"], needs=None, gives=None),

        "clan_kamo": dict(
            site="gene", title="The House of Kamo",
            body=[
                "The Kamo house is the oldest of the three by its own account, and the most careful of its forms. It holds that inheritance proves itself in the blood, and its inherited technique is the manipulation of blood itself.",
                "The house keeps to the old succession: the heir is the eldest son of the main line who bears the technique. Where the main line has not produced one, the house has made arrangements. The Register does not describe the arrangements.",
                "The name Noritoshi appears twice in the line. The first bearer, of the Meiji era, is recorded elsewhere as the most wicked sorcerer in the history of the craft. The house does not speak of him, and gave the name again regardless.",
                "Records of the main line's succession are restricted.",
            ],
            links=["clans"], needs=None, gives=None),

        "clan_zenin": dict(
            site="gene", title="The House of Zen'in",
            body=[
                "The Zen'in house is the largest of the three and counts its strength in numbers, in inherited techniques, and in cursed tools, of which it keeps the greatest private store in the country.",
                "Its most prized inheritance is the Ten Shadows. A Zen'in head who held it died in the Keicho era together with the head of the Gojo house, each by the other's hand, before their lords. Neither house has forgotten the terms.",
                "A household saying is recorded here as given: one who is not a Zen'in is not a sorcerer, and one who is not a sorcerer is not a person. Members born without cursed energy are omitted from this Register at the house's request.",
                "The entry for the branch families is restricted.",
            ],
            links=["clans", "clan_gojo"], needs=None, gives=None),

        "legends": dict(
            site="board", title="Seen around Tokyo, thread 41",
            body=[
                "No. 4411 · the alley behind the arcade off the shopping street. went past at 2am. every light on that one block was out, and only that block. never again",
                "No. 4412 · a transformer. happens",
                "No. 4413 · a transformer doesn't make the vending machines go dark from the inside",
                "No. 4419 · kawagoe, the sun mall, the shut one. third floor. the escalator runs at night with the power off. the security firm won't send anyone to that floor any more",
                "No. 4424 · a friend's cousin did night security there. says the cold on that floor has a direction",
                "No. 4430 · mods delete every post about the school. everyone has noticed. this one will be gone by morning",
            ],
            links=["legends_market", "gojo"], needs=None, gives=None),

        "legends_market": dict(
            site="board", title="The market under Shibuya",
            body=[
                "No. 3107 · not a joke thread. there is a staircase in Shibuya that is only there after the last train. at the bottom a man sits at a folding table under a paper lantern. cash only",
                "No. 3108 · what does he sell",
                "No. 3110 · paper. strips of paper with writing on. a friend bought one for a gambling habit, won for a month, and then lost a tooth",
                "No. 3115 · how does anyone find it",
                "No. 3116 · nobody finds it sober. the club two doors from the crossing. don't stop at the club's door. keep going down",
                "No. 3121 · went. the stairs weren't there",
                "No. 3122 · then it wasn't late enough",
            ],
            links=["legends"], needs=None, gives=("flag", "market_found")),
    }

    PC_PAGE_ORDER = ("home", "techniques", "board_reports", "sukuna_folk", "sukuna", "gojo",
                     "clans", "clan_gojo", "clan_kamo", "clan_zenin", "legends", "legends_market")

    ## What exists for me ----------------------------------------------------------

    def pc_can_see(page):
        """P6 (room_computer.rpy). bool: the page is listed, linked and
        counted for me now: it exists, its `needs` flag (if any) is set,
        and the market page only while market_exists()."""
        p = PC_PAGES.get(page)
        if p is None:
            return False
        if page == PC_MARKET_PAGE and not market_exists():
            return False
        return not p["needs"] or has_flag(p["needs"])

    def pc_pages():
        """P6. The ids of the pages that exist for me now, in order."""
        return [p for p in PC_PAGE_ORDER if pc_can_see(p)]

    def pc_links(page):
        """P6. The pages a page links to that exist for me now."""
        return [p for p in PC_PAGES[page]["links"] if pc_can_see(p)]

    def pc_address(page):
        """P6. The made-up address in the address bar."""
        p = PC_PAGES[page]
        site = PC_SITES[p["site"]]
        return "https://%s/%s" % (site["url"], "" if page == PC_HOME else page.replace("_", "-"))

    def pc_color(site):
        """P6. A site's colour (its gui.pc_* token)."""
        return getattr(gui, PC_SITES[site]["color"], gui.paper)

    ## Reading ---------------------------------------------------------------------

    def pc_has_read(page):
        """P6 (room_computer.rpy). bool: the page has been read."""
        return page in store.pc_read

    def pc_visit(page):
        """P6. Reads a page. The first read adds it to pc_read, sets the
        flag researched_<page> and gives the page's `gives` (Insight +1 when
        it names none). Returns the line for the "Noted." strip ("" on a
        later read, or for a page I can't see)."""
        if not pc_can_see(page) or page in store.pc_read:
            return ""
        store.pc_read.add(page)
        flag("researched_" + page)
        kind, what = PC_PAGES[page]["gives"] or PC_GIVES
        if kind == "flag":
            flag(what)
            return "Noted."
        before = getattr(store, kind)
        gain(kind, what, quiet=True)
        got = getattr(store, kind) - before
        if got > 0:
            return "Noted. %s +%d" % (kind.capitalize(), got)
        return "Noted."

    def pc_request(page, note=""):
        """P6 (room_computer.rpy). Returns None. Asks me to look a page up:
        it shows on the computer's home page and as a lead in the journal's
        Missions tab until the page is read. A page already read, already
        asked for, or not in PC_PAGES is left alone. The note is drawn as
        it is written: brackets and braces in it are not read as text tags
        or substitutions."""
        if page not in PC_PAGES or page in store.pc_read:
            return None
        if any(r[0] == page for r in store.pc_requests):
            return None
        store.pc_requests.append((page, str(note or PC_PAGES[page]["title"])))
        return None

    def pc_leads():
        """P6 (room_computer.rpy). The open requests, a list of (page,
        note): the one that ships with the game (PC_AUTO_REQUESTS, once its
        flag is set) and whatever missions asked for with pc_request, each
        until its page is read."""
        out = []
        seen = set()
        rows = [(p, n) for p, n, f in PC_AUTO_REQUESTS if has_flag(f)] + [tuple(r) for r in store.pc_requests]
        for page, note in rows:
            if page in seen or page in store.pc_read or not pc_can_see(page):
                continue
            seen.add(page)
            out.append((page, note))
        return out

    def pc_records():
        """P6 (room_computer.rpy). The titles of the pages read, in the
        browser's order, as a list of str."""
        return [PC_PAGES[p]["title"] for p in PC_PAGE_ORDER if p in store.pc_read]

    ## The cross-check (4.11) --------------------------------------------------------

    def pc_week():
        """P6. The board's week (what pc_checked_week is compared with)."""
        return board_week_now()

    def pc_checked():
        """P6. bool: this week's board has been cross-checked."""
        return store.pc_checked_week == pc_week()

    def pc_offers():
        """P6. This week's open offers as the page lists them: a list of
        (title, posted grade, flagged). Read-only: the rows come from
        board_summary(), which leaves out the cards already taken. An
        offer is flagged once the week is cross-checked and its true grade
        is not the one posted."""
        checked = pc_checked()
        return [(o["title"], o["grade"], bool(checked and o.get("true_grade", o["grade"]) != o["grade"]))
                for o in board_summary()["offers"]]

    def pc_check_ok():
        """P6. bool: there is a board to cross-check and this week's has
        not been done."""
        return bool(pc_offers()) and not pc_checked()

    def pc_check():
        """P6. bool: marks this week's board cross-checked. False (and
        nothing changes) when it already is, or there is nothing posted."""
        if not pc_check_ok():
            return False
        store.pc_checked_week = pc_week()
        return True

    ## Validator ---------------------------------------------------------------------

    def pc_validate():
        """P6. Lint findings for the sites and pages."""
        out = []
        if sorted(PC_PAGE_ORDER) != sorted(PC_PAGES):
            out.append("PC_PAGE_ORDER and PC_PAGES list different pages")
        if len(PC_PAGES) != 12:
            out.append("PC_PAGES has %d pages (twelve)" % len(PC_PAGES))
        if sorted(PC_SITE_ORDER) != sorted(PC_SITES):
            out.append("PC_SITE_ORDER and PC_SITES list different sites")
        for site, s in sorted(PC_SITES.items()):
            if set(s) != {"name", "url", "tone", "color"}:
                out.append("PC_SITES %s: keys %r" % (site, sorted(s)))
        for page, p in sorted(PC_PAGES.items()):
            if set(p) != {"site", "title", "body", "links", "needs", "gives"}:
                out.append("PC_PAGES %s: keys %r" % (page, sorted(p)))
                continue
            if p["site"] not in PC_SITES:
                out.append("PC_PAGES %s: unknown site %r" % (page, p["site"]))
            if not p["body"] or not all(isinstance(t, str) and t for t in p["body"]):
                out.append("PC_PAGES %s: an empty body" % page)
            for l in p["links"]:
                if l not in PC_PAGES:
                    out.append("PC_PAGES %s: links to an unknown page %r" % (page, l))
            g = p["gives"]
            if g is not None and not (isinstance(g, tuple) and len(g) == 2
                                      and ((g[0] == "insight" and isinstance(g[1], int)) or (g[0] == "flag" and isinstance(g[1], str)))):
                out.append("PC_PAGES %s: gives %r" % (page, g))
            for t in [p["title"]] + list(p["body"]):
                if "[" in t or "{" in t:
                    out.append("PC_PAGES %s: a bracket in its text" % page)
        for page, note, f in PC_AUTO_REQUESTS:
            if page not in PC_PAGES:
                out.append("PC_AUTO_REQUESTS: unknown page %r" % page)
        for need in (PC_HOME, PC_BOARD_PAGE, PC_MARKET_PAGE):
            if need not in PC_PAGES:
                out.append("PC_PAGES: no page %r" % need)
        return out

    register_validator(pc_validate)

    register_place_action("pc_open", "My computer", "Look something up. Reading is free.",
                          cost=0, locs=("dorm",), order=5)


style pc_title is text:
    font gui.display_font
    color gui.paper
    size 34

style pc_body is text:
    color gui.paper
    size 20
    line_spacing 4

style pc_small is text:
    color gui.dim
    size 16

style pc_mark_button is button:
    background None
    hover_background Frame("gui/panel_hover.png", 4, 4)
    padding (8, 4, 8, 4)
    xfill True

style pc_link_button is button:
    background None
    padding (0, 2, 0, 2)

style pc_link_text is text:
    color gui.gold
    hover_color gui.paper
    size 20
    underline True


## The browser (4.11). Returns ("page", id), ("check",) or ("close",). A page
## I can't see (yet) shows Home.
screen pc_screen(page="home"):

    tag sandbox
    modal True

    $ _pc_id = page if pc_can_see(page) else PC_HOME
    $ _pc_p = PC_PAGES[_pc_id]
    $ _pc_s = PC_SITES[_pc_p["site"]]
    $ _pc_leads = pc_leads()

    add graded_bg()
    add Solid(gui.ink) alpha 0.72

    key "game_menu" action Return(("close",))

    ## A harness's autoplay never waits on it.
    if smoke_autoplay:
        timer 0.05 action Return(("close",))

    frame:
        pos (210, 110)
        xysize (1500, 860)
        background Solid(gui.pc_page)
        padding (0, 0)

        vbox:
            spacing 0

            ## The title bar.
            fixed:
                ysize 40
                add Solid(gui.pc_chrome)
                text _pc_p["title"] + " · " + _pc_s["name"]:
                    substitute False
                    style "pc_small"
                    color gui.paper
                    xpos 18
                    yalign 0.5
                fixed:
                    xysize (40, 40)
                    xalign 1.0
                    use icon_btn("close", Return(("close",)), tip="Shut it down", size=28, w=40,
                                 wid="pc_close", words="never")

            ## The address bar.
            fixed:
                ysize 48
                add Solid(gui.pc_bar)
                frame:
                    background Solid(gui.pc_side)
                    pos (16, 7)
                    xysize (1468, 34)
                    padding (14, 0)
                    text pc_address(_pc_id) substitute False style "pc_small" yalign 0.5

            hbox:
                spacing 0

                ## Bookmarks, by site; a gold dot on a page not read yet.
                frame:
                    background Solid(gui.pc_side)
                    xysize (300, 772)
                    padding (10, 14)
                    vbox:
                        spacing 1
                        for _pc_k in PC_SITE_ORDER:
                            $ _pc_list = [p for p in pc_pages() if PC_PAGES[p]["site"] == _pc_k]
                            if _pc_list:
                                null height 8
                                text PC_SITES[_pc_k]["name"]:
                                    substitute False
                                    style "pc_small"
                                    size 14
                                    color pc_color(_pc_k)
                                    xpos 8
                                for _pc_q in _pc_list:
                                    button:
                                        id "pc_mark_" + _pc_q
                                        style "pc_mark_button"
                                        selected (_pc_q == _pc_id)
                                        selected_background Frame("gui/panel_active.png", 4, 4)
                                        action Return(("page", _pc_q))
                                        hbox:
                                            spacing 8
                                            if pc_has_read(_pc_q):
                                                null width 8
                                            else:
                                                add Solid(gui.gold) xysize (8, 8) yalign 0.5
                                            text PC_PAGES[_pc_q]["title"]:
                                                substitute False
                                                size 18
                                                color (gui.paper if _pc_q == _pc_id else gui.dim)
                                                yalign 0.5

                ## The page.
                frame:
                    background None
                    xysize (1200, 772)
                    padding (30, 28, 20, 24)
                    viewport:
                        id "pc_view"
                        xysize (1150, 700)
                        scrollbars "vertical"
                        side_spacing 10
                        vscrollbar_xsize 10
                        vscrollbar_unscrollable "hide"
                        mousewheel True
                        draggable True
                        has vbox
                        spacing 16
                        xsize 1100

                        text _pc_s["name"]:
                            substitute False
                            font gui.body_bold_font
                            size 20
                            kerning 1
                            color pc_color(_pc_p["site"])
                        text _pc_p["title"] substitute False style "pc_title"

                        if pc_noted:
                            frame:
                                background Solid(gui.gold)
                                padding (14, 5)
                                text pc_noted substitute False color gui.ink size 18 font gui.body_bold_font

                        ## Home: what I've been asked to look up comes first (4.11).
                        if _pc_id == PC_HOME and _pc_leads:
                            vbox:
                                spacing 6
                                text "REQUESTED READING" style "jjk_label" color gui.gold
                                for _pc_q, _pc_note in _pc_leads:
                                    button:
                                        id "pc_lead_" + _pc_q
                                        style "pc_link_button"
                                        action Return(("page", _pc_q))
                                        text _pc_note.replace("{", "{{") substitute False style "pc_link_text"

                        for _pc_t in _pc_p["body"]:
                            text _pc_t substitute False style "pc_body"

                        ## Home: then the sites, a line each.
                        if _pc_id == PC_HOME:
                            vbox:
                                spacing 10
                                text "SITES" style "jjk_label"
                                for _pc_k in PC_SITE_ORDER:
                                    $ _pc_list = [p for p in pc_pages() if PC_PAGES[p]["site"] == _pc_k and p != PC_HOME]
                                    if _pc_list:
                                        button:
                                            id "pc_site_" + _pc_k
                                            background Frame("gui/panel_dark.png", 4, 4)
                                            hover_background Frame("gui/panel_hover.png", 4, 4)
                                            padding (18, 6)
                                            xsize 1100
                                            action Return(("page", _pc_list[0]))
                                            hbox:
                                                spacing 16
                                                text PC_SITES[_pc_k]["name"]:
                                                    substitute False
                                                    font gui.body_bold_font
                                                    size 20
                                                    color pc_color(_pc_k)
                                                    yalign 0.5
                                                text PC_SITES[_pc_k]["tone"] substitute False style "pc_small" size 18 yalign 0.5

                        ## The board's postings, and the cross-check.
                        if _pc_id == PC_BOARD_PAGE:
                            $ _pc_rows = pc_offers()
                            if not _pc_rows:
                                text "No assignments are posted." style "pc_body" color gui.dim
                            for _pc_title, _pc_grade, _pc_bad in _pc_rows:
                                hbox:
                                    spacing 16
                                    fixed:
                                        xysize (150, 30)
                                        use grade_chip(_pc_grade, 14)
                                    text _pc_title substitute False style "pc_body" yalign 0.5
                                    if _pc_bad:
                                        text "This one doesn't add up." style "pc_body" color gui.gold yalign 0.5
                            if pc_check_ok() and period == PERIODS[-1]:
                                ## At Night it is drawn shut, like every
                                ## other thing that costs time.
                                textbutton "Cross-check the reports · 1 period":
                                    id "pc_check"
                                    style "jjk_button"
                                    xsize 520
                                    text_color gui.mute
                                    action None
                                text "Too late. Bed." style "pc_small" size 18
                            elif pc_check_ok():
                                textbutton "Cross-check the reports · 1 period":
                                    id "pc_check"
                                    style "jjk_button"
                                    xsize 520
                                    text_color gui.gold
                                    text_hover_color gui.paper
                                    action Return(("check",))
                            elif _pc_rows:
                                text "Cross-checked this week." style "pc_small" size 18

                        ## Links.
                        if _pc_id != PC_HOME and pc_links(_pc_id):
                            null height 4
                            text "SEE ALSO" style "jjk_label"
                            for _pc_q in pc_links(_pc_id):
                                button:
                                    id "pc_link_" + _pc_q
                                    style "pc_link_button"
                                    action Return(("page", _pc_q))
                                    text PC_PAGES[_pc_q]["title"] substitute False style "pc_link_text"


## My computer (4.11): browse until I close it. Reading costs no time; the
## cross-check costs one period, once a week. `call screen pc_screen(_pc_page)`
## and the line after it are protected (2.3).
label sb_do_pc_open:

    $ _pc_page = "home"
    $ pc_noted = pc_visit(_pc_page)

    while True:
        call screen pc_screen(_pc_page)
        $ _pc_r = _return

        if not isinstance(_pc_r, tuple) or not _pc_r or _pc_r[0] == "close":
            $ pc_noted = ""
            return

        elif _pc_r[0] == "page":
            if pc_can_see(_pc_r[1]):
                $ _pc_page = _pc_r[1]
                $ pc_noted = pc_visit(_pc_page)

        elif _pc_r[0] == "check":
            $ pc_noted = ""
            if period == PERIODS[-1]:
                "Too late. Bed."
            elif pc_check():
                "I pull the survey sheet behind every posting and read them against each other: who signed, how long they stayed, what they wrote down and what they left out."
                $ _pc_bad_n = len([r for r in pc_offers() if r[2]])
                if _pc_bad_n == 1:
                    "One of them doesn't add up."
                elif _pc_bad_n:
                    "More than one of them doesn't add up."
                else:
                    "They all add up. This week."
                $ advance_period_soft(1)

    return


## Computer state (3.3).
default pc_read = set()          # page ids read
default pc_requests = []         # [(page, note)]
default pc_checked_week = -1     # the board_week already cross-checked
default pc_noted = ""            # the "Noted." line of the page just read for the first time
