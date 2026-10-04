################################################################################
## Cursed Bonds — the Library.
##
## Phase 2, P6 (PHASE2_DESIGN.md 4.14, D34, 6.1). What there is to do in the
## Library: "Study in the stacks", one shelf an hour. The room itself is in
## sb_world.rpy, its picture in bg_placeholders.rpy (P0); the stacks and the
## locked cabinet are hotspots (room_spots.rpy).
##
##   LIB_SHELVES            what each shelf gives, and what I read there
##   lib_gains(shelf)       the gains a shelf gives today, as [(stat, n)]
##   lib_read(shelf)        applies them
##   label sb_do_lib_study  the shelf menu (protected from this commit on, 2.3)
##
## A desk gives Insight +3 (sb_do_study); a shelf here gives 4. On a rest day
## (the day after a night with Gojo) nothing raises Control, so the
## barrier-craft shelf gives its Insight only (4.15).
################################################################################

init -1 python:

    LIB_STAMINA = 8

    ## shelf -> gains [(stat, amount)] and the lines I read there, one a day.
    LIB_SHELVES = {
        "theory": dict(
            gains=[("insight", 4)],
            lines=[
                "A grey textbook with no author. Cursed energy comes out of what people would rather not feel, and a sorcerer is someone who has learned to spend it on purpose. I read the chapter on output twice.",
                "Somebody has pencilled in the margins of the theory shelf for forty years. Half the notes argue with the book, and the notes are usually right.",
                "Reserve, control, output. The book draws them as three sides of one triangle and then spends two hundred pages explaining why it is never an even one.",
            ]),
        "barrier": dict(
            gains=[("control", 2), ("insight", 2)],
            lines=[
                "A manual of veils, all diagrams. I trace the simplest one on the desk with a finger until my hand knows the order the lines go down in.",
                "The barrier book says a curtain is a promise about who may come in, and that the craft is in what the promise leaves out. I copy three of them out by hand.",
                "Page after page of conditions. Every barrier here is paid for with something, and the good ones are paid for with very little.",
            ]),
        "history": dict(
            gains=[("insight", 4)],
            lines=[
                "A bound run of incident reports going back before the war. The handwriting changes every few years. The curses mostly don't.",
                "A history of the school, written by the school. I read it for what it is careful about, and it is careful about a great deal.",
                "Lists of names with grades beside them, and a date after most of the names. I read the short lives slowly.",
            ]),
    }

    def lib_gains(shelf):
        """P6 (room_library.rpy). The gains a shelf gives today, as a list of
        (stat, amount). On a rest day (not night_can_work()) Control and
        Output are left out: nothing raises them that day (4.15)."""
        rows = LIB_SHELVES[shelf]["gains"]
        if not night_can_work():
            rows = [g for g in rows if g[0] not in ("control", "output")]
        return [tuple(g) for g in rows]

    def lib_line(shelf):
        """P6. Today's line for a shelf."""
        lines = LIB_SHELVES[shelf]["lines"]
        return lines[store.day % len(lines)]

    def lib_read(shelf):
        """P6. Returns None. An hour at a shelf: its gains, and the stamina."""
        for stat, n in lib_gains(shelf):
            gain(stat, n)
        spend_stamina(LIB_STAMINA)
        return None

    def lib_validate():
        """P6. Lint findings for the shelf table."""
        out = []
        for key, row in sorted(LIB_SHELVES.items()):
            if not row.get("lines"):
                out.append("LIB_SHELVES %s: no lines" % key)
            for g in row.get("gains", ()):
                if len(g) != 2 or g[0] not in ("insight", "control", "output"):
                    out.append("LIB_SHELVES %s: bad gain %r" % (key, g))
        return out

    register_validator(lib_validate)

    register_place_action("lib_study", "Study in the stacks", "One shelf an hour. More than a desk gives.",
                          cost=1, locs=("library",))


## An hour in the stacks (4.14). The menu is protected (2.3): its caption and
## its three choices stay as they are.
label sb_do_lib_study:

    menu:
        "Shelves to the ceiling, and one hour. I can do one of them justice."

        "Theory: what cursed energy is, and what it costs":
            $ _lib_shelf = "theory"

        "Barrier craft: veils and curtains, with diagrams":
            $ _lib_shelf = "barrier"

        "History: who did this before me, and how it went":
            $ _lib_shelf = "history"

    $ _lib_line = lib_line(_lib_shelf)
    "[_lib_line]"
    if _lib_shelf == "barrier" and not night_can_work():
        "My hands won't hold a line today. I read it, and leave the practice for a day I can stand up straight."
    $ lib_read(_lib_shelf)
    $ advance_period_soft(1)
    return
